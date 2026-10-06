"""Add nullable rights defense assessment to legal assessments."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "ae4c6e8b2f53"
down_revision = "9e3b5d7f1a42"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "legal_assessments",
        sa.Column("rights_defense_assessment", postgresql.JSONB(), nullable=True),
    )
    op.create_check_constraint(
        "ck_legal_assessments_rights_defense_object",
        "legal_assessments",
        "rights_defense_assessment IS NULL OR jsonb_typeof(rights_defense_assessment) = 'object'",
    )


def downgrade():
    op.drop_constraint(
        "ck_legal_assessments_rights_defense_object",
        "legal_assessments",
        type_="check",
    )
    op.drop_column("legal_assessments", "rights_defense_assessment")
