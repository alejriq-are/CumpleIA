"""Confirmaciones exitosas/revocacion con PostgreSQL real y override pytest local."""

import asyncio
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from fastapi import HTTPException
from sqlalchemy import delete, select, text

from app.db.models import (
    EipdConfirmationEvidence,
    EipdPolicyPublication,
    EipdPolicySelection,
    EipdPolicySelector,
    LegalAssessment,
    LegalAssessmentSeries,
)
from app.services import licitud
from app.services.eipd_policy import build_eipd_review_policy_metadata_v1
from tests import test_eipd_confirmation_atomic as atomic
from tests import test_eipd_policy_shared_lock as locks
from tests import test_rls_isolation_licitud as rls
from tests import test_services_eipd_policy_store as store
from tests.test_api_eipd_controls_v2_readiness import insert_historical_positive

rat_m3 = atomic.rat_m3
resolution_rat = atomic.resolution_rat
complete_resolution = atomic.complete_resolution
prepared_protected_assessment = atomic.prepared_protected_assessment
policy = atomic.policy
biometric = atomic.biometric
synthetic_confirmation = atomic.synthetic_confirmation
allow_synthetic_policy = atomic.allow_synthetic_policy


@pytest_asyncio.fixture
async def disabled_successor(synthetic_confirmation, _session_factory, profile_a_id):
    async with _session_factory() as db:
        await db.execute(text("SET LOCAL ROLE eipd_policy_admin"))
        pub = await store.publish(db, profile_a_id)
        await db.commit()
    yield pub
    # Fixture owner restaura estado previo solo para limpieza, nunca canal runtime.
    original, selection = synthetic_confirmation[3:]
    async with _session_factory() as db:
        selector = await db.get(EipdPolicySelector, 1)
        if selector.publication_id == pub.id:
            selector.revision = 1
            selector.publication_id = original.id
            selector.selection_id = selection.id
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


async def evidence(factory, aid):
    async with factory() as db:
        rows = (
            await db.scalars(
                select(EipdConfirmationEvidence).where(
                    EipdConfirmationEvidence.assessment_id == aid
                )
            )
        ).all()
        return [
            {c.key: getattr(row, c.key) for c in row.__table__.columns} for row in rows
        ]


async def confirm(db, state, org, actor):
    return await licitud.confirm_legal_assessment_v1(
        db, org, state[0], UUID(state[2]["id"]), actor
    )


@pytest.mark.parametrize("biometric", [False, True])
@pytest.mark.parametrize("commit_holder", [True, False])
async def test_two_confirmations_serialize_and_keep_one_evidence(
    synthetic_confirmation,
    allow_synthetic_policy,
    _session_factory,
    _app_session_factory,
    org_a_id,
    profile_a_id,
    auth_a_id,
    commit_holder,
    biometric,
):
    aid = UUID(synthetic_confirmation[2]["id"])
    previous_id = await atomic.previous_confirmed(
        _session_factory, synthetic_confirmation[2], profile_a_id
    )
    async with _app_session_factory() as holder, _app_session_factory() as waiter:
        await rls._set_auth_user(holder, auth_a_id)
        await rls._set_auth_user(waiter, auth_a_id)
        await confirm(holder, synthetic_confirmation, org_a_id, profile_a_id)
        pid = await waiter.scalar(text("SELECT pg_backend_pid()"))
        task = asyncio.create_task(
            confirm(waiter, synthetic_confirmation, org_a_id, profile_a_id)
        )
        try:
            await locks.blocked(holder, pid)
            assert not task.done()
            assert (
                await evidence(_session_factory, aid) == []
            )  # Todavia no publicado por commit.
            if commit_holder:
                await holder.commit()
                with pytest.raises(HTTPException) as exc:
                    await asyncio.wait_for(task, 5)
                assert exc.value.status_code == 409
                await waiter.rollback()
            else:
                await holder.rollback()
                assert (await asyncio.wait_for(task, 5)).status == "confirmado"
                await waiter.commit()
        finally:
            await locks.stop(task)
            await holder.rollback()
            await waiter.rollback()
    rows = await evidence(_session_factory, aid)
    assert (
        len(rows) == 1
        and rows[0]["policy_hash"] == synthetic_confirmation[3].policy_hash
    )
    async with _session_factory() as db:
        assert (await db.get(LegalAssessment, aid)).status == "confirmado"
        previous = await db.get(LegalAssessment, previous_id)
        assert (
            previous.status == "reemplazado"
            and previous.replaced_by_assessment_id == aid
        )


async def next_draft_with_old_positive(factory, state, org, actor):
    """Sucesor historico sintetico; no promociona revisiones en produccion."""
    async with factory() as db:
        confirmed = await db.get(LegalAssessment, UUID(state[2]["id"]))
        values = {
            c.key: getattr(confirmed, c.key)
            for c in confirmed.__table__.columns
            if c.key not in ("id", "created_at", "updated_at")
        }
        draft = LegalAssessment(
            **dict(
                values,
                id=uuid4(),
                version=confirmed.version + 1,
                status="borrador",
                confirmed_at=None,
                confirmed_by=None,
                replaced_at=None,
                replaced_by_assessment_id=None,
            )
        )
        db.add(draft)
        series = await db.get(LegalAssessmentSeries, draft.series_id)
        series.next_version = draft.version + 1
        await db.commit()
    original = dict(state[2], id=str(draft.id))
    await insert_historical_positive(
        factory,
        org,
        actor,
        original,
        build_eipd_review_policy_metadata_v1(state[3].payload),
    )
    return state[0], state[1], original, state[3], state[4]


@pytest.mark.parametrize("biometric", [False, True])
@pytest.mark.parametrize("commit_confirmation", [True, False])
async def test_revocation_waits_successful_transaction_and_preserves_history(
    synthetic_confirmation,
    disabled_successor,
    allow_synthetic_policy,
    _session_factory,
    _app_session_factory,
    org_a_id,
    profile_a_id,
    auth_a_id,
    commit_confirmation,
    biometric,
):
    aid = UUID(synthetic_confirmation[2]["id"])
    async with _app_session_factory() as holder, _session_factory() as admin:
        await rls._set_auth_user(holder, auth_a_id)
        await confirm(holder, synthetic_confirmation, org_a_id, profile_a_id)
        # Copia exacta de evidencia aun no confirmada por commit.
        row = (
            await holder.scalars(
                select(EipdConfirmationEvidence).where(
                    EipdConfirmationEvidence.assessment_id == aid
                )
            )
        ).one()
        before = {c.key: getattr(row, c.key) for c in row.__table__.columns}
        await admin.execute(text("SET LOCAL ROLE eipd_policy_admin"))
        pid = await admin.scalar(text("SELECT pg_backend_pid()"))
        task = asyncio.create_task(
            store.choose(admin, profile_a_id, disabled_successor, 1)
        )
        try:
            await locks.blocked(holder, pid)
            assert not task.done()
            if commit_confirmation:
                await holder.commit()
            else:
                await holder.rollback()
            assert (await asyncio.wait_for(task, 5)).selector.revision == 2
            await admin.commit()
        finally:
            await locks.stop(task)
            await holder.rollback()
            await admin.rollback()
    assert await evidence(_session_factory, aid) == (
        [before] if commit_confirmation else []
    )
    future = (
        await next_draft_with_old_positive(
            _session_factory, synthetic_confirmation, org_a_id, profile_a_id
        )
        if commit_confirmation
        else synthetic_confirmation
    )
    async with _app_session_factory() as reader:
        await rls._set_auth_user(reader, auth_a_id)
        with pytest.raises(HTTPException) as exc:
            await confirm(reader, future, org_a_id, profile_a_id)
        assert exc.value.status_code == 409
        controls = exc.value.detail["eipd_controls_v2"]
        assert controls["policy"]["policy_hash"] == disabled_successor.policy_hash
        assert controls["policy"]["activation"] == "deshabilitada"
        assert controls["review_policy_status"] == "obsoleta"
        assert "gate_eipd_no_habilitado" in {
            i["code"] for i in controls["confirmation_blockers"]
        }
        await reader.rollback()
    assert await evidence(_session_factory, aid) == (
        [before] if commit_confirmation else []
    )
    if commit_confirmation:
        await atomic.assert_rolled_back(_session_factory, UUID(future[2]["id"]))
        async with _session_factory() as db:
            assert (await db.get(LegalAssessment, aid)).status == "confirmado"


@pytest.mark.parametrize("biometric", [False, True])
@pytest.mark.parametrize("commit_admin", [True, False])
async def test_waiting_confirmation_reloads_revocation_or_rollback(
    synthetic_confirmation,
    disabled_successor,
    allow_synthetic_policy,
    _session_factory,
    _app_session_factory,
    org_a_id,
    profile_a_id,
    auth_a_id,
    commit_admin,
    biometric,
):
    aid = UUID(synthetic_confirmation[2]["id"])
    async with _session_factory() as admin, _app_session_factory() as reader:
        await admin.execute(text("SET LOCAL ROLE eipd_policy_admin"))
        await store.choose(admin, profile_a_id, disabled_successor, 1)
        await rls._set_auth_user(reader, auth_a_id)
        pid = await reader.scalar(text("SELECT pg_backend_pid()"))
        task = asyncio.create_task(
            confirm(reader, synthetic_confirmation, org_a_id, profile_a_id)
        )
        try:
            await locks.blocked(admin, pid)
            assert not task.done()
            if commit_admin:
                await admin.commit()
                with pytest.raises(HTTPException) as exc:
                    await asyncio.wait_for(task, 5)
                controls = exc.value.detail["eipd_controls_v2"]
                assert (
                    controls["policy"]["policy_hash"] == disabled_successor.policy_hash
                )
                assert controls["review_policy_status"] == "obsoleta"
                await reader.rollback()
            else:
                await admin.rollback()
                assert (await asyncio.wait_for(task, 5)).status == "confirmado"
                await reader.commit()
        finally:
            await locks.stop(task)
            await reader.rollback()
            await admin.rollback()
    if commit_admin:
        await atomic.assert_rolled_back(_session_factory, aid)
    else:
        rows = await evidence(_session_factory, aid)
        assert len(rows) == 1
        assert rows[0]["policy_hash"] == synthetic_confirmation[3].policy_hash
        assert rows[0]["selector_revision"] == 1
