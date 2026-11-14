"""Lectura HTTP ficticia de metadatos V1/V2/null sin reconstruir historia."""

from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event

from tests import test_eipd_review_metadata_storage as old
from tests import test_eipd_review_metadata_v2_storage as successor

app_role_session = old.app_role_session
licitud_base_data = old.licitud_base_data
review_data = old.review_data


@pytest.fixture
async def stored(
    review_data, _app_session_factory, auth_a_id, org_a_id, profile_a_id, request
):
    version = request.param
    async with _app_session_factory() as db:
        await old.cases._set_auth_user(db, auth_a_id)
        if version is None:
            identity = review_data["review_a"]
        else:
            data = old.values(org_a_id, review_data["assessment_a"], profile_a_id)
            metadata = old.metadata(data) if version == 1 else successor.metadata(data)
            identity = await old.insert(db, data, metadata)
            await db.commit()
    return review_data["treatment_a"], review_data["assessment_a"], identity, version


@pytest.mark.parametrize("stored", [None, 1, 2], indirect=True)
async def test_v3_reads_original_identity_and_preserves_v2_contract(
    stored, client_a, org_a_id, org_b_id, _app_engine, review_data
):
    tid, aid, rid, version = stored
    url = f"/licitud/treatments/{tid}/assessments/{aid}/eipd-resolution/reviews/{rid}"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        statements = []

        def record(_conn, _cursor, statement, _params, _ctx, _many):
            statements.append(statement)

        event.listen(_app_engine.sync_engine, "before_cursor_execute", record)
        try:
            response = await client.get(url + "/v3")
        finally:
            event.remove(_app_engine.sync_engine, "before_cursor_execute", record)
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["response_schema_version"] == 3
        metadata = body["review_context_metadata"]
        assert (metadata["metadata_schema_version"] if metadata else None) == version
        assert not any(
            s.lstrip().upper().startswith(("INSERT", "UPDATE", "DELETE"))
            for s in statements
        )
        assert "can_confirm" not in body and "approved" not in body
        assert (await client.get(url + "/v3")).json() == body
        assert (
            await client.get(url + "/v3", headers={"X-Organization-Id": str(org_b_id)})
        ).status_code == 403
        wrong = f"/licitud/treatments/{uuid4()}/assessments/{aid}/eipd-resolution/reviews/{rid}/v3"
        assert (await client.get(wrong)).status_code == 404
        other_event = f"/licitud/treatments/{tid}/assessments/{aid}/eipd-resolution/reviews/{review_data['review_b']}/v3"
        assert (await client.get(other_event)).status_code == 404
        legacy = await client.get(url + "/v2")
        if version == 2:
            assert legacy.status_code == 409
            assert (
                legacy.json()["detail"]["code"]
                == "revision_eipd_metadata_v2_requiere_salida_v3"
            )
            assert metadata["representation_coverage"] == "contexto_v3"
        else:
            assert legacy.status_code == 200, legacy.text
            assert {**legacy.json(), "response_schema_version": 3} == body
