import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import test from "node:test";

import { buildPortableArtifact } from "../skills/build-report/scripts/build_portable_artifact.mjs";
import {
  isLocalPortableRequest,
  resolveChromiumExecutable,
} from "../skills/build-report/scripts/portable_browser_helpers.mjs";
import {
  buildPortableVerifierHarness,
  chromiumDumpArguments,
  injectPortableVerifierProbe,
  parsePortableVerifierDump,
  spawnChromiumDump,
} from "../skills/build-report/scripts/portable_browser_cli.mjs";
import {
  assertArtifactMatchesEmbedded,
  expectedPortableCounts,
  extractEmbeddedArtifact,
  parseArguments,
  VerificationDeadline,
  verifyPortableArtifactStructure,
  waitForResponsiveLayout,
} from "../skills/build-report/scripts/verify_portable_artifact.mjs";
import { reportFixture } from "./portable-browser.smoke.mjs";

function fakeExecutable(path) {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, "", "utf8");
  return path;
}

test("portable verifier reads the validated artifact embedded in generated HTML", () => {
  const input = reportFixture();
  const html = buildPortableArtifact(input);
  const embedded = extractEmbeddedArtifact(html);

  assert.equal(embedded.manifest.title, input.manifest.title);
  assert.deepEqual(expectedPortableCounts(embedded), {
    blocks: 8,
    charts: 1,
    html: 0,
    metrics: 3,
    tables: 1,
  });
  assert.throws(
    () => extractEmbeddedArtifact("<!doctype html><title>Not portable</title>"),
    (error) => error.code === "payload_missing",
  );

  const staleInput = structuredClone(input);
  staleInput.snapshot.datasets.summary[0].revenue = 1;
  assert.throws(
    () => assertArtifactMatchesEmbedded(staleInput, embedded),
    (error) => error.code === "artifact_mismatch" && /exactly match/.test(error.message),
  );
});

test("structural verification requires the exact payload, fallback, reader, and runtime", () => {
  const directory = mkdtempSync(join(tmpdir(), "portable-structural-verifier-"));
  const artifactPath = join(directory, "artifact.json");
  const htmlPath = join(directory, "report.html");
  const input = reportFixture();
  const html = buildPortableArtifact(input);
  writeFileSync(artifactPath, JSON.stringify(input), "utf8");
  writeFileSync(htmlPath, html, "utf8");

  const result = verifyPortableArtifactStructure({ artifactPath, htmlPath });
  assert.equal(result.ok, true);
  assert.equal(result.title, input.manifest.title);
  assert.deepEqual(result.counts, {
    blocks: 8,
    charts: 1,
    html: 0,
    metrics: 3,
    tables: 1,
  });

  writeFileSync(
    htmlPath,
    html.replace("data-analytics-portable-reader-runtime-source", "missing-runtime-source"),
    "utf8",
  );
  assert.throws(
    () => verifyPortableArtifactStructure({ artifactPath, htmlPath }),
    (error) => error.code === "runtime_missing",
  );
});

test("browser resolver honors an explicit executable and rejects a stale explicit path", () => {
  const directory = mkdtempSync(join(tmpdir(), "portable-browser-explicit-"));
  const executable = fakeExecutable(join(directory, "chromium"));

  assert.equal(resolveChromiumExecutable({
    env: { PLAYWRIGHT_EXECUTABLE_PATH: executable },
    packagedExecutable: join(directory, "missing-packaged"),
  }), executable);
  assert.throws(
    () => resolveChromiumExecutable({
      env: { PLAYWRIGHT_EXECUTABLE_PATH: join(directory, "missing") },
      packagedExecutable: executable,
    }),
    (error) => error.code === "browser_unavailable" && /does not exist/.test(error.message),
  );
});

test("browser resolver finds headless-shell layouts in configured and macOS caches", () => {
  const directory = mkdtempSync(join(tmpdir(), "portable-browser-cache-"));
  const configuredRoot = join(directory, "configured");
  const configured = fakeExecutable(join(
    configuredRoot,
    "chromium_headless_shell-999",
    "chrome-headless-shell-linux64",
    "chrome-headless-shell",
  ));
  assert.equal(resolveChromiumExecutable({
    env: { PLAYWRIGHT_BROWSERS_PATH: configuredRoot },
    home: join(directory, "home"),
    packagedExecutable: join(directory, "missing-packaged"),
    platform: "linux",
  }), configured);

  const macHome = join(directory, "mac-home");
  const headlessShell = fakeExecutable(join(
    macHome,
    ".cache/ms-playwright",
    "chromium_headless_shell-1228",
    "chrome-headless-shell-mac-arm64",
    "chrome-headless-shell",
  ));
  assert.equal(resolveChromiumExecutable({
    env: {},
    home: macHome,
    packagedExecutable: join(directory, "missing-packaged"),
    platform: "darwin",
  }), headlessShell);
});

test("browser resolver does not auto-select full Chrome from Playwright caches", () => {
  const directory = mkdtempSync(join(tmpdir(), "portable-browser-full-chrome-"));
  const root = join(directory, "cache");
  fakeExecutable(join(
    root,
    "chromium-1229",
    "chrome-mac-arm64",
    "Google Chrome for Testing.app",
    "Contents/MacOS/Google Chrome for Testing",
  ));
  assert.throws(
    () => resolveChromiumExecutable({
      env: { PLAYWRIGHT_BROWSERS_PATH: root },
      home: join(directory, "home"),
      platform: "darwin",
    }),
    (error) => error.code === "browser_unavailable" && /headless-shell/.test(error.message),
  );
});

test("browser resolver prefers headless-shell over full Chrome at the same revision", () => {
  const directory = mkdtempSync(join(tmpdir(), "portable-browser-preference-"));
  const root = join(directory, "cache");
  fakeExecutable(join(
    root,
    "chromium-1229",
    "chrome-mac-arm64",
    "Google Chrome for Testing.app",
    "Contents/MacOS/Google Chrome for Testing",
  ));
  const headlessShell = fakeExecutable(join(
    root,
    "chromium_headless_shell-1229",
    "chrome-headless-shell-mac-arm64",
    "chrome-headless-shell",
  ));
  assert.equal(resolveChromiumExecutable({
    env: { PLAYWRIGHT_BROWSERS_PATH: root },
    home: join(directory, "home"),
    platform: "darwin",
  }), headlessShell);
});

test("browser resolver supports legacy Playwright headless_shell cache layouts", () => {
  const directory = mkdtempSync(join(tmpdir(), "portable-browser-legacy-"));
  const root = join(directory, "cache");
  const legacyShell = fakeExecutable(join(
    root,
    "chromium_headless_shell-1181",
    "chrome-mac",
    "headless_shell",
  ));
  assert.equal(resolveChromiumExecutable({
    env: { PLAYWRIGHT_BROWSERS_PATH: root },
    home: join(directory, "home"),
    platform: "darwin",
  }), legacyShell);
});

test("dependency-free Chromium probe injection and dump parsing use stable markers", () => {
  const source = "<!doctype html><html><head><meta http-equiv=\"Content-Security-Policy\"></head><body></body></html>";
  const instrumented = injectPortableVerifierProbe(source, {
    actionTimeoutMs: 100,
    channel: "test-channel",
    checkSource: false,
    expectedCounts: { blocks: 0, charts: 0, html: 0, metrics: 0, tables: 0 },
    readerRoot: "#reader",
    readyTimeoutMs: 100,
    title: "Test",
    viewport: { height: 844, name: "mobile", width: 390 },
  });
  assert.ok(
    instrumented.indexOf("data-portable-verifier-probe") <
      instrumented.indexOf("Content-Security-Policy"),
    "probe should install error and network capture before the artifact CSP and runtime",
  );
  assert.match(instrumented, /function portableVerifierProbe/);

  const payload = {
    ok: true,
    results: [{ ok: true, viewport: { name: "mobile", width: 390 } }],
  };
  const encoded = Buffer.from(JSON.stringify(payload), "utf8").toString("base64");
  assert.deepEqual(parsePortableVerifierDump(
    `<html><head><meta data-result="${encoded}" ` +
      `id="data-analytics-portable-verifier-result"></head></html>`,
  ), payload);
  assert.throws(
    () => parsePortableVerifierDump("<html></html>"),
    (error) => error.code === "probe_missing",
  );
  assert.throws(
    () => parsePortableVerifierDump(
      `<meta id="data-analytics-portable-verifier-result" data-result="${encoded}">` +
        `<meta id="data-analytics-portable-verifier-result" data-result="${encoded}">`,
    ),
    (error) => error.code === "probe_invalid" && error.details.count === 2,
  );
});

test("Chromium harness and arguments keep both exact viewports offline", () => {
  const harness = buildPortableVerifierHarness({
    channel: "channel",
    frames: [
      { html: "<!doctype html><title>Desktop</title>", viewport: { height: 1000, name: "desktop", width: 1440 } },
      { html: "<!doctype html><title>Mobile</title>", viewport: { height: 844, name: "mobile", width: 390 } },
    ],
    timeoutMs: 5000,
  });
  assert.match(harness, /width="1440"/);
  assert.match(harness, /width="390"/);
  assert.match(harness, /addEventListener\("message"/);
  assert.match(harness, /sandbox="allow-scripts"/);

  const arguments_ = chromiumDumpArguments({
    colorScheme: "dark",
    height: 1000,
    profilePath: "/tmp/profile",
    url: "file:///tmp/harness.html",
    virtualTimeBudgetMs: 5000,
    width: 1846,
  });
  assert.ok(arguments_.includes("--dump-dom"));
  assert.ok(arguments_.includes("--blink-settings=preferredColorScheme=0"));
  assert.ok(arguments_.includes("--host-resolver-rules=MAP * ~NOTFOUND"));
  assert.ok(arguments_.includes("--proxy-server=http://127.0.0.1:9"));
  assert.ok(!arguments_.includes("--allow-file-access-from-files"));
  assert.equal(arguments_.at(-1), "file:///tmp/harness.html");
});

test("Chromium CLI runner uses a direct subprocess without browser-library APIs", async () => {
  const result = await spawnChromiumDump({
    arguments: ["-e", "process.stdout.write('probe-output')"],
    executablePath: process.execPath,
    timeoutMs: 1000,
  });
  assert.equal(result.stdout, "probe-output");
  assert.equal(result.stderr, "");
});

test("Chromium CLI runner bounds diagnostics and preserves process failure codes", async () => {
  const noisy = await spawnChromiumDump({
    arguments: [
      "-e",
      "process.stderr.write('diagnostic-tail'); process.stdout.write('ok')",
    ],
    executablePath: process.execPath,
    maxDiagnosticBytes: 4,
    timeoutMs: 1000,
  });
  assert.equal(noisy.stdout, "ok");
  assert.equal(noisy.stderr, "tail");

  await assert.rejects(
    spawnChromiumDump({
      arguments: ["-e", "process.stderr.write('failed'); process.exit(7)"],
      executablePath: process.execPath,
      timeoutMs: 1000,
    }),
    (error) => error.code === "browser_failed" &&
      error.details.code === 7 &&
      error.details.diagnostics === "failed",
  );
});

test("Chromium CLI runner waits for termination on output limits and timeouts", async () => {
  await assert.rejects(
    spawnChromiumDump({
      arguments: ["-e", "process.stdout.write('too much output')"],
      executablePath: process.execPath,
      maxOutputBytes: 4,
      timeoutMs: 1000,
    }),
    (error) => error.code === "browser_output_limit" && error.details.limit === 4,
  );
  const startedAt = performance.now();
  await assert.rejects(
    spawnChromiumDump({
      arguments: ["-e", "setInterval(() => {}, 1000)"],
      executablePath: process.execPath,
      timeoutMs: 20,
    }),
    (error) => error.code === "browser_timeout" && error.details.timeoutMs === 20,
  );
  assert.ok(performance.now() - startedAt < 1000);
});

test("verifier CLI parsing stays minimal and local URL policy rejects network requests", () => {
  assert.deepEqual(parseArguments(["--html", "report.html"]), { html: "report.html" });
  assert.deepEqual(
    parseArguments([
      "--html",
      "report.html",
      "--artifact",
      "artifact.json",
      "--timeout-ms",
      "9000",
    ]),
    { artifact: "artifact.json", html: "report.html", "timeout-ms": "9000" },
  );
  assert.equal(isLocalPortableRequest("file:///tmp/report.html"), true);
  assert.equal(isLocalPortableRequest("blob:null/abc"), true);
  assert.equal(isLocalPortableRequest("https://example.com/collect"), false);
});

test("whole-run deadline reports a stable timeout once the budget is exhausted", () => {
  let now = 100;
  const deadline = new VerificationDeadline(10, () => now);
  assert.equal(deadline.remainingMs("setup"), 10);
  now = 111;
  assert.throws(
    () => deadline.remainingMs("browser launch"),
    (error) => error.code === "verification_timeout" &&
      /10000ms|10ms/.test(error.message) &&
      error.details.phase === "browser launch",
  );
});

test("whole-run deadline interrupts a hung asynchronous phase", async () => {
  const deadline = new VerificationDeadline(20);
  const started = performance.now();
  await assert.rejects(
    deadline.run("browser launch", () => new Promise(() => {})),
    (error) => error.code === "verification_timeout" &&
      error.details.phase === "browser launch",
  );
  assert.ok(performance.now() - started < 200);
});

test("responsive verification gives asynchronous chart layout a bounded settle window", async () => {
  const calls = [];
  const settledPage = {
    async waitForFunction(predicate, argument, options) {
      calls.push({ argument, options, predicate: String(predicate) });
    },
  };
  assert.equal(await waitForResponsiveLayout(settledPage, 375), true);
  assert.deepEqual(calls[0].options, { polling: "raf", timeout: 375 });
  assert.match(calls[0].predicate, /scrollWidth.*clientWidth/);

  const persistentlyWidePage = {
    async waitForFunction() {
      throw new Error("timed out while still wide");
    },
  };
  assert.equal(await waitForResponsiveLayout(persistentlyWidePage, 25), false);
});
