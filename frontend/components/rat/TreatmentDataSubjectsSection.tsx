"use client";

import { useState } from "react";
import { createClient } from "@/lib/supabase/client";
import { DATA_SUBJECTS } from "@/lib/rat/dataSubjects";
import {
  ApiError,
  api,
  type TreatmentDataSubjectIn,
  type TreatmentDataSubjectOut,
} from "@/lib/api/client";

type Props = {
  organizationId: string;
  treatmentId: string;
  subjects: TreatmentDataSubjectOut[];
  onSaved: (subjects: TreatmentDataSubjectOut[]) => void;
};

type SubjectDraft = TreatmentDataSubjectIn;

const predefinedCodes = new Set(DATA_SUBJECTS.map((item) => item.code));

function emptySubject(code: string, name: string): SubjectDraft {
  return {
    category_code: code,
    category_name: name,
    includes_children: false,
    includes_adolescents: false,
    is_vulnerable_group: false,
    notes: null,
  };
}

export function TreatmentDataSubjectsSection({
  organizationId,
  treatmentId,
  subjects,
  onSaved,
}: Props) {
  const [items, setItems] = useState<SubjectDraft[]>(
    subjects.map((item) => ({
      category_code: item.category_code,
      category_name: item.category_name,
      includes_children: item.includes_children,
      includes_adolescents: item.includes_adolescents,
      is_vulnerable_group: item.is_vulnerable_group,
      notes: item.notes,
    }))
  );

  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function selected(code: string) {
    return items.some((item) => item.category_code === code);
  }

  function togglePredefined(code: string, name: string) {
    setSaved(false);

    setItems((current) => {
      if (current.some((item) => item.category_code === code)) {
        return current.filter((item) => item.category_code !== code);
      }

      return [...current, emptySubject(code, name)];
    });
  }

  function updateSubject(code: string, patch: Partial<Omit<SubjectDraft, "category_code">>) {
    setSaved(false);
    setItems((current) =>
      current.map((item) => (item.category_code === code ? { ...item, ...patch } : item))
    );
  }

  function addCustomSubject() {
    setSaved(false);

    setItems((current) => [...current, emptySubject(`otro_${crypto.randomUUID()}`, "")]);
  }

  function removeSubject(code: string) {
    setSaved(false);
    setItems((current) => current.filter((item) => item.category_code !== code));
  }

  async function saveSubjects() {
    const invalidCustom = items.some(
      (item) => !predefinedCodes.has(item.category_code) && item.category_name.trim().length === 0
    );

    if (invalidCustom) {
      setError("Indica el nombre de cada categoría personalizada.");
      return;
    }

    const normalized: TreatmentDataSubjectIn[] = items.map((item) => ({
      ...item,
      category_name: item.category_name.trim(),
      notes: item.notes?.trim() || null,
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

      const updated = await api.rat.replaceDataSubjects(
        session.access_token,
        organizationId,
        treatmentId,
        normalized
      );

      setItems(
        updated.map((item) => ({
          category_code: item.category_code,
          category_name: item.category_name,
          includes_children: item.includes_children,
          includes_adolescents: item.includes_adolescents,
          is_vulnerable_group: item.is_vulnerable_group,
          notes: item.notes,
        }))
      );

      onSaved(updated);
      setSaved(true);
    } catch (e) {
      if (e instanceof ApiError) {
        setError(e.message);
      } else {
        setError(
          e instanceof Error ? e.message : "No se pudieron guardar las categorías de titulares."
        );
      }
    } finally {
      setSaving(false);
    }
  }

  function renderOptions(item: SubjectDraft) {
    return (
      <div className="mt-3 space-y-3 border-t border-gray-100 pt-3">
        <div className="flex flex-wrap gap-4 text-sm text-gray-700">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={item.includes_children}
              onChange={(e) =>
                updateSubject(item.category_code, {
                  includes_children: e.target.checked,
                })
              }
              className="h-4 w-4 rounded border-gray-300"
            />
            Incluye niños
          </label>

          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={item.includes_adolescents}
              onChange={(e) =>
                updateSubject(item.category_code, {
                  includes_adolescents: e.target.checked,
                })
              }
              className="h-4 w-4 rounded border-gray-300"
            />
            Incluye adolescentes
          </label>

          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={item.is_vulnerable_group}
              onChange={(e) =>
                updateSubject(item.category_code, {
                  is_vulnerable_group: e.target.checked,
                })
              }
              className="h-4 w-4 rounded border-gray-300"
            />
            Grupo vulnerable
          </label>
        </div>

        <textarea
          rows={2}
          value={item.notes ?? ""}
          onChange={(e) =>
            updateSubject(item.category_code, {
              notes: e.target.value,
            })
          }
          placeholder="Notas opcionales"
          className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm"
        />
      </div>
    );
  }

  const customSubjects = items.filter((item) => !predefinedCodes.has(item.category_code));

  return (
    <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <div>
        <h2 className="text-lg font-semibold text-gray-900">Titulares de los datos</h2>
        <p className="mt-1 text-sm text-gray-500">
          Identifica las categorías de personas cuyos datos son tratados en esta actividad.
        </p>
      </div>

      <div className="mt-6 grid gap-3 md:grid-cols-2">
        {DATA_SUBJECTS.map((subject) => {
          const item = items.find((current) => current.category_code === subject.code);
          const isSelected = Boolean(item);

          return (
            <div key={subject.code} className="rounded-lg border border-gray-200 p-4">
              <label className="flex cursor-pointer gap-3">
                <input
                  type="checkbox"
                  checked={isSelected}
                  onChange={() => togglePredefined(subject.code, subject.name)}
                  className="mt-1 h-4 w-4 rounded border-gray-300"
                />

                <span>
                  <span className="block text-sm font-medium text-gray-900">{subject.name}</span>
                  <span className="mt-1 block text-xs text-gray-500">{subject.description}</span>
                </span>
              </label>

              {item && renderOptions(item)}
            </div>
          );
        })}
      </div>

      <div className="mt-6">
        <div className="flex items-center justify-between gap-3">
          <h3 className="text-sm font-semibold text-gray-900">Otras categorías</h3>

          <button
            type="button"
            onClick={addCustomSubject}
            className="text-sm font-medium text-blue-700 hover:underline"
          >
            + Agregar otra categoría
          </button>
        </div>

        <div className="mt-3 space-y-3">
          {customSubjects.map((item) => (
            <div key={item.category_code} className="rounded-lg border border-gray-200 p-4">
              <div className="flex gap-3">
                <input
                  type="text"
                  value={item.category_name}
                  onChange={(e) =>
                    updateSubject(item.category_code, {
                      category_name: e.target.value,
                    })
                  }
                  placeholder="Nombre de la categoría"
                  className="block flex-1 rounded-lg border border-gray-300 px-3 py-2 shadow-sm"
                />

                <button
                  type="button"
                  onClick={() => removeSubject(item.category_code)}
                  className="text-sm font-medium text-red-600 hover:text-red-700"
                >
                  Eliminar
                </button>
              </div>

              {renderOptions(item)}
            </div>
          ))}
        </div>
      </div>

      {error && (
        <div className="mt-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
      )}

      {saved && (
        <div className="mt-4 rounded-lg bg-green-50 px-4 py-3 text-sm text-green-700">
          Titulares guardados.
        </div>
      )}

      <div className="mt-6 flex justify-end">
        <button
          type="button"
          onClick={saveSubjects}
          disabled={saving}
          className="rounded-lg bg-blue-700 px-5 py-2.5 text-sm font-medium text-white hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {saving ? "Guardando…" : "Guardar titulares"}
        </button>
      </div>
    </section>
  );
}
