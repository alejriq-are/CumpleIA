"""Matriz documental EIPD independiente de revision, frontera y autorizacion."""

from copy import deepcopy
from dataclasses import FrozenInstanceError
from datetime import date, datetime

import pytest
from pydantic import ValidationError

from app.schemas.licitud import EipdResolutionAssessmentStoredV1
from app.services.eipd_resolution import (
    EipdResolutionContextV1,
    bind_eipd_resolution_v1,
    evaluate_eipd_resolution_document_v1,
)

TODAY = date(2026, 10, 6)
TEXT_FIELDS = [
    "document_reference",
    "document_version",
    "report_reference",
    "prepared_by",
    "processing_operations",
    "processing_context",
    "technologies_description",
    "exceptions_coverage_analysis",
    "necessity_analysis",
    "proportionality_analysis",
    "minimization_analysis",
    "prior_assessment_analysis",
    "residual_risk_summary",
    "residual_risk_rationale",
    "limitations_analysis",
    "follow_up_plan",
]
RESPONSE_FIELDS = [
    "necessary_for_purpose",
    "proportionate_processing",
    "minimization_addressed",
    "performed_before_processing",
]
RISK_FIELDS = [
    "risk_id",
    "description",
    "impact_analysis",
    "initial_assessment_analysis",
    "residual_assessment_analysis",
]
MEASURE_FIELDS = [
    "measure_id",
    "description",
    "effectiveness_analysis",
    "implementation_analysis",
]


def evidence():
    return [{"evidence_type": "informe", "reference": "Informe documentado"}]


def yes():
    return {"answer": "si", "rationale": "Control documentado y revisado"}


@pytest.fixture
def complete_resolution(complete_lia_context):
    rat = deepcopy(complete_lia_context[1])
    context = {f: None for f in EipdResolutionContextV1.model_fields}
    context.update(rat_context_snapshot=rat, legal_basis="consentimiento_art12")
    document = {f: "Analisis documentado" for f in TEXT_FIELDS}
    document.update({f: yes() for f in RESPONSE_FIELDS})
    document.update(
        completed_on="2026-10-05",
        purpose_description=rat["purpose"],
        scope={
            "data_category_codes": [c["category_code"] for c in rat["data_categories"]],
            "data_subject_codes": [c["category_code"] for c in rat["data_subjects"]],
        },
        risks=[
            {
                **{f: "Analisis" for f in RISK_FIELDS},
                "risk_id": "R1",
                "evidence": evidence(),
            }
        ],
        measures=[
            {
                **{f: "Analisis" for f in MEASURE_FIELDS},
                "measure_id": "M1",
                "risk_ids": ["R1"],
                "implemented": yes(),
                "evidence": evidence(),
            }
        ],
        residual_risk_level="no_alto",
        evidence=evidence(),
        official_sources={
            "status": "identificado",
            "checked_on": "2026-10-06",
            "applicability_analysis": "Revision documental de fuentes",
            "sources": [
                {
                    "source_reference": "Fuente oficial consultada",
                    "publication_version": "v1",
                    "review_analysis": "Version y alcance documentados",
                    "applicability": "aplicable",
                }
            ],
            "evidence": evidence(),
        },
        agency_consultation={"status": "no_solicitada", "analysis": "Decision fundada"},
    )
    return document, context


def evaluate(document, context):
    return evaluate_eipd_resolution_document_v1(
        bind_eipd_resolution_v1(document, context), context, evaluated_on=TODAY
    )


def codes(result):
    return {i.code for i in result.issues}


def applicability(result):
    return {i.field: i.applicability for i in result.applicability}


def test_complete_is_preparation_only_and_immutable(complete_resolution):
    doc, ctx = complete_resolution
    before = deepcopy((doc, ctx))
    result = evaluate(doc, ctx)
    assert result.result == "completo" and result.context_current
    assert result.is_document_prepared and not result.issues
    assert not hasattr(result, "can_confirm")
    assert (doc, ctx) == before
    with pytest.raises(FrozenInstanceError):
        result.result = "completo"


@pytest.mark.parametrize("field", TEXT_FIELDS + ["purpose_description"])
@pytest.mark.parametrize("missing", [None, " "])
def test_each_required_text_missing(complete_resolution, field, missing):
    doc, ctx = complete_resolution
    doc[field] = missing
    result = evaluate(doc, ctx)
    assert result.result == "incompleto" and not result.is_document_prepared
    assert any(
        i.field == field and i.code == "campo_obligatorio" for i in result.issues
    )


@pytest.mark.parametrize("field", RESPONSE_FIELDS)
@pytest.mark.parametrize(
    "value,expected,code",
    [
        (None, "incompleto", "respuesta_ausente"),
        (
            {"answer": "pendiente", "rationale": "Pendiente"},
            "incompleto",
            "respuesta_pendiente",
        ),
        ({"answer": "si"}, "incompleto", "fundamento_ausente"),
        (
            {"answer": "no", "rationale": "No cumple"},
            "requiere_revision",
            "respuesta_revision",
        ),
    ],
)
def test_response_matrix(complete_resolution, field, value, expected, code):
    doc, ctx = complete_resolution
    doc[field] = value
    result = evaluate(doc, ctx)
    assert result.result == expected and code in codes(result)


@pytest.mark.parametrize("field", RISK_FIELDS)
def test_each_risk_field_required(complete_resolution, field):
    doc, ctx = complete_resolution
    doc["risks"][0][field] = None
    result = evaluate(doc, ctx)
    assert result.result == (
        "requiere_revision" if field == "risk_id" else "incompleto"
    )
    assert any(i.field == "risks.0." + field for i in result.issues)


@pytest.mark.parametrize("field", MEASURE_FIELDS)
def test_each_measure_field_required(complete_resolution, field):
    doc, ctx = complete_resolution
    doc["measures"][0][field] = " "
    result = evaluate(doc, ctx)
    assert result.result == "incompleto"
    assert any(i.field == "measures.0." + field for i in result.issues)


@pytest.mark.parametrize("root", ["evidence", "risk", "measure", "official"])
@pytest.mark.parametrize(
    "value",
    [
        [],
        [{"evidence_type": "registro"}],
        [{"evidence_type": " ", "reference": "REF"}],
        [{"evidence_type": "registro", "reference": " "}],
    ],
)
def test_evidence_required_and_all_items_checked(complete_resolution, root, value):
    doc, ctx = complete_resolution
    target = (
        doc
        if root == "evidence"
        else (
            doc["risks"][0]
            if root == "risk"
            else doc["measures"][0] if root == "measure" else doc["official_sources"]
        )
    )
    target["evidence"] = value
    result = evaluate(doc, ctx)
    assert result.result == "incompleto" and not result.is_document_prepared
    assert any(i.code.startswith("evidencia_") for i in result.issues)


@pytest.mark.parametrize(
    "mode,code,expected",
    [
        ("no_risks", "riesgos_ausentes", "requiere_revision"),
        ("no_measures", "medidas_ausentes", "incompleto"),
        ("risk_duplicate", "identificador_duplicado", "requiere_revision"),
        ("measure_duplicate", "identificador_duplicado", "requiere_revision"),
        ("unknown", "referencia_riesgo_desconocida", "requiere_revision"),
        ("duplicate_ref", "referencia_riesgo_duplicada", "requiere_revision"),
        ("empty_ref", "referencia_riesgo_vacia", "incompleto"),
        ("no_ref", "referencias_riesgo_ausentes", "incompleto"),
        ("uncovered", "riesgo_sin_medida", "incompleto"),
        ("not_implemented", "respuesta_revision", "requiere_revision"),
        ("pending_measure", "respuesta_pendiente", "incompleto"),
    ],
)
def test_risks_measures_cross_references(complete_resolution, mode, code, expected):
    doc, ctx = complete_resolution
    if mode == "no_risks":
        doc["risks"] = []
    elif mode == "no_measures":
        doc["measures"] = []
    elif mode == "risk_duplicate":
        extra = deepcopy(doc["risks"][0])
        extra["risk_id"] = " r1 "
        doc["risks"].append(extra)
    elif mode == "measure_duplicate":
        extra = deepcopy(doc["measures"][0])
        extra["measure_id"] = " m1 "
        doc["measures"].append(extra)
    elif mode == "uncovered":
        extra = deepcopy(doc["risks"][0])
        extra["risk_id"] = "R2"
        doc["risks"].append(extra)
    elif mode in ("unknown", "duplicate_ref", "empty_ref", "no_ref"):
        doc["measures"][0]["risk_ids"] = {
            "unknown": ["R99"],
            "duplicate_ref": ["R1", " r1 "],
            "empty_ref": [" "],
            "no_ref": [],
        }[mode]
    else:
        doc["measures"][0]["implemented"] = {
            "answer": "no" if mode == "not_implemented" else "pendiente",
            "rationale": "Plan pendiente",
        }
    result = evaluate(doc, ctx)
    assert result.result == expected and code in codes(result)


def test_references_and_purpose_normalized_unicode(complete_resolution):
    doc, ctx = complete_resolution
    doc["purpose_description"] = "  " + doc["purpose_description"].upper() + "  "
    doc["risks"][0]["risk_id"] = "RÉ"
    doc["measures"][0]["risk_ids"] = [" re\u0301 "]
    assert evaluate(doc, ctx).result == "completo"


@pytest.mark.parametrize(
    "level,expected",
    [
        (None, "incompleto"),
        ("sin_resolver", "incompleto"),
        ("alto", "requiere_revision"),
    ],
)
def test_residual_risk_is_declared_not_scored(complete_resolution, level, expected):
    doc, ctx = complete_resolution
    doc["residual_risk_level"] = level
    assert evaluate(doc, ctx).result == expected


@pytest.mark.parametrize("field", ["completed_on", "checked_on"])
@pytest.mark.parametrize(
    "value,expected,code",
    [
        (None, "incompleto", "fecha_ausente"),
        ("2026-10-07", "requiere_revision", "fecha_futura"),
    ],
)
def test_required_dates(complete_resolution, field, value, expected, code):
    doc, ctx = complete_resolution
    target = doc if field == "completed_on" else doc["official_sources"]
    target[field] = value
    result = evaluate(doc, ctx)
    assert result.result == expected and code in codes(result)


@pytest.mark.parametrize(
    "mode,expected",
    [
        ("missing", "incompleto"),
        ("pending", "incompleto"),
        ("none_status", "incompleto"),
        ("empty_sources", "incompleto"),
        ("no_version", "incompleto"),
        ("no_analysis", "incompleto"),
        ("source_no_reference", "incompleto"),
        ("source_no_analysis", "incompleto"),
        ("source_pending", "incompleto"),
        ("source_none", "incompleto"),
        ("contradiction", "requiere_revision"),
        ("no_identified", "completo"),
        ("identified_not_applicable", "completo"),
    ],
)
def test_sources_conditions(complete_resolution, mode, expected):
    doc, ctx = complete_resolution
    sources = doc["official_sources"]
    source = sources["sources"][0]
    if mode == "missing":
        doc["official_sources"] = None
    elif mode == "pending":
        sources["status"] = "pendiente"
    elif mode == "none_status":
        sources["status"] = None
    elif mode == "empty_sources":
        sources["sources"] = []
    elif mode == "no_version":
        source["publication_version"] = None
    elif mode == "no_analysis":
        sources["applicability_analysis"] = " "
    elif mode == "source_no_reference":
        source["source_reference"] = " "
    elif mode == "source_no_analysis":
        source["review_analysis"] = None
    elif mode == "source_pending":
        source["applicability"] = "pendiente"
    elif mode == "source_none":
        source["applicability"] = None
    elif mode == "contradiction":
        sources["status"] = "no_identificado"
    elif mode == "no_identified":
        sources["status"] = "no_identificado"
        source.update(applicability="no_aplicable", publication_version=None)
    elif mode == "identified_not_applicable":
        source["applicability"] = "no_aplicable"
    result = evaluate(doc, ctx)
    assert result.result == expected
    if mode == "no_identified":
        assert (
            applicability(result)["official_sources.sources.0.publication_version"]
            == "no_aplicable"
        )
        assert not hasattr(result, "official_sources_verified")


def concluded_consultation():
    return dict(
        status="concluida",
        analysis="Consulta analizada",
        consultation_reference="Consulta1",
        response_reference="Respuesta1",
        recommendations_analysis="Antecedentes evaluados",
        reassessment_analysis="Evaluacion actualizada",
        recommendations_addressed=yes(),
        evidence=evidence(),
    )


@pytest.mark.parametrize(
    "status,expected",
    [
        (None, "incompleto"),
        ("en_curso", "requiere_revision"),
        ("concluida", "completo"),
        ("no_solicitada", "completo"),
    ],
)
def test_consultation_states(complete_resolution, status, expected):
    doc, ctx = complete_resolution
    doc["agency_consultation"] = (
        concluded_consultation()
        if status == "concluida"
        else {"status": status, "analysis": "Decision fundada"}
    )
    if status == "en_curso":
        doc["agency_consultation"].update(
            consultation_reference="Consulta1", evidence=evidence()
        )
    result = evaluate(doc, ctx)
    assert result.result == expected
    if status is None:
        assert (
            applicability(result)["agency_consultation.response_reference"]
            == "sin_resolver"
        )


@pytest.mark.parametrize(
    "field",
    [
        "analysis",
        "consultation_reference",
        "response_reference",
        "recommendations_analysis",
        "reassessment_analysis",
        "recommendations_addressed",
        "evidence",
    ],
)
def test_each_concluded_consultation_field_required(complete_resolution, field):
    doc, ctx = complete_resolution
    doc["agency_consultation"] = concluded_consultation()
    doc["agency_consultation"][field] = [] if field == "evidence" else None
    assert evaluate(doc, ctx).result == "incompleto"


@pytest.mark.parametrize(
    "field",
    [
        "consultation_reference",
        "response_reference",
        "recommendations_analysis",
        "reassessment_analysis",
        "recommendations_addressed",
    ],
)
def test_unsolicited_consultation_residual_fields(complete_resolution, field):
    doc, ctx = complete_resolution
    doc["agency_consultation"][field] = (
        yes() if field == "recommendations_addressed" else "Residual"
    )
    result = evaluate(doc, ctx)
    assert result.result == "requiere_revision" and "campo_residual" in codes(result)
    assert applicability(result)["agency_consultation." + field] == "no_aplicable"


@pytest.mark.parametrize(
    "answer,expected", [("no", "requiere_revision"), ("pendiente", "incompleto")]
)
def test_recommendations_not_automatic_authorization(
    complete_resolution, answer, expected
):
    doc, ctx = complete_resolution
    doc["agency_consultation"] = concluded_consultation()
    doc["agency_consultation"]["recommendations_addressed"]["answer"] = answer
    assert evaluate(doc, ctx).result == expected


@pytest.mark.parametrize("field", ["data_category_codes", "data_subject_codes"])
@pytest.mark.parametrize(
    "mode,expected",
    [
        ("empty", "incompleto"),
        ("unknown", "requiere_revision"),
        ("duplicate", "requiere_revision"),
    ],
)
def test_scope_exact_rat_and_semantic_duplicates(
    complete_resolution, field, mode, expected
):
    doc, ctx = complete_resolution
    initial = doc["scope"][field][0]
    doc["scope"][field] = (
        []
        if mode == "empty"
        else (
            ["unknown"] if mode == "unknown" else [initial, " " + initial.upper() + " "]
        )
    )
    assert evaluate(doc, ctx).result == expected


def test_scope_includes_non_sensitive_categories_and_exception_subset(
    complete_resolution,
):
    doc, ctx = complete_resolution
    rat = ctx["rat_context_snapshot"]
    extra = deepcopy(rat["data_categories"][0])
    extra.update(category_code="otro", is_sensitive=False)
    rat["data_categories"].append(extra)
    doc["scope"]["data_category_codes"].append("otro")
    ctx["sensitive_rights_exception_assessment"] = {
        "scope": {
            "data_category_codes": [doc["scope"]["data_category_codes"][0]],
            "data_subject_codes": doc["scope"]["data_subject_codes"],
        }
    }
    assert evaluate(doc, ctx).result == "completo"
    doc["scope"]["data_category_codes"].remove("otro")
    assert evaluate(doc, ctx).result == "requiere_revision"


@pytest.mark.parametrize(
    "kind",
    ["sensitive_rights_exception_assessment", "biometric_rights_exception_assessment"],
)
@pytest.mark.parametrize(
    "mode,expected", [("missing", "incompleto"), ("outside", "requiere_revision")]
)
def test_exception_scope_containment(complete_resolution, kind, mode, expected):
    doc, ctx = complete_resolution
    ctx[kind] = (
        {}
        if mode == "missing"
        else {
            "scope": {
                "data_category_codes": ["unknown"],
                "data_subject_codes": doc["scope"]["data_subject_codes"],
            }
        }
    )
    assert evaluate(doc, ctx).result == expected


def test_missing_document_context_and_binding(complete_resolution):
    doc, ctx = complete_resolution
    result = evaluate_eipd_resolution_document_v1(None, None, evaluated_on=TODAY)
    assert result.result == "incompleto" and not result.context_current
    assert {"expediente_ausente", "contexto_ausente", "asociacion_ausente"}.issubset(
        codes(result)
    )
    result = evaluate_eipd_resolution_document_v1(
        EipdResolutionAssessmentStoredV1.model_validate(doc), ctx, evaluated_on=TODAY
    )
    assert result.result == "incompleto" and "asociacion_ausente" in codes(result)


@pytest.mark.parametrize(
    "field", ["legal_basis", "consent_assessment", "rat_context_snapshot"]
)
def test_binding_stale_reads_do_not_reassociate(complete_resolution, field):
    doc, ctx = complete_resolution
    bound = bind_eipd_resolution_v1(doc, ctx)
    original = bound.model_dump(mode="json")
    if field == "legal_basis":
        ctx[field] = "defensa_derechos_art13e"
    elif field == "consent_assessment":
        ctx[field] = {"notes": "Cambio"}
    else:
        ctx[field]["retention"]["retention_rule"] = "Cambio"
    result = evaluate_eipd_resolution_document_v1(bound, ctx, evaluated_on=TODAY)
    assert result.result == "requiere_revision" and not result.context_current
    assert "asociacion_obsoleta" in codes(result)
    assert bound.model_dump(mode="json") == original


def test_all_issues_retained_revision_precedes_missing(complete_resolution):
    doc, ctx = complete_resolution
    doc.update(
        document_reference=None,
        residual_risk_level="alto",
        performed_before_processing={"answer": "no"},
    )
    result = evaluate(doc, ctx)
    assert result.result == "requiere_revision"
    assert {
        "campo_obligatorio",
        "riesgo_residual_alto",
        "respuesta_revision",
        "fundamento_ausente",
    }.issubset(codes(result))


def test_date_and_evidence_do_not_infer_prior_assessment(complete_resolution):
    doc, ctx = complete_resolution
    doc["performed_before_processing"] = None
    doc["completed_on"] = "1900-01-01"
    doc["evidence"][0]["obtained_on"] = "1900-01-01"
    assert "respuesta_ausente" in codes(evaluate(doc, ctx))
    doc["performed_before_processing"] = yes()
    doc["evidence"][0]["obtained_on"] = "2099-01-01"
    assert evaluate(doc, ctx).result == "completo"


def test_deterministic_models_json_no_mutation(complete_resolution):
    doc, ctx = complete_resolution
    bound = bind_eipd_resolution_v1(doc, ctx)
    before = deepcopy((bound.model_dump(mode="json"), ctx))
    first = evaluate_eipd_resolution_document_v1(
        bound, EipdResolutionContextV1.model_validate(ctx), evaluated_on=TODAY
    )
    second = evaluate_eipd_resolution_document_v1(
        bound.model_dump(mode="json"), ctx, evaluated_on=TODAY
    )
    assert first == second and (bound.model_dump(mode="json"), ctx) == before


@pytest.mark.parametrize("value", [None, "2026-10-06", datetime(2026, 10, 6)])
def test_evaluation_date_explicit_type(complete_resolution, value):
    doc, ctx = complete_resolution
    with pytest.raises(ValueError):
        evaluate_eipd_resolution_document_v1(
            bind_eipd_resolution_v1(doc, ctx), ctx, evaluated_on=value
        )


def test_mutated_models_and_unsupported_binding_rejected(complete_resolution):
    doc, ctx = complete_resolution
    bound = bind_eipd_resolution_v1(doc, ctx)
    bound.residual_risk_level = "invalid"
    with pytest.raises(ValidationError):
        evaluate_eipd_resolution_document_v1(bound, ctx, evaluated_on=TODAY)
    bound = bind_eipd_resolution_v1(doc, ctx)
    bound.context_binding.binding_version = 2
    with pytest.raises(ValidationError):
        evaluate_eipd_resolution_document_v1(bound, ctx, evaluated_on=TODAY)


@pytest.mark.parametrize(
    "field",
    [
        "response_reference",
        "recommendations_analysis",
        "reassessment_analysis",
        "recommendations_addressed",
    ],
)
def test_ongoing_consultation_residual_conclusion_fields(complete_resolution, field):
    doc, ctx = complete_resolution
    doc["agency_consultation"] = {
        "status": "en_curso",
        "analysis": "En evaluacion",
        "consultation_reference": "CONS1",
        "evidence": evidence(),
        field: (
            yes()
            if field == "recommendations_addressed"
            else "Antecedente de conclusion"
        ),
    }
    result = evaluate(doc, ctx)
    assert result.result == "requiere_revision"
    assert {"consulta_en_curso", "campo_residual"}.issubset(codes(result))


@pytest.mark.parametrize("field", ["consultation_reference", "evidence"])
def test_ongoing_consultation_missing_requirements_preserve_both_categories(
    complete_resolution, field
):
    doc, ctx = complete_resolution
    doc["agency_consultation"] = {
        "status": "en_curso",
        "analysis": "En evaluacion",
        "consultation_reference": "CONS1",
        "evidence": evidence(),
    }
    doc["agency_consultation"][field] = [] if field == "evidence" else None
    result = evaluate(doc, ctx)
    assert result.result == "requiere_revision"
    assert {i.category for i in result.issues} == {"requiere_revision", "incompleto"}


def test_missing_scope_and_consultation_objects_report_all_requirements(
    complete_resolution,
):
    doc, ctx = complete_resolution
    doc.update(scope=None, agency_consultation=None)
    result = evaluate(doc, ctx)
    assert result.result == "incompleto"
    assert {
        "alcance_ausente",
        "alcance_vacio",
        "consulta_ausente",
        "estado_consulta_ausente",
    }.issubset(codes(result))


def test_missing_context_never_marks_bound_document_prepared(complete_resolution):
    doc, ctx = complete_resolution
    bound = bind_eipd_resolution_v1(doc, ctx)
    result = evaluate_eipd_resolution_document_v1(bound, None, evaluated_on=TODAY)
    assert result.result == "incompleto" and not result.context_current
    assert not result.is_document_prepared
    assert applicability(result)["context_binding.context_hash"] == "sin_resolver"


def test_purpose_mismatch_requires_revision(complete_resolution):
    doc, ctx = complete_resolution
    doc["purpose_description"] = "Otra finalidad"
    result = evaluate(doc, ctx)
    assert result.result == "requiere_revision" and "finalidad_distinta" in codes(
        result
    )


def test_numbered_issues_ordered_and_deduplicated(complete_resolution):
    doc, ctx = complete_resolution
    doc["risks"] = [{"risk_id": f"R{i}"} for i in range(12)]
    first = evaluate(doc, ctx)
    second = evaluate(doc, ctx)
    assert first == second
    ids = [i.field for i in first.issues if i.code == "riesgo_sin_medida"]
    assert ids == [f"risks.{i}.risk_id" for i in range(12) if i != 1]
    assert len(set(first.issues)) == len(first.issues)
    assert len(set(first.applicability)) == len(first.applicability)


def test_each_evidence_item_checked_not_only_first(complete_resolution):
    doc, ctx = complete_resolution
    doc["evidence"].append({"evidence_type": "registro", "reference": None})
    result = evaluate(doc, ctx)
    assert any(
        i.field == "evidence.1.reference" and i.code == "evidencia_incompleta"
        for i in result.issues
    )
