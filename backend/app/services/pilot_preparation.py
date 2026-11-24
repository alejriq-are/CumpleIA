"""Evalua referencias ficticias, sin convertirlas en decisiones persistidas."""

from fastapi import HTTPException

from app.schemas.pilot_preparation import PilotPreparationOut
from app.services import mvp_dossier
from app.services import organization_acceptance as acceptance

REFERENCE_FIELDS = (
    "review_reference",
    "environment_reference",
    "access_reference",
    "restore_reference",
    "retention_reference",
    "support_reference",
    "incident_reference",
)


async def prepare(db, org, tid, aid, actor, payload):
    # build valida entorno y comparte serie: revocacion/escritura espera hasta fin.
    dossier = await mvp_dossier.build(db, org, tid, aid)
    await acceptance.member(db, org, actor)
    grant = await acceptance.latest(db, org, aid, actor)
    if grant is None or grant.action != "otorgar" or grant.id != payload.authority_id:
        raise HTTPException(
            403, detail="Facultad explicita vigente requerida para simulacion"
        )
    hashes = {d.kind: d.content_hash for d in dossier.documents}
    if payload.document_hashes != hashes:
        raise HTTPException(
            409, detail="Documentos cambiaron; consultar expediente antes de preparar"
        )
    refs = {k: getattr(payload, k) for k in REFERENCE_FIELDS}
    missing = [k for k, v in refs.items() if not v] + [
        k for k, v in hashes.items() if v is None
    ]
    if payload.review_decision != "acepta":
        missing.append("revision_juridica_ficticia_no_aceptada")
    return PilotPreparationOut(
        organization_id=org,
        treatment_id=tid,
        assessment_id=aid,
        actor_id=actor,
        authority_id=grant.id,
        authority_evidence_reference=grant.evidence_reference,
        document_hashes=hashes,
        declared_references=refs,
        review_decision=payload.review_decision,
        missing=missing,
        preparation_complete=not missing,
    )


async def simulate_act(db, org, tid, aid, actor, payload):
    from copy import deepcopy

    from app.schemas.pilot_preparation import SIMULATION_SCENARIO, PilotSimulationOut

    prepared = await prepare(db, org, tid, aid, actor, payload)
    value = prepared.model_dump(
        mode="python", exclude={"schema_version", "authority_evidence_reference"}
    )
    return PilotSimulationOut(
        **value,
        act_reference=payload.act_reference,
        designation_reference=payload.designation_reference,
        authority_evidence_reference="SIMULADA-ENLACE-FACULTAD-"
        + str(prepared.authority_id).upper(),
        scenario=deepcopy(SIMULATION_SCENARIO),
        legal_review_status=(
            "pendiente_no_realizada"
            if payload.review_decision == "pendiente"
            else "simulada_sin_valor_juridico"
        ),
    )
