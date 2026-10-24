"""Persistencia tenant de evidencia; politica y positivos sinteticos, no activacion."""

from copy import deepcopy
from datetime import UTC, datetime
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import delete, select, text
from sqlalchemy.exc import DBAPIError, IntegrityError

from app.db.models import (
    EipdConfirmationEvidence,
    EipdPolicyPublication,
    EipdPolicySelection,
    EipdPolicySelector,
    EipdResolutionReview,
    LegalAssessment,
)
from app.services.eipd_policy import build_eipd_policy_hash_v1
from tests import test_eipd_policy_global_persistence as global_fixtures
from tests import test_rls_isolation_licitud as rls
from tests import test_services_eipd_policy as policy_fixtures

app_role_session = rls.app_role_session
licitud_base_data = rls.licitud_base_data
policy = policy_fixtures.policy


def evidence_values(org, aid, actor, review, pub, event):
    return dict(
        id=uuid4(),
        organization_id=org,
        assessment_id=aid,
        created_by=actor,
        review_id=review.id,
        publication_id=pub.id,
        selector_revision=event.revision,
        selection_id=event.id,
        policy_version=pub.policy_version,
        policy_reference=pub.policy_reference,
        policy_hash=pub.policy_hash,
        document_hash=review.document_hash,
        context_hash=review.context_hash,
    )


@pytest_asyncio.fixture(loop_scope="function")
async def evidence_state(
    _session_factory,
    licitud_base_data,
    profile_a_id,
    profile_b_id,
    org_a_id,
    org_b_id,
    policy,
    app_role_session,
):
    async with _session_factory() as db:
        assert await db.get(EipdPolicySelector, 1) is None
        pub = global_fixtures.publication(profile_a_id)
        pub.payload = policy
        pub.policy_reference = policy["policy_reference"]
        pub.policy_hash = build_eipd_policy_hash_v1(policy)
        db.add(pub)
        await db.flush()
        event = global_fixtures.selection(pub, profile_a_id)
        db.add(event)
        await db.flush()
        db.add(
            EipdPolicySelector(
                id=1, revision=1, publication_id=pub.id, selection_id=event.id
            )
        )
        reviews = []
        for suffix, org, actor in (
            ("a", org_a_id, profile_a_id),
            ("b", org_b_id, profile_b_id),
        ):
            aid = licitud_base_data["assessment_" + suffix]
            assessment = await db.get(LegalAssessment, aid)
            assessment.eipd_resolution_assessment = {"schema_version": 1}
            row = EipdResolutionReview(
                id=uuid4(),
                organization_id=org,
                assessment_id=aid,
                created_by=actor,
                decision="continuar",
                rationale="TEST: positivo fixture",
                review_reference="TEST",
                document_hash="a" * 64,
                context_hash="b" * 64,
                policy_version=1,
                policy_reference=pub.policy_reference,
                policy_hash=pub.policy_hash,
            )
            db.add(row)
            reviews.append(row)
        await db.flush()
        values_a = evidence_values(
            org_a_id,
            licitud_base_data["assessment_a"],
            profile_a_id,
            reviews[0],
            pub,
            event,
        )
        values_b = evidence_values(
            org_b_id,
            licitud_base_data["assessment_b"],
            profile_b_id,
            reviews[1],
            pub,
            event,
        )
        db.add(EipdConfirmationEvidence(**values_b))
        await db.commit()
    publication_ids = [pub.id]
    yield dict(
        licitud_base_data,
        values_a=values_a,
        values_b=values_b,
        pub=pub,
        event=event,
        publication_ids=publication_ids,
    )
    await app_role_session.rollback()
    async with _session_factory() as db:
        aids = [licitud_base_data["assessment_a"], licitud_base_data["assessment_b"]]
        await db.execute(
            delete(EipdConfirmationEvidence).where(
                EipdConfirmationEvidence.assessment_id.in_(aids)
            )
        )
        await db.execute(
            delete(EipdResolutionReview).where(
                EipdResolutionReview.assessment_id.in_(aids)
            )
        )
        await db.execute(delete(EipdPolicySelector).where(EipdPolicySelector.id == 1))
        await db.execute(
            delete(EipdPolicySelection).where(
                EipdPolicySelection.publication_id.in_(publication_ids)
            )
        )
        await db.execute(
            delete(EipdPolicyPublication).where(
                EipdPolicyPublication.id.in_(publication_ids)
            )
        )
        await db.commit()


async def test_runtime_evidence_roundtrip_and_tenant_isolation(
    app_role_session, evidence_state, auth_a_id, auth_b_id
):
    await rls._set_auth_user(app_role_session, auth_a_id)
    row = EipdConfirmationEvidence(**evidence_state["values_a"])
    app_role_session.add(row)
    await app_role_session.flush()
    assert row.created_at.tzinfo is not None
    visible = (await app_role_session.scalars(select(EipdConfirmationEvidence))).all()
    assert [x.id for x in visible] == [row.id]
    assert (
        await app_role_session.scalar(
            select(EipdConfirmationEvidence.id).where(
                EipdConfirmationEvidence.id == evidence_state["values_b"]["id"]
            )
        )
        is None
    )
    await app_role_session.commit()
    await rls._set_auth_user(app_role_session, auth_b_id)
    assert (
        await app_role_session.scalars(select(EipdConfirmationEvidence.id))
    ).all() == [evidence_state["values_b"]["id"]]


async def test_privileges_append_only(app_role_session):
    row = (
        await app_role_session.execute(
            text(
                """SELECT current_user,
      (SELECT rolbypassrls FROM pg_roles WHERE rolname=current_user),
      (SELECT relrowsecurity FROM pg_class WHERE oid='eipd_confirmation_evidence'::regclass),
      has_table_privilege(current_user,'eipd_confirmation_evidence','SELECT'),
      has_table_privilege(current_user,'eipd_confirmation_evidence','INSERT'),
      has_table_privilege(current_user,'eipd_confirmation_evidence','UPDATE'),
      has_table_privilege(current_user,'eipd_confirmation_evidence','DELETE'),
      has_table_privilege(current_user,'eipd_confirmation_evidence','TRUNCATE'),
      has_table_privilege('eipd_policy_admin','eipd_confirmation_evidence','INSERT')"""
            )
        )
    ).one()
    assert tuple(row) == (
        "app_user",
        False,
        True,
        True,
        True,
        False,
        False,
        False,
        False,
    )


@pytest.mark.parametrize("operation", ["UPDATE", "DELETE", "TRUNCATE"])
async def test_runtime_cannot_rewrite_evidence(
    app_role_session, evidence_state, auth_b_id, operation
):
    await rls._set_auth_user(app_role_session, auth_b_id)
    query = (
        "UPDATE eipd_confirmation_evidence SET id=id"
        if operation == "UPDATE"
        else (
            "DELETE FROM eipd_confirmation_evidence"
            if operation == "DELETE"
            else "TRUNCATE eipd_confirmation_evidence"
        )
    )
    with pytest.raises(DBAPIError):
        await app_role_session.execute(text(query))
    await app_role_session.rollback()


@pytest.mark.parametrize(
    "mode",
    [
        "other_tenant",
        "spoof_actor",
        "confirmed",
        "missing_document",
        "later_negative",
        "unauthenticated",
    ],
)
async def test_rls_rejects_invalid_runtime_insert(
    app_role_session, evidence_state, auth_a_id, profile_b_id, _session_factory, mode
):
    values = dict(evidence_state["values_a"])
    if mode == "other_tenant":
        values = dict(evidence_state["values_b"], id=uuid4())
    elif mode == "spoof_actor":
        values["created_by"] = profile_b_id
    if mode in ("confirmed", "missing_document", "later_negative"):
        async with _session_factory() as db:
            assessment = await db.get(LegalAssessment, values["assessment_id"])
            if mode == "confirmed":
                assessment.status = "confirmado"
                assessment.confirmed_at = datetime.now(UTC)
                assessment.confirmed_by = values["created_by"]
            elif mode == "missing_document":
                assessment.eipd_resolution_assessment = None
            else:
                positive = await db.get(EipdResolutionReview, values["review_id"])
                db.add(
                    EipdResolutionReview(
                        organization_id=positive.organization_id,
                        assessment_id=positive.assessment_id,
                        created_by=positive.created_by,
                        decision="no_continuar",
                        rationale="TEST: nueva negativa",
                        review_reference="TEST",
                        document_hash=positive.document_hash,
                        context_hash=positive.context_hash,
                    )
                )
            await db.commit()
    if mode != "unauthenticated":
        await rls._set_auth_user(app_role_session, auth_a_id)
    app_role_session.add(EipdConfirmationEvidence(**values))
    with pytest.raises(DBAPIError):
        await app_role_session.flush()
    await app_role_session.rollback()


@pytest.mark.parametrize(
    "field,value",
    [
        ("policy_version", 2),
        ("selector_revision", 0),
        ("selector_revision", 2),
        ("policy_hash", "c" * 64),
        ("policy_reference", "otra"),
        ("document_hash", "c" * 64),
        ("context_hash", "c" * 64),
        ("review_id", uuid4()),
        ("publication_id", uuid4()),
        ("selection_id", uuid4()),
        ("review_decision", "no_continuar"),
        ("organization_id", uuid4()),
        ("assessment_id", uuid4()),
    ],
)
async def test_composite_bindings_reject_forgery(
    _session_factory, evidence_state, field, value
):
    async with _session_factory() as db:
        values = dict(evidence_state["values_a"], **{field: value})
        db.add(EipdConfirmationEvidence(**values))
        with pytest.raises(IntegrityError):
            await db.flush()
        await db.rollback()


async def test_evidence_and_assessment_rollback_together(
    app_role_session, evidence_state, auth_a_id, _session_factory
):
    await rls._set_auth_user(app_role_session, auth_a_id)
    app_role_session.add(EipdConfirmationEvidence(**evidence_state["values_a"]))
    await app_role_session.flush()
    assessment = await app_role_session.get(
        LegalAssessment, evidence_state["assessment_a"]
    )
    assessment.status = "confirmado"
    assessment.confirmed_at = datetime.now(UTC)
    assessment.confirmed_by = evidence_state["values_a"]["created_by"]
    await app_role_session.flush()
    await app_role_session.rollback()
    async with _session_factory() as db:
        assert (
            await db.get(LegalAssessment, evidence_state["assessment_a"])
        ).status == "borrador"
        assert (
            await db.get(EipdConfirmationEvidence, evidence_state["values_a"]["id"])
            is None
        )


async def test_duplicate_assessment_evidence_rejected(_session_factory, evidence_state):
    async with _session_factory() as db:
        db.add(EipdConfirmationEvidence(**dict(evidence_state["values_b"], id=uuid4())))
        with pytest.raises(IntegrityError):
            await db.flush()
        await db.rollback()


async def test_revocation_preserves_history_and_rejects_new_evidence(
    _session_factory,
    app_role_session,
    evidence_state,
    auth_a_id,
    auth_b_id,
    profile_a_id,
):
    async with _session_factory() as db:
        oldpub = evidence_state["pub"]
        policy = deepcopy(oldpub.payload)
        policy["policy_reference"] += " revocada"
        policy["activation"] = "deshabilitada"
        pub = global_fixtures.publication(profile_a_id)
        pub.payload = policy
        pub.policy_reference = policy["policy_reference"]
        pub.policy_hash = build_eipd_policy_hash_v1(policy)
        db.add(pub)
        await db.flush()
        event = global_fixtures.selection(pub, profile_a_id, evidence_state["event"])
        db.add(event)
        await db.flush()
        selector = await db.get(EipdPolicySelector, 1)
        selector.revision = 2
        selector.publication_id = pub.id
        selector.selection_id = event.id
        await db.commit()
        evidence_state["publication_ids"].append(pub.id)
    await rls._set_auth_user(app_role_session, auth_a_id)
    app_role_session.add(EipdConfirmationEvidence(**evidence_state["values_a"]))
    with pytest.raises(DBAPIError):
        await app_role_session.flush()
    await app_role_session.rollback()
    await rls._set_auth_user(app_role_session, auth_b_id)
    old = await app_role_session.get(
        EipdConfirmationEvidence, evidence_state["values_b"]["id"]
    )
    assert old.selector_revision == 1 and old.publication_id == evidence_state["pub"].id


@pytest.mark.parametrize("mode", ["negative", "legacy"])
async def test_fk_cannot_accredit_negative_or_legacy_human_event(
    _session_factory, evidence_state, mode
):
    values = dict(evidence_state["values_a"])
    async with _session_factory() as db:
        row = EipdResolutionReview(
            organization_id=values["organization_id"],
            assessment_id=values["assessment_id"],
            created_by=values["created_by"],
            decision="no_continuar" if mode == "negative" else "continuar",
            rationale="TEST",
            review_reference="TEST",
            document_hash=values["document_hash"],
            context_hash=values["context_hash"],
            policy_version=values["policy_version"] if mode == "negative" else None,
            policy_reference=values["policy_reference"] if mode == "negative" else None,
            policy_hash=values["policy_hash"] if mode == "negative" else None,
        )
        db.add(row)
        await db.flush()
        values["review_id"] = row.id
        db.add(EipdConfirmationEvidence(**values))
        with pytest.raises(IntegrityError):
            await db.flush()
        await db.rollback()
