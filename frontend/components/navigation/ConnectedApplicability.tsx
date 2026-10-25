"use client";
import { useEffect, useId, useRef, useState } from "react";
import { navigationApi, type Applicability, type Determination } from "@/lib/api/navigation";
import { sessionToken } from "@/components/licitud/LicitudWorkspace";
import { navigationReadError } from "./connected-navigation";
export type ApplicabilityLoadState = { loading: boolean; error: string };
const pending: Determination = { state: "pendiente", reason: "" };
export const determinationLabels = {
  pendiente: "Pendiente de analizar",
  corresponde: "Corresponde",
  no_corresponde: "No corresponde",
  informacion_insuficiente: "Información insuficiente",
};
export function ConnectedApplicability({
  organizationId,
  treatmentId,
  assessmentId,
  readOnly,
  onSaved,
  onDirty,
  onLoadState,
  token = sessionToken,
  refreshVersion = 0,
}: {
  organizationId: string;
  treatmentId: string;
  assessmentId: string;
  readOnly: boolean;
  onSaved: (v: Applicability) => void;
  onDirty: (v: boolean) => void;
  onLoadState?: (v: ApplicabilityLoadState) => void;
  token?: () => Promise<string>;
  refreshVersion?: number;
}) {
  const id = useId();
  const editingHelpId = `${id}-editing-help`;
  const saveHelpId = `${id}-save-help`;
  const [manualVersion, setManualVersion] = useState(0);
  const [loading, setLoading] = useState(true);
  const [saved, setSaved] = useState<Applicability | null>(null);
  const [eipd, setEipd] = useState(pending);
  const [infancia, setInfancia] = useState(pending);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const [fiction, setFiction] = useState(false);
  const dirty =
    !!saved &&
    (JSON.stringify(eipd) !== JSON.stringify(saved.eipd) ||
      JSON.stringify(infancia) !== JSON.stringify(saved.infancia));
  const dirtyRef = useRef(dirty);
  dirtyRef.current = dirty;
  useEffect(() => {
    onDirty(dirty);
  }, [dirty, onDirty]);
  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    onLoadState?.({ loading: true, error: "" });
    (async () => {
      try {
        const v = await navigationApi.get(
          { token: await token(), organizationId, treatmentId },
          assessmentId
        );
        if (active) {
          setSaved(v);
          if (!dirtyRef.current) {
            setEipd(v.eipd);
            setInfancia(v.infancia);
          }
          onSaved(v);
          onLoadState?.({ loading: false, error: "" });
        }
      } catch (e) {
        if (active) {
          const message = navigationReadError(e, "No se pudo consultar la determinación.");
          setError(message);
          onLoadState?.({ loading: false, error: message });
        }
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => {
      active = false;
    };
  }, [
    organizationId,
    treatmentId,
    assessmentId,
    token,
    onSaved,
    onLoadState,
    refreshVersion,
    manualVersion,
  ]);
  async function save() {
    if (!saved) return;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const v = await navigationApi.save(
        { token: await token(), organizationId, treatmentId },
        assessmentId,
        {
          data_kind: "ficticios",
          request_id: crypto.randomUUID(),
          expected_revision: saved.revision,
          context_hash: saved.context_hash,
          eipd,
          infancia,
        }
      );
      setSaved(v);
      onSaved(v);
      setNotice("Determinación guardada en el servidor.");
      setFiction(false);
    } catch (e) {
      setError(e instanceof Error ? e.message : "No se pudo guardar.");
    } finally {
      setBusy(false);
    }
  }
  const valid = [eipd, infancia].every((v) => v.state === "pendiente" || v.reason.trim());
  const editingHelp = readOnly
    ? "Tu rol permite solo consulta: puedes ver la determinación, pero no modificarla ni guardarla."
    : saved?.editable === false
      ? "El servidor indica que esta evaluación es de solo consulta. La determinación solo puede editarse mientras la evaluación está en borrador."
      : busy
        ? "Guardando la determinación. Espera a que termine la operación."
        : loading
          ? "Consultando la determinación. Espera a que termine la consulta antes de editar o guardar."
          : !saved
            ? "No hay una determinación disponible. Reintenta la consulta antes de editar o guardar."
            : "";
  const missing = [
    eipd.state !== "pendiente" && !eipd.reason.trim() ? "fundamento sobre EIPD" : "",
    infancia.state !== "pendiente" && !infancia.reason.trim()
      ? "fundamento sobre infancia y adolescencia"
      : "",
    !fiction ? "declaración de datos ficticios" : "",
  ].filter(Boolean);
  const saveHelp = missing.length
    ? `Para guardar, completa: ${missing.join("; ")}.`
    : "Requisitos completos. Puedes guardar la determinación.";
  const saveDescriptionId = editingHelp ? editingHelpId : saveHelpId;
  return (
    <div className="space-y-5">
      <h2 className="text-xl font-bold">Determinar aplicabilidad</h2>
      <p>
        Registra por separado si corresponde EIPD e infancia y adolescencia. Los accesos se
        habilitan después de guardar. No constituye aprobación ni activa EIPD.
      </p>
      <p className="text-sm text-slate-600">
        Esta determinación corresponde al alcance guardado en la evaluación. Editar el RAT no
        sustituye automáticamente ese alcance; revisa su asociación antes de continuar.
      </p>
      {editingHelp && (
        <p
          id={editingHelpId}
          role={loading || busy ? "status" : undefined}
          className="rounded border border-blue-200 bg-blue-50 p-3"
        >
          {editingHelp}
        </p>
      )}
      {saved && !saved.current && saved.revision > 0 && (
        <p role="status" className="rounded border border-amber-400 bg-amber-50 p-3">
          El alcance asociado cambió. Revisa y guarda nuevamente la determinación; los antecedentes
          anteriores se conservan.
        </p>
      )}
      {(
        [
          ["EIPD", eipd, setEipd],
          ["infancia y adolescencia", infancia, setInfancia],
        ] as const
      ).map(([label, value, set]) => (
        <fieldset
          key={label}
          aria-describedby={editingHelp ? editingHelpId : undefined}
          disabled={readOnly || saved?.editable === false || busy || loading || !saved}
          className="space-y-3 rounded-lg border p-4"
        >
          <legend className="font-bold">{label}</legend>
          <label className="block">
            ¿Corresponde documentar {label}?
            <select
              aria-label={`¿Corresponde documentar ${label}?`}
              aria-describedby={editingHelp ? editingHelpId : undefined}
              className="mt-2 block w-full rounded border p-3"
              value={value.state}
              onChange={(e) => {
                set({ ...value, state: e.target.value as Determination["state"] });
                setNotice("");
              }}
            >
              {Object.entries(determinationLabels).map(([key, text]) => (
                <option key={key} value={key}>
                  {text}
                </option>
              ))}
            </select>
          </label>
          <label className="block">
            Fundamento sobre {label}
            <textarea
              aria-label={`Fundamento sobre ${label}`}
              aria-describedby={editingHelp ? editingHelpId : undefined}
              className="mt-2 block w-full rounded border p-3"
              rows={4}
              value={value.reason}
              onChange={(e) => {
                set({ ...value, reason: e.target.value });
                setNotice("");
              }}
            />
          </label>
        </fieldset>
      ))}
      <button
        className="rounded border p-3"
        disabled={busy || loading}
        onClick={() => setManualVersion((v) => v + 1)}
      >
        Actualizar estado guardado sin descartar el borrador
      </button>
      {error && (
        <p role="alert" className="rounded bg-red-50 p-3 text-red-800">
          {error}
        </p>
      )}
      <p>
        Contrasta infancia con el alcance del RAT. La presencia de menores no determina por sí sola
        la necesidad de una EIPD. Cambiar esta determinación conserva documentos y revisiones
        previos.
      </p>
      {dirty && (
        <p className="rounded bg-amber-50 p-3">
          Cambios sin guardar. Se conservan al navegar durante esta visita.
        </p>
      )}
      <label className="flex gap-3">
        <input
          type="checkbox"
          aria-describedby={saveDescriptionId}
          checked={fiction}
          onChange={(e) => setFiction(e.target.checked)}
          disabled={readOnly || busy}
        />
        Declaro que esta prueba utiliza únicamente datos ficticios.
      </label>
      {notice && (
        <p role="status" className="rounded bg-teal-50 p-3">
          {notice}
        </p>
      )}
      {!editingHelp && (
        <p id={saveHelpId} aria-live="polite" className="text-sm text-slate-700">
          {saveHelp}
        </p>
      )}
      <button
        aria-describedby={saveDescriptionId}
        disabled={
          readOnly || saved?.editable === false || busy || loading || !saved || !valid || !fiction
        }
        onClick={save}
        className="rounded bg-blue-800 px-4 py-3 font-semibold text-white disabled:opacity-50"
      >
        {busy ? "Guardando…" : "Guardar determinación"}
      </button>
      {saved && (
        <details>
          <summary>Historial de determinaciones ({saved.history.length})</summary>
          <ul className="space-y-2">
            {saved.history.map((v) => (
              <li key={v.revision}>
                Versión {v.revision} · {v.created_at} · EIPD: {determinationLabels[v.eipd.state]} ·
                Infancia: {determinationLabels[v.infancia.state]}
                <p>{v.eipd.reason}</p>
                <p>{v.infancia.reason}</p>
              </li>
            ))}
          </ul>
        </details>
      )}
    </div>
  );
}
