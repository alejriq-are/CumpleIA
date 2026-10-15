"""Identidad vigente y campos completos se comprueban separadamente."""

from copy import deepcopy

import pytest
from pydantic import ValidationError

from app.schemas.child_adolescent import ChildAdolescentReadinessOutV1
from app.services.child_adolescent_binding import bind_child_adolescent_v1 as bind
from app.services.child_adolescent_readiness import (
    build_child_adolescent_readiness_v1 as build,
)
from tests import test_child_adolescent_binding as cases

context = cases.context
material = cases.material
bound_material = cases.bound_material


def test_complete_current_document_never_authorizes(bound_material):
    doc, ctx = bound_material
    bound = bind(doc, ctx)
    before = deepcopy((bound, ctx))
    result = build(bound, ctx)
    assert result.result == result.documentary_result == "completo"
    assert result.association_status == "vigente"
    assert not result.can_confirm and not result.authorizes_action
    assert result == ChildAdolescentReadinessOutV1.model_validate_json(
        result.model_dump_json()
    )
    assert (bound, ctx) == before


@pytest.mark.parametrize("change", ["context", "document", "parent"])
def test_complete_but_stale_document_still_requires_review(bound_material, change):
    doc, ctx = bound_material
    bound = bind(doc, ctx).model_dump(mode="json")
    if change == "context":
        ctx["rat_context_snapshot"]["purpose"] = "PRUEBA: otra finalidad"
    elif change == "parent":
        ctx["organization_id"] = "a0000000-0000-0000-0000-000000000099"
    else:
        bound["assessment"]["notes"] = "PRUEBA: cambio"
    result = build(bound, ctx)
    assert result.documentary_result == "completo"
    assert result.result == "requiere_revision"
    assert result.association_status == "requiere_revision"
    assert any(i.field == "context_binding" for i in result.issues)


def test_current_identity_does_not_complete_missing_content(bound_material):
    doc, ctx = bound_material
    doc["best_interests_analysis"] = " "
    result = build(bind(doc, ctx), ctx)
    assert result.association_status == "vigente"
    assert result.result == "incompleto"


def test_absence_and_non_applicability_are_distinct(bound_material):
    _, ctx = bound_material
    assert build(None, ctx).result == "incompleto"
    rat = ctx["rat_context_snapshot"]
    rat["data_subjects"][0]["includes_children"] = False
    rat["special_regimes"]["includes_children"] = False
    result = build(None, ctx)
    assert result.result == result.association_status == "no_aplicable"
    assert result.issues == []


@pytest.mark.parametrize("change", ["confirm", "authority", "fake_complete", "extra"])
def test_output_contract_rejects_authority_or_incoherence(bound_material, change):
    doc, ctx = bound_material
    doc["best_interests_analysis"] = None
    raw = build(bind(doc, ctx), ctx).model_dump(mode="json")
    if change == "confirm":
        raw["can_confirm"] = True
    elif change == "authority":
        raw["authorizes_action"] = True
    elif change == "fake_complete":
        raw["result"] = "completo"
    else:
        raw["action_context"] = {}
    with pytest.raises(ValidationError):
        ChildAdolescentReadinessOutV1.model_validate(raw)


def test_invalid_context_not_hidden_by_document_absence():
    with pytest.raises(ValidationError):
        build(None, {})


@pytest.mark.parametrize(
    "change",
    [
        "no_applicability_with_identity",
        "pending_without_issues",
        "complete_stale_identity",
    ],
)
def test_output_cannot_hide_documentary_or_identity_pending_state(
    bound_material, change
):
    doc, ctx = bound_material
    raw = build(bind(doc, ctx), ctx).model_dump(mode="json")
    if change == "no_applicability_with_identity":
        raw["documentary_result"] = raw["result"] = "no_aplicable"
    elif change == "pending_without_issues":
        raw["documentary_result"] = "incompleto"
    else:
        raw["association_status"] = "requiere_revision"
    with pytest.raises(ValidationError):
        ChildAdolescentReadinessOutV1.model_validate(raw)
