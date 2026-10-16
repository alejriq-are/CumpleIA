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
    import {ChildEipdHistory} from ${JSON.stringify(path.resolve("components/licitud/ChildEipdHistory.tsx"))};
    import {childEipdApi,validatePolicy,validateResolution,validateReview} from ${JSON.stringify(path.resolve("lib/api/child-eipd.ts"))};
    const id="a0000000-0000-0000-0000-000000000001";
    const scope={organizationId:id,treatmentId:id,assessmentId:id,token:"PRUEBA"};
    const policy={policy:{policy_schema_version:1,policy_reference:"m3-t1-infancia-pruebas-negativas-v1",sources_status:"pendiente",acceptance_status:"pendiente",activation:"deshabilitada",allowed_decisions:["requiere_cambios","no_continuar"],global_policy_identity:{policy_version:1,policy_reference:"PRUEBA: politica global",policy_hash:"d".repeat(64)}},policy_hash:"e".repeat(64),authorizes_action:false,can_confirm:false};
    function resolution(version=1){return {id:"b0000000-0000-0000-0000-"+String(version).padStart(12,"0"),organization_id:id,treatment_id:id,assessment_id:id,version,resolution_binding_version:4,stored_coverage:"contexto_v4",data_kind:"ficticios",document:{schema_version:1,document_reference:"PRUEBA: resolucion "+version,document_version:"1",notes:"PRUEBA: parcial"},context_snapshot:{context_schema_version:4,organization_id:id,treatment_id:id,assessment_id:id,child_adolescent_assessment:{assessment:{schema_version:1}}},document_hash:"a".repeat(64),context_hash:"b".repeat(64),child_material_hash:"c".repeat(64),created_by:id,created_at:"2026-10-16T10:00:00Z",authorizes_action:false,can_confirm:false};}
    function review(row=resolution(),decision="requiere_cambios",n=1){return {...row,id:"c0000000-0000-0000-0000-"+String(n).padStart(12,"0"),response_schema_version:4,resolution_id:row.id,decision,rationale:"PRUEBA: faltan evidencias",review_reference:"PRUEBA: revision",policy_snapshot:policy.policy,policy_hash:policy.policy_hash,review_context_metadata:{metadata_schema_version:3,resolution_binding_version:4,context_schema_version:4,child_coverage:"contexto_v4",document_hash:row.document_hash,context_hash:row.context_hash,child_material_hash:row.child_material_hash,policy_hash:policy.policy_hash}};}
    const demo=window.demo={calls:[],mode:"ok",release:null,status:"borrador",rows:[resolution()],events:[],policy};
    window.fetch=async(url,options)=>{
      demo.calls.push({url,options});
      if(options.method==="POST"){
        if(demo.mode==="wait")await new Promise(resolve=>{demo.release=resolve;});
        if(demo.mode==="unknown")throw new Error("PRUEBA: respuesta incierta");
        if(demo.mode==="denied")return new Response(JSON.stringify({detail:"PRUEBA: permiso"}),{status:403});
        if(demo.mode==="conflict"||demo.mode==="disabled")return new Response(JSON.stringify({detail:{code:demo.mode==="disabled"?"infancia_escritura_ficticia_no_habilitada":"infancia_resolucion_obsoleta"}}),{status:409});
        const body=JSON.parse(options.body);
        if(url.endsWith("/reviews")){
          const row=demo.rows.find(row=>url.includes(row.id));
          const saved={...review(row,body.decision,demo.events.length+1),rationale:body.rationale,review_reference:body.review_reference};
          if(demo.mode==="different-review")saved.decision="no_continuar";
          demo.events.push(saved);return new Response(JSON.stringify(saved),{status:201});
        }
        const saved={...resolution(demo.rows.length+1),document:body.document};demo.rows.push(saved);
        if(demo.mode==="invalid-post")saved.can_confirm=true;
        return new Response(JSON.stringify(saved),{status:201});
      }
      if(url.endsWith("/policy"))return new Response(JSON.stringify(demo.policy),{status:200});
      if(url.endsWith("/reviews"))return new Response(JSON.stringify(demo.events.filter(event=>url.includes(event.resolution_id))),{status:200});
      if(demo.mode==="load-error")return new Response(JSON.stringify({detail:"PRUEBA"}),{status:503});
      return new Response(JSON.stringify(demo.rows),{status:200});
    };
    const load=async()=>({policy:await childEipdApi.policy(scope),resolutions:await childEipdApi.list(scope),status:demo.status});
    const create=draft=>childEipdApi.create(scope,draft),reviews=row=>childEipdApi.reviews(scope,row),saveReview=(row,decision,rationale,reference)=>childEipdApi.review(scope,row,decision,rationale,reference);
    const root=createRoot(document.getElementById("root"));
    window.mount=(options={})=>{demo.status=options.confirmed?"confirmado":"borrador";root.render(React.createElement(ChildEipdHistory,{load,create,reviews,review:saveReview,readOnly:options.readOnly??false}));};
    window.contract=(mutation)=>{const p=structuredClone(policy),r=resolution(),v=review(r);mutation({p,r,v});try{validatePolicy(p);validateResolution(r,scope);validateReview(v,scope,r);return null;}catch(error){return error.status??error.message;}};
    window.api={scope,childEipdApi,resolution};

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
  await expect(
    page.getByText(
      "Política de pruebas: fuentes pendientes, aceptación pendiente y activación deshabilitada."
    )
  ).toBeVisible();
}
async function enable(page: import("@playwright/test").Page) {
  await page
    .getByRole("checkbox", { name: "Declaro que este registro usa datos ficticios" })
    .check();
}
async function select(page: import("@playwright/test").Page) {
  await page.getByRole("button", { name: "Consultar resolución 1", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Resolución 1 consultada" })).toBeVisible();
}
async function fillReview(page: import("@playwright/test").Page) {
  await page
    .getByLabel("Fundamento de la revisión *", { exact: true })
    .fill("PRUEBA: falta evidencia");
  await page.getByLabel("Referencia de la revisión *", { exact: true }).fill("PRUEBA-REV-2");
}
async function posts(page: import("@playwright/test").Page) {
  return page.evaluate(() =>
    (window as any).demo.calls.filter((c: any) => c.options.method === "POST")
  );
}
test("crea sucesor parcial y registra ambas decisiones negativas con identidad del servidor", async ({
  page,
}) => {
  await mount(page);
  await enable(page);
  await page
    .getByLabel("Referencia de la resolución *", { exact: true })
    .fill("  PRUEBA: sucesor 2  ");
  await page
    .getByLabel("Notas de la resolución", { exact: true })
    .fill("PRUEBA: documento parcial");
  await page.getByRole("button", { name: "Registrar resolución ficticia", exact: true }).click();
  await expect(page.getByRole("status")).toContainText("Resolución documental 2 registrada");
  for (const decision of ["requiere_cambios", "no_continuar"]) {
    await fillReview(page);
    await page.getByLabel("Decisión de la revisión").selectOption(decision);
    await page.getByRole("button", { name: "Registrar revisión ficticia", exact: true }).click();
    await expect(page.getByLabel("Fundamento de la revisión *", { exact: true })).toHaveValue("");
  }
  const calls = await posts(page);
  expect(calls).toHaveLength(3);
  expect(JSON.parse(calls[0].options.body)).toEqual({
    data_kind: "ficticios",
    document: {
      schema_version: 1,
      document_reference: "PRUEBA: sucesor 2",
      document_version: null,
      notes: "PRUEBA: documento parcial",
    },
  });
  for (const [i, decision] of ["requiere_cambios", "no_continuar"].entries()) {
    expect(JSON.parse(calls[i + 1].options.body)).toEqual({
      data_kind: "ficticios",
      decision,
      rationale: "PRUEBA: falta evidencia",
      review_reference: "PRUEBA-REV-2",
    });
    expect(calls[i + 1].url).toContain("b0000000-0000-0000-0000-000000000002/reviews");
    expect(calls[i + 1].options.headers["X-Organization-Id"]).toBe(
      "a0000000-0000-0000-0000-000000000001"
    );
  }
  await page.getByRole("button", { name: "Actualizar historial de infancia" }).click();
  await page.getByRole("button", { name: "Consultar resolución 2", exact: true }).click();
  await expect(page.getByText("PRUEBA-REV-2", { exact: true })).toHaveCount(2);
  await expect(
    page.getByText(
      "Esta consulta es histórica: no acredita vigencia del material actual ni concede autorización."
    )
  ).toBeVisible();
  const values = await page
    .getByLabel("Decisión de la revisión")
    .locator("option")
    .evaluateAll((options) => options.map((o) => (o as HTMLOptionElement).value));
  expect(values).toEqual(["requiere_cambios", "no_continuar"]);
});
for (const options of [{ readOnly: true }, { confirmed: true }])
  test(`consulta sin escrituras ${JSON.stringify(options)}`, async ({ page }) => {
    await mount(page, options);
    await select(page);
    await expect(page.getByRole("checkbox")).toBeDisabled();
    await expect(
      page.getByRole("button", { name: "Registrar revisión ficticia", exact: true })
    ).toBeDisabled();
    expect(await posts(page)).toHaveLength(0);
  });
test("requiere declaración ficticia y referencia, conserva borrador al actualizar", async ({
  page,
}) => {
  await mount(page);
  await expect(page.getByLabel("Referencia de la resolución *", { exact: true })).toBeDisabled();
  await enable(page);
  await page.getByRole("button", { name: "Registrar resolución ficticia", exact: true }).click();
  expect(await posts(page)).toHaveLength(0);
  await page.getByLabel("Referencia de la resolución *", { exact: true }).fill("PRUEBA: conservar");
  await select(page);
  await page.getByRole("button", { name: "Actualizar historial de infancia" }).click();
  await expect(page.getByRole("heading", { name: "Resolución 1 consultada" })).toHaveCount(0);
  await expect(page.getByLabel("Referencia de la resolución *", { exact: true })).toHaveValue(
    "PRUEBA: conservar"
  );
});
for (const mode of ["denied", "conflict", "disabled"])
  test(`rechazo ${mode} conserva revisión y no reintenta`, async ({ page }) => {
    await mount(page);
    await enable(page);
    await select(page);
    await fillReview(page);
    await page.evaluate((mode) => ((window as any).demo.mode = mode), mode);
    await page.getByRole("button", { name: "Registrar revisión ficticia", exact: true }).click();
    await expect(page.getByRole("alert")).toContainText(
      mode === "denied" ? "No tienes permiso" : mode === "disabled" ? "deshabilitado" : "cambió"
    );
    await expect(page.getByLabel("Fundamento de la revisión *", { exact: true })).toHaveValue(
      "PRUEBA: falta evidencia"
    );
    expect(await posts(page)).toHaveLength(1);
  });
for (const mode of ["unknown", "invalid-post"])
  test(`resultado incierto ${mode} bloquea repetición incluso tras consultar`, async ({ page }) => {
    await mount(page);
    await enable(page);
    await page
      .getByLabel("Referencia de la resolución *", { exact: true })
      .fill("PRUEBA: incierto");
    await page.evaluate((mode) => ((window as any).demo.mode = mode), mode);
    await page.getByRole("button", { name: "Registrar resolución ficticia", exact: true }).click();
    await expect(page.getByRole("alert")).toContainText("Resultado incierto");
    await expect(
      page.getByRole("button", { name: "Registrar resolución ficticia", exact: true })
    ).toBeDisabled();
    await page.evaluate(() => {
      (window as any).demo.mode = "ok";
      (window as any).demo.rows.forEach((r: any) => (r.can_confirm = false));
    });
    await page.getByRole("button", { name: "Actualizar historial de infancia" }).click();
    await expect(
      page.getByRole("button", { name: "Registrar resolución ficticia", exact: true })
    ).toBeDisabled();
    expect(await posts(page)).toHaveLength(1);
  });
test("bloquea doble registro y cambio de selección mientras persiste", async ({ page }) => {
  await mount(page);
  await enable(page);
  await select(page);
  await fillReview(page);
  await page.evaluate(() => ((window as any).demo.mode = "wait"));
  await page.getByRole("button", { name: "Registrar revisión ficticia", exact: true }).dblclick();
  await expect(
    page.getByRole("button", { name: "Consultar resolución 1", exact: true })
  ).toBeDisabled();
  await expect.poll(async () => (await posts(page)).length).toBe(1);
  await page.evaluate(() => (window as any).demo.release());
  await expect(page.getByRole("status")).toContainText("Revisión negativa registrada");
});
test("carga incompatible impide editar y no expone historial ajeno", async ({ page }) => {
  await page.evaluate(
    () => ((window as any).demo.rows[0].organization_id = "a0000000-0000-0000-0000-000000000099")
  );
  await page.evaluate(() => (window as any).mount());
  await expect(page.getByRole("alert")).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Consultar resolución 1", exact: true })
  ).toHaveCount(0);
  expect(await posts(page)).toHaveLength(0);
});
test("política activa se rechaza antes de mostrar formularios", async ({ page }) => {
  await page.evaluate(() => {
    (window as any).demo.policy.policy.activation = "habilitada";
    (window as any).mount();
  });
  await expect(page.getByRole("alert")).toBeVisible();
  await expect(page.getByRole("checkbox")).toHaveCount(0);
  expect(await posts(page)).toHaveLength(0);
});
test("historial de revisiones incompatibles se rechaza sin seleccionar resolución", async ({
  page,
}) => {
  await page.evaluate(() => {
    const r = (window as any).api.resolution();
    (window as any).demo.events = [{ ...r, resolution_id: r.id, decision: "continuar" }];
  });
  await mount(page);
  await page.getByRole("button", { name: "Consultar resolución 1", exact: true }).click();
  await expect(page.getByRole("alert")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Resolución 1 consultada" })).toHaveCount(0);
});
test("contratos rechazan identidad, cobertura, decisión y hashes cruzados", async ({ page }) => {
  const results = await page.evaluate(() => {
    const contract = (window as any).contract;
    return [
      contract(() => {}),
      contract(({ r }: any) => (r.context_snapshot.assessment_id = "otro")),
      contract(({ r }: any) => (r.stored_coverage = "contexto_v3")),
      contract(({ r }: any) => (r.context_snapshot.child_adolescent_assessment = null)),
      contract(({ v }: any) => (v.decision = "continuar")),
      contract(({ v }: any) => (v.can_confirm = true)),
      contract(({ v }: any) => (v.document_hash = "f".repeat(64))),
      contract(({ v }: any) => (v.review_context_metadata.policy_hash = "f".repeat(64))),
      contract(({ p }: any) => p.policy.allowed_decisions.push("continuar")),
    ];
  });
  expect(results).toEqual([null, 502, 502, 502, 502, 502, 502, 502, 502]);
});
test("cliente rechaza decisión positiva, scope inválido y campos no editables sin HTTP", async ({
  page,
}) => {
  const results = await page.evaluate(async () => {
    const { scope, childEipdApi: a, resolution } = (window as any).api;
    const reject = async (fn: any) => {
      try {
        await fn();
        return null;
      } catch (e) {
        return (e as any).status;
      }
    };
    return [
      await reject(() => a.review(scope, resolution(), "continuar", "PRUEBA", "PRUEBA")),
      await reject(() => a.list({ ...scope, treatmentId: "invalido" })),
      await reject(() =>
        a.create(scope, {
          schema_version: 1,
          document_reference: "PRUEBA",
          document_hash: "f".repeat(64),
        })
      ),
    ];
  });
  expect(results).toEqual([400, 400, 400]);
  expect(await page.evaluate(() => (window as any).demo.calls.length)).toBe(0);
});

test("lista duplicada se rechaza sin mostrar dos versiones del mismo registro", async ({
  page,
}) => {
  await page.evaluate(() => {
    (window as any).demo.rows.push(structuredClone((window as any).demo.rows[0]));
    (window as any).mount();
  });
  await expect(page.getByRole("alert")).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Consultar resolución 1", exact: true })
  ).toHaveCount(0);
});
test("fallo de actualización retira selección y deshabilita registro conservando borrador", async ({
  page,
}) => {
  await mount(page);
  await enable(page);
  await page.getByLabel("Referencia de la resolución *", { exact: true }).fill("PRUEBA: preservar");
  await select(page);
  await page.evaluate(() => ((window as any).demo.mode = "load-error"));
  await page.getByRole("button", { name: "Actualizar historial de infancia" }).click();
  await expect(page.getByRole("alert")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Resolución 1 consultada" })).toHaveCount(0);
  expect(await posts(page)).toHaveLength(0);
  await page.evaluate(() => ((window as any).demo.mode = "ok"));
  await page.getByRole("button", { name: "Actualizar historial de infancia" }).click();
  await expect(page.getByLabel("Referencia de la resolución *", { exact: true })).toHaveValue(
    "PRUEBA: preservar"
  );
});
test("revisión ajena a resolución o metadata antigua se rechaza", async ({ page }) => {
  const results = await page.evaluate(() => {
    const c = (window as any).contract;
    return [
      c(({ v }: any) => (v.resolution_id = "b0000000-0000-0000-0000-000000000099")),
      c(({ v }: any) => (v.review_context_metadata.metadata_schema_version = 2)),
      c(({ v }: any) => (v.data_kind = "reales")),
      c(({ r }: any) => (r.context_snapshot.child_adolescent_assessment = [])),
      c(({ r }: any) => (r.authorizes_action = true)),
    ];
  });
  expect(results).toEqual([502, 502, 502, 502, 502]);
});

test("respuesta negativa distinta de la solicitada se trata como incierta", async ({ page }) => {
  await mount(page);
  await enable(page);
  await select(page);
  await fillReview(page);
  await page.evaluate(() => ((window as any).demo.mode = "different-review"));
  await page.getByRole("button", { name: "Registrar revisión ficticia", exact: true }).click();
  await expect(page.getByRole("alert")).toContainText("Resultado incierto");
  await expect(
    page.getByRole("button", { name: "Registrar revisión ficticia", exact: true })
  ).toBeDisabled();
  expect(await posts(page)).toHaveLength(1);
});
