"""Casos ficticios de forma; no prueban facultad, aplicabilidad o preparacion."""

from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas.licitud import ContractEvidenceV1
from app.schemas.sensitive_representation import SensitiveRepresentationAssessmentV1


@pytest.mark.parametrize("kind", [None, "representante_legal", "mandatario"])
def test_partial_draft_does_not_authorize(kind):
    value = SensitiveRepresentationAssessmentV1(representation_kind=kind)
    assert value.evidence == []
    assert value.scope is None
    assert not hasattr(value, "can_confirm")
    assert not hasattr(value, "ready")


@pytest.mark.parametrize("kind", ["titular", "parentesco", "administrador", ""])
def test_unknown_kind_is_rejected(kind):
    with pytest.raises(ValidationError):
        SensitiveRepresentationAssessmentV1(representation_kind=kind)


@pytest.mark.parametrize(
    "field",
    [
        "representative_reference",
        "represented_subjects_reference",
        "authority_document_reference",
        "authority_document_version",
        "authority_basis_description",
        "express_authority_analysis",
        "scope_match_analysis",
        "validity_analysis",
        "limitations",
        "revocation_information",
        "notes",
    ],
)
def test_supplied_blank_text_is_rejected_but_none_is_partial(field):
    with pytest.raises(ValidationError):
        SensitiveRepresentationAssessmentV1(**{field: " \t\n"})
    assert getattr(SensitiveRepresentationAssessmentV1(**{field: None}), field) is None


@pytest.mark.parametrize(
    "field",
    [
        "ready",
        "can_confirm",
        "accepted_by",
        "context_binding",
        "context_hash",
        "created_by",
        "created_at",
        "organization_id",
        "assessment_id",
    ],
)
def test_server_or_authority_fields_are_not_editable(field):
    with pytest.raises(ValidationError):
        SensitiveRepresentationAssessmentV1(**{field: "PRUEBA"})


@pytest.mark.parametrize("version", [0, 2, "otra"])
def test_unknown_schema_version_is_rejected(version):
    with pytest.raises(ValidationError):
        SensitiveRepresentationAssessmentV1(schema_version=version)


@pytest.mark.parametrize(
    "scope",
    [
        {"data_category_codes": ["PRUEBA", "PRUEBA"]},
        {"data_subject_codes": ["PRUEBA", "PRUEBA"]},
        {"data_category_codes": [" "]},
        {"data_subject_codes": [""]},
        {"can_confirm": True},
    ],
)
def test_scope_remains_closed_and_unambiguous(scope):
    with pytest.raises(ValidationError):
        SensitiveRepresentationAssessmentV1(scope=scope)


def test_documented_interval_rejects_reverse_order_only():
    with pytest.raises(ValidationError):
        SensitiveRepresentationAssessmentV1(
            valid_from=date(2026, 2, 2), valid_until=date(2026, 2, 1)
        )
    same = SensitiveRepresentationAssessmentV1(
        valid_from=date(2026, 2, 2), valid_until=date(2026, 2, 2)
    )
    assert same.valid_from == same.valid_until
    partial = SensitiveRepresentationAssessmentV1(valid_until=date(2026, 2, 1))
    assert partial.valid_from is None
    assert SensitiveRepresentationAssessmentV1().valid_until is None


@pytest.mark.parametrize("kind", ["representante_legal", "mandatario"])
def test_fictitious_document_roundtrips_without_inferring_authority(kind):
    payload = {
        "representation_kind": kind,
        "representative_reference": "PRUEBA: representante ficticio",
        "represented_subjects_reference": "PRUEBA: titulares ficticios",
        "authority_document_reference": "PRUEBA: documento",
        "authority_document_version": "PRUEBA-1",
        "authority_basis_description": "PRUEBA: fundamento declarado, no acreditado",
        "express_authority_analysis": "PRUEBA: analisis ficticio",
        "scope": {"data_category_codes": ["PRUEBA"], "data_subject_codes": ["PRUEBA"]},
        "scope_match_analysis": "PRUEBA: correspondencia declarada",
        "issued_on": "2026-01-01",
        "valid_from": "2026-01-02",
        "valid_until": "2026-02-01",
        "validity_analysis": "PRUEBA: sin validacion externa",
        "limitations": "PRUEBA: no acredita facultades reales",
        "revocation_information": "PRUEBA: informacion ficticia",
        "evidence": [{"evidence_type": "PRUEBA", "reference": "PRUEBA: evidencia"}],
    }
    value = SensitiveRepresentationAssessmentV1.model_validate(payload)
    assert value.model_dump(mode="json", exclude_unset=True) == payload
    restored = SensitiveRepresentationAssessmentV1.model_validate_json(
        value.model_dump_json()
    )
    assert restored == value
    assert not hasattr(value, "can_confirm")


def test_evidence_lists_are_independent_and_reject_extra_fields():
    first = SensitiveRepresentationAssessmentV1()
    second = SensitiveRepresentationAssessmentV1()
    first.evidence.append(ContractEvidenceV1(evidence_type="PRUEBA"))
    assert second.evidence == []
    with pytest.raises(ValidationError):
        SensitiveRepresentationAssessmentV1(
            evidence=[{"evidence_type": "PRUEBA", "accepted_by": "PRUEBA"}]
        )
