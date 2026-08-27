import React, { StrictMode, useEffect, useLayoutEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";

import pluginManifest from "../.codex-plugin/plugin.json";
import { connectMcpWidgetHost } from "./mcp-host.js";
import AnalyticsApp from "./analytics-app/App";
import "./styles/codex-theme.css";
import "./analytics-app/tokens.css";
import "./analytics-app/charting/chart-tokens.css";
import "./analytics-app/styles.css";

const CHART_WIDGET_RESOURCE_URI =
  `ui://widget/datascience-chart-${encodeURIComponent(pluginManifest.version)}.html`;
const ARTIFACT_BLOCK_TYPES = new Set(["markdown", "metric-strip", "chart", "table", "html"]);
let chartWidgetHtmlPromise = null;

const artifactApp = connectMcpWidgetHost({
  name: "Data Analytics Artifact App",
  version: "0.1.8",
  availableDisplayModes: ["inline", "fullscreen"],
  initialDisplayMode: "fullscreen",
});

const fallbackPayload = {
  ok: false,
  widget_type: "artifact",
  surface: "report",
  manifest: {
    version: 1,
    surface: "report",
    title: "Data Analytics artifact",
    description: "Waiting for an artifact payload.",
    blocks: [
      {
        id: "empty_state",
        type: "markdown",
        layout: "full",
        body: "## Waiting for Data\n\nThis artifact has not received a manifest and bounded snapshot yet.",
      },
    ],
    sources: [],
  },
  snapshot: {
    version: 1,
    status: "blocked",
    datasets: {},
    accessIssues: [
      {
        id: "missing_artifact_payload",
        message: "No Data Analytics artifact payload is available yet.",
      },
    ],
  },
  sources: [],
  package_info: {
    manifestPath: "tool payload",
    root: "mcp://datascience-artifact",
    snapshotPath: "tool payload",
  },
};

function createMemoryStorage() {
  const values = new Map();
  return {
    get length() {
      return values.size;
    },
    clear() {
      values.clear();
    },
    getItem(key) {
      const normalizedKey = String(key);
      return values.has(normalizedKey) ? values.get(normalizedKey) : null;
    },
    key(index) {
      return Array.from(values.keys())[index] ?? null;
    },
    removeItem(key) {
      values.delete(String(key));
    },
    setItem(key, value) {
      values.set(String(key), String(value));
    },
  };
}

function storageWorks(storage) {
  if (!storage) return false;
  const key = "__datascience_artifact_storage_probe__";
  try {
    storage.setItem(key, "1");
    storage.removeItem(key);
    return true;
  } catch {
    return false;
  }
}

function installStorageFallback() {
  if (typeof window === "undefined") return;
  try {
    if (storageWorks(window.localStorage)) return;
  } catch {
    // Accessing localStorage can throw in sandboxed MCP iframes.
  }

  const storage = window.__datascienceArtifactMemoryStorage || createMemoryStorage();
  window.__datascienceArtifactMemoryStorage = storage;
  try {
    Object.defineProperty(window, "localStorage", {
      configurable: true,
      value: storage,
    });
  } catch {
    // If the host prevents overriding localStorage, the fallback is still
    // available for future wrapper code through __datascienceArtifactMemoryStorage.
  }
}

function isArtifactPayload(value) {
  return Boolean(
    value &&
      typeof value === "object" &&
      value.widget_type === "artifact" &&
      value.manifest &&
      value.snapshot,
  );
}

function decodePayload(raw) {
  if (typeof raw !== "string") return raw;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function pickPayload(raw) {
  raw = decodePayload(raw);
  if (!raw || typeof raw !== "object") return null;
  if (Array.isArray(raw.content)) {
    for (const item of raw.content) {
      const found = pickPayload(item && (item.text || item));
      if (found) return found;
    }
  }
  if (isArtifactPayload(raw)) return raw;
  if (raw.structuredContent && typeof raw.structuredContent === "object") {
    return pickPayload(raw.structuredContent);
  }
  if (raw.payload && typeof raw.payload === "object") {
    return pickPayload(raw.payload);
  }
  if (raw.toolOutput && typeof raw.toolOutput === "object") {
    return pickPayload(raw.toolOutput);
  }
  if (raw.toolResponseMetadata && typeof raw.toolResponseMetadata === "object") {
    return pickPayload(raw.toolResponseMetadata);
  }
  if (raw.detail && typeof raw.detail === "object") return pickPayload(raw.detail);
  if (raw.globals && typeof raw.globals === "object") return pickPayload(raw.globals);
  return null;
}

function isPlainObject(value) {
  return Boolean(value && typeof value === "object" && !Array.isArray(value));
}

function hasOwn(value, key) {
  return isPlainObject(value) && Object.prototype.hasOwnProperty.call(value, key);
}

function validateDatasetRows(rows, path, issues) {
  if (!Array.isArray(rows)) {
    issues.push(`${path} must be an array of row objects.`);
    return [];
  }
  rows.forEach((row, index) => {
    if (!isPlainObject(row)) {
      issues.push(`${path}[${index}] must be an object.`);
    }
  });
  return rows.filter(isPlainObject);
}

function validateFieldReference(rows, field, path, issues) {
  if (typeof field !== "string" || !field.trim()) {
    issues.push(`${path} must be a non-empty field name.`);
    return;
  }
  if (!rows.length) return;
  if (!rows.some((row) => hasOwn(row, field))) {
    issues.push(`${path} references "${field}", but no sampled row contains that field.`);
  }
}

function chartEncoding(chart, role) {
  return isPlainObject(chart.encodings) && isPlainObject(chart.encodings[role]) ? chart.encodings[role] : {};
}

function chartEncodingField(chart, role) {
  const field = chartEncoding(chart, role).field;
  return typeof field === "string" && field.trim() ? field : null;
}

function chartEncodingFields(chart, role) {
  const fields = chartEncoding(chart, role).fields;
  return Array.isArray(fields) ? fields.filter((field) => typeof field === "string" && field.trim()) : [];
}

function hasChartEncodingSpec(chart) {
  return Boolean(
    isPlainObject(chart.encodings) &&
      chartEncodingField(chart, "x") &&
      (chartEncodingField(chart, "y") || chartEncodingFields(chart, "y").length),
  );
}

function validateEncodedChartFields(rows, chart, path, issues) {
  if (chart.xField != null) {
    issues.push(`${path}.xField is not supported for artifact charts; use encodings.`);
  }
  if (chart.series != null) {
    issues.push(`${path}.series is not supported for artifact charts; use encodings.`);
  }
  if (!hasChartEncodingSpec(chart)) {
    issues.push(`${path}.encodings must declare x and y fields before rendering.`);
    return;
  }
  validateFieldReference(rows, chartEncodingField(chart, "x"), `${path}.encodings.x.field`, issues);
  const yField = chartEncodingField(chart, "y");
  if (yField) validateFieldReference(rows, yField, `${path}.encodings.y.field`, issues);
  chartEncodingFields(chart, "y").forEach((field, fieldIndex) => {
    validateFieldReference(rows, field, `${path}.encodings.y.fields[${fieldIndex}]`, issues);
  });
  ["color", "size", "facet", "label"].forEach((role) => {
    const field = chartEncodingField(chart, role);
    if (field) validateFieldReference(rows, field, `${path}.encodings.${role}.field`, issues);
  });
}

function validateArtifactPayload(payload) {
  const issues = [];
  if (!isPlainObject(payload)) {
    return ["Artifact payload must be an object."];
  }

  const manifest = payload.manifest;
  const snapshot = payload.snapshot;
  if (!isPlainObject(manifest)) issues.push("manifest must be an object.");
  if (!isPlainObject(snapshot)) issues.push("snapshot must be an object.");
  if (!isPlainObject(manifest) || !isPlainObject(snapshot)) return issues;
  if (typeof manifest.title !== "string" || !manifest.title.trim()) {
    issues.push("manifest.title is required for artifact rendering.");
  }

  const datasets = snapshot.datasets;
  if (!isPlainObject(datasets)) {
    issues.push("snapshot.datasets must be an object keyed by dataset id.");
  }
  const datasetRows = new Map();
  if (isPlainObject(datasets)) {
    Object.entries(datasets).forEach(([datasetId, rows]) => {
      datasetRows.set(datasetId, validateDatasetRows(rows, `snapshot.datasets.${datasetId}`, issues));
    });
  }

  const blocks = manifest.blocks;
  if (!Array.isArray(blocks)) issues.push("manifest.blocks must be an array.");

  if (Array.isArray(blocks)) {
    blocks.forEach((block, index) => {
      if (!isPlainObject(block)) {
        issues.push(`manifest.blocks[${index}] must be an object.`);
        return;
      }
      if (typeof block.id !== "string" || !block.id.trim()) {
        issues.push(`manifest.blocks[${index}].id must be a non-empty string.`);
      }
      if (typeof block.type !== "string" || !block.type.trim()) {
        issues.push(`manifest.blocks[${index}].type must be a non-empty string.`);
      } else if (!ARTIFACT_BLOCK_TYPES.has(block.type)) {
        issues.push(`manifest.blocks[${index}].type is not supported.`);
      }
      if (block.type === "markdown" && (typeof block.body !== "string" || !block.body.trim())) {
        issues.push(`manifest.blocks[${index}].body must be a non-empty Markdown string.`);
      }
      if (block.type === "html" && (typeof block.body !== "string" || !block.body.trim())) {
        issues.push(`manifest.blocks[${index}].body must be a non-empty HTML string.`);
      }
    });
  }

  const charts = Array.isArray(manifest.charts) ? manifest.charts : [];
  const chartIds = new Set();
  if (manifest.charts != null && !Array.isArray(manifest.charts)) {
    issues.push("manifest.charts must be an array when provided.");
  }
  charts.forEach((chart, index) => {
    const path = `manifest.charts[${index}]`;
    if (!isPlainObject(chart)) {
      issues.push(`${path} must be an object.`);
      return;
    }
    if (typeof chart.id !== "string" || !chart.id.trim()) {
      issues.push(`${path}.id must be a non-empty string.`);
    } else {
      chartIds.add(chart.id);
    }
    if (typeof chart.dataset !== "string" || !chart.dataset.trim()) {
      issues.push(`${path}.dataset must be a non-empty string.`);
      return;
    }
    const rows = datasetRows.get(chart.dataset);
    if (!rows) {
      issues.push(`${path}.dataset references missing dataset "${chart.dataset}".`);
      return;
    }
    validateEncodedChartFields(rows, chart, path, issues);
  });

  const cards = Array.isArray(manifest.cards) ? manifest.cards : [];
  const cardIds = new Set();
  if (manifest.cards != null && !Array.isArray(manifest.cards)) {
    issues.push("manifest.cards must be an array when provided.");
  }
  cards.forEach((card, index) => {
    const path = `manifest.cards[${index}]`;
    if (!isPlainObject(card)) {
      issues.push(`${path} must be an object.`);
      return;
    }
    if (typeof card.id !== "string" || !card.id.trim()) {
      issues.push(`${path}.id must be a non-empty string.`);
    } else {
      cardIds.add(card.id);
    }
    if (typeof card.dataset !== "string" || !card.dataset.trim()) {
      issues.push(`${path}.dataset must be a non-empty string.`);
      return;
    }
    const rows = datasetRows.get(card.dataset);
    if (!rows) {
      issues.push(`${path}.dataset references missing dataset "${card.dataset}".`);
      return;
    }
    ["valueField", "format", "label", "title", "indicators", "deltaField", "deltaLabel"].forEach((removedField) => {
      if (hasOwn(card, removedField)) {
        issues.push(`${path}.${removedField} is not supported; use metrics[].`);
      }
    });
    if (!Array.isArray(card.metrics) || !card.metrics.length) {
      issues.push(`${path}.metrics must contain at least one metric.`);
    }
    const metrics = Array.isArray(card.metrics) ? card.metrics : [];
    metrics.forEach((metric, metricIndex) => {
      const metricPath = `${path}.metrics[${metricIndex}]`;
      if (!isPlainObject(metric)) {
        issues.push(`${metricPath} must be an object.`);
        return;
      }
      if (typeof metric.label !== "string" || !metric.label.trim()) {
        issues.push(`${metricPath}.label must be a non-empty string.`);
      }
      validateFieldReference(rows, metric.field, `${metricPath}.field`, issues);
      if (metric.format != null && typeof metric.format !== "string") {
        issues.push(`${metricPath}.format must be a string when provided.`);
      }
      if (metric.signed != null && typeof metric.signed !== "boolean") {
        issues.push(`${metricPath}.signed must be a boolean when provided.`);
      }
      if (hasOwn(metric, "movement")) {
        issues.push(`${metricPath}.movement is not supported; use signed.`);
      }
    });
  });

  const tables = Array.isArray(manifest.tables) ? manifest.tables : [];
  const tableIds = new Set();
  if (manifest.tables != null && !Array.isArray(manifest.tables)) {
    issues.push("manifest.tables must be an array when provided.");
  }
  tables.forEach((table, index) => {
    const path = `manifest.tables[${index}]`;
    if (!isPlainObject(table)) {
      issues.push(`${path} must be an object.`);
      return;
    }
    if (typeof table.id !== "string" || !table.id.trim()) {
      issues.push(`${path}.id must be a non-empty string.`);
    } else {
      tableIds.add(table.id);
    }
    if (typeof table.dataset !== "string" || !table.dataset.trim()) {
      issues.push(`${path}.dataset must be a non-empty string.`);
      return;
    }
    const rows = datasetRows.get(table.dataset);
    if (!rows) {
      issues.push(`${path}.dataset references missing dataset "${table.dataset}".`);
      return;
    }
    if (!Array.isArray(table.columns) || !table.columns.length) {
      issues.push(`${path}.columns must be a non-empty array.`);
      return;
    }
    const columnFields = new Set();
    table.columns.forEach((column, columnIndex) => {
      if (!isPlainObject(column)) {
        issues.push(`${path}.columns[${columnIndex}] must be an object.`);
        return;
      }
      validateFieldReference(rows, column.field, `${path}.columns[${columnIndex}].field`, issues);
      if (typeof column.field === "string" && column.field) {
        columnFields.add(column.field);
      }
    });
    if (table.defaultSort != null) {
      if (!isPlainObject(table.defaultSort)) {
        issues.push(`${path}.defaultSort must be an object.`);
      } else {
        if (!columnFields.has(table.defaultSort.field)) {
          issues.push(`${path}.defaultSort.field must reference a declared table column.`);
        }
        if (!["asc", "desc"].includes(table.defaultSort.direction)) {
          issues.push(`${path}.defaultSort.direction must be asc or desc.`);
        }
      }
    }
  });

  if (Array.isArray(blocks)) {
    blocks.forEach((block, index) => {
      if (!isPlainObject(block)) return;
      if (block.type === "chart" && !chartIds.has(block.chartId)) {
        issues.push(`manifest.blocks[${index}].chartId references a missing chart.`);
      }
      if (block.type === "metric-strip") {
        if (!Array.isArray(block.cardIds) || !block.cardIds.length) {
          issues.push(`manifest.blocks[${index}].cardIds must reference at least one metric card.`);
        } else {
          block.cardIds.forEach((cardId, cardIndex) => {
            if (!cardIds.has(cardId)) {
              issues.push(`manifest.blocks[${index}].cardIds[${cardIndex}] references a missing metric card.`);
            }
          });
        }
      }
      if (block.type === "table" && !tableIds.has(block.tableId)) {
        issues.push(`manifest.blocks[${index}].tableId references a missing table.`);
      }
    });
  }

  return issues;
}

function InvalidArtifactPayload({ issues, surface }) {
  const visibleIssues = Array.isArray(issues) ? issues.slice(0, 8) : [];
  const issueCount = Array.isArray(issues) ? issues.length : visibleIssues.length;
  const artifactLabel =
    surface === "dashboard" || surface === "report" ? surface : "artifact";
  return (
    <main
      style={{
        background: "#fff",
        color: "#111827",
        fontFamily: "Inter, system-ui, sans-serif",
        minHeight: "100vh",
        padding: 24,
      }}
    >
      <section
        style={{
          border: "1px solid #e5e7eb",
          borderRadius: 12,
          maxWidth: 760,
          padding: 20,
        }}
      >
        <h1 style={{ fontSize: 18, lineHeight: "24px", margin: "0 0 8px" }}>
          Artifact validation failed
        </h1>
        <p style={{ color: "#4b5563", fontSize: 14, lineHeight: "20px", margin: "0 0 16px" }}>
          The {artifactLabel} was blocked before rendering because its manifest or snapshot does not match
          the Data Analytics artifact contract.
        </p>
        <ul style={{ color: "#374151", fontSize: 13, lineHeight: "20px", margin: 0, paddingLeft: 20 }}>
          {visibleIssues.map((issue, index) => (
            <li key={`${issue}-${index}`}>{issue}</li>
          ))}
        </ul>
        {issueCount > visibleIssues.length ? (
          <p style={{ color: "#6b7280", fontSize: 12, margin: "12px 0 0" }}>
            {issueCount - visibleIssues.length} more validation issue
            {issueCount - visibleIssues.length === 1 ? "" : "s"} hidden.
          </p>
        ) : null}
      </section>
    </main>
  );
}

function currentHostPayload() {
  if (typeof window === "undefined") return null;
  return (
    pickPayload(window.openai?.toolOutput) ||
    pickPayload(window.openai?.toolResponseMetadata) ||
    pickPayload(window.openai)
  );
}

function fallbackForEnvironment() {
  return fallbackPayload;
}

function artifactIdentity(payload) {
  const manifest = payload?.manifest || {};
  const snapshot = payload?.snapshot || {};
  return [
    manifest.title || "artifact",
    manifest.generatedAt || "",
    snapshot.generatedAt || "",
    payload?.surface || manifest.surface || "artifact",
  ].join(":");
}

function jsonResponse(body, init = {}) {
  return new Response(JSON.stringify(body), {
    status: init.status || 200,
    headers: {
      "content-type": "application/json; charset=utf-8",
      ...(init.headers || {}),
    },
  });
}

function textResponse(body, init = {}) {
  return new Response(String(body ?? ""), {
    status: init.status || 200,
    headers: {
      "content-type": "text/plain; charset=utf-8",
      ...(init.headers || {}),
    },
  });
}

function htmlResponse(body, init = {}) {
  return new Response(String(body ?? ""), {
    status: init.status || 200,
    headers: {
      "content-type": "text/html; charset=utf-8",
      ...(init.headers || {}),
    },
  });
}

function readChartWidgetHtml() {
  if (!chartWidgetHtmlPromise) {
    chartWidgetHtmlPromise = (async () => {
      await artifactApp.ready;
      const resource = await artifactApp.readServerResource({
        uri: CHART_WIDGET_RESOURCE_URI,
      });
      const content = Array.isArray(resource?.contents)
        ? resource.contents.find((entry) => typeof entry?.text === "string")
        : null;
      if (!content?.text) {
        throw new Error("The shared chart detail resource did not include HTML.");
      }
      return content.text;
    })();
  }
  return chartWidgetHtmlPromise;
}

function sourceTextForPath(payload, sourcePath) {
  const manifestSources = Array.isArray(payload?.manifest?.sources)
    ? payload.manifest.sources
    : [];
  const inlineSources = Array.isArray(payload?.sources) ? payload.sources : [];
  const declared = [...manifestSources, ...inlineSources].find((source) => {
    if (!source || typeof source !== "object") return false;
    return source.path === sourcePath || source.id === sourcePath || source.href === sourcePath;
  });
  if (typeof declared?.query?.sql === "string") return declared.query.sql;
  return null;
}

function installMcpFetchShim(payload) {
  window.__datascienceArtifactPayload = payload;
  if (window.__datascienceArtifactFetchShimInstalled) return;

  const nativeFetch = window.fetch.bind(window);
  window.__datascienceArtifactFetchShimInstalled = true;
  window.fetch = async (input, init) => {
    const requestUrl = typeof input === "string" ? input : input?.url;
    const url = new URL(requestUrl || "", window.location.origin);
    const currentPayload = window.__datascienceArtifactPayload || fallbackForEnvironment();

    if (url.origin === window.location.origin && url.pathname === "/api/manifest") {
      return jsonResponse(currentPayload.manifest || {});
    }
    if (url.origin === window.location.origin && url.pathname === "/api/snapshot") {
      return jsonResponse(currentPayload.snapshot || {});
    }
    if (url.origin === window.location.origin && url.pathname === "/api/package") {
      return jsonResponse(
        currentPayload.package_info ||
          currentPayload.packageInfo || {
            manifestPath: "tool payload",
            root: "mcp://datascience-artifact",
            snapshotPath: "tool payload",
          },
      );
    }
    if (url.origin === window.location.origin && url.pathname === "/api/inline-chart-widget") {
      try {
        return htmlResponse(await readChartWidgetHtml());
      } catch (error) {
        return textResponse(error instanceof Error ? error.message : "Inline chart widget asset is unavailable.", {
          status: 503,
        });
      }
    }
    if (
      url.origin === window.location.origin &&
      (url.pathname === "/api/source-file" || url.pathname === "/api/source")
    ) {
      const sourcePath = url.searchParams.get("path") || "";
      const text = sourceTextForPath(currentPayload, sourcePath);
      if (text != null) return textResponse(text);
      return textResponse("Source text was not included in this hosted artifact.", {
        status: 404,
      });
    }

    return nativeFetch(input, init);
  };
}

function displayModeFromPayload(payload) {
  return (
    normalizeDisplayMode(
      payload?.displayMode ||
        payload?.display_mode ||
        payload?.manifest?.displayMode ||
        payload?.manifest?.display_mode,
    ) || "inline"
  );
}

function normalizeDisplayMode(mode) {
  return mode === "inline" || mode === "fullscreen" || mode === "pip" ? mode : "";
}

function readUrlDisplayMode() {
  if (typeof window === "undefined") return "";
  try {
    const params = new URLSearchParams(window.location.search);
    const hashParams = new URLSearchParams(window.location.hash.replace(/^#/, ""));
    const raw = (
      params.get("displayMode") ||
      params.get("display_mode") ||
      params.get("preview") ||
      hashParams.get("displayMode") ||
      hashParams.get("display_mode") ||
      hashParams.get("preview") ||
      ""
    ).toLowerCase();
    if (raw === "fullscreen" || raw === "full" || raw === "expanded") return "fullscreen";
    if (raw === "inline" || raw === "compact") return "inline";
  } catch {
    // Ignore malformed URLs from host previews.
  }
  return "";
}

function pickDisplayMode(raw) {
  const value = decodePayload(raw);
  if (!value || typeof value !== "object") return "";
  if (value.type === "datascience-chart-widget-display-mode") return "";
  return normalizeDisplayMode(
    value.displayMode ||
      value.display_mode ||
      value.mode ||
      value.view?.displayMode ||
      value.hostContext?.displayMode ||
      value.host?.displayMode ||
      value.globals?.displayMode ||
      value.globals?.view?.displayMode ||
      value.globals?.hostContext?.displayMode,
  );
}

function currentHostDisplayMode() {
  if (typeof window === "undefined") return "inline";
  const hostApi = window.openai || {};
  return (
    readUrlDisplayMode() ||
    normalizeDisplayMode(
      hostApi.displayMode ||
        hostApi.view?.displayMode ||
        hostApi.hostContext?.displayMode ||
        hostApi.host?.displayMode,
    ) ||
    "inline"
  );
}

function hostSupportsDisplayMode() {
  if (typeof window === "undefined") return false;
  const hostApi = window.openai || {};
  const availableDisplayModes =
    hostApi.availableDisplayModes ||
    hostApi.hostContext?.availableDisplayModes ||
    hostApi.view?.availableDisplayModes;
  if (Array.isArray(availableDisplayModes) && availableDisplayModes.includes("fullscreen")) {
    return true;
  }
  return Boolean(window.openai) || typeof hostApi.requestDisplayMode === "function";
}

function applyDocumentDisplayMode(mode) {
  if (typeof document === "undefined") return;
  const normalized = normalizeDisplayMode(mode) || "inline";
  document.documentElement.dataset.displayMode = normalized;
  document.body.dataset.displayMode = normalized;
}

function useHostPayload() {
  const [payload, setPayload] = useState(() => currentHostPayload() || fallbackForEnvironment());

  useEffect(() => {
    function apply(raw) {
      const next = pickPayload(raw);
      if (next) setPayload(next);
    }
    function handleMessage(event) {
      apply(event.data);
    }
    function handleToolResult(event) {
      apply(event.detail);
    }
    function handleGlobals(event) {
      apply(event.detail?.globals);
    }

    apply(currentHostPayload());
    window.addEventListener("message", handleMessage);
    window.addEventListener("datascience-widget-tool-result", handleToolResult);
    window.addEventListener("openai:set_globals", handleGlobals);
    return () => {
      window.removeEventListener("message", handleMessage);
      window.removeEventListener("datascience-widget-tool-result", handleToolResult);
      window.removeEventListener("openai:set_globals", handleGlobals);
    };
  }, []);

  return payload;
}

function useHostDisplayMode() {
  const [displayMode, setDisplayMode] = useState(() => currentHostDisplayMode());

  useEffect(() => {
    function apply(raw) {
      const next = pickDisplayMode(raw);
      if (next) setDisplayMode(next);
    }
    function handleMessage(event) {
      apply(event.data);
    }
    function handleGlobals(event) {
      apply(event.detail?.globals || event.detail);
    }

    setDisplayMode(currentHostDisplayMode());
    applyDocumentDisplayMode(currentHostDisplayMode());
    window.addEventListener("message", handleMessage);
    window.addEventListener("openai:set_globals", handleGlobals);
    return () => {
      window.removeEventListener("message", handleMessage);
      window.removeEventListener("openai:set_globals", handleGlobals);
    };
  }, []);

  useEffect(() => {
    applyDocumentDisplayMode(displayMode);
  }, [displayMode]);

  return { displayMode, setDisplayMode };
}

async function requestArtifactDisplayMode(mode, setDisplayMode) {
  const requestDisplayMode = window.openai?.requestDisplayMode;
  if (typeof requestDisplayMode !== "function") return { mode: currentHostDisplayMode() };

  try {
    const result = await Promise.resolve(requestDisplayMode({ mode }));
    const resultMode = normalizeDisplayMode(result?.mode || result?.displayMode);
    if (resultMode) {
      setDisplayMode(resultMode);
      applyDocumentDisplayMode(resultMode);
      return result;
    }
  } catch {
    const currentMode = currentHostDisplayMode();
    setDisplayMode(currentMode);
    applyDocumentDisplayMode(currentMode);
  }
  return { mode: currentHostDisplayMode() };
}

function ArtifactApp() {
  const payload = useHostPayload();
  const surface = payload?.surface || payload?.manifest?.surface;
  const identity = useMemo(() => artifactIdentity(payload), [payload]);
  const validationIssues = useMemo(() => validateArtifactPayload(payload), [identity, payload]);
  const { displayMode, setDisplayMode } = useHostDisplayMode();
  const requestedDisplayMode = useMemo(() => displayModeFromPayload(payload), [identity, payload]);
  const hasFullscreenArtifactSurface = surface === "report" || surface === "dashboard";
  const canRequestFullscreen =
    hasFullscreenArtifactSurface && hostSupportsDisplayMode() && displayMode !== "fullscreen";
  const requestFullscreen = canRequestFullscreen
    ? () => {
        void requestArtifactDisplayMode("fullscreen", setDisplayMode);
      }
    : undefined;

  useLayoutEffect(() => {
    installMcpFetchShim(payload);
  }, [payload]);

  useEffect(() => {
    const mode = requestedDisplayMode;
    if (mode === "inline") return;
    const requestDisplayMode = window.openai?.requestDisplayMode;
    if (typeof requestDisplayMode !== "function") return;
    try {
      void Promise.resolve(requestDisplayMode({ mode }))
        .then((result) => {
          const resultMode = normalizeDisplayMode(result?.mode || result?.displayMode);
          if (resultMode) {
            setDisplayMode(resultMode);
            applyDocumentDisplayMode(resultMode);
          }
        })
        .catch(() => {
          // Hosts may decline fullscreen/pip; the compact artifact launcher remains inline.
        });
    } catch {
      // Some hosts expose requestDisplayMode as a fire-and-forget function.
    }
  }, [identity, requestedDisplayMode, setDisplayMode]);

  if (validationIssues.length) {
    return <InvalidArtifactPayload issues={validationIssues} surface={surface} />;
  }

  return (
    <ArtifactErrorBoundary surface={surface}>
      <div className="datascience-artifact-shell" data-display-mode={displayMode}>
        <AnalyticsApp
          key={identity}
          displayMode={displayMode === "fullscreen" ? "fullscreen" : "inline"}
          onRequestFullscreen={requestFullscreen}
        />
      </div>
    </ArtifactErrorBoundary>
  );
}

class ArtifactErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  render() {
    if (this.state.error) {
      const message =
        this.state.error instanceof Error ? this.state.error.message : String(this.state.error);
      return (
        <InvalidArtifactPayload
          issues={[`Unexpected render failure: ${message}`]}
          surface={this.props.surface}
        />
      );
    }
    return this.props.children;
  }
}

const root = document.getElementById("root");

if (!root) {
  throw new Error("Missing root element");
}

installStorageFallback();

createRoot(root).render(
  <StrictMode>
    <ArtifactErrorBoundary>
      <ArtifactApp />
    </ArtifactErrorBoundary>
  </StrictMode>,
);
