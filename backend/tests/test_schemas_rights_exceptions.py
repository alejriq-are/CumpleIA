import pytest
from pydantic import ValidationError

from app.schemas.licitud import (
    BiometricAssessmentV1,
    BiometricRightsExceptionAssessmentV1,
    RightsExceptionContextV1,
    SensitiveConsentAssessmentV1,
    SensitiveRightsExceptionAssessmentV1,
)

MODELS = [SensitiveRightsExceptionAssessmentV1, BiometricRightsExceptionAssessmentV1]
RESPONSE_CASES = (
    [
        (RightsExceptionContextV1, field)
        for field in [
            "related_to_right",
            "necessary_for_route",
            "within_forum_scope",
            "principles_addressed",
        ]
    ]
    + [(SensitiveRightsExceptionAssessmentV1, "exception_conditions_met")]
    + [
        (BiometricRightsExceptionAssessmentV1, field)
        for field in [
            "unique_identification_confirmed",
            "exception_conditions_met",
            "all_systems_documented",
        ]
    ]
)


@pytest.mark.parametrize("model", [RightsExceptionContextV1] + MODELS)
def test_rights_exception_partial_and_independent_lists(model):
    first, second = model(), model()
    assert first.evidence == [] and first.evidence is not second.evidence
    if model != RightsExceptionContextV1:
        assert (
            first.schema_version == 1 and first.context is None and first.scope is None
        )
        assert first.exception_basis is None
    if model == BiometricRightsExceptionAssessmentV1:
        assert first.systems == [] and first.systems is not second.systems


@pytest.mark.parametrize(
    "field,value",
    [
        ("route", v)
        for v in ["formulacion_derecho", "ejercicio_derecho", "defensa_derecho"]
    ]
    + [("right_holder", v) for v in ["responsable", "tercero", "ambos"]]
    + [("forum_type", v) for v in ["tribunal_justicia", "organo_administrativo"]]
    + [("proceeding_stage", v) for v in ["preparacion", "en_curso", "finalizado"]],
)
def test_rights_exception_context_enums(field, value):
    context = RightsExceptionContextV1.model_validate({field: value})
    assert context.model_dump()[field] == value
    assert context.proceeding_reference is None


@pytest.mark.parametrize("model,field", RESPONSE_CASES)
@pytest.mark.parametrize("answer", ["si", "no", "pendiente"])
def test_rights_exception_partial_responses(model, field, answer):
    document = model.model_validate({field: {"answer": answer}})
    assert document.model_dump()[field] == {"answer": answer, "rationale": None}


@pytest.mark.parametrize(
    "model,basis",
    [
        (SensitiveRightsExceptionAssessmentV1, "defensa_derechos_art16d"),
        (BiometricRightsExceptionAssessmentV1, "defensa_derechos_art16bis_d"),
    ],
)
def test_rights_exception_nested_roundtrip(model, basis):
    payload = {
        "exception_basis": basis,
        "context": {
            "context_reference": "Caso A",
            "forum_type": "organo_administrativo",
            "proceeding_stage": "preparacion",
            "right_basis_reference": "Referencia contractual",
            "evidence": [{"evidence_type": "actuacion", "obtained_on": "1900-01-01"}],
        },
        "scope": {"data_category_codes": ["id"], "data_subject_codes": ["clientes"]},
        "evidence": [{"evidence_type": "expediente", "obtained_on": "2026-10-06"}],
    }
    if model == BiometricRightsExceptionAssessmentV1:
        payload["systems"] = [
            {
                "system_reference": "A",
                "evidence": [{"evidence_type": "aviso", "obtained_on": "1900-01-01"}],
            },
            {"system_reference": "B"},
        ]
    document = model.model_validate(payload)
    serialized = document.model_dump(mode="json")
    assert serialized["context"]["evidence"][0]["obtained_on"] == "1900-01-01"
    assert serialized["evidence"][0]["obtained_on"] == "2026-10-06"
    assert model.model_validate(serialized) == document
    if model == BiometricRightsExceptionAssessmentV1:
        assert [item["system_reference"] for item in serialized["systems"]] == [
            "A",
            "B",
        ]


@pytest.mark.parametrize("stage", ["preparacion", "en_curso", "finalizado"])
def test_rights_exception_conditionals_not_enforced_on_drafts(stage):
    context = RightsExceptionContextV1(
        proceeding_stage=stage,
        preparatory_actions="Por revisar",
        post_proceeding_necessity_analysis="Por revisar",
    )
    assert context.preparatory_actions == "Por revisar"
    assert context.post_proceeding_necessity_analysis == "Por revisar"


@pytest.mark.parametrize("model", MODELS)
@pytest.mark.parametrize(
    "data",
    [
        {"approved": True},
        {"result": "completo"},
        {"can_confirm": True},
        {"eipd_approved": True},
        {"schema_version": 2},
        {"exception_basis": "consentimiento_expreso"},
        {"context": {"approved": True}},
        {"context": {"forum_type": "organo_publico"}},
        {"context": {"route": "otra"}},
        {"context": {"proceeding_stage": "otra"}},
        {"context": {"right_holder": "titular"}},
        {"context": {"evidence": None}},
        {"scope": {"unknown": True}},
        {"scope": {"data_category_codes": [" "]}},
        {"scope": {"data_subject_codes": ["clientes", "clientes"]}},
        {"evidence": None},
        {"evidence": [{"evidence_type": "registro", "approved": True}]},
        {"evidence": [{"evidence_type": "registro", "obtained_on": "invalid"}]},
        {"exception_conditions_met": {"answer": "no_aplica"}},
        {"exception_conditions_met": {"answer": "si", "approved": True}},
        {"context": {"necessary_for_route": {"answer": "no_aplica"}}},
    ],
)
def test_rights_exception_closed_documents(model, data):
    with pytest.raises(ValidationError):
        model.model_validate(data)


@pytest.mark.parametrize("model,field", RESPONSE_CASES)
def test_rights_exception_no_aplica_rejected(model, field):
    with pytest.raises(ValidationError):
        model.model_validate({field: {"answer": "no_aplica"}})


@pytest.mark.parametrize(
    "data",
    [
        {"systems": None},
        {"systems": [{"template": "raw"}]},
        {"systems": [{"purpose_disclosed": {"answer": "no_aplica"}}]},
        {
            "systems": [
                {"evidence": [{"evidence_type": "aviso", "obtained_on": "invalid"}]}
            ]
        },
        {"unique_identification_confirmed": {"answer": "no_aplica"}},
        {"all_systems_documented": {"answer": "no_aplica"}},
        {"exception_basis": "defensa_derechos_art16d"},
    ],
)
def test_biometric_rights_exception_closed_systems(data):
    with pytest.raises(ValidationError):
        BiometricRightsExceptionAssessmentV1.model_validate(data)


def test_exception_bases_are_not_interchangeable_or_consent_routes():
    with pytest.raises(ValidationError):
        SensitiveRightsExceptionAssessmentV1(
            exception_basis="defensa_derechos_art16bis_d"
        )
    for model in (BiometricAssessmentV1, SensitiveConsentAssessmentV1):
        with pytest.raises(ValidationError):
            model.model_validate({"exception_basis": "defensa_derechos_art16d"})


def test_biometric_rights_exception_duplicate_references_left_for_readiness():
    document = BiometricRightsExceptionAssessmentV1(
        systems=[{"system_reference": "A"}, {"system_reference": " a "}]
    )
    assert [item.system_reference for item in document.systems] == ["A", " a "]
