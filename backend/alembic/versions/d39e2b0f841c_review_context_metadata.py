"""Add nullable review context identity without backfill or event activation."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "d39e2b0f841c"
down_revision = "c28f1a9d730b"
branch_labels = None
depends_on = None

CHECK = "review_context_metadata IS NULL OR (\njsonb_typeof(review_context_metadata) = 'object'\nAND review_context_metadata ?& ARRAY['metadata_schema_version','resolution_binding_version','context_schema_version','research_coverage','document_hash','context_hash','research_material_hash']\nAND review_context_metadata - ARRAY['metadata_schema_version','resolution_binding_version','context_schema_version','research_coverage','document_hash','context_hash','research_material_hash'] = '{}'::jsonb\nAND jsonb_typeof(review_context_metadata->'metadata_schema_version') = 'number'\nAND review_context_metadata->>'metadata_schema_version' = '1'\nAND jsonb_typeof(review_context_metadata->'resolution_binding_version') = 'number'\nAND review_context_metadata->>'resolution_binding_version' IN ('1','2')\nAND jsonb_typeof(review_context_metadata->'context_schema_version') = 'number'\nAND review_context_metadata->>'context_schema_version' = review_context_metadata->>'resolution_binding_version'\nAND jsonb_typeof(review_context_metadata->'research_coverage') = 'string'\nAND review_context_metadata->>'research_coverage' = CASE WHEN review_context_metadata->>'context_schema_version' = '2' THEN 'contexto_v2' ELSE 'no_cubierta' END\nAND jsonb_typeof(review_context_metadata->'document_hash') = 'string'\nAND review_context_metadata->>'document_hash' = document_hash\nAND jsonb_typeof(review_context_metadata->'context_hash') = 'string'\nAND review_context_metadata->>'context_hash' = context_hash\nAND (review_context_metadata->'research_material_hash' = 'null'::jsonb OR\n    (review_context_metadata->>'context_schema_version' = '2'\n     AND jsonb_typeof(review_context_metadata->'research_material_hash') = 'string'\n     AND review_context_metadata->>'research_material_hash' ~ '^[0-9a-f]{64}$'))\n) IS TRUE"


def upgrade():
    op.add_column(
        "eipd_resolution_reviews",
        sa.Column("review_context_metadata", postgresql.JSONB(), nullable=True),
    )
    op.create_check_constraint(
        "ck_eipd_reviews_context_metadata", "eipd_resolution_reviews", CHECK
    )


def downgrade():
    op.drop_constraint(
        "ck_eipd_reviews_context_metadata", "eipd_resolution_reviews", type_="check"
    )
    op.drop_column("eipd_resolution_reviews", "review_context_metadata")
