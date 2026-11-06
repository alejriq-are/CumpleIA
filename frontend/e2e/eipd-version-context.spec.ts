import { test, expect, type Page } from "@playwright/test";
import { browserBundle } from "./helpers/browser-bundle";
import { mkdtemp, readFile, rm } from "node:fs/promises";
import { execFileSync } from "node:child_process";
import { tmpdir } from "node:os";
import path from "node:path";
let script: string, css: string;
const material = {
  schema_version: 1,
  document_type: "eipd_general",
  saved_assessment: {
    rat_context_snapshot: {
      purpose: "[FICTICIA] Gestión de trabajadores adultos.",
      data_categories: [
        { category_code: "contacto", category_name: "Datos de contacto", is_sensitive: false },
      ],
      data_subjects: [
        {
          category_code: "trabajadores",
          category_name: "Trabajadores adultos",
          includes_children: false,
        },
      ],
      retention: {
        retention_rule: "[FICTICIA] 30 días.",
        deletion_method: "[FICTICIA] Borrado al finalizar.",
      },
      systems: [],
      data_sources: [{ source_type: "titular", description: "Formulario simulado" }],
      additional_scope: { reference: "SIMULADA-ADICIONAL" },
    },
    eipd_resolution_assessment: {},
  },
  applicability: { eipd: { state: "corresponde", reason: "[FICTICIA] Determinación conservada." } },
  diagnostic: {
    rule_set: "cumpleia.general.registration.v1",
    readiness: {
      eipd_resolution: {
        result: "incompleto",
        context_current: true,
        issues: Array.from({ length: 120 }, (_, i) => ({
          field: `risks.${i}.impact_analysis`,
          category: "incompleto",
          code: "campo_obligatorio",
        })),
      },
      other_control: { result: "requiere_revision" },
    },
  },
  policy: {
    policy: {
      policy_reference: "SIMULADA-REGLAS",
      global_policy_identity: { policy_reference: "SIMULADA-GENERAL", policy_version: 1 },
    },
  },
  support_records: Array.from({ length: 34 }, (_, i) => ({
    id: `SIMULADO-${i}`,
    kind: i % 2 ? "attachment" : "risk_assessment",
    payload: { reference: `SIMULADA-${i}` },
  })),
};
test.beforeAll(async () => {
  script =
    await browserBundle(`import React from "react";import {createRoot} from "react-dom/client";
    import {EipdVersionContext} from ${JSON.stringify(path.resolve("components/licitud/EipdVersionContext.tsx"))};
    window.renderContext=value=>createRoot(document.getElementById("root")).render(React.createElement(EipdVersionContext,{value}));`);
  const directory = await mkdtemp(path.join(tmpdir(), "cumpleia-context-style-"));
  try {
    const filename = path.join(directory, "style.css");
    execFileSync(
      process.execPath,
      [
        require.resolve("tailwindcss/lib/cli.js"),
        "-i",
        "app/globals.css",
        "--content",
        "components/licitud/**/*.tsx,components/licitud/document-focus.ts",
        "-o",
        filename,
      ],
      { stdio: "pipe" }
    );
    css = await readFile(filename, "utf8");
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
});
async function setup(page: Page, value: unknown = material) {
  await page.setContent(
    '<main class="mx-auto max-w-4xl p-4"><div id="root"></div><label>Fundamento pendiente<textarea id="pending">[FICTICIA] Conservar sin enviar</textarea></label></main>'
  );
  await page.addStyleTag({ content: css });
  await page.addScriptTag({ content: script });
  await page.evaluate((value) => {
    const w = window as any;
    w.original = JSON.stringify(value);
    w.material = value;
    w.calls = 0;
    w.fetch = async () => {
      w.calls++;
      throw new Error("No se permiten solicitudes en esta consulta");
    };
    w.renderContext(value);
  }, value);
  await page
    .getByText("Contexto y antecedentes conservados con la versión", { exact: true })
    .click();
}
test("opening a large record shows only five compact sections and no expanded payload", async ({
  page,
}) => {
  await setup(page);
  const root = page.locator("#root > details");
  await expect(root.locator(":scope > details")).toHaveCount(5);
  expect(await root.locator(":scope > details[open]").count()).toBe(0);
  expect(await root.evaluate((el) => el.getBoundingClientRect().height)).toBeLessThan(850);
  await expect(page.getByText("Plazo o criterio de conservación", { exact: true })).toBeHidden();
  await expect(root.locator("input,textarea,select")).toHaveCount(0);
  await expect(root).not.toContainText("Otro antecedente registrado");
  await page.getByText("Alcance RAT guardado", { exact: true }).click();
  await expect(page.getByText("[FICTICIA] 30 días.", { exact: true })).toBeVisible();
  await expect(page.getByText("[FICTICIA] Borrado al finalizar.", { exact: true })).toBeVisible();
  await expect(page.getByText("Método de eliminación", { exact: true })).toBeVisible();
  await page.getByText("Otros antecedentes del alcance", { exact: true }).click();
  await page.getByText("Additional scope · Abrir detalle", { exact: true }).click();
  await expect(page.getByText("SIMULADA-ADICIONAL", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Cerrar antecedentes y volver a revisiones" }).click();
  await expect(
    page.getByText("Contexto y antecedentes conservados con la versión", { exact: true })
  ).toBeFocused();
  await expect(root).not.toHaveAttribute("open", "");
  expect(await page.evaluate(() => (window as any).calls)).toBe(0);
  expect(
    await page.evaluate(() => JSON.stringify((window as any).material) === (window as any).original)
  ).toBe(true);
  await expect(page.locator("#pending")).toHaveValue("[FICTICIA] Conservar sin enviar");
});
test("diagnostic observations and support records expand by group only", async ({ page }) => {
  await setup(page);
  await page.getByText("Diagnóstico al registrar", { exact: true }).click();
  await expect(page.getByText("120 observaciones documentales", { exact: true })).toBeVisible();
  await expect(
    page.getByText(
      "Riesgos — Elemento 1 — Análisis de impacto: falta completar o fundamentar este dato.",
      { exact: true }
    )
  ).toBeHidden();
  await page.getByText("Riesgos", { exact: true }).click();
  await expect(
    page.getByText(
      "Riesgos — Elemento 1 — Análisis de impacto: falta completar o fundamentar este dato.",
      { exact: true }
    )
  ).toBeVisible();
  await page.getByText("Índice de valoraciones y anexos consultados", { exact: true }).click();
  await expect(page.getByText("Valoración de riesgos", { exact: true }).first()).toBeVisible();
  await expect(page.getByText("Anexo", { exact: true }).first()).toBeVisible();
  await expect(page.getByText("SIMULADA-0", { exact: true })).toBeHidden();
});
for (const width of [1280, 320]) {
  test("keyboard, compact height and no horizontal overflow at " + width, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    await setup(page);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(
      true
    );
    await page.screenshot({ path: `/tmp/cumpleia-5c-context-${width}.png`, fullPage: true });
    const summary = page
      .locator("summary")
      .filter({ has: page.getByText("Alcance RAT guardado", { exact: true }) });
    await summary.focus();
    await page.keyboard.press("Enter");
    await expect(page.getByText("[FICTICIA] 30 días.", { exact: true })).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(
      true
    );
    await page.screenshot({ path: `/tmp/cumpleia-5c-context-rat-${width}.png`, fullPage: true });
    await page.getByRole("button", { name: "Cerrar antecedentes y volver a revisiones" }).focus();
    await page.keyboard.press("Enter");
    await expect(
      page.getByText("Contexto y antecedentes conservados con la versión", { exact: true })
    ).toBeFocused();
  });
}
test("missing historical diagnosis is described without inventing completeness", async ({
  page,
}) => {
  await setup(page, { ...material, diagnostic: {}, support_records: [] });
  await expect(
    page.getByText("No hay un resultado documental EIPD conservado", { exact: true })
  ).toBeVisible();
  await page.getByText("Índice de valoraciones y anexos consultados", { exact: true }).click();
  await expect(page.getByText("Sin elementos conservados.", { exact: true }).last()).toBeVisible();
});
