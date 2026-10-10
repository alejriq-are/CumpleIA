"""Metadatos opcionales PostgreSQL, sin activar revision V2."""

import json

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.db.models import EipdResolutionReview
from app.services.eipd_review_metadata import read_eipd_review_context_metadata_v1
from tests import test_eipd_resolution_persistence as cases

app_role_session = cases.app_role_session
licitud_base_data = cases.licitud_base_data
review_data = cases.review_data


def values(org, assessment, actor):
    return cases.review_values(org, assessment, actor)


def metadata(data):
    return dict(
        metadata_schema_version=1,
        resolution_binding_version=2,
        context_schema_version=2,
        research_coverage="contexto_v2",
        document_hash=data["document_hash"],
        context_hash=data["context_hash"],
        research_material_hash=None,
    )


async def insert(session, data, material):
    return await session.scalar(
        text(
            """INSERT INTO eipd_resolution_reviews
      (organization_id,assessment_id,created_by,decision,rationale,review_reference,
       document_hash,context_hash,review_context_metadata)
      VALUES (:organization_id,:assessment_id,:created_by,:decision,:rationale,:review_reference,
       :document_hash,:context_hash,CAST(:metadata AS jsonb)) RETURNING id"""
        ),
        dict(data, metadata=json.dumps(material)),
    )


async def test_column_nullability_permissions_and_rls(_session_factory):
    async with _session_factory() as db:
        row = (
            await db.execute(
                text(
                    "SELECT is_nullable,data_type,column_default FROM information_schema.columns WHERE table_name='eipd_resolution_reviews' AND column_name='review_context_metadata'"
                )
            )
        ).one()
        assert tuple(row) == ("YES", "jsonb", None)
        assert await db.scalar(
            text(
                "SELECT has_column_privilege('app_user','eipd_resolution_reviews','review_context_metadata','SELECT,INSERT')"
            )
        )
        assert not await db.scalar(
            text(
                "SELECT has_column_privilege('app_user','eipd_resolution_reviews','review_context_metadata','UPDATE')"
            )
        )
        assert await db.scalar(
            text(
                "SELECT relrowsecurity FROM pg_class WHERE oid='eipd_resolution_reviews'::regclass"
            )
        )
    assert EipdResolutionReview.__table__.c.review_context_metadata.nullable


async def test_runtime_roundtrip_and_historical_null(
    app_role_session, review_data, auth_a_id, org_a_id, profile_a_id
):
    await cases._set_auth_user(app_role_session, auth_a_id)
    old = await app_role_session.get(EipdResolutionReview, review_data["review_a"])
    before = (old.id, old.document_hash, old.context_hash, old.created_at, old.decision)
    assert old.review_context_metadata is None
    assert read_eipd_review_context_metadata_v1(old) is None
    data = values(org_a_id, review_data["assessment_a"], profile_a_id)
    material = metadata(data)
    identity = await insert(app_role_session, data, material)
    event = await app_role_session.get(EipdResolutionReview, identity)
    parsed = read_eipd_review_context_metadata_v1(event)
    assert parsed.model_dump(mode="json") == material
    assert (
        old.id,
        old.document_hash,
        old.context_hash,
        old.created_at,
        old.decision,
    ) == before
    assert old.review_context_metadata is None
    for operation in (
        "UPDATE eipd_resolution_reviews SET review_context_metadata=NULL WHERE id=:id",
        "DELETE FROM eipd_resolution_reviews WHERE id=:id",
    ):
        with pytest.raises(DBAPIError, match="permission denied"):
            async with app_role_session.begin_nested():
                await app_role_session.execute(text(operation), {"id": identity})


@pytest.mark.parametrize(
    "change",
    [
        "array",
        "null",
        "partial",
        "extra",
        "version",
        "bool",
        "pair",
        "coverage",
        "document",
        "context",
        "research",
    ],
)
async def test_database_rejects_invalid_identity(
    app_role_session, review_data, auth_a_id, org_a_id, profile_a_id, change
):
    await cases._set_auth_user(app_role_session, auth_a_id)
    data = values(org_a_id, review_data["assessment_a"], profile_a_id)
    material = metadata(data)
    if change == "array":
        material = []
    elif change == "null":
        material = None
    elif change == "partial":
        material.pop("research_material_hash")
    elif change == "extra":
        material["approved"] = True
    elif change == "version":
        material["metadata_schema_version"] = 99
    elif change == "bool":
        material["metadata_schema_version"] = True
    elif change == "pair":
        material["context_schema_version"] = 1
    elif change == "coverage":
        material["research_coverage"] = "no_cubierta"
    elif change == "document":
        material["document_hash"] = "c" * 64
    elif change == "context":
        material["context_hash"] = "c" * 64
    else:
        material["research_material_hash"] = "fake"
    with pytest.raises(DBAPIError):
        async with app_role_session.begin_nested():
            await insert(app_role_session, data, material)


@pytest.mark.parametrize("mode", ["tenant", "actor", "parent", "no_auth"])
async def test_metadata_does_not_bypass_rls(
    app_role_session,
    review_data,
    auth_a_id,
    org_a_id,
    org_b_id,
    profile_a_id,
    profile_b_id,
    mode,
):
    if mode != "no_auth":
        await cases._set_auth_user(app_role_session, auth_a_id)
    data = values(org_a_id, review_data["assessment_a"], profile_a_id)
    if mode == "tenant":
        data.update(organization_id=org_b_id, assessment_id=review_data["assessment_b"])
    elif mode == "actor":
        data["created_by"] = profile_b_id
    elif mode == "parent":
        data["assessment_id"] = review_data["assessment_b"]
    with pytest.raises(DBAPIError, match="row-level security"):
        async with app_role_session.begin_nested():
            await insert(app_role_session, data, metadata(data))
