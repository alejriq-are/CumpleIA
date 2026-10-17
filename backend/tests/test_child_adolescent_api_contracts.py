"""Entradas cerradas; API publica el documento y conserva contratos historicos."""

import pytest
from pydantic import ValidationError

from app.schemas.child_adolescent_api import (
    LegalAssessmentChildDraftCreateV1 as Create,
)
from app.schemas.child_adolescent_api import (
    LegalAssessmentChildDraftUpdateV1 as Update,
)
from app.schemas.child_adolescent_api import (
    LegalAssessmentChildOutV1 as Out,
)
from app.schemas.licitud import (
    LegalAssessmentRepresentationDraftCreateV1,
    LegalAssessmentRepresentationDraftUpdateV1,
    LegalAssessmentRepresentationOutV2,
)

CREATE = dict(
    purpose_id="a0000000-0000-0000-0000-000000000001",
    scope=dict(data_category_codes=["PRUEBA"], data_subject_codes=["PRUEBA"]),
)


@pytest.mark.parametrize("model", [Create, Update])
def test_omission_null_and_reaporte_have_distinct_intent(model):
    base = CREATE if model is Create else {}
    absent = model.model_validate(base)
    null = model.model_validate({**base, "child_adolescent_assessment": None})
    supplied = model.model_validate(
        {**base, "child_adolescent_assessment": {"declared_groups": ["ninos_ninas"]}}
    )
    assert "child_adolescent_assessment" not in absent.model_fields_set
    assert "child_adolescent_assessment" in null.model_fields_set
    assert null.child_adolescent_assessment is None
    assert supplied.child_adolescent_assessment.declared_groups == ["ninos_ninas"]
    assert (
        model.model_validate_json(supplied.model_dump_json(exclude_unset=True))
        == supplied
    )


@pytest.mark.parametrize("model", [Create, Update])
@pytest.mark.parametrize(
    "field",
    [
        "context_binding",
        "context_hash",
        "document_hash",
        "created_by",
        "can_confirm",
        "authorizes_action",
    ],
)
def test_raw_document_rejects_server_fields(model, field):
    base = CREATE if model is Create else {}
    with pytest.raises(ValidationError):
        model.model_validate({**base, "child_adolescent_assessment": {field: "PRUEBA"}})


@pytest.mark.parametrize("model", [Create, Update])
def test_server_envelope_not_accepted_as_document(model):
    base = CREATE if model is Create else {}
    with pytest.raises(ValidationError):
        model.model_validate(
            {
                **base,
                "child_adolescent_assessment": {
                    "assessment": {},
                    "context_binding": {
                        "binding_version": 1,
                        "context_hash": "a" * 64,
                        "document_hash": "b" * 64,
                    },
                },
            }
        )


def test_historical_contracts_unchanged_and_openapi_publishes_new_field():
    from app.main import app

    for model in (
        LegalAssessmentRepresentationDraftCreateV1,
        LegalAssessmentRepresentationDraftUpdateV1,
        LegalAssessmentRepresentationOutV2,
    ):
        assert "child_adolescent_assessment" not in model.model_fields
    assert "child_adolescent_assessment" in Out.model_fields
    spec = app.openapi()
    for path, operations in spec["paths"].items():
        if path.startswith("/licitud/treatments/") and (
            path.endswith("/assessments") or path.endswith("/{assessment_id}")
        ):
            for method in ("post", "patch"):
                operation = operations.get(method)
                if not operation or "requestBody" not in operation:
                    continue
                ref = operation["requestBody"]["content"]["application/json"][
                    "schema"
                ].get("$ref")
                if ref:
                    schema = spec["components"]["schemas"][ref.rsplit("/", 1)[1]]
                    assert "child_adolescent_assessment" in schema.get("properties", {})
