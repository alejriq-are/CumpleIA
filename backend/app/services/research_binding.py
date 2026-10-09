"""Asociacion nueva independiente; no reinterpreta bindings historicos especiales."""

import hashlib
import json
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, TypeAdapter

from app.schemas.licitud import LegalBasis, LiaAssessmentV1, RatContextSnapshotV1
from app.schemas.research import BoundResearchAssessmentV1, ResearchAssessmentV1


def validated(model, value):
    return model.model_validate(
        value.model_dump(mode="python") if isinstance(value, BaseModel) else value
    )


def digest(kind, material):
    canonical = json.dumps(
        {"domain": kind, "version": 1, "material": material},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def build_research_context_hash_v1(snapshot, legal_basis, lia_assessment):
    rat = validated(RatContextSnapshotV1, snapshot)
    basis = TypeAdapter(LegalBasis | None).validate_python(legal_basis)
    lia = (
        validated(LiaAssessmentV1, lia_assessment)
        if lia_assessment is not None
        else None
    )
    return digest(
        "cumpleia.research.context",
        {
            "rat_context_snapshot": rat.model_dump(mode="json"),
            "legal_basis": basis,
            "lia_assessment": lia.model_dump(mode="json") if lia else None,
        },
    )


def build_research_document_hash_v1(assessment):
    return digest(
        "cumpleia.research.document",
        validated(ResearchAssessmentV1, assessment).model_dump(mode="json"),
    )


def bind_research_assessment_v1(assessment, snapshot, legal_basis, lia_assessment):
    document = validated(ResearchAssessmentV1, assessment)
    return BoundResearchAssessmentV1.model_validate(
        {
            "assessment": document.model_dump(mode="python"),
            "context_binding": {
                "schema_version": 1,
                "context_hash": build_research_context_hash_v1(
                    snapshot, legal_basis, lia_assessment
                ),
                "document_hash": build_research_document_hash_v1(document),
            },
        }
    )


@dataclass(frozen=True)
class ResearchAssociationV1:
    result: Literal["vigente", "requiere_revision"]
    issues: tuple[str, ...]

    @property
    def can_confirm(self):
        return False


def evaluate_research_association_v1(bound, snapshot, legal_basis, lia_assessment):
    if bound is None:
        return ResearchAssociationV1("requiere_revision", ("asociacion_ausente",))
    document = validated(BoundResearchAssessmentV1, bound)
    issues = []
    if document.context_binding.context_hash != build_research_context_hash_v1(
        snapshot, legal_basis, lia_assessment
    ):
        issues.append("asociacion_contexto_obsoleta")
    if document.context_binding.document_hash != build_research_document_hash_v1(
        document.assessment
    ):
        issues.append("asociacion_documento_obsoleta")
    return ResearchAssociationV1(
        "requiere_revision" if issues else "vigente", tuple(issues)
    )
