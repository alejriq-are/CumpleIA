"""Metadata sucesora con PostgreSQL/app_user; fixtures exclusivamente ficticias."""

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.db.models import EipdResolutionReview
from app.services.eipd_review_metadata_v2 import read_eipd_review_context_metadata_v2
from tests import test_eipd_review_metadata_storage as previous

app_role_session = previous.app_role_session
licitud_base_data = previous.licitud_base_data
review_data = previous.review_data


def metadata(data):
    return dict(
        metadata_schema_version=2,
        resolution_binding_version=3,
        context_schema_version=3,
        research_coverage="contexto_v3",
        representation_coverage="contexto_v3",
        document_hash=data["document_hash"],
        context_hash=data["context_hash"],
        research_material_hash=None,
        representation_material_hash="a" * 64,
    )


async def test_new_metadata_roundtrip_append_only_and_old_null(
    app_role_session,
    review_data,
    auth_a_id,
    org_a_id,
    profile_a_id,
):
    await previous.cases._set_auth_user(app_role_session, auth_a_id)
    old = await app_role_session.get(EipdResolutionReview, review_data["review_a"])
    assert read_eipd_review_context_metadata_v2(old) is None
    before = (old.document_hash, old.context_hash, old.created_at)
    data = previous.values(org_a_id, review_data["assessment_a"], profile_a_id)
    material = metadata(data)
    identity = await previous.insert(app_role_session, data, material)
    event = await app_role_session.get(EipdResolutionReview, identity)
    assert (
        read_eipd_review_context_metadata_v2(event).model_dump(mode="json") == material
    )
    assert (old.document_hash, old.context_hash, old.created_at) == before
    assert old.review_context_metadata is None
    for operation in (
        "UPDATE eipd_resolution_reviews SET review_context_metadata=NULL WHERE id=:id",
        "DELETE FROM eipd_resolution_reviews WHERE id=:id",
    ):
        with pytest.raises(DBAPIError, match="permission denied"):
            async with app_role_session.begin_nested():
                await app_role_session.execute(text(operation), {"id": identity})


@pytest.mark.parametrize(
    "field,value",
    [
        ("metadata_schema_version", True),
        ("metadata_schema_version", "2"),
        ("resolution_binding_version", 2),
        ("context_schema_version", 2),
        ("representation_coverage", "no_cubierta"),
        ("research_coverage", "contexto_v2"),
        ("document_hash", "b" * 64),
        ("context_hash", "c" * 64),
        ("representation_material_hash", "invalid"),
        ("research_material_hash", 7),
        ("can_confirm", True),
    ],
)
async def test_sql_rejects_incompatible_metadata(
    app_role_session,
    review_data,
    auth_a_id,
    org_a_id,
    profile_a_id,
    field,
    value,
):
    await previous.cases._set_auth_user(app_role_session, auth_a_id)
    data = previous.values(org_a_id, review_data["assessment_a"], profile_a_id)
    material = metadata(data)
    material[field] = value
    with pytest.raises(DBAPIError, match="check constraint"):
        async with app_role_session.begin_nested():
            await previous.insert(app_role_session, data, material)


async def test_missing_new_field_cannot_fall_back_to_old_contract(
    app_role_session,
    review_data,
    auth_a_id,
    org_a_id,
    profile_a_id,
):
    await previous.cases._set_auth_user(app_role_session, auth_a_id)
    data = previous.values(org_a_id, review_data["assessment_a"], profile_a_id)
    material = metadata(data)
    material.pop("representation_material_hash")
    with pytest.raises(DBAPIError, match="check constraint"):
        async with app_role_session.begin_nested():
            await previous.insert(app_role_session, data, material)


@pytest.mark.parametrize("mode", ["tenant", "actor", "parent", "no_auth"])
async def test_successor_metadata_does_not_bypass_rls(
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
        await previous.cases._set_auth_user(app_role_session, auth_a_id)
    data = previous.values(org_a_id, review_data["assessment_a"], profile_a_id)
    if mode == "tenant":
        data.update(organization_id=org_b_id, assessment_id=review_data["assessment_b"])
    elif mode == "actor":
        data["created_by"] = profile_b_id
    elif mode == "parent":
        data["assessment_id"] = review_data["assessment_b"]
    with pytest.raises(DBAPIError, match="row-level security"):
        async with app_role_session.begin_nested():
            await previous.insert(app_role_session, data, metadata(data))
