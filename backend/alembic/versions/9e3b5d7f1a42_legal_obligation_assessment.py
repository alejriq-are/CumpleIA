"""Add nullable legal obligation assessment to legal assessments."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "9e3b5d7f1a42"
down_revision = "8d2f4a6c9e31"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "legal_assessments",
        sa.Column("legal_obligation_assessment", postgresql.JSONB(), nullable=True),
    )
    op.create_check_constraint(
        "ck_legal_assessments_legal_obligation_object",
        "legal_assessments",
        "legal_obligation_assessment IS NULL OR jsonb_typeof(legal_obligation_assessment) = 'object'",
    )


def downgrade():
    op.drop_constraint(
        "ck_legal_assessments_legal_obligation_object",
        "legal_assessments",
        type_="check",
    )
    op.drop_column("legal_assessments", "legal_obligation_assessment")
