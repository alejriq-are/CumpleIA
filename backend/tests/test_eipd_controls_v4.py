"""Composicion ficticia completa, sin promocionar representacion o politica."""

from copy import deepcopy
from datetime import date

import pytest
from pydantic import ValidationError

from app.services.eipd_controls_v4 import EipdControlCompositionInputV4
from app.services.eipd_controls_v4 import compose_eipd_controls_v4 as compose
from app.services.eipd_resolution_binding_v3 import bind_eipd_resolution_v3
from tests import test_eipd_resolution_binding_v3 as cases

complete_resolution = cases.complete_resolution
context = cases.context
materials = cases.materials
represented = cases.represented
DAY = date(2026, 10, 14)


@pytest.fixture
def value(represented):
    document, ctx = represented
    return dict(
        assessment=dict(
            organization_id="a0000000-0000-0000-0000-000000000001",
            treatment_id="a0000000-0000-0000-0000-000000000002",
            assessment_id="a0000000-0000-0000-0000-000000000003",
            assessment_status="borrador",
            assessment_schema_version=1,
            rat_context_schema_version=1,
            justification="PRUEBA",
            rat_context_current=True,
            context=ctx,
            resolution=bind_eipd_resolution_v3(document, ctx).model_dump(mode="json"),
            latest_review=None,
        ),
        policy=None,
        latest_review_policy=None,
    )


@pytest.mark.parametrize("research_present", [True, False])
def test_shared_controls_and_representation_are_kept_without_authority(
    value, research_present
):
    if not research_present:
        value["assessment"]["context"].update(
            research_assessment=None, special_conditions=None
        )
    before = deepcopy(value)
    result = compose(value, evaluated_on=DAY)
    assert result.evaluation_version == 4
    assert result.preparation_result == "requiere_revision"
    assert result.ordinary is not None and result.representation is not None
    assert not result.can_confirm and not result.authorizes_action
    for issues in (
        result.preparation_issues,
        result.review_blockers,
        result.confirmation_blockers,
    ):
        assert any(i.code == "politica_representacion_no_implementada" for i in issues)
    assert any(i.code == "revision_ausente" for i in result.confirmation_blockers)
    if not research_present:
        assert not any(
            i.code == "investigacion_confirmacion_bloqueada"
            for i in result.preparation_issues
        )
    assert result == compose(
        EipdControlCompositionInputV4.model_validate(value), evaluated_on=DAY
    )
    assert value == before


def test_missing_context_remains_diagnosed_and_blocked(value):
    value["assessment"]["context"] = None
    result = compose(value, evaluated_on=DAY)
    assert result.representation is None and result.context_metadata is None
    assert not result.can_confirm
    assert any(
        i.code == "contexto_rat_no_disponible" for i in result.preparation_issues
    )


def test_independent_identity_failure_is_preserved(value):
    value["assessment"]["treatment_id"] = "a0000000-0000-0000-0000-000000000099"
    result = compose(value, evaluated_on=DAY)
    assert any(
        i.code == "asociacion_contexto_obsoleta" for i in result.representation.issues
    )
    assert any(
        i.code == "asociacion_contexto_obsoleta" for i in result.preparation_issues
    )
    assert not result.can_confirm


@pytest.mark.parametrize(
    "field,value_bad",
    [
        ("assessment_schema_version", True),
        ("rat_context_current", 1),
        ("can_confirm", True),
    ],
)
def test_closed_input_rejects_injected_or_loose_flags(value, field, value_bad):
    value["assessment"][field] = value_bad
    with pytest.raises(ValidationError):
        compose(value, evaluated_on=DAY)


@pytest.mark.parametrize("decision", ["continuar", "requiere_cambios", "no_continuar"])
def test_fictitious_current_review_does_not_remove_representation_barrier(
    value, decision
):
    from app.services.eipd_policy import build_eipd_policy_hash_v1
    from app.services.eipd_resolution_binding_v3 import (
        build_eipd_resolution_document_hash_v3,
    )

    assessment = value["assessment"]
    document = assessment["resolution"]
    review = dict(
        id="a0000000-0000-0000-0000-000000000004",
        organization_id=assessment["organization_id"],
        assessment_id=assessment["assessment_id"],
        created_by="a0000000-0000-0000-0000-000000000005",
        decision=decision,
        rationale="PRUEBA: revision ficticia",
        review_reference="PRUEBA",
        document_hash=build_eipd_resolution_document_hash_v3(document),
        context_hash=document["context_binding"]["context_hash"],
        created_at="2026-10-14T12:00:00Z",
    )
    policy = dict(
        policy_version=1,
        policy_reference="PRUEBA",
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
    assessment["latest_review"] = review
    value.update(
        policy=policy,
        latest_review_policy=dict(
            review_id=review["id"],
            policy_version=1,
            policy_reference="PRUEBA",
            policy_hash=build_eipd_policy_hash_v1(policy),
        ),
    )
    result = compose(value, evaluated_on=DAY)
    assert result.review_state.review_status == "vigente"
    assert result.review_policy_status == "vigente"
    assert any(
        i.code == "politica_representacion_no_implementada"
        for i in result.confirmation_blockers
    )
    assert not result.can_confirm and not result.authorizes_action
