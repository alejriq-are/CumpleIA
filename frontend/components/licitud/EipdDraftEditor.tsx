"use client";
import type { RiskEvaluation } from "@/lib/api/assessment-support";
import { useEffect, useRef, useState } from "react";
import { documentFields } from "@/lib/licitud/eipd-document";
import { ApiError } from "@/lib/api/client";
import {
  eipdDraftApi,
  editableEipd,
  type EipdValue,
  type EipdDiagnostic,
  type EipdDraftRow,
} from "@/lib/api/eipd-draft";
import { EipdDocumentFields, EipdDocumentView } from "./EipdDocumentFields";
import { sessionToken } from "./LicitudWorkspace";
export function EipdDraftEditor({
  organizationId,
  treatmentId,
  assessmentId,
  readOnly,
  token = sessionToken,
  refreshVersion = 0,
  onDirty,
  onSaved,
  onLoaded,
  valuation,
}: {
  organizationId: string;
  treatmentId: string;
  assessmentId: string;
  readOnly: boolean;
  token?: () => Promise<string>;
  refreshVersion?: number;
  onDirty?: (dirty: boolean) => void;
  onSaved?: (row: EipdDraftRow) => void;
  onLoaded?: (row: EipdDraftRow) => void;
  valuation?: RiskEvaluation | null;
}) {
  const [row, setRow] = useState<EipdDraftRow | null>(null);
  const [doc, setDoc] = useState<EipdValue>({ schema_version: 1 });
  const [baseline, setBaseline] = useState("");
  const [diagnostic, setDiagnostic] = useState<EipdDiagnostic | null>(null);
  const [busy, setBusy] = useState(false),
    [uncertain, setUncertain] = useState(false);
  const [error, setError] = useState(""),
    [message, setMessage] = useState("");
  const [preview, setPreview] = useState(false);
  const running = useRef(false),
    alive = useRef(false),
    generation = useRef(0);
  const dirty = Boolean(row && JSON.stringify(doc) !== baseline);
  useEffect(() => {
    onDirty?.(dirty || busy || uncertain);
  }, [dirty, busy, uncertain, onDirty]);
  useEffect(() => {
    let active = true;
    alive.current = true;
    setRow(null);
    setError("");
    setBusy(true);
    (async () => {
      try {
        const scope = { organizationId, treatmentId, token: await token() };
        const loaded = await eipdDraftApi.load(scope, assessmentId);
        if (
          loaded.id !== assessmentId ||
          loaded.organization_id !== organizationId ||
          loaded.treatment_id !== treatmentId ||
          !Object.hasOwn(loaded, "eipd_resolution_assessment")
        )
          throw new Error("Scope incompatible");
        const editable = editableEipd(loaded.eipd_resolution_assessment);
        if (active) {
          setRow(loaded);
          onLoaded?.(loaded);
          setDoc(editable);
          setBaseline(JSON.stringify(editable));
        }
      } catch {
        if (active)
          setError(
            "No se pudo cargar un documento EIPD válido. Revisa sesión y permisos; no se habilita el guardado."
          );
      } finally {
        if (active) setBusy(false);
      }
    })();
    return () => {
      active = false;
      alive.current = false;
    };
  }, [organizationId, treatmentId, assessmentId, token, onLoaded]);
  useEffect(() => {
    let active = true;
    const request = ++generation.current;
    setDiagnostic(null);
    (async () => {
      try {
        const value = await eipdDraftApi.diagnostic(
          { organizationId, treatmentId, token: await token() },
          assessmentId
        );
        if (active && request === generation.current) setDiagnostic(value);
      } catch {
        /* La falta de diagnóstico no se interpreta como suficiencia. */
      }
    })();
    return () => {
      active = false;
    };
  }, [organizationId, treatmentId, assessmentId, token, refreshVersion]);
  useEffect(() => {
    if (dirty) setMessage("");
  }, [dirty]);
  async function save() {
    if (running.current || busy || uncertain || readOnly || row?.status !== "borrador") return;
    running.current = true;
    setBusy(true);
    setError("");
    setMessage("");
    setDiagnostic(null);
    const request = ++generation.current;
    try {
      const scope = { organizationId, treatmentId, token: await token() };
      const saved = await eipdDraftApi.save(scope, assessmentId, doc);
      if (!alive.current) return;
      const value = editableEipd(saved.eipd_resolution_assessment);
      setRow(saved);
      setDoc(value);
      setBaseline(JSON.stringify(value));
      setMessage("Borrador EIPD guardado en servidor. No constituye una evaluación aprobada.");
      onSaved?.(saved);
      try {
        const ready = await eipdDraftApi.diagnostic(scope, assessmentId);
        if (alive.current && request === generation.current) setDiagnostic(ready);
      } catch {
        if (alive.current)
          setError(
            "El borrador se guardó, pero el diagnóstico no está disponible. No se acredita preparación."
          );
      }
    } catch (cause) {
      if (alive.current) {
        const unknown = !(cause instanceof ApiError) || cause.status >= 500 || cause.status === 408;
        setUncertain(unknown);
        setError(
          unknown
            ? "Resultado incierto del guardado EIPD. Conservamos los campos; consulta el expediente antes de reintentar."
            : "Guardado EIPD rechazado. Revisa el formato, permisos y coherencia del contexto; conservamos los cambios."
        );
      }
    } finally {
      running.current = false;
      if (alive.current) setBusy(false);
    }
  }
  const disabled = readOnly || row?.status !== "borrador" || busy || uncertain;
  return (
    <section aria-label="Documento EIPD en borrador" className="space-y-4 rounded border p-4">
      <h2 className="text-xl font-semibold">Documentar EIPD</h2>
      <p>
        Este formulario documenta análisis y evidencias de prueba. Abrirlo no determina que una EIPD
        sea obligatoria. La confirmación y la activación permanecen bloqueadas.
      </p>
      <p
        role="note"
        className={dirty ? "rounded border border-amber-400 bg-amber-50 p-3" : "text-sm"}
      >
        {dirty
          ? "EIPD: cambios sin guardar; se conservan al navegar entre secciones y pestañas."
          : row
            ? "Documento EIPD cargado del servidor. Los pendientes jurídicos no se resuelven al guardar."
            : "Cargando documento EIPD…"}
      </p>
      {error && <p role="alert">{error}</p>}
      {row && (
        <form
          className="space-y-4"
          noValidate
          onSubmit={(event) => {
            event.preventDefault();
            void save();
          }}
        >
          <fieldset disabled={disabled} className="space-y-3">
            <legend>Documento editable · evaluación versión {row.version}</legend>
            <label className="block">
              Referencia del documento EIPD
              <input
                aria-label="Referencia del documento EIPD"
                className="block w-full rounded border p-2"
                value={String(doc.document_reference ?? "")}
                onChange={(e) =>
                  setDoc((value) => ({ ...value, document_reference: e.target.value || null }))
                }
              />
            </label>
            <label className="block">
              Etiqueta del documento EIPD
              <input
                aria-label="Etiqueta del documento EIPD"
                className="block w-full rounded border p-2"
                value={String(doc.document_version ?? "")}
                onChange={(e) =>
                  setDoc((value) => ({ ...value, document_version: e.target.value || null }))
                }
              />
            </label>
            <EipdDocumentFields
              value={doc}
              onChange={(value) => {
                setDoc(value);
                setMessage("");
              }}
              guided
            />
            <label className="block">
              Notas del borrador EIPD (opcional)
              <textarea
                aria-label="Notas del borrador EIPD (opcional)"
                className="block w-full rounded border p-2"
                value={String(doc.notes ?? "")}
                onChange={(e) => setDoc((value) => ({ ...value, notes: e.target.value || null }))}
              />
            </label>
            <button
              type="button"
              className="rounded border px-4 py-2"
              onClick={() => setPreview(!preview)}
            >
              Ver vista previa EIPD
            </button>
            {!readOnly && row.status === "borrador" && (
              <button type="submit" className="rounded bg-blue-800 px-4 py-2 text-white">
                {busy ? "Guardando EIPD…" : "Guardar borrador EIPD"}
              </button>
            )}
          </fieldset>
          {message && !dirty && (
            <p
              role="status"
              className="rounded border border-green-600 bg-green-50 p-3 text-green-900"
            >
              {message}
            </p>
          )}
          {preview && (
            <aside
              className="space-y-2 rounded border border-blue-300 bg-blue-50 p-3"
              aria-label="Vista previa del borrador EIPD"
            >
              <EipdDocumentView value={doc} expanded valuation={dirty ? null : valuation} />
              <p>
                Guardar actualiza el borrador; no registra una resolución inmutable. En infancia,
                preparar y registrar una resolución es una acción separada.
              </p>
            </aside>
          )}
        </form>
      )}
      <section aria-label="Diagnóstico del documento EIPD" className="space-y-2 rounded border p-3">
        <h3 className="font-semibold">Diagnóstico del servidor</h3>
        {!diagnostic ? (
          <p>Diagnóstico no disponible. No se presume que el documento esté preparado.</p>
        ) : (
          <>
            {!diagnostic.rat_context_current && (
              <p>
                El contexto RAT cambió o no puede verificarse. Revisa las diferencias antes de
                continuar.
              </p>
            )}
            <p>
              {diagnostic.eipd_resolution
                ? diagnostic.eipd_resolution.result === "completo"
                  ? "Campos documentales evaluados como completos; falta revisión jurídica y no habilita EIPD."
                  : "El documento conserva faltantes o requiere revisión."
                : "No hay un diagnóstico general aplicable a este documento; revisa los requisitos específicos, incluido infancia cuando corresponda."}
            </p>
            {diagnostic.eipd_resolution && (
              <details>
                <summary>
                  Detalle de pendientes documentales ({diagnostic.eipd_resolution.issues.length})
                </summary>
                <ul>
                  {diagnostic.eipd_resolution.issues.map((issue, index) => (
                    <li key={index}>
                      {Object.entries(documentFields).find(([key]) =>
                        issue.field.split(/[.\[\]]/).includes(key)
                      )?.[1].label ?? "Documento EIPD"}
                      :{" "}
                      {issue.category === "incompleto"
                        ? "información pendiente de completar"
                        : "requiere revisión de antecedentes"}
                    </li>
                  ))}
                </ul>
              </details>
            )}
          </>
        )}
        <p>
          Activación EIPD: bloqueada. Sin aprobación jurídica automática ni puntuación de riesgo
          calculada por el sistema.
        </p>
      </section>
    </section>
  );
}
