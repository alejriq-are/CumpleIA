"""Lectura sucesora de identidad guardada; no deriva vigencia ni autoridad."""

from app.schemas.licitud import (
    EipdResolutionReviewOutV3,
    EipdResolutionReviewWithPolicyOut,
)
from app.services.eipd_review_metadata_v2 import read_eipd_review_context_metadata_v2


def serialize_eipd_resolution_review_v3(event):
    metadata = read_eipd_review_context_metadata_v2(event)
    return EipdResolutionReviewOutV3.model_validate(
        {
            **{
                name: getattr(event, name)
                for name in EipdResolutionReviewWithPolicyOut.model_fields
            },
            "response_schema_version": 3,
            "review_context_metadata": (
                metadata.model_dump(mode="python") if metadata else None
            ),
        }
    )
