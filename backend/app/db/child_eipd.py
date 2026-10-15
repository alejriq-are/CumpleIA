"""Historial sucesor separado; no cambia payloads historicos."""

import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

POLICY_CHECK = """(jsonb_typeof(policy_snapshot)='object'
AND policy_snapshot ?& ARRAY['policy_schema_version','policy_reference','sources_status','acceptance_status','activation','allowed_decisions','global_policy_identity']
AND policy_snapshot - ARRAY['policy_schema_version','policy_reference','sources_status','acceptance_status','activation','allowed_decisions','global_policy_identity']='{}'::jsonb
AND jsonb_typeof(policy_snapshot->'policy_schema_version')='number' AND policy_snapshot->>'policy_schema_version'='1'
AND policy_snapshot->>'policy_reference'='m3-t1-infancia-pruebas-negativas-v1'
AND policy_snapshot->>'sources_status'='pendiente' AND policy_snapshot->>'acceptance_status'='pendiente'
AND policy_snapshot->>'activation'='deshabilitada'
AND policy_snapshot->'allowed_decisions'='["requiere_cambios","no_continuar"]'::jsonb
AND jsonb_typeof(policy_snapshot->'global_policy_identity')='object'
AND policy_snapshot->'global_policy_identity' ?& ARRAY['policy_version','policy_reference','policy_hash']
AND (policy_snapshot->'global_policy_identity') - ARRAY['policy_version','policy_reference','policy_hash']='{}'::jsonb
AND jsonb_typeof(policy_snapshot->'global_policy_identity'->'policy_version')='number'
AND policy_snapshot->'global_policy_identity'->>'policy_version'='1'
AND jsonb_typeof(policy_snapshot->'global_policy_identity'->'policy_reference')='string'
AND btrim(policy_snapshot->'global_policy_identity'->>'policy_reference')<>''
AND policy_snapshot->'global_policy_identity'->>'policy_hash' ~ '^[0-9a-f]{64}$') IS TRUE"""
METADATA_CHECK = """(jsonb_typeof(review_context_metadata)='object'
AND review_context_metadata ?& ARRAY['metadata_schema_version','resolution_binding_version','context_schema_version','child_coverage','document_hash','context_hash','child_material_hash','policy_hash']
AND review_context_metadata - ARRAY['metadata_schema_version','resolution_binding_version','context_schema_version','child_coverage','document_hash','context_hash','child_material_hash','policy_hash']='{}'::jsonb
AND jsonb_typeof(review_context_metadata->'metadata_schema_version')='number' AND review_context_metadata->>'metadata_schema_version'='3'
AND jsonb_typeof(review_context_metadata->'resolution_binding_version')='number' AND review_context_metadata->>'resolution_binding_version'='4'
AND jsonb_typeof(review_context_metadata->'context_schema_version')='number' AND review_context_metadata->>'context_schema_version'='4'
AND review_context_metadata->>'child_coverage'='contexto_v4'
AND review_context_metadata->>'document_hash'=document_hash
AND review_context_metadata->>'context_hash'=context_hash
AND review_context_metadata->>'child_material_hash'=child_material_hash
AND review_context_metadata->>'policy_hash'=policy_hash) IS TRUE"""


class ChildIdentity:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=sa.text("gen_random_uuid()"),
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    treatment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    assessment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    data_kind: Mapped[str] = mapped_column(
        sa.Text, nullable=False, server_default="ficticios"
    )
    document_hash: Mapped[str] = mapped_column(sa.Text, nullable=False)
    context_hash: Mapped[str] = mapped_column(sa.Text, nullable=False)
    child_material_hash: Mapped[str] = mapped_column(sa.Text, nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("profiles.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=sa.func.clock_timestamp(),
    )


def checks():
    return [
        sa.CheckConstraint("data_kind='ficticios'", name="data_kind"),
        sa.CheckConstraint(
            "document_hash ~ '^[0-9a-f]{64}$' AND context_hash ~ '^[0-9a-f]{64}$' AND child_material_hash ~ '^[0-9a-f]{64}$'",
            name="hashes",
        ),
    ]


class EipdChildResolution(ChildIdentity, Base):
    __tablename__ = "eipd_child_resolutions"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["assessment_id", "treatment_id", "organization_id"],
            [
                "legal_assessments.id",
                "legal_assessments.treatment_id",
                "legal_assessments.organization_id",
            ],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "assessment_id", "version", name="uq_child_resolution_version"
        ),
        sa.UniqueConstraint(
            "id",
            "assessment_id",
            "treatment_id",
            "organization_id",
            "document_hash",
            "context_hash",
            "child_material_hash",
            name="uq_child_resolution_material",
        ),
        sa.CheckConstraint("version>=1", name="version"),
        sa.CheckConstraint("jsonb_typeof(document)='object'", name="document"),
        sa.CheckConstraint(
            "(jsonb_typeof(context_snapshot)='object' AND context_snapshot->>'context_schema_version'='4' AND context_snapshot->>'organization_id'=organization_id::text AND context_snapshot->>'treatment_id'=treatment_id::text AND context_snapshot->>'assessment_id'=assessment_id::text AND jsonb_typeof(context_snapshot->'child_adolescent_assessment')='object') IS TRUE",
            name="context_identity",
        ),
        *checks(),
    )
    version: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    document: Mapped[dict] = mapped_column(JSONB, nullable=False)
    context_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)


class EipdChildReview(ChildIdentity, Base):
    __tablename__ = "eipd_child_reviews"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            [
                "resolution_id",
                "assessment_id",
                "treatment_id",
                "organization_id",
                "document_hash",
                "context_hash",
                "child_material_hash",
            ],
            [
                "eipd_child_resolutions.id",
                "eipd_child_resolutions.assessment_id",
                "eipd_child_resolutions.treatment_id",
                "eipd_child_resolutions.organization_id",
                "eipd_child_resolutions.document_hash",
                "eipd_child_resolutions.context_hash",
                "eipd_child_resolutions.child_material_hash",
            ],
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(
            "decision IN ('requiere_cambios','no_continuar')", name="negative_decision"
        ),
        sa.CheckConstraint(
            "btrim(rationale)<>'' AND btrim(review_reference)<>''", name="human_review"
        ),
        sa.CheckConstraint(POLICY_CHECK, name="disabled_policy"),
        sa.CheckConstraint(METADATA_CHECK, name="metadata_v3"),
        sa.CheckConstraint("policy_hash ~ '^[0-9a-f]{64}$'", name="policy_hash"),
        *checks(),
    )
    resolution_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    decision: Mapped[str] = mapped_column(sa.Text, nullable=False)
    rationale: Mapped[str] = mapped_column(sa.Text, nullable=False)
    review_reference: Mapped[str] = mapped_column(sa.Text, nullable=False)
    policy_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    policy_hash: Mapped[str] = mapped_column(sa.Text, nullable=False)
    review_context_metadata: Mapped[dict] = mapped_column(JSONB, nullable=False)
