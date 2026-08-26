import { defineConfig } from "@playwright/test";

const testPort = Number(process.env.MOBILE_RUNTIME_TEST_PORT ?? 4174);

export default defineConfig({
  testDir: "./tests",
  testMatch: "**/*.spec.ts",
  timeout: 20_000,
  use: {
    baseURL: `http://127.0.0.1:${testPort}`,
    viewport: { width: 1100, height: 1100 },
  },
  webServer: {
    command: `npm run dev -- --port ${testPort}`,
    url: `http://127.0.0.1:${testPort}/tests/runtime-fixture.html`,
    reuseExistingServer: process.env.MOBILE_RUNTIME_TEST_PORT == null,
  },
});
