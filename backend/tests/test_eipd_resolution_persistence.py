"""Persistencia EIPD y barreras PostgreSQL reales, sin servicios/API de revision."""

import pytest
import pytest_asyncio
from sqlalchemy import delete, select, text
from sqlalchemy.exc import DBAPIError, IntegrityError

from app.db.models import EipdResolutionReview, LegalAssessment
from tests import test_rls_isolation_licitud as licitud_fixtures

app_role_session = licitud_fixtures.app_role_session
licitud_base_data = licitud_fixtures.licitud_base_data
_set_auth_user = licitud_fixtures._set_auth_user


def review_values(org, assessment, actor):
    return dict(
        organization_id=org,
        assessment_id=assessment,
        created_by=actor,
        decision="requiere_cambios",
        rationale="Revision documentada",
        review_reference="REV1",
        document_hash="a" * 64,
        context_hash="b" * 64,
    )


@pytest_asyncio.fixture(loop_scope="function")
async def review_data(
    _session_factory,
    licitud_base_data,
    org_a_id,
    org_b_id,
    profile_a_id,
    profile_b_id,
    app_role_session,
):
    ids = []
    async with _session_factory() as session:
        for suffix, org, actor in [
            ("a", org_a_id, profile_a_id),
            ("b", org_b_id, profile_b_id),
        ]:
            assessment_id = licitud_base_data["assessment_" + suffix]
            assessment = await session.get(LegalAssessment, assessment_id)
            assessment.eipd_resolution_assessment = {"schema_version": 1}
            event = EipdResolutionReview(**review_values(org, assessment_id, actor))
            session.add(event)
            await session.flush()
            ids.append(event.id)
        await session.commit()
    yield dict(licitud_base_data, review_a=ids[0], review_b=ids[1])
    await app_role_session.rollback()
    async with _session_factory() as session:
        await session.execute(
            delete(EipdResolutionReview).where(
                EipdResolutionReview.assessment_id.in_(
                    [
                        licitud_base_data["assessment_a"],
                        licitud_base_data["assessment_b"],
                    ]
                )
            )
        )
        await session.commit()


async def insert_review(session, values):
    return await session.scalar(
        text(
            """INSERT INTO eipd_resolution_reviews
        (organization_id, assessment_id, created_by, decision, rationale,
         review_reference, document_hash, context_hash)
        VALUES (:organization_id, :assessment_id, :created_by, :decision,
                :rationale, :review_reference, :document_hash, :context_hash)
        RETURNING id"""
        ),
        values,
    )


async def test_runtime_role_rls_and_privileges(app_role_session):
    row = (
        await app_role_session.execute(
            text(
                """SELECT current_user,
        (SELECT rolbypassrls FROM pg_roles WHERE rolname=current_user),
        (SELECT relrowsecurity FROM pg_class WHERE oid='eipd_resolution_reviews'::regclass),
        has_table_privilege(current_user, 'eipd_resolution_reviews', 'SELECT'),
        has_table_privilege(current_user, 'eipd_resolution_reviews', 'INSERT'),
        has_table_privilege(current_user, 'eipd_resolution_reviews', 'UPDATE'),
        has_table_privilege(current_user, 'eipd_resolution_reviews', 'DELETE'),
        has_table_privilege(current_user, 'eipd_resolution_reviews', 'TRUNCATE')"""
            )
        )
    ).one()
    assert tuple(row) == ("app_user", False, True, True, True, False, False, False)


@pytest.mark.parametrize("auth", ["a", "b", "none"])
async def test_review_rls_reads_only_own_history(
    app_role_session, review_data, auth_a_id, auth_b_id, auth
):
    if auth != "none":
        await _set_auth_user(app_role_session, auth_a_id if auth == "a" else auth_b_id)
    ids = set((await app_role_session.scalars(select(EipdResolutionReview.id))).all())
    expected = set() if auth == "none" else {review_data["review_" + auth]}
    assert ids == expected


async def test_valid_runtime_insert_and_server_timestamp(
    app_role_session, review_data, auth_a_id, org_a_id, profile_a_id
):
    await _set_auth_user(app_role_session, auth_a_id)
    event_id = await insert_review(
        app_role_session,
        review_values(org_a_id, review_data["assessment_a"], profile_a_id),
    )
    event = await app_role_session.get(EipdResolutionReview, event_id)
    assert event.id != review_data["review_a"]
    assert event.created_at.tzinfo is not None
    assert event.created_by == profile_a_id and event.decision == "requiere_cambios"
    assert event.document_hash == "a" * 64
    assert (
        len((await app_role_session.scalars(select(EipdResolutionReview))).all()) == 2
    )


@pytest.mark.parametrize(
    "operation",
    [
        "UPDATE eipd_resolution_reviews SET decision='continuar' WHERE id=:id",
        "DELETE FROM eipd_resolution_reviews WHERE id=:id",
        "TRUNCATE eipd_resolution_reviews",
    ],
)
async def test_runtime_cannot_modify_delete_or_truncate(
    app_role_session, review_data, auth_a_id, operation
):
    await _set_auth_user(app_role_session, auth_a_id)
    with pytest.raises(DBAPIError, match="permission denied"):
        async with app_role_session.begin_nested():
            await app_role_session.execute(
                text(operation), {"id": review_data["review_a"]}
            )


@pytest.mark.parametrize("mode", ["tenant", "actor", "parent", "no_auth"])
async def test_runtime_rejects_spoofed_insert(
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
        await _set_auth_user(app_role_session, auth_a_id)
    values = review_values(org_a_id, review_data["assessment_a"], profile_a_id)
    if mode == "tenant":
        values.update(
            organization_id=org_b_id, assessment_id=review_data["assessment_b"]
        )
    elif mode == "actor":
        values["created_by"] = profile_b_id
    elif mode == "parent":
        values["assessment_id"] = review_data["assessment_b"]
    with pytest.raises(DBAPIError, match="row-level security"):
        await insert_review(app_role_session, values)


@pytest.mark.parametrize("state", ["no_document", "confirmed"])
async def test_runtime_review_requires_draft_document(
    _session_factory,
    app_role_session,
    review_data,
    auth_a_id,
    org_a_id,
    profile_a_id,
    state,
):
    async with _session_factory() as session:
        assessment = await session.get(LegalAssessment, review_data["assessment_a"])
        if state == "no_document":
            assessment.eipd_resolution_assessment = None
        else:
            await session.execute(
                text(
                    """UPDATE legal_assessments SET status='confirmado',
                confirmed_by=:actor, confirmed_at=now() WHERE id=:id"""
                ),
                {"actor": profile_a_id, "id": assessment.id},
            )
        await session.commit()
    await _set_auth_user(app_role_session, auth_a_id)
    with pytest.raises(DBAPIError, match="row-level security"):
        await insert_review(
            app_role_session,
            review_values(org_a_id, review_data["assessment_a"], profile_a_id),
        )


@pytest.mark.parametrize("target", ["assessment", "organization"])
async def test_parent_delete_cannot_erase_history(
    app_role_session, review_data, auth_a_id, org_a_id, target
):
    await _set_auth_user(app_role_session, auth_a_id)
    table = "legal_assessments" if target == "assessment" else "organizations"
    row_id = review_data["assessment_a"] if target == "assessment" else org_a_id
    if target == "assessment":
        with pytest.raises(DBAPIError):
            async with app_role_session.begin_nested():
                await app_role_session.execute(
                    text(f"DELETE FROM {table} WHERE id=:id"), {"id": row_id}
                )
    else:
        result = await app_role_session.execute(
            text(f"DELETE FROM {table} WHERE id=:id"), {"id": row_id}
        )
        assert result.rowcount == 0
    assert (
        await app_role_session.get(EipdResolutionReview, review_data["review_a"])
        is not None
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("decision", "approved"),
        ("rationale", ""),
        ("rationale", " "),
        ("rationale", "\n\t"),
        ("review_reference", ""),
        ("review_reference", "\t"),
        ("document_hash", "A" * 64),
        ("document_hash", "a" * 63),
        ("context_hash", "g" * 64),
        ("context_hash", "a" * 65),
        ("created_by", None),
        ("assessment_id", None),
    ],
)
async def test_database_checks_review_payload(
    _session_factory, review_data, org_a_id, profile_a_id, field, value
):
    values = review_values(org_a_id, review_data["assessment_a"], profile_a_id)
    values[field] = value
    async with _session_factory() as session:
        session.add(EipdResolutionReview(**values))
        with pytest.raises(IntegrityError):
            await session.flush()
        await session.rollback()


async def test_composite_fk_rejects_cross_tenant_even_owner(
    _session_factory, review_data, org_a_id, profile_a_id
):
    async with _session_factory() as session:
        session.add(
            EipdResolutionReview(
                **review_values(org_a_id, review_data["assessment_b"], profile_a_id)
            )
        )
        with pytest.raises(
            IntegrityError, match="fk_eipd_resolution_reviews_assessment_tenant"
        ):
            await session.flush()
        await session.rollback()


@pytest.mark.parametrize("value", [[], "informe", 5, True])
async def test_resolution_jsonb_only_objects(_session_factory, review_data, value):
    async with _session_factory() as session:
        assessment = await session.get(LegalAssessment, review_data["assessment_a"])
        assessment.eipd_resolution_assessment = value
        with pytest.raises(IntegrityError, match="eipd_resolution"):
            await session.flush()
        await session.rollback()


async def test_json_null_rejected_sql_null_allowed_and_history_preserved(
    app_role_session, review_data, auth_a_id
):
    await _set_auth_user(app_role_session, auth_a_id)
    before = await app_role_session.get(EipdResolutionReview, review_data["review_a"])
    snapshot = (
        before.decision,
        before.document_hash,
        before.context_hash,
        before.created_at,
    )
    with pytest.raises(IntegrityError):
        async with app_role_session.begin_nested():
            await app_role_session.execute(
                text(
                    """UPDATE legal_assessments
                SET eipd_resolution_assessment='null'::jsonb WHERE id=:id"""
                ),
                {"id": review_data["assessment_a"]},
            )
    await app_role_session.execute(
        text(
            """UPDATE legal_assessments
        SET eipd_resolution_assessment=NULL WHERE id=:id"""
        ),
        {"id": review_data["assessment_a"]},
    )
    after = await app_role_session.get(
        EipdResolutionReview, review_data["review_a"], populate_existing=True
    )
    assert (
        after.decision,
        after.document_hash,
        after.context_hash,
        after.created_at,
    ) == snapshot


async def test_resolution_orm_none_is_sql_null(_session_factory, review_data):
    async with _session_factory() as session:
        assessment = await session.get(LegalAssessment, review_data["assessment_a"])
        assessment.eipd_resolution_assessment = None
        await session.flush()
        assert await session.scalar(
            text(
                """SELECT eipd_resolution_assessment IS NULL
            FROM legal_assessments WHERE id=:id"""
            ),
            {"id": assessment.id},
        )
        await session.rollback()


async def test_resolution_other_tenant_not_readable(
    app_role_session, review_data, auth_a_id
):
    await _set_auth_user(app_role_session, auth_a_id)
    assert (
        await app_role_session.get(LegalAssessment, review_data["assessment_b"]) is None
    )
    own = await app_role_session.get(LegalAssessment, review_data["assessment_a"])
    assert own.eipd_resolution_assessment == {"schema_version": 1}
