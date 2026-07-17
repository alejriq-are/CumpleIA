import uuid

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.deps import CurrentProfile, OrgMembership
from app.db.models import Membership, Profile, UserRole

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


@router.get("", response_model=ProfileOut)
async def get_me(current_profile: CurrentProfile) -> Profile:
    return current_profile


@router.get("/membership", response_model=MembershipOut)
async def get_my_membership(membership: OrgMembership) -> Membership:
    return membership
