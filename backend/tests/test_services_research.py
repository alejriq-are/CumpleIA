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
    result = evaluate(document, rat, "interes_legitimo_art13d", lia)
    assert result.result == "completo" and not result.can_confirm
    assert result.applicability[0].applicability == "no_aplicable"
    assert context == before
    assert evaluate(document, rat, "interes_legitimo_art13d", lia) == result


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
    assert (
        evaluate(document, rat, "interes_legitimo_art13d", lia).result == "incompleto"
    )


@pytest.mark.parametrize("field", ["exclusive_use", "measures_implemented"])
@pytest.mark.parametrize(
    "answer,expected", [("no", "requiere_revision"), ("pendiente", "incompleto")]
)
def test_negative_and_pending_responses(context, field, answer, expected):
    document, rat, lia = context
    document[field]["answer"] = answer
    assert evaluate(document, rat, "interes_legitimo_art13d", lia).result == expected


def test_publication_requires_anonymization(context):
    document, rat, lia = context
    document["publication_planned"]["answer"] = "si"
    assert (
        evaluate(document, rat, "interes_legitimo_art13d", lia).result == "incompleto"
    )
    document.update(
        anonymization_method="Procedimiento",
        anonymization_analysis="Analisis",
        anonymization_evidence=[dict(evidence_type="informe", reference="Registro")],
    )
    assert evaluate(document, rat, "interes_legitimo_art13d", lia).result == "completo"
    document["publication_planned"]["answer"] = "no"
    assert (
        evaluate(document, rat, "interes_legitimo_art13d", lia).result
        == "requiere_revision"
    )


@pytest.mark.parametrize("field", ["data_category_codes", "data_subject_codes"])
def test_incompatible_scope(context, field):
    document, rat, lia = context
    document[field] = ["fuera"]
    assert (
        evaluate(document, rat, "interes_legitimo_art13d", lia).result
        == "requiere_revision"
    )


@pytest.mark.parametrize("change", ["sensitive", "children", "purpose", "basis", "lia"])
def test_unsupported_context_and_dependencies(context, change):
    document, rat, lia = context
    basis = "interes_legitimo_art13d"
    if change == "sensitive":
        rat["data_categories"][0]["is_sensitive"] = True
    if change == "children":
        rat["data_subjects"][0]["includes_children"] = True
    if change == "purpose":
        document["purpose_description"] = "Otra"
    if change == "basis":
        basis = "consentimiento_art12"
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
        evaluate(model, rat, "interes_legitimo_art13d", lia)


@pytest.mark.parametrize("answer", [None, "pendiente"])
def test_unknown_publication_does_not_waive_anonymization(context, answer):
    document, rat, lia = context
    document["publication_planned"] = (
        None if answer is None else dict(answer=answer, rationale="Aun no decidido")
    )
    result = evaluate(document, rat, "interes_legitimo_art13d", lia)
    assert result.result == "incompleto"
    assert result.applicability[0].applicability == "sin_resolver"
    assert not result.can_confirm


@pytest.mark.parametrize("field", ["reference", "evidence_type"])
def test_empty_evidence_does_not_credit_quality_and_security(context, field):
    document, rat, lia = context
    document["evidence"][0][field] = "   "
    result = evaluate(document, rat, "interes_legitimo_art13d", lia)
    assert result.result == "incompleto"
    assert any(i.code == "evidencia_incompleta" for i in result.issues)


@pytest.mark.parametrize(
    "field",
    ["anonymization_method", "anonymization_analysis", "anonymization_evidence"],
)
def test_publication_requires_each_anonymization_component(context, field):
    document, rat, lia = context
    document.update(
        publication_planned=dict(answer="si", rationale="Difusion"),
        anonymization_method="Proceso",
        anonymization_analysis="Analisis",
        anonymization_evidence=[dict(evidence_type="informe", reference="Registro")],
    )
    document.pop(field)
    result = evaluate(document, rat, "interes_legitimo_art13d", lia)
    assert result.result == "incompleto"
    assert result.applicability[0].applicability == "aplicable"


@pytest.mark.parametrize(
    "collection,field",
    [
        ("data_categories", "data_category_codes"),
        ("data_subjects", "data_subject_codes"),
    ],
)
def test_partial_rat_scope_requires_review(context, collection, field):
    document, rat, lia = context
    another = deepcopy(rat[collection][0])
    another["category_code"] = "segundo"
    rat[collection].append(another)
    result = evaluate(document, rat, "interes_legitimo_art13d", lia)
    assert any(
        i.field == field and i.code == "alcance_no_cubierto" for i in result.issues
    )
    assert result.result == "requiere_revision"


@pytest.mark.parametrize("field", ["data_category_codes", "data_subject_codes"])
def test_semantic_duplicate_scope_requires_review(context, field):
    document, rat, lia = context
    original = document[field][0]
    document[field].append(" " + original.upper() + " ")
    assert (
        evaluate(document, rat, "interes_legitimo_art13d", lia).result
        == "requiere_revision"
    )


@pytest.mark.parametrize(
    "location,field",
    [
        ("special_regimes", "includes_adolescents"),
        ("special_regimes", "has_vulnerable_groups"),
        ("data_subjects", "includes_adolescents"),
        ("data_subjects", "is_vulnerable_group"),
        ("special_regimes", "has_sensitive_data"),
    ],
)
def test_scope_flags_cannot_bypass_initial_route_limits(context, location, field):
    document, rat, lia = context
    target = rat[location][0] if location == "data_subjects" else rat[location]
    target[field] = True
    result = evaluate(document, rat, "interes_legitimo_art13d", lia)
    assert result.result == "requiere_revision" and not result.can_confirm
    assert any(
        i.code in ("titulares_no_preparados", "ruta_sensible_no_preparada")
        for i in result.issues
    )


def test_empty_document_and_snapshot_do_not_authorize(context):
    _, _, lia = context
    result = evaluate(None, None, "interes_legitimo_art13d", lia)
    assert result.result == "incompleto" and not result.can_confirm
    assert any(i.code == "expediente_ausente" for i in result.issues)
    assert any(i.code == "snapshot_ausente" for i in result.issues)


@pytest.mark.parametrize(
    "field", ["exclusive_use", "measures_implemented", "publication_planned"]
)
def test_response_without_reason_is_incomplete(context, field):
    document, rat, lia = context
    document[field]["rationale"] = "   "
    result = evaluate(document, rat, "interes_legitimo_art13d", lia)
    assert result.result == "incompleto"
    assert any(i.field == field + ".rationale" for i in result.issues)


def test_abbreviated_basis_is_not_catalog_authority(context):
    document, rat, lia = context
    result = evaluate(document, rat, "interes_legitimo", lia)
    assert result.result == "requiere_revision"
    assert any(
        i.field == "legal_basis" and i.code == "base_no_admitida" for i in result.issues
    )
