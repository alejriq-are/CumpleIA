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
from zoneinfo import ZoneInfo

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
    Organization,
    Profile,
    UserRole,
)
from app.db.session import get_db
from app.main import app
from tests.conftest import _make_profile_override_from_db, _make_rls_db_override

_VIEWER_PROFILE_ID = uuid.uuid4()
_VIEWER_AUTH_ID = uuid.uuid4()


@pytest_asyncio.fixture(autouse=True)
async def _restaurar_organizacion_a(_session_factory, org_a_id):
    """`org_a_id` es session-scoped (`_seed_test_data` en conftest.py): los
    tests de exportación que fijan `size`/`rut`/`industry` vía
    `PATCH /organizations` no deben dejar ese estado para el resto de la
    suite."""
    async with _session_factory() as session:
        original = await session.get(Organization, org_a_id)
        nombre, rut, industry, size = (
            original.name,
            original.rut,
            original.industry,
            original.size,
        )

    yield

    async with _session_factory() as session:
        organizacion = await session.get(Organization, org_a_id)
        organizacion.name = nombre
        organizacion.rut = rut
        organizacion.industry = industry
        organizacion.size = size
        await session.commit()


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


@pytest.mark.asyncio
async def test_reabrir_respuestas_invalida_el_informe_ya_generado(
    client_a, org_a_id, monkeypatch
):
    """Fix de la revisión del PR #13 (hallazgo #2), a nivel de API: tras
    generar un informe, volver a guardar respuestas debe dejar `informe`
    en null en vez de mostrar uno desactualizado en silencio."""

    async def _fake_generar_informe(db, diagnostic):
        diagnostic.informe_ia = {"resumen_ejecutivo": "Resumen mock.", "narrativas": []}
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
        pregunta_ids = [p["id"] for p in cuestionario["preguntas"]]
        respuestas = [{"pregunta_id": pid, "answer": "Sí"} for pid in pregunta_ids]
        await client.post(
            "/diagnostico/respuestas",
            headers={"X-Organization-Id": str(org_a_id)},
            json={"respuestas": respuestas},
        )
        await client.post(
            "/diagnostico/informe", headers={"X-Organization-Id": str(org_a_id)}
        )

        reabrir = await client.post(
            "/diagnostico/respuestas",
            headers={"X-Organization-Id": str(org_a_id)},
            json={"respuestas": [{"pregunta_id": pregunta_ids[0], "answer": "No"}]},
        )
        assert reabrir.json()["informe"] is None

        actual = (
            await client.get(
                "/diagnostico/actual", headers={"X-Organization-Id": str(org_a_id)}
            )
        ).json()
        assert actual["informe"] is None


@pytest.mark.asyncio
async def test_exportar_404_sin_diagnostico_previo(client_a, org_a_id):
    async with AsyncClient(
        transport=ASGITransport(app=client_a), base_url="http://test"
    ) as client:
        resp = await client.get(
            "/diagnostico/informe/exportar",
            headers={"X-Organization-Id": str(org_a_id)},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_exportar_409_sin_informe_generado(client_a, org_a_id):
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

        resp = await client.get(
            "/diagnostico/informe/exportar",
            headers={"X-Organization-Id": str(org_a_id)},
        )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_exportar_200_devuelve_html_descargable_con_contenido_del_informe(
    client_a, org_a_id, monkeypatch
):
    async def _fake_generar_informe(db, diagnostic):
        diagnostic.informe_ia = {
            "resumen_ejecutivo": "Resumen mock <script>alert(1)</script>.",
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
        pregunta_ids = [p["id"] for p in cuestionario["preguntas"]]
        preguntas_con_brecha = pregunta_ids[:1]
        respuestas = [
            {
                "pregunta_id": pid,
                "answer": "No" if pid in preguntas_con_brecha else "Sí",
            }
            for pid in pregunta_ids
        ]
        await client.post(
            "/diagnostico/respuestas",
            headers={"X-Organization-Id": str(org_a_id)},
            json={"respuestas": respuestas},
        )
        await client.post(
            "/diagnostico/informe", headers={"X-Organization-Id": str(org_a_id)}
        )

        resp = await client.get(
            "/diagnostico/informe/exportar",
            headers={"X-Organization-Id": str(org_a_id)},
        )

    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/html")
    assert "attachment" in resp.headers["content-disposition"]
    body = resp.text
    assert "Resumen mock &lt;script&gt;alert(1)&lt;/script&gt;." in body
    assert "<script>alert(1)</script>" not in body
    assert "Riesgo Alto" in body or "Riesgo Medio" in body or "Riesgo Bajo" in body


@pytest.mark.asyncio
async def test_exportar_200_renderiza_narrativa_y_citas_del_hallazgo_con_escape(
    client_a, org_a_id, monkeypatch
):
    """Hallazgo #1 de la revisión del PR #17: ningún test cubría la rama que
    renderiza `narrativa`/`citas` por hallazgo (app/services/
    diagnostico_exportacion.py) — el único test 200 previo mockeaba
    `narrativas: []`, así que ese `escape()` nunca corría en CI."""

    async def _fake_generar_informe(db, diagnostic):
        findings = (
            (
                await db.execute(
                    select(Finding).where(Finding.diagnostic_id == diagnostic.id)
                )
            )
            .scalars()
            .all()
        )
        diagnostic.informe_ia = {
            "resumen_ejecutivo": "Resumen mock.",
            "narrativas": [
                {
                    "finding_id": str(findings[0].id),
                    "narrativa": "Narrativa mock <script>alert(2)</script> con riesgo real.",
                    "citas": [{"source": "ley_21719", "reference": "Artículo 14"}],
                }
            ],
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
        pregunta_ids = [p["id"] for p in cuestionario["preguntas"]]
        respuestas = [
            {"pregunta_id": pid, "answer": "No" if pid == pregunta_ids[0] else "Sí"}
            for pid in pregunta_ids
        ]
        await client.post(
            "/diagnostico/respuestas",
            headers={"X-Organization-Id": str(org_a_id)},
            json={"respuestas": respuestas},
        )
        await client.post(
            "/diagnostico/informe", headers={"X-Organization-Id": str(org_a_id)}
        )

        resp = await client.get(
            "/diagnostico/informe/exportar",
            headers={"X-Organization-Id": str(org_a_id)},
        )

    assert resp.status_code == 200
    body = resp.text
    assert (
        "<p class='narrativa'>Narrativa mock &lt;script&gt;alert(2)&lt;/script&gt; con riesgo real.</p>"
        in body
    )
    assert "<script>alert(2)</script>" not in body
    assert "<ul class='citas'>" in body
    assert "<li>ley_21719 — Artículo 14</li>" in body


@pytest.mark.asyncio
async def test_viewer_puede_exportar_informe(
    viewer_client_org_a, client_a, org_a_id, monkeypatch
):
    async def _fake_generar_informe(db, diagnostic):
        diagnostic.informe_ia = {"resumen_ejecutivo": "Resumen mock.", "narrativas": []}
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
        await client.post(
            "/diagnostico/informe", headers={"X-Organization-Id": str(org_a_id)}
        )

    async with AsyncClient(
        transport=ASGITransport(app=viewer_client_org_a), base_url="http://test"
    ) as client:
        resp = await client.get(
            "/diagnostico/informe/exportar",
            headers={"X-Organization-Id": str(org_a_id)},
        )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_guardar_respuestas_expone_answer_y_risk_base_por_hallazgo(
    client_a, org_a_id
):
    """Mejora al informe (ítem 3): sin `answer`/`risk_base` en `HallazgoOut`
    no se puede explicar por qué una pregunta de riesgo base Alto aparece
    como hallazgo Medio. Responder TODO en 'Parcial' garantiza al menos una
    degradación real (riesgo_base != risk), salvo que el catálogo sembrado
    fuera 100% riesgo Bajo, lo que test_diagnostico_puntaje.py ya descarta."""
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
            {"pregunta_id": p["id"], "answer": "Parcial"}
            for p in cuestionario["preguntas"]
        ]
        resp = await client.post(
            "/diagnostico/respuestas",
            headers={"X-Organization-Id": str(org_a_id)},
            json={"respuestas": respuestas},
        )

    data = resp.json()
    assert all(h["answer"] == "Parcial" for h in data["hallazgos"])
    assert all(h["risk_base"] is not None for h in data["hallazgos"])
    assert any(
        h["risk"] != h["risk_base"] for h in data["hallazgos"]
    ), "el catálogo debe tener al menos una pregunta de riesgo base distinto de Bajo"


@pytest.mark.asyncio
async def test_exportar_incluye_identificacion_conteo_metodologia_y_riesgo_ajustado(
    client_a, org_a_id, monkeypatch
):
    """Mejoras al informe (ítems 1, 2 y 3): encabezado de identificación
    (empresa/RUT/rubro/tamaño/quién respondió/ID), conteo determinista de
    hallazgos por riesgo (BUG-01: fuente única de verdad, no una cifra que
    declare el LLM) y la explicación base/ajustado cuando 'Parcial' degrada
    el riesgo."""

    async def _fake_generar_informe(db, diagnostic):
        diagnostic.informe_ia = {"resumen_ejecutivo": "Resumen mock.", "narrativas": []}
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
            {"pregunta_id": p["id"], "answer": "Parcial"}
            for p in cuestionario["preguntas"]
        ]
        guardado = (
            await client.post(
                "/diagnostico/respuestas",
                headers={"X-Organization-Id": str(org_a_id)},
                json={"respuestas": respuestas},
            )
        ).json()
        degradado = next(
            h for h in guardado["hallazgos"] if h["risk"] != h["risk_base"]
        )

        await client.post(
            "/diagnostico/informe", headers={"X-Organization-Id": str(org_a_id)}
        )
        resp = await client.get(
            "/diagnostico/informe/exportar",
            headers={"X-Organization-Id": str(org_a_id)},
        )

    assert resp.status_code == 200
    body = resp.text

    total_abierto = sum(1 for h in guardado["hallazgos"] if h["status"] != "cerrado")
    assert (
        f'<span class="conteo-numero">{total_abierto}</span><span>Total abiertos</span>'
        in body
    )
    assert "Hallazgos abiertos por riesgo" in body

    assert "Metodología" in body
    assert "Parcial</strong> = 50%" in body

    assert 'class="identificacion"' in body
    assert "ID de diagnóstico" in body
    assert "Respondido por" in body
    assert "Propietario/a" in body  # client_a es owner (conftest.py)

    assert (
        f"base {degradado['risk_base']}, ajustado por respuesta Parcial" in body
    ), "debe explicar el riesgo ajustado cuando Parcial degrada el riesgo base"


async def _generar_y_exportar_informe(client: AsyncClient, org_a_id) -> str:
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
    await client.post(
        "/diagnostico/informe", headers={"X-Organization-Id": str(org_a_id)}
    )
    resp = await client.get(
        "/diagnostico/informe/exportar",
        headers={"X-Organization-Id": str(org_a_id)},
    )
    assert resp.status_code == 200
    return resp.text


@pytest.mark.asyncio
async def test_exportar_incluye_aviso_pyme_para_pequena_y_mediana_empresa(
    client_a, org_a_id, monkeypatch
):
    """Pedido explícito del usuario (2026-08-10): 'pequeña'/'mediana' muestran
    la sigla PYME y el aviso de asesoría; 'micro'/'grande' no."""

    async def _fake_generar_informe(db, diagnostic):
        diagnostic.informe_ia = {"resumen_ejecutivo": "Resumen mock.", "narrativas": []}
        diagnostic.informe_generado_en = datetime.now(UTC)
        return diagnostic.informe_ia

    monkeypatch.setattr(
        diagnostico_api.diagnostico_ia, "generar_informe", _fake_generar_informe
    )

    async with AsyncClient(
        transport=ASGITransport(app=client_a), base_url="http://test"
    ) as client:
        await client.patch(
            "/organizations",
            headers={"X-Organization-Id": str(org_a_id)},
            json={"name": "Organización A (test)", "size": "pequeña"},
        )
        body = await _generar_y_exportar_informe(client, org_a_id)

    assert "Pequeña empresa (PYME)" in body
    assert "CumpleIA puede asesorarte" in body


@pytest.mark.asyncio
async def test_exportar_no_incluye_aviso_pyme_para_micro_empresa(
    client_a, org_a_id, monkeypatch
):
    async def _fake_generar_informe(db, diagnostic):
        diagnostic.informe_ia = {"resumen_ejecutivo": "Resumen mock.", "narrativas": []}
        diagnostic.informe_generado_en = datetime.now(UTC)
        return diagnostic.informe_ia

    monkeypatch.setattr(
        diagnostico_api.diagnostico_ia, "generar_informe", _fake_generar_informe
    )

    async with AsyncClient(
        transport=ASGITransport(app=client_a), base_url="http://test"
    ) as client:
        await client.patch(
            "/organizations",
            headers={"X-Organization-Id": str(org_a_id)},
            json={"name": "Organización A (test)", "size": "micro"},
        )
        body = await _generar_y_exportar_informe(client, org_a_id)

    assert "Micro empresa" in body
    assert "(PYME)" not in body
    assert "CumpleIA puede asesorarte" not in body


@pytest.mark.asyncio
async def test_exportar_muestra_la_hora_convertida_a_chile_no_en_utc(
    client_a, org_a_id, monkeypatch
):
    """`informe_generado_en` se guarda en UTC (`datetime.now(UTC)`,
    diagnostico_ia.py); el HTML exportado debe convertirla a America/Santiago
    antes de mostrarla, no formatear el UTC crudo como si fuera hora local."""
    momento_utc = datetime(2026, 8, 10, 23, 30, tzinfo=UTC)

    async def _fake_generar_informe(db, diagnostic):
        diagnostic.informe_ia = {"resumen_ejecutivo": "Resumen mock.", "narrativas": []}
        diagnostic.informe_generado_en = momento_utc
        return diagnostic.informe_ia

    monkeypatch.setattr(
        diagnostico_api.diagnostico_ia, "generar_informe", _fake_generar_informe
    )

    async with AsyncClient(
        transport=ASGITransport(app=client_a), base_url="http://test"
    ) as client:
        body = await _generar_y_exportar_informe(client, org_a_id)

    hora_chile_esperada = momento_utc.astimezone(ZoneInfo("America/Santiago")).strftime(
        "%d-%m-%Y %H:%M"
    )
    hora_utc_cruda = momento_utc.strftime("%d-%m-%Y %H:%M")

    assert hora_chile_esperada in body
    assert hora_chile_esperada != hora_utc_cruda, (
        "el momento elegido debe tener un offset real distinto de 0 para que "
        "este test detecte una regresión a formatear UTC crudo"
    )
    assert hora_utc_cruda not in body
