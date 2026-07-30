"""Configuración versionada del cuestionario de autodiagnóstico (Módulo 1).

Lectura: cualquier perfil autenticado (la config activa es global, no
tenant-scoped — toda organización la necesita para responder el cuestionario).
Guardado: solo `superadmin` (ver SPEC_admin_config_cuestionario.md).
"""

import uuid
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentProfile, SuperadminProfile
from app.db.session import get_db
from app.services.cuestionario_config import (
    ConfigActiva,
    PreguntaRiesgoInput,
    SeccionPesoInput,
    crear_nueva_version,
    obtener_config_activa,
    validar_guardado,
)

router = APIRouter(prefix="/cuestionario-config", tags=["cuestionario-config"])

RiesgoDisplay = Literal["Alto", "Medio", "Bajo"]


class ObligacionOut(BaseModel):
    id: str
    numero_guia: str
    nombre: str


class SeccionOut(BaseModel):
    id: str
    numero_romano: str
    nombre: str
    obligacion_id: str
    orden: int
    peso_pct: int


class PreguntaOut(BaseModel):
    id: str
    seccion_id: str
    texto: str
    orden: int
    riesgo: RiesgoDisplay


class CreadoPorOut(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str | None


class ConfigVersionOut(BaseModel):
    numero_version: int
    activa: bool
    nota: str | None
    creado_en: datetime
    creado_por: CreadoPorOut


class ConfigCuestionarioOut(BaseModel):
    version: ConfigVersionOut
    obligaciones: list[ObligacionOut]
    secciones: list[SeccionOut]
    preguntas: list[PreguntaOut]


class SeccionPesoIn(BaseModel):
    seccion_id: str
    peso_pct: int = Field(ge=0, le=100)


class PreguntaRiesgoIn(BaseModel):
    pregunta_id: str
    riesgo: RiesgoDisplay


class GuardarConfigRequest(BaseModel):
    nota: str | None = None
    pesos: list[SeccionPesoIn]
    riesgos: list[PreguntaRiesgoIn]


def _a_response(data: ConfigActiva) -> ConfigCuestionarioOut:
    return ConfigCuestionarioOut(
        version=ConfigVersionOut(
            numero_version=data.version.numero_version,
            activa=data.version.activa,
            nota=data.version.nota,
            creado_en=data.version.creado_en,
            creado_por=CreadoPorOut(
                id=data.creado_por_profile.id,
                email=data.creado_por_profile.email,
                full_name=data.creado_por_profile.full_name,
            ),
        ),
        obligaciones=[
            ObligacionOut(id=o.id, numero_guia=o.numero_guia, nombre=o.nombre)
            for o in data.obligaciones
        ],
        secciones=[
            SeccionOut(
                id=s.id,
                numero_romano=s.numero_romano,
                nombre=s.nombre,
                obligacion_id=s.obligacion_id,
                orden=s.orden,
                peso_pct=data.peso_por_seccion[s.id],
            )
            for s in data.secciones
        ],
        preguntas=[
            PreguntaOut(
                id=p.id,
                seccion_id=p.seccion_id,
                texto=p.texto,
                orden=p.orden,
                riesgo=data.riesgo_por_pregunta[p.id],
            )
            for p in data.preguntas
        ],
    )


@router.get("", response_model=ConfigCuestionarioOut)
async def leer_config_activa(
    current_profile: CurrentProfile,
    db: AsyncSession = Depends(get_db),
) -> ConfigCuestionarioOut:
    data = await obtener_config_activa(db)
    return _a_response(data)


@router.post(
    "", response_model=ConfigCuestionarioOut, status_code=status.HTTP_201_CREATED
)
async def guardar_nueva_version(
    payload: GuardarConfigRequest,
    superadmin: SuperadminProfile,
    db: AsyncSession = Depends(get_db),
) -> ConfigCuestionarioOut:
    """Crea una nueva versión de la configuración (append-only).

    Valida ANTES de escribir: 10 secciones con peso sumando 100, 50 preguntas
    con riesgo asignado. Si algo falla, responde 400 y no toca la base de
    datos (ver `validar_guardado`).
    """
    pesos = [
        SeccionPesoInput(seccion_id=p.seccion_id, peso_pct=p.peso_pct)
        for p in payload.pesos
    ]
    riesgos = [
        PreguntaRiesgoInput(pregunta_id=r.pregunta_id, riesgo=r.riesgo)
        for r in payload.riesgos
    ]

    await validar_guardado(db, pesos, riesgos)
    await crear_nueva_version(db, superadmin.id, payload.nota, pesos, riesgos)

    data = await obtener_config_activa(db)
    return _a_response(data)
