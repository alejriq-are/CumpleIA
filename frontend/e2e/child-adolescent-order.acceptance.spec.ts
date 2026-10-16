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

const up = (page: import("@playwright/test").Page, n: number) =>
  page.getByRole("button", { name: `Subir evidencia ${n}`, exact: true });
const down = (page: import("@playwright/test").Page, n: number) =>
  page.getByRole("button", { name: `Bajar evidencia ${n}`, exact: true });
async function two(page: import("@playwright/test").Page, options = {}) {
  await mount(page, options);
  if (Object.keys(options).length) return;
  await page.getByRole("button", { name: "Añadir evidencia", exact: true }).click();
  await page.getByLabel("Tipo de evidencia 2", { exact: true }).fill("PRUEBA: segunda");
  await page.getByLabel("Referencia de evidencia 2", { exact: true }).fill("PRUEBA: segunda ref");
}
async function save(page: import("@playwright/test").Page) {
  await page.getByRole("button", { name: "Guardar documento", exact: true }).click();
  await expect(page.getByRole("status")).toHaveText("Documento guardado.");
  return page.evaluate(() =>
    (window as any).demo.calls.filter((c: any) => c.options.method === "PATCH")
  );
}
const originalEvidence = {
  evidence_type: "PRUEBA",
  reference: "PRUEBA: evidencia",
  obtained_on: "2026-10-01",
  notes: "PRUEBA: conservar",
};
const secondEvidence = { evidence_type: "PRUEBA: segunda", reference: "PRUEBA: segunda ref" };
test("aceptacion: subir conserva contenido y orden persistido", async ({ page }) => {
  await two(page);
  await expect(up(page, 1)).toBeDisabled();
  await expect(down(page, 2)).toBeDisabled();
  await up(page, 2).click();
  await expect(page.getByLabel("Referencia de evidencia 1", { exact: true })).toHaveValue(
    "PRUEBA: segunda ref"
  );
  const calls = await save(page);
  expect(calls).toHaveLength(1);
  expect(JSON.parse(calls[0].options.body).child_adolescent_assessment.evidence).toEqual([
    secondEvidence,
    originalEvidence,
  ]);
  await expect(page.getByText("Confirmación y activación bloqueadas.")).toBeVisible();
});
test("aceptacion: bajar conserva todos los metadatos", async ({ page }) => {
  await two(page);
  await down(page, 1).click();
  const calls = await save(page);
  expect(calls).toHaveLength(1);
  expect(JSON.parse(calls[0].options.body).child_adolescent_assessment.evidence).toEqual([
    secondEvidence,
    originalEvidence,
  ]);
});
test("aceptacion: cero y una evidencia no ofrecen movimiento valido", async ({ page }) => {
  await mount(page);
  await expect(up(page, 1)).toBeDisabled();
  await expect(down(page, 1)).toBeDisabled();
  await page.getByRole("button", { name: "Quitar evidencia 1", exact: true }).click();
  await expect(page.getByRole("button", { name: /^(Subir|Bajar) evidencia/ })).toHaveCount(0);
  await page.getByRole("button", { name: "Añadir evidencia", exact: true }).click();
  await expect(up(page, 1)).toBeDisabled();
  await expect(down(page, 1)).toBeDisabled();
});
for (const option of [{ readOnly: true }, { confirmed: true }])
  test(`aceptacion: movimiento bloqueado ${JSON.stringify(option)}`, async ({ page }) => {
    await mount(page, option);
    await expect(up(page, 1)).toBeDisabled();
    await expect(down(page, 1)).toBeDisabled();
    expect(
      await page.evaluate(
        () => (window as any).demo.calls.filter((c: any) => c.options.method === "PATCH").length
      )
    ).toBe(0);
  });
test("aceptacion: busy y uncertain bloquean movimiento", async ({ page }) => {
  await two(page);
  await page.evaluate(() => {
    (window as any).demo.mode = "wait";
  });
  await page.getByRole("button", { name: "Guardar documento", exact: true }).click();
  await expect(up(page, 2)).toBeDisabled();
  await expect(down(page, 1)).toBeDisabled();
  await page.evaluate(() => (window as any).demo.release());
  await expect(page.getByRole("status")).toHaveText("Documento guardado.");
  await expect(up(page, 2)).toBeEnabled();
  await expect(down(page, 1)).toBeEnabled();
  await page.evaluate(() => {
    (window as any).demo.mode = "unknown";
  });
  await page.getByRole("button", { name: "Guardar documento", exact: true }).click();
  await expect(page.getByRole("alert")).toBeVisible();
  await expect(up(page, 2)).toBeDisabled();
  await expect(down(page, 1)).toBeDisabled();
  expect(
    await page.evaluate(
      () => (window as any).demo.calls.filter((c: any) => c.options.method === "PATCH").length
    )
  ).toBe(2);
});
test("aceptacion: 403 permite reordenar y reintentar", async ({ page }) => {
  await two(page);
  await page.evaluate(() => {
    (window as any).demo.mode = "denied";
  });
  await page.getByRole("button", { name: "Guardar documento", exact: true }).click();
  await expect(page.getByRole("alert")).toBeVisible();
  await expect(up(page, 2)).toBeEnabled();
  await up(page, 2).click();
  await page.evaluate(() => {
    (window as any).demo.mode = "ok";
  });
  const calls = await save(page);
  expect(calls).toHaveLength(2);
  expect(JSON.parse(calls[1].options.body).child_adolescent_assessment.evidence).toEqual([
    secondEvidence,
    originalEvidence,
  ]);
  await expect(page.getByRole("alert")).toHaveCount(0);
});
