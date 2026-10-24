"""Ensayo de ciclo de vida sobre login temporal; solo base aislada via runner."""

from uuid import uuid4

import asyncpg
import pytest
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from app.db.eipd_admin import _prepare_channel
from app.services.eipd_policy_store import read_eipd_policy_audit_snapshot_v1
from tests import test_eipd_admin_channel as pools

dedicated = pools.dedicated

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def snapshot(factory):
    async with factory() as db:
        return await read_eipd_policy_audit_snapshot_v1(db)


async def rejected_connection(url, error, code):
    engine = create_async_engine(
        url, poolclass=NullPool, echo=False, hide_parameters=True
    )
    try:
        with pytest.raises(error) as failure:
            async with engine.connect():
                pytest.fail("Credencial retirada abrio conexion")
        assert failure.value.sqlstate == code
    finally:
        await engine.dispose()


async def test_password_rotation_requires_recycling_existing_connections(
    dedicated, _session_factory
):
    factory, role = dedicated
    engine = factory.kw["bind"]
    old_url = engine.url
    new_password = uuid4().hex
    before = await snapshot(_session_factory)
    async with factory() as db:
        old_pid = await db.scalar(text("SELECT pg_backend_pid()"))
        await db.rollback()
        async with _session_factory() as maintenance:
            await maintenance.execute(
                text(f"ALTER ROLE {role} PASSWORD '{new_password}'")
            )
            await maintenance.commit()
        # ALTER PASSWORD no invalida una conexion ya autenticada.
        assert await db.scalar(text("SELECT pg_backend_pid()")) == old_pid
        await _prepare_channel(db)
        await db.rollback()
        await rejected_connection(old_url, asyncpg.InvalidPasswordError, "28P01")
    await engine.dispose()
    await rejected_connection(old_url, asyncpg.InvalidPasswordError, "28P01")
    replacement = create_async_engine(
        old_url.set(password=new_password),
        poolclass=NullPool,
        echo=False,
        hide_parameters=True,
    )
    try:
        async with AsyncSession(replacement) as db:
            await _prepare_channel(db)
            assert await db.scalar(text("SELECT current_user")) == "eipd_policy_admin"
            await db.rollback()
            assert await db.scalar(text("SELECT current_user")) == role
            assert not await db.scalar(
                text("SELECT NULLIF(current_setting('request.jwt.claim.sub',true),'')")
            )
            await db.rollback()
    finally:
        await replacement.dispose()
    assert await snapshot(_session_factory) == before


async def test_nologin_blocks_new_connections_and_channel_guard_then_recovers(
    dedicated, _session_factory
):
    factory, role = dedicated
    url = factory.kw["bind"].url
    before = await snapshot(_session_factory)
    try:
        async with factory() as db:
            pid = await db.scalar(text("SELECT pg_backend_pid()"))
            await db.rollback()
            async with _session_factory() as maintenance:
                await maintenance.execute(text(f"ALTER ROLE {role} NOLOGIN"))
                await maintenance.commit()
            # NOLOGIN no termina la sesion existente; la guarda de app la rechaza.
            assert await db.scalar(text("SELECT pg_backend_pid()")) == pid
            with pytest.raises(HTTPException) as failure:
                await _prepare_channel(db)
            assert failure.value.status_code == 503
            await db.rollback()
            await rejected_connection(
                url, asyncpg.InvalidAuthorizationSpecificationError, "28000"
            )
    finally:
        async with _session_factory() as maintenance:
            await maintenance.execute(text(f"ALTER ROLE {role} LOGIN"))
            await maintenance.commit()
    await factory.kw["bind"].dispose()
    async with factory() as db:
        await _prepare_channel(db)
        await db.rollback()
    assert await snapshot(_session_factory) == before


async def test_membership_retirement_rejects_warm_connection_then_recovers(
    dedicated, _session_factory
):
    factory, role = dedicated
    before = await snapshot(_session_factory)
    try:
        async with factory() as db:
            await _prepare_channel(db)
            await db.rollback()
            async with _session_factory() as maintenance:
                await maintenance.execute(text(f"REVOKE eipd_policy_admin FROM {role}"))
                await maintenance.commit()
            with pytest.raises(HTTPException) as failure:
                await _prepare_channel(db)
            assert failure.value.status_code == 503
            await db.rollback()
    finally:
        async with _session_factory() as maintenance:
            await maintenance.execute(text(f"GRANT eipd_policy_admin TO {role}"))
            await maintenance.commit()
    async with factory() as db:
        await _prepare_channel(db)
        await db.rollback()
    assert await snapshot(_session_factory) == before
