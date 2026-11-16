"""Append-only fictitious support records; tenant-scoped independent of EIPD V1 hashes."""

import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AssessmentSupportRecord(Base):
    __tablename__ = "assessment_support_records"
    __table_args__ = (
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
            "assessment_id", "kind", "revision", name="uq_assessment_support_revision"
        ),
        sa.UniqueConstraint(
            "assessment_id", "request_id", name="uq_assessment_support_request"
        ),
        sa.CheckConstraint("kind IN ('risk','annex')", name="support_kind"),
        sa.CheckConstraint(
            "revision > 0 AND data_kind='ficticios'", name="support_fictitious"
        ),
        sa.CheckConstraint("document_hash ~ '^[0-9a-f]{64}$'", name="support_hash"),
        sa.CheckConstraint(
            "(kind='risk' AND content IS NULL) OR (kind='annex' AND content IS NOT NULL AND octet_length(content) BETWEEN 1 AND 2097152)",
            name="support_content",
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
    request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), server_default=sa.func.clock_timestamp()
    )
    kind: Mapped[str] = mapped_column(sa.Text)
    revision: Mapped[int] = mapped_column(sa.Integer)
    data_kind: Mapped[str] = mapped_column(sa.Text, default="ficticios")
    document_hash: Mapped[str] = mapped_column(sa.Text)
    payload: Mapped[dict] = mapped_column(JSONB)
    content: Mapped[bytes | None] = mapped_column(sa.LargeBinary)
