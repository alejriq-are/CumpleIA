import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { api } from "@/lib/api/client";
import { CuestionarioConfigEditor } from "@/components/admin/CuestionarioConfigEditor";

export default async function CuestionarioConfigPage() {
  const supabase = await createClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();

  if (!session) {
    redirect("/login");
  }

  try {
    const config = await api.cuestionarioConfig.get(session.access_token);
    return <CuestionarioConfigEditor initialConfig={config} />;
  } catch (error) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">
        No se pudo cargar la configuración del cuestionario:{" "}
        {error instanceof Error ? error.message : "error desconocido"}.
      </div>
    );
  }
}
