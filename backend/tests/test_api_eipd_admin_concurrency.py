"""Concurrencia HTTP sobre JWT real y locks PostgreSQL, con pausas de test."""

import asyncio
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db import eipd_admin as channel
from app.db.models import EipdPolicyPublication
from app.services.eipd_policy_store import _SELECTION_LOCK
from tests import test_api_eipd_admin as http
from tests import test_eipd_policy_shared_lock as locks

pytestmark = pytest.mark.asyncio(loop_scope="session")
api = http.api
dedicated = http.dedicated
authority = http.authority
cleanup = http.cleanup
signing_key = http.signing_key
patch_jwks = http.patch_jwks


async def request_body(api, credential, operation):
    if operation == "publications":
        return http.publication()
    pub = await api.post(
        "/admin/eipd/publications", json=http.publication(), headers=credential
    )
    assert pub.status_code == 201, pub.text
    return http.selection(pub.json()["id"])


@pytest.mark.parametrize("operation", ["publications", "selections"])
@pytest.mark.parametrize("commit_revocation", [True, False])
async def test_revocation_before_http_authority_waits_and_reloads(
    api,
    dedicated,
    authority,
    signing_key,
    _session_factory,
    operation,
    commit_revocation,
):
    credential = http.headers(signing_key, authority[1])
    body = await request_body(api, credential, operation)
    before = await http.state(_session_factory)
    async with dedicated[0]() as db:
        pid = await db.scalar(text("SELECT pg_backend_pid()"))
    async with _session_factory() as owner:
        await owner.execute(
            text("UPDATE profiles SET is_superadmin=false WHERE id=:id"),
            {"id": authority[0]},
        )
        task = asyncio.create_task(
            api.post("/admin/eipd/" + operation, json=body, headers=credential)
        )
        try:
            await locks.blocked(owner, pid)
            assert not task.done()
            if commit_revocation:
                await owner.commit()
            else:
                await owner.rollback()
            response = await asyncio.wait_for(task, 5)
            assert response.status_code == (
                403 if commit_revocation else 201
            ), response.text
            after = await http.state(_session_factory)
            if commit_revocation:
                assert after == before
            elif operation == "publications":
                assert len(after.publications) == len(before.publications) + 1
            else:
                assert len(after.selections) == 1 and after.selector.revision == 1
        finally:
            await locks.stop(task)
            await owner.rollback()


@pytest.mark.parametrize("operation", ["publications", "selections"])
@pytest.mark.parametrize("finish", ["commit", "rollback", "cancel"])
async def test_revocation_after_http_authority_waits_until_transaction_end(
    monkeypatch,
    api,
    dedicated,
    authority,
    signing_key,
    _session_factory,
    operation,
    finish,
):
    credential = http.headers(signing_key, authority[1])
    body = await request_body(api, credential, operation)
    before = await http.state(_session_factory)
    reached, release = asyncio.Event(), asyncio.Event()
    original = AsyncSession.commit

    async def paused_commit(db):
        if db.bind is dedicated[0].kw["bind"]:
            reached.set()
            await release.wait()
            if finish == "rollback":
                raise RuntimeError("TEST rollback at commit")
        return await original(db)

    with monkeypatch.context() as scoped:
        scoped.setattr(AsyncSession, "commit", paused_commit)
        request = asyncio.create_task(
            api.post("/admin/eipd/" + operation, json=body, headers=credential)
        )
        update = None
        async with _session_factory() as owner:
            try:
                await asyncio.wait_for(reached.wait(), 5)
                pid = await owner.scalar(text("SELECT pg_backend_pid()"))
                update = asyncio.create_task(
                    owner.execute(
                        text("UPDATE profiles SET is_superadmin=false WHERE id=:id"),
                        {"id": authority[0]},
                    )
                )
                async with _session_factory() as observer:
                    await locks.blocked(observer, pid)
                assert not update.done()
                if finish == "cancel":
                    request.cancel()
                    with pytest.raises(asyncio.CancelledError):
                        await request
                else:
                    release.set()
                    response = await asyncio.wait_for(request, 5)
                    assert response.status_code == (201 if finish == "commit" else 500)
                await asyncio.wait_for(update, 5)
                await owner.commit()
            finally:
                release.set()
                await locks.stop(request)
                if update is not None:
                    await locks.stop(update)
                await owner.rollback()
    after = await http.state(_session_factory)
    if finish != "commit":
        assert after == before
    elif operation == "publications":
        assert len(after.publications) == len(before.publications) + 1
    else:
        assert len(after.selections) == 1 and after.selector.revision == 1
    denied = await api.post("/admin/eipd/" + operation, json=body, headers=credential)
    assert denied.status_code == 403
    assert await http.state(_session_factory) == after
    async with dedicated[0]() as db:
        assert await db.scalar(text("SELECT current_user")) == dedicated[1]
        assert not await db.scalar(
            text("SELECT current_setting('request.jwt.claim.sub',true)")
        )


@pytest_asyncio.fixture
async def parallel(monkeypatch, api, dedicated):
    name = "test_eipd_http_" + uuid4().hex
    engine = create_async_engine(
        dedicated[0].kw["bind"].url,
        pool_size=2,
        max_overflow=0,
        echo=False,
        hide_parameters=True,
        isolation_level="READ COMMITTED",
        connect_args={"server_settings": {"application_name": name}},
    )
    factory = async_sessionmaker(engine, expire_on_commit=False)
    monkeypatch.setattr(channel, "get_eipd_admin_session_factory", lambda: factory)
    try:
        yield factory, name
    finally:
        await engine.dispose()


async def blocked_requests(observer, name, count):
    async def wait():
        while True:
            # pg_stat_activity puede conservar snapshot durante la transaccion observadora.
            await observer.execute(text("SELECT pg_stat_clear_snapshot()"))
            pids = (
                (
                    await observer.execute(
                        text(
                            "SELECT pid FROM pg_stat_activity WHERE application_name=:name "
                            "AND cardinality(pg_blocking_pids(pid))>0"
                        ),
                        {"name": name},
                    )
                )
                .scalars()
                .all()
            )
            if len(pids) == count:
                return pids
            await asyncio.sleep(0.02)

    return await asyncio.wait_for(wait(), 5)


async def test_two_http_selections_same_revision_only_one_commits(
    api, parallel, authority, signing_key, _session_factory
):
    credential = http.headers(signing_key, authority[1])
    publications = []
    for _ in range(2):
        response = await api.post(
            "/admin/eipd/publications", json=http.publication(), headers=credential
        )
        assert response.status_code == 201
        publications.append(response.json()["id"])
    async with _session_factory() as holder:
        await holder.execute(
            text("SELECT pg_advisory_xact_lock(:key)"), {"key": _SELECTION_LOCK}
        )
        tasks = [
            asyncio.create_task(
                api.post(
                    "/admin/eipd/selections",
                    json=http.selection(pub),
                    headers=credential,
                )
            )
            for pub in publications
        ]
        try:
            pids = await blocked_requests(holder, parallel[1], 2)
            assert len(set(pids)) == 2 and all(not t.done() for t in tasks)
            await holder.commit()
            responses = await asyncio.wait_for(asyncio.gather(*tasks), 5)
            assert sorted(r.status_code for r in responses) == [201, 409]
            state = await http.state(_session_factory)
            winner = next(r.json() for r in responses if r.status_code == 201)
            assert len(state.publications) == 2 and len(state.selections) == 1
            assert str(state.selector.selection_id) == winner["event"]["id"]
            assert (
                str(state.selector.publication_id) == winner["event"]["publication_id"]
            )
            assert state.selector.revision == 1
        finally:
            for task in tasks:
                await locks.stop(task)
            await holder.rollback()


async def test_two_http_publications_same_reference_unique_conflict_is_409(
    monkeypatch, api, parallel, authority, signing_key, _session_factory
):
    credential = http.headers(signing_key, authority[1])
    body = http.publication()
    barrier = asyncio.Barrier(2)
    reached, release = asyncio.Event(), asyncio.Event()
    original_flush, original_commit = AsyncSession.flush, AsyncSession.commit

    async def simultaneous_flush(db, *args, **kwargs):
        if db.bind is parallel[0].kw["bind"] and any(
            isinstance(row, EipdPolicyPublication) for row in db.new
        ):
            await asyncio.wait_for(barrier.wait(), 5)
        return await original_flush(db, *args, **kwargs)

    async def paused_commit(db):
        if db.bind is parallel[0].kw["bind"]:
            reached.set()
            await release.wait()
        return await original_commit(db)

    with monkeypatch.context() as scoped:
        scoped.setattr(AsyncSession, "flush", simultaneous_flush)
        scoped.setattr(AsyncSession, "commit", paused_commit)
        tasks = [
            asyncio.create_task(
                api.post("/admin/eipd/publications", json=body, headers=credential)
            )
            for _ in range(2)
        ]
        try:
            await asyncio.wait_for(reached.wait(), 5)
            async with _session_factory() as observer:
                await blocked_requests(observer, parallel[1], 1)
            assert all(not t.done() for t in tasks)
            release.set()
            responses = await asyncio.wait_for(asyncio.gather(*tasks), 5)
            assert sorted(r.status_code for r in responses) == [201, 409]
            state = await http.state(_session_factory)
            assert (
                len(state.publications) == 1
                and not state.selections
                and state.selector is None
            )
            assert (
                state.publications[0].policy.policy_reference
                == body["policy"]["policy_reference"]
            )
        finally:
            release.set()
            for task in tasks:
                await locks.stop(task)
