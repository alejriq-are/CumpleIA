"""Entrada sin hashes/actor de registro; salida nunca autoriza EIPD."""

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictInt,
    StringConstraints,
    model_validator,
)

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class AuthorityCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    data_kind: Literal["ficticios"]
    actor_id: UUID
    expected_revision: StrictInt = Field(ge=0)
    action: Literal["otorgar", "revocar"]
    organization_role: Literal["responsable", "encargado"]
    responsible_party_reference: Text | None = None
    faculty_reference: Text
    evidence_reference: Text

    @model_validator(mode="after")
    def responsible(self):
        if (
            self.organization_role == "encargado"
            and not self.responsible_party_reference
        ):
            raise ValueError("Identificar responsable por cuya cuenta actua")
        return self


class AuthorityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    id: UUID
    organization_id: UUID
    treatment_id: UUID
    assessment_id: UUID
    actor_id: UUID
    revision: StrictInt
    action: Literal["otorgar", "revocar"]
    organization_role: Literal["responsable", "encargado"]
    responsible_party_reference: str | None
    faculty_reference: str
    evidence_reference: str
    created_by: UUID
    created_at: datetime
    data_kind: Literal["ficticios"]
    authorizes_action: Literal[False] = False
    can_confirm: Literal[False] = False


class AcceptanceCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    data_kind: Literal["ficticios"]
    authority_id: UUID
    decision: Literal["acepta", "rechaza", "requiere_cambios"]
    rationale: Text
    evidence_reference: Text


class AcceptanceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    id: UUID
    organization_id: UUID
    treatment_id: UUID
    assessment_id: UUID
    actor_id: UUID
    created_by: UUID
    created_at: datetime
    data_kind: Literal["ficticios"]
    authority_id: UUID
    resolution_id: UUID
    decision: Literal["acepta", "rechaza", "requiere_cambios"]
    rationale: str
    evidence_reference: str
    document_hash: str
    context_hash: str
    child_material_hash: str
    material_status: Literal["coincide", "obsoleto", "no_disponible"] = "no_disponible"
    faculty_current: bool = False
    authorizes_action: Literal[False] = False
    can_confirm: Literal[False] = False


class AuthorityState(BaseModel):
    actor_id: UUID
    may_designate: bool
    authorities: list[AuthorityOut]
    authorizes_action: Literal[False] = False
    can_confirm: Literal[False] = False
