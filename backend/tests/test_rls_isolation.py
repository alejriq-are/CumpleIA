"""Tests de Row-Level Security a nivel de base de datos.

A diferencia de `test_tenant_isolation.py` (que verifica el chequeo de
membresía en `app/core/deps.py` a través de la API HTTP), estos tests hablan
directo con Postgres usando el rol restringido `app_user` (APP_DATABASE_URL,
sin BYPASSRLS) y SIN pasar por FastAPI. El objetivo es probar la segunda capa
de defensa exigida por CLAUDE.md: si una consulta futura olvidara filtrar por
organization_id, RLS debe bloquear igual el cruce entre organizaciones.

También cubren el caso "huevo y gallina" del alta de tenant (POST
/organizations en app/api/organizations.py crea la organización y la primera
membresía 'owner' sin que el usuario tenga membresías previas) y el intento
de abuso de esa misma vía de bootstrap para autoadjudicarse una organización
ajena ya existente.

Requiere: Docker Postgres corriendo con la migración aplicada (la migración
0001 crea el rol `app_user`, sus políticas y las funciones SECURITY DEFINER).
"""

import uuid

import pytest
import pytest_asyncio
from sqlalchemy import delete, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.db.models import Profile

settings = get_settings()

_SUPERADMIN_PROFILE_ID = uuid.uuid4()
_SUPERADMIN_AUTH_ID = uuid.uuid4()


@pytest_asyncio.fixture(loop_scope="function")
async def app_role_session():
    """Sesión nueva conectada como `app_user` (rol de runtime, sin BYPASSRLS).

    NullPool: cada test parte de una conexión física nueva, sin GUCs de sesión
    filtrados de un test anterior.

    `loop_scope="function"` explícito: sin esto, esta fixture hereda el
    default del proyecto (`asyncio_default_fixture_loop_scope = "session"`,
    ver pyproject.toml) mientras el test corre en su propio loop de función.
    El engine/conexión asyncpg quedan atados al loop de sesión y el test,
    ejecutando en otro loop, revienta al hacer rollback/close con
    "Future attached to a different loop".
    """
    engine = create_async_engine(settings.app_database_url, poolclass=NullPool)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.rollback()
    await engine.dispose()


async def _set_auth_user(session, auth_user_id) -> None:
    """Emula lo que hace get_current_profile() en cada request real."""
    await session.execute(
        text("SELECT set_config('request.jwt.claim.sub', :sub, true)"),
        {"sub": str(auth_user_id)},
    )


@pytest_asyncio.fixture
async def superadmin_sin_membresia(_session_factory):
    """Perfil `is_superadmin=True` sin ninguna membresía en ninguna
    organización — exactamente el caso que exponía el bug de `org_visibility`
    (revisión del PR #13, hallazgo #1): `require_permission` ya concede el
    permiso a un superadmin sobre cualquier organización sin exigir
    membresía, pero la política RLS de `organizations` no lo dejaba pasar."""
    async with _session_factory() as session:
        session.add(
            Profile(
                id=_SUPERADMIN_PROFILE_ID,
                auth_user_id=_SUPERADMIN_AUTH_ID,
                email="superadmin_rls_test@cumpleia.cl",
                is_superadmin=True,
            )
        )
        await session.commit()

    yield _SUPERADMIN_AUTH_ID

    async with _session_factory() as session:
        await session.execute(
            delete(Profile).where(Profile.id == _SUPERADMIN_PROFILE_ID)
        )
        await session.commit()


# ── Aislamiento cruzado a nivel de RLS (sin pasar por la API) ─────────────────


@pytest.mark.asyncio
async def test_rls_filtra_organizations_por_usuario(
    app_role_session, auth_a_id, org_a_id, org_b_id, _seed_test_data
):
    """Usuario A, consultando directo con SQL, solo ve su propia organización."""
    await _set_auth_user(app_role_session, auth_a_id)
    result = await app_role_session.execute(text("SELECT id FROM organizations"))
    visible_ids = {row[0] for row in result}
    assert org_a_id in visible_ids
    assert org_b_id not in visible_ids


@pytest.mark.asyncio
async def test_rls_bloquea_lectura_directa_de_memberships_ajenas(
    app_role_session, auth_a_id, org_b_id, _seed_test_data
):
    """Aunque el SQL no filtre por organization_id, RLS igual excluye la fila."""
    await _set_auth_user(app_role_session, auth_a_id)
    result = await app_role_session.execute(
        text("SELECT id FROM memberships WHERE organization_id = :org_id"),
        {"org_id": str(org_b_id)},
    )
    assert result.first() is None


@pytest.mark.asyncio
async def test_rls_sin_auth_uid_no_ve_ninguna_organizacion(
    app_role_session, org_a_id, org_b_id, _seed_test_data
):
    """Si nunca se pobló auth.uid() (bug de wiring), RLS falla cerrado: 0 filas."""
    result = await app_role_session.execute(text("SELECT id FROM organizations"))
    assert result.first() is None


# ── Alta de tenant (bootstrap): debe seguir funcionando bajo RLS ─────────────


@pytest.mark.asyncio
async def test_bootstrap_crea_organizacion_y_primera_membresia_propia(
    app_role_session, auth_a_id, profile_a_id, _seed_test_data
):
    """Reproduce exactamente POST /organizations con `app_user` + RLS activo.

    En ese momento el usuario no tiene ninguna membresía sobre la organización
    nueva (auth_org_ids() todavía no la incluye), así que esto solo pasa si
    org_self_service_insert y memberships_self_bootstrap_insert están vigentes.
    """
    await _set_auth_user(app_role_session, auth_a_id)
    new_org_id = uuid.uuid4()

    await app_role_session.execute(
        text("INSERT INTO organizations (id, name) VALUES (:id, :name)"),
        {"id": str(new_org_id), "name": "Organización bootstrap (test)"},
    )
    await app_role_session.execute(
        text(
            "INSERT INTO memberships (organization_id, profile_id, role) "
            "VALUES (:org_id, :profile_id, 'owner')"
        ),
        {"org_id": str(new_org_id), "profile_id": str(profile_a_id)},
    )

    result = await app_role_session.execute(
        text("SELECT role FROM memberships WHERE organization_id = :org_id"),
        {"org_id": str(new_org_id)},
    )
    row = result.first()
    assert row is not None, "La membresía de bootstrap no quedó visible/creada."
    assert row[0] == "owner"


@pytest.mark.asyncio
async def test_bootstrap_no_permite_apropiarse_de_organizacion_ajena(
    app_role_session, auth_a_id, profile_a_id, org_b_id, _seed_test_data
):
    """Usuario A no puede usar la vía de bootstrap para autoasignarse 'owner'
    de la organización B, que ya tiene dueño (profile_b).

    Esto es exactamente el hueco que introduciría un NOT EXISTS ingenuo contra
    `memberships` dentro de la propia política: como A no ve las membresías de
    B por RLS, un NOT EXISTS directo (sin SECURITY DEFINER) parecería "vacío"
    y dejaría pasar el INSERT. organization_is_unclaimed() evita eso.
    """
    await _set_auth_user(app_role_session, auth_a_id)

    with pytest.raises(DBAPIError, match="row-level security"):
        await app_role_session.execute(
            text(
                "INSERT INTO memberships (organization_id, profile_id, role) "
                "VALUES (:org_id, :profile_id, 'owner')"
            ),
            {"org_id": str(org_b_id), "profile_id": str(profile_a_id)},
        )


# ── org_visibility: superadmin sin membresía (fix de la revisión del PR #13) ──


@pytest.mark.asyncio
async def test_rls_superadmin_ve_organizacion_sin_ser_miembro(
    app_role_session, superadmin_sin_membresia, org_a_id, _seed_test_data
):
    """`require_permission` ya concede el permiso a un superadmin sobre
    cualquier organización sin exigir membresía (ver ADR 0001); esta política
    debe dejarlo pasar también a nivel de RLS, no solo a nivel de aplicación —
    de lo contrario código como app/services/diagnostico_ia.py::generar_informe
    (que sí necesita leer la fila, no solo el permiso) rompe en silencio."""
    await _set_auth_user(app_role_session, superadmin_sin_membresia)
    result = await app_role_session.execute(
        text("SELECT id FROM organizations WHERE id = :org_id"),
        {"org_id": str(org_a_id)},
    )
    assert result.first() is not None


@pytest.mark.asyncio
async def test_rls_no_superadmin_sigue_sin_ver_organizacion_ajena(
    app_role_session, auth_a_id, org_b_id, _seed_test_data
):
    """La relajación de org_visibility es específica de is_superadmin(): un
    usuario normal sin membresía en B sigue sin poder verla (regresión del
    aislamiento multi-tenant que la política ya garantizaba)."""
    await _set_auth_user(app_role_session, auth_a_id)
    result = await app_role_session.execute(
        text("SELECT id FROM organizations WHERE id = :org_id"),
        {"org_id": str(org_b_id)},
    )
    assert result.first() is None
