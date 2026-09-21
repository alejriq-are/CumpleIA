"use client";

import { useEffect, useState } from "react";
import { createClient } from "@/lib/supabase/client";
import {
  ApiError,
  api,
  type DeclarationStatus,
  type SystemCreate,
  type SystemOut,
  type TreatmentDetailOut,
} from "@/lib/api/client";

type Props = {
  organizationId: string;
  treatmentId: string;
  treatment: TreatmentDetailOut;
  onSaved: (treatment: TreatmentDetailOut) => void;
};

type NewSystemForm = {
  name: string;
  provider: string;
  hosting_location: string;
  hosting_country: string;
};

const EMPTY_SYSTEM: NewSystemForm = {
  name: "",
  provider: "",
  hosting_location: "",
  hosting_country: "",
};

function nullable(value: string) {
  const trimmed = value.trim();
  return trimmed ? trimmed : null;
}

export function TreatmentSystemsSection({
  organizationId,
  treatmentId,
  treatment,
  onSaved,
}: Props) {
  const [declaration, setDeclaration] = useState<DeclarationStatus | "">(
    treatment.systems_declaration ?? ""
  );
  const [catalog, setCatalog] = useState<SystemOut[]>([]);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(
    new Set(treatment.systems.map((system) => system.id))
  );
  const [newSystem, setNewSystem] = useState<NewSystemForm>(EMPTY_SYSTEM);

  const [loadingCatalog, setLoadingCatalog] = useState(true);
  const [creating, setCreating] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    (async () => {
      try {
        const supabase = createClient();
        const {
          data: { session },
        } = await supabase.auth.getSession();

        if (!session) {
          throw new Error("Tu sesión expiró. Vuelve a iniciar sesión.");
        }

        const systems = await api.rat.listSystems(session.access_token, organizationId);

        if (active) {
          setCatalog(systems);
        }
      } catch (e) {
        if (!active) return;

        setError(e instanceof Error ? e.message : "No se pudo cargar el catálogo de sistemas.");
      } finally {
        if (active) setLoadingCatalog(false);
      }
    })();

    return () => {
      active = false;
    };
  }, [organizationId]);

  function toggleSystem(systemId: string) {
    setSaved(false);

    setSelectedIds((current) => {
      const next = new Set(current);

      if (next.has(systemId)) {
        next.delete(systemId);
      } else {
        next.add(systemId);
      }

      return next;
    });
  }

  async function createSystem() {
    if (!newSystem.name.trim()) {
      setError("Debes indicar el nombre del sistema.");
      return;
    }

    setCreating(true);
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

      const body: SystemCreate = {
        name: newSystem.name.trim(),
        provider: nullable(newSystem.provider),
        hosting_location: nullable(newSystem.hosting_location),
        hosting_country: nullable(newSystem.hosting_country),
      };

      const created = await api.rat.createSystem(session.access_token, organizationId, body);

      setCatalog((current) => [...current, created]);
      setSelectedIds((current) => new Set([...current, created.id]));
      setNewSystem(EMPTY_SYSTEM);
      setDeclaration("si");
    } catch (e) {
      if (e instanceof ApiError) {
        setError(e.message);
      } else {
        setError(e instanceof Error ? e.message : "No se pudo crear el sistema.");
      }
    } finally {
      setCreating(false);
    }
  }

  async function saveSystems() {
    if (!declaration) {
      setError("Debes indicar si esta actividad utiliza sistemas.");
      return;
    }

    if (declaration === "si" && selectedIds.size === 0) {
      setError("Si la actividad utiliza sistemas, selecciona al menos uno.");
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

      const ids = declaration === "no" ? [] : Array.from(selectedIds);

      await api.rat.replaceSystems(session.access_token, organizationId, treatmentId, ids);

      await api.rat.updateTreatment(session.access_token, organizationId, treatmentId, {
        systems_declaration: declaration,
      });

      const refreshed = await api.rat.getTreatment(
        session.access_token,
        organizationId,
        treatmentId
      );

      setSelectedIds(new Set(refreshed.systems.map((system) => system.id)));
      setDeclaration(refreshed.systems_declaration ?? "");
      onSaved(refreshed);
      setSaved(true);
    } catch (e) {
      if (e instanceof ApiError) {
        setError(e.message);
      } else {
        setError(e instanceof Error ? e.message : "No se pudo guardar la información de sistemas.");
      }
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <div>
        <h2 className="text-lg font-semibold text-gray-900">Sistemas utilizados</h2>
        <p className="mt-1 text-sm text-gray-500">
          Indica si esta actividad utiliza sistemas o plataformas para tratar datos personales.
        </p>
      </div>

      <div className="mt-6 grid gap-3 sm:grid-cols-3">
        {[
          { value: "si", label: "Sí usa sistemas" },
          { value: "no", label: "No usa sistemas" },
          { value: "pendiente", label: "Pendiente de revisión" },
        ].map((option) => (
          <label
            key={option.value}
            className="flex cursor-pointer items-center gap-3 rounded-lg border border-gray-200 p-4"
          >
            <input
              type="radio"
              name="systems-declaration"
              value={option.value}
              checked={declaration === option.value}
              onChange={() => {
                setDeclaration(option.value as DeclarationStatus);
                setSaved(false);
              }}
              className="h-4 w-4"
            />
            <span className="text-sm font-medium text-gray-800">{option.label}</span>
          </label>
        ))}
      </div>

      {declaration === "si" && (
        <div className="mt-8 space-y-6">
          <div>
            <h3 className="text-sm font-semibold text-gray-900">Sistemas asociados</h3>
            <p className="mt-1 text-xs text-gray-500">
              Selecciona uno o más sistemas del catálogo de la organización.
            </p>

            {loadingCatalog ? (
              <p className="mt-3 text-sm text-gray-500">Cargando sistemas…</p>
            ) : catalog.length === 0 ? (
              <div className="mt-3 rounded-lg border border-dashed border-gray-300 p-4 text-sm text-gray-500">
                Aún no existen sistemas en el catálogo.
              </div>
            ) : (
              <div className="mt-3 grid gap-3 md:grid-cols-2">
                {catalog.map((system) => (
                  <label
                    key={system.id}
                    className="flex cursor-pointer gap-3 rounded-lg border border-gray-200 p-4"
                  >
                    <input
                      type="checkbox"
                      checked={selectedIds.has(system.id)}
                      onChange={() => toggleSystem(system.id)}
                      className="mt-1 h-4 w-4 rounded border-gray-300"
                    />

                    <span>
                      <span className="block text-sm font-medium text-gray-900">{system.name}</span>

                      {(system.provider || system.hosting_location || system.hosting_country) && (
                        <span className="mt-1 block text-xs text-gray-500">
                          {[system.provider, system.hosting_location, system.hosting_country]
                            .filter(Boolean)
                            .join(" · ")}
                        </span>
                      )}
                    </span>
                  </label>
                ))}
              </div>
            )}
          </div>

          <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
            <h3 className="text-sm font-semibold text-gray-900">Agregar sistema al catálogo</h3>

            <div className="mt-4 grid gap-4 md:grid-cols-2">
              <input
                type="text"
                value={newSystem.name}
                onChange={(e) =>
                  setNewSystem((current) => ({
                    ...current,
                    name: e.target.value,
                  }))
                }
                placeholder="Nombre del sistema *"
                className="rounded-lg border border-gray-300 px-3 py-2"
              />

              <input
                type="text"
                value={newSystem.provider}
                onChange={(e) =>
                  setNewSystem((current) => ({
                    ...current,
                    provider: e.target.value,
                  }))
                }
                placeholder="Proveedor, ej. Microsoft"
                className="rounded-lg border border-gray-300 px-3 py-2"
              />

              <input
                type="text"
                value={newSystem.hosting_location}
                onChange={(e) =>
                  setNewSystem((current) => ({
                    ...current,
                    hosting_location: e.target.value,
                  }))
                }
                placeholder="Ubicación de alojamiento"
                className="rounded-lg border border-gray-300 px-3 py-2"
              />

              <input
                type="text"
                value={newSystem.hosting_country}
                onChange={(e) =>
                  setNewSystem((current) => ({
                    ...current,
                    hosting_country: e.target.value,
                  }))
                }
                placeholder="País de alojamiento"
                className="rounded-lg border border-gray-300 px-3 py-2"
              />
            </div>

            <div className="mt-4 flex justify-end">
              <button
                type="button"
                onClick={createSystem}
                disabled={creating}
                className="rounded-lg border border-blue-700 px-4 py-2 text-sm font-medium text-blue-700 hover:bg-blue-50 disabled:opacity-60"
              >
                {creating ? "Creando…" : "Agregar sistema"}
              </button>
            </div>
          </div>
        </div>
      )}

      {declaration === "no" && (
        <p className="mt-5 text-sm text-gray-500">
          Al guardar, se eliminarán las asociaciones de sistemas existentes para esta actividad.
        </p>
      )}

      {declaration === "pendiente" && (
        <p className="mt-5 text-sm text-amber-700">
          Mientras esta declaración permanezca pendiente, el requisito de sistemas no se considerará
          resuelto.
        </p>
      )}

      {error && (
        <div className="mt-5 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
      )}

      {saved && (
        <div className="mt-5 rounded-lg bg-green-50 px-4 py-3 text-sm text-green-700">
          Información de sistemas guardada.
        </div>
      )}

      <div className="mt-6 flex justify-end">
        <button
          type="button"
          onClick={saveSystems}
          disabled={saving}
          className="rounded-lg bg-blue-700 px-5 py-2.5 text-sm font-medium text-white hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {saving ? "Guardando…" : "Guardar sistemas"}
        </button>
      </div>
    </section>
  );
}
