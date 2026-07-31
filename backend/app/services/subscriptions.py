"""Vigencia de acceso por organización.

Ver docs/adr/0001-modelo-organizaciones-roles-suscripcion.md. Toda
organización tiene exactamente una fila en `subscriptions` desde que se crea
(ver app/api/organizations.py y scripts/seed_dev.py; la migración 0004 hizo
el backfill de las que ya existían) — por eso `get_subscription_status` puede
asumir `scalar_one()` sin manejar un caso "no existe" que no puede ocurrir.
Todas nacen `active`: el cálculo real de vigencia según facturación es
trabajo futuro, pero la interfaz ya está definida.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Subscription, SubscriptionStatus


async def get_subscription_status(
    db: AsyncSession, organization_id: uuid.UUID
) -> SubscriptionStatus:
    return (
        await db.execute(
            select(Subscription.status).where(
                Subscription.organization_id == organization_id
            )
        )
    ).scalar_one()


def is_subscription_active(status: SubscriptionStatus) -> bool:
    return status in (SubscriptionStatus.active, SubscriptionStatus.grace)
