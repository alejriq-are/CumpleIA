"""Preparación documental del consentimiento sensible, sin habilitar confirmación."""

from dataclasses import dataclass
from typing import Literal

from app.schemas.licitud import (
    ConsentAssessmentV1,
    RatContextSnapshotV1,
    SensitiveConsentAssessmentV1,
    SpecialConditionsV1,
)
from app.services.consentimiento import evaluate_consent_assessment_v1


@dataclass(frozen=True)
class SensitiveConsentIssueV1:
    field: str
    code: str
    category: Literal["incompleto", "requiere_revision"]
    question_id: str | None = None


@dataclass(frozen=True)
class SensitiveConsentApplicabilityV1:
    field: str
    applicability: Literal["aplicable", "no_aplicable", "sin_resolver"]


@dataclass(frozen=True)
class SensitiveConsentReadinessV1:
    result: Literal["incompleto", "requiere_revision", "completo"]
    issues: tuple[SensitiveConsentIssueV1, ...]
    applicability: tuple[SensitiveConsentApplicabilityV1, ...]

    @property
    def can_confirm(self):
        """Preparación documental únicamente; no habilita gates transversales."""
        return self.result == "completo"


def evaluate_sensitive_consent_assessment_v1(
    assessment, snapshot, special_conditions, consent_assessment
):
    from app.services.licitud import canonicalize_text_v1

    def validate(model, value):
        return model.model_validate(
            value.model_dump() if isinstance(value, model) else value
        )

    document = (
        validate(SensitiveConsentAssessmentV1, assessment)
        if assessment is not None
        else SensitiveConsentAssessmentV1()
    )
    rat = validate(RatContextSnapshotV1, snapshot) if snapshot is not None else None
    special = (
        validate(SpecialConditionsV1, special_conditions)
        if special_conditions is not None
        else None
    )
    consent_result = evaluate_consent_assessment_v1(consent_assessment)
    consent = (
        validate(ConsentAssessmentV1, consent_assessment)
        if consent_assessment is not None
        else None
    )
    issues = [
        SensitiveConsentIssueV1(
            (
                "consent_assessment"
                if item.field == "consent_assessment"
                else "consent_assessment." + item.field
            ),
            item.code,
            item.category,
            item.question_id,
        )
        for item in consent_result.issues
    ]
    applicability = [
        SensitiveConsentApplicabilityV1(
            "consent_assessment.answers." + item.question_id, item.applicability
        )
        for item in consent_result.applicability
    ]

    def issue(field, code, category="incompleto"):
        issues.append(SensitiveConsentIssueV1(field, code, category))

    def present(value):
        return value is not None and bool(value.strip())

    def text(field):
        if not present(getattr(document, field)):
            issue(field, "campo_obligatorio")

    def response(field):
        value = getattr(document, field)
        if value is None:
            issue(field, "respuesta_ausente")
            return
        if value.answer == "pendiente":
            issue(field + ".answer", "respuesta_pendiente")
        elif value.answer == "no":
            issue(field + ".answer", "respuesta_revision", "requiere_revision")
        if not present(value.rationale):
            issue(field + ".rationale", "fundamento_ausente")

    if assessment is None:
        issue("sensitive_consent_assessment", "expediente_ausente")
    if rat is None:
        issue("rat_context_snapshot", "snapshot_ausente")
    else:
        if rat.organization_role != "responsable":
            issue(
                "rat_context_snapshot.organization_role",
                "rol_no_admitido",
                "requiere_revision",
            )
        if present(document.purpose_description) and canonicalize_text_v1(
            document.purpose_description
        ) != canonicalize_text_v1(rat.purpose):
            issue("purpose_description", "finalidad_distinta", "requiere_revision")
    declaration = None
    condition = None
    if special is None:
        issue("special_conditions", "condiciones_ausentes")
    else:
        declaration = next(
            (d for d in special.declarations if d.question_id == "datos_sensibles"),
            None,
        )
        condition = next(
            (c for c in special.conditions if c.regime_id == "sensibles_art16"),
            None,
        )
        if declaration is None:
            issue(
                "special_conditions.declarations.datos_sensibles", "declaracion_ausente"
            )
        else:
            field = "special_conditions.declarations.datos_sensibles"
            if declaration.answer == "pendiente":
                issue(field + ".answer", "respuesta_pendiente")
            elif declaration.answer == "no":
                issue(field + ".answer", "regimen_no_declarado", "requiere_revision")
            if not present(declaration.rationale):
                issue(field + ".rationale", "fundamento_ausente")
        if condition is None:
            issue(
                "special_conditions.conditions.sensibles_art16",
                "expediente_regimen_ausente",
            )
        else:
            field = "special_conditions.conditions.sensibles_art16"
            if condition.authorization_route is None:
                issue(field + ".authorization_route", "ruta_ausente")
            elif condition.authorization_route != "consentimiento":
                issue(
                    field + ".authorization_route",
                    "ruta_no_admitida",
                    "requiere_revision",
                )
            if condition.uses_consent_assessment is not True:
                issue(
                    field + ".uses_consent_assessment",
                    "referencia_consentimiento_incoherente",
                    "requiere_revision",
                )
            if condition.sensitive_condition_id != "consentimiento_expreso_art16":
                issue(
                    field + ".sensitive_condition_id",
                    "condicion_no_admitida",
                    "requiere_revision",
                )
            for name in ("legal_reference", "documentary_analysis"):
                if not present(getattr(condition, name)):
                    issue(field + "." + name, "campo_obligatorio")
            if not condition.evidence:
                issue(field + ".evidence", "evidencia_ausente")
            for index, item in enumerate(condition.evidence):
                for name in ("evidence_type", "reference"):
                    if not present(getattr(item, name)):
                        issue(
                            f"{field}.evidence.{index}.{name}", "evidencia_incompleta"
                        )
    for field in (
        "purpose_description",
        "sensitive_data_description",
        "processing_operations",
        "declaration_reference",
        "declaration_content_analysis",
    ):
        text(field)
    if document.expression_method is None:
        issue("expression_method", "campo_obligatorio")
    methods = {
        "escrito": "escrito",
        "verbal": "verbal",
        "tecnologico_equivalente": "electronico",
    }
    if consent is not None:
        if consent.given_by != "titular":
            issue(
                "consent_assessment.given_by",
                "representacion_no_preparada",
                "requiere_revision",
            )
        if (
            document.expression_method is not None
            and consent.grant_method != methods[document.expression_method]
        ):
            issue("expression_method", "medio_discordante", "requiere_revision")
    applies = (
        None
        if document.expression_method is None
        else document.expression_method == "tecnologico_equivalente"
    )
    applicability.append(
        SensitiveConsentApplicabilityV1(
            "technology_equivalence_analysis",
            (
                "sin_resolver"
                if applies is None
                else "aplicable" if applies else "no_aplicable"
            ),
        )
    )
    if applies:
        text("technology_equivalence_analysis")
    elif applies is False and present(document.technology_equivalence_analysis):
        issue("technology_equivalence_analysis", "campo_residual", "requiere_revision")
    if rat is not None and (
        not rat.special_regimes.has_sensitive_data
        or not any(item.is_sensitive for item in rat.data_categories)
    ):
        issue(
            "rat_context_snapshot", "contexto_sensible_incoherente", "requiere_revision"
        )
    if document.scope is None:
        issue("scope", "alcance_ausente")
    for field, available in (
        (
            "data_category_codes",
            (
                {canonicalize_text_v1(i.category_code) for i in rat.data_categories}
                if rat
                else None
            ),
        ),
        (
            "data_subject_codes",
            (
                {canonicalize_text_v1(i.category_code) for i in rat.data_subjects}
                if rat
                else None
            ),
        ),
    ):
        values = (
            [canonicalize_text_v1(v) for v in getattr(document.scope, field)]
            if document.scope is not None
            else []
        )
        if document.scope is not None:
            if not values:
                issue("scope." + field, "alcance_vacio")
            elif len(values) != len(set(values)) or (
                available is not None and not set(values).issubset(available)
            ):
                issue("scope." + field, "alcance_invalido", "requiere_revision")
        if rat is not None and values:
            required = (
                {
                    canonicalize_text_v1(i.category_code)
                    for i in rat.data_categories
                    if i.is_sensitive
                }
                if field == "data_category_codes"
                else {canonicalize_text_v1(i.category_code) for i in rat.data_subjects}
            )
            if set(values) != required:
                issue(
                    "scope." + field,
                    "cobertura_sensible_incompleta",
                    "requiere_revision",
                )
        for name, item in (
            ("declarations.datos_sensibles", declaration),
            ("conditions.sensibles_art16", condition),
        ):
            if item is None:
                continue
            selected = [canonicalize_text_v1(v) for v in getattr(item, field)]
            if not selected:
                issue("special_conditions." + name + "." + field, "alcance_vacio")
            elif len(selected) != len(set(selected)) or (
                available is not None and not set(selected).issubset(available)
            ):
                issue(
                    "special_conditions." + name + "." + field,
                    "alcance_invalido",
                    "requiere_revision",
                )
            if rat is not None and selected:
                required = (
                    {
                        canonicalize_text_v1(i.category_code)
                        for i in rat.data_categories
                        if i.is_sensitive
                    }
                    if field == "data_category_codes"
                    else {
                        canonicalize_text_v1(i.category_code) for i in rat.data_subjects
                    }
                )
                if set(selected) != required:
                    issue(
                        "special_conditions." + name + "." + field,
                        "cobertura_sensible_incompleta",
                        "requiere_revision",
                    )
            if values and selected and set(values) != set(selected):
                issue("scope." + field, "alcance_discordante", "requiere_revision")
    for field in (
        "express_declaration_documented",
        "sensitive_scope_explicit",
        "purpose_specific",
        "proof_available",
        "consent_current",
    ):
        response(field)
    if not document.evidence:
        issue("evidence", "evidencia_ausente")
    for index, item in enumerate(document.evidence):
        for field in ("evidence_type", "reference"):
            if not present(getattr(item, field)):
                issue(f"evidence.{index}.{field}", "evidencia_incompleta")

    def order(item):
        roots = [
            "rat_context_snapshot",
            "sensitive_consent_assessment",
            "special_conditions",
            "consent_assessment",
        ] + list(SensitiveConsentAssessmentV1.model_fields)
        parts = item.field.split(".")
        return (
            roots.index(parts[0]),
            tuple((0, int(p)) if p.isdigit() else (1, p) for p in parts[1:]),
            item.code,
        )

    # Two comparisons may report the same scope discordance, keep one reason.
    issues = list(dict.fromkeys(issues))
    issues.sort(key=order)
    result = (
        "incompleto"
        if any(i.category == "incompleto" for i in issues)
        else "requiere_revision" if issues else "completo"
    )
    return SensitiveConsentReadinessV1(result, tuple(issues), tuple(applicability))
