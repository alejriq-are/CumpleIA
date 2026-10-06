"""Add nullable economic obligations assessment to legal assessments."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "bf5d7f9c3a64"
down_revision = "ae4c6e8b2f53"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "legal_assessments",
        sa.Column("economic_obligations_assessment", postgresql.JSONB(), nullable=True),
    )
    op.create_check_constraint(
        "ck_legal_assessments_economic_obligations_object",
        "legal_assessments",
        "economic_obligations_assessment IS NULL OR jsonb_typeof(economic_obligations_assessment) = 'object'",
    )


def downgrade():
    op.drop_constraint(
        "ck_legal_assessments_economic_obligations_object",
        "legal_assessments",
        type_="check",
    )
    op.drop_column("legal_assessments", "economic_obligations_assessment")
