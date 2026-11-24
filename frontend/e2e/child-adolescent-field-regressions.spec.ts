import { test, expect } from "@playwright/test";
import { mkdtemp, writeFile, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";

let directory: string;
let script: string;

test.beforeAll(async () => {
  directory = await mkdtemp(path.join(tmpdir(), "cumpleia-eipd-ui-"));
  const loader = path.join(directory, "typescript-loader.cjs");
  await writeFile(
    loader,
    `const ts=require(${JSON.stringify(require.resolve("typescript"))}); module.exports=function(source){return ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.ESNext,target:ts.ScriptTarget.ES2021,jsx:ts.JsxEmit.ReactJSX}}).outputText};`
  );
  const entry = path.join(directory, "entry.js");
  await writeFile(
    entry,
    `
    import React from "react";
    import {createRoot} from "react-dom/client";
    import {ChildAdolescentEditor} from ${JSON.stringify(path.resolve("components/licitud/ChildAdolescentEditor.tsx"))};
    import {childEditorAccess} from ${JSON.stringify(path.resolve("lib/licitud/editor-access.ts"))};
    import {childApi,validateChildReadiness} from ${JSON.stringify(path.resolve("lib/api/child-adolescent.ts"))};
    const id="a0000000-0000-0000-0000-000000000001";
    const scope={organizationId:id,treatmentId:id,assessmentId:id,token:"PRUEBA"};
    const emptyDecision={prerequisites_met:false,context_metadata:null,issues:[{code:"politica_infancia_no_implementada",message:"Revisión pendiente de infancia"}]};
    const v5={evaluation_version:5,context_schema_version:4,context_hash:"a".repeat(64),child_adolescent_coverage:"contexto_v4",resolution_child_coverage:"no_cubierta",can_confirm:false,authorizes_action:false,child_adolescent:{result:"incompleto",association_status:"vigente",can_confirm:false,authorizes_action:false},confirmation_blockers:emptyDecision.issues,continuar:emptyDecision,requiere_cambios:emptyDecision,no_continuar:emptyDecision};
    window.demo={calls:[],mode:"ok",release:null};
    let row={id,status:"borrador",rat_context_snapshot:{data_categories:[{category_code:"id",category_name:"Identidad"}],data_subjects:[{category_code:"clientes",category_name:"Clientes"}]},child_adolescent_assessment:{assessment:{schema_version:1,declared_groups:["ninos_ninas"],data_category_codes:["id"],data_subject_codes:["clientes"],notes:"PRUEBA: nota inicial",evidence:[{evidence_type:"PRUEBA",reference:"PRUEBA: evidencia",obtained_on:"2026-10-01",notes:"PRUEBA: conservar"}]},context_binding:{binding_version:1,context_hash:"a".repeat(64),document_hash:"b".repeat(64)}}};
    window.fetch=async(url,options)=>{
      window.demo.calls.push({url,options});
      if(options.method==="PATCH"){
        if(window.demo.mode==="denied")return new Response(JSON.stringify({detail:"PRUEBA: sin permiso"}),{status:403});
        if(window.demo.mode==="unknown")throw new Error("PRUEBA: respuesta incierta");
        if(window.demo.mode==="wait")await new Promise(resolve=>{window.demo.release=resolve;});
        const document=JSON.parse(options.body).child_adolescent_assessment;
        row={...row,child_adolescent_assessment:document?{assessment:document,context_binding:row.child_adolescent_assessment?.context_binding??{binding_version:1,context_hash:"a".repeat(64),document_hash:"b".repeat(64)}}:null};
      }
      if(url.endsWith("/readiness")){
        if(window.demo.mode==="diagnostic-error" && window.demo.calls.some(c=>c.options.method==="PATCH"))return new Response(JSON.stringify({detail:"PRUEBA"}),{status:503});
        return new Response(JSON.stringify({eipd_controls_v5:v5}),{status:200});
      }
      return new Response(JSON.stringify(row),{status:200});
    };
    const load=()=>childApi.load(scope),save=doc=>childApi.save(scope,doc),readiness=()=>childApi.readiness(scope);
    window.validateChildReadiness=validateChildReadiness;
    window.childEditorAccess=childEditorAccess;
    window.readyFixture=()=>JSON.parse(JSON.stringify({eipd_controls_v5:v5}));
    const root=createRoot(document.getElementById("root"));
    window.mount=(options={})=>{if(options.confirmed)row.status="confirmado";root.render(React.createElement(ChildAdolescentEditor,{load,save,readiness,readOnly:options.readOnly??false}));};
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
            "process.env.NEXT_PUBLIC_API_URL": JSON.stringify("http://test.invalid"),
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
  await page.setContent('<div id="root"></div>');
  await page.addScriptTag({ content: script });
});
async function mount(page: import("@playwright/test").Page, options = {}) {
  await page.evaluate((options) => (window as any).mount(options), options);
  await expect(page.getByLabel("Notas", { exact: true })).toBeVisible();
}

async function savedBody(page: import("@playwright/test").Page) {
  await page.getByRole("button", { name: "Guardar documento", exact: true }).click();
  await expect(page.getByRole("status")).toHaveText("Documento guardado.");
  const calls = await page.evaluate(() =>
    (window as any).demo.calls.filter((c: any) => c.options.method === "PATCH")
  );
  expect(calls).toHaveLength(1);
  const document = JSON.parse(calls[0].options.body).child_adolescent_assessment;
  expect(document.evidence).toEqual([
    {
      evidence_type: "PRUEBA",
      reference: "PRUEBA: evidencia",
      obtained_on: "2026-10-01",
      notes: "PRUEBA: conservar",
    },
  ]);
  await expect(page.getByText("Confirmación y activación bloqueadas.")).toBeVisible();
  return document;
}

test("L1 guarda analisis de alcance sin alterar evidencia", async ({ page }) => {
  await mount(page);
  await page.getByLabel("Análisis de edad y alcance", { exact: true }).fill("PRUEBA: alcance");
  expect((await savedBody(page)).age_scope_analysis).toBe("PRUEBA: alcance");
});
test("L1 vaciar analisis de alcance envia null", async ({ page }) => {
  await mount(page);
  const input = page.getByLabel("Análisis de edad y alcance", { exact: true });
  await input.fill("PRUEBA: alcance");
  await input.fill("");
  expect((await savedBody(page)).age_scope_analysis).toBeNull();
});
test("L1 alcance bloqueado en solo lectura sin PATCH", async ({ page }) => {
  await mount(page, { readOnly: true });
  await expect(page.getByLabel("Análisis de edad y alcance", { exact: true })).toBeDisabled();
  expect(
    await page.evaluate(
      () => (window as any).demo.calls.filter((c: any) => c.options.method === "PATCH").length
    )
  ).toBe(0);
});

test("guarda el valor especificado en best_interests_analysis", async ({ page }) => {
  await mount(page);
  await page.getByLabel("Interés superior", { exact: true }).fill("PRUEBA: interes");
  const body = await savedBody(page);
  expect(body.best_interests_analysis).toBe("PRUEBA: interes");
});
test("limpia best_interests_analysis a null tras establecerlo", async ({ page }) => {
  await mount(page);
  await page.getByLabel("Interés superior", { exact: true }).fill("PRUEBA: interes");
  await page.getByLabel("Interés superior", { exact: true }).fill("");
  const body = await savedBody(page);
  expect(body.best_interests_analysis).toBeNull();
});
test("readOnly deshabilitado no realiza PATCH", async ({ page }) => {
  await mount(page, { readOnly: true });
  await expect(page.getByLabel("Interés superior", { exact: true })).toBeDisabled();
  const calls = await page.evaluate(() =>
    (window as any).demo.calls.filter((c: any) => c.options.method === "PATCH")
  );
  expect(calls).toHaveLength(0);
});

test("L2 guarda declaracion sensible sin alterar evidencia", async ({ page }) => {
  await mount(page);
  await page
    .getByRole("combobox", { name: /^Datos sensibles de adolescentes menores de 16/ })
    .selectOption("si");
  expect((await savedBody(page)).sensitive_under16).toBe("si");
});
test("L2 vaciar declaracion sensible envia null", async ({ page }) => {
  await mount(page);
  const input = page.getByRole("combobox", {
    name: /^Datos sensibles de adolescentes menores de 16/,
  });
  await input.selectOption("si");
  await input.selectOption("");
  expect((await savedBody(page)).sensitive_under16).toBeNull();
});
test("L2 selector bloqueado en solo lectura sin PATCH", async ({ page }) => {
  await mount(page, { readOnly: true });
  await expect(
    page.getByRole("combobox", { name: /^Datos sensibles de adolescentes menores de 16/ })
  ).toBeDisabled();
  expect(
    await page.evaluate(
      () => (window as any).demo.calls.filter((c: any) => c.options.method === "PATCH").length
    )
  ).toBe(0);
});

test("Ruta propuesta: seleccionar consentimiento y guardar persiste el valor", async ({ page }) => {
  await mount(page);
  const route = page.getByRole("combobox", { name: /^Ruta propuesta/ });
  await route.selectOption("consentimiento");
  const body = await savedBody(page);
  expect(body.proposed_authorization_route).toBe("consentimiento");
});
test("Ruta propuesta: seleccionar consentimiento y luego vaciar persiste null", async ({
  page,
}) => {
  await mount(page);
  const route = page.getByRole("combobox", { name: /^Ruta propuesta/ });
  await route.selectOption("consentimiento");
  await route.selectOption("");
  const body = await savedBody(page);
  expect(body.proposed_authorization_route).toBeNull();
});
test("Ruta propuesta: readOnly desactiva el control y no emite PATCH", async ({ page }) => {
  await mount(page, { readOnly: true });
  const route = page.getByRole("combobox", { name: /^Ruta propuesta/ });
  await expect(route).toBeDisabled();
  const patches = await page.evaluate(() =>
    (window as any).demo.calls.filter((c: any) => c.options.method === "PATCH")
  );
  expect(patches).toHaveLength(0);
});

test("L3 desmarcar categoria guarda lista vacia", async ({ page }) => {
  await mount(page);
  await page.getByRole("checkbox", { name: "Identidad", exact: true }).uncheck();
  expect((await savedBody(page)).data_category_codes).toEqual([]);
});
test("L3 restaurar categoria guarda un solo codigo", async ({ page }) => {
  await mount(page);
  const input = page.getByRole("checkbox", { name: "Identidad", exact: true });
  await input.uncheck();
  await input.check();
  expect((await savedBody(page)).data_category_codes).toEqual(["id"]);
});
test("L3 categoria bloqueada en solo lectura sin PATCH", async ({ page }) => {
  await mount(page, { readOnly: true });
  await expect(page.getByRole("checkbox", { name: "Identidad", exact: true })).toBeDisabled();
  expect(
    await page.evaluate(
      () => (window as any).demo.calls.filter((c: any) => c.options.method === "PATCH").length
    )
  ).toBe(0);
});

test("desmarcar Clientes produce data_subject_codes vacío y se guarda", async ({ page }) => {
  await mount(page);
  const clientes = page.getByRole("checkbox", { name: "Clientes", exact: true });
  await expect(clientes).toBeChecked();
  await clientes.uncheck();
  const body = await savedBody(page);
  expect(body.data_subject_codes).toEqual([]);
});
test("desmarcar y volver a marcar Clientes restaura el código en data_subject_codes", async ({
  page,
}) => {
  await mount(page);
  const clientes = page.getByRole("checkbox", { name: "Clientes", exact: true });
  await clientes.uncheck();
  await clientes.check();
  const body = await savedBody(page);
  expect(body.data_subject_codes).toEqual(["clientes"]);
});
test("readOnly true deshabilita el checkbox Clientes y no emite PATCH", async ({ page }) => {
  await mount(page, { readOnly: true });
  const clientes = page.getByRole("checkbox", { name: "Clientes", exact: true });
  await expect(clientes).toBeDisabled();
  await expect(page.getByText("Consulta de solo lectura.")).toBeVisible();
  await expect(page.getByText("Confirmación y activación bloqueadas.")).toBeVisible();
  const calls = await page.evaluate(() =>
    (window as any).demo.calls.filter((c: any) => c.options.method === "PATCH")
  );
  expect(calls).toHaveLength(0);
});
