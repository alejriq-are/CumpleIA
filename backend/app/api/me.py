import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentProfile, OrgMembership
from app.db.models import Membership, Organization, Profile, UserRole
from app.db.session import get_db

router = APIRouter(prefix="/me", tags=["usuario"])


class ProfileOut(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str | None

    model_config = {"from_attributes": True}


class MembershipOut(BaseModel):
    organization_id: uuid.UUID
    role: UserRole

    model_config = {"from_attributes": True}


class OrganizationMembershipOut(BaseModel):
    id: uuid.UUID  # id de la organización
    name: str
    role: UserRole  # rol del usuario autenticado en esa organización


@router.get("", response_model=ProfileOut)
async def get_me(current_profile: CurrentProfile) -> Profile:
    return current_profile


@router.get("/organizations", response_model=list[OrganizationMembershipOut])
async def get_my_organizations(
    current_profile: CurrentProfile,
    db: AsyncSession = Depends(get_db),
) -> list[OrganizationMembershipOut]:
    """Organizaciones a las que pertenece el usuario, con su rol en cada una.

    No requiere la cabecera X-Organization-Id: es la vía para que el frontend
    descubra a qué organizaciones tiene acceso (p. ej. al completar el
    onboarding). Devuelve `[]` con 200 si aún no pertenece a ninguna.

    Solo se listan organizaciones con membresía del usuario: el JOIN por
    `profile_id` garantiza que nunca se filtren organizaciones ajenas.
    """
    result = await db.execute(
        select(Organization.id, Organization.name, Membership.role)
        .join(Membership, Membership.organization_id == Organization.id)
        .where(Membership.profile_id == current_profile.id)
        .order_by(Organization.name)
    )
    return [
        OrganizationMembershipOut(id=row.id, name=row.name, role=row.role)
        for row in result.all()
    ]


@router.get("/membership", response_model=MembershipOut)
async def get_my_membership(membership: OrgMembership) -> Membership:
    return membership
