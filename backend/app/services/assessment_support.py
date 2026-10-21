"""Independent documentary support. No confirmation, scoring of legal gates or external storage."""

import base64
import binascii
import hashlib
import json
from datetime import date
from pathlib import PurePath

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import defer

from app.core.config import get_settings
from app.db.assessment_support import AssessmentSupportRecord as Record
from app.schemas.assessment_support import RiskMethodology
from app.services import licitud
from app.services.organization_acceptance import member, series_lock

MATRIX = (
    ("bajo", "bajo", "medio", "alto"),
    ("bajo", "medio", "alto", "alto"),
    ("medio", "alto", "alto", "muy_alto"),
    ("alto", "alto", "muy_alto", "muy_alto"),
)
LEVELS = ("bajo", "medio", "alto", "muy_alto")


def conflict(message):
    raise HTTPException(409, detail=message)


def gate():
    if get_settings().environment not in ("development", "test"):
        conflict("Soporte documental disponible solo para pruebas ficticias")


def digest(value):
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            default=str,
        ).encode()
    ).hexdigest()


def fingerprint(row):
    # Bind to complete saved assessment material; do not alter any prior document hash.
    return digest(
        {
            column.name: getattr(row, column.name)
            for column in row.__table__.columns
            if column.name not in ("created_at", "updated_at")
        }
    )


def level(rating):
    if rating.probability is None or rating.impact is None:
        return "sin_resolver"
    return MATRIX[rating.probability - 1][rating.impact - 1]


def evaluate(analysis: RiskMethodology, document: dict, annexes=()):
    risk_rows = document.get("risks", [])
    measures = document.get("measures", [])
    ids = [r.get("risk_id") for r in risk_rows]
    mids = [m.get("measure_id") for m in measures]
    if (
        any(not isinstance(i, str) or not i.strip() for i in ids + mids)
        or len(ids) != len(set(ids))
        or len(mids) != len(set(mids))
    ):
        conflict(
            "Asigna identificadores unicos a riesgos y medidas antes de valorarlos"
        )
    ratings = {r.risk_id: r for r in analysis.risks}
    controls = {m.measure_id: m for m in analysis.controls}
    if len(ratings) != len(analysis.risks) or len(controls) != len(analysis.controls):
        conflict("Valoraciones duplicadas")
    if not set(ratings).issubset(ids) or not set(controls).issubset(mids):
        conflict(
            "La valoracion referencia riesgos o medidas que no estan en el documento guardado"
        )
    known_evidence = {a["reference"] for a in annexes}

    def evidence_refs(value):
        if isinstance(value, dict):
            for k, v in value.items():
                if k == "evidence" and isinstance(v, list):
                    known_evidence.update(
                        e.get("reference")
                        for e in v
                        if isinstance(e, dict) and e.get("reference")
                    )
                evidence_refs(v)
        elif isinstance(value, list):
            for item in value:
                evidence_refs(item)

    evidence_refs(document)
    for control in analysis.controls:
        measure = next(m for m in measures if m["measure_id"] == control.measure_id)
        if control.status == "verificada" and (
            (measure.get("implemented") or {}).get("answer") != "si"
            or not control.evidence_references
            or not set(control.evidence_references).issubset(known_evidence)
            or not control.rationale.strip()
            or control.dimension is None
            or control.effectiveness == "no_evaluada"
        ):
            conflict(
                "Un control verificado exige implementacion declarada, evidencia registrada, dimension, eficacia y fundamento"
            )
    results = []
    for risk_id in ids:
        rating = ratings.get(risk_id)
        if rating is None:
            results.append(
                dict(
                    risk_id=risk_id,
                    inherent="sin_resolver",
                    projected="sin_resolver",
                    residual="sin_resolver",
                )
            )
            continue
        if rating.review_on:
            try:
                date.fromisoformat(rating.review_on)
            except ValueError:
                conflict("Fecha de revision invalida")
        for item in (rating.inherent, rating.projected, rating.residual):
            if (item.probability is not None or item.impact is not None) and (
                not item.rationale.strip()
                or not analysis.horizon.strip()
                or not rating.harm.strip()
            ):
                conflict(
                    "Toda valoracion exige horizonte, dano a las personas y fundamento"
                )
        if level(rating.residual) != "sin_resolver":
            linked = [m for m in measures if risk_id in m.get("risk_ids", [])]
            if not linked or any(
                m["measure_id"] not in controls
                or controls[m["measure_id"]].status != "verificada"
                for m in linked
            ):
                conflict(
                    "El residual actual exige controles asociados verificados; usa residual previsto mientras falte verificacion"
                )
            if level(rating.inherent) == "sin_resolver":
                conflict("Valora primero el riesgo inherente")
            for dimension, before, after in (
                (
                    "probabilidad",
                    rating.inherent.probability,
                    rating.residual.probability,
                ),
                ("impacto", rating.inherent.impact, rating.residual.impact),
            ):
                if after < before and not any(
                    controls[m["measure_id"]].dimension in (dimension, "ambos")
                    and controls[m["measure_id"]].effectiveness
                    in ("parcial", "suficiente")
                    for m in linked
                ):
                    conflict(
                        "La reduccion residual exige un control eficaz sobre la dimension reducida"
                    )
        results.append(
            dict(
                risk_id=risk_id,
                inherent=level(rating.inherent),
                projected=level(rating.projected),
                residual=level(rating.residual),
            )
        )
    resolved = [r["residual"] for r in results if r["residual"] in LEVELS]
    return dict(
        methodology=analysis.methodology,
        matrix=MATRIX,
        risks=results,
        worst_residual=max(resolved, key=LEVELS.index) if resolved else "sin_resolver",
        unresolved=not results or any(r["residual"] == "sin_resolver" for r in results),
        can_confirm=False,
        activation="deshabilitada",
    )


def metadata(row):
    return dict(
        id=str(row.id),
        revision=row.revision,
        kind=row.kind,
        document_hash=row.document_hash,
        created_at=row.created_at.isoformat(),
        **row.payload,
    )


async def records(db, org, tid, aid):
    return list(
        await db.scalars(
            select(Record)
            .options(defer(Record.content))
            .where(
                Record.organization_id == org,
                Record.treatment_id == tid,
                Record.assessment_id == aid,
            )
            .order_by(Record.kind, Record.revision)
        )
    )


async def snapshot(db, org, tid, aid):
    gate()
    row = await licitud.get_legal_assessment_v1(db, org, tid, aid)
    saved = await records(db, org, tid, aid)
    risks = [r for r in saved if r.kind == "risk"]
    current_hash = fingerprint(row)
    risk = metadata(risks[-1]) if risks else None
    if risk:
        risk["current"] = risk["document_hash"] == current_hash
    return dict(
        schema_version=1,
        assessment_id=str(aid),
        organization_id=str(org),
        treatment_id=str(tid),
        document_hash=current_hash,
        risk_evaluation=risk,
        risk_history=[
            dict(
                id=str(r.id),
                revision=r.revision,
                created_at=r.created_at.isoformat(),
                document_hash=r.document_hash,
            )
            for r in risks
        ],
        annexes=[metadata(r) for r in saved if r.kind == "annex"],
        can_confirm=False,
        activation="deshabilitada",
    )


async def save_risks(db, org, tid, aid, actor, payload):
    gate()
    await member(db, org, actor)
    await series_lock(db, org, tid, aid)
    row = await licitud.get_legal_assessment_v1(db, org, tid, aid)
    await db.refresh(row)
    if row.status != "borrador":
        conflict("Evaluacion de solo lectura")
    saved = await records(db, org, tid, aid)
    previous = next((r for r in saved if r.request_id == payload.request_id), None)
    input_hash = digest(payload.model_dump(mode="json"))
    if previous:
        if previous.kind != "risk" or previous.payload.get("input_hash") != input_hash:
            conflict("Solicitud ya utilizada con otro contenido")
        return await snapshot(db, org, tid, aid)
    revision = max((r.revision for r in saved if r.kind == "risk"), default=0)
    if payload.expected_revision != revision or payload.document_hash != fingerprint(
        row
    ):
        conflict(
            "Cambio concurrente: vuelve a consultar antes de guardar la valoracion"
        )
    document = row.eipd_resolution_assessment
    if not document:
        conflict("Guarda primero el borrador EIPD")
    result = evaluate(
        payload.analysis, document, [r.payload for r in saved if r.kind == "annex"]
    )
    db.add(
        Record(
            organization_id=org,
            treatment_id=tid,
            assessment_id=aid,
            created_by=actor,
            request_id=payload.request_id,
            kind="risk",
            revision=revision + 1,
            data_kind="ficticios",
            document_hash=payload.document_hash,
            payload=dict(
                analysis=payload.analysis.model_dump(mode="json"),
                result=result,
                input_hash=input_hash,
            ),
        )
    )
    await db.flush()
    return await snapshot(db, org, tid, aid)


def decode_annex(payload):
    name = payload.filename
    if PurePath(name).name != name or any(
        c in name for c in ("/", chr(92), "\r", "\n", "\x00")
    ):
        raise HTTPException(422, detail="Nombre de archivo invalido")
    try:
        data = base64.b64decode(payload.content_base64, validate=True)
    except (ValueError, binascii.Error):
        raise HTTPException(422, detail="Archivo invalido") from None
    if not 0 < len(data) <= 2097152:
        raise HTTPException(413, detail="Maximo 2 MiB por archivo")
    suffix = PurePath(name).suffix.lower()
    if suffix == ".pdf" and data.startswith(b"%PDF-"):
        mime = "application/pdf"
    elif suffix == ".txt":
        try:
            data.decode("utf-8")
        except UnicodeError:
            raise HTTPException(422, detail="Texto UTF-8 requerido") from None
        if b"\x00" in data:
            raise HTTPException(422, detail="Texto invalido")
        mime = "text/plain"
    else:
        raise HTTPException(
            422,
            detail="Solo PDF o TXT UTF-8; el archivo debe coincidir con su extension",
        )
    return data, mime


async def save_annex(db, org, tid, aid, actor, payload):
    gate()
    await member(db, org, actor)
    data, mime = decode_annex(payload)
    await series_lock(db, org, tid, aid)
    row = await licitud.get_legal_assessment_v1(db, org, tid, aid)
    await db.refresh(row)
    if row.status != "borrador":
        conflict("Evaluacion de solo lectura")
    saved = await records(db, org, tid, aid)
    checksum = hashlib.sha256(data).hexdigest()
    input_hash = digest(
        {
            **payload.model_dump(mode="json", exclude={"content_base64"}),
            "sha256": checksum,
        }
    )
    previous = next((r for r in saved if r.request_id == payload.request_id), None)
    if previous:
        if previous.kind != "annex" or previous.payload.get("input_hash") != input_hash:
            conflict("Solicitud ya utilizada con otro contenido")
        return await snapshot(db, org, tid, aid)
    annexes = [r for r in saved if r.kind == "annex"]
    if (
        len(annexes) >= 50
        or sum(r.payload["size"] for r in annexes) + len(data) > 20 * 1024 * 1024
    ):
        conflict("Limite por evaluacion: 50 anexos o 20 MiB")
    doc = row.eipd_resolution_assessment or {}
    if not set(payload.risk_ids).issubset(
        {r.get("risk_id") for r in doc.get("risks", [])}
    ) or not set(payload.measure_ids).issubset(
        {m.get("measure_id") for m in doc.get("measures", [])}
    ):
        conflict("Asocia el anexo a identificadores guardados en esta evaluacion")
    version = 1 + sum(r.payload["reference"] == payload.reference for r in annexes)
    meta = payload.model_dump(
        mode="json", exclude={"data_kind", "request_id", "content_base64"}
    )
    db.add(
        Record(
            organization_id=org,
            treatment_id=tid,
            assessment_id=aid,
            created_by=actor,
            request_id=payload.request_id,
            kind="annex",
            revision=max((r.revision for r in annexes), default=0) + 1,
            data_kind="ficticios",
            document_hash=fingerprint(row),
            payload=dict(
                **meta,
                version=version,
                mime=mime,
                size=len(data),
                sha256=checksum,
                input_hash=input_hash,
            ),
            content=data,
        )
    )
    await db.flush()
    return await snapshot(db, org, tid, aid)


async def download_annex(db, org, tid, aid, annex_id):
    gate()
    await licitud.get_legal_assessment_v1(db, org, tid, aid)
    row = await db.scalar(
        select(Record).where(
            Record.id == annex_id,
            Record.organization_id == org,
            Record.treatment_id == tid,
            Record.assessment_id == aid,
            Record.kind == "annex",
        )
    )
    if row is None:
        raise HTTPException(404, detail="Anexo no disponible")
    return row
