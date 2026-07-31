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


class LegalBasis(str, enum.Enum):
    consentimiento = "consentimiento"
    contrato = "contrato"
    obligacion_legal = "obligacion_legal"
    interes_legitimo = "interes_legitimo"
    otra = "otra"


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
    updated_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
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
    __table_args__ = (UniqueConstraint("organization_id", "profile_id"),)

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

    __table_args__ = (
        CheckConstraint(
            "status IN ('en_progreso', 'completado')",
            name="status_valido",
        ),
    )


class DiagnosticAnswer(Base):
    __tablename__ = "diagnostic_answers"
    __table_args__ = (
        UniqueConstraint("diagnostic_id", "pregunta_id"),
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


class Finding(Base):
    __tablename__ = "findings"
    __table_args__ = (
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
    updated_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
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
        UUID(as_uuid=True), ForeignKey("findings.id", ondelete="SET NULL"), nullable=True
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

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    provider: Mapped[str | None] = mapped_column(Text, nullable=True)
    hosting_location: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_international: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )


class Vendor(Base):
    __tablename__ = "vendors"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[ThirdPartyRole | None] = mapped_column(
        sa.Enum(ThirdPartyRole, name="third_party_role", create_type=False),
        nullable=True,
    )
    is_international: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    has_dpa: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )


class Treatment(Base):
    __tablename__ = "treatments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    purpose: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_categories: Mapped[list[str] | None] = mapped_column(
        ARRAY(Text), nullable=True
    )
    data_subjects: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    has_sensitive: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    retention: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_international: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
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


# ── Módulo 3 — Bases de licitud ───────────────────────────────────────────────


class LegalBase(Base):
    __tablename__ = "legal_bases"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    treatment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("treatments.id", ondelete="CASCADE"),
        nullable=False,
    )
    basis: Mapped[LegalBasis] = mapped_column(
        sa.Enum(LegalBasis, name="legal_basis", create_type=False), nullable=False
    )
    justification: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)
    approved: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    lia: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )


# ── Módulo 4 — Documentos generados ──────────────────────────────────────────


class Document(Base):
    __tablename__ = "documents"

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
