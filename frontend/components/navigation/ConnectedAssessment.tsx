"use client";
import { assessmentUnits, type WorkUnit } from "./work-units";
import type { WorkState } from "./work-unit-state";
import { useCallback, useEffect, useState } from "react";
import { AssessmentFlow, type AssessmentLocation } from "@/components/licitud/AssessmentFlow";
import type { Applicability } from "@/lib/api/navigation";
import {
  ConnectedApplicability,
  determinationLabels,
  type ApplicabilityLoadState,
} from "./ConnectedApplicability";
import { SessionRecovery } from "./SessionRecovery";
import type { WorkLocation } from "./connected-navigation";
import type { AvailabilityReadState } from "./connected-availability";
import { connectedDestinations } from "./connected-destinations";
export function ConnectedAssessment({
  location,
  name,
  readOnly,
  go,
  onScope,
  onAvailability,
  onPending,
  onWorkUnit,
  active,
  availabilityRefresh = 0,
}: {
  active: boolean;
  availabilityRefresh?: number;
  location: WorkLocation;
  name: string;
  readOnly: boolean;
  go: (v: WorkLocation, replace?: boolean) => void;
  onScope: (key: string, v: Applicability) => void;
  onAvailability: (key: string, v: AvailabilityReadState) => void;
  onPending: (key: string, dirty: boolean) => void;
  onWorkUnit: (unit: WorkUnit) => void;
}) {
  const [refreshVersion, setRefreshVersion] = useState(0);
  const refresh = useCallback(() => setRefreshVersion((n) => n + 1), []);
  const [loadState, setLoadState] = useState<ApplicabilityLoadState>({ loading: true, error: "" });
  const [relocation, setRelocation] = useState<{ signature: string; text: string } | null>(null);
  const [loadedAvailability, setLoadedAvailability] = useState(-1);
  const awaitingAvailability = loadedAvailability !== availabilityRefresh;
  const [saved, setSaved] = useState<Applicability | null>(null);
  const signature = saved ? `${saved.context_hash}:${saved.revision}:${saved.current}` : "";
  const [appDirty, setAppDirty] = useState(false);
  const [flowDirty, setFlowDirty] = useState(false);
  const key = `${location.organizationId}:${location.treatmentId}:${location.assessmentId}`;
  const reportUnit = useCallback(
    (kind: string, state: WorkState) => {
      const unit = assessmentUnits[kind];
      if (!unit) return;
      onWorkUnit({
        id: `${key}:${kind}`,
        label: unit.label,
        location: { ...location, module: "licitud", section: unit.section, step: unit.step ?? 0 },
        origin: unit.temporary ? "temporary" : "form",
        state,
      });
    },
    [key, location, onWorkUnit]
  );
  const applicabilityState = useCallback(
    (state: WorkState) => reportUnit("aplicabilidad", state),
    [reportUnit]
  );
  const scope = {
    eipd: !!saved?.current && saved.eipd.state === "corresponde",
    infancia: !!saved?.current && saved.infancia.state === "corresponde",
  };
  const loaded = useCallback(
    (v: Applicability) => {
      setLoadedAvailability(availabilityRefresh);
      setSaved(v);
      onScope(key, v);
    },
    [key, onScope, availabilityRefresh]
  );
  useEffect(() => {
    onAvailability(key, loadState);
  }, [key, loadState, onAvailability]);
  useEffect(() => {
    onPending(key, appDirty || flowDirty);
  }, [key, appDirty, flowDirty, onPending]);
  useEffect(() => {
    if (!saved || !active || awaitingAvailability || loadState.loading || loadState.error) return;
    if (
      (location.section === "eipd" && !scope.eipd) ||
      (["infancia", "preparar"].includes(location.section) && !scope.infancia)
    ) {
      const topic = location.section === "eipd" ? "EIPD" : "infancia y adolescencia";
      const determination = location.section === "eipd" ? saved.eipd : saved.infancia;
      setRelocation({
        signature,
        text:
          saved.revision === 0
            ? "Volviste a Determinar aplicabilidad porque todavía no hay una determinación guardada para esta evaluación. Su formulario no está habilitado."
            : saved.current
              ? `Volviste a Determinar aplicabilidad porque ${topic} figura como «${determinationLabels[determination.state]}» en la determinación guardada. Su formulario no está habilitado.`
              : `Volviste a Determinar aplicabilidad porque la determinación guardada de ${topic} requiere revisión para el alcance asociado a esta evaluación.`,
      });
      go({ ...location, section: "aplicabilidad", step: 0 }, true);
    } else if (location.section !== "aplicabilidad") {
      setRelocation(null);
    }
  }, [
    active,
    saved,
    signature,
    loadState,
    scope.eipd,
    scope.infancia,
    location,
    go,
    awaitingAvailability,
  ]);
  const section = location.section;
  const conditional = ["eipd", "infancia", "preparar"].includes(section);
  const flow: AssessmentLocation = {
    tab:
      section === "revisar"
        ? "revisar"
        : section === "historial"
          ? "historial"
          : section === "resumen"
            ? "resumen"
            : "completar",
    section: ["base", "infancia", "preparar", "eipd", "anexos"].includes(section)
      ? (section as AssessmentLocation["section"])
      : "alcance",
    step: location.step,
  };
  return (
    <div className="space-y-5">
      {section === "aplicabilidad" && relocation?.signature === signature && (
        <section
          aria-label="Cambio de sección"
          className="space-y-3 rounded border border-amber-400 bg-amber-50 p-4"
        >
          <p role="status">{relocation.text}</p>
          <p>
            {appDirty || flowDirty ? "Hay cambios sin guardar en esta evaluación. " : ""}Los
            borradores abiertos se conservan durante esta visita.
          </p>
          <p>Los documentos anteriores, si existen, siguen disponibles para consulta.</p>
          <button
            type="button"
            className="rounded border p-3"
            onClick={() => go({ ...location, section: "revisar", step: 0 })}
          >
            Ir a {connectedDestinations.licitud.revisar}
          </button>
          <button type="button" className="rounded border p-3" onClick={() => setRelocation(null)}>
            Cerrar aviso
          </button>
        </section>
      )}
      {section !== "aplicabilidad" &&
        (loadState.loading || (awaitingAvailability && !loadState.error)) && (
          <p role="status" className="rounded border bg-blue-50 p-4">
            Cargando evaluación y aplicabilidad… Los borradores de esta visita se conservan.
          </p>
        )}
      {section !== "aplicabilidad" && loadState.error && (
        <section className="space-y-3 rounded border border-red-200 bg-red-50 p-4">
          <p role="alert">No se pudo consultar la aplicabilidad. {loadState.error}</p>
          <SessionRecovery required={loadState.authRequired} />
          <p>
            Los borradores de esta visita se conservan. Reintentar no guarda ni descarta cambios.
          </p>
          <button className="rounded border p-3" onClick={refresh}>
            Reintentar consulta
          </button>
          <button
            className="rounded border p-3"
            onClick={() => go({ ...location, section: "aplicabilidad", step: 0 })}
          >
            Ir a Determinar aplicabilidad
          </button>
        </section>
      )}
      <div hidden={section !== "aplicabilidad"}>
        <ConnectedApplicability
          organizationId={location.organizationId}
          treatmentId={location.treatmentId}
          assessmentId={location.assessmentId}
          readOnly={readOnly}
          refreshVersion={refreshVersion + availabilityRefresh}
          onSaved={loaded}
          onDirty={setAppDirty}
          onWorkState={applicabilityState}
          onLoadState={setLoadState}
          onOpen={(section) => go({ ...location, section, step: 0 })}
        />
      </div>
      <div
        hidden={
          section === "aplicabilidad" ||
          (conditional && (awaitingAvailability || loadState.loading || !!loadState.error)) ||
          (section === "eipd" && !scope.eipd) ||
          (["infancia", "preparar"].includes(section) && !scope.infancia)
        }
      >
        <AssessmentFlow
          organizationId={location.organizationId}
          organizationName={name}
          treatmentId={location.treatmentId}
          assessmentId={location.assessmentId}
          readOnly={readOnly}
          onPending={setFlowDirty}
          onWorkUnit={reportUnit}
          onAssessmentSaved={refresh}
          navigation={{
            scope,
            location: flow,
            labels: connectedDestinations.licitud,
            go: (v) =>
              go({ ...location, section: v.tab === "completar" ? v.section : v.tab, step: v.step }),
          }}
        />
      </div>
    </div>
  );
}
