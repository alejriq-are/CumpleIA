import { test, expect, type Page } from "@playwright/test";
import { rm } from "node:fs/promises";
import { buildConnectedHarness } from "./helpers/connected-harness";
const api = process.env.CUMPLEIA_UI_API;
const org = process.env.CUMPLEIA_UI_ORG ?? "";
const tid = process.env.CUMPLEIA_UI_TREATMENT ?? "";
const aid = process.env.CUMPLEIA_UI_ASSESSMENT ?? "";
let directory: string, script: string, css: string;
test.skip(!api, "API aislada explícita requerida");
test.setTimeout(60000);
test.beforeAll(async () => {
  if (!api) return;
  ({ directory, script, css } = await buildConnectedHarness(
    [
      {
        id: org,
        name: "[FICTICIA] Organización aislada",
        role: "owner",
        rut: null,
        size: null,
        industry: null,
      },
    ],
    api
  ));
});
test.afterAll(async () => {
  if (directory) await rm(directory, { recursive: true, force: true });
});
async function mount(page: Page) {
  await page.addStyleTag({ content: css });
  await page.addScriptTag({ content: script });
}
async function section(page: Page, name: string) {
  await page.locator("header").getByRole("button", { name: "Secciones", exact: true }).click();
  await page
    .getByRole("dialog", { name: "Secciones del módulo", exact: true })
    .getByRole("button", { name, exact: true })
    .click();
}

test("navegación real API/PostgreSQL: guardar, recargar y recuperar contexto y documentos", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("dialog", async (d) => d.accept());
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(api + "/__connected-isolated-test");
  await mount(page);
  await page.getByRole("button", { name: "Cambiar contexto", exact: true }).click();
  const context = page.getByRole("dialog", { name: "Contexto de trabajo", exact: true });
  await context.getByLabel("Tratamiento del RAT", { exact: true }).selectOption(tid);
  await expect(
    context.getByLabel("Finalidad de la evaluación", { exact: true }).locator("option")
  ).toHaveCount(2);
  await context
    .getByLabel("Finalidad de la evaluación", { exact: true })
    .selectOption({ index: 1 });
  await context.getByLabel("Evaluación", { exact: true }).selectOption(aid);
  await context.getByRole("button", { name: "Aplicar contexto", exact: true }).click();
  await page.getByRole("button", { name: "Abrir menú", exact: true }).click();
  await page
    .getByRole("navigation", { name: "Módulos de la maqueta" })
    .getByRole("button", { name: "Bases de licitud", exact: true })
    .click();
  const main = page.locator("main.prototype-work");
  await expect(
    main.getByRole("heading", { name: "Determinar aplicabilidad", exact: true })
  ).toBeVisible();
  await main
    .getByLabel("¿Corresponde documentar EIPD?", { exact: true })
    .selectOption("corresponde");
  await main
    .getByLabel("Fundamento sobre EIPD", { exact: true })
    .fill("[FICTICIA] Determinación integrada");
  await main
    .getByLabel("¿Corresponde documentar infancia y adolescencia?", { exact: true })
    .selectOption("corresponde");
  await main
    .getByLabel("Fundamento sobre infancia y adolescencia", { exact: true })
    .fill("[FICTICIA] Alcance con menores");
  await main.getByLabel("Declaro que esta prueba utiliza únicamente datos ficticios.").check();
  await main.getByRole("button", { name: "Guardar determinación", exact: true }).click();
  await expect(
    main.getByText("Determinación guardada en el servidor.", { exact: true })
  ).toBeVisible();
  await section(page, "Base y fundamento");
  await main
    .getByRole("textbox", { name: "Fundamento", exact: true })
    .fill("[FICTICIA] Navegación conectada persistente");
  await main.getByRole("button", { name: "Guardar borrador", exact: true }).click();
  await expect(
    main.getByText(/Borrador guardado. Los cambios se guardaron correctamente/)
  ).toBeVisible();
  await page.reload();
  await mount(page);
  await expect(main.getByRole("textbox", { name: "Fundamento", exact: true })).toHaveValue(
    "[FICTICIA] Navegación conectada persistente"
  );
  await section(page, "Determinar aplicabilidad");
  await expect(main.getByLabel("Fundamento sobre EIPD", { exact: true })).toHaveValue(
    "[FICTICIA] Determinación integrada"
  );
  await section(page, "Completar infancia y adolescencia");
  await expect(main.getByText("Determinar aplicabilidad", { exact: true })).not.toBeVisible();
  expect(errors).toEqual([]);
});
