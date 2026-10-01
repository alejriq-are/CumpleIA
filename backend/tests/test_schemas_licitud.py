import pytest
from pydantic import ValidationError

from app.schemas.licitud import RatCanonicalContextV1, RatContextSnapshotV1


def canonical_context_v1(**overrides):
    data = {
        "purpose": "gestión de clientes",
        "organization_role": "responsable",
        "data_categories": [
            {
                "category_code": "identificacion",
                "category_name": "datos de identificación",
                "is_sensitive": False,
            }
        ],
        "data_subjects": [
            {
                "category_code": "clientes",
                "category_name": "clientes",
                "includes_children": False,
                "includes_adolescents": False,
                "is_vulnerable_group": False,
            }
        ],
        "data_sources": [
            {
                "source_type": "titular",
                "description": None,
                "is_public_source": False,
            }
        ],
        "retention": {"retention_rule": "5 años"},
        "automated_decisions": {
            "has_automated_decisions": False,
            "description": None,
        },
        "systems": [],
        "third_parties": [],
        "international_transfers": [],
        "special_regimes": {
            "has_sensitive_data": False,
            "includes_children": False,
            "includes_adolescents": False,
            "has_vulnerable_groups": False,
        },
    }
    data.update(overrides)
    return data


def test_rat_canonical_context_v1_acepta_estructura_documentada():
    context = RatCanonicalContextV1.model_validate(canonical_context_v1())

    assert context.purpose == "gestión de clientes"
    assert context.organization_role == "responsable"
    assert context.systems == []
    assert context.data_categories[0].category_code == "identificacion"


def test_rat_canonical_context_v1_rechaza_valores_fuera_de_dominios_m2():
    with pytest.raises(ValidationError):
        RatCanonicalContextV1.model_validate(
            canonical_context_v1(organization_role="controlador")
        )


def test_rat_canonical_context_v1_rechaza_systems_no_vacio():
    with pytest.raises(ValidationError):
        RatCanonicalContextV1.model_validate(
            canonical_context_v1(systems=[{"name": "CRM"}])
        )


def test_rat_context_snapshot_v1_acepta_trazabilidad_documental():
    snapshot = RatContextSnapshotV1.model_validate(
        {
            "purpose": " Gestión de clientes ",
            "organization_role": "responsable",
            "data_categories": [
                {
                    "category_code": "ID",
                    "category_name": "Identidad",
                    "is_sensitive": False,
                    "notes": "Dato declarado por el cliente",
                }
            ],
            "data_subjects": [
                {
                    "category_code": "CLIENTES",
                    "category_name": "Clientes",
                    "includes_children": False,
                    "includes_adolescents": False,
                    "is_vulnerable_group": False,
                    "notes": None,
                }
            ],
            "data_sources": [
                {
                    "source_type": "titular",
                    "description": " Formulario web ",
                    "is_public_source": False,
                }
            ],
            "retention": {
                "retention_rule": " Cinco años ",
                "deletion_method": " Borrado seguro ",
            },
            "automated_decisions": {
                "has_automated_decisions": False,
                "description": "No participa",
            },
            "systems": [
                {
                    "name": "CRM",
                    "provider": "Proveedor",
                    "hosting_location": "Cloud",
                    "hosting_country": "Chile",
                    "is_international": False,
                }
            ],
            "third_parties": [
                {
                    "vendor_name": "Proveedor",
                    "country": " Chile ",
                    "relationship_type": "encargado",
                    "purpose": " Hosting ",
                    "has_data_access": True,
                    "has_contract": True,
                    "contract_reference": "C-123",
                    "engagement_object": "Hosting",
                    "engagement_duration": "12 meses",
                    "has_subprocessors": False,
                    "notes": "Contrato vigente",
                }
            ],
            "international_transfers": [
                {
                    "recipient_name": "Receptor España",
                    "destination_country": " España ",
                    "adequacy_status": "adecuado",
                    "mechanism": None,
                    "guarantees_description": None,
                    "evidence_reference": "EV-001",
                }
            ],
            "special_regimes": {
                "has_sensitive_data": False,
                "includes_children": False,
                "includes_adolescents": False,
                "has_vulnerable_groups": False,
            },
        }
    )

    assert snapshot.purpose == " Gestión de clientes "
    assert snapshot.data_categories[0].notes == "Dato declarado por el cliente"
    assert snapshot.retention.deletion_method == " Borrado seguro "
    assert snapshot.automated_decisions.description == "No participa"
    assert snapshot.systems[0].name == "CRM"
    assert snapshot.third_parties[0].vendor_name == "Proveedor"
    assert snapshot.international_transfers[0].evidence_reference == "EV-001"
