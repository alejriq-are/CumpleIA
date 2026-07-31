"""Tests de app/services/authorization.py (ADR 0001).

`role_has_permission` es una función pura (sin DB): se prueba como matriz de
los 4 roles × 4 permisos. `has_permission` sí toca la base (resuelve la
membresía real) y corre contra el rol admin (`_session_factory`) — es lógica
de negocio, no una política RLS; el aislamiento por organización ya está
cubierto en test_rls_isolation.py / test_rls_isolation_diagnosticos.py.
"""

import uuid

import pytest
import pytest_asyncio
from sqlalchemy import delete

from app.db.models import Profile, UserRole
from app.services.authorization import Permission, has_permission, role_has_permission

_ALL_PERMISSIONS = {
    Permission.view_content,
    Permission.edit_content,
    Permission.manage_members,
    Permission.manage_organization,
}

_EXPECTED_BY_ROLE = {
    UserRole.viewer: {Permission.view_content},
    UserRole.editor: {Permission.view_content, Permission.edit_content},
    UserRole.admin: _ALL_PERMISSIONS,
    UserRole.owner: _ALL_PERMISSIONS,
}


@pytest.mark.parametrize("role", list(UserRole))
def test_role_has_permission_matriz(role):
    for permission in Permission:
        esperado = permission in _EXPECTED_BY_ROLE[role]
        assert (
            role_has_permission(role, permission) is esperado
        ), f"{role}/{permission}: se esperaba {esperado}"


_SUPERADMIN_PROFILE_ID = uuid.uuid4()
_SUPERADMIN_AUTH_ID = uuid.uuid4()


@pytest_asyncio.fixture
async def superadmin_profile(_session_factory):
    """Perfil con is_superadmin=True, sin ninguna membresía en ninguna
    organización — a propósito, para probar que el bypass no depende de
    pertenencia (ver ADR 0001)."""
    async with _session_factory() as session:
        profile = Profile(
            id=_SUPERADMIN_PROFILE_ID,
            auth_user_id=_SUPERADMIN_AUTH_ID,
            email="superadmin_authz_test@cumpleia.cl",
            is_superadmin=True,
        )
        session.add(profile)
        await session.commit()

    yield profile

    async with _session_factory() as session:
        await session.execute(
            delete(Profile).where(Profile.id == _SUPERADMIN_PROFILE_ID)
        )
        await session.commit()


@pytest.mark.asyncio
async def test_has_permission_miembro_real_usa_su_rol(
    _session_factory, org_a_id, profile_a_id, _seed_test_data
):
    async with _session_factory() as session:
        profile_a = await session.get(Profile, profile_a_id)
        assert await has_permission(
            session, profile_a, Permission.manage_organization, org_a_id
        )


@pytest.mark.asyncio
async def test_has_permission_no_miembro_es_false_aunque_la_organizacion_exista(
    _session_factory, org_a_id, profile_b_id, _seed_test_data
):
    async with _session_factory() as session:
        profile_b = await session.get(Profile, profile_b_id)
        assert not await has_permission(
            session, profile_b, Permission.view_content, org_a_id
        )


@pytest.mark.asyncio
async def test_has_permission_superadmin_bypassa_sin_membresia(
    _session_factory, org_a_id, superadmin_profile, _seed_test_data
):
    async with _session_factory() as session:
        assert await has_permission(
            session, superadmin_profile, Permission.manage_organization, org_a_id
        )
