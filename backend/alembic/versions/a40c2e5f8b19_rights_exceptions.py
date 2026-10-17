"""Add nullable sensitive and biometric rights exception assessments."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "a40c2e5f8b19"
down_revision = "f39b1d4e7a08"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "legal_assessments",
        sa.Column(
            "sensitive_rights_exception_assessment", postgresql.JSONB(), nullable=True
        ),
    )
    op.create_check_constraint(
        "ck_legal_assessments_sensitive_rights_exception_object",
        "legal_assessments",
        "sensitive_rights_exception_assessment IS NULL OR jsonb_typeof(sensitive_rights_exception_assessment) = 'object'",
    )
    op.add_column(
        "legal_assessments",
        sa.Column(
            "biometric_rights_exception_assessment", postgresql.JSONB(), nullable=True
        ),
    )
    op.create_check_constraint(
        "ck_legal_assessments_biometric_rights_exception_object",
        "legal_assessments",
        "biometric_rights_exception_assessment IS NULL OR jsonb_typeof(biometric_rights_exception_assessment) = 'object'",
    )


def downgrade():
    op.drop_constraint(
        "ck_legal_assessments_biometric_rights_exception_object",
        "legal_assessments",
        type_="check",
    )
    op.drop_column("legal_assessments", "biometric_rights_exception_assessment")
    op.drop_constraint(
        "ck_legal_assessments_sensitive_rights_exception_object",
        "legal_assessments",
        type_="check",
    )
    op.drop_column("legal_assessments", "sensitive_rights_exception_assessment")
