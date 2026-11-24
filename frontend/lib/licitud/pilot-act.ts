import { SIMULATION_WATERMARK, type PilotResult } from "@/lib/api/pilot-preparation";
function escape(value: string) {
  return value.replace(
    /[&<>"']/g,
    (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]!
  );
}
export function pilotActHtml(act: PilotResult) {
  if (
    act.watermark !== SIMULATION_WATERMARK ||
    act.data_kind !== "ficticios" ||
    act.can_confirm !== false ||
    act.authorizes_action !== false ||
    act.allows_real_data !== false ||
    act.mvp_ready !== false
  )
    throw new Error("Acta simulada incompatible");
  return `<!doctype html><html lang="es-CL"><head><meta charset="utf-8"><title>${escape(act.act_reference)} — ACTA SIMULADA</title><style>body{font-family:Arial,sans-serif;margin:2rem;line-height:1.5}.mark{border:3px solid #a00;color:#a00;padding:1rem;font-weight:bold}pre{white-space:pre-wrap;overflow-wrap:anywhere}@media print{.mark{color:#000;border-color:#000}}</style></head><body><header class="mark">${escape(SIMULATION_WATERMARK)}</header><h1>${escape(act.act_reference)}</h1><p>${escape(act.scenario_notice)}</p><p>Revisión jurídica: ${act.legal_review_status === "pendiente_no_realizada" ? "PENDIENTE / NO REALIZADA" : "REVISIÓN SIMULADA, SIN VALOR JURÍDICO"}. No hay revisor ni informe jurídico real acreditados.</p><p>Los RUT y la fecha son valores de prueba. Las referencias SIMULADA- no prueban que el contenido sea ficticio ni jurídicamente válido. La identidad técnica de sesión no acredita a la persona del escenario.</p><h2>Escenario y referencias de prueba</h2><pre>${escape(JSON.stringify(act, null, 2))}</pre><footer class="mark">${escape(SIMULATION_WATERMARK)}</footer></body></html>`;
}
export function downloadPilotAct(act: PilotResult, format: "html" | "json") {
  const html = pilotActHtml(act);
  const value = format === "html" ? html : JSON.stringify(act, null, 2);
  const url = URL.createObjectURL(
    new Blob([value], { type: format === "html" ? "text/html;charset=utf-8" : "application/json" })
  );
  const link = document.createElement("a");
  link.href = url;
  link.download = `${act.act_reference}.${format}`;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 0);
}
