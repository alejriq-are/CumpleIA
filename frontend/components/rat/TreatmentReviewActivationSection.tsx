"use client";

import { useMemo, useState } from "react";
import { createClient } from "@/lib/supabase/client";
import { ApiError, api, type TreatmentDetailOut, type TreatmentStatus } from "@/lib/api/client";
import { treatmentReadyForActivation, treatmentRequirements } from "@/lib/rat-readiness";

type Props = {
  organizationId: string;
  treatmentId: string;
  treatment: TreatmentDetailOut;
  onSaved: (updated: TreatmentDetailOut) => void;
};

export function TreatmentReviewActivationSection({
  organizationId,
  treatmentId,
  treatment,
  onSaved,
}: Props) {
  const [changing, setChanging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const requirements = useMemo(() => treatmentRequirements(treatment), [treatment]);

  const missing = requirements.filter((requirement) => !requirement.complete);
  const ready = treatmentReadyForActivation(treatment);

  async function changeStatus(status: TreatmentStatus, successMessage: string) {
    setChanging(true);
    setError(null);
    setMessage(null);

    try {
      const supabase = createClient();
      const {
        data: { session },
      } = await supabase.auth.getSession();

      if (!session) {
        throw new Error("Tu sesión expiró. Vuelve a iniciar sesión.");
      }

      const updated = await api.rat.updateTreatment(
        session.access_token,
        organizationId,
        treatmentId,
        { status }
      );

      onSaved(updated);
      setMessage(successMessage);
    } catch (e) {
      if (e instanceof ApiError) {
        setError(e.message);
      } else {
        setError(
          e instanceof Error ? e.message : "No se pudo actualizar el estado de la actividad."
        );
      }
    } finally {
      setChanging(false);
    }
  }

  async function archiveTreatment() {
    const confirmed = window.confirm(
      "¿Quieres archivar esta actividad? Permanecerá en el inventario con estado Archivado."
    );

    if (!confirmed) return;

    await changeStatus("archivado", "La actividad fue archivada.");
  }

  return (
    <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <div>
        <h2 className="text-lg font-semibold text-gray-900">Revisión y activación</h2>
        <p className="mt-1 text-sm text-gray-500">
          Revisa que el registro tenga la información mínima necesaria antes de incorporarlo como
          actividad activa del inventario.
        </p>
      </div>

      {error && (
        <div className="mt-5 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
      )}

      {message && (
        <div className="mt-5 rounded-lg bg-green-50 px-4 py-3 text-sm text-green-700">
          {message}
        </div>
      )}

      {treatment.status === "borrador" && !ready && (
        <div className="mt-5 rounded-lg border border-amber-200 bg-amber-50 px-4 py-4">
          <p className="font-medium text-amber-900">Aún no puedes activar esta actividad.</p>
          <p className="mt-1 text-sm text-amber-800">
            Faltan {missing.length} de los 10 requisitos de preparación:
          </p>

          <ul className="mt-3 space-y-1 text-sm text-amber-800">
            {missing.map((requirement) => (
              <li key={requirement.label}>• {requirement.label}</li>
            ))}
          </ul>
        </div>
      )}

      {treatment.status === "borrador" && ready && (
        <div className="mt-5 rounded-lg border border-green-200 bg-green-50 px-4 py-4">
          <p className="font-medium text-green-900">El registro está preparado para activarse.</p>
          <p className="mt-1 text-sm text-green-800">
            Los 10 requisitos mínimos de preparación están resueltos. La activación no representa
            por sí sola una certificación de cumplimiento legal.
          </p>
        </div>
      )}

      {treatment.status === "activo" && (
        <div className="mt-5 rounded-lg border border-green-200 bg-green-50 px-4 py-4">
          <p className="font-medium text-green-900">Esta actividad está activa.</p>
          <p className="mt-1 text-sm text-green-800">
            Forma parte del inventario activo de actividades de tratamiento. Puedes seguir
            editándolo; si un cambio deja pendiente alguno de los requisitos de preparación, volverá
            automáticamente a Registro en preparación y deberá activarse nuevamente.
          </p>
        </div>
      )}

      {treatment.status === "archivado" && (
        <div className="mt-5 rounded-lg border border-gray-200 bg-gray-50 px-4 py-4">
          <p className="font-medium text-gray-900">Esta actividad está archivada.</p>
          <p className="mt-1 text-sm text-gray-600">
            Puede reactivarse si vuelve a ser necesaria y cumple los requisitos actuales de
            preparación.
          </p>

          {!ready && (
            <p className="mt-3 text-sm font-medium text-amber-700">
              Antes de reactivarla debes resolver {missing.length} requisito
              {missing.length === 1 ? "" : "s"} pendiente
              {missing.length === 1 ? "" : "s"}.
            </p>
          )}
        </div>
      )}

      <div className="mt-6 flex flex-wrap justify-end gap-3">
        {treatment.status === "borrador" && (
          <button
            type="button"
            disabled={!ready || changing}
            onClick={() => changeStatus("activo", "La actividad fue activada correctamente.")}
            className="rounded-lg bg-green-700 px-5 py-2.5 text-sm font-medium text-white hover:bg-green-800 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {changing ? "Actualizando…" : "Activar actividad"}
          </button>
        )}

        {treatment.status === "activo" && (
          <>
            <button
              type="button"
              disabled={changing}
              onClick={() =>
                changeStatus("borrador", "La actividad volvió al estado de preparación.")
              }
              className="rounded-lg border border-gray-300 bg-white px-5 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Volver a preparación
            </button>

            <button
              type="button"
              disabled={changing}
              onClick={archiveTreatment}
              className="rounded-lg border border-gray-300 bg-white px-5 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Archivar actividad
            </button>
          </>
        )}

        {treatment.status === "archivado" && (
          <button
            type="button"
            disabled={!ready || changing}
            onClick={() => changeStatus("activo", "La actividad fue reactivada correctamente.")}
            className="rounded-lg bg-green-700 px-5 py-2.5 text-sm font-medium text-white hover:bg-green-800 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {changing ? "Actualizando…" : "Reactivar actividad"}
          </button>
        )}
      </div>
    </section>
  );
}
