"""Conexion atomica; habilitada/positiva solo fixture owner y override pytest local."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from fastapi import HTTPException
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from app.db.models import (
    EipdConfirmationEvidence,
    EipdPolicyPublication,
    EipdPolicySelection,
    EipdPolicySelector,
    EipdResolutionReview,
    LegalAssessment,
)
from app.services import licitud
from app.services.eipd_policy import (
    build_eipd_policy_hash_v1,
    build_eipd_review_policy_metadata_v1,
)
from app.services.eipd_policy_store import read_selected_eipd_policy_v1
from tests import test_api_eipd_prepared_frontier as protected
from tests import test_api_eipd_resolution as fixtures
from tests import test_eipd_policy_global_persistence as global_fixtures
from tests import test_rls_isolation_licitud as rls
from tests import test_services_eipd_policy as policy_fixtures
from tests.test_api_eipd_controls_v2_readiness import insert_historical_positive

rat_m3 = fixtures.rat_m3
resolution_rat = fixtures.resolution_rat
complete_resolution = protected.complete_resolution
prepared_protected_assessment = protected.prepared_protected_assessment
policy = policy_fixtures.policy


@pytest.fixture
def biometric():
    return False


@pytest_asyncio.fixture
async def synthetic_confirmation(
    prepared_protected_assessment, _session_factory, profile_a_id, org_a_id, policy
):
    tid, detail, original = prepared_protected_assessment
    aid = UUID(original["id"])
    async with _session_factory() as db:
        assert await db.get(EipdPolicySelector, 1) is None
        pub = global_fixtures.publication(profile_a_id)
        pub.payload = policy
        pub.policy_reference = policy["policy_reference"]
        pub.policy_hash = build_eipd_policy_hash_v1(policy)
        db.add(pub)
        await db.flush()
        selection = global_fixtures.selection(pub, profile_a_id)
        db.add(selection)
        await db.flush()
        db.add(
            EipdPolicySelector(
                id=1, revision=1, publication_id=pub.id, selection_id=selection.id
            )
        )
        await db.commit()
    await insert_historical_positive(
        _session_factory,
        org_a_id,
        profile_a_id,
        original,
        build_eipd_review_policy_metadata_v1(policy),
    )
    yield tid, detail, original, pub, selection
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
        await db.execute(
            delete(EipdPolicySelector).where(
                EipdPolicySelector.publication_id == pub.id
            )
        )
        await db.execute(
            delete(EipdPolicySelection).where(EipdPolicySelection.id == selection.id)
        )
        await db.execute(
            delete(EipdPolicyPublication).where(EipdPolicyPublication.id == pub.id)
        )
        await db.commit()


@pytest.fixture
def allow_synthetic_policy(monkeypatch):
    # Solo fixture de esta prueba: no flag/configuracion/ruta nueva de produccion.
    async def selected(db):
        return (await read_selected_eipd_policy_v1(db)).policy

    monkeypatch.setattr(licitud, "_selected_disabled_eipd_policy_v1", selected)


async def previous_confirmed(factory, original, actor):
    async with factory() as db:
        draft = await db.get(LegalAssessment, UUID(original["id"]))
        values = {
            c.key: getattr(draft, c.key)
            for c in draft.__table__.columns
            if c.key not in ("id", "created_at", "updated_at")
        }
        draft.version = 2
        await db.flush()
        previous = LegalAssessment(
            **dict(
                values,
                id=uuid4(),
                version=1,
                status="confirmado",
                confirmed_at=datetime.now(UTC),
                confirmed_by=actor,
            )
        )
        db.add(previous)
        await db.commit()
        return previous.id


async def assert_rolled_back(factory, aid, previous_id=None):
    async with factory() as db:
        assert (await db.get(LegalAssessment, aid)).status == "borrador"
        assert (
            await db.scalars(
                select(EipdConfirmationEvidence).where(
                    EipdConfirmationEvidence.assessment_id == aid
                )
            )
        ).all() == []
        if previous_id:
            previous = await db.get(LegalAssessment, previous_id)
            assert previous.status == "confirmado"
            assert (
                previous.replaced_at is None
                and previous.replaced_by_assessment_id is None
            )


@pytest.mark.parametrize("biometric", [False, True])
async def test_production_guard_rejects_enabled_fixture_without_evidence(
    client_a, synthetic_confirmation, org_a_id, _session_factory, biometric
):
    _, detail, original, _, _ = synthetic_confirmation
    async with fixtures.client_for(client_a, org_a_id) as client:
        response = await client.post(detail + "/confirm")
        assert response.status_code == 409
        assert response.json()["detail"] == {
            "code": "politica_eipd_habilitada_no_admitida"
        }
    await assert_rolled_back(_session_factory, UUID(original["id"]))


@pytest.mark.parametrize("biometric", [False, True])
@pytest.mark.parametrize("replace", [False, True])
async def test_synthetic_confirmation_commits_exact_evidence_and_replacement(
    client_a,
    synthetic_confirmation,
    allow_synthetic_policy,
    org_a_id,
    profile_a_id,
    _session_factory,
    replace,
    biometric,
):
    _, detail, original, pub, selection = synthetic_confirmation
    previous_id = (
        await previous_confirmed(_session_factory, original, profile_a_id)
        if replace
        else None
    )
    async with fixtures.client_for(client_a, org_a_id) as client:
        response = await client.post(detail + "/confirm")
        assert response.status_code == 200, response.text
        assert response.json()["status"] == "confirmado"
        assert (await client.post(detail + "/confirm")).status_code == 409
    async with _session_factory() as db:
        row = (
            await db.scalars(
                select(EipdConfirmationEvidence).where(
                    EipdConfirmationEvidence.assessment_id == UUID(original["id"])
                )
            )
        ).one()
        assert row.created_by == profile_a_id and row.organization_id == org_a_id
        assert (
            row.publication_id,
            row.selector_revision,
            row.selection_id,
            row.policy_hash,
        ) == (pub.id, 1, selection.id, pub.policy_hash)
        latest = (
            await db.scalars(
                select(EipdResolutionReview).where(
                    EipdResolutionReview.assessment_id == row.assessment_id
                )
            )
        ).one()
        assert row.review_id == latest.id
        assert (
            row.document_hash == latest.document_hash
            and row.context_hash == latest.context_hash
        )
        confirmed = await db.get(LegalAssessment, row.assessment_id)
        assert row.created_at <= confirmed.confirmed_at
        if previous_id:
            previous = await db.get(LegalAssessment, previous_id)
            assert (
                previous.status == "reemplazado"
                and previous.replaced_by_assessment_id == row.assessment_id
            )


@pytest.mark.parametrize(
    "failure", ["evidence_insert", "after_evidence", "after_replacement", "final_flush"]
)
async def test_failure_rolls_back_evidence_draft_previous(
    synthetic_confirmation,
    allow_synthetic_policy,
    org_a_id,
    profile_a_id,
    auth_a_id,
    _session_factory,
    _app_session_factory,
    monkeypatch,
    failure,
):
    tid, _, original, _, _ = synthetic_confirmation
    aid = UUID(original["id"])
    previous_id = await previous_confirmed(_session_factory, original, profile_a_id)
    async with _app_session_factory() as db:
        await rls._set_auth_user(db, auth_a_id)
        flush = db.flush
        calls = 0

        async def fail_flush(*args, **kwargs):
            nonlocal calls
            calls += 1
            if failure == "evidence_insert" and calls == 1:
                evidence = next(
                    row for row in db.new if isinstance(row, EipdConfirmationEvidence)
                )
                evidence.policy_hash = (
                    "0" * 64
                )  # FK real, no sustitucion del resultado DB.
            await flush(*args, **kwargs)
            if (
                (failure == "after_evidence" and calls == 1)
                or (failure == "after_replacement" and calls == 2)
                or (failure == "final_flush" and calls == 3)
            ):
                raise RuntimeError("TEST: fallo transaccional")

        monkeypatch.setattr(db, "flush", fail_flush)
        with pytest.raises((RuntimeError, IntegrityError)):
            await licitud.confirm_legal_assessment_v1(
                db, org_a_id, tid, aid, profile_a_id
            )
        await db.rollback()
    await assert_rolled_back(_session_factory, aid, previous_id)


@pytest.mark.parametrize("mode", ["negative", "old_identity"])
async def test_failed_gate_never_attempts_evidence(
    synthetic_confirmation,
    allow_synthetic_policy,
    org_a_id,
    profile_a_id,
    auth_a_id,
    _session_factory,
    _app_session_factory,
    monkeypatch,
    mode,
):
    tid, _, original, _, _ = synthetic_confirmation
    aid = UUID(original["id"])
    async with _session_factory() as db:
        row = (
            await db.scalars(
                select(EipdResolutionReview).where(
                    EipdResolutionReview.assessment_id == aid
                )
            )
        ).one()
        if mode == "negative":
            row.decision = (
                "no_continuar"  # Owner sintetico: runtime no puede editar historia.
            )
        else:
            row.policy_hash = "0" * 64
        await db.commit()

    async def forbidden(*args, **kwargs):
        raise AssertionError("Evidencia antes de aprobar controles")

    monkeypatch.setattr(licitud, "record_eipd_confirmation_evidence_v1", forbidden)
    async with _app_session_factory() as db:
        await rls._set_auth_user(db, auth_a_id)
        with pytest.raises(HTTPException) as exc:
            await licitud.confirm_legal_assessment_v1(
                db, org_a_id, tid, aid, profile_a_id
            )
        assert exc.value.status_code == 409
        await db.rollback()
    await assert_rolled_back(_session_factory, aid)
