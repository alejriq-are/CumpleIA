"""Immutable general EIPD versions with tenant-scoped registration."""

from alembic import op

revision = "b95e7f3d1204"
down_revision = "a84f6e2c9103"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """CREATE TABLE eipd_document_versions (
        id uuid PRIMARY KEY, organization_id uuid NOT NULL, treatment_id uuid NOT NULL,
        assessment_id uuid NOT NULL, created_by uuid NOT NULL REFERENCES profiles(id) ON DELETE RESTRICT,
        created_at timestamptz NOT NULL DEFAULT clock_timestamp(), request_id uuid NOT NULL,
        version integer NOT NULL, data_kind text NOT NULL, reason text NOT NULL,
        source_hash text NOT NULL, input_hash text NOT NULL, bundle_hash text NOT NULL, bundle jsonb NOT NULL,
        CONSTRAINT fk_eipd_version_parent FOREIGN KEY (assessment_id,treatment_id,organization_id)
          REFERENCES legal_assessments(id,treatment_id,organization_id) ON DELETE RESTRICT,
        CONSTRAINT uq_eipd_document_number UNIQUE(assessment_id,version),
        CONSTRAINT uq_eipd_document_request UNIQUE(organization_id,created_by,request_id),
        CONSTRAINT eipd_version_fictitious CHECK(version>0 AND data_kind='ficticios'),
        CONSTRAINT eipd_version_reason CHECK(length(btrim(reason))>0),
        CONSTRAINT eipd_version_hashes CHECK(source_hash ~ '^[0-9a-f]{64}$' AND input_hash ~ '^[0-9a-f]{64}$' AND bundle_hash ~ '^[0-9a-f]{64}$')
    )"""
    )
    op.execute(
        "CREATE INDEX ix_eipd_version_tenant ON eipd_document_versions(organization_id,treatment_id,assessment_id)"
    )
    op.execute("ALTER TABLE eipd_document_versions ENABLE ROW LEVEL SECURITY")
    op.execute("REVOKE ALL ON eipd_document_versions FROM PUBLIC")
    op.execute("GRANT SELECT, INSERT ON eipd_document_versions TO app_user")
    op.execute(
        "REVOKE UPDATE, DELETE, TRUNCATE ON eipd_document_versions FROM app_user"
    )
    op.execute(
        "CREATE POLICY tenant_read ON eipd_document_versions FOR SELECT TO app_user USING (organization_id IN (SELECT auth_org_ids()))"
    )
    op.execute(
        """CREATE POLICY tenant_register ON eipd_document_versions FOR INSERT TO app_user WITH CHECK (
        organization_id IN (SELECT auth_org_ids())
        AND created_by IN (SELECT id FROM profiles WHERE auth_user_id=auth.uid())
        AND EXISTS (SELECT 1 FROM memberships m WHERE m.organization_id=eipd_document_versions.organization_id AND m.profile_id=eipd_document_versions.created_by AND m.role IN ('owner','admin','editor'))
        AND EXISTS (SELECT 1 FROM subscriptions s WHERE s.organization_id=eipd_document_versions.organization_id AND s.status IN ('active','grace'))
        AND EXISTS (SELECT 1 FROM legal_assessments a WHERE a.id=eipd_document_versions.assessment_id AND a.organization_id=eipd_document_versions.organization_id AND a.treatment_id=eipd_document_versions.treatment_id AND a.status='borrador'))"""
    )
    op.execute(
        """CREATE FUNCTION protect_general_eipd_version() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF TG_OP='UPDATE' OR current_user='app_user' THEN
        RAISE EXCEPTION 'Registered general EIPD history is immutable';
      END IF;
      RETURN OLD;
    END $$"""
    )
    op.execute(
        "CREATE TRIGGER immutable_general_eipd BEFORE UPDATE OR DELETE ON eipd_document_versions FOR EACH ROW EXECUTE FUNCTION protect_general_eipd_version()"
    )


def downgrade():
    raise RuntimeError("Historial protegido: no se elimina automáticamente")
