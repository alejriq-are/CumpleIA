"""Allow successor review metadata without rewriting historical events."""

import sqlalchemy as sa

from alembic import op

revision = "f52d6c9b3e10"
down_revision = "e41c5b8a2d90"
branch_labels = None
depends_on = None

OLD_CHECK = "review_context_metadata IS NULL OR (\njsonb_typeof(review_context_metadata) = 'object'\nAND review_context_metadata ?& ARRAY['metadata_schema_version','resolution_binding_version','context_schema_version','research_coverage','document_hash','context_hash','research_material_hash']\nAND review_context_metadata - ARRAY['metadata_schema_version','resolution_binding_version','context_schema_version','research_coverage','document_hash','context_hash','research_material_hash'] = '{}'::jsonb\nAND jsonb_typeof(review_context_metadata->'metadata_schema_version') = 'number'\nAND review_context_metadata->>'metadata_schema_version' = '1'\nAND jsonb_typeof(review_context_metadata->'resolution_binding_version') = 'number'\nAND review_context_metadata->>'resolution_binding_version' IN ('1','2')\nAND jsonb_typeof(review_context_metadata->'context_schema_version') = 'number'\nAND review_context_metadata->>'context_schema_version' = review_context_metadata->>'resolution_binding_version'\nAND jsonb_typeof(review_context_metadata->'research_coverage') = 'string'\nAND review_context_metadata->>'research_coverage' = CASE WHEN review_context_metadata->>'context_schema_version' = '2' THEN 'contexto_v2' ELSE 'no_cubierta' END\nAND jsonb_typeof(review_context_metadata->'document_hash') = 'string'\nAND review_context_metadata->>'document_hash' = document_hash\nAND jsonb_typeof(review_context_metadata->'context_hash') = 'string'\nAND review_context_metadata->>'context_hash' = context_hash\nAND (review_context_metadata->'research_material_hash' = 'null'::jsonb OR\n    (review_context_metadata->>'context_schema_version' = '2'\n     AND jsonb_typeof(review_context_metadata->'research_material_hash') = 'string'\n     AND review_context_metadata->>'research_material_hash' ~ '^[0-9a-f]{64}$'))\n) IS TRUE"
CHECK = "(review_context_metadata IS NULL OR (\njsonb_typeof(review_context_metadata) = 'object'\nAND review_context_metadata ?& ARRAY['metadata_schema_version','resolution_binding_version','context_schema_version','research_coverage','document_hash','context_hash','research_material_hash']\nAND review_context_metadata - ARRAY['metadata_schema_version','resolution_binding_version','context_schema_version','research_coverage','document_hash','context_hash','research_material_hash'] = '{}'::jsonb\nAND jsonb_typeof(review_context_metadata->'metadata_schema_version') = 'number'\nAND review_context_metadata->>'metadata_schema_version' = '1'\nAND jsonb_typeof(review_context_metadata->'resolution_binding_version') = 'number'\nAND review_context_metadata->>'resolution_binding_version' IN ('1','2')\nAND jsonb_typeof(review_context_metadata->'context_schema_version') = 'number'\nAND review_context_metadata->>'context_schema_version' = review_context_metadata->>'resolution_binding_version'\nAND jsonb_typeof(review_context_metadata->'research_coverage') = 'string'\nAND review_context_metadata->>'research_coverage' = CASE WHEN review_context_metadata->>'context_schema_version' = '2' THEN 'contexto_v2' ELSE 'no_cubierta' END\nAND jsonb_typeof(review_context_metadata->'document_hash') = 'string'\nAND review_context_metadata->>'document_hash' = document_hash\nAND jsonb_typeof(review_context_metadata->'context_hash') = 'string'\nAND review_context_metadata->>'context_hash' = context_hash\nAND (review_context_metadata->'research_material_hash' = 'null'::jsonb OR\n    (review_context_metadata->>'context_schema_version' = '2'\n     AND jsonb_typeof(review_context_metadata->'research_material_hash') = 'string'\n     AND review_context_metadata->>'research_material_hash' ~ '^[0-9a-f]{64}$'))\n) IS TRUE) OR ((jsonb_typeof(review_context_metadata) = 'object'\nAND review_context_metadata ?& ARRAY['metadata_schema_version','resolution_binding_version','context_schema_version','research_coverage','representation_coverage','document_hash','context_hash','research_material_hash','representation_material_hash']\nAND review_context_metadata - ARRAY['metadata_schema_version','resolution_binding_version','context_schema_version','research_coverage','representation_coverage','document_hash','context_hash','research_material_hash','representation_material_hash'] = '{}'::jsonb\nAND jsonb_typeof(review_context_metadata->'metadata_schema_version') = 'number'\nAND review_context_metadata->>'metadata_schema_version' = '2'\nAND jsonb_typeof(review_context_metadata->'resolution_binding_version') = 'number'\nAND review_context_metadata->>'resolution_binding_version' = '3'\nAND jsonb_typeof(review_context_metadata->'context_schema_version') = 'number'\nAND review_context_metadata->>'context_schema_version' = '3'\nAND jsonb_typeof(review_context_metadata->'research_coverage') = 'string'\nAND review_context_metadata->>'research_coverage' = 'contexto_v3'\nAND jsonb_typeof(review_context_metadata->'representation_coverage') = 'string'\nAND review_context_metadata->>'representation_coverage' = 'contexto_v3'\nAND jsonb_typeof(review_context_metadata->'document_hash') = 'string'\nAND review_context_metadata->>'document_hash' = document_hash\nAND jsonb_typeof(review_context_metadata->'context_hash') = 'string'\nAND review_context_metadata->>'context_hash' = context_hash\nAND (review_context_metadata->'research_material_hash' = 'null'::jsonb OR (jsonb_typeof(review_context_metadata->'research_material_hash') = 'string' AND review_context_metadata->>'research_material_hash' ~ '^[0-9a-f]{64}$'))\nAND (review_context_metadata->'representation_material_hash' = 'null'::jsonb OR (jsonb_typeof(review_context_metadata->'representation_material_hash') = 'string' AND review_context_metadata->>'representation_material_hash' ~ '^[0-9a-f]{64}$'))) IS TRUE)"


def upgrade():
    op.drop_constraint(
        op.f("ck_eipd_resolution_reviews_ck_eipd_reviews_context_metadata"),
        "eipd_resolution_reviews",
        type_="check",
    )
    op.create_check_constraint(
        "ck_eipd_reviews_context_metadata", "eipd_resolution_reviews", CHECK
    )


def downgrade():
    # No destruir eventos V2 para restaurar un contrato antiguo.
    connection = op.get_bind()
    if connection.scalar(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM eipd_resolution_reviews WHERE review_context_metadata->>'metadata_schema_version' = '2')"
        )
    ):
        raise RuntimeError(
            "Downgrade requiere ausencia de eventos metadata V2; no se borran ni convierten"
        )
    op.drop_constraint(
        op.f("ck_eipd_resolution_reviews_ck_eipd_reviews_context_metadata"),
        "eipd_resolution_reviews",
        type_="check",
    )
    op.create_check_constraint(
        "ck_eipd_reviews_context_metadata", "eipd_resolution_reviews", OLD_CHECK
    )
