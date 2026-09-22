import { randomUUID } from "node:crypto";
import { test, expect } from "./fixtures";

test("RAT exige iniciar sesión", async ({ page }) => {
  await page.goto("/dashboard/rat");
  await expect(page).toHaveURL(/\/login(?:\?|$)/);
  await expect(page.getByLabel("Correo electrónico")).toBeVisible();
});

test("RAT autenticado: preparación, activación, archivo y reactivación", async ({ rat }) => {
  const { page, organizationId, request, trackTreatment } = rat;
  const name = `E2E RAT ${randomUUID()}`;
  const section = (heading: string) =>
    page
      .locator("section")
      .filter({ has: page.getByRole("heading", { name: heading, exact: true }) });
  const review = section("Revisión y activación");
  const progress = page.getByRole("progressbar", { name: "Avance de preparación del registro" });

  await page.goto("/dashboard/rat");
  await expect(page.getByRole("heading", { name: "Inventario de tratamientos" })).toBeVisible();
  const organization = page.getByRole("combobox", { name: "Organización:" });
  if (await organization.count()) await organization.selectOption(organizationId);
  await expect(page.getByRole("link", { name: "Nueva actividad", exact: true })).toHaveAttribute(
    "href",
    `/dashboard/rat/nuevo?organizationId=${organizationId}`
  );
  await page.getByRole("link", { name: "Nueva actividad", exact: true }).click();
  await page.getByLabel("Nombre de la actividad *", { exact: true }).fill(name);
  await page.getByRole("combobox", { name: /Rol de la organización/ }).selectOption("responsable");
  await page
    .getByLabel("Regla de conservación", { exact: true })
    .fill("Eliminar al cerrar la prueba E2E.");
  const creation = page.waitForResponse(
    (response) =>
      new URL(response.url()).pathname === "/rat/treatments" &&
      response.request().method() === "POST"
  );
  await page.getByRole("button", { name: "Crear actividad", exact: true }).click();
  const created = await creation;
  expect(created.status()).toBe(201);
  const treatment = await created.json();
  trackTreatment(treatment.id);
  const detailURL = `/dashboard/rat/${treatment.id}?organizationId=${organizationId}`;
  await expect(page).toHaveURL(new RegExp(`/dashboard/rat/${treatment.id}\\?`));
  await expect(progress).toHaveAttribute("aria-valuenow", "3");
  await expect(
    review.getByRole("button", { name: "Activar actividad", exact: true })
  ).toBeDisabled();
  // El servidor también debe rechazar la activación incompleta.
  const rejected = await request(`/rat/treatments/${treatment.id}`, "PATCH", { status: "activo" });
  expect(rejected.status).toBe(400);

  await page.getByRole("button", { name: "+ Agregar finalidad", exact: true }).click();
  await page
    .getByPlaceholder("Ej. Gestionar la relación comercial con clientes")
    .fill("Gestionar clientes de prueba");
  await page.getByRole("button", { name: "Guardar finalidades", exact: true }).click();
  await expect(page.getByText("Finalidades guardadas.", { exact: true })).toBeVisible();
  await section("Categorías de datos personales")
    .getByRole("checkbox", { name: /Datos de identificación/ })
    .check();
  await page.getByRole("button", { name: "Guardar categorías", exact: true }).click();
  await expect(page.getByText("Categorías de datos guardadas.", { exact: true })).toBeVisible();
  await section("Titulares de los datos")
    .getByRole("checkbox", { name: /Clientes/ })
    .check();
  await page.getByRole("button", { name: "Guardar titulares", exact: true }).click();
  await expect(page.getByText("Titulares guardados.", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "+ Agregar fuente", exact: true }).click();
  await section("Fuentes de los datos").getByRole("combobox").selectOption("titular");
  await page
    .getByPlaceholder("Ej. Formulario de registro del cliente")
    .fill("Formulario sintético E2E");
  await page.getByRole("button", { name: "Guardar fuentes", exact: true }).click();
  await expect(page.getByText("Fuentes de datos guardadas.", { exact: true })).toBeVisible();

  await page.getByRole("radio", { name: "No usa sistemas", exact: true }).check();
  await page.getByRole("button", { name: "Guardar sistemas", exact: true }).click();
  await expect(page.getByText("Información de sistemas guardada.", { exact: true })).toBeVisible();
  await page.getByRole("radio", { name: "No intervienen", exact: true }).check();
  await page.getByRole("button", { name: "Guardar proveedores", exact: true }).click();
  await expect(
    page.getByText("Información de proveedores guardada.", { exact: true })
  ).toBeVisible();
  await page.getByRole("radio", { name: "No existen", exact: true }).check();
  await page.getByRole("button", { name: "Guardar transferencias", exact: true }).click();
  await expect(
    page.getByText("Información de transferencias internacionales guardada.", { exact: true })
  ).toBeVisible();
  await expect(progress).toHaveAttribute("aria-valuenow", "10");
  await page.reload();
  await expect(progress).toHaveAttribute("aria-valuenow", "10");

  await review.getByRole("button", { name: "Activar actividad", exact: true }).click();
  await expect(review.getByText("Esta actividad está activa.", { exact: true })).toBeVisible();
  await page.reload();
  await expect(review.getByText("Esta actividad está activa.", { exact: true })).toBeVisible();

  // Un cambio que deja requisitos pendientes debe invalidar el estado activo.
  await section("Sistemas utilizados")
    .getByRole("radio", { name: "Pendiente de revisión", exact: true })
    .check();
  await page.getByRole("button", { name: "Guardar sistemas", exact: true }).click();
  await expect(page.getByText("Información de sistemas guardada.", { exact: true })).toBeVisible();
  await page.reload();
  await expect(progress).toHaveAttribute("aria-valuenow", "9");
  await expect(
    review.getByRole("button", { name: "Activar actividad", exact: true })
  ).toBeDisabled();
  await page.getByRole("radio", { name: "No usa sistemas", exact: true }).check();
  await page.getByRole("button", { name: "Guardar sistemas", exact: true }).click();
  await expect(progress).toHaveAttribute("aria-valuenow", "10");
  await review.getByRole("button", { name: "Activar actividad", exact: true }).click();
  await expect(review.getByText("Esta actividad está activa.", { exact: true })).toBeVisible();
  await review.getByRole("button", { name: "Volver a preparación", exact: true }).click();
  await expect(
    review.getByText("El registro está preparado para activarse.", { exact: true })
  ).toBeVisible();
  await review.getByRole("button", { name: "Activar actividad", exact: true }).click();
  await expect(review.getByText("Esta actividad está activa.", { exact: true })).toBeVisible();

  page.once("dialog", (dialog) => dialog.accept());
  await review.getByRole("button", { name: "Archivar actividad", exact: true }).click();
  await expect(review.getByText("Esta actividad está archivada.", { exact: true })).toBeVisible();
  await page.reload();
  await expect(review.getByText("Esta actividad está archivada.", { exact: true })).toBeVisible();
  await review.getByRole("button", { name: "Reactivar actividad", exact: true }).click();
  await expect(review.getByText("Esta actividad está activa.", { exact: true })).toBeVisible();

  await page.goto("/dashboard/rat");
  if (await organization.count()) await organization.selectOption(organizationId);
  const row = page.getByRole("row").filter({ has: page.getByRole("link", { name, exact: true }) });
  await expect(row.getByText("Activo", { exact: true })).toBeVisible();
  await row.getByRole("link", { name, exact: true }).click();
  await expect(page).toHaveURL(`http://localhost:3000${detailURL}`);
  await expect(review.getByText("Esta actividad está activa.", { exact: true })).toBeVisible();
});
