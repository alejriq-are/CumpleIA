"""Contratos Pydantic del Módulo 2 — Registro de Actividades de Tratamiento.

Estos schemas representan el modelo normalizado introducido en M2-T1.
Las columnas legacy conservadas temporalmente en la base de datos no forman
parte del contrato público del RAT.
"""

import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

OrganizationRole = Literal["responsable", "encargado"]
TreatmentStatus = Literal["borrador", "activo", "archivado"]
DeclarationStatus = Literal["si", "no", "pendiente"]
DataSourceType = Literal[
    "titular",
    "tercero",
    "fuente_publica",
    "recogida_automatica",
    "otro",
]
VendorRelationshipType = Literal["encargado", "cesionario", "otro"]
AdequacyStatus = Literal[
    "adecuado",
    "no_adecuado",
    "pendiente",
    "no_determinado",
]


class ORMOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ── Finalidades ───────────────────────────────────────────────────────────────


class TreatmentPurposeIn(BaseModel):
    purpose: str = Field(min_length=1)
    is_primary: bool = False
    sort_order: int = Field(default=0, ge=0)


class TreatmentPurposeOut(ORMOut):
    id: uuid.UUID
    purpose: str
    is_primary: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime


class TreatmentPurposesReplace(BaseModel):
    items: list[TreatmentPurposeIn]


# ── Categorías de datos ──────────────────────────────────────────────────────


class TreatmentDataCategoryIn(BaseModel):
    category_code: str = Field(min_length=1)
    category_name: str = Field(min_length=1)
    is_sensitive: bool = False
    notes: str | None = None


class TreatmentDataCategoryOut(ORMOut):
    id: uuid.UUID
    category_code: str
    category_name: str
    is_sensitive: bool
    notes: str | None
    created_at: datetime
    updated_at: datetime


class TreatmentDataCategoriesReplace(BaseModel):
    items: list[TreatmentDataCategoryIn]


# ── Categorías de titulares ──────────────────────────────────────────────────


class TreatmentDataSubjectIn(BaseModel):
    category_code: str = Field(min_length=1)
    category_name: str = Field(min_length=1)
    includes_children: bool = False
    includes_adolescents: bool = False
    is_vulnerable_group: bool = False
    notes: str | None = None


class TreatmentDataSubjectOut(ORMOut):
    id: uuid.UUID
    category_code: str
    category_name: str
    includes_children: bool
    includes_adolescents: bool
    is_vulnerable_group: bool
    notes: str | None
    created_at: datetime
    updated_at: datetime


class TreatmentDataSubjectsReplace(BaseModel):
    items: list[TreatmentDataSubjectIn]


# ── Fuentes de datos ─────────────────────────────────────────────────────────


class TreatmentDataSourceIn(BaseModel):
    source_type: DataSourceType
    description: str | None = None
    is_public_source: bool = False


class TreatmentDataSourceOut(ORMOut):
    id: uuid.UUID
    source_type: DataSourceType
    description: str | None
    is_public_source: bool
    created_at: datetime
    updated_at: datetime


class TreatmentDataSourcesReplace(BaseModel):
    items: list[TreatmentDataSourceIn]


# ── Sistemas ─────────────────────────────────────────────────────────────────


class SystemCreate(BaseModel):
    name: str = Field(min_length=1)
    provider: str | None = None
    hosting_location: str | None = None
    hosting_country: str | None = None


class SystemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    provider: str | None = None
    hosting_location: str | None = None
    hosting_country: str | None = None


class SystemOut(ORMOut):
    id: uuid.UUID
    name: str
    provider: str | None
    hosting_location: str | None
    hosting_country: str | None
    created_at: datetime
    updated_at: datetime


class TreatmentSystemsReplace(BaseModel):
    system_ids: list[uuid.UUID]


# ── Proveedores / terceros ───────────────────────────────────────────────────


class VendorCreate(BaseModel):
    name: str = Field(min_length=1)
    country: str | None = None


class VendorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    country: str | None = None


class VendorOut(ORMOut):
    id: uuid.UUID
    name: str
    country: str | None
    created_at: datetime
    updated_at: datetime


class TreatmentVendorIn(BaseModel):
    vendor_id: uuid.UUID
    relationship_type: VendorRelationshipType
    purpose: str | None = None
    has_data_access: bool = True
    has_contract: bool = False
    contract_reference: str | None = None
    engagement_object: str | None = None
    engagement_duration: str | None = None
    has_subprocessors: bool = False
    notes: str | None = None


class TreatmentVendorOut(ORMOut):
    id: uuid.UUID
    vendor_id: uuid.UUID
    relationship_type: VendorRelationshipType
    purpose: str | None
    has_data_access: bool
    has_contract: bool
    contract_reference: str | None
    engagement_object: str | None
    engagement_duration: str | None
    has_subprocessors: bool
    notes: str | None
    created_at: datetime
    updated_at: datetime


class TreatmentVendorsReplace(BaseModel):
    items: list[TreatmentVendorIn]


# ── Transferencias internacionales ────────────────────────────────────────────


class InternationalTransferBase(BaseModel):
    vendor_id: uuid.UUID | None = None
    recipient_name: str | None = None
    destination_country: str = Field(min_length=1)
    adequacy_status: AdequacyStatus = "pendiente"
    mechanism: str | None = None
    guarantees_description: str | None = None
    evidence_reference: str | None = None

    @model_validator(mode="after")
    def validar_destinatario(self):
        if self.vendor_id is None and not self.recipient_name:
            raise ValueError(
                "Debe indicar vendor_id o recipient_name para la transferencia"
            )
        return self


class InternationalTransferCreate(InternationalTransferBase):
    pass


class InternationalTransferUpdate(BaseModel):
    vendor_id: uuid.UUID | None = None
    recipient_name: str | None = None
    destination_country: str | None = Field(default=None, min_length=1)
    adequacy_status: AdequacyStatus | None = None
    mechanism: str | None = None
    guarantees_description: str | None = None
    evidence_reference: str | None = None


class InternationalTransferOut(ORMOut):
    id: uuid.UUID
    treatment_id: uuid.UUID
    vendor_id: uuid.UUID | None
    recipient_name: str | None
    destination_country: str
    adequacy_status: AdequacyStatus
    mechanism: str | None
    guarantees_description: str | None
    evidence_reference: str | None
    created_at: datetime
    updated_at: datetime


# ── Actividad de tratamiento ─────────────────────────────────────────────────


class TreatmentCreate(BaseModel):
    name: str = Field(min_length=1)
    description: str | None = None
    organization_role: OrganizationRole | None = None
    business_area: str | None = None
    data_flow_description: str | None = None
    start_date: date | None = None
    next_review_at: datetime | None = None
    retention_rule: str | None = None
    systems_declaration: DeclarationStatus | None = None
    vendors_declaration: DeclarationStatus | None = None
    international_transfers_declaration: DeclarationStatus | None = None
    deletion_method: str | None = None
    has_automated_decisions: bool = False
    automated_decision_description: str | None = None


class TreatmentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    description: str | None = None
    organization_role: OrganizationRole | None = None
    business_area: str | None = None
    data_flow_description: str | None = None
    start_date: date | None = None
    last_reviewed_at: datetime | None = None
    next_review_at: datetime | None = None
    status: TreatmentStatus | None = None
    retention_rule: str | None = None
    systems_declaration: DeclarationStatus | None = None
    vendors_declaration: DeclarationStatus | None = None
    international_transfers_declaration: DeclarationStatus | None = None
    deletion_method: str | None = None
    has_automated_decisions: bool | None = None
    automated_decision_description: str | None = None


class TreatmentSummaryOut(ORMOut):
    id: uuid.UUID
    name: str
    description: str | None
    organization_role: OrganizationRole | None
    business_area: str | None
    status: TreatmentStatus
    systems_declaration: DeclarationStatus | None
    vendors_declaration: DeclarationStatus | None
    international_transfers_declaration: DeclarationStatus | None
    start_date: date | None
    last_reviewed_at: datetime | None
    next_review_at: datetime | None
    created_at: datetime
    updated_at: datetime


class TreatmentDetailOut(TreatmentSummaryOut):
    data_flow_description: str | None
    retention_rule: str | None
    deletion_method: str | None
    has_automated_decisions: bool
    automated_decision_description: str | None

    purposes: list[TreatmentPurposeOut] = []
    data_categories: list[TreatmentDataCategoryOut] = []
    data_subjects: list[TreatmentDataSubjectOut] = []
    data_sources: list[TreatmentDataSourceOut] = []
    systems: list[SystemOut] = []
    vendors: list[TreatmentVendorOut] = []
    international_transfers: list[InternationalTransferOut] = []
