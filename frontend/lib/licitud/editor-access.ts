export function childEditorAccess(
  organizationId: string | undefined,
  memberships: { id: string; name: string; role: string }[],
  isSuperadmin: boolean
) {
  if (
    !organizationId ||
    !/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(organizationId)
  )
    return null;
  const member = memberships.find((o) => o.id === organizationId);
  if (isSuperadmin)
    return {
      id: organizationId,
      name: member?.name ?? "Expediente interno de prueba",
      readOnly: false,
    };
  if (!member) return null;
  return {
    id: member.id,
    name: member.name,
    readOnly: !["owner", "admin", "editor"].includes(member.role),
  };
}
