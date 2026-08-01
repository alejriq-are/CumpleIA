"""Tests funcionales de GET/POST /diagnostico/* (Módulo 1, Tareas 3 y 4).

Ejercen los endpoints extremo a extremo contra `app_user` con RLS activo
(mismas fixtures `client_a`/`client_b` de conftest.py). El aislamiento RLS a
nivel de fila (INSERT/SELECT directos contra Postgres) vive en
test_rls_isolation_diagnosticos.py; este archivo cubre la capa de API: forma
de la respuesta, wiring de permisos (`require_permission`, primer consumidor
real — ver app/core/deps.py) y el ciclo de vida completo de un diagnóstico.

`POST /diagnostico/informe` (Tarea 4) mockea `diagnostico_ia.generar_informe`
— el guardarraíl de citas/finding_id y la exclusión de ley_19628 ya se prueban
en test_diagnostico_ia.py; aquí solo se cubre el wiring HTTP (404/409/200).

Requiere el seed de scripts/seed_modulo1_cuestionario.py ya aplicado (v1
activa, 50 preguntas), igual que el resto de la suite del Módulo 1.
"""

import uuid
from datetime import UTC, datetime

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select

from app.api import diagnostico as diagnostico_api
from app.core.deps import get_current_profile
from app.db.models import (
    Diagnostic,
    DiagnosticAnswer,
    Finding,
    Membership,
    Profile,
    UserRole,
)
from app.db.session import get_db
from app.main import app
from tests.conftest import _make_profile_override_from_db, _make_rls_db_override

_VIEWER_PROFILE_ID = uuid.uuid4()
_VIEWER_AUTH_ID = uuid.uuid4()


@pytest_asyncio.fixture(autouse=True)
async def _limpiar_diagnostico_org_a(_session_factory, org_a_id):
    """A lo sumo un Diagnostic por organización (UNIQUE desde la migración
    0005): limpia antes y después de cada test para no chocar con el
    siguiente ni con lo que haya dejado un run anterior."""

    async def _borrar():
        async with _session_factory() as session:
            diagnostic_ids = (
                (
                    await session.execute(
                        select(Diagnostic.id).where(
                            Diagnostic.organization_id == org_a_id
                        )
                    )
                )
                .scalars()
                .all()
            )
            if diagnostic_ids:
                await session.execute(
                    delete(Finding).where(Finding.diagnostic_id.in_(diagnostic_ids))
                )
                await session.execute(
                    delete(DiagnosticAnswer).where(
                        DiagnosticAnswer.diagnostic_id.in_(diagnostic_ids)
                    )
                )
                await session.execute(
                    delete(Diagnostic).where(Diagnostic.id.in_(diagnostic_ids))
                )
                await session.commit()

    await _borrar()
    yield
    await _borrar()


@pytest_asyncio.fixture
async def viewer_client_org_a(_session_factory, _app_session_factory, org_a_id):
    """Cliente autenticado con rol `viewer` en la organización A.

    `client_a` (conftest.py) es `owner` — tiene todos los permisos y no sirve
    para probar el 403 de `edit_content` en `POST /diagnostico/respuestas`.
    """
    async with _session_factory() as session:
        session.add(
            Profile(
                id=_VIEWER_PROFILE_ID,
                auth_user_id=_VIEWER_AUTH_ID,
                email="viewer_diagnostico_test@cumpleia.cl",
            )
        )
        await session.flush()
        session.add(
            Membership(
                organization_id=org_a_id,
                profile_id=_VIEWER_PROFILE_ID,
                role=UserRole.viewer,
            )
        )
        await session.commit()

    app.dependency_overrides[get_current_profile] = _make_profile_override_from_db(
        _VIEWER_AUTH_ID
    )
    app.dependency_overrides[get_db] = _make_rls_db_override(
        _VIEWER_AUTH_ID, _app_session_factory
    )
    yield app
    app.dependency_overrides.pop(get_current_profile, None)
    app.dependency_overrides.pop(get_db, None)

    async with _session_factory() as session:
        await session.execute(
            delete(Membership).where(Membership.profile_id == _VIEWER_PROFILE_ID)
        )
        await session.execute(delete(Profile).where(Profile.id == _VIEWER_PROFILE_ID))
        await session.commit()


@pytest.mark.asyncio
async def test_cuestionario_devuelve_catalogo_completo(client_a, org_a_id):
    async with AsyncClient(
        transport=ASGITransport(app=client_a), base_url="http://test"
    ) as client:
        resp = await client.get(
            "/diagnostico/cuestionario", headers={"X-Organization-Id": str(org_a_id)}
        )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["secciones"]) == 10
    assert len(data["preguntas"]) == 50
    assert set(data["opciones_respuesta"]) == {"Sí", "Parcial", "No", "N/A"}


@pytest.mark.asyncio
async def test_actual_404_sin_diagnostico_previo(client_a, org_a_id):
    async with AsyncClient(
        transport=ASGITransport(app=client_a), base_url="http://test"
    ) as client:
        resp = await client.get(
            "/diagnostico/actual", headers={"X-Organization-Id": str(org_a_id)}
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_viewer_puede_leer_pero_no_guardar_respuestas(
    viewer_client_org_a, org_a_id
):
    async with AsyncClient(
        transport=ASGITransport(app=viewer_client_org_a), base_url="http://test"
    ) as client:
        lectura = await client.get(
            "/diagnostico/cuestionario", headers={"X-Organization-Id": str(org_a_id)}
        )
        escritura = await client.post(
            "/diagnostico/respuestas",
            headers={"X-Organization-Id": str(org_a_id)},
            json={"respuestas": [{"pregunta_id": "S1Q1", "answer": "Sí"}]},
        )
    assert lectura.status_code == 200
    assert escritura.status_code == 403


@pytest.mark.asyncio
async def test_guardar_pregunta_desconocida_devuelve_400(client_a, org_a_id):
    async with AsyncClient(
        transport=ASGITransport(app=client_a), base_url="http://test"
    ) as client:
        resp = await client.post(
            "/diagnostico/respuestas",
            headers={"X-Organization-Id": str(org_a_id)},
            json={"respuestas": [{"pregunta_id": "NO-EXISTE", "answer": "Sí"}]},
        )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_ciclo_completo_guarda_calcula_y_completa(client_a, org_a_id):
    async with AsyncClient(
        transport=ASGITransport(app=client_a), base_url="http://test"
    ) as client:
        cuestionario = (
            await client.get(
                "/diagnostico/cuestionario",
                headers={"X-Organization-Id": str(org_a_id)},
            )
        ).json()
        pregunta_ids = [p["id"] for p in cuestionario["preguntas"]]
        preguntas_con_brecha = set(pregunta_ids[:3])

        respuestas = [
            {
                "pregunta_id": pid,
                "answer": "No" if pid in preguntas_con_brecha else "Sí",
            }
            for pid in pregunta_ids
        ]
        resp = await client.post(
            "/diagnostico/respuestas",
            headers={"X-Organization-Id": str(org_a_id)},
            json={"respuestas": respuestas},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "completado"
        assert data["global_score"] is not None
        assert 0 <= data["global_score"] <= 100
        assert len(data["respuestas"]) == 50
        assert {h["pregunta_id"] for h in data["hallazgos"]} == preguntas_con_brecha
        assert all(h["status"] == "abierto" for h in data["hallazgos"])
        assert all(h["risk"] in ("Alto", "Medio", "Bajo") for h in data["hallazgos"])

        actual = (
            await client.get(
                "/diagnostico/actual", headers={"X-Organization-Id": str(org_a_id)}
            )
        ).json()
        assert actual["id"] == data["id"]
        assert actual["status"] == "completado"
        assert len(actual["hallazgos"]) == 3


@pytest.mark.asyncio
async def test_alternar_respuesta_cierra_hallazgo_sin_borrarlo(client_a, org_a_id):
    async with AsyncClient(
        transport=ASGITransport(app=client_a), base_url="http://test"
    ) as client:
        cuestionario = (
            await client.get(
                "/diagnostico/cuestionario",
                headers={"X-Organization-Id": str(org_a_id)},
            )
        ).json()
        pregunta_id = cuestionario["preguntas"][0]["id"]

        abrir = await client.post(
            "/diagnostico/respuestas",
            headers={"X-Organization-Id": str(org_a_id)},
            json={"respuestas": [{"pregunta_id": pregunta_id, "answer": "No"}]},
        )
        hallazgo_id = next(
            h["id"]
            for h in abrir.json()["hallazgos"]
            if h["pregunta_id"] == pregunta_id
        )
        assert (
            next(h for h in abrir.json()["hallazgos"] if h["id"] == hallazgo_id)[
                "status"
            ]
            == "abierto"
        )

        cerrar = await client.post(
            "/diagnostico/respuestas",
            headers={"X-Organization-Id": str(org_a_id)},
            json={"respuestas": [{"pregunta_id": pregunta_id, "answer": "Sí"}]},
        )
        hallazgo_cerrado = next(
            h for h in cerrar.json()["hallazgos"] if h["id"] == hallazgo_id
        )
        assert hallazgo_cerrado["status"] == "cerrado"


@pytest.mark.asyncio
async def test_informe_404_sin_diagnostico_previo(client_a, org_a_id):
    async with AsyncClient(
        transport=ASGITransport(app=client_a), base_url="http://test"
    ) as client:
        resp = await client.post(
            "/diagnostico/informe", headers={"X-Organization-Id": str(org_a_id)}
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_informe_409_con_diagnostico_en_progreso(client_a, org_a_id):
    async with AsyncClient(
        transport=ASGITransport(app=client_a), base_url="http://test"
    ) as client:
        cuestionario = (
            await client.get(
                "/diagnostico/cuestionario",
                headers={"X-Organization-Id": str(org_a_id)},
            )
        ).json()
        pregunta_id = cuestionario["preguntas"][0]["id"]
        await client.post(
            "/diagnostico/respuestas",
            headers={"X-Organization-Id": str(org_a_id)},
            json={"respuestas": [{"pregunta_id": pregunta_id, "answer": "Sí"}]},
        )

        resp = await client.post(
            "/diagnostico/informe", headers={"X-Organization-Id": str(org_a_id)}
        )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_informe_200_con_diagnostico_completado_y_reflejado_en_actual(
    client_a, org_a_id, monkeypatch
):
    async def _fake_generar_informe(db, diagnostic):
        diagnostic.informe_ia = {
            "resumen_ejecutivo": "Resumen mock.",
            "narrativas": [],
        }
        diagnostic.informe_generado_en = datetime.now(UTC)
        return diagnostic.informe_ia

    monkeypatch.setattr(
        diagnostico_api.diagnostico_ia, "generar_informe", _fake_generar_informe
    )

    async with AsyncClient(
        transport=ASGITransport(app=client_a), base_url="http://test"
    ) as client:
        cuestionario = (
            await client.get(
                "/diagnostico/cuestionario",
                headers={"X-Organization-Id": str(org_a_id)},
            )
        ).json()
        respuestas = [
            {"pregunta_id": p["id"], "answer": "Sí"} for p in cuestionario["preguntas"]
        ]
        await client.post(
            "/diagnostico/respuestas",
            headers={"X-Organization-Id": str(org_a_id)},
            json={"respuestas": respuestas},
        )

        resp = await client.post(
            "/diagnostico/informe", headers={"X-Organization-Id": str(org_a_id)}
        )
        assert resp.status_code == 200
        assert resp.json()["informe"]["resumen_ejecutivo"] == "Resumen mock."

        actual = (
            await client.get(
                "/diagnostico/actual", headers={"X-Organization-Id": str(org_a_id)}
            )
        ).json()
        assert actual["informe"]["resumen_ejecutivo"] == "Resumen mock."
