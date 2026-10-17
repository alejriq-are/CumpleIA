"""Contratos versionados de documento/binding; nunca autorizan acciones."""

import pytest
from pydantic import ValidationError

from app.schemas import sensitive_representation as facade
from app.schemas.licitud import (
    BoundSensitiveRepresentationV1,
    LegalAssessmentDraftCreate,
    LegalAssessmentDraftUpdate,
    LegalAssessmentOut,
    LegalAssessmentRepresentationDraftCreateV1,
    LegalAssessmentRepresentationDraftUpdateV1,
    LegalAssessmentRepresentationOutV1,
    SensitiveRepresentationAssessmentV1,
)

CREATE = {
    "purpose_id": "a0000000-0000-0000-0000-000000000001",
    "scope": {"data_category_codes": ["PRUEBA"], "data_subject_codes": ["PRUEBA"]},
}
MODELS = [
    LegalAssessmentRepresentationDraftCreateV1,
    LegalAssessmentRepresentationDraftUpdateV1,
]


@pytest.mark.parametrize("model", MODELS)
def test_omission_null_and_document_are_distinct(model):
    base = CREATE if model is MODELS[0] else {}
    absent = model.model_validate(base)
    explicit = model.model_validate(
        {**base, "sensitive_representation_assessment": None}
    )
    document = model.model_validate(
        {
            **base,
            "sensitive_representation_assessment": {
                "representation_kind": "mandatario",
                "authority_document_reference": "PRUEBA",
            },
        }
    )
    assert "sensitive_representation_assessment" not in absent.model_fields_set
    assert "sensitive_representation_assessment" in explicit.model_fields_set
    assert explicit.sensitive_representation_assessment is None
    assert (
        document.sensitive_representation_assessment.authority_document_reference
        == "PRUEBA"
    )


@pytest.mark.parametrize("model", MODELS)
@pytest.mark.parametrize(
    "field",
    [
        "context_binding",
        "context_hash",
        "document_hash",
        "created_by",
        "accepted_by",
        "can_confirm",
    ],
)
def test_server_fields_inside_document_are_rejected(model, field):
    base = CREATE if model is MODELS[0] else {}
    with pytest.raises(ValidationError):
        model.model_validate(
            {**base, "sensitive_representation_assessment": {field: "PRUEBA"}}
        )


@pytest.mark.parametrize("model", MODELS)
def test_bound_envelope_is_not_document_input(model):
    base = CREATE if model is MODELS[0] else {}
    with pytest.raises(ValidationError):
        model.model_validate(
            {
                **base,
                "sensitive_representation_assessment": {
                    "assessment": {},
                    "context_binding": {
                        "binding_version": 1,
                        "context_hash": "a" * 64,
                        "document_hash": "b" * 64,
                    },
                },
            }
        )


def test_update_keeps_existing_null_scope_rejection():
    with pytest.raises(ValidationError):
        LegalAssessmentRepresentationDraftUpdateV1(scope=None)


def test_facade_exports_same_classes_and_output_uses_server_shape():
    assert (
        facade.SensitiveRepresentationAssessmentV1
        is SensitiveRepresentationAssessmentV1
    )
    assert facade.BoundSensitiveRepresentationV1 is BoundSensitiveRepresentationV1
    schema = LegalAssessmentRepresentationOutV1.model_json_schema()
    prop = schema["properties"]["sensitive_representation_assessment"]
    assert {"$ref": "#/$defs/BoundSensitiveRepresentationV1"} in prop["anyOf"]


def test_legacy_models_remain_without_new_field():
    for model in [
        LegalAssessmentDraftCreate,
        LegalAssessmentDraftUpdate,
        LegalAssessmentOut,
    ]:
        assert "sensitive_representation_assessment" not in model.model_fields


@pytest.mark.parametrize(
    "change",
    [
        {"can_confirm": True},
        {"authorizes_action": True},
        {"evaluation_version": 2},
        {
            "result": "completo",
            "issues": [{"field": "PRUEBA", "code": "PRUEBA", "category": "incompleto"}],
        },
    ],
)
def test_readiness_cannot_claim_authority_or_inconsistent_completeness(change):
    from app.schemas.licitud import SensitiveRepresentationReadinessOutV1

    with pytest.raises(ValidationError):
        SensitiveRepresentationReadinessOutV1.model_validate(
            {"result": "completo", "issues": [], **change}
        )
