"""Binding ficticio sucesor; identidad documental sin autoridad operativa."""

from copy import deepcopy

import pytest
from pydantic import ValidationError

from app.schemas.licitud import (
    EipdResolutionAssessmentStoredV1,
    EipdResolutionAssessmentStoredV2,
)
from app.services.eipd_resolution_binding_v2 import (
    EipdResolutionContextV2,
    build_eipd_resolution_context_hash_v2,
)
from app.services.eipd_resolution_binding_v3 import (
    EipdResolutionContextV3,
    bind_eipd_resolution_v3,
    build_eipd_resolution_context_hash_v3,
    build_eipd_resolution_document_hash_v3,
    eipd_resolution_context_is_current_v3,
)
from app.services.sensitive_representation_binding import (
    bind_sensitive_representation_v1,
)
from tests import test_eipd_resolution_binding_v2 as previous

complete_resolution = previous.complete_resolution
context = previous.context
materials = previous.materials


@pytest.fixture
def represented(materials):
    document, ctx = deepcopy(materials)
    binding_context = {
        "organization_id": "a0000000-0000-0000-0000-000000000001",
        "treatment_id": "a0000000-0000-0000-0000-000000000002",
        "assessment_id": "a0000000-0000-0000-0000-000000000003",
        "rat_context_snapshot": ctx["rat_context_snapshot"],
        "legal_basis": ctx["legal_basis"],
        "consent_assessment": ctx["consent_assessment"],
        "sensitive_consent_assessment": ctx["sensitive_consent_assessment"],
    }
    ctx["sensitive_representation_assessment"] = bind_sensitive_representation_v1(
        {"representation_kind": "mandatario", "notes": "PRUEBA: documento ficticio"},
        binding_context,
    ).model_dump(mode="json")
    ctx["context_schema_version"] = 3
    return document, ctx


def test_deterministic_nonmutating_binding(represented):
    document, ctx = represented
    before = deepcopy(represented)
    bound = bind_eipd_resolution_v3(document, ctx)
    assert bound.context_binding.binding_version == 3
    assert eipd_resolution_context_is_current_v3(bound, ctx)
    assert build_eipd_resolution_context_hash_v3(
        ctx
    ) == build_eipd_resolution_context_hash_v3(
        EipdResolutionContextV3.model_validate(ctx)
    )
    assert build_eipd_resolution_document_hash_v3(
        bound
    ) == build_eipd_resolution_document_hash_v3(bound.model_dump(mode="json"))
    assert represented == before


@pytest.mark.parametrize(
    "change",
    ["body", "context_hash", "document_hash", "withdraw", "research", "rat", "consent"],
)
def test_changed_material_invalidates_binding_without_repair(represented, change):
    document, ctx = represented
    bound = bind_eipd_resolution_v3(document, ctx)
    original = bound.model_dump(mode="json")
    if change == "body":
        ctx["sensitive_representation_assessment"]["assessment"]["notes"] += " revisado"
    elif change in ("context_hash", "document_hash"):
        ctx["sensitive_representation_assessment"]["context_binding"][change] = "a" * 64
    elif change == "withdraw":
        ctx["sensitive_representation_assessment"] = None
    elif change == "research":
        ctx["research_assessment"] = None
    elif change == "rat":
        ctx["rat_context_snapshot"]["purpose"] += " revisada"
    else:
        ctx["consent_assessment"] = {"given_by": "representante_legal"}
    assert not eipd_resolution_context_is_current_v3(bound, ctx)
    assert bound.model_dump(mode="json") == original


def test_required_explicit_null_and_closed_versions(represented):
    document, ctx = represented
    missing = deepcopy(ctx)
    missing.pop("sensitive_representation_assessment")
    with pytest.raises(ValidationError):
        EipdResolutionContextV3.model_validate(missing)
    EipdResolutionContextV3.model_validate(
        dict(ctx, sensitive_representation_assessment=None)
    )
    for bad in (dict(ctx, context_schema_version=2), dict(ctx, can_confirm=True)):
        with pytest.raises(ValidationError):
            EipdResolutionContextV3.model_validate(bad)
    with pytest.raises(ValidationError):
        EipdResolutionContextV2.model_validate(ctx)
    bound = bind_eipd_resolution_v3(document, ctx)
    for model in (EipdResolutionAssessmentStoredV1, EipdResolutionAssessmentStoredV2):
        with pytest.raises(ValidationError):
            model.model_validate(bound.model_dump(mode="json"))
    with pytest.raises(ValidationError):
        bind_eipd_resolution_v3(bound, ctx)


def test_v3_null_does_not_share_v2_hash(represented):
    _, ctx = represented
    ctx["sensitive_representation_assessment"] = None
    legacy = {
        key: value
        for key, value in ctx.items()
        if key != "sensitive_representation_assessment"
    }
    legacy["context_schema_version"] = 2
    assert build_eipd_resolution_context_hash_v3(
        ctx
    ) != build_eipd_resolution_context_hash_v2(legacy)
