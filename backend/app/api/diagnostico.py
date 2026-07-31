"""API del Autodiagnóstico (Fase 1, Módulo 1, Tarea 3).

Ver `Fase 1/plan-fase1-modulo1-autodiagnostico.md` y
`docs/adr/0002-logica-adaptativa-riesgo-remediacion.md`. Todo endpoint exige
`X-Organization-Id` + el permiso correspondiente vía `require_permission`
(app/core/deps.py) — primer consumidor real de esa dependencia, que hoy solo
tenía la firma pensada para este módulo.

`GET /cuestionario` no filtra preguntas por rubro/tamaño de organización
(capa 1 del ADR, diferida): el catálogo es el mismo para todas.
"""

import uuid
from datetime import date
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_permission
from app.db.models import Diagnostic, DiagnosticAnswer, Finding, Profile
from app.db.session import get_db
from app.services import diagnostico as diagnostico_service
from app.services.authorization import Permission
from app.services.cuestionario_config import (
    obtener_config_activa,
    obtener_config_por_id,
)

router = APIRouter(prefix="/diagnostico", tags=["diagnostico"])

RespuestaAnswer = Literal["Sí", "Parcial", "No", "N/A"]
OPCIONES_RESPUESTA: tuple[RespuestaAnswer, ...] = ("Sí", "Parcial", "No", "N/A")


class ObligacionCuestionarioOut(BaseModel):
    id: str
    numero_guia: str
    nombre: str


class SeccionCuestionarioOut(BaseModel):
    id: str
    numero_romano: str
    nombre: str
    obligacion_id: str
    orden: int


class PreguntaCuestionarioOut(BaseModel):
    id: str
    seccion_id: str
    texto: str
    orden: int


class CuestionarioOut(BaseModel):
    opciones_respuesta: list[str]
    obligaciones: list[ObligacionCuestionarioOut]
    secciones: list[SeccionCuestionarioOut]
    preguntas: list[PreguntaCuestionarioOut]


class RespuestaIn(BaseModel):
    pregunta_id: str
    answer: RespuestaAnswer
    notes: str | None = None


class GuardarRespuestasRequest(BaseModel):
    respuestas: list[RespuestaIn]


class RespuestaOut(BaseModel):
    pregunta_id: str
    answer: str | None
    notes: str | None


class PuntajeSeccionOut(BaseModel):
    seccion_id: str
    numero_romano: str
    nombre: str
    score: float | None


class DocumentoReferenciaOut(BaseModel):
    id: uuid.UUID
    tipo: str
    titulo: str
    fecha: date | None
    url: str


class HallazgoOut(BaseModel):
    id: uuid.UUID
    pregunta_id: str | None
    seccion_id: str | None
    description: str
    risk: str
    status: str
    corrective_action: str | None
    responsible: str | None
    # Vacío hasta que exista el endpoint de carga/vinculación de
    # reference_documents (ver ADR 0002, capa 3 — queda en backlog).
    documentos_referencia: list[DocumentoReferenciaOut]


class DiagnosticoActualOut(BaseModel):
    id: uuid.UUID
    status: str
    global_score: float | None
    puntaje_por_seccion: list[PuntajeSeccionOut]
    respuestas: list[RespuestaOut]
    hallazgos: list[HallazgoOut]


async def _construir_actual_out(
    db: AsyncSession, diagnostic: Diagnostic
) -> DiagnosticoActualOut:
    config = await obtener_config_por_id(db, diagnostic.config_version_id)
    preguntas_por_id = {p.id: p for p in config.preguntas}
    section_scores: dict = diagnostic.section_scores or {}

    respuestas = (
        (
            await db.execute(
                select(DiagnosticAnswer).where(
                    DiagnosticAnswer.diagnostic_id == diagnostic.id
                )
            )
        )
        .scalars()
        .all()
    )
    hallazgos = (
        (
            await db.execute(
                select(Finding).where(Finding.diagnostic_id == diagnostic.id)
            )
        )
        .scalars()
        .all()
    )

    return DiagnosticoActualOut(
        id=diagnostic.id,
        status=diagnostic.status,
        global_score=(
            float(diagnostic.global_score)
            if diagnostic.global_score is not None
            else None
        ),
        puntaje_por_seccion=[
            PuntajeSeccionOut(
                seccion_id=s.id,
                numero_romano=s.numero_romano,
                nombre=s.nombre,
                score=section_scores.get(s.id),
            )
            for s in config.secciones
        ],
        respuestas=[
            RespuestaOut(pregunta_id=r.pregunta_id, answer=r.answer, notes=r.notes)
            for r in respuestas
        ],
        hallazgos=[
            HallazgoOut(
                id=h.id,
                pregunta_id=h.pregunta_id,
                seccion_id=(
                    preguntas_por_id[h.pregunta_id].seccion_id
                    if h.pregunta_id in preguntas_por_id
                    else None
                ),
                description=h.description,
                risk=h.risk.value.capitalize(),
                status=h.status.value,
                corrective_action=h.corrective_action,
                responsible=h.responsible,
                documentos_referencia=[],
            )
            for h in hallazgos
        ],
    )


@router.get("/cuestionario", response_model=CuestionarioOut)
async def leer_cuestionario(
    current_profile: Profile = Depends(require_permission(Permission.view_content)),
    db: AsyncSession = Depends(get_db),
) -> CuestionarioOut:
    config = await obtener_config_activa(db)
    return CuestionarioOut(
        opciones_respuesta=list(OPCIONES_RESPUESTA),
        obligaciones=[
            ObligacionCuestionarioOut(
                id=o.id, numero_guia=o.numero_guia, nombre=o.nombre
            )
            for o in config.obligaciones
        ],
        secciones=[
            SeccionCuestionarioOut(
                id=s.id,
                numero_romano=s.numero_romano,
                nombre=s.nombre,
                obligacion_id=s.obligacion_id,
                orden=s.orden,
            )
            for s in config.secciones
        ],
        preguntas=[
            PreguntaCuestionarioOut(
                id=p.id, seccion_id=p.seccion_id, texto=p.texto, orden=p.orden
            )
            for p in config.preguntas
        ],
    )


@router.post("/respuestas", response_model=DiagnosticoActualOut)
async def guardar_respuestas(
    payload: GuardarRespuestasRequest,
    x_organization_id: Annotated[uuid.UUID, Header()],
    current_profile: Profile = Depends(require_permission(Permission.edit_content)),
    db: AsyncSession = Depends(get_db),
) -> DiagnosticoActualOut:
    diagnostic = await diagnostico_service.obtener_o_crear_diagnostico_vigente(
        db, x_organization_id, current_profile.id
    )
    respuestas = [
        diagnostico_service.RespuestaGuardar(
            pregunta_id=r.pregunta_id, answer=r.answer, notes=r.notes
        )
        for r in payload.respuestas
    ]
    await diagnostico_service.guardar_respuestas(db, diagnostic, respuestas)
    await diagnostico_service.recalcular_diagnostico(db, diagnostic)
    return await _construir_actual_out(db, diagnostic)


@router.get("/actual", response_model=DiagnosticoActualOut)
async def leer_diagnostico_actual(
    x_organization_id: Annotated[uuid.UUID, Header()],
    current_profile: Profile = Depends(require_permission(Permission.view_content)),
    db: AsyncSession = Depends(get_db),
) -> DiagnosticoActualOut:
    diagnostic = await diagnostico_service.obtener_diagnostico_vigente(
        db, x_organization_id
    )
    if diagnostic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La organización todavía no tiene un diagnóstico en curso.",
        )
    return await _construir_actual_out(db, diagnostic)
