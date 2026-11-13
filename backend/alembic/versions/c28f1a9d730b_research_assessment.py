"""Add nullable research assessment without backfill."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "c28f1a9d730b"
down_revision = "b17d95c0286f"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "legal_assessments",
        sa.Column("research_assessment", postgresql.JSONB(), nullable=True),
    )
    op.create_check_constraint(
        "ck_legal_assessments_research_object",
        "legal_assessments",
        "research_assessment IS NULL OR jsonb_typeof(research_assessment) = 'object'",
    )


def downgrade():
    op.drop_constraint(
        "ck_legal_assessments_research_object", "legal_assessments", type_="check"
    )
    op.drop_column("legal_assessments", "research_assessment")
