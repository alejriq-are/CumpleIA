"use client";

import { useState, type FormEvent } from "react";
import { ApiError } from "@/lib/api/client";
import type { EipdReviewPreparationOut, EipdResolutionReviewOutV2 } from "@/lib/api/eipd-review";

type Scope = { organizationId: string; treatmentId: string; assessmentId: string };
type Props = {
  loadPreparation: (scope: Scope) => Promise<EipdReviewPreparationOut>;
  loadEvent: (scope: Scope, reviewId: string) => Promise<EipdResolutionReviewOutV2>;
};
const labels = {
  continuar: "Continuar",
  requiere_cambios: "Requiere cambios",
  no_continuar: "No continuar",
} as const;
const uuidPattern = "[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}";
export function consultationError(error: unknown): string {
  if (error instanceof ApiError) {
    const messages: Record<number, string> = {
      401: "La sesión no es válida. Vuelve a iniciar sesión.",
      402: "La suscripción de esta organización no permite la consulta.",
      403: "No tienes permiso para consultar este expediente.",
      404: "No se encontró el expediente o la revisión en esta organización.",
      409: "El estado del expediente no permite completar esta consulta.",
    };
    return messages[error.status] ?? "No se pudo completar la consulta.";
  }
  return "No se pudo consultar el expediente. Revisa los identificadores y la conexión.";
}

export function PreparationView({ value }: { value: EipdReviewPreparationOut }) {
  const result = value.review_prerequisites_v3;
  return (
    <section aria-labelledby="preparation-heading" className="space-y-4">
      <h2 id="preparation-heading" className="text-xl font-semibold">
        Requisitos de revisión
      </h2>
      <p>Estado del expediente: {value.status}.</p>
      <p className="text-sm text-gray-600">
        Cumplir estos requisitos documentales no concede permiso ni registra una decisión.
      </p>
      {result === null ? (
        <p>Este expediente no tiene diagnóstico de revisión V3 disponible.</p>
      ) : (
        <div className="grid gap-4 md:grid-cols-3">
          {(Object.keys(labels) as (keyof typeof labels)[]).map((decision) => {
            const diagnostic = result[decision];
            return (
              <article key={decision} className="rounded-lg border bg-white p-4">
                <h3 className="font-semibold">{labels[decision]}</h3>
                <p className="mt-2">
                  {diagnostic.prerequisites_met
                    ? "Requisitos documentales cumplidos."
                    : "Requisitos documentales pendientes."}
                </p>
                <p className="mt-2 text-sm">
                  {diagnostic.context_metadata === null
                    ? "Identidad auditable no disponible."
                    : "Identidad del material actual disponible."}
                </p>
                {diagnostic.issues.length > 0 && (
                  <ul className="mt-3 list-disc space-y-2 pl-5 text-sm">
                    {diagnostic.issues.map((issue, index) => (
                      <li key={`${issue.code}-${index}`}>{issue.code.replaceAll("_", " ")}</li>
                    ))}
                  </ul>
                )}
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}

export function EventView({ value }: { value: EipdResolutionReviewOutV2 }) {
  return (
    <section aria-labelledby="event-heading" className="space-y-3 rounded-lg border bg-white p-5">
      <h2 id="event-heading" className="text-xl font-semibold">
        Revisión guardada
      </h2>
      <dl className="space-y-2 break-words text-sm">
        <div>
          <dt className="font-semibold">Decisión</dt>
          <dd>{labels[value.decision]}</dd>
        </div>
        <div>
          <dt className="font-semibold">Fundamento</dt>
          <dd className="whitespace-pre-wrap">{value.rationale}</dd>
        </div>
        <div>
          <dt className="font-semibold">Referencia</dt>
          <dd>{value.review_reference}</dd>
        </div>
        <div>
          <dt className="font-semibold">Fecha registrada (UTC)</dt>
          <dd>{value.created_at}</dd>
        </div>
        <div>
          <dt className="font-semibold">Política registrada</dt>
          <dd>{value.policy_reference ?? "Sin identidad de política registrada."}</dd>
        </div>
        <div>
          <dt className="font-semibold">Metadatos auditables</dt>
          <dd>
            {value.review_context_metadata === null
              ? "Sin metadatos registrados; no se reconstruyen."
              : `Contexto versión ${value.review_context_metadata.context_schema_version}. Cobertura: ${value.review_context_metadata.research_coverage === "contexto_v2" ? "contexto de investigación" : "sin cobertura de investigación"}.`}
          </dd>
        </div>
      </dl>
      <p className="text-sm text-gray-600">
        Esta es la identidad guardada con el evento. Su consulta no acredita vigencia del expediente
        actual.
      </p>
    </section>
  );
}

export function EipdReviewConsultation({ loadPreparation, loadEvent }: Props) {
  const [scope, setScope] = useState<Scope>({
    organizationId: "",
    treatmentId: "",
    assessmentId: "",
  });
  const [reviewId, setReviewId] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [preparation, setPreparation] = useState<EipdReviewPreparationOut | null>(null);
  const [event, setEvent] = useState<EipdResolutionReviewOutV2 | null>(null);
  function changeScope(field: keyof Scope, value: string) {
    setScope({ ...scope, [field]: value });
    setPreparation(null);
    setEvent(null);
    setReviewId("");
    setError("");
  }
  async function consult(e: FormEvent, kind: "preparation" | "event") {
    e.preventDefault();
    if (busy) return;
    setBusy(true);
    setError("");
    setPreparation(null);
    setEvent(null);
    try {
      if (kind === "preparation") setPreparation(await loadPreparation(scope));
      else setEvent(await loadEvent(scope, reviewId));
    } catch (failure) {
      setError(consultationError(failure));
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <h1 className="text-2xl font-bold">Consulta interna de revisiones EIPD</h1>
      <p>
        Selecciona el expediente mediante sus identificadores. Esta pantalla solo consulta datos.
      </p>
      <p className="rounded-lg border border-blue-200 bg-blue-50 p-4 text-sm">
        M3-T1 en progreso. La confirmación y la activación EIPD permanecen bloqueadas.
      </p>
      <form
        onSubmit={(e) => consult(e, "preparation")}
        className="space-y-4 rounded-lg border bg-white p-5"
        aria-busy={busy}
      >
        <fieldset disabled={busy} className="space-y-4">
          <legend className="mb-3 font-semibold">Expediente a consultar</legend>
          {(
            [
              ["organizationId", "Organización"],
              ["treatmentId", "Tratamiento"],
              ["assessmentId", "Evaluación"],
            ] as const
          ).map(([field, label]) => (
            <label key={field} className="block text-sm font-medium">
              {label} (identificador)
              <input
                required
                pattern={uuidPattern}
                value={scope[field]}
                onChange={(e) => changeScope(field, e.target.value)}
                className="mt-1 block w-full rounded border p-2 font-normal"
                autoComplete="off"
                spellCheck={false}
              />
            </label>
          ))}
          <button type="submit" className="rounded bg-blue-700 px-4 py-2 text-white">
            Consultar requisitos
          </button>
        </fieldset>
      </form>
      <form
        onSubmit={(e) => consult(e, "event")}
        className="space-y-3 rounded-lg border bg-white p-5"
        aria-busy={busy}
      >
        <fieldset
          disabled={
            busy ||
            Object.values(scope).some((value) => !new RegExp(`^${uuidPattern}$`).test(value))
          }
          className="space-y-3"
        >
          <legend className="mb-3 font-semibold">Consultar un evento guardado</legend>
          <label className="block text-sm font-medium">
            Revisión (identificador)
            <input
              required
              pattern={uuidPattern}
              value={reviewId}
              onChange={(e) => {
                setReviewId(e.target.value);
                setEvent(null);
                setError("");
              }}
              className="mt-1 block w-full rounded border p-2 font-normal"
              autoComplete="off"
              spellCheck={false}
            />
          </label>
          <button type="submit" className="rounded bg-blue-700 px-4 py-2 text-white">
            Consultar revisión
          </button>
        </fieldset>
      </form>
      <div role="status" aria-live="polite">
        {busy ? "Consultando…" : ""}
      </div>
      {error && (
        <p role="alert" className="rounded border border-red-200 bg-red-50 p-4 text-red-800">
          {error}
        </p>
      )}
      {preparation && <PreparationView value={preparation} />}
      {event && <EventView value={event} />}
    </div>
  );
}
