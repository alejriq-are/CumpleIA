"""Historial sucesor inmutable; no concede permisos EIPD."""

from fastapi import HTTPException
from sqlalchemy import func, select

from app.core.config import get_settings
from app.db.child_eipd import EipdChildResolution, EipdChildReview
from app.db.models import LegalAssessment, LegalAssessmentSeries
from app.schemas.eipd_child_persistence import (
    ChildNegativePolicyV1,
    ChildPolicyOutV1,
    ChildResolutionOutV4,
    ChildReviewMetadataV3,
    ChildReviewOutV4,
)
from app.services.child_adolescent_binding import (
    evaluate_child_adolescent_association_v1,
)
from app.services.eipd_child import EipdChildContextV4
from app.services.eipd_policy import build_eipd_review_policy_metadata_v1
from app.services.research_binding import digest


def conflict(code):
    raise HTTPException(409, detail={"code": code})


async def selected_policy(db):
    from app.services import licitud

    policy = ChildNegativePolicyV1(
        global_policy_identity=build_eipd_review_policy_metadata_v1(
            await licitud._selected_disabled_eipd_policy_v1(db)
        )
    )
    return ChildPolicyOutV1(
        policy=policy,
        policy_hash=digest(
            "cumpleia.eipd.child.policy.v1", policy.model_dump(mode="json")
        ),
    )


async def locked_context(db, org, tid, aid):
    from app.services import licitud

    if get_settings().environment not in ("development", "test"):
        conflict("infancia_escritura_solo_desarrollo")
    draft = await licitud.get_legal_assessment_draft_v1(db, org, tid, aid)
    try:
        await licitud.resolve_eipd_policy_snapshot_for_transaction_v1(db)
    except ValueError:
        conflict("politica_eipd_no_disponible")
    policy = await selected_policy(db)
    series = await db.scalar(
        select(LegalAssessmentSeries)
        .where(
            LegalAssessmentSeries.id == draft.series_id,
            LegalAssessmentSeries.organization_id == org,
            LegalAssessmentSeries.treatment_id == tid,
        )
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    if series is None:
        conflict("serie_no_disponible")
    draft = await db.scalar(
        select(LegalAssessment)
        .where(
            LegalAssessment.id == aid,
            LegalAssessment.series_id == series.id,
            LegalAssessment.organization_id == org,
            LegalAssessment.treatment_id == tid,
        )
        .execution_options(populate_existing=True)
    )
    if draft is None or draft.status != "borrador":
        conflict("evaluacion_no_editable")
    bundle = await licitud.build_rat_context_bundle_from_m2_v1(
        db,
        org,
        tid,
        purpose_key=series.purpose_key,
        scope=licitud._scope_from_snapshot_v1(draft.rat_context_snapshot),
    )
    if licitud.build_rat_context_hash_v1(bundle.canonical) != draft.rat_context_hash:
        conflict("infancia_contexto_rat_obsoleto")
    if (
        draft.child_adolescent_assessment is None
        or evaluate_child_adolescent_association_v1(
            draft.child_adolescent_assessment,
            licitud._child_adolescent_context_v1(draft, bundle.snapshot),
        ).result
        != "vigente"
    ):
        conflict("infancia_asociacion_no_vigente")
    previous = licitud.build_eipd_resolution_context_from_assessment_v3(
        draft, bundle.snapshot
    )
    context = EipdChildContextV4.model_validate(
        {
            **previous.model_dump(mode="python"),
            "context_schema_version": 4,
            "organization_id": org,
            "treatment_id": tid,
            "assessment_id": aid,
            "child_adolescent_assessment": draft.child_adolescent_assessment,
        }
    )
    return context, policy


def context_hash(context):
    return digest("cumpleia.eipd.child.context.v4", context.model_dump(mode="json"))


def child_hash(context):
    return digest(
        "cumpleia.eipd.child.material.v4",
        context.child_adolescent_assessment.model_dump(mode="json"),
    )


def resolution_out(row):
    context = EipdChildContextV4.model_validate(row.context_snapshot)
    out = ChildResolutionOutV4.model_validate(row)
    if (context.organization_id, context.treatment_id, context.assessment_id) != (
        row.organization_id,
        row.treatment_id,
        row.assessment_id,
    ) or context.child_adolescent_assessment is None:
        conflict("infancia_historial_invalido")
    if (
        row.context_hash != context_hash(context)
        or row.child_material_hash != child_hash(context)
        or row.document_hash
        != digest(
            "cumpleia.eipd.child.document.v4", out.document.model_dump(mode="json")
        )
    ):
        conflict("infancia_historial_invalido")
    return out


def review_out(row):
    out = ChildReviewOutV4.model_validate(row)
    expected = ChildReviewMetadataV3(
        document_hash=row.document_hash,
        context_hash=row.context_hash,
        child_material_hash=row.child_material_hash,
        policy_hash=row.policy_hash,
    )
    if out.review_context_metadata != expected or row.policy_hash != digest(
        "cumpleia.eipd.child.policy.v1", out.policy_snapshot.model_dump(mode="json")
    ):
        conflict("infancia_historial_invalido")
    return out


async def create_resolution(db, org, tid, aid, actor, payload):
    context, _ = await locked_context(db, org, tid, aid)
    version = (
        await db.scalar(
            select(func.max(EipdChildResolution.version)).where(
                EipdChildResolution.assessment_id == aid,
                EipdChildResolution.organization_id == org,
            )
        )
    ) or 0
    row = EipdChildResolution(
        organization_id=org,
        treatment_id=tid,
        assessment_id=aid,
        version=version + 1,
        data_kind=payload.data_kind,
        document=payload.document.model_dump(mode="json"),
        context_snapshot=context.model_dump(mode="json"),
        context_hash=context_hash(context),
        child_material_hash=child_hash(context),
        document_hash=digest(
            "cumpleia.eipd.child.document.v4", payload.document.model_dump(mode="json")
        ),
        created_by=actor,
    )
    db.add(row)
    await db.flush()
    return resolution_out(row)


async def get_resolution(db, org, tid, aid, rid):
    from app.services import licitud

    await licitud.get_legal_assessment_v1(db, org, tid, aid)
    row = await db.scalar(
        select(EipdChildResolution).where(
            EipdChildResolution.id == rid,
            EipdChildResolution.organization_id == org,
            EipdChildResolution.treatment_id == tid,
            EipdChildResolution.assessment_id == aid,
        )
    )
    if row is None:
        raise HTTPException(404, detail="Resolucion de infancia no encontrada")
    resolution_out(row)
    return row


async def list_resolutions(db, org, tid, aid):
    from app.services import licitud

    await licitud.get_legal_assessment_v1(db, org, tid, aid)
    rows = await db.scalars(
        select(EipdChildResolution)
        .where(
            EipdChildResolution.organization_id == org,
            EipdChildResolution.treatment_id == tid,
            EipdChildResolution.assessment_id == aid,
        )
        .order_by(EipdChildResolution.version)
    )
    return [resolution_out(r) for r in rows]


async def create_review(db, org, tid, aid, rid, actor, payload):
    context, policy = await locked_context(db, org, tid, aid)
    resolution = await get_resolution(db, org, tid, aid, rid)
    if resolution.context_hash != context_hash(
        context
    ) or resolution.child_material_hash != child_hash(context):
        conflict("infancia_resolucion_obsoleta")
    metadata = ChildReviewMetadataV3(
        document_hash=resolution.document_hash,
        context_hash=resolution.context_hash,
        child_material_hash=resolution.child_material_hash,
        policy_hash=policy.policy_hash,
    )
    row = EipdChildReview(
        organization_id=org,
        treatment_id=tid,
        assessment_id=aid,
        resolution_id=rid,
        decision=payload.decision,
        data_kind=payload.data_kind,
        rationale=payload.rationale,
        review_reference=payload.review_reference,
        document_hash=resolution.document_hash,
        context_hash=resolution.context_hash,
        child_material_hash=resolution.child_material_hash,
        policy_snapshot=policy.policy.model_dump(mode="json"),
        policy_hash=policy.policy_hash,
        review_context_metadata=metadata.model_dump(mode="json"),
        created_by=actor,
    )
    db.add(row)
    await db.flush()
    return review_out(row)


async def list_reviews(db, org, tid, aid, rid):
    await get_resolution(db, org, tid, aid, rid)
    rows = await db.scalars(
        select(EipdChildReview)
        .where(
            EipdChildReview.resolution_id == rid,
            EipdChildReview.organization_id == org,
            EipdChildReview.treatment_id == tid,
            EipdChildReview.assessment_id == aid,
        )
        .order_by(EipdChildReview.created_at, EipdChildReview.id)
    )
    return [review_out(r) for r in rows]


async def get_review(db, org, tid, aid, rid, event_id):
    await get_resolution(db, org, tid, aid, rid)
    row = await db.scalar(
        select(EipdChildReview).where(
            EipdChildReview.id == event_id,
            EipdChildReview.resolution_id == rid,
            EipdChildReview.organization_id == org,
            EipdChildReview.treatment_id == tid,
            EipdChildReview.assessment_id == aid,
        )
    )
    if row is None:
        raise HTTPException(404, detail="Revision de infancia no encontrada")
    return review_out(row)
