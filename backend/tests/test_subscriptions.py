"""Tests de app/services/subscriptions.py (ADR 0001).

Lógica de negocio (qué status representa vigencia), no la política RLS de la
tabla `subscriptions` — eso vive en test_rls_isolation_subscriptions.py. Corre
contra el rol admin (`_session_factory`), igual que el resto de los tests de
servicio (p. ej. test_authorization.py).
"""

import uuid

import pytest
import pytest_asyncio
from sqlalchemy import delete

from app.db.models import (
    Membership,
    Organization,
    Subscription,
    SubscriptionCommitmentType,
    SubscriptionStatus,
)
from app.services.subscriptions import get_subscription_status, is_subscription_active

_ORG_ID = uuid.UUID("c0000000-0000-0000-0000-000000000001")


@pytest_asyncio.fixture
async def organizacion_con_suscripcion(_session_factory):
    async with _session_factory() as session:
        session.add(Organization(id=_ORG_ID, name="Organización suscripción (test)"))
        await session.flush()
        session.add(
            Subscription(
                organization_id=_ORG_ID,
                commitment_type=SubscriptionCommitmentType.monthly,
                status=SubscriptionStatus.grace,
            )
        )
        await session.commit()

    yield _ORG_ID

    async with _session_factory() as session:
        await session.execute(
            delete(Membership).where(Membership.organization_id == _ORG_ID)
        )
        await session.execute(
            delete(Subscription).where(Subscription.organization_id == _ORG_ID)
        )
        await session.execute(delete(Organization).where(Organization.id == _ORG_ID))
        await session.commit()


@pytest.mark.asyncio
async def test_get_subscription_status_lee_el_status_real(
    _session_factory, organizacion_con_suscripcion
):
    async with _session_factory() as session:
        status = await get_subscription_status(session, organizacion_con_suscripcion)
    assert status == SubscriptionStatus.grace


@pytest.mark.asyncio
async def test_toda_organizacion_de_test_tiene_suscripcion_active(
    _session_factory, org_a_id, _seed_test_data
):
    """org_a_id la crea `_seed_test_data` (conftest.py) junto con su
    Subscription, igual que el flujo real de `POST /organizations` — si esto
    falla, el invariante "toda organización tiene una fila de suscripción"
    se rompió en alguno de los puntos de creación (ver ADR 0001)."""
    async with _session_factory() as session:
        status = await get_subscription_status(session, org_a_id)
    assert status == SubscriptionStatus.active


@pytest.mark.parametrize(
    ("status", "esperado"),
    [
        (SubscriptionStatus.active, True),
        (SubscriptionStatus.grace, True),
        (SubscriptionStatus.suspended, False),
        (SubscriptionStatus.cancelled, False),
    ],
)
def test_is_subscription_active(status, esperado):
    assert is_subscription_active(status) is esperado
