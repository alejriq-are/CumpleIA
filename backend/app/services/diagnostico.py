"""Orquestación del Autodiagnóstico (Fase 1, Módulo 1, Tarea 3).

Conecta el catálogo versionado (app/services/cuestionario_config.py) con el
motor de puntaje puro (app/services/diagnostico_puntaje.py, sin tocar):
resuelve el diagnóstico vigente de una organización, guarda respuestas y
recalcula puntajes/hallazgos tras cada guardado. Ver
docs/adr/0002-logica-adaptativa-riesgo-remediacion.md para el alcance
(capas 1-4) y `Fase 1/plan-fase1-modulo1-autodiagnostico.md` para el diseño
de "diagnóstico vigente" (get-or-create, no historial).
"""

import uuid
from dataclasses import dataclass

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Diagnostic,
    DiagnosticAnswer,
    Finding,
    FindingStatus,
    Pregunta,
    RiskLevel,
)
from app.services.cuestionario_config import (
    obtener_config_activa,
    obtener_config_por_id,
)
from app.services.diagnostico_puntaje import (
    RespuestaInput,
    calcular_puntaje_global,
    calcular_puntaje_por_seccion,
    detectar_brechas,
)

RESPUESTAS_VALIDAS = {"Sí", "Parcial", "No", "N/A"}


@dataclass(frozen=True)
class RespuestaGuardar:
    pregunta_id: str
    answer: str  # 'Sí' | 'Parcial' | 'No' | 'N/A'
    notes: str | None = None


async def obtener_diagnostico_vigente(
    db: AsyncSession, organization_id: uuid.UUID
) -> Diagnostic | None:
    result = await db.execute(
        select(Diagnostic).where(Diagnostic.organization_id == organization_id)
    )
    return result.scalar_one_or_none()


async def obtener_o_crear_diagnostico_vigente(
    db: AsyncSession, organization_id: uuid.UUID, profile_id: uuid.UUID
) -> Diagnostic:
    """Get-or-create: a lo sumo un Diagnostic por organización
    (`diagnostics.organization_id` es UNIQUE desde la migración 0005).

    Insert-then-select, nunca select-then-insert (mismo motivo que el
    aprovisionamiento JIT de Profile en app/core/deps.py): dos guardados
    concurrentes de la primera respuesta no deben crear dos filas.
    """
    existente = await obtener_diagnostico_vigente(db, organization_id)
    if existente is not None:
        return existente

    config_activa = await obtener_config_activa(db)
    await db.execute(
        pg_insert(Diagnostic)
        .values(
            organization_id=organization_id,
            config_version_id=config_activa.version.id,
            created_by=profile_id,
            updated_by=profile_id,
        )
        .on_conflict_do_nothing(index_elements=["organization_id"])
    )
    result = await db.execute(
        select(Diagnostic).where(Diagnostic.organization_id == organization_id)
    )
    return result.scalar_one()


async def guardar_respuestas(
    db: AsyncSession, diagnostic: Diagnostic, respuestas: list[RespuestaGuardar]
) -> None:
    """Upsert de DiagnosticAnswer por (diagnostic_id, pregunta_id).

    Valida ANTES de escribir que todo pregunta_id exista en el catálogo y que
    todo answer esté en el dominio permitido (mismo estilo fail-fast que
    validar_guardado en cuestionario_config.py): un valor inválido no debe
    crear una respuesta huérfana ni depender de que el CHECK de la base
    aborte con un error crudo — el router ya restringe `answer` con un
    Literal de Pydantic, pero esta función es el servicio reusable, no solo
    su único llamador actual.
    """
    if not respuestas:
        return

    answers_invalidas = sorted(
        {r.answer for r in respuestas if r.answer not in RESPUESTAS_VALIDAS}
    )
    if answers_invalidas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Respuestas fuera del dominio permitido: {answers_invalidas}",
        )

    pregunta_ids_catalogo = set((await db.execute(select(Pregunta.id))).scalars().all())
    desconocidas = sorted({r.pregunta_id for r in respuestas} - pregunta_ids_catalogo)
    if desconocidas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Preguntas desconocidas en el catálogo: {desconocidas}",
        )

    stmt = pg_insert(DiagnosticAnswer).values(
        [
            {
                "organization_id": diagnostic.organization_id,
                "diagnostic_id": diagnostic.id,
                "pregunta_id": r.pregunta_id,
                "answer": r.answer,
                "notes": r.notes,
            }
            for r in respuestas
        ]
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=["diagnostic_id", "pregunta_id"],
        set_={"answer": stmt.excluded.answer, "notes": stmt.excluded.notes},
    )
    await db.execute(stmt)


async def recalcular_diagnostico(db: AsyncSession, diagnostic: Diagnostic) -> None:
    """Recalcula puntajes y sincroniza hallazgos tras guardar respuestas.

    Usa la config PINNEADA en `diagnostic.config_version_id` (no
    necesariamente la activa hoy): el puntaje debe ser reproducible aunque
    el superadmin publique una nueva versión de pesos/riesgo mientras el
    diagnóstico está en progreso.
    """
    config = await obtener_config_por_id(db, diagnostic.config_version_id)
    preguntas_por_id = {p.id: p for p in config.preguntas}
    seccion_por_pregunta = {p.id: p.seccion_id for p in config.preguntas}

    answers = (
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
    respuestas_input = [
        RespuestaInput(pregunta_id=a.pregunta_id, answer=a.answer)
        for a in answers
        if a.answer is not None
    ]

    puntaje_por_seccion = calcular_puntaje_por_seccion(
        respuestas_input, seccion_por_pregunta
    )
    diagnostic.section_scores = puntaje_por_seccion
    diagnostic.global_score = calcular_puntaje_global(
        puntaje_por_seccion, config.peso_por_seccion
    )
    diagnostic.status = (
        "completado"
        if len(respuestas_input) >= len(config.preguntas)
        else "en_progreso"
    )

    brechas = detectar_brechas(
        respuestas_input, seccion_por_pregunta, config.riesgo_por_pregunta
    )
    detectadas_por_pregunta = {b.pregunta_id: b for b in brechas}

    hallazgos_existentes = {
        f.pregunta_id: f
        for f in (
            await db.execute(
                select(Finding).where(Finding.diagnostic_id == diagnostic.id)
            )
        )
        .scalars()
        .all()
    }

    for brecha in brechas:
        pregunta = preguntas_por_id[brecha.pregunta_id]
        description = f"Brecha detectada en la pregunta: {pregunta.texto}"
        risk = RiskLevel(brecha.riesgo.lower())
        existente = hallazgos_existentes.get(brecha.pregunta_id)
        if existente is None:
            db.add(
                Finding(
                    organization_id=diagnostic.organization_id,
                    diagnostic_id=diagnostic.id,
                    pregunta_id=brecha.pregunta_id,
                    description=description,
                    risk=risk,
                    status=FindingStatus.abierto,
                )
            )
        else:
            existente.description = description
            existente.risk = risk
            if existente.status == FindingStatus.cerrado:
                existente.status = FindingStatus.abierto

    for pregunta_id, hallazgo in hallazgos_existentes.items():
        if (
            pregunta_id not in detectadas_por_pregunta
            and hallazgo.status != FindingStatus.cerrado
        ):
            hallazgo.status = FindingStatus.cerrado

    # Fix de la revisión del PR #13 (hallazgo #2): toda respuesta nueva puede
    # cambiar puntajes/hallazgos, así que un informe ya generado (Tarea 4)
    # deja de reflejar el estado actual del diagnóstico. Se invalida en vez
    # de dejarlo obsoleto en silencio — el usuario debe pedir uno nuevo
    # (POST /diagnostico/informe) para verlo actualizado.
    if diagnostic.informe_ia is not None or diagnostic.informe_generado_en is not None:
        diagnostic.informe_ia = None
        diagnostic.informe_generado_en = None
