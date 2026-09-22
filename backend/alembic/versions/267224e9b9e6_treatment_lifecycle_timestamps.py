"""treatment lifecycle timestamps

Revision ID: 267224e9b9e6
Revises: f4a5b6c7d8e9
Create Date: 2026-09-22 12:22:23.992810
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "267224e9b9e6"
down_revision: str | None = "f4a5b6c7d8e9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "treatments",
        sa.Column(
            "activated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=True,
        ),
    )
    op.add_column(
        "treatments",
        sa.Column(
            "archived_at",
            sa.TIMESTAMP(timezone=True),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("treatments", "archived_at")
    op.drop_column("treatments", "activated_at")
