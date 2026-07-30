"""Seed de la configuración versionada del cuestionario de autodiagnóstico (Módulo 1).

Carga docs/Modulo1/cuestionario_autodiagnostico_config.json —fuente de verdad,
no se inventan valores— en `obligaciones`, `secciones` y `preguntas` (contenido
fijo, fiel a la guía CCS), y crea `config_versiones` v1 (activa) con sus filas
de `config_seccion_pesos` y `config_pregunta_riesgo`.

Uso:
    cd backend
    python -m scripts.seed_modulo1_cuestionario
    python -m scripts.seed_modulo1_cuestionario --creado-por <uuid-de-un-perfil-existente>

Sin --creado-por usa/crea un perfil superadmin fijo de desarrollo (mismo
patrón de IDs fijos que scripts/seed_dev.py). Con --creado-por, el perfil debe
existir de antemano — el script no fabrica identidades para un id ajeno.

Idempotente: si ya existe `config_versiones` con numero_version=1, no hace nada.
"""

import argparse
import asyncio
import json
import uuid
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
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

settings = get_settings()

CONFIG_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "docs"
    / "Modulo1"
    / "cuestionario_autodiagnostico_config.json"
)

# IDs fijos para el superadmin de desarrollo (mismo patrón que seed_dev.py)
DEV_SUPERADMIN_PROFILE_ID = uuid.UUID("40000000-0000-0000-0000-000000000001")
DEV_SUPERADMIN_AUTH_USER_ID = uuid.UUID("40000000-0000-0000-0000-000000000002")

_NIVELES_RIESGO_VALIDOS = {"Alto", "Medio", "Bajo"}


def _validar_config(data: dict) -> None:
    """Chequeo de integridad del archivo antes de escribir nada en la BD.

    No reemplaza la validación del service layer (paso 3, sobre lo que envía
    el panel admin): esto solo confirma que el JSON fuente no está corrupto o
    editado a mano de forma inconsistente.
    """
    secciones = data["secciones"]
    if len(secciones) != 10:
        raise SystemExit(f"Se esperaban 10 secciones; el JSON trae {len(secciones)}.")

    total_preguntas = sum(len(s["preguntas"]) for s in secciones)
    if total_preguntas != 50:
        raise SystemExit(f"Se esperaban 50 preguntas; el JSON trae {total_preguntas}.")

    suma_pesos = sum(s["peso_pct"] for s in secciones)
    if abs(suma_pesos - 100) > 0.01:
        raise SystemExit(
            f"Los peso_pct de las secciones suman {suma_pesos}; deberían sumar 100."
        )

    for seccion in secciones:
        for pregunta in seccion["preguntas"]:
            if pregunta["riesgo"] not in _NIVELES_RIESGO_VALIDOS:
                raise SystemExit(
                    f"Riesgo inválido '{pregunta['riesgo']}' en pregunta {pregunta['id']}."
                )


async def _resolver_creado_por(
    db: AsyncSession, creado_por: uuid.UUID | None
) -> Profile:
    if creado_por is not None:
        profile = await db.get(Profile, creado_por)
        if profile is None:
            raise SystemExit(
                f"No existe un perfil con id={creado_por}. "
                "Pásalo con --creado-por apuntando a un perfil real, o "
                "usa el default de desarrollo omitiendo el flag."
            )
        return profile

    profile = await db.get(Profile, DEV_SUPERADMIN_PROFILE_ID)
    if profile is None:
        profile = Profile(
            id=DEV_SUPERADMIN_PROFILE_ID,
            auth_user_id=DEV_SUPERADMIN_AUTH_USER_ID,
            email="superadmin@cumpleia.cl",
            full_name="Superadmin Demo",
            is_superadmin=True,
        )
        db.add(profile)
        await db.flush()
    elif not profile.is_superadmin:
        profile.is_superadmin = True
    return profile


async def seed(db: AsyncSession, creado_por: uuid.UUID | None) -> None:
    existing = await db.execute(
        select(ConfigVersion).where(ConfigVersion.numero_version == 1)
    )
    if existing.scalar_one_or_none() is not None:
        print("La configuración v1 del cuestionario ya existe. Nada que hacer.")
        return

    data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    _validar_config(data)

    profile = await _resolver_creado_por(db, creado_por)

    # Sin relationship() entre estos modelos (estilo plano del resto del
    # repo), el unit-of-work de SQLAlchemy no infiere el orden de inserción
    # entre tablas distintas a partir de las FKs del esquema: hay que
    # flushear cada nivel antes de insertar el que depende de él.
    for obligacion in data["obligaciones"]:
        db.add(
            Obligacion(
                id=obligacion["id"],
                numero_guia=obligacion["numero_guia"],
                nombre=obligacion["nombre"],
            )
        )
    await db.flush()

    for orden_seccion, seccion in enumerate(data["secciones"], start=1):
        db.add(
            Seccion(
                id=seccion["id"],
                numero_romano=seccion["numero"],
                nombre=seccion["nombre"],
                obligacion_id=seccion["obligacion_id"],
                orden=orden_seccion,
            )
        )
    await db.flush()

    for seccion in data["secciones"]:
        for orden_pregunta, pregunta in enumerate(seccion["preguntas"], start=1):
            db.add(
                Pregunta(
                    id=pregunta["id"],
                    seccion_id=seccion["id"],
                    texto=pregunta["texto"],
                    orden=orden_pregunta,
                )
            )
    await db.flush()

    version = ConfigVersion(
        numero_version=1,
        activa=True,
        nota="Versión inicial cargada desde cuestionario_autodiagnostico_config.json",
        creado_por=profile.id,
    )
    db.add(version)
    await db.flush()

    for seccion in data["secciones"]:
        db.add(
            ConfigSeccionPeso(
                version_id=version.id,
                seccion_id=seccion["id"],
                peso_pct=seccion["peso_pct"],
            )
        )
        for pregunta in seccion["preguntas"]:
            db.add(
                ConfigPreguntaRiesgo(
                    version_id=version.id,
                    pregunta_id=pregunta["id"],
                    riesgo=RiskLevel(pregunta["riesgo"].lower()),
                )
            )

    await db.commit()

    print("Configuración del cuestionario cargada correctamente.")
    print(f"  Obligaciones : {len(data['obligaciones'])}")
    print(f"  Secciones    : {len(data['secciones'])}")
    print(f"  Preguntas    : {sum(len(s['preguntas']) for s in data['secciones'])}")
    print(f"  Versión      : {version.numero_version} (activa)")
    print(f"  Creado por   : {profile.id}  ({profile.email})")


async def main(args: argparse.Namespace) -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    SessionLocal = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with SessionLocal() as db:
        await seed(db, args.creado_por)
    await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Seed de la configuración versionada del cuestionario (Módulo 1)"
    )
    parser.add_argument(
        "--creado-por",
        type=uuid.UUID,
        default=None,
        help="ID de un perfil superadmin existente (default: perfil de desarrollo fijo)",
    )
    asyncio.run(main(parser.parse_args()))
