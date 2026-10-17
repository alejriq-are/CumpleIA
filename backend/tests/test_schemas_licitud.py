import pytest
from pydantic import ValidationError

from app.schemas.licitud import (
    ConsentAssessmentV1,
    LegalAssessmentDraftCreate,
    LegalAssessmentDraftUpdate,
    RatCanonicalContextV1,
    RatContextSnapshotV1,
)


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


def test_legal_assessment_draft_create_acepta_borrador_incompleto():
    payload = LegalAssessmentDraftCreate.model_validate(
        {
            "purpose_id": "11111111-1111-1111-1111-111111111111",
            "scope": {
                "data_category_codes": ["identificacion"],
                "data_subject_codes": ["clientes"],
            },
            "legal_basis": None,
            "justification": None,
        }
    )

    assert str(payload.purpose_id) == "11111111-1111-1111-1111-111111111111"
    assert payload.legal_basis is None
    assert payload.justification is None


def test_legal_assessment_draft_create_rechaza_base_fuera_de_catalogo():
    with pytest.raises(ValidationError):
        LegalAssessmentDraftCreate.model_validate(
            {
                "purpose_id": "11111111-1111-1111-1111-111111111111",
                "scope": {
                    "data_category_codes": [],
                    "data_subject_codes": [],
                },
                "legal_basis": "otra",
            }
        )


def test_legal_assessment_draft_update_preserva_campos_omitidos():
    payload = LegalAssessmentDraftUpdate.model_validate(
        {"justification": "Pendiente de revisión"}
    )

    assert payload.model_dump(exclude_unset=True) == {
        "justification": "Pendiente de revisión"
    }


def test_legal_assessment_draft_update_admite_null_explicito():
    payload = LegalAssessmentDraftUpdate.model_validate({"legal_basis": None})

    assert payload.model_dump(exclude_unset=True) == {"legal_basis": None}


def test_legal_assessment_draft_update_rechaza_scope_null_explicito():
    with pytest.raises(ValidationError) as exc:
        LegalAssessmentDraftUpdate.model_validate({"scope": None})

    assert "scope no puede ser null" in str(exc.value)


def test_consent_assessment_v1_admite_borrador_y_listas_independientes():
    draft = ConsentAssessmentV1.model_validate({})
    partial = ConsentAssessmentV1.model_validate(
        {"answers": [{"question_id": "consentimiento_libre", "answer": "pendiente"}]}
    )
    assert draft.given_by is None
    assert draft.grant_method is None
    assert draft.answers == []
    assert draft.evidence == []
    assert partial.answers[0].answer == "pendiente"
    assert draft.answers is not partial.answers


def test_consent_assessment_v1_preserva_evidencia_en_json():
    payload = {
        "schema_version": 1,
        "given_by": "mandatario",
        "grant_method": "electronico",
        "answers": [
            {
                "question_id": "mandatario_facultad_expresa",
                "answer": "si",
                "comment": "Verificado",
            },
            {"question_id": "contexto_contrato_servicio", "answer": "no"},
            {
                "question_id": "tratamiento_necesario_contrato_servicio",
                "answer": "no_aplica",
            },
        ],
        "evidence": [
            {
                "evidence_type": "registro",
                "reference": "EV-1",
                "obtained_on": "2026-10-05",
                "mechanism": "Portal",
                "notes": "Original",
            }
        ],
        "notes": "Pendiente de confirmación",
    }
    assessment = ConsentAssessmentV1.model_validate(payload)
    serialized = assessment.model_dump(mode="json")
    assert serialized["evidence"] == payload["evidence"]
    assert serialized["answers"][0] == payload["answers"][0]
    assert (
        ConsentAssessmentV1.model_validate_json(assessment.model_dump_json())
        == assessment
    )


@pytest.mark.parametrize(
    "payload",
    [
        {"schema_version": 2},
        {"given_by": "tercero"},
        {"grant_method": "desconocido"},
        {"answers": [{"question_id": "desconocida", "answer": "si"}]},
        {"answers": [{"question_id": "consentimiento_libre", "answer": "tal_vez"}]},
        {"evidence": [{"evidence_type": "registro", "obtained_on": "2026-02-30"}]},
    ],
)
def test_consent_assessment_v1_rechaza_dominios_y_fecha_invalidos(payload):
    with pytest.raises(ValidationError):
        ConsentAssessmentV1.model_validate(payload)


def test_consent_assessment_v1_rechaza_preguntas_duplicadas():
    with pytest.raises(ValidationError, match="question_id duplicados"):
        ConsentAssessmentV1.model_validate(
            {
                "answers": [
                    {"question_id": "consentimiento_libre", "answer": "si"},
                    {"question_id": "consentimiento_libre", "answer": "no"},
                ]
            }
        )
