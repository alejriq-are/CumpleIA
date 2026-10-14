"""Contrato documental preliminar; sin persistencia, autorizacion o gate."""

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.licitud import ContractEvidenceV1, SpecialScopeV1


class SensitiveRepresentationAssessmentV1(BaseModel):
    """Borrador incompleto admitido; forma valida no acredita facultades."""

    model_config = ConfigDict(extra="forbid")
    schema_version: Literal[1] = 1
    representation_kind: Literal["representante_legal", "mandatario"] | None = None
    representative_reference: str | None = None
    represented_subjects_reference: str | None = None
    authority_document_reference: str | None = None
    authority_document_version: str | None = None
    authority_basis_description: str | None = None
    express_authority_analysis: str | None = None
    scope: SpecialScopeV1 | None = None
    scope_match_analysis: str | None = None
    issued_on: date | None = None
    valid_from: date | None = None
    valid_until: date | None = None
    validity_analysis: str | None = None
    limitations: str | None = None
    revocation_information: str | None = None
    evidence: list[ContractEvidenceV1] = Field(default_factory=list)
    notes: str | None = None

    @field_validator(
        "representative_reference",
        "represented_subjects_reference",
        "authority_document_reference",
        "authority_document_version",
        "authority_basis_description",
        "express_authority_analysis",
        "scope_match_analysis",
        "validity_analysis",
        "limitations",
        "revocation_information",
        "notes",
    )
    @classmethod
    def reject_blank_text(cls, value):
        if value is not None and not value.strip():
            raise ValueError("Texto aportado no puede estar vacio")
        return value

    @model_validator(mode="after")
    def validate_documented_interval(self):
        if self.valid_from and self.valid_until and self.valid_until < self.valid_from:
            raise ValueError("Intervalo documental contradictorio")
        return self
