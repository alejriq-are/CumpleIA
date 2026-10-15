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


class ChildAdolescentIssueOutV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    field: str
    code: str
    category: Literal["incompleto", "requiere_revision"]


class ChildAdolescentReadinessOutV1(BaseModel):
    """Salida interna de diagnostico, sin permisos positivos."""

    model_config = ConfigDict(extra="forbid")
    evaluation_version: Literal[1]
    result: Literal["no_aplicable", "incompleto", "requiere_revision", "completo"]
    documentary_result: Literal[
        "no_aplicable", "incompleto", "requiere_revision", "completo"
    ]
    association_status: Literal["no_aplicable", "vigente", "requiere_revision"]
    issues: list[ChildAdolescentIssueOutV1]
    can_confirm: Literal[False]
    authorizes_action: Literal[False]

    @model_validator(mode="after")
    def coherent_result(self):
        if self.documentary_result == "no_aplicable" and (
            self.association_status != "no_aplicable" or self.issues
        ):
            raise ValueError("No aplicabilidad incoherente con asociacion o motivos")
        if (
            self.documentary_result in ("incompleto", "requiere_revision")
            and not self.issues
        ):
            raise ValueError("Diagnostico documental pendiente exige motivos")
        expected = (
            "requiere_revision"
            if any(i.category == "requiere_revision" for i in self.issues)
            else (
                "incompleto"
                if self.issues
                else (
                    "no_aplicable"
                    if self.documentary_result == "no_aplicable"
                    else "completo"
                )
            )
        )
        if self.result != expected:
            raise ValueError("Resultado de diagnostico incoherente")
        if self.result == "completo" and self.association_status != "vigente":
            raise ValueError("Documento completo exige asociacion vigente")
        return self
