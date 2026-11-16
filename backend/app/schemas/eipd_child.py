"""Composicion documental V5; no contrato de resolucion o permiso positivo."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.child_adolescent import ChildAdolescentReadinessOutV1
from app.schemas.licitud import ConfirmationBlockerOut


class EipdChildIssueV5(ConfirmationBlockerOut):
    model_config = ConfigDict(extra="forbid")


class EipdChildDecisionV5(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prerequisites_met: Literal[False] = False
    context_metadata: None = None
    issues: list[EipdChildIssueV5]


class EipdChildCompositionV5Out(BaseModel):
    model_config = ConfigDict(extra="forbid")
    evaluation_version: Literal[5] = 5
    context_schema_version: Literal[4] = 4
    evaluation_scope: Literal["requisitos_documentales"] = "requisitos_documentales"
    context_hash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    child_adolescent_coverage: Literal["contexto_v4", "contexto_actual_no_disponible"]
    resolution_child_coverage: Literal["no_cubierta"] = "no_cubierta"
    child_adolescent: ChildAdolescentReadinessOutV1
    preparation_result: Literal["requiere_revision"] = "requiere_revision"
    confirmation_blockers: list[EipdChildIssueV5]
    continuar: EipdChildDecisionV5
    requiere_cambios: EipdChildDecisionV5
    no_continuar: EipdChildDecisionV5
    can_confirm: Literal[False] = False
    authorizes_action: Literal[False] = False

    @model_validator(mode="after")
    def coverage_and_gates(self):
        if (self.context_hash is not None) != (
            self.child_adolescent_coverage == "contexto_v4"
        ):
            raise ValueError("Cobertura requiere contexto actual disponible")
        required = "politica_infancia_no_implementada"
        for blockers in [
            self.confirmation_blockers,
            self.continuar.issues,
            self.requiere_cambios.issues,
            self.no_continuar.issues,
        ]:
            if required not in {i.code for i in blockers}:
                raise ValueError("Falta gate conservador de infancia")
        return self
