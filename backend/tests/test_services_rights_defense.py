from copy import deepcopy

import pytest
from pydantic import ValidationError

from app.services.rights_defense import (
    evaluate_rights_defense_assessment_v1 as evaluate,
)


@pytest.mark.parametrize(
    "route", ["formulacion_derecho", "ejercicio_derecho", "defensa_derecho"]
)
@pytest.mark.parametrize("forum", ["tribunal_justicia", "organo_publico"])
def test_derechos_completos_por_ruta_y_foro(
    complete_rights_defense, complete_lia_context, route, forum
):
    rights = complete_rights_defense
    rights.update(route=route, forum_type=forum)
    before = deepcopy(rights)
    result = evaluate(rights, complete_lia_context[1])
    assert result.result == "completo" and result.can_confirm
    assert result == evaluate(rights, complete_lia_context[1]) and rights == before


@pytest.mark.parametrize("stage", ["preparacion", "en_curso", "finalizado"])
def test_etapas_y_aplicabilidad(complete_rights_defense, complete_lia_context, stage):
    rights = complete_rights_defense
    rights.update(route="formulacion_derecho", proceeding_stage=stage)
    if stage == "preparacion":
        rights.pop("proceeding_reference")
        rights["preparatory_actions"] = "Preparar formulación"
    elif stage == "finalizado":
        rights["post_proceeding_necessity_analysis"] = "Necesidad posterior documentada"
    result = evaluate(rights, complete_lia_context[1])
    assert result.result == "completo"
    a = {i.field: i.applicability for i in result.applicability}
    assert a["preparatory_actions"] == (
        "aplicable" if stage == "preparacion" else "no_aplicable"
    )
    assert a["post_proceeding_necessity_analysis"] == (
        "aplicable" if stage == "finalizado" else "no_aplicable"
    )


@pytest.mark.parametrize(
    "field",
    [
        "route",
        "right_holder",
        "forum_type",
        "proceeding_stage",
        "purpose_description",
        "right_description",
        "right_basis_reference",
        "holder_connection_analysis",
        "forum_description",
        "processing_operations",
        "necessity_analysis",
        "data_minimization_analysis",
        "related_to_right",
        "necessary_for_route",
        "within_forum_scope",
        "evidence",
        "proceeding_reference",
    ],
)
def test_derechos_faltantes(complete_rights_defense, complete_lia_context, field):
    complete_rights_defense.pop(field)
    result = evaluate(complete_rights_defense, complete_lia_context[1])
    assert result.result == "incompleto"
    assert field in {i.field for i in result.issues}


@pytest.mark.parametrize(
    "field", ["related_to_right", "necessary_for_route", "within_forum_scope"]
)
@pytest.mark.parametrize(
    "answer,expected", [("no", "requiere_revision"), ("pendiente", "incompleto")]
)
def test_respuestas_derechos(
    complete_rights_defense, complete_lia_context, field, answer, expected
):
    complete_rights_defense[field]["answer"] = answer
    assert evaluate(complete_rights_defense, complete_lia_context[1]).result == expected
    complete_rights_defense[field]["rationale"] = " "
    assert (
        evaluate(complete_rights_defense, complete_lia_context[1]).result
        == "incompleto"
    )


@pytest.mark.parametrize("route", ["ejercicio_derecho", "defensa_derecho"])
def test_preparacion_en_ruta_incoherente(
    complete_rights_defense, complete_lia_context, route
):
    complete_rights_defense.update(
        route=route,
        proceeding_stage="preparacion",
        preparatory_actions="Preparar actuación",
    )
    result = evaluate(complete_rights_defense, complete_lia_context[1])
    assert result.result == "requiere_revision"
    assert "etapa_ruta_incoherente" in {i.code for i in result.issues}


@pytest.mark.parametrize(
    "change",
    ["residual", "purpose", "role", "evidence", "post_missing", "preparation_missing"],
)
def test_derechos_motivos_y_precedencia(
    complete_rights_defense, complete_lia_context, change
):
    rights = complete_rights_defense
    rat = complete_lia_context[1]
    if change == "residual":
        rights["post_proceeding_necessity_analysis"] = "Residuo"
    elif change == "purpose":
        rights["purpose_description"] = "Otra finalidad"
    elif change == "role":
        rat["organization_role"] = "encargado"
    elif change == "evidence":
        rights["evidence"].append({"evidence_type": " "})
    elif change == "post_missing":
        rights["proceeding_stage"] = "finalizado"
    elif change == "preparation_missing":
        rights.update(route="formulacion_derecho", proceeding_stage="preparacion")
    result = evaluate(rights, rat)
    assert result.result == (
        "incompleto"
        if change in ("evidence", "post_missing", "preparation_missing")
        else "requiere_revision"
    )
    rights["necessity_analysis"] = " "
    assert evaluate(rights, rat).result == "incompleto"


def test_derechos_ausencia_validacion_y_orden(
    complete_rights_defense, complete_lia_context
):
    assert evaluate(None, None).result == "incompleto"
    assert {i.applicability for i in evaluate(None, None).applicability} == {
        "sin_resolver"
    }
    with pytest.raises(ValidationError):
        evaluate({"route": "otra"}, None)
    with pytest.raises(ValidationError):
        evaluate(None, {})
    rights = complete_rights_defense
    rights["purpose_description"] = " GESTIÓN de clientes "
    assert evaluate(rights, complete_lia_context[1]).result == "completo"
    rights["related_to_right"] = {"answer": "pendiente"}
    assert [i.field for i in evaluate(rights, complete_lia_context[1]).issues] == [
        "related_to_right.answer",
        "related_to_right.rationale",
    ]
