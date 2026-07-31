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
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentProfile
from app.db.models import (
    Membership,
    Organization,
    Subscription,
    SubscriptionCommitmentType,
    SubscriptionStatus,
    UserRole,
)
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
    """Crea la organización, la membresía `owner` y su suscripción en una sola
    transacción.

    Los tres INSERT viven en la misma sesión y se confirman juntos al cerrar
    la request (`get_db` hace commit al final). Si cualquiera falla, el
    manejador de `get_db` hace rollback y no queda nada a medias: nunca una
    organización sin dueño, sin suscripción, ni una membresía huérfana. La
    suscripción nace `active`/`monthly` (ver
    docs/adr/0001-modelo-organizaciones-roles-suscripcion.md y
    app/services/subscriptions.py): toda organización debe tener exactamente
    una fila en `subscriptions` desde que existe.

    IDs generados en Python (no vía DEFAULT de Postgres) e INSERTs sin
    RETURNING a propósito: con RETURNING, Postgres reevalúa la política de
    SELECT (`org_visibility`/visibilidad de memberships) sobre la fila recién
    insertada, y en ese instante la membership `owner` todavía no existe
    (huevo y gallina) → RLS la rechaza aunque el INSERT en sí sea legítimo.
    Insertando sin RETURNING evitamos esa reevaluación; el SELECT de vuelta se
    hace después, cuando la membership ya existe dentro de la misma
    transacción y la política de visibilidad la deja pasar.
    """
    org_id = uuid.uuid4()
    membership_id = uuid.uuid4()
    subscription_id = uuid.uuid4()

    await db.execute(
        insert(Organization).values(
            id=org_id,
            name=payload.name,
            rut=payload.rut,
            industry=payload.industry,
            size=payload.size,
        )
    )
    await db.execute(
        insert(Membership).values(
            id=membership_id,
            organization_id=org_id,
            profile_id=current_profile.id,
            role=UserRole.owner,
        )
    )
    await db.execute(
        insert(Subscription).values(
            id=subscription_id,
            organization_id=org_id,
            commitment_type=SubscriptionCommitmentType.monthly,
            status=SubscriptionStatus.active,
            created_by=current_profile.id,
            updated_by=current_profile.id,
        )
    )

    org = (
        await db.execute(select(Organization).where(Organization.id == org_id))
    ).scalar_one()
    membership = (
        await db.execute(select(Membership).where(Membership.id == membership_id))
    ).scalar_one()

    return OrganizationOut(id=org.id, name=org.name, role=membership.role)
