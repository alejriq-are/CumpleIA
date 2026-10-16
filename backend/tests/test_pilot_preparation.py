"""Actas y operacion declaradas con fixtures; nunca aceptacion real."""

import pytest
from sqlalchemy import text

from tests import test_eipd_child_successors as cases
from tests import test_organization_acceptance as acts

rat_m3 = cases.rat_m3
saved = cases.saved
explicit_review_policy = cases.explicit_review_policy
prepared = cases.prepared
pytestmark = pytest.mark.asyncio(loop_scope="session")


def route(state):
    return cases.parent(state) + "/pilot-preparation/v1"


async def body(http, state, actor):
    g = await acts.grant(http, state, actor)
    dossier = (await http.get(cases.parent(state) + "/mvp-dossier/v1")).json()
    return dict(
        data_kind="ficticios",
        authority_id=g["id"],
        document_hashes={d["kind"]: d["content_hash"] for d in dossier["documents"]},
        review_decision="acepta",
        **{
            k: "PRUEBA: referencia declarada"
            for k in (
                "review_reference",
                "environment_reference",
                "access_reference",
                "restore_reference",
                "retention_reference",
                "support_reference",
                "incident_reference",
            )
        },
    )


async def test_complete_references_never_release_or_persist(
    prepared, profile_a_id, _session_factory
):
    state, _ = prepared
    async with cases.client(state) as http:
        p = await body(http, state, profile_a_id)
        before = (await http.get(cases.url(state) + "/policy")).json()
        r = await http.post(route(state), json=p)
        assert r.status_code == 200, r.text
        v = r.json()
        assert v["preparation_complete"] and not v["missing"]
        assert (
            v["actor_id"] == str(profile_a_id)
            and v["evidence_status"] == "declarada_no_verificada"
        )
        assert v["persistence"] == "simulacion_no_registrada"
        assert all(
            v[k] is False
            for k in (
                "mvp_ready",
                "allows_real_data",
                "can_confirm",
                "authorizes_action",
            )
        )
        assert (await http.get(cases.url(state) + "/policy")).json() == before
    async with _session_factory() as db:
        assert (
            await db.scalar(
                text("SELECT count(*) FROM organization_document_acceptances")
            )
            == 0
        )


@pytest.mark.parametrize(
    "field",
    [
        "review_reference",
        "environment_reference",
        "restore_reference",
        "incident_reference",
    ],
)
async def test_missing_reference_visible_not_complete(prepared, profile_a_id, field):
    state, _ = prepared
    async with cases.client(state) as http:
        p = await body(http, state, profile_a_id)
        p[field] = None
        v = (await http.post(route(state), json=p)).json()
        assert field in v["missing"] and not v["preparation_complete"]


async def test_revocation_and_changed_document_reject(prepared, profile_a_id):
    state, _ = prepared
    async with cases.client(state) as http:
        p = await body(http, state, profile_a_id)
        await http.post(
            cases.url(state) + "/resolutions",
            json={"data_kind": "ficticios", "document": {"notes": "PRUEBA sucesor"}},
        )
        assert (await http.post(route(state), json=p)).status_code == 409
        await acts.grant(http, state, profile_a_id, revision=1, action="revocar")
        assert (await http.post(route(state), json=p)).status_code == 403


@pytest.mark.parametrize(
    "change",
    [
        {"data_kind": "reales"},
        {"mvp_ready": True},
        {"actor_id": "a0000000-0000-0000-0000-000000000002"},
    ],
)
async def test_injected_real_or_server_fields_rejected(prepared, profile_a_id, change):
    state, _ = prepared
    async with cases.client(state) as http:
        p = await body(http, state, profile_a_id)
        assert (await http.post(route(state), json={**p, **change})).status_code == 422
