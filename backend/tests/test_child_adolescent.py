"""Documentos ficticios: completitud no autoriza y nombres no prueban edad."""

from copy import deepcopy

import pytest

from app.services.child_adolescent import evaluate_child_adolescent_v1 as evaluate
from tests import test_services_research as research

context = research.context


@pytest.fixture
def material(context):
    _, rat, _ = deepcopy(context)
    rat["data_subjects"][0]["includes_children"] = True
    rat["special_regimes"]["includes_children"] = True
    doc = dict(
        declared_groups=["ninos_ninas"],
        data_category_codes=["id"],
        data_subject_codes=["clientes"],
        proposed_authorization_route="consentimiento",
        declared_consent_giver="padre_madre",
        evidence=[dict(evidence_type="PRUEBA", reference="PRUEBA: evidencia ficticia")],
    )
    for field in (
        "age_scope_analysis",
        "best_interests_analysis",
        "progressive_autonomy_analysis",
        "authorization_reference",
        "authorization_analysis",
    ):
        doc[field] = "PRUEBA: analisis ficticio"
    return doc, rat


def test_complete_document_is_deterministic_without_authority(material):
    before = deepcopy(material)
    result = evaluate(*material)
    assert result.result == "completo"
    assert result.issues == ()
    assert not result.can_confirm and not result.authorizes_action
    assert evaluate(*material) == result
    assert material == before


@pytest.mark.parametrize(
    "field",
    [
        "age_scope_analysis",
        "best_interests_analysis",
        "progressive_autonomy_analysis",
        "authorization_reference",
        "authorization_analysis",
    ],
)
def test_whitespace_is_not_documentary_analysis(material, field):
    doc, rat = material
    doc[field] = " "
    assert evaluate(doc, rat).result == "incompleto"


@pytest.mark.parametrize(
    "change", ["other_code", "other_group", "mixed", "legal_route", "self_child"]
)
def test_incoherent_or_pending_routes_require_review(material, change):
    doc, rat = material
    if change == "other_code":
        doc["data_subject_codes"] = ["ajeno"]
    elif change == "other_group":
        doc["declared_groups"] = ["adolescentes"]
    elif change == "mixed":
        rat["data_subjects"][0]["includes_adolescents"] = True
        doc["declared_groups"].append("adolescentes")
    elif change == "legal_route":
        doc["proposed_authorization_route"] = "autorizacion_legal_expresa"
    else:
        doc["declared_consent_giver"] = "titular"
    assert evaluate(doc, rat).result == "requiere_revision"


def test_sensitive_and_adolescent_flags_do_not_prove_under16(material):
    doc, rat = material
    rat["data_subjects"][0].update(includes_children=False, includes_adolescents=True)
    rat["data_categories"][0]["is_sensitive"] = True
    rat["special_regimes"].update(
        includes_children=False, includes_adolescents=True, has_sensitive_data=True
    )
    doc["declared_groups"] = ["adolescentes"]
    result = evaluate(doc, rat)
    assert any(i.code == "cruce_sensible_edad_pendiente" for i in result.issues)
    assert doc.get("sensitive_under16") is None
    doc["sensitive_under16"] = "no"
    assert evaluate(doc, rat).result == "completo"


def test_missing_context_or_document_does_not_approve(material):
    doc, rat = material
    assert evaluate(None, rat).result == "incompleto"
    assert evaluate(doc, None).result == "incompleto"
    assert evaluate(None, None).result == "incompleto"


def test_no_child_flags_no_document_is_not_applicable(context):
    _, rat, _ = context
    assert evaluate(None, rat).result == "no_aplicable"


def test_incoherent_rat_summary_does_not_hide_child_scope(material):
    _, rat = material
    rat["special_regimes"]["includes_children"] = False
    result = evaluate(None, rat)
    assert result.result == "requiere_revision"
    assert any(i.code == "resumen_rat_incoherente" for i in result.issues)


@pytest.mark.parametrize(
    "change",
    [
        "sensitive_without_age",
        "under16_subgroup_pending",
        "empty_evidence",
        "residual_document",
    ],
)
def test_documentary_cross_checks_do_not_infer_authority(material, change):
    doc, rat = material
    if change == "sensitive_without_age":
        doc["sensitive_under16"] = "si"
    elif change == "under16_subgroup_pending":
        doc["declared_groups"] = ["adolescentes_sensibles_menores_16"]
        doc["sensitive_under16"] = "pendiente"
    elif change == "empty_evidence":
        doc["evidence"] = [{"evidence_type": "PRUEBA", "reference": " "}]
    else:
        rat["data_subjects"][0]["includes_children"] = False
        rat["special_regimes"]["includes_children"] = False
    result = evaluate(doc, rat)
    assert result.result in ("incompleto", "requiere_revision")
    assert not result.can_confirm and not result.authorizes_action
