"use client";

import { useEffect, useState, type KeyboardEvent, type ReactNode } from "react";

const tabs = [
  ["resumen", "Resumen y siguientes pasos"],
  ["completar", "Completar datos"],
  ["revisar", "Revisar documentos"],
  ["historial", "Historial y descargas"],
] as const;
type Tab = (typeof tabs)[number][0];
type Scenario = "adultos" | "infancia" | "revocada";
type Section = "alcance" | "fundamento" | "infancia" | "documento";
const scenarios: Record<Scenario, { label: string; treatment: string; purpose: string }> = {
  adultos: {
    label: "Adultos",
    treatment: "[FICTICIA] Gestión de clientes adultos",
    purpose: "Ensayar una evaluación para clientes adultos con registros sintéticos.",
  },
  infancia: {
    label: "Infancia",
    treatment: "[FICTICIA] Programa con participantes de 10 a 13 años",
    purpose: "Ensayar el análisis de infancia con cinco participantes sintéticos.",
  },
  revocada: {
    label: "Facultad revocada",
    treatment: "[FICTICIA] Programa con participantes de 10 a 13 años",
    purpose: "Consultar la documentación de infancia después de revocar una facultad ficticia.",
  },
};
const sections: [Section, string][] = [
  ["alcance", "1. Alcance del RAT"],
  ["fundamento", "2. Base y fundamento"],
  ["infancia", "3. Infancia"],
  ["documento", "4. Preparar documento"],
];
type Draft = { basis: string; rationale: string; age: string; notes: string };
type ReviewDraft = { kind: "revision" | "decision"; choice: string; rationale: string };
const initialDraft = (scenario: Scenario): Draft => ({
  basis: "",
  rationale: "[FICTICIA] Evaluación pendiente. No hay autorización para operar.",
  age: scenario === "adultos" ? "" : "[FICTICIA] Cinco participantes sintéticos de 10 a 13 años.",
  notes: "[FICTICIA] Documento de ensayo; análisis y evidencias pendientes.",
});
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
  const [tab, setTab] = useState<Tab>("resumen");
  const [section, setSection] = useState<Section>("alcance");
  const [version, setVersion] = useState("2");
  const [ready, setReady] = useState(false);
  const [drafts, setDrafts] = useState<Record<Scenario, Draft>>({
    adultos: initialDraft("adultos"),
    infancia: initialDraft("infancia"),
    revocada: initialDraft("revocada"),
  });
  const [saved, setSaved] = useState<Record<Scenario, Draft>>({
    adultos: initialDraft("adultos"),
    infancia: initialDraft("infancia"),
    revocada: initialDraft("revocada"),
  });
  const [reviews, setReviews] = useState<Record<string, ReviewDraft>>({});
  const [notice, setNotice] = useState("");
  const [facultyOpen, setFacultyOpen] = useState(false);
  const [preview, setPreview] = useState(false);
  const [copied, setCopied] = useState(false);
  const current = scenarios[scenario];
  const draft = drafts[scenario];
  const dirty = JSON.stringify(draft) !== JSON.stringify(saved[scenario]);
  const reviewKey = `${scenario}:${version}`;
  const review = reviews[reviewKey] ?? emptyReview();
  const revoked = scenario === "revocada";
  const adult = scenario === "adultos";
  const documentName = adult
    ? "Documento de evaluación de licitud"
    : "Resolución documental de infancia";
  const reference = `SIMULADA-${adult ? "ADULTOS" : "INFANCIA"}-00${version}`;

  useEffect(() => {
    const readLocation = () => {
      const params = new URLSearchParams(window.location.hash.slice(1));
      const target = params.get("escenario");
      const destination = params.get("pestana");
      if (target && Object.hasOwn(scenarios, target)) setScenario(target as Scenario);
      if (tabs.some(([key]) => key === destination)) setTab(destination as Tab);
      if (["1", "2"].includes(params.get("version") ?? "")) setVersion(params.get("version")!);
      setPreview(false);
    };
    readLocation();
    setReady(true);
    window.addEventListener("hashchange", readLocation);
    return () => window.removeEventListener("hashchange", readLocation);
  }, []);
  useEffect(() => {
    if (!ready) return;
    const params = new URLSearchParams({ escenario: scenario, pestana: tab, version });
    window.history.replaceState(null, "", `#${params}`);
  }, [scenario, tab, version, ready]);

  function go(target: Tab) {
    setTab(target);
    setPreview(false);
  }
  function edit(key: keyof Draft, value: string) {
    setDrafts((all) => ({ ...all, [scenario]: { ...all[scenario], [key]: value } }));
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
      source: "fixture_demostrativa",
      scenario,
      document: { reference, version: `DEMO-${version}` },
      faculty_current: !revoked,
      illustrative_history: "Requiere cambios; ejemplo precargado",
      contains_user_edits: false,
      activation: "deshabilitada",
      allows_real_data: false,
      authorizes_action: false,
      persisted_events: 0,
    };
    const url = URL.createObjectURL(
      new Blob([JSON.stringify(packet, null, 2)], { type: "application/json" })
    );
    const link = document.createElement("a");
    link.href = url;
    link.download = `maqueta-licitud-${scenario}-v${version}.json`;
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    setNotice("Ejemplo descargado. No contiene tus textos de ensayo ni es un expediente real.");
  }

  return (
    <div className="space-y-5 text-slate-800">
      <header className="space-y-4 rounded-xl border border-blue-200 bg-blue-50 p-5 sm:p-6">
        <div className="flex flex-wrap items-center gap-3">
          <span className="rounded-full bg-blue-800 px-3 py-1 text-xs font-bold text-white">
            MAQUETA NAVEGABLE
          </span>
          <span className="text-sm font-semibold">EIPD deshabilitada · Solo datos ficticios</span>
        </div>
        <h1 className="text-2xl font-bold text-slate-950">Licitud, paso a paso</h1>
        <p>
          Explora dónde completar datos y dónde revisar documentos. Esta demostración no consulta ni
          modifica tus expedientes.
        </p>
        <p className="text-sm">
          Los cambios se conservan entre pestañas y escenarios durante esta visita. Al recargar se
          reinician. No ingreses datos reales.
        </p>
        <label className="block max-w-md font-medium">
          Escenario de prueba
          <select
            className={input}
            value={scenario}
            onChange={(event) => {
              setScenario(event.target.value as Scenario);
              setSection("alcance");
              setNotice("");
              setPreview(false);
              setFacultyOpen(false);
              setCopied(false);
            }}
          >
            {Object.entries(scenarios).map(([key, value]) => (
              <option key={key} value={key}>
                {value.label}
              </option>
            ))}
          </select>
        </label>
        <p className="font-semibold">{current.treatment}</p>
        <p className="text-sm">
          Organización: [FICTICIA] Organización de demostración · Evaluación: versión 1 · Estado:
          borrador de ejemplo
        </p>
      </header>

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
      <div role="status" aria-live="polite" className="text-sm">
        {dirty
          ? "Cambios sin guardar en el borrador de ensayo. Se conservan al cambiar de pestaña."
          : "Borrador de ejemplo disponible; sin cambios pendientes de ensayo."}
        {notice && (
          <p className="mt-2 rounded-lg border border-blue-200 bg-blue-50 p-3">{notice}</p>
        )}
      </div>
      <div
        role="tabpanel"
        id={`prototype-panel-${tab}`}
        aria-labelledby={`prototype-tab-${tab}`}
        tabIndex={0}
        className="space-y-5 focus-visible:outline focus-visible:outline-2 focus-visible:outline-blue-800"
      >
        {tab === "resumen" && (
          <>
            <Card title="Tu recorrido">
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
                    "Revisa el alcance RAT",
                    "Finalidad, personas y categorías de datos.",
                    "completar",
                  ],
                  [
                    "Completa la evaluación",
                    adult
                      ? "Base propuesta y fundamento."
                      : "Fundamento, infancia y documento de ensayo.",
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
                    <span className="text-sm font-semibold text-blue-800">Paso {index + 1}</span>
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
                  : "Revisa el alcance y completa el fundamento pendiente de la evaluación de ejemplo."}
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
            <p>
              Aquí prepara los datos la persona editora. Los documentos registrados se consultan en
              Revisar documentos.
            </p>
            <nav aria-label="Secciones para completar" className="flex flex-wrap gap-2">
              {sections
                .filter(([key]) => !adult || key !== "infancia")
                .map(([key, label], index) => (
                  <button
                    type="button"
                    key={key}
                    aria-current={section === key ? "step" : undefined}
                    className={section === key ? button : secondary}
                    onClick={() => setSection(key)}
                  >
                    {label}
                  </button>
                ))}
            </nav>
            {section === "alcance" && (
              <section className="space-y-3" aria-label="Alcance del RAT de ejemplo">
                <h3 className="font-semibold">Alcance asociado · solo lectura</h3>
                <p>{current.purpose}</p>
                <p>
                  Titulares:{" "}
                  {adult
                    ? "clientes adultos sintéticos"
                    : "participantes sintéticos de 10 a 13 años"}
                  . Categoría: identificación. Fuente: registros generados para el ensayo.
                </p>
                <p className="text-sm">
                  En la aplicación, este resumen mostrará el RAT asociado y las diferencias
                  pendientes. En la maqueta no se edita el inventario.
                </p>
                <button type="button" className={button} onClick={() => setSection("fundamento")}>
                  Continuar a base y fundamento
                </button>
              </section>
            )}
            {section === "fundamento" && (
              <section className="space-y-4" aria-label="Base y fundamento de ensayo">
                <h3 className="font-semibold">Base y fundamento</h3>
                <p className="text-sm">
                  Puedes guardar un borrador con la base pendiente. Este ejemplo no recomienda una
                  base jurídica.
                </p>
                <label className="block font-medium">
                  Base propuesta de ensayo
                  <select
                    className={input}
                    value={draft.basis}
                    onChange={(e) => edit("basis", e.target.value)}
                  >
                    <option value="">Pendiente de definir</option>
                    <option value="analisis">Propuesta pendiente de análisis (ejemplo)</option>
                  </select>
                </label>
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
            {section === "infancia" && !adult && (
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
                  Interés superior, autonomía y autorización: pendientes de revisión en el ejemplo.
                </p>
              </section>
            )}
            {section === "documento" && (
              <section className="space-y-4" aria-label="Preparar documento de ensayo">
                <h3 className="font-semibold">Preparar documento de ensayo</h3>
                <p>
                  {copied
                    ? `Copia de ${reference} preparada para explorar la edición. El original permanece intacto.`
                    : "Prepara un borrador; registrar una versión definitiva será una acción distinta en la aplicación."}
                </p>
                <label className="block font-medium">
                  Notas del documento de ensayo
                  <textarea
                    rows={4}
                    className={input}
                    aria-label="Notas del documento de ensayo"
                    value={draft.notes}
                    onChange={(e) => edit("notes", e.target.value)}
                  />
                </label>
                <p className="text-sm">
                  No se crea ninguna resolución ni se modifica una versión registrada desde esta
                  maqueta.
                </p>
              </section>
            )}
            <div className="flex flex-wrap gap-3 border-t border-slate-200 pt-4">
              <button
                type="button"
                className={button}
                onClick={() => {
                  setSaved((all) => ({ ...all, [scenario]: { ...draft } }));
                  setNotice(
                    "Guardado simulado en esta visita. No se guardó en el servidor; al recargar se reinicia."
                  );
                  const applicable = sections.filter(([key]) => !adult || key !== "infancia");
                  const index = applicable.findIndex(([key]) => key === section);
                  if (index < applicable.length - 1) setSection(applicable[index + 1][0]);
                  else go("revisar");
                }}
              >
                Simular guardado y continuar
              </button>
              <button type="button" className={secondary} onClick={() => go("revisar")}>
                Explorar revisión sin guardar
              </button>
            </div>
          </Card>
        )}

        {tab === "revisar" && (
          <>
            <Card title="Elegir documento y versión">
              <p>
                Primero lee el documento. Después elige entre revisión del documento y decisión de
                la organización.
              </p>
              <label className="block max-w-lg font-medium">
                Versión a consultar
                <select
                  className={input}
                  value={version}
                  onChange={(e) => {
                    setVersion(e.target.value);
                    setPreview(false);
                    setCopied(false);
                  }}
                >
                  <option value="2">Versión 2 · DEMO-2 · Requiere cambios</option>
                  <option value="1">Versión 1 · DEMO-1 · Histórica</option>
                </select>
              </label>
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
                <p>Evaluación asociada: versión 1. {current.purpose}</p>
                <p>
                  Contenido de ejemplo registrado: análisis y evidencias pendientes.{" "}
                  {adult
                    ? "Solo clientes adultos sintéticos."
                    : "Solo participantes sintéticos; sin datos sensibles."}
                </p>
                <p className="text-sm">
                  Esta lectura conserva el original. Tus textos de ensayo no se incorporan a este
                  documento.
                </p>
              </article>
              <button
                type="button"
                className={secondary}
                onClick={() => {
                  setCopied(true);
                  setSection("documento");
                  go("completar");
                  setNotice(`Copia de ${reference} preparada. No se registró una versión nueva.`);
                }}
              >
                Preparar otra versión en Completar datos
              </button>
            </Card>
            <Card title="Revisar la versión seleccionada">
              <label className="block font-medium">
                Tipo de actuación
                <select
                  className={input}
                  value={review.kind}
                  onChange={(e) =>
                    changeReview({ kind: e.target.value as ReviewDraft["kind"], choice: "" })
                  }
                >
                  <option value="revision">Revisión del documento</option>
                  <option value="decision">Decisión documental de organización</option>
                </select>
              </label>
              <p>
                {review.kind === "revision"
                  ? "La persona revisora documenta observaciones. Las opciones actuales son Requiere cambios y No continuar."
                  : "La decisión de organización requiere una facultad vigente. Es distinta de la revisión del documento."}
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
                    Otorgar o revocar corresponde a una gestión distinta de revisar. En esta maqueta
                    solo se muestra el historial precargado.
                  </p>
                  <p>
                    Ejemplo: revisión de facultad 1, otorgada.
                    {revoked && " Revisión de facultad 2, revocada."}
                  </p>
                  <p className="text-sm">
                    Cambiar escenario permite explorar otra situación; no otorga facultades reales.
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
                    onChange={(e) => changeReview({ choice: e.target.value })}
                  >
                    <option value="">Selecciona un resultado</option>
                    <option value="requiere_cambios">Requiere cambios</option>
                    {review.kind === "revision" && (
                      <option value="no_continuar">No continuar</option>
                    )}
                  </select>
                </label>
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
                    La maqueta termina aquí esta actuación. No crea eventos ni cambia el historial.
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
              Consulta lo registrado sin mezclarlo con el borrador editable. Todos los registros
              siguientes son ejemplos precargados.
            </p>
            <ol className="space-y-3" aria-label="Historial precargado">
              <li className="rounded-lg border border-slate-200 p-4">
                <h3 className="font-semibold">Versión 1 · DEMO-1</h3>
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
              <li className="rounded-lg border border-slate-200 p-4">
                <h3 className="font-semibold">Versión 2 · DEMO-2</h3>
                <p>Segunda versión de ejemplo. Decisión documental precargada: requiere cambios.</p>
                <p>
                  Facultad actual: {revoked ? "revocada" : "vigente en el escenario simulado"}. El
                  registro anterior se conserva.
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
              {revoked && (
                <li className="rounded-lg border border-amber-300 bg-amber-50 p-4">
                  Facultad revocada · revisión 2. Las nuevas decisiones de organización están
                  bloqueadas; el historial sigue disponible.
                </li>
              )}
            </ol>
            <p className="text-sm">
              La descarga contiene únicamente el escenario y la versión seleccionada ({version});
              excluye los textos que escribiste. No es el expediente documental de la aplicación.
            </p>
            <button type="button" className={button} onClick={download}>
              Descargar ejemplo ficticio JSON
            </button>
            <details className="rounded-lg border border-slate-200 p-3">
              <summary className="cursor-pointer font-medium">Qué validar en esta maqueta</summary>
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
      <footer className="border-t border-slate-200 pt-4 text-sm">
        Maqueta aislada · sin registro en servidor · sin datos reales · no confirma ni activa EIPD.
      </footer>
    </div>
  );
}
