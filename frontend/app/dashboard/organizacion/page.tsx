import Link from "next/link";
import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { api } from "@/lib/api/client";
import { OrganizacionForm } from "@/components/organizacion/OrganizacionForm";

export default async function OrganizacionPage() {
  const supabase = await createClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();

  if (!session) {
    redirect("/login");
  }

  const organizaciones = await api.me.organizations(session.access_token);

  return (
    <div className="space-y-6">
      <Link href="/dashboard" className="text-sm text-blue-700 hover:underline">
        ← Volver al panel
      </Link>

      <div>
        <h1 className="text-2xl font-bold text-gray-900">Datos de la organización</h1>
        <p className="mt-1 text-sm text-gray-500">
          Esta información aparece en el encabezado de los informes exportados.
        </p>
      </div>

      <OrganizacionForm organizacion={organizaciones[0] ?? null} />
    </div>
  );
}
