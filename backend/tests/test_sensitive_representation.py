"""Completitud de documentos ficticios, sin verificar facultad o consentimiento."""

from copy import deepcopy
from datetime import date

import pytest

from app.services.sensitive_representation import (
    evaluate_sensitive_representation_v1 as evaluate,
)
from app.services.sensitive_representation_binding import (
    bind_sensitive_representation_v1 as bind,
)
from tests import test_services_research as research

context = research.context
DAY = date(2026, 10, 14)


@pytest.fixture
def material(context):
    _, rat, _ = context
    scope = {
        "data_category_codes": [
            item["category_code"] for item in rat["data_categories"]
        ],
        "data_subject_codes": [item["category_code"] for item in rat["data_subjects"]],
    }
    doc = {
        key: "PRUEBA: declaracion ficticia, no validada"
        for key in (
            "representative_reference",
            "represented_subjects_reference",
            "authority_document_reference",
            "authority_document_version",
            "authority_basis_description",
            "express_authority_analysis",
            "scope_match_analysis",
            "validity_analysis",
            "limitations",
            "revocation_information",
        )
    }
    doc.update(
        representation_kind="mandatario",
        scope=scope,
        evidence=[{"evidence_type": "PRUEBA", "reference": "PRUEBA: evidencia"}],
    )
    ctx = {
        "organization_id": "a0000000-0000-0000-0000-000000000001",
        "treatment_id": "a0000000-0000-0000-0000-000000000002",
        "assessment_id": "a0000000-0000-0000-0000-000000000003",
        "rat_context_snapshot": rat,
        "legal_basis": "consentimiento_art12",
        "consent_assessment": {"given_by": "mandatario"},
        "sensitive_consent_assessment": {"scope": scope},
    }
    return doc, ctx


def test_complete_material_is_deterministic_and_never_authorizes(material):
    doc, ctx = material
    bound = bind(doc, ctx)
    before = deepcopy(bound)
    result = evaluate(bound, ctx, evaluated_on=DAY)
    assert result.result == "completo" and result.issues == ()
    assert not result.can_confirm and bound == before
    assert evaluate(bound.model_dump(mode="json"), ctx, evaluated_on=DAY) == result


@pytest.mark.parametrize(
    "field",
    [
        "representation_kind",
        "representative_reference",
        "represented_subjects_reference",
        "authority_document_reference",
        "authority_document_version",
        "authority_basis_description",
        "express_authority_analysis",
        "scope_match_analysis",
        "validity_analysis",
        "limitations",
        "revocation_information",
        "scope",
        "evidence",
    ],
)
def test_missing_material_has_specific_field_issue(material, field):
    doc, ctx = material
    doc.pop(field)
    result = evaluate(bind(doc, ctx), ctx, evaluated_on=DAY)
    assert result.result == "incompleto"
    assert any(issue.field == field for issue in result.issues)
    assert not result.can_confirm


@pytest.mark.parametrize(
    "field", ["includes_children", "includes_adolescents", "has_vulnerable_groups"]
)
def test_concurrent_regimes_remain_under_review(material, field):
    doc, ctx = material
    ctx["rat_context_snapshot"]["special_regimes"][field] = True
    result = evaluate(bind(doc, ctx), ctx, evaluated_on=DAY)
    assert result.result == "requiere_revision" and not result.can_confirm


def test_subject_flag_is_not_hidden_by_aggregate_flag(material):
    doc, ctx = material
    ctx["rat_context_snapshot"]["data_subjects"][0]["includes_children"] = True
    result = evaluate(bind(doc, ctx), ctx, evaluated_on=DAY)
    assert any(issue.field == "rat.includes_children" for issue in result.issues)


@pytest.mark.parametrize(
    "field,value",
    [
        ("issued_on", "2026-10-15"),
        ("valid_from", "2026-10-15"),
        ("valid_until", "2026-10-13"),
    ],
)
def test_documented_dates_require_review(material, field, value):
    doc, ctx = material
    doc[field] = value
    result = evaluate(bind(doc, ctx), ctx, evaluated_on=DAY)
    assert result.result == "requiere_revision"
    assert any(issue.field == field for issue in result.issues)


def test_final_day_is_not_expired_and_no_duration_is_invented(material):
    doc, ctx = material
    doc["valid_until"] = DAY
    assert evaluate(bind(doc, ctx), ctx, evaluated_on=DAY).result == "completo"
    doc.pop("valid_until")
    assert evaluate(bind(doc, ctx), ctx, evaluated_on=DAY).result == "completo"


@pytest.mark.parametrize(
    "change",
    [
        "kind",
        "basis",
        "rat_scope",
        "sensitive_scope",
        "missing_sensitive_scope",
        "evidence_reference",
    ],
)
def test_incompatible_or_incomplete_material_remains_blocked(material, change):
    doc, ctx = material
    if change == "kind":
        doc["representation_kind"] = "representante_legal"
    elif change == "basis":
        ctx["legal_basis"] = "interes_legitimo_art13d"
    elif change == "rat_scope":
        doc["scope"] = {"data_category_codes": [], "data_subject_codes": []}
    elif change == "sensitive_scope":
        ctx["sensitive_consent_assessment"]["scope"] = {
            "data_category_codes": [],
            "data_subject_codes": [],
        }
    elif change == "missing_sensitive_scope":
        ctx["sensitive_consent_assessment"] = None
    else:
        doc["evidence"] = [{"evidence_type": "PRUEBA", "reference": " "}]
    result = evaluate(bind(doc, ctx), ctx, evaluated_on=DAY)
    assert result.result != "completo" and not result.can_confirm


def test_stale_binding_is_not_concealed_by_complete_material(material):
    doc, ctx = material
    bound = bind(doc, ctx)
    ctx["consent_assessment"]["notes"] = "PRUEBA: cambio"
    result = evaluate(bound, ctx, evaluated_on=DAY)
    assert result.result == "requiere_revision"
    assert any(issue.code == "asociacion_contexto_obsoleta" for issue in result.issues)


def test_missing_and_titular_paths_never_authorize(material):
    _, ctx = material
    assert evaluate(None, ctx, evaluated_on=DAY).result == "incompleto"
    ctx["consent_assessment"]["given_by"] = "titular"
    result = evaluate(None, ctx, evaluated_on=DAY)
    assert result.result == "no_aplicable" and not result.can_confirm
    ctx["consent_assessment"] = None
    assert evaluate(None, ctx, evaluated_on=DAY).result == "incompleto"
