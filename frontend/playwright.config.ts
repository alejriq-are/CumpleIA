import { defineConfig, devices } from "@playwright/test";

// Servicios locales iniciados según docs/project/frontend-e2e.md.
export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  workers: 1,
  retries: 0,
  forbidOnly: Boolean(process.env.CI),
  timeout: 120_000,
  expect: { timeout: 15_000 },
  reporter: "list",
  outputDir: "test-results",
  preserveOutput: "never",
  use: {
    baseURL: "http://localhost:3000",
    trace: "off",
    screenshot: "off",
    video: "off",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
