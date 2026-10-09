from copy import deepcopy

import pytest
from pydantic import ValidationError

from app.schemas.research import ResearchAssessmentV1
from app.services.research import evaluate_research_assessment_v1 as evaluate


@pytest.fixture
def context(complete_lia_context):
    lia, rat = complete_lia_context
    document = dict(
        purpose_type="cientifico",
        purpose_description=rat["purpose"],
        public_interest_analysis="Analisis",
        exclusive_use=dict(answer="si", rationale="Control"),
        exclusivity_controls_analysis="Controles",
        quality_measures_analysis="Medidas",
        security_measures_analysis="Medidas",
        measures_implemented=dict(answer="si", rationale="Evidencia"),
        evidence=[dict(evidence_type="control", reference="Registro")],
        publication_planned=dict(answer="no", rationale="No se publica"),
        retention_analysis="Criterio",
        data_category_codes=["id"],
        data_subject_codes=["clientes"],
    )
    return document, deepcopy(rat), deepcopy(lia)


def test_complete_document_never_enables_confirmation(context):
    document, rat, lia = context
    before = deepcopy(context)
    result = evaluate(document, rat, "interes_legitimo", lia)
    assert result.result == "completo" and not result.can_confirm
    assert result.applicability[0].applicability == "no_aplicable"
    assert context == before
    assert evaluate(document, rat, "interes_legitimo", lia) == result


@pytest.mark.parametrize(
    "field",
    [
        "purpose_type",
        "purpose_description",
        "public_interest_analysis",
        "quality_measures_analysis",
        "security_measures_analysis",
        "retention_analysis",
        "evidence",
        "exclusive_use",
        "measures_implemented",
        "publication_planned",
    ],
)
def test_missing_required_material(context, field):
    document, rat, lia = context
    document.pop(field)
    assert evaluate(document, rat, "interes_legitimo", lia).result == "incompleto"


@pytest.mark.parametrize("field", ["exclusive_use", "measures_implemented"])
@pytest.mark.parametrize(
    "answer,expected", [("no", "requiere_revision"), ("pendiente", "incompleto")]
)
def test_negative_and_pending_responses(context, field, answer, expected):
    document, rat, lia = context
    document[field]["answer"] = answer
    assert evaluate(document, rat, "interes_legitimo", lia).result == expected


def test_publication_requires_anonymization(context):
    document, rat, lia = context
    document["publication_planned"]["answer"] = "si"
    assert evaluate(document, rat, "interes_legitimo", lia).result == "incompleto"
    document.update(
        anonymization_method="Procedimiento",
        anonymization_analysis="Analisis",
        anonymization_evidence=[dict(evidence_type="informe", reference="Registro")],
    )
    assert evaluate(document, rat, "interes_legitimo", lia).result == "completo"
    document["publication_planned"]["answer"] = "no"
    assert (
        evaluate(document, rat, "interes_legitimo", lia).result == "requiere_revision"
    )


@pytest.mark.parametrize("field", ["data_category_codes", "data_subject_codes"])
def test_incompatible_scope(context, field):
    document, rat, lia = context
    document[field] = ["fuera"]
    assert (
        evaluate(document, rat, "interes_legitimo", lia).result == "requiere_revision"
    )


@pytest.mark.parametrize("change", ["sensitive", "children", "purpose", "basis", "lia"])
def test_unsupported_context_and_dependencies(context, change):
    document, rat, lia = context
    basis = "interes_legitimo"
    if change == "sensitive":
        rat["data_categories"][0]["is_sensitive"] = True
    if change == "children":
        rat["data_subjects"][0]["includes_children"] = True
    if change == "purpose":
        document["purpose_description"] = "Otra"
    if change == "basis":
        basis = "consentimiento"
    if change == "lia":
        lia = None
    assert evaluate(document, rat, basis, lia).result != "completo"


def test_closed_schema_and_revalidation(context):
    document, rat, lia = context
    with pytest.raises(ValidationError):
        ResearchAssessmentV1.model_validate(document | {"authorized": True})
    model = ResearchAssessmentV1.model_validate(document)
    model.publication_planned.answer = "invalid"
    with pytest.raises(ValidationError):
        evaluate(model, rat, "interes_legitimo", lia)
