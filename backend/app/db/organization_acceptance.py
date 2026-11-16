"""Facultad explicita y decisiones tenant; historial ficticio separado de politica global."""

import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Identity:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=sa.text("gen_random_uuid()"),
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    treatment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    assessment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    actor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("profiles.id", ondelete="RESTRICT"),
        nullable=False,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("profiles.id", ondelete="RESTRICT"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=sa.func.clock_timestamp(),
    )
    data_kind: Mapped[str] = mapped_column(sa.Text, nullable=False)


class OrganizationAcceptanceAuthority(Identity, Base):
    __tablename__ = "organization_acceptance_authorities"
    __table_args__ = (
        sa.Index(
            "ix_organization_acceptance_authorities_history",
            "organization_id",
            "assessment_id",
            "created_at",
            "id",
        ),
        sa.ForeignKeyConstraint(
            ["assessment_id", "treatment_id", "organization_id"],
            [
                "legal_assessments.id",
                "legal_assessments.treatment_id",
                "legal_assessments.organization_id",
            ],
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "assessment_id", "actor_id", "revision", name="uq_org_authority_revision"
        ),
        sa.UniqueConstraint(
            "id",
            "assessment_id",
            "treatment_id",
            "organization_id",
            "actor_id",
            name="uq_org_authority_identity",
        ),
        sa.CheckConstraint("data_kind='ficticios'", name="data_kind"),
        sa.CheckConstraint("revision>0", name="revision"),
        sa.CheckConstraint("action IN ('otorgar','revocar')", name="action"),
        sa.CheckConstraint(
            "organization_role IN ('responsable','encargado')", name="organization_role"
        ),
        sa.CheckConstraint(
            "organization_role='responsable' OR (responsible_party_reference IS NOT NULL AND btrim(responsible_party_reference)<>'')",
            name="responsible_party",
        ),
        sa.CheckConstraint(
            "btrim(faculty_reference)<>'' AND btrim(evidence_reference)<>''",
            name="evidence",
        ),
    )
    revision: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    action: Mapped[str] = mapped_column(sa.Text, nullable=False)
    organization_role: Mapped[str] = mapped_column(sa.Text, nullable=False)
    responsible_party_reference: Mapped[str | None] = mapped_column(sa.Text)
    faculty_reference: Mapped[str] = mapped_column(sa.Text, nullable=False)
    evidence_reference: Mapped[str] = mapped_column(sa.Text, nullable=False)


class OrganizationDocumentAcceptance(Identity, Base):
    __tablename__ = "organization_document_acceptances"
    __table_args__ = (
        sa.Index(
            "ix_organization_document_acceptances_history",
            "organization_id",
            "assessment_id",
            "created_at",
            "id",
        ),
        sa.ForeignKeyConstraint(
            [
                "authority_id",
                "assessment_id",
                "treatment_id",
                "organization_id",
                "actor_id",
            ],
            [
                "organization_acceptance_authorities.id",
                "organization_acceptance_authorities.assessment_id",
                "organization_acceptance_authorities.treatment_id",
                "organization_acceptance_authorities.organization_id",
                "organization_acceptance_authorities.actor_id",
            ],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            [
                "resolution_id",
                "assessment_id",
                "treatment_id",
                "organization_id",
                "document_hash",
                "context_hash",
                "child_material_hash",
            ],
            [
                "eipd_child_resolutions.id",
                "eipd_child_resolutions.assessment_id",
                "eipd_child_resolutions.treatment_id",
                "eipd_child_resolutions.organization_id",
                "eipd_child_resolutions.document_hash",
                "eipd_child_resolutions.context_hash",
                "eipd_child_resolutions.child_material_hash",
            ],
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint("data_kind='ficticios'", name="data_kind"),
        sa.CheckConstraint(
            "decision IN ('acepta','rechaza','requiere_cambios')", name="decision"
        ),
        sa.CheckConstraint("created_by=actor_id", name="actor_identity"),
        sa.CheckConstraint(
            "document_hash ~ '^[0-9a-f]{64}$' AND context_hash ~ '^[0-9a-f]{64}$' AND child_material_hash ~ '^[0-9a-f]{64}$'",
            name="hashes",
        ),
        sa.CheckConstraint(
            "btrim(rationale)<>'' AND btrim(evidence_reference)<>''", name="evidence"
        ),
    )
    authority_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    resolution_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    decision: Mapped[str] = mapped_column(sa.Text, nullable=False)
    rationale: Mapped[str] = mapped_column(sa.Text, nullable=False)
    evidence_reference: Mapped[str] = mapped_column(sa.Text, nullable=False)
    document_hash: Mapped[str] = mapped_column(sa.Text, nullable=False)
    context_hash: Mapped[str] = mapped_column(sa.Text, nullable=False)
    child_material_hash: Mapped[str] = mapped_column(sa.Text, nullable=False)
