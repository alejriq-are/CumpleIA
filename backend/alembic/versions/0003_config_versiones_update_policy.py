"""Módulo 1 — política RLS de UPDATE faltante en config_versiones

`app/services/cuestionario_config.py::crear_nueva_version` desactiva la
versión vigente con un UPDATE (`activa=False`) antes de insertar la nueva,
porque el índice único parcial `ux_config_versiones_activa` no admite dos
filas con `activa=true` a la vez. La migración 0002 dejó `config_versiones`
con RLS activo pero solo políticas de SELECT e INSERT — sin una de UPDATE,
Postgres deniega por defecto: el UPDATE no falla, simplemente afecta 0 filas.

Bajo el rol admin (BYPASSRLS) que usaba toda la suite de tests hasta ahora
esto quedaba invisible. Corriendo de verdad contra `app_user` (como en
producción, donde `app/db/session.py` siempre usa `app_database_url`), la
versión vieja nunca se desactiva y el INSERT de la nueva versión revienta
con `duplicate key value violates unique constraint "ux_config_versiones_activa"`
— el guardado de configuración del panel admin está roto en producción desde
que existe. Ver backend/tests/test_cuestionario_config.py::superadmin_client,
migrado a `app_user`+RLS real como parte del Paso 0 de Fase 1/Tarea 1.

`config_seccion_pesos`/`config_pregunta_riesgo` no necesitan esta política:
son append-only de verdad, nunca se actualiza una fila existente (cada
versión tiene su propio juego de filas).

Revision ID: c3d4e5f6a7b8
Revises: b7c8d9e0f1a2
Create Date: 2026-07-31
"""

from collections.abc import Sequence

from alembic import op

revision: str = "c3d4e5f6a7b8"
down_revision: str | None = "b7c8d9e0f1a2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE POLICY config_versiones_update ON config_versiones "
        "FOR UPDATE USING (is_superadmin()) WITH CHECK (is_superadmin())"
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS config_versiones_update ON config_versiones")
