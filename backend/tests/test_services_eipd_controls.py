from copy import deepcopy
from dataclasses import FrozenInstanceError
from datetime import date, datetime
from uuid import UUID

import pytest
from pydantic import ValidationError

from app.schemas.licitud import EipdResolutionAssessmentStoredV1
from app.services.eipd_controls import (
    ORDINARY_EVALUATORS,
    EipdControlCompositionInputV1,
    compose_eipd_controls_v1,
)
from app.services.eipd_resolution import bind_eipd_resolution_v1
from tests import test_api_licitud as consent_fixtures
from tests import test_eipd_resolution_readiness as review_fixtures
from tests import test_services_eipd_frontier as frontier_fixtures
from tests import test_services_eipd_resolution as resolution_fixtures

frontier_context = frontier_fixtures.frontier_context
complete_resolution = resolution_fixtures.complete_resolution
complete_payload = consent_fixtures.complete_payload
TODAY = date(2026, 10, 6)


@pytest.fixture
def prepared_controls(frontier_context, complete_contract, complete_resolution):
    ctx = deepcopy(frontier_context)
    ctx["contract_assessment"] = deepcopy(complete_contract)
    frontier_fixtures.rebind(ctx)
    doc = bind_eipd_resolution_v1(complete_resolution[0], ctx).model_dump(mode="json")
    return dict(
        organization_id=str(UUID(int=2)),
        assessment_id=str(UUID(int=3)),
        assessment_status="borrador",
        assessment_schema_version=1,
        rat_context_schema_version=1,
        justification="Necesidad documentada",
        rat_context_current=True,
        context=ctx,
        resolution=doc,
        latest_review=None,
    )


def compose(data):
    return compose_eipd_controls_v1(data, evaluated_on=TODAY)


def codes(items):
    return {i.code for i in items}


def test_documentary_preparation_does_not_authorize(prepared_controls):
    before = deepcopy(prepared_controls)
    result = compose(prepared_controls)
    assert result.preparation_result == "preparado", result.preparation_issues
    assert result.ordinary.result == "completo"
    assert result.detection_v2.result == "requiere_eipd"
    assert result.resolution.is_document_prepared
    assert result.review_state.review_status == "sin_revision"
    assert codes(result.review_blockers) == {
        "fuentes_oficiales_no_verificadas",
        "gate_eipd_no_habilitado",
    }
    assert "revision_ausente" in codes(result.confirmation_blockers)
    assert not any(i.stage == "review" for i in result.review_blockers)
    assert not hasattr(result, "can_confirm")
    assert prepared_controls == before
    assert (
        compose(EipdControlCompositionInputV1.model_validate(prepared_controls))
        == result
    )
    with pytest.raises(FrozenInstanceError):
        result.preparation_result = "preparado"


@pytest.mark.parametrize("decision", ["continuar", "requiere_cambios", "no_continuar"])
def test_latest_human_decision_is_separate_and_cannot_remove_global_barriers(
    prepared_controls, decision
):
    prepared_controls["latest_review"] = review_fixtures.review_payload(
        EipdResolutionAssessmentStoredV1.model_validate(
            prepared_controls["resolution"]
        ),
        decision,
    )
    result = compose(prepared_controls)
    assert result.preparation_result == "preparado"
    assert result.review_state.review_status == "vigente"
    assert result.review_state.latest_review.decision == decision
    assert {"fuentes_oficiales_no_verificadas", "gate_eipd_no_habilitado"} <= codes(
        result.confirmation_blockers
    )
    assert ("decision_no_continuar" in codes(result.confirmation_blockers)) == (
        decision != "continuar"
    )
    with pytest.raises(FrozenInstanceError):
        result.review_state.latest_review.decision = "continuar"


@pytest.mark.parametrize(
    "mode",
    ["organization", "assessment", "document_hash", "context_hash", "document_changed"],
)
def test_wrong_or_obsolete_review_cannot_accredit_confirmation(prepared_controls, mode):
    review = review_fixtures.review_payload(
        EipdResolutionAssessmentStoredV1.model_validate(prepared_controls["resolution"])
    )
    prepared_controls["latest_review"] = review
    if mode in ("organization", "assessment"):
        review[mode + "_id"] = str(UUID(int=99))
    elif mode.endswith("hash"):
        review[mode] = "a" * 64
    else:
        prepared_controls["resolution"]["notes"] = "Documento cambiado"
    result = compose(prepared_controls)
    assert result.preparation_result == "preparado"
    assert result.review_state.review_status == "obsoleta"
    assert "revision_obsoleta" in codes(result.confirmation_blockers)
    if mode in ("organization", "assessment"):
        assert "revision_otro_expediente" in codes(result.confirmation_blockers)
    assert not any(i.stage == "review" for i in result.review_blockers)


@pytest.mark.parametrize(
    "field,value,code",
    [
        ("assessment_status", "confirmado", "evaluacion_no_borrador"),
        ("assessment_status", "reemplazado", "evaluacion_no_borrador"),
        ("assessment_schema_version", 2, "version_no_admitida"),
        ("rat_context_schema_version", 2, "version_no_admitida"),
        ("justification", None, "justificacion_ausente"),
        ("justification", " ", "justificacion_ausente"),
        ("rat_context_current", None, "vigencia_rat_no_resuelta"),
        ("rat_context_current", False, "contexto_rat_desactualizado"),
        ("context", None, "contexto_rat_no_disponible"),
        ("resolution", None, "expediente_ausente"),
    ],
)
def test_each_common_condition_blocks_recording_and_confirmation(
    prepared_controls, field, value, code
):
    prepared_controls[field] = value
    result = compose(prepared_controls)
    assert result.preparation_result != "preparado"
    assert code in codes(result.preparation_issues)
    assert code in codes(result.review_blockers)
    assert code in codes(result.confirmation_blockers)


@pytest.mark.parametrize("basis", ORDINARY_EVALUATORS)
def test_each_ordinary_evaluator_remains_independent(
    prepared_controls,
    basis,
    complete_payload,
    complete_contract,
    complete_legal_obligation,
    complete_rights_defense,
    complete_economic_obligations,
    complete_lia_context,
):
    documents = {
        "consent_assessment": complete_payload,
        "contract_assessment": complete_contract,
        "legal_obligation_assessment": complete_legal_obligation,
        "rights_defense_assessment": complete_rights_defense,
        "economic_obligations_assessment": complete_economic_obligations,
        "lia_assessment": complete_lia_context[0],
    }
    ctx = prepared_controls["context"]
    ctx["contract_assessment"] = None
    field, evaluator = ORDINARY_EVALUATORS[basis]
    ctx["legal_basis"] = basis
    ctx[field] = deepcopy(documents[field])
    frontier_fixtures.rebind(ctx)
    result = compose(prepared_controls)
    expected = (
        evaluator(ctx[field])
        if basis == "consentimiento_art12"
        else evaluator(ctx[field], ctx["rat_context_snapshot"])
    )
    assert result.ordinary.result == expected.result
    assert [(i.field, i.code, i.category) for i in result.ordinary.issues] == [
        (i.field, i.code, i.category) for i in expected.issues
    ]
    # La composicion no inventa permiso si la base ordinaria tiene sus propios limites.
    ctx[field] = None
    result = compose(prepared_controls)
    assert result.ordinary.result == "incompleto"
    assert any(i.stage == "ordinary" for i in result.review_blockers)


@pytest.mark.parametrize("mode", ["ordinary", "frontier", "resolution", "risk"])
def test_documentary_stage_failure_is_retained(prepared_controls, mode):
    if mode == "ordinary":
        prepared_controls["context"]["contract_assessment"] = {}
    elif mode == "frontier":
        prepared_controls["context"]["sensitive_rights_exception_assessment"] = {}
    elif mode == "resolution":
        prepared_controls["resolution"]["report_reference"] = None
    else:
        prepared_controls["resolution"]["residual_risk_level"] = "alto"
    result = compose(prepared_controls)
    assert result.preparation_result != "preparado"
    assert any(
        i.stage == ("resolution" if mode == "risk" else mode)
        for i in result.review_blockers
    )
    assert len(result.review_blockers) == len(set(result.review_blockers))


@pytest.mark.parametrize(
    "extra", ["approved", "sources_verified", "can_confirm", "effective_date"]
)
def test_closed_server_context(prepared_controls, extra):
    prepared_controls[extra] = True
    with pytest.raises(ValidationError):
        compose(prepared_controls)


@pytest.mark.parametrize(
    "field,value",
    [
        ("rat_context_current", "yes"),
        ("assessment_schema_version", True),
        ("rat_context_schema_version", "1"),
    ],
)
def test_internal_flags_are_strict(prepared_controls, field, value):
    prepared_controls[field] = value
    with pytest.raises(ValidationError):
        compose(prepared_controls)


@pytest.mark.parametrize("when", [None, "2026-10-06", datetime(2026, 10, 6)])
def test_explicit_date_without_normative_activation(prepared_controls, when):
    with pytest.raises(ValueError):
        compose_eipd_controls_v1(prepared_controls, evaluated_on=when)


def test_mutated_input_revalidated_and_all_motives_ordered(prepared_controls):
    model = EipdControlCompositionInputV1.model_validate(prepared_controls)
    model.assessment_schema_version = True
    with pytest.raises(ValidationError):
        compose(model)
    prepared_controls["rat_context_current"] = False
    prepared_controls["justification"] = None
    result = compose(prepared_controls)
    assert result.preparation_result == "requiere_revision"
    assert {"justificacion_ausente", "contexto_rat_desactualizado"} <= codes(
        result.preparation_issues
    )
    assert result == compose(prepared_controls)
