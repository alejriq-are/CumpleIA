"""5B.1: explicit immutable registration; no review, acceptance or activation."""

import json
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select, text

from app.db.eipd_document_versions import EipdDocumentVersion as Version
from app.services import assessment_support as support
from app.services import licitud, navigation_applicability
from app.services.eipd_child_persistence import selected_policy
from app.services.organization_acceptance import member, series_lock

DOMAIN = "cumpleia.eipd.general.registered.v1"


def canonical(value):
    return json.loads(json.dumps(value, default=str, ensure_ascii=False))


def digest(value):
    return support.digest({"domain": DOMAIN, "material": value})


def output(row):
    if digest(row.bundle) != row.bundle_hash:
        support.conflict("Integridad de la versión documental no verificable")
    return dict(
        id=str(row.id),
        organization_id=str(row.organization_id),
        treatment_id=str(row.treatment_id),
        assessment_id=str(row.assessment_id),
        version=row.version,
        created_by=str(row.created_by),
        created_at=row.created_at.isoformat(),
        request_id=str(row.request_id),
        reason=row.reason,
        source_hash=row.source_hash,
        bundle_hash=row.bundle_hash,
        bundle=row.bundle,
        can_confirm=False,
        activation="deshabilitada",
    )


async def history(db, org, tid, aid):
    await licitud.get_legal_assessment_v1(db, org, tid, aid)
    return list(
        (
            await db.scalars(
                select(Version)
                .where(
                    Version.organization_id == org,
                    Version.treatment_id == tid,
                    Version.assessment_id == aid,
                )
                .order_by(Version.version)
            )
        ).all()
    )


async def policy_lock(db):
    try:
        await licitud.resolve_eipd_policy_snapshot_for_transaction_v1(db)
    except ValueError:
        support.conflict("Política EIPD no disponible para registrar")


async def source(db, org, tid, aid, *, locked=False):
    # Global policy selector must always precede request and series locks.
    if not locked:
        await policy_lock(db)
        await series_lock(db, org, tid, aid)
    policy = await selected_policy(db)
    row = await licitud.get_legal_assessment_v1(db, org, tid, aid)
    await db.refresh(row)
    if row.status != "borrador" or row.eipd_resolution_assessment is None:
        support.conflict("Se requiere un borrador EIPD guardado y editable")
    applicability = await navigation_applicability.snapshot(db, org, tid, aid)
    if not applicability["current"] or applicability["eipd"]["state"] != "corresponde":
        support.conflict("Guarda una determinación vigente de EIPD: Corresponde")
    readiness = await licitud.get_legal_assessment_readiness_v1(db, org, tid, aid)
    diagnostic = readiness.model_dump(mode="json")
    if not diagnostic["rat_context_current"]:
        support.conflict(
            "El alcance RAT cambió; revisa su asociación antes de registrar"
        )
    records = await support.records(db, org, tid, aid)
    saved = canonical({c.name: getattr(row, c.name) for c in row.__table__.columns})
    material = dict(
        schema_version=1,
        document_type="eipd_general",
        saved_assessment=saved,
        applicability=applicability,
        support_records=[
            canonical(
                dict(
                    id=r.id,
                    kind=r.kind,
                    revision=r.revision,
                    document_hash=r.document_hash,
                    created_at=r.created_at,
                    created_by=r.created_by,
                    payload=r.payload,
                )
            )
            for r in records
        ],
        policy=policy.model_dump(mode="json"),
        diagnostic=dict(
            rule_set="cumpleia.general.registration.v1", readiness=diagnostic
        ),
    )
    # updated_at is deliberately included: edit/revert cannot reuse an old token.
    return material, digest(material)


async def preview(db, org, tid, aid):
    support.gate()
    material, token = await source(db, org, tid, aid)
    rows = await history(db, org, tid, aid)
    return dict(
        source_hash=token,
        latest_version=rows[-1].version if rows else 0,
        bundle=material,
        can_confirm=False,
        activation="deshabilitada",
    )


async def register(db, org, tid, aid, actor, payload):
    support.gate()
    await member(db, org, actor)  # Actual tenant member, including platform admins.
    # A request key is tenant/actor scoped, including across different series.
    # Lock order: global policy -> request -> series; retained until commit.
    await policy_lock(db)
    await db.execute(
        text("SELECT pg_advisory_xact_lock(hashtextextended(:key, 0))"),
        {"key": f"{DOMAIN}:{org}:{actor}:{payload.request_id}"},
    )
    await series_lock(db, org, tid, aid)
    request_hash = digest(
        dict(
            treatment_id=tid, assessment_id=aid, payload=payload.model_dump(mode="json")
        )
    )
    previous = await db.scalar(
        select(Version).where(
            Version.organization_id == org,
            Version.created_by == actor,
            Version.request_id == payload.request_id,
        )
    )
    if previous:
        if previous.input_hash != request_hash:
            support.conflict("Solicitud ya utilizada con otro contenido")
        return output(previous)
    material, token = await source(db, org, tid, aid, locked=True)
    rows = await history(db, org, tid, aid)
    latest = rows[-1].version if rows else 0
    if (
        token != payload.expected_source_hash
        or latest != payload.expected_latest_version
    ):
        support.conflict(
            "El borrador o su contexto cambió: consulta de nuevo antes de registrar"
        )
    bundle = canonical(
        dict(
            **material,
            version=latest + 1,
            predecessor_id=str(rows[-1].id) if rows else None,
            reason=payload.reason,
            registered_by=actor,
        )
    )
    result = Version(
        organization_id=org,
        treatment_id=tid,
        assessment_id=aid,
        created_by=actor,
        request_id=payload.request_id,
        version=latest + 1,
        data_kind="ficticios",
        reason=payload.reason,
        source_hash=token,
        input_hash=request_hash,
        bundle_hash=digest(bundle),
        bundle=bundle,
    )
    db.add(result)
    await db.flush()
    await db.refresh(result)
    return output(result)


async def lookup(db, org, tid, aid, request_id: UUID, actor):
    rows = await history(db, org, tid, aid)
    row = next(
        (r for r in rows if r.request_id == request_id and r.created_by == actor), None
    )
    if row is None:
        raise HTTPException(404, detail="Solicitud de registro no encontrada")
    return output(row)
