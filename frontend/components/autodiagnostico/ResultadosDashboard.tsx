"use client";

import { useState } from "react";
import { createClient } from "@/lib/supabase/client";
import { api, type DiagnosticoActualOut, type OrganizationMembershipOut } from "@/lib/api/client";

const RIESGO_ESTILO: Record<string, string> = {
  Alto: "border-red-200 bg-red-50 text-red-700",
  Medio: "border-amber-200 bg-amber-50 text-amber-700",
  Bajo: "border-green-200 bg-green-50 text-green-700",
};

// "pequeña"/"mediana" llevan la sigla PYME (pedido explícito del usuario);
// "micro"/"grande" no. Mismo criterio que
// app/services/diagnostico_exportacion.py::_TAMANOS_PYME en el backend.
const TAMANOS_PYME = new Set(["pequeña", "mediana"]);

async function obtenerTokenVigente(): Promise<string> {
  const supabase = createClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();
  if (!session) {
    throw new Error("Tu sesión expiró. Vuelve a iniciar sesión.");
  }
  return session.access_token;
}

export function ResultadosDashboard({
  actual,
  organizationId,
  organizacion,
  onEditar,
  onActualizar,
}: {
  actual: DiagnosticoActualOut;
  organizationId: string;
  organizacion: OrganizationMembershipOut | null;
  onEditar: () => void;
  onActualizar: (actual: DiagnosticoActualOut) => void;
}) {
  const [generando, setGenerando] = useState(false);
  const [descargando, setDescargando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const narrativaPorHallazgo = Object.fromEntries(
    (actual.informe?.narrativas ?? []).map((n) => [n.finding_id, n])
  );

  async function handleGenerarInforme() {
    setGenerando(true);
    setError(null);
    try {
      const token = await obtenerTokenVigente();
      const nuevo = await api.diagnostico.generarInforme(token, organizationId);
      onActualizar(nuevo);
    } catch (e) {
      setError(e instanceof Error ? e.message : "No se pudo generar el informe.");
    } finally {
      setGenerando(false);
    }
  }

  async function handleDescargar() {
    setDescargando(true);
    setError(null);
    try {
      const token = await obtenerTokenVigente();
      const blob = await api.diagnostico.exportarInforme(token, organizationId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `informe-autodiagnostico-${actual.id}.html`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      setError(e instanceof Error ? e.message : "No se pudo descargar el informe.");
    } finally {
      setDescargando(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Resultado del autodiagnóstico</h1>
          <p className="mt-1 text-sm text-gray-500">
            Puntaje de cumplimiento de la Ley N.° 21.719 según el catálogo CCS.
          </p>
        </div>
        <button
          type="button"
          onClick={onEditar}
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
        >
          Editar respuestas
        </button>
      </div>

      {organizacion?.size && TAMANOS_PYME.has(organizacion.size) && (
        <div className="rounded-lg border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-900">
          <strong>¿Sabías que...?</strong> Como empresa PYME, CumpleIA puede asesorarte en la
          implementación de tu programa de cumplimiento de la Ley N.° 21.719 — desde la definición
          de políticas hasta la designación de un Delegado de Protección de Datos.
        </div>
      )}

      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <p className="text-sm text-gray-500">Puntaje global</p>
        <p className="text-4xl font-bold text-blue-800">
          {actual.global_score !== null ? Math.round(actual.global_score) : "s/i"}
          <span className="text-lg font-normal text-gray-400"> / 100</span>
        </p>
      </div>

      <div className="overflow-hidden rounded-xl border border-gray-200 bg-white">
        <table className="min-w-full divide-y divide-gray-200 text-sm">
          <thead className="bg-gray-50 text-left text-xs font-medium uppercase text-gray-500">
            <tr>
              <th className="px-4 py-3">Sección</th>
              <th className="px-4 py-3 text-right">Puntaje</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {actual.puntaje_por_seccion.map((s) => (
              <tr key={s.seccion_id}>
                <td className="px-4 py-3 text-gray-900">
                  {s.numero_romano}. {s.nombre}
                </td>
                <td className="px-4 py-3 text-right font-medium text-gray-900">
                  {s.score !== null ? Math.round(s.score) : "s/i"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div>
        <h2 className="text-lg font-semibold text-gray-900">
          Hallazgos ({actual.hallazgos.filter((h) => h.status !== "cerrado").length} abiertos)
        </h2>
        <div className="mt-3 space-y-3">
          {actual.hallazgos.length === 0 && (
            <p className="text-sm text-gray-500">El diagnóstico no registra hallazgos.</p>
          )}
          {actual.hallazgos.map((h) => {
            const narrativa = narrativaPorHallazgo[h.id];
            return (
              <div
                key={h.id}
                className={`rounded-xl border p-4 ${
                  h.status === "cerrado"
                    ? "border-gray-200 bg-gray-50 opacity-60"
                    : "border-gray-200 bg-white"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span
                    className={`inline-block rounded-full border px-2 py-0.5 text-xs font-medium ${
                      RIESGO_ESTILO[h.risk] ?? "border-gray-200 bg-gray-50 text-gray-700"
                    }`}
                  >
                    Riesgo {h.risk}
                    {h.answer === "Parcial" && h.risk_base && h.risk_base !== h.risk && (
                      <> — base {h.risk_base}</>
                    )}
                  </span>
                  <span className="text-xs font-medium uppercase text-gray-400">{h.status}</span>
                </div>
                <p className="mt-2 text-sm text-gray-900">{h.description}</p>
                {h.answer && (
                  <p className="mt-1 text-xs text-gray-500">
                    Respuesta: <span className="font-medium">{h.answer}</span>
                  </p>
                )}
                {narrativa && <p className="mt-2 text-sm text-gray-600">{narrativa.narrativa}</p>}
              </div>
            );
          })}
        </div>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <h2 className="text-lg font-semibold text-gray-900">Informe</h2>

        {!actual.informe ? (
          <div className="mt-3">
            <p className="text-sm text-gray-500">
              Todavía no se ha generado el informe narrativo de este diagnóstico.
            </p>
            <button
              type="button"
              onClick={handleGenerarInforme}
              disabled={generando}
              className="mt-3 rounded-lg bg-blue-700 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {generando ? "Generando…" : "Generar informe con IA"}
            </button>
          </div>
        ) : (
          <div className="mt-3 space-y-4">
            <p className="text-xs text-gray-400">
              Generado el{" "}
              {new Date(actual.informe.generado_en).toLocaleString("es-CL", {
                timeZone: "America/Santiago",
                dateStyle: "short",
                timeStyle: "short",
              })}
            </p>
            <p className="whitespace-pre-line text-sm text-gray-700">
              {actual.informe.resumen_ejecutivo}
            </p>

            {/* Trade-off freemium: el detalle de respuestas queda reservado
                a la Carpeta de Evidencia (Módulo 5, de pago) en vez de
                incluirse gratis en este informe — ver docs/backlog.md. */}
            <div className="rounded-lg border border-violet-200 bg-violet-50 px-4 py-3 text-sm text-violet-800">
              <span className="font-medium">Anexo de respuestas</span> — disponible en la Carpeta de
              Evidencia{" "}
              <span className="ml-1 inline-block rounded-full bg-violet-100 px-2 py-0.5 text-xs font-medium text-violet-700">
                Próximamente
              </span>
              <p className="mt-1 text-xs text-violet-700">
                El detalle completo de las {actual.respuestas.length} respuestas quedará disponible
                como parte de la bitácora de evidencia, junto con el resto del expediente de
                cumplimiento.
              </p>
            </div>

            <div className="flex flex-wrap gap-3">
              <button
                type="button"
                onClick={handleDescargar}
                disabled={descargando}
                className="rounded-lg bg-blue-700 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {descargando ? "Descargando…" : "Descargar informe (HTML)"}
              </button>
              <button
                type="button"
                onClick={handleGenerarInforme}
                disabled={generando}
                title="Vuelve a generar el informe con IA — usa las respuestas y puntajes actuales"
                className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {generando ? "Regenerando…" : "Regenerar informe"}
              </button>
            </div>
          </div>
        )}
      </div>

      {error && <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}
    </div>
  );
}
