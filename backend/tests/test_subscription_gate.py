"""Tests del gate server-side de suscripción para módulos M2+."""

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.core.deps import require_active_subscription
from app.db.models import Profile, SubscriptionStatus

_ORG_ID = uuid.UUID("d0000000-0000-0000-0000-000000000001")
_PROFILE_ID = uuid.UUID("d0000000-0000-0000-0000-000000000002")
_AUTH_ID = uuid.UUID("d0000000-0000-0000-0000-000000000003")


def _profile(*, is_superadmin: bool = False) -> Profile:
    return Profile(
        id=_PROFILE_ID,
        auth_user_id=_AUTH_ID,
        email="subscription-gate-test@cumpleia.cl",
        is_superadmin=is_superadmin,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "subscription_status",
    [
        SubscriptionStatus.active,
        SubscriptionStatus.grace,
    ],
)
async def test_gate_permite_suscripcion_vigente(subscription_status):
    profile = _profile()
    db = AsyncMock()

    with (
        patch("app.core.deps.has_permission", new=AsyncMock(return_value=True)),
        patch(
            "app.core.deps.get_subscription_status",
            new=AsyncMock(return_value=subscription_status),
        ),
    ):
        result = await require_active_subscription(
            x_organization_id=_ORG_ID,
            current_profile=profile,
            db=db,
        )

    assert result is profile


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "subscription_status",
    [
        SubscriptionStatus.suspended,
        SubscriptionStatus.cancelled,
    ],
)
async def test_gate_bloquea_suscripcion_no_vigente(subscription_status):
    profile = _profile()
    db = AsyncMock()

    with (
        patch("app.core.deps.has_permission", new=AsyncMock(return_value=True)),
        patch(
            "app.core.deps.get_subscription_status",
            new=AsyncMock(return_value=subscription_status),
        ),
    ):
        with pytest.raises(HTTPException) as exc:
            await require_active_subscription(
                x_organization_id=_ORG_ID,
                current_profile=profile,
                db=db,
            )

    assert exc.value.status_code == 402
    assert exc.value.detail == "La organización requiere una suscripción activa"


@pytest.mark.asyncio
async def test_gate_superadmin_no_depende_de_suscripcion():
    profile = _profile(is_superadmin=True)
    db = AsyncMock()

    get_status = AsyncMock(side_effect=AssertionError("No debe consultar suscripción"))

    with (
        patch("app.core.deps.has_permission", new=AsyncMock()) as has_perm,
        patch("app.core.deps.get_subscription_status", new=get_status),
    ):
        result = await require_active_subscription(
            x_organization_id=_ORG_ID,
            current_profile=profile,
            db=db,
        )

    assert result is profile
    has_perm.assert_not_awaited()
    get_status.assert_not_awaited()


@pytest.mark.asyncio
async def test_gate_bloquea_organizacion_ajena_antes_de_consultar_suscripcion():
    profile = _profile()
    db = AsyncMock()

    get_status = AsyncMock(
        side_effect=AssertionError("No debe consultar una suscripción ajena")
    )

    with (
        patch(
            "app.core.deps.has_permission",
            new=AsyncMock(return_value=False),
        ),
        patch(
            "app.core.deps.get_subscription_status",
            new=get_status,
        ),
    ):
        with pytest.raises(HTTPException) as exc:
            await require_active_subscription(
                x_organization_id=_ORG_ID,
                current_profile=profile,
                db=db,
            )

    assert exc.value.status_code == 403
    get_status.assert_not_awaited()
