"use client";

import { useEffect, useState } from "react";
import { createClient } from "@/lib/supabase/client";
import {
  ApiError,
  api,
  type DeclarationStatus,
  type TreatmentDetailOut,
  type TreatmentVendorIn,
  type VendorCreate,
  type VendorOut,
  type VendorRelationshipType,
} from "@/lib/api/client";

type Props = {
  organizationId: string;
  treatmentId: string;
  treatment: TreatmentDetailOut;
  onSaved: (treatment: TreatmentDetailOut) => void;
};

type VendorRelationDraft = {
  key: string;
  vendor_id: string;
  relationship_type: VendorRelationshipType;
  purpose: string;
  has_data_access: boolean;
  has_contract: boolean;
  contract_reference: string;
  engagement_object: string;
  engagement_duration: string;
  has_subprocessors: boolean;
  notes: string;
};

type NewVendorForm = {
  name: string;
  country: string;
};

const EMPTY_VENDOR: NewVendorForm = {
  name: "",
  country: "",
};

function nullable(value: string) {
  const trimmed = value.trim();
  return trimmed ? trimmed : null;
}

function newRelation(vendorId = ""): VendorRelationDraft {
  return {
    key: crypto.randomUUID(),
    vendor_id: vendorId,
    relationship_type: "encargado",
    purpose: "",
    has_data_access: true,
    has_contract: false,
    contract_reference: "",
    engagement_object: "",
    engagement_duration: "",
    has_subprocessors: false,
    notes: "",
  };
}

export function TreatmentVendorsSection({
  organizationId,
  treatmentId,
  treatment,
  onSaved,
}: Props) {
  const [declaration, setDeclaration] = useState<DeclarationStatus | "">(
    treatment.vendors_declaration ?? ""
  );

  const [catalog, setCatalog] = useState<VendorOut[]>([]);
  const [relations, setRelations] = useState<VendorRelationDraft[]>(
    treatment.vendors.map((item) => ({
      key: item.id,
      vendor_id: item.vendor_id,
      relationship_type: item.relationship_type,
      purpose: item.purpose ?? "",
      has_data_access: item.has_data_access,
      has_contract: item.has_contract,
      contract_reference: item.contract_reference ?? "",
      engagement_object: item.engagement_object ?? "",
      engagement_duration: item.engagement_duration ?? "",
      has_subprocessors: item.has_subprocessors,
      notes: item.notes ?? "",
    }))
  );

  const [newVendor, setNewVendor] = useState<NewVendorForm>(EMPTY_VENDOR);
  const [addingVendorKey, setAddingVendorKey] = useState<string | null>(null);
  const [loadingCatalog, setLoadingCatalog] = useState(true);
  const [creating, setCreating] = useState(false);
  const [deletingVendorId, setDeletingVendorId] = useState<string | null>(null);
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

        const vendors = await api.rat.listVendors(session.access_token, organizationId);

        if (active) setCatalog(vendors);
      } catch (e) {
        if (!active) return;

        setError(e instanceof Error ? e.message : "No se pudo cargar el catálogo de proveedores.");
      } finally {
        if (active) setLoadingCatalog(false);
      }
    })();

    return () => {
      active = false;
    };
  }, [organizationId]);

  function addRelation() {
    setSaved(false);
    setRelations((current) => [...current, newRelation()]);
  }

  function removeRelation(key: string) {
    setSaved(false);
    setRelations((current) => current.filter((item) => item.key !== key));
    if (addingVendorKey === key) {
      setAddingVendorKey(null);
      setNewVendor(EMPTY_VENDOR);
    }
  }

  function updateRelation(key: string, patch: Partial<Omit<VendorRelationDraft, "key">>) {
    setSaved(false);
    setRelations((current) =>
      current.map((item) => (item.key === key ? { ...item, ...patch } : item))
    );
  }

  async function createVendor(key: string) {
    if (!newVendor.name.trim()) {
      setError("Debes indicar el nombre del proveedor o tercero.");
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

      const body: VendorCreate = {
        name: newVendor.name.trim(),
        country: nullable(newVendor.country),
      };

      const created = await api.rat.createVendor(session.access_token, organizationId, body);

      setCatalog((current) => [...current, created]);
      updateRelation(key, { vendor_id: created.id });
      setAddingVendorKey(null);
      setNewVendor(EMPTY_VENDOR);
      setDeclaration("si");
    } catch (e) {
      if (e instanceof ApiError) {
        setError(e.message);
      } else {
        setError(e instanceof Error ? e.message : "No se pudo crear el proveedor o tercero.");
      }
    } finally {
      setCreating(false);
    }
  }

  async function deleteVendorFromCatalog(vendor: VendorOut) {
    if (relations.some((relation) => relation.vendor_id === vendor.id)) {
      setError(
        "Esta organización está seleccionada en una relación de esta actividad. " +
          "Elimina primero esa relación y guarda los cambios antes de borrarla del catálogo."
      );
      return;
    }

    const confirmed = window.confirm(`¿Eliminar "${vendor.name}" del catálogo de la organización?`);

    if (!confirmed) return;

    setDeletingVendorId(vendor.id);
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

      await api.rat.deleteVendor(session.access_token, organizationId, vendor.id);

      setCatalog((current) => current.filter((item) => item.id !== vendor.id));
    } catch (e) {
      if (e instanceof ApiError) {
        setError(e.message);
      } else {
        setError(
          e instanceof Error ? e.message : "No se pudo eliminar la organización del catálogo."
        );
      }
    } finally {
      setDeletingVendorId(null);
    }
  }

  async function saveVendors() {
    if (!declaration) {
      setError("Debes indicar si intervienen proveedores o terceros.");
      return;
    }

    if (
      declaration === "si" &&
      (relations.length === 0 || relations.some((item) => !item.vendor_id))
    ) {
      setError("Si intervienen proveedores o terceros, registra al menos una relación completa.");
      return;
    }

    const keys = relations.map((item) => `${item.vendor_id}:${item.relationship_type}`);

    if (new Set(keys).size !== keys.length) {
      setError("No puedes repetir el mismo proveedor con el mismo tipo de relación.");
      return;
    }

    const missingContractReference = relations.find(
      (item) => item.has_contract && !item.contract_reference.trim()
    );

    if (declaration !== "no" && missingContractReference) {
      setError(
        "Si existe contrato o acuerdo documentado, debes indicar su identificación o referencia."
      );
      return;
    }

    const items: TreatmentVendorIn[] =
      declaration === "no"
        ? []
        : relations.map((item) => ({
            vendor_id: item.vendor_id,
            relationship_type: item.relationship_type,
            purpose: nullable(item.purpose),
            has_data_access: item.has_data_access,
            has_contract: item.has_contract,
            contract_reference: item.has_contract ? nullable(item.contract_reference) : null,
            engagement_object: nullable(item.engagement_object),
            engagement_duration: nullable(item.engagement_duration),
            has_subprocessors: item.has_subprocessors,
            notes: nullable(item.notes),
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

      await api.rat.replaceVendors(session.access_token, organizationId, treatmentId, items);

      await api.rat.updateTreatment(session.access_token, organizationId, treatmentId, {
        vendors_declaration: declaration,
      });

      const refreshed = await api.rat.getTreatment(
        session.access_token,
        organizationId,
        treatmentId
      );

      setDeclaration(refreshed.vendors_declaration ?? "");
      setRelations(
        refreshed.vendors.map((item) => ({
          key: item.id,
          vendor_id: item.vendor_id,
          relationship_type: item.relationship_type,
          purpose: item.purpose ?? "",
          has_data_access: item.has_data_access,
          has_contract: item.has_contract,
          contract_reference: item.contract_reference ?? "",
          engagement_object: item.engagement_object ?? "",
          engagement_duration: item.engagement_duration ?? "",
          has_subprocessors: item.has_subprocessors,
          notes: item.notes ?? "",
        }))
      );

      onSaved(refreshed);
      setSaved(true);
    } catch (e) {
      if (e instanceof ApiError) {
        setError(e.message);
      } else {
        setError(
          e instanceof Error ? e.message : "No se pudo guardar la información de proveedores."
        );
      }
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <div>
        <h2 className="text-lg font-semibold text-gray-900">Proveedores y terceros</h2>
        <p className="mt-1 text-sm text-gray-500">
          Indica si terceros participan en esta actividad o acceden a los datos personales tratados.
        </p>
      </div>

      <div className="mt-6 grid gap-3 sm:grid-cols-3">
        {[
          { value: "si", label: "Sí intervienen" },
          { value: "no", label: "No intervienen" },
          { value: "pendiente", label: "Pendiente de revisión" },
        ].map((option) => (
          <label
            key={option.value}
            className="flex cursor-pointer items-center gap-3 rounded-lg border border-gray-200 p-4"
          >
            <input
              type="radio"
              name="vendors-declaration"
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
            <div className="flex items-center justify-between gap-3">
              <div>
                <h3 className="text-sm font-semibold text-gray-900">
                  Relaciones con proveedores o terceros
                </h3>
                <p className="mt-1 text-xs text-gray-500">
                  Un proveedor puede tener más de un rol, pero no puedes repetir la misma
                  combinación proveedor + tipo.
                </p>
              </div>

              <button
                type="button"
                onClick={addRelation}
                className="text-sm font-medium text-blue-700 hover:underline"
              >
                + Agregar relación
              </button>
            </div>

            {loadingCatalog ? (
              <p className="mt-4 text-sm text-gray-500">Cargando proveedores…</p>
            ) : relations.length === 0 ? (
              <div className="mt-4 rounded-lg border border-dashed border-gray-300 p-4 text-sm text-gray-500">
                Aún no has asociado proveedores o terceros.
              </div>
            ) : (
              <div className="mt-4 space-y-4">
                {relations.map((relation) => (
                  <div key={relation.key} className="rounded-lg border border-gray-200 p-4">
                    <div className="grid gap-4 md:grid-cols-2">
                      <div>
                        <label>
                          <span className="text-sm font-medium text-gray-700">
                            Proveedor o tercero *
                          </span>
                          <select
                            value={
                              addingVendorKey === relation.key ? "__new__" : relation.vendor_id
                            }
                            disabled={creating}
                            onChange={(e) => {
                              setNewVendor(EMPTY_VENDOR);
                              setAddingVendorKey(
                                e.target.value === "__new__" ? relation.key : null
                              );
                              setSaved(false);
                              if (e.target.value !== "__new__") {
                                updateRelation(relation.key, { vendor_id: e.target.value });
                              }
                            }}
                            className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2"
                          >
                            <option value="">Selecciona</option>
                            <option value="__new__">+ Agregar nuevo...</option>
                            {catalog.map((vendor) => (
                              <option key={vendor.id} value={vendor.id}>
                                {vendor.name}
                                {vendor.country ? ` — ${vendor.country}` : ""}
                              </option>
                            ))}
                          </select>
                        </label>
                        {addingVendorKey === relation.key && (
                          <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
                            <h3 className="text-sm font-semibold text-gray-900">
                              Agregar proveedor o tercero al catálogo
                            </h3>

                            <div className="mt-4 grid gap-4 md:grid-cols-2">
                              <input
                                type="text"
                                value={newVendor.name}
                                onChange={(e) =>
                                  setNewVendor((current) => ({
                                    ...current,
                                    name: e.target.value,
                                  }))
                                }
                                aria-label="Nombre del nuevo proveedor"
                                disabled={creating}
                                placeholder="Nombre *"
                                className="rounded-lg border border-gray-300 px-3 py-2"
                              />

                              <input
                                type="text"
                                value={newVendor.country}
                                onChange={(e) =>
                                  setNewVendor((current) => ({
                                    ...current,
                                    country: e.target.value,
                                  }))
                                }
                                aria-label="País del nuevo proveedor"
                                disabled={creating}
                                placeholder="País"
                                className="rounded-lg border border-gray-300 px-3 py-2"
                              />
                            </div>

                            <div className="mt-4 flex justify-end gap-3">
                              <button
                                type="button"
                                disabled={creating}
                                onClick={() => {
                                  setAddingVendorKey(null);
                                  setNewVendor(EMPTY_VENDOR);
                                }}
                                className="text-sm text-gray-600 disabled:opacity-60"
                              >
                                Cancelar
                              </button>
                              <button
                                type="button"
                                onClick={() => createVendor(relation.key)}
                                disabled={creating}
                                className="rounded-lg border border-blue-700 px-4 py-2 text-sm font-medium text-blue-700 hover:bg-blue-50 disabled:opacity-60"
                              >
                                {creating ? "Creando…" : "Agregar proveedor"}
                              </button>
                            </div>
                          </div>
                        )}
                      </div>

                      <label>
                        <span className="text-sm font-medium text-gray-700">Tipo de relación</span>
                        <select
                          value={relation.relationship_type}
                          onChange={(e) =>
                            updateRelation(relation.key, {
                              relationship_type: e.target.value as VendorRelationshipType,
                              ...(e.target.value !== "encargado"
                                ? {
                                    engagement_object: "",
                                    engagement_duration: "",
                                    has_subprocessors: false,
                                  }
                                : {}),
                            })
                          }
                          className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2"
                        >
                          <option value="encargado">Encargado de tratamiento</option>
                          <option value="cesionario">Cesionario</option>
                          <option value="otro">Otro tercero</option>
                        </select>

                        <div className="mt-2 rounded-lg bg-blue-50 px-3 py-2 text-xs text-gray-700">
                          {relation.relationship_type === "encargado" && (
                            <p>
                              <strong>Encargado de tratamiento:</strong> presta un servicio y trata
                              datos personales siguiendo las instrucciones de tu organización.
                              Ejemplos: proveedor cloud, nómina, CRM administrado, mesa de ayuda o
                              SOC administrado.
                            </p>
                          )}

                          {relation.relationship_type === "cesionario" && (
                            <p>
                              <strong>Cesionario:</strong> recibe datos personales y los trata como
                              responsable para finalidades propias.
                            </p>
                          )}

                          {relation.relationship_type === "otro" && (
                            <p>
                              <strong>Otro tercero:</strong> participa en la actividad, pero no
                              actúa como encargado de tratamiento ni como cesionario.
                            </p>
                          )}
                        </div>
                      </label>

                      <label className="md:col-span-2">
                        <span className="text-sm font-medium text-gray-700">
                          Finalidad de la relación
                        </span>
                        <input
                          type="text"
                          value={relation.purpose}
                          onChange={(e) =>
                            updateRelation(relation.key, {
                              purpose: e.target.value,
                            })
                          }
                          placeholder="Ej. Prestación del servicio de almacenamiento"
                          className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2"
                        />
                      </label>

                      <label className="flex items-center gap-2 text-sm text-gray-700">
                        <input
                          type="checkbox"
                          checked={relation.has_data_access}
                          onChange={(e) =>
                            updateRelation(relation.key, {
                              has_data_access: e.target.checked,
                            })
                          }
                          className="h-4 w-4 rounded border-gray-300"
                        />
                        Tiene acceso a datos personales
                      </label>

                      <label className="flex items-center gap-2 text-sm text-gray-700">
                        <input
                          type="checkbox"
                          checked={relation.has_contract}
                          onChange={(e) =>
                            updateRelation(relation.key, {
                              has_contract: e.target.checked,
                            })
                          }
                          className="h-4 w-4 rounded border-gray-300"
                        />
                        ¿Existe contrato o acuerdo documentado?
                      </label>

                      <div className="md:col-span-2 rounded-lg border border-gray-200 bg-gray-50 px-4 py-3 text-xs text-gray-600">
                        {relation.relationship_type === "encargado" && (
                          <p>
                            <strong>Sobre el documento:</strong> cuando esta organización actúa como
                            encargado de tratamiento, el servicio debe quedar regulado mediante un
                            contrato o acuerdo que describa el encargo, incluyendo su objeto,
                            duración, finalidad y las obligaciones de las partes.
                          </p>
                        )}

                        {relation.relationship_type === "cesionario" && (
                          <p>
                            <strong>Sobre el documento:</strong> cuando existe una cesión de datos,
                            conviene identificar el documento que deja constancia de las partes, los
                            datos comunicados y las finalidades de la cesión.
                          </p>
                        )}

                        {relation.relationship_type === "otro" && (
                          <p>
                            <strong>Sobre el documento:</strong> puede existir un contrato o acuerdo
                            aunque no corresponda específicamente a un encargo de tratamiento o a
                            una cesión. Si existe, CumpleIA permite dejarlo identificado.
                          </p>
                        )}

                        <p className="mt-2 border-t border-gray-200 pt-2">
                          <strong>¿Por qué pedimos una referencia?</strong> CumpleIA utiliza este
                          dato para localizar posteriormente la evidencia correspondiente, por
                          ejemplo: número de contrato, nombre del documento, fecha, enlace o código
                          interno. La ley no exige un campo denominado “referencia del contrato”.
                        </p>
                      </div>

                      {relation.has_contract && (
                        <label className="md:col-span-2">
                          <span className="text-sm font-medium text-gray-700">
                            Identificación o referencia del contrato/acuerdo *
                          </span>
                          <input
                            type="text"
                            value={relation.contract_reference}
                            onChange={(e) =>
                              updateRelation(relation.key, {
                                contract_reference: e.target.value,
                              })
                            }
                            className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2"
                            placeholder="Ej. Contrato SOC-2026-014 / Acuerdo de tratamiento de datos"
                          />
                        </label>
                      )}

                      {relation.relationship_type === "encargado" && (
                        <>
                          <label>
                            <span className="text-sm font-medium text-gray-700">
                              Objeto del encargo
                            </span>
                            <input
                              type="text"
                              value={relation.engagement_object}
                              onChange={(e) =>
                                updateRelation(relation.key, {
                                  engagement_object: e.target.value,
                                })
                              }
                              className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2"
                            />
                          </label>

                          <label>
                            <span className="text-sm font-medium text-gray-700">
                              Duración del encargo
                            </span>
                            <input
                              type="text"
                              value={relation.engagement_duration}
                              onChange={(e) =>
                                updateRelation(relation.key, {
                                  engagement_duration: e.target.value,
                                })
                              }
                              className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2"
                              placeholder="Ej. Mientras dure el contrato"
                            />
                          </label>

                          <label className="flex items-center gap-2 text-sm text-gray-700">
                            <input
                              type="checkbox"
                              checked={relation.has_subprocessors}
                              onChange={(e) =>
                                updateRelation(relation.key, {
                                  has_subprocessors: e.target.checked,
                                })
                              }
                              className="h-4 w-4 rounded border-gray-300"
                            />
                            Utiliza subencargados
                          </label>
                        </>
                      )}

                      <label className="md:col-span-2">
                        <span className="text-sm font-medium text-gray-700">Notas</span>
                        <textarea
                          rows={2}
                          value={relation.notes}
                          onChange={(e) =>
                            updateRelation(relation.key, {
                              notes: e.target.value,
                            })
                          }
                          className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2"
                        />
                      </label>
                    </div>

                    <div className="mt-4 flex justify-end">
                      <button
                        type="button"
                        onClick={() => removeRelation(relation.key)}
                        disabled={creating && addingVendorKey === relation.key}
                        className="text-sm font-medium text-red-600 hover:text-red-700"
                      >
                        Eliminar relación
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {declaration === "si" && (
        <details className="mt-6 rounded-lg border border-gray-200 bg-gray-50">
          <summary className="cursor-pointer px-4 py-3 text-sm font-medium text-gray-700">
            Administrar catálogo de organizaciones
          </summary>

          <div className="border-t border-gray-200 px-4 py-4">
            <p className="mb-3 text-xs text-gray-500">
              Aquí puedes eliminar proveedores u otras organizaciones que ya no necesites. Si una
              organización está asociada a una actividad de tratamiento, primero debes eliminar esa
              relación.
            </p>

            {catalog.length === 0 ? (
              <p className="text-sm text-gray-500">No hay organizaciones registradas.</p>
            ) : (
              <div className="divide-y divide-gray-200">
                {catalog.map((vendor) => (
                  <div key={vendor.id} className="flex items-center justify-between gap-4 py-3">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{vendor.name}</p>
                      {vendor.country && <p className="text-xs text-gray-500">{vendor.country}</p>}
                    </div>

                    <button
                      type="button"
                      onClick={() => deleteVendorFromCatalog(vendor)}
                      disabled={deletingVendorId === vendor.id}
                      className="text-sm font-medium text-red-600 hover:text-red-700 disabled:opacity-50"
                    >
                      {deletingVendorId === vendor.id ? "Eliminando…" : "Eliminar del catálogo"}
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </details>
      )}

      {declaration === "no" && (
        <p className="mt-5 text-sm text-gray-500">
          Al guardar, se eliminarán las asociaciones de proveedores y terceros existentes para esta
          actividad.
        </p>
      )}

      {declaration === "pendiente" && (
        <p className="mt-5 text-sm text-amber-700">
          Mientras esta declaración permanezca pendiente, el requisito de proveedores no se
          considerará resuelto.
        </p>
      )}

      {error && (
        <div className="mt-5 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
      )}

      {saved && (
        <div className="mt-5 rounded-lg bg-green-50 px-4 py-3 text-sm text-green-700">
          Información de proveedores guardada.
        </div>
      )}

      <div className="mt-6 flex justify-end">
        <button
          type="button"
          onClick={saveVendors}
          disabled={saving || creating || addingVendorKey !== null}
          className="rounded-lg bg-blue-700 px-5 py-2.5 text-sm font-medium text-white hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {saving ? "Guardando…" : "Guardar proveedores"}
        </button>
      </div>
    </section>
  );
}
