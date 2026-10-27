import Link from "next/link";
import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { api } from "@/lib/api/client";
import { ConnectedWorkspace } from "@/components/navigation/ConnectedWorkspace";
export const metadata = { title: "Espacio de trabajo | CumpleIA" };

export default async function ConnectedPage() {
  const {
    data: { session },
  } = await (await createClient()).auth.getSession();
  if (!session) redirect("/login");
  const organizations = await api.me.organizations(session.access_token);
  if (!organizations.length)
    return (
      <main className="space-y-4" aria-labelledby="connected-empty-title">
        <h1 id="connected-empty-title" className="text-2xl font-bold">
          Espacio de trabajo
        </h1>
        <p>Necesitas una organización para comenzar.</p>
        <Link href="/dashboard/organizacion" className="text-blue-800 underline">
          Crear organización
        </Link>
      </main>
    );
  return <ConnectedWorkspace organizations={organizations} />;
}
