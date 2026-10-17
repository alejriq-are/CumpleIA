"""Asociacion separada de representacion; no modifica bindings historicos."""

from dataclasses import dataclass
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.licitud import (
    ConsentAssessmentV1,
    LegalBasis,
    RatContextSnapshotV1,
    SensitiveConsentAssessmentV1,
)
from app.schemas.sensitive_representation import (
    BoundSensitiveRepresentationV1,
    SensitiveRepresentationAssessmentV1,
)
from app.services.research_binding import digest, validated


class SensitiveRepresentationContextV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    context_schema_version: Literal[1] = 1
    organization_id: UUID
    treatment_id: UUID
    assessment_id: UUID
    rat_context_snapshot: RatContextSnapshotV1
    legal_basis: LegalBasis | None
    consent_assessment: ConsentAssessmentV1 | None
    sensitive_consent_assessment: SensitiveConsentAssessmentV1 | None


def build_sensitive_representation_context_hash_v1(context):
    return digest(
        "cumpleia.sensitive_representation.context",
        validated(SensitiveRepresentationContextV1, context).model_dump(mode="json"),
    )


def build_sensitive_representation_document_hash_v1(assessment):
    return digest(
        "cumpleia.sensitive_representation.document",
        validated(SensitiveRepresentationAssessmentV1, assessment).model_dump(
            mode="json"
        ),
    )


def bind_sensitive_representation_v1(assessment, context):
    document = validated(SensitiveRepresentationAssessmentV1, assessment)
    return BoundSensitiveRepresentationV1.model_validate(
        {
            "assessment": document.model_dump(mode="python"),
            "context_binding": {
                "binding_version": 1,
                "context_hash": build_sensitive_representation_context_hash_v1(context),
                "document_hash": build_sensitive_representation_document_hash_v1(
                    document
                ),
            },
        }
    )


@dataclass(frozen=True)
class SensitiveRepresentationAssociationV1:
    result: Literal["vigente", "requiere_revision"]
    issues: tuple[str, ...]

    @property
    def can_confirm(self):
        return False


def evaluate_sensitive_representation_association_v1(bound, context):
    # Validar contexto incluso cuando no hay documento; no ocultar un caller invalido.
    context_hash = build_sensitive_representation_context_hash_v1(context)
    if bound is None:
        return SensitiveRepresentationAssociationV1(
            "requiere_revision", ("asociacion_ausente",)
        )
    document = validated(BoundSensitiveRepresentationV1, bound)
    issues = []
    if document.context_binding.context_hash != context_hash:
        issues.append("asociacion_contexto_obsoleta")
    if (
        document.context_binding.document_hash
        != build_sensitive_representation_document_hash_v1(document.assessment)
    ):
        issues.append("asociacion_documento_obsoleta")
    return SensitiveRepresentationAssociationV1(
        "requiere_revision" if issues else "vigente", tuple(issues)
    )
