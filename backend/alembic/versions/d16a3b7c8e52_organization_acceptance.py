"""Facultad y aceptacion documental tenant; pruebas ficticias, RLS e historia RESTRICT."""

import sqlalchemy as sa

from alembic import op

revision = "d16a3b7c8e52"
down_revision = "c95f0a2b6d43"
branch_labels = None
depends_on = None
DDL = (
    "\nCREATE TABLE organization_acceptance_authorities (\n\trevision INTEGER NOT NULL, \n\taction TEXT NOT NULL, \n\torganization_role TEXT NOT NULL, \n\tresponsible_party_reference TEXT, \n\tfaculty_reference TEXT NOT NULL, \n\tevidence_reference TEXT NOT NULL, \n\tid UUID DEFAULT gen_random_uuid() NOT NULL, \n\torganization_id UUID NOT NULL, \n\ttreatment_id UUID NOT NULL, \n\tassessment_id UUID NOT NULL, \n\tactor_id UUID NOT NULL, \n\tcreated_by UUID NOT NULL, \n\tcreated_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, \n\tdata_kind TEXT NOT NULL, \n\tCONSTRAINT pk_organization_acceptance_authorities PRIMARY KEY (id), \n\tCONSTRAINT fk_organization_acceptance_authorities_assessment_id_le_a09e FOREIGN KEY(assessment_id, treatment_id, organization_id) REFERENCES legal_assessments (id, treatment_id, organization_id) ON DELETE RESTRICT, \n\tCONSTRAINT uq_org_authority_revision UNIQUE (assessment_id, actor_id, revision), \n\tCONSTRAINT uq_org_authority_identity UNIQUE (id, assessment_id, treatment_id, organization_id, actor_id), \n\tCONSTRAINT ck_organization_acceptance_authorities_data_kind CHECK (data_kind='ficticios'), \n\tCONSTRAINT ck_organization_acceptance_authorities_revision CHECK (revision>0), \n\tCONSTRAINT ck_organization_acceptance_authorities_action CHECK (action IN ('otorgar','revocar')), \n\tCONSTRAINT ck_organization_acceptance_authorities_organization_role CHECK (organization_role IN ('responsable','encargado')), \n\tCONSTRAINT ck_organization_acceptance_authorities_responsible_party CHECK (organization_role='responsable' OR (responsible_party_reference IS NOT NULL AND btrim(responsible_party_reference)<>'')), \n\tCONSTRAINT ck_organization_acceptance_authorities_evidence CHECK (btrim(faculty_reference)<>'' AND btrim(evidence_reference)<>''), \n\tCONSTRAINT fk_organization_acceptance_authorities_actor_id_profiles FOREIGN KEY(actor_id) REFERENCES profiles (id) ON DELETE RESTRICT, \n\tCONSTRAINT fk_organization_acceptance_authorities_created_by_profiles FOREIGN KEY(created_by) REFERENCES profiles (id) ON DELETE RESTRICT\n)\n\n",
    "\nCREATE TABLE organization_document_acceptances (\n\tauthority_id UUID NOT NULL, \n\tresolution_id UUID NOT NULL, \n\tdecision TEXT NOT NULL, \n\trationale TEXT NOT NULL, \n\tevidence_reference TEXT NOT NULL, \n\tdocument_hash TEXT NOT NULL, \n\tcontext_hash TEXT NOT NULL, \n\tchild_material_hash TEXT NOT NULL, \n\tid UUID DEFAULT gen_random_uuid() NOT NULL, \n\torganization_id UUID NOT NULL, \n\ttreatment_id UUID NOT NULL, \n\tassessment_id UUID NOT NULL, \n\tactor_id UUID NOT NULL, \n\tcreated_by UUID NOT NULL, \n\tcreated_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, \n\tdata_kind TEXT NOT NULL, \n\tCONSTRAINT pk_organization_document_acceptances PRIMARY KEY (id), \n\tCONSTRAINT fk_organization_document_acceptances_authority_id_organ_a601 FOREIGN KEY(authority_id, assessment_id, treatment_id, organization_id, actor_id) REFERENCES organization_acceptance_authorities (id, assessment_id, treatment_id, organization_id, actor_id) ON DELETE RESTRICT, \n\tCONSTRAINT fk_organization_document_acceptances_resolution_id_eipd_3bec FOREIGN KEY(resolution_id, assessment_id, treatment_id, organization_id, document_hash, context_hash, child_material_hash) REFERENCES eipd_child_resolutions (id, assessment_id, treatment_id, organization_id, document_hash, context_hash, child_material_hash) ON DELETE RESTRICT, \n\tCONSTRAINT ck_organization_document_acceptances_data_kind CHECK (data_kind='ficticios'), \n\tCONSTRAINT ck_organization_document_acceptances_decision CHECK (decision IN ('acepta','rechaza','requiere_cambios')), \n\tCONSTRAINT ck_organization_document_acceptances_actor_identity CHECK (created_by=actor_id), \n\tCONSTRAINT ck_organization_document_acceptances_hashes CHECK (document_hash ~ '^[0-9a-f]{64}$' AND context_hash ~ '^[0-9a-f]{64}$' AND child_material_hash ~ '^[0-9a-f]{64}$'), \n\tCONSTRAINT ck_organization_document_acceptances_evidence CHECK (btrim(rationale)<>'' AND btrim(evidence_reference)<>''), \n\tCONSTRAINT fk_organization_document_acceptances_actor_id_profiles FOREIGN KEY(actor_id) REFERENCES profiles (id) ON DELETE RESTRICT, \n\tCONSTRAINT fk_organization_document_acceptances_created_by_profiles FOREIGN KEY(created_by) REFERENCES profiles (id) ON DELETE RESTRICT\n)\n\n",
)
TABLES = ("organization_acceptance_authorities", "organization_document_acceptances")


def upgrade():
    for sql in DDL:
        op.execute(sa.text(sql))
    for table in TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"REVOKE ALL ON {table} FROM PUBLIC")
        op.execute(f"GRANT SELECT,INSERT ON {table} TO app_user")
        op.execute(f"REVOKE UPDATE,DELETE,TRUNCATE ON {table} FROM app_user")
        op.execute(
            f"CREATE POLICY tenant_read ON {table} FOR SELECT TO app_user USING (organization_id IN (SELECT auth_org_ids()))"
        )
        common = f"""organization_id IN (SELECT auth_org_ids())
  AND created_by IN (SELECT id FROM profiles WHERE auth_user_id=auth.uid())
  AND EXISTS (SELECT 1 FROM subscriptions s WHERE s.organization_id={table}.organization_id AND s.status IN ('active','grace'))"""
        if table == TABLES[0]:
            check = f"""{common}
   AND EXISTS (SELECT 1 FROM memberships m WHERE m.organization_id={table}.organization_id AND m.profile_id={table}.created_by AND m.role IN ('owner','admin'))
   AND (action='revocar' OR EXISTS (SELECT 1 FROM memberships m WHERE m.organization_id={table}.organization_id AND m.profile_id={table}.actor_id AND m.role IN ('owner','admin','editor')))"""
        else:
            check = f"""{common} AND actor_id=created_by
   AND EXISTS (SELECT 1 FROM memberships m WHERE m.organization_id={table}.organization_id AND m.profile_id={table}.actor_id AND m.role IN ('owner','admin','editor'))
   AND EXISTS (SELECT 1 FROM organization_acceptance_authorities g WHERE g.id={table}.authority_id AND g.organization_id={table}.organization_id AND g.actor_id={table}.actor_id AND g.assessment_id={table}.assessment_id AND g.action='otorgar'
   AND NOT EXISTS (SELECT 1 FROM organization_acceptance_authorities newer WHERE newer.organization_id=g.organization_id AND newer.assessment_id=g.assessment_id AND newer.actor_id=g.actor_id AND newer.revision>g.revision))
   AND EXISTS (SELECT 1 FROM legal_assessments a WHERE a.id={table}.assessment_id AND a.organization_id={table}.organization_id AND a.status='borrador')"""
        op.execute(
            f"CREATE POLICY tenant_insert ON {table} FOR INSERT TO app_user WITH CHECK ({check})"
        )
        op.execute(
            f"CREATE TRIGGER immutable_organization_history BEFORE UPDATE OR DELETE ON {table} FOR EACH ROW EXECUTE FUNCTION public.protect_eipd_child_history()"
        )
        op.create_index(
            f"ix_{table}_history",
            table,
            ["organization_id", "assessment_id", "created_at", "id"],
        )


def downgrade():
    if any(
        op.get_bind().scalar(sa.text("SELECT count(*) FROM " + table))
        for table in TABLES
    ):
        raise RuntimeError("Downgrade bloqueado: historial de aceptacion no vacio")
    for table in reversed(TABLES):
        op.drop_table(table)
