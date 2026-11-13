"""Preparación documental de derechos; no certifica necesidad jurídica."""

from dataclasses import dataclass
from typing import Literal

from app.schemas.licitud import RatContextSnapshotV1, RightsDefenseAssessmentV1


@dataclass(frozen=True)
class RightsDefenseIssueV1:
    field: str
    code: str
    category: Literal["incompleto", "requiere_revision"]
    question_id: str | None = None


@dataclass(frozen=True)
class RightsDefenseApplicabilityV1:
    field: str
    applicability: Literal["aplicable", "no_aplicable", "sin_resolver"]


@dataclass(frozen=True)
class RightsDefenseReadinessV1:
    result: Literal["incompleto", "requiere_revision", "completo"]
    issues: tuple[RightsDefenseIssueV1, ...]
    applicability: tuple[RightsDefenseApplicabilityV1, ...]

    @property
    def can_confirm(self):
        """Supera solamente preparación de derechos, no controles transversales."""
        return self.result == "completo"


def evaluate_rights_defense_assessment_v1(assessment, snapshot):
    from app.services.licitud import canonicalize_text_v1

    rights = (
        RightsDefenseAssessmentV1.model_validate(assessment)
        if assessment is not None
        else RightsDefenseAssessmentV1()
    )
    rat = (
        RatContextSnapshotV1.model_validate(snapshot) if snapshot is not None else None
    )
    issues = []
    applicability = []

    def issue(field, code, category="incompleto"):
        issues.append(RightsDefenseIssueV1(field, code, category))

    def present(value):
        return value is not None and bool(value.strip())

    def text(field):
        if not present(getattr(rights, field)):
            issue(field, "campo_obligatorio")

    def response(field):
        value = getattr(rights, field)
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
        issue("rights_defense_assessment", "expediente_ausente")
    if rat is None:
        issue("rat_context_snapshot", "snapshot_ausente")
    else:
        if rat.organization_role != "responsable":
            issue(
                "rat_context_snapshot.organization_role",
                "rol_no_admitido",
                "requiere_revision",
            )
        if present(rights.purpose_description) and canonicalize_text_v1(
            rights.purpose_description
        ) != canonicalize_text_v1(rat.purpose):
            issue("purpose_description", "finalidad_distinta", "requiere_revision")
    for field in ("route", "right_holder", "forum_type", "proceeding_stage"):
        if getattr(rights, field) is None:
            issue(field, "campo_obligatorio")
    for field in (
        "purpose_description",
        "right_description",
        "right_basis_reference",
        "holder_connection_analysis",
        "forum_description",
        "processing_operations",
        "necessity_analysis",
        "data_minimization_analysis",
    ):
        text(field)
    for field in ("related_to_right", "necessary_for_route", "within_forum_scope"):
        response(field)
    if rights.proceeding_stage == "preparacion" and rights.route in (
        "ejercicio_derecho",
        "defensa_derecho",
    ):
        issue("proceeding_stage", "etapa_ruta_incoherente", "requiere_revision")
    for field in (
        "proceeding_reference",
        "preparatory_actions",
        "post_proceeding_necessity_analysis",
    ):
        applies = (
            None
            if rights.proceeding_stage is None
            else (
                rights.proceeding_stage != "preparacion"
                if field == "proceeding_reference"
                else (
                    rights.proceeding_stage == "preparacion"
                    if field == "preparatory_actions"
                    else rights.proceeding_stage == "finalizado"
                )
            )
        )
        state = (
            "sin_resolver"
            if applies is None
            else "aplicable" if applies else "no_aplicable"
        )
        applicability.append(RightsDefenseApplicabilityV1(field, state))
        if applies:
            text(field)
        elif (
            applies is False
            and field != "proceeding_reference"
            and present(getattr(rights, field))
        ):
            issue(field, "campo_residual", "requiere_revision")
    if not rights.evidence:
        issue("evidence", "evidencia_ausente")
    for index, item in enumerate(rights.evidence):
        for field in ("evidence_type", "reference"):
            if not present(getattr(item, field)):
                issue(f"evidence.{index}.{field}", "evidencia_incompleta")

    def order(item):
        parts = item.field.split(".")
        if parts[0] == "rat_context_snapshot":
            return (0, 0, 0, 0)
        if parts[0] == "rights_defense_assessment":
            return (1, 0, 0, 0)
        field_index = list(RightsDefenseAssessmentV1.model_fields).index(parts[0])
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
    return RightsDefenseReadinessV1(result, tuple(issues), tuple(applicability))
