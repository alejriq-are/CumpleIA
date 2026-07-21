"""Tests de aprovisionamiento de usuarios y organizaciones (onboarding Fase 0).

Cubren el camino REAL (sin override de get_current_profile), validando el JWT
ES256 contra un JWKS simulado, igual que test_auth.py:

- Aprovisionamiento JIT del perfil idempotente bajo doble llamada (incl. concurrente).
- Usuario recién aprovisionado, sin membresías → GET /me = 200.
- POST /organizations crea la membresía `owner` y habilita el acceso al tenant.
- Usuario sin membresía intentando acceder al recurso de otra org → 403.

Requiere: Docker Postgres corriendo con la migración aplicada.
"""

import asyncio
import uuid
from datetime import UTC, datetime, timedelta

import jwt
import pytest
import pytest_asyncio
from cryptography.hazmat.primitives.asymmetric import ec
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, func, select

from app.core import security
from app.core.config import get_settings
from app.db.models import Membership, Organization, Profile

_KID = "test-key-1"

# auth_user_id fijo para el "usuario nuevo": no está en el seed de conftest,
# así que su perfil solo puede existir si el aprovisionamiento JIT lo crea.
_NEW_AUTH_ID = uuid.UUID("c0000000-0000-0000-0000-000000000003")
_NEW_EMAIL = "nuevo@test.cl"


# ── Infraestructura de firma ES256 + JWKS simulado ───────────────────────────


class _FakeSigningKey:
    def __init__(self, key):
        self.key = key


class _FakeJWKSClient:
    def __init__(self, public_key):
        self._public_key = public_key

    def get_signing_key_from_jwt(self, token):  # noqa: ARG002
        return _FakeSigningKey(self._public_key)


@pytest.fixture
def signing_key():
    return ec.generate_private_key(ec.SECP256R1())


@pytest.fixture
def patch_jwks(signing_key, monkeypatch):
    fake = _FakeJWKSClient(signing_key.public_key())
    monkeypatch.setattr(security, "_get_jwks_client", lambda: fake)
    return fake


def _issuer() -> str:
    return f"{get_settings().supabase_url.rstrip('/')}/auth/v1"


def _sign(
    private_key,
    *,
    sub: str,
    email: str | None = _NEW_EMAIL,
    exp_delta: timedelta = timedelta(hours=1),
) -> str:
    now = datetime.now(tz=UTC)
    payload: dict = {
        "sub": sub,
        "aud": "authenticated",
        "iss": _issuer(),
        "iat": now,
        "exp": now + exp_delta,
    }
    if email is not None:
        payload["email"] = email
    return jwt.encode(payload, private_key, algorithm="ES256", headers={"kid": _KID})


# ── Limpieza del usuario nuevo (antes y después de cada test) ─────────────────


async def _purge_new_user(session_factory) -> None:
    """Elimina, en orden FK-seguro, el perfil nuevo y todo lo que colgó de él."""
    async with session_factory() as session:
        profile = (
            await session.execute(
                select(Profile).where(Profile.auth_user_id == _NEW_AUTH_ID)
            )
        ).scalar_one_or_none()
        if profile is not None:
            org_ids = (
                (
                    await session.execute(
                        select(Membership.organization_id).where(
                            Membership.profile_id == profile.id
                        )
                    )
                )
                .scalars()
                .all()
            )
            await session.execute(
                delete(Membership).where(Membership.profile_id == profile.id)
            )
            if org_ids:
                await session.execute(
                    delete(Organization).where(Organization.id.in_(org_ids))
                )
            await session.execute(delete(Profile).where(Profile.id == profile.id))
            await session.commit()


@pytest_asyncio.fixture
async def clean_new_user(_session_factory):
    await _purge_new_user(_session_factory)
    yield
    await _purge_new_user(_session_factory)


# ── Tests ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_primer_acceso_crea_perfil_y_devuelve_200(
    patch_jwks, signing_key, app_db_only, clean_new_user, _session_factory
):
    """Usuario nuevo (sin fila previa) → JIT crea el perfil y /me = 200."""
    token = _sign(signing_key, sub=str(_NEW_AUTH_ID))
    async with AsyncClient(
        transport=ASGITransport(app=app_db_only), base_url="http://test"
    ) as ac:
        response = await ac.get("/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200, response.text
    assert response.json()["email"] == _NEW_EMAIL

    # El perfil quedó persistido con los datos del token.
    async with _session_factory() as session:
        profile = (
            await session.execute(
                select(Profile).where(Profile.auth_user_id == _NEW_AUTH_ID)
            )
        ).scalar_one()
        assert profile.email == _NEW_EMAIL


@pytest.mark.asyncio
async def test_perfil_sin_membresias_devuelve_200(
    patch_jwks, signing_key, app_db_only, clean_new_user
):
    """Un perfil recién aprovisionado sin ninguna membresía igual obtiene 200 en /me.

    Perfil ausente/no-onboardeado NUNCA es 401: el token es válido.
    """
    token = _sign(signing_key, sub=str(_NEW_AUTH_ID))
    async with AsyncClient(
        transport=ASGITransport(app=app_db_only), base_url="http://test"
    ) as ac:
        response = await ac.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, response.text


@pytest.mark.asyncio
async def test_jit_idempotente_bajo_doble_llamada(
    patch_jwks, signing_key, app_db_only, clean_new_user, _session_factory
):
    """Dos peticiones concurrentes del mismo usuario nuevo → un solo perfil."""
    token = _sign(signing_key, sub=str(_NEW_AUTH_ID))

    async with AsyncClient(
        transport=ASGITransport(app=app_db_only), base_url="http://test"
    ) as ac:
        r1, r2 = await asyncio.gather(
            ac.get("/me", headers={"Authorization": f"Bearer {token}"}),
            ac.get("/me", headers={"Authorization": f"Bearer {token}"}),
        )

    assert r1.status_code == 200, r1.text
    assert r2.status_code == 200, r2.text
    assert r1.json()["id"] == r2.json()["id"]

    async with _session_factory() as session:
        count = (
            await session.execute(
                select(func.count())
                .select_from(Profile)
                .where(Profile.auth_user_id == _NEW_AUTH_ID)
            )
        ).scalar_one()
    assert count == 1, f"Se esperaba 1 perfil, hay {count} (JIT no fue idempotente)."


@pytest.mark.asyncio
async def test_crear_organizacion_genera_membresia_owner(
    patch_jwks, signing_key, app_db_only, clean_new_user
):
    """POST /organizations → 201, y el creador queda con acceso owner al tenant."""
    token = _sign(signing_key, sub=str(_NEW_AUTH_ID))
    headers = {"Authorization": f"Bearer {token}"}

    async with AsyncClient(
        transport=ASGITransport(app=app_db_only), base_url="http://test"
    ) as ac:
        created = await ac.post(
            "/organizations",
            headers=headers,
            json={"name": "PYME Nueva SpA", "rut": "77.888.999-0"},
        )
        assert created.status_code == 201, created.text
        body = created.json()
        assert body["role"] == "owner"
        org_id = body["id"]

        # La membresía habilita el acceso al tenant recién creado.
        membership = await ac.get(
            "/me/membership", headers={**headers, "X-Organization-Id": org_id}
        )
    assert membership.status_code == 200, membership.text
    assert membership.json()["role"] == "owner"
    assert str(membership.json()["organization_id"]) == org_id


@pytest.mark.asyncio
async def test_usuario_sin_membresia_no_accede_a_org_ajena(
    patch_jwks, signing_key, app_db_only, clean_new_user, org_a_id
):
    """Usuario nuevo (sin membresías) pide la org A del seed → 403."""
    token = _sign(signing_key, sub=str(_NEW_AUTH_ID))
    async with AsyncClient(
        transport=ASGITransport(app=app_db_only), base_url="http://test"
    ) as ac:
        response = await ac.get(
            "/me/membership",
            headers={
                "Authorization": f"Bearer {token}",
                "X-Organization-Id": str(org_a_id),
            },
        )
    assert response.status_code == 403, response.text
