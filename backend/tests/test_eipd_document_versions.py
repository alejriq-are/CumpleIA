"""General EIPD registration against PostgreSQL and the actual app_user role."""

import asyncio
from uuid import UUID, uuid4

import pytest
from sqlalchemy import delete, text, update
from sqlalchemy.exc import DBAPIError

from app.db.eipd_document_versions import EipdDocumentVersion as Version
from app.db.models import Membership, TreatmentPurpose, UserRole
from tests import test_eipd_child_successors as cases
from tests.test_navigation_applicability import payload as determination

rat_m3 = cases.rat_m3
saved = cases.saved
explicit_review_policy = cases.explicit_review_policy
pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest.fixture
async def ready(saved, explicit_review_policy, _session_factory):
    try:
        async with cases.client(saved) as http:
            base = cases.parent(saved)
            response = await http.patch(
                base,
                json={
                    "eipd_resolution_assessment": {
                        "document_reference": "SIMULADA-EIPD-5B1",
                        "notes": "[FICTICIA] Incompleto deliberadamente",
                    }
                },
            )
            assert response.status_code == 200, response.text
            url = base + "/applicability"
            response = await http.post(
                url, json=determination((await http.get(url)).json())
            )
            assert response.status_code == 201, response.text
        yield saved
    finally:
        async with _session_factory() as db:
            await db.execute(delete(Version).where(Version.treatment_id == saved[0]))
            await db.commit()


def endpoint(state):
    return cases.parent(state) + "/eipd-versions/v1"


def registration(preview):
    return dict(
        request_id=str(uuid4()),
        data_kind="ficticios",
        expected_source_hash=preview["source_hash"],
        expected_latest_version=preview["latest_version"],
        reason="[FICTICIA] Conservar antecedente incompleto",
    )


async def test_incomplete_registration_retry_and_frozen_history(ready):
    async with cases.client(ready) as http:
        url = endpoint(ready)
        response = await http.get(url + "/preview")
        assert response.status_code == 200, response.text
        v = response.json()
        assert v["latest_version"] == 0 and not v["can_confirm"]
        assert v["bundle"]["diagnostic"]["readiness"]
        body = registration(v)
        response = await http.post(url, json=body)
        assert response.status_code == 201, response.text
        first = response.json()
        assert first["version"] == 1 and not first["can_confirm"]
        assert first["bundle"]["saved_assessment"]["eipd_resolution_assessment"]
        assert (await http.post(url, json=body)).json() == first
        assert (await http.get(url + "/requests/" + body["request_id"])).json() == first
        assert (
            await http.post(url, json={**body, "reason": "Otro contenido"})
        ).status_code == 409
        response = await http.patch(
            cases.parent(ready),
            json={
                "eipd_resolution_assessment": {
                    "document_reference": "SIMULADA-EIPD-5B1",
                    "notes": "[FICTICIA] Segunda edición",
                }
            },
        )
        assert response.status_code == 200, response.text
        assert (await http.get(url + "/" + first["id"])).json() == first
        assert (await http.post(url, json=body)).json() == first
        assert (
            await http.post(url, json={**body, "request_id": str(uuid4())})
        ).status_code == 409
        second_body = registration((await http.get(url + "/preview")).json())
        second = (await http.post(url, json=second_body)).json()
        assert second["version"] == 2
        assert second["bundle"]["predecessor_id"] == first["id"]
        assert len((await http.get(url)).json()) == 2


async def test_concurrent_requests_only_one_version_and_same_request_retry(ready):
    async with cases.client(ready) as http:
        url = endpoint(ready)
        body = registration((await http.get(url + "/preview")).json())
        results = await asyncio.gather(
            http.post(url, json=body), http.post(url, json=body)
        )
        assert [r.status_code for r in results] == [201, 201], [r.text for r in results]
        assert results[0].json()["id"] == results[1].json()["id"]
        body = registration((await http.get(url + "/preview")).json())
        results = await asyncio.gather(
            http.post(url, json=body),
            http.post(url, json={**body, "request_id": str(uuid4())}),
        )
        assert sorted(r.status_code for r in results) == [201, 409], [
            r.text for r in results
        ]


async def test_closed_schema_and_current_determination_required(ready):
    async with cases.client(ready) as http:
        url = endpoint(ready)
        body = registration((await http.get(url + "/preview")).json())
        for patch in (
            {"data_kind": "reales"},
            {"reason": " "},
            {"document": {}},
            {"can_confirm": True},
        ):
            assert (await http.post(url, json={**body, **patch})).status_code == 422
        applicability = cases.parent(ready) + "/applicability"
        current = (await http.get(applicability)).json()
        v = determination(current)
        v["eipd"] = dict(state="no_corresponde", reason="[FICTICIA] Prueba")
        assert (await http.post(applicability, json=v)).status_code == 201
        assert (await http.post(url, json=body)).status_code == 409
        assert (await http.get(url + "/preview")).status_code == 409
        assert (await http.get(url)).json() == []


async def test_rls_immutable_and_viewer_denied(
    ready,
    org_b_id,
    auth_b_id,
    auth_a_id,
    profile_a_id,
    _session_factory,
    _app_session_factory,
):
    async with cases.client(ready) as http:
        url = endpoint(ready)
        body = registration((await http.get(url + "/preview")).json())
        response = await http.post(url, json=body)
        assert response.status_code == 201, response.text
        vid = response.json()["id"]
        assert (
            await http.get(
                url + "/" + vid, headers={"X-Organization-Id": str(org_b_id)}
            )
        ).status_code in (403, 404)
    async with _app_session_factory() as db:
        await db.execute(
            text("SELECT set_config('request.jwt.claim.sub',:sub,true)"),
            {"sub": str(auth_b_id)},
        )
        assert (
            await db.scalar(
                text("SELECT count(*) FROM eipd_document_versions WHERE id=:id"),
                {"id": UUID(vid)},
            )
            == 0
        )
        await db.rollback()
        await db.execute(
            text("SELECT set_config('request.jwt.claim.sub',:sub,true)"),
            {"sub": str(auth_a_id)},
        )
        for sql in (
            "UPDATE eipd_document_versions SET reason='changed' WHERE id=:id",
            "DELETE FROM eipd_document_versions WHERE id=:id",
            "TRUNCATE eipd_document_versions",
        ):
            with pytest.raises(DBAPIError):
                async with db.begin_nested():
                    await db.execute(text(sql), {"id": UUID(vid)})
        await db.rollback()
    async with _session_factory() as db:
        with pytest.raises(DBAPIError):
            async with db.begin_nested():
                await db.execute(
                    update(Version)
                    .where(Version.id == UUID(vid))
                    .values(reason="changed")
                )
        await db.rollback()
        await db.execute(
            update(Membership)
            .where(
                Membership.organization_id == ready[3],
                Membership.profile_id == profile_a_id,
            )
            .values(role=UserRole.viewer)
        )
        await db.commit()
    try:
        async with cases.client(ready) as http:
            assert (await http.post(url, json=body)).status_code == 403
            assert (await http.get(url + "/" + vid)).status_code == 200
    finally:
        async with _session_factory() as db:
            await db.execute(
                update(Membership)
                .where(
                    Membership.organization_id == ready[3],
                    Membership.profile_id == profile_a_id,
                )
                .values(role=UserRole.admin)
            )
            await db.commit()


async def test_same_request_key_across_series_is_controlled(
    ready, rat_m3, _session_factory
):
    tid, original_payload = rat_m3
    purpose = uuid4()
    async with _session_factory() as db:
        db.add(
            TreatmentPurpose(
                id=purpose,
                treatment_id=tid,
                organization_id=ready[3],
                purpose="[FICTICIA] Otra finalidad",
            )
        )
        await db.commit()
    async with cases.client(ready) as http:
        response = await http.post(
            f"/licitud/treatments/{tid}/assessments",
            json={
                **original_payload,
                "purpose_id": str(purpose),
                "eipd_resolution_assessment": {
                    "document_reference": "SIMULADA-OTRA",
                    "notes": "[FICTICIA] Concurrencia",
                },
            },
        )
        assert response.status_code == 201, response.text
        second = (tid, response.json(), ready[2], ready[3])
        applicability = cases.parent(second) + "/applicability"
        response = await http.post(
            applicability, json=determination((await http.get(applicability)).json())
        )
        assert response.status_code == 201, response.text
        url1, url2 = endpoint(ready), endpoint(second)
        body1 = registration((await http.get(url1 + "/preview")).json())
        body2 = registration((await http.get(url2 + "/preview")).json())
        body2["request_id"] = body1["request_id"]
        responses = await asyncio.gather(
            http.post(url1, json=body1), http.post(url2, json=body2)
        )
        assert sorted(r.status_code for r in responses) == [201, 409], [
            r.text for r in responses
        ]
        assert (
            len((await http.get(url1)).json()) + len((await http.get(url2)).json()) == 1
        )
