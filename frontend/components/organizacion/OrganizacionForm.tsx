"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { createClient } from "@/lib/supabase/client";
import { api, type OrganizationMembershipOut } from "@/lib/api/client";

// "pequeña"/"mediana" llevan la sigla "(PYME)" a pedido explícito del
// usuario; "micro"/"grande" no (no es la clasificación MIPYME formal
// chilena, que sí incluye a la micro empresa).
const TAMANOS = [
  { value: "micro", label: "Micro empresa" },
  { value: "pequeña", label: "Pequeña empresa (PYME)" },
  { value: "mediana", label: "Mediana empresa (PYME)" },
  { value: "grande", label: "Gran Empresa" },
];

// Asume una sola organización por usuario, igual que AutodiagnosticoWorkspace
// (no existe todavía un selector/contexto global de organización activa).
export function OrganizacionForm({
  organizacion,
}: {
  organizacion: OrganizationMembershipOut | null;
}) {
  const router = useRouter();
  const [name, setName] = useState(organizacion?.name ?? "");
  const [rut, setRut] = useState(organizacion?.rut ?? "");
  const [industry, setIndustry] = useState(organizacion?.industry ?? "");
  const [size, setSize] = useState(organizacion?.size ?? "");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exito, setExito] = useState<string | null>(null);

  async function handleGuardar() {
    if (!name.trim()) {
      setError("El nombre de la organización es obligatorio.");
      return;
    }
    setSaving(true);
    setError(null);
    setExito(null);

    try {
      const supabase = createClient();
      const {
        data: { session },
      } = await supabase.auth.getSession();
      if (!session) {
        throw new Error("Tu sesión expiró. Vuelve a iniciar sesión.");
      }

      const body = {
        name: name.trim(),
        rut: rut.trim() || undefined,
        industry: industry.trim() || undefined,
        size: size.trim() || undefined,
      };

      if (organizacion) {
        await api.organizations.update(session.access_token, organizacion.id, body);
        setExito("Datos actualizados.");
      } else {
        await api.organizations.create(session.access_token, body);
        setExito("Organización creada.");
      }
      router.refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "No se pudieron guardar los cambios.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="max-w-xl space-y-4 rounded-xl border border-gray-200 bg-white p-6">
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700">
          Nombre de la organización
        </label>
        <input
          id="name"
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Ej: Comercial Los Alerces SpA"
          className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>

      <div>
        <label htmlFor="rut" className="block text-sm font-medium text-gray-700">
          RUT
        </label>
        <input
          id="rut"
          type="text"
          value={rut}
          onChange={(e) => setRut(e.target.value)}
          placeholder="76.111.222-3"
          className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>

      <div>
        <label htmlFor="industry" className="block text-sm font-medium text-gray-700">
          Rubro / industria
        </label>
        <input
          id="industry"
          type="text"
          value={industry}
          onChange={(e) => setIndustry(e.target.value)}
          placeholder="Ej: Comercio, Salud, Servicios profesionales"
          className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>

      <div>
        <label htmlFor="size" className="block text-sm font-medium text-gray-700">
          Tamaño
        </label>
        <select
          id="size"
          value={size}
          onChange={(e) => setSize(e.target.value)}
          className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          <option value="">Sin especificar</option>
          {TAMANOS.map((t) => (
            <option key={t.value} value={t.value}>
              {t.label}
            </option>
          ))}
        </select>
      </div>

      {error && <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}
      {exito && <p className="rounded-lg bg-green-50 px-3 py-2 text-sm text-green-700">{exito}</p>}

      <button
        type="button"
        onClick={handleGuardar}
        disabled={saving}
        className="rounded-lg bg-blue-700 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {saving ? "Guardando…" : organizacion ? "Guardar cambios" : "Crear organización"}
      </button>
    </div>
  );
}
