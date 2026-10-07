"""Identidad de politica opcional en eventos EIPD; no reescribe historia.

Revision ID: c62e407bad31
Revises: b51d3f6a9c20
"""

import sqlalchemy as sa

from alembic import op

revision = "c62e407bad31"
down_revision = "b51d3f6a9c20"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "eipd_resolution_reviews",
        sa.Column("policy_version", sa.Integer(), nullable=True),
    )
    op.add_column(
        "eipd_resolution_reviews",
        sa.Column("policy_reference", sa.Text(), nullable=True),
    )
    op.add_column(
        "eipd_resolution_reviews", sa.Column("policy_hash", sa.Text(), nullable=True)
    )
    op.create_check_constraint(
        "ck_eipd_resolution_reviews_policy_identity",
        "eipd_resolution_reviews",
        "(policy_version IS NULL AND policy_reference IS NULL AND policy_hash IS NULL) OR (policy_version IS NOT NULL AND policy_reference IS NOT NULL AND policy_hash IS NOT NULL AND policy_version = 1 AND policy_reference ~ '[^[:space:]]' AND policy_hash ~ '^[0-9a-f]{64}$')",
    )
    # RLS/FK y permisos SELECT/INSERT permanecen; sin backfill ni eventos promovidos.


def downgrade() -> None:
    op.drop_constraint(
        "ck_eipd_resolution_reviews_policy_identity",
        "eipd_resolution_reviews",
        type_="check",
    )
    op.drop_column("eipd_resolution_reviews", "policy_hash")
    op.drop_column("eipd_resolution_reviews", "policy_reference")
    op.drop_column("eipd_resolution_reviews", "policy_version")
