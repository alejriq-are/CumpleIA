"use client";
import { useEffect, useRef, useState } from "react";
import { apiFetch, ApiError } from "@/lib/api/client";
import type { RegisteredVersion, VersionScope } from "@/lib/api/eipd-versions";
import { documentNavigationButtonClass as button } from "./document-focus";

type Review = {
  id: string;
  version_id: string;
  sequence: number;
  previous_id: string | null;
  outcome: "favorable" | "requiere_cambios" | "no_continuar";
  reason: string;
  reference: string;
  created_by: string;
  created_at: string;
  request_id: string;
  authority_id: string;
};
type Faculty = {
  id: string;
  subject_id: string;
  action: "grant" | "revoke";
  sequence: number;
  reason: string;
  reference: string;
  created_by: string;
  created_at: string;
  expires_at: string | null;
};
type State = {
  version_id: string;
  organization_id: string;
  treatment_id: string;
  assessment_id: string;
  reviews: Review[];
  authority_id: string | null;
  can_review: boolean;
  blocked_reason: string | null;
  can_favorable: boolean;
  may_manage: boolean;
  authorities: Faculty[];
};
type Request = {
  request_id: string;
  data_kind: "ficticios";
  authority_id: string;
  expected_previous_id: string | null;
  outcome: Review["outcome"];
  reason: string;
  reference: string;
};
const labels = {
  favorable: "Favorable",
  requiere_cambios: "Requiere cambios",
  no_continuar: "No continuar",
};

export function EipdVersionReviews({
  version,
  scope,
  onLock,
}: {
  version: RegisteredVersion;
  scope: () => Promise<VersionScope>;
  onLock: (value: boolean) => void;
}) {
  const [state, setState] = useState<State | null>(null);
  const [busy, setBusy] = useState(false);
  const working = useRef(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [outcome, setOutcome] = useState<Review["outcome"]>("requiere_cambios");
  const [reason, setReason] = useState("");
  const [reference, setReference] = useState("");
  const [fictitious, setFictitious] = useState(false);
  const [pending, setPending] = useState<Request | null>(null);
  const [missing, setMissing] = useState(false);
  const [subject, setSubject] = useState("");
  const [facultyReason, setFacultyReason] = useState("");
  const [facultyReference, setFacultyReference] = useState("");
  const [expires, setExpires] = useState("");
  const [facultyAction, setFacultyAction] = useState<"grant" | "revoke">("grant");
  const dirty =
    !!reason.trim() || !!reference.trim() || !!facultyReason.trim() || !!facultyReference.trim();
  useEffect(() => {
    onLock(busy || !!pending || dirty);
  }, [busy, pending, dirty, onLock]);
  useEffect(() => {
    if (!dirty && !pending) return;
    const warn = (event: BeforeUnloadEvent) => {
      event.preventDefault();
    };
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, [dirty, pending]);
  const path = (s: VersionScope) =>
    `/licitud/treatments/${encodeURIComponent(s.treatmentId)}/assessments/${encodeURIComponent(s.assessmentId)}/eipd-versions/v1`;
  async function read() {
    const s = await scope();
    const v = await apiFetch<State>(path(s) + "/" + version.id + "/review-state", {
      ...s,
      cache: "no-store",
    });
    if (
      !v ||
      v.version_id !== version.id ||
      v.organization_id !== s.organizationId ||
      v.treatment_id !== s.treatmentId ||
      v.assessment_id !== s.assessmentId ||
      !Array.isArray(v.reviews) ||
      !Array.isArray(v.authorities) ||
      typeof v.can_review !== "boolean" ||
      typeof v.can_favorable !== "boolean" ||
      v.reviews.some((r) => r.version_id !== version.id || !(r.outcome in labels))
    ) {
      throw new Error("Respuesta de revisión incompatible. Consulta de nuevo.");
    }
    setState(v);
    return v;
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
      setError(e instanceof Error ? e.message : "No se pudo completar la actuación");
    } finally {
      working.current = false;
      setBusy(false);
    }
  }
  async function accepted(v: Review, body: Request) {
    if (
      v.version_id !== version.id ||
      v.request_id !== body.request_id ||
      v.outcome !== body.outcome ||
      v.reason !== body.reason ||
      v.reference !== body.reference
    ) {
      throw new Error("Respuesta incompatible; conserva la solicitud y consulta su resultado.");
    }
    setPending(null);
    setMissing(false);
    setReason("");
    setReference("");
    setFictitious(false);
    setMessage("Revisión registrada. No activa ni acepta la EIPD.");
    await read();
  }
  async function send(body: Request) {
    const s = await scope();
    try {
      const v = await apiFetch<Review>(path(s) + "/" + version.id + "/reviews", {
        ...s,
        method: "POST",
        body,
        cache: "no-store",
      });
      await accepted(v, body);
    } catch (e) {
      if (e instanceof ApiError && [403, 404, 409, 422].includes(e.status)) {
        setPending(null);
        setState(null);
      }
      throw e;
    }
  }
  return (
    <section aria-label="Revisión de la versión EIPD" className="space-y-3 rounded border p-3">
      <h5 className="font-semibold">Revisiones de la versión {version.version}</h5>
      <p>
        Referencia:{" "}
        {String(
          version.bundle.saved_assessment.eipd_resolution_assessment.document_reference ||
            "Sin referencia"
        )}
        . Cada conclusión corresponde exclusivamente a esta versión conservada.
      </p>
      <button
        type="button"
        className={button}
        disabled={busy || !!pending}
        onClick={() =>
          void action(async () => {
            await read();
          })
        }
      >
        Consultar revisiones y facultades
      </button>
      {state && (
        <>
          <ol className="space-y-3">
            {state.reviews.map((r) => (
              <li key={r.id} className="rounded border p-3">
                <p>
                  {r.sequence}. {labels[r.outcome]}
                </p>
                <p className="whitespace-pre-wrap">{r.reason}</p>
                <p>Referencia: {r.reference}</p>
                <p className="break-all">Persona revisora: {r.created_by}</p>
                <p>Fecha (UTC): {r.created_at}</p>
              </li>
            ))}
          </ol>
          {!state.reviews.length && <p>Esta versión todavía no tiene revisiones.</p>}
          {state.blocked_reason && <p>{state.blocked_reason}</p>}
          {!state.can_favorable && (
            <p>
              Favorable está bloqueado: los requisitos documentales de esta versión conservada no
              están completos.
            </p>
          )}
          <form
            className="space-y-2"
            onSubmit={(e) => {
              e.preventDefault();
              if (!state.can_review || !state.authority_id || pending || working.current) return;
              const body: Request = {
                request_id: crypto.randomUUID(),
                data_kind: "ficticios",
                authority_id: state.authority_id,
                expected_previous_id: state.reviews.at(-1)?.id ?? null,
                outcome,
                reason: reason.trim(),
                reference: reference.trim(),
              };
              setPending(body);
              void action(() => send(body));
            }}
          >
            <label className="block">
              Resultado
              <select
                className="block rounded border p-2"
                value={outcome}
                disabled={busy || !!pending || !state.can_review}
                onChange={(e) => setOutcome(e.target.value as Review["outcome"])}
              >
                {Object.entries(labels).map(([v, label]) => (
                  <option key={v} value={v} disabled={v === "favorable" && !state.can_favorable}>
                    {label}
                  </option>
                ))}
              </select>
            </label>
            <label className="block">
              Fundamento de la revisión
              <textarea
                className="block w-full rounded border p-2"
                maxLength={4000}
                value={reason}
                disabled={busy || !!pending}
                onChange={(e) => setReason(e.target.value)}
              />
            </label>
            <label className="block">
              Referencia de respaldo de la revisión
              <input
                className="block w-full rounded border p-2"
                maxLength={1000}
                value={reference}
                disabled={busy || !!pending}
                onChange={(e) => setReference(e.target.value)}
              />
            </label>
            <label className="block">
              <input
                type="checkbox"
                checked={fictitious}
                disabled={busy || !!pending}
                onChange={(e) => setFictitious(e.target.checked)}
              />{" "}
              Declaro datos ficticios para esta revisión
            </label>
            <button
              className={button}
              disabled={
                busy ||
                !!pending ||
                !state.can_review ||
                !fictitious ||
                !reason.trim() ||
                !reference.trim() ||
                (outcome === "favorable" && !state.can_favorable)
              }
            >
              {state.reviews.length ? "Registrar reconsideración" : "Registrar revisión"}
            </button>
          </form>
          <details>
            <summary>Historial de facultades del expediente</summary>
            <ul>
              {state.authorities.map((f) => (
                <li key={f.id} className="my-2 break-words">
                  {f.subject_id}: {f.action === "grant" ? "Otorgamiento" : "Revocación"} (
                  {f.sequence}). {f.reason}. Referencia: {f.reference}. Por: {f.created_by}. Fecha
                  (UTC): {f.created_at}. Vencimiento: {f.expires_at ?? "Sin vencimiento"}.
                </li>
              ))}
            </ul>
          </details>
          {state.may_manage && (
            <details>
              <summary>Administrar facultad de revisión del expediente</summary>
              <p>
                La facultad permite revisar y no autoriza decisiones de la organización. No puedes
                otorgártela.
              </p>
              <form
                className="space-y-2"
                onSubmit={(e) => {
                  e.preventDefault();
                  void action(async () => {
                    const s = await scope();
                    const previous = state.authorities
                      .filter((f) => f.subject_id === subject.trim())
                      .at(-1);
                    await apiFetch(path(s) + "/review-authorities", {
                      ...s,
                      method: "POST",
                      body: {
                        subject_id: subject.trim(),
                        action: facultyAction,
                        expected_sequence: previous?.sequence ?? 0,
                        reason: facultyReason.trim(),
                        reference: facultyReference.trim(),
                        expires_at:
                          facultyAction === "grant" && expires
                            ? new Date(expires).toISOString()
                            : null,
                      },
                    });
                    setFacultyReason("");
                    setFacultyReference("");
                    setMessage("Actuación de facultad registrada.");
                    await read();
                  });
                }}
              >
                <fieldset disabled={busy || !!pending} className="min-w-0 space-y-2">
                  <label className="block">
                    Identificador de la persona destinataria
                    <input
                      className="block w-full rounded border p-2"
                      required
                      value={subject}
                      onChange={(e) => setSubject(e.target.value)}
                    />
                  </label>
                  <label className="block">
                    Actuación
                    <select
                      value={facultyAction}
                      onChange={(e) => setFacultyAction(e.target.value as "grant" | "revoke")}
                    >
                      <option value="grant">Otorgar</option>
                      <option value="revoke">Revocar</option>
                    </select>
                  </label>
                  <label className="block">
                    Motivo de la facultad
                    <textarea
                      required
                      maxLength={4000}
                      className="block w-full rounded border p-2"
                      value={facultyReason}
                      onChange={(e) => setFacultyReason(e.target.value)}
                    />
                  </label>
                  <label className="block">
                    Referencia de respaldo de la facultad
                    <input
                      required
                      maxLength={1000}
                      className="block w-full rounded border p-2"
                      value={facultyReference}
                      onChange={(e) => setFacultyReference(e.target.value)}
                    />
                  </label>
                  <label className="block">
                    Vencimiento opcional (hora local)
                    <input
                      type="datetime-local"
                      disabled={facultyAction === "revoke"}
                      value={expires}
                      onChange={(e) => setExpires(e.target.value)}
                    />
                  </label>
                  <button
                    className={button}
                    disabled={
                      busy || !!pending || !facultyReason.trim() || !facultyReference.trim()
                    }
                  >
                    Registrar actuación de facultad
                  </button>
                </fieldset>
              </form>
            </details>
          )}
        </>
      )}
      {dirty && !pending && (
        <button
          type="button"
          className={button}
          disabled={busy}
          onClick={() => {
            setReason("");
            setReference("");
            setFictitious(false);
            setFacultyReason("");
            setFacultyReference("");
            setExpires("");
          }}
        >
          Descartar campos de revisión y facultad sin registrar
        </button>
      )}
      {pending && (
        <div className="space-y-2">
          <p>Resultado pendiente de comprobar. Mantén abierta esta versión y esta pestaña.</p>
          <button
            className={button}
            disabled={busy}
            onClick={() =>
              void action(async () => {
                const s = await scope();
                try {
                  const v = await apiFetch<Review>(
                    path(s) + "/" + version.id + "/review-requests/" + pending.request_id,
                    { ...s, cache: "no-store" }
                  );
                  await accepted(v, pending);
                } catch (e) {
                  if (e instanceof ApiError && e.status === 404) {
                    setMissing(true);
                    setMessage("Solicitud no encontrada; puedes reintentar la misma revisión.");
                  } else throw e;
                }
              })
            }
          >
            Consultar resultado de la revisión
          </button>
          {missing && (
            <button
              className={button}
              disabled={busy}
              onClick={() => void action(() => send(pending))}
            >
              Reintentar la misma revisión
            </button>
          )}
        </div>
      )}
      {error && <p role="alert">{error}</p>}
      {(busy || message) && (
        <p role="status" aria-label="Estado de revisión EIPD">
          {busy ? "Consultando o registrando revisión…" : message}
        </p>
      )}
    </section>
  );
}
