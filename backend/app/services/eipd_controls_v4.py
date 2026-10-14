"""Composicion sucesora de representacion, con evaluadores historicos intactos."""

from dataclasses import dataclass
from datetime import date
from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from app.schemas.eipd_review_metadata import EipdReviewContextMetadataV2
from app.schemas.licitud import (
    EipdResolutionAssessmentStoredV1,
    EipdResolutionAssessmentStoredV2,
    EipdResolutionAssessmentStoredV3,
)
from app.services.eipd_controls import (
    ComposedReviewStateV1,
    EipdCompositionIssueV1,
    OrdinaryControlReadinessV1,
    _compose_eipd_controls,
)
from app.services.eipd_controls_v3 import (
    EipdAssessmentInputV3,
    EipdControlCompositionInputV3,
    _compose_v3,
)
from app.services.eipd_policy import EipdPolicyReadinessV1
from app.services.eipd_representation import compose_eipd_representation_v1
from app.services.eipd_resolution import EipdResolutionContextV1
from app.services.eipd_resolution_binding_v2 import EipdResolutionContextV2
from app.services.eipd_resolution_binding_v3 import EipdResolutionContextV3
from app.services.eipd_resolution_readiness_v2 import (
    ResolutionReadinessVersioned,
    derive_eipd_resolution_review_state_versioned,
    evaluate_eipd_resolution_document_versioned,
)
from app.services.eipd_screening_v2 import EipdReadinessV2
from app.services.eipd_screening_v3 import EipdReadinessV3
from app.services.sensitive_representation import SensitiveRepresentationReadinessV1


class EipdAssessmentInputV4(EipdAssessmentInputV3):
    treatment_id: UUID
    context: EipdResolutionContextV3 | None
    resolution: (
        EipdResolutionAssessmentStoredV1
        | EipdResolutionAssessmentStoredV2
        | EipdResolutionAssessmentStoredV3
        | None
    )


class EipdControlCompositionInputV4(EipdControlCompositionInputV3):
    assessment: EipdAssessmentInputV4


@dataclass(frozen=True)
class EipdControlCompositionV4:
    preparation_result: Literal["requiere_revision"]
    ordinary: OrdinaryControlReadinessV1 | None
    representation: SensitiveRepresentationReadinessV1 | None
    detection: EipdReadinessV2 | EipdReadinessV3
    resolution: ResolutionReadinessVersioned
    review_state: ComposedReviewStateV1
    preparation_issues: tuple[EipdCompositionIssueV1, ...]
    review_blockers: tuple[EipdCompositionIssueV1, ...]
    confirmation_blockers: tuple[EipdCompositionIssueV1, ...]
    policy: EipdPolicyReadinessV1
    review_policy_status: Literal[
        "sin_revision", "sin_identidad", "vigente", "obsoleta"
    ]
    context_metadata: EipdReviewContextMetadataV2 | None

    @property
    def evaluation_version(self) -> Literal[4]:
        return 4

    @property
    def authorizes_action(self) -> Literal[False]:
        return False

    @property
    def can_confirm(self) -> Literal[False]:
        return False


def compose_eipd_controls_v4(value, *, evaluated_on: date):
    raw = value.model_dump(mode="python") if isinstance(value, BaseModel) else value
    data = EipdControlCompositionInputV4.model_validate(raw)
    assessment = data.assessment
    ctx = assessment.context
    joint = (
        compose_eipd_representation_v1(
            dict(
                organization_id=assessment.organization_id,
                treatment_id=assessment.treatment_id,
                assessment_id=assessment.assessment_id,
                context=ctx,
                resolution=assessment.resolution,
            ),
            evaluated_on=evaluated_on,
        )
        if ctx is not None
        else None
    )
    research_route = ctx is not None and (
        ctx.research_assessment is not None
        or (
            ctx.special_conditions is not None
            and (
                any(
                    c.regime_id == "investigacion_art16quinquies"
                    for c in ctx.special_conditions.conditions
                )
                or any(
                    d.question_id
                    == "fines_historicos_estadisticos_cientificos_investigacion"
                    and d.answer == "si"
                    for d in ctx.special_conditions.declarations
                )
            )
        )
    )
    model = EipdResolutionContextV2 if research_route else EipdResolutionContextV1
    screening_context = None
    if ctx is not None:
        material = {
            k: v
            for k, v in ctx.model_dump(mode="python").items()
            if k in model.model_fields
        }
        if research_route:
            material["context_schema_version"] = 2
        screening_context = model.model_validate(material)

    def evaluate_resolution(document, context, *, evaluated_on):
        return (
            joint.resolution
            if joint is not None
            else evaluate_eipd_resolution_document_versioned(
                document, context, evaluated_on=evaluated_on
            )
        )

    compose = _compose_v3 if research_route else _compose_eipd_controls
    base, policy, policy_status = compose(
        assessment,
        evaluated_on=evaluated_on,
        policy_context=(data.policy, data.latest_review_policy),
        input_model=EipdAssessmentInputV4,
        screening_context=screening_context,
        resolution_evaluator=evaluate_resolution,
        review_deriver=derive_eipd_resolution_review_state_versioned,
    )
    barrier = EipdCompositionIssueV1(
        "activation",
        "policy.routes",
        "politica_representacion_no_implementada",
        "requiere_revision",
    )

    def blocked(items):
        return tuple(
            sorted(
                set((*items, barrier)),
                key=lambda i: (i.stage, i.field, i.code, i.question_id or ""),
            )
        )

    return EipdControlCompositionV4(
        "requiere_revision",
        base.ordinary,
        joint.representation if joint else None,
        base.detection_v3 if research_route else base.detection_v2,
        base.resolution,
        base.review_state,
        blocked(base.preparation_issues),
        blocked(base.review_blockers),
        blocked(base.confirmation_blockers),
        policy,
        policy_status,
        joint.context_metadata if joint else None,
    )
