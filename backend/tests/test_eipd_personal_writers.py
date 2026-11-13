"""Entradas personales sin actor de cliente; primitivas privadas solo fixtures."""

from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.services.eipd_policy_store import (
    publish_eipd_policy_v1,
    read_eipd_policy_audit_snapshot_v1,
    select_eipd_policy_v1,
)
from tests import test_eipd_personal_authority as personal
from tests import test_rls_isolation_licitud as rls
from tests import test_services_eipd_policy_store as fixtures

app_role_session = rls.app_role_session
authority = personal.authority


@pytest_asyncio.fixture(autouse=True)
async def cleanup(_session_factory, authority):
    yield
    async with _session_factory() as db:
        params = dict(actor=authority[0])
        ids = "SELECT id FROM eipd_policy_publications WHERE created_by=:actor"
        await db.execute(
            text(f"DELETE FROM eipd_policy_selector WHERE publication_id IN ({ids})"),
            params,
        )
        await db.execute(
            text(f"DELETE FROM eipd_policy_selections WHERE publication_id IN ({ids})"),
            params,
        )
        await db.execute(
            text("DELETE FROM eipd_policy_publications WHERE created_by=:actor"), params
        )
        await db.commit()


async def publish(db):
    return await publish_eipd_policy_v1(
        db, fixtures.disabled(), rationale="TEST", evidence_reference="TEST"
    )


async def choose(db, pub):
    return await select_eipd_policy_v1(
        db,
        dict(publication_id=pub.id, expected_revision=0),
        rationale="TEST",
        evidence_reference="TEST",
    )


async def test_derived_actor_publish_then_select_atomic(_session_factory, authority):
    async with _session_factory() as db:
        await personal.admin(db, authority[1])
        pub = await publish(db)
        assert pub.created_by == authority[0]
        assert (await read_eipd_policy_audit_snapshot_v1(db)).selector is None
        plan = await choose(db, pub)
        assert plan.event.created_by == authority[0]
        await db.commit()
    async with _session_factory() as db:
        state = await read_eipd_policy_audit_snapshot_v1(db)
        assert state.selector.publication_id == pub.id
        assert len(state.publications) == len(state.selections) == 1


@pytest.mark.parametrize("operation", ["publish", "select"])
@pytest.mark.parametrize("identity", ["anonymous", "unknown", "tenant"])
async def test_untrusted_person_cannot_write(
    _session_factory, authority, auth_a_id, identity, operation
):
    async with _session_factory() as db:
        await personal.admin(db, authority[1])
        pub = await publish(db)
        await db.commit()
    async with _session_factory() as db:
        await db.execute(text("SET LOCAL ROLE eipd_policy_admin"))
        if identity != "anonymous":
            await rls._set_auth_user(
                db, uuid4() if identity == "unknown" else auth_a_id
            )
        with pytest.raises(DBAPIError):
            await (publish(db) if operation == "publish" else choose(db, pub))
        await db.rollback()
    async with _session_factory() as db:
        state = await read_eipd_policy_audit_snapshot_v1(db)
        assert state.selector is None and len(state.publications) == 1
        assert state.selections == ()


async def test_runtime_channel_rejected_even_for_superadmin(
    app_role_session, authority
):
    await rls._set_auth_user(app_role_session, authority[1])
    with pytest.raises(PermissionError):
        await publish(app_role_session)
    await app_role_session.rollback()


@pytest.mark.parametrize("operation", ["publish", "select"])
async def test_actor_argument_not_accepted(_session_factory, authority, operation):
    async with _session_factory() as db:
        await personal.admin(db, authority[1])
        with pytest.raises(TypeError):
            if operation == "publish":
                await publish_eipd_policy_v1(
                    db,
                    fixtures.disabled(),
                    actor_id=uuid4(),
                    rationale="TEST",
                    evidence_reference="TEST",
                )
            else:
                await select_eipd_policy_v1(
                    db,
                    dict(publication_id=uuid4(), expected_revision=0),
                    actor_id=uuid4(),
                    rationale="TEST",
                    evidence_reference="TEST",
                )
        assert (await read_eipd_policy_audit_snapshot_v1(db)).publications == ()
        await db.rollback()


async def test_rollback_removes_publication_event_selector(_session_factory, authority):
    async with _session_factory() as db:
        await personal.admin(db, authority[1])
        pub = await publish(db)
        await choose(db, pub)
        await db.rollback()
    async with _session_factory() as db:
        state = await read_eipd_policy_audit_snapshot_v1(db)
        assert state.selector is None and state.publications == state.selections == ()
