"""Tests de contratos Pydantic del Módulo 2 — RAT."""

import uuid

import pytest
from pydantic import ValidationError

from app.schemas.rat import (
    InternationalTransferCreate,
    TreatmentCreate,
    TreatmentDataSourceIn,
    TreatmentPurposeIn,
    TreatmentUpdate,
)


def test_treatment_create_acepta_modelo_normalizado():
    model = TreatmentCreate(
        name="Gestión de clientes",
        organization_role="responsable",
        business_area="Comercial",
        has_automated_decisions=False,
    )

    assert model.name == "Gestión de clientes"
    assert model.organization_role == "responsable"
    assert model.has_automated_decisions is False


def test_treatment_rechaza_organization_role_fuera_de_dominio():
    with pytest.raises(ValidationError):
        TreatmentCreate(
            name="Gestión de clientes",
            organization_role="otro",
        )


def test_treatment_update_rechaza_status_fuera_de_dominio():
    with pytest.raises(ValidationError):
        TreatmentUpdate(status="eliminado")


def test_purpose_rechaza_sort_order_negativo():
    with pytest.raises(ValidationError):
        TreatmentPurposeIn(
            purpose="Prestación del servicio",
            sort_order=-1,
        )


def test_data_source_rechaza_tipo_fuera_de_dominio():
    with pytest.raises(ValidationError):
        TreatmentDataSourceIn(
            source_type="desconocida",
        )


def test_transferencia_exige_vendor_o_recipient_name():
    with pytest.raises(ValidationError):
        InternationalTransferCreate(
            destination_country="Estados Unidos",
        )


def test_transferencia_acepta_vendor():
    vendor_id = uuid.uuid4()

    model = InternationalTransferCreate(
        vendor_id=vendor_id,
        destination_country="Estados Unidos",
    )

    assert model.vendor_id == vendor_id
    assert model.adequacy_status == "pendiente"


def test_transferencia_acepta_destinatario_libre():
    model = InternationalTransferCreate(
        recipient_name="Proveedor internacional",
        destination_country="Alemania",
    )

    assert model.recipient_name == "Proveedor internacional"


def test_treatment_no_expone_campos_legacy():
    campos = TreatmentCreate.model_fields

    assert "purpose" not in campos
    assert "data_categories" not in campos
    assert "data_subjects" not in campos
    assert "has_sensitive" not in campos
    assert "retention" not in campos
    assert "is_international" not in campos
