"use client";
import { useCallback, useRef, useState } from "react";
import { PrototypeDrawer } from "./PrototypeDrawer";
import { workStatusLabels, type WorkUnit } from "./work-units";
export function ConnectedPendingSummary({
  units,
  describe,
}: {
  units: WorkUnit[];
  describe: (unit: WorkUnit) => string;
}) {
  const [open, setOpen] = useState(false);
  const trigger = useRef<HTMLButtonElement>(null);
  const close = useCallback(() => {
    setOpen(false);
    requestAnimationFrame(() => trigger.current?.focus());
  }, []);
  return (
    <div className="mt-2">
      <button
        ref={trigger}
        type="button"
        aria-expanded={open}
        aria-controls="connected-pending-panel"
        className="rounded border border-amber-700 px-3 py-2 font-semibold text-amber-900"
        onClick={() => setOpen(true)}
      >
        Ver pendientes ({units.length})
      </button>
      {units.length > 0 && <span className="ml-2">Guarda cada formulario antes de recargar.</span>}
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
          Los siete pasos del borrador EIPD cuentan como una unidad. Esta lista no guarda ni cambia
          el contexto. Los cambios sin guardar se conservan solo durante esta visita en esta
          pestaña.
        </p>
        {units.length === 0 ? (
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
              </li>
            ))}
          </ul>
        )}
      </PrototypeDrawer>
    </div>
  );
}
