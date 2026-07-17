import uuid
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import extract_auth_user_id
from app.db.models import Membership, Profile
from app.db.session import get_db

_bearer = HTTPBearer()


async def get_current_profile(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer)],
    db: AsyncSession = Depends(get_db),
) -> Profile:
    auth_user_id = extract_auth_user_id(credentials.credentials)

    result = await db.execute(
        select(Profile).where(Profile.auth_user_id == auth_user_id)
    )
    profile = result.scalar_one_or_none()

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Perfil de usuario no encontrado",
        )
    return profile


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
