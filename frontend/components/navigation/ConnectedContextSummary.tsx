"use client";
import { useCallback, useRef, useState } from "react";
import { PrototypeDrawer } from "./PrototypeDrawer";

export type SelectedEvaluation = { purpose: string; version: number; status: string };

/** Read-only context; opening it never saves or changes the selected evaluation. */
export function ConnectedContextSummary({
  organization,
  treatment,
  evaluation,
  assessmentSelected,
}: {
  organization: string;
  treatment?: string;
  evaluation?: SelectedEvaluation;
  assessmentSelected: boolean;
}) {
  const [open, setOpen] = useState(false);
  const trigger = useRef<HTMLButtonElement>(null);
  const close = useCallback(() => {
    setOpen(false);
    requestAnimationFrame(() => trigger.current?.focus({ preventScroll: true }));
  }, []);
  const evaluationLabel = evaluation
    ? `versión ${evaluation.version} · ${evaluation.status}`
    : "Evaluación seleccionada";
  return (
    <>
      <div className="connected-context-strip">
        <div data-testid="connected-context-summary" className="connected-context-brief">
          <div className="connected-context-names">
            <p className="connected-context-name">
              <span className="sr-only">Organización: </span>
              {organization}
            </p>
            {treatment && (
              <>
                <span aria-hidden="true"> · </span>
                <p className="connected-context-name">
                  <span className="sr-only">Tratamiento: </span>
                  {treatment}
                </p>
              </>
            )}
          </div>
          {assessmentSelected && (
            <p className="connected-evaluation-badge" aria-label={`Evaluación: ${evaluationLabel}`}>
              {evaluationLabel}
            </p>
          )}
        </div>
        <button
          ref={trigger}
          type="button"
          aria-haspopup="dialog"
          aria-expanded={open}
          aria-controls="connected-context-detail"
          onClick={() => setOpen(true)}
        >
          Ver contexto completo
        </button>
      </div>
      <PrototypeDrawer
        open={open}
        id="connected-context-detail"
        label="Contexto seleccionado"
        className="prototype-sections-drawer connected-context-detail"
        close={close}
      >
        <button type="button" onClick={close}>
          Cerrar detalle
        </button>
        <h2>Contexto seleccionado</h2>
        <p>
          Consulta del contexto de trabajo. Abrir este detalle no cambia la selección ni guarda el
          formulario.
        </p>
        <dl>
          <dt>Organización</dt>
          <dd>{organization}</dd>
          {treatment && (
            <>
              <dt>Tratamiento</dt>
              <dd>{treatment}</dd>
            </>
          )}
          {assessmentSelected && (
            <>
              <dt>Finalidad</dt>
              <dd>{evaluation?.purpose ?? "Pendiente de consulta"}</dd>
              <dt>Evaluación</dt>
              <dd>{evaluationLabel}</dd>
            </>
          )}
        </dl>
        {assessmentSelected && (
          <p>
            La versión indicada corresponde a la evaluación seleccionada. Los documentos históricos
            conservan su propia versión, referencia y revisiones en Documentos guardados.
          </p>
        )}
      </PrototypeDrawer>
    </>
  );
}
