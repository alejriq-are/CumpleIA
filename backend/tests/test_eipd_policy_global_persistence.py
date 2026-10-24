"""Control global EIPD: integridad y privilegios PostgreSQL, sin resolver activo."""

from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import delete, text
from sqlalchemy.exc import DBAPIError, IntegrityError

from app.db.models import EipdPolicyPublication, EipdPolicySelection, EipdPolicySelector
from app.services.eipd_policy import (
    build_eipd_policy_hash_v1,
    resolve_eipd_gate_policy_v1,
)
from tests import test_rls_isolation_licitud as rls_fixtures

app_role_session = rls_fixtures.app_role_session
_set_auth_user = rls_fixtures._set_auth_user

TABLES = ("eipd_policy_publications", "eipd_policy_selections", "eipd_policy_selector")


def publication(actor, reference=None):
    policy = resolve_eipd_gate_policy_v1().model_dump(mode="json")
    policy["policy_reference"] = reference or "TEST: " + str(uuid4())
    return EipdPolicyPublication(
        id=uuid4(),
        policy_version=1,
        policy_reference=policy["policy_reference"],
        policy_hash=build_eipd_policy_hash_v1(policy),
        payload=policy,
        created_by=actor,
        rationale="TEST: publicacion",
        evidence_reference="TEST: evidencia",
    )


def selection(pub, actor, previous=None):
    return EipdPolicySelection(
        id=uuid4(),
        revision=previous.revision + 1 if previous else 1,
        previous_revision=previous.revision if previous else 0,
        previous_publication_id=previous.publication_id if previous else None,
        previous_policy_hash=previous.policy_hash if previous else None,
        publication_id=pub.id,
        policy_hash=pub.policy_hash,
        created_by=actor,
        rationale="TEST: seleccion",
        evidence_reference="TEST: evidencia",
    )


@pytest_asyncio.fixture
async def global_state(_session_factory, profile_a_id):
    async with _session_factory() as db:
        assert (
            await db.get(EipdPolicySelector, 1) is None
        ), "Fixture requiere selector local vacio"
        pub = publication(profile_a_id)
        db.add(pub)
        await db.flush()
        event = selection(pub, profile_a_id)
        db.add(event)
        await db.flush()
        db.add(
            EipdPolicySelector(
                id=1, revision=1, publication_id=pub.id, selection_id=event.id
            )
        )
        await db.commit()
    yield pub, event
    async with _session_factory() as db:
        await db.execute(delete(EipdPolicySelector).where(EipdPolicySelector.id == 1))
        await db.execute(
            delete(EipdPolicySelection).where(EipdPolicySelection.id == event.id)
        )
        await db.execute(
            delete(EipdPolicyPublication).where(EipdPolicyPublication.id == pub.id)
        )
        await db.commit()


@pytest.mark.parametrize("table", TABLES)
async def test_runtime_readonly_rls_privileges(app_role_session, table):
    row = (
        await app_role_session.execute(
            text(
                """SELECT current_user,
      (SELECT rolbypassrls FROM pg_roles WHERE rolname=current_user),
      (SELECT relrowsecurity FROM pg_class WHERE oid=CAST(:table AS regclass)),
      has_table_privilege(current_user,:table,'SELECT'),
      has_table_privilege(current_user,:table,'INSERT'),
      has_table_privilege(current_user,:table,'UPDATE'),
      has_table_privilege(current_user,:table,'DELETE'),
      has_table_privilege(current_user,:table,'TRUNCATE'),
      pg_has_role(current_user,'eipd_policy_admin','MEMBER')"""
            ),
            {"table": table},
        )
    ).one()
    assert tuple(row) == (
        "app_user",
        False,
        True,
        True,
        False,
        False,
        False,
        False,
        False,
    )


@pytest.mark.parametrize("authenticated", [False, True])
@pytest.mark.parametrize("table", TABLES)
async def test_global_read_requires_auth(
    app_role_session, global_state, auth_a_id, table, authenticated
):
    if authenticated:
        await _set_auth_user(app_role_session, auth_a_id)
    else:
        await app_role_session.execute(
            text("SELECT set_config('request.jwt.claim.sub', '', true)")
        )
    assert await app_role_session.scalar(text(f"SELECT count(*) FROM {table}")) == int(
        authenticated
    )


@pytest.mark.parametrize("operation", ["UPDATE", "DELETE", "TRUNCATE"])
@pytest.mark.parametrize("table", TABLES)
async def test_runtime_cannot_mutate_global(
    app_role_session, global_state, auth_a_id, table, operation
):
    await _set_auth_user(app_role_session, auth_a_id)
    query = (
        f"UPDATE {table} SET id=id"
        if operation == "UPDATE"
        else (
            f"{operation} FROM {table}"
            if operation == "DELETE"
            else f"TRUNCATE {table}"
        )
    )
    with pytest.raises(DBAPIError):
        await app_role_session.execute(text(query))
    await app_role_session.rollback()


async def test_runtime_cannot_publish_or_assume_admin(
    app_role_session, auth_a_id, profile_a_id
):
    await _set_auth_user(app_role_session, auth_a_id)
    app_role_session.add(publication(profile_a_id))
    with pytest.raises(DBAPIError):
        await app_role_session.flush()
    await app_role_session.rollback()
    with pytest.raises(DBAPIError):
        await app_role_session.execute(text("SET LOCAL ROLE eipd_policy_admin"))
    await app_role_session.rollback()


async def test_admin_is_restricted_and_can_plan_atomic_selection(
    _session_factory, global_state, profile_a_id
):
    _, old = global_state
    async with _session_factory() as db:
        await db.execute(text("SET LOCAL ROLE eipd_policy_admin"))
        row = (
            await db.execute(
                text(
                    "SELECT rolcanlogin,rolsuper,rolbypassrls,rolcreaterole,rolcreatedb FROM pg_roles WHERE rolname=current_user"
                )
            )
        ).one()
        assert tuple(row) == (False, False, False, False, False)
        pub = publication(profile_a_id)
        db.add(pub)
        await db.flush()
        new = selection(pub, profile_a_id, old)
        db.add(new)
        await db.flush()
        await db.execute(
            text(
                "UPDATE eipd_policy_selector SET revision=2,publication_id=:pub,selection_id=:event WHERE id=1"
            ),
            dict(pub=pub.id, event=new.id),
        )
        await db.execute(text("SET CONSTRAINTS ALL IMMEDIATE"))
        assert await db.scalar(text("SELECT revision FROM eipd_policy_selector")) == 2
        await db.rollback()
    async with _session_factory() as db:
        assert (await db.get(EipdPolicySelector, 1)).revision == 1


@pytest.mark.parametrize("table", TABLES[:2])
@pytest.mark.parametrize("operation", ["UPDATE", "DELETE", "TRUNCATE"])
async def test_admin_audit_append_only(
    _session_factory, global_state, table, operation
):
    async with _session_factory() as db:
        await db.execute(text("SET LOCAL ROLE eipd_policy_admin"))
        query = (
            f"UPDATE {table} SET id=id"
            if operation == "UPDATE"
            else (
                f"{operation} FROM {table}"
                if operation == "DELETE"
                else f"TRUNCATE {table}"
            )
        )
        with pytest.raises(DBAPIError):
            await db.execute(text(query))
        await db.rollback()


@pytest.mark.parametrize(
    "mode",
    [
        "reference",
        "hash",
        "version",
        "payload",
        "blank",
        "duplicate_reference",
        "revision_gap",
        "previous_hash",
        "previous_partial",
        "reselection",
        "selector_identity",
        "selector_singleton",
        "missing_selector_update",
    ],
)
async def test_database_rejects_invalid_control(
    _session_factory, global_state, profile_a_id, mode
):
    old_pub, old_event = global_state
    async with _session_factory() as db:
        pub = publication(profile_a_id)
        if mode == "reference":
            pub.policy_reference = " "
        elif mode == "hash":
            pub.policy_hash = "bad"
        elif mode == "version":
            pub.policy_version = 2
        elif mode == "payload":
            pub.payload = {}
        elif mode == "blank":
            pub.evidence_reference = " "
        elif mode == "duplicate_reference":
            pub.policy_reference = old_pub.policy_reference
            pub.payload = old_pub.payload
        with pytest.raises(IntegrityError):
            if mode in (
                "reference",
                "hash",
                "version",
                "payload",
                "blank",
                "duplicate_reference",
            ):
                db.add(pub)
                await db.flush()
            else:
                db.add(pub)
                await db.flush()
                new = selection(pub, profile_a_id, old_event)
                if mode == "revision_gap":
                    new.revision = 4
                elif mode == "previous_hash":
                    new.previous_policy_hash = "a" * 64
                elif mode == "previous_partial":
                    new.previous_policy_hash = None
                elif mode == "reselection":
                    new.publication_id = old_pub.id
                    new.policy_hash = old_pub.policy_hash
                db.add(new)
                await db.flush()
                if mode == "selector_identity":
                    await db.execute(
                        text(
                            "UPDATE eipd_policy_selector SET revision=2, publication_id=:pub WHERE id=1"
                        ),
                        dict(pub=pub.id),
                    )
                elif mode == "selector_singleton":
                    db.add(
                        EipdPolicySelector(
                            id=2, revision=2, publication_id=pub.id, selection_id=new.id
                        )
                    )
                    await db.flush()
                if mode == "missing_selector_update":
                    await db.commit()
                else:
                    await db.execute(text("SET CONSTRAINTS ALL IMMEDIATE"))
        await db.rollback()
        assert (await db.get(EipdPolicySelector, 1)).revision == 1
        assert await db.get(EipdPolicyPublication, pub.id) is None


@pytest.mark.parametrize("table", TABLES)
async def test_global_control_shared_with_other_authenticated_tenant(
    app_role_session, global_state, auth_b_id, table
):
    await _set_auth_user(app_role_session, auth_b_id)
    assert await app_role_session.scalar(text(f"SELECT count(*) FROM {table}")) == 1


@pytest.mark.parametrize("table", TABLES[1:])
async def test_runtime_cannot_insert_selection_or_selector(
    app_role_session, auth_a_id, table
):
    await _set_auth_user(app_role_session, auth_a_id)
    with pytest.raises(DBAPIError) as exc:
        await app_role_session.execute(text(f"INSERT INTO {table} DEFAULT VALUES"))
    assert "permission denied" in str(exc.value).lower()
    await app_role_session.rollback()
