import { test, expect } from "@playwright/test";
import { browserBundle } from "./helpers/browser-bundle";
import path from "node:path";
test("saved pending content identifies missing fields and provides section actions", async ({
  page,
}) => {
  const bundle = await browserBundle(
    `import React from "react";import {createRoot} from "react-dom/client";import {EipdPendingContent} from ${JSON.stringify(path.resolve("components/licitud/EipdPendingContent.tsx"))};createRoot(document.getElementById("root")).render(React.createElement(EipdPendingContent,{saved:{risks:[{risk_id:"R1"}]},issues:[{field:"scope.data_category_codes",code:"alcance_vacio",category:"incompleto"},{field:"scope.data_subject_codes",code:"alcance_vacio",category:"incompleto"},{field:"risks.0.impact_analysis",code:"campo_obligatorio",category:"incompleto"}],onComplete:root=>document.getElementById("destination").textContent=root}));`
  );
  await page.setContent('<div id="root"></div><output id="destination"></output>');
  await page.addScriptTag({ content: bundle });
  await expect(
    page.getByRole("cell", {
      name: "Falta indicar las categorías de datos incluidas.",
      exact: true,
    })
  ).toBeVisible();
  await expect(
    page.getByRole("cell", {
      name: "Falta indicar las categorías de titulares incluidas.",
      exact: true,
    })
  ).toBeVisible();
  await expect(
    page.getByText("R1: Falta describir el daño potencial a las personas.", { exact: true })
  ).toBeVisible();
  await page.getByRole("button", { name: "Completar alcance", exact: true }).first().click();
  await expect(page.locator("#destination")).toHaveText("scope");
  await page.getByRole("button", { name: "Completar riesgo R1", exact: true }).click();
  await expect(page.locator("#destination")).toHaveText("risks");
});
