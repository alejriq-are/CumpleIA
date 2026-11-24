"""Persist independent review faculties and conclusions for Base y fundamento."""

from alembic import op

revision = "d51ba5e1a702"
down_revision = "bf5d10a26c41"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """CREATE TABLE base_fundamento_review_authorities (
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
        """CREATE TABLE base_fundamento_reviews (
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
        outcome text NOT NULL CHECK (outcome IN ('favorable', 'requiere_cambios', 'desfavorable')),
        reason text NOT NULL CHECK (length(btrim(reason)) > 0),
        reference text NOT NULL CHECK (length(btrim(reference)) > 0),
        resolutions jsonb NOT NULL CHECK (jsonb_typeof(resolutions) = 'array'),
        observations jsonb NOT NULL CHECK (jsonb_typeof(observations) = 'array'),
        UNIQUE (version_id, sequence),
        UNIQUE (id, version_id, sequence),
        UNIQUE (organization_id, created_by, request_id),
        CHECK ((sequence = 1) = (previous_id IS NULL)),
        FOREIGN KEY (authority_id, assessment_id, created_by, organization_id)
            REFERENCES base_fundamento_review_authorities(id, assessment_id, subject_id, organization_id),
        FOREIGN KEY (previous_id, version_id, previous_sequence)
            REFERENCES base_fundamento_reviews(id, version_id, sequence),
        FOREIGN KEY (version_id, assessment_id, treatment_id, organization_id)
            REFERENCES base_fundamento_versions(id, assessment_id, treatment_id, organization_id)
    )"""
    )

    # Runtime writes remain tenant/actor constrained, with a common DB-side
    # series lock as a second barrier even for direct SQL using app_user.
    op.execute(
        """CREATE FUNCTION validate_base_fundamento_review() RETURNS trigger
        LANGUAGE plpgsql SET search_path = public, pg_temp AS $$
        DECLARE latest_faculty base_fundamento_review_authorities%ROWTYPE;
                document base_fundamento_versions%ROWTYPE;
                previous_review base_fundamento_reviews%ROWTYPE;
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
          IF TG_TABLE_NAME='base_fundamento_review_authorities' THEN
            IF NOT EXISTS (SELECT 1 FROM memberships m WHERE m.organization_id=NEW.organization_id
                AND m.profile_id=NEW.created_by AND m.role IN ('owner','admin')) OR
               NOT EXISTS (SELECT 1 FROM memberships m WHERE m.organization_id=NEW.organization_id
                AND m.profile_id=NEW.subject_id AND m.role IN ('owner','admin','editor')) THEN
              RAISE EXCEPTION 'Administracion y destinatario habilitados requeridos';
            END IF;
            SELECT coalesce(max(sequence),0) INTO last_sequence FROM base_fundamento_review_authorities
              WHERE organization_id=NEW.organization_id AND assessment_id=NEW.assessment_id
                AND subject_id=NEW.subject_id;
            IF NEW.sequence<>last_sequence+1 THEN RAISE EXCEPTION 'Secuencia de facultad obsoleta'; END IF;
          ELSE
            SELECT * INTO document FROM base_fundamento_versions WHERE id=NEW.version_id
              AND organization_id=NEW.organization_id AND treatment_id=NEW.treatment_id
              AND assessment_id=NEW.assessment_id;
            IF NOT FOUND OR document.created_by=NEW.created_by THEN
              RAISE EXCEPTION 'Version no disponible o autorrevision';
            END IF;
            SELECT * INTO latest_faculty FROM base_fundamento_review_authorities
              WHERE organization_id=NEW.organization_id AND assessment_id=NEW.assessment_id
                AND subject_id=NEW.created_by ORDER BY sequence DESC LIMIT 1;
            IF latest_faculty.id IS NULL OR latest_faculty.id<>NEW.authority_id OR
               latest_faculty.action<>'grant' OR
               (latest_faculty.expires_at IS NOT NULL AND latest_faculty.expires_at<=clock_timestamp()) THEN
              RAISE EXCEPTION 'Facultad expresa vigente requerida';
            END IF;
            SELECT * INTO previous_review FROM base_fundamento_reviews
              WHERE version_id=NEW.version_id ORDER BY sequence DESC LIMIT 1;
            IF NEW.sequence<>coalesce(previous_review.sequence,0)+1 OR
               NEW.previous_id IS DISTINCT FROM previous_review.id THEN
              RAISE EXCEPTION 'Revision previa obsoleta';
            END IF;
            IF NEW.outcome='favorable' AND (
              document.bundle#>>'{diagnostic,rule_set}' IS DISTINCT FROM 'cumpleia.base_fundamento.v1'
              OR document.bundle#>>'{diagnostic,legal_basis}' IS NULL
              OR jsonb_typeof(document.bundle#>'{diagnostic,findings}') IS DISTINCT FROM 'array'
              OR jsonb_typeof(document.bundle#>'{diagnostic,applicability}') IS DISTINCT FROM 'array'
              OR EXISTS (
                SELECT 1 FROM jsonb_array_elements(document.bundle#>'{diagnostic,findings}') AS f
                WHERE NOT coalesce(
                  f->>'criterion_id'='base.respaldo'
                  AND f->>'code' IN ('evidencia_ausente','evidencia_incompleta',
                    'tipo_evidencia_vacio','referencia_de_respaldo_ausente')
                  AND EXISTS (
                    SELECT 1 FROM jsonb_array_elements(NEW.resolutions) AS r
                    WHERE r->>'field'=f->>'field' AND r->>'code'=f->>'code'
                      AND r->>'criterion_id'=f->>'criterion_id'
                      AND r->>'resolution'='respaldo_equivalente'
                      AND length(btrim(r->>'justification'))>0
                      AND length(btrim(r->>'reference'))>0
                  ), false)
              )
              OR EXISTS (
                SELECT 1 FROM jsonb_array_elements(document.bundle#>'{diagnostic,applicability}') AS a
                WHERE NOT coalesce(
                  a->>'criterion_id' IS NOT NULL AND (
                    a->>'applicability'='aplicable'
                    OR (a->>'applicability'='no_aplicable' AND EXISTS (
                      SELECT 1 FROM jsonb_array_elements(NEW.resolutions) AS r
                      WHERE r->>'field'=a->>'field' AND r->>'criterion_id'=a->>'criterion_id'
                        AND r->>'code'='aplicabilidad'
                        AND r->>'resolution'='no_aplica'
                        AND length(btrim(r->>'justification'))>0
                    ))
                  ), false)
              )
            ) THEN
              RAISE EXCEPTION 'Requisitos esenciales de la version sin resolver';
            END IF;
          END IF;
          NEW.created_at := clock_timestamp();
          RETURN NEW;
        END $$"""
    )
    for table in ("base_fundamento_review_authorities", "base_fundamento_reviews"):
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
            f"""CREATE TRIGGER validate_base_fundamento_review BEFORE INSERT ON {table}
            FOR EACH ROW EXECUTE FUNCTION validate_base_fundamento_review()"""
        )
        op.execute(
            f"""CREATE POLICY tenant_read ON {table} FOR SELECT TO app_user
            USING (organization_id IN (SELECT auth_org_ids()))"""
        )
        op.execute(
            f"""CREATE TRIGGER immutable_base_fundamento_review BEFORE UPDATE OR DELETE ON {table}
            FOR EACH ROW EXECUTE FUNCTION protect_general_eipd_version()"""
        )


def downgrade():
    raise RuntimeError("Historial protegido: no se elimina automáticamente")
