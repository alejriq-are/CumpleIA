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
identity_material = cases.bound_material


@pytest.fixture
def bound_material(identity_material):
    doc, ctx = identity_material
    doc["declared_consent_giver"] = "representante_legal"
    ctx["consent_assessment"] = {"given_by": "representante_legal"}
    ctx["special_conditions_document"] = {
        "declarations": [
            {
                "question_id": q,
                "answer": answer,
                "rationale": "PRUEBA: declaracion ficticia",
            }
            for q, answer in [
                ("ninos_ninas", "si"),
                ("adolescentes", "no"),
                ("datos_sensibles_adolescentes_menores_16", "no"),
            ]
        ],
        "conditions": [
            {
                "regime_id": "infancia_adolescencia_art16quater",
                "authorization_route": "consentimiento",
            }
        ],
    }
    return doc, ctx


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


@pytest.mark.parametrize(
    "change",
    [
        "missing_special",
        "missing_consent",
        "mismatch_giver",
        "parent_not_mapped",
        "different_scope",
        "missing_condition",
        "mismatch_declaration",
        "pending_declaration",
        "mismatch_route",
    ],
)
def test_current_identity_cannot_hide_related_document_incoherence(
    bound_material, change
):
    doc, ctx = bound_material
    if change == "missing_special":
        ctx["special_conditions_document"] = None
    elif change == "missing_consent":
        ctx["consent_assessment"] = None
    elif change == "mismatch_giver":
        ctx["consent_assessment"]["given_by"] = "titular"
    elif change == "parent_not_mapped":
        doc["declared_consent_giver"] = "padre_madre"
    elif change == "different_scope":
        ctx["special_conditions_document"]["declarations"][0]["data_subject_codes"] = [
            "ajeno"
        ]
    elif change == "missing_condition":
        ctx["special_conditions_document"]["conditions"] = []
    elif change == "mismatch_declaration":
        ctx["special_conditions_document"]["declarations"][0]["answer"] = "no"
    elif change == "pending_declaration":
        ctx["special_conditions_document"]["declarations"][0]["answer"] = "pendiente"
    else:
        ctx["special_conditions_document"]["conditions"][0][
            "authorization_route"
        ] = "excepcion_legal"
    result = build(bind(doc, ctx), ctx)
    assert result.documentary_result == "completo"
    assert result.association_status == "vigente"
    assert result.result in ("incompleto", "requiere_revision")
    assert result.issues
    assert not result.can_confirm and not result.authorizes_action


def test_sensitive_consent_presence_is_checked_separately(bound_material):
    doc, ctx = bound_material
    rat = ctx["rat_context_snapshot"]
    rat["data_categories"][0]["is_sensitive"] = True
    rat["special_regimes"]["has_sensitive_data"] = True
    result = build(bind(doc, ctx), ctx)
    assert any(
        i.code == "consentimiento_sensible_relacionado_pendiente" for i in result.issues
    )
    assert result.association_status == "vigente"
    assert not result.can_confirm


def test_special_declaration_cannot_create_sensitive_under16_cross(bound_material):
    doc, ctx = bound_material
    doc["declared_groups"] = ["adolescentes"]
    rat = ctx["rat_context_snapshot"]
    rat["data_subjects"][0].update(includes_children=False, includes_adolescents=True)
    rat["special_regimes"].update(includes_children=False, includes_adolescents=True)
    declarations = ctx["special_conditions_document"]["declarations"]
    for declaration, answer in zip(declarations, ["no", "si", "si"], strict=True):
        declaration["answer"] = answer
    result = build(bind(doc, ctx), ctx)
    assert result.documentary_result == "completo"
    assert result.result == "requiere_revision"
    assert any(i.code == "declaracion_edad_incoherente" for i in result.issues)
