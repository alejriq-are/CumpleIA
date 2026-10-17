import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import { LegalAssessmentEditor } from "@/components/licitud/LegalAssessmentEditor";
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
      <Link href="/dashboard/licitud" className="text-blue-700">
        Volver a Bases de licitud
      </Link>
      <h1 className="text-2xl font-bold">Evaluación de licitud</h1>
      <p>{organization.name}</p>
      <LegalAssessmentEditor
        organizationId={organization.id}
        treatmentId={treatmentId}
        assessmentId={assessmentId}
        readOnly={organization.readOnly}
      />
      <h2 className="text-xl font-semibold">Infancia, expediente y revisiones</h2>
      <p>
        Completa infancia solo cuando corresponda al tratamiento. Los requisitos pendientes no
        habilitan la activación EIPD.
      </p>
      <ChildAdolescentPage
        organizationId={organization.id}
        treatmentId={treatmentId}
        assessmentId={assessmentId}
        readOnly={organization.readOnly}
      />
    </div>
  );
}
