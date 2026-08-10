"""Fix: falta política RLS de UPDATE en `organizations`

Detectado al construir `PATCH /organizations` (edición de nombre/RUT/rubro/
tamaño, mejora al informe del Autodiagnóstico — ítem de identificación).
`organizations` tiene RLS activo desde la migración 0001 con solo dos
políticas: `org_visibility` (SELECT) y `org_self_service_insert` (INSERT).
Nunca hubo una política de UPDATE porque nada en el código intentaba
modificar la fila bajo `app_user` — los únicos escritores previos eran
`POST /organizations` (INSERT) y los scripts de seed (rol admin, sin RLS).
Con RLS activo y ningún policy que cubra UPDATE, Postgres deniega por
default: el UPDATE de `PATCH /organizations` afectaba 0 filas en silencio
(SQLAlchemy lo detecta y lanza `StaleDataError`, no un error de permisos).

Mismo criterio que `org_visibility`: cualquier miembro de la organización
(`auth_org_ids()`) o un superadmin puede actualizarla — el nivel de permiso
dentro de la organización (`Permission.manage_organization`) ya lo exige la
capa de aplicación (`require_permission`, ver app/api/organizations.py), RLS
solo cubre el límite de organización.

Revision ID: d2e3f4a5b6c7
Revises: c1d2e3f4a5b6
Create Date: 2026-08-10
"""

from collections.abc import Sequence

from alembic import op

revision: str = "d2e3f4a5b6c7"
down_revision: str | None = "c1d2e3f4a5b6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE POLICY org_update ON organizations "
        "FOR UPDATE "
        "USING (id IN (SELECT auth_org_ids()) OR is_superadmin()) "
        "WITH CHECK (id IN (SELECT auth_org_ids()) OR is_superadmin())"
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS org_update ON organizations")
