"""Servicios internos §93; caller autentica actor y gestiona commit/rollback.

Sin API administrativa. Revision/preparacion/confirmacion conectadas en §§95–96.
"""

from uuid import uuid4

from sqlalchemy import select, text

from app.db.models import EipdPolicyPublication, EipdPolicySelection, EipdPolicySelector
from app.services.eipd_policy_audit import (
    EipdPolicyAuditSnapshotV1,
    EipdPolicySelectionRequestV1,
    _validated,
    build_eipd_policy_publication_v1,
    plan_eipd_policy_selection_v1,
)

# Serializa bootstrap (no existe fila para FOR UPDATE) y selecciones administrativas.
# Canal administrativo exclusivo; nunca adquiere series.
_SELECTION_LOCK = 719_093
_SNAPSHOT_SQL = """SELECT jsonb_build_object(
  'publications', COALESCE((SELECT jsonb_agg(to_jsonb(p) ORDER BY p.id)
    FROM eipd_policy_publications p), '[]'::jsonb),
  'selections', COALESCE((SELECT jsonb_agg(to_jsonb(e) ORDER BY e.revision)
    FROM eipd_policy_selections e), '[]'::jsonb),
  'selector', (SELECT to_jsonb(s) FROM eipd_policy_selector s WHERE s.id=1))"""


async def _require_admin(db):
    # Rol DB separado acredita canal, no identidad personal del actor.
    # Entradas personales derivan actor via barrera; primitivas privadas requieren
    # caller interno confiable y no son endpoints ni entrada de payload tenant.
    if await db.scalar(text("SELECT current_user")) != "eipd_policy_admin":
        raise PermissionError("Canal administrativo EIPD requerido")


async def read_eipd_policy_audit_snapshot_v1(db):
    """Una lectura SQL coherente; sin locks/escrituras/cache/fallback."""
    raw = await db.scalar(text(_SNAPSHOT_SQL))
    publications = []
    for row in raw["publications"]:
        policy = row["payload"]
        if row["policy_version"] != policy.get("policy_version") or row[
            "policy_reference"
        ] != policy.get("policy_reference"):
            raise ValueError("Identidad de publicacion incoherente")
        publications.append(
            dict(
                id=row["id"],
                policy=policy,
                policy_hash=row["policy_hash"],
                created_by=row["created_by"],
                created_at=row["created_at"],
                rationale=row["rationale"],
                evidence_reference=row["evidence_reference"],
            )
        )
    selector = raw["selector"]
    if selector is not None:
        selector = {
            key: selector[key] for key in ("revision", "publication_id", "selection_id")
        }
    return _validated(
        EipdPolicyAuditSnapshotV1,
        dict(
            publications=publications,
            selections=raw["selections"],
            selector=selector,
        ),
    )


async def read_selected_eipd_policy_v1(db):
    """Lectura orientativa validada; no garantiza estabilidad hasta commit."""
    state = await read_eipd_policy_audit_snapshot_v1(db)
    if state.selector is None:
        raise ValueError("Politica seleccionada no disponible")
    return next(p for p in state.publications if p.id == state.selector.publication_id)


async def _publish_eipd_policy_v1(
    db, policy, *, actor_id, rationale, evidence_reference
):
    await _require_admin(db)
    publication = build_eipd_policy_publication_v1(
        policy,
        publication_id=uuid4(),
        actor_id=actor_id,
        created_at=await db.scalar(text("SELECT clock_timestamp()")),
        rationale=rationale,
        evidence_reference=evidence_reference,
    )
    # Activacion real requiere fuentes/aceptacion y matriz operacional pendientes.
    if publication.policy.activation != "deshabilitada":
        raise ValueError("Publicacion habilitada aun no admitida por este canal")
    if (
        await db.scalar(
            select(EipdPolicyPublication.id).where(
                EipdPolicyPublication.policy_reference
                == publication.policy.policy_reference
            )
        )
        is not None
    ):
        raise ValueError("Referencia de politica ya registrada")
    row = EipdPolicyPublication(
        id=publication.id,
        policy_version=publication.policy.policy_version,
        policy_reference=publication.policy.policy_reference,
        policy_hash=publication.policy_hash,
        payload=publication.policy.model_dump(mode="json"),
        created_by=publication.created_by,
        created_at=publication.created_at,
        rationale=publication.rationale,
        evidence_reference=publication.evidence_reference,
    )
    db.add(row)
    await db.flush()
    return publication


async def _select_eipd_policy_v1(
    db, request, *, actor_id, rationale, evidence_reference
):
    """Advisory -> selector FOR UPDATE; caller conserva transaccion hasta commit."""
    await _require_admin(db)
    request = _validated(EipdPolicySelectionRequestV1, request)
    await db.execute(
        text("SELECT pg_advisory_xact_lock(:key)"), {"key": _SELECTION_LOCK}
    )
    await db.scalar(
        select(EipdPolicySelector)
        .where(EipdPolicySelector.id == 1)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    state = await read_eipd_policy_audit_snapshot_v1(db)
    plan = plan_eipd_policy_selection_v1(
        state,
        request,
        event_id=uuid4(),
        actor_id=actor_id,
        created_at=await db.scalar(text("SELECT clock_timestamp()")),
        rationale=rationale,
        evidence_reference=evidence_reference,
    )
    publication = next(
        p for p in state.publications if p.id == plan.selector.publication_id
    )
    if publication.policy.activation != "deshabilitada":
        raise ValueError("Seleccion habilitada aun no admitida por este canal")
    db.add(EipdPolicySelection(**plan.event.model_dump(mode="python")))
    await db.flush()
    selector = await db.get(EipdPolicySelector, 1)
    values = plan.selector.model_dump(mode="python")
    if selector is None:
        db.add(EipdPolicySelector(id=1, **values))
    else:
        for key, value in values.items():
            setattr(selector, key, value)
    await db.flush()
    return plan


async def lock_eipd_policy_selector_v1(db, *, require_selector=True):
    """Advisory compartido -> selector FOR SHARE; nunca llamar tras lock de serie.

    Funcion DB limitada comprueba actor registrado. Caller conserva transaccion y
    permisos de accion; no cambia privilegios ni politica. Selector ausente falla
    cerrado por defecto, incluso durante bootstrap. require_selector=False mantiene
    el advisory compartido aunque falte selector: confirmacion revalida bajo serie
    y exige politica solo en ambito EIPD. Locks hasta commit/rollback.
    """
    if await db.scalar(text("SHOW transaction_isolation")) != "read committed":
        raise ValueError("Resolver transaccional EIPD exige READ COMMITTED")
    present = await db.scalar(text("SELECT public.lock_eipd_policy_selector_v1()"))
    if require_selector and not present:
        raise ValueError("Politica seleccionada no disponible")
    return present


async def resolve_eipd_policy_snapshot_for_transaction_v1(db):
    """Snapshot validado tras espera, con locks retenidos hasta commit/rollback.

    Sin cache, fallback, bootstrap ni activacion. Acciones conectadas §§95–96;
    caller debe adoptar orden selector -> serie
    y revalidar sus controles.
    """
    await lock_eipd_policy_selector_v1(db)
    state = await read_eipd_policy_audit_snapshot_v1(db)
    if state.selector is None:
        raise ValueError("Politica seleccionada no disponible")
    return state


async def authorize_eipd_personal_actor_v1(db):
    """Sub verificado por caller; perfil -> advisory -> selector en pasos siguientes.

    Retiene FOR SHARE hasta commit/rollback, sin cache ni actor del cliente.
    SQL no autentica criptograficamente JWT; conexion separada de servidor requerida.
    Conectado a entradas personales publish/select; primitivas privadas para setup
    confiable/interno, nunca sustituir entrada personal en transporte administrativo.
    """
    await _require_admin(db)
    if await db.scalar(text("SHOW transaction_isolation")) != "read committed":
        raise ValueError("Autoridad personal exige READ COMMITTED")
    return await db.scalar(text("SELECT public.lock_eipd_personal_authority_v1()"))


async def publish_eipd_policy_v1(db, policy, *, rationale, evidence_reference):
    """Entrada personal: actor derivado, perfil bloqueado antes de escribir."""
    actor = await authorize_eipd_personal_actor_v1(db)
    return await _publish_eipd_policy_v1(
        db,
        policy,
        actor_id=actor,
        rationale=rationale,
        evidence_reference=evidence_reference,
    )


async def select_eipd_policy_v1(db, request, *, rationale, evidence_reference):
    """Perfil autorizado -> advisory exclusivo -> selector exclusivo; sin commit."""
    actor = await authorize_eipd_personal_actor_v1(db)
    return await _select_eipd_policy_v1(
        db,
        request,
        actor_id=actor,
        rationale=rationale,
        evidence_reference=evidence_reference,
    )
