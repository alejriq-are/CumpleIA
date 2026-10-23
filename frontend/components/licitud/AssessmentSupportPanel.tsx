"use client";
import { useEffect, useRef, useState } from "react";
import type { Assessment } from "@/lib/api/licitud";
import { SaveFeedback } from "./SaveFeedback";
import { ApiError } from "@/lib/api/client";
import {
  supportApi,
  annexFileError,
  type Support,
  type Analysis,
  type Rating,
  type Rank,
  type RiskRating,
  type ControlRating,
  blankRisk,
  blankControl,
  levelLabels,
  ratingLevel,
  matrix,
} from "@/lib/api/assessment-support";

type Props = {
  organizationId: string;
  treatmentId: string;
  assessmentId: string;
  token: () => Promise<string>;
  row: Assessment | null;
  readOnly: boolean;
  blocked: boolean;
  refreshVersion: number;
  mode: "risks" | "annexes" | "review";
  hidden: boolean;
  onSaved: () => void;
  onLoaded: (value: Support | null) => void;
  onDirty: (dirty: boolean) => void;
};
const annexSections: Record<string, string> = {
  alcance: "Alcance",
  base: "Base y fundamento",
  necesidad: "Necesidad y proporcionalidad",
  riesgos: "Riesgos",
  medidas: "Medidas",
  fuentes: "Fuentes y evidencias",
  seguimiento: "Seguimiento",
};
const textClass = "block w-full rounded border p-2";
function TextField({
  label,
  value,
  onChange,
  type = "text",
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: string;
}) {
  return (
    <label className="block">
      {label}
      {type === "date" ? (
        <input
          type="date"
          aria-label={label}
          className={textClass}
          value={value}
          onChange={(e) => onChange(e.target.value)}
        />
      ) : (
        <textarea
          aria-label={label}
          className={textClass}
          value={value}
          onChange={(e) => onChange(e.target.value)}
        />
      )}
    </label>
  );
}
function RatingFields({
  label,
  help,
  value,
  onChange,
}: {
  label: string;
  help?: string;
  value: Rating;
  onChange: (value: Rating) => void;
}) {
  return (
    <fieldset className="space-y-3 rounded border p-3">
      <legend className="font-semibold">{label}</legend>
      {help && <p className="rounded bg-blue-50 p-3 text-base leading-relaxed">{help}</p>}
      <div className="grid gap-3 md:grid-cols-2">
        {(["probability", "impact"] as const).map((key) => (
          <label key={key}>
            {key === "probability" ? "Probabilidad" : "Impacto en las personas"}
            <select
              aria-label={`${label} — ${key === "probability" ? "Probabilidad" : "Impacto"}`}
              className={textClass}
              value={value[key] ?? ""}
              onChange={(e) =>
                onChange({
                  ...value,
                  [key]: e.target.value ? (Number(e.target.value) as Rank) : null,
                })
              }
            >
              <option value="">Sin evaluar</option>
              {(key === "probability"
                ? ["Baja", "Media", "Alta", "Muy alta"]
                : ["Bajo", "Moderado", "Grave", "Muy grave"]
              ).map((text, index) => (
                <option key={index} value={index + 1}>
                  {text}
                </option>
              ))}
            </select>
          </label>
        ))}
      </div>
      <p className="rounded bg-blue-50 p-2">
        Nivel orientativo: <strong>{levelLabels[ratingLevel(value)]}</strong>. Se combina la matriz
        definida, no una probabilidad estadística.
      </p>
      <TextField
        label={`${label} — Fundamento`}
        value={value.rationale}
        onChange={(rationale) => onChange({ ...value, rationale })}
      />
    </fieldset>
  );
}
export function AssessmentSupportPanel(props: Props) {
  const [support, setSupport] = useState<Support | null>(null),
    [analysis, setAnalysis] = useState<Analysis>({
      methodology: "CUMPLEIA-CUALITATIVA-1",
      horizon: "12 meses",
      risks: [],
      controls: [],
    });
  const [baseline, setBaseline] = useState(""),
    [busy, setBusy] = useState(false),
    [valid, setValid] = useState(false),
    [uncertain, setUncertain] = useState(false),
    [error, setError] = useState(""),
    [message, setMessage] = useState("");
  const [annex, setAnnex] = useState({
      reference: "",
      description: "",
      section: "fuentes",
      risk_ids: "",
      measure_ids: "",
    }),
    [file, setFile] = useState<File | null>(null),
    [fictitious, setFictitious] = useState(false);
  const analysisDirty = Boolean(baseline && JSON.stringify(analysis) !== baseline),
    annexDirty = Boolean(file || Object.entries(annex).some(([key, v]) => key !== "section" && v));
  const dirty = analysisDirty || annexDirty;
  const dirtyRef = useRef(false),
    running = useRef(false),
    alive = useRef(true);
  dirtyRef.current = analysisDirty;
  const { onDirty } = props;
  useEffect(() => {
    onDirty(dirty || busy || uncertain);
  }, [dirty, busy, uncertain, onDirty]);
  useEffect(() => {
    if (dirty) setMessage("");
  }, [dirty]);
  function accept(value: Support, reset = false) {
    setSupport(value);
    props.onLoaded(value);
    setValid(true);
    if (!dirtyRef.current || reset) {
      const doc = props.row?.eipd_resolution_assessment;
      const risks = Array.isArray(doc?.risks) ? (doc.risks as { risk_id?: string }[]) : [];
      const controls = Array.isArray(doc?.measures)
        ? (doc.measures as { measure_id?: string }[])
        : [];
      const stored = value.risk_evaluation?.analysis;
      const next: Analysis = {
        methodology: "CUMPLEIA-CUALITATIVA-1",
        horizon: stored?.horizon ?? "12 meses",
        risks: risks
          .filter((r) => r.risk_id)
          .map(
            (r) => stored?.risks.find((item) => item.risk_id === r.risk_id) ?? blankRisk(r.risk_id!)
          ),
        controls: controls
          .filter((c) => c.measure_id)
          .map(
            (c) =>
              stored?.controls.find((item) => item.measure_id === c.measure_id) ??
              blankControl(c.measure_id!)
          ),
      };
      setAnalysis(next);
      setBaseline(JSON.stringify(next));
    }
  }
  async function scope() {
    return {
      organizationId: props.organizationId,
      treatmentId: props.treatmentId,
      assessmentId: props.assessmentId,
      token: await props.token(),
    };
  }
  const loadGeneration = useRef<object>({});
  const loadRef = useRef<() => Promise<void>>(async () => {});
  loadRef.current = async () => {
    const generation = {};
    loadGeneration.current = generation;
    setValid(false);
    props.onLoaded(null);
    try {
      const value = await supportApi.load(await scope());
      if (alive.current && generation === loadGeneration.current) {
        accept(value);
        setError("");
        setUncertain(false);
      }
    } catch {
      if (alive.current && generation === loadGeneration.current)
        setError(
          "No se pudo consultar la valoración y los anexos. Tus ediciones se conservan; las escrituras están bloqueadas hasta consultar correctamente."
        );
    }
  };
  useEffect(() => {
    alive.current = true;
    void loadRef.current();
    return () => {
      alive.current = false;
      loadGeneration.current = {};
    };
  }, [
    props.organizationId,
    props.treatmentId,
    props.assessmentId,
    props.refreshVersion,
    props.row?.eipd_resolution_assessment,
  ]);
  async function mutate(kind: "risk" | "annex") {
    if (
      running.current ||
      !valid ||
      !support ||
      props.blocked ||
      props.readOnly ||
      props.row?.status !== "borrador" ||
      uncertain
    )
      return;
    running.current = true;
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const s = await scope();
      const id = crypto.randomUUID();
      const value =
        kind === "risk"
          ? await supportApi.risks(s, analysis, support, id)
          : file && fictitious
            ? await supportApi.annex(
                s,
                {
                  ...annex,
                  risk_ids: annex.risk_ids
                    .split(/[,\n]/)
                    .map((v) => v.trim())
                    .filter(Boolean),
                  measure_ids: annex.measure_ids
                    .split(/[,\n]/)
                    .map((v) => v.trim())
                    .filter(Boolean),
                },
                file,
                id
              )
            : null;
      if (!value) throw new ApiError(422, "Selecciona un archivo y declara que es ficticio.");
      if (!alive.current) return;
      accept(value, kind === "risk");
      if (kind === "annex") {
        setFile(null);
        setAnnex({
          reference: "",
          description: "",
          section: "fuentes",
          risk_ids: "",
          measure_ids: "",
        });
        setFictitious(false);
      }
      setMessage(
        kind === "risk"
          ? "Valoración guardada como nueva revisión. No aprueba ni activa EIPD."
          : "Anexo ficticio guardado. Puedes descargarlo desde la lista; no acredita su veracidad ni aprobación."
      );
      props.onSaved();
    } catch (cause) {
      if (alive.current) {
        const unknown = !(cause instanceof ApiError) || cause.status >= 500 || cause.status === 408;
        setUncertain(unknown);
        setError(
          unknown
            ? "Resultado incierto. Conservamos los datos; consulta los registros antes de volver a guardar."
            : (cause as Error).message
        );
      }
    } finally {
      running.current = false;
      if (alive.current) setBusy(false);
    }
  }
  const disabled =
    props.readOnly ||
    props.row?.status !== "borrador" ||
    busy ||
    !valid ||
    props.blocked ||
    uncertain;
  const risk = (index: number, next: RiskRating) =>
    setAnalysis((v) => ({ ...v, risks: v.risks.map((r, i) => (i === index ? next : r)) }));
  const control = (index: number, next: ControlRating) =>
    setAnalysis((v) => ({ ...v, controls: v.controls.map((c, i) => (i === index ? next : c)) }));
  const valuation = valid ? support?.risk_evaluation : null;
  return (
    <section
      id="licitud-support-panel"
      hidden={props.hidden}
      className="min-w-0 space-y-4 break-words rounded border p-4"
      aria-label="Valoración y anexos de la evaluación"
    >
      <h2 className="text-xl font-semibold">
        {props.mode === "risks"
          ? "Valorar riesgos para las personas"
          : props.mode === "annexes"
            ? "Anexos de respaldo"
            : "Valoración guardada y anexos de respaldo"}
      </h2>
      <p>
        Solo datos ficticios. Los registros se conservan con nuevas revisiones; no modifican
        resoluciones anteriores ni habilitan EIPD.
      </p>
      {props.mode === "review" && <SaveFeedback error={error} />}
      <button type="button" disabled={busy} onClick={() => void loadRef.current()}>
        Consultar valoración y anexos
      </button>
      {props.blocked && (
        <p role="note">
          Guarda primero los cambios del documento antes de valorar riesgos o adjuntar respaldo.
        </p>
      )}
      {valuation && !valuation.current && (
        <p role="note" className="rounded border border-amber-400 bg-amber-50 p-3">
          El documento cambió desde la revisión {valuation.revision}. Esta valoración es histórica;
          revisa los datos y guarda una nueva revisión.
        </p>
      )}
      {props.mode === "risks" && (
        <>
          <details className="rounded bg-blue-50 p-3">
            <summary className="font-semibold">
              Metodología CUMPLEIA-CUALITATIVA-1 y criterios
            </summary>
            <p>
              Metodología interna de ensayo, no matriz impuesta por ley. El impacto mide daño a
              titulares: discriminación, exposición, pérdida de control o impedimento de derechos.
              Valora sin controles el riesgo inherente y conserva los fundamentos.
            </p>
            <p>
              Probabilidad: baja (circunstancias excepcionales); media (escenario plausible); alta
              (exposición recurrente o antecedentes relevantes); muy alta (condiciones favorables al
              daño presentes de forma persistente). Declara el horizonte temporal y los
              antecedentes, sin inventar porcentajes.
            </p>
            <p>
              Impacto: bajo (molestias limitadas y reversibles); moderado (consecuencias relevantes
              recuperables); grave (perjuicio serio o dificultad significativa para ejercer
              derechos); muy grave (daño extremo o difícilmente reversible). No se evalúa la pérdida
              económica de la organización.
            </p>
            <div
              className="max-w-full overflow-x-auto"
              role="region"
              aria-label="Matriz de valoración; desplazamiento horizontal"
              tabIndex={0}
            >
              <table className="w-full min-w-[480px] border">
                <caption>Matriz: filas de probabilidad, columnas de impacto</caption>
                <thead>
                  <tr>
                    <th>Probabilidad / impacto</th>
                    {["Bajo", "Moderado", "Grave", "Muy grave"].map((t) => (
                      <th key={t}>{t}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {matrix.map((row, i) => (
                    <tr key={i}>
                      <th>{["Baja", "Media", "Alta", "Muy alta"][i]}</th>
                      {row.map((level, j) => (
                        <td key={j}>{levelLabels[level]}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p>
              El residual previsto sirve para planificar. El residual actual exige todos los
              controles asociados verificados, declarados implementados y con evidencias. No se
              restan porcentajes ni se presume eficacia. El resumen conserva el mayor nivel y señala
              por separado los riesgos sin resolver, sin promediar.
            </p>
          </details>
          <fieldset disabled={disabled} className="space-y-4">
            <TextField
              label="Horizonte temporal de la valoración"
              value={analysis.horizon}
              onChange={(horizon) => setAnalysis((v) => ({ ...v, horizon }))}
            />
            {!analysis.risks.length && (
              <p>Guarda riesgos con identificadores en Documentar EIPD antes de valorarlos.</p>
            )}
            {analysis.risks.map((item, index) => (
              <section key={item.risk_id} className="space-y-3 rounded border p-3">
                <h3 className="bg-blue-100 p-2 font-semibold">Riesgo {item.risk_id}</h3>
                <TextField
                  label={`${item.risk_id} — Daño potencial a las personas`}
                  value={item.harm}
                  onChange={(harm) => risk(index, { ...item, harm })}
                />
                <TextField
                  label={`${item.risk_id} — Antecedentes de frecuencia y exposición`}
                  value={item.frequency_context}
                  onChange={(frequency_context) => risk(index, { ...item, frequency_context })}
                />
                {(
                  [
                    ["inherent", "Inherente, antes de controles"],
                    ["projected", "Residual previsto"],
                    ["residual", "Residual actual verificado"],
                  ] as const
                ).map(([key, label]) => (
                  <RatingFields
                    key={key}
                    label={`${item.risk_id} — ${label}`}
                    help={
                      key === "projected"
                        ? "Es el riesgo que se espera que permanezca si las medidas propuestas se implementan y funcionan como se prevé. Sirve para planificar; no acredita una reducción del riesgo actual."
                        : key === "residual"
                          ? "Es el riesgo que permanece con las medidas ya implementadas y su funcionamiento comprobado mediante evidencias. Mientras falte esa verificación, deja esta valoración sin evaluar y utiliza el residual previsto."
                          : undefined
                    }
                    value={item[key]}
                    onChange={(next) => risk(index, { ...item, [key]: next })}
                  />
                ))}
                <TextField
                  label={`${item.risk_id} — Acción de tratamiento`}
                  value={item.action}
                  onChange={(action) => risk(index, { ...item, action })}
                />
                <TextField
                  label={`${item.risk_id} — Responsable ficticio`}
                  value={item.owner_reference}
                  onChange={(owner_reference) => risk(index, { ...item, owner_reference })}
                />
                <TextField
                  label={`${item.risk_id} — Fecha de revisión`}
                  value={item.review_on ?? ""}
                  type="date"
                  onChange={(review_on) => risk(index, { ...item, review_on: review_on || null })}
                />
              </section>
            ))}
            {analysis.controls.map((item, index) => (
              <section key={item.measure_id} className="space-y-3 rounded border p-3">
                <h3 className="bg-blue-100 p-2 font-semibold">Control {item.measure_id}</h3>
                {(
                  [
                    [
                      "dimension",
                      "Dimensión de mitigación",
                      [
                        ["probabilidad", "Probabilidad"],
                        ["impacto", "Impacto"],
                        ["ambos", "Ambos"],
                      ],
                    ],
                    [
                      "effectiveness",
                      "Eficacia cualitativa",
                      [
                        ["no_evaluada", "No evaluada"],
                        ["insuficiente", "Insuficiente"],
                        ["parcial", "Parcial"],
                        ["suficiente", "Suficiente"],
                      ],
                    ],
                    [
                      "status",
                      "Estado de verificación",
                      [
                        ["propuesta", "Propuesta"],
                        ["en_implementacion", "En implementación"],
                        ["verificada", "Verificada"],
                      ],
                    ],
                  ] as const
                ).map(([key, label, choices]) => (
                  <label key={key} className="block">
                    {label}
                    <select
                      aria-label={`${item.measure_id} — ${label}`}
                      className={textClass}
                      value={item[key] ?? ""}
                      onChange={(e) => control(index, { ...item, [key]: e.target.value || null })}
                    >
                      {key === "dimension" && <option value="">Sin declarar</option>}
                      {choices.map(([code, text]) => (
                        <option key={code} value={code}>
                          {text}
                        </option>
                      ))}
                    </select>
                  </label>
                ))}
                <p className="text-sm">
                  Probabilidad: reduce que el daño ocurra. Impacto: reduce sus consecuencias.
                  Eficacia insuficiente/parcial/suficiente requiere fundamento; no es un porcentaje.
                  Verificada exige implementación y evidencias registradas; declarar una propuesta
                  no acredita mitigación actual.
                </p>
                <TextField
                  label={`${item.measure_id} — Fundamento de mitigación`}
                  value={item.rationale}
                  onChange={(rationale) => control(index, { ...item, rationale })}
                />
                <TextField
                  label={`${item.measure_id} — Referencias de evidencia o anexos, una por línea`}
                  value={item.evidence_references.join("\n")}
                  onChange={(v) =>
                    control(index, {
                      ...item,
                      evidence_references: v
                        .split("\n")
                        .map((s) => s.trim())
                        .filter(Boolean),
                    })
                  }
                />
              </section>
            ))}
            <SaveFeedback
              error={error}
              message={message}
              busy={busy}
              dirty={analysisDirty}
              dirtyMessage="Cambios pendientes de guardar en valoración. Se conservan al navegar."
            />
            <button
              className="rounded bg-blue-800 px-3 py-2 text-white disabled:opacity-50"
              type="button"
              disabled={disabled || !analysis.risks.length}
              onClick={() => void mutate("risk")}
            >
              {busy ? "Guardando valoración…" : "Guardar valoración de riesgos"}
            </button>
          </fieldset>
        </>
      )}
      {props.mode === "review" && (
        <>
          {valuation ? (
            <div className="rounded bg-blue-50 p-3">
              <p>
                Valoración revisión {valuation.revision} ·{" "}
                {valuation.current
                  ? "asociada al documento actual"
                  : "histórica, requiere reevaluación"}
              </p>
              {valuation.result.worst_residual === "sin_resolver" ? (
                <p>
                  <strong>Evaluación del riesgo residual actual pendiente.</strong> Hay riesgos sin
                  evaluar o sin verificación suficiente de sus controles. Todavía no puede
                  determinarse el nivel residual actual del conjunto.
                </p>
              ) : (
                <>
                  <p>
                    Nivel más alto de riesgo residual actual entre los riesgos evaluados:{" "}
                    <strong>{levelLabels[valuation.result.worst_residual]}</strong>.
                  </p>
                  {valuation.result.unresolved && (
                    <p>
                      Hay riesgos pendientes de evaluación o verificación. Este nivel no resume el
                      conjunto completo.
                    </p>
                  )}
                  <p>
                    La valoración está guardada. Una persona responsable debe revisar sus
                    fundamentos y evidencias antes de aprobarla.
                  </p>
                </>
              )}
            </div>
          ) : (
            <p>Sin valoración estructurada guardada.</p>
          )}
        </>
      )}
      {(props.mode === "annexes" || props.mode === "review") && (
        <>
          <h3 className="font-semibold">Anexos guardados</h3>
          <p>
            PDF o TXT UTF-8, hasta 2 MiB por archivo y 20 MiB/50 anexos por evaluación. Las
            versiones se conservan. El JSON incluye el índice y hashes; los archivos se descargan
            por separado.
          </p>
          {!support?.annexes.length && <p>Sin anexos registrados.</p>}
          {support?.annexes.map((item) => (
            <article key={item.id} className="space-y-2 rounded border p-3">
              <h4 className="font-semibold text-blue-900">
                {item.reference} · versión {item.version}
              </h4>
              <p>
                {item.filename} — {item.description}
              </p>
              <dl className="space-y-1">
                <div>
                  <dt className="inline font-semibold">Sección relacionada: </dt>
                  <dd className="inline">
                    {annexSections[item.section] ?? "Sección no identificada"}
                  </dd>
                </div>
                <div>
                  <dt className="inline font-semibold">Riesgos vinculados: </dt>
                  <dd className="inline">
                    {item.risk_ids.join(", ") || "Sin vínculos registrados"}
                  </dd>
                </div>
                <div>
                  <dt className="inline font-semibold">Medidas vinculadas: </dt>
                  <dd className="inline">
                    {item.measure_ids.join(", ") || "Sin vínculos registrados"}
                  </dd>
                </div>
              </dl>
              <button
                type="button"
                disabled={busy}
                onClick={() =>
                  void scope()
                    .then((s) => supportApi.download(s, item))
                    .catch(() => setError("No se pudo descargar y comprobar el anexo."))
                }
              >
                Descargar {item.reference} versión {item.version}
              </button>
            </article>
          ))}
          {props.mode === "annexes" && (
            <fieldset disabled={disabled} className="space-y-3">
              <legend>Agregar anexo ficticio</legend>
              <TextField
                label="Referencia del anexo (SIMULADA-)"
                value={annex.reference}
                onChange={(reference) => setAnnex((v) => ({ ...v, reference }))}
              />
              <TextField
                label="Descripción del anexo"
                value={annex.description}
                onChange={(description) => setAnnex((v) => ({ ...v, description }))}
              />
              <label>
                Sección relacionada
                <select
                  aria-label="Sección relacionada"
                  className={textClass}
                  value={annex.section}
                  onChange={(e) => setAnnex((v) => ({ ...v, section: e.target.value }))}
                >
                  {Object.entries(annexSections).map(([code, label]) => (
                    <option key={code} value={code}>
                      {label}
                    </option>
                  ))}
                </select>
              </label>
              <p className="text-sm">
                Elige la parte del documento que respalda este archivo. Puedes adjuntar respaldo de
                alcance, base de licitud u otra sección sin vincularlo a riesgos o medidas.
              </p>
              <details className="space-y-3 rounded border p-3">
                <summary>Vínculos opcionales con riesgos y medidas</summary>
                <p className="text-sm">
                  Completa estos vínculos solo si el archivo respalda riesgos o medidas específicos.
                  Son independientes de la sección elegida; puedes dejarlos vacíos. Usa códigos ya
                  guardados en esta evaluación, un código por línea, no descripciones. Cambiar la
                  sección conserva los vínculos que hayas escrito.
                </p>
                <TextField
                  label="Códigos de riesgos vinculados (opcional; ejemplo: R1)"
                  value={annex.risk_ids}
                  onChange={(risk_ids) => setAnnex((v) => ({ ...v, risk_ids }))}
                />
                <TextField
                  label="Códigos de medidas vinculadas (opcional; ejemplo: M1)"
                  value={annex.measure_ids}
                  onChange={(measure_ids) => setAnnex((v) => ({ ...v, measure_ids }))}
                />
              </details>
              <label className="block">
                Archivo ficticio PDF o TXT
                <input
                  key={support?.annexes.length ?? 0}
                  type="file"
                  className="block max-w-full"
                  accept=".pdf,.txt"
                  aria-label="Archivo ficticio PDF o TXT"
                  aria-describedby="annex-file-help"
                  aria-invalid={Boolean(file && annexFileError(file))}
                  onChange={(e) => {
                    setFile(e.target.files?.[0] ?? null);
                    setError("");
                    setMessage("");
                  }}
                />
              </label>
              <p
                id="annex-file-help"
                className={
                  file && annexFileError(file)
                    ? "rounded border border-red-600 bg-red-50 p-3 text-red-950"
                    : "text-slate-700"
                }
              >
                {(file && annexFileError(file)) ||
                  "Formatos admitidos: PDF o TXT UTF-8. Tamaño máximo: 2 MiB por archivo."}
              </p>
              <label className="block">
                <input
                  type="checkbox"
                  checked={fictitious}
                  onChange={(e) => setFictitious(e.target.checked)}
                />{" "}
                Confirmo que el archivo y sus datos son ficticios
              </label>
              <SaveFeedback
                error={error}
                message={message}
                busy={busy}
                dirty={annexDirty && !message}
                dirtyMessage="Anexo pendiente de guardar. Los campos se conservan al corregir el archivo."
              />
              <button
                className="rounded bg-blue-800 px-3 py-2 text-white disabled:opacity-50"
                type="button"
                disabled={disabled || !file || !fictitious}
                onClick={() => void mutate("annex")}
              >
                {busy ? "Guardando anexo…" : "Guardar anexo ficticio"}
              </button>
            </fieldset>
          )}
        </>
      )}
      <p>
        Activación EIPD bloqueada. Guardar una valoración o adjuntar documentos no equivale a
        revisión jurídica.
      </p>
    </section>
  );
}
