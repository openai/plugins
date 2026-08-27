import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { createServer } from "node:http";
import {
  mkdtempSync,
  readFileSync,
  readdirSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { pathToFileURL, fileURLToPath } from "node:url";
import { gunzipSync } from "node:zlib";

import pixelmatch from "pixelmatch";
import { chromium } from "playwright-core";
import { PNG } from "pngjs";

import {
  browserExecutable,
  dashboardFixture,
  reportFixture,
} from "./portable-browser.smoke.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const pluginRoot = resolve(here, "..");
const builderPath = resolve(
  pluginRoot,
  "skills/build-report/scripts/build_portable_artifact.mjs",
);
const assetDirectory = resolve(pluginRoot, "assets");

function normalizedAsset(name) {
  const prefix = `${name}.gz.b64.part`;
  const encoded = readdirSync(assetDirectory)
    .filter((entry) => entry.startsWith(prefix))
    .sort()
    .map((entry) => readFileSync(join(assetDirectory, entry), "utf8").replace(/\s/g, ""))
    .join("");
  assert.ok(encoded, `missing normalized ${name} parts`);
  return gunzipSync(Buffer.from(encoded, "base64")).toString("utf8");
}

function buildPortable(directory, name, fixture) {
  const input = join(directory, `${name}.json`);
  const output = join(directory, `${name}.html`);
  writeFileSync(input, JSON.stringify(fixture), "utf8");
  execFileSync(process.execPath, [builderPath, "--input", input, "--output", output]);
  return output;
}

function mergedManifest(fixture) {
  const sources = new Map();
  for (const source of [...(fixture.manifest.sources ?? []), ...(fixture.sources ?? [])]) {
    sources.set(source.id, { ...(sources.get(source.id) ?? {}), ...source });
  }
  return { ...fixture.manifest, sources: [...sources.values()] };
}

function jsonResponse(response, value) {
  response.writeHead(200, {
    "content-type": "application/json; charset=utf-8",
    "cache-control": "no-store",
  });
  response.end(JSON.stringify(value));
}

function mcpPayload(fixture) {
  return {
    ok: true,
    widget_type: "artifact",
    surface: fixture.surface,
    manifest: mergedManifest(fixture),
    snapshot: fixture.snapshot,
    sources: fixture.sources ?? [],
    package_info: {
      controls: { edit: true, refresh: true, persistence: true, copyAsImage: true },
      mode: "mcp",
    },
  };
}

async function parityServer(widgetHtml) {
  let fixture = reportFixture();
  const server = createServer((request, response) => {
    const url = new URL(request.url ?? "/", "http://127.0.0.1");
    if (url.pathname === "/" || url.pathname === "/index.html") {
      const payload = JSON.stringify(mcpPayload(fixture)).replace(/</g, "\\u003c");
      const hostBridge = `<script>window.openai={toolOutput:${payload},availableDisplayModes:["inline","fullscreen"],displayMode:"fullscreen",requestDisplayMode:async request=>request,sendFollowUpMessage:async()=>({ok:true})};</script>`;
      response.writeHead(200, { "content-type": "text/html; charset=utf-8" });
      response.end(widgetHtml.replace("<head>", `<head>${hostBridge}`));
      return;
    }
    if (url.pathname === "/api/manifest") {
      jsonResponse(response, mergedManifest(fixture));
      return;
    }
    if (url.pathname === "/api/snapshot") {
      jsonResponse(response, fixture.snapshot);
      return;
    }
    if (url.pathname === "/api/package") {
      jsonResponse(response, {
        controls: { edit: true, refresh: true, persistence: true, copyAsImage: true },
        mode: "mcp",
      });
      return;
    }
    if (url.pathname === "/api/source-file") {
      response.writeHead(200, { "content-type": "text/plain; charset=utf-8" });
      response.end(fixture.sources?.[0]?.query?.sql ?? "");
      return;
    }
    response.writeHead(404, { "content-type": "text/plain" });
    response.end("Not found");
  });
  await new Promise((resolveListen, rejectListen) => {
    server.once("error", rejectListen);
    server.listen(0, "127.0.0.1", resolveListen);
  });
  const address = server.address();
  assert.ok(address && typeof address === "object");
  return {
    setFixture(nextFixture) { fixture = nextFixture; },
    url: `http://127.0.0.1:${address.port}/`,
    close: () => new Promise((resolveClose, rejectClose) => server.close((error) => error ? rejectClose(error) : resolveClose())),
  };
}

async function openPortable(context, file) {
  const page = await context.newPage();
  await page.goto(pathToFileURL(file).href, { waitUntil: "load" });
  await page.waitForFunction(() => document.documentElement.dataset.dataAnalyticsPortableReader === "ready");
  return page;
}

async function openMcp(context, url, title) {
  const page = await context.newPage();
  const errors = [];
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(message.text());
  });
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto(url, { waitUntil: "load" });
  try {
    await page.getByText(title, { exact: true }).first().waitFor({ timeout: 5_000 });
  } catch (error) {
    throw new Error(`MCP fixture failed to render: ${errors.join(" | ")} | ${await page.locator("body").innerText()}`, { cause: error });
  }
  await page.locator(".analytics-layout-canvas").waitFor();
  return page;
}

function normalizedText(text) {
  return text.replace(/\s+/g, " ").trim();
}

async function sharedContent(page) {
  return {
    fontFamily: await page.locator("main.dashboard-shell").evaluate((node) => getComputedStyle(node).fontFamily),
    filters: normalizedText(await page.locator(".filter-toolbar").allInnerTexts().then((values) => values.join(" "))),
    blocks: normalizedText(await page.locator(".analytics-layout-canvas").innerText()),
    blockTypes: await page.locator(".analytics-layout-item").evaluateAll((nodes) => nodes.map((node) =>
      [...node.classList].find((name) => name.startsWith("analytics-layout-item-") && name !== "analytics-layout-item-shell") ?? "unknown")),
  };
}

async function sourceDialogText(page) {
  const button = page.locator(
    'button[data-artifact-action="open-options"]' +
      '[data-artifact-kind="card"]' +
      '[data-artifact-id="revenue"]',
  );
  const card = button.locator("..").locator("..");
  await card.evaluate((node) => window.scrollTo(0, Math.max(0, window.scrollY + node.getBoundingClientRect().top - 72)));
  await button.focus();
  await button.press("ArrowDown");
  const sourceAction = page.locator('[role="menu"] [data-artifact-action="view-source"]');
  await sourceAction.waitFor();
  await sourceAction.focus();
  await sourceAction.press("Enter");
  const dialog = page.locator('[data-artifact-dialog="source"]');
  await dialog.waitFor();
  const overview = normalizedText(await dialog.innerText());
  await dialog.getByRole("tab", { name: "SQL query" }).click();
  await dialog.getByRole("button", { name: "Copy query" }).waitFor();
  const sql = normalizedText(await dialog.innerText());
  await dialog.getByRole("button", { name: "Close data source" }).click();
  return { overview, sql };
}

async function sharedScreenshot(page, output, viewportName, colorScheme, surface, adapter) {
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.mouse.move(0, 0);
  await page.waitForTimeout(50);
  const shell = page.locator("main.dashboard-shell");
  await shell.screenshot({
    path: output,
    animations: "disabled",
    caret: "hide",
    mask: [page.locator(".analytics-top-bar")],
    maskColor: "#ff00ff",
  });
  return { viewportName, colorScheme, surface, adapter, output };
}

function imageDifference(first, second) {
  const left = PNG.sync.read(readFileSync(first));
  const right = PNG.sync.read(readFileSync(second));
  assert.deepEqual(
    { width: left.width, height: left.height },
    { width: right.width, height: right.height },
  );
  const differingPixels = pixelmatch(
    left.data,
    right.data,
    null,
    left.width,
    left.height,
    { includeAA: false, threshold: 0.1 },
  );
  return {
    width: left.width,
    height: left.height,
    differingPixels,
    differingPercent: differingPixels * 100 / (left.width * left.height),
  };
}

const directory = mkdtempSync(join(tmpdir(), "data-analytics-portable-parity-"));
const widgetHtml = normalizedAsset("datascience-artifact-widget.html");
const server = await parityServer(widgetHtml);
const browser = await chromium.launch({ executablePath: browserExecutable(), headless: true });
const results = [];

try {
  for (const [surface, fixture] of [
    ["report", reportFixture()],
    ["dashboard", dashboardFixture()],
  ]) {
    server.setFixture(fixture);
    const portableFile = buildPortable(directory, surface, fixture);
    for (const viewport of [
      { name: "desktop", width: 1440, height: 1000 },
      { name: "tablet", width: 820, height: 1000 },
      { name: "mobile", width: 390, height: 844 },
    ]) {
      for (const colorScheme of ["light", "dark"]) {
        const context = await browser.newContext({
          viewport: { width: viewport.width, height: viewport.height },
          colorScheme,
          reducedMotion: "reduce",
        });
        const portable = await openPortable(context, portableFile);
        const mcp = await openMcp(context, server.url, fixture.manifest.title);
        assert.deepEqual(await sharedContent(portable), await sharedContent(mcp));
        if (viewport.name === "desktop" && colorScheme === "light") {
          assert.deepEqual(await sourceDialogText(portable), await sourceDialogText(mcp));
        }

        const portableImage = join(directory, `${surface}-${viewport.name}-${colorScheme}-portable.png`);
        const mcpImage = join(directory, `${surface}-${viewport.name}-${colorScheme}-mcp.png`);
        await sharedScreenshot(portable, portableImage, viewport.name, colorScheme, surface, "portable");
        await sharedScreenshot(mcp, mcpImage, viewport.name, colorScheme, surface, "mcp");
        const difference = imageDifference(portableImage, mcpImage);
        assert.ok(
          difference.differingPercent <= 0.5,
          `${surface} ${viewport.name} ${colorScheme} differs by ${difference.differingPercent.toFixed(3)}% pixels`,
        );
        results.push({ surface, viewport: viewport.name, colorScheme, difference, portableImage, mcpImage });
        await context.close();
      }
    }
  }
  console.log(JSON.stringify({ directory, results }, null, 2));
} finally {
  await browser.close();
  await server.close();
}
