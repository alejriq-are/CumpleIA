"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";
import { TreatmentProgress } from "@/components/rat/TreatmentProgress";
import {
  ApiError,
  api,
  type OrganizationMembershipOut,
  type OrganizationRole,
  type TreatmentCreate,
  type TreatmentDetailOut,
} from "@/lib/api/client";

type Props = {
  organizaciones: OrganizationMembershipOut[];
  initialOrganizationId: string;
  treatmentId?: string;
};

type FormState = {
  name: string;
  description: string;
  organization_role: OrganizationRole | "";
  business_area: string;
  data_flow_description: string;
  start_date: string;
  next_review_at: string;
  retention_rule: string;
  deletion_method: string;
  has_automated_decisions: boolean;
  automated_decision_description: string;
};

const EMPTY_FORM: FormState = {
  name: "",
  description: "",
  organization_role: "",
  business_area: "",
  data_flow_description: "",
  start_date: "",
  next_review_at: "",
  retention_rule: "",
  deletion_method: "",
  has_automated_decisions: false,
  automated_decision_description: "",
};

function detailToForm(detail: TreatmentDetailOut): FormState {
  return {
    name: detail.name,
    description: detail.description ?? "",
    organization_role: detail.organization_role ?? "",
    business_area: detail.business_area ?? "",
    data_flow_description: detail.data_flow_description ?? "",
    start_date: detail.start_date ?? "",
    next_review_at: detail.next_review_at ? detail.next_review_at.slice(0, 16) : "",
    retention_rule: detail.retention_rule ?? "",
    deletion_method: detail.deletion_method ?? "",
    has_automated_decisions: detail.has_automated_decisions,
    automated_decision_description: detail.automated_decision_description ?? "",
  };
}

function nullable(value: string) {
  const trimmed = value.trim();
  return trimmed ? trimmed : null;
}

export function TreatmentGeneralForm({
  organizaciones,
  initialOrganizationId,
  treatmentId,
}: Props) {
  const router = useRouter();

  const [orgId, setOrgId] = useState(initialOrganizationId);
  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [detail, setDetail] = useState<TreatmentDetailOut | null>(null);
  const [loading, setLoading] = useState(Boolean(treatmentId));
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [errorStatus, setErrorStatus] = useState<number | null>(null);

  const editing = Boolean(treatmentId);

  useEffect(() => {
    if (!treatmentId) {
      setForm(EMPTY_FORM);
      setLoading(false);
      return;
    }

    let vigente = true;
    setLoading(true);
    setError(null);
    setErrorStatus(null);

    (async () => {
      try {
        const supabase = createClient();
        const {
          data: { session },
        } = await supabase.auth.getSession();

        if (!session) {
          throw new Error("Tu sesión expiró. Vuelve a iniciar sesión.");
        }

        const detail = await api.rat.getTreatment(session.access_token, orgId, treatmentId);

        if (!vigente) return;
        setForm(detailToForm(detail));
        setDetail(detail);
      } catch (e) {
        if (!vigente) return;

        if (e instanceof ApiError) {
          setErrorStatus(e.status);
          setError(e.message);
        } else {
          setError(
            e instanceof Error ? e.message : "No se pudo cargar la actividad de tratamiento."
          );
        }
      } finally {
        if (vigente) setLoading(false);
      }
    })();

    return () => {
      vigente = false;
    };
  }, [orgId, treatmentId]);

  function update<K extends keyof FormState>(field: K, value: FormState[K]) {
    setSaved(false);
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!form.name.trim()) {
      setError("Debes indicar el nombre de la actividad.");
      return;
    }

    if (!form.organization_role) {
      setError("Debes indicar el rol de la organización.");
      return;
    }

    setSaving(true);
    setSaved(false);
    setError(null);
    setErrorStatus(null);

    try {
      const supabase = createClient();
      const {
        data: { session },
      } = await supabase.auth.getSession();

      if (!session) {
        throw new Error("Tu sesión expiró. Vuelve a iniciar sesión.");
      }

      const body: TreatmentCreate = {
        name: form.name.trim(),
        description: nullable(form.description),
        organization_role: form.organization_role,
        business_area: nullable(form.business_area),
        data_flow_description: nullable(form.data_flow_description),
        start_date: form.start_date || null,
        next_review_at: form.next_review_at ? new Date(form.next_review_at).toISOString() : null,
        retention_rule: nullable(form.retention_rule),
        deletion_method: nullable(form.deletion_method),
        has_automated_decisions: form.has_automated_decisions,
        automated_decision_description: form.has_automated_decisions
          ? nullable(form.automated_decision_description)
          : null,
      };

      if (treatmentId) {
        const updated = await api.rat.updateTreatment(
          session.access_token,
          orgId,
          treatmentId,
          body
        );

        setForm(detailToForm(updated));
        setDetail(updated);
        setSaved(true);
      } else {
        const created = await api.rat.createTreatment(session.access_token, orgId, body);

        router.push(`/dashboard/rat/${created.id}?organizationId=${encodeURIComponent(orgId)}`);
        router.refresh();
      }
    } catch (e) {
      if (e instanceof ApiError) {
        setErrorStatus(e.status);
        setError(e.message);
      } else {
        setError(e instanceof Error ? e.message : "No se pudieron guardar los cambios.");
      }
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="rounded-xl border border-gray-200 bg-white px-6 py-8 text-sm text-gray-500">
        Cargando actividad…
      </div>
    );
  }

  if (errorStatus === 402) {
    return (
      <div className="rounded-xl border border-amber-200 bg-amber-50 px-5 py-4 text-sm text-amber-800">
        Tu suscripción no permite actualmente acceder al Inventario de Tratamientos.
      </div>
    );
  }

  if (errorStatus === 403) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">
        No tienes permisos para acceder a esta actividad.
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {editing && detail && <TreatmentProgress treatment={detail} />}
      {organizaciones.length > 1 && !editing && (
        <label className="block text-sm text-gray-700">
          Organización
          <select
            value={orgId}
            onChange={(e) => setOrgId(e.target.value)}
            className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            {organizaciones.map((org) => (
              <option key={org.id} value={org.id}>
                {org.name}
              </option>
            ))}
          </select>
        </label>
      )}

      {error && <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

      {saved && (
        <div className="rounded-lg bg-green-50 px-4 py-3 text-sm text-green-700">
          Cambios guardados.
        </div>
      )}

      <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <div className="mb-6">
          <h2 className="text-lg font-semibold text-gray-900">Información general</h2>
          <p className="mt-1 text-sm text-gray-500">
            Describe la actividad de tratamiento. Podrás completar las demás secciones del RAT
            posteriormente.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
          <label className="md:col-span-2">
            <span className="text-sm font-medium text-gray-700">Nombre de la actividad *</span>
            <input
              type="text"
              required
              value={form.name}
              onChange={(e) => update("name", e.target.value)}
              className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              placeholder="Ej. Gestión de clientes"
            />
          </label>

          <label className="md:col-span-2">
            <span className="text-sm font-medium text-gray-700">Descripción</span>
            <textarea
              rows={3}
              value={form.description}
              onChange={(e) => update("description", e.target.value)}
              className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </label>

          <label>
            <span className="text-sm font-medium text-gray-700">Área de negocio</span>
            <input
              type="text"
              value={form.business_area}
              onChange={(e) => update("business_area", e.target.value)}
              className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              placeholder="Ej. Comercial"
            />
          </label>

          <label>
            <span className="text-sm font-medium text-gray-700">Rol de la organización *</span>
            <select
              required
              value={form.organization_role}
              onChange={(e) => update("organization_role", e.target.value as OrganizationRole | "")}
              className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="">Selecciona</option>
              <option value="responsable">Responsable</option>
              <option value="encargado">Encargado</option>
            </select>
          </label>

          <label className="md:col-span-2">
            <span className="text-sm font-medium text-gray-700">
              Descripción general del flujo de datos
            </span>
            <textarea
              rows={4}
              value={form.data_flow_description}
              onChange={(e) => update("data_flow_description", e.target.value)}
              className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              placeholder="Describe de forma simple cómo se obtienen, usan y almacenan los datos."
            />
          </label>

          <label>
            <span className="text-sm font-medium text-gray-700">Fecha de inicio</span>
            <input
              type="date"
              value={form.start_date}
              onChange={(e) => update("start_date", e.target.value)}
              className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm"
            />
          </label>

          <label>
            <span className="text-sm font-medium text-gray-700">Próxima revisión</span>
            <input
              type="datetime-local"
              value={form.next_review_at}
              onChange={(e) => update("next_review_at", e.target.value)}
              className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm"
            />
          </label>

          <label className="md:col-span-2">
            <span className="text-sm font-medium text-gray-700">Regla de conservación</span>
            <textarea
              rows={2}
              value={form.retention_rule}
              onChange={(e) => update("retention_rule", e.target.value)}
              className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm"
              placeholder="Ej. Cinco años desde el término de la relación contractual."
            />
          </label>

          <label className="md:col-span-2">
            <span className="text-sm font-medium text-gray-700">Método de eliminación</span>
            <textarea
              rows={2}
              value={form.deletion_method}
              onChange={(e) => update("deletion_method", e.target.value)}
              className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm"
              placeholder="Ej. Eliminación segura del sistema y respaldos según política interna."
            />
          </label>

          <div className="md:col-span-2">
            <label className="flex items-center gap-3 text-sm font-medium text-gray-700">
              <input
                type="checkbox"
                checked={form.has_automated_decisions}
                onChange={(e) => update("has_automated_decisions", e.target.checked)}
                className="h-4 w-4 rounded border-gray-300"
              />
              Existen decisiones automatizadas
            </label>
          </div>

          {form.has_automated_decisions && (
            <label className="md:col-span-2">
              <span className="text-sm font-medium text-gray-700">
                Descripción de la decisión automatizada
              </span>
              <textarea
                rows={3}
                value={form.automated_decision_description}
                onChange={(e) => update("automated_decision_description", e.target.value)}
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm"
              />
            </label>
          )}
        </div>
      </section>

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={saving}
          className="rounded-lg bg-blue-700 px-5 py-2.5 text-sm font-medium text-white hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {saving ? "Guardando…" : editing ? "Guardar cambios" : "Crear actividad"}
        </button>
      </div>
    </form>
  );
}
