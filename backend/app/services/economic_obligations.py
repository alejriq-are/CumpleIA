"""Preparación documental económica; no verifica autenticidad o vigencia economic."""

from dataclasses import dataclass
from typing import Literal

from app.schemas.licitud import EconomicObligationsAssessmentV1, RatContextSnapshotV1


@dataclass(frozen=True)
class EconomicObligationsIssueV1:
    field: str
    code: str
    category: Literal["incompleto", "requiere_revision"]
    question_id: str | None = None


@dataclass(frozen=True)
class EconomicObligationsApplicabilityV1:
    field: str
    applicability: Literal["aplicable", "no_aplicable", "sin_resolver"]


@dataclass(frozen=True)
class EconomicObligationsReadinessV1:
    result: Literal["incompleto", "requiere_revision", "completo"]
    issues: tuple[EconomicObligationsIssueV1, ...]
    applicability: tuple[EconomicObligationsApplicabilityV1, ...]

    @property
    def can_confirm(self):
        """Supera solamente preparación económica, no controles transversales."""
        return self.result == "completo"


def evaluate_economic_obligations_assessment_v1(assessment, snapshot):
    from app.services.licitud import canonicalize_text_v1

    economic = (
        EconomicObligationsAssessmentV1.model_validate(assessment)
        if assessment is not None
        else EconomicObligationsAssessmentV1()
    )
    rat = (
        RatContextSnapshotV1.model_validate(snapshot) if snapshot is not None else None
    )
    issues = []
    applicability = []

    def issue(field, code, category="incompleto"):
        issues.append(EconomicObligationsIssueV1(field, code, category))

    def present(value):
        return value is not None and bool(value.strip())

    def text(field):
        if not present(getattr(economic, field)):
            issue(field, "campo_obligatorio")

    def response(field):
        value = getattr(economic, field)
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
        issue("economic_obligations_assessment", "expediente_ausente")
    if rat is None:
        issue("rat_context_snapshot", "snapshot_ausente")
    else:
        if rat.organization_role != "responsable":
            issue(
                "rat_context_snapshot.organization_role",
                "rol_no_admitido",
                "requiere_revision",
            )
        if present(economic.purpose_description) and canonicalize_text_v1(
            economic.purpose_description
        ) != canonicalize_text_v1(rat.purpose):
            issue("purpose_description", "finalidad_distinta", "requiere_revision")
    for field in ("route", "obligation_type"):
        if getattr(economic, field) is None:
            issue(field, "campo_obligatorio")
    for field in (
        "purpose_description",
        "obligation_description",
        "obligation_reference",
        "holder_connection_analysis",
        "processing_operations",
        "applicability_analysis",
        "data_minimization_analysis",
        "title_iii_analysis",
        "retention_and_deletion_analysis",
        "accuracy_and_update_analysis",
    ):
        text(field)
    factual = economic.operations_include_communication
    if factual is None:
        issue("operations_include_communication", "respuesta_ausente")
    else:
        if factual.answer == "pendiente":
            issue("operations_include_communication.answer", "respuesta_pendiente")
        elif economic.route is not None and (factual.answer == "si") != (
            economic.route == "con_comunicacion"
        ):
            issue(
                "operations_include_communication.answer",
                "operaciones_ruta_incoherentes",
                "requiere_revision",
            )
        if not present(factual.rationale):
            issue("operations_include_communication.rationale", "fundamento_ausente")
    for field in (
        "related_to_obligation",
        "title_iii_reviewed",
        "processing_within_title_iii",
        "retention_and_deletion_compatible",
        "accuracy_controls_documented",
    ):
        response(field)
    conditional_texts = (
        "communication_scope",
        "communication_eligibility_analysis",
        "communication_restrictions_analysis",
        "payment_and_extinction_controls",
    )
    conditional_responses = (
        "communication_permitted",
        "excluded_data_screened",
        "communication_limits_respected",
    )
    applies = None if economic.route is None else economic.route == "con_comunicacion"
    for field in conditional_texts + conditional_responses:
        state = (
            "sin_resolver"
            if applies is None
            else "aplicable" if applies else "no_aplicable"
        )
        applicability.append(EconomicObligationsApplicabilityV1(field, state))
        if applies:
            if field in conditional_texts:
                text(field)
            else:
                response(field)
        elif applies is False:
            value = getattr(economic, field)
            residual = (
                present(value) if field in conditional_texts else value is not None
            )
            if residual:
                issue(field, "campo_residual", "requiere_revision")
    if not economic.normative_references:
        issue("normative_references", "referencia_normativa_ausente")
    for index, reference in enumerate(economic.normative_references):
        for field in type(reference).model_fields:
            value = getattr(reference, field)
            if value is None or (isinstance(value, str) and not value.strip()):
                issue(
                    f"normative_references.{index}.{field}",
                    "referencia_normativa_incompleta",
                )
    if not economic.evidence:
        issue("evidence", "evidencia_ausente")
    for index, item in enumerate(economic.evidence):
        for field in ("evidence_type", "reference"):
            if not present(getattr(item, field)):
                issue(f"evidence.{index}.{field}", "evidencia_incompleta")

    def order(item):
        parts = item.field.split(".")
        if parts[0] == "rat_context_snapshot":
            return (0, 0, 0, 0)
        if parts[0] == "economic_obligations_assessment":
            return (1, 0, 0, 0)
        field_index = list(EconomicObligationsAssessmentV1.model_fields).index(parts[0])
        if parts[0] == "normative_references" and len(parts) > 1:
            return (
                2,
                field_index,
                int(parts[1]),
                list(
                    type(economic.normative_references[int(parts[1])]).model_fields
                ).index(parts[2]),
            )
        if parts[0] == "evidence" and len(parts) > 1:
            return (
                2,
                field_index,
                int(parts[1]),
                0 if parts[2] == "evidence_type" else 1,
            )
        return (2, field_index, 0, 0 if len(parts) == 1 or parts[1] == "answer" else 1)

    issues.sort(key=order)
    result = (
        "incompleto"
        if any(i.category == "incompleto" for i in issues)
        else "requiere_revision" if issues else "completo"
    )
    return EconomicObligationsReadinessV1(result, tuple(issues), tuple(applicability))
