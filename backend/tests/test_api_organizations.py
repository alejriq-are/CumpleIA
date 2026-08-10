"""Tests de PATCH /organizations (edición de datos de la organización).

Hasta esta tarea no existía ningún flujo de edición — los datos de
identificación (nombre, RUT, rubro, tamaño) solo se podían fijar al crear la
organización (`POST /organizations`, ya cubierto en test_provisioning.py) o
vía el seed de desarrollo. Usa el mismo patrón `client_a`/RLS real que
test_api_diagnostico.py.

`org_a_id` es un fixture de sesión (`_seed_test_data` en conftest.py, session
-scoped): este archivo restaura los datos originales en el teardown para no
interferir con otros tests que corran después en la misma sesión de pytest.
"""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from app.core.deps import get_current_profile
from app.db.models import Membership, Organization, Profile, UserRole
from app.db.session import get_db
from app.main import app
from tests.conftest import _make_profile_override_from_db, _make_rls_db_override

_VIEWER_PROFILE_ID = uuid.uuid4()
_VIEWER_AUTH_ID = uuid.uuid4()


@pytest_asyncio.fixture(autouse=True)
async def _restaurar_organizacion_a(_session_factory, org_a_id):
    """PATCH muta la fila real de la organización semilla de test (session
    -scoped) — sin este restore, un test posterior que dependa del nombre
    original ("Organización A (test)") se rompería según el orden de
    ejecución."""
    async with _session_factory() as session:
        original = await session.get(Organization, org_a_id)
        nombre_original = original.name
        rut_original = original.rut
        industry_original = original.industry
        size_original = original.size

    yield

    async with _session_factory() as session:
        organizacion = await session.get(Organization, org_a_id)
        organizacion.name = nombre_original
        organizacion.rut = rut_original
        organizacion.industry = industry_original
        organizacion.size = size_original
        await session.commit()


@pytest_asyncio.fixture
async def viewer_client_org_a(_session_factory, _app_session_factory, org_a_id):
    """Cliente autenticado con rol `viewer` en la organización A — no tiene
    `Permission.manage_organization` (solo `view_content`)."""
    async with _session_factory() as session:
        session.add(
            Profile(
                id=_VIEWER_PROFILE_ID,
                auth_user_id=_VIEWER_AUTH_ID,
                email="viewer_org_test@cumpleia.cl",
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
async def test_owner_puede_actualizar_datos_de_organizacion(client_a, org_a_id):
    async with AsyncClient(
        transport=ASGITransport(app=client_a), base_url="http://test"
    ) as client:
        resp = await client.patch(
            "/organizations",
            headers={"X-Organization-Id": str(org_a_id)},
            json={
                "name": "Comercial Los Alerces SpA",
                "rut": "76.111.222-3",
                "industry": "Retail",
                "size": "pequeña",
            },
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(org_a_id)
    assert data["name"] == "Comercial Los Alerces SpA"
    assert data["rut"] == "76.111.222-3"
    assert data["industry"] == "Retail"
    assert data["size"] == "pequeña"

    # Persistido de verdad, no solo devuelto en la respuesta.
    async with AsyncClient(
        transport=ASGITransport(app=client_a), base_url="http://test"
    ) as client:
        organizaciones = (
            await client.get(
                "/me/organizations",
                headers={"X-Organization-Id": str(org_a_id)},
            )
        ).json()
    propia = next(o for o in organizaciones if o["id"] == str(org_a_id))
    assert propia["name"] == "Comercial Los Alerces SpA"
    assert propia["rut"] == "76.111.222-3"


@pytest.mark.asyncio
async def test_viewer_no_puede_actualizar_organizacion(viewer_client_org_a, org_a_id):
    async with AsyncClient(
        transport=ASGITransport(app=viewer_client_org_a), base_url="http://test"
    ) as client:
        resp = await client.patch(
            "/organizations",
            headers={"X-Organization-Id": str(org_a_id)},
            json={"name": "Intento no autorizado"},
        )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_actualizar_organizacion_de_otra_org_devuelve_403(client_b, org_a_id):
    """`client_b` no tiene membresía en `org_a_id` — RLS/permiso deben
    bloquearlo antes de tocar la fila de otra organización."""
    async with AsyncClient(
        transport=ASGITransport(app=client_b), base_url="http://test"
    ) as client:
        resp = await client.patch(
            "/organizations",
            headers={"X-Organization-Id": str(org_a_id)},
            json={"name": "Intento cruzado"},
        )
    assert resp.status_code == 403
