import pytest
from pydantic import ValidationError

from app.schemas.licitud import SensitiveConsentAssessmentV1


@pytest.mark.parametrize("method", ["escrito", "verbal", "tecnologico_equivalente"])
def test_sensitive_consent_partial_and_factual_date(method):
    document = SensitiveConsentAssessmentV1.model_validate(
        {
            "expression_method": method,
            "declaration_obtained_on": "2026-10-06",
            "evidence": [{"evidence_type": "declaracion", "obtained_on": "2020-01-01"}],
        }
    )
    assert document.scope is None
    assert document.declaration_version_reference is None
    assert document.technology_equivalence_analysis is None
    serialized = document.model_dump(mode="json")
    assert serialized["declaration_obtained_on"] == "2026-10-06"
    assert serialized["evidence"][0]["obtained_on"] == "2020-01-01"


@pytest.mark.parametrize(
    "field",
    [
        "express_declaration_documented",
        "sensitive_scope_explicit",
        "purpose_specific",
        "proof_available",
        "consent_current",
    ],
)
@pytest.mark.parametrize("answer", ["si", "no", "pendiente"])
def test_sensitive_consent_draft_responses(field, answer):
    document = SensitiveConsentAssessmentV1.model_validate({field: {"answer": answer}})
    assert document.model_dump()[field]["answer"] == answer


@pytest.mark.parametrize(
    "data",
    [
        {"approved": True},
        {"schema_version": 2},
        {"expression_method": "acto_afirmativo"},
        {"declaration_obtained_on": "invalid"},
        {"scope": {"unknown": True}},
        {"evidence": [{"evidence_type": "registro", "obtained_on": "invalid"}]},
    ]
    + [
        {field: {"answer": "no_aplica"}}
        for field in [
            "express_declaration_documented",
            "sensitive_scope_explicit",
            "purpose_specific",
            "proof_available",
            "consent_current",
        ]
    ],
)
def test_sensitive_consent_closed_contract(data):
    with pytest.raises(ValidationError):
        SensitiveConsentAssessmentV1.model_validate(data)


def test_sensitive_consent_empty_draft_evidence_is_independent():
    first = SensitiveConsentAssessmentV1()
    second = SensitiveConsentAssessmentV1()
    assert first.evidence == [] and second.evidence == []
    assert first.evidence is not second.evidence
