from copy import deepcopy

import pytest
from pydantic import ValidationError

from app.services.economic_obligations import (
    evaluate_economic_obligations_assessment_v1 as evaluate,
)

TEXTS = [
    "purpose_description",
    "obligation_description",
    "obligation_reference",
    "holder_connection_analysis",
    "processing_operations",
    "applicability_analysis",
    "data_minimization_analysis",
    "title_iii_analysis",
    "retention_and_deletion_analysis",
    "accuracy_and_update_analysis",
]
RESPONSES = [
    "related_to_obligation",
    "title_iii_reviewed",
    "processing_within_title_iii",
    "retention_and_deletion_compatible",
    "accuracy_controls_documented",
    "communication_permitted",
    "excluded_data_screened",
    "communication_limits_respected",
]
COND_TEXTS = [
    "communication_scope",
    "communication_eligibility_analysis",
    "communication_restrictions_analysis",
    "payment_and_extinction_controls",
]
COND_RESPONSES = RESPONSES[-3:]


@pytest.mark.parametrize("route", ["sin_comunicacion", "con_comunicacion"])
@pytest.mark.parametrize("kind", ["economica", "financiera", "bancaria", "comercial"])
def test_economico_completo_inmutable(
    complete_economic_obligations, complete_lia_context, route, kind
):
    data = complete_economic_obligations
    data.update(route=route, obligation_type=kind)
    if route == "sin_comunicacion":
        data["operations_include_communication"]["answer"] = "no"
        for field in COND_TEXTS + COND_RESPONSES:
            data.pop(field)
    before = deepcopy(data)
    rat_before = deepcopy(complete_lia_context[1])
    result = evaluate(data, complete_lia_context[1])
    assert result.can_confirm and result.result == "completo"
    assert result == evaluate(data, complete_lia_context[1])
    assert data == before and complete_lia_context[1] == rat_before
    assert {i.applicability for i in result.applicability} == {
        "aplicable" if route == "con_comunicacion" else "no_aplicable"
    }


@pytest.mark.parametrize(
    "field",
    [
        "route",
        "obligation_type",
        "operations_include_communication",
        "normative_references",
        "evidence",
    ]
    + TEXTS
    + RESPONSES
    + COND_TEXTS,
)
def test_economico_faltantes(
    complete_economic_obligations, complete_lia_context, field
):
    complete_economic_obligations.pop(field)
    result = evaluate(complete_economic_obligations, complete_lia_context[1])
    assert result.result == "incompleto"
    assert field in {i.field for i in result.issues}


@pytest.mark.parametrize("field", RESPONSES)
@pytest.mark.parametrize(
    "answer,expected", [("no", "requiere_revision"), ("pendiente", "incompleto")]
)
def test_economico_respuestas_y_precedencia(
    complete_economic_obligations, complete_lia_context, field, answer, expected
):
    data = complete_economic_obligations
    data[field]["answer"] = answer
    assert evaluate(data, complete_lia_context[1]).result == expected
    data[field]["rationale"] = " "
    result = evaluate(data, complete_lia_context[1])
    assert result.result == "incompleto"
    if answer == "no":
        assert {i.category for i in result.issues} == {
            "incompleto",
            "requiere_revision",
        }


@pytest.mark.parametrize("field", COND_TEXTS + COND_RESPONSES)
def test_economico_residuales(
    complete_economic_obligations, complete_lia_context, field
):
    data = complete_economic_obligations
    saved = data[field]
    data["route"] = "sin_comunicacion"
    data["operations_include_communication"]["answer"] = "no"
    for name in COND_TEXTS + COND_RESPONSES:
        data.pop(name)
    data[field] = saved
    result = evaluate(data, complete_lia_context[1])
    assert result.result == "requiere_revision"
    assert [(i.field, i.code) for i in result.issues] == [(field, "campo_residual")]


@pytest.mark.parametrize(
    "route,answer,expected",
    [
        ("con_comunicacion", "no", "requiere_revision"),
        ("sin_comunicacion", "si", "requiere_revision"),
        ("con_comunicacion", "pendiente", "incompleto"),
        (None, "si", "incompleto"),
    ],
)
def test_economico_declaracion_factual(
    complete_economic_obligations, complete_lia_context, route, answer, expected
):
    data = complete_economic_obligations
    data["route"] = route
    data["operations_include_communication"]["answer"] = answer
    if route == "sin_comunicacion":
        for f in COND_TEXTS + COND_RESPONSES:
            data.pop(f)
    result = evaluate(data, complete_lia_context[1])
    assert result.result == expected
    if route is None:
        assert {i.applicability for i in result.applicability} == {"sin_resolver"}
        assert all(i.field not in COND_TEXTS + COND_RESPONSES for i in result.issues)
    else:
        assert "operations_include_communication.answer" in {
            i.field for i in result.issues
        }
    data["operations_include_communication"]["rationale"] = None
    assert evaluate(data, complete_lia_context[1]).result == "incompleto"


@pytest.mark.parametrize(
    "field",
    [
        "norm_name",
        "provision",
        "official_source_url",
        "version_reference",
        "relevance_analysis",
    ],
)
def test_economico_referencia_incompleta(
    complete_economic_obligations, complete_lia_context, field
):
    complete_economic_obligations["normative_references"].append({})
    complete_economic_obligations["normative_references"][0][field] = None
    result = evaluate(complete_economic_obligations, complete_lia_context[1])
    assert result.result == "incompleto"
    assert f"normative_references.0.{field}" in {i.field for i in result.issues}
    assert [i.field for i in result.issues][-5:] == [
        f"normative_references.1.{f}"
        for f in (
            "norm_name",
            "provision",
            "official_source_url",
            "version_reference",
            "relevance_analysis",
        )
    ]


@pytest.mark.parametrize("change", ["purpose", "role", "evidence"])
def test_economico_contexto_y_evidencia(
    complete_economic_obligations, complete_lia_context, change
):
    data = complete_economic_obligations
    rat = complete_lia_context[1]
    if change == "purpose":
        data["purpose_description"] = "Otra finalidad"
    elif change == "role":
        rat["organization_role"] = "encargado"
    else:
        data["evidence"].append({"evidence_type": " "})
    result = evaluate(data, rat)
    assert result.result == (
        "incompleto" if change == "evidence" else "requiere_revision"
    )
    data["title_iii_analysis"] = " "
    assert evaluate(data, rat).result == "incompleto"


def test_economico_ausencia_validacion_canonizacion_orden(
    complete_economic_obligations, complete_lia_context
):
    assert evaluate(None, None).result == "incompleto"
    with pytest.raises(ValidationError):
        evaluate({"approved": True}, None)
    with pytest.raises(ValidationError):
        evaluate(None, {})
    data = complete_economic_obligations
    data["purpose_description"] = " GESTIÓN de clientes "
    assert evaluate(data, complete_lia_context[1]).result == "completo"
    data["related_to_obligation"] = {"answer": "pendiente"}
    assert [i.field for i in evaluate(data, complete_lia_context[1]).issues] == [
        "related_to_obligation.answer",
        "related_to_obligation.rationale",
    ]
