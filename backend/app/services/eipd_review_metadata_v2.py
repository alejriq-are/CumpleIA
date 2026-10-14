"""Metadata pura del contexto V3; no convierte historia ni autoriza acciones."""

from app.schemas.eipd_review_metadata import EipdReviewContextMetadataV2
from app.schemas.licitud import EipdResolutionAssessmentStoredV3
from app.services.eipd_resolution import _hash, _validated_json
from app.services.eipd_resolution_binding_v3 import (
    EipdResolutionContextV3,
    build_eipd_resolution_context_hash_v3,
    build_eipd_resolution_document_hash_v3,
)


def build_eipd_review_context_metadata_v2(document, context):
    parsed = EipdResolutionAssessmentStoredV3.model_validate(
        _validated_json(EipdResolutionAssessmentStoredV3, document)
    )
    ctx = EipdResolutionContextV3.model_validate(
        _validated_json(EipdResolutionContextV3, context)
    )
    context_hash = build_eipd_resolution_context_hash_v3(ctx)
    if context_hash != parsed.context_binding.context_hash:
        raise ValueError("Asociacion obsoleta: no generar identidad vigente")

    def material_hash(name, material):
        if material is None:
            return None
        return _hash(
            {
                "domain": "cumpleia.eipd.review." + name + "_material",
                "metadata_schema_version": 2,
                "material": material.model_dump(mode="json"),
            }
        )

    return EipdReviewContextMetadataV2(
        metadata_schema_version=2,
        resolution_binding_version=3,
        context_schema_version=3,
        research_coverage="contexto_v3",
        representation_coverage="contexto_v3",
        document_hash=build_eipd_resolution_document_hash_v3(parsed),
        context_hash=context_hash,
        research_material_hash=material_hash("research", ctx.research_assessment),
        representation_material_hash=material_hash(
            "representation", ctx.sensitive_representation_assessment
        ),
    )
