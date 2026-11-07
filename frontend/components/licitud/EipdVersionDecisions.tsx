"use client";

import { useEffect, useRef, useState } from "react";
import { apiFetch, ApiError } from "@/lib/api/client";
import type { RegisteredVersion, VersionScope } from "@/lib/api/eipd-versions";
import {
  documentDisclosureClass,
  documentNavigationButtonClass as button,
  focusDocumentSection,
} from "./document-focus";

const outcomes = {
  acepta: "Acepta",
  requiere_cambios: "Requiere cambios",
  rechaza: "Rechaza",
};
type Outcome = keyof typeof outcomes;
type Request = {
  request_id: string;
  data_kind: "ficticios";
  expected_authority_id: string;
  expected_review_id: string | null;
  expected_decision_id: string | null;
  outcome: Outcome;
  reason: string;
  reference: string;
};
type Decision = {
  id: string;
  organization_id: string;
  treatment_id: string;
  assessment_id: string;
  version_id: string;
  request_id: string;
  sequence: number;
  review_id: string | null;
  authority_id: string;
  previous_id: string | null;
  outcome: Outcome;
  reason: string;
  reference: string;
  created_by: string;
  created_at: string;
};
type Faculty = {
  id: string;
  sequence: number;
  action: "grant" | "revoke";
  subject_id: string;
  created_by: string;
  created_at: string;
  expires_at: string | null;
  compatibility_reason: string | null;
  reason: string;
  reference: string;
};
type DecisionState = {
  organization_id: string;
  treatment_id: string;
  assessment_id: string;
  version_id: string;
  decisions: Decision[];
  authorities: Faculty[];
  latest_review_id: string | null;
  authority_id: string | null;
  may_manage: boolean;
  can_decide: boolean;
  can_accept: boolean;
  blocked_reason: string | null;
  acceptance_blocked_reason: string | null;
};
const emptyFaculty = {
  subject: "",
  action: "grant" as Faculty["action"],
  reason: "",
  reference: "",
  expires: "",
  compatibility: "",
};

export function EipdVersionDecisions({
  version,
  scope,
  onLock,
}: {
  version: RegisteredVersion;
  scope: () => Promise<VersionScope>;
  onLock: (locked: boolean) => void;
}) {
  const [state, setState] = useState<DecisionState | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [refreshRequired, setRefreshRequired] = useState(false);
  const [outcome, setOutcome] = useState<Outcome>("requiere_cambios");
  const [reason, setReason] = useState("");
  const [reference, setReference] = useState("");
  const [fictitious, setFictitious] = useState(false);
  const [pending, setPending] = useState<Request | null>(null);
  const [missing, setMissing] = useState(false);
  const [faculty, setFaculty] = useState(emptyFaculty);
  const [facultyUncertain, setFacultyUncertain] = useState(false);
  const working = useRef(false);
  const dirty = Boolean(
    reason.trim() ||
    reference.trim() ||
    fictitious ||
    faculty.subject.trim() ||
    faculty.reason.trim() ||
    faculty.reference.trim() ||
    faculty.compatibility.trim() ||
    faculty.expires
  );
  const locked = dirty || busy || !!pending || facultyUncertain;
  useEffect(() => onLock(locked), [locked, onLock]);
  useEffect(() => {
    if (!locked) return;
    const warn = (event: BeforeUnloadEvent) => event.preventDefault();
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, [locked]);

  const path = (s: VersionScope) =>
    `/licitud/treatments/${encodeURIComponent(s.treatmentId)}/assessments/${encodeURIComponent(s.assessmentId)}/eipd-versions/v1`;
  const versionPath = (s: VersionScope) => path(s) + "/" + version.id;
  function matchesVersion(
    value: Pick<
      Decision,
      "organization_id" | "treatment_id" | "assessment_id" | "version_id"
    > | null
  ) {
    return (
      value?.version_id === version.id &&
      value.organization_id === version.organization_id &&
      value.treatment_id === version.treatment_id &&
      value.assessment_id === version.assessment_id
    );
  }

  async function read() {
    const s = await scope();
    const value = await apiFetch<DecisionState>(versionPath(s) + "/decision-state", {
      ...s,
      cache: "no-store",
    });
    if (
      !matchesVersion(value) ||
      !Array.isArray(value.decisions) ||
      !value.decisions.every((d) => matchesVersion(d) && Object.hasOwn(outcomes, d.outcome)) ||
      !Array.isArray(value.authorities) ||
      typeof value.can_decide !== "boolean" ||
      typeof value.can_accept !== "boolean" ||
      typeof value.may_manage !== "boolean"
    ) {
      throw new Error("Respuesta de decisión incompatible. Vuelve a consultar.");
    }
    setState(value);
    setRefreshRequired(false);
    if (facultyUncertain) {
      setFacultyUncertain(false);
      setMessage(
        "Historial actualizado. Comprueba si la actuación de facultad figura antes de volver a enviarla."
      );
    }
  }
  async function action(fn: () => Promise<void>) {
    if (working.current) return;
    working.current = true;
    setBusy(true);
    setError("");
    setMessage("");
    try {
      await fn();
    } catch (e) {
      setError(e instanceof Error ? e.message : "No se pudo completar la actuación.");
    } finally {
      working.current = false;
      setBusy(false);
    }
  }
  async function accepted(value: Decision, body: Request) {
    if (
      !matchesVersion(value) ||
      value.request_id !== body.request_id ||
      value.authority_id !== body.expected_authority_id ||
      value.review_id !== body.expected_review_id ||
      value.previous_id !== body.expected_decision_id ||
      value.outcome !== body.outcome ||
      value.reason !== body.reason ||
      value.reference !== body.reference
    ) {
      throw new Error("Respuesta incompatible. Consulta el resultado de la solicitud.");
    }
    setPending(null);
    setMissing(false);
    setReason("");
    setReference("");
    setFictitious(false);
    setOutcome("requiere_cambios");
    setMessage("Decisión documental registrada.");
    setRefreshRequired(true);
    await read();
  }
  async function send(body: Request) {
    const s = await scope();
    let value: Decision;
    try {
      value = await apiFetch<Decision>(versionPath(s) + "/decisions", {
        ...s,
        method: "POST",
        body,
      });
    } catch (e) {
      if (e instanceof ApiError && [400, 403, 404, 409, 422].includes(e.status)) {
        setPending(null);
        setMissing(false);
        setRefreshRequired(true);
        if (e.status === 409) {
          throw new Error(
            `${e.message} Tus campos se conservan. Consulta decisiones y facultades antes de reintentar.`
          );
        }
      }
      throw e;
    }
    await accepted(value, body);
  }

  async function recover(body: Request) {
    const s = await scope();
    try {
      const value = await apiFetch<Decision>(
        versionPath(s) + "/decision-requests/" + body.request_id,
        {
          ...s,
          cache: "no-store",
        }
      );
      await accepted(value, body);
    } catch (e) {
      if (e instanceof ApiError && e.status === 404) {
        setMissing(true);
        setMessage("Solicitud sin resultado registrado. Puedes reintentar la misma decisión.");
      } else throw e;
    }
  }

  async function designate(current: DecisionState) {
    const s = await scope();
    const subject = faculty.subject.trim().toLowerCase();
    const last = current.authorities.filter((a) => a.subject_id === subject).at(-1);
    try {
      await apiFetch(path(s) + "/decision-authorities", {
        ...s,
        method: "POST",
        body: {
          subject_id: subject,
          action: faculty.action,
          expected_sequence: last?.sequence ?? 0,
          reason: faculty.reason.trim(),
          reference: faculty.reference.trim(),
          expires_at:
            faculty.action === "grant" && faculty.expires
              ? new Date(faculty.expires).toISOString()
              : null,
          compatibility_reason:
            faculty.action === "grant" ? faculty.compatibility.trim() || null : null,
        },
      });
    } catch (e) {
      if (!(e instanceof ApiError) || e.status >= 500) setFacultyUncertain(true);
      setRefreshRequired(true);
      throw e;
    }
    setFaculty(emptyFaculty);
    setMessage("Actuación de facultad de decisión registrada.");
    setRefreshRequired(true);
    await read();
  }

  return (
    <details className="space-y-3 rounded border p-3">
      <summary className={documentDisclosureClass}>Decisión de la organización</summary>
      <p>
        Versión EIPD {version.version} ·{" "}
        {String(
          version.bundle.saved_assessment.eipd_resolution_assessment.document_reference ??
            "Sin referencia"
        )}
      </p>
      <p>
        La decisión documental queda asociada a esta versión. Confirmación y activación permanecen
        bloqueadas.
      </p>
      <button
        type="button"
        className={button}
        disabled={busy || !!pending}
        onClick={() => void action(read)}
      >
        Consultar decisiones y facultades
      </button>
      {error && (
        <p
          key={error}
          ref={focusDocumentSection}
          tabIndex={-1}
          role="alert"
          className="rounded border border-red-300 bg-red-50 p-3"
        >
          {error}
        </p>
      )}
      {message && <p role="status">{message}</p>}
      {state && (
        <>
          <h5 className="font-semibold">Historial de decisiones de la versión {version.version}</h5>
          {state.decisions.length === 0 && <p>Esta versión todavía no tiene decisiones.</p>}
          {state.decisions.length > 0 && (
            <ol className="space-y-2">
              {state.decisions.map((d) => (
                <li key={d.id} className="break-words rounded border p-3">
                  <p className="font-semibold">
                    {d.sequence}. {outcomes[d.outcome]}
                  </p>
                  <p>{d.reason}</p>
                  <p>Referencia del acta: {d.reference}</p>
                  <p>
                    Persona decisora: {d.created_by} · Fecha (UTC): {d.created_at}
                  </p>
                  <p>
                    Revisión vinculada: {d.review_id ?? "Sin revisión"} · Facultad utilizada:{" "}
                    {d.authority_id}
                  </p>
                </li>
              ))}
            </ol>
          )}
          {state.blocked_reason && <p>{state.blocked_reason}</p>}
          {state.can_decide && state.acceptance_blocked_reason && (
            <p>Acepta está bloqueado. {state.acceptance_blocked_reason}</p>
          )}
          {(state.can_decide || dirty) && (
            <form
              className="space-y-2"
              onSubmit={(e) => {
                e.preventDefault();
                if (
                  !state.can_decide ||
                  !state.authority_id ||
                  refreshRequired ||
                  pending ||
                  facultyUncertain ||
                  (outcome === "acepta" && !state.can_accept) ||
                  !reason.trim() ||
                  !reference.trim() ||
                  !fictitious
                )
                  return;
                const body: Request = {
                  request_id: crypto.randomUUID(),
                  data_kind: "ficticios",
                  expected_authority_id: state.authority_id,
                  expected_review_id: state.latest_review_id,
                  expected_decision_id: state.decisions.at(-1)?.id ?? null,
                  outcome,
                  reason: reason.trim(),
                  reference: reference.trim(),
                };
                setPending(body);
                setMissing(false);
                void action(() => send(body));
              }}
            >
              <fieldset
                disabled={busy || !!pending || facultyUncertain}
                className="min-w-0 space-y-2"
              >
                <label className="block">
                  Resultado de la decisión
                  <select
                    className="block rounded border p-2"
                    value={outcome}
                    onChange={(e) => setOutcome(e.target.value as Outcome)}
                  >
                    {Object.entries(outcomes).map(([value, label]) => (
                      <option
                        key={value}
                        value={value}
                        disabled={value === "acepta" && !state.can_accept}
                      >
                        {label}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="block">
                  Fundamento de la decisión
                  <textarea
                    className="block w-full rounded border p-2"
                    required
                    maxLength={4000}
                    value={reason}
                    onChange={(e) => setReason(e.target.value)}
                  />
                </label>
                <label className="block">
                  Referencia del acta
                  <input
                    className="block w-full rounded border p-2"
                    required
                    maxLength={1000}
                    value={reference}
                    onChange={(e) => setReference(e.target.value)}
                  />
                </label>
                <label className="block">
                  <input
                    type="checkbox"
                    checked={fictitious}
                    onChange={(e) => setFictitious(e.target.checked)}
                  />{" "}
                  Declaro datos ficticios para esta decisión
                </label>
                <button
                  className={button}
                  disabled={
                    refreshRequired ||
                    !state.can_decide ||
                    !state.authority_id ||
                    !reason.trim() ||
                    !reference.trim() ||
                    !fictitious ||
                    (outcome === "acepta" && !state.can_accept)
                  }
                >
                  {state.decisions.length
                    ? "Registrar reconsideración de la decisión"
                    : "Registrar decisión"}
                </button>
              </fieldset>
            </form>
          )}
          <details>
            <summary className={documentDisclosureClass}>
              Historial de facultades de decisión
            </summary>
            {state.authorities.length === 0 && (
              <p>Todavía no hay actuaciones de facultad de decisión.</p>
            )}
            <ul className="space-y-2">
              {state.authorities.map((a) => (
                <li key={a.id} className="break-words rounded border p-3">
                  <p>
                    {a.subject_id} · {a.action === "grant" ? "Otorgamiento" : "Revocación"}{" "}
                    {a.sequence}
                  </p>
                  <p>
                    {a.reason} · Respaldo: {a.reference}
                  </p>
                  <p>
                    Por: {a.created_by} · Fecha (UTC): {a.created_at} · Vencimiento (UTC):{" "}
                    {a.expires_at ?? "Sin vencimiento"}
                  </p>
                  {a.compatibility_reason && (
                    <p>Compatibilidad documentada: {a.compatibility_reason}</p>
                  )}
                </li>
              ))}
            </ul>
          </details>
          {state.may_manage && (
            <details>
              <summary className={documentDisclosureClass}>
                Administrar facultades de decisión
              </summary>
              <p>
                Otorga esta facultad a otra persona del expediente. Documenta la compatibilidad si
                podrá revisar y decidir sobre la misma versión.
              </p>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  if (
                    busy ||
                    pending ||
                    refreshRequired ||
                    facultyUncertain ||
                    !faculty.reason.trim() ||
                    !faculty.reference.trim()
                  )
                    return;
                  void action(() => designate(state));
                }}
              >
                <fieldset
                  disabled={busy || !!pending || facultyUncertain}
                  className="min-w-0 space-y-2"
                >
                  <label className="block">
                    Identificador de la persona destinataria
                    <input
                      className="block w-full rounded border p-2"
                      required
                      pattern="[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
                      value={faculty.subject}
                      onChange={(e) => setFaculty({ ...faculty, subject: e.target.value })}
                    />
                  </label>
                  <label className="block">
                    Actuación de facultad de decisión
                    <select
                      value={faculty.action}
                      onChange={(e) =>
                        setFaculty({ ...faculty, action: e.target.value as Faculty["action"] })
                      }
                    >
                      <option value="grant">Otorgar</option>
                      <option value="revoke">Revocar</option>
                    </select>
                  </label>
                  <label className="block">
                    Motivo de la facultad de decisión
                    <textarea
                      className="block w-full rounded border p-2"
                      required
                      maxLength={4000}
                      value={faculty.reason}
                      onChange={(e) => setFaculty({ ...faculty, reason: e.target.value })}
                    />
                  </label>
                  <label className="block">
                    Referencia de respaldo de la facultad de decisión
                    <input
                      className="block w-full rounded border p-2"
                      required
                      maxLength={1000}
                      value={faculty.reference}
                      onChange={(e) => setFaculty({ ...faculty, reference: e.target.value })}
                    />
                  </label>
                  {faculty.action === "grant" && (
                    <>
                      <label className="block">
                        Fundamento de compatibilidad de funciones (opcional)
                        <textarea
                          className="block w-full rounded border p-2"
                          maxLength={4000}
                          value={faculty.compatibility}
                          onChange={(e) =>
                            setFaculty({ ...faculty, compatibility: e.target.value })
                          }
                        />
                      </label>
                      <label className="block">
                        Vencimiento opcional (hora local)
                        <input
                          type="datetime-local"
                          value={faculty.expires}
                          onChange={(e) => setFaculty({ ...faculty, expires: e.target.value })}
                        />
                      </label>
                    </>
                  )}
                  <button
                    className={button}
                    disabled={
                      refreshRequired || !faculty.reason.trim() || !faculty.reference.trim()
                    }
                  >
                    Registrar actuación de facultad de decisión
                  </button>
                </fieldset>
              </form>
            </details>
          )}
        </>
      )}
      {dirty && !pending && !facultyUncertain && (
        <button
          type="button"
          className={button}
          disabled={busy}
          onClick={() => {
            setOutcome("requiere_cambios");
            setReason("");
            setReference("");
            setFictitious(false);
            setFaculty(emptyFaculty);
          }}
        >
          Descartar campos de decisión y facultad sin registrar
        </button>
      )}
      {pending && (
        <div className="space-y-2">
          <p>Resultado pendiente de comprobar. Mantén abierta esta versión y esta pestaña.</p>
          <button
            type="button"
            className={button}
            disabled={busy}
            onClick={() => void action(() => recover(pending))}
          >
            Consultar resultado de la solicitud de decisión
          </button>
          {missing && (
            <button
              type="button"
              className={button}
              disabled={busy}
              onClick={() => {
                setMissing(false);
                void action(() => send(pending));
              }}
            >
              Reintentar la misma decisión
            </button>
          )}
        </div>
      )}
    </details>
  );
}
