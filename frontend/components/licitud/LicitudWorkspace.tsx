"use client";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import {
  api,
  ApiError,
  type OrganizationMembershipOut,
  type TreatmentDetailOut,
  type TreatmentSummaryOut,
} from "@/lib/api/client";
import { SaveFeedback } from "./SaveFeedback";
import { sessionToken } from "@/lib/auth/session";
export { sessionToken } from "@/lib/auth/session";
import { legalBases, legalBasisHelp, licitudApi, type AssessmentSummary } from "@/lib/api/licitud";

export function LicitudWorkspace({
  organizaciones,
  token = sessionToken,
  onPending,
  onCreationPending,
  initialTreatmentId,
  workingDescription,
}: {
  organizaciones: OrganizationMembershipOut[];
  initialTreatmentId?: string;
  workingDescription?: string;
  token?: () => Promise<string>;
  onPending?: (dirty: boolean) => void;
  onCreationPending?: (value: { pending: boolean; treatmentId: string }) => void;
}) {
  const initialTreatment = useRef(initialTreatmentId);
  const [creationOpen, setCreationOpen] = useState(true);
  const [org, setOrg] = useState(organizaciones[0]?.id ?? "");
  const [treatments, setTreatments] = useState<TreatmentSummaryOut[]>([]);
  const [tid, setTid] = useState("");
  const [detail, setDetail] = useState<TreatmentDetailOut | null>(null);
  const [rows, setRows] = useState<AssessmentSummary[]>([]);
  const [offset, setOffset] = useState(0);
  const [purpose, setPurpose] = useState("");
  const [categories, setCategories] = useState<string[]>([]);
  const [subjects, setSubjects] = useState<string[]>([]);
  const [basis, setBasis] = useState("");
  const [justification, setJustification] = useState("");
  const [fiction, setFiction] = useState(false);
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [createError, setCreateError] = useState("");
  const [existing, setExisting] = useState<AssessmentSummary[]>([]);
  const [creating, setCreating] = useState(false);
  const draftFingerprint = JSON.stringify([purpose, categories, subjects, basis, justification]);
  const [submitted, setSubmitted] = useState("");
  const draftPending =
    !!(purpose || categories.length || subjects.length || basis || justification) &&
    draftFingerprint !== submitted;
  useEffect(() => onPending?.(draftPending), [draftPending, onPending]);
  useEffect(
    () => onCreationPending?.({ pending: draftPending, treatmentId: tid }),
    [draftPending, tid, onCreationPending]
  );
  const writable = ["owner", "admin", "editor"].includes(
    organizaciones.find((o) => o.id === org)?.role ?? ""
  );
  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    setTid("");
    setTreatments([]);
    setDetail(null);
    setRows([]);
    setMessage("");
    setCreateError("");
    setExisting([]);
    (async () => {
      try {
        const list = await api.rat.treatments(await token(), org);
        if (active) {
          setTreatments(list);
          if (initialTreatment.current && list.some((item) => item.id === initialTreatment.current))
            setTid(initialTreatment.current);
          initialTreatment.current = undefined;
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
  }, [org, token]);
  useEffect(() => {
    let active = true;
    setDetail(null);
    setRows([]);
    setPurpose("");
    setCategories([]);
    setSubjects([]);
    setBasis("");
    setJustification("");
    setFiction(false);
    setMessage("");
    setError("");
    setOffset(0);
    setCreateError("");
    setExisting([]);
    if (!tid) return;
    setLoading(true);
    (async () => {
      try {
        const t = await token();
        const [d, list] = await Promise.all([
          api.rat.getTreatment(t, org, tid),
          licitudApi.list({ token: t, organizationId: org, treatmentId: tid }),
        ]);
        if (active) {
          if (d.id !== tid)
            throw new Error(
              "El tratamiento consultado no corresponde a la selección. Vuelve a elegirlo."
            );
          setDetail(d);
          setRows(list);
        }
      } catch (e) {
        if (active) setError(e instanceof Error ? e.message : "No se pudo cargar el tratamiento.");
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => {
      active = false;
    };
  }, [org, tid, token]);
  async function page(next: number) {
    setBusy(true);
    setError("");
    try {
      const list = await licitudApi.list(
        { token: await token(), organizationId: org, treatmentId: tid },
        next
      );
      setRows(list);
      setOffset(next);
    } catch (e) {
      setError(e instanceof Error ? e.message : "No se pudo cargar el historial.");
    } finally {
      setBusy(false);
    }
  }
  async function create(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setCreating(true);
    setError("");
    setCreateError("");
    setExisting([]);
    setMessage("");
    try {
      const scope = { token: await token(), organizationId: org, treatmentId: tid };
      const row = await licitudApi.create(scope, {
        purpose_id: purpose,
        scope: { data_category_codes: categories, data_subject_codes: subjects },
        legal_basis: basis || null,
        justification: justification || null,
      });
      setRows([row]);
      setOffset(0);
      setMessage("Borrador creado. Abre la evaluación para continuar.");
      setSubmitted(draftFingerprint);
      setFiction(false);
      try {
        setRows(await licitudApi.list(scope));
      } catch {
        setError(
          "El borrador fue creado. Usa Actualizar historial para recuperar las otras evaluaciones."
        );
      }
    } catch (e) {
      const conflict =
        e instanceof ApiError && e.status === 409 && /Ya existe un borrador/.test(e.message);
      if (conflict) {
        setCreateError(
          "Ya existe un borrador para esta finalidad. No se creó otra evaluación ni se guardaron los cambios de este formulario. Abre el borrador existente desde las evaluaciones disponibles."
        );
        try {
          const list = await licitudApi.list({
            token: await token(),
            organizationId: org,
            treatmentId: tid,
          });
          setRows(list);
          setOffset(0);
          setExisting(list.filter((item) => item.status === "borrador"));
        } catch {
          setCreateError(
            "Ya existe un borrador para esta finalidad. No se creó otra evaluación. Usa Actualizar historial para localizar el borrador existente; tus campos se conservan."
          );
        }
      } else {
        const unknown = !(e instanceof ApiError) || e.status >= 500 || e.status === 408;
        setCreateError(
          unknown
            ? "Resultado incierto. Conservamos el formulario; consulta el historial antes de volver a crear para evitar duplicados."
            : `${e.message} No se creó el borrador. Conservamos los campos para corregirlos.`
        );
      }
    } finally {
      setBusy(false);
      setCreating(false);
    }
  }

  const checkbox = (values: string[], set: (v: string[]) => void, code: string) =>
    set(values.includes(code) ? values.filter((v) => v !== code) : [...values, code]);
  return (
    <div className="licitud-ui space-y-6">
      <p className="rounded-lg bg-blue-50 p-4">
        Pruebas de desarrollo: utiliza únicamente datos ficticios. Guardar un borrador no acredita
        validez jurídica. La activación EIPD permanece bloqueada.
      </p>
      {workingDescription && (
        <section
          aria-label="Trabajo seleccionado"
          className="rounded border border-blue-200 bg-blue-50 p-3"
        >
          <h2 className="font-semibold">Trabajando en…</h2>
          <p>{workingDescription}</p>
          <p className="text-sm">
            Consultar esta lista o preparar otra evaluación no cambia tu selección de trabajo. Abrir
            una evaluación guardada sí cambia el contexto.
          </p>
        </section>
      )}
      <label className="block">
        Organización
        <select
          className="block w-full rounded border p-2"
          aria-label="Organización"
          aria-describedby="workspace-org-help"
          value={org}
          disabled={busy}
          onChange={(e) => setOrg(e.target.value)}
        >
          {organizaciones.map((o) => (
            <option key={o.id} value={o.id}>
              {o.name}
            </option>
          ))}
        </select>
      </label>
      <p id="workspace-org-help" className="text-sm" aria-live="polite">
        Selecciona la organización a cuyo inventario pertenece la evaluación. Solo aparecen las
        organizaciones de tu cuenta; sus datos y permisos se mantienen separados.
      </p>
      <label className="block">
        Tratamiento del RAT
        <select
          className="block w-full rounded border p-2"
          aria-label="Tratamiento del RAT"
          aria-describedby="workspace-rat-help"
          value={tid}
          disabled={busy || loading}
          onChange={(e) => setTid(e.target.value)}
        >
          <option value="">Selecciona un tratamiento</option>
          {treatments.map((t) => (
            <option key={t.id} value={t.id}>
              {t.name}
            </option>
          ))}
        </select>
      </label>
      <p id="workspace-rat-help" className="text-sm" aria-live="polite">
        {tid
          ? "Selecciona dentro de este tratamiento la finalidad y los datos concretos que evaluarás. Puedes consultar sus evaluaciones anteriores antes de crear otra."
          : "Elige primero una actividad del inventario RAT. Si no está disponible, completa el inventario antes de evaluar su base de licitud."}
      </p>
      <Link prefetch={false} className="text-blue-700 underline" href="/dashboard/rat">
        Completar el inventario RAT
      </Link>
      {loading && <p role="status">Cargando…</p>}
      {error && <p role="alert">{error}</p>}

      {detail && (
        <>
          <section className="rounded border p-4">
            <h2 className="text-xl font-semibold">Evaluaciones guardadas</h2>
            <p>
              Abre una evaluación existente para trabajar en ella. Esta acción no crea otra
              evaluación.
            </p>
            {!rows.length && <p>No hay evaluaciones en esta página.</p>}
            <ul>
              {rows.map((row) => (
                <li key={row.id} className="py-2">
                  <Link
                    prefetch={false}
                    className="text-blue-700 underline"
                    href={`/dashboard/licitud/${tid}/${row.id}?organizationId=${encodeURIComponent(org)}`}
                  >
                    {row.purpose_snapshot} — versión {row.version} ({row.status})
                  </Link>
                </li>
              ))}
            </ul>
            <button disabled={busy || offset === 0} onClick={() => page(Math.max(0, offset - 50))}>
              Página anterior
            </button>{" "}
            <button disabled={busy || rows.length < 50} onClick={() => page(offset + 50)}>
              Página siguiente
            </button>{" "}
            <button disabled={busy} onClick={() => page(0)}>
              Actualizar historial
            </button>
          </section>
          {writable && !creationOpen && (
            <div className="space-y-2 rounded border p-4">
              <p>
                Creación cancelada. No se creó otra evaluación ni cambió tu contexto. Los campos de
                esta preparación se conservan durante esta visita en esta pestaña.
              </p>
              <button
                type="button"
                className="rounded border border-blue-300 bg-blue-50 px-3 py-2 font-semibold text-blue-900"
                onClick={() => setCreationOpen(true)}
              >
                Volver a preparar evaluación
              </button>
            </div>
          )}
          {writable ? (
            <form
              hidden={!creationOpen}
              onSubmit={create}
              onChange={() => {
                setMessage("");
                setCreateError("");
                setExisting([]);
              }}
              className="space-y-4 rounded border p-4"
            >
              <h2 className="text-xl font-semibold">Crear evaluación en borrador</h2>
              <p className="font-semibold">Crear evaluación para: {detail.name}</p>
              <p className="text-sm">
                Esto prepara un registro nuevo; todavía no se ha creado. El tratamiento se propone
                solo si está disponible en tu inventario autorizado. Elige finalidad y alcance del
                RAT actual: no se copian los de la evaluación seleccionada, que puede conservar un
                alcance anterior.
              </p>
              <label className="block">
                Finalidad
                <select
                  className="block w-full rounded border p-2"
                  required
                  aria-label="Finalidad"
                  aria-describedby="workspace-purpose-help"
                  value={purpose}
                  disabled={busy}
                  onChange={(e) => setPurpose(e.target.value)}
                >
                  <option value="">Selecciona una finalidad</option>
                  {detail.purposes.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.purpose}
                    </option>
                  ))}
                </select>
              </label>
              <p id="workspace-purpose-help" className="text-sm" aria-live="polite">
                {purpose
                  ? "Evalúas esta finalidad concreta. Incluye solo las categorías y titulares que participan en ella; otra finalidad puede necesitar una evaluación diferente."
                  : "Selecciona para qué se utilizan los datos dentro del tratamiento. Una evaluación corresponde a una finalidad."}
              </p>
              <fieldset disabled={busy}>
                <legend>Categorías de datos incluidas</legend>
                {detail.data_categories.map((c) => (
                  <label key={c.category_code} className="block">
                    <input
                      type="checkbox"
                      checked={categories.includes(c.category_code)}
                      onChange={() => checkbox(categories, setCategories, c.category_code)}
                    />
                    {c.category_name}
                  </label>
                ))}
              </fieldset>
              <fieldset disabled={busy}>
                <legend>Titulares incluidos</legend>
                {detail.data_subjects.map((c) => (
                  <label key={c.category_code} className="block">
                    <input
                      type="checkbox"
                      checked={subjects.includes(c.category_code)}
                      onChange={() => checkbox(subjects, setSubjects, c.category_code)}
                    />
                    {c.category_name}
                  </label>
                ))}
              </fieldset>
              <label className="block">
                Base de licitud propuesta
                <select
                  className="block w-full rounded border p-2"
                  aria-label="Base de licitud propuesta"
                  aria-describedby="workspace-basis-help"
                  value={basis}
                  disabled={busy}
                  onChange={(e) => setBasis(e.target.value)}
                >
                  <option value="">Pendiente de definir</option>
                  {legalBases.map(([code, label]) => (
                    <option key={code} value={code}>
                      {label}
                    </option>
                  ))}
                </select>
              </label>
              <p id="workspace-basis-help" className="text-sm" aria-live="polite">
                {legalBasisHelp[basis] ?? "Revisa la base y el fundamento propuestos."}
              </p>
              <label className="block">
                Fundamento
                <textarea
                  className="block w-full rounded border p-2"
                  aria-label="Fundamento"
                  value={justification}
                  disabled={busy}
                  onChange={(e) => setJustification(e.target.value)}
                />
              </label>
              <label className="block">
                <input
                  type="checkbox"
                  checked={fiction}
                  disabled={busy}
                  onChange={(e) => setFiction(e.target.checked)}
                />
                Confirmo que ingreso únicamente datos ficticios de prueba
              </label>
              {(!detail.purposes.length ||
                !detail.data_categories.length ||
                !detail.data_subjects.length) && (
                <p>
                  Completa finalidades, categorías y titulares en el RAT antes de crear la
                  evaluación.
                </p>
              )}
              <SaveFeedback error={createError} message={message} busy={creating} />
              {existing.length > 0 && (
                <div aria-label="Borradores existentes" className="space-y-2">
                  <p>Abre el borrador que corresponde a la finalidad que quieres evaluar:</p>
                  {existing.map((item) => (
                    <Link
                      key={item.id}
                      prefetch={false}
                      className="block font-semibold text-blue-800 underline"
                      href={`/dashboard/licitud/${tid}/${item.id}?organizationId=${encodeURIComponent(org)}`}
                    >
                      Abrir borrador existente: {item.purpose_snapshot} — versión {item.version}
                    </Link>
                  ))}
                </div>
              )}
              <button
                className="rounded bg-blue-700 px-4 py-2 text-white disabled:opacity-50"
                disabled={busy || !fiction || !purpose || !categories.length || !subjects.length}
              >
                {busy ? "Creando evaluación…" : "Crear borrador"}
              </button>
              <button
                type="button"
                disabled={busy}
                className="ml-2 rounded border border-blue-300 bg-blue-50 px-3 py-2 font-semibold text-blue-900 disabled:opacity-50"
                onClick={() => setCreationOpen(false)}
              >
                Cancelar creación
              </button>
              <p className="text-sm">
                Crear borrador guarda una evaluación nueva en el servidor. Después usa su enlace en
                Evaluaciones guardadas para abrirla. Cancelar no guarda ni descarta los campos de
                esta preparación.
              </p>
            </form>
          ) : (
            <p>Tu rol permite consultar evaluaciones; no permite crear borradores.</p>
          )}
        </>
      )}
    </div>
  );
}
