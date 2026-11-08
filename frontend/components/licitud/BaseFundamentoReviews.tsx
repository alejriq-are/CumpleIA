"use client";

import { useRef, useState } from "react";
import { apiFetch } from "@/lib/api/client";
import type { VersionScope } from "@/lib/api/eipd-versions";
import { documentDisclosureClass, documentNavigationButtonClass as button } from "./document-focus";
import {
  baseVersionPath,
  OperationFeedback,
  RequestRecovery,
  useBaseOperation,
  useBasePending,
  useBaseRequest,
} from "./BaseFundamentoOperation";
import { BaseFundamentoRequirements, requirementTitle } from "./BaseFundamentoRequirements";
import type { BaseVersion, Requirement } from "./BaseFundamentoVersionTypes";

const outcomes = {
  favorable: "Favorable",
  requiere_cambios: "Requiere cambios",
  desfavorable: "Desfavorable",
};
const input = "block w-full min-w-0 rounded border p-2";
type Outcome = keyof typeof outcomes;
type Resolution = Requirement & { justification: string; reference: string | null };
type Observation = { description: string; responsible: string; due_on: string };
type ReviewRequest = {
  request_id: string;
  data_kind: "ficticios";
  authority_id: string;
  expected_previous_id: string | null;
  outcome: Outcome;
  reason: string;
  reference: string;
  resolutions: Resolution[];
  observations: Observation[];
};
type Review = Omit<ReviewRequest, "data_kind" | "expected_previous_id"> & {
  id: string;
  version_id: string;
  sequence: number;
  created_at: string;
  created_by: string;
  organization_id: string;
  treatment_id: string;
  assessment_id: string;
  previous_id: string | null;
};
type Faculty = {
  id: string;
  subject_id: string;
  sequence: number;
  action: "grant" | "revoke";
  reason: string;
  reference: string;
  expires_at: string | null;
  created_at: string;
  created_by: string;
};
type State = {
  version_id: string;
  organization_id: string;
  treatment_id: string;
  assessment_id: string;
  reviews: Review[];
  authorities: Faculty[];
  authority_id: string | null;
  blocked_reason: string | null;
  can_review: boolean;
  can_favorable: boolean;
  may_manage: boolean;
  favorable_requirements: Requirement[];
};

const text = (form: FormData, field: string) => String(form.get(field) ?? "").trim();
const resolutionLabel = (r: Requirement) =>
  r.resolution === "no_aplica" ? "No aplica" : "Respaldo equivalente";
const requirementKey = (r: Requirement) => JSON.stringify([r.criterion_id, r.field, r.code]);

export function BaseFundamentoReviews({
  version,
  scope,
  onPending,
}: {
  version: BaseVersion;
  scope: () => Promise<VersionScope>;
  onPending: (value: boolean) => void;
}) {
  const [state, setState] = useState<State | null>(null);
  const [reviewDirty, setReviewDirty] = useState(false);
  const [facultyDirty, setFacultyDirty] = useState(false);
  const [needsRefresh, setNeedsRefresh] = useState(false);
  const [outcome, setOutcome] = useState<Outcome>("requiere_cambios");
  const [facultyAction, setFacultyAction] = useState<Faculty["action"]>("grant");
  const [observations, setObservations] = useState<string[]>([]);
  const form = useRef<HTMLFormElement>(null);
  const facultyForm = useRef<HTMLFormElement>(null);
  const operation = useBaseOperation();
  const { busy, run, setNotice } = operation;
  const path = (s: VersionScope) => baseVersionPath(s) + "/" + version.id;
  function matches(
    value: Pick<State, "version_id" | "organization_id" | "treatment_id" | "assessment_id"> | null
  ) {
    return (
      value?.version_id === version.id &&
      value.organization_id === version.organization_id &&
      value.treatment_id === version.treatment_id &&
      value.assessment_id === version.assessment_id
    );
  }
  function clearReview() {
    form.current?.reset();
    setOutcome("requiere_cambios");
    setObservations([]);
    setReviewDirty(false);
  }
  const request = useBaseRequest<ReviewRequest, Review>(
    scope,
    (s) => ({ post: path(s) + "/reviews", receipt: path(s) + "/review-requests/" }),
    (value, body) => {
      if (
        !matches(value) ||
        value.request_id !== body.request_id ||
        value.outcome !== body.outcome ||
        value.authority_id !== body.authority_id ||
        value.previous_id !== body.expected_previous_id ||
        value.reason !== body.reason ||
        value.reference !== body.reference
      ) {
        throw new Error("Respuesta incompatible. Consulta el resultado de la solicitud.");
      }
      setState(
        (current) =>
          current && {
            ...current,
            reviews: [...current.reviews.filter((r) => r.id !== value.id), value],
          }
      );
      clearReview();
      setNeedsRefresh(true);
      setNotice(
        "Revisión de Base y fundamento registrada. Vuelve a consultar antes de otra actuación."
      );
    },
    () => setNeedsRefresh(true)
  );
  useBasePending(busy || reviewDirty || facultyDirty || !!request.pending, onPending);

  async function read() {
    const s = await scope();
    const value = await apiFetch<State>(path(s) + "/review-state", { ...s, cache: "no-store" });
    if (
      !matches(value) ||
      !Array.isArray(value.reviews) ||
      !value.reviews.every((r) => matches(r) && Object.hasOwn(outcomes, r.outcome)) ||
      !Array.isArray(value.authorities) ||
      !Array.isArray(value.favorable_requirements)
    ) {
      throw new Error("Respuesta de revisión incompatible. Vuelve a consultar.");
    }
    setState(value);
    setNeedsRefresh(false);
  }

  async function designate(data: FormData, current: State) {
    const s = await scope();
    const subject = text(data, "subject").toLowerCase();
    const previous = current.authorities.filter((a) => a.subject_id === subject).at(-1);
    const expires = text(data, "expires");
    setNeedsRefresh(true);
    await apiFetch(baseVersionPath(s) + "/review-authorities", {
      ...s,
      method: "POST",
      body: {
        subject_id: subject,
        action: facultyAction,
        expected_sequence: previous?.sequence ?? 0,
        reason: text(data, "reason"),
        reference: text(data, "reference"),
        expires_at: facultyAction === "grant" && expires ? new Date(expires).toISOString() : null,
      },
    });
    facultyForm.current?.reset();
    setFacultyAction("grant");
    setFacultyDirty(false);
    setNotice("Actuación de facultad registrada.");
    await read();
  }

  const requirements = state?.favorable_requirements ?? [];
  const resolvable = requirements.filter((r) => r.resolution);
  const criterion = (r: Requirement) => requirementTitle(r, version.bundle);

  return (
    <section aria-label="Revisión de Base y fundamento" className="space-y-3 rounded border p-3">
      <h4 className="font-semibold">Revisión de la versión {version.version}</h4>
      <button
        type="button"
        className={button}
        disabled={busy || !!request.pending}
        onClick={() => void run(read)}
      >
        Consultar revisiones y facultades de Base y fundamento
      </button>
      <OperationFeedback error={operation.error} notice={operation.notice} />
      {needsRefresh && (
        <p>Vuelve a consultar el historial y las facultades antes de registrar otra actuación.</p>
      )}
      {state && (
        <>
          {state.reviews.length === 0 && <p>Esta versión todavía no tiene revisiones.</p>}
          <ol className="space-y-2">
            {state.reviews.map((r) => (
              <li key={r.id} className="space-y-1 break-words rounded border p-2">
                <p className="font-semibold">
                  {r.sequence}. {outcomes[r.outcome]}
                </p>
                <p>
                  {r.reason} · Respaldo: {r.reference}
                </p>
                <p>
                  Persona revisora: {r.created_by} · Fecha (UTC): {r.created_at}
                </p>
                <p>Facultad utilizada: {r.authority_id}</p>
                {r.resolutions.length > 0 && (
                  <ul className="list-disc pl-5">
                    {r.resolutions.map((item) => (
                      <li key={requirementKey(item)}>
                        {criterion(item)} · {resolutionLabel(item)} · {item.justification}
                        {item.reference && ` · Respaldo: ${item.reference}`}
                      </li>
                    ))}
                  </ul>
                )}
                {r.observations.length > 0 && (
                  <ul aria-label="Observaciones de seguimiento" className="list-disc pl-5">
                    {r.observations.map((item, index) => (
                      <li key={index}>
                        {item.description} · Responsable: {item.responsible} · Plazo: {item.due_on}
                      </li>
                    ))}
                  </ul>
                )}
              </li>
            ))}
          </ol>
          {state.blocked_reason && <p>{state.blocked_reason}</p>}
          <BaseFundamentoRequirements material={version.bundle} requirements={requirements} />
          {(state.can_review || reviewDirty) && (
            <form
              ref={form}
              className="space-y-2"
              onChange={() => setReviewDirty(true)}
              onSubmit={(event) => {
                event.preventDefault();
                if (
                  busy ||
                  request.pending ||
                  needsRefresh ||
                  !state.can_review ||
                  !state.authority_id ||
                  (outcome === "favorable" && !state.can_favorable)
                )
                  return;
                const data = new FormData(event.currentTarget);
                const resolutions = resolvable.flatMap((item, index) => {
                  const justification = text(data, `justification-${index}`);
                  return justification
                    ? [
                        {
                          ...item,
                          justification,
                          reference: text(data, `reference-${index}`) || null,
                        },
                      ]
                    : [];
                });
                if (outcome === "favorable" && resolutions.length !== resolvable.length) return;
                const body: ReviewRequest = {
                  request_id: crypto.randomUUID(),
                  data_kind: "ficticios",
                  authority_id: state.authority_id,
                  expected_previous_id: state.reviews.at(-1)?.id ?? null,
                  outcome,
                  reason: text(data, "reason"),
                  reference: text(data, "reference"),
                  resolutions,
                  observations: observations.map((id) => ({
                    description: text(data, `description-${id}`),
                    responsible: text(data, `responsible-${id}`),
                    due_on: text(data, `due-${id}`),
                  })),
                };
                if (!body.reason || !body.reference || !data.has("fictitious")) return;
                void run(() => request.send(body));
              }}
            >
              <fieldset disabled={busy || !!request.pending} className="min-w-0 space-y-2">
                <label className="block">
                  Resultado de la revisión
                  <select
                    className={input}
                    value={outcome}
                    onChange={(e) => setOutcome(e.target.value as Outcome)}
                  >
                    {Object.entries(outcomes).map(([value, label]) => (
                      <option
                        key={value}
                        value={value}
                        disabled={value === "favorable" && !state.can_favorable}
                      >
                        {label}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="block">
                  Fundamento de la revisión
                  <textarea name="reason" className={input} maxLength={4000} required />
                </label>
                <label className="block">
                  Referencia de respaldo de la revisión
                  <input name="reference" className={input} maxLength={1000} required />
                </label>
                {resolvable.length > 0 && (
                  <fieldset className="min-w-0 space-y-2 rounded border p-2">
                    <legend>Requisitos que puedes resolver en esta revisión</legend>
                    {resolvable.map((item, index) => (
                      <div key={requirementKey(item)} className="space-y-1 break-words">
                        <p>
                          {criterion(item)} · {resolutionLabel(item)}
                        </p>
                        <label className="block">
                          Justificación de {resolutionLabel(item).toLowerCase()}
                          <textarea
                            name={`justification-${index}`}
                            className={input}
                            maxLength={4000}
                            required={outcome === "favorable"}
                          />
                        </label>
                        {item.resolution === "respaldo_equivalente" && (
                          <label className="block">
                            Dónde consultar el respaldo equivalente
                            <input
                              name={`reference-${index}`}
                              className={input}
                              maxLength={1000}
                              required={outcome === "favorable"}
                            />
                          </label>
                        )}
                      </div>
                    ))}
                  </fieldset>
                )}
                <fieldset className="min-w-0 space-y-2 rounded border p-2">
                  <legend>Observaciones de seguimiento</legend>
                  <p>
                    Indica pendientes menores con responsable y plazo. Los bloqueos esenciales se
                    resuelven por separado.
                  </p>
                  {observations.map((id, index) => (
                    <div key={id} className="space-y-1">
                      <label className="block">
                        Observación {index + 1}
                        <textarea
                          name={`description-${id}`}
                          className={input}
                          maxLength={4000}
                          required
                        />
                      </label>
                      <label className="block">
                        Responsable
                        <input
                          name={`responsible-${id}`}
                          className={input}
                          maxLength={300}
                          required
                        />
                      </label>
                      <label className="block">
                        Plazo
                        <input name={`due-${id}`} type="date" required />
                      </label>
                      <button
                        type="button"
                        className={button}
                        onClick={() =>
                          setObservations((items) => items.filter((item) => item !== id))
                        }
                      >
                        Quitar observación {index + 1}
                      </button>
                    </div>
                  ))}
                  <button
                    type="button"
                    className={button}
                    disabled={observations.length >= 50}
                    onClick={() => {
                      setObservations((items) => [...items, crypto.randomUUID()]);
                      setReviewDirty(true);
                    }}
                  >
                    Añadir observación
                  </button>
                </fieldset>
                <label className="block">
                  <input name="fictitious" type="checkbox" required /> Declaro datos ficticios para
                  esta revisión
                </label>
                <button
                  className={button}
                  disabled={
                    needsRefresh ||
                    !state.can_review ||
                    (outcome === "favorable" && !state.can_favorable)
                  }
                >
                  {state.reviews.length
                    ? "Registrar reconsideración de Base y fundamento"
                    : "Registrar revisión de Base y fundamento"}
                </button>
              </fieldset>
            </form>
          )}
          <details>
            <summary className={documentDisclosureClass}>
              Historial de facultades de revisión de Base y fundamento
            </summary>
            {state.authorities.length === 0 && <p>Todavía no hay actuaciones de facultad.</p>}
            <ul className="space-y-2">
              {state.authorities.map((a) => (
                <li key={a.id} className="break-words rounded border p-2">
                  {a.subject_id} · {a.action === "grant" ? "Otorgamiento" : "Revocación"}{" "}
                  {a.sequence} · {a.reason}
                  <p>
                    Respaldo: {a.reference} · Por: {a.created_by} · Fecha (UTC): {a.created_at}
                  </p>
                  <p>Vencimiento (UTC): {a.expires_at ?? "Sin vencimiento"}</p>
                </li>
              ))}
            </ul>
          </details>
          {state.may_manage && (
            <details>
              <summary className={documentDisclosureClass}>
                Administrar facultades de revisión de Base y fundamento
              </summary>
              <form
                ref={facultyForm}
                onChange={() => setFacultyDirty(true)}
                onSubmit={(e) => {
                  e.preventDefault();
                  if (busy || request.pending || needsRefresh) return;
                  const data = new FormData(e.currentTarget);
                  void run(() => designate(data, state));
                }}
              >
                <fieldset className="min-w-0 space-y-2" disabled={busy || !!request.pending}>
                  <label className="block">
                    Identificador de la persona destinataria
                    <input
                      name="subject"
                      className={input}
                      required
                      pattern="[0-9a-fA-F]{8}(-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}"
                    />
                  </label>
                  <label className="block">
                    Actuación
                    <select
                      className={input}
                      value={facultyAction}
                      onChange={(e) => setFacultyAction(e.target.value as Faculty["action"])}
                    >
                      <option value="grant">Otorgar</option>
                      <option value="revoke">Revocar</option>
                    </select>
                  </label>
                  <label className="block">
                    Motivo de la facultad
                    <textarea name="reason" className={input} maxLength={4000} required />
                  </label>
                  <label className="block">
                    Referencia de la facultad
                    <input name="reference" className={input} maxLength={1000} required />
                  </label>
                  {facultyAction === "grant" && (
                    <label className="block">
                      Vencimiento opcional (hora local)
                      <input name="expires" type="datetime-local" />
                    </label>
                  )}
                  <button className={button} disabled={needsRefresh}>
                    Registrar actuación de facultad de Base y fundamento
                  </button>
                </fieldset>
              </form>
            </details>
          )}
        </>
      )}
      {(reviewDirty || facultyDirty) && !request.pending && (
        <button
          type="button"
          className={button}
          disabled={busy}
          onClick={() => {
            clearReview();
            facultyForm.current?.reset();
            setFacultyAction("grant");
            setFacultyDirty(false);
          }}
        >
          Descartar campos de revisión y facultad sin registrar
        </button>
      )}
      {request.pending && (
        <RequestRecovery
          busy={busy}
          missing={request.missing}
          recover={() => void run(request.recover)}
          retry={() => {
            if (request.pending) void run(() => request.send(request.pending!));
          }}
        />
      )}
    </section>
  );
}
