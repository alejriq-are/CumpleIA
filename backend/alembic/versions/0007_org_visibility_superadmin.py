"""Fix: org_visibility bloqueaba a un superadmin sin membresía.

Detectado en la revisión del PR #13 (Fase 1/Módulo 1, Tarea 4):
app/services/diagnostico_ia.py::generar_informe lee `Organization` bajo
`app_user` (RLS real) para construir el perfil de la organización en el
prompt del informe. `require_permission` (app/core/deps.py) documenta
explícitamente que un superadmin tiene el permiso sobre CUALQUIER
organización aunque no sea miembro de ella (ver ADR 0001) — pero la
política `org_visibility` de la migración 0001 solo permitía
`id IN (SELECT auth_org_ids())`, sin la cláusula `OR is_superadmin()` que
ya tienen otras políticas del proyecto (ver `subscriptions_insert`,
migración 0004). Resultado real: un superadmin sin membresía que generaba
un informe para la organización de un cliente recibía `organization = None`
(la fila quedaba invisible bajo RLS) y un `AttributeError` no manejado
(500) al leer `organization.industry`.

No es un fix específico de la Tarea 4: cualquier código futuro que lea
`Organization` bajo `app_user` en un contexto de superadmin tendría el
mismo problema. Se corrige en la política, no parcheando cada llamador.

Revision ID: b8c9d0e1f2a3
Revises: a7b8c9d0e1f2
Create Date: 2026-08-01
"""

from collections.abc import Sequence

from alembic import op

revision: str = "b8c9d0e1f2a3"
down_revision: str | None = "a7b8c9d0e1f2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("DROP POLICY IF EXISTS org_visibility ON organizations")
    op.execute(
        "CREATE POLICY org_visibility ON organizations "
        "FOR SELECT USING (id IN (SELECT auth_org_ids()) OR is_superadmin())"
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS org_visibility ON organizations")
    op.execute(
        "CREATE POLICY org_visibility ON organizations "
        "FOR SELECT USING (id IN (SELECT auth_org_ids()))"
    )
