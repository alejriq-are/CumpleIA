"""Tests de app/services/diagnostico.py (Fase 1, Módulo 1, Tarea 3).

Corren contra el rol admin (`_session_factory`, sin RLS) — son lógica de
negocio (orquestación get-or-create, upsert, recálculo), no una política RLS;
el aislamiento por organización de `reference_documents`/`findings` vive en
test_rls_isolation_diagnosticos.py. Requiere el seed de
scripts/seed_modulo1_cuestionario.py ya aplicado (v1 activa, 50 preguntas),
igual que el resto de la suite del Módulo 1.
"""

import pytest
import pytest_asyncio
from fastapi import HTTPException
from sqlalchemy import delete, select

from app.db.models import ConfigVersion, Diagnostic, DiagnosticAnswer, Finding, Pregunta
from app.services import diagnostico


@pytest_asyncio.fixture(autouse=True)
async def _limpiar_diagnosticos_org_a(_session_factory, org_a_id):
    """A lo sumo un Diagnostic por organización (UNIQUE desde la migración
    0005): sin este barrido, un test que no limpie tras de sí rompe el
    siguiente con `duplicate key value` — antes y después, por si un run
    previo quedó a medias."""

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
async def diagnostico_org_a(_session_factory, org_a_id, profile_a_id):
    """Diagnostic vigente de la organización A, creado vía el propio servicio
    (no INSERT directo): así cada test que lo use empieza desde el mismo
    get-or-create que ejercerá la API."""
    async with _session_factory() as session:
        creado = await diagnostico.obtener_o_crear_diagnostico_vigente(
            session, org_a_id, profile_a_id
        )
        await session.commit()
        return creado.id


async def _preguntas_activas_ids(_session_factory) -> list[str]:
    async with _session_factory() as session:
        return list((await session.execute(select(Pregunta.id))).scalars().all())


@pytest.mark.asyncio
async def test_get_or_create_es_idempotente_y_pinnea_version_activa(
    _session_factory, org_a_id, profile_a_id
):
    async with _session_factory() as session:
        version_activa_id = await session.scalar(
            select(ConfigVersion.id).where(ConfigVersion.activa.is_(True))
        )
        primero = await diagnostico.obtener_o_crear_diagnostico_vigente(
            session, org_a_id, profile_a_id
        )
        await session.commit()

    async with _session_factory() as session:
        segundo = await diagnostico.obtener_o_crear_diagnostico_vigente(
            session, org_a_id, profile_a_id
        )
        await session.commit()

    assert primero.id == segundo.id, "get-or-create debe devolver el mismo Diagnostic"
    assert primero.config_version_id == version_activa_id


@pytest.mark.asyncio
async def test_guardar_respuestas_rechaza_pregunta_desconocida_sin_escribir_nada(
    _session_factory, diagnostico_org_a
):
    async with _session_factory() as session:
        diagnostic = await session.get(Diagnostic, diagnostico_org_a)
        preguntas_reales = (
            await session.execute(select(Pregunta.id).limit(1))
        ).scalar_one()

        with pytest.raises(HTTPException) as exc_info:
            await diagnostico.guardar_respuestas(
                session,
                diagnostic,
                [
                    diagnostico.RespuestaGuardar(
                        pregunta_id=preguntas_reales, answer="Sí"
                    ),
                    diagnostico.RespuestaGuardar(pregunta_id="NO-EXISTE", answer="No"),
                ],
            )
        assert exc_info.value.status_code == 400
        await session.rollback()

    async with _session_factory() as session:
        respuestas = (
            (
                await session.execute(
                    select(DiagnosticAnswer).where(
                        DiagnosticAnswer.diagnostic_id == diagnostico_org_a
                    )
                )
            )
            .scalars()
            .all()
        )
    assert (
        respuestas == []
    ), "un lote con una pregunta inválida no debe escribir ninguna"


@pytest.mark.asyncio
async def test_guardar_respuestas_rechaza_answer_fuera_de_dominio_sin_escribir_nada(
    _session_factory, diagnostico_org_a
):
    """El servicio no debe confiar únicamente en el Literal de Pydantic del
    router: un llamador que lo invoque directamente con un `answer` fuera de
    dominio debe recibir un 400 controlado, no un DBAPIError crudo del CHECK
    de la base."""
    async with _session_factory() as session:
        diagnostic = await session.get(Diagnostic, diagnostico_org_a)
        pregunta_real = (
            await session.execute(select(Pregunta.id).limit(1))
        ).scalar_one()

        with pytest.raises(HTTPException) as exc_info:
            await diagnostico.guardar_respuestas(
                session,
                diagnostic,
                [
                    diagnostico.RespuestaGuardar(
                        pregunta_id=pregunta_real, answer="Tal vez"
                    )
                ],
            )
        assert exc_info.value.status_code == 400
        await session.rollback()

    async with _session_factory() as session:
        respuestas = (
            (
                await session.execute(
                    select(DiagnosticAnswer).where(
                        DiagnosticAnswer.diagnostic_id == diagnostico_org_a
                    )
                )
            )
            .scalars()
            .all()
        )
    assert respuestas == [], "un answer fuera de dominio no debe escribir nada"


@pytest.mark.asyncio
async def test_recalcular_marca_completado_solo_con_todas_las_preguntas(
    _session_factory, diagnostico_org_a
):
    pregunta_ids = await _preguntas_activas_ids(_session_factory)
    assert len(pregunta_ids) >= 2, "el catálogo sembrado debe tener preguntas"

    async with _session_factory() as session:
        diagnostic = await session.get(Diagnostic, diagnostico_org_a)
        respuestas = [
            diagnostico.RespuestaGuardar(pregunta_id=pid, answer="Sí")
            for pid in pregunta_ids[:-1]
        ]
        hubo_cambio = await diagnostico.guardar_respuestas(
            session, diagnostic, respuestas
        )
        await diagnostico.recalcular_diagnostico(session, diagnostic, hubo_cambio)
        await session.commit()
        assert diagnostic.status == "en_progreso"

    async with _session_factory() as session:
        diagnostic = await session.get(Diagnostic, diagnostico_org_a)
        hubo_cambio = await diagnostico.guardar_respuestas(
            session,
            diagnostic,
            [diagnostico.RespuestaGuardar(pregunta_id=pregunta_ids[-1], answer="Sí")],
        )
        await diagnostico.recalcular_diagnostico(session, diagnostic, hubo_cambio)
        await session.commit()
        assert diagnostic.status == "completado"


@pytest.mark.asyncio
async def test_recalcular_reabre_y_cierra_hallazgo_ida_y_vuelta(
    _session_factory, diagnostico_org_a
):
    pregunta_ids = await _preguntas_activas_ids(_session_factory)
    pregunta_id = pregunta_ids[0]

    async def _responder(answer: str) -> Finding:
        async with _session_factory() as session:
            diagnostic = await session.get(Diagnostic, diagnostico_org_a)
            hubo_cambio = await diagnostico.guardar_respuestas(
                session,
                diagnostic,
                [diagnostico.RespuestaGuardar(pregunta_id=pregunta_id, answer=answer)],
            )
            await diagnostico.recalcular_diagnostico(session, diagnostic, hubo_cambio)
            await session.commit()

        async with _session_factory() as session:
            return (
                await session.execute(
                    select(Finding).where(
                        Finding.diagnostic_id == diagnostico_org_a,
                        Finding.pregunta_id == pregunta_id,
                    )
                )
            ).scalar_one()

    abierto = await _responder("No")
    assert abierto.status.value == "abierto"
    assert abierto.risk.value in ("alto", "medio", "bajo")

    cerrado = await _responder("Sí")
    assert cerrado.id == abierto.id, "debe ser la MISMA fila, no un Finding nuevo"
    assert cerrado.status.value == "cerrado"

    reabierto = await _responder("No")
    assert reabierto.id == abierto.id
    assert reabierto.status.value == "abierto"
