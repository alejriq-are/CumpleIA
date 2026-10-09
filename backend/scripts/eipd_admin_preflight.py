"""python -m scripts.eipd_admin_preflight; diagnostico limitado, sin JWT/escrituras."""

import asyncio
import json

from sqlalchemy import text

from app.db.eipd_admin import _prepare_channel, get_eipd_admin_session_factory
from app.services.eipd_policy_store import read_eipd_policy_audit_snapshot_v1


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
            state = await read_eipd_policy_audit_snapshot_v1(db)
            if any(p.policy.activation != "deshabilitada" for p in state.publications):
                raise ValueError("Politica habilitada inesperada")
            return {
                "status": "ok" if state.selector else "pending_selector",
                "channel_verified": True,
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
