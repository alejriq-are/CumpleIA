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
    <div className="space-y-6">
      <Link href="/dashboard" className="text-blue-700">
        Volver al panel
      </Link>
      <h1 className="text-2xl font-bold">Bases de licitud</h1>
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
