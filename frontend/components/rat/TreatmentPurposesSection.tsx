"use client";

import { useState } from "react";
import { createClient } from "@/lib/supabase/client";
import { ApiError, api, type TreatmentPurposeIn, type TreatmentPurposeOut } from "@/lib/api/client";

type Props = {
  organizationId: string;
  treatmentId: string;
  purposes: TreatmentPurposeOut[];
  onSaved: (purposes: TreatmentPurposeOut[]) => void;
};

type PurposeDraft = {
  purpose: string;
  is_primary: boolean;
};

export function TreatmentPurposesSection({
  organizationId,
  treatmentId,
  purposes,
  onSaved,
}: Props) {
  const [items, setItems] = useState<PurposeDraft[]>(
    purposes.map((item) => ({
      purpose: item.purpose,
      is_primary: item.is_primary,
    }))
  );
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function addPurpose() {
    setSaved(false);
    setItems((current) => [
      ...current,
      {
        purpose: "",
        is_primary: current.length === 0,
      },
    ]);
  }

  function updatePurpose(index: number, value: string) {
    setSaved(false);
    setItems((current) =>
      current.map((item, itemIndex) => (itemIndex === index ? { ...item, purpose: value } : item))
    );
  }

  function setPrimary(index: number) {
    setSaved(false);
    setItems((current) =>
      current.map((item, itemIndex) => ({
        ...item,
        is_primary: itemIndex === index,
      }))
    );
  }

  function removePurpose(index: number) {
    setSaved(false);

    setItems((current) => {
      const next = current.filter((_, itemIndex) => itemIndex !== index);

      if (next.length > 0 && !next.some((item) => item.is_primary)) {
        next[0] = { ...next[0], is_primary: true };
      }

      return next;
    });
  }

  async function savePurposes() {
    const normalized: TreatmentPurposeIn[] = items
      .map((item, index) => ({
        purpose: item.purpose.trim(),
        is_primary: item.is_primary,
        sort_order: index,
      }))
      .filter((item) => item.purpose.length > 0);

    if (items.length > 0 && normalized.length !== items.length) {
      setError("Completa o elimina las finalidades vacías antes de guardar.");
      return;
    }

    setSaving(true);
    setSaved(false);
    setError(null);

    try {
      const supabase = createClient();
      const {
        data: { session },
      } = await supabase.auth.getSession();

      if (!session) {
        throw new Error("Tu sesión expiró. Vuelve a iniciar sesión.");
      }

      const updated = await api.rat.replacePurposes(
        session.access_token,
        organizationId,
        treatmentId,
        normalized
      );

      setItems(
        updated.map((item) => ({
          purpose: item.purpose,
          is_primary: item.is_primary,
        }))
      );
      onSaved(updated);
      setSaved(true);
    } catch (e) {
      if (e instanceof ApiError) {
        setError(e.message);
      } else {
        setError(e instanceof Error ? e.message : "No se pudieron guardar las finalidades.");
      }
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Finalidades</h2>
          <p className="mt-1 text-sm text-gray-500">
            Indica para qué se realiza este tratamiento de datos personales.
          </p>
        </div>

        <button
          type="button"
          onClick={addPurpose}
          className="rounded-lg border border-blue-700 px-4 py-2 text-sm font-medium text-blue-700 hover:bg-blue-50"
        >
          + Agregar finalidad
        </button>
      </div>

      <div className="mt-6 space-y-4">
        {items.length === 0 && (
          <div className="rounded-lg border border-dashed border-gray-300 px-4 py-6 text-sm text-gray-500">
            Aún no has registrado finalidades.
          </div>
        )}

        {items.map((item, index) => (
          <div
            key={index}
            className="grid gap-3 rounded-lg border border-gray-200 p-4 md:grid-cols-[1fr_auto_auto] md:items-center"
          >
            <input
              type="text"
              value={item.purpose}
              onChange={(e) => updatePurpose(index, e.target.value)}
              placeholder="Ej. Gestionar la relación comercial con clientes"
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />

            <label className="flex items-center gap-2 text-sm text-gray-700">
              <input
                type="radio"
                name="primary-purpose"
                checked={item.is_primary}
                onChange={() => setPrimary(index)}
                className="h-4 w-4"
              />
              Principal
            </label>

            <button
              type="button"
              onClick={() => removePurpose(index)}
              className="text-sm font-medium text-red-600 hover:text-red-700"
            >
              Eliminar
            </button>
          </div>
        ))}
      </div>

      {error && (
        <div className="mt-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
      )}

      {saved && (
        <div className="mt-4 rounded-lg bg-green-50 px-4 py-3 text-sm text-green-700">
          Finalidades guardadas.
        </div>
      )}

      <div className="mt-6 flex justify-end">
        <button
          type="button"
          onClick={savePurposes}
          disabled={saving}
          className="rounded-lg bg-blue-700 px-5 py-2.5 text-sm font-medium text-white hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {saving ? "Guardando…" : "Guardar finalidades"}
        </button>
      </div>
    </section>
  );
}
