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
        schema_version: 1,
        data_kind: "ficticios",
        organization_id: org,
        treatment_id: tid,
        assessment_id: aid,
        actor_id: actor,
        authority_id: grant,
        authority_evidence_reference: "PRUEBA facultad",
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
    await page.getByLabel(label, { exact: true }).fill("PRUEBA");
  await page.getByRole("button", { name: "Validar preparación ficticia" }).click();
  await expect(page.getByRole("status")).toContainText(
    "Referencias de prueba completas; evidencia no verificada"
  );
  await expect(page.getByRole("status")).toContainText("Simulación no registrada");
  expect(posts()).toBe(2);
  await page.getByLabel("Decisión de revisión ficticia").selectOption("requiere_cambios");
  await expect(page.getByRole("status")).toHaveCount(0);
});
for (const mode of ["no-authority", "forged"]) {
  test(`rechazo ${mode} conserva referencias`, async ({ page }) => {
    const posts = await setup(page, mode);
    await page.getByRole("checkbox").check();
    await page
      .getByLabel("Referencia de restauración", { exact: true })
      .fill("PRUEBA guardar referencia");
    await page.getByRole("button", { name: "Validar preparación ficticia" }).click();
    await expect(page.getByRole("alert")).toBeVisible();
    await expect(page.getByLabel("Referencia de restauración", { exact: true })).toHaveValue(
      "PRUEBA guardar referencia"
    );
    expect(posts()).toBe(mode === "no-authority" ? 0 : 1);
    await expect(page.getByRole("status")).toHaveCount(0);
  });
}
