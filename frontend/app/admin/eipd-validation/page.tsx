"use client";

import { useState } from "react";
import { createClient } from "@/lib/supabase/client";

type Draft = {
  policy: {
    policy_reference: string;
    activation: string;
    sources_status: string;
    acceptance_status: string;
  };
  rationale: string;
  evidence_reference: string;
};

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
  const [draft, setDraft] = useState<Draft | null>(null);
  const [publicationAttempted, setPublicationAttempted] = useState(false);
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

  async function preparePublication() {
    if (!local) return;
    setBusy(true);
    setDraft(null);
    setMessage("");
    try {
      const { data, error } = await createClient().auth.getSession();
      if (error || !data.session) {
        setMessage("Inicia sesión para preparar la publicación.");
        return;
      }
      const headers = { Authorization: `Bearer ${data.session.access_token}` };
      const auditResponse = await fetch("http://127.0.0.1:8001/admin/eipd/audit", {
        headers,
        cache: "no-store",
      });
      if (!auditResponse.ok) throw new Error("audit");
      const current: Audit = await auditResponse.json();
      setAudit(current);
      const response = await fetch("http://127.0.0.1:8001/admin/eipd/publication-draft", {
        headers,
        cache: "no-store",
      });
      if (!response.ok) throw new Error("draft");
      const proposal: Draft = await response.json();
      if (
        proposal.policy.activation !== "deshabilitada" ||
        proposal.policy.sources_status !== "pendiente" ||
        proposal.policy.acceptance_status !== "pendiente"
      )
        throw new Error("policy");
      if (
        current.publications.some(
          (p) => p.policy.policy_reference === proposal.policy.policy_reference
        )
      ) {
        setMessage(
          "La política ya está publicada. Consulta el registro; no se publicará otra vez."
        );
        return;
      }
      setDraft(proposal);
      setMessage("Propuesta preparada. Revisa los datos antes de publicar.");
    } catch {
      setMessage("No se pudo preparar la publicación. Consulta el registro y comprueba tu acceso.");
    } finally {
      setBusy(false);
    }
  }

  async function publishDisabled() {
    if (
      !local ||
      busy ||
      publicationAttempted ||
      !draft ||
      draft.policy.activation !== "deshabilitada"
    )
      return;
    setBusy(true);
    setMessage("");
    try {
      const { data, error } = await createClient().auth.getSession();
      if (error || !data.session) {
        setMessage("Inicia sesión para publicar la política.");
        return;
      }
      setPublicationAttempted(true);
      const headers = { Authorization: `Bearer ${data.session.access_token}` };
      const response = await fetch("http://127.0.0.1:8001/admin/eipd/publications", {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify(draft),
        cache: "no-store",
      });
      setAudit(null);
      if (response.status !== 201) {
        setMessage(
          "Publicación no confirmada. Consulta el registro antes de continuar; no se reintentará automáticamente."
        );
        return;
      }
      const published: Audit["publications"][number] = await response.json();
      const auditResponse = await fetch("http://127.0.0.1:8001/admin/eipd/audit", {
        headers,
        cache: "no-store",
      });
      if (!auditResponse.ok) throw new Error("audit");
      const current: Audit = await auditResponse.json();
      setAudit(current);
      const stored = current.publications.find((p) => p.id === published.id);
      if (
        !stored ||
        stored.policy_hash !== published.policy_hash ||
        stored.policy.activation !== "deshabilitada"
      )
        throw new Error("verification");
      setDraft(null);
      setMessage(
        "Política deshabilitada publicada y confirmada en el registro. Esta acción no selecciona la política. La activación EIPD permanece bloqueada."
      );
    } catch {
      setAudit(null);
      setMessage(
        "No se pudo confirmar el resultado. Consulta el registro antes de continuar; no repitas la publicación a ciegas."
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="mx-auto max-w-2xl space-y-4 p-6">
      <h1 className="text-2xl font-semibold">Comprobar acceso administrativo</h1>
      <p>
        Las comprobaciones utilizan tu sesión actual. Solo el botón de publicación guarda una
        política deshabilitada.
      </p>
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
      {local && (
        <section
          className="space-y-3 rounded border p-4"
          aria-label="Publicación local deshabilitada"
        >
          <h2 className="text-xl font-semibold">Publicar política deshabilitada</h2>
          <p>
            Se guardará una publicación permanente en el registro local, con tu usuario y fecha. Las
            fuentes y la aceptación seguirán pendientes; esta acción no selecciona ni activa la
            política.
          </p>
          <button
            type="button"
            onClick={preparePublication}
            disabled={busy || publicationAttempted}
            className="rounded bg-blue-700 px-4 py-2 text-white disabled:opacity-50"
          >
            Preparar publicación
          </button>
          {draft && (
            <div className="space-y-2">
              <p>Referencia: {draft.policy.policy_reference}</p>
              <p>Estado: deshabilitada. Fuentes: pendientes. Aceptación: pendiente.</p>
              <p>Motivo: {draft.rationale}</p>
              <p>Evidencia: {draft.evidence_reference}</p>
              <button
                type="button"
                onClick={publishDisabled}
                disabled={busy || publicationAttempted}
                className="rounded bg-blue-700 px-4 py-2 text-white disabled:opacity-50"
              >
                Publicar política deshabilitada
              </button>
            </div>
          )}
        </section>
      )}
      <p role="status" aria-live="polite">
        {message}
      </p>
    </main>
  );
}
