from copy import deepcopy
from datetime import datetime

import pytest
from pydantic import ValidationError

from app.services.eipd_controls_v3 import EipdControlCompositionInputV3
from app.services.eipd_resolution import (
    EipdResolutionContextV1,
    bind_eipd_resolution_v1,
)
from app.services.eipd_resolution_binding_v2 import bind_eipd_resolution_v2
from app.services.eipd_review_v3 import evaluate_eipd_resolution_review_prerequisites_v3
from tests import test_eipd_controls_v3 as cases

context = cases.context
frontier_context = cases.frontier_context
complete_resolution = cases.complete_resolution
composition = cases.composition


def evaluate(value, decision="requiere_cambios"):
    return evaluate_eipd_resolution_review_prerequisites_v3(
        value,
        dict(decision=decision, rationale="Revision fundada", review_reference="REV1"),
        evaluated_on=cases.TODAY,
    )


@pytest.mark.parametrize("decision", ["requiere_cambios", "no_continuar"])
def test_negative_partial_with_server_identity(composition, decision):
    composition["assessment"]["resolution"]["necessity_analysis"] = None
    # Reaporte explicito del documento incompleto conserva identidad vigente.
    doc = composition["assessment"]["resolution"]
    doc.pop("context_binding")
    composition["assessment"]["resolution"] = bind_eipd_resolution_v2(
        doc, composition["assessment"]["context"]
    ).model_dump(mode="json")
    before = deepcopy(composition)
    result = evaluate(composition, decision)
    assert (
        result.prerequisites_met
        and result.context_metadata.research_coverage == "contexto_v2"
    )
    assert result.composition is None and not result.can_confirm
    assert result.evaluation_version == 3
    assert result == evaluate(
        EipdControlCompositionInputV3.model_validate(composition), decision
    )
    assert before == composition


def test_positive_keeps_common_barriers_without_prior_review(composition):
    result = evaluate(composition, "continuar")
    codes = cases.codes(result.issues)
    assert result.context_metadata is not None and not result.prerequisites_met
    assert "investigacion_confirmacion_bloqueada" in codes
    assert "politica_investigacion_no_implementada" in codes
    assert "fuentes_oficiales_no_verificadas" in codes
    assert "revision_ausente" not in codes
    assert not result.can_confirm and result.composition is not None


@pytest.mark.parametrize(
    "change", ["stale", "legacy", "missing", "rat", "status", "version"]
)
def test_identity_and_state_barriers(composition, complete_resolution, change):
    data = composition["assessment"]
    expected = {
        "stale": "asociacion_obsoleta",
        "legacy": "asociacion_investigacion_no_cubierta",
        "missing": "expediente_ausente",
        "rat": "contexto_rat_desactualizado",
        "status": "evaluacion_no_borrador",
        "version": "version_no_admitida",
    }[change]
    if change == "stale":
        data["context"]["research_assessment"]["assessment"][
            "public_interest_analysis"
        ] += " modificado"
    elif change == "legacy":
        legacy = {
            k: v
            for k, v in data["context"].items()
            if k in EipdResolutionContextV1.model_fields
        }
        data["resolution"] = bind_eipd_resolution_v1(
            complete_resolution[0], legacy
        ).model_dump(mode="json")
    elif change == "missing":
        data.update(resolution=None, context=None)
    elif change == "rat":
        data["rat_context_current"] = False
    elif change == "status":
        data["assessment_status"] = "confirmado"
    else:
        data["assessment_schema_version"] = 99
    result = evaluate(composition)
    assert not result.prerequisites_met and expected in cases.codes(result.issues)
    if change in ("stale", "legacy", "missing"):
        assert result.context_metadata is None
        assert "metadatos_revision_no_disponibles" in cases.codes(result.issues)


def test_null_research_still_has_explicit_v2_coverage(composition, complete_resolution):
    data = composition["assessment"]
    data["context"]["research_assessment"] = None
    data["resolution"] = bind_eipd_resolution_v2(
        complete_resolution[0], data["context"]
    ).model_dump(mode="json")
    result = evaluate(composition)
    assert result.prerequisites_met
    assert result.context_metadata.research_material_hash is None
    assert result.context_metadata.research_coverage == "contexto_v2"


def test_request_cannot_supply_metadata_or_unknown_decision(composition):
    for change in ({"context_metadata": {}}, {"decision": "aprobar"}):
        request = dict(
            decision="no_continuar",
            rationale="Revision fundada",
            review_reference="REV1",
        )
        request.update(change)
        with pytest.raises(ValidationError):
            evaluate_eipd_resolution_review_prerequisites_v3(
                composition, request, evaluated_on=cases.TODAY
            )
    with pytest.raises(ValueError):
        evaluate_eipd_resolution_review_prerequisites_v3(
            composition, {}, evaluated_on=datetime(2026, 10, 9)
        )


@pytest.mark.parametrize("decision", ["continuar", "requiere_cambios", "no_continuar"])
def test_decision_only_diagnostic_matches_validated_human_request(
    composition, decision
):
    from app.services.eipd_review_v3 import (
        evaluate_eipd_review_decision_prerequisites_v3,
    )

    assert evaluate_eipd_review_decision_prerequisites_v3(
        composition, decision, evaluated_on=cases.TODAY
    ) == evaluate(composition, decision)
    with pytest.raises(ValidationError):
        evaluate_eipd_review_decision_prerequisites_v3(
            composition, "aprobar", evaluated_on=cases.TODAY
        )
