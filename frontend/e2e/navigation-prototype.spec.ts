import { test, expect, type Page } from "@playwright/test";
import { mkdtemp, readFile, writeFile, rm } from "node:fs/promises";
import { execFileSync } from "node:child_process";
import { tmpdir } from "node:os";
import path from "node:path";

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
      path.resolve("components/navigation/NavigationPrototype.tsx"),
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
const taskNav = (page: Page) => page.getByRole("navigation", { name: "Tareas del módulo" });
const stepNav = (page: Page) => page.getByRole("navigation", { name: "Pasos de la tarea" });
const work = (page: Page) => page.locator("#prototype-content");
async function module(page: Page, name: string) {
  if (await page.getByLabel("Módulo de la maqueta", { exact: true }).isVisible()) {
    const values: Record<string, string> = {
      "Panel principal": "panel",
      Diagnóstico: "diagnostico",
      "Inventario RAT": "rat",
      "Bases de licitud": "licitud",
      Documentos: "documentos",
      Evidencia: "evidencia",
      Organización: "organizacion",
    };
    await page.getByLabel("Módulo de la maqueta", { exact: true }).selectOption(values[name]);
  } else await moduleNav(page).getByRole("button", { name, exact: true }).click();
}
async function task(page: Page, name: string) {
  await taskNav(page).getByRole("button", { name, exact: true }).click();
}
async function step(page: Page, name: string) {
  await stepNav(page)
    .getByRole("button", { name: new RegExp(name) })
    .click();
}
async function children(page: Page) {
  await page.getByLabel("Escenario de prueba").selectOption("infancia");
  await module(page, "Bases de licitud");
}

test("todos los módulos y sus tareas tienen destino, foco y menú consistente sin red", async ({
  page,
}) => {
  await open(page);
  for (const name of [
    "Diagnóstico",
    "Inventario RAT",
    "Bases de licitud",
    "Documentos",
    "Evidencia",
    "Organización",
  ]) {
    await module(page, name);
    for (const t of [
      "Resumen",
      "Completar datos",
      "Documentos y revisiones",
      "Historial y descargas",
    ]) {
      await task(page, t);
      const count = await stepNav(page).getByRole("button").count();
      for (let i = 0; i < count; i++) {
        await stepNav(page).getByRole("button").nth(i).click();
        await expect(work(page)).toBeFocused();
        await expect(work(page).locator("#prototype-section-title")).not.toBeEmpty();
      }
    }
  }
  await module(page, "Panel principal");
  await expect(page.getByRole("heading", { name: "Continúa donde lo dejaste" })).toBeVisible();
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
  await task(page, "Documentos y revisiones");
  await expect(work(page).getByText(value, { exact: true })).toBeVisible();
  await page.getByLabel("Escenario de prueba").selectOption("infancia");
  await task(page, "Completar datos");
  await step(page, "Base y fundamento");
  await expect(page.getByLabel("Fundamento", { exact: true })).not.toHaveValue(value);
  await expect(
    stepNav(page).getByRole("button", { name: /Infancia y adolescencia/ })
  ).toBeVisible();
  await page.getByLabel("Escenario de prueba").selectOption("adultos");
  await expect(stepNav(page).getByRole("button", { name: /Infancia y adolescencia/ })).toHaveCount(
    0
  );
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

test("móvil sin desborde, selector de pasos y diálogo utilizable", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await open(page);
  await children(page);
  await task(page, "Completar datos");
  await page.getByLabel("Paso de la tarea", { exact: true }).selectOption("preparar");
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
  await expect(
    stepNav(page).getByRole("button", { name: /Infancia y adolescencia/ })
  ).toContainText("Cambios sin guardar");
  await page.getByRole("button", { name: "Guardar cambios en la maqueta", exact: true }).click();
  await expect(
    stepNav(page).getByRole("button", { name: /Infancia y adolescencia/ })
  ).toContainText("Guardado en maqueta");
  await page.getByLabel("Notas de infancia", { exact: true }).fill("[FICTICIA] NOTA SIN GUARDAR");
  await expect(
    stepNav(page).getByRole("button", { name: /Infancia y adolescencia/ })
  ).toContainText("Cambios sin guardar");
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
  await children(page);
  await task(page, "Completar datos");
  await step(page, "Infancia y adolescencia");
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.evaluate(() => new Promise(requestAnimationFrame));
  await page.screenshot({ path: path.join(dir, "maqueta-infancia-desktop.png"), fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  await module(page, "Panel principal");
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.evaluate(() => new Promise(requestAnimationFrame));
  await page.screenshot({ path: path.join(dir, "maqueta-panel-mobile.png"), fullPage: true });
  await module(page, "Bases de licitud");
  await task(page, "Completar datos");
  await page.getByLabel("Paso de la tarea", { exact: true }).selectOption("infancia");
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.evaluate(() => new Promise(requestAnimationFrame));
  await page.screenshot({ path: path.join(dir, "maqueta-infancia-mobile.png"), fullPage: true });
});
