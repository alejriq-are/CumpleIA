"""Append-only applicability alongside documentary support; retain tenant policies."""

from alembic import op

revision = "f6a24c8e9102"
down_revision = "e67a4b829c10"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "ALTER TABLE assessment_support_records DROP CONSTRAINT ck_assessment_support_records_support_kind"
    )
    op.execute(
        "ALTER TABLE assessment_support_records ADD CONSTRAINT ck_assessment_support_records_support_kind CHECK (kind IN ('risk','annex','applicability'))"
    )
    op.execute(
        "ALTER TABLE assessment_support_records DROP CONSTRAINT ck_assessment_support_records_support_content"
    )
    op.execute(
        "ALTER TABLE assessment_support_records ADD CONSTRAINT ck_assessment_support_records_support_content CHECK ((kind IN ('risk','applicability') AND content IS NULL) OR (kind='annex' AND content IS NOT NULL AND octet_length(content) BETWEEN 1 AND 2097152))"
    )


def downgrade():
    raise RuntimeError("Historial protegido: no se elimina automaticamente")
