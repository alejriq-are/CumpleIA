"use client";
import { useState, useRef, useEffect } from "react";
import type { Dossier } from "@/lib/api/mvp-dossier";
import { downloadPilotAct } from "@/lib/licitud/pilot-act";
import {
  pilotReferences,
  pilotScenario,
  SIMULATION_WATERMARK,
  type PilotForm,
  type PilotResult,
} from "@/lib/api/pilot-preparation";
export type PilotPrepare = (packet: Dossier, form: PilotForm) => Promise<PilotResult>;
export function PilotPreparationPanel({
  packet,
  prepare,
}: {
  packet: Dossier;
  prepare: PilotPrepare;
}) {
  const [form, setForm] = useState<PilotForm>({
    act_reference: "SIMULADA-PILOTO-ACTA-001",
    designation_reference: "SIMULADA-PILOTO-DES-001",
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
      <p className="rounded border-2 border-red-700 p-3 font-bold">{SIMULATION_WATERMARK}</p>
      <p>
        {pilotScenario.company.name} · RUT de prueba {pilotScenario.company.test_rut}.{" "}
        {pilotScenario.company.contact}
      </p>
      <p>
        {pilotScenario.person.name} · {pilotScenario.person.position}. Fecha de designación
        simulada: {pilotScenario.designation.test_date}.
      </p>
      <p>
        Escenario de prueba; no identifica a la organización ni persona real de la sesión. Revisión
        jurídica pendiente / no realizada por defecto.
      </p>
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
          {(["act_reference", "designation_reference"] as const).map((k) => (
            <label key={k} className="block">
              {k === "act_reference"
                ? "Referencia del acta simulada"
                : "Referencia de designación simulada"}
              <input
                aria-label={
                  k === "act_reference"
                    ? "Referencia del acta simulada"
                    : "Referencia de designación simulada"
                }
                required
                pattern="SIMULADA-[A-Z0-9][A-Z0-9-]*"
                maxLength={128}
                value={form[k]}
                onChange={(e) => {
                  setResult(null);
                  setForm({ ...form, [k]: e.target.value });
                }}
                className="block w-full rounded border p-2"
              />
            </label>
          ))}
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
                maxLength={128}
                pattern="SIMULADA-[A-Z0-9][A-Z0-9-]*"
                placeholder="SIMULADA-PILOTO-..."
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
          <p>{result.watermark}</p>
          <p>
            Revisión:{" "}
            {result.legal_review_status === "pendiente_no_realizada"
              ? "pendiente / no realizada"
              : "simulada, sin valor jurídico"}
            .
          </p>
          <button type="button" onClick={() => downloadPilotAct(result, "html")}>
            Descargar acta simulada HTML
          </button>
          <button type="button" onClick={() => downloadPilotAct(result, "json")}>
            Descargar acta simulada JSON
          </button>
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
