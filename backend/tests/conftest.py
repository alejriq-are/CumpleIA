"""Fixtures compartidas para los tests de CumpleIA.

Estrategia de BD: los fixtures crean datos reales en la DB (commit),
los tests corren contra esos datos y el teardown los elimina.
El engine usa la misma DATABASE_URL del .env (requiere Docker Postgres activo).
"""

import os

# SUPABASE_URL es obligatorio para arrancar la app (config.py). Se define un valor
# de test ANTES de importar app.main; en CI/producción la env var real tiene
# prioridad y no es sobreescrita por setdefault.
os.environ.setdefault("SUPABASE_URL", "https://test-project.supabase.co")

import uuid  # noqa: E402

import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402
from fastapi import Depends  # noqa: E402
from sqlalchemy import delete, select, text  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.core.deps import get_current_profile  # noqa: E402
from app.db.models import Membership, Organization, Profile, UserRole  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.main import app  # noqa: E402

settings = get_settings()

# Variables de secretos que config.py exige en producción. En un entorno real
# (contenedor de dev o CI con dummies) están presentes en os.environ, y
# pydantic-settings las lee aunque se pase _env_file=None. Si no se neutralizan,
# el test que garantiza el arranque seguro en producción pasaría por omisión.
_SENSITIVE_ENV_VARS = (
    "SUPABASE_SERVICE_ROLE_KEY",
    "SUPABASE_ANON_KEY",
    "SECRET_KEY",
)


@pytest.fixture(autouse=True)
def _hermetic_settings(monkeypatch):
    """Aísla cada test de los secretos presentes en el entorno real.

    Borra las variables sensibles antes de cada test e invalida la caché de
    `get_settings()` para que cualquier reconstrucción de `Settings` vea el
    entorno neutralizado. `monkeypatch` restaura las variables al finalizar.

    Un test que necesite esos secretos presentes (p. ej. el caso inverso de
    producción) los define con `monkeypatch.setenv` dentro de su cuerpo: como
    corre después de este fixture, prevalece.
    """
    for var in _SENSITIVE_ENV_VARS:
        monkeypatch.delenv(var, raising=False)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


# IDs fijos: facilitan debugging y evitan colisiones entre ejecuciones
_ORG_A_ID = uuid.UUID("a0000000-0000-0000-0000-000000000001")
_ORG_B_ID = uuid.UUID("b0000000-0000-0000-0000-000000000001")
_PROFILE_A_ID = uuid.UUID("a0000000-0000-0000-0000-000000000002")
_PROFILE_B_ID = uuid.UUID("b0000000-0000-0000-0000-000000000002")
_AUTH_A_ID = uuid.UUID("a0000000-0000-0000-0000-000000000003")
_AUTH_B_ID = uuid.UUID("b0000000-0000-0000-0000-000000000003")


# ── Engine de test (NullPool: sin caché de conexiones, evita cross-loop reuse) ──

# Dos engines separados y con roles distintos, a propósito:
# - `_engine`/`_session_factory` (settings.database_url, rol admin): SOLO para
#   fixtures de setup/teardown/aserciones directas (sembrar orgs de test,
#   verificar filas). BYPASSRLS — nunca debe ser el que sirve una request HTTP
#   de los tests, porque eso escondería un bug real de RLS (pasó en Fase 0:
#   ver Claude_22_julio_2026/estado-23jul2026.md).
# - `_app_engine`/`_app_session_factory` (settings.app_database_url, `app_user`
#   real, sin BYPASSRLS): el que deben usar los overrides de get_db que sirven
#   una request de test, para que RLS esté realmente activo — igual que en
#   producción (ver app/db/session.py).


@pytest.fixture(scope="session")
def _engine():
    engine = create_async_engine(settings.database_url, echo=False, poolclass=NullPool)
    yield engine


@pytest.fixture(scope="session")
def _session_factory(_engine):
    return async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def _app_engine():
    engine = create_async_engine(
        settings.app_database_url, echo=False, poolclass=NullPool
    )
    yield engine


@pytest.fixture(scope="session")
def _app_session_factory(_app_engine):
    return async_sessionmaker(_app_engine, class_=AsyncSession, expire_on_commit=False)


# ── Datos de test (session-scoped: se crean una vez y se limpian al final) ────


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _seed_test_data(_session_factory):
    """Crea orgs, perfiles y membresías de test. Se limpia al final de la sesión."""
    async with _session_factory() as session:
        # Limpiar datos previos en orden FK-seguro (sin ORM cascade)
        await session.execute(
            delete(Membership).where(
                Membership.organization_id.in_([_ORG_A_ID, _ORG_B_ID])
            )
        )
        await session.execute(
            delete(Organization).where(Organization.id.in_([_ORG_A_ID, _ORG_B_ID]))
        )
        await session.execute(
            delete(Profile).where(Profile.id.in_([_PROFILE_A_ID, _PROFILE_B_ID]))
        )
        await session.commit()

        # Crear perfiles (sin FK a organizations)
        profile_a = Profile(
            id=_PROFILE_A_ID,
            auth_user_id=_AUTH_A_ID,
            email="usuario_a@test.cl",
            full_name="Usuario A",
        )
        profile_b = Profile(
            id=_PROFILE_B_ID,
            auth_user_id=_AUTH_B_ID,
            email="usuario_b@test.cl",
            full_name="Usuario B",
        )
        session.add(profile_a)
        session.add(profile_b)
        await session.flush()

        # Crear organizaciones
        org_a = Organization(id=_ORG_A_ID, name="Organización A (test)", plan="free")
        org_b = Organization(id=_ORG_B_ID, name="Organización B (test)", plan="free")
        session.add(org_a)
        session.add(org_b)
        await session.flush()

        # Membresías: A → org_a, B → org_b (cada uno solo tiene acceso a la suya)
        session.add(
            Membership(
                organization_id=_ORG_A_ID, profile_id=_PROFILE_A_ID, role=UserRole.owner
            )
        )
        session.add(
            Membership(
                organization_id=_ORG_B_ID, profile_id=_PROFILE_B_ID, role=UserRole.owner
            )
        )
        await session.commit()

    yield  # tests corren aquí

    # Teardown: eliminar en orden FK-seguro via DELETE bulk (sin ORM cascade)
    async with _session_factory() as session:
        await session.execute(
            delete(Membership).where(
                Membership.organization_id.in_([_ORG_A_ID, _ORG_B_ID])
            )
        )
        await session.execute(
            delete(Organization).where(Organization.id.in_([_ORG_A_ID, _ORG_B_ID]))
        )
        await session.execute(
            delete(Profile).where(Profile.id.in_([_PROFILE_A_ID, _PROFILE_B_ID]))
        )
        await session.commit()


# ── Perfiles expuestos a los tests ────────────────────────────────────────────


@pytest.fixture(scope="session")
def profile_a_id() -> uuid.UUID:
    return _PROFILE_A_ID


@pytest.fixture(scope="session")
def profile_b_id() -> uuid.UUID:
    return _PROFILE_B_ID


@pytest.fixture(scope="session")
def org_a_id() -> uuid.UUID:
    return _ORG_A_ID


@pytest.fixture(scope="session")
def org_b_id() -> uuid.UUID:
    return _ORG_B_ID


@pytest.fixture(scope="session")
def auth_a_id() -> uuid.UUID:
    """auth_user_id (el 'sub' del JWT) del perfil A, para firmar tokens de test."""
    return _AUTH_A_ID


@pytest.fixture(scope="session")
def auth_b_id() -> uuid.UUID:
    """auth_user_id (el 'sub' del JWT) del perfil B, para firmar tokens de test."""
    return _AUTH_B_ID


# ── Cliente HTTP con JWT override ─────────────────────────────────────────────


def _make_rls_db_override(auth_user_id: uuid.UUID, session_factory):
    """Override de get_db que corre contra `app_user` con RLS realmente activo.

    Puebla `request.jwt.claim.sub` al abrir la sesión — lo que en producción
    hace `get_current_profile()` real (ver app/core/deps.py) sobre la MISMA
    sesión que después sirve el resto del request. Acá hace falta hacerlo en
    el override de get_db porque get_current_profile también está overrideado
    (para no validar un JWT real en cada test) y por lo tanto nunca ejecuta
    ese set_config por su cuenta. Sin esto, auth.uid() quedaría NULL y RLS
    bloquearía todo (o, peor, pasaría inadvertido si el rol tuviera BYPASSRLS).
    """

    async def _override():
        async with session_factory() as session:
            await session.execute(
                text("SELECT set_config('request.jwt.claim.sub', :sub, true)"),
                {"sub": str(auth_user_id)},
            )
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    return _override


def _make_profile_override_from_db(auth_user_id: uuid.UUID):
    """Override de get_current_profile que reutiliza la sesión de get_db.

    Depende de `get_db` (no abre una sesión propia) para que la lectura del
    perfil ocurra en la misma sesión donde ya corrió el set_config de
    `_make_rls_db_override` — si abriera una sesión aparte, sería una conexión
    distinta sin auth.uid() poblado y perfectamente podría devolver 0 filas
    bajo RLS.
    """

    async def _override(db: AsyncSession = Depends(get_db)) -> Profile:
        result = await db.execute(
            select(Profile).where(Profile.auth_user_id == auth_user_id)
        )
        return result.scalar_one()

    return _override


def _make_db_override(session_factory):
    """Override de get_db que usa el engine NullPool de test (rol admin, sin RLS).

    Solo para fixtures de setup/teardown que necesitan escribir sin pasar por
    políticas de organización (p. ej. sembrar datos). Refleja el `get_db` real
    (commit al terminar, rollback ante excepción): sin el commit, las
    escrituras del request se revertirían al cerrar la sesión y no serían
    visibles para requests posteriores ni para las aserciones.
    """

    async def _override():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    return _override


@pytest.fixture
def client_a(_app_session_factory, auth_a_id, _seed_test_data):
    """AsyncClient autenticado como usuario A, contra `app_user` con RLS activo."""
    app.dependency_overrides[get_current_profile] = _make_profile_override_from_db(
        auth_a_id
    )
    app.dependency_overrides[get_db] = _make_rls_db_override(
        auth_a_id, _app_session_factory
    )
    yield app
    app.dependency_overrides.pop(get_current_profile, None)
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def client_b(_app_session_factory, auth_b_id, _seed_test_data):
    """AsyncClient autenticado como usuario B, contra `app_user` con RLS activo."""
    app.dependency_overrides[get_current_profile] = _make_profile_override_from_db(
        auth_b_id
    )
    app.dependency_overrides[get_db] = _make_rls_db_override(
        auth_b_id, _app_session_factory
    )
    yield app
    app.dependency_overrides.pop(get_current_profile, None)
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def app_db_only(_app_session_factory, _seed_test_data):
    """App con SOLO get_db overrideado, contra `app_user` con RLS activo.

    A diferencia de client_a/client_b, NO sobreescribe get_current_profile: la
    validación real del JWT (ES256 + JWKS) se ejecuta, y el propio
    get_current_profile real hace su set_config sobre esta misma sesión — no
    hace falta el override especial de get_db con set_config incluido.
    """
    app.dependency_overrides[get_db] = _make_db_override(_app_session_factory)
    yield app
    app.dependency_overrides.pop(get_db, None)
