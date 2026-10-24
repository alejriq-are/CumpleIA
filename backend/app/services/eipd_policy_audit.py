"""Contratos puros §90. No DB, autorizacion, reloj ni resolver activo."""

from datetime import UTC, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StrictInt, model_validator

from app.services.eipd_controls import (
    EipdControlCompositionInputV1,
    compose_eipd_controls_v2,
)
from app.services.eipd_policy import (
    EipdGatePolicyV1,
    EipdReviewPolicyIdentityV1,
    Hash,
    Text,
    build_eipd_policy_hash_v1,
)


class AuditModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid", frozen=True, revalidate_instances="always"
    )


def _utc(value):
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Fecha datetime con zona explicita requerida")
    return value.astimezone(UTC)


def _validated(model, value):
    raw = value.model_dump(mode="python") if isinstance(value, BaseModel) else value
    parsed = model.model_validate(raw)
    return model.model_validate(parsed.model_dump(mode="python"))


class EipdPolicyPublicationV1(AuditModel):
    id: UUID
    policy: EipdGatePolicyV1
    policy_hash: Hash
    created_by: UUID
    created_at: datetime
    rationale: Text
    evidence_reference: Text

    @model_validator(mode="after")
    def coherent(self):
        object.__setattr__(self, "created_at", _utc(self.created_at))
        if self.policy_hash != build_eipd_policy_hash_v1(self.policy):
            raise ValueError("Hash de publicacion incoherente")
        return self


class EipdPolicySelectionV1(AuditModel):
    id: UUID
    previous_revision: StrictInt = Field(ge=0)
    revision: StrictInt = Field(ge=1)
    previous_publication_id: UUID | None
    previous_policy_hash: Hash | None
    publication_id: UUID
    policy_hash: Hash
    created_by: UUID
    created_at: datetime
    rationale: Text
    evidence_reference: Text

    @model_validator(mode="after")
    def coherent(self):
        object.__setattr__(self, "created_at", _utc(self.created_at))
        if self.revision != self.previous_revision + 1:
            raise ValueError("Revision de seleccion no consecutiva")
        empty = (
            self.previous_publication_id is None and self.previous_policy_hash is None
        )
        full = (
            self.previous_publication_id is not None
            and self.previous_policy_hash is not None
        )
        if not (
            (self.previous_revision == 0 and empty)
            or (self.previous_revision > 0 and full)
        ):
            raise ValueError("Identidad anterior incompleta")
        if self.publication_id == self.previous_publication_id:
            raise ValueError("Reseleccion de publicacion prohibida")
        return self


class EipdPolicySelectorV1(AuditModel):
    revision: StrictInt = Field(ge=1)
    publication_id: UUID
    selection_id: UUID


class EipdPolicyAuditSnapshotV1(AuditModel):
    publications: tuple[EipdPolicyPublicationV1, ...]
    selections: tuple[EipdPolicySelectionV1, ...]
    selector: EipdPolicySelectorV1 | None

    @model_validator(mode="after")
    def coherent(self):
        publications = {p.id: p for p in self.publications}
        references = {p.policy.policy_reference for p in self.publications}
        if len(publications) != len(self.publications) or len(references) != len(
            self.publications
        ):
            raise ValueError("Publicacion/referencia duplicada")
        if len({e.id for e in self.selections}) != len(self.selections):
            raise ValueError("Evento duplicado")
        previous = None
        used = set()
        for revision, event in enumerate(self.selections, 1):
            publication = publications.get(event.publication_id)
            if publication is None or event.policy_hash != publication.policy_hash:
                raise ValueError("Publicacion de evento ausente/incoherente")
            if event.revision != revision or event.previous_revision != revision - 1:
                raise ValueError("Cadena de revisiones incompleta")
            if event.created_at < publication.created_at:
                raise ValueError("Seleccion anterior a publicacion")
            if previous and (
                event.previous_publication_id != previous.publication_id
                or event.previous_policy_hash != previous.policy_hash
                or event.created_at < previous.created_at
            ):
                raise ValueError("Cadena anterior incoherente")
            if event.publication_id in used:
                raise ValueError("Publicacion ya seleccionada")
            used.add(event.publication_id)
            previous = event
        if previous is None:
            if self.selector is not None:
                raise ValueError("Selector sin auditoria")
        elif self.selector is None or (
            self.selector.revision != previous.revision
            or self.selector.publication_id != previous.publication_id
            or self.selector.selection_id != previous.id
        ):
            raise ValueError("Selector no coincide con ultimo evento")
        return self


class EipdPolicySelectionRequestV1(AuditModel):
    expected_revision: StrictInt = Field(ge=0)
    publication_id: UUID


class EipdPolicySelectionPlanV1(AuditModel):
    event: EipdPolicySelectionV1
    selector: EipdPolicySelectorV1

    @model_validator(mode="after")
    def coherent(self):
        if (
            self.event.id != self.selector.selection_id
            or self.event.revision != self.selector.revision
            or self.event.publication_id != self.selector.publication_id
        ):
            raise ValueError("Plan de seleccion incoherente")
        return self


def build_eipd_policy_publication_v1(
    policy, *, publication_id, actor_id, created_at, rationale, evidence_reference
):
    return EipdPolicyPublicationV1.model_validate(
        dict(
            id=publication_id,
            policy=policy,
            policy_hash=build_eipd_policy_hash_v1(policy),
            created_by=actor_id,
            created_at=_utc(created_at),
            rationale=rationale,
            evidence_reference=evidence_reference,
        )
    )


def plan_eipd_policy_selection_v1(
    snapshot, request, *, event_id, actor_id, created_at, rationale, evidence_reference
):
    """Caller verifica autoridad, historia completa y locks; plan no escribe."""
    state = _validated(EipdPolicyAuditSnapshotV1, snapshot)
    request = _validated(EipdPolicySelectionRequestV1, request)
    current = state.selector.revision if state.selector else 0
    if request.expected_revision != current:
        raise ValueError("Revision esperada obsoleta")
    publication = next(
        (p for p in state.publications if p.id == request.publication_id), None
    )
    if publication is None:
        raise ValueError("Publicacion no registrada")
    if any(e.publication_id == publication.id for e in state.selections):
        raise ValueError("Publicacion ya seleccionada")
    previous = state.selections[-1] if state.selections else None
    event = EipdPolicySelectionV1.model_validate(
        dict(
            id=event_id,
            previous_revision=current,
            revision=current + 1,
            previous_publication_id=previous.publication_id if previous else None,
            previous_policy_hash=previous.policy_hash if previous else None,
            publication_id=publication.id,
            policy_hash=publication.policy_hash,
            created_by=actor_id,
            created_at=_utc(created_at),
            rationale=rationale,
            evidence_reference=evidence_reference,
        )
    )
    selector = EipdPolicySelectorV1(
        revision=event.revision, publication_id=publication.id, selection_id=event.id
    )
    _validated(
        EipdPolicyAuditSnapshotV1,
        dict(
            publications=state.publications,
            selections=(*state.selections, event),
            selector=selector,
        ),
    )
    return EipdPolicySelectionPlanV1(event=event, selector=selector)


class EipdConfirmationEvidenceV1(AuditModel):
    id: UUID
    organization_id: UUID
    assessment_id: UUID
    review_id: UUID
    publication_id: UUID
    selector_revision: StrictInt = Field(ge=1)
    selection_id: UUID
    policy_version: StrictInt = Field(ge=1, le=1)
    policy_reference: Text
    policy_hash: Hash
    document_hash: Hash
    context_hash: Hash
    created_by: UUID
    created_at: datetime

    @model_validator(mode="after")
    def coherent(self):
        object.__setattr__(self, "created_at", _utc(self.created_at))
        return self


def build_eipd_confirmation_evidence_v1(
    snapshot, assessment, review_policy, *, evidence_id, actor_id, created_at
):
    """Recompute controles; no acredita permisos, locks ni commit atomico."""
    state = _validated(EipdPolicyAuditSnapshotV1, snapshot)
    if state.selector is None:
        raise ValueError("Selector ausente")
    created_at = _utc(created_at)
    selection = state.selections[-1]
    if created_at < selection.created_at:
        raise ValueError("Evidencia anterior a seleccion")
    publication = next(
        p for p in state.publications if p.id == state.selector.publication_id
    )
    assessment = _validated(EipdControlCompositionInputV1, assessment)
    identity = _validated(EipdReviewPolicyIdentityV1, review_policy)
    controls = compose_eipd_controls_v2(
        dict(
            assessment=assessment,
            policy=publication.policy,
            latest_review_policy=identity,
        ),
        evaluated_on=created_at.date(),
    )
    if controls.confirmation_blockers:
        raise ValueError("Controles de confirmacion no preparados")
    review = assessment.latest_review
    if created_at < review.created_at:
        raise ValueError("Evidencia anterior a revision humana")
    return EipdConfirmationEvidenceV1.model_validate(
        dict(
            id=evidence_id,
            organization_id=assessment.organization_id,
            assessment_id=assessment.assessment_id,
            review_id=review.id,
            publication_id=publication.id,
            selector_revision=selection.revision,
            selection_id=selection.id,
            policy_version=publication.policy.policy_version,
            policy_reference=publication.policy.policy_reference,
            policy_hash=publication.policy_hash,
            document_hash=review.document_hash,
            context_hash=review.context_hash,
            created_by=actor_id,
            created_at=created_at,
        )
    )
