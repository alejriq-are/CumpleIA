"use client";
import { useEffect, useState } from "react";
import { licitudApi, legalBases, type Assessment } from "@/lib/api/licitud";
import { sessionToken } from "./LicitudWorkspace";
const fields = [
  ["purpose_and_interest", "legitimate_interest", "Interés legítimo declarado"],
  ["necessity", "necessity_analysis", "Análisis de necesidad"],
  ["necessity", "alternatives_analysis", "Alternativas consideradas"],
  ["nature_and_scope", "volume_and_scope", "Naturaleza y alcance"],
  ["reasonable_expectations", "expectations_analysis", "Expectativas de los titulares"],
  ["impact", "impact_analysis", "Impactos en los titulares"],
  ["safeguards", "safeguards_analysis", "Medidas de protección"],
  ["transparency_and_opposition", "opposition_procedure", "Procedimiento de oposición"],
  ["conclusion", "balancing_summary", "Balance y fundamentos pendientes de revisión"],
] as const;
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
}: {
  organizationId: string;
  treatmentId: string;
  assessmentId: string;
  readOnly: boolean;
  token?: () => Promise<string>;
}) {
  const [row, setRow] = useState<Assessment | null>(null),
    [basis, setBasis] = useState(""),
    [justification, setJustification] = useState(""),
    [values, setValues] = useState<Record<string, string>>({}),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [message, setMessage] = useState("");
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
          setValues(
            Object.fromEntries(
              fields.map(([group, key]) => [
                group + "." + key,
                String(section(out.lia_assessment, group)[key] ?? ""),
              ])
            )
          );
        }
      } catch (e) {
        if (active) setError(e instanceof Error ? e.message : "No se pudo cargar la evaluación.");
      }
    })();
    return () => {
      active = false;
    };
  }, [organizationId, treatmentId, assessmentId, token]);
  const disabled = readOnly || row?.status !== "borrador" || busy;
  async function save(e: React.FormEvent) {
    e.preventDefault();
    if (!row || disabled) return;
    setBusy(true);
    setMessage("");
    setError("");
    try {
      let lia: Record<string, unknown> | undefined;
      if (basis === "interes_legitimo_art13d") {
        lia = { ...(row.lia_assessment ?? {}), schema_version: 1 };
        for (const [group, key] of fields) {
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
      setMessage(
        "Borrador guardado. La documentación sigue pendiente de revisión jurídica. Recarga el expediente para actualizar los diagnósticos y vínculos de los paneles inferiores."
      );
    } catch (e) {
      setError(
        (e instanceof Error ? e.message : "No se pudo guardar.") +
          " Conservamos tus cambios en el formulario. Si no recibiste respuesta, recarga para verificar el estado guardado."
      );
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="space-y-4 rounded border p-4">
      <h2 className="text-xl font-semibold">Evaluación y fundamento</h2>
      {error && <p role="alert">{error}</p>}
      {message && <p role="status">{message}</p>}
      {row ? (
        <form onSubmit={save} className="space-y-4">
          <p>
            {row.purpose_snapshot} — versión {row.version} ({row.status})
          </p>
          <p>
            Prueba con datos ficticios. Esta pantalla guarda borradores; no confirma ni activa EIPD.
          </p>
          <label className="block">
            Base de licitud propuesta
            <select
              className="block w-full rounded border p-2"
              disabled={disabled}
              aria-label="Base de licitud propuesta"
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
              {fields.map(([group, key, label]) => (
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
