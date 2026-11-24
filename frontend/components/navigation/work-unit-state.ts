"use client";
import { useEffect } from "react";
export type WorkState = {
  status: "not_loaded" | "loading" | "ready" | "edited" | "saving" | "saved" | "error";
  pending: boolean;
};
export type WorkReporter = (state: WorkState) => void;
// UI observations only: a successful read is not evidence of a successful write.
export function useWorkState(
  report: WorkReporter | undefined,
  value: {
    loaded: boolean;
    loading?: boolean;
    saving?: boolean;
    dirty: boolean;
    saved?: boolean;
    error?: boolean;
    uncertain?: boolean;
  }
) {
  const pending = value.dirty || !!value.saving || !!value.uncertain;
  const status: WorkState["status"] = value.saving
    ? "saving"
    : value.loading
      ? "loading"
      : value.error
        ? "error"
        : value.dirty
          ? "edited"
          : value.saved
            ? "saved"
            : value.loaded
              ? "ready"
              : "not_loaded";
  useEffect(() => {
    report?.({ status, pending });
  }, [report, status, pending]);
}
