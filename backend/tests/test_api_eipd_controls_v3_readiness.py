"""Lectura HTTP V3 conservadora sin escrituras ni autoridad del cliente."""

from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError
from sqlalchemy import event, select

from app.db.models import EipdResolutionReview
from app.main import app
from app.schemas.licitud import EipdControlCompositionV3Out
from tests import test_api_licitud as api

rat_m3 = api.rat_m3
pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest.mark.parametrize("with_research", [True, False])
async def test_readonly_v3_and_tenant_boundary(
    client_a,
    rat_m3,
    org_a_id,
    org_b_id,
    complete_lia_context,
    _session_factory,
    _app_engine,
    with_research,
):
    treatment, payload = rat_m3
    lia, _ = complete_lia_context
    if with_research:
        payload.update(
            legal_basis="interes_legitimo_art13d",
            lia_assessment=lia,
            research_assessment={
                "purpose_type": "cientifico",
                "purpose_description": "Gestion de clientes",
            },
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
        statements = []

        def record(_conn, _cursor, statement, _parameters, _context, _many):
            statements.append(statement)

        event.listen(_app_engine.sync_engine, "before_cursor_execute", record)
        try:
            response = await client.get(url + "/readiness")
        finally:
            event.remove(_app_engine.sync_engine, "before_cursor_execute", record)
        assert response.status_code == 200, response.text
        data = response.json()
        assert not any(
            s.lstrip().upper().startswith(("INSERT", "UPDATE", "DELETE"))
            for s in statements
        )
        assert (
            sum(
                "eipd_resolution_reviews" in s
                and s.lstrip().upper().startswith("SELECT")
                for s in statements
            )
            == 1
        )
        controls = data["eipd_controls_v3"]
        if with_research:
            assert (
                controls["evaluation_version"] == 3 and controls["can_confirm"] is False
            )
            assert controls["detection_v3"]["can_continue"] is False
            assert (
                controls["detection_v3"]["frontier"]["research_association"]["result"]
                == "vigente"
            )
            assert controls["policy"]["policy_hash"] is None
            assert "politica_no_disponible" in {
                i["code"] for i in controls["confirmation_blockers"]
            }
            assert "investigacion_confirmacion_bloqueada" in {
                i["code"] for i in controls["confirmation_blockers"]
            }
            assert EipdControlCompositionV3Out.model_validate(controls)
            for field, value in [
                ("evaluation_version", 2),
                ("can_confirm", True),
                ("approved", True),
            ]:
                with pytest.raises(ValidationError):
                    EipdControlCompositionV3Out.model_validate(
                        dict(controls, **{field: value})
                    )
            assert (
                await client.get(
                    url + "/readiness?activation=habilitada&can_confirm=true"
                )
            ).json() == data
            assert (await client.post(url + "/confirm")).status_code == 400
            stale = await client.patch(
                url,
                json={"legal_basis": "consentimiento_art12", "lia_assessment": None},
            )
            assert stale.status_code == 200
            after = (await client.get(url + "/readiness")).json()["eipd_controls_v3"]
            assert (
                after["detection_v3"]["frontier"]["research_association"]["result"]
                == "requiere_revision"
            )
            assert not after["can_confirm"]
            assert (await client.get(url)).json()["research_assessment"] == original[
                "research_assessment"
            ]
        else:
            assert controls is None
            assert (await client.get(url)).json() == original
        assert (
            await client.get(
                url + "/readiness", headers={"X-Organization-Id": str(org_b_id)}
            )
        ).status_code == 403
        async with _session_factory() as db:
            assert not (
                await db.scalars(
                    select(EipdResolutionReview).where(
                        EipdResolutionReview.assessment_id == UUID(original["id"])
                    )
                )
            ).all()


async def test_openapi_closed_v3():
    schemas = app.openapi()["components"]["schemas"]
    for name in (
        "EipdControlCompositionV3Out",
        "EipdReadinessV3Out",
        "EipdFrontierReadinessV2Out",
        "EipdResolutionDocumentVersionedOut",
    ):
        assert schemas[name]["additionalProperties"] is False
    assert (
        schemas["EipdControlCompositionV3Out"]["properties"]["evaluation_version"][
            "const"
        ]
        == 3
    )
    assert "eipd_controls_v3" in schemas["LegalAssessmentReadinessOut"]["properties"]
