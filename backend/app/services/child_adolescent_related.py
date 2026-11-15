"""Coherencia entre declaraciones documentales; no valida parentesco o facultades."""

from app.schemas.child_adolescent import ChildAdolescentAssessmentV1
from app.services.child_adolescent import ChildAdolescentIssueV1
from app.services.child_adolescent_binding import ChildAdolescentContextV1
from app.services.research_binding import validated


def evaluate_child_adolescent_related_v1(document, context):
    doc = validated(ChildAdolescentAssessmentV1, document)
    ctx = validated(ChildAdolescentContextV1, context)
    issues = []

    def issue(field, code, category="incompleto"):
        issues.append(ChildAdolescentIssueV1(field, code, category))

    if doc.proposed_authorization_route == "consentimiento":
        consent = ctx.consent_assessment
        if consent is None or consent.given_by is None:
            issue("consent_assessment.given_by", "consentimiento_relacionado_pendiente")
        elif doc.declared_consent_giver not in ("titular", "representante_legal"):
            issue(
                "declared_consent_giver",
                "relacion_otorgante_no_comparable",
                "requiere_revision",
            )
        elif doc.declared_consent_giver != consent.given_by:
            issue(
                "consent_assessment.given_by",
                "otorgante_documental_incoherente",
                "requiere_revision",
            )
        categories = {
            c.category_code: c for c in ctx.rat_context_snapshot.data_categories
        }
        if (
            any(
                categories[c].is_sensitive
                for c in doc.data_category_codes
                if c in categories
            )
            and ctx.sensitive_consent_assessment is None
        ):
            issue(
                "sensitive_consent_assessment",
                "consentimiento_sensible_relacionado_pendiente",
            )
    special = ctx.special_conditions_document
    if special is None:
        issue("special_conditions_document", "declaraciones_especiales_pendientes")
        return tuple(sorted(set(issues), key=lambda i: (i.field, i.code)))
    categories = {c.category_code for c in ctx.rat_context_snapshot.data_categories}
    subjects = {c.category_code for c in ctx.rat_context_snapshot.data_subjects}

    def same_scope(value):
        return (set(value.data_category_codes) or categories) == set(
            doc.data_category_codes
        ) and (set(value.data_subject_codes) or subjects) == set(doc.data_subject_codes)

    declarations = {d.question_id: d for d in special.declarations}
    expected = {
        "ninos_ninas": "si" if "ninos_ninas" in doc.declared_groups else "no",
        "adolescentes": (
            "si"
            if any(
                g in doc.declared_groups
                for g in ("adolescentes", "adolescentes_sensibles_menores_16")
            )
            else "no"
        ),
        "datos_sensibles_adolescentes_menores_16": doc.sensitive_under16,
    }
    selected_sensitive = any(
        c.is_sensitive
        for c in ctx.rat_context_snapshot.data_categories
        if c.category_code in doc.data_category_codes
    )
    if expected["adolescentes"] == "no" or not selected_sensitive:
        expected["datos_sensibles_adolescentes_menores_16"] = "no"
    for question, answer in expected.items():
        field = "special_conditions_document.declarations." + question
        declaration = declarations.get(question)
        if declaration is None or declaration.answer == "pendiente":
            issue(field, "declaracion_edad_pendiente")
            continue
        if not (declaration.rationale or "").strip():
            issue(field, "fundamento_declaracion_pendiente")
        if not same_scope(declaration):
            issue(field, "alcance_edad_no_comparable", "requiere_revision")
        elif answer in ("si", "no") and declaration.answer != answer:
            issue(field, "declaracion_edad_incoherente", "requiere_revision")
    condition = next(
        (
            c
            for c in special.conditions
            if c.regime_id == "infancia_adolescencia_art16quater"
        ),
        None,
    )
    if condition is None:
        issue("special_conditions_document.conditions", "condicion_infancia_pendiente")
    else:
        if not same_scope(condition):
            issue(
                "special_conditions_document.conditions",
                "alcance_edad_no_comparable",
                "requiere_revision",
            )
        if doc.proposed_authorization_route == "consentimiento":
            if condition.authorization_route is None:
                issue(
                    "special_conditions_document.conditions", "ruta_especial_pendiente"
                )
            elif condition.authorization_route != "consentimiento":
                issue(
                    "special_conditions_document.conditions",
                    "ruta_especial_incoherente",
                    "requiere_revision",
                )
    return tuple(sorted(set(issues), key=lambda i: (i.field, i.code)))
