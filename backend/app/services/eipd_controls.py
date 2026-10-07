"""Composicion pura §74: diagnostico compartido, sin habilitar gates."""

from dataclasses import dataclass, fields
from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, StrictBool, StrictInt, model_validator

from app.schemas.licitud import (
    EipdResolutionAssessmentStoredV1,
    EipdResolutionReviewOut,
    EipdResolutionReviewStateOut,
    LegalAssessmentStatus,
    LegalBasis,
)
from app.services.consentimiento import evaluate_consent_assessment_v1
from app.services.contract import evaluate_contract_assessment_v1
from app.services.economic_obligations import (
    evaluate_economic_obligations_assessment_v1,
)
from app.services.eipd_policy import (
    EipdGatePolicyV1,
    EipdPolicyReadinessV1,
    EipdReviewPolicyIdentityV1,
    evaluate_eipd_policy_v1,
)
from app.services.eipd_resolution import (
    EipdResolutionApplicabilityV1,
    EipdResolutionContextV1,
    EipdResolutionDocumentReadinessV1,
    EipdResolutionIssueV1,
    derive_eipd_resolution_review_state_v1,
    evaluate_eipd_resolution_document_v1,
)
from app.services.eipd_screening_v2 import EipdReadinessV2, evaluate_eipd_screening_v2
from app.services.legal_obligation import evaluate_legal_obligation_assessment_v1
from app.services.lia import evaluate_lia_assessment_v1
from app.services.rights_defense import evaluate_rights_defense_assessment_v1


class EipdControlCompositionInputV1(BaseModel):
    """Entrada de servidor; todos los campos explicitos, incluso null."""

    model_config = ConfigDict(extra="forbid")
    organization_id: UUID
    assessment_id: UUID
    assessment_status: LegalAssessmentStatus
    assessment_schema_version: StrictInt
    rat_context_schema_version: StrictInt
    justification: str | None
    rat_context_current: StrictBool | None
    context: EipdResolutionContextV1 | None
    resolution: EipdResolutionAssessmentStoredV1 | None
    latest_review: EipdResolutionReviewOut | None


@dataclass(frozen=True)
class EipdCompositionIssueV1:
    stage: str
    field: str
    code: str
    category: Literal["incompleto", "requiere_revision"]
    question_id: str | None = None


@dataclass(frozen=True)
class OrdinaryControlReadinessV1:
    legal_basis: LegalBasis
    result: Literal["completo", "incompleto", "requiere_revision"]
    issues: tuple[EipdResolutionIssueV1, ...]
    applicability: tuple[EipdResolutionApplicabilityV1, ...]


@dataclass(frozen=True)
class ComposedReviewSnapshotV1:
    id: UUID
    organization_id: UUID
    assessment_id: UUID
    decision: Literal["continuar", "requiere_cambios", "no_continuar"]
    rationale: str
    review_reference: str
    document_hash: str
    context_hash: str
    created_by: UUID
    created_at: datetime


@dataclass(frozen=True)
class ComposedReviewStateV1:
    review_status: Literal["sin_revision", "vigente", "obsoleta"]
    latest_review: ComposedReviewSnapshotV1 | None


@dataclass(frozen=True)
class EipdControlCompositionV1:
    preparation_result: Literal["preparado", "incompleto", "requiere_revision"]
    ordinary: OrdinaryControlReadinessV1 | None
    detection_v2: EipdReadinessV2
    resolution: EipdResolutionDocumentReadinessV1
    review_state: ComposedReviewStateV1
    preparation_issues: tuple[EipdCompositionIssueV1, ...]
    review_blockers: tuple[EipdCompositionIssueV1, ...]
    confirmation_blockers: tuple[EipdCompositionIssueV1, ...]


class EipdControlCompositionInputV2(BaseModel):
    model_config = ConfigDict(extra="forbid")
    assessment: EipdControlCompositionInputV1
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
class EipdControlCompositionV2(EipdControlCompositionV1):
    policy: EipdPolicyReadinessV1
    review_policy_status: Literal[
        "sin_revision", "sin_identidad", "vigente", "obsoleta"
    ]

    @property
    def evaluation_version(self):
        return 2


def compose_eipd_controls_v2(value, *, evaluated_on: date):
    raw = value.model_dump(mode="python") if isinstance(value, BaseModel) else value
    data = EipdControlCompositionInputV2.model_validate(raw)
    base, policy, status = _compose_eipd_controls(
        data.assessment,
        evaluated_on=evaluated_on,
        policy_context=(data.policy, data.latest_review_policy),
    )
    return EipdControlCompositionV2(
        **{f.name: getattr(base, f.name) for f in fields(base)},
        policy=policy,
        review_policy_status=status,
    )


ORDINARY_EVALUATORS = {
    "consentimiento_art12": ("consent_assessment", evaluate_consent_assessment_v1),
    "contrato_precontractual_art13c": (
        "contract_assessment",
        evaluate_contract_assessment_v1,
    ),
    "obligacion_legal_art13b": (
        "legal_obligation_assessment",
        evaluate_legal_obligation_assessment_v1,
    ),
    "interes_legitimo_art13d": ("lia_assessment", evaluate_lia_assessment_v1),
    "defensa_derechos_art13e": (
        "rights_defense_assessment",
        evaluate_rights_defense_assessment_v1,
    ),
    "obligaciones_economicas_art13a": (
        "economic_obligations_assessment",
        evaluate_economic_obligations_assessment_v1,
    ),
}
STAGES = (
    "state",
    "rat",
    "ordinary",
    "frontier",
    "detection",
    "resolution",
    "sources",
    "activation",
    "review",
)


def compose_eipd_controls_v1(value, *, evaluated_on: date) -> EipdControlCompositionV1:
    """Calcula cada etapa sin autoridad, reloj normativo, DB ni escritura.

    Fuentes/aceptacion pendientes son barreras de producto explicitas. Registro
    negativo conserva prerequisitos propios §67; no usar esta composicion para
    exigirle preparacion completa. Revision positiva no exige evento positivo previo.
    """
    return _compose_eipd_controls(value, evaluated_on=evaluated_on)[0]


def _compose_eipd_controls(value, *, evaluated_on: date, policy_context=None):
    if type(evaluated_on) is not date:
        raise ValueError("evaluated_on exige date explicita")
    # Modo python conserva bool invalidos en StrictInt: JSON los serializa como 1.
    raw = value.model_dump(mode="python") if isinstance(value, BaseModel) else value
    data = EipdControlCompositionInputV1.model_validate(raw)
    issues = []

    def issue(stage, field, code, category="incompleto", question_id=None):
        issues.append(EipdCompositionIssueV1(stage, field, code, category, question_id))

    def add(stage, items, prefix=""):
        for item in items:
            issue(
                stage, prefix + item.field, item.code, item.category, item.question_id
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
    detection = evaluate_eipd_screening_v2(ctx)
    add("frontier", detection.frontier.issues)
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
    resolution = evaluate_eipd_resolution_document_v1(
        data.resolution, ctx, evaluated_on=evaluated_on
    )
    add("resolution", resolution.issues)
    prepared_issues = tuple(
        sorted(
            set(issues),
            key=lambda i: (STAGES.index(i.stage), i.field, i.code, i.question_id or ""),
        )
    )
    preparation = (
        "requiere_revision"
        if any(i.category == "requiere_revision" for i in prepared_issues)
        else "incompleto" if prepared_issues else "preparado"
    )
    policy = None
    review_policy_status = "sin_revision"
    if policy_context is None:
        issue(
            "sources",
            "official_sources",
            "fuentes_oficiales_no_verificadas",
            "requiere_revision",
        )
        issue("activation", "eipd_gate", "gate_eipd_no_habilitado", "requiere_revision")
    else:
        policy = evaluate_eipd_policy_v1(
            policy_context[0], route=detection.frontier.route, evaluated_on=evaluated_on
        )
        for item in policy.issues:
            issue(item.stage, item.field, item.code, item.category)
    common = tuple(
        sorted(
            set(issues),
            key=lambda i: (STAGES.index(i.stage), i.field, i.code, i.question_id or ""),
        )
    )
    state = derive_eipd_resolution_review_state_v1(
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
    if policy_context is not None and data.latest_review is not None:
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
            key=lambda i: (STAGES.index(i.stage), i.field, i.code, i.question_id or ""),
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
    result = EipdControlCompositionV1(
        preparation,
        ordinary,
        detection,
        resolution,
        frozen_state,
        prepared_issues,
        common,
        confirmation,
    )
    return result, policy, review_policy_status
