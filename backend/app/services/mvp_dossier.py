"""Reune snapshots existentes bajo serie compartida; no publica ni persiste actas."""

import hashlib
import json
from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy import select

from app.core.config import get_settings
from app.db.models import LegalAssessmentSeries
from app.schemas.child_adolescent_api import LegalAssessmentChildOutV1
from app.schemas.mvp_dossier import MvpDossierOut
from app.services import (
    eipd_child_persistence as child,
)
from app.services import (
    licitud,
)
from app.services import (
    organization_acceptance as acceptance,
)

SOURCES = [
    {
        "reference": "DO-21719",
        "artifact_reference": "docs/project/policy-evidence/ley-21719-do-2024-12-13.pdf",
        "artifact_sha256": "a760962caa0348d4ad9d7530a42eee12370d5dd74ea968a19ab91f1c86109e2a",
        "title": "Ley 21.719 — publicacion original",
        "url": "https://www.diariooficial.interior.gob.cl/publicaciones/2024/12/13/44023/01/2583630.pdf",
        "scope_note": "Publicacion original; no sustituye texto consolidado ni revision de aplicabilidad.",
    },
    {
        "reference": "BCN-21719",
        "title": "Ley 21.719 — texto BCN",
        "url": "https://www.bcn.cl/leychile/navegar?i=1209272",
        "scope_note": "Revalidar version y regimen temporal antes de empresa piloto.",
    },
    {
        "reference": "BCN-DS662",
        "title": "Decreto 662 — modelos de prevencion de infracciones",
        "url": "https://www.leychile.cl/navegar?idNorma=1227971",
        "scope_note": "Modelo de adopcion voluntaria. No es lista de operaciones EIPD ni certificacion de CumpleIA.",
    },
]
GATES = [
    (
        "G1",
        "Alcance MVP documental",
        "alcance_definido",
        "RAT asociado, evaluacion de licitud/LIA y EIPD; sin datos reales ni activacion.",
    ),
    (
        "G2",
        "Revision juridica de organizacion",
        "pendiente",
        "Persona facultada, evidencia autentica, fuentes vigentes y revision de aplicabilidad. Lista/orientaciones EIPD no verificadas en busqueda acotada.",
    ),
    (
        "G3",
        "Politica y contratos versionados",
        "pendiente",
        "Compatibilidad y validacion de reglas globales separadas de actas tenant; no promover V1.",
    ),
    (
        "G4",
        "Validacion tecnica del candidato",
        "pendiente",
        "CI y recorrido del commit candidato exacto; no usar conteos historicos.",
    ),
    (
        "G5",
        "Operacion del piloto",
        "pendiente",
        "Entorno, accesos, restauracion, retencion, soporte e incidentes por validar.",
    ),
    (
        "G6",
        "Datos reales",
        "bloqueado",
        "Decision separada, organizacion piloto, migracion y controles de procedencia/minimizacion.",
    ),
    (
        "G7",
        "Activacion EIPD",
        "bloqueado",
        "Excluida de este MVP documental; requiere nueva decision explicita y pruebas de positivos.",
    ),
]


def digest(value):
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def document(kind, content, version, coverage, events=None):
    return dict(
        kind=kind,
        status="disponible" if content is not None else "sin_documento",
        version=version,
        coverage=coverage,
        content=content,
        content_hash=digest(content) if content is not None else None,
        organization_acceptance=(
            ("consultar_eventos" if events else "sin_eventos")
            if kind == "eipd"
            else "sin_flujo"
        ),
        acceptance_events=events or [],
    )


async def build(db, org, tid, aid):
    if get_settings().environment not in ("development", "test"):
        raise HTTPException(
            409, detail="Expediente MVP disponible solo en desarrollo/pruebas"
        )
    draft = await licitud.get_legal_assessment_v1(db, org, tid, aid)
    # Los escritores M3 usan la misma serie. No tocar selector ni politica global.
    series = await db.scalar(
        select(LegalAssessmentSeries)
        .where(
            LegalAssessmentSeries.id == draft.series_id,
            LegalAssessmentSeries.organization_id == org,
            LegalAssessmentSeries.treatment_id == tid,
        )
        .with_for_update(read=True)
    )
    if series is None:
        raise HTTPException(409, detail="Serie de expediente no disponible")
    await db.refresh(draft)
    assessment = LegalAssessmentChildOutV1.model_validate(draft).model_dump(mode="json")
    docs = [
        document(
            "rat",
            assessment["rat_context_snapshot"],
            assessment["rat_context_schema_version"],
            "Snapshot RAT asociado al alcance de esta evaluacion; no inventario completo ni comprobacion de RAT actual.",
        ),
        document(
            "licitud_lia",
            assessment,
            assessment["version"],
            "Evaluacion completa; LIA si fue aportada. Tener datos no acredita suficiencia juridica.",
        ),
    ]
    resolutions = await child.list_resolutions(db, org, tid, aid)
    if resolutions:
        row = max(resolutions, key=lambda x: x.version)
        events = [
            e.model_dump(mode="json")
            for e in await acceptance.history(db, org, tid, aid, row.id)
        ]
        docs.append(
            document(
                "eipd",
                row.model_dump(mode="json"),
                row.version,
                "Sucesor con cobertura infancia; eventos solo para esta resolucion.",
                events,
            )
        )
    else:
        legacy = assessment.get("eipd_resolution_assessment")
        docs.append(
            document(
                "eipd",
                legacy,
                legacy.get("schema_version") if legacy else None,
                "Documento previo si existe; no se promueve a cobertura infancia ni hereda aceptacion.",
            )
        )
    from app.services.assessment_support import snapshot

    payload = dict(
        support=await snapshot(db, org, tid, aid),
        organization_id=org,
        treatment_id=tid,
        assessment_id=aid,
        assessment_version=draft.version,
        generated_at=datetime.now(UTC),
        rat_snapshot_note="Se conserva el snapshot asociado. Los gates y fuentes son una propuesta documental, no una liberacion ni acta real.",
        documents=docs,
        official_sources=[{**s, "consulted_on": "2026-10-16"} for s in SOURCES],
        release_gates=[
            dict(id=i, title=t, status=s, evidence_needed=e) for i, t, s, e in GATES
        ],
        packet_hash="0" * 64,
    )
    report = MvpDossierOut.model_validate(payload)
    canonical = report.model_dump(mode="json", exclude={"packet_hash"})
    return report.model_copy(update={"packet_hash": digest(canonical)})
