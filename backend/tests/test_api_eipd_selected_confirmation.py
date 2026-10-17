"""Preparacion/confirmacion con selector real; sin activacion ni evidencia nueva."""

import asyncio
import json
from uuid import UUID

import pytest
from fastapi import HTTPException
from sqlalchemy import event, text

from app.services.licitud import confirm_legal_assessment_v1
from tests import test_api_eipd_prepared_frontier as protected
from tests import test_api_eipd_resolution as fixtures
from tests import test_eipd_policy_shared_lock as locks
from tests import test_rls_isolation_licitud as rls
from tests import test_services_eipd_policy_store as store
from tests.test_api_eipd_resolution_reviews import events, review, setup


@pytest.fixture
def biometric():
    return False


rat_m3 = fixtures.rat_m3
resolution_rat = fixtures.resolution_rat
complete_payload = fixtures.complete_payload
complete_resolution = protected.complete_resolution
prepared_protected_assessment = protected.prepared_protected_assessment
store_state = store.store_state
cleanup_store_controls = store.cleanup_store_controls


@pytest.mark.parametrize("biometric", [False, True])
async def test_same_selected_identity_in_review_readiness_confirmation(
    client_a,
    prepared_protected_assessment,
    org_a_id,
    _session_factory,
    profile_a_id,
    store_state,
    biometric,
    _app_engine,
):
    _, detail, original = prepared_protected_assessment
    async with fixtures.client_for(client_a, org_a_id) as client:
        response = await client.post(detail + "/eipd-resolution/reviews", json=review())
        assert response.status_code == 201
        before = (await client.get(detail + "/readiness")).json()["eipd_controls_v2"]
        assert (
            before["policy"]["policy_reference"]
            == store_state[0].policy.policy_reference
        )
        assert before["policy"]["policy_hash"] == store_state[0].policy_hash
        assert before["review_policy_status"] == "vigente"
        statements = []

        def observe(_conn, _cursor, statement, _params, _ctx, _many):
            statements.append(statement)

        event.listen(_app_engine.sync_engine, "before_cursor_execute", observe)
        try:
            response = await client.post(detail + "/confirm")
        finally:
            event.remove(_app_engine.sync_engine, "before_cursor_execute", observe)
        assert response.status_code == 409
        assert response.json()["detail"]["eipd_controls_v2"] == before
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
        async with _session_factory() as db:
            await db.execute(text("SET LOCAL ROLE eipd_policy_admin"))
            successor = await store.publish(db, profile_a_id)
            await store.choose(db, profile_a_id, successor, 1)
            await db.commit()
        updated = (await client.get(detail + "/readiness")).json()["eipd_controls_v2"]
        assert updated["policy"]["policy_hash"] == successor.policy_hash
        assert updated["review_policy_status"] == "obsoleta"
        response = await client.post(detail + "/confirm")
        assert response.status_code == 409
        assert response.json()["detail"]["eipd_controls_v2"] == updated
        assert len(await events(_session_factory, original["id"])) == 1


@pytest.mark.parametrize("mode", ["missing", "hash", "extra"])
@pytest.mark.parametrize("suffix", ["/readiness", "/confirm"])
async def test_policy_failure_preserves_prepared_draft(
    client_a,
    prepared_protected_assessment,
    org_a_id,
    _session_factory,
    store_state,
    mode,
    suffix,
):
    _, detail, original = prepared_protected_assessment
    async with _session_factory() as db:
        if mode == "missing":
            await db.execute(text("DELETE FROM eipd_policy_selector WHERE id=1"))
        else:
            payload = store_state[0].policy.model_dump(mode="json")
            if mode == "hash":
                payload["acceptance_reference"] = "TEST: altered"
            else:
                payload["unexpected"] = True
            await db.execute(
                text(
                    "UPDATE eipd_policy_publications SET payload=CAST(:payload AS jsonb) WHERE id=:id"
                ),
                dict(id=store_state[0].id, payload=json.dumps(payload)),
            )
        await db.commit()
    async with fixtures.client_for(client_a, org_a_id) as client:
        response = await (
            client.get(detail + suffix)
            if suffix == "/readiness"
            else client.post(detail + suffix)
        )
        assert response.status_code == 409, response.text
        assert response.json()["detail"] == {"code": "politica_eipd_no_disponible"}
        assert (await client.get(detail)).json() == original
    assert await events(_session_factory, original["id"]) == []


async def test_ordinary_without_selector_confirms_without_policy_bootstrap(
    client_a,
    resolution_rat,
    org_a_id,
    complete_payload,
    _session_factory,
):
    async with fixtures.client_for(client_a, org_a_id) as client:
        tid, payload = resolution_rat
        detail, _ = await setup(
            client,
            (tid, dict(payload, consent_assessment=complete_payload)),
            document=False,
        )
        readiness = await client.get(detail + "/readiness")
        assert readiness.status_code == 200
        assert readiness.json()["eipd_controls_v2"] is None
        response = await client.post(detail + "/confirm")
        assert response.status_code == 200, response.text
    async with _session_factory() as db:
        assert await db.scalar(text("SELECT count(*) FROM eipd_policy_selector")) == 0
        assert (
            await db.scalar(text("SELECT count(*) FROM eipd_confirmation_evidence"))
            == 0
        )


@pytest.mark.parametrize("commit_admin", [True, False])
async def test_confirmation_waits_admin_and_uses_post_wait_policy(
    client_a,
    prepared_protected_assessment,
    org_a_id,
    profile_a_id,
    auth_a_id,
    _session_factory,
    _app_session_factory,
    store_state,
    commit_admin,
):
    tid, _, original = prepared_protected_assessment
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
            confirm_legal_assessment_v1(
                reader, org_a_id, tid, UUID(original["id"]), profile_a_id
            )
        )
        try:
            await locks.blocked(admin, pid)
            assert not task.done()
            if commit_admin:
                await admin.commit()
            else:
                await admin.rollback()
            with pytest.raises(HTTPException) as exc:
                await asyncio.wait_for(task, 5)
            assert exc.value.status_code == 409
            selected = publication if commit_admin else store_state[0]
            assert (
                exc.value.detail["eipd_controls_v2"]["policy"]["policy_hash"]
                == selected.policy_hash
            )
        finally:
            await locks.stop(task)
            await admin.rollback()
            await reader.rollback()


@pytest.mark.parametrize("commit_confirmation", [True, False])
async def test_admin_waits_until_blocked_confirmation_transaction_finishes(
    prepared_protected_assessment,
    org_a_id,
    profile_a_id,
    auth_a_id,
    _session_factory,
    _app_session_factory,
    store_state,
    commit_confirmation,
):
    tid, _, original = prepared_protected_assessment
    async with _session_factory() as db:
        await db.execute(text("SET LOCAL ROLE eipd_policy_admin"))
        publication = await store.publish(db, profile_a_id)
        await db.commit()
    async with _app_session_factory() as reader, _session_factory() as admin:
        await rls._set_auth_user(reader, auth_a_id)
        with pytest.raises(HTTPException):
            await confirm_legal_assessment_v1(
                reader, org_a_id, tid, UUID(original["id"]), profile_a_id
            )
        await admin.execute(text("SET LOCAL ROLE eipd_policy_admin"))
        pid = await admin.scalar(text("SELECT pg_backend_pid()"))
        task = asyncio.create_task(store.choose(admin, profile_a_id, publication, 1))
        try:
            await locks.blocked(reader, pid)
            assert not task.done()
            if commit_confirmation:
                await reader.commit()
            else:
                await reader.rollback()
            await asyncio.wait_for(task, 5)
            await admin.commit()
        finally:
            await locks.stop(task)
            await reader.rollback()
            await admin.rollback()
