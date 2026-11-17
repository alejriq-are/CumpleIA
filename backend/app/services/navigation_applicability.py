"""Versioned navigation determinations. Does not mutate assessments or legal gates."""

from app.db.assessment_support import AssessmentSupportRecord as Record
from app.services import assessment_support as support
from app.services import licitud
from app.services.organization_acceptance import member, series_lock


def context_hash(row):
    return support.digest(
        {
            "organization_id": row.organization_id,
            "treatment_id": row.treatment_id,
            "assessment_id": row.id,
            "rat_context_snapshot": row.rat_context_snapshot,
        }
    )


async def snapshot(db, org, tid, aid):
    support.gate()
    row = await licitud.get_legal_assessment_v1(db, org, tid, aid)
    history = [
        r for r in await support.records(db, org, tid, aid) if r.kind == "applicability"
    ]
    current = history[-1] if history else None
    digest = context_hash(row)
    return dict(
        organization_id=str(org),
        treatment_id=str(tid),
        assessment_id=str(aid),
        context_hash=digest,
        revision=current.revision if current else 0,
        current=current is not None and current.document_hash == digest,
        editable=row.status == "borrador",
        eipd=current.payload["eipd"] if current else dict(state="pendiente", reason=""),
        infancia=(
            current.payload["infancia"]
            if current
            else dict(state="pendiente", reason="")
        ),
        history=[
            dict(
                revision=r.revision,
                created_by=str(r.created_by),
                created_at=r.created_at.isoformat(),
                context_hash=r.document_hash,
                eipd=r.payload["eipd"],
                infancia=r.payload["infancia"],
            )
            for r in history
        ],
        can_confirm=False,
        activation="deshabilitada",
    )


async def save(db, org, tid, aid, actor, payload):
    support.gate()
    await member(db, org, actor)
    await series_lock(db, org, tid, aid)
    row = await licitud.get_legal_assessment_v1(db, org, tid, aid)
    await db.refresh(row)
    if row.status != "borrador":
        support.conflict("Evaluación de solo lectura")
    history = await support.records(db, org, tid, aid)
    input_hash = support.digest(payload.model_dump(mode="json"))
    previous = next((r for r in history if r.request_id == payload.request_id), None)
    if previous:
        if (
            previous.kind != "applicability"
            or previous.payload.get("input_hash") != input_hash
        ):
            support.conflict("Solicitud ya utilizada con otro contenido")
        return await snapshot(db, org, tid, aid)
    revision = max(
        (r.revision for r in history if r.kind == "applicability"), default=0
    )
    if payload.expected_revision != revision or payload.context_hash != context_hash(
        row
    ):
        support.conflict(
            "Cambio concurrente o de alcance: vuelve a consultar antes de guardar"
        )
    # No adult/child fixture rule: real RAT context is reviewed by the user.
    db.add(
        Record(
            organization_id=org,
            treatment_id=tid,
            assessment_id=aid,
            created_by=actor,
            request_id=payload.request_id,
            kind="applicability",
            revision=revision + 1,
            data_kind="ficticios",
            document_hash=context_hash(row),
            payload=dict(
                eipd=payload.eipd.model_dump(),
                infancia=payload.infancia.model_dump(),
                input_hash=input_hash,
            ),
        )
    )
    await db.flush()
    return await snapshot(db, org, tid, aid)
