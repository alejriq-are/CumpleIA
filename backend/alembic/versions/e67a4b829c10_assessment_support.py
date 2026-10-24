"""Independent risk methodology and fictitious annexes with tenant isolation."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "e67a4b829c10"
down_revision = "d16a3b7c8e52"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "assessment_support_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("treatment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("assessment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("profiles.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("request_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.clock_timestamp(),
            nullable=False,
        ),
        sa.Column("kind", sa.Text, nullable=False),
        sa.Column("revision", sa.Integer, nullable=False),
        sa.Column("data_kind", sa.Text, nullable=False),
        sa.Column("document_hash", sa.Text, nullable=False),
        sa.Column("payload", postgresql.JSONB, nullable=False),
        sa.Column("content", sa.LargeBinary),
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
    op.execute("ALTER TABLE assessment_support_records ENABLE ROW LEVEL SECURITY")
    op.execute("REVOKE ALL ON assessment_support_records FROM PUBLIC")
    op.execute("GRANT SELECT,INSERT ON assessment_support_records TO app_user")
    op.execute(
        "REVOKE UPDATE,DELETE,TRUNCATE ON assessment_support_records FROM app_user"
    )
    op.execute(
        "CREATE POLICY tenant_read ON assessment_support_records FOR SELECT TO app_user USING (organization_id IN (SELECT auth_org_ids()))"
    )
    op.execute(
        """CREATE POLICY tenant_insert ON assessment_support_records FOR INSERT TO app_user WITH CHECK (
      organization_id IN (SELECT auth_org_ids())
      AND created_by IN (SELECT id FROM profiles WHERE auth_user_id=auth.uid())
      AND EXISTS (SELECT 1 FROM memberships m WHERE m.organization_id=assessment_support_records.organization_id AND m.profile_id=assessment_support_records.created_by AND m.role IN ('owner','admin','editor'))
      AND EXISTS (SELECT 1 FROM subscriptions s WHERE s.organization_id=assessment_support_records.organization_id AND s.status IN ('active','grace'))
      AND EXISTS (SELECT 1 FROM legal_assessments a WHERE a.id=assessment_support_records.assessment_id AND a.organization_id=assessment_support_records.organization_id AND a.treatment_id=assessment_support_records.treatment_id AND a.status='borrador'))"""
    )


def downgrade():
    raise RuntimeError("Historial protegido: no se elimina automaticamente")
