"""Autoridad personal EIPD limitada, sin API ni conexion a escritores.

Revision ID: b17d95c0286f
Revises: a06c84bf175e
"""

from alembic import op

revision = "b17d95c0286f"
down_revision = "a06c84bf175e"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """CREATE FUNCTION public.lock_eipd_personal_authority_v1()
      RETURNS uuid LANGUAGE plpgsql VOLATILE SECURITY DEFINER
      SET search_path=pg_catalog AS $$
      DECLARE actor uuid; authorized boolean;
      BEGIN
        IF auth.uid() IS NULL THEN
          RAISE EXCEPTION 'Identidad administrativa requerida' USING ERRCODE='42501';
        END IF;
        SELECT id,is_superadmin INTO actor,authorized FROM public.profiles
          WHERE auth_user_id=auth.uid() FOR SHARE;
        IF actor IS NULL OR authorized IS DISTINCT FROM true THEN
          RAISE EXCEPTION 'Autoridad personal administrativa requerida' USING ERRCODE='42501';
        END IF;
        RETURN actor;
      END $$"""
    )
    op.execute(
        "REVOKE ALL ON FUNCTION public.lock_eipd_personal_authority_v1() FROM PUBLIC,app_user,eipd_policy_admin"
    )
    op.execute(
        "GRANT EXECUTE ON FUNCTION public.lock_eipd_personal_authority_v1() TO eipd_policy_admin"
    )


def downgrade():
    op.execute("DROP FUNCTION public.lock_eipd_personal_authority_v1()")
