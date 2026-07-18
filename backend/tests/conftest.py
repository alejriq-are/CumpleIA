"""Fixtures compartidas para los tests de CumpleIA.

Estrategia de BD: los fixtures crean datos reales en la DB (commit),
los tests corren contra esos datos y el teardown los elimina.
El engine usa la misma DATABASE_URL del .env (requiere Docker Postgres activo).
"""

import uuid

import pytest
import pytest_asyncio
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.core.deps import get_current_profile
from app.db.models import Membership, Organization, Profile, UserRole
from app.main import app

settings = get_settings()

# Secret fijo para tests (no necesita coincidir con Supabase en local)
TEST_JWT_SECRET = "test-jwt-secret-cumpleia-isolation-2026"

# IDs fijos: facilitan debugging y evitan colisiones entre ejecuciones
_ORG_A_ID = uuid.UUID("a0000000-0000-0000-0000-000000000001")
_ORG_B_ID = uuid.UUID("b0000000-0000-0000-0000-000000000001")
_PROFILE_A_ID = uuid.UUID("a0000000-0000-0000-0000-000000000002")
_PROFILE_B_ID = uuid.UUID("b0000000-0000-0000-0000-000000000002")
_AUTH_A_ID = uuid.UUID("a0000000-0000-0000-0000-000000000003")
_AUTH_B_ID = uuid.UUID("b0000000-0000-0000-0000-000000000003")


def make_token(auth_user_id: uuid.UUID) -> str:
    return jwt.encode(
        {"sub": str(auth_user_id), "aud": "authenticated", "role": "authenticated"},
        TEST_JWT_SECRET,
        algorithm="HS256",
    )


# ── Engine de test (session-scoped para reutilizar conexión) ──────────────────

@pytest.fixture(scope="session")
def _engine():
    engine = create_async_engine(settings.database_url, echo=False)
    yield engine
    import asyncio
    asyncio.get_event_loop().run_until_complete(engine.dispose())


@pytest.fixture(scope="session")
def _session_factory(_engine):
    return async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)


# ── Datos de test (session-scoped: se crean una vez y se limpian al final) ────

@pytest_asyncio.fixture(scope="session", autouse=True)
async def _seed_test_data(_session_factory):
    """Crea orgs, perfiles y membresías de test. Se limpia al final de la sesión."""
    async with _session_factory() as session:
        # Limpiar datos previos si quedaron de una ejecución anterior
        for model_id, Model in [
            (_ORG_A_ID, Organization), (_ORG_B_ID, Organization),
        ]:
            existing = await session.get(Model, model_id)
            if existing:
                await session.delete(existing)
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
        # Limpiar perfiles previos
        for pid in [_PROFILE_A_ID, _PROFILE_B_ID]:
            p = await session.get(Profile, pid)
            if p:
                await session.delete(p)
        await session.commit()

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
        session.add(Membership(organization_id=_ORG_A_ID, profile_id=_PROFILE_A_ID, role=UserRole.owner))
        session.add(Membership(organization_id=_ORG_B_ID, profile_id=_PROFILE_B_ID, role=UserRole.owner))
        await session.commit()

    yield  # tests corren aquí

    # Teardown: eliminar en orden inverso de FK
    async with _session_factory() as session:
        for org_id in [_ORG_A_ID, _ORG_B_ID]:
            org = await session.get(Organization, org_id)
            if org:
                await session.delete(org)
        for profile_id in [_PROFILE_A_ID, _PROFILE_B_ID]:
            profile = await session.get(Profile, profile_id)
            if profile:
                await session.delete(profile)
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
def token_a() -> str:
    return make_token(_AUTH_A_ID)

@pytest.fixture(scope="session")
def token_b() -> str:
    return make_token(_AUTH_B_ID)


# ── Cliente HTTP con JWT override ─────────────────────────────────────────────

def _make_auth_override(profile_id: uuid.UUID, session_factory):
    """Override de get_current_profile que devuelve el perfil de test desde la BD."""
    async def _override():
        async with session_factory() as session:
            profile = await session.get(Profile, profile_id)
            return profile
    return _override


@pytest.fixture
def client_a(_session_factory, _seed_test_data):
    """AsyncClient autenticado como usuario A."""
    app.dependency_overrides[get_current_profile] = _make_auth_override(
        _PROFILE_A_ID, _session_factory
    )
    yield app
    app.dependency_overrides.pop(get_current_profile, None)


@pytest.fixture
def client_b(_session_factory, _seed_test_data):
    """AsyncClient autenticado como usuario B."""
    app.dependency_overrides[get_current_profile] = _make_auth_override(
        _PROFILE_B_ID, _session_factory
    )
    yield app
    app.dependency_overrides.pop(get_current_profile, None)
