"""5C.2 decisions and independent faculties for exact EIPD versions."""

from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.services import assessment_support as support
from app.services import eipd_document_versions as versions
from app.services import eipd_version_reviews as reviews
from app.services import licitud, navigation_applicability
from app.services.eipd_version_reviews import exact, rows, scope
from app.services.organization_acceptance import member, series_lock

DOMAIN = "cumpleia.eipd.general.decision.v1"


async def authorities(db, org, tid, aid):
    await licitud.get_legal_assessment_v1(db, org, tid, aid)
    return await rows(
        db,
        """SELECT * FROM eipd_decision_authority_events
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
        raise HTTPException(403, detail="No puedes otorgarte la facultad de decisión")
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
    if payload.action == "revoke" and payload.compatibility_reason is not None:
        raise HTTPException(422, detail="La compatibilidad se documenta al otorgar")
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
            """INSERT INTO eipd_decision_authority_events
        (id, organization_id, treatment_id, assessment_id, subject_id, created_by,
         sequence, action, expires_at, reason, reference, compatibility_reason)
        VALUES (:id,:organization_id,:treatment_id,:assessment_id,:subject_id,:created_by,
         :sequence,:action,:expires_at,:reason,:reference,:compatibility_reason) RETURNING *""",
            params,
        )
    )[0]


async def history(db, org, tid, aid, vid):
    await exact(db, org, tid, aid, vid)
    return await rows(
        db,
        """SELECT * FROM eipd_version_decisions
        WHERE organization_id=:organization_id AND treatment_id=:treatment_id
        AND assessment_id=:assessment_id AND version_id=:version_id ORDER BY sequence""",
        dict(**scope(org, tid, aid), version_id=vid),
    )


async def acceptance_block(db, org, tid, aid, version, review):
    if not review or review["outcome"] != "favorable":
        return "La última revisión de esta versión debe ser Favorable"
    bundle = version.bundle
    if not reviews.favorable(bundle):
        return "La versión conservada no cumple los requisitos documentales"
    saved = bundle["saved_assessment"]
    row = await licitud.get_legal_assessment_v1(db, org, tid, aid)
    await db.refresh(row)
    if any(
        saved.get(field) != getattr(row, field)
        for field in ("rat_context_hash", "purpose_snapshot")
    ):
        return "El alcance adoptado difiere del conservado"
    readiness = await licitud.get_legal_assessment_readiness_v1(db, org, tid, aid)
    if readiness.rat_context_current is not True:
        return "El alcance RAT actual requiere revisión"
    current = await navigation_applicability.snapshot(db, org, tid, aid)
    historical = bundle["applicability"]
    if (
        not current["current"]
        or current["eipd"]["state"] != "corresponde"
        or current["eipd"] != historical["eipd"]
    ):
        return "La determinación EIPD vigente difiere de la conservada"
    try:
        policy = await versions.selected_policy(db)
    except ValueError:
        return "No se pudo verificar la política EIPD vigente"
    if policy.model_dump(mode="json") != bundle["policy"]:
        return "La política EIPD vigente difiere de la conservada"
    records = {
        str(r.id): (r.revision, r.document_hash)
        for r in await support.records(db, org, tid, aid)
    }
    if any(
        records.get(r["id"]) != (r["revision"], r["document_hash"])
        for r in bundle["support_records"]
        if r["kind"] != "applicability"
    ):
        return "No se pudo verificar un respaldo conservado"
    return None


async def state(db, org, tid, aid, vid, actor, *, check_acceptance=True):
    version = await exact(db, org, tid, aid, vid)
    authorities_history = await authorities(db, org, tid, aid)
    entries = await history(db, org, tid, aid, vid)
    reviews_history = await reviews.history(db, org, tid, aid, vid)
    last_review = reviews_history[-1] if reviews_history else None
    faculty = next(
        (e for e in reversed(authorities_history) if e["subject_id"] == actor), None
    )
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
        reason = "Se requiere membresía habilitada para decidir"
    if (
        not faculty
        or faculty["action"] != "grant"
        or (faculty["expires_at"] is not None and faculty["expires_at"] <= now)
    ):
        reason = "Se requiere una facultad expresa y vigente de decisión"
    elif not faculty["compatibility_reason"] and any(
        r["created_by"] == actor for r in reviews_history
    ):
        reason = "La facultad debe documentar la compatibilidad de revisión y decisión"
    if version.created_by == actor:
        reason = "No puedes decidir sobre una versión registrada por ti"
    accept_reason = reason
    if check_acceptance and reason is None:
        accept_reason = await acceptance_block(db, org, tid, aid, version, last_review)
    return dict(
        **scope(org, tid, aid),
        version_id=vid,
        decisions=entries,
        latest_review_id=last_review["id"] if last_review else None,
        authority_id=faculty["id"] if faculty else None,
        authorities=authorities_history,
        may_manage=may_manage,
        can_decide=reason is None,
        blocked_reason=reason,
        acceptance_blocked_reason=accept_reason,
        can_accept=check_acceptance and accept_reason is None,
        can_confirm=False,
        activation="deshabilitada",
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
        raise HTTPException(404, detail="Solicitud de decisión no encontrada")
    return found


async def rat_read_lock(db):
    # The pilot must also coordinate with RAT writers outside the evaluation
    # series. NOWAIT avoids waiting with the series and policy locks held.
    try:
        async with db.begin_nested():
            await db.execute(
                text(
                    "LOCK TABLE international_transfers, treatment_data_categories, "
                    "treatment_data_sources, treatment_data_subjects, treatment_purposes, "
                    "treatment_vendors, treatments, vendors IN SHARE MODE NOWAIT"
                )
            )
    except DBAPIError as exc:
        if getattr(exc.orig, "sqlstate", None) != "55P03":
            raise
        support.conflict("El RAT está cambiando; consulta nuevamente antes de decidir")


async def record(db, org, tid, aid, vid, actor, payload):
    support.gate()
    await member(db, org, actor)
    await exact(db, org, tid, aid, vid)
    fingerprint = versions.digest(
        dict(
            domain=DOMAIN,
            version_id=vid,
            treatment_id=tid,
            assessment_id=aid,
            payload=payload.model_dump(mode="json"),
        )
    )
    params = dict(org=org, actor=actor, request=payload.request_id)

    async def replay():
        matches = await rows(
            db,
            """SELECT * FROM eipd_version_decisions
            WHERE organization_id=:org AND created_by=:actor AND request_id=:request""",
            params,
        )
        if matches and matches[0]["input_hash"] != fingerprint:
            support.conflict("Solicitud ya utilizada con otro contenido")
        return matches[0] if matches else None

    previous = await replay()
    if previous:
        return previous
    accepting = payload.outcome == "acepta"
    if accepting:
        await versions.policy_lock(db)
    await db.execute(
        text("SELECT pg_advisory_xact_lock(hashtextextended(:key, 0))"),
        {"key": f"{DOMAIN}:{org}:{actor}:{payload.request_id}"},
    )
    previous = await replay()
    if previous:
        return previous
    await series_lock(db, org, tid, aid)
    if accepting:
        await rat_read_lock(db)
    current = await state(db, org, tid, aid, vid, actor, check_acceptance=accepting)
    if (
        current["authority_id"] is not None
        and payload.expected_authority_id != current["authority_id"]
    ):
        support.conflict("La facultad cambió; consulta su historial")
    if not current["can_decide"]:
        raise HTTPException(403, detail=current["blocked_reason"])
    entries = current["decisions"]
    if (
        payload.expected_decision_id != (entries[-1]["id"] if entries else None)
        or payload.expected_review_id != current["latest_review_id"]
    ):
        support.conflict("La revisión o decisión previa cambió; consulta el historial")
    if accepting and not current["can_accept"]:
        raise HTTPException(422, detail=current["acceptance_blocked_reason"])
    return (
        await rows(
            db,
            """INSERT INTO eipd_version_decisions
        (id, organization_id, treatment_id, assessment_id, version_id, created_by,
         sequence, previous_id, review_id, request_id, outcome, reason, reference, authority_id, input_hash)
        VALUES (:id,:organization_id,:treatment_id,:assessment_id,:version_id,:created_by,
          :sequence,:previous_id,:review_id,:request_id,:outcome,:reason,:reference,:authority_id,:input_hash)
        RETURNING *""",
            dict(
                **scope(org, tid, aid),
                id=uuid4(),
                version_id=vid,
                created_by=actor,
                sequence=len(entries) + 1,
                previous_id=payload.expected_decision_id,
                review_id=payload.expected_review_id,
                request_id=payload.request_id,
                outcome=payload.outcome,
                reason=payload.reason,
                reference=payload.reference,
                authority_id=payload.expected_authority_id,
                input_hash=fingerprint,
            ),
        )
    )[0]
