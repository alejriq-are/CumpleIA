import { test, expect, type Page } from "@playwright/test";
import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { browserBundle } from "./helpers/browser-bundle";
let script: string;
const org = "a0000000-0000-0000-0000-000000000001",
  tid = "a0000000-0000-0000-0000-000000000002",
  aid = "a0000000-0000-0000-0000-000000000003";
test.beforeAll(async () => {
  script = await browserBundle(`
 import React from "react";import {createRoot} from "react-dom/client";
 import {AssessmentSupportPanel} from ${JSON.stringify(path.resolve("components/licitud/AssessmentSupportPanel.tsx"))};
 const root=createRoot(document.getElementById("root"));let key=0;
 const row={status:"borrador",eipd_resolution_assessment:{risks:[{risk_id:"R1"}],measures:[{measure_id:"M1",risk_ids:["R1"]}]}};
 window.show=(mode="risks",readOnly=false)=>root.render(React.createElement(AssessmentSupportPanel,{key:++key,organizationId:${JSON.stringify(org)},treatmentId:${JSON.stringify(tid)},assessmentId:${JSON.stringify(aid)},token:async()=>"PRUEBA",row,readOnly,blocked:false,refreshVersion:0,mode,hidden:false,onSaved:()=>{},onLoaded:()=>{},onDirty:()=>{}}));
 `);
});
async function setup(page: Page, mode = "risks", failure = "", readOnly = false) {
  const state: any = {
    schema_version: 1,
    organization_id: org,
    treatment_id: tid,
    assessment_id: aid,
    document_hash: "a".repeat(64),
    risk_evaluation: null,
    risk_history: [],
    annexes: [],
    can_confirm: false,
    activation: "deshabilitada",
  };
  const writes: any[] = [];
  let bytes = Buffer.from("");
  await page.route("http://localhost/__support-test", (r) =>
    r.fulfill({ body: '<div id="root"></div>', contentType: "text/html" })
  );
  await page.route("http://test.invalid/**", async (r) => {
    if (r.request().method() === "OPTIONS")
      return r.fulfill({
        status: 204,
        headers: {
          "access-control-allow-origin": "*",
          "access-control-allow-headers": "*",
          "access-control-allow-methods": "GET,POST",
        },
      });
    const send = (body: any, status = 200) =>
      r.fulfill({
        status,
        contentType: "application/json",
        headers: { "access-control-allow-origin": "*" },
        body: JSON.stringify(body),
      });
    if (r.request().method() === "GET") {
      if (r.request().url().endsWith("/content"))
        return r.fulfill({ body: bytes, headers: { "access-control-allow-origin": "*" } });
      return send(state);
    }
    const body = r.request().postDataJSON();
    writes.push(body);
    if (failure === "denied") return send({ detail: "PRUEBA sin permiso" }, 403);
    if (failure === "unknown") return r.abort();
    if (r.request().url().endsWith("/risk-evaluations")) {
      state.risk_evaluation = {
        id: aid,
        revision: 1,
        current: true,
        analysis: body.analysis,
        result: {
          risks: [
            {
              risk_id: "R1",
              inherent: "alto",
              projected: "sin_resolver",
              residual: "sin_resolver",
            },
          ],
          worst_residual: "sin_resolver",
          unresolved: true,
          can_confirm: false,
          activation: "deshabilitada",
        },
      };
    } else {
      bytes = Buffer.from(body.content_base64, "base64");
      state.annexes.push({
        ...body,
        id: aid,
        version: 1,
        size: bytes.length,
        sha256: createHash("sha256").update(bytes).digest("hex"),
        mime: "text/plain",
        created_at: "2026-10-20",
      });
    }
    if (failure === "mismatch")
      state.risk_evaluation.analysis.risks[0].harm = "[FICTICIA] Respuesta distinta";
    return send(state, 201);
  });
  await page.goto("http://localhost/__support-test");
  if (process.env.CUMPLEIA_PREVIEW_CSS)
    await page.addStyleTag({ path: process.env.CUMPLEIA_PREVIEW_CSS });
  await page.addScriptTag({ content: script });
  await page.evaluate(({ mode, readOnly }) => (window as any).show(mode, readOnly), {
    mode,
    readOnly,
  });
  await expect(page.getByRole("heading", { level: 2 })).toBeVisible();
  return { state, writes };
}
async function fillRisk(page: Page) {
  await page
    .getByLabel("R1 — Daño potencial a las personas", { exact: true })
    .fill("[FICTICIA] Exposición de información y pérdida de control");
  await page
    .getByLabel("R1 — Inherente, antes de controles — Probabilidad", { exact: true })
    .selectOption("2");
  await page
    .getByLabel("R1 — Inherente, antes de controles — Impacto", { exact: true })
    .selectOption("3");
  await page
    .getByLabel("R1 — Inherente, antes de controles — Fundamento", { exact: true })
    .fill("[FICTICIA] Exposición plausible con perjuicio grave");
}
test("conserva valoración fundamentada y la recupera sin presumir residual verificado", async ({
  page,
}) => {
  const { writes } = await setup(page);
  await fillRisk(page);
  await page.getByRole("button", { name: "Guardar valoración de riesgos", exact: true }).click();
  await expect(page.getByRole("status")).toContainText("Valoración guardada");
  expect(writes[0].analysis.risks[0].residual.probability).toBeNull();
  expect(writes[0].analysis.controls[0].status).toBe("propuesta");
  await page.evaluate(() => (window as any).show());
  await expect(page.getByLabel("R1 — Daño potencial a las personas", { exact: true })).toHaveValue(
    /pérdida de control/
  );
});
test("requiere declaración ficticia, guarda anexo y descarga exactamente sus bytes", async ({
  page,
}) => {
  await setup(page, "annexes");
  await page.getByLabel("Referencia del anexo (SIMULADA-)", { exact: true }).fill("SIMULADA-A1");
  await page
    .getByLabel("Descripción del anexo", { exact: true })
    .fill("[FICTICIA] Matriz de permisos");
  const bytes = Buffer.from("[FICTICIA] Matriz de acceso del ensayo");
  await page
    .getByLabel("Archivo ficticio PDF o TXT", { exact: true })
    .setInputFiles({ name: "matriz.txt", mimeType: "text/plain", buffer: bytes });
  await expect(
    page.getByRole("button", { name: "Guardar anexo ficticio", exact: true })
  ).toBeDisabled();
  await page.getByLabel("Confirmo que el archivo y sus datos son ficticios").check();
  await page.getByRole("button", { name: "Guardar anexo ficticio", exact: true }).click();
  await expect(page.getByRole("status")).toContainText("Anexo ficticio guardado");
  const pending = page.waitForEvent("download");
  await page.getByRole("button", { name: "Descargar SIMULADA-A1 versión 1", exact: true }).click();
  const downloaded = await pending;
  expect(downloaded.suggestedFilename()).toBe("matriz.txt");
  expect(await readFile((await downloaded.path())!)).toEqual(bytes);
  await expect(page.getByLabel("Archivo ficticio PDF o TXT", { exact: true })).toHaveValue("");
});
for (const failure of ["denied", "unknown", "mismatch"]) {
  test(`preserva ediciones ante ${failure} y bloquea reintento incierto`, async ({ page }) => {
    const { writes } = await setup(page, "risks", failure);
    await fillRisk(page);
    await page.getByRole("button", { name: "Guardar valoración de riesgos", exact: true }).click();
    await expect(page.getByRole("alert")).toContainText(
      failure !== "denied" ? "Resultado incierto" : "sin permiso"
    );
    await expect(
      page.getByLabel("R1 — Daño potencial a las personas", { exact: true })
    ).toHaveValue(/Exposición/);
    expect(writes).toHaveLength(1);
    await expect(page.getByRole("status")).toHaveCount(0);
    if (failure !== "denied")
      await expect(
        page.getByRole("button", { name: "Guardar valoración de riesgos", exact: true })
      ).toBeDisabled();
  });
}
test("rol de consulta no permite escribir", async ({ page }) => {
  const { writes } = await setup(page, "risks", "", true);
  await expect(
    page.getByRole("button", { name: "Guardar valoración de riesgos", exact: true })
  ).toBeDisabled();
  expect(writes).toHaveLength(0);
});

test("metodología y formulario accesibles en móvil", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await setup(page);
  await page.getByText("Metodología CUMPLEIA-CUALITATIVA-1 y criterios", { exact: true }).click();
  if (process.env.CUMPLEIA_PREVIEW_CSS) {
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(
      true
    );
    await page.screenshot({ path: "/tmp/cumpleia-risk-method-mobile.png", fullPage: true });
  }
});
