"""Prerequisitos puros §86; no accion, DB, permisos ni resolver activo."""

from dataclasses import dataclass
from datetime import date
from typing import Literal

from pydantic import BaseModel

from app.services.eipd_controls import (
    STAGES,
    EipdCompositionIssueV1,
    EipdControlCompositionInputV2,
    EipdControlCompositionV2,
    compose_eipd_controls_v2,
)
from app.services.eipd_resolution import _evaluate_eipd_review_partial_prerequisites


@dataclass(frozen=True)
class EipdResolutionReviewPrerequisitesV2:
    decision: Literal["continuar", "requiere_cambios", "no_continuar"]
    issues: tuple[EipdCompositionIssueV1, ...]
    composition: EipdControlCompositionV2 | None

    @property
    def evaluation_version(self):
        return 2

    @property
    def prerequisites_met(self):
        return not self.issues


def evaluate_eipd_resolution_review_prerequisites_v2(
    value, review, *, evaluated_on: date
):
    """Negativas parciales; continuar exige controles comunes, nunca evento previo.

    El caller debe autenticar/autorizar, validar versiones, resolver politica real
    y releer estado/contexto bajo lock antes de escribir. Un resultado puro sin
    motivos no reemplaza esos controles ni habilita el resolver real deshabilitado.
    """
    raw = value.model_dump(mode="python") if isinstance(value, BaseModel) else value
    data = EipdControlCompositionInputV2.model_validate(raw)
    # Segunda lectura desde python revalida incluso assessment anidado mutado.
    data = EipdControlCompositionInputV2.model_validate(data.model_dump(mode="python"))
    assessment = data.assessment
    partial, _, _ = _evaluate_eipd_review_partial_prerequisites(
        assessment.assessment_status,
        assessment.resolution,
        assessment.context,
        review,
        evaluated_on=evaluated_on,
    )
    issues = [
        EipdCompositionIssueV1(
            (
                "state"
                if i.field == "status"
                else "rat" if i.field == "rat_context_snapshot" else "resolution"
            ),
            i.field,
            i.code,
            i.category,
            i.question_id,
        )
        for i in partial.issues
    ]
    composition = None
    if partial.decision == "continuar":
        composition = compose_eipd_controls_v2(data, evaluated_on=evaluated_on)
        issues.extend(composition.review_blockers)
    ordered = tuple(
        sorted(
            set(issues),
            key=lambda i: (STAGES.index(i.stage), i.field, i.code, i.question_id or ""),
        )
    )
    return EipdResolutionReviewPrerequisitesV2(partial.decision, ordered, composition)
