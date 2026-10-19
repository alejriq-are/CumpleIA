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
  await page.getByRole("button", { name: "Guardar borrador de ensayo" }).click();
  await expect(page.getByRole("status").filter({ hasText: "Guardado simulado" })).toBeVisible();
  await page.getByRole("button", { name: "Preparar documento para revisión", exact: true }).click();
  await expect(
    page.getByLabel("Notas específicas del documento (opcional)", { exact: true })
  ).toBeVisible();
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
  await page.getByRole("button", { name: "Crear nueva versión a partir de DEMO-2" }).click();
  await expect(
    page.getByRole("status").filter({ hasText: "SIMULADA-INFANCIA-002 se conserva intacta" })
  ).toBeVisible();
  await tab(page, "Historial y descargas");
  await expect(
    page.getByRole("list", { name: "Historial documental de ensayo" }).getByRole("listitem")
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
    prototype_version: 3,
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

async function prepare(page: Page, notes = "") {
  await tab(page, "Completar datos");
  await page.getByRole("button", { name: "Preparar documento para revisión", exact: true }).click();
  if (notes)
    await page
      .getByLabel("Notas específicas del documento (opcional)", { exact: true })
      .fill(notes);
}
async function register(page: Page, version: number) {
  await page
    .getByRole("checkbox", {
      name: "He revisado esta vista previa como responsable ficticio del ensayo",
    })
    .check();
  await page
    .getByRole("button", { name: `Simular registro de versión DEMO-${version}`, exact: true })
    .click();
  await expect(page.getByRole("article", { name: "Documento seleccionado" })).toContainText(
    `DEMO-${version}`
  );
}

test("preparacion: vista previa completa, pendientes y revision invalidada por cambios", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await open(page);
  await tab(page, "Completar datos");
  await expect(
    page.getByRole("navigation", { name: "Secciones para completar" }).getByRole("button")
  ).toHaveCount(2);
  await page.getByRole("button", { name: "Continuar a base y fundamento" }).click();
  await page
    .getByLabel("Fundamento de ensayo", { exact: true })
    .fill("[FICTICIA] Fundamento reunido");
  await prepare(page);
  await expect(page.getByRole("article", { name: "Contenido que se prepararía" })).toContainText(
    "[FICTICIA] Fundamento reunido"
  );
  await expect(page.getByRole("region", { name: "Faltantes del documento" })).toContainText(
    "Base de licitud pendiente de definir"
  );
  await expect(
    page.getByRole("button", { name: "Simular registro de versión DEMO-3", exact: true })
  ).toBeDisabled();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(
    true
  );
  if (process.env.CUMPLEIA_PREPARATION_MOBILE)
    await page.screenshot({ path: process.env.CUMPLEIA_PREPARATION_MOBILE, fullPage: true });
  const reviewed = page.getByRole("checkbox", {
    name: "He revisado esta vista previa como responsable ficticio del ensayo",
  });
  await reviewed.check();
  await page
    .getByLabel("Notas específicas del documento (opcional)", { exact: true })
    .fill("[FICTICIA] Nota posterior a lectura");
  await expect(reviewed).not.toBeChecked();
  await expect(
    page.getByRole("button", { name: "Simular registro de versión DEMO-3", exact: true })
  ).toBeDisabled();
  await page.getByRole("button", { name: "Volver a base y fundamento", exact: true }).click();
  await page
    .getByLabel("Fundamento de ensayo", { exact: true })
    .fill("[FICTICIA] Fundamento corregido");
  await prepare(page);
  await expect(
    page.getByLabel("Notas específicas del documento (opcional)", { exact: true })
  ).toHaveValue("[FICTICIA] Nota posterior a lectura");
  await expect(reviewed).not.toBeChecked();
  await register(page, 3);
  await expect(page.getByRole("article", { name: "Documento seleccionado" })).toContainText(
    "[FICTICIA] Fundamento corregido"
  );
  expect(requests).toEqual([]);
});

test("documentos: registrar incluye infancia y notas, descargar copia exacta, modificar crea otra version", async ({
  page,
}) => {
  await open(page, "#tratamiento=infancia&finalidad=ensayo&pestana=completar&version=2");
  await expect(
    page.getByRole("navigation", { name: "Secciones para completar" }).getByRole("button")
  ).toHaveCount(3);
  await page.getByRole("button", { name: "2. Base y fundamento", exact: true }).click();
  await page.getByLabel("Base propuesta de ensayo").selectOption("analisis");
  await page
    .getByLabel("Fundamento de ensayo", { exact: true })
    .fill("[FICTICIA] Fundamento version 3");
  await page.getByRole("button", { name: "3. Infancia", exact: true }).click();
  await page
    .getByLabel("Análisis de edad y alcance de ensayo")
    .fill("[FICTICIA] Cinco participantes; sin datos sensibles");
  await prepare(page, "[FICTICIA] Nota especifica version 3");
  if (process.env.CUMPLEIA_PREPARATION_DESKTOP)
    await page.screenshot({ path: process.env.CUMPLEIA_PREPARATION_DESKTOP, fullPage: true });
  await register(page, 3);
  const document = page.getByRole("article", { name: "Documento seleccionado" });
  await expect(document).toContainText("[FICTICIA] Cinco participantes; sin datos sensibles");
  await expect(document).toContainText("[FICTICIA] Nota especifica version 3");
  await tab(page, "Historial y descargas");
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "Descargar ejemplo ficticio JSON" }).click();
  const value = JSON.parse(await readFile((await (await downloadPromise).path())!, "utf8"));
  expect(value).toMatchObject({
    contains_user_edits: true,
    persisted_events: 0,
    activation: "deshabilitada",
    simulated_document_versions: 1,
    document: {
      reference: "SIMULADA-INFANCIA-003",
      content: {
        draft: {
          basis: "analisis",
          rationale: "[FICTICIA] Fundamento version 3",
          age: "[FICTICIA] Cinco participantes; sin datos sensibles",
          notes: "[FICTICIA] Nota especifica version 3",
        },
      },
    },
  });
  await page.getByRole("button", { name: "Consultar versión 3", exact: true }).click();
  await page
    .getByRole("button", { name: "Crear nueva versión a partir de DEMO-3", exact: true })
    .click();
  await page
    .getByLabel("Fundamento de ensayo", { exact: true })
    .fill("[FICTICIA] Fundamento version 4");
  await page
    .getByLabel("Motivo del cambio (obligatorio)", { exact: true })
    .fill("[FICTICIA] Actualizar fundamento");
  await prepare(page, "[FICTICIA] Nota version 4");
  await register(page, 4);
  await page.getByLabel("Versión a consultar").selectOption("3");
  await expect(document).toContainText("[FICTICIA] Fundamento version 3");
  await expect(document).not.toContainText("[FICTICIA] Fundamento version 4");
  await page.getByLabel("Versión a consultar").selectOption("4");
  await expect(document).toContainText("[FICTICIA] Fundamento version 4");
  expect(requests).toEqual([]);
});

test("versiones de ensayo por finalidad: no se mezclan ni reaparecen despues de recargar", async ({
  page,
}) => {
  await open(page);
  await prepare(page);
  await register(page, 3);
  await chooseTreatment(page, "adultos", "consultas");
  await tab(page, "Historial y descargas");
  await expect(page.getByRole("button", { name: "Consultar versión 3", exact: true })).toHaveCount(
    0
  );
  await chooseTreatment(page, "adultos", "gestion");
  await tab(page, "Historial y descargas");
  await page.getByRole("button", { name: "Consultar versión 3", exact: true }).click();
  await page.reload();
  await page.addStyleTag({ content: css });
  await page.addScriptTag({ content: script });
  await expect(page.getByRole("status")).toContainText("La versión de ensayo no está disponible");
  await expect(page.getByLabel("Versión a consultar")).toHaveValue("2");
  expect(requests).toEqual([]);
});

test("copia desde version seleccionada y conserva origen, motivo y versiones anteriores", async ({
  page,
}) => {
  await open(page);
  await tab(page, "Completar datos");
  await page.getByRole("button", { name: "Continuar a base y fundamento" }).click();
  await page
    .getByLabel("Fundamento de ensayo", { exact: true })
    .fill("[FICTICIA] Original version 3");
  await prepare(page, "[FICTICIA] Notas version 3");
  await register(page, 3);
  await page
    .getByRole("button", { name: "Crear nueva versión a partir de DEMO-3", exact: true })
    .click();
  await expect(
    page.getByRole("region", { name: "Origen y motivo de la nueva versión" })
  ).toContainText("SIMULADA-ADULTOS-003");
  await page
    .getByLabel("Motivo del cambio (obligatorio)", { exact: true })
    .fill("[FICTICIA] Revision de contenido");
  await page
    .getByLabel("Fundamento de ensayo", { exact: true })
    .fill("[FICTICIA] Version 4 distinta");
  await prepare(page, "[FICTICIA] Notas version 4");
  await register(page, 4);
  // Consult an older version while the latest draft has different content.
  await page.getByLabel("Versión a consultar").selectOption("3");
  await expect(
    page.getByRole("heading", { name: "Emitir revisión sobre DEMO-3", exact: true })
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Crear nueva versión a partir de DEMO-3", exact: true })
    .click();
  await expect(page.getByLabel("Fundamento de ensayo", { exact: true })).toHaveValue(
    "[FICTICIA] Original version 3"
  );
  await expect(page.getByLabel("Motivo del cambio (obligatorio)", { exact: true })).toHaveValue("");
  await page
    .getByLabel("Motivo del cambio (obligatorio)", { exact: true })
    .fill("[FICTICIA] Nueva rama desde 3");
  await prepare(page);
  await expect(
    page.getByLabel("Notas específicas del documento (opcional)", { exact: true })
  ).toHaveValue("[FICTICIA] Notas version 3");
  await expect(page.getByRole("article", { name: "Contenido que se prepararía" })).toContainText(
    "Nueva rama desde 3"
  );
  await register(page, 5);
  const document = page.getByRole("article", { name: "Documento seleccionado" });
  await expect(document).toContainText("[FICTICIA] Original version 3");
  await expect(document).toContainText("SIMULADA-ADULTOS-003 · DEMO-3");
  await expect(document).toContainText("[FICTICIA] Nueva rama desde 3");
  await page.getByLabel("Versión a consultar").selectOption("4");
  await expect(document).toContainText("[FICTICIA] Version 4 distinta");
  await page.getByLabel("Versión a consultar").selectOption("3");
  await expect(document).not.toContainText("Nueva rama desde 3");
  expect(requests).toEqual([]);
});

test("copia protege borrador pendiente y exige motivo de cambio revisado", async ({ page }) => {
  await open(page);
  await tab(page, "Completar datos");
  await page.getByRole("button", { name: "Continuar a base y fundamento" }).click();
  await page
    .getByLabel("Fundamento de ensayo", { exact: true })
    .fill("[FICTICIA] No descartar sin confirmar");
  await tab(page, "Revisar documentos");
  await page
    .getByRole("button", { name: "Crear nueva versión a partir de DEMO-2", exact: true })
    .click();
  await expect(
    page.getByRole("alertdialog", { name: "Confirmar reemplazo del borrador" })
  ).toBeVisible();
  await page.getByRole("button", { name: "Conservar borrador actual", exact: true }).click();
  await tab(page, "Completar datos");
  await expect(page.getByLabel("Fundamento de ensayo", { exact: true })).toHaveValue(
    "[FICTICIA] No descartar sin confirmar"
  );
  await tab(page, "Revisar documentos");
  await page
    .getByRole("button", { name: "Crear nueva versión a partir de DEMO-2", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Reemplazar borrador y copiar DEMO-2", exact: true })
    .click();
  await expect(page.getByLabel("Fundamento de ensayo", { exact: true })).toHaveValue(
    "[FICTICIA] Evaluación pendiente. No hay autorización para operar."
  );
  await prepare(page);
  const check = page.getByRole("checkbox", {
    name: "He revisado esta vista previa como responsable ficticio del ensayo",
  });
  const record = page.getByRole("button", {
    name: "Simular registro de versión DEMO-3",
    exact: true,
  });
  await check.check();
  await expect(record).toBeDisabled();
  await page.getByLabel("Motivo del cambio (obligatorio)", { exact: true }).fill("   ");
  await check.check();
  await expect(record).toBeDisabled();
  await page
    .getByLabel("Motivo del cambio (obligatorio)", { exact: true })
    .fill("[FICTICIA] Correccion desde fixture 2");
  await expect(check).not.toBeChecked();
  await check.check();
  await expect(record).toBeEnabled();
  if (process.env.CUMPLEIA_COPY_PREVIEW)
    await page.screenshot({ path: process.env.CUMPLEIA_COPY_PREVIEW, fullPage: true });
  await record.click();
  await tab(page, "Historial y descargas");
  const pending = page.waitForEvent("download");
  await page.getByRole("button", { name: "Descargar ejemplo ficticio JSON" }).click();
  const value = JSON.parse(await readFile((await (await pending).path())!, "utf8"));
  expect(value.document.content.draft).toMatchObject({
    origin: { version: "2", reference: "SIMULADA-ADULTOS-002" },
    changeReason: "[FICTICIA] Correccion desde fixture 2",
  });
  expect(value).toMatchObject({ activation: "deshabilitada", persisted_events: 0 });
  expect(requests).toEqual([]);
});

test("historial: solo resalta la version seleccionada y descarga el mismo documento", async ({
  page,
}) => {
  await open(page);
  await prepare(page);
  await register(page, 3);
  for (const version of ["1", "2", "3"]) {
    await page.getByLabel("Versión a consultar").selectOption(version);
    await tab(page, "Historial y descargas");
    const history = page.getByRole("list", { name: "Historial documental de ensayo" });
    const selected = history.locator('[aria-current="true"]');
    await expect(selected).toHaveCount(1);
    await expect(selected).toContainText(`Versión ${version} · DEMO-${version}`);
    await expect(selected).toContainText("Seleccionada para descarga");
    await expect(selected).toHaveCSS("background-color", "rgb(239, 246, 255)");
    for (const other of ["1", "2", "3"].filter((value) => value !== version)) {
      const row = history.getByRole("listitem").filter({
        has: page.getByRole("heading", { name: `Versión ${other} · DEMO-${other}`, exact: true }),
      });
      await expect(row).toHaveCSS("background-color", "rgb(255, 255, 255)");
      await expect(row).not.toContainText("Seleccionada para descarga");
    }
    await expect(page.getByText(`La descarga de DEMO-${version}`, { exact: false })).toBeVisible();
    const pending = page.waitForEvent("download");
    await page.getByRole("button", { name: "Descargar ejemplo ficticio JSON" }).click();
    const downloaded = await pending;
    expect(downloaded.suggestedFilename()).toBe(`maqueta-licitud-adultos-gestion-v${version}.json`);
    const value = JSON.parse(await readFile((await downloaded.path())!, "utf8"));
    expect(value.document.version).toBe(`DEMO-${version}`);
    expect(value).toMatchObject({ activation: "deshabilitada", persisted_events: 0 });
    await history
      .getByRole("button", { name: `Consultar versión ${version}`, exact: true })
      .click();
  }
  expect(requests).toEqual([]);
});

test("ayudas: explican actuacion y resultado seleccionado sin cambiar el documento", async ({
  page,
}) => {
  await open(page);
  await tab(page, "Revisar documentos");
  const action = page.getByLabel("Tipo de actuación", { exact: true });
  const result = page.getByLabel("Resultado de ensayo", { exact: true });
  const actionHelp = page.locator("#prototype-action-help");
  const resultHelp = page.locator("#prototype-result-help");
  await expect(action).toHaveAttribute("aria-describedby", "prototype-action-help");
  await expect(result).toHaveAttribute("aria-describedby", "prototype-result-help");
  await expect(actionHelp).toContainText("señalar faltantes");
  await expect(resultHelp).toContainText("Selecciona el resultado");
  await result.selectOption("requiere_cambios");
  await expect(resultHelp).toContainText("antes de otra revisión");
  await result.selectOption("no_continuar");
  await expect(resultHelp).toContainText("no detiene procesos automáticamente");
  await action.selectOption("decision");
  await expect(actionHelp).toContainText("facultad vigente");
  await expect(result).toHaveValue("");
  await expect(result.getByRole("option", { name: "No continuar", exact: true })).toHaveCount(0);
  await result.selectOption("requiere_cambios");
  await expect(resultHelp).toContainText("la organización solicita ajustes");
  await revokeFaculty(page);
  await expect(result).toBeDisabled();
  await expect(actionHelp).toContainText("facultad vigente");
  await action.selectOption("revision");
  await expect(result).toBeEnabled();
  await expect(resultHelp).toContainText("Selecciona el resultado");
  await expect(page.getByRole("article", { name: "Documento seleccionado" })).toContainText(
    "SIMULADA-ADULTOS-002"
  );
  expect(requests).toEqual([]);
});
