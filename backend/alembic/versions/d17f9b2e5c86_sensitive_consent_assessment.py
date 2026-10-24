"""Add nullable sensitive consent assessment to legal assessments."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "d17f9b2e5c86"
down_revision = "c06e8a1d4b75"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "legal_assessments",
        sa.Column("sensitive_consent_assessment", postgresql.JSONB(), nullable=True),
    )
    op.create_check_constraint(
        "ck_legal_assessments_sensitive_consent_object",
        "legal_assessments",
        "sensitive_consent_assessment IS NULL OR jsonb_typeof(sensitive_consent_assessment) = 'object'",
    )


def downgrade():
    op.drop_constraint(
        "ck_legal_assessments_sensitive_consent_object",
        "legal_assessments",
        type_="check",
    )
    op.drop_column("legal_assessments", "sensitive_consent_assessment")
