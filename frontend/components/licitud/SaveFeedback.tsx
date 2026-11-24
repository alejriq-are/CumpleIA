"use client";
import { useEffect, useRef } from "react";

/** Feedback belongs next to the action and never treats a rejected write as saved. */
export function SaveFeedback({
  error = "",
  message = "",
  busy = false,
  dirty = false,
  dirtyMessage = "Cambios sin guardar. Se conservan al navegar.",
}: {
  error?: string;
  message?: string;
  busy?: boolean;
  dirty?: boolean;
  dirtyMessage?: string;
}) {
  const alert = useRef<HTMLParagraphElement>(null);
  useEffect(() => {
    if (error && alert.current?.getClientRects().length) {
      alert.current.focus({ preventScroll: true });
      alert.current.scrollIntoView({ block: "nearest", behavior: "instant" });
    }
  }, [error, busy]);
  return (
    <div className="space-y-3">
      {dirty && (
        <p role="note" className="rounded border border-amber-400 bg-amber-50 p-3 text-amber-950">
          {dirtyMessage}
        </p>
      )}
      {busy && <p role="status">Guardando…</p>}
      {!busy && error && (
        <p
          ref={alert}
          tabIndex={-1}
          role="alert"
          className="rounded border border-red-600 bg-red-50 p-3 font-medium text-red-950"
        >
          {error}
        </p>
      )}
      {!busy && message && !dirty && (
        <p role="status" className="rounded border border-green-600 bg-green-50 p-3 text-green-950">
          {message}
        </p>
      )}
    </div>
  );
}
