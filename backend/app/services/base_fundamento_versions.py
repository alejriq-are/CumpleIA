"""5D.1: immutable versions of the saved legal basis and its diagnosis."""

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select, text

from app.db.base_fundamento_versions import BaseFundamentoVersion as Version
from app.services import assessment_support as support
from app.services import licitud
from app.services.base_fundamento_catalog import (
    BASES,
    evaluate_base_document,
    favorable_requirements,
)
from app.services.eipd_document_versions import canonical
from app.services.organization_acceptance import member, series_lock

DOMAIN = "cumpleia.base_fundamento.registered.v1"


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
        favorable_requirements=favorable_requirements(row.bundle),
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


async def source(db, org, tid, aid, annex_ids):
    if len(annex_ids) != len(set(annex_ids)):
        raise HTTPException(422, detail="Cada anexo debe seleccionarse una sola vez")
    row = await licitud.get_legal_assessment_v1(db, org, tid, aid)
    await db.refresh(row)
    if row.status != "borrador":
        support.conflict("Se requiere una evaluación editable con contenido guardado")

    basis = BASES.get(row.legal_basis)
    form = getattr(row, basis.form) if basis else None
    alternatives = {
        field: getattr(row, field)
        for field in ("consent_assessment", "lia_assessment")
        if (not basis or basis.form != field) and getattr(row, field) is not None
    }
    records = (
        {
            record.id: record
            for record in await support.records(db, org, tid, aid)
            if record.kind == "annex"
        }
        if annex_ids
        else {}
    )
    if any(annex_id not in records for annex_id in annex_ids):
        raise HTTPException(
            404, detail="Anexo guardado no encontrado en esta evaluación"
        )
    material = canonical(
        dict(
            schema_version=1,
            document_type="base_fundamento",
            saved_assessment=dict(
                id=row.id,
                organization_id=row.organization_id,
                treatment_id=row.treatment_id,
                series_id=row.series_id,
                version=row.version,
                legal_basis=row.legal_basis,
                justification=row.justification,
                purpose_snapshot=row.purpose_snapshot,
                rat_context_hash=row.rat_context_hash,
                rat_context_snapshot=row.rat_context_snapshot,
            ),
            primary_form={"kind": basis.form, "content": form} if basis else None,
            alternatives=alternatives,
            annexes=[
                dict(
                    id=r.id,
                    revision=r.revision,
                    document_hash=r.document_hash,
                    sha256=r.payload["sha256"],
                    reference=r.payload.get("reference"),
                    version=r.payload.get("version"),
                )
                for r in (records[annex_id] for annex_id in annex_ids)
            ],
            diagnostic=evaluate_base_document(
                legal_basis=row.legal_basis,
                justification=row.justification,
                purpose=row.purpose_snapshot,
                snapshot=row.rat_context_snapshot,
                document=form,
            ),
        )
    )
    return material, digest({"material": material, "updated_at": row.updated_at})


async def preview(db, org, tid, aid, annex_ids):
    support.gate()
    await series_lock(db, org, tid, aid)
    material, token = await source(db, org, tid, aid, annex_ids)
    rows = await history(db, org, tid, aid)
    return dict(
        source_hash=token,
        latest_version=rows[-1].version if rows else 0,
        bundle=material,
        favorable_requirements=favorable_requirements(material),
        can_confirm=False,
        activation="deshabilitada",
    )


async def register(db, org, tid, aid, actor, payload):
    support.gate()
    await member(db, org, actor)  # Actual tenant member, including platform admins.
    # A request key is tenant/actor scoped, including across different series.
    # Lock order: request, then series. The snapshot uses only saved material.
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
    material, token = await source(db, org, tid, aid, payload.annex_ids)
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
