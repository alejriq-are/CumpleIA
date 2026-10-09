"""Persistencia HTTP de investigacion con PostgreSQL y runtime RLS."""

from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.db.models import TreatmentDataSource
from app.main import app
from app.services.research_binding import evaluate_research_association_v1
from tests import test_api_licitud as api
from tests import test_services_research as research_cases

rat_m3 = api.rat_m3
context = research_cases.context
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


async def test_research_readiness_complete_stale_and_readonly(
    client_a, rat_m3, org_a_id, context, _session_factory
):
    treatment, payload = rat_m3
    document, _, lia = context
    async with _session_factory() as db:
        db.add(
            TreatmentDataSource(
                organization_id=org_a_id,
                treatment_id=treatment,
                source_type="titular",
                is_public_source=False,
            )
        )
        await db.commit()
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
        created = await client.post(
            f"/licitud/treatments/{treatment}/assessments", json=payload
        )
        assert created.status_code == 201, created.text
        original = created.json()
        url = f"/licitud/treatments/{treatment}/assessments/{original['id']}"
        for _ in range(2):
            response = await client.get(url + "/readiness")
            assert response.status_code == 200, response.text
            result = response.json()
            assert result["research"]["result"] == "completo", result["research"]
            assert result["research"]["association_result"] == "vigente"
            assert result["research"]["association_issues"] == []
            assert result["research"]["can_confirm"] is False
            assert "investigacion_confirmacion_bloqueada" in {
                b["code"] for b in result["confirmation_blockers"]
            }
        assert (await client.get(url)).json() == original
        rejected = await client.post(url + "/confirm")
        assert rejected.status_code == 409, rejected.text
        assert (await client.get(url)).json() == original
        lia["conclusion"]["balancing_summary"] += " revisada"
        changed = await client.patch(url, json={"lia_assessment": lia})
        assert changed.status_code == 200, changed.text
        stale = (await client.get(url + "/readiness")).json()["research"]
        assert stale["result"] == "completo"
        assert stale["association_result"] == "requiere_revision"
        assert "asociacion_contexto_obsoleta" in stale["association_issues"]
        assert (await client.get(url)).json()["research_assessment"] == original[
            "research_assessment"
        ]
        current = await client.patch(url, json={"research_assessment": document})
        assert current.status_code == 200
        assert (await client.get(url + "/readiness")).json()["research"][
            "association_result"
        ] == "vigente"
        document.pop("evidence")
        assert (
            await client.patch(url, json={"research_assessment": document})
        ).status_code == 200
        assert (await client.get(url + "/readiness")).json()["research"][
            "result"
        ] == "incompleto"
        assert (
            await client.patch(url, json={"research_assessment": None})
        ).status_code == 200
        assert (await client.get(url + "/readiness")).json()["research"] is None


async def test_declared_research_missing_document(client_a, rat_m3, org_a_id):
    treatment, payload = rat_m3
    for declaration in payload["special_conditions"]["declarations"]:
        if (
            declaration["question_id"]
            == "fines_historicos_estadisticos_cientificos_investigacion"
        ):
            declaration["answer"] = "si"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        created = await client.post(
            f"/licitud/treatments/{treatment}/assessments", json=payload
        )
        assert created.status_code == 201, created.text
        url = f"/licitud/treatments/{treatment}/assessments/{created.json()['id']}"
        response = await client.get(url + "/readiness")
        assert response.status_code == 200, response.text
        ready = response.json()
        assert ready["research"]["can_confirm"] is False
        assert "expediente_ausente" in {i["code"] for i in ready["research"]["issues"]}
        assert ready["research"]["association_issues"] == ["asociacion_ausente"]
        assert "investigacion_confirmacion_bloqueada" in {
            i["code"] for i in ready["confirmation_blockers"]
        }
        assert (await client.get(url)).json()["research_assessment"] is None


@pytest.mark.parametrize("remove", [False, True])
async def test_successor_api_final_context_and_omission(
    client_a, rat_m3, org_a_id, complete_lia_context, negative_controls, remove
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
        created = await client.post(
            f"/licitud/treatments/{treatment}/assessments", json=payload
        )
        assert created.status_code == 201, created.text
        initial = created.json()
        url = f"/licitud/treatments/{treatment}/assessments/{initial['id']}"
        assert initial["special_conditions"]["context_binding"]["schema_version"] == 11
        assert initial["eipd_screening"]["context_binding"]["schema_version"] == 12
        ready = (await client.get(url + "/readiness")).json()
        assert ready["special"]["context_current"] and ready["eipd"]["context_current"]
        replacement = (
            None if remove else {**document, "public_interest_analysis": "Revision"}
        )
        changed = await client.patch(
            url,
            json={
                "research_assessment": replacement,
                "legal_basis": "consentimiento_art12",
                "lia_assessment": None,
            },
        )
        assert changed.status_code == 200, changed.text
        result = changed.json()
        assert result["special_conditions"] == initial["special_conditions"]
        assert result["eipd_screening"] == initial["eipd_screening"]
        ready = (await client.get(url + "/readiness")).json()
        assert (
            not ready["special"]["context_current"]
            and not ready["eipd"]["context_current"]
        )
        combined = await client.patch(
            url,
            json={
                "research_assessment": document,
                "legal_basis": "interes_legitimo_art13d",
                "lia_assessment": lia,
                **negative_controls,
            },
        )
        assert combined.status_code == 200, combined.text
        final = combined.json()
        ready = (await client.get(url + "/readiness")).json()
        assert ready["special"]["context_current"] and ready["eipd"]["context_current"]
        assert "investigacion_confirmacion_bloqueada" in {
            i["code"] for i in ready["confirmation_blockers"]
        }
        assert (await client.get(url)).json() == final
        specials = dict(
            negative_controls["special_conditions"], notes="Revision documental"
        )
        single = await client.patch(url, json={"special_conditions": specials})
        assert single.status_code == 200
        assert single.json()["eipd_screening"] == final["eipd_screening"]
        assert not (await client.get(url + "/readiness")).json()["eipd"][
            "context_current"
        ]
        before = (await client.get(url)).json()
        invalid = await client.patch(
            url,
            json={
                "research_assessment": None,
                "special_conditions": {
                    "conditions": [
                        {
                            "regime_id": "investigacion_art16quinquies",
                            "authorization_route": "excepcion_legal",
                            "data_category_codes": ["fuera"],
                            "data_subject_codes": ["clientes"],
                        }
                    ]
                },
            },
        )
        assert invalid.status_code in (400, 422), invalid.text
        assert (await client.get(url)).json() == before
