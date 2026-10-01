"""Contratos Pydantic del Módulo 3 — Bases de Licitud.

Define los contratos versionados para evaluaciones jurídicas y para el
contexto RAT utilizado por M3. Los identificadores técnicos de M2 no forman
parte de la identidad semántica histórica del contexto.
"""

import uuid
from typing import Literal

from pydantic import BaseModel, Field, model_validator

LegalBasis = Literal[
    "consentimiento_art12",
    "obligaciones_economicas_art13a",
    "obligacion_legal_art13b",
    "contrato_precontractual_art13c",
    "interes_legitimo_art13d",
    "defensa_derechos_art13e",
]

LegalAssessmentStatus = Literal[
    "borrador",
    "confirmado",
    "reemplazado",
]


class LegalAssessmentScopeIn(BaseModel):
    """Selección M2 aplicable a la finalidad evaluada."""

    data_category_codes: list[str] = Field(default_factory=list)
    data_subject_codes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validar_codigos_de_alcance(self):
        if any(not code.strip() for code in self.data_category_codes):
            raise ValueError("data_category_codes no admite códigos vacíos")
        if any(not code.strip() for code in self.data_subject_codes):
            raise ValueError("data_subject_codes no admite códigos vacíos")
        if len(self.data_category_codes) != len(set(self.data_category_codes)):
            raise ValueError("data_category_codes no admite códigos duplicados")
        if len(self.data_subject_codes) != len(set(self.data_subject_codes)):
            raise ValueError("data_subject_codes no admite códigos duplicados")
        return self


class LegalAssessmentDraftCreate(BaseModel):
    """Entrada para crear una nueva versión en estado borrador."""

    purpose_id: uuid.UUID
    scope: LegalAssessmentScopeIn
    legal_basis: LegalBasis | None = None
    justification: str | None = None


class LegalAssessmentDraftUpdate(BaseModel):
    """Actualización parcial de un borrador existente."""

    scope: LegalAssessmentScopeIn | None = None
    legal_basis: LegalBasis | None = None
    justification: str | None = None

    @model_validator(mode="after")
    def validar_scope_null_explicito(self):
        if "scope" in self.model_fields_set and self.scope is None:
            raise ValueError("scope no puede ser null")
        return self


# ── Contexto RAT canónico v1 ─────────────────────────────────────────────────


class RatCanonicalDataCategoryV1(BaseModel):
    category_code: str
    category_name: str
    is_sensitive: bool


class RatCanonicalDataSubjectV1(BaseModel):
    category_code: str
    category_name: str
    includes_children: bool
    includes_adolescents: bool
    is_vulnerable_group: bool


class RatCanonicalDataSourceV1(BaseModel):
    source_type: Literal[
        "titular",
        "tercero",
        "fuente_publica",
        "recogida_automatica",
        "otro",
    ]
    description: str | None
    is_public_source: bool


class RatCanonicalRetentionV1(BaseModel):
    retention_rule: str | None


class RatCanonicalAutomatedDecisionsV1(BaseModel):
    has_automated_decisions: bool
    description: str | None


class RatCanonicalThirdPartyV1(BaseModel):
    relationship_type: Literal[
        "encargado",
        "cesionario",
        "otro",
    ]
    has_data_access: bool
    country: str | None
    has_subprocessors: bool
    purpose: str | None


class RatCanonicalInternationalTransferV1(BaseModel):
    destination_country: str
    adequacy_status: Literal[
        "adecuado",
        "no_adecuado",
        "pendiente",
        "no_determinado",
    ]
    mechanism: str | None
    guarantees_description: str | None


class RatCanonicalSpecialRegimesV1(BaseModel):
    has_sensitive_data: bool
    includes_children: bool
    includes_adolescents: bool
    has_vulnerable_groups: bool


class RatCanonicalContextV1(BaseModel):
    purpose: str
    organization_role: Literal["responsable", "encargado"] | None
    data_categories: list[RatCanonicalDataCategoryV1]
    data_subjects: list[RatCanonicalDataSubjectV1]
    data_sources: list[RatCanonicalDataSourceV1]
    retention: RatCanonicalRetentionV1
    automated_decisions: RatCanonicalAutomatedDecisionsV1
    systems: list[dict] = Field(default_factory=list, max_length=0)
    third_parties: list[RatCanonicalThirdPartyV1]
    international_transfers: list[RatCanonicalInternationalTransferV1]
    special_regimes: RatCanonicalSpecialRegimesV1


# ── Snapshot documental RAT v1 ────────────────────────────────────────────────


class RatSnapshotDataCategoryV1(BaseModel):
    category_code: str
    category_name: str
    is_sensitive: bool
    notes: str | None


class RatSnapshotDataSubjectV1(BaseModel):
    category_code: str
    category_name: str
    includes_children: bool
    includes_adolescents: bool
    is_vulnerable_group: bool
    notes: str | None


class RatSnapshotDataSourceV1(BaseModel):
    source_type: Literal[
        "titular",
        "tercero",
        "fuente_publica",
        "recogida_automatica",
        "otro",
    ]
    description: str | None
    is_public_source: bool


class RatSnapshotRetentionV1(BaseModel):
    retention_rule: str | None
    deletion_method: str | None


class RatSnapshotAutomatedDecisionsV1(BaseModel):
    has_automated_decisions: bool
    description: str | None


class RatSnapshotSystemV1(BaseModel):
    name: str
    provider: str | None
    hosting_location: str | None
    hosting_country: str | None
    is_international: bool


class RatSnapshotThirdPartyV1(BaseModel):
    vendor_name: str
    country: str | None
    relationship_type: Literal[
        "encargado",
        "cesionario",
        "otro",
    ]
    purpose: str | None
    has_data_access: bool
    has_contract: bool
    contract_reference: str | None
    engagement_object: str | None
    engagement_duration: str | None
    has_subprocessors: bool
    notes: str | None


class RatSnapshotInternationalTransferV1(BaseModel):
    recipient_name: str | None
    destination_country: str
    adequacy_status: Literal[
        "adecuado",
        "no_adecuado",
        "pendiente",
        "no_determinado",
    ]
    mechanism: str | None
    guarantees_description: str | None
    evidence_reference: str | None


class RatSnapshotSpecialRegimesV1(BaseModel):
    has_sensitive_data: bool
    includes_children: bool
    includes_adolescents: bool
    has_vulnerable_groups: bool


class RatContextSnapshotV1(BaseModel):
    purpose: str
    organization_role: Literal["responsable", "encargado"] | None
    data_categories: list[RatSnapshotDataCategoryV1]
    data_subjects: list[RatSnapshotDataSubjectV1]
    data_sources: list[RatSnapshotDataSourceV1]
    retention: RatSnapshotRetentionV1
    automated_decisions: RatSnapshotAutomatedDecisionsV1
    systems: list[RatSnapshotSystemV1]
    third_parties: list[RatSnapshotThirdPartyV1]
    international_transfers: list[RatSnapshotInternationalTransferV1]
    special_regimes: RatSnapshotSpecialRegimesV1
