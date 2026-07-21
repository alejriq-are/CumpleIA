"""Validación de JWT de Supabase contra su JWKS público (ES256).

Supabase firma los access tokens con clave asimétrica (ES256) y publica las
claves públicas en `<SUPABASE_URL>/auth/v1/.well-known/jwks.json`. Aquí se
descarga y cachea ese JWKS con `PyJWKClient`, se selecciona la clave por el
`kid` del token y se valida firma, expiración, audiencia y emisor.

Nunca se registra el token completo en el log.
"""

import logging
import uuid
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

import jwt
from fastapi import HTTPException, status
from jwt import PyJWKClient
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidAudienceError,
    InvalidIssuerError,
    InvalidTokenError,
    PyJWKClientConnectionError,
    PyJWKClientError,
)

from app.core.config import get_settings

logger = logging.getLogger("app.auth")

_ALGORITHM = "ES256"
_AUDIENCE = "authenticated"


def _base_url() -> str:
    """URL base de Supabase sin barra final."""
    return get_settings().supabase_url.rstrip("/")


def _issuer() -> str:
    return f"{_base_url()}/auth/v1"


@lru_cache
def _get_jwks_client() -> PyJWKClient:
    """Cliente JWKS cacheado a nivel de proceso.

    `PyJWKClient` mantiene su propia caché de claves, por lo que no descarga el
    JWKS en cada petición. Se construye una sola vez gracias a `lru_cache`.
    """
    jwks_url = f"{_base_url()}/auth/v1/.well-known/jwks.json"
    return PyJWKClient(jwks_url)


def _unauthorized(detail: str = "Token inválido o expirado") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def decode_supabase_jwt(token: str) -> dict[str, Any]:
    """Valida un access token de Supabase y devuelve su payload.

    - 401 si el token está expirado, mal firmado o con audiencia/emisor incorrectos.
    - 503 si el JWKS no se puede descargar (fallo de infraestructura, no credencial).
    """
    try:
        signing_key = _get_jwks_client().get_signing_key_from_jwt(token)
    except PyJWKClientConnectionError as exc:
        # Red caída / endpoint JWKS inaccesible → no es culpa de la credencial.
        logger.error("No se pudo descargar el JWKS de Supabase: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de autenticación no disponible",
        ) from exc
    except PyJWKClientError as exc:
        # kid no encontrado en el JWKS: la clave que firmó el token no es de Supabase.
        logger.warning("kid del token no está en el JWKS de Supabase")
        raise _unauthorized() from exc
    except InvalidTokenError as exc:
        # Encabezado malformado o sin kid.
        logger.warning("Token con encabezado inválido: %s", type(exc).__name__)
        raise _unauthorized() from exc

    try:
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=[_ALGORITHM],
            audience=_AUDIENCE,
            issuer=_issuer(),
        )
    except ExpiredSignatureError as exc:
        logger.warning("Token expirado")
        raise _unauthorized("Token expirado") from exc
    except (InvalidAudienceError, InvalidIssuerError) as exc:
        logger.warning("Audiencia o emisor inválido: %s", type(exc).__name__)
        raise _unauthorized() from exc
    except InvalidTokenError as exc:
        # Firma inválida u otro problema de validación.
        logger.warning("Firma o token inválido: %s", type(exc).__name__)
        raise _unauthorized() from exc


def extract_auth_user_id(token: str) -> uuid.UUID:
    payload = decode_supabase_jwt(token)
    sub = payload.get("sub")
    if not sub:
        raise _unauthorized("Token sin identificador de usuario")
    try:
        return uuid.UUID(sub)
    except ValueError as exc:
        raise _unauthorized("Identificador de usuario inválido en el token") from exc


@dataclass(frozen=True)
class AuthIdentity:
    """Identidad derivada EXCLUSIVAMENTE de los claims del JWT ya validado.

    `auth_user_id` (el `sub` de Supabase) es la clave de vinculación: única e
    inmutable. `email` y `full_name` se usan solo para poblar el perfil en el
    aprovisionamiento JIT; nunca se leen del cuerpo de la petición.
    """

    auth_user_id: uuid.UUID
    email: str | None
    full_name: str | None


def extract_auth_identity(token: str) -> AuthIdentity:
    """Valida el token y devuelve la identidad para aprovisionar el perfil.

    Toma `sub`, `email` y el nombre (`user_metadata.full_name` o `.name`) del
    payload firmado por Supabase. El cliente no puede influir en estos valores.
    """
    payload = decode_supabase_jwt(token)

    sub = payload.get("sub")
    if not sub:
        raise _unauthorized("Token sin identificador de usuario")
    try:
        auth_user_id = uuid.UUID(sub)
    except ValueError as exc:
        raise _unauthorized("Identificador de usuario inválido en el token") from exc

    email = payload.get("email")
    metadata = payload.get("user_metadata") or {}
    full_name = metadata.get("full_name") or metadata.get("name")

    return AuthIdentity(
        auth_user_id=auth_user_id,
        email=email,
        full_name=full_name,
    )
