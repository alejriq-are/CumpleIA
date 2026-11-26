"use client";
import { useWorkState, type WorkReporter } from "@/components/navigation/work-unit-state";
import { useEffect, useRef, useState } from "react";
import { ApiError } from "@/lib/api/client";
import type { ChildAssessment, ChildDocument, ChildReadiness } from "@/lib/api/child-adolescent";
type Props = {
  load: () => Promise<ChildAssessment>;
  save: (doc: ChildDocument | null) => Promise<ChildAssessment>;
  readiness: () => Promise<ChildReadiness>;
  readOnly?: boolean;
  refreshVersion?: number;
  onSaved?: () => void;
  onDirty?: (dirty: boolean) => void;
  onWorkState?: WorkReporter;
  onOpenAssessmentSection?: (section: "alcance" | "base") => void;
};
const textFields = [
  ["age_scope_analysis", "Análisis de edad y alcance"],
  ["best_interests_analysis", "Interés superior"],
  ["progressive_autonomy_analysis", "Autonomía progresiva"],
  ["authorization_reference", "Referencia de autorización"],
  ["authorization_analysis", "Análisis de autorización"],
  ["notes", "Notas"],
] as const;
const groups = [
  ["ninos_ninas", "Niños y niñas"],
  ["adolescentes", "Adolescentes"],
  ["adolescentes_sensibles_menores_16", "Adolescentes menores de 16 con datos sensibles"],
] as const;
const pendingFields: Record<string, [string, string]> = {
  age_scope_analysis: ["Edad y alcance", "Falta explicar las edades y el alcance del tratamiento."],
  best_interests_analysis: [
    "Interés superior",
    "Falta explicar cómo se considera el interés superior.",
  ],
  progressive_autonomy_analysis: [
    "Autonomía progresiva",
    "Falta explicar cómo se considera la autonomía progresiva.",
  ],
  authorization_reference: ["Autorizaciones", "Falta indicar la referencia de la autorización."],
  authorization_analysis: [
    "Autorizaciones",
    "Falta explicar el fundamento de la autorización propuesta.",
  ],
  declared_groups: ["Edad y alcance", "Falta declarar los grupos de edad incluidos."],
  data_category_codes: ["Edad y alcance", "Falta seleccionar las categorías de datos incluidas."],
  data_subject_codes: ["Edad y alcance", "Falta seleccionar los grupos de titulares incluidos."],
  proposed_authorization_route: [
    "Autorizaciones",
    "Falta elegir la vía de autorización propuesta.",
  ],
  declared_consent_giver: ["Autorizaciones", "Falta indicar quién otorgaría el consentimiento."],
  sensitive_under16: [
    "Edad y alcance",
    "Falta aclarar si se tratan datos sensibles de adolescentes menores de 16 años.",
  ],
  evidence: ["Evidencias", "Falta incorporar una evidencia con su referencia."],
  rat_context_snapshot: [
    "Alcance del RAT",
    "No se pudo comprobar el alcance del RAT asociado a la evaluación.",
  ],
  child_adolescent_assessment: [
    "Documento de infancia",
    "Revisa el documento de infancia guardado y su asociación con esta evaluación.",
  ],
};
const pendingReasons: Record<string, string> = {
  expediente_infancia_ausente:
    "Todavía no hay un documento de infancia guardado en esta evaluación.",
  asociacion_ausente: "Falta asociar el documento de infancia a la evaluación.",
  asociacion_contexto_obsoleta: "La asociación corresponde a un alcance anterior de la evaluación.",
  asociacion_documento_obsoleta: "La asociación corresponde a un contenido anterior del documento.",
  codigo_ajeno_al_alcance: "Hay una selección que no pertenece al alcance del RAT guardado.",
  grupos_rat_incoherentes:
    "Los grupos de edad declarados no coinciden con el alcance del RAT guardado.",
  cruce_sensible_edad_incoherente:
    "La declaración de datos sensibles no coincide con los grupos de edad seleccionados.",
  subgrupo_edad_incoherente:
    "El grupo de menores de 16 años con datos sensibles no coincide con lo declarado.",
  otorgante_requiere_revision:
    "Revisa si el otorgante declarado corresponde a los grupos incluidos.",
  autorizacion_legal_infancia_revision_pendiente: "La vía de autorización legal requiere revisión.",
  grupos_mixtos_revision_pendiente:
    "Revisa por separado los requisitos de los distintos grupos de edad.",
  expediente_infancia_residual:
    "Hay un documento de infancia conservado que requiere revisar su pertinencia para este alcance.",
  resumen_rat_incoherente: "Los antecedentes de infancia del alcance guardado requieren revisión.",
  consentimiento_relacionado_pendiente:
    "Falta indicar quién otorga el consentimiento en Base y fundamento.",
  relacion_otorgante_no_comparable:
    "No se pudo comparar el otorgante del documento de infancia con el del consentimiento.",
  otorgante_documental_incoherente:
    "El otorgante declarado no coincide con el registrado en Consentimiento.",
  consentimiento_sensible_relacionado_pendiente:
    "Revisa el consentimiento relacionado con los datos sensibles de adolescentes menores de 16 años.",
  declaraciones_especiales_pendientes:
    "Falta completar las declaraciones sobre condiciones especiales del tratamiento.",
  condicion_infancia_pendiente:
    "Falta documentar la condición de infancia en las condiciones especiales.",
  ruta_especial_pendiente: "Falta indicar la vía de autorización en las condiciones especiales.",
  ruta_especial_incoherente:
    "La vía de autorización de las condiciones especiales no coincide con la del documento de infancia.",
};
const ageLabels: Record<string, string> = {
  ninos_ninas: "niños y niñas",
  adolescentes: "adolescentes",
  datos_sensibles_adolescentes_menores_16: "datos sensibles de adolescentes menores de 16 años",
};

export function ChildAdolescentEditor({
  load,
  save,
  readiness,
  readOnly = false,
  refreshVersion = 0,
  onSaved,
  onDirty,
  onWorkState,
  onOpenAssessmentSection,
}: Props) {
  const formRef = useRef<HTMLFormElement>(null);
  const [row, setRow] = useState<ChildAssessment | null>(null),
    [doc, setDoc] = useState<ChildDocument>({}),
    [ready, setReady] = useState<ChildReadiness | null>(null),
    [busy, setBusy] = useState(true),
    [error, setError] = useState(""),
    [message, setMessage] = useState("");
  const [uncertain, setUncertain] = useState(false);
  const running = useRef(false);
  const [baseline, setBaseline] = useState("{}");
  const dirty = Boolean(row && JSON.stringify(doc) !== baseline);
  useWorkState(onWorkState, {
    loaded: !!row,
    loading: !row && busy,
    saving: !!row && busy,
    dirty,
    saved: !!message,
    error: !!error,
    uncertain,
  });
  useEffect(() => {
    onDirty?.(dirty || busy || uncertain);
  }, [dirty, busy, uncertain, onDirty]);
  useEffect(() => {
    if (!refreshVersion) return;
    let active = true;
    setReady(null);
    readiness()
      .then((value) => {
        if (active) setReady(value);
      })
      .catch(() => {
        if (active)
          setError(
            "No se pudo actualizar el diagnóstico. Los cambios del formulario se conservan; consulta nuevamente antes de preparar documentos."
          );
      });
    return () => {
      active = false;
    };
  }, [refreshVersion, readiness]);
  useEffect(() => {
    let active = true;
    setRow(null);
    setReady(null);
    setError("");
    setBusy(true);
    Promise.all([load(), readiness()])
      .then(([r, d]) => {
        if (active) {
          setRow(r);
          setDoc(r.child_adolescent_assessment?.assessment ?? {});
          setBaseline(JSON.stringify(r.child_adolescent_assessment?.assessment ?? {}));
          setReady(d);
        }
      })
      .catch(() => {
        if (active) setError("No se pudo cargar el expediente. Revisa tu sesión y permisos.");
      })
      .finally(() => {
        if (active) setBusy(false);
      });
    return () => {
      active = false;
    };
  }, [load, readiness]);
  async function persist(remove = false) {
    if (running.current || uncertain || !row || readOnly || row.status !== "borrador") return;
    running.current = true;
    setBusy(true);
    setError("");
    setMessage("");
    setReady(null);
    try {
      const r = await save(remove ? null : doc);
      setRow(r);
      setDoc(r.child_adolescent_assessment?.assessment ?? {});
      setBaseline(JSON.stringify(r.child_adolescent_assessment?.assessment ?? {}));
      onSaved?.();
      setMessage(remove ? "Documento retirado del borrador." : "Documento guardado.");
      setReady(null);
      try {
        setReady(await readiness());
      } catch {
        setError(
          "El documento se guardó, pero no se pudo actualizar el diagnóstico. Recarga para consultarlo."
        );
      }
    } catch (cause) {
      setUncertain(!(cause instanceof ApiError) || cause.status >= 500 || cause.status === 408);
      setError(
        "No se confirmó el guardado. Conservamos tus cambios; recarga antes de volver a intentar."
      );
    } finally {
      running.current = false;
      setBusy(false);
    }
  }
  function moveEvidence(from: number, to: number) {
    if (from === to || from < 0 || to < 0) return;
    setDoc((d) => {
      const list = d.evidence;
      if (!list || from >= list.length || to >= list.length) return d;
      const next = list.slice();
      const [item] = next.splice(from, 1);
      next.splice(to, 0, item);
      return { ...d, evidence: next };
    });
  }
  function selection(
    field: "data_category_codes" | "data_subject_codes",
    value: string,
    on: boolean
  ) {
    setDoc((d) => ({
      ...d,
      [field]: on ? [...(d[field] ?? []), value] : (d[field] ?? []).filter((x) => x !== value),
    }));
  }
  return (
    <section className="space-y-5">
      <p className="rounded border border-blue-200 bg-blue-50 p-4">
        Pruebas de desarrollo: utiliza únicamente datos ficticios. Guardar este documento no
        confirma el expediente ni activa EIPD.
      </p>
      {error && (
        <p role="alert" className="text-red-700">
          {error}
        </p>
      )}
      {message && <p role="status">{message}</p>}
      {uncertain && (
        <button type="button" onClick={() => window.location.reload()}>
          Recargar expediente
        </button>
      )}
      {busy && !row && <p>Cargando expediente…</p>}
      {row && (
        <>
          <p>Estado del expediente: {row.status}.</p>
          <p
            role="note"
            className={dirty ? "rounded border border-amber-400 bg-amber-50 p-3" : "text-sm"}
          >
            {dirty
              ? "Infancia: cambios sin guardar. Se conservan entre pestañas; guarda antes de preparar una versión."
              : "Documento de infancia cargado del servidor; completa esta sección solo cuando corresponda al alcance."}
          </p>
          {(readOnly || row.status !== "borrador") && <p>Consulta de solo lectura.</p>}
          <form
            ref={formRef}
            onSubmit={(e) => {
              e.preventDefault();
              void persist();
            }}
            className="space-y-4 rounded border bg-white p-5"
          >
            <fieldset
              disabled={busy || uncertain || readOnly || row.status !== "borrador"}
              className="space-y-4"
            >
              <legend className="font-semibold">Documento de infancia y adolescencia</legend>
              <fieldset data-pending-field="declared_groups" tabIndex={-1}>
                <legend>Grupos declarados</legend>
                {groups.map(([value, label]) => (
                  <label key={value} className="block">
                    <input
                      type="checkbox"
                      checked={(doc.declared_groups ?? []).includes(value)}
                      onChange={(e) =>
                        setDoc((d) => ({
                          ...d,
                          declared_groups: e.target.checked
                            ? [...(d.declared_groups ?? []), value]
                            : (d.declared_groups ?? []).filter((x) => x !== value),
                        }))
                      }
                    />{" "}
                    {label}
                  </label>
                ))}
              </fieldset>
              {(
                [
                  [
                    "data_category_codes",
                    "Categorías de datos",
                    row.rat_context_snapshot.data_categories,
                  ],
                  [
                    "data_subject_codes",
                    "Grupos de titulares",
                    row.rat_context_snapshot.data_subjects,
                  ],
                ] as const
              ).map(([field, label, items]) => (
                <fieldset key={field} data-pending-field={field} tabIndex={-1}>
                  <legend>{label}</legend>
                  {items.map((item) => (
                    <label className="block" key={item.category_code}>
                      <input
                        type="checkbox"
                        checked={(doc[field] ?? []).includes(item.category_code)}
                        onChange={(e) => selection(field, item.category_code, e.target.checked)}
                      />{" "}
                      {item.category_name}
                    </label>
                  ))}
                </fieldset>
              ))}
              {textFields.map(([field, label]) => (
                <label className="block" key={field}>
                  {label}
                  <textarea
                    data-pending-field={field}
                    aria-label={label}
                    className="mt-1 block w-full rounded border p-2"
                    value={doc[field] ?? ""}
                    onChange={(e) => setDoc((d) => ({ ...d, [field]: e.target.value || null }))}
                  />
                </label>
              ))}
              <label className="block">
                Datos sensibles de adolescentes menores de 16
                <select
                  className="block rounded border p-2"
                  data-pending-field="sensitive_under16"
                  value={doc.sensitive_under16 ?? ""}
                  onChange={(e) =>
                    setDoc((d) => ({
                      ...d,
                      sensitive_under16: (e.target.value ||
                        null) as ChildDocument["sensitive_under16"],
                    }))
                  }
                >
                  <option value="">Sin declarar</option>
                  <option value="si">Sí</option>
                  <option value="no">No</option>
                  <option value="pendiente">Pendiente</option>
                </select>
              </label>
              <label className="block">
                Autorización propuesta
                <select
                  className="block rounded border p-2"
                  data-pending-field="proposed_authorization_route"
                  value={doc.proposed_authorization_route ?? ""}
                  onChange={(e) =>
                    setDoc((d) => ({
                      ...d,
                      proposed_authorization_route: (e.target.value ||
                        null) as ChildDocument["proposed_authorization_route"],
                    }))
                  }
                >
                  <option value="">Sin declarar</option>
                  <option value="consentimiento">Consentimiento</option>
                  <option value="autorizacion_legal_expresa">Autorización legal expresa</option>
                </select>
              </label>
              <label className="block">
                Otorgante declarado
                <select
                  className="block rounded border p-2"
                  data-pending-field="declared_consent_giver"
                  value={doc.declared_consent_giver ?? ""}
                  onChange={(e) =>
                    setDoc((d) => ({
                      ...d,
                      declared_consent_giver: (e.target.value ||
                        null) as ChildDocument["declared_consent_giver"],
                    }))
                  }
                >
                  <option value="">Sin declarar</option>
                  <option value="padre_madre">Padre o madre</option>
                  <option value="representante_legal">Representante legal</option>
                  <option value="cuidado_personal">Cuidado personal</option>
                  <option value="titular">Titular</option>
                </select>
              </label>
              {(doc.evidence ?? []).map((evidence, index) => (
                <div key={index} className="space-y-2 rounded border p-3">
                  <label className="block">
                    Tipo de evidencia {index + 1}
                    <input
                      className="block w-full rounded border p-2"
                      value={evidence.evidence_type}
                      onChange={(e) =>
                        setDoc((d) => ({
                          ...d,
                          evidence: d.evidence?.map((v, i) =>
                            i === index ? { ...v, evidence_type: e.target.value } : v
                          ),
                        }))
                      }
                    />
                  </label>
                  <label className="block">
                    Referencia de evidencia {index + 1}
                    <input
                      className="block w-full rounded border p-2"
                      value={evidence.reference ?? ""}
                      onChange={(e) =>
                        setDoc((d) => ({
                          ...d,
                          evidence: d.evidence?.map((v, i) =>
                            i === index ? { ...v, reference: e.target.value || null } : v
                          ),
                        }))
                      }
                    />
                  </label>
                  <button
                    type="button"
                    disabled={
                      index === 0 || busy || uncertain || readOnly || row.status !== "borrador"
                    }
                    onClick={() => moveEvidence(index, index - 1)}
                  >
                    Subir evidencia {index + 1}
                  </button>
                  <button
                    type="button"
                    disabled={
                      index === (doc.evidence?.length ?? 1) - 1 ||
                      busy ||
                      uncertain ||
                      readOnly ||
                      row.status !== "borrador"
                    }
                    onClick={() => moveEvidence(index, index + 1)}
                  >
                    Bajar evidencia {index + 1}
                  </button>
                  <button
                    type="button"
                    onClick={() =>
                      setDoc((d) => ({ ...d, evidence: d.evidence?.filter((_, i) => i !== index) }))
                    }
                  >
                    Quitar evidencia {index + 1}
                  </button>
                </div>
              ))}
              <button
                type="button"
                data-pending-field="evidence"
                onClick={() =>
                  setDoc((d) => ({
                    ...d,
                    evidence: [...(d.evidence ?? []), { evidence_type: "", reference: null }],
                  }))
                }
              >
                Añadir evidencia
              </button>
              <div className="flex flex-wrap gap-3">
                <button className="rounded bg-blue-700 px-4 py-2 text-white" type="submit">
                  Guardar documento
                </button>
                <button
                  type="button"
                  disabled={!row.child_adolescent_assessment}
                  onClick={() => void persist(true)}
                >
                  Retirar documento del borrador
                </button>
              </div>
            </fieldset>
          </form>
          {ready?.eipd_controls_v5 && (
            <section className="rounded border p-4">
              <h2 className="font-semibold">Requisitos EIPD de infancia</h2>
              <p>Confirmación y activación bloqueadas.</p>
              <p>
                {ready.eipd_controls_v5.child_adolescent_coverage === "contexto_v4"
                  ? "La consulta incluye infancia en el contexto actual."
                  : "No se dispone del contexto actual; requiere revisión."}
              </p>
              <p>Las resoluciones anteriores no cubren este documento.</p>
              <p className="mt-2">Los pendientes se basan en el contenido guardado.</p>
              {(() => {
                const controls = ready.eipd_controls_v5;
                const issues = controls.child_adolescent.issues ?? [];
                const rows = new Map<
                  string,
                  {
                    section: string;
                    message: string;
                    target?: string;
                    destination?: "alcance" | "base";
                    guidance?: string;
                  }
                >();
                for (const issue of issues) {
                  const field = pendingFields[issue.field.split(".")[0]];
                  const age = ageLabels[issue.field.split(".").at(-1) ?? ""];
                  const ageMessage =
                    age &&
                    (
                      {
                        declaracion_edad_pendiente: "Falta completar la declaración sobre",
                        fundamento_declaracion_pendiente:
                          "Falta explicar el fundamento de la declaración sobre",
                        alcance_edad_no_comparable:
                          "No se pudo comparar con el RAT la declaración sobre",
                        declaracion_edad_incoherente: "No coincide con el RAT la declaración sobre",
                      } as Record<string, string>
                    )[issue.code];
                  const message =
                    (issue.code === "codigo_ajeno_al_alcance"
                      ? issue.field === "data_category_codes"
                        ? "Una categoría de datos seleccionada no pertenece al alcance del RAT guardado."
                        : "Un grupo de titulares seleccionado no pertenece al alcance del RAT guardado."
                      : pendingReasons[issue.code]) ??
                    (ageMessage ? ageMessage + " " + age + "." : undefined) ??
                    field?.[1] ??
                    "Revisa los antecedentes relacionados con infancia y adolescencia.";
                  const section =
                    field?.[0] ??
                    (issue.field.startsWith("consent_assessment")
                      ? "Consentimiento"
                      : issue.field.startsWith("special_conditions_document")
                        ? "Condiciones especiales"
                        : "Documento de infancia");
                  const target =
                    field &&
                    !["rat_context_snapshot", "child_adolescent_assessment"].includes(
                      issue.field.split(".")[0]
                    )
                      ? issue.field
                      : undefined;
                  const destination = issue.field.startsWith("consent_assessment")
                    ? "base"
                    : issue.field === "rat_context_snapshot"
                      ? "alcance"
                      : undefined;
                  rows.set(section + message, {
                    section,
                    message,
                    target,
                    destination,
                    guidance:
                      section === "Condiciones especiales"
                        ? "Requiere revisión de las condiciones especiales. Este formulario no permite editarlas."
                        : undefined,
                  });
                }
                for (const blocker of controls.confirmation_blockers) {
                  if (issues.some((issue) => issue.code === blocker.code)) continue;
                  if (blocker.code === "politica_infancia_no_implementada") continue;
                  const section = "Requisitos de la evaluación";
                  const message = blocker.message;
                  const guidance = {
                    condiciones_especiales_no_preparadas:
                      "Requiere revisión de las condiciones especiales. Este formulario no permite editarlas.",
                    screening_eipd_no_preparado:
                      "Requiere revisar el análisis previo de EIPD. Esta pantalla no permite completarlo.",
                    infancia_confirmacion_bloqueada:
                      "La confirmación permanece bloqueada en el piloto.",
                  }[blocker.code as string];
                  rows.set(section + message, { section, message, guidance });
                }
                return rows.size ? (
                  <details className="mt-3">
                    <summary className="cursor-pointer rounded border border-blue-300 bg-blue-50 p-3 font-semibold">
                      Detalle de pendientes documentales ({rows.size})
                    </summary>
                    <table className="mt-2 w-full table-fixed break-words text-left text-sm">
                      <thead>
                        <tr>
                          {["Sección", "Pendiente", "Acción"].map((label) => (
                            <th key={label} scope="col" className="border bg-blue-50 p-2">
                              {label}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {[...rows.entries()].map(
                          ([key, { section, message, target, destination, guidance }]) => (
                            <tr key={key}>
                              <td className="border p-2 align-top">{section}</td>
                              <td className="border p-2 align-top">{message}</td>
                              <td className="border p-2 align-top">
                                {target &&
                                !busy &&
                                !uncertain &&
                                !readOnly &&
                                row.status === "borrador" ? (
                                  <button
                                    type="button"
                                    className="rounded border border-blue-300 bg-blue-50 p-2 font-semibold text-blue-800"
                                    onClick={() => {
                                      const control = formRef.current?.querySelector<HTMLElement>(
                                        `[data-pending-field="${target}"]`
                                      );
                                      const focusTarget =
                                        control?.querySelector<HTMLElement>("input:enabled") ??
                                        control;
                                      focusTarget?.focus({ preventScroll: true });
                                      focusTarget?.scrollIntoView({ block: "center" });
                                    }}
                                  >
                                    Ir al campo
                                  </button>
                                ) : target ? (
                                  "Consulta de solo lectura o edición no disponible."
                                ) : destination && onOpenAssessmentSection ? (
                                  <button
                                    type="button"
                                    className="rounded border border-blue-300 bg-blue-50 p-2 font-semibold text-blue-800"
                                    onClick={() => onOpenAssessmentSection(destination)}
                                  >
                                    {destination === "alcance"
                                      ? "Ir a Alcance del RAT"
                                      : "Ir a Base y fundamento"}
                                  </button>
                                ) : (
                                  (guidance ??
                                  "Requiere revisión de los antecedentes de la evaluación.")
                                )}
                              </td>
                            </tr>
                          )
                        )}
                      </tbody>
                    </table>
                  </details>
                ) : (
                  <p>No se informaron pendientes documentales.</p>
                );
              })()}
            </section>
          )}
        </>
      )}
    </section>
  );
}
