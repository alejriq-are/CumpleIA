"""General EIPD registered history, separate from mutable draft endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_active_subscription, require_permission
from app.db.models import Profile
from app.db.session import get_db
from app.schemas.eipd_document_versions import EipdVersionRegister
from app.services import eipd_document_versions as service
from app.services.authorization import Permission

router = APIRouter(
    prefix="/licitud/treatments/{treatment_id}/assessments/{assessment_id}/eipd-versions/v1",
    tags=["licitud"],
    dependencies=[Depends(require_active_subscription)],
)


@router.get("/preview")
async def preview(
    treatment_id: UUID,
    assessment_id: UUID,
    x_organization_id: Annotated[UUID, Header()],
    profile: Profile = Depends(require_permission(Permission.view_content)),
    db: AsyncSession = Depends(get_db),
):
    return await service.preview(db, x_organization_id, treatment_id, assessment_id)


@router.post("", status_code=201)
async def register(
    treatment_id: UUID,
    assessment_id: UUID,
    payload: EipdVersionRegister,
    x_organization_id: Annotated[UUID, Header()],
    profile: Profile = Depends(require_permission(Permission.register_document)),
    db: AsyncSession = Depends(get_db),
):
    return await service.register(
        db, x_organization_id, treatment_id, assessment_id, profile.id, payload
    )


@router.get("")
async def history(
    treatment_id: UUID,
    assessment_id: UUID,
    x_organization_id: Annotated[UUID, Header()],
    profile: Profile = Depends(require_permission(Permission.view_content)),
    db: AsyncSession = Depends(get_db),
):
    rows = await service.history(db, x_organization_id, treatment_id, assessment_id)
    return [
        dict(
            id=str(r.id),
            version=r.version,
            created_at=r.created_at.isoformat(),
            reason=r.reason,
            bundle_hash=r.bundle_hash,
        )
        for r in rows
    ]


@router.get("/requests/{request_id}")
async def lookup(
    treatment_id: UUID,
    assessment_id: UUID,
    request_id: UUID,
    x_organization_id: Annotated[UUID, Header()],
    profile: Profile = Depends(require_permission(Permission.view_content)),
    db: AsyncSession = Depends(get_db),
):
    return await service.lookup(
        db, x_organization_id, treatment_id, assessment_id, request_id, profile.id
    )


@router.get("/{version_id}")
async def detail(
    treatment_id: UUID,
    assessment_id: UUID,
    version_id: UUID,
    x_organization_id: Annotated[UUID, Header()],
    profile: Profile = Depends(require_permission(Permission.view_content)),
    db: AsyncSession = Depends(get_db),
):
    rows = await service.history(db, x_organization_id, treatment_id, assessment_id)
    row = next((r for r in rows if r.id == version_id), None)
    if row is None:
        raise HTTPException(404, detail="Versión documental no encontrada")
    return service.output(row)
