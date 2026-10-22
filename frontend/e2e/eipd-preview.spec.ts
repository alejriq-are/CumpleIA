import { test, expect } from "@playwright/test";
import { browserBundle } from "./helpers/browser-bundle";
import path from "node:path";
let bundle: string;
test.beforeAll(async () => {
  bundle = await browserBundle(
    `import React from "react";import {createRoot} from "react-dom/client";import {EipdDocumentView} from ${JSON.stringify(path.resolve("components/licitud/EipdDocumentFields.tsx"))};window.renderPreview=(value,valuation,annexes)=>createRoot(document.getElementById("root")).render(React.createElement(EipdDocumentView,{value,expanded:true,valuation,annexes}));`
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
async function setup(
  page: import("@playwright/test").Page,
  doc: unknown,
  valuation?: unknown,
  annexes?: unknown
) {
  await page.setContent(
    '<main class="licitud-ui" style="max-width:1200px;margin:auto;padding:16px"><div id="root"></div></main>'
  );
  if (process.env.CUMPLEIA_PREVIEW_CSS)
    await page.addStyleTag({ path: process.env.CUMPLEIA_PREVIEW_CSS });
  await page.addScriptTag({ content: bundle });
  await page.evaluate(
    ({ doc, valuation, annexes }) => (window as any).renderPreview(doc, valuation, annexes),
    { doc, valuation, annexes }
  );
}
test("relaciona riesgos y controles sin asignar niveles ni perder las evidencias", async ({
  page,
}) => {
  await setup(page, value);
  const first = page.getByRole("region", { name: "Detalle del riesgo R1", exact: true }),
    second = page.getByRole("region", { name: "Detalle del riesgo R2", exact: true }),
    third = page.getByRole("region", { name: "Detalle del riesgo R3", exact: true });
  await expect(
    first.getByRole("table", { name: "Controles asociados a R1", exact: true })
  ).toContainText("M1");
  await expect(
    first.getByRole("table", { name: "Controles asociados a R1", exact: true })
  ).toContainText("M2");
  await expect(
    second.getByRole("table", { name: "Controles asociados a R2", exact: true })
  ).toContainText("M2");
  await expect(
    second.getByRole("table", { name: "Controles asociados a R2", exact: true })
  ).not.toContainText("M1");
  await expect(third).toContainText("Sin medidas asociadas a este riesgo");
  await expect(page.getByRole("note")).toContainText("M3");
  await expect(
    first.getByRole("table", { name: "Valoración cualitativa de R1", exact: true })
  ).not.toContainText("Alto");
  await first.getByText("Fundamentos, evidencias y seguimiento de R1", { exact: true }).click();
  await expect(first).toContainText("Residual R1");
  await expect(first.getByText("SIMULADA-EVIDENCIA-R1", { exact: false })).toBeVisible();
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
    name: "Valoración cualitativa de R1; desplazamiento horizontal",
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
    const table = page.getByRole("table", { name: "Valoración cualitativa de R1", exact: true });
    const first = table.getByRole("row").nth(1),
      projected = table.getByRole("row").nth(2),
      actual = table.getByRole("row").nth(3);
    if (current) {
      await expect(first).toContainText("Media");
      await expect(first).toContainText("Grave");
      await expect(first).toContainText("Alto");
      await expect(projected).toContainText("Medio");
      await expect(actual).toContainText("Sin evaluar");
      await expect(actual).not.toContainText("Medio");
      const detail = page.getByRole("region", { name: "Detalle del riesgo R1", exact: true });
      await detail
        .getByText("Fundamentos, evidencias y seguimiento de R1", { exact: true })
        .click();
      await expect(detail).toContainText("[FICTICIA] Pendiente verificar");
    } else {
      await expect(first).toContainText("Pendiente");
      await expect(first).not.toContainText("Media");
      await expect(page.getByText(/Sus niveles no se presentan como actuales/)).toBeVisible();
    }
    if (current && process.env.CUMPLEIA_PREVIEW_CSS) {
      await page.setViewportSize({ width: 1440, height: 1000 });
      await page.screenshot({ path: "/tmp/cumpleia-risks-desktop.png", fullPage: true });
    }
  });

test("detalle muestra fundamentos vigentes, horizonte, seguimiento y anexos sin confundir implementación con verificación", async ({
  page,
}) => {
  const valuation = {
    revision: 4,
    current: true,
    analysis: {
      horizon: "12 meses",
      risks: [
        {
          risk_id: "R1",
          harm: "[FICTICIA] Pérdida de control",
          frequency_context: "[FICTICIA] Acceso frecuente",
          inherent: {
            probability: 2,
            impact: 3,
            rationale: "[FICTICIA] Fundamento inherente vigente",
          },
          projected: { probability: 1, impact: 3, rationale: "[FICTICIA] Previsión condicionada" },
          residual: { probability: null, impact: null, rationale: "" },
          action: "[FICTICIA] Revisar permisos",
          owner_reference: "[FICTICIA] Equipo de ensayo",
          review_on: "2026-11-22",
        },
      ],
      controls: [
        {
          measure_id: "M1",
          dimension: "probabilidad",
          effectiveness: "parcial",
          status: "propuesta",
          rationale: "[FICTICIA] Reducción esperada",
          evidence_references: ["SIMULADA-EVIDENCIA-M1"],
        },
      ],
    },
    result: {
      risks: [{ risk_id: "R1", inherent: "alto", projected: "medio", residual: "sin_resolver" }],
    },
  };
  const annexes = [1, 2].map((version) => ({
    id: `anexo-${version}`,
    reference: "SIMULADA-ANEXO-R1-M1",
    version,
    filename: `permisos-v${version}.txt`,
    description: "[FICTICIA] Propuesta",
    risk_ids: ["R1"],
    measure_ids: ["M1"],
  }));
  await setup(page, value, valuation, annexes);
  const detail = page.getByRole("region", { name: "Detalle del riesgo R1", exact: true });
  await expect(page.getByText("Horizonte temporal:", { exact: true }).locator("..")).toContainText(
    "12 meses"
  );
  await expect(detail).toContainText("[FICTICIA] Acceso frecuente");
  const controls = detail.getByRole("table", { name: "Controles asociados a R1", exact: true });
  await expect(controls).toContainText("Implementación declarada");
  await expect(controls).toContainText("Pendiente");
  await expect(controls).toContainText("Propuesta");
  await detail.getByText("Fundamentos, evidencias y seguimiento de R1", { exact: true }).click();
  for (const fragment of [
    "Fundamento inherente vigente",
    "Previsión condicionada",
    "Reducción esperada",
    "SIMULADA-EVIDENCIA-M1",
    "permisos-v1.txt",
    "permisos-v2.txt",
    "2026-11-22",
    "Equipo de ensayo",
  ]) {
    await expect(detail).toContainText(fragment);
  }
  await expect(detail).toContainText("Análisis inicial del documento");
  await expect(detail).toContainText("Análisis inicial R1");
  await expect(detail).toContainText("Referencias de verificación del control");
  if (process.env.CUMPLEIA_PREVIEW_CSS) {
    await page.setViewportSize({ width: 1440, height: 1000 });
    await page.screenshot({ path: "/tmp/cumpleia-ux-risk-desktop.png", fullPage: true });
    await page.setViewportSize({ width: 390, height: 844 });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(
      true
    );
    await page.screenshot({ path: "/tmp/cumpleia-ux-risk-mobile.png", fullPage: true });
  }
});
