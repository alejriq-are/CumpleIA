import enum
import uuid
from datetime import date, datetime

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

# ── Enums ────────────────────────────────────────────────────────────────────


class UserRole(str, enum.Enum):
    owner = "owner"
    admin = "admin"
    editor = "editor"
    viewer = "viewer"


class SubscriptionCommitmentType(str, enum.Enum):
    monthly = "monthly"
    annual_commitment_monthly_billing = "annual_commitment_monthly_billing"


class SubscriptionStatus(str, enum.Enum):
    active = "active"
    grace = "grace"
    suspended = "suspended"
    cancelled = "cancelled"


class RiskLevel(str, enum.Enum):
    alto = "alto"
    medio = "medio"
    bajo = "bajo"


class FindingStatus(str, enum.Enum):
    abierto = "abierto"
    en_proceso = "en_proceso"
    cerrado = "cerrado"
    no_aplica = "no_aplica"


class ThirdPartyRole(str, enum.Enum):
    encargado = "encargado"
    cesion = "cesion"
    transferencia_internacional = "transferencia_internacional"


class DocumentType(str, enum.Enum):
    politica_proteccion_datos = "politica_proteccion_datos"
    politica_privacidad = "politica_privacidad"
    politica_conservacion = "politica_conservacion"
    politica_seguridad = "politica_seguridad"
    procedimiento_arsop = "procedimiento_arsop"
    procedimiento_incidentes = "procedimiento_incidentes"


class DocumentStatus(str, enum.Enum):
    borrador = "borrador"
    aprobado = "aprobado"
    archivado = "archivado"


# ── Núcleo multi-tenant ───────────────────────────────────────────────────────


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    rut: Mapped[str | None] = mapped_column(Text, nullable=True)
    industry: Mapped[str | None] = mapped_column(Text, nullable=True)
    size: Mapped[str | None] = mapped_column(Text, nullable=True)
    plan: Mapped[str] = mapped_column(Text, nullable=False, server_default="free")
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    # onupdate: PATCH /organizations muta estos atributos vía ORM (nunca un
    # upsert crudo), así que se refresca solo — antes de ese endpoint esta
    # fila nunca se actualizaba después de crearse.
    updated_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    memberships: Mapped[list["Membership"]] = relationship(
        back_populates="organization"
    )


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    auth_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, nullable=False
    )
    email: Mapped[str] = mapped_column(Text, nullable=False)
    full_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Bandera global de plataforma (staff CumpleIA), independiente de cualquier
    # organización — no confundir con Membership.role, que es por-tenant.
    is_superadmin: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    memberships: Mapped[list["Membership"]] = relationship(back_populates="profile")


class Membership(Base):
    __tablename__ = "memberships"
    __table_args__ = (
        sa.Index("ix_memberships_organization_id", "organization_id"),
        UniqueConstraint("organization_id", "profile_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[UserRole] = mapped_column(
        sa.Enum(UserRole, name="user_role", create_type=False),
        nullable=False,
        server_default="owner",
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    organization: Mapped["Organization"] = relationship(back_populates="memberships")
    profile: Mapped["Profile"] = relationship(back_populates="memberships")


# ── Suscripción (vigencia de acceso por organización) ────────────────────────
# Ver docs/adr/0001-modelo-organizaciones-roles-suscripcion.md. Una fila por
# organización (organization_id UNIQUE); todas nacen 'active' porque el
# cálculo real de facturación todavía no existe (ver
# app/services/subscriptions.py).


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    commitment_type: Mapped[SubscriptionCommitmentType] = mapped_column(
        sa.Enum(
            SubscriptionCommitmentType,
            name="subscription_commitment_type",
            create_type=False,
        ),
        nullable=False,
    )
    status: Mapped[SubscriptionStatus] = mapped_column(
        sa.Enum(SubscriptionStatus, name="subscription_status", create_type=False),
        nullable=False,
        server_default="active",
    )
    grace_until: Mapped[datetime | None] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=True
    )
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=True
    )


# ── Módulo 1 — Cuestionario: contenido fijo (fuente CCS, global, sin RLS) ────


class Obligacion(Base):
    __tablename__ = "obligaciones"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    numero_guia: Mapped[str] = mapped_column(Text, nullable=False)
    nombre: Mapped[str] = mapped_column(Text, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )


class Seccion(Base):
    __tablename__ = "secciones"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    numero_romano: Mapped[str] = mapped_column(Text, nullable=False)
    nombre: Mapped[str] = mapped_column(Text, nullable=False)
    obligacion_id: Mapped[str] = mapped_column(
        Text, ForeignKey("obligaciones.id"), nullable=False
    )
    orden: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )


class Pregunta(Base):
    __tablename__ = "preguntas"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    seccion_id: Mapped[str] = mapped_column(
        Text, ForeignKey("secciones.id"), nullable=False
    )
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    orden: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )


# ── Módulo 1 — Cuestionario: parámetros de negocio versionados ───────────────
# Append-only: nunca se actualiza una versión existente, solo se crea una
# nueva y se activa. Editable solo por profiles.is_superadmin (ver RLS).


class ConfigVersion(Base):
    __tablename__ = "config_versiones"
    __table_args__ = (
        sa.Index(
            "ux_config_versiones_activa",
            "activa",
            unique=True,
            postgresql_where=sa.text("activa"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    numero_version: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    activa: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    nota: Mapped[str | None] = mapped_column(Text, nullable=True)
    creado_por: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False
    )
    creado_en: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )


class ConfigSeccionPeso(Base):
    __tablename__ = "config_seccion_pesos"
    __table_args__ = (UniqueConstraint("version_id", "seccion_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("config_versiones.id"), nullable=False
    )
    seccion_id: Mapped[str] = mapped_column(
        Text, ForeignKey("secciones.id"), nullable=False
    )
    peso_pct: Mapped[float] = mapped_column(
        Numeric(5, 2),
        CheckConstraint(
            "peso_pct >= 0 AND peso_pct <= 100",
            name="peso_pct_rango",
        ),
        nullable=False,
    )


class ConfigPreguntaRiesgo(Base):
    __tablename__ = "config_pregunta_riesgo"
    __table_args__ = (UniqueConstraint("version_id", "pregunta_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("config_versiones.id"), nullable=False
    )
    pregunta_id: Mapped[str] = mapped_column(
        Text, ForeignKey("preguntas.id"), nullable=False
    )
    riesgo: Mapped[RiskLevel] = mapped_column(
        sa.Enum(RiskLevel, name="risk_level", create_type=False), nullable=False
    )


# ── Módulo 1 — Diagnóstico ────────────────────────────────────────────────────


class Diagnostic(Base):
    __tablename__ = "diagnostics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    # UNIQUE (Tarea 3): "diagnóstico vigente" es get-or-create, no historial —
    # a lo sumo un Diagnostic por organización. Ver
    # app/services/diagnostico.py::obtener_o_crear_diagnostico_vigente
    # (patrón insert-then-select, igual que el aprovisionamiento JIT de
    # Profile en app/core/deps.py, para que sea seguro ante dos guardados
    # concurrentes).
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    # FK a la versión de config (pesos/riesgo) vigente cuando se generó, para
    # que el informe sea reproducible aunque el admin ajuste valores después.
    config_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("config_versiones.id"), nullable=False
    )
    global_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    section_scores: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="en_progreso"
    )
    # Tarea 4 (capa de IA): informe narrativo generado y saneado por
    # app/services/diagnostico_ia.py — None hasta la primera generación.
    # Se sobrescribe en cada regeneración (sin versionado en esta tarea).
    informe_ia: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    informe_generado_en: Mapped[datetime | None] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    # onupdate: Diagnostic siempre se toca vía atributos ORM (nunca un upsert
    # crudo como diagnostic_answers), así que basta con esto para que se
    # refresque cada vez que guardar_respuestas fija updated_by.
    updated_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=True
    )
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=True
    )

    __table_args__ = (
        sa.Index("ix_diagnostics_organization_id", "organization_id"),
        CheckConstraint(
            "status IN ('en_progreso', 'completado')",
            name="status_valido",
        ),
    )


class DiagnosticAnswer(Base):
    __tablename__ = "diagnostic_answers"
    __table_args__ = (
        sa.Index("ix_diagnostic_answers_organization_id", "organization_id"),
        UniqueConstraint(
            "diagnostic_id",
            "pregunta_id",
            name="uq_diagnostic_answers_diagnostic_id_pregunta_id",
        ),
        CheckConstraint(
            "answer IN ('Sí', 'Parcial', 'No', 'N/A')",
            name="answer_valido",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    diagnostic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("diagnostics.id", ondelete="CASCADE"),
        nullable=False,
    )
    pregunta_id: Mapped[str] = mapped_column(
        Text, ForeignKey("preguntas.id"), nullable=False
    )
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    # Trazabilidad de quién respondió (mejoras al informe, ver migración
    # 0008): actualizado explícitamente por
    # app/services/diagnostico.py::guardar_respuestas, no por `onupdate` —
    # el upsert (`ON CONFLICT DO UPDATE`) no pasa por el flush de la ORM.
    updated_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=True
    )
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=True
    )


class Finding(Base):
    __tablename__ = "findings"
    __table_args__ = (
        sa.Index("ix_findings_organization_id", "organization_id"),
        UniqueConstraint(
            "diagnostic_id",
            "pregunta_id",
            name="uq_findings_diagnostic_id_pregunta_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    diagnostic_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("diagnostics.id", ondelete="SET NULL"),
        nullable=True,
    )
    # Pregunta que originó la brecha (Fase 1, Módulo 1, Tarea 3): permite que
    # app/services/diagnostico.py sincronice (abra/cierre) el Finding de cada
    # recálculo por identidad, no por comparar el texto libre de description.
    # Nula para hallazgos que no vengan del motor de puntaje (p. ej. RAT,
    # módulos futuros).
    pregunta_id: Mapped[str | None] = mapped_column(
        Text, ForeignKey("preguntas.id"), nullable=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    risk: Mapped[RiskLevel] = mapped_column(
        sa.Enum(RiskLevel, name="risk_level", create_type=False), nullable=False
    )
    corrective_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    responsible: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[FindingStatus] = mapped_column(
        sa.Enum(FindingStatus, name="finding_status", create_type=False),
        nullable=False,
        server_default="abierto",
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    # onupdate: recalcular_diagnostico muta description/risk/status vía
    # atributos ORM (nunca un upsert crudo), así que se refresca solo.
    updated_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class ReferenceDocument(Base):
    """Documento de referencia (ADR 0002, capa 3): la organización enlaza su
    propia política de gobernanza para justificar cómo resuelve una brecha,
    en vez de que CumpleIA fije plazos de cumplimiento propios sin respaldo
    normativo. Hoy solo se usa `tipo='politica_interna_gobernanza'` (tabla
    tenant-scoped); `instructivo_agencia` es de dominio, pero poblarlo como
    catálogo global (sin organization_id, análogo a `Obligacion`/`Seccion`/
    `Pregunta`) es trabajo futuro, no de esta tabla — ver ADR 0002.
    """

    __tablename__ = "reference_documents"
    __table_args__ = (
        sa.Index("ix_reference_documents_organization_id", "organization_id"),
        CheckConstraint(
            "tipo IN ('politica_interna_gobernanza', 'instructivo_agencia')",
            name="tipo_valido",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    tipo: Mapped[str] = mapped_column(Text, nullable=False)
    titulo: Mapped[str] = mapped_column(Text, nullable=False)
    fecha: Mapped[date | None] = mapped_column(sa.Date, nullable=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    finding_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("findings.id", ondelete="SET NULL"),
        nullable=True,
    )
    diagnostic_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("diagnostics.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=True
    )
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=True
    )


# ── Módulo 2 — Inventario (RAT) ───────────────────────────────────────────────


class System(Base):
    __tablename__ = "systems"
    __table_args__ = (
        sa.Index("ix_systems_organization_id", "organization_id"),
        UniqueConstraint(
            "id",
            "organization_id",
            name="uq_systems_id_organization_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    provider: Mapped[str | None] = mapped_column(Text, nullable=True)
    hosting_location: Mapped[str | None] = mapped_column(Text, nullable=True)
    hosting_country: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Legacy: se conserva durante la transición a international_transfers.
    is_international: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
    )

    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id"),
        nullable=True,
    )
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id"),
        nullable=True,
    )


class Vendor(Base):
    __tablename__ = "vendors"
    __table_args__ = (
        sa.Index("ix_vendors_organization_id", "organization_id"),
        UniqueConstraint(
            "id",
            "organization_id",
            name="uq_vendors_id_organization_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    country: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Legacy: la relación canónica vive en treatment_vendors.
    role: Mapped[ThirdPartyRole | None] = mapped_column(
        sa.Enum(
            ThirdPartyRole,
            name="third_party_role",
            create_type=False,
        ),
        nullable=True,
    )
    is_international: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
    )
    has_dpa: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
    )

    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id"),
        nullable=True,
    )
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id"),
        nullable=True,
    )


class Treatment(Base):
    __tablename__ = "treatments"
    __table_args__ = (
        sa.Index("ix_treatments_organization_id", "organization_id"),
        UniqueConstraint(
            "id",
            "organization_id",
            name="uq_treatments_id_organization_id",
        ),
        CheckConstraint(
            "organization_role IS NULL OR "
            "organization_role IN ('responsable', 'encargado')",
            name="organization_role",
        ),
        CheckConstraint(
            "status IN ('borrador', 'activo', 'archivado')",
            name="status",
        ),
        *(
            CheckConstraint(
                f"{field} IS NULL OR {field} IN ('si', 'no', 'pendiente')",
                name=field,
            )
            for field in (
                "systems_declaration",
                "vendors_declaration",
                "international_transfers_declaration",
            )
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    organization_role: Mapped[str | None] = mapped_column(Text, nullable=True)
    business_area: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_flow_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    start_date: Mapped[date | None] = mapped_column(sa.Date, nullable=True)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=True,
    )
    next_review_at: Mapped[datetime | None] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default="borrador",
    )
    activated_at: Mapped[datetime | None] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=True,
    )
    archived_at: Mapped[datetime | None] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=True,
    )
    status_changed_at: Mapped[datetime | None] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=True,
    )

    retention_rule: Mapped[str | None] = mapped_column(Text, nullable=True)
    systems_declaration: Mapped[str | None] = mapped_column(Text, nullable=True)
    vendors_declaration: Mapped[str | None] = mapped_column(Text, nullable=True)
    international_transfers_declaration: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    deletion_method: Mapped[str | None] = mapped_column(Text, nullable=True)

    has_automated_decisions: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
    )
    automated_decision_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Legacy: se conservan hasta completar transición funcional de M2.
    purpose: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_categories: Mapped[list[str] | None] = mapped_column(
        ARRAY(Text),
        nullable=True,
    )
    data_subjects: Mapped[list[str] | None] = mapped_column(
        ARRAY(Text),
        nullable=True,
    )
    has_sensitive: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
    )
    retention: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_international: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
    )

    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id"),
        nullable=True,
    )
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id"),
        nullable=True,
    )


class TreatmentPurpose(Base):
    __tablename__ = "treatment_purposes"
    __table_args__ = (
        sa.Index("ix_treatment_purposes_organization_id", "organization_id"),
        sa.Index("ix_treatment_purposes_treatment_id", "treatment_id"),
        sa.ForeignKeyConstraint(
            ["treatment_id", "organization_id"],
            ["treatments.id", "treatments.organization_id"],
            name="fk_treatment_purposes_treatment_tenant",
            ondelete="CASCADE",
        ),
        UniqueConstraint(
            "treatment_id",
            "purpose",
            name="uq_treatment_purposes_treatment_purpose",
        ),
        CheckConstraint(
            "sort_order >= 0",
            name="sort_order",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    treatment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    purpose: Mapped[str] = mapped_column(Text, nullable=False)
    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
    )
    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id"),
        nullable=True,
    )
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id"),
        nullable=True,
    )


class TreatmentDataCategory(Base):
    __tablename__ = "treatment_data_categories"
    __table_args__ = (
        sa.Index("ix_treatment_data_categories_organization_id", "organization_id"),
        sa.Index("ix_treatment_data_categories_treatment_id", "treatment_id"),
        sa.ForeignKeyConstraint(
            ["treatment_id", "organization_id"],
            ["treatments.id", "treatments.organization_id"],
            name="fk_treatment_data_categories_treatment_tenant",
            ondelete="CASCADE",
        ),
        UniqueConstraint(
            "treatment_id",
            "category_code",
            name="uq_treatment_data_categories_treatment_code",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    treatment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    category_code: Mapped[str] = mapped_column(Text, nullable=False)
    category_name: Mapped[str] = mapped_column(Text, nullable=False)
    is_sensitive: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id"),
        nullable=True,
    )
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id"),
        nullable=True,
    )


class TreatmentDataSubject(Base):
    __tablename__ = "treatment_data_subjects"
    __table_args__ = (
        sa.Index("ix_treatment_data_subjects_organization_id", "organization_id"),
        sa.Index("ix_treatment_data_subjects_treatment_id", "treatment_id"),
        sa.ForeignKeyConstraint(
            ["treatment_id", "organization_id"],
            ["treatments.id", "treatments.organization_id"],
            name="fk_treatment_data_subjects_treatment_tenant",
            ondelete="CASCADE",
        ),
        UniqueConstraint(
            "treatment_id",
            "category_code",
            name="uq_treatment_data_subjects_treatment_code",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    treatment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    category_code: Mapped[str] = mapped_column(Text, nullable=False)
    category_name: Mapped[str] = mapped_column(Text, nullable=False)
    includes_children: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
    )
    includes_adolescents: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
    )
    is_vulnerable_group: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id"),
        nullable=True,
    )
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id"),
        nullable=True,
    )


class TreatmentDataSource(Base):
    __tablename__ = "treatment_data_sources"
    __table_args__ = (
        sa.Index("ix_treatment_data_sources_organization_id", "organization_id"),
        sa.Index("ix_treatment_data_sources_treatment_id", "treatment_id"),
        sa.ForeignKeyConstraint(
            ["treatment_id", "organization_id"],
            ["treatments.id", "treatments.organization_id"],
            name="fk_treatment_data_sources_treatment_tenant",
            ondelete="CASCADE",
        ),
        CheckConstraint(
            "source_type IN "
            "('titular', 'tercero', 'fuente_publica', "
            "'recogida_automatica', 'otro')",
            name="source_type",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    treatment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    source_type: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_public_source: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id"),
        nullable=True,
    )
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id"),
        nullable=True,
    )


class TreatmentSystem(Base):
    __tablename__ = "treatment_systems"
    __table_args__ = (
        sa.Index("ix_treatment_systems_organization_id", "organization_id"),
        sa.Index("ix_treatment_systems_system_id", "system_id"),
        sa.Index("ix_treatment_systems_treatment_id", "treatment_id"),
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
        UniqueConstraint(
            "treatment_id",
            "system_id",
            name="uq_treatment_systems_treatment_system",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    treatment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    system_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id"),
        nullable=True,
    )
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id"),
        nullable=True,
    )


class TreatmentVendor(Base):
    __tablename__ = "treatment_vendors"
    __table_args__ = (
        sa.Index("ix_treatment_vendors_organization_id", "organization_id"),
        sa.Index("ix_treatment_vendors_treatment_id", "treatment_id"),
        sa.Index("ix_treatment_vendors_vendor_id", "vendor_id"),
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
        UniqueConstraint(
            "treatment_id",
            "vendor_id",
            "relationship_type",
            name="uq_treatment_vendors_relationship",
        ),
        CheckConstraint(
            "relationship_type IN ('encargado', 'cesionario', 'otro')",
            name="relationship_type",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    treatment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    vendor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    relationship_type: Mapped[str] = mapped_column(Text, nullable=False)
    purpose: Mapped[str | None] = mapped_column(Text, nullable=True)
    has_data_access: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true",
    )
    has_contract: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
    )
    contract_reference: Mapped[str | None] = mapped_column(Text, nullable=True)
    engagement_object: Mapped[str | None] = mapped_column(Text, nullable=True)
    engagement_duration: Mapped[str | None] = mapped_column(Text, nullable=True)
    has_subprocessors: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id"),
        nullable=True,
    )
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id"),
        nullable=True,
    )


class InternationalTransfer(Base):
    __tablename__ = "international_transfers"
    __table_args__ = (
        sa.Index("ix_international_transfers_organization_id", "organization_id"),
        sa.Index("ix_international_transfers_treatment_id", "treatment_id"),
        sa.Index("ix_international_transfers_vendor_id", "vendor_id"),
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
        CheckConstraint(
            "vendor_id IS NOT NULL OR recipient_name IS NOT NULL",
            name="recipient",
        ),
        CheckConstraint(
            "adequacy_status IN "
            "('adecuado', 'no_adecuado', 'pendiente', 'no_determinado')",
            name="adequacy_status",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    treatment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    vendor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    recipient_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    destination_country: Mapped[str] = mapped_column(Text, nullable=False)
    adequacy_status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default="pendiente",
    )
    mechanism: Mapped[str | None] = mapped_column(Text, nullable=True)
    guarantees_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    evidence_reference: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id"),
        nullable=True,
    )
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id"),
        nullable=True,
    )


# ── Módulo 3 — Bases de licitud ───────────────────────────────────────────────


class LegalAssessmentSeries(Base):
    __tablename__ = "legal_assessment_series"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["treatment_id", "organization_id"],
            ["treatments.id", "treatments.organization_id"],
            name="fk_legal_assessment_series_treatment_tenant",
            ondelete="CASCADE",
        ),
        UniqueConstraint(
            "id",
            "treatment_id",
            "organization_id",
            name="uq_legal_assessment_series_identity_tenant",
        ),
        UniqueConstraint(
            "organization_id",
            "treatment_id",
            "purpose_key",
            name="uq_legal_assessment_series_treatment_purpose",
        ),
        CheckConstraint(
            "next_version >= 1",
            name="ck_legal_assessment_series_next_version",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    treatment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    purpose_key: Mapped[str] = mapped_column(Text, nullable=False)
    purpose_text: Mapped[str] = mapped_column(Text, nullable=False)
    next_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="1",
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id"),
        nullable=True,
    )
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id"),
        nullable=True,
    )


class LegalAssessment(Base):
    __tablename__ = "legal_assessments"
    __table_args__ = (
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
        UniqueConstraint(
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
        UniqueConstraint(
            "series_id",
            "version",
            name="uq_legal_assessments_series_version",
        ),
        UniqueConstraint(
            "id", "organization_id", name="uq_legal_assessments_id_tenant"
        ),
        CheckConstraint(
            "eipd_resolution_assessment IS NULL OR jsonb_typeof(eipd_resolution_assessment) = 'object'",
            name="ck_legal_assessments_eipd_resolution_object",
        ),
        CheckConstraint(
            "eipd_screening IS NULL OR jsonb_typeof(eipd_screening) = 'object'",
            name="ck_legal_assessments_eipd_screening_object",
        ),
        CheckConstraint(
            "contract_assessment IS NULL OR jsonb_typeof(contract_assessment) = 'object'",
            name="ck_legal_assessments_contract_assessment_object",
        ),
        CheckConstraint(
            "legal_obligation_assessment IS NULL OR jsonb_typeof(legal_obligation_assessment) = 'object'",
            name="ck_legal_assessments_legal_obligation_object",
        ),
        CheckConstraint(
            "rights_defense_assessment IS NULL OR jsonb_typeof(rights_defense_assessment) = 'object'",
            name="ck_legal_assessments_rights_defense_object",
        ),
        CheckConstraint(
            "economic_obligations_assessment IS NULL OR jsonb_typeof(economic_obligations_assessment) = 'object'",
            name="ck_legal_assessments_economic_obligations_object",
        ),
        CheckConstraint(
            "geolocation_assessment IS NULL OR jsonb_typeof(geolocation_assessment) = 'object'",
            name="ck_legal_assessments_geolocation_object",
        ),
        CheckConstraint(
            "sensitive_consent_assessment IS NULL OR jsonb_typeof(sensitive_consent_assessment) = 'object'",
            name="ck_legal_assessments_sensitive_consent_object",
        ),
        CheckConstraint(
            "sensitive_rights_exception_assessment IS NULL OR jsonb_typeof(sensitive_rights_exception_assessment) = 'object'",
            name="ck_legal_assessments_sensitive_rights_exception_object",
        ),
        CheckConstraint(
            "biometric_rights_exception_assessment IS NULL OR jsonb_typeof(biometric_rights_exception_assessment) = 'object'",
            name="ck_legal_assessments_biometric_rights_exception_object",
        ),
        CheckConstraint(
            "biometric_assessment IS NULL OR jsonb_typeof(biometric_assessment) = 'object'",
            name="ck_legal_assessments_biometric_object",
        ),
        CheckConstraint(
            "health_assessment IS NULL OR jsonb_typeof(health_assessment) = 'object'",
            name="ck_legal_assessments_health_object",
        ),
        CheckConstraint(
            "research_assessment IS NULL OR jsonb_typeof(research_assessment) = 'object'",
            name="ck_legal_assessments_research_object",
        ),
        CheckConstraint("version >= 1", name="ck_legal_assessments_version"),
        CheckConstraint(
            "schema_version >= 1",
            name="ck_legal_assessments_schema_version",
        ),
        CheckConstraint(
            "rat_context_schema_version >= 1",
            name="ck_legal_assessments_rat_context_schema_version",
        ),
        CheckConstraint(
            "status IN ('borrador', 'confirmado', 'reemplazado')",
            name="ck_legal_assessments_status",
        ),
        CheckConstraint(
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
        CheckConstraint(
            "replaced_by_assessment_id IS NULL " "OR replaced_by_assessment_id <> id",
            name="ck_legal_assessments_not_self_replaced",
        ),
        CheckConstraint(
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
        sa.Index(
            "uq_legal_assessments_one_draft_per_series",
            "series_id",
            unique=True,
            postgresql_where=sa.text("status = 'borrador'"),
        ),
        sa.Index(
            "uq_legal_assessments_one_confirmed_per_series",
            "series_id",
            unique=True,
            postgresql_where=sa.text("status = 'confirmado'"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    series_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    treatment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default="borrador",
    )
    legal_basis: Mapped[str | None] = mapped_column(Text, nullable=True)
    justification: Mapped[str | None] = mapped_column(Text, nullable=True)
    purpose_snapshot: Mapped[str] = mapped_column(Text, nullable=False)
    rat_context_hash: Mapped[str] = mapped_column(Text, nullable=False)
    rat_context_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    consent_assessment: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    lia_assessment: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    geolocation_assessment: Mapped[dict | None] = mapped_column(
        JSONB(none_as_null=True), nullable=True
    )
    sensitive_consent_assessment: Mapped[dict | None] = mapped_column(
        JSONB(none_as_null=True), nullable=True
    )
    sensitive_rights_exception_assessment: Mapped[dict | None] = mapped_column(
        JSONB(none_as_null=True), nullable=True
    )
    biometric_rights_exception_assessment: Mapped[dict | None] = mapped_column(
        JSONB(none_as_null=True), nullable=True
    )
    biometric_assessment: Mapped[dict | None] = mapped_column(
        JSONB(none_as_null=True), nullable=True
    )
    research_assessment: Mapped[dict | None] = mapped_column(
        JSONB(none_as_null=True), nullable=True
    )
    health_assessment: Mapped[dict | None] = mapped_column(
        JSONB(none_as_null=True), nullable=True
    )
    economic_obligations_assessment: Mapped[dict | None] = mapped_column(
        JSONB(none_as_null=True), nullable=True
    )
    rights_defense_assessment: Mapped[dict | None] = mapped_column(
        JSONB(none_as_null=True), nullable=True
    )
    legal_obligation_assessment: Mapped[dict | None] = mapped_column(
        JSONB(none_as_null=True), nullable=True
    )
    contract_assessment: Mapped[dict | None] = mapped_column(
        JSONB(none_as_null=True), nullable=True
    )
    special_conditions: Mapped[dict | None] = mapped_column(
        JSONB(none_as_null=True), nullable=True
    )
    eipd_screening: Mapped[dict | None] = mapped_column(
        JSONB(none_as_null=True), nullable=True
    )
    eipd_resolution_assessment: Mapped[dict | None] = mapped_column(
        JSONB(none_as_null=True), nullable=True
    )
    schema_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="1",
    )
    rat_context_schema_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="1",
    )
    confirmed_at: Mapped[datetime | None] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=True,
    )
    confirmed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id"),
        nullable=True,
    )
    replaced_at: Mapped[datetime | None] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=True,
    )
    replaced_by_assessment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id"),
        nullable=True,
    )
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id"),
        nullable=True,
    )


class EipdResolutionReview(Base):
    """Historial de revision EIPD; runtime solo puede insertar y leer."""

    __tablename__ = "eipd_resolution_reviews"
    __table_args__ = (
        CheckConstraint(
            "review_context_metadata IS NULL OR (\njsonb_typeof(review_context_metadata) = 'object'\nAND review_context_metadata ?& ARRAY['metadata_schema_version','resolution_binding_version','context_schema_version','research_coverage','document_hash','context_hash','research_material_hash']\nAND review_context_metadata - ARRAY['metadata_schema_version','resolution_binding_version','context_schema_version','research_coverage','document_hash','context_hash','research_material_hash'] = '{}'::jsonb\nAND jsonb_typeof(review_context_metadata->'metadata_schema_version') = 'number'\nAND review_context_metadata->>'metadata_schema_version' = '1'\nAND jsonb_typeof(review_context_metadata->'resolution_binding_version') = 'number'\nAND review_context_metadata->>'resolution_binding_version' IN ('1','2')\nAND jsonb_typeof(review_context_metadata->'context_schema_version') = 'number'\nAND review_context_metadata->>'context_schema_version' = review_context_metadata->>'resolution_binding_version'\nAND jsonb_typeof(review_context_metadata->'research_coverage') = 'string'\nAND review_context_metadata->>'research_coverage' = CASE WHEN review_context_metadata->>'context_schema_version' = '2' THEN 'contexto_v2' ELSE 'no_cubierta' END\nAND jsonb_typeof(review_context_metadata->'document_hash') = 'string'\nAND review_context_metadata->>'document_hash' = document_hash\nAND jsonb_typeof(review_context_metadata->'context_hash') = 'string'\nAND review_context_metadata->>'context_hash' = context_hash\nAND (review_context_metadata->'research_material_hash' = 'null'::jsonb OR\n    (review_context_metadata->>'context_schema_version' = '2'\n     AND jsonb_typeof(review_context_metadata->'research_material_hash') = 'string'\n     AND review_context_metadata->>'research_material_hash' ~ '^[0-9a-f]{64}$'))\n) IS TRUE",
            name="ck_eipd_reviews_context_metadata",
        ),
        UniqueConstraint(
            "id",
            "assessment_id",
            "organization_id",
            "document_hash",
            "context_hash",
            "policy_version",
            "policy_reference",
            "policy_hash",
            "decision",
            name="uq_eipd_reviews_confirmation_binding",
        ),
        sa.ForeignKeyConstraint(
            ["assessment_id", "organization_id"],
            ["legal_assessments.id", "legal_assessments.organization_id"],
            name="fk_eipd_resolution_reviews_assessment_tenant",
        ),
        CheckConstraint(
            "decision IN ('continuar', 'requiere_cambios', 'no_continuar')",
            name="ck_eipd_resolution_reviews_decision",
        ),
        CheckConstraint(
            "rationale ~ '[^[:space:]]'", name="ck_eipd_resolution_reviews_rationale"
        ),
        CheckConstraint(
            "review_reference ~ '[^[:space:]]'",
            name="ck_eipd_resolution_reviews_reference",
        ),
        CheckConstraint(
            "document_hash ~ '^[0-9a-f]{64}$'",
            name="ck_eipd_resolution_reviews_document_hash",
        ),
        CheckConstraint(
            "context_hash ~ '^[0-9a-f]{64}$'",
            name="ck_eipd_resolution_reviews_context_hash",
        ),
        CheckConstraint(
            "(policy_version IS NULL AND policy_reference IS NULL AND policy_hash IS NULL) OR (policy_version IS NOT NULL AND policy_reference IS NOT NULL AND policy_hash IS NOT NULL AND policy_version = 1 AND policy_reference ~ '[^[:space:]]' AND policy_hash ~ '^[0-9a-f]{64}$')",
            name="ck_eipd_resolution_reviews_policy_identity",
        ),
        sa.Index("ix_eipd_resolution_reviews_organization_id", "organization_id"),
        sa.Index(
            "ix_eipd_resolution_reviews_assessment_history",
            "organization_id",
            "assessment_id",
            "created_at",
            "id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    assessment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    decision: Mapped[str] = mapped_column(Text, nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    review_reference: Mapped[str] = mapped_column(Text, nullable=False)
    document_hash: Mapped[str] = mapped_column(Text, nullable=False)
    context_hash: Mapped[str] = mapped_column(Text, nullable=False)
    review_context_metadata: Mapped[dict | None] = mapped_column(
        JSONB(none_as_null=True), nullable=True
    )
    policy_version: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    policy_reference: Mapped[str | None] = mapped_column(Text, nullable=True)
    policy_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.clock_timestamp(),
    )


# ── Módulo 4 — Documentos generados ──────────────────────────────────────────


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (sa.Index("ix_documents_organization_id", "organization_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    type: Mapped[DocumentType] = mapped_column(
        sa.Enum(DocumentType, name="document_type", create_type=False), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    status: Mapped[DocumentStatus] = mapped_column(
        sa.Enum(DocumentStatus, name="document_status", create_type=False),
        nullable=False,
        server_default="borrador",
    )
    storage_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=True
    )


# ── Módulo 5 — Bitácora de evidencia (append-only) ───────────────────────────


class EvidenceEvent(Base):
    __tablename__ = "evidence_events"
    __table_args__ = (
        sa.Index("ix_evidence_events_organization_id", "organization_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    actor_profile_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=True
    )
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    payload_hash: Mapped[str] = mapped_column(Text, nullable=False)
    prev_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    event_hash: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )


# ── RAG — Base de conocimiento (global, sin RLS por tenant) ──────────────────


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"
    __table_args__ = (
        sa.Index(
            "knowledge_chunks_embedding_idx",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    source: Mapped[str] = mapped_column(Text, nullable=False)
    reference: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list | None] = mapped_column(Vector(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )


class EipdPolicyPublication(Base):
    """Control global; escritura solo por canal administrativo separado."""

    __tablename__ = "eipd_policy_publications"
    __table_args__ = (
        UniqueConstraint(
            "id",
            "policy_version",
            "policy_reference",
            "policy_hash",
            name="uq_eipd_publications_confirmation_binding",
        ),
        UniqueConstraint("policy_reference"),
        UniqueConstraint("id", "policy_hash"),
        CheckConstraint("policy_version = 1", name="policy_version"),
        CheckConstraint("policy_reference ~ '[^[:space:]]'", name="reference"),
        CheckConstraint("policy_hash ~ '^[0-9a-f]{64}$'", name="hash"),
        CheckConstraint(
            "rationale ~ '[^[:space:]]' AND evidence_reference ~ '[^[:space:]]'",
            name="evidence",
        ),
        CheckConstraint(
            "jsonb_typeof(payload) = 'object' AND payload ? 'policy_version' AND payload ? 'policy_reference' AND payload->>'policy_version' = '1' AND payload->>'policy_reference' = policy_reference",
            name="payload_identity",
        ),
    )
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    policy_version: Mapped[int] = mapped_column(Integer, nullable=False)
    policy_reference: Mapped[str] = mapped_column(Text, nullable=False)
    policy_hash: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.clock_timestamp(),
    )
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_reference: Mapped[str] = mapped_column(Text, nullable=False)


class EipdPolicySelection(Base):
    __tablename__ = "eipd_policy_selections"
    __table_args__ = (
        UniqueConstraint("revision"),
        UniqueConstraint("publication_id"),
        UniqueConstraint(
            "revision",
            "publication_id",
            "policy_hash",
            name="uq_eipd_policy_selections_revision_publication_hash",
        ),
        UniqueConstraint(
            "revision",
            "publication_id",
            "id",
            name="uq_eipd_policy_selections_revision_publication_id",
        ),
        sa.ForeignKeyConstraint(
            ["publication_id", "policy_hash"],
            ["eipd_policy_publications.id", "eipd_policy_publications.policy_hash"],
        ),
        sa.ForeignKeyConstraint(
            ["previous_revision", "previous_publication_id", "previous_policy_hash"],
            [
                "eipd_policy_selections.revision",
                "eipd_policy_selections.publication_id",
                "eipd_policy_selections.policy_hash",
            ],
        ),
        CheckConstraint(
            "revision > 0 AND previous_revision >= 0 AND revision = previous_revision + 1",
            name="revision",
        ),
        CheckConstraint(
            "(previous_revision = 0 AND previous_publication_id IS NULL AND previous_policy_hash IS NULL) OR (previous_revision > 0 AND previous_publication_id IS NOT NULL AND previous_policy_hash IS NOT NULL)",
            name="previous_identity",
        ),
        CheckConstraint(
            "publication_id IS DISTINCT FROM previous_publication_id",
            name="no_reselection",
        ),
        CheckConstraint(
            "rationale ~ '[^[:space:]]' AND evidence_reference ~ '[^[:space:]]'",
            name="evidence",
        ),
    )
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    previous_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    revision: Mapped[int] = mapped_column(Integer, nullable=False)
    previous_publication_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    previous_policy_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    publication_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    policy_hash: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.clock_timestamp(),
    )
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_reference: Mapped[str] = mapped_column(Text, nullable=False)


class EipdPolicySelector(Base):
    __tablename__ = "eipd_policy_selector"
    __table_args__ = (
        CheckConstraint("id = 1", name="singleton"),
        CheckConstraint("revision > 0", name="revision"),
        sa.ForeignKeyConstraint(
            ["revision", "publication_id", "selection_id"],
            [
                "eipd_policy_selections.revision",
                "eipd_policy_selections.publication_id",
                "eipd_policy_selections.id",
            ],
        ),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    revision: Mapped[int] = mapped_column(Integer, nullable=False)
    publication_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    selection_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)


class EipdConfirmationEvidence(Base):
    """Evidencia tenant append-only; no habilita por si misma la confirmacion."""

    __tablename__ = "eipd_confirmation_evidence"
    __table_args__ = (
        UniqueConstraint("assessment_id"),
        sa.ForeignKeyConstraint(
            ["assessment_id", "organization_id"],
            ["legal_assessments.id", "legal_assessments.organization_id"],
        ),
        sa.ForeignKeyConstraint(
            [
                "review_id",
                "assessment_id",
                "organization_id",
                "document_hash",
                "context_hash",
                "policy_version",
                "policy_reference",
                "policy_hash",
                "review_decision",
            ],
            [
                "eipd_resolution_reviews.id",
                "eipd_resolution_reviews.assessment_id",
                "eipd_resolution_reviews.organization_id",
                "eipd_resolution_reviews.document_hash",
                "eipd_resolution_reviews.context_hash",
                "eipd_resolution_reviews.policy_version",
                "eipd_resolution_reviews.policy_reference",
                "eipd_resolution_reviews.policy_hash",
                "eipd_resolution_reviews.decision",
            ],
        ),
        sa.ForeignKeyConstraint(
            ["publication_id", "policy_version", "policy_reference", "policy_hash"],
            [
                "eipd_policy_publications.id",
                "eipd_policy_publications.policy_version",
                "eipd_policy_publications.policy_reference",
                "eipd_policy_publications.policy_hash",
            ],
        ),
        sa.ForeignKeyConstraint(
            ["selector_revision", "publication_id", "selection_id"],
            [
                "eipd_policy_selections.revision",
                "eipd_policy_selections.publication_id",
                "eipd_policy_selections.id",
            ],
        ),
        CheckConstraint("review_decision = 'continuar'", name="positive_review"),
        CheckConstraint(
            "policy_version = 1 AND selector_revision > 0", name="versions"
        ),
        CheckConstraint("policy_reference ~ '[^[:space:]]'", name="policy_reference"),
        CheckConstraint(
            "policy_hash ~ '^[0-9a-f]{64}$' AND document_hash ~ '^[0-9a-f]{64}$' AND context_hash ~ '^[0-9a-f]{64}$'",
            name="hashes",
        ),
        sa.Index("ix_eipd_confirmation_evidence_organization_id", "organization_id"),
    )
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    assessment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    review_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    publication_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    selector_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    selection_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    policy_version: Mapped[int] = mapped_column(Integer, nullable=False)
    policy_reference: Mapped[str] = mapped_column(Text, nullable=False)
    policy_hash: Mapped[str] = mapped_column(Text, nullable=False)
    document_hash: Mapped[str] = mapped_column(Text, nullable=False)
    context_hash: Mapped[str] = mapped_column(Text, nullable=False)
    review_decision: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="continuar"
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.clock_timestamp(),
    )
