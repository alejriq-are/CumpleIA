import { test, expect } from "@playwright/test";
import { mkdtemp, writeFile, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";

let directory: string;
let script: string;
const ids = [1, 2, 3, 4].map((n) => `a0000000-0000-0000-0000-${String(n).padStart(12, "0")}`);

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
    import {EipdReviewConsultation} from ${JSON.stringify(path.resolve("components/admin/EipdReviewConsultation.tsx"))};
    import {ApiError} from ${JSON.stringify(path.resolve("lib/api/client.ts"))};
    window.demo={calls:[],mode:"ok",release:null,issues:null,latestStatus:"sin_revision"};
    function preparation(scope){
      const partial={prerequisites_met:true,context_metadata:null,issues:[]};
      if(window.demo.issues)partial.issues=window.demo.issues;
      return {review_prerequisites_v4:window.demo.v4??null,current_control_issues_v4:window.demo.v4issues??null,assessment_id:scope.assessmentId,status:"borrador",sensitive_representation:window.demo.representation??null,representation_context_coverage:window.demo.representation?"pendiente":"no_aplica",policy_status:window.demo.policyStatus ?? {sources_status:"pendiente",acceptance_status:"pendiente",activation:"deshabilitada"},latest_review_context_status:window.demo.latestStatus,review_prerequisites_v3:{evaluation_version:3,evaluation_scope:"requisitos_documentales",authorizes_action:false,can_confirm:false,requiere_cambios:partial,no_continuar:partial,continuar:{prerequisites_met:false,context_metadata:null,issues:[{stage:"research",field:"research_assessment",code:"investigacion_confirmacion_bloqueada",category:"pendiente_revision",question_id:null}]}}};
    }
    async function loadPreparation(scope){
      window.demo.calls.push({kind:"preparation",scope});
      if(window.demo.mode==="error")throw new ApiError(window.demo.errorStatus ?? 403,"TEST");
      if(window.demo.mode==="wait")return new Promise(resolve=>{window.demo.release=()=>resolve(preparation(scope));});
      return preparation(scope);
    }
    async function loadEvent(scope,id){window.demo.calls.push({kind:"event",scope,id});return {decision:"no_continuar",rationale:"TEST: revisar",review_reference:"TEST: REV160",created_at:"2026-10-09T00:00:00Z",policy_reference:null,review_context_metadata:window.demo.eventMetadata??null};}
    async function recordNegative(scope,request){
      window.demo.calls.push({kind:"record",scope,request});
      if(window.demo.recordMode==="unknown")throw new Error("PRUEBA: conexion perdida");
      if(window.demo.recordMode==="denied")throw new ApiError(403,"PRUEBA");
      if(window.demo.recordMode==="stale")throw new ApiError(409,"PRUEBA");
      if(window.demo.recordMode==="wait")await new Promise(resolve=>{window.demo.releaseRecord=resolve;});
      return {id:"a0000000-0000-0000-0000-000000000004",...request,created_at:"2026-10-14T00:00:00Z",policy_reference:"PRUEBA",review_context_metadata:null};
    }
    const root=createRoot(document.getElementById("root"));
    window.enableRecording=()=>root.render(React.createElement(EipdReviewConsultation,{loadPreparation,loadEvent,recordNegative}));
    root.render(React.createElement(EipdReviewConsultation,{loadPreparation,loadEvent}));
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
  await page.setContent('<div id="root"></div>');
  await page.addScriptTag({ content: script });
  await expect(
    page.getByRole("heading", { name: "Consulta interna de revisiones EIPD" })
  ).toBeVisible();
});
async function scopeForm(page: import("@playwright/test").Page) {
  for (const [index, label] of ["Organización", "Tratamiento", "Evaluación"].entries()) {
    await page.getByLabel(`${label} (identificador)`, { exact: true }).fill(ids[index]);
  }
}

test("solo consulta y limpia datos al cambiar expediente", async ({ page }) => {
  await expect(
    page.getByText(
      "Pruebas de desarrollo: utiliza únicamente datos ficticios hasta disponer de la versión MVP.",
      { exact: false }
    )
  ).toBeVisible();
  await scopeForm(page);
  await page.getByRole("button", { name: "Consultar requisitos" }).click();
  await expect(page.getByRole("heading", { name: "Requisitos de revisión" })).toBeVisible();
  await expect(
    page.getByText(
      "Cumplir estos requisitos documentales no concede permiso ni registra una decisión."
    )
  ).toBeVisible();
  await page.getByText("Investigación — 1 motivo distinto", { exact: true }).click();
  await expect(
    page
      .locator("li > p")
      .getByText("La confirmación del expediente de investigación permanece bloqueada.")
  ).toBeVisible();
  expect(await page.getByRole("button").allTextContents()).toEqual([
    "Consultar requisitos",
    "Consultar revisión",
  ]);
  await page.getByLabel("Evaluación (identificador)", { exact: true }).fill(ids[3]);
  await expect(page.getByRole("heading", { name: "Requisitos de revisión" })).toHaveCount(0);
});

test("espera deshabilita cambios y peticiones duplicadas", async ({ page }) => {
  await scopeForm(page);
  await page.evaluate(() => {
    (window as unknown as { demo: { mode: string } }).demo.mode = "wait";
  });
  await page.getByRole("button", { name: "Consultar requisitos" }).click();
  await expect(page.getByRole("status")).toHaveText("Consultando…");
  await expect(page.getByLabel("Organización (identificador)", { exact: true })).toBeDisabled();
  await expect(page.getByRole("button", { name: "Consultar requisitos" })).toBeDisabled();
  await page.evaluate(() => {
    (window as unknown as { demo: { release: () => void } }).demo.release();
  });
  await expect(page.getByRole("heading", { name: "Requisitos de revisión" })).toBeVisible();
  const count = await page.evaluate(
    () => (window as unknown as { demo: { calls: unknown[] } }).demo.calls.length
  );
  expect(count).toBe(1);
});

test("errores claros sin mostrar resultados de consultas anteriores", async ({ page }) => {
  await scopeForm(page);
  await page.getByRole("button", { name: "Consultar requisitos" }).click();
  await expect(page.getByRole("heading", { name: "Requisitos de revisión" })).toBeVisible();
  await page.evaluate(() => {
    (window as unknown as { demo: { mode: string } }).demo.mode = "error";
  });
  await page.getByRole("button", { name: "Consultar requisitos" }).click();
  await expect(page.getByRole("alert")).toHaveText(
    "No tienes permiso para consultar este expediente."
  );
  await expect(page.getByRole("heading", { name: "Requisitos de revisión" })).toHaveCount(0);
  await expect(page.getByRole("link", { name: "Volver a iniciar sesión" })).toHaveCount(0);
});

test("evento historico no infiere metadata y seleccion explicita delimita consulta", async ({
  page,
}) => {
  await expect(page.getByRole("button", { name: "Consultar revisión" })).toBeDisabled();
  await scopeForm(page);
  await page.getByLabel("Revisión (identificador)", { exact: true }).fill(ids[3]);
  await page.getByRole("button", { name: "Consultar revisión" }).click();
  await expect(page.getByRole("heading", { name: "Revisión guardada" })).toBeVisible();
  await expect(page.getByText("Sin metadatos registrados; no se reconstruyen.")).toBeVisible();
  await expect(page.getByText("Sin identidad de política registrada.")).toBeVisible();
  const calls = await page.evaluate(
    () => (window as unknown as { demo: { calls: unknown[] } }).demo.calls
  );
  expect(calls).toEqual([
    {
      kind: "event",
      scope: { organizationId: ids[0], treatmentId: ids[1], assessmentId: ids[2] },
      id: ids[3],
    },
  ]);
});

test("motivos distinguen campos y preguntas, agrupan duplicados y presentan motivos desconocidos en español", async ({
  page,
}) => {
  await scopeForm(page);
  await page.evaluate(() => {
    const first = {
      stage: "resolution",
      field: "eipd_resolution_assessment.document_reference",
      code: "campo_obligatorio",
      category: "incompleto",
      question_id: null,
    };
    (window as unknown as { demo: { issues: unknown[] } }).demo.issues = [
      first,
      first,
      { ...first, field: "eipd_resolution_assessment.document_version" },
      {
        ...first,
        stage: "research",
        field: "research_assessment",
        code: "codigo_futuro",
        question_id: "pregunta_futura",
      },
    ];
  });
  await page.getByRole("button", { name: "Consultar requisitos" }).click();
  const card = page
    .locator("article")
    .filter({ has: page.getByRole("heading", { name: "Requiere cambios", exact: true }) });
  await expect(card.getByText("4 motivos informados.")).toBeVisible();
  await expect(card.locator("li")).toHaveCount(3);
  await expect(
    card.getByText("Campo: Documento EIPD › Referencia del documento")
  ).not.toBeVisible();
  await card.getByText("Documento EIPD — 2 motivos distintos", { exact: true }).click();
  await card.getByText("Investigación — 1 motivo distinto", { exact: true }).click();
  await expect(card.getByText("Campo: Documento EIPD › Referencia del documento")).toBeVisible();
  await expect(card.getByText("Campo: Documento EIPD › Versión del documento")).toBeVisible();
  await expect(card.getByText("Informado 2 veces por el diagnóstico.")).toBeVisible();
  await expect(card.getByText("Pregunta: Pregunta pendiente de identificar")).toBeVisible();
  await card.locator("li").last().getByText("Detalle del diagnóstico").click();
  await expect(card.getByText("codigo_futuro", { exact: true })).toHaveCount(0);
  await expect(card.locator("li").last().getByText("Incompleto", { exact: true })).toBeVisible();
  await expect(card.getByText("Investigación", { exact: true })).toHaveCount(1);
  await expect(
    card.getByText("Hay un motivo pendiente de revisión. Consulta su detalle.", { exact: true })
  ).toBeVisible();
});

test("temas se despliegan con teclado sin perder motivos al cerrar", async ({ page }) => {
  await scopeForm(page);
  await page.getByRole("button", { name: "Consultar requisitos" }).click();
  const summary = page.getByText("Investigación — 1 motivo distinto", { exact: true });
  const message = page
    .locator("li > p")
    .getByText("La confirmación del expediente de investigación permanece bloqueada.");
  await expect(message).not.toBeVisible();
  await summary.focus();
  await page.keyboard.press("Enter");
  await expect(message).toBeVisible();
  await page.keyboard.press("Enter");
  await expect(message).not.toBeVisible();
  await page.keyboard.press("Enter");
  await expect(message).toBeVisible();
  expect(
    await page.evaluate(
      () => (window as unknown as { demo: { calls: unknown[] } }).demo.calls.length
    )
  ).toBe(1);
});

test("estado de ultima revision distingue historia y requisitos sin atribuir autoridad", async ({
  page,
}) => {
  await scopeForm(page);
  const messages = {
    sin_revision: "No hay una revisión guardada para este expediente.",
    sin_metadatos:
      "La última revisión no tiene identidad documental registrada; no se puede comparar con el material actual.",
    vigente: "El vínculo documental de la última revisión corresponde al material actual.",
    obsoleta:
      "El vínculo documental de la última revisión está desactualizado respecto del material actual.",
  };
  for (const [state, message] of Object.entries(messages)) {
    await page.evaluate((state) => {
      (window as unknown as { demo: { latestStatus: string } }).demo.latestStatus = state;
    }, state);
    await page.getByRole("button", { name: "Consultar requisitos" }).click();
    await expect(page.getByText(message, { exact: true })).toBeVisible();
  }
  await expect(
    page.getByText(
      "Este estado no aprueba el expediente ni autoriza continuar, confirmar o activar. Se refiere a la última revisión, aunque consultes otro evento histórico."
    )
  ).toBeVisible();
  await page.getByLabel("Revisión (identificador)", { exact: true }).fill(ids[3]);
  await page.getByRole("button", { name: "Consultar revisión" }).click();
  await expect(
    page.getByRole("heading", { name: "Vínculo de la última revisión con el material actual" })
  ).toHaveCount(0);
  await expect(page.getByRole("heading", { name: "Revisión guardada" })).toBeVisible();
});

test("politica pendiente visible sin autoridad y separada de evento historico", async ({
  page,
}) => {
  await scopeForm(page);
  await page.getByRole("button", { name: "Consultar requisitos", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Estado de la política EIPD" })).toBeVisible();
  await expect(page.getByText("Pendientes de verificación", { exact: true })).toBeVisible();
  await expect(page.getByText("Deshabilitada", { exact: true })).toBeVisible();
  await expect(
    page.getByText("Este estado corresponde a la política actual.", { exact: false })
  ).toBeVisible();
  await page.getByLabel("Revisión (identificador)", { exact: true }).fill(ids[3]);
  await page.getByRole("button", { name: "Consultar revisión", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Revisión guardada" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Estado de la política EIPD" })).toHaveCount(0);
});

test("estados ficticios de politica no autorizan expediente ni muestran controles de confirmacion", async ({
  page,
}) => {
  await scopeForm(page);
  for (const item of [
    {
      sources_status: "verificadas",
      acceptance_status: "pendiente",
      activation: "deshabilitada",
      acceptance: "Pendiente",
      activationLabel: "Deshabilitada",
    },
    {
      sources_status: "verificadas",
      acceptance_status: "aceptada",
      activation: "deshabilitada",
      acceptance: "Aceptada según el registro",
      activationLabel: "Deshabilitada",
    },
    {
      sources_status: "verificadas",
      acceptance_status: "aceptada",
      activation: "habilitada",
      acceptance: "Aceptada según el registro",
      activationLabel: "Habilitada según el registro",
    },
  ]) {
    await page.evaluate(
      (status) => {
        (window as unknown as { demo: { policyStatus: unknown } }).demo.policyStatus = status;
      },
      {
        sources_status: item.sources_status,
        acceptance_status: item.acceptance_status,
        activation: item.activation,
      }
    );
    await page.getByRole("button", { name: "Consultar requisitos", exact: true }).click();
    const panel = page.locator('section[aria-labelledby="policy-status-heading"]');
    await expect(panel.getByText("Verificadas según el registro", { exact: true })).toBeVisible();
    await expect(panel.getByText(item.acceptance, { exact: true })).toBeVisible();
    await expect(panel.getByText(item.activationLabel, { exact: true })).toBeVisible();
    await expect(
      panel.getByText("No aprueba el expediente ni autoriza por sí solo", { exact: false })
    ).toBeVisible();
    await expect(page.getByRole("button", { name: /confirmar|activar|aprobar/i })).toHaveCount(0);
    await expect(
      page.getByText("Requisitos documentales pendientes.", { exact: true })
    ).toBeVisible();
  }
});

test("sesion vencida ofrece inicio de sesion y limpia el enlace al cambiar expediente", async ({
  page,
}) => {
  await scopeForm(page);
  await page.getByRole("button", { name: "Consultar requisitos" }).click();
  await page.evaluate(() => {
    Object.assign((window as unknown as { demo: object }).demo, {
      mode: "error",
      errorStatus: 401,
    });
  });
  await page.getByRole("button", { name: "Consultar requisitos" }).click();
  await expect(page.getByRole("alert")).toContainText(
    "La sesión no es válida. Vuelve a iniciar sesión."
  );
  await expect(page.getByRole("link", { name: "Volver a iniciar sesión" })).toHaveAttribute(
    "href",
    "/login"
  );
  await expect(page.getByRole("heading", { name: "Requisitos de revisión" })).toHaveCount(0);
  await page.getByLabel("Evaluación (identificador)", { exact: true }).fill(ids[3]);
  await expect(page.getByRole("link", { name: "Volver a iniciar sesión" })).toHaveCount(0);
  await page.evaluate(() => {
    Object.assign((window as unknown as { demo: object }).demo, { mode: "ok" });
  });
  await page.getByRole("button", { name: "Consultar requisitos" }).click();
  await expect(page.getByRole("heading", { name: "Requisitos de revisión" })).toBeVisible();
  await expect(page.getByRole("alert")).toHaveCount(0);
});

test("representacion muestra faltantes y cobertura pendiente sin vigencia global", async ({
  page,
}) => {
  await scopeForm(page);
  await page.evaluate(() => {
    Object.assign((window as unknown as { demo: object }).demo, {
      latestStatus: "vigente",
      representation: {
        evaluation_version: 1,
        evaluation_scope: "requisitos_documentales",
        authorizes_action: false,
        can_confirm: false,
        result: "incompleto",
        issues: [
          {
            stage: "representation",
            field: "authority_document_reference",
            code: "representacion_material_pendiente",
            category: "incompleto",
            question_id: null,
          },
        ],
      },
    });
  });
  await page.getByRole("button", { name: "Consultar requisitos" }).click();
  await expect(
    page.getByRole("heading", { name: "Representación del consentimiento sensible" })
  ).toBeVisible();
  await expect(page.getByText("Documentación incompleta.", { exact: true })).toBeVisible();
  await expect(
    page.getByText("Las revisiones EIPD anteriores no cubren este material de representación.", {
      exact: false,
    })
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Vínculo de la última revisión con el material actual" })
  ).toHaveCount(0);
  await page.getByText("Representación sensible — 1 motivo distinto", { exact: true }).click();
  await expect(
    page
      .getByText("Falta aportar este dato documental de la representación.", { exact: false })
      .first()
  ).toBeVisible();
  await expect(page.getByRole("button", { name: /confirmar|activar|registrar/i })).toHaveCount(0);
  await page.getByLabel("Revisión (identificador)", { exact: true }).fill(ids[3]);
  await page.getByRole("button", { name: "Consultar revisión" }).click();
  await expect(page.getByRole("heading", { name: "Revisión guardada" })).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Representación del consentimiento sensible" })
  ).toHaveCount(0);
  await expect(
    page.getByText("Las revisiones EIPD anteriores no cubren este material de representación.", {
      exact: false,
    })
  ).toHaveCount(0);
});

test("V4 muestra motivos completos y decisiones bloqueadas sin mezclar historia", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 749 });
  await scopeForm(page);
  await page.evaluate(() => {
    const issue = {
      stage: "activation",
      field: "policy.routes",
      code: "politica_representacion_no_implementada",
      category: "requiere_revision",
      question_id: null,
    };
    const decision = { prerequisites_met: false, context_metadata: null, issues: [issue] };
    Object.assign((window as unknown as { demo: object }).demo, {
      latestStatus: "vigente",
      v4issues: [issue, issue, issue],
      representation: {
        evaluation_version: 1,
        evaluation_scope: "requisitos_documentales",
        authorizes_action: false,
        can_confirm: false,
        result: "incompleto",
        issues: [],
      },
      v4: {
        evaluation_version: 4,
        evaluation_scope: "requisitos_documentales",
        authorizes_action: false,
        can_confirm: false,
        continuar: decision,
        requiere_cambios: decision,
        no_continuar: decision,
      },
    });
  });
  await page.getByRole("button", { name: "Consultar requisitos" }).click();
  await expect(page.getByRole("heading", { name: "Motivos del expediente actual" })).toBeVisible();
  await expect(
    page.getByText("El diagnóstico actual incluye la representación.", { exact: false })
  ).toBeVisible();
  await expect(page.getByText("Registro de revisión no habilitado.", { exact: true })).toHaveCount(
    3
  );
  await expect(page.getByRole("heading", { name: "Continuar", exact: true })).toBeVisible();
  const region = page.getByRole("region", { name: "Motivos del expediente actual" });
  await region.getByText("Habilitación EIPD — 1 motivo distinto", { exact: true }).click();
  await expect(
    region
      .getByText(
        "La política para representación sigue pendiente; no se permite confirmar o registrar una revisión.",
        { exact: false }
      )
      .first()
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Vínculo de la última revisión con el material actual" })
  ).toHaveCount(0);
  await expect(page.getByRole("button", { name: /confirmar|activar|registrar/i })).toHaveCount(0);
  await page.getByLabel("Revisión (identificador)", { exact: true }).fill(ids[3]);
  await page.getByRole("button", { name: "Consultar revisión" }).click();
  await expect(page.getByRole("heading", { name: "Revisión guardada" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Motivos del expediente actual" })).toHaveCount(0);
});

test("historia sucesora muestra cobertura guardada sin acreditar vigencia actual", async ({
  page,
}) => {
  await scopeForm(page);
  await page.evaluate(() => {
    Object.assign((window as unknown as { demo: object }).demo, {
      eventMetadata: {
        metadata_schema_version: 2,
        resolution_binding_version: 3,
        context_schema_version: 3,
        research_coverage: "contexto_v3",
        representation_coverage: "contexto_v3",
        document_hash: "a".repeat(64),
        context_hash: "b".repeat(64),
        research_material_hash: null,
        representation_material_hash: "d".repeat(64),
      },
    });
  });
  await page.getByLabel("Revisión (identificador)", { exact: true }).fill(ids[3]);
  await page.getByRole("button", { name: "Consultar revisión" }).click();
  await expect(
    page.getByText(
      "Contexto versión 3. Cobertura: contexto de investigación y representación. Material de representación: identidad registrada.",
      { exact: true }
    )
  ).toBeVisible();
  await expect(
    page.getByText("Su consulta no acredita vigencia del expediente actual.", { exact: false })
  ).toBeVisible();
  await expect(page.getByRole("button", { name: /confirmar|activar|registrar/i })).toHaveCount(0);
});

async function negativeForm(page: import("@playwright/test").Page) {
  await page.evaluate(() => {
    const w = window as any;
    const blocked = { prerequisites_met: false, context_metadata: null, issues: [] };
    w.demo.v4 = {
      evaluation_version: 4,
      continuar: blocked,
      requiere_cambios: blocked,
      no_continuar: blocked,
    };
    w.enableRecording();
  });
  await scopeForm(page);
  await page.getByRole("button", { name: "Consultar requisitos" }).click();
  await expect(
    page.getByRole("heading", { name: "Registrar revisión negativa de prueba" })
  ).toBeVisible();
  await page
    .getByLabel("Fundamento de la revisión", { exact: true })
    .fill("PRUEBA: faltan evidencias ficticias");
  await page.getByLabel("Referencia de la revisión", { exact: true }).fill("PRUEBA-UI-V3");
}

test("registro negativo exige datos ficticios y conserva evento sin habilitar positivos", async ({
  page,
}) => {
  await negativeForm(page);
  const submit = page.getByRole("button", { name: "Guardar revisión negativa" });
  await expect(submit).toBeDisabled();
  await page.getByLabel("Estoy usando únicamente datos ficticios.").check();
  await page.getByLabel("Decisión negativa").selectOption("no_continuar");
  await submit.click();
  await expect(page.getByText("Revisión negativa guardada.", { exact: false })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Revisión guardada", exact: true })).toBeVisible();
  await expect(submit).toHaveCount(0);
  const calls = await page.evaluate(() =>
    (window as any).demo.calls.filter((x: any) => x.kind === "record")
  );
  expect(calls).toHaveLength(1);
  expect(calls[0].request).toEqual({
    decision: "no_continuar",
    rationale: "PRUEBA: faltan evidencias ficticias",
    review_reference: "PRUEBA-UI-V3",
  });
  await expect(page.getByRole("button", { name: /confirmar|activar|^Continuar$/i })).toHaveCount(0);
});

test("registro pendiente bloquea cambios y doble envio", async ({ page }) => {
  await negativeForm(page);
  await page.evaluate(() => {
    (window as any).demo.recordMode = "wait";
  });
  await page.getByLabel("Estoy usando únicamente datos ficticios.").check();
  await page.getByRole("button", { name: "Guardar revisión negativa" }).click();
  await expect(page.getByLabel("Organización (identificador)", { exact: true })).toBeDisabled();
  await expect(page.getByRole("button", { name: "Guardar revisión negativa" })).toBeDisabled();
  await page.evaluate(() => (window as any).demo.releaseRecord());
  await expect(page.getByText("Revisión negativa guardada.", { exact: false })).toBeVisible();
  expect(
    await page.evaluate(
      () => (window as any).demo.calls.filter((x: any) => x.kind === "record").length
    )
  ).toBe(1);
});

test("resultado incierto bloquea repeticion incluso al consultar nuevamente", async ({ page }) => {
  await negativeForm(page);
  await page.evaluate(() => {
    (window as any).demo.recordMode = "unknown";
  });
  await page.getByLabel("Estoy usando únicamente datos ficticios.").check();
  await page.getByRole("button", { name: "Guardar revisión negativa" }).click();
  await expect(page.getByRole("alert")).toContainText(
    "No se pudo verificar si la revisión quedó guardada"
  );
  await expect(page.getByRole("button", { name: "Guardar revisión negativa" })).toBeDisabled();
  await page.getByRole("button", { name: "Consultar requisitos" }).click();
  await expect(page.getByRole("button", { name: "Guardar revisión negativa" })).toBeDisabled();
  expect(
    await page.evaluate(
      () => (window as any).demo.calls.filter((x: any) => x.kind === "record").length
    )
  ).toBe(1);
});

test("cambio de expediente limpia solicitud y permiso denegado no muestra exito", async ({
  page,
}) => {
  await negativeForm(page);
  await page.evaluate(() => {
    (window as any).demo.recordMode = "denied";
  });
  await page.getByLabel("Estoy usando únicamente datos ficticios.").check();
  await page.getByRole("button", { name: "Guardar revisión negativa" }).click();
  await expect(page.getByRole("alert")).toContainText("No tienes permiso para registrar");
  await expect(page.getByText("Revisión negativa guardada.", { exact: false })).toHaveCount(0);
  await page.getByLabel("Evaluación (identificador)", { exact: true }).fill(ids[3]);
  await page.getByRole("button", { name: "Consultar requisitos" }).click();
  await expect(page.getByLabel("Fundamento de la revisión", { exact: true })).toHaveValue("");
  await expect(page.getByLabel("Referencia de la revisión", { exact: true })).toHaveValue("");
  await expect(page.getByLabel("Estoy usando únicamente datos ficticios.")).not.toBeChecked();
});

test("material cambiado exige nueva consulta y formulario usable en movil", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 749 });
  await negativeForm(page);
  await page.evaluate(() => {
    (window as any).demo.recordMode = "stale";
  });
  await page.getByLabel("Estoy usando únicamente datos ficticios.").check();
  await page.getByRole("button", { name: "Guardar revisión negativa" }).click();
  await expect(page.getByRole("alert")).toContainText("Consulta de nuevo los requisitos");
  await expect(page.getByRole("button", { name: "Guardar revisión negativa" })).toHaveCount(0);
  await page.getByRole("button", { name: "Consultar requisitos" }).click();
  await expect(page.getByRole("button", { name: "Guardar revisión negativa" })).toBeEnabled();
});
