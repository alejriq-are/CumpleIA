"""Add nullable geolocation assessment to legal assessments."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "c06e8a1d4b75"
down_revision = "bf5d7f9c3a64"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "legal_assessments",
        sa.Column("geolocation_assessment", postgresql.JSONB(), nullable=True),
    )
    op.create_check_constraint(
        "ck_legal_assessments_geolocation_object",
        "legal_assessments",
        "geolocation_assessment IS NULL OR jsonb_typeof(geolocation_assessment) = 'object'",
    )


def downgrade():
    op.drop_constraint(
        "ck_legal_assessments_geolocation_object",
        "legal_assessments",
        type_="check",
    )
    op.drop_column("legal_assessments", "geolocation_assessment")
