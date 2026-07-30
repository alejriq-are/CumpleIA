"""Configuración versionada del cuestionario de autodiagnóstico (Módulo 1).

Contenido fijo (obligaciones/secciones/preguntas, fuente CCS) + parámetros de
negocio versionados (peso_pct por sección, riesgo por pregunta) — ver
migración 0002 y docs/Modulo1/. La API expone el riesgo como 'Alto'/'Medio'/
'Bajo' (SPEC_admin_config_cuestionario.md); la base lo guarda en minúscula
reutilizando el enum `risk_level` compartido con `findings.risk` — la
conversión de casing vive solo aquí, en el borde servicio↔API.
"""

import uuid
from dataclasses import dataclass

from fastapi import HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    ConfigPreguntaRiesgo,
    ConfigSeccionPeso,
    ConfigVersion,
    Obligacion,
    Pregunta,
    Profile,
    RiskLevel,
    Seccion,
)

TOTAL_SECCIONES = 10
TOTAL_PREGUNTAS = 50
SUMA_PESO_ESPERADA = 100


@dataclass(frozen=True)
class SeccionPesoInput:
    seccion_id: str
    peso_pct: int


@dataclass(frozen=True)
class PreguntaRiesgoInput:
    pregunta_id: str
    riesgo: str  # 'Alto' | 'Medio' | 'Bajo', tal como llega de la API


@dataclass(frozen=True)
class ConfigActiva:
    version: ConfigVersion
    creado_por_profile: Profile
    obligaciones: list[Obligacion]
    secciones: list[Seccion]
    peso_por_seccion: dict[str, int]
    preguntas: list[Pregunta]
    riesgo_por_pregunta: dict[str, str]  # 'Alto' | 'Medio' | 'Bajo'


async def _ids_canonicos(db: AsyncSession) -> tuple[set[str], set[str]]:
    seccion_ids = set((await db.execute(select(Seccion.id))).scalars().all())
    pregunta_ids = set((await db.execute(select(Pregunta.id))).scalars().all())
    return seccion_ids, pregunta_ids


def _bad_request(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


async def validar_guardado(
    db: AsyncSession,
    pesos: list[SeccionPesoInput],
    riesgos: list[PreguntaRiesgoInput],
) -> None:
    """Valida el payload de guardado ANTES de escribir nada en la base.

    Lanza HTTPException(400) con el primer problema encontrado. Solo hace
    SELECT sobre contenido fijo (secciones/preguntas); ningún INSERT/UPDATE
    ocurre hasta que esta función retorna sin lanzar — así una validación
    fallida nunca deja una versión a medio escribir.
    """
    seccion_ids, pregunta_ids = await _ids_canonicos(db)

    ids_pesos = [p.seccion_id for p in pesos]
    if len(ids_pesos) != len(set(ids_pesos)):
        raise _bad_request("Hay secciones repetidas en los pesos enviados.")

    seccion_ids_payload = set(ids_pesos)
    if seccion_ids_payload != seccion_ids:
        faltantes = sorted(seccion_ids - seccion_ids_payload)
        sobrantes = sorted(seccion_ids_payload - seccion_ids)
        detalle = []
        if faltantes:
            detalle.append(f"faltan: {faltantes}")
        if sobrantes:
            detalle.append(f"desconocidas: {sobrantes}")
        raise _bad_request(
            f"Deben venir las {TOTAL_SECCIONES} secciones con peso, ni más ni "
            f"menos ({'; '.join(detalle)})."
        )

    suma_pesos = sum(p.peso_pct for p in pesos)
    if suma_pesos != SUMA_PESO_ESPERADA:
        raise _bad_request(
            f"Los peso_pct deben sumar {SUMA_PESO_ESPERADA}; suman {suma_pesos}."
        )

    ids_riesgos = [r.pregunta_id for r in riesgos]
    if len(ids_riesgos) != len(set(ids_riesgos)):
        raise _bad_request("Hay preguntas repetidas en los riesgos enviados.")

    pregunta_ids_payload = set(ids_riesgos)
    if pregunta_ids_payload != pregunta_ids:
        faltantes = sorted(pregunta_ids - pregunta_ids_payload)
        sobrantes = sorted(pregunta_ids_payload - pregunta_ids)
        detalle = []
        if faltantes:
            detalle.append(f"faltan: {faltantes}")
        if sobrantes:
            detalle.append(f"desconocidas: {sobrantes}")
        raise _bad_request(
            f"Deben venir las {TOTAL_PREGUNTAS} preguntas con riesgo, ni más ni "
            f"menos ({'; '.join(detalle)})."
        )


async def crear_nueva_version(
    db: AsyncSession,
    creado_por: uuid.UUID,
    nota: str | None,
    pesos: list[SeccionPesoInput],
    riesgos: list[PreguntaRiesgoInput],
) -> ConfigVersion:
    """Crea la nueva versión activa. Llamar solo después de `validar_guardado`.

    Desactiva la versión vigente ANTES de insertar la nueva: el índice único
    parcial `ux_config_versiones_activa` (activa WHERE activa) no admite dos
    filas con activa=true a la vez, ni siquiera brevemente dentro de la misma
    transacción — a diferencia del pseudocódigo de referencia en
    schema_modulo1_cuestionario.sql, que las inserta en el otro orden.
    """
    await db.execute(
        update(ConfigVersion).where(ConfigVersion.activa.is_(True)).values(activa=False)
    )

    numero_actual = (
        await db.execute(select(func.max(ConfigVersion.numero_version)))
    ).scalar() or 0

    version = ConfigVersion(
        numero_version=numero_actual + 1,
        activa=True,
        nota=nota,
        creado_por=creado_por,
    )
    db.add(version)
    await db.flush()

    for peso in pesos:
        db.add(
            ConfigSeccionPeso(
                version_id=version.id,
                seccion_id=peso.seccion_id,
                peso_pct=peso.peso_pct,
            )
        )
    for riesgo in riesgos:
        db.add(
            ConfigPreguntaRiesgo(
                version_id=version.id,
                pregunta_id=riesgo.pregunta_id,
                riesgo=RiskLevel(riesgo.riesgo.lower()),
            )
        )
    await db.flush()
    return version


async def obtener_config_activa(db: AsyncSession) -> ConfigActiva:
    version = (
        await db.execute(select(ConfigVersion).where(ConfigVersion.activa.is_(True)))
    ).scalar_one_or_none()
    if version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "No hay una versión de configuración activa. "
                "Ejecuta scripts.seed_modulo1_cuestionario."
            ),
        )

    creado_por_profile = await db.get(Profile, version.creado_por)

    obligaciones = (await db.execute(select(Obligacion))).scalars().all()
    secciones = (
        (await db.execute(select(Seccion).order_by(Seccion.orden))).scalars().all()
    )
    preguntas = (
        (await db.execute(select(Pregunta).order_by(Pregunta.orden))).scalars().all()
    )

    pesos = (
        (
            await db.execute(
                select(ConfigSeccionPeso).where(
                    ConfigSeccionPeso.version_id == version.id
                )
            )
        )
        .scalars()
        .all()
    )
    riesgos = (
        (
            await db.execute(
                select(ConfigPreguntaRiesgo).where(
                    ConfigPreguntaRiesgo.version_id == version.id
                )
            )
        )
        .scalars()
        .all()
    )

    return ConfigActiva(
        version=version,
        creado_por_profile=creado_por_profile,
        obligaciones=list(obligaciones),
        secciones=list(secciones),
        peso_por_seccion={p.seccion_id: int(p.peso_pct) for p in pesos},
        preguntas=list(preguntas),
        riesgo_por_pregunta={
            r.pregunta_id: r.riesgo.value.capitalize() for r in riesgos
        },
    )
