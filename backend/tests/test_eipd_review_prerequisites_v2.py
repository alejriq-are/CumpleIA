"""Revision v2 pura: negativos parciales y positivos sin circularidad."""

from copy import deepcopy
from dataclasses import FrozenInstanceError, asdict
from datetime import date, datetime

import pytest
from pydantic import ValidationError

from app.schemas.licitud import EipdResolutionReviewIn
from app.services.eipd_controls import (
    EipdControlCompositionInputV1,
    EipdControlCompositionInputV2,
)
from app.services.eipd_policy import resolve_eipd_gate_policy_v1
from app.services.eipd_resolution import (
    bind_eipd_resolution_v1,
    evaluate_eipd_resolution_review_prerequisites_v1,
)
from app.services.eipd_review_v2 import evaluate_eipd_resolution_review_prerequisites_v2
from tests import test_services_eipd_policy as policy_fixtures

frontier_context = policy_fixtures.frontier_context
complete_resolution = policy_fixtures.complete_resolution
prepared_controls = policy_fixtures.prepared_controls
policy = policy_fixtures.policy
TODAY = date(2026, 10, 7)


def request(decision="continuar"):
    return dict(
        decision=decision, rationale="Revision fundada", review_reference="TEST: REV86"
    )


def evaluate(assessment, policy, decision="continuar", identity=None):
    return evaluate_eipd_resolution_review_prerequisites_v2(
        dict(assessment=assessment, policy=policy, latest_review_policy=identity),
        request(decision),
        evaluated_on=TODAY,
    )


def rebind(assessment):
    document = deepcopy(assessment["resolution"])
    document.pop("context_binding", None)
    assessment["resolution"] = bind_eipd_resolution_v1(
        document, assessment["context"]
    ).model_dump(mode="json")


def codes(result):
    return {i.code for i in result.issues}


def test_prepared_positive_needs_no_previous_event_but_v1_stays_closed(
    prepared_controls, policy
):
    before = deepcopy((prepared_controls, policy))
    result = evaluate(prepared_controls, policy)
    assert result.evaluation_version == 2 and result.prerequisites_met
    assert not result.issues
    assert result.composition.review_state.latest_review is None
    assert "revision_ausente" in {
        i.code for i in result.composition.confirmation_blockers
    }
    assert result.composition.detection_v2.result == "requiere_eipd"
    assert not hasattr(result, "can_confirm")
    assert (prepared_controls, policy) == before
    legacy = evaluate_eipd_resolution_review_prerequisites_v1(
        "borrador",
        prepared_controls["resolution"],
        prepared_controls["context"],
        request(),
        evaluated_on=TODAY,
    )
    assert not legacy.prerequisites_met
    assert {i.code for i in legacy.issues} == {
        "frontera_revision_no_validada",
        "fuentes_oficiales_no_verificadas",
    }
    with pytest.raises(FrozenInstanceError):
        result.decision = "no_continuar"
    with pytest.raises(FrozenInstanceError):
        result.composition.policy.activation = "deshabilitada"


@pytest.mark.parametrize("decision", ["requiere_cambios", "no_continuar"])
@pytest.mark.parametrize(
    "mode",
    ["partial", "ordinary", "justification", "high_risk", "disabled", "missing_policy"],
)
def test_negatives_keep_partial_prerequisites_without_full_composition(
    prepared_controls, policy, decision, mode
):
    if mode == "partial":
        prepared_controls["resolution"] = bind_eipd_resolution_v1(
            {"document_reference": "TEST: parcial"}, prepared_controls["context"]
        ).model_dump(mode="json")
    elif mode == "ordinary":
        prepared_controls["context"]["contract_assessment"] = None
        rebind(prepared_controls)
    elif mode == "justification":
        prepared_controls["justification"] = None
    elif mode == "high_risk":
        prepared_controls["resolution"]["residual_risk_level"] = "alto"
    elif mode == "disabled":
        policy = resolve_eipd_gate_policy_v1()
    elif mode == "missing_policy":
        policy = None
    result = evaluate(prepared_controls, policy, decision)
    assert result.prerequisites_met and result.composition is None
    legacy = evaluate_eipd_resolution_review_prerequisites_v1(
        prepared_controls["assessment_status"],
        prepared_controls["resolution"],
        prepared_controls["context"],
        request(decision),
        evaluated_on=TODAY,
    )
    assert legacy.prerequisites_met


@pytest.mark.parametrize("decision", ["continuar", "requiere_cambios", "no_continuar"])
@pytest.mark.parametrize(
    "mode", ["document", "context", "unbound", "obsolete", "confirmed", "replaced"]
)
def test_partial_common_conditions_cannot_be_skipped(
    prepared_controls, policy, decision, mode
):
    if mode == "document":
        prepared_controls["resolution"] = None
    elif mode == "context":
        prepared_controls["context"] = None
    elif mode == "unbound":
        prepared_controls["resolution"]["context_binding"] = None
    elif mode == "obsolete":
        prepared_controls["resolution"]["context_binding"]["context_hash"] = "a" * 64
    elif mode == "confirmed":
        prepared_controls["assessment_status"] = "confirmado"
    elif mode == "replaced":
        prepared_controls["assessment_status"] = "reemplazado"
    result = evaluate(prepared_controls, policy, decision)
    assert not result.prerequisites_met
    legacy = evaluate_eipd_resolution_review_prerequisites_v1(
        prepared_controls["assessment_status"],
        prepared_controls["resolution"],
        prepared_controls["context"],
        request(decision),
        evaluated_on=TODAY,
    )
    assert {
        i.code
        for i in legacy.issues
        if i.code
        not in {"frontera_revision_no_validada", "fuentes_oficiales_no_verificadas"}
    } <= codes(result)
    if decision != "continuar":
        projected = [
            {k: v for k, v in asdict(i).items() if k != "stage"} for i in result.issues
        ]
        assert projected == [asdict(i) for i in legacy.issues]


@pytest.mark.parametrize(
    "mode",
    [
        "missing_policy",
        "disabled",
        "route",
        "future",
        "ordinary",
        "partial",
        "high_risk",
        "version",
        "rat",
        "frontier",
    ],
)
def test_positive_requires_every_stage(prepared_controls, policy, mode):
    if mode == "missing_policy":
        policy = None
    elif mode == "disabled":
        policy = resolve_eipd_gate_policy_v1()
    elif mode == "route":
        route = evaluate(
            prepared_controls, policy
        ).composition.detection_v2.frontier.route
        policy["routes"] = [r for r in policy["routes"] if r != route]
    elif mode == "future":
        policy["source_records"][0]["publication_date"] = "2026-10-08"
    elif mode == "ordinary":
        prepared_controls["context"]["contract_assessment"] = None
        rebind(prepared_controls)
    elif mode == "partial":
        prepared_controls["resolution"] = bind_eipd_resolution_v1(
            {}, prepared_controls["context"]
        ).model_dump(mode="json")
    elif mode == "high_risk":
        prepared_controls["resolution"]["residual_risk_level"] = "alto"
    elif mode == "version":
        prepared_controls["assessment_schema_version"] = 2
    elif mode == "rat":
        prepared_controls["rat_context_current"] = False
    elif mode == "frontier":
        prepared_controls["context"]["sensitive_rights_exception_assessment"] = {}
        rebind(prepared_controls)
    result = evaluate(prepared_controls, policy)
    assert not result.prerequisites_met and result.composition is not None
    assert set(result.composition.review_blockers) <= set(result.issues)
    assert len(set(result.issues)) == len(result.issues)
    assert not any(i.stage == "review" for i in result.issues)


@pytest.mark.parametrize("mode", ["negative", "old_identity"])
def test_positive_does_not_depend_on_previous_decision_or_policy(
    prepared_controls, policy, mode
):
    identity = policy_fixtures.add_review(prepared_controls, policy, "no_continuar")
    if mode == "old_identity":
        identity["policy_hash"] = "b" * 64
    result = evaluate(prepared_controls, policy, identity=identity)
    assert result.prerequisites_met
    assert result.composition.confirmation_blockers
    assert not result.composition.review_blockers


@pytest.mark.parametrize("when", [None, "2026-10-07", datetime(2026, 10, 7)])
def test_explicit_date_without_clock(prepared_controls, policy, when):
    with pytest.raises(ValueError):
        evaluate_eipd_resolution_review_prerequisites_v2(
            dict(
                assessment=prepared_controls, policy=policy, latest_review_policy=None
            ),
            request(),
            evaluated_on=when,
        )


@pytest.mark.parametrize(
    "mode", ["extra", "metadata", "mutated_review", "mutated_assessment"]
)
@pytest.mark.parametrize("decision", ["continuar", "no_continuar"])
def test_closed_inputs_and_mutated_models(prepared_controls, policy, mode, decision):
    value = dict(assessment=prepared_controls, policy=policy, latest_review_policy=None)
    payload = request(decision)
    if mode == "extra":
        value["approved"] = True
    elif mode == "metadata":
        payload["policy_hash"] = "a" * 64
    elif mode == "mutated_review":
        payload = EipdResolutionReviewIn.model_validate(payload)
        payload.decision = "approved"
    else:
        value["assessment"] = EipdControlCompositionInputV1.model_validate(
            prepared_controls
        )
        value["assessment"].assessment_schema_version = True
    with pytest.raises(ValidationError):
        evaluate_eipd_resolution_review_prerequisites_v2(
            value, payload, evaluated_on=TODAY
        )


def test_valid_model_matches_dict(prepared_controls, policy):
    value = dict(assessment=prepared_controls, policy=policy, latest_review_policy=None)
    assert evaluate_eipd_resolution_review_prerequisites_v2(
        EipdControlCompositionInputV2.model_validate(value),
        EipdResolutionReviewIn.model_validate(request()),
        evaluated_on=TODAY,
    ) == evaluate(prepared_controls, policy)
