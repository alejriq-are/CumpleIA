"""Requisitos documentales sucesores puros; ninguna accion de revision habilitada."""

from dataclasses import dataclass
from datetime import date
from typing import Literal

from pydantic import BaseModel, TypeAdapter

from app.schemas.eipd_review_metadata import EipdReviewContextMetadataV2
from app.schemas.licitud import EipdResolutionReviewIn
from app.services.eipd_controls import EipdCompositionIssueV1
from app.services.eipd_controls_v4 import (
    EipdControlCompositionInputV4,
    EipdControlCompositionV4,
    compose_eipd_controls_v4,
)

Decision = Literal["continuar", "requiere_cambios", "no_continuar"]


@dataclass(frozen=True)
class EipdReviewDocumentaryPrerequisitesV4:
    decision: Decision
    documentary_issues: tuple[EipdCompositionIssueV1, ...]
    current_context_metadata: EipdReviewContextMetadataV2 | None
    composition: EipdControlCompositionV4

    @property
    def evaluation_version(self) -> Literal[4]:
        return 4

    @property
    def documentary_prerequisites_met(self) -> bool:
        return not self.documentary_issues

    @property
    def prerequisites_met(self) -> Literal[False]:
        return False

    @property
    def authorizes_action(self) -> Literal[False]:
        return False

    @property
    def can_confirm(self) -> Literal[False]:
        return False


def evaluate_eipd_resolution_review_documentary_prerequisites_v4(
    value, review, *, evaluated_on: date
):
    """Valida solicitud humana sin aceptar identidad, actor ni hashes del cliente."""
    raw = review.model_dump(mode="python") if isinstance(review, BaseModel) else review
    request = EipdResolutionReviewIn.model_validate(raw)
    return evaluate_eipd_review_documentary_decision_v4(
        value, request.decision, evaluated_on=evaluated_on
    )


def evaluate_eipd_review_documentary_decision_v4(
    value, decision, *, evaluated_on: date
):
    """Negativas identifican material actual sin exigir completitud del contenido.

    Este resultado interno no es contexto de accion ni permiso. El escritor debe
    autorizar, releer bajo locks y aplicar la politica propia del registro negativo.
    """
    if type(evaluated_on) is not date:
        raise ValueError("evaluated_on exige date explicita")
    decision = TypeAdapter(Decision).validate_python(decision)
    raw = value.model_dump(mode="python") if isinstance(value, BaseModel) else value
    data = EipdControlCompositionInputV4.model_validate(raw)
    composition = compose_eipd_controls_v4(data, evaluated_on=evaluated_on)
    issues = []

    def block(stage, field, code):
        issues.append(
            EipdCompositionIssueV1(stage, field, code, "requiere_revision", None)
        )

    a = data.assessment
    if a.assessment_status != "borrador":
        block("state", "assessment_status", "evaluacion_no_borrador")
    for field in ("assessment_schema_version", "rat_context_schema_version"):
        if getattr(a, field) != 1:
            block("state", field, "version_no_admitida")
    if a.rat_context_current is not True:
        block("rat", "rat_context_current", "contexto_rat_no_vigente")
    if a.resolution is None or a.resolution.context_binding is None:
        block("resolution", "context_binding", "asociacion_ausente")
    elif a.resolution.context_binding.binding_version != 3:
        block("resolution", "context_binding", "asociacion_representacion_no_cubierta")
    identity_matches = a.context is not None and not any(
        i.field == "context_binding"
        for i in (
            composition.representation.issues if composition.representation else ()
        )
    )
    if not identity_matches:
        block("review", "context", "asociacion_contexto_obsoleta")
    metadata = composition.context_metadata if identity_matches else None
    if metadata is None:
        block("review", "context_metadata", "metadatos_revision_no_disponibles")
    if decision == "continuar":
        issues.extend(composition.review_blockers)
    ordered = tuple(sorted(set(issues), key=lambda i: (i.stage, i.field, i.code)))
    return EipdReviewDocumentaryPrerequisitesV4(
        decision, ordered, metadata, composition
    )
