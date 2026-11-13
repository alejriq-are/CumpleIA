"""Visibilidad HTTP de identidad auditada; eventos solo como fixtures aisladas."""

from uuid import UUID

import pytest
from sqlalchemy import event, select

from app.db.models import EipdResolutionReview
from app.main import app
from app.services.eipd_resolution_binding_v2 import EipdResolutionContextV2
from app.services.eipd_review_metadata import build_eipd_review_context_metadata_v1
from tests import test_api_eipd_resolution as api
from tests.eipd_selected_policy_fixtures import (
    explicit_review_policy as explicit_review_policy,
)

rat_m3 = api.rat_m3
resolution_rat = api.resolution_rat


@pytest.mark.parametrize(
    "mode", ["none", "legacy", "current", "stale", "negative_latest"]
)
async def test_latest_metadata_readonly_no_fallback_and_no_authority(
    client_a,
    resolution_rat,
    org_a_id,
    org_b_id,
    profile_a_id,
    _session_factory,
    _app_engine,
    mode,
):
    treatment, payload = resolution_rat
    async with api.client_for(client_a, org_a_id) as client:
        created = await client.post(
            f"/licitud/treatments/{treatment}/assessments",
            json={
                **payload,
                "research_assessment": {"purpose_type": "cientifico"},
                "eipd_resolution_assessment": {"document_reference": "TEST: EIPD152"},
            },
        )
        assert created.status_code == 201, created.text
        original = created.json()
        url = f"/licitud/treatments/{treatment}/assessments/{original['id']}"
        ctx = {
            k: original[k]
            for k in EipdResolutionContextV2.model_fields
            if k != "context_schema_version"
        }
        metadata = build_eipd_review_context_metadata_v1(
            original["eipd_resolution_assessment"], ctx
        )
        rid = None
        if mode != "none":
            async with _session_factory() as db:
                row = EipdResolutionReview(
                    organization_id=org_a_id,
                    assessment_id=UUID(original["id"]),
                    created_by=profile_a_id,
                    decision="continuar",
                    rationale="TEST: historia sintetica",
                    review_reference="TEST: REV152",
                    document_hash=metadata.document_hash,
                    context_hash=metadata.context_hash,
                    review_context_metadata=(
                        metadata.model_dump(mode="json") if mode != "legacy" else None
                    ),
                )
                db.add(row)
                await db.flush()
                rid = str(row.id)
                await db.commit()
            if mode == "negative_latest":
                async with _session_factory() as db:
                    row = EipdResolutionReview(
                        organization_id=org_a_id,
                        assessment_id=UUID(original["id"]),
                        created_by=profile_a_id,
                        decision="no_continuar",
                        rationale="TEST: ultima negativa",
                        review_reference="TEST: REV152B",
                        document_hash=metadata.document_hash,
                        context_hash=metadata.context_hash,
                    )
                    db.add(row)
                    await db.flush()
                    rid = str(row.id)
                    await db.commit()
        if mode == "stale":
            changed = await client.patch(
                url, json={"research_assessment": {"purpose_type": "estadistico"}}
            )
            assert changed.status_code == 200
        before = (await client.get(url)).json()
        statements = []

        def record(_conn, _cursor, statement, _parameters, _context, _many):
            statements.append(statement)

        event.listen(_app_engine.sync_engine, "before_cursor_execute", record)
        try:
            response = await client.get(url + "/readiness")
        finally:
            event.remove(_app_engine.sync_engine, "before_cursor_execute", record)
        assert response.status_code == 200, response.text
        assert (
            sum(
                "eipd_resolution_reviews" in s
                and s.lstrip().upper().startswith("SELECT")
                for s in statements
            )
            == 1
        )
        assert not any(
            s.lstrip().upper().startswith(("INSERT", "UPDATE", "DELETE"))
            for s in statements
        )
        data = response.json()["eipd_controls_v3"]
        assert (
            data["review_context_metadata_status"]
            == {
                "none": "sin_revision",
                "legacy": "sin_metadatos",
                "current": "vigente",
                "stale": "obsoleta",
                "negative_latest": "sin_metadatos",
            }[mode]
        )
        if mode in ("current", "stale"):
            assert data["latest_review_context_metadata"] == metadata.model_dump(
                mode="json"
            )
        else:
            assert data["latest_review_context_metadata"] is None
        if rid:
            assert data["review_state"]["latest_review"]["id"] == rid
        if mode == "negative_latest":
            assert data["review_state"]["latest_review"]["decision"] == "no_continuar"
        if mode in ("legacy", "negative_latest", "stale"):
            assert (
                "metadatos_revision_obsoletos"
                if mode == "stale"
                else "revision_sin_metadatos_contexto"
            ) in {i["code"] for i in data["confirmation_blockers"]}
        assert not data["can_confirm"] and data["confirmation_blockers"]
        rejected = await client.post(
            url + "/eipd-resolution/reviews",
            json={
                "decision": "continuar",
                "rationale": "TEST: rechazo",
                "review_reference": "TEST: nueva",
            },
        )
        assert rejected.status_code == 409
        assert (
            rejected.json()["detail"]["code"] == "resolucion_eipd_v2_revision_pendiente"
        )
        assert (await client.get(url)).json() == before
        assert (
            await client.get(
                url + "/readiness", headers={"X-Organization-Id": str(org_b_id)}
            )
        ).status_code == 403
        async with _session_factory() as db:
            rows = (
                await db.scalars(
                    select(EipdResolutionReview).where(
                        EipdResolutionReview.assessment_id == UUID(original["id"])
                    )
                )
            ).all()
            assert len(rows) == (
                0 if mode == "none" else 2 if mode == "negative_latest" else 1
            )


async def test_openapi_metadata_output_only():
    schemas = app.openapi()["components"]["schemas"]
    assert schemas["EipdReviewContextMetadataV1"]["additionalProperties"] is False
    assert (
        "latest_review_context_metadata"
        in schemas["EipdControlCompositionV3Out"]["properties"]
    )
    assert (
        "review_context_metadata" not in schemas["EipdResolutionReviewIn"]["properties"]
    )
