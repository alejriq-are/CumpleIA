"""Protege identidad/autoridad de perfiles conservando JIT autenticado.

Revision ID: a06c84bf175e
Revises: f95b73aed064
"""

from alembic import op

revision = "a06c84bf175e"
down_revision = "f95b73aed064"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "REVOKE INSERT, UPDATE, DELETE, TRUNCATE ON public.profiles FROM app_user"
    )
    op.execute(
        "GRANT INSERT (auth_user_id,email,full_name) ON public.profiles TO app_user"
    )
    op.execute(
        "GRANT UPDATE (email,full_name,updated_at) ON public.profiles TO app_user"
    )
    op.execute(
        """CREATE FUNCTION public.check_runtime_profile_identity_v1()
      RETURNS trigger LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $$
      BEGIN
        IF current_user='app_user' THEN
          IF auth.uid() IS NULL OR NEW.auth_user_id IS DISTINCT FROM auth.uid() THEN
            RAISE EXCEPTION 'Identidad propia autenticada requerida' USING ERRCODE='42501';
          END IF;
          IF TG_OP='INSERT' AND NEW.is_superadmin THEN
            RAISE EXCEPTION 'Autoridad administrativa no permitida' USING ERRCODE='42501';
          END IF;
          IF TG_OP='UPDATE' AND (OLD.auth_user_id IS DISTINCT FROM auth.uid()
            OR NEW.id IS DISTINCT FROM OLD.id
            OR NEW.auth_user_id IS DISTINCT FROM OLD.auth_user_id
            OR NEW.is_superadmin IS DISTINCT FROM OLD.is_superadmin) THEN
            RAISE EXCEPTION 'Identidad y autoridad inmutables para runtime' USING ERRCODE='42501';
          END IF;
        END IF;
        RETURN NEW;
      END $$"""
    )
    op.execute(
        "REVOKE ALL ON FUNCTION public.check_runtime_profile_identity_v1() FROM PUBLIC,app_user,eipd_policy_admin"
    )
    op.execute(
        "CREATE TRIGGER runtime_profile_identity BEFORE INSERT OR UPDATE ON public.profiles FOR EACH ROW EXECUTE FUNCTION public.check_runtime_profile_identity_v1()"
    )


def downgrade():
    op.execute("DROP TRIGGER runtime_profile_identity ON public.profiles")
    op.execute("DROP FUNCTION public.check_runtime_profile_identity_v1()")
    op.execute(
        "REVOKE INSERT(auth_user_id,email,full_name), UPDATE(email,full_name,updated_at) ON public.profiles FROM app_user"
    )
    op.execute("GRANT INSERT,UPDATE,DELETE ON public.profiles TO app_user")
