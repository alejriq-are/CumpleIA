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
    window.demo={calls:[],mode:"ok",release:null};
    function preparation(scope){
      const partial={prerequisites_met:true,context_metadata:null,issues:[]};
      return {assessment_id:scope.assessmentId,status:"borrador",review_prerequisites_v3:{evaluation_version:3,evaluation_scope:"requisitos_documentales",authorizes_action:false,can_confirm:false,requiere_cambios:partial,no_continuar:partial,continuar:{prerequisites_met:false,context_metadata:null,issues:[{code:"investigacion_confirmacion_bloqueada"}]}}};
    }
    async function loadPreparation(scope){
      window.demo.calls.push({kind:"preparation",scope});
      if(window.demo.mode==="error")throw new ApiError(403,"TEST");
      if(window.demo.mode==="wait")return new Promise(resolve=>{window.demo.release=()=>resolve(preparation(scope));});
      return preparation(scope);
    }
    async function loadEvent(scope,id){window.demo.calls.push({kind:"event",scope,id});return {decision:"no_continuar",rationale:"TEST: revisar",review_reference:"TEST: REV160",created_at:"2026-10-09T00:00:00Z",policy_reference:null,review_context_metadata:null};}
    createRoot(document.getElementById("root")).render(React.createElement(EipdReviewConsultation,{loadPreparation,loadEvent}));
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
  await scopeForm(page);
  await page.getByRole("button", { name: "Consultar requisitos" }).click();
  await expect(page.getByRole("heading", { name: "Requisitos de revisión" })).toBeVisible();
  await expect(
    page.getByText(
      "Cumplir estos requisitos documentales no concede permiso ni registra una decisión."
    )
  ).toBeVisible();
  await expect(page.getByText("investigacion confirmacion bloqueada")).toBeVisible();
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
