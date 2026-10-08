"""Pool administrativo separado y dependencia personal para rutas EIPD."""

from collections.abc import AsyncGenerator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError, DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.core.security import extract_auth_user_id
from app.services.eipd_policy_store import authorize_eipd_personal_actor_v1

_bearer = HTTPBearer(auto_error=False)


def _unavailable():
    return HTTPException(503, "Canal administrativo EIPD no disponible")


@lru_cache
def get_eipd_admin_session_factory():
    """Inicializacion diferida, sin credencial por defecto ni URL en errores."""
    configured = get_settings().eipd_admin_database_url
    if configured is None or not configured.get_secret_value():
        raise _unavailable()
    try:
        url = make_url(configured.get_secret_value())
        if url.drivername != "postgresql+asyncpg" or not url.username:
            raise ValueError("Canal no admitido")
        engine = create_async_engine(
            url,
            echo=False,
            hide_parameters=True,
            pool_pre_ping=True,
            isolation_level="READ COMMITTED",
        )
    except (ValueError, TypeError, ArgumentError):
        raise _unavailable() from None
    return async_sessionmaker(engine, expire_on_commit=False)


async def _prepare_channel(db):
    # Verificar el login real antes de asumir el rol limitado. Nunca SET ROLE
    # desde una conexion owner/app_user, aunque esas conexiones puedan asumirlo.
    safe = await db.scalar(
        text(
            """
        SELECT rolcanlogin AND NOT rolsuper AND NOT rolbypassrls
          AND NOT rolcreaterole AND NOT rolcreatedb AND NOT rolreplication
          AND NOT rolinherit AND rolname NOT IN ('app_user','eipd_policy_admin')
          AND pg_has_role(oid,'eipd_policy_admin','MEMBER')
          AND NOT EXISTS (
            SELECT 1 FROM pg_auth_members m
            WHERE m.member=r.oid AND m.roleid<>'eipd_policy_admin'::regrole)
          AND NOT EXISTS (SELECT 1 FROM pg_class c WHERE c.relowner=r.oid)
        FROM pg_roles r WHERE rolname=session_user
        """
        )
    )
    if safe is not True:
        raise _unavailable()
    await db.execute(text("SET LOCAL ROLE eipd_policy_admin"))


def _sqlstate(exc):
    original = exc.orig
    return getattr(original, "sqlstate", None) or getattr(original, "pgcode", None)


async def get_eipd_admin_db(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> AsyncGenerator[AsyncSession, None]:
    """JWT primero; sub local y perfil bloqueado hasta commit/rollback.

    No JIT ni identidad del body/header tenant. La barrera DB vuelve a consultar
    autoridad; no reutiliza require_superadmin ni un flag cargado en otro pool.
    """
    if credentials is None:
        raise HTTPException(
            401, "No autenticado", headers={"WWW-Authenticate": "Bearer"}
        )
    auth_user_id = extract_auth_user_id(credentials.credentials)
    factory = get_eipd_admin_session_factory()
    async with factory() as db:
        try:
            try:
                await _prepare_channel(db)
                await db.execute(
                    text("SELECT set_config('request.jwt.claim.sub', :sub, true)"),
                    {"sub": str(auth_user_id)},
                )
                await authorize_eipd_personal_actor_v1(db)
            except DBAPIError as exc:
                if _sqlstate(exc) == "42501":
                    raise HTTPException(
                        403, "Requiere autoridad administrativa EIPD"
                    ) from None
                raise _unavailable() from None
            yield db
            await db.commit()
        except BaseException:
            await db.rollback()
            raise
