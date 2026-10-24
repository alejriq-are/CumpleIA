"""python -m scripts.eipd_admin_preflight; diagnostico limitado, sin JWT/escrituras."""

import asyncio
import json

from sqlalchemy import text

from app.db.eipd_admin import _prepare_channel, get_eipd_admin_session_factory
from app.services.eipd_policy_store import read_eipd_policy_audit_snapshot_v1


async def inspect_permissions(db):
    """Catalogo public: permisos efectivos incluyen PUBLIC y grants por columna."""
    group_safe = await db.scalar(
        text(
            """
        SELECT NOT (rolcanlogin OR rolsuper OR rolbypassrls OR rolcreaterole
          OR rolcreatedb OR rolreplication OR rolinherit)
          AND NOT EXISTS (SELECT 1 FROM pg_auth_members WHERE member=r.oid)
          AND NOT EXISTS (SELECT 1 FROM pg_class WHERE relowner=r.oid)
          AND NOT pg_has_role('app_user',r.oid,'MEMBER')
          AND NOT EXISTS (SELECT 1 FROM pg_auth_members
            WHERE member=session_user::regrole AND admin_option)
          AND NOT has_schema_privilege(r.oid,'public','CREATE')
          AND NOT has_schema_privilege(session_user,'public','CREATE')
        FROM pg_roles r WHERE rolname='eipd_policy_admin'
    """
        )
    )
    if group_safe is not True:
        raise ValueError("Grupo/canal incompatible")
    rows = (
        await db.execute(
            text(
                """
        SELECT c.relname,c.relrowsecurity,
          has_table_privilege(current_user,c.oid,'SELECT'),
          has_table_privilege(current_user,c.oid,'INSERT'),
          has_table_privilege(current_user,c.oid,'UPDATE'),
          has_table_privilege(current_user,c.oid,'DELETE,TRUNCATE,REFERENCES,TRIGGER'),
          has_any_column_privilege(current_user,c.oid,'UPDATE'),
          has_any_column_privilege(current_user,c.oid,'REFERENCES')
        FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
        WHERE n.nspname='public' AND c.relname IN
          ('eipd_policy_publications','eipd_policy_selections','eipd_policy_selector')
          AND c.relkind IN ('r','p')
    """
            )
        )
    ).all()
    if len(rows) != 3:
        raise ValueError("Catalogo incompleto")
    for name, rls, read, insert, update, destructive, column_update, references in rows:
        expected_update = name == "eipd_policy_selector"
        if (
            not rls
            or not read
            or not insert
            or update != expected_update
            or column_update != expected_update
            or destructive
            or references
        ):
            raise ValueError("Permisos de auditoria incompatibles")
    leaked = await db.scalar(
        text(
            """
        SELECT EXISTS (
          SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
          WHERE n.nspname='public' AND c.relkind IN ('r','p','v','m','f')
            AND (
              has_table_privilege(session_user,c.oid,'SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER')
              OR has_any_column_privilege(session_user,c.oid,'SELECT,INSERT,UPDATE,REFERENCES')
              OR (c.relname NOT IN ('eipd_policy_publications','eipd_policy_selections','eipd_policy_selector')
                AND (has_table_privilege(current_user,c.oid,'SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER')
                  OR has_any_column_privilege(current_user,c.oid,'SELECT,INSERT,UPDATE,REFERENCES')))
            ))
    """
        )
    )
    if leaked:
        raise ValueError("Acceso fuera de alcance")


async def inspect_channel(factory):
    """Caller proporciona el pool dedicado; rollback siempre, sin identidad personal."""
    async with factory() as db:
        try:
            await db.execute(text("SET TRANSACTION READ ONLY"))
            await _prepare_channel(db)
            if await db.scalar(
                text("SELECT NULLIF(current_setting('request.jwt.claim.sub',true),'')")
            ):
                raise ValueError("Identidad residual")
            if await db.scalar(text("SHOW transaction_isolation")) != "read committed":
                raise ValueError("Aislamiento no admitido")
            allowed = await db.scalar(
                text(
                    "SELECT has_function_privilege(current_user, 'public.lock_eipd_personal_authority_v1()', 'EXECUTE') "
                    "AND NOT has_table_privilege(current_user,'public.profiles','UPDATE') "
                    "AND NOT has_column_privilege(current_user,'public.profiles','is_superadmin','UPDATE')"
                )
            )
            if allowed is not True:
                raise ValueError("Permisos no admitidos")
            await inspect_permissions(db)
            state = await read_eipd_policy_audit_snapshot_v1(db)
            if any(p.policy.activation != "deshabilitada" for p in state.publications):
                raise ValueError("Politica habilitada inesperada")
            return {
                "status": "ok" if state.selector else "pending_selector",
                "report_version": 1,
                "channel_verified": True,
                "permissions_verified": True,
                "permission_scope": "public_relations_and_role_flags",
                "environment_identity_verified": False,
                "migration_head_verified": False,
                "audit_coherent": True,
                "selector_present": state.selector is not None,
                "selector_revision": (
                    state.selector.revision if state.selector else None
                ),
                "personal_authentication_verified": False,
                "activation_authorized": False,
            }
        finally:
            await db.rollback()


async def main():
    factory = None
    try:
        factory = get_eipd_admin_session_factory()
        report = await inspect_channel(factory)
        code = 0 if report["status"] == "ok" else 2
    except Exception:
        # No imprimir excepciones/URL/parametros ni distinguir secretos en errores.
        report = {
            "status": "failed",
            "channel_verified": False,
            "activation_authorized": False,
        }
        code = 1
    finally:
        if factory is not None:
            await factory.kw["bind"].dispose()
    print(json.dumps(report, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
