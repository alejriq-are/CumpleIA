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
  const { writes } = await setup(page, "annexes");
  await page.getByLabel("Referencia del anexo (SIMULADA-)", { exact: true }).fill("SIMULADA-A1");
  const riskLink = page.getByLabel("Códigos de riesgos vinculados (opcional; ejemplo: R1)", {
    exact: true,
  });
  const measureLink = page.getByLabel("Códigos de medidas vinculadas (opcional; ejemplo: M1)", {
    exact: true,
  });
  await expect(riskLink).toBeHidden();
  await page.getByText("Vínculos opcionales con riesgos y medidas", { exact: true }).click();
  await riskLink.fill("R1");
  await measureLink.fill("M1");
  await page.getByLabel("Sección relacionada", { exact: true }).selectOption("base");
  await expect(riskLink).toHaveValue("R1");
  await expect(measureLink).toHaveValue("M1");
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
  const savedAnnex = page.getByRole("article").filter({ hasText: "SIMULADA-A1 · versión 1" });
  await expect(savedAnnex.locator("dl > div").nth(0)).toHaveText(
    "Sección relacionada: Base y fundamento"
  );
  await expect(savedAnnex.locator("dl > div").nth(1)).toHaveText("Riesgos vinculados: R1");
  await expect(savedAnnex.locator("dl > div").nth(2)).toHaveText("Medidas vinculadas: M1");
  expect(writes[0].section).toBe("base");
  expect(writes[0].risk_ids).toEqual(["R1"]);
  expect(writes[0].measure_ids).toEqual(["M1"]);
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

for (const [filename, size, reason] of [
  ["prueba.csv", 20, "Formato no admitido"],
  ["grande.txt", 2097153, "supera el tamaño máximo"],
  ["vacio.txt", 0, "está vacío"],
] as const) {
  test(`anexo ${filename}: archivo inválido bloquea guardar sin duplicar error y permite corregir`, async ({
    page,
  }) => {
    const { writes } = await setup(page, "annexes");
    await page
      .getByLabel("Referencia del anexo (SIMULADA-)", { exact: true })
      .fill("SIMULADA-VALIDACION");
    await page
      .getByLabel("Descripción del anexo", { exact: true })
      .fill("[FICTICIA] Descripción conservada");
    await page.getByLabel("Sección relacionada", { exact: true }).selectOption("medidas");
    await page.getByText("Vínculos opcionales con riesgos y medidas", { exact: true }).click();
    await page
      .getByLabel("Códigos de riesgos vinculados (opcional; ejemplo: R1)", { exact: true })
      .fill("R1");
    await page
      .getByLabel("Códigos de medidas vinculadas (opcional; ejemplo: M1)", { exact: true })
      .fill("M1");
    const input = page.getByLabel("Archivo ficticio PDF o TXT", { exact: true });
    await input.setInputFiles({
      name: filename,
      mimeType: "text/plain",
      buffer: Buffer.alloc(size, 88),
    });
    await expect(input).toHaveAttribute("aria-invalid", "true");
    await expect(input).toHaveAccessibleDescription(new RegExp(reason));
    await page.getByLabel("Confirmo que el archivo y sus datos son ficticios").check();
    const save = page.getByRole("button", { name: "Guardar anexo ficticio", exact: true });
    await expect(save).toBeDisabled();
    await expect(save).toHaveAccessibleDescription(/Corrige el archivo/);
    await expect(page.getByRole("alert")).toHaveCount(1);
    await expect(page.getByRole("alert")).toContainText(reason);
    expect(writes).toHaveLength(0);
    await expect(page.getByLabel("Descripción del anexo", { exact: true })).toHaveValue(
      "[FICTICIA] Descripción conservada"
    );
    await expect(page.getByRole("status")).toHaveCount(0);
    await input.setInputFiles({
      name: "corregido.txt",
      mimeType: "text/plain",
      buffer: Buffer.from("[FICTICIA] Corregido"),
    });
    await expect(input).toHaveAttribute("aria-invalid", "false");
    await expect(page.getByRole("alert")).toHaveCount(0);
    await expect(page.getByLabel("Referencia del anexo (SIMULADA-)", { exact: true })).toHaveValue(
      "SIMULADA-VALIDACION"
    );
    await expect(page.getByLabel("Sección relacionada", { exact: true })).toHaveValue("medidas");
    await expect(
      page.getByLabel("Códigos de riesgos vinculados (opcional; ejemplo: R1)", { exact: true })
    ).toHaveValue("R1");
    await expect(
      page.getByLabel("Códigos de medidas vinculadas (opcional; ejemplo: M1)", { exact: true })
    ).toHaveValue("M1");
    await expect(
      page.getByLabel("Confirmo que el archivo y sus datos son ficticios")
    ).toBeChecked();
    await expect(save).toBeEnabled();
    await save.focus();
    await page.keyboard.press("Space");
    await expect(page.getByRole("status")).toContainText("Anexo ficticio guardado");
    expect(writes).toHaveLength(1);
  });
}
test("resumen pendiente no inventa un mayor residual evaluado", async ({ page }) => {
  await setup(page);
  await fillRisk(page);
  await page.getByRole("button", { name: "Guardar valoración de riesgos", exact: true }).click();
  await expect(page.getByRole("status")).toContainText("Valoración guardada");
  await page.evaluate(() => (window as any).show("review"));
  await expect(
    page.getByText("Evaluación del riesgo residual actual pendiente.", { exact: true })
  ).toBeVisible();
  await expect(page.getByText(/Mayor residual actual registrado/)).toHaveCount(0);
});

for (const width of [1280, 390, 320]) {
  test(`matriz legible con cabeceras alineadas a ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    const { writes } = await setup(page);
    await page.getByText("Metodología CUMPLEIA-CUALITATIVA-1 y criterios", { exact: true }).click();
    const table = page.getByRole("table");
    await expect(table).toBeVisible();
    await expect(table.getByRole("columnheader")).toHaveCount(5);
    await expect(table.getByRole("rowheader")).toHaveCount(4);
    await expect(table.getByRole("cell")).toHaveText([
      "Bajo",
      "Bajo",
      "Medio",
      "Alto",
      "Bajo",
      "Medio",
      "Alto",
      "Alto",
      "Medio",
      "Alto",
      "Alto",
      "Muy alto",
      "Alto",
      "Alto",
      "Muy alto",
      "Muy alto",
    ]);
    if (process.env.CUMPLEIA_PREVIEW_CSS) {
      const cells = table.locator("tbody tr").first().locator("td");
      const headers = table.getByRole("columnheader");
      for (let col = 0; col < 4; col++) {
        const header = await headers.nth(col + 1).boundingBox();
        const cell = await cells.nth(col).boundingBox();
        expect(Math.abs(header!.x + header!.width / 2 - cell!.x - cell!.width / 2)).toBeLessThan(1);
        await expect(cells.nth(col)).toHaveCSS("text-align", "center");
      }
      await expect(cells.nth(0)).toHaveCSS("background-color", "rgb(220, 252, 231)");
      await expect(cells.nth(2)).toHaveCSS("background-color", "rgb(254, 249, 195)");
      await expect(cells.nth(3)).toHaveCSS("background-color", "rgb(254, 215, 170)");
      await expect(table.getByRole("cell", { name: "Muy alto", exact: true }).first()).toHaveCSS(
        "background-color",
        "rgb(254, 202, 202)"
      );
      expect(
        await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)
      ).toBeTruthy();
    }
    expect(writes).toHaveLength(0);
    if (process.env.MATRIX_SCREENSHOTS) {
      await table.getByRole("rowheader", { name: "Baja", exact: true }).scrollIntoViewIfNeeded();
      await page.screenshot({ path: `${process.env.MATRIX_SCREENSHOTS}/matriz-${width}.png` });
    }
  });
}

test("11A valoración explica horizonte, fundamentos y verificación sin escribir", async ({
  page,
}) => {
  const { writes } = await setup(page);
  await expect(
    page.getByLabel("Horizonte temporal de la valoración", { exact: true })
  ).toHaveAccessibleDescription(/período.*12 meses/);
  await expect(
    page.getByLabel("R1 — Inherente, antes de controles — Fundamento", { exact: true })
  ).toHaveAccessibleDescription(/justifican los niveles/);
  await expect(
    page.getByRole("group", { name: "R1 — Residual actual verificado", exact: true })
  ).toHaveAccessibleDescription(/implementadas.*evidencias/);
  await fillRisk(page);
  expect(writes).toHaveLength(0);
});

test("anexo: borrar selección y rechazo del servidor conservan datos sin anunciar éxito", async ({
  page,
}) => {
  const { writes } = await setup(page, "annexes", "denied");
  const input = page.getByLabel("Archivo ficticio PDF o TXT", { exact: true });
  const save = page.getByRole("button", { name: "Guardar anexo ficticio", exact: true });
  await expect(save).toBeDisabled();
  await expect(save).toHaveAccessibleDescription(/selecciona un archivo/);
  await page
    .getByLabel("Referencia del anexo (SIMULADA-)", { exact: true })
    .fill("SIMULADA-RECHAZO");
  await page
    .getByLabel("Descripción del anexo", { exact: true })
    .fill("[FICTICIA] Conservar ante rechazo");
  const file = {
    name: "valido.txt",
    mimeType: "text/plain",
    buffer: Buffer.from("[FICTICIA] Texto"),
  };
  await input.setInputFiles(file);
  await expect(save).toBeDisabled();
  await expect(save).toHaveAccessibleDescription(/confirma/);
  await page.getByLabel("Confirmo que el archivo y sus datos son ficticios").check();
  await expect(save).toBeEnabled();
  await input.setInputFiles([]);
  await expect(save).toBeDisabled();
  await expect(save).toHaveAccessibleDescription(/selecciona un archivo/);
  await input.setInputFiles(file);
  await save.click();
  await expect(page.getByRole("alert")).toHaveCount(1);
  await expect(page.getByRole("alert")).toContainText("sin permiso");
  await expect(page.getByRole("alert")).toBeFocused();
  await expect(page.getByRole("status")).toHaveCount(0);
  await expect(page.getByLabel("Descripción del anexo", { exact: true })).toHaveValue(
    "[FICTICIA] Conservar ante rechazo"
  );
  await expect(input).toHaveAttribute("aria-invalid", "false");
  expect(writes).toHaveLength(1);
});

for (const width of [1280, 390, 320]) {
  test(`anexos: aviso y vínculos opcionales legibles con teclado a ${width}px`, async ({
    page,
  }) => {
    await page.setViewportSize({ width, height: 900 });
    const { writes } = await setup(page, "annexes");
    const disclosure = page.getByText("Vínculos opcionales con riesgos y medidas", { exact: true });
    await page.getByLabel("Sección relacionada", { exact: true }).focus();
    await page.keyboard.press("Tab");
    await expect(disclosure).toBeFocused();
    const risks = page.getByLabel("Códigos de riesgos vinculados (opcional; ejemplo: R1)", {
      exact: true,
    });
    for (let cycle = 0; cycle < 3; cycle++) {
      await page.keyboard.down("Space");
      await expect(risks).toBeVisible();
      await page.keyboard.down("Space");
      await expect(risks).toBeVisible();
      await page.keyboard.up("Space");
      await expect(risks).toBeVisible();
      await expect(disclosure).toBeFocused();
      if (cycle === 0) await risks.fill("R1");
      await disclosure.focus();
      await page.keyboard.press("Space");
      await expect(risks).toBeHidden();
    }
    await page.keyboard.press("Enter");
    await expect(risks).toBeVisible();
    await expect(risks).toHaveValue("R1");
    await disclosure.click();
    await expect(risks).toBeHidden();
    await page.getByLabel("Archivo ficticio PDF o TXT", { exact: true }).setInputFiles({
      name: "invalido.csv",
      mimeType: "text/csv",
      buffer: Buffer.from("[FICTICIA]"),
    });
    await expect(page.getByRole("alert")).toContainText("Formato no admitido");
    await expect(
      page.getByRole("button", { name: "Guardar anexo ficticio", exact: true })
    ).toBeDisabled();
    if (process.env.CUMPLEIA_PREVIEW_CSS) {
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(
        true
      );
      await page.screenshot({
        path: `/tmp/cumpleia-annex-validation-${width}.png`,
        fullPage: true,
      });
    }
    expect(writes).toHaveLength(0);
  });
}
