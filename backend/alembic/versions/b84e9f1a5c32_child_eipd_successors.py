"""Historial sucesor infancia, politica negativa cerrada y RLS desde origen."""

import sqlalchemy as sa

from alembic import op

revision = "b84e9f1a5c32"
down_revision = "a73d8e0c4b21"
branch_labels = None
depends_on = None

DDL = (
    """
CREATE TABLE eipd_child_resolutions (
    version INTEGER NOT NULL, 
    document JSONB NOT NULL, 
    context_snapshot JSONB NOT NULL, 
    id UUID DEFAULT gen_random_uuid() NOT NULL, 
    organization_id UUID NOT NULL, 
    treatment_id UUID NOT NULL, 
    assessment_id UUID NOT NULL, 
    data_kind TEXT DEFAULT 'ficticios' NOT NULL, 
    document_hash TEXT NOT NULL, 
    context_hash TEXT NOT NULL, 
    child_material_hash TEXT NOT NULL, 
    created_by UUID NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
    CONSTRAINT pk_eipd_child_resolutions PRIMARY KEY (id), 
    CONSTRAINT fk_eipd_child_resolutions_assessment_id_legal_assessments FOREIGN KEY(assessment_id, treatment_id, organization_id) REFERENCES legal_assessments (id, treatment_id, organization_id) ON DELETE CASCADE, 
    CONSTRAINT uq_child_resolution_version UNIQUE (assessment_id, version), 
    CONSTRAINT uq_child_resolution_material UNIQUE (id, assessment_id, treatment_id, organization_id, document_hash, context_hash, child_material_hash), 
    CONSTRAINT ck_eipd_child_resolutions_version CHECK (version>=1), 
    CONSTRAINT ck_eipd_child_resolutions_document CHECK (jsonb_typeof(document)='object'), 
    CONSTRAINT ck_eipd_child_resolutions_context_identity CHECK ((jsonb_typeof(context_snapshot)='object' AND context_snapshot->>'context_schema_version'='4' AND context_snapshot->>'organization_id'=organization_id::text AND context_snapshot->>'treatment_id'=treatment_id::text AND context_snapshot->>'assessment_id'=assessment_id::text AND jsonb_typeof(context_snapshot->'child_adolescent_assessment')='object') IS TRUE), 
    CONSTRAINT ck_eipd_child_resolutions_data_kind CHECK (data_kind='ficticios'), 
    CONSTRAINT ck_eipd_child_resolutions_hashes CHECK (document_hash ~ '^[0-9a-f]{64}$' AND context_hash ~ '^[0-9a-f]{64}$' AND child_material_hash ~ '^[0-9a-f]{64}$'), 
    CONSTRAINT fk_eipd_child_resolutions_created_by_profiles FOREIGN KEY(created_by) REFERENCES profiles (id)
)

""",
    """
CREATE TABLE eipd_child_reviews (
    resolution_id UUID NOT NULL, 
    decision TEXT NOT NULL, 
    rationale TEXT NOT NULL, 
    review_reference TEXT NOT NULL, 
    policy_snapshot JSONB NOT NULL, 
    policy_hash TEXT NOT NULL, 
    review_context_metadata JSONB NOT NULL, 
    id UUID DEFAULT gen_random_uuid() NOT NULL, 
    organization_id UUID NOT NULL, 
    treatment_id UUID NOT NULL, 
    assessment_id UUID NOT NULL, 
    data_kind TEXT DEFAULT 'ficticios' NOT NULL, 
    document_hash TEXT NOT NULL, 
    context_hash TEXT NOT NULL, 
    child_material_hash TEXT NOT NULL, 
    created_by UUID NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
    CONSTRAINT pk_eipd_child_reviews PRIMARY KEY (id), 
    CONSTRAINT fk_eipd_child_reviews_resolution_id_eipd_child_resolutions FOREIGN KEY(resolution_id, assessment_id, treatment_id, organization_id, document_hash, context_hash, child_material_hash) REFERENCES eipd_child_resolutions (id, assessment_id, treatment_id, organization_id, document_hash, context_hash, child_material_hash) ON DELETE CASCADE, 
    CONSTRAINT ck_eipd_child_reviews_negative_decision CHECK (decision IN ('requiere_cambios','no_continuar')), 
    CONSTRAINT ck_eipd_child_reviews_human_review CHECK (btrim(rationale)<>'' AND btrim(review_reference)<>''), 
    CONSTRAINT ck_eipd_child_reviews_disabled_policy CHECK ((jsonb_typeof(policy_snapshot)='object'
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
AND policy_snapshot->'global_policy_identity'->>'policy_hash' ~ '^[0-9a-f]{64}$') IS TRUE), 
    CONSTRAINT ck_eipd_child_reviews_metadata_v3 CHECK ((jsonb_typeof(review_context_metadata)='object'
AND review_context_metadata ?& ARRAY['metadata_schema_version','resolution_binding_version','context_schema_version','child_coverage','document_hash','context_hash','child_material_hash','policy_hash']
AND review_context_metadata - ARRAY['metadata_schema_version','resolution_binding_version','context_schema_version','child_coverage','document_hash','context_hash','child_material_hash','policy_hash']='{}'::jsonb
AND jsonb_typeof(review_context_metadata->'metadata_schema_version')='number' AND review_context_metadata->>'metadata_schema_version'='3'
AND jsonb_typeof(review_context_metadata->'resolution_binding_version')='number' AND review_context_metadata->>'resolution_binding_version'='4'
AND jsonb_typeof(review_context_metadata->'context_schema_version')='number' AND review_context_metadata->>'context_schema_version'='4'
AND review_context_metadata->>'child_coverage'='contexto_v4'
AND review_context_metadata->>'document_hash'=document_hash
AND review_context_metadata->>'context_hash'=context_hash
AND review_context_metadata->>'child_material_hash'=child_material_hash
AND review_context_metadata->>'policy_hash'=policy_hash) IS TRUE), 
    CONSTRAINT ck_eipd_child_reviews_policy_hash CHECK (policy_hash ~ '^[0-9a-f]{64}$'), 
    CONSTRAINT ck_eipd_child_reviews_data_kind CHECK (data_kind='ficticios'), 
    CONSTRAINT ck_eipd_child_reviews_hashes CHECK (document_hash ~ '^[0-9a-f]{64}$' AND context_hash ~ '^[0-9a-f]{64}$' AND child_material_hash ~ '^[0-9a-f]{64}$'), 
    CONSTRAINT fk_eipd_child_reviews_created_by_profiles FOREIGN KEY(created_by) REFERENCES profiles (id)
)

""",
)


def upgrade():
    op.create_unique_constraint(
        "uq_assessment_child_parent",
        "legal_assessments",
        ["id", "treatment_id", "organization_id"],
    )
    for sql in DDL:
        op.execute(sa.text(sql))
    op.execute(
        """CREATE FUNCTION public.protect_eipd_child_history() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF TG_OP='UPDATE' OR current_user='app_user' THEN RAISE EXCEPTION 'Historial infancia inmutable'; END IF;
      RETURN OLD;
    END $$"""
    )
    for table in ("eipd_child_resolutions", "eipd_child_reviews"):
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY tenant_read ON {table} FOR SELECT TO app_user USING (organization_id IN (SELECT auth_org_ids()))"
        )
        op.execute(
            f"""CREATE POLICY tenant_insert ON {table} FOR INSERT TO app_user WITH CHECK (
            organization_id IN (SELECT auth_org_ids())
            AND created_by IN (SELECT id FROM profiles WHERE auth_user_id=auth.uid())
            AND (is_superadmin() OR EXISTS (SELECT 1 FROM memberships m JOIN profiles p ON p.id=m.profile_id WHERE m.organization_id={table}.organization_id AND p.auth_user_id=auth.uid() AND m.role IN ('owner','admin','editor')))
            AND EXISTS (SELECT 1 FROM subscriptions s WHERE s.organization_id={table}.organization_id AND s.status IN ('active','grace'))
            AND EXISTS (SELECT 1 FROM legal_assessments a WHERE a.id={table}.assessment_id AND a.organization_id={table}.organization_id AND a.treatment_id={table}.treatment_id AND a.status='borrador' AND a.child_adolescent_assessment IS NOT NULL)
        )"""
        )
        op.execute(f"REVOKE ALL ON {table} FROM PUBLIC")
        op.execute(f"REVOKE UPDATE,DELETE,TRUNCATE ON {table} FROM app_user")
        op.execute(f"GRANT SELECT,INSERT ON {table} TO app_user")
        op.execute(
            f"CREATE TRIGGER immutable_child_history BEFORE UPDATE OR DELETE ON {table} FOR EACH ROW EXECUTE FUNCTION public.protect_eipd_child_history()"
        )
        op.create_index(
            f"ix_{table}_history",
            table,
            ["organization_id", "assessment_id", "created_at", "id"],
        )


def downgrade():
    db = op.get_bind()
    if any(
        db.scalar(sa.text("SELECT count(*) FROM " + table))
        for table in ("eipd_child_reviews", "eipd_child_resolutions")
    ):
        raise RuntimeError(
            "Downgrade bloqueado: existen resoluciones o revisiones de infancia"
        )
    op.drop_table("eipd_child_reviews")
    op.drop_table("eipd_child_resolutions")
    op.execute("DROP FUNCTION public.protect_eipd_child_history()")
    op.drop_constraint(
        "uq_assessment_child_parent", "legal_assessments", type_="unique"
    )
