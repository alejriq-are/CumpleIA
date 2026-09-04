"""Pruebas autoritativas de la tarea «organización actual segura».

El código candidato se monta sólo de lectura, sin red, base de datos ni
credenciales. Se usan dobles mínimos para comprobar la ruta y su contrato.
"""

from __future__ import annotations

import inspect
import os
import uuid
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("SUPABASE_URL", "http://invalid.local")
WORKSPACE = "/workspace"
if not os.path.isdir(WORKSPACE):
    pytest.skip("solo se ejecuta dentro del verifier aislado", allow_module_level=True)

from app.api import organizations as api  # noqa: E402
from app.core.deps import get_current_profile  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.main import app  # noqa: E402

ORG_A_ID = uuid.UUID("10000000-0000-0000-0000-000000000010")


class _FakeDb:
    def __init__(self, organization, membership=None):
        self.organization = organization
        self.membership = membership
        self.requested_id = None

    async def get(self, model, identifier):
        assert model.__name__ == "Organization"
        self.requested_id = identifier
        return self.organization

    async def execute(self, _statement):
        return SimpleNamespace(scalar_one_or_none=lambda: self.membership)


async def _request(db: _FakeDb, organization_id: uuid.UUID):
    async def _profile():
        return SimpleNamespace(
            id=uuid.UUID("10000000-0000-0000-0000-000000000099"),
            is_superadmin=False,
        )

    async def _db():
        yield db

    app.dependency_overrides[get_current_profile] = _profile
    app.dependency_overrides[get_db] = _db
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            return await client.get(
                "/organizations/current",
                headers={"X-Organization-Id": str(organization_id)},
            )
    finally:
        app.dependency_overrides.pop(get_current_profile, None)
        app.dependency_overrides.pop(get_db, None)


def _route():
    matches = [
        route
        for route in api.router.routes
        if route.path == "/organizations/current" and route.methods == {"GET"}
    ]
    assert len(matches) == 1, "debe existir exactamente GET /organizations/current"
    return matches[0]


def test_ruta_usa_el_tenant_del_header_y_permiso_de_lectura():
    route = _route()
    source = inspect.getsource(route.endpoint)
    signature = inspect.signature(route.endpoint)

    assert "x_organization_id" in signature.parameters
    assert "Header" in source
    assert "require_permission(Permission.view_content)" in source
    assert "organization_id" not in route.path
    assert route.response_model is api.OrganizationDetailOut


@pytest.mark.asyncio
async def test_lectura_autorizada_devuelve_solo_datos_de_la_org_seleccionada():
    route = _route()
    organization = SimpleNamespace(
        id=ORG_A_ID,
        name="Organización A",
        rut="76.000.000-1",
        industry="Servicios",
        size="pequeña",
    )
    db = _FakeDb(organization)

    output = await route.endpoint(ORG_A_ID, SimpleNamespace(), db)

    assert db.requested_id == ORG_A_ID
    assert output.model_dump() == {
        "id": ORG_A_ID,
        "name": "Organización A",
        "rut": "76.000.000-1",
        "industry": "Servicios",
        "size": "pequeña",
    }


@pytest.mark.asyncio
async def test_viewer_miembro_puede_leer_y_tenant_ajeno_recibe_403():
    organization = SimpleNamespace(
        id=ORG_A_ID,
        name="Organización A",
        rut=None,
        industry=None,
        size=None,
    )
    viewer = SimpleNamespace(role=api.UserRole.viewer)
    allowed = await _request(_FakeDb(organization, viewer), ORG_A_ID)
    assert allowed.status_code == 200
    assert allowed.json() == {
        "id": str(ORG_A_ID),
        "name": "Organización A",
        "rut": None,
        "industry": None,
        "size": None,
    }

    denied = await _request(_FakeDb(organization, None), ORG_A_ID)
    assert denied.status_code == 403


@pytest.mark.asyncio
async def test_organizacion_autorizada_ausente_devuelve_404():
    route = _route()
    db = _FakeDb(None)

    with pytest.raises(HTTPException) as raised:
        await route.endpoint(ORG_A_ID, SimpleNamespace(), db)

    assert raised.value.status_code == 404

    viewer = SimpleNamespace(role=api.UserRole.viewer)
    response = await _request(_FakeDb(None, viewer), ORG_A_ID)
    assert response.status_code == 404
