"use client";

import { useMemo, useState } from "react";
import { createClient } from "@/lib/supabase/client";
import {
  api,
  type CuestionarioOut,
  type DiagnosticoActualOut,
  type OpcionRespuesta,
  type RespuestaIn,
} from "@/lib/api/client";

const OPCIONES: OpcionRespuesta[] = ["Sí", "Parcial", "No", "N/A"];

type RespuestaState = { answer: OpcionRespuesta | null; notes: string };

export function Cuestionario({
  cuestionario,
  respuestasIniciales,
  organizationId,
  onCompletado,
}: {
  cuestionario: CuestionarioOut;
  respuestasIniciales: DiagnosticoActualOut["respuestas"];
  organizationId: string;
  onCompletado: (actual: DiagnosticoActualOut) => void;
}) {
  const secciones = useMemo(
    () => [...cuestionario.secciones].sort((a, b) => a.orden - b.orden),
    [cuestionario.secciones]
  );

  const preguntasPorSeccion = useMemo(() => {
    const grupos: Record<string, CuestionarioOut["preguntas"]> = {};
    for (const p of cuestionario.preguntas) {
      (grupos[p.seccion_id] ??= []).push(p);
    }
    for (const lista of Object.values(grupos)) {
      lista.sort((a, b) => a.orden - b.orden);
    }
    return grupos;
  }, [cuestionario.preguntas]);

  const [respuestas, setRespuestas] = useState<Record<string, RespuestaState>>(() =>
    Object.fromEntries(
      respuestasIniciales
        .filter((r) => r.answer !== null)
        .map((r) => [r.pregunta_id, { answer: r.answer as OpcionRespuesta, notes: r.notes ?? "" }])
    )
  );
  const [paso, setPaso] = useState(0);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const seccionActual = secciones[paso];
  const preguntasSeccion = preguntasPorSeccion[seccionActual.id] ?? [];
  const totalPreguntas = cuestionario.preguntas.length;
  const totalRespondidas = Object.values(respuestas).filter((r) => r.answer !== null).length;
  const seccionCompleta = preguntasSeccion.every((p) => respuestas[p.id]?.answer);
  const esUltimaSeccion = paso === secciones.length - 1;

  function actualizarRespuesta(preguntaId: string, cambios: Partial<RespuestaState>) {
    setRespuestas((prev) => {
      const base: RespuestaState = prev[preguntaId] ?? { answer: null, notes: "" };
      return { ...prev, [preguntaId]: { ...base, ...cambios } };
    });
  }

  async function guardarSeccionActual(): Promise<DiagnosticoActualOut> {
    const supabase = createClient();
    const {
      data: { session },
    } = await supabase.auth.getSession();
    if (!session) {
      throw new Error("Tu sesión expiró. Vuelve a iniciar sesión.");
    }

    const payload: RespuestaIn[] = preguntasSeccion.map((p) => ({
      pregunta_id: p.id,
      answer: respuestas[p.id].answer as OpcionRespuesta,
      notes: respuestas[p.id].notes.trim() || undefined,
    }));

    return api.diagnostico.guardarRespuestas(session.access_token, organizationId, payload);
  }

  async function handleSiguiente() {
    if (!seccionCompleta || saving) return;
    setSaving(true);
    setError(null);
    try {
      const actual = await guardarSeccionActual();
      if (esUltimaSeccion) {
        onCompletado(actual);
      } else {
        setPaso((p) => p + 1);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "No se pudo guardar la sección.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center justify-between text-sm text-gray-500">
          <span>
            Sección {paso + 1} de {secciones.length}: {seccionActual.numero_romano}.{" "}
            {seccionActual.nombre}
          </span>
          <span>
            {totalRespondidas} / {totalPreguntas} preguntas respondidas
          </span>
        </div>
        <div className="mt-2 h-2 overflow-hidden rounded-full bg-gray-200">
          <div
            className="h-full bg-blue-700 transition-all"
            style={{ width: `${(totalRespondidas / totalPreguntas) * 100}%` }}
          />
        </div>
      </div>

      <div className="space-y-4 rounded-xl border border-gray-200 bg-white p-6">
        {preguntasSeccion.map((p) => (
          <div key={p.id} className="border-b border-gray-100 pb-4 last:border-0 last:pb-0">
            <p className="text-sm font-medium text-gray-900">{p.texto}</p>
            <div className="mt-2 flex flex-wrap gap-2">
              {OPCIONES.map((op) => (
                <button
                  key={op}
                  type="button"
                  onClick={() => actualizarRespuesta(p.id, { answer: op })}
                  className={`rounded-lg border px-3 py-1.5 text-sm font-medium transition-colors ${
                    respuestas[p.id]?.answer === op
                      ? "border-blue-700 bg-blue-700 text-white"
                      : "border-gray-300 text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  {op}
                </button>
              ))}
            </div>
            <input
              type="text"
              value={respuestas[p.id]?.notes ?? ""}
              onChange={(e) => actualizarRespuesta(p.id, { notes: e.target.value })}
              placeholder="Notas u observaciones (opcional)"
              className="mt-2 block w-full rounded-lg border border-gray-300 px-3 py-1.5 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
        ))}
      </div>

      {error && <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}

      <div className="flex justify-between">
        <button
          type="button"
          onClick={() => setPaso((p) => p - 1)}
          disabled={paso === 0 || saving}
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Anterior
        </button>
        <button
          type="button"
          onClick={handleSiguiente}
          disabled={!seccionCompleta || saving}
          className="rounded-lg bg-blue-700 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {saving ? "Guardando…" : esUltimaSeccion ? "Finalizar" : "Siguiente"}
        </button>
      </div>
    </div>
  );
}
