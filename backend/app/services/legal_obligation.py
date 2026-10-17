"""Preparación documental normativa; no verifica autenticidad o vigencia legal."""

from dataclasses import dataclass
from typing import Literal

from app.schemas.licitud import LegalObligationAssessmentV1, RatContextSnapshotV1


@dataclass(frozen=True)
class LegalObligationIssueV1:
    field: str
    code: str
    category: Literal["incompleto", "requiere_revision"]
    question_id: str | None = None


@dataclass(frozen=True)
class LegalObligationApplicabilityV1:
    field: str
    applicability: Literal["aplicable", "no_aplicable", "sin_resolver"]


@dataclass(frozen=True)
class LegalObligationReadinessV1:
    result: Literal["incompleto", "requiere_revision", "completo"]
    issues: tuple[LegalObligationIssueV1, ...]
    applicability: tuple[LegalObligationApplicabilityV1, ...]

    @property
    def can_confirm(self):
        """Supera solamente preparación normativa, no controles transversales."""
        return self.result == "completo"


def evaluate_legal_obligation_assessment_v1(assessment, snapshot):
    from app.services.licitud import canonicalize_text_v1

    legal = (
        LegalObligationAssessmentV1.model_validate(assessment)
        if assessment is not None
        else LegalObligationAssessmentV1()
    )
    rat = (
        RatContextSnapshotV1.model_validate(snapshot) if snapshot is not None else None
    )
    issues = []
    applicability = []

    def issue(field, code, category="incompleto"):
        issues.append(LegalObligationIssueV1(field, code, category))

    def present(value):
        return value is not None and bool(value.strip())

    def text(field):
        if not present(getattr(legal, field)):
            issue(field, "campo_obligatorio")

    def response(field):
        value = getattr(legal, field)
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
        issue("legal_obligation_assessment", "expediente_ausente")
    if rat is None:
        issue("rat_context_snapshot", "snapshot_ausente")
    else:
        if rat.organization_role != "responsable":
            issue(
                "rat_context_snapshot.organization_role",
                "rol_no_admitido",
                "requiere_revision",
            )
        if present(legal.purpose_description) and canonicalize_text_v1(
            legal.purpose_description
        ) != canonicalize_text_v1(rat.purpose):
            issue("purpose_description", "finalidad_distinta", "requiere_revision")
    if legal.route is None:
        issue("route", "ruta_ausente")
    for field in (
        "purpose_description",
        "normative_requirement_description",
        "processing_operations",
        "applicability_analysis",
        "necessity_analysis",
        "data_minimization_analysis",
    ):
        text(field)
    for field in (
        "normative_basis_reviewed",
        "normative_basis_in_force",
        "processing_within_legal_scope",
    ):
        response(field)
    for field, route in (
        ("obligation_applies_to_controller", "cumplimiento_obligacion_legal"),
        ("processing_required_by_law", "tratamiento_dispuesto_por_ley"),
    ):
        applies = None if legal.route is None else legal.route == route
        state = (
            "sin_resolver"
            if applies is None
            else "aplicable" if applies else "no_aplicable"
        )
        applicability.append(LegalObligationApplicabilityV1(field, state))
        if applies:
            response(field)
        elif applies is False and getattr(legal, field) is not None:
            issue(field, "campo_residual", "requiere_revision")
    if not legal.normative_references:
        issue("normative_references", "referencia_normativa_ausente")
    for index, reference in enumerate(legal.normative_references):
        for field in type(reference).model_fields:
            value = getattr(reference, field)
            if value is None or (isinstance(value, str) and not value.strip()):
                issue(
                    f"normative_references.{index}.{field}",
                    "referencia_normativa_incompleta",
                )
    if not legal.evidence:
        issue("evidence", "evidencia_ausente")
    for index, item in enumerate(legal.evidence):
        for field in ("evidence_type", "reference"):
            if not present(getattr(item, field)):
                issue(f"evidence.{index}.{field}", "evidencia_incompleta")

    def order(item):
        parts = item.field.split(".")
        if parts[0] == "rat_context_snapshot":
            return (0, 0, 0, 0)
        if parts[0] == "legal_obligation_assessment":
            return (1, 0, 0, 0)
        field_index = list(LegalObligationAssessmentV1.model_fields).index(parts[0])
        if parts[0] == "normative_references" and len(parts) > 1:
            return (
                2,
                field_index,
                int(parts[1]),
                list(
                    type(legal.normative_references[int(parts[1])]).model_fields
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
    return LegalObligationReadinessV1(result, tuple(issues), tuple(applicability))
