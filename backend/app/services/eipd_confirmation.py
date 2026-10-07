"""Evidencia interna; caller conserva locks selector -> serie y transaccion.

No endpoint, permisos nuevos, bootstrap ni activacion. El caller arma el contexto
actual bajo locks; constructor puro recompone controles y DB impone RLS/FK.
"""

from uuid import uuid4

from sqlalchemy import text

from app.db.models import EipdConfirmationEvidence
from app.services.eipd_policy_audit import build_eipd_confirmation_evidence_v1
from app.services.eipd_policy_store import read_eipd_policy_audit_snapshot_v1


async def record_eipd_confirmation_evidence_v1(
    db, assessment, review_policy, *, actor_id
):
    snapshot = await read_eipd_policy_audit_snapshot_v1(db)
    evidence = build_eipd_confirmation_evidence_v1(
        snapshot,
        assessment,
        review_policy,
        evidence_id=uuid4(),
        actor_id=actor_id,
        created_at=await db.scalar(text("SELECT clock_timestamp()")),
    )
    row = EipdConfirmationEvidence(**evidence.model_dump(mode="python"))
    db.add(row)
    # RLS exige borrador y ultima revision positiva: antes de cambiar status.
    await db.flush()
    return row
