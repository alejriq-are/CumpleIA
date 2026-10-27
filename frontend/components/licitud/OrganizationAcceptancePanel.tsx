"use client";
import { documentLabels } from "@/lib/licitud/document-labels";
import { useState, useEffect, useId, useRef } from "react";
import { ApiError } from "@/lib/api/client";
import type {
  Acceptance,
  Authority,
  AuthorityState,
  Designation,
} from "@/lib/api/organization-acceptance";
type Snapshot = { state: AuthorityState; events: Acceptance[] };
type Props = {
  readOnly: boolean;
  guided?: boolean;
  load: () => Promise<Snapshot>;
  designate: (actor: string, p: Designation) => Promise<Authority>;
  record: (
    actor: string,
    p: {
      authority_id: string;
      decision: Acceptance["decision"];
      rationale: string;
      evidence_reference: string;
    }
  ) => Promise<Acceptance>;
};
const labels = {
  acepta: "Acepta el documento",
  rechaza: "Rechaza el documento",
  requiere_cambios: "Requiere cambios",
};
export function OrganizationAcceptancePanel({
  readOnly,
  load,
  designate,
  record,
  guided = false,
}: Props) {
  const choiceHelpId = useId();
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null),
    [target, setTarget] = useState("");
  const [action, setAction] = useState<Designation["action"]>("otorgar"),
    [role, setRole] = useState<Designation["organization_role"]>("responsable");
  const [party, setParty] = useState(""),
    [faculty, setFaculty] = useState(""),
    [evidence, setEvidence] = useState("");
  const [choice, setChoice] = useState<Acceptance["decision"] | "">(guided ? "" : "acepta"),
    [rationale, setRationale] = useState(""),
    [acta, setActa] = useState("");
  const [fictitious, setFictitious] = useState(false),
    [busy, setBusy] = useState(false),
    [uncertain, setUncertain] = useState(false),
    [error, setError] = useState(""),
    [message, setMessage] = useState("");
  const [facultyOpen, setFacultyOpen] = useState(false);
  const running = useRef(false),
    epoch = useRef(0),
    alive = useRef(false);
  useEffect(() => {
    alive.current = true;
    const seq = ++epoch.current;
    setBusy(true);
    load()
      .then((v) => {
        if (alive.current && seq === epoch.current) {
          setSnapshot(v);
          setTarget((t) => t || v.state.actor_id);
        }
      })
      .catch(() => {
        if (alive.current && seq === epoch.current) setError("No se pudo consultar la aceptación.");
      })
      .finally(() => {
        if (alive.current && seq === epoch.current) setBusy(false);
      });
    return () => {
      alive.current = false;
    };
  }, [load]);
  const latest = (actor: string) =>
    snapshot?.state.authorities
      .filter((v) => v.actor_id === actor)
      .sort((a, b) => b.revision - a.revision)[0];
  const own = snapshot ? latest(snapshot.state.actor_id) : undefined;
  async function refresh() {
    if (running.current || busy) return;
    running.current = true;
    setBusy(true);
    setError("");
    try {
      const v = await load();
      if (alive.current) setSnapshot(v);
    } catch {
      if (alive.current) {
        setSnapshot(null);
        setError("Consulta no disponible; registro bloqueado.");
      }
    } finally {
      running.current = false;
      if (alive.current) setBusy(false);
    }
  }
  async function write(kind: "faculty" | "decision") {
    if (running.current || busy || uncertain || readOnly || !fictitious || !snapshot) return;
    if (kind === "faculty" && !snapshot.state.may_designate) return;
    if (kind === "decision" && own?.action !== "otorgar") return;
    running.current = true;
    setBusy(true);
    setError("");
    setMessage("");
    try {
      if (kind === "faculty") {
        const saved = await designate(snapshot.state.actor_id, {
          actor_id: target.trim(),
          expected_revision: latest(target.trim())?.revision ?? 0,
          action,
          organization_role: role,
          responsible_party_reference: party.trim() || null,
          faculty_reference: faculty.trim(),
          evidence_reference: evidence.trim(),
        });
        if (alive.current) {
          setSnapshot(
            (s) =>
              s && {
                state: { ...s.state, authorities: [...s.state.authorities, saved] },
                events: s.events.map((v) =>
                  v.actor_id === saved.actor_id ? { ...v, faculty_current: false } : v
                ),
              }
          );
          setMessage(
            "Facultad de prueba registrada. No es una verificación de representación real."
          );
          setFaculty("");
          setEvidence("");
        }
      } else if (own && choice) {
        const saved = await record(snapshot.state.actor_id, {
          authority_id: own.id,
          decision: choice,
          rationale: rationale.trim(),
          evidence_reference: acta.trim(),
        });
        if (alive.current) {
          setSnapshot((s) => s && { ...s, events: [...s.events, saved] });
          setRationale("");
          setActa("");
          setMessage("Decisión documental de prueba registrada. No confirma ni activa EIPD.");
        }
      }
    } catch (cause) {
      if (alive.current) {
        const unknown = !(cause instanceof ApiError) || cause.status >= 500 || cause.status === 408;
        setUncertain(unknown);
        setError(
          unknown
            ? "Resultado incierto: no repitas el registro; consulta el historial antes de recargar."
            : cause instanceof ApiError && cause.status === 409
              ? "Material o revisión de facultad cambió. Actualiza la consulta; conservamos el formulario."
              : "Registro rechazado. Revisa permisos, facultad y referencias; conservamos el formulario."
        );
      }
    } finally {
      running.current = false;
      if (alive.current) setBusy(false);
    }
  }
  const disabled = readOnly || busy || uncertain || !fictitious;
  return (
    <section
      aria-label="Aceptación documental por organización"
      className="space-y-4 rounded border p-4"
    >
      <h3>Aceptación documental por organización</h3>
      <p>
        Solo pruebas con datos ficticios. La organización decide mediante una persona facultada.
        Esta decisión no publica política global, no confirma ni activa EIPD.
      </p>
      {error && <p role="alert">{error}</p>}
      {message && <p role="status">{message}</p>}
      {uncertain && (
        <p>Registro bloqueado tras resultado incierto; la consulta sigue disponible.</p>
      )}
      <button type="button" disabled={busy} onClick={() => void refresh()}>
        Actualizar aceptación de organización
      </button>
      {snapshot && (
        <>
          <p className="break-all">Persona de esta sesión de prueba: {snapshot.state.actor_id}</p>
          <label>
            <input
              type="checkbox"
              checked={fictitious}
              disabled={readOnly || busy || uncertain}
              onChange={(e) => setFictitious(e.target.checked)}
            />{" "}
            Declaro datos ficticios para la aceptación
          </label>
          {guided && (
            <button
              type="button"
              className="rounded border px-3 py-2"
              aria-expanded={facultyOpen}
              onClick={() => setFacultyOpen(!facultyOpen)}
            >
              Gestionar facultades de la organización
            </button>
          )}
          <div hidden={guided && !facultyOpen}>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                void write("faculty");
              }}
            >
              <fieldset disabled={disabled || !snapshot.state.may_designate} className="space-y-3">
                <legend>Designación explícita de facultad</legend>
                <p>
                  Administración de la organización: registra la referencia que respalda la
                  designación. El rol owner/admin no equivale a una facultad para aceptar.
                </p>
                <label className="block">
                  Persona facultada (identificador de prueba)
                  <input
                    aria-label="Persona facultada (identificador de prueba)"
                    required
                    className="block w-full rounded border p-2"
                    value={target}
                    onChange={(e) => setTarget(e.target.value)}
                  />
                </label>
                <label className="block">
                  Acción sobre la facultad
                  <select
                    aria-label="Acción sobre la facultad"
                    value={action}
                    onChange={(e) => setAction(e.target.value as Designation["action"])}
                  >
                    <option value="otorgar">Otorgar</option>
                    <option value="revocar">Revocar</option>
                  </select>
                </label>
                <label className="block">
                  Rol de la organización
                  <select
                    aria-label="Rol de la organización"
                    value={role}
                    onChange={(e) => setRole(e.target.value as Designation["organization_role"])}
                  >
                    <option value="responsable">Responsable</option>
                    <option value="encargado">Encargado</option>
                  </select>
                </label>
                <label className="block">
                  Responsable por cuya cuenta actúa
                  <input
                    aria-label="Responsable por cuya cuenta actúa"
                    required={role === "encargado"}
                    className="block w-full rounded border p-2"
                    value={party}
                    onChange={(e) => setParty(e.target.value)}
                  />
                </label>
                <label className="block">
                  Referencia de la facultad
                  <input
                    aria-label="Referencia de la facultad"
                    required
                    className="block w-full rounded border p-2"
                    value={faculty}
                    onChange={(e) => setFaculty(e.target.value)}
                  />
                </label>
                <label className="block">
                  Evidencia de la facultad
                  <input
                    aria-label="Evidencia de la facultad"
                    required
                    className="block w-full rounded border p-2"
                    value={evidence}
                    onChange={(e) => setEvidence(e.target.value)}
                  />
                </label>
                <button type="submit">Registrar facultad ficticia</button>
              </fieldset>
            </form>
          </div>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              void write("decision");
            }}
          >
            <fieldset disabled={disabled || own?.action !== "otorgar"} className="space-y-3">
              <legend>Decisión sobre el documento consultado</legend>
              <label className="block">
                {documentLabels.organizationDecision}
                <select
                  aria-label={documentLabels.organizationDecision}
                  value={choice}
                  required
                  aria-describedby={choiceHelpId}
                  onChange={(e) => setChoice(e.target.value as Acceptance["decision"])}
                >
                  {guided && <option value="">Selecciona una decisión</option>}
                  {Object.entries(labels).map(([v, label]) => (
                    <option key={v} value={v}>
                      {label}
                    </option>
                  ))}
                </select>
              </label>
              <p id={choiceHelpId} aria-live="polite" className="text-sm">
                {!choice
                  ? "Selecciona la posición que quieres registrar sobre este documento. Explica sus motivos y aporta la referencia del acta ficticia."
                  : choice === "requiere_cambios"
                    ? "Requiere cambios: la organización solicita ajustes antes de volver a considerar esta versión."
                    : choice === "rechaza"
                      ? "Rechaza el documento: deja constancia del desacuerdo de la organización con esta versión. No borra el historial."
                      : "Acepta el documento: registra exclusivamente una aceptación documental ficticia sobre esta resolución. No constituye aceptación jurídica real ni habilita EIPD."}
              </p>
              <label className="block">
                Fundamento de la decisión
                <textarea
                  aria-label="Fundamento de la decisión"
                  required
                  className="block w-full rounded border p-2"
                  value={rationale}
                  onChange={(e) => setRationale(e.target.value)}
                />
              </label>
              <label className="block">
                Referencia del acta ficticia
                <input
                  aria-label="Referencia del acta ficticia"
                  required
                  className="block w-full rounded border p-2"
                  value={acta}
                  onChange={(e) => setActa(e.target.value)}
                />
              </label>
              <button type="submit">Registrar decisión documental ficticia</button>
            </fieldset>
          </form>
          <h4>Historial documental de esta versión</h4>
          <p>La coincidencia de material es orientativa y no es autorización jurídica.</p>
          {snapshot.events.length === 0 && <p>No hay decisiones de organización registradas.</p>}
          <ul>
            {snapshot.events.map((v) => (
              <li key={v.id} className="space-y-1 rounded border p-3">
                <p>Decisión de la organización: {labels[v.decision]}</p>
                <p>{v.rationale}</p>
                <p>{v.evidence_reference}</p>
                <p>
                  Material:{" "}
                  {v.material_status === "coincide"
                    ? "coincide"
                    : v.material_status === "obsoleto"
                      ? "obsoleto"
                      : "no disponible"}
                  . Facultad actual: {v.faculty_current ? "registrada" : "no disponible"}.
                </p>
                <p className="break-all">
                  Actor: {v.actor_id}. Fecha (UTC): {v.created_at}.
                </p>
              </li>
            ))}
          </ul>
          <details>
            <summary>Historial de facultades del expediente</summary>
            <ul>
              {snapshot.state.authorities.map((v) => (
                <li key={v.id} className="break-all">
                  Revisión {v.revision}: {v.action}, {v.organization_role}, persona {v.actor_id}.{" "}
                  {v.faculty_reference}. {v.evidence_reference}.
                </li>
              ))}
            </ul>
          </details>
        </>
      )}
    </section>
  );
}
