"""Preparación documental de la excepción biométrica de derechos; no autoriza tratamiento."""

from dataclasses import dataclass
from typing import Literal

from app.schemas.licitud import (
    BiometricRightsExceptionAssessmentV1,
    RatContextSnapshotV1,
    RightsExceptionContextV1,
    SensitiveRightsExceptionAssessmentV1,
    SpecialConditionsV1,
)
from app.services.sensitive_rights_exception import (
    evaluate_sensitive_rights_exception_v1,
)


@dataclass(frozen=True)
class BiometricRightsExceptionIssueV1:
    field: str
    code: str
    category: Literal["incompleto", "requiere_revision"]
    question_id: str | None = None


@dataclass(frozen=True)
class BiometricRightsExceptionApplicabilityV1:
    field: str
    applicability: Literal["aplicable", "no_aplicable", "sin_resolver"]


@dataclass(frozen=True)
class BiometricRightsExceptionReadinessV1:
    result: Literal["incompleto", "requiere_revision", "completo"]
    issues: tuple[BiometricRightsExceptionIssueV1, ...]
    applicability: tuple[BiometricRightsExceptionApplicabilityV1, ...]

    @property
    def can_confirm(self):
        """Preparación documental solamente; no supera las barreras EIPD/transversales."""
        return self.result == "completo"


def evaluate_biometric_rights_exception_v1(
    assessment, snapshot, special_conditions, sensitive_exception
):
    from app.services.licitud import canonicalize_text_v1

    def validate(model, value):
        return model.model_validate(
            value.model_dump() if isinstance(value, model) else value
        )

    document = (
        validate(BiometricRightsExceptionAssessmentV1, assessment)
        if assessment is not None
        else BiometricRightsExceptionAssessmentV1()
    )
    rat = validate(RatContextSnapshotV1, snapshot) if snapshot is not None else None
    special = (
        validate(SpecialConditionsV1, special_conditions)
        if special_conditions is not None
        else None
    )
    context = document.context or RightsExceptionContextV1()
    sensitive = (
        validate(SensitiveRightsExceptionAssessmentV1, sensitive_exception)
        if sensitive_exception is not None
        else None
    )
    dependency = evaluate_sensitive_rights_exception_v1(sensitive, rat, special)

    def dependency_field(field):
        return (
            field
            if field.startswith(
                (
                    "rat_context_snapshot",
                    "special_conditions",
                    "sensitive_rights_exception_assessment",
                )
            )
            else "sensitive_rights_exception_assessment." + field
        )

    issues = [
        BiometricRightsExceptionIssueV1(
            dependency_field(i.field), i.code, i.category, i.question_id
        )
        for i in dependency.issues
    ]
    applicability = [
        BiometricRightsExceptionApplicabilityV1(
            dependency_field(i.field), i.applicability
        )
        for i in dependency.applicability
    ]

    def issue(field, code, category="incompleto", question_id=None):
        issues.append(
            BiometricRightsExceptionIssueV1(field, code, category, question_id)
        )

    def applicable(field, value="aplicable"):
        applicability.append(BiometricRightsExceptionApplicabilityV1(field, value))

    def present(value):
        return value is not None and bool(value.strip())

    def text(field, value, question_id=None):
        applicable(field)
        if not present(value):
            issue(field, "campo_obligatorio", question_id=question_id)

    def enum(field, value):
        applicable(field)
        if value is None:
            issue(field, "campo_obligatorio")

    def response(field, value):
        applicable(field)
        if value is None:
            issue(field, "respuesta_ausente")
            return
        if value.answer == "pendiente":
            issue(field + ".answer", "respuesta_pendiente")
        elif value.answer == "no":
            issue(field + ".answer", "respuesta_revision", "requiere_revision")
        if not present(value.rationale):
            issue(field + ".rationale", "fundamento_ausente")

    def evidence(field, values, question_id=None):
        applicable(field)
        if not values:
            issue(field, "evidencia_ausente", question_id=question_id)
        for index, item in enumerate(values):
            for name in ("evidence_type", "reference"):
                if not present(getattr(item, name)):
                    issue(
                        f"{field}.{index}.{name}",
                        "evidencia_incompleta",
                        question_id=question_id,
                    )

    if assessment is None:
        issue("biometric_rights_exception_assessment", "expediente_ausente")
    if rat is None:
        issue("rat_context_snapshot", "snapshot_ausente")
    else:
        if rat.organization_role != "responsable":
            issue(
                "rat_context_snapshot.organization_role",
                "rol_no_admitido",
                "requiere_revision",
            )
        if not rat.special_regimes.has_sensitive_data or not any(
            c.is_sensitive for c in rat.data_categories
        ):
            issue(
                "rat_context_snapshot",
                "contexto_sensible_incoherente",
                "requiere_revision",
            )
        if present(context.purpose_description) and canonicalize_text_v1(
            context.purpose_description
        ) != canonicalize_text_v1(rat.purpose):
            issue(
                "context.purpose_description", "finalidad_distinta", "requiere_revision"
            )

    enum("exception_basis", document.exception_basis)
    applicable("context")
    if document.context is None:
        issue("context", "contexto_derechos_ausente")
    for name in (
        "context_reference",
        "purpose_description",
        "right_description",
        "right_basis_reference",
        "holder_connection_analysis",
        "forum_description",
        "proceeding_reference",
        "processing_operations",
        "necessity_analysis",
        "data_minimization_analysis",
        "safeguards_analysis",
    ):
        text("context." + name, getattr(context, name))
    for name in ("route", "right_holder", "forum_type", "proceeding_stage"):
        enum("context." + name, getattr(context, name))
    for name in (
        "related_to_right",
        "necessary_for_route",
        "within_forum_scope",
        "principles_addressed",
    ):
        response("context." + name, getattr(context, name))
    for name, stage in (
        ("preparatory_actions", "preparacion"),
        ("post_proceeding_necessity_analysis", "finalizado"),
    ):
        field = "context." + name
        value = getattr(context, name)
        applies = (
            None
            if context.proceeding_stage is None
            else context.proceeding_stage == stage
        )
        applicable(
            field,
            (
                "sin_resolver"
                if applies is None
                else "aplicable" if applies else "no_aplicable"
            ),
        )
        if applies is True and not present(value):
            issue(field, "campo_obligatorio")
        elif applies is False and present(value):
            issue(field, "campo_residual", "requiere_revision")
    evidence("context.evidence", context.evidence)
    for name in (
        "biometric_data_description",
        "exception_application_analysis",
        "unique_identification_analysis",
        "sensitive_context_connection_analysis",
        "systems_coverage_analysis",
    ):
        text(name, getattr(document, name))
    response("exception_conditions_met", document.exception_conditions_met)
    evidence("evidence", document.evidence)
    response(
        "unique_identification_confirmed", document.unique_identification_confirmed
    )
    response("all_systems_documented", document.all_systems_documented)
    applicable("systems")
    if not document.systems:
        issue("systems", "sistemas_ausentes")
    seen = set()
    for index, system in enumerate(document.systems):
        prefix = f"systems.{index}."
        for name in (
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
            text(prefix + name, getattr(system, name))
        for name in (
            "system_identification_disclosed",
            "purpose_disclosed",
            "use_period_disclosed",
            "rights_exercise_disclosed",
        ):
            response(prefix + name, getattr(system, name))
        evidence(prefix + "evidence", system.evidence)
        if present(system.system_reference):
            reference = canonicalize_text_v1(system.system_reference)
            if reference in seen:
                issue(
                    prefix + "system_reference",
                    "sistema_duplicado",
                    "requiere_revision",
                )
            seen.add(reference)
    if sensitive is not None and sensitive.context is not None:
        for name in (
            "context_reference",
            "purpose_description",
            "route",
            "right_holder",
            "forum_type",
            "proceeding_stage",
            "proceeding_reference",
        ):
            ours = getattr(context, name)
            theirs = getattr(sensitive.context, name)
            if name in (
                "context_reference",
                "purpose_description",
                "proceeding_reference",
            ):
                matches = not (
                    present(ours) and present(theirs)
                ) or canonicalize_text_v1(ours) == canonicalize_text_v1(theirs)
            else:
                matches = ours is None or theirs is None or ours == theirs
            if not matches:
                issue(
                    "context." + name,
                    "vinculo_contexto_sensible_discordante",
                    "requiere_revision",
                )

    declaration = None
    condition = None
    question_id = "biometricos_identificacion_unica"
    declaration_path = (
        "special_conditions.declarations.biometricos_identificacion_unica"
    )
    condition_path = "special_conditions.conditions.biometricos_art16ter"
    applicable(declaration_path)
    applicable(condition_path)
    if special is None:
        issue("special_conditions", "condiciones_ausentes", question_id=question_id)
    else:
        declaration = next(
            (d for d in special.declarations if d.question_id == question_id), None
        )
        condition = next(
            (c for c in special.conditions if c.regime_id == "biometricos_art16ter"),
            None,
        )
        if declaration is None:
            issue(declaration_path, "declaracion_ausente", question_id=question_id)
        else:
            if declaration.answer == "pendiente":
                issue(
                    declaration_path + ".answer",
                    "respuesta_pendiente",
                    question_id=question_id,
                )
            elif declaration.answer == "no":
                issue(
                    declaration_path + ".answer",
                    "regimen_no_declarado",
                    "requiere_revision",
                    question_id,
                )
            text(declaration_path + ".rationale", declaration.rationale, question_id)
        if condition is None:
            issue(condition_path, "expediente_regimen_ausente", question_id=question_id)
        else:
            for name, expected, missing, mismatch in (
                (
                    "authorization_route",
                    "excepcion_legal",
                    "ruta_ausente",
                    "ruta_no_admitida",
                ),
                (
                    "uses_consent_assessment",
                    False,
                    "referencia_consentimiento_ausente",
                    "referencia_consentimiento_incoherente",
                ),
            ):
                field = condition_path + "." + name
                value = getattr(condition, name)
                applicable(field)
                if value is None:
                    issue(field, missing, question_id=question_id)
                elif value != expected:
                    issue(field, mismatch, "requiere_revision", question_id)
            for name in ("legal_reference", "documentary_analysis"):
                text(condition_path + "." + name, getattr(condition, name), question_id)
            evidence(condition_path + ".evidence", condition.evidence, question_id)

    applicable("scope")
    if document.scope is None:
        issue("scope", "alcance_ausente")
    for field in ("data_category_codes", "data_subject_codes"):
        available = (
            None
            if rat is None
            else {
                canonicalize_text_v1(i.category_code)
                for i in (
                    rat.data_categories
                    if field == "data_category_codes"
                    else rat.data_subjects
                )
            }
        )
        required = (
            None
            if rat is None
            else {
                canonicalize_text_v1(i.category_code)
                for i in (
                    rat.data_categories
                    if field == "data_category_codes"
                    else rat.data_subjects
                )
                if field != "data_category_codes" or i.is_sensitive
            }
        )
        selected_sets = []
        for path, item, qid in (
            ("scope", document.scope, None),
            (declaration_path, declaration, question_id),
            (condition_path, condition, question_id),
        ):
            applicable(path + "." + field)
            if item is None:
                continue
            values = [canonicalize_text_v1(v) for v in getattr(item, field)]
            if not values:
                issue(path + "." + field, "alcance_vacio", question_id=qid)
            elif (
                len(values) != len(set(values))
                or any(not v for v in values)
                or (available is not None and not set(values).issubset(available))
            ):
                issue(path + "." + field, "alcance_invalido", "requiere_revision", qid)
            if values and required is not None and set(values) != required:
                issue(
                    path + "." + field,
                    "cobertura_biometria_no_preparada",
                    "requiere_revision",
                    qid,
                )
            if (
                values
                and sensitive is not None
                and sensitive.scope is not None
                and set(values)
                != {canonicalize_text_v1(v) for v in getattr(sensitive.scope, field)}
            ):
                issue(
                    path + "." + field,
                    "alcance_excepcion_sensible_discordante",
                    "requiere_revision",
                    qid,
                )
            if values:
                selected_sets.append(set(values))
        if selected_sets and any(v != selected_sets[0] for v in selected_sets[1:]):
            issue("scope." + field, "alcance_discordante", "requiere_revision")

    roots = [
        "rat_context_snapshot",
        "biometric_rights_exception_assessment",
        "sensitive_rights_exception_assessment",
        "special_conditions",
    ] + list(BiometricRightsExceptionAssessmentV1.model_fields)

    def order(item):
        parts = item.field.split(".")
        return (
            roots.index(parts[0]),
            tuple((0, int(p)) if p.isdigit() else (1, p) for p in parts[1:]),
            getattr(item, "code", ""),
        )

    ordered_issues = tuple(sorted(set(issues), key=order))
    ordered_applicability = tuple(sorted(set(applicability), key=order))
    result = (
        "incompleto"
        if any(i.category == "incompleto" for i in ordered_issues)
        else "requiere_revision" if ordered_issues else "completo"
    )
    return BiometricRightsExceptionReadinessV1(
        result, ordered_issues, ordered_applicability
    )
