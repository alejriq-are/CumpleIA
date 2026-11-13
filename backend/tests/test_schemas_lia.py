import pytest
from pydantic import ValidationError

from app.schemas.licitud import LegalAssessmentDraftUpdate, LiaAssessmentV1


def test_lia_borrador_vacio_y_colecciones_independientes():
    first, second = LiaAssessmentV1(), LiaAssessmentV1()
    assert first.schema_version == 1
    assert first.conclusion.decision is None
    assert first.necessity.contributes_to_purpose is None
    assert first.safeguards.measures == []
    assert first.safeguards.measures is not second.safeguards.measures
    assert first.impact is not second.impact


def test_lia_documental_preserva_textos_y_respuestas_en_roundtrip():
    payload = {
        "purpose_and_interest": {
            "legitimate_interest": " Gestión de clientes ",
            "interest_holder": "ambos",
        },
        "necessity": {
            "less_intrusive_alternative": {
                "answer": "no",
                "comment": "Alternativas analizadas",
            },
            "proportionality_analysis": "Análisis documentado",
        },
        "nature_and_scope": {
            "exclusively_professional_context": {"answer": "no_aplica"}
        },
        "reasonable_expectations": {"prior_relationship": {"answer": "si"}},
        "impact": {
            "severity": "media",
            "likelihood": "baja",
            "relevant_unmitigated_impacts": {"answer": "pendiente"},
        },
        "safeguards": {
            "measures": [
                {
                    "description": " Acceso restringido ",
                    "mitigated_impact": "Acceso indebido",
                }
            ]
        },
        "transparency_and_opposition": {"opposition_channel": "Portal"},
        "conclusion": {
            "decision": "requiere_revision",
            "balancing_summary": "Pendiente de revisión",
        },
    }
    result = LiaAssessmentV1.model_validate(payload)
    assert result.purpose_and_interest.legitimate_interest == " Gestión de clientes "
    assert result.safeguards.measures[0].description == " Acceso restringido "
    assert LiaAssessmentV1.model_validate_json(result.model_dump_json()) == result
    assert (
        result.model_dump(mode="json")["necessity"]["less_intrusive_alternative"]
        == payload["necessity"]["less_intrusive_alternative"]
    )


@pytest.mark.parametrize(
    "payload",
    [
        {"schema_version": 2},
        {"purpose_and_interest": {"interest_holder": "publico"}},
        {"conclusion": {"decision": "aprobado"}},
        {"impact": {"severity": "critica"}},
        {"impact": {"likelihood": "imposible"}},
        {"necessity": {"linked_to_interest": {"answer": "tal_vez"}}},
        {"necessity": {"linked_to_interest": {}}},
        {"safeguards": {"measures": [{}]}},
        {"necessity": None},
    ],
)
def test_lia_rechaza_estructura_y_dominios_invalidos(payload):
    with pytest.raises(ValidationError):
        LiaAssessmentV1.model_validate(payload)


@pytest.mark.parametrize(
    "section",
    [
        "purpose_and_interest",
        "necessity",
        "nature_and_scope",
        "reasonable_expectations",
        "impact",
        "safeguards",
        "transparency_and_opposition",
        "conclusion",
    ],
)
def test_lia_no_descarta_campos_desconocidos(section):
    with pytest.raises(ValidationError):
        LiaAssessmentV1.model_validate({section: {"campo_desconocido": "valor"}})


def test_lia_no_admite_duplicar_hechos_rat_ni_campos_de_version_futura():
    with pytest.raises(ValidationError):
        LiaAssessmentV1.model_validate({"nature_and_scope": {"data_categories": []}})
    with pytest.raises(ValidationError):
        LiaAssessmentV1.model_validate({"nueva_seccion": {}})
    with pytest.raises(ValidationError):
        LiaAssessmentV1.model_validate(
            {"necessity": {"linked_to_interest": {"answer": "si", "confidence": 1}}}
        )


def test_lia_update_distingue_omision_null_y_seccion_vacia():
    assert LegalAssessmentDraftUpdate().model_dump(exclude_unset=True) == {}
    assert LegalAssessmentDraftUpdate(lia_assessment=None).model_dump(
        exclude_unset=True
    ) == {"lia_assessment": None}
    updated = LegalAssessmentDraftUpdate.model_validate({"lia_assessment": {}})
    assert updated.lia_assessment.schema_version == 1
