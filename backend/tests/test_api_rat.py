"""Tests HTTP end-to-end del Módulo 2 — RAT.

Ejercen FastAPI contra `app_user` con RLS activo mediante los fixtures
client_a/client_b de conftest.py.
"""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, update

from app.core.deps import get_current_profile
from app.db.models import (
    Membership,
    Profile,
    Subscription,
    SubscriptionStatus,
    System,
    Treatment,
    UserRole,
    Vendor,
)
from app.db.session import get_db
from app.main import app
from tests.conftest import (
    _make_profile_override_from_db,
    _make_rls_db_override,
)

_VIEWER_PROFILE_ID = uuid.UUID("e0000000-0000-0000-0000-000000000001")
_VIEWER_AUTH_ID = uuid.UUID("e0000000-0000-0000-0000-000000000002")


@pytest_asyncio.fixture(autouse=True)
async def _limpiar_rat(_session_factory, org_a_id, org_b_id):
    """Deja M2 limpio antes y después de cada test."""

    async def limpiar():
        async with _session_factory() as session:
            # Treatment elimina por CASCADE sus relaciones RAT y transferencias.
            await session.execute(
                delete(Treatment).where(
                    Treatment.organization_id.in_([org_a_id, org_b_id])
                )
            )
            await session.execute(
                delete(System).where(System.organization_id.in_([org_a_id, org_b_id]))
            )
            await session.execute(
                delete(Vendor).where(Vendor.organization_id.in_([org_a_id, org_b_id]))
            )
            await session.commit()

    await limpiar()
    yield
    await limpiar()


@pytest_asyncio.fixture
async def viewer_client_org_a(
    _session_factory,
    _app_session_factory,
    org_a_id,
):
    """Usuario viewer de org A: puede leer RAT pero no editarlo."""

    async with _session_factory() as session:
        session.add(
            Profile(
                id=_VIEWER_PROFILE_ID,
                auth_user_id=_VIEWER_AUTH_ID,
                email="viewer_rat_test@cumpleia.cl",
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
        _VIEWER_AUTH_ID,
        _app_session_factory,
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


@pytest_asyncio.fixture
async def org_a_suspended(_session_factory, org_a_id):
    """Suspende org A durante un test y restaura active al terminar."""

    async with _session_factory() as session:
        await session.execute(
            update(Subscription)
            .where(Subscription.organization_id == org_a_id)
            .values(status=SubscriptionStatus.suspended)
        )
        await session.commit()

    yield

    async with _session_factory() as session:
        await session.execute(
            update(Subscription)
            .where(Subscription.organization_id == org_a_id)
            .values(status=SubscriptionStatus.active)
        )
        await session.commit()


@pytest.mark.asyncio
async def test_crud_basico_treatment(client_a, org_a_id):
    headers = {"X-Organization-Id": str(org_a_id)}

    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
    ) as client:
        creado = await client.post(
            "/rat/treatments",
            headers=headers,
            json={
                "name": "Gestión de clientes",
                "organization_role": "responsable",
                "business_area": "Comercial",
            },
        )

        assert creado.status_code == 201
        treatment_id = creado.json()["id"]
        assert creado.json()["status"] == "borrador"

        listado = await client.get(
            "/rat/treatments",
            headers=headers,
        )
        assert listado.status_code == 200
        assert any(item["id"] == treatment_id for item in listado.json())

        detalle = await client.get(
            f"/rat/treatments/{treatment_id}",
            headers=headers,
        )
        assert detalle.status_code == 200
        assert detalle.json()["name"] == "Gestión de clientes"

        actualizado = await client.patch(
            f"/rat/treatments/{treatment_id}",
            headers=headers,
            json={
                "name": "Gestión comercial de clientes",
                "status": "activo",
            },
        )
        assert actualizado.status_code == 200
        assert actualizado.json()["name"] == "Gestión comercial de clientes"
        assert actualizado.json()["status"] == "activo"

        eliminado = await client.delete(
            f"/rat/treatments/{treatment_id}",
            headers=headers,
        )
        assert eliminado.status_code == 204

        inexistente = await client.get(
            f"/rat/treatments/{treatment_id}",
            headers=headers,
        )
        assert inexistente.status_code == 404


@pytest.mark.asyncio
async def test_viewer_puede_leer_pero_no_escribir(
    viewer_client_org_a,
    org_a_id,
):
    headers = {"X-Organization-Id": str(org_a_id)}

    async with AsyncClient(
        transport=ASGITransport(app=viewer_client_org_a),
        base_url="http://test",
    ) as client:
        lectura = await client.get(
            "/rat/treatments",
            headers=headers,
        )
        escritura = await client.post(
            "/rat/treatments",
            headers=headers,
            json={"name": "No permitido"},
        )

    assert lectura.status_code == 200
    assert escritura.status_code == 403


@pytest.mark.asyncio
async def test_suscripcion_suspendida_bloquea_modulo(
    client_a,
    org_a_id,
    org_a_suspended,
):
    del org_a_suspended

    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
    ) as client:
        lectura = await client.get(
            "/rat/treatments",
            headers={"X-Organization-Id": str(org_a_id)},
        )

    assert lectura.status_code == 402
    assert lectura.json()["detail"] == (
        "La organización requiere una suscripción activa"
    )


@pytest.mark.asyncio
async def test_usuario_b_no_accede_a_rat_de_org_a(
    client_b,
    org_a_id,
):
    async with AsyncClient(
        transport=ASGITransport(app=client_b),
        base_url="http://test",
    ) as client:
        respuesta = await client.get(
            "/rat/treatments",
            headers={"X-Organization-Id": str(org_a_id)},
        )

    assert respuesta.status_code == 403
    assert respuesta.json()["detail"] == "Sin acceso a esta organización"


@pytest.mark.asyncio
async def test_componentes_normalizados_aparecen_en_detalle(
    client_a,
    org_a_id,
):
    headers = {"X-Organization-Id": str(org_a_id)}

    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
    ) as client:
        treatment = await client.post(
            "/rat/treatments",
            headers=headers,
            json={"name": "Gestión de plataforma"},
        )
        assert treatment.status_code == 201
        treatment_id = treatment.json()["id"]

        purposes = await client.put(
            f"/rat/treatments/{treatment_id}/purposes",
            headers=headers,
            json={
                "items": [
                    {
                        "purpose": "Prestar el servicio",
                        "is_primary": True,
                        "sort_order": 0,
                    }
                ]
            },
        )
        assert purposes.status_code == 200

        categories = await client.put(
            f"/rat/treatments/{treatment_id}/data-categories",
            headers=headers,
            json={
                "items": [
                    {
                        "category_code": "identificacion",
                        "category_name": "Datos de identificación",
                        "is_sensitive": False,
                    }
                ]
            },
        )
        assert categories.status_code == 200

        subjects = await client.put(
            f"/rat/treatments/{treatment_id}/data-subjects",
            headers=headers,
            json={
                "items": [
                    {
                        "category_code": "clientes",
                        "category_name": "Clientes",
                    }
                ]
            },
        )
        assert subjects.status_code == 200

        sources = await client.put(
            f"/rat/treatments/{treatment_id}/data-sources",
            headers=headers,
            json={
                "items": [
                    {
                        "source_type": "titular",
                        "description": "Formulario web",
                    }
                ]
            },
        )
        assert sources.status_code == 200

        system = await client.post(
            "/rat/systems",
            headers=headers,
            json={
                "name": "CRM",
                "provider": "Proveedor CRM",
                "hosting_country": "Chile",
            },
        )
        assert system.status_code == 201
        system_id = system.json()["id"]

        relation_system = await client.put(
            f"/rat/treatments/{treatment_id}/systems",
            headers=headers,
            json={"system_ids": [system_id]},
        )
        assert relation_system.status_code == 204

        vendor = await client.post(
            "/rat/vendors",
            headers=headers,
            json={
                "name": "Cloud Provider",
                "country": "Estados Unidos",
            },
        )
        assert vendor.status_code == 201
        vendor_id = vendor.json()["id"]

        relation_vendor = await client.put(
            f"/rat/treatments/{treatment_id}/vendors",
            headers=headers,
            json={
                "items": [
                    {
                        "vendor_id": vendor_id,
                        "relationship_type": "encargado",
                        "purpose": "Hosting",
                        "has_data_access": True,
                    }
                ]
            },
        )
        assert relation_vendor.status_code == 200

        transfer = await client.post(
            f"/rat/treatments/{treatment_id}/international-transfers",
            headers=headers,
            json={
                "vendor_id": vendor_id,
                "destination_country": "Estados Unidos",
                "adequacy_status": "pendiente",
            },
        )
        assert transfer.status_code == 201

        detalle = await client.get(
            f"/rat/treatments/{treatment_id}",
            headers=headers,
        )
        assert detalle.status_code == 200

        data = detalle.json()

        assert len(data["purposes"]) == 1
        assert len(data["data_categories"]) == 1
        assert len(data["data_subjects"]) == 1
        assert len(data["data_sources"]) == 1
        assert len(data["systems"]) == 1
        assert len(data["vendors"]) == 1
        assert len(data["international_transfers"]) == 1

        assert data["systems"][0]["id"] == system_id
        assert data["vendors"][0]["vendor_id"] == vendor_id
        assert (
            data["international_transfers"][0]["destination_country"]
            == "Estados Unidos"
        )


@pytest.mark.asyncio
async def test_no_permite_vincular_system_de_otro_tenant(
    client_a,
    org_a_id,
    org_b_id,
    _session_factory,
    profile_b_id,
):
    async with _session_factory() as session:
        system_b = System(
            organization_id=org_b_id,
            name="Sistema org B",
            created_by=profile_b_id,
            updated_by=profile_b_id,
        )
        session.add(system_b)
        await session.commit()
        system_b_id = system_b.id

    headers = {"X-Organization-Id": str(org_a_id)}

    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
    ) as client:
        treatment = await client.post(
            "/rat/treatments",
            headers=headers,
            json={"name": "Tratamiento org A"},
        )
        assert treatment.status_code == 201

        respuesta = await client.put(
            f"/rat/treatments/{treatment.json()['id']}/systems",
            headers=headers,
            json={"system_ids": [str(system_b_id)]},
        )

    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == (
        "Uno o más sistemas no pertenecen a la organización"
    )
