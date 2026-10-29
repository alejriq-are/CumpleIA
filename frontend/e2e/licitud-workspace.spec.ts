import { execFileSync } from "node:child_process";
import { test, expect } from "@playwright/test";
import { mkdtemp, writeFile, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
let directory: string;
let script: string;
let css: string;
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
 import {AssessmentFlow} from ${JSON.stringify(path.resolve("components/licitud/AssessmentFlow.tsx"))};
 import {LegalAssessmentEditor} from ${JSON.stringify(path.resolve("components/licitud/LegalAssessmentEditor.tsx"))};
 const org=${JSON.stringify(org)},tid=${JSON.stringify(treatment)};
 const root=createRoot(document.getElementById("root"));
 const organization={id:org,name:"[FICTICIA] Comercial Piloto Andes SpA",role:"owner"};
 window.demo={calls:[],mode:"ok",rows:[]};
 const detail={special_regimes:{includes_children:true,includes_adolescents:false},id:tid,name:"[FICTICIA] Clientes",purposes:[{id:tid,purpose:"[FICTICIA] Gestion de clientes"}],data_categories:[{category_code:"id",category_name:"Identidad"}],data_subjects:[{category_code:"clientes",category_name:"Clientes"}]};
 if(!${integrated})window.fetch=async(url,opts)=>{
  const method=opts.method??"GET";window.demo.calls.push({url,method,body:opts.body?JSON.parse(opts.body):null});
  const result=value=>new Response(JSON.stringify(value),{status:200});
  if(url.endsWith("/support"))return result(window.demo.support??{schema_version:1,organization_id:org,treatment_id:tid,assessment_id:tid,document_hash:"f".repeat(64),risk_evaluation:null,risk_history:[],annexes:[],can_confirm:false,activation:"deshabilitada"});
  if(url.endsWith("/readiness")&&window.demo.mode==="diagnostic-down")return new Response(JSON.stringify({detail:"PRUEBA diagnóstico no disponible"}),{status:503});
  if(url.endsWith("/readiness"))return result({assessment_id:tid,rat_context_current:true,eipd_resolution:window.demo.rows[0]?.eipd_resolution_assessment?{result:"incompleto",issues:[{field:"risks",code:"analisis_pendiente",category:"incompleto"}]}:null,eipd_controls_v5:null});
  if(url.endsWith("/eipd-child/v4/policy"))return result({policy:{policy_schema_version:1,policy_reference:"m3-t1-infancia-pruebas-negativas-v1",sources_status:"pendiente",acceptance_status:"pendiente",activation:"deshabilitada",allowed_decisions:["requiere_cambios","no_continuar"],global_policy_identity:{policy_version:1,policy_reference:"PRUEBA",policy_hash:"d".repeat(64)}},policy_hash:"e".repeat(64),authorizes_action:false,can_confirm:false});
  if(url.endsWith("/eipd-child/v4/resolutions"))return result([]);
  if(url.includes("/rat/treatments"))return result(url.endsWith("/rat/treatments")?[detail]:detail);
  if(method==="POST"){
   if(window.demo.mode==="denied")return new Response(JSON.stringify({detail:"PRUEBA: sin permiso"}),{status:403});
   if(window.demo.mode==="conflict")return new Response(JSON.stringify({detail:"Ya existe un borrador para esta finalidad"}),{status:409});
   const body=JSON.parse(opts.body);const row={id:tid,organization_id:org,treatment_id:tid,version:1,status:"borrador",purpose_snapshot:detail.purposes[0].purpose,rat_context_snapshot:detail,child_adolescent_assessment:null,eipd_resolution_assessment:null,...body,lia_assessment:null};window.demo.rows=[row];return new Response(JSON.stringify(row),{status:201});
  }
  if(method==="PATCH"){
   if(window.demo.mode==="unknown-save")throw new Error("PRUEBA: respuesta incierta");
   if(window.demo.mode==="denied")return new Response(JSON.stringify({detail:"PRUEBA: sin permiso"}),{status:403});
   const update=JSON.parse(opts.body);
   if(Object.hasOwn(update,"child_adolescent_assessment") && update.child_adolescent_assessment)update.child_adolescent_assessment={assessment:update.child_adolescent_assessment,context_binding:{context_hash:"a".repeat(64),document_hash:"b".repeat(64),binding_version:1}};
   window.demo.rows[0]={...window.demo.rows[0],...update};return result(window.demo.rows[0]);
  }
  if(url.includes("?offset="))return result(window.demo.rows);
  return result(window.demo.rows[0]);
 };
 window.workspace=(role="owner")=>root.render(React.createElement(LicitudWorkspace,{organizaciones:[{...organization,role}],token:async()=>"PRUEBA"}));
 window.flow=(id,readOnly=false)=>root.render(React.createElement(AssessmentFlow,{key:id,organizationId:org,organizationName:organization.name,treatmentId:tid,assessmentId:id,readOnly,token:async()=>"PRUEBA"}));
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
  const source = path.join(directory, "styles.css");
  await writeFile(source, await readFile(path.resolve("app/globals.css"), "utf8"));
  execFileSync(process.execPath, [
    require.resolve("tailwindcss/lib/cli.js"),
    "-i",
    source,
    "-o",
    path.join(directory, "output.css"),
    "--content",
    "components/licitud/**/*.tsx",
  ]);
  css = await readFile(path.join(directory, "output.css"), "utf8");
});
test.afterAll(async () => {
  if (directory) await rm(directory, { recursive: true, force: true });
});

test.beforeEach(async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 749 });
  if (integrated) await page.goto(process.env.CUMPLEIA_UI_API + "/__licitud-isolated-test");
  else await page.setContent('<div id="root"></div>');
  await page.addScriptTag({ content: "window.process={env:{}};" });
  await page.addStyleTag({ content: css });
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
  await expect(page.getByRole("status")).toContainText(
    "Los cambios se guardaron correctamente en el servidor"
  );
  await expect(page.getByText("Cambios sin guardar.", { exact: false })).toHaveCount(0);
  await page.evaluate(() => (window as any).workspace());
  await expect(page.getByLabel("Tratamiento del RAT", { exact: true })).toBeVisible();
  await page.getByLabel("Tratamiento del RAT").selectOption(treatment);
  await expect(page.getByRole("link", { name: /versión 1/ })).toBeVisible();
  await page.evaluate((id) => (window as any).editor(id), id);
  await expect(page.getByLabel("Análisis de necesidad", { exact: true }).first()).toHaveValue(
    "[FICTICIA] Necesidad de prueba"
  );
  await page.evaluate((id) => (window as any).flow(id), id);
  await page.getByRole("tab", { name: "Completar datos", exact: true }).click();
  await page.getByRole("button", { name: "2. Base y fundamento", exact: true }).click();
  await expect(page.getByLabel("Análisis de necesidad", { exact: true }).first()).toHaveValue(
    "[FICTICIA] Necesidad de prueba"
  );
  await page
    .getByLabel("Fundamento", { exact: true })
    .fill("[FICTICIA] Cambio conservado entre pestañas");
  await page.getByRole("tab", { name: "Revisar documentos", exact: true }).click();
  await expect(
    page.getByText("Hay cambios pendientes en Completar datos.", { exact: false })
  ).toBeVisible();
  await expect(page.getByLabel("Fundamento", { exact: true })).toBeHidden();
  await page.getByRole("tab", { name: "Completar datos", exact: true }).click();
  await page.getByRole("button", { name: "2. Base y fundamento", exact: true }).click();
  await expect(page.getByLabel("Fundamento", { exact: true })).toHaveValue(
    "[FICTICIA] Cambio conservado entre pestañas"
  );
  await page.getByRole("button", { name: "Guardar borrador", exact: true }).click();
  await expect(page.getByText("Borrador guardado.", { exact: false })).toBeVisible();
  await expect(page.getByText("Guarda primero los cambios de base", { exact: false })).toHaveCount(
    0
  );
  await page.getByRole("tab", { name: "Historial y descargas", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "Consultar expediente documental", exact: true })
  ).toBeVisible();
  await page.getByRole("tab", { name: "Completar datos", exact: true }).click();
  await page.getByRole("button", { name: "Documentar EIPD", exact: true }).click();
  await page
    .getByLabel("Referencia del documento EIPD", { exact: true })
    .fill("SIMULADA-EIPD-RECORRIDO-001");
  await page.getByRole("button", { name: "3. Describir riesgos", exact: true }).click();
  await page.getByRole("button", { name: "Añadir riesgos", exact: true }).click();
  await page.getByLabel("Riesgos 1 — Identificador del riesgo", { exact: true }).fill("R1");
  await page
    .getByLabel("Riesgos 1 — Descripción", { exact: true })
    .fill("[FICTICIA] Acceso indebido de ensayo");
  await page.getByRole("button", { name: "5. Medidas de mitigación", exact: true }).click();
  await page.getByRole("button", { name: "Añadir medidas", exact: true }).click();
  await page.getByLabel("Medidas 1 — Identificador de la medida", { exact: true }).fill("M1");
  await page
    .getByLabel("Medidas 1 — Descripción", { exact: true })
    .fill("[FICTICIA] Control de accesos");
  await page.getByLabel("Medidas 1 — Riesgos asociados", { exact: true }).fill("R1");
  await page.getByRole("button", { name: "7. Riesgo residual y seguimiento", exact: true }).click();
  await page
    .getByRole("region", { name: "Documento EIPD en borrador", exact: true })
    .getByLabel("Nivel del riesgo residual", { exact: true })
    .selectOption("sin_resolver");
  await page
    .getByRole("region", { name: "Documento EIPD en borrador", exact: true })
    .getByLabel("Plan de seguimiento", { exact: true })
    .fill("[FICTICIA] Revisar eficacia y evidencias");
  await page.getByRole("button", { name: "Guardar borrador EIPD", exact: true }).click();
  await expect(page.getByText("Borrador EIPD guardado en servidor.", { exact: false }))
    .toBeVisible()
    .catch(async (cause) => {
      throw new Error(
        `${cause.message}\nAvisos del guardado ficticio: ${(await page.getByRole("alert").allTextContents()).join("; ")}`
      );
    });
  const eipdRegion = page.getByRole("region", { name: "Documento EIPD en borrador", exact: true });
  const success = eipdRegion.getByRole("status");
  await expect(success).toContainText("Borrador EIPD guardado en servidor");
  const saveBox = await eipdRegion
    .getByRole("button", { name: "Guardar borrador EIPD", exact: true })
    .boundingBox();
  const successBox = await success.boundingBox();
  expect(Math.abs(successBox!.y - saveBox!.y)).toBeLessThan(250);
  await eipdRegion
    .getByLabel("Nombre de la edición (texto libre)", { exact: true })
    .fill("CAMBIO-SIN-GUARDAR");
  await expect(success).toHaveCount(0);
  await expect(eipdRegion.getByText("EIPD: cambios sin guardar", { exact: false })).toBeVisible();
  await page.evaluate(() => (window as any).workspace());
  await expect(page.getByLabel("Tratamiento del RAT", { exact: true })).toBeVisible();
  await page.evaluate((id) => (window as any).flow(id), id);
  await page.getByRole("tab", { name: "Completar datos", exact: true }).click();
  await page.getByRole("button", { name: "Documentar EIPD", exact: true }).click();
  await expect(page.getByLabel("Referencia del documento EIPD", { exact: true })).toHaveValue(
    "SIMULADA-EIPD-RECORRIDO-001"
  );
  await page.getByRole("button", { name: "3. Describir riesgos", exact: true }).click();
  await expect(page.getByLabel("Riesgos 1 — Descripción", { exact: true })).toHaveValue(
    "[FICTICIA] Acceso indebido de ensayo"
  );
  await page.getByRole("button", { name: "5. Medidas de mitigación", exact: true }).click();
  await expect(page.getByLabel("Medidas 1 — Riesgos asociados", { exact: true })).toHaveValue("R1");
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(
    true
  );
  if (process.env.CUMPLEIA_EIPD_MOBILE)
    await page.screenshot({ path: process.env.CUMPLEIA_EIPD_MOBILE, fullPage: true });
  if (process.env.CUMPLEIA_EIPD_DESKTOP) {
    await page.setViewportSize({ width: 1280, height: 900 });
    await page.screenshot({ path: process.env.CUMPLEIA_EIPD_DESKTOP, fullPage: true });
  }

  await page.getByRole("tab", { name: "Revisar documentos", exact: true }).click();
  await expect(
    page.getByRole("region", { name: "Borrador EIPD guardado para consulta", exact: true })
  ).toBeVisible();
  await expect(
    page.getByRole("region", { name: "Borrador EIPD guardado para consulta", exact: true })
  ).toContainText("borrador documental");
  if (integrated) {
    await page.getByRole("tab", { name: "Completar datos", exact: true }).click();
    await page.getByRole("button", { name: "4. Valorar riesgos", exact: true }).click();
    const support = page.getByRole("region", {
      name: "Valoración y anexos de la evaluación",
      exact: true,
    });
    await support
      .getByLabel("R1 — Daño potencial a las personas", { exact: true })
      .fill("[FICTICIA] Exposición y pérdida de control");
    await support
      .getByLabel("R1 — Inherente, antes de controles — Probabilidad", { exact: true })
      .selectOption("2");
    await support
      .getByLabel("R1 — Inherente, antes de controles — Impacto", { exact: true })
      .selectOption("3");
    await support
      .getByLabel("R1 — Inherente, antes de controles — Fundamento", { exact: true })
      .fill("[FICTICIA] Escenario plausible y daño grave");
    await support
      .getByRole("button", { name: "Guardar valoración de riesgos", exact: true })
      .click();
    await expect(support.getByRole("status")).toContainText("Valoración guardada");
    await page.getByRole("button", { name: "Anexos de respaldo", exact: true }).click();
    await support
      .getByLabel("Referencia del anexo (SIMULADA-)", { exact: true })
      .fill("SIMULADA-ANEXO-R1");
    await support
      .getByLabel("Descripción del anexo", { exact: true })
      .fill("[FICTICIA] Matriz de acceso para R1");
    await support.getByText("Vínculos opcionales con riesgos y medidas", { exact: true }).click();
    await support
      .getByLabel("Códigos de riesgos vinculados (opcional; ejemplo: R1)", { exact: true })
      .fill("R1");
    await support.getByLabel("Archivo ficticio PDF o TXT", { exact: true }).setInputFiles({
      name: "matriz-ensayo.txt",
      mimeType: "text/plain",
      buffer: Buffer.from("[FICTICIA] Acceso simulado"),
    });
    await support
      .getByText("Confirmo que el archivo y sus datos son ficticios", { exact: true })
      .check();
    await support.getByRole("button", { name: "Guardar anexo ficticio", exact: true }).click();
    await expect(support.getByRole("status")).toContainText("Anexo ficticio guardado");
    const download = page.waitForEvent("download");
    await support
      .getByRole("button", { name: "Descargar SIMULADA-ANEXO-R1 versión 1", exact: true })
      .click();
    expect((await download).suggestedFilename()).toBe("matriz-ensayo.txt");
    await page.getByRole("tab", { name: "Revisar documentos", exact: true }).click();
    await page.getByText("Contenido del documento guardado", { exact: true }).first().click();
    await expect(
      page
        .getByRole("table", { name: "Valoración cualitativa de R1", exact: true })
        .getByText("Alto", { exact: true })
    ).toBeVisible();
    await expect(
      page.getByRole("region", { name: "Alcance RAT guardado", exact: true })
    ).toBeVisible();
    await expect(
      page.getByRole("region", { name: "Evaluación de licitud guardada", exact: true })
    ).toBeVisible();
  }
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
  await page.getByLabel("Análisis de necesidad", { exact: true }).first().fill("[FICTICIA] Nuevo");
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

test("recorrido integrado conserva ambos borradores, refresca consultas y exige lectura de preparacion", async ({
  page,
}) => {
  test.skip(integrated, "Control de fallos y solicitudes de componentes con fixtures");
  await draft(page);
  await expect(page.getByRole("status")).toContainText("Borrador creado");
  await page.evaluate((id) => (window as any).flow(id), treatment);
  await expect(page.getByRole("tab", { name: "Resumen y siguientes pasos" })).toHaveAttribute(
    "aria-selected",
    "true"
  );
  await page.getByRole("tab", { name: "Completar datos", exact: true }).click();
  await page.getByRole("button", { name: "2. Base y fundamento", exact: true }).click();
  await page.getByRole("button", { name: "3. Infancia", exact: true }).click();
  await page
    .getByLabel("Análisis de edad y alcance", { exact: true })
    .fill("[FICTICIA] Cinco participantes");
  await page.getByRole("button", { name: "2. Base y fundamento", exact: true }).click();
  await page.getByLabel("Fundamento", { exact: true }).fill("[FICTICIA] Fundamento pendiente");
  await page.getByRole("tab", { name: "Revisar documentos", exact: true }).click();
  await expect(page.getByLabel("Análisis de edad y alcance", { exact: true })).toBeHidden();
  await page.getByRole("tab", { name: "Completar datos", exact: true }).click();
  await page.getByRole("button", { name: "2. Base y fundamento", exact: true }).click();
  await expect(page.getByLabel("Análisis de edad y alcance", { exact: true })).toHaveValue(
    "[FICTICIA] Cinco participantes"
  );
  await page.getByRole("button", { name: "Guardar borrador", exact: true }).click();
  await expect(page.getByText("Borrador guardado.", { exact: false })).toBeVisible();
  await expect(page.getByLabel("Análisis de edad y alcance", { exact: true })).toHaveValue(
    "[FICTICIA] Cinco participantes"
  );
  await page
    .getByRole("button", { name: "Preparar nueva versión documental de infancia", exact: true })
    .first()
    .click();
  await expect(
    page.getByText("Guarda primero los cambios de base", { exact: false })
  ).toBeVisible();
  await page.getByRole("button", { name: "3. Infancia", exact: true }).click();
  await page.getByRole("button", { name: "Guardar documento", exact: true }).click();
  await expect(page.getByText("Documento guardado.", { exact: true })).toBeVisible();
  await expect(page.getByLabel("Análisis de edad y alcance", { exact: true })).toHaveValue(
    "[FICTICIA] Cinco participantes"
  );
  await expect(page.getByText("Guarda primero los cambios de base", { exact: false })).toHaveCount(
    0
  );
  await page
    .getByRole("button", { name: "Preparar nueva versión documental de infancia", exact: true })
    .first()
    .click();
  await page
    .getByRole("checkbox", { name: "Declaro que este registro usa datos ficticios" })
    .check();
  await page
    .getByLabel("Referencia del documento de infancia *", { exact: true })
    .fill("SIMULADA-RECORRIDO-001");
  await page
    .getByRole("button", { name: "Ver vista previa de la versión por registrar", exact: true })
    .last()
    .click();
  const record = page.getByRole("button", {
    name: "Registrar nueva versión documental ficticia",
    exact: true,
  });
  await expect(record).toBeDisabled();
  const check = page.getByRole("checkbox", {
    name: "He revisado el contenido como responsable ficticio del ensayo",
  });
  await check.check();
  await expect(record).toBeEnabled();
  await page
    .getByLabel("Notas del documento de infancia", { exact: true })
    .fill("[FICTICIA] Nota posterior");
  await expect(check).not.toBeChecked();
  await expect(record).toBeDisabled();
  if (process.env.CUMPLEIA_FLOW_MOBILE)
    await page.screenshot({ path: process.env.CUMPLEIA_FLOW_MOBILE, fullPage: true });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(
    true
  );
  await page.getByRole("tab", { name: "Resumen y siguientes pasos", exact: true }).focus();
  await page.keyboard.press("End");
  await expect(page.getByRole("tab", { name: "Historial y descargas", exact: true })).toBeFocused();
  const calls = await page.evaluate(() => (window as any).demo.calls);
  expect(calls.filter((c: any) => c.url.endsWith("/readiness")).length).toBeGreaterThan(2);
  expect(
    calls.filter((c: any) => c.url.endsWith("/eipd-child/v4/resolutions") && c.method === "POST")
  ).toHaveLength(0);
});

test("recorrido de solo lectura y rechazo de guardado mantienen barreras y contenido", async ({
  page,
}) => {
  test.skip(integrated, "Fixture de permiso y error controlados");
  await draft(page);
  await expect(page.getByRole("status")).toContainText("Borrador creado");
  await page.evaluate((id) => (window as any).flow(id), treatment);
  await page.getByRole("tab", { name: "Completar datos", exact: true }).click();
  await page.getByRole("button", { name: "2. Base y fundamento", exact: true }).click();
  await page.getByLabel("Fundamento", { exact: true }).fill("[FICTICIA] No perder ante rechazo");
  await page.evaluate(() => ((window as any).demo.mode = "denied"));
  await page.getByRole("button", { name: "Guardar borrador", exact: true }).click();
  await expect(page.getByRole("alert").filter({ hasText: "sin permiso" })).toBeVisible();
  await page.getByRole("tab", { name: "Historial y descargas", exact: true }).click();
  await page.getByRole("tab", { name: "Completar datos", exact: true }).click();
  await page.getByRole("button", { name: "2. Base y fundamento", exact: true }).click();
  await expect(page.getByLabel("Fundamento", { exact: true })).toHaveValue(
    "[FICTICIA] No perder ante rechazo"
  );
  await page.evaluate((id) => (window as any).flow(id, true), treatment);
  await expect(page.getByLabel("Fundamento", { exact: true })).toBeDisabled();
  await expect(page.getByRole("button", { name: "Guardar borrador", exact: true })).toHaveCount(0);
  await expect(page.getByRole("button", { name: /Confirmar|Activar/ })).toHaveCount(0);
});

test("borrador EIPD conserva errores, bloquea repeticion incierta y no envia metadata del servidor", async ({
  page,
}) => {
  test.skip(integrated, "Fallos controlados");
  await draft(page);
  await expect(page.getByRole("status")).toContainText("Borrador creado");
  await page.evaluate((id) => {
    (window as any).demo.rows[0].eipd_resolution_assessment = {
      schema_version: 1,
      document_reference: "SIMULADA-PREVIA",
      context_binding: { binding_version: 1, context_hash: "a".repeat(64) },
    };
    (window as any).flow(id);
  }, treatment);
  await page.getByRole("tab", { name: "Completar datos", exact: true }).click();
  await page.getByRole("button", { name: "Documentar EIPD", exact: true }).click();
  await page
    .getByLabel("Referencia del documento EIPD", { exact: true })
    .fill("SIMULADA-EIPD-EDITADA");
  await page.evaluate(() => ((window as any).demo.mode = "denied"));
  await page.getByRole("button", { name: "Guardar borrador EIPD", exact: true }).click();
  await expect(
    page.getByRole("alert").filter({ hasText: "Guardado EIPD rechazado" })
  ).toBeVisible();
  await expect(page.getByLabel("Referencia del documento EIPD", { exact: true })).toHaveValue(
    "SIMULADA-EIPD-EDITADA"
  );
  await page.getByRole("tab", { name: "Historial y descargas", exact: true }).click();
  await page.getByRole("tab", { name: "Completar datos", exact: true }).click();
  await expect(page.getByLabel("Referencia del documento EIPD", { exact: true })).toHaveValue(
    "SIMULADA-EIPD-EDITADA"
  );
  const calls = await page.evaluate(() =>
    (window as any).demo.calls.filter((c: any) => c.method === "PATCH")
  );
  expect(calls).toHaveLength(1);
  expect(calls[0].body.eipd_resolution_assessment).not.toHaveProperty("context_binding");
  await page.evaluate(() => ((window as any).demo.mode = "unknown-save"));
  await page.getByRole("button", { name: "Guardar borrador EIPD", exact: true }).click();
  await expect(
    page.getByRole("alert").filter({ hasText: "Resultado incierto del guardado EIPD" })
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Guardar borrador EIPD", exact: true })
  ).toBeDisabled();
});

test("documento EIPD incompatible no se reemplaza y consulta no permite guardar", async ({
  page,
}) => {
  test.skip(integrated, "Fixture de incompatibilidad y permiso");
  await draft(page);
  await expect(page.getByRole("status")).toContainText("Borrador creado");
  await page.evaluate((id) => {
    (window as any).demo.rows[0].eipd_resolution_assessment = {
      schema_version: 1,
      campo_futuro: "No perder",
    };
    (window as any).flow(id);
  }, treatment);
  await page.getByRole("tab", { name: "Completar datos", exact: true }).click();
  await page.getByRole("button", { name: "Documentar EIPD", exact: true }).click();
  await expect(
    page.getByRole("alert").filter({ hasText: "No se pudo cargar un documento EIPD válido" })
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Guardar borrador EIPD", exact: true })
  ).toHaveCount(0);
  await page.evaluate(() => (window as any).workspace());
  await expect(page.getByLabel("Tratamiento del RAT", { exact: true })).toBeVisible();
  await page.evaluate((id) => {
    (window as any).demo.rows[0].eipd_resolution_assessment = null;
    (window as any).flow(id, true);
  }, treatment);
  await page.getByRole("tab", { name: "Completar datos", exact: true }).click();
  await page.getByRole("button", { name: "Documentar EIPD", exact: true }).click();
  await expect(page.getByLabel("Referencia del documento EIPD", { exact: true })).toBeDisabled();
  await expect(
    page.getByRole("button", { name: "Guardar borrador EIPD", exact: true })
  ).toHaveCount(0);
});

for (const mode of ["adultos", "infancia", "error"] as const) {
  test(`revision muestra infancia solo si aplica y conserva errores: ${mode}`, async ({ page }) => {
    test.skip(integrated, "Variantes de alcance e historial aisladas del servidor");
    await draft(page);
    await expect(page.getByRole("status")).toContainText("Borrador creado");
    await page.evaluate(
      ({ tid, mode }) => {
        (window as any).demo.rows[0].rat_context_snapshot.special_regimes.includes_children =
          mode === "infancia";
        if (mode === "error") {
          const previous = window.fetch;
          window.fetch = (async (url: any, opts: any) =>
            String(url).endsWith("/eipd-child/v4/resolutions")
              ? new Response(JSON.stringify({ detail: "PRUEBA: historial no disponible" }), {
                  status: 503,
                })
              : previous(url, opts)) as typeof fetch;
        }
        (window as any).flow(tid);
      },
      { tid: treatment, mode }
    );
    await page.getByRole("tab", { name: "Revisar documentos", exact: true }).click();
    const history = page.getByRole("heading", {
      name: "Versiones registradas y revisiones de infancia",
      exact: true,
    });
    if (mode === "adultos") {
      await expect(
        page.getByText("No hay un documento EIPD guardado.", {
          exact: false,
        })
      ).toBeVisible();
      await expect(history).toBeHidden();
      await expect(
        page.getByText("Elige una resolución y lee su contenido.", { exact: false })
      ).toBeHidden();
      await page.getByRole("tab", { name: "Completar datos", exact: true }).click();
      await page.getByRole("button", { name: "Documentar EIPD", exact: true }).click();
      await page
        .getByLabel("Referencia del documento EIPD", { exact: true })
        .fill("SIMULADA-EIPD-ADULTOS-001");
      await page.getByRole("button", { name: "Guardar borrador EIPD", exact: true }).click();
      await expect(
        page.getByText("Borrador EIPD guardado en servidor.", { exact: false })
      ).toBeVisible();
      await page.getByRole("tab", { name: "Revisar documentos", exact: true }).click();
      await expect(
        page.getByRole("region", { name: "Borrador EIPD guardado para consulta", exact: true })
      ).toBeVisible();
      await expect(
        page.getByText("El borrador EIPD general está disponible para consulta.", { exact: false })
      ).toBeVisible();
      await expect(history).toBeHidden();
      await expect(
        page.getByText("El registro de revisiones disponible abajo", { exact: false })
      ).toBeHidden();
    } else {
      await expect(history).toBeVisible();
      if (mode === "error")
        await expect(page.locator('[id$="-child-history"]').getByRole("alert")).toBeVisible();
      else
        await expect(
          page.getByText("No hay versiones del documento de infancia registradas.", { exact: true })
        ).toBeVisible();
    }
  });
}

test("fuentes vacias no aparecen al navegar y borrador incompleto conserva datos parciales", async ({
  page,
}) => {
  test.skip(integrated, "Variantes aisladas");
  await draft(page);
  const editor = page.getByRole("region", { name: "Documento EIPD en borrador", exact: true });
  await expect(page.getByRole("status")).toContainText("Borrador creado");
  await page.evaluate((tid) => (window as any).flow(tid), treatment);
  await page.getByRole("tab", { name: "Completar datos", exact: true }).click();
  await page.getByRole("button", { name: "Documentar EIPD", exact: true }).click();
  await page.getByRole("button", { name: "6. Fuentes y evidencias", exact: true }).click();
  await expect(
    editor.getByLabel("Fuentes del documento — Fuentes 1 — Referencia de la fuente", {
      exact: true,
    })
  ).toHaveCount(0);
  await expect(
    editor.getByRole("button", { name: "Añadir consulta a la autoridad — evidencias", exact: true })
  ).toBeHidden();
  await editor
    .getByLabel("Consulta a la autoridad — Estado de consulta", { exact: true })
    .selectOption("en_curso");
  await expect(
    editor.getByRole("button", { name: "Añadir consulta a la autoridad — evidencias", exact: true })
  ).toBeVisible();
  await editor
    .getByLabel("Consulta a la autoridad — Referencia de consulta", { exact: true })
    .fill("SIMULADA-CONSULTA-001");
  await editor
    .getByLabel("Consulta a la autoridad — Estado de consulta", { exact: true })
    .selectOption("no_solicitada");
  await expect(
    editor.getByLabel("Consulta a la autoridad — Referencia de consulta", { exact: true })
  ).toHaveValue("SIMULADA-CONSULTA-001");
  await page
    .getByRole("button", { name: "Añadir fuentes del documento — evidencias", exact: true })
    .click();
  await page.getByRole("button", { name: "Guardar borrador EIPD", exact: true }).click();
  await expect(
    page.getByText("Borrador EIPD guardado en servidor.", { exact: false })
  ).toBeVisible();
  const saved = await page.evaluate(() => (window as any).demo.rows[0].eipd_resolution_assessment);
  expect(saved.official_sources.evidence).toEqual([]);
  expect(saved.agency_consultation.consultation_reference).toBe("SIMULADA-CONSULTA-001");
  await page
    .getByRole("button", { name: "Añadir fuentes del documento — evidencias", exact: true })
    .click();
  await editor
    .getByLabel("Fuentes del documento — Evidencias 1 — Referencia", { exact: true })
    .fill("SIMULADA-PARCIAL-001");
  await page.getByRole("button", { name: "Guardar borrador EIPD", exact: true }).click();
  await expect(page.getByRole("alert")).toContainText("rechazado");
  await expect(
    editor.getByLabel("Fuentes del documento — Evidencias 1 — Referencia", { exact: true })
  ).toHaveValue("SIMULADA-PARCIAL-001");
});

test("conflicto conocido conserva formulario y permite abrir borrador sin sugerir reintento incierto", async ({
  page,
}) => {
  test.skip(integrated, "Escenario de interfaz con fixtures ficticios");
  await draft(page);
  await expect(page.getByRole("status")).toContainText("Borrador creado");
  await page.evaluate(() => {
    (window as any).demo.mode = "conflict";
  });
  await page.getByLabel("Confirmo que ingreso únicamente datos ficticios de prueba").check();
  await page.getByRole("button", { name: "Crear borrador", exact: true }).click();
  const alert = page.getByRole("alert");
  await expect(alert).toContainText("No se creó otra evaluación");
  await expect(alert).not.toContainText("Si no recibiste respuesta");
  await expect(page.getByRole("link", { name: /Abrir borrador existente:/ })).toHaveAttribute(
    "href",
    new RegExp(`/dashboard/licitud/${treatment}/`)
  );
  await expect(page.getByLabel("Fundamento", { exact: true })).toHaveValue(
    "[FICTICIA] Prueba de recorrido"
  );
  await expect(alert).toBeFocused();
});
test("paso 4 de EIPD conserva borradores al navegar y el aviso de base precede Guardar", async ({
  page,
}) => {
  test.skip(integrated, "Escenario de interfaz con fixtures ficticios");
  await draft(page);
  await page.evaluate(() => {
    const d = (window as any).demo;
    d.rows[0].rat_context_snapshot.special_regimes = {
      includes_children: false,
      includes_adolescents: false,
    };
  });
  await page.evaluate((id) => (window as any).flow(id), treatment);
  await page.getByRole("tab", { name: "Completar datos", exact: true }).click();
  await expect(page.getByRole("button", { name: "Valorar riesgos", exact: true })).toHaveCount(0);
  await page.getByRole("button", { name: "2. Base y fundamento", exact: true }).click();
  await page.getByLabel("Fundamento", { exact: true }).fill("[FICTICIA] Cambio pendiente");
  const notice = page.getByRole("note").filter({ hasText: "Cambios sin guardar" });
  expect(
    await notice.evaluate((el) => el.parentElement?.nextElementSibling?.textContent)
  ).toContain("Guardar borrador");
  await page.getByRole("button", { name: "Documentar EIPD", exact: true }).click();
  await page
    .getByLabel("Referencia del documento EIPD", { exact: true })
    .fill("SIMULADA-PENDIENTE");
  await page.getByRole("button", { name: "4. Valorar riesgos", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Valorar riesgos para las personas" })
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Guardar valoración de riesgos", exact: true })
  ).toBeDisabled();
  await expect(
    page.getByRole("button", { name: "5. Medidas de mitigación", exact: true })
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "6. Fuentes y evidencias", exact: true })
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "7. Riesgo residual y seguimiento", exact: true })
  ).toBeVisible();
  await page
    .getByRole("button", { name: "1. Tratamiento y alcance de la EIPD", exact: true })
    .click();
  await expect(page.getByLabel("Referencia del documento EIPD", { exact: true })).toHaveValue(
    "SIMULADA-PENDIENTE"
  );
  await page.getByRole("button", { name: "2. Base y fundamento", exact: true }).click();
  await expect(page.getByLabel("Fundamento", { exact: true })).toHaveValue(
    "[FICTICIA] Cambio pendiente"
  );
  await page.getByRole("tab", { name: "Resumen y siguientes pasos", exact: true }).click();
  await expect(page.getByText(/contrato documental EIPD de infancia/)).toHaveCount(0);
});

test("valoración y anexo pendientes se conservan entre pasos EIPD y pestañas", async ({ page }) => {
  test.skip(integrated, "Escenario de interfaz con fixtures ficticios");
  await draft(page);
  await expect(page.getByRole("status")).toContainText("Borrador creado");
  await page.evaluate(() => {
    const d = (window as any).demo;
    d.rows[0].eipd_resolution_assessment = {
      schema_version: 1,
      document_reference: "SIMULADA-NAVEGACION",
      risks: [{ risk_id: "R1" }],
      measures: [{ measure_id: "M1", risk_ids: ["R1"] }],
    };
    d.rows[0].rat_context_snapshot.special_regimes = {
      includes_children: false,
      includes_adolescents: false,
    };
  });
  await page.evaluate((id) => (window as any).flow(id), treatment);
  await page.getByRole("tab", { name: "Completar datos", exact: true }).click();
  await page.getByRole("button", { name: "Documentar EIPD", exact: true }).click();
  await page.getByRole("button", { name: "4. Valorar riesgos", exact: true }).click();
  const harm = page.getByLabel("R1 — Daño potencial a las personas", { exact: true });
  await harm.fill("[FICTICIA] Borrador de valoración conservado");
  await page.getByRole("button", { name: "5. Medidas de mitigación", exact: true }).click();
  await page.getByRole("button", { name: "Anexos de respaldo", exact: true }).click();
  await page
    .getByLabel("Descripción del anexo", { exact: true })
    .fill("[FICTICIA] Anexo pendiente");
  await page.getByRole("tab", { name: "Revisar documentos", exact: true }).click();
  await page.getByRole("tab", { name: "Completar datos", exact: true }).click();
  await page.getByRole("button", { name: "Documentar EIPD", exact: true }).click();
  await page.getByRole("button", { name: "4. Valorar riesgos", exact: true }).click();
  await expect(harm).toHaveValue("[FICTICIA] Borrador de valoración conservado");
  await page.getByRole("button", { name: "Anexos de respaldo", exact: true }).click();
  await expect(page.getByLabel("Descripción del anexo", { exact: true })).toHaveValue(
    "[FICTICIA] Anexo pendiente"
  );
  expect(
    await page.evaluate(
      () =>
        (window as any).demo.calls.filter(
          (c: any) => c.method === "POST" && /risk-evaluations|annexes/.test(c.url)
        ).length
    )
  ).toBe(0);
});

test("guardado confirmado permanece visible aunque falle el diagnóstico posterior", async ({
  page,
}) => {
  test.skip(integrated, "Fallo controlado de diagnóstico");
  await draft(page);
  await expect(page.getByRole("status")).toContainText("Borrador creado");
  await page.evaluate((id) => (window as any).flow(id), treatment);
  await page.getByRole("tab", { name: "Completar datos", exact: true }).click();
  await page.getByRole("button", { name: "Documentar EIPD", exact: true }).click();
  await page
    .getByLabel("Referencia del documento EIPD", { exact: true })
    .fill("SIMULADA-DIAGNOSTICO");
  await page.evaluate(() => ((window as any).demo.mode = "diagnostic-down"));
  await page.getByRole("button", { name: "Guardar borrador EIPD", exact: true }).click();
  const region = page.getByRole("region", { name: "Documento EIPD en borrador", exact: true });
  await expect(region.getByRole("status")).toContainText("Borrador EIPD guardado en servidor");
  await expect(region.getByRole("alert")).toContainText(
    "se guardó, pero el diagnóstico no está disponible"
  );
  expect(
    await page.evaluate(
      () => (window as any).demo.rows[0].eipd_resolution_assessment.document_reference
    )
  ).toBe("SIMULADA-DIAGNOSTICO");
});

for (const basis of [null, "consentimiento_art12", "interes_legitimo_art13d"]) {
  test(`título de consulta menciona LIA solo para interés legítimo: ${basis}`, async ({ page }) => {
    test.skip(integrated, "Escenario de interfaz con fixtures ficticios");
    await draft(page);
    await expect(page.getByRole("status")).toContainText("Borrador creado");
    await page.evaluate((basis) => {
      (window as any).demo.rows[0].legal_basis = basis;
    }, basis);
    await page.evaluate((id) => (window as any).flow(id), treatment);
    await page.getByRole("tab", { name: "Revisar documentos", exact: true }).click();
    const region = page.getByRole("region", {
      name: "Evaluación de licitud guardada",
      exact: true,
    });
    const active = basis === "interes_legitimo_art13d";
    await expect(region.getByRole("heading")).toHaveText(
      `Base de licitud y fundamento${active ? " · LIA" : ""} · evaluación versión 1`
    );
    await region
      .getByText(`Consultar evaluación de licitud${active ? " y LIA" : ""}`, { exact: true })
      .click();
    await expect(region.getByRole("region", { name: /LIA/ })).toHaveCount(0);
  });
}

test("11A ayudas asociadas y vista previa conservan ediciones sin guardar", async ({ page }) => {
  test.skip(integrated, "Ayudas con datos controlados");
  await draft(page);
  await expect(page.getByRole("status")).toContainText("Borrador creado");
  await page.evaluate((id) => (window as any).flow(id), treatment);
  await page.getByRole("tab", { name: "Completar datos", exact: true }).click();
  await page.getByRole("button", { name: "Documentar EIPD", exact: true }).click();
  const region = page.getByRole("region", { name: "Documento EIPD en borrador", exact: true });
  await expect(
    region.getByLabel("Referencia del documento EIPD", { exact: true })
  ).toHaveAccessibleDescription(/Referencia manual.*no es obligatoria/i);
  const purpose = region.getByLabel("Finalidad del tratamiento", { exact: true });
  await expect(purpose).toHaveAccessibleDescription(/para qué se usarán los datos/);
  await purpose.fill("[FICTICIA] Finalidad pendiente 11A");
  const before = await page.evaluate(
    () => (window as any).demo.calls.filter((c: any) => c.method === "PATCH").length
  );
  await region.getByRole("button", { name: "Ver vista previa EIPD", exact: true }).click();
  await expect(
    region.getByRole("note").filter({ hasText: "Vista previa de tu borrador" })
  ).toContainText("incluye ediciones pendientes");
  await expect(
    region.getByRole("complementary", { name: "Vista previa del borrador EIPD" })
  ).toContainText("[FICTICIA] Finalidad pendiente 11A");
  expect(
    await page.evaluate(
      () => (window as any).demo.calls.filter((c: any) => c.method === "PATCH").length
    )
  ).toBe(before);
  await region.getByRole("button", { name: "Guardar borrador EIPD", exact: true }).click();
  await expect(region.getByRole("status")).toContainText("Borrador EIPD guardado");
  await purpose.fill("[FICTICIA] Otra edición pendiente 11A");
  await expect(
    region.getByRole("status").filter({ hasText: "Borrador EIPD guardado" })
  ).toHaveCount(0);
  await expect(purpose).toHaveValue("[FICTICIA] Otra edición pendiente 11A");
});
