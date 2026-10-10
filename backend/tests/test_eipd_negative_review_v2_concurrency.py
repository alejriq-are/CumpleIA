"""Locks PostgreSQL reales para negativas V2; solo fixtures aisladas."""

import asyncio
from uuid import UUID

import pytest
import pytest_asyncio
from fastapi import HTTPException
from sqlalchemy import delete, text

from app.db.models import (
    EipdPolicyPublication,
    EipdPolicySelection,
    EipdPolicySelector,
    EipdResolutionReview,
    LegalAssessment,
)
from app.schemas.licitud import EipdResolutionReviewIn, LegalAssessmentDraftUpdate
from app.services import licitud
from tests import test_api_eipd_negative_review_v2 as http
from tests import test_eipd_policy_shared_lock as locks
from tests import test_rls_isolation_licitud as rls
from tests import test_services_eipd_policy_store as store

explicit_review_policy = http.explicit_review_policy
rat_m3 = http.rat_m3
resolution_rat = http.resolution_rat


@pytest_asyncio.fixture
async def state(client_a, resolution_rat, org_a_id):
    async with http.api.client_for(client_a, org_a_id) as client:
        _, original = await http.create(client, resolution_rat)
    return resolution_rat[0], UUID(original["id"]), original


async def review(db, state, org, actor):
    return await licitud.record_eipd_resolution_review_v1(
        db,
        org,
        state[0],
        state[1],
        actor,
        EipdResolutionReviewIn.model_validate(http.request()),
    )


@pytest.mark.parametrize("change", ["stale", "rebind", "withdraw"])
@pytest.mark.parametrize("commit_change", [True, False])
async def test_waiting_negative_reloads_committed_material_or_rollback(
    state,
    _app_session_factory,
    _session_factory,
    org_a_id,
    profile_a_id,
    auth_a_id,
    change,
    commit_change,
):
    async with _app_session_factory() as holder, _app_session_factory() as waiter:
        await rls._set_auth_user(holder, auth_a_id)
        await rls._set_auth_user(waiter, auth_a_id)
        changes = {"research_assessment": {"purpose_type": "estadistico"}}
        if change == "rebind":
            changes["eipd_resolution_assessment"] = {
                "document_reference": "TEST: EIPD155 cambiado"
            }
        elif change == "withdraw":
            changes = {"eipd_resolution_assessment": None}
        updated = await licitud.update_legal_assessment_draft_v1(
            holder,
            org_a_id,
            state[0],
            state[1],
            profile_a_id,
            LegalAssessmentDraftUpdate.model_validate(changes),
        )
        expected_document = (
            updated.eipd_resolution_assessment
            if commit_change
            else state[2]["eipd_resolution_assessment"]
        )
        pid = await waiter.scalar(text("SELECT pg_backend_pid()"))
        task = asyncio.create_task(review(waiter, state, org_a_id, profile_a_id))
        try:
            await locks.blocked(holder, pid)
            assert not task.done()
            assert not await http.rows(_session_factory, str(state[1]))
            if commit_change:
                await holder.commit()
            else:
                await holder.rollback()
            if commit_change and change != "rebind":
                with pytest.raises(HTTPException) as exc:
                    await asyncio.wait_for(task, 5)
                assert exc.value.status_code == 409
                # Withdrawn document returns to historical partial prerequisites;
                # neither dispatch may infer or recreate its missing identity.
                await waiter.rollback()
            else:
                event = await asyncio.wait_for(task, 5)
                assert (
                    event.context_hash
                    == expected_document["context_binding"]["context_hash"]
                )
                assert event.review_context_metadata["resolution_binding_version"] == 2
                await waiter.commit()
        finally:
            await locks.stop(task)
            await holder.rollback()
            await waiter.rollback()
    events = await http.rows(_session_factory, str(state[1]))
    assert len(events) == (0 if commit_change and change != "rebind" else 1)
    if events:
        assert (
            events[0].review_context_metadata["context_hash"]
            == expected_document["context_binding"]["context_hash"]
        )
        async with _session_factory() as db:
            assert (await db.get(LegalAssessment, state[1])).status == "borrador"


@pytest_asyncio.fixture
async def successor(state, explicit_review_policy, _session_factory, profile_a_id):
    async with _session_factory() as db:
        selector = await db.get(EipdPolicySelector, 1)
        previous = (selector.publication_id, selector.selection_id, selector.revision)
        await db.execute(text("SET LOCAL ROLE eipd_policy_admin"))
        pub = await store.publish(db, profile_a_id)
        await db.commit()
    yield pub
    # Cleanup exclusively synthetic isolated data, not runtime permissions.
    async with _session_factory() as db:
        await db.execute(
            delete(EipdResolutionReview).where(
                EipdResolutionReview.assessment_id == state[1]
            )
        )
        selector = await db.get(EipdPolicySelector, 1)
        selector.publication_id, selector.selection_id, selector.revision = previous
        await db.flush()
        await db.execute(
            delete(EipdPolicySelection).where(
                EipdPolicySelection.publication_id == pub.id
            )
        )
        await db.execute(
            delete(EipdPolicyPublication).where(EipdPolicyPublication.id == pub.id)
        )
        await db.commit()


@pytest.mark.parametrize("commit_admin", [True, False])
async def test_negative_waits_policy_selection_and_uses_current_identity(
    state,
    successor,
    explicit_review_policy,
    _app_session_factory,
    _session_factory,
    org_a_id,
    profile_a_id,
    auth_a_id,
    commit_admin,
):
    async with _session_factory() as admin, _app_session_factory() as waiter:
        await admin.execute(text("SET LOCAL ROLE eipd_policy_admin"))
        await store.choose(admin, profile_a_id, successor, 1)
        await rls._set_auth_user(waiter, auth_a_id)
        pid = await waiter.scalar(text("SELECT pg_backend_pid()"))
        task = asyncio.create_task(review(waiter, state, org_a_id, profile_a_id))
        try:
            await locks.blocked(admin, pid)
            assert not task.done()
            assert not await http.rows(_session_factory, str(state[1]))
            if commit_admin:
                await admin.commit()
            else:
                await admin.rollback()
            event = await asyncio.wait_for(task, 5)
            expected = successor if commit_admin else explicit_review_policy
            assert event.policy_hash == expected.policy_hash
            assert event.policy_reference == expected.policy.policy_reference
            assert event.policy_version == expected.policy.policy_version
            assert event.review_context_metadata["research_coverage"] == "contexto_v2"
            await waiter.commit()
        finally:
            await locks.stop(task)
            await admin.rollback()
            await waiter.rollback()
    events = await http.rows(_session_factory, str(state[1]))
    assert len(events) == 1 and events[0].policy_hash == expected.policy_hash


@pytest.mark.parametrize("commit_review", [True, False])
async def test_policy_change_waits_negative_transaction_until_commit_or_rollback(
    state,
    successor,
    explicit_review_policy,
    _app_session_factory,
    _session_factory,
    org_a_id,
    profile_a_id,
    auth_a_id,
    commit_review,
):
    async with _app_session_factory() as reader, _session_factory() as admin:
        await rls._set_auth_user(reader, auth_a_id)
        event = await review(reader, state, org_a_id, profile_a_id)
        assert event.policy_hash == explicit_review_policy.policy_hash
        await admin.execute(text("SET LOCAL ROLE eipd_policy_admin"))
        pid = await admin.scalar(text("SELECT pg_backend_pid()"))
        task = asyncio.create_task(store.choose(admin, profile_a_id, successor, 1))
        try:
            await locks.blocked(reader, pid)
            assert not task.done()
            assert not await http.rows(_session_factory, str(state[1]))
            if commit_review:
                await reader.commit()
            else:
                await reader.rollback()
            assert (await asyncio.wait_for(task, 5)).selector.revision == 2
            await admin.commit()
        finally:
            await locks.stop(task)
            await reader.rollback()
            await admin.rollback()
    events = await http.rows(_session_factory, str(state[1]))
    assert len(events) == int(commit_review)
    if events:
        assert events[0].policy_hash == explicit_review_policy.policy_hash
        assert events[0].review_context_metadata is not None
        async with _app_session_factory() as db:
            await rls._set_auth_user(db, auth_a_id)
            latest, identity = await licitud._latest_eipd_review_snapshot_v1(
                db, org_a_id, state[1]
            )
            assert latest["id"] == events[0].id
            assert identity.policy_hash != successor.policy_hash
            await db.rollback()
