"""Almacenamiento infancia con datos ficticios, RLS y restricciones SQL."""

import importlib.util
from pathlib import Path
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from alembic.migration import MigrationContext
from alembic.operations import Operations
from app.db.base import Base
from app.db.models import LegalAssessment
from tests import test_api_licitud as api

rat_m3 = api.rat_m3
pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_column_nullable_rls_and_constraints(_session_factory):
    async with _session_factory() as db:
        row = (
            await db.execute(
                text(
                    "SELECT is_nullable,data_type FROM information_schema.columns WHERE table_name='legal_assessments' AND column_name='child_adolescent_assessment'"
                )
            )
        ).one()
        assert tuple(row) == ("YES", "jsonb")
        assert await db.scalar(
            text(
                "SELECT has_column_privilege('app_user','legal_assessments','child_adolescent_assessment','SELECT,INSERT,UPDATE')"
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
                    "SELECT count(*) FROM pg_constraint WHERE conrelid='legal_assessments'::regclass AND pg_get_constraintdef(oid) LIKE '%child_adolescent_assessment%'"
                )
            )
            == 2
        )
    assert LegalAssessment.__table__.c.child_adolescent_assessment.nullable


@pytest.fixture
async def draft(client_a, rat_m3, org_a_id):
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
    return UUID(response.json()["id"])


async def test_old_draft_defaults_sql_null_and_rejects_nonobjects(
    draft, _session_factory
):
    async with _session_factory() as db:
        assert await db.scalar(
            text(
                "SELECT child_adolescent_assessment IS NULL FROM legal_assessments WHERE id=:id"
            ),
            {"id": draft},
        )
        for invalid in ("[]", '"PRUEBA"', "42", "true", "null"):
            with pytest.raises(IntegrityError):
                async with db.begin_nested():
                    await db.execute(
                        text(
                            "UPDATE legal_assessments SET child_adolescent_assessment=CAST(:value AS jsonb) WHERE id=:id"
                        ),
                        {"value": invalid, "id": draft},
                    )


async def test_internal_object_roundtrip_and_explicit_sql_null(draft, _session_factory):
    async with _session_factory() as db:
        row = await db.get(LegalAssessment, draft)
        row.child_adolescent_assessment = {
            "assessment": {"notes": "PRUEBA: material ficticio"},
            "context_binding": {},
        }
        await db.flush()
        db.expire(row)
        await db.refresh(row)
        assert row.child_adolescent_assessment["assessment"]["notes"].startswith(
            "PRUEBA"
        )
        row.child_adolescent_assessment = None
        await db.flush()
        assert await db.scalar(
            text(
                "SELECT child_adolescent_assessment IS NULL FROM legal_assessments WHERE id=:id"
            ),
            {"id": draft},
        )
        await db.rollback()


async def test_child_prevents_confirmed_status_in_sql(draft, _session_factory):
    async with _session_factory() as db:
        await db.execute(
            text(
                "UPDATE legal_assessments SET child_adolescent_assessment='{}'::jsonb WHERE id=:id"
            ),
            {"id": draft},
        )
        with pytest.raises(IntegrityError) as failure:
            async with db.begin_nested():
                await db.execute(
                    text(
                        "UPDATE legal_assessments SET status='confirmado',confirmed_at=clock_timestamp(),confirmed_by=created_by WHERE id=:id"
                    ),
                    {"id": draft},
                )
        expected = await db.scalar(
            text(
                "SELECT conname FROM pg_constraint WHERE conrelid='legal_assessments'::regclass AND pg_get_constraintdef(oid) LIKE '%child_adolescent_assessment%' AND pg_get_constraintdef(oid) LIKE '%confirmado%'"
            )
        )
        assert failure.value.orig.__cause__.constraint_name == expected
        assert (
            await db.scalar(
                text("SELECT status FROM legal_assessments WHERE id=:id"), {"id": draft}
            )
            == "borrador"
        )
        await db.rollback()


async def test_runtime_tenant_can_write_only_own_material(
    draft, _app_session_factory, auth_a_id, auth_b_id
):
    async with _app_session_factory() as db:
        assert await db.scalar(text("SELECT current_user")) == "app_user"
        await db.execute(
            text("SELECT set_config('request.jwt.claim.sub',:sub,true)"),
            {"sub": str(auth_a_id)},
        )
        own = await db.execute(
            text(
                "UPDATE legal_assessments SET child_adolescent_assessment='{}'::jsonb WHERE id=:id"
            ),
            {"id": draft},
        )
        assert own.rowcount == 1
        await db.commit()
    async with _app_session_factory() as db:
        await db.execute(
            text("SELECT set_config('request.jwt.claim.sub',:sub,true)"),
            {"sub": str(auth_b_id)},
        )
        assert (
            await db.scalar(
                text(
                    "SELECT child_adolescent_assessment FROM legal_assessments WHERE id=:id"
                ),
                {"id": draft},
            )
            is None
        )
        other = await db.execute(
            text(
                "UPDATE legal_assessments SET child_adolescent_assessment=NULL WHERE id=:id"
            ),
            {"id": draft},
        )
        assert other.rowcount == 0
        await db.rollback()


async def test_downgrade_refuses_to_drop_saved_documents(draft, _session_factory):
    path = (
        Path(__file__).parents[1]
        / "alembic/versions/a73d8e0c4b21_child_adolescent_document.py"
    )
    spec = importlib.util.spec_from_file_location("child_migration", path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    async with _session_factory() as db:
        await db.execute(
            text(
                "UPDATE legal_assessments SET child_adolescent_assessment='{}'::jsonb WHERE id=:id"
            ),
            {"id": draft},
        )
        connection = await db.connection()

        def try_downgrade(sync):
            with Operations.context(
                MigrationContext.configure(
                    sync, opts={"target_metadata": Base.metadata}
                )
            ):
                migration.downgrade()

        with pytest.raises(RuntimeError, match="existen documentos de infancia"):
            await connection.run_sync(try_downgrade)
        assert (
            await db.scalar(
                text(
                    "SELECT child_adolescent_assessment FROM legal_assessments WHERE id=:id"
                ),
                {"id": draft},
            )
            == {}
        )
        await db.rollback()


async def test_empty_downgrade_upgrade_restores_constraints_transactionally(
    _session_factory,
):
    path = (
        Path(__file__).parents[1]
        / "alembic/versions/a73d8e0c4b21_child_adolescent_document.py"
    )
    spec = importlib.util.spec_from_file_location("child_migration_roundtrip", path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    successor_path = (
        Path(__file__).parents[1]
        / "alembic/versions/b84e9f1a5c32_child_eipd_successors.py"
    )
    successor_spec = importlib.util.spec_from_file_location(
        "child_successor_roundtrip", successor_path
    )
    successor = importlib.util.module_from_spec(successor_spec)
    successor_spec.loader.exec_module(successor)
    async with _session_factory() as db:
        assert (
            await db.scalar(
                text(
                    "SELECT count(*) FROM legal_assessments WHERE child_adolescent_assessment IS NOT NULL"
                )
            )
            == 0
        )
        connection = await db.connection()

        def roundtrip(sync):
            with Operations.context(
                MigrationContext.configure(
                    sync, opts={"target_metadata": Base.metadata}
                )
            ):
                successor.downgrade()
                migration.downgrade()
                assert (
                    sync.scalar(
                        text(
                            "SELECT count(*) FROM information_schema.columns WHERE table_name='legal_assessments' AND column_name='child_adolescent_assessment'"
                        )
                    )
                    == 0
                )
                migration.upgrade()
                successor.upgrade()

        await connection.run_sync(roundtrip)
        assert (
            await db.scalar(
                text(
                    "SELECT count(*) FROM pg_constraint WHERE conrelid='legal_assessments'::regclass AND pg_get_constraintdef(oid) LIKE '%child_adolescent_assessment%'"
                )
            )
            == 2
        )
        await db.rollback()
