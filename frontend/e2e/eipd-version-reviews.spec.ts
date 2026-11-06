import { test, expect, type Page } from "@playwright/test";
import { browserBundle } from "./helpers/browser-bundle";
import path from "node:path";

const org = "10000000-0000-0000-0000-000000000001";
const tid = "10000000-0000-0000-0000-000000000002";
const aid = "10000000-0000-0000-0000-000000000003";
const vid = "10000000-0000-0000-0000-000000000004";
const faculty = "10000000-0000-0000-0000-000000000005";
const actor = "10000000-0000-0000-0000-000000000006";
let bundle: string;
test.setTimeout(30000);
test.beforeAll(async () => {
  bundle =
    await browserBundle(`import React from "react";import {createRoot} from "react-dom/client";
    import {EipdVersionReviews} from ${JSON.stringify(path.resolve("components/licitud/EipdVersionReviews.tsx"))};
    createRoot(document.getElementById("root")).render(React.createElement(EipdVersionReviews,{
      version:{id:${JSON.stringify(vid)},version:3,bundle:{saved_assessment:{eipd_resolution_assessment:{document_reference:"SIMULADA-V3"}}}},
      scope:async()=>({organizationId:${JSON.stringify(org)},treatmentId:${JSON.stringify(tid)},assessmentId:${JSON.stringify(aid)},token:"fixture-token"}),
      onLock:v=>window.locked=v
    }));`);
});
async function setup(page: Page, mode = "ok") {
  await page.route("http://localhost:3000/fixture", (route) =>
    route.fulfill({
      contentType: "text/html",
      body: '<div id="root"></div>',
    })
  );
  await page.goto("http://localhost:3000/fixture");
  await page.evaluate(
    ({ org, tid, aid, vid, faculty, actor, mode }) => {
      const w = window as any;
      w.posts = [];
      w.reviews = [];
      w.faculties = [];
      w.lost = false;
      w.fetch = async (url: string, init: any = {}) => {
        const reply = (data: any, status = 200) =>
          new Response(JSON.stringify(data), {
            status,
            headers: { "Content-Type": "application/json" },
          });
        if (url.endsWith("/review-state"))
          return reply({
            version_id: mode === "foreign" ? aid : vid,
            organization_id: org,
            treatment_id: tid,
            assessment_id: aid,
            reviews: w.reviews,
            authority_id: faculty,
            can_review: mode !== "blocked",
            blocked_reason:
              mode === "blocked" ? "No puedes revisar una versión registrada por ti" : null,
            can_favorable: mode === "complete",
            may_manage: true,
            authorities: w.faculties,
          });
        if ((init.method || "GET") === "POST") {
          const b = JSON.parse(init.body);
          w.posts.push(b);
          if (url.endsWith("/review-authorities")) {
            w.faculties.push({
              ...b,
              id: faculty,
              sequence: b.expected_sequence + 1,
              created_by: actor,
              created_at: "2026-11-05T12:00:00Z",
            });
            return reply(w.faculties.at(-1), 201);
          }
          if (mode === "conflict")
            return reply({ detail: "La revisión previa cambió; consulta el historial" }, 409);
          const review = {
            ...b,
            id: crypto.randomUUID(),
            version_id: vid,
            sequence: w.reviews.length + 1,
            previous_id: b.expected_previous_id,
            created_by: actor,
            created_at: "2026-11-05T12:00:00Z",
          };
          if (!w.lost || mode !== "missing") w.reviews.push(review);
          if ((mode === "lost" || mode === "missing") && !w.lost) {
            w.lost = true;
            if (mode === "missing") w.reviews = [];
            throw new TypeError("Respuesta perdida");
          }
          if (mode === "missing" && !w.reviews.length) w.reviews.push(review);
          return reply(review, 201);
        }
        if (url.includes("/review-requests/")) {
          const found = w.reviews.find((r: any) => url.endsWith(r.request_id));
          return found ? reply(found) : reply({ detail: "No encontrada" }, 404);
        }
        throw new Error("Unexpected fixture request");
      };
    },
    { org, tid, aid, vid, faculty, actor, mode }
  );
  await page.addScriptTag({ content: bundle });
  await page.getByRole("button", { name: "Consultar revisiones y facultades" }).click();
}
async function fill(page: Page) {
  await page.getByLabel("Fundamento de la revisión").fill("[FICTICIA] Se requieren antecedentes");
  await page.getByLabel("Referencia de respaldo de la revisión").fill("SIMULADA-INFORME");
  await page.getByLabel("Declaro datos ficticios para esta revisión").check();
}

test("review and reconsideration preserve exact version and expected predecessor", async ({
  page,
}) => {
  await setup(page);
  await fill(page);
  await expect(page.getByRole("option", { name: "Favorable", exact: true })).toHaveAttribute(
    "disabled",
    ""
  );
  await page.getByRole("button", { name: "Registrar revisión", exact: true }).click();
  await expect(page.getByText("1. Requiere cambios")).toBeVisible();
  await fill(page);
  await page.getByRole("combobox", { name: /Resultado/ }).selectOption("no_continuar");
  await page.getByRole("button", { name: "Registrar reconsideración", exact: true }).click();
  await expect(page.getByText("2. No continuar")).toBeVisible();
  const posts = await page.evaluate(() => (window as any).posts);
  const reviews = await page.evaluate(() => (window as any).reviews);
  expect(posts[0].expected_previous_id).toBeNull();
  expect(posts[1].expected_previous_id).toBe(reviews[0].id);
  expect(posts[0].authority_id).toBe(faculty);
});

test("author block is explained and no review can be submitted", async ({ page }) => {
  await setup(page, "blocked");
  await expect(page.getByText("No puedes revisar una versión registrada por ti")).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Registrar revisión", exact: true })
  ).toBeDisabled();
  expect(await page.evaluate(() => (window as any).posts)).toEqual([]);
});

for (const mode of ["lost", "missing"]) {
  test("uncertain response recovers without duplicating: " + mode, async ({ page }) => {
    await setup(page, mode);
    await fill(page);
    await page.getByRole("button", { name: "Registrar revisión", exact: true }).click();
    await expect(
      page.getByText("Resultado pendiente de comprobar.", { exact: false })
    ).toBeVisible();
    await expect.poll(() => page.evaluate(() => (window as any).locked)).toBe(true);
    await page.getByRole("button", { name: "Consultar resultado de la revisión" }).click();
    if (mode === "missing")
      await page.getByRole("button", { name: "Reintentar la misma revisión" }).click();
    await expect(page.getByText("1. Requiere cambios")).toBeVisible();
    const posts = await page.evaluate(() => (window as any).posts);
    expect(posts).toHaveLength(mode === "lost" ? 1 : 2);
    if (posts.length === 2) expect(posts[1]).toEqual(posts[0]);
  });
}

test("conflict preserves fields and requires a fresh history consultation", async ({ page }) => {
  await setup(page, "conflict");
  await fill(page);
  await page.getByRole("button", { name: "Registrar revisión", exact: true }).click();
  await expect(page.getByRole("alert")).toContainText("revisión previa cambió");
  await page.getByRole("button", { name: "Consultar revisiones y facultades" }).click();
  await expect(page.getByLabel("Fundamento de la revisión")).toHaveValue(
    "[FICTICIA] Se requieren antecedentes"
  );
});

test("foreign state is rejected without enabling review", async ({ page }) => {
  await setup(page, "foreign");
  await expect(page.getByRole("alert")).toContainText("incompatible");
  await expect(page.getByRole("button", { name: "Registrar revisión", exact: true })).toHaveCount(
    0
  );
});

test("faculty grant and revoke use independent sequences and retain reasons", async ({ page }) => {
  await setup(page);
  await page.getByText("Administrar facultad de revisión del expediente", { exact: true }).click();
  await page.getByLabel("Identificador de la persona destinataria").fill(actor);
  await page.getByLabel("Motivo de la facultad").fill("[FICTICIA] Designación");
  await page.getByLabel("Referencia de respaldo de la facultad").fill("SIMULADA-ACTA");
  await page.getByRole("button", { name: "Registrar actuación de facultad" }).click();
  await page.getByRole("combobox", { name: /Actuación/ }).selectOption("revoke");
  await page.getByLabel("Motivo de la facultad").fill("[FICTICIA] Revocación");
  await page.getByLabel("Referencia de respaldo de la facultad").fill("SIMULADA-ACTA-2");
  await page.getByRole("button", { name: "Registrar actuación de facultad" }).click();
  const posts = await page.evaluate(() => (window as any).posts);
  expect(posts.map((p: any) => [p.action, p.expected_sequence])).toEqual([
    ["grant", 0],
    ["revoke", 1],
  ]);
});

test("keyboard and narrow viewport retain readable form and explicit discard", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 850 });
  await setup(page, "complete");
  await expect(page.getByRole("option", { name: "Favorable", exact: true })).toBeEnabled();
  await page.getByRole("combobox", { name: /Resultado/ }).selectOption("favorable");
  await fill(page);
  await expect.poll(() => page.evaluate(() => (window as any).locked)).toBe(true);
  const discard = page.getByRole("button", {
    name: "Descartar campos de revisión y facultad sin registrar",
  });
  await discard.focus();
  await page.keyboard.press("Enter");
  await expect(page.getByLabel("Fundamento de la revisión")).toHaveValue("");
  await expect.poll(() => page.evaluate(() => (window as any).locked)).toBe(false);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(
    true
  );
});
