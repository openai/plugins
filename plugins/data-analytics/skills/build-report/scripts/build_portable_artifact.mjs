#!/usr/bin/env node

import {
  mkdirSync,
  readFileSync,
  readdirSync,
  writeFileSync,
} from "node:fs";
import { createRequire } from "node:module";
import { dirname, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { gunzipSync, gzipSync } from "node:zlib";

const require = createRequire(import.meta.url);
const scriptDirectory = dirname(fileURLToPath(import.meta.url));
const pluginRoot = resolve(scriptDirectory, "../../..");
const assetDirectory = resolve(pluginRoot, "assets");
const server = require(resolve(pluginRoot, "mcp/server.cjs"));

export const READER_ASSET = "portable-artifact-reader.html";
export const PAYLOAD_SOURCE_ID = "data-analytics-portable-artifact-payload-source";
export const RUNTIME_SOURCE_ID = "data-analytics-portable-reader-runtime-source";
export const PAYLOAD_GLOBAL = "__DATA_ANALYTICS_PORTABLE_ARTIFACT__";
export const READER_ROOT_ID = "data-analytics-portable-reader";
export const FALLBACK_ROOT_ID = "data-analytics-portable-fallback";
export const READER_READY_EVENT = "data-analytics-portable-reader-ready";

const MAX_CHART_SUMMARY_ROWS = 50;
const MAX_STATIC_CHART_BYTES = 150_000;
const MAX_STATIC_CHART_ENTRIES = 200;
const MAX_STATIC_CHART_ELEMENTS = 2_500;
const MAX_STATIC_CHART_TOTAL_BYTES = 750_000;
const STATIC_SVG_NAMESPACE = "http://www.w3.org/2000/svg";
const STATIC_SVG_ELEMENTS = new Set([
  "circle",
  "clippath",
  "defs",
  "ellipse",
  "g",
  "lineargradient",
  "line",
  "path",
  "polygon",
  "polyline",
  "radialgradient",
  "rect",
  "stop",
  "svg",
  "text",
  "tspan",
]);
const STATIC_SVG_ATTRIBUTES = new Set([
  "alignment-baseline",
  "baseline-shift",
  "aria-hidden",
  "class",
  "clip-path",
  "clip-rule",
  "clippathunits",
  "cx",
  "cy",
  "d",
  "dominant-baseline",
  "dx",
  "dy",
  "fill",
  "fill-opacity",
  "fill-rule",
  "focusable",
  "font-family",
  "font-size",
  "font-style",
  "font-variant",
  "font-variant-numeric",
  "font-weight",
  "fr",
  "fx",
  "fy",
  "gradienttransform",
  "gradientunits",
  "height",
  "id",
  "letter-spacing",
  "lengthadjust",
  "offset",
  "opacity",
  "paint-order",
  "pathlength",
  "points",
  "preserveaspectratio",
  "r",
  "rx",
  "ry",
  "rotate",
  "shape-rendering",
  "stop-color",
  "stop-opacity",
  "spreadmethod",
  "stroke",
  "stroke-dasharray",
  "stroke-dashoffset",
  "stroke-linecap",
  "stroke-linejoin",
  "stroke-miterlimit",
  "stroke-opacity",
  "stroke-width",
  "text-anchor",
  "textlength",
  "transform",
  "vector-effect",
  "viewbox",
  "width",
  "word-spacing",
  "x",
  "x1",
  "x2",
  "xmlns",
  "y",
  "y1",
  "y2",
]);

const PORTABLE_CREDENTIAL_ASSIGNMENT_PATTERN = /\b(?:password|passwd|pwd|secret|api[-_]?key|access[-_]?token|refresh[-_]?token|token|authorization|cookie|private[-_]?key|credential)\b\s*(?:=|:|=>)\s*(?:"[^"]+"|'[^']+'|[^\s,;)]+)/iu;
const PORTABLE_SECRET_TOKEN_PATTERN = /\b(?:AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{16,}|eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,})\b/u;
const PORTABLE_LOCAL_PATH_PATTERN = /(?:^|[\s"'`(=])(?:file:\/\/|\/(?:[^/\s]+\/)+|[A-Za-z]:[\\/]|\\\\[^\\/\s]+[\\/]|~[\\/])/iu;
const PORTABLE_PARENT_PATH_PATTERN = /(?:^|[\\/\s"'`(=])\.\.(?:[\\/]|$)/u;
const PORTABLE_CREDENTIAL_FIELD_PATTERN = /^(?:password|passwd|pwd|secret|api[-_]?key|access[-_]?token|refresh[-_]?token|token|authorization|cookie|private[-_]?key|credential)$/iu;
const PORTABLE_SENSITIVE_URL_PARAMETER_PATTERN = /^(?:password|passwd|pwd|secret|api[-_]?key|access[-_]?token|refresh[-_]?token|token|authorization|cookie|private[-_]?key|credential|sig|signature|x-amz-credential|x-amz-security-token|x-amz-signature|x-goog-credential|x-goog-signature)$/iu;

const READ_ONLY_CONTROLS = Object.freeze({
  copyAsImage: false,
  delete: false,
  drag: false,
  edit: false,
  export: false,
  exportHostedLink: false,
  fullscreen: false,
  hostedLink: false,
  persistence: false,
  refresh: false,
  reorder: false,
  share: false,
});

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function asObject(value) {
  return value && typeof value === "object" && !Array.isArray(value) ? value : {};
}

function cloneJson(value) {
  return JSON.parse(JSON.stringify(value));
}

function assertPortableSafeText(value, fieldPath) {
  if (typeof value !== "string" || !value) return;
  if (/^https?:\/\//iu.test(value)) {
    let parsed;
    try {
      parsed = new URL(value);
    } catch {
      parsed = null;
    }
    if (parsed?.username || parsed?.password) {
      throw new Error(`${fieldPath} contains URL credentials that cannot be embedded in portable HTML.`);
    }
    for (const [key] of parsed?.searchParams ?? []) {
      if (PORTABLE_SENSITIVE_URL_PARAMETER_PATTERN.test(key)) {
        throw new Error(`${fieldPath} contains a sensitive URL parameter that cannot be embedded in portable HTML.`);
      }
    }
  }
  if (PORTABLE_CREDENTIAL_ASSIGNMENT_PATTERN.test(value) || PORTABLE_SECRET_TOKEN_PATTERN.test(value)) {
    throw new Error(`${fieldPath} contains credential-like text that cannot be embedded in portable HTML.`);
  }
  if (PORTABLE_LOCAL_PATH_PATTERN.test(value) || PORTABLE_PARENT_PATH_PATTERN.test(value)) {
    throw new Error(`${fieldPath} contains a local filesystem path that cannot be embedded in portable HTML.`);
  }
}

function assertPortableSafeValue(value, fieldPath) {
  if (typeof value === "string") {
    assertPortableSafeText(value, fieldPath);
    return;
  }
  if (Array.isArray(value)) {
    value.forEach((item, index) => assertPortableSafeValue(item, `${fieldPath}[${index}]`));
    return;
  }
  if (!value || typeof value !== "object") return;
  for (const [key, child] of Object.entries(value)) {
    if (PORTABLE_CREDENTIAL_FIELD_PATTERN.test(key) && child != null && String(child).trim()) {
      throw new Error(`${fieldPath}.${key} contains credential-like data that cannot be embedded in portable HTML.`);
    }
    assertPortableSafeValue(child, `${fieldPath}.${key}`);
  }
}

function assertPortableProvenanceSafe(payload) {
  const manifest = asObject(payload.manifest);
  assertPortableSafeValue(payload.sources, "$.sources");
  assertPortableSafeValue(manifest.sources, "$.manifest.sources");
  for (const [collectionName, items] of Object.entries({
    cards: manifest.cards,
    charts: manifest.charts,
    tables: manifest.tables,
  })) {
    asArray(items).forEach((item, index) => {
      if (item?.source) {
        assertPortableSafeValue(item.source, `$.manifest.${collectionName}[${index}].source`);
      }
    });
  }
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function staticChartDimension(value, label) {
  if (!Number.isInteger(value) || value < 1 || value > 10_000) {
    throw new Error(`${label} must be an integer from 1 through 10000.`);
  }
  return value;
}

function decodeStaticSvgAttribute(value, label) {
  const entityPattern = /&(?:#(\d+)|#x([0-9a-f]+)|quot|amp|lt|gt|apos);/giu;
  if (/&(?!(?:#\d+|#x[0-9a-f]+|quot|amp|lt|gt|apos);)/iu.test(value)) {
    throw new Error(`${label} contains an unsupported SVG character reference.`);
  }
  try {
    return value.replace(entityPattern, (entity, decimal, hexadecimal) => {
      if (decimal || hexadecimal) {
        const codePoint = Number.parseInt(decimal ?? hexadecimal, hexadecimal ? 16 : 10);
        if (
          !Number.isInteger(codePoint) ||
          codePoint < 1 ||
          codePoint > 0x10ffff ||
          (codePoint >= 0xd800 && codePoint <= 0xdfff)
        ) {
          throw new Error("invalid code point");
        }
        return String.fromCodePoint(codePoint);
      }
      return {
        "&amp;": "&",
        "&apos;": "'",
        "&gt;": ">",
        "&lt;": "<",
        "&quot;": '"',
      }[entity.toLowerCase()];
    });
  } catch {
    throw new Error(`${label} contains an invalid SVG character reference.`);
  }
}

function staticSvgMarkup(value, label) {
  if (typeof value !== "string") throw new Error(`${label} must be inline SVG markup.`);
  const markup = value.trim();
  const byteLength = Buffer.byteLength(markup, "utf8");
  if (!markup.startsWith("<svg") || !markup.endsWith("</svg>")) {
    throw new Error(`${label} must contain exactly one inline SVG root.`);
  }
  if (byteLength > MAX_STATIC_CHART_BYTES) {
    throw new Error(`${label} exceeds the ${MAX_STATIC_CHART_BYTES.toLocaleString("en-US")} byte limit.`);
  }
  if (/<!|<\?|(?:^|\s)(?:href|xlink:href|src|style)\s*=|(?:^|\s)on[a-z0-9_-]+\s*=|\bvar\s*\(/iu.test(markup)) {
    throw new Error(`${label} contains unsupported active or externally styled SVG content.`);
  }

  const tagPattern = /<(\/)?([A-Za-z][A-Za-z0-9]*)([^<>]*)>/gu;
  const ids = new Set();
  const references = [];
  const tagStack = [];
  let elementCount = 0;
  let rootNamespace = null;
  let scanOffset = 0;
  let svgOpenCount = 0;
  let svgCloseCount = 0;
  let match;
  while ((match = tagPattern.exec(markup))) {
    const gap = markup.slice(scanOffset, match.index);
    const parentTag = tagStack.at(-1);
    if (
      /[<>]/u.test(gap) ||
      (gap.trim() && parentTag !== "text" && parentTag !== "tspan")
    ) {
      throw new Error(`${label} contains malformed SVG markup.`);
    }
    scanOffset = tagPattern.lastIndex;
    const closing = Boolean(match[1]);
    const tagName = match[2].toLowerCase();
    if (!STATIC_SVG_ELEMENTS.has(tagName)) {
      throw new Error(`${label} contains unsupported <${match[2]}> content.`);
    }
    if (tagName === "svg") {
      if (closing) svgCloseCount += 1;
      else svgOpenCount += 1;
    }
    if (closing) {
      if (match[3].trim() || tagStack.pop() !== tagName) {
        throw new Error(`${label} contains unbalanced SVG elements.`);
      }
      continue;
    }
    elementCount += 1;
    if (elementCount > MAX_STATIC_CHART_ELEMENTS) {
      throw new Error(`${label} exceeds the ${MAX_STATIC_CHART_ELEMENTS.toLocaleString("en-US")} element limit.`);
    }

    const selfClosing = /\/\s*$/u.test(match[3]);
    const rawAttributes = match[3].replace(/\/\s*$/u, "");
    const attributePattern = /\s+([A-Za-z_:][A-Za-z0-9_.:-]*)="([^"]*)"/gu;
    let attribute;
    while ((attribute = attributePattern.exec(rawAttributes))) {
      const originalName = attribute[1];
      const name = originalName.toLowerCase();
      const attributeValue = decodeStaticSvgAttribute(attribute[2], `${label} attribute ${originalName}`);
      if (!STATIC_SVG_ATTRIBUTES.has(name)) {
        throw new Error(`${label} contains unsupported SVG attribute ${originalName}.`);
      }
      if (name === "class" && attributeValue !== "portable-static-chart-svg") {
        throw new Error(`${label} contains an unsupported SVG class.`);
      }
      if (name === "aria-hidden" && attributeValue !== "true") {
        throw new Error(`${label} SVG must be hidden from the accessibility tree.`);
      }
      if (name === "focusable" && attributeValue !== "false") {
        throw new Error(`${label} SVG must not be focusable.`);
      }
      if (name === "xmlns") {
        if (tagName !== "svg" || svgOpenCount !== 1 || attributeValue !== STATIC_SVG_NAMESPACE) {
          throw new Error(`${label} must use the standard SVG namespace on its root.`);
        }
        rootNamespace = attributeValue;
      }
      if (name === "id") {
        if (!/^[A-Za-z][A-Za-z0-9_.:-]*$/u.test(attributeValue) || ids.has(attributeValue)) {
          throw new Error(`${label} contains an invalid or duplicate SVG id.`);
        }
        ids.add(attributeValue);
      }
      const urlReferences = [...attributeValue.matchAll(/url\(\s*(["']?)([^)'"\s]+)\1\s*\)/giu)];
      if (/url\s*\(/iu.test(attributeValue) && (urlReferences.length !== 1 || urlReferences[0][0] !== attributeValue.trim())) {
        throw new Error(`${label} contains an unsupported SVG reference.`);
      }
      for (const reference of urlReferences) {
        if (!reference[2].startsWith("#")) {
          throw new Error(`${label} contains an external SVG reference.`);
        }
        references.push(reference[2].slice(1));
      }
      if (name !== "xmlns" && /\b(?:data|blob|file|https?|javascript):/iu.test(attributeValue)) {
        throw new Error(`${label} contains an external SVG reference.`);
      }
      if (/[\\\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/u.test(attributeValue) || /\bvar\s*\(/iu.test(attributeValue)) {
        throw new Error(`${label} contains unsupported SVG attribute content.`);
      }
    }
    if (rawAttributes.replace(attributePattern, "").trim()) {
      throw new Error(`${label} contains malformed or unquoted SVG attributes.`);
    }
    if (!selfClosing) tagStack.push(tagName);
  }
  const trailing = markup.slice(scanOffset);
  if (/[<>]/u.test(trailing) || trailing.trim()) {
    throw new Error(`${label} contains malformed SVG markup.`);
  }
  if (tagStack.length || svgOpenCount !== 1 || svgCloseCount !== 1 || elementCount < 2) {
    throw new Error(`${label} must contain exactly one non-empty inline SVG root.`);
  }
  if (rootNamespace !== STATIC_SVG_NAMESPACE) {
    throw new Error(`${label} must use the standard SVG namespace on its root.`);
  }
  for (const reference of references) {
    if (!ids.has(reference)) throw new Error(`${label} contains an unresolved SVG reference.`);
  }
  return markup;
}

function staticLegendItems(value, label) {
  if (!Array.isArray(value) || value.length > 100) {
    throw new Error(`${label} must be an array with at most 100 items.`);
  }
  return value.map((rawItem, index) => {
    const item = asObject(rawItem);
    const itemLabel = typeof item.label === "string" ? item.label.trim() : "";
    const color = typeof item.color === "string" ? item.color.trim() : "";
    if (!itemLabel || itemLabel.length > 500) {
      throw new Error(`${label}[${index}].label must contain 1 through 500 characters.`);
    }
    if (
      !color
      || color.length > 100
      || /[;{}]|url\s*\(|var\s*\(/iu.test(color)
      || !/^(?:#[0-9a-f]{3,8}|rgba?\([\d.,%\s+-]+\)|hsla?\([\d.,%\s+-]+\)|transparent|currentcolor)$/iu.test(color)
    ) {
      throw new Error(`${label}[${index}].color must be a resolved CSS color.`);
    }
    const marker = item.marker === "line" ? "line" : item.marker === "dot" ? "dot" : null;
    if (!marker) throw new Error(`${label}[${index}].marker must be dot or line.`);
    const dasharray = item.dasharray == null ? null : String(item.dasharray).trim();
    if (dasharray && (dasharray.length > 100 || !/^[A-Za-z0-9.,%+\-\s]+$/u.test(dasharray))) {
      throw new Error(`${label}[${index}].dasharray is invalid.`);
    }
    return { color, label: itemLabel, marker, ...(dasharray ? { dasharray } : {}) };
  });
}

function staticLegend(value, label) {
  const legend = asObject(value);
  const position = legend.position === "right" ? "right" : legend.position === "bottom" ? "bottom" : null;
  if (!position) throw new Error(`${label}.position must be bottom or right.`);
  const title = legend.title == null ? null : String(legend.title).trim();
  if (title != null && (!title || title.length > 500)) {
    throw new Error(`${label}.title must contain 1 through 500 characters when present.`);
  }
  return {
    items: staticLegendItems(legend.items, `${label}.items`),
    position,
    title,
  };
}

function normalizeStaticChartVariant(value, label) {
  const variant = asObject(value);
  return {
    legend: staticLegend(variant.legend, `${label}.legend`),
    svg: staticSvgMarkup(variant.svg, `${label}.svg`),
  };
}

function normalizeStaticCharts(value) {
  if (value == null) return new Map();
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error("staticCharts must be an object keyed by chart block id.");
  }
  const entries = Object.entries(value);
  if (entries.length > MAX_STATIC_CHART_ENTRIES) {
    throw new Error(`staticCharts supports at most ${MAX_STATIC_CHART_ENTRIES} chart entries.`);
  }
  let totalBytes = 0;
  const charts = new Map(entries.map(([blockId, rawChart]) => {
    const staticChart = asObject(rawChart);
    const normalized = {
      dark: normalizeStaticChartVariant(staticChart.dark, `staticCharts.${blockId}.dark`),
      height: staticChartDimension(staticChart.height, `staticCharts.${blockId}.height`),
      light: normalizeStaticChartVariant(staticChart.light, `staticCharts.${blockId}.light`),
      width: staticChartDimension(staticChart.width, `staticCharts.${blockId}.width`),
    };
    totalBytes += Buffer.byteLength(JSON.stringify(normalized.light), "utf8") +
      Buffer.byteLength(JSON.stringify(normalized.dark), "utf8");
    return [blockId, normalized];
  }));
  if (totalBytes > MAX_STATIC_CHART_TOTAL_BYTES) {
    throw new Error(`staticCharts exceeds the ${MAX_STATIC_CHART_TOTAL_BYTES.toLocaleString("en-US")} byte total limit.`);
  }
  return charts;
}

function safeLinkTarget(value) {
  const target = String(value ?? "").trim();
  if (/^(?:https?:|mailto:)/i.test(target)) return target;
  if (/^(?:#|\.\.?\/)/.test(target)) return target;
  return "#";
}

const INLINE_QUANTITATIVE_LITERAL_PATTERN = /(?:[$€£¥]\s*)?[+−-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?:\s?(?:%|[kKmMbBtTxX]))?/gu;
const INLINE_MONTH_BEFORE_NUMBER_PATTERN = /(?:^|\s)(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+$/iu;

function isInlineQuantitativeLiteral(source, match) {
  const token = match[0];
  const start = match.index ?? 0;
  const end = start + token.length;
  const previous = source[start - 1] ?? "";
  const next = source[end] ?? "";
  if (/^[+\u2212-]/u.test(token) && /\d/u.test(previous)) return false;
  if (/\d/u.test(token[0]) && /[\p{L}\p{N}_]/u.test(previous)) return false;
  if (/[\p{L}\p{N}_]/u.test(next)) return false;
  if (/[./:-]/u.test(previous) && /\d/u.test(source[start - 2] ?? "")) return false;
  if (/[./:-]/u.test(next) && /\d/u.test(source[end + 1] ?? "")) return false;

  const plainInteger = token.replace(/[+−-]/gu, "").trim();
  const numericYear = /^\d{4}$/u.test(plainInteger) ? Number(plainInteger) : null;
  if (numericYear != null && numericYear >= 1900 && numericYear <= 2100) return false;
  if (/^\d{1,2}$/u.test(plainInteger)) {
    const prefix = source.slice(Math.max(0, start - 12), start);
    if (INLINE_MONTH_BEFORE_NUMBER_PATTERN.test(prefix)) return false;
  }
  return true;
}

function renderInlineText(value, sourceOptions) {
  const source = String(value ?? "");
  const { nextSourceTooltipId, sourceItem, sourcesById } = sourceOptions ?? {};
  if (
    !sourceItem
    || !(sourcesById instanceof Map)
    || typeof nextSourceTooltipId !== "function"
    || !sourceForItem(sourceItem, sourcesById)
  ) {
    return escapeHtml(source);
  }

  let output = "";
  let offset = 0;
  for (const match of source.matchAll(INLINE_QUANTITATIVE_LITERAL_PATTERN)) {
    if (!isInlineQuantitativeLiteral(source, match)) continue;
    const index = match.index ?? 0;
    output += escapeHtml(source.slice(offset, index));
    output += sourceValueAffordance(
      sourceItem,
      sourcesById,
      match[0],
      nextSourceTooltipId(),
    );
    offset = index + match[0].length;
  }
  output += escapeHtml(source.slice(offset));
  return output;
}

const INLINE_MARKDOWN_TOKEN_PATTERN = /(`[^`\n]+`|\*\*[^*\n]+\*\*|\[[^\]\n]+\]\([^)\n]+\)|\*[^*\n]+\*)/g;

function inlineMarkdownPlainText(value) {
  const source = String(value ?? "");
  let output = "";
  let offset = 0;
  for (const match of source.matchAll(INLINE_MARKDOWN_TOKEN_PATTERN)) {
    output += source.slice(offset, match.index);
    const token = match[0];
    if (token.startsWith("`")) {
      output += token.slice(1, -1);
    } else if (token.startsWith("**")) {
      output += token.slice(2, -2);
    } else if (token.startsWith("[")) {
      output += /^\[([^\]]+)\]\([^)]+\)$/.exec(token)?.[1] ?? token;
    } else {
      output += token.slice(1, -1);
    }
    offset = (match.index ?? 0) + token.length;
  }
  return output + source.slice(offset);
}

function renderInlineMarkdown(value, sourceOptions) {
  const source = String(value ?? "");
  let output = "";
  let offset = 0;
  for (const match of source.matchAll(INLINE_MARKDOWN_TOKEN_PATTERN)) {
    output += renderInlineText(source.slice(offset, match.index), sourceOptions);
    const token = match[0];
    if (token.startsWith("`")) {
      output += `<code>${escapeHtml(token.slice(1, -1))}</code>`;
    } else if (token.startsWith("**")) {
      output += `<strong>${renderInlineText(token.slice(2, -2), sourceOptions)}</strong>`;
    } else if (token.startsWith("[")) {
      const parts = /^\[([^\]]+)\]\(([^)]+)\)$/.exec(token);
      const label = parts?.[1] ?? token;
      const href = safeLinkTarget(parts?.[2]);
      output += `<a href="${escapeHtml(href)}" rel="noreferrer">${escapeHtml(label)}</a>`;
    } else {
      output += `<em>${renderInlineText(token.slice(1, -1), sourceOptions)}</em>`;
    }
    offset = (match.index ?? 0) + token.length;
  }
  output += renderInlineText(source.slice(offset), sourceOptions);
  return output;
}

function markdownPlainText(markdown) {
  return String(markdown ?? "")
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/\*\*([^*]+)\*\*/g, "$1")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .trim();
}

function markdownFirstLine(markdown, fallback) {
  const first = markdownPlainText(markdown).split(/\r?\n/).find((line) => line.trim());
  return first?.trim() || fallback;
}

function normalizedText(value) {
  return String(value ?? "")
    .normalize("NFC")
    .replace(/\s+/gu, " ")
    .trim();
}

function normalizedInlineMarkdownText(markdown) {
  return normalizedText(inlineMarkdownPlainText(markdown));
}

function staticMarkdownBody(markdown, title) {
  const source = String(markdown ?? "").replaceAll("\r\n", "\n");
  const lines = source.split("\n");
  const headingIndex = lines.findIndex((line) => line.trim());
  if (headingIndex < 0) return source;
  const heading = /^#[ \t]+([^\r\n]+)$/u.exec(lines[headingIndex]);
  if (!heading || normalizedInlineMarkdownText(heading[1]) !== normalizedText(title)) return source;
  lines.splice(headingIndex, 1);
  while (lines[headingIndex] != null && !lines[headingIndex].trim()) lines.splice(headingIndex, 1);
  const body = lines.join("\n");
  return body.trim() ? body : null;
}

export function renderMarkdown(markdown, sourceOptions = null) {
  const lines = String(markdown ?? "").replaceAll("\r\n", "\n").split("\n");
  const output = [];
  let index = 0;

  while (index < lines.length) {
    const line = lines[index];
    if (!line.trim()) {
      index += 1;
      continue;
    }

    const fence = /^\s*```(?:\w+)?\s*$/.exec(line);
    if (fence) {
      const code = [];
      index += 1;
      while (index < lines.length && !/^\s*```\s*$/.test(lines[index])) {
        code.push(lines[index]);
        index += 1;
      }
      if (index < lines.length) index += 1;
      output.push(`<pre><code>${escapeHtml(code.join("\n"))}</code></pre>`);
      continue;
    }

    const heading = /^(#{1,6})\s+(.+)$/.exec(line);
    if (heading) {
      const level = heading[1].length;
      output.push(`<h${level}>${renderInlineMarkdown(heading[2], sourceOptions)}</h${level}>`);
      index += 1;
      continue;
    }

    if (/^\s*(?:---+|___+|\*\*\*+)\s*$/.test(line)) {
      output.push("<hr />");
      index += 1;
      continue;
    }

    const unordered = /^\s*[-+*]\s+(.+)$/.exec(line);
    const ordered = /^\s*\d+[.)]\s+(.+)$/.exec(line);
    if (unordered || ordered) {
      const tag = unordered ? "ul" : "ol";
      const items = [];
      while (index < lines.length) {
        const match = tag === "ul"
          ? /^\s*[-+*]\s+(.+)$/.exec(lines[index])
          : /^\s*\d+[.)]\s+(.+)$/.exec(lines[index]);
        if (!match) break;
        items.push(`<li>${renderInlineMarkdown(match[1], sourceOptions)}</li>`);
        index += 1;
      }
      output.push(`<${tag}>${items.join("")}</${tag}>`);
      continue;
    }

    const quote = /^\s*>\s?(.*)$/.exec(line);
    if (quote) {
      const quoted = [];
      while (index < lines.length) {
        const match = /^\s*>\s?(.*)$/.exec(lines[index]);
        if (!match) break;
        quoted.push(match[1]);
        index += 1;
      }
      output.push(`<blockquote>${renderInlineMarkdown(quoted.join(" "), sourceOptions)}</blockquote>`);
      continue;
    }

    const paragraph = [line.trim()];
    index += 1;
    while (
      index < lines.length &&
      lines[index].trim() &&
      !/^(?:#{1,6}\s|\s*```|\s*[-+*]\s+|\s*\d+[.)]\s+|\s*>)/.test(lines[index])
    ) {
      paragraph.push(lines[index].trim());
      index += 1;
    }
    output.push(`<p>${renderInlineMarkdown(paragraph.join(" "), sourceOptions)}</p>`);
  }

  return output.join("\n");
}

function numberValue(value) {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string" && value.trim()) {
    const parsed = Number(value.replaceAll(",", ""));
    if (Number.isFinite(parsed)) return parsed;
  }
  return null;
}

function formatValue(value, format, unit) {
  if (value == null || value === "") return "—";
  const numeric = numberValue(value);
  if (numeric == null) return String(value);
  let rendered;
  if (format === "percent") {
    rendered = new Intl.NumberFormat("en-US", {
      maximumFractionDigits: 1,
      style: "percent",
    }).format(numeric);
  } else if (format === "currency") {
    rendered = new Intl.NumberFormat("en-US", {
      currency: "USD",
      maximumFractionDigits: 2,
      notation: "compact",
      style: "currency",
    }).format(numeric);
  } else if (format === "number") {
    rendered = new Intl.NumberFormat("en-US", { maximumFractionDigits: 2 }).format(numeric);
  } else {
    rendered = new Intl.NumberFormat("en-US", {
      maximumFractionDigits: 2,
      notation: "compact",
    }).format(numeric);
  }
  return unit && format !== "currency" ? `${rendered}${unit}` : rendered;
}

function rowsFor(snapshot, dataset) {
  return asArray(asObject(snapshot?.datasets)[dataset]);
}

function rowMatchesFilter(row, filter) {
  return Object.entries(asObject(filter)).every(
    ([field, expected]) => String(row?.[field] ?? "") === String(expected ?? ""),
  );
}

function filterTargets(filter) {
  const normalized = asObject(filter);
  const targets = [
    { dataset: normalized.dataset, field: normalized.field },
    ...asArray(normalized.targets).map((target) => ({
      dataset: target?.dataset,
      field: target?.field ?? normalized.field,
    })),
  ];
  const seen = new Set();
  return targets.filter((target) => {
    if (!target.dataset || !target.field) return false;
    const key = `${target.dataset}\u0001${target.field}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function filterFieldForDataset(filter, dataset) {
  return filterTargets(filter).find((target) => target.dataset === dataset)?.field ?? null;
}

function dashboardSurfaceDatasets(cards, charts, tables) {
  return new Set([...cards, ...charts, ...tables]
    .map((surface) => surface?.dataset)
    .filter(Boolean));
}

function isGlobalFilter(filter, cards, charts, tables) {
  const requiredDatasets = dashboardSurfaceDatasets(cards, charts, tables);
  if (requiredDatasets.size <= 1) return true;
  const targetDatasets = new Set(filterTargets(filter).map((target) => target.dataset));
  return [...requiredDatasets].every((dataset) => targetDatasets.has(dataset));
}

function activeFallbackFilters(manifest, cards, charts, tables) {
  const filters = asArray(manifest.filters);
  if (manifest.surface === "report") return filters;
  return filters.filter((filter) => isGlobalFilter(filter, cards, charts, tables));
}

function filterRowsForDefault(rows, dataset, filters, usedFields = []) {
  const usedFieldSet = new Set(usedFields.filter(Boolean));
  const explicitAllFields = new Set(filters
    .map((filter) => {
      const field = filterFieldForDataset(filter, dataset);
      const selected = filter.defaultValue ?? "all";
      return field && selected === "all" && rows.some((row) => String(row?.[field] ?? "") === "all")
        ? field
        : null;
    })
    .filter(Boolean));
  const filteredRows = rows.filter((row) => filters.every((filter) => {
    const field = filterFieldForDataset(filter, dataset);
    if (!field) return true;
    const selected = filter.defaultValue ?? "all";
    if (selected === "all") {
      return !explicitAllFields.has(field) || String(row?.[field] ?? "") === "all";
    }
    return String(row?.[field] ?? "") === String(selected);
  }));
  const aggregateFields = Object.keys(rows[0] ?? {}).filter((field) => {
    if (usedFieldSet.has(field)) return false;
    let hasAggregate = false;
    let hasBreakdown = false;
    for (const row of filteredRows) {
      const value = String(row?.[field] ?? "");
      if (value === "all") hasAggregate = true;
      else if (value) hasBreakdown = true;
      if (hasAggregate && hasBreakdown) return true;
    }
    return false;
  });
  if (!aggregateFields.length) return filteredRows;
  const aggregateRows = filteredRows.filter((row) => (
    aggregateFields.every((field) => String(row?.[field] ?? "") === "all")
  ));
  return aggregateRows.length ? aggregateRows : filteredRows;
}

function compareTableValues(left, right, field, direction) {
  const leftValue = left?.[field];
  const rightValue = right?.[field];
  if (leftValue == null && rightValue == null) return 0;
  if (leftValue == null) return direction === "asc" ? 1 : -1;
  if (rightValue == null) return direction === "asc" ? -1 : 1;
  const result = typeof leftValue === "number" && typeof rightValue === "number"
    ? leftValue - rightValue
    : String(leftValue).localeCompare(String(rightValue), undefined, {
      numeric: true,
      sensitivity: "base",
    });
  return direction === "asc" ? result : -result;
}

function sortTableRowsByDefault(rows, table) {
  const defaultSort = asObject(table.defaultSort);
  if (
    typeof defaultSort.field !== "string"
    || !asArray(table.columns).some((column) => column?.field === defaultSort.field)
  ) {
    return rows;
  }
  const direction = defaultSort.direction === "desc" ? "desc" : "asc";
  return [...rows].sort((left, right) => (
    compareTableValues(left, right, defaultSort.field, direction)
  ));
}

function sourceForItem(item, sourcesById) {
  if (item?.source && typeof item.source === "object") return item.source;
  return typeof item?.sourceId === "string" ? sourcesById.get(item.sourceId) : null;
}

function sourceStringList(value) {
  if (Array.isArray(value)) {
    return value.map((item) => String(item ?? "").trim()).filter(Boolean);
  }
  const text = String(value ?? "").trim();
  return text ? [text] : [];
}

function sourceTableNames(source, query) {
  for (const candidate of [source, query]) {
    const object = asObject(candidate);
    for (const key of ["tables_used", "tablesUsed", "source_tables", "sourceTables", "tables"]) {
      const values = sourceStringList(object[key]);
      if (values.length) return values;
    }
  }
  const tables = [];
  const seen = new Set();
  const sql = typeof query.sql === "string" ? query.sql : "";
  for (const match of sql.matchAll(/\b(?:from|join)\s+([`"\[]?[\w.-]+(?:\.[\w.-]+){0,3}[`"\]]?)/giu)) {
    const table = match[1].replace(/^[`"\[]|[`"\]]$/gu, "");
    const normalized = table.toLowerCase();
    if (!table || seen.has(normalized)) continue;
    seen.add(normalized);
    tables.push(table);
  }
  return tables;
}

function sourceAffordanceDetails(item, sourcesById, contextDescription = "") {
  const source = sourceForItem(item, sourcesById);
  const context = String(contextDescription ?? "").trim();
  if (!source && !context) return null;
  const query = asObject(source?.query);
  const sourceId = source && (source.id || item.sourceId || source.path || source.href || "source");
  const label = source && (source.label || query.engine || source.path || source.href || sourceId);
  const tables = source ? sourceTableNames(source, query) : [];
  const metadata = tables.length
    ? `${tables.length === 1 ? "Table" : "Tables"}: ${tables.join(", ")}`
    : source?.path
      ? `File: ${source.path}`
      : "";
  return { context, label, metadata, query, source, sourceId };
}

function sourceAffordanceBody(details, itemLabel, { includeDetails = true } = {}) {
  const sql = includeDetails && typeof details.query.sql === "string" && details.query.sql.trim()
    ? `<pre class="portable-source-query-data" aria-hidden="true"><code>${escapeHtml(details.query.sql)}</code></pre>`
    : "";
  return [
    `<span class="portable-source-tooltip-heading" aria-hidden="true">${details.source ? "Source for" : "About"} ${escapeHtml(itemLabel)}</span>`,
    details.context ? `<span class="portable-source-context">${escapeHtml(details.context)}</span>` : "",
    details.source ? `<strong>Source: ${escapeHtml(details.label)}</strong>` : "",
    details.metadata ? `<span class="portable-source-meta">${escapeHtml(details.metadata)}</span>` : "",
    includeDetails && details.query.description
      ? `<p class="portable-source-description-data">${escapeHtml(details.query.description)}</p>`
      : "",
    sql,
  ].join("");
}

function inlineSourceAffordance(item, sourcesById, itemLabel, tooltipId, contextDescription = "") {
  const details = sourceAffordanceDetails(item, sourcesById, contextDescription);
  if (!details) return { attributes: "", markup: "" };
  return {
    attributes: ` data-portable-source-host="true" tabindex="0" aria-label="${escapeHtml(itemLabel)}" aria-describedby="${tooltipId}"`,
    markup: [
    `<div class="portable-inline-source"${details.sourceId ? ` data-source-id="${escapeHtml(details.sourceId)}"` : ""}>`,
    `<div class="portable-inline-source-content portable-source-tooltip-content" id="${tooltipId}" role="tooltip">`,
    sourceAffordanceBody(details, itemLabel),
    "</div>",
    "</div>",
    ].join(""),
  };
}

function sourceValueAffordance(item, sourcesById, value, tooltipId, contextDescription = "") {
  const details = sourceAffordanceDetails(item, sourcesById, contextDescription);
  const renderedValue = escapeHtml(value);
  if (!details) return renderedValue;
  const tooltipDetails = details.source ? { ...details, context: "" } : details;
  return [
    `<span class="portable-source-tooltip portable-source-value" data-portable-source-host="true" tabindex="0" aria-describedby="${tooltipId}">`,
    `<span class="portable-source-value-text">${renderedValue}</span>`,
    `<span class="portable-source-tooltip-content" id="${tooltipId}" role="tooltip">`,
    sourceAffordanceBody(tooltipDetails, value, { includeDetails: false }),
    "</span>",
    "</span>",
  ].join("");
}

function sourceSummaryAffordance(item, sourcesById, itemLabel, contextDescription = "") {
  const details = sourceAffordanceDetails(item, sourcesById, contextDescription);
  if (!details?.source) return "";
  return [
    `<div class="portable-inline-source portable-source-summary"${details.sourceId ? ` data-source-id="${escapeHtml(details.sourceId)}"` : ""}>`,
    '<div class="portable-inline-source-content portable-source-summary-content">',
    sourceAffordanceBody(details, itemLabel),
    "</div>",
    "</div>",
  ].join("");
}

function metricCardFallback(card, blockId, snapshot, sourcesById, filters, nextSourceTooltipId) {
  const metrics = asArray(card.metrics);
  const rows = filterRowsForDefault(
    rowsFor(snapshot, card.dataset),
    card.dataset,
    filters,
    metrics.map((metric) => metric.field),
  );
  const row = rows.find((candidate) => rowMatchesFilter(candidate, card.filter)) ?? {};
  const [primary, ...supporting] = metrics;
  const label = primary?.label ?? card.id;
  const primaryRawValue = primary ? row[primary.field] : null;
  const value = primary ? formatValue(primaryRawValue, primary.format) : "—";
  const valueMarkup = primaryRawValue == null || primaryRawValue === ""
    ? escapeHtml(value)
    : sourceValueAffordance(
      card,
      sourcesById,
      value,
      nextSourceTooltipId(),
      card.description,
    );
  const badges = supporting.map((metric) => {
    const rawValue = row[metric.field];
    const numeric = numberValue(rawValue);
    const prefix = metric.signed && numeric > 0 ? "+" : "";
    const rendered = prefix + formatValue(rawValue, metric.format);
    const movementClass = metric.signed && numeric > 0
      ? " portable-positive"
      : metric.signed && numeric < 0
        ? " portable-negative"
        : "";
    const renderedMarkup = rawValue == null || rawValue === ""
      ? escapeHtml(rendered)
      : sourceValueAffordance(card, sourcesById, rendered, nextSourceTooltipId());
    return `<span class="portable-metric-badge${movementClass}"><span>${escapeHtml(metric.label)}</span> <strong>${renderedMarkup}</strong></span>`;
  }).join("");
  const description = card.description
    ? `<p class="portable-card-description">${escapeHtml(card.description)}</p>`
    : "";
  const sourceSummary = sourceSummaryAffordance(
    card,
    sourcesById,
    label,
    card.description,
  );
  const artifactId = `metric:${blockId}:${card.id}`;
  return [
    `<article class="portable-metric-card" data-artifact-id="${escapeHtml(artifactId)}" data-artifact-kind="card" data-card-id="${escapeHtml(card.id)}">`,
    `<p class="portable-metric-label">${escapeHtml(label)}</p>`,
    `<p class="portable-metric-value">${valueMarkup}</p>`,
    description,
    badges ? `<div class="portable-metric-badges">${badges}</div>` : "",
    sourceSummary,
    "</article>",
  ].join("");
}

function fieldLabel(field) {
  return String(field ?? "")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function chartColumns(chart, rows) {
  const encodings = asObject(chart.encodings);
  const columns = [];
  const seen = new Set();
  for (const role of ["x", "y", "color", "size", "facet", "label"]) {
    const encoding = asObject(encodings[role]);
    const fields = [encoding.field, ...asArray(encoding.fields)].filter(
      (field) => typeof field === "string" && field,
    );
    for (const field of fields) {
      if (seen.has(field)) continue;
      seen.add(field);
      columns.push({
        field,
        format: encoding.format ?? (role === "y" ? chart.valueFormat : undefined),
        label: encoding.label ?? fieldLabel(field),
        unit: encoding.unit ?? (role === "y" ? chart.unit : undefined),
      });
    }
  }
  for (const encoding of asArray(encodings.tooltip)) {
    const field = asObject(encoding).field;
    if (typeof field !== "string" || !field || seen.has(field)) continue;
    seen.add(field);
    columns.push({
      field,
      format: encoding.format,
      label: encoding.label ?? fieldLabel(field),
      unit: encoding.unit,
    });
  }
  if (!columns.length && rows.length) {
    for (const field of Object.keys(asObject(rows[0]))) {
      columns.push({ field, label: fieldLabel(field) });
    }
  }
  return columns;
}

function isNumericTableColumn(column, rows) {
  const format = column.format ?? column.type;
  if (["currency", "number", "percent"].includes(format)) return true;
  const values = rows.map((row) => row?.[column.field]).filter((value) => value != null && value !== "");
  return values.length > 0 && values.every((value) => numberValue(value) != null);
}

function tableColumnLooksLikeMovement(column) {
  return column.movement === true || column.semantic === "movement" || column.role === "movement";
}

function tableMovementDirection(value) {
  const numeric = numberValue(value);
  if (numeric != null) return numeric > 0 ? "positive" : numeric < 0 ? "negative" : "neutral";
  const text = String(value ?? "").trim();
  if (/^[+↑]/.test(text)) return "positive";
  if (/^[-−↓]/.test(text)) return "negative";
  return "neutral";
}

function tableCellClasses(column, rows, value, extraClasses = []) {
  const classes = [...extraClasses];
  if (isNumericTableColumn(column, rows)) classes.push("portable-table-number");
  if (column.align === "center") classes.push("portable-table-center");
  if (tableColumnLooksLikeMovement(column)) {
    const direction = tableMovementDirection(value);
    if (direction === "positive") classes.push("portable-table-positive");
    else if (direction === "negative") classes.push("portable-table-negative");
  }
  return classes.length ? ` class="${classes.join(" ")}"` : "";
}

function tableCellText(column, row) {
  const rawValue = row?.[column.field];
  return `${tableColumnLooksLikeMovement(column) && numberValue(rawValue) > 0 ? "+" : ""}${formatValue(rawValue, column.format ?? column.type, column.unit)}`;
}

function tableTruncationNote(rowCount, visibleRowCount) {
  return rowCount > visibleRowCount
    ? `<p class="portable-table-note">${rowCount.toLocaleString("en-US")} results · Showing first ${visibleRowCount.toLocaleString("en-US")}</p>`
    : "";
}

function semanticTable({
  columns,
  rows,
  caption,
  rowLimit = Number.POSITIVE_INFINITY,
  showTruncation = true,
  sourceItem = null,
  sourcesById = null,
  nextSourceTooltipId = null,
}) {
  const visibleRows = rows.slice(0, rowLimit);
  const header = columns.map((column) => `<th scope="col"${tableCellClasses(column, rows)}>${escapeHtml(column.label ?? fieldLabel(column.field))}</th>`).join("");
  const body = visibleRows.map((row) => {
    const cells = columns.map((column) => {
      const rawValue = row?.[column.field];
      const rendered = tableCellText(column, row);
      const hasSourceTooltip = sourceItem
        && sourcesById
        && typeof nextSourceTooltipId === "function"
        && isNumericTableColumn(column, rows)
        && rawValue != null
        && rawValue !== "";
      const content = hasSourceTooltip
        ? sourceValueAffordance(sourceItem, sourcesById, rendered, nextSourceTooltipId())
        : escapeHtml(rendered);
      return `<td${tableCellClasses(column, rows, rawValue, hasSourceTooltip ? ["portable-table-source-cell"] : [])}>${content}</td>`;
    }).join("");
    return `<tr>${cells}</tr>`;
  }).join("");
  const empty = visibleRows.length
    ? ""
    : `<tr><td class="portable-empty-cell" colspan="${Math.max(columns.length, 1)}">No rows available.</td></tr>`;
  const truncation = showTruncation ? tableTruncationNote(rows.length, visibleRows.length) : "";
  return [
    '<div class="portable-table-scroll">',
    "<table>",
    caption ? `<caption>${escapeHtml(caption)}</caption>` : "",
    `<thead><tr>${header}</tr></thead>`,
    `<tbody>${body || empty}</tbody>`,
    "</table>",
    "</div>",
    truncation,
  ].join("");
}

function staticChartLegend(legend) {
  if (!legend.items.length && !legend.title) return "";
  const content = legend.items.map((item) => [
    "<li>",
    `<span class="portable-static-chart-legend-marker portable-static-chart-legend-marker-${item.marker}${item.dasharray ? " portable-static-chart-legend-marker-dashed" : ""}" style="--portable-legend-color:${escapeHtml(item.color)}"></span>`,
    `<span>${escapeHtml(item.label)}</span>`,
    "</li>",
  ].join("")).join("");
  return [
    `<div class="portable-static-chart-legend-wrap portable-static-chart-legend-${legend.position}">`,
    legend.title ? `<p class="portable-static-chart-legend-title">${escapeHtml(legend.title)}</p>` : "",
    content ? `<ul class="portable-static-chart-legend">${content}</ul>` : "",
    "</div>",
  ].join("");
}

function staticChartVariant(variant, theme) {
  return [
    `<div class="portable-static-chart-variant portable-static-chart-${theme}" aria-hidden="true">`,
    variant.svg,
    staticChartLegend(variant.legend),
    "</div>",
  ].join("");
}

function staticChartVector(chart, blockId, staticChart) {
  if (!staticChart) return "";
  const label = `${chart.title} chart`;
  return [
    `<div class="portable-static-chart" data-static-chart-id="${escapeHtml(chart.id)}" data-static-chart-block-id="${escapeHtml(blockId)}" role="img" aria-label="${escapeHtml(label)}" style="max-width:${staticChart.width}px">`,
    staticChartVariant(staticChart.light, "light"),
    staticChartVariant(staticChart.dark, "dark"),
    "</div>",
  ].join("");
}

function chartFallback(chart, blockId, snapshot, sourcesById, filters, staticCharts, tooltipId) {
  const unfilteredRows = rowsFor(snapshot, chart.dataset);
  const columns = chartColumns(chart, unfilteredRows);
  const rows = filterRowsForDefault(
    unfilteredRows,
    chart.dataset,
    filters,
    columns.map((column) => column.field),
  );
  const staticChart = staticCharts.get(blockId);
  const chartVector = staticChartVector(chart, blockId, staticChart);
  const chartData = columns.length
    ? semanticTable({ columns, rows, caption: `${chart.title} data`, rowLimit: MAX_CHART_SUMMARY_ROWS })
    : '<p class="portable-empty">No chart data is available.</p>';
  const displayTitle = chart.headerMarkdown
    ? markdownFirstLine(chart.headerMarkdown, chart.title)
    : chart.title;
  const sourceAffordance = inlineSourceAffordance(chart, sourcesById, displayTitle, tooltipId);
  const header = chart.headerMarkdown
    ? `<figcaption class="portable-visual-header portable-markdown">${renderMarkdown(chart.headerMarkdown)}</figcaption>`
    : `<figcaption class="portable-visual-header"><strong>${escapeHtml(chart.title)}</strong>${chart.showDescription && chart.subtitle ? `<span>${escapeHtml(chart.subtitle)}</span>` : ""}</figcaption>`;
  return [
    `<figure class="portable-content-card portable-chart-summary" data-artifact-id="${escapeHtml(chart.id)}" data-artifact-kind="chart" data-chart-id="${escapeHtml(chart.id)}" data-portable-visual-title="${escapeHtml(displayTitle)}"${sourceAffordance.attributes}>`,
    header,
    sourceAffordance.markup,
    chartVector,
    staticChart && columns.length
      ? `<div class="portable-chart-data portable-chart-data-has-vector">${chartData}</div>`
      : chartData,
    "</figure>",
  ].join("");
}

function tableFallback(table, snapshot, sourcesById, filters, nextSourceTooltipId) {
  const rowLimit = 15;
  const columns = asArray(table.columns);
  const rows = sortTableRowsByDefault(filterRowsForDefault(
    rowsFor(snapshot, table.dataset),
    table.dataset,
    filters,
    columns.map((column) => column.field),
  ), table);
  const displayTitle = table.headerMarkdown
    ? markdownFirstLine(table.headerMarkdown, table.title)
    : table.title;
  const hasSource = Boolean(sourceForItem(table, sourcesById));
  const sourceSummary = sourceSummaryAffordance(table, sourcesById, displayTitle);
  const header = table.headerMarkdown
    ? `<header class="portable-visual-header portable-markdown">${renderMarkdown(table.headerMarkdown)}</header>`
    : `<header class="portable-visual-header"><h2>${escapeHtml(table.title)}</h2>${table.showDescription && table.subtitle ? `<p>${escapeHtml(table.subtitle)}</p>` : ""}</header>`;
  return [
    `<section class="portable-content-card portable-table-card" data-artifact-id="${escapeHtml(table.id)}" data-artifact-kind="table" data-table-id="${escapeHtml(table.id)}" data-portable-visual-title="${escapeHtml(displayTitle)}">`,
    header,
    sourceSummary,
    '<div class="portable-table-source-region">',
    semanticTable({
      columns,
      rows,
      caption: table.title,
      rowLimit,
      showTruncation: false,
      sourceItem: hasSource ? table : null,
      sourcesById: hasSource ? sourcesById : null,
      nextSourceTooltipId,
    }),
    "</div>",
    tableTruncationNote(rows.length, Math.min(rows.length, rowLimit)),
    "</section>",
  ].join("");
}

function customHtmlFallback(block) {
  const csp = "default-src 'none'; img-src data: blob:; style-src 'unsafe-inline'; font-src data:; connect-src 'none'; script-src 'none'; media-src data: blob:; frame-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'";
  const source = `<!doctype html><html><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="${csp}"><style>html{color-scheme:light dark}body{margin:0;font:14px/1.5 system-ui,sans-serif;color:CanvasText;background:Canvas}img{max-width:100%;height:auto}</style></head><body>${block.body}</body></html>`;
  return [
    '<section class="portable-content-card portable-custom-html">',
    `<iframe sandbox="" loading="lazy" referrerpolicy="no-referrer" title="Custom report content" srcdoc="${escapeHtml(source)}"></iframe>`,
    "</section>",
  ].join("");
}

function accessIssuesFallback(snapshot) {
  const issues = asArray(snapshot?.accessIssues);
  if (!issues.length) return "";
  const items = issues.map((issue) => {
    const message = issue?.message ?? "Required data could not be loaded.";
    const scope = issue?.scope || issue?.dataset || issue?.sourceId;
    return `<li>${scope ? `<strong>${escapeHtml(scope)}:</strong> ` : ""}${escapeHtml(message)}</li>`;
  }).join("");
  return `<section class="portable-notice" aria-labelledby="portable-access-issues"><h2 id="portable-access-issues">Data access issues</h2><ul>${items}</ul></section>`;
}

function sourcesFallback(sources) {
  if (!sources.length) return "";
  const items = sources.map((source, index) => {
    const query = asObject(source.query);
    const label = source.label || source.path || source.href || source.id || `Source ${index + 1}`;
    const metadata = [source.path, query.engine, query.executed_at].filter(Boolean).map(escapeHtml).join(" · ");
    const sql = typeof query.sql === "string" && query.sql.trim()
      ? `<details class="portable-source-query" open><summary>SQL query</summary><pre><code>${escapeHtml(query.sql)}</code></pre></details>`
      : "";
    return [
      "<li>",
      `<strong>${escapeHtml(label)}</strong>`,
      metadata ? `<span class="portable-source-meta">${metadata}</span>` : "",
      query.description ? `<p>${escapeHtml(query.description)}</p>` : "",
      sql,
      "</li>",
    ].join("");
  }).join("");
  return `<section class="portable-sources" aria-labelledby="portable-sources-heading"><h2 id="portable-sources-heading">Sources</h2><ol>${items}</ol></section>`;
}

function staticFiltersFallback(filters) {
  if (!filters.length) return "";
  const items = filters.map((filter) => {
    const label = filter.label || fieldLabel(filter.field || filter.id);
    const selected = filter.defaultValue == null || filter.defaultValue === "all"
      ? "All"
      : String(filter.defaultValue);
    return `<span class="portable-filter-chip"><span>${escapeHtml(label)}</span><strong>${escapeHtml(selected)}</strong></span>`;
  }).join("");
  return `<div class="portable-filter-bar" aria-label="Default filters">${items}</div>`;
}

function formatPortableDate(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return `${new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "UTC",
  }).format(date)} UTC`;
}

export function semanticFallback(payload, options = {}) {
  const manifest = asObject(payload.manifest);
  const snapshot = asObject(payload.snapshot);
  const surface = payload.surface || manifest.surface || "artifact";
  const staticCharts = normalizeStaticCharts(options.staticCharts);
  const cardSpecs = asArray(manifest.cards);
  const chartSpecs = asArray(manifest.charts);
  const tableSpecs = asArray(manifest.tables);
  const filters = activeFallbackFilters(manifest, cardSpecs, chartSpecs, tableSpecs);
  const cards = new Map(cardSpecs.map((card) => [card.id, card]));
  const charts = new Map(chartSpecs.map((chart) => [chart.id, chart]));
  const tables = new Map(tableSpecs.map((table) => [table.id, table]));
  const sourcesById = new Map();
  let sourceTooltipIndex = 0;
  const nextSourceTooltipId = () => {
    sourceTooltipIndex += 1;
    return `portable-source-tooltip-${sourceTooltipIndex}`;
  };
  for (const source of asArray(payload.sources)) {
    for (const key of [source.id, source.path, source.href]) {
      if (typeof key === "string" && key) sourcesById.set(key, source);
    }
  }
  const blocks = asArray(manifest.blocks).map((block) => {
    let content = "";
    let itemLayout = block.layout;
    if (block.type === "markdown") {
      const body = staticMarkdownBody(block.body, manifest.title);
      if (body == null) return "";
      const itemLabel = markdownFirstLine(body, "Narrative");
      content = `<section class="portable-markdown">${renderMarkdown(body, {
        nextSourceTooltipId,
        sourceItem: block,
        sourcesById,
      })}</section>${sourceSummaryAffordance(block, sourcesById, itemLabel)}`;
    } else if (block.type === "metric-strip") {
      const metrics = asArray(block.cardIds).map((cardId) => cards.get(cardId)).filter(Boolean);
      content = `<section class="portable-metric-grid">${metrics.map((card) => metricCardFallback(card, block.id, snapshot, sourcesById, filters, nextSourceTooltipId)).join("")}</section>`;
    } else if (block.type === "chart" && charts.has(block.chartId)) {
      const chart = charts.get(block.chartId);
      itemLayout = surface === "dashboard" ? itemLayout ?? chart.layout ?? "half" : itemLayout ?? "full";
      content = chartFallback(chart, block.id, snapshot, sourcesById, filters, staticCharts, nextSourceTooltipId());
    } else if (block.type === "table" && tables.has(block.tableId)) {
      const table = tables.get(block.tableId);
      itemLayout = surface === "dashboard" ? itemLayout ?? table.layout ?? "full" : itemLayout ?? "full";
      content = tableFallback(table, snapshot, sourcesById, filters, nextSourceTooltipId);
    } else if (block.type === "html") {
      content = customHtmlFallback(block);
    }
    if (itemLayout == null) itemLayout = "full";
    const layout = block.type === "metric-strip" || itemLayout !== "half" ? "full" : "half";
    return `<div class="portable-block portable-layout-${layout}" data-artifact-block-id="${escapeHtml(block.id)}" data-artifact-block-type="${escapeHtml(block.type)}" data-layout="${layout}">${content}</div>`;
  }).join("\n");
  const status = surface !== "report" && snapshot.status && snapshot.status !== "ready"
    ? `<span class="portable-status">${escapeHtml(snapshot.status)}</span>`
    : "";
  const generatedAt = snapshot.generatedAt || manifest.generatedAt;

  return [
    `<main id="${FALLBACK_ROOT_ID}" class="portable-fallback" data-portable-fallback="true" data-portable-surface="${escapeHtml(surface)}">`,
    '<header class="portable-page-header">',
    `<div class="portable-page-heading"><p class="portable-surface-label">Data Analytics ${escapeHtml(surface)}</p><h1>${escapeHtml(manifest.title)}</h1>`,
    manifest.description ? `<p class="portable-description">${escapeHtml(manifest.description)}</p>` : "",
    "</div>",
    `<div class="portable-page-meta">${status}${generatedAt ? `<time datetime="${escapeHtml(generatedAt)}">${escapeHtml(formatPortableDate(generatedAt))}</time>` : ""}</div>`,
    "</header>",
    accessIssuesFallback(snapshot),
    surface === "dashboard" ? staticFiltersFallback(filters) : "",
    `<div class="portable-block-stack">${blocks}</div>`,
    sourcesFallback(asArray(payload.sources)),
    "</main>",
  ].join("");
}

function fallbackStyles() {
  return `
:root{color-scheme:light dark;--portable-canvas:#fff;--portable-surface:#fff;--portable-surface-subtle:#f7f7f7;--portable-ink:#0d0d0d;--portable-muted:#5d5d5d;--portable-tertiary:#8f8f8f;--portable-table-text:#5d5d5d;--portable-border:rgba(13,13,13,.1);--portable-accent:#0285ff;--portable-positive:#00692a;--portable-positive-bg:#edfaf2;--portable-negative:#ba2623;--portable-negative-bg:#fff0f0;--portable-warning-bg:#fff8e6;--portable-warning-border:#e7b84b;--portable-radius:16px;--portable-safe-area-top:env(safe-area-inset-top,0px);--portable-safe-area-right:env(safe-area-inset-right,0px);--portable-safe-area-bottom:env(safe-area-inset-bottom,0px);--portable-safe-area-left:env(safe-area-inset-left,0px);font-family:ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:var(--portable-canvas);color:var(--portable-ink)}
@media(prefers-color-scheme:dark){:root{--portable-canvas:#181818;--portable-surface:#212121;--portable-surface-subtle:#2a2a2a;--portable-ink:#dfdfdf;--portable-muted:#cdcdcd;--portable-tertiary:#afafaf;--portable-table-text:#cdcdcd;--portable-border:rgba(255,255,255,.12);--portable-accent:#66b5ff;--portable-positive:#79d996;--portable-positive-bg:rgba(64,180,99,.16);--portable-negative:#ff8583;--portable-negative-bg:rgba(224,74,70,.16);--portable-warning-bg:#302817;--portable-warning-border:#8b6a20}.portable-static-chart-light{display:none!important}.portable-static-chart-dark{display:block!important}}
*{box-sizing:border-box}html,body{margin:0;min-height:100%;background:var(--portable-canvas);color:var(--portable-ink)}body{position:relative;font-size:14px;line-height:1.5}a{color:var(--portable-accent)}code,pre{font-family:ui-monospace,SFMono-Regular,Menlo,monospace}pre{max-width:100%;overflow:auto;padding:12px;border:1px solid var(--portable-border);border-radius:8px;background:var(--portable-surface-subtle);font-size:12px}.portable-fallback{width:min(1120px,100%);margin:0 auto;padding:28px 24px 56px}.portable-page-header{display:flex;align-items:flex-start;justify-content:space-between;gap:24px;padding-bottom:24px;border-bottom:1px solid var(--portable-border)}.portable-page-header h1{margin:2px 0 6px;font-size:26px;line-height:1.2;font-weight:600;letter-spacing:-.02em}.portable-description{max-width:720px;margin:0;color:var(--portable-muted)}.portable-page-meta{display:flex;align-items:flex-end;flex-direction:column;gap:6px;color:var(--portable-muted);font-size:12px}.portable-status{padding:2px 8px;border:1px solid var(--portable-border);border-radius:999px;text-transform:capitalize}.portable-block-stack{display:grid;gap:20px;margin-top:24px}.portable-markdown{max-width:820px}.portable-markdown>:first-child{margin-top:0}.portable-markdown>:last-child{margin-bottom:0}.portable-markdown h1,.portable-markdown h2,.portable-markdown h3{line-height:1.25;font-weight:600}.portable-markdown h2{font-size:20px}.portable-markdown h3{font-size:16px}.portable-markdown blockquote{margin:12px 0;padding-left:14px;border-left:3px solid var(--portable-border);color:var(--portable-muted)}.portable-markdown li+li{margin-top:4px}.portable-content-card,.portable-metric-card{border:1px solid var(--portable-border);border-radius:var(--portable-radius);background:var(--portable-surface)}.portable-content-card{padding:18px}.portable-content-card h2{margin:0;font-size:16px}.portable-content-card header>p{margin:4px 0 16px;color:var(--portable-muted)}.portable-metric-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}.portable-metric-card{padding:16px}.portable-metric-value{margin:4px 0 0;font-size:28px;line-height:1.1;font-weight:600;letter-spacing:-.02em}.portable-card-description{margin:8px 0 0;color:var(--portable-muted);font-size:12px}.portable-metric-badges{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}.portable-metric-badge{padding:3px 7px;border-radius:999px;background:var(--portable-surface-subtle);font-size:11px}.portable-chart-summary{margin:0}.portable-chart-summary figcaption{display:flex;flex-direction:column;margin-bottom:14px}.portable-chart-summary figcaption span{color:var(--portable-muted);font-size:12px}.portable-static-chart{width:100%;margin:0 auto 12px;overflow:hidden;border-radius:8px;background:var(--portable-surface)}.portable-static-chart-variant>svg{display:block;width:100%;height:auto;overflow:visible;pointer-events:none}.portable-static-chart-dark{display:none}.portable-static-chart-legend-wrap{margin:8px 12px 2px;color:var(--portable-muted);font-size:12px}.portable-static-chart-legend-title{margin:0 0 5px;text-align:center;font-weight:600}.portable-static-chart-legend{display:flex;flex-wrap:wrap;justify-content:center;gap:6px 16px;margin:0;padding:0;color:var(--portable-muted);font-size:12px;list-style:none}.portable-static-chart-legend li{display:inline-flex;align-items:center;gap:6px}.portable-static-chart-legend-marker{display:inline-block;flex:0 0 auto}.portable-static-chart-legend-marker-dot{width:9px;height:9px;border-radius:999px;background:var(--portable-legend-color)}.portable-static-chart-legend-marker-line{width:18px;height:0;border-top:2px solid var(--portable-legend-color)}.portable-static-chart-legend-marker-dashed{border-top-style:dashed}.portable-chart-data{margin-top:10px}.portable-chart-data>summary{width:max-content;cursor:pointer;color:var(--portable-accent);font-size:12px;font-weight:500}.portable-chart-data[open]>summary{margin-bottom:8px}.portable-table-scroll{max-width:100%;overflow:auto;border:1px solid var(--portable-border);border-radius:8px}table{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums}caption{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}th,td{padding:9px 11px;border-bottom:1px solid var(--portable-border);text-align:left;white-space:nowrap}th{position:sticky;top:0;background:var(--portable-surface-subtle);color:var(--portable-muted);font-size:11px;font-weight:600;text-transform:uppercase}tbody tr:last-child td{border-bottom:0}.portable-empty-cell{text-align:center;color:var(--portable-muted)}.portable-table-note{margin:8px 0 0;color:var(--portable-muted);font-size:11px}.portable-notice{margin-top:20px;padding:14px 16px;border:1px solid var(--portable-warning-border);border-radius:10px;background:var(--portable-warning-bg)}.portable-notice h2{margin:0 0 6px;font-size:14px}.portable-notice ul{margin:0;padding-left:20px}.portable-custom-html{padding:0;overflow:hidden}.portable-custom-html iframe{display:block;width:100%;min-height:240px;border:0;background:var(--portable-surface)}.portable-sources{margin-top:32px;padding-top:22px;border-top:1px solid var(--portable-border)}.portable-sources h2{font-size:16px}.portable-sources ol{display:grid;gap:10px;padding-left:22px}.portable-sources li>strong{display:block}.portable-source-meta{display:block;color:var(--portable-muted);font-size:11px}.portable-sources p{margin:2px 0;color:var(--portable-muted)}.portable-sources details{margin-top:5px}.portable-sources summary{cursor:pointer;color:var(--portable-accent)}#${READER_ROOT_ID}[aria-hidden="true"]{position:absolute;inset:0;visibility:hidden;width:100%;pointer-events:none}
.portable-eyebrow{margin:0;color:var(--portable-muted);font-size:11px;font-weight:600;letter-spacing:.08em;text-transform:uppercase}
.portable-block,.portable-content-card,.portable-inline-source,.portable-inline-source-content,.portable-source-query,.portable-sources,.portable-sources ol,.portable-sources li{min-width:0}
@media screen{.portable-fallback.portable-enhanced-hidden,.portable-sources,.portable-source-summary{display:none!important}}
:root{--portable-border:rgba(13,13,13,.05)}
@media(prefers-color-scheme:dark){:root{--portable-border:rgba(255,255,255,.04);--portable-positive:#04b84c;--portable-positive-bg:rgba(4,184,76,.15);--portable-negative:#fa423e;--portable-negative-bg:rgba(250,66,62,.16)}}
.portable-fallback{width:100%;margin:0;padding:0 32px 56px}.portable-page-header{position:sticky;top:0;z-index:60;display:flex;align-items:center;justify-content:space-between;width:100vw;height:48px;min-height:48px;margin-right:calc(50% - 50vw);margin-left:calc(50% - 50vw);padding:8px 12px;border-bottom:1px solid var(--portable-border);background:var(--portable-canvas)}.portable-page-heading{min-width:0}.portable-page-header h1{margin:0;overflow:hidden;font-size:14px;font-weight:500;line-height:22px;letter-spacing:0;text-overflow:ellipsis;white-space:nowrap}.portable-page-meta{display:flex;align-items:center;flex-direction:row;gap:8px;color:var(--portable-tertiary);font-size:14px;font-weight:500;line-height:22px}.portable-description,.portable-surface-label{margin:0}.portable-fallback[data-portable-surface="report"]>.portable-block-stack,.portable-fallback[data-portable-surface="report"]>.portable-filter-bar,.portable-fallback[data-portable-surface="report"]>.portable-notice{width:100%;max-width:768px;margin-right:auto;margin-left:auto}.portable-block-stack{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:32px;margin-top:32px}.portable-layout-full{grid-column:1/-1}.portable-filter-bar{display:flex;flex-wrap:wrap;gap:8px;margin-top:24px}.portable-filter-chip{display:inline-flex;align-items:center;gap:8px;min-height:32px;padding:4px 12px;border:1px solid var(--portable-border);border-radius:999px;background:var(--portable-surface);color:var(--portable-muted);font-size:14px;line-height:20px}.portable-filter-chip strong{color:var(--portable-ink);font-weight:600}.portable-content-card{overflow:visible;padding:0;border:0;border-radius:0;background:transparent}.portable-metric-grid{grid-template-columns:repeat(auto-fit,minmax(min(100%,216px),1fr));gap:8px;align-items:start}.portable-metric-card{position:relative;overflow:visible;padding:20px;border-radius:16px}.portable-metric-label{margin:0;color:var(--portable-muted);font-size:14px;font-weight:400;line-height:20px;overflow-wrap:anywhere}.portable-metric-value{margin:4px 0 0;font-size:20px;font-weight:500;line-height:26px;letter-spacing:0;overflow-wrap:anywhere}.portable-metric-badges{gap:8px;margin-top:8px}.portable-metric-badge{display:inline-flex;flex-wrap:wrap;gap:4px;align-items:center;padding:2px 8px;border:1px solid var(--portable-border);border-radius:999px;background:var(--portable-surface-subtle);color:var(--portable-muted);font-size:12px;font-weight:500;line-height:18px}.portable-metric-badge strong{color:var(--portable-ink);font-weight:500}.portable-metric-badge.portable-positive{border-color:transparent;background:var(--portable-positive-bg);color:var(--portable-positive)}.portable-metric-badge.portable-positive *{color:inherit}.portable-metric-badge.portable-negative{border-color:transparent;background:var(--portable-negative-bg);color:var(--portable-negative)}.portable-metric-badge.portable-negative *{color:inherit}.portable-visual-header{display:block;margin:0 0 16px}.portable-visual-header>strong,.portable-visual-header h1,.portable-visual-header h2,.portable-visual-header h3{display:block;margin:0;color:var(--portable-ink);font-size:16px;font-weight:500;line-height:24px;letter-spacing:0}.portable-visual-header>span,.portable-visual-header>p,.portable-visual-header p,.portable-visual-header li{margin:0;color:var(--portable-ink);font-size:14px;font-weight:400;line-height:20px}.portable-chart-summary figcaption{display:block;margin-bottom:16px}.portable-static-chart{margin:0 auto;overflow:visible;border-radius:0;background:transparent}.portable-chart-data-has-vector{display:none}.portable-table-scroll{overflow:auto;border:0;border-radius:0}.portable-table-scroll table{width:max-content;min-width:0;table-layout:auto}.portable-table-scroll th,.portable-table-scroll td{max-width:none;overflow:hidden;border-bottom:1px solid var(--portable-border);text-overflow:ellipsis;vertical-align:top}.portable-table-scroll th{position:relative;padding:0 16px 6px 0;background:transparent;color:var(--portable-tertiary);font-size:12px;font-weight:600;line-height:18px;letter-spacing:0;text-transform:none;white-space:normal}.portable-table-scroll td{padding:8px 16px 8px 0;color:var(--portable-table-text);font-size:14px;line-height:22px;white-space:normal}.portable-table-scroll th:last-child,.portable-table-scroll td:last-child{padding-right:0}.portable-table-scroll tbody tr:last-child td{border-bottom:1px solid var(--portable-border)}.portable-table-scroll td:first-child{color:var(--portable-ink)}.portable-table-number{font-variant-numeric:tabular-nums;text-align:right}.portable-table-center{text-align:center}.portable-table-positive{color:var(--portable-positive)!important}.portable-table-negative{color:var(--portable-negative)!important}.portable-table-note{margin:12px 0 0;color:var(--portable-tertiary);font-size:12px;line-height:18px}.portable-card-description{margin:0}
.portable-chart-summary .portable-visual-header>span,.portable-content-card .portable-visual-header>p{margin:0;color:var(--portable-ink);font-size:14px;font-weight:400;line-height:20px}.portable-markdown h1,.portable-markdown h2,.portable-markdown h3{font-weight:500}.portable-table-scroll th{height:30px;padding-top:6px;padding-bottom:6px}.portable-table-scroll tbody tr:last-child td{border-bottom:0}
@media screen{.portable-description,.portable-surface-label,.portable-card-description{display:none}.portable-table-source-region{width:fit-content;max-width:100%}.portable-table-source-cell{overflow:visible!important}.portable-chart-data-has-vector{position:absolute!important;display:block!important;width:1px!important;height:1px!important;margin:-1px!important;padding:0!important;overflow:hidden!important;clip:rect(0 0 0 0)!important;clip-path:inset(50%)!important;white-space:nowrap!important;border:0!important}}
@media screen and (max-width:760px){.portable-fallback{padding:0 24px 40px}.portable-page-header{position:static;z-index:auto;display:flex;align-items:flex-start;justify-content:flex-start;flex-direction:column;width:100%;height:auto;min-height:0;margin:0;padding:24px 0 0;border-bottom:0;background:transparent;gap:4px}.portable-page-heading{width:100%}.portable-page-meta{order:-1;display:flex;align-items:center;flex-flow:row wrap;gap:6px;color:var(--portable-tertiary);font-size:11px;font-weight:600;line-height:16px;letter-spacing:.08em;text-transform:uppercase}.portable-page-meta:empty{display:none}.portable-page-meta .portable-status{display:none}.portable-page-header h1{margin:0;overflow:visible;font-size:24px;font-weight:600;line-height:30px;letter-spacing:-.02em;text-overflow:clip;white-space:normal}.portable-block-stack{grid-template-columns:minmax(0,1fr);gap:24px;margin-top:24px}.portable-layout-half,.portable-layout-full{grid-column:1}.portable-static-chart-variant{min-width:0}}
[data-portable-source-host]{position:relative}[data-portable-source-host]:hover,[data-portable-source-host]:focus,.portable-source-tooltip:hover,.portable-source-tooltip:focus{z-index:2}[data-portable-source-host]:focus,.portable-source-tooltip:focus{outline:0}[data-portable-source-host]:focus-visible,.portable-source-tooltip:focus-visible{outline:2px solid var(--portable-accent);outline-offset:2px}.portable-source-tooltip{position:relative;display:inline-block;padding:0;border:0;appearance:none;background:none;color:inherit;font:inherit;line-height:inherit;cursor:help;text-decoration:underline dotted;text-underline-offset:.18em;touch-action:manipulation}.portable-source-tooltip:focus-visible{border-radius:3px}.portable-inline-source{position:absolute;z-index:1000;inset:0;display:block;width:100%;height:100%;margin:0;padding:0;border:0;text-align:left;pointer-events:none}.portable-source-tooltip-content{position:fixed;z-index:1000;top:var(--portable-source-tooltip-top,8px);right:auto;bottom:auto;left:var(--portable-source-tooltip-left,8px);display:none;width:max-content;max-width:min(360px,calc(100vw - 16px));padding:8px 10px;overflow:visible;border-radius:8px;background:#171411;color:#fff;font-family:ui-sans-serif,system-ui,sans-serif;font-size:12px;font-style:normal;font-weight:400;line-height:1.4;overflow-wrap:anywhere;white-space:normal;text-align:left;text-decoration:none;box-shadow:0 8px 24px rgba(23,20,17,.2);transform:none;opacity:0;visibility:hidden;pointer-events:none}.portable-source-tooltip-content,.portable-source-tooltip-content *{color:#fff!important;font-style:normal!important;text-decoration:none!important}.portable-source-tooltip-heading{display:none}.portable-source-context{display:block;margin-bottom:6px}.portable-source-tooltip-content>strong,.portable-source-tooltip-content>.portable-source-meta{display:block}.portable-source-tooltip-content>.portable-source-meta{color:#fff;font-size:12px}.portable-source-description-data,.portable-source-query-data{display:none!important}html:not([data-portable-source-tooltips-ready]) .portable-source-tooltip-content{position:absolute;top:auto;right:auto;bottom:calc(100% + 8px);left:50%;max-width:min(360px,80vw);transform:translateX(-50%)}.portable-source-tooltip:hover>.portable-source-tooltip-content,.portable-source-tooltip:focus>.portable-source-tooltip-content,.portable-source-tooltip:focus-within>.portable-source-tooltip-content,[data-portable-source-host]:hover>.portable-inline-source>.portable-source-tooltip-content,[data-portable-source-host]:focus>.portable-inline-source>.portable-source-tooltip-content,[data-portable-source-host]:focus-within>.portable-inline-source>.portable-source-tooltip-content{display:block;opacity:1;visibility:visible}
html:not([data-portable-source-tooltips-ready]) .portable-chart-summary>.portable-inline-source{position:sticky;inset:auto;top:56px;width:100%;height:0;margin:0}html:not([data-portable-source-tooltips-ready]) .portable-chart-summary>.portable-inline-source>.portable-source-tooltip-content{position:absolute;top:8px;right:0;bottom:auto;left:0;margin-inline:auto;max-width:min(360px,calc(100vw - 32px));transform:none}
@media screen and (min-width:601px){html:not([data-portable-source-tooltips-ready]) .portable-table-scroll:has(.portable-source-tooltip:hover),html:not([data-portable-source-tooltips-ready]) .portable-table-scroll:has(.portable-source-tooltip:focus){overflow:visible}}
@media screen and (hover:hover) and (pointer:fine){.portable-source-tooltip:focus:not(:focus-visible):not(:hover)>.portable-source-tooltip-content,[data-portable-source-host]:focus:not(:focus-visible):not(:hover)>.portable-inline-source>.portable-source-tooltip-content{display:none;opacity:0;visibility:hidden}.portable-source-tooltip:focus-visible>.portable-source-tooltip-content,[data-portable-source-host]:focus-visible>.portable-inline-source>.portable-source-tooltip-content{display:block;opacity:1;visibility:visible}}
@media(min-width:601px){.portable-source-tooltip-heading{display:none}}
.portable-source-tooltip-content[data-portable-source-tooltip-mobile-portaled]{position:fixed;z-index:1000;top:auto;right:calc(16px + var(--portable-safe-area-right));bottom:calc(16px + var(--portable-safe-area-bottom));left:calc(16px + var(--portable-safe-area-left));display:block;width:auto;max-width:none;max-height:min(40vh,280px);max-height:min(40dvh,280px,calc(100dvh - var(--portable-safe-area-top) - var(--portable-safe-area-bottom) - 32px));padding:14px 16px;overflow-y:auto;border-radius:14px;font-size:14px;line-height:1.45;transform:none;opacity:1;visibility:visible;pointer-events:auto}.portable-source-tooltip-content[data-portable-source-tooltip-mobile-portaled][data-portable-source-tooltip-mobile-positioned]{top:var(--portable-source-tooltip-mobile-top);right:auto;bottom:auto;left:var(--portable-source-tooltip-mobile-left);width:var(--portable-source-tooltip-mobile-width);max-height:var(--portable-source-tooltip-mobile-max-height)}
@media screen and (max-width:600px){html:not([data-portable-source-tooltips-ready]) .portable-table-scroll:focus-within{overflow:visible}html:not([data-portable-source-tooltips-ready]) td.portable-table-source-cell:focus-within{overflow:visible!important}.portable-source-tooltip:hover>.portable-source-tooltip-content,.portable-source-tooltip:focus>.portable-source-tooltip-content,.portable-source-tooltip:focus-within>.portable-source-tooltip-content,[data-portable-source-host]:hover>.portable-inline-source>.portable-source-tooltip-content,[data-portable-source-host]:focus>.portable-inline-source>.portable-source-tooltip-content,[data-portable-source-host]:focus-within>.portable-inline-source>.portable-source-tooltip-content{display:none;opacity:0;visibility:hidden}.portable-source-tooltip[data-portable-source-tooltip-open]>.portable-source-tooltip-content,[data-portable-source-host][data-portable-source-tooltip-open]>.portable-inline-source>.portable-source-tooltip-content,html:not([data-portable-source-tooltips-ready]) .portable-source-tooltip:focus>.portable-source-tooltip-content,html:not([data-portable-source-tooltips-ready]) [data-portable-source-host]:focus>.portable-inline-source>.portable-source-tooltip-content{position:fixed;z-index:1000;top:auto;right:calc(16px + var(--portable-safe-area-right));bottom:calc(16px + var(--portable-safe-area-bottom));left:calc(16px + var(--portable-safe-area-left));display:block;width:auto;max-width:none;max-height:min(40vh,280px);max-height:min(40dvh,280px,calc(100dvh - var(--portable-safe-area-top) - var(--portable-safe-area-bottom) - 32px));padding:14px 16px;overflow-y:auto;border-radius:14px;font-size:14px;line-height:1.45;transform:none;opacity:1;visibility:visible;pointer-events:auto}.portable-source-tooltip[data-portable-source-tooltip-mobile-positioned]>.portable-source-tooltip-content,[data-portable-source-host][data-portable-source-tooltip-mobile-positioned]>.portable-inline-source>.portable-source-tooltip-content{top:var(--portable-source-tooltip-mobile-top);right:auto;bottom:auto;left:var(--portable-source-tooltip-mobile-left);width:var(--portable-source-tooltip-mobile-width);max-height:var(--portable-source-tooltip-mobile-max-height)}.portable-source-tooltip-heading{display:block;margin-bottom:6px;font-weight:600}}
@media print{#${READER_ROOT_ID}{display:none!important}.portable-fallback{display:block!important;width:100%;padding:0}.portable-sources{display:none!important}.portable-static-chart{overflow:visible}.portable-static-chart-variant{min-width:0}.portable-static-chart-light{display:block!important}.portable-static-chart-dark{display:none!important}.portable-content-card,.portable-metric-card{break-inside:avoid}.portable-custom-html iframe{min-height:320px}}
@media print{:root{color-scheme:light;--portable-canvas:#fff;--portable-surface:#fff;--portable-surface-subtle:#f7f7f7;--portable-ink:#0d0d0d;--portable-muted:#5d5d5d;--portable-tertiary:#8f8f8f;--portable-table-text:#5d5d5d;--portable-border:rgba(13,13,13,.1);--portable-positive:#00692a;--portable-negative:#ba2623}html,body{background:#fff!important;color:#0d0d0d!important}.portable-page-header{position:static;width:auto;height:auto;min-height:0;margin:0 0 24px;padding:0 0 16px;align-items:flex-start}.portable-page-header h1{margin:2px 0 6px;font-size:24px;line-height:1.2;white-space:normal}.portable-surface-label,.portable-description,.portable-card-description{display:block}.portable-page-meta{font-size:12px}.portable-block-stack{display:grid;grid-template-columns:minmax(0,1fr);gap:20px;margin-top:24px}.portable-layout-half,.portable-layout-full{grid-column:1}.portable-filter-bar{margin-top:0}}
@media print{.portable-source-tooltip{cursor:inherit;text-decoration:none}.portable-source-tooltip>.portable-source-tooltip-content,.portable-source-tooltip-content[data-portable-source-tooltip-mobile-portaled]{display:none!important}.portable-inline-source{position:static!important;inset:auto!important;display:block!important;width:auto!important;height:auto!important;margin-top:8px!important;padding-top:6px!important;text-align:left!important}.portable-source-tooltip-content,.portable-source-summary-content{position:static!important;inset:auto!important;display:block!important;width:auto!important;max-width:none!important;max-height:none!important;padding:0!important;overflow:visible!important;background:transparent!important;box-shadow:none!important;transform:none!important;opacity:1!important;visibility:visible!important;pointer-events:none!important}.portable-source-tooltip-content,.portable-source-tooltip-content *,.portable-source-summary-content,.portable-source-summary-content *{color:var(--portable-muted)!important}.portable-source-tooltip-heading,.portable-source-context{display:none!important}}
@media print{:root{--portable-border:rgba(13,13,13,.05)}}
`;
}

export function encodeCompressedText(value) {
  return gzipSync(Buffer.from(String(value), "utf8"), { level: 9, mtime: 0 }).toString("base64");
}

function wrappedBase64(value) {
  return value.match(/.{1,76}/g)?.join("\n") ?? "";
}

function decodeCompressedText(value) {
  const encoded = String(value).replace(/\s/g, "");
  if (
    !encoded
    || encoded.length % 4 !== 0
    || !/^[A-Za-z0-9+/]+={0,2}$/.test(encoded)
  ) {
    throw new Error("Compressed text is not canonical base64.");
  }
  const buffer = Buffer.from(encoded, "base64");
  if (buffer.toString("base64") !== encoded) {
    throw new Error("Compressed text is not canonical base64.");
  }
  return gunzipSync(buffer).toString("utf8");
}

export function assertPortableReaderRuntime(runtimeHtml) {
  if (!runtimeHtml.trim()) throw new Error("Portable artifact reader runtime is empty.");
  if (/Redirecting to the local widget source|window\.location\.replace\(target\)/i.test(runtimeHtml)) {
    throw new Error("Portable artifact reader asset is still a development redirect; run npm run build.");
  }
  const forbidden = [
    [/<script\b[^>]*\bsrc\s*=/i, "external script"],
    [/<link\b[^>]*\bhref\s*=/i, "external stylesheet"],
    [/\bwindow\.openai\b/i, "window.openai"],
    [/@modelcontextprotocol\/ext-apps/i, "MCP host dependency"],
    [/\/api\/(?:manifest|snapshot|package|source|inline-chart-widget)/i, "artifact API dependency"],
    [/\bfetch\s*\(/i, "network fetch"],
    [/\bXMLHttpRequest\b|\bEventSource\b|\bWebSocket\b/i, "network client"],
    [/\b(?:localStorage|sessionStorage|indexedDB)\b/i, "browser storage dependency"],
    [/\bnavigator\.sendBeacon\b/i, "beacon client"],
    [/(?:\bwindow\.)?\blocation\.(?:assign|replace)\s*\(/i, "top-level navigation"],
    [/\bwindow\.open\s*\(/i, "window navigation"],
  ];
  for (const [pattern, label] of forbidden) {
    if (pattern.test(runtimeHtml)) {
      throw new Error(`Portable artifact reader runtime contains a forbidden ${label}.`);
    }
  }
  if (!runtimeHtml.includes(READER_READY_EVENT)) {
    throw new Error(`Portable artifact reader runtime must dispatch ${READER_READY_EVENT} after its first render.`);
  }
}

export function readPackagedReaderRuntime() {
  const prefix = `${READER_ASSET}.gz.b64.part`;
  const parts = readdirSync(assetDirectory).filter((name) => name.startsWith(prefix)).sort();
  if (!parts.length) {
    throw new Error(
      `Portable artifact reader bundle parts are missing for ${READER_ASSET}; use the packaged plugin or run npm run build.`,
    );
  }
  const encoded = parts.map((name) => readFileSync(resolve(assetDirectory, name), "utf8").trim()).join("");
  let html;
  try {
    html = decodeCompressedText(encoded);
  } catch (error) {
    throw new Error(`Portable artifact reader bundle parts are corrupt: ${error.message}`);
  }
  assertPortableReaderRuntime(html);
  return { encoded, html, parts };
}

export function preparePortablePayload(input) {
  const validation = server.callTool("validate_artifact", input);
  const canonical = validation?.artifact_payload;
  if (!canonical || typeof canonical !== "object") {
    throw new Error("validate_artifact did not return an artifact_payload.");
  }
  const payload = cloneJson(canonical);
  assertPortableProvenanceSafe(payload);
  const packageInfo = {
    artifactRuntime: READER_ASSET,
    deliveryMode: "portable_html",
    hostedReadOnly: true,
    mode: "portable_html",
    portableHtml: true,
    readOnly: true,
    controls: { ...READ_ONLY_CONTROLS },
  };
  payload.package_info = packageInfo;
  payload.packageInfo = packageInfo;
  return payload;
}

function runtimeLoaderScript() {
  return `(() => {
  const RUNTIME_STYLE_ATTRIBUTE = "data-data-analytics-portable-runtime-style";
  const fallback = document.getElementById(${JSON.stringify(FALLBACK_ROOT_ID)});
  const reader = document.getElementById(${JSON.stringify(READER_ROOT_ID)});
  const payloadSource = document.getElementById(${JSON.stringify(PAYLOAD_SOURCE_ID)});
  const runtimeSource = document.getElementById(${JSON.stringify(RUNTIME_SOURCE_ID)});
  const state = document.documentElement.dataset;
  state.dataAnalyticsPortableReader = "fallback";

  if (fallback) fallback.classList.remove("portable-enhanced-hidden");
  if (reader) {
    reader.setAttribute("aria-hidden", "true");
    reader.setAttribute("inert", "");
  }

  if (!fallback || !reader || !(payloadSource instanceof HTMLTemplateElement) || !(runtimeSource instanceof HTMLTemplateElement)) {
    state.dataAnalyticsPortableReader = "missing-runtime";
    return;
  }
  if (typeof DecompressionStream !== "function") {
    state.dataAnalyticsPortableReader = "unsupported";
    return;
  }

  async function decompress(source) {
    const encoded = source.content.textContent.replace(/\\s/g, "");
    const binary = atob(encoded);
    const bytes = new Uint8Array(binary.length);
    for (let index = 0; index < binary.length; index += 1) bytes[index] = binary.charCodeAt(index);
    const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream("gzip"));
    return new Response(stream).text();
  }

  let revealed = false;
  function revealReader() {
    if (revealed) return;
    revealed = true;
    requestAnimationFrame(() => requestAnimationFrame(() => {
      fallback.classList.add("portable-enhanced-hidden");
      reader.removeAttribute("aria-hidden");
      reader.removeAttribute("inert");
      state.dataAnalyticsPortableReader = "ready";
    }));
  }
  window.addEventListener(${JSON.stringify(READER_READY_EVENT)}, revealReader, { once: true });
  document.addEventListener(${JSON.stringify(READER_READY_EVENT)}, revealReader, { once: true });

  async function boot() {
    try {
      const [payloadText, runtimeHtml] = await Promise.all([
        decompress(payloadSource),
        decompress(runtimeSource),
      ]);
      window[${JSON.stringify(PAYLOAD_GLOBAL)}] = JSON.parse(payloadText);

      const runtimeDocument = new DOMParser().parseFromString(runtimeHtml, "text/html");
      const parserError = runtimeDocument.querySelector("parsererror");
      if (parserError) throw new Error("Portable reader runtime could not be parsed.");
      const scripts = Array.from(runtimeDocument.querySelectorAll("script"));
      if (scripts.some((script) => script.hasAttribute("src"))) {
        throw new Error("Portable reader runtime contains an external script.");
      }
      for (const script of scripts) script.remove();
      for (const style of document.head.querySelectorAll("style[" + RUNTIME_STYLE_ATTRIBUTE + "]")) {
        style.remove();
      }
      for (const style of runtimeDocument.querySelectorAll("style")) {
        const runtimeStyle = document.importNode(style, true);
        runtimeStyle.setAttribute(RUNTIME_STYLE_ATTRIBUTE, "true");
        document.head.append(runtimeStyle);
      }
      reader.replaceChildren(...Array.from(runtimeDocument.body.childNodes, (node) => document.importNode(node, true)));
      reader.dataset.portableArtifactReader = "true";
      state.dataAnalyticsPortableReader = "loading";

      for (const original of scripts) {
        const script = document.createElement("script");
        for (const attribute of original.attributes) script.setAttribute(attribute.name, attribute.value);
        script.textContent = original.textContent;
        const removeRuntimeScript = () => {
          window.removeEventListener(${JSON.stringify(READER_READY_EVENT)}, removeRuntimeScript);
          document.removeEventListener(${JSON.stringify(READER_READY_EVENT)}, removeRuntimeScript);
          script.remove();
        };
        window.addEventListener(${JSON.stringify(READER_READY_EVENT)}, removeRuntimeScript, { once: true });
        document.addEventListener(${JSON.stringify(READER_READY_EVENT)}, removeRuntimeScript, { once: true });
        script.addEventListener("load", removeRuntimeScript, { once: true });
        script.addEventListener("error", removeRuntimeScript, { once: true });
        document.head.append(script);
      }
    } catch (error) {
      state.dataAnalyticsPortableReader = "failed";
      console.warn("Portable Data Analytics reader could not start; keeping semantic fallback.", error);
    }
  }

  function scheduleBoot() {
    requestAnimationFrame(() => window.setTimeout(() => void boot(), 0));
  }
  if (document.readyState === "complete") scheduleBoot();
  else window.addEventListener("load", scheduleBoot, { once: true });
})();`;
}

function staticSourceTooltipRuntimeScript() {
  return `(() => {
  const RUNTIME_FLAG = "__dataAnalyticsPortableSourceTooltipsInitialized";
  const READY_ATTRIBUTE = "data-portable-source-tooltips-ready";
  const OPEN_ATTRIBUTE = "data-portable-source-tooltip-open";
  const MOBILE_POSITIONED_ATTRIBUTE = "data-portable-source-tooltip-mobile-positioned";
  const MOBILE_PORTALED_ATTRIBUTE = "data-portable-source-tooltip-mobile-portaled";
  const HOST_SELECTOR = "[data-portable-source-host]";
  const DISCOVERABLE_SELECTOR = ".portable-source-tooltip";
  const CONTENT_SELECTOR = ".portable-source-tooltip-content";
  const INTERACTIVE_SELECTOR = "a,button,input,select,textarea,summary,details,[role='button'],[contenteditable='true']";
  const GAP = 8;
  const MOBILE_VIEWPORT_PADDING = 16;
  const MOBILE_MAX_WIDTH = 600;
  const SCROLL_DISMISS_THRESHOLD = 24;
  const VIEWPORT_PADDING = 8;
  const fallback = document.querySelector("[data-portable-fallback]");

  if (window[RUNTIME_FLAG]) return;

  let activeHost = null;
  let activeTooltipOrigin = null;
  let mobileTrayScrollY = 0;
  let placementFrame = 0;

  function viewportBounds() {
    const viewport = window.visualViewport;
    return {
      bottom: (viewport?.offsetTop ?? 0) + (viewport?.height ?? window.innerHeight),
      left: viewport?.offsetLeft ?? 0,
      right: (viewport?.offsetLeft ?? 0) + (viewport?.width ?? window.innerWidth),
      top: viewport?.offsetTop ?? 0,
    };
  }

  function usesMobileTray() {
    return (window.visualViewport?.width ?? window.innerWidth) <= MOBILE_MAX_WIDTH;
  }

  function clampAxis(value, size, start, end) {
    const minimum = start + VIEWPORT_PADDING;
    const maximum = Math.max(minimum, end - size - VIEWPORT_PADDING);
    return Math.min(Math.max(value, minimum), maximum);
  }

  function rootPixelValue(property) {
    const value = Number.parseFloat(getComputedStyle(document.documentElement).getPropertyValue(property));
    return Number.isFinite(value) ? Math.max(0, value) : 0;
  }

  function tooltipForHost(host) {
    if (!(host instanceof HTMLElement)) return null;
    for (const tooltipId of String(host.getAttribute("aria-describedby") ?? "").split(/\\s+/u).filter(Boolean)) {
      const describedTooltip = document.getElementById(tooltipId);
      if (describedTooltip instanceof HTMLElement && describedTooltip.matches(CONTENT_SELECTOR)) {
        return describedTooltip;
      }
    }
    const direct = Array.from(host.children).find((child) => child.matches(CONTENT_SELECTOR));
    if (direct instanceof HTMLElement) return direct;
    const wrapper = Array.from(host.children).find((child) => child.classList.contains("portable-inline-source"));
    const wrapped = wrapper?.querySelector(":scope > " + CONTENT_SELECTOR);
    return wrapped instanceof HTMLElement ? wrapped : null;
  }

  function restoreMobileTooltip() {
    const origin = activeTooltipOrigin;
    activeTooltipOrigin = null;
    if (!origin) return;
    const { nextSibling, parent, tooltip } = origin;
    tooltip.removeAttribute(MOBILE_PORTALED_ATTRIBUTE);
    tooltip.removeAttribute(MOBILE_POSITIONED_ATTRIBUTE);
    if (nextSibling?.parentNode === parent) parent.insertBefore(tooltip, nextSibling);
    else parent.appendChild(tooltip);
  }

  function portalMobileTooltip(host) {
    if (!(fallback instanceof HTMLElement)) return null;
    const tooltip = tooltipForHost(host);
    if (!(tooltip instanceof HTMLElement)) return null;
    if (activeTooltipOrigin?.tooltip === tooltip) return tooltip;
    restoreMobileTooltip();
    const parent = tooltip.parentNode;
    if (!parent) return null;
    activeTooltipOrigin = { nextSibling: tooltip.nextSibling, parent, tooltip };
    tooltip.setAttribute(MOBILE_PORTALED_ATTRIBUTE, "true");
    fallback.appendChild(tooltip);
    return tooltip;
  }

  function clearMobilePlacement(host) {
    if (!(host instanceof HTMLElement)) return;
    host.removeAttribute(MOBILE_POSITIONED_ATTRIBUTE);
    const tooltip = tooltipForHost(host);
    if (!(tooltip instanceof HTMLElement)) return;
    tooltip.removeAttribute(MOBILE_POSITIONED_ATTRIBUTE);
    for (const property of [
      "--portable-source-tooltip-mobile-left",
      "--portable-source-tooltip-mobile-max-height",
      "--portable-source-tooltip-mobile-top",
      "--portable-source-tooltip-mobile-width",
    ]) {
      tooltip.style.removeProperty(property);
    }
  }

  function placeMobileTray(host) {
    const tooltip = tooltipForHost(host);
    if (!(tooltip instanceof HTMLElement)) return;
    const viewport = viewportBounds();
    const leftPadding = MOBILE_VIEWPORT_PADDING + rootPixelValue("--portable-safe-area-left");
    const rightPadding = MOBILE_VIEWPORT_PADDING + rootPixelValue("--portable-safe-area-right");
    const topPadding = MOBILE_VIEWPORT_PADDING + rootPixelValue("--portable-safe-area-top");
    const bottomPadding = MOBILE_VIEWPORT_PADDING + rootPixelValue("--portable-safe-area-bottom");
    const left = viewport.left + leftPadding;
    const right = Math.max(left + 1, viewport.right - rightPadding);
    const topBoundary = viewport.top + topPadding;
    const bottom = Math.max(topBoundary + 1, viewport.bottom - bottomPadding);
    const width = Math.max(1, right - left);
    const availableHeight = Math.max(1, bottom - topBoundary);
    const maxHeight = Math.max(1, Math.min(280, availableHeight * 0.4));

    tooltip.style.setProperty("--portable-source-tooltip-mobile-left", String(Math.round(left)) + "px");
    tooltip.style.setProperty("--portable-source-tooltip-mobile-max-height", String(Math.round(maxHeight)) + "px");
    tooltip.style.setProperty("--portable-source-tooltip-mobile-top", String(Math.round(topBoundary)) + "px");
    tooltip.style.setProperty("--portable-source-tooltip-mobile-width", String(Math.round(width)) + "px");
    host.setAttribute(MOBILE_POSITIONED_ATTRIBUTE, "true");
    tooltip.setAttribute(MOBILE_POSITIONED_ATTRIBUTE, "true");

    const tooltipHeight = Math.min(tooltip.getBoundingClientRect().height, maxHeight);
    const top = Math.max(topBoundary, bottom - tooltipHeight);
    tooltip.style.setProperty("--portable-source-tooltip-mobile-top", String(Math.round(top)) + "px");
  }

  function placeTooltip(host) {
    if (!(host instanceof HTMLElement)) return;
    if (usesMobileTray()) {
      placeMobileTray(host);
      return;
    }
    clearMobilePlacement(host);
    const tooltip = tooltipForHost(host);
    if (!(tooltip instanceof HTMLElement)) return;

    const hostRect = host.getBoundingClientRect();
    const tooltipRect = tooltip.getBoundingClientRect();
    if (!tooltipRect.width || !tooltipRect.height) return;
    const viewport = viewportBounds();
    const centeredLeft = hostRect.left + (hostRect.width - tooltipRect.width) / 2;
    const aboveTop = hostRect.top - tooltipRect.height - GAP;
    const belowTop = hostRect.bottom + GAP;
    const preferredTop = aboveTop < viewport.top + VIEWPORT_PADDING ? belowTop : aboveTop;
    const left = clampAxis(centeredLeft, tooltipRect.width, viewport.left, viewport.right);
    const top = clampAxis(preferredTop, tooltipRect.height, viewport.top, viewport.bottom);

    tooltip.style.setProperty("--portable-source-tooltip-left", String(Math.round(left)) + "px");
    tooltip.style.setProperty("--portable-source-tooltip-top", String(Math.round(top)) + "px");
  }

  function closeMobileTray({ restoreFocus = false } = {}) {
    if (placementFrame) {
      window.cancelAnimationFrame(placementFrame);
      placementFrame = 0;
    }
    const host = activeHost;
    if (!(host instanceof HTMLElement)) {
      restoreMobileTooltip();
      return;
    }
    host.removeAttribute(OPEN_ATTRIBUTE);
    clearMobilePlacement(host);
    restoreMobileTooltip();
    if (usesMobileTray() && host.matches(DISCOVERABLE_SELECTOR)) host.setAttribute("aria-expanded", "false");
    activeHost = null;
    if (restoreFocus) host.focus({ preventScroll: true });
  }

  function openMobileTray(host) {
    if (!(host instanceof HTMLElement) || !(tooltipForHost(host) instanceof HTMLElement)) return;
    if (activeHost && activeHost !== host) closeMobileTray();
    activeHost = host;
    mobileTrayScrollY = window.scrollY;
    portalMobileTooltip(host);
    host.setAttribute(OPEN_ATTRIBUTE, "true");
    if (host.matches(DISCOVERABLE_SELECTOR)) host.setAttribute("aria-expanded", "true");
    schedulePlacement(host);
  }

  function toggleMobileTray(host) {
    if (activeHost === host && host.getAttribute(OPEN_ATTRIBUTE) === "true") closeMobileTray();
    else openMobileTray(host);
  }

  function syncSemantics() {
    const isMobile = usesMobileTray();
    document.querySelectorAll(DISCOVERABLE_SELECTOR).forEach((host) => {
      if (!(host instanceof HTMLElement)) return;
      if (isMobile) {
        if (!host.hasAttribute("role")) {
          host.setAttribute("role", "button");
          host.setAttribute("data-portable-source-tooltip-runtime-role", "true");
        }
        host.setAttribute("aria-expanded", host.getAttribute(OPEN_ATTRIBUTE) === "true" ? "true" : "false");
      } else {
        if (host.getAttribute("data-portable-source-tooltip-runtime-role") === "true") {
          host.removeAttribute("role");
          host.removeAttribute("data-portable-source-tooltip-runtime-role");
        }
        host.removeAttribute("aria-expanded");
      }
    });
  }

  function schedulePlacement(host = activeHost) {
    if (!(host instanceof HTMLElement)) return;
    activeHost = host;
    if (placementFrame) window.cancelAnimationFrame(placementFrame);
    placementFrame = window.requestAnimationFrame(() => {
      placementFrame = 0;
      placeTooltip(host);
    });
  }

  function eventHost(event) {
    const target = event.target;
    if (!(target instanceof Element) || !(fallback instanceof HTMLElement)) return null;
    let host = target.closest(HOST_SELECTOR);
    if (!(host instanceof HTMLElement) && usesMobileTray()) {
      const cell = target.closest("td.portable-table-source-cell");
      host = cell?.querySelector(":scope > " + HOST_SELECTOR) ?? null;
    }
    return host instanceof HTMLElement && fallback.contains(host) ? host : null;
  }

  function isNestedInteractive(target, host) {
    if (!(target instanceof Element) || !(host instanceof HTMLElement)) return false;
    const interactive = target.closest(INTERACTIVE_SELECTOR);
    return interactive instanceof HTMLElement && interactive !== host && host.contains(interactive);
  }

  function handlePointerDown(event) {
    if (!usesMobileTray() || !(activeHost instanceof HTMLElement)) return;
    const target = event.target;
    if (!(target instanceof Element) || target.closest(CONTENT_SELECTOR)) return;
    if (eventHost(event) === activeHost) return;
    closeMobileTray();
  }

  function handleClick(event) {
    if (!usesMobileTray()) return;
    const target = event.target;
    if (!(target instanceof Element)) return;
    if (!(fallback instanceof HTMLElement) || !fallback.contains(target)) {
      closeMobileTray();
      return;
    }
    if (target.closest(CONTENT_SELECTOR)) return;
    const host = eventHost(event);
    if (host instanceof HTMLElement) {
      if (isNestedInteractive(target, host)) return;
      event.preventDefault();
      event.stopPropagation();
      if (document.activeElement !== host) host.focus({ preventScroll: true });
      toggleMobileTray(host);
      return;
    }
    closeMobileTray();
  }

  function handleKeydown(event) {
    if (!usesMobileTray()) return;
    if (event.key === "Escape") {
      closeMobileTray({ restoreFocus: true });
      return;
    }
    if (event.key !== "Enter" && event.key !== " ") return;
    const host = eventHost(event);
    if (!(host instanceof HTMLElement) || isNestedInteractive(event.target, host)) return;
    event.preventDefault();
    toggleMobileTray(host);
  }

  function handleFocusIn(event) {
    const host = eventHost(event);
    if (!usesMobileTray()) schedulePlacement(host);
  }

  function handleScroll() {
    if (usesMobileTray()) {
      if (activeHost && Math.abs(window.scrollY - mobileTrayScrollY) >= SCROLL_DISMISS_THRESHOLD) closeMobileTray();
      return;
    }
    schedulePlacement();
  }

  function handleViewportChange() {
    syncSemantics();
    if (!usesMobileTray() && activeHost?.getAttribute(OPEN_ATTRIBUTE) === "true") {
      closeMobileTray();
      return;
    }
    if (usesMobileTray()) {
      if (activeHost?.getAttribute(OPEN_ATTRIBUTE) === "true") schedulePlacement(activeHost);
      else activeHost = null;
      return;
    }
    schedulePlacement();
  }

  function setup() {
    if (!(fallback instanceof HTMLElement)) throw new Error("Portable fallback root is missing.");
    syncSemantics();
    document.addEventListener("pointerover", (event) => {
      if (!usesMobileTray()) schedulePlacement(eventHost(event));
    }, true);
    document.addEventListener("pointerdown", handlePointerDown, true);
    document.addEventListener("click", handleClick, true);
    document.addEventListener("focusin", handleFocusIn);
    document.addEventListener("keydown", handleKeydown);
    document.addEventListener("scroll", handleScroll, true);
    window.addEventListener("resize", handleViewportChange);
    window.visualViewport?.addEventListener("resize", handleViewportChange);
    window.visualViewport?.addEventListener("scroll", handleViewportChange);
    window.addEventListener("beforeprint", () => closeMobileTray());
    window.addEventListener(${JSON.stringify(READER_READY_EVENT)}, () => closeMobileTray(), { once: true });
    document.addEventListener(${JSON.stringify(READER_READY_EVENT)}, () => closeMobileTray(), { once: true });

    const currentHost = document.querySelector(HOST_SELECTOR + ":hover, " + HOST_SELECTOR + ":focus");
    if (!usesMobileTray() && currentHost instanceof HTMLElement) schedulePlacement(currentHost);
  }

  try {
    setup();
    window[RUNTIME_FLAG] = true;
    document.documentElement.setAttribute(READY_ATTRIBUTE, "true");
  } catch (error) {
    console.warn("Portable source tooltips could not start; keeping the CSS fallback.", error);
  }
})();`;
}

function htmlDocument({ payload, payloadEncoded, runtimeEncoded, fallback }) {
  const title = escapeHtml(payload.manifest?.title || "Data Analytics artifact");
  const contentSecurityPolicy = [
    "default-src 'none'",
    "img-src data: blob:",
    "font-src data:",
    "style-src 'unsafe-inline'",
    "script-src 'unsafe-inline' blob:",
    "connect-src 'none'",
    "media-src data: blob:",
    "worker-src blob:",
    "frame-src 'self' data: blob:",
    "object-src 'none'",
    "base-uri 'none'",
    "form-action 'none'",
  ].join("; ");
  return `<!doctype html>
<html lang="en" data-data-analytics-portable-artifact="true">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta name="color-scheme" content="light dark" />
<meta http-equiv="Content-Security-Policy" content="${escapeHtml(contentSecurityPolicy)}" />
<meta name="referrer" content="no-referrer" />
<title>${title}</title>
<style data-data-analytics-portable-fallback="true">${fallbackStyles()}</style>
</head>
<body>
${fallback}
<script data-data-analytics-portable-source-tooltips="true">${staticSourceTooltipRuntimeScript()}</script>
<div id="${READER_ROOT_ID}" aria-hidden="true" inert></div>
<template id="${PAYLOAD_SOURCE_ID}" data-compression="gzip-base64">
${wrappedBase64(payloadEncoded)}
</template>
<template id="${RUNTIME_SOURCE_ID}" data-compression="gzip-base64">
${wrappedBase64(runtimeEncoded)}
</template>
<script data-data-analytics-portable-loader="true">${runtimeLoaderScript()}</script>
</body>
</html>
`;
}

export function buildPortableArtifact(input, options = {}) {
  const payload = preparePortablePayload(input);
  let runtimeHtml = options.runtimeHtml;
  const suppliedRuntimeEncoded = options.runtimeEncoded;
  if (runtimeHtml == null && suppliedRuntimeEncoded == null) {
    const packaged = readPackagedReaderRuntime();
    runtimeHtml = packaged.html;
  } else if (runtimeHtml == null) {
    runtimeHtml = decodeCompressedText(suppliedRuntimeEncoded);
  } else if (suppliedRuntimeEncoded != null) {
    const decodedRuntime = decodeCompressedText(suppliedRuntimeEncoded);
    if (decodedRuntime !== runtimeHtml) {
      throw new Error("runtimeHtml and runtimeEncoded must decode to identical runtime HTML.");
    }
  }
  assertPortableReaderRuntime(runtimeHtml);
  const runtimeEncoded = encodeCompressedText(runtimeHtml);
  const payloadJson = JSON.stringify(payload);
  const payloadEncoded = encodeCompressedText(payloadJson);
  const fallback = semanticFallback(payload, { staticCharts: options.staticCharts });
  return htmlDocument({ payload, payloadEncoded, runtimeEncoded, fallback });
}

function usage() {
  return `Usage: node ${fileURLToPath(import.meta.url)} --input artifact.json --output report.html`;
}

function parseArguments(argv) {
  const parsed = {};
  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === "--help" || argument === "-h") return { help: true };
    if (argument !== "--input" && argument !== "--output") {
      throw new Error(`Unknown argument: ${argument}\n${usage()}`);
    }
    const value = argv[index + 1];
    if (!value || value.startsWith("--")) {
      throw new Error(`${argument} requires a path.\n${usage()}`);
    }
    const key = argument.slice(2);
    if (parsed[key]) throw new Error(`${argument} may only be specified once.`);
    parsed[key] = value;
    index += 1;
  }
  if (!parsed.input || !parsed.output) throw new Error(`--input and --output are required.\n${usage()}`);
  return parsed;
}

export function runCli(argv = process.argv.slice(2)) {
  const options = parseArguments(argv);
  if (options.help) {
    process.stdout.write(`${usage()}\n`);
    return;
  }
  const inputPath = resolve(options.input);
  const outputPath = resolve(options.output);
  let input;
  try {
    input = JSON.parse(readFileSync(inputPath, "utf8"));
  } catch (error) {
    throw new Error(`Could not read artifact input ${inputPath}: ${error.message}`);
  }
  const html = buildPortableArtifact(input);
  mkdirSync(dirname(outputPath), { recursive: true });
  writeFileSync(outputPath, html, "utf8");
  process.stdout.write(`Wrote ${outputPath} as a validated, self-contained Data Analytics HTML artifact.\n`);
}

const isMain = process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url;
if (isMain) {
  try {
    runCli();
  } catch (error) {
    process.stderr.write(`${error?.message || String(error)}\n`);
    process.exitCode = 1;
  }
}
