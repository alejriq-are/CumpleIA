from copy import deepcopy

import pytest
from pydantic import ValidationError

from app.schemas.licitud import ConsentAssessmentV1
from app.services.consentimiento import evaluate_consent_assessment_v1


@pytest.fixture
def complete_payload():
    ids = [
        "consentimiento_libre",
        "consentimiento_informado",
        "consentimiento_especifico_finalidad",
        "consentimiento_previo",
        "voluntad_inequivoca",
        "accion_afirmativa_clara",
        "revocacion_posible",
        "revocacion_medio_equivalente",
        "revocacion_expedita",
        "revocacion_fidedigna",
        "revocacion_gratuita",
        "revocacion_disponible_permanentemente",
        "responsable_puede_acreditar",
    ]
    return {
        "given_by": "titular",
        "grant_method": "electronico",
        "answers": [{"question_id": q, "answer": "si"} for q in ids]
        + [{"question_id": "contexto_contrato_servicio", "answer": "no"}],
    }


def test_completo_sin_evidencia_no_muta_y_acepta_modelo(complete_payload):
    original = deepcopy(complete_payload)
    result = evaluate_consent_assessment_v1(complete_payload)
    assert result.result == "completo"
    assert result.can_confirm
    assert result.issues == ()
    assert [a.applicability for a in result.applicability] == [
        "no_aplicable",
        "no_aplicable",
    ]
    assert complete_payload == original
    assert (
        evaluate_consent_assessment_v1(
            ConsentAssessmentV1.model_validate(complete_payload)
        )
        == result
    )


@pytest.mark.parametrize("payload", [None, {}])
def test_expediente_ausente_o_vacio(payload):
    result = evaluate_consent_assessment_v1(payload)
    assert result.result == "incompleto"
    assert not result.can_confirm
    assert all(a.applicability == "sin_resolver" for a in result.applicability)


@pytest.mark.parametrize("field", ["given_by", "grant_method"])
def test_campos_obligatorios(complete_payload, field):
    complete_payload[field] = None
    result = evaluate_consent_assessment_v1(complete_payload)
    assert result.result == "incompleto"
    assert result.issues[0].field == field


@pytest.mark.parametrize(
    "answer,expected,code",
    [
        (None, "incompleto", "pregunta_omitida"),
        ("pendiente", "incompleto", "respuesta_pendiente"),
        ("no_aplica", "incompleto", "no_aplica_invalido"),
        ("no", "requiere_revision", "respuesta_desfavorable"),
    ],
)
def test_pregunta_general(complete_payload, answer, expected, code):
    if answer is None:
        complete_payload["answers"].pop(0)
    else:
        complete_payload["answers"][0]["answer"] = answer
    result = evaluate_consent_assessment_v1(complete_payload)
    assert result.result == expected
    assert result.issues[0].code == code
    assert not result.can_confirm


@pytest.mark.parametrize(
    "question",
    ["mandatario_facultad_expresa", "tratamiento_necesario_contrato_servicio"],
)
@pytest.mark.parametrize(
    "answer,expected",
    [
        (None, "incompleto"),
        ("pendiente", "incompleto"),
        ("no_aplica", "incompleto"),
        ("no", "requiere_revision"),
        ("si", "completo"),
    ],
)
def test_condicional_aplicable(complete_payload, question, answer, expected):
    if question == "mandatario_facultad_expresa":
        complete_payload["given_by"] = "mandatario"
    else:
        complete_payload["answers"][-1]["answer"] = "si"
    if answer is not None:
        complete_payload["answers"].append({"question_id": question, "answer": answer})
    result = evaluate_consent_assessment_v1(complete_payload)
    assert result.result == expected
    assert (
        next(a for a in result.applicability if a.question_id == question).applicability
        == "aplicable"
    )


@pytest.mark.parametrize(
    "question",
    ["mandatario_facultad_expresa", "tratamiento_necesario_contrato_servicio"],
)
@pytest.mark.parametrize(
    "answer,expected",
    [
        ("no_aplica", "completo"),
        ("si", "requiere_revision"),
        ("no", "requiere_revision"),
        ("pendiente", "requiere_revision"),
    ],
)
def test_condicional_no_aplicable(complete_payload, question, answer, expected):
    complete_payload["answers"].append({"question_id": question, "answer": answer})
    result = evaluate_consent_assessment_v1(complete_payload)
    assert result.result == expected
    if expected == "requiere_revision":
        assert result.issues[0].code == "respuesta_no_aplicable"


@pytest.mark.parametrize("answer", [None, "pendiente", "no_aplica"])
def test_dependencia_sin_resolver_no_se_suple_con_condicional(complete_payload, answer):
    if answer is None:
        complete_payload["answers"].pop()
    else:
        complete_payload["answers"][-1]["answer"] = answer
    complete_payload["answers"].append(
        {"question_id": "tratamiento_necesario_contrato_servicio", "answer": "si"}
    )
    result = evaluate_consent_assessment_v1(complete_payload)
    assert result.result == "incompleto"
    assert result.applicability[1].applicability == "sin_resolver"
    assert result.issues[-1].code == "aplicabilidad_sin_resolver"


def test_representante_legal_no_activa_mandatario(complete_payload):
    complete_payload["given_by"] = "representante_legal"
    assert evaluate_consent_assessment_v1(complete_payload).result == "completo"


@pytest.mark.parametrize(
    "evidence_type,expected",
    [("", "incompleto"), (" \t ", "incompleto"), ("registro", "completo")],
)
def test_evidencia_opcional_tipo_no_vacio(complete_payload, evidence_type, expected):
    complete_payload["evidence"] = [{"evidence_type": evidence_type}]
    result = evaluate_consent_assessment_v1(complete_payload)
    assert result.result == expected
    if expected == "incompleto":
        assert result.issues[-1].field == "evidence.0.evidence_type"


def test_precedencia_motivos_y_orden_determinista(complete_payload):
    complete_payload["answers"][0]["answer"] = "no"
    complete_payload["answers"][1]["answer"] = "pendiente"
    result = evaluate_consent_assessment_v1(complete_payload)
    assert result.result == "incompleto"
    assert [i.category for i in result.issues] == ["requiere_revision", "incompleto"]
    complete_payload["answers"].reverse()
    assert evaluate_consent_assessment_v1(complete_payload) == result


@pytest.mark.parametrize(
    "change",
    [
        {"schema_version": 2},
        {"answers": [{"question_id": "desconocida", "answer": "si"}]},
        {"answers": [{"question_id": "consentimiento_libre", "answer": "tal_vez"}]},
        {"evidence": [{"evidence_type": "registro", "obtained_on": "2026-02-30"}]},
    ],
)
def test_contrato_invalido_se_rechaza(complete_payload, change):
    complete_payload.update(change)
    with pytest.raises(ValidationError):
        evaluate_consent_assessment_v1(complete_payload)


def test_duplicados_y_modelo_mutado_se_rechazan(complete_payload):
    model = ConsentAssessmentV1.model_validate(complete_payload)
    model.answers.append(model.answers[0])
    with pytest.raises(ValidationError):
        evaluate_consent_assessment_v1(model)
    complete_payload["answers"].append(complete_payload["answers"][0])
    with pytest.raises(ValidationError):
        evaluate_consent_assessment_v1(complete_payload)
