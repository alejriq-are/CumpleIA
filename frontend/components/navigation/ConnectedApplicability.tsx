"use client";
import { useWorkState, type WorkReporter } from "@/components/navigation/work-unit-state";
import { useEffect, useId, useRef, useState } from "react";
import { navigationApi, type Applicability, type Determination } from "@/lib/api/navigation";
import { ApiError } from "@/lib/api/client";
import { sessionToken } from "@/components/licitud/LicitudWorkspace";
import { navigationReadError } from "./connected-navigation";
import { connectedDestinations } from "./connected-destinations";
export type ApplicabilityLoadState = { loading: boolean; error: string };
const pending: Determination = { state: "pendiente", reason: "" };
export const determinationLabels = {
  pendiente: "Pendiente de analizar",
  corresponde: "Corresponde",
  no_corresponde: "No corresponde",
  informacion_insuficiente: "Información insuficiente",
};
function registrationDate(value: string) {
  const date = new Date(value);
  if (!value || Number.isNaN(date.getTime())) return "Fecha no disponible";
  return new Intl.DateTimeFormat("es-CL", {
    dateStyle: "long",
    hourCycle: "h23",
    ...(value.includes("T") ? { timeStyle: "short" as const } : {}),
    timeZone: value.includes("T") ? "America/Santiago" : "UTC",
  }).format(date);
}
export function ConnectedApplicability({
  organizationId,
  treatmentId,
  assessmentId,
  readOnly,
  onSaved,
  onDirty,
  onWorkState,
  onLoadState,
  onOpen,
  token = sessionToken,
  refreshVersion = 0,
}: {
  organizationId: string;
  treatmentId: string;
  assessmentId: string;
  readOnly: boolean;
  onSaved: (v: Applicability) => void;
  onDirty: (v: boolean) => void;
  onWorkState?: WorkReporter;
  onLoadState?: (v: ApplicabilityLoadState) => void;
  onOpen: (section: "eipd" | "infancia" | "revisar") => void;
  token?: () => Promise<string>;
  refreshVersion?: number;
}) {
  const id = useId();
  const editingHelpId = `${id}-editing-help`;
  const saveHelpId = `${id}-save-help`;
  const queryHelpId = `${id}-query-help`;
  const [manualVersion, setManualVersion] = useState(0);
  const [loading, setLoading] = useState(true);
  const [saved, setSaved] = useState<Applicability | null>(null);
  const [eipd, setEipd] = useState(pending);
  const [infancia, setInfancia] = useState(pending);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [queryNotice, setQueryNotice] = useState("");
  const [conflict, setConflict] = useState(false);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [fiction, setFiction] = useState(false);
  const dirty =
    !!saved &&
    (JSON.stringify(eipd) !== JSON.stringify(saved.eipd) ||
      JSON.stringify(infancia) !== JSON.stringify(saved.infancia));
  useWorkState(onWorkState, {
    loaded: !!saved,
    loading,
    saving: busy,
    dirty,
    saved: !!notice,
    error: !!error,
  });
  const dirtyRef = useRef(dirty);
  dirtyRef.current = dirty;
  useEffect(() => {
    onDirty(dirty);
  }, [dirty, onDirty]);
  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    setNotice("");
    setQueryNotice("");
    onLoadState?.({ loading: true, error: "" });
    (async () => {
      try {
        const v = await navigationApi.get(
          { token: await token(), organizationId, treatmentId },
          assessmentId
        );
        if (active) {
          const keepDraft = dirtyRef.current;
          setSaved(v);
          setConflict(false);
          if (manualVersion > 0) {
            setQueryNotice(
              keepDraft
                ? "Consulta completada. Tus cambios pendientes se conservaron; compara el estado guardado con tu borrador antes de guardar."
                : "Consulta completada. El formulario muestra la determinación consultada en el servidor."
            );
          }
          if (!keepDraft) {
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
    setQueryNotice("");
    setConflict(false);
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
      if (e instanceof ApiError && e.status === 409) {
        setConflict(true);
        setHistoryOpen(true);
      }
      setError(e instanceof Error ? e.message : "No se pudo guardar.");
    } finally {
      setBusy(false);
    }
  }
  const registration = saved?.history.find((entry) => entry.revision === saved.revision);
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
      {saved && (
        <section
          aria-label="Estado guardado y borrador de aplicabilidad"
          className="space-y-3 rounded-lg border border-slate-300 bg-white p-4"
        >
          <h3 className="font-bold">Última determinación consultada en el servidor</h3>
          {saved.revision > 0 ? (
            <div className="space-y-1 text-sm">
              <p>
                Revisión de aplicabilidad {saved.revision} ·{" "}
                {saved.current ? "Asociada al alcance actual" : "Requiere revisión del alcance"}
              </p>
              <p>
                Fecha de registro (Chile continental):{" "}
                {registration
                  ? registrationDate(registration.created_at)
                  : "Fecha no disponible"}{" "}
              </p>
              <p className="break-all">
                Registrada por (identificador): {registration?.created_by || "No disponible"}
              </p>
              <p>
                El servidor informa el identificador de la persona; no entrega su nombre en esta
                consulta.
              </p>
            </div>
          ) : (
            <p>Todavía no hay una determinación guardada para esta evaluación.</p>
          )}
          <p className={dirty ? "font-semibold text-amber-900" : "text-slate-700"}>
            {dirty
              ? "Tu borrador tiene cambios sin guardar. Los accesos dependen de la determinación guardada, no de estas ediciones."
              : saved.revision > 0
                ? "El formulario coincide con esta determinación consultada."
                : "Los valores del formulario son iniciales; aún no se han guardado."}
          </p>
          {(
            [
              ["eipd", "EIPD", eipd],
              ["infancia", "Infancia y adolescencia", infancia],
            ] as const
          ).map(([topic, label, draft]) => (
            <div key={topic} className="space-y-2 border-t border-slate-200 pt-3">
              <h4 className="font-semibold">{label}</h4>
              <div className={dirty ? "grid gap-3 md:grid-cols-2" : ""}>
                <div className="min-w-0 space-y-1 break-words">
                  <p className="font-semibold">
                    {saved.revision > 0 ? "Guardado en el servidor" : "Sin guardar en el servidor"}
                  </p>
                  <p>
                    <span className="font-semibold">
                      ¿Corresponde documentar{" "}
                      {topic === "eipd" ? "EIPD" : "infancia y adolescencia"}?:{" "}
                    </span>
                    {determinationLabels[saved[topic].state]}
                  </p>
                  {dirty && (
                    <div>
                      <p className="font-semibold">
                        Fundamento sobre {topic === "eipd" ? "EIPD" : "infancia y adolescencia"}:
                      </p>
                      <p className="whitespace-pre-wrap break-words">
                        {saved[topic].reason || "Sin fundamento registrado."}
                      </p>
                    </div>
                  )}
                </div>
                {dirty && (
                  <div className="min-w-0 space-y-1 rounded border border-amber-300 bg-amber-50 p-3 break-words">
                    <p className="font-semibold">Tu borrador en el formulario</p>
                    <p>
                      <span className="font-semibold">
                        ¿Corresponde documentar{" "}
                        {topic === "eipd" ? "EIPD" : "infancia y adolescencia"}?:{" "}
                      </span>
                      {determinationLabels[draft.state]}
                    </p>
                    <div>
                      <p className="font-semibold">
                        Fundamento sobre {topic === "eipd" ? "EIPD" : "infancia y adolescencia"}:
                      </p>
                      <p className="whitespace-pre-wrap break-words">
                        {draft.reason || "Sin fundamento escrito."}
                      </p>
                    </div>
                    <p className="text-sm">
                      {JSON.stringify(draft) === JSON.stringify(saved[topic])
                        ? "Sin diferencias en este tema."
                        : "Difiere de lo consultado en el servidor."}
                    </p>
                  </div>
                )}
              </div>
            </div>
          ))}
        </section>
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
                setQueryNotice("");
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
                setQueryNotice("");
              }}
            />
          </label>
        </fieldset>
      ))}
      <section
        aria-label="Consultar determinación guardada"
        className="space-y-3 rounded-lg border border-slate-300 bg-slate-50 p-4"
      >
        <button
          type="button"
          className="rounded border-2 border-blue-800 bg-white px-4 py-3 font-semibold text-blue-900 hover:bg-blue-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700 disabled:opacity-50"
          aria-describedby={queryHelpId}
          disabled={busy || loading}
          onClick={() => setManualVersion((v) => v + 1)}
        >
          {loading ? "Consultando determinación…" : "Consultar última determinación guardada"}
        </button>
        <p id={queryHelpId} className="text-sm text-slate-700">
          Consulta lo guardado en el servidor para esta evaluación y actualiza los accesos según ese
          estado. Conserva tus cambios pendientes y no guarda el formulario. No recarga el RAT ni
          sincroniza otras ventanas.
        </p>
        {queryNotice && (
          <p role="status" className="rounded border border-blue-200 bg-blue-50 p-3">
            {queryNotice}
          </p>
        )}
        {conflict && (
          <p className="font-semibold text-amber-900">
            El guardado fue rechazado. Conservamos tu borrador. Consulta la última determinación
            para comparar antes de volver a guardar.
          </p>
        )}
        {error && (
          <p role="alert" className="rounded bg-red-50 p-3 text-red-800">
            {error}
          </p>
        )}
      </section>
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
      {saved && !loading && (
        <section
          aria-label="Disponibilidad de formularios"
          aria-live="polite"
          className="space-y-3 rounded border border-blue-200 bg-blue-50 p-4"
        >
          <h3 className="font-bold">
            {saved.revision === 0
              ? "Sin determinación guardada"
              : "Accesos según la determinación guardada"}
          </h3>
          <ul className="space-y-4">
            {(
              [
                ["eipd", "EIPD"],
                ["infancia", "Infancia y adolescencia"],
              ] as const
            ).map(([topic, label]) => {
              const available = saved.current && saved[topic].state === "corresponde";
              const needsReview = !saved.current && saved.revision > 0;
              const action = readOnly || !saved.editable ? "Consultar" : "Completar";
              return (
                <li key={topic}>
                  <p className="font-semibold">
                    {label}: {determinationLabels[saved[topic].state]}
                  </p>
                  {available ? (
                    <button
                      type="button"
                      className="mt-2 rounded border border-blue-800 bg-white px-3 py-2 font-semibold text-blue-900"
                      onClick={() => onOpen(topic)}
                    >
                      {action} {topic === "eipd" ? "EIPD" : "infancia y adolescencia"}
                    </button>
                  ) : (
                    <p className="text-sm">
                      El formulario no está habilitado.{" "}
                      {needsReview
                        ? "La determinación guardada requiere revisión para el alcance asociado; revísala y guárdala nuevamente antes de continuar."
                        : saved[topic].state === "no_corresponde"
                          ? "La determinación guardada indica que no corresponde completarlo."
                          : saved[topic].state === "informacion_insuficiente"
                            ? "Falta información para determinar si corresponde completarlo."
                            : "La decisión está pendiente. Solo se habilita si guardas «Corresponde» con su fundamento."}
                    </p>
                  )}
                </li>
              );
            })}
          </ul>
          <p className="text-sm">
            Los documentos anteriores, si existen, se conservan y pueden consultarse en Revisar y
            decidir.
          </p>
          <button
            type="button"
            className="rounded border border-blue-800 bg-white px-3 py-2 text-blue-900"
            onClick={() => onOpen("revisar")}
          >
            Ir a {connectedDestinations.licitud.revisar}
          </button>
        </section>
      )}
      {!editingHelp && (
        <p id={saveHelpId} aria-live="polite" className="text-sm text-slate-700">
          {saveHelp}
        </p>
      )}
      {notice && (
        <p role="status" className="rounded border border-teal-300 bg-teal-50 p-3">
          {notice}
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
        <details open={historyOpen} onToggle={(e) => setHistoryOpen(e.currentTarget.open)}>
          <summary>Historial de determinaciones ({saved.history.length})</summary>
          <ul className="space-y-2">
            {saved.history.map((v) => (
              <li key={v.revision} className="space-y-1 rounded border p-3 break-words">
                <p className="font-semibold">
                  Revisión de aplicabilidad {v.revision} · {registrationDate(v.created_at)}
                </p>
                <p className="break-all">
                  Registrada por (identificador): {v.created_by || "No disponible"}
                </p>
                <p>EIPD: {determinationLabels[v.eipd.state]}</p>
                <p className="whitespace-pre-wrap">
                  {v.eipd.reason || "Sin fundamento registrado."}
                </p>
                <p>Infancia y adolescencia: {determinationLabels[v.infancia.state]}</p>
                <p className="whitespace-pre-wrap">
                  {v.infancia.reason || "Sin fundamento registrado."}
                </p>
              </li>
            ))}
          </ul>
        </details>
      )}
    </div>
  );
}
