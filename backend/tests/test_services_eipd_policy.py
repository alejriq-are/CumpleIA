"""Politica sintetica interna: no acredita fuentes reales ni activa API/gates."""

from copy import deepcopy
from dataclasses import FrozenInstanceError
from datetime import date, datetime
from uuid import UUID

import pytest
from pydantic import ValidationError

from app.schemas.licitud import EipdResolutionAssessmentStoredV1, EipdResolutionReviewIn
from app.services.eipd_controls import (
    EipdControlCompositionInputV1,
    EipdControlCompositionInputV2,
    compose_eipd_controls_v1,
    compose_eipd_controls_v2,
)
from app.services.eipd_policy import (
    EipdGatePolicyV1,
    build_eipd_policy_hash_v1,
    evaluate_eipd_policy_v1,
)
from tests import test_eipd_resolution_readiness as review_fixtures
from tests import test_services_eipd_controls as controls_fixtures

frontier_context = controls_fixtures.frontier_context
complete_resolution = controls_fixtures.complete_resolution
prepared_controls = controls_fixtures.prepared_controls
TODAY = date(2026, 10, 7)
ROUTES = ["sensible_derechos", "sensible_biometrica_derechos"]


@pytest.fixture
def policy():
    return dict(
        policy_version=1,
        policy_reference="TEST: revision politica 1",
        routes=ROUTES[:],
        sources_status="verificadas",
        source_records=[
            dict(
                emitter="TEST: emisor sintetico",
                instrument_reference="TEST: instrumento",
                primary_url="https://example.org/test-instrument",
                publication_version="TEST: version 1",
                publication_date="2026-10-06",
                applicability_analysis="TEST: cobertura documentada",
                applicable_routes=ROUTES[:],
                verification_reference="TEST: evidencia servidor",
                verified_by=str(UUID(int=4)),
            )
        ],
        acceptance_status="aceptada",
        acceptance_reference="TEST: aceptacion",
        validation_commit="a" * 40,
        acceptance_evidence_reference="TEST: pruebas",
        accepted_by=str(UUID(int=5)),
        activation="habilitada",
    )


def compose(assessment, policy, identity=None):
    return compose_eipd_controls_v2(
        dict(assessment=assessment, policy=policy, latest_review_policy=identity),
        evaluated_on=TODAY,
    )


def codes(items):
    return {i.code for i in items}


def add_review(assessment, policy, decision="continuar"):
    document = EipdResolutionAssessmentStoredV1.model_validate(assessment["resolution"])
    assessment["latest_review"] = review_fixtures.review_payload(document, decision)
    return dict(
        review_id=assessment["latest_review"]["id"],
        policy_version=1,
        policy_reference=policy["policy_reference"],
        policy_hash=build_eipd_policy_hash_v1(policy),
    )


@pytest.mark.parametrize(
    "mode",
    [
        "bool",
        "version",
        "extra",
        "routes_duplicate",
        "routes_unknown",
        "no_routes",
        "no_sources",
        "sources_pending",
        "acceptance_pending",
        "acceptance_missing",
        "bad_commit",
        "bad_url",
        "source_scope",
        "source_duplicate",
        "source_blank",
        "source_routes_duplicate",
    ],
)
def test_invalid_policy_never_becomes_permission(policy, mode):
    if mode == "bool":
        policy["policy_version"] = True
    elif mode == "version":
        policy["policy_version"] = 2
    elif mode == "extra":
        policy["approved"] = True
    elif mode == "routes_duplicate":
        policy["routes"].append(ROUTES[0])
    elif mode == "routes_unknown":
        policy["routes"].append("otras_excepciones")
    elif mode == "no_routes":
        policy["routes"] = []
    elif mode == "no_sources":
        policy["source_records"] = []
    elif mode == "sources_pending":
        policy["sources_status"] = "pendiente"
    elif mode == "acceptance_pending":
        policy["acceptance_status"] = "pendiente"
    elif mode == "acceptance_missing":
        policy["accepted_by"] = None
    elif mode == "bad_commit":
        policy["validation_commit"] = "abc123"
    elif mode == "bad_url":
        policy["source_records"][0]["primary_url"] = "file:///secret"
    elif mode == "source_scope":
        policy["source_records"][0]["applicable_routes"] = [ROUTES[0]]
    elif mode == "source_duplicate":
        policy["source_records"] *= 2
    elif mode == "source_blank":
        policy["source_records"][0]["verification_reference"] = "  "
    elif mode == "source_routes_duplicate":
        policy["source_records"][0]["applicable_routes"] *= 2
    with pytest.raises(ValidationError):
        EipdGatePolicyV1.model_validate(policy)


@pytest.mark.parametrize(
    "field",
    ["policy_version", "policy_reference", "routes", "source_records", "activation"],
)
def test_every_required_policy_field_is_explicit(policy, field):
    del policy[field]
    with pytest.raises(ValidationError):
        EipdGatePolicyV1.model_validate(policy)


@pytest.mark.parametrize(
    "mode",
    [
        "reference",
        "source",
        "acceptance",
        "route",
        "activation",
        "responsible",
        "publication",
    ],
)
def test_policy_hash_changes_with_relevant_evidence(policy, mode):
    before = build_eipd_policy_hash_v1(policy)
    if mode == "reference":
        policy["policy_reference"] += " nueva"
    elif mode == "source":
        policy["source_records"][0]["applicability_analysis"] += " nueva"
    elif mode == "acceptance":
        policy["acceptance_evidence_reference"] += " nueva"
    elif mode == "route":
        policy["routes"] = [ROUTES[0]]
    elif mode == "activation":
        policy["activation"] = "deshabilitada"
    elif mode == "responsible":
        policy["accepted_by"] = str(UUID(int=9))
    elif mode == "publication":
        policy["source_records"][0]["publication_version"] += " nueva"
    assert build_eipd_policy_hash_v1(policy) != before


def test_hash_canonical_and_inputs_unchanged(policy):
    second = deepcopy(policy["source_records"][0])
    second["instrument_reference"] = "TEST: segundo instrumento"
    policy["source_records"].append(second)
    before = deepcopy(policy)
    digest = build_eipd_policy_hash_v1(policy)
    assert policy == before
    policy["routes"].reverse()
    policy["source_records"].reverse()
    for source in policy["source_records"]:
        source["applicable_routes"].reverse()
    assert build_eipd_policy_hash_v1(policy) == digest
    assert build_eipd_policy_hash_v1(EipdGatePolicyV1.model_validate(policy)) == digest


@pytest.mark.parametrize(
    "mode", ["missing", "pending", "disabled", "unaccepted", "future", "outside_route"]
)
def test_policy_barriers_do_not_require_human_event(policy, mode):
    route = ROUTES[1]
    if mode == "missing":
        policy = None
    elif mode == "pending":
        policy.update(
            sources_status="pendiente",
            acceptance_status="pendiente",
            activation="deshabilitada",
            source_records=[],
        )
    elif mode == "disabled":
        policy["activation"] = "deshabilitada"
    elif mode == "unaccepted":
        policy.update(acceptance_status="pendiente", activation="deshabilitada")
    elif mode == "future":
        policy["source_records"][0]["publication_date"] = "2026-10-08"
    elif mode == "outside_route":
        policy["routes"] = [ROUTES[0]]
    result = evaluate_eipd_policy_v1(policy, route=route, evaluated_on=TODAY)
    assert result.issues
    assert not any(i.stage == "review" for i in result.issues)
    with pytest.raises(FrozenInstanceError):
        result.activation = "habilitada"


@pytest.mark.parametrize("when", [None, "2026-10-07", datetime(2026, 10, 7)])
def test_date_explicit_not_normative_activation(policy, when):
    with pytest.raises(ValueError):
        evaluate_eipd_policy_v1(policy, route=ROUTES[0], evaluated_on=when)


def test_unknown_evaluation_route_rejected(policy):
    with pytest.raises(ValueError):
        evaluate_eipd_policy_v1(policy, route="otra", evaluated_on=TODAY)


@pytest.mark.parametrize("mode", ["policy", "source", "nested_input"])
def test_mutated_models_revalidated(policy, prepared_controls, mode):
    model = EipdGatePolicyV1.model_validate(policy)
    if mode == "source":
        model.source_records[0].verification_reference = " "
    else:
        model.policy_version = True
    if mode == "nested_input":
        data = EipdControlCompositionInputV2.model_construct(
            assessment=EipdControlCompositionInputV1.model_validate(prepared_controls),
            policy=model,
            latest_review_policy=None,
        )
        with pytest.raises(ValidationError):
            compose_eipd_controls_v2(data, evaluated_on=TODAY)
    else:
        with pytest.raises(ValidationError):
            build_eipd_policy_hash_v1(model)


def test_v2_prepared_is_not_authorization_and_v1_preserved(policy, prepared_controls):
    before = deepcopy((policy, prepared_controls))
    result = compose(prepared_controls, policy)
    assert result.evaluation_version == 2
    assert result.preparation_result == "preparado"
    assert not result.review_blockers  # No circularidad: no necesita evento anterior.
    assert codes(result.confirmation_blockers) == {"revision_ausente"}
    assert result.detection_v2.result == "requiere_eipd"
    assert result.detection_v2.frontier.screening.result == "pendiente_revision"
    assert result.review_policy_status == "sin_revision"
    assert not hasattr(result, "can_confirm")
    assert (policy, prepared_controls) == before
    legacy = compose_eipd_controls_v1(prepared_controls, evaluated_on=TODAY)
    assert codes(legacy.review_blockers) == {
        "fuentes_oficiales_no_verificadas",
        "gate_eipd_no_habilitado",
    }
    assert legacy.preparation_issues == result.preparation_issues
    with pytest.raises(FrozenInstanceError):
        result.policy.activation = "deshabilitada"


@pytest.mark.parametrize("decision", ["continuar", "requiere_cambios", "no_continuar"])
def test_current_policy_identity_does_not_replace_human_decision(
    policy, prepared_controls, decision
):
    identity = add_review(prepared_controls, policy, decision)
    result = compose(prepared_controls, policy, identity)
    assert result.review_policy_status == "vigente"
    assert result.review_state.review_status == "vigente"
    assert not result.review_blockers
    assert bool(result.confirmation_blockers) == (decision != "continuar")
    if decision != "continuar":
        assert "decision_no_continuar" in codes(result.confirmation_blockers)
    with pytest.raises(FrozenInstanceError):
        result.review_state.latest_review.decision = "continuar"


@pytest.mark.parametrize(
    "mode",
    [
        "missing",
        "hash",
        "reference",
        "other_event",
        "policy_changed",
        "document_changed",
        "other_tenant",
        "other_assessment",
    ],
)
def test_no_old_review_can_accredit_v2(policy, prepared_controls, mode):
    identity = add_review(prepared_controls, policy)
    if mode == "missing":
        identity = None
    elif mode == "hash":
        identity["policy_hash"] = "b" * 64
    elif mode == "reference":
        identity["policy_reference"] += " otra"
    elif mode == "other_event":
        identity["review_id"] = str(UUID(int=9))
    elif mode == "policy_changed":
        policy["acceptance_reference"] += " nueva"
    elif mode == "document_changed":
        prepared_controls["resolution"]["notes"] = "Cambio de documento"
    elif mode == "other_tenant":
        prepared_controls["latest_review"]["organization_id"] = str(UUID(int=9))
    elif mode == "other_assessment":
        prepared_controls["latest_review"]["assessment_id"] = str(UUID(int=9))
    result = compose(prepared_controls, policy, identity)
    assert result.confirmation_blockers
    assert not result.review_blockers
    if mode == "missing":
        assert result.review_policy_status == "sin_identidad"
    elif mode in ("hash", "reference", "other_event", "policy_changed"):
        assert result.review_policy_status == "obsoleta"
    else:
        assert "revision_obsoleta" in codes(result.confirmation_blockers)


@pytest.mark.parametrize(
    "mode", ["missing_policy", "disabled", "future", "route", "document", "ordinary"]
)
def test_shared_stages_never_disappear_with_matching_review(
    policy, prepared_controls, mode
):
    identity = add_review(prepared_controls, policy)
    if mode == "missing_policy":
        policy = None
    elif mode == "disabled":
        policy["activation"] = "deshabilitada"
    elif mode == "future":
        policy["source_records"][0]["publication_date"] = "2026-10-08"
    elif mode == "route":
        route = compose(prepared_controls, policy).detection_v2.frontier.route
        policy["routes"] = [r for r in ROUTES if r != route]
    elif mode == "document":
        prepared_controls["resolution"] = None
    elif mode == "ordinary":
        prepared_controls["context"]["contract_assessment"] = None
    result = compose(prepared_controls, policy, identity)
    assert result.review_blockers and result.confirmation_blockers
    if mode in ("document", "ordinary"):
        assert result.preparation_result != "preparado"
    assert len(result.confirmation_blockers) == len(set(result.confirmation_blockers))


@pytest.mark.parametrize(
    "extra", ["can_confirm", "approved", "policy_hash", "activation_date"]
)
def test_internal_and_client_inputs_are_closed(policy, prepared_controls, extra):
    data = dict(
        assessment=prepared_controls,
        policy=policy,
        latest_review_policy=None,
        **{extra: True},
    )
    with pytest.raises(ValidationError):
        compose_eipd_controls_v2(data, evaluated_on=TODAY)
    with pytest.raises(ValidationError):
        EipdResolutionReviewIn.model_validate(
            dict(
                decision="continuar",
                rationale="Fundamento",
                review_reference="R1",
                **{extra: True},
            )
        )


def test_identity_without_event_rejected(policy, prepared_controls):
    identity = add_review(prepared_controls, policy)
    prepared_controls["latest_review"] = None
    with pytest.raises(ValidationError):
        compose(prepared_controls, policy, identity)


@pytest.mark.parametrize(
    "mode", ["bool", "version", "hash", "extra", "missing", "mutated"]
)
def test_review_policy_metadata_revalidated_and_closed(policy, prepared_controls, mode):
    from app.services.eipd_policy import EipdReviewPolicyIdentityV1

    identity = add_review(prepared_controls, policy)
    if mode == "bool":
        identity["policy_version"] = True
    elif mode == "version":
        identity["policy_version"] = 2
    elif mode == "hash":
        identity["policy_hash"] = "not-a-hash"
    elif mode == "extra":
        identity["approved"] = True
    elif mode == "missing":
        del identity["review_id"]
    elif mode == "mutated":
        identity = EipdReviewPolicyIdentityV1.model_validate(identity)
        identity.policy_version = True
    with pytest.raises(ValidationError):
        compose(prepared_controls, policy, identity)


def test_policy_issue_order_deterministic(policy):
    policy["source_records"][0]["publication_date"] = "2026-10-08"
    second = deepcopy(policy["source_records"][0])
    second["instrument_reference"] = "TEST: aaa"
    policy["source_records"].append(second)
    before = evaluate_eipd_policy_v1(policy, route=ROUTES[0], evaluated_on=TODAY)
    policy["source_records"].reverse()
    assert (
        evaluate_eipd_policy_v1(policy, route=ROUTES[0], evaluated_on=TODAY) == before
    )
