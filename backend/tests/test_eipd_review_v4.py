"""Requisitos ficticios internos no habilitan escritura ni decisiones positivas."""

from copy import deepcopy
from datetime import datetime

import pytest
from pydantic import ValidationError

from app.services.eipd_review_v4 import (
    evaluate_eipd_resolution_review_documentary_prerequisites_v4 as request,
)
from app.services.eipd_review_v4 import (
    evaluate_eipd_review_documentary_decision_v4 as evaluate,
)
from tests import test_eipd_controls_v4 as cases

DAY = cases.DAY
complete_resolution = cases.complete_resolution
context = cases.context
materials = cases.materials
represented = cases.represented
value = cases.value


@pytest.mark.parametrize("decision", ["requiere_cambios", "no_continuar"])
def test_negative_identity_can_be_current_without_action_or_complete_content(
    value, decision
):
    before = deepcopy(value)
    result = evaluate(value, decision, evaluated_on=DAY)
    assert result.documentary_prerequisites_met
    assert result.current_context_metadata.metadata_schema_version == 2
    assert result.composition.review_blockers
    assert not result.prerequisites_met
    assert not result.authorizes_action and not result.can_confirm
    assert value == before


@pytest.mark.parametrize(
    "change",
    [
        "stale_rat",
        "no_context",
        "no_resolution",
        "other_parent",
        "other_tenant",
        "other_treatment",
        "historical",
    ],
)
def test_missing_or_stale_identity_never_meets_documentary_requirements(value, change):
    a = value["assessment"]
    if change == "stale_rat":
        a["rat_context_current"] = False
    elif change == "no_context":
        a["context"] = None
    elif change == "no_resolution":
        a["resolution"] = None
    elif change == "other_parent":
        a["assessment_id"] = "a0000000-0000-0000-0000-000000000099"
    elif change == "other_tenant":
        a["organization_id"] = "a0000000-0000-0000-0000-000000000099"
    elif change == "other_treatment":
        a["treatment_id"] = "a0000000-0000-0000-0000-000000000099"
    else:
        a["assessment_status"] = "confirmado"
    result = evaluate(value, "requiere_cambios", evaluated_on=DAY)
    assert not result.documentary_prerequisites_met
    assert not result.prerequisites_met


def test_positive_remains_documentarily_blocked(value):
    result = evaluate(value, "continuar", evaluated_on=DAY)
    assert not result.documentary_prerequisites_met
    assert any(
        i.code == "politica_representacion_no_implementada"
        for i in result.documentary_issues
    )


@pytest.mark.parametrize("extra", ["context_metadata", "created_by", "document_hash"])
def test_human_request_rejects_server_fields(value, extra):
    with pytest.raises(ValidationError):
        request(
            value,
            dict(
                decision="no_continuar",
                rationale="PRUEBA",
                review_reference="PRUEBA",
                **{extra: "PRUEBA"},
            ),
            evaluated_on=DAY,
        )


def test_date_and_decision_are_explicit(value):
    with pytest.raises(ValueError):
        evaluate(value, "no_continuar", evaluated_on=datetime(2026, 10, 14))
    with pytest.raises(ValidationError):
        evaluate(value, "aprobar", evaluated_on=DAY)
