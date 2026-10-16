"use client";
import { useState, useRef, useEffect } from "react";
import type { Dossier } from "@/lib/api/mvp-dossier";
const labels = {
  rat: "RAT asociado",
  licitud_lia: "Evaluación de licitud / LIA",
  eipd: "Documento EIPD",
};
export function MvpDossierPanel({ load }: { load: () => Promise<Dossier> }) {
  const [packet, setPacket] = useState<Dossier | null>(null),
    [busy, setBusy] = useState(false),
    [error, setError] = useState("");
  const active = useRef(true),
    running = useRef(false),
    epoch = useRef(0);
  useEffect(() => {
    active.current = true;
    epoch.current++;
    running.current = false;
    setBusy(false);
    setError("");
    setPacket(null);
    return () => {
      active.current = false;
    };
  }, [load]);
  async function consult() {
    if (running.current) return;
    running.current = true;
    const seq = epoch.current;
    setBusy(true);
    setPacket(null);
    setError("");
    try {
      const p = await load();
      if (active.current && seq === epoch.current) setPacket(p);
    } catch {
      if (active.current && seq === epoch.current)
        setError("No se pudo consultar un expediente válido. Descarga bloqueada.");
    } finally {
      if (active.current && seq === epoch.current) {
        running.current = false;
        setBusy(false);
      }
    }
  }
  function download() {
    if (!packet || busy) return;
    const url = URL.createObjectURL(
      new Blob([JSON.stringify(packet, null, 2)], { type: "application/json" })
    );
    const a = document.createElement("a");
    a.href = url;
    a.download = `expediente-mvp-${packet.assessment_id}.json`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 0);
  }
  return (
    <section aria-label="Expediente documental MVP" className="space-y-4 rounded border p-4">
      <h2 className="text-xl font-bold">Expediente documental MVP</h2>
      <p>
        RAT asociado, evaluación de licitud/LIA y EIPD. Solo desarrollo con datos ficticios.
        Consultar o descargar no aprueba documentos ni libera el MVP.
      </p>
      <button type="button" disabled={busy} onClick={() => void consult()}>
        Consultar expediente documental
      </button>
      {error && <p role="alert">{error}</p>}
      {packet && (
        <>
          <p>{packet.rat_snapshot_note}</p>
          <p>
            Procedencia de los datos: no verificada. Aceptación jurídica real pendiente de la
            organización piloto. EIPD bloqueada.
          </p>
          <p className="break-all">Identidad del paquete: {packet.packet_hash}</p>
          <button type="button" disabled={busy} onClick={download}>
            Descargar expediente JSON
          </button>
          {packet.documents.map((d) => (
            <details key={d.kind}>
              <summary>
                {labels[d.kind]} — {d.status === "disponible" ? "disponible" : "sin documento"}
              </summary>
              <p>{d.coverage}</p>
              <p>
                Versión: {d.version ?? "no disponible"}.{" "}
                {d.organization_acceptance === "sin_flujo"
                  ? "Sin flujo de aceptación para este documento."
                  : "Los eventos ficticios corresponden solo a la resolución EIPD indicada."}
              </p>
              <pre className="overflow-auto whitespace-pre-wrap break-all">
                {JSON.stringify(d.content, null, 2)}
              </pre>
              <p>{d.acceptance_events.length} eventos documentales ficticios.</p>
            </details>
          ))}
          <h3>Fuentes oficiales para revisión</h3>
          <p>Consultadas, pendientes de revisión de aplicabilidad y aceptación jurídica.</p>
          <ul>
            {packet.official_sources.map((s) => (
              <li key={s.reference}>
                <a href={s.url} target="_blank" rel="noopener noreferrer" className="text-blue-700">
                  {s.title}
                </a>
                <p>{s.scope_note}</p>
                {s.artifact_sha256 && (
                  <p className="break-all">
                    SHA-256 de la copia archivada: {s.artifact_sha256}. El checksum no acredita
                    aceptación jurídica.
                  </p>
                )}
              </li>
            ))}
          </ul>
          <h3>Criterios de salida a MVP</h3>
          <ul>
            {packet.release_gates.map((g) => (
              <li key={g.id}>
                <strong>
                  {g.id}: {g.title}
                </strong>
                <p>
                  {g.status === "alcance_definido"
                    ? "Alcance definido"
                    : g.status === "bloqueado"
                      ? "Bloqueado"
                      : "Pendiente"}
                  . {g.evidence_needed}
                </p>
              </li>
            ))}
          </ul>
        </>
      )}
    </section>
  );
}
