from copy import deepcopy

import pytest
from pydantic import ValidationError

from app.schemas.licitud import LegalObligationAssessmentV1, RatContextSnapshotV1
from app.services.legal_obligation import (
    evaluate_legal_obligation_assessment_v1 as evaluate,
)


@pytest.mark.parametrize(
    "route", ["cumplimiento_obligacion_legal", "tratamiento_dispuesto_por_ley"]
)
def test_normativa_completa_pura_por_ruta(
    complete_legal_obligation, complete_lia_context, route
):
    legal = complete_legal_obligation
    legal["route"] = route
    if route == "tratamiento_dispuesto_por_ley":
        legal["processing_required_by_law"] = legal.pop(
            "obligation_applies_to_controller"
        )
    original = deepcopy(legal)
    result = evaluate(legal, complete_lia_context[1])
    assert result.result == "completo" and result.can_confirm
    assert result == evaluate(
        LegalObligationAssessmentV1.model_validate(legal),
        RatContextSnapshotV1.model_validate(complete_lia_context[1]),
    )
    assert legal == original
    assert [i.applicability for i in result.applicability] == (
        ["aplicable", "no_aplicable"]
        if route == "cumplimiento_obligacion_legal"
        else ["no_aplicable", "aplicable"]
    )


@pytest.mark.parametrize(
    "field",
    [
        "route",
        "purpose_description",
        "normative_requirement_description",
        "processing_operations",
        "applicability_analysis",
        "necessity_analysis",
        "data_minimization_analysis",
        "normative_references",
        "normative_basis_reviewed",
        "normative_basis_in_force",
        "processing_within_legal_scope",
        "obligation_applies_to_controller",
        "evidence",
    ],
)
def test_normativa_faltantes(complete_legal_obligation, complete_lia_context, field):
    complete_legal_obligation.pop(field)
    result = evaluate(complete_legal_obligation, complete_lia_context[1])
    assert result.result == "incompleto"
    assert field in {i.field for i in result.issues}


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
def test_referencia_incompleta_no_oculta_por_otra(
    complete_legal_obligation, complete_lia_context, field
):
    extra = deepcopy(complete_legal_obligation["normative_references"][0])
    extra[field] = None
    complete_legal_obligation["normative_references"].append(extra)
    result = evaluate(complete_legal_obligation, complete_lia_context[1])
    assert result.result == "incompleto"
    assert result.issues[0].field == "normative_references.1." + field


@pytest.mark.parametrize(
    "field",
    [
        "normative_basis_reviewed",
        "normative_basis_in_force",
        "processing_within_legal_scope",
        "obligation_applies_to_controller",
    ],
)
@pytest.mark.parametrize(
    "answer,expected", [("no", "requiere_revision"), ("pendiente", "incompleto")]
)
def test_respuestas_normativas(
    complete_legal_obligation, complete_lia_context, field, answer, expected
):
    complete_legal_obligation[field]["answer"] = answer
    result = evaluate(complete_legal_obligation, complete_lia_context[1])
    assert result.result == expected
    complete_legal_obligation[field]["rationale"] = " "
    result = evaluate(complete_legal_obligation, complete_lia_context[1])
    assert result.result == "incompleto"
    assert "fundamento_ausente" in {i.code for i in result.issues}


@pytest.mark.parametrize("change", ["residual", "purpose", "role", "evidence"])
def test_normativa_revision_y_precedencia(
    complete_legal_obligation, complete_lia_context, change
):
    legal = complete_legal_obligation
    rat = complete_lia_context[1]
    if change == "residual":
        legal["processing_required_by_law"] = {"answer": "pendiente"}
    elif change == "purpose":
        legal["purpose_description"] = "Otra finalidad"
    elif change == "role":
        rat["organization_role"] = "encargado"
    elif change == "evidence":
        legal["evidence"].append({"evidence_type": " "})
    result = evaluate(legal, rat)
    assert result.result == (
        "incompleto" if change == "evidence" else "requiere_revision"
    )
    legal["necessity_analysis"] = " "
    assert evaluate(legal, rat).result == "incompleto"


def test_normativa_ausente_y_contratos_invalidos(
    complete_legal_obligation, complete_lia_context
):
    result = evaluate(None, None)
    assert result.result == "incompleto"
    assert result.issues[0].code == "snapshot_ausente"
    assert {i.applicability for i in result.applicability} == {"sin_resolver"}
    with pytest.raises(ValidationError):
        evaluate({"route": "otra"}, None)
    with pytest.raises(ValidationError):
        evaluate(None, {})
    complete_legal_obligation["normative_references"][0][
        "official_source_url"
    ] = "file:///local"
    with pytest.raises(ValidationError):
        evaluate(complete_legal_obligation, None)


def test_normativa_canonizacion_y_orden(
    complete_legal_obligation, complete_lia_context
):
    legal = complete_legal_obligation
    legal["purpose_description"] = " GESTIÓN de CLIENTES "
    assert evaluate(legal, complete_lia_context[1]).result == "completo"
    legal["normative_basis_reviewed"] = {"answer": "pendiente"}
    result = evaluate(legal, complete_lia_context[1])
    assert [i.field for i in result.issues] == [
        "normative_basis_reviewed.answer",
        "normative_basis_reviewed.rationale",
    ]
    assert result == evaluate(legal, complete_lia_context[1])
