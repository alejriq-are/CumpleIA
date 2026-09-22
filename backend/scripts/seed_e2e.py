"""Fixture local para pruebas E2E del frontend.

Crea o reutiliza:
- usuario real en Supabase Auth;
- organización E2E local;
- perfil vinculado al auth_user_id real;
- membresía owner;
- suscripción activa.

Las credenciales E2E se leen desde .env y nunca se guardan en Git.

Uso:
    cd ~/projects/CumpleIA/backend
    ../.venv/bin/python -m scripts.seed_e2e
"""

from __future__ import annotations

import asyncio
import json
import uuid
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.db.models import (
    Membership,
    Organization,
    Profile,
    Subscription,
    SubscriptionCommitmentType,
    SubscriptionStatus,
    UserRole,
)


_REPO_ROOT = Path(__file__).resolve().parents[2]
_ENV_FILE = _REPO_ROOT / ".env"

E2E_ORG_ID = uuid.UUID("11000000-0000-0000-0000-000000000001")
E2E_PROFILE_ID = uuid.UUID("21000000-0000-0000-0000-000000000001")


def _read_env_value(name: str) -> str:
    if not _ENV_FILE.exists():
        raise RuntimeError(f"No existe {_ENV_FILE}")

    for raw_line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        if key.strip() == name:
            value = value.strip()
            if value:
                return value

    raise RuntimeError(f"{name} no está configurada en {_ENV_FILE}")


def _supabase_request(
    method: str,
    path: str,
    *,
    service_role_key: str,
    body: dict | None = None,
) -> dict:
    settings = get_settings()
    url = f"{settings.supabase_url.rstrip('/')}{path}"

    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")

    request = Request(
        url,
        data=data,
        method=method,
        headers={
            "apikey": service_role_key,
            "Authorization": f"Bearer {service_role_key}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urlopen(request, timeout=30) as response:
            payload = response.read().decode("utf-8")
            return json.loads(payload) if payload else {}
    except HTTPError as exc:
        payload = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Supabase Auth respondió HTTP {exc.code}: {payload}"
        ) from exc


def _find_auth_user(email: str, service_role_key: str) -> dict | None:
    page = 1
    per_page = 100

    while True:
        query = urlencode({"page": page, "per_page": per_page})
        result = _supabase_request(
            "GET",
            f"/auth/v1/admin/users?{query}",
            service_role_key=service_role_key,
        )

        users = result.get("users", [])
        for user in users:
            if (user.get("email") or "").lower() == email.lower():
                return user

        if len(users) < per_page:
            return None

        page += 1


def _ensure_auth_user(email: str, password: str, service_role_key: str) -> uuid.UUID:
    existing = _find_auth_user(email, service_role_key)
    if existing is not None:
        return uuid.UUID(existing["id"])

    created = _supabase_request(
        "POST",
        "/auth/v1/admin/users",
        service_role_key=service_role_key,
        body={
            "email": email,
            "password": password,
            "email_confirm": True,
        },
    )

    user_id = created.get("id")
    if not user_id:
        raise RuntimeError("Supabase creó el usuario pero no devolvió su id")

    return uuid.UUID(user_id)


async def seed() -> None:
    settings = get_settings()

    if not settings.supabase_service_role_key:
        raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY no está configurada")

    email = _read_env_value("E2E_USER_EMAIL")
    password = _read_env_value("E2E_USER_PASSWORD")

    auth_user_id = _ensure_auth_user(
        email,
        password,
        settings.supabase_service_role_key,
    )

    engine = create_async_engine(settings.database_url, echo=False)
    SessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    try:
        async with SessionLocal() as session:
            org = await session.get(Organization, E2E_ORG_ID)
            if org is None:
                org = Organization(
                    id=E2E_ORG_ID,
                    name="Organización E2E RAT",
                    rut="76.999.999-9",
                    industry="Pruebas",
                    size="micro",
                    plan="free",
                )
                session.add(org)
            else:
                org.name = "Organización E2E RAT"

            profile_result = await session.execute(
                select(Profile).where(Profile.auth_user_id == auth_user_id)
            )
            profile = profile_result.scalar_one_or_none()

            if profile is None:
                profile = await session.get(Profile, E2E_PROFILE_ID)

                if profile is None:
                    profile = Profile(
                        id=E2E_PROFILE_ID,
                        auth_user_id=auth_user_id,
                        email=email,
                        full_name="Usuario E2E RAT",
                    )
                    session.add(profile)
                else:
                    profile.auth_user_id = auth_user_id
                    profile.email = email
                    profile.full_name = "Usuario E2E RAT"
            else:
                profile.email = email
                profile.full_name = "Usuario E2E RAT"

            await session.flush()

            membership_result = await session.execute(
                select(Membership).where(
                    Membership.organization_id == E2E_ORG_ID,
                    Membership.profile_id == profile.id,
                )
            )
            membership = membership_result.scalar_one_or_none()

            if membership is None:
                session.add(
                    Membership(
                        organization_id=E2E_ORG_ID,
                        profile_id=profile.id,
                        role=UserRole.owner,
                    )
                )
            else:
                membership.role = UserRole.owner

            subscription_result = await session.execute(
                select(Subscription).where(
                    Subscription.organization_id == E2E_ORG_ID
                )
            )
            subscription = subscription_result.scalar_one_or_none()

            if subscription is None:
                session.add(
                    Subscription(
                        organization_id=E2E_ORG_ID,
                        commitment_type=SubscriptionCommitmentType.monthly,
                        status=SubscriptionStatus.active,
                        created_by=profile.id,
                        updated_by=profile.id,
                    )
                )
            else:
                subscription.status = SubscriptionStatus.active
                subscription.commitment_type = SubscriptionCommitmentType.monthly
                subscription.updated_by = profile.id

            await session.commit()

        print("Fixture E2E listo.")
        print(f"  Organización : {E2E_ORG_ID}")
        print(f"  Perfil       : {profile.id}")
        print(f"  Auth user    : {auth_user_id}")
        print("  Rol          : owner")
        print("  Suscripción  : active")
        print("  Credenciales : cargadas desde .env")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
