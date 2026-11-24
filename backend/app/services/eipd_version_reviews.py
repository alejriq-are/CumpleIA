"""5C.1: explicit faculty and append-only conclusions on exact versions."""

from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import text

from app.services import assessment_support as support
from app.services import eipd_document_versions as versions
from app.services import licitud
from app.services.organization_acceptance import member, series_lock

DOMAIN = "cumpleia.eipd.general.review.v1"


async def rows(db, sql, params):
    return [dict(r) for r in (await db.execute(text(sql), params)).mappings()]


def scope(org, tid, aid):
    return dict(organization_id=org, treatment_id=tid, assessment_id=aid)


async def exact(db, org, tid, aid, vid):
    history = await versions.history(db, org, tid, aid)
    row = next((r for r in history if r.id == vid), None)
    if row is None:
        raise HTTPException(404, detail="Versión documental no encontrada")
    versions.output(row)  # Verify the immutable bundle before using its diagnosis.
    return row


def favorable(bundle):
    diagnostic = bundle.get("diagnostic", {})
    document = diagnostic.get("readiness", {}).get("eipd_resolution")
    return (
        diagnostic.get("rule_set") == "cumpleia.general.registration.v1"
        and isinstance(document, dict)
        and document.get("result") == "completo"
        and document.get("context_current") is True
        and document.get("issues") == []
    )


async def authorities(db, org, tid, aid):
    await licitud.get_legal_assessment_v1(db, org, tid, aid)
    return await rows(
        db,
        """SELECT * FROM eipd_review_authority_events
        WHERE organization_id=:organization_id AND treatment_id=:treatment_id
        AND assessment_id=:assessment_id ORDER BY created_at, sequence, id""",
        scope(org, tid, aid),
    )


async def designate(db, org, tid, aid, actor, payload):
    support.gate()
    await series_lock(db, org, tid, aid)
    await member(db, org, actor, manage=True)
    await member(db, org, payload.subject_id)
    if payload.action == "grant" and actor == payload.subject_id:
        raise HTTPException(403, detail="No puedes otorgarte la facultad de revisión")
    events = await authorities(db, org, tid, aid)
    last = next(
        (e for e in reversed(events) if e["subject_id"] == payload.subject_id), None
    )
    if payload.expected_sequence != (last["sequence"] if last else 0):
        support.conflict("La facultad cambió; consulta su historial")
    now = await db.scalar(text("SELECT clock_timestamp()"))
    if payload.expires_at is not None and (
        payload.action != "grant"
        or payload.expires_at.tzinfo is None
        or payload.expires_at <= now
    ):
        raise HTTPException(422, detail="Vencimiento futuro con zona horaria requerido")
    params = dict(
        **scope(org, tid, aid),
        id=uuid4(),
        created_by=actor,
        sequence=payload.expected_sequence + 1,
        **payload.model_dump(exclude={"expected_sequence"}),
    )
    return (
        await rows(
            db,
            """INSERT INTO eipd_review_authority_events
        (id, organization_id, treatment_id, assessment_id, subject_id, created_by,
         sequence, action, expires_at, reason, reference)
        VALUES (:id,:organization_id,:treatment_id,:assessment_id,:subject_id,:created_by,
         :sequence,:action,:expires_at,:reason,:reference) RETURNING *""",
            params,
        )
    )[0]


async def history(db, org, tid, aid, vid):
    await exact(db, org, tid, aid, vid)
    return await rows(
        db,
        """SELECT * FROM eipd_version_reviews
        WHERE organization_id=:organization_id AND treatment_id=:treatment_id
        AND assessment_id=:assessment_id AND version_id=:version_id ORDER BY sequence""",
        dict(**scope(org, tid, aid), version_id=vid),
    )


async def state(db, org, tid, aid, vid, actor):
    version = await exact(db, org, tid, aid, vid)
    events = await authorities(db, org, tid, aid)
    last = next((e for e in reversed(events) if e["subject_id"] == actor), None)
    now = await db.scalar(text("SELECT clock_timestamp()"))
    reason = None
    may_manage = False
    try:
        await member(db, org, actor, manage=True)
        may_manage = True
    except HTTPException:
        pass
    try:
        await member(db, org, actor)
    except HTTPException:
        reason = "Se requiere membresía habilitada para revisar"
    if (
        not last
        or last["action"] != "grant"
        or (last["expires_at"] is not None and last["expires_at"] <= now)
    ):
        reason = "Se requiere una facultad expresa y vigente para este expediente"
    if version.created_by == actor:
        reason = "No puedes revisar una versión registrada por ti"
    return dict(
        version_id=vid,
        organization_id=org,
        treatment_id=tid,
        assessment_id=aid,
        reviews=await history(db, org, tid, aid, vid),
        authority_id=last["id"] if last else None,
        blocked_reason=reason,
        can_review=reason is None,
        can_favorable=favorable(version.bundle),
        may_manage=may_manage,
        authorities=events,
    )


async def lookup(db, org, tid, aid, vid, actor, request_id):
    entries = await history(db, org, tid, aid, vid)
    found = next(
        (
            e
            for e in entries
            if e["created_by"] == actor and e["request_id"] == request_id
        ),
        None,
    )
    if found is None:
        raise HTTPException(404, detail="Solicitud de revisión no encontrada")
    return found


async def record(db, org, tid, aid, vid, actor, payload):
    support.gate()
    # Request precedes series. No policy lock: only the frozen bundle is used.
    await db.execute(
        text("SELECT pg_advisory_xact_lock(hashtextextended(:key,0))"),
        {"key": f"{DOMAIN}:{org}:{actor}:{payload.request_id}"},
    )
    await series_lock(db, org, tid, aid)
    await member(db, org, actor)
    version = await exact(db, org, tid, aid, vid)
    fingerprint = versions.digest(
        dict(
            version_id=vid,
            treatment_id=tid,
            assessment_id=aid,
            payload=payload.model_dump(mode="json"),
        )
    )
    previous = await rows(
        db,
        """SELECT * FROM eipd_version_reviews
        WHERE organization_id=:org AND created_by=:actor AND request_id=:request""",
        dict(org=org, actor=actor, request=payload.request_id),
    )
    if previous:
        if previous[0]["input_hash"] != fingerprint:
            support.conflict("Solicitud ya utilizada con otro contenido")
        return previous[0]
    current = await state(db, org, tid, aid, vid, actor)
    if not current["can_review"]:
        raise HTTPException(403, detail=current["blocked_reason"])
    if payload.authority_id != current["authority_id"]:
        support.conflict("La facultad cambió; consulta su historial")
    entries = current["reviews"]
    last = entries[-1] if entries else None
    if payload.expected_previous_id != (last["id"] if last else None):
        support.conflict("La revisión previa cambió; consulta el historial")
    if payload.outcome == "favorable" and not favorable(version.bundle):
        raise HTTPException(
            422, detail="La versión conservada no cumple los requisitos documentales"
        )
    params = dict(
        **scope(org, tid, aid),
        id=uuid4(),
        version_id=vid,
        created_by=actor,
        sequence=len(entries) + 1,
        previous_id=payload.expected_previous_id,
        input_hash=fingerprint,
        **payload.model_dump(exclude={"expected_previous_id", "data_kind"}),
    )
    return (
        await rows(
            db,
            """INSERT INTO eipd_version_reviews
        (id,organization_id,treatment_id,assessment_id,version_id,created_by,sequence,
         previous_id,request_id,outcome,reason,reference,authority_id,input_hash)
        VALUES (:id,:organization_id,:treatment_id,:assessment_id,:version_id,:created_by,
         :sequence,:previous_id,:request_id,:outcome,:reason,:reference,:authority_id,:input_hash)
        RETURNING *""",
            params,
        )
    )[0]
