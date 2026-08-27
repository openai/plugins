import { randomUUID } from "node:crypto";
import {
  mkdtempSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";

import {
  PortableBrowserError,
  resolveChromiumExecutable,
} from "./portable_browser_helpers.mjs";
import {
  chromiumDumpArguments,
  spawnChromiumDump,
} from "./portable_browser_cli.mjs";

const READER_ROOT = "#data-analytics-portable-reader";
const CHART_CARD = `${READER_ROOT} section[data-artifact-kind="chart"][data-artifact-id]`;
const CHART_SURFACE = ".chart-plot svg.recharts-surface";
const EXTRACTION_VIEWPORT = Object.freeze({ width: 1_200, height: 900 });
const EXTRACTION_RESULT_ATTRIBUTE = "data-portable-chart-extraction";
const EXTRACTION_TERMINAL_STATES = Object.freeze([
  "ready",
  "failed",
  "missing-runtime",
  "unsupported",
]);
const MAX_BROWSER_OUTPUT_BYTES = 16_000_000;
const MIN_BROWSER_OUTPUT_BYTES = 4_000_000;
const MAX_BROWSER_DIAGNOSTIC_BYTES = 64_000;
const MAX_RUNTIME_DIAGNOSTICS = 100;
const MAX_RUNTIME_DIAGNOSTIC_LENGTH = 2_000;
const SETTLE_FRAME_COUNT = 60;
const SETTLE_FRAME_MS = 16;

const SVG_ELEMENT_NAMES = Object.freeze({
  circle: "circle",
  clippath: "clipPath",
  defs: "defs",
  ellipse: "ellipse",
  g: "g",
  lineargradient: "linearGradient",
  line: "line",
  path: "path",
  polygon: "polygon",
  polyline: "polyline",
  radialgradient: "radialGradient",
  rect: "rect",
  stop: "stop",
  svg: "svg",
  text: "text",
  tspan: "tspan",
});

const PRESENTATION_ATTRIBUTES = Object.freeze([
  "clip-path",
  "clip-rule",
  "fill",
  "fill-opacity",
  "fill-rule",
  "opacity",
  "paint-order",
  "shape-rendering",
  "stroke",
  "stroke-dasharray",
  "stroke-dashoffset",
  "stroke-linecap",
  "stroke-linejoin",
  "stroke-miterlimit",
  "stroke-opacity",
  "stroke-width",
  "vector-effect",
]);

const TEXT_ATTRIBUTES = Object.freeze([
  ...PRESENTATION_ATTRIBUTES,
  "alignment-baseline",
  "baseline-shift",
  "dominant-baseline",
  "font-family",
  "font-size",
  "font-style",
  "font-variant",
  "font-variant-numeric",
  "font-weight",
  "letter-spacing",
  "text-anchor",
  "word-spacing",
]);

const SVG_ATTRIBUTES_BY_ELEMENT = Object.freeze({
  circle: ["id", "cx", "cy", "r", "transform", ...PRESENTATION_ATTRIBUTES],
  clippath: ["id", "clippathunits", "transform"],
  defs: ["id"],
  ellipse: ["id", "cx", "cy", "rx", "ry", "transform", ...PRESENTATION_ATTRIBUTES],
  g: ["id", "transform", ...PRESENTATION_ATTRIBUTES],
  lineargradient: [
    "id", "x1", "y1", "x2", "y2", "gradientunits", "gradienttransform", "spreadmethod",
  ],
  line: ["id", "x1", "y1", "x2", "y2", "transform", ...PRESENTATION_ATTRIBUTES],
  path: ["id", "d", "pathlength", "transform", ...PRESENTATION_ATTRIBUTES],
  polygon: ["id", "points", "pathlength", "transform", ...PRESENTATION_ATTRIBUTES],
  polyline: ["id", "points", "pathlength", "transform", ...PRESENTATION_ATTRIBUTES],
  radialgradient: [
    "id", "cx", "cy", "r", "fx", "fy", "fr", "gradientunits", "gradienttransform", "spreadmethod",
  ],
  rect: ["id", "x", "y", "width", "height", "rx", "ry", "transform", ...PRESENTATION_ATTRIBUTES],
  stop: ["id", "offset", "stop-color", "stop-opacity"],
  svg: ["id", "viewbox", "x", "y", "width", "height", "preserveaspectratio"],
  text: [
    "id", "x", "y", "dx", "dy", "rotate", "textlength", "lengthadjust", "transform", ...TEXT_ATTRIBUTES,
  ],
  tspan: [
    "id", "x", "y", "dx", "dy", "rotate", "textlength", "lengthadjust", "transform", ...TEXT_ATTRIBUTES,
  ],
});

const SVG_ATTRIBUTE_OUTPUT_NAMES = Object.freeze({
  clippathunits: "clipPathUnits",
  gradienttransform: "gradientTransform",
  gradientunits: "gradientUnits",
  lengthadjust: "lengthAdjust",
  pathlength: "pathLength",
  preserveaspectratio: "preserveAspectRatio",
  spreadmethod: "spreadMethod",
  textlength: "textLength",
  viewbox: "viewBox",
});

const EXTRACTION_LIMITS = Object.freeze({
  attributeLength: 262_144,
  attributesPerElement: 64,
  chartCount: 200,
  dimension: 10_000,
  idLength: 256,
  legendItems: 100,
  legendTextLength: 500,
  markupBytes: 150_000,
  svgElements: 2_500,
  textLength: 100_000,
  totalMarkupBytes: 750_000,
});

async function settleRenderedChartsInBrowser(chartCardSelector, frameCount, frameMs) {
    await document.fonts?.ready;
    let previous = "";
    let stableFrames = 0;
    for (let frameIndex = 0; frameIndex < frameCount; frameIndex += 1) {
      const geometry = Array.from(document.querySelectorAll(chartCardSelector)).flatMap((card) => {
        const frame = card.querySelector(".chart-frame");
        if (!(frame instanceof HTMLElement)) return [];
        const frameBox = frame.getBoundingClientRect();
        const surface = frame.querySelector(".chart-plot svg.recharts-surface");
        const surfaceBox = surface?.getBoundingClientRect();
        return [[
          Math.round(frameBox.width),
          Math.round(frameBox.height),
          Math.round(surfaceBox?.width ?? frameBox.width),
          Math.round(surfaceBox?.height ?? frameBox.height),
        ]];
      });
      const ready = geometry.every(([frameWidth, frameHeight, surfaceWidth, surfaceHeight]) =>
        frameWidth > 1 && frameHeight > 1 && surfaceWidth > 1 && surfaceHeight > 1);
      const current = ready ? JSON.stringify(geometry) : "";
      stableFrames = current && current === previous ? stableFrames + 1 : 0;
      if (stableFrames >= 2) return;
      previous = current;
      await new Promise((resolveFrame) => setTimeout(resolveFrame, frameMs));
    }
    throw new Error("Portable chart geometry did not settle before SVG extraction.");
}

function extractChartVariantInBrowser(node, options) {
    try {
      const surfaces = node.querySelectorAll(options.surfaceSelector);
      if (surfaces.length !== 1 || !(surfaces[0] instanceof SVGSVGElement)) return null;
      const sourceSvg = surfaces[0];
      const sourceElements = [sourceSvg, ...sourceSvg.querySelectorAll("*")];
      if (sourceElements.length > options.limits.svgElements) return null;
      if (!/^[A-Za-z][A-Za-z0-9_-]{0,80}$/.test(options.prefix)) return null;

      const sourceBox = sourceSvg.getBoundingClientRect();
      const width = Math.round(sourceBox.width);
      const height = Math.round(sourceBox.height);
      if (
        width < 1 ||
        height < 1 ||
        width > options.limits.dimension ||
        height > options.limits.dimension
      ) return null;

      let invalid = false;
      let totalTextLength = 0;
      const ignoredElements = new Set(["desc", "title"]);
      const idReplacements = new Map();
      for (const source of sourceElements) {
        const tagName = source.tagName.toLowerCase();
        if (ignoredElements.has(tagName)) continue;
        if (!options.elementNames[tagName]) return null;
        if (source.attributes.length > options.limits.attributesPerElement) return null;
        const id = source.getAttribute("id");
        if (!id) continue;
        if (
          id.length > options.limits.idLength ||
          /[\u0000-\u001f\u007f\s"'<>]/.test(id) ||
          idReplacements.has(id)
        ) return null;
        idReplacements.set(id, `${options.prefix}-${idReplacements.size}`);
      }

      function safeValue(value) {
        return Boolean(
          value &&
          value.length <= options.limits.attributeLength &&
          !/[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f<>]/.test(value) &&
          !/(?:javascript|data|blob|file|https?):/i.test(value) &&
          !/(?:expression|var)\s*\(/i.test(value) &&
          !/@import/i.test(value)
        );
      }

      function safeAttributeValue(value) {
        const trimmed = String(value ?? "").trim();
        if (!safeValue(trimmed)) return null;
        if (!/url\s*\(/i.test(trimmed)) return trimmed;
        const reference = /^url\(\s*(["']?)#([^\s"'()]+)\1\s*\)$/i.exec(trimmed);
        if (!reference) return null;
        const replacement = idReplacements.get(reference[2]);
        return replacement ? `url(#${replacement})` : null;
      }

      const presentationElements = new Set([
        "circle", "ellipse", "line", "path", "polygon", "polyline", "rect",
      ]);
      const textElements = new Set(["text", "tspan"]);
      const namespace = "http://www.w3.org/2000/svg";

      function buildSafeElement(source) {
        const tagName = source.tagName.toLowerCase();
        if (ignoredElements.has(tagName)) return null;
        const outputTagName = options.elementNames[tagName];
        const allowedAttributes = new Set(options.attributesByElement[tagName] ?? []);
        if (!outputTagName || !allowedAttributes.size) {
          invalid = true;
          return null;
        }

        const target = document.createElementNS(namespace, outputTagName);
        const replacementId = idReplacements.get(source.getAttribute("id"));
        if (replacementId) target.setAttribute("id", replacementId);

        for (const attribute of source.attributes) {
          const lowerName = attribute.name.toLowerCase();
          if (lowerName === "id" || !allowedAttributes.has(lowerName)) continue;
          const resolvedFromComputed =
            options.presentationAttributes.includes(lowerName) ||
            options.textAttributes.includes(lowerName) ||
            lowerName === "stop-color" ||
            lowerName === "stop-opacity";
          if (resolvedFromComputed && !/url\s*\(/i.test(attribute.value)) continue;
          const value = safeAttributeValue(attribute.value);
          if (value == null) {
            invalid = true;
            return null;
          }
          target.setAttribute(options.attributeOutputNames[lowerName] ?? lowerName, value);
        }

        const computed = getComputedStyle(source);
        const computedProperties = textElements.has(tagName)
          ? options.textAttributes
          : presentationElements.has(tagName)
            ? options.presentationAttributes
            : tagName === "stop"
              ? ["stop-color", "stop-opacity"]
              : tagName === "g"
                ? ["opacity"]
                : [];
        for (const property of computedProperties) {
          if (!allowedAttributes.has(property)) continue;
          const original = source.getAttribute(property);
          const rawValue = original && /url\s*\(/i.test(original)
            ? original
            : computed.getPropertyValue(property).trim();
          if (!rawValue) continue;
          const value = safeAttributeValue(rawValue);
          if (value == null) {
            invalid = true;
            return null;
          }
          target.setAttribute(options.attributeOutputNames[property] ?? property, value);
        }

        for (const child of source.childNodes) {
          if (child.nodeType === Node.ELEMENT_NODE) {
            const childTagName = child.tagName.toLowerCase();
            if (ignoredElements.has(childTagName)) continue;
            const safeChild = buildSafeElement(child);
            if (invalid || !safeChild) return null;
            target.append(safeChild);
          } else if (child.nodeType === Node.TEXT_NODE) {
            const text = child.textContent ?? "";
            if (!textElements.has(tagName) && !/^\s*$/.test(text)) {
              invalid = true;
              return null;
            }
            if (!textElements.has(tagName)) continue;
            totalTextLength += text.length;
            if (totalTextLength > options.limits.textLength) {
              invalid = true;
              return null;
            }
            target.append(document.createTextNode(text));
          }
        }
        return target;
      }

      const clone = buildSafeElement(sourceSvg);
      if (invalid || !(clone instanceof SVGSVGElement)) return null;

      const sourceViewBox = sourceSvg.getAttribute("viewBox");
      const viewBoxParts = sourceViewBox?.replaceAll(",", " ").trim().split(/\s+/).map(Number);
      const validViewBox = viewBoxParts?.length === 4 &&
        viewBoxParts.every(Number.isFinite) &&
        viewBoxParts[2] > 0 &&
        viewBoxParts[3] > 0 &&
        viewBoxParts[2] <= options.limits.dimension &&
        viewBoxParts[3] <= options.limits.dimension;
      clone.setAttribute("xmlns", namespace);
      clone.setAttribute("aria-hidden", "true");
      clone.setAttribute("class", "portable-static-chart-svg");
      clone.setAttribute("focusable", "false");
      clone.setAttribute("height", String(height));
      clone.setAttribute("preserveAspectRatio", "xMidYMid meet");
      clone.setAttribute("viewBox", validViewBox ? viewBoxParts.join(" ") : `0 0 ${width} ${height}`);
      clone.setAttribute("width", String(width));

      const outputIds = new Set();
      for (const element of [clone, ...clone.querySelectorAll("*")]) {
        const id = element.getAttribute("id");
        if (id && outputIds.has(id)) return null;
        if (id) outputIds.add(id);
      }
      for (const element of [clone, ...clone.querySelectorAll("*")]) {
        for (const attribute of element.attributes) {
          const value = attribute.value;
          if (attribute.name === "xmlns" && value === namespace) continue;
          if (!safeValue(value)) return null;
          if (!/url\s*\(/i.test(value)) continue;
          const reference = /^url\(#([^\s"'()]+)\)$/i.exec(value);
          if (!reference || !outputIds.has(reference[1])) return null;
        }
      }

      const legendWrap = node.querySelector(".chart-frame > .chart-legend-wrap");
      const legendItems = legendWrap
        ? Array.from(legendWrap.querySelectorAll(":scope > .chart-legend > .chart-legend-item"))
        : [];
      if (legendItems.length > options.limits.legendItems) return null;
      const legend = {
        items: [],
        position: legendWrap?.classList.contains("chart-legend-wrap--right") ? "right" : "bottom",
        title: null,
      };
      function safeLegendText(value) {
        return Boolean(
          value &&
          value.length <= options.limits.legendTextLength &&
          !/[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/.test(value)
        );
      }
      const legendTitle = legendWrap?.querySelector(":scope > .chart-legend-title")?.textContent?.trim();
      if (legendTitle) {
        if (!safeLegendText(legendTitle)) return null;
        legend.title = legendTitle;
      }
      for (const item of legendItems) {
        const label = item.textContent?.trim();
        if (!safeLegendText(label)) return null;
        const line = item.querySelector(".chart-legend-line line");
        const dot = item.querySelector(".chart-legend-dot");
        let color;
        let dasharray;
        let marker;
        if (line instanceof SVGElement) {
          const computed = getComputedStyle(line);
          color = computed.stroke;
          const computedDasharray = computed.strokeDasharray;
          dasharray = computedDasharray && computedDasharray !== "none" ? computedDasharray : undefined;
          marker = "line";
        } else if (dot instanceof HTMLElement) {
          color = getComputedStyle(dot).backgroundColor;
          marker = "dot";
        } else {
          return null;
        }
        if (!safeValue(color) || (dasharray && !safeValue(dasharray))) return null;
        legend.items.push({
          color,
          label,
          marker,
          ...(dasharray ? { dasharray } : {}),
        });
      }

      const svg = clone.outerHTML.replaceAll("><", ">\n<");
      if (new TextEncoder().encode(svg).byteLength > options.limits.markupBytes) return null;
      return { height, legend, svg, width };
    } catch {
      return null;
    }
}

/** Runs inside the instrumented artifact. Keep it self-contained and serializable. */
function portableChartExtractionProbe(encodedConfig) {
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
  const externalRequests = [];
  const externalRequestSet = new Set();
  const pageErrors = [];
  let externalRequestOverflow = false;

  function compact(value) {
    if (value instanceof Error) return value.stack || value.message;
    if (typeof value === "string") return value;
    try {
      return JSON.stringify(value);
    } catch {
      return String(value);
    }
  }

  function appendDiagnostic(value) {
    if (pageErrors.length >= config.maxRuntimeDiagnostics) return;
    pageErrors.push(compact(value).slice(0, config.maxRuntimeDiagnosticLength));
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
    if (!url || externalRequestSet.has(url)) return;
    if (externalRequests.length >= config.maxRuntimeDiagnostics) {
      externalRequestOverflow = true;
      return;
    }
    externalRequestSet.add(url);
    externalRequests.push(url);
  }

  addEventListener("error", (event) => {
    if (event.error || event.message) appendDiagnostic(event.error || event.message);
  });
  addEventListener("unhandledrejection", (event) => appendDiagnostic(event.reason));

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
      globalThis[constructorName] = new Proxy(Original, {
        construct(target, argumentsList) {
          recordRequest(argumentsList[0]);
          return Reflect.construct(target, argumentsList);
        },
      });
    }
    if (typeof PerformanceObserver === "function") {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) recordRequest(entry.name);
      });
      observer.observe({ type: "resource", buffered: true });
    }
  } catch (error) {
    appendDiagnostic(`Extraction instrumentation failed: ${compact(error)}`);
  }

  function delay(milliseconds) {
    return new Promise((resolveDelay) => setTimeout(resolveDelay, milliseconds));
  }

  function finish(result) {
    const marker = document.createElement("meta");
    marker.setAttribute(config.resultAttribute, config.resultToken);
    marker.setAttribute("data-result", encode(result));
    document.head.append(marker);
  }

  async function run() {
    try {
      const environment = {
        height: innerHeight,
        prefersDark: matchMedia("(prefers-color-scheme: dark)").matches,
        reducedMotion: matchMedia("(prefers-reduced-motion: reduce)").matches,
        width: innerWidth,
      };
      if (
        environment.width !== config.viewport.width ||
        environment.height !== config.viewport.height ||
        environment.prefersDark !== (config.colorScheme === "dark") ||
        !environment.reducedMotion
      ) {
        const error = new Error("Chromium did not apply the requested chart extraction environment.");
        error.code = "browser_environment_mismatch";
        error.details = environment;
        throw error;
      }

      const terminalStates = new Set(config.terminalStates);
      const deadline = performance.now() + config.readyTimeoutMs;
      let readerState = "";
      do {
        readerState = document.documentElement.dataset.dataAnalyticsPortableReader ?? "";
        if (terminalStates.has(readerState)) break;
        await delay(16);
      } while (performance.now() < deadline);

      if (!terminalStates.has(readerState)) {
        const error = new Error(
          `Portable reader did not reach a terminal state within ${config.readyTimeoutMs}ms ` +
            `(state: ${readerState || "unset"}).`,
        );
        error.code = "reader_timeout";
        throw error;
      }
      if (readerState !== "ready") {
        const error = new Error(`Portable reader entered terminal failure state: ${readerState}.`);
        error.code = `reader_${readerState}`;
        throw error;
      }

      await settleRenderedChartsInBrowser(
        config.chartCardSelector,
        config.settleFrameCount,
        config.settleFrameMs,
      );

      const cards = Array.from(document.querySelectorAll(config.chartCardSelector));
      if (cards.length > config.limits.chartCount) {
        const error = new Error(
          `Portable SVG extraction supports at most ${config.limits.chartCount} charts.`,
        );
        error.code = "chart_limit";
        throw error;
      }

      const charts = [];
      let serializedVariantBytes = 0;
      for (let index = 0; index < cards.length; index += 1) {
        const card = cards[index];
        const identity = {
          blockId: card.closest("[data-artifact-block-id]")?.getAttribute("data-artifact-block-id"),
          chartId: card.getAttribute("data-artifact-id"),
        };
        const chartKey = identity.blockId || identity.chartId;
        if (
          typeof identity.chartId !== "string" ||
          !identity.chartId ||
          identity.chartId.length > config.limits.idLength ||
          typeof chartKey !== "string" ||
          !chartKey ||
          chartKey.length > config.limits.idLength
        ) continue;

        let variant = extractChartVariantInBrowser(card, {
          attributeOutputNames: config.attributeOutputNames,
          attributesByElement: config.attributesByElement,
          elementNames: config.elementNames,
          limits: config.limits,
          prefix: `portable-${index}-${config.colorScheme}`,
          presentationAttributes: config.presentationAttributes,
          surfaceSelector: config.chartSurfaceSelector,
          textAttributes: config.textAttributes,
        });
        if (variant) {
          const variantBytes = new TextEncoder().encode(JSON.stringify(variant)).byteLength;
          if (serializedVariantBytes + variantBytes > config.limits.totalMarkupBytes) {
            variant = null;
          } else {
            serializedVariantBytes += variantBytes;
          }
        }
        charts.push({
          chartId: identity.chartId,
          chartKey,
          variant,
        });
      }

      for (const entry of performance.getEntriesByType?.("resource") ?? []) {
        recordRequest(entry.name);
      }
      await delay(32);
      finish({
        charts,
        externalRequestOverflow,
        externalRequests,
        environment,
        ok: true,
        pageErrors,
      });
    } catch (error) {
      finish({
        code: error?.code ?? "chart_extraction_failed",
        error: compact(error),
        externalRequestOverflow,
        externalRequests,
        ok: false,
        pageErrors,
      });
    }
  }

  void run();
}

function encodeJson(value) {
  return Buffer.from(JSON.stringify(value), "utf8").toString("base64");
}

function decodeJson(value) {
  return JSON.parse(Buffer.from(value, "base64").toString("utf8"));
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

export function injectPortableChartExtractionProbe(html, config) {
  const head = /<head(?:\s[^>]*)?>/i.exec(html);
  if (!head) {
    throw new PortableBrowserError(
      "html_invalid",
      "Portable HTML has no head element for chart extraction instrumentation.",
    );
  }
  const encodedConfig = encodeJson(config);
  const scriptBody = [
    "(() => {",
    `const settleRenderedChartsInBrowser = ${settleRenderedChartsInBrowser.toString()};`,
    `const extractChartVariantInBrowser = ${extractChartVariantInBrowser.toString()};`,
    `(${portableChartExtractionProbe.toString()})(${JSON.stringify(encodedConfig)});`,
    "})();",
  ].join("\n").replaceAll("</script", "<\\/script");
  const script = `<script data-portable-chart-extraction-probe>${scriptBody}</script>`;
  const insertion = head.index + head[0].length;
  return `${html.slice(0, insertion)}\n${script}\n${html.slice(insertion)}`;
}

export function parsePortableChartExtractionDump(dom, resultToken) {
  const markerPattern = new RegExp(
    `<meta\\b(?=[^>]*\\b${EXTRACTION_RESULT_ATTRIBUTE}=["']${escapeRegExp(resultToken)}["'])` +
      `(?=[^>]*\\bdata-result=["']([^"']+)["'])[^>]*>`,
    "gi",
  );
  const matches = [...dom.matchAll(markerPattern)];
  if (matches.length === 0) {
    throw new PortableBrowserError(
      "probe_missing",
      "Chromium finished without returning a portable chart extraction result.",
    );
  }
  if (matches.length !== 1) {
    throw new PortableBrowserError(
      "probe_invalid",
      "Chromium returned more than one portable chart extraction result.",
      { count: matches.length },
    );
  }
  try {
    return decodeJson(matches[0][1]);
  } catch (error) {
    throw new PortableBrowserError(
      "probe_invalid",
      `Chromium returned an unreadable portable chart extraction result: ${error.message}`,
    );
  }
}

function extractionProbeConfig({ colorScheme, readyTimeoutMs, resultToken }) {
  return {
    attributeOutputNames: SVG_ATTRIBUTE_OUTPUT_NAMES,
    attributesByElement: SVG_ATTRIBUTES_BY_ELEMENT,
    chartCardSelector: CHART_CARD,
    chartSurfaceSelector: CHART_SURFACE,
    colorScheme,
    elementNames: SVG_ELEMENT_NAMES,
    limits: EXTRACTION_LIMITS,
    maxRuntimeDiagnosticLength: MAX_RUNTIME_DIAGNOSTIC_LENGTH,
    maxRuntimeDiagnostics: MAX_RUNTIME_DIAGNOSTICS,
    presentationAttributes: PRESENTATION_ATTRIBUTES,
    readyTimeoutMs,
    resultAttribute: EXTRACTION_RESULT_ATTRIBUTE,
    resultToken,
    settleFrameCount: SETTLE_FRAME_COUNT,
    settleFrameMs: SETTLE_FRAME_MS,
    terminalStates: EXTRACTION_TERMINAL_STATES,
    textAttributes: TEXT_ATTRIBUTES,
    viewport: EXTRACTION_VIEWPORT,
  };
}

async function extractColorScheme({
  actionTimeoutMs,
  browserExecutable,
  colorScheme,
  directory,
  html,
  maxOutputBytes,
  readyTimeoutMs,
  runDump,
}) {
  const resultToken = randomUUID();
  const probePath = join(directory, `portable-${colorScheme}.html`);
  const profilePath = join(directory, `profile-${colorScheme}`);
  const probe = injectPortableChartExtractionProbe(
    html,
    extractionProbeConfig({ colorScheme, readyTimeoutMs, resultToken }),
  );
  writeFileSync(probePath, probe, "utf8");

  const settleBudgetMs = SETTLE_FRAME_COUNT * SETTLE_FRAME_MS;
  const virtualTimeBudgetMs = readyTimeoutMs + settleBudgetMs + 750;
  const browserArguments = chromiumDumpArguments({
    colorScheme,
    height: EXTRACTION_VIEWPORT.height,
    profilePath,
    url: pathToFileURL(probePath).href,
    virtualTimeBudgetMs,
    width: EXTRACTION_VIEWPORT.width,
  });
  const { stdout } = await runDump({
    arguments: browserArguments,
    executablePath: browserExecutable,
    maxDiagnosticBytes: MAX_BROWSER_DIAGNOSTIC_BYTES,
    maxOutputBytes,
    timeoutMs: actionTimeoutMs + virtualTimeBudgetMs + 2_000,
  });
  const result = parsePortableChartExtractionDump(stdout, resultToken);
  if (!result?.ok) {
    throw new PortableBrowserError(
      result?.code ?? "chart_extraction_failed",
      result?.error ?? "Portable chart extraction failed.",
      { pageErrors: result?.pageErrors ?? [] },
    );
  }
  if (result.externalRequestOverflow) {
    throw new PortableBrowserError(
      "network_request_limit",
      "Portable SVG extraction exceeded the external request diagnostic limit.",
    );
  }
  if (result.pageErrors?.length) {
    throw new PortableBrowserError(
      "browser_page_error",
      "Portable SVG extraction encountered a browser page error.",
      { pageErrors: result.pageErrors },
    );
  }
  return result;
}

/**
 * Extract sanitized, theme-resolved inline SVG from the shared reader. Charts
 * without a Recharts SVG retain the semantic data table fallback.
 */
export async function extractPortableChartSvgs({
  actionTimeoutMs = 2_500,
  browserExecutable,
  htmlPath,
  readyTimeoutMs = 5_000,
  runDump = spawnChromiumDump,
} = {}) {
  if (!htmlPath) throw new Error("htmlPath is required.");

  const absoluteHtmlPath = resolve(htmlPath);
  const html = readFileSync(absoluteHtmlPath, "utf8");
  const executablePath = browserExecutable ?? resolveChromiumExecutable();
  const directory = mkdtempSync(join(tmpdir(), "data-analytics-portable-chart-extraction-"));
  const externalRequests = new Set();
  const staticCharts = new Map();
  const invalidChartKeys = new Set();
  const inputBytes = Buffer.byteLength(html, "utf8");
  const maxOutputBytes = Math.min(
    MAX_BROWSER_OUTPUT_BYTES,
    Math.max(
      MIN_BROWSER_OUTPUT_BYTES,
      inputBytes * 2 + Math.ceil(EXTRACTION_LIMITS.totalMarkupBytes * 4 / 3) + 1_000_000,
    ),
  );

  try {
    for (const colorScheme of ["light", "dark"]) {
      const result = await extractColorScheme({
        actionTimeoutMs,
        browserExecutable: executablePath,
        colorScheme,
        directory,
        html,
        maxOutputBytes,
        readyTimeoutMs,
        runDump,
      });
      for (const request of result.externalRequests ?? []) externalRequests.add(request);
      for (const { chartId, chartKey, variant } of result.charts ?? []) {
        if (
          invalidChartKeys.has(chartKey) ||
          staticCharts.get(chartKey)?.[colorScheme]
        ) continue;
        if (!variant) {
          staticCharts.delete(chartKey);
          invalidChartKeys.add(chartKey);
          continue;
        }

        const currentStaticChart = staticCharts.get(chartKey);
        if (
          currentStaticChart &&
          (currentStaticChart.chartId !== chartId ||
            Math.abs(currentStaticChart.width - variant.width) > 1 ||
            Math.abs(currentStaticChart.height - variant.height) > 1)
        ) {
          staticCharts.delete(chartKey);
          invalidChartKeys.add(chartKey);
          continue;
        }
        staticCharts.set(chartKey, {
          ...(currentStaticChart ?? {
            chartId,
            height: variant.height,
            width: variant.width,
          }),
          [colorScheme]: {
            legend: variant.legend,
            svg: variant.svg,
          },
        });
      }
    }

    if (externalRequests.size) {
      throw new Error(`Portable SVG extraction attempted network requests:\n${[...externalRequests].join("\n")}`);
    }

    let totalMarkupBytes = 0;
    for (const [chartKey, staticChart] of staticCharts) {
      if (!staticChart.light?.svg || !staticChart.dark?.svg) {
        staticCharts.delete(chartKey);
        continue;
      }
      const chartBytes = Buffer.byteLength(JSON.stringify(staticChart.light), "utf8") +
        Buffer.byteLength(JSON.stringify(staticChart.dark), "utf8");
      if (totalMarkupBytes + chartBytes > EXTRACTION_LIMITS.totalMarkupBytes) {
        staticCharts.delete(chartKey);
        continue;
      }
      totalMarkupBytes += chartBytes;
    }
    return Object.fromEntries(staticCharts);
  } finally {
    try {
      rmSync(directory, { force: true, maxRetries: 3, recursive: true, retryDelay: 100 });
    } catch {
      // Preserve extraction or browser capability failures if an OS briefly
      // retains a lock on the disposable Chromium profile.
    }
  }
}
