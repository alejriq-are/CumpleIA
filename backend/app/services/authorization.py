"""Autorización por permisos dentro de una organización.

Ver docs/adr/0001-modelo-organizaciones-roles-suscripcion.md. El catálogo de
permisos y su relación con los roles vive en código, no en una tabla: con 4
roles fijos (`UserRole`) y sin necesidad de que una organización personalice
sus propios permisos, una tabla `permissions` dinámica sería sobre-ingeniería
para el segmento objetivo (micro/pequeña empresa, autoservicio).
"""

import enum
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Membership, Profile, UserRole


class Permission(str, enum.Enum):
    view_content = "view_content"
    edit_content = "edit_content"
    manage_members = "manage_members"
    manage_organization = "manage_organization"


# Jerarquía acumulativa: viewer ⊂ editor ⊂ admin = owner. `owner` y `admin`
# comparten el mismo conjunto de permisos por ahora; lo que distingue a
# `owner` (intransferible/no removible) es una regla que se aplicará el día
# que exista gestión de miembros, no un permiso.
_ROLE_PERMISSIONS: dict[UserRole, frozenset[Permission]] = {
    UserRole.viewer: frozenset({Permission.view_content}),
    UserRole.editor: frozenset({Permission.view_content, Permission.edit_content}),
    UserRole.admin: frozenset(
        {
            Permission.view_content,
            Permission.edit_content,
            Permission.manage_members,
            Permission.manage_organization,
        }
    ),
    UserRole.owner: frozenset(
        {
            Permission.view_content,
            Permission.edit_content,
            Permission.manage_members,
            Permission.manage_organization,
        }
    ),
}


def role_has_permission(role: UserRole, permission: Permission) -> bool:
    return permission in _ROLE_PERMISSIONS[role]


async def has_permission(
    db: AsyncSession,
    profile: Profile,
    permission: Permission,
    organization_id: uuid.UUID,
) -> bool:
    """El admin de plataforma (`is_superadmin`) no depende de ninguna
    membresía: tiene acceso pleno a cualquier organización. Para el resto,
    el permiso depende del rol de su `Membership` en esa organización
    puntual; sin membresía, no hay permiso posible."""
    if profile.is_superadmin:
        return True

    membership = (
        await db.execute(
            select(Membership).where(
                Membership.organization_id == organization_id,
                Membership.profile_id == profile.id,
            )
        )
    ).scalar_one_or_none()
    if membership is None:
        return False

    return role_has_permission(membership.role, permission)
