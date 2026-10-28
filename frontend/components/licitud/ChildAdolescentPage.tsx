"use client";
import type { WorkReporter } from "@/components/navigation/work-unit-state";
import { preparePilot, type PilotForm } from "@/lib/api/pilot-preparation";
import type { Dossier } from "@/lib/api/mvp-dossier";
import { MvpDossierPanel } from "./MvpDossierPanel";
import { loadMvpDossier } from "@/lib/api/mvp-dossier";
import { useCallback } from "react";
import { OrganizationAcceptancePanel } from "./OrganizationAcceptancePanel";
import { organizationAcceptanceApi } from "@/lib/api/organization-acceptance";
import { ChildEipdHistory } from "./ChildEipdHistory";
import {
  childEipdApi,
  type ChildResolution,
  type ResolutionDraft,
  type NegativeDecision,
} from "@/lib/api/child-eipd";
import { ChildAdolescentEditor } from "./ChildAdolescentEditor";
import { childApi, type ChildDocument } from "@/lib/api/child-adolescent";
import { sessionToken } from "./LicitudWorkspace";
import type { FlowTab } from "./AssessmentFlow";
export function ChildAdolescentPage({
  regionPrefix = "licitud-child",
  organizationId,
  treatmentId,
  assessmentId,
  readOnly,
  view,
  editorVisible = true,
  preparationVisible = true,
  reviewVisible = true,
  onResolutionHistory,
  onView,
  refreshVersion = 0,
  onSaved,
  onDirty,
  onWorkState,
  onPreparationState,
  preparationBlocked = false,
  onDocumentPending,
  token = sessionToken,
}: {
  regionPrefix?: string;
  organizationId: string;
  treatmentId: string;
  assessmentId: string;
  readOnly: boolean;
  view?: FlowTab;
  editorVisible?: boolean;
  preparationVisible?: boolean;
  reviewVisible?: boolean;
  onResolutionHistory?: (hasRecords: boolean | null) => void;
  onView?: (view: FlowTab) => void;
  refreshVersion?: number;
  onSaved?: () => void;
  onDirty?: (dirty: boolean) => void;
  onWorkState?: WorkReporter;
  onPreparationState?: WorkReporter;
  preparationBlocked?: boolean;
  onDocumentPending?: (pending: boolean) => void;
  token?: () => Promise<string>;
}) {
  const scope = useCallback(async () => {
    return { organizationId, treatmentId, assessmentId, token: await token() };
  }, [organizationId, treatmentId, assessmentId, token]);
  const pilot = useCallback(
    async (packet: Dossier, form: PilotForm) => preparePilot(await scope(), packet, form),
    [scope]
  );
  const dossier = useCallback(async () => {
    // Invalida paquetes observados cuando cambia material guardado.
    void refreshVersion;
    return loadMvpDossier(await scope());
  }, [scope, refreshVersion]);
  const load = useCallback(async () => childApi.load(await scope()), [scope]);
  const save = useCallback(
    async (doc: ChildDocument | null) => childApi.save(await scope(), doc),
    [scope]
  );
  const readiness = useCallback(async () => childApi.readiness(await scope()), [scope]);
  const history = useCallback(async () => {
    void refreshVersion;
    onResolutionHistory?.(null);
    const current = await scope();
    const [assessment, policy, resolutions] = await Promise.all([
      childApi.load(current),
      childEipdApi.policy(current),
      childEipdApi.list(current),
    ]);
    onResolutionHistory?.(resolutions.length > 0);
    return { status: assessment.status, policy, resolutions, context: assessment };
  }, [scope, refreshVersion, onResolutionHistory]);
  const createResolution = useCallback(
    async (draft: ResolutionDraft) => childEipdApi.create(await scope(), draft),
    [scope]
  );
  const loadReviews = useCallback(
    async (resolution: ChildResolution) => childEipdApi.reviews(await scope(), resolution),
    [scope]
  );
  const createReview = useCallback(
    async (
      resolution: ChildResolution,
      decision: NegativeDecision,
      rationale: string,
      reference: string
    ) => childEipdApi.review(await scope(), resolution, decision, rationale, reference),
    [scope]
  );
  const organizationAcceptance = useCallback(
    (resolution: ChildResolution, historyReadOnly: boolean) => (
      <AcceptanceForResolution
        key={resolution.id}
        readOnly={readOnly || historyReadOnly}
        scope={scope}
        resolution={resolution}
        guided={view !== undefined}
      />
    ),
    [readOnly, scope, view]
  );
  return (
    <div key={`${organizationId}:${treatmentId}:${assessmentId}`} className="space-y-6">
      <div id={`${regionPrefix}-downloads`} hidden={view !== undefined && view !== "historial"}>
        <MvpDossierPanel load={dossier} prepare={pilot} />
      </div>
      <div
        id={`${regionPrefix}-editor`}
        hidden={view !== undefined && (view !== "completar" || !editorVisible)}
      >
        <h2 className="text-xl font-semibold">Infancia y adolescencia · cuando corresponda</h2>
        <ChildAdolescentEditor
          key={`${organizationId}:${treatmentId}:${assessmentId}`}
          load={load}
          save={save}
          readiness={readiness}
          readOnly={readOnly}
          refreshVersion={refreshVersion}
          onSaved={onSaved}
          onDirty={onDirty}
          onWorkState={onWorkState}
        />
      </div>
      <div
        id={`${regionPrefix}-history`}
        hidden={
          view !== undefined &&
          (view === "revisar" ? !reviewVisible : view !== "completar" || !preparationVisible)
        }
      >
        <ChildEipdHistory
          load={history}
          create={createResolution}
          reviews={loadReviews}
          review={createReview}
          readOnly={readOnly}
          organizationAcceptance={organizationAcceptance}
          view={view === "completar" ? "prepare" : view ? "review" : "all"}
          onPrepare={() => {
            if (!preparationBlocked) onView?.("completar");
          }}
          onRecorded={() => {
            onSaved?.();
            onView?.("revisar");
          }}
          preparationBlocked={preparationBlocked}
          onPending={onDocumentPending}
          onWorkState={onPreparationState}
        />
      </div>
    </div>
  );
}

function AcceptanceForResolution({
  scope,
  resolution,
  readOnly,
  guided,
}: {
  scope: () => Promise<import("@/lib/api/child-adolescent").ChildScope>;
  resolution: ChildResolution;
  readOnly: boolean;
  guided?: boolean;
}) {
  const load = useCallback(
    async () => organizationAcceptanceApi.load(await scope(), resolution),
    [scope, resolution]
  );
  const designate = useCallback(
    async (actor: string, p: import("@/lib/api/organization-acceptance").Designation) =>
      organizationAcceptanceApi.designate(await scope(), actor, p),
    [scope]
  );
  const record = useCallback(
    async (
      actor: string,
      p: {
        authority_id: string;
        decision: import("@/lib/api/organization-acceptance").Acceptance["decision"];
        rationale: string;
        evidence_reference: string;
      }
    ) => organizationAcceptanceApi.record(await scope(), resolution, actor, p),
    [scope, resolution]
  );
  return (
    <OrganizationAcceptancePanel
      load={load}
      guided={guided}
      designate={designate}
      record={record}
      readOnly={readOnly}
    />
  );
}
