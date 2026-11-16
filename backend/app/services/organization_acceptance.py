"""Decisiones documentales de organizacion; no cambia politica ni confirma EIPD."""

from fastapi import HTTPException
from sqlalchemy import func, select

from app.core.config import get_settings
from app.db.child_eipd import EipdChildResolution
from app.db.models import LegalAssessmentSeries, Membership, UserRole
from app.db.organization_acceptance import (
    OrganizationAcceptanceAuthority as Authority,
)
from app.db.organization_acceptance import (
    OrganizationDocumentAcceptance as Acceptance,
)
from app.schemas.organization_acceptance import (
    AcceptanceOut,
    AuthorityOut,
    AuthorityState,
)
from app.services import eipd_child_persistence as child


async def member(db, org, actor, manage=False):
    row = await db.scalar(
        select(Membership).where(
            Membership.organization_id == org, Membership.profile_id == actor
        )
    )
    allowed = (
        (UserRole.owner, UserRole.admin)
        if manage
        else (UserRole.owner, UserRole.admin, UserRole.editor)
    )
    if row is None or row.role not in allowed:
        raise HTTPException(403, detail="Miembro de organizacion facultado requerido")
    return row


def test_gate():
    settings = get_settings()
    if (
        settings.environment not in ("development", "test")
        or not settings.eipd_child_test_writes_enabled
    ):
        child.conflict("aceptacion_solo_pruebas_ficticias")


async def series_lock(db, org, tid, aid):
    from app.services import licitud

    draft = await licitud.get_legal_assessment_v1(db, org, tid, aid)
    series = await db.scalar(
        select(LegalAssessmentSeries)
        .where(
            LegalAssessmentSeries.id == draft.series_id,
            LegalAssessmentSeries.organization_id == org,
            LegalAssessmentSeries.treatment_id == tid,
        )
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    if series is None:
        child.conflict("serie_no_disponible")
    return series


async def latest(db, org, aid, actor):
    return await db.scalar(
        select(Authority)
        .where(
            Authority.organization_id == org,
            Authority.assessment_id == aid,
            Authority.actor_id == actor,
        )
        .order_by(Authority.revision.desc())
        .limit(1)
    )


async def state(db, org, tid, aid, actor):
    from app.services import licitud

    await licitud.get_legal_assessment_v1(db, org, tid, aid)
    membership = await db.scalar(
        select(Membership).where(
            Membership.organization_id == org, Membership.profile_id == actor
        )
    )
    rows = await db.scalars(
        select(Authority)
        .where(
            Authority.organization_id == org,
            Authority.treatment_id == tid,
            Authority.assessment_id == aid,
        )
        .order_by(Authority.created_at, Authority.id)
    )
    return AuthorityState(
        actor_id=actor,
        may_designate=membership is not None
        and membership.role in (UserRole.owner, UserRole.admin),
        authorities=[AuthorityOut.model_validate(r) for r in rows],
    )


async def designate(db, org, tid, aid, actor, payload):
    test_gate()
    # Sin adquirir selector despues de serie: designacion no toca politica global.
    await series_lock(db, org, tid, aid)
    await member(db, org, actor, manage=True)
    if payload.action == "otorgar":
        await member(db, org, payload.actor_id)
    previous = await latest(db, org, aid, payload.actor_id)
    if payload.expected_revision != (previous.revision if previous else 0):
        child.conflict("facultad_revision_obsoleta")
    row = Authority(
        organization_id=org,
        treatment_id=tid,
        assessment_id=aid,
        created_by=actor,
        revision=payload.expected_revision + 1,
        **payload.model_dump(exclude={"expected_revision"}),
    )
    db.add(row)
    await db.flush()
    return AuthorityOut.model_validate(row)


async def record(db, org, tid, aid, rid, actor, payload):
    # Selector -> serie; misma serie serializa designacion/revocacion y decisiones.
    context, _ = await child.locked_context(db, org, tid, aid)
    await member(db, org, actor)
    authority = await latest(db, org, aid, actor)
    if (
        authority is None
        or authority.action != "otorgar"
        or authority.id != payload.authority_id
    ):
        raise HTTPException(403, detail="Facultad explicita vigente requerida")
    row = await child.get_resolution(db, org, tid, aid, rid)
    max_version = await db.scalar(
        select(func.max(EipdChildResolution.version)).where(
            EipdChildResolution.organization_id == org,
            EipdChildResolution.assessment_id == aid,
        )
    )
    if (
        row.version != max_version
        or row.context_hash != child.context_hash(context)
        or row.child_material_hash != child.child_hash(context)
    ):
        child.conflict("aceptacion_material_obsoleto")
    event = Acceptance(
        organization_id=org,
        treatment_id=tid,
        assessment_id=aid,
        resolution_id=rid,
        actor_id=actor,
        created_by=actor,
        document_hash=row.document_hash,
        context_hash=row.context_hash,
        child_material_hash=row.child_material_hash,
        **payload.model_dump(),
    )
    db.add(event)
    await db.flush()
    return AcceptanceOut.model_validate(event).model_copy(
        update={"material_status": "coincide", "faculty_current": True}
    )


async def material_status(db, org, tid, aid, row):
    from app.services import licitud

    draft = await licitud.get_legal_assessment_v1(db, org, tid, aid)
    if draft.status != "borrador":
        return "obsoleto"
    series = await db.scalar(
        select(LegalAssessmentSeries).where(LegalAssessmentSeries.id == draft.series_id)
    )
    try:
        bundle = await licitud.build_rat_context_bundle_from_m2_v1(
            db,
            org,
            tid,
            purpose_key=series.purpose_key,
            scope=licitud._scope_from_snapshot_v1(draft.rat_context_snapshot),
        )
        if (
            licitud.build_rat_context_hash_v1(bundle.canonical)
            != draft.rat_context_hash
            or draft.child_adolescent_assessment is None
        ):
            return "obsoleto"
        context = child.EipdChildContextV4.model_validate(
            {
                **licitud.build_eipd_resolution_context_from_assessment_v3(
                    draft, bundle.snapshot
                ).model_dump(mode="python"),
                "context_schema_version": 4,
                "organization_id": org,
                "treatment_id": tid,
                "assessment_id": aid,
                "child_adolescent_assessment": draft.child_adolescent_assessment,
            }
        )
    except (ValueError, HTTPException):
        return "no_disponible"
    maximum = await db.scalar(
        select(func.max(EipdChildResolution.version)).where(
            EipdChildResolution.organization_id == org,
            EipdChildResolution.assessment_id == aid,
        )
    )
    return (
        "coincide"
        if row.version == maximum
        and row.context_hash == child.context_hash(context)
        and row.child_material_hash == child.child_hash(context)
        else "obsoleto"
    )


async def history(db, org, tid, aid, rid):
    row = await child.get_resolution(db, org, tid, aid, rid)
    status = await material_status(db, org, tid, aid, row)
    values = await db.scalars(
        select(Acceptance)
        .where(
            Acceptance.organization_id == org,
            Acceptance.assessment_id == aid,
            Acceptance.treatment_id == tid,
            Acceptance.resolution_id == rid,
        )
        .order_by(Acceptance.created_at, Acceptance.id)
    )
    result = []
    for event in values:
        if (event.document_hash, event.context_hash, event.child_material_hash) != (
            row.document_hash,
            row.context_hash,
            row.child_material_hash,
        ):
            child.conflict("aceptacion_historial_invalido")
        authority = await latest(db, org, aid, event.actor_id)
        membership = await db.scalar(
            select(Membership).where(
                Membership.organization_id == org,
                Membership.profile_id == event.actor_id,
            )
        )
        eligible = membership is not None and membership.role in (
            UserRole.owner,
            UserRole.admin,
            UserRole.editor,
        )
        result.append(
            AcceptanceOut.model_validate(event).model_copy(
                update={
                    "material_status": status,
                    "faculty_current": eligible
                    and authority is not None
                    and authority.id == event.authority_id
                    and authority.action == "otorgar",
                }
            )
        )
    return result
