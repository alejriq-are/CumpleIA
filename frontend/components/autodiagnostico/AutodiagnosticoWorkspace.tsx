"use client";

import { useEffect, useState } from "react";
import { createClient } from "@/lib/supabase/client";
import {
  api,
  type CuestionarioOut,
  type DiagnosticoActualOut,
  type OrganizationMembershipOut,
} from "@/lib/api/client";
import { Cuestionario } from "./Cuestionario";
import { ResultadosDashboard } from "./ResultadosDashboard";

type Modo = "cuestionario" | "resultados";

export function AutodiagnosticoWorkspace({
  organizaciones,
}: {
  organizaciones: OrganizationMembershipOut[];
}) {
  const [orgId, setOrgId] = useState(organizaciones[0].id);
  const [cuestionario, setCuestionario] = useState<CuestionarioOut | null>(null);
  const [actual, setActual] = useState<DiagnosticoActualOut | null>(null);
  const [modo, setModo] = useState<Modo>("cuestionario");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let vigente = true;
    setLoading(true);
    setError(null);

    (async () => {
      try {
        const supabase = createClient();
        const {
          data: { session },
        } = await supabase.auth.getSession();
        if (!session) {
          throw new Error("Tu sesión expiró. Vuelve a iniciar sesión.");
        }

        const [cuestionarioData, actualData] = await Promise.all([
          api.diagnostico.cuestionario(session.access_token, orgId),
          api.diagnostico.actual(session.access_token, orgId),
        ]);

        if (!vigente) return;
        setCuestionario(cuestionarioData);
        setActual(actualData);
        setModo(actualData?.status === "completado" ? "resultados" : "cuestionario");
      } catch (e) {
        if (vigente) {
          setError(e instanceof Error ? e.message : "No se pudo cargar el autodiagnóstico.");
        }
      } finally {
        if (vigente) setLoading(false);
      }
    })();

    return () => {
      vigente = false;
    };
  }, [orgId]);

  if (loading) {
    return <p className="text-sm text-gray-500">Cargando autodiagnóstico…</p>;
  }

  if (error) {
    return <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>;
  }

  if (!cuestionario) return null;

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
            {organizaciones.map((o) => (
              <option key={o.id} value={o.id}>
                {o.name}
              </option>
            ))}
          </select>
        </label>
      )}

      {modo === "cuestionario" ? (
        <Cuestionario
          cuestionario={cuestionario}
          respuestasIniciales={actual?.respuestas ?? []}
          organizationId={orgId}
          onCompletado={(nuevo) => {
            setActual(nuevo);
            setModo("resultados");
          }}
        />
      ) : (
        actual && (
          <ResultadosDashboard
            actual={actual}
            organizationId={orgId}
            organizacion={organizaciones.find((o) => o.id === orgId) ?? null}
            onEditar={() => setModo("cuestionario")}
            onActualizar={setActual}
          />
        )
      )}
    </div>
  );
}
