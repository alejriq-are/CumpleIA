"use client";

import { useEffect, useRef, useState } from "react";
import { apiFetch, ApiError } from "@/lib/api/client";
import type { VersionScope } from "@/lib/api/eipd-versions";
import { documentNavigationButtonClass as button, focusDocumentSection } from "./document-focus";

export function baseVersionPath(scope: VersionScope) {
  return `/licitud/treatments/${encodeURIComponent(scope.treatmentId)}/assessments/${encodeURIComponent(scope.assessmentId)}/base-fundamento-versions/v1`;
}

export function useBaseOperation() {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const working = useRef(false);
  async function run(action: () => Promise<void>) {
    if (working.current) return;
    working.current = true;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await action();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No se pudo completar la operación.");
    } finally {
      working.current = false;
      setBusy(false);
    }
  }
  return { busy, error, notice, setNotice, run };
}

export function useBaseRequest<Request extends { request_id: string }, Result>(
  scope: () => Promise<VersionScope>,
  paths: (s: VersionScope) => { post: string; receipt: string },
  accept: (value: Result, request: Request) => void,
  onRejected: () => void
) {
  const [pending, setPending] = useState<Request | null>(null);
  const [missing, setMissing] = useState(false);

  async function send(request: Request) {
    setPending(request);
    setMissing(false);
    const s = await scope();
    let value: Result;
    try {
      value = await apiFetch<Result>(paths(s).post, { ...s, method: "POST", body: request });
    } catch (cause) {
      if (cause instanceof ApiError && [400, 403, 404, 409, 422].includes(cause.status)) {
        setPending(null);
        onRejected();
        throw new Error(`${cause.message} Tus campos se conservan.`);
      }
      throw cause;
    }
    accept(value, request);
    setPending(null);
  }

  async function recover() {
    if (!pending) return;
    const s = await scope();
    try {
      const value = await apiFetch<Result>(paths(s).receipt + pending.request_id, {
        ...s,
        cache: "no-store",
      });
      accept(value, pending);
      setPending(null);
      setMissing(false);
    } catch (cause) {
      if (cause instanceof ApiError && cause.status === 404) setMissing(true);
      else throw cause;
    }
  }

  return { pending, missing, send, recover };
}

export function useBasePending(locked: boolean, onPending: (value: boolean) => void) {
  useEffect(() => {
    onPending(locked);
  }, [locked, onPending]);
  useEffect(() => {
    if (!locked) return;
    const warn = (event: BeforeUnloadEvent) => event.preventDefault();
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, [locked]);
}

export function OperationFeedback({ error, notice }: { error: string; notice: string }) {
  return (
    <>
      {error && (
        <p
          key={error}
          role="alert"
          tabIndex={-1}
          ref={focusDocumentSection}
          className="rounded border border-red-300 bg-red-50 p-2"
        >
          {error}
        </p>
      )}
      {notice && <p role="status">{notice}</p>}
    </>
  );
}

export function RequestRecovery({
  busy,
  missing,
  recover,
  retry,
}: {
  busy: boolean;
  missing: boolean;
  recover: () => void;
  retry: () => void;
}) {
  return (
    <div className="space-y-2 rounded border border-amber-300 bg-amber-50 p-3">
      <p role="status">
        {missing
          ? "La solicitud aún no figura. Puedes reintentar la misma solicitud."
          : "El resultado está por comprobar. Mantén abierta esta pestaña y consulta la solicitud."}
      </p>
      <button type="button" className={button} disabled={busy} onClick={recover}>
        Consultar resultado de la solicitud
      </button>
      {missing && (
        <button type="button" className={button} disabled={busy} onClick={retry}>
          Reintentar la misma solicitud
        </button>
      )}
    </div>
  );
}
