import Link from "next/link";
import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { api } from "@/lib/api/client";
import { ConnectedWorkspace } from "@/components/navigation/ConnectedWorkspace";
export default async function ConnectedPage() {
  const {
    data: { session },
  } = await (await createClient()).auth.getSession();
  if (!session) redirect("/login");
  const organizations = await api.me.organizations(session.access_token);
  if (!organizations.length)
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold">Espacio de trabajo</h1>
        <p>Necesitas una organización para comenzar.</p>
        <Link href="/dashboard/organizacion" className="text-blue-800 underline">
          Crear organización
        </Link>
      </div>
    );
  return <ConnectedWorkspace organizations={organizations} />;
}
