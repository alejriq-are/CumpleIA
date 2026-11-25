import Link from "next/link";
import { encodeWork } from "@/components/navigation/connected-navigation";
import { notFound, redirect } from "next/navigation";
import { AssessmentFlow } from "@/components/licitud/AssessmentFlow";
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
  if (organizations.some((v) => v.id === organization.id))
    redirect(
      "/dashboard/trabajo" +
        encodeWork({
          organizationId: organization.id,
          treatmentId,
          assessmentId,
          module: "licitud",
          section: "aplicabilidad",
          step: 0,
        })
    );
  return (
    <div className="space-y-6">
      <Link href="/dashboard/licitud" className="text-blue-700">
        Volver a Bases de licitud
      </Link>
      <h1 className="text-2xl font-bold">Evaluación de licitud</h1>
      <p>{organization.name}</p>
      <AssessmentFlow
        key={`${organization.id}:${treatmentId}:${assessmentId}`}
        organizationId={organization.id}
        organizationName={organization.name}
        treatmentId={treatmentId}
        assessmentId={assessmentId}
        readOnly={organization.readOnly}
      />
    </div>
  );
}
