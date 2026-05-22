import { expect, test } from "@playwright/test";

test.use({
  viewport: { width: 1280, height: 720 },
  colorScheme: "light",
  reducedMotion: "reduce",
  locale: "en-US",
  timezoneId: "UTC",
});

const viewportCases = [
  { name: "desktop", size: { width: 1280, height: 720 } },
  { name: "mobile-portrait", size: { width: 390, height: 844 } },
  // Keep this case when the approved contract calls for a landscape mobile design.
  { name: "mobile-landscape", size: { width: 844, height: 390 } },
];

test("chart matches the approved responsive baselines", async ({ page }) => {
  // Mock at the network boundary so chart transforms and render logic stay real.
  await page.route("**/api/chart-data*", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        series: [
          { date: "2024-01-01", value: 12 },
          { date: "2024-01-02", value: 18 },
          { date: "2024-01-03", value: 15 },
        ],
      }),
    });
  });

  for (const viewportCase of viewportCases) {
    await page.setViewportSize(viewportCase.size);

    await page.goto("http://127.0.0.1:3000/chart-demo", {
      waitUntil: "networkidle",
    });

    const chart = page.locator("[data-testid='chart-root']");

    await expect(chart).toBeVisible();
    await page.waitForFunction(() => document.fonts?.status !== "loading");

    await expect(chart).toHaveScreenshot(
      `chart-demo-${viewportCase.name}.png`,
      {
        animations: "disabled",
        caret: "hide",
        scale: "css",
      },
    );
  }
});
