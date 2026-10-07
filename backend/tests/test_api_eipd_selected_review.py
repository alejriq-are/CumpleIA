"""Revision con selector real: sin fallback, identidad y locks hasta transaccion."""

import asyncio
import json
from uuid import UUID

import pytest
from sqlalchemy import event, text

from app.schemas.licitud import EipdResolutionReviewIn
from app.services.eipd_policy import build_eipd_review_policy_metadata_v1
from app.services.licitud import record_eipd_resolution_review_v1
from tests import test_api_eipd_resolution as fixtures
from tests import test_eipd_policy_shared_lock as locks
from tests import test_rls_isolation_licitud as rls
from tests import test_services_eipd_policy_store as store
from tests.test_api_eipd_resolution_reviews import events, review, setup

rat_m3 = fixtures.rat_m3
resolution_rat = fixtures.resolution_rat
store_state = store.store_state
cleanup_store_controls = store.cleanup_store_controls


@pytest.mark.parametrize("decision", ["requiere_cambios", "no_continuar"])
async def test_http_records_selected_identity(
    client_a,
    resolution_rat,
    org_a_id,
    profile_a_id,
    _session_factory,
    store_state,
    decision,
    _app_engine,
):
    statements = []

    def observe(_conn, _cursor, statement, _params, _ctx, _many):
        statements.append(statement)

    async with fixtures.client_for(client_a, org_a_id) as client:
        detail, original = await setup(client, resolution_rat)
        event.listen(_app_engine.sync_engine, "before_cursor_execute", observe)
        try:
            response = await client.post(
                detail + "/eipd-resolution/reviews", json=review(decision)
            )
        finally:
            event.remove(_app_engine.sync_engine, "before_cursor_execute", observe)
        assert response.status_code == 201, response.text
        rows = await events(_session_factory, original["id"])
        expected = build_eipd_review_policy_metadata_v1(store_state[0].policy)
        assert len(rows) == 1 and rows[0].created_by == profile_a_id
        assert {key: getattr(rows[0], key) for key in expected} == expected
        assert expected["policy_reference"].startswith("TEST:")
        selector = next(
            i
            for i, sql in enumerate(statements)
            if "lock_eipd_policy_selector_v1()" in sql
        )
        series = next(
            i
            for i, sql in enumerate(statements)
            if "legal_assessment_series" in sql and "FOR UPDATE" in sql
        )
        assert selector < series
        assert any("jsonb_build_object" in sql for sql in statements[series + 1 :])
        assert (await client.get(detail)).json() == original


@pytest.mark.parametrize("mode", ["missing", "extra", "hash"])
async def test_http_policy_failure_has_no_event_or_draft_change(
    client_a,
    resolution_rat,
    org_a_id,
    _session_factory,
    store_state,
    mode,
):
    async with fixtures.client_for(client_a, org_a_id) as client:
        detail, original = await setup(client, resolution_rat)
        async with _session_factory() as db:
            if mode == "missing":
                await db.execute(text("DELETE FROM eipd_policy_selector WHERE id=1"))
            else:
                payload = store_state[0].policy.model_dump(mode="json")
                if mode == "extra":
                    payload["unexpected"] = True
                else:
                    payload["activation"] = "deshabilitada"
                    payload["authorized_routes"] = []
                await db.execute(
                    text(
                        "UPDATE eipd_policy_publications SET payload=CAST(:payload AS jsonb) WHERE id=:id"
                    ),
                    dict(id=store_state[0].id, payload=json.dumps(payload)),
                )
            await db.commit()
        response = await client.post(detail + "/eipd-resolution/reviews", json=review())
        assert response.status_code == 409, response.text
        assert response.json()["detail"] == {"code": "politica_eipd_no_disponible"}
        assert (await client.get(detail)).json() == original
        assert await events(_session_factory, original["id"]) == []


async def call_review(db, org, tid, original, actor):
    return await record_eipd_resolution_review_v1(
        db,
        org,
        tid,
        UUID(original["id"]),
        actor,
        EipdResolutionReviewIn.model_validate(review()),
    )


@pytest.mark.parametrize("commit_admin", [True, False])
async def test_review_waits_admin_and_records_post_wait_identity(
    client_a,
    resolution_rat,
    org_a_id,
    profile_a_id,
    auth_a_id,
    _session_factory,
    _app_session_factory,
    store_state,
    commit_admin,
):
    async with fixtures.client_for(client_a, org_a_id) as client:
        _, original = await setup(client, resolution_rat)
    async with _session_factory() as db:
        await db.execute(text("SET LOCAL ROLE eipd_policy_admin"))
        publication = await store.publish(db, profile_a_id)
        await db.commit()
    async with _session_factory() as admin, _app_session_factory() as reader:
        await admin.execute(text("SET LOCAL ROLE eipd_policy_admin"))
        await store.choose(admin, profile_a_id, publication, 1)
        await rls._set_auth_user(reader, auth_a_id)
        pid = await reader.scalar(text("SELECT pg_backend_pid()"))
        task = asyncio.create_task(
            call_review(reader, org_a_id, resolution_rat[0], original, profile_a_id)
        )
        try:
            await locks.blocked(admin, pid)
            assert not task.done()
            if commit_admin:
                await admin.commit()
            else:
                await admin.rollback()
            result = await asyncio.wait_for(task, 5)
            selected = publication if commit_admin else store_state[0]
            assert result.policy_reference == selected.policy.policy_reference
            assert result.policy_hash == selected.policy_hash
            await reader.commit()
        finally:
            await locks.stop(task)
            await reader.rollback()
            await admin.rollback()
    assert len(await events(_session_factory, original["id"])) == 1


@pytest.mark.parametrize("commit_review", [True, False])
async def test_admin_waits_until_review_transaction_finishes(
    client_a,
    resolution_rat,
    org_a_id,
    profile_a_id,
    auth_a_id,
    _session_factory,
    _app_session_factory,
    store_state,
    commit_review,
):
    async with fixtures.client_for(client_a, org_a_id) as client:
        _, original = await setup(client, resolution_rat)
    async with _session_factory() as db:
        await db.execute(text("SET LOCAL ROLE eipd_policy_admin"))
        publication = await store.publish(db, profile_a_id)
        await db.commit()
    async with _app_session_factory() as reader, _session_factory() as admin:
        await rls._set_auth_user(reader, auth_a_id)
        result = await call_review(
            reader, org_a_id, resolution_rat[0], original, profile_a_id
        )
        assert result.policy_hash == store_state[0].policy_hash
        await admin.execute(text("SET LOCAL ROLE eipd_policy_admin"))
        pid = await admin.scalar(text("SELECT pg_backend_pid()"))
        task = asyncio.create_task(store.choose(admin, profile_a_id, publication, 1))
        try:
            await locks.blocked(reader, pid)
            assert not task.done()
            if commit_review:
                await reader.commit()
            else:
                await reader.rollback()
            plan = await asyncio.wait_for(task, 5)
            assert plan.selector.revision == 2
            await admin.commit()
        finally:
            await locks.stop(task)
            await reader.rollback()
            await admin.rollback()
    assert len(await events(_session_factory, original["id"])) == int(commit_review)
