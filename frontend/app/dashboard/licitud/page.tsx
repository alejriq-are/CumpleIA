import Link from "next/link";
import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { api } from "@/lib/api/client";
import { LicitudWorkspace } from "@/components/licitud/LicitudWorkspace";
export default async function Page() {
  const {
    data: { session },
  } = await (await createClient()).auth.getSession();
  if (!session) redirect("/login");
  const organizations = await api.me.organizations(session.access_token);
  return (
    <div className="licitud-ui space-y-6">
      <Link href="/dashboard" className="text-blue-700">
        Volver al panel
      </Link>
      <h1 className="text-2xl font-bold">Bases de licitud</h1>
      <aside className="rounded-lg border border-blue-200 bg-blue-50 p-4">
        <p className="font-semibold">Prueba una forma más clara de completar y revisar</p>
        <p className="mt-1 text-sm">
          Maqueta con escenarios ficticios; tus expedientes no cambian.
        </p>
        <Link
          href="/dashboard/maqueta"
          className="mt-3 inline-block rounded-md bg-blue-800 px-4 py-2 font-medium text-white hover:bg-blue-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-800"
        >
          Abrir maqueta integral de CumpleIA
        </Link>
      </aside>
      {organizations.length ? (
        <LicitudWorkspace organizaciones={organizations} />
      ) : (
        <p>
          Crea una{" "}
          <Link href="/dashboard/organizacion" className="text-blue-700 underline">
            organización de prueba
          </Link>{" "}
          para comenzar.
        </p>
      )}
    </div>
  );
}
