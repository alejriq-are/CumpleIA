import uuid
from typing import Any

from fastapi import HTTPException, status
from jose import JWTError, jwt

from app.core.config import get_settings

_ALGORITHM = "HS256"
_AUDIENCE = "authenticated"


def decode_supabase_jwt(token: str, *, secret: str | None = None) -> dict[str, Any]:
    _secret = secret or get_settings().supabase_jwt_secret
    try:
        return jwt.decode(token, _secret, algorithms=[_ALGORITHM], audience=_AUDIENCE)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def extract_auth_user_id(token: str, *, secret: str | None = None) -> uuid.UUID:
    payload = decode_supabase_jwt(token, secret=secret)
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sin identificador de usuario",
        )
    try:
        return uuid.UUID(sub)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identificador de usuario inválido en el token",
        ) from exc
