"""Identidad V3 ficticia, sin atribuir autoridad ni convertir eventos historicos."""

from copy import deepcopy
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

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


@pytest.mark.parametrize("version", [None, 1, 2])
def test_compatible_reader_and_output_preserve_history(represented, version):
    from app.schemas.licitud import EipdResolutionReviewOutV3
    from app.services.eipd_review_metadata_v2 import (
        read_eipd_review_context_metadata_v2,
    )

    document, ctx = represented
    identity = build(bind_eipd_resolution_v3(document, ctx), ctx).model_dump(
        mode="json"
    )
    if version == 1:
        identity = {
            "metadata_schema_version": 1,
            "resolution_binding_version": 2,
            "context_schema_version": 2,
            "research_coverage": "contexto_v2",
            "document_hash": identity["document_hash"],
            "context_hash": identity["context_hash"],
            "research_material_hash": None,
        }
    event = dict(
        id=uuid4(),
        organization_id=uuid4(),
        assessment_id=uuid4(),
        created_by=uuid4(),
        decision="requiere_cambios",
        rationale="PRUEBA",
        review_reference="PRUEBA",
        created_at=datetime.now(UTC),
        document_hash=identity["document_hash"],
        context_hash=identity["context_hash"],
        review_context_metadata=identity if version else None,
    )
    before = deepcopy(event)
    parsed = read_eipd_review_context_metadata_v2(SimpleNamespace(**event))
    assert (parsed.model_dump(mode="json") if parsed else None) == event[
        "review_context_metadata"
    ]
    out = EipdResolutionReviewOutV3.model_validate(
        dict(event, response_schema_version=3)
    )
    assert (
        out.review_context_metadata.model_dump(mode="json")
        if out.review_context_metadata
        else None
    ) == event["review_context_metadata"]
    assert event == before
    if version:
        event["document_hash"] = "f" * 64
        with pytest.raises(ValueError):
            read_eipd_review_context_metadata_v2(SimpleNamespace(**event))
        with pytest.raises(ValidationError):
            EipdResolutionReviewOutV3.model_validate(
                dict(event, response_schema_version=3)
            )


@pytest.mark.parametrize("version", [True, "2", 0, 3])
def test_reader_rejects_unknown_or_loose_version(represented, version):
    from app.services.eipd_review_metadata_v2 import (
        read_eipd_review_context_metadata_v2,
    )

    document, ctx = represented
    metadata = build(bind_eipd_resolution_v3(document, ctx), ctx).model_dump(
        mode="json"
    )
    metadata["metadata_schema_version"] = version
    with pytest.raises(ValueError):
        read_eipd_review_context_metadata_v2(
            SimpleNamespace(
                review_context_metadata=metadata,
                document_hash=metadata["document_hash"],
                context_hash=metadata["context_hash"],
            )
        )
