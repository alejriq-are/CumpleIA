import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { api } from "@/lib/api/client";
import { encodeWork } from "@/components/navigation/connected-navigation";
export default async function Page({
  searchParams,
}: {
  searchParams: Promise<{ organizationId?: string }>;
}) {
  const {
    data: { session },
  } = await (await createClient()).auth.getSession();
  if (!session) redirect("/login");
  const organizations = await api.me.organizations(session.access_token);
  if (!organizations.length) redirect("/dashboard/organizacion");
  const requested = (await searchParams).organizationId;
  const org = organizations.find((v) => v.id === requested) ?? organizations[0];
  redirect(
    "/dashboard/trabajo" +
      encodeWork({
        organizationId: org.id,
        treatmentId: "",
        assessmentId: "",
        module: "rat",
        section: "catalogo",
        step: 0,
      })
  );
}
