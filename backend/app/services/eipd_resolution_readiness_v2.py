"""Dispatch documental puro; vigencia no autoriza revision ni confirmacion."""

from dataclasses import dataclass

from pydantic import BaseModel

from app.schemas.licitud import (
    EipdResolutionAssessmentStoredV1,
    EipdResolutionAssessmentStoredV2,
    EipdResolutionReviewOut,
    EipdResolutionReviewStateOut,
)
from app.services.eipd_resolution import (
    EipdResolutionContextV1,
    EipdResolutionIssueV1,
    _evaluate_eipd_resolution_document,
    _validated_json,
    build_eipd_resolution_document_hash_v1,
    eipd_resolution_context_is_current_v1,
)
from app.services.eipd_resolution_binding_v2 import (
    EipdResolutionContextV2,
    build_eipd_resolution_document_hash_v2,
    eipd_resolution_context_is_current_v2,
)
from app.services.research import evaluate_research_assessment_v1
from app.services.research_binding import evaluate_research_association_v1


@dataclass(frozen=True)
class ResolutionReadinessVersioned:
    result: str
    context_current: bool
    issues: tuple
    applicability: tuple
    binding_version: int | None

    @property
    def can_confirm(self):
        return False


def _materials(document, context):
    raw = (
        document.model_dump(mode="json")
        if isinstance(document, BaseModel)
        else document
    )
    binding = (raw or {}).get("context_binding")
    version = binding.get("binding_version") if binding else 1
    if version not in (1, 2):
        raise ValueError("Version de asociacion no admitida")
    model = (
        EipdResolutionAssessmentStoredV2
        if version == 2
        else EipdResolutionAssessmentStoredV1
    )
    parsed = (
        model.model_validate(_validated_json(model, document))
        if document is not None
        else None
    )
    data = (
        context.model_dump(mode="json") if isinstance(context, BaseModel) else context
    )
    extended = data is not None and (
        "research_assessment" in data or "context_schema_version" in data
    )
    ctx = (
        (
            EipdResolutionContextV2.model_validate(data)
            if extended or version == 2
            else EipdResolutionContextV1.model_validate(data)
        )
        if data is not None
        else None
    )
    # Proyeccion V1 solo para reglas historicas; su falta de cobertura es explicita.
    legacy = (
        EipdResolutionContextV1.model_validate(
            {
                k: v
                for k, v in ctx.model_dump(mode="json").items()
                if k in EipdResolutionContextV1.model_fields
            }
        )
        if isinstance(ctx, EipdResolutionContextV2)
        else ctx
    )
    return parsed, ctx, legacy, version


def evaluate_eipd_resolution_document_versioned(document, context, *, evaluated_on):
    parsed, ctx, legacy, version = _materials(document, context)
    current_context = ctx if version == 2 else legacy
    result = _evaluate_eipd_resolution_document(
        parsed,
        current_context,
        evaluated_on=evaluated_on,
        document_model=(
            EipdResolutionAssessmentStoredV2
            if version == 2
            else EipdResolutionAssessmentStoredV1
        ),
        context_model=(
            EipdResolutionContextV2 if version == 2 else EipdResolutionContextV1
        ),
        context_is_current=(
            eipd_resolution_context_is_current_v2
            if version == 2
            else eipd_resolution_context_is_current_v1
        ),
    )
    issues = list(result.issues)
    current = result.context_current
    research = getattr(ctx, "research_assessment", None)
    if research is not None:
        if version == 1:
            issues.append(
                EipdResolutionIssueV1(
                    "research_assessment",
                    "asociacion_investigacion_no_cubierta",
                    "requiere_revision",
                )
            )
            current = False
        preparation = evaluate_research_assessment_v1(
            research.assessment,
            ctx.rat_context_snapshot,
            ctx.legal_basis,
            ctx.lia_assessment,
        )
        issues.extend(
            EipdResolutionIssueV1("research_assessment." + i.field, i.code, i.category)
            for i in preparation.issues
        )
        association = evaluate_research_association_v1(
            research, ctx.rat_context_snapshot, ctx.legal_basis, ctx.lia_assessment
        )
        issues.extend(
            EipdResolutionIssueV1(
                "research_assessment.context_binding", code, "requiere_revision"
            )
            for code in association.issues
        )
    ordered = tuple(sorted(set(issues), key=lambda i: (i.field, i.code, i.category)))
    state = (
        "requiere_revision"
        if any(i.category == "requiere_revision" for i in ordered)
        else "incompleto" if ordered else "completo"
    )
    return ResolutionReadinessVersioned(
        state,
        current,
        ordered,
        result.applicability,
        version if parsed and parsed.context_binding else None,
    )


def derive_eipd_resolution_review_state_versioned(document, context, latest_review):
    parsed, ctx, legacy, version = _materials(document, context)
    if latest_review is None:
        return EipdResolutionReviewStateOut(
            review_status="sin_revision", latest_review=None
        )
    review = EipdResolutionReviewOut.model_validate(
        _validated_json(EipdResolutionReviewOut, latest_review)
    )
    current = False
    if parsed is not None and ctx is not None:
        if version == 2:
            current = eipd_resolution_context_is_current_v2(
                parsed, ctx
            ) and review.document_hash == build_eipd_resolution_document_hash_v2(parsed)
        else:
            current = (
                getattr(ctx, "research_assessment", None) is None
                and eipd_resolution_context_is_current_v1(parsed, legacy)
                and review.document_hash
                == build_eipd_resolution_document_hash_v1(parsed)
            )
        current = (
            current
            and parsed.context_binding is not None
            and review.context_hash == parsed.context_binding.context_hash
        )
    return EipdResolutionReviewStateOut(
        review_status="vigente" if current else "obsoleta", latest_review=review
    )
