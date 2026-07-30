"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";

type Status = "checking" | "ready" | "invalid";
type Message = { type: "error" | "info"; text: string };

export function ResetPasswordForm() {
  const [status, setStatus] = useState<Status>("checking");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState<Message | null>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const supabase = createClient();

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((event) => {
      if (event === "PASSWORD_RECOVERY") {
        setStatus("ready");
      }
    });

    // Si la página se recarga, la sesión de recuperación ya existe en las
    // cookies y el evento PASSWORD_RECOVERY no se vuelve a emitir. En ese
    // caso basta con confirmar que hay una sesión activa.
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session) {
        setStatus((current) => (current === "checking" ? "ready" : current));
      }
    });

    const timeout = setTimeout(() => {
      setStatus((current) => (current === "checking" ? "invalid" : current));
    }, 4000);

    return () => {
      subscription.unsubscribe();
      clearTimeout(timeout);
    };
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setMessage(null);

    if (password.length < 8) {
      setMessage({ type: "error", text: "La contraseña debe tener al menos 8 caracteres." });
      return;
    }
    if (password !== confirmPassword) {
      setMessage({ type: "error", text: "Las contraseñas no coinciden." });
      return;
    }

    setLoading(true);
    const supabase = createClient();
    const { error } = await supabase.auth.updateUser({ password });

    if (error) {
      setLoading(false);
      setMessage({ type: "error", text: error.message });
      return;
    }

    await supabase.auth.signOut();
    router.push("/login?reset=success");
    router.refresh();
  }

  if (status === "checking") {
    return <p className="text-sm text-gray-500">Verificando enlace de recuperación…</p>;
  }

  if (status === "invalid") {
    return (
      <div className="space-y-4">
        <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
          Este enlace de recuperación no es válido o ya expiró.
        </p>
        <a
          href="/forgot-password"
          className="block text-center text-sm font-medium text-blue-700 hover:text-blue-800"
        >
          Solicitar un nuevo enlace
        </a>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="password" className="block text-sm font-medium text-gray-700">
          Nueva contraseña
        </label>
        <input
          id="password"
          type="password"
          required
          minLength={8}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Mínimo 8 caracteres"
          className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>

      <div>
        <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
          Confirmar contraseña
        </label>
        <input
          id="confirmPassword"
          type="password"
          required
          minLength={8}
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          placeholder="Repite la contraseña"
          className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>

      {message && (
        <p
          className={`rounded-lg px-3 py-2 text-sm ${
            message.type === "error" ? "bg-red-50 text-red-700" : "bg-blue-50 text-blue-700"
          }`}
        >
          {message.text}
        </p>
      )}

      <button
        type="submit"
        disabled={loading}
        className="w-full rounded-lg bg-blue-700 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-800 disabled:opacity-60"
      >
        {loading ? "Guardando…" : "Guardar nueva contraseña"}
      </button>
    </form>
  );
}
