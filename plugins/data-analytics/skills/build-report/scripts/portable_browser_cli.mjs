import { spawn } from "node:child_process";

import { PortableBrowserError } from "./portable_browser_helpers.mjs";

export const PORTABLE_VERIFIER_RESULT_ID = "data-analytics-portable-verifier-result";

const MAX_BROWSER_OUTPUT_BYTES = 4_000_000;
const MAX_BROWSER_DIAGNOSTIC_BYTES = 64_000;

function encodeJson(value) {
  return Buffer.from(JSON.stringify(value), "utf8").toString("base64");
}

function decodeJson(value) {
  return JSON.parse(Buffer.from(value, "base64").toString("utf8"));
}

function escapeAttribute(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll('"', "&quot;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

/**
 * Runs inside each instrumented portable artifact. Keep this function
 * self-contained: its source is serialized into the temporary HTML without a
 * bundler or a browser automation library.
 */
function portableVerifierProbe(encodedConfig) {
  function decode(value) {
    const binary = atob(value);
    const bytes = Uint8Array.from(binary, (character) => character.charCodeAt(0));
    return JSON.parse(new TextDecoder().decode(bytes));
  }

  const sendToParent = (message, targetOrigin) => parent.postMessage(message, targetOrigin);
  const config = decode(encodedConfig);
  document.currentScript?.remove();
  const startedAt = performance.now();
  const consoleErrors = [];
  const pageErrors = [];
  const externalRequests = [];
  const externalRequestSet = new Set();
  const terminalStates = new Set(["ready", "failed", "missing-runtime", "unsupported"]);

  function compact(value) {
    if (value instanceof Error) return value.stack || value.message;
    if (typeof value === "string") return value;
    try {
      return JSON.stringify(value);
    } catch {
      return String(value);
    }
  }

  function append(items, value) {
    if (items.length >= 20) return;
    items.push(compact(value).slice(0, 500));
  }

  function externalUrl(value) {
    try {
      const candidate = typeof value === "string" ? value : value?.url ?? String(value);
      const parsed = new URL(candidate, location.href);
      if (["about:", "blob:", "data:", "file:"].includes(parsed.protocol)) return null;
      return parsed.href;
    } catch {
      return null;
    }
  }

  function recordRequest(value) {
    const url = externalUrl(value);
    if (!url || externalRequestSet.has(url) || externalRequests.length >= 20) return;
    externalRequestSet.add(url);
    externalRequests.push(url);
  }

  const originalConsoleError = console.error.bind(console);
  console.error = (...values) => {
    append(consoleErrors, values.map(compact).join(" "));
    return originalConsoleError(...values);
  };

  addEventListener("error", (event) => {
    if (event.error || event.message) append(pageErrors, event.error || event.message);
  });
  addEventListener("unhandledrejection", (event) => append(pageErrors, event.reason));
  addEventListener("securitypolicyviolation", (event) => recordRequest(event.blockedURI));

  try {
    if (typeof fetch === "function") {
      const originalFetch = fetch;
      globalThis.fetch = function instrumentedFetch(input, ...arguments_) {
        recordRequest(input);
        return Reflect.apply(originalFetch, this, [input, ...arguments_]);
      };
    }
    if (typeof XMLHttpRequest === "function") {
      const originalOpen = XMLHttpRequest.prototype.open;
      XMLHttpRequest.prototype.open = function instrumentedOpen(method, url, ...arguments_) {
        recordRequest(url);
        return Reflect.apply(originalOpen, this, [method, url, ...arguments_]);
      };
    }
    if (typeof navigator.sendBeacon === "function") {
      const originalSendBeacon = navigator.sendBeacon.bind(navigator);
      navigator.sendBeacon = (url, data) => {
        recordRequest(url);
        return originalSendBeacon(url, data);
      };
    }
    for (const constructorName of ["EventSource", "WebSocket"]) {
      const Original = globalThis[constructorName];
      if (typeof Original !== "function") continue;
      function Instrumented(url, ...arguments_) {
        recordRequest(url);
        return new Original(url, ...arguments_);
      }
      Object.setPrototypeOf(Instrumented, Original);
      Instrumented.prototype = Original.prototype;
      globalThis[constructorName] = Instrumented;
    }
    if (typeof PerformanceObserver === "function") {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) recordRequest(entry.name);
      });
      observer.observe({ type: "resource", buffered: true });
    }
  } catch (error) {
    append(pageErrors, `Verifier instrumentation failed: ${compact(error)}`);
  }

  function delay(milliseconds) {
    return new Promise((resolve) => setTimeout(resolve, milliseconds));
  }

  async function waitUntil(predicate, timeoutMs) {
    const deadline = performance.now() + timeoutMs;
    do {
      const result = predicate();
      if (result) return result;
      await delay(16);
    } while (performance.now() < deadline);
    return null;
  }

  function fail(code, message, details = {}) {
    const error = new Error(message);
    error.code = code;
    error.details = details;
    throw error;
  }

  function check(condition, code, message, details = {}) {
    if (!condition) fail(code, message, details);
  }

  function isVisible(node) {
    if (!(node instanceof Element)) return false;
    const style = getComputedStyle(node);
    const rect = node.getBoundingClientRect();
    return !node.hidden &&
      style.display !== "none" &&
      style.visibility !== "hidden" &&
      rect.width > 0 &&
      rect.height > 0;
  }

  function visibleElement(selector, root = document) {
    return Array.from(root.querySelectorAll(selector)).find(isVisible) ?? null;
  }

  function dispatchKey(target, key) {
    const keyCodes = { ArrowDown: 40, Enter: 13, Escape: 27 };
    const keyCode = keyCodes[key] ?? 0;
    for (const type of ["keydown", "keyup"]) {
      target.dispatchEvent(new KeyboardEvent(type, {
        bubbles: true,
        cancelable: true,
        code: key,
        key,
        keyCode,
        which: keyCode,
      }));
    }
  }

  function renderedCounts(root) {
    return {
      blocks: root.querySelectorAll("[data-analytics-layout-item]").length,
      charts: root.querySelectorAll(".chart-frame").length,
      html: root.querySelectorAll("iframe.report-html-frame").length,
      metrics: root.querySelectorAll(".report-metric-card").length,
      tables: root.querySelectorAll(".table-card").length,
    };
  }

  function sameCounts(actual, expected) {
    return ["blocks", "charts", "html", "metrics", "tables"]
      .every((key) => actual[key] === expected[key]);
  }

  async function exerciseSourceDialog(timeoutMs) {
    const started = performance.now();
    const remaining = () => Math.max(1, timeoutMs - (performance.now() - started));
    const button = document.querySelector(
      `${config.readerRoot} button[data-artifact-action="open-options"]` +
        `[data-artifact-has-source="true"]`,
    );
    check(
      button instanceof HTMLButtonElement,
      "source_control_missing",
      "Artifact declares source-backed content, but no source menu button was rendered.",
    );
    button.scrollIntoView({ block: "center", inline: "nearest" });
    button.focus();
    dispatchKey(button, "ArrowDown");

    let menu = await waitUntil(
      () => visibleElement('[role="menu"]'),
      Math.min(250, remaining()),
    );
    let activation = "keyboard_menu_semantic_click";
    if (!menu) {
      // The direct CLI cannot produce trusted input events. Retain the
      // ArrowDown accessibility probe above, then fall back to the semantic
      // button activation when Chromium does not deliver that synthetic event
      // through the framework scheduler.
      button.click();
      activation = "semantic_click";
      menu = await waitUntil(() => visibleElement('[role="menu"]'), remaining());
    }
    check(menu, "source_control_missing", "The source options menu did not open.");
    const sourceAction = menu.querySelector('[data-artifact-action="view-source"]');
    check(
      sourceAction instanceof HTMLButtonElement && sourceAction.getAttribute("role") === "menuitem",
      "source_control_missing",
      "The source menu has no semantic View data source action.",
    );

    sourceAction.focus();
    sourceAction.click();
    const dialog = await waitUntil(
      () => document.querySelector('[data-artifact-dialog="source"]'),
      remaining(),
    );
    check(
      dialog,
      "source_dialog_invalid",
      "The View data source action did not open a dialog.",
      {
        dialogCount: document.querySelectorAll('[data-artifact-dialog="source"]').length,
        menuCount: document.querySelectorAll('[role="menu"]').length,
      },
    );
    const visibleDialog = await waitUntil(() => isVisible(dialog), remaining());
    check(
      visibleDialog,
      "source_dialog_invalid",
      "The rendered source dialog did not become visible.",
    );
    const overviewTab = Array.from(dialog.querySelectorAll('[role="tab"]'))
      .find((node) => node.textContent?.trim() === "Overview");
    check(
      overviewTab,
      "source_dialog_invalid",
      "Source dialog opened without its Overview tab.",
    );
    dispatchKey(document.activeElement || dialog, "Escape");
    return activation;
  }

  function send(result) {
    sendToParent({
      channel: config.channel,
      result: {
        ...result,
        viewport: config.viewport,
      },
    }, "*");
  }

  async function run() {
    const timings = {};
    try {
      const readyStartedAt = performance.now();
      const readerState = await waitUntil(() => {
        const state = document.documentElement.dataset.dataAnalyticsPortableReader ?? "";
        return terminalStates.has(state) ? state : null;
      }, config.readyTimeoutMs);
      timings.readerReadyMs = Math.round((performance.now() - readyStartedAt) * 10) / 10;
      if (!readerState) {
        fail(
          "reader_timeout",
          `Portable reader did not reach a terminal state within ${config.readyTimeoutMs}ms.`,
          {
            state: document.documentElement.dataset.dataAnalyticsPortableReader ?? "unset",
          },
        );
      }
      check(
        readerState === "ready",
        `reader_${readerState}`,
        `Portable reader entered terminal failure state: ${readerState}.`,
        { state: readerState },
      );

      const contentStartedAt = performance.now();
      check(
        matchMedia("(prefers-reduced-motion: reduce)").matches,
        "browser_configuration",
        "Chromium did not apply the verifier's reduced-motion mode.",
      );
      check(
        matchMedia("(prefers-color-scheme: light)").matches,
        "browser_configuration",
        "Chromium did not apply the verifier's deterministic light theme.",
      );
      check(
        innerWidth === config.viewport.width && innerHeight === config.viewport.height,
        "viewport_mismatch",
        "Chromium did not render the portable artifact at the requested viewport.",
        {
          actual: { height: innerHeight, width: innerWidth },
          expected: config.viewport,
        },
      );
      if (document.fonts?.ready) {
        await Promise.race([document.fonts.ready, delay(250)]);
      }
      await delay(32);
      const root = document.querySelector(config.readerRoot);
      check(root && isVisible(root), "reader_not_visible", "Portable reader root is not visible.");
      const heading = root.querySelector("h1");
      const actualTitle = heading?.textContent?.trim() ?? "";
      check(
        actualTitle === config.title.trim(),
        "title_mismatch",
        "Rendered title does not match the embedded artifact title.",
        { actual: actualTitle, expected: config.title.trim() },
      );
      const counts = renderedCounts(root);
      check(
        sameCounts(counts, config.expectedCounts),
        "count_mismatch",
        "Rendered block counts do not match the embedded artifact.",
        { actual: counts, expected: config.expectedCounts },
      );
      const geometrySelectors = [
        "[data-analytics-layout-item]",
        ".chart-frame",
        ".table-card",
        ".report-metric-card",
      ];
      const invalidGeometry = geometrySelectors.flatMap((selector) =>
        Array.from(root.querySelectorAll(selector)).flatMap((node) => {
          const rect = node.getBoundingClientRect();
          if (rect.width > 0 && rect.height > 0) return [];
          return [{
            height: rect.height,
            id: node.getAttribute("data-layout-block-id") || node.id || node.className,
            width: rect.width,
          }];
        }),
      );
      check(
        invalidGeometry.length === 0,
        "content_not_visible",
        "One or more rendered report elements have zero width or height.",
        { invalid: invalidGeometry.slice(0, 20) },
      );
      const fallback = document.querySelector("[data-portable-fallback]");
      check(fallback, "fallback_missing", "Portable artifact has no semantic fallback root.");
      check(
        !isVisible(fallback),
        "fallback_visible",
        "Semantic fallback is still visible after the portable reader reported ready.",
      );
      await waitUntil(
        () => document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1,
        500,
      );
      const overflow = {
        clientWidth: document.documentElement.clientWidth,
        scrollWidth: document.documentElement.scrollWidth,
      };
      check(
        overflow.scrollWidth <= overflow.clientWidth + 1,
        "horizontal_overflow",
        `Portable artifact overflows horizontally at ${config.viewport.width}px.`,
        { overflow, viewport: config.viewport },
      );
      timings.contentChecksMs = Math.round((performance.now() - contentStartedAt) * 10) / 10;

      const sourceStartedAt = performance.now();
      const sourceInteraction = config.checkSource
        ? await exerciseSourceDialog(config.actionTimeoutMs)
        : "not_applicable";
      timings.sourceDialogMs = Math.round((performance.now() - sourceStartedAt) * 10) / 10;

      for (const entry of performance.getEntriesByType?.("resource") ?? []) {
        recordRequest(entry.name);
      }
      check(
        externalRequests.length === 0,
        "external_request",
        "Portable artifact attempted one or more external network requests.",
        { requests: externalRequests },
      );
      check(
        pageErrors.length === 0 && consoleErrors.length === 0,
        "browser_error",
        "Portable artifact emitted a browser error.",
        { consoleErrors, pageErrors },
      );

      send({
        counts,
        ok: true,
        sourceInteraction,
        timings: {
          ...timings,
          totalMs: Math.round((performance.now() - startedAt) * 10) / 10,
        },
      });
    } catch (error) {
      send({
        code: error?.code || "probe_failed",
        details: {
          ...(error?.details || {}),
          consoleErrors,
          externalRequests,
          pageErrors,
        },
        error: error?.message || String(error),
        ok: false,
        timings: {
          ...timings,
          totalMs: Math.round((performance.now() - startedAt) * 10) / 10,
        },
      });
    }
  }

  void run();
}

/** Runs inside the temporary top-level harness and collects both iframe probes. */
function portableVerifierHarness(encodedConfig) {
  function decode(value) {
    const binary = atob(value);
    const bytes = Uint8Array.from(binary, (character) => character.charCodeAt(0));
    return JSON.parse(new TextDecoder().decode(bytes));
  }

  function encode(value) {
    const bytes = new TextEncoder().encode(JSON.stringify(value));
    let binary = "";
    for (let index = 0; index < bytes.length; index += 8_192) {
      binary += String.fromCharCode(...bytes.subarray(index, index + 8_192));
    }
    return btoa(binary);
  }

  const config = decode(encodedConfig);
  const results = new Map();
  let completed = false;
  const frameElements = Array.from(document.querySelectorAll("iframe[data-verifier-frame]"));
  document.currentScript?.remove();

  for (const [index, frame] of frameElements.entries()) {
    const frameConfig = config.frames[index];
    if (!frameConfig) continue;
    frame.srcdoc = frameConfig.html;
  }

  function finish(result) {
    if (completed) return;
    completed = true;
    for (const frame of frameElements) frame.removeAttribute("srcdoc");
    const marker = document.createElement("meta");
    marker.id = config.resultId;
    marker.setAttribute("data-result", encode(result));
    document.head.append(marker);
    document.documentElement.dataset.portableVerifier = "complete";
  }

  addEventListener("message", (event) => {
    if (event.data?.channel !== config.channel) return;
    const result = event.data?.result;
    const name = result?.viewport?.name;
    if (!config.viewportNames.includes(name) || results.has(name)) return;
    const frameIndex = config.viewportNames.indexOf(name);
    if (frameElements[frameIndex]?.contentWindow !== event.source) return;
    results.set(name, result);
    if (results.size === config.viewportNames.length) {
      finish({
        ok: true,
        results: config.viewportNames.map((viewportName) => results.get(viewportName)),
      });
    }
  });

  setTimeout(() => {
    const missing = config.viewportNames.filter((name) => !results.has(name));
    finish({
      code: "probe_timeout",
      error: `Portable verifier probe timed out waiting for: ${missing.join(", ")}.`,
      missing,
      ok: false,
      results: config.viewportNames.flatMap((name) => results.has(name) ? [results.get(name)] : []),
    });
  }, config.timeoutMs);
}

export function injectPortableVerifierProbe(html, config) {
  const head = /<head(?:\s[^>]*)?>/i.exec(html);
  if (!head) {
    throw new PortableBrowserError(
      "html_invalid",
      "Portable HTML has no head element for verifier instrumentation.",
    );
  }
  const encodedConfig = encodeJson(config);
  const script = `<script data-portable-verifier-probe>(` +
    `${portableVerifierProbe.toString()})(${JSON.stringify(encodedConfig)});</script>`;
  const insertion = head.index + head[0].length;
  return `${html.slice(0, insertion)}\n${script}\n${html.slice(insertion)}`;
}

export function buildPortableVerifierHarness({
  channel,
  frames,
  resultId = PORTABLE_VERIFIER_RESULT_ID,
  timeoutMs,
}) {
  const config = {
    channel,
    frames: frames.map((frame) => ({ html: frame.html })),
    resultId,
    timeoutMs,
    viewportNames: frames.map((frame) => frame.viewport.name),
  };
  const encodedConfig = encodeJson(config);
  const frameMarkup = frames.map((frame) => {
    const { height, name, width } = frame.viewport;
    return `<iframe data-verifier-frame height="${height}" sandbox="allow-scripts" ` +
      `style="border:0;display:block;flex:0 0 ${width}px;height:${height}px;width:${width}px" ` +
      `title="${escapeAttribute(name)} portable verifier" width="${width}"></iframe>`;
  }).join("\n");
  return [
    "<!doctype html>",
    "<html><head><meta charset=\"utf-8\">",
    "<style>html,body{margin:0}body{display:flex;align-items:flex-start;gap:16px}</style>",
    "</head><body>",
    frameMarkup,
    `<script>(${portableVerifierHarness.toString()})(${JSON.stringify(encodedConfig)});</script>`,
    "</body></html>",
  ].join("\n");
}

export function parsePortableVerifierDump(dom) {
  const markerPattern = new RegExp(
    `<meta\\b(?=[^>]*\\bid=["']${PORTABLE_VERIFIER_RESULT_ID}["'])` +
      `(?=[^>]*\\bdata-result=["']([^"']+)["'])[^>]*>`,
    "gi",
  );
  const matches = [...dom.matchAll(markerPattern)];
  if (matches.length === 0) {
    throw new PortableBrowserError(
      "probe_missing",
      "Chromium finished without returning a portable verifier probe result.",
    );
  }
  if (matches.length !== 1) {
    throw new PortableBrowserError(
      "probe_invalid",
      "Chromium returned more than one portable verifier probe result.",
      { count: matches.length },
    );
  }
  try {
    return decodeJson(matches[0][1]);
  } catch (error) {
    throw new PortableBrowserError(
      "probe_invalid",
      `Chromium returned an unreadable portable verifier result: ${error.message}`,
    );
  }
}

export function chromiumDumpArguments({
  colorScheme = "light",
  extraArguments = [],
  height,
  profilePath,
  screenshotPath,
  url,
  virtualTimeBudgetMs,
  width,
}) {
  return [
    "--headless",
    "--no-sandbox",
    "--disable-gpu",
    "--disable-dev-shm-usage",
    "--disable-background-networking",
    "--disable-component-update",
    "--disable-default-apps",
    "--disable-domain-reliability",
    "--disable-features=Translate,OptimizationHints,MediaRouter,AutofillServerCommunication",
    "--disable-sync",
    "--metrics-recording-only",
    "--mute-audio",
    "--no-default-browser-check",
    "--no-first-run",
    `--blink-settings=preferredColorScheme=${colorScheme === "dark" ? 0 : 1}`,
    "--force-color-profile=srgb",
    "--force-prefers-reduced-motion",
    "--host-resolver-rules=MAP * ~NOTFOUND",
    "--proxy-server=http://127.0.0.1:9",
    "--proxy-bypass-list=<-loopback>",
    "--run-all-compositor-stages-before-draw",
    ...extraArguments,
    "--dump-dom",
    `--user-data-dir=${profilePath}`,
    `--virtual-time-budget=${Math.ceil(virtualTimeBudgetMs)}`,
    `--window-size=${width},${height}`,
    ...(screenshotPath ? [`--screenshot=${screenshotPath}`] : []),
    url,
  ];
}

function diagnosticTail(value) {
  return value.slice(Math.max(0, value.length - 4_000)).trim();
}

export function spawnChromiumDump({
  arguments: browserArguments,
  executablePath,
  maxDiagnosticBytes = MAX_BROWSER_DIAGNOSTIC_BYTES,
  maxOutputBytes = MAX_BROWSER_OUTPUT_BYTES,
  spawnImpl = spawn,
  timeoutMs,
}) {
  return new Promise((resolve, reject) => {
    let settled = false;
    let stderr = "";
    let stdout = "";
    let stdoutBytes = 0;
    let terminationError;
    let terminationTimer;
    let timer;
    let child;
    try {
      child = spawnImpl(executablePath, browserArguments, {
        stdio: ["ignore", "pipe", "pipe"],
      });
    } catch (error) {
      reject(new PortableBrowserError(
        "browser_launch_failed",
        `Could not start Chromium: ${error.message}`,
        { executablePath },
      ));
      return;
    }
    child.stdout.setEncoding("utf8");
    child.stderr.setEncoding("utf8");

    function finish(error, result) {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      clearTimeout(terminationTimer);
      if (error) reject(error);
      else resolve(result);
    }

    function terminate(error) {
      if (settled || terminationError) return;
      terminationError = error;
      clearTimeout(timer);
      child.kill("SIGKILL");
      // Wait for close so temporary Chromium profiles are not still locked on
      // Windows. The bounded fallback preserves the original failure if a
      // platform never reports close after termination.
      terminationTimer = setTimeout(() => finish(error), 1_000);
    }

    child.stdout.on("data", (chunk) => {
      stdoutBytes += Buffer.byteLength(chunk, "utf8");
      if (stdoutBytes > maxOutputBytes) {
        terminate(new PortableBrowserError(
          "browser_output_limit",
          "Chromium stdout exceeded the verifier output limit.",
          { limit: maxOutputBytes },
        ));
        return;
      }
      stdout += chunk;
    });
    child.stderr.on("data", (chunk) => {
      const next = Buffer.from(stderr + chunk, "utf8");
      stderr = next.subarray(Math.max(0, next.byteLength - maxDiagnosticBytes)).toString("utf8");
    });
    child.on("error", (error) => finish(new PortableBrowserError(
      "browser_launch_failed",
      `Could not start Chromium: ${error.message}`,
      { executablePath },
    )));
    child.on("close", (code, signal) => {
      if (terminationError) {
        finish(terminationError);
        return;
      }
      if (code !== 0) {
        finish(new PortableBrowserError(
          "browser_failed",
          `Chromium exited before verification completed (code ${code ?? "none"}).`,
          { code, diagnostics: diagnosticTail(stderr), signal },
        ));
        return;
      }
      finish(null, { stderr, stdout });
    });

    timer = setTimeout(() => {
      terminate(new PortableBrowserError(
        "browser_timeout",
        `Chromium did not finish within ${timeoutMs}ms.`,
        { timeoutMs },
      ));
    }, timeoutMs);
  });
}
