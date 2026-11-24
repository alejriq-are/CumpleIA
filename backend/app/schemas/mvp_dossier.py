"""Expediente de consulta; ninguna salida cierra gates juridicos o activa EIPD."""

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class Closed(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DossierDocument(Closed):
    kind: Literal["rat", "licitud_lia", "eipd"]
    status: Literal["disponible", "sin_documento"]
    version: int | None
    coverage: str
    content: dict[str, Any] | None
    content_hash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    organization_acceptance: Literal["sin_flujo", "consultar_eventos", "sin_eventos"]
    acceptance_events: list[dict[str, Any]] = Field(default_factory=list)


class OfficialSource(Closed):
    reference: str
    title: str
    url: HttpUrl
    consulted_on: str
    status: Literal["consultada_sin_aceptacion_juridica"] = (
        "consultada_sin_aceptacion_juridica"
    )
    scope_note: str
    artifact_reference: str | None = None
    artifact_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    legal_verifier: None = None


class ReleaseGate(Closed):
    id: str
    title: str
    status: Literal["alcance_definido", "pendiente", "bloqueado"]
    evidence_needed: str


class MvpDossierOut(Closed):
    schema_version: Literal[1] = 1
    organization_id: UUID
    treatment_id: UUID
    assessment_id: UUID
    assessment_version: int
    generated_at: datetime
    data_provenance: Literal["no_verificada"] = "no_verificada"
    scope: Literal["expediente_documental_rat_licitud_lia_eipd"] = (
        "expediente_documental_rat_licitud_lia_eipd"
    )
    rat_snapshot_note: str
    support: dict[str, Any] | None = None
    documents: list[DossierDocument]
    official_sources: list[OfficialSource]
    release_gates: list[ReleaseGate]
    packet_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    hash_algorithm: Literal["sha256_json_sort_keys_utf8"] = "sha256_json_sort_keys_utf8"
    legal_acceptance: Literal["pendiente_organizacion_piloto"] = (
        "pendiente_organizacion_piloto"
    )
    mvp_ready: Literal[False] = False
    allows_real_data: Literal[False] = False
    authorizes_action: Literal[False] = False
    can_confirm: Literal[False] = False
    activation: Literal["deshabilitada"] = "deshabilitada"
