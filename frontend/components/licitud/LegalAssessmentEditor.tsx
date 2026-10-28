"use client";
import { useWorkState, type WorkReporter } from "@/components/navigation/work-unit-state";
import { useEffect, useRef, useState } from "react";
import { licitudApi, legalBases, legalBasisHelp, type Assessment } from "@/lib/api/licitud";
import { SaveFeedback } from "./SaveFeedback";
import { sessionToken } from "./LicitudWorkspace";
import { liaFields } from "@/lib/licitud/lia-fields";
function section(doc: Record<string, unknown> | null, key: string): Record<string, unknown> {
  const value = doc?.[key];
  return value && typeof value === "object" && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : {};
}
export function LegalAssessmentEditor({
  organizationId,
  treatmentId,
  assessmentId,
  readOnly,
  token = sessionToken,
  onLoaded,
  onSaved,
  onDirty,
  onWorkState,
}: {
  organizationId: string;
  treatmentId: string;
  assessmentId: string;
  readOnly: boolean;
  token?: () => Promise<string>;
  onLoaded?: (row: Assessment) => void;
  onSaved?: (row: Assessment) => void;
  onDirty?: (dirty: boolean) => void;
  onWorkState?: WorkReporter;
}) {
  const [row, setRow] = useState<Assessment | null>(null),
    [basis, setBasis] = useState(""),
    [justification, setJustification] = useState(""),
    [values, setValues] = useState<Record<string, string>>({}),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [message, setMessage] = useState("");
  const running = useRef(false);
  const [baseline, setBaseline] = useState("");
  const fingerprint = JSON.stringify([basis, justification, values]);
  const dirty = Boolean(row && baseline && fingerprint !== baseline);
  useWorkState(onWorkState, {
    loaded: !!row,
    loading: !row && !error,
    saving: busy,
    dirty,
    saved: !!message,
    error: !!error,
  });
  useEffect(() => {
    onDirty?.(dirty || busy);
  }, [dirty, busy, onDirty]);
  useEffect(() => {
    let active = true;
    setRow(null);
    setError("");
    setMessage("");
    (async () => {
      try {
        const out = await licitudApi.get(
          { token: await token(), organizationId, treatmentId },
          assessmentId
        );
        if (active) {
          setRow(out);
          setBasis(out.legal_basis ?? "");
          setJustification(out.justification ?? "");
          const loaded = Object.fromEntries(
            liaFields.map(([group, key]) => [
              group + "." + key,
              String(section(out.lia_assessment, group)[key] ?? ""),
            ])
          );
          setValues(loaded);
          setBaseline(JSON.stringify([out.legal_basis ?? "", out.justification ?? "", loaded]));
          onLoaded?.(out);
        }
      } catch (e) {
        if (active) setError(e instanceof Error ? e.message : "No se pudo cargar la evaluación.");
      }
    })();
    return () => {
      active = false;
    };
  }, [organizationId, treatmentId, assessmentId, token, onLoaded]);
  const disabled = readOnly || row?.status !== "borrador" || busy;
  async function save(e: React.FormEvent) {
    e.preventDefault();
    if (!row || disabled || running.current) return;
    running.current = true;
    setBusy(true);
    setMessage("");
    setError("");
    try {
      let lia: Record<string, unknown> | undefined;
      if (basis === "interes_legitimo_art13d") {
        lia = { ...(row.lia_assessment ?? {}), schema_version: 1 };
        for (const [group, key] of liaFields) {
          lia[group] = { ...section(lia, group), [key]: values[group + "." + key] || null };
        }
      }
      const out = await licitudApi.save(
        { token: await token(), organizationId, treatmentId },
        assessmentId,
        {
          legal_basis: basis || null,
          justification: justification || null,
          ...(lia ? { lia_assessment: lia } : {}),
        }
      );
      setRow(out);
      setBaseline(fingerprint);
      onSaved?.(out);
      setMessage(
        "Borrador guardado. Los cambios se guardaron correctamente en el servidor. La evaluación continúa en borrador, pendiente de revisión jurídica."
      );
    } catch (e) {
      setError(
        (e instanceof Error ? e.message : "No se pudo guardar.") +
          " Conservamos tus cambios en el formulario. Si no recibiste respuesta, recarga para verificar el estado guardado."
      );
    } finally {
      running.current = false;
      setBusy(false);
    }
  }
  return (
    <section className="space-y-4 rounded border p-4">
      <h2 className="text-xl font-semibold">Evaluación y fundamento</h2>
      {!row && error && <SaveFeedback error={error} />}
      {row ? (
        <form onSubmit={save} className="space-y-4">
          <p>
            {row.purpose_snapshot} — versión {row.version} ({row.status})
          </p>
          <p>Contenido cargado del servidor. Guardar no equivale a aprobación jurídica.</p>
          <p>
            Prueba con datos ficticios. Esta pantalla guarda borradores; no confirma ni activa EIPD.
          </p>
          <label className="block">
            Base de licitud propuesta
            <select
              className="block w-full rounded border p-2"
              disabled={disabled}
              aria-label="Base de licitud propuesta"
              aria-describedby="legal-basis-help"
              value={basis}
              onChange={(e) => {
                setBasis(e.target.value);
                setMessage("");
              }}
            >
              <option value="">Pendiente de definir</option>
              {legalBases.map(([code, label]) => (
                <option key={code} value={code}>
                  {label}
                </option>
              ))}
            </select>
          </label>
          <p id="legal-basis-help" className="text-sm" aria-live="polite">
            {legalBasisHelp[basis] ?? "Revisa la base propuesta y su fundamento antes de guardar."}
          </p>
          <label className="block">
            Fundamento
            <textarea
              className="block w-full rounded border p-2"
              disabled={disabled}
              aria-label="Fundamento"
              value={justification}
              onChange={(e) => {
                setJustification(e.target.value);
                setMessage("");
              }}
            />
          </label>
          {basis === "interes_legitimo_art13d" && (
            <fieldset disabled={disabled} className="space-y-3">
              <legend className="font-semibold">LIA: análisis en borrador</legend>
              <p>
                Registra los análisis principales. Esto no completa automáticamente todos los
                requisitos de la LIA.
              </p>
              {liaFields.map(([group, key, label]) => (
                <label key={key} className="block">
                  {label}
                  <textarea
                    className="block w-full rounded border p-2"
                    aria-label={label}
                    value={values[group + "." + key] ?? ""}
                    onChange={(e) => {
                      setValues((v) => ({ ...v, [group + "." + key]: e.target.value }));
                      setMessage("");
                    }}
                  />
                </label>
              ))}
            </fieldset>
          )}
          <SaveFeedback
            error={error}
            message={message}
            busy={busy}
            dirty={dirty}
            dirtyMessage="Cambios sin guardar. Se conservan al cambiar de pestaña; guarda antes de preparar un documento."
          />
          {row.status !== "borrador" || readOnly ? (
            <p>Consulta de solo lectura.</p>
          ) : (
            <button
              className="rounded bg-blue-700 px-4 py-2 text-white disabled:opacity-50"
              disabled={busy}
            >
              {busy ? "Guardando…" : "Guardar borrador"}
            </button>
          )}
        </form>
      ) : (
        !error && <p role="status">Cargando evaluación…</p>
      )}
    </section>
  );
}
