"""Contrato ficticio parcial, cerrado, sin inferir edad ni facultades."""

import pytest
from pydantic import ValidationError

from app.schemas.child_adolescent import ChildAdolescentAssessmentV1 as Document


def test_partial_document_is_not_authorization():
    value = Document()
    assert value.declared_groups == []
    assert value.sensitive_under16 is None
    assert value.proposed_authorization_route is None
    assert "can_confirm" not in value.model_dump()
    assert Document.model_validate_json(value.model_dump_json()) == value


@pytest.mark.parametrize(
    "field",
    [
        "can_confirm",
        "authorizes_action",
        "context_binding",
        "created_by",
        "date_of_birth",
    ],
)
def test_server_or_personal_identity_fields_rejected(field):
    with pytest.raises(ValidationError):
        Document.model_validate({field: "PRUEBA"})


@pytest.mark.parametrize("groups", [["adultos"], ["adolescentes", "adolescentes"]])
def test_unknown_or_duplicate_groups_rejected(groups):
    with pytest.raises(ValidationError):
        Document(declared_groups=groups)


def test_declarations_do_not_infer_consent_giver_or_age_from_names():
    value = Document(
        declared_groups=["adolescentes"],
        data_subject_codes=["PRUEBA_menores_16"],
        notes="PRUEBA: menor de edad",
    )
    assert value.sensitive_under16 is None
    assert value.declared_consent_giver is None
    assert value.proposed_authorization_route is None


def test_subgroup_and_sensitive_assertion_remain_separate_documentary_inputs():
    value = Document(
        declared_groups=["adolescentes_sensibles_menores_16"],
        sensitive_under16="pendiente",
    )
    assert value.sensitive_under16 == "pendiente"
    assert value.authorization_reference is None
    assert value.authorization_analysis is None
