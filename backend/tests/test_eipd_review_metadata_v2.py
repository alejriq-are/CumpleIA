"""Identidad V3 ficticia, sin atribuir autoridad ni convertir eventos historicos."""

from copy import deepcopy

import pytest
from pydantic import ValidationError

from app.schemas.eipd_review_metadata import (
    EipdReviewContextMetadataV1,
    EipdReviewContextMetadataV2,
)
from app.services.eipd_resolution_binding_v3 import bind_eipd_resolution_v3
from app.services.eipd_review_metadata_v2 import (
    build_eipd_review_context_metadata_v2 as build,
)
from tests import test_eipd_resolution_binding_v3 as binding

complete_resolution = binding.complete_resolution
context = binding.context
materials = binding.materials
represented = binding.represented


@pytest.mark.parametrize("representation_present", [True, False])
@pytest.mark.parametrize("research_present", [True, False])
def test_metadata_records_coverage_and_presence_without_authority(
    represented, representation_present, research_present
):
    document, ctx = represented
    if not representation_present:
        ctx["sensitive_representation_assessment"] = None
    if not research_present:
        ctx["research_assessment"] = None
    bound = bind_eipd_resolution_v3(document, ctx)
    original = deepcopy((ctx, bound.model_dump(mode="json")))
    result = build(bound, ctx)
    assert result == build(bound.model_dump(mode="json"), ctx)
    assert result.context_schema_version == result.resolution_binding_version == 3
    assert result.representation_coverage == result.research_coverage == "contexto_v3"
    assert (result.representation_material_hash is not None) == representation_present
    assert (result.research_material_hash is not None) == research_present
    assert not hasattr(result, "can_confirm")
    assert original == (ctx, bound.model_dump(mode="json"))
    with pytest.raises(ValidationError):
        EipdReviewContextMetadataV1.model_validate(result.model_dump(mode="json"))


def test_stale_context_cannot_generate_current_metadata(represented):
    document, ctx = represented
    bound = bind_eipd_resolution_v3(document, ctx)
    ctx["sensitive_representation_assessment"]["assessment"]["notes"] += " cambiado"
    with pytest.raises(ValueError):
        build(bound, ctx)


@pytest.mark.parametrize(
    "field,value",
    [
        ("metadata_schema_version", True),
        ("metadata_schema_version", "2"),
        ("resolution_binding_version", 2),
        ("context_schema_version", 2),
        ("representation_coverage", "no_cubierta"),
        ("can_confirm", True),
        ("representation_material_hash", "no_es_hash"),
    ],
)
def test_closed_metadata_rejects_incompatible_fields(represented, field, value):
    document, ctx = represented
    raw = build(bind_eipd_resolution_v3(document, ctx), ctx).model_dump(mode="json")
    raw[field] = value
    with pytest.raises(ValidationError):
        EipdReviewContextMetadataV2.model_validate(raw)
