"""treatment status changed timestamp

Revision ID: 48fe0b9c21e4
Revises: 267224e9b9e6
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "48fe0b9c21e4"
down_revision: str | None = "267224e9b9e6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "treatments",
        sa.Column(
            "status_changed_at",
            sa.TIMESTAMP(timezone=True),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("treatments", "status_changed_at")
