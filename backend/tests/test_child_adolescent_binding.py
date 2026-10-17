"""Identidad ficticia por tenant/padre/material, sin autoridad ni cambios historicos."""

from copy import deepcopy

import pytest
from pydantic import ValidationError

from app.services.child_adolescent_binding import (
    bind_child_adolescent_v1 as bind,
)
from app.services.child_adolescent_binding import (
    build_child_adolescent_context_hash_v1 as context_hash,
)
from app.services.child_adolescent_binding import (
    evaluate_child_adolescent_association_v1 as evaluate,
)
from tests import test_child_adolescent as cases

context = cases.context
material = cases.material


@pytest.fixture
def bound_material(material):
    doc, rat = material
    ctx = dict(
        organization_id="a0000000-0000-0000-0000-000000000001",
        treatment_id="a0000000-0000-0000-0000-000000000002",
        assessment_id="a0000000-0000-0000-0000-000000000003",
        rat_context_snapshot=rat,
        legal_basis="consentimiento_art12",
        consent_assessment=None,
        sensitive_consent_assessment=None,
        special_conditions_document=None,
        sensitive_representation_assessment=None,
    )
    return doc, ctx


def test_identity_deterministic_roundtrip_no_mutation_or_authority(bound_material):
    doc, ctx = bound_material
    before = deepcopy(bound_material)
    bound = bind(doc, ctx)
    assert bind(doc, dict(reversed(list(ctx.items())))) == bound
    assert bound_material == before
    result = evaluate(bound.model_dump(mode="json"), ctx)
    assert result.result == "vigente"
    assert not result.can_confirm and not result.authorizes_action
    assert bound.context_binding.context_hash != bound.context_binding.document_hash


@pytest.mark.parametrize(
    "field",
    [
        "organization_id",
        "treatment_id",
        "assessment_id",
        "rat_context_snapshot",
        "legal_basis",
        "consent_assessment",
        "sensitive_consent_assessment",
        "special_conditions_document",
    ],
)
def test_changed_parent_or_context_requires_explicit_reaporte(bound_material, field):
    doc, ctx = bound_material
    original = bind(doc, ctx)
    changed = deepcopy(ctx)
    if field.endswith("_id"):
        changed[field] = "a0000000-0000-0000-0000-000000000099"
    elif field == "rat_context_snapshot":
        changed[field]["purpose"] = "PRUEBA: otra finalidad"
    elif field == "legal_basis":
        changed[field] = None
    else:
        changed[field] = {}
    assert evaluate(original, changed).issues == ("asociacion_contexto_obsoleta",)
    assert evaluate(bind(doc, changed), changed).result == "vigente"
    assert original.context_binding.context_hash == context_hash(ctx)


def test_changed_document_cannot_reuse_saved_hash(bound_material):
    doc, ctx = bound_material
    bound = bind(doc, ctx).model_dump(mode="json")
    bound["assessment"]["notes"] = "PRUEBA: cambio posterior"
    assert evaluate(bound, ctx).issues == ("asociacion_documento_obsoleta",)


def test_absence_validates_context_and_requires_revision(bound_material):
    _, ctx = bound_material
    assert evaluate(None, ctx).issues == ("asociacion_ausente",)
    with pytest.raises(ValidationError):
        evaluate(None, {})


@pytest.mark.parametrize("change", ["version", "hash", "extra", "missing_nullable"])
def test_closed_versioned_contracts_reject_injection(bound_material, change):
    doc, ctx = bound_material
    bound = bind(doc, ctx).model_dump(mode="json")
    if change == "version":
        bound["context_binding"]["binding_version"] = 2
    elif change == "hash":
        bound["context_binding"]["document_hash"] = "invalid"
    elif change == "extra":
        bound["can_confirm"] = True
    else:
        del ctx["special_conditions_document"]
    with pytest.raises(ValidationError):
        evaluate(bound, ctx)


def test_representation_change_invalidates_child_identity(bound_material):
    from app.services.sensitive_representation_binding import (
        bind_sensitive_representation_v1,
    )

    doc, ctx = bound_material
    bound = bind(doc, ctx)
    related = {
        field: ctx[field]
        for field in (
            "organization_id",
            "treatment_id",
            "assessment_id",
            "rat_context_snapshot",
            "legal_basis",
            "consent_assessment",
            "sensitive_consent_assessment",
        )
    }
    changed = deepcopy(ctx)
    changed["sensitive_representation_assessment"] = bind_sensitive_representation_v1(
        {}, related
    ).model_dump(mode="json")
    assert evaluate(bound, changed).issues == ("asociacion_contexto_obsoleta",)
    assert evaluate(bind(doc, changed), changed).result == "vigente"


def test_special_binding_is_not_silently_projected_or_accepted(bound_material):
    doc, ctx = bound_material
    ctx["special_conditions_document"] = {"context_binding": {"schema_version": 1}}
    with pytest.raises(ValidationError):
        bind(doc, ctx)
