"""Resolucion EIPD y eventos de revision con RLS desde su creacion.

Revision ID: b51d3f6a9c20
Revises: a40c2e5f8b19
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "b51d3f6a9c20"
down_revision = "a40c2e5f8b19"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "legal_assessments",
        sa.Column(
            "eipd_resolution_assessment",
            postgresql.JSONB(none_as_null=True),
            nullable=True,
        ),
    )
    op.create_check_constraint(
        "ck_legal_assessments_eipd_resolution_object",
        "legal_assessments",
        "eipd_resolution_assessment IS NULL OR jsonb_typeof(eipd_resolution_assessment) = 'object'",
    )
    op.create_unique_constraint(
        "uq_legal_assessments_id_tenant", "legal_assessments", ["id", "organization_id"]
    )
    op.create_table(
        "eipd_resolution_reviews",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column("assessment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("decision", sa.Text(), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("review_reference", sa.Text(), nullable=False),
        sa.Column("document_hash", sa.Text(), nullable=False),
        sa.Column("context_hash", sa.Text(), nullable=False),
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("profiles.id"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("clock_timestamp()"),
        ),
        sa.ForeignKeyConstraint(
            ["assessment_id", "organization_id"],
            ["legal_assessments.id", "legal_assessments.organization_id"],
            name="fk_eipd_resolution_reviews_assessment_tenant",
        ),
        sa.CheckConstraint(
            "decision IN ('continuar', 'requiere_cambios', 'no_continuar')",
            name="ck_eipd_resolution_reviews_decision",
        ),
        sa.CheckConstraint(
            "rationale ~ '[^[:space:]]'", name="ck_eipd_resolution_reviews_rationale"
        ),
        sa.CheckConstraint(
            "review_reference ~ '[^[:space:]]'",
            name="ck_eipd_resolution_reviews_reference",
        ),
        sa.CheckConstraint(
            "document_hash ~ '^[0-9a-f]{64}$'",
            name="ck_eipd_resolution_reviews_document_hash",
        ),
        sa.CheckConstraint(
            "context_hash ~ '^[0-9a-f]{64}$'",
            name="ck_eipd_resolution_reviews_context_hash",
        ),
    )
    op.create_index(
        "ix_eipd_resolution_reviews_organization_id",
        "eipd_resolution_reviews",
        ["organization_id"],
    )
    op.create_index(
        "ix_eipd_resolution_reviews_assessment_history",
        "eipd_resolution_reviews",
        ["organization_id", "assessment_id", "created_at", "id"],
    )
    op.execute("ALTER TABLE eipd_resolution_reviews ENABLE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY tenant_isolation_select ON eipd_resolution_reviews "
        "FOR SELECT USING (organization_id IN (SELECT auth_org_ids()))"
    )
    op.execute(
        "CREATE POLICY tenant_isolation_insert ON eipd_resolution_reviews "
        "FOR INSERT WITH CHECK (organization_id IN (SELECT auth_org_ids()) "
        "AND created_by IN (SELECT id FROM profiles WHERE auth_user_id = auth.uid()) "
        "AND EXISTS (SELECT 1 FROM legal_assessments a "
        "WHERE a.id = assessment_id AND a.organization_id = eipd_resolution_reviews.organization_id "
        "AND a.status = 'borrador' AND a.eipd_resolution_assessment IS NOT NULL))"
    )
    # Default privileges heredados conceden UPDATE/DELETE: retirar explicitamente.
    op.execute("REVOKE ALL ON eipd_resolution_reviews FROM PUBLIC")
    op.execute(
        "REVOKE UPDATE, DELETE, TRUNCATE ON eipd_resolution_reviews FROM app_user"
    )
    op.execute("GRANT SELECT, INSERT ON eipd_resolution_reviews TO app_user")


def downgrade() -> None:
    op.drop_table("eipd_resolution_reviews")
    op.drop_constraint(
        "uq_legal_assessments_id_tenant", "legal_assessments", type_="unique"
    )
    op.drop_constraint(
        "ck_legal_assessments_eipd_resolution_object",
        "legal_assessments",
        type_="check",
    )
    op.drop_column("legal_assessments", "eipd_resolution_assessment")
