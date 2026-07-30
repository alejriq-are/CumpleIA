"use client";

import { useMemo, useState } from "react";
import { createClient } from "@/lib/supabase/client";
import {
  api,
  type ConfigCuestionarioOut,
  type PreguntaOut,
  type RiesgoDisplay,
} from "@/lib/api/client";

const NIVELES_RIESGO: RiesgoDisplay[] = ["Alto", "Medio", "Bajo"];
const SUMA_ESPERADA = 100;

type Tab = "pesos" | "riesgos";

function formatearFecha(iso: string): string {
  return new Date(iso).toLocaleDateString("es-CL", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

export function CuestionarioConfigEditor({
  initialConfig,
}: {
  initialConfig: ConfigCuestionarioOut;
}) {
  const [data, setData] = useState(initialConfig);
  const [tab, setTab] = useState<Tab>("pesos");
  const [pesos, setPesos] = useState<Record<string, number>>(() =>
    Object.fromEntries(initialConfig.secciones.map((s) => [s.id, s.peso_pct]))
  );
  const [riesgos, setRiesgos] = useState<Record<string, RiesgoDisplay>>(() =>
    Object.fromEntries(initialConfig.preguntas.map((p) => [p.id, p.riesgo]))
  );
  const [nota, setNota] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exito, setExito] = useState<string | null>(null);

  const obligacionPorId = useMemo(
    () => Object.fromEntries(data.obligaciones.map((o) => [o.id, o])),
    [data.obligaciones]
  );

  const preguntasPorSeccion = useMemo(() => {
    const grupos: Record<string, PreguntaOut[]> = {};
    for (const p of data.preguntas) {
      (grupos[p.seccion_id] ??= []).push(p);
    }
    return grupos;
  }, [data.preguntas]);

  // Suma en vivo: recalculada en cada tecla, no solo al enviar. El botón
  // "Guardar cambios" se deshabilita mientras no sea exactamente 100, igual
  // que en el mockup — no basta con esperar el 400 del backend.
  const sumaPesos = useMemo(() => Object.values(pesos).reduce((acc, v) => acc + v, 0), [pesos]);
  const sumaOk = sumaPesos === SUMA_ESPERADA;
  const puedeGuardar = sumaOk && !saving;

  function actualizarPeso(seccionId: string, valor: number) {
    const acotado = Math.max(0, Math.min(100, Math.round(valor)));
    setPesos((prev) => ({ ...prev, [seccionId]: acotado }));
  }

  function actualizarRiesgo(preguntaId: string, valor: RiesgoDisplay) {
    setRiesgos((prev) => ({ ...prev, [preguntaId]: valor }));
  }

  async function handleGuardar() {
    if (!sumaOk) return; // defensa adicional: nunca envía si la suma no cuadra
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

      const nuevaConfig = await api.cuestionarioConfig.save(session.access_token, {
        nota: nota.trim() || undefined,
        pesos: data.secciones.map((s) => ({ seccion_id: s.id, peso_pct: pesos[s.id] })),
        riesgos: data.preguntas.map((p) => ({
          pregunta_id: p.id,
          riesgo: riesgos[p.id],
        })),
      });

      setData(nuevaConfig);
      setPesos(Object.fromEntries(nuevaConfig.secciones.map((s) => [s.id, s.peso_pct])));
      setRiesgos(Object.fromEntries(nuevaConfig.preguntas.map((p) => [p.id, p.riesgo])));
      setNota("");
      setExito(`Guardado como versión ${nuevaConfig.version.numero_version}.`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error al guardar los cambios.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Configuración del cuestionario</h1>
        <p className="mt-1 text-sm text-gray-500">
          Pesos por sección y nivel de riesgo por pregunta del autodiagnóstico (Módulo 1).
        </p>
      </div>

      {/* Banner de versión activa */}
      <div className="rounded-xl border border-gray-200 bg-white px-5 py-4 text-sm text-gray-700">
        Versión activa: <span className="font-semibold">v{data.version.numero_version}</span>
        {" · aplicada el "}
        {formatearFecha(data.version.creado_en)}
        {" · por "}
        <span className="font-medium">
          {data.version.creado_por.full_name ?? data.version.creado_por.email}
        </span>
        {data.version.nota && (
          <span className="block text-gray-500">Nota: {data.version.nota}</span>
        )}
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200">
        {(
          [
            ["pesos", "Pesos por sección"],
            ["riesgos", "Riesgo por pregunta"],
          ] as [Tab, string][]
        ).map(([value, label]) => (
          <button
            key={value}
            type="button"
            onClick={() => setTab(value)}
            className={`border-b-2 px-4 pb-3 text-sm font-medium transition-colors ${
              tab === value
                ? "border-blue-700 text-blue-700"
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === "pesos" && (
        <div className="overflow-hidden rounded-xl border border-gray-200 bg-white">
          <table className="min-w-full divide-y divide-gray-200 text-sm">
            <thead className="bg-gray-50 text-left text-xs font-medium uppercase text-gray-500">
              <tr>
                <th className="px-4 py-3">Sección</th>
                <th className="px-4 py-3">Obligación</th>
                <th className="px-4 py-3 text-right">Peso %</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {data.secciones.map((s) => (
                <tr key={s.id}>
                  <td className="px-4 py-3 text-gray-900">
                    {s.numero_romano}. {s.nombre}
                  </td>
                  <td className="px-4 py-3">
                    <span className="inline-block rounded-full bg-violet-50 px-2 py-1 text-xs font-medium text-violet-700">
                      {obligacionPorId[s.obligacion_id]?.nombre ?? s.obligacion_id}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <input
                      type="number"
                      min={0}
                      max={100}
                      step={1}
                      value={pesos[s.id]}
                      onChange={(e) => actualizarPeso(s.id, Number(e.target.value))}
                      className="w-20 rounded-lg border border-gray-300 px-2 py-1 text-right text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <div
            className={`border-t px-4 py-3 text-sm font-medium ${
              sumaOk
                ? "border-green-200 bg-green-50 text-green-700"
                : "border-red-200 bg-red-50 text-red-700"
            }`}
          >
            Suma de pesos: {sumaPesos}% {sumaOk ? "— correcto" : `(debe ser ${SUMA_ESPERADA}%)`}
          </div>
        </div>
      )}

      {tab === "riesgos" && (
        <div className="space-y-2">
          {data.secciones.map((s) => (
            <details
              key={s.id}
              className="rounded-xl border border-gray-200 bg-white px-4 py-3 open:pb-4"
            >
              <summary className="cursor-pointer select-none text-sm font-medium text-gray-900">
                {s.numero_romano}. {s.nombre}
                <span className="ml-2 text-xs font-normal text-gray-500">
                  ({(preguntasPorSeccion[s.id] ?? []).length} preguntas)
                </span>
              </summary>
              <div className="mt-3 divide-y divide-gray-100 border-t border-gray-100">
                {(preguntasPorSeccion[s.id] ?? []).map((p) => (
                  <div key={p.id} className="flex items-center justify-between gap-4 py-3 text-sm">
                    <span className="text-gray-700">{p.texto}</span>
                    <select
                      value={riesgos[p.id]}
                      onChange={(e) => actualizarRiesgo(p.id, e.target.value as RiesgoDisplay)}
                      className="shrink-0 rounded-lg border border-gray-300 px-2 py-1 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    >
                      {NIVELES_RIESGO.map((nivel) => (
                        <option key={nivel} value={nivel}>
                          {nivel}
                        </option>
                      ))}
                    </select>
                  </div>
                ))}
              </div>
            </details>
          ))}
        </div>
      )}

      {/* Acciones de guardado, comunes a ambas pantallas */}
      <div className="space-y-3 rounded-xl border border-gray-200 bg-white p-5">
        <div>
          <label htmlFor="nota" className="block text-sm font-medium text-gray-700">
            Nota de la versión (opcional)
          </label>
          <input
            id="nota"
            type="text"
            value={nota}
            onChange={(e) => setNota(e.target.value)}
            placeholder="Ej: ajuste de pesos tras revisión con Alicia"
            className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        <p className="text-xs text-gray-500">
          Los autodiagnósticos ya generados no se recalculan: cada informe conserva el snapshot de
          los pesos y riesgos vigentes al momento en que se generó.
        </p>

        {error && <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}
        {exito && (
          <p className="rounded-lg bg-green-50 px-3 py-2 text-sm text-green-700">{exito}</p>
        )}

        <button
          type="button"
          onClick={handleGuardar}
          disabled={!puedeGuardar}
          className="rounded-lg bg-blue-700 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {saving ? "Guardando…" : "Guardar cambios"}
        </button>
      </div>
    </div>
  );
}
