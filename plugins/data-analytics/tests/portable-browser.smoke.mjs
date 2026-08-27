import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import {
  mkdtempSync,
  readFileSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { pathToFileURL, fileURLToPath } from "node:url";

import { chromium } from "playwright-core";

import { buildPortableArtifact } from "../skills/build-report/scripts/build_portable_artifact.mjs";
import { extractPortableChartSvgs } from "../skills/build-report/scripts/extract_portable_chart_svgs.mjs";
import {
  resolveChromiumExecutable,
  waitForPortableReader,
} from "../skills/build-report/scripts/portable_browser_helpers.mjs";
import { verifyPortableArtifact } from "../skills/build-report/scripts/verify_portable_artifact.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const pluginRoot = resolve(here, "..");
const builderPath = resolve(
  pluginRoot,
  "skills/build-report/scripts/build_portable_artifact.mjs",
);
const ROOT = "#data-analytics-portable-reader-root";

export const browserExecutable = resolveChromiumExecutable;

function source() {
  return {
    id: "revenue_sql",
    label: "Revenue warehouse query",
    path: "queries/revenue.sql",
    query: {
      engine: "trino",
      sql: "SELECT region, week, series, account, revenue, growth, customers FROM analytics.revenue_reader_qa",
      description: "Representative reviewed revenue rows for portable reader QA.",
      executed_at: "2026-07-07T19:58:00Z",
      tables_used: ["analytics.revenue_reader_qa"],
    },
  };
}

export function dashboardFixture() {
  const regions = [
    { name: "North", revenue: 2_450_000, growth: 0.142, customers: 128, start: 220_000 },
    { name: "South", revenue: 1_980_000, growth: 0.087, customers: 104, start: 195_000 },
  ];
  const trendValues = {
    North: [[510_000, 480_000], [590_000, 520_000], [640_000, 570_000], [710_000, 620_000]],
    South: [[430_000, 420_000], [470_000, 455_000], [505_000, 490_000], [575_000, 540_000]],
  };
  const weeks = ["2026-06-08", "2026-06-15", "2026-06-22", "2026-06-29"];
  return {
    surface: "dashboard",
    manifest: {
      version: 1,
      surface: "dashboard",
      title: "Portable Reader QA Dashboard",
      description: "A representative dashboard used to verify portable-reader interactions.",
      generatedAt: "2026-07-07T20:00:00Z",
      filters: [{
        id: "region",
        label: "Region",
        dataset: "overview",
        field: "region",
        defaultValue: "North",
        includeAll: true,
        targets: [
          { dataset: "trend", field: "region" },
          { dataset: "detail", field: "region" },
        ],
      }],
      cards: [
        {
          id: "revenue",
          description: "Revenue and year-over-year growth for the selected region.",
          dataset: "overview",
          sourceId: "revenue_sql",
          metrics: [
            { label: "Revenue", field: "revenue", format: "currency" },
            { label: "Growth", field: "growth", format: "percent", signed: true },
          ],
        },
        {
          id: "customers",
          description: "Active customers for the selected region.",
          dataset: "overview",
          sourceId: "revenue_sql",
          metrics: [{ label: "Customers", field: "customers", format: "number" }],
        },
      ],
      charts: [{
        id: "revenue_trend",
        title: "Revenue trend versus plan",
        subtitle: "Actual revenue is tracking above plan in the selected region.",
        headerMarkdown: "Hover for exact values and use the legend to compare **Actual** with **Plan**.",
        type: "line",
        dataset: "trend",
        sourceId: "revenue_sql",
        encodings: {
          x: { field: "week", type: "temporal", label: "Week" },
          y: { field: "revenue", type: "quantitative", label: "Revenue", format: "currency" },
          color: { field: "series", type: "nominal", label: "Series" },
        },
        yAxisTitle: "Revenue",
        valueFormat: "currency",
      }],
      tables: [{
        id: "account_detail",
        title: "Account detail",
        subtitle: "Sortable account-level rows supporting the dashboard.",
        dataset: "detail",
        sourceId: "revenue_sql",
        defaultSort: { field: "revenue", direction: "desc" },
        density: "dense",
        layout: "full",
        columns: [
          { field: "account", label: "Account", type: "text" },
          { field: "region", label: "Region", type: "text" },
          { field: "revenue", label: "Revenue", format: "currency" },
          { field: "growth", label: "Growth", format: "percent", movement: true },
        ],
      }],
      sources: [{ id: "revenue_sql", label: "Revenue warehouse query", path: "queries/revenue.sql" }],
      blocks: [
        { id: "metrics", type: "metric-strip", cardIds: ["revenue", "customers"] },
        { id: "trend", type: "chart", chartId: "revenue_trend" },
        { id: "detail", type: "table", tableId: "account_detail", layout: "full" },
        { id: "note", type: "markdown", body: "## What to watch\n\nGrowth remains positive, but the mix is shifting toward larger accounts." },
        { id: "custom", type: "html", body: "<section><strong>Portable custom block</strong><p>This content stays sandboxed.</p></section>" },
      ],
    },
    snapshot: {
      version: 1,
      generatedAt: "2026-07-07T20:00:00Z",
      status: "ready",
      datasets: {
        overview: regions.map((region) => ({
          region: region.name,
          revenue: region.revenue,
          growth: region.growth,
          customers: region.customers,
        })),
        trend: regions.flatMap((region) => weeks.flatMap((week, index) => [
          { region: region.name, week, series: "Actual", revenue: trendValues[region.name][index][0] },
          { region: region.name, week, series: "Plan", revenue: trendValues[region.name][index][1] },
        ])),
        detail: regions.flatMap((region) => Array.from({ length: 16 }, (_, index) => ({
          account: `${region.name} ${String(index + 1).padStart(2, "0")}`,
          region: region.name,
          revenue: region.start - index * 10_000,
          growth: Number((region.growth + 0.068 - index * 0.01).toFixed(3)),
        }))),
      },
    },
    sources: [source()],
    package_info: { root: "qa", manifestPath: "dashboard.json", snapshotPath: "dashboard.json" },
  };
}

export function reportFixture() {
  return {
    surface: "report",
    manifest: {
      version: 1,
      surface: "report",
      title: "Portable Reader QA Report",
      description: "A representative executive report for parity and conversion verification.",
      generatedAt: "2026-07-07T20:00:00Z",
      cards: [
        {
          id: "revenue",
          description: "Current quarter revenue and growth.",
          dataset: "summary",
          sourceId: "revenue_sql",
          metrics: [
            { label: "Revenue", field: "revenue", format: "currency" },
            { label: "Growth", field: "growth", format: "percent", signed: true },
          ],
        },
        {
          id: "margin",
          description: "Current gross margin.",
          dataset: "summary",
          sourceId: "revenue_sql",
          metrics: [{ label: "Gross margin", field: "margin", format: "percent" }],
        },
        {
          id: "retention",
          description: "Retention for strategic enterprise accounts.",
          dataset: "summary",
          source: {
            id: "retention_snapshot",
            label: "Retention snapshot",
            query: {
              engine: "snapshot",
              description: "Reviewed strategic account retention evidence.",
              sql: "SELECT retention FROM analytics.retention_snapshot",
              tables_used: ["analytics.retention_snapshot"],
            },
          },
          metrics: [{
            label: "Net revenue retention across strategic enterprise accounts",
            field: "retention",
            format: "percent",
          }],
        },
      ],
      charts: [{
        id: "quarterly_revenue",
        title: "Revenue is accelerating",
        subtitle: "Actual revenue has remained above plan for three quarters.",
        type: "bar",
        dataset: "quarterly",
        sourceId: "revenue_sql",
        encodings: {
          x: { field: "quarter", type: "ordinal", label: "Quarter" },
          y: { field: "revenue", type: "quantitative", label: "Revenue", format: "currency" },
          color: { field: "series", type: "nominal", label: "Series" },
        },
        yAxisTitle: "Revenue",
        valueFormat: "currency",
        layout: "full",
      }],
      tables: [{
        id: "segment_detail",
        title: "Segment performance",
        dataset: "segments",
        sourceId: "revenue_sql",
        defaultSort: { field: "revenue", direction: "desc" },
        columns: [
          { field: "segment", label: "Segment", type: "text" },
          { field: "revenue", label: "Revenue", format: "currency" },
          { field: "growth", label: "Growth", format: "percent", movement: true },
        ],
      }],
      sources: [{ id: "revenue_sql", label: "Revenue warehouse query", path: "queries/revenue.sql" }],
      blocks: [
        { id: "title", type: "markdown", body: "# Portable Reader QA Report" },
        { id: "headline", type: "markdown", body: "## Revenue is ahead of plan\n\nGrowth accelerated while gross margin remained healthy." },
        { id: "metrics", type: "metric-strip", cardIds: ["revenue", "margin", "retention"] },
        { id: "chart", type: "chart", chartId: "quarterly_revenue", layout: "full" },
        { id: "detail", type: "table", tableId: "segment_detail", layout: "full" },
        {
          id: "recommendation",
          type: "markdown",
          sourceId: "revenue_sql",
          body: "## Recommendation\n\nPrioritize enterprise expansion: revenue reached **$7.42M**, up 18.4%, while monitoring margin as the mix shifts.",
        },
      ],
    },
    snapshot: {
      version: 1,
      generatedAt: "2026-07-07T20:00:00Z",
      status: "ready",
      datasets: {
        summary: [{ revenue: 7_420_000, growth: 0.184, margin: 0.713, retention: 1.126 }],
        quarterly: [
          { quarter: "Q1", series: "Actual", revenue: 5_800_000 },
          { quarter: "Q1", series: "Plan", revenue: 5_600_000 },
          { quarter: "Q2", series: "Actual", revenue: 6_400_000 },
          { quarter: "Q2", series: "Plan", revenue: 6_100_000 },
          { quarter: "Q3", series: "Actual", revenue: 7_420_000 },
          { quarter: "Q3", series: "Plan", revenue: 6_800_000 },
        ],
        segments: [
          { segment: "Enterprise", revenue: 4_100_000, growth: 0.22 },
          { segment: "Mid-market", revenue: 2_180_000, growth: 0.16 },
          { segment: "Self-serve", revenue: 1_140_000, growth: 0.08 },
        ],
      },
    },
    sources: [source()],
    package_info: { root: "qa", manifestPath: "report.json", snapshotPath: "report.json" },
  };
}

export function blockedFixture() {
  const fixture = reportFixture();
  fixture.manifest.title = "Portable Reader Blocked Snapshot";
  fixture.manifest.blocks[0].body = "# Portable Reader Blocked Snapshot";
  fixture.snapshot.status = "blocked";
  fixture.snapshot.datasets = {};
  fixture.snapshot.accessIssues = [{
    id: "warehouse_blocked",
    dataset: "quarterly",
    message: "Warehouse access is required to populate this report.",
  }];
  return fixture;
}

function buildArtifact(directory, name, fixture) {
  const input = join(directory, `${name}.json`);
  const output = join(directory, `${name}.html`);
  writeFileSync(input, JSON.stringify(fixture), "utf8");
  execFileSync(process.execPath, [builderPath, "--input", input, "--output", output], {
    encoding: "utf8",
  });
  return output;
}

async function waitReady(page, budgetMs) {
  await waitForPortableReader(page, budgetMs);
  const readyMs = await page.evaluate(() => performance.now());
  assert.ok(readyMs <= budgetMs, `reader ready in ${readyMs.toFixed(1)}ms, budget ${budgetMs}ms`);
  return readyMs;
}

async function clickCenter(page, locator) {
  await locator.scrollIntoViewIfNeeded();
  const box = await locator.boundingBox();
  assert.ok(box, "expected a visible pointer target");
  await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
}

async function openCardMenu(page, kind, id) {
  const button = page.locator(
    `${ROOT} button[data-artifact-action="open-options"]` +
      `[data-artifact-kind=${JSON.stringify(kind)}]` +
      `[data-artifact-id=${JSON.stringify(id)}]`,
  );
  assert.equal(await button.count(), 1, `expected stable ${kind} menu button ${id}`);
  const card = button.locator("..").locator("..");
  await card.scrollIntoViewIfNeeded();
  await card.evaluate((node) => {
    const top = window.scrollY + node.getBoundingClientRect().top - 72;
    window.scrollTo(0, Math.max(0, top));
  });
  await card.hover();
  await page.waitForTimeout(20);
  await button.focus();
  await button.press("ArrowDown");
  await page.locator("[role=menu]").waitFor();
}

async function dashboardChecks(browser, file, outputDirectory) {
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1000 },
    colorScheme: "light",
    reducedMotion: "reduce",
  });
  const page = await context.newPage();
  const requests = [];
  page.on("request", (request) => requests.push(request.url()));
  await page.goto(pathToFileURL(file).href, { waitUntil: "load" });
  const readyMs = await waitReady(page, 1_500);
  const root = page.locator(ROOT);

  assert.equal(await page.locator("[data-portable-fallback]").evaluate((node) => getComputedStyle(node).display), "none");
  assert.deepEqual(await page.evaluate(() => Object.keys(localStorage)), []);
  assert.ok(requests.every((url) => url.startsWith("file:") || url.startsWith("about:")), requests.join("\n"));

  const chartBox = await root.locator(".chart-frame").first().boundingBox();
  const tableBox = await root.locator(".table-card").first().boundingBox();
  assert.ok(chartBox && tableBox && chartBox.y + chartBox.height <= tableBox.y, "chart and table must not overlap");

  const filterButton = root.locator("button").filter({ hasText: "Region" }).first();
  await clickCenter(page, filterButton);
  const filterInteractionMs = await page.evaluate(async () => {
    const item = [...document.querySelectorAll("[role=menuitemradio]")]
      .find((node) => node.textContent?.trim() === "South");
    if (!(item instanceof HTMLElement)) throw new Error("South filter option missing");
    const start = performance.now();
    item.click();
    while (!document.querySelector("#data-analytics-portable-reader-root")?.textContent?.includes("$1.98M")) {
      await new Promise(requestAnimationFrame);
    }
    return performance.now() - start;
  });
  assert.ok(filterInteractionMs <= 100, `filter responded in ${filterInteractionMs.toFixed(1)}ms`);
  assert.match(await filterButton.innerText(), /South/);
  assert.equal(await root.getByText("$1.98M", { exact: true }).count(), 1);
  assert.equal(await root.getByText("104", { exact: true }).count(), 1);

  const table = root.locator("table").first();
  assert.match(await table.locator("tbody tr").first().innerText(), /South 01/);
  const next = root.locator("button[aria-label='Next page']");
  await clickCenter(page, next);
  await page.waitForFunction((selector) => document.querySelector(selector)?.textContent?.includes("South 16"), `${ROOT} table tbody tr`);
  await clickCenter(page, root.locator("button[aria-label='Previous page']"));
  await page.waitForFunction((selector) => document.querySelector(selector)?.textContent?.includes("South 01"), `${ROOT} table tbody tr`);

  const accountSort = table.getByRole("button", { name: "Account", exact: true });
  await accountSort.evaluate((node) => node.click());
  await page.waitForTimeout(0);
  await accountSort.evaluate((node) => node.click());
  await page.waitForFunction((selector) => document.querySelector(selector)?.textContent?.includes("South 16"), `${ROOT} table tbody tr`);
  assert.equal(await accountSort.locator("..").getAttribute("aria-sort"), "descending");

  const resizeHandle = table.getByRole("button", { name: "Resize Account column" });
  const accountHeader = resizeHandle.locator("..");
  const widthBeforeKeyboard = (await accountHeader.boundingBox()).width;
  await resizeHandle.focus();
  await page.keyboard.press("ArrowRight");
  await page.waitForTimeout(50);
  const widthAfterKeyboard = (await accountHeader.boundingBox()).width;
  assert.ok(widthAfterKeyboard > widthBeforeKeyboard, "keyboard resize should increase the column width");
  const resizeBox = await resizeHandle.boundingBox();
  await page.mouse.move(resizeBox.x + resizeBox.width / 2, resizeBox.y + resizeBox.height / 2);
  await page.mouse.down();
  await page.mouse.move(resizeBox.x + resizeBox.width / 2 + 24, resizeBox.y + resizeBox.height / 2);
  await page.mouse.up();
  await page.waitForTimeout(50);
  assert.ok((await accountHeader.boundingBox()).width > widthAfterKeyboard, "pointer resize should increase the column width");

  const chart = root.locator(".recharts-wrapper").first();
  await chart.scrollIntoViewIfNeeded();
  const chartPlot = await chart.boundingBox();
  await page.mouse.move(chartPlot.x + chartPlot.width * 0.1, chartPlot.y + chartPlot.height * 0.45);
  await page.waitForFunction((selector) => document.querySelector(selector)?.textContent?.includes("$430K"), `${ROOT} .recharts-tooltip-wrapper`);
  const tooltipText = await page.evaluate((selector) => [...document.querySelectorAll(selector)]
    .map((node) => node.textContent ?? "")
    .find((text) => text.includes("$430K")) ?? "", `${ROOT} .recharts-tooltip-wrapper`);
  assert.match(tooltipText, /Plan\$420K/);

  const planLegend = root.getByRole("button", { name: "Plan", exact: true }).first();
  await clickCenter(page, planLegend);
  assert.equal(await planLegend.getAttribute("aria-pressed"), "false");
  assert.equal(await root.locator(".recharts-line-curve").count(), 1);

  await openCardMenu(page, "card", "revenue");
  const sourceAction = page.locator('[role="menu"] [data-artifact-action="view-source"]');
  await sourceAction.focus();
  await sourceAction.press("Enter");
  const sourceDialog = page.locator('[data-artifact-dialog="source"]');
  await sourceDialog.waitFor();
  assert.match(await sourceDialog.innerText(), /Tables used[\s\S]*analytics\.revenue_reader_qa/);
  const overviewTab = sourceDialog.getByRole("tab", { name: "Overview" });
  await overviewTab.focus();
  await page.keyboard.press("ArrowRight");
  await page.waitForTimeout(50);
  assert.equal(await page.evaluate(() => document.activeElement?.textContent?.trim()), "Data preview");
  await sourceDialog.getByRole("tab", { name: "SQL query" }).click();
  const copyQuery = sourceDialog.getByRole("button", { name: "Copy query" });
  await copyQuery.waitFor();
  assert.match(await sourceDialog.innerText(), /SELECT region,[\s\S]*analytics\.revenue_reader_qa/);
  await copyQuery.evaluate((node) => node.click());
  await page.waitForFunction(() => {
    const button = [...document.querySelectorAll("button")].find((node) => /Copy(?: query| failed)|Copied/.test(node.textContent ?? ""));
    return button?.textContent?.trim() === "Copied" || button?.textContent?.trim() === "Copy failed";
  });
  const clipboardResult = (await sourceDialog.locator(".source-query-copy").innerText()).trim();
  assert.ok(["Copied", "Copy failed"].includes(clipboardResult));
  await sourceDialog.getByRole("button", { name: "Close data source" }).click();

  await openCardMenu(page, "chart", "revenue_trend");
  await page.getByRole("menuitem", { name: "View expanded" }).click();
  const chartDialog = page.getByRole("dialog");
  assert.equal(await chartDialog.getByRole("button", { name: "Close expanded chart" }).count(), 1);
  assert.equal(await chartDialog.getByRole("button", { name: /Edit|Delete|Save/i }).count(), 0);
  await chartDialog.getByRole("button", { name: "Close expanded chart" }).click();

  await openCardMenu(page, "table", "account_detail");
  await page.getByRole("menuitem", { name: "View fullscreen" }).click();
  const tableDialog = page.getByRole("dialog");
  assert.match(await tableDialog.innerText(), /Account detail/);
  assert.equal(await tableDialog.getByRole("button", { name: /Edit|Delete|Save/i }).count(), 0);
  await tableDialog.locator("button[aria-label^='Close']").click();

  assert.equal(await root.getByRole("button", { name: /Edit|Delete|Refresh|Export|Share|Copy as image/i }).count(), 0);
  const customFrame = root.locator("iframe").first();
  const sandbox = await customFrame.getAttribute("sandbox");
  assert.doesNotMatch(sandbox ?? "", /allow-(?:scripts|forms|popups|top-navigation)/);
  assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1), true);

  const screenshot = join(outputDirectory, "portable-dashboard-light.png");
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(50);
  await page.screenshot({ path: screenshot, fullPage: true });
  await context.close();
  return { readyMs, filterInteractionMs, clipboardResult, screenshot };
}

async function reportChecks(browser, file, outputDirectory) {
  const results = [];
  for (const viewport of [
    { name: "desktop", width: 1440, height: 1000, budget: 1_500 },
    { name: "tablet", width: 820, height: 1000, budget: 2_500 },
    { name: "mobile", width: 390, height: 844, budget: 2_500 },
  ]) {
    for (const colorScheme of ["light", "dark"]) {
      const context = await browser.newContext({
        viewport: { width: viewport.width, height: viewport.height },
        colorScheme,
        reducedMotion: "reduce",
      });
      const page = await context.newPage();
      const requests = [];
      page.on("request", (request) => requests.push(request.url()));
      await page.goto(pathToFileURL(file).href, { waitUntil: "load" });
      const readyMs = await waitReady(page, viewport.budget);
      const text = await page.locator(ROOT).innerText();
      const markers = [
        "Revenue is ahead of plan",
        "$7.42M",
        "Revenue is accelerating",
        "Segment performance",
        "Recommendation",
      ];
      const offsets = markers.map((marker) => text.indexOf(marker));
      assert.ok(offsets.every((offset) => offset >= 0));
      assert.deepEqual(offsets, [...offsets].sort((left, right) => left - right));
      assert.match(text, /Net revenue retention across strategic enterprise accounts/);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1), true);
      assert.ok(requests.every((url) => url.startsWith("file:") || url.startsWith("about:")), requests.join("\n"));
      if (viewport.name === "mobile" && colorScheme === "light") {
        await openCardMenu(page, "card", "revenue");
        const sourceAction = page.locator('[role="menu"] [data-artifact-action="view-source"]');
        await sourceAction.focus();
        await sourceAction.press("Enter");
        const sourceDialog = page.locator('[data-artifact-dialog="source"]');
        await sourceDialog.waitFor();
        const dialogBox = await sourceDialog.boundingBox();
        assert.ok(dialogBox, "mobile source dialog should have visible geometry");
        assert.ok(dialogBox.x >= -1 && dialogBox.y >= -1, "mobile source dialog should start inside the viewport");
        assert.ok(
          dialogBox.x + dialogBox.width <= viewport.width + 1 &&
            dialogBox.y + dialogBox.height <= viewport.height + 1,
          "mobile source dialog should stay inside the viewport",
        );
        assert.equal(
          await sourceDialog.locator(".source-modal-body").evaluate((node) => getComputedStyle(node).overflowY),
          "auto",
        );
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1), true);
        await page.keyboard.press("Escape");
        await sourceDialog.waitFor({ state: "hidden" });
      }
      const screenshot = join(outputDirectory, `portable-report-${viewport.name}-${colorScheme}.png`);
      await page.screenshot({ path: screenshot, fullPage: true });
      results.push({ viewport: viewport.name, colorScheme, readyMs, screenshot });
      await context.close();
    }
  }
  return results;
}

async function serializedReplayChecks(browser, file, outputDirectory) {
  const desktopContext = await browser.newContext({
    viewport: { width: 1440, height: 1000 },
    colorScheme: "light",
    reducedMotion: "reduce",
  });
  const desktopPage = await desktopContext.newPage();
  await desktopPage.goto(pathToFileURL(file).href, { waitUntil: "load" });
  await waitForPortableReader(desktopPage, 1_500);

  const replayFile = join(outputDirectory, "portable-dashboard-serialized-replay.html");
  const serializedHtml = await desktopPage.content();
  assert.match(
    serializedHtml,
    /id="data-analytics-portable-artifact-payload-source"/,
    "serialized output should retain its embedded payload source",
  );
  assert.match(
    serializedHtml,
    /id="data-analytics-portable-reader-runtime-source"/,
    "serialized output should retain its embedded runtime source",
  );
  assert.doesNotMatch(
    serializedHtml,
    /<script[^>]*type="module"/i,
    "serialized output should not retain the transient runtime module",
  );
  writeFileSync(replayFile, serializedHtml, "utf8");
  await desktopContext.close();

  const mobileContext = await browser.newContext({
    viewport: { width: 390, height: 844 },
    colorScheme: "light",
    reducedMotion: "reduce",
  });
  const mobilePage = await mobileContext.newPage();
  const errors = [];
  mobilePage.on("pageerror", (error) => errors.push(`pageerror: ${error.message}`));
  mobilePage.on("console", (message) => {
    if (message.type() === "error") errors.push(`console: ${message.text()}`);
  });

  await mobilePage.goto(pathToFileURL(replayFile).href, { waitUntil: "load" });
  await waitForPortableReader(mobilePage, 2_500);
  await mobilePage.waitForTimeout(50);

  const replayState = await mobilePage.evaluate(() => {
    const fallback = document.querySelector("[data-portable-fallback]");
    const reader = document.getElementById("data-analytics-portable-reader");
    const chart = reader?.querySelector(
      '.chart-panel[data-artifact-kind="chart"][data-artifact-id="revenue_trend"]',
    );
    const frame = chart?.querySelector(".chart-frame");
    const chartBounds = chart?.getBoundingClientRect();
    const frameBounds = frame?.getBoundingClientRect();
    return {
      chartBounds: chartBounds && {
        bottom: chartBounds.bottom,
        left: chartBounds.left,
        right: chartBounds.right,
        top: chartBounds.top,
      },
      chartCards: reader?.querySelectorAll(
        '.chart-panel[data-artifact-kind="chart"][data-artifact-id="revenue_trend"]',
      ).length ?? 0,
      embeddedSources: document.querySelectorAll(
        "#data-analytics-portable-artifact-payload-source, #data-analytics-portable-reader-runtime-source",
      ).length,
      fallbackVisible: fallback instanceof HTMLElement && getComputedStyle(fallback).display !== "none",
      frameBounds: frameBounds && {
        bottom: frameBounds.bottom,
        left: frameBounds.left,
        right: frameBounds.right,
        top: frameBounds.top,
      },
      frameClientWidth: frame?.clientWidth ?? 0,
      frameScrollWidth: frame?.scrollWidth ?? 0,
      horizontalOverflow: document.documentElement.scrollWidth > window.innerWidth + 1,
      readerRoots: document.querySelectorAll("#data-analytics-portable-reader-root").length,
      readerHidden: reader?.getAttribute("aria-hidden") ?? null,
      readerInert: reader?.hasAttribute("inert") ?? false,
      readerVisible: reader instanceof HTMLElement && getComputedStyle(reader).display !== "none",
      rechartsSurfaces: chart?.querySelectorAll(".recharts-wrapper > svg.recharts-surface").length ?? 0,
      rechartsWrappers: chart?.querySelectorAll(".recharts-wrapper").length ?? 0,
      runtimeModules: document.head.querySelectorAll('script[type="module"]').length,
      viewportWidth: window.innerWidth,
    };
  });

  assert.equal(replayState.readerRoots, 1, "serialized replay should retain one live reader root");
  assert.equal(replayState.embeddedSources, 2, "serialized replay should retain both embedded boot sources");
  assert.equal(replayState.runtimeModules, 0, "serialized replay should not retain a transient runtime module");
  assert.equal(replayState.chartCards, 1, "serialized replay should retain one chart card");
  assert.equal(replayState.rechartsWrappers, 1, "serialized replay should render one Recharts chart");
  assert.equal(replayState.rechartsSurfaces, 1, "serialized replay should not duplicate the chart SVG");
  assert.equal(replayState.fallbackVisible, false, "fallback should hide only after the replayed reader is ready");
  assert.equal(replayState.readerVisible, true, "replayed live reader should be visible");
  assert.equal(replayState.readerHidden, null, "ready replay should leave the live reader in the accessibility tree");
  assert.equal(replayState.readerInert, false, "ready replay should restore live reader interaction");
  assert.ok(replayState.chartBounds && replayState.frameBounds, "replayed chart should have visible geometry");
  assert.ok(
    replayState.frameBounds.left >= replayState.chartBounds.left - 1 &&
      replayState.frameBounds.right <= replayState.chartBounds.right + 1,
    "replayed chart should fit its card horizontally",
  );
  assert.ok(
    replayState.frameBounds.left >= -1 && replayState.frameBounds.right <= replayState.viewportWidth + 1,
    "replayed chart should fit the mobile viewport",
  );
  assert.ok(
    replayState.frameScrollWidth <= replayState.frameClientWidth + 1,
    "replayed chart should not overflow its frame",
  );
  assert.equal(replayState.horizontalOverflow, false, "serialized mobile replay should not overflow horizontally");
  assert.deepEqual(errors, [], `serialized mobile replay errors:\n${errors.join("\n")}`);

  const screenshot = join(outputDirectory, "portable-dashboard-serialized-replay-mobile.png");
  await mobilePage.screenshot({ path: screenshot, fullPage: true });
  await mobileContext.close();
  return { replayFile, screenshot };
}

function assertExtractedSvgIntegrity(svg, { requireLocalReference = false } = {}) {
  assert.match(svg, /^<svg\b/);
  assert.doesNotMatch(svg, /<(?:foreignObject|image|script)\b/i);
  assert.doesNotMatch(svg, /\son[a-z]+\s*=/i);
  assert.doesNotMatch(svg, /(?:href|src)\s*=\s*["'](?!#)/i);

  const ids = [...svg.matchAll(/\sid="([^"]+)"/g)].map((match) => match[1]);
  assert.equal(new Set(ids).size, ids.length, "extracted SVG IDs must be unique");
  const paintUrls = [...svg.matchAll(/url\(([^)]+)\)/g)].map((match) => match[1].trim().replace(/^["']|["']$/g, ""));
  assert.ok(paintUrls.every((value) => value.startsWith("#")), "extracted SVG paint URLs must be local fragments");
  const references = paintUrls.map((value) => value.slice(1));
  if (requireLocalReference) assert.ok(references.length > 0, "expected a local SVG paint reference");
  for (const reference of references) {
    assert.ok(ids.includes(reference), `unresolved extracted SVG reference: ${reference}`);
  }
}

async function assertStaticVectorChart(page, colorScheme, {
  blockId = "chart",
  label = /Revenue is accelerating chart/,
} = {}) {
  const wrapper = page.locator(`[data-static-chart-block-id=${JSON.stringify(blockId)}]`);
  assert.equal(await wrapper.count(), 1);
  assert.equal(await wrapper.getAttribute("role"), "img");
  assert.match(await wrapper.getAttribute("aria-label"), label);
  assert.equal(await wrapper.locator("img").count(), 0, "static charts must not contain raster images");
  assert.equal(
    await wrapper.locator('[src^="data:image/"], [href^="data:image/"]').count(),
    0,
    "static charts must not contain image data URIs",
  );
  assert.doesNotMatch(await wrapper.innerHTML(), /data:image\//i);

  const expected = wrapper.locator(`.portable-static-chart-${colorScheme}`);
  const other = wrapper.locator(`.portable-static-chart-${colorScheme === "light" ? "dark" : "light"}`);
  assert.equal(await expected.count(), 1);
  assert.equal(await other.count(), 1);
  assert.match(await expected.getAttribute("class"), /portable-static-chart-variant/);
  assert.match(await other.getAttribute("class"), /portable-static-chart-variant/);
  assert.equal(await expected.getAttribute("aria-hidden"), "true");
  assert.equal(await other.getAttribute("aria-hidden"), "true");
  assert.equal(await expected.isVisible(), true);
  assert.equal(await other.isHidden(), true);

  const svg = expected.locator("svg.portable-static-chart-svg");
  assert.equal(await svg.count(), 1);
  assert.equal(await svg.isVisible(), true);
  assert.equal(await svg.getAttribute("aria-hidden"), "true");
  assert.equal(await svg.getAttribute("focusable"), "false");
  assert.ok(await svg.getAttribute("viewBox"), "static chart SVG must preserve a viewBox");
  const geometry = await svg.boundingBox();
  const wrapperGeometry = await wrapper.boundingBox();
  assert.ok(geometry && geometry.width > 1 && geometry.height > 1, "static chart SVG must have visible geometry");
  assert.ok(wrapperGeometry && wrapperGeometry.width > 1 && wrapperGeometry.height > 1, "static chart wrapper must have visible geometry");
  const scrollState = await wrapper.evaluate((node) => ({
    clientWidth: node.clientWidth,
    narrow: matchMedia("(max-width: 640px)").matches,
    overflowX: getComputedStyle(node).overflowX,
    scrollWidth: node.scrollWidth,
  }));
  if (scrollState.narrow) {
    assert.equal(scrollState.overflowX, "visible");
    assert.ok(scrollState.scrollWidth <= scrollState.clientWidth + 1, "narrow static charts should scale fluidly within their wrapper");
  } else {
    assert.ok(scrollState.scrollWidth <= scrollState.clientWidth + 1, "wide static charts should remain fluid within their wrapper");
  }

  const legend = expected.locator("ol, ul").first();
  assert.equal(await legend.count(), 1, "static chart should retain its native legend list");
  assert.match(await legend.innerText(), /Actual[\s\S]*Plan/);
  assert.equal(await expected.locator("button").count(), 0, "static legend must not expose inert controls");

  const integrity = await wrapper.evaluate((node) => {
    const allIds = Array.from(document.querySelectorAll("[id]"))
      .map((element) => element.id)
      .filter(Boolean);
    const duplicateDocumentIds = [...new Set(allIds.filter((id, index) => allIds.indexOf(id) !== index))];
    const variants = Array.from(node.querySelectorAll("svg.portable-static-chart-svg")).map((surface) => {
      const ids = Array.from(surface.querySelectorAll("[id]")).map((element) => element.id);
      const idSet = new Set(ids);
      const duplicateIds = [...new Set(ids.filter((id, index) => ids.indexOf(id) !== index))];
      const unresolved = [];
      const external = [];
      for (const element of [surface, ...surface.querySelectorAll("*")]) {
        for (const attribute of element.attributes) {
          const value = attribute.value;
          for (const match of value.matchAll(/url\(["']?#([^)'"\s]+)["']?\)/g)) {
            if (!idSet.has(match[1])) unresolved.push(`${attribute.name}=${value}`);
          }
          if ((attribute.name === "href" || attribute.name === "xlink:href") && !value.startsWith("#")) {
            external.push(`${attribute.name}=${value}`);
          }
          if (/url\((?!["']?#)/i.test(value)) external.push(`${attribute.name}=${value}`);
        }
      }
      return { duplicateIds, external, unresolved };
    });
    return {
      duplicateDocumentIds,
      forbiddenElements: node.querySelectorAll("script, foreignObject, image").length,
      variants,
    };
  });
  assert.deepEqual(integrity.duplicateDocumentIds, []);
  assert.equal(integrity.forbiddenElements, 0);
  for (const variant of integrity.variants) {
    assert.deepEqual(variant.duplicateIds, []);
    assert.deepEqual(variant.external, []);
    assert.deepEqual(variant.unresolved, []);
  }

  return wrapper;
}

async function assertStaticSourceTooltips(page, { mobile }) {
  const fallback = page.locator("[data-portable-fallback]");
  const valueHosts = fallback.locator(".portable-source-value[data-portable-source-host]");
  const chartHost = fallback.locator("figure.portable-chart-summary[data-portable-source-host]");
  const hosts = fallback.locator("[data-portable-source-host]");
  const runtimeReady = await page.locator('html[data-portable-source-tooltips-ready="true"]').count() === 1;
  assert.equal(await valueHosts.count(), 12, "every sourced report metric, table value, and narrative claim should expose provenance");
  assert.equal(await chartHost.count(), 1, "the chart should retain its existing figure-level source host");
  assert.equal(await hosts.count(), 13, "only sourced values and the chart figure should be source hosts");
  assert.equal(await fallback.locator("article.portable-metric-card[data-portable-source-host]").count(), 0);
  assert.equal(await fallback.locator(".portable-table-source-region[data-portable-source-host]").count(), 0);
  assert.equal(await fallback.locator(".portable-table-scroll[data-portable-source-host]").count(), 0);
  assert.equal(await fallback.locator("td:not(.portable-table-source-cell) [data-portable-source-host]").count(), 0);
  assert.equal(await fallback.locator("td.portable-table-source-cell").count(), 6, "only the six numeric table cells should be discoverable source values");
  assert.equal(await fallback.locator("td.portable-table-source-cell > .portable-source-value").count(), 6);
  const narrativeHosts = fallback.locator(
    '[data-artifact-block-id="recommendation"] .portable-markdown .portable-source-value[data-portable-source-host]',
  );
  assert.equal(await narrativeHosts.count(), 2, "source-backed markdown should expose its two quantitative claims");
  assert.deepEqual(
    await narrativeHosts.evaluateAll((nodes) => nodes.map((node) => node.firstChild?.textContent)),
    ["$7.42M", "18.4%"],
  );
  assert.equal(await chartHost.locator(":scope > .portable-inline-source > .portable-source-tooltip-content").count(), 1);
  assert.equal(await chartHost.locator(".portable-source-value").count(), 0, "chart provenance should remain unchanged");
  assert.equal(await page.locator(".portable-source-tooltip-trigger, details.portable-source-disclosure").count(), 0, "static provenance should not add a visible control");
  assert.equal(await fallback.getByRole("button", { name: /source/i }).count(), 0, "static provenance should not add a Source button");
  assert.equal(await page.locator(".portable-sources").isHidden(), true, "screen mode should keep the full source inventory quiet");

  const descriptions = await valueHosts.evaluateAll((nodes) => nodes.map((node) => ({
    cursor: getComputedStyle(node).cursor,
    id: node.getAttribute("aria-describedby"),
    decoration: getComputedStyle(node).textDecorationStyle,
    directTooltips: Array.from(node.children).filter((child) => child.matches(".portable-source-tooltip-content")).length,
    tabindex: node.getAttribute("tabindex"),
  })));
  const describedIds = descriptions.map(({ id }) => id);
  assert.equal(describedIds.every(Boolean), true);
  assert.equal(descriptions.every(({ cursor }) => cursor === "help"), true, "discoverable values should use the production help cursor");
  assert.equal(descriptions.every(({ decoration }) => decoration === "dotted"), true, "discoverable values should use dotted underlines");
  assert.equal(descriptions.every(({ directTooltips }) => directTooltips === 1), true);
  assert.equal(descriptions.every(({ tabindex }) => tabindex === "0"), true, "discoverable values should be keyboard focusable");
  assert.equal(new Set(describedIds).size, describedIds.length, "each sourced host needs a unique tooltip id");
  for (const id of describedIds) {
    const tooltip = page.locator(`#${id}`);
    assert.equal(await tooltip.count(), 1);
    assert.equal(await tooltip.getAttribute("role"), "tooltip");
    assert.equal(await tooltip.isHidden(), true, "source tooltips should not add idle visual layout");
  }

  const allDescribedIds = await hosts.evaluateAll((nodes) => nodes.map((node) => node.getAttribute("aria-describedby")));
  assert.equal(allDescribedIds.every(Boolean), true);
  assert.equal(new Set(allDescribedIds).size, allDescribedIds.length, "value and chart source descriptions must not collide");

  const metricCards = fallback.locator("article.portable-metric-card");
  const firstCard = metricCards.first();
  const firstCardBounds = await firstCard.boundingBox();
  assert.ok(firstCardBounds);
  if (!mobile) {
    await page.mouse.move(firstCardBounds.x + firstCardBounds.width - 8, firstCardBounds.y + firstCardBounds.height - 8);
    assert.equal(
      await fallback.locator(".portable-source-value > .portable-source-tooltip-content:visible").count(),
      0,
      "blank metric-card padding must not trigger provenance",
    );
    const textCell = fallback.locator('[data-table-id="segment_detail"] tbody td:not(.portable-table-source-cell)').first();
    await textCell.hover();
    assert.equal(
      await fallback.locator(".portable-source-value > .portable-source-tooltip-content:visible").count(),
      0,
      "text cells must not trigger numeric provenance tooltips",
    );
  }

  const host = valueHosts.first();
  const tooltipId = await host.getAttribute("aria-describedby");
  const tooltip = page.locator(`#${tooltipId}`);
  assert.match(await tooltip.textContent(), /Source: Revenue warehouse query[\s\S]*Table: analytics\.revenue_reader_qa/);
  assert.equal(await tooltip.locator(".portable-source-tooltip-heading").getAttribute("aria-hidden"), "true");
  assert.equal(await tooltip.locator("pre.portable-source-query-data").count(), 0, "value tooltips should not duplicate SQL");
  assert.equal(await tooltip.locator(".portable-source-description-data").count(), 0, "value tooltips should stay concise");
  assert.equal(await host.innerText(), "$7.42M");
  if (mobile && runtimeReady) {
    assert.equal(await host.getAttribute("role"), "button");
    assert.equal(await host.getAttribute("aria-expanded"), "false");
  } else {
    assert.notEqual(await host.getAttribute("role"), "button", "desktop and CSS-only values should retain inline semantics");
    assert.equal(await host.getAttribute("aria-expanded"), null);
  }

  await host.evaluate((node) => node.scrollIntoView({ block: "center" }));
  const initialHostBounds = await host.boundingBox();
  assert.ok(initialHostBounds);
  assert.ok(initialHostBounds.width < firstCardBounds.width / 2, "the hover target should be the value, not the whole card");
  if (mobile) {
    await page.touchscreen.tap(
      initialHostBounds.x + initialHostBounds.width / 2,
      initialHostBounds.y + initialHostBounds.height / 2,
    );
    assert.equal(await host.evaluate((node) => document.activeElement === node), true);
  } else {
    await host.hover();
    assert.equal(await tooltip.isVisible(), true);
    assert.equal(
      await tooltip.evaluate((node) => getComputedStyle(node).position),
      runtimeReady ? "fixed" : "absolute",
    );
    if (runtimeReady) {
      await page.waitForFunction((id) => {
        const node = document.getElementById(id);
        return node?.style.getPropertyValue("--portable-source-tooltip-left")
          && node.style.getPropertyValue("--portable-source-tooltip-top");
      }, tooltipId);
    }
    await page.mouse.move(0, 0);
    await page.evaluate(() => {
      if (document.activeElement instanceof HTMLElement) document.activeElement.blur();
    });
    assert.equal(await tooltip.isHidden(), true);
    let reachedHost = false;
    for (let attempt = 0; attempt < 20 && !reachedHost; attempt += 1) {
      await page.keyboard.press("Tab");
      reachedHost = await host.evaluate((node) => document.activeElement === node);
    }
    assert.equal(reachedHost, true, "keyboard traversal should reach the underlined value");
  }
  assert.equal(await tooltip.isVisible(), true);
  const bounds = await tooltip.boundingBox();
  const viewport = page.viewportSize();
  assert.ok(bounds && viewport);
  assert.ok(bounds.x >= -1 && bounds.x + bounds.width <= viewport.width + 1);
  assert.ok(bounds.y >= -1 && bounds.y + bounds.height <= viewport.height + 1);
  if (!mobile && runtimeReady) {
    const expectedLeft = Math.min(
      Math.max(initialHostBounds.x + (initialHostBounds.width - bounds.width) / 2, 8),
      viewport.width - bounds.width - 8,
    );
    const aboveTop = initialHostBounds.y - bounds.height - 8;
    const preferredTop = aboveTop < 8 ? initialHostBounds.y + initialHostBounds.height + 8 : aboveTop;
    const expectedTop = Math.min(Math.max(preferredTop, 8), viewport.height - bounds.height - 8);
    assert.ok(Math.abs(bounds.x - expectedLeft) <= 2, "desktop sources should be centered on and clamped around their value");
    assert.ok(Math.abs(bounds.y - expectedTop) <= 2, "desktop sources should be vertically placed from their value rect");
  } else if (!mobile) {
    assert.ok(
      Math.abs((bounds.x + bounds.width / 2) - (initialHostBounds.x + initialHostBounds.width / 2)) <= 2,
      "CSS-only sources should be centered on their value",
    );
    assert.ok(
      Math.abs((bounds.y + bounds.height) - (initialHostBounds.y - 8)) <= 2,
      "CSS-only sources should sit directly above their value",
    );
  }
  const activeHostBounds = await host.boundingBox();
  assert.ok(activeHostBounds);
  assert.ok(Math.abs(activeHostBounds.width - initialHostBounds.width) <= 1);
  assert.ok(Math.abs(activeHostBounds.height - initialHostBounds.height) <= 1, "provenance must not add card height");
  if (mobile) {
    assert.equal(await tooltip.evaluate((node) => getComputedStyle(node).position), "fixed");
    assert.equal(await tooltip.evaluate((node) => getComputedStyle(node).pointerEvents), "auto");
    assert.match(await tooltip.locator(".portable-source-tooltip-heading").textContent(), /^Source for /);
    if (runtimeReady) {
      assert.equal(await host.getAttribute("role"), "button");
      assert.equal(await host.getAttribute("aria-expanded"), "true");
      await page.touchscreen.tap(
        initialHostBounds.x + initialHostBounds.width / 2,
        initialHostBounds.y + initialHostBounds.height / 2,
      );
      assert.equal(await tooltip.isHidden(), true, "a second tap should close the production-style mobile tray");
      assert.equal(await host.getAttribute("aria-expanded"), "false");

      await host.focus();
      await page.keyboard.press("Enter");
      assert.equal(await tooltip.isVisible(), true, "Enter should open a focused value tooltip");
      assert.equal(await host.getAttribute("aria-expanded"), "true");
      await page.keyboard.press("Enter");
      assert.equal(await tooltip.isHidden(), true, "Enter should also toggle a value tooltip closed");
      await page.keyboard.press(" ");
      assert.equal(await tooltip.isVisible(), true, "Space should open a focused value tooltip");
      await page.keyboard.press("Escape");
      assert.equal(await tooltip.isHidden(), true);
      assert.equal(await host.getAttribute("aria-expanded"), "false");
      assert.equal(await host.evaluate((node) => document.activeElement === node), true, "Escape should restore focus");

      await page.keyboard.press(" ");
      assert.equal(await tooltip.isVisible(), true);
      await fallback.locator(".portable-block-stack").dispatchEvent("pointerdown", {
        bubbles: true,
        isPrimary: true,
        pointerId: 1,
        pointerType: "touch",
      });
      assert.equal(await tooltip.isHidden(), true, "a pointer-only outside tap should dismiss the mobile source tray");
      assert.equal(await host.getAttribute("aria-expanded"), "false");

      await page.keyboard.press(" ");
      assert.equal(await tooltip.isVisible(), true);
      await page.touchscreen.tap(8, 8);
      assert.equal(await tooltip.isHidden(), true, "tapping outside should dismiss the mobile source tray");
      assert.equal(await host.getAttribute("aria-expanded"), "false");

      await host.evaluate((node) => node.scrollIntoView({ block: "center" }));
      const reopenedBounds = await host.boundingBox();
      assert.ok(reopenedBounds);
      await page.touchscreen.tap(
        reopenedBounds.x + reopenedBounds.width / 2,
        reopenedBounds.y + reopenedBounds.height / 2,
      );
      assert.equal(await tooltip.isVisible(), true);
      const scrollDelta = await page.evaluate(() => {
        const start = window.scrollY;
        const maximum = Math.max(0, document.documentElement.scrollHeight - window.innerHeight);
        const target = maximum - start >= 32 ? start + 32 : Math.max(0, start - 32);
        window.scrollTo(0, target);
        return Math.abs(window.scrollY - start);
      });
      assert.ok(scrollDelta >= 24, "the dismissal check needs a real 24px scroll");
      await page.waitForFunction(
        () => !document.querySelector(".portable-source-value")?.hasAttribute("data-portable-source-tooltip-open"),
      );
      assert.equal(await tooltip.isHidden(), true, "scrolling should dismiss the mobile source tray");
    } else {
      assert.equal(await host.getAttribute("role"), null);
      assert.equal(await host.getAttribute("aria-expanded"), null);
    }

    const nextHost = valueHosts.nth(1);
    await nextHost.evaluate((node) => node.scrollIntoView({ block: "center" }));
    const nextBounds = await nextHost.boundingBox();
    assert.ok(nextBounds);
    await page.touchscreen.tap(nextBounds.x + nextBounds.width / 2, nextBounds.y + nextBounds.height / 2);
    assert.equal(await tooltip.isHidden(), true);
    const nextTooltip = page.locator(`#${await nextHost.getAttribute("aria-describedby")}`);
    assert.equal(await nextHost.evaluate((node) => document.activeElement === node), true);
    assert.equal(await nextTooltip.isVisible(), true);
    if (runtimeReady) {
      assert.equal(await nextHost.getAttribute("role"), "button");
      assert.equal(await nextHost.getAttribute("aria-expanded"), "true");
      await page.keyboard.press("Escape");
      assert.equal(await nextTooltip.isHidden(), true);
      assert.equal(await nextHost.evaluate((node) => document.activeElement === node), true);
      assert.equal(await nextHost.getAttribute("aria-expanded"), "false");
    }

    if (runtimeReady) {
      const tableCell = fallback.locator('td.portable-table-source-cell').first();
      const tableHost = tableCell.locator(':scope > .portable-source-value');
      await tableCell.evaluate((node) => node.scrollIntoView({ block: "center", inline: "center" }));
      const paddingPoint = await tableCell.evaluate((cell) => {
        const cellBounds = cell.getBoundingClientRect();
        const valueBounds = cell.querySelector(":scope > .portable-source-value")?.getBoundingClientRect();
        if (!valueBounds) return null;
        const candidates = [
          { x: cellBounds.left + 2, y: cellBounds.top + cellBounds.height / 2 },
          { x: cellBounds.right - 2, y: cellBounds.top + cellBounds.height / 2 },
          { x: cellBounds.left + cellBounds.width / 2, y: cellBounds.top + 2 },
          { x: cellBounds.left + cellBounds.width / 2, y: cellBounds.bottom - 2 },
        ];
        return candidates.find(({ x, y }) => (
          x < valueBounds.left || x > valueBounds.right || y < valueBounds.top || y > valueBounds.bottom
        )) ?? null;
      });
      assert.ok(paddingPoint, "the table cell should expose tappable padding outside its underlined value");
      await page.touchscreen.tap(paddingPoint.x, paddingPoint.y);
      const tableTooltip = page.locator(`#${await tableHost.getAttribute("aria-describedby")}`);
      assert.equal(await tableHost.evaluate((node) => document.activeElement === node), true);
      assert.equal(await tableHost.getAttribute("aria-expanded"), "true");
      assert.equal(await tableTooltip.isVisible(), true, "tapping table-cell padding should open its value tooltip");
      await page.keyboard.press("Escape");
      assert.equal(await tableTooltip.isHidden(), true);
    }
  } else {
    assert.equal(await tooltip.evaluate((node) => getComputedStyle(node).pointerEvents), "none");
    await page.keyboard.press("Tab");
    assert.equal(await tooltip.isHidden(), true);
    for (const index of [3, 4]) {
      const nextHost = valueHosts.nth(index);
      const nextTooltip = page.locator(`#${await nextHost.getAttribute("aria-describedby")}`);
      await nextHost.evaluate((node) => node.scrollIntoView({ block: "center" }));
      await nextHost.hover();
      assert.equal(await nextTooltip.isVisible(), true);
      const nextBounds = await nextTooltip.boundingBox();
      const nextViewport = page.viewportSize();
      assert.ok(nextBounds && nextViewport);
      assert.ok(nextBounds.x >= -1 && nextBounds.x + nextBounds.width <= nextViewport.width + 1);
      assert.ok(nextBounds.y >= -1 && nextBounds.y + nextBounds.height <= nextViewport.height + 1);
      await page.mouse.move(0, 0);
      assert.equal(await nextTooltip.isHidden(), true);
    }
  }

  const narrativeHost = narrativeHosts.first();
  const narrativeTooltip = page.locator(`#${await narrativeHost.getAttribute("aria-describedby")}`);
  await page.evaluate(() => {
    if (document.activeElement instanceof HTMLElement) document.activeElement.blur();
  });
  await narrativeHost.evaluate((node) => node.scrollIntoView({ block: "center" }));
  if (mobile) {
    const narrativeBounds = await narrativeHost.boundingBox();
    assert.ok(narrativeBounds);
    await page.touchscreen.tap(
      narrativeBounds.x + narrativeBounds.width / 2,
      narrativeBounds.y + narrativeBounds.height / 2,
    );
  } else {
    await narrativeHost.hover();
  }
  assert.equal(await narrativeTooltip.isVisible(), true, "a source-backed metric in narrative text should open its tooltip");
  assert.match(await narrativeTooltip.textContent(), /Source: Revenue warehouse query/);
  if (mobile && runtimeReady) {
    await page.keyboard.press("Escape");
    assert.equal(await narrativeTooltip.isHidden(), true);
  } else {
    await page.mouse.move(0, 0);
    await page.evaluate(() => {
      if (document.activeElement instanceof HTMLElement) document.activeElement.blur();
    });
  }
}

async function assertStaticVisualAlignment(page, { mobile }) {
  const measurements = await page.evaluate(() => {
    const headerMeta = document.querySelector(".portable-page-meta");
    if (headerMeta && !headerMeta.querySelector(".portable-status")) {
      const status = document.createElement("span");
      status.className = "portable-status";
      status.textContent = "blocked";
      headerMeta.prepend(status);
    }
    const rect = (selector) => {
      const bounds = document.querySelector(selector)?.getBoundingClientRect();
      return bounds ? { height: bounds.height, width: bounds.width, x: bounds.x, y: bounds.y } : null;
    };
    const style = (selector) => {
      const node = document.querySelector(selector);
      if (!node) return null;
      const computed = getComputedStyle(node);
      return {
        borderBottomWidth: computed.borderBottomWidth,
        borderTopWidth: computed.borderTopWidth,
        borderRadius: computed.borderRadius,
        backgroundColor: computed.backgroundColor,
        display: computed.display,
        fontSize: computed.fontSize,
        fontWeight: computed.fontWeight,
        gap: computed.gap,
        height: computed.height,
        minWidth: computed.minWidth,
        order: computed.order,
        paddingTop: computed.paddingTop,
        position: computed.position,
        textTransform: computed.textTransform,
        whiteSpace: computed.whiteSpace,
        width: computed.width,
      };
    };
    return {
      chartCard: style(".portable-chart-summary"),
      chartData: style(".portable-chart-data-has-vector"),
      chartVariant: style(".portable-static-chart-variant"),
      header: rect(".portable-page-header"),
      headerStyle: style(".portable-page-header"),
      headerMeta: style(".portable-page-meta"),
      headerStatus: style(".portable-page-meta .portable-status"),
      headerTime: rect(".portable-page-meta time"),
      headerTitle: rect(".portable-page-header h1"),
      headerTitleStyle: style(".portable-page-header h1"),
      label: style(".portable-metric-label"),
      metricCard: style(".portable-metric-card"),
      metricDescription: style(".portable-card-description"),
      metricGrid: style(".portable-metric-grid"),
      stack: rect(".portable-block-stack"),
      table: rect(".portable-table-scroll table"),
      tableWrap: style(".portable-table-scroll"),
      value: style(".portable-metric-value"),
      matchingTitleElementCount: Array.from(document.querySelectorAll("[data-portable-fallback] h1"))
        .filter((node) => (
          node.textContent?.trim() === document.querySelector(".portable-page-header h1")?.textContent?.trim()
        )).length,
      visibleMatchingTitleCount: Array.from(document.querySelectorAll("[data-portable-fallback] h1"))
        .filter((node) => (
          node.textContent?.trim() === document.querySelector(".portable-page-header h1")?.textContent?.trim()
          && getComputedStyle(node).display !== "none"
          && node.getBoundingClientRect().height > 0
        )).length,
    };
  });
  const viewport = page.viewportSize();
  assert.ok(
    viewport
      && measurements.header
      && measurements.headerStyle
      && measurements.headerStatus
      && measurements.headerTime
      && measurements.headerTitle
      && measurements.headerTitleStyle
      && measurements.stack
      && measurements.table,
  );
  assert.equal(measurements.matchingTitleElementCount, 1, "static HTML should contain exactly one report title");
  assert.equal(measurements.visibleMatchingTitleCount, 1, "static mode should render exactly one report title");
  if (mobile) {
    assert.ok(Math.abs(measurements.stack.width - (viewport.width - 48)) <= 1);
    assert.ok(Math.abs(measurements.header.width - measurements.stack.width) <= 1);
    assert.ok(Math.abs(measurements.header.x - 24) <= 1);
    assert.equal(measurements.headerStyle.position, "static", "mobile static mode should not retain the sticky top bar");
    assert.equal(measurements.headerStyle.borderBottomWidth, "0px");
    assert.equal(measurements.headerStyle.backgroundColor, "rgba(0, 0, 0, 0)");
    assert.equal(measurements.headerMeta.display, "flex");
    assert.equal(measurements.headerMeta.order, "-1");
    assert.equal(measurements.headerMeta.textTransform, "uppercase");
    assert.equal(measurements.headerStatus.display, "none", "the mobile eyebrow should contain only the generated date");
    assert.ok(
      measurements.headerTime.y + measurements.headerTime.height <= measurements.headerTitle.y,
      "the mobile date eyebrow should render above the main title",
    );
    assert.equal(measurements.headerTitleStyle.fontSize, "24px");
    assert.equal(measurements.headerTitleStyle.whiteSpace, "normal");
    assert.equal(measurements.chartVariant.minWidth, "0px");
  } else {
    assert.ok(Math.abs(measurements.header.width - viewport.width) <= 1);
    assert.ok(Math.abs(measurements.header.height - 48) <= 1);
    assert.equal(measurements.headerStyle.position, "sticky");
    assert.equal(measurements.headerStyle.borderBottomWidth, "1px");
    assert.notEqual(measurements.headerStatus.display, "none", "desktop should retain the status pill in its top bar");
    assert.equal(measurements.headerTitleStyle.fontSize, "14px");
    assert.equal(measurements.headerTitleStyle.whiteSpace, "nowrap");
    assert.ok(Math.abs(measurements.stack.width - Math.min(768, viewport.width - 64)) <= 1);
  }
  assert.equal(measurements.metricGrid.gap, "8px");
  assert.equal(measurements.metricCard.paddingTop, "20px");
  assert.equal(measurements.metricCard.borderRadius, "16px");
  assert.equal(measurements.label.fontSize, "14px");
  assert.equal(measurements.label.textTransform, "none");
  assert.equal(measurements.value.fontSize, "20px");
  assert.equal(measurements.value.fontWeight, "500");
  assert.equal(measurements.metricDescription.display, "none");
  assert.equal(measurements.chartCard.borderTopWidth, "0px");
  assert.equal(measurements.chartCard.paddingTop, "0px");
  assert.equal(measurements.chartData.display, "block");
  assert.equal(measurements.chartData.position, "absolute");
  assert.equal(measurements.chartData.width, "1px");
  assert.equal(measurements.chartData.height, "1px");
  assert.equal(measurements.tableWrap.borderTopWidth, "0px");
  assert.ok(measurements.table.width > 100 && measurements.table.width < measurements.stack.width, "small static tables should retain live-reader content width");
}

async function assertMobileTooltipWithinVisualViewport(context, page, { expectLayoutMobile = true } = {}) {
  const cdp = await context.newCDPSession(page);
  await cdp.send("Emulation.setPageScaleFactor", { pageScaleFactor: 2 });
  await page.waitForFunction(() => (
    window.visualViewport && window.visualViewport.width < window.innerWidth * 0.75
  ));

  const host = page.locator('td.portable-table-source-cell > .portable-source-value').first();
  await host.evaluate((node) => node.scrollIntoView({ block: "center", inline: "center" }));
  await host.evaluate((node) => node.click());
  const tooltipId = await host.getAttribute("aria-describedby");
  assert.ok(tooltipId);
  const tooltip = page.locator(`#${tooltipId}`);
  await page.waitForFunction((id) => {
    const node = document.querySelector(`[aria-describedby="${CSS.escape(id)}"]`);
    return node?.hasAttribute("data-portable-source-tooltip-mobile-positioned");
  }, tooltipId);
  await page.evaluate(() => new Promise((resolve) => {
    requestAnimationFrame(() => requestAnimationFrame(resolve));
  }));
  assert.equal(await tooltip.isVisible(), true);

  const geometry = await tooltip.evaluate((node) => {
    const viewport = window.visualViewport;
    const rect = node.getBoundingClientRect();
    const root = getComputedStyle(document.documentElement);
    const inset = (name) => Number.parseFloat(root.getPropertyValue(name)) || 0;
    return {
      display: getComputedStyle(node).display,
      layoutMobile: matchMedia("(max-width:600px)").matches,
      parentIsFallback: Boolean(node.parentElement?.hasAttribute("data-portable-fallback")),
      portaled: node.getAttribute("data-portable-source-tooltip-mobile-portaled"),
      positioned: node.getAttribute("data-portable-source-tooltip-mobile-positioned"),
      position: getComputedStyle(node).position,
      rect: { bottom: rect.bottom, left: rect.left, right: rect.right, top: rect.top },
      safe: {
        bottom: inset("--portable-safe-area-bottom"),
        left: inset("--portable-safe-area-left"),
        right: inset("--portable-safe-area-right"),
        top: inset("--portable-safe-area-top"),
      },
      viewport: viewport ? {
        bottom: viewport.offsetTop + viewport.height,
        left: viewport.offsetLeft,
        right: viewport.offsetLeft + viewport.width,
        top: viewport.offsetTop,
        width: viewport.width,
      } : null,
    };
  });
  assert.ok(geometry.viewport);
  const geometrySummary = JSON.stringify(geometry);
  assert.equal(geometry.layoutMobile, expectLayoutMobile, geometrySummary);
  assert.equal(geometry.display, "block", geometrySummary);
  assert.equal(geometry.position, "fixed", geometrySummary);
  assert.equal(geometry.parentIsFallback, true, geometrySummary);
  assert.equal(geometry.portaled, "true", geometrySummary);
  assert.equal(geometry.positioned, "true", geometrySummary);
  assert.ok(geometry.viewport.width < 390, `the zoom check must use the narrower visual viewport: ${geometrySummary}`);
  assert.ok(
    geometry.rect.left >= geometry.viewport.left + geometry.safe.left + 15,
    `the tooltip should respect the visual viewport's safe left edge: ${geometrySummary}`,
  );
  assert.ok(
    geometry.rect.right <= geometry.viewport.right - geometry.safe.right - 15,
    `the tooltip should respect the visual viewport's safe right edge: ${geometrySummary}`,
  );
  assert.ok(
    geometry.rect.top >= geometry.viewport.top + geometry.safe.top + 15,
    `the tooltip should respect the visual viewport's safe top edge: ${geometrySummary}`,
  );
  assert.ok(
    geometry.rect.bottom <= geometry.viewport.bottom - geometry.safe.bottom - 15,
    `the tooltip should respect the visual viewport's safe bottom edge: ${geometrySummary}`,
  );

  await page.keyboard.press("Escape");
  await cdp.send("Emulation.setPageScaleFactor", { pageScaleFactor: 1 });
}

async function assertMobileTableTooltipEscapesOverflow(page, { runtimeReady }) {
  const tableHost = page.locator(
    '[data-table-id="segment_detail"] tbody tr:last-child '
      + 'td.portable-table-source-cell:last-child > .portable-source-value',
  );
  const tableScroller = tableHost.locator("xpath=ancestor::div[contains(@class, 'portable-table-scroll')]");
  assert.equal(await tableHost.count(), 1, "the clipping regression needs one trailing table metric");
  assert.equal(await tableScroller.count(), 1);
  assert.equal(
    await tableHost.evaluate((node) => node.firstChild?.textContent?.trim()),
    "+8%",
    "the no-JavaScript path should target the exact underlined table value",
  );
  const tooltipId = await tableHost.getAttribute("aria-describedby");
  assert.ok(tooltipId);
  const tooltip = page.locator(`#${tooltipId}`);
  assert.equal(
    await tableHost.locator(`:scope > #${tooltipId}`).count(),
    1,
    "the closed tooltip should begin under its source-value host",
  );
  await tableHost.evaluate((node) => {
    const tableScroller = node.closest(".portable-table-scroll");
    if (tableScroller instanceof HTMLElement) {
      const table = tableScroller.querySelector("table");
      if (table instanceof HTMLElement) table.style.minWidth = "800px";
      tableScroller.style.height = "80px";
      // Mobile preview engines commonly promote overflow scrollers to their own
      // compositing layer. A transform reproduces that clipping boundary in the
      // Chromium smoke runner without changing the authored table geometry.
      tableScroller.style.transform = "translateZ(0)";
    }
    node.scrollIntoView({ block: "center", inline: "center" });
    if (tableScroller instanceof HTMLElement) tableScroller.scrollLeft = tableScroller.scrollWidth;
  });
  const initialScroller = await tableScroller.evaluate((node) => ({
    clientWidth: node.clientWidth,
    overflow: getComputedStyle(node).overflow,
    scrollLeft: node.scrollLeft,
    scrollWidth: node.scrollWidth,
  }));
  assert.equal(initialScroller.overflow, "auto");
  assert.ok(
    initialScroller.scrollWidth >= 800 && initialScroller.scrollWidth > initialScroller.clientWidth,
    `the regression needs a genuinely wide table: ${JSON.stringify(initialScroller)}`,
  );
  assert.ok(initialScroller.scrollLeft > 0, `the table must be horizontally scrolled: ${JSON.stringify(initialScroller)}`);
  if (runtimeReady) {
    await tableHost.evaluate((node) => {
      node.click();
      node.click();
    });
    await page.evaluate(() => new Promise((resolve) => {
      requestAnimationFrame(() => requestAnimationFrame(resolve));
    }));
    assert.equal(await tableHost.getAttribute("data-portable-source-tooltip-open"), null);
    assert.equal(await tableHost.getAttribute("data-portable-source-tooltip-mobile-positioned"), null);
    assert.equal(await tooltip.getAttribute("data-portable-source-tooltip-mobile-portaled"), null);
    assert.equal(await tooltip.getAttribute("data-portable-source-tooltip-mobile-positioned"), null);
    assert.equal(
      await tooltip.evaluate((node) => [
        "--portable-source-tooltip-mobile-left",
        "--portable-source-tooltip-mobile-max-height",
        "--portable-source-tooltip-mobile-top",
        "--portable-source-tooltip-mobile-width",
      ].every((property) => !node.style.getPropertyValue(property))),
      true,
      "closing before the placement frame should not leave stale mobile geometry",
    );
    assert.equal(await tableHost.locator(`:scope > #${tooltipId}`).count(), 1);
  }
  const hostBounds = await tableHost.boundingBox();
  assert.ok(hostBounds);
  await page.touchscreen.tap(
    hostBounds.x + hostBounds.width / 2,
    hostBounds.y + hostBounds.height / 2,
  );

  await page.waitForFunction((id) => {
    const node = document.getElementById(id);
    return node && getComputedStyle(node).visibility === "visible";
  }, tooltipId);
  if (runtimeReady) {
    await page.waitForFunction((id) => {
      const node = document.getElementById(id);
      return node?.hasAttribute("data-portable-source-tooltip-mobile-portaled")
        && node.hasAttribute("data-portable-source-tooltip-mobile-positioned");
    }, tooltipId);
  }
  assert.equal(await tooltip.isVisible(), true);

  const rendering = await tableHost.evaluate((host) => {
    const tooltipNode = document.getElementById(host.getAttribute("aria-describedby") ?? "");
    const tableScroller = host.closest(".portable-table-scroll");
    if (!(tooltipNode instanceof HTMLElement) || !(tableScroller instanceof HTMLElement)) return null;
    const tooltipRect = tooltipNode.getBoundingClientRect();
    const scrollerRect = tableScroller.getBoundingClientRect();
    const viewport = window.visualViewport;
    const viewportRect = {
      bottom: (viewport?.offsetTop ?? 0) + (viewport?.height ?? window.innerHeight),
      left: viewport?.offsetLeft ?? 0,
      right: (viewport?.offsetLeft ?? 0) + (viewport?.width ?? window.innerWidth),
      top: viewport?.offsetTop ?? 0,
    };
    const horizontalInset = Math.min(12, Math.max(2, tooltipRect.width / 4));
    const verticalInset = Math.min(12, Math.max(2, tooltipRect.height / 4));
    const points = [
      { name: "top-left", x: tooltipRect.left + horizontalInset, y: tooltipRect.top + verticalInset },
      { name: "top-right", x: tooltipRect.right - horizontalInset, y: tooltipRect.top + verticalInset },
      { name: "bottom-left", x: tooltipRect.left + horizontalInset, y: tooltipRect.bottom - verticalInset },
      { name: "bottom-right", x: tooltipRect.right - horizontalInset, y: tooltipRect.bottom - verticalInset },
      { name: "center", x: tooltipRect.left + tooltipRect.width / 2, y: tooltipRect.top + tooltipRect.height / 2 },
    ].map((point) => {
      const topElement = document.elementFromPoint(point.x, point.y);
      return {
        ...point,
        hitsTooltip: Boolean(topElement && (
          topElement === tooltipNode || tooltipNode.contains(topElement)
        )),
        outsideTableScroller: (
          point.x < scrollerRect.left
          || point.x > scrollerRect.right
          || point.y < scrollerRect.top
          || point.y > scrollerRect.bottom
        ),
        topElement: topElement instanceof Element
          ? `${topElement.tagName.toLowerCase()}.${topElement.className}`
          : null,
      };
    });
    return {
      clientWidth: tableScroller.clientWidth,
      overflow: getComputedStyle(tableScroller).overflow,
      portaled: tooltipNode.getAttribute("data-portable-source-tooltip-mobile-portaled"),
      positioned: tooltipNode.getAttribute("data-portable-source-tooltip-mobile-positioned"),
      points,
      scrollLeft: tableScroller.scrollLeft,
      scrollWidth: tableScroller.scrollWidth,
      scrollerRect: {
        bottom: scrollerRect.bottom,
        left: scrollerRect.left,
        right: scrollerRect.right,
        top: scrollerRect.top,
      },
      tooltipRect: {
        bottom: tooltipRect.bottom,
        left: tooltipRect.left,
        right: tooltipRect.right,
        top: tooltipRect.top,
      },
      viewportRect,
    };
  });
  assert.ok(rendering);
  const renderingSummary = JSON.stringify(rendering);
  assert.ok(rendering.scrollWidth > rendering.clientWidth, renderingSummary);
  assert.equal(
    rendering.overflow,
    runtimeReady ? "auto" : "visible",
    runtimeReady
      ? `portaling must preserve horizontal table scrolling: ${renderingSummary}`
      : `CSS-only focus must temporarily release the clipping boundary: ${renderingSummary}`,
  );
  if (runtimeReady) {
    assert.ok(rendering.scrollLeft > 0, `portaling should preserve the horizontal scroll position: ${renderingSummary}`);
    assert.equal(rendering.portaled, "true", renderingSummary);
    assert.equal(rendering.positioned, "true", renderingSummary);
    assert.equal(await tooltip.evaluate((node) => node.parentElement?.hasAttribute("data-portable-fallback")), true);
    assert.equal(await tableHost.locator(`:scope > #${tooltipId}`).count(), 0);
  } else {
    assert.equal(rendering.portaled, null, renderingSummary);
    assert.equal(rendering.positioned, null, renderingSummary);
    assert.equal(await tableHost.locator(`:scope > #${tooltipId}`).count(), 1);
  }
  assert.ok(
    rendering.tooltipRect.top < rendering.scrollerRect.top
      || rendering.tooltipRect.bottom > rendering.scrollerRect.bottom,
    `the mobile tray must extend vertically beyond the table overflow bounds: ${renderingSummary}`,
  );
  assert.ok(
    rendering.points.filter(({ outsideTableScroller }) => outsideTableScroller).length >= 2,
    `the visibility probes must exercise pixels outside the table overflow bounds: ${renderingSummary}`,
  );
  assert.equal(
    rendering.points.every(({ hitsTooltip }) => hitsTooltip),
    true,
    `the complete mobile tray must win hit testing even outside the table overflow bounds: ${renderingSummary}`,
  );
  assert.ok(rendering.tooltipRect.left >= rendering.viewportRect.left - 1, renderingSummary);
  assert.ok(rendering.tooltipRect.right <= rendering.viewportRect.right + 1, renderingSummary);
  assert.ok(rendering.tooltipRect.top >= rendering.viewportRect.top - 1, renderingSummary);
  assert.ok(rendering.tooltipRect.bottom <= rendering.viewportRect.bottom + 1, renderingSummary);

  if (runtimeReady) {
    assert.equal(await tableHost.getAttribute("aria-expanded"), "true");
    assert.equal(await tableHost.getAttribute("data-portable-source-tooltip-open"), "true");
    assert.equal(await tableHost.getAttribute("data-portable-source-tooltip-mobile-positioned"), "true");
    await tooltip.dispatchEvent("pointerdown", {
      bubbles: true,
      isPrimary: true,
      pointerId: 2,
      pointerType: "touch",
    });
    assert.equal(await tooltip.isVisible(), true, "interacting with a portaled tooltip should keep it open");
    await page.locator(".portable-block-stack").dispatchEvent("pointerdown", {
      bubbles: true,
      isPrimary: true,
      pointerId: 3,
      pointerType: "touch",
    });
    assert.equal(await tableHost.getAttribute("aria-expanded"), "false");
    assert.equal(await tableHost.getAttribute("data-portable-source-tooltip-open"), null);
    assert.equal(await tableHost.getAttribute("data-portable-source-tooltip-mobile-positioned"), null);
    assert.equal(await tooltip.getAttribute("data-portable-source-tooltip-mobile-portaled"), null);
    assert.equal(await tooltip.getAttribute("data-portable-source-tooltip-mobile-positioned"), null);
    assert.equal(
      await tooltip.evaluate((node) => [
        "--portable-source-tooltip-mobile-left",
        "--portable-source-tooltip-mobile-max-height",
        "--portable-source-tooltip-mobile-top",
        "--portable-source-tooltip-mobile-width",
      ].every((property) => !node.style.getPropertyValue(property))),
      true,
      "closing the tray should clear its viewport-placement styles",
    );
    assert.equal(
      await tableHost.locator(`:scope > #${tooltipId}`).count(),
      1,
      "closing the tray should restore the tooltip under its original host",
    );
  } else {
    await page.evaluate(() => {
      if (document.activeElement instanceof HTMLElement) document.activeElement.blur();
    });
    assert.equal(await tableHost.locator(`:scope > #${tooltipId}`).count(), 1);
  }
  assert.equal(await tooltip.isHidden(), true);
  assert.equal(
    await tableScroller.evaluate((node) => getComputedStyle(node).overflow),
    "auto",
    "closing the tooltip should restore the horizontally scrollable table",
  );
}

async function fallbackAndFailureChecks(browser, reportFile, dashboardFile, blockedFile, directory) {
  for (const colorScheme of ["light", "dark"]) {
    const noJavaScript = await browser.newContext({
      colorScheme,
      hasTouch: true,
      javaScriptEnabled: false,
      viewport: { width: 390, height: 844 },
    });
    const noJavaScriptPage = await noJavaScript.newPage();
    await noJavaScriptPage.goto(pathToFileURL(reportFile).href, { waitUntil: "load" });
    assert.equal(await noJavaScriptPage.locator("[data-portable-fallback]").isVisible(), true);
    assert.match(await noJavaScriptPage.locator("body").innerText(), /Portable Reader QA Report[\s\S]*Revenue is ahead of plan/);
    await assertStaticVectorChart(noJavaScriptPage, colorScheme);
    await assertStaticVisualAlignment(noJavaScriptPage, { mobile: true });
    await assertStaticSourceTooltips(noJavaScriptPage, { mobile: true });
    await assertMobileTableTooltipEscapesOverflow(noJavaScriptPage, { runtimeReady: false });
    assert.equal(await noJavaScriptPage.locator(".portable-chart-data table").count(), 1);
    assert.equal(await noJavaScriptPage.locator(".portable-chart-data").getAttribute("aria-hidden"), null);
    assert.match(await noJavaScriptPage.locator('[data-table-id="segment_detail"]').innerText(), /\+22%/);
    const mobileLayout = await noJavaScriptPage.evaluate(() => ({
      fits: document.documentElement.scrollWidth <= window.innerWidth + 1,
      overflowing: Array.from(document.querySelectorAll("body *"))
        .filter((element) => element.getBoundingClientRect().right > window.innerWidth + 1)
        .slice(0, 10)
        .map((element) => ({
          className: element.className,
          tagName: element.tagName,
          text: element.textContent?.trim().slice(0, 80),
        })),
    }));
    assert.equal(mobileLayout.fits, true, `${colorScheme} static fallback overflow: ${JSON.stringify(mobileLayout.overflowing)}`);
    await noJavaScript.close();
  }

  const noJavaScriptTablet = await browser.newContext({
    javaScriptEnabled: false,
    viewport: { width: 820, height: 900 },
  });
  const noJavaScriptTabletPage = await noJavaScriptTablet.newPage();
  await noJavaScriptTabletPage.goto(pathToFileURL(reportFile).href, { waitUntil: "load" });
  await assertStaticVisualAlignment(noJavaScriptTabletPage, { mobile: false });
  assert.equal(await noJavaScriptTabletPage.locator("article.portable-metric-card[data-portable-source-host]").count(), 0);
  const tabletHost = noJavaScriptTabletPage.locator(".portable-source-value").nth(3);
  await tabletHost.evaluate((node) => node.scrollIntoView({ block: "center" }));
  const tabletHostBounds = await tabletHost.boundingBox();
  assert.ok(tabletHostBounds);
  await tabletHost.hover();
  const tabletTooltip = noJavaScriptTabletPage.locator(
    `#${await tabletHost.getAttribute("aria-describedby")}`,
  );
  assert.equal(await tabletTooltip.isVisible(), true);
  assert.equal(await tabletTooltip.evaluate((node) => getComputedStyle(node).position), "absolute");
  const tabletTooltipBounds = await tabletTooltip.boundingBox();
  assert.ok(tabletTooltipBounds);
  assert.ok(
    Math.abs((tabletTooltipBounds.x + tabletTooltipBounds.width / 2)
      - (tabletHostBounds.x + tabletHostBounds.width / 2)) <= 2,
  );
  assert.ok(Math.abs((tabletTooltipBounds.y + tabletTooltipBounds.height) - (tabletHostBounds.y - 8)) <= 2);
  await noJavaScriptTabletPage.mouse.move(0, 0);
  const tabletTableCard = noJavaScriptTabletPage.locator('[data-table-id="segment_detail"]');
  await tabletTableCard.evaluate((node) => node.scrollIntoView({ block: "center" }));
  await tabletTableCard.locator(".portable-visual-header h2").evaluate((node) => {
    node.textContent = "Segment performance with a deliberately long heading that must not move its source tooltip";
  });
  assert.equal(await tabletTableCard.locator(".portable-table-source-region[data-portable-source-host]").count(), 0);
  const tabletTableHost = tabletTableCard.locator("td.portable-table-source-cell .portable-source-value").first();
  const tabletTableHostBounds = await tabletTableHost.boundingBox();
  assert.ok(tabletTableHostBounds);
  await tabletTableHost.hover();
  const tabletTableTooltip = noJavaScriptTabletPage.locator(
    `#${await tabletTableHost.getAttribute("aria-describedby")}`,
  );
  assert.equal(await tabletTableTooltip.isVisible(), true);
  assert.equal(await tabletTableTooltip.evaluate((node) => getComputedStyle(node).position), "absolute");
  const tabletTableTooltipBounds = await tabletTableTooltip.boundingBox();
  const tabletViewport = noJavaScriptTabletPage.viewportSize();
  assert.ok(tabletTableTooltipBounds && tabletViewport);
  assert.ok(
    Math.abs((tabletTableTooltipBounds.x + tabletTableTooltipBounds.width / 2)
      - (tabletTableHostBounds.x + tabletTableHostBounds.width / 2)) <= 2,
    "a no-JavaScript table tooltip should be centered on its numeric value",
  );
  assert.ok(
    Math.abs((tabletTableTooltipBounds.y + tabletTableTooltipBounds.height) - (tabletTableHostBounds.y - 8)) <= 2,
  );
  assert.ok(tabletTableTooltipBounds.x >= 0);
  assert.ok(tabletTableTooltipBounds.x + tabletTableTooltipBounds.width <= tabletViewport.width);
  await noJavaScriptTablet.close();

  const noJavaScriptScreenshot = await browser.newContext({
    colorScheme: "dark",
    javaScriptEnabled: false,
    viewport: { width: 1690, height: 467 },
  });
  const noJavaScriptScreenshotPage = await noJavaScriptScreenshot.newPage();
  await noJavaScriptScreenshotPage.goto(pathToFileURL(reportFile).href, { waitUntil: "load" });
  const screenshotTableCard = noJavaScriptScreenshotPage.locator('[data-table-id="segment_detail"]');
  await screenshotTableCard.evaluate((node) => {
    window.scrollTo(0, window.scrollY + node.getBoundingClientRect().top - 60);
  });
  assert.equal(await screenshotTableCard.locator(".portable-table-source-region[data-portable-source-host]").count(), 0);
  const screenshotTableHost = screenshotTableCard.locator("td.portable-table-source-cell .portable-source-value").first();
  const screenshotTableHostBounds = await screenshotTableHost.boundingBox();
  assert.ok(screenshotTableHostBounds);
  await screenshotTableHost.hover();
  const screenshotTableTooltip = noJavaScriptScreenshotPage.locator(
    `#${await screenshotTableHost.getAttribute("aria-describedby")}`,
  );
  const screenshotTableTooltipBounds = await screenshotTableTooltip.boundingBox();
  assert.ok(screenshotTableTooltipBounds);
  assert.ok(
    Math.abs((screenshotTableTooltipBounds.x + screenshotTableTooltipBounds.width / 2)
      - (screenshotTableHostBounds.x + screenshotTableHostBounds.width / 2)) <= 2,
  );
  assert.ok(
    Math.abs((screenshotTableTooltipBounds.y + screenshotTableTooltipBounds.height)
      - (screenshotTableHostBounds.y - 8)) <= 2,
  );
  assert.ok(screenshotTableTooltipBounds.y >= 0);
  assert.ok(screenshotTableTooltipBounds.y + screenshotTableTooltipBounds.height <= 467);
  assert.ok(screenshotTableTooltipBounds.x + screenshotTableTooltipBounds.width <= 1690);
  await noJavaScriptScreenshot.close();

  const staticDashboard = await browser.newContext({
    colorScheme: "light",
    javaScriptEnabled: false,
    viewport: { width: 1440, height: 1000 },
  });
  const staticDashboardPage = await staticDashboard.newPage();
  await staticDashboardPage.goto(pathToFileURL(dashboardFile).href, { waitUntil: "load" });
  assert.equal(await staticDashboardPage.locator(".portable-filter-bar").isVisible(), true);
  assert.match(await staticDashboardPage.locator(".portable-filter-bar").innerText(), /Region[\s\S]*North/);
  assert.equal(
    await staticDashboardPage.locator('[data-artifact-block-id="trend"]').getAttribute("data-layout"),
    "half",
  );
  assert.equal(
    await staticDashboardPage.locator('[data-artifact-block-id="detail"]').getAttribute("data-layout"),
    "full",
  );
  assert.equal(await staticDashboardPage.locator(".portable-source-tooltip-trigger, details.portable-source-disclosure").count(), 0);
  await assertStaticVectorChart(staticDashboardPage, "light", {
    blockId: "trend",
    label: /Revenue trend versus plan chart/,
  });
  assert.equal(await staticDashboardPage.locator("html[data-portable-source-tooltips-ready]").count(), 0);
  const noJavaScriptValueHosts = staticDashboardPage.locator(".portable-source-value[data-portable-source-host]");
  assert.equal(await noJavaScriptValueHosts.count(), 33);
  assert.equal(await staticDashboardPage.locator("figure.portable-chart-summary[data-portable-source-host]").count(), 1);
  const noJavaScriptHost = noJavaScriptValueHosts.first();
  await noJavaScriptHost.evaluate((node) => node.scrollIntoView({ block: "center" }));
  const noJavaScriptHostBounds = await noJavaScriptHost.boundingBox();
  assert.ok(noJavaScriptHostBounds);
  await noJavaScriptHost.hover();
  const noJavaScriptTooltip = staticDashboardPage.locator(
    `#${await noJavaScriptHost.getAttribute("aria-describedby")}`,
  );
  assert.equal(await noJavaScriptTooltip.isVisible(), true);
  assert.equal(await noJavaScriptTooltip.evaluate((node) => getComputedStyle(node).position), "absolute");
  assert.equal(await noJavaScriptTooltip.evaluate((node) => getComputedStyle(node).pointerEvents), "none");
  assert.equal(
    await noJavaScriptTooltip.evaluate((node) => node.style.getPropertyValue("--portable-source-tooltip-left")),
    "",
  );
  const noJavaScriptTooltipBounds = await noJavaScriptTooltip.boundingBox();
  assert.ok(noJavaScriptTooltipBounds);
  assert.ok(
    Math.abs((noJavaScriptTooltipBounds.x + noJavaScriptTooltipBounds.width / 2)
      - (noJavaScriptHostBounds.x + noJavaScriptHostBounds.width / 2)) <= 2,
  );
  assert.ok(
    Math.abs((noJavaScriptTooltipBounds.y + noJavaScriptTooltipBounds.height)
      - (noJavaScriptHostBounds.y - 8)) <= 2,
  );
  await staticDashboardPage.mouse.move(0, 0);
  const noJavaScriptSecondHost = noJavaScriptValueHosts.nth(1);
  await noJavaScriptSecondHost.evaluate((node) => node.scrollIntoView({ block: "center" }));
  const noJavaScriptSecondHostBounds = await noJavaScriptSecondHost.boundingBox();
  assert.ok(noJavaScriptSecondHostBounds);
  await noJavaScriptSecondHost.hover();
  const noJavaScriptSecondTooltip = staticDashboardPage.locator(
    `#${await noJavaScriptSecondHost.getAttribute("aria-describedby")}`,
  );
  const noJavaScriptSecondTooltipBounds = await noJavaScriptSecondTooltip.boundingBox();
  assert.ok(noJavaScriptSecondTooltipBounds);
  assert.ok(
    Math.abs((noJavaScriptSecondTooltipBounds.x + noJavaScriptSecondTooltipBounds.width / 2)
      - (noJavaScriptSecondHostBounds.x + noJavaScriptSecondHostBounds.width / 2)) <= 2,
  );
  await staticDashboardPage.mouse.move(0, 0);
  const noJavaScriptLongTableCard = staticDashboardPage.locator('[data-table-id="account_detail"]');
  assert.equal(await noJavaScriptLongTableCard.locator(".portable-table-source-region[data-portable-source-host]").count(), 0);
  const noJavaScriptLongTableHost = noJavaScriptLongTableCard
    .locator("td.portable-table-source-cell .portable-source-value")
    .nth(10);
  await noJavaScriptLongTableHost.evaluate((node) => node.scrollIntoView({ block: "center" }));
  const noJavaScriptLongTableBounds = await noJavaScriptLongTableHost.boundingBox();
  const noJavaScriptViewport = staticDashboardPage.viewportSize();
  assert.ok(noJavaScriptLongTableBounds && noJavaScriptViewport);
  assert.ok(noJavaScriptLongTableBounds.y >= 0 && noJavaScriptLongTableBounds.y < noJavaScriptViewport.height);
  await noJavaScriptLongTableHost.hover();
  const noJavaScriptLongTableTooltip = staticDashboardPage.locator(
    `#${await noJavaScriptLongTableHost.getAttribute("aria-describedby")}`,
  );
  assert.equal(await noJavaScriptLongTableTooltip.isVisible(), true);
  assert.equal(await noJavaScriptLongTableTooltip.evaluate((node) => getComputedStyle(node).position), "absolute");
  const noJavaScriptLongTableTooltipBounds = await noJavaScriptLongTableTooltip.boundingBox();
  assert.ok(noJavaScriptLongTableTooltipBounds);
  assert.ok(
    Math.abs((noJavaScriptLongTableTooltipBounds.x + noJavaScriptLongTableTooltipBounds.width / 2)
      - (noJavaScriptLongTableBounds.x + noJavaScriptLongTableBounds.width / 2)) <= 2,
    "long-table source placement should use the numeric value rect",
  );
  assert.ok(
    Math.abs((noJavaScriptLongTableTooltipBounds.y + noJavaScriptLongTableTooltipBounds.height)
      - (noJavaScriptLongTableBounds.y - 8)) <= 2,
  );
  await staticDashboardPage.mouse.move(0, 0);
  await staticDashboard.close();

  const staticDashboardRuntime = await browser.newContext({
    colorScheme: "light",
    viewport: { width: 1440, height: 1000 },
  });
  const staticDashboardRuntimePage = await staticDashboardRuntime.newPage();
  await staticDashboardRuntimePage.addInitScript(() => { delete globalThis.DecompressionStream; });
  await staticDashboardRuntimePage.goto(pathToFileURL(dashboardFile).href, { waitUntil: "load" });
  await staticDashboardRuntimePage.waitForFunction(
    () => document.documentElement.dataset.dataAnalyticsPortableReader === "unsupported",
  );
  assert.equal(
    await staticDashboardRuntimePage.locator('html[data-portable-source-tooltips-ready="true"]').count(),
    1,
  );
  const longTableCard = staticDashboardRuntimePage.locator('[data-table-id="account_detail"]');
  assert.equal(await longTableCard.locator(".portable-table-source-region[data-portable-source-host]").count(), 0);
  const longTableHost = longTableCard.locator("td.portable-table-source-cell .portable-source-value").nth(10);
  await longTableHost.evaluate((node) => node.scrollIntoView({ block: "center" }));
  const longTableBounds = await longTableHost.boundingBox();
  const dashboardViewport = staticDashboardRuntimePage.viewportSize();
  assert.ok(longTableBounds && dashboardViewport);
  await longTableHost.hover();
  const longTableTooltip = staticDashboardRuntimePage.locator(
    `#${await longTableHost.getAttribute("aria-describedby")}`,
  );
  assert.equal(await longTableTooltip.isVisible(), true);
  await staticDashboardRuntimePage.waitForFunction((id) => {
    const node = document.getElementById(id);
    return node?.style.getPropertyValue("--portable-source-tooltip-left")
      && node.style.getPropertyValue("--portable-source-tooltip-top");
  }, await longTableHost.getAttribute("aria-describedby"));
  assert.equal(await longTableTooltip.evaluate((node) => getComputedStyle(node).position), "fixed");
  const longTableTooltipBounds = await longTableTooltip.boundingBox();
  assert.ok(longTableTooltipBounds && longTableTooltipBounds.y >= 8);
  assert.ok(longTableTooltipBounds.x >= 8);
  assert.ok(longTableTooltipBounds.x + longTableTooltipBounds.width <= dashboardViewport.width - 8);
  assert.ok(longTableTooltipBounds.y + longTableTooltipBounds.height <= dashboardViewport.height - 8);
  const expectedLongTableLeft = Math.min(
    Math.max(longTableBounds.x + (longTableBounds.width - longTableTooltipBounds.width) / 2, 8),
    dashboardViewport.width - longTableTooltipBounds.width - 8,
  );
  assert.ok(Math.abs(longTableTooltipBounds.x - expectedLongTableLeft) <= 2);
  const longTableAbove = longTableBounds.y - longTableTooltipBounds.height - 8;
  const longTablePreferredTop = longTableAbove < 8
    ? longTableBounds.y + longTableBounds.height + 8
    : longTableAbove;
  const expectedLongTableTop = Math.min(
    Math.max(longTablePreferredTop, 8),
    dashboardViewport.height - longTableTooltipBounds.height - 8,
  );
  assert.ok(
    Math.abs(longTableTooltipBounds.y - expectedLongTableTop) <= 2,
    "a long-table tooltip should use production placement from its value rect",
  );
  await staticDashboardRuntimePage.mouse.move(0, 0);
  await staticDashboardRuntime.close();

  const missingDecompression = await browser.newContext();
  const missingPage = await missingDecompression.newPage();
  await missingPage.addInitScript(() => { delete globalThis.DecompressionStream; });
  await missingPage.goto(pathToFileURL(reportFile).href, { waitUntil: "load" });
  await missingPage.waitForFunction(() => document.documentElement.dataset.dataAnalyticsPortableReader === "unsupported");
  assert.equal(await missingPage.locator("[data-portable-fallback]").isVisible(), true);
  assert.equal(await missingPage.locator('html[data-portable-source-tooltips-ready="true"]').count(), 1);
  await assertStaticVectorChart(missingPage, "light");
  await assertStaticVisualAlignment(missingPage, { mobile: false });
  await assertStaticSourceTooltips(missingPage, { mobile: false });
  await missingDecompression.close();

  const missingDecompressionMobile = await browser.newContext({
    hasTouch: true,
    viewport: { width: 390, height: 844 },
  });
  const missingMobilePage = await missingDecompressionMobile.newPage();
  await missingMobilePage.addInitScript(() => { delete globalThis.DecompressionStream; });
  await missingMobilePage.goto(pathToFileURL(reportFile).href, { waitUntil: "load" });
  await missingMobilePage.waitForFunction(
    () => document.documentElement.dataset.dataAnalyticsPortableReader === "unsupported",
  );
  await assertStaticSourceTooltips(missingMobilePage, { mobile: true });
  await assertMobileTableTooltipEscapesOverflow(missingMobilePage, { runtimeReady: true });
  await assertMobileTooltipWithinVisualViewport(missingDecompressionMobile, missingMobilePage);
  await missingDecompressionMobile.close();

  const missingDecompressionZoomedTablet = await browser.newContext({
    hasTouch: true,
    viewport: { width: 768, height: 900 },
  });
  const missingZoomedTabletPage = await missingDecompressionZoomedTablet.newPage();
  await missingZoomedTabletPage.addInitScript(() => { delete globalThis.DecompressionStream; });
  await missingZoomedTabletPage.goto(pathToFileURL(reportFile).href, { waitUntil: "load" });
  await missingZoomedTabletPage.waitForFunction(
    () => document.documentElement.dataset.dataAnalyticsPortableReader === "unsupported",
  );
  await assertMobileTooltipWithinVisualViewport(
    missingDecompressionZoomedTablet,
    missingZoomedTabletPage,
    { expectLayoutMobile: false },
  );
  await missingDecompressionZoomedTablet.close();

  const original = readFileSync(reportFile, "utf8");
  const corrupt = original.replace(
    /(<template id="data-analytics-portable-reader-runtime-source"[^>]*>)[\s\S]*?(<\/template>)/,
    "$1AAAA$2",
  );
  assert.notEqual(corrupt, original);
  const corruptFile = join(directory, "corrupt-runtime.html");
  writeFileSync(corruptFile, corrupt, "utf8");
  const corruptContext = await browser.newContext();
  const corruptPage = await corruptContext.newPage();
  await corruptPage.goto(pathToFileURL(corruptFile).href, { waitUntil: "load" });
  await corruptPage.waitForFunction(() => document.documentElement.dataset.dataAnalyticsPortableReader === "failed");
  assert.equal(await corruptPage.locator("[data-portable-fallback]").isVisible(), true);
  assert.equal(await corruptPage.locator('html[data-portable-source-tooltips-ready="true"]').count(), 1);
  await assertStaticVectorChart(corruptPage, "light");
  await assertStaticSourceTooltips(corruptPage, { mobile: false });
  await corruptContext.close();

  const blockedContext = await browser.newContext({ viewport: { width: 1024, height: 800 } });
  const blockedPage = await blockedContext.newPage();
  await blockedPage.goto(pathToFileURL(blockedFile).href, { waitUntil: "load" });
  await waitReady(blockedPage, 1_500);
  assert.match(await blockedPage.locator(ROOT).innerText(), /Warehouse access is required|No rows available|No rows match/);
  await blockedContext.close();
}

async function printChecks(browser, reportFile, directory) {
  const context = await browser.newContext({
    colorScheme: "dark",
    viewport: { width: 1200, height: 900 },
  });
  const page = await context.newPage();
  await page.goto(pathToFileURL(reportFile).href, { waitUntil: "load" });
  await waitReady(page, 1_500);
  await page.emulateMedia({ media: "print" });
  assert.equal(await page.locator("[data-portable-fallback]").evaluate((node) => getComputedStyle(node).display), "block");
  assert.equal(await page.locator("#data-analytics-portable-reader").evaluate((node) => getComputedStyle(node).display), "none");
  assert.equal(
    await page.locator("[data-portable-fallback]").evaluate((node) => {
      const title = node.querySelector(".portable-page-header h1")?.textContent?.trim();
      return Array.from(node.querySelectorAll("h1")).filter((heading) => (
        heading.textContent?.trim() === title && getComputedStyle(heading).display !== "none"
      )).length;
    }),
    1,
    "print should render one report title",
  );
  await assertStaticVectorChart(page, "light");
  const printValueHosts = page.locator(".portable-source-value[data-portable-source-host]");
  const repeatedValueTooltips = printValueHosts.locator(":scope > .portable-source-tooltip-content");
  const canonicalSummaries = page.locator(".portable-source-summary > .portable-source-summary-content");
  const chartSource = page.locator(
    "figure.portable-chart-summary[data-portable-source-host] > .portable-inline-source > .portable-source-tooltip-content",
  );
  assert.equal(await printValueHosts.count(), 12);
  assert.equal(await repeatedValueTooltips.count(), 12);
  assert.equal(
    await repeatedValueTooltips.evaluateAll((nodes) => nodes.every((node) => getComputedStyle(node).display === "none")),
    true,
    "print should hide every repeated value-level tooltip body",
  );
  assert.equal(
    await printValueHosts.evaluateAll((nodes) => nodes.every((node) => (
      getComputedStyle(node).textDecorationLine === "none" && getComputedStyle(node).cursor !== "help"
    ))),
    true,
    "print should remove the interactive underline and cursor",
  );
  assert.equal(await canonicalSummaries.count(), 5, "sourced metric cards, table, and narrative should each print one canonical source summary");
  assert.equal(
    await canonicalSummaries.evaluateAll((nodes) => nodes.every((node) => getComputedStyle(node).display === "block")),
    true,
  );
  assert.equal(await chartSource.count(), 1, "the chart should retain one canonical source body");
  assert.equal(await chartSource.isVisible(), true);
  for (const block of [
    ...await page.locator("article.portable-metric-card").all(),
    page.locator('[data-table-id="segment_detail"]'),
    page.locator('[data-artifact-block-id="recommendation"]'),
  ]) {
    assert.equal(await block.locator(":scope > .portable-source-summary").count(), 1, "each sourced metric, table, or narrative block should print one summary");
  }
  assert.equal(await page.locator(".portable-source-tooltip-trigger").count(), 0);
  assert.equal(
    await page.locator(".portable-source-summary").first().evaluate((node) => getComputedStyle(node).position),
    "static",
  );
  assert.equal(
    await canonicalSummaries.first().evaluate((node) => getComputedStyle(node).position),
    "static",
  );
  assert.equal(await page.locator(".portable-sources").isHidden(), true);
  const printDate = page.locator(".portable-page-meta time");
  assert.equal(await printDate.isVisible(), true, "print should retain the generated date");
  assert.equal(await printDate.getAttribute("datetime"), "2026-07-07T20:00:00Z");
  assert.equal(await page.locator("body").evaluate((node) => getComputedStyle(node).backgroundColor), "rgb(255, 255, 255)");
  const printText = await page.locator("[data-portable-fallback]").innerText();
  assert.match(printText, /Source: Revenue warehouse query[\s\S]*Table: analytics\.revenue_reader_qa/);
  assert.match(printText, /Source: Retention snapshot[\s\S]*Table: analytics\.retention_snapshot/);
  assert.equal((printText.match(/Source: Revenue warehouse query/g) ?? []).length, 5);
  assert.equal((printText.match(/Source: Retention snapshot/g) ?? []).length, 1);
  assert.doesNotMatch(printText, /SQL query|SELECT region/);
  const pdf = join(directory, "portable-report.pdf");
  await page.pdf({ path: pdf, format: "Letter", printBackground: true });
  assert.ok(readFileSync(pdf).byteLength > 10_000);
  await context.close();

  const mobileContext = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const mobilePage = await mobileContext.newPage();
  await mobilePage.addInitScript(() => { delete globalThis.DecompressionStream; });
  await mobilePage.goto(pathToFileURL(reportFile).href, { waitUntil: "load" });
  const mobileHost = mobilePage.locator(".portable-source-value[data-portable-source-host]").first();
  await mobileHost.evaluate((node) => node.setAttribute("data-portable-source-tooltip-open", "true"));
  await mobilePage.emulateMedia({ media: "print" });
  const mobilePrintTooltip = mobileHost.locator(":scope > .portable-source-tooltip-content");
  assert.equal(await mobilePrintTooltip.isHidden(), true);
  assert.equal(await mobilePrintTooltip.evaluate((node) => getComputedStyle(node).maxHeight), "none");
  assert.equal(await mobilePrintTooltip.evaluate((node) => getComputedStyle(node).overflow), "visible");
  assert.equal(await mobilePrintTooltip.evaluate((node) => getComputedStyle(node).paddingTop), "0px");
  assert.equal(await mobilePage.locator(".portable-source-summary-content").first().isVisible(), true);
  assert.equal(await mobilePage.locator(".portable-page-meta time").isVisible(), true);
  await mobileContext.close();
  return pdf;
}

export async function runPortableBrowserSmoke() {
  const directory = mkdtempSync(join(tmpdir(), "data-analytics-portable-browser-"));
  const dashboardInput = dashboardFixture();
  const dashboardFile = buildArtifact(directory, "dashboard", dashboardInput);
  const reportInput = reportFixture();
  const reportFile = buildArtifact(directory, "report", reportInput);
  const gradientInput = reportFixture();
  gradientInput.manifest.title = "Portable Reader SVG Gradient QA";
  gradientInput.manifest.blocks[0].body = "# Portable Reader SVG Gradient QA";
  gradientInput.manifest.charts[0].type = "area";
  const gradientFile = buildArtifact(directory, "svg-gradient", gradientInput);
  const blockedFile = buildArtifact(directory, "blocked", blockedFixture());
  const browser = await chromium.launch({ executablePath: browserExecutable(), headless: true });

  try {
    const staticCharts = await extractPortableChartSvgs({
      htmlPath: reportFile,
      readyTimeoutMs: 5_000,
    });
    assert.ok(staticCharts.chart?.light?.svg && staticCharts.chart?.dark?.svg);
    assert.doesNotMatch(staticCharts.chart.light.svg, /<img|data:image\//i);
    assert.doesNotMatch(staticCharts.chart.dark.svg, /<img|data:image\//i);
    assertExtractedSvgIntegrity(staticCharts.chart.light.svg);
    assertExtractedSvgIntegrity(staticCharts.chart.dark.svg);
    assert.ok(
      staticCharts.chart.light.legend.items.length > 0 && staticCharts.chart.dark.legend.items.length > 0,
    );
    assert.notEqual(
      staticCharts.chart.light.legend.items[0].color,
      staticCharts.chart.dark.legend.items[0].color,
      "light and dark SVG variants should resolve different legend paint",
    );
    const dashboardStaticCharts = await extractPortableChartSvgs({
      htmlPath: dashboardFile,
      readyTimeoutMs: 5_000,
    });
    assert.ok(dashboardStaticCharts.trend?.light?.svg && dashboardStaticCharts.trend?.dark?.svg);
    const gradientCharts = await extractPortableChartSvgs({
      htmlPath: gradientFile,
      readyTimeoutMs: 5_000,
    });
    assert.ok(gradientCharts.chart?.light?.svg && gradientCharts.chart?.dark?.svg);
    assertExtractedSvgIntegrity(gradientCharts.chart.light.svg, { requireLocalReference: true });
    assertExtractedSvgIntegrity(gradientCharts.chart.dark.svg, { requireLocalReference: true });
    assert.deepEqual(
      gradientCharts.chart.light.legend.items.map((item) => item.label),
      ["Actual", "Plan"],
    );
    assert.ok(
      gradientCharts.chart.light.legend.items.some((item) => item.marker === "line" && item.dasharray),
      "native static legend should preserve the dashed planning-series marker",
    );
    writeFileSync(reportFile, buildPortableArtifact(reportInput, { staticCharts }), "utf8");
    writeFileSync(dashboardFile, buildPortableArtifact(dashboardInput, { staticCharts: dashboardStaticCharts }), "utf8");
    const cliVerifier = await verifyPortableArtifact({
      browserExecutable: browserExecutable(),
      htmlPath: reportFile,
      timeoutMs: 10_000,
    });
    assert.deepEqual(cliVerifier.viewports, [1_440, 390]);
    assert.equal(cliVerifier.sourceDialog, "passed");
    assert.match(cliVerifier.sourceInteraction, /semantic_click/);
    const dashboard = await dashboardChecks(browser, dashboardFile, directory);
    const serializedReplay = await serializedReplayChecks(browser, dashboardFile, directory);
    const reports = await reportChecks(browser, reportFile, directory);
    await fallbackAndFailureChecks(browser, reportFile, dashboardFile, blockedFile, directory);
    const pdf = await printChecks(browser, reportFile, directory);
    const result = { cliVerifier, directory, dashboard, serializedReplay, reports, pdf };
    console.log(JSON.stringify(result, null, 2));
    return result;
  } finally {
    await browser.close();
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  await runPortableBrowserSmoke();
}
