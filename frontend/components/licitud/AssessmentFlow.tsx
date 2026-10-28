"use client";
import { eipdStepLabels } from "@/lib/licitud/eipd-steps";
import { documentLabels } from "@/lib/licitud/document-labels";
import Link from "next/link";
import { useCallback, useEffect, useId, useState } from "react";
import type { Assessment } from "@/lib/api/licitud";
import { LegalAssessmentEditor } from "./LegalAssessmentEditor";
import { sessionToken } from "./LicitudWorkspace";
import { EipdDocumentView } from "./EipdDocumentFields";
import { EipdDraftEditor } from "./EipdDraftEditor";
import { AssessmentSupportPanel } from "./AssessmentSupportPanel";
import { DossierDocumentView } from "./DossierDocumentView";
import type { Support } from "@/lib/api/assessment-support";
import { ChildAdolescentPage } from "./ChildAdolescentPage";
export type FlowTab = "resumen" | "completar" | "revisar" | "historial";
const tabs: [FlowTab, string][] = [
  ["resumen", "Resumen y siguientes pasos"],
  ["completar", "Completar datos"],
  ["revisar", "Revisar documentos"],
  ["historial", "Historial y descargas"],
];
export type AssessmentLocation = {
  tab: FlowTab;
  section: "alcance" | "base" | "infancia" | "preparar" | "eipd" | "anexos";
  step: number;
};
export function AssessmentFlow({
  organizationId,
  organizationName,
  treatmentId,
  assessmentId,
  readOnly,
  token = sessionToken,
  navigation,
  onPending,
  onAssessmentSaved,
}: {
  organizationId: string;
  organizationName: string;
  treatmentId: string;
  assessmentId: string;
  readOnly: boolean;
  token?: () => Promise<string>;
  navigation?: {
    location: AssessmentLocation;
    labels?: Partial<Record<FlowTab, string>>;
    go: (v: AssessmentLocation) => void;
    scope: { eipd: boolean; infancia: boolean };
  };
  onPending?: (dirty: boolean) => void;
  onAssessmentSaved?: () => void;
}) {
  const [localTab, localSetTab] = useState<FlowTab>("resumen");
  const [localSection, localSetSection] = useState<AssessmentLocation["section"]>("alcance");
  const [localStep, localSetStep] = useState(0);
  const flowId = useId();
  const childPrefix = `${flowId}-child`;
  const supportPanelId = `${flowId}-support`;
  const tab = navigation?.location.tab ?? localTab;
  const section = navigation?.location.section ?? localSection;
  const eipdStep = navigation?.location.step ?? localStep;
  function setTab(value: FlowTab) {
    if (navigation) navigation.go({ ...navigation.location, tab: value });
    else localSetTab(value);
  }
  function setSection(value: AssessmentLocation["section"]) {
    if (navigation) navigation.go({ ...navigation.location, section: value });
    else localSetSection(value);
  }
  function setEipdStep(value: number) {
    if (navigation) navigation.go({ ...navigation.location, step: value });
    else localSetStep(value);
  }
  const [row, setRow] = useState<Assessment | null>(null);
  const [refreshVersion, setRefreshVersion] = useState(0);
  const [legalDirty, setLegalDirty] = useState(false);
  const [childDirty, setChildDirty] = useState(false);
  const [resolutionHistory, setResolutionHistory] = useState<boolean | null>(null);
  const [documentDirty, setDocumentDirty] = useState(false);
  const [eipdDirty, setEipdDirty] = useState(false);
  const [supportDirty, setSupportDirty] = useState(false);
  const [support, setSupport] = useState<Support | null>(null);
  const dirty = legalDirty || childDirty || eipdDirty;
  const hasUnsaved = dirty || documentDirty || supportDirty;
  const childRelevant = navigation
    ? navigation.scope.infancia
    : Boolean(
        row?.rat_context_snapshot?.special_regimes?.includes_children ||
        row?.rat_context_snapshot?.special_regimes?.includes_adolescents ||
        row?.child_adolescent_assessment
      );
  const childReviewVisible = childRelevant || resolutionHistory !== false;
  const loaded = useCallback((value: Assessment) => setRow(value), []);
  const saved = useCallback(
    (value?: Assessment) => {
      if (value) setRow(value);
      setRefreshVersion((n) => n + 1);
      onAssessmentSaved?.();
    },
    [onAssessmentSaved]
  );
  const childSaved = useCallback(() => saved(), [saved]);
  useEffect(() => {
    if (navigation) return;
    const change = () => {
      const value = window.location.hash.slice(1);
      if (tabs.some(([key]) => key === value)) localSetTab(value as FlowTab);
    };
    change();
    window.addEventListener("hashchange", change);
    return () => window.removeEventListener("hashchange", change);
  }, [navigation]);
  useEffect(() => {
    onPending?.(hasUnsaved);
  }, [hasUnsaved, onPending]);
  useEffect(() => {
    if (!hasUnsaved) return;
    const warn = (event: BeforeUnloadEvent) => {
      event.preventDefault();
      event.returnValue = "";
    };
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, [hasUnsaved]);
  function go(next: FlowTab) {
    setTab(next);
    if (!navigation) window.history.replaceState(null, "", `#${next}`);
  }
  return (
    <div className="licitud-ui space-y-5 [&_button]:rounded [&_button]:border [&_button]:px-3 [&_button]:py-2 [&_button:disabled]:opacity-50">
      {!navigation && (
        <>
          <p className="rounded border border-blue-200 bg-blue-50 p-4">
            Recorrido conectado al servidor · Solo datos ficticios. Guardar y revisar no confirman
            ni activan EIPD.
          </p>
          <aside aria-label="Alcance de la evaluación" className="space-y-2 rounded border p-4">
            <p className="font-semibold">{organizationName}</p>
            <p>Finalidad: {row?.purpose_snapshot ?? "Cargando evaluación…"}</p>
            <p>
              Evaluación: {row ? `versión ${row.version} · ${row.status}` : "pendiente de carga"}.{" "}
              {readOnly && "Tu rol permite solo consulta."}
            </p>
            <p className="text-sm">
              Estás trabajando en la evaluación guardada. Cada resolución documental conserva su
              propia versión y las revisiones que le corresponden.
            </p>
          </aside>
        </>
      )}
      {navigation && readOnly && <p>Tu rol permite solo consulta.</p>}
      <div
        hidden={!!navigation}
        role="tablist"
        aria-label="Recorrido de Bases de licitud"
        className="grid grid-cols-2 gap-2 md:grid-cols-4"
      >
        {tabs.map(([key, label], index) => (
          <button
            type="button"
            key={key}
            id={`${flowId}-tab-${key}`}
            role="tab"
            aria-selected={tab === key}
            aria-controls={`${flowId}-panel-${key}`}
            tabIndex={tab === key ? 0 : -1}
            className={`rounded border p-3 text-left ${tab === key ? "bg-blue-800 font-semibold text-white" : "border-slate-300 bg-white"}`}
            onClick={() => go(key)}
            onKeyDown={(event) => {
              const target =
                event.key === "Home"
                  ? 0
                  : event.key === "End"
                    ? tabs.length - 1
                    : event.key === "ArrowRight"
                      ? (index + 1) % tabs.length
                      : event.key === "ArrowLeft"
                        ? (index + tabs.length - 1) % tabs.length
                        : null;
              if (target !== null) {
                event.preventDefault();
                go(tabs[target][0]);
                document.getElementById(`${flowId}-tab-${tabs[target][0]}`)?.focus();
              }
            }}
          >
            {label}
          </button>
        ))}
      </div>
      {hasUnsaved && tab !== "completar" && (
        <p role="status" className="rounded border border-amber-400 bg-amber-50 p-3">
          Hay cambios pendientes en Completar datos. Se conservan al navegar; los documentos y
          descargas usan lo guardado en servidor.
        </p>
      )}
      <section
        role={navigation ? "region" : "tabpanel"}
        id={`${flowId}-panel-resumen`}
        aria-labelledby={navigation ? undefined : `${flowId}-tab-resumen`}
        aria-label={navigation ? "Resumen de la evaluación" : undefined}
        hidden={tab !== "resumen"}
        className="space-y-4 rounded border p-5"
      >
        <h2 className="text-xl font-semibold">Recorrido de esta evaluación</h2>
        <ol className="list-decimal space-y-2 pl-6">
          <li>Revisa el alcance del RAT asociado a esta evaluación.</li>
          <li>Completa y guarda base, fundamento y los análisis que correspondan.</li>
          <li>Consulta la versión documental antes de emitir una revisión o decisión.</li>
          <li>Consulta el historial y descarga el expediente guardado.</li>
        </ol>
        <p>
          {dirty
            ? "Siguiente paso: guarda los cambios pendientes."
            : "Siguiente paso: revisa el alcance y completa los análisis pendientes. Guardado no significa aprobación jurídica."}
        </p>
        <button
          type="button"
          className="rounded bg-blue-800 px-4 py-2 text-white"
          onClick={() => go("completar")}
        >
          Ir a completar datos
        </button>
        <p>
          Completa y guarda los datos de esta evaluación. Luego podrás consultar el alcance del RAT,
          la base de licitud y el documento EIPD guardado, si existe. Guardar no equivale a aprobar
          la evaluación.
        </p>
      </section>
      <section
        role={navigation ? "region" : "tabpanel"}
        aria-owns={
          !navigation && tab === "completar"
            ? `${childPrefix}-editor ${childPrefix}-history`
            : undefined
        }
        id={`${flowId}-panel-completar`}
        aria-labelledby={navigation ? undefined : `${flowId}-tab-completar`}
        aria-label={navigation ? "Completar datos de la evaluación" : undefined}
        hidden={tab !== "completar"}
        className="space-y-5"
      >
        <nav
          hidden={!!navigation}
          aria-label="Secciones para completar"
          className="flex flex-wrap gap-2"
        >
          {(
            [
              ["alcance", "1. Alcance del RAT"],
              ["base", "2. Base y fundamento"],
              ...(childRelevant ? [["infancia", "3. Infancia"]] : []),
            ] as ["alcance" | "base" | "infancia", string][]
          ).map(([key, label]) => (
            <button
              key={key}
              type="button"
              aria-current={section === key ? "step" : undefined}
              className={section === key ? "bg-blue-800 text-white" : "bg-white"}
              onClick={() => setSection(key)}
            >
              {label}
            </button>
          ))}
          <button
            type="button"
            className={section === "eipd" ? "bg-blue-800 text-white" : "bg-white"}
            onClick={() => setSection("eipd")}
          >
            Documentar EIPD
          </button>
          <button
            type="button"
            className={section === "anexos" ? "bg-blue-800 text-white" : "bg-white"}
            onClick={() => setSection("anexos")}
          >
            Anexos de respaldo
          </button>
          {childRelevant && (
            <button
              type="button"
              className={section === "preparar" ? "bg-blue-800 text-white" : "bg-white"}
              onClick={() => setSection("preparar")}
            >
              {documentLabels.prepareChild}
            </button>
          )}
        </nav>
        <div hidden={section !== "alcance"}>
          <section aria-label="Alcance RAT asociado" className="space-y-2 rounded border p-4">
            <h2 className="font-semibold">1. Alcance del RAT · solo lectura</h2>
            <ul className="list-disc space-y-1 pl-5">
              <li>Finalidad: {row?.purpose_snapshot ?? "Pendiente de carga"}</li>
              <li>
                Titulares:{" "}
                {row?.rat_context_snapshot?.data_subjects?.map((v) => v.category_name).join(", ") ||
                  "Consulta el alcance guardado del expediente."}
              </li>
              <li>
                Categorías:{" "}
                {row?.rat_context_snapshot?.data_categories
                  ?.map((v) => v.category_name)
                  .join(", ") || "Consulta el alcance guardado del expediente."}
              </li>
              <li>
                Fuentes:{" "}
                {row?.rat_context_snapshot?.data_sources
                  ?.map((v) => v.description || v.source_type || "Sin descripción")
                  .join("; ") || "Sin fuentes en el contexto asociado."}
              </li>
            </ul>
            <p>
              Este contexto pertenece a la evaluación guardada; no se reemplaza automáticamente al
              editar el RAT.
            </p>
            <Link className="text-blue-800 underline" href="/dashboard/rat">
              Consultar inventario RAT
            </Link>
          </section>
          <button
            type="button"
            className="rounded bg-blue-800 px-4 py-2 text-white"
            onClick={() => setSection("base")}
          >
            Continuar a base y fundamento
          </button>
        </div>
        <div hidden={section !== "base"}>
          <h2 className="font-semibold">2. Base y fundamento</h2>
          <LegalAssessmentEditor
            organizationId={organizationId}
            treatmentId={treatmentId}
            assessmentId={assessmentId}
            readOnly={readOnly}
            token={token}
            onLoaded={loaded}
            onSaved={saved}
            onDirty={setLegalDirty}
          />
          <p className="text-sm">
            Guarda el borrador para que tus cambios aparezcan en Revisar documentos.
            {childRelevant && " Los análisis de infancia se completan en su sección específica."}
          </p>
        </div>
        <div hidden={section !== "eipd" || (navigation && !navigation.scope.eipd)}>
          <EipdDraftEditor
            externalNavigation={!!navigation}
            supportPanelId={supportPanelId}
            organizationId={organizationId}
            treatmentId={treatmentId}
            assessmentId={assessmentId}
            readOnly={readOnly}
            token={token}
            refreshVersion={refreshVersion}
            onDirty={setEipdDirty}
            onSaved={saved}
            onLoaded={loaded}
            valuation={support?.risk_evaluation}
            annexes={support?.annexes}
            step={eipdStep}
            onStepChange={setEipdStep}
          />
        </div>
      </section>
      <section
        role={navigation ? "region" : "tabpanel"}
        aria-owns={!navigation && tab === "revisar" ? `${childPrefix}-history` : undefined}
        id={`${flowId}-panel-revisar`}
        aria-labelledby={navigation ? undefined : `${flowId}-tab-revisar`}
        aria-label={navigation ? "Documentos guardados de la evaluación" : undefined}
        hidden={tab !== "revisar"}
        className="space-y-3"
      >
        <h2 className="text-xl font-semibold">
          {navigation?.labels?.revisar ?? "Revisar documentos guardados"}
        </h2>
        <p>
          Consulta lo guardado; las ediciones pendientes no se incluyen. Consultar contenido no
          emite una revisión formal.
        </p>
        {row && (
          <>
            <section aria-label="Alcance RAT guardado" className="space-y-3 rounded border p-4">
              <h3 className="font-semibold">Alcance RAT asociado guardado</h3>
              <details>
                <summary>Consultar alcance RAT</summary>
                <DossierDocumentView
                  document={{
                    kind: "rat",
                    status: "disponible",
                    version: 1,
                    coverage: "",
                    content_hash: null,
                    organization_acceptance: "sin_flujo",
                    acceptance_events: [],
                    content: { ...row.rat_context_snapshot, purpose: row.purpose_snapshot },
                  }}
                />
              </details>
            </section>
            <section
              aria-label="Evaluación de licitud guardada"
              className="space-y-3 rounded border p-4"
            >
              <h3 className="font-semibold">
                Base de licitud y fundamento
                {row.legal_basis === "interes_legitimo_art13d" ? " · LIA" : ""} · evaluación versión{" "}
                {row.version}
              </h3>
              <details>
                <summary>
                  Consultar evaluación de licitud
                  {row.legal_basis === "interes_legitimo_art13d" ? " y LIA" : ""}
                </summary>
                <DossierDocumentView
                  document={{
                    kind: "licitud_lia",
                    status: "disponible",
                    version: row.version,
                    coverage: "",
                    content_hash: null,
                    organization_acceptance: "sin_flujo",
                    acceptance_events: [],
                    content: { ...row },
                  }}
                />
              </details>
            </section>
          </>
        )}

        {row?.eipd_resolution_assessment && (
          <section
            className="space-y-3 rounded border p-4"
            aria-label="Borrador EIPD guardado para consulta"
          >
            <h3 className="font-semibold">
              Documento EIPD guardado · evaluación versión {row.version}
            </h3>
            <p>
              Consulta el contenido guardado en servidor. Es un borrador documental, distinto de una
              resolución registrada. Los cambios pendientes no se incluyen.
            </p>
            <dl className="space-y-3">
              <div>
                <dt className="bg-blue-100 p-2 font-semibold text-blue-950">Referencia EIPD</dt>
                <dd className="bg-white p-3">
                  {String(row.eipd_resolution_assessment.document_reference ?? "Sin referencia")}
                </dd>
              </div>
              <div>
                <dt className="bg-blue-100 p-2 font-semibold text-blue-950">
                  {documentLabels.edition}
                </dt>
                <dd className="bg-white p-3">
                  {String(
                    row.eipd_resolution_assessment.document_version ?? "Sin nombre de edición"
                  )}
                </dd>
              </div>
            </dl>
            <EipdDocumentView
              value={row.eipd_resolution_assessment}
              valuation={support?.risk_evaluation}
              annexes={support?.annexes}
            />
            {childReviewVisible && (
              <p>
                El registro de revisiones disponible abajo corresponde a resoluciones de infancia
                seleccionadas; no se atribuye a este borrador EIPD general.
              </p>
            )}
          </section>
        )}

        {childReviewVisible ? (
          <p>
            Elige una resolución y lee su contenido. Revisar deja una observación; decidir por la
            organización requiere facultad vigente. Ninguna acción edita el original.
          </p>
        ) : (
          <p>
            {row?.eipd_resolution_assessment
              ? "El borrador EIPD general está disponible para consulta. El registro de revisiones formales de este documento aún no está integrado."
              : "No hay un documento EIPD guardado. El alcance RAT y la evaluación de licitud están disponibles arriba."}
          </p>
        )}
      </section>
      <section
        role={navigation ? "region" : "tabpanel"}
        aria-owns={!navigation ? `${childPrefix}-downloads` : undefined}
        id={`${flowId}-panel-historial`}
        aria-labelledby={navigation ? undefined : `${flowId}-tab-historial`}
        aria-label={navigation ? "Historial y descargas de la evaluación" : undefined}
        hidden={tab !== "historial"}
      >
        <h2 className="text-xl font-semibold">
          {navigation?.labels?.historial ?? "Historial y descargas del servidor"}
        </h2>
        <p>
          El expediente reúne lo guardado. Los cambios pendientes del formulario no se incluyen.
        </p>
      </section>
      <AssessmentSupportPanel
        panelId={supportPanelId}
        organizationId={organizationId}
        treatmentId={treatmentId}
        assessmentId={assessmentId}
        token={token}
        row={row}
        readOnly={readOnly}
        blocked={dirty || !row}
        refreshVersion={refreshVersion}
        mode={
          tab === "completar" && section === "eipd" && eipdStep === 3
            ? "risks"
            : tab === "completar" && section === "anexos"
              ? "annexes"
              : "review"
        }
        hidden={
          !(
            tab === "revisar" ||
            (tab === "completar" &&
              ((section === "eipd" && eipdStep === 3) || section === "anexos"))
          )
        }
        onSaved={childSaved}
        onLoaded={setSupport}
        onDirty={setSupportDirty}
      />
      {navigation && navigation.scope.eipd && tab === "completar" && section === "eipd" && (
        <nav aria-label="Cambiar paso EIPD" className="flex flex-wrap gap-3">
          {eipdStep > 0 && (
            <button type="button" onClick={() => setEipdStep(eipdStep - 1)}>
              ← Anterior: {eipdStepLabels[eipdStep - 1]}
            </button>
          )}
          {eipdStep < eipdStepLabels.length - 1 && (
            <button type="button" onClick={() => setEipdStep(eipdStep + 1)}>
              Siguiente: {eipdStepLabels[eipdStep + 1]} →
            </button>
          )}
        </nav>
      )}
      <ChildAdolescentPage
        regionPrefix={childPrefix}
        organizationId={organizationId}
        treatmentId={treatmentId}
        assessmentId={assessmentId}
        readOnly={readOnly}
        token={token}
        view={tab}
        editorVisible={section === "infancia" && childRelevant}
        preparationVisible={section === "preparar" && childRelevant}
        reviewVisible={childReviewVisible}
        onResolutionHistory={setResolutionHistory}
        onView={(next) => {
          if (navigation)
            navigation.go({
              ...navigation.location,
              tab: next,
              section: next === "completar" ? (childRelevant ? "preparar" : "alcance") : section,
            });
          else {
            if (next === "completar") setSection(childRelevant ? "preparar" : "alcance");
            go(next);
          }
        }}
        refreshVersion={refreshVersion}
        onSaved={childSaved}
        onDirty={setChildDirty}
        preparationBlocked={dirty || supportDirty || !row || !childRelevant}
        onDocumentPending={setDocumentDirty}
      />
    </div>
  );
}
