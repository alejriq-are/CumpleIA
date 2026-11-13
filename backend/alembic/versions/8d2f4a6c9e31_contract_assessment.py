"""Add nullable contractual assessment to legal assessments."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "8d2f4a6c9e31"
down_revision = "7c9e1a3b5d20"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "legal_assessments",
        sa.Column("contract_assessment", postgresql.JSONB(), nullable=True),
    )
    op.create_check_constraint(
        "ck_legal_assessments_contract_assessment_object",
        "legal_assessments",
        "contract_assessment IS NULL OR jsonb_typeof(contract_assessment) = 'object'",
    )


def downgrade():
    op.drop_constraint(
        "ck_legal_assessments_contract_assessment_object",
        "legal_assessments",
        type_="check",
    )
    op.drop_column("legal_assessments", "contract_assessment")
