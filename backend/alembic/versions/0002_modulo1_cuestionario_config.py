"""Módulo 1 — configuración versionada del cuestionario de autodiagnóstico

Contenido estructural fijo (obligaciones/secciones/preguntas, fiel a la guía
CCS) más los parámetros de negocio versionados (peso_pct por sección, riesgo
por pregunta) que administra el rol superadmin desde el panel interno.

Adaptado de docs/Modulo1/schema_modulo1_cuestionario.sql a los nombres reales
de Fase 0: `organizaciones`→`organizations`, `usuarios`→`profiles`. El rol
`superadmin` no existe como valor de `user_role` (ese enum es un rol POR
membresía/organización); se modela como bandera global `profiles.is_superadmin`
más una función `is_superadmin()` (mismo patrón SECURITY DEFINER que
`auth_org_ids()` de la migración anterior) para no acoplar un rol de
plataforma a ninguna organización.

`diagnostics`/`diagnostic_answers` ya existían desde Fase 0 (sin API todavía);
se extienden en vez de crear `autodiagnosticos`/`autodiagnostico_respuestas`
en paralelo, evitando dos tablas tenant-scoped para lo mismo.

Revision ID: b7c8d9e0f1a2
Revises: a1b2c3d4e5f6
Create Date: 2026-07-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "b7c8d9e0f1a2"
down_revision: str | None = "a1b2c3d4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ── Rol superadmin (global, no tenant-scoped) ─────────────────────────────
    op.add_column(
        "profiles",
        sa.Column(
            "is_superadmin", sa.Boolean(), nullable=False, server_default="false"
        ),
    )

    # SECURITY DEFINER: igual que auth_org_ids(), necesita ver `profiles` sin el
    # filtro de RLS del rol que llama para poder resolver auth.uid() -> bandera.
    op.execute(
        """
        CREATE FUNCTION is_superadmin()
        RETURNS boolean
        LANGUAGE sql STABLE SECURITY DEFINER SET search_path = public AS $$
            SELECT COALESCE(
                (SELECT p.is_superadmin FROM profiles p WHERE p.auth_user_id = auth.uid()),
                false
            )
        $$
        """
    )
    op.execute("GRANT EXECUTE ON FUNCTION is_superadmin() TO app_user")

    # ── Contenido estructural (global, NO tenant-scoped, NO versionado) ───────
    op.create_table(
        "obligaciones",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("numero_guia", sa.Text(), nullable=False),
        sa.Column("nombre", sa.Text(), nullable=False),
        sa.Column(
            "creado_en",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_table(
        "secciones",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("numero_romano", sa.Text(), nullable=False),
        sa.Column("nombre", sa.Text(), nullable=False),
        sa.Column(
            "obligacion_id",
            sa.Text(),
            sa.ForeignKey("obligaciones.id"),
            nullable=False,
        ),
        sa.Column("orden", sa.SmallInteger(), nullable=False),
        sa.Column(
            "creado_en",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_table(
        "preguntas",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column(
            "seccion_id", sa.Text(), sa.ForeignKey("secciones.id"), nullable=False
        ),
        sa.Column("texto", sa.Text(), nullable=False),
        sa.Column("orden", sa.SmallInteger(), nullable=False),
        sa.Column(
            "creado_en",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # ── Parámetros de negocio versionados (peso_pct, riesgo) ──────────────────
    op.create_table(
        "config_versiones",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("numero_version", sa.Integer(), nullable=False, unique=True),
        sa.Column("activa", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("nota", sa.Text(), nullable=True),
        sa.Column(
            "creado_por",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("profiles.id"),
            nullable=False,
        ),
        sa.Column(
            "creado_en",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "ux_config_versiones_activa",
        "config_versiones",
        ["activa"],
        unique=True,
        postgresql_where=sa.text("activa"),
    )

    op.create_table(
        "config_seccion_pesos",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("config_versiones.id"),
            nullable=False,
        ),
        sa.Column(
            "seccion_id", sa.Text(), sa.ForeignKey("secciones.id"), nullable=False
        ),
        sa.Column(
            "peso_pct",
            sa.Numeric(5, 2),
            sa.CheckConstraint(
                "peso_pct >= 0 AND peso_pct <= 100",
                name="peso_pct_rango",
            ),
            nullable=False,
        ),
        sa.UniqueConstraint("version_id", "seccion_id"),
    )

    op.create_table(
        "config_pregunta_riesgo",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("config_versiones.id"),
            nullable=False,
        ),
        sa.Column(
            "pregunta_id", sa.Text(), sa.ForeignKey("preguntas.id"), nullable=False
        ),
        sa.Column(
            "riesgo",
            postgresql.ENUM(
                "alto", "medio", "bajo", name="risk_level", create_type=False
            ),
            nullable=False,
        ),
        sa.UniqueConstraint("version_id", "pregunta_id"),
    )

    # RLS de config_*: lectura abierta (toda organización necesita leer la
    # config activa), escritura solo superadmin, sin UPDATE/DELETE (append-only
    # real: sin política definida para esos comandos, RLS deniega por defecto,
    # mismo patrón que evidence_events en la migración anterior).
    for table in ("config_versiones", "config_seccion_pesos", "config_pregunta_riesgo"):
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"CREATE POLICY {table}_select ON {table} FOR SELECT USING (true)")
        op.execute(
            f"CREATE POLICY {table}_insert ON {table} "
            f"FOR INSERT WITH CHECK (is_superadmin())"
        )

    # ── Extiende diagnostics/diagnostic_answers (Fase 0, sin API todavía) ─────
    op.add_column(
        "diagnostics",
        sa.Column(
            "config_version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("config_versiones.id"),
            nullable=False,
        ),
    )
    op.create_check_constraint(
        "status_valido",
        "diagnostics",
        "status IN ('en_progreso', 'completado')",
    )

    op.alter_column(
        "diagnostic_answers", "question_code", new_column_name="pregunta_id"
    )
    op.drop_column("diagnostic_answers", "section")
    op.create_foreign_key(
        "fk_diagnostic_answers_pregunta_id_preguntas",
        "diagnostic_answers",
        "preguntas",
        ["pregunta_id"],
        ["id"],
    )
    op.create_check_constraint(
        "answer_valido",
        "diagnostic_answers",
        "answer IN ('Sí', 'Parcial', 'No', 'N/A')",
    )
    op.create_unique_constraint(
        "uq_diagnostic_answers_diagnostic_id_pregunta_id",
        "diagnostic_answers",
        ["diagnostic_id", "pregunta_id"],
    )

    # Defensivo: ALTER DEFAULT PRIVILEGES de la migración anterior ya debería
    # cubrir estas tablas nuevas (mismo rol de migración), pero se re-otorga
    # explícito para no depender de eso.
    op.execute(
        "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user"
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_diagnostic_answers_diagnostic_id_pregunta_id",
        "diagnostic_answers",
        type_="unique",
    )
    op.drop_constraint(
        "ck_diagnostic_answers_answer_valido", "diagnostic_answers", type_="check"
    )
    op.drop_constraint(
        "fk_diagnostic_answers_pregunta_id_preguntas",
        "diagnostic_answers",
        type_="foreignkey",
    )
    op.add_column("diagnostic_answers", sa.Column("section", sa.Text(), nullable=True))
    op.alter_column(
        "diagnostic_answers", "pregunta_id", new_column_name="question_code"
    )

    op.drop_constraint("ck_diagnostics_status_valido", "diagnostics", type_="check")
    op.drop_column("diagnostics", "config_version_id")

    for table in ("config_pregunta_riesgo", "config_seccion_pesos", "config_versiones"):
        op.execute(f"DROP POLICY IF EXISTS {table}_select ON {table}")
        op.execute(f"DROP POLICY IF EXISTS {table}_insert ON {table}")

    op.drop_table("config_pregunta_riesgo")
    op.drop_table("config_seccion_pesos")
    op.drop_index("ux_config_versiones_activa", table_name="config_versiones")
    op.drop_table("config_versiones")
    op.drop_table("preguntas")
    op.drop_table("secciones")
    op.drop_table("obligaciones")

    op.execute("DROP FUNCTION IF EXISTS is_superadmin()")
    op.drop_column("profiles", "is_superadmin")
