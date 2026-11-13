"""Resolver compartido con app_user, bloqueo PostgreSQL real y cero activacion."""

import asyncio
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.services.eipd_policy import resolve_eipd_gate_policy_v1
from app.services.eipd_policy_store import (
    resolve_eipd_policy_snapshot_for_transaction_v1,
)
from tests import test_rls_isolation_licitud as rls
from tests import test_services_eipd_policy_store as store

app_role_session = rls.app_role_session
store_state = store.store_state
cleanup_store_controls = store.cleanup_store_controls


async def blocked(holder, pid):
    async def wait():
        while not await holder.scalar(
            text("SELECT pg_blocking_pids(:pid)"), dict(pid=pid)
        ):
            await asyncio.sleep(0.02)

    await asyncio.wait_for(wait(), 5)


async def stop(task):
    if not task.done():
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


async def test_function_security_and_runtime_privileges(app_role_session):
    row = (
        await app_role_session.execute(
            text(
                """SELECT prosecdef,proconfig,
      has_function_privilege('app_user','public.lock_eipd_policy_selector_v1()','EXECUTE'),
      has_function_privilege('eipd_policy_admin','public.lock_eipd_policy_selector_v1()','EXECUTE'),
      has_table_privilege('app_user','eipd_policy_selector','UPDATE'),
      (SELECT rolbypassrls FROM pg_roles WHERE rolname='app_user')
      FROM pg_proc WHERE oid='public.lock_eipd_policy_selector_v1()'::regprocedure"""
            )
        )
    ).one()
    assert tuple(row) == (True, ["search_path=pg_catalog"], True, False, False, False)


@pytest.mark.parametrize("actor", ["anonymous", "unknown"])
async def test_unregistered_auth_cannot_lock(app_role_session, store_state, actor):
    await app_role_session.execute(
        text("SELECT set_config('request.jwt.claim.sub',:sub,true)"),
        dict(sub="" if actor == "anonymous" else str(uuid4())),
    )
    with pytest.raises(DBAPIError):
        await resolve_eipd_policy_snapshot_for_transaction_v1(app_role_session)
    await app_role_session.rollback()


async def test_missing_selector_fails_closed(app_role_session, auth_a_id):
    await rls._set_auth_user(app_role_session, auth_a_id)
    with pytest.raises(ValueError, match="no disponible"):
        await resolve_eipd_policy_snapshot_for_transaction_v1(app_role_session)
    await app_role_session.rollback()
    assert resolve_eipd_gate_policy_v1().activation == "deshabilitada"


@pytest.mark.parametrize("isolation", ["REPEATABLE READ", "SERIALIZABLE"])
async def test_other_isolation_rejected(
    app_role_session, store_state, auth_a_id, isolation
):
    await app_role_session.execute(text(f"SET TRANSACTION ISOLATION LEVEL {isolation}"))
    await rls._set_auth_user(app_role_session, auth_a_id)
    with pytest.raises(ValueError, match="READ COMMITTED"):
        await resolve_eipd_policy_snapshot_for_transaction_v1(app_role_session)
    await app_role_session.rollback()


async def test_two_tenants_can_hold_shared_lock(
    _app_session_factory, store_state, auth_a_id, auth_b_id
):
    async with _app_session_factory() as first, _app_session_factory() as second:
        await rls._set_auth_user(first, auth_a_id)
        await rls._set_auth_user(second, auth_b_id)
        one = await resolve_eipd_policy_snapshot_for_transaction_v1(first)
        two = await asyncio.wait_for(
            resolve_eipd_policy_snapshot_for_transaction_v1(second), 5
        )
        assert one == two and one.selector.revision == 1
        await first.rollback()
        await second.rollback()


@pytest.mark.parametrize("commit_reader", [True, False])
async def test_admin_waits_until_reader_transaction_finishes(
    _session_factory,
    _app_session_factory,
    store_state,
    profile_a_id,
    auth_a_id,
    commit_reader,
):
    async with _session_factory() as preparer:
        await preparer.execute(text("SET LOCAL ROLE eipd_policy_admin"))
        pub = await store.publish(preparer, profile_a_id)
        await preparer.commit()
    async with _app_session_factory() as reader, _session_factory() as admin:
        await rls._set_auth_user(reader, auth_a_id)
        before = await resolve_eipd_policy_snapshot_for_transaction_v1(reader)
        await admin.execute(text("SET LOCAL ROLE eipd_policy_admin"))
        pid = await admin.scalar(text("SELECT pg_backend_pid()"))
        task = asyncio.create_task(store.choose(admin, profile_a_id, pub, 1))
        try:
            await blocked(reader, pid)
            assert not task.done()
            again = await resolve_eipd_policy_snapshot_for_transaction_v1(reader)
            assert again == before
            if commit_reader:
                await reader.commit()
            else:
                await reader.rollback()
            plan = await asyncio.wait_for(task, 5)
            assert plan.selector.revision == 2
            await admin.commit()
        finally:
            await stop(task)
            await reader.rollback()
            await admin.rollback()


@pytest.mark.parametrize("commit_admin", [True, False])
@pytest.mark.parametrize("bootstrap", [False, True])
async def test_reader_waits_for_admin_and_reloads_current_selection(
    _session_factory,
    _app_session_factory,
    store_state,
    profile_a_id,
    auth_a_id,
    commit_admin,
    bootstrap,
):
    if bootstrap:
        async with _session_factory() as db:
            await db.execute(text("DELETE FROM eipd_policy_selector WHERE id=1"))
            await db.execute(
                text("DELETE FROM eipd_policy_selections WHERE id=:id"),
                dict(id=store_state[1].event.id),
            )
            await db.commit()
    revision = 0 if bootstrap else 1
    async with _session_factory() as preparer:
        await preparer.execute(text("SET LOCAL ROLE eipd_policy_admin"))
        pub = await store.publish(preparer, profile_a_id)
        await preparer.commit()
    async with _session_factory() as admin, _app_session_factory() as reader:
        await admin.execute(text("SET LOCAL ROLE eipd_policy_admin"))
        await store.choose(admin, profile_a_id, pub, revision)
        await rls._set_auth_user(reader, auth_a_id)
        pid = await reader.scalar(text("SELECT pg_backend_pid()"))
        task = asyncio.create_task(
            resolve_eipd_policy_snapshot_for_transaction_v1(reader)
        )
        try:
            await blocked(admin, pid)
            assert not task.done()
            if commit_admin:
                await admin.commit()
            else:
                await admin.rollback()
            if bootstrap and not commit_admin:
                with pytest.raises(ValueError, match="no disponible"):
                    await asyncio.wait_for(task, 5)
            else:
                state = await asyncio.wait_for(task, 5)
                assert state.selector.revision == revision + int(commit_admin)
                assert state.selector.publication_id == (
                    pub.id if commit_admin else store_state[0].id
                )
                assert len(state.selections) == state.selector.revision
            await reader.rollback()
        finally:
            await stop(task)
            await admin.rollback()
            await reader.rollback()


@pytest.mark.parametrize("mode", ["hash", "extra"])
async def test_locked_resolver_rejects_corrupted_fixture_without_fallback(
    _session_factory,
    app_role_session,
    store_state,
    auth_a_id,
    mode,
):
    async with _session_factory() as owner:
        row = store_state[0]
        payload = row.policy.model_dump(mode="json")
        if mode == "hash":
            payload["acceptance_reference"] = "TEST: alterada"
        else:
            payload["approved"] = True
        import json

        await owner.execute(
            text(
                "UPDATE eipd_policy_publications SET payload=CAST(:payload AS jsonb) WHERE id=:id"
            ),
            dict(payload=json.dumps(payload), id=row.id),
        )
        await owner.commit()
    await rls._set_auth_user(app_role_session, auth_a_id)
    with pytest.raises(ValueError):
        await resolve_eipd_policy_snapshot_for_transaction_v1(app_role_session)
    await app_role_session.rollback()
    async with _session_factory() as owner:
        assert (
            await owner.scalar(text("SELECT count(*) FROM eipd_policy_selections")) == 1
        )
    assert resolve_eipd_gate_policy_v1().activation == "deshabilitada"
