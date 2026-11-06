import { test, expect, type Page } from "@playwright/test";
import { browserBundle } from "./helpers/browser-bundle";
import path from "node:path";
let bundle: string;
const org = "10000000-0000-0000-0000-000000000001",
  tid = "10000000-0000-0000-0000-000000000002",
  aid = "10000000-0000-0000-0000-000000000003";
const actor = "10000000-0000-0000-0000-000000000004",
  vid = "10000000-0000-0000-0000-000000000005";
const material = {
  schema_version: 1,
  document_type: "eipd_general",
  saved_assessment: {
    id: aid,
    organization_id: org,
    treatment_id: tid,
    version: 1,
    purpose_snapshot: "[FICTICIA] Finalidad conservada",
    rat_context_snapshot: { title: "RAT histórico" },
    eipd_resolution_assessment: { schema_version: 1, notes: "[FICTICIA] Contenido guardado" },
  },
  applicability: { eipd: "corresponde" },
  support_records: [],
  policy: { reference: "Ensayo" },
  diagnostic: { readiness: { result: "incompleto" } },
};
const preview = {
  source_hash: "a".repeat(64),
  latest_version: 0,
  bundle: material,
  can_confirm: false,
  activation: "deshabilitada",
};
test.beforeAll(async () => {
  bundle = await browserBundle(
    `import React from "react";import {createRoot} from "react-dom/client";import {EipdVersions} from ${JSON.stringify(path.resolve("components/licitud/EipdVersions.tsx"))};const root=createRoot(document.getElementById("root"));window.renderVersions=(props)=>root.render(React.createElement(EipdVersions,{organizationId:${JSON.stringify(org)},treatmentId:${JSON.stringify(tid)},assessmentId:${JSON.stringify(aid)},token:async()=>"fixture-token",canRegister:true,canCopy:true,onCopy:v=>window.copied=v,...props}));`
  );
});
async function setup(page: Page, mode = "success", props = {}) {
  await page.route("http://localhost:3000/fixture", (r) =>
    r.fulfill({ contentType: "text/html", body: '<div id="root"></div>' })
  );
  await page.goto("http://localhost:3000/fixture");
  await page.evaluate(
    ({ preview, org, tid, aid, actor, vid, mode }) => {
      const w = window as any;
      w.mode = mode;
      w.calls = [];
      w.posts = [];
      w.found = null;
      w.fetch = async (url: string, init: any = {}) => {
        w.calls.push({ url, ...init });
        const method = init.method || "GET";
        const response = (v: any, status = 200) =>
          new Response(JSON.stringify(v), {
            status,
            headers: { "Content-Type": "application/json" },
          });
        if (url.endsWith("/preview"))
          return response(
            w.mode === "foreign"
              ? {
                  ...preview,
                  bundle: {
                    ...preview.bundle,
                    saved_assessment: { ...preview.bundle.saved_assessment, id: vid },
                  },
                }
              : preview
          );
        if (method === "POST") {
          const b = JSON.parse(init.body);
          w.posts.push(b);
          if (w.mode === "stale") return response({ detail: "El origen cambió" }, 409);
          if (w.mode === "missing" && w.posts.length === 1) throw new TypeError("Offline");
          w.found = {
            id: vid,
            organization_id: org,
            treatment_id: tid,
            assessment_id: aid,
            version: 1,
            created_by: actor,
            created_at: "2026-11-02T12:00:00Z",
            request_id: b.request_id,
            reason: b.reason,
            source_hash: b.expected_source_hash,
            bundle_hash: "b".repeat(64),
            bundle: {
              ...preview.bundle,
              version: 1,
              predecessor_id: null,
              reason: b.reason,
              registered_by: actor,
            },
            can_confirm: false,
            activation: "deshabilitada",
          };
          if (w.mode === "lost") throw new TypeError("Response lost");
          return response(w.found, 201);
        }
        if (url.includes("/requests/"))
          return w.found ? response(w.found) : response({ detail: "No encontrado" }, 404);
        if (w.byId?.[url.split("/").at(-1)!]) return response(w.byId[url.split("/").at(-1)!]);
        if (url.endsWith("/" + vid)) return response(w.found);
        return response(w.versionHistory ?? (w.found ? [w.found] : []));
      };
    },
    { preview, org, tid, aid, actor, vid, mode }
  );
  await page.addScriptTag({ content: bundle });
  await page.evaluate((props) => (window as any).renderVersions(props), props);
}
async function prepare(page: Page) {
  await page
    .getByRole("button", { name: "Preparar registro de versión EIPD", exact: true })
    .click();
  await page
    .getByLabel("Motivo del registro de versión EIPD", { exact: true })
    .fill("[FICTICIA] Versión de prueba");
  await page.getByLabel("Declaro datos ficticios para esta versión EIPD", { exact: true }).check();
  await page
    .getByLabel("He leído el contenido guardado y sus pendientes antes de registrar", {
      exact: true,
    })
    .check();
}
test("registro explícito, consulta histórica y copia confirmada sin otra escritura", async ({
  page,
}) => {
  await setup(page);
  await prepare(page);
  await page
    .getByRole("button", { name: "Registrar versión documental EIPD", exact: true })
    .click();
  await expect(page.getByRole("status")).toContainText("Versión EIPD 1 registrada");
  await page.getByRole("button", { name: "Mostrar historial de versiones EIPD" }).click();
  await page.getByRole("button", { name: "Consultar versión EIPD 1", exact: true }).click();
  await page.getByRole("button", { name: "Ocultar historial de versiones EIPD" }).click();
  await expect(
    page.getByRole("button", { name: "Consultar versión EIPD 1", exact: true })
  ).toBeHidden();
  await expect(page.getByRole("article")).toContainText("Contenido guardado");
  await page.getByRole("button", { name: "Preparar borrador desde esta versión EIPD" }).click();
  await page.getByRole("button", { name: "Conservar mi borrador actual" }).click();
  expect(await page.evaluate(() => (window as any).copied)).toBeUndefined();
  await page.getByRole("button", { name: "Preparar borrador desde esta versión EIPD" }).click();
  await page.getByRole("button", { name: "Reemplazar borrador con esta copia" }).click();
  expect(await page.evaluate(() => (window as any).copied.notes)).toContain("Contenido guardado");
  expect(await page.evaluate(() => (window as any).posts.length)).toBe(1);
  const calls = await page.evaluate(() => (window as any).calls);
  expect(
    calls.every((c: any) => c.cache === "no-store" && c.headers["X-Organization-Id"] === org)
  ).toBeTruthy();
});
test("respuesta perdida recupera solicitud sin duplicar registro", async ({ page }) => {
  await setup(page, "lost");
  await prepare(page);
  await page
    .getByRole("button", { name: "Registrar versión documental EIPD", exact: true })
    .click();
  await expect(page.getByRole("alert")).toContainText("por comprobar");
  await expect(
    page.getByRole("button", { name: "Preparar registro de versión EIPD", exact: true })
  ).toBeDisabled();
  await page.getByRole("button", { name: "Consultar resultado del registro EIPD" }).click();
  await expect(page.getByRole("status")).toContainText("Versión EIPD 1 registrada");
  expect(await page.evaluate(() => (window as any).posts.length)).toBe(1);
});
test("404 permite reintentar exactamente la misma solicitud", async ({ page }) => {
  await setup(page, "missing");
  await prepare(page);
  await page
    .getByRole("button", { name: "Registrar versión documental EIPD", exact: true })
    .click();
  await page.getByRole("button", { name: "Consultar resultado del registro EIPD" }).click();
  await page.getByRole("button", { name: "Reintentar el mismo registro EIPD" }).click();
  await expect(page.getByRole("status")).toContainText("Versión EIPD 1 registrada");
  const posts = await page.evaluate(() => (window as any).posts);
  expect(posts).toHaveLength(2);
  expect(posts[1]).toEqual(posts[0]);
});
test("origen desactualizado exige otra vista previa", async ({ page }) => {
  await setup(page, "stale");
  await prepare(page);
  await page
    .getByRole("button", { name: "Registrar versión documental EIPD", exact: true })
    .click();
  await expect(page.getByRole("alert")).toContainText("Registro rechazado");
  await expect(
    page.getByRole("button", { name: "Registrar versión documental EIPD", exact: true })
  ).toHaveCount(0);
  await expect(
    page.getByRole("button", { name: "Preparar registro de versión EIPD", exact: true })
  ).toBeEnabled();
  expect(await page.evaluate(() => (window as any).posts.length)).toBe(1);
});
test("respuesta de otra evaluación no habilita registro", async ({ page }) => {
  await setup(page, "foreign");
  await page
    .getByRole("button", { name: "Preparar registro de versión EIPD", exact: true })
    .click();
  await expect(page.getByRole("alert")).toContainText("incompatible");
  await expect(page.getByLabel("Motivo del registro de versión EIPD", { exact: true })).toHaveCount(
    0
  );
});
test("ediciones pendientes bloquean registro pero conservan consulta", async ({ page }) => {
  await setup(page, "success", {
    canRegister: false,
    draftDirty: true,
    blockedReason: "Guarda los cambios pendientes",
  });
  await expect(
    page.getByRole("button", { name: "Preparar registro de versión EIPD", exact: true })
  ).toBeDisabled();
  await page.getByRole("button", { name: "Mostrar historial de versiones EIPD" }).click();
  await expect(
    page.getByText("No hay versiones EIPD registradas en esta evaluación.")
  ).toBeVisible();
  expect(await page.evaluate(() => (window as any).posts.length)).toBe(0);
});

test("editar el origen invalida la vista previa sin escribir una versión", async ({ page }) => {
  await setup(page);
  await prepare(page);
  await page.evaluate(() =>
    (window as any).renderVersions({
      sourceRevision: "nueva-edicion",
      canRegister: false,
      draftDirty: true,
    })
  );
  await expect(
    page.getByRole("button", { name: "Registrar versión documental EIPD", exact: true })
  ).toHaveCount(0);
  expect(await page.evaluate(() => (window as any).posts.length)).toBe(0);
});
test("consulta de solo lectura no ofrece registro ni reemplazo y admite teclado", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await setup(page, "success", { onCopy: null, canRegister: false });
  await expect(
    page.getByRole("button", { name: "Preparar registro de versión EIPD", exact: true })
  ).toHaveCount(0);
  const history = page.getByRole("button", { name: "Mostrar historial de versiones EIPD" });
  await history.focus();
  await page.keyboard.press("Space");
  await expect(
    page.getByText("No hay versiones EIPD registradas en esta evaluación.")
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Ocultar historial de versiones EIPD" })
  ).toBeFocused();
  expect(await page.evaluate(() => (window as any).posts.length)).toBe(0);
});

test("consulta abre versiones recientes primero sin formulario de registro", async ({ page }) => {
  await setup(page, "success", { consultationOnly: true });
  await page.evaluate(
    ({ preview, org, tid, aid, actor, vid }) => {
      const w = window as any;
      const first = {
        id: vid,
        organization_id: org,
        treatment_id: tid,
        assessment_id: aid,
        version: 1,
        created_by: actor,
        created_at: "2026-11-05T12:00:00Z",
        request_id: crypto.randomUUID(),
        reason: "[FICTICIA] Primera",
        source_hash: "a".repeat(64),
        bundle_hash: "b".repeat(64),
        bundle: {
          ...preview.bundle,
          version: 1,
          predecessor_id: null,
          reason: "[FICTICIA] Primera",
          registered_by: actor,
        },
        can_confirm: false,
        activation: "deshabilitada",
      };
      const second = {
        ...first,
        id: crypto.randomUUID(),
        version: 2,
        reason: "[FICTICIA] Segunda",
        bundle: { ...first.bundle, version: 2, predecessor_id: vid, reason: "[FICTICIA] Segunda" },
      };
      w.versionHistory = [first, second];
      w.byId = { [first.id]: first, [second.id]: second };
    },
    { preview, org, tid, aid, actor, vid }
  );
  await page.getByRole("button", { name: "Actualizar historial de versiones EIPD" }).click();
  await expect(page.getByRole("button", { name: /^Consultar versión EIPD/ })).toHaveText([
    "Consultar versión EIPD 2",
    "Consultar versión EIPD 1",
  ]);
  await expect(
    page.getByRole("region", { name: "Registrar versión EIPD", exact: true })
  ).toHaveCount(0);
  await page.getByRole("button", { name: "Consultar versión EIPD 2", exact: true }).click();
  await expect(
    page.getByRole("article", { name: "Versión EIPD 2 consultada", exact: true })
  ).toBeVisible();
  const content = page.getByText("Contenido EIPD conservado para esta versión", { exact: true });
  await expect(content.locator("..")).not.toHaveAttribute("open", "");
  await expect(
    page.getByRole("button", { name: "Consultar revisiones y facultades", exact: true })
  ).toBeVisible();
  expect(await page.evaluate(() => (window as any).posts.length)).toBe(0);
});
