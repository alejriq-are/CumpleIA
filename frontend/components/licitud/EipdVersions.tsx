"use client";
import { useEffect, useId, useRef, useState, type ReactNode } from "react";
import { ApiError } from "@/lib/api/client";
import { editableEipd, type EipdValue } from "@/lib/api/eipd-draft";
import {
  eipdVersionsApi,
  type VersionMaterial,
  type VersionPreview,
  type VersionRequest,
  type RegisteredVersion,
  type VersionMetadata,
} from "@/lib/api/eipd-versions";
import { EipdVersionDecisions } from "./EipdVersionDecisions";
import { EipdVersionReviews } from "./EipdVersionReviews";
import { EipdVersionContext } from "./EipdVersionContext";
import { EipdDocumentView } from "./EipdDocumentFields";
import { documentDisclosureClass, documentNavigationButtonClass as button } from "./document-focus";

function openDisclosure(section: HTMLDivElement | null) {
  const disclosure = section?.querySelector("details");
  if (!disclosure) return;
  disclosure.open = true;
  disclosure.querySelector("summary")?.focus();
}

function MaterialView({
  value,
  expandedDocument = true,
  showContext = true,
}: {
  value: VersionMaterial;
  expandedDocument?: boolean;
  showContext?: boolean;
}) {
  const a = value.saved_assessment;
  const doc = a.eipd_resolution_assessment;
  return (
    <div className="space-y-3">
      <dl className="space-y-2">
        <div>
          <dt className="font-semibold">Finalidad guardada</dt>
          <dd>{String(a.purpose_snapshot ?? "Sin finalidad")}</dd>
        </div>
        <div>
          <dt className="font-semibold">Evaluación de origen</dt>
          <dd>n.º {String(a.version)}</dd>
        </div>
      </dl>
      <dl className="space-y-3">
        {[
          ["Referencia del documento EIPD", doc.document_reference],
          ["Nombre de la edición (texto libre)", doc.document_version],
          ["Notas del borrador EIPD conservadas", doc.notes],
        ].map(([label, content]) => (
          <div key={String(label)}>
            <dt className="font-semibold">{String(label)}</dt>
            <dd className="whitespace-pre-wrap break-words">
              {String(content || "Sin información registrada")}
            </dd>
          </div>
        ))}
      </dl>
      <EipdDocumentView
        value={doc}
        expanded={expandedDocument}
        summaryLabel="Contenido EIPD conservado para esta versión"
      />
      {showContext && (
        <>
          <p>
            Se conserva el diagnóstico, la determinación, la política y el contexto consultados al
            registrar. Los respaldos históricos no acreditan controles actuales. Los archivos anexos
            no se copian dentro de esta versión.
          </p>
          <EipdVersionContext value={value} />
        </>
      )}
    </div>
  );
}

type Props = {
  children?: ReactNode;
  organizationId: string;
  treatmentId: string;
  assessmentId: string;
  token: () => Promise<string>;
  canRegister?: boolean;
  consultationOnly?: boolean;
  blockedReason?: string;
  sourceRevision?: string;
  onPending?: (value: boolean) => void;
  onLock?: (value: boolean) => void;
  onCopy?: (value: EipdValue) => void;
  draftDirty?: boolean;
  canCopy?: boolean;
};
// A context-keyed instance keeps request IDs and preparations isolated to their evaluation.
export function EipdVersions(props: Props) {
  return (
    <VersionsPanel
      key={`${props.organizationId}/${props.treatmentId}/${props.assessmentId}`}
      {...props}
    />
  );
}
function VersionsPanel({
  children,
  organizationId,
  treatmentId,
  assessmentId,
  token,
  canRegister = false,
  consultationOnly = false,
  blockedReason,
  sourceRevision,
  onPending,
  onLock,
  onCopy,
  draftDirty,
  canCopy = false,
}: Props) {
  const id = useId();
  const [preview, setPreview] = useState<VersionPreview | null>(null);
  const [history, setHistory] = useState<VersionMetadata[] | null>(null);
  const [historyOpen, setHistoryOpen] = useState(consultationOnly);
  const [historyError, setHistoryError] = useState("");
  const [detail, setDetail] = useState<RegisteredVersion | null>(null);
  const [reason, setReason] = useState("");
  const [fictitious, setFictitious] = useState(false);
  const [reviewed, setReviewed] = useState(false);
  const [busy, setBusy] = useState(false);
  const [reviewLock, setReviewLock] = useState(false);
  const [decisionLock, setDecisionLock] = useState(false);
  const acting = reviewLock || decisionLock;
  const [pending, setPending] = useState<VersionRequest | null>(null);
  const [missing, setMissing] = useState(false);
  const [confirmCopy, setConfirmCopy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const alive = useRef(true);
  const running = useRef(false);
  const listButton = useRef<HTMLButtonElement>(null);
  const detailHeading = useRef<HTMLHeadingElement>(null);
  const reviewSection = useRef<HTMLDivElement>(null);
  const decisionSection = useRef<HTMLDivElement>(null);
  const contentSection = useRef<HTMLDivElement>(null);
  const contextSection = useRef<HTMLDivElement>(null);
  const actionTrigger = useRef<HTMLElement | null>(null);
  useEffect(() => {
    if (busy) return;
    const trigger = actionTrigger.current;
    actionTrigger.current = null;
    if (
      trigger?.isConnected &&
      document.activeElement === document.body &&
      !trigger.matches(":disabled")
    ) {
      trigger.focus({ preventScroll: true });
    }
  }, [busy]);
  useEffect(() => {
    alive.current = true;
    return () => {
      alive.current = false;
    };
  }, []);
  useEffect(() => {
    setPreview(null);
    setReviewed(false);
    setFictitious(false);
  }, [sourceRevision, canRegister]);
  useEffect(() => {
    onPending?.(!!reason.trim() || !!pending || busy || acting);
  }, [reason, pending, busy, acting, onPending]);
  useEffect(() => {
    onLock?.(busy || !!pending || acting);
  }, [busy, pending, acting, onLock]);

  useEffect(() => {
    let current = true;
    setHistoryError("");
    void token()
      .then((accessToken) =>
        eipdVersionsApi.history({ organizationId, treatmentId, assessmentId, token: accessToken })
      )
      .then((rows) => {
        if (current) setHistory(rows);
      })
      .catch(() => {
        if (current)
          setHistoryError("No se pudo consultar el historial. Vuelve a intentar actualizarlo.");
      });
    return () => {
      current = false;
    };
  }, [organizationId, treatmentId, assessmentId, token]);
  const scope = async () => ({ organizationId, treatmentId, assessmentId, token: await token() });
  async function action(work: () => Promise<void>) {
    if (running.current) return;
    running.current = true;
    actionTrigger.current =
      document.activeElement instanceof HTMLElement ? document.activeElement : null;
    setBusy(true);
    setError("");
    setMessage("");
    try {
      await work();
    } catch (e) {
      if (alive.current)
        setError(
          e instanceof ApiError
            ? e.message
            : "No se pudo conectar con el servidor. Conservamos esta preparación; vuelve a intentar la consulta."
        );
    } finally {
      running.current = false;
      if (alive.current) setBusy(false);
    }
  }
  function accepted(v: RegisteredVersion) {
    if (!alive.current) return;
    setDetail(v);
    setPreview(null);
    setPending(null);
    setMissing(false);
    setReason("");
    setReviewed(false);
    setFictitious(false);
    setConfirmCopy(false);
    setHistory((h) =>
      [...(h ?? []).filter((r) => r.id !== v.id), v].sort((a, b) => a.version - b.version)
    );
    setMessage(
      `Versión EIPD ${v.version} registrada en el servidor. El borrador no cambió. No constituye aprobación ni activa EIPD.`
    );
  }
  async function send(body: VersionRequest) {
    try {
      accepted(await eipdVersionsApi.register(await scope(), body));
    } catch (e) {
      if (!alive.current) return;
      // A network failure, 408, server failure or unverifiable response may follow a committed POST.
      const unknown = !(e instanceof ApiError) || e.status >= 500 || e.status === 408;
      if (!unknown) {
        setPending(null);
        setPreview(null);
        setReviewed(false);
      }
      setMissing(false);
      setError(
        unknown
          ? "Resultado del registro por comprobar. No generes otra solicitud ni cierres esta pestaña. Consulta el resultado; se conserva el identificador para reintentar sin duplicar."
          : `Registro rechazado. ${e.message} Consulta una nueva vista previa antes de registrar. Tu borrador no cambió.`
      );
    }
  }
  const disabled = busy || reviewLock || !!pending;
  return (
    <section
      aria-label="Versiones del documento EIPD"
      className="space-y-4 rounded border border-blue-300 bg-blue-50 p-4"
    >
      <h3 className="text-lg font-semibold">
        {consultationOnly
          ? "Versiones del documento EIPD guardadas"
          : "Versiones del documento EIPD"}
      </h3>
      <p>
        {consultationOnly
          ? "Elige una versión registrada para consultar su contenido y sus revisiones. La evaluación se identifica por su número; cada versión del documento EIPD tiene otro número y sus propias revisiones."
          : "Guardar borrador permite seguir editando. Registrar conserva una copia con número propio, diagnóstico e historial de revisiones; no aprueba ni activa la EIPD. La decisión de la organización sigue pendiente."}
      </p>
      {consultationOnly && !detail && (
        <details open className="space-y-3 rounded border border-slate-200 bg-white p-3">
          <summary className="cursor-pointer font-semibold text-slate-950">
            Cómo revisar y decidir una EIPD
          </summary>
          <ol className="list-decimal space-y-2 pl-5 marker:font-semibold">
            <li>
              <strong>Registra la versión.</strong> Quien prepara la EIPD guarda el borrador en{" "}
              <strong>Completar EIPD</strong> y registra una versión de ese contenido.
            </li>
            <li>
              <strong>Consulta la versión exacta.</strong> En la lista de abajo, pulsa{" "}
              <strong>Consultar versión EIPD</strong> y comprueba su número y referencia.
            </li>
            <li>
              <strong>Registra la revisión.</strong> Abre <strong>Revisiones y facultades</strong>.
              Una persona distinta de quien registró la versión y con facultad de revisión vigente
              emite la conclusión.
            </li>
            <li>
              <strong>Registra la decisión.</strong> Abre{" "}
              <strong>Decisión de la organización</strong>. Se requiere una facultad de decisión
              independiente. <strong>Acepta</strong> exige que la última revisión de esa versión sea{" "}
              <strong>Favorable</strong>, que el documento esté completo y que su contexto siga
              vigente.
            </li>
          </ol>
          <p className="text-sm">
            La administración del expediente otorga cada facultad desde su sección. Quien registró
            la versión queda excluido de decidir sobre ella. Si la misma persona revisa y decide, la
            facultad de decisión debe documentar esa compatibilidad.
          </p>
          <p className="text-sm">La confirmación y la activación siguen bloqueadas.</p>
        </details>
      )}
      <button
        type="button"
        ref={listButton}
        className={button}
        disabled={busy || acting}
        onClick={() =>
          void action(async () => {
            const rows = await eipdVersionsApi.history(await scope());
            if (alive.current) {
              setHistory(rows);
              setHistoryError("");
            }
          })
        }
      >
        {consultationOnly
          ? "Actualizar lista de versiones"
          : "Actualizar historial de versiones EIPD"}
      </button>
      {consultationOnly && reviewLock && (
        <div className="space-y-2 rounded border border-amber-300 bg-amber-50 p-3">
          <p role="status">
            Hay una revisión o actuación de facultad en curso o pendiente. Resuélvela para
            actualizar la lista o cambiar de versión.
          </p>
          <button
            type="button"
            className={button}
            onClick={() => openDisclosure(reviewSection.current)}
          >
            Ir a Revisiones y facultades
          </button>
        </div>
      )}
      {consultationOnly && decisionLock && (
        <div className="space-y-2 rounded border border-amber-300 bg-amber-50 p-3">
          <p role="status">
            Hay una decisión o actuación de facultad de decisión en curso o pendiente. Resuélvela
            para actualizar la lista o cambiar de versión.
          </p>
          <button
            type="button"
            className={button}
            onClick={() => openDisclosure(decisionSection.current)}
          >
            Ir a Decisión de la organización
          </button>
        </div>
      )}
      {!consultationOnly && (
        <button
          type="button"
          className={button}
          aria-expanded={historyOpen}
          onClick={() => setHistoryOpen(!historyOpen)}
        >
          {historyOpen
            ? "Ocultar historial de versiones EIPD"
            : "Mostrar historial de versiones EIPD"}
        </button>
      )}
      <p>
        {history
          ? history.length
            ? `${history.length} versiones registradas · última versión: ${Math.max(...history.map((v) => v.version))}.`
            : "No hay versiones EIPD registradas en esta evaluación."
          : "Consultando versiones registradas…"}
      </p>
      {historyError && <p role="alert">{historyError}</p>}
      {history && historyOpen && (!consultationOnly || !detail) && (
        <div className="space-y-2">
          <h4 className="font-semibold">Versiones EIPD registradas</h4>
          {[...history]
            .sort((a, b) => (consultationOnly ? b.version - a.version : a.version - b.version))
            .map((v) => (
              <div key={v.id} className="rounded border bg-white p-3">
                <p>
                  Versión EIPD {v.version} · {v.created_at} · {v.reason}
                </p>
                <button
                  type="button"
                  className={button}
                  disabled={busy || acting}
                  onClick={() =>
                    void action(async () => {
                      const v2 = await eipdVersionsApi.detail(await scope(), v.id);
                      if (alive.current) {
                        setDetail(v2);
                        if (consultationOnly)
                          requestAnimationFrame(() => detailHeading.current?.focus());
                        setConfirmCopy(false);
                      }
                    })
                  }
                >
                  Consultar versión EIPD {v.version}
                </button>
              </div>
            ))}
        </div>
      )}
      {detail && (
        <article
          aria-label={`Versión EIPD ${detail.version} consultada`}
          className="space-y-3 rounded border bg-white p-4"
        >
          {consultationOnly && (
            <button
              type="button"
              className={button}
              disabled={busy || acting}
              onClick={() => {
                setDetail(null);
                listButton.current?.focus();
              }}
            >
              Volver a versiones EIPD
            </button>
          )}
          <h4 ref={detailHeading} tabIndex={-1} className="text-lg font-semibold">
            Versión EIPD {detail.version} consultada
          </h4>
          <p>
            Registro histórico de solo lectura. No acredita vigencia del contexto actual ni
            aprobación.
          </p>
          <dl>
            <dt className="font-semibold">Motivo del registro</dt>
            <dd>{detail.reason}</dd>
            <dt className="font-semibold">Fecha registrada (UTC)</dt>
            <dd>{detail.created_at}</dd>
            <dt className="font-semibold">Registrada por (identificador)</dt>
            <dd className="break-all">{detail.created_by}</dd>
          </dl>
          {consultationOnly ? (
            <>
              <p>
                Referencia:{" "}
                {String(
                  detail.bundle.saved_assessment.eipd_resolution_assessment.document_reference ??
                    "Sin referencia"
                )}
              </p>
            </>
          ) : (
            <MaterialView value={detail.bundle} />
          )}
          {consultationOnly && (
            <p className="rounded border border-blue-200 bg-blue-50 p-3 text-sm">
              <strong>Orden para aceptar esta versión.</strong> Consulta la última conclusión en{" "}
              <strong>Revisiones y facultades</strong>. Si falta, regístrala allí. Con una revisión{" "}
              <strong>Favorable</strong>, consulta <strong>Decisión de la organización</strong> para
              comprobar si <strong>Acepta</strong> está disponible.
            </p>
          )}
          <div ref={reviewSection}>
            <EipdVersionReviews
              key={detail.id}
              version={detail}
              scope={scope}
              onLock={setReviewLock}
              showActionMenu={consultationOnly}
              adjacentActions={
                consultationOnly && (
                  <>
                    <button
                      type="button"
                      className={button}
                      onClick={() => openDisclosure(decisionSection.current)}
                    >
                      Decisión de la organización
                    </button>
                    <button
                      type="button"
                      className={button}
                      onClick={() => openDisclosure(contentSection.current)}
                    >
                      Contenido conservado
                    </button>
                    <button
                      type="button"
                      className={button}
                      onClick={() => openDisclosure(contextSection.current)}
                    >
                      Contexto y antecedentes
                    </button>
                  </>
                )
              }
            />
          </div>
          {consultationOnly && (
            <>
              <div ref={decisionSection}>
                <EipdVersionDecisions
                  key={detail.id}
                  version={detail}
                  scope={scope}
                  onLock={setDecisionLock}
                  documentLabel={`Versión EIPD ${detail.version} · ${String(
                    detail.bundle.saved_assessment.eipd_resolution_assessment.document_reference ??
                      "Sin referencia"
                  )}`}
                />
              </div>
              <div ref={contentSection}>
                <MaterialView value={detail.bundle} expandedDocument={false} showContext={false} />
              </div>
              <div ref={contextSection} className="space-y-3">
                <p>
                  Se conserva el diagnóstico, la determinación, la política y el contexto
                  consultados al registrar. Los respaldos históricos no acreditan controles
                  actuales. Los archivos anexos no se copian dentro de esta versión.
                </p>
                <EipdVersionContext value={detail.bundle} />
              </div>
            </>
          )}
          <details>
            <summary className={documentDisclosureClass}>Identidad de la versión EIPD</summary>
            <p className="break-all">Identificador: {detail.id}</p>
            <p className="break-all">Huella del contenido: {detail.bundle_hash}</p>
            <p className="break-all">
              Versión precedente: {detail.bundle.predecessor_id ?? "Primera versión"}
            </p>
          </details>
          {onCopy && (
            <button
              type="button"
              className={button}
              disabled={disabled || !canCopy}
              onClick={() => setConfirmCopy(true)}
            >
              Preparar borrador desde esta versión EIPD
            </button>
          )}
          {confirmCopy && onCopy && (
            <div className="space-y-2 rounded border border-amber-400 bg-amber-50 p-3">
              <p>
                Se reemplazarán los campos del borrador en esta pestaña con una copia del documento
                de esta versión. {draftDirty && "Hay cambios sin guardar que se reemplazarán."} El
                original, el borrador del servidor y las versiones registradas no cambian. No se
                copian decisiones ni se declara vigente una valoración histórica.
              </p>
              <button
                type="button"
                className={button}
                disabled={disabled || !canCopy}
                onClick={() => {
                  if (!canCopy) return;
                  onCopy(editableEipd(detail.bundle.saved_assessment.eipd_resolution_assessment));
                  setPreview(null);
                  setReviewed(false);
                  setConfirmCopy(false);
                  setMessage(
                    "Copia preparada en el borrador de esta pestaña. Revísala y guárdala explícitamente antes de registrar otra versión."
                  );
                }}
              >
                Reemplazar borrador con esta copia
              </button>
              <button type="button" className={button} onClick={() => setConfirmCopy(false)}>
                Conservar mi borrador actual
              </button>
            </div>
          )}
        </article>
      )}
      {consultationOnly && (
        <>
          {error && <p role="alert">{error}</p>}
          {(busy || message) && <p role="status">{busy ? "Consultando versión EIPD…" : message}</p>}
        </>
      )}
      {children}
      {!consultationOnly && (
        <section
          aria-label="Registrar versión EIPD"
          className="space-y-3 rounded border bg-white p-4"
        >
          <h3 className="text-lg font-semibold">Registrar una versión del borrador guardado</h3>
          {onCopy && (
            <p>
              Los siete pasos pertenecen a un mismo borrador. Guarda sus cambios antes de preparar
              el registro de una versión.
            </p>
          )}
          {blockedReason && <p>{blockedReason}</p>}
          {onCopy && (
            <button
              type="button"
              className={button}
              disabled={disabled || !canRegister}
              onClick={() =>
                void action(async () => {
                  const v = await eipdVersionsApi.preview(await scope());
                  if (alive.current) {
                    setPreview(v);
                    setReviewed(false);
                    setFictitious(false);
                  }
                })
              }
            >
              Preparar registro de versión EIPD
            </button>
          )}
          {preview && !pending && (
            <div
              className="space-y-3 rounded border bg-white p-3"
              aria-label="Vista previa para registrar versión EIPD"
            >
              <h4 className="text-lg font-semibold">
                Vista previa del contenido guardado para registrar
              </h4>
              <p>
                Próxima versión prevista: {preview.latest_version + 1}. El servidor verificará
                nuevamente el origen y la secuencia al registrar. Esta consulta no guarda ni
                registra.
              </p>
              <MaterialView value={preview.bundle} />
              <label className="block" htmlFor={id + "-reason"}>
                Motivo del registro de versión EIPD
              </label>
              <textarea
                id={id + "-reason"}
                className="block w-full rounded border p-2"
                maxLength={4000}
                disabled={disabled}
                value={reason}
                onChange={(e) => setReason(e.target.value)}
              />
              <label className="block">
                <input
                  type="checkbox"
                  checked={fictitious}
                  disabled={disabled}
                  onChange={(e) => setFictitious(e.target.checked)}
                />{" "}
                Declaro datos ficticios para esta versión EIPD
              </label>
              <label className="block">
                <input
                  type="checkbox"
                  checked={reviewed}
                  disabled={disabled}
                  onChange={(e) => setReviewed(e.target.checked)}
                />{" "}
                He leído el contenido guardado y sus pendientes antes de registrar
              </label>
              <p>
                Registrar conserva esta versión exacta. Las versiones anteriores no se reemplazan.
                La confirmación y activación EIPD permanecen bloqueadas.
              </p>
              <button
                type="button"
                className={button}
                disabled={disabled || !canRegister || !reason.trim() || !fictitious || !reviewed}
                onClick={() => {
                  if (running.current) return;
                  const body: VersionRequest = {
                    request_id: crypto.randomUUID(),
                    data_kind: "ficticios",
                    expected_source_hash: preview.source_hash,
                    expected_latest_version: preview.latest_version,
                    reason: reason.trim(),
                  };
                  setPending(body);
                  void action(() => send(body));
                }}
              >
                Registrar versión documental EIPD
              </button>
              <button
                type="button"
                className={button}
                disabled={disabled}
                onClick={() => {
                  setPreview(null);
                  setReason("");
                  setReviewed(false);
                  setFictitious(false);
                }}
              >
                Cancelar preparación de registro
              </button>
            </div>
          )}
          {pending && (
            <div className="space-y-3 rounded border border-amber-400 bg-amber-50 p-3">
              <p>
                Solicitud de registro pendiente de comprobar. Conserva abierta esta pestaña hasta
                resolverla.
              </p>
              <button
                type="button"
                className={button}
                disabled={busy || acting}
                onClick={() =>
                  void action(async () => {
                    try {
                      accepted(await eipdVersionsApi.lookup(await scope(), pending.request_id));
                    } catch (e) {
                      if (e instanceof ApiError && e.status === 404) {
                        if (alive.current) {
                          setMissing(true);
                          setMessage(
                            "La consulta aún no encuentra esta solicitud. Puedes reintentar el mismo registro con el mismo identificador y contenido; no se prepara otro."
                          );
                        }
                      } else throw e;
                    }
                  })
                }
              >
                Consultar resultado del registro EIPD
              </button>
              {missing && (
                <button
                  type="button"
                  className={button}
                  disabled={busy || acting}
                  onClick={() => void action(() => send(pending))}
                >
                  Reintentar el mismo registro EIPD
                </button>
              )}
            </div>
          )}
          {error && (
            <p role="alert" className="rounded border border-red-300 bg-red-50 p-3">
              {error}
            </p>
          )}
          {(busy || message) && (
            <p role="status">{busy ? "Consultando o registrando versión EIPD…" : message}</p>
          )}
        </section>
      )}
    </section>
  );
}
