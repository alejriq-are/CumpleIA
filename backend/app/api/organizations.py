"""Onboarding de tenant: creación de una organización por autoservicio.

En Fase 0 el aprovisionamiento del perfil es automático (JIT en cada request),
pero la organización se crea de forma EXPLÍCITA: un usuario recién registrado
llama a `POST /organizations` y queda como `owner`. Así no se generan
organizaciones basura y el aislamiento multi-tenant se puede probar de punta a
punta (perfil → organización → membresía → acceso).

Fuera de alcance de Fase 0: el flujo de invitación (que un segundo usuario se
una a una organización existente). El modelo de datos ya lo soporta sin cambios
destructivos —`memberships` admite N perfiles por organización con distintos
roles (`owner`/`admin`/`editor`/`viewer`)—, de modo que añadir invitaciones más
adelante será solo lógica nueva, no una migración que rompa datos.
"""

import uuid

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentProfile
from app.db.models import Membership, Organization, UserRole
from app.db.session import get_db

router = APIRouter(prefix="/organizations", tags=["organizaciones"])


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    rut: str | None = None
    industry: str | None = None
    size: str | None = None


class OrganizationOut(BaseModel):
    id: uuid.UUID
    name: str
    role: UserRole  # rol del usuario actual en la organización recién creada


@router.post("", response_model=OrganizationOut, status_code=status.HTTP_201_CREATED)
async def create_organization(
    payload: OrganizationCreate,
    current_profile: CurrentProfile,
    db: AsyncSession = Depends(get_db),
) -> OrganizationOut:
    """Crea la organización y la membresía `owner` en una sola transacción.

    Ambos INSERT viven en la misma sesión y se confirman juntos al cerrar la
    request (`get_db` hace commit al final). Si cualquiera de los dos falla, el
    manejador de `get_db` hace rollback y no queda nada a medias: nunca una
    organización sin dueño ni una membresía huérfana.
    """
    org = Organization(
        name=payload.name,
        rut=payload.rut,
        industry=payload.industry,
        size=payload.size,
    )
    db.add(org)
    await db.flush()  # asigna org.id sin cerrar la transacción

    membership = Membership(
        organization_id=org.id,
        profile_id=current_profile.id,
        role=UserRole.owner,
    )
    db.add(membership)
    await db.flush()

    return OrganizationOut(id=org.id, name=org.name, role=membership.role)
