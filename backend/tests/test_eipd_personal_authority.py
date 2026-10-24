"""Barrera personal DB real, sin publicacion ni activacion."""

import asyncio
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.services.eipd_policy_store import authorize_eipd_personal_actor_v1
from tests import test_eipd_policy_shared_lock as locks
from tests import test_rls_isolation_licitud as rls

app_role_session = rls.app_role_session


@pytest_asyncio.fixture
async def authority(_session_factory, _seed_test_data):
    actor, auth = uuid4(), uuid4()
    async with _session_factory() as db:
        await db.execute(
            text(
                "INSERT INTO profiles(id,auth_user_id,email,is_superadmin) VALUES (:id,:auth,:email,true)"
            ),
            dict(id=actor, auth=auth, email=str(auth) + "@example.org"),
        )
        await db.commit()
    yield actor, auth
    async with _session_factory() as db:
        await db.execute(text("DELETE FROM profiles WHERE id=:id"), dict(id=actor))
        await db.commit()


async def admin(db, auth):
    await db.execute(text("SET LOCAL ROLE eipd_policy_admin"))
    await rls._set_auth_user(db, auth)


@pytest.mark.parametrize("kind", ["anonymous", "unknown", "tenant"])
async def test_denied_without_global_authority(_session_factory, auth_a_id, kind):
    async with _session_factory() as db:
        await db.execute(text("SET LOCAL ROLE eipd_policy_admin"))
        if kind != "anonymous":
            await rls._set_auth_user(db, auth_a_id if kind == "tenant" else uuid4())
        with pytest.raises(DBAPIError):
            await authorize_eipd_personal_actor_v1(db)
        await db.rollback()


async def test_runtime_superadmin_still_has_wrong_channel(app_role_session, authority):
    await rls._set_auth_user(app_role_session, authority[1])
    with pytest.raises(PermissionError):
        await authorize_eipd_personal_actor_v1(app_role_session)
    with pytest.raises(DBAPIError):
        await app_role_session.scalar(
            text("SELECT public.lock_eipd_personal_authority_v1()")
        )
    await app_role_session.rollback()


async def test_derived_actor_and_safe_function(_session_factory, authority):
    async with _session_factory() as db:
        row = (
            await db.execute(
                text(
                    "SELECT prosecdef,proconfig,has_function_privilege('app_user','public.lock_eipd_personal_authority_v1()','EXECUTE'),has_table_privilege('eipd_policy_admin','profiles','UPDATE') FROM pg_proc WHERE oid='public.lock_eipd_personal_authority_v1()'::regprocedure"
                )
            )
        ).one()
        assert tuple(row) == (True, ["search_path=pg_catalog"], False, False)
        await admin(db, authority[1])
        assert await authorize_eipd_personal_actor_v1(db) == authority[0]
        await db.rollback()
        await db.execute(text("SET LOCAL ROLE eipd_policy_admin"))
        with pytest.raises(DBAPIError):
            await authorize_eipd_personal_actor_v1(
                db
            )  # Sub local no sobrevive rollback.
        await db.rollback()


@pytest.mark.parametrize("commit_change", [True, False])
async def test_revocation_before_authorization_reloads_after_wait(
    _session_factory, authority, commit_change
):
    async with _session_factory() as owner, _session_factory() as reader:
        await owner.execute(
            text("UPDATE profiles SET is_superadmin=false WHERE id=:id"),
            dict(id=authority[0]),
        )
        await admin(reader, authority[1])
        pid = await reader.scalar(text("SELECT pg_backend_pid()"))
        task = asyncio.create_task(authorize_eipd_personal_actor_v1(reader))
        try:
            await locks.blocked(owner, pid)
            if commit_change:
                await owner.commit()
                with pytest.raises(DBAPIError):
                    await asyncio.wait_for(task, 5)
            else:
                await owner.rollback()
                assert await asyncio.wait_for(task, 5) == authority[0]
        finally:
            await locks.stop(task)
            await reader.rollback()
            await owner.rollback()


@pytest.mark.parametrize("commit_actor", [True, False])
async def test_revocation_waits_authorized_transaction(
    _session_factory, authority, commit_actor
):
    async with _session_factory() as reader, _session_factory() as owner:
        await admin(reader, authority[1])
        assert await authorize_eipd_personal_actor_v1(reader) == authority[0]
        pid = await owner.scalar(text("SELECT pg_backend_pid()"))
        task = asyncio.create_task(
            owner.execute(
                text("UPDATE profiles SET is_superadmin=false WHERE id=:id"),
                dict(id=authority[0]),
            )
        )
        try:
            await locks.blocked(reader, pid)
            if commit_actor:
                await reader.commit()
            else:
                await reader.rollback()
            await asyncio.wait_for(task, 5)
            await owner.commit()
        finally:
            await locks.stop(task)
            await reader.rollback()
            await owner.rollback()
