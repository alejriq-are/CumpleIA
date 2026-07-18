"""Tests de aislamiento multi-tenant (requisito de aceptación del PASO 4).

Verifican que un usuario de la organización A NO puede leer datos de la B,
y que el sistema rechaza correctamente tokens inválidos o ausentes.

Requiere: Docker Postgres corriendo con la migración aplicada.
"""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app

# ── Aislamiento de tenant ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_usuario_b_no_puede_acceder_a_org_a(client_b, org_a_id):
    """Usuario B intenta acceder a org A → debe recibir 403."""
    async with AsyncClient(
        transport=ASGITransport(app=client_b), base_url="http://test"
    ) as ac:
        response = await ac.get(
            "/me/membership",
            headers={"X-Organization-Id": str(org_a_id)},
        )
    assert response.status_code == 403, (
        f"Se esperaba 403 pero se obtuvo {response.status_code}. "
        "El aislamiento multi-tenant falló: usuario B pudo acceder a org A."
    )


@pytest.mark.asyncio
async def test_usuario_a_no_puede_acceder_a_org_b(client_a, org_b_id):
    """Usuario A intenta acceder a org B → debe recibir 403."""
    async with AsyncClient(
        transport=ASGITransport(app=client_a), base_url="http://test"
    ) as ac:
        response = await ac.get(
            "/me/membership",
            headers={"X-Organization-Id": str(org_b_id)},
        )
    assert response.status_code == 403, (
        f"Se esperaba 403 pero se obtuvo {response.status_code}. "
        "El aislamiento multi-tenant falló: usuario A pudo acceder a org B."
    )


@pytest.mark.asyncio
async def test_usuario_a_puede_acceder_a_su_propia_org(client_a, org_a_id):
    """Usuario A accede a su propia org → debe recibir 200 con rol correcto."""
    async with AsyncClient(
        transport=ASGITransport(app=client_a), base_url="http://test"
    ) as ac:
        response = await ac.get(
            "/me/membership",
            headers={"X-Organization-Id": str(org_a_id)},
        )
    assert response.status_code == 200, (
        f"Se esperaba 200 pero se obtuvo {response.status_code}."
    )
    data = response.json()
    assert str(data["organization_id"]) == str(org_a_id)
    assert data["role"] == "owner"


@pytest.mark.asyncio
async def test_usuario_b_puede_acceder_a_su_propia_org(client_b, org_b_id):
    """Usuario B accede a su propia org → debe recibir 200 con rol correcto."""
    async with AsyncClient(
        transport=ASGITransport(app=client_b), base_url="http://test"
    ) as ac:
        response = await ac.get(
            "/me/membership",
            headers={"X-Organization-Id": str(org_b_id)},
        )
    assert response.status_code == 200
    data = response.json()
    assert str(data["organization_id"]) == str(org_b_id)
    assert data["role"] == "owner"


@pytest.mark.asyncio
async def test_org_id_inventado_es_rechazado(client_a):
    """Enviar un org_id que no existe → debe recibir 403."""
    fake_org = uuid.uuid4()
    async with AsyncClient(
        transport=ASGITransport(app=client_a), base_url="http://test"
    ) as ac:
        response = await ac.get(
            "/me/membership",
            headers={"X-Organization-Id": str(fake_org)},
        )
    assert response.status_code == 403


# ── Autenticación ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_request_sin_token_es_rechazado():
    """Sin header Authorization → 403 (HTTPBearer devuelve 403 si falta el header)."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/me")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_token_invalido_es_rechazado():
    """Token JWT malformado → 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/me", headers={"Authorization": "Bearer token.falso.aqui"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_health_no_requiere_autenticacion():
    """GET /health debe responder 200 sin autenticación."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
