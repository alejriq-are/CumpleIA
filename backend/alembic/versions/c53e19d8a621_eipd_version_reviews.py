"""Persist immutable review authority and reviews for registered EIPD versions."""

from alembic import op

revision = "c53e19d8a621"
down_revision = "b95e7f3d1204"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """ALTER TABLE eipd_document_versions ADD CONSTRAINT uq_eipd_version_scope
        UNIQUE (id, assessment_id, treatment_id, organization_id)"""
    )
    op.execute(
        """CREATE TABLE eipd_review_authority_events (
        id uuid PRIMARY KEY,
        organization_id uuid NOT NULL,
        treatment_id uuid NOT NULL,
        assessment_id uuid NOT NULL,
        subject_id uuid NOT NULL REFERENCES profiles(id),
        created_by uuid NOT NULL REFERENCES profiles(id),
        created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
        sequence integer NOT NULL CHECK (sequence > 0),
        action text NOT NULL CHECK (action IN ('grant', 'revoke')),
        expires_at timestamptz,
        reason text NOT NULL CHECK (length(btrim(reason)) > 0),
        reference text NOT NULL CHECK (length(btrim(reference)) > 0),
        CHECK (action <> 'grant' OR subject_id <> created_by),
        CHECK (expires_at IS NULL OR (action = 'grant' AND expires_at > created_at)),
        UNIQUE (assessment_id, subject_id, sequence),
        UNIQUE (id, assessment_id, subject_id, organization_id),
        FOREIGN KEY (assessment_id, treatment_id, organization_id)
            REFERENCES legal_assessments(id, treatment_id, organization_id)
    )"""
    )
    op.execute(
        """CREATE TABLE eipd_version_reviews (
        id uuid PRIMARY KEY,
        organization_id uuid NOT NULL,
        treatment_id uuid NOT NULL,
        assessment_id uuid NOT NULL,
        version_id uuid NOT NULL,
        created_by uuid NOT NULL REFERENCES profiles(id),
        created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
        sequence integer NOT NULL CHECK (sequence > 0),
        previous_id uuid,
        previous_sequence integer GENERATED ALWAYS AS (sequence - 1) STORED,
        request_id uuid NOT NULL,
        authority_id uuid NOT NULL,
        input_hash text NOT NULL CHECK (input_hash ~ '^[0-9a-f]{64}$'),
        outcome text NOT NULL CHECK (outcome IN ('favorable', 'requiere_cambios', 'no_continuar')),
        reason text NOT NULL CHECK (length(btrim(reason)) > 0),
        reference text NOT NULL CHECK (length(btrim(reference)) > 0),
        UNIQUE (version_id, sequence),
        UNIQUE (id, version_id, sequence),
        UNIQUE (organization_id, created_by, request_id),
        CHECK ((sequence = 1) = (previous_id IS NULL)),
        FOREIGN KEY (authority_id, assessment_id, created_by, organization_id)
            REFERENCES eipd_review_authority_events(id, assessment_id, subject_id, organization_id),
        FOREIGN KEY (previous_id, version_id, previous_sequence)
            REFERENCES eipd_version_reviews(id, version_id, sequence),
        FOREIGN KEY (version_id, assessment_id, treatment_id, organization_id)
            REFERENCES eipd_document_versions(id, assessment_id, treatment_id, organization_id)
    )"""
    )

    # Runtime writes remain tenant/actor constrained, with a common DB-side
    # series lock as a second barrier even for direct SQL using app_user.
    op.execute(
        """CREATE FUNCTION validate_general_eipd_review() RETURNS trigger
        LANGUAGE plpgsql SET search_path = public, pg_temp AS $$
        DECLARE latest_faculty eipd_review_authority_events%ROWTYPE;
                document eipd_document_versions%ROWTYPE;
                previous_review eipd_version_reviews%ROWTYPE;
                last_sequence integer;
        BEGIN
          PERFORM 1 FROM legal_assessment_series s
            JOIN legal_assessments a ON a.series_id=s.id
            WHERE a.id=NEW.assessment_id AND a.organization_id=NEW.organization_id
              AND a.treatment_id=NEW.treatment_id FOR UPDATE OF s;
          IF NOT FOUND THEN RAISE EXCEPTION 'Expediente no disponible'; END IF;
          IF NOT EXISTS (SELECT 1 FROM memberships m WHERE m.organization_id=NEW.organization_id
              AND m.profile_id=NEW.created_by AND m.role IN ('owner','admin','editor')) THEN
            RAISE EXCEPTION 'Membresia habilitada requerida';
          END IF;
          IF TG_TABLE_NAME='eipd_review_authority_events' THEN
            IF NOT EXISTS (SELECT 1 FROM memberships m WHERE m.organization_id=NEW.organization_id
                AND m.profile_id=NEW.created_by AND m.role IN ('owner','admin')) OR
               NOT EXISTS (SELECT 1 FROM memberships m WHERE m.organization_id=NEW.organization_id
                AND m.profile_id=NEW.subject_id AND m.role IN ('owner','admin','editor')) THEN
              RAISE EXCEPTION 'Administracion y destinatario habilitados requeridos';
            END IF;
            SELECT coalesce(max(sequence),0) INTO last_sequence FROM eipd_review_authority_events
              WHERE organization_id=NEW.organization_id AND assessment_id=NEW.assessment_id
                AND subject_id=NEW.subject_id;
            IF NEW.sequence<>last_sequence+1 THEN RAISE EXCEPTION 'Secuencia de facultad obsoleta'; END IF;
          ELSE
            SELECT * INTO document FROM eipd_document_versions WHERE id=NEW.version_id
              AND organization_id=NEW.organization_id AND treatment_id=NEW.treatment_id
              AND assessment_id=NEW.assessment_id;
            IF NOT FOUND OR document.created_by=NEW.created_by THEN
              RAISE EXCEPTION 'Version no disponible o autorrevision';
            END IF;
            SELECT * INTO latest_faculty FROM eipd_review_authority_events
              WHERE organization_id=NEW.organization_id AND assessment_id=NEW.assessment_id
                AND subject_id=NEW.created_by ORDER BY sequence DESC LIMIT 1;
            IF latest_faculty.id IS NULL OR latest_faculty.id<>NEW.authority_id OR
               latest_faculty.action<>'grant' OR
               (latest_faculty.expires_at IS NOT NULL AND latest_faculty.expires_at<=clock_timestamp()) THEN
              RAISE EXCEPTION 'Facultad expresa vigente requerida';
            END IF;
            SELECT * INTO previous_review FROM eipd_version_reviews
              WHERE version_id=NEW.version_id ORDER BY sequence DESC LIMIT 1;
            IF NEW.sequence<>coalesce(previous_review.sequence,0)+1 OR
               NEW.previous_id IS DISTINCT FROM previous_review.id THEN
              RAISE EXCEPTION 'Revision previa obsoleta';
            END IF;
            IF NEW.outcome='favorable' AND NOT coalesce(
              document.bundle#>>'{diagnostic,rule_set}'='cumpleia.general.registration.v1'
              AND document.bundle#>>'{diagnostic,readiness,eipd_resolution,result}'='completo'
              AND document.bundle#>>'{diagnostic,readiness,eipd_resolution,context_current}'='true'
              AND document.bundle#>'{diagnostic,readiness,eipd_resolution,issues}'='[]'::jsonb,
              false) THEN
              RAISE EXCEPTION 'Version documental incompleta';
            END IF;
          END IF;
          NEW.created_at := clock_timestamp();
          RETURN NEW;
        END $$"""
    )
    for table in ("eipd_review_authority_events", "eipd_version_reviews"):
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"REVOKE ALL ON {table} FROM PUBLIC, app_user")
        op.execute(f"GRANT SELECT, INSERT ON {table} TO app_user")
        op.execute(
            f"""CREATE POLICY tenant_write ON {table} FOR INSERT TO app_user
            WITH CHECK (
              organization_id IN (SELECT auth_org_ids())
              AND created_by IN (SELECT id FROM profiles WHERE auth_user_id=auth.uid())
              AND EXISTS (SELECT 1 FROM subscriptions s
                WHERE s.organization_id={table}.organization_id AND s.status IN ('active','grace'))
            )"""
        )
        op.execute(
            f"""CREATE TRIGGER validate_eipd_review BEFORE INSERT ON {table}
            FOR EACH ROW EXECUTE FUNCTION validate_general_eipd_review()"""
        )
        op.execute(
            f"""CREATE POLICY tenant_read ON {table} FOR SELECT TO app_user
            USING (organization_id IN (SELECT auth_org_ids()))"""
        )
        op.execute(
            f"""CREATE TRIGGER immutable_eipd_review BEFORE UPDATE OR DELETE ON {table}
            FOR EACH ROW EXECUTE FUNCTION protect_general_eipd_version()"""
        )


def downgrade():
    raise RuntimeError("Historial protegido: no se elimina automáticamente")
