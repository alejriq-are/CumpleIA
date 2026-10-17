import { test, expect } from "@playwright/test";
import { mkdtemp, writeFile, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
let directory: string;
let script: string;
const integrated = Boolean(process.env.CUMPLEIA_UI_API);
const org = process.env.CUMPLEIA_UI_ORG ?? "a0000000-0000-0000-0000-000000000001";
const treatment = process.env.CUMPLEIA_UI_TREATMENT ?? "a0000000-0000-0000-0000-000000000004";
test.setTimeout(20000);
test.beforeAll(async () => {
  directory = await mkdtemp(path.join(tmpdir(), "cumpleia-licitud-ui-"));
  const loader = path.join(directory, "loader.cjs");
  await writeFile(
    loader,
    `const ts=require(${JSON.stringify(require.resolve("typescript"))}); module.exports=source=>ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.ESNext,target:ts.ScriptTarget.ES2021,jsx:ts.JsxEmit.ReactJSX}}).outputText;`
  );
  const entry = path.join(directory, "entry.js");
  await writeFile(
    entry,
    `
 import React from "react";import {createRoot} from "react-dom/client";
 import {LicitudWorkspace} from ${JSON.stringify(path.resolve("components/licitud/LicitudWorkspace.tsx"))};
 import {LegalAssessmentEditor} from ${JSON.stringify(path.resolve("components/licitud/LegalAssessmentEditor.tsx"))};
 const org=${JSON.stringify(org)},tid=${JSON.stringify(treatment)};
 const root=createRoot(document.getElementById("root"));
 const organization={id:org,name:"[FICTICIA] Comercial Piloto Andes SpA",role:"owner"};
 window.demo={calls:[],mode:"ok",rows:[]};
 const detail={id:tid,name:"[FICTICIA] Clientes",purposes:[{id:tid,purpose:"[FICTICIA] Gestion de clientes"}],data_categories:[{category_code:"id",category_name:"Identidad"}],data_subjects:[{category_code:"clientes",category_name:"Clientes"}]};
 if(!${integrated})window.fetch=async(url,opts)=>{
  const method=opts.method??"GET";window.demo.calls.push({url,method,body:opts.body?JSON.parse(opts.body):null});
  const result=value=>new Response(JSON.stringify(value),{status:200});
  if(url.includes("/rat/treatments"))return result(url.endsWith("/rat/treatments")?[detail]:detail);
  if(method==="POST"){
   if(window.demo.mode==="denied")return new Response(JSON.stringify({detail:"PRUEBA: sin permiso"}),{status:403});
   const body=JSON.parse(opts.body);const row={id:tid,organization_id:org,treatment_id:tid,version:1,status:"borrador",purpose_snapshot:detail.purposes[0].purpose,...body,lia_assessment:null};window.demo.rows=[row];return new Response(JSON.stringify(row),{status:201});
  }
  if(method==="PATCH"){
   if(window.demo.mode==="denied")return new Response(JSON.stringify({detail:"PRUEBA: sin permiso"}),{status:403});
   window.demo.rows[0]={...window.demo.rows[0],...JSON.parse(opts.body)};return result(window.demo.rows[0]);
  }
  if(url.includes("?offset="))return result(window.demo.rows);
  return result(window.demo.rows[0]);
 };
 window.workspace=(role="owner")=>root.render(React.createElement(LicitudWorkspace,{organizaciones:[{...organization,role}],token:async()=>"PRUEBA"}));
 window.editor=(id,readOnly=false)=>root.render(React.createElement(LegalAssessmentEditor,{organizationId:org,treatmentId:tid,assessmentId:id,readOnly,token:async()=>"PRUEBA"}));
 `
  );
  const runtime = require("next/dist/compiled/webpack/webpack");
  runtime.init();
  await new Promise<void>((resolve, reject) => {
    runtime.webpack(
      {
        mode: "development",
        devtool: false,
        entry,
        output: { path: directory, filename: "bundle.js" },
        resolve: {
          extensions: [".ts", ".tsx", ".js"],
          alias: { "@": process.cwd() },
          modules: [path.resolve("node_modules"), "node_modules"],
        },
        module: { rules: [{ test: /\.tsx?$/, use: loader }] },
        plugins: [
          new runtime.webpack.DefinePlugin({
            "process.env.NEXT_PUBLIC_API_URL": JSON.stringify(
              process.env.CUMPLEIA_UI_API ?? "http://test.invalid"
            ),
          }),
        ],
      },
      (error: Error | null, stats: { hasErrors: () => boolean; toString: () => string }) => {
        if (error || stats.hasErrors()) reject(error ?? new Error(stats.toString()));
        else resolve();
      }
    );
  });
  script = await readFile(path.join(directory, "bundle.js"), "utf8");
});
test.afterAll(async () => {
  if (directory) await rm(directory, { recursive: true, force: true });
});

test.beforeEach(async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 749 });
  if (integrated) await page.goto(process.env.CUMPLEIA_UI_API + "/__licitud-isolated-test");
  else await page.setContent('<div id="root"></div>');
  await page.addScriptTag({ content: "window.process={env:{}};" });
  await page.addScriptTag({ content: script });
});

async function selectTreatment(page: import("@playwright/test").Page, role = "owner") {
  await page.evaluate((role) => (window as any).workspace(role), role);
  await page.getByLabel("Tratamiento del RAT").selectOption(treatment);
  await expect(page.getByRole("heading", { name: "Evaluaciones guardadas" })).toBeVisible();
}
async function draft(page: import("@playwright/test").Page) {
  await selectTreatment(page);
  await page.getByLabel("Finalidad", { exact: true }).selectOption({ index: 1 });
  await page.getByLabel("Identidad", { exact: true }).check();
  await page.getByLabel("Clientes", { exact: true }).check();
  await page.getByLabel("Base de licitud propuesta").selectOption("interes_legitimo_art13d");
  await page.getByLabel("Fundamento", { exact: true }).fill("[FICTICIA] Prueba de recorrido");
  await expect(page.getByRole("button", { name: "Crear borrador", exact: true })).toBeDisabled();
  await page.getByLabel("Confirmo que ingreso únicamente datos ficticios de prueba").check();
  await page.getByRole("button", { name: "Crear borrador", exact: true }).click();
}
test("crea borrador, abre y guarda LIA y recupera el historial sin activar EIPD", async ({
  page,
}) => {
  await draft(page);
  await expect(page.getByRole("status")).toContainText("Borrador creado");
  const link = page.getByRole("link", { name: /versión 1/ });
  const href = await link.getAttribute("href");
  expect(href).toContain(`/dashboard/licitud/${treatment}/`);
  expect(href).toContain(`organizationId=${org}`);
  const id = href!.split("/").pop()!.split("?")[0];
  await page.evaluate((id) => (window as any).editor(id), id);
  await page
    .getByLabel("Interés legítimo declarado", { exact: true })
    .fill("[FICTICIA] Interes pendiente de revision");
  await page
    .getByLabel("Análisis de necesidad", { exact: true })
    .fill("[FICTICIA] Necesidad de prueba");
  await page.getByRole("button", { name: "Guardar borrador", exact: true }).click();
  await expect(page.getByRole("status")).toContainText("Borrador guardado");
  await page.evaluate(() => (window as any).workspace());
  await page.getByLabel("Tratamiento del RAT").selectOption(treatment);
  await expect(page.getByRole("link", { name: /versión 1/ })).toBeVisible();
  await page.evaluate((id) => (window as any).editor(id), id);
  await expect(page.getByLabel("Análisis de necesidad", { exact: true })).toHaveValue(
    "[FICTICIA] Necesidad de prueba"
  );
  await expect(page.getByRole("button", { name: /Confirmar|Activar/ })).toHaveCount(0);
  if (!integrated) {
    const calls = await page.evaluate(() => (window as any).demo.calls);
    expect(calls.some((c: any) => c.url.includes("/confirm"))).toBe(false);
  }
});
test("viewer consulta sin formulario de creación", async ({ page }) => {
  test.skip(integrated, "El rol servidor se prueba en backend");
  await selectTreatment(page, "viewer");
  await expect(
    page.getByText("Tu rol permite consultar evaluaciones; no permite crear borradores.")
  ).toBeVisible();
  await expect(page.getByRole("button", { name: "Crear borrador", exact: true })).toHaveCount(0);
});
test("rechazo de creación conserva el formulario y no presenta éxito", async ({ page }) => {
  test.skip(integrated, "Negativa controlada de UI");
  await page.evaluate(() => ((window as any).demo.mode = "denied"));
  await draft(page);
  await expect(page.getByRole("alert")).toContainText("sin permiso");
  await expect(page.getByLabel("Fundamento", { exact: true })).toHaveValue(
    "[FICTICIA] Prueba de recorrido"
  );
  await expect(page.getByRole("link", { name: /versión 1/ })).toHaveCount(0);
});
test("editar LIA conserva campos anteriores no representados", async ({ page }) => {
  test.skip(integrated, "Fixture de preservación controlada");
  await draft(page);
  await expect(page.getByRole("status")).toContainText("Borrador creado");
  await page.evaluate((tid) => {
    (window as any).demo.rows[0].lia_assessment = {
      purpose_and_interest: { public_benefit: "[FICTICIA] Conservar" },
      safeguards: { measures: [{ description: "[FICTICIA] Medida previa" }] },
    };
    (window as any).editor(tid);
  }, treatment);
  await page.getByLabel("Análisis de necesidad", { exact: true }).fill("[FICTICIA] Nuevo");
  await page.getByRole("button", { name: "Guardar borrador", exact: true }).click();
  await expect(page.getByRole("status")).toContainText("Borrador guardado");
  const row = await page.evaluate(() => (window as any).demo.rows[0]);
  expect(row.lia_assessment.purpose_and_interest.public_benefit).toBe("[FICTICIA] Conservar");
  expect(row.lia_assessment.safeguards.measures).toHaveLength(1);
});
test("historial confirmado no permite editar", async ({ page }) => {
  test.skip(integrated, "Fixture confirmada sin confirmar por API");
  await draft(page);
  await expect(page.getByRole("status")).toContainText("Borrador creado");
  await page.evaluate((tid) => {
    (window as any).demo.rows[0].status = "confirmado";
    (window as any).editor(tid);
  }, treatment);
  await expect(page.getByLabel("Fundamento", { exact: true })).toBeDisabled();
  await expect(page.getByRole("button", { name: "Guardar borrador", exact: true })).toHaveCount(0);
});
