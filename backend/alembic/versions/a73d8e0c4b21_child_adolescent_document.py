"""Documento infancia nullable, sin backfill ni confirmacion.

Revision ID: a73d8e0c4b21
Revises: f52d6c9b3e10
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "a73d8e0c4b21"
down_revision = "f52d6c9b3e10"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "legal_assessments",
        sa.Column("child_adolescent_assessment", postgresql.JSONB(), nullable=True),
    )
    op.create_check_constraint(
        "ck_legal_assessments_child_adolescent_object",
        "legal_assessments",
        "child_adolescent_assessment IS NULL OR jsonb_typeof(child_adolescent_assessment) = 'object'",
    )
    op.create_check_constraint(
        "ck_legal_assessments_child_adolescent_no_confirmation",
        "legal_assessments",
        "child_adolescent_assessment IS NULL OR status <> 'confirmado'",
    )


def downgrade():
    # No permitir perdida de documentos ya aportados.
    count = op.get_bind().scalar(
        sa.text(
            "SELECT count(*) FROM legal_assessments WHERE child_adolescent_assessment IS NOT NULL"
        )
    )
    if count:
        raise RuntimeError("Downgrade bloqueado: existen documentos de infancia")
    op.drop_constraint(
        op.f(
            "ck_legal_assessments_ck_legal_assessments_child_adolescent_no_confirmation"
        ),
        "legal_assessments",
        type_="check",
    )
    op.drop_constraint(
        op.f("ck_legal_assessments_ck_legal_assessments_child_adolescent_object"),
        "legal_assessments",
        type_="check",
    )
    op.drop_column("legal_assessments", "child_adolescent_assessment")
