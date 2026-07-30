"use client";

import { useState } from "react";
import { createClient } from "@/lib/supabase/client";

type Message = { type: "error" | "info"; text: string };

export function ForgotPasswordForm() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState<Message | null>(null);
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    const supabase = createClient();
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/reset-password`,
    });

    setLoading(false);

    // No revelamos si el correo está registrado o no: mismo mensaje en ambos casos.
    if (error) {
      setMessage({
        type: "error",
        text: "No pudimos procesar la solicitud. Intenta nuevamente.",
      });
      return;
    }
    setSent(true);
  }

  if (sent) {
    return (
      <div className="space-y-4">
        <p className="rounded-lg bg-blue-50 px-3 py-2 text-sm text-blue-700">
          Si el correo está registrado, te enviamos un enlace para recuperar tu contraseña.
          Revisa tu bandeja de entrada.
        </p>
        <a
          href="/login"
          className="block text-center text-sm font-medium text-blue-700 hover:text-blue-800"
        >
          Volver a iniciar sesión
        </a>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700">
          Correo electrónico
        </label>
        <input
          id="email"
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="tu@empresa.cl"
          className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>

      {message && (
        <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{message.text}</p>
      )}

      <button
        type="submit"
        disabled={loading}
        className="w-full rounded-lg bg-blue-700 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-800 disabled:opacity-60"
      >
        {loading ? "Enviando…" : "Enviar enlace de recuperación"}
      </button>

      <a
        href="/login"
        className="block text-center text-sm font-medium text-blue-700 hover:text-blue-800"
      >
        Volver a iniciar sesión
      </a>
    </form>
  );
}
