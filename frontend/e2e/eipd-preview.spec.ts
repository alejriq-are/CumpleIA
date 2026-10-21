import { test, expect } from "@playwright/test";
import { browserBundle } from "./helpers/browser-bundle";
import path from "node:path";
let bundle: string;
test.beforeAll(async () => {
  bundle = await browserBundle(
    `import React from "react";import {createRoot} from "react-dom/client";import {EipdDocumentView} from ${JSON.stringify(path.resolve("components/licitud/EipdDocumentFields.tsx"))};window.renderPreview=(value,valuation)=>createRoot(document.getElementById("root")).render(React.createElement(EipdDocumentView,{value,expanded:true,valuation}));`
  );
});
const value = {
  schema_version: 1,
  purpose_description: "[FICTICIA] Revisar el ensayo de trabajadores",
  residual_risk_level: "alto",
  risks: [
    {
      risk_id: "R1",
      description: "[FICTICIA] Acceso indebido",
      impact_analysis: "[FICTICIA] Exposición",
      initial_assessment_analysis: "[FICTICIA] Análisis inicial R1",
      residual_assessment_analysis: "[FICTICIA] Residual R1",
      evidence: [
        { evidence_type: "[FICTICIA] Matriz de accesos", reference: "SIMULADA-EVIDENCIA-R1" },
      ],
    },
    {
      risk_id: "R2",
      description: "[FICTICIA] Pérdida",
      impact_analysis: "[FICTICIA] Indisponibilidad",
      residual_assessment_analysis: "[FICTICIA] Residual R2",
    },
    { risk_id: "R3", description: "[FICTICIA] Sin controles" },
  ],
  measures: [
    {
      measure_id: "M1",
      description: "[FICTICIA] Permisos",
      risk_ids: ["R1"],
      effectiveness_analysis: "[FICTICIA] Eficacia M1 pendiente",
      implemented: { answer: "pendiente", rationale: "[FICTICIA] Verificación pendiente" },
    },
    {
      measure_id: "M2",
      description: "[FICTICIA] Control compartido",
      risk_ids: ["R1", "R2"],
      implemented: { answer: "no" },
    },
    { measure_id: "M3", description: "[FICTICIA] Sin asociación", risk_ids: ["R99"] },
  ],
};
async function setup(page: import("@playwright/test").Page, doc: unknown) {
  await page.setContent(
    '<main style="max-width:1200px;margin:auto;padding:16px"><div id="root"></div></main>'
  );
  if (process.env.CUMPLEIA_PREVIEW_CSS)
    await page.addStyleTag({ path: process.env.CUMPLEIA_PREVIEW_CSS });
  await page.addScriptTag({ content: bundle });
  await page.evaluate((doc) => (window as any).renderPreview(doc), doc);
}
test("relaciona riesgos y controles sin asignar niveles ni perder las evidencias", async ({
  page,
}) => {
  await setup(page, value);
  const table = page.getByRole("table");
  const first = table.getByRole("row").nth(1),
    second = table.getByRole("row").nth(2),
    third = table.getByRole("row").nth(3);
  await expect(first).toContainText("M1");
  await expect(first).toContainText("M2");
  await expect(first).toContainText("Implementada: Pendiente");
  await expect(first).toContainText("Residual R1");
  await expect(second).toContainText("M2");
  await expect(second).not.toContainText("M1");
  await expect(second).toContainText("Residual R2");
  await expect(third).toContainText("Sin medidas asociadas a este riesgo");
  await expect(table).not.toContainText("M3");
  await expect(page.getByRole("note")).toContainText("M3");
  await expect(table).not.toContainText("Alto");
  await expect(page.getByText("Alto", { exact: true })).toBeVisible();
  await page.getByText("Análisis y evidencias por riesgo y medida", { exact: true }).click();
  await expect(page.getByText("SIMULADA-EVIDENCIA-R1", { exact: true })).toBeVisible();
  await expect(page.getByText("[FICTICIA] Sin asociación", { exact: true })).toBeVisible();
});
test("titulos y respuestas diferenciados y tabla navegable en movil", async ({ page }) => {
  await setup(page, value);
  await page.setViewportSize({ width: 390, height: 844 });
  const title = page.locator("dt").filter({ hasText: "Finalidad del tratamiento" });
  await expect(title).toHaveClass(/bg-blue-100/);
  await expect(title.locator("+ dd")).toHaveClass(/bg-white/);
  const region = page.getByRole("region", {
    name: "Tabla de riesgos y controles; desplazamiento horizontal",
    exact: true,
  });
  await expect(region).toHaveAttribute("tabindex", "0");
  if (process.env.CUMPLEIA_PREVIEW_CSS) {
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(
      true
    );
    await region.evaluate((element) => {
      element.scrollLeft = element.scrollWidth;
    });
    expect(await region.evaluate((element) => element.scrollLeft)).toBeGreaterThan(0);
    await region.evaluate((element) => {
      element.scrollLeft = 0;
    });
    await page.screenshot({ path: "/tmp/cumpleia-risk-preview-mobile.png", fullPage: true });
    await page.setViewportSize({ width: 1440, height: 1000 });
    await page.screenshot({ path: "/tmp/cumpleia-risk-preview-desktop.png", fullPage: true });
  }
});
test("documento sin riesgos conserva medidas y datos sin fabricar asociaciones", async ({
  page,
}) => {
  await setup(page, {
    schema_version: 1,
    risks: [],
    measures: [{ measure_id: "M1", description: "[FICTICIA] Medida sin riesgos" }],
  });
  await expect(page.getByRole("table")).toHaveCount(0);
  await page.getByText("Análisis y evidencias por riesgo y medida", { exact: true }).click();
  await expect(page.getByText("[FICTICIA] Medida sin riesgos", { exact: true })).toBeVisible();
});

for (const current of [true, false])
  test(`tabla distingue valoración vigente de histórica: ${current}`, async ({ page }) => {
    await setup(page, value);
    const valuation = {
      revision: 1,
      current,
      analysis: {
        risks: [
          {
            risk_id: "R1",
            harm: "[FICTICIA] Discriminación",
            inherent: { probability: 2, impact: 3 },
            projected: { probability: 1, impact: 3 },
            residual: { probability: null, impact: null },
          },
        ],
        controls: [
          {
            measure_id: "M1",
            dimension: "probabilidad",
            effectiveness: "parcial",
            status: "propuesta",
            rationale: "[FICTICIA] Pendiente verificar",
          },
        ],
      },
      result: {
        risks: [{ risk_id: "R1", inherent: "alto", projected: "medio", residual: "sin_resolver" }],
      },
    };
    await page.evaluate(
      ({ value, valuation }) => {
        document.getElementById("root")!.remove();
        const root = document.createElement("div");
        root.id = "root";
        document.querySelector("main")!.append(root);
        (window as any).renderPreview(value, valuation);
      },
      { value, valuation }
    );
    const first = page.getByRole("table").getByRole("row").nth(1);
    if (current) {
      await expect(first).toContainText("Probabilidad: Media. Impacto: Grave.");
      await expect(first).toContainText("Nivel por riesgo: Alto.");
      await expect(first).toContainText("Residual actual: Sin resolver. Previsto: Medio.");
    } else {
      await expect(first).toContainText("Nivel por riesgo: Sin resolver.");
      await expect(first).not.toContainText("Probabilidad: Media.");
    }
    if (current && process.env.CUMPLEIA_PREVIEW_CSS) {
      await page.setViewportSize({ width: 1440, height: 1000 });
      await page.screenshot({ path: "/tmp/cumpleia-risks-desktop.png", fullPage: true });
    }
  });
