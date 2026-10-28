"use client";
import { useCallback, useRef, useState } from "react";
import { PrototypeDrawer } from "./PrototypeDrawer";
import { workStatusLabels, type WorkUnit } from "./work-units";
export function ConnectedPendingSummary({
  units,
  describe,
  destinationLabel,
  destinationContext,
  currentDescription,
  changesContext,
  openUnit,
  busy,
  error,
  cancelOpen,
}: {
  units: WorkUnit[];
  describe: (unit: WorkUnit) => string;
  destinationLabel: (unit: WorkUnit) => string;
  destinationContext: (unit: WorkUnit) => string;
  currentDescription: string;
  changesContext: (unit: WorkUnit) => boolean;
  openUnit: (unit: WorkUnit) => Promise<boolean>;
  busy: boolean;
  error: string;
  cancelOpen: () => void;
}) {
  const [open, setOpen] = useState(false);
  const [selected, setSelected] = useState<WorkUnit | null>(null);
  const trigger = useRef<HTMLButtonElement>(null);
  const returnUnit = useRef<string | null>(null);
  const close = useCallback(() => {
    cancelOpen();
    setOpen(false);
    setSelected(null);
    requestAnimationFrame(() => trigger.current?.focus());
  }, [cancelOpen]);
  async function navigate(unit: WorkUnit) {
    if (await openUnit(unit)) {
      setOpen(false);
      setSelected(null);
    }
  }
  function cancelSelection() {
    cancelOpen();
    setSelected(null);
    requestAnimationFrame(() => {
      if (returnUnit.current)
        document.getElementById(`pending-link-${returnUnit.current}`)?.focus();
    });
  }
  return (
    <div className="connected-pending-summary mt-2">
      <button
        ref={trigger}
        type="button"
        aria-expanded={open}
        aria-controls="connected-pending-panel"
        className="connected-pending-trigger rounded border border-amber-700 px-3 py-2 font-semibold text-amber-900"
        onClick={() => {
          cancelOpen();
          setSelected(null);
          setOpen(true);
        }}
      >
        Ver pendientes ({units.length})
      </button>
      <span className="ml-2">Guarda cada formulario antes de recargar.</span>
      <PrototypeDrawer
        open={open}
        id="connected-pending-panel"
        label="Unidades de trabajo pendientes"
        className="prototype-sections-drawer"
        close={close}
      >
        <h2 className="text-xl font-bold">Unidades de trabajo pendientes ({units.length})</h2>
        <button type="button" className="my-3 rounded border p-3" onClick={close}>
          Cerrar pendientes
        </button>
        <p className="mb-4">
          Los siete pasos del borrador EIPD cuentan como una unidad. Abrir un pendiente no guarda
          sus cambios. Se conservan solo durante esta visita en esta pestaña.
        </p>
        {busy && (
          <p role="status" className="my-3 rounded bg-blue-50 p-3">
            Validando el destino y su contexto…
          </p>
        )}
        {error && (
          <p role="alert" className="my-3 rounded bg-red-50 p-3">
            {error} Los borradores se conservan; puedes reintentar o cancelar.
          </p>
        )}
        {selected ? (
          <section
            aria-label="Confirmar destino pendiente"
            className="space-y-3 rounded border bg-blue-50 p-3 break-words"
          >
            <h3 className="font-bold">Antes de cambiar de contexto</h3>
            <p>Ahora: {currentDescription}</p>
            <p>Contexto de destino: {destinationContext(selected)}</p>
            <p>Destino: {destinationLabel(selected)}</p>
            <p>
              Abrirás {selected.label}. Los {units.length} pendientes de esta visita se conservan en
              sus formularios; no se guardan ni se copian a otra evaluación. Otras pestañas no
              cambian.
            </p>
            <button
              type="button"
              className="rounded bg-blue-800 p-3 text-white disabled:opacity-50"
              disabled={busy}
              onClick={() => void navigate(selected)}
            >
              Abrir pendiente en este contexto
            </button>
            <button type="button" className="rounded border p-3" onClick={cancelSelection}>
              Cancelar cambio
            </button>
          </section>
        ) : units.length === 0 ? (
          <p>
            No hay cambios pendientes informados. Esto no significa que todos los formularios estén
            completos o guardados en el servidor.
          </p>
        ) : (
          <ul className="space-y-4">
            {units.map((unit) => (
              <li key={unit.id} className="break-words rounded border p-3">
                <h3 className="font-bold">{unit.label}</h3>
                <p className="whitespace-normal">{describe(unit)}</p>
                <p>{workStatusLabels[unit.state.status]}</p>
                <p>
                  {unit.origin === "temporary"
                    ? "Preparación temporal: se registra mediante una nueva versión documental."
                    : "Formulario: utiliza su acción de guardado correspondiente."}
                </p>
                <p>Destino: {destinationLabel(unit)}</p>
                <button
                  id={`pending-link-${unit.id}`}
                  type="button"
                  disabled={busy}
                  className="mt-2 rounded border border-blue-700 p-3 font-semibold text-blue-900 disabled:opacity-50"
                  onClick={() => {
                    returnUnit.current = unit.id;
                    if (changesContext(unit)) {
                      cancelOpen();
                      setSelected(unit);
                    } else void navigate(unit);
                  }}
                >
                  Ir a {unit.label}
                </button>
              </li>
            ))}
          </ul>
        )}
      </PrototypeDrawer>
    </div>
  );
}
