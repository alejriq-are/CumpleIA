"use client";
import { useState, useRef, useEffect } from "react";
import type { Dossier } from "@/lib/api/mvp-dossier";
import { pilotReferences, type PilotForm, type PilotResult } from "@/lib/api/pilot-preparation";
export type PilotPrepare = (packet: Dossier, form: PilotForm) => Promise<PilotResult>;
export function PilotPreparationPanel({
  packet,
  prepare,
}: {
  packet: Dossier;
  prepare: PilotPrepare;
}) {
  const [form, setForm] = useState<PilotForm>({
    review_decision: "pendiente",
    review_reference: null,
    environment_reference: null,
    access_reference: null,
    restore_reference: null,
    retention_reference: null,
    support_reference: null,
    incident_reference: null,
  });
  const [fictitious, setFictitious] = useState(false),
    [busy, setBusy] = useState(false),
    [result, setResult] = useState<PilotResult | null>(null),
    [error, setError] = useState("");
  const running = useRef(false),
    alive = useRef(false);
  useEffect(() => {
    alive.current = true;
    return () => {
      alive.current = false;
    };
  }, []);
  async function submit() {
    if (running.current || !fictitious) return;
    running.current = true;
    setBusy(true);
    setResult(null);
    setError("");
    try {
      const r = await prepare(packet, form);
      if (alive.current) setResult(r);
    } catch {
      if (alive.current)
        setError(
          "Preparación rechazada: revisa facultad y expediente vigentes. Conservamos referencias."
        );
    } finally {
      running.current = false;
      if (alive.current) setBusy(false);
    }
  }
  return (
    <section aria-label="Preparación ficticia del piloto" className="space-y-3 rounded border p-3">
      <h3>Preparación ficticia del piloto</h3>
      <p>
        Las referencias aportadas son declaraciones de prueba, no actas verificadas. No se registran
        decisiones reales ni se libera el MVP. Requiere facultad ficticia explícita vigente.
      </p>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          void submit();
        }}
      >
        <fieldset disabled={busy} className="space-y-3">
          <label>
            <input
              type="checkbox"
              checked={fictitious}
              onChange={(e) => setFictitious(e.target.checked)}
            />{" "}
            Declaro referencias ficticias para el piloto
          </label>
          <label className="block">
            Decisión de revisión ficticia
            <select
              aria-label="Decisión de revisión ficticia"
              value={form.review_decision}
              onChange={(e) => {
                setResult(null);
                setForm({
                  ...form,
                  review_decision: e.target.value as PilotForm["review_decision"],
                });
              }}
            >
              <option value="pendiente">Pendiente</option>
              <option value="acepta">Acepta para la simulación</option>
              <option value="rechaza">Rechaza</option>
              <option value="requiere_cambios">Requiere cambios</option>
            </select>
          </label>
          {Object.entries(pilotReferences).map(([k, label]) => (
            <label key={k} className="block">
              {label}
              <input
                aria-label={label}
                className="block w-full rounded border p-2"
                value={form[k as keyof typeof pilotReferences] ?? ""}
                maxLength={1000}
                onChange={(e) => {
                  setResult(null);
                  setForm({ ...form, [k]: e.target.value });
                }}
              />
            </label>
          ))}
          <button type="submit" disabled={!fictitious || busy}>
            Validar preparación ficticia
          </button>
        </fieldset>
      </form>
      {error && <p role="alert">{error}</p>}
      {result && (
        <div role="status">
          <p>
            {result.preparation_complete
              ? "Referencias de prueba completas; evidencia no verificada."
              : "Faltan referencias o revisión de prueba."}
          </p>
          <ul>
            {result.missing.map((x) => (
              <li key={x}>{x}</li>
            ))}
          </ul>
          <p>
            Simulación no registrada. Aceptación real pendiente; datos reales y EIPD bloqueados.
          </p>
        </div>
      )}
    </section>
  );
}
