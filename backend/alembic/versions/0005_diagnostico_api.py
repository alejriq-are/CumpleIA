"""Fase 1 / Módulo 1, Tarea 3 — API del Autodiagnóstico

Dos cambios de modelo de datos, ambos requeridos por
docs/adr/0002-logica-adaptativa-riesgo-remediacion.md antes de escribir la
API (ver ese ADR para el porqué completo, incluida la razón de por qué NO se
construye aquí el catálogo `instructivo_agencia` como tabla global):

1. `findings.pregunta_id`: permite que `app/services/diagnostico.py`
   sincronice (abra/cierre) el Finding que corresponde a cada pregunta en
   cada recálculo de puntaje, por identidad y no por comparar texto libre.
   Con `UniqueConstraint(diagnostic_id, pregunta_id)` sirve además como
   llave de upsert.

2. `diagnostics.organization_id` pasa a UNIQUE: "diagnóstico vigente" es
   get-or-create, no historial (a lo sumo un Diagnostic por organización).
   Sin esta restricción, dos guardados concurrentes de la primera respuesta
   podrían crear dos filas para la misma organización.

3. `reference_documents`: entidad de "documento de referencia" (capa 3 del
   ADR) — la organización enlaza su propia política de gobernanza para un
   hallazgo o para el diagnóstico completo, en vez de que CumpleIA fije
   plazos de cumplimiento propios sin respaldo normativo. Tenant-scoped,
   mismo patrón de RLS genérico (`tenant_isolation_select`/`_modify`) que
   `diagnostics`/`findings` en la migración 0001 — a diferencia de
   `subscriptions` (migración 0004), aquí no hace falta restringir UPDATE a
   `is_superadmin()`: es contenido propio de cada organización, no de
   plataforma. Solo se puede escribir `tipo='politica_interna_gobernanza'`
   desde esta tarea; no existe todavía endpoint de carga (queda anotado en
   docs/backlog.md).

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-07-31
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "e5f6a7b8c9d0"
down_revision: str | None = "d4e5f6a7b8c9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ── diagnostics: a lo sumo uno por organización ──────────────────────────
    op.create_unique_constraint(
        "uq_diagnostics_organization_id", "diagnostics", ["organization_id"]
    )

    # ── findings.pregunta_id ──────────────────────────────────────────────────
    op.add_column(
        "findings",
        sa.Column("pregunta_id", sa.Text(), sa.ForeignKey("preguntas.id"), nullable=True),
    )
    op.create_unique_constraint(
        "uq_findings_diagnostic_id_pregunta_id",
        "findings",
        ["diagnostic_id", "pregunta_id"],
    )

    # ── reference_documents ───────────────────────────────────────────────────
    op.create_table(
        "reference_documents",
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
        ),
        sa.Column("tipo", sa.Text(), nullable=False),
        sa.Column("titulo", sa.Text(), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=True),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column(
            "finding_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("findings.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "diagnostic_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("diagnostics.id", ondelete="SET NULL"),
            nullable=True,
        ),
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
        sa.CheckConstraint(
            "tipo IN ('politica_interna_gobernanza', 'instructivo_agencia')",
            name="tipo_valido",
        ),
    )
    op.create_index(
        "ix_reference_documents_organization_id",
        "reference_documents",
        ["organization_id"],
    )

    op.execute("ALTER TABLE reference_documents ENABLE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY tenant_isolation_select ON reference_documents "
        "FOR SELECT USING (organization_id IN (SELECT auth_org_ids()))"
    )
    op.execute(
        "CREATE POLICY tenant_isolation_modify ON reference_documents "
        "FOR ALL USING (organization_id IN (SELECT auth_org_ids())) "
        "WITH CHECK (organization_id IN (SELECT auth_org_ids()))"
    )

    # Defensivo: mismo re-GRANT explícito que la migración 0002 para tablas
    # nuevas, sin depender de que ALTER DEFAULT PRIVILEGES ya cubra esta.
    op.execute(
        "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user"
    )


def downgrade() -> None:
    op.execute(
        "DROP POLICY IF EXISTS tenant_isolation_modify ON reference_documents"
    )
    op.execute(
        "DROP POLICY IF EXISTS tenant_isolation_select ON reference_documents"
    )
    op.drop_index("ix_reference_documents_organization_id", table_name="reference_documents")
    op.drop_table("reference_documents")

    op.drop_constraint(
        "uq_findings_diagnostic_id_pregunta_id", "findings", type_="unique"
    )
    op.drop_column("findings", "pregunta_id")

    op.drop_constraint("uq_diagnostics_organization_id", "diagnostics", type_="unique")
