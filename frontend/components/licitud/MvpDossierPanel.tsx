"use client";
import { PilotPreparationPanel, type PilotPrepare } from "./PilotPreparationPanel";
import { useState, useRef, useEffect } from "react";
import { DossierDocumentView, record } from "./DossierDocumentView";
import type { Dossier } from "@/lib/api/mvp-dossier";
const labels = {
  rat: "RAT asociado",
  licitud_lia: "Evaluación de licitud / LIA",
  eipd: "Documento EIPD",
};
export function MvpDossierPanel({
  load,
  prepare,
}: {
  load: () => Promise<Dossier>;
  prepare?: PilotPrepare;
}) {
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
  const originalLawSource = packet?.official_sources.find(
    (source) =>
      source.url ===
      "https://www.diariooficial.interior.gob.cl/publicaciones/2024/12/13/44023/01/2583630.pdf"
  );
  const consultationLawSource = packet?.official_sources.find(
    (source) => source.url === "https://www.bcn.cl/leychile/navegar?i=1209272"
  );
  const sources = packet?.official_sources.filter(
    (source) => !(originalLawSource && consultationLawSource && source === originalLawSource)
  );
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
          <p>
            El expediente conserva el contexto RAT asociado a esta evaluación. Consultarlo no
            aprueba los documentos.
          </p>
          <p>
            Procedencia de los datos: no verificada. Aceptación jurídica real pendiente de la
            organización piloto. EIPD bloqueada.
          </p>
          <details>
            <summary>Identificación técnica del expediente</summary>
            <p className="break-all">Identidad del paquete: {packet.packet_hash}</p>
          </details>
          <button type="button" disabled={busy} onClick={download}>
            Descargar expediente JSON
          </button>
          {packet.documents.map((d) => (
            <details key={d.kind}>
              <summary>
                {labels[d.kind]} — {d.status === "disponible" ? "disponible" : "sin documento"}
              </summary>
              <div className="space-y-4 rounded border p-4">
                <p>
                  {d.kind === "rat"
                    ? "Contexto del RAT conservado al crear la evaluación. No representa necesariamente el inventario actual."
                    : d.kind === "licitud_lia"
                      ? "Evaluación guardada y análisis de interés legítimo, si se completó. Su guardado no implica aprobación."
                      : record(d.content).document
                        ? "Resolución documental registrada. Los eventos mostrados corresponden exclusivamente a esta resolución."
                        : "Borrador EIPD guardado, pendiente de completar y revisar. Su guardado no implica aprobación."}
                </p>
                <p>
                  {d.kind === "eipd" && !record(d.content).document
                    ? `Evaluación asociada: versión ${packet.assessment_version}.`
                    : `Versión: ${d.version ?? "no disponible"}.`}
                </p>
                <DossierDocumentView document={d} />
                {d.kind === "eipd" && Boolean(record(d.content).document) && (
                  <p>
                    {d.acceptance_events.length} eventos documentales ficticios asociados a esta
                    resolución.
                  </p>
                )}
                <details>
                  <summary>Detalle técnico del documento (JSON)</summary>
                  <pre className="overflow-auto whitespace-pre-wrap break-all">
                    {JSON.stringify(d.content, null, 2)}
                  </pre>
                </details>
              </div>
            </details>
          ))}
          <h3>Fuentes oficiales para revisión</h3>
          <p>Consultadas, pendientes de revisión de aplicabilidad y aceptación jurídica.</p>
          <ul aria-label="Fuentes oficiales">
            {sources?.map((s) => (
              <li key={s.reference}>
                <a href={s.url} target="_blank" rel="noopener noreferrer" className="text-blue-700">
                  {s === consultationLawSource ? "Ley 21.719" : s.title}
                </a>
                <p>{s.scope_note}</p>
                {s === consultationLawSource && originalLawSource && (
                  <>
                    <p>Consulta en la Biblioteca del Congreso Nacional.</p>
                    <details>
                      <summary>Publicación y trazabilidad de esta ley</summary>
                      <a
                        href={originalLawSource.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-700"
                      >
                        Publicación original en el Diario Oficial
                      </a>
                      <p>{originalLawSource.scope_note}</p>
                      {originalLawSource.artifact_sha256 && (
                        <p className="break-all">
                          SHA-256 de la copia archivada: {originalLawSource.artifact_sha256}. El
                          checksum no acredita aceptación jurídica.
                        </p>
                      )}
                    </details>
                  </>
                )}
                {s.artifact_sha256 && (
                  <p className="break-all">
                    SHA-256 de la copia archivada: {s.artifact_sha256}. El checksum no acredita
                    aceptación jurídica.
                  </p>
                )}
              </li>
            ))}
          </ul>
          {prepare && (
            <PilotPreparationPanel key={packet.packet_hash} packet={packet} prepare={prepare} />
          )}
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
