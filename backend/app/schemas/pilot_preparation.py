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


SimulationReference = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, pattern=r"^SIMULADA-[A-Z0-9][A-Z0-9-]*$", max_length=128
    ),
]
SIMULATION_WATERMARK = "ACTA DE PRUEBA, DATOS FICTICIOS, SIN VALOR JURÍDICO"
SIMULATION_SCENARIO = {
    "company": {
        "name": "[FICTICIA] Comercial Piloto Andes SpA",
        "test_rut": "00.000.000-0",
        "activity": "Comercio minorista en línea; clientes, trabajadores y programa de fidelización con menores (escenario de prueba).",
        "address": "Calle Ficticia 123, Santiago",
        "contact": "contacto@piloto.example.invalid",
    },
    "person": {
        "name": "[FICTICIA] Persona Facultada Piloto",
        "test_rut": "00.000.001-0",
        "position": "Gerencia General (representante legal simulado)",
        "contact": "facultada@piloto.example.invalid",
    },
    "designation": {
        "type": "designación simulada para pruebas",
        "test_date": "2000-01-01",
        "date_status": "simulada",
        "real_legal_document": None,
    },
}


class PilotSimulationIn(PilotPreparationIn):
    act_reference: SimulationReference = "SIMULADA-PILOTO-ACTA-001"
    designation_reference: SimulationReference = "SIMULADA-PILOTO-DES-001"
    review_reference: SimulationReference | None = None
    environment_reference: SimulationReference | None = None
    access_reference: SimulationReference | None = None
    restore_reference: SimulationReference | None = None
    retention_reference: SimulationReference | None = None
    support_reference: SimulationReference | None = None
    incident_reference: SimulationReference | None = None


class PilotSimulationOut(PilotPreparationOut):
    schema_version: Literal[2] = 2
    watermark: Literal["ACTA DE PRUEBA, DATOS FICTICIOS, SIN VALOR JURÍDICO"] = (
        SIMULATION_WATERMARK
    )
    act_reference: SimulationReference
    designation_reference: SimulationReference
    authority_evidence_reference: SimulationReference
    declared_references: dict[str, SimulationReference | None]
    scenario: dict
    legal_review_status: Literal[
        "pendiente_no_realizada", "simulada_sin_valor_juridico"
    ]
    scenario_notice: Literal[
        "Escenario ficticio; no identifica ni acredita a la organización o persona real de la sesión."
    ] = "Escenario ficticio; no identifica ni acredita a la organización o persona real de la sesión."
