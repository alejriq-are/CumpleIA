"""Evita borrar historial de infancia al eliminar sus padres."""

import sqlalchemy as sa

from alembic import op

revision = "c95f0a2b6d43"
down_revision = "b84e9f1a5c32"
branch_labels = None
depends_on = None
RELATIONS = (
    (
        "fk_eipd_child_resolutions_assessment_id_legal_assessments",
        "eipd_child_resolutions",
        "legal_assessments",
        ["assessment_id", "treatment_id", "organization_id"],
        ["id", "treatment_id", "organization_id"],
    ),
    (
        "fk_eipd_child_reviews_resolution_id_eipd_child_resolutions",
        "eipd_child_reviews",
        "eipd_child_resolutions",
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
            "id",
            "assessment_id",
            "treatment_id",
            "organization_id",
            "document_hash",
            "context_hash",
            "child_material_hash",
        ],
    ),
)


def replace_relations(action):
    for name, table, parent, local, remote in RELATIONS:
        op.drop_constraint(op.f(name), table, type_="foreignkey")
        op.create_foreign_key(op.f(name), table, parent, local, remote, ondelete=action)


def upgrade():
    replace_relations("RESTRICT")


def downgrade():
    db = op.get_bind()
    if any(
        db.scalar(sa.text("SELECT count(*) FROM " + table))
        for table in ("eipd_child_reviews", "eipd_child_resolutions")
    ):
        raise RuntimeError(
            "Downgrade bloqueado: no restaurar cascadas con historial infancia"
        )
    replace_relations("CASCADE")
