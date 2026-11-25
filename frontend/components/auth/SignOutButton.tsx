"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";

export function SignOutButton({ beforeSignOut }: { beforeSignOut?: () => Promise<boolean> } = {}) {
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  async function handleSignOut() {
    if (beforeSignOut && !(await beforeSignOut())) return;
    setLoading(true);
    const supabase = createClient();
    await supabase.auth.signOut();
    router.push("/login");
    router.refresh();
  }

  return (
    <button
      type="button"
      onClick={handleSignOut}
      disabled={loading}
      className="text-sm font-medium text-gray-500 hover:text-gray-700 disabled:opacity-60"
    >
      {loading ? "Cerrando…" : "Cerrar sesión"}
    </button>
  );
}
