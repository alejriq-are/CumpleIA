import uuid
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import extract_auth_identity
from app.db.models import Membership, Profile
from app.db.session import get_db

# auto_error=False: si falta el header Authorization NO lanzamos 403 automático;
# lo gestionamos abajo para devolver 401 (semántica HTTP correcta).
_bearer = HTTPBearer(auto_error=False)


async def get_current_profile(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    db: AsyncSession = Depends(get_db),
) -> Profile:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    identity = extract_auth_identity(credentials.credentials)

    # Puebla auth.uid() para esta transacción: las políticas RLS (ver migración
    # 0001) filtran por `auth_org_ids()`, que a su vez lee auth.uid(). Sin esto
    # el backend consultaría siempre como "usuario NULL" y RLS bloquearía todo
    # (o, si el rol de conexión tuviera BYPASSRLS, no filtraría nada — de ahí
    # que el runtime deba usar `app_user`, ver app/db/session.py).
    # `is_local=true` (tercer argumento de set_config) lo limita a la
    # transacción actual: al hacer commit/rollback en get_db() el valor se
    # descarta y no se filtra a la siguiente petición que reutilice la conexión
    # del pool.
    await db.execute(
        text("SELECT set_config('request.jwt.claim.sub', :sub, true)"),
        {"sub": str(identity.auth_user_id)},
    )

    # Aprovisionamiento JIT: en el primer acceso de un usuario de Supabase aún no
    # existe su fila en `profiles`. Se crea aquí a partir de los claims validados
    # del JWT. La ausencia de perfil NO es un fallo de autenticación (el token es
    # válido); por eso ya no se devuelve 401: simplemente se crea el perfil.
    #
    # Idempotente y seguro ante concurrencia: INSERT ... ON CONFLICT DO NOTHING
    # sobre `auth_user_id` (índice único). Dos peticiones simultáneas del mismo
    # usuario recién logueado no duplican filas ni fallan por carrera. Se hace
    # INSERT-luego-SELECT (nunca SELECT-luego-INSERT, que sí tendría carrera).
    #
    # `email` es NOT NULL; los tokens de Supabase siempre lo traen, pero se deja
    # un valor derivado del `sub` como red de seguridad si faltara.
    email = identity.email or f"{identity.auth_user_id}@sin-email.local"
    await db.execute(
        pg_insert(Profile)
        .values(
            auth_user_id=identity.auth_user_id,
            email=email,
            full_name=identity.full_name,
        )
        .on_conflict_do_nothing(index_elements=["auth_user_id"])
    )

    result = await db.execute(
        select(Profile).where(Profile.auth_user_id == identity.auth_user_id)
    )
    return result.scalar_one()


async def get_org_membership(
    x_organization_id: Annotated[uuid.UUID, Header()],
    current_profile: Profile = Depends(get_current_profile),
    db: AsyncSession = Depends(get_db),
) -> Membership:
    """Verifica que el usuario autenticado sea miembro de la organización indicada.

    El organization_id llega en el header X-Organization-Id pero NUNCA se confía
    directamente: se valida contra la tabla memberships en cada request.
    """
    result = await db.execute(
        select(Membership).where(
            Membership.organization_id == x_organization_id,
            Membership.profile_id == current_profile.id,
        )
    )
    membership = result.scalar_one_or_none()

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sin acceso a esta organización",
        )
    return membership


# Tipos anotados para inyección en endpoints
CurrentProfile = Annotated[Profile, Depends(get_current_profile)]
OrgMembership = Annotated[Membership, Depends(get_org_membership)]
