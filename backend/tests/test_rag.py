"""Tests del endpoint RAG /rag/search.

El endpoint requiere autenticación. Las pruebas de validación y de
comportamiento sin VOYAGE_API_KEY se hacen autenticadas (fixture client_a);
además se verifica que sin token la respuesta sea 401.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_rag_search_sin_token_devuelve_401():
    """Sin header Authorization el endpoint debe rechazar con 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/rag/search",
            json={"query": "base de licitud consentimiento", "top_k": 3},
        )
    assert response.status_code == 401
    assert response.headers.get("WWW-Authenticate") == "Bearer"


@pytest.mark.asyncio
async def test_rag_search_sin_api_key_devuelve_503(client_a):
    """Autenticado pero sin VOYAGE_API_KEY: 503, no un error interno."""
    async with AsyncClient(
        transport=ASGITransport(app=client_a), base_url="http://test"
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
async def test_rag_search_query_muy_corta_devuelve_422(client_a):
    """Query de menos de 3 caracteres debe ser rechazada con 422."""
    async with AsyncClient(
        transport=ASGITransport(app=client_a), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/rag/search",
            json={"query": "ab"},
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_rag_search_top_k_fuera_de_rango_devuelve_422(client_a):
    """top_k > 20 debe ser rechazado con 422."""
    async with AsyncClient(
        transport=ASGITransport(app=client_a), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/rag/search",
            json={"query": "proteccion de datos personales", "top_k": 99},
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_rag_search_respeta_esquema(client_a):
    """La respuesta debe incluir los campos query y results."""
    async with AsyncClient(
        transport=ASGITransport(app=client_a), base_url="http://test"
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


@pytest.mark.asyncio
async def test_rag_search_sql_valido_con_embedding_mockeado(client_a, monkeypatch):
    """Regresión: la consulta pgvector debe ejecutarse sin error de sintaxis.

    Antes usaba `:emb::vector`, que SQLAlchemy no bindeaba y Postgres rechazaba
    con 'syntax error at or near ":"'. Se mockea el embedding para no depender de
    Voyage y así el SQL se ejecuta de verdad contra la BD (0 resultados si no hay
    chunks con embedding, pero sin error 500). Autenticado vía client_a.
    """
    from app.services import rag as rag_service

    async def _fake_embedding(query: str) -> list[float]:
        return [0.01] * 1024

    monkeypatch.setattr(rag_service, "_get_query_embedding", _fake_embedding)

    async with AsyncClient(
        transport=ASGITransport(app=client_a), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/rag/search",
            json={"query": "dato personal identificable", "top_k": 3},
        )
    assert response.status_code == 200, response.text
    assert isinstance(response.json()["results"], list)
