from copy import deepcopy
from dataclasses import FrozenInstanceError
from typing import get_args

import pytest
from pydantic import ValidationError

from app.schemas.licitud import EipdQuestionIdV1
from app.services.eipd_frontier import evaluate_eipd_frontier_v1
from app.services.eipd_resolution import EipdResolutionContextV1
from app.services.eipd_screening_v2 import evaluate_eipd_screening_v2
from tests import test_services_eipd_frontier as fixtures
from tests import test_services_eipd_resolution as resolution_fixtures

frontier_context = fixtures.frontier_context
complete_resolution = resolution_fixtures.complete_resolution


def test_prepared_exception_remains_required_with_historical_diagnostic(
    frontier_context,
):
    before = deepcopy(frontier_context)
    historical = evaluate_eipd_frontier_v1(frontier_context).screening
    result = evaluate_eipd_screening_v2(frontier_context)
    assert result.evaluation_version == 2 and result.result == "requiere_eipd"
    assert result.context_current and result.frontier.is_frontier_prepared
    assert not result.can_continue and not hasattr(result, "can_confirm")
    assert result.frontier.screening == historical
    assert historical.result == "pendiente_revision"
    assert any(i.code == "excepcion_especial_no_validada" for i in historical.issues)
    assert any(i.code == "excepcion_especial_preparada" for i in result.issues)
    assert all(i.category == "supuesto_declarado" for i in result.issues)
    positive = [i for i in historical.issues if i.code == "supuesto_declarado"]
    assert positive and all(i in result.issues for i in positive)
    assert result.observations == historical.observations
    assert frontier_context == before
    assert (
        evaluate_eipd_screening_v2(
            EipdResolutionContextV1.model_validate(frontier_context)
        )
        == result
    )
    assert evaluate_eipd_frontier_v1(frontier_context).screening == historical
    with pytest.raises(FrozenInstanceError):
        result.result = "sin_supuestos_declarados"


@pytest.mark.parametrize("question", get_args(EipdQuestionIdV1))
@pytest.mark.parametrize("answer", ["pendiente", "opposite", "missing_rationale"])
def test_unresolved_or_other_trigger_does_not_gain_prepared_route(
    frontier_context, question, answer
):
    declaration = next(
        a
        for a in frontier_context["eipd_screening"]["answers"]
        if a["question_id"] == question
    )
    if answer == "missing_rationale":
        declaration["rationale"] = None
    elif answer == "opposite":
        declaration["answer"] = (
            "no" if question == "datos_protegidos_excepcion_consentimiento" else "si"
        )
    else:
        declaration["answer"] = "pendiente"
    fixtures.rebind(frontier_context)
    result = evaluate_eipd_screening_v2(frontier_context)
    historical = result.frontier.screening
    assert not result.frontier.is_frontier_prepared
    assert (
        result.result,
        result.issues,
        result.observations,
        result.context_current,
    ) == (
        historical.result,
        historical.issues,
        historical.observations,
        historical.context_current,
    )
    assert not any(i.code == "excepcion_especial_preparada" for i in result.issues)
    assert not result.can_continue


@pytest.mark.parametrize(
    "mode",
    [
        "sensitive_missing",
        "role",
        "screening_stale",
        "special_stale",
        "residual",
        "mixed",
    ],
)
def test_invalid_context_preserves_all_historical_motives(frontier_context, mode):
    if mode == "sensitive_missing":
        frontier_context["sensitive_rights_exception_assessment"] = None
        fixtures.rebind(frontier_context)
    elif mode == "role":
        frontier_context["rat_context_snapshot"]["organization_role"] = "encargado"
        fixtures.rebind(frontier_context)
    elif mode.endswith("stale"):
        field = "eipd_screening" if mode == "screening_stale" else "special_conditions"
        frontier_context[field]["context_binding"]["hash"] = "a" * 64
    elif mode == "residual":
        frontier_context["health_assessment"] = {}
        fixtures.rebind(frontier_context)
    else:
        declaration = next(
            d
            for d in frontier_context["special_conditions"]["declarations"]
            if d["question_id"] == "geolocalizacion"
        )
        declaration.update(
            answer="si",
            rationale="Otro regimen",
            data_category_codes=["id"],
            data_subject_codes=["clientes"],
        )
        fixtures.rebind(frontier_context)
    before = deepcopy(frontier_context)
    result = evaluate_eipd_screening_v2(frontier_context)
    assert not result.frontier.is_frontier_prepared
    assert result.issues == result.frontier.screening.issues
    assert result.result == result.frontier.screening.result
    assert any(i.code == "excepcion_especial_no_validada" for i in result.issues)
    assert frontier_context == before


@pytest.mark.parametrize(
    "extra",
    [
        "prepared_exceptions",
        "approved",
        "sources_verified",
        "frontier_prepared",
        "evaluation_version",
    ],
)
def test_no_client_override(frontier_context, extra):
    frontier_context[extra] = True
    with pytest.raises(ValidationError):
        evaluate_eipd_screening_v2(frontier_context)


def test_missing_context_keeps_pending_detection():
    result = evaluate_eipd_screening_v2(None)
    assert result.result == "pendiente_revision" and not result.context_current
    assert result.frontier.result == "incompleto" and not result.can_continue
    assert {i.code for i in result.issues} == {
        "snapshot_ausente",
        "screening_ausente",
        "pregunta_omitida",
    }


def test_ordinary_negative_screening_unchanged(complete_resolution, negative_controls):
    _, ctx = complete_resolution
    ctx = deepcopy(ctx)
    ctx["special_conditions"] = deepcopy(negative_controls["special_conditions"])
    ctx["eipd_screening"] = deepcopy(negative_controls["eipd_screening"])
    fixtures.rebind(ctx)
    result = evaluate_eipd_screening_v2(ctx)
    assert result.result == "sin_supuestos_declarados" and result.context_current
    assert result.can_continue and not hasattr(result, "can_confirm")
    assert not result.frontier.is_frontier_prepared
    assert result.issues == result.frontier.screening.issues == ()
