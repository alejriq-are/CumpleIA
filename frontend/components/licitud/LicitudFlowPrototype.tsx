"use client";

import { useEffect, useState, type KeyboardEvent, type ReactNode } from "react";

const tabs = [
  ["resumen", "Resumen y siguientes pasos"],
  ["completar", "Completar datos"],
  ["revisar", "Revisar documentos"],
  ["historial", "Historial y descargas"],
] as const;
type Tab = (typeof tabs)[number][0];
type Scenario = "adultos" | "infancia";
type Section = "alcance" | "fundamento" | "infancia";
const scenarios: Record<
  Scenario,
  { label: string; treatment: string; purposes: Record<string, string> }
> = {
  adultos: {
    label: "Clientes adultos",
    treatment: "[FICTICIA] Gestión de clientes adultos",
    purposes: {
      gestion: "[FICTICIA] Administrar la relación con clientes adultos sintéticos.",
      consultas: "[FICTICIA] Atender consultas de clientes adultos sintéticos.",
    },
  },
  infancia: {
    label: "Participantes de 10 a 13 años",
    treatment: "[FICTICIA] Programa con participantes de 10 a 13 años",
    purposes: {
      ensayo: "[FICTICIA] Ensayar el análisis de infancia con cinco participantes sintéticos.",
    },
  },
};
const sections: [Section, string][] = [
  ["alcance", "Alcance del RAT"],
  ["fundamento", "Base y fundamento"],
  ["infancia", "Infancia"],
];
type Draft = {
  basis: string;
  rationale: string;
  age: string;
  notes: string;
  origin: { version: string; reference: string } | null;
  changeReason: string;
};
type ReviewDraft = { kind: "revision" | "decision"; choice: string; rationale: string };
const initialDraft = (scenario: Scenario): Draft => ({
  basis: "",
  rationale: "[FICTICIA] Evaluación pendiente. No hay autorización para operar.",
  age: scenario === "adultos" ? "" : "[FICTICIA] Cinco participantes sintéticos de 10 a 13 años.",
  notes: "",
  origin: null,
  changeReason: "",
});
type PreparedDocument = {
  version: string;
  reference: string;
  treatment: string;
  purpose: string;
  subjects: string;
  category: string;
  source: string;
  evaluationVersion: number;
  organization: string;
  preparatoryReview?: "lectura_simulada_sin_aceptacion_juridica";
  draft: Draft;
  pending: string[];
};
function referenceFor(scenario: Scenario, purpose: string, version: string) {
  return `SIMULADA-${scenario === "adultos" ? "ADULTOS" : "INFANCIA"}${purpose === "consultas" ? "-CONSULTAS" : ""}-00${version}`;
}
function prepareSnapshot(
  scenario: Scenario,
  purpose: string,
  draft: Draft,
  version: string
): PreparedDocument {
  const pending = [
    "Revisión jurídica y evidencias pendientes en este ensayo. La lista no acredita completitud legal.",
  ];
  if (draft.origin && !draft.changeReason.trim())
    pending.unshift("Motivo del cambio sin completar.");
  if (!draft.basis) pending.unshift("Base de licitud pendiente de definir.");
  if (!draft.rationale.trim()) pending.unshift("Fundamento sin completar.");
  if (scenario === "infancia") {
    pending.push(
      "Interés superior, autonomía y autorización: análisis adicionales pendientes en el ejemplo."
    );
    if (!draft.age.trim()) pending.unshift("Análisis de edad y alcance sin completar.");
  }
  return {
    version,
    reference: referenceFor(scenario, purpose, version),
    treatment: scenarios[scenario].treatment,
    purpose: scenarios[scenario].purposes[purpose],
    subjects:
      scenario === "adultos"
        ? "Clientes adultos sintéticos"
        : "Participantes sintéticos de 10 a 13 años",
    category: "Identificación",
    source: "Registros generados para el ensayo",
    evaluationVersion: 1,
    organization: "[FICTICIA] Organización de demostración",
    draft: { ...draft },
    pending,
  };
}
function DocumentContent({ document }: { document: PreparedDocument }) {
  const fields: [string, string][] = [
    ...(document.draft.origin
      ? [
          [
            "Versión de origen",
            `${document.draft.origin.reference} · DEMO-${document.draft.origin.version}`,
          ] as [string, string],
          ["Motivo del cambio", document.draft.changeReason || "Sin completar"] as [string, string],
        ]
      : []),
    ["Organización", document.organization],
    ["Tratamiento", document.treatment],
    ["Finalidad", document.purpose],
    ["Titulares", document.subjects],
    ["Categoría", document.category],
    ["Fuente", document.source],
    [
      "Base propuesta",
      document.draft.basis ? "Propuesta pendiente de análisis (ejemplo)" : "Pendiente de definir",
    ],
    ["Fundamento", document.draft.rationale || "Sin completar"],
    ...(document.draft.age
      ? [["Análisis de edad y alcance", document.draft.age] as [string, string]]
      : []),
    ["Notas específicas del documento", document.draft.notes || "Sin notas (opcional)"],
  ];
  return (
    <dl className="space-y-3">
      {fields.map(([label, value]) => (
        <div key={label}>
          <dt className="font-semibold">{label}</dt>
          <dd className="whitespace-pre-wrap break-words">{value}</dd>
        </div>
      ))}
    </dl>
  );
}
const emptyReview = (): ReviewDraft => ({ kind: "revision", choice: "", rationale: "" });
const button =
  "rounded-md bg-blue-800 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-900 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-600 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-800";
const secondary =
  "rounded-md border border-slate-400 bg-white px-4 py-2 text-sm font-semibold text-slate-800 hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-800";
const input = "mt-2 block w-full rounded-md border border-slate-400 bg-white p-3 text-slate-900";

function Card({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="space-y-4 rounded-xl border border-slate-200 bg-white p-5 sm:p-6">
      <h2 className="text-lg font-semibold text-slate-900">{title}</h2>
      {children}
    </section>
  );
}

export function LicitudFlowPrototype() {
  const [scenario, setScenario] = useState<Scenario>("adultos");
  const [purpose, setPurpose] = useState("gestion");
  const [selectedTreatment, setSelectedTreatment] = useState<Scenario | "">("");
  const [selectedPurpose, setSelectedPurpose] = useState("");
  const [selectionOpen, setSelectionOpen] = useState(true);
  const [active, setActive] = useState(false);
  const [revoked, setRevoked] = useState(false);
  const [tab, setTab] = useState<Tab>("resumen");
  const [section, setSection] = useState<Section>("alcance");
  const [version, setVersion] = useState("2");
  const [ready, setReady] = useState(false);
  const [drafts, setDrafts] = useState<Record<string, Draft>>({});
  const [saved, setSaved] = useState<Record<string, Draft>>({});
  const [reviews, setReviews] = useState<Record<string, ReviewDraft>>({});
  const [notice, setNotice] = useState("");
  const [facultyOpen, setFacultyOpen] = useState(false);
  const [preview, setPreview] = useState(false);
  const [preparationOpen, setPreparationOpen] = useState(false);
  const [reviewedFingerprint, setReviewedFingerprint] = useState("");
  const [copyRequest, setCopyRequest] = useState<{
    scopeKey: string;
    document: PreparedDocument;
  } | null>(null);
  const [documents, setDocuments] = useState<Record<string, PreparedDocument[]>>({});
  const current = scenarios[scenario];
  const scopeKey = `${scenario}:${purpose}`;
  const draft = drafts[scopeKey] ?? initialDraft(scenario);
  const dirty = JSON.stringify(draft) !== JSON.stringify(saved[scopeKey] ?? initialDraft(scenario));
  const reviewKey = `${scopeKey}:${version}`;
  const review = reviews[reviewKey] ?? emptyReview();
  const adult = scenario === "adultos";
  const documentName = adult
    ? "Documento de evaluación de licitud"
    : "Resolución documental de infancia";
  const reference = referenceFor(scenario, purpose, version);
  const prepared = documents[scopeKey] ?? [];
  const selectedDocument = prepared.find((document) => document.version === version);
  const nextVersion = String(
    Math.max(2, ...prepared.map((document) => Number(document.version))) + 1
  );
  const candidate = prepareSnapshot(scenario, purpose, draft, nextVersion);
  const fingerprint = JSON.stringify(candidate);
  const reviewed = reviewedFingerprint === fingerprint;
  const missingChangeReason = Boolean(draft.origin && !draft.changeReason.trim());
  const sourceDocument =
    selectedDocument ?? prepareSnapshot(scenario, purpose, initialDraft(scenario), version);

  useEffect(() => {
    const readLocation = () => {
      const params = new URLSearchParams(window.location.hash.slice(1));
      // Preserve old V1 demo links while keeping permissions separate from the treatment.
      const legacy = params.get("escenario");
      const target = params.get("tratamiento") ?? (legacy === "revocada" ? "infancia" : legacy);
      const destination = params.get("pestana");
      if (target && Object.hasOwn(scenarios, target)) {
        const treatment = target as Scenario;
        const proposed = params.get("finalidad") ?? Object.keys(scenarios[treatment].purposes)[0];
        if (Object.hasOwn(scenarios[treatment].purposes, proposed)) {
          setScenario(treatment);
          setPurpose(proposed);
          setSelectedTreatment(treatment);
          setSelectedPurpose(proposed);
          setActive(true);
          setSelectionOpen(false);
        }
      }
      setRevoked(params.get("facultad") === "revocada" || legacy === "revocada");
      if (tabs.some(([key]) => key === destination)) setTab(destination as Tab);
      if (/^[1-9]\d{0,2}$/.test(params.get("version") ?? "")) setVersion(params.get("version")!);
      setPreview(false);
    };
    readLocation();
    setReady(true);
    window.addEventListener("hashchange", readLocation);
    return () => window.removeEventListener("hashchange", readLocation);
  }, []);
  useEffect(() => {
    if (!ready || !active) return;
    const params = new URLSearchParams({
      tratamiento: scenario,
      finalidad: purpose,
      facultad: revoked ? "revocada" : "vigente",
      pestana: tab,
      version,
    });
    window.history.replaceState(null, "", `#${params}`);
  }, [scenario, purpose, revoked, tab, version, ready, active]);

  useEffect(() => {
    if (
      ready &&
      active &&
      Number(version) > 2 &&
      !documents[scopeKey]?.some((row) => row.version === version)
    ) {
      setVersion("2");
      setNotice(
        "La versión de ensayo no está disponible en esta visita. Al recargar se reinician los registros simulados; se muestra DEMO-2."
      );
    }
  }, [ready, active, version, documents, scopeKey]);
  function openPreparation() {
    setPreparationOpen(true);
    setReviewedFingerprint("");
    setNotice("");
  }
  function backToEdit(target: Section) {
    setSection(target);
    setPreparationOpen(false);
    setReviewedFingerprint("");
  }
  function registerDocument() {
    if (!reviewed || missingChangeReason) return;
    const snapshot: PreparedDocument = {
      ...structuredClone(candidate),
      preparatoryReview: "lectura_simulada_sin_aceptacion_juridica",
    };
    setDocuments((all) => ({ ...all, [scopeKey]: [...(all[scopeKey] ?? []), snapshot] }));
    setSaved((all) => ({ ...all, [scopeKey]: { ...draft } }));
    setVersion(snapshot.version);
    setPreparationOpen(false);
    setReviewedFingerprint("");
    go("revisar");
    setNotice(
      `Versión DEMO-${snapshot.version} registrada solo en memoria para revisión. No es aprobación jurídica ni guardado en servidor; se reinicia al recargar.`
    );
  }
  function copyVersion(document: PreparedDocument) {
    const nextDraft: Draft = {
      ...structuredClone(document.draft),
      origin: { version: document.version, reference: document.reference },
      changeReason: "",
    };
    setDrafts((all) => ({ ...all, [scopeKey]: nextDraft }));
    setCopyRequest(null);
    backToEdit("fundamento");
    go("completar");
    setNotice(
      `Se copió DEMO-${document.version} a un nuevo borrador. La versión ${document.reference} se conserva intacta. Indica el motivo del cambio.`
    );
  }
  function startCopy() {
    if (dirty) setCopyRequest({ scopeKey, document: structuredClone(sourceDocument) });
    else copyVersion(sourceDocument);
  }
  function go(target: Tab) {
    setTab(target);
    setPreview(false);
    setCopyRequest(null);
  }
  function edit(key: Exclude<keyof Draft, "origin">, value: string) {
    setDrafts((all) => ({
      ...all,
      [scopeKey]: { ...(all[scopeKey] ?? initialDraft(scenario)), [key]: value },
    }));
    setNotice("");
  }
  function changeReview(change: Partial<ReviewDraft>) {
    setReviews((all) => ({
      ...all,
      [reviewKey]: { ...(all[reviewKey] ?? emptyReview()), ...change },
    }));
    setPreview(false);
  }
  function moveTab(event: KeyboardEvent<HTMLButtonElement>, index: number) {
    let next: number;
    if (event.key === "ArrowRight") next = (index + 1) % tabs.length;
    else if (event.key === "ArrowLeft") next = (index + tabs.length - 1) % tabs.length;
    else if (event.key === "Home") next = 0;
    else if (event.key === "End") next = tabs.length - 1;
    else return;
    event.preventDefault();
    go(tabs[next][0]);
    document.getElementById(`prototype-tab-${tabs[next][0]}`)?.focus();
  }
  function download() {
    const packet = {
      type: "maqueta_navegable",
      data_kind: "ficticios",
      source: selectedDocument ? "version_ensayo_en_memoria" : "fixture_demostrativa",
      prototype_version: 3,
      treatment: scenario,
      purpose,
      document: {
        reference,
        version: `DEMO-${version}`,
        ...(selectedDocument ? { content: selectedDocument } : {}),
      },
      faculty_current: !revoked,
      illustrative_history: selectedDocument
        ? "Pendiente de revisión; versión de ensayo"
        : "Requiere cambios; ejemplo precargado",
      contains_user_edits: Boolean(selectedDocument),
      activation: "deshabilitada",
      allows_real_data: false,
      authorizes_action: false,
      persisted_events: 0,
      simulated_document_versions: prepared.length,
    };
    const url = URL.createObjectURL(
      new Blob([JSON.stringify(packet, null, 2)], { type: "application/json" })
    );
    const link = document.createElement("a");
    link.href = url;
    link.download = `maqueta-licitud-${scenario}-${purpose}-v${version}.json`;
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    setNotice(
      selectedDocument
        ? "Versión de ensayo descargada con sus textos ficticios. No es un expediente real."
        : "Ejemplo descargado. No contiene tus textos de ensayo ni es un expediente real."
    );
  }

  return (
    <div className="space-y-5 text-slate-800">
      <header className="space-y-4 rounded-xl border border-blue-200 bg-blue-50 p-5 sm:p-6">
        <div className="flex flex-wrap items-center gap-3">
          <span className="rounded-full bg-blue-800 px-3 py-1 text-xs font-bold text-white">
            MAQUETA NAVEGABLE · VERSIÓN 3
          </span>
          <span className="text-sm font-semibold">EIPD deshabilitada · Solo datos ficticios</span>
        </div>
        <h1 className="text-2xl font-bold text-slate-950">Licitud, paso a paso</h1>
        <p>
          Explora dónde completar datos y dónde revisar documentos. Esta demostración no consulta ni
          modifica tus expedientes.
        </p>
        <p className="text-sm">
          Los cambios se conservan entre pestañas, tratamientos y finalidades durante esta visita.
          Al recargar se reinician. No ingreses datos reales.
        </p>
      </header>

      <details className="rounded-xl border border-slate-300 bg-slate-50 p-4">
        <summary className="cursor-pointer font-semibold">
          Herramientas de demostración · ejemplos opcionales
        </summary>
        <div className="mt-4 space-y-4">
          <p>
            Estos ejemplos solo precargan la selección inicial. No son pasos del flujo ni categorías
            que debas elegir en el producto.
          </p>
          <div className="flex flex-wrap gap-3">
            {(["adultos", "infancia"] as const).map((example) => (
              <button
                key={example}
                type="button"
                className={secondary}
                onClick={() => {
                  setSelectedTreatment(example);
                  setSelectedPurpose(Object.keys(scenarios[example].purposes)[0]);
                  setSelectionOpen(true);
                  setPreview(false);
                }}
              >
                Cargar ejemplo de {example === "adultos" ? "adultos" : "infancia"}
              </button>
            ))}
          </div>
          <label className="block max-w-lg font-medium">
            Facultad simulada de la persona
            <select
              className={input}
              value={revoked ? "revocada" : "vigente"}
              aria-label="Facultad simulada de la persona"
              aria-describedby="prototype-faculty-help"
              onChange={(e) => {
                setRevoked(e.target.value === "revocada");
                setPreview(false);
              }}
            >
              <option value="vigente">Vigente en la demostración</option>
              <option value="revocada">Revocada en la demostración</option>
            </select>
          </label>
          <p id="prototype-faculty-help" aria-live="polite" className="text-sm">
            {revoked
              ? "Revocada: elige esta situación para comprobar el bloqueo de nuevas decisiones de organización. Puedes seguir consultando documentos y preparando observaciones de revisión."
              : "Vigente: elige esta situación para explorar la decisión de organización con una persona facultada en el ejemplo. No significa que el documento esté aceptado."}
          </p>
          <p className="text-sm">
            La facultad es una condición de la persona, no un tipo de tratamiento RAT. Cambiarla no
            cambia los datos seleccionados ni otorga permisos reales.
          </p>
        </div>
      </details>

      {selectionOpen && (
        <Card title="Antes de empezar: selecciona qué vas a evaluar">
          <p>
            Primero elige organización, tratamiento RAT y finalidad. Después recorre los cuatro
            pasos para ese alcance. La maqueta solo ofrece un inventario ficticio.
          </p>
          <p className="text-sm">
            Organización de ejemplo: [FICTICIA] Organización de demostración.
          </p>
          <label className="block font-medium">
            Tratamiento RAT de ejemplo
            <select
              className={input}
              aria-label="Tratamiento RAT de ejemplo"
              aria-describedby="prototype-treatment-help"
              value={selectedTreatment}
              onChange={(e) => {
                setSelectedTreatment(e.target.value as Scenario | "");
                setSelectedPurpose("");
              }}
            >
              <option value="">Selecciona un tratamiento</option>
              {Object.entries(scenarios).map(([key, value]) => (
                <option key={key} value={key}>
                  {value.treatment}
                </option>
              ))}
            </select>
          </label>
          <p id="prototype-treatment-help" aria-live="polite" className="text-sm">
            {!selectedTreatment
              ? "Elige la actividad del RAT que quieres evaluar. Después selecciona para qué se utilizan los datos dentro de esa actividad."
              : selectedTreatment === "adultos"
                ? "Clientes adultos: permite ensayar la gestión de la relación o la atención de consultas con clientes sintéticos. Elige la finalidad concreta a continuación."
                : "Programa de infancia: permite ensayar el caso de cinco participantes sintéticos de 10 a 13 años. Agrega una sección para analizar edad y alcance; no determina una base jurídica."}
          </p>
          <label className="block font-medium">
            Finalidad a evaluar
            <select
              className={input}
              disabled={!selectedTreatment}
              aria-label="Finalidad a evaluar"
              aria-describedby="prototype-purpose-help"
              value={selectedPurpose}
              onChange={(e) => setSelectedPurpose(e.target.value)}
            >
              <option value="">Selecciona una finalidad</option>
              {selectedTreatment &&
                Object.entries(scenarios[selectedTreatment].purposes).map(([key, label]) => (
                  <option key={key} value={key}>
                    {label}
                  </option>
                ))}
            </select>
          </label>
          <p id="prototype-purpose-help" aria-live="polite" className="text-sm">
            {!selectedTreatment
              ? "Primero selecciona un tratamiento para conocer sus finalidades disponibles."
              : !selectedPurpose
                ? "Elige el objetivo concreto que vas a evaluar. Cada finalidad conserva un borrador separado durante esta visita."
                : selectedPurpose === "gestion"
                  ? "Administrar la relación: elige este ejemplo para evaluar el uso de datos en la gestión de clientes adultos sintéticos. Es distinto del objetivo de atender consultas."
                  : selectedPurpose === "consultas"
                    ? "Atender consultas: elige este ejemplo para evaluar el uso de datos al responder consultas de clientes adultos sintéticos. Sus textos se mantienen separados de la gestión de la relación."
                    : "Ensayar el análisis de infancia: elige este objetivo para recorrer el análisis del programa con cinco participantes sintéticos. Completa también la sección Infancia."}
          </p>
          <p className="text-sm">
            Un tratamiento puede tener varias finalidades. Aquí evalúas una por vez; sus textos de
            ensayo se conservan por separado.
          </p>
          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              className={button}
              disabled={!selectedTreatment || !selectedPurpose}
              onClick={() => {
                if (
                  !selectedTreatment ||
                  !Object.hasOwn(scenarios[selectedTreatment].purposes, selectedPurpose)
                )
                  return;
                setScenario(selectedTreatment);
                setPurpose(selectedPurpose);
                setActive(true);
                setSelectionOpen(false);
                setTab("resumen");
                setSection("alcance");
                setVersion("2");
                setPreview(false);
                setPreparationOpen(false);
                setReviewedFingerprint("");
                setNotice("");
                setFacultyOpen(false);
              }}
            >
              Abrir evaluación de ejemplo
            </button>
            {active && (
              <button
                type="button"
                className={secondary}
                onClick={() => {
                  setSelectedTreatment(scenario);
                  setSelectedPurpose(purpose);
                  setSelectionOpen(false);
                }}
              >
                Volver a la evaluación seleccionada
              </button>
            )}
          </div>
        </Card>
      )}

      {active && !selectionOpen && (
        <>
          <aside
            className="space-y-3 rounded-xl border border-blue-200 bg-blue-50 p-4"
            aria-label="Alcance seleccionado"
          >
            <p className="text-xs font-bold uppercase tracking-wide text-blue-800">
              Evaluación sobre el alcance seleccionado
            </p>
            <p className="font-semibold">{current.treatment}</p>
            <p>
              <strong>Finalidad:</strong> {current.purposes[purpose]}
            </p>
            <p className="text-sm">
              Organización ficticia · Evaluación: versión 1 · Borrador de ejemplo. Facultad de la
              persona: {revoked ? "revocada" : "vigente en la demostración"}.
            </p>
            <button
              type="button"
              className={secondary}
              onClick={() => {
                setSelectedTreatment(scenario);
                setSelectedPurpose(purpose);
                setSelectionOpen(true);
                setPreview(false);
              }}
            >
              Cambiar tratamiento o finalidad
            </button>
          </aside>

          <div
            aria-label="Secciones de la maqueta"
            role="tablist"
            className="grid grid-cols-2 gap-2 lg:grid-cols-4"
          >
            {tabs.map(([key, label], index) => (
              <button
                key={key}
                type="button"
                id={`prototype-tab-${key}`}
                role="tab"
                aria-selected={tab === key}
                aria-controls={`prototype-panel-${key}`}
                tabIndex={tab === key ? 0 : -1}
                onClick={() => go(key)}
                onKeyDown={(event) => moveTab(event, index)}
                className={`${tab === key ? "border-blue-800 bg-blue-800 text-white" : "border-slate-300 bg-white text-slate-800 hover:bg-slate-100"} rounded-lg border p-3 text-left text-sm font-semibold focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-800`}
              >
                {label}
              </button>
            ))}
          </div>
          {notice && (
            <p role="status" className="rounded-lg border border-blue-200 bg-blue-50 p-3 text-sm">
              {notice}
            </p>
          )}
          <div
            role="tabpanel"
            id={`prototype-panel-${tab}`}
            aria-labelledby={`prototype-tab-${tab}`}
            tabIndex={0}
            className="space-y-5 focus-visible:outline focus-visible:outline-2 focus-visible:outline-blue-800"
          >
            {tab === "resumen" && (
              <>
                <Card title="Los cuatro pasos de esta evaluación">
                  <p>
                    Completar prepara un borrador. Revisar deja una observación sobre una versión
                    concreta. Avanzar no significa aprobar.
                  </p>
                  <ol
                    className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4"
                    aria-label="Esquema del flujo"
                  >
                    {[
                      [
                        "Revisa el alcance seleccionado",
                        "Finalidad, personas y categorías de datos.",
                        "completar",
                      ],
                      [
                        "Completa la evaluación",
                        adult
                          ? "Base, fundamento y preparación del documento para revisión."
                          : "Fundamento e infancia; después prepara el documento para revisión.",
                        "completar",
                      ],
                      [
                        "Selecciona y revisa",
                        "Lee la versión antes de formular una revisión.",
                        "revisar",
                      ],
                      ["Consulta el resultado", "Historial y descarga del ejemplo.", "historial"],
                    ].map(([title, description, destination], index) => (
                      <li key={title} className="rounded-lg border border-slate-200 p-4">
                        <span className="text-sm font-semibold text-blue-800">
                          Paso {index + 1}
                        </span>
                        <h3 className="my-2 font-semibold">{title}</h3>
                        <p className="mb-3 text-sm">{description}</p>
                        <button
                          type="button"
                          className={secondary}
                          onClick={() => {
                            setSection(index === 0 ? "alcance" : "fundamento");
                            go(destination as Tab);
                          }}
                        >
                          Ir al paso {index + 1}
                        </button>
                      </li>
                    ))}
                  </ol>
                </Card>
                <Card title="Siguiente paso recomendado">
                  <p>
                    {revoked
                      ? "La facultad está revocada. Puedes leer documentos e historial; la decisión de organización está bloqueada."
                      : "Revisa el alcance seleccionado y completa el fundamento pendiente de esta evaluación."}
                  </p>
                  <button
                    type="button"
                    className={button}
                    onClick={() => {
                      setSection("alcance");
                      go(revoked ? "revisar" : "completar");
                    }}
                  >
                    {revoked ? "Consultar documento y bloqueo" : "Comenzar por el alcance"}
                  </button>
                  <dl className="grid gap-3 text-sm sm:grid-cols-2">
                    <div>
                      <dt className="font-semibold">Base de licitud</dt>
                      <dd>Pendiente de evaluación jurídica</dd>
                    </div>
                    <div>
                      <dt className="font-semibold">Infancia</dt>
                      <dd>
                        {adult
                          ? "Fuera del alcance de este ejemplo de adultos"
                          : "Documento de infancia de ejemplo disponible"}
                      </dd>
                    </div>
                    <div>
                      <dt className="font-semibold">Revisión precargada</dt>
                      <dd>Requiere cambios · ejemplo histórico</dd>
                    </div>
                    <div>
                      <dt className="font-semibold">Facultad de organización</dt>
                      <dd>{revoked ? "Revocada" : "Vigente solo en el escenario simulado"}</dd>
                    </div>
                  </dl>
                  <p className="text-sm">
                    El ejemplo no determina si corresponde una EIPD. Su activación permanece
                    deshabilitada.
                  </p>
                </Card>
              </>
            )}

            {tab === "completar" && (
              <Card title="Completar un borrador">
                <p
                  role="status"
                  className={`rounded-lg border p-3 text-sm font-semibold ${dirty ? "border-amber-400 bg-amber-50" : "border-slate-300 bg-slate-50"}`}
                >
                  {dirty
                    ? "Cambios sin guardar en el borrador de ensayo. Se conservan al cambiar de pestaña."
                    : "Borrador de ensayo sin cambios pendientes. Guardado solo durante esta visita."}
                </p>
                <p>
                  Aquí prepara los datos la persona editora. Los documentos registrados se consultan
                  en Revisar documentos.
                </p>
                {draft.origin && (
                  <section
                    className="space-y-3 rounded-lg border border-blue-300 bg-blue-50 p-4"
                    aria-label="Origen y motivo de la nueva versión"
                  >
                    <h3 className="font-semibold">
                      Nueva versión a partir de DEMO-{draft.origin.version}
                    </h3>
                    <p className="break-words">
                      <strong>Versión de origen:</strong> {draft.origin.reference} · DEMO-
                      {draft.origin.version}
                    </p>
                    <p>
                      Se copió el contenido de esa versión, no el último borrador editado. El
                      original no cambia. No necesitas emitir una revisión negativa para justificar
                      una actualización.
                    </p>
                    <label className="block font-medium">
                      Motivo del cambio (obligatorio)
                      <textarea
                        aria-label="Motivo del cambio (obligatorio)"
                        rows={3}
                        className={input}
                        value={draft.changeReason}
                        onChange={(e) => edit("changeReason", e.target.value)}
                      />
                    </label>
                    <p className="text-sm">
                      Explica por qué preparas otra versión. Este motivo quedará junto al contenido
                      registrado; es distinto de las observaciones de la persona revisora.
                    </p>
                  </section>
                )}
                <nav aria-label="Secciones para completar" className="flex flex-wrap gap-2">
                  {sections
                    .filter(([key]) => !adult || key !== "infancia")
                    .map(([key, label], index) => (
                      <button
                        type="button"
                        key={key}
                        aria-current={section === key ? "step" : undefined}
                        className={section === key ? button : secondary}
                        onClick={() => backToEdit(key)}
                      >
                        {index + 1}. {label}
                      </button>
                    ))}
                </nav>
                {!preparationOpen && section === "alcance" && (
                  <section className="space-y-3" aria-label="Alcance del RAT de ejemplo">
                    <h3 className="font-semibold">Alcance asociado · solo lectura</h3>
                    <ul className="list-disc space-y-2 pl-5" aria-label="Resumen del alcance">
                      <li>
                        <strong>Finalidad:</strong> {current.purposes[purpose]}
                      </li>
                      <li>
                        <strong>Titulares:</strong>{" "}
                        {adult
                          ? "clientes adultos sintéticos"
                          : "participantes sintéticos de 10 a 13 años"}
                        .
                      </li>
                      <li>
                        <strong>Categoría:</strong> identificación.
                      </li>
                      <li>
                        <strong>Fuente:</strong> registros generados para el ensayo.
                      </li>
                    </ul>
                    <p className="text-sm">
                      En la aplicación, este resumen mostrará el RAT asociado y las diferencias
                      pendientes. En la maqueta no se edita el inventario.
                    </p>
                    <button
                      type="button"
                      className={button}
                      onClick={() => setSection("fundamento")}
                    >
                      Continuar a base y fundamento
                    </button>
                  </section>
                )}
                {!preparationOpen && section === "fundamento" && (
                  <section className="space-y-4" aria-label="Base y fundamento de ensayo">
                    <h3 className="font-semibold">Base y fundamento</h3>
                    <p className="text-sm">
                      Puedes guardar un borrador con la base pendiente. Este ejemplo no recomienda
                      una base jurídica.
                    </p>
                    <label className="block font-medium">
                      Base propuesta de ensayo
                      <select
                        className={input}
                        value={draft.basis}
                        aria-label="Base propuesta de ensayo"
                        aria-describedby="prototype-basis-help"
                        onChange={(e) => edit("basis", e.target.value)}
                      >
                        <option value="">Pendiente de definir</option>
                        <option value="analisis">Propuesta pendiente de análisis (ejemplo)</option>
                      </select>
                    </label>
                    <p id="prototype-basis-help" aria-live="polite" className="text-sm">
                      {draft.basis
                        ? "Propuesta pendiente de análisis: úsala para ensayar una propuesta que todavía debe justificarse y revisarse. Explica el razonamiento en el fundamento; esta opción ilustrativa no identifica ni valida una base jurídica concreta."
                        : "Pendiente de definir: mantenla cuando aún no tengas una propuesta de base para este tratamiento y finalidad. Puedes preparar el documento dejando ese punto declarado como pendiente."}
                    </p>
                    <label className="block font-medium">
                      Fundamento de ensayo
                      <textarea
                        rows={4}
                        className={input}
                        aria-label="Fundamento de ensayo"
                        value={draft.rationale}
                        onChange={(e) => edit("rationale", e.target.value)}
                      />
                    </label>
                  </section>
                )}
                {!preparationOpen && section === "infancia" && !adult && (
                  <section className="space-y-4" aria-label="Infancia de ensayo">
                    <h3 className="font-semibold">Infancia y adolescencia</h3>
                    <p className="text-sm">
                      Sección ilustrativa para este escenario, no una determinación legal. En la
                      aplicación se contrastará con el alcance del RAT.
                    </p>
                    <label className="block font-medium">
                      Análisis de edad y alcance de ensayo
                      <textarea
                        rows={4}
                        className={input}
                        aria-label="Análisis de edad y alcance de ensayo"
                        value={draft.age}
                        onChange={(e) => edit("age", e.target.value)}
                      />
                    </label>
                    <p>
                      Interés superior, autonomía y autorización: pendientes de revisión en el
                      ejemplo.
                    </p>
                  </section>
                )}
                {!preparationOpen && (
                  <div className="flex flex-wrap gap-3 border-t border-slate-200 pt-4">
                    <button
                      type="button"
                      className={secondary}
                      onClick={() => {
                        setSaved((all) => ({ ...all, [scopeKey]: { ...draft } }));
                        setNotice(
                          "Guardado simulado del borrador en esta visita. No se guardó en el servidor; al recargar se reinicia."
                        );
                      }}
                    >
                      Guardar borrador de ensayo
                    </button>
                    <button type="button" className={button} onClick={openPreparation}>
                      Preparar documento para revisión
                    </button>
                  </div>
                )}
                {preparationOpen && (
                  <section
                    className="space-y-5 rounded-lg border border-blue-300 bg-blue-50 p-4"
                    aria-label="Preparación documental"
                  >
                    <h3 className="text-lg font-semibold">
                      Vista previa del documento para revisión
                    </h3>
                    <p className="break-words font-semibold">
                      Se prepararía: {candidate.reference} · versión {nextVersion} · DEMO-
                      {nextVersion}
                    </p>
                    <p>
                      Revisa el contenido como responsable ficticio del ensayo. Puedes volver a
                      editar antes de registrar. Los faltantes se conservan como pendientes; no
                      equivalen a una evaluación aprobada.
                    </p>
                    <label className="block font-medium">
                      Notas específicas del documento (opcional)
                      <textarea
                        aria-label="Notas específicas del documento (opcional)"
                        className={input}
                        rows={3}
                        value={draft.notes}
                        onChange={(e) => edit("notes", e.target.value)}
                      />
                    </label>
                    <article
                      aria-label="Contenido que se prepararía"
                      className="rounded-lg border border-slate-200 bg-white p-4"
                    >
                      <DocumentContent document={candidate} />
                    </article>
                    <section
                      aria-label="Faltantes del documento"
                      className="space-y-2 rounded-lg border border-amber-300 bg-amber-50 p-4"
                    >
                      <h4 className="font-semibold">
                        Faltantes y pendientes declarados del ejemplo
                      </h4>
                      <ul className="list-disc space-y-2 pl-5">
                        {candidate.pending.map((item) => (
                          <li key={item}>{item}</li>
                        ))}
                      </ul>
                    </section>
                    <div className="flex flex-wrap gap-3">
                      <button
                        type="button"
                        className={secondary}
                        onClick={() => backToEdit("fundamento")}
                      >
                        Volver a base y fundamento
                      </button>
                      {!adult && (
                        <button
                          type="button"
                          className={secondary}
                          onClick={() => backToEdit("infancia")}
                        >
                          Volver a infancia
                        </button>
                      )}
                      <button
                        type="button"
                        className={secondary}
                        onClick={() => backToEdit("alcance")}
                      >
                        Volver al alcance
                      </button>
                    </div>
                    <label className="flex items-start gap-2 font-medium">
                      <input
                        type="checkbox"
                        className="mt-1"
                        checked={reviewed}
                        onChange={(e) =>
                          setReviewedFingerprint(e.target.checked ? fingerprint : "")
                        }
                      />
                      He revisado esta vista previa como responsable ficticio del ensayo
                    </label>
                    <p className="text-sm">
                      Esta declaración solo confirma la lectura del ensayo. No otorga facultades ni
                      acepta jurídicamente el documento. Al modificar contenido se debe revisar otra
                      vez.
                    </p>
                    <button
                      type="button"
                      className={button}
                      disabled={!reviewed || missingChangeReason}
                      onClick={registerDocument}
                    >
                      Simular registro de versión DEMO-{nextVersion}
                    </button>
                    {missingChangeReason && (
                      <p className="font-semibold text-amber-900">
                        Para registrar esta nueva versión, vuelve a completar el motivo del cambio.
                      </p>
                    )}
                    <p className="text-sm">
                      Se conservará todo el contenido mostrado en esta visita, separado del borrador
                      editable. No se envía al servidor; al recargar se pierde. Los cambios
                      posteriores se registran en otra versión.
                    </p>
                  </section>
                )}
              </Card>
            )}

            {tab === "revisar" && (
              <>
                <Card title="Elegir documento y versión">
                  <p>
                    Primero lee el documento. Después elige entre revisión del documento y decisión
                    de la organización.
                  </p>
                  <label className="block max-w-lg font-medium">
                    Versión a consultar
                    <select
                      className={input}
                      value={version}
                      aria-label="Versión a consultar"
                      aria-describedby="prototype-version-help"
                      onChange={(e) => {
                        setVersion(e.target.value);
                        setCopyRequest(null);
                        setPreview(false);
                        setPreparationOpen(false);
                        setReviewedFingerprint("");
                      }}
                    >
                      {[...prepared].reverse().map((document) => (
                        <option key={document.version} value={document.version}>
                          Versión {document.version} · DEMO-{document.version} · Pendiente de
                          revisión (ensayo)
                        </option>
                      ))}
                      <option value="2">Versión 2 · DEMO-2 · Requiere cambios</option>
                      <option value="1">Versión 1 · DEMO-1 · Histórica</option>
                    </select>
                  </label>
                  <p id="prototype-version-help" aria-live="polite" className="text-sm">
                    {selectedDocument
                      ? `DEMO-${version}: versión creada durante esta visita, pendiente de revisión. Consúltala para comprobar el contenido registrado. Las observaciones y la descarga corresponden a esta selección; editar requiere crear otra versión.`
                      : version === "1"
                        ? "DEMO-1: ejemplo histórico precargado. Elígelo para consultar el contenido anterior o usarlo como origen de otra versión. La descarga y las observaciones corresponden a DEMO-1."
                        : "DEMO-2: segundo ejemplo precargado, con Requiere cambios en su historial. Elígelo para consultar esa versión o preparar otra a partir de ella. La descarga y las observaciones corresponden a DEMO-2."}
                  </p>
                  <article
                    className="space-y-3 rounded-lg border-l-4 border-blue-800 bg-blue-50 p-4"
                    aria-label="Documento seleccionado"
                  >
                    <h3 className="font-semibold">
                      {documentName} · versión {version}
                    </h3>
                    <p className="break-words font-semibold">
                      {reference} · Etiqueta documental: DEMO-{version}
                    </p>
                    <p>Evaluación asociada: versión 1. {current.purposes[purpose]}</p>
                    {selectedDocument ? (
                      <>
                        <p className="font-semibold">
                          Versión de ensayo registrada en esta visita · pendiente de revisión.
                        </p>
                        <DocumentContent document={selectedDocument} />
                        <h4 className="font-semibold">Pendientes conservados al registrar</h4>
                        <ul className="list-disc space-y-2 pl-5">
                          {selectedDocument.pending.map((item) => (
                            <li key={item}>{item}</li>
                          ))}
                        </ul>
                        <p>
                          Este contenido se conserva sin cambios durante la visita. Editar el
                          borrador no modifica esta versión.
                        </p>
                      </>
                    ) : (
                      <>
                        <p>
                          Contenido de ejemplo registrado: análisis y evidencias pendientes.{" "}
                          {adult
                            ? "Solo clientes adultos sintéticos."
                            : "Solo participantes sintéticos; sin datos sensibles."}
                        </p>
                        <p className="text-sm">
                          Ejemplo precargado: el contenido que se copiará se detalla a continuación.
                          Tus textos nuevos se incorporan solo a versiones que prepares y registres.
                        </p>
                        <DocumentContent document={sourceDocument} />
                      </>
                    )}
                  </article>
                  <button type="button" className={secondary} onClick={startCopy}>
                    Crear nueva versión a partir de DEMO-{version}
                  </button>
                  {copyRequest?.scopeKey === scopeKey && (
                    <aside
                      role="alertdialog"
                      aria-label="Confirmar reemplazo del borrador"
                      aria-describedby="prototype-copy-warning"
                      className="space-y-3 rounded-lg border border-amber-400 bg-amber-50 p-4"
                    >
                      <h3 className="font-semibold">
                        Hay cambios sin guardar en el borrador actual
                      </h3>
                      <p id="prototype-copy-warning">
                        Copiar DEMO-{copyRequest.document.version} reemplazará esos cambios en este
                        tratamiento y finalidad. Las versiones registradas se conservan.
                      </p>
                      <div className="flex flex-wrap gap-3">
                        <button
                          type="button"
                          className={button}
                          onClick={() => copyVersion(copyRequest.document)}
                        >
                          Reemplazar borrador y copiar DEMO-{copyRequest.document.version}
                        </button>
                        <button
                          type="button"
                          className={secondary}
                          onClick={() => setCopyRequest(null)}
                        >
                          Conservar borrador actual
                        </button>
                      </div>
                    </aside>
                  )}
                </Card>
                <Card
                  title={
                    review.kind === "revision"
                      ? `Emitir revisión sobre DEMO-${version}`
                      : `Emitir decisión de organización sobre DEMO-${version}`
                  }
                >
                  <p>
                    Esta sección recoge observaciones o decisiones sobre el documento ya registrado.
                    No modifica su contenido ni explica los cambios de una nueva versión; ese motivo
                    se completa al iniciar su edición.
                  </p>
                  <label className="block font-medium">
                    Tipo de actuación
                    <select
                      className={input}
                      value={review.kind}
                      aria-label="Tipo de actuación"
                      aria-describedby="prototype-action-help"
                      onChange={(e) =>
                        changeReview({ kind: e.target.value as ReviewDraft["kind"], choice: "" })
                      }
                    >
                      <option value="revision">Revisión del documento</option>
                      <option value="decision">Decisión documental de organización</option>
                    </select>
                  </label>
                  <p id="prototype-action-help" aria-live="polite" className="text-sm">
                    {review.kind === "revision"
                      ? "Revisión del documento: elige esta opción para señalar faltantes, pedir correcciones o recomendar no continuar sobre la versión seleccionada. No modifica el documento ni expresa una decisión de la organización."
                      : "Decisión documental de organización: elige esta opción para expresar la posición de la organización sobre la versión seleccionada. Requiere una persona con facultad vigente. En esta maqueta solo se previsualiza Requiere cambios; no hay aceptación jurídica ni activación EIPD."}
                  </p>
                  <div className="flex flex-wrap items-center gap-3 rounded-lg bg-slate-100 p-3">
                    <p className="text-sm font-semibold">
                      Facultad:{" "}
                      {revoked
                        ? "revocada; decisión de organización bloqueada"
                        : "vigente en este ejemplo ficticio"}
                      .
                    </p>
                    <button
                      type="button"
                      className={secondary}
                      aria-expanded={facultyOpen}
                      aria-controls="prototype-faculty"
                      onClick={() => setFacultyOpen(!facultyOpen)}
                    >
                      Ver gestión de facultades
                    </button>
                  </div>
                  {facultyOpen && (
                    <aside
                      id="prototype-faculty"
                      className="space-y-2 rounded-lg border border-slate-300 p-4"
                      aria-label="Gestión de facultades de ejemplo"
                    >
                      <h3 className="font-semibold">Gestión separada · administración</h3>
                      <p>
                        Otorgar o revocar corresponde a una gestión distinta de revisar. En esta
                        maqueta solo se muestra el historial precargado.
                      </p>
                      <p>
                        Ejemplo: revisión de facultad 1, otorgada.
                        {revoked && " Revisión de facultad 2, revocada."}
                      </p>
                      <p className="text-sm">
                        Cambiar escenario permite explorar otra situación; no otorga facultades
                        reales.
                      </p>
                    </aside>
                  )}
                  {review.kind === "decision" && (
                    <p
                      id="prototype-block"
                      className="rounded-lg border border-amber-300 bg-amber-50 p-3"
                    >
                      {revoked
                        ? "No puedes emitir una decisión de organización: la facultad está revocada. La decisión anterior y el historial siguen disponibles."
                        : "En esta maqueta puedes previsualizar Requiere cambios. No se registra una aceptación ni se habilitan decisiones reales."}
                    </p>
                  )}
                  <fieldset
                    disabled={review.kind === "decision" && revoked}
                    aria-describedby={review.kind === "decision" ? "prototype-block" : undefined}
                    className="space-y-4 disabled:opacity-60"
                  >
                    <legend className="mb-2 font-semibold">
                      {review.kind === "revision"
                        ? "Observación de revisión"
                        : "Decisión de organización de ensayo"}
                    </legend>
                    <label className="block font-medium">
                      Resultado de ensayo
                      <select
                        className={input}
                        value={review.choice}
                        aria-label="Resultado de ensayo"
                        aria-describedby="prototype-result-help"
                        onChange={(e) => changeReview({ choice: e.target.value })}
                      >
                        <option value="">Selecciona un resultado</option>
                        <option value="requiere_cambios">Requiere cambios</option>
                        {review.kind === "revision" && (
                          <option value="no_continuar">No continuar</option>
                        )}
                      </select>
                    </label>
                    <p id="prototype-result-help" aria-live="polite" className="text-sm">
                      {!review.choice
                        ? "Selecciona el resultado que describa tu conclusión. Después explica los motivos y los puntos concretos que deben atenderse en el fundamento."
                        : review.choice === "no_continuar"
                          ? "No continuar: úsalo cuando tu conclusión sea recomendar que no se siga adelante con lo planteado en esta versión. Explica las razones en el fundamento. La vista previa no detiene procesos automáticamente ni borra el documento."
                          : review.kind === "decision"
                            ? "Requiere cambios: expresa que la organización solicita ajustes a esta versión antes de volver a considerarla. Indica cuáles y por qué. En la maqueta es una vista previa; no registra una decisión ni autoriza operar."
                            : "Requiere cambios: úsalo cuando identifiques faltantes o aspectos que deben corregirse antes de otra revisión. Detalla cuáles y por qué. Para modificar el contenido se crea una nueva versión; esta observación conserva intacta la versión revisada."}
                    </p>
                    <label className="block font-medium">
                      Fundamento de revisión de ensayo
                      <textarea
                        rows={3}
                        className={input}
                        value={review.rationale}
                        onChange={(e) => changeReview({ rationale: e.target.value })}
                      />
                    </label>
                    <p className="break-words text-sm font-semibold">
                      Actuarías sobre: {reference} · versión {version} · DEMO-{version}
                    </p>
                    <button
                      type="button"
                      className={button}
                      disabled={!review.choice || !review.rationale.trim()}
                      onClick={() => setPreview(true)}
                    >
                      Previsualizar {review.kind === "revision" ? "revisión" : "decisión"} · versión{" "}
                      {version}
                    </button>
                  </fieldset>
                  {preview && !(revoked && review.kind === "decision") && (
                    <aside
                      role="note"
                      aria-label="Vista previa sin registro"
                      className="space-y-2 rounded-lg border border-blue-300 bg-blue-50 p-4"
                    >
                      <h3 className="font-semibold">Vista previa · no se ha registrado</h3>
                      <p>
                        {reference} · versión {version} ·{" "}
                        {review.choice === "requiere_cambios" ? "Requiere cambios" : "No continuar"}
                      </p>
                      <p className="whitespace-pre-wrap break-words">{review.rationale}</p>
                      <p>
                        La maqueta termina aquí esta actuación. No crea eventos ni cambia el
                        historial.
                      </p>
                      <button type="button" className={secondary} onClick={() => go("historial")}>
                        Consultar historial de ejemplo
                      </button>
                    </aside>
                  )}
                </Card>
              </>
            )}

            {tab === "historial" && (
              <Card title="Historial y descargas de ejemplo">
                <p>
                  Consulta versiones precargadas y las que prepares en esta visita. Las nuevas
                  versiones conservan el contenido revisado sin modificar las anteriores.
                </p>
                <ol className="space-y-3" aria-label="Historial documental de ensayo">
                  <li
                    aria-current={version === "1" ? "true" : undefined}
                    className={`rounded-lg border p-4 ${version === "1" ? "border-blue-300 bg-blue-50" : "border-slate-200 bg-white"}`}
                  >
                    <h3 className="font-semibold">Versión 1 · DEMO-1</h3>
                    {version === "1" && <p className="font-semibold">Seleccionada para descarga</p>}
                    <p>Documento original de ejemplo. Revisión: requiere cambios.</p>
                    <button
                      type="button"
                      className={`${secondary} mt-3`}
                      onClick={() => {
                        setVersion("1");
                        go("revisar");
                      }}
                    >
                      Consultar versión 1
                    </button>
                  </li>
                  <li
                    aria-current={version === "2" ? "true" : undefined}
                    className={`rounded-lg border p-4 ${version === "2" ? "border-blue-300 bg-blue-50" : "border-slate-200 bg-white"}`}
                  >
                    <h3 className="font-semibold">Versión 2 · DEMO-2</h3>
                    {version === "2" && <p className="font-semibold">Seleccionada para descarga</p>}
                    <p>
                      Segunda versión de ejemplo. Decisión documental precargada: requiere cambios.
                    </p>
                    <p>
                      Facultad actual: {revoked ? "revocada" : "vigente en el escenario simulado"}.
                      El registro anterior se conserva.
                    </p>
                    <button
                      type="button"
                      className={`${secondary} mt-3`}
                      onClick={() => {
                        setVersion("2");
                        go("revisar");
                      }}
                    >
                      Consultar versión 2
                    </button>
                  </li>
                  {prepared.map((document) => (
                    <li
                      key={document.version}
                      aria-current={version === document.version ? "true" : undefined}
                      className={`space-y-2 rounded-lg border p-4 ${version === document.version ? "border-blue-300 bg-blue-50" : "border-slate-200 bg-white"}`}
                    >
                      <h3 className="font-semibold">
                        Versión {document.version} · DEMO-{document.version}
                      </h3>
                      {version === document.version && (
                        <p className="font-semibold">Seleccionada para descarga</p>
                      )}
                      <p className="break-words">
                        {document.reference} · Registrada solo durante esta visita · Pendiente de
                        revisión.
                      </p>
                      <p>
                        {document.pending.length} pendientes declarados; sin aprobación jurídica ni
                        activación EIPD.
                      </p>
                      <button
                        type="button"
                        className={secondary}
                        onClick={() => {
                          setVersion(document.version);
                          go("revisar");
                        }}
                      >
                        Consultar versión {document.version}
                      </button>
                    </li>
                  ))}
                  {revoked && (
                    <li className="rounded-lg border border-amber-300 bg-amber-50 p-4">
                      Facultad revocada · revisión 2. Las nuevas decisiones de organización están
                      bloqueadas; el historial sigue disponible.
                    </li>
                  )}
                </ol>
                <p className="text-sm">
                  {selectedDocument
                    ? `La descarga de DEMO-${version} incluye todo el contenido ficticio de esa versión registrada, incluidos los textos del ensayo. No incluye modificaciones posteriores del borrador.`
                    : `La descarga de DEMO-${version} contiene solo el ejemplo precargado; no incluye tus textos de ensayo.`}{" "}
                  No es un expediente real.
                </p>
                <button type="button" className={button} onClick={download}>
                  Descargar ejemplo ficticio JSON
                </button>
                <details className="rounded-lg border border-slate-200 p-3">
                  <summary className="cursor-pointer font-medium">
                    Qué validar en esta maqueta
                  </summary>
                  <ul className="mt-3 list-disc space-y-2 pl-5">
                    <li>¿Distingues dónde completar y dónde revisar?</li>
                    <li>¿Se reconoce la versión sobre la que actuarías?</li>
                    <li>¿Se entiende el motivo de un bloqueo y cómo consultar el historial?</li>
                    <li>¿Los siguientes pasos y los botones permiten continuar sin ayuda?</li>
                  </ul>
                </details>
              </Card>
            )}
          </div>
        </>
      )}
      <footer className="border-t border-slate-200 pt-4 text-sm">
        Maqueta aislada · sin registro en servidor · sin datos reales · no confirma ni activa EIPD.
      </footer>
    </div>
  );
}
