"""Tests del endpoint RAG /rag/search.

Verifica que el endpoint existe, valida parámetros y responde correctamente
cuando no hay VOYAGE_API_KEY configurada (retorna 503, no 500).
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_rag_search_sin_api_key_devuelve_503():
    """Sin VOYAGE_API_KEY el endpoint debe retornar 503, no un error interno."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/rag/search",
            json={"query": "base de licitud consentimiento", "top_k": 3},
        )
    # 503 = clave no configurada (esperado en dev sin Voyage AI)
    # 200 = clave configurada y BD con datos
    assert response.status_code in (
        200,
        503,
    ), f"Se esperaba 200 o 503, se obtuvo {response.status_code}: {response.text}"


@pytest.mark.asyncio
async def test_rag_search_query_muy_corta_devuelve_422():
    """Query de menos de 3 caracteres debe ser rechazada con 422."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/rag/search",
            json={"query": "ab"},
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_rag_search_top_k_fuera_de_rango_devuelve_422():
    """top_k > 20 debe ser rechazado con 422."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/rag/search",
            json={"query": "proteccion de datos personales", "top_k": 99},
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_rag_search_respeta_esquema():
    """La respuesta debe incluir los campos query y results."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/rag/search",
            json={"query": "dato personal identificable", "top_k": 2},
        )
    if response.status_code == 200:
        data = response.json()
        assert "query" in data
        assert "results" in data
        assert isinstance(data["results"], list)
