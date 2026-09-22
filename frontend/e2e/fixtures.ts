import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { parseEnv } from "node:util";
import { test as base, expect, type Page } from "@playwright/test";

const organizationId = "11000000-0000-0000-0000-000000000001";
const apiURL = "http://localhost:8000";

type RatSession = {
  page: Page;
  organizationId: string;
  request: (path: string, method?: string, body?: unknown) => Promise<Response>;
  trackTreatment: (id: string) => void;
};

export const test = base.extend<{ rat: RatSession }>({
  rat: async ({ page }, use) => {
    // No se exportan secretos a process.env ni a procesos del frontend.
    let credentials: Record<string, string | undefined>;
    try {
      credentials = parseEnv(readFileSync(resolve(__dirname, "../../.env"), "utf8"));
    } catch {
      throw new Error("E2E requiere .env en la raíz del repositorio.");
    }
    const email = credentials.E2E_USER_EMAIL;
    const password = credentials.E2E_USER_PASSWORD;
    credentials = {};
    if (!email || !password) {
      throw new Error("Configura E2E_USER_EMAIL y E2E_USER_PASSWORD en .env y ejecuta seed_e2e.");
    }

    let token: string;
    let phase = "abrir login";
    page.setDefaultTimeout(15_000);
    try {
      await page.goto("/login");
      phase = "completar credenciales";
      await page.getByLabel("Correo electrónico").fill(email);
      await page.getByLabel("Contraseña", { exact: true }).fill(password);
      phase = "autenticar en Supabase";
      const [response] = await Promise.all([
        page.waitForResponse((response) => new URL(response.url()).pathname === "/auth/v1/token", {
          timeout: 20_000,
        }),
        page.locator("form").getByRole("button", { name: "Iniciar sesión" }).click(),
      ]);
      if (!response.ok()) throw new Error("login failed");
      const session = await response.json();
      if (typeof session.access_token !== "string") throw new Error("missing session");
      token = session.access_token;
      phase = "abrir dashboard";
      await expect(page).toHaveURL(/\/dashboard$/);
    } catch {
      // Los errores de fill pueden incluir su argumento: nunca propagar el error original.
      throw new Error(
        `Falló el login E2E (${phase}). Revisa servicios, configuración y fixture local.`
      );
    }

    const request: RatSession["request"] = async (path, method = "GET", body) => {
      if (!path.startsWith("/rat/") && path !== "/me/organizations") {
        throw new Error("Ruta fuera del alcance del fixture RAT.");
      }
      try {
        // fetch nativo evita adjuntar headers/cuerpos autenticados al reporte de Playwright.
        return await fetch(`${apiURL}${path}`, {
          method,
          redirect: "error",
          signal: AbortSignal.timeout(15_000),
          headers: {
            Authorization: `Bearer ${token}`,
            "X-Organization-Id": organizationId,
            "Content-Type": "application/json",
          },
          body: body === undefined ? undefined : JSON.stringify(body),
        });
      } catch {
        throw new Error("No se pudo consultar la API local del RAT.");
      }
    };

    const memberships = await request("/me/organizations");
    expect(memberships.status, "La API debe aceptar la sesión real").toBe(200);
    const organizations = await memberships.json();
    expect(
      organizations.some(
        (org: { id: string; role: string }) => org.id === organizationId && org.role === "owner"
      ),
      "Ejecuta seed_e2e: se requiere owner en la organización E2E"
    ).toBe(true);
    const inventory = await request("/rat/treatments");
    expect(inventory.status, "Fixture con acceso RAT y suscripción vigente").toBe(200);

    const created = new Set<string>();
    try {
      await use({
        page,
        organizationId,
        request,
        trackTreatment: (id) => {
          if (!/^[0-9a-f-]{36}$/i.test(id)) throw new Error("ID de tratamiento inválido.");
          created.add(id);
        },
      });
    } finally {
      for (const id of created) {
        const result = await request(`/rat/treatments/${id}`, "DELETE");
        expect(result.status, "Limpieza del tratamiento creado por esta prueba").toBe(204);
        const missing = await request(`/rat/treatments/${id}`);
        expect(missing.status, "La limpieza debe persistir").toBe(404);
      }
    }
  },
});

export { expect };
