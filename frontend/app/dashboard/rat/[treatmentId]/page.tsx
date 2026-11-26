import { encodeWork } from "@/components/navigation/connected-navigation";
import { redirect } from "next/navigation";
import { api } from "@/lib/api/client";
import { createClient } from "@/lib/supabase/server";

export default async function TratamientoPage({
  params,
  searchParams,
}: {
  params: Promise<{ treatmentId: string }>;
  searchParams: Promise<{ organizationId?: string }>;
}) {
  const { treatmentId } = await params;

  const supabase = await createClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();

  if (!session) {
    redirect("/login");
  }

  const organizaciones = await api.me.organizations(session.access_token);

  if (organizaciones.length === 0) {
    redirect("/dashboard/organizacion");
  }

  const requested = (await searchParams).organizationId;
  const initialOrganizationId =
    organizaciones.find((org) => org.id === requested)?.id ?? organizaciones[0].id;

  redirect(
    "/dashboard/trabajo" +
      encodeWork({
        organizationId: initialOrganizationId,
        treatmentId,
        assessmentId: "",
        module: "rat",
        section: "general",
        step: 0,
      })
  );
}
