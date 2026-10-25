"""Actual runtime-role roundtrips, append-only history and concurrency for navigation."""

from uuid import uuid4

import pytest
from sqlalchemy import text, update
from sqlalchemy.exc import DBAPIError

from app.db.models import Membership, UserRole
from tests import test_eipd_child_successors as cases

rat_m3 = cases.rat_m3
saved = cases.saved
pytestmark = pytest.mark.asyncio(loop_scope="session")


def payload(v, **patch):
    return dict(
        data_kind="ficticios",
        request_id=str(uuid4()),
        expected_revision=v["revision"],
        context_hash=v["context_hash"],
        eipd=dict(state="corresponde", reason="PRUEBA revisión manual"),
        infancia=dict(state="pendiente", reason=""),
        **patch,
    )


async def test_roundtrip_independent_history_and_idempotence(saved):
    async with cases.client(saved) as http:
        base = cases.parent(saved)
        url = base + "/applicability"
        initial = (await http.get(url)).json()
        assert initial["revision"] == 0 and not initial["current"]
        document = (await http.get(base)).json()
        body = payload(initial)
        response = await http.post(url, json=body)
        assert response.status_code == 201, response.text
        first = response.json()
        assert first["current"] and first["eipd"]["state"] == "corresponde"
        assert first["infancia"]["state"] == "pendiente" and not first["can_confirm"]
        assert (await http.post(url, json=body)).json()["revision"] == 1
        response = await http.post(
            url, json={**body, "eipd": dict(state="no_corresponde", reason="PRUEBA")}
        )
        assert response.status_code == 409
        second = payload(first)
        second["eipd"] = dict(
            state="informacion_insuficiente", reason="PRUEBA antecedentes"
        )
        second["infancia"] = dict(state="corresponde", reason="PRUEBA alcance")
        response = await http.post(url, json=second)
        assert response.status_code == 201, response.text
        result = (await http.get(url)).json()
        assert result["revision"] == 2 and len(result["history"]) == 2
        assert result["history"][0]["eipd"]["state"] == "corresponde"
        assert (
            result["infancia"]["state"] == "corresponde"
            and result["eipd"]["state"] == "informacion_insuficiente"
        )
        assert (await http.get(base)).json() == document
        assert (
            await http.post(url, json={**body, "request_id": str(uuid4())})
        ).status_code == 409
        summary = (await http.get(base.rsplit("/", 1)[0])).json()
        assert summary[0]["series_id"] == document["series_id"]


@pytest.mark.parametrize(
    "state", ["corresponde", "no_corresponde", "informacion_insuficiente"]
)
async def test_reason_required_and_closed_schema(saved, state):
    async with cases.client(saved) as http:
        url = cases.parent(saved) + "/applicability"
        v = (await http.get(url)).json()
        body = payload(v)
        body["infancia"] = dict(state=state, reason=" ")
        assert (await http.post(url, json=body)).status_code == 422
        body["infancia"]["reason"] = "PRUEBA"
        body["can_confirm"] = True
        assert (await http.post(url, json=body)).status_code == 422


async def test_wrong_context_and_fictitious_only(saved):
    async with cases.client(saved) as http:
        url = cases.parent(saved) + "/applicability"
        v = (await http.get(url)).json()
        body = payload(v)
        assert (
            await http.post(url, json={**body, "context_hash": "f" * 64})
        ).status_code == 409
        assert (
            await http.post(url, json={**body, "data_kind": "reales"})
        ).status_code == 422
        assert (
            await http.get(
                f"/licitud/treatments/{uuid4()}/assessments/{saved[1]['id']}/applicability"
            )
        ).status_code == 404


async def test_tenant_rls_and_viewer(
    saved, org_b_id, auth_b_id, profile_a_id, _app_session_factory, _session_factory
):
    async with cases.client(saved) as http:
        url = cases.parent(saved) + "/applicability"
        v = (await http.get(url)).json()
        response = await http.post(url, json=payload(v))
        assert response.status_code == 201, response.text
        assert (
            await http.get(url, headers={"X-Organization-Id": str(org_b_id)})
        ).status_code in (403, 404)
        assert (
            await http.post(
                url,
                json=payload(response.json()),
                headers={"X-Organization-Id": str(org_b_id)},
            )
        ).status_code in (403, 404)
    async with _app_session_factory() as db:
        await db.execute(
            text("SELECT set_config('request.jwt.claim.sub',:sub,true)"),
            {"sub": str(auth_b_id)},
        )
        assert (
            await db.scalar(
                text(
                    "SELECT count(*) FROM assessment_support_records WHERE assessment_id=:aid AND kind='applicability'"
                ),
                {"aid": saved[1]["id"]},
            )
            == 0
        )
        with pytest.raises(DBAPIError):
            async with db.begin_nested():
                await db.execute(
                    text(
                        "UPDATE assessment_support_records SET revision=99 WHERE kind='applicability'"
                    )
                )
    async with _session_factory() as db:
        await db.execute(
            update(Membership)
            .where(
                Membership.organization_id == saved[3],
                Membership.profile_id == profile_a_id,
            )
            .values(role=UserRole.viewer)
        )
        await db.commit()
    try:
        async with cases.client(saved) as http:
            assert (await http.get(url)).status_code == 200
            assert (await http.post(url, json=payload(v))).status_code == 403
    finally:
        async with _session_factory() as db:
            await db.execute(
                update(Membership)
                .where(
                    Membership.organization_id == saved[3],
                    Membership.profile_id == profile_a_id,
                )
                .values(role=UserRole.owner)
            )
            await db.commit()


async def test_scope_change_requires_review_and_keeps_history(saved, _session_factory):
    from app.db.models import LegalAssessment

    async with cases.client(saved) as http:
        base = cases.parent(saved)
        url = base + "/applicability"
        first = (
            await http.post(url, json=payload((await http.get(url)).json()))
        ).json()
        original = (await http.get(base)).json()
        # Simulate the saved snapshot advancing, without changing any prior determination.
        context = {
            **original["rat_context_snapshot"],
            "data_flow_description": "PRUEBA alcance modificado",
        }
        async with _session_factory() as db:
            await db.execute(
                update(LegalAssessment)
                .where(LegalAssessment.id == saved[1]["id"])
                .values(rat_context_snapshot=context)
            )
            await db.commit()
        changed = (await http.get(url)).json()
        assert not changed["current"] and changed["revision"] == first["revision"]
        assert changed["history"] == first["history"]
        assert changed["eipd"] == first["eipd"]
        assert changed["context_hash"] != first["context_hash"]
        assert (await http.post(url, json=payload(first))).status_code == 409
        reviewed = await http.post(url, json=payload(changed))
        assert reviewed.status_code == 201, reviewed.text
        assert reviewed.json()["current"] and reviewed.json()["revision"] == 2
        assert (await http.get(base)).json()["child_adolescent_assessment"] == original[
            "child_adolescent_assessment"
        ]


async def test_simultaneous_writes_keep_one_revision(saved):
    import asyncio

    async with cases.client(saved) as http:
        url = cases.parent(saved) + "/applicability"
        initial = (await http.get(url)).json()
        responses = await asyncio.gather(
            http.post(url, json=payload(initial)), http.post(url, json=payload(initial))
        )
        assert sorted(r.status_code for r in responses) == [201, 409]
        assert (await http.get(url)).json()["revision"] == 1
