import Link from "next/link";
import { redirect } from "next/navigation";
import { TreatmentGeneralForm } from "@/components/rat/TreatmentGeneralForm";
import { api } from "@/lib/api/client";
import { createClient } from "@/lib/supabase/server";

export default async function NuevoTratamientoPage({
  searchParams,
}: {
  searchParams: Promise<{ organizationId?: string }>;
}) {
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

  return (
    <div className="space-y-6">
      <Link href="/dashboard/rat" className="text-sm text-blue-700 hover:underline">
        ← Volver al inventario
      </Link>

      <div>
        <h1 className="text-2xl font-bold text-gray-900">Nueva actividad de tratamiento</h1>
        <p className="mt-1 text-sm text-gray-500">
          Comienza con la información general. La actividad se guardará como borrador.
        </p>
      </div>

      <TreatmentGeneralForm
        organizaciones={organizaciones}
        initialOrganizationId={initialOrganizationId}
      />
    </div>
  );
}
