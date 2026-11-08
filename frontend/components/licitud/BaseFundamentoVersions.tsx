"use client";

import { useRef, useState, type ReactNode } from "react";
import { apiFetch } from "@/lib/api/client";
import type { Annex } from "@/lib/api/assessment-support";
import type { VersionScope } from "@/lib/api/eipd-versions";
import { SavedBasisDocumentView, ValueView } from "./DossierDocumentView";
import { BaseFundamentoRequirements } from "./BaseFundamentoRequirements";
import { BaseFundamentoReviews } from "./BaseFundamentoReviews";
import { documentDisclosureClass, documentNavigationButtonClass as button } from "./document-focus";
import {
  baseVersionPath,
  OperationFeedback,
  RequestRecovery,
  useBaseOperation,
  useBasePending,
  useBaseRequest,
} from "./BaseFundamentoOperation";
import type {
  BaseMaterial,
  Requirement,
  BasePreview,
  BaseVersion,
  BaseVersionItem,
} from "./BaseFundamentoVersionTypes";

type ScopeProps = {
  scope: () => Promise<VersionScope>;
  onPending: (value: boolean) => void;
};
type RegisterRequest = {
  request_id: string;
  data_kind: "ficticios";
  expected_source_hash: string;
  expected_latest_version: number;
  reason: string;
  annex_ids: string[];
};

function matchesMaterial(value: BaseMaterial | undefined, scope: VersionScope) {
  return (
    value?.document_type === "base_fundamento" &&
    value.saved_assessment?.organization_id === scope.organizationId &&
    value.saved_assessment?.treatment_id === scope.treatmentId &&
    value.saved_assessment?.id === scope.assessmentId &&
    Array.isArray(value.diagnostic?.findings) &&
    Array.isArray(value.diagnostic.criteria) &&
    Array.isArray(value.diagnostic.coverage_pending) &&
    Array.isArray(value.annexes)
  );
}

function BaseMaterialView({
  material,
  requirements,
}: {
  material: BaseMaterial;
  requirements: Requirement[];
}) {
  const primary = material.primary_form;
  const standard = primary?.kind === "consent_assessment" || primary?.kind === "lia_assessment";
  return (
    <div className="space-y-3">
      <section aria-label="Diagnóstico documental conservado" className="space-y-2">
        <h4 className="font-semibold">Diagnóstico documental conservado</h4>
        <BaseFundamentoRequirements material={material} requirements={requirements} />
        {material.diagnostic.coverage_pending.length > 0 && (
          <p>Cobertura pendiente del piloto: {material.diagnostic.coverage_pending.join(", ")}.</p>
        )}
      </section>
      <SavedBasisDocumentView
        value={{
          ...material.saved_assessment,
          ...material.alternatives,
          ...(standard && primary ? { [primary.kind]: primary.content } : {}),
        }}
      />
      {primary && !standard && (
        <details>
          <summary className={documentDisclosureClass}>Consultar formulario principal</summary>
          <ValueView value={primary.content} />
        </details>
      )}
      <details>
        <summary className={documentDisclosureClass}>Consultar alcance RAT conservado</summary>
        <ValueView value={material.saved_assessment.rat_context_snapshot} />
      </details>
      {material.annexes.length > 0 && (
        <section aria-label="Respaldos seleccionados">
          <h4 className="font-semibold">Respaldos seleccionados</h4>
          <ul className="list-disc break-words pl-5">
            {material.annexes.map((a) => (
              <li key={a.id}>
                {a.reference} · versión {a.version} · revisión {a.revision} · SHA-256 {a.sha256}
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}

export function BaseFundamentoRegister({
  scope,
  onPending,
  blocked,
  annexes,
  savedRevision,
}: ScopeProps & {
  blocked: boolean;
  annexes: Annex[];
  savedRevision: number;
}) {
  const [preview, setPreview] = useState<{ value: BasePreview; revision: number } | null>(null);
  const [selected, setSelected] = useState<string[]>([]);
  const [reason, setReason] = useState("");
  const [declared, setDeclared] = useState(false);
  const [reviewed, setReviewed] = useState(false);
  const [registered, setRegistered] = useState<BaseVersion | null>(null);
  const op = useBaseOperation();
  const { busy, run, setNotice } = op;
  const request = useBaseRequest<RegisterRequest, BaseVersion>(
    scope,
    (s) => ({ post: baseVersionPath(s), receipt: baseVersionPath(s) + "/requests/" }),
    (value, body) => {
      const saved = preview?.value.bundle.saved_assessment;
      if (
        !saved ||
        value?.request_id !== body.request_id ||
        value.source_hash !== body.expected_source_hash ||
        value.version !== body.expected_latest_version + 1 ||
        value.reason !== body.reason ||
        value.assessment_id !== saved.id ||
        value.organization_id !== saved.organization_id ||
        value.treatment_id !== saved.treatment_id ||
        value.bundle?.document_type !== "base_fundamento"
      ) {
        throw new Error("Respuesta incompatible. Consulta el resultado de la solicitud.");
      }
      setRegistered(value);
      setReason("");
      setDeclared(false);
      setReviewed(false);
      setSelected([]);
      setPreview(null);
      setNotice(`Versión de Base y fundamento ${value.version} registrada en el servidor.`);
    },
    () => {
      setPreview(null);
      setReviewed(false);
    }
  );
  const dirty = !!reason.trim() || declared || reviewed || selected.length > 0;
  useBasePending(busy || dirty || !!request.pending, onPending);
  const validPreview = preview && (preview.revision === savedRevision || request.pending);
  async function prepare() {
    const s = await scope();
    const query = new URLSearchParams(selected.map((id) => ["annex_ids", id]));
    const value = await apiFetch<BasePreview>(
      baseVersionPath(s) + "/preview" + (query.size ? "?" + query : ""),
      {
        ...s,
        cache: "no-store",
      }
    );
    if (
      !matchesMaterial(value?.bundle, s) ||
      typeof value.source_hash !== "string" ||
      !Number.isSafeInteger(value.latest_version) ||
      !Array.isArray(value.favorable_requirements)
    ) {
      throw new Error("Vista previa incompatible. Vuelve a consultar.");
    }
    setPreview({ value, revision: savedRevision });
    setReviewed(false);
  }

  return (
    <section
      aria-label="Registrar versión de Base y fundamento"
      className="space-y-3 rounded border p-4"
    >
      <h3 className="font-semibold">Registrar versión de Base y fundamento</h3>
      <p>
        Guarda el borrador antes de preparar la versión. Puedes conservar una propuesta incompleta o
        pendiente de definir.
      </p>
      {blocked && <p>Guarda los cambios de la evaluación y los anexos antes de registrar.</p>}
      {annexes.length > 0 && (
        <fieldset className="space-y-2" disabled={busy || !!request.pending}>
          <legend>Respaldos guardados que se incorporarán</legend>
          {annexes.map((a) => (
            <label key={a.id} className="block break-words">
              <input
                type="checkbox"
                checked={selected.includes(a.id)}
                onChange={(e) => {
                  setSelected((ids) =>
                    e.target.checked ? [...ids, a.id] : ids.filter((id) => id !== a.id)
                  );
                  setPreview(null);
                  setReviewed(false);
                }}
              />{" "}
              {a.reference} · versión {a.version} · {a.filename}
            </label>
          ))}
        </fieldset>
      )}
      <button
        type="button"
        className={button}
        disabled={busy || blocked || !!request.pending}
        onClick={() => void run(prepare)}
      >
        Preparar registro de Base y fundamento
      </button>
      <OperationFeedback error={op.error} notice={op.notice} />
      {registered && (
        <p>
          Consulta la versión {registered.version} en Documentos guardados → Evaluación de licitud
          guardada.
        </p>
      )}
      {preview && !validPreview && (
        <p>El borrador guardado cambió. Prepara una vista previa nueva.</p>
      )}
      {validPreview && preview && (
        <form
          className="space-y-3"
          onSubmit={(e) => {
            e.preventDefault();
            if (blocked || busy || request.pending || !reason.trim() || !declared || !reviewed)
              return;
            const body: RegisterRequest = {
              request_id: crypto.randomUUID(),
              data_kind: "ficticios",
              expected_source_hash: preview.value.source_hash,
              expected_latest_version: preview.value.latest_version,
              reason: reason.trim(),
              annex_ids: selected,
            };
            void run(() => request.send(body));
          }}
        >
          <details open>
            <summary className={documentDisclosureClass}>
              Vista previa del contenido guardado
            </summary>
            <p>Próxima versión prevista {preview.value.latest_version + 1}.</p>
            <BaseMaterialView
              material={preview.value.bundle}
              requirements={preview.value.favorable_requirements}
            />
          </details>
          <fieldset disabled={busy || !!request.pending} className="min-w-0 space-y-2">
            <label className="block">
              Motivo del registro
              <textarea
                className="block w-full rounded border p-2"
                required
                maxLength={4000}
                value={reason}
                onChange={(e) => setReason(e.target.value)}
              />
            </label>
            <label className="block">
              <input
                type="checkbox"
                required
                checked={declared}
                onChange={(e) => setDeclared(e.target.checked)}
              />{" "}
              Declaro datos ficticios para esta versión
            </label>
            <label className="block">
              <input
                type="checkbox"
                required
                checked={reviewed}
                onChange={(e) => setReviewed(e.target.checked)}
              />{" "}
              Revisé el contenido guardado y sus pendientes
            </label>
            <button
              className={button}
              disabled={blocked || !reason.trim() || !declared || !reviewed}
            >
              Registrar versión documental de Base y fundamento
            </button>
          </fieldset>
        </form>
      )}
      {dirty && !request.pending && (
        <button
          type="button"
          className={button}
          disabled={busy}
          onClick={() => {
            setSelected([]);
            setReason("");
            setDeclared(false);
            setReviewed(false);
            setPreview(null);
          }}
        >
          Descartar preparación del registro
        </button>
      )}
      {request.pending && (
        <RequestRecovery
          busy={busy}
          missing={request.missing}
          recover={() => void run(request.recover)}
          retry={() => {
            const body = request.pending;
            if (body && !blocked) void run(() => request.send(body));
          }}
        />
      )}
    </section>
  );
}

export function BaseFundamentoHistory({
  scope,
  onPending,
  savedEvaluation,
}: ScopeProps & { savedEvaluation?: ReactNode }) {
  const [items, setItems] = useState<BaseVersionItem[] | null>(null);
  const [detail, setDetail] = useState<BaseVersion | null>(null);
  const [reviewPending, setReviewPending] = useState(false);
  const detailHeading = useRef<HTMLHeadingElement>(null);
  const historyButton = useRef<HTMLButtonElement>(null);
  const op = useBaseOperation();
  const { busy, run } = op;
  useBasePending(busy || reviewPending, onPending);

  async function history() {
    const s = await scope();
    const value = await apiFetch<BaseVersionItem[]>(baseVersionPath(s), {
      ...s,
      cache: "no-store",
    });
    if (!Array.isArray(value)) throw new Error("No se pudo verificar la lista de versiones.");
    setItems([...value].reverse());
  }
  async function open(item: BaseVersionItem) {
    const s = await scope();
    const value = await apiFetch<BaseVersion>(baseVersionPath(s) + "/" + item.id, {
      ...s,
      cache: "no-store",
    });
    if (
      value?.id !== item.id ||
      value.version !== item.version ||
      !matchesMaterial(value.bundle, s) ||
      !Array.isArray(value.favorable_requirements)
    ) {
      throw new Error("No se pudo verificar la versión solicitada.");
    }
    setDetail(value);
    requestAnimationFrame(() => detailHeading.current?.focus());
  }
  return (
    <section
      aria-label="Versiones de Base y fundamento"
      className="space-y-3 rounded border border-blue-300 bg-blue-50 p-4"
    >
      <h4 className="font-semibold">Versiones de Base y fundamento</h4>
      <p>
        Consulta la versión exacta antes de revisar. Cada versión conserva su propio diagnóstico y
        su historial.
      </p>
      <button
        ref={historyButton}
        type="button"
        className={button}
        disabled={busy || reviewPending}
        onClick={() => void run(history)}
      >
        {items
          ? "Actualizar lista de versiones de Base y fundamento"
          : "Consultar versiones de Base y fundamento"}
      </button>
      <OperationFeedback error={op.error} notice={op.notice} />
      {reviewPending && (
        <p>
          Termina o descarta los campos pendientes de revisión o facultad antes de cambiar de
          versión.
        </p>
      )}
      {items?.length === 0 && <p>Todavía no hay versiones registradas de Base y fundamento.</p>}
      {items && !detail && (
        <ul className="space-y-2">
          {items.map((item) => (
            <li key={item.id} className="space-y-2 rounded border bg-white p-2">
              <p>
                Versión {item.version} · {item.created_at} · {item.reason}
              </p>
              <button
                type="button"
                className={button}
                disabled={busy}
                onClick={() => void run(() => open(item))}
              >
                Consultar versión de Base y fundamento {item.version}
              </button>
            </li>
          ))}
        </ul>
      )}
      {detail && (
        <article className="space-y-3 rounded border bg-white p-3">
          <button
            type="button"
            className={button}
            disabled={busy || reviewPending}
            onClick={() => {
              setDetail(null);
              historyButton.current?.focus();
            }}
          >
            Volver a versiones de Base y fundamento
          </button>
          <h4 tabIndex={-1} ref={detailHeading} className="font-semibold">
            Versión de Base y fundamento {detail.version} consultada
          </h4>
          <p>
            {detail.reason} · Fecha (UTC): {detail.created_at}
          </p>
          <p className="break-words">Registrada por: {detail.created_by}</p>
          <BaseFundamentoReviews
            key={detail.id}
            version={detail}
            scope={scope}
            onPending={setReviewPending}
          />
          <details>
            <summary className={documentDisclosureClass}>Consultar evaluación de licitud</summary>
            <p className="py-2">
              Contenido y diagnóstico conservados en la versión {detail.version}.
            </p>
            <BaseMaterialView
              material={detail.bundle}
              requirements={detail.favorable_requirements}
            />
          </details>
        </article>
      )}
      {!detail && savedEvaluation}
    </section>
  );
}
