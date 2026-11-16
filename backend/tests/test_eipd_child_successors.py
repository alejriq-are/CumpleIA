"""Sucesores ficticios: API real con PostgreSQL, politica cerrada e historia intacta."""

import asyncio
from copy import deepcopy
from uuid import UUID, uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, IntegrityError

from app.db.child_eipd import EipdChildReview
from app.schemas.eipd_child_persistence import ChildNegativePolicyV1
from tests import test_api_child_adolescent as cases
from tests import test_rls_isolation_licitud as rls

rat_m3 = cases.rat_m3
saved = cases.saved
explicit_review_policy = cases.explicit_review_policy
pytestmark = pytest.mark.asyncio(loop_scope="session")


def client(state):
    return AsyncClient(
        transport=ASGITransport(app=state[2]),
        base_url="http://test",
        headers={"X-Organization-Id": str(state[3])},
    )


def parent(state):
    return f"/licitud/treatments/{state[0]}/assessments/{state[1]['id']}"


def url(state):
    return parent(state) + "/eipd-child/v4"


def review(decision="requiere_cambios"):
    return dict(
        data_kind="ficticios",
        decision=decision,
        rationale="PRUEBA: evidencia ficticia incompleta",
        review_reference="PRUEBA-INFANCIA",
    )


@pytest.fixture
async def prepared(saved, explicit_review_policy):
    async with client(saved) as http:
        response = await http.post(
            url(saved) + "/resolutions",
            json=dict(
                data_kind="ficticios", document={"notes": "PRUEBA: resolucion ficticia"}
            ),
        )
        assert response.status_code == 201, response.text
    return saved, response.json()


async def test_roundtrip_policy_and_closed_authority(prepared):
    state, resolution = prepared
    path = url(state) + f"/resolutions/{resolution['id']}"
    assert resolution["stored_coverage"] == "contexto_v4"
    assert (
        resolution["context_snapshot"]["child_adolescent_assessment"]
        == state[1]["child_adolescent_assessment"]
    )
    async with client(state) as http:
        assert (await http.get(path)).json() == resolution
        assert (await http.get(url(state) + "/resolutions")).json() == [resolution]
        policy = (await http.get(url(state) + "/policy")).json()
        assert policy["policy"]["activation"] == "deshabilitada"
        assert policy["policy"]["acceptance_status"] == "pendiente"
        events = []
        for decision in ("requiere_cambios", "no_continuar"):
            response = await http.post(path + "/reviews", json=review(decision))
            assert response.status_code == 201, response.text
            event = response.json()
            events.append(event)
            assert event["policy_hash"] == policy["policy_hash"]
            assert (
                event["review_context_metadata"]["child_material_hash"]
                == resolution["child_material_hash"]
            )
            assert not event["authorizes_action"] and not event["can_confirm"]
            assert (await http.get(path + f"/reviews/{event['id']}")).json() == event
        assert (await http.get(path + "/reviews")).json() == events
        assert (await http.post(parent(state) + "/confirm")).status_code == 409
        unchanged = (await http.get(parent(state))).json()
        assert unchanged["status"] == "borrador"
        assert (
            unchanged["eipd_resolution_assessment"]
            == state[1]["eipd_resolution_assessment"]
        )


@pytest.mark.parametrize(
    "patch",
    [
        {"decision": "continuar"},
        {"decision": "activar"},
        {"data_kind": "reales"},
        {"policy_hash": "a" * 64},
        {"policy_snapshot": {}},
        {"created_by": str(uuid4())},
        {"rationale": " "},
        {"review_reference": " "},
    ],
)
async def test_reject_injected_or_positive_reviews(prepared, patch):
    state, resolution = prepared
    async with client(state) as http:
        path = url(state) + f"/resolutions/{resolution['id']}/reviews"
        response = await http.post(path, json={**review(), **patch})
        assert response.status_code == 422, response.text
        assert (await http.get(path)).json() == []


@pytest.mark.parametrize(
    "change",
    [
        {"activation": "habilitada"},
        {"acceptance_status": "aceptada"},
        {"sources_status": "verificadas"},
        {"policy_schema_version": True},
        {"allowed_decisions": ["continuar"]},
        {"can_confirm": True},
    ],
)
async def test_policy_contract_cannot_promote(change):
    original = dict(
        global_policy_identity=dict(
            policy_version=1, policy_reference="PRUEBA", policy_hash="a" * 64
        )
    )
    with pytest.raises(ValidationError):
        ChildNegativePolicyV1.model_validate({**original, **change})


async def test_material_change_successor_and_history(prepared):
    state, resolution = prepared
    path = url(state) + f"/resolutions/{resolution['id']}"
    async with client(state) as http:
        old = (await http.post(path + "/reviews", json=review())).json()
        response = await http.patch(
            parent(state),
            json={
                "child_adolescent_assessment": {
                    "declared_groups": ["ninos_ninas"],
                    "notes": "PRUEBA: nuevo material ficticio",
                }
            },
        )
        assert response.status_code == 200, response.text
        stale = await http.post(path + "/reviews", json=review())
        assert (
            stale.status_code == 409
            and stale.json()["detail"]["code"] == "infancia_resolucion_obsoleta"
        )
        assert (await http.get(path)).json() == resolution
        assert (await http.get(path + "/reviews")).json() == [old]
        new = await http.post(
            url(state) + "/resolutions", json=dict(data_kind="ficticios", document={})
        )
        assert new.status_code == 201, new.text
        assert (
            new.json()["version"] == 2
            and new.json()["context_hash"] != resolution["context_hash"]
        )
        assert (await http.get(path + f"/reviews/{old['id']}")).json() == old
        response = await http.patch(
            parent(state), json={"child_adolescent_assessment": None}
        )
        assert response.status_code == 200, response.text
        assert (
            await http.post(
                url(state) + "/resolutions",
                json=dict(data_kind="ficticios", document={}),
            )
        ).status_code == 409
        assert (await http.post(path + "/reviews", json=review())).status_code == 409
        assert (await http.get(path)).json() == resolution


async def test_consent_change_requires_explicit_reaporte(prepared):
    state, resolution = prepared
    async with client(state) as http:
        response = await http.patch(
            parent(state),
            json={
                "consent_assessment": {
                    "given_by": "mandatario",
                    "notes": "PRUEBA: otro contexto",
                }
            },
        )
        assert response.status_code == 200, response.text
        post = await http.post(
            url(state) + "/resolutions", json=dict(data_kind="ficticios", document={})
        )
        assert (
            post.status_code == 409
            and post.json()["detail"]["code"] == "infancia_asociacion_no_vigente"
        )


async def test_serialized_resolution_versions(prepared):
    state, first = prepared

    async def create():
        async with client(state) as http:
            response = await http.post(
                url(state) + "/resolutions",
                json=dict(data_kind="ficticios", document={}),
            )
            assert response.status_code == 201, response.text
            return response.json()["version"]

    assert sorted(await asyncio.gather(create(), create())) == [2, 3]


async def test_tenant_and_parent_isolation(prepared, client_b, org_b_id):
    state, resolution = prepared
    path = url(state) + f"/resolutions/{resolution['id']}"
    async with AsyncClient(
        transport=ASGITransport(app=client_b),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_b_id)},
    ) as http:
        assert (await http.get(path)).status_code == 404
        assert (await http.post(path + "/reviews", json=review())).status_code == 404


async def test_wrong_parent_and_review(prepared):
    state, resolution = prepared
    path = url(state) + f"/resolutions/{resolution['id']}"
    async with client(state) as http:
        assert (
            await http.get(path.replace(state[1]["id"], str(uuid4())))
        ).status_code in (403, 404)
        assert (await http.get(path + f"/reviews/{uuid4()}")).status_code == 404


async def test_runtime_rls_and_append_only(
    prepared, _session_factory, _app_session_factory, auth_a_id, auth_b_id
):
    state, resolution = prepared
    async with client(state) as http:
        event = (
            await http.post(
                url(state) + f"/resolutions/{resolution['id']}/reviews", json=review()
            )
        ).json()
    async with _app_session_factory() as db:
        await rls._set_auth_user(db, auth_b_id)
        for table in ("eipd_child_resolutions", "eipd_child_reviews"):
            assert await db.scalar(text(f"SELECT count(*) FROM {table}")) == 0
        await db.rollback()
        await rls._set_auth_user(db, auth_a_id)
        assert (
            await db.scalar(
                text("SELECT count(*) FROM eipd_child_resolutions WHERE id=:id"),
                dict(id=UUID(resolution["id"])),
            )
            == 1
        )
        for table in ("eipd_child_resolutions", "eipd_child_reviews"):
            assert not await db.scalar(
                text(f"SELECT has_table_privilege('app_user','{table}','UPDATE')")
            )
            assert not await db.scalar(
                text(f"SELECT has_table_privilege('app_user','{table}','DELETE')")
            )
            assert await db.scalar(
                text(
                    f"SELECT relrowsecurity FROM pg_class WHERE oid='{table}'::regclass"
                )
            )
    async with _session_factory() as db:
        for table, key in (
            ("eipd_child_resolutions", resolution["id"]),
            ("eipd_child_reviews", event["id"]),
        ):
            with pytest.raises(DBAPIError):
                async with db.begin_nested():
                    await db.execute(
                        text(f"UPDATE {table} SET data_kind=data_kind WHERE id=:id"),
                        dict(id=UUID(key)),
                    )


@pytest.mark.parametrize("change", ["positive", "policy", "metadata", "parent"])
async def test_sql_constraints_enforce_closed_history(
    prepared, _session_factory, change
):
    state, resolution = prepared
    async with client(state) as http:
        event = (
            await http.post(
                url(state) + f"/resolutions/{resolution['id']}/reviews", json=review()
            )
        ).json()
    async with _session_factory() as db:
        row = await db.get(EipdChildReview, UUID(event["id"]))
        data = {
            column.name: deepcopy(getattr(row, column.name))
            for column in EipdChildReview.__table__.columns
        }
        data["id"] = uuid4()
        if change == "positive":
            data["decision"] = "continuar"
        if change == "policy":
            data["policy_snapshot"]["activation"] = "habilitada"
        if change == "metadata":
            data["review_context_metadata"]["context_hash"] = "b" * 64
        if change == "parent":
            data["child_material_hash"] = "b" * 64
            data["review_context_metadata"]["child_material_hash"] = "b" * 64
        with pytest.raises(IntegrityError):
            async with db.begin_nested():
                await db.execute(EipdChildReview.__table__.insert().values(**data))


@pytest.mark.parametrize("role", ["viewer", "inactive"])
async def test_write_roles_and_subscription(prepared, _session_factory, role):
    from sqlalchemy import update

    from app.db.models import Membership, Subscription

    state, resolution = prepared
    async with _session_factory() as db:
        if role == "viewer":
            await db.execute(
                update(Membership)
                .where(Membership.organization_id == state[3])
                .values(role="viewer")
            )
        else:
            await db.execute(
                update(Subscription)
                .where(Subscription.organization_id == state[3])
                .values(status="suspended")
            )
        await db.commit()
    try:
        async with client(state) as http:
            assert (
                await http.post(
                    url(state) + "/resolutions",
                    json=dict(data_kind="ficticios", document={}),
                )
            ).status_code == (403 if role == "viewer" else 402)
            assert (
                await http.post(
                    url(state) + f"/resolutions/{resolution['id']}/reviews",
                    json=review(),
                )
            ).status_code == (403 if role == "viewer" else 402)
            if role == "viewer":
                assert (
                    await http.get(url(state) + f"/resolutions/{resolution['id']}")
                ).status_code == 200
    finally:
        async with _session_factory() as db:
            await db.execute(
                update(Membership)
                .where(Membership.organization_id == state[3])
                .values(role="owner")
            )
            await db.execute(
                update(Subscription)
                .where(Subscription.organization_id == state[3])
                .values(status="active")
            )
            await db.commit()


async def test_no_policy_no_fallback(saved, _session_factory):
    async with _session_factory() as db:
        await db.execute(text("DELETE FROM eipd_policy_selector WHERE id=1"))
        await db.commit()
    async with client(saved) as http:
        response = await http.post(
            url(saved) + "/resolutions", json=dict(data_kind="ficticios", document={})
        )
        assert response.status_code == 409, response.text
        assert response.json()["detail"]["code"] == "politica_eipd_no_disponible"
        assert (await http.get(url(saved) + "/resolutions")).json() == []


async def test_non_development_write_denied(prepared, monkeypatch):
    from types import SimpleNamespace

    from app.services import eipd_child_persistence as service

    state, resolution = prepared
    monkeypatch.setattr(
        service, "get_settings", lambda: SimpleNamespace(environment="production")
    )
    async with client(state) as http:
        response = await http.post(
            url(state) + f"/resolutions/{resolution['id']}/reviews", json=review()
        )
        assert (
            response.status_code == 409
            and response.json()["detail"]["code"]
            == "infancia_escritura_solo_desarrollo"
        )


@pytest.mark.parametrize("commit_change", [True, False])
async def test_waiting_review_reloads_child_after_commit_or_rollback(
    prepared, _app_session_factory, auth_a_id, profile_a_id, commit_change
):
    from fastapi import HTTPException

    from app.schemas.child_adolescent_api import LegalAssessmentChildDraftUpdateV1
    from app.schemas.eipd_child_persistence import ChildReviewCreateV4
    from app.services import eipd_child_persistence as service
    from app.services import licitud
    from tests import test_eipd_policy_shared_lock as locks

    state, resolution = prepared
    async with _app_session_factory() as holder, _app_session_factory() as waiter:
        await rls._set_auth_user(holder, auth_a_id)
        await rls._set_auth_user(waiter, auth_a_id)
        await licitud.update_legal_assessment_draft_v1(
            holder,
            state[3],
            state[0],
            UUID(state[1]["id"]),
            profile_a_id,
            LegalAssessmentChildDraftUpdateV1.model_validate(
                {"child_adolescent_assessment": None}
            ),
        )
        pid = await waiter.scalar(text("SELECT pg_backend_pid()"))
        task = asyncio.create_task(
            service.create_review(
                waiter,
                state[3],
                state[0],
                UUID(state[1]["id"]),
                UUID(resolution["id"]),
                profile_a_id,
                ChildReviewCreateV4.model_validate(review()),
            )
        )
        try:
            await locks.blocked(holder, pid)
            if commit_change:
                await holder.commit()
                with pytest.raises(HTTPException) as error:
                    await asyncio.wait_for(task, 5)
                assert error.value.status_code == 409
                await waiter.rollback()
            else:
                await holder.rollback()
                event = await asyncio.wait_for(task, 5)
                assert (
                    event.context_hash == resolution["context_hash"]
                    and not event.authorizes_action
                )
                await waiter.commit()
        finally:
            await holder.rollback()
            await locks.stop(task)
            await waiter.rollback()


async def test_downgrade_guard_and_empty_roundtrip(prepared, _session_factory):
    import importlib.util
    from pathlib import Path

    from alembic.migration import MigrationContext
    from alembic.operations import Operations
    from app.db.base import Base

    path = (
        Path(__file__).parents[1]
        / "alembic/versions/b84e9f1a5c32_child_eipd_successors.py"
    )
    spec = importlib.util.spec_from_file_location("child_successor_migration", path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    restrict_path = (
        Path(__file__).parents[1]
        / "alembic/versions/c95f0a2b6d43_restrict_child_eipd_history.py"
    )
    restrict_spec = importlib.util.spec_from_file_location(
        "child_history_restrict_roundtrip", restrict_path
    )
    restrict = importlib.util.module_from_spec(restrict_spec)
    restrict_spec.loader.exec_module(restrict)
    async with _session_factory() as db:
        connection = await db.connection()

        def downgrade(sync):
            with Operations.context(
                MigrationContext.configure(
                    sync, opts={"target_metadata": Base.metadata}
                )
            ):
                restrict.downgrade()
                migration.downgrade()

        with pytest.raises(RuntimeError, match="historial infancia"):
            await connection.run_sync(downgrade)
        # Eliminacion exclusivamente de fixtures ficticias dentro de transaccion revertida.
        await db.execute(text("DELETE FROM eipd_child_reviews"))
        await db.execute(text("DELETE FROM eipd_child_resolutions"))
        acceptance_path = (
            Path(__file__).parents[1]
            / "alembic/versions/d16a3b7c8e52_organization_acceptance.py"
        )
        acceptance_spec = importlib.util.spec_from_file_location(
            "acceptance_migration_roundtrip", acceptance_path
        )
        acceptance_migration = importlib.util.module_from_spec(acceptance_spec)
        acceptance_spec.loader.exec_module(acceptance_migration)

        def remove_acceptance(sync):
            with Operations.context(
                MigrationContext.configure(
                    sync, opts={"target_metadata": Base.metadata}
                )
            ):
                acceptance_migration.downgrade()

        await connection.run_sync(remove_acceptance)
        await connection.run_sync(downgrade)

        def upgrade(sync):
            with Operations.context(
                MigrationContext.configure(
                    sync, opts={"target_metadata": Base.metadata}
                )
            ):
                migration.upgrade()
                restrict.upgrade()
                acceptance_migration.upgrade()

        await connection.run_sync(upgrade)
        assert await db.scalar(
            text(
                "SELECT relrowsecurity FROM pg_class WHERE oid='eipd_child_reviews'::regclass"
            )
        )
        await db.rollback()


async def test_rat_change_rejects_new_resolution(prepared, _session_factory):
    state, _ = prepared
    async with _session_factory() as db:
        await db.execute(
            text(
                "UPDATE treatments SET retention_rule='PRUEBA: retencion modificada' WHERE id=:id"
            ),
            dict(id=state[0]),
        )
        await db.commit()
    async with client(state) as http:
        response = await http.post(
            url(state) + "/resolutions", json=dict(data_kind="ficticios", document={})
        )
        assert (
            response.status_code == 409
            and response.json()["detail"]["code"] == "infancia_contexto_rat_obsoleto"
        )


@pytest.mark.parametrize(
    "change",
    [
        {"context_hash": "a" * 64},
        {"context_snapshot": {}},
        {"data_kind": "reales"},
        {"document": {"context_binding": {}}},
    ],
)
async def test_resolution_server_fields_rejected(prepared, change):
    state, _ = prepared
    async with client(state) as http:
        response = await http.post(
            url(state) + "/resolutions",
            json={"data_kind": "ficticios", "document": {}, **change},
        )
        assert response.status_code == 422
        assert len((await http.get(url(state) + "/resolutions")).json()) == 1


@pytest.mark.parametrize("actor", ["other_tenant", "forged_author", "viewer"])
async def test_direct_insert_rls_rejects_cross_tenant_or_actor(
    prepared,
    _session_factory,
    _app_session_factory,
    auth_a_id,
    auth_b_id,
    profile_b_id,
    actor,
):
    from sqlalchemy import update

    from app.db.child_eipd import EipdChildResolution
    from app.db.models import Membership

    state, resolution = prepared
    async with _session_factory() as db:
        row = await db.get(EipdChildResolution, UUID(resolution["id"]))
        data = {
            c.name: deepcopy(getattr(row, c.name))
            for c in EipdChildResolution.__table__.columns
        }
        if actor == "viewer":
            await db.execute(
                update(Membership)
                .where(Membership.organization_id == state[3])
                .values(role="viewer")
            )
            await db.commit()
    data["id"] = uuid4()
    data["version"] = 2
    if actor == "forged_author":
        data["created_by"] = profile_b_id
    try:
        async with _app_session_factory() as db:
            await rls._set_auth_user(
                db, auth_b_id if actor == "other_tenant" else auth_a_id
            )
            with pytest.raises(DBAPIError):
                await db.execute(EipdChildResolution.__table__.insert().values(**data))
            await db.rollback()
    finally:
        if actor == "viewer":
            async with _session_factory() as db:
                await db.execute(
                    update(Membership)
                    .where(Membership.organization_id == state[3])
                    .values(role="owner")
                )
                await db.commit()


async def test_parent_delete_cannot_erase_child_history(
    prepared, _app_session_factory, auth_a_id
):
    state, resolution = prepared
    async with client(state) as http:
        response = await http.post(
            url(state) + f"/resolutions/{resolution['id']}/reviews", json=review()
        )
        assert response.status_code == 201, response.text
    async with _app_session_factory() as db:
        await rls._set_auth_user(db, auth_a_id)
        with pytest.raises(DBAPIError):
            async with db.begin_nested():
                await db.execute(
                    text("DELETE FROM legal_assessments WHERE id=:id"),
                    dict(id=UUID(state[1]["id"])),
                )
        assert (
            await db.scalar(
                text("SELECT count(*) FROM eipd_child_resolutions WHERE id=:id"),
                dict(id=UUID(resolution["id"])),
            )
            == 1
        )
        assert (
            await db.scalar(
                text("SELECT count(*) FROM eipd_child_reviews WHERE resolution_id=:id"),
                dict(id=UUID(resolution["id"])),
            )
            == 1
        )
        await db.rollback()


async def test_restrict_fks_and_parent_links(prepared, _session_factory):
    state, resolution = prepared
    async with client(state) as http:
        response = await http.post(
            url(state) + f"/resolutions/{resolution['id']}/reviews", json=review()
        )
        assert response.status_code == 201, response.text
    async with _session_factory() as db:
        actions = (
            (
                await db.execute(
                    text(
                        "SELECT confdeltype FROM pg_constraint WHERE conname IN ('fk_eipd_child_resolutions_assessment_id_legal_assessments','fk_eipd_child_reviews_resolution_id_eipd_child_resolutions')"
                    )
                )
            )
            .scalars()
            .all()
        )
        assert len(actions) == 2 and all(x == b"r" or x == "r" for x in actions)
        for table, key in (
            ("legal_assessments", state[1]["id"]),
            ("eipd_child_resolutions", resolution["id"]),
        ):
            with pytest.raises(IntegrityError):
                async with db.begin_nested():
                    await db.execute(
                        text(f"DELETE FROM {table} WHERE id=:id"), dict(id=UUID(key))
                    )
        assert (
            await db.scalar(
                text("SELECT count(*) FROM eipd_child_reviews WHERE resolution_id=:id"),
                dict(id=UUID(resolution["id"])),
            )
            == 1
        )


async def test_missing_environment_and_opt_in_fail_closed(prepared, monkeypatch):
    from app.core.config import Settings
    from app.services import eipd_child_persistence as service

    monkeypatch.delenv("ENVIRONMENT", raising=False)
    monkeypatch.delenv("EIPD_CHILD_TEST_WRITES_ENABLED", raising=False)
    settings = Settings(_env_file=None, supabase_url="https://test-project.supabase.co")
    assert (
        settings.environment == "development"
        and not settings.eipd_child_test_writes_enabled
    )
    monkeypatch.setattr(service, "get_settings", lambda: settings)
    state, resolution = prepared
    async with client(state) as http:
        for path, payload in (
            (url(state) + "/resolutions", dict(data_kind="ficticios", document={})),
            (url(state) + f"/resolutions/{resolution['id']}/reviews", review()),
        ):
            response = await http.post(path, json=payload)
            assert (
                response.status_code == 409
                and response.json()["detail"]["code"]
                == "infancia_escritura_ficticia_no_habilitada"
            )
        assert (
            await http.get(url(state) + f"/resolutions/{resolution['id']}")
        ).status_code == 200
