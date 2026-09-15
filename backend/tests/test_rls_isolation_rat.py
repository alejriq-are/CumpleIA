"""Persistencia, RLS e integridad multi-tenant del Módulo 2 — RAT.

Valida tres capas distintas:

1. RLS real usando `app_user` sin BYPASSRLS.
2. Integridad referencial tenant-aware mediante FK compuestas.
3. Persistencia válida de las entidades normalizadas del RAT.

No prueba API ni frontend: M2-T1 cubre únicamente persistencia.
"""

import uuid

import pytest
import pytest_asyncio
from sqlalchemy import delete, select, text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.db.models import (
    InternationalTransfer,
    System,
    Treatment,
    TreatmentDataCategory,
    TreatmentDataSource,
    TreatmentDataSubject,
    TreatmentPurpose,
    TreatmentSystem,
    TreatmentVendor,
    Vendor,
)

settings = get_settings()


@pytest_asyncio.fixture(loop_scope="function")
async def app_role_session():
    """Sesión directa como app_user, con RLS realmente activo."""
    engine = create_async_engine(
        settings.app_database_url,
        poolclass=NullPool,
    )
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await engine.dispose()


async def _set_auth_user(session, auth_user_id) -> None:
    await session.execute(
        text("SELECT set_config(" "'request.jwt.claim.sub', :sub, true" ")"),
        {"sub": str(auth_user_id)},
    )


@pytest_asyncio.fixture
async def rat_base_data(
    _session_factory,
    org_a_id,
    org_b_id,
    _seed_test_data,
):
    """Crea entidades raíz M2 en dos organizaciones usando rol admin."""

    treatment_a_id = uuid.uuid4()
    treatment_b_id = uuid.uuid4()
    system_a_id = uuid.uuid4()
    system_b_id = uuid.uuid4()
    vendor_a_id = uuid.uuid4()
    vendor_b_id = uuid.uuid4()

    async with _session_factory() as session:
        session.add_all(
            [
                Treatment(
                    id=treatment_a_id,
                    organization_id=org_a_id,
                    name="Gestión clientes Org A",
                    organization_role="responsable",
                ),
                Treatment(
                    id=treatment_b_id,
                    organization_id=org_b_id,
                    name="Gestión clientes Org B",
                    organization_role="responsable",
                ),
                System(
                    id=system_a_id,
                    organization_id=org_a_id,
                    name="CRM Org A",
                ),
                System(
                    id=system_b_id,
                    organization_id=org_b_id,
                    name="CRM Org B",
                ),
                Vendor(
                    id=vendor_a_id,
                    organization_id=org_a_id,
                    name="Proveedor Org A",
                    country="Chile",
                ),
                Vendor(
                    id=vendor_b_id,
                    organization_id=org_b_id,
                    name="Proveedor Org B",
                    country="Estados Unidos",
                ),
            ]
        )
        await session.commit()

    yield {
        "treatment_a": treatment_a_id,
        "treatment_b": treatment_b_id,
        "system_a": system_a_id,
        "system_b": system_b_id,
        "vendor_a": vendor_a_id,
        "vendor_b": vendor_b_id,
    }

    # Limpieza explícita en orden de dependencias.
    async with _session_factory() as session:
        treatment_ids = [treatment_a_id, treatment_b_id]

        await session.execute(
            delete(InternationalTransfer).where(
                InternationalTransfer.treatment_id.in_(treatment_ids)
            )
        )
        await session.execute(
            delete(TreatmentVendor).where(
                TreatmentVendor.treatment_id.in_(treatment_ids)
            )
        )
        await session.execute(
            delete(TreatmentSystem).where(
                TreatmentSystem.treatment_id.in_(treatment_ids)
            )
        )
        await session.execute(
            delete(TreatmentDataSource).where(
                TreatmentDataSource.treatment_id.in_(treatment_ids)
            )
        )
        await session.execute(
            delete(TreatmentDataSubject).where(
                TreatmentDataSubject.treatment_id.in_(treatment_ids)
            )
        )
        await session.execute(
            delete(TreatmentDataCategory).where(
                TreatmentDataCategory.treatment_id.in_(treatment_ids)
            )
        )
        await session.execute(
            delete(TreatmentPurpose).where(
                TreatmentPurpose.treatment_id.in_(treatment_ids)
            )
        )
        await session.execute(delete(Treatment).where(Treatment.id.in_(treatment_ids)))
        await session.execute(
            delete(System).where(System.id.in_([system_a_id, system_b_id]))
        )
        await session.execute(
            delete(Vendor).where(Vendor.id.in_([vendor_a_id, vendor_b_id]))
        )
        await session.commit()


# ── RLS de la entidad raíz ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_rls_rat_permite_lectura_de_treatment_propio(
    app_role_session,
    auth_a_id,
    org_a_id,
    rat_base_data,
):
    await _set_auth_user(app_role_session, auth_a_id)

    result = await app_role_session.execute(
        text("SELECT id FROM treatments " "WHERE organization_id = :org_id"),
        {"org_id": str(org_a_id)},
    )

    ids = {row[0] for row in result}
    assert rat_base_data["treatment_a"] in ids


@pytest.mark.asyncio
async def test_rls_rat_bloquea_lectura_de_treatment_ajeno(
    app_role_session,
    auth_b_id,
    org_a_id,
    rat_base_data,
):
    await _set_auth_user(app_role_session, auth_b_id)

    result = await app_role_session.execute(
        text("SELECT id FROM treatments " "WHERE organization_id = :org_id"),
        {"org_id": str(org_a_id)},
    )

    assert result.first() is None


# ── RLS de tablas nuevas ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_rls_rat_bloquea_insert_de_finalidad_en_org_ajena(
    app_role_session,
    auth_b_id,
    org_a_id,
    rat_base_data,
):
    """Usuario B no puede insertar contenido bajo organization_id de A."""

    await _set_auth_user(app_role_session, auth_b_id)

    with pytest.raises(DBAPIError, match="row-level security"):
        await app_role_session.execute(
            text(
                """
                INSERT INTO treatment_purposes
                    (organization_id, treatment_id, purpose)
                VALUES
                    (:org_id, :treatment_id, :purpose)
                """
            ),
            {
                "org_id": str(org_a_id),
                "treatment_id": str(rat_base_data["treatment_a"]),
                "purpose": "Finalidad no autorizada",
            },
        )


# ── Integridad cross-tenant ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_fk_compuesta_bloquea_treatment_system_cross_tenant(
    _session_factory,
    org_a_id,
    rat_base_data,
):
    """Treatment de A no puede enlazarse con System de B."""

    async with _session_factory() as session:
        session.add(
            TreatmentSystem(
                organization_id=org_a_id,
                treatment_id=rat_base_data["treatment_a"],
                system_id=rat_base_data["system_b"],
            )
        )

        with pytest.raises(IntegrityError):
            await session.commit()

        await session.rollback()


@pytest.mark.asyncio
async def test_fk_compuesta_bloquea_treatment_vendor_cross_tenant(
    _session_factory,
    org_a_id,
    rat_base_data,
):
    """Treatment de A no puede enlazarse con Vendor de B."""

    async with _session_factory() as session:
        session.add(
            TreatmentVendor(
                organization_id=org_a_id,
                treatment_id=rat_base_data["treatment_a"],
                vendor_id=rat_base_data["vendor_b"],
                relationship_type="encargado",
            )
        )

        with pytest.raises(IntegrityError):
            await session.commit()

        await session.rollback()


@pytest.mark.asyncio
async def test_fk_compuesta_bloquea_transferencia_con_vendor_cross_tenant(
    _session_factory,
    org_a_id,
    rat_base_data,
):
    """Transferencia de A no puede referenciar Vendor de B."""

    async with _session_factory() as session:
        session.add(
            InternationalTransfer(
                organization_id=org_a_id,
                treatment_id=rat_base_data["treatment_a"],
                vendor_id=rat_base_data["vendor_b"],
                destination_country="Estados Unidos",
                adequacy_status="pendiente",
            )
        )

        with pytest.raises(IntegrityError):
            await session.commit()

        await session.rollback()


# ── Persistencia válida dentro del mismo tenant ──────────────────────────────


@pytest.mark.asyncio
async def test_rat_persistencia_normalizada_mismo_tenant(
    _session_factory,
    org_a_id,
    rat_base_data,
):
    treatment_id = rat_base_data["treatment_a"]

    async with _session_factory() as session:
        session.add_all(
            [
                TreatmentPurpose(
                    organization_id=org_a_id,
                    treatment_id=treatment_id,
                    purpose="Gestionar relación contractual con clientes",
                    is_primary=True,
                    sort_order=0,
                ),
                TreatmentDataCategory(
                    organization_id=org_a_id,
                    treatment_id=treatment_id,
                    category_code="identificacion",
                    category_name="Datos de identificación",
                    is_sensitive=False,
                ),
                TreatmentDataSubject(
                    organization_id=org_a_id,
                    treatment_id=treatment_id,
                    category_code="clientes",
                    category_name="Clientes",
                ),
                TreatmentDataSource(
                    organization_id=org_a_id,
                    treatment_id=treatment_id,
                    source_type="titular",
                    description="Formulario de contratación",
                ),
                TreatmentSystem(
                    organization_id=org_a_id,
                    treatment_id=treatment_id,
                    system_id=rat_base_data["system_a"],
                ),
                TreatmentVendor(
                    organization_id=org_a_id,
                    treatment_id=treatment_id,
                    vendor_id=rat_base_data["vendor_a"],
                    relationship_type="encargado",
                    has_data_access=True,
                    has_contract=True,
                ),
                InternationalTransfer(
                    organization_id=org_a_id,
                    treatment_id=treatment_id,
                    vendor_id=rat_base_data["vendor_a"],
                    destination_country="Estados Unidos",
                    adequacy_status="pendiente",
                ),
            ]
        )

        await session.commit()

    async with _session_factory() as session:
        assert (
            await session.scalar(
                select(TreatmentPurpose).where(
                    TreatmentPurpose.treatment_id == treatment_id
                )
            )
            is not None
        )
        assert (
            await session.scalar(
                select(TreatmentDataCategory).where(
                    TreatmentDataCategory.treatment_id == treatment_id
                )
            )
            is not None
        )
        assert (
            await session.scalar(
                select(TreatmentDataSubject).where(
                    TreatmentDataSubject.treatment_id == treatment_id
                )
            )
            is not None
        )
        assert (
            await session.scalar(
                select(TreatmentDataSource).where(
                    TreatmentDataSource.treatment_id == treatment_id
                )
            )
            is not None
        )
        assert (
            await session.scalar(
                select(TreatmentSystem).where(
                    TreatmentSystem.treatment_id == treatment_id
                )
            )
            is not None
        )
        assert (
            await session.scalar(
                select(TreatmentVendor).where(
                    TreatmentVendor.treatment_id == treatment_id
                )
            )
            is not None
        )
        assert (
            await session.scalar(
                select(InternationalTransfer).where(
                    InternationalTransfer.treatment_id == treatment_id
                )
            )
            is not None
        )
