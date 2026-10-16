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
test("edita documento crudo sin enviar identidad y conserva referencias", async ({ page }) => {
  await mount(page);
  await page.getByLabel("Notas", { exact: true }).fill("PRUEBA: documento editado");
  await page.getByRole("button", { name: "Guardar documento", exact: true }).click();
  await expect(page.getByRole("status")).toHaveText("Documento guardado.");
  const calls = await page.evaluate(() =>
    (window as any).demo.calls.filter((c: any) => c.options.method === "PATCH")
  );
  expect(calls).toHaveLength(1);
  const body = JSON.parse(calls[0].options.body);
  expect(Object.keys(body)).toEqual(["child_adolescent_assessment"]);
  expect(body.child_adolescent_assessment.context_binding).toBeUndefined();
  expect(body.child_adolescent_assessment.notes).toBe("PRUEBA: documento editado");
  expect(body.child_adolescent_assessment.evidence[0].obtained_on).toBe("2026-10-01");
  expect(calls[0].options.headers["X-Organization-Id"]).toBe(
    "a0000000-0000-0000-0000-000000000001"
  );
  await expect(page.getByText("Confirmación y activación bloqueadas.")).toBeVisible();
});
test("retiro envia null y no habilita acciones", async ({ page }) => {
  await mount(page);
  await page.getByRole("button", { name: "Retirar documento del borrador" }).click();
  await expect(page.getByRole("status")).toHaveText("Documento retirado del borrador.");
  const body = await page.evaluate(() =>
    JSON.parse(
      (window as any).demo.calls.find((c: any) => c.options.method === "PATCH").options.body
    )
  );
  expect(body).toEqual({ child_adolescent_assessment: null });
  await expect(page.getByRole("button", { name: "Retirar documento del borrador" })).toBeDisabled();
  await expect(page.getByText("Confirmación y activación bloqueadas.")).toBeVisible();
});
for (const option of [{ readOnly: true }, { confirmed: true }])
  test(`solo lectura ${JSON.stringify(option)}`, async ({ page }) => {
    await mount(page, option);
    await expect(
      page.getByRole("button", { name: "Guardar documento", exact: true })
    ).toBeDisabled();
    await expect(page.getByLabel("Notas", { exact: true })).toBeDisabled();
    await expect(page.getByRole("checkbox", { name: "Niños y niñas", exact: true })).toBeDisabled();
    await expect(
      page.getByRole("button", { name: "Retirar documento del borrador" })
    ).toBeDisabled();
    expect(
      await page.evaluate(
        () => (window as any).demo.calls.filter((c: any) => c.options.method === "PATCH").length
      )
    ).toBe(0);
  });
for (const mode of ["denied", "unknown"])
  test(`no afirma guardado ni pierde cambios ${mode}`, async ({ page }) => {
    await mount(page);
    await page.getByLabel("Notas", { exact: true }).fill("PRUEBA: conservar borrador");
    await page.evaluate((mode) => {
      (window as any).demo.mode = mode;
    }, mode);
    await page.getByRole("button", { name: "Guardar documento", exact: true }).click();
    await expect(page.getByRole("alert")).toContainText("No se confirmó el guardado");
    await expect(page.getByLabel("Notas", { exact: true })).toHaveValue(
      "PRUEBA: conservar borrador"
    );
    await expect(page.getByRole("status")).toHaveCount(0);
    await expect(page.getByText("La consulta incluye infancia en el contexto actual.")).toHaveCount(
      0
    );
    if (mode === "unknown") {
      await expect(
        page.getByRole("button", { name: "Guardar documento", exact: true })
      ).toBeDisabled();
      await expect(page.getByRole("button", { name: "Recargar expediente" })).toBeVisible();
    }
  });
test("separa guardado confirmado de fallo de diagnostico", async ({ page }) => {
  await mount(page);
  await page.evaluate(() => {
    (window as any).demo.mode = "diagnostic-error";
  });
  await page.getByRole("button", { name: "Guardar documento", exact: true }).click();
  await expect(page.getByRole("status")).toHaveText("Documento guardado.");
  await expect(page.getByRole("alert")).toContainText("no se pudo actualizar el diagnóstico");
  await expect(page.getByText("La consulta incluye infancia en el contexto actual.")).toHaveCount(
    0
  );
});
test("bloquea doble envio mientras espera", async ({ page }) => {
  await mount(page);
  await page.evaluate(() => {
    (window as any).demo.mode = "wait";
  });
  await page.getByRole("button", { name: "Guardar documento", exact: true }).click();
  await expect(page.getByRole("button", { name: "Guardar documento", exact: true })).toBeDisabled();
  await expect(page.getByLabel("Notas", { exact: true })).toBeDisabled();
  await expect(page.getByRole("checkbox", { name: "Niños y niñas", exact: true })).toBeDisabled();
  await expect(page.getByRole("button", { name: "Retirar documento del borrador" })).toBeDisabled();
  expect(
    await page.evaluate(
      () => (window as any).demo.calls.filter((c: any) => c.options.method === "PATCH").length
    )
  ).toBe(1);
  await page.evaluate(() => (window as any).demo.release());
  await expect(page.getByRole("status")).toHaveText("Documento guardado.");
  await expect(page.getByLabel("Notas", { exact: true })).toBeEnabled();
  await expect(page.getByRole("checkbox", { name: "Niños y niñas", exact: true })).toBeEnabled();
  await expect(page.getByRole("button", { name: "Retirar documento del borrador" })).toBeEnabled();
  expect(
    await page.evaluate(
      () => (window as any).demo.calls.filter((c: any) => c.options.method === "PATCH").length
    )
  ).toBe(1);
});
test("cliente rechaza autoridad positiva y cobertura incoherente", async ({ page }) => {
  for (const variant of ["authority", "metadata", "coverage", "hash", "gate"]) {
    const rejected = await page.evaluate((variant) => {
      const w = window as any,
        v = w.readyFixture();
      if (variant === "authority") v.eipd_controls_v5.authorizes_action = true;
      if (variant === "metadata") v.eipd_controls_v5.continuar.context_metadata = {};
      if (variant === "coverage") v.eipd_controls_v5.resolution_child_coverage = "contexto_v4";
      if (variant === "hash") v.eipd_controls_v5.context_hash = null;
      if (variant === "gate") v.eipd_controls_v5.no_continuar.issues = [];
      try {
        w.validateChildReadiness(v);
        return false;
      } catch {
        return true;
      }
    }, variant);
    expect(rejected).toBe(true);
  }
});

test("navegacion admite staff y miembros, nunca tenant ajeno", async ({ page }) => {
  const values = await page.evaluate(() => {
    const w = window as any,
      id = "a0000000-0000-0000-0000-000000000001";
    return [
      w.childEditorAccess(id, [], false),
      w.childEditorAccess(id, [], true),
      w.childEditorAccess(id, [{ id, name: "PRUEBA", role: "viewer" }], false),
      w.childEditorAccess(id, [{ id, name: "PRUEBA", role: "editor" }], false),
      w.childEditorAccess("invalid", [], true),
    ];
  });
  expect(values[0]).toBeNull();
  expect(values[1].readOnly).toBe(false);
  expect(values[2].readOnly).toBe(true);
  expect(values[3].readOnly).toBe(false);
  expect(values[4]).toBeNull();
});
