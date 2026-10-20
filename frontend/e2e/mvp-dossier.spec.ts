import { test, expect } from "@playwright/test";
import { browserBundle } from "./helpers/browser-bundle";
import path from "node:path";
import { readFile } from "node:fs/promises";
let bundle: string;
const org = "a0000000-0000-0000-0000-000000000001",
  tid = "a0000000-0000-0000-0000-000000000002",
  aid = "a0000000-0000-0000-0000-000000000003";
function packet(): any {
  return {
    schema_version: 1,
    organization_id: org,
    treatment_id: tid,
    assessment_id: aid,
    assessment_version: 1,
    generated_at: "2026-10-16T18:00:00Z",
    data_provenance: "no_verificada",
    scope: "expediente_documental_rat_licitud_lia_eipd",
    rat_snapshot_note: "PRUEBA: snapshot asociado",
    packet_hash: "a".repeat(64),
    hash_algorithm: "sha256_json_sort_keys_utf8",
    legal_acceptance: "pendiente_organizacion_piloto",
    mvp_ready: false,
    allows_real_data: false,
    authorizes_action: false,
    can_confirm: false,
    activation: "deshabilitada",
    documents: ["rat", "licitud_lia", "eipd"].map((kind, i) => ({
      kind,
      status: i === 2 ? "sin_documento" : "disponible",
      version: i === 2 ? null : 1,
      coverage: "PRUEBA cobertura",
      content: i === 2 ? null : { notes: "PRUEBA <script>window.bad=true</script>" },
      content_hash: i === 2 ? null : "b".repeat(64),
      organization_acceptance: i === 2 ? "sin_eventos" : "sin_flujo",
      acceptance_events: [],
    })),
    official_sources: [
      "https://www.diariooficial.interior.gob.cl/publicaciones/2024/12/13/44023/01/2583630.pdf",
      "https://www.bcn.cl/leychile/navegar?i=1209272",
      "https://www.leychile.cl/navegar?idNorma=1227971",
    ].map((url, i) => ({
      reference: `S${i}`,
      title: `Fuente oficial ${i}`,
      url,
      consulted_on: "2026-10-16",
      status: "consultada_sin_aceptacion_juridica",
      scope_note: "PRUEBA alcance",
      legal_verifier: null,
      ...(i === 0 ? { artifact_sha256: "c".repeat(64) } : {}),
    })),
    release_gates: Array.from({ length: 7 }, (_, i) => ({
      id: `G${i + 1}`,
      title: `Gate ${i + 1}`,
      status: i === 0 ? "alcance_definido" : i >= 5 ? "bloqueado" : "pendiente",
      evidence_needed: "PRUEBA evidencia pendiente",
    })),
  };
}
test.beforeAll(async () => {
  bundle = await browserBundle(
    `import React from "react";import {createRoot} from "react-dom/client";import {MvpDossierPanel} from ${JSON.stringify(path.resolve("components/licitud/MvpDossierPanel.tsx"))};import {loadMvpDossier} from ${JSON.stringify(path.resolve("lib/api/mvp-dossier.ts"))};createRoot(document.getElementById("root")).render(React.createElement(MvpDossierPanel,{load:()=>loadMvpDossier({organizationId:${JSON.stringify(org)},treatmentId:${JSON.stringify(tid)},assessmentId:${JSON.stringify(aid)},token:"PRUEBA"})}));`
  );
});
async function setup(page: any, value: any) {
  await page.route("http://test.invalid/**", (route: any) =>
    route.fulfill({ json: value, headers: { "Access-Control-Allow-Origin": "*" } })
  );
  await page.setContent('<div id="root"></div>');
  await page.addScriptTag({ content: bundle });
}
test("consulta y descarga tres documentos sin acciones ni aceptacion real", async ({ page }) => {
  await setup(page, packet());
  await page.getByRole("button", { name: "Consultar expediente documental" }).click();
  await expect(page.getByText(/Procedencia de los datos/)).toBeVisible();
  const sources = page.getByRole("list", { name: "Fuentes oficiales", exact: true });
  await expect(sources.getByRole("listitem")).toHaveCount(2);
  await expect(sources.getByRole("link")).toHaveCount(2);
  await expect(sources.getByRole("link", { name: "Ley 21.719", exact: true })).toHaveAttribute(
    "href",
    "https://www.bcn.cl/leychile/navegar?i=1209272"
  );
  await sources.getByText("Publicación y trazabilidad de esta ley", { exact: true }).click();
  await expect(
    sources.getByRole("link", { name: "Publicación original en el Diario Oficial", exact: true })
  ).toHaveAttribute("href", packet().official_sources[0].url);
  await expect(sources.getByText("SHA-256 de la copia archivada:", { exact: false })).toContainText(
    "c".repeat(64)
  );
  await expect(page.getByRole("button", { name: /aprobar|confirmar|activar/i })).toHaveCount(0);
  const download = page.waitForEvent("download");
  await page.getByRole("button", { name: "Descargar expediente JSON" }).click();
  const file = await download;
  expect(file.suggestedFilename()).toBe(`expediente-mvp-${aid}.json`);
  const exported = JSON.parse(await readFile((await file.path())!, "utf8"));
  expect(exported.official_sources).toEqual(packet().official_sources);
  expect(exported.packet_hash).toBe(packet().packet_hash);
  await page.getByText("RAT asociado — disponible", { exact: true }).click();
  expect(await page.evaluate(() => Boolean((window as any).bad))).toBe(false);
});
for (const mode of ["tenant", "positive", "real-data", "source", "gate", "documents"]) {
  test(`respuesta ${mode} bloquea expediente`, async ({ page }) => {
    const v = packet();
    if (mode === "tenant") v.organization_id = tid;
    if (mode === "positive") v.can_confirm = true;
    if (mode === "real-data") v.allows_real_data = true;
    if (mode === "source") v.official_sources[0].url = "javascript:alert(1)";
    if (mode === "gate") v.release_gates[1].status = "aceptado";
    if (mode === "documents") v.documents.pop();
    await setup(page, v);
    await page.getByRole("button", { name: "Consultar expediente documental" }).click();
    await expect(page.getByRole("alert")).toBeVisible();
    await expect(page.getByRole("button", { name: "Descargar expediente JSON" })).toHaveCount(0);
  });
}
test("fallo al actualizar retira paquete y descarga anteriores", async ({ page }) => {
  await setup(page, packet());
  await page.getByRole("button", { name: "Consultar expediente documental" }).click();
  await expect(page.getByRole("button", { name: "Descargar expediente JSON" })).toBeVisible();
  await page.unroute("http://test.invalid/**");
  await page.route("http://test.invalid/**", (route) =>
    route.fulfill({
      status: 403,
      json: { detail: "PRUEBA permiso retirado" },
      headers: { "Access-Control-Allow-Origin": "*" },
    })
  );
  await page.getByRole("button", { name: "Consultar expediente documental" }).click();
  await expect(page.getByRole("alert")).toBeVisible();
  await expect(page.getByRole("button", { name: "Descargar expediente JSON" })).toHaveCount(0);
});
