"""Servicios de control global deshabilitado con PostgreSQL real."""

import asyncio
from copy import deepcopy
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import event, text

from app.db.models import EipdPolicyPublication
from app.services.eipd_policy import resolve_eipd_gate_policy_v1
from app.services.eipd_policy_store import (
    publish_eipd_policy_v1,
    read_eipd_policy_audit_snapshot_v1,
    read_selected_eipd_policy_v1,
    select_eipd_policy_v1,
)
from tests import test_rls_isolation_licitud as rls
from tests import test_services_eipd_policy as policy_fixtures

app_role_session = rls.app_role_session
policy = policy_fixtures.policy


def disabled():
    value = resolve_eipd_gate_policy_v1().model_dump(mode="python")
    value["policy_reference"] = "TEST: " + str(uuid4())
    return value


async def publish(db, actor, value=None):
    return await publish_eipd_policy_v1(
        db,
        value or disabled(),
        actor_id=actor,
        rationale="TEST: publicacion",
        evidence_reference="TEST",
    )


async def choose(db, actor, pub, revision):
    return await select_eipd_policy_v1(
        db,
        dict(publication_id=pub.id, expected_revision=revision),
        actor_id=actor,
        rationale="TEST: seleccion",
        evidence_reference="TEST",
    )


@pytest_asyncio.fixture(autouse=True)
async def cleanup_store_controls(_session_factory, _seed_test_data, profile_a_id):
    yield
    async with _session_factory() as db:
        params = {"actor": profile_a_id}
        pubids = "SELECT id FROM eipd_policy_publications WHERE created_by=:actor AND policy_reference LIKE 'TEST:%'"
        await db.execute(
            text(
                f"DELETE FROM eipd_policy_selector WHERE publication_id IN ({pubids})"
            ),
            params,
        )
        await db.execute(
            text(
                f"DELETE FROM eipd_policy_selections WHERE publication_id IN ({pubids})"
            ),
            params,
        )
        await db.execute(
            text(
                "DELETE FROM eipd_policy_publications WHERE created_by=:actor AND policy_reference LIKE 'TEST:%'"
            ),
            params,
        )
        await db.commit()


@pytest_asyncio.fixture
async def store_state(_session_factory, _seed_test_data, profile_a_id):
    async with _session_factory() as db:
        await db.execute(text("SET LOCAL ROLE eipd_policy_admin"))
        assert (await read_eipd_policy_audit_snapshot_v1(db)).selector is None
        pub = await publish(db, profile_a_id)
        plan = await choose(db, profile_a_id, pub, 0)
        await db.commit()
    yield pub, plan
    # _seed_test_data limpia solo controles TEST de actores sinteticos.


async def test_publish_without_select_and_bootstrap(
    _session_factory, _seed_test_data, profile_a_id
):
    before = disabled()
    copy = deepcopy(before)
    async with _session_factory() as db:
        await db.execute(text("SET LOCAL ROLE eipd_policy_admin"))
        pub = await publish(db, profile_a_id, before)
        assert before == copy and pub.created_by == profile_a_id
        assert pub.created_at.tzinfo is not None
        state = await read_eipd_policy_audit_snapshot_v1(db)
        assert state.selector is None and len(state.publications) == 1
        with pytest.raises(ValueError):
            await read_selected_eipd_policy_v1(db)
        plan = await choose(db, profile_a_id, pub, 0)
        assert plan.selector.revision == 1
        await db.commit()
    assert resolve_eipd_gate_policy_v1().activation == "deshabilitada"


@pytest.mark.parametrize("operation", ["publish", "select"])
@pytest.mark.parametrize("role", ["owner", "runtime"])
async def test_only_separate_admin_channel_can_write(
    _session_factory, app_role_session, store_state, profile_a_id, operation, role
):
    pub, _ = store_state
    async with _session_factory() as owner:
        db = owner if role == "owner" else app_role_session
        with pytest.raises(PermissionError):
            if operation == "publish":
                await publish(db, profile_a_id)
            else:
                await choose(db, profile_a_id, pub, 1)
        await db.rollback()


@pytest.mark.parametrize("authenticated", [False, True])
async def test_selected_read_single_sql_and_no_write(
    app_role_session, store_state, auth_a_id, _app_engine, authenticated
):
    pub, _ = store_state
    if authenticated:
        await rls._set_auth_user(app_role_session, auth_a_id)
    queries = []
    # Esta fixture runtime usa su propio engine; escuchar bind de su sesion.
    engine = app_role_session.bind.sync_engine

    def record(_conn, _cursor, statement, _parameters, _context, _many):
        queries.append(statement)

    event.listen(engine, "before_cursor_execute", record)
    try:
        if authenticated:
            selected = await read_selected_eipd_policy_v1(app_role_session)
            assert selected.id == pub.id
        else:
            with pytest.raises(ValueError):
                await read_selected_eipd_policy_v1(app_role_session)
    finally:
        event.remove(engine, "before_cursor_execute", record)
    assert len(queries) == 1 and queries[0].lstrip().startswith("SELECT")


@pytest.mark.parametrize(
    "mode",
    [
        "extra",
        "bool",
        "missing_target",
        "stale",
        "reuse",
        "duplicate_reference",
        "enabled",
    ],
)
async def test_bad_admin_input_preserves_state(
    _session_factory, store_state, profile_a_id, policy, mode
):
    pub, _ = store_state
    async with _session_factory() as db:
        await db.execute(text("SET LOCAL ROLE eipd_policy_admin"))
        before = await read_eipd_policy_audit_snapshot_v1(db)
        with pytest.raises(ValueError):
            if mode == "duplicate_reference":
                await publish(db, profile_a_id, pub.policy)
            elif mode == "enabled":
                await publish(db, profile_a_id, policy)
            else:
                request = dict(publication_id=pub.id, expected_revision=1)
                if mode == "extra":
                    request["actor_id"] = profile_a_id
                elif mode == "bool":
                    request["expected_revision"] = True
                elif mode == "missing_target":
                    request["publication_id"] = uuid4()
                elif mode == "stale":
                    request["expected_revision"] = 0
                await select_eipd_policy_v1(
                    db,
                    request,
                    actor_id=profile_a_id,
                    rationale="TEST",
                    evidence_reference="TEST",
                )
        after = await read_eipd_policy_audit_snapshot_v1(db)
        assert after == before
        await db.rollback()


@pytest.mark.parametrize(
    "mode", ["hash", "payload_extra", "payload_version", "time", "selector_missing"]
)
async def test_read_rejects_corrupted_owner_fixture(
    _session_factory, store_state, mode
):
    pub, _ = store_state
    async with _session_factory() as db:
        row = await db.get(EipdPolicyPublication, pub.id)
        if mode == "hash":
            # No cambiar FK hash: payload semanticamente alterado conserva hash SQL.
            payload = deepcopy(row.payload)
            payload["acceptance_reference"] = "alterada"
            row.payload = payload
        elif mode == "payload_extra":
            row.payload = dict(row.payload, approved=True)
        elif mode == "payload_version":
            row.payload = dict(row.payload, routes=["desconocida"])
        elif mode == "time":
            from datetime import timedelta

            row.created_at = row.created_at + timedelta(days=1)
        else:
            await db.execute(text("DELETE FROM eipd_policy_selector WHERE id=1"))
        await db.flush()
        with pytest.raises(ValueError):
            await read_selected_eipd_policy_v1(db)
        await db.rollback()


@pytest.mark.parametrize("commit_change", [True, False])
@pytest.mark.parametrize("bootstrap", [False, True])
async def test_admin_selection_waits_and_rereads_revision(
    _session_factory, store_state, profile_a_id, commit_change, bootstrap
):
    if bootstrap:
        async with _session_factory() as db:
            await db.execute(text("DELETE FROM eipd_policy_selector WHERE id=1"))
            await db.execute(
                text("DELETE FROM eipd_policy_selections WHERE id=:id"),
                {"id": store_state[1].event.id},
            )
            await db.commit()
    expected_revision = 0 if bootstrap else 1
    async with _session_factory() as preparer:
        await preparer.execute(text("SET LOCAL ROLE eipd_policy_admin"))
        first = await publish(preparer, profile_a_id)
        second = await publish(preparer, profile_a_id)
        await preparer.commit()
    async with _session_factory() as holder, _session_factory() as waiter:
        for db in (holder, waiter):
            await db.execute(text("SET LOCAL ROLE eipd_policy_admin"))
        await choose(holder, profile_a_id, first, expected_revision)
        pid = await waiter.scalar(text("SELECT pg_backend_pid()"))
        task = asyncio.create_task(
            choose(waiter, profile_a_id, second, expected_revision)
        )
        try:

            async def blocked():
                while not await holder.scalar(
                    text("SELECT pg_blocking_pids(:pid)"), dict(pid=pid)
                ):
                    await asyncio.sleep(0.02)

            await asyncio.wait_for(blocked(), 5)
            assert not task.done()
            if commit_change:
                await holder.commit()
            else:
                await holder.rollback()
            if commit_change:
                with pytest.raises(ValueError, match="obsoleta"):
                    await asyncio.wait_for(task, 5)
            else:
                result = await asyncio.wait_for(task, 5)
                assert (
                    result.selector.revision == expected_revision + 1
                    and result.selector.publication_id == second.id
                )
            await waiter.rollback()
        finally:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            await holder.rollback()
            await waiter.rollback()
    async with _session_factory() as db:
        state = await read_eipd_policy_audit_snapshot_v1(db)
        revision = expected_revision + int(commit_change)
        assert (state.selector.revision if state.selector else 0) == revision
        assert len(state.selections) == revision


async def test_failed_or_rolled_back_selection_has_no_event(
    _session_factory, store_state, profile_a_id
):
    async with _session_factory() as db:
        await db.execute(text("SET LOCAL ROLE eipd_policy_admin"))
        before = await read_eipd_policy_audit_snapshot_v1(db)
        pub = await publish(db, profile_a_id)
        await choose(db, profile_a_id, pub, 1)
        await db.rollback()
    async with _session_factory() as db:
        assert await read_eipd_policy_audit_snapshot_v1(db) == before
