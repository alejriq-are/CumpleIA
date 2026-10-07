"""Series/tenants independientes y PATCH con PostgreSQL real; politica sintetica."""

import asyncio
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from fastapi import HTTPException
from sqlalchemy import delete, select, text

from app.db.models import (
    EipdConfirmationEvidence,
    EipdResolutionReview,
    LegalAssessment,
    LegalAssessmentSeries,
    Treatment,
    TreatmentDataCategory,
    TreatmentDataSubject,
    TreatmentPurpose,
)
from app.schemas.licitud import LegalAssessmentDraftUpdate
from app.services import licitud
from app.services.eipd_policy import build_eipd_review_policy_metadata_v1
from tests import test_eipd_confirmation_concurrency as concurrent
from tests import test_eipd_policy_shared_lock as locks
from tests import test_rls_isolation_licitud as rls
from tests.test_api_eipd_controls_v2_readiness import insert_historical_positive

rat_m3 = concurrent.rat_m3
resolution_rat = concurrent.resolution_rat
complete_resolution = concurrent.complete_resolution
prepared_protected_assessment = concurrent.prepared_protected_assessment
policy = concurrent.policy
biometric = concurrent.biometric
synthetic_confirmation = concurrent.synthetic_confirmation
allow_synthetic_policy = concurrent.allow_synthetic_policy


def values(row):
    return {
        c.key: getattr(row, c.key)
        for c in row.__table__.columns
        if c.key not in ("id", "created_at", "updated_at")
    }


@pytest_asyncio.fixture
async def independent_series(
    synthetic_confirmation,
    _session_factory,
    org_a_id,
    org_b_id,
    profile_a_id,
    profile_b_id,
    auth_a_id,
    auth_b_id,
    cross_tenant,
):
    org = org_b_id if cross_tenant else org_a_id
    actor = profile_b_id if cross_tenant else profile_a_id
    auth = auth_b_id if cross_tenant else auth_a_id
    source_tid, _, original, pub, selection = synthetic_confirmation
    tid, sid, aid = uuid4(), uuid4(), uuid4()
    async with _session_factory() as db:
        source = await db.get(Treatment, source_tid)
        db.add(Treatment(**dict(values(source), id=tid, organization_id=org)))
        await db.flush()
        for model in (TreatmentPurpose, TreatmentDataCategory, TreatmentDataSubject):
            rows = (
                await db.scalars(select(model).where(model.treatment_id == source_tid))
            ).all()
            for row in rows:
                db.add(
                    model(
                        **dict(
                            values(row),
                            id=uuid4(),
                            organization_id=org,
                            treatment_id=tid,
                        )
                    )
                )
        draft = await db.get(LegalAssessment, UUID(original["id"]))
        series = await db.get(LegalAssessmentSeries, draft.series_id)
        db.add(
            LegalAssessmentSeries(
                **dict(
                    values(series),
                    id=sid,
                    treatment_id=tid,
                    organization_id=org,
                    created_by=actor,
                    updated_by=actor,
                )
            )
        )
        await db.flush()
        db.add(
            LegalAssessment(
                **dict(
                    values(draft),
                    id=aid,
                    series_id=sid,
                    treatment_id=tid,
                    organization_id=org,
                    created_by=actor,
                    updated_by=actor,
                )
            )
        )
        await db.commit()
    cloned = dict(
        original,
        id=str(aid),
        organization_id=str(org),
        treatment_id=str(tid),
        series_id=str(sid),
    )
    await insert_historical_positive(
        _session_factory,
        org,
        actor,
        cloned,
        build_eipd_review_policy_metadata_v1(pub.payload),
    )
    yield (tid, "", cloned, pub, selection), org, actor, auth
    async with _session_factory() as db:
        await db.execute(
            delete(EipdConfirmationEvidence).where(
                EipdConfirmationEvidence.assessment_id == aid
            )
        )
        await db.execute(
            delete(EipdResolutionReview).where(
                EipdResolutionReview.assessment_id == aid
            )
        )
        await db.execute(delete(LegalAssessment).where(LegalAssessment.id == aid))
        await db.execute(
            delete(LegalAssessmentSeries).where(LegalAssessmentSeries.id == sid)
        )
        await db.execute(delete(Treatment).where(Treatment.id == tid))
        await db.commit()


@pytest.mark.parametrize("biometric", [False, True])
@pytest.mark.parametrize("cross_tenant", [False, True])
async def test_independent_confirmations_coexist_and_isolate_evidence(
    synthetic_confirmation,
    independent_series,
    allow_synthetic_policy,
    _session_factory,
    _app_session_factory,
    org_a_id,
    profile_a_id,
    auth_a_id,
    cross_tenant,
    biometric,
):
    second_state, second_org, second_actor, second_auth = independent_series
    aid = UUID(synthetic_confirmation[2]["id"])
    bid = UUID(second_state[2]["id"])
    async with _app_session_factory() as first, _app_session_factory() as second:
        await rls._set_auth_user(first, auth_a_id)
        await rls._set_auth_user(second, second_auth)
        await concurrent.confirm(first, synthetic_confirmation, org_a_id, profile_a_id)
        # Primera transaccion sigue abierta: otra serie debe poder confirmar.
        await asyncio.wait_for(
            concurrent.confirm(second, second_state, second_org, second_actor), 5
        )
        one = (await first.scalars(select(EipdConfirmationEvidence))).all()
        two = (await second.scalars(select(EipdConfirmationEvidence))).all()
        assert {r.assessment_id for r in one} == {aid}
        assert {r.assessment_id for r in two} == {bid}
        assert one[0].created_by == profile_a_id and two[0].created_by == second_actor
        assert await concurrent.evidence(_session_factory, aid) == []
        assert await concurrent.evidence(_session_factory, bid) == []
        await first.commit()
        await second.commit()
        await rls._set_auth_user(first, auth_a_id)
        visible = set(
            (await first.scalars(select(EipdConfirmationEvidence.assessment_id))).all()
        )
        assert visible == ({aid} if cross_tenant else {aid, bid})
        if cross_tenant:
            with pytest.raises(HTTPException) as exc:
                await concurrent.confirm(first, second_state, second_org, second_actor)
            assert exc.value.status_code == 404
        await first.rollback()
    assert len(await concurrent.evidence(_session_factory, aid)) == 1
    assert len(await concurrent.evidence(_session_factory, bid)) == 1


@pytest.mark.parametrize("biometric", [False, True])
@pytest.mark.parametrize("cross_tenant", [False, True])
@pytest.mark.parametrize("commit_patch", [True, False])
async def test_patch_blocks_only_its_series_then_confirmation_reloads(
    synthetic_confirmation,
    independent_series,
    allow_synthetic_policy,
    _session_factory,
    _app_session_factory,
    org_a_id,
    profile_a_id,
    auth_a_id,
    cross_tenant,
    biometric,
    commit_patch,
):
    second_state, second_org, second_actor, second_auth = independent_series
    tid, _, original, _, _ = synthetic_confirmation
    aid = UUID(original["id"])
    bid = UUID(second_state[2]["id"])
    async with (
        _app_session_factory() as patcher,
        _app_session_factory() as waiter,
        _app_session_factory() as independent,
    ):
        await rls._set_auth_user(patcher, auth_a_id)
        await rls._set_auth_user(waiter, auth_a_id)
        await rls._set_auth_user(independent, second_auth)
        await licitud.update_legal_assessment_draft_v1(
            patcher,
            org_a_id,
            tid,
            aid,
            profile_a_id,
            LegalAssessmentDraftUpdate(sensitive_rights_exception_assessment={}),
        )
        pid = await waiter.scalar(text("SELECT pg_backend_pid()"))
        task = asyncio.create_task(
            concurrent.confirm(waiter, synthetic_confirmation, org_a_id, profile_a_id)
        )
        try:
            await locks.blocked(patcher, pid)
            assert not task.done()
            # Waiter conserva selector compartido mientras espera serie; otro tenant/serie avanza.
            await asyncio.wait_for(
                concurrent.confirm(independent, second_state, second_org, second_actor),
                5,
            )
            await independent.commit()
            assert len(await concurrent.evidence(_session_factory, bid)) == 1
            assert not task.done()
            if commit_patch:
                await patcher.commit()
                with pytest.raises(HTTPException) as exc:
                    await asyncio.wait_for(task, 5)
                assert exc.value.status_code == 409
                await waiter.rollback()
                await concurrent.atomic.assert_rolled_back(_session_factory, aid)
            else:
                await patcher.rollback()
                assert (await asyncio.wait_for(task, 5)).status == "confirmado"
                await waiter.commit()
                assert len(await concurrent.evidence(_session_factory, aid)) == 1
        finally:
            await locks.stop(task)
            await patcher.rollback()
            await waiter.rollback()
            await independent.rollback()
