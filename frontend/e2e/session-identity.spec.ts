import { test, expect } from "@playwright/test";
import { browserBundle } from "./helpers/browser-bundle";
import path from "node:path";
let script: string;
test.beforeAll(async () => {
  script =
    await browserBundle(`import React from "react";import {createRoot} from "react-dom/client";
    import {SessionIdentity} from ${JSON.stringify(path.resolve("components/navigation/SessionIdentity.tsx"))};
    const root=createRoot(document.getElementById("root"));
    window.renderPerson=(person,role)=>root.render(React.createElement(SessionIdentity,{person,role}));`);
});
test("session identity changes with the supplied authenticated person and organization role", async ({
  page,
}) => {
  await page.setContent('<div id="root"></div>');
  await page.addScriptTag({ content: script });
  await page.evaluate(() =>
    (window as any).renderPerson(
      { id: "PERFIL-A", email: "a@example.test", full_name: "Persona A" },
      "owner"
    )
  );
  await expect(page.getByText("a@example.test", { exact: true })).toBeVisible();
  await expect(page.getByText("Propietario", { exact: true })).toBeVisible();
  await page.evaluate(() =>
    (window as any).renderPerson(
      { id: "PERFIL-B", email: "b@example.test", full_name: null },
      "editor"
    )
  );
  await expect(page.getByText("b@example.test", { exact: true })).toBeVisible();
  await expect(page.getByText("Editor", { exact: true })).toBeVisible();
  await expect(page.getByText("Persona A", { exact: true })).toHaveCount(0);
  await expect(page.getByText("a@example.test", { exact: true })).toHaveCount(0);
  await page.getByText("Identificador de la persona", { exact: true }).click();
  await expect(page.getByText("PERFIL-B", { exact: true })).toBeVisible();
});
test("missing identity is explicit instead of attributing a person from organization data", async ({
  page,
}) => {
  await page.setContent('<div id="root"></div>');
  await page.addScriptTag({ content: script });
  await page.evaluate(() => (window as any).renderPerson(null, "editor"));
  await expect(
    page.getByText("No se ha podido consultar la identidad de esta sesión.", { exact: true })
  ).toBeVisible();
  await expect(page.getByText("Editor", { exact: true })).toHaveCount(0);
  await expect(page.getByText("Correo de acceso", { exact: true })).toHaveCount(0);
});
