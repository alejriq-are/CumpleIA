import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import { ChildAdolescentPage } from "@/components/licitud/ChildAdolescentPage";
import { childEditorAccess } from "@/lib/licitud/editor-access";
import { api } from "@/lib/api/client";
import { createClient } from "@/lib/supabase/server";
export default async function Page({
  params,
  searchParams,
}: {
  params: Promise<{ treatmentId: string; assessmentId: string }>;
  searchParams: Promise<{ organizationId?: string }>;
}) {
  const { treatmentId, assessmentId } = await params;
  const { organizationId } = await searchParams;
  const {
    data: { session },
  } = await (await createClient()).auth.getSession();
  if (!session) redirect("/login");
  const [organizations, profile] = await Promise.all([
    api.me.organizations(session.access_token),
    api.me.get(session.access_token),
  ]);
  const organization = childEditorAccess(organizationId, organizations, profile.is_superadmin);
  if (!organization) notFound();
  return (
    <div className="space-y-6">
      <Link href="/dashboard/rat" className="text-blue-700">
        Volver al inventario
      </Link>
      <h1 className="text-2xl font-bold">Infancia y adolescencia</h1>
      <p>{organization.name}</p>
      <ChildAdolescentPage
        organizationId={organization.id}
        treatmentId={treatmentId}
        assessmentId={assessmentId}
        readOnly={organization.readOnly}
      />
    </div>
  );
}
