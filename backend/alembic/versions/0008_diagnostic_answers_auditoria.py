"""Trazabilidad de quién respondió el Autodiagnóstico (mejoras al informe)

`diagnostic_answers` solo tenía `created_at`: al editar una respuesta ya
existente el upsert (`ON CONFLICT DO UPDATE`, ver
app/services/diagnostico.py::guardar_respuestas) no tocaba esa columna, así
que no quedaba ningún rastro de cuándo se modificó una respuesta ni quién lo
hizo — hueco respecto a la convención de auditoría de CLAUDE.md ("toda tabla
lleva created_at, updated_at, created_by, updated_by"). Se agrega
`updated_at`/`created_by`/`updated_by`, poblados por el servicio (el upsert
no pasa por el flush de la ORM, así que no basta con `onupdate` en el modelo
para esta tabla en particular).

Sin cambios de RLS: las políticas `tenant_isolation_*` de `diagnostic_answers`
(migración 0005) ya cubren las columnas nuevas.

Revision ID: c1d2e3f4a5b6
Revises: b8c9d0e1f2a3
Create Date: 2026-08-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "c1d2e3f4a5b6"
down_revision: str | None = "b8c9d0e1f2a3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "diagnostic_answers",
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.add_column(
        "diagnostic_answers",
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "diagnostic_answers",
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "diagnostic_answers_created_by_fkey",
        "diagnostic_answers",
        "profiles",
        ["created_by"],
        ["id"],
    )
    op.create_foreign_key(
        "diagnostic_answers_updated_by_fkey",
        "diagnostic_answers",
        "profiles",
        ["updated_by"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "diagnostic_answers_updated_by_fkey", "diagnostic_answers", type_="foreignkey"
    )
    op.drop_constraint(
        "diagnostic_answers_created_by_fkey", "diagnostic_answers", type_="foreignkey"
    )
    op.drop_column("diagnostic_answers", "updated_by")
    op.drop_column("diagnostic_answers", "created_by")
    op.drop_column("diagnostic_answers", "updated_at")
