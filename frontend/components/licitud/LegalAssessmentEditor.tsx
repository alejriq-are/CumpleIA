"use client";
import { useWorkState, type WorkReporter } from "@/components/navigation/work-unit-state";
import { useEffect, useRef, useState } from "react";
import {
  licitudApi,
  legalBases,
  legalBasisHelp,
  type Assessment,
  type SavedBasisDiagnostics,
} from "@/lib/api/licitud";
import { SavedBasisDocumentView } from "./DossierDocumentView";
import { SaveFeedback } from "./SaveFeedback";
import { sessionToken } from "./LicitudWorkspace";
import { liaFields } from "@/lib/licitud/lia-fields";
import { ConsentForm, LiaForm, consentQuestions, type LegalDocument } from "./LegalBasisForms";
export function LegalAssessmentEditor({
  organizationId,
  treatmentId,
  assessmentId,
  readOnly,
  token = sessionToken,
  onLoaded,
  onSaved,
  onDirty,
  onWorkState,
}: {
  organizationId: string;
  treatmentId: string;
  assessmentId: string;
  readOnly: boolean;
  token?: () => Promise<string>;
  onLoaded?: (row: Assessment) => void;
  onSaved?: (row: Assessment) => void;
  onDirty?: (dirty: boolean) => void;
  onWorkState?: WorkReporter;
}) {
  const [row, setRow] = useState<Assessment | null>(null),
    [basis, setBasis] = useState(""),
    [justification, setJustification] = useState(""),
    [lia, setLia] = useState<LegalDocument | null>(null),
    [consent, setConsent] = useState<LegalDocument | null>(null),
    [consultation, setDiagnostic] = useState<SavedBasisDiagnostics | null>(null),
    [diagnosticError, setDiagnosticError] = useState(""),
    [checking, setChecking] = useState(false),
    [consultedBasis, setConsultedBasis] = useState(""),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [message, setMessage] = useState("");
  const running = useRef(false);
  const queryGeneration = useRef(0);
  const [baseline, setBaseline] = useState("");
  const fingerprint = JSON.stringify([basis, justification, lia, consent]);
  const dirty = Boolean(row && baseline && fingerprint !== baseline);
  useWorkState(onWorkState, {
    loaded: !!row,
    loading: !row && !error,
    saving: busy,
    dirty,
    saved: !!message,
    error: !!error,
  });
  useEffect(() => {
    onDirty?.(dirty || busy);
  }, [dirty, busy, onDirty]);
  useEffect(() => {
    let active = true;
    queryGeneration.current += 1;
    setChecking(false);
    setDiagnosticError("");
    setRow(null);
    setError("");
    setMessage("");
    (async () => {
      try {
        const out = await licitudApi.get(
          { token: await token(), organizationId, treatmentId },
          assessmentId
        );
        if (active) {
          setRow(out);
          setBasis(out.legal_basis ?? "");
          setJustification(out.justification ?? "");
          setLia(out.lia_assessment ?? null);
          setConsent(out.consent_assessment ?? null);
          setDiagnostic(null);
          setConsultedBasis("");
          setBaseline(
            JSON.stringify([
              out.legal_basis ?? "",
              out.justification ?? "",
              out.lia_assessment ?? null,
              out.consent_assessment ?? null,
            ])
          );
          onLoaded?.(out);
        }
      } catch (e) {
        if (active) setError(e instanceof Error ? e.message : "No se pudo cargar la evaluación.");
      }
    })();
    return () => {
      active = false;
      queryGeneration.current += 1;
    };
  }, [organizationId, treatmentId, assessmentId, token, onLoaded]);
  const selectedConsent = basis === "consentimiento_art12";
  const diagnostic =
    consultation && consultedBasis === basis
      ? selectedConsent
        ? consultation.consent
        : consultation.lia
      : null;
  const savedDocument =
    consultation && consultedBasis === basis
      ? selectedConsent
        ? consultation.consent_document
        : consultation.lia_document
      : null;
  const currentDocument = selectedConsent ? consent : lia;
  const matchesConsultation = JSON.stringify(currentDocument) === JSON.stringify(savedDocument);
  const disabled = readOnly || row?.status !== "borrador" || busy;
  async function save(e: React.FormEvent) {
    e.preventDefault();
    if (!row || disabled || running.current) return;
    running.current = true;
    setBusy(true);
    setMessage("");
    setError("");
    try {
      const out = await licitudApi.save(
        { token: await token(), organizationId, treatmentId },
        assessmentId,
        {
          legal_basis: basis || null,
          justification: justification || null,
          ...(basis === "interes_legitimo_art13d" && lia ? { lia_assessment: lia } : {}),
          ...(basis === "consentimiento_art12" && consent ? { consent_assessment: consent } : {}),
        }
      );
      setRow(out);
      if (basis === "interes_legitimo_art13d") setLia(out.lia_assessment ?? null);
      if (basis === "consentimiento_art12") setConsent(out.consent_assessment ?? null);
      setBaseline(
        JSON.stringify([
          out.legal_basis ?? "",
          out.justification ?? "",
          out.lia_assessment ?? null,
          out.consent_assessment ?? null,
        ])
      );
      setDiagnostic(null);
      setConsultedBasis("");
      onSaved?.(out);
      setMessage(
        "Borrador guardado. Los cambios se guardaron correctamente en el servidor. La evaluación continúa en borrador, pendiente de revisión jurídica."
      );
    } catch (e) {
      setError(
        (e instanceof Error ? e.message : "No se pudo guardar.") +
          " Conservamos tus cambios en esta pestaña. Si la respuesta fue incierta, verifica el estado del servidor en otra pestaña antes de volver a guardar."
      );
    } finally {
      running.current = false;
      setBusy(false);
    }
  }
  return (
    <section className="space-y-4 rounded border p-4">
      <h2 className="text-xl font-semibold">Evaluación y fundamento</h2>
      {!row && error && <SaveFeedback error={error} />}
      {row ? (
        <form onSubmit={save} className="space-y-4">
          <p>
            {row.purpose_snapshot} — versión {row.version} ({row.status})
          </p>
          <p>Contenido cargado del servidor. Guardar no equivale a aprobación jurídica.</p>
          <p>
            Prueba con datos ficticios. Esta pantalla guarda borradores; no confirma ni activa EIPD.
          </p>
          <section
            aria-label="Última base y fundamento consultados en el servidor"
            className="space-y-3 rounded border border-blue-200 bg-white p-4"
          >
            <h3 className="text-lg font-semibold">
              Última base y fundamento consultados en el servidor
            </h3>
            <p>
              Evaluación versión {row.version} · {row.status}. Este resumen muestra lo cargado al
              abrir la evaluación o después de guardar en esta pestaña. No incluye ediciones
              pendientes ni se actualiza automáticamente con cambios de otras pestañas.
            </p>
            <dl className="space-y-2">
              <div>
                <dt className="font-semibold">Base de licitud propuesta guardada</dt>
                <dd>
                  {legalBases.find(([key]) => key === row.legal_basis)?.[1] ??
                    "Pendiente de definir"}
                </dd>
              </div>
              <div>
                <dt className="font-semibold">Fundamento guardado</dt>
                <dd className="whitespace-pre-wrap break-words">
                  {row.justification || "Sin fundamento registrado."}
                </dd>
              </div>
              <div>
                <dt className="font-semibold">Formularios conservados en esta evaluación</dt>
                <dd>
                  Consentimiento: {row.consent_assessment ? "Guardado" : "Sin formulario guardado"}.
                </dd>
                <dd>LIA: {row.lia_assessment ? "Guardado" : "Sin formulario guardado"}.</dd>
              </div>
            </dl>
            {dirty && (
              <p className="rounded border border-amber-300 bg-amber-50 p-3">
                Tienes cambios sin guardar. El resumen conserva lo consultado en el servidor; tus
                ediciones están en el formulario de abajo.
              </p>
            )}
            <p className="text-sm">
              Guardar una base propuesta y su fundamento no aprueba la evaluación.
            </p>
          </section>
          <label className="block">
            Base de licitud propuesta
            <select
              className="block w-full rounded border p-2"
              disabled={disabled}
              aria-label="Base de licitud propuesta"
              aria-describedby="legal-basis-help"
              value={basis}
              onChange={(e) => {
                setBasis(e.target.value);
                setMessage("");
              }}
            >
              <option value="">Pendiente de definir</option>
              {legalBases.map(([code, label]) => (
                <option key={code} value={code}>
                  {label}
                </option>
              ))}
            </select>
          </label>
          <p id="legal-basis-help" className="text-sm" aria-live="polite">
            {legalBasisHelp[basis] ?? "Revisa la base propuesta y su fundamento antes de guardar."}
          </p>
          {(basis === "interes_legitimo_art13d" || basis === "consentimiento_art12") && (
            <p className="rounded border border-blue-200 bg-blue-50 p-3 text-sm">
              {basis === "consentimiento_art12"
                ? "Seleccionar Consentimiento y guardar el formulario registra tu análisis. No acredita por sí solo un consentimiento válido ni implica que la evaluación esté aprobada."
                : "Seleccionar una base y guardar el formulario registra tu análisis. No implica que la evaluación esté aprobada."}
            </p>
          )}
          <label className="block">
            Fundamento
            <textarea
              className="block w-full rounded border p-2"
              disabled={disabled}
              aria-label="Fundamento"
              value={justification}
              onChange={(e) => {
                setJustification(e.target.value);
                setMessage("");
              }}
            />
          </label>
          <p>
            Guardar actualiza la base y su formulario activo. Los cambios de un formulario inactivo
            se conservan en esta pestaña: vuelve a seleccionarlo y guarda para persistirlos.
          </p>
          {basis === "interes_legitimo_art13d" && (
            <LiaForm
              value={lia ?? { schema_version: 1 }}
              applicability={
                diagnostic && matchesConsultation
                  ? Object.fromEntries(
                      (diagnostic?.applicability ?? []).map((a) => [a.field, a.applicability])
                    )
                  : {}
              }
              disabled={disabled}
              onChange={(v) => {
                setLia(v);
                setMessage("");
              }}
            />
          )}
          {basis === "consentimiento_art12" && (
            <ConsentForm
              value={consent ?? { schema_version: 1 }}
              disabled={disabled}
              applicability={
                diagnostic && matchesConsultation
                  ? Object.fromEntries(
                      (diagnostic?.applicability ?? []).map((a) => [a.field, a.applicability])
                    )
                  : {}
              }
              onChange={(v) => {
                setConsent(v);
                setMessage("");
              }}
            />
          )}
          {(basis === "consentimiento_art12" || basis === "interes_legitimo_art13d") && (
            <section
              className="space-y-3 rounded border bg-blue-50 p-4"
              aria-label="Diagnóstico del formulario guardado"
            >
              <h3 className="font-semibold">Diagnóstico del formulario guardado</h3>
              <p>
                Consulta lo guardado en el servidor. No analiza las ediciones pendientes ni guarda
                el formulario. Un resultado documental completo no constituye aprobación jurídica.
              </p>
              <button
                type="button"
                disabled={busy || checking}
                className="rounded border border-blue-400 bg-white p-2 disabled:opacity-50"
                onClick={async () => {
                  const generation = ++queryGeneration.current;
                  setChecking(true);
                  setDiagnosticError("");
                  try {
                    const result = await licitudApi.basisDiagnostics(
                      { token: await token(), organizationId, treatmentId },
                      assessmentId
                    );
                    if (generation !== queryGeneration.current) return;
                    setDiagnostic(result);
                    setConsultedBasis(basis);
                  } catch (e) {
                    if (generation !== queryGeneration.current) return;
                    setDiagnostic(null);
                    setDiagnosticError(
                      e instanceof Error ? e.message : "No se pudo consultar el diagnóstico."
                    );
                  } finally {
                    if (generation === queryGeneration.current) setChecking(false);
                  }
                }}
              >
                {checking ? "Consultando…" : "Consultar diagnóstico guardado"}
              </button>
              {dirty && (
                <p>
                  Hay cambios pendientes. Puedes consultar lo guardado sin perderlos; no se incluyen
                  en el diagnóstico hasta que guardes el formulario correspondiente.
                </p>
              )}
              {diagnosticError && (
                <p role="alert">
                  No se pudo consultar el diagnóstico. {diagnosticError} El resultado de guardado no
                  cambia.
                </p>
              )}
              {diagnostic && (
                <div role="status">
                  <p className="font-semibold">
                    {selectedConsent ? "Consentimiento" : "LIA"}: diagnóstico del contenido guardado
                  </p>
                  <p>Finalidad guardada en esta evaluación: {consultation?.purpose_snapshot}</p>
                  {!selectedConsent && (
                    <p>
                      El diagnóstico LIA utiliza la finalidad y los datos asociados a esta
                      evaluación. Si modificaste el inventario RAT después, esos cambios solo se
                      incluyen cuando actualizas el alcance de esta evaluación desde Alcance del
                      RAT.
                    </p>
                  )}
                  {consultation?.legal_basis !== basis && (
                    <p>
                      La base propuesta que está guardada como seleccionada es:{" "}
                      {legalBases.find(([key]) => key === consultation?.legal_basis)?.[1] ??
                        "Pendiente de definir"}
                      . Este formulario se conserva para consulta, pero consultarlo no cambia esa
                      selección ni aprueba la evaluación.
                    </p>
                  )}
                  {!matchesConsultation && (
                    <p className="rounded border border-amber-300 bg-amber-50 p-2">
                      Tu formulario difiere del contenido consultado. El diagnóstico corresponde
                      únicamente a las respuestas guardadas que se muestran abajo.
                    </p>
                  )}
                  <p>
                    Estado documental:{" "}
                    {(
                      {
                        completo: "Completo",
                        incompleto: "Incompleto",
                        requiere_revision: "Requiere revisión",
                      } as Record<string, string>
                    )[diagnostic.result] ?? diagnostic.result}
                  </p>
                  <ul className="list-disc pl-5">
                    {diagnostic.issues.map((issue, i) => (
                      <li key={i}>
                        {liaFields.find(([group, key]) => issue.field === group + "." + key)?.[2] ??
                          consentQuestions.find(([key]) => issue.field.endsWith(key))?.[1] ??
                          (
                            {
                              given_by: "Quién otorga el consentimiento",
                              grant_method: "Método de otorgamiento",
                              consent_assessment: "Expediente de consentimiento",
                            } as Record<string, string>
                          )[issue.field] ??
                          "Antecedente del formulario"}
                        :{" "}
                        {(
                          {
                            campo_obligatorio: "Falta completar este campo",
                            tipo_evidencia_vacio: "Falta identificar el tipo de evidencia",
                            respuesta_no_aplicable:
                              "Revisar la respuesta conservada: este campo no aplica",
                            respuesta_revision: "Respuesta que requiere revisión",
                            finalidad_distinta: "La finalidad difiere del alcance del RAT",
                            medida_incompleta: "Completa la medida y el impacto que mitiga",
                            decision_revision: "La conclusión requiere revisión",
                            pregunta_omitida: "Falta responder",
                            respuesta_pendiente: "Pendiente de analizar",
                            respuesta_desfavorable: "Respuesta que requiere revisión",
                            no_aplica_invalido: "No aplica requiere revisión",
                            aplicabilidad_sin_resolver: "Falta determinar la aplicabilidad",
                            expediente_ausente: "No hay expediente guardado",
                          } as Record<string, string>
                        )[issue.code] ?? "Revisar este antecedente y su fundamento"}
                      </li>
                    ))}
                  </ul>
                  <details className="rounded border bg-white p-3">
                    <summary>Respuestas guardadas analizadas</summary>
                    {savedDocument ? (
                      <SavedBasisDocumentView
                        value={{
                          purpose_snapshot: consultation?.purpose_snapshot,
                          legal_basis: basis,
                          ...(selectedConsent
                            ? { consent_assessment: savedDocument }
                            : { lia_assessment: savedDocument }),
                        }}
                      />
                    ) : (
                      <p>No hay formulario guardado para esta base.</p>
                    )}
                  </details>
                </div>
              )}
            </section>
          )}
          <SaveFeedback
            error={error}
            message={message}
            busy={busy}
            dirty={dirty}
            dirtyMessage="Cambios sin guardar. Se conservan al cambiar de pestaña; guarda antes de preparar un documento."
          />
          {row.status !== "borrador" || readOnly ? (
            <p>Consulta de solo lectura.</p>
          ) : (
            <button
              className="rounded bg-blue-700 px-4 py-2 text-white disabled:opacity-50"
              disabled={busy}
            >
              {busy ? "Guardando…" : "Guardar borrador"}
            </button>
          )}
        </form>
      ) : (
        !error && <p role="status">Cargando evaluación…</p>
      )}
    </section>
  );
}
