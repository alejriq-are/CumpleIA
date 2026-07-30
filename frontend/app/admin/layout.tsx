import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { api } from "@/lib/api/client";

// Panel interno de CumpleIA (rol superadmin) — no visible ni enlazado para
// admin_pyme/usuario. La verificación real vive en el backend (403 si el
// perfil no tiene is_superadmin); esto solo evita exponer la ruta en la UI.
export default async function AdminLayout({ children }: { children: React.ReactNode }) {
  const supabase = await createClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();

  if (!session) {
    redirect("/login");
  }

  const profile = await api.me.get(session.access_token).catch(() => null);
  if (!profile?.is_superadmin) {
    redirect("/dashboard");
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="border-b border-gray-200 bg-white px-6 py-4">
        <div className="mx-auto flex max-w-5xl items-center justify-between">
          <span className="text-xl font-bold text-blue-800">CumpleIA · Panel interno</span>
          <span className="text-sm text-gray-500">{profile.email}</span>
        </div>
      </nav>
      <main className="mx-auto max-w-5xl px-6 py-8">{children}</main>
    </div>
  );
}
