"""Composicion V3 pura de investigacion; diagnosticos sin autoridad de confirmar."""

from dataclasses import dataclass
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, model_validator

from app.schemas.licitud import (
    EipdResolutionAssessmentStoredV1,
    EipdResolutionAssessmentStoredV2,
    EipdResolutionReviewStateOut,
)
from app.services.eipd_controls import (
    ORDINARY_EVALUATORS,
    ComposedReviewSnapshotV1,
    ComposedReviewStateV1,
    EipdCompositionIssueV1,
    EipdControlCompositionInputV1,
    OrdinaryControlReadinessV1,
)
from app.services.eipd_policy import (
    EipdGatePolicyV1,
    EipdPolicyReadinessV1,
    EipdReviewPolicyIdentityV1,
    evaluate_eipd_policy_v1,
)
from app.services.eipd_resolution import (
    EipdResolutionApplicabilityV1,
    EipdResolutionIssueV1,
)
from app.services.eipd_resolution_binding_v2 import EipdResolutionContextV2
from app.services.eipd_resolution_readiness_v2 import (
    ResolutionReadinessVersioned,
    derive_eipd_resolution_review_state_versioned,
    evaluate_eipd_resolution_document_versioned,
)
from app.services.eipd_screening_v3 import EipdReadinessV3, evaluate_eipd_screening_v3


class EipdAssessmentInputV3(EipdControlCompositionInputV1):
    model_config = ConfigDict(extra="forbid", revalidate_instances="always")
    context: EipdResolutionContextV2 | None
    resolution: (
        EipdResolutionAssessmentStoredV1 | EipdResolutionAssessmentStoredV2 | None
    )


class EipdControlCompositionInputV3(BaseModel):
    model_config = ConfigDict(extra="forbid", revalidate_instances="always")
    assessment: EipdAssessmentInputV3
    policy: EipdGatePolicyV1 | None
    latest_review_policy: EipdReviewPolicyIdentityV1 | None

    @model_validator(mode="after")
    def metadata_requires_review(self):
        if (
            self.latest_review_policy is not None
            and self.assessment.latest_review is None
        ):
            raise ValueError("Identidad de politica sin evento humano")
        return self


@dataclass(frozen=True)
class EipdControlCompositionV3:
    preparation_result: Literal["preparado", "incompleto", "requiere_revision"]
    ordinary: OrdinaryControlReadinessV1 | None
    detection_v3: EipdReadinessV3
    resolution: ResolutionReadinessVersioned
    review_state: ComposedReviewStateV1
    preparation_issues: tuple[EipdCompositionIssueV1, ...]
    review_blockers: tuple[EipdCompositionIssueV1, ...]
    confirmation_blockers: tuple[EipdCompositionIssueV1, ...]
    policy: EipdPolicyReadinessV1
    review_policy_status: Literal[
        "sin_revision", "sin_identidad", "vigente", "obsoleta"
    ]

    @property
    def evaluation_version(self) -> Literal[3]:
        return 3

    @property
    def can_confirm(self) -> Literal[False]:
        return False


STAGES_V3 = (
    "state",
    "rat",
    "ordinary",
    "research",
    "frontier",
    "detection",
    "resolution",
    "sources",
    "activation",
    "review",
)


def compose_eipd_controls_v3(value, *, evaluated_on: date) -> EipdControlCompositionV3:
    raw = value.model_dump(mode="python") if isinstance(value, BaseModel) else value
    data = EipdControlCompositionInputV3.model_validate(raw)
    return _compose_v3(
        data.assessment,
        evaluated_on=evaluated_on,
        policy_context=(data.policy, data.latest_review_policy),
    )[0]


def _compose_v3(value, *, evaluated_on: date, policy_context):
    if type(evaluated_on) is not date:
        raise ValueError("evaluated_on exige date explicita")
    # Modo python conserva bool invalidos en StrictInt: JSON los serializa como 1.
    raw = value.model_dump(mode="python") if isinstance(value, BaseModel) else value
    data = EipdAssessmentInputV3.model_validate(raw)
    issues = []

    def issue(stage, field, code, category="incompleto", question_id=None):
        issues.append(EipdCompositionIssueV1(stage, field, code, category, question_id))

    def add(stage, items, prefix=""):
        for item in items:
            issue(
                stage,
                prefix + item.field,
                item.code,
                item.category,
                getattr(item, "question_id", None),
            )

    if data.assessment_status != "borrador":
        issue(
            "state", "assessment_status", "evaluacion_no_borrador", "requiere_revision"
        )
    for field in ("assessment_schema_version", "rat_context_schema_version"):
        if getattr(data, field) != 1:
            issue("state", field, "version_no_admitida", "requiere_revision")
    if not data.justification or not data.justification.strip():
        issue("state", "justification", "justificacion_ausente")
    ctx = data.context
    if ctx is None:
        issue("rat", "rat_context_snapshot", "contexto_rat_no_disponible")
    if data.rat_context_current is None:
        issue("rat", "rat_context_current", "vigencia_rat_no_resuelta")
    elif data.rat_context_current is False:
        issue(
            "rat",
            "rat_context_current",
            "contexto_rat_desactualizado",
            "requiere_revision",
        )
    ordinary = None
    if ctx is not None:
        rat = ctx.rat_context_snapshot
        if not rat.data_categories or not rat.data_subjects:
            issue("rat", "rat_context_snapshot", "alcance_ausente")
        if ctx.legal_basis is None:
            issue("ordinary", "legal_basis", "base_ausente")
        else:
            field, evaluator = ORDINARY_EVALUATORS[ctx.legal_basis]
            document = getattr(ctx, field)
            result = (
                evaluator(document)
                if ctx.legal_basis == "consentimiento_art12"
                else evaluator(document, rat)
            )
            ordinary = OrdinaryControlReadinessV1(
                ctx.legal_basis,
                result.result,
                tuple(
                    EipdResolutionIssueV1(
                        i.field, i.code, i.category, getattr(i, "question_id", None)
                    )
                    for i in result.issues
                ),
                tuple(
                    EipdResolutionApplicabilityV1(
                        getattr(a, "field", None) or "answers." + a.question_id,
                        a.applicability,
                    )
                    for a in result.applicability
                ),
            )
            add("ordinary", ordinary.issues, field + ".")
    detection = evaluate_eipd_screening_v3(ctx)
    add("frontier", detection.frontier.issues)
    frontier = detection.frontier
    if frontier.research is not None:
        add("research", frontier.research.issues, "research_assessment.")
    if frontier.research_association is not None:
        for code in frontier.research_association.issues:
            issue(
                "research",
                "research_assessment.context_binding",
                code,
                "requiere_revision",
            )
    issue(
        "research",
        "research_assessment",
        "investigacion_confirmacion_bloqueada",
        "requiere_revision",
    )
    for item in detection.issues:
        issue("detection", item.field, item.code, "requiere_revision", item.question_id)
    if detection.result != "requiere_eipd":
        issue(
            "detection",
            "eipd_screening",
            "deteccion_fuera_frontera",
            (
                "requiere_revision"
                if detection.frontier.result == "requiere_revision"
                else "incompleto"
            ),
        )
    resolution = evaluate_eipd_resolution_document_versioned(
        data.resolution, ctx, evaluated_on=evaluated_on
    )
    add("resolution", resolution.issues)
    prepared_issues = tuple(
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
    preparation = (
        "requiere_revision"
        if any(i.category == "requiere_revision" for i in prepared_issues)
        else "incompleto" if prepared_issues else "preparado"
    )
    policy = None
    review_policy_status = "sin_revision"
    # Politica V1 no representa investigacion. Evaluar barreras generales sin
    # atribuir cobertura a una ruta historica ni ampliar silenciosamente V1.
    policy = evaluate_eipd_policy_v1(
        policy_context[0], route="sin_resolver", evaluated_on=evaluated_on
    )
    issue(
        "activation",
        "policy.routes",
        "politica_investigacion_no_implementada",
        "requiere_revision",
    )
    for item in policy.issues:
        issue(item.stage, item.field, item.code, item.category)
    common = tuple(
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
    state = derive_eipd_resolution_review_state_versioned(
        data.resolution, ctx, data.latest_review
    )
    if data.latest_review is None:
        issue("review", "latest_review", "revision_ausente")
    else:
        review = data.latest_review
        if (
            review.organization_id != data.organization_id
            or review.assessment_id != data.assessment_id
        ):
            issue(
                "review",
                "latest_review",
                "revision_otro_expediente",
                "requiere_revision",
            )
            state = EipdResolutionReviewStateOut(
                review_status="obsoleta", latest_review=review
            )
        if state.review_status != "vigente":
            issue("review", "latest_review", "revision_obsoleta", "requiere_revision")
        if review.decision != "continuar":
            issue(
                "review",
                "latest_review.decision",
                "decision_no_continuar",
                "requiere_revision",
            )
    if data.latest_review is not None:
        identity = policy_context[1]
        if identity is None:
            review_policy_status = "sin_identidad"
            issue(
                "review",
                "latest_review.policy",
                "revision_sin_politica",
                "requiere_revision",
            )
        elif (
            identity.review_id != data.latest_review.id
            or identity.policy_version != policy.policy_version
            or identity.policy_reference != policy.policy_reference
            or identity.policy_hash != policy.policy_hash
        ):
            review_policy_status = "obsoleta"
            issue(
                "review",
                "latest_review.policy",
                "politica_revision_obsoleta",
                "requiere_revision",
            )
        else:
            review_policy_status = "vigente"
        # Estado documental se conserva separado de vigencia de politica.
    confirmation = tuple(
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
    frozen_state = ComposedReviewStateV1(
        state.review_status,
        (
            ComposedReviewSnapshotV1(**state.latest_review.model_dump())
            if state.latest_review
            else None
        ),
    )
    result = EipdControlCompositionV3(
        preparation,
        ordinary,
        detection,
        resolution,
        frozen_state,
        prepared_issues,
        common,
        confirmation,
        policy,
        review_policy_status,
    )
    return result, policy, review_policy_status
