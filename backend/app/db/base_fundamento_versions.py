"""Immutable registered versions of Base y fundamento."""

import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class BaseFundamentoVersion(Base):
    __tablename__ = "base_fundamento_versions"
    __table_args__ = (
        sa.UniqueConstraint(
            "id",
            "assessment_id",
            "treatment_id",
            "organization_id",
            name="uq_base_fundamento_version_scope",
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
            "assessment_id", "version", name="uq_base_fundamento_number"
        ),
        sa.UniqueConstraint(
            "organization_id",
            "created_by",
            "request_id",
            name="uq_base_fundamento_request",
        ),
        sa.CheckConstraint(
            "version > 0 AND data_kind='ficticios'",
            name="base_fundamento_version_fictitious",
        ),
        sa.CheckConstraint(
            "length(btrim(reason)) > 0", name="base_fundamento_version_reason"
        ),
        sa.CheckConstraint(
            "source_hash ~ '^[0-9a-f]{64}$' AND input_hash ~ '^[0-9a-f]{64}$' AND bundle_hash ~ '^[0-9a-f]{64}$'",
            name="base_fundamento_version_hashes",
        ),
    )
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    treatment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    assessment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("profiles.id", ondelete="RESTRICT")
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), server_default=sa.func.clock_timestamp()
    )
    request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    version: Mapped[int] = mapped_column(sa.Integer)
    data_kind: Mapped[str] = mapped_column(sa.Text)
    reason: Mapped[str] = mapped_column(sa.Text)
    source_hash: Mapped[str] = mapped_column(sa.Text)
    input_hash: Mapped[str] = mapped_column(sa.Text)
    bundle_hash: Mapped[str] = mapped_column(sa.Text)
    bundle: Mapped[dict] = mapped_column(JSONB)
