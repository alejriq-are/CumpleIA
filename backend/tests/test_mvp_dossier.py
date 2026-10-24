"""Expediente observado, sin actos reales ni cierre automatico de gates."""

from uuid import UUID, uuid4

import pytest
from sqlalchemy import text

from app.services.mvp_dossier import digest
from tests import test_eipd_child_successors as cases
from tests import test_organization_acceptance as acts

rat_m3 = cases.rat_m3
saved = cases.saved
explicit_review_policy = cases.explicit_review_policy
prepared = cases.prepared
pytestmark = pytest.mark.asyncio(loop_scope="session")


def path(state):
    return cases.parent(state) + "/mvp-dossier/v1"


async def test_bundle_exact_documents_sources_gates_and_hash(
    prepared, profile_a_id, _session_factory
):
    state, row = prepared
    async with cases.client(state) as http:
        g = await acts.grant(http, state, profile_a_id)
        assert (
            await http.post(acts.events(state, row), json=acts.decision(g["id"]))
        ).status_code == 201
        before = (await http.get(cases.url(state) + "/policy")).json()
        out = await http.get(path(state))
        assert out.status_code == 200, out.text
        v = out.json()
        assert [d["kind"] for d in v["documents"]] == ["rat", "licitud_lia", "eipd"]
        assert v["documents"][1]["content"]["id"] == state[1]["id"]
        assert v["documents"][2]["content"] == row
        assert len(v["documents"][2]["acceptance_events"]) == 1
        assert all(
            d["organization_acceptance"] == "sin_flujo" and not d["acceptance_events"]
            for d in v["documents"][:2]
        )
        for d in v["documents"]:
            assert d["content_hash"] == digest(d["content"])
        assert v["packet_hash"] == digest(
            {k: x for k, x in v.items() if k != "packet_hash"}
        )
        assert [x["status"] for x in v["release_gates"]] == [
            "alcance_definido",
            *(["pendiente"] * 4),
            "bloqueado",
            "bloqueado",
        ]
        assert all(
            x["legal_verifier"] is None
            and x["status"] == "consultada_sin_aceptacion_juridica"
            for x in v["official_sources"]
        )
        assert not any(
            v[k]
            for k in (
                "mvp_ready",
                "allows_real_data",
                "authorizes_action",
                "can_confirm",
            )
        )
        assert (
            v["activation"] == "deshabilitada"
            and v["data_provenance"] == "no_verificada"
        )
        assert (await http.get(cases.url(state) + "/policy")).json() == before
        assert (await http.post(cases.parent(state) + "/confirm")).status_code == 409
    async with _session_factory() as db:
        assert (
            await db.scalar(
                text(
                    "SELECT count(*) FROM organization_document_acceptances WHERE assessment_id=:aid"
                ),
                {"aid": UUID(state[1]["id"])},
            )
            == 1
        )


async def test_missing_resolution_is_explicit(saved):
    async with cases.client(saved) as http:
        v = (await http.get(path(saved))).json()
        d = v["documents"][2]
        assert (
            d["status"] == "sin_documento"
            and d["content"] is None
            and d["content_hash"] is None
        )
        assert not v["mvp_ready"]


async def test_changed_material_does_not_carry_acceptance(prepared, profile_a_id):
    state, row = prepared
    async with cases.client(state) as http:
        g = await acts.grant(http, state, profile_a_id)
        assert (
            await http.post(acts.events(state, row), json=acts.decision(g["id"]))
        ).status_code == 201
        assert (
            await http.patch(
                cases.parent(state),
                json={
                    "child_adolescent_assessment": {
                        "declared_groups": ["ninos_ninas"],
                        "notes": "PRUEBA cambio",
                    }
                },
            )
        ).status_code == 200
        v = (await http.get(path(state))).json()
        assert (
            v["documents"][2]["acceptance_events"][0]["material_status"] == "obsoleto"
        )
        new = (
            await http.post(
                cases.url(state) + "/resolutions",
                json={"data_kind": "ficticios", "document": {}},
            )
        ).json()
        v = (await http.get(path(state))).json()
        assert (
            v["documents"][2]["content"]["id"] == new["id"]
            and v["documents"][2]["acceptance_events"] == []
        )


async def test_foreign_tenant_and_wrong_parent(prepared, org_b_id):
    state, _ = prepared
    async with cases.client(state) as http:
        assert (
            await http.get(path(state), headers={"X-Organization-Id": str(org_b_id)})
        ).status_code in (403, 404)
        assert (
            await http.get(path(state).replace(state[1]["id"], str(uuid4())))
        ).status_code == 404


async def test_production_blocked(prepared, monkeypatch):
    from app.services import mvp_dossier

    state, _ = prepared
    monkeypatch.setattr(mvp_dossier.get_settings(), "environment", "production")
    async with cases.client(state) as http:
        assert (await http.get(path(state))).status_code == 409


async def test_viewer_can_read_but_suspended_subscription_cannot(
    prepared, profile_a_id, _session_factory
):
    from sqlalchemy import update

    from app.db.models import Membership, Subscription, UserRole

    state, _ = prepared
    async with _session_factory() as db:
        await db.execute(
            update(Membership)
            .where(
                Membership.organization_id == state[3],
                Membership.profile_id == profile_a_id,
            )
            .values(role=UserRole.viewer)
        )
        await db.commit()
    try:
        async with cases.client(state) as http:
            assert (await http.get(path(state))).status_code == 200
            async with _session_factory() as db:
                await db.execute(
                    update(Subscription)
                    .where(Subscription.organization_id == state[3])
                    .values(status="suspended")
                )
                await db.commit()
            assert (await http.get(path(state))).status_code == 402
    finally:
        async with _session_factory() as db:
            await db.execute(
                update(Membership)
                .where(
                    Membership.organization_id == state[3],
                    Membership.profile_id == profile_a_id,
                )
                .values(role=UserRole.owner)
            )
            await db.execute(
                update(Subscription)
                .where(Subscription.organization_id == state[3])
                .values(status="active")
            )
            await db.commit()
