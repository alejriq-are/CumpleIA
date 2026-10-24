"""Add nullable biometric assessment to legal assessments."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "f39b1d4e7a08"
down_revision = "e28a0c3f6d97"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "legal_assessments",
        sa.Column("biometric_assessment", postgresql.JSONB(), nullable=True),
    )
    op.create_check_constraint(
        "ck_legal_assessments_biometric_object",
        "legal_assessments",
        "biometric_assessment IS NULL OR jsonb_typeof(biometric_assessment) = 'object'",
    )


def downgrade():
    op.drop_constraint(
        "ck_legal_assessments_biometric_object",
        "legal_assessments",
        type_="check",
    )
    op.drop_column("legal_assessments", "biometric_assessment")
