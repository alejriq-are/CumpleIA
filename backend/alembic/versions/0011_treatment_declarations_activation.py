"""M2-T3.0: declaraciones explícitas de Treatment.

Revision ID: f4a5b6c7d8e9
Revises: e3f4a5b6c7d8
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "f4a5b6c7d8e9"
down_revision: str | None = "e3f4a5b6c7d8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_FIELDS = (
    "systems_declaration",
    "vendors_declaration",
    "international_transfers_declaration",
)


def upgrade() -> None:
    for field in _FIELDS:
        op.add_column("treatments", sa.Column(field, sa.Text(), nullable=True))
        op.create_check_constraint(
            f"ck_treatments_{field}",
            "treatments",
            f"{field} IS NULL OR {field} IN ('si', 'no', 'pendiente')",
        )


def downgrade() -> None:
    for field in reversed(_FIELDS):
        op.drop_constraint(f"ck_treatments_{field}", "treatments", type_="check")
        op.drop_column("treatments", field)
