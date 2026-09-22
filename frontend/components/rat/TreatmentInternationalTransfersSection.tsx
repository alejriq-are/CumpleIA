"use client";

import { useEffect, useMemo, useState } from "react";
import { createClient } from "@/lib/supabase/client";
import {
  ApiError,
  api,
  type AdequacyStatus,
  type DeclarationStatus,
  type InternationalTransferCreate,
  type InternationalTransferOut,
  type TreatmentDetailOut,
  type VendorOut,
} from "@/lib/api/client";

type Props = {
  organizationId: string;
  treatmentId: string;
  treatment: TreatmentDetailOut;
  onSaved: (treatment: TreatmentDetailOut) => void;
};

type RecipientMode = "vendor" | "manual";

type TransferDraft = {
  key: string;
  id: string | null;
  recipientMode: RecipientMode;
  vendor_id: string;
  recipient_name: string;
  destination_country: string;
  adequacy_status: AdequacyStatus;
  mechanism: string;
  guarantees_description: string;
  evidence_reference: string;
};

function nullable(value: string) {
  const trimmed = value.trim();
  return trimmed ? trimmed : null;
}

function draftFromTransfer(item: InternationalTransferOut): TransferDraft {
  return {
    key: item.id,
    id: item.id,
    recipientMode: item.vendor_id ? "vendor" : "manual",
    vendor_id: item.vendor_id ?? "",
    recipient_name: item.recipient_name ?? "",
    destination_country: item.destination_country,
    adequacy_status: item.adequacy_status,
    mechanism: item.mechanism ?? "",
    guarantees_description: item.guarantees_description ?? "",
    evidence_reference: item.evidence_reference ?? "",
  };
}

function newTransfer(): TransferDraft {
  return {
    key: crypto.randomUUID(),
    id: null,
    recipientMode: "vendor",
    vendor_id: "",
    recipient_name: "",
    destination_country: "",
    adequacy_status: "pendiente",
    mechanism: "",
    guarantees_description: "",
    evidence_reference: "",
  };
}

const ADEQUACY_OPTIONS: Array<{
  value: AdequacyStatus;
  label: string;
}> = [
  { value: "adecuado", label: "Adecuado" },
  { value: "no_adecuado", label: "No adecuado" },
  { value: "pendiente", label: "Pendiente de revisión" },
  { value: "no_determinado", label: "No determinado" },
];

export function TreatmentInternationalTransfersSection({
  organizationId,
  treatmentId,
  treatment,
  onSaved,
}: Props) {
  const [declaration, setDeclaration] = useState<DeclarationStatus | "">(
    treatment.international_transfers_declaration ?? ""
  );

  const [transfers, setTransfers] = useState<TransferDraft[]>(
    treatment.international_transfers.map(draftFromTransfer)
  );

  const [vendors, setVendors] = useState<VendorOut[]>([]);
  const [loadingVendors, setLoadingVendors] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const existingTransferIds = useMemo(
    () => new Set(treatment.international_transfers.map((item) => item.id)),
    [treatment.international_transfers]
  );

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

        const catalog = await api.rat.listVendors(session.access_token, organizationId);

        if (active) setVendors(catalog);
      } catch (e) {
        if (!active) return;

        setError(
          e instanceof Error ? e.message : "No se pudo cargar el catálogo de organizaciones."
        );
      } finally {
        if (active) setLoadingVendors(false);
      }
    })();

    return () => {
      active = false;
    };
  }, [organizationId]);

  function addTransfer() {
    setSaved(false);
    setTransfers((current) => [...current, newTransfer()]);
  }

  function removeTransfer(key: string) {
    setSaved(false);
    setTransfers((current) => current.filter((item) => item.key !== key));
  }

  function updateTransfer(key: string, patch: Partial<Omit<TransferDraft, "key" | "id">>) {
    setSaved(false);
    setTransfers((current) =>
      current.map((item) => (item.key === key ? { ...item, ...patch } : item))
    );
  }

  function validateTransfers() {
    if (declaration !== "si") return null;

    if (transfers.length === 0) {
      return "Si existen transferencias internacionales, registra al menos una.";
    }

    for (const item of transfers) {
      if (item.recipientMode === "vendor" && !item.vendor_id) {
        return "Selecciona una organización destinataria en todas las transferencias.";
      }

      if (item.recipientMode === "manual" && !item.recipient_name.trim()) {
        return "Indica el nombre del destinatario en todas las transferencias.";
      }

      if (!item.destination_country.trim()) {
        return "Indica el país de destino en todas las transferencias.";
      }
    }

    return null;
  }

  function toPayload(item: TransferDraft): InternationalTransferCreate {
    return {
      vendor_id: item.recipientMode === "vendor" ? item.vendor_id || null : null,
      recipient_name: item.recipientMode === "manual" ? nullable(item.recipient_name) : null,
      destination_country: item.destination_country.trim(),
      adequacy_status: item.adequacy_status,
      mechanism: nullable(item.mechanism),
      guarantees_description: nullable(item.guarantees_description),
      evidence_reference: nullable(item.evidence_reference),
    };
  }

  async function saveTransfers() {
    if (!declaration) {
      setError("Debes indicar si existen transferencias internacionales.");
      return;
    }

    const validationError = validateTransfers();
    if (validationError) {
      setError(validationError);
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

      const token = session.access_token;

      if (declaration === "no") {
        for (const transfer of treatment.international_transfers) {
          await api.rat.deleteInternationalTransfer(token, organizationId, transfer.id);
        }
      } else {
        const draftExistingIds = new Set(
          transfers.map((item) => item.id).filter((id): id is string => Boolean(id))
        );

        for (const existingId of existingTransferIds) {
          if (!draftExistingIds.has(existingId)) {
            await api.rat.deleteInternationalTransfer(token, organizationId, existingId);
          }
        }

        for (const item of transfers) {
          const payload = toPayload(item);

          if (item.id) {
            await api.rat.updateInternationalTransfer(token, organizationId, item.id, payload);
          } else {
            await api.rat.createInternationalTransfer(token, organizationId, treatmentId, payload);
          }
        }
      }

      await api.rat.updateTreatment(token, organizationId, treatmentId, {
        international_transfers_declaration: declaration,
      });

      const refreshed = await api.rat.getTreatment(token, organizationId, treatmentId);

      setDeclaration(refreshed.international_transfers_declaration ?? "");
      setTransfers(refreshed.international_transfers.map(draftFromTransfer));

      onSaved(refreshed);
      setSaved(true);
    } catch (e) {
      if (e instanceof ApiError) {
        setError(e.message);
      } else {
        setError(
          e instanceof Error
            ? e.message
            : "No se pudo guardar la información de transferencias internacionales."
        );
      }
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <div>
        <h2 className="text-lg font-semibold text-gray-900">Transferencias internacionales</h2>
        <p className="mt-1 text-sm text-gray-500">
          Indica si en esta actividad los datos personales son enviados, almacenados o puestos a
          disposición de destinatarios ubicados fuera de Chile.
        </p>
      </div>

      <div className="mt-6 grid gap-3 sm:grid-cols-3">
        {[
          {
            value: "si",
            label: "Sí existen",
          },
          {
            value: "no",
            label: "No existen",
          },
          {
            value: "pendiente",
            label: "Pendiente de revisión",
          },
        ].map((option) => (
          <label
            key={option.value}
            className="flex cursor-pointer items-center gap-3 rounded-lg border border-gray-200 p-4"
          >
            <input
              type="radio"
              name="international-transfers-declaration"
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
        <div className="mt-8">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h3 className="text-sm font-semibold text-gray-900">Transferencias registradas</h3>
              <p className="mt-1 text-xs text-gray-500">
                Registra cada destinatario y país al que se transfieren o desde donde se accede a
                los datos.
              </p>
            </div>

            <button
              type="button"
              onClick={addTransfer}
              className="text-sm font-medium text-blue-700 hover:underline"
            >
              + Agregar transferencia
            </button>
          </div>

          {transfers.length === 0 ? (
            <div className="mt-4 rounded-lg border border-dashed border-gray-300 p-4 text-sm text-gray-500">
              Aún no has registrado transferencias internacionales.
            </div>
          ) : (
            <div className="mt-4 space-y-5">
              {transfers.map((transfer, index) => (
                <div key={transfer.key} className="rounded-lg border border-gray-200 p-4">
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-semibold text-gray-900">
                      Transferencia {index + 1}
                    </h4>

                    <button
                      type="button"
                      onClick={() => removeTransfer(transfer.key)}
                      className="text-sm font-medium text-red-600 hover:text-red-700"
                    >
                      Eliminar
                    </button>
                  </div>

                  <div className="mt-4 grid gap-4 md:grid-cols-2">
                    <div className="md:col-span-2">
                      <span className="text-sm font-medium text-gray-700">Destinatario</span>

                      <div className="mt-2 flex flex-wrap gap-5">
                        <label className="flex items-center gap-2 text-sm text-gray-700">
                          <input
                            type="radio"
                            checked={transfer.recipientMode === "vendor"}
                            onChange={() =>
                              updateTransfer(transfer.key, {
                                recipientMode: "vendor",
                                recipient_name: "",
                              })
                            }
                          />
                          Organización registrada
                        </label>

                        <label className="flex items-center gap-2 text-sm text-gray-700">
                          <input
                            type="radio"
                            checked={transfer.recipientMode === "manual"}
                            onChange={() =>
                              updateTransfer(transfer.key, {
                                recipientMode: "manual",
                                vendor_id: "",
                              })
                            }
                          />
                          Otro destinatario
                        </label>
                      </div>
                    </div>

                    {transfer.recipientMode === "vendor" ? (
                      <label className="md:col-span-2">
                        <span className="text-sm font-medium text-gray-700">
                          Organización destinataria *
                        </span>

                        <select
                          value={transfer.vendor_id}
                          onChange={(e) =>
                            updateTransfer(transfer.key, {
                              vendor_id: e.target.value,
                            })
                          }
                          disabled={loadingVendors}
                          className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2"
                        >
                          <option value="">
                            {loadingVendors ? "Cargando organizaciones…" : "Selecciona"}
                          </option>

                          {vendors.map((vendor) => (
                            <option key={vendor.id} value={vendor.id}>
                              {vendor.name}
                              {vendor.country ? ` — ${vendor.country}` : ""}
                            </option>
                          ))}
                        </select>
                      </label>
                    ) : (
                      <label className="md:col-span-2">
                        <span className="text-sm font-medium text-gray-700">
                          Nombre del destinatario *
                        </span>

                        <input
                          type="text"
                          value={transfer.recipient_name}
                          onChange={(e) =>
                            updateTransfer(transfer.key, {
                              recipient_name: e.target.value,
                            })
                          }
                          placeholder="Ej. Data Center XYZ"
                          className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2"
                        />
                      </label>
                    )}

                    <label>
                      <span className="text-sm font-medium text-gray-700">País de destino *</span>

                      <input
                        type="text"
                        value={transfer.destination_country}
                        onChange={(e) =>
                          updateTransfer(transfer.key, {
                            destination_country: e.target.value,
                          })
                        }
                        placeholder="Ej. Estados Unidos"
                        className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2"
                      />
                    </label>

                    <label>
                      <span className="text-sm font-medium text-gray-700">
                        Estado de adecuación
                      </span>

                      <select
                        value={transfer.adequacy_status}
                        onChange={(e) =>
                          updateTransfer(transfer.key, {
                            adequacy_status: e.target.value as AdequacyStatus,
                          })
                        }
                        className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2"
                      >
                        {ADEQUACY_OPTIONS.map((option) => (
                          <option key={option.value} value={option.value}>
                            {option.label}
                          </option>
                        ))}
                      </select>

                      <div className="mt-2 rounded-lg bg-blue-50 px-3 py-2 text-xs text-gray-700">
                        {transfer.adequacy_status === "adecuado" && (
                          <p>
                            <strong>Adecuado:</strong> el país de destino cuenta con un nivel de
                            protección reconocido como adecuado para la transferencia de datos
                            personales.
                          </p>
                        )}

                        {transfer.adequacy_status === "no_adecuado" && (
                          <p>
                            <strong>No adecuado:</strong> el país no cuenta con un nivel de
                            protección reconocido como adecuado. Esto no significa por sí solo un
                            incumplimiento, pero la transferencia debe sustentarse en otro mecanismo
                            o garantía aplicable.
                          </p>
                        )}

                        {transfer.adequacy_status === "pendiente" && (
                          <p>
                            <strong>Pendiente de revisión:</strong> este punto aún debe ser revisado
                            antes de considerar resuelta la situación de la transferencia.
                          </p>
                        )}

                        {transfer.adequacy_status === "no_determinado" && (
                          <p>
                            <strong>No determinado:</strong> todavía no existe información
                            suficiente para concluir si el país de destino puede considerarse
                            adecuado.
                          </p>
                        )}

                        <p className="mt-2 border-t border-blue-100 pt-2">
                          <strong>Importante:</strong> este estado evalúa el nivel de protección del
                          país de destino, no la seguridad, calidad o reputación del proveedor.
                        </p>
                      </div>
                    </label>

                    {transfer.adequacy_status === "no_adecuado" && (
                      <div className="md:col-span-2 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
                        <strong>Documenta el fundamento de la transferencia.</strong> Indica a
                        continuación el mecanismo aplicable, las garantías o medidas utilizadas y
                        una referencia a la evidencia que permita respaldarlas.
                      </div>
                    )}

                    <label className="md:col-span-2">
                      <span className="text-sm font-medium text-gray-700">Mecanismo aplicable</span>

                      <input
                        type="text"
                        value={transfer.mechanism}
                        onChange={(e) =>
                          updateTransfer(transfer.key, {
                            mechanism: e.target.value,
                          })
                        }
                        placeholder="Ej. Cláusulas contractuales"
                        className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2"
                      />
                    </label>

                    <label className="md:col-span-2">
                      <span className="text-sm font-medium text-gray-700">
                        Garantías o medidas aplicadas
                      </span>

                      <textarea
                        rows={2}
                        value={transfer.guarantees_description}
                        onChange={(e) =>
                          updateTransfer(transfer.key, {
                            guarantees_description: e.target.value,
                          })
                        }
                        placeholder="Describe brevemente las garantías aplicables."
                        className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2"
                      />
                    </label>

                    <label className="md:col-span-2">
                      <span className="text-sm font-medium text-gray-700">
                        Referencia de evidencia
                      </span>

                      <input
                        type="text"
                        value={transfer.evidence_reference}
                        onChange={(e) =>
                          updateTransfer(transfer.key, {
                            evidence_reference: e.target.value,
                          })
                        }
                        placeholder="Ej. Contrato, cláusula, informe o documento interno"
                        className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2"
                      />
                    </label>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {declaration === "no" && (
        <div className="mt-5 rounded-lg bg-gray-50 px-4 py-3 text-sm text-gray-600">
          Al guardar “No existen”, se eliminarán las transferencias internacionales previamente
          registradas para esta actividad.
        </div>
      )}

      {declaration === "pendiente" && (
        <div className="mt-5 rounded-lg bg-amber-50 px-4 py-3 text-sm text-amber-700">
          Mientras esta declaración permanezca pendiente, el requisito de transferencias
          internacionales no se considerará resuelto.
        </div>
      )}

      {error && (
        <div className="mt-5 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
      )}

      {saved && (
        <div className="mt-5 rounded-lg bg-green-50 px-4 py-3 text-sm text-green-700">
          Información de transferencias internacionales guardada.
        </div>
      )}

      <div className="mt-6 flex justify-end">
        <button
          type="button"
          onClick={saveTransfers}
          disabled={saving}
          className="rounded-lg bg-blue-700 px-5 py-2.5 text-sm font-medium text-white hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {saving ? "Guardando…" : "Guardar transferencias"}
        </button>
      </div>
    </section>
  );
}
