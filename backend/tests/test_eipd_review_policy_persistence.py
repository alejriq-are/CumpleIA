"""Metadatos de politica opcionales, integridad PostgreSQL y RLS sin activar revision."""

from datetime import UTC, datetime
from uuid import UUID

import pytest
from pydantic import ValidationError
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError, IntegrityError

from app.db.models import EipdResolutionReview
from app.schemas.licitud import (
    EipdResolutionReviewIn,
    EipdResolutionReviewWithPolicyOut,
)
from app.services.eipd_policy import (
    build_eipd_policy_hash_v1,
    build_eipd_review_policy_metadata_v1,
    derive_eipd_review_policy_identity_v1,
)
from tests import test_eipd_resolution_persistence as persistence_fixtures
from tests import test_services_eipd_policy as policy_fixtures

app_role_session = persistence_fixtures.app_role_session
licitud_base_data = persistence_fixtures.licitud_base_data
review_data = persistence_fixtures.review_data
policy = policy_fixtures.policy


async def insert_policy_event(session, values):
    return await session.scalar(
        text(
            """INSERT INTO eipd_resolution_reviews
        (organization_id, assessment_id, created_by, decision, rationale,
         review_reference, document_hash, context_hash, policy_version, policy_reference, policy_hash)
        VALUES (:organization_id, :assessment_id, :created_by, :decision, :rationale,
                :review_reference, :document_hash, :context_hash, :policy_version, :policy_reference, :policy_hash)
        RETURNING id"""
        ),
        values,
    )


def values(org, assessment, actor, **metadata):
    return (
        dict(
            persistence_fixtures.review_values(org, assessment, actor),
            policy_version=None,
            policy_reference=None,
            policy_hash=None,
        )
        | metadata
    )


async def test_runtime_policy_event_roundtrip_and_legacy_unchanged(
    app_role_session, review_data, auth_a_id, org_a_id, profile_a_id, policy
):
    await persistence_fixtures._set_auth_user(app_role_session, auth_a_id)
    legacy = await app_role_session.get(EipdResolutionReview, review_data["review_a"])
    assert derive_eipd_review_policy_identity_v1(legacy) is None
    old_snapshot = (
        legacy.id,
        legacy.document_hash,
        legacy.context_hash,
        legacy.created_at,
        legacy.decision,
    )
    metadata = build_eipd_review_policy_metadata_v1(policy)
    event_id = await insert_policy_event(
        app_role_session,
        values(org_a_id, review_data["assessment_a"], profile_a_id, **metadata),
    )
    event = await app_role_session.get(EipdResolutionReview, event_id)
    identity = derive_eipd_review_policy_identity_v1(event)
    assert (
        identity.review_id == event.id
        and identity.policy_hash == build_eipd_policy_hash_v1(policy)
    )
    assert (
        identity.policy_reference == policy["policy_reference"]
        and identity.policy_version == 1
    )
    assert (
        legacy.id,
        legacy.document_hash,
        legacy.context_hash,
        legacy.created_at,
        legacy.decision,
    ) == old_snapshot
    assert event.created_at.tzinfo is not None
    assert {
        e.id
        for e in (await app_role_session.scalars(select(EipdResolutionReview))).all()
    } == {legacy.id, event.id}


@pytest.mark.parametrize(
    "mode",
    [
        "version",
        "reference",
        "hash",
        "version_reference",
        "version_hash",
        "reference_hash",
        "v0",
        "v2",
        "blank",
        "spaces",
        "short_hash",
        "upper_hash",
    ],
)
async def test_database_rejects_partial_or_invalid_policy_identity(
    app_role_session, review_data, auth_a_id, org_a_id, profile_a_id, mode
):
    await persistence_fixtures._set_auth_user(app_role_session, auth_a_id)
    metadata = dict(
        policy_version=1, policy_reference="TEST: politica", policy_hash="c" * 64
    )
    if mode in (
        "version",
        "reference",
        "hash",
        "version_reference",
        "version_hash",
        "reference_hash",
    ):
        metadata = {
            "policy_" + key: metadata["policy_" + key] for key in mode.split("_")
        }
    elif mode == "v0":
        metadata["policy_version"] = 0
    elif mode == "v2":
        metadata["policy_version"] = 2
    elif mode == "blank":
        metadata["policy_reference"] = ""
    elif mode == "spaces":
        metadata["policy_reference"] = "  "
    elif mode == "short_hash":
        metadata["policy_hash"] = "a" * 63
    elif mode == "upper_hash":
        metadata["policy_hash"] = "A" * 64
    constraint_name = await app_role_session.scalar(
        text(
            "SELECT conname FROM pg_constraint WHERE conrelid='eipd_resolution_reviews'::regclass "
            "AND contype='c' AND pg_get_constraintdef(oid) LIKE '%policy_version%'"
        )
    )
    assert constraint_name is not None
    with pytest.raises(IntegrityError, match=constraint_name):
        async with app_role_session.begin_nested():
            await insert_policy_event(
                app_role_session,
                values(org_a_id, review_data["assessment_a"], profile_a_id, **metadata),
            )


@pytest.mark.parametrize("mode", ["tenant", "actor", "parent", "no_auth"])
async def test_policy_metadata_does_not_bypass_rls(
    app_role_session,
    review_data,
    auth_a_id,
    org_a_id,
    org_b_id,
    profile_a_id,
    profile_b_id,
    policy,
    mode,
):
    if mode != "no_auth":
        await persistence_fixtures._set_auth_user(app_role_session, auth_a_id)
    data = values(
        org_a_id,
        review_data["assessment_a"],
        profile_a_id,
        **build_eipd_review_policy_metadata_v1(policy),
    )
    if mode == "tenant":
        data.update(organization_id=org_b_id, assessment_id=review_data["assessment_b"])
    elif mode == "actor":
        data["created_by"] = profile_b_id
    elif mode == "parent":
        data["assessment_id"] = review_data["assessment_b"]
    with pytest.raises(DBAPIError, match="row-level security"):
        async with app_role_session.begin_nested():
            await insert_policy_event(app_role_session, data)


async def test_policy_identity_cannot_be_updated_in_runtime(
    app_role_session, review_data, auth_a_id
):
    await persistence_fixtures._set_auth_user(app_role_session, auth_a_id)
    with pytest.raises(DBAPIError, match="permission denied"):
        async with app_role_session.begin_nested():
            await app_role_session.execute(
                text(
                    "UPDATE eipd_resolution_reviews SET policy_version=1, policy_reference='TEST', policy_hash=:hash WHERE id=:id"
                ),
                {"hash": "c" * 64, "id": review_data["review_a"]},
            )


@pytest.mark.parametrize("decision", ["continuar", "requiere_cambios", "no_continuar"])
async def test_legacy_identity_never_promoted(_session_factory, review_data, decision):
    async with _session_factory() as session:
        row = await session.get(EipdResolutionReview, review_data["review_a"])
        data = {
            name: getattr(row, name)
            for name in EipdResolutionReviewWithPolicyOut.model_fields
        }
        data["decision"] = decision
        out = EipdResolutionReviewWithPolicyOut.model_validate(data)
        assert (
            out.policy_version is None
            and out.policy_reference is None
            and out.policy_hash is None
        )
        assert derive_eipd_review_policy_identity_v1(out) is None


@pytest.fixture
def server_event(policy):
    return dict(
        id=str(UUID(int=1)),
        organization_id=str(UUID(int=2)),
        assessment_id=str(UUID(int=3)),
        decision="continuar",
        rationale="Fundamento",
        review_reference="TEST: R1",
        document_hash="a" * 64,
        context_hash="b" * 64,
        created_by=str(UUID(int=4)),
        created_at=datetime(2026, 10, 7, tzinfo=UTC),
        **build_eipd_review_policy_metadata_v1(policy),
    )


@pytest.mark.parametrize(
    "mode", ["valid", "partial", "bool", "version", "reference", "hash", "extra"]
)
def test_server_output_closed_and_coherent(server_event, mode):
    if mode == "partial":
        server_event["policy_reference"] = None
    elif mode == "bool":
        server_event["policy_version"] = True
    elif mode == "version":
        server_event["policy_version"] = 2
    elif mode == "reference":
        server_event["policy_reference"] = " "
    elif mode == "hash":
        server_event["policy_hash"] = "BAD"
    elif mode == "extra":
        server_event["approved"] = True
    if mode == "valid":
        out = EipdResolutionReviewWithPolicyOut.model_validate(server_event)
        assert derive_eipd_review_policy_identity_v1(out).review_id == out.id
    else:
        with pytest.raises(ValidationError):
            EipdResolutionReviewWithPolicyOut.model_validate(server_event)


@pytest.mark.parametrize("field", ["policy_version", "policy_reference", "policy_hash"])
def test_client_cannot_supply_server_metadata(server_event, field):
    with pytest.raises(ValidationError):
        EipdResolutionReviewIn.model_validate(
            {
                "decision": "continuar",
                "rationale": "Fundamento",
                "review_reference": "TEST: R1",
                field: server_event[field],
            }
        )


@pytest.mark.parametrize(
    "field", ["policy_version", "policy_reference", "policy_hash", "id"]
)
def test_mapper_rejects_incomplete_identity(server_event, field):
    server_event[field] = None
    with pytest.raises(ValidationError):
        derive_eipd_review_policy_identity_v1(server_event)
