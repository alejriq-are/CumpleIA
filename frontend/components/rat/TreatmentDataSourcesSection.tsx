"use client";

import { useState } from "react";
import { createClient } from "@/lib/supabase/client";
import {
  ApiError,
  api,
  type DataSourceType,
  type TreatmentDataSourceIn,
  type TreatmentDataSourceOut,
} from "@/lib/api/client";

type Props = {
  organizationId: string;
  treatmentId: string;
  sources: TreatmentDataSourceOut[];
  onSaved: (sources: TreatmentDataSourceOut[]) => void;
};

type SourceDraft = {
  source_type: DataSourceType;
  description: string;
};

const SOURCE_OPTIONS: { value: DataSourceType; label: string }[] = [
  { value: "titular", label: "Directamente del titular" },
  { value: "tercero", label: "Tercero" },
  { value: "fuente_publica", label: "Fuente pública" },
  { value: "recogida_automatica", label: "Recogida automática" },
  { value: "otro", label: "Otra fuente" },
];

export function TreatmentDataSourcesSection({
  organizationId,
  treatmentId,
  sources,
  onSaved,
}: Props) {
  const [items, setItems] = useState<SourceDraft[]>(
    sources.map((item) => ({
      source_type: item.source_type,
      description: item.description ?? "",
    }))
  );

  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function addSource() {
    setSaved(false);
    setItems((current) => [
      ...current,
      {
        source_type: "titular",
        description: "",
      },
    ]);
  }

  function updateSource(index: number, patch: Partial<SourceDraft>) {
    setSaved(false);
    setItems((current) =>
      current.map((item, itemIndex) => (itemIndex === index ? { ...item, ...patch } : item))
    );
  }

  function removeSource(index: number) {
    setSaved(false);
    setItems((current) => current.filter((_, itemIndex) => itemIndex !== index));
  }

  async function saveSources() {
    const normalized: TreatmentDataSourceIn[] = items.map((item) => ({
      source_type: item.source_type,
      description: item.description.trim() || null,
      is_public_source: item.source_type === "fuente_publica",
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

      const updated = await api.rat.replaceDataSources(
        session.access_token,
        organizationId,
        treatmentId,
        normalized
      );

      setItems(
        updated.map((item) => ({
          source_type: item.source_type,
          description: item.description ?? "",
        }))
      );

      onSaved(updated);
      setSaved(true);
    } catch (e) {
      if (e instanceof ApiError) {
        setError(e.message);
      } else {
        setError(e instanceof Error ? e.message : "No se pudieron guardar las fuentes de datos.");
      }
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Fuentes de los datos</h2>
          <p className="mt-1 text-sm text-gray-500">
            Indica de dónde se obtienen los datos personales utilizados en esta actividad.
          </p>
        </div>

        <button
          type="button"
          onClick={addSource}
          className="rounded-lg border border-blue-700 px-4 py-2 text-sm font-medium text-blue-700 hover:bg-blue-50"
        >
          + Agregar fuente
        </button>
      </div>

      <div className="mt-6 space-y-4">
        {items.length === 0 && (
          <div className="rounded-lg border border-dashed border-gray-300 px-4 py-6 text-sm text-gray-500">
            Aún no has registrado fuentes de datos.
          </div>
        )}

        {items.map((item, index) => (
          <div key={index} className="rounded-lg border border-gray-200 p-4">
            <div className="grid gap-4 md:grid-cols-[240px_1fr_auto] md:items-start">
              <label>
                <span className="text-sm font-medium text-gray-700">Tipo de fuente</span>

                <select
                  value={item.source_type}
                  onChange={(e) =>
                    updateSource(index, {
                      source_type: e.target.value as DataSourceType,
                    })
                  }
                  className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm"
                >
                  {SOURCE_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </label>

              <label>
                <span className="text-sm font-medium text-gray-700">Descripción</span>

                <input
                  type="text"
                  value={item.description}
                  onChange={(e) =>
                    updateSource(index, {
                      description: e.target.value,
                    })
                  }
                  placeholder="Ej. Formulario de registro del cliente"
                  className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm"
                />
              </label>

              <button
                type="button"
                onClick={() => removeSource(index)}
                className="mt-7 text-sm font-medium text-red-600 hover:text-red-700"
              >
                Eliminar
              </button>
            </div>

            {item.source_type === "fuente_publica" && (
              <p className="mt-3 text-xs text-gray-500">
                Esta fuente se registrará automáticamente como fuente pública.
              </p>
            )}
          </div>
        ))}
      </div>

      {error && (
        <div className="mt-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
      )}

      {saved && (
        <div className="mt-4 rounded-lg bg-green-50 px-4 py-3 text-sm text-green-700">
          Fuentes de datos guardadas.
        </div>
      )}

      <div className="mt-6 flex justify-end">
        <button
          type="button"
          onClick={saveSources}
          disabled={saving}
          className="rounded-lg bg-blue-700 px-5 py-2.5 text-sm font-medium text-white hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {saving ? "Guardando…" : "Guardar fuentes"}
        </button>
      </div>
    </section>
  );
}
