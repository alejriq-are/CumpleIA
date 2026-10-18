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
  directory = await mkdtemp(path.join(tmpdir(), "cumpleia-prototype-"));
  const loader = path.join(directory, "loader.cjs");
  await writeFile(
    loader,
    `const ts=require(${JSON.stringify(require.resolve("typescript"))}); module.exports=source=>ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.ESNext,target:ts.ScriptTarget.ES2021,jsx:ts.JsxEmit.ReactJSX}}).outputText;`
  );
  const entry = path.join(directory, "entry.js");
  await writeFile(
    entry,
    `import React from "react";import {createRoot} from "react-dom/client";import {LicitudFlowPrototype} from ${JSON.stringify(path.resolve("components/licitud/LicitudFlowPrototype.tsx"))};createRoot(document.getElementById("root")).render(React.createElement(LicitudFlowPrototype));`
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
      path.resolve("components/licitud/LicitudFlowPrototype.tsx"),
    ],
    { stdio: "pipe" }
  );
  css = await readFile(path.join(directory, "style.css"), "utf8");
});
test.afterAll(async () => {
  if (directory) await rm(directory, { recursive: true, force: true });
});
async function open(page: Page, fragment = "", selectDefault = true) {
  requests.length = 0;
  await page.route("**/*", async (route) => {
    const request = route.request();
    if (request.isNavigationRequest() && request.url().startsWith("http://prototype.invalid/")) {
      await route.fulfill({
        contentType: "text/html",
        body: '<main style="max-width:1152px;margin:auto;padding:24px"><div id="root"></div></main>',
      });
    } else {
      requests.push(`${request.method()} ${request.url()}`);
      await route.abort();
    }
  });
  await page.goto(`http://prototype.invalid/dashboard/licitud/maqueta${fragment}`);
  await page.addStyleTag({ content: css });
  await page.addScriptTag({ content: script });
  await expect(page.getByRole("heading", { name: "Licitud, paso a paso" })).toBeVisible();
  if (!fragment && selectDefault) await chooseTreatment(page, "adultos");
}
async function chooseTreatment(
  page: Page,
  treatment: "adultos" | "infancia",
  purpose = treatment === "adultos" ? "gestion" : "ensayo"
) {
  const change = page.getByRole("button", { name: "Cambiar tratamiento o finalidad" });
  if (await change.isVisible()) await change.click();
  await page.getByLabel("Tratamiento RAT de ejemplo", { exact: true }).selectOption(treatment);
  await page.getByLabel("Finalidad a evaluar", { exact: true }).selectOption(purpose);
  await page.getByRole("button", { name: "Abrir evaluación de ejemplo" }).click();
}
async function revokeFaculty(page: Page) {
  await page
    .getByText("Herramientas de demostración · ejemplos opcionales", { exact: true })
    .click();
  await page.getByLabel("Facultad simulada de la persona").selectOption("revocada");
}
async function tab(page: Page, name: string) {
  await page.getByRole("tab", { name, exact: true }).click();
}

test("adultos: orientacion, edicion y guardado simulado conservan borrador entre pestanas", async ({
  page,
}) => {
  await open(page);
  await expect(page.getByRole("list", { name: "Esquema del flujo" })).toBeVisible();
  await page.getByRole("button", { name: "Comenzar por el alcance" }).click();
  await expect(page.getByRole("tab", { name: "Completar datos", exact: true })).toHaveAttribute(
    "aria-selected",
    "true"
  );
  await page.getByRole("button", { name: "Continuar a base y fundamento" }).click();
  await page
    .getByLabel("Fundamento de ensayo", { exact: true })
    .fill("[FICTICIA] Texto de ensayo adulto");
  await expect(page.getByRole("status")).toContainText("Cambios sin guardar");
  await tab(page, "Historial y descargas");
  await tab(page, "Completar datos");
  await expect(page.getByLabel("Fundamento de ensayo", { exact: true })).toHaveValue(
    "[FICTICIA] Texto de ensayo adulto"
  );
  await page.getByRole("button", { name: "Simular guardado y continuar" }).click();
  await expect(page.getByRole("status")).toContainText("Guardado simulado");
  await expect(page.getByLabel("Notas del documento de ensayo")).toBeVisible();
  expect(requests).toEqual([]);
});

test("infancia: datos de escenario independientes y borradores conservados al alternar", async ({
  page,
}) => {
  await open(page);
  await chooseTreatment(page, "infancia");
  await tab(page, "Completar datos");
  await page.getByRole("button", { name: "3. Infancia", exact: true }).click();
  await page
    .getByLabel("Análisis de edad y alcance de ensayo")
    .fill("[FICTICIA] Alcance conservado");
  await chooseTreatment(page, "adultos");
  await tab(page, "Completar datos");
  await expect(page.getByRole("button", { name: "3. Infancia", exact: true })).toHaveCount(0);
  await chooseTreatment(page, "infancia");
  await tab(page, "Completar datos");
  await page.getByRole("button", { name: "3. Infancia", exact: true }).click();
  await expect(page.getByLabel("Análisis de edad y alcance de ensayo")).toHaveValue(
    "[FICTICIA] Alcance conservado"
  );
  expect(requests).toEqual([]);
});

test("revision vinculada a version exacta; cambios entre versiones no arrastran fundamento", async ({
  page,
}) => {
  await open(page, "#escenario=infancia&pestana=revisar&version=2");
  await page.getByLabel("Resultado de ensayo").selectOption("requiere_cambios");
  await page
    .getByLabel("Fundamento de revisión de ensayo")
    .fill("[FICTICIA] Observacion solo version 2");
  await page.getByRole("button", { name: "Previsualizar revisión · versión 2" }).click();
  await expect(page.getByRole("note")).toContainText("SIMULADA-INFANCIA-002");
  await page.getByLabel("Versión a consultar").selectOption("1");
  await expect(page.getByRole("note")).toHaveCount(0);
  await expect(page.getByLabel("Fundamento de revisión de ensayo")).toHaveValue("");
  await expect(page.getByRole("article", { name: "Documento seleccionado" })).toContainText(
    "SIMULADA-INFANCIA-001"
  );
  await page.getByLabel("Versión a consultar").selectOption("2");
  await expect(page.getByLabel("Fundamento de revisión de ensayo")).toHaveValue(
    "[FICTICIA] Observacion solo version 2"
  );
  await page.getByRole("button", { name: "Preparar otra versión en Completar datos" }).click();
  await expect(
    page.getByText(/Copia de SIMULADA-INFANCIA-002 preparada para explorar/)
  ).toBeVisible();
  await tab(page, "Historial y descargas");
  await expect(
    page.getByRole("list", { name: "Historial precargado" }).getByRole("listitem")
  ).toHaveCount(2);
  expect(requests).toEqual([]);
});

test("facultad revocada explica bloqueo y conserva consulta y revision independiente", async ({
  page,
}) => {
  await open(page, "#escenario=revocada&pestana=resumen&version=2");
  await page.getByRole("button", { name: "Consultar documento y bloqueo" }).click();
  await page.getByLabel("Tipo de actuación").selectOption("decision");
  await expect(page.getByText(/No puedes emitir una decisión de organización/)).toBeVisible();
  await expect(page.getByLabel("Resultado de ensayo")).toBeDisabled();
  await expect(page.getByLabel("Fundamento de revisión de ensayo")).toBeDisabled();
  await page.getByRole("button", { name: "Ver gestión de facultades" }).click();
  await expect(
    page.getByRole("complementary", { name: "Gestión de facultades de ejemplo" })
  ).toContainText("Revisión de facultad 2, revocada");
  await page.getByLabel("Tipo de actuación").selectOption("revision");
  await expect(page.getByLabel("Resultado de ensayo")).toBeEnabled();
  await tab(page, "Historial y descargas");
  await expect(
    page.getByText(/Segunda versión de ejemplo. Decisión documental precargada/)
  ).toBeVisible();
  expect(requests).toEqual([]);
});

test("descarga ficticia sin textos editados ni eventos registrados; sin solicitudes de API", async ({
  page,
}) => {
  await open(page, "#escenario=revocada&pestana=historial&version=2");
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "Descargar ejemplo ficticio JSON" }).click();
  const download = await downloadPromise;
  const value = JSON.parse(await readFile((await download.path())!, "utf8"));
  expect(value).toMatchObject({
    prototype_version: 2,
    treatment: "infancia",
    purpose: "ensayo",
    faculty_current: false,
    activation: "deshabilitada",
    allows_real_data: false,
    authorizes_action: false,
    persisted_events: 0,
    contains_user_edits: false,
  });
  expect(download.suggestedFilename()).toBe("maqueta-licitud-infancia-ensayo-v2.json");
  expect(requests).toEqual([]);
  await expect(
    page.getByRole("button", {
      name: /Activar|Registrar decisión|Registrar revisión|Otorgar facultad/,
    })
  ).toHaveCount(0);
});

test("teclado, enlace directo y ancho movil permiten recorrer las cuatro pestanas", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await open(page);
  const first = page.getByRole("tab", { name: "Resumen y siguientes pasos" });
  await first.focus();
  await page.keyboard.press("ArrowRight");
  await expect(page.getByRole("tab", { name: "Completar datos", exact: true })).toBeFocused();
  await page.keyboard.press("End");
  await expect(page.getByRole("tab", { name: "Historial y descargas" })).toBeFocused();
  await page.keyboard.press("Home");
  await expect(first).toBeFocused();
  for (const name of [
    "Resumen y siguientes pasos",
    "Completar datos",
    "Revisar documentos",
    "Historial y descargas",
  ]) {
    await tab(page, name);
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)
    ).toBe(true);
  }
  await chooseTreatment(page, "infancia");
  await revokeFaculty(page);
  await tab(page, "Revisar documentos");
  await expect(page).toHaveURL(
    /tratamiento=infancia&finalidad=ensayo&facultad=revocada&pestana=revisar&version=2/
  );
  if (process.env.CUMPLEIA_PROTOTYPE_SCREENSHOT) {
    await page.getByLabel("Tipo de actuación").selectOption("decision");
    await page.screenshot({ path: process.env.CUMPLEIA_PROTOTYPE_SCREENSHOT, fullPage: true });
  }
});

test("recarga reinicia textos de ensayo; resumen de escritorio sin desbordamiento", async ({
  page,
}) => {
  await page.setViewportSize({ width: 1280, height: 900 });
  await open(page);
  await tab(page, "Completar datos");
  await page.getByRole("button", { name: "Continuar a base y fundamento" }).click();
  await page.getByLabel("Fundamento de ensayo", { exact: true }).fill("[FICTICIA] Temporal");
  await page.reload();
  await page.addStyleTag({ content: css });
  await page.addScriptTag({ content: script });
  await page.getByRole("button", { name: "Continuar a base y fundamento" }).click();
  await expect(page.getByLabel("Fundamento de ensayo", { exact: true })).toHaveValue(
    "[FICTICIA] Evaluación pendiente. No hay autorización para operar."
  );
  await tab(page, "Resumen y siguientes pasos");
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(
    true
  );
  if (process.env.CUMPLEIA_PROTOTYPE_SCREENSHOT_DESKTOP)
    await page.screenshot({
      path: process.env.CUMPLEIA_PROTOTYPE_SCREENSHOT_DESKTOP,
      fullPage: true,
    });
  expect(requests).toEqual([]);
});

test("V2: seleccion inicial obligatoria y finalidades dependen del tratamiento", async ({
  page,
}) => {
  await open(page, "", false);
  await expect(page.getByRole("tablist")).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Abrir evaluación de ejemplo" })).toBeDisabled();
  await expect(page.getByLabel("Finalidad a evaluar", { exact: true })).toBeDisabled();
  await page.getByLabel("Tratamiento RAT de ejemplo", { exact: true }).selectOption("adultos");
  await page.getByLabel("Finalidad a evaluar", { exact: true }).selectOption("consultas");
  await page.getByLabel("Tratamiento RAT de ejemplo", { exact: true }).selectOption("infancia");
  await expect(page.getByLabel("Finalidad a evaluar", { exact: true })).toHaveValue("");
  await expect(
    page
      .getByLabel("Finalidad a evaluar", { exact: true })
      .getByRole("option", { name: /Atender consultas/ })
  ).toHaveCount(0);
  await page.getByLabel("Finalidad a evaluar", { exact: true }).selectOption("ensayo");
  await page.getByRole("button", { name: "Abrir evaluación de ejemplo" }).click();
  await expect(page.getByRole("complementary", { name: "Alcance seleccionado" })).toContainText(
    "Ensayar el análisis de infancia"
  );
  await expect(page.getByRole("list", { name: "Esquema del flujo" })).toContainText(
    "Revisa el alcance seleccionado"
  );
  await expect(page.getByRole("tab")).toHaveCount(4);
  expect(requests).toEqual([]);
});

test("V2: ejemplos solo precargan seleccion y facultad no cambia tratamiento ni finalidad", async ({
  page,
}) => {
  await open(page, "", false);
  await page
    .getByText("Herramientas de demostración · ejemplos opcionales", { exact: true })
    .click();
  await page.getByRole("button", { name: "Cargar ejemplo de infancia" }).click();
  await expect(page.getByLabel("Tratamiento RAT de ejemplo", { exact: true })).toHaveValue(
    "infancia"
  );
  await expect(page.getByRole("tablist")).toHaveCount(0);
  await page.getByRole("button", { name: "Abrir evaluación de ejemplo" }).click();
  await page.getByLabel("Facultad simulada de la persona").selectOption("revocada");
  await expect(page.getByRole("complementary", { name: "Alcance seleccionado" })).toContainText(
    "Programa con participantes de 10 a 13 años"
  );
  await expect(page.getByRole("complementary", { name: "Alcance seleccionado" })).toContainText(
    "Ensayar el análisis de infancia"
  );
  await tab(page, "Revisar documentos");
  await page.getByLabel("Tipo de actuación").selectOption("decision");
  await expect(page.getByLabel("Resultado de ensayo")).toBeDisabled();
  expect(requests).toEqual([]);
});

test("V2: mismo tratamiento, distintas finalidades, borradores separados y contexto exacto", async ({
  page,
}) => {
  await open(page);
  await tab(page, "Completar datos");
  await page.getByRole("button", { name: "Continuar a base y fundamento" }).click();
  await page.getByLabel("Fundamento de ensayo", { exact: true }).fill("[FICTICIA] Solo gestion");
  await chooseTreatment(page, "adultos", "consultas");
  await tab(page, "Completar datos");
  await page.getByRole("button", { name: "Continuar a base y fundamento" }).click();
  await expect(page.getByLabel("Fundamento de ensayo", { exact: true })).not.toHaveValue(
    "[FICTICIA] Solo gestion"
  );
  await page.getByLabel("Fundamento de ensayo", { exact: true }).fill("[FICTICIA] Solo consultas");
  await tab(page, "Revisar documentos");
  await expect(page.getByRole("article", { name: "Documento seleccionado" })).toContainText(
    "SIMULADA-ADULTOS-CONSULTAS-002"
  );
  await chooseTreatment(page, "adultos", "gestion");
  await tab(page, "Completar datos");
  await page.getByRole("button", { name: "Continuar a base y fundamento" }).click();
  await expect(page.getByLabel("Fundamento de ensayo", { exact: true })).toHaveValue(
    "[FICTICIA] Solo gestion"
  );
  expect(requests).toEqual([]);
});
