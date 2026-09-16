"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { createClient } from "@/lib/supabase/client";
import {
  ApiError,
  api,
  type OrganizationMembershipOut,
  type TreatmentStatus,
  type TreatmentSummaryOut,
} from "@/lib/api/client";

function statusLabel(status: TreatmentStatus) {
  switch (status) {
    case "activo":
      return "Activo";
    case "archivado":
      return "Archivado";
    default:
      return "Registro en preparación";
  }
}

function statusClasses(status: TreatmentStatus) {
  switch (status) {
    case "activo":
      return "bg-green-50 text-green-700";
    case "archivado":
      return "bg-gray-100 text-gray-600";
    default:
      return "bg-amber-50 text-amber-700";
  }
}

function formatDate(value?: string | null) {
  if (!value) return "—";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "—";

  return new Intl.DateTimeFormat("es-CL", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  }).format(date);
}

export function RatWorkspace({ organizaciones }: { organizaciones: OrganizationMembershipOut[] }) {
  const [orgId, setOrgId] = useState(organizaciones[0].id);
  const [tratamientos, setTratamientos] = useState<TreatmentSummaryOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [errorStatus, setErrorStatus] = useState<number | null>(null);

  useEffect(() => {
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

        const data = await api.rat.treatments(session.access_token, orgId);

        if (!vigente) return;
        setTratamientos(data);
      } catch (e) {
        if (!vigente) return;

        setTratamientos([]);

        if (e instanceof ApiError) {
          setErrorStatus(e.status);
          setError(e.message);
        } else {
          setError(
            e instanceof Error ? e.message : "No se pudo cargar el inventario de tratamientos."
          );
        }
      } finally {
        if (vigente) setLoading(false);
      }
    })();

    return () => {
      vigente = false;
    };
  }, [orgId]);

  return (
    <div className="space-y-6">
      {organizaciones.length > 1 && (
        <label className="block text-sm text-gray-700">
          Organización:{" "}
          <select
            value={orgId}
            onChange={(e) => setOrgId(e.target.value)}
            className="ml-2 rounded-lg border border-gray-300 px-2 py-1 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            {organizaciones.map((org) => (
              <option key={org.id} value={org.id}>
                {org.name}
              </option>
            ))}
          </select>
        </label>
      )}

      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Inventario de tratamientos</h1>
          <p className="mt-1 max-w-2xl text-sm text-gray-500">
            Registra y mantén las actividades en que tu organización trata datos personales.
          </p>
        </div>

        <Link
          href={`/dashboard/rat/nuevo?organizationId=${encodeURIComponent(orgId)}`}
          className="inline-flex items-center justify-center rounded-lg bg-blue-700 px-4 py-2 text-sm font-medium text-white hover:bg-blue-800"
        >
          Nueva actividad
        </Link>
      </div>

      {loading && (
        <div className="rounded-xl border border-gray-200 bg-white px-5 py-8 text-sm text-gray-500">
          Cargando actividades de tratamiento…
        </div>
      )}

      {!loading && errorStatus === 402 && (
        <div className="rounded-xl border border-amber-200 bg-amber-50 px-5 py-4">
          <h2 className="font-semibold text-amber-900">Inventario no disponible</h2>
          <p className="mt-1 text-sm text-amber-800">
            Tu suscripción no permite actualmente acceder al Inventario de Tratamientos. Revisa el
            estado de tu plan para continuar.
          </p>
        </div>
      )}

      {!loading && errorStatus === 403 && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-5 py-4">
          <h2 className="font-semibold text-red-900">Sin acceso</h2>
          <p className="mt-1 text-sm text-red-700">
            No tienes permisos para acceder al inventario de esta organización.
          </p>
        </div>
      )}

      {!loading && error && errorStatus !== 402 && errorStatus !== 403 && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {!loading && !error && tratamientos.length === 0 && (
        <div className="rounded-xl border border-dashed border-gray-300 bg-white px-6 py-12 text-center">
          <h2 className="font-semibold text-gray-900">Aún no hay actividades registradas</h2>
          <p className="mx-auto mt-2 max-w-xl text-sm text-gray-500">
            Crea tu primera actividad de tratamiento para comenzar a construir el inventario de
            datos personales de la organización.
          </p>
          <Link
            href={`/dashboard/rat/nuevo?organizationId=${encodeURIComponent(orgId)}`}
            className="mt-5 inline-flex rounded-lg bg-blue-700 px-4 py-2 text-sm font-medium text-white hover:bg-blue-800"
          >
            Crear primera actividad
          </Link>
        </div>
      )}

      {!loading && !error && tratamientos.length > 0 && (
        <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500">
                    Actividad
                  </th>
                  <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500">
                    Área
                  </th>
                  <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500">
                    Estado
                  </th>
                  <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500">
                    Actualización
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {tratamientos.map((tratamiento) => (
                  <tr key={tratamiento.id} className="hover:bg-gray-50">
                    <td className="px-5 py-4">
                      <Link
                        href={`/dashboard/rat/${tratamiento.id}?organizationId=${encodeURIComponent(orgId)}`}
                        className="font-medium text-blue-700 hover:underline"
                      >
                        {tratamiento.name}
                      </Link>
                    </td>
                    <td className="px-5 py-4 text-sm text-gray-600">
                      {tratamiento.business_area || "—"}
                    </td>
                    <td className="px-5 py-4">
                      <span
                        className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${statusClasses(
                          tratamiento.status
                        )}`}
                      >
                        {statusLabel(tratamiento.status)}
                      </span>
                    </td>
                    <td className="px-5 py-4 text-sm text-gray-500">
                      {formatDate(tratamiento.updated_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
