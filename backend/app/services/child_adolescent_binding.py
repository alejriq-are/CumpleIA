"""Identidad separada de infancia; no reescribe hashes especiales o EIPD."""

from dataclasses import dataclass
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.child_adolescent import (
    BoundChildAdolescentAssessmentV1,
    ChildAdolescentAssessmentV1,
)
from app.schemas.licitud import (
    BoundSensitiveRepresentationV1,
    ConsentAssessmentV1,
    LegalBasis,
    RatContextSnapshotV1,
    SensitiveConsentAssessmentV1,
    SpecialConditionsDraftIn,
)
from app.services.research_binding import digest, validated


class ChildAdolescentContextV1(BaseModel):
    """Proyeccion explicita de declaraciones especiales sin binding circular."""

    model_config = ConfigDict(extra="forbid")
    context_schema_version: Literal[1] = 1
    organization_id: UUID
    treatment_id: UUID
    assessment_id: UUID
    rat_context_snapshot: RatContextSnapshotV1
    legal_basis: LegalBasis | None
    consent_assessment: ConsentAssessmentV1 | None
    sensitive_consent_assessment: SensitiveConsentAssessmentV1 | None
    special_conditions_document: SpecialConditionsDraftIn | None
    sensitive_representation_assessment: BoundSensitiveRepresentationV1 | None


def build_child_adolescent_context_hash_v1(context):
    return digest(
        "cumpleia.child_adolescent.context",
        validated(ChildAdolescentContextV1, context).model_dump(mode="json"),
    )


def build_child_adolescent_document_hash_v1(document):
    return digest(
        "cumpleia.child_adolescent.document",
        validated(ChildAdolescentAssessmentV1, document).model_dump(mode="json"),
    )


def bind_child_adolescent_v1(document, context):
    doc = validated(ChildAdolescentAssessmentV1, document)
    return BoundChildAdolescentAssessmentV1.model_validate(
        {
            "assessment": doc.model_dump(mode="python"),
            "context_binding": {
                "binding_version": 1,
                "context_hash": build_child_adolescent_context_hash_v1(context),
                "document_hash": build_child_adolescent_document_hash_v1(doc),
            },
        }
    )


@dataclass(frozen=True)
class ChildAdolescentAssociationV1:
    result: Literal["vigente", "requiere_revision"]
    issues: tuple[str, ...]

    @property
    def can_confirm(self) -> Literal[False]:
        return False

    @property
    def authorizes_action(self) -> Literal[False]:
        return False


def evaluate_child_adolescent_association_v1(bound, context):
    context_hash = build_child_adolescent_context_hash_v1(context)
    if bound is None:
        return ChildAdolescentAssociationV1(
            "requiere_revision", ("asociacion_ausente",)
        )
    document = validated(BoundChildAdolescentAssessmentV1, bound)
    issues = []
    if document.context_binding.context_hash != context_hash:
        issues.append("asociacion_contexto_obsoleta")
    if (
        document.context_binding.document_hash
        != build_child_adolescent_document_hash_v1(document.assessment)
    ):
        issues.append("asociacion_documento_obsoleta")
    return ChildAdolescentAssociationV1(
        "requiere_revision" if issues else "vigente", tuple(issues)
    )
