"""Salida V4 no confunde identidad actual con requisitos de acciones."""

from copy import deepcopy
from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas.licitud import (
    EipdControlCompositionV4Out,
    LegalAssessmentRepresentationReadinessOutV1,
    LegalAssessmentRepresentationReadinessOutV2,
)
from app.services.eipd_controls_v4_output import build_eipd_controls_v4_output as build
from tests import test_eipd_controls_v4 as cases

complete_resolution = cases.complete_resolution
context = cases.context
materials = cases.materials
represented = cases.represented
value = cases.value
DAY = date(2026, 10, 14)


@pytest.mark.parametrize("route", ["research", "ordinary", "no_context"])
def test_versioned_output_preserves_diagnostics_and_blocks_all_decisions(value, route):
    if route == "ordinary":
        value["assessment"]["context"].update(
            research_assessment=None, special_conditions=None
        )
    elif route == "no_context":
        value["assessment"]["context"] = None
    before = deepcopy(value)
    result = build(value, evaluated_on=DAY)
    assert result.evaluation_version == 4
    assert not result.authorizes_action and not result.can_confirm
    assert result.detection.evaluation_version == (3 if route == "research" else 2)
    assert result.resolution.binding_version == 3
    decisions = result.review_prerequisites_v4
    for name in ("continuar", "requiere_cambios", "no_continuar"):
        decision = getattr(decisions, name)
        assert decision.prerequisites_met is False
        assert decision.context_metadata is None
        assert any(
            i.code == "politica_representacion_no_implementada" for i in decision.issues
        )
    assert value == before
    assert (
        EipdControlCompositionV4Out.model_validate_json(result.model_dump_json())
        == result
    )


@pytest.mark.parametrize("field", ["authorizes_action", "can_confirm"])
def test_output_flags_cannot_authorize(value, field):
    raw = build(value, evaluated_on=DAY).model_dump(mode="json")
    raw[field] = True
    with pytest.raises(ValidationError):
        EipdControlCompositionV4Out.model_validate(raw)


@pytest.mark.parametrize("decision", ["continuar", "requiere_cambios", "no_continuar"])
def test_current_metadata_is_not_action_context(value, decision):
    raw = build(value, evaluated_on=DAY).model_dump(mode="json")
    assert raw["context_metadata"] is not None
    raw["review_prerequisites_v4"][decision]["context_metadata"] = raw[
        "context_metadata"
    ]
    with pytest.raises(ValidationError):
        EipdControlCompositionV4Out.model_validate(raw)
    raw["review_prerequisites_v4"][decision]["context_metadata"] = None
    raw["review_prerequisites_v4"][decision]["prerequisites_met"] = True
    with pytest.raises(ValidationError):
        EipdControlCompositionV4Out.model_validate(raw)


def test_successor_root_preserves_old_contract():
    assert (
        "eipd_controls_v4"
        not in LegalAssessmentRepresentationReadinessOutV1.model_fields
    )
    assert (
        LegalAssessmentRepresentationReadinessOutV2.model_fields[
            "eipd_controls_v4"
        ].default
        is None
    )
