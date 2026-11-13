"""Asociacion documental con fixtures ficticios, sin facultades o gate."""

from copy import deepcopy

import pytest
from pydantic import ValidationError

from app.services.sensitive_representation_binding import (
    bind_sensitive_representation_v1 as bind,
)
from app.services.sensitive_representation_binding import (
    evaluate_sensitive_representation_association_v1 as evaluate,
)
from tests import test_services_research as research

context = research.context


@pytest.fixture
def material(context):
    _, rat, _ = context
    return (
        {
            "representation_kind": "mandatario",
            "authority_document_reference": "PRUEBA: documento",
        },
        {
            "organization_id": "a0000000-0000-0000-0000-000000000001",
            "treatment_id": "a0000000-0000-0000-0000-000000000002",
            "assessment_id": "a0000000-0000-0000-0000-000000000003",
            "rat_context_snapshot": rat,
            "legal_basis": "consentimiento_art12",
            "consent_assessment": {"given_by": "mandatario"},
            "sensitive_consent_assessment": {},
        },
    )


def test_deterministic_binding_does_not_mutate_or_authorize(material):
    document, ctx = material
    original = deepcopy(material)
    bound = bind(document, ctx)
    assert bind(document, dict(reversed(list(ctx.items())))) == bound
    assert material == original
    result = evaluate(bound, ctx)
    assert result.result == "vigente" and not result.can_confirm
    assert bound.context_binding.context_hash != bound.context_binding.document_hash
    assert evaluate(bound.model_dump(mode="json"), ctx) == result


@pytest.mark.parametrize(
    "field",
    [
        "organization_id",
        "treatment_id",
        "assessment_id",
        "legal_basis",
        "consent_assessment",
        "sensitive_consent_assessment",
        "rat_context_snapshot",
    ],
)
def test_changed_context_invalidates_binding(material, field):
    document, ctx = material
    bound = bind(document, ctx)
    if field.endswith("_id"):
        ctx[field] = "a0000000-0000-0000-0000-000000000004"
    elif field == "legal_basis":
        ctx[field] = "interes_legitimo_art13d"
    elif field == "consent_assessment":
        ctx[field]["given_by"] = "representante_legal"
    elif field == "sensitive_consent_assessment":
        ctx[field]["notes"] = "PRUEBA: material distinto"
    else:
        ctx[field]["purpose"] = "PRUEBA: otra finalidad"
    result = evaluate(bound, ctx)
    assert result.issues == ("asociacion_contexto_obsoleta",)
    assert not result.can_confirm


def test_document_change_needs_explicit_rebinding(material):
    document, ctx = material
    old = bind(document, ctx)
    changed = old.model_dump(mode="json")
    changed["assessment"]["authority_document_version"] = "PRUEBA-2"
    assert evaluate(changed, ctx).issues == ("asociacion_documento_obsoleta",)
    fresh = bind(changed["assessment"], ctx)
    assert evaluate(fresh, ctx).result == "vigente"
    assert not evaluate(fresh, ctx).can_confirm
    assert old.assessment.authority_document_version is None


def test_missing_document_requires_review(material):
    _, ctx = material
    result = evaluate(None, ctx)
    assert result.issues == ("asociacion_ausente",) and not result.can_confirm


@pytest.mark.parametrize(
    "field,value",
    [
        ("context_schema_version", 2),
        ("organization_id", "invalido"),
        ("legal_basis", "inventada"),
        ("can_confirm", True),
    ],
)
def test_invalid_context_is_not_hidden_by_missing_document(material, field, value):
    _, ctx = material
    ctx[field] = value
    with pytest.raises(ValidationError):
        evaluate(None, ctx)


@pytest.mark.parametrize(
    "field,value",
    [
        ("binding_version", 2),
        ("context_hash", "invalido"),
        ("document_hash", "invalido"),
        ("accepted_by", "PRUEBA"),
    ],
)
def test_invalid_binding_rejected(material, field, value):
    document, ctx = material
    bound = bind(document, ctx).model_dump(mode="json")
    bound["context_binding"][field] = value
    with pytest.raises(ValidationError):
        evaluate(bound, ctx)


def test_both_context_and_document_changes_are_reported(material):
    document, ctx = material
    bound = bind(document, ctx).model_dump(mode="json")
    bound["assessment"]["notes"] = "PRUEBA: documento modificado"
    ctx["consent_assessment"]["notes"] = "PRUEBA: contexto modificado"
    result = evaluate(bound, ctx)
    assert result.issues == (
        "asociacion_contexto_obsoleta",
        "asociacion_documento_obsoleta",
    )
    assert result.result == "requiere_revision" and not result.can_confirm
