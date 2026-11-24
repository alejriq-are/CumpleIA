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
export function ChildAdolescentEditor({
  load,
  save,
  readiness,
  readOnly = false,
  refreshVersion = 0,
  onSaved,
  onDirty,
  onWorkState,
}: Props) {
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
              <fieldset>
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
                <fieldset key={field}>
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
                Ruta propuesta
                <select
                  className="block rounded border p-2"
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
              <ul className="list-disc pl-5">
                {ready.eipd_controls_v5.confirmation_blockers.map((i, n) => (
                  <li key={n}>{i.message}</li>
                ))}
              </ul>
            </section>
          )}
        </>
      )}
    </section>
  );
}
