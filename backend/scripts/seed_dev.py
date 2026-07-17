"""Seed de desarrollo: crea una organización y un usuario de prueba.

Uso:
    cd backend
    python -m scripts.seed_dev
"""

import asyncio
import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.db.models import Membership, Organization, Profile, UserRole

settings = get_settings()

# IDs fijos para dev (facilitan referencias en tests y consola)
DEV_ORG_ID = uuid.UUID("10000000-0000-0000-0000-000000000001")
DEV_PROFILE_ID = uuid.UUID("20000000-0000-0000-0000-000000000001")
DEV_AUTH_USER_ID = uuid.UUID("30000000-0000-0000-0000-000000000001")


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with SessionLocal() as session:
        # Idempotente: no duplicar si ya existe
        result = await session.execute(
            text("SELECT COUNT(*) FROM organizations WHERE id = :id"),
            {"id": str(DEV_ORG_ID)},
        )
        if result.scalar() > 0:
            print("El seed de desarrollo ya existe. Nada que hacer.")
            await engine.dispose()
            return

        org = Organization(
            id=DEV_ORG_ID,
            name="Organización Demo",
            rut="76.123.456-7",
            industry="Comercio",
            size="micro",
            plan="free",
        )
        session.add(org)

        profile = Profile(
            id=DEV_PROFILE_ID,
            auth_user_id=DEV_AUTH_USER_ID,
            email="dev@cumpleia.cl",
            full_name="Usuario Demo",
        )
        session.add(profile)

        await session.flush()

        membership = Membership(
            organization_id=org.id,
            profile_id=profile.id,
            role=UserRole.owner,
        )
        session.add(membership)
        await session.commit()

    print("Seed creado correctamente.")
    print(f"  Organización : {DEV_ORG_ID}  (Organización Demo)")
    print(f"  Perfil       : {DEV_PROFILE_ID}  (dev@cumpleia.cl)")
    print(f"  auth_user_id : {DEV_AUTH_USER_ID}  (fake, solo para dev local)")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
