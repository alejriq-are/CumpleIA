"""Append-only scope reviews retain existing RLS and immutable-record protection."""

from alembic import op

revision = "a84f6e2c9103"
down_revision = "f6a24c8e9102"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "ALTER TABLE assessment_support_records DROP CONSTRAINT ck_assessment_support_records_support_kind"
    )
    op.execute(
        "ALTER TABLE assessment_support_records ADD CONSTRAINT ck_assessment_support_records_support_kind CHECK (kind IN ('risk','annex','applicability','scope'))"
    )
    op.execute(
        "ALTER TABLE assessment_support_records DROP CONSTRAINT ck_assessment_support_records_support_content"
    )
    op.execute(
        "ALTER TABLE assessment_support_records ADD CONSTRAINT ck_assessment_support_records_support_content CHECK ((kind IN ('risk','applicability','scope') AND content IS NULL) OR (kind='annex' AND content IS NOT NULL AND octet_length(content) BETWEEN 1 AND 2097152))"
    )


def downgrade():
    raise RuntimeError("Historial protegido: no se elimina automaticamente")
