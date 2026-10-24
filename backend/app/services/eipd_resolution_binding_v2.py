"""Asociacion pura de investigacion; sin dispatch, eventos ni permiso de confirmar."""

from typing import Literal

from app.schemas.licitud import (
    BoundResearchAssessmentV1,
    EipdResolutionAssessmentStoredV2,
    EipdResolutionAssessmentV1,
)
from app.services.eipd_resolution import EipdResolutionContextV1, _hash, _validated_json


class EipdResolutionContextV2(EipdResolutionContextV1):
    context_schema_version: Literal[2] = 2
    research_assessment: BoundResearchAssessmentV1 | None


def build_eipd_resolution_context_hash_v2(context):
    return _hash(
        {
            "domain": "cumpleia.eipd.resolution.research",
            "binding_version": 2,
            "context": _validated_json(EipdResolutionContextV2, context),
        }
    )


def bind_eipd_resolution_v2(document, context):
    material = _validated_json(EipdResolutionAssessmentV1, document)
    material["context_binding"] = {
        "binding_version": 2,
        "context_hash": build_eipd_resolution_context_hash_v2(context),
    }
    return EipdResolutionAssessmentStoredV2.model_validate(material)


def build_eipd_resolution_document_hash_v2(document):
    return _hash(
        {
            "domain": "cumpleia.eipd.resolution.document.research",
            "binding_version": 2,
            "document": _validated_json(EipdResolutionAssessmentStoredV2, document),
        }
    )


def eipd_resolution_context_is_current_v2(document, context):
    parsed = EipdResolutionAssessmentStoredV2.model_validate(
        _validated_json(EipdResolutionAssessmentStoredV2, document)
    )
    return parsed.context_binding.context_hash == build_eipd_resolution_context_hash_v2(
        context
    )
