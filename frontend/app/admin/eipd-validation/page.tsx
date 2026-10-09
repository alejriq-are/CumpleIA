"use client";

import { useState } from "react";
import { createClient } from "@/lib/supabase/client";

type Audit = {
  selector: { revision: number; publication_id: string } | null;
  publications: {
    id: string;
    policy: { policy_reference: string; activation: string };
    policy_hash: string;
  }[];
  selections: { id: string; revision: number }[];
};

export default function EipdValidationPage() {
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [audit, setAudit] = useState<Audit | null>(null);
  const local = process.env.NODE_ENV === "development";

  async function checkAccess() {
    setBusy(true);
    setMessage("");
    try {
      const { data, error } = await createClient().auth.getSession();
      if (error || !data.session) {
        setMessage("Inicia sesión para comprobar el acceso.");
        return;
      }
      const response = await fetch("http://127.0.0.1:8001/admin/eipd/status", {
        headers: { Authorization: `Bearer ${data.session.access_token}` },
        cache: "no-store",
      });
      if (response.status === 401) setMessage("La sesión no es válida. Vuelve a iniciar sesión.");
      else if (response.status === 403) setMessage("Tu usuario no tiene acceso administrativo.");
      else if (response.status === 503) setMessage("El canal administrativo no está disponible.");
      else if (!response.ok) setMessage("No se pudo completar la comprobación.");
      else {
        const result = await response.json();
        setMessage(
          result.authenticated_admin === true
            ? "Acceso administrativo confirmado. La activación EIPD permanece bloqueada."
            : "No se pudo confirmar el acceso."
        );
      }
    } catch {
      setMessage("No se pudo conectar con el servicio de validación local.");
    } finally {
      setBusy(false);
    }
  }

  async function readAudit() {
    setBusy(true);
    setAudit(null);
    setMessage("");
    try {
      const { data, error } = await createClient().auth.getSession();
      if (error || !data.session) {
        setMessage("Inicia sesión para consultar el registro.");
        return;
      }
      const response = await fetch("http://127.0.0.1:8001/admin/eipd/audit", {
        headers: { Authorization: `Bearer ${data.session.access_token}` },
        cache: "no-store",
      });
      if (!response.ok) {
        setMessage("No se pudo consultar el registro. Comprueba tu acceso administrativo.");
        return;
      }
      setAudit(await response.json());
      setMessage("Registro consultado. La activación EIPD permanece bloqueada.");
    } catch {
      setMessage("No se pudo conectar con el servicio de validación local.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="mx-auto max-w-2xl space-y-4 p-6">
      <h1 className="text-2xl font-semibold">Comprobar acceso administrativo</h1>
      <p>Esta comprobación utiliza tu sesión actual y no modifica políticas.</p>
      {local ? (
        <button
          type="button"
          onClick={checkAccess}
          disabled={busy}
          className="rounded bg-blue-700 px-4 py-2 text-white disabled:opacity-50"
        >
          {busy ? "Comprobando…" : "Comprobar acceso"}
        </button>
      ) : (
        <p>Esta pantalla está disponible solo en desarrollo local.</p>
      )}
      {local && (
        <button
          type="button"
          onClick={readAudit}
          disabled={busy}
          className="rounded bg-blue-700 px-4 py-2 text-white disabled:opacity-50"
        >
          Consultar registro
        </button>
      )}
      {audit && (
        <section className="space-y-2" aria-label="Registro de políticas">
          <h2 className="text-xl font-semibold">Registro de políticas</h2>
          <p>Revisión actual: {audit.selector?.revision ?? 0}</p>
          <p>
            Publicaciones: {audit.publications.length}. Selecciones: {audit.selections.length}.
          </p>
          {!audit.selector && <p>Todavía no hay una política seleccionada.</p>}
          {audit.publications.map((publication) => (
            <p key={publication.id}>
              {publication.policy.policy_reference}: {publication.policy.activation}
              {audit.selector?.publication_id === publication.id ? " · seleccionada" : ""}
            </p>
          ))}
          <p>La consulta no modifica políticas.</p>
        </section>
      )}
      <p role="status" aria-live="polite">
        {message}
      </p>
    </main>
  );
}
