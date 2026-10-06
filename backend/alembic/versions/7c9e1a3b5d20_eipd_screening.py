"""Add nullable EIPD screening to legal assessments.

Revision ID: 7c9e1a3b5d20
Revises: 5997a757f17b
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "7c9e1a3b5d20"
down_revision = "5997a757f17b"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "legal_assessments",
        sa.Column("eipd_screening", postgresql.JSONB(), nullable=True),
    )
    op.create_check_constraint(
        "ck_legal_assessments_eipd_screening_object",
        "legal_assessments",
        "eipd_screening IS NULL OR jsonb_typeof(eipd_screening) = 'object'",
    )


def downgrade():
    op.drop_constraint(
        "ck_legal_assessments_eipd_screening_object", "legal_assessments", type_="check"
    )
    op.drop_column("legal_assessments", "eipd_screening")
