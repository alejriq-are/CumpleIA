"""Fase 1 / Módulo 1, Tarea 4 — Capa de IA con guardarraíles

Agrega a `diagnostics` el informe narrativo generado por
app/services/diagnostico_ia.py: `informe_ia` (JSONB, ya saneado por los
guardarraíles del servicio — nunca contiene una cita que no corresponda a un
fragmento realmente recuperado por RAG) y `informe_generado_en`. Sin cambios
de RLS: las políticas `tenant_isolation_select`/`_modify` de `diagnostics`
(migración 0001) ya cubren las columnas nuevas.

Ambas columnas nullable y sin versionado: regenerar el informe sobrescribe
las anteriores (alcance "simple, económico" de esta tarea).

Revision ID: a7b8c9d0e1f2
Revises: e5f6a7b8c9d0
Create Date: 2026-07-31
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "a7b8c9d0e1f2"
down_revision: str | None = "e5f6a7b8c9d0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "diagnostics", sa.Column("informe_ia", postgresql.JSONB(), nullable=True)
    )
    op.add_column(
        "diagnostics",
        sa.Column("informe_generado_en", sa.TIMESTAMP(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("diagnostics", "informe_generado_en")
    op.drop_column("diagnostics", "informe_ia")
