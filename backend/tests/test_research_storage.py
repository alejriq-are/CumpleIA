from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.db.models import LegalAssessment
from tests import test_api_licitud as api

rat_m3 = api.rat_m3
pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_research_column_nullable_check_and_runtime_grants(_session_factory):
    async with _session_factory() as db:
        row = (
            await db.execute(
                text(
                    "SELECT is_nullable,data_type FROM information_schema.columns WHERE table_name='legal_assessments' AND column_name='research_assessment'"
                )
            )
        ).one()
        assert tuple(row) == ("YES", "jsonb")
        assert await db.scalar(
            text(
                "SELECT has_column_privilege('app_user','legal_assessments','research_assessment','SELECT,INSERT,UPDATE')"
            )
        )
        assert await db.scalar(
            text(
                "SELECT relrowsecurity FROM pg_class WHERE oid='legal_assessments'::regclass"
            )
        )
        assert (
            await db.scalar(
                text(
                    "SELECT count(*) FROM pg_constraint WHERE conrelid='legal_assessments'::regclass AND contype='c' AND pg_get_constraintdef(oid) LIKE '%jsonb_typeof(research_assessment)%'"
                )
            )
            == 1
        )
    assert LegalAssessment.__table__.c.research_assessment.nullable


async def test_storage_defaults_null_and_rejects_nonobject(
    client_a, rat_m3, org_a_id, _session_factory
):
    treatment_id, payload = rat_m3
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        response = await client.post(
            f"/licitud/treatments/{treatment_id}/assessments", json=payload
        )
        assert response.status_code == 201, response.text
    identity = UUID(response.json()["id"])
    async with _session_factory() as db:
        assert await db.scalar(
            text(
                "SELECT research_assessment IS NULL FROM legal_assessments WHERE id=:id"
            ),
            {"id": identity},
        )
        for invalid in ("[]", '"text"', "42", "true", "null"):
            with pytest.raises(IntegrityError):
                async with db.begin_nested():
                    await db.execute(
                        text(
                            "UPDATE legal_assessments SET research_assessment=CAST(:value AS jsonb) WHERE id=:id"
                        ),
                        {"value": invalid, "id": identity},
                    )
        await db.execute(
            text(
                "UPDATE legal_assessments SET research_assessment=CAST(:value AS jsonb) WHERE id=:id"
            ),
            {"value": '{"assessment": {}, "context_binding": {}}', "id": identity},
        )
        assert (
            await db.scalar(
                text("SELECT research_assessment FROM legal_assessments WHERE id=:id"),
                {"id": identity},
            )
        )["assessment"] == {}
        await db.rollback()
    # SQL limita a objeto; contrato completo sera validado por servicio/API posterior.
