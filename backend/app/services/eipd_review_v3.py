"""Prerequisitos puros V3 para resoluciones V2; sin permisos ni escritura."""

from dataclasses import dataclass
from datetime import date
from typing import Literal

from pydantic import BaseModel

from app.schemas.eipd_review_metadata import EipdReviewContextMetadataV1
from app.schemas.licitud import EipdResolutionReviewIn
from app.services.eipd_controls import EipdCompositionIssueV1
from app.services.eipd_controls_v3 import (
    STAGES_V3,
    EipdControlCompositionInputV3,
    EipdControlCompositionV3,
    compose_eipd_controls_v3,
)
from app.services.eipd_review_metadata import build_eipd_review_context_metadata_v1


@dataclass(frozen=True)
class EipdResolutionReviewPrerequisitesV3:
    decision: Literal["continuar", "requiere_cambios", "no_continuar"]
    issues: tuple[EipdCompositionIssueV1, ...]
    context_metadata: EipdReviewContextMetadataV1 | None
    composition: EipdControlCompositionV3 | None

    @property
    def evaluation_version(self) -> Literal[3]:
        return 3

    @property
    def prerequisites_met(self) -> bool:
        return not self.issues

    @property
    def can_confirm(self) -> Literal[False]:
        return False


def evaluate_eipd_resolution_review_prerequisites_v3(
    value, review, *, evaluated_on: date
):
    """Negativas requieren identidad V2 vigente, no completitud del contenido.

    Continuar agrega controles comunes sin exigir una revision humana anterior.
    Metadata se genera desde material de servidor, nunca de la solicitud humana.
    Caller debe autorizar tenant/actor y releer bajo lock antes de cualquier evento.
    Este evaluador no habilita la accion HTTP V2 ni la activacion de EIPD.
    """
    if type(evaluated_on) is not date:
        raise ValueError("evaluated_on exige date explicita")
    raw = value.model_dump(mode="python") if isinstance(value, BaseModel) else value
    data = EipdControlCompositionInputV3.model_validate(raw)
    raw_review = (
        review.model_dump(mode="python") if isinstance(review, BaseModel) else review
    )
    request = EipdResolutionReviewIn.model_validate(raw_review)
    assessment = data.assessment
    issues = []

    def block(stage, field, code, category="requiere_revision"):
        issues.append(EipdCompositionIssueV1(stage, field, code, category, None))

    if assessment.assessment_status != "borrador":
        block("state", "assessment_status", "evaluacion_no_borrador")
    for field in ("assessment_schema_version", "rat_context_schema_version"):
        if getattr(assessment, field) != 1:
            block("state", field, "version_no_admitida")
    if assessment.rat_context_current is not True:
        block(
            "rat",
            "rat_context_current",
            (
                "contexto_rat_desactualizado"
                if assessment.rat_context_current is False
                else "vigencia_rat_no_resuelta"
            ),
        )
    document, context = assessment.resolution, assessment.context
    metadata = None
    if document is None:
        block(
            "resolution",
            "eipd_resolution_assessment",
            "expediente_ausente",
            "incompleto",
        )
    if context is None:
        block("rat", "rat_context_snapshot", "contexto_rat_no_disponible", "incompleto")
    if document is not None:
        if document.context_binding is None:
            block("resolution", "context_binding", "asociacion_ausente", "incompleto")
        elif document.context_binding.binding_version != 2:
            block(
                "resolution", "context_binding", "asociacion_investigacion_no_cubierta"
            )
        elif context is not None:
            try:
                metadata = build_eipd_review_context_metadata_v1(document, context)
            except ValueError:
                block(
                    "resolution", "context_binding.context_hash", "asociacion_obsoleta"
                )
    if metadata is None:
        block("review", "context_metadata", "metadatos_revision_no_disponibles")
    composition = None
    if request.decision == "continuar":
        composition = compose_eipd_controls_v3(data, evaluated_on=evaluated_on)
        issues.extend(composition.review_blockers)
    ordered = tuple(
        sorted(
            set(issues),
            key=lambda i: (
                STAGES_V3.index(i.stage),
                i.field,
                i.code,
                i.question_id or "",
            ),
        )
    )
    return EipdResolutionReviewPrerequisitesV3(
        request.decision, ordered, metadata, composition
    )
