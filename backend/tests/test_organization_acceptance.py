"""Aceptacion ficticia en API/DB reales; no confiere autoridad global."""

import asyncio
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text, update
from sqlalchemy.exc import DBAPIError

from app.db.models import Membership, UserRole
from tests import test_eipd_child_successors as cases
from tests import test_rls_isolation_licitud as rls

rat_m3 = cases.rat_m3
saved = cases.saved
explicit_review_policy = cases.explicit_review_policy
prepared = cases.prepared
pytestmark = pytest.mark.asyncio(loop_scope="session")


def base(state):
    return cases.parent(state) + "/organization-acceptance/v1"


def designation(actor, revision=0, action="otorgar", role="responsable"):
    return dict(
        data_kind="ficticios",
        actor_id=str(actor),
        expected_revision=revision,
        action=action,
        organization_role=role,
        responsible_party_reference=(
            "PRUEBA: responsable mandante" if role == "encargado" else None
        ),
        faculty_reference="PRUEBA: designacion",
        evidence_reference="PRUEBA: evidencia facultad",
    )


def decision(aid, choice="acepta"):
    return dict(
        data_kind="ficticios",
        authority_id=aid,
        decision=choice,
        rationale="PRUEBA: revision documental ficticia",
        evidence_reference="PRUEBA: acta ficticia",
    )


async def grant(http, state, actor, **kw):
    result = await http.post(base(state) + "/authority", json=designation(actor, **kw))
    assert result.status_code == 201, result.text
    return result.json()


def events(state, row):
    return base(state) + f"/resolutions/{row['id']}/events"


async def test_owner_no_implicit_authority_and_three_decisions(prepared, profile_a_id):
    state, row = prepared
    async with cases.client(state) as http:
        before = (await http.get(cases.url(state) + "/policy")).json()
        denied = await http.post(events(state, row), json=decision(str(uuid4())))
        assert denied.status_code == 403
        g = await grant(http, state, profile_a_id)
        for choice in ("acepta", "rechaza", "requiere_cambios"):
            response = await http.post(
                events(state, row), json=decision(g["id"], choice)
            )
            assert response.status_code == 201, response.text
            out = response.json()
            assert out["actor_id"] == str(profile_a_id) and out[
                "organization_id"
            ] == str(state[3])
            assert (
                out["document_hash"] == row["document_hash"]
                and out["material_status"] == "coincide"
            )
            assert not out["can_confirm"] and not out["authorizes_action"]
        history = (await http.get(events(state, row))).json()
        assert len(history) == 3
        assert (await http.get(cases.url(state) + "/policy")).json() == before
        assert (await http.post(cases.parent(state) + "/confirm")).status_code == 409


async def test_revision_cas_concurrency_and_revoke(prepared, profile_a_id):
    state, row = prepared
    async with cases.client(state) as http:
        results = await asyncio.gather(
            *[
                http.post(base(state) + "/authority", json=designation(profile_a_id))
                for _ in range(2)
            ]
        )
        assert sorted(r.status_code for r in results) == [201, 409]
        g = next(r.json() for r in results if r.status_code == 201)
        assert (
            await http.post(events(state, row), json=decision(g["id"]))
        ).status_code == 201
        revoke = await grant(http, state, profile_a_id, revision=1, action="revocar")
        assert revoke["revision"] == 2
        assert (
            await http.post(events(state, row), json=decision(g["id"]))
        ).status_code == 403
        out = (await http.get(events(state, row))).json()[0]
        assert not out["faculty_current"]


async def test_new_resolution_does_not_inherit_acceptance(prepared, profile_a_id):
    state, row = prepared
    async with cases.client(state) as http:
        g = await grant(http, state, profile_a_id)
        assert (
            await http.post(events(state, row), json=decision(g["id"]))
        ).status_code == 201
        new = (
            await http.post(
                cases.url(state) + "/resolutions",
                json=dict(data_kind="ficticios", document={"notes": "PRUEBA: sucesor"}),
            )
        ).json()
        assert (await http.get(events(state, row))).json()[0][
            "material_status"
        ] == "obsoleto"
        assert (await http.get(events(state, new))).json() == []
        assert (
            await http.post(events(state, row), json=decision(g["id"]))
        ).status_code == 409


async def test_changed_child_material_is_obsolete(prepared, profile_a_id):
    state, row = prepared
    async with cases.client(state) as http:
        g = await grant(http, state, profile_a_id)
        assert (
            await http.post(events(state, row), json=decision(g["id"]))
        ).status_code == 201
        patch = await http.patch(
            cases.parent(state),
            json={
                "child_adolescent_assessment": {
                    "declared_groups": ["ninos_ninas"],
                    "notes": "PRUEBA: cambio",
                }
            },
        )
        assert patch.status_code == 200
        assert (
            await http.post(events(state, row), json=decision(g["id"]))
        ).status_code == 409
        assert (await http.get(events(state, row))).json()[0][
            "material_status"
        ] == "obsoleto"


@pytest.mark.parametrize("role", [UserRole.editor, UserRole.viewer])
async def test_editor_viewer_cannot_designate(
    prepared, profile_a_id, _session_factory, role
):
    state, _ = prepared
    async with _session_factory() as db:
        await db.execute(
            update(Membership)
            .where(
                Membership.profile_id == profile_a_id,
                Membership.organization_id == state[3],
            )
            .values(role=role)
        )
        await db.commit()
    try:
        async with cases.client(state) as http:
            assert (
                await http.post(
                    base(state) + "/authority", json=designation(profile_a_id)
                )
            ).status_code == 403
    finally:
        async with _session_factory() as db:
            await db.execute(
                update(Membership)
                .where(
                    Membership.profile_id == profile_a_id,
                    Membership.organization_id == state[3],
                )
                .values(role=UserRole.owner)
            )
            await db.commit()


async def test_foreign_actor_and_header_rejected(prepared, profile_b_id, org_b_id):
    state, row = prepared
    async with cases.client(state) as http:
        assert (
            await http.post(base(state) + "/authority", json=designation(profile_b_id))
        ).status_code == 403
        assert (
            await http.get(
                events(state, row), headers={"X-Organization-Id": str(org_b_id)}
            )
        ).status_code in (403, 404)


@pytest.mark.parametrize(
    "change",
    [
        {"data_kind": "reales"},
        {"decision": "continuar"},
        {"created_by": str(uuid4())},
        {"document_hash": "a" * 64},
    ],
)
async def test_closed_input(prepared, change):
    state, row = prepared
    async with cases.client(state) as http:
        assert (
            await http.post(
                events(state, row), json={**decision(str(uuid4())), **change}
            )
        ).status_code == 422


async def test_encargado_requires_responsible_reference(prepared, profile_a_id):
    state, _ = prepared
    p = designation(profile_a_id, role="encargado")
    p["responsible_party_reference"] = None
    async with cases.client(state) as http:
        assert (await http.post(base(state) + "/authority", json=p)).status_code == 422
        g = await grant(http, state, profile_a_id, role="encargado")
        assert g["responsible_party_reference"]


async def test_sql_isolation_immutability_and_parent_restrict(
    prepared, profile_a_id, auth_a_id, auth_b_id, _app_session_factory, _session_factory
):
    state, row = prepared
    async with cases.client(state) as http:
        g = await grant(http, state, profile_a_id)
        out = (await http.post(events(state, row), json=decision(g["id"]))).json()
    async with _app_session_factory() as db:
        await rls._set_auth_user(db, auth_b_id)
        assert (
            await db.scalar(
                text(
                    "SELECT count(*) FROM organization_document_acceptances WHERE id=:id"
                ),
                {"id": UUID(out["id"])},
            )
            == 0
        )
        await db.rollback()
        await rls._set_auth_user(db, auth_a_id)
        for table in (
            "organization_acceptance_authorities",
            "organization_document_acceptances",
        ):
            for operation in ("UPDATE", "DELETE", "TRUNCATE"):
                assert not await db.scalar(
                    text("SELECT has_table_privilege('app_user',:t,:op)"),
                    {"t": table, "op": operation},
                )
        with pytest.raises(DBAPIError):
            await db.execute(
                text("DELETE FROM legal_assessments WHERE id=:id"),
                {"id": UUID(state[1]["id"])},
            )
        await db.rollback()
    async with _session_factory() as db:
        with pytest.raises(DBAPIError):
            async with db.begin_nested():
                await db.execute(
                    text(
                        "UPDATE organization_document_acceptances SET rationale='cambio' WHERE id=:id"
                    ),
                    {"id": UUID(out["id"])},
                )


async def test_opt_in_closed(prepared, profile_a_id, monkeypatch):
    from app.services import organization_acceptance as service

    state, row = prepared
    settings = service.get_settings()
    monkeypatch.setattr(settings, "eipd_child_test_writes_enabled", False)
    async with cases.client(state) as http:
        assert (
            await http.post(base(state) + "/authority", json=designation(profile_a_id))
        ).status_code == 409
        assert (
            await http.post(events(state, row), json=decision(str(uuid4())))
        ).status_code == 409


@pytest.mark.parametrize("revoke_wins", [True, False])
async def test_acceptance_and_revocation_serialize_real_transactions(
    prepared, profile_a_id, auth_a_id, _app_session_factory, revoke_wins
):
    from fastapi import HTTPException

    from app.schemas.organization_acceptance import AcceptanceCreate, AuthorityCreate
    from app.services import organization_acceptance as service
    from tests import test_eipd_policy_shared_lock as locks

    state, row = prepared
    async with cases.client(state) as http:
        g = await grant(http, state, profile_a_id)
        async with _app_session_factory() as holder, _app_session_factory() as waiter:
            await rls._set_auth_user(holder, auth_a_id)
            await rls._set_auth_user(waiter, auth_a_id)
            pid = await waiter.scalar(text("SELECT pg_backend_pid()"))
            args = (state[3], state[0], UUID(state[1]["id"]))
            revoke = AuthorityCreate.model_validate(
                designation(profile_a_id, revision=1, action="revocar")
            )
            accept = AcceptanceCreate.model_validate(decision(g["id"]))
            if revoke_wins:
                await service.designate(holder, *args, profile_a_id, revoke)
                task = asyncio.create_task(
                    service.record(waiter, *args, UUID(row["id"]), profile_a_id, accept)
                )
            else:
                await service.record(
                    holder, *args, UUID(row["id"]), profile_a_id, accept
                )
                task = asyncio.create_task(
                    service.designate(waiter, *args, profile_a_id, revoke)
                )
            try:
                await locks.blocked(holder, pid)
                assert not task.done()
                await holder.commit()
                if revoke_wins:
                    with pytest.raises(HTTPException) as error:
                        await asyncio.wait_for(task, 5)
                    assert error.value.status_code == 403
                    await waiter.rollback()
                else:
                    result = await asyncio.wait_for(task, 5)
                    assert result.action == "revocar"
                    await waiter.commit()
            finally:
                await holder.rollback()
                await locks.stop(task)
                await waiter.rollback()
        out = (await http.get(events(state, row))).json()
        assert len(out) == (0 if revoke_wins else 1)
        if out:
            assert not out[0]["faculty_current"] and not out[0]["authorizes_action"]


async def test_grant_cannot_bypass_membership_loss_and_can_be_revoked(
    prepared, profile_a_id, _session_factory
):
    state, row = prepared
    async with cases.client(state) as http:
        g = await grant(http, state, profile_a_id)
        async with _session_factory() as db:
            await db.execute(
                update(Membership)
                .where(
                    Membership.profile_id == profile_a_id,
                    Membership.organization_id == state[3],
                )
                .values(role=UserRole.viewer)
            )
            await db.commit()
        try:
            assert (
                await http.post(events(state, row), json=decision(g["id"]))
            ).status_code == 403
        finally:
            async with _session_factory() as db:
                await db.execute(
                    update(Membership)
                    .where(
                        Membership.profile_id == profile_a_id,
                        Membership.organization_id == state[3],
                    )
                    .values(role=UserRole.owner)
                )
                await db.commit()
        assert (
            await http.post(
                base(state) + "/authority",
                json=designation(profile_a_id, revision=1, action="revocar"),
            )
        ).status_code == 201


async def test_new_history_blocks_resolution_delete_and_migration_downgrade(
    prepared, profile_a_id, _session_factory
):
    import importlib.util
    from pathlib import Path

    from alembic.migration import MigrationContext
    from alembic.operations import Operations

    state, row = prepared
    async with cases.client(state) as http:
        g = await grant(http, state, profile_a_id)
        assert (
            await http.post(events(state, row), json=decision(g["id"]))
        ).status_code == 201
    async with _session_factory() as db:
        with pytest.raises(DBAPIError):
            async with db.begin_nested():
                await db.execute(
                    text("DELETE FROM eipd_child_resolutions WHERE id=:id"),
                    {"id": UUID(row["id"])},
                )
        spec = importlib.util.spec_from_file_location(
            "organization_acceptance_migration",
            Path(__file__).parents[1]
            / "alembic/versions/d16a3b7c8e52_organization_acceptance.py",
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        connection = await db.connection()

        def downgrade(sync):
            with Operations.context(MigrationContext.configure(sync)):
                module.downgrade()

        with pytest.raises(RuntimeError, match="historial de aceptacion"):
            await connection.run_sync(downgrade)
