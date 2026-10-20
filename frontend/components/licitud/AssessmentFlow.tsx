"use client";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import type { Assessment } from "@/lib/api/licitud";
import { LegalAssessmentEditor } from "./LegalAssessmentEditor";
import { sessionToken } from "./LicitudWorkspace";
import { EipdDocumentView } from "./EipdDocumentFields";
import { EipdDraftEditor } from "./EipdDraftEditor";
import { ChildAdolescentPage } from "./ChildAdolescentPage";
export type FlowTab = "resumen" | "completar" | "revisar" | "historial";
const tabs: [FlowTab, string][] = [
  ["resumen", "Resumen y siguientes pasos"],
  ["completar", "Completar datos"],
  ["revisar", "Revisar documentos"],
  ["historial", "Historial y descargas"],
];
export function AssessmentFlow({
  organizationId,
  organizationName,
  treatmentId,
  assessmentId,
  readOnly,
  token = sessionToken,
}: {
  organizationId: string;
  organizationName: string;
  treatmentId: string;
  assessmentId: string;
  readOnly: boolean;
  token?: () => Promise<string>;
}) {
  const [tab, setTab] = useState<FlowTab>("resumen");
  const [section, setSection] = useState<"alcance" | "base" | "infancia" | "preparar" | "eipd">(
    "alcance"
  );
  const [row, setRow] = useState<Assessment | null>(null);
  const [refreshVersion, setRefreshVersion] = useState(0);
  const [legalDirty, setLegalDirty] = useState(false);
  const [childDirty, setChildDirty] = useState(false);
  const [resolutionHistory, setResolutionHistory] = useState<boolean | null>(null);
  const [documentDirty, setDocumentDirty] = useState(false);
  const [eipdDirty, setEipdDirty] = useState(false);
  const dirty = legalDirty || childDirty || eipdDirty;
  const hasUnsaved = dirty || documentDirty;
  const childRelevant = Boolean(
    row?.rat_context_snapshot?.special_regimes?.includes_children ||
    row?.rat_context_snapshot?.special_regimes?.includes_adolescents ||
    row?.child_adolescent_assessment
  );
  const childReviewVisible = childRelevant || resolutionHistory !== false;
  const loaded = useCallback((value: Assessment) => setRow(value), []);
  const saved = useCallback((value?: Assessment) => {
    if (value) setRow(value);
    setRefreshVersion((n) => n + 1);
  }, []);
  const childSaved = useCallback(() => saved(), [saved]);
  useEffect(() => {
    const change = () => {
      const value = window.location.hash.slice(1);
      if (tabs.some(([key]) => key === value)) setTab(value as FlowTab);
    };
    change();
    window.addEventListener("hashchange", change);
    return () => window.removeEventListener("hashchange", change);
  }, []);
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
    window.history.replaceState(null, "", `#${next}`);
  }
  return (
    <div className="space-y-5 [&_button]:rounded [&_button]:border [&_button]:px-3 [&_button]:py-2 [&_button:disabled]:opacity-50">
      <p className="rounded border border-blue-200 bg-blue-50 p-4">
        Recorrido conectado al servidor · Solo datos ficticios. Guardar y revisar no confirman ni
        activan EIPD.
      </p>
      <aside aria-label="Alcance de la evaluación" className="space-y-2 rounded border p-4">
        <p className="font-semibold">{organizationName}</p>
        <p>Finalidad: {row?.purpose_snapshot ?? "Cargando evaluación…"}</p>
        <p>
          Evaluación: {row ? `versión ${row.version} · ${row.status}` : "pendiente de carga"}.{" "}
          {readOnly && "Tu rol permite solo consulta."}
        </p>
        <p className="text-sm">
          La versión de la evaluación y la versión de una resolución documental son registros
          distintos. Las revisiones se vinculan a la resolución seleccionada.
        </p>
      </aside>
      <div
        role="tablist"
        aria-label="Recorrido de Bases de licitud"
        className="grid grid-cols-2 gap-2 md:grid-cols-4"
      >
        {tabs.map(([key, label], index) => (
          <button
            type="button"
            key={key}
            id={`licitud-tab-${key}`}
            role="tab"
            aria-selected={tab === key}
            aria-controls={`licitud-panel-${key}`}
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
                document.getElementById(`licitud-tab-${tabs[target][0]}`)?.focus();
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
        role="tabpanel"
        id="licitud-panel-resumen"
        aria-labelledby="licitud-tab-resumen"
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
          La preparación disponible corresponde al contrato documental EIPD de infancia. No crea una
          versión autónoma de RAT o LIA ni determina que una EIPD sea obligatoria.
        </p>
      </section>
      <section
        role="tabpanel"
        aria-owns={tab === "completar" ? "licitud-child-editor licitud-child-history" : undefined}
        id="licitud-panel-completar"
        aria-labelledby="licitud-tab-completar"
        hidden={tab !== "completar"}
        className="space-y-5"
      >
        <nav aria-label="Secciones para completar" className="flex flex-wrap gap-2">
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
            className={section === "preparar" ? "bg-blue-800 text-white" : "bg-white"}
            onClick={() => setSection("preparar")}
          >
            Preparar resolución documental de infancia
          </button>
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
            Guarda el borrador antes de preparar una versión documental. Los análisis de infancia se
            completan en su sección cuando corresponden al alcance guardado.
          </p>
        </div>
        <div hidden={section !== "eipd"}>
          <EipdDraftEditor
            organizationId={organizationId}
            treatmentId={treatmentId}
            assessmentId={assessmentId}
            readOnly={readOnly}
            token={token}
            refreshVersion={refreshVersion}
            onDirty={setEipdDirty}
            onSaved={saved}
            onLoaded={loaded}
          />
        </div>
      </section>
      <section
        role="tabpanel"
        aria-owns={tab === "revisar" ? "licitud-child-history" : undefined}
        id="licitud-panel-revisar"
        aria-labelledby="licitud-tab-revisar"
        hidden={tab !== "revisar"}
        className="space-y-3"
      >
        <h2 className="text-xl font-semibold">Revisar documentos guardados</h2>
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
            <EipdDocumentView value={row.eipd_resolution_assessment} />
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
              : "No hay documentos guardados para consultar en esta pestaña. Puedes consultar la evaluación guardada en Historial y descargas."}
          </p>
        )}
      </section>
      <section
        role="tabpanel"
        aria-owns="licitud-child-downloads"
        id="licitud-panel-historial"
        aria-labelledby="licitud-tab-historial"
        hidden={tab !== "historial"}
      >
        <h2 className="text-xl font-semibold">Historial y descargas del servidor</h2>
        <p>
          El expediente reúne lo guardado. Los cambios pendientes del formulario no se incluyen.
        </p>
      </section>
      <ChildAdolescentPage
        organizationId={organizationId}
        treatmentId={treatmentId}
        assessmentId={assessmentId}
        readOnly={readOnly}
        token={token}
        view={tab}
        editorVisible={section === "infancia" && childRelevant}
        preparationVisible={section === "preparar"}
        reviewVisible={childReviewVisible}
        onResolutionHistory={setResolutionHistory}
        onView={(next) => {
          if (next === "completar") setSection("preparar");
          go(next);
        }}
        refreshVersion={refreshVersion}
        onSaved={childSaved}
        onDirty={setChildDirty}
        preparationBlocked={dirty || !row}
        onDocumentPending={setDocumentDirty}
      />
    </div>
  );
}
