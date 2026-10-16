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
      import {ChildEipdHistory} from ${JSON.stringify(path.resolve("components/licitud/ChildEipdHistory.tsx"))};
      import {childEipdApi} from ${JSON.stringify(path.resolve("lib/api/child-eipd.ts"))};
      import {childApi} from ${JSON.stringify(path.resolve("lib/api/child-adolescent.ts"))};
      import {eipdReviewApi} from ${JSON.stringify(path.resolve("lib/api/eipd-review.ts"))};
      const scope=s=>({...s,token:"PRUEBA: sesion sintetica del servidor aislado"});
      const root=createRoot(document.getElementById("root"));
      window.openChildEditor=(s)=>{const context=scope(s);root.render(React.createElement(ChildAdolescentEditor,{load:()=>childApi.load(context),save:doc=>childApi.save(context,doc),readiness:()=>childApi.readiness(context)}));};
      window.openChildHistory=(s)=>{const context=scope(s);root.render(React.createElement(ChildEipdHistory,{
        load:async()=>{const [a,p,r]=await Promise.all([childApi.load(context),childEipdApi.policy(context),childEipdApi.list(context)]);return {status:a.status,policy:p,resolutions:r};},
        create:d=>childEipdApi.create(context,d),reviews:r=>childEipdApi.reviews(context,r),review:(r,d,f,ref)=>childEipdApi.review(context,r,d,f,ref),readOnly:false
      }));};
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
    await page.evaluate((s) => (window as any).openChildHistory(s), {
      organizationId: process.env.CUMPLEIA_UI_ORG!,
      treatmentId: process.env.CUMPLEIA_UI_TREATMENT!,
      assessmentId: process.env.CUMPLEIA_UI_ASSESSMENT!,
    });
    await page
      .getByRole("checkbox", { name: "Declaro que este registro usa datos ficticios" })
      .check();
    await page
      .getByLabel("Referencia de la resolución *", { exact: true })
      .fill("PRUEBA-RES-CHROMIUM-INFANCIA");
    await page
      .getByLabel("Notas de la resolución", { exact: true })
      .fill("PRUEBA: sucesor Chromium aislado");
    await page.getByRole("button", { name: "Registrar resolución ficticia", exact: true }).click();
    await expect(page.getByRole("status")).toContainText("Resolución documental 1 registrada");
    await page
      .getByLabel("Fundamento de la revisión *", { exact: true })
      .fill("PRUEBA: faltan evidencias ficticias");
    await page
      .getByLabel("Referencia de la revisión *", { exact: true })
      .fill("PRUEBA-CHROMIUM-INFANCIA-V4");
    await page.getByRole("button", { name: "Registrar revisión ficticia", exact: true }).click();
    await expect(page.getByRole("status")).toContainText("Revisión negativa registrada");
    await page.getByRole("button", { name: "Actualizar historial de infancia" }).click();
    await page.getByRole("button", { name: "Consultar resolución 1", exact: true }).click();
    await expect(page.getByText("PRUEBA-CHROMIUM-INFANCIA-V4", { exact: true })).toBeVisible();
    // El servidor tambien debe rechazar la decision positiva fuera del formulario.
    const successor = await page.evaluate(
      async (scope) => {
        const base = `/licitud/treatments/${scope.treatment}/assessments/${scope.assessment}/eipd-child/v4`;
        const headers = {
          "Content-Type": "application/json",
          "X-Organization-Id": scope.organization,
        };
        const resolutions = await (await fetch(base + "/resolutions", { headers })).json();
        const r = resolutions[0];
        const path = base + `/resolutions/${r.id}/reviews`;
        const events = await (await fetch(path, { headers })).json();
        const rejected = await fetch(path, {
          method: "POST",
          headers,
          body: JSON.stringify({
            data_kind: "ficticios",
            decision: "continuar",
            rationale: "PRUEBA",
            review_reference: "PRUEBA-POSITIVA-RECHAZADA",
          }),
        });
        return { resolution: r, event: events[0], rejected: rejected.status };
      },
      {
        organization: process.env.CUMPLEIA_UI_ORG!,
        treatment: process.env.CUMPLEIA_UI_TREATMENT!,
        assessment: process.env.CUMPLEIA_UI_ASSESSMENT!,
      }
    );
    expect(successor.rejected).toBe(422);
    expect(successor.resolution.document.document_reference).toBe("PRUEBA-RES-CHROMIUM-INFANCIA");
    expect(successor.event.review_context_metadata.child_coverage).toBe("contexto_v4");
    expect(successor.event.document_hash).toBe(successor.resolution.document_hash);
    expect(successor.event.can_confirm).toBe(false);
    expect(successor.event.authorizes_action).toBe(false);

    await expect(page.getByRole("button", { name: /confirmar|activar|^Continuar$/i })).toHaveCount(
      0
    );
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
});
