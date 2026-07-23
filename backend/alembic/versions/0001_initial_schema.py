"""Esquema inicial — Fase 0

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-07-17
"""

import os
from collections.abc import Sequence

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Tablas de negocio que reciben aislamiento por tenant (RLS SELECT + ALL)
_TENANT_TABLES = [
    "diagnostics",
    "diagnostic_answers",
    "findings",
    "systems",
    "vendors",
    "treatments",
    "legal_bases",
    "documents",
]


def upgrade() -> None:
    # ── Extensiones ──────────────────────────────────────────────────────────
    # pgcrypto no es necesario: gen_random_uuid() es built-in desde PostgreSQL 13
    op.execute('CREATE EXTENSION IF NOT EXISTS "vector"')

    # ── Schema auth stub para desarrollo local (Docker) ──────────────────────
    # En Supabase este schema y auth.uid() ya existen con la implementación real
    # (lee el JWT vía PostgREST). CREATE OR REPLACE los pisaría con este stub y
    # rompería RLS en todo el proyecto, no solo para este backend — por eso se
    # crea SOLO si no existe. El stub replica el comportamiento real: lee el
    # mismo GUC de sesión (`request.jwt.claim.sub`) que el backend puebla en
    # cada request (ver app/core/deps.py::get_current_profile), así RLS se
    # comporta igual en Docker local que en Supabase.
    op.execute("CREATE SCHEMA IF NOT EXISTS auth")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_proc p
                JOIN pg_namespace n ON n.oid = p.pronamespace
                WHERE n.nspname = 'auth' AND p.proname = 'uid'
            ) THEN
                CREATE FUNCTION auth.uid() RETURNS uuid
                LANGUAGE sql STABLE AS $fn$
                    SELECT NULLIF(current_setting('request.jwt.claim.sub', true), '')::uuid
                $fn$;
            END IF;
        END
        $$;
        """
    )

    # ── Tipos enum ───────────────────────────────────────────────────────────
    op.execute("CREATE TYPE user_role AS ENUM ('owner', 'admin', 'editor', 'viewer')")
    op.execute("CREATE TYPE risk_level AS ENUM ('alto', 'medio', 'bajo')")
    op.execute(
        "CREATE TYPE finding_status AS ENUM ('abierto', 'en_proceso', 'cerrado', 'no_aplica')"
    )
    op.execute(
        "CREATE TYPE legal_basis AS ENUM "
        "('consentimiento', 'contrato', 'obligacion_legal', 'interes_legitimo', 'otra')"
    )
    op.execute(
        "CREATE TYPE third_party_role AS ENUM "
        "('encargado', 'cesion', 'transferencia_internacional')"
    )
    op.execute(
        "CREATE TYPE document_type AS ENUM "
        "('politica_proteccion_datos', 'politica_privacidad', 'politica_conservacion', "
        "'politica_seguridad', 'procedimiento_arsop', 'procedimiento_incidentes')"
    )
    op.execute(
        "CREATE TYPE document_status AS ENUM ('borrador', 'aprobado', 'archivado')"
    )

    # ── Tablas (orden respeta FK) ─────────────────────────────────────────────

    op.create_table(
        "organizations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("rut", sa.Text(), nullable=True),
        sa.Column("industry", sa.Text(), nullable=True),
        sa.Column("size", sa.Text(), nullable=True),
        sa.Column("plan", sa.Text(), nullable=False, server_default="free"),
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
    )

    op.create_table(
        "profiles",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "auth_user_id", postgresql.UUID(as_uuid=True), unique=True, nullable=False
        ),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("full_name", sa.Text(), nullable=True),
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
    )

    op.create_table(
        "memberships",
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
        sa.Column(
            "profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "role",
            postgresql.ENUM(
                "owner",
                "admin",
                "editor",
                "viewer",
                name="user_role",
                create_type=False,
            ),
            nullable=False,
            server_default="owner",
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("organization_id", "profile_id"),
    )

    # Función helper para RLS (usa auth.uid() de Supabase o el stub local)
    op.execute(
        """
        CREATE OR REPLACE FUNCTION auth_org_ids()
        RETURNS SETOF uuid
        LANGUAGE sql STABLE SECURITY DEFINER SET search_path = public AS $$
            SELECT m.organization_id
            FROM memberships m
            JOIN profiles p ON p.id = m.profile_id
            WHERE p.auth_user_id = auth.uid()
        $$
        """
    )

    op.create_table(
        "diagnostics",
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
        sa.Column("global_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("section_scores", postgresql.JSONB(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False, server_default="en_progreso"),
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

    op.create_table(
        "diagnostic_answers",
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
        sa.Column(
            "diagnostic_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("diagnostics.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("section", sa.Text(), nullable=False),
        sa.Column("question_code", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_table(
        "findings",
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
        sa.Column(
            "diagnostic_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("diagnostics.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "risk",
            postgresql.ENUM(
                "alto", "medio", "bajo", name="risk_level", create_type=False
            ),
            nullable=False,
        ),
        sa.Column("corrective_action", sa.Text(), nullable=True),
        sa.Column("responsible", sa.Text(), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(
                "abierto",
                "en_proceso",
                "cerrado",
                "no_aplica",
                name="finding_status",
                create_type=False,
            ),
            nullable=False,
            server_default="abierto",
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
    )

    op.create_table(
        "systems",
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
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("provider", sa.Text(), nullable=True),
        sa.Column("hosting_location", sa.Text(), nullable=True),
        sa.Column(
            "is_international", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_table(
        "vendors",
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
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column(
            "role",
            postgresql.ENUM(
                "encargado",
                "cesion",
                "transferencia_internacional",
                name="third_party_role",
                create_type=False,
            ),
            nullable=True,
        ),
        sa.Column(
            "is_international", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column("has_dpa", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_table(
        "treatments",
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
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("purpose", sa.Text(), nullable=True),
        sa.Column("data_categories", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("data_subjects", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column(
            "has_sensitive", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column("retention", sa.Text(), nullable=True),
        sa.Column(
            "is_international", sa.Boolean(), nullable=False, server_default="false"
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
    )

    op.create_table(
        "legal_bases",
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
        sa.Column(
            "treatment_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("treatments.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "basis",
            postgresql.ENUM(
                "consentimiento",
                "contrato",
                "obligacion_legal",
                "interes_legitimo",
                "otra",
                name="legal_basis",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("justification", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Numeric(4, 3), nullable=True),
        sa.Column("approved", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("lia", postgresql.JSONB(), nullable=True),
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
    )

    op.create_table(
        "documents",
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
        sa.Column(
            "type",
            postgresql.ENUM(
                "politica_proteccion_datos",
                "politica_privacidad",
                "politica_conservacion",
                "politica_seguridad",
                "procedimiento_arsop",
                "procedimiento_incidentes",
                name="document_type",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "status",
            postgresql.ENUM(
                "borrador",
                "aprobado",
                "archivado",
                name="document_status",
                create_type=False,
            ),
            nullable=False,
            server_default="borrador",
        ),
        sa.Column("storage_path", sa.Text(), nullable=True),
        sa.Column("content_hash", sa.Text(), nullable=True),
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
    )

    op.create_table(
        "evidence_events",
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
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column(
            "actor_profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("profiles.id"),
            nullable=True,
        ),
        sa.Column("payload", postgresql.JSONB(), nullable=True),
        sa.Column("payload_hash", sa.Text(), nullable=False),
        sa.Column("prev_hash", sa.Text(), nullable=True),
        sa.Column("event_hash", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_table(
        "knowledge_chunks",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("reference", sa.Text(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(1024), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # ── Índices por tenant ────────────────────────────────────────────────────
    tenant_index_tables = [
        "diagnostics",
        "diagnostic_answers",
        "findings",
        "systems",
        "vendors",
        "treatments",
        "legal_bases",
        "documents",
        "evidence_events",
        "memberships",
    ]
    for table in tenant_index_tables:
        op.create_index(f"ix_{table}_organization_id", table, ["organization_id"])

    # Índice vectorial para RAG (hnsw, similitud coseno — funciona en tablas vacías)
    op.execute(
        "CREATE INDEX ON knowledge_chunks " "USING hnsw (embedding vector_cosine_ops)"
    )

    # ── Row-Level Security ────────────────────────────────────────────────────
    rls_tables = [
        "organizations",
        "memberships",
        "diagnostics",
        "diagnostic_answers",
        "findings",
        "systems",
        "vendors",
        "treatments",
        "legal_bases",
        "documents",
        "evidence_events",
    ]
    for table in rls_tables:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")

    # Política genérica por tenant (SELECT + modificación)
    for table in _TENANT_TABLES:
        op.execute(
            f"CREATE POLICY tenant_isolation_select ON {table} "
            f"FOR SELECT USING (organization_id IN (SELECT auth_org_ids()))"
        )
        op.execute(
            f"CREATE POLICY tenant_isolation_modify ON {table} "
            f"FOR ALL USING (organization_id IN (SELECT auth_org_ids())) "
            f"WITH CHECK (organization_id IN (SELECT auth_org_ids()))"
        )

    # Organizations: solo ve las propias
    op.execute(
        "CREATE POLICY org_visibility ON organizations "
        "FOR SELECT USING (id IN (SELECT auth_org_ids()))"
    )
    # Alta de tenant por autoservicio (POST /organizations, ver
    # app/api/organizations.py): en ese momento el usuario NO tiene ninguna
    # membresía todavía, por lo que auth_org_ids() está vacío y no sirve como
    # condición. Cualquier usuario autenticado puede crear una organización
    # nueva; lo sensible (leer/escribir SUS datos) sigue detrás de
    # org_visibility y de las políticas por tenant de arriba.
    op.execute(
        "CREATE POLICY org_self_service_insert ON organizations "
        "FOR INSERT WITH CHECK (auth.uid() IS NOT NULL)"
    )

    # Membresías
    op.execute(
        "CREATE POLICY tenant_isolation_select ON memberships "
        "FOR SELECT USING (organization_id IN (SELECT auth_org_ids()))"
    )
    op.execute(
        "CREATE POLICY tenant_isolation_modify ON memberships "
        "FOR ALL USING (organization_id IN (SELECT auth_org_ids())) "
        "WITH CHECK (organization_id IN (SELECT auth_org_ids()))"
    )
    # Mismo problema del huevo y la gallina: la primera membresía de una
    # organización recién creada no puede validarse contra auth_org_ids()
    # (todavía vacío). Se permite auto-insertarse como 'owner' ÚNICAMENTE si
    # la organización aún no tiene ninguna membresía — así no sirve para
    # auto-adjudicarse acceso a una organización ya existente (eso lo sigue
    # bloqueando tenant_isolation_modify, que exige pertenencia previa). Las
    # políticas permisivas se combinan con OR: basta con que una de las dos
    # autorice el INSERT.
    #
    # OJO: el chequeo de "¿ya tiene dueño esta organización?" NO puede ser un
    # NOT EXISTS directo contra `memberships` dentro de la propia política.
    # Ese subquery lo ejecutaría `app_user` bajo tenant_isolation_select, que
    # solo deja ver membresías de organizaciones a las que YA perteneces — es
    # decir, para cualquier organización ajena el subquery siempre parecería
    # "vacío" (no por estar realmente desocupada, sino porque el atacante no
    # puede verla), y NOT EXISTS daría TRUE igual. Eso habría permitido a
    # cualquier usuario autenticado autoasignarse 'owner' de una organización
    # ajena ya existente. Por eso se delega en una función SECURITY DEFINER
    # (mismo patrón que auth_org_ids()) que ve todas las filas sin el filtro
    # de RLS del rol que llama.
    op.execute(
        """
        CREATE OR REPLACE FUNCTION organization_is_unclaimed(target_org_id uuid)
        RETURNS boolean
        LANGUAGE sql STABLE SECURITY DEFINER SET search_path = public AS $$
            SELECT NOT EXISTS (
                SELECT 1 FROM memberships WHERE organization_id = target_org_id
            )
        $$
        """
    )
    op.execute(
        "CREATE POLICY memberships_self_bootstrap_insert ON memberships "
        "FOR INSERT WITH CHECK ("
        "role = 'owner' "
        "AND profile_id IN (SELECT id FROM profiles WHERE auth_user_id = auth.uid()) "
        "AND organization_is_unclaimed(organization_id)"
        ")"
    )

    # Evidencia: INSERT + SELECT permitidos; sin UPDATE ni DELETE (append-only)
    op.execute(
        "CREATE POLICY evidence_select ON evidence_events "
        "FOR SELECT USING (organization_id IN (SELECT auth_org_ids()))"
    )
    op.execute(
        "CREATE POLICY evidence_insert ON evidence_events "
        "FOR INSERT WITH CHECK (organization_id IN (SELECT auth_org_ids()))"
    )

    # ── Rol de aplicación restringido (para que RLS aplique de verdad) ────────
    # El rol usado para migraciones (DATABASE_URL) es dueño de las tablas y,
    # como cualquier superusuario/dueño de tabla en Postgres, ignora RLS por
    # defecto. Si el backend consultara con ese mismo rol, las políticas de
    # arriba serían letra muerta. `app_user` es un rol de login sin
    # BYPASSRLS ni superusuario: es el que debe usar app/db/session.py
    # (APP_DATABASE_URL) en runtime.
    app_db_password = os.environ.get("APP_DB_PASSWORD", "app_dev_password")
    op.execute(
        f"""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_user') THEN
                CREATE ROLE app_user LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE
                    NOBYPASSRLS PASSWORD '{app_db_password}';
            END IF;
        END
        $$;
        """
    )
    op.execute("GRANT USAGE ON SCHEMA public TO app_user")
    op.execute("GRANT USAGE ON SCHEMA auth TO app_user")
    op.execute(
        "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user"
    )
    op.execute(
        "ALTER DEFAULT PRIVILEGES IN SCHEMA public "
        "GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user"
    )
    op.execute("GRANT EXECUTE ON FUNCTION auth.uid() TO app_user")
    op.execute("GRANT EXECUTE ON FUNCTION auth_org_ids() TO app_user")
    op.execute("GRANT EXECUTE ON FUNCTION organization_is_unclaimed(uuid) TO app_user")

    # Nota deliberadamente NO se usa ALTER TABLE ... FORCE ROW LEVEL SECURITY:
    # forzaría RLS incluso para el dueño de las tablas (el rol de migración),
    # y auth_org_ids()/organization_is_unclaimed() son SECURITY DEFINER que
    # dependen de que ESE rol vea `memberships` sin el filtro de RLS para
    # poder calcular a qué organizaciones pertenece cada usuario. Con FORCE,
    # esas funciones se autobloquearían (auth_org_ids() necesitaría el
    # resultado de auth_org_ids() para leer memberships). No hace falta de
    # todos modos: `app_user` nunca es dueño de estas tablas, así que ya está
    # sujeto a RLS sin excepción.


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_user') THEN
                EXECUTE 'DROP OWNED BY app_user';
                DROP ROLE app_user;
            END IF;
        END
        $$;
        """
    )

    tables = [
        "knowledge_chunks",
        "evidence_events",
        "documents",
        "legal_bases",
        "treatments",
        "vendors",
        "systems",
        "findings",
        "diagnostic_answers",
        "diagnostics",
        "memberships",
        "profiles",
        "organizations",
    ]
    for table in tables:
        op.drop_table(table)

    op.execute("DROP FUNCTION IF EXISTS organization_is_unclaimed(uuid)")
    op.execute("DROP FUNCTION IF EXISTS auth_org_ids()")
    op.execute("DROP FUNCTION IF EXISTS auth.uid()")
    op.execute("DROP SCHEMA IF EXISTS auth CASCADE")

    for enum_name in [
        "document_status",
        "document_type",
        "third_party_role",
        "legal_basis",
        "finding_status",
        "risk_level",
        "user_role",
    ]:
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
