import Link from "next/link";
import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { api } from "@/lib/api/client";
import { AutodiagnosticoWorkspace } from "@/components/autodiagnostico/AutodiagnosticoWorkspace";

export default async function AutodiagnosticoPage() {
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

      {organizaciones.length === 0 ? (
        <div className="rounded-xl border border-amber-200 bg-amber-50 px-5 py-4 text-sm text-amber-800">
          Todavía no tienes una organización.{" "}
          <Link href="/dashboard/organizacion" className="font-medium underline">
            Crea una
          </Link>{" "}
          antes de comenzar el autodiagnóstico.
        </div>
      ) : (
        <AutodiagnosticoWorkspace organizaciones={organizaciones} />
      )}
    </div>
  );
}
