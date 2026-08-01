"""Tests de app/services/diagnostico_ia.py (Fase 1, Módulo 1, Tarea 4).

Corren contra el rol admin (`_session_factory`, sin RLS) — igual que
test_diagnostico_service.py. El LLM y el RAG se mockean siempre (nunca se
gasta crédito real de Anthropic/Voyage en esta suite); la única llamada real
end-to-end vive fuera de los tests automatizados (ver plan de verificación).
"""

import pytest
import pytest_asyncio
from fastapi import HTTPException
from sqlalchemy import delete, select

from app.db.models import Diagnostic, DiagnosticAnswer, Finding, Pregunta
from app.services import diagnostico, diagnostico_ia


class _FakeLLMClient:
    def __init__(self, respuesta: dict):
        self._respuesta = respuesta

    async def generate_structured(
        self, *, system: str, prompt: str, schema: dict, tool_name: str = "responder"
    ) -> dict:
        return self._respuesta


@pytest_asyncio.fixture(autouse=True)
async def _limpiar_diagnosticos_org_a(_session_factory, org_a_id):
    """Mismo barrido que test_diagnostico_service.py: a lo sumo un Diagnostic
    por organización (UNIQUE desde la migración 0005)."""

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
async def diagnostico_completado_org_a(_session_factory, org_a_id, profile_a_id):
    """Diagnostic de la organización A, completado: las dos primeras preguntas
    en 'No' (generan hallazgos), el resto en 'Sí'."""
    async with _session_factory() as session:
        creado = await diagnostico.obtener_o_crear_diagnostico_vigente(
            session, org_a_id, profile_a_id
        )
        await session.commit()
        diagnostic_id = creado.id

    async with _session_factory() as session:
        pregunta_ids = (await session.execute(select(Pregunta.id))).scalars().all()

    async with _session_factory() as session:
        diagnostic = await session.get(Diagnostic, diagnostic_id)
        respuestas = [
            diagnostico.RespuestaGuardar(
                pregunta_id=pid, answer="No" if i < 2 else "Sí"
            )
            for i, pid in enumerate(pregunta_ids)
        ]
        await diagnostico.guardar_respuestas(session, diagnostic, respuestas)
        await diagnostico.recalcular_diagnostico(session, diagnostic)
        await session.commit()
        assert diagnostic.status == "completado"

    return diagnostic_id


@pytest.mark.asyncio
async def test_generar_informe_rechaza_diagnostico_no_completado(
    _session_factory, org_a_id, profile_a_id
):
    async with _session_factory() as session:
        diagnostic = await diagnostico.obtener_o_crear_diagnostico_vigente(
            session, org_a_id, profile_a_id
        )
        await session.commit()

        with pytest.raises(HTTPException) as exc_info:
            await diagnostico_ia.generar_informe(session, diagnostic)
        assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_generar_informe_usa_solo_ley_21719_y_guia_ccs(
    _session_factory, diagnostico_completado_org_a, monkeypatch
):
    """El retrieval RAG de la Tarea 4 debe excluir ley_19628 (pedido
    explícito del usuario) — se verifica el `sources` recibido, no el
    comportamiento genérico de search_chunks (ya probado en test_rag.py)."""
    llamada = {}

    async def _fake_search_chunks(query, db, top_k=12, sources=None):
        llamada["sources"] = sources
        return []

    monkeypatch.setattr(diagnostico_ia, "search_chunks", _fake_search_chunks)
    monkeypatch.setattr(
        diagnostico_ia,
        "get_llm_client",
        lambda settings: _FakeLLMClient(
            {"resumen_ejecutivo": "Resumen.", "narrativas": []}
        ),
    )

    async with _session_factory() as session:
        diagnostic = await session.get(Diagnostic, diagnostico_completado_org_a)
        await diagnostico_ia.generar_informe(session, diagnostic)
        await session.commit()

    assert llamada["sources"] == ["ley_21719", "guia_ccs"]
    assert "ley_19628" not in llamada["sources"]


@pytest.mark.asyncio
async def test_generar_informe_descarta_citas_y_findings_inventados(
    _session_factory, diagnostico_completado_org_a, monkeypatch
):
    async with _session_factory() as session:
        diagnostic = await session.get(Diagnostic, diagnostico_completado_org_a)
        hallazgos = (
            (
                await session.execute(
                    select(Finding).where(Finding.diagnostic_id == diagnostic.id)
                )
            )
            .scalars()
            .all()
        )
    assert hallazgos, "la fixture debe generar al menos un hallazgo"
    finding_real = hallazgos[0]

    async def _fake_search_chunks(query, db, top_k=12, sources=None):
        return [
            {
                "id": "chunk-1",
                "source": "ley_21719",
                "reference": "Art. 1",
                "content": "Contenido real recuperado.",
                "similarity": 0.9,
            }
        ]

    monkeypatch.setattr(diagnostico_ia, "search_chunks", _fake_search_chunks)
    monkeypatch.setattr(
        diagnostico_ia,
        "get_llm_client",
        lambda settings: _FakeLLMClient(
            {
                "resumen_ejecutivo": "Resumen de prueba.",
                "narrativas": [
                    {
                        "finding_id": str(finding_real.id),
                        "narrativa": "Narrativa real, con una cita válida y una inventada.",
                        "citas": [
                            {"source": "ley_21719", "reference": "Art. 1"},
                            {"source": "ley_19628", "reference": "Art. 99"},
                        ],
                    },
                    {
                        "finding_id": "finding-que-no-existe",
                        "narrativa": "No debería sobrevivir al guardarraíl.",
                        "citas": [],
                    },
                ],
            }
        ),
    )

    async with _session_factory() as session:
        diagnostic = await session.get(Diagnostic, diagnostico_completado_org_a)
        informe = await diagnostico_ia.generar_informe(session, diagnostic)
        await session.commit()

    assert len(informe["narrativas"]) == 1
    assert informe["narrativas"][0]["finding_id"] == str(finding_real.id)
    assert informe["narrativas"][0]["citas"] == [
        {"source": "ley_21719", "reference": "Art. 1"}
    ]

    async with _session_factory() as session:
        diagnostic = await session.get(Diagnostic, diagnostico_completado_org_a)
        assert diagnostic.informe_ia is not None
        assert diagnostic.informe_generado_en is not None
        assert diagnostic.informe_ia == informe
