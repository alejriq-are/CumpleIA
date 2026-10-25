"use client";
import { useCallback, useEffect, useState } from "react";
import { AssessmentFlow, type AssessmentLocation } from "@/components/licitud/AssessmentFlow";
import type { Applicability } from "@/lib/api/navigation";
import { ConnectedApplicability } from "./ConnectedApplicability";
import type { WorkLocation } from "./connected-navigation";
export function ConnectedAssessment({
  location,
  name,
  readOnly,
  go,
  onScope,
  onPending,
  active,
}: {
  active: boolean;
  location: WorkLocation;
  name: string;
  readOnly: boolean;
  go: (v: WorkLocation, replace?: boolean) => void;
  onScope: (key: string, v: Applicability) => void;
  onPending: (key: string, dirty: boolean) => void;
}) {
  const [refreshVersion, setRefreshVersion] = useState(0);
  const refresh = useCallback(() => setRefreshVersion((n) => n + 1), []);
  const [saved, setSaved] = useState<Applicability | null>(null);
  const [appDirty, setAppDirty] = useState(false);
  const [flowDirty, setFlowDirty] = useState(false);
  const key = `${location.organizationId}:${location.treatmentId}:${location.assessmentId}`;
  const scope = {
    eipd: !!saved?.current && saved.eipd.state === "corresponde",
    infancia: !!saved?.current && saved.infancia.state === "corresponde",
  };
  const loaded = useCallback(
    (v: Applicability) => {
      setSaved(v);
      onScope(key, v);
    },
    [key, onScope]
  );
  useEffect(() => {
    onPending(key, appDirty || flowDirty);
  }, [key, appDirty, flowDirty, onPending]);
  useEffect(() => {
    if (!saved || !active) return;
    if (
      (location.section === "eipd" && !scope.eipd) ||
      (["infancia", "preparar"].includes(location.section) && !scope.infancia)
    )
      go({ ...location, section: "aplicabilidad", step: 0 }, true);
  }, [active, saved, scope.eipd, scope.infancia, location, go]);
  const section = location.section;
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
      <div hidden={section !== "aplicabilidad"}>
        <ConnectedApplicability
          organizationId={location.organizationId}
          treatmentId={location.treatmentId}
          assessmentId={location.assessmentId}
          readOnly={readOnly}
          refreshVersion={refreshVersion}
          onSaved={loaded}
          onDirty={setAppDirty}
        />
      </div>
      <div
        hidden={
          section === "aplicabilidad" ||
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
          onAssessmentSaved={refresh}
          navigation={{
            scope,
            location: flow,
            go: (v) =>
              go({ ...location, section: v.tab === "completar" ? v.section : v.tab, step: v.step }),
          }}
        />
      </div>
    </div>
  );
}
