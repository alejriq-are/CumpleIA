import { test, expect } from "@playwright/test";
import { mkdtemp, writeFile, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";

test.skip(!process.env.CUMPLEIA_UI_API, "Requiere API aislada iniciada por pytest");

test("formulario y cliente reales registran una negativa en API aislada", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 749 });
  const api = process.env.CUMPLEIA_UI_API!;
  page.on("requestfailed", (request) =>
    console.log("Solicitud de prueba fallida:", request.failure()?.errorText)
  );
  page.on("console", (message) => {
    if (message.type() === "error") console.log("Navegador de prueba:", message.text());
  });
  expect(api).toMatch(/^http:\/\/127\.0\.0\.1:\d+$/);
  const directory = await mkdtemp(path.join(tmpdir(), "cumpleia-ui-integrated-"));
  try {
    const loader = path.join(directory, "typescript-loader.cjs");
    await writeFile(
      loader,
      `const ts=require(${JSON.stringify(require.resolve("typescript"))});module.exports=function(source){return ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.ESNext,target:ts.ScriptTarget.ES2021,jsx:ts.JsxEmit.ReactJSX}}).outputText};`
    );
    const entry = path.join(directory, "entry.js");
    await writeFile(
      entry,
      `
      import React from "react";
      import {createRoot} from "react-dom/client";
      import {EipdReviewConsultation} from ${JSON.stringify(path.resolve("components/admin/EipdReviewConsultation.tsx"))};
      import {ChildAdolescentEditor} from ${JSON.stringify(path.resolve("components/licitud/ChildAdolescentEditor.tsx"))};
      import {childApi} from ${JSON.stringify(path.resolve("lib/api/child-adolescent.ts"))};
      import {eipdReviewApi} from ${JSON.stringify(path.resolve("lib/api/eipd-review.ts"))};
      const scope=s=>({...s,token:"PRUEBA: sesion sintetica del servidor aislado"});
      const root=createRoot(document.getElementById("root"));
      window.openChildEditor=(s)=>{const context=scope(s);root.render(React.createElement(ChildAdolescentEditor,{load:()=>childApi.load(context),save:doc=>childApi.save(context,doc),readiness:()=>childApi.readiness(context)}));};
      root.render(React.createElement(EipdReviewConsultation,{
        loadPreparation:s=>eipdReviewApi.preparation(scope(s)),
        loadEvent:(s,id)=>eipdReviewApi.event(scope(s),id),
        recordNegative:(s,r)=>eipdReviewApi.recordNegativeV3(scope(s),r)
      }));
    `
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
            alias: { "@": process.cwd() },
            modules: [path.resolve("node_modules"), "node_modules"],
          },
          module: { rules: [{ test: /\.tsx?$/, use: loader }] },
          plugins: [
            new runtime.webpack.DefinePlugin({
              "process.env.NEXT_PUBLIC_API_URL": JSON.stringify(api),
            }),
          ],
        },
        (error: Error | null, stats: { hasErrors: () => boolean; toString: () => string }) =>
          error || stats.hasErrors() ? reject(error ?? new Error(stats.toString())) : resolve()
      )
    );
    // HTML shell and API share the isolated server origin; no browser security override.
    await page.goto(api + "/__eipd-isolated-test");
    await page.addScriptTag({ content: await readFile(path.join(directory, "bundle.js"), "utf8") });
    for (const [label, value] of [
      ["Organización", process.env.CUMPLEIA_UI_ORG],
      ["Tratamiento", process.env.CUMPLEIA_UI_TREATMENT],
      ["Evaluación", process.env.CUMPLEIA_UI_ASSESSMENT],
    ]) {
      await page.getByLabel(`${label} (identificador)`, { exact: true }).fill(value!);
    }
    await page.getByRole("button", { name: "Consultar requisitos" }).click();
    await expect(
      page.getByRole("heading", { name: "Registrar revisión negativa de prueba" })
    ).toBeVisible();
    await page
      .getByLabel("Fundamento de la revisión", { exact: true })
      .fill("PRUEBA INTEGRADA: faltan evidencias ficticias");
    await page
      .getByLabel("Referencia de la revisión", { exact: true })
      .fill("PRUEBA-CHROMIUM-API-V3");
    await page.getByLabel("Estoy usando únicamente datos ficticios.").check();
    await page.getByRole("button", { name: "Guardar revisión negativa" }).click();
    await expect(page.getByText("Revisión negativa guardada.", { exact: false })).toBeVisible();
    await expect(page.getByText("Contexto versión 3.", { exact: false })).toBeVisible();
    await expect(page.getByRole("button", { name: "Guardar revisión negativa" })).toHaveCount(0);
    await page.getByRole("button", { name: "Consultar revisión", exact: true }).click();
    await expect(page.getByText("PRUEBA-CHROMIUM-API-V3", { exact: true })).toBeVisible();
    await expect(page.getByRole("button", { name: /confirmar|activar|^Continuar$/i })).toHaveCount(
      0
    );
    await page.evaluate((s) => (window as any).openChildEditor(s), {
      organizationId: process.env.CUMPLEIA_UI_ORG!,
      treatmentId: process.env.CUMPLEIA_UI_TREATMENT!,
      assessmentId: process.env.CUMPLEIA_UI_ASSESSMENT!,
    });
    await page
      .getByLabel("Notas", { exact: true })
      .fill("PRUEBA: editor Chromium con API real aislada");
    await page.getByLabel("Niños y niñas", { exact: true }).check();
    await page.getByRole("button", { name: "Guardar documento", exact: true }).click();
    await expect(page.getByRole("status")).toHaveText("Documento guardado.");
    await expect(
      page.getByText("La consulta incluye infancia en el contexto actual.")
    ).toBeVisible();
    await expect(page.getByText("Confirmación y activación bloqueadas.")).toBeVisible();
    // API sucesora desde Chromium; no se presenta como un formulario nuevo.
    const successor = await page.evaluate(async (scope) => {
      const base = `/licitud/treatments/${scope.treatment}/assessments/${scope.assessment}/eipd-child/v4`;
      const headers = {"Content-Type":"application/json", "X-Organization-Id":scope.organization};
      const created = await fetch(base + "/resolutions", {method:"POST",headers,body:JSON.stringify({data_kind:"ficticios",document:{notes:"PRUEBA: sucesor Chromium aislado"}})});
      const resolution = await created.json();
      const path = base + `/resolutions/${resolution.id}/reviews`;
      const request = {data_kind:"ficticios",decision:"requiere_cambios",rationale:"PRUEBA: faltan evidencias ficticias",review_reference:"PRUEBA-CHROMIUM-INFANCIA-V4"};
      const saved = await fetch(path,{method:"POST",headers,body:JSON.stringify(request)});
      const event = await saved.json();
      const loaded = await fetch(path + `/${event.id}`,{headers});
      const rejected = await fetch(path,{method:"POST",headers,body:JSON.stringify({...request,decision:"continuar"})});
      return {created:created.status,saved:saved.status,loaded:loaded.status,rejected:rejected.status,event,history:await loaded.json()};
    }, {organization:process.env.CUMPLEIA_UI_ORG!,treatment:process.env.CUMPLEIA_UI_TREATMENT!,assessment:process.env.CUMPLEIA_UI_ASSESSMENT!});
    expect([successor.created,successor.saved,successor.loaded,successor.rejected]).toEqual([201,201,200,422]);
    expect(successor.history).toEqual(successor.event);
    expect(successor.event.review_context_metadata.child_coverage).toBe("contexto_v4");
    expect(successor.event.can_confirm).toBe(false);
    expect(successor.event.authorizes_action).toBe(false);

    await expect(page.getByRole("button", { name: /confirmar|activar|^Continuar$/i })).toHaveCount(
      0
    );
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
});
