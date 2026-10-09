"""Persistencia HTTP de investigacion con PostgreSQL y runtime RLS."""

from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.main import app
from app.services.research_binding import evaluate_research_association_v1
from tests import test_api_licitud as api

rat_m3 = api.rat_m3
pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_research_patch_binding_and_null(
    client_a, rat_m3, org_a_id, complete_lia_context
):
    treatment, payload = rat_m3
    lia, _ = complete_lia_context
    document = {
        "purpose_type": "cientifico",
        "purpose_description": "Gestión de clientes",
    }
    payload.update(
        research_assessment=document,
        legal_basis="interes_legitimo_art13d",
        lia_assessment=lia,
    )
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        response = await client.post(
            f"/licitud/treatments/{treatment}/assessments", json=payload
        )
        assert response.status_code == 201, response.text
        initial = response.json()
        url = f"/licitud/treatments/{treatment}/assessments/{initial['id']}"
        bound = initial["research_assessment"]
        assert bound["assessment"]["purpose_type"] == "cientifico"
        assert (
            evaluate_research_association_v1(
                bound,
                initial["rat_context_snapshot"],
                initial["legal_basis"],
                initial["lia_assessment"],
            ).result
            == "vigente"
        )
        assert (await client.get(url)).json()["research_assessment"] == bound
        response = await client.patch(
            url, json={"legal_basis": "consentimiento_art12", "lia_assessment": None}
        )
        assert response.status_code == 200, response.text
        changed = response.json()
        assert changed["research_assessment"] == bound
        assert (
            evaluate_research_association_v1(
                bound,
                changed["rat_context_snapshot"],
                changed["legal_basis"],
                changed["lia_assessment"],
            ).result
            == "requiere_revision"
        )
        response = await client.patch(
            url,
            json={
                "legal_basis": "interes_legitimo_art13d",
                "lia_assessment": lia,
                "research_assessment": document,
            },
        )
        assert response.status_code == 200, response.text
        current = response.json()
        assert (
            evaluate_research_association_v1(
                current["research_assessment"],
                current["rat_context_snapshot"],
                current["legal_basis"],
                current["lia_assessment"],
            ).result
            == "vigente"
        )
        assert not evaluate_research_association_v1(
            current["research_assessment"],
            current["rat_context_snapshot"],
            current["legal_basis"],
            current["lia_assessment"],
        ).can_confirm
        assert (await client.patch(url, json={"research_assessment": None})).json()[
            "research_assessment"
        ] is None
        assert (await client.get(url)).json()["research_assessment"] is None


@pytest.mark.parametrize("operation", ["create", "patch"])
async def test_client_binding_rejected(client_a, rat_m3, org_a_id, operation):
    treatment, payload = rat_m3
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        url = f"/licitud/treatments/{treatment}/assessments"
        if operation == "patch":
            created = await client.post(url, json=payload)
            assert created.status_code == 201
            url += "/" + created.json()["id"]
            response = await client.patch(
                url,
                json={
                    "research_assessment": {
                        "context_binding": {"context_hash": "a" * 64}
                    }
                },
            )
        else:
            payload["research_assessment"] = {
                "context_binding": {"context_hash": "a" * 64}
            }
            response = await client.post(url, json=payload)
        assert response.status_code == 422


@pytest.mark.parametrize("status", ["confirmado", "reemplazado"])
async def test_research_immutable_and_tenant(
    client_a, rat_m3, org_a_id, org_b_id, _session_factory, status
):
    treatment, payload = rat_m3
    payload["research_assessment"] = {"purpose_type": "cientifico"}
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        response = await client.post(
            f"/licitud/treatments/{treatment}/assessments", json=payload
        )
        assert response.status_code == 201, response.text
        original = response.json()
        url = f"/licitud/treatments/{treatment}/assessments/{original['id']}"
        async with AsyncClient(
            transport=ASGITransport(app=client_a),
            base_url="http://test",
            headers={"X-Organization-Id": str(org_b_id)},
        ) as other:
            assert (await other.get(url)).status_code == 403
            assert (
                await other.patch(url, json={"research_assessment": None})
            ).status_code == 403
        async with _session_factory() as db:
            await db.execute(
                text(
                    "UPDATE legal_assessments SET status='confirmado', confirmed_at=now(), confirmed_by=created_by WHERE id=:id"
                ),
                {"id": UUID(original["id"])},
            )
            await db.commit()
        if status == "reemplazado":
            replacement = await client.post(
                f"/licitud/treatments/{treatment}/assessments", json=payload
            )
            assert replacement.status_code == 201, replacement.text
            async with _session_factory() as db:
                await db.execute(
                    text(
                        "UPDATE legal_assessments SET status='reemplazado', replaced_at=now(), replaced_by_assessment_id=:replacement WHERE id=:id"
                    ),
                    {
                        "id": UUID(original["id"]),
                        "replacement": UUID(replacement.json()["id"]),
                    },
                )
                await db.commit()
        assert (
            await client.patch(url, json={"research_assessment": None})
        ).status_code == 409
        assert (await client.get(url)).json()["research_assessment"] == original[
            "research_assessment"
        ]


async def test_openapi_research_contracts():
    schemas = app.openapi()["components"]["schemas"]
    for name in ("LegalAssessmentDraftCreate", "LegalAssessmentDraftUpdate"):
        alternatives = schemas[name]["properties"]["research_assessment"]["anyOf"]
        assert {"$ref": "#/components/schemas/ResearchAssessmentV1"} in alternatives
    assert schemas["ResearchAssessmentV1"]["additionalProperties"] is False
    assert "context_binding" not in schemas["ResearchAssessmentV1"]["properties"]
    assert "context_binding" in schemas["BoundResearchAssessmentV1"]["properties"]
