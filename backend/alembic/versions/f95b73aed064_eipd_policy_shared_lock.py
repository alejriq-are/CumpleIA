"""Bloqueo compartido limitado de selector EIPD; no escritura runtime.

Revision ID: f95b73aed064
Revises: e84a629dcf53
"""

from alembic import op

revision = "f95b73aed064"
down_revision = "e84a629dcf53"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """CREATE FUNCTION public.lock_eipd_policy_selector_v1()
      RETURNS boolean LANGUAGE plpgsql VOLATILE SECURITY DEFINER
      SET search_path = pg_catalog AS $$
      BEGIN
        IF auth.uid() IS NULL OR NOT EXISTS (
          SELECT 1 FROM public.profiles WHERE auth_user_id=auth.uid()) THEN
          RAISE EXCEPTION 'Actor autenticado requerido para bloqueo EIPD'
            USING ERRCODE='42501';
        END IF;
        PERFORM pg_catalog.pg_advisory_xact_lock_shared(719093::bigint);
        PERFORM id FROM public.eipd_policy_selector WHERE id=1 FOR SHARE;
        RETURN FOUND;
      END $$"""
    )
    op.execute(
        "REVOKE ALL ON FUNCTION public.lock_eipd_policy_selector_v1() FROM PUBLIC, app_user, eipd_policy_admin"
    )
    op.execute(
        "GRANT EXECUTE ON FUNCTION public.lock_eipd_policy_selector_v1() TO app_user"
    )


def downgrade() -> None:
    op.execute("DROP FUNCTION public.lock_eipd_policy_selector_v1()")
