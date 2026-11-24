"""Guided scope adoption with append-only before/after evidence.

A scope revision is neither a new assessment version nor an applicability decision.
Existing documents retain their original bindings and historical records.
"""

from copy import deepcopy
from datetime import UTC, datetime

from sqlalchemy import select

from app.db.assessment_support import AssessmentSupportRecord as Record
from app.db.models import LegalAssessmentSeries
from app.services import assessment_support as support
from app.services import licitud
from app.services.organization_acceptance import member, series_lock


async def preview(db, org, tid, aid, payload):
    support.gate()
    row = await licitud.get_legal_assessment_v1(db, org, tid, aid)
    series = await db.scalar(
        select(LegalAssessmentSeries).where(
            LegalAssessmentSeries.id == row.series_id,
            LegalAssessmentSeries.organization_id == org,
            LegalAssessmentSeries.treatment_id == tid,
        )
    )
    bundle = await licitud.build_rat_context_bundle_from_m2_v1(
        db,
        org,
        tid,
        purpose_key=series.purpose_key,
        scope=payload.scope,
    )
    candidate = bundle.snapshot.model_dump(mode="json")
    material = dict(
        organization_id=str(org),
        treatment_id=str(tid),
        assessment_id=str(aid),
        before=row.rat_context_snapshot,
        after=candidate,
    )
    history = [r for r in await support.records(db, org, tid, aid) if r.kind == "scope"]
    return dict(
        **material,
        review_hash=support.digest(material),
        rat_context_hash=licitud.build_rat_context_hash_v1(bundle.canonical),
        changed=material["before"] != candidate,
        editable=row.status == "borrador",
        history=[
            dict(
                revision=r.revision,
                created_by=str(r.created_by),
                created_at=r.created_at.isoformat(),
                **r.payload,
            )
            for r in history
        ],
    )


async def apply(db, org, tid, aid, actor, payload):
    support.gate()
    await member(db, org, actor)
    await series_lock(db, org, tid, aid)
    row = await licitud.get_legal_assessment_v1(db, org, tid, aid)
    await db.refresh(row)
    if row.status != "borrador":
        support.conflict("La evaluación es de solo lectura")
    records = await support.records(db, org, tid, aid)
    input_hash = support.digest(payload.model_dump(mode="json"))
    previous = next((r for r in records if r.request_id == payload.request_id), None)
    if previous:
        if previous.kind != "scope" or previous.payload.get("input_hash") != input_hash:
            support.conflict("Solicitud ya utilizada con otro contenido")
        return row
    review = await preview(db, org, tid, aid, payload)
    if review["review_hash"] != payload.review_hash:
        support.conflict(
            "El RAT o la evaluación cambiaron. Compara nuevamente antes de actualizar el alcance"
        )
    if not review["changed"]:
        support.conflict("El alcance ya coincide; no es necesario actualizarlo")
    db.add(
        Record(
            organization_id=org,
            treatment_id=tid,
            assessment_id=aid,
            created_by=actor,
            request_id=payload.request_id,
            kind="scope",
            revision=1
            + max((r.revision for r in records if r.kind == "scope"), default=0),
            data_kind="ficticios",
            document_hash=payload.review_hash,
            payload=dict(
                before=deepcopy(review["before"]),
                after=deepcopy(review["after"]),
                reason=payload.reason,
                input_hash=input_hash,
            ),
        )
    )
    row.rat_context_snapshot = review["after"]
    row.rat_context_hash = review["rat_context_hash"]
    row.purpose_snapshot = review["after"]["purpose"]
    row.updated_at = datetime.now(UTC)
    row.updated_by = actor
    await db.flush()
    return row
