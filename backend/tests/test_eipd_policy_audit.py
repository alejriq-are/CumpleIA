"""Auditoria pura con politica sintetica; no activa resolver real."""

from copy import deepcopy
from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from pydantic import ValidationError

from app.services.eipd_policy import resolve_eipd_gate_policy_v1
from app.services.eipd_policy_audit import (
    EipdPolicyAuditSnapshotV1,
    EipdPolicyPublicationV1,
    EipdPolicySelectionRequestV1,
    build_eipd_confirmation_evidence_v1,
    build_eipd_policy_publication_v1,
    plan_eipd_policy_selection_v1,
)
from tests import test_services_eipd_policy as fixtures

policy = fixtures.policy
frontier_context = fixtures.frontier_context
complete_resolution = fixtures.complete_resolution
prepared_controls = fixtures.prepared_controls
NOW = datetime(2026, 10, 7, 15, tzinfo=UTC)
ACTOR = UUID(int=100)


def publication(policy, n=1):
    return build_eipd_policy_publication_v1(
        policy,
        publication_id=UUID(int=n),
        actor_id=ACTOR,
        created_at=NOW - timedelta(hours=1),
        rationale="Revision fundada",
        evidence_reference="TEST: evidencia",
    )


def plan(state, target, revision=0, n=10):
    return plan_eipd_policy_selection_v1(
        state,
        dict(publication_id=target, expected_revision=revision),
        event_id=UUID(int=n),
        actor_id=ACTOR,
        created_at=NOW,
        rationale="Seleccion fundada",
        evidence_reference="TEST: seleccion",
    )


def selected(policy):
    p = publication(policy)
    state = dict(publications=[p], selections=[], selector=None)
    result = plan(state, p.id)
    return dict(publications=[p], selections=[result.event], selector=result.selector)


def test_publish_select_bootstrap_and_revoke_are_pure(policy):
    initial = deepcopy(policy)
    state = selected(policy)
    second = deepcopy(policy)
    second["policy_reference"] += " revocada"
    second["activation"] = "deshabilitada"
    p2 = publication(second, 2)
    state["publications"].append(p2)
    before = deepcopy(state)
    result = plan(state, p2.id, 1, 11)
    assert result.event.previous_policy_hash == state["publications"][0].policy_hash
    assert result.event.revision == 2
    assert result.selector.publication_id == p2.id
    assert state == before and policy == initial
    with pytest.raises(ValidationError):
        result.event.revision = 4
    assert resolve_eipd_gate_policy_v1().activation == "deshabilitada"


@pytest.mark.parametrize(
    "mode", ["hash", "extra", "naive", "empty", "version", "mutated_policy"]
)
def test_publication_closed_and_hash_checked(policy, mode):
    p = publication(policy)
    data = p.model_dump(mode="python")
    if mode == "hash":
        data["policy_hash"] = "a" * 64
    elif mode == "extra":
        data["approved"] = True
    elif mode == "naive":
        data["created_at"] = NOW.replace(tzinfo=None)
    elif mode == "empty":
        data["evidence_reference"] = " "
    elif mode == "version":
        data["policy"]["policy_version"] = True
    else:
        p.policy.policy_reference += " mutada"
        data = p.model_dump(mode="python")
    with pytest.raises(ValidationError):
        EipdPolicyPublicationV1.model_validate(data)


@pytest.mark.parametrize(
    "mode",
    ["stale", "unknown", "reuse", "duplicate_event", "early", "naive", "bool", "extra"],
)
def test_selection_plan_rejects_invalid_inputs(policy, mode):
    state = selected(policy)
    p2policy = deepcopy(policy)
    p2policy["policy_reference"] += " nueva"
    p2 = publication(p2policy, 2)
    state["publications"].append(p2)
    request = dict(publication_id=p2.id, expected_revision=1)
    args = dict(
        event_id=UUID(int=11),
        actor_id=ACTOR,
        created_at=NOW,
        rationale="Seleccion",
        evidence_reference="TEST",
    )
    if mode == "stale":
        request["expected_revision"] = 0
    elif mode == "unknown":
        request["publication_id"] = UUID(int=999)
    elif mode == "reuse":
        request["publication_id"] = UUID(int=1)
    elif mode == "duplicate_event":
        args["event_id"] = UUID(int=10)
    elif mode == "early":
        args["created_at"] = NOW - timedelta(days=1)
    elif mode == "naive":
        args["created_at"] = NOW.replace(tzinfo=None)
    elif mode == "bool":
        request["expected_revision"] = True
    else:
        request["activation"] = "habilitada"
    with pytest.raises((ValueError, ValidationError)):
        plan_eipd_policy_selection_v1(state, request, **args)


@pytest.mark.parametrize(
    "mode",
    [
        "missing_selector",
        "selector_revision",
        "selector_event",
        "selector_publication",
        "missing_publication",
        "hash",
        "gap",
        "previous_partial",
        "duplicate_reference",
        "duplicate_publication",
        "extra",
        "mutated_nested",
    ],
)
def test_snapshot_rejects_corruption(policy, mode):
    state = EipdPolicyAuditSnapshotV1.model_validate(selected(policy))
    data = state.model_dump(mode="python")
    if mode == "missing_selector":
        data["selector"] = None
    elif mode == "selector_revision":
        data["selector"]["revision"] = 2
    elif mode == "selector_event":
        data["selector"]["selection_id"] = UUID(int=999)
    elif mode == "selector_publication":
        data["selector"]["publication_id"] = UUID(int=999)
    elif mode == "missing_publication":
        data["publications"] = []
    elif mode == "hash":
        data["selections"][0]["policy_hash"] = "a" * 64
    elif mode == "gap":
        data["selections"][0]["revision"] = 3
    elif mode == "previous_partial":
        data["selections"][0]["previous_policy_hash"] = "a" * 64
    elif mode in ("duplicate_reference", "duplicate_publication"):
        other = deepcopy(data["publications"][0])
        if mode == "duplicate_reference":
            other["id"] = UUID(int=2)
        data["publications"] = [*data["publications"], other]
    elif mode == "extra":
        data["authorized"] = True
    else:
        state.publications[0].policy.policy_reference += " alterada"
        data = state.model_dump(mode="python")
    with pytest.raises(ValidationError):
        EipdPolicyAuditSnapshotV1.model_validate(data)


@pytest.mark.parametrize("biometric", [False, True])
def test_confirmation_evidence_recomputes_controls(
    policy, prepared_controls, biometric
):
    identity = fixtures.add_review(prepared_controls, policy)
    state = selected(policy)
    before = deepcopy(prepared_controls)
    result = build_eipd_confirmation_evidence_v1(
        state,
        prepared_controls,
        identity,
        evidence_id=UUID(int=20),
        actor_id=ACTOR,
        created_at=NOW,
    )
    assert result.policy_hash == identity["policy_hash"]
    assert str(result.review_id) == str(identity["review_id"])
    assert result.selector_revision == 1 and result.selection_id == UUID(int=10)
    assert str(result.organization_id) == str(prepared_controls["organization_id"])
    assert prepared_controls == before
    with pytest.raises(ValidationError):
        result.policy_hash = "b" * 64


@pytest.mark.parametrize(
    "mode",
    [
        "negative",
        "old_policy",
        "other_review",
        "tenant",
        "assessment",
        "document",
        "ordinary",
        "disabled",
        "missing_selector",
        "early",
        "naive",
        "mutated_version",
    ],
)
def test_evidence_cannot_bypass_controls(policy, prepared_controls, mode):
    identity = fixtures.add_review(prepared_controls, policy)
    state = selected(policy)
    created_at = NOW
    if mode == "negative":
        prepared_controls["latest_review"]["decision"] = "no_continuar"
    elif mode == "old_policy":
        identity["policy_hash"] = "a" * 64
    elif mode == "other_review":
        identity["review_id"] = UUID(int=999)
    elif mode == "tenant":
        prepared_controls["latest_review"]["organization_id"] = UUID(int=999)
    elif mode == "assessment":
        prepared_controls["latest_review"]["assessment_id"] = UUID(int=999)
    elif mode == "document":
        prepared_controls["resolution"]["notes"] = "Cambio"
    elif mode == "ordinary":
        prepared_controls["context"]["contract_assessment"] = None
    elif mode == "disabled":
        policy["activation"] = "deshabilitada"
        state = selected(policy)
        identity = fixtures.add_review(prepared_controls, policy)
    elif mode == "missing_selector":
        state = dict(publications=[], selections=[], selector=None)
    elif mode == "early":
        created_at = NOW - timedelta(days=1)
    elif mode == "naive":
        created_at = NOW.replace(tzinfo=None)
    else:
        from app.services.eipd_controls import EipdControlCompositionInputV1

        prepared_controls = EipdControlCompositionInputV1.model_validate(
            prepared_controls
        )
        prepared_controls.assessment_schema_version = True
    with pytest.raises((ValueError, ValidationError)):
        build_eipd_confirmation_evidence_v1(
            state,
            prepared_controls,
            identity,
            evidence_id=UUID(int=20),
            actor_id=ACTOR,
            created_at=created_at,
        )


@pytest.mark.parametrize("value", [True, -1, "1", 1.0])
def test_revision_strict(value):
    with pytest.raises(ValidationError):
        EipdPolicySelectionRequestV1(
            publication_id=UUID(int=1), expected_revision=value
        )


@pytest.mark.parametrize(
    "mode",
    [
        "valid",
        "previous_hash",
        "previous_publication",
        "reverse_time",
        "reselect_old",
        "plan_mismatch",
    ],
)
def test_full_chain_and_plan_coherence(policy, mode):
    from app.services.eipd_policy_audit import EipdPolicySelectionPlanV1

    state = selected(policy)
    second = deepcopy(policy)
    second["policy_reference"] += " segunda"
    state["publications"].append(publication(second, 2))
    result = plan(state, UUID(int=2), 1, 11)
    state["selections"].append(result.event)
    state["selector"] = result.selector
    if mode == "valid":
        assert EipdPolicyAuditSnapshotV1.model_validate(state).selector.revision == 2
        return
    if mode == "plan_mismatch":
        raw = result.model_dump(mode="python")
        raw["selector"]["selection_id"] = UUID(int=999)
        with pytest.raises(ValidationError):
            EipdPolicySelectionPlanV1.model_validate(raw)
        return
    if mode == "reselect_old":
        with pytest.raises(ValueError):
            plan(state, UUID(int=1), 2, 12)
        return
    raw = EipdPolicyAuditSnapshotV1.model_validate(state).model_dump(mode="python")
    if mode == "previous_hash":
        raw["selections"][1]["previous_policy_hash"] = "b" * 64
    elif mode == "previous_publication":
        raw["selections"][1]["previous_publication_id"] = UUID(int=999)
    else:
        raw["selections"][1]["created_at"] = NOW - timedelta(minutes=1)
    with pytest.raises(ValidationError):
        EipdPolicyAuditSnapshotV1.model_validate(raw)
