import { test, expect, type Page } from "@playwright/test";
import { rm, mkdir } from "node:fs/promises";
import path from "node:path";
import { buildConnectedHarness } from "./helpers/connected-harness";
let directory: string, script: string, css: string;
let viewerHarness: Awaited<ReturnType<typeof buildConnectedHarness>>;
let editorHarness: Awaited<ReturnType<typeof buildConnectedHarness>>;
const org = "a0000000-0000-0000-0000-000000000001";
const tid = "a0000000-0000-0000-0000-000000000002";
const aid = "a0000000-0000-0000-0000-000000000003";
const aid2 = "a0000000-0000-0000-0000-000000000004";
const series = "a0000000-0000-0000-0000-000000000005";
const organization = {
  id: org,
  name: "[FICTICIA] Organización conectada",
  role: "owner",
  rut: null,
  size: null,
  industry: null,
};
let releaseValidation: (() => void) | undefined;
let releaseApplicability: (() => void) | undefined;
let records: Record<string, any>,
  determinations: Record<string, any>,
  calls: { path: string; method: string; org: string | null; body: any }[],
  errors: string[],
  mode: string;
const detail = {
  id: tid,
  organization_id: org,
  name: "[FICTICIA] Actividad mixta",
  status: "borrador",
  description: "PRUEBA alcance",
  organization_role: "responsable",
  business_area: "PRUEBA",
  data_flow_description: "PRUEBA",
  start_date: null,
  last_reviewed_at: null,
  next_review_at: null,
  retention_rule: "PRUEBA",
  deletion_method: "PRUEBA",
  has_automated_decisions: false,
  automated_decision_description: null,
  systems_declaration: "sin_sistemas",
  vendors_declaration: "sin_proveedores",
  international_transfers_declaration: "sin_transferencias",
  purposes: [
    { id: series, purpose: "[FICTICIA] Finalidad de prueba", is_primary: true, sort_order: 0 },
  ],
  data_categories: [
    {
      category_code: "identificacion",
      category_name: "Identificación",
      is_sensitive: false,
      notes: null,
    },
  ],
  data_subjects: [
    {
      category_code: "clientes",
      category_name: "Clientes",
      includes_children: true,
      includes_adolescents: false,
      notes: null,
    },
  ],
  data_sources: [],
  systems: [],
  vendors: [],
  international_transfers: [],
};
function assessment(id: string, version: number) {
  return {
    id,
    series_id: series,
    organization_id: org,
    treatment_id: tid,
    version,
    status: "borrador",
    purpose_snapshot: "[FICTICIA] Finalidad de prueba",
    rat_context_hash: "a".repeat(64),
    rat_context_snapshot: detail,
    legal_basis: null,
    justification: "[FICTICIA] Fundamento inicial",
    lia_assessment: null,
    child_adolescent_assessment: null,
    eipd_resolution_assessment: null,
  };
}
function applicability(id: string) {
  return (
    determinations[id] ?? {
      organization_id: org,
      treatment_id: tid,
      assessment_id: id,
      context_hash: "a".repeat(64),
      revision: 0,
      current: false,
      editable: true,
      eipd: { state: "pendiente", reason: "" },
      infancia: { state: "pendiente", reason: "" },
      history: [],
      can_confirm: false,
      activation: "deshabilitada",
    }
  );
}
test.setTimeout(30000);
test.beforeAll(async () => {
  ({ directory, script, css } = await buildConnectedHarness([organization], "http://test.invalid"));
  viewerHarness = await buildConnectedHarness(
    [{ ...organization, role: "viewer" }],
    "http://test.invalid"
  );
  editorHarness = await buildConnectedHarness(
    [{ ...organization, role: "editor" }],
    "http://test.invalid"
  );
});
test.afterAll(async () => {
  if (directory) await rm(directory, { recursive: true, force: true });
  for (const harness of [viewerHarness, editorHarness]) {
    if (harness) await rm(harness.directory, { recursive: true, force: true });
  }
});
async function capture(page: Page, name: string) {
  const dir = process.env.CONNECTED_SCREENSHOTS;
  if (dir) {
    await mkdir(dir, { recursive: true });
    await page.screenshot({ path: path.join(dir, name), fullPage: false });
  }
}
async function visit(page: Page, hash = "", bundle = script) {
  await page.goto("http://localhost:3999/" + hash);
  await page.addStyleTag({ content: css });
  await page.addScriptTag({ content: bundle });
  await expect(page.getByRole("heading", { name: "Panel principal", exact: true })).toBeVisible();
}
test.beforeEach(async ({ page }) => {
  records = { [aid]: assessment(aid, 1), [aid2]: assessment(aid2, 2) };
  determinations = {};
  calls = [];
  errors = [];
  mode = "ok";
  releaseValidation = undefined;
  releaseApplicability = undefined;
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("dialog", async (d) => (d.type() === "beforeunload" ? d.accept() : d.dismiss()));
  await page.route("**/*", async (route) => {
    const req = route.request(),
      url = new URL(req.url());
    if (url.hostname === "localhost")
      return route.fulfill({ contentType: "text/html", body: '<div id="root"></div>' });
    if (url.hostname !== "test.invalid") return route.abort();
    const headers = {
      "access-control-allow-origin": "*",
      "access-control-allow-headers": "*",
      "access-control-allow-methods": "GET,POST,PATCH,OPTIONS",
    };
    if (req.method() === "OPTIONS") return route.fulfill({ status: 204, headers });
    const pathname = url.pathname,
      method = req.method(),
      body = req.postDataJSON();
    calls.push({ path: pathname, method, org: req.headers()["x-organization-id"] ?? null, body });
    const result = (value: any, status = 200) =>
      route.fulfill({
        status,
        headers,
        contentType: "application/json",
        body: JSON.stringify(value),
      });
    if (mode === "deny" && pathname.startsWith("/rat"))
      return result({ detail: "PRUEBA sin acceso" }, 403);
    if (pathname === "/rat/treatments") return result([detail]);
    if (pathname === `/rat/treatments/${tid}`) {
      if (mode === "hold")
        await new Promise<void>((resolve) => {
          releaseValidation = resolve;
        });
      return result(detail);
    }
    if (pathname === "/diagnostico/cuestionario")
      return result({
        secciones: [
          { id: "s1", orden: 1, numero_romano: "I", nombre: "Sección inicial" },
          { id: "s2", orden: 2, numero_romano: "II", nombre: "Sección final" },
        ],
        preguntas: Array.from({ length: 50 }, (_, i) => ({
          id: `q${i + 1}`,
          seccion_id: i < 25 ? "s1" : "s2",
          orden: i + 1,
          texto: `[FICTICIA] Pregunta ${i + 1}`,
        })),
      });
    if (pathname === "/diagnostico/actual") return result({ detail: "No existe" }, 404);
    if (pathname.endsWith("/assessments"))
      return result(url.searchParams.get("offset") === "50" ? [] : Object.values(records));
    const match = pathname.match(/\/assessments\/([^/]+)/);
    const id = match?.[1] ?? aid;
    if (pathname.endsWith("/applicability")) {
      if (method === "GET" && mode === "app-readonly")
        return result({ ...applicability(id), editable: false });
      if (method === "GET" && mode === "app-offline") return route.abort("internetdisconnected");
      if (method === "GET" && ["app-hold-fail", "app-hold"].includes(mode)) {
        const fail = mode === "app-hold-fail";
        await new Promise<void>((resolve) => {
          releaseApplicability = resolve;
        });
        if (fail) return result({ detail: "PRUEBA determinación no disponible" }, 503);
      }
      if (method === "GET" && mode === "app-fail")
        return result({ detail: "PRUEBA determinación no disponible" }, 503);
      if (method === "POST") {
        const prev = applicability(id);
        if (mode === "conflict" || body.expected_revision !== prev.revision)
          return result({ detail: "PRUEBA cambio concurrente" }, 409);
        determinations[id] = {
          ...prev,
          ...body,
          revision: prev.revision + 1,
          current: true,
          history: [
            ...prev.history,
            {
              revision: prev.revision + 1,
              created_at: "2026-10-25",
              created_by: "PRUEBA",
              eipd: body.eipd,
              infancia: body.infancia,
            },
          ],
        };
      }
      return result(
        mode === "wrong-applicability"
          ? { ...applicability(id), assessment_id: aid2 }
          : applicability(id)
      );
    }
    if (pathname.endsWith("/support"))
      return result({
        schema_version: 1,
        organization_id: org,
        treatment_id: tid,
        assessment_id: id,
        document_hash: "a".repeat(64),
        risk_evaluation: null,
        risk_history: [],
        annexes: [],
        can_confirm: false,
        activation: "deshabilitada",
      });
    if (pathname.endsWith("/readiness"))
      return result({ assessment_id: id, rat_context_current: true, eipd_controls_v5: null });
    if (pathname.endsWith("/eipd-child/v4/resolutions")) return result([]);
    if (pathname.endsWith("/eipd-child/v4/policy"))
      return result({
        policy: {
          policy_schema_version: 1,
          policy_reference: "PRUEBA",
          sources_status: "pendiente",
          acceptance_status: "pendiente",
          activation: "deshabilitada",
          allowed_decisions: ["requiere_cambios", "no_continuar"],
          global_policy_identity: {
            policy_version: 1,
            policy_reference: "PRUEBA",
            policy_hash: "d".repeat(64),
          },
        },
        policy_hash: "e".repeat(64),
        authorizes_action: false,
        can_confirm: false,
      });
    if (match && records[id] && pathname.endsWith(id)) {
      if (method === "PATCH") records[id] = { ...records[id], ...body };
      return result(records[id]);
    }
    return result({ detail: "Ruta de prueba no implementada" }, 404);
  });
  await visit(page);
});
const main = (page: Page) => page.locator("main.prototype-work");
async function mod(page: Page, name: string) {
  const mobile = page.getByRole("button", { name: "Abrir menú", exact: true });
  if (await mobile.isVisible()) await mobile.click();
  await page
    .getByRole("navigation", { name: "Módulos de la maqueta" })
    .getByRole("button", { name, exact: true })
    .click();
}
async function section(page: Page, name: string) {
  await page.locator("header").getByRole("button", { name: "Secciones", exact: true }).click();
  await page
    .getByRole("dialog", { name: "Secciones del módulo", exact: true })
    .getByRole("button", { name, exact: true })
    .click();
}
async function choose(page: Page, id = aid) {
  await page.getByRole("button", { name: "Cambiar contexto", exact: true }).click();
  const dialog = page.getByRole("dialog", { name: "Contexto de trabajo", exact: true });
  await dialog.getByLabel("Tratamiento del RAT", { exact: true }).selectOption(tid);
  await dialog.getByLabel("Finalidad de la evaluación", { exact: true }).selectOption(series);
  await dialog.getByLabel("Evaluación", { exact: true }).selectOption(id);
  await dialog.getByRole("button", { name: "Aplicar contexto", exact: true }).click();
  await expect(dialog).not.toBeVisible();
}
async function legal(page: Page) {
  await choose(page);
  await mod(page, "Bases de licitud");
  await expect(
    main(page).getByRole("heading", { name: "Determinar aplicabilidad", exact: true })
  ).toBeVisible();
}
async function enable(page: Page) {
  await main(page)
    .getByLabel("¿Corresponde documentar EIPD?", { exact: true })
    .selectOption("corresponde");
  await main(page)
    .getByLabel("Fundamento sobre EIPD", { exact: true })
    .fill("[FICTICIA] Revisión manual");
  await main(page)
    .getByLabel("Declaro que esta prueba utiliza únicamente datos ficticios.")
    .check();
  await main(page).getByRole("button", { name: "Guardar determinación", exact: true }).click();
  await expect(
    main(page).getByText("Determinación guardada en el servidor.", { exact: true })
  ).toBeVisible();
}

test("catálogo de 50 preguntas, borrador entre módulos y contexto cancelado", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await mod(page, "Autodiagnóstico");
  await expect(main(page).getByText("0 / 50 preguntas respondidas", { exact: true })).toBeVisible();
  await main(page)
    .getByPlaceholder("Notas u observaciones (opcional)")
    .first()
    .fill("[FICTICIA] Nota conservada");
  await section(page, "II. Sección final");
  await expect(main(page).getByText("[FICTICIA] Pregunta 50", { exact: true })).toBeVisible();
  await section(page, "I. Sección inicial");
  await mod(page, "Panel principal");
  await mod(page, "Autodiagnóstico");
  await expect(main(page).getByPlaceholder("Notas u observaciones (opcional)").first()).toHaveValue(
    "[FICTICIA] Nota conservada"
  );
  await page.getByRole("button", { name: "Cambiar contexto", exact: true }).click();
  await page.getByRole("dialog").getByRole("button", { name: "Cancelar", exact: true }).click();
  await expect(main(page).getByPlaceholder("Notas u observaciones (opcional)").first()).toHaveValue(
    "[FICTICIA] Nota conservada"
  );
  expect(errors).toEqual([]);
});
test("aplicabilidad guardada, aislamiento, enlaces y reapertura desde servidor", async ({
  page,
}) => {
  await legal(page);
  await page.locator("header").getByRole("button", { name: "Secciones", exact: true }).click();
  await expect(
    page.getByRole("dialog").getByText("Completar EIPD", { exact: true })
  ).not.toBeVisible();
  await page.keyboard.press("Escape");
  await enable(page);
  await capture(page, "conectada-aplicabilidad-escritorio.png");
  await section(page, "Medidas de mitigación");
  await expect(main(page).getByText("Determinar aplicabilidad", { exact: true })).not.toBeVisible();
  await section(page, "Base y fundamento");
  await main(page)
    .getByRole("textbox", { name: "Fundamento", exact: true })
    .fill("[FICTICIA] Borrador uno");
  await choose(page, aid2);
  await expect(
    main(page).getByRole("heading", { name: "Determinar aplicabilidad", exact: true })
  ).toBeVisible();
  await choose(page, aid);
  await section(page, "Base y fundamento");
  await expect(main(page).getByRole("textbox", { name: "Fundamento", exact: true })).toHaveValue(
    "[FICTICIA] Borrador uno"
  );
  await page.reload();
  await page.addStyleTag({ content: css });
  await page.addScriptTag({ content: script });
  await expect(main(page).getByRole("textbox", { name: "Fundamento", exact: true })).toHaveValue(
    "[FICTICIA] Fundamento inicial"
  );
  await section(page, "Determinar aplicabilidad");
  await expect(main(page).getByLabel("¿Corresponde documentar EIPD?", { exact: true })).toHaveValue(
    "corresponde"
  );
  expect(
    calls
      .filter((v) => v.path.endsWith("/applicability") && v.method === "POST")
      .every((v) => v.org === org)
  ).toBe(true);
  expect(errors).toEqual([]);
});
test("conflicto conserva determinación pendiente y no habilita menú", async ({ page }) => {
  await legal(page);
  mode = "conflict";
  await main(page)
    .getByLabel("¿Corresponde documentar EIPD?", { exact: true })
    .selectOption("corresponde");
  await main(page)
    .getByLabel("Fundamento sobre EIPD", { exact: true })
    .fill("[FICTICIA] No sobrescribir");
  await main(page)
    .getByLabel("Declaro que esta prueba utiliza únicamente datos ficticios.")
    .check();
  await main(page).getByRole("button", { name: "Guardar determinación", exact: true }).click();
  await expect(main(page).getByRole("alert")).toContainText("cambio concurrente");
  await expect(main(page).getByLabel("Fundamento sobre EIPD", { exact: true })).toHaveValue(
    "[FICTICIA] No sobrescribir"
  );
  expect(Object.keys(determinations)).toHaveLength(0);
  expect(errors).toEqual([]);
});
test("móvil: foco, Escape, clic exterior y límites de pantalla", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 740 });
  await legal(page);
  await enable(page);
  await page.locator("header").getByRole("button", { name: "Secciones", exact: true }).click();
  const drawer = page.getByRole("dialog", { name: "Secciones del módulo", exact: true });
  await drawer.getByRole("button").last().focus();
  await page.keyboard.press("Escape");
  await expect(drawer).not.toBeVisible();
  await page.locator("header").getByRole("button", { name: "Secciones", exact: true }).click();
  await capture(page, "conectada-secciones-movil.png");
  const box = (await drawer.boundingBox())!;
  await page.mouse.click((box.width + 320) / 2, 300);
  await expect(drawer).not.toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  expect(errors).toEqual([]);
});
test("contexto rechazado no se aplica ni produce escrituras", async ({ page }) => {
  mode = "deny";
  await page.getByRole("button", { name: "Cambiar contexto", exact: true }).click();
  const dialog = page.getByRole("dialog", { name: "Contexto de trabajo", exact: true });
  await expect(dialog.getByRole("alert")).toContainText("sin acceso");
  await expect(
    dialog.getByRole("button", { name: "Aplicar contexto", exact: true })
  ).toBeDisabled();
  await dialog.getByRole("button", { name: "Cancelar", exact: true }).click();
  expect(calls.some((v) => v.method !== "GET")).toBe(false);
  expect(errors).toEqual([]);
});

test("RAT conserva campos entre secciones y nueva actividad al volver del catálogo", async ({
  page,
}) => {
  await choose(page);
  await mod(page, "Inventario de tratamientos");
  await section(page, "Información general");
  const name = main(page).getByRole("textbox", { name: "Nombre de la actividad *", exact: true });
  await name.fill("[FICTICIA] Nombre pendiente");
  await section(page, "Finalidades");
  await section(page, "Información general");
  await expect(name).toHaveValue("[FICTICIA] Nombre pendiente");
  await section(page, "Nueva actividad");
  const fresh = main(page).getByRole("textbox", { name: "Nombre de la actividad *", exact: true });
  await fresh.fill("[FICTICIA] Nueva actividad pendiente");
  await section(page, "Catálogo de tratamientos");
  await section(page, "Nueva actividad");
  await expect(
    main(page).getByRole("textbox", { name: "Nombre de la actividad *", exact: true })
  ).toHaveValue("[FICTICIA] Nueva actividad pendiente");
  expect(errors).toEqual([]);
});

test("cancelar validación lenta impide que una respuesta tardía cambie el contexto", async ({
  page,
}) => {
  await page.getByRole("button", { name: "Cambiar contexto", exact: true }).click();
  const dialog = page.getByRole("dialog", { name: "Contexto de trabajo", exact: true });
  await dialog.getByLabel("Tratamiento del RAT", { exact: true }).selectOption(tid);
  await dialog.getByLabel("Finalidad de la evaluación", { exact: true }).selectOption(series);
  await dialog.getByLabel("Evaluación", { exact: true }).selectOption(aid);
  mode = "hold";
  await dialog.getByRole("button", { name: "Aplicar contexto", exact: true }).click();
  await expect.poll(() => !!releaseValidation).toBe(true);
  await expect(
    dialog.getByRole("button", { name: "Aplicar contexto", exact: true })
  ).toBeDisabled();
  await dialog.getByRole("button", { name: "Cancelar", exact: true }).click();
  const response = page.waitForResponse((v) => v.url().endsWith(`/rat/treatments/${tid}`));
  releaseValidation!();
  await response;
  await expect(page.locator("header")).not.toContainText("Actividad mixta");
  await expect(
    main(page).getByRole("heading", { name: "Panel principal", exact: true })
  ).toBeVisible();
  expect(errors).toEqual([]);
});

test("Atrás y Adelante restauran evaluación sin mezclar borradores", async ({ page }) => {
  await legal(page);
  await section(page, "Base y fundamento");
  await main(page)
    .getByRole("textbox", { name: "Fundamento", exact: true })
    .fill("[FICTICIA] Contexto uno pendiente");
  await choose(page, aid2);
  await expect(
    main(page).getByRole("heading", { name: "Determinar aplicabilidad", exact: true })
  ).toBeVisible();
  await page.goBack();
  await expect(main(page).getByRole("textbox", { name: "Fundamento", exact: true })).toHaveValue(
    "[FICTICIA] Contexto uno pendiente"
  );
  await page.goForward();
  await expect(
    main(page).getByRole("heading", { name: "Determinar aplicabilidad", exact: true })
  ).toBeVisible();
  expect(errors).toEqual([]);
});

test("cancelar cierre de sesión conserva el borrador del cuestionario", async ({ page }) => {
  await mod(page, "Autodiagnóstico");
  const note = main(page).getByPlaceholder("Notas u observaciones (opcional)").first();
  await note.fill("[FICTICIA] No descartar al cancelar salida");
  await page.getByRole("button", { name: "Cerrar sesión", exact: true }).click();
  const dialog = page.getByRole("dialog", { name: "Salir del espacio de trabajo", exact: true });
  await expect(dialog).toBeVisible();
  await dialog.getByRole("button", { name: "Continuar editando", exact: true }).click();
  await expect(dialog).not.toBeVisible();
  await expect(note).toHaveValue("[FICTICIA] No descartar al cancelar salida");
  expect(errors).toEqual([]);
});

test("respuesta de otra evaluación no habilita formularios ni permite guardar", async ({
  page,
}) => {
  mode = "wrong-applicability";
  await legal(page);
  await expect(main(page).getByRole("alert")).toContainText("no corresponde al contexto");
  await expect(
    main(page).getByRole("button", { name: "Guardar determinación", exact: true })
  ).toBeDisabled();
  expect(calls.some((v) => v.method !== "GET")).toBe(false);
  expect(errors).toEqual([]);
});

for (const target of ["eipd", "infancia", "preparar"]) {
  test(`enlace directo a ${target}: carga, error visible y reintento`, async ({ page }) => {
    if (target !== "eipd")
      await page.setViewportSize({ width: target === "infancia" ? 390 : 320, height: 844 });
    determinations[aid] = {
      ...applicability(aid),
      current: true,
      revision: 1,
      eipd: { state: "corresponde", reason: "[FICTICIA] EIPD" },
      infancia: { state: "corresponde", reason: "[FICTICIA] Infancia" },
    };
    mode = "app-hold-fail";
    await page.evaluate((hash) => {
      window.location.hash = hash;
    }, `#/licitud/${target}?organizationId=${org}&treatmentId=${tid}&assessmentId=${aid}`);
    await expect(main(page).getByRole("status")).toContainText(
      "Cargando evaluación y aplicabilidad"
    );
    await expect.poll(() => !!releaseApplicability).toBe(true);
    await capture(page, `lote1-${target}-cargando.png`);
    releaseApplicability!();
    await expect(main(page).getByRole("alert")).toContainText("PRUEBA determinación no disponible");
    await expect(
      main(page).getByRole("button", { name: "Ir a Determinar aplicabilidad", exact: true })
    ).toBeVisible();
    await capture(page, `lote1-${target}-error.png`);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(
      true
    );
    mode = "ok";
    await main(page).getByRole("button", { name: "Reintentar consulta", exact: true }).click();
    await expect(
      main(page).getByRole("alert").filter({ hasText: "No se pudo consultar la aplicabilidad" })
    ).not.toBeVisible();
    await expect(
      main(page).getByText(
        "Recorrido conectado al servidor · Solo datos ficticios. Guardar y revisar no confirman ni activan EIPD.",
        { exact: true }
      )
    ).toBeVisible();
    await expect(page).toHaveURL(new RegExp(`/licitud/${target}\\?`));
    expect(calls.some((v) => v.method !== "GET")).toBe(false);
    expect(errors).toEqual([]);
  });
}

test("recuperar aplicabilidad conserva borradores de determinación y base", async ({ page }) => {
  await legal(page);
  await enable(page);
  await section(page, "Base y fundamento");
  await main(page)
    .getByRole("textbox", { name: "Fundamento", exact: true })
    .fill("[FICTICIA] Base pendiente conservada");
  await section(page, "Determinar aplicabilidad");
  await main(page)
    .getByLabel("Fundamento sobre EIPD", { exact: true })
    .fill("[FICTICIA] Determinación pendiente conservada");
  mode = "app-fail";
  await main(page)
    .getByRole("button", {
      name: "Actualizar estado guardado sin descartar el borrador",
      exact: true,
    })
    .click();
  await expect(main(page).getByRole("alert")).toContainText("PRUEBA determinación no disponible");
  await section(page, "Tratamiento y alcance de la EIPD");
  await expect(main(page).getByRole("alert")).toContainText("PRUEBA determinación no disponible");
  await main(page)
    .getByRole("button", { name: "Ir a Determinar aplicabilidad", exact: true })
    .click();
  await expect(main(page).getByLabel("Fundamento sobre EIPD", { exact: true })).toHaveValue(
    "[FICTICIA] Determinación pendiente conservada"
  );
  mode = "ok";
  await main(page)
    .getByRole("button", {
      name: "Actualizar estado guardado sin descartar el borrador",
      exact: true,
    })
    .click();
  await expect(main(page).getByRole("alert")).not.toBeVisible();
  await expect(main(page).getByLabel("Fundamento sobre EIPD", { exact: true })).toHaveValue(
    "[FICTICIA] Determinación pendiente conservada"
  );
  await section(page, "Base y fundamento");
  await expect(main(page).getByRole("textbox", { name: "Fundamento", exact: true })).toHaveValue(
    "[FICTICIA] Base pendiente conservada"
  );
  expect(calls.filter((v) => v.method === "POST")).toHaveLength(1);
  expect(errors).toEqual([]);
});

test("validación de enlace muestra carga fuera del diálogo y permite reintentar", async ({
  page,
}) => {
  mode = "hold";
  await page.evaluate((hash) => {
    window.location.hash = hash;
  }, `#/licitud/base?organizationId=${org}&treatmentId=${tid}&assessmentId=${aid}`);
  await expect(page.getByRole("status")).toContainText(
    "Consultando evaluación y contexto autorizado"
  );
  await expect.poll(() => !!releaseValidation).toBe(true);
  mode = "deny";
  releaseValidation!();
  // The held treatment response is accepted; retry is exercised after a fresh denied link.
  await expect(main(page).getByRole("textbox", { name: "Fundamento", exact: true })).toBeVisible();
  await page.evaluate((hash) => {
    window.location.hash = hash;
  }, `#/licitud/base?organizationId=${org}&treatmentId=${tid}&assessmentId=${aid2}`);
  await expect(page.getByRole("alert")).toContainText("PRUEBA sin acceso");
  mode = "ok";
  await page.getByRole("button", { name: "Reintentar apertura", exact: true }).click();
  await expect(page.getByRole("alert")).not.toBeVisible();
  await expect(page).toHaveURL(new RegExp(`assessmentId=${aid2}`));
  expect(calls.some((v) => v.method !== "GET")).toBe(false);
  expect(errors).toEqual([]);
});

test("desconexión muestra ayuda en español y se recupera sin descartar el borrador", async ({
  page,
}) => {
  await legal(page);
  await main(page)
    .getByLabel("Fundamento sobre EIPD", { exact: true })
    .fill("[FICTICIA] Texto pendiente durante desconexión");
  mode = "app-offline";
  await main(page)
    .getByRole("button", {
      name: "Actualizar estado guardado sin descartar el borrador",
      exact: true,
    })
    .click();
  await expect(main(page).getByRole("alert")).toContainText(
    "No se pudo conectar con el servidor. Revisa la conexión y vuelve a intentar."
  );
  await expect(main(page).getByRole("alert")).not.toContainText("Failed to fetch");
  mode = "ok";
  await main(page)
    .getByRole("button", {
      name: "Actualizar estado guardado sin descartar el borrador",
      exact: true,
    })
    .click();
  await expect(main(page).getByRole("alert")).not.toBeVisible();
  await expect(main(page).getByLabel("Fundamento sobre EIPD", { exact: true })).toHaveValue(
    "[FICTICIA] Texto pendiente durante desconexión"
  );
  expect(calls.some((v) => v.method !== "GET")).toBe(false);
  expect(errors).toEqual([]);
});

for (const width of [1280, 390]) {
  test(`contexto visible según módulo y retorno con borrador a ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 844 });
    await legal(page);
    await section(page, "Base y fundamento");
    await main(page)
      .getByRole("textbox", { name: "Fundamento", exact: true })
      .fill("[FICTICIA] Lote 2 conservar");
    const context = page.getByTestId("connected-context-summary");
    await expect(context).toContainText("Organización: [FICTICIA] Organización conectada");
    await expect(context).toContainText("Tratamiento: [FICTICIA] Actividad mixta");
    await expect(context).toContainText(
      "Finalidad y evaluación: [FICTICIA] Finalidad de prueba · versión 1 · borrador"
    );
    for (const moduleName of ["Autodiagnóstico", "Mi organización", "Panel principal"]) {
      await mod(page, moduleName);
      await expect(context).toHaveText("Organización: [FICTICIA] Organización conectada");
    }
    await mod(page, "Inventario de tratamientos");
    await expect(context).toContainText("Tratamiento: [FICTICIA] Actividad mixta");
    await expect(context).not.toContainText("Finalidad");
    await expect(context).not.toContainText("versión");
    await mod(page, "Bases de licitud");
    await expect(context).toContainText("versión 1 · borrador");
    await expect(main(page).getByRole("textbox", { name: "Fundamento", exact: true })).toHaveValue(
      "[FICTICIA] Lote 2 conservar"
    );
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(
      true
    );
    await capture(page, `lote2-contexto-licitud-${width}.png`);
    expect(calls.some((v) => v.method !== "GET")).toBe(false);
    expect(errors).toEqual([]);
  });
}

test("Continuar identifica evaluación y versión recordadas sin cambiar el destino", async ({
  page,
}) => {
  await legal(page);
  await section(page, "Base y fundamento");
  await main(page)
    .getByRole("textbox", { name: "Fundamento", exact: true })
    .fill("[FICTICIA] Continuar versión uno");
  await choose(page, aid2);
  await section(page, "Base y fundamento");
  await main(page)
    .getByRole("textbox", { name: "Fundamento", exact: true })
    .fill("[FICTICIA] Continuar versión dos");
  await mod(page, "Panel principal");
  const resume = main(page).getByRole("button", { name: /^Continuar en Base y fundamento/ });
  await expect(resume).toContainText("Organización: [FICTICIA] Organización conectada");
  await expect(resume).toContainText("Tratamiento: [FICTICIA] Actividad mixta");
  await expect(resume).toContainText(
    "Finalidad y evaluación: [FICTICIA] Finalidad de prueba · versión 2 · borrador"
  );
  await expect(page.getByTestId("connected-context-summary")).not.toContainText("versión");
  await page.setViewportSize({ width: 320, height: 844 });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await capture(page, "lote2-continuar-320.png");
  await resume.click();
  await expect(main(page).getByRole("textbox", { name: "Fundamento", exact: true })).toHaveValue(
    "[FICTICIA] Continuar versión dos"
  );
  await choose(page, aid);
  await section(page, "Base y fundamento");
  await expect(main(page).getByRole("textbox", { name: "Fundamento", exact: true })).toHaveValue(
    "[FICTICIA] Continuar versión uno"
  );
  expect(calls.some((v) => v.method !== "GET")).toBe(false);
  expect(errors).toEqual([]);
});

test("Continuar al Autodiagnóstico identifica organización y conserva su ámbito", async ({
  page,
}) => {
  await legal(page);
  await mod(page, "Autodiagnóstico");
  await main(page)
    .getByPlaceholder("Notas u observaciones (opcional)")
    .first()
    .fill("[FICTICIA] Diagnóstico organizacional");
  await mod(page, "Panel principal");
  const resume = main(page).getByRole("button", { name: /^Continuar en/ });
  await expect(resume).toContainText("Organización: [FICTICIA] Organización conectada");
  await expect(resume).not.toContainText("Actividad mixta");
  await expect(resume).not.toContainText("versión");
  await resume.click();
  await expect(main(page).getByPlaceholder("Notas u observaciones (opcional)").first()).toHaveValue(
    "[FICTICIA] Diagnóstico organizacional"
  );
  await expect(page.getByTestId("connected-context-summary")).toHaveText(
    "Organización: [FICTICIA] Organización conectada"
  );
  expect(calls.some((v) => v.method !== "GET")).toBe(false);
  expect(errors).toEqual([]);
});

test("Guardar determinación explica requisitos faltantes y los actualiza sin escribir", async ({
  page,
}) => {
  await legal(page);
  const save = main(page).getByRole("button", { name: "Guardar determinación", exact: true });
  await expect(save).toBeDisabled();
  await expect(save).toHaveAccessibleDescription(/declaración de datos ficticios/);
  await main(page)
    .getByLabel("¿Corresponde documentar EIPD?", { exact: true })
    .selectOption("corresponde");
  await expect(save).toHaveAccessibleDescription(/fundamento sobre EIPD/);
  await save.scrollIntoViewIfNeeded();
  await expect(save).toHaveText("Guardar determinación");
  await page.evaluate(
    () =>
      new Promise<void>((resolve) =>
        requestAnimationFrame(() => requestAnimationFrame(() => resolve()))
      )
  );
  await capture(page, "lote3-requisitos-faltantes.png");
  await main(page)
    .getByLabel("Fundamento sobre EIPD", { exact: true })
    .fill("[FICTICIA] Análisis de prueba");
  await expect(save).not.toHaveAccessibleDescription(/fundamento sobre EIPD/);
  await main(page)
    .getByLabel("Declaro que esta prueba utiliza únicamente datos ficticios.")
    .check();
  await expect(save).toBeEnabled();
  await expect(save).toHaveAccessibleDescription(/Requisitos completos/);
  await main(page)
    .getByLabel("¿Corresponde documentar infancia y adolescencia?", { exact: true })
    .selectOption("informacion_insuficiente");
  await expect(save).toBeDisabled();
  await expect(save).toHaveAccessibleDescription(/fundamento sobre infancia y adolescencia/);
  await main(page)
    .getByLabel("Fundamento sobre infancia y adolescencia", { exact: true })
    .fill("[FICTICIA] Información pendiente de contraste");
  await expect(save).toBeEnabled();
  await capture(page, "lote3-requisitos-completos.png");
  expect(calls.some((v) => v.method !== "GET")).toBe(false);
  expect(errors).toEqual([]);
});

test("evaluación de solo consulta explica el bloqueo indicado por servidor", async ({ page }) => {
  mode = "app-readonly";
  await legal(page);
  await expect(main(page).getByLabel("Fundamento sobre EIPD", { exact: true })).toBeDisabled();
  await expect(
    main(page).getByRole("button", { name: "Guardar determinación", exact: true })
  ).toHaveAccessibleDescription(/evaluación.*solo consulta/);
  await expect(
    main(page).getByText(/El servidor indica que esta evaluación es de solo consulta/)
  ).toBeVisible();
  expect(calls.some((v) => v.method !== "GET")).toBe(false);
  expect(errors).toEqual([]);
});

test("rol de consulta ve motivos en aplicabilidad, RAT y organización sin escrituras", async ({
  page,
}) => {
  await visit(page, "", viewerHarness.script);
  await legal(page);
  await expect(main(page).getByLabel("Fundamento sobre EIPD", { exact: true })).toBeDisabled();
  await expect(
    main(page).getByRole("button", { name: "Guardar determinación", exact: true })
  ).toHaveAccessibleDescription(/Tu rol permite solo consulta/);
  await mod(page, "Inventario de tratamientos");
  await section(page, "Información general");
  await expect(
    main(page).getByText(
      "Tu rol permite solo consulta del RAT; no puedes crear ni modificar actividades de tratamiento.",
      { exact: true }
    )
  ).toBeVisible();
  await expect(
    main(page).getByRole("textbox", { name: "Nombre de la actividad *", exact: true })
  ).toBeDisabled();
  await mod(page, "Mi organización");
  await expect(
    main(page).getByText(
      "Tu rol permite consultar los datos de la organización, pero no modificarlos.",
      { exact: true }
    )
  ).toBeVisible();
  await expect(main(page).getByLabel("Nombre de la organización", { exact: true })).toBeDisabled();
  await page.setViewportSize({ width: 320, height: 844 });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await capture(page, "lote3-organizacion-consulta-320.png");
  expect(calls.some((v) => v.method !== "GET")).toBe(false);
  expect(errors).toEqual([]);
});

test("editor puede editar RAT pero recibe explicación de solo consulta en organización", async ({
  page,
}) => {
  await visit(page, "", editorHarness.script);
  await choose(page);
  await mod(page, "Inventario de tratamientos");
  await section(page, "Información general");
  await expect(
    main(page).getByRole("textbox", { name: "Nombre de la actividad *", exact: true })
  ).toBeEnabled();
  await mod(page, "Mi organización");
  await expect(main(page).getByLabel("Nombre de la organización", { exact: true })).toBeDisabled();
  await expect(
    main(page).getByText(
      "Tu rol permite consultar los datos de la organización, pero no modificarlos.",
      { exact: true }
    )
  ).toBeVisible();
  expect(calls.some((v) => v.method !== "GET")).toBe(false);
  expect(errors).toEqual([]);
});

test("contexto explica dependencia y evaluación faltante conservando selección opcional", async ({
  page,
}) => {
  await page.getByRole("button", { name: "Cambiar contexto", exact: true }).click();
  const dialog = page.getByRole("dialog", { name: "Contexto de trabajo", exact: true });
  await expect(
    dialog.getByLabel("Finalidad de la evaluación", { exact: true })
  ).toHaveAccessibleDescription(/Selecciona primero un tratamiento/);
  await expect(dialog.getByLabel("Evaluación", { exact: true })).toHaveAccessibleDescription(
    /después una finalidad/
  );
  const apply = dialog.getByRole("button", { name: "Aplicar contexto", exact: true });
  await expect(apply).toBeEnabled();
  await expect(apply).toHaveAccessibleDescription(/Puedes aplicar solo la organización/);
  await dialog.getByLabel("Tratamiento del RAT", { exact: true }).selectOption(tid);
  await expect(dialog.getByLabel("Finalidad de la evaluación", { exact: true })).toBeEnabled();
  await expect(apply).toHaveAccessibleDescription(/Puedes aplicar organización y tratamiento/);
  await dialog.getByLabel("Finalidad de la evaluación", { exact: true }).selectOption(series);
  await expect(apply).toBeDisabled();
  await expect(apply).toHaveAccessibleDescription(
    /Selecciona una evaluación para la finalidad elegida/
  );
  await capture(page, "lote3-evaluacion-faltante.png");
  await dialog.getByLabel("Evaluación", { exact: true }).selectOption(aid);
  await expect(apply).toBeEnabled();
  await expect(apply).toHaveAccessibleDescription(/El contexto está listo/);
  await capture(page, "lote3-contexto-requisitos.png");
  await dialog.getByRole("button", { name: "Cancelar", exact: true }).click();
  expect(calls.some((v) => v.method !== "GET")).toBe(false);
  expect(errors).toEqual([]);
});

const availability = (page: Page) =>
  main(page).getByRole("region", { name: "Disponibilidad de formularios", exact: true });
const relocation = (page: Page) =>
  main(page).getByRole("region", { name: "Cambio de sección", exact: true });
for (const state of ["pendiente", "corresponde", "no_corresponde", "informacion_insuficiente"]) {
  test(`resultado guardado explica accesos para ambos temas: ${state}`, async ({ page }) => {
    await legal(page);
    await expect(availability(page)).toContainText("Sin determinación guardada");
    for (const topic of ["EIPD", "infancia y adolescencia"]) {
      await main(page)
        .getByLabel(`¿Corresponde documentar ${topic}?`, { exact: true })
        .selectOption(state);
      if (state !== "pendiente")
        await main(page)
          .getByLabel(`Fundamento sobre ${topic}`, { exact: true })
          .fill(`[FICTICIA] Análisis ${topic}`);
    }
    await expect(
      availability(page).getByRole("button", { name: "Completar EIPD", exact: true })
    ).not.toBeVisible();
    await main(page)
      .getByLabel("Declaro que esta prueba utiliza únicamente datos ficticios.")
      .check();
    await main(page).getByRole("button", { name: "Guardar determinación", exact: true }).click();
    await expect(
      main(page).getByText("Determinación guardada en el servidor.", { exact: true })
    ).toBeVisible();
    await expect(availability(page)).toContainText("Accesos según la determinación guardada");
    for (const topic of ["EIPD", "infancia y adolescencia"]) {
      const button = availability(page).getByRole("button", {
        name: `Completar ${topic}`,
        exact: true,
      });
      if (state === "corresponde") await expect(button).toBeVisible();
      else await expect(button).not.toBeVisible();
    }
    if (state === "corresponde") {
      await main(page)
        .getByLabel("¿Corresponde documentar EIPD?", { exact: true })
        .selectOption("no_corresponde");
      await availability(page).getByRole("button", { name: "Completar EIPD", exact: true }).click();
      await expect(page).toHaveURL(/\/licitud\/eipd\?/);
    } else {
      await expect(availability(page)).toContainText("El formulario no está habilitado");
      await availability(page)
        .getByRole("button", { name: "Ir a Revisar y decidir", exact: true })
        .click();
      await expect(page).toHaveURL(/\/licitud\/revisar\?/);
    }
    expect(calls.filter((v) => v.method === "POST")).toHaveLength(1);
    expect(errors).toEqual([]);
  });
}

test("resultado positivo de EIPD no habilita infancia y ofrece acceso directo", async ({
  page,
}) => {
  await legal(page);
  await enable(page);
  await expect(
    availability(page).getByRole("button", { name: "Completar EIPD", exact: true })
  ).toBeVisible();
  await expect(
    availability(page).getByRole("button", {
      name: "Completar infancia y adolescencia",
      exact: true,
    })
  ).not.toBeVisible();
  await availability(page).scrollIntoViewIfNeeded();
  await capture(page, "lote4-resultado-eipd.png");
  await availability(page).getByRole("button", { name: "Completar EIPD", exact: true }).click();
  await expect(page).toHaveURL(/\/licitud\/eipd\?/);
  expect(calls.filter((v) => v.method === "POST")).toHaveLength(1);
  expect(errors).toEqual([]);
});
for (const target of ["eipd", "infancia", "preparar"]) {
  test(`reubicación desde ${target} explica causa y conserva borradores`, async ({ page }) => {
    if (target !== "eipd")
      await page.setViewportSize({ width: target === "infancia" ? 390 : 320, height: 844 });
    determinations[aid] = {
      ...applicability(aid),
      current: true,
      revision: 1,
      eipd: { state: "corresponde", reason: "[FICTICIA] EIPD guardada" },
      infancia: { state: "corresponde", reason: "[FICTICIA] Infancia guardada" },
    };
    await legal(page);
    if (target === "eipd") {
      await section(page, "Tratamiento y alcance de la EIPD");
      await main(page)
        .getByRole("textbox", { name: "Notas del borrador EIPD (opcional)", exact: true })
        .fill("[FICTICIA] Conservar al reubicar");
      await section(page, "Determinar aplicabilidad");
    }
    mode = "app-hold";
    await main(page)
      .getByRole("button", {
        name: "Actualizar estado guardado sin descartar el borrador",
        exact: true,
      })
      .click();
    await expect.poll(() => !!releaseApplicability).toBe(true);
    await section(
      page,
      target === "eipd"
        ? "Tratamiento y alcance de la EIPD"
        : target === "infancia"
          ? "Completar infancia y adolescencia"
          : "Preparar resolución documental"
    );
    const topic = target === "eipd" ? "eipd" : "infancia";
    determinations[aid] = {
      ...determinations[aid],
      revision: 2,
      [topic]: { state: "no_corresponde", reason: "[FICTICIA] Cambio guardado" },
    };
    mode = "ok";
    releaseApplicability!();
    await expect(relocation(page)).toContainText("No corresponde");
    await expect(relocation(page)).toContainText("se conservan durante esta visita");
    await expect(
      relocation(page).getByRole("button", { name: "Ir a Revisar y decidir", exact: true })
    ).toBeVisible();
    await expect(page).toHaveURL(/\/licitud\/aplicabilidad\?/);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(
      true
    );
    await capture(page, `lote4-reubicacion-${target}.png`);
    if (target === "eipd") {
      await expect(relocation(page)).toContainText("Hay cambios sin guardar en esta evaluación");
      determinations[aid] = {
        ...determinations[aid],
        revision: 3,
        eipd: { state: "corresponde", reason: "[FICTICIA] Aplicabilidad restaurada" },
      };
      await main(page)
        .getByRole("button", {
          name: "Actualizar estado guardado sin descartar el borrador",
          exact: true,
        })
        .click();
      await expect(relocation(page)).not.toBeVisible();
      await availability(page).getByRole("button", { name: "Completar EIPD", exact: true }).click();
      await expect(
        main(page).getByRole("textbox", { name: "Notas del borrador EIPD (opcional)", exact: true })
      ).toHaveValue("[FICTICIA] Conservar al reubicar");
    }
    expect(calls.some((v) => v.method !== "GET")).toBe(false);
    expect(errors).toEqual([]);
  });
}

test("determinación desasociada explica revisión y conserva acceso a consulta", async ({
  page,
}) => {
  determinations[aid] = {
    ...applicability(aid),
    revision: 1,
    current: false,
    eipd: { state: "corresponde", reason: "[FICTICIA] Alcance anterior" },
  };
  await page.evaluate((hash) => {
    window.location.hash = hash;
  }, `#/licitud/eipd?organizationId=${org}&treatmentId=${tid}&assessmentId=${aid}`);
  await expect(relocation(page)).toContainText("requiere revisión");
  await expect(availability(page)).toContainText("requiere revisión");
  await expect(
    availability(page).getByRole("button", { name: "Completar EIPD", exact: true })
  ).not.toBeVisible();
  await expect(
    availability(page).getByRole("button", { name: "Ir a Revisar y decidir", exact: true })
  ).toBeVisible();
  expect(calls.some((v) => v.method !== "GET")).toBe(false);
  expect(errors).toEqual([]);
});

test("enlace sin determinación explica ausencia de guardado y permite cerrar el aviso", async ({
  page,
}) => {
  await page.evaluate((hash) => {
    window.location.hash = hash;
  }, `#/licitud/eipd?organizationId=${org}&treatmentId=${tid}&assessmentId=${aid}`);
  await expect(relocation(page)).toContainText("todavía no hay una determinación guardada");
  await expect(relocation(page)).not.toContainText("requiere revisión");
  await expect(availability(page)).toContainText("Sin determinación guardada");
  await relocation(page).getByRole("button", { name: "Cerrar aviso", exact: true }).click();
  await expect(relocation(page)).not.toBeVisible();
  await expect(availability(page)).toBeVisible();
  expect(calls.some((v) => v.method !== "GET")).toBe(false);
  expect(errors).toEqual([]);
});
