"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import {
  api,
  type OrganizationMembershipOut,
  type TreatmentDetailOut,
  type TreatmentSummaryOut,
} from "@/lib/api/client";
import { createClient } from "@/lib/supabase/client";
import { legalBases, licitudApi, type AssessmentSummary } from "@/lib/api/licitud";

export async function sessionToken() {
  const { data, error } = await createClient().auth.getSession();
  if (error || !data.session) throw new Error("Tu sesión expiró. Vuelve a iniciar sesión.");
  return data.session.access_token;
}
export function LicitudWorkspace({
  organizaciones,
  token = sessionToken,
}: {
  organizaciones: OrganizationMembershipOut[];
  token?: () => Promise<string>;
}) {
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
    (async () => {
      try {
        const list = await api.rat.treatments(await token(), org);
        if (active) setTreatments(list);
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
    setError("");
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
      setFiction(false);
      try {
        setRows(await licitudApi.list(scope));
      } catch {
        setError(
          "El borrador fue creado. Usa Actualizar historial para recuperar las otras evaluaciones."
        );
      }
    } catch (e) {
      setError(
        (e instanceof Error ? e.message : "No se pudo crear el borrador.") +
          " Si no recibiste respuesta, vuelve a consultar el historial antes de reintentar."
      );
    } finally {
      setBusy(false);
    }
  }
  const checkbox = (values: string[], set: (v: string[]) => void, code: string) =>
    set(values.includes(code) ? values.filter((v) => v !== code) : [...values, code]);
  return (
    <div className="space-y-6">
      <p className="rounded-lg bg-blue-50 p-4">
        Pruebas de desarrollo: utiliza únicamente datos ficticios. Guardar un borrador no acredita
        validez jurídica. La activación EIPD permanece bloqueada.
      </p>
      <label className="block">
        Organización
        <select
          className="block w-full rounded border p-2"
          aria-label="Organización"
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
      <label className="block">
        Tratamiento del RAT
        <select
          className="block w-full rounded border p-2"
          aria-label="Tratamiento del RAT"
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
      <Link prefetch={false} className="text-blue-700 underline" href="/dashboard/rat">
        Completar el inventario RAT
      </Link>
      {loading && <p role="status">Cargando…</p>}
      {error && <p role="alert">{error}</p>}
      {message && <p role="status">{message}</p>}
      {detail && (
        <>
          <section className="rounded border p-4">
            <h2 className="text-xl font-semibold">Evaluaciones guardadas</h2>
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
          {writable ? (
            <form onSubmit={create} className="space-y-4 rounded border p-4">
              <h2 className="text-xl font-semibold">Crear evaluación en borrador</h2>
              <label className="block">
                Finalidad
                <select
                  className="block w-full rounded border p-2"
                  required
                  aria-label="Finalidad"
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
              <button
                className="rounded bg-blue-700 px-4 py-2 text-white disabled:opacity-50"
                disabled={busy || !fiction || !purpose || !categories.length || !subjects.length}
              >
                {busy ? "Guardando…" : "Crear borrador"}
              </button>
            </form>
          ) : (
            <p>Tu rol permite consultar evaluaciones; no permite crear borradores.</p>
          )}
        </>
      )}
    </div>
  );
}
