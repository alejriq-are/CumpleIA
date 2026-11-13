"""Privilegios efectivos/JIT y proteccion de identidad frente a app_user real."""

from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from tests import test_rls_isolation_licitud as rls

app_role_session = rls.app_role_session


async def test_effective_privileges(app_role_session):
    row = (
        await app_role_session.execute(
            text(
                """SELECT
      has_table_privilege(current_user,'profiles','INSERT'),
      has_table_privilege(current_user,'profiles','UPDATE'),
      has_table_privilege(current_user,'profiles','DELETE'),
      has_table_privilege(current_user,'profiles','TRUNCATE'),
      has_column_privilege(current_user,'profiles','is_superadmin','UPDATE'),
      has_column_privilege(current_user,'profiles','auth_user_id','UPDATE'),
      has_column_privilege(current_user,'profiles','id','INSERT'),
      has_column_privilege(current_user,'profiles','email','UPDATE')"""
            )
        )
    ).one()
    assert tuple(row) == (False, False, False, False, False, False, False, True)


async def test_jit_insert_conflict_and_own_basic_update(app_role_session):
    auth = uuid4()
    await rls._set_auth_user(app_role_session, auth)
    sql = text(
        "INSERT INTO profiles(auth_user_id,email,full_name) VALUES (:auth,:email,'TEST') ON CONFLICT(auth_user_id) DO NOTHING RETURNING id,is_superadmin"
    )
    params = dict(auth=auth, email="test-" + str(auth) + "@example.org")
    row = (await app_role_session.execute(sql, params)).one()
    assert row.id and row.is_superadmin is False
    assert (await app_role_session.execute(sql, params)).first() is None
    await app_role_session.execute(
        text("UPDATE profiles SET full_name='TEST updated' WHERE id=:id"),
        dict(id=row.id),
    )
    assert (
        await app_role_session.scalar(
            text("SELECT full_name FROM profiles WHERE id=:id"), dict(id=row.id)
        )
        == "TEST updated"
    )
    await app_role_session.rollback()


@pytest.mark.parametrize(
    "mode", ["anonymous", "other_identity", "promote", "explicit_id"]
)
async def test_forged_insert_denied(app_role_session, auth_a_id, mode):
    if mode != "anonymous":
        await rls._set_auth_user(app_role_session, auth_a_id)
    identity = uuid4() if mode in ("anonymous", "other_identity") else auth_a_id
    columns = "auth_user_id,email"
    values = ":auth,:email"
    if mode == "promote":
        columns += ",is_superadmin"
        values += ",true"
    if mode == "explicit_id":
        columns += ",id"
        values += ",:id"
    with pytest.raises(DBAPIError):
        await app_role_session.execute(
            text(f"INSERT INTO profiles({columns}) VALUES ({values})"),
            dict(auth=identity, email="test@example.org", id=uuid4()),
        )
    await app_role_session.rollback()


@pytest.mark.parametrize(
    "mode", ["promote", "identity", "id", "delete", "truncate", "other_basic"]
)
async def test_runtime_mutation_denied(
    app_role_session, auth_a_id, profile_a_id, profile_b_id, mode
):
    await rls._set_auth_user(app_role_session, auth_a_id)
    statements = {
        "promote": "UPDATE profiles SET is_superadmin=true WHERE id=:id",
        "identity": "UPDATE profiles SET auth_user_id=:new WHERE id=:id",
        "id": "UPDATE profiles SET id=:new WHERE id=:id",
        "delete": "DELETE FROM profiles WHERE id=:id",
        "truncate": "TRUNCATE profiles CASCADE",
        "other_basic": "UPDATE profiles SET full_name='TEST forged' WHERE id=:id",
    }
    with pytest.raises(DBAPIError):
        await app_role_session.execute(
            text(statements[mode]),
            dict(
                id=profile_b_id if mode == "other_basic" else profile_a_id, new=uuid4()
            ),
        )
    await app_role_session.rollback()
