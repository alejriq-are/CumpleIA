"""Módulo 2 / RAT — Tarea 1: persistencia normalizada

Implementa el modelo físico del Registro de Actividades de Tratamiento (RAT)
definido en docs/project/modulo2-rat-diseno.md.

Principios de esta migración:

1. `treatments` sigue siendo la entidad raíz de una actividad de tratamiento.
2. Finalidades, categorías de datos, titulares y fuentes dejan de depender
   exclusivamente de arrays/texto libre y pasan a entidades relacionadas.
3. Sistemas y terceros se relacionan N:M con los tratamientos.
4. Las transferencias internacionales son una entidad propia; no un rol de
   Vendor ni un booleano suficiente por sí mismo.
5. Todas las relaciones tenant-scoped incluyen `organization_id`.
6. Las FK compuestas garantizan que una relación no pueda enlazar objetos de
   organizaciones diferentes, incluso si un usuario pertenece a ambas.
7. Las columnas legacy del scaffold inicial se conservan temporalmente para
   compatibilidad; su eliminación corresponde a una migración posterior.
8. No implementa la lógica funcional del Módulo 3 (bases de licitud).

Revision ID: e3f4a5b6c7d8
Revises: d2e3f4a5b6c7
Create Date: 2026-09-15
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "e3f4a5b6c7d8"
down_revision: str | None = "d2e3f4a5b6c7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


_NEW_TENANT_TABLES = [
    "treatment_purposes",
    "treatment_data_categories",
    "treatment_data_subjects",
    "treatment_data_sources",
    "treatment_systems",
    "treatment_vendors",
    "international_transfers",
]


def _audit_columns() -> list[sa.Column]:
    return [
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
    ]


def _tenant_id_column() -> sa.Column:
    return sa.Column(
        "organization_id",
        postgresql.UUID(as_uuid=True),
        sa.ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )


def _uuid_pk() -> sa.Column:
    return sa.Column(
        "id",
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    )


def upgrade() -> None:
    # ── Integridad compuesta de las entidades principales ──────────────────
    #
    # Permite que las tablas hijas referencien simultáneamente id +
    # organization_id. El id ya es globalmente UNIQUE por ser PK, pero esta
    # restricción adicional es necesaria como target de una FK compuesta.
    op.create_unique_constraint(
        "uq_treatments_id_organization_id",
        "treatments",
        ["id", "organization_id"],
    )
    op.create_unique_constraint(
        "uq_systems_id_organization_id",
        "systems",
        ["id", "organization_id"],
    )
    op.create_unique_constraint(
        "uq_vendors_id_organization_id",
        "vendors",
        ["id", "organization_id"],
    )

    # ── treatments: ampliar scaffold sin eliminar columnas legacy ──────────
    op.add_column("treatments", sa.Column("description", sa.Text(), nullable=True))
    op.add_column(
        "treatments",
        sa.Column("organization_role", sa.Text(), nullable=True),
    )
    op.add_column("treatments", sa.Column("business_area", sa.Text(), nullable=True))
    op.add_column(
        "treatments",
        sa.Column("data_flow_description", sa.Text(), nullable=True),
    )
    op.add_column("treatments", sa.Column("start_date", sa.Date(), nullable=True))
    op.add_column(
        "treatments",
        sa.Column(
            "last_reviewed_at",
            sa.TIMESTAMP(timezone=True),
            nullable=True,
        ),
    )
    op.add_column(
        "treatments",
        sa.Column(
            "next_review_at",
            sa.TIMESTAMP(timezone=True),
            nullable=True,
        ),
    )
    op.add_column(
        "treatments",
        sa.Column(
            "status",
            sa.Text(),
            nullable=False,
            server_default="borrador",
        ),
    )
    op.add_column(
        "treatments",
        sa.Column("retention_rule", sa.Text(), nullable=True),
    )
    op.add_column(
        "treatments",
        sa.Column("deletion_method", sa.Text(), nullable=True),
    )
    op.add_column(
        "treatments",
        sa.Column(
            "has_automated_decisions",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
    )
    op.add_column(
        "treatments",
        sa.Column(
            "automated_decision_description",
            sa.Text(),
            nullable=True,
        ),
    )

    op.create_check_constraint(
        "ck_treatments_organization_role",
        "treatments",
        "organization_role IS NULL OR "
        "organization_role IN ('responsable', 'encargado')",
    )
    op.create_check_constraint(
        "ck_treatments_status",
        "treatments",
        "status IN ('borrador', 'activo', 'archivado')",
    )

    # ── systems: auditoría + país de hosting ────────────────────────────────
    op.add_column(
        "systems",
        sa.Column("hosting_country", sa.Text(), nullable=True),
    )
    op.add_column(
        "systems",
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.add_column(
        "systems",
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("profiles.id"),
            nullable=True,
        ),
    )
    op.add_column(
        "systems",
        sa.Column(
            "updated_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("profiles.id"),
            nullable=True,
        ),
    )

    # ── vendors: maestro del tercero, no de la relación con Treatment ──────
    op.add_column("vendors", sa.Column("country", sa.Text(), nullable=True))
    op.add_column(
        "vendors",
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.add_column(
        "vendors",
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("profiles.id"),
            nullable=True,
        ),
    )
    op.add_column(
        "vendors",
        sa.Column(
            "updated_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("profiles.id"),
            nullable=True,
        ),
    )

    # ── Finalidades ─────────────────────────────────────────────────────────
    op.create_table(
        "treatment_purposes",
        _uuid_pk(),
        _tenant_id_column(),
        sa.Column(
            "treatment_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("purpose", sa.Text(), nullable=False),
        sa.Column(
            "is_primary",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column(
            "sort_order",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        *_audit_columns(),
        sa.ForeignKeyConstraint(
            ["treatment_id", "organization_id"],
            ["treatments.id", "treatments.organization_id"],
            name="fk_treatment_purposes_treatment_tenant",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "treatment_id",
            "purpose",
            name="uq_treatment_purposes_treatment_purpose",
        ),
        sa.CheckConstraint(
            "sort_order >= 0",
            name="ck_treatment_purposes_sort_order",
        ),
    )

    # ── Categorías de datos ─────────────────────────────────────────────────
    op.create_table(
        "treatment_data_categories",
        _uuid_pk(),
        _tenant_id_column(),
        sa.Column(
            "treatment_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("category_code", sa.Text(), nullable=False),
        sa.Column("category_name", sa.Text(), nullable=False),
        sa.Column(
            "is_sensitive",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        *_audit_columns(),
        sa.ForeignKeyConstraint(
            ["treatment_id", "organization_id"],
            ["treatments.id", "treatments.organization_id"],
            name="fk_treatment_data_categories_treatment_tenant",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "treatment_id",
            "category_code",
            name="uq_treatment_data_categories_treatment_code",
        ),
    )

    # ── Categorías de titulares ─────────────────────────────────────────────
    op.create_table(
        "treatment_data_subjects",
        _uuid_pk(),
        _tenant_id_column(),
        sa.Column(
            "treatment_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("category_code", sa.Text(), nullable=False),
        sa.Column("category_name", sa.Text(), nullable=False),
        sa.Column(
            "includes_children",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column(
            "includes_adolescents",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column(
            "is_vulnerable_group",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        *_audit_columns(),
        sa.ForeignKeyConstraint(
            ["treatment_id", "organization_id"],
            ["treatments.id", "treatments.organization_id"],
            name="fk_treatment_data_subjects_treatment_tenant",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "treatment_id",
            "category_code",
            name="uq_treatment_data_subjects_treatment_code",
        ),
    )

    # ── Fuentes/origen de los datos ────────────────────────────────────────
    op.create_table(
        "treatment_data_sources",
        _uuid_pk(),
        _tenant_id_column(),
        sa.Column(
            "treatment_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("source_type", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "is_public_source",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        *_audit_columns(),
        sa.ForeignKeyConstraint(
            ["treatment_id", "organization_id"],
            ["treatments.id", "treatments.organization_id"],
            name="fk_treatment_data_sources_treatment_tenant",
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(
            "source_type IN "
            "('titular', 'tercero', 'fuente_publica', "
            "'recogida_automatica', 'otro')",
            name="ck_treatment_data_sources_source_type",
        ),
    )

    # ── Treatment ↔ System ──────────────────────────────────────────────────
    op.create_table(
        "treatment_systems",
        _uuid_pk(),
        _tenant_id_column(),
        sa.Column(
            "treatment_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "system_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        *_audit_columns(),
        sa.ForeignKeyConstraint(
            ["treatment_id", "organization_id"],
            ["treatments.id", "treatments.organization_id"],
            name="fk_treatment_systems_treatment_tenant",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["system_id", "organization_id"],
            ["systems.id", "systems.organization_id"],
            name="fk_treatment_systems_system_tenant",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "treatment_id",
            "system_id",
            name="uq_treatment_systems_treatment_system",
        ),
    )

    # ── Treatment ↔ Vendor ──────────────────────────────────────────────────
    op.create_table(
        "treatment_vendors",
        _uuid_pk(),
        _tenant_id_column(),
        sa.Column(
            "treatment_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "vendor_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("relationship_type", sa.Text(), nullable=False),
        sa.Column("purpose", sa.Text(), nullable=True),
        sa.Column(
            "has_data_access",
            sa.Boolean(),
            nullable=False,
            server_default="true",
        ),
        sa.Column(
            "has_contract",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column("contract_reference", sa.Text(), nullable=True),
        sa.Column("engagement_object", sa.Text(), nullable=True),
        sa.Column("engagement_duration", sa.Text(), nullable=True),
        sa.Column(
            "has_subprocessors",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        *_audit_columns(),
        sa.ForeignKeyConstraint(
            ["treatment_id", "organization_id"],
            ["treatments.id", "treatments.organization_id"],
            name="fk_treatment_vendors_treatment_tenant",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["vendor_id", "organization_id"],
            ["vendors.id", "vendors.organization_id"],
            name="fk_treatment_vendors_vendor_tenant",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "treatment_id",
            "vendor_id",
            "relationship_type",
            name="uq_treatment_vendors_relationship",
        ),
        sa.CheckConstraint(
            "relationship_type IN ('encargado', 'cesionario', 'otro')",
            name="ck_treatment_vendors_relationship_type",
        ),
    )

    # ── Transferencias internacionales ──────────────────────────────────────
    op.create_table(
        "international_transfers",
        _uuid_pk(),
        _tenant_id_column(),
        sa.Column(
            "treatment_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "vendor_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column("recipient_name", sa.Text(), nullable=True),
        sa.Column("destination_country", sa.Text(), nullable=False),
        sa.Column(
            "adequacy_status",
            sa.Text(),
            nullable=False,
            server_default="pendiente",
        ),
        sa.Column("mechanism", sa.Text(), nullable=True),
        sa.Column("guarantees_description", sa.Text(), nullable=True),
        sa.Column("evidence_reference", sa.Text(), nullable=True),
        *_audit_columns(),
        sa.ForeignKeyConstraint(
            ["treatment_id", "organization_id"],
            ["treatments.id", "treatments.organization_id"],
            name="fk_international_transfers_treatment_tenant",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["vendor_id", "organization_id"],
            ["vendors.id", "vendors.organization_id"],
            name="fk_international_transfers_vendor_tenant",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            "vendor_id IS NOT NULL OR recipient_name IS NOT NULL",
            name="ck_international_transfers_recipient",
        ),
        sa.CheckConstraint(
            "adequacy_status IN "
            "('adecuado', 'no_adecuado', 'pendiente', 'no_determinado')",
            name="ck_international_transfers_adequacy_status",
        ),
    )

    # ── M3: sólo coherencia tenant del vínculo existente ───────────────────
    #
    # No se altera la semántica de LegalBase ni se implementa M3.
    op.create_foreign_key(
        "fk_legal_bases_treatment_tenant",
        "legal_bases",
        "treatments",
        ["treatment_id", "organization_id"],
        ["id", "organization_id"],
        ondelete="CASCADE",
    )

    # ── Índices tenant / relaciones ─────────────────────────────────────────
    for table in _NEW_TENANT_TABLES:
        op.create_index(
            f"ix_{table}_organization_id",
            table,
            ["organization_id"],
        )

    op.create_index(
        "ix_treatment_purposes_treatment_id",
        "treatment_purposes",
        ["treatment_id"],
    )
    op.create_index(
        "ix_treatment_data_categories_treatment_id",
        "treatment_data_categories",
        ["treatment_id"],
    )
    op.create_index(
        "ix_treatment_data_subjects_treatment_id",
        "treatment_data_subjects",
        ["treatment_id"],
    )
    op.create_index(
        "ix_treatment_data_sources_treatment_id",
        "treatment_data_sources",
        ["treatment_id"],
    )
    op.create_index(
        "ix_treatment_systems_treatment_id",
        "treatment_systems",
        ["treatment_id"],
    )
    op.create_index(
        "ix_treatment_systems_system_id",
        "treatment_systems",
        ["system_id"],
    )
    op.create_index(
        "ix_treatment_vendors_treatment_id",
        "treatment_vendors",
        ["treatment_id"],
    )
    op.create_index(
        "ix_treatment_vendors_vendor_id",
        "treatment_vendors",
        ["vendor_id"],
    )
    op.create_index(
        "ix_international_transfers_treatment_id",
        "international_transfers",
        ["treatment_id"],
    )
    op.create_index(
        "ix_international_transfers_vendor_id",
        "international_transfers",
        ["vendor_id"],
    )

    # ── Backfill seguro de campos legacy que sí pueden normalizarse ─────────
    #
    # No crea transferencias internacionales desde is_international porque
    # faltan país, destinatario y mecanismo jurídico.
    op.execute(
        """
        INSERT INTO treatment_purposes
            (organization_id, treatment_id, purpose, is_primary, sort_order)
        SELECT organization_id, id, purpose, true, 0
        FROM treatments
        WHERE purpose IS NOT NULL
          AND btrim(purpose) <> ''
        """
    )

    op.execute(
        """
        INSERT INTO treatment_data_categories
            (
                organization_id,
                treatment_id,
                category_code,
                category_name,
                is_sensitive
            )
        SELECT
            t.organization_id,
            t.id,
            'legacy_' || md5(category),
            category,
            t.has_sensitive
        FROM treatments t
        CROSS JOIN LATERAL unnest(
            COALESCE(t.data_categories, ARRAY[]::text[])
        ) AS category
        WHERE btrim(category) <> ''
        ON CONFLICT (treatment_id, category_code) DO NOTHING
        """
    )

    op.execute(
        """
        INSERT INTO treatment_data_subjects
            (
                organization_id,
                treatment_id,
                category_code,
                category_name
            )
        SELECT
            t.organization_id,
            t.id,
            'legacy_' || md5(subject),
            subject
        FROM treatments t
        CROSS JOIN LATERAL unnest(
            COALESCE(t.data_subjects, ARRAY[]::text[])
        ) AS subject
        WHERE btrim(subject) <> ''
        ON CONFLICT (treatment_id, category_code) DO NOTHING
        """
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


def downgrade() -> None:
    op.drop_constraint(
        "fk_legal_bases_treatment_tenant",
        "legal_bases",
        type_="foreignkey",
    )

    for table in reversed(_NEW_TENANT_TABLES):
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation_modify ON {table}")
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation_select ON {table}")

    # Las tablas eliminadas arrastran sus índices y constraints propios.
    for table in reversed(_NEW_TENANT_TABLES):
        op.drop_table(table)

    op.drop_constraint(
        "ck_treatments_status",
        "treatments",
        type_="check",
    )
    op.drop_constraint(
        "ck_treatments_organization_role",
        "treatments",
        type_="check",
    )

    for column in [
        "automated_decision_description",
        "has_automated_decisions",
        "deletion_method",
        "retention_rule",
        "status",
        "next_review_at",
        "last_reviewed_at",
        "start_date",
        "data_flow_description",
        "business_area",
        "organization_role",
        "description",
    ]:
        op.drop_column("treatments", column)

    for column in [
        "updated_by",
        "created_by",
        "updated_at",
        "country",
    ]:
        op.drop_column("vendors", column)

    for column in [
        "updated_by",
        "created_by",
        "updated_at",
        "hosting_country",
    ]:
        op.drop_column("systems", column)

    op.drop_constraint(
        "uq_vendors_id_organization_id",
        "vendors",
        type_="unique",
    )
    op.drop_constraint(
        "uq_systems_id_organization_id",
        "systems",
        type_="unique",
    )
    op.drop_constraint(
        "uq_treatments_id_organization_id",
        "treatments",
        type_="unique",
    )
