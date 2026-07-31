"""Tests funcionales de GET/POST /cuestionario-config (Módulo 1, paso 3).

Cubre lectura de la config activa y guardado de una nueva versión con su
validación previa (10 secciones con peso sumando 100, 50 preguntas con
riesgo asignado). El test de aislamiento RLS/multi-tenant específico del
paso 5 del prompt de Módulo 1 vive en su propio archivo.

Requiere el seed de scripts/seed_modulo1_cuestionario.py ya aplicado (v1
activa) — igual que el resto de la suite, corre contra Docker Postgres.
"""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select, update

from app.core.deps import get_current_profile
from app.db.models import (
    ConfigPreguntaRiesgo,
    ConfigSeccionPeso,
    ConfigVersion,
    Profile,
)
from app.db.session import get_db
from app.main import app
from tests.conftest import _make_profile_override_from_db, _make_rls_db_override

_SUPERADMIN_PROFILE_ID = uuid.uuid4()
_SUPERADMIN_AUTH_ID = uuid.uuid4()


@pytest_asyncio.fixture
async def superadmin_client(_session_factory, _app_session_factory):
    """AsyncClient autenticado como un perfil con is_superadmin=True.

    Corre contra `app_user` con RLS activo (mismas fixtures que client_a/
    client_b en conftest.py) para que la política `..._insert WITH CHECK
    (is_superadmin())` de la migración 0002 se ejerza de verdad, no solo el
    guard de FastAPI (`require_superadmin` en app/core/deps.py). El alta y
    baja del perfil de test sí usan el rol admin (`_session_factory`): es
    setup/teardown de fixture, no la sesión que sirve el request bajo prueba.
    """
    async with _session_factory() as session:
        session.add(
            Profile(
                id=_SUPERADMIN_PROFILE_ID,
                auth_user_id=_SUPERADMIN_AUTH_ID,
                email="superadmin_test@cumpleia.cl",
                is_superadmin=True,
            )
        )
        await session.commit()

    app.dependency_overrides[get_current_profile] = _make_profile_override_from_db(
        _SUPERADMIN_AUTH_ID
    )
    app.dependency_overrides[get_db] = _make_rls_db_override(
        _SUPERADMIN_AUTH_ID, _app_session_factory
    )
    yield app
    app.dependency_overrides.pop(get_current_profile, None)
    app.dependency_overrides.pop(get_db, None)

    async with _session_factory() as session:
        await session.execute(
            delete(Profile).where(Profile.id == _SUPERADMIN_PROFILE_ID)
        )
        await session.commit()


@pytest_asyncio.fixture
async def _restaurar_v1_como_activa(_session_factory):
    """Borra cualquier versión creada por el test y reactiva v1.

    config_versiones es append-only por diseño (sin política RLS de DELETE),
    pero este fixture usa `database_url` (dueño de las tablas, sin RLS) —
    igual que el resto de los fixtures de test — para dejar la BD de dev
    como estaba antes del test, sin depender del orden de ejecución.
    """
    yield
    async with _session_factory() as session:
        otras_versiones = select(ConfigVersion.id).where(
            ConfigVersion.numero_version != 1
        )
        await session.execute(
            delete(ConfigPreguntaRiesgo).where(
                ConfigPreguntaRiesgo.version_id.in_(otras_versiones)
            )
        )
        await session.execute(
            delete(ConfigSeccionPeso).where(
                ConfigSeccionPeso.version_id.in_(otras_versiones)
            )
        )
        await session.execute(
            delete(ConfigVersion).where(ConfigVersion.numero_version != 1)
        )
        await session.execute(
            update(ConfigVersion)
            .where(ConfigVersion.numero_version == 1)
            .values(activa=True)
        )
        await session.commit()


@pytest.mark.asyncio
async def test_lectura_config_activa_disponible_a_cualquier_autenticado(client_a):
    async with AsyncClient(
        transport=ASGITransport(app=client_a), base_url="http://test"
    ) as client:
        resp = await client.get("/cuestionario-config")

    assert resp.status_code == 200
    data = resp.json()
    assert data["version"]["activa"] is True
    assert len(data["secciones"]) == 10
    assert len(data["preguntas"]) == 50
    assert sum(s["peso_pct"] for s in data["secciones"]) == 100
    assert all(p["riesgo"] in ("Alto", "Medio", "Bajo") for p in data["preguntas"])


@pytest.mark.asyncio
async def test_guardado_rechaza_a_usuario_no_superadmin(client_a):
    async with AsyncClient(
        transport=ASGITransport(app=client_a), base_url="http://test"
    ) as client:
        resp = await client.post(
            "/cuestionario-config", json={"pesos": [], "riesgos": []}
        )

    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_guardado_rechaza_pesos_incompletos_sin_tocar_bd(
    superadmin_client, _session_factory, _restaurar_v1_como_activa
):
    async with AsyncClient(
        transport=ASGITransport(app=superadmin_client), base_url="http://test"
    ) as client:
        activa = (await client.get("/cuestionario-config")).json()
        pesos = [
            {"seccion_id": s["id"], "peso_pct": s["peso_pct"]}
            for s in activa["secciones"]
        ][
            :-1
        ]  # falta una sección a propósito
        riesgos = [
            {"pregunta_id": p["id"], "riesgo": p["riesgo"]} for p in activa["preguntas"]
        ]

        resp = await client.post(
            "/cuestionario-config", json={"pesos": pesos, "riesgos": riesgos}
        )

    assert resp.status_code == 400

    async with _session_factory() as session:
        versiones = (await session.execute(select(ConfigVersion))).scalars().all()
    assert len(versiones) == 1  # sigue solo la v1 del seed


@pytest.mark.asyncio
async def test_guardado_rechaza_suma_de_pesos_distinta_de_100(
    superadmin_client, _session_factory, _restaurar_v1_como_activa
):
    async with AsyncClient(
        transport=ASGITransport(app=superadmin_client), base_url="http://test"
    ) as client:
        activa = (await client.get("/cuestionario-config")).json()
        pesos = [
            {"seccion_id": s["id"], "peso_pct": s["peso_pct"]}
            for s in activa["secciones"]
        ]
        pesos[0]["peso_pct"] += 5  # rompe la suma = 100
        riesgos = [
            {"pregunta_id": p["id"], "riesgo": p["riesgo"]} for p in activa["preguntas"]
        ]

        resp = await client.post(
            "/cuestionario-config", json={"pesos": pesos, "riesgos": riesgos}
        )

    assert resp.status_code == 400

    async with _session_factory() as session:
        versiones = (await session.execute(select(ConfigVersion))).scalars().all()
    assert len(versiones) == 1


@pytest.mark.asyncio
async def test_guardado_crea_nueva_version_activa(
    superadmin_client, _session_factory, _restaurar_v1_como_activa
):
    async with AsyncClient(
        transport=ASGITransport(app=superadmin_client), base_url="http://test"
    ) as client:
        activa = (await client.get("/cuestionario-config")).json()
        version_anterior = activa["version"]["numero_version"]

        pesos = [
            {"seccion_id": s["id"], "peso_pct": s["peso_pct"]}
            for s in activa["secciones"]
        ]
        riesgos = [
            {"pregunta_id": p["id"], "riesgo": p["riesgo"]} for p in activa["preguntas"]
        ]
        # Mueve 1 punto entre dos secciones: cambia el contenido, mantiene la suma en 100
        pesos[0]["peso_pct"] += 1
        pesos[1]["peso_pct"] -= 1

        resp = await client.post(
            "/cuestionario-config",
            json={"nota": "ajuste de prueba", "pesos": pesos, "riesgos": riesgos},
        )

    assert resp.status_code == 201
    nueva = resp.json()
    assert nueva["version"]["numero_version"] == version_anterior + 1
    assert nueva["version"]["activa"] is True
    assert nueva["version"]["creado_por"]["email"] == "superadmin_test@cumpleia.cl"

    # La versión anterior queda desactivada (índice único parcial de una sola activa)
    async with _session_factory() as session:
        anterior = (
            await session.execute(
                select(ConfigVersion).where(
                    ConfigVersion.numero_version == version_anterior
                )
            )
        ).scalar_one()
    assert anterior.activa is False
