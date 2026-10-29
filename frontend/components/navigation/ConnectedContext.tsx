"use client";
import { useEffect, useId, useRef, useState } from "react";
import { api, type OrganizationMembershipOut, type TreatmentSummaryOut } from "@/lib/api/client";
import { licitudApi, type AssessmentSummary } from "@/lib/api/licitud";
import { sessionToken } from "@/components/licitud/LicitudWorkspace";
export type WorkContext = { organizationId: string; treatmentId: string; assessmentId: string };
export function ConnectedContext({
  organizations,
  current,
  pendingCount = 0,
  currentDescription,
  describeDestination,
  apply,
  cancel,
  token = sessionToken,
  applying = false,
  applyError = "",
}: {
  organizations: OrganizationMembershipOut[];
  current: WorkContext;
  pendingCount?: number;
  currentDescription?: string;
  describeDestination?: (context: WorkContext) => string;
  apply: (v: WorkContext) => void;
  cancel: () => void;
  token?: () => Promise<string>;
  applying?: boolean;
  applyError?: string;
}) {
  const id = useId();
  const dependencyHelpId = `${id}-dependencies`;
  const applyHelpId = `${id}-apply-help`;
  const [org, setOrg] = useState(current.organizationId);
  const [tid, setTid] = useState(current.treatmentId);
  const [aid, setAid] = useState(current.assessmentId);
  const [series, setSeries] = useState("");
  const selectedAid = useRef(aid);
  selectedAid.current = aid;
  const [treatments, setTreatments] = useState<TreatmentSummaryOut[]>([]);
  const [rows, setRows] = useState<AssessmentSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    setTreatments([]);
    (async () => {
      try {
        const v = await api.rat.treatments(await token(), org);
        if (active) {
          setTreatments(v);
        }
      } catch (e) {
        if (active) setError(e instanceof Error ? e.message : "No se pudo cargar el inventario.");
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => {
      active = false;
    };
  }, [org, token]); // treatment selection is validated against this response
  useEffect(() => {
    let active = true;
    setRows([]);
    if (!tid) return;
    setLoading(true);
    setError("");
    (async () => {
      try {
        const auth = await token();
        const list: AssessmentSummary[] = [];
        let offset = 0;
        while (active) {
          const page = await licitudApi.list(
            { token: auth, organizationId: org, treatmentId: tid },
            offset
          );
          list.push(...page);
          if (page.length < 50) break;
          offset += 50;
        }
        if (active) {
          setRows(list);
          const selected = list.find((r) => r.id === selectedAid.current);
          setSeries(selected?.series_id ?? selected?.id ?? "");
          if (!selected) setAid("");
        }
      } catch (e) {
        if (active)
          setError(e instanceof Error ? e.message : "No se pudieron cargar las evaluaciones.");
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => {
      active = false;
    };
  }, [org, tid, token]);
  const purposes = Array.from(
    new Map(rows.map((v) => [v.series_id ?? v.id, v.purpose_snapshot])).entries()
  );
  const applyBlocked = applying
    ? "Espera a que termine la validación del contexto."
    : loading
      ? "Espera a que termine la consulta de los contextos autorizados."
      : error
        ? "No se puede aplicar el contexto mientras no se complete la consulta. Revisa el error indicado."
        : !organizations.some((value) => value.id === org)
          ? "Selecciona una organización a la que tengas acceso."
          : tid && !treatments.some((value) => value.id === tid)
            ? "Selecciona un tratamiento disponible para esta organización."
            : series && !rows.some((value) => value.id === aid)
              ? "Selecciona una evaluación para la finalidad elegida."
              : "";
  const applyHelp =
    applyBlocked ||
    (!tid
      ? "Puedes aplicar solo la organización. El tratamiento y la evaluación son opcionales."
      : !series
        ? "Puedes aplicar organización y tratamiento. Para trabajar con una evaluación, elige también su finalidad y versión."
        : "El contexto está listo para aplicar.");
  return (
    <div className="space-y-4">
      <h3 className="font-semibold">Elegir trabajo existente</h3>
      <p>
        Aplicar contexto cambia tu selección de trabajo; no crea una evaluación. Para crear una
        nueva, usa Preparar → Evaluaciones y creación de borrador.
      </p>
      <p>
        Selecciona el contexto guardado en el servidor. Los borradores abiertos se conservan durante
        esta visita; no se copian a otra evaluación.
      </p>
      <p id={dependencyHelpId} className="text-sm text-slate-600">
        Selecciona primero un tratamiento para habilitar Finalidad y después una finalidad para
        habilitar Evaluación.
      </p>
      <label className="block">
        Organización
        <select
          aria-label="Organización"
          className="mt-2 block w-full rounded border p-3"
          value={org}
          onChange={(e) => {
            setOrg(e.target.value);
            setTid("");
            setAid("");
            setSeries("");
          }}
        >
          {organizations.map((v) => (
            <option value={v.id} key={v.id}>
              {v.name}
            </option>
          ))}
        </select>
      </label>
      <label className="block">
        Tratamiento del RAT
        <select
          aria-label="Tratamiento del RAT"
          aria-describedby={dependencyHelpId}
          className="mt-2 block w-full rounded border p-3"
          value={tid}
          onChange={(e) => {
            setTid(e.target.value);
            setAid("");
            setSeries("");
          }}
          disabled={loading}
        >
          <option value="">Sin tratamiento seleccionado</option>
          {treatments.map((v) => (
            <option key={v.id} value={v.id}>
              {v.name}
            </option>
          ))}
        </select>
      </label>
      <label className="block">
        Finalidad de la evaluación
        <select
          aria-label="Finalidad de la evaluación"
          aria-describedby={dependencyHelpId}
          className="mt-2 block w-full rounded border p-3"
          disabled={loading || !tid}
          value={series}
          onChange={(e) => {
            setSeries(e.target.value);
            setAid("");
          }}
        >
          <option value="">Selecciona una finalidad guardada</option>
          {purposes.map(([key, label]) => (
            <option key={key} value={key}>
              {label}
            </option>
          ))}
        </select>
      </label>
      <label className="block">
        Evaluación
        <select
          aria-label="Evaluación"
          aria-describedby={dependencyHelpId}
          className="mt-2 block w-full rounded border p-3"
          disabled={loading || !series}
          value={aid}
          onChange={(e) => setAid(e.target.value)}
        >
          <option value="">Selecciona una evaluación</option>
          {rows
            .filter((v) => (v.series_id ?? v.id) === series)
            .map((v) => (
              <option key={v.id} value={v.id}>
                Versión {v.version} · {v.status}
              </option>
            ))}
        </select>
      </label>
      {(loading || applying) && <p role="status">Consultando contextos autorizados…</p>}
      {(error || applyError) && <p role="alert">{error || applyError}</p>}
      {tid && !loading && rows.length === 0 && (
        <p>
          No hay evaluaciones guardadas para este tratamiento. Puedes crearlas desde Bases de
          licitud.
        </p>
      )}
      <p id={applyHelpId} aria-live="polite" className="text-sm text-slate-700">
        {applyHelp}
      </p>
      {pendingCount > 0 && describeDestination && (
        <section
          aria-label="Antes de aplicar contexto"
          className="space-y-2 break-words rounded border border-blue-200 bg-blue-50 p-3"
        >
          <h3 className="font-bold">Antes de aplicar contexto</h3>
          <p>Ahora: {currentDescription}</p>
          <p>
            Selección propuesta:{" "}
            {organizations.find((v) => v.id === org)?.name ?? "Organización sin seleccionar"} ·{" "}
            {treatments.find((v) => v.id === tid)?.name ?? "Sin tratamiento seleccionado"} ·{" "}
            {rows.find((v) => v.id === aid)
              ? `${rows.find((v) => v.id === aid)!.purpose_snapshot} · versión ${rows.find((v) => v.id === aid)!.version} · ${rows.find((v) => v.id === aid)!.status}`
              : "Sin evaluación seleccionada"}
          </p>
          <p>
            Destino al aplicar:{" "}
            <strong>
              {describeDestination({ organizationId: org, treatmentId: tid, assessmentId: aid })}
            </strong>
          </p>
          <p>
            Los {pendingCount} pendientes se conservan en sus formularios durante esta visita.
            Aplicar no los guarda ni copia sus datos a la nueva selección. Otras pestañas no
            cambian. Cancelar mantiene la selección y la pantalla actuales.
          </p>
        </section>
      )}
      <div className="flex gap-3">
        <button
          aria-describedby={applyHelpId}
          className="rounded bg-blue-800 p-3 text-white disabled:opacity-50"
          disabled={!!applyBlocked}
          onClick={() => apply({ organizationId: org, treatmentId: tid, assessmentId: aid })}
        >
          Aplicar contexto
        </button>
        <button className="rounded border p-3" onClick={cancel}>
          Cancelar
        </button>
      </div>
    </div>
  );
}
