"""5D.1 registration via the real API and restricted PostgreSQL role."""

import asyncio
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from tests import test_eipd_child_successors as cases
from tests import test_eipd_document_versions as versions
from tests.test_assessment_support_api import annex_payload
from tests.test_eipd_version_reviews import runtime

rat_m3 = cases.rat_m3
saved = cases.saved
pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest.fixture
async def assessment(saved, _session_factory):
    yield saved
    async with _session_factory() as db:
        await db.execute(
            text("DELETE FROM base_fundamento_versions WHERE treatment_id=:tid"),
            {"tid": saved[0]},
        )
        await db.commit()


def endpoint(state):
    return cases.parent(state) + "/base-fundamento-versions/v1"


async def test_pending_basis_and_alternatives_frozen(assessment):
    async with cases.client(assessment) as http:
        parent = cases.parent(assessment)
        url = endpoint(assessment)
        patch = await http.patch(
            parent,
            json={
                "legal_basis": None,
                "justification": "[FICTICIA] Se estudian alternativas",
                "consent_assessment": {"given_by": "titular"},
                "lia_assessment": {
                    "purpose_and_interest": {
                        "legitimate_interest": "[FICTICIA] Interés estudiado"
                    }
                },
            },
        )
        assert patch.status_code == 200, patch.text
        preview = (await http.get(url + "/preview")).json()
        bundle = preview["bundle"]
        assert bundle["primary_form"] is None
        assert any(
            r["code"] == "base_pendiente" and r["resolution"] is None
            for r in preview["favorable_requirements"]
        )
        assert set(bundle["alternatives"]) == {"consent_assessment", "lia_assessment"}
        assert any(
            f["code"] == "base_pendiente" for f in bundle["diagnostic"]["findings"]
        )
        body = versions.registration(preview)
        response = await http.post(url, json=body)
        assert response.status_code == 201, response.text
        first = response.json()
        assert first["version"] == 1 and first["can_confirm"] is False
        patch = await http.patch(parent, json={"legal_basis": "consentimiento_art12"})
        assert patch.status_code == 200, patch.text
        assert (await http.post(url, json=body)).json() == first
        assert (await http.get(url + "/requests/" + body["request_id"])).json() == first
        assert (await http.get(url + "/" + first["id"])).json() == first
        assert (
            await http.post(url, json=body | {"reason": "Cambio"})
        ).status_code == 409
        next_preview = (await http.get(url + "/preview")).json()
        assert next_preview["bundle"]["primary_form"]["kind"] == "consent_assessment"
        assert set(next_preview["bundle"]["alternatives"]) == {"lia_assessment"}
        assert next_preview["latest_version"] == 1
        assert len((await http.get(url)).json()) == 1


async def test_stale_preview_concurrency_and_annex_validation(assessment):
    async with cases.client(assessment) as http:
        url = endpoint(assessment)
        annex_id = str(uuid4())
        assert (
            await http.get(url + "/preview", params={"annex_ids": annex_id})
        ).status_code == 404
        assert (
            await http.get(
                url + "/preview",
                params=[
                    ("annex_ids", annex_id),
                    ("annex_ids", annex_id),
                ],
            )
        ).status_code == 422
        preview = (await http.get(url + "/preview")).json()
        patch = await http.patch(
            cases.parent(assessment), json={"justification": "[FICTICIA] Cambio"}
        )
        assert patch.status_code == 200, patch.text
        assert (
            await http.post(url, json=versions.registration(preview))
        ).status_code == 409
        preview = (await http.get(url + "/preview")).json()
        results = await asyncio.gather(
            *(http.post(url, json=versions.registration(preview)) for _ in range(2))
        )
        assert sorted(r.status_code for r in results) == [201, 409]


async def test_runtime_history_is_tenant_scoped_and_immutable(
    assessment,
    auth_a_id,
    auth_b_id,
    _app_session_factory,
):
    async with cases.client(assessment) as http:
        url = endpoint(assessment)
        preview = (await http.get(url + "/preview")).json()
        response = await http.post(url, json=versions.registration(preview))
        assert response.status_code == 201, response.text
        version = response.json()
    query = text("SELECT id FROM base_fundamento_versions WHERE id=CAST(:id AS uuid)")
    params = {"id": version["id"]}
    async with runtime(_app_session_factory, auth_b_id) as db:
        assert await db.scalar(query, params) is None
    with pytest.raises(DBAPIError):
        async with runtime(_app_session_factory, auth_a_id) as db:
            assert await db.scalar(query, params) is not None
            await db.execute(
                text(
                    "UPDATE base_fundamento_versions SET reason='Alterado' WHERE id=CAST(:id AS uuid)"
                ),
                params,
            )


async def test_only_selected_saved_annex_version_is_frozen(assessment):
    async with cases.client(assessment) as http:
        parent = cases.parent(assessment)
        url = endpoint(assessment)
        body = annex_payload() | {"section": "base", "risk_ids": [], "measure_ids": []}
        upload = await http.post(parent + "/annexes", json=body)
        assert upload.status_code == 201, upload.text
        selected = upload.json()["annexes"][0]
        assert (await http.get(url + "/preview")).json()["bundle"]["annexes"] == []
        preview = (
            await http.get(url + "/preview", params={"annex_ids": selected["id"]})
        ).json()
        response = await http.post(
            url, json=versions.registration(preview) | {"annex_ids": [selected["id"]]}
        )
        assert response.status_code == 201, response.text
        registered = response.json()
        assert registered["bundle"]["annexes"] == [
            {
                key: selected[key]
                for key in (
                    "id",
                    "revision",
                    "document_hash",
                    "sha256",
                    "reference",
                    "version",
                )
            }
        ]
        another = await http.post(
            parent + "/annexes", json=body | {"request_id": str(uuid4())}
        )
        assert another.status_code == 201, another.text
        assert len(another.json()["annexes"]) == 2
        assert (await http.get(url + "/" + registered["id"])).json() == registered
