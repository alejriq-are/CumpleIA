import { readFile } from "node:fs/promises";
import { SIMULATION_WATERMARK, pilotScenario } from "../lib/api/pilot-preparation";
import { test, expect } from "@playwright/test";
import path from "node:path";
import { browserBundle } from "./helpers/browser-bundle";
let bundle: string;
const org = "a0000000-0000-0000-0000-000000000001",
  tid = "a0000000-0000-0000-0000-000000000002",
  aid = "a0000000-0000-0000-0000-000000000003",
  actor = "a0000000-0000-0000-0000-000000000004",
  grant = "a0000000-0000-0000-0000-000000000005";
test.beforeAll(async () => {
  bundle = await browserBundle(
    `import React from "react";import {createRoot} from "react-dom/client";import {PilotPreparationPanel} from ${JSON.stringify(path.resolve("components/licitud/PilotPreparationPanel.tsx"))};import {preparePilot} from ${JSON.stringify(path.resolve("lib/api/pilot-preparation.ts"))};const s={organizationId:${JSON.stringify(org)},treatmentId:${JSON.stringify(tid)},assessmentId:${JSON.stringify(aid)},token:"PRUEBA"};const packet={organization_id:s.organizationId,treatment_id:s.treatmentId,assessment_id:s.assessmentId,documents:["rat","licitud_lia","eipd"].map(kind=>({kind,content_hash:"a".repeat(64)}))};createRoot(document.getElementById("root")).render(React.createElement(PilotPreparationPanel,{packet,prepare:(p,f)=>preparePilot(s,p,f)}));`
  );
});
async function setup(page: any, mode: string) {
  let posts = 0;
  await page.route("http://test.invalid/**", async (route: any) => {
    const r = route.request();
    if (r.method() === "GET")
      return route.fulfill({
        json: {
          actor_id: actor,
          can_confirm: false,
          authorizes_action: false,
          authorities:
            mode === "no-authority"
              ? []
              : [
                  {
                    id: grant,
                    organization_id: org,
                    treatment_id: tid,
                    assessment_id: aid,
                    actor_id: actor,
                    revision: 1,
                    action: "otorgar",
                    data_kind: "ficticios",
                    can_confirm: false,
                    authorizes_action: false,
                  },
                ],
        },
        headers: { "Access-Control-Allow-Origin": "*" },
      });
    posts++;
    const p = r.postDataJSON();
    expect(p.data_kind).toBe("ficticios");
    expect(p.actor_id).toBeUndefined();
    const missing = Object.entries(p)
      .filter(([k, v]) => k.endsWith("_reference") && !v)
      .map(([k]) => k);
    if (p.review_decision !== "acepta") missing.push("revision_juridica_ficticia_no_aceptada");
    return route.fulfill({
      json: {
        schema_version: 2,
        watermark: mode === "watermark" ? "ACTA" : SIMULATION_WATERMARK,
        scenario:
          mode === "scenario"
            ? { ...pilotScenario, company: { ...pilotScenario.company, name: "Empresa real" } }
            : pilotScenario,
        act_reference: p.act_reference,
        designation_reference: p.designation_reference,
        scenario_notice:
          "Escenario ficticio; no identifica ni acredita a la organización o persona real de la sesión.",
        legal_review_status:
          p.review_decision === "pendiente"
            ? "pendiente_no_realizada"
            : "simulada_sin_valor_juridico",
        data_kind: "ficticios",
        organization_id: org,
        treatment_id: tid,
        assessment_id: aid,
        actor_id: actor,
        authority_id: grant,
        authority_evidence_reference: "SIMULADA-ENLACE-FACULTAD-001",
        document_hashes: p.document_hashes,
        declared_references: Object.fromEntries(
          Object.entries(p).filter(([k]) => k.endsWith("_reference"))
        ),
        review_decision: p.review_decision,
        missing,
        preparation_complete: missing.length === 0,
        evidence_status: "declarada_no_verificada",
        persistence: "simulacion_no_registrada",
        legal_acceptance: "pendiente_organizacion_piloto",
        mvp_ready: mode === "forged",
        allows_real_data: false,
        can_confirm: false,
        authorizes_action: false,
        activation: "deshabilitada",
      },
      headers: { "Access-Control-Allow-Origin": "*" },
    });
  });
  await page.setContent('<div id="root"></div>');
  await page.addScriptTag({ content: bundle });
  return () => posts;
}
test("campos faltantes visibles y completos no liberan MVP", async ({ page }) => {
  const posts = await setup(page, "valid");
  await expect(page.getByRole("button", { name: "Validar preparación ficticia" })).toBeDisabled();
  await page.getByRole("checkbox").check();
  await page.getByRole("button", { name: "Validar preparación ficticia" }).click();
  await expect(page.getByRole("status")).toContainText("Faltan referencias");
  await expect(page.getByLabel("Decisión de revisión ficticia")).toHaveValue("pendiente");
  const pendingDownload = page.waitForEvent("download");
  await page.getByRole("button", { name: "Descargar acta simulada JSON", exact: true }).click();
  const pendingFile = await pendingDownload;
  const pending = JSON.parse(await readFile((await pendingFile.path())!, "utf8"));
  expect(pending.watermark).toBe(SIMULATION_WATERMARK);
  expect(pending.legal_review_status).toBe("pendiente_no_realizada");
  expect(pending.declared_references.review_reference).toBeNull();
  expect(pending.scenario.company.name).toBe("[FICTICIA] Comercial Piloto Andes SpA");
  expect(pending.scenario.designation.date_status).toBe("simulada");
  expect(pending.mvp_ready).toBe(false);

  await page.getByLabel("Decisión de revisión ficticia").selectOption("acepta");
  for (const label of [
    "Referencia de revisión jurídica ficticia",
    "Referencia de entorno",
    "Referencia de control de accesos",
    "Referencia de restauración",
    "Referencia de retención",
    "Referencia de soporte",
    "Referencia de incidentes",
  ])
    await page.getByLabel(label, { exact: true }).fill("SIMULADA-PILOTO-REF-001");
  await page.getByRole("button", { name: "Validar preparación ficticia" }).click();
  await expect(page.getByRole("status")).toContainText(
    "Referencias de prueba completas; evidencia no verificada"
  );
  await expect(page.getByRole("status")).toContainText("Simulación no registrada");
  const download = page.waitForEvent("download");
  await page.getByRole("button", { name: "Descargar acta simulada HTML", exact: true }).click();
  const artifact = await download;
  expect(artifact.suggestedFilename()).toBe("SIMULADA-PILOTO-ACTA-001.html");
  expect(posts()).toBe(2);
  await page.getByLabel("Decisión de revisión ficticia").selectOption("requiere_cambios");
  await expect(page.getByRole("status")).toHaveCount(0);
});
for (const mode of ["no-authority", "forged", "watermark", "scenario"]) {
  test(`rechazo ${mode} conserva referencias`, async ({ page }) => {
    const posts = await setup(page, mode);
    await page.getByRole("checkbox").check();
    await page
      .getByLabel("Referencia de restauración", { exact: true })
      .fill("SIMULADA-PILOTO-REST-001");
    await page.getByRole("button", { name: "Validar preparación ficticia" }).click();
    await expect(page.getByRole("alert")).toBeVisible();
    await expect(page.getByLabel("Referencia de restauración", { exact: true })).toHaveValue(
      "SIMULADA-PILOTO-REST-001"
    );
    expect(posts()).toBe(mode === "no-authority" ? 0 : 1);
    await expect(page.getByRole("status")).toHaveCount(0);
  });
}
