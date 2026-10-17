"""Asociacion pura de representacion; sin dispatch, eventos ni permiso de confirmar."""

from typing import Literal

from app.schemas.licitud import (
    BoundSensitiveRepresentationV1,
    EipdResolutionAssessmentStoredV3,
    EipdResolutionAssessmentV1,
)
from app.services.eipd_resolution import _hash, _validated_json
from app.services.eipd_resolution_binding_v2 import EipdResolutionContextV2


class EipdResolutionContextV3(EipdResolutionContextV2):
    context_schema_version: Literal[3] = 3
    sensitive_representation_assessment: BoundSensitiveRepresentationV1 | None


def build_eipd_resolution_context_hash_v3(context):
    return _hash(
        {
            "domain": "cumpleia.eipd.resolution.representation",
            "binding_version": 3,
            "context": _validated_json(EipdResolutionContextV3, context),
        }
    )


def bind_eipd_resolution_v3(document, context):
    material = _validated_json(EipdResolutionAssessmentV1, document)
    material["context_binding"] = {
        "binding_version": 3,
        "context_hash": build_eipd_resolution_context_hash_v3(context),
    }
    return EipdResolutionAssessmentStoredV3.model_validate(material)


def build_eipd_resolution_document_hash_v3(document):
    return _hash(
        {
            "domain": "cumpleia.eipd.resolution.document.representation",
            "binding_version": 3,
            "document": _validated_json(EipdResolutionAssessmentStoredV3, document),
        }
    )


def eipd_resolution_context_is_current_v3(document, context):
    parsed = EipdResolutionAssessmentStoredV3.model_validate(
        _validated_json(EipdResolutionAssessmentStoredV3, document)
    )
    return parsed.context_binding.context_hash == build_eipd_resolution_context_hash_v3(
        context
    )
