"use client";
import { useState } from "react";
import {
  evaluationOptions,
  purposeOptions,
  treatmentOptions,
  type EvaluationId,
  type Scenario,
} from "./prototype-data";
export function PrototypeContext({
  id,
  organization,
  pending,
  apply,
  cancel,
}: {
  id: EvaluationId;
  organization: string;
  pending: (id: EvaluationId) => boolean;
  apply: (id: EvaluationId) => void;
  cancel: () => void;
}) {
  const [selected, setSelected] = useState(id);
  const evaluation = evaluationOptions.find((item) => item.id === selected)!;
  const purpose = purposeOptions.find((item) => item.id === evaluation.purposeId)!;
  const input = "mt-2 block w-full rounded-lg border border-slate-300 bg-white p-3";
  return (
    <div className="space-y-4">
      <p className="font-semibold">Organización: {organization}</p>
      <p>
        Cada evaluación conserva sus propios borradores y guardados. Cambiar de contexto no copia
        respuestas ni decisiones.
      </p>
      {pending(id) && (
        <p className="rounded-lg bg-amber-50 p-3">
          La evaluación actual tiene cambios pendientes. Se conservarán al cambiar.
        </p>
      )}
      <label className="block font-semibold">
        Tratamiento del <abbr title="Registro de Actividades de Tratamiento">RAT</abbr>
        <select
          aria-label="Tratamiento del RAT"
          className={input}
          value={evaluation.treatment}
          onChange={(event) =>
            setSelected(
              evaluationOptions.find((item) => item.treatment === (event.target.value as Scenario))!
                .id
            )
          }
        >
          {treatmentOptions.map((item) => (
            <option key={item.id} value={item.id}>
              {item.label.replace("[FICTICIA] ", "")}
            </option>
          ))}
        </select>
      </label>
      <label className="block font-semibold">
        Finalidad de la evaluación
        <select
          aria-label="Finalidad de la evaluación"
          className={input}
          value={evaluation.purposeId}
          onChange={(event) =>
            setSelected(
              evaluationOptions.find(
                (item) =>
                  item.treatment === evaluation.treatment && item.purposeId === event.target.value
              )!.id
            )
          }
        >
          {purposeOptions
            .filter((item) => item.treatment === evaluation.treatment)
            .map((item) => (
              <option key={item.id} value={item.id}>
                {item.id === "citas"
                  ? "Coordinación de citas"
                  : item.id === "comercial"
                    ? "Seguimiento comercial"
                    : "Programa con menores"}
              </option>
            ))}
        </select>
      </label>
      <p className="text-sm text-slate-600">Finalidad completa: {purpose.label}</p>
      <label className="block font-semibold">
        Evaluación
        <select
          aria-label="Evaluación"
          className={input}
          value={selected}
          onChange={(event) => setSelected(event.target.value as EvaluationId)}
        >
          {evaluationOptions
            .filter(
              (item) =>
                item.treatment === evaluation.treatment && item.purposeId === evaluation.purposeId
            )
            .map((item) => (
              <option key={item.id} value={item.id}>
                Versión {item.version} · Borrador
                {pending(item.id) ? " · Cambios pendientes" : ""}
              </option>
            ))}
        </select>
      </label>
      <p className="text-sm text-slate-600">Evaluación seleccionada: {evaluation.label}</p>
      <div className="flex flex-wrap gap-3 border-t border-slate-200 pt-4">
        <button
          className="rounded-lg bg-blue-800 px-4 py-3 font-semibold text-white"
          onClick={() => apply(selected)}
        >
          Usar esta evaluación
        </button>
        <button
          className="rounded-lg border border-slate-300 px-4 py-3 font-semibold"
          onClick={cancel}
        >
          Cancelar
        </button>
      </div>
    </div>
  );
}
