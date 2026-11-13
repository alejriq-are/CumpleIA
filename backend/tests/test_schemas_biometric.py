import pytest
from pydantic import ValidationError

from app.schemas.licitud import BiometricAssessmentV1, BiometricSystemV1

SYSTEM_RESPONSES = [
    "system_identification_disclosed",
    "purpose_disclosed",
    "use_period_disclosed",
    "rights_exercise_disclosed",
]
ASSESSMENT_RESPONSES = ["unique_identification_confirmed", "all_systems_documented"]


def test_biometric_partial_drafts_and_independent_lists():
    first, second = BiometricAssessmentV1(), BiometricAssessmentV1()
    assert first.schema_version == 1 and first.route is None and first.scope is None
    for field in ("systems", "evidence"):
        assert getattr(first, field) == []
        assert getattr(first, field) is not getattr(second, field)
    left, right = BiometricSystemV1(), BiometricSystemV1()
    assert left.system_reference is None
    assert left.evidence == [] and left.evidence is not right.evidence


@pytest.mark.parametrize("field", SYSTEM_RESPONSES)
@pytest.mark.parametrize("answer", ["si", "no", "pendiente"])
def test_biometric_system_partial_responses(field, answer):
    system = BiometricSystemV1.model_validate({field: {"answer": answer}})
    assert system.model_dump()[field] == {"answer": answer, "rationale": None}


@pytest.mark.parametrize("field", ASSESSMENT_RESPONSES)
@pytest.mark.parametrize("answer", ["si", "no", "pendiente"])
def test_biometric_assessment_partial_responses(field, answer):
    document = BiometricAssessmentV1.model_validate({field: {"answer": answer}})
    assert document.model_dump()[field] == {"answer": answer, "rationale": None}


def test_biometric_systems_roundtrip_and_factual_dates():
    payload = {
        "route": "consentimiento_expreso",
        "scope": {"data_category_codes": ["bio"], "data_subject_codes": ["clientes"]},
        "systems": [
            {
                "system_reference": "system-a",
                "specific_purpose": "Acceso",
                "evidence": [{"evidence_type": "aviso", "obtained_on": "1900-01-01"}],
            },
            {
                "system_reference": "system-b",
                "specific_purpose": "Verificación",
                "rights_exercise_disclosed": {
                    "answer": "si",
                    "rationale": "Canal comunicado",
                },
            },
        ],
    }
    document = BiometricAssessmentV1.model_validate(payload)
    serialized = document.model_dump(mode="json")
    assert [item["system_reference"] for item in serialized["systems"]] == [
        "system-a",
        "system-b",
    ]
    assert serialized["systems"][0]["evidence"][0]["obtained_on"] == "1900-01-01"
    assert (
        serialized["systems"][1]["rights_exercise_disclosed"]["rationale"]
        == "Canal comunicado"
    )
    assert BiometricAssessmentV1.model_validate(serialized) == document


def test_biometric_semantic_duplicates_remain_for_readiness():
    document = BiometricAssessmentV1(
        systems=[{"system_reference": " A "}, {"system_reference": "a"}, {}]
    )
    assert len(document.systems) == 3
    assert document.systems[0].system_reference == " A "


@pytest.mark.parametrize(
    "data",
    [
        {"approved": True},
        {"result": "completo"},
        {"can_confirm": True},
        {"schema_version": 2},
        {"route": "excepcion_legal"},
        {"systems": None},
        {"systems": ["invalid"]},
        {"systems": [{"approved": True}]},
        {"systems": [{"template": "raw"}]},
        {"scope": {"unknown": True}},
        {"scope": {"data_category_codes": [" "]}},
        {"scope": {"data_subject_codes": ["clientes", "clientes"]}},
        {"evidence": [{"evidence_type": "aviso", "obtained_on": "invalid"}]},
        {"evidence": [{"evidence_type": "aviso", "approved": True}]},
    ]
    + [{field: {"answer": "no_aplica"}} for field in ASSESSMENT_RESPONSES],
)
def test_biometric_assessment_closed_contract(data):
    with pytest.raises(ValidationError):
        BiometricAssessmentV1.model_validate(data)


@pytest.mark.parametrize(
    "data",
    [
        {"approved": True},
        {"result": "completo"},
        {"can_confirm": True},
        {"embedding": [0.1]},
        {"fingerprint": "raw"},
        {"evidence": None},
        {"evidence": [{"evidence_type": "aviso", "obtained_on": "invalid"}]},
        {"evidence": [{"evidence_type": "aviso", "approved": True}]},
    ]
    + [{field: {"answer": "no_aplica"}} for field in SYSTEM_RESPONSES]
    + [{field: {"answer": "si", "approved": True}} for field in SYSTEM_RESPONSES],
)
def test_biometric_system_closed_contract(data):
    with pytest.raises(ValidationError):
        BiometricSystemV1.model_validate(data)
