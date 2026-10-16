"""Simulacion de preparacion: referencias no equivalen a actas verificadas."""

from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, StringConstraints

Text = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)
]


class PilotPreparationIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    data_kind: Literal["ficticios"]
    authority_id: UUID
    document_hashes: dict[Literal["rat", "licitud_lia", "eipd"], Text | None]
    review_decision: Literal["acepta", "rechaza", "requiere_cambios", "pendiente"]
    review_reference: Text | None = None
    environment_reference: Text | None = None
    access_reference: Text | None = None
    restore_reference: Text | None = None
    retention_reference: Text | None = None
    support_reference: Text | None = None
    incident_reference: Text | None = None


class PilotPreparationOut(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal[1] = 1
    data_kind: Literal["ficticios"] = "ficticios"
    organization_id: UUID
    treatment_id: UUID
    assessment_id: UUID
    actor_id: UUID
    authority_id: UUID
    authority_evidence_reference: str
    document_hashes: dict[str, str | None]
    declared_references: dict[str, str | None]
    review_decision: str
    missing: list[str]
    preparation_complete: bool
    evidence_status: Literal["declarada_no_verificada"] = "declarada_no_verificada"
    persistence: Literal["simulacion_no_registrada"] = "simulacion_no_registrada"
    legal_acceptance: Literal["pendiente_organizacion_piloto"] = (
        "pendiente_organizacion_piloto"
    )
    mvp_ready: Literal[False] = False
    allows_real_data: Literal[False] = False
    can_confirm: Literal[False] = False
    authorizes_action: Literal[False] = False
    activation: Literal["deshabilitada"] = "deshabilitada"
