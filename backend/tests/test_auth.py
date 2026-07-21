"""Tests de validación de JWT (ES256 contra JWKS de Supabase).

No se llama a Supabase de verdad: se genera un par de claves ES256 en el propio
test y se simula el cliente JWKS parcheando `app.core.security._get_jwks_client`.

Cubre:
- Sin header Authorization → 401 con WWW-Authenticate: Bearer
- Token con formato basura (abc.def.ghi) → 401
- Token firmado con una clave ES256 propia (no la de Supabase) → 401
- Token expirado → 401
- Token válido (firma ES256 + JWKS simulados) → 200
- JWKS inaccesible (red caída) → 503
- Config sin SUPABASE_URL → la app falla al arrancar
"""

from datetime import UTC, datetime, timedelta

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from httpx import ASGITransport, AsyncClient
from jwt.exceptions import PyJWKClientConnectionError

from app.core import security
from app.core.config import get_settings

_KID = "test-key-1"


# ── Infraestructura de claves y JWKS simulado ────────────────────────────────


class _FakeSigningKey:
    def __init__(self, key):
        self.key = key


class _FakeJWKSClient:
    """Sustituye a PyJWKClient: devuelve siempre la clave pública de test."""

    def __init__(self, public_key):
        self._public_key = public_key

    def get_signing_key_from_jwt(self, token):  # noqa: ARG002
        return _FakeSigningKey(self._public_key)


class _DownJWKSClient:
    """Simula un JWKS inaccesible (red caída)."""

    def get_signing_key_from_jwt(self, token):  # noqa: ARG002
        raise PyJWKClientConnectionError("no se pudo conectar al JWKS")


@pytest.fixture
def signing_key():
    """Par de claves EC P-256 (ES256) fijo para el test."""
    return ec.generate_private_key(ec.SECP256R1())


@pytest.fixture
def patch_jwks(signing_key, monkeypatch):
    """Parchea el cliente JWKS para que valide con la clave pública de test."""
    fake = _FakeJWKSClient(signing_key.public_key())
    monkeypatch.setattr(security, "_get_jwks_client", lambda: fake)
    return fake


def _issuer() -> str:
    return f"{get_settings().supabase_url.rstrip('/')}/auth/v1"


def _sign(
    private_key,
    *,
    sub: str,
    exp_delta: timedelta = timedelta(hours=1),
    aud: str = "authenticated",
    iss: str | None = None,
    kid: str = _KID,
) -> str:
    now = datetime.now(tz=UTC)
    payload = {
        "sub": sub,
        "aud": aud,
        "iss": iss if iss is not None else _issuer(),
        "iat": now,
        "exp": now + exp_delta,
    }
    return jwt.encode(payload, private_key, algorithm="ES256", headers={"kid": kid})


# ── Tests ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_sin_header_devuelve_401():
    from app.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/me")
    assert response.status_code == 401
    assert response.headers.get("WWW-Authenticate") == "Bearer"


@pytest.mark.asyncio
async def test_token_basura_devuelve_401(patch_jwks):
    from app.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/me", headers={"Authorization": "Bearer abc.def.ghi"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_token_firmado_con_clave_ajena_devuelve_401(patch_jwks, auth_a_id):
    """Token firmado con OTRA clave ES256: la firma no valida → 401."""
    from app.main import app

    clave_ajena = ec.generate_private_key(ec.SECP256R1())
    token = _sign(clave_ajena, sub=str(auth_a_id))
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_token_expirado_devuelve_401(patch_jwks, signing_key, auth_a_id):
    from app.main import app

    token = _sign(signing_key, sub=str(auth_a_id), exp_delta=timedelta(hours=-1))
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_audiencia_incorrecta_devuelve_401(patch_jwks, signing_key, auth_a_id):
    token = _sign(signing_key, sub=str(auth_a_id), aud="otra-audiencia")
    from app.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_token_valido_devuelve_200(
    patch_jwks, signing_key, auth_a_id, app_db_only
):
    """Token ES256 válido + JWKS simulado + perfil en BD → 200."""
    token = _sign(signing_key, sub=str(auth_a_id))
    async with AsyncClient(
        transport=ASGITransport(app=app_db_only), base_url="http://test"
    ) as ac:
        response = await ac.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "usuario_a@test.cl"


@pytest.mark.asyncio
async def test_jwks_inaccesible_devuelve_503(signing_key, auth_a_id, monkeypatch):
    """Si el JWKS no se puede descargar → 503, no 401."""
    monkeypatch.setattr(security, "_get_jwks_client", lambda: _DownJWKSClient())
    token = _sign(signing_key, sub=str(auth_a_id))
    from app.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 503


def test_config_sin_supabase_url_falla_con_mensaje_claro(monkeypatch):
    """Sin SUPABASE_URL definido, Settings no valida y el mensaje dice dónde buscar.

    Antes de la validación custom, el error era el genérico "Field required"
    de pydantic, que no indica qué archivo revisar cuando el .env no aporta
    el valor.
    """
    from pydantic import ValidationError

    from app.core.config import Settings

    monkeypatch.delenv("SUPABASE_URL", raising=False)
    # _env_file=None evita que un .env local aporte el valor
    with pytest.raises(ValidationError, match="SUPABASE_URL no está definido"):
        Settings(_env_file=None)


def test_config_produccion_exige_secretos():
    """En producción, faltar service_role/anon/secret_key hace fallar el arranque.

    Las variables sensibles se neutralizan en el fixture autouse `_hermetic_settings`
    (conftest), así que este test es determinista con o sin secretos definidos en
    el entorno real (local o CI).
    """
    from pydantic import ValidationError

    from app.core.config import Settings

    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            supabase_url="https://x.supabase.co",
            environment="production",
        )


def test_config_produccion_con_secretos_arranca(monkeypatch):
    """Caso inverso: con los tres secretos presentes y environment=production,
    Settings se construye SIN lanzar.

    Sin este test, `test_config_produccion_exige_secretos` pasaría igual si el
    validador reventara por un motivo equivocado: aquí se prueba que exige por
    AUSENCIA de secretos, no por otra causa.
    """
    from app.core.config import Settings

    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "dummy-service-role")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "dummy-anon")
    monkeypatch.setenv("SECRET_KEY", "dummy-secret")

    settings = Settings(
        _env_file=None,
        supabase_url="https://x.supabase.co",
        environment="production",
    )

    assert settings.is_production
    assert settings.supabase_service_role_key == "dummy-service-role"
    assert settings.supabase_anon_key == "dummy-anon"
    assert settings.secret_key == "dummy-secret"
