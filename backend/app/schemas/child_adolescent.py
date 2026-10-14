"""Primer contrato documental interno de infancia; sin entrada API ni autoridad."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.licitud import SpecialEvidenceV1, SpecialScopeV1


class ChildAdolescentAssessmentV1(SpecialScopeV1):
    schema_version: Literal[1] = 1
    declared_groups: list[
        Literal["ninos_ninas", "adolescentes", "adolescentes_sensibles_menores_16"]
    ] = Field(default_factory=list)
    age_scope_analysis: str | None = None
    sensitive_under16: Literal["si", "no", "pendiente"] | None = None
    best_interests_analysis: str | None = None
    progressive_autonomy_analysis: str | None = None
    proposed_authorization_route: (
        Literal["consentimiento", "autorizacion_legal_expresa"] | None
    ) = None
    authorization_reference: str | None = None
    authorization_analysis: str | None = None
    declared_consent_giver: (
        Literal["padre_madre", "representante_legal", "cuidado_personal", "titular"]
        | None
    ) = None
    evidence: list[SpecialEvidenceV1] = Field(default_factory=list)
    notes: str | None = None

    @model_validator(mode="after")
    def unique_groups(self):
        if len(self.declared_groups) != len(set(self.declared_groups)):
            raise ValueError("declared_groups no admite duplicados")
        return self


class ChildAdolescentBindingV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    binding_version: Literal[1] = 1
    context_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    document_hash: str = Field(pattern=r"^[0-9a-f]{64}$")


class BoundChildAdolescentAssessmentV1(BaseModel):
    """Envoltorio servidor independiente; no forma parte de entradas HTTP."""

    model_config = ConfigDict(extra="forbid")
    assessment: ChildAdolescentAssessmentV1
    context_binding: ChildAdolescentBindingV1
