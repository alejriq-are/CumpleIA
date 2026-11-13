"""Composicion documental pura de representacion/EIPD; nunca autoriza acciones."""

from dataclasses import dataclass, replace
from datetime import date
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.eipd_review_metadata import EipdReviewContextMetadataV2
from app.schemas.licitud import (
    EipdResolutionAssessmentStoredV1,
    EipdResolutionAssessmentStoredV2,
    EipdResolutionAssessmentStoredV3,
)
from app.services.eipd_resolution import EipdResolutionIssueV1
from app.services.eipd_resolution_binding_v3 import EipdResolutionContextV3
from app.services.eipd_resolution_readiness_v2 import (
    ResolutionReadinessVersioned,
    evaluate_eipd_resolution_document_versioned,
)
from app.services.eipd_review_metadata_v2 import build_eipd_review_context_metadata_v2
from app.services.sensitive_representation import (
    SensitiveRepresentationReadinessV1,
    evaluate_sensitive_representation_v1,
)


class EipdRepresentationInputV1(BaseModel):
    """Entrada interna derivada del expediente; no contrato HTTP."""

    model_config = ConfigDict(extra="forbid", revalidate_instances="always")
    organization_id: UUID
    treatment_id: UUID
    assessment_id: UUID
    context: EipdResolutionContextV3
    resolution: (
        EipdResolutionAssessmentStoredV1
        | EipdResolutionAssessmentStoredV2
        | EipdResolutionAssessmentStoredV3
        | None
    )


@dataclass(frozen=True)
class EipdRepresentationReadinessV1:
    representation: SensitiveRepresentationReadinessV1
    resolution: ResolutionReadinessVersioned
    context_metadata: EipdReviewContextMetadataV2 | None

    @property
    def authorizes_action(self) -> Literal[False]:
        return False

    @property
    def can_confirm(self) -> Literal[False]:
        return False


def compose_eipd_representation_v1(value, *, evaluated_on: date):
    if type(evaluated_on) is not date:
        raise ValueError("evaluated_on exige date explicita")
    raw = value.model_dump(mode="python") if isinstance(value, BaseModel) else value
    data = EipdRepresentationInputV1.model_validate(raw)
    ctx = data.context
    representation = evaluate_sensitive_representation_v1(
        ctx.sensitive_representation_assessment,
        dict(
            organization_id=data.organization_id,
            treatment_id=data.treatment_id,
            assessment_id=data.assessment_id,
            rat_context_snapshot=ctx.rat_context_snapshot,
            legal_basis=ctx.legal_basis,
            consent_assessment=ctx.consent_assessment,
            sensitive_consent_assessment=ctx.sensitive_consent_assessment,
        ),
        evaluated_on=evaluated_on,
    )
    resolution = evaluate_eipd_resolution_document_versioned(
        data.resolution, ctx, evaluated_on=evaluated_on
    )
    issues = [
        i
        for i in resolution.issues
        if i.code != "representacion_evaluacion_integracion_pendiente"
    ]
    issues.extend(
        EipdResolutionIssueV1(
            "sensitive_representation_assessment." + i.field, i.code, i.category
        )
        for i in representation.issues
    )
    ordered = tuple(sorted(set(issues), key=lambda i: (i.field, i.code, i.category)))
    result = (
        "requiere_revision"
        if any(i.category == "requiere_revision" for i in ordered)
        else "incompleto" if ordered else "completo"
    )
    resolution = replace(resolution, result=result, issues=ordered)
    # Metadata identifica material asociado; no demuestra completitud ni facultades.
    metadata = (
        build_eipd_review_context_metadata_v2(data.resolution, ctx)
        if resolution.binding_version == 3 and resolution.context_current
        else None
    )
    return EipdRepresentationReadinessV1(representation, resolution, metadata)
