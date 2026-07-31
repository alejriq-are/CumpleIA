"""Modelo de organizaciones, roles y suscripción — tabla subscriptions

Ver docs/adr/0001-modelo-organizaciones-roles-suscripcion.md para el porqué
completo. Este ADR no toca `organizations`/`memberships`/`user_role` (ya
cumplían el scoping y el enum de rol no necesitaba cambios) — el único
modelo de datos nuevo es la suscripción.

Una fila por organización (`organization_id` UNIQUE): representa el estado
de vigencia de acceso, hoy sin cálculo real de facturación detrás (todas
nacen `active`), pero con la interfaz ya definida para cuando exista. El
backfill de abajo asegura que TODA organización ya existente (seed de dev,
datos de test, organizaciones creadas antes de esta migración) también
quede con su fila — así `get_subscription_status`
(app/services/subscriptions.py) puede asumir `scalar_one()` sin manejar un
caso "no existe" que, tras esta migración, no puede ocurrir.

RLS: SELECT abierto a los miembros de la propia organización (mismo patrón
`auth_org_ids()` que el resto de las tablas tenant-scoped). UPDATE
restringido a `is_superadmin()` (mismo patrón que `config_versiones` en la
migración 0002) — no existe autoservicio de facturación todavía, así que
ningún admin de organización debe poder cambiar el status de su propia
suscripción una vez creada. Sin política de DELETE: una suscripción no se
borra.

INSERT: `is_superadmin()` O pertenencia a la organización
(`auth_org_ids()`) — igual que `org_self_service_insert`/
`memberships_self_bootstrap_insert` de la migración 0001, `POST
/organizations` (app/api/organizations.py) inserta Organization, Membership
y Subscription en ese orden dentro de la MISMA transacción: para cuando
corre el INSERT de `subscriptions`, la Membership recién insertada ya es
visible para `auth_org_ids()` (misma transacción, MVCC), así que no hace
falta una función `..._is_unclaimed()` extra. Esto no es una escalada de
privilegios real: `organization_id` es UNIQUE (una sola fila por
organización, para siempre) y el status solo puede cambiar después vía
UPDATE, que sigue siendo exclusivo de superadmin.

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-07-31
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "d4e5f6a7b8c9"
down_revision: str | None = "c3d4e5f6a7b8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE subscription_commitment_type AS ENUM "
        "('monthly', 'annual_commitment_monthly_billing')"
    )
    op.execute(
        "CREATE TYPE subscription_status AS ENUM "
        "('active', 'grace', 'suspended', 'cancelled')"
    )

    op.create_table(
        "subscriptions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "commitment_type",
            postgresql.ENUM(
                "monthly",
                "annual_commitment_monthly_billing",
                name="subscription_commitment_type",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            postgresql.ENUM(
                "active",
                "grace",
                "suspended",
                "cancelled",
                name="subscription_status",
                create_type=False,
            ),
            nullable=False,
            server_default="active",
        ),
        sa.Column("grace_until", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("profiles.id"),
            nullable=True,
        ),
        sa.Column(
            "updated_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("profiles.id"),
            nullable=True,
        ),
    )

    # Backfill: toda organización ya existente queda con su fila de
    # suscripción (ver docstring del módulo). created_by/updated_by quedan
    # NULL a propósito: no hay un actor humano detrás de este backfill.
    op.execute(
        "INSERT INTO subscriptions (organization_id, commitment_type, status) "
        "SELECT id, 'monthly', 'active' FROM organizations"
    )

    op.execute("ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY subscriptions_select ON subscriptions "
        "FOR SELECT USING (organization_id IN (SELECT auth_org_ids()))"
    )
    op.execute(
        "CREATE POLICY subscriptions_insert ON subscriptions "
        "FOR INSERT WITH CHECK "
        "(is_superadmin() OR organization_id IN (SELECT auth_org_ids()))"
    )
    op.execute(
        "CREATE POLICY subscriptions_update ON subscriptions "
        "FOR UPDATE USING (is_superadmin()) WITH CHECK (is_superadmin())"
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS subscriptions_update ON subscriptions")
    op.execute("DROP POLICY IF EXISTS subscriptions_insert ON subscriptions")
    op.execute("DROP POLICY IF EXISTS subscriptions_select ON subscriptions")
    op.drop_table("subscriptions")
    op.execute("DROP TYPE IF EXISTS subscription_status")
    op.execute("DROP TYPE IF EXISTS subscription_commitment_type")
