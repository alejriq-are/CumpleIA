"""modulo3 licitud persistencia

Revision ID: 5997a757f17b
Revises: 48fe0b9c21e4
Create Date: 2026-09-22 20:05:56.874710

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op


revision: str = "5997a757f17b"
down_revision: str | None = "48fe0b9c21e4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None
_NEW_TENANT_TABLES = [
    "legal_assessment_series",
    "legal_assessments",
]


def upgrade() -> None:
    op.create_table(
        "legal_assessment_series",
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
            nullable=False,
        ),
        sa.Column("purpose_key", sa.Text(), nullable=False),
        sa.Column("purpose_text", sa.Text(), nullable=False),
        sa.Column(
            "next_version",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("1"),
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
        sa.ForeignKeyConstraint(
            ["treatment_id", "organization_id"],
            ["treatments.id", "treatments.organization_id"],
            name="fk_legal_assessment_series_treatment_tenant",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "id",
            "treatment_id",
            "organization_id",
            name="uq_legal_assessment_series_identity_tenant",
        ),
        sa.UniqueConstraint(
            "organization_id",
            "treatment_id",
            "purpose_key",
            name="uq_legal_assessment_series_treatment_purpose",
        ),
        sa.CheckConstraint(
            "next_version >= 1",
            name="ck_legal_assessment_series_next_version",
        ),
    )
    op.create_table(
        "legal_assessments",
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
            "series_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "treatment_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "version",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Text(),
            nullable=False,
            server_default=sa.text("'borrador'"),
        ),
        sa.Column(
            "legal_basis",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "justification",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "purpose_snapshot",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "rat_context_hash",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "rat_context_snapshot",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "consent_assessment",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "lia_assessment",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "special_conditions",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "schema_version",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("1"),
        ),
        sa.Column(
            "rat_context_schema_version",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("1"),
        ),
        sa.Column(
            "confirmed_at",
            sa.TIMESTAMP(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "confirmed_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("profiles.id"),
            nullable=True,
        ),
        sa.Column(
            "replaced_at",
            sa.TIMESTAMP(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "replaced_by_assessment_id",
            postgresql.UUID(as_uuid=True),
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
        sa.ForeignKeyConstraint(
            ["series_id", "treatment_id", "organization_id"],
            [
                "legal_assessment_series.id",
                "legal_assessment_series.treatment_id",
                "legal_assessment_series.organization_id",
            ],
            name="fk_legal_assessments_series_treatment_tenant",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "id",
            "series_id",
            "organization_id",
            name="uq_legal_assessments_identity_series_tenant",
        ),
        sa.ForeignKeyConstraint(
            ["replaced_by_assessment_id", "series_id", "organization_id"],
            [
                "legal_assessments.id",
                "legal_assessments.series_id",
                "legal_assessments.organization_id",
            ],
            name="fk_legal_assessments_replaced_by_same_series",
        ),
        sa.UniqueConstraint(
            "series_id",
            "version",
            name="uq_legal_assessments_series_version",
        ),
        sa.CheckConstraint(
            "version >= 1",
            name="ck_legal_assessments_version",
        ),
        sa.CheckConstraint(
            "schema_version >= 1",
            name="ck_legal_assessments_schema_version",
        ),
        sa.CheckConstraint(
            "rat_context_schema_version >= 1",
            name="ck_legal_assessments_rat_context_schema_version",
        ),
        sa.CheckConstraint(
            "status IN ('borrador', 'confirmado', 'reemplazado')",
            name="ck_legal_assessments_status",
        ),
        sa.CheckConstraint(
            "legal_basis IS NULL OR legal_basis IN ("
            "'consentimiento_art12', "
            "'obligaciones_economicas_art13a', "
            "'obligacion_legal_art13b', "
            "'contrato_precontractual_art13c', "
            "'interes_legitimo_art13d', "
            "'defensa_derechos_art13e'"
            ")",
            name="ck_legal_assessments_legal_basis",
        ),
        sa.CheckConstraint(
            "replaced_by_assessment_id IS NULL " "OR replaced_by_assessment_id <> id",
            name="ck_legal_assessments_not_self_replaced",
        ),
        sa.CheckConstraint(
            "("
            "status = 'borrador' "
            "AND confirmed_at IS NULL "
            "AND confirmed_by IS NULL "
            "AND replaced_at IS NULL "
            "AND replaced_by_assessment_id IS NULL"
            ") OR ("
            "status = 'confirmado' "
            "AND confirmed_at IS NOT NULL "
            "AND confirmed_by IS NOT NULL "
            "AND replaced_at IS NULL "
            "AND replaced_by_assessment_id IS NULL"
            ") OR ("
            "status = 'reemplazado' "
            "AND confirmed_at IS NOT NULL "
            "AND confirmed_by IS NOT NULL "
            "AND replaced_at IS NOT NULL "
            "AND replaced_by_assessment_id IS NOT NULL"
            ")",
            name="ck_legal_assessments_lifecycle_fields",
        ),
    )
    op.create_index(
        "uq_legal_assessments_one_draft_per_series",
        "legal_assessments",
        ["series_id"],
        unique=True,
        postgresql_where=sa.text("status = 'borrador'"),
    )

    op.create_index(
        "uq_legal_assessments_one_confirmed_per_series",
        "legal_assessments",
        ["series_id"],
        unique=True,
        postgresql_where=sa.text("status = 'confirmado'"),
    )
    # ── Índices tenant / relaciones ─────────────────────────────────────────
    for table in _NEW_TENANT_TABLES:
        op.create_index(
            f"ix_{table}_organization_id",
            table,
            ["organization_id"],
        )

    op.create_index(
        "ix_legal_assessment_series_treatment_id",
        "legal_assessment_series",
        ["treatment_id"],
    )

    op.create_index(
        "ix_legal_assessments_treatment_id",
        "legal_assessments",
        ["treatment_id"],
    )

    op.create_index(
        "ix_legal_assessments_series_id",
        "legal_assessments",
        ["series_id"],
    )
    # ── RLS ─────────────────────────────────────────────────────────────────
    for table in _NEW_TENANT_TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY tenant_isolation_select ON {table} "
            "FOR SELECT USING "
            "(organization_id IN (SELECT auth_org_ids()))"
        )
        op.execute(
            f"CREATE POLICY tenant_isolation_modify ON {table} "
            "FOR ALL USING "
            "(organization_id IN (SELECT auth_org_ids())) "
            "WITH CHECK "
            "(organization_id IN (SELECT auth_org_ids()))"
        )

    # Defensivo: mismo patrón usado en migraciones previas.
    op.execute(
        "GRANT SELECT, INSERT, UPDATE, DELETE "
        "ON ALL TABLES IN SCHEMA public TO app_user"
    )
    # ── Retiro seguro del scaffolding M3 legacy ─────────────────────────────
    # No hubo flujo funcional de M3 sobre legal_bases. Aun así, nunca
    # eliminamos datos inesperados silenciosamente en otro entorno.
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM legal_bases LIMIT 1) THEN
                RAISE EXCEPTION
                    'M3 migration aborted: legacy legal_bases contains data';
            END IF;
        END
        $$;
        """
    )

    op.drop_table("legal_bases")
    op.execute("DROP TYPE IF EXISTS legal_basis")


def downgrade() -> None:
    # No destruir evaluaciones M3 reales al hacer downgrade accidentalmente.
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM legal_assessments LIMIT 1)
               OR EXISTS (SELECT 1 FROM legal_assessment_series LIMIT 1) THEN
                RAISE EXCEPTION
                    'M3 downgrade aborted: legal assessment data exists';
            END IF;
        END
        $$;
        """
    )

    # ── Restaurar scaffolding M3 legacy ─────────────────────────────────────
    op.execute(
        "CREATE TYPE legal_basis AS ENUM "
        "('consentimiento', 'contrato', 'obligacion_legal', "
        "'interes_legitimo', 'otra')"
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
        sa.Column(
            "approved",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
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
        sa.ForeignKeyConstraint(
            ["treatment_id", "organization_id"],
            ["treatments.id", "treatments.organization_id"],
            name="fk_legal_bases_treatment_tenant",
            ondelete="CASCADE",
        ),
    )

    op.create_index(
        "ix_legal_bases_organization_id",
        "legal_bases",
        ["organization_id"],
    )

    op.execute("ALTER TABLE legal_bases ENABLE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY tenant_isolation_select ON legal_bases "
        "FOR SELECT USING "
        "(organization_id IN (SELECT auth_org_ids()))"
    )
    op.execute(
        "CREATE POLICY tenant_isolation_modify ON legal_bases "
        "FOR ALL USING "
        "(organization_id IN (SELECT auth_org_ids())) "
        "WITH CHECK "
        "(organization_id IN (SELECT auth_org_ids()))"
    )

    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE " "ON legal_bases TO app_user")

    # ── Retirar persistencia M3 nueva ───────────────────────────────────────
    for table in reversed(_NEW_TENANT_TABLES):
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation_modify ON {table}")
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation_select ON {table}")

    op.drop_table("legal_assessments")
    op.drop_table("legal_assessment_series")
