import React from "react";
import { createRoot } from "react-dom/client";

import { connectMcpWidgetHost } from "./mcp-host.js";
import { DataTable } from "./analytics-app/tables/DataTable.jsx";
import { renderSourceCode, sourceCodeLanguage, sourceCodeText, sourceQueryFromSource } from "./sql-source-view.js";
import "./styles/codex-theme.css";
import "./analytics-app/tokens.css";
import "./analytics-app/tables/data-table.css";
import "./sql-source-view.css";
import "./datascience-table-widget.css";

connectMcpWidgetHost({
  name: "Data Analytics Table Widget",
  version: "0.1.1",
  availableDisplayModes: ["inline", "fullscreen"],
});


const TABLE_CARD_PAGE_SIZE = 15;

const fallbackPayload = {
  title: "Top segments by week-over-week change",
  subtitle: "Sorted by absolute contribution to the weekly movement.",
  source: {
    label: "Warehouse",
    query: {
      engine: "static-demo",
      id: "table-widget-demo",
      sql: "SELECT segment, wau, wow, driver FROM demo.weekly_segment_movements ORDER BY ABS(wow) DESC LIMIT 5",
      description: "Ranks demo segments by absolute week-over-week movement.",
      executed_at: "2026-05-01T00:00:00Z",
    },
  },
  metrics: [
    { label: "Rows", value: 5 },
    { label: "Window", value: "7d" },
  ],
  columns: [
    { key: "segment", label: "Segment", type: "text" },
    { key: "wau", label: "WAU", type: "number" },
    { key: "wow", label: "WoW", type: "percent" },
    { key: "driver", label: "Driver", type: "text" },
  ],
  rows: [
    { segment: "Team", wau: 182300, wow: 0.083, driver: "Onboarding recovery" },
    { segment: "Enterprise", wau: 109420, wow: 0.041, driver: "Seat expansion" },
    { segment: "Free", wau: 761020, wow: -0.018, driver: "Seasonality" },
    { segment: "Plus", wau: 323110, wow: 0.012, driver: "Normal variance" },
    { segment: "Edu", wau: 38440, wow: -0.031, driver: "Term break" },
  ],
  notes: ["Rows are capped to the current preview."],
  max_rows: 50,
};

let payload = fallbackPayload;
let displayMode = "inline";
let lastPayloadSignature = "";
let tableRoot = null;

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
  if (raw.structuredContent && typeof raw.structuredContent === "object") {
    return pickPayload(raw.structuredContent);
  }
  if (raw.payload && typeof raw.payload === "object") {
    return pickPayload(raw.payload);
  }
  if (Array.isArray(raw.rows) || raw.result_table) return raw;
  return null;
}

function payloadSignature(value) {
  try {
    return JSON.stringify(value);
  } catch {
    return String(Date.now());
  }
}

function currentHostPayload() {
  return (
    pickPayload(window.openai && window.openai.toolOutput) ||
    pickPayload(window.openai && window.openai.toolResponseMetadata)
  );
}

function readUrlDisplayMode() {
  try {
    const params = new URLSearchParams(window.location.search);
    const hashParams = new URLSearchParams(window.location.hash.replace(/^#/, ""));
    const raw = (
      params.get("displayMode") ||
      params.get("display_mode") ||
      hashParams.get("displayMode") ||
      hashParams.get("display_mode") ||
      ""
    ).toLowerCase();
    if (raw === "fullscreen" || raw === "full" || raw === "expanded") return "fullscreen";
    if (raw === "inline" || raw === "compact") return "inline";
  } catch {
    return "";
  }
  return "";
}

function setDisplayMode(mode) {
  if (mode !== "inline" && mode !== "fullscreen") return;
  displayMode = mode;
  document.documentElement.dataset.displayMode = mode;
  document.body.dataset.displayMode = mode;
  const widget = document.querySelector(".widget");
  if (widget) widget.dataset.displayMode = mode;
}

function applyHostState(raw) {
  const next = decodePayload(raw);
  if (!next || typeof next !== "object") return;
  const mode =
    next.displayMode ||
    next.display_mode ||
    (next.view && next.view.displayMode) ||
    (next.hostContext && next.hostContext.displayMode) ||
    (next.globals && (next.globals.displayMode || (next.globals.view && next.globals.view.displayMode)));
  if (mode === "inline" || mode === "fullscreen") {
    setDisplayMode(mode);
    renderTable();
    renderQueryPreview();
  }
}

function hostedEmptyPayload() {
  return {
    title: "Data Analytics table",
    rows: [],
    notes: ["Waiting for widget data."],
    max_rows: 50,
  };
}

function applyPayload(raw) {
  const next = pickPayload(raw);
  if (!next) return false;
  const signature = payloadSignature(next);
  if (signature === lastPayloadSignature) return true;
  lastPayloadSignature = signature;
  payload = next;
  render();
  return true;
}

function text(value) {
  return value == null ? "" : String(value);
}

function resultTable() {
  return payload.result_table && typeof payload.result_table === "object" ? payload.result_table : null;
}

function sourceQuery() {
  return sourceQueryFromSource(payload.source);
}

function sourceLabel() {
  const source = payload.source;
  if (source && typeof source === "object" && !Array.isArray(source)) return text(source.label);
  return text(source);
}

function queryText() {
  return sourceCodeText(sourceQuery());
}

function queryLanguage() {
  return sourceCodeLanguage(sourceQuery());
}

function setQueryStatus(message) {
  const status = document.getElementById("query-status");
  if (status) status.textContent = message || "";
}

function renderQueryControls() {
  if (displayMode !== "fullscreen") {
    setQueryStatus("");
    return;
  }
  const source = sourceQuery();
  const table = resultTable();
  const label =
    (source && (source.label || source.id || source.engine)) || sourceLabel();
  const rowCount = table && Number.isFinite(Number(table.row_count)) ? Number(table.row_count) : null;
  const suffix = rowCount != null ? ` · ${new Intl.NumberFormat().format(rowCount)} rows${table.truncated ? " sampled" : ""}` : "";
  setQueryStatus(label ? `${label}${suffix}` : "");
}

function inferColumns(rows) {
  const seen = new Set();
  const columns = [];
  for (const row of rows) {
    if (!row || typeof row !== "object") continue;
    for (const key of Object.keys(row)) {
      if (seen.has(key)) continue;
      seen.add(key);
      columns.push({ key, label: key.replaceAll("_", " ") });
    }
  }
  return columns;
}

function renderTable() {
  const tablePayload = resultTable();
  const rows = Array.isArray(tablePayload?.rows) ? tablePayload.rows : Array.isArray(payload.rows) ? payload.rows : [];
  const columns =
    Array.isArray(tablePayload?.columns) && tablePayload.columns.length
      ? tablePayload.columns
      : Array.isArray(payload.columns) && payload.columns.length
        ? payload.columns
        : inferColumns(rows);
  const maxRows = Math.max(1, Number(payload.max_rows || 50));
  const pageSize = displayMode === "fullscreen" ? Math.max(1, Math.min(rows.length, maxRows)) : TABLE_CARD_PAGE_SIZE;

  const wrap = document.getElementById("table-wrap");
  if (!wrap) return;
  wrap.className = `table-wrap table-density-dense ${displayMode === "fullscreen" ? "fullscreen" : ""}`;
  if (!tableRoot) tableRoot = createRoot(wrap);

  tableRoot.render(
    React.createElement(DataTable, {
      columns,
      maxRows,
      pageSize,
      rows,
      showCount: false,
    }),
  );

  const pagination = document.getElementById("pagination");
  if (pagination) pagination.hidden = true;

  const count = document.getElementById("count");
  const totalRows = tablePayload && Number.isFinite(Number(tablePayload.row_count)) ? Number(tablePayload.row_count) : rows.length;
  const shownRows = Math.min(rows.length, maxRows);
  count.textContent = rows.length && totalRows > shownRows ? `${shownRows} of ${totalRows} results` : "";
  count.hidden = !count.textContent;
}

function renderQueryPreview() {
  const preview = document.getElementById("query-preview");
  const code = document.getElementById("query-code");
  const heading = document.getElementById("query-heading");
  if (!preview || !code) return;
  const sql = queryText();
  const shouldShow = displayMode === "fullscreen" && Boolean(sql);
  preview.hidden = !shouldShow;
  if (!shouldShow) {
    code.textContent = "";
    return;
  }
  const language = queryLanguage() || "Query";
  if (heading) heading.textContent = language === "SQL" ? "Source SQL" : `Source ${language}`;
  code.dataset.language = language;
  renderSourceCode(code, sql, language);
}

function render() {
  document.getElementById("title").textContent = text(payload.title || "Data Analytics table");
  document.getElementById("subtitle").textContent = text(payload.subtitle);
  document.getElementById("subtitle").hidden = !payload.subtitle;
  renderQueryControls();
  renderTable();
  renderQueryPreview();

  const notes = document.getElementById("notes");
  notes.innerHTML = "";
  const noteItems = Array.isArray(payload.notes) ? payload.notes : [];
  notes.hidden = !noteItems.length;
  for (const item of noteItems.slice(0, 4)) {
    const li = document.createElement("li");
    li.className = "note";
    li.textContent = item;
    notes.appendChild(li);
  }
  document.getElementById("footer").hidden = !document.getElementById("count").textContent && !noteItems.length;
}

setDisplayMode(readUrlDisplayMode() || "inline");

window.addEventListener("message", (event) => {
  applyHostState(event.data);
  applyPayload(event.data);
});

window.addEventListener("openai:set_globals", (event) => {
  const globals = event.detail && event.detail.globals;
  applyHostState(globals);
  if (globals && applyPayload(globals.toolOutput)) return;
  applyPayload(currentHostPayload());
});

if (!applyPayload(currentHostPayload())) {
  const initialPayload = window.openai ? hostedEmptyPayload() : fallbackPayload;
  payload = initialPayload;
  lastPayloadSignature = payloadSignature(initialPayload);
  render();
}

let hostPollAttempts = 0;
const hostPoll = window.setInterval(() => {
  hostPollAttempts += 1;
  const hostApi = window.openai || {};
  applyHostState(hostApi);
  applyPayload(currentHostPayload());
  if (hostPollAttempts >= 80) {
    window.clearInterval(hostPoll);
  }
}, 250);
