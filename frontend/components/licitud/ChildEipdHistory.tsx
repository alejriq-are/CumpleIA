"use client";
import { useEffect, useRef, useState } from "react";
import { ApiError } from "@/lib/api/client";
import type {
  ChildPolicy,
  ChildResolution,
  ChildReview,
  ResolutionDraft,
  NegativeDecision,
} from "@/lib/api/child-eipd";
type Snapshot = { policy: ChildPolicy; resolutions: ChildResolution[]; status: string };
type Props = {
  load: () => Promise<Snapshot>;
  create: (draft: ResolutionDraft) => Promise<ChildResolution>;
  reviews: (resolution: ChildResolution) => Promise<ChildReview[]>;
  review: (
    resolution: ChildResolution,
    decision: NegativeDecision,
    rationale: string,
    reference: string
  ) => Promise<ChildReview>;
  readOnly: boolean;
};
const empty = { reference: "", version: "", notes: "" };
function problem(error: unknown) {
  if (error instanceof ApiError && error.status === 409) {
    const code = (error.detail as { code?: string } | undefined)?.code;
    if (
      code === "infancia_escritura_ficticia_no_habilitada" ||
      code === "infancia_escritura_solo_desarrollo"
    )
      return "El servidor mantiene deshabilitado el registro de pruebas. Puedes consultar el historial.";
    return "El material o el expediente cambió. Actualiza el historial y revisa el documento de infancia; puede requerir una nueva resolución.";
  }
  if (error instanceof ApiError && error.status === 401)
    return "La sesión no está disponible. Ingresa nuevamente.";
  if (error instanceof ApiError && error.status === 403)
    return "No tienes permiso para registrar este evento. Conservamos el formulario.";
  return "No se pudo completar la operación. Conservamos el formulario.";
}
export function ChildEipdHistory({ load, create, reviews, review, readOnly }: Props) {
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [selected, setSelected] = useState<ChildResolution | null>(null);
  const [events, setEvents] = useState<ChildReview[]>([]);
  const [draft, setDraft] = useState(empty);
  const [decision, setDecision] = useState<NegativeDecision>("requiere_cambios");
  const [rationale, setRationale] = useState(""),
    [reference, setReference] = useState("");
  const [fictitious, setFictitious] = useState(false);
  const [busy, setBusy] = useState(false),
    [uncertain, setUncertain] = useState(false);
  const [error, setError] = useState(""),
    [message, setMessage] = useState("");
  const running = useRef(false),
    generation = useRef(0),
    mounted = useRef(false);
  useEffect(() => {
    mounted.current = true;
    const request = ++generation.current;
    setBusy(true);
    setSnapshot(null);
    setSelected(null);
    setEvents([]);
    setError("");
    load()
      .then((value) => {
        if (mounted.current && request === generation.current) setSnapshot(value);
      })
      .catch((cause) => {
        if (mounted.current && request === generation.current) setError(problem(cause));
      })
      .finally(() => {
        if (mounted.current && request === generation.current) setBusy(false);
      });
    return () => {
      mounted.current = false;
    };
  }, [load]);
  async function refresh() {
    if (running.current) return;
    running.current = true;
    const request = ++generation.current;
    setBusy(true);
    setError("");
    setMessage("");
    setSelected(null);
    setEvents([]);
    try {
      const value = await load();
      if (mounted.current && request === generation.current) setSnapshot(value);
    } catch (cause) {
      if (mounted.current && request === generation.current) {
        setSnapshot(null);
        setError(problem(cause));
      }
    } finally {
      running.current = false;
      if (mounted.current && request === generation.current) setBusy(false);
    }
  }
  async function choose(row: ChildResolution) {
    if (running.current || busy) return;
    running.current = true;
    const request = ++generation.current;
    setBusy(true);
    setSelected(null);
    setEvents([]);
    setError("");
    setMessage("");
    setRationale("");
    setReference("");
    try {
      const values = await reviews(row);
      if (mounted.current && request === generation.current) {
        setSelected(row);
        setEvents(values);
      }
    } catch (cause) {
      if (mounted.current && request === generation.current) setError(problem(cause));
    } finally {
      running.current = false;
      if (mounted.current && request === generation.current) setBusy(false);
    }
  }
  const editable = Boolean(snapshot && snapshot.status === "borrador" && !readOnly && !uncertain);
  async function write(kind: "resolution" | "review") {
    if (running.current || busy || !editable || !fictitious) return;
    if (
      (kind === "resolution" && !draft.reference.trim()) ||
      (kind === "review" && (!selected || !rationale.trim() || !reference.trim()))
    ) {
      setError("Completa las referencias y el fundamento requeridos.");
      return;
    }
    running.current = true;
    setBusy(true);
    setError("");
    setMessage("");
    const request = ++generation.current;
    try {
      if (kind === "resolution") {
        const saved = await create({
          schema_version: 1,
          document_reference: draft.reference.trim(),
          document_version: draft.version.trim() || null,
          notes: draft.notes.trim() || null,
        });
        if (mounted.current && request === generation.current) {
          setSnapshot(
            (s) =>
              s && { ...s, resolutions: [...s.resolutions.filter((r) => r.id !== saved.id), saved] }
          );
          setSelected(saved);
          setEvents([]);
          setDraft(empty);
          setMessage(
            `Resolución documental ${saved.version} registrada. EIPD permanece bloqueada.`
          );
        }
      } else if (selected) {
        const saved = await review(selected, decision, rationale.trim(), reference.trim());
        if (mounted.current && request === generation.current) {
          setEvents((values) => [...values, saved]);
          setRationale("");
          setReference("");
          setMessage("Revisión negativa registrada. EIPD permanece bloqueada.");
        }
      }
    } catch (cause) {
      if (mounted.current && request === generation.current) {
        const ambiguous =
          !(cause instanceof ApiError) || cause.status >= 500 || cause.status === 408;
        setUncertain(ambiguous);
        setError(
          ambiguous
            ? "Resultado incierto: no repitas el registro. Consulta el historial antes de recargar la página."
            : problem(cause)
        );
      }
    } finally {
      running.current = false;
      if (mounted.current && request === generation.current) setBusy(false);
    }
  }
  return (
    <section
      aria-label="Historial EIPD de infancia"
      className="space-y-5 rounded border bg-white p-5"
    >
      <h2 className="text-xl font-semibold">Resoluciones y revisiones de infancia</h2>
      <p>
        Pruebas de desarrollo: utiliza solo datos ficticios. Los registros son inmutables. La
        confirmación y la activación EIPD permanecen bloqueadas.
      </p>
      <p>
        Esta consulta es histórica: no acredita vigencia del material actual ni concede
        autorización.
      </p>
      {uncertain && (
        <p>
          No repitas el registro: su resultado fue incierto. La consulta sigue disponible para
          revisar lo guardado antes de recargar la página.
        </p>
      )}
      {error && <p role="alert">{error}</p>}
      {message && <p role="status">{message}</p>}
      <button type="button" disabled={busy} onClick={() => void refresh()}>
        Actualizar historial de infancia
      </button>
      {busy && <p>Cargando operación de historial…</p>}
      {snapshot && (
        <>
          <p>
            Política de pruebas: fuentes pendientes, aceptación pendiente y activación
            deshabilitada.
          </p>
          {(!editable || readOnly) && <p>Registro deshabilitado; consulta disponible.</p>}
          <label className="block">
            <input
              type="checkbox"
              checked={fictitious}
              disabled={!editable || busy}
              onChange={(e) => setFictitious(e.target.checked)}
            />{" "}
            Declaro que este registro usa datos ficticios
          </label>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              void write("resolution");
            }}
          >
            <fieldset disabled={!editable || busy || !fictitious} className="space-y-3">
              <legend>Registrar resolución documental parcial</legend>
              <p>
                Registra identificación y notas del documento; no declara completitud ni sustituye
                el análisis EIPD. Se vincula al último documento de infancia guardado; los cambios
                sin guardar no forman parte de la resolución.
              </p>
              <label className="block">
                Referencia de la resolución *
                <input
                  className="block w-full rounded border p-2"
                  required
                  value={draft.reference}
                  onChange={(e) => setDraft((d) => ({ ...d, reference: e.target.value }))}
                />
              </label>
              <label className="block">
                Versión del documento
                <input
                  className="block w-full rounded border p-2"
                  value={draft.version}
                  onChange={(e) => setDraft((d) => ({ ...d, version: e.target.value }))}
                />
              </label>
              <label className="block">
                Notas de la resolución
                <textarea
                  className="block w-full rounded border p-2"
                  aria-label="Notas de la resolución"
                  value={draft.notes}
                  onChange={(e) => setDraft((d) => ({ ...d, notes: e.target.value }))}
                />
              </label>
              <button type="submit">Registrar resolución ficticia</button>
            </fieldset>
          </form>
          <h3 className="font-semibold">Resoluciones guardadas</h3>
          {snapshot.resolutions.length === 0 && <p>No hay resoluciones de infancia registradas.</p>}
          <ul>
            {snapshot.resolutions.map((row) => (
              <li key={row.id}>
                <button type="button" disabled={busy} onClick={() => void choose(row)}>
                  Consultar resolución {row.version}
                </button>
              </li>
            ))}
          </ul>
          {selected && (
            <>
              <h3 className="font-semibold">Resolución {selected.version} consultada</h3>
              <dl>
                <dt>Referencia</dt>
                <dd>{String(selected.document.document_reference ?? "Sin referencia")}</dd>
                <dt>Versión documental</dt>
                <dd>{String(selected.document.document_version ?? "Sin declarar")}</dd>
                <dt>Notas</dt>
                <dd className="whitespace-pre-wrap">
                  {String(selected.document.notes ?? "Sin notas")}
                </dd>
                <dt>Fecha registrada (UTC)</dt>
                <dd>{selected.created_at}</dd>
              </dl>
              <details>
                <summary>Identidad del registro</summary>
                <dl className="break-all">
                  <dt>Resolución</dt>
                  <dd>{selected.id}</dd>
                  <dt>Documento</dt>
                  <dd>{selected.document_hash}</dd>
                  <dt>Contexto</dt>
                  <dd>{selected.context_hash}</dd>
                  <dt>Material de infancia</dt>
                  <dd>{selected.child_material_hash}</dd>
                </dl>
              </details>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  void write("review");
                }}
              >
                <fieldset disabled={!editable || busy || !fictitious} className="space-y-3">
                  <legend>Registrar revisión negativa</legend>
                  <label className="block">
                    Decisión de la revisión
                    <select
                      className="block w-full rounded border p-2"
                      value={decision}
                      onChange={(e) => setDecision(e.target.value as NegativeDecision)}
                    >
                      <option value="requiere_cambios">Requiere cambios</option>
                      <option value="no_continuar">No continuar</option>
                    </select>
                  </label>
                  <label className="block">
                    Fundamento de la revisión *
                    <textarea
                      className="block w-full rounded border p-2"
                      aria-label="Fundamento de la revisión *"
                      required
                      value={rationale}
                      onChange={(e) => setRationale(e.target.value)}
                    />
                  </label>
                  <label className="block">
                    Referencia de la revisión *
                    <input
                      className="block w-full rounded border p-2"
                      required
                      value={reference}
                      onChange={(e) => setReference(e.target.value)}
                    />
                  </label>
                  <button type="submit">Registrar revisión ficticia</button>
                </fieldset>
              </form>
              <h3 className="font-semibold">Revisiones de esta resolución</h3>
              {events.length === 0 && <p>No hay revisiones registradas para esta resolución.</p>}
              <ul>
                {events.map((event) => (
                  <li key={event.id} className="rounded border p-3">
                    <p>
                      {event.decision === "requiere_cambios" ? "Requiere cambios" : "No continuar"}
                    </p>
                    <p className="whitespace-pre-wrap">{event.rationale}</p>
                    <p>{event.review_reference}</p>
                    <p>Fecha registrada (UTC): {event.created_at}</p>
                    <p>Política registrada: {event.policy_snapshot.policy_reference}</p>
                  </li>
                ))}
              </ul>
            </>
          )}
        </>
      )}
    </section>
  );
}
