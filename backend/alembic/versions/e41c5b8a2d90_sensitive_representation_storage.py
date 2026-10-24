"""Representacion nullable, sin backfill y sin confirmacion.

Revision ID: e41c5b8a2d90
Revises: d39e2b0f841c
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "e41c5b8a2d90"
down_revision = "d39e2b0f841c"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "legal_assessments",
        sa.Column(
            "sensitive_representation_assessment", postgresql.JSONB(), nullable=True
        ),
    )
    op.create_check_constraint(
        "ck_legal_assessments_sensitive_representation_object",
        "legal_assessments",
        "sensitive_representation_assessment IS NULL OR jsonb_typeof(sensitive_representation_assessment) = 'object'",
    )
    op.create_check_constraint(
        "ck_legal_assessments_sensitive_representation_no_confirmation",
        "legal_assessments",
        "sensitive_representation_assessment IS NULL OR status <> 'confirmado'",
    )


def downgrade():
    op.drop_constraint(
        "ck_legal_assessments_sensitive_representation_no_confirmation",
        "legal_assessments",
        type_="check",
    )
    op.drop_constraint(
        "ck_legal_assessments_sensitive_representation_object",
        "legal_assessments",
        type_="check",
    )
    op.drop_column("legal_assessments", "sensitive_representation_assessment")
