"use client";
import { useWorkState, type WorkReporter } from "@/components/navigation/work-unit-state";
import {
  documentDisclosureClass,
  documentNavigationButtonClass,
  focusDocumentSection,
} from "./document-focus";
import { DocumentCapabilities } from "./DocumentCapabilities";
import { documentLabels } from "@/lib/licitud/document-labels";
import { type ReactNode } from "react";
import { EipdDocumentFields, EipdDocumentView } from "./EipdDocumentFields";
import { useEffect, useId, useRef, useState } from "react";
import { legalBases, type Assessment } from "@/lib/api/licitud";
import type { ChildAssessment } from "@/lib/api/child-adolescent";
import { liaFields } from "@/lib/licitud/lia-fields";
import { ApiError } from "@/lib/api/client";
import type {
  ChildPolicy,
  ChildResolution,
  ChildReview,
  ResolutionDraft,
  NegativeDecision,
} from "@/lib/api/child-eipd";
type Snapshot = {
  policy: ChildPolicy;
  resolutions: ChildResolution[];
  status: string;
  context?: ChildAssessment & Partial<Assessment>;
};
type Props = {
  organizationAcceptance?: (resolution: ChildResolution, readOnly: boolean) => ReactNode;
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
  view?: "all" | "prepare" | "review";
  onPrepare?: () => void;
  onRecorded?: () => void;
  preparationBlocked?: boolean;
  onPending?: (pending: boolean) => void;
  onWorkState?: WorkReporter;
};
const empty = { reference: "", version: "", notes: "" };
function problem(error: unknown) {
  if (error instanceof ApiError && error.status === 400) return error.message;
  if (error instanceof ApiError && error.status === 422)
    return "Revisa los campos del documento: el servidor rechazó su formato. Conservamos el formulario.";
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
export function ChildEipdHistory({
  load,
  create,
  reviews,
  review,
  readOnly,
  organizationAcceptance,
  view = "all",
  onPrepare,
  onRecorded,
  preparationBlocked = false,
  onPending,
  onWorkState,
}: Props) {
  const selectedHeading = useRef<HTMLHeadingElement>(null);
  const reviewHeading = useRef<HTMLHeadingElement>(null);
  const reviewHistoryHeading = useRef<HTMLHeadingElement>(null);
  const decisionHeading = useRef<HTMLHeadingElement>(null);
  const [jump, setJump] = useState<"review" | "history" | "decision" | null>(null);
  const [copyOrigin, setCopyOrigin] = useState<{ version: number; reference: string } | null>(null);
  useEffect(() => {
    if (!jump) return;
    const target =
      jump === "review"
        ? reviewHeading.current
        : jump === "history"
          ? reviewHistoryHeading.current
          : decisionHeading.current;
    focusDocumentSection(target);
    setJump(null);
  }, [jump]);
  const editionHelpId = useId();
  const actuationHelpId = useId();
  const reviewHelpId = useId();
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [selected, setSelected] = useState<ChildResolution | null>(null);
  const [events, setEvents] = useState<ChildReview[]>([]);
  const [draft, setDraft] = useState(empty);
  const [preparing, setPreparing] = useState(false);
  const [reviewed, setReviewed] = useState("");
  const [document, setDocument] = useState<Record<string, unknown>>({});
  const fingerprint = JSON.stringify([draft, document]);
  const pending = Boolean(
    draft.reference || draft.version || draft.notes || Object.keys(document).length
  );
  const [confirmCopy, setConfirmCopy] = useState(false);
  const reviewDrafts = useRef<
    Record<string, { decision: NegativeDecision | ""; rationale: string; reference: string }>
  >({});
  useEffect(() => {
    onPending?.(pending);
  }, [pending, onPending]);
  const [actuation, setActuation] = useState<"revision" | "decision">("revision");
  const [decision, setDecision] = useState<NegativeDecision | "">(
    view === "all" ? "requiere_cambios" : ""
  );
  const [rationale, setRationale] = useState(""),
    [reference, setReference] = useState("");
  useEffect(() => {
    if (selected) reviewDrafts.current[selected.id] = { decision, rationale, reference };
  }, [selected, decision, rationale, reference]);
  const [fictitious, setFictitious] = useState(false);
  const [busy, setBusy] = useState(false),
    [uncertain, setUncertain] = useState(false);
  const [error, setError] = useState(""),
    [message, setMessage] = useState("");
  useWorkState(onWorkState, {
    loaded: !!snapshot,
    loading: !snapshot && busy,
    dirty: pending,
    error: !!error,
    uncertain: pending && uncertain,
  });
  const running = useRef(false),
    generation = useRef(0),
    mounted = useRef(false);
  useEffect(() => {
    mounted.current = true;
    const request = ++generation.current;
    setBusy(true);
    setSnapshot(null);
    setPreparing(false);
    setReviewed("");
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
    if (selected) reviewDrafts.current[selected.id] = { decision, rationale, reference };
    const remembered = reviewDrafts.current[row.id];
    setDecision(remembered?.decision ?? (view === "all" ? "requiere_cambios" : ""));
    setRationale(remembered?.rationale ?? "");
    setReference(remembered?.reference ?? "");
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
  const registrationReason = busy
    ? "Hay una consulta o un registro en curso; espera su resultado."
    : !snapshot
      ? error
        ? "La consulta falló; actualiza el historial antes de continuar."
        : "Consulta primero el historial y la política de pruebas."
      : readOnly
        ? "El rol o el estado de la evaluación permite solo consulta."
        : snapshot.status !== "borrador"
          ? "El expediente debe estar en borrador para registrar actuaciones."
          : uncertain
            ? "El resultado anterior es incierto; no repitas el registro. Consulta lo guardado."
            : "";
  async function write(kind: "resolution" | "review") {
    if (running.current || busy || !editable || !fictitious) return;
    if (
      kind === "resolution" &&
      (preparationBlocked || (view !== "all" && (!preparing || reviewed !== fingerprint)))
    )
      return;
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
          ...document,
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
          setCopyOrigin(null);
          setDocument({});
          setPreparing(false);
          setReviewed("");
          onRecorded?.();
          setMessage(
            `Versión documental de infancia ${saved.version} registrada. El original se conserva y EIPD permanece bloqueada.`
          );
        }
      } else if (selected && decision) {
        const saved = await review(selected, decision, rationale.trim(), reference.trim());
        if (mounted.current && request === generation.current) {
          setEvents((values) => [...values, saved]);
          setRationale("");
          setReference("");
          delete reviewDrafts.current[selected.id];
          setMessage("Revisión negativa registrada. EIPD permanece bloqueada.");
          onRecorded?.();
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
  function copySelected() {
    if (!selected || !editable || busy) return;
    setConfirmCopy(false);
    setCopyOrigin({
      version: selected.version,
      reference: String(selected.document.document_reference ?? "Sin referencia"),
    });
    const {
      schema_version: _,
      document_reference,
      document_version,
      notes,
      ...fields
    } = structuredClone(selected.document);
    setDraft({
      reference: typeof document_reference === "string" ? document_reference : "",
      version: typeof document_version === "string" ? document_version : "",
      notes: typeof notes === "string" ? notes : "",
    });
    setDocument(fields);
    setPreparing(false);
    setReviewed("");
    onPrepare?.();
    setMessage(
      "Copia temporal preparada. Todavía no está registrada en el servidor; Registrar nueva versión documental crea el nuevo registro y conserva el original."
    );
  }
  return (
    <section
      aria-label="Historial EIPD de infancia"
      className="space-y-5 rounded border bg-white p-5"
    >
      <h2 className="text-xl font-semibold">
        {view === "prepare"
          ? documentLabels.prepareChild
          : "Versiones registradas y revisiones de infancia"}
      </h2>
      <p>
        Pruebas de desarrollo: utiliza solo datos ficticios. Los registros son inmutables. La
        confirmación y la activación EIPD permanecen bloqueadas.
      </p>
      <p className="text-sm">
        En los antecedentes anteriores, cada versión registrada se denomina «resolución documental».
        Sus números, referencias y documentos conservados no cambian.
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
      <button
        type="button"
        className={documentNavigationButtonClass}
        disabled={busy}
        onClick={() => void refresh()}
      >
        Actualizar historial de infancia
      </button>
      {busy && <p>Cargando operación de historial…</p>}
      {!snapshot && (
        <DocumentCapabilities
          object="Historial de infancia sin consultar"
          actions={[
            {
              action: "Preparar o registrar actuaciones",
              state: "pending",
              reason: registrationReason,
            },
            {
              action: "Confirmar o activar EIPD",
              state: "blocked",
              reason: "El piloto no habilita estas acciones.",
            },
          ]}
        />
      )}
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
          <div hidden={view === "review"}>
            <DocumentCapabilities
              object="Preparación temporal de nueva versión de infancia"
              actions={[
                {
                  action: "Completar preparación y ver vista previa",
                  state:
                    !editable || busy || !fictitious || preparationBlocked
                      ? "blocked"
                      : "available",
                  reason:
                    registrationReason ||
                    (preparationBlocked
                      ? "Guarda primero base, fundamento e infancia; la nueva versión usa ese material guardado."
                      : !fictitious
                        ? "Declara el uso de datos ficticios para completar la preparación."
                        : "La preparación vive en esta pestaña; la vista previa todavía no registra una versión."),
                },
                {
                  action: "Registrar nueva versión",
                  state:
                    !editable ||
                    busy ||
                    !fictitious ||
                    preparationBlocked ||
                    !draft.reference.trim() ||
                    (view !== "all" && (!preparing || reviewed !== fingerprint))
                      ? "blocked"
                      : "available",
                  reason:
                    registrationReason ||
                    (preparationBlocked
                      ? "Hay cambios del material asociado pendientes de guardar."
                      : !fictitious
                        ? "Falta la declaración de datos ficticios."
                        : !draft.reference.trim()
                          ? "Completa la referencia del documento."
                          : view !== "all" && (!preparing || reviewed !== fingerprint)
                            ? "Abre la vista previa y confirma la lectura del contenido antes de registrar."
                            : "Crea un registro nuevo y conserva los anteriores; el servidor valida la asociación del material al registrar."),
                },
                {
                  action: "Confirmar o activar EIPD",
                  state: "blocked",
                  reason: "Registrar una versión no habilita estas acciones.",
                },
              ]}
            />
            {preparationBlocked && (
              <p role="alert" className="rounded border border-amber-400 bg-amber-50 p-3">
                Guarda primero los cambios de base, fundamento e infancia. La versión documental se
                vincula exclusivamente al material guardado.
              </p>
            )}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                void write("resolution");
              }}
            >
              <fieldset
                disabled={!editable || busy || !fictitious || preparationBlocked}
                className="space-y-3"
              >
                <legend>{documentLabels.prepareChild}</legend>
                {copyOrigin && (
                  <p className="rounded border border-blue-200 bg-blue-50 p-3">
                    Origen de la copia temporal: versión documental de infancia {copyOrigin.version}{" "}
                    · {copyOrigin.reference}. El original se conserva. Revisa nuevamente la vista
                    previa antes de registrar otra versión.
                  </p>
                )}
                <p className="rounded border border-blue-200 bg-blue-50 p-3">
                  Esta preparación es temporal en esta pestaña: copiar o ver la vista previa no
                  guarda una nueva versión en el servidor. Solo Registrar nueva versión documental
                  crea el registro. Las versiones anteriores se conservan. No recargues si deseas
                  conservar esta preparación temporal.
                </p>
                <p>
                  Completa el documento y sus análisis. Puedes registrar faltantes sin declarar una
                  EIPD completa ni conceder autorización. Se vincula al último documento de infancia
                  guardado; guarda primero sus cambios en el editor de infancia.
                </p>
                <label className="block">
                  Referencia del documento de infancia *
                  <input
                    className="block w-full rounded border p-2"
                    required
                    value={draft.reference}
                    onChange={(e) => setDraft((d) => ({ ...d, reference: e.target.value }))}
                  />
                </label>
                <label className="block">
                  {documentLabels.edition}
                  <input
                    className="block w-full rounded border p-2"
                    aria-describedby={editionHelpId}
                    value={draft.version}
                    onChange={(e) => setDraft((d) => ({ ...d, version: e.target.value }))}
                  />
                </label>
                <label className="block">
                  Notas del documento de infancia
                  <textarea
                    className="block w-full rounded border p-2"
                    aria-label="Notas del documento de infancia"
                    value={draft.notes}
                    onChange={(e) => setDraft((d) => ({ ...d, notes: e.target.value }))}
                  />
                </label>
                <p id={editionHelpId} className="text-sm">
                  {documentLabels.editionHelp}
                </p>
                <EipdDocumentFields value={document} onChange={setDocument} />
                {view === "all" ? (
                  <button type="submit">{documentLabels.registerChild}</button>
                ) : (
                  <>
                    <button
                      type="button"
                      className="rounded bg-blue-800 px-4 py-2 text-white"
                      onClick={() => {
                        setPreparing(true);
                        setReviewed("");
                      }}
                    >
                      Ver vista previa de la versión por registrar
                    </button>
                    {preparing && (
                      <aside
                        aria-label="Vista previa de la versión documental"
                        className="space-y-3 rounded border border-blue-300 bg-blue-50 p-4"
                      >
                        <h3 className="font-semibold">Vista previa · todavía no registrada</h3>
                        <p>
                          La numeración definitiva la asigna el servidor al registrar. Esta
                          resolución usa la evaluación y el documento de infancia guardados.
                        </p>
                        <dl>
                          <dt className="rounded-t border border-blue-200 bg-blue-100 px-3 py-2 font-semibold text-blue-950">
                            Referencia
                          </dt>
                          <dd className="rounded-b border border-t-0 border-blue-200 bg-white px-3 py-3 whitespace-pre-wrap break-words text-slate-950">
                            {draft.reference || "Pendiente de completar"}
                          </dd>
                          <dt className="rounded-t border border-blue-200 bg-blue-100 px-3 py-2 font-semibold text-blue-950">
                            {documentLabels.edition}
                          </dt>
                          <dd className="rounded-b border border-t-0 border-blue-200 bg-white px-3 py-3 whitespace-pre-wrap break-words text-slate-950">
                            {draft.version || "Sin nombre de edición (opcional)"}
                          </dd>
                          <dt className="rounded-t border border-blue-200 bg-blue-100 px-3 py-2 font-semibold text-blue-950">
                            Notas específicas
                          </dt>
                          <dd className="rounded-b border border-t-0 border-blue-200 bg-white px-3 py-3 whitespace-pre-wrap break-words text-slate-950">
                            {draft.notes || "Sin notas (opcional)"}
                          </dd>
                        </dl>
                        {snapshot.context && (
                          <section
                            aria-label="Contexto guardado que acompaña la resolución"
                            className="space-y-2 rounded border bg-white p-3"
                          >
                            <h4 className="font-semibold">
                              Contexto guardado que acompaña la resolución
                            </h4>
                            <dl className="space-y-2">
                              <div>
                                <dt className="rounded-t border border-blue-200 bg-blue-100 px-3 py-2 font-semibold text-blue-950">
                                  Finalidad
                                </dt>
                                <dd className="rounded-b border border-t-0 border-blue-200 bg-white px-3 py-3 whitespace-pre-wrap break-words text-slate-950">
                                  {snapshot.context.purpose_snapshot ?? "Sin finalidad disponible"}
                                </dd>
                              </div>
                              <div>
                                <dt className="rounded-t border border-blue-200 bg-blue-100 px-3 py-2 font-semibold text-blue-950">
                                  Titulares
                                </dt>
                                <dd className="rounded-b border border-t-0 border-blue-200 bg-white px-3 py-3 whitespace-pre-wrap break-words text-slate-950">
                                  {snapshot.context.rat_context_snapshot.data_subjects
                                    .map((v) => v.category_name)
                                    .join(", ") || "Sin titulares"}
                                </dd>
                              </div>
                              <div>
                                <dt className="rounded-t border border-blue-200 bg-blue-100 px-3 py-2 font-semibold text-blue-950">
                                  Categorías
                                </dt>
                                <dd className="rounded-b border border-t-0 border-blue-200 bg-white px-3 py-3 whitespace-pre-wrap break-words text-slate-950">
                                  {snapshot.context.rat_context_snapshot.data_categories
                                    .map((v) => v.category_name)
                                    .join(", ") || "Sin categorías"}
                                </dd>
                              </div>
                              <div>
                                <dt className="rounded-t border border-blue-200 bg-blue-100 px-3 py-2 font-semibold text-blue-950">
                                  Base propuesta
                                </dt>
                                <dd className="rounded-b border border-t-0 border-blue-200 bg-white px-3 py-3 whitespace-pre-wrap break-words text-slate-950">
                                  {legalBases.find(
                                    ([code]) => code === snapshot.context?.legal_basis
                                  )?.[1] ?? "Pendiente de definir"}
                                </dd>
                              </div>
                              <div>
                                <dt className="rounded-t border border-blue-200 bg-blue-100 px-3 py-2 font-semibold text-blue-950">
                                  Fundamento
                                </dt>
                                <dd className="rounded-b border border-t-0 border-blue-200 bg-white px-3 py-3 whitespace-pre-wrap break-words text-slate-950">
                                  {snapshot.context.justification || "Pendiente de completar"}
                                </dd>
                              </div>
                              {liaFields.map(([group, key, label]) => {
                                const value = (
                                  snapshot.context?.lia_assessment?.[group] as
                                    Record<string, unknown> | undefined
                                )?.[key];
                                return typeof value === "string" && value ? (
                                  <div key={key}>
                                    <dt className="rounded-t border border-blue-200 bg-blue-100 px-3 py-2 font-semibold text-blue-950">
                                      {label}
                                    </dt>
                                    <dd className="rounded-b border border-t-0 border-blue-200 bg-white px-3 py-3 whitespace-pre-wrap break-words text-slate-950">
                                      {value}
                                    </dd>
                                  </div>
                                ) : null;
                              })}
                              <div>
                                <dt className="rounded-t border border-blue-200 bg-blue-100 px-3 py-2 font-semibold text-blue-950">
                                  Análisis de edad y alcance guardado
                                </dt>
                                <dd className="rounded-b border border-t-0 border-blue-200 bg-white px-3 py-3 whitespace-pre-wrap break-words text-slate-950">
                                  {snapshot.context.child_adolescent_assessment?.assessment
                                    .age_scope_analysis || "Sin documento de infancia guardado"}
                                </dd>
                              </div>
                            </dl>
                            <p>
                              El servidor conserva su contexto completo con la resolución; no se
                              incorporan cambios sin guardar.
                            </p>
                          </section>
                        )}
                        <EipdDocumentView value={document} expanded />
                        <p>
                          Faltantes declarados:{" "}
                          {!draft.reference.trim() ? "falta referencia; " : ""}
                          {!Object.keys(document).length
                            ? "no se han aportado análisis, riesgos ni medidas; "
                            : ""}
                          revisión jurídica y suficiencia de evidencias pendientes. No es una
                          comprobación exhaustiva ni una EIPD aprobada.
                        </p>
                        <label className="block">
                          <input
                            type="checkbox"
                            checked={reviewed === fingerprint}
                            onChange={(e) => setReviewed(e.target.checked ? fingerprint : "")}
                          />{" "}
                          He revisado el contenido como responsable ficticio del ensayo
                        </label>
                        <p>
                          Si modificas cualquier campo debes revisar nuevamente. Puedes volver a
                          completar los análisis antes de registrar.
                        </p>
                        <button
                          type="button"
                          className={documentNavigationButtonClass}
                          onClick={() => setPreparing(false)}
                        >
                          Volver a completar documento
                        </button>
                        <button
                          type="submit"
                          className="rounded bg-blue-800 px-4 py-2 text-white disabled:opacity-50"
                          disabled={reviewed !== fingerprint || !draft.reference.trim()}
                        >
                          {documentLabels.registerChild}
                        </button>
                      </aside>
                    )}
                  </>
                )}
              </fieldset>
            </form>
          </div>
          <div hidden={view === "prepare"}>
            <h3 className="font-semibold">{documentLabels.registeredChild}</h3>
            {snapshot.resolutions.length === 0 && (
              <p>No hay versiones del documento de infancia registradas.</p>
            )}
            <ul className="flex flex-wrap gap-2">
              {snapshot.resolutions.map((row) => (
                <li key={row.id}>
                  <button
                    type="button"
                    className={documentNavigationButtonClass}
                    disabled={busy}
                    onClick={() => void choose(row)}
                  >
                    Consultar versión documental {row.version}
                  </button>
                </li>
              ))}
            </ul>
            {selected && (
              <>
                <h3 ref={selectedHeading} tabIndex={-1} className="scroll-mt-80 font-semibold">
                  Versión documental de infancia {selected.version} consultada
                </h3>
                <p className="break-words text-sm">
                  Documento consultado: versión de infancia {selected.version} ·{" "}
                  {String(selected.document.document_reference ?? "Sin referencia")}. Fecha de
                  registro (UTC): {selected.created_at}.
                </p>
                <nav
                  aria-label="Accesos al documento de infancia consultado"
                  className="flex flex-wrap gap-2"
                >
                  <button
                    type="button"
                    className={documentNavigationButtonClass}
                    onClick={() => {
                      setActuation("revision");
                      setJump("review");
                    }}
                  >
                    Ir a Revisión del documento
                  </button>
                  <button
                    type="button"
                    className={documentNavigationButtonClass}
                    onClick={() => setJump("history")}
                  >
                    Ver revisiones registradas
                  </button>
                  {organizationAcceptance && (
                    <button
                      type="button"
                      className={documentNavigationButtonClass}
                      onClick={() => {
                        setActuation("decision");
                        setJump("decision");
                      }}
                    >
                      Ir a Decisión de la organización
                    </button>
                  )}
                </nav>
                <DocumentCapabilities
                  object={`Versión documental de infancia ${selected.version} · ${String(selected.document.document_reference ?? "Sin referencia")}`}
                  actions={[
                    {
                      action: "Editar esta versión",
                      state: "blocked",
                      reason:
                        "Es un registro histórico conservado. Preparar una copia no modifica este original.",
                    },
                    {
                      action: "Preparar nueva versión a partir de esta",
                      state: !editable || busy ? "blocked" : "available",
                      reason:
                        registrationReason ||
                        "Copia su contenido a una preparación temporal; solo el registro explícito crea otra versión.",
                    },
                    {
                      action: "Registrar revisión documental",
                      state:
                        !editable ||
                        busy ||
                        !fictitious ||
                        !decision ||
                        !rationale.trim() ||
                        !reference.trim()
                          ? "blocked"
                          : "available",
                      reason:
                        registrationReason ||
                        (!fictitious
                          ? "Falta la declaración de datos ficticios."
                          : !decision || !rationale.trim() || !reference.trim()
                            ? "Selecciona Requiere cambios o No continuar y completa fundamento y referencia en Revisión del documento."
                            : "Registra una observación sobre esta versión exacta; no modifica el documento ni decide por la organización."),
                    },
                    {
                      action: "Decisión de la organización",
                      state: organizationAcceptance ? "pending" : "blocked",
                      reason: organizationAcceptance
                        ? "Selecciona Decisión de la organización para consultar la facultad de la persona de esta sesión. Ser administrador no concede esa facultad."
                        : "Este recorrido no tiene integrada una decisión organizacional.",
                    },
                    {
                      action: "Confirmar o activar EIPD",
                      state: "blocked",
                      reason:
                        "Ni una revisión ni Acepta el documento habilitan estas acciones. La consulta histórica no verifica la vigencia del material actual.",
                    },
                  ]}
                />
                <EipdDocumentView value={selected.document} />
                {view !== "all" && (
                  <label className="block font-medium">
                    Tipo de actuación
                    <select
                      aria-label="Tipo de actuación"
                      aria-describedby={actuationHelpId}
                      className="block w-full rounded border p-2"
                      value={actuation}
                      onChange={(e) => setActuation(e.target.value as "revision" | "decision")}
                    >
                      <option value="revision">Revisión del documento</option>
                      <option value="decision">Decisión de la organización</option>
                    </select>
                  </label>
                )}
                {view !== "all" && (
                  <p id={actuationHelpId} aria-live="polite" className="text-sm">
                    {actuation === "revision"
                      ? "Revisión del documento: registra observaciones sobre la resolución seleccionada. No expresa una decisión de la organización ni modifica el original."
                      : "Decisión de organización: requiere una facultad vigente y se refiere a esta resolución exacta. Es distinta de revisar y no confirma ni activa EIPD."}
                  </p>
                )}
                <div hidden={view !== "all" && actuation !== "decision"}>
                  {organizationAcceptance && (
                    <h3 ref={decisionHeading} tabIndex={-1} className="scroll-mt-80 font-semibold">
                      Decisión de la organización · versión de infancia {selected.version}
                    </h3>
                  )}
                  {organizationAcceptance?.(selected, !editable || readOnly)}
                </div>
                <button
                  type="button"
                  className={documentNavigationButtonClass}
                  disabled={!editable || busy}
                  onClick={() => (pending ? setConfirmCopy(true) : copySelected())}
                >
                  {documentLabels.copyChild}
                </button>
                {confirmCopy && (
                  <aside
                    role="alertdialog"
                    aria-label="Reemplazar documento en preparación"
                    className="space-y-3 rounded border border-amber-400 bg-amber-50 p-4"
                  >
                    <p>
                      Copiar esta resolución reemplazará el documento que estás preparando. El
                      original y las versiones registradas no cambian.
                    </p>
                    <button type="button" disabled={busy} onClick={copySelected}>
                      Reemplazar preparación con una copia de esta versión
                    </button>
                    <button type="button" onClick={() => setConfirmCopy(false)}>
                      Conservar documento en preparación
                    </button>
                  </aside>
                )}
                <dl>
                  <dt className="rounded-t border border-blue-200 bg-blue-100 px-3 py-2 font-semibold text-blue-950">
                    Referencia
                  </dt>
                  <dd className="rounded-b border border-t-0 border-blue-200 bg-white px-3 py-3 whitespace-pre-wrap break-words text-slate-950">
                    {String(selected.document.document_reference ?? "Sin referencia")}
                  </dd>
                  <dt className="rounded-t border border-blue-200 bg-blue-100 px-3 py-2 font-semibold text-blue-950">
                    {documentLabels.edition}
                  </dt>
                  <dd className="rounded-b border border-t-0 border-blue-200 bg-white px-3 py-3 whitespace-pre-wrap break-words text-slate-950">
                    {String(selected.document.document_version ?? "Sin declarar")}
                  </dd>
                  <dt className="rounded-t border border-blue-200 bg-blue-100 px-3 py-2 font-semibold text-blue-950">
                    Notas
                  </dt>
                  <dd className="rounded-b border border-t-0 border-blue-200 bg-white px-3 py-3 whitespace-pre-wrap break-words text-slate-950">
                    {String(selected.document.notes ?? "Sin notas")}
                  </dd>
                  <dt className="rounded-t border border-blue-200 bg-blue-100 px-3 py-2 font-semibold text-blue-950">
                    Fecha registrada (UTC)
                  </dt>
                  <dd className="rounded-b border border-t-0 border-blue-200 bg-white px-3 py-3 whitespace-pre-wrap break-words text-slate-950">
                    {selected.created_at}
                  </dd>
                </dl>
                <details>
                  <summary className={documentDisclosureClass}>Identidad del registro</summary>
                  <dl className="break-all">
                    <dt className="rounded-t border border-blue-200 bg-blue-100 px-3 py-2 font-semibold text-blue-950">
                      Resolución
                    </dt>
                    <dd className="rounded-b border border-t-0 border-blue-200 bg-white px-3 py-3 whitespace-pre-wrap break-words text-slate-950">
                      {selected.id}
                    </dd>
                    <dt className="rounded-t border border-blue-200 bg-blue-100 px-3 py-2 font-semibold text-blue-950">
                      Documento
                    </dt>
                    <dd className="rounded-b border border-t-0 border-blue-200 bg-white px-3 py-3 whitespace-pre-wrap break-words text-slate-950">
                      {selected.document_hash}
                    </dd>
                    <dt className="rounded-t border border-blue-200 bg-blue-100 px-3 py-2 font-semibold text-blue-950">
                      Contexto
                    </dt>
                    <dd className="rounded-b border border-t-0 border-blue-200 bg-white px-3 py-3 whitespace-pre-wrap break-words text-slate-950">
                      {selected.context_hash}
                    </dd>
                    <dt className="rounded-t border border-blue-200 bg-blue-100 px-3 py-2 font-semibold text-blue-950">
                      Material de infancia
                    </dt>
                    <dd className="rounded-b border border-t-0 border-blue-200 bg-white px-3 py-3 whitespace-pre-wrap break-words text-slate-950">
                      {selected.child_material_hash}
                    </dd>
                  </dl>
                </details>
                <p className="rounded border border-blue-300 bg-blue-50 p-3">
                  Revisarás la resolución {selected.version}:{" "}
                  {String(selected.document.document_reference ?? "Sin referencia")}. La observación
                  no modifica el original ni justifica los cambios de otra versión.
                </p>
                <div hidden={view !== "all" && actuation !== "revision"}>
                  <h3 ref={reviewHeading} tabIndex={-1} className="scroll-mt-80 font-semibold">
                    Revisión del documento · versión de infancia {selected.version}
                  </h3>
                  <form
                    onSubmit={(e) => {
                      e.preventDefault();
                      void write("review");
                    }}
                  >
                    <fieldset disabled={!editable || busy || !fictitious} className="space-y-3">
                      <legend>Registrar revisión negativa</legend>
                      <label className="block">
                        {documentLabels.reviewResult}
                        <select
                          className="block w-full rounded border p-2"
                          value={decision}
                          required
                          aria-label={documentLabels.reviewResult}
                          aria-describedby={reviewHelpId}
                          onChange={(e) => setDecision(e.target.value as NegativeDecision)}
                        >
                          {view !== "all" && <option value="">Selecciona un resultado</option>}
                          <option value="requiere_cambios">Requiere cambios</option>
                          <option value="no_continuar">No continuar</option>
                        </select>
                      </label>
                      <p id={reviewHelpId} className="text-sm" aria-live="polite">
                        {!decision
                          ? "Selecciona el resultado que describa tu observación y explica los motivos en el fundamento."
                          : decision === "requiere_cambios"
                            ? "Requiere cambios: identifica faltantes o correcciones necesarias antes de otra revisión. Explica qué debe cambiar y por qué."
                            : "No continuar: documenta la recomendación de no seguir con lo planteado en esta resolución. Explica sus motivos; no borra el documento ni activa acciones automáticamente."}
                      </p>
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
                </div>
                <h3 ref={reviewHistoryHeading} tabIndex={-1} className="scroll-mt-80 font-semibold">
                  Revisiones de esta versión documental
                </h3>
                <p>
                  Antecedentes de la versión de infancia {selected.version} ·{" "}
                  {String(selected.document.document_reference ?? "Sin referencia")}. Esta lista no
                  es una auditoría completa del expediente.
                </p>
                <button
                  type="button"
                  className={documentNavigationButtonClass}
                  onClick={() => focusDocumentSection(selectedHeading.current)}
                >
                  Volver al documento consultado
                </button>
                {events.length === 0 && (
                  <p>No hay revisiones registradas para esta versión documental.</p>
                )}
                <ul>
                  {events.map((event) => (
                    <li key={event.id} className="rounded border p-3">
                      <p>
                        Resultado de la revisión documental:{" "}
                        {event.decision === "requiere_cambios"
                          ? "Requiere cambios"
                          : "No continuar"}
                      </p>
                      <p>
                        Versión revisada: infancia {selected.version} ·{" "}
                        {String(selected.document.document_reference ?? "Sin referencia")}
                      </p>
                      <p className="whitespace-pre-wrap">
                        Fundamento de la revisión: {event.rationale}
                      </p>
                      <p>
                        Referencia de la revisión: <span>{event.review_reference}</span>
                      </p>
                      <p>Fecha registrada (UTC): {event.created_at}</p>
                      <p className="break-all">
                        Registrada por (identificador): {event.created_by}
                      </p>
                      <p>Política registrada: {event.policy_snapshot.policy_reference}</p>
                    </li>
                  ))}
                </ul>
              </>
            )}
          </div>
        </>
      )}
    </section>
  );
}
