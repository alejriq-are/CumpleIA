"use client";
import { useEffect, useRef, useState } from "react";
import { api, type TreatmentDetailOut } from "@/lib/api/client";
import {
  scopeReviewApi,
  type Assessment,
  type AssessmentScope,
  type ScopeReview,
} from "@/lib/api/licitud";
import { useWorkState, type WorkReporter } from "@/components/navigation/work-unit-state";
import { documentDisclosureClass, documentNavigationButtonClass } from "./document-focus";
import { DossierDocumentView } from "./DossierDocumentView";
import { navigationReadError } from "@/components/navigation/connected-navigation";
import { requiresSignIn } from "@/lib/auth/session";
import { SessionRecovery } from "@/components/navigation/SessionRecovery";

function selection(row: Assessment): AssessmentScope {
  return {
    data_category_codes:
      row.rat_context_snapshot?.data_categories?.map((v) => v.category_code) ?? [],
    data_subject_codes: row.rat_context_snapshot?.data_subjects?.map((v) => v.category_code) ?? [],
  };
}
// Presentation only: JSON/JSONB key order must not dictate comparison order.
const scopeFieldOrder = [
  "category_code",
  "category_name",
  "includes_children",
  "includes_adolescents",
  "is_vulnerable_group",
  "includes_sensitive_data",
  "includes_biometrics",
  "notes",
];
function orderedSnapshot(value: unknown): unknown {
  if (Array.isArray(value)) {
    const items = [...value];
    if (items.every((v) => v && typeof v === "object" && "category_code" in v))
      items.sort((a, b) => String(a.category_code).localeCompare(String(b.category_code), "es"));
    return items.map(orderedSnapshot);
  }
  if (value && typeof value === "object")
    return Object.fromEntries(
      Object.entries(value)
        .sort(([a], [b]) => {
          const rank = (key: string) => {
            const i = scopeFieldOrder.indexOf(key);
            return i < 0 ? scopeFieldOrder.length : i;
          };
          return rank(a) - rank(b) || a.localeCompare(b, "es");
        })
        .map(([key, item]) => [key, orderedSnapshot(item)])
    );
  return value;
}
function Snapshot({ value }: { value: Record<string, unknown> }) {
  return (
    <DossierDocumentView
      document={{
        kind: "rat",
        status: "disponible",
        version: 1,
        coverage: "",
        content_hash: null,
        organization_acceptance: "sin_flujo",
        acceptance_events: [],
        content: orderedSnapshot(value) as Record<string, unknown>,
      }}
    />
  );
}
export function AssessmentScopeReview({
  row,
  readOnly,
  token,
  onSaved,
  onDirty,
  onWorkState,
  onEditRat,
  onDetermine,
}: {
  row: Assessment;
  readOnly: boolean;
  token: () => Promise<string>;
  onSaved: (row: Assessment) => void;
  onDirty: (dirty: boolean) => void;
  onWorkState?: WorkReporter;
  onEditRat?: (section: string) => void;
  onDetermine?: () => void;
}) {
  const [rat, setRat] = useState<TreatmentDetailOut | null>(null);
  const [chosen, setChosen] = useState(() => selection(row));
  const [review, setReview] = useState<ScopeReview | null>(null);
  const [reason, setReason] = useState("");
  const [fiction, setFiction] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [authRequired, setAuthRequired] = useState(false);
  const [message, setMessage] = useState("");
  const dirty = !!reason || JSON.stringify(chosen) !== JSON.stringify(selection(row));
  const dirtyRef = useRef(dirty);
  dirtyRef.current = dirty;
  const savedHash = row.rat_context_hash;
  useEffect(() => {
    if (!dirtyRef.current) setChosen(selection(row));
    setReview(null);
    // Other editors can update the stored assessment while this pane remains mounted.
  }, [savedHash]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => onDirty(dirty || busy), [dirty, busy, onDirty]);
  useWorkState(onWorkState, { loaded: !!rat, loading: busy, dirty, error: !!error });
  const credentials = async () => ({
    token: await token(),
    organizationId: row.organization_id,
    treatmentId: row.treatment_id,
  });
  async function consult() {
    setBusy(true);
    setError("");
    setAuthRequired(false);
    setReview(null);
    setMessage("");
    try {
      setRat(await api.rat.getTreatment(await token(), row.organization_id, row.treatment_id));
    } catch (e) {
      setError(
        navigationReadError(
          e,
          "No se pudo consultar o actualizar el alcance. Tus cambios se conservan."
        )
      );
      setAuthRequired(requiresSignIn(e));
    } finally {
      setBusy(false);
    }
  }
  async function compare() {
    setBusy(true);
    setError("");
    setAuthRequired(false);
    setMessage("");
    setReview(null);
    setFiction(false);
    try {
      setReview(await scopeReviewApi.preview(await credentials(), row.id, chosen));
    } catch (e) {
      setError(
        navigationReadError(
          e,
          "No se pudo consultar o actualizar el alcance. Tus cambios se conservan."
        )
      );
      setAuthRequired(requiresSignIn(e));
    } finally {
      setBusy(false);
    }
  }
  const request = useRef<string | null>(null);
  async function apply() {
    if (!review || !fiction || !reason.trim()) return;
    setBusy(true);
    setError("");
    setAuthRequired(false);
    request.current ??= crypto.randomUUID();
    try {
      const value = await scopeReviewApi.apply(await credentials(), row.id, {
        scope: chosen,
        review_hash: review.review_hash,
        reason: reason.trim(),
        request_id: request.current,
        data_kind: "ficticios",
      });
      onSaved(value);
      setChosen(selection(value));
      setReason("");
      setFiction(false);
      setReview(null);
      request.current = null;
      setMessage(
        "Alcance actualizado en esta evaluación. Revisa y guarda nuevamente las determinaciones de EIPD e infancia. Sus antecedentes y los documentos anteriores se conservan."
      );
    } catch (e) {
      setError(
        navigationReadError(
          e,
          "No se pudo consultar o actualizar el alcance. Tus cambios se conservan."
        )
      );
      setAuthRequired(requiresSignIn(e));
    } finally {
      setBusy(false);
    }
  }
  function change(key: keyof AssessmentScope, code: string, checked: boolean) {
    setChosen((v) => ({
      ...v,
      [key]: checked ? [...v[key], code] : v[key].filter((c) => c !== code),
    }));
    setReview(null);
    setFiction(false);
    request.current = null;
    setMessage("");
  }
  return (
    <section
      aria-label="Revisar alcance asociado"
      className="space-y-4 rounded border border-blue-200 p-4"
    >
      <h3 className="font-semibold">Revisar y actualizar el alcance de esta evaluación</h3>
      <p>
        Si ahora se incluyen hijos de clientes, puedes incorporar adultos y menores en el mismo
        tratamiento. Revisa titulares, edades en sus notas, categorías de datos y finalidad en el
        RAT. El nombre del tratamiento no determina la aplicabilidad.
      </p>
      <p>
        Guardar el RAT no incorpora automáticamente sus cambios aquí. Compara y actualiza
        expresamente este alcance antes de revisar las determinaciones. Si necesitas evaluar otra
        finalidad, crea otra evaluación desde Evaluaciones y creación de borrador.
      </p>
      {onEditRat && (
        <div className="flex flex-wrap gap-2">
          {[
            ["titulares", "Revisar titulares y edades en el RAT"],
            ["categorias", "Revisar categorías de datos en el RAT"],
            ["finalidades", "Revisar finalidades en el RAT"],
          ].map(([section, label]) => (
            <button
              key={section}
              type="button"
              className={documentNavigationButtonClass}
              onClick={() => onEditRat(section)}
            >
              {label}
            </button>
          ))}
        </div>
      )}
      <button
        type="button"
        className={documentNavigationButtonClass}
        disabled={busy}
        onClick={consult}
      >
        Consultar RAT actual para revisar alcance
      </button>
      {rat && (
        <fieldset disabled={busy || readOnly || row.status !== "borrador"} className="space-y-3">
          <legend className="font-semibold">
            Selecciona los datos y titulares para la misma finalidad
          </legend>
          <p>Finalidad guardada: {row.purpose_snapshot}</p>
          <p>
            Consultar el RAT no guarda esta selección. Los datos de otras finalidades no se
            incorporan automáticamente.
          </p>
          <fieldset>
            <legend>Categorías de datos del RAT actual</legend>
            {rat.data_categories.map((v) => (
              <label key={v.category_code} className="block">
                <input
                  type="checkbox"
                  checked={chosen.data_category_codes.includes(v.category_code)}
                  onChange={(e) => change("data_category_codes", v.category_code, e.target.checked)}
                />{" "}
                {v.category_name}
              </label>
            ))}
          </fieldset>
          <fieldset>
            <legend>Titulares del RAT actual</legend>
            {rat.data_subjects.map((v) => (
              <div key={v.category_code} className="mb-3 rounded border border-gray-200 p-3">
                <label className="block font-medium">
                  <input
                    type="checkbox"
                    checked={chosen.data_subject_codes.includes(v.category_code)}
                    onChange={(e) =>
                      change("data_subject_codes", v.category_code, e.target.checked)
                    }
                  />{" "}
                  {v.category_name}
                </label>
                <p>
                  Incluye niños y niñas: {v.includes_children ? "Sí" : "No"} · Incluye adolescentes:{" "}
                  {v.includes_adolescents ? "Sí" : "No"} · Grupo vulnerable:{" "}
                  {v.is_vulnerable_group ? "Sí" : "No"}
                </p>
                <p className="whitespace-pre-wrap break-words">
                  <span className="font-medium">
                    Notas sobre los titulares y edades (opcional):
                  </span>{" "}
                  {v.notes || "Sin notas registradas."}
                </p>
              </div>
            ))}
          </fieldset>
          {[
            ...chosen.data_category_codes.filter(
              (c) => !rat.data_categories.some((v) => v.category_code === c)
            ),
            ...chosen.data_subject_codes.filter(
              (c) => !rat.data_subjects.some((v) => v.category_code === c)
            ),
          ].length > 0 && (
            <div role="status">
              <p>
                Estos códigos anteriores ya no están en el RAT. Desmárcalos y elige los que
                correspondan al alcance actual.
              </p>
              {(["data_category_codes", "data_subject_codes"] as const).map((key) =>
                chosen[key]
                  .filter(
                    (c) =>
                      !(
                        key === "data_category_codes" ? rat.data_categories : rat.data_subjects
                      ).some((v) => v.category_code === c)
                  )
                  .map((code) => (
                    <label key={key + code} className="block">
                      <input type="checkbox" checked onChange={() => change(key, code, false)} />{" "}
                      {code} · retirado del RAT
                    </label>
                  ))
              )}
            </div>
          )}
          <button
            type="button"
            className={documentNavigationButtonClass}
            onClick={compare}
            disabled={!chosen.data_category_codes.length || !chosen.data_subject_codes.length}
          >
            Comparar alcance guardado y propuesto
          </button>
        </fieldset>
      )}
      {review && (
        <div className="space-y-3">
          <p role="status">
            {review.changed
              ? "El alcance propuesto difiere del guardado. Revisa las diferencias antes de actualizar."
              : "El alcance propuesto coincide con el guardado. No es necesario actualizarlo."}
          </p>
          <div className="grid gap-3 lg:grid-cols-2">
            <section aria-label="Alcance guardado">
              <h4 className="font-semibold">Alcance guardado en esta evaluación</h4>
              <Snapshot value={review.before} />
            </section>
            <section aria-label="Alcance propuesto">
              <h4 className="font-semibold">Alcance propuesto desde el RAT actual</h4>
              <Snapshot value={review.after} />
            </section>
          </div>
          <details>
            <summary className={documentDisclosureClass}>
              Historial de actualizaciones de alcance ({review.history.length})
            </summary>
            {review.history.map((v) => (
              <div key={v.revision} className="my-3 rounded border p-3">
                <p>
                  Revisión de alcance {v.revision} · {v.created_at} · Persona (identificador):{" "}
                  {v.created_by}
                </p>
                <p>Motivo: {v.reason}</p>
                <details>
                  <summary className={documentDisclosureClass}>
                    Consultar alcance anterior y posterior
                  </summary>
                  <Snapshot value={v.before} />
                  <Snapshot value={v.after} />
                </details>
              </div>
            ))}
          </details>
          {review.changed && (
            <fieldset disabled={busy || readOnly || !review.editable} className="space-y-3">
              <label className="block">
                Motivo del cambio de alcance
                <textarea
                  className="mt-2 block w-full rounded border p-3"
                  value={reason}
                  maxLength={5000}
                  onChange={(e) => {
                    setReason(e.target.value);
                    request.current = null;
                  }}
                />
              </label>
              <label className="block">
                <input
                  type="checkbox"
                  checked={fiction}
                  onChange={(e) => setFiction(e.target.checked)}
                />{" "}
                Revisé la comparación y declaro datos ficticios para actualizar el alcance.
              </label>
              <p>
                Esta acción conserva el alcance anterior en el historial y actualiza la misma
                evaluación. No crea otra evaluación ni una versión documental. Las determinaciones
                anteriores quedan pendientes de revisión para el nuevo alcance; no se borran sus
                fundamentos, documentos, anexos ni revisiones.
              </p>
              <button
                type="button"
                className="bg-blue-800 text-white"
                disabled={!fiction || !reason.trim()}
                onClick={apply}
              >
                Actualizar alcance de esta evaluación
              </button>
            </fieldset>
          )}
        </div>
      )}
      {busy && <p role="status">Consultando o actualizando alcance…</p>}
      {error && (
        <div role="alert" className="rounded border border-red-200 bg-red-50 p-3">
          {error}
          <SessionRecovery required={authRequired} />
        </div>
      )}
      {message && (
        <p role="status" className="rounded border border-green-200 bg-green-50 p-3">
          {message}
        </p>
      )}
      {onDetermine && (
        <button type="button" className={documentNavigationButtonClass} onClick={onDetermine}>
          Volver a determinar aplicabilidad en esta evaluación
        </button>
      )}
    </section>
  );
}
