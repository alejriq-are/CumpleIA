"use client";

import { useMemo, useState } from "react";
import { createClient } from "@/lib/supabase/client";
import { DATA_CATEGORIES } from "@/lib/rat/dataCategories";
import {
  ApiError,
  api,
  type TreatmentDataCategoryIn,
  type TreatmentDataCategoryOut,
} from "@/lib/api/client";

type Props = {
  organizationId: string;
  treatmentId: string;
  categories: TreatmentDataCategoryOut[];
  onSaved: (categories: TreatmentDataCategoryOut[]) => void;
};

export function TreatmentDataCategoriesSection({
  organizationId,
  treatmentId,
  categories,
  onSaved,
}: Props) {
  const initialSelected = useMemo(
    () => new Set(categories.map((item) => item.category_code)),
    [categories]
  );

  const [selected, setSelected] = useState<Set<string>>(initialSelected);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function toggle(code: string) {
    setSaved(false);
    setSelected((current) => {
      const next = new Set(current);

      if (next.has(code)) {
        next.delete(code);
      } else {
        next.add(code);
      }

      return next;
    });
  }

  async function saveCategories() {
    const items: TreatmentDataCategoryIn[] = DATA_CATEGORIES.filter((category) =>
      selected.has(category.code)
    ).map((category) => ({
      category_code: category.code,
      category_name: category.name,
      is_sensitive: category.isSensitive,
      notes: null,
    }));

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

      const updated = await api.rat.replaceDataCategories(
        session.access_token,
        organizationId,
        treatmentId,
        items
      );

      onSaved(updated);
      setSelected(new Set(updated.map((item) => item.category_code)));
      setSaved(true);
    } catch (e) {
      if (e instanceof ApiError) {
        setError(e.message);
      } else {
        setError(
          e instanceof Error ? e.message : "No se pudieron guardar las categorías de datos."
        );
      }
    } finally {
      setSaving(false);
    }
  }

  const generalCategories = DATA_CATEGORIES.filter((category) => !category.isSensitive);
  const sensitiveCategories = DATA_CATEGORIES.filter((category) => category.isSensitive);

  return (
    <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <div>
        <h2 className="text-lg font-semibold text-gray-900">Categorías de datos personales</h2>
        <p className="mt-1 text-sm text-gray-500">
          Selecciona las categorías de datos que utiliza esta actividad de tratamiento.
        </p>
      </div>

      <div className="mt-6">
        <h3 className="text-sm font-semibold text-gray-900">Datos personales</h3>

        <div className="mt-3 grid gap-3 md:grid-cols-2">
          {generalCategories.map((category) => (
            <label
              key={category.code}
              className="flex cursor-pointer gap-3 rounded-lg border border-gray-200 p-4"
            >
              <input
                type="checkbox"
                checked={selected.has(category.code)}
                onChange={() => toggle(category.code)}
                className="mt-1 h-4 w-4 rounded border-gray-300"
              />

              <span>
                <span className="block text-sm font-medium text-gray-900">{category.name}</span>
                <span className="mt-1 block text-xs text-gray-500">{category.description}</span>
              </span>
            </label>
          ))}
        </div>
      </div>

      <div className="mt-8">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-semibold text-gray-900">Datos sensibles</h3>
          <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800">
            Protección reforzada
          </span>
        </div>

        <p className="mt-1 text-xs text-gray-500">
          Estas categorías requieren especial atención por su naturaleza.
        </p>

        <div className="mt-3 grid gap-3 md:grid-cols-2">
          {sensitiveCategories.map((category) => (
            <label
              key={category.code}
              className="flex cursor-pointer gap-3 rounded-lg border border-amber-200 bg-amber-50/40 p-4"
            >
              <input
                type="checkbox"
                checked={selected.has(category.code)}
                onChange={() => toggle(category.code)}
                className="mt-1 h-4 w-4 rounded border-gray-300"
              />

              <span>
                <span className="block text-sm font-medium text-gray-900">{category.name}</span>
                <span className="mt-1 block text-xs text-gray-500">{category.description}</span>
              </span>
            </label>
          ))}
        </div>
      </div>

      {error && (
        <div className="mt-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
      )}

      {saved && (
        <div className="mt-4 rounded-lg bg-green-50 px-4 py-3 text-sm text-green-700">
          Categorías de datos guardadas.
        </div>
      )}

      <div className="mt-6 flex justify-end">
        <button
          type="button"
          onClick={saveCategories}
          disabled={saving}
          className="rounded-lg bg-blue-700 px-5 py-2.5 text-sm font-medium text-white hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {saving ? "Guardando…" : "Guardar categorías"}
        </button>
      </div>
    </section>
  );
}
