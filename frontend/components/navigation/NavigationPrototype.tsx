"use client";
import { useEffect, useRef, useState, type ReactNode } from "react";
import {
  modules,
  steps,
  fields,
  labels,
  initial,
  scenarioNames,
  purpose,
  seedResolutions,
  type ModuleId,
  type TaskId,
  type Scenario,
  type Values,
} from "./prototype-data";
import { MainModules, ModuleOptions } from "./PrototypeMenus";
import { moduleNavigation, groupDestinations } from "./prototype-navigation";
const primary =
  "rounded-lg bg-blue-800 px-4 py-3 font-semibold text-white hover:bg-blue-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-800 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-600";
const secondary =
  "rounded-lg border border-slate-300 bg-white px-4 py-3 font-semibold text-slate-800 hover:border-blue-700 hover:bg-blue-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-800";
const input =
  "mt-2 block w-full rounded-lg border border-slate-300 bg-white p-3 font-normal text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-700";
type Location = { module: ModuleId; task: TaskId; section: string };
type Overlay = {
  kind: "detail" | "copy" | "preview" | "register" | "reset";
  title: string;
  text?: string;
};
function Card({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <h3 className="mb-3 text-lg font-bold text-slate-950">{title}</h3>
      {children}
    </section>
  );
}
export function NavigationPrototype() {
  const [location, setLocation] = useState<Location>({
    module: "panel",
    task: "resumen",
    section: "estado",
  });
  const [scenario, setScenario] = useState<Scenario>("adultos");
  const [drafts, setDrafts] = useState<Record<Scenario, Values>>({
    adultos: initial("adultos"),
    infancia: initial("infancia"),
  });
  const [saved, setSaved] = useState<Record<Scenario, Values>>({
    adultos: initial("adultos"),
    infancia: initial("infancia"),
  });
  const [savedSteps, setSavedSteps] = useState<Record<Scenario, string[]>>({
    adultos: [],
    infancia: [],
  });
  const [resolutions, setResolutions] = useState(seedResolutions);
  const [selected, setSelected] = useState(2);
  const [origin, setOrigin] = useState<string | null>(null);
  const [overlay, setOverlay] = useState<Overlay | null>(null);
  const [notice, setNotice] = useState("");
  const [events, setEvents] = useState<string[]>([]);
  const [choice, setChoice] = useState("");
  const [rationale, setRationale] = useState("");
  const [reference, setReference] = useState("");
  const [reviews, setReviews] = useState<
    { version: number; choice: string; text: string; reference: string }[]
  >([]);
  const [fictitious, setFictitious] = useState(false);
  const [fileName, setFileName] = useState("");
  const [fileError, setFileError] = useState("");
  const [fileKey, setFileKey] = useState(0);
  const [annexes, setAnnexes] = useState<Record<Scenario, string[]>>({ adultos: [], infancia: [] });
  const contentRef = useRef<HTMLElement>(null);
  const navigationRef = useRef<HTMLDivElement>(null);
  const rootRef = useRef<HTMLDivElement>(null);
  const dialogRef = useRef<HTMLDialogElement>(null);
  const dialogTrigger = useRef<HTMLElement | null>(null);
  const first = useRef(true);
  const { module, task, section } = location;
  const m = modules.find((v) => v.id === module)!;
  const menu = steps(module, task, scenario);
  const values = drafts[scenario];
  const stored = saved[scenario];
  const fs = fields[section];
  const title = labels[section];
  const row = resolutions.find((r) => r.version === selected)!;
  const dirty = Object.keys(values).some((k) => values[k] !== stored[k]);
  const validAnnex = Boolean(
    values["anexos.referencia"]?.startsWith("SIMULADA-") &&
    values["anexos.descripcion"]?.trim() &&
    fileName &&
    !fileError &&
    fictitious
  );
  const validPreparation = Boolean(
    values["preparar.referencia"]?.startsWith("SIMULADA-") &&
    values["preparar.notas"]?.trim() &&
    values["preparar.motivo"]?.trim() &&
    fictitious
  );
  useEffect(() => {
    const node = navigationRef.current;
    if (!node) return;
    const update = () =>
      rootRef.current?.style.setProperty("--navigation-height", `${node.offsetHeight}px`);
    update();
    const observer = new ResizeObserver(update);
    observer.observe(node);
    return () => observer.disconnect();
  }, []);
  useEffect(() => {
    if (navigationRef.current)
      rootRef.current?.style.setProperty(
        "--navigation-height",
        `${navigationRef.current.offsetHeight}px`
      );
    if (first.current) {
      first.current = false;
      return;
    }
    contentRef.current?.focus({ preventScroll: true });
    contentRef.current?.scrollIntoView({ block: "start" });
  }, [location, scenario]);
  useEffect(() => {
    if (overlay && dialogRef.current && !dialogRef.current.open) {
      dialogTrigger.current = document.activeElement as HTMLElement;
      dialogRef.current.showModal();
    }
  }, [overlay]);
  function go(mod: ModuleId, t?: TaskId, s?: string) {
    t = t ?? (mod === "licitud" ? "completar" : "resumen");
    setNotice("");
    setLocation({ module: mod, task: t, section: s ?? steps(mod, t, scenario)[0] });
  }
  function edit(key: string, value: string) {
    setDrafts((old) => ({ ...old, [scenario]: { ...old[scenario], [key]: value } }));
    setNotice("");
  }
  function changeScenario(s: Scenario) {
    setScenario(s);
    setLocation((old) => ({ ...old, section: steps(old.module, old.task, s)[0] }));
    setFictitious(false);
    setFileName("");
    setFileError("");
    setFileKey((v) => v + 1);
    setChoice("");
    setRationale("");
    setReference("");
    setNotice("");
  }
  function close() {
    dialogRef.current?.close();
    setOverlay(null);
    requestAnimationFrame(() => dialogTrigger.current?.focus());
  }
  function detail(title: string, text: string) {
    setOverlay({ kind: "detail", title, text });
  }
  function stepDirty(item: string) {
    return (
      fields[item]?.some((field) => (values[field.key] ?? "") !== (stored[field.key] ?? "")) ??
      false
    );
  }
  function save() {
    if (!fs || (section === "anexos" && !validAnnex)) return;
    const next = { ...stored };
    for (const f of fs) next[f.key] = values[f.key] ?? "";
    setSaved((old) => ({ ...old, [scenario]: next }));
    setSavedSteps((old) => ({
      ...old,
      [scenario]: Array.from(new Set([...old[scenario], section])),
    }));
    if (section === "anexos") {
      setAnnexes((old) => ({
        ...old,
        [scenario]: [
          ...old[scenario],
          `${values["anexos.referencia"]} · ${values["anexos.seccion"]} · ${fileName}`,
        ],
      }));
      setFileName("");
      setFileKey((v) => v + 1);
      setFictitious(false);
    }
    setEvents((old) => [`${scenarioNames[scenario]} · ${title}: guardado simulado.`, ...old]);
    setNotice("Guardado en la maqueta durante esta visita. Recargar reinicia el ejemplo.");
  }
  function download() {
    const blob = new Blob(
      [
        JSON.stringify(
          {
            type: "maqueta_sin_valor_juridico",
            scenario,
            values: stored,
            resolutions: scenario === "infancia" ? resolutions : [],
            annexes: annexes[scenario],
            can_confirm: false,
            activation: "deshabilitada",
          },
          null,
          2
        ),
      ],
      { type: "application/json" }
    );
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `maqueta-cumpleia-${scenario}.json`;
    a.click();
    URL.revokeObjectURL(url);
    setNotice("Descargaste el ejemplo guardado. No incluye cambios pendientes.");
  }
  function form() {
    const readOnly = module === "licitud" && section === "alcance";
    return (
      <>
        {readOnly && (
          <p className="rounded-lg border border-sky-200 bg-sky-50 p-4">
            Información del RAT de ejemplo. Aquí solo se consulta; el acceso inferior abre su
            edición en el inventario.
          </p>
        )}
        {section === "base" && (
          <p className="rounded-lg bg-amber-50 p-4">
            Consentimiento y LIA: formularios completos pendientes de desarrollo. Aquí se prueba su
            acceso propuesto.
          </p>
        )}
        {section === "preparar" && (
          <p className="rounded-lg bg-sky-50 p-4">
            Origen: {origin ?? "Preparación nueva"}. Copiar prepara un formulario temporal;
            registrar agrega una versión al ejemplo.
          </p>
        )}
        {fs.map((f) => (
          <label key={f.key} className="block font-semibold text-slate-800">
            {f.label}
            {f.options ? (
              <select
                className={input}
                aria-label={f.label}
                value={values[f.key] ?? f.options[0]}
                disabled={readOnly}
                onChange={(e) => edit(f.key, e.target.value)}
              >
                {f.options.map((v) => (
                  <option key={v}>{v}</option>
                ))}
              </select>
            ) : (
              <textarea
                rows={f.key.endsWith("notas") ? 4 : 3}
                aria-label={f.label}
                className={input}
                value={values[f.key] ?? ""}
                readOnly={readOnly}
                onChange={(e) => edit(f.key, e.target.value)}
              />
            )}{" "}
            {f.hint && (
              <span className="mt-1 block text-sm font-normal text-slate-600">{f.hint}</span>
            )}
          </label>
        ))}
        {section === "base" &&
          ["Consentimiento", "Interés legítimo"].includes(values["base.tipo"]) && (
            <button
              className={secondary}
              onClick={() =>
                detail(
                  `Formulario previsto de ${values["base.tipo"]}`,
                  "Propuesta: preguntas por requisito, fundamento y referencias de evidencia. Respuestas sin declarar por defecto. El desarrollo LIC-FORM-001 sigue pendiente; esta ventana no valida consentimiento ni LIA."
                )
              }
            >
              Abrir información del formulario previsto ↗
            </button>
          )}
        {section === "anexos" && (
          <>
            <label className="block font-semibold">
              Archivo PDF o TXT de ejemplo
              <input
                key={fileKey}
                className={input}
                type="file"
                accept=".pdf,.txt"
                aria-invalid={Boolean(fileError)}
                aria-describedby="file-help"
                onChange={(e) => {
                  const f = e.target.files?.[0];
                  setFileName(f?.name ?? "");
                  setFileError(
                    !f
                      ? ""
                      : !/\.(pdf|txt)$/i.test(f.name)
                        ? "Formato no admitido. Selecciona PDF o TXT."
                        : !f.size
                          ? "El archivo está vacío."
                          : f.size > 2 * 1024 * 1024
                            ? "El archivo supera 2 MiB."
                            : ""
                  );
                }}
              />
            </label>
            <p
              id="file-help"
              role={fileError ? "alert" : undefined}
              className={
                fileError
                  ? "rounded-lg border border-red-300 bg-red-50 p-3 text-red-800"
                  : "text-sm text-slate-600"
              }
            >
              {fileError ||
                "Hasta 2 MiB. El archivo no se carga a ningún servidor; la maqueta solo conserva su nombre."}
            </p>
          </>
        )}
        {["anexos", "preparar"].includes(section) && (
          <label className="flex items-start gap-3">
            <input
              type="checkbox"
              className="mt-1 h-5 w-5 shrink-0"
              checked={fictitious}
              onChange={(e) => setFictitious(e.target.checked)}
            />
            Declaro que este ejemplo usa únicamente datos ficticios.
          </label>
        )}
        {readOnly ? (
          <button className={secondary} onClick={() => go("rat", "completar", "alcance")}>
            Abrir edición en Inventario RAT →
          </button>
        ) : (
          <div className="space-y-3 rounded-xl border border-blue-200 bg-blue-50 p-4">
            <p>
              {fs.some((f) => (values[f.key] ?? "") !== (stored[f.key] ?? ""))
                ? "Cambios sin guardar en este paso. Navegar conserva tus cambios durante esta visita."
                : "Puedes guardar el ejemplo o continuar navegando."}
            </p>
            {section === "anexos" && !validAnnex && (
              <p id="save-help">
                Para guardar: referencia SIMULADA-, descripción, PDF/TXT válido y declaración
                ficticia.
              </p>
            )}
            {section === "preparar" && (
              <p id="prepare-help">
                Para revisar: referencia SIMULADA-, notas, motivo del cambio y declaración ficticia.
              </p>
            )}
            <div className="flex flex-wrap gap-3">
              <button
                className={primary}
                disabled={
                  (section === "anexos" && !validAnnex) ||
                  (section === "preparar" && !validPreparation)
                }
                aria-describedby={
                  section === "anexos"
                    ? "save-help"
                    : section === "preparar"
                      ? "prepare-help"
                      : undefined
                }
                onClick={() =>
                  section === "preparar"
                    ? setOverlay({
                        kind: "preview",
                        title: "Revisar nueva resolución antes de registrarla",
                      })
                    : save()
                }
              >
                {section === "preparar"
                  ? "Abrir vista previa de la resolución →"
                  : "Guardar cambios en la maqueta"}
              </button>
              {menu.indexOf(section) < menu.length - 1 && (
                <button
                  className={secondary}
                  onClick={() => go(module, task, menu[menu.indexOf(section) + 1])}
                >
                  Siguiente: {labels[menu[menu.indexOf(section) + 1]]} →
                </button>
              )}
              {menu.indexOf(section) > 0 && (
                <button
                  className={secondary}
                  onClick={() => go(module, task, menu[menu.indexOf(section) - 1])}
                >
                  ← Anterior
                </button>
              )}
            </div>
          </div>
        )}
      </>
    );
  }

  function resolutionView() {
    return (
      <>
        <div className="flex flex-wrap gap-3" role="group" aria-label="Elegir resolución">
          {resolutions.map((r) => (
            <button
              key={r.version}
              aria-pressed={r.version === selected}
              className={r.version === selected ? primary : secondary}
              onClick={() => {
                setSelected(r.version);
                setChoice("");
                setRationale("");
                setReference("");
              }}
            >
              Consultar resolución {r.version}
            </button>
          ))}
        </div>
        <Card title={`Resolución ${selected} · ${row.reference}`}>
          <p className="whitespace-pre-wrap">{row.notes}</p>
          {row.origin && <p className="mt-3">Origen: {row.origin}</p>}
          <button
            className={`${secondary} mt-4`}
            onClick={() =>
              setOverlay({ kind: "copy", title: "Preparar una copia de esta resolución" })
            }
          >
            Preparar sucesor desde esta resolución →
          </button>
        </Card>
        {section === "resoluciones" && (
          <div className="flex flex-wrap gap-3">
            <button className={secondary} onClick={() => go("licitud", "revisar", "revisiones")}>
              Abrir revisión de esta resolución →
            </button>
            <button className={secondary} onClick={() => go("licitud", "revisar", "decisiones")}>
              Abrir decisión de organización →
            </button>
          </div>
        )}
        {section === "revisiones" && (
          <Card title="Revisión del documento">
            <p className="mb-4">
              Objetivo: resolución {selected}. Registra observaciones; no modifica el original ni
              expresa una decisión de organización.
            </p>
            <label className="block font-semibold">
              Resultado de revisión
              <select className={input} value={choice} onChange={(e) => setChoice(e.target.value)}>
                <option value="">Selecciona un resultado</option>
                <option>Requiere cambios</option>
                <option>No continuar</option>
              </select>
            </label>
            <label className="mt-4 block font-semibold">
              Fundamento de la revisión
              <textarea
                className={input}
                value={rationale}
                onChange={(e) => setRationale(e.target.value)}
              />
            </label>
            <label className="mt-4 block font-semibold">
              Referencia de revisión ficticia
              <input
                className={input}
                value={reference}
                onChange={(e) => setReference(e.target.value)}
              />
            </label>
            <p className="my-3">
              Completa resultado, fundamento y referencia SIMULADA- para registrar en la maqueta.
            </p>
            <button
              className={primary}
              disabled={!choice || !rationale.trim() || !reference.startsWith("SIMULADA-")}
              onClick={() => {
                setReviews((old) => [
                  ...old,
                  { version: selected, choice, text: rationale, reference },
                ]);
                setChoice("");
                setRationale("");
                setReference("");
                setNotice("Revisión registrada solo en la maqueta; original conservado.");
              }}
            >
              Registrar revisión simulada
            </button>
            <h4 className="mt-5 font-bold">Revisiones de esta resolución</h4>
            {selected <= 2 ? (
              <p className="mt-2 rounded-lg bg-slate-50 p-3">
                {selected === 1 ? "Requiere cambios" : "No continuar"} · Revisión ficticia previa.
              </p>
            ) : (
              <p className="mt-2">Sin revisiones previas para esta nueva versión.</p>
            )}
            {reviews
              .filter((r) => r.version === selected)
              .map((r, i) => (
                <p key={i} className="mt-2 rounded-lg bg-slate-50 p-3">
                  {r.choice} · {r.text} · {r.reference}
                </p>
              ))}
          </Card>
        )}
        {section === "decisiones" && (
          <Card title="Decisión de la organización">
            <p className="rounded-lg border border-amber-300 bg-amber-50 p-4 font-semibold">
              No puedes registrar una decisión: la facultad de la persona de ejemplo está revocada.
            </p>
            <p className="my-4">
              La decisión histórica permanece consultable. El ejemplo no acredita vigencia ni
              autorización.
            </p>
            <button className={primary} disabled>
              Registrar decisión de organización
            </button>
            <button
              className={`${secondary} mt-4 block`}
              onClick={() => go("licitud", "revisar", "facultades")}
            >
              Consultar historial de facultades →
            </button>
            <p className="mt-4">
              {selected <= 2
                ? "Decisión previa del ejemplo: Requiere cambios. Es distinta de la revisión documental."
                : "Sin decisiones previas para esta nueva resolución del ejemplo."}
            </p>
          </Card>
        )}
      </>
    );
  }
  function content() {
    if (module === "rat" && section === "estado")
      return (
        <Card title="Catálogo de tratamientos de ejemplo">
          <p className="mb-5 text-slate-600">
            Elige un tratamiento para abrir su actividad. Son ejemplos ficticios independientes.
          </p>
          <div className="grid gap-4 lg:grid-cols-2">
            {(["adultos", "infancia"] as Scenario[]).map((item) => (
              <div key={item} className="rounded-xl border border-slate-200 p-4">
                <h4 className="font-bold text-slate-950">{drafts[item]["rat.nombre"]}</h4>
                <p className="mt-2 text-sm text-slate-600">{purpose[item]}</p>
                <button
                  className={`${primary} mt-4`}
                  onClick={() => {
                    changeScenario(item);
                    go("rat", "completar", "alcance");
                  }}
                >
                  Abrir actividad de{" "}
                  {item === "adultos" ? "clientes adultos" : "programa con menores"} →
                </button>
              </div>
            ))}
          </div>
        </Card>
      );
    if (section === "estado")
      return module === "panel" ? (
        <>
          <div className="rounded-xl bg-slate-900 p-6 text-white">
            <p className="text-sm font-semibold text-sky-200">TU ESPACIO DE TRABAJO</p>
            <h3 className="mt-2 text-2xl font-bold">Continúa donde lo dejaste</h3>
            <p className="mt-2 text-slate-200">
              Escenario: {scenarioNames[scenario]}. Encuentra cada tarea desde el mismo lugar.
            </p>
            <button
              className="mt-5 rounded-lg bg-white px-4 py-3 font-bold text-blue-900 hover:bg-blue-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-sky-300"
              onClick={() => go("licitud", "completar", "base")}
            >
              Continuar evaluación de ejemplo →
            </button>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            {modules
              .filter((v) => v.id !== "panel")
              .map((v) => (
                <button
                  key={v.id}
                  className="rounded-xl border border-slate-200 bg-white p-5 text-left shadow-sm transition hover:border-blue-600 hover:shadow-md focus-visible:outline focus-visible:outline-2 focus-visible:outline-blue-800"
                  onClick={() => go(v.id)}
                >
                  <span className="text-lg font-bold text-slate-950">{v.title}</span>
                  <p className="mt-2 text-slate-600">{v.description}</p>
                  <span className="mt-4 inline-block font-semibold text-blue-800">
                    Abrir módulo →
                  </span>
                </button>
              ))}
          </div>
        </>
      ) : (
        <>
          <Card title="Tu siguiente paso">
            <p>
              Revisa el alcance y completa los antecedentes pendientes. Los estados indican avance
              del ejemplo, no aprobación.
            </p>
            <button className={`${primary} mt-4`} onClick={() => go(module, "completar")}>
              Ir a completar datos →
            </button>
          </Card>
          <div className="grid gap-4 sm:grid-cols-2">
            <Card title="Avance documental">
              <p className="text-3xl font-bold text-blue-900">
                {savedSteps[scenario].length} pasos
              </p>
              <p className="mt-2">guardados en esta visita, entre los módulos del ejemplo.</p>
            </Card>
            <Card title="Revisión pendiente">
              <p>
                Una persona responsable debe revisar fundamentos y evidencias. Confirmación y
                activación EIPD bloqueadas.
              </p>
              <button className={`${secondary} mt-4`} onClick={() => go(module, "revisar")}>
                Abrir documentos y revisiones →
              </button>
            </Card>
          </div>
        </>
      );
    if (section === "ayuda")
      return (
        <Card title="Un recorrido para probar">
          <ol className="list-inside list-decimal space-y-3">
            <li>Abre un módulo desde el menú principal de la izquierda.</li>
            <li>Elige una opción superior. La flecha indica que contiene un submenú.</li>
            <li>Edita y guarda un ejemplo; cambia de sección para comprobar su conservación.</li>
            <li>Consulta lo guardado y prueba abrir y cerrar detalles.</li>
          </ol>
          <p className="mt-5">
            Los cambios duran esta visita. Recargar reinicia los ejemplos. No se envían datos a tus
            expedientes.
          </p>
        </Card>
      );
    if (
      ["resoluciones", "revisiones", "decisiones"].includes(section) &&
      module === "licitud" &&
      scenario === "infancia"
    )
      return resolutionView();
    if (section === "facultades")
      return (
        <Card title="Historial de facultades">
          <p className="rounded-lg border border-amber-300 bg-amber-50 p-4">
            Facultad actual del ejemplo: revocada. Consultar el historial no concede permisos.
          </p>
          <ol className="mt-5 space-y-4">
            <li>
              <strong>1. Otorgamiento ficticio</strong>
              <p>SIMULADA-MAQUETA-FAC-001 · Persona responsable del ejemplo.</p>
            </li>
            <li>
              <strong>2. Revocación ficticia</strong>
              <p>SIMULADA-MAQUETA-REVOCACION-002 · La decisión anterior se conserva.</p>
            </li>
          </ol>
        </Card>
      );
    if (section === "versiones")
      return (
        <Card title="Versiones del ejemplo">
          {module === "licitud" && scenario === "infancia" ? (
            resolutions.map((r) => (
              <div
                key={r.version}
                className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 py-4"
              >
                <div>
                  <p className="font-bold">Resolución {r.version}</p>
                  <p className="break-all">{r.reference}</p>
                </div>
                <button
                  className={secondary}
                  onClick={() => {
                    setSelected(r.version);
                    go("licitud", "revisar", "resoluciones");
                  }}
                >
                  Abrir versión {r.version} →
                </button>
              </div>
            ))
          ) : (
            <p>
              Ejemplo inicial · Versión 1 · Borrador ficticio. No hay registros reales en esta
              maqueta.
            </p>
          )}
        </Card>
      );
    if (section === "eventos")
      return (
        <Card title="Actividad de esta visita">
          {events.length ? (
            <ol className="space-y-3">
              {events.map((e, i) => (
                <li key={i} className="rounded-lg bg-slate-50 p-3">
                  {e}
                </li>
              ))}
            </ol>
          ) : (
            <p>Aún no hay actividad nueva en la maqueta.</p>
          )}
        </Card>
      );
    if (section === "descargas")
      return (
        <Card title="Descargar el ejemplo guardado">
          <p>
            Incluye campos guardados en la maqueta, versiones ficticias y referencias de anexos. No
            es un expediente jurídico ni una exportación del servidor.
          </p>
          <button className={`${primary} mt-5`} onClick={download}>
            Descargar JSON de demostración ↓
          </button>
        </Card>
      );
    if (section === "equipo")
      return (
        <Card title="Equipo de ejemplo">
          <p>Persona responsable · Usuario ficticio.</p>
          <p className="mt-3">
            No se envían invitaciones ni se modifican permisos en esta maqueta.
          </p>
          <button
            className={`${secondary} mt-5`}
            onClick={() => go("organizacion", "revisar", "facultades")}
          >
            Consultar facultades del ejemplo →
          </button>
        </Card>
      );
    if (["resultados", "informe"].includes(section))
      return (
        <Card title="Diagnóstico de demostración">
          <p>
            Resultado ilustrativo. No se calcula una puntuación jurídica a partir de estas
            respuestas.
          </p>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            <div className="rounded-lg bg-amber-50 p-4">
              <strong>Alcance por revisar</strong>
              <p>Confirmar tratamientos y finalidad.</p>
            </div>
            <div className="rounded-lg bg-blue-50 p-4">
              <strong>Siguiente tarea</strong>
              <p>Documentar base y fundamento.</p>
            </div>
          </div>
          <button className={`${primary} mt-5`} onClick={() => go("rat", "completar", "alcance")}>
            Abrir alcance en el inventario →
          </button>
        </Card>
      );
    if (["documentos", "biblioteca", "respaldos"].includes(section))
      return (
        <>
          <Card title="Alcance y base guardados en la maqueta">
            <p className="font-bold">{stored["rat.finalidad"]}</p>
            <p className="mt-3">Base: {stored["base.tipo"]}</p>
            <p className="mt-3 whitespace-pre-wrap">{stored["base.fundamento"]}</p>
            <p className="mt-3 text-slate-600">
              Procedencia: datos iniciales y campos guardados en esta visita. Las ediciones
              pendientes no se incluyen.
            </p>
            <button
              className={`${secondary} mt-4`}
              onClick={() =>
                detail(
                  "Alcance RAT del ejemplo",
                  `${stored["rat.categorias"]} · ${stored["rat.titulares"]}. Fuente: ${stored["rat.fuentes"]}. Conservación: ${stored["rat.conservacion"]}.`
                )
              }
            >
              Abrir detalle del alcance ↗
            </button>
          </Card>
          {scenario === "infancia" && (
            <Card title="Documento de infancia guardado en la maqueta">
              <p>{stored["infancia.edad"]}</p>
              <p className="mt-3 whitespace-pre-wrap">{stored["infancia.notas"]}</p>
              <button
                className={`${secondary} mt-4`}
                onClick={() => go("licitud", "completar", "infancia")}
              >
                Abrir editor de infancia →
              </button>
            </Card>
          )}
          {["eipd", "proporcionalidad"].some((item) => savedSteps[scenario].includes(item)) && (
            <Card title="Documento EIPD guardado en la maqueta">
              <p className="font-bold">{stored["eipd.referencia"]}</p>
              <p className="mt-3 whitespace-pre-wrap">{stored["eipd.analisis"]}</p>
              <p className="mt-3 whitespace-pre-wrap">
                {stored["eipd.seguimiento"] || "Seguimiento pendiente de completar."}
              </p>
            </Card>
          )}
          <Card title="Riesgo y medida que lo sustenta">
            <p className="text-sm font-bold text-slate-600">
              EJEMPLO DE LECTURA FIJO · NO RECALCULADO
            </p>
            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <div className="rounded-lg bg-slate-50 p-4">
                <p className="font-bold">R1 · Residual del ejemplo: Medio</p>
                <p>Baja probabilidad · Impacto grave</p>
              </div>
              <div className="rounded-lg bg-slate-50 p-4">
                <p className="font-bold">M1 · Restricción de acceso</p>
                <p>Probabilidad · Eficacia parcial · Verificación sintética</p>
              </div>
            </div>
            <p className="mt-3">
              Ilustración independiente de los campos editables. No acredita controles reales.
            </p>
            <button
              className={`${secondary} mt-4`}
              onClick={() =>
                detail(
                  "Evidencia vinculada a R1 y M1",
                  "SIMULADA-MAQUETA-EVIDENCIA-001 · Versión 1 · Sección Medidas. Acta sintética con casos predefinidos de acceso. No representa pruebas ejecutadas ni un archivo del expediente real."
                )
              }
            >
              Consultar evidencia y versión ↗
            </button>
          </Card>
          {scenario === "infancia" && (
            <button className={primary} onClick={() => go("licitud", "revisar", "resoluciones")}>
              Abrir resoluciones de infancia →
            </button>
          )}
          <Card title="Anexos guardados del ejemplo">
            {annexes[scenario].length ? (
              annexes[scenario].map((a, i) => (
                <p key={i} className="mb-3 rounded-lg bg-slate-50 p-3">
                  {a} · Solo nombre; archivo no almacenado.
                </p>
              ))
            ) : (
              <p>Sin anexos añadidos durante esta visita.</p>
            )}
            <button
              className={`${secondary} mt-4`}
              onClick={() => go("licitud", "completar", "anexos")}
            >
              Abrir formulario de anexo →
            </button>
          </Card>
        </>
      );
    if (fs) return form();
    return (
      <Card title="Revisión documental">
        <p>
          El flujo formal de revisión de RAT/LIA requiere desarrollo posterior. Aquí puedes probar
          su ubicación.
        </p>
        <button
          className={`${secondary} mt-4`}
          onClick={() =>
            detail(
              "Revisión de adultos · acceso previsto",
              "Propuesta de navegación. No registra una aprobación ni habilita un flujo formal del producto."
            )
          }
        >
          Abrir alcance de revisión previsto ↗
        </button>
      </Card>
    );
  }

  return (
    <div
      ref={rootRef}
      className="text-base leading-relaxed text-slate-800 [overflow-wrap:anywhere]"
    >
      <a
        href="#prototype-content"
        className="sr-only focus:not-sr-only focus:mb-4 focus:block focus:rounded focus:bg-blue-800 focus:p-3 focus:text-white"
      >
        Saltar al contenido de la maqueta
      </a>
      <header className="mb-5 flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm font-bold uppercase tracking-widest text-blue-800">
            CumpleIA · Diseño de navegación
          </p>
          <h1 className="mt-1 text-2xl font-bold text-slate-950">Maqueta integral</h1>
          <p className="mt-1 text-sm text-slate-600">Menú lateral y opciones por módulo</p>
        </div>
        <button
          className={secondary}
          onClick={() =>
            setOverlay({ kind: "reset", title: "Reiniciar los ejemplos de la maqueta" })
          }
        >
          Reiniciar ejemplos
        </button>
      </header>
      <aside className="mb-5 rounded-xl border border-sky-200 bg-sky-50 px-4 py-3 text-sm text-sky-950">
        <strong>Entorno de demostración.</strong> Solo ejemplos ficticios. Los guardados duran esta
        visita; recargar reinicia la maqueta. Tus expedientes no cambian.
      </aside>
      <div className="grid items-start gap-5 md:grid-cols-[240px_minmax(0,1fr)]">
        <MainModules module={module} go={(mod) => go(mod)} />
        <div className="min-w-0">
          <div
            ref={navigationRef}
            className="top-0 z-20 mb-5 sm:sticky rounded-xl border border-slate-200 bg-gray-50 p-3 shadow-sm"
            aria-label="Navegación del módulo"
          >
            <div className="mb-3 flex flex-col items-start justify-between gap-3 sm:flex-row sm:flex-wrap">
              <div className="w-full min-w-0 sm:w-auto sm:flex-1">
                <p className="text-xs font-semibold text-slate-500">Inicio / {m.title}</p>
                <h2 className="mt-1 text-xl font-bold text-slate-950">{m.title}</h2>
                <p className="mt-1 text-xs text-slate-600">
                  Organización de ejemplo · {scenarioNames[scenario]} · Evaluación v1
                </p>
              </div>
              <label className="w-full min-w-0 text-xs font-semibold sm:w-auto">
                Escenario de prueba
                <select
                  aria-label="Escenario de prueba"
                  className="mt-1 block w-full max-w-full rounded-lg border border-slate-300 bg-white p-2 text-sm sm:w-auto"
                  value={scenario}
                  onChange={(e) => changeScenario(e.target.value as Scenario)}
                >
                  <option value="adultos">Clientes adultos</option>
                  <option value="infancia">Programa con menores</option>
                </select>
              </label>
            </div>
            <ModuleOptions
              location={location}
              scenario={scenario}
              go={go}
              status={(item) =>
                stepDirty(item)
                  ? "Cambios sin guardar"
                  : savedSteps[scenario].includes(item)
                    ? "Guardado en maqueta"
                    : ""
              }
            />
          </div>
          <div className="mb-4 rounded-lg border border-slate-200 bg-white p-3 text-sm">
            <p className="font-semibold">{values["rat.nombre"]}</p>
            <p className="mt-1 text-slate-600">{values["rat.finalidad"]}</p>
            {dirty && (
              <p className="mt-2 font-semibold text-amber-900">
                Cambios sin guardar · Se conservan al navegar durante esta visita.
              </p>
            )}
          </div>
          <section
            ref={contentRef}
            id="prototype-content"
            style={{ scrollMarginTop: "calc(var(--navigation-height, 190px) + 16px)" }}
            tabIndex={-1}
            aria-labelledby="prototype-section-title"
            className="min-w-0 rounded-xl border border-slate-200 bg-white p-5 shadow-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-700 sm:p-6"
          >
            <header className="mb-6 border-b border-slate-200 pb-4">
              <p className="text-sm font-semibold text-blue-800">
                {m.title} /{" "}
                {moduleNavigation(module, scenario).find((group) =>
                  groupDestinations(group, scenario).some(
                    (item) => item.task === task && item.section === section
                  )
                )?.label ?? "Resumen"}
              </p>
              <h2 id="prototype-section-title" className="mt-1 text-xl font-bold text-slate-950">
                {title}
              </h2>
              <p className="mt-2 text-sm text-slate-600">
                {task === "completar"
                  ? "Navegar conserva tus cambios durante esta visita. Guarda antes de consultar el documento."
                  : "Consultar no registra decisiones. Elige una opción del menú superior para continuar."}
              </p>
            </header>
            {notice && (
              <p
                role="status"
                className="mb-5 rounded-lg border border-teal-300 bg-teal-50 p-4 text-teal-950"
              >
                {notice}
              </p>
            )}
            <div className="space-y-5">{content()}</div>
          </section>
        </div>
      </div>
      <footer className="mt-6 text-sm text-slate-500">
        Propuesta para pruebas de navegación · Sin conexión a expedientes · Confirmación y
        activación EIPD bloqueadas.
      </footer>
      {overlay && (
        <dialog
          ref={dialogRef}
          aria-labelledby="prototype-dialog-title"
          onCancel={(event) => {
            event.preventDefault();
            close();
          }}
          onClose={() => setOverlay(null)}
          className={`m-auto max-h-[90dvh] w-[calc(100%-2rem)] max-w-xl overflow-y-auto rounded-2xl border border-slate-200 bg-white p-6 text-slate-900 shadow-2xl backdrop:bg-slate-950/40 ${overlay.kind === "detail" ? "md:fixed md:inset-y-0 md:left-auto md:right-0 md:m-0 md:h-dvh md:max-h-dvh md:rounded-r-none" : ""}`}
        >
          <div className="mb-5 flex items-start justify-between gap-4">
            <h2 id="prototype-dialog-title" className="text-xl font-bold">
              {overlay.title}
            </h2>
            <button autoFocus className={secondary} onClick={close}>
              Cerrar
            </button>
          </div>
          {overlay.kind === "detail" && <p className="whitespace-pre-wrap">{overlay.text}</p>}
          {overlay.kind === "copy" && (
            <>
              <p>
                Se copiará {row.reference} al formulario temporal. Reemplazará lo que estés
                preparando. El original y las versiones registradas se conservan.
              </p>
              <div className="mt-5 flex flex-wrap gap-3">
                <button
                  className={primary}
                  onClick={() => {
                    setDrafts((old) => ({
                      ...old,
                      infancia: {
                        ...old.infancia,
                        "preparar.referencia": `${row.reference}-COPIA`,
                        "preparar.notas": row.notes,
                        "preparar.motivo": "",
                      },
                    }));
                    setOrigin(row.reference);
                    setFictitious(false);
                    setOverlay(null);
                    go("licitud", "completar", "preparar");
                    setNotice(
                      "Copia temporal preparada. Completa el motivo antes de revisarla. El original permanece intacto."
                    );
                  }}
                >
                  Reemplazar y copiar a preparación
                </button>
                <button className={secondary} onClick={close}>
                  Conservar documento en preparación
                </button>
              </div>
            </>
          )}
          {overlay.kind === "preview" && (
            <>
              <p className="mb-4 rounded-lg bg-amber-50 p-3">
                Vista previa ficticia. Todavía no se creó otra resolución.
              </p>
              <dl className="space-y-3">
                <dt className="font-bold">Referencia</dt>
                <dd>{values["preparar.referencia"]}</dd>
                <dt className="font-bold">Notas</dt>
                <dd className="whitespace-pre-wrap">{values["preparar.notas"]}</dd>
                <dt className="font-bold">Motivo del cambio</dt>
                <dd>{values["preparar.motivo"]}</dd>
              </dl>
              <p className="my-4">
                Análisis y evidencias pendientes. Registrar no confirma ni activa EIPD.
              </p>
              <button
                className={primary}
                onClick={() =>
                  setOverlay({ kind: "register", title: "Confirmar registro simulado" })
                }
              >
                Continuar al registro de ejemplo →
              </button>
            </>
          )}
          {overlay.kind === "register" && (
            <>
              <p>
                Se agregará una resolución a la memoria de esta maqueta. Las anteriores no cambian.
                Recargar reinicia el ejemplo.
              </p>
              <div className="mt-5 flex flex-wrap gap-3">
                <button
                  className={primary}
                  onClick={() => {
                    const version = Math.max(...resolutions.map((r) => r.version)) + 1;
                    setResolutions((old) => [
                      ...old,
                      {
                        version,
                        reference: values["preparar.referencia"],
                        notes: values["preparar.notas"],
                        origin: origin ?? undefined,
                      },
                    ]);
                    setSelected(version);
                    setFictitious(false);
                    setOverlay(null);
                    setDrafts((old) => ({
                      ...old,
                      infancia: {
                        ...old.infancia,
                        "preparar.referencia": "",
                        "preparar.notas": "",
                        "preparar.motivo": "",
                      },
                    }));
                    setOrigin(null);
                    setEvents((old) => [
                      `Infancia · Resolución ${version} registrada en la maqueta.`,
                      ...old,
                    ]);
                    go("licitud", "revisar", "resoluciones");
                    setNotice(
                      `Resolución ${version} agregada solo al ejemplo. Las anteriores se conservan.`
                    );
                  }}
                >
                  Registrar resolución solo en maqueta
                </button>
                <button className={secondary} onClick={close}>
                  Volver sin registrar
                </button>
              </div>
            </>
          )}
          {overlay.kind === "reset" && (
            <>
              <p>
                Se descartarán los cambios de ambos escenarios de la maqueta. Los expedientes de
                CumpleIA no se modifican.
              </p>
              <div className="mt-5 flex flex-wrap gap-3">
                <button
                  className={primary}
                  onClick={() => {
                    setDrafts({ adultos: initial("adultos"), infancia: initial("infancia") });
                    setSaved({ adultos: initial("adultos"), infancia: initial("infancia") });
                    setSavedSteps({ adultos: [], infancia: [] });
                    setAnnexes({ adultos: [], infancia: [] });
                    setResolutions(seedResolutions());
                    setSelected(2);
                    setOrigin(null);
                    setReviews([]);
                    setEvents([]);
                    setFictitious(false);
                    setFileName("");
                    setFileError("");
                    setFileKey((v) => v + 1);
                    setChoice("");
                    setRationale("");
                    setReference("");
                    setOverlay(null);
                    go("panel");
                    setNotice("Ejemplos reiniciados.");
                  }}
                >
                  Reiniciar maqueta
                </button>
                <button className={secondary} onClick={close}>
                  Conservar esta visita
                </button>
              </div>
            </>
          )}
        </dialog>
      )}
    </div>
  );
}
