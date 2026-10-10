"""Metadatos puros desde contexto de servidor; sin eventos ni autoridad."""

from pydantic import BaseModel

from app.schemas.eipd_review_metadata import EipdReviewContextMetadataV1
from app.schemas.licitud import EipdResolutionReviewOut
from app.services.eipd_resolution import (
    EipdResolutionContextV1,
    _hash,
    build_eipd_resolution_context_hash_v1,
    build_eipd_resolution_document_hash_v1,
)
from app.services.eipd_resolution_binding_v2 import (
    EipdResolutionContextV2,
    build_eipd_resolution_context_hash_v2,
    build_eipd_resolution_document_hash_v2,
)
from app.services.eipd_resolution_readiness_v2 import _materials


def build_eipd_review_context_metadata_v1(document, context):
    """Identifica material asociado vigente; completitud y permiso son independientes."""
    parsed, ctx, _, version = _materials(document, context)
    if parsed is None or parsed.context_binding is None or ctx is None:
        raise ValueError("Metadatos exige resolucion asociada y contexto")
    model = EipdResolutionContextV2 if version == 2 else EipdResolutionContextV1
    if type(ctx) is not model:
        raise ValueError("No proyectar ContextV2 sobre binding V1")
    context_hash = (
        build_eipd_resolution_context_hash_v2
        if version == 2
        else build_eipd_resolution_context_hash_v1
    )(ctx)
    if context_hash != parsed.context_binding.context_hash:
        raise ValueError("Asociacion obsoleta: no generar identidad vigente")
    document_hash = (
        build_eipd_resolution_document_hash_v2
        if version == 2
        else build_eipd_resolution_document_hash_v1
    )(parsed)
    research = getattr(ctx, "research_assessment", None)
    research_hash = (
        _hash(
            {
                "domain": "cumpleia.eipd.review.research_material",
                "metadata_schema_version": 1,
                "research": research.model_dump(mode="json"),
            }
        )
        if research is not None
        else None
    )
    return EipdReviewContextMetadataV1(
        metadata_schema_version=1,
        resolution_binding_version=version,
        context_schema_version=version,
        research_coverage="contexto_v2" if version == 2 else "no_cubierta",
        document_hash=document_hash,
        context_hash=context_hash,
        research_material_hash=research_hash,
    )


def eipd_review_metadata_is_current_v1(metadata, document, context, review):
    """Ausencia historica no se infiere; true solo describe identidad de material."""
    if metadata is None or review is None:
        return False
    raw = (
        metadata.model_dump(mode="python")
        if isinstance(metadata, BaseModel)
        else metadata
    )
    parsed = EipdReviewContextMetadataV1.model_validate(raw)
    raw_review = (
        review.model_dump(mode="python") if isinstance(review, BaseModel) else review
    )
    event = EipdResolutionReviewOut.model_validate(raw_review)
    if (event.document_hash, event.context_hash) != (
        parsed.document_hash,
        parsed.context_hash,
    ):
        return False
    try:
        current = build_eipd_review_context_metadata_v1(document, context)
    except ValueError:
        return False
    return parsed == current
