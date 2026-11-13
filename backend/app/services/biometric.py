"""Preparación documental biométrica; no habilita el régimen especial."""

from dataclasses import dataclass
from typing import Literal

from app.schemas.licitud import (
    BiometricAssessmentV1,
    RatContextSnapshotV1,
    SensitiveConsentAssessmentV1,
    SpecialConditionsV1,
)
from app.services.sensitive_consent import evaluate_sensitive_consent_assessment_v1


@dataclass(frozen=True)
class BiometricIssueV1:
    field: str
    code: str
    category: Literal["incompleto", "requiere_revision"]
    question_id: str | None = None


@dataclass(frozen=True)
class BiometricApplicabilityV1:
    field: str
    applicability: Literal["aplicable", "no_aplicable", "sin_resolver"]


@dataclass(frozen=True)
class BiometricReadinessV1:
    result: Literal["incompleto", "requiere_revision", "completo"]
    issues: tuple[BiometricIssueV1, ...]
    applicability: tuple[BiometricApplicabilityV1, ...]

    @property
    def can_confirm(self):
        """Preparación únicamente; otros controles siguen siendo obligatorios."""
        return self.result == "completo"


def evaluate_biometric_assessment_v1(
    assessment, snapshot, special_conditions, consent_assessment, sensitive_consent
):
    from app.services.licitud import canonicalize_text_v1

    def validate(model, value):
        return model.model_validate(
            value.model_dump() if isinstance(value, model) else value
        )

    document = (
        validate(BiometricAssessmentV1, assessment)
        if assessment is not None
        else BiometricAssessmentV1()
    )
    rat = validate(RatContextSnapshotV1, snapshot) if snapshot is not None else None
    special = (
        validate(SpecialConditionsV1, special_conditions)
        if special_conditions is not None
        else None
    )
    sensitive = (
        validate(SensitiveConsentAssessmentV1, sensitive_consent)
        if sensitive_consent is not None
        else None
    )
    dependency = evaluate_sensitive_consent_assessment_v1(
        sensitive_consent, snapshot, special_conditions, consent_assessment
    )
    issues = [
        BiometricIssueV1(
            (
                i.field
                if i.field.startswith(
                    (
                        "rat_context_snapshot",
                        "special_conditions",
                        "consent_assessment",
                        "sensitive_consent_assessment",
                    )
                )
                else "sensitive_consent_assessment." + i.field
            ),
            i.code,
            i.category,
            i.question_id,
        )
        for i in dependency.issues
    ]
    applicability = [
        BiometricApplicabilityV1(
            (
                i.field
                if i.field.startswith("consent_assessment")
                else "sensitive_consent_assessment." + i.field
            ),
            i.applicability,
        )
        for i in dependency.applicability
    ]

    def issue(field, code, category="incompleto"):
        issues.append(BiometricIssueV1(field, code, category))

    def present(value):
        return value is not None and bool(str(value).strip())

    def text(field, owner=document, prefix=""):
        applicability.append(BiometricApplicabilityV1(prefix + field, "aplicable"))
        if not present(getattr(owner, field)):
            issue(prefix + field, "campo_obligatorio")

    def response(field, owner=document, prefix=""):
        applicability.append(BiometricApplicabilityV1(prefix + field, "aplicable"))
        value = getattr(owner, field)
        if value is None:
            issue(prefix + field, "respuesta_ausente")
            return
        if value.answer == "pendiente":
            issue(prefix + field + ".answer", "respuesta_pendiente")
        elif value.answer == "no":
            issue(prefix + field + ".answer", "respuesta_revision", "requiere_revision")
        if not present(value.rationale):
            issue(prefix + field + ".rationale", "fundamento_ausente")

    def evidence(items, prefix=""):
        applicability.append(BiometricApplicabilityV1(prefix + "evidence", "aplicable"))
        if not items:
            issue(prefix + "evidence", "evidencia_ausente")
        for index, item in enumerate(items):
            for field in ("evidence_type", "reference"):
                if not present(getattr(item, field)):
                    issue(f"{prefix}evidence.{index}.{field}", "evidencia_incompleta")

    if assessment is None:
        issue("biometric_assessment", "expediente_ausente")
    for field in (
        "purpose_description",
        "biometric_data_description",
        "processing_operations",
        "unique_identification_analysis",
        "systems_coverage_analysis",
    ):
        text(field)
    if document.route is None:
        issue("route", "ruta_ausente")
    if (
        rat is not None
        and present(document.purpose_description)
        and canonicalize_text_v1(document.purpose_description)
        != canonicalize_text_v1(rat.purpose)
    ):
        issue("purpose_description", "finalidad_distinta", "requiere_revision")
    for field in ("unique_identification_confirmed", "all_systems_documented"):
        response(field)
    evidence(document.evidence)
    applicability.append(BiometricApplicabilityV1("systems", "aplicable"))
    if not document.systems:
        issue("systems", "sistemas_ausentes")
    seen = set()
    for index, system in enumerate(document.systems):
        prefix = f"systems.{index}."
        for field in (
            "system_reference",
            "system_name",
            "system_description",
            "specific_purpose",
            "purpose_alignment_analysis",
            "use_period_description",
            "retention_alignment_analysis",
            "rights_exercise_description",
            "rights_contact_channel",
            "information_reference",
        ):
            text(field, system, prefix)
        for field in (
            "system_identification_disclosed",
            "purpose_disclosed",
            "use_period_disclosed",
            "rights_exercise_disclosed",
        ):
            response(field, system, prefix)
        evidence(system.evidence, prefix)
        reference = (
            canonicalize_text_v1(system.system_reference)
            if present(system.system_reference)
            else None
        )
        if reference is not None:
            if reference in seen:
                issue(
                    prefix + "system_reference",
                    "sistema_duplicado",
                    "requiere_revision",
                )
            seen.add(reference)
    declaration = (
        next(
            (
                i
                for i in special.declarations
                if i.question_id == "biometricos_identificacion_unica"
            ),
            None,
        )
        if special
        else None
    )
    condition = (
        next(
            (i for i in special.conditions if i.regime_id == "biometricos_art16ter"),
            None,
        )
        if special
        else None
    )
    for item, field in (
        (
            declaration,
            "special_conditions.declarations.biometricos_identificacion_unica",
        ),
        (condition, "special_conditions.conditions.biometricos_art16ter"),
    ):
        if item is None:
            issue(
                field,
                (
                    "declaracion_ausente"
                    if ".declarations." in field
                    else "expediente_regimen_ausente"
                ),
            )
            continue
        if item is declaration:
            if item.answer == "pendiente":
                issue(field + ".answer", "respuesta_pendiente")
            elif item.answer == "no":
                issue(field + ".answer", "regimen_no_declarado", "requiere_revision")
            if not present(item.rationale):
                issue(field + ".rationale", "fundamento_ausente")
        else:
            if item.authorization_route is None:
                issue(field + ".authorization_route", "ruta_ausente")
            elif item.authorization_route != "consentimiento":
                issue(
                    field + ".authorization_route",
                    "ruta_no_admitida",
                    "requiere_revision",
                )
            if item.uses_consent_assessment is not True:
                issue(
                    field + ".uses_consent_assessment",
                    "referencia_consentimiento_incoherente",
                    "requiere_revision",
                )
            for name in ("legal_reference", "documentary_analysis"):
                if not present(getattr(item, name)):
                    issue(field + "." + name, "campo_obligatorio")
            if not item.evidence:
                issue(field + ".evidence", "evidencia_ausente")
            for index, evidence in enumerate(item.evidence):
                for name in ("evidence_type", "reference"):
                    if not present(getattr(evidence, name)):
                        issue(
                            f"{field}.evidence.{index}.{name}", "evidencia_incompleta"
                        )
    if document.scope is None:
        issue("scope", "alcance_ausente")
    for name in ("data_category_codes", "data_subject_codes"):
        required = (
            None
            if rat is None
            else {
                canonicalize_text_v1(i.category_code)
                for i in (
                    rat.data_categories
                    if name == "data_category_codes"
                    else rat.data_subjects
                )
                if name != "data_category_codes" or i.is_sensitive
            }
        )
        available = (
            None
            if rat is None
            else {
                canonicalize_text_v1(i.category_code)
                for i in (
                    rat.data_categories
                    if name == "data_category_codes"
                    else rat.data_subjects
                )
            }
        )
        selectors = [
            ("scope", document.scope),
            (
                "special_conditions.declarations.biometricos_identificacion_unica",
                declaration,
            ),
            (
                "special_conditions.conditions.biometricos_art16ter",
                condition,
            ),
        ]
        selected_sets = []
        for field, item in selectors:
            if item is None:
                continue
            values = [canonicalize_text_v1(v) for v in getattr(item, name)]
            selected_sets.append(set(values))
            if not values:
                issue(field + "." + name, "alcance_vacio")
            elif len(values) != len(set(values)) or (
                available is not None and not set(values).issubset(available)
            ):
                issue(field + "." + name, "alcance_invalido", "requiere_revision")
            if values and required is not None and set(values) != required:
                issue(
                    field + "." + name,
                    "cobertura_biometria_no_preparada",
                    "requiere_revision",
                )
            if (
                sensitive is not None
                and sensitive.scope is not None
                and values
                and set(values)
                != {canonicalize_text_v1(v) for v in getattr(sensitive.scope, name)}
            ):
                issue(
                    field + "." + name,
                    "alcance_consentimiento_discordante",
                    "requiere_revision",
                )
        if selected_sets and any(
            values != selected_sets[0] for values in selected_sets[1:]
        ):
            issue("scope." + name, "alcance_discordante", "requiere_revision")

    roots = [
        "rat_context_snapshot",
        "biometric_assessment",
        "special_conditions",
        "consent_assessment",
        "sensitive_consent_assessment",
    ] + list(BiometricAssessmentV1.model_fields)

    def order(item):
        parts = item.field.split(".")
        return (
            roots.index(parts[0]),
            tuple((0, int(p)) if p.isdigit() else (1, p) for p in parts[1:]),
            item.code,
        )

    issues = sorted(set(issues), key=order)
    result = (
        "incompleto"
        if any(i.category == "incompleto" for i in issues)
        else "requiere_revision" if issues else "completo"
    )
    return BiometricReadinessV1(result, tuple(issues), tuple(applicability))
