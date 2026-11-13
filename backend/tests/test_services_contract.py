from copy import deepcopy

import pytest
from pydantic import ValidationError

from app.schemas.licitud import ContractAssessmentV1, RatContextSnapshotV1
from app.services.contract import evaluate_contract_assessment_v1


@pytest.mark.parametrize(
    "route", ["celebracion_contrato", "ejecucion_contrato", "medidas_precontractuales"]
)
def test_contrato_completo_por_ruta(complete_contract, complete_lia_context, route):
    _, rat = complete_lia_context
    complete_contract["route"] = route
    if route == "medidas_precontractuales":
        complete_contract.pop("contractual_reference")
        complete_contract.update(
            precontractual_measures="Preparar oferta",
            requested_by_holder={"answer": "si", "rationale": "Solicitud recibida"},
            request_reference="Solicitud interna",
        )
    original = deepcopy(complete_contract)
    a = evaluate_contract_assessment_v1(complete_contract, rat)
    assert a.result == "completo" and a.can_confirm
    assert a == evaluate_contract_assessment_v1(
        ContractAssessmentV1.model_validate(complete_contract),
        RatContextSnapshotV1.model_validate(rat),
    )
    assert complete_contract == original
    states = {i.field: i.applicability for i in a.applicability}
    assert states["requested_by_holder"] == (
        "aplicable" if route == "medidas_precontractuales" else "no_aplicable"
    )


@pytest.mark.parametrize(
    "field",
    [
        "route",
        "purpose_description",
        "relationship_description",
        "contractual_reference",
        "contractual_object",
        "processing_operations",
        "necessity_analysis",
        "data_minimization_analysis",
        "holder_is_party",
        "necessary_for_route",
        "purpose_within_route",
        "evidence",
    ],
)
def test_contrato_faltante_es_incompleto(
    complete_contract, complete_lia_context, field
):
    _, rat = complete_lia_context
    complete_contract.pop(field)
    a = evaluate_contract_assessment_v1(complete_contract, rat)
    assert a.result == "incompleto" and not a.can_confirm
    assert field in {i.field for i in a.issues}


@pytest.mark.parametrize(
    "field", ["holder_is_party", "necessary_for_route", "purpose_within_route"]
)
@pytest.mark.parametrize(
    "answer,expected", [("no", "requiere_revision"), ("pendiente", "incompleto")]
)
def test_respuestas_contractuales(
    complete_contract, complete_lia_context, field, answer, expected
):
    complete_contract[field]["answer"] = answer
    assert (
        evaluate_contract_assessment_v1(
            complete_contract, complete_lia_context[1]
        ).result
        == expected
    )


@pytest.mark.parametrize(
    "field", ["holder_is_party", "necessary_for_route", "purpose_within_route"]
)
def test_fundamento_contractual_vacio(complete_contract, complete_lia_context, field):
    complete_contract[field]["rationale"] = " "
    result = evaluate_contract_assessment_v1(complete_contract, complete_lia_context[1])
    assert (
        result.result == "incompleto" and result.issues[0].code == "fundamento_ausente"
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("requested_by_holder", {"answer": "pendiente"}),
        ("precontractual_measures", "Contenido residual"),
        ("request_reference", "Solicitud residual"),
    ],
)
def test_condicional_residual(complete_contract, complete_lia_context, field, value):
    complete_contract[field] = value
    result = evaluate_contract_assessment_v1(complete_contract, complete_lia_context[1])
    assert (
        result.result == "requiere_revision"
        and result.issues[0].code == "campo_residual"
    )


@pytest.mark.parametrize("change", ["purpose", "role", "evidence", "request"])
def test_motivos_contractuales_y_precedencia(
    complete_contract, complete_lia_context, change
):
    _, rat = complete_lia_context
    if change == "purpose":
        complete_contract["purpose_description"] = "Otra finalidad"
    elif change == "role":
        rat["organization_role"] = "encargado"
    elif change == "evidence":
        complete_contract["evidence"].append({"evidence_type": " "})
    elif change == "request":
        complete_contract.update(
            route="medidas_precontractuales",
            precontractual_measures="Oferta",
            request_reference="Solicitud",
            requested_by_holder={"answer": "no", "rationale": "No solicitadas"},
        )
    result = evaluate_contract_assessment_v1(complete_contract, rat)
    assert result.result == (
        "incompleto" if change == "evidence" else "requiere_revision"
    )
    complete_contract["necessity_analysis"] = " "
    result = evaluate_contract_assessment_v1(complete_contract, rat)
    assert result.result == "incompleto"
    if change != "evidence":
        assert any(i.category == "requiere_revision" for i in result.issues)


def test_contrato_ausente_ruta_desconocida_y_contexto(
    complete_contract, complete_lia_context
):
    _, rat = complete_lia_context
    result = evaluate_contract_assessment_v1(None, rat)
    assert result.result == "incompleto"
    assert {i.applicability for i in result.applicability} == {"sin_resolver"}
    assert (
        evaluate_contract_assessment_v1(complete_contract, None).issues[0].code
        == "snapshot_ausente"
    )
    with pytest.raises(ValidationError):
        evaluate_contract_assessment_v1({"route": "otra"}, None)
    with pytest.raises(ValidationError):
        evaluate_contract_assessment_v1(None, {})


def test_finalidad_canonica_y_orden_estable(complete_contract, complete_lia_context):
    _, rat = complete_lia_context
    complete_contract["purpose_description"] = " GESTIÓN de clientes "
    assert evaluate_contract_assessment_v1(complete_contract, rat).result == "completo"
    complete_contract["holder_is_party"] = {"answer": "pendiente"}
    a = evaluate_contract_assessment_v1(complete_contract, rat)
    assert [i.field for i in a.issues] == [
        "holder_is_party.answer",
        "holder_is_party.rationale",
    ]
    assert a == evaluate_contract_assessment_v1(complete_contract, rat)
