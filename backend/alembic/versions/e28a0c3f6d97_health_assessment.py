"""Add nullable health assessment to legal assessments."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "e28a0c3f6d97"
down_revision = "d17f9b2e5c86"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "legal_assessments",
        sa.Column("health_assessment", postgresql.JSONB(), nullable=True),
    )
    op.create_check_constraint(
        "ck_legal_assessments_health_object",
        "legal_assessments",
        "health_assessment IS NULL OR jsonb_typeof(health_assessment) = 'object'",
    )


def downgrade():
    op.drop_constraint(
        "ck_legal_assessments_health_object",
        "legal_assessments",
        type_="check",
    )
    op.drop_column("legal_assessments", "health_assessment")
