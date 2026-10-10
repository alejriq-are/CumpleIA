"""Serializa identidad persistida; nunca infiere metadata historica."""

from app.schemas.licitud import (
    EipdResolutionReviewOutV2,
    EipdResolutionReviewWithPolicyOut,
)
from app.services.eipd_review_metadata import read_eipd_review_context_metadata_v1


def serialize_eipd_resolution_review_v2(event):
    metadata = read_eipd_review_context_metadata_v1(event)
    return EipdResolutionReviewOutV2.model_validate(
        {
            **{
                name: getattr(event, name)
                for name in EipdResolutionReviewWithPolicyOut.model_fields
            },
            "response_schema_version": 2,
            "review_context_metadata": (
                metadata.model_dump(mode="python") if metadata else None
            ),
        }
    )
