"""RLS a nivel de base de datos para `subscriptions` (ADR 0001).

Mismo patrón que test_rls_isolation.py/test_rls_isolation_diagnosticos.py:
habla directo con Postgres usando el rol restringido `app_user`
(APP_DATABASE_URL, sin BYPASSRLS), sin pasar por FastAPI.
"""

import uuid

import pytest
import pytest_asyncio
from sqlalchemy import delete, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.db.models import Organization

settings = get_settings()


@pytest_asyncio.fixture(loop_scope="function")
async def app_role_session():
    """Ver docstring equivalente en test_rls_isolation.py."""
    engine = create_async_engine(settings.app_database_url, poolclass=NullPool)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.rollback()
    await engine.dispose()


async def _set_auth_user(session, auth_user_id) -> None:
    await session.execute(
        text("SELECT set_config('request.jwt.claim.sub', :sub, true)"),
        {"sub": str(auth_user_id)},
    )


# ── Aislamiento de lectura ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_rls_permite_lectura_directa_de_suscripcion_propia(
    app_role_session, auth_a_id, org_a_id, _seed_test_data
):
    await _set_auth_user(app_role_session, auth_a_id)
    result = await app_role_session.execute(
        text("SELECT status FROM subscriptions WHERE organization_id = :org_id"),
        {"org_id": str(org_a_id)},
    )
    row = result.first()
    assert row is not None
    assert row[0] == "active"


@pytest.mark.asyncio
async def test_rls_bloquea_lectura_directa_de_suscripcion_ajena(
    app_role_session, auth_b_id, org_a_id, _seed_test_data
):
    await _set_auth_user(app_role_session, auth_b_id)
    result = await app_role_session.execute(
        text("SELECT status FROM subscriptions WHERE organization_id = :org_id"),
        {"org_id": str(org_a_id)},
    )
    assert result.first() is None


# ── UPDATE: exclusivo de superadmin, incluso sobre la propia organización ────


@pytest.mark.asyncio
async def test_rls_bloquea_update_de_status_por_miembro_no_superadmin(
    app_role_session, auth_a_id, org_a_id, _seed_test_data
):
    """El UPDATE no lanza error (la política es USING, no una restricción de
    esquema): simplemente no afecta ninguna fila, mismo comportamiento que
    documenta la migración 0003 para config_versiones."""
    await _set_auth_user(app_role_session, auth_a_id)
    result = await app_role_session.execute(
        text(
            "UPDATE subscriptions SET status = 'suspended' "
            "WHERE organization_id = :org_id"
        ),
        {"org_id": str(org_a_id)},
    )
    assert result.rowcount == 0


# ── Bootstrap: alta de organización debe poder crear su propia suscripción ──


@pytest.mark.asyncio
async def test_bootstrap_crea_organizacion_membresia_y_suscripcion_propia(
    app_role_session, auth_a_id, profile_a_id, _seed_test_data
):
    """Reproduce POST /organizations (organizations.py) bajo `app_user` con RLS
    activo: Organization, Membership y Subscription en la misma transacción.
    Solo pasa si `subscriptions_insert` reconoce la membresía recién insertada
    vía `auth_org_ids()` (MVCC, misma transacción) sin necesitar una función
    tipo `organization_is_unclaimed()`."""
    await _set_auth_user(app_role_session, auth_a_id)
    new_org_id = uuid.uuid4()

    await app_role_session.execute(
        text("INSERT INTO organizations (id, name) VALUES (:id, :name)"),
        {"id": str(new_org_id), "name": "Organización bootstrap suscripción (test)"},
    )
    await app_role_session.execute(
        text(
            "INSERT INTO memberships (organization_id, profile_id, role) "
            "VALUES (:org_id, :profile_id, 'owner')"
        ),
        {"org_id": str(new_org_id), "profile_id": str(profile_a_id)},
    )
    await app_role_session.execute(
        text(
            "INSERT INTO subscriptions (organization_id, commitment_type, status) "
            "VALUES (:org_id, 'monthly', 'active')"
        ),
        {"org_id": str(new_org_id)},
    )

    result = await app_role_session.execute(
        text("SELECT status FROM subscriptions WHERE organization_id = :org_id"),
        {"org_id": str(new_org_id)},
    )
    row = result.first()
    assert row is not None, "La suscripción de bootstrap no quedó visible/creada."
    assert row[0] == "active"


@pytest_asyncio.fixture
async def organizacion_ajena_sin_suscripcion(_session_factory):
    """Organización de la que A/B no son miembros y que todavía no tiene fila
    en `subscriptions` — a propósito, para probar el bloqueo de RLS puro, sin
    que la unicidad de organization_id enmascare el resultado."""
    org_id = uuid.uuid4()
    async with _session_factory() as session:
        session.add(Organization(id=org_id, name="Organización ajena (test)"))
        await session.commit()

    yield org_id

    async with _session_factory() as session:
        await session.execute(delete(Organization).where(Organization.id == org_id))
        await session.commit()


@pytest.mark.asyncio
async def test_bootstrap_no_permite_crear_suscripcion_para_organizacion_ajena(
    app_role_session, auth_a_id, organizacion_ajena_sin_suscripcion, _seed_test_data
):
    """Usuario A no puede insertar una Subscription para una organización de
    la que no es miembro, aunque esa organización todavía no tenga ninguna
    fila en `subscriptions` (así que la unicidad no es lo que lo bloquea)."""
    await _set_auth_user(app_role_session, auth_a_id)

    with pytest.raises(DBAPIError, match="row-level security"):
        await app_role_session.execute(
            text(
                "INSERT INTO subscriptions "
                "(organization_id, commitment_type, status) "
                "VALUES (:org_id, 'monthly', 'active')"
            ),
            {"org_id": str(organizacion_ajena_sin_suscripcion)},
        )
