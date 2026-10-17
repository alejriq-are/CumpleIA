"""Preparación documental de la excepción sensible de derechos; no autoriza tratamiento."""

from dataclasses import dataclass
from typing import Literal

from app.schemas.licitud import (
    RatContextSnapshotV1,
    RightsExceptionContextV1,
    SensitiveRightsExceptionAssessmentV1,
    SpecialConditionsV1,
)


@dataclass(frozen=True)
class SensitiveRightsExceptionIssueV1:
    field: str
    code: str
    category: Literal["incompleto", "requiere_revision"]
    question_id: str | None = None


@dataclass(frozen=True)
class SensitiveRightsExceptionApplicabilityV1:
    field: str
    applicability: Literal["aplicable", "no_aplicable", "sin_resolver"]


@dataclass(frozen=True)
class SensitiveRightsExceptionReadinessV1:
    result: Literal["incompleto", "requiere_revision", "completo"]
    issues: tuple[SensitiveRightsExceptionIssueV1, ...]
    applicability: tuple[SensitiveRightsExceptionApplicabilityV1, ...]

    @property
    def can_confirm(self):
        """Preparación documental solamente; no supera las barreras EIPD/transversales."""
        return self.result == "completo"


def evaluate_sensitive_rights_exception_v1(assessment, snapshot, special_conditions):
    from app.services.licitud import canonicalize_text_v1

    def validate(model, value):
        return model.model_validate(
            value.model_dump() if isinstance(value, model) else value
        )

    document = (
        validate(SensitiveRightsExceptionAssessmentV1, assessment)
        if assessment is not None
        else SensitiveRightsExceptionAssessmentV1()
    )
    rat = validate(RatContextSnapshotV1, snapshot) if snapshot is not None else None
    special = (
        validate(SpecialConditionsV1, special_conditions)
        if special_conditions is not None
        else None
    )
    context = document.context or RightsExceptionContextV1()
    issues = []
    applicability = []

    def issue(field, code, category="incompleto", question_id=None):
        issues.append(
            SensitiveRightsExceptionIssueV1(field, code, category, question_id)
        )

    def applicable(field, value="aplicable"):
        applicability.append(SensitiveRightsExceptionApplicabilityV1(field, value))

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
        issue("sensitive_rights_exception_assessment", "expediente_ausente")
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
    for name in ("sensitive_data_description", "exception_application_analysis"):
        text(name, getattr(document, name))
    response("exception_conditions_met", document.exception_conditions_met)
    evidence("evidence", document.evidence)

    declaration = None
    condition = None
    question_id = "datos_sensibles"
    declaration_path = "special_conditions.declarations.datos_sensibles"
    condition_path = "special_conditions.conditions.sensibles_art16"
    applicable(declaration_path)
    applicable(condition_path)
    if special is None:
        issue("special_conditions", "condiciones_ausentes", question_id=question_id)
    else:
        declaration = next(
            (d for d in special.declarations if d.question_id == question_id), None
        )
        condition = next(
            (c for c in special.conditions if c.regime_id == "sensibles_art16"), None
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
                    "sensitive_condition_id",
                    "defensa_derechos_art16d",
                    "condicion_ausente",
                    "condicion_no_admitida",
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
                    "cobertura_sensible_incompleta",
                    "requiere_revision",
                    qid,
                )
            if values:
                selected_sets.append(set(values))
        if selected_sets and any(v != selected_sets[0] for v in selected_sets[1:]):
            issue("scope." + field, "alcance_discordante", "requiere_revision")

    roots = [
        "rat_context_snapshot",
        "sensitive_rights_exception_assessment",
        "special_conditions",
    ] + list(SensitiveRightsExceptionAssessmentV1.model_fields)

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
    return SensitiveRightsExceptionReadinessV1(
        result, ordered_issues, ordered_applicability
    )
