from copy import deepcopy
from datetime import date, datetime
from uuid import UUID

import pytest
from pydantic import ValidationError

from app.services.eipd_controls import compose_eipd_controls_v2
from app.services.eipd_controls_v3 import (
    EipdControlCompositionInputV3,
    compose_eipd_controls_v3,
)
from app.services.eipd_resolution import (
    EipdResolutionContextV1,
    bind_eipd_resolution_v1,
)
from app.services.eipd_resolution_binding_v2 import (
    bind_eipd_resolution_v2,
    build_eipd_resolution_document_hash_v2,
)
from tests import test_eipd_frontier_v2 as frontier_cases
from tests import test_services_eipd_resolution as resolution_cases
from tests.test_eipd_resolution_readiness import review_payload

context = frontier_cases.context
frontier_context = frontier_cases.frontier_context
complete_resolution = resolution_cases.complete_resolution
TODAY = date(2026, 10, 9)


@pytest.fixture
def composition(frontier_context, complete_resolution):
    bound = bind_eipd_resolution_v2(complete_resolution[0], frontier_context)
    return dict(
        assessment=dict(
            organization_id=str(UUID(int=2)),
            assessment_id=str(UUID(int=3)),
            assessment_status="borrador",
            assessment_schema_version=1,
            rat_context_schema_version=1,
            justification="Necesidad documentada",
            rat_context_current=True,
            context=frontier_context,
            resolution=bound.model_dump(mode="json"),
            latest_review=None,
        ),
        policy=None,
        latest_review_policy=None,
    )


def compose(value):
    return compose_eipd_controls_v3(value, evaluated_on=TODAY)


def codes(items):
    return {i.code for i in items}


def add_review(value, decision="continuar"):
    document = value["assessment"]["resolution"]
    review = dict(
        id=str(UUID(int=1)),
        organization_id=str(UUID(int=2)),
        assessment_id=str(UUID(int=3)),
        created_by=str(UUID(int=4)),
        decision=decision,
        rationale="Revision fundada",
        review_reference="REV1",
        document_hash=build_eipd_resolution_document_hash_v2(document),
        context_hash=document["context_binding"]["context_hash"],
        created_at="2026-10-09T00:00:00Z",
    )
    value["assessment"]["latest_review"] = review


def test_complete_research_does_not_authorize(composition):
    before = deepcopy(composition)
    result = compose(composition)
    assert result.evaluation_version == 3 and not result.can_confirm
    assert result.preparation_result == "requiere_revision"
    assert result.detection_v3.frontier.research.result == "completo"
    assert result.resolution.binding_version == 2 and result.resolution.context_current
    assert "investigacion_confirmacion_bloqueada" in codes(result.preparation_issues)
    assert "politica_investigacion_no_implementada" in codes(result.review_blockers)
    assert "fuentes_oficiales_no_verificadas" in codes(result.confirmation_blockers)
    assert "revision_ausente" in codes(result.confirmation_blockers)
    assert not any(i.stage == "review" for i in result.review_blockers)
    assert result == compose(EipdControlCompositionInputV3.model_validate(composition))
    assert composition == before
    assert all(
        any(c.field == i.field and c.code == i.code for c in result.preparation_issues)
        for i in result.detection_v3.issues
    )


@pytest.mark.parametrize("decision", ["continuar", "requiere_cambios", "no_continuar"])
def test_human_review_does_not_remove_barriers(composition, decision):
    add_review(composition, decision)
    result = compose(composition)
    assert result.review_state.review_status == "vigente"
    assert result.review_state.latest_review.decision == decision
    assert result.review_policy_status == "sin_identidad"
    assert not result.can_confirm
    assert "revision_sin_politica" in codes(result.confirmation_blockers)
    if decision != "continuar":
        assert "decision_no_continuar" in codes(result.confirmation_blockers)


@pytest.mark.parametrize("change", ["research", "tenant", "assessment"])
def test_stale_or_foreign_review_kept_visible(composition, change):
    add_review(composition)
    if change == "research":
        composition["assessment"]["context"]["research_assessment"]["assessment"][
            "public_interest_analysis"
        ] += " cambiado"
    else:
        field = "organization_id" if change == "tenant" else "assessment_id"
        composition["assessment"]["latest_review"][field] = str(UUID(int=999))
    result = compose(composition)
    assert result.review_state.review_status == "obsoleta"
    assert result.review_state.latest_review is not None
    assert not result.can_confirm
    assert "revision_obsoleta" in codes(result.confirmation_blockers)


def test_legacy_resolution_has_no_research_coverage(composition, complete_resolution):
    ctx = composition["assessment"]["context"]
    legacy = {k: v for k, v in ctx.items() if k in EipdResolutionContextV1.model_fields}
    bound = bind_eipd_resolution_v1(complete_resolution[0], legacy)
    composition["assessment"]["resolution"] = bound.model_dump(mode="json")
    composition["assessment"]["latest_review"] = review_payload(bound)
    result = compose(composition)
    assert result.resolution.binding_version == 1
    assert "asociacion_investigacion_no_cubierta" in codes(result.resolution.issues)
    assert not result.resolution.context_current and not result.can_confirm
    assert result.review_state.review_status == "obsoleta"


def test_absent_context_remains_blocked(composition):
    composition["assessment"].update(context=None, resolution=None)
    result = compose(composition)
    assert not result.can_confirm
    assert "contexto_rat_no_disponible" in codes(result.preparation_issues)


@pytest.mark.parametrize(
    "change", ["extra", "version", "strict", "metadata", "missing"]
)
def test_closed_inputs(composition, change):
    if change == "extra":
        composition["approved"] = True
    elif change == "version":
        composition["assessment"]["context"]["context_schema_version"] = 99
    elif change == "strict":
        composition["assessment"]["assessment_schema_version"] = True
    elif change == "metadata":
        composition["latest_review_policy"] = dict(
            review_id=str(UUID(int=1)),
            policy_version=1,
            policy_reference="P1",
            policy_hash="a" * 64,
        )
    else:
        composition["assessment"]["context"].pop("research_assessment")
    with pytest.raises(ValidationError):
        compose(composition)


def test_explicit_date_and_historical_contract(composition):
    with pytest.raises(ValueError):
        compose_eipd_controls_v3(composition, evaluated_on=datetime(2026, 10, 9))
    with pytest.raises(ValidationError):
        compose_eipd_controls_v2(composition, evaluated_on=TODAY)


@pytest.mark.parametrize("matching", [True, False])
def test_policy_identity_is_separate_from_authority(composition, matching):
    from app.services.eipd_policy import build_eipd_policy_hash_v1

    add_review(composition)
    policy = dict(
        policy_version=1,
        policy_reference="P1",
        routes=[],
        sources_status="pendiente",
        source_records=[],
        acceptance_status="pendiente",
        acceptance_reference=None,
        validation_commit=None,
        acceptance_evidence_reference=None,
        accepted_by=None,
        activation="deshabilitada",
    )
    composition["policy"] = policy
    composition["latest_review_policy"] = dict(
        review_id=composition["assessment"]["latest_review"]["id"],
        policy_version=1,
        policy_reference="P1",
        policy_hash=build_eipd_policy_hash_v1(policy) if matching else "a" * 64,
    )
    result = compose(composition)
    assert result.review_state.review_status == "vigente"
    assert result.review_policy_status == ("vigente" if matching else "obsoleta")
    assert not result.can_confirm
    assert "politica_investigacion_no_implementada" in codes(
        result.confirmation_blockers
    )
    assert "investigacion_confirmacion_bloqueada" in codes(result.confirmation_blockers)


def test_unknown_resolution_binding_rejected(composition):
    composition["assessment"]["resolution"]["context_binding"]["binding_version"] = 99
    with pytest.raises(ValidationError):
        compose(composition)
