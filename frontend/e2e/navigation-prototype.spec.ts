import { test, expect, type Page } from "@playwright/test";
import { mkdtemp, readFile, writeFile, rm } from "node:fs/promises";
import { execFileSync } from "node:child_process";
import { tmpdir } from "node:os";
import path from "node:path";
import {
  moduleNavigation,
  groupDestinations,
  type Destination,
} from "../components/navigation/prototype-navigation";
import {
  labels,
  steps,
  type ModuleId,
  type TaskId,
  type Scenario,
} from "../components/navigation/prototype-data";

let directory: string;
let script: string;
let css: string;
const requests: string[] = [];
test.setTimeout(30000);
test.beforeAll(async () => {
  directory = await mkdtemp(path.join(tmpdir(), "cumpleia-navigation-"));
  const loader = path.join(directory, "loader.cjs");
  await writeFile(
    loader,
    `const ts=require(${JSON.stringify(require.resolve("typescript"))}); module.exports=source=>ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.ESNext,target:ts.ScriptTarget.ES2021,jsx:ts.JsxEmit.ReactJSX}}).outputText;`
  );
  const entry = path.join(directory, "entry.js");
  await writeFile(
    entry,
    `import React from "react";import {createRoot} from "react-dom/client";import {NavigationPrototype} from ${JSON.stringify(path.resolve("components/navigation/NavigationPrototype.tsx"))};createRoot(document.getElementById("root")).render(React.createElement(NavigationPrototype));`
  );
  const runtime = require("next/dist/compiled/webpack/webpack");
  runtime.init();
  await new Promise<void>((resolve, reject) =>
    runtime.webpack(
      {
        mode: "development",
        devtool: false,
        entry,
        output: { path: directory, filename: "bundle.js" },
        resolve: {
          extensions: [".ts", ".tsx", ".js"],
          modules: [path.resolve("node_modules"), "node_modules"],
        },
        module: { rules: [{ test: /\.tsx?$/, use: loader }] },
      },
      (error: Error | null, stats: { hasErrors: () => boolean; toString: () => string }) => {
        if (error || stats.hasErrors()) reject(error ?? new Error(stats.toString()));
        else resolve();
      }
    )
  );
  script = await readFile(path.join(directory, "bundle.js"), "utf8");
  const source = path.join(directory, "tailwind.css");
  await writeFile(source, "@tailwind base; @tailwind components; @tailwind utilities;");
  execFileSync(
    process.execPath,
    [
      require.resolve("tailwindcss/lib/cli.js"),
      "-i",
      source,
      "-o",
      path.join(directory, "style.css"),
      "--content",
      path.resolve("components/navigation/*.tsx"),
    ],
    { stdio: "pipe" }
  );
  css = await readFile(path.join(directory, "style.css"), "utf8");
});
test.afterAll(async () => {
  if (directory) await rm(directory, { recursive: true, force: true });
});
async function open(page: Page) {
  requests.length = 0;
  await page.route("**/*", async (route) => {
    if (
      route.request().isNavigationRequest() &&
      route.request().url().startsWith("http://prototype.invalid/")
    ) {
      await route.fulfill({
        contentType: "text/html",
        body: '<main style="max-width:1152px;margin:auto;padding:24px"><div id="root"></div></main>',
      });
    } else {
      requests.push(`${route.request().method()} ${route.request().url()}`);
      await route.abort();
    }
  });
  await page.goto("http://prototype.invalid/dashboard/maqueta");
  await page.addStyleTag({ content: css });
  await page.addScriptTag({ content: script });
  await expect(page.getByRole("heading", { name: "Maqueta integral", exact: true })).toBeVisible();
}
const moduleNav = (page: Page) => page.getByRole("navigation", { name: "Módulos de la maqueta" });
const optionsNav = (page: Page) => page.getByRole("navigation", { name: "Opciones del módulo" });
const work = (page: Page) => page.locator("#prototype-content");
const moduleNames: Record<string, ModuleId> = {
  "Panel principal": "panel",
  Diagnóstico: "diagnostico",
  "Inventario RAT": "rat",
  "Bases de licitud": "licitud",
  Documentos: "documentos",
  Evidencia: "evidencia",
  Organización: "organizacion",
};
const visibleNames: Record<ModuleId, string> = {
  panel: "Inicio / Panel principal",
  diagnostico: "Autodiagnóstico",
  rat: "Inventario de tratamientos",
  licitud: "Bases de licitud",
  documentos: "Políticas y referencias normativas",
  evidencia: "Carpeta de evidencias",
  organizacion: "Mi organización",
};
async function currentModule(page: Page): Promise<ModuleId> {
  const current = await page
    .locator("#prototype-global-menu")
    .locator('button[aria-current="page"]')
    .textContent();
  return (Object.entries(visibleNames).find(([, name]) => current?.includes(name))?.[0] ??
    "panel") as ModuleId;
}
async function module(page: Page, name: string) {
  const toggle = page.getByRole("button", { name: "Abrir menú", exact: true });
  if (await toggle.isVisible()) await toggle.click();
  await moduleNav(page)
    .getByRole("button", { name: visibleNames[moduleNames[name]], exact: true })
    .click();
}
async function navigate(page: Page, destination: Destination) {
  const scenario = (
    (await page.getByLabel("Tratamiento del RAT").count())
      ? await page.getByLabel("Tratamiento del RAT").inputValue()
      : "adultos"
  ) as Scenario;
  const group = moduleNavigation(destination.module, scenario).find((group) =>
    groupDestinations(group, scenario).some(
      (item) => item.task === destination.task && item.section === destination.section
    )
  )!;
  const mobile = page.getByRole("button", { name: "Opciones del módulo", exact: true });
  if ((await mobile.isVisible()) && (await mobile.getAttribute("aria-expanded")) === "false")
    await mobile.click();
  const opener = optionsNav(page).locator(`[data-nav-group="${group.id}"]`);
  if (groupDestinations(group, scenario).length === 1) await opener.click();
  else {
    if ((await opener.getAttribute("aria-expanded")) !== "true") await opener.click();
    const index = groupDestinations(group, scenario).findIndex(
      (item) => item.section === destination.section && item.task === destination.task
    );
    await page.locator(`[data-group="${group.id}"]`).getByRole("button").nth(index).click();
  }
}
async function task(page: Page, name: string) {
  const mod = await currentModule(page);
  const scenario = (
    (await page.getByLabel("Tratamiento del RAT").count())
      ? await page.getByLabel("Tratamiento del RAT").inputValue()
      : "adultos"
  ) as Scenario;
  const tasks: Record<string, TaskId> = {
    Resumen: "resumen",
    "Completar datos": "completar",
    "Documentos y revisiones": "revisar",
    "Historial y descargas": "historial",
  };
  const t = tasks[name];
  await navigate(page, { module: mod, task: t, section: steps(mod, t, scenario)[0] });
}
async function step(page: Page, name: string) {
  const mod = await currentModule(page);
  const scenario = (
    (await page.getByLabel("Tratamiento del RAT").count())
      ? await page.getByLabel("Tratamiento del RAT").inputValue()
      : "adultos"
  ) as Scenario;
  const destination = moduleNavigation(mod, scenario)
    .flatMap((group) => groupDestinations(group, scenario))
    .find((item) => labels[item.section]?.includes(name))!;
  if (!destination) throw new Error(`Destino ausente: ${name}`);
  await navigate(page, destination);
}
async function children(page: Page) {
  await module(page, "Bases de licitud");
  await page.getByLabel("Tratamiento del RAT").selectOption("infancia");
}

test("todos los módulos y destinos abren contenido con foco, sin red ni capas genéricas", async ({
  page,
}) => {
  await open(page);
  for (const name of ["Diagnóstico", "Inventario RAT", "Bases de licitud", "Organización"]) {
    await module(page, name);
    const mod = moduleNames[name];
    for (const group of moduleNavigation(mod, "adultos")) {
      for (const destination of groupDestinations(group, "adultos")) {
        await navigate(page, destination);
        await expect(work(page)).toBeFocused();
        await expect(work(page).locator("#prototype-section-title")).toHaveText(
          labels[destination.section]
        );
        await expect(optionsNav(page).locator("[data-group]")).toHaveCount(0);
      }
    }
  }
  await module(page, "Panel principal");
  await expect(page.getByRole("heading", { name: "Continúa donde lo dejaste" })).toBeVisible();
  await expect(page.getByRole("navigation", { name: "Tareas del módulo" })).toHaveCount(0);
  expect(requests).toEqual([]);
});

test("borradores conservados entre módulos, escenarios separados y consulta solo guardada", async ({
  page,
}) => {
  await open(page);
  await module(page, "Bases de licitud");
  await task(page, "Completar datos");
  await step(page, "Base y fundamento");
  const value = "[FICTICIA] FUNDAMENTO EDITADO ADULTOS";
  await page.getByLabel("Fundamento", { exact: true }).fill(value);
  await module(page, "Inventario RAT");
  await module(page, "Bases de licitud");
  await task(page, "Completar datos");
  await step(page, "Base y fundamento");
  await expect(page.getByLabel("Fundamento", { exact: true })).toHaveValue(value);
  await task(page, "Documentos y revisiones");
  await expect(work(page).getByText(value, { exact: true })).toHaveCount(0);
  await task(page, "Completar datos");
  await step(page, "Base y fundamento");
  await page.getByRole("button", { name: "Guardar cambios en la maqueta", exact: true }).click();
  await expect(page.getByRole("status")).toContainText("Guardado en la maqueta");
  const feedbackBounds = await page.getByRole("status").boundingBox();
  const fieldBounds = await page.getByLabel("Fundamento", { exact: true }).boundingBox();
  const saveBounds = await page
    .getByRole("button", { name: "Guardar cambios en la maqueta", exact: true })
    .boundingBox();
  expect(feedbackBounds!.y).toBeGreaterThanOrEqual(fieldBounds!.y + fieldBounds!.height);
  expect(feedbackBounds!.y + feedbackBounds!.height).toBeLessThanOrEqual(saveBounds!.y);
  if (process.env.MAQUETA_SCREENSHOTS) {
    await page.screenshot({
      path: path.join(process.env.MAQUETA_SCREENSHOTS, "maqueta-confirmacion-sobre-guardar.png"),
      fullPage: true,
    });
  }

  await task(page, "Documentos y revisiones");
  await expect(work(page).getByText(value, { exact: true })).toBeVisible();
  await page.getByLabel("Tratamiento del RAT").selectOption("infancia");
  await task(page, "Completar datos");
  await step(page, "Base y fundamento");
  await expect(page.getByLabel("Fundamento", { exact: true })).not.toHaveValue(value);
  await expect(optionsNav(page).locator('[data-nav-group="infancia"]')).toBeVisible();
  await page.getByLabel("Tratamiento del RAT").selectOption("adultos");
  await expect(optionsNav(page).locator('[data-nav-group="infancia"]')).toHaveCount(0);
});

test("cancelar copia conserva marca temporal y confirmar copia preserva original", async ({
  page,
}) => {
  await open(page);
  await children(page);
  await task(page, "Completar datos");
  await step(page, "Preparar resolución");
  await page
    .getByLabel("Notas de la resolución en preparación")
    .fill("[FICTICIA] MARCA PARA CONSERVAR");
  await task(page, "Documentos y revisiones");
  await step(page, "Resoluciones");
  await page.getByRole("button", { name: /Preparar sucesor desde/ }).click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await page
    .getByRole("button", { name: "Conservar documento en preparación", exact: true })
    .click();
  await task(page, "Completar datos");
  await step(page, "Preparar resolución");
  await expect(page.getByLabel("Notas de la resolución en preparación")).toHaveValue(
    "[FICTICIA] MARCA PARA CONSERVAR"
  );
  await task(page, "Documentos y revisiones");
  await step(page, "Resoluciones");
  await page.getByRole("button", { name: /Preparar sucesor desde/ }).click();
  await page.getByRole("button", { name: "Reemplazar y copiar a preparación" }).click();
  await expect(page.getByLabel("Referencia de la nueva resolución")).toHaveValue(
    "SIMULADA-MAQUETA-RES-002-COPIA"
  );
  await page
    .getByLabel("Notas de la resolución en preparación")
    .fill("[FICTICIA] SUCESOR MODIFICADO");
  await page.getByLabel("Motivo del cambio").fill("Prueba ficticia de versión");
  await page.getByRole("checkbox").check();
  await page.getByRole("button", { name: /Abrir vista previa de la resolución/ }).click();
  await expect(page.getByRole("dialog")).toContainText("Todavía no se creó otra resolución");
  await page.getByRole("button", { name: /Continuar al registro de ejemplo/ }).click();
  await page.getByRole("button", { name: "Registrar resolución solo en maqueta" }).click();
  await expect(page.getByText(/^Cambios sin guardar ·/)).toHaveCount(0);
  await expect(
    page.getByRole("button", { name: "Consultar resolución 3", exact: true })
  ).toBeVisible();
  await page.getByRole("button", { name: "Consultar resolución 2", exact: true }).click();
  await expect(work(page).getByText("[FICTICIA] SUCESOR MODIFICADO", { exact: true })).toHaveCount(
    0
  );
  await expect(work(page)).toContainText("Segundo documento del ejemplo");
  await step(page, "Decisiones de la organización");
  await expect(
    page.getByRole("button", { name: "Registrar decisión de organización", exact: true })
  ).toBeDisabled();
  await expect(work(page)).toContainText("facultad de la persona de ejemplo está revocada");
  expect(requests).toEqual([]);
});

test("anexo inválido bloquea guardado, conserva campos y corrige selección", async ({ page }) => {
  await open(page);
  await module(page, "Bases de licitud");
  await task(page, "Completar datos");
  await step(page, "Anexos de respaldo");
  await page.getByLabel("Referencia del anexo de ejemplo").fill("SIMULADA-ANEXO-PRUEBA");
  await page.getByLabel("Descripción del respaldo").fill("[FICTICIA] Respaldo de prueba");
  await page.getByRole("checkbox").check();
  const file = page.getByLabel("Archivo PDF o TXT de ejemplo");
  await file.setInputFiles({
    name: "prueba.csv",
    mimeType: "text/csv",
    buffer: Buffer.from("ficticio"),
  });
  await expect(page.getByRole("alert")).toHaveText("Formato no admitido. Selecciona PDF o TXT.");
  await expect(
    page.getByRole("button", { name: "Guardar cambios en la maqueta", exact: true })
  ).toBeDisabled();
  await expect(page.getByLabel("Referencia del anexo de ejemplo")).toHaveValue(
    "SIMULADA-ANEXO-PRUEBA"
  );
  await file.setInputFiles({ name: "vacio.txt", mimeType: "text/plain", buffer: Buffer.alloc(0) });
  await expect(page.getByRole("alert")).toHaveText("El archivo está vacío.");
  await file.setInputFiles({
    name: "grande.txt",
    mimeType: "text/plain",
    buffer: Buffer.alloc(2 * 1024 * 1024 + 1),
  });
  await expect(page.getByRole("alert")).toHaveText("El archivo supera 2 MiB.");
  await file.setInputFiles({
    name: "valido.txt",
    mimeType: "text/plain",
    buffer: Buffer.from("[FICTICIA] Contenido"),
  });
  await expect(page.getByRole("alert")).toHaveCount(0);
  await page.getByRole("button", { name: "Guardar cambios en la maqueta", exact: true }).click();
  await task(page, "Documentos y revisiones");
  await expect(work(page)).toContainText("SIMULADA-ANEXO-PRUEBA · Base y fundamento · valido.txt");
  await page.getByRole("button", { name: "Reiniciar ejemplos", exact: true }).click();
  await page.getByRole("button", { name: "Reiniciar maqueta", exact: true }).click();
  await module(page, "Bases de licitud");
  await task(page, "Documentos y revisiones");
  await expect(work(page)).toContainText("Sin anexos añadidos durante esta visita.");
  await expect(work(page)).not.toContainText("SIMULADA-ANEXO-PRUEBA");
});

test("panel de detalle, Escape y restauración de foco", async ({ page }) => {
  await open(page);
  await module(page, "Bases de licitud");
  await task(page, "Documentos y revisiones");
  const opener = page.getByRole("button", { name: /Abrir detalle del alcance/ });
  await opener.click();
  await expect(page.getByRole("dialog", { name: "Alcance RAT del ejemplo" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Cerrar", exact: true })).toBeFocused();
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await expect(opener).toBeFocused();
});

test("descarga solo datos guardados y recarga reinicia el ejemplo", async ({ page }) => {
  await open(page);
  await module(page, "Bases de licitud");
  await task(page, "Completar datos");
  await step(page, "Base y fundamento");
  await page.getByLabel("Fundamento", { exact: true }).fill("[FICTICIA] GUARDADO");
  await page.getByRole("button", { name: "Guardar cambios en la maqueta", exact: true }).click();
  await page.getByLabel("Fundamento", { exact: true }).fill("[FICTICIA] PENDIENTE");
  await task(page, "Historial y descargas");
  await step(page, "Descargas");
  const pending = page.waitForEvent("download");
  await page.getByRole("button", { name: /Descargar JSON de demostración/ }).click();
  const download = await pending;
  const file = await download.path();
  const packet = JSON.parse(await readFile(file!, "utf8"));
  expect(packet.values["base.fundamento"]).toBe("[FICTICIA] GUARDADO");
  expect(packet.can_confirm).toBe(false);
  expect(packet.resolutions).toEqual([]);
  await open(page);
  await module(page, "Bases de licitud");
  await task(page, "Completar datos");
  await step(page, "Base y fundamento");
  await expect(page.getByLabel("Fundamento", { exact: true })).not.toHaveValue(
    "[FICTICIA] GUARDADO"
  );
});

test("reinicio pide confirmación y permite conservar visita", async ({ page }) => {
  await open(page);
  await page.getByRole("button", { name: "Reiniciar ejemplos", exact: true }).click();
  await page.getByRole("button", { name: "Conservar esta visita", exact: true }).click();
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await children(page);
  await task(page, "Completar datos");
  await step(page, "Infancia y adolescencia");
  await page.getByLabel("Notas de infancia").fill("[FICTICIA] CAMBIO");
  await page.getByRole("button", { name: "Reiniciar ejemplos", exact: true }).click();
  await page.getByRole("button", { name: "Reiniciar maqueta", exact: true }).click();
  await expect(page.getByRole("status")).toContainText("Ejemplos reiniciados");
  await module(page, "Bases de licitud");
  await task(page, "Completar datos");
  await step(page, "Infancia y adolescencia");
  await expect(page.getByLabel("Notas de infancia")).not.toHaveValue("[FICTICIA] CAMBIO");
});

test("móvil sin desborde, menús desplegables y diálogo utilizable", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await open(page);
  await children(page);
  await task(page, "Completar datos");
  await step(page, "Preparar resolución");
  await expect(page.getByLabel("Motivo del cambio")).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(
    true
  );
  await task(page, "Documentos y revisiones");
  await page.getByRole("button", { name: /Abrir detalle del alcance/ }).click();
  await expect(page.getByRole("dialog")).toBeVisible();
  expect(
    await page
      .getByRole("dialog")
      .evaluate((el) => el.getBoundingClientRect().width <= window.innerWidth)
  ).toBe(true);
  await page.getByRole("button", { name: "Cerrar", exact: true }).click();
  await page.setViewportSize({ width: 320, height: 740 });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(
    true
  );
});

test("infancia guardada se consulta y el estado vuelve a pendiente al editar", async ({ page }) => {
  await open(page);
  await children(page);
  await task(page, "Completar datos");
  await step(page, "Infancia y adolescencia");
  await page
    .getByLabel("Notas de infancia", { exact: true })
    .fill("[FICTICIA] NOTA GUARDADA DE INFANCIA");
  await expect(optionsNav(page).locator('[data-nav-group="infancia"]')).toContainText(
    "Cambios sin guardar"
  );
  await page.getByRole("button", { name: "Guardar cambios en la maqueta", exact: true }).click();
  await expect(optionsNav(page).locator('[data-nav-group="infancia"]')).toContainText(
    "Guardado en maqueta"
  );
  await page.getByLabel("Notas de infancia", { exact: true }).fill("[FICTICIA] NOTA SIN GUARDAR");
  await expect(optionsNav(page).locator('[data-nav-group="infancia"]')).toContainText(
    "Cambios sin guardar"
  );
  await task(page, "Documentos y revisiones");
  await expect(work(page)).toContainText("[FICTICIA] NOTA GUARDADA DE INFANCIA");
  await expect(work(page).getByText("[FICTICIA] NOTA SIN GUARDAR", { exact: true })).toHaveCount(0);
});

test("capturas de escritorio y móvil para revisión visual", async ({ page }) => {
  test.skip(!process.env.MAQUETA_SCREENSHOTS, "Captura visual opcional");
  const dir = process.env.MAQUETA_SCREENSHOTS!;
  await page.setViewportSize({ width: 1440, height: 1100 });
  await open(page);
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.evaluate(() => new Promise(requestAnimationFrame));
  await page.screenshot({ path: path.join(dir, "maqueta-panel-desktop.png"), fullPage: true });
  await module(page, "Bases de licitud");
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({
    path: path.join(dir, "maqueta-seleccion-finalidad-desktop.png"),
    fullPage: true,
  });
  await children(page);
  await task(page, "Completar datos");
  await step(page, "Infancia y adolescencia");
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.evaluate(() => new Promise(requestAnimationFrame));
  await page.screenshot({ path: path.join(dir, "maqueta-infancia-desktop.png"), fullPage: true });
  await optionsNav(page).locator('[data-nav-group="eipd"]').click();
  await page.screenshot({ path: path.join(dir, "maqueta-menu-eipd-desktop.png"), fullPage: false });
  await page.keyboard.press("Escape");
  await optionsNav(page).locator('[data-nav-group="resoluciones"]').click();
  await page.screenshot({
    path: path.join(dir, "maqueta-menu-resoluciones-desktop.png"),
    fullPage: false,
  });
  await page.keyboard.press("Escape");
  await module(page, "Inventario RAT");
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({ path: path.join(dir, "maqueta-rat-desktop.png"), fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  await module(page, "Panel principal");
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.evaluate(() => new Promise(requestAnimationFrame));
  await page.screenshot({ path: path.join(dir, "maqueta-panel-mobile.png"), fullPage: true });
  await module(page, "Bases de licitud");
  await task(page, "Completar datos");
  await step(page, "Infancia y adolescencia");
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.evaluate(() => new Promise(requestAnimationFrame));
  await page.screenshot({ path: path.join(dir, "maqueta-infancia-mobile.png"), fullPage: true });
  await page.setViewportSize({ width: 1440, height: 1100 });
  await module(page, "Organización");
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({
    path: path.join(dir, "maqueta-organizacion-desktop.png"),
    fullPage: true,
  });
});

test("menú EIPD abre por clic, permanece visible y cierra con Escape, selección o clic exterior", async ({
  page,
}) => {
  await open(page);
  await module(page, "Bases de licitud");
  const trigger = optionsNav(page).getByRole("button", { name: "Documentar EIPD", exact: false });
  await trigger.hover();
  await expect(trigger).toHaveAttribute("aria-expanded", "false");
  await trigger.click();
  await expect(trigger).toHaveAttribute("aria-expanded", "true");
  await page.mouse.move(1, 1);
  await expect(page.locator('[data-group="eipd"]')).toBeVisible();
  await expect(page.locator('[data-group="eipd"]').getByRole("button")).toHaveCount(5);
  await page.keyboard.press("Escape");
  await expect(trigger).toBeFocused();
  await expect(trigger).toHaveAttribute("aria-expanded", "false");
  await trigger.press("ArrowDown");
  await expect(page.locator('[data-group="eipd"]').getByRole("button").first()).toBeFocused();
  await page.keyboard.press("End");
  await expect(page.locator('[data-group="eipd"]').getByRole("button").last()).toBeFocused();
  await page.keyboard.press("Home");
  await page.keyboard.press("ArrowDown");
  await page.keyboard.press("Enter");
  await expect(work(page)).toBeFocused();
  await expect(page.locator("#prototype-section-title")).toHaveText("Necesidad y proporcionalidad");
  await page
    .getByRole("textbox", { name: "Necesidad y proporcionalidad", exact: true })
    .fill("[FICTICIA] JUSTIFICACIÓN CONSERVADA");
  await trigger.click();
  await work(page).click();
  await expect(trigger).toHaveAttribute("aria-expanded", "false");
  await step(page, "Riesgos y valoración");
  await step(page, "Necesidad y proporcionalidad");
  await expect(
    page.getByRole("textbox", { name: "Necesidad y proporcionalidad", exact: true })
  ).toHaveValue("[FICTICIA] JUSTIFICACIÓN CONSERVADA");
});

test("preparar resolución se encuentra desde su menú sin pasar por Completar datos", async ({
  page,
}) => {
  await open(page);
  await children(page);
  const trigger = optionsNav(page).getByRole("button", { name: /Resoluciones y revisiones/ });
  await expect(trigger).toBeVisible();
  await trigger.click();
  await page
    .locator('[data-group="resoluciones"]')
    .getByRole("button", { name: /Preparar resolución documental/ })
    .click();
  await expect(page.locator("#prototype-section-title")).toHaveText(
    "Preparar resolución documental"
  );
  await expect(page.getByLabel("Referencia de la nueva resolución")).toBeVisible();
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await expect(moduleNav(page).locator('button[aria-current="page"]')).toContainText(
    "Bases de licitud"
  );
  await expect(optionsNav(page).locator('[data-nav-group="resoluciones"]')).toHaveClass(
    /border-orange-600/
  );
});

test("menús completos sin desborde en escritorio, tableta y móvil", async ({ page }) => {
  await open(page);
  for (const width of [1440, 1024, 768, 640, 390, 320]) {
    await page.setViewportSize({ width, height: 900 });
    await children(page);
    const mobile = page.getByRole("button", { name: "Opciones del módulo", exact: true });
    if (await mobile.isVisible()) await mobile.click();
    for (const id of ["eipd", "resoluciones", "historial"]) {
      const trigger = optionsNav(page).locator(`[data-nav-group="${id}"]`);
      await trigger.click();
      const bounds = await page.locator(`[data-group="${id}"]`).boundingBox();
      expect(bounds!.x).toBeGreaterThanOrEqual(0);
      expect(bounds!.x + bounds!.width).toBeLessThanOrEqual(width);
      expect(
        await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)
      ).toBe(true);
      await page.keyboard.press("Escape");
    }
  }
});

test("Mi organización reproduce los cuatro datos y los módulos futuros indican Próximamente", async ({
  page,
}) => {
  await open(page);
  for (const title of ["Políticas y referencias normativas", "Carpeta de evidencias"]) {
    await expect(
      moduleNav(page).getByRole("button", { name: new RegExp(`^${title}`) })
    ).toBeDisabled();
    await expect(
      moduleNav(page).getByRole("button", { name: new RegExp(`^${title}`) })
    ).toContainText("Próximamente");
    await expect(work(page).getByRole("button", { name: new RegExp(`^${title}`) })).toBeDisabled();
    await expect(work(page).getByRole("button", { name: new RegExp(`^${title}`) })).toContainText(
      "Próximamente"
    );
  }
  await module(page, "Organización");
  await expect(page.locator("#prototype-section-title")).toHaveText("Datos de la organización");
  await expect(
    page.getByRole("textbox", { name: "Nombre de la organización", exact: true })
  ).toHaveValue("CumpleIA Demo");
  await expect(page.getByRole("textbox", { name: "RUT", exact: true })).toHaveValue("1111111-0");
  await expect(page.getByRole("textbox", { name: "Rubro / industria", exact: true })).toHaveValue(
    "Consultoría"
  );
  await expect(page.getByLabel("Tamaño", { exact: true })).toHaveValue("Pequeña empresa (PYME)");
  await expect(page.getByLabel("Tamaño").locator("option")).toHaveCount(5);
  await expect(page.getByLabel("Tratamiento del RAT")).toHaveCount(0);
  await page
    .getByRole("textbox", { name: "Rubro / industria", exact: true })
    .fill("[FICTICIA] Servicios");
  await page.getByRole("button", { name: "Guardar cambios", exact: true }).click();
  await expect(page.getByRole("status")).toContainText("Guardado en la maqueta");
  await module(page, "Bases de licitud");
  await page.getByLabel("Tratamiento del RAT").selectOption("infancia");
  await expect(optionsNav(page).locator('[data-nav-group="consultas"]')).toBeEnabled();
  await module(page, "Organización");
  await expect(page.getByRole("textbox", { name: "Rubro / industria", exact: true })).toHaveValue(
    "[FICTICIA] Servicios"
  );
  expect(requests).toEqual([]);
});

test("tratamiento, finalidad y evaluación filtran opciones y conservan borradores separados", async ({
  page,
}) => {
  await open(page);
  await module(page, "Bases de licitud");
  await expect(page.getByLabel("Finalidad de la evaluación").locator("option")).toHaveCount(2);
  await expect(page.getByLabel("Evaluación", { exact: true }).locator("option")).toHaveCount(2);
  await step(page, "Base y fundamento");
  await page.getByLabel("Fundamento", { exact: true }).fill("[FICTICIA] CITAS V1 GUARDADO");
  await page.getByRole("button", { name: "Guardar cambios en la maqueta", exact: true }).click();
  await page.getByLabel("Fundamento", { exact: true }).fill("[FICTICIA] CITAS V1 PENDIENTE");
  await page.getByLabel("Evaluación", { exact: true }).selectOption("adultos-citas-v2");
  await expect(page.getByLabel("Fundamento", { exact: true })).not.toHaveValue(/CITAS V1/);
  await page.getByLabel("Fundamento", { exact: true }).fill("[FICTICIA] CITAS V2 PENDIENTE");
  await page.getByLabel("Finalidad de la evaluación").selectOption("comercial");
  await expect(page.getByLabel("Evaluación", { exact: true })).toHaveValue("adultos-comercial");
  await expect(page.getByLabel("Evaluación", { exact: true }).locator("option")).toHaveCount(1);
  await expect(page.getByLabel("Fundamento", { exact: true })).not.toHaveValue(/CITAS/);
  await page.getByLabel("Fundamento", { exact: true }).fill("[FICTICIA] COMERCIAL GUARDADO");
  await page.getByRole("button", { name: "Guardar cambios en la maqueta", exact: true }).click();
  await page.getByLabel("Finalidad de la evaluación").selectOption("citas");
  await expect(page.getByLabel("Fundamento", { exact: true })).toHaveValue(
    "[FICTICIA] CITAS V1 PENDIENTE"
  );
  await task(page, "Documentos y revisiones");
  await expect(work(page)).toContainText("[FICTICIA] CITAS V1 GUARDADO");
  await expect(work(page)).not.toContainText("[FICTICIA] COMERCIAL GUARDADO");
  await expect(work(page)).not.toContainText("[FICTICIA] CITAS V1 PENDIENTE");
  await page.getByLabel("Evaluación", { exact: true }).selectOption("adultos-citas-v2");
  await step(page, "Base y fundamento");
  await expect(page.getByLabel("Fundamento", { exact: true })).toHaveValue(
    "[FICTICIA] CITAS V2 PENDIENTE"
  );
  await module(page, "Inventario RAT");
  await expect(page.getByLabel("Evaluación", { exact: true })).toHaveValue("adultos-citas-v2");
  await page.getByLabel("Tratamiento del RAT").selectOption("infancia");
  await expect(page.getByLabel("Finalidad de la evaluación")).toHaveValue("programa");
  await expect(page.getByLabel("Finalidad de la evaluación").locator("option")).toHaveCount(1);
  await expect(page.getByLabel("Evaluación", { exact: true })).toHaveValue("infancia");
  await module(page, "Bases de licitud");
  await expect(optionsNav(page).locator('[data-nav-group="infancia"]')).toBeVisible();
  expect(requests).toEqual([]);
});

test("anexos, actividad y JSON corresponden a la finalidad y evaluación seleccionadas", async ({
  page,
}) => {
  await open(page);
  await module(page, "Bases de licitud");
  await step(page, "Anexos de respaldo");
  await page.getByLabel("Referencia del anexo de ejemplo").fill("SIMULADA-SOLO-CITAS-V1");
  await page.getByLabel("Descripción del respaldo").fill("[FICTICIA] Solo citas v1");
  await page.getByRole("checkbox").check();
  await page.getByLabel("Archivo PDF o TXT de ejemplo").setInputFiles({
    name: "citas.txt",
    mimeType: "text/plain",
    buffer: Buffer.from("[FICTICIA]"),
  });
  await page.getByRole("button", { name: "Guardar cambios en la maqueta", exact: true }).click();
  await page.getByLabel("Finalidad de la evaluación").selectOption("comercial");
  await task(page, "Documentos y revisiones");
  await expect(work(page)).not.toContainText("SIMULADA-SOLO-CITAS-V1");
  await task(page, "Historial y descargas");
  await step(page, "Actividad del ejemplo");
  await expect(work(page)).toContainText("Aún no hay actividad nueva");
  await step(page, "Descargas");
  const pending = page.waitForEvent("download");
  await page.getByRole("button", { name: /Descargar JSON de demostración/ }).click();
  const download = await pending;
  const packet = JSON.parse(await readFile((await download.path())!, "utf8"));
  expect(packet.purposeId).toBe("comercial");
  expect(packet.evaluation.id).toBe("adultos-comercial");
  expect(packet.evaluation.version).toBe(1);
  expect(packet.annexes).toEqual([]);
  expect(packet.can_confirm).toBe(false);
  await page.getByLabel("Finalidad de la evaluación").selectOption("citas");
  await task(page, "Documentos y revisiones");
  await expect(work(page)).toContainText("SIMULADA-SOLO-CITAS-V1");
});

test("registrar resolución consume su preparación y conserva otros cambios pendientes", async ({
  page,
}) => {
  await open(page);
  await children(page);
  await step(page, "Infancia y adolescencia");
  await page
    .getByLabel("Notas de infancia", { exact: true })
    .fill("[FICTICIA] INFANCIA SIGUE PENDIENTE");
  await step(page, "Preparar resolución");
  await page.getByLabel("Motivo del cambio").fill("[FICTICIA] Ensayo de registro independiente");
  await page.getByRole("checkbox").check();
  await page.getByRole("button", { name: /Abrir vista previa de la resolución/ }).click();
  await page.getByRole("button", { name: /Continuar al registro de ejemplo/ }).click();
  await page.getByRole("button", { name: "Registrar resolución solo en maqueta" }).click();
  await expect(
    page.getByRole("button", { name: "Consultar resolución 3", exact: true })
  ).toBeVisible();
  await expect(page.getByText(/^Cambios sin guardar ·/)).toBeVisible();
  await task(page, "Documentos y revisiones");
  await expect(work(page)).not.toContainText("[FICTICIA] INFANCIA SIGUE PENDIENTE");
  await step(page, "Infancia y adolescencia");
  await expect(page.getByLabel("Notas de infancia", { exact: true })).toHaveValue(
    "[FICTICIA] INFANCIA SIGUE PENDIENTE"
  );
  await page.getByRole("button", { name: "Guardar cambios en la maqueta", exact: true }).click();
  await expect(page.getByText(/^Cambios sin guardar ·/)).toHaveCount(0);
});
