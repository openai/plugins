import { connectMcpWidgetHost } from "./mcp-host.js";
import {
CANONICAL_CHART_TYPES,
canonicalVisualizationType,
chartPickerSections,
resolveCssColors,
} from "./recharts-config.js";
import { destroyRechartsChart, renderRechartsChart } from "./recharts-renderer.jsx";
import { destroyDataTable, renderDataTable } from "./table-renderer.jsx";
import { renderSourceCode, sourceCodeLanguage, sourceCodeText, sourceQueryFromSource } from "./sql-source-view.js";
import "./styles/codex-theme.css";
import "./analytics-app/tokens.css";
import "./sql-source-view.css";
import "./datascience-chart-widget.css";

connectMcpWidgetHost({
name: "Data Analytics Chart Widget",
version: "0.1.1",
availableDisplayModes: ["inline", "fullscreen"],
});


function round(value, digits = 1) {
const factor = 10 ** digits;
return Math.round(value * factor) / factor;
}

function isoDateFromDay(startMs, dayIndex) {
return new Date(startMs + dayIndex * 86400000).toISOString().slice(0, 10);
}

function weekdayName(startMs, dayIndex) {
return new Date(startMs + dayIndex * 86400000).toLocaleDateString(undefined, { weekday: "short", timeZone: "UTC" });
}

function buildFallbackRows() {
const startMs = Date.UTC(2026, 0, 1);
const weekdayLift = [0.62, 1.05, 1.1, 1.08, 1.12, 1.0, 0.58];
const regions = [
{ region: "North America", multiplier: 1.22, accountMultiplier: 1.18, productOffset: 0 },
{ region: "EMEA", multiplier: 0.82, accountMultiplier: 0.9, productOffset: 1 },
];
const plans = [
{ plan: "Self-serve", channel: "Organic", baseRevenue: 0.78, weeklyGrowth: 0.055, baseAccounts: 3.1, accountGrowth: 0.09, activation: 43, conversion: 7.8, margin: 61 },
{ plan: "Team", channel: "Partner", baseRevenue: 1.18, weeklyGrowth: 0.085, baseAccounts: 1.85, accountGrowth: 0.055, activation: 56, conversion: 12.4, margin: 66 },
{ plan: "Enterprise", channel: "Sales-led", baseRevenue: 1.72, weeklyGrowth: 0.13, baseAccounts: 0.72, accountGrowth: 0.025, activation: 69, conversion: 18.2, margin: 72 },
];
const products = ["Chat", "API", "Agents", "Voice"];
const rows = [];
for (let dayIndex = 0; dayIndex < 91; dayIndex += 1) {
const weekIndex = Math.floor(dayIndex / 7);
const weekday = new Date(startMs + dayIndex * 86400000).getUTCDay();
for (const [regionIndex, region] of regions.entries()) {
for (const [planIndex, plan] of plans.entries()) {
const wave = Math.sin((dayIndex + 1) * (planIndex + 1.7) + regionIndex * 2.1) * 0.07;
const lift = weekdayLift[weekday] * (1 + wave);
const revenue = (plan.baseRevenue + weekIndex * plan.weeklyGrowth) * region.multiplier * lift;
const activeAccounts = (plan.baseAccounts + weekIndex * plan.accountGrowth) * region.accountMultiplier * lift;
rows.push({
date: isoDateFromDay(startMs, dayIndex),
weekday: weekdayName(startMs, dayIndex),
region: region.region,
plan: plan.plan,
acquisition_channel: plan.channel,
product_area: products[(planIndex + region.productOffset + weekIndex) % products.length],
lifecycle_stage: dayIndex < 28 ? "New" : planIndex === 0 ? "Retention" : "Expansion",
revenue_m: round(revenue, 2),
active_accounts_k: round(activeAccounts, 1),
activation_rate_pct: round(plan.activation + weekIndex * 0.35 + regionIndex * 0.8 + wave * 18, 1),
conversion_rate_pct: round(plan.conversion + weekIndex * 0.18 + regionIndex * 0.4 + wave * 6, 1),
pipeline_m: round(revenue * (planIndex === 2 ? 1.75 : planIndex === 1 ? 1.32 : 0.92), 2),
spend_m: round(revenue * (planIndex === 0 ? 0.19 : planIndex === 1 ? 0.16 : 0.13), 2),
margin_pct: round(plan.margin + weekIndex * 0.18 - (weekday === 0 || weekday === 6 ? 1.4 : 0) + wave * 7, 1),
});
}
}
}
return rows;
}

const fallbackRows = buildFallbackRows();
const fallbackPayload = {
ok: true,
widget_type: "chart",
title: "Daily product growth demo by plan and region",
source: {
query: {
engine: "static-demo",
id: "widget-demo-growth-configs",
executed_at: "2026-05-01T00:00:00Z",
sql:
"SELECT date, weekday, region, plan, acquisition_channel, product_area, lifecycle_stage, revenue_m, active_accounts_k, activation_rate_pct, conversion_rate_pct, pipeline_m, spend_m, margin_pct FROM demo.widget_growth_configurations_daily",
},
},
table: {
columns: [
{ key: "date", label: "Date", type: "date" },
{ key: "weekday", label: "Weekday", type: "text" },
{ key: "region", label: "Region", type: "text" },
{ key: "plan", label: "Plan", type: "text" },
{ key: "acquisition_channel", label: "Acquisition channel", type: "text" },
{ key: "product_area", label: "Product area", type: "text" },
{ key: "lifecycle_stage", label: "Lifecycle stage", type: "text" },
{ key: "revenue_m", label: "Revenue", type: "number", unit: "$M" },
{ key: "active_accounts_k", label: "Active accounts", type: "number", unit: "K" },
{ key: "activation_rate_pct", label: "Activation rate", type: "number", unit: "%" },
{ key: "conversion_rate_pct", label: "Conversion rate", type: "number", unit: "%" },
{ key: "pipeline_m", label: "Pipeline", type: "number", unit: "$M" },
{ key: "spend_m", label: "Spend", type: "number", unit: "$M" },
{ key: "margin_pct", label: "Margin", type: "number", unit: "%" },
],
rows: fallbackRows,
row_count: fallbackRows.length,
truncated: false,
},
chart: {
type: "bar",
fields: {
x: { field: "date", type: "temporal", time_unit: "week" },
y: { field: "revenue_m", type: "quantitative", aggregate: "sum", unit: "$M" },
color: { field: "plan", type: "nominal" },
},
},
display: {
unit: "$M",
controls: true,
},
};

const colors = [
"var(--ds-chart-series-blue)",
"var(--ds-chart-series-orange)",
"var(--ds-chart-series-green)",
"var(--ds-chart-series-purple)",
"var(--ds-chart-series-red)",
"var(--ds-chart-series-pink)",
"var(--ds-chart-series-yellow)",
"var(--ds-chart-series-neutral)",
];
const colorEdges = colors;
const visualizationTypes = CANONICAL_CHART_TYPES;
const aggregationOptions = ["Sum", "Average", "Minimum", "Maximum", "Count"];
const fieldMenuSearchThreshold = 12;
const measureNamesField = "__measure_names__";
let payload = fallbackPayload;
let activeVisualizationType = "bar";
let chartSettings = {
barOrientation: "vertical",
barGroupMode: "grouped",
};
let viewMode = "both";
let dataMode = "table";
let chartConfig = {
xField: "x",
yField: "y",
colorField: "series",
lineStyleField: "",
labelField: "",
sizeField: "",
timeUnit: "none",
yAggregation: "sum",
};
let visibleSeries = new Set();
let visibleSeriesSignature = "";
let revealAllSeriesAfterGroupingChange = false;
let chartInstance = null;
let lastPayloadSignature = "";
let hasExternalPayload = false;
let displayMode = "inline";
let selectedDataFilters = {};
let shareMenuOpen = false;
const splitStorageKeyPrefix = "datascience-chart-split:";
const defaultSplitFraction = 0.618;
const minSplitFraction = 0.35;
const maxSplitFraction = 0.78;
let splitFraction = defaultSplitFraction;
let resizeFrame = 0;

function isDetailDisplayMode(mode = displayMode) {
return mode === "fullscreen" || mode === "modal";
}

function decodePayload(raw) {
if (typeof raw !== "string") return raw;
try {
return JSON.parse(raw);
} catch {
return null;
}
}

function readUrlWidgetInstanceId() {
try {
const params = new URLSearchParams(window.location.search);
const hashParams = new URLSearchParams(window.location.hash.replace(/^#/, ""));
return (
params.get("widgetInstanceId") ||
params.get("widgetId") ||
hashParams.get("widgetInstanceId") ||
hashParams.get("widgetId") ||
""
);
} catch {
return "";
}
}

const urlWidgetInstanceId = readUrlWidgetInstanceId();

function readUrlDisplayMode() {
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
if (raw === "modal" || raw === "dialog") return "modal";
if (raw === "inline" || raw === "compact") return "inline";
return "";
} catch {
return "";
}
}

const urlDisplayMode = readUrlDisplayMode();

function firstString(...values) {
for (const value of values) {
if (value == null || value === "") continue;
return String(value);
}
return "";
}

function currentWidgetInstanceId() {
const hostApi = window.openai || {};
const hostContext = hostApi.hostContext || {};
const view = hostApi.view || {};
return firstString(
hostApi.widgetInstanceId,
hostApi.widgetId,
hostApi.widget_instance_id,
hostApi.widget_id,
hostContext.widgetInstanceId,
hostContext.widgetId,
view.widgetInstanceId,
view.widgetId,
urlWidgetInstanceId,
);
}

function targetWidgetInstanceId(raw) {
raw = decodePayload(raw);
if (!raw || typeof raw !== "object") return "";
const meta = raw._meta || raw.meta || {};
const globals = raw.globals || {};
const hostContext = raw.hostContext || {};
const view = raw.view || {};
return firstString(
raw.targetWidgetInstanceId,
raw.targetWidgetId,
raw.target_widget_instance_id,
raw.target_widget_id,
meta.targetWidgetInstanceId,
meta.targetWidgetId,
globals.targetWidgetInstanceId,
globals.targetWidgetId,
hostContext.targetWidgetInstanceId,
hostContext.targetWidgetId,
view.targetWidgetInstanceId,
view.targetWidgetId,
);
}

function messageTargetsThisWidget(raw) {
const target = targetWidgetInstanceId(raw);
if (!target) return true;
return target === currentWidgetInstanceId();
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
if (raw.structuredContent && typeof raw.structuredContent === "object") return pickPayload(raw.structuredContent);
if (raw.payload && typeof raw.payload === "object") return pickPayload(raw.payload);
if (
Array.isArray(raw.data) ||
raw.table ||
raw.chart ||
raw.result_table ||
raw.visualization_spec ||
raw.widget_type === "table" ||
Array.isArray(raw.rows)
) {
return raw;
}
return null;
}

function currentHostPayload() {
return (
pickPayload(window.openai && window.openai.toolOutput) ||
pickPayload(window.openai && window.openai.toolResponseMetadata)
);
}

function currentHostDisplayMode() {
const hostApi = window.openai || {};
return (
urlDisplayMode ||
hostApi.displayMode ||
(hostApi.view && hostApi.view.displayMode) ||
(hostApi.hostContext && hostApi.hostContext.displayMode) ||
(hostApi.host && hostApi.host.displayMode) ||
displayMode
);
}

function hostSupportsDisplayMode() {
const hostApi = window.openai || {};
const availableDisplayModes =
hostApi.availableDisplayModes ||
(hostApi.hostContext && hostApi.hostContext.availableDisplayModes) ||
(hostApi.view && hostApi.view.availableDisplayModes);
if (Array.isArray(availableDisplayModes) && availableDisplayModes.includes("fullscreen")) {
return true;
}
return Boolean(window.openai) || typeof hostApi.requestDisplayMode === "function";
}

function hostedEmptyPayload() {
return { title: "Data Analytics chart", data: [] };
}

function payloadSignature(value) {
try {
return JSON.stringify(value);
} catch {
return String(Date.now());
}
}

function canApplyPayload(raw, routingContext = raw) {
if (!hasExternalPayload) return true;
const target = targetWidgetInstanceId(routingContext);
return Boolean(target && target === currentWidgetInstanceId());
}

function applyPayload(raw, routingContext = raw) {
if (!canApplyPayload(raw, routingContext)) return false;
const next = pickPayload(raw);
if (!next) return false;
const signature = payloadSignature(next);
hasExternalPayload = true;
if (signature === lastPayloadSignature) return true;
lastPayloadSignature = signature;
normalizePayload(next);
render();
return true;
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
if (mode === "inline" || mode === "fullscreen" || mode === "modal") {
setDisplayMode(mode);
}
}

async function requestDisplayMode(mode) {
const hostApi = window.openai || {};
setDisplayMode(mode);
if (typeof hostApi.requestDisplayMode !== "function") {
return { mode };
}

try {
const result = await hostApi.requestDisplayMode({ mode });
if (result && (result.mode === "inline" || result.mode === "fullscreen" || result.mode === "modal")) {
setDisplayMode(result.mode);
return result;
}
} catch {
setDisplayMode(currentHostDisplayMode());
}
return { mode: displayMode };
}

function setDisplayMode(mode) {
if (mode !== "inline" && mode !== "fullscreen" && mode !== "modal") return;
const changed = displayMode !== mode;
displayMode = mode;
const widget = document.querySelector(".widget");
if (widget) {
widget.dataset.displayMode = mode;
const instanceId = currentWidgetInstanceId();
if (instanceId) widget.dataset.widgetInstanceId = instanceId;
}
document.documentElement.dataset.displayMode = mode;
document.body.dataset.displayMode = mode;
applySplitLayout();
const button = document.getElementById("display-mode-button");
if (!button) return;
const showInlineExpand = mode === "inline" && hostSupportsDisplayMode();
button.hidden = !showInlineExpand;
button.title = "Expand chart";
button.setAttribute("aria-label", "Expand chart");
const modalCloseButton = document.getElementById("modal-title-close-button");
if (modalCloseButton) modalCloseButton.hidden = mode !== "modal";
if (changed) render();
}

function setViewMode(mode) {
viewMode = canonicalViewMode(mode);
const widget = document.querySelector(".widget");
if (widget) widget.dataset.viewMode = viewMode;
document.querySelectorAll("[data-view-mode-choice]").forEach((button) => {
button.setAttribute("aria-pressed", String(button.dataset.viewModeChoice === viewMode));
});
applySplitLayout();
}

function clampSplitFraction(value) {
const parsed = Number(value);
if (!Number.isFinite(parsed)) return defaultSplitFraction;
return Math.min(maxSplitFraction, Math.max(minSplitFraction, parsed));
}

function splitStorageKey() {
const title = text((activeDataset() && activeDataset().title) || payload.title || "default").slice(0, 80);
return `${splitStorageKeyPrefix}${currentWidgetInstanceId() || "local"}:${title}`;
}

function readStoredSplitFraction() {
try {
return clampSplitFraction(window.localStorage.getItem(splitStorageKey()) || defaultSplitFraction);
} catch {
return defaultSplitFraction;
}
}

function writeStoredSplitFraction() {
try {
window.localStorage.setItem(splitStorageKey(), String(splitFraction));
} catch {
// Ignore storage failures; the current drag still applies for this session.
}
}

function shouldUseSplitLayout() {
return false;
}

function splitMetrics() {
const appMain = document.querySelector(".app-main");
const controls = document.getElementById("controls");
const resizer = document.getElementById("split-resizer");
if (!appMain || !resizer) return null;
appMain.style.gridTemplateRows = "";
const controlsVisible = controls && !controls.hidden && window.getComputedStyle(controls).display !== "none";
const controlsHeight = controlsVisible ? controls.getBoundingClientRect().height : 0;
const resizerHeight = resizer.getBoundingClientRect().height || 12;
const availableHeight = appMain.clientHeight - controlsHeight - resizerHeight;
if (availableHeight <= 0) return null;
return { appMain, resizer, controlsHeight, resizerHeight, availableHeight };
}

function resetSplitLayout() {
const appMain = document.querySelector(".app-main");
if (appMain) appMain.style.gridTemplateRows = "";
resizeChartInstance();
}

function applySplitLayout() {
if (resizeFrame) window.cancelAnimationFrame(resizeFrame);
resizeFrame = window.requestAnimationFrame(() => {
resizeFrame = 0;
if (!shouldUseSplitLayout()) {
resetSplitLayout();
return;
}
const metrics = splitMetrics();
if (!metrics) return;
const minChartHeight = Math.min(260, metrics.availableHeight * 0.5);
const minBottomHeight = Math.min(190, metrics.availableHeight * 0.4);
const lowerBound = Math.max(minSplitFraction, minChartHeight / metrics.availableHeight);
const upperBound = Math.min(maxSplitFraction, 1 - minBottomHeight / metrics.availableHeight);
const effectiveFraction = Math.min(Math.max(splitFraction, lowerBound), Math.max(lowerBound, upperBound));
const chartHeight = Math.round(metrics.availableHeight * effectiveFraction);
const bottomHeight = Math.max(0, metrics.availableHeight - chartHeight);
metrics.appMain.style.gridTemplateRows = `${Math.round(metrics.controlsHeight)}px ${chartHeight}px ${Math.round(metrics.resizerHeight)}px ${bottomHeight}px`;
metrics.resizer.setAttribute("aria-valuenow", String(Math.round(effectiveFraction * 100)));
resizeChartInstance();
});
}

function setSplitFraction(nextFraction, options = {}) {
splitFraction = clampSplitFraction(nextFraction);
if (options.persist) writeStoredSplitFraction();
applySplitLayout();
}

function setSplitFractionFromPointer(clientY, options = {}) {
const metrics = splitMetrics();
if (!metrics) return;
const rect = metrics.appMain.getBoundingClientRect();
const chartHeight = clientY - rect.top - metrics.controlsHeight - metrics.resizerHeight / 2;
setSplitFraction(chartHeight / metrics.availableHeight, options);
}

function setupSplitResizer() {
const resizer = document.getElementById("split-resizer");
const widget = document.querySelector(".widget");
if (!resizer) return;
let activePointerId = null;

resizer.addEventListener("pointerdown", (event) => {
if (!shouldUseSplitLayout()) return;
activePointerId = event.pointerId;
resizer.setPointerCapture?.(event.pointerId);
widget?.classList.add("is-resizing");
setSplitFractionFromPointer(event.clientY);
event.preventDefault();
});

resizer.addEventListener("pointermove", (event) => {
if (activePointerId !== event.pointerId) return;
setSplitFractionFromPointer(event.clientY);
});

const finishPointerDrag = (event) => {
if (activePointerId !== event.pointerId) return;
activePointerId = null;
widget?.classList.remove("is-resizing");
writeStoredSplitFraction();
};
resizer.addEventListener("pointerup", finishPointerDrag);
resizer.addEventListener("pointercancel", finishPointerDrag);
resizer.addEventListener("lostpointercapture", () => {
activePointerId = null;
widget?.classList.remove("is-resizing");
});

resizer.addEventListener("dblclick", () => {
setSplitFraction(defaultSplitFraction, { persist: true });
});

resizer.addEventListener("keydown", (event) => {
if (!shouldUseSplitLayout()) return;
if (event.key === "ArrowUp") {
setSplitFraction(splitFraction - 0.03, { persist: true });
event.preventDefault();
} else if (event.key === "ArrowDown") {
setSplitFraction(splitFraction + 0.03, { persist: true });
event.preventDefault();
} else if (event.key === "Home") {
setSplitFraction(defaultSplitFraction, { persist: true });
event.preventDefault();
} else if (event.key === "End") {
setSplitFraction(maxSplitFraction, { persist: true });
event.preventDefault();
}
});
}

function setupViewModeControls() {
document.querySelectorAll("[data-view-mode-choice]").forEach((button) => {
button.addEventListener("click", () => {
setViewMode(button.dataset.viewModeChoice);
});
});
setViewMode(viewMode);
}

function canonicalDataMode(value) {
const raw = text(value || "").toLowerCase();
return raw === "query" || raw === "sql" || raw === "python" || raw === "code" ? "query" : "table";
}

function setDataMode(mode) {
dataMode = canonicalDataMode(mode);
const widget = document.querySelector(".widget");
const bottomSplit = document.getElementById("bottom-split");
if (widget) widget.dataset.dataMode = dataMode;
if (bottomSplit) bottomSplit.dataset.dataMode = dataMode;
document.querySelectorAll(".data-mode-segmented").forEach((control) => {
control.dataset.activeMode = dataMode;
});
document.querySelectorAll("[data-data-mode-choice]").forEach((button) => {
button.setAttribute("aria-pressed", String(button.dataset.dataModeChoice === dataMode));
});
}

function setupDataModeControls() {
document.querySelectorAll("[data-data-mode-choice]").forEach((button) => {
button.addEventListener("click", () => {
setDataMode(button.dataset.dataModeChoice);
});
});
setDataMode(dataMode);
}

function setupDisplayModeControls() {
const button = document.getElementById("display-mode-button");
const backButton = document.getElementById("detail-back-button");
const modalCloseButton = document.getElementById("modal-title-close-button");
const toggleDisplayMode = () => {
if (!button) return;
button.disabled = true;
const nextMode = isDetailDisplayMode() ? "inline" : "fullscreen";
requestDisplayMode(nextMode).finally(() => {
button.disabled = false;
});
};
if (button) button.addEventListener("click", toggleDisplayMode);
if (backButton) {
backButton.addEventListener("click", () => {
requestDisplayMode("inline");
});
}
if (modalCloseButton) {
modalCloseButton.addEventListener("click", () => {
requestDisplayMode("inline");
});
}
setDisplayMode(currentHostDisplayMode());
}

function asArray(value) {
return Array.isArray(value) ? value : [];
}

function text(value) {
return value == null ? "" : String(value);
}

function number(value) {
const parsed = Number(value);
return Number.isFinite(parsed) ? parsed : null;
}

function valueFor(dataset, key, fallback = null) {
return dataset && dataset[key] != null ? dataset[key] : payload[key] != null ? payload[key] : fallback;
}

function objectFor(dataset, key) {
const value = valueFor(dataset, key);
return value && typeof value === "object" && !Array.isArray(value) ? value : null;
}

function resultTableFor(dataset) {
return objectFor(dataset, "table") || objectFor(dataset, "result_table") || null;
}

function sourceQueryFor(dataset) {
return sourceQueryFromSource(objectFor(dataset, "source"));
}

function sourceLabelFor(dataset) {
const source = valueFor(dataset, "source", payload.source);
if (source && typeof source === "object" && !Array.isArray(source)) return text(source.label);
return text(source);
}

function sqlTextFor(dataset) {
return sourceCodeText(sourceQueryFor(dataset));
}

function queryLanguageFor(dataset) {
return sourceCodeLanguage(sourceQueryFor(dataset));
}

function compactList(values) {
return values.map((value) => text(value).trim()).filter(Boolean);
}

function listFromValue(value) {
if (Array.isArray(value)) {
return compactList(value.map((item) => {
if (item && typeof item === "object") {
const label = item.label || item.name || item.table || item.field || item.metric || item.id;
const detail = item.description || item.definition || item.value || item.expression;
return label && detail ? `${label}: ${detail}` : label || detail;
}
return item;
}));
}
if (value && typeof value === "object") {
return compactList(Object.entries(value).map(([key, item]) => `${key}: ${item}`));
}
return compactList([value]);
}

function firstListFromObjects(objects, keys) {
for (const object of objects) {
if (!object) continue;
for (const key of keys) {
const values = listFromValue(object[key]);
if (values.length) return values;
}
}
return [];
}

function isLikelySourceTableName(value) {
const tableName = text(value).trim().replace(/^[`"\[]|[`"\]]$/g, "");
return /^[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+){1,3}$/.test(tableName);
}

function sourceTableNamesFromMetadata(objects) {
return firstListFromObjects(objects, [
"tables_used",
"tablesUsed",
"source_tables",
"sourceTables",
"tables",
]).filter(isLikelySourceTableName);
}

function extractTablesFromSql(sql) {
const tables = [];
const seen = new Set();
const pattern = /\b(?:from|join)\s+([`"\[]?[\w.-]+(?:\.[\w.-]+){0,3}[`"\]]?)/gi;
let match;
while ((match = pattern.exec(sql))) {
const table = match[1].replace(/^[`"\[]|[`"\]]$/g, "");
const normalized = table.toLowerCase();
if (!table || seen.has(normalized)) continue;
seen.add(normalized);
tables.push(table);
}
return tables;
}

function sourceMetadataObjects(dataset) {
return [
objectFor(dataset, "source"),
sourceQueryFor(dataset),
objectFor(dataset, "display"),
objectFor(dataset, "chart"),
dataset && typeof dataset === "object" ? dataset : null,
payload && typeof payload === "object" ? payload : null,
];
}

function metricDefinitionList(dataset) {
const explicit = firstListFromObjects(sourceMetadataObjects(dataset), [
"metric_definitions",
"metricDefinitions",
"metrics_definition",
"metricDefinition",
]);
if (explicit.length) return explicit;
const table = resultTableFor(dataset) || {};
const columns = asArray(table.columns);
const yFields = asArray(visualizationSpecFor(dataset).encodings?.y?.fields);
const yField = visualizationSpecFor(dataset).encodings?.y?.field || chartConfig.yField;
const metricFields = new Set(compactList([yField, ...yFields]));
return compactList(columns
.filter((column) => column && (!metricFields.size || metricFields.has(column.key)))
.map((column) => `${column.label || column.key}: displayed from ${column.key}${column.unit ? ` (${column.unit})` : ""}`))
.slice(0, 6);
}

function sourceDetailText(values, fallback = "Not declared") {
const items = compactList(Array.isArray(values) ? values : [values]);
return items.length ? items.join("; ") : fallback;
}

function sourceDetailList(values, fallback = "Not declared") {
const items = compactList(Array.isArray(values) ? values : [values]);
return items.length ? items : [fallback];
}

function sourceFieldsForDataset(dataset) {
const spec = visualizationSpecFor(dataset);
const fields = new Set();
function addField(field) {
if (field) fields.add(field);
}
addField(spec.encodings?.x?.field);
addField(spec.encodings?.y?.field);
for (const field of spec.encodings?.y?.fields ?? []) addField(field);
addField(spec.encodings?.color?.field);
return Array.from(fields);
}

function visualizationSpecFor(dataset) {
const chart = objectFor(dataset, "chart");
if (chart) {
const fields = chart.fields && typeof chart.fields === "object" && !Array.isArray(chart.fields)
? chart.fields
: {};
const options = chart.options && typeof chart.options === "object" && !Array.isArray(chart.options)
? chart.options
: {};
const display = objectFor(dataset, "display") || {};
return {
visualization_type: chart.type,
encodings: fields,
settings: {
...(options.orientation != null ? { orientation: options.orientation } : {}),
...(options.grouping != null ? { group_mode: options.grouping } : {}),
...(options.points != null ? { show_points: options.points } : {}),
...(options.multi_measure_series != null
? { multi_measure_series: options.multi_measure_series }
: {}),
},
presentation: {
...(display.unit != null ? { unit: display.unit } : {}),
...(display.baseline != null ? { baseline: display.baseline } : {}),
...(display.x_axis_title != null ? { x_axis_title: display.x_axis_title } : {}),
...(display.y_axis_title != null ? { y_axis_title: display.y_axis_title } : {}),
...(display.controls != null ? { show_controls: display.controls } : {}),
},
};
}
return objectFor(dataset, "visualization_spec") || {};
}

function chartSpecFor(dataset) {
return objectFor(dataset, "chart_spec") || {};
}

function specEncodings(dataset) {
const encodings = visualizationSpecFor(dataset).encodings;
return encodings && typeof encodings === "object" ? encodings : {};
}

function specEncoding(dataset, role) {
const encoding = specEncodings(dataset)[role];
return encoding && typeof encoding === "object" ? encoding : {};
}

function specPresentation(dataset) {
const presentation = visualizationSpecFor(dataset).presentation;
return presentation && typeof presentation === "object" ? presentation : {};
}

function specSettings(dataset) {
const settings = visualizationSpecFor(dataset).settings;
if (settings && typeof settings === "object" && !Array.isArray(settings)) return settings;
return objectFor(dataset, "settings") || {};
}

function specValue(dataset, key, fallback = null) {
const presentation = specPresentation(dataset);
return presentation[key] != null ? presentation[key] : valueFor(dataset, key, fallback);
}

function selectedMeasureColumn(dataset) {
return asArray(resultTableFor(dataset)?.columns).find(
(column) => column && column.key === chartConfig.yField,
);
}

function columnValueFormat(column) {
const format = text(column?.format);
if (["compact", "number", "percent", "currency"].includes(format)) return format;
const type = text(column?.type);
if (["number", "percent", "currency"].includes(type)) return type;
return null;
}

function valueFormatFor(dataset, existing = chartSpecFor(dataset)) {
return existing.valueFormat || columnValueFormat(selectedMeasureColumn(dataset));
}

function currentWidgetSpec() {
const dataset = activeDataset();
const valueFormat = valueFormatFor(dataset);
return {
version: "1",
visualization_type: activeVisualizationType,
encodings: {
x: {
field: chartConfig.xField,
type: fieldLooksDateLike(dataset, chartConfig.xField) ? "temporal" : "nominal",
...(chartConfig.timeUnit && chartConfig.timeUnit !== "none" ? { time_unit: chartConfig.timeUnit } : {}),
},
y: {
aggregate: chartConfig.yAggregation,
field: chartConfig.yField,
type: "quantitative",
...(valueFormat ? { format: valueFormat } : {}),
...(unitFor(dataset) ? { unit: unitFor(dataset) } : {}),
},
...(chartConfig.colorField ? { color: { field: chartConfig.colorField, type: "nominal" } } : {}),
...(chartConfig.lineStyleField ? { lineStyle: { field: chartConfig.lineStyleField, type: "nominal" } } : {}),
...(chartConfig.labelField ? { label: { field: chartConfig.labelField, type: "text" } } : {}),
...(chartConfig.sizeField ? { size: { field: chartConfig.sizeField, type: "quantitative" } } : {}),
},
presentation: {
data_mode: dataMode,
unit: unitFor(dataset),
view_mode: viewMode,
},
settings: {
orientation: chartSettings.barOrientation,
group_mode: chartSettings.barGroupMode,
},
};
}

function syntheticSeriesField(value, index) {
const slug = text(value || "value").toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "").slice(0, 40);
return `__series_${index}_${slug || "value"}`;
}

function uniqueProjectedSeriesValues(rows) {
const values = [];
const seen = new Set();
for (const row of rows) {
const value = text((row && row.series) || "Value");
if (seen.has(value)) continue;
seen.add(value);
values.push(value);
}
return values;
}

function projectedRowsUseColorEncoding(rows) {
return Boolean(chartConfig.colorField) || usesMeasureNames() || uniqueProjectedSeriesValues(rows).length > 1;
}

function projectedRenderRows(rows) {
return rows.map((row) => {
const output = {};
for (const [key, value] of Object.entries(row || {})) {
if (key === "raw") continue;
output[key] = value;
}
return output;
});
}

function projectedRenderColumns(rows, dataset) {
const valueFormat = valueFormatFor(dataset);
const columns = [
{
key: "x",
label: fieldLabel(dataset, chartConfig.xField, "X"),
type: fieldLooksDateLike(dataset, chartConfig.xField) ? "date" : "text",
},
{
key: "y",
label: fieldLabel(dataset, chartConfig.yField, "Value"),
type: "number",
...(valueFormat ? { format: valueFormat } : {}),
unit: unitFor(dataset),
},
];
if (projectedRowsUseColorEncoding(rows)) {
columns.splice(1, 0, { key: "series", label: "Series", type: "text" });
}
if (rows.some((row) => row && row.size != null)) {
columns.push({ key: "size", label: fieldLabel(dataset, chartConfig.sizeField, "Size"), type: "number" });
}
if (rows.some((row) => row && row.lineStyle != null)) {
columns.push({ key: "lineStyle", label: "Line style", type: "text" });
}
if (rows.some((row) => row && row.label != null)) {
columns.push({ key: "label", label: fieldLabel(dataset, chartConfig.labelField, "Label"), type: "text" });
}
return columns;
}

function projectedChartSpec(dataset, type, rows) {
const existing = chartSpecFor(dataset);
const sourceSettings = specSettings(dataset);
const useColor = projectedRowsUseColorEncoding(rows);
const xAxisTitle = specValue(dataset, "x_axis_title", existing.xAxisTitle);
const yAxisTitle = specValue(dataset, "y_axis_title", existing.yAxisTitle);
const valueFormat = valueFormatFor(dataset, existing);
return {
id: text(existing.id || valueFor(dataset, "id", "default")) || "default",
title: text(valueFor(dataset, "title", payload.title || "Data Analytics chart")),
subtitle: specValue(dataset, "subtitle", payload.subtitle),
type,
dataset: text(valueFor(dataset, "dataset", valueFor(dataset, "id", "default"))) || "default",
encodings: {
x: {
field: "x",
label: fieldLabel(dataset, chartConfig.xField, "X"),
type: fieldLooksDateLike(dataset, chartConfig.xField) ? "temporal" : "nominal",
...(chartConfig.timeUnit && chartConfig.timeUnit !== "none" ? { time_unit: chartConfig.timeUnit } : {}),
},
y: {
aggregate: "none",
field: "y",
label: fieldLabel(dataset, chartConfig.yField, "Value"),
type: "quantitative",
...(valueFormat ? { format: valueFormat } : {}),
unit: unitFor(dataset),
},
...(useColor ? { color: { field: "series", label: "Series", type: "nominal" } } : {}),
...(rows.some((row) => row && row.lineStyle != null)
? { lineStyle: { field: "lineStyle", label: "Line style", type: "nominal" } }
: {}),
...(rows.some((row) => row && row.label != null)
? { label: { field: "label", label: fieldLabel(dataset, chartConfig.labelField, "Label"), type: "text" } }
: {}),
...(rows.some((row) => row && row.size != null)
? { size: { field: "size", label: fieldLabel(dataset, chartConfig.sizeField, "Size"), type: "quantitative" } }
: {}),
},
...(xAxisTitle != null ? { xAxisTitle } : {}),
...(yAxisTitle != null ? { yAxisTitle } : {}),
unit: unitFor(dataset),
valueFormat,
settings: {
orientation: chartSettings.barOrientation,
groupMode: chartSettings.barGroupMode,
group_mode: chartSettings.barGroupMode,
...(sourceSettings.showPoints != null || sourceSettings.show_points != null
? {
showPoints: sourceSettings.showPoints ?? sourceSettings.show_points,
show_points: sourceSettings.show_points ?? sourceSettings.showPoints,
}
: {}),
},
surface: {
...(existing.surface || {}),
surface: isDetailDisplayMode() ? "explorer" : "compact",
showControls: Boolean(specValue(dataset, "show_controls", payload.show_controls)),
},
};
}

function notifyChartSpecChange() {
if (typeof window.parent?.postMessage !== "function" || window.parent === window) return;
window.parent.postMessage(
{
type: "datascience-chart-widget-spec-change",
widgetInstanceId: currentWidgetInstanceId(),
visualization_spec: currentWidgetSpec(),
},
"*",
);
}

function notifyChartSpecReset() {
if (typeof window.parent?.postMessage !== "function" || window.parent === window) return;
window.parent.postMessage(
{
type: "datascience-chart-widget-spec-reset",
widgetInstanceId: currentWidgetInstanceId(),
},
"*",
);
}

function widgetVisualizationType(type) {
return canonicalVisualizationType(type);
}

function canonicalBarOrientation(value, fallback = "vertical") {
const raw = text(value || "").trim().toLowerCase().replaceAll("_", "").replaceAll("-", "");
if (raw === "vertical" || raw === "column") return "vertical";
if (raw === "horizontal") return "horizontal";
if (raw === "auto" || raw === "automatic") return fallback;
return fallback;
}

function canonicalBarGroupMode(value, fallback = "grouped") {
const raw = text(value || "").trim().toLowerCase().replaceAll("_", "").replaceAll("-", "").replaceAll("%", "100");
if (raw === "single") return "single";
if (raw === "grouped" || raw === "group") return "grouped";
if (raw === "stacked" || raw === "stack") return "stacked";
if (raw === "stacked100" || raw === "stack100" || raw === "100" || raw === "100stacked") return "stacked100";
return fallback;
}

function resetChartSettings(dataset = activeDataset(), requestedType = activeVisualizationType) {
const settings = specSettings(dataset);
chartSettings = {
barOrientation: canonicalBarOrientation(
settings.orientation ?? settings.bar_orientation ?? valueFor(dataset, "bar_orientation"),
"vertical",
),
barGroupMode: canonicalBarGroupMode(
settings.group_mode ?? settings.groupMode ?? settings.bar_group_mode ?? valueFor(dataset, "bar_group_mode"),
"grouped",
),
};
}

function rendererBarOrientation() {
return chartSettings.barOrientation === "horizontal" ? "horizontal" : "vertical";
}

function rendererVisualizationType(type = activeVisualizationType) {
const canonical = widgetVisualizationType(type);
return canonical;
}

function applyChartSettingsAttributes() {
const widget = document.querySelector(".widget");
if (!widget) return;
widget.dataset.barOrientation = chartSettings.barOrientation;
widget.dataset.barGroupMode = chartSettings.barGroupMode;
}

function unitFor(dataset) {
const selectedMeasure = selectedMeasureColumn(dataset);
if (selectedMeasure?.unit != null && text(selectedMeasure.unit).trim()) {
return text(selectedMeasure.unit).trim();
}
return specValue(dataset, "unit", payload.unit);
}

function activeDataset() {
return payload;
}

function isTablePayload(dataset) {
return (
valueFor(dataset, "widget_type", payload.widget_type) === "table" ||
visualizationSpecFor(dataset).visualization_type === "table"
);
}

function setQueryStatus(message) {
const status = document.getElementById("query-status");
if (status) status.textContent = message || "";
}

function formatRunTime(value) {
const raw = text(value);
if (!raw) return "";
const date = new Date(raw);
if (!Number.isFinite(date.getTime())) return raw;
return new Intl.DateTimeFormat(undefined, {
day: "numeric",
hour: "numeric",
minute: "2-digit",
month: "short",
year: "numeric",
}).format(date);
}

function renderDetailHeader(dataset, title, subtitle) {
const detailTitle = document.getElementById("detail-title");
const detailSubtitle = document.getElementById("detail-subtitle");
const runTime = document.getElementById("detail-run-time");
const sourceQuery = sourceQueryFor(dataset) || {};
if (detailTitle) detailTitle.textContent = text(title);
if (detailSubtitle) {
detailSubtitle.textContent = text(subtitle);
detailSubtitle.hidden = !subtitle;
}
if (runTime) {
const formatted = formatRunTime(sourceQuery.executed_at || valueFor(dataset, "executed_at", payload.executed_at));
runTime.textContent = formatted;
const refreshButton = document.getElementById("detail-refresh-button");
if (refreshButton) refreshButton.hidden = !formatted;
}
}

function renderQueryControls(dataset) {
if (displayMode !== "fullscreen") {
setQueryStatus("");
return;
}
const sourceQuery = sourceQueryFor(dataset);
const resultTable = resultTableFor(dataset);
const label =
(sourceQuery && (sourceQuery.label || sourceQuery.id || sourceQuery.engine));
const rowCount = resultTable && Number.isFinite(Number(resultTable.row_count)) ? Number(resultTable.row_count) : null;
const suffix = rowCount != null ? ` · ${formatNumber(rowCount, 0)} rows${resultTable.truncated ? " sampled" : ""}` : "";
setQueryStatus(label ? `${label}${suffix}` : "");
}

function setupMenuDismissal() {
document.addEventListener("click", () => {
closeFieldMenus();
closeChartPicker();
closeDataFilterMenus();
closeShareMenu();
});
document.addEventListener("keydown", (event) => {
if (event.key === "Escape") {
closeFieldMenus();
closeChartPicker();
closeDataFilterMenus();
closeShareMenu();
}
});
}

function canonicalViewMode(value) {
const raw = text(value || "").toLowerCase().replaceAll("-", "_").replaceAll(" ", "_");
if (raw === "vis" || raw === "viz" || raw === "chart") return "visualization";
if (raw === "table" || raw === "data") return "table";
if (raw === "both" || raw === "split") return "both";
return "both";
}

function normalizePayload(nextPayload) {
payload = nextPayload || fallbackPayload;
const requestedVisualizationType =
visualizationSpecFor(activeDataset()).visualization_type;
activeVisualizationType = widgetVisualizationType(requestedVisualizationType);
resetChartSettings(activeDataset(), requestedVisualizationType);
viewMode = canonicalViewMode(viewMode);
dataMode = canonicalDataMode(specValue(activeDataset(), "data_mode", payload.data_mode || dataMode));
selectedDataFilters = {};
splitFraction = readStoredSplitFraction();
resetChartConfig(activeDataset());
resetVisibleSeries();
}

function resetVisibleSeries() {
const names = rechartsLegendNamesForDataset(projectedDataset(activeDataset()), activeVisualizationType);
visibleSeries = new Set(names);
visibleSeriesSignature = names.join("\u0000");
}

function orderedVisibleSeries(seriesNames, selectedSeries) {
const selected = selectedSeries instanceof Set ? selectedSeries : new Set(asArray(selectedSeries).map(text));
return new Set(asArray(seriesNames).map(text).filter((series) => selected.has(series)));
}

function reconcileVisibleSeries(seriesNames) {
const names = asArray(seriesNames).map(text);
const signature = names.join("\u0000");
if (revealAllSeriesAfterGroupingChange) {
visibleSeries = new Set(names);
visibleSeriesSignature = signature;
revealAllSeriesAfterGroupingChange = false;
return;
}
if (signature === visibleSeriesSignature) return;
const available = new Set(names);
const stillVisible = [...visibleSeries].filter((series) => available.has(series));
visibleSeries = stillVisible.length ? orderedVisibleSeries(names, new Set(stillVisible)) : new Set(names);
visibleSeriesSignature = signature;
}

const COMPACT_VALUE_THRESHOLD = 100000;

function compactDigits(value) {
const absolute = Math.abs(value);
if (absolute >= COMPACT_VALUE_THRESHOLD) return 1;
return 2;
}

function formatNumber(value, compact = false) {
const numeric = number(value);
if (numeric == null) return "";
const absolute = Math.abs(numeric);
return new Intl.NumberFormat(undefined, {
maximumFractionDigits: compactDigits(numeric),
notation: compact && absolute >= COMPACT_VALUE_THRESHOLD ? "compact" : "standard",
}).format(numeric);
}

function isUsdUnit(unit) {
return unit === "$" || text(unit).toUpperCase() === "USD";
}

function unitScaleSuffix(unit) {
const normalized = text(unit).toLowerCase();
if (normalized === "usd millions" || normalized === "usd million") return "M";
if (normalized === "usd billions" || normalized === "usd billion") return "B";
if (normalized === "usd thousands" || normalized === "usd thousand") return "K";
if (/^\$[kmbt]$/i.test(text(unit))) return text(unit).slice(1).toUpperCase();
return null;
}

function formatCurrency(value) {
const numeric = number(value);
if (numeric == null) return "";
const absolute = Math.abs(numeric);
return new Intl.NumberFormat(undefined, {
currency: "USD",
maximumFractionDigits: compactDigits(numeric),
notation: absolute >= COMPACT_VALUE_THRESHOLD ? "compact" : "standard",
style: "currency",
}).format(numeric);
}

function formatValue(value, unit) {
const cleanUnit = text(unit);
if (!cleanUnit) return formatNumber(value, true);
if (cleanUnit === "%" || cleanUnit.startsWith("%")) return `${formatNumber(value)}%`;
if (isUsdUnit(cleanUnit)) return formatCurrency(value);
const scaleSuffix = unitScaleSuffix(cleanUnit);
if (scaleSuffix) return `$${formatNumber(value)}${scaleSuffix}`;
if (cleanUnit.startsWith("$")) return `$${formatNumber(value)}${cleanUnit.slice(1)}`;
return `${formatNumber(value, true)} ${cleanUnit}`;
}

function formatTableCell(value, type) {
if (value == null) return "";
const numeric = number(value);
if (type === "number" && numeric != null) return formatNumber(numeric, true);
if (type === "percent" && numeric != null) return `${formatNumber(numeric * 100)}%`;
if (type === "currency" && numeric != null) return formatCurrency(numeric);
return text(value);
}

function tableColumns(dataset, rows) {
const resultTable = resultTableFor(dataset);
const columns = asArray(resultTable && resultTable.columns);
if (columns.length) return columns;
const keys = Object.keys(rows[0] || {});
return keys.map((key) => ({ key, label: key }));
}

function rawChartRows(dataset) {
const resultTable = resultTableFor(dataset);
const resultRows = resultTable && Array.isArray(resultTable.rows) ? resultTable.rows : null;
if (resultRows) {
return resultRows.map((row) => (row && typeof row === "object" ? { ...row } : {}));
}
return asArray(dataset.data).map((point) => {
const row = point && typeof point === "object" ? { ...point } : {};
row.x = text(point && point.x);
row.series = text((point && point.series) || "Value");
row.y = number(point && point.y);
if (point && point.label != null) row.label = point.label;
return row;
});
}

function dataFilterKey(dataset, fieldKey) {
return `${text(dataset && dataset.id) || "default"}\u0000${fieldKey}`;
}

function selectedDataFilterValue(dataset, fieldKey) {
return selectedDataFilters[dataFilterKey(dataset, fieldKey)] || "all";
}

function uniqueFilterValues(rows, fieldKey) {
const seen = new Set();
const values = [];
for (const row of rows) {
const value = text(row && row[fieldKey]);
if (!value || seen.has(value)) continue;
seen.add(value);
values.push(value);
}
return values.sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));
}

function filterRowsExcluding(dataset, rows, excludedFieldKey) {
const specs = dataFilterSpecs(dataset);
if (!specs.length) return rows;
return rows.filter((row) =>
specs.every((spec) => {
if (spec.key === excludedFieldKey) return true;
const selected = selectedDataFilterValue(dataset, spec.key);
return selected === "all" || text(row && row[spec.key]) === selected;
}),
);
}

function filterOptionsForSpec(dataset, spec) {
return uniqueFilterValues(filterRowsExcluding(dataset, rawChartRows(dataset), spec.key), spec.key);
}

function pruneDataFilters(dataset) {
let changed = true;
while (changed) {
changed = false;
for (const spec of dataFilterSpecs(dataset)) {
const key = dataFilterKey(dataset, spec.key);
const selected = selectedDataFilters[key];
if (!selected) continue;
if (!filterOptionsForSpec(dataset, spec).includes(selected)) {
delete selectedDataFilters[key];
changed = true;
}
}
}
}

function dataFilterSpecs(dataset) {
const rows = rawChartRows(dataset);
return availableFields(dataset)
.filter((field) => {
if (field.synthetic || field.numeric || field.type === "date") return false;
if (field.key === chartConfig.yField || field.key === measureNamesField) return false;
if (fieldLooksDateLike(dataset, field.key)) return false;
const values = uniqueFilterValues(rows, field.key);
return values.length > 1 && values.length <= 24;
})
.map((field) => ({
...field,
options: uniqueFilterValues(rows, field.key),
}));
}

function applyDataFilters(dataset, rows) {
const specs = dataFilterSpecs(dataset);
if (!specs.length) return rows;
return rows.filter((row) =>
specs.every((spec) => {
const selected = selectedDataFilterValue(dataset, spec.key);
return selected === "all" || text(row && row[spec.key]) === selected;
}),
);
}

function chartRows(dataset) {
return applyDataFilters(dataset, rawChartRows(dataset));
}

function chartColumns(rows, dataset = activeDataset()) {
const resultTable = resultTableFor(dataset);
const declared = asArray(resultTable && resultTable.columns)
.map((column) => column && column.key)
.filter((key) => typeof key === "string" && key);
if (declared.length) return declared;
const preferred = resultTable ? [] : ["series", "x", "y", "label"];
const seen = new Set();
const keys = [];
for (const key of preferred) {
if (rows.some((row) => row[key] != null && row[key] !== "")) {
seen.add(key);
keys.push(key);
}
}
for (const row of rows) {
for (const key of Object.keys(row)) {
if (seen.has(key)) continue;
seen.add(key);
keys.push(key);
}
}
return keys;
}

function columnLabel(key, dataset = activeDataset()) {
if (key === measureNamesField) return "Measure names";
const resultTable = resultTableFor(dataset);
const declared = asArray(resultTable && resultTable.columns).find((column) => column && column.key === key);
if (declared && declared.label) return text(declared.label);
const labels = {
x: "X",
y: "Y",
series: "Series",
label: "Label",
};
return labels[key] || key.replaceAll("_", " ").replace(/\b\w/g, (char) => char.toUpperCase());
}

function columnType(dataset, key) {
const resultTable = resultTableFor(dataset);
const declared = asArray(resultTable && resultTable.columns).find((column) => column && column.key === key);
return declared && declared.type ? text(declared.type) : "";
}

function columnUnit(dataset, key) {
const resultTable = resultTableFor(dataset);
const declared = asArray(resultTable && resultTable.columns).find((column) => column && column.key === key);
return declared && declared.unit != null ? text(declared.unit).trim() : "";
}

function isNumericColumn(rows, key, dataset = activeDataset()) {
const type = columnType(dataset, key);
if (["number", "percent", "currency"].includes(type)) return true;
if (["text", "date"].includes(type)) return false;
return rows.some((row) => number(row[key]) != null);
}

function availableFields(dataset) {
const rows = rawChartRows(dataset);
return chartColumns(rows, dataset).map((key) => ({
key,
label: columnLabel(key, dataset),
numeric: isNumericColumn(rows, key, dataset),
type: columnType(dataset, key),
}));
}

function hasField(dataset, key) {
if (key === measureNamesField) return compatibleMeasureNameFields(dataset).length > 1;
return availableFields(dataset).some((field) => field.key === key);
}

function fieldLabel(dataset, key, fallback = "None") {
const field = availableFields(dataset).find((item) => item.key === key);
return field ? field.label : fallback;
}

function colorGroupingRoleLabel(type = activeVisualizationType) {
type = widgetVisualizationType(type);
if (type === "pie") return "Slice by";
if (type === "heatmap") return "Y-axis";
if ((type === "bar" && (chartSettings.barGroupMode === "stacked" || chartSettings.barGroupMode === "stacked100")) || type === "stackedArea") return "Stack by";
if (type === "line" || type === "area") return "Series by";
if (type === "bar") return "Group by";
return "Color by";
}

function chartUsesSingleSeriesOnly(type = activeVisualizationType) {
return ["funnel", "leaderboard", "waterfall"].includes(widgetVisualizationType(type));
}

function chartRoleSpecs(type = activeVisualizationType) {
type = widgetVisualizationType(type);
if (type === "funnel") {
return [
{ role: "x", label: "Stage", fallback: "Stage", required: true, aggregate: false, time: false },
{ role: "y", label: "Value", fallback: "Value", required: true, aggregate: true, time: false },
];
}
if (type === "waterfall") {
return [
{ role: "x", label: "Step", fallback: "Step", required: true, aggregate: false, time: false },
{ role: "y", label: "Change", fallback: "Change", required: true, aggregate: true, time: false },
];
}
if (type === "leaderboard") {
return [
{ role: "x", label: "Category", fallback: "Category", required: true, aggregate: false, time: false },
{ role: "y", label: "Value", fallback: "Value", required: true, aggregate: true, time: false },
];
}
if (type === "pie") {
return [
{ role: "color", label: colorGroupingRoleLabel(type), fallback: "Slice", required: true, aggregate: false, time: false },
{ role: "y", label: "Value", fallback: "Value", required: true, aggregate: true, time: false },
];
}
if (type === "histogram") {
return [
{ role: "y", label: "Value", fallback: "Value", required: true, aggregate: false, time: false },
];
}
if (type === "scatter") {
return [
{ role: "x", label: "X-axis", fallback: "X-axis", required: true, aggregate: false, time: false, numeric: true },
{ role: "y", label: "Y-axis", fallback: "Y-axis", required: true, aggregate: false, time: false, numeric: true },
{ role: "size", label: "Size by", fallback: "None", required: false, aggregate: false, time: false, numeric: true },
{ role: "label", label: "Label by", fallback: "None", required: false, aggregate: false, time: false },
{ role: "color", label: colorGroupingRoleLabel(type), fallback: "None", required: false, aggregate: false, time: false },
];
}
if (type === "heatmap") {
return [
{ role: "x", label: "X-axis", fallback: "X-axis", required: true, aggregate: false, time: true },
{ role: "color", label: "Y-axis", fallback: "Y-axis", required: true, aggregate: false, time: false },
{ role: "y", label: "Value", fallback: "Value", required: true, aggregate: true, time: false },
];
}
return [
{ role: "x", label: "X-axis", fallback: "X-axis", required: true, aggregate: false, time: true },
{ role: "y", label: "Y-axis", fallback: "Y-axis", required: true, aggregate: true, time: false },
{ role: "color", label: colorGroupingRoleLabel(type), fallback: "None", required: false, aggregate: false, time: false },
];
}

function chartRoleSpec(role, type = activeVisualizationType) {
return chartRoleSpecs(type).find((spec) => spec.role === role) || { role, label: role, fallback: "None", required: false };
}

function detailControlLabel(spec) {
if (spec && spec.detailLabel) return spec.detailLabel;
if (spec && spec.label && !/^x-axis$|^y-axis$/i.test(spec.label)) {
return text(spec.label).replace("-axis", " axis");
}
if (spec && spec.role === "color" && /^y-axis$/i.test(spec.label || "")) return "Y axis";
if (spec && spec.role === "x") return "X axis";
if (spec && spec.role === "y") return "Y axis";
if (spec && spec.role === "size") return "Size by";
if (spec && spec.role === "label") return "Label by";
if (spec && spec.role === "color") return "Stack by";
if (spec && spec.role === "time") return "Time period";
return text((spec && spec.label) || "").replace("-axis", " axis");
}

function fieldKeyForRole(role) {
if (role === "x") return chartConfig.xField;
if (role === "y") return chartConfig.yField;
if (role === "size") return chartConfig.sizeField;
if (role === "label") return chartConfig.labelField;
if (role === "color") return chartConfig.colorField;
return "";
}

function compatibleFieldsForRole(dataset, role, type = activeVisualizationType) {
const fields = availableFields(dataset);
const spec = chartRoleSpec(role, type);
let compatible = fields;
if (["funnel", "leaderboard", "waterfall"].includes(widgetVisualizationType(type)) && role === "x") {
compatible = fields.filter((field) => !field.numeric);
}
if (role === "y" || role === "size" || spec.numeric) compatible = fields.filter((field) => field.numeric);
if (role === "color") {
const dimensions = fields.filter((field) => !field.numeric && field.key !== chartConfig.xField);
const measures = compatibleMeasureNameFields(dataset);
compatible = [
...dimensions,
...(measures.length > 1 ? [{ key: measureNamesField, label: "Measure names", numeric: false, type: "text", synthetic: true }] : []),
];
}
return compatible.length ? compatible : fields;
}

function canonicalTimeUnit(value) {
const raw = text(value || "").toLowerCase();
return ["year", "quarter", "month", "week", "day", "hour", "minute", "second"].includes(raw) ? raw : "none";
}

function canonicalAggregation(value) {
const raw = text(value || "").toLowerCase();
const aliases = { average: "avg", mean: "avg", minimum: "min", maximum: "max" };
const next = aliases[raw] || raw;
return ["sum", "avg", "min", "max", "count"].includes(next) ? next : "sum";
}

function aggregationLabel(value) {
const labels = { sum: "Sum", avg: "Avg", min: "Min", max: "Max", count: "Count" };
return labels[canonicalAggregation(value)] || "Sum";
}

function timeUnitLabel(value) {
const unit = canonicalTimeUnit(value);
return unit === "none" ? "None" : unit.replace(/^\w/, (char) => char.toUpperCase());
}

function timeUnitOptionsForDataset(dataset, fieldKey = chartConfig.xField) {
if (!fieldLooksDateLike(dataset, fieldKey)) return [];
const values = rawChartRows(dataset).map((row) => text(row && row[fieldKey])).filter(Boolean);
const hasClockTime = values.some((value) => /[T\s]\d{1,2}:\d{2}/.test(value));
const hasSeconds = values.some((value) => /[T\s]\d{1,2}:\d{2}:\d{2}/.test(value));
const options = ["None", "Year", "Quarter", "Month", "Week", "Day"];
if (hasClockTime) options.push("Hour", "Minute");
if (hasSeconds) options.push("Second");
return options;
}

function parseDateValue(value) {
if (value instanceof Date && Number.isFinite(value.getTime())) return value;
if (typeof value !== "string") return null;
const raw = text(value);
if (!raw) return null;
if (!/^\d{4}[-/]\d{1,2}(?:[-/]\d{1,2})?(?:[T\s]\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)?$/.test(raw)) return null;
const parsed = new Date(raw);
return Number.isFinite(parsed.getTime()) ? parsed : null;
}

function formatTimeValue(value, unit) {
unit = canonicalTimeUnit(unit);
if (unit === "none") return text(value);
const date = parseDateValue(value);
if (!date) return text(value);
const year = date.getUTCFullYear();
const month = date.getUTCMonth() + 1;
const pad = (next) => String(next).padStart(2, "0");
if (unit === "year") return String(year);
if (unit === "quarter") return `${year} Q${Math.floor((month - 1) / 3) + 1}`;
if (unit === "month") return `${year}-${pad(month)}`;
if (unit === "week") {
const first = Date.UTC(year, 0, 1);
const current = Date.UTC(year, date.getUTCMonth(), date.getUTCDate());
const week = Math.floor((current - first) / (7 * 24 * 60 * 60 * 1000)) + 1;
return `${year} W${pad(week)}`;
}
if (unit === "day") return `${year}-${pad(month)}-${pad(date.getUTCDate())}`;
if (unit === "hour") return `${year}-${pad(month)}-${pad(date.getUTCDate())} ${pad(date.getUTCHours())}:00`;
if (unit === "minute") return `${year}-${pad(month)}-${pad(date.getUTCDate())} ${pad(date.getUTCHours())}:${pad(date.getUTCMinutes())}`;
return `${year}-${pad(month)}-${pad(date.getUTCDate())} ${pad(date.getUTCHours())}:${pad(date.getUTCMinutes())}:${pad(date.getUTCSeconds())}`;
}

function resetChartConfig(dataset = activeDataset()) {
const fields = availableFields(dataset);
const rows = rawChartRows(dataset);
const xEncoding = specEncoding(dataset, "x");
const yEncoding = specEncoding(dataset, "y");
const sizeEncoding = specEncoding(dataset, "size");
const colorEncoding = specEncoding(dataset, "color");
const lineStyleEncoding = specEncoding(dataset, "lineStyle");
const labelEncoding = specEncoding(dataset, "label");
const firstDimension = fields.find((field) => !field.numeric)?.key || "x";
const firstMeasure = fields.find((field) => field.numeric)?.key || "y";
const hasResultTable = Boolean(resultTableFor(dataset));
const fallbackColor = hasResultTable ? "" : fields.find((field) => field.key === "series")?.key || "";
const nextXField = text(xEncoding.field || chartConfig.xField || firstDimension) || firstDimension;
const nextYField = text(yEncoding.field || chartConfig.yField || firstMeasure) || firstMeasure;
const requestedTimeUnit = xEncoding.time_unit;
const explicitColor = colorEncoding.field || (multiMeasureSeriesEnabled(dataset) ? measureNamesField : "");
const explicitLineStyle = lineStyleEncoding.field;
const explicitLabel = labelEncoding.field;
const explicitSize = sizeEncoding.field;
chartConfig = {
xField: nextXField,
yField: nextYField,
colorField: text(explicitColor || fallbackColor) || fallbackColor,
lineStyleField: text(explicitLineStyle || chartConfig.lineStyleField || "") || "",
labelField: text(explicitLabel || chartConfig.labelField || "") || "",
sizeField: text(explicitSize || chartConfig.sizeField || "") || "",
timeUnit: requestedTimeUnit != null ? canonicalTimeUnit(requestedTimeUnit) : canonicalTimeUnit(chartConfig.timeUnit || "none"),
yAggregation: canonicalAggregation(yEncoding.aggregate || chartConfig.yAggregation),
};
if (!hasField(dataset, chartConfig.xField)) chartConfig.xField = firstDimension;
if (!hasField(dataset, chartConfig.yField)) chartConfig.yField = firstMeasure;
if (!hasField(dataset, chartConfig.colorField)) chartConfig.colorField = fallbackColor;
if (!hasField(dataset, chartConfig.lineStyleField)) chartConfig.lineStyleField = "";
if (!hasField(dataset, chartConfig.labelField)) chartConfig.labelField = "";
if (!hasField(dataset, chartConfig.sizeField)) chartConfig.sizeField = "";
if (!fieldLooksDateLike(dataset, chartConfig.xField)) chartConfig.timeUnit = "none";
}

function normalizeChartConfigForType(dataset = activeDataset(), type = activeVisualizationType) {
if (!chartUsesSingleSeriesOnly(type)) return;
const compatibleStageFields = compatibleFieldsForRole(dataset, "x", type);
const compatibleValueFields = compatibleFieldsForRole(dataset, "y", type);
if (!compatibleStageFields.some((field) => field.key === chartConfig.xField)) {
chartConfig.xField = compatibleStageFields[0]?.key || chartConfig.xField;
}
if (!compatibleValueFields.some((field) => field.key === chartConfig.yField)) {
chartConfig.yField = compatibleValueFields[0]?.key || chartConfig.yField;
}
chartConfig.colorField = "";
chartConfig.timeUnit = "none";
}

function fieldLooksDateLike(dataset, fieldKey) {
if (!fieldKey) return false;
const field = availableFields(dataset).find((candidate) => candidate.key === fieldKey);
if (field && field.type === "date") return true;
if (field && field.numeric) return false;
return rawChartRows(dataset).some((row) => row[fieldKey] != null && parseDateValue(row[fieldKey]));
}

function measureNameFields(dataset) {
return availableFields(dataset).filter((field) => field.numeric && field.key !== chartConfig.xField);
}

function multiMeasureSeriesEnabled(dataset) {
return specSettings(dataset).multi_measure_series === true;
}

function measureCompatibilityKey(dataset, field) {
if (!field) return "";
const unit = columnUnit(dataset, field.key);
if (unit) return `unit:${unit.toLowerCase()}`;
return field.type === "percent" ? "type:percent" : "";
}

function compatibleMeasureNameFields(dataset) {
const measures = measureNameFields(dataset);
if (multiMeasureSeriesEnabled(dataset)) return measures;
const selectedMeasure = measures.find((field) => field.key === chartConfig.yField);
const compatibilityKey = measureCompatibilityKey(dataset, selectedMeasure);
if (!compatibilityKey) return [];
return measures.filter((field) => measureCompatibilityKey(dataset, field) === compatibilityKey);
}

function usesMeasureNames() {
return chartConfig.colorField === measureNamesField;
}

function appendAggregatedValue(groups, x, series, y, row, lineStyle = null) {
const key = `${x}\u0000${series}`;
if (y == null) return;
if (!groups.has(key)) {
groups.set(key, { x, series, lineStyle, values: [], raw: row });
}
if (lineStyle && !groups.get(key).lineStyle) groups.get(key).lineStyle = lineStyle;
groups.get(key).values.push(y);
}

function aggregateRows(rows, dataset = activeDataset()) {
const groups = new Map();
for (const row of rows) {
const x = formatTimeValue(row[chartConfig.xField], chartConfig.timeUnit);
if (usesMeasureNames()) {
for (const field of compatibleMeasureNameFields(dataset)) {
appendAggregatedValue(groups, x, field.label, number(row[field.key]), row);
}
continue;
}
const series = chartConfig.colorField ? text(row[chartConfig.colorField] || "Value") : "Value";
const y = chartConfig.yAggregation === "count" ? 1 : number(row[chartConfig.yField]);
const lineStyle = chartConfig.lineStyleField ? text(row[chartConfig.lineStyleField] || "") : "";
appendAggregatedValue(groups, x, series, y, row, lineStyle || null);
}
const output = [...groups.values()].map((group) => {
let y = 0;
if (chartConfig.yAggregation === "avg") y = group.values.reduce((sum, value) => sum + value, 0) / group.values.length;
else if (chartConfig.yAggregation === "min") y = Math.min(...group.values);
else if (chartConfig.yAggregation === "max") y = Math.max(...group.values);
else y = group.values.reduce((sum, value) => sum + value, 0);
return { x: group.x, y, series: group.series, ...(group.lineStyle ? { lineStyle: group.lineStyle } : {}), raw: group.raw };
});
return output;
}

function rawProjectedRows(rows, dataset = activeDataset()) {
const output = [];
for (const row of rows) {
if (usesMeasureNames()) {
for (const field of compatibleMeasureNameFields(dataset)) {
const y = number(row[field.key]);
if (y == null) continue;
output.push({
x: row[chartConfig.xField],
y,
size: chartConfig.sizeField ? number(row[chartConfig.sizeField]) : null,
series: field.label,
...(chartConfig.labelField ? { label: text(row[chartConfig.labelField] || "") } : {}),
raw: row,
});
}
continue;
}
const y = number(row[chartConfig.yField]);
if (y == null) continue;
output.push({
x: row[chartConfig.xField],
y,
size: chartConfig.sizeField ? number(row[chartConfig.sizeField]) : null,
series: chartConfig.colorField ? text(row[chartConfig.colorField] || "Value") : "Value",
...(chartConfig.lineStyleField ? { lineStyle: text(row[chartConfig.lineStyleField] || "") } : {}),
...(chartConfig.labelField ? { label: text(row[chartConfig.labelField] || "") } : {}),
raw: row,
});
}
return output;
}

function projectedDataset(dataset) {
const type = widgetVisualizationType(activeVisualizationType);
const rows = projectedDataForType(dataset, type);
const renderRows = projectedRenderRows(rows);
return {
...dataset,
chart_spec: projectedChartSpec(dataset, type, rows),
data: renderRows,
table: {
columns: projectedRenderColumns(rows, dataset),
rows: renderRows,
row_count: renderRows.length,
truncated: false,
},
};
}

function projectedDataForType(dataset, type = activeVisualizationType) {
type = widgetVisualizationType(type);
const rows = chartRows(dataset);
return type === "scatter" || type === "histogram" || type === "boxPlot" ? rawProjectedRows(rows, dataset) : aggregateRows(rows, dataset);
}

function hasNonNegativeProjectedValues(data) {
let observed = false;
for (const point of data) {
const value = number(point && point.y);
if (value == null) continue;
observed = true;
if (value < 0) return false;
}
return observed;
}

function projectedSeriesCount(data) {
return groupData(data).size;
}

function projectedXCount(data) {
return uniqueX(data).length;
}

function numericValuesForField(dataset, fieldKey) {
if (!fieldKey) return [];
return rawChartRows(dataset)
.map((row) => number(row && row[fieldKey]))
.filter((value) => value != null);
}

function hasDistributionSample(dataset, fieldKey, minimumValues = 10) {
const values = numericValuesForField(dataset, fieldKey);
return values.length >= minimumValues && new Set(values.map((value) => String(value))).size >= 3;
}

function maxNumericValuesPerCategory(dataset, categoryField, valueField) {
if (!categoryField || !valueField) return 0;
const counts = new Map();
for (const row of rawChartRows(dataset)) {
if (number(row && row[valueField]) == null) continue;
const category = text(row && row[categoryField]);
counts.set(category, (counts.get(category) || 0) + 1);
}
return Math.max(0, ...counts.values());
}

function compatibleChartPickerSections(dataset = activeDataset()) {
return chartPickerSections
.map((section) => ({
...section,
options: section.options
.filter((option, index, options) => {
const canonicalType = widgetVisualizationType(option.type);
return options.findIndex((candidate) => widgetVisualizationType(candidate.type) === canonicalType) === index;
})
.map((option) => ({ ...option, type: widgetVisualizationType(option.type) })),
}))
.filter((section) => section.options.length);
}

function ensureActiveChartTypeIsSupported(dataset = activeDataset()) {
activeVisualizationType = widgetVisualizationType(activeVisualizationType || "bar");
normalizeChartConfigForType(dataset, activeVisualizationType);
}

function renderFieldList(dataset) {
const root = document.getElementById("field-list");
if (!root) return;
root.innerHTML = "";
const rows = rawChartRows(dataset);
const keys = chartColumns(rows, dataset);
const measures = keys.filter((key) => isNumericColumn(rows, key, dataset));
const dimensions = keys.filter((key) => !measures.includes(key));
const activeKeys = new Set([chartConfig.xField, chartConfig.yField, chartConfig.colorField, chartConfig.lineStyleField, chartConfig.labelField, chartConfig.sizeField]);
const filter = text(document.querySelector(".field-filter")?.value).trim().toLowerCase();

function appendGroup(title, fields) {
fields = fields.filter((key) => !filter || columnLabel(key, dataset).toLowerCase().includes(filter) || key.toLowerCase().includes(filter));
if (!fields.length) return;
const group = document.createElement("div");
group.className = "field-group";
const heading = document.createElement("p");
heading.className = "field-group-title";
heading.textContent = title;
const list = document.createElement("ul");
list.className = "field-list";
for (const key of fields) {
const item = document.createElement("li");
item.className = `field-item${activeKeys.has(key) ? " is-active" : ""}`;
const icon = document.createElement("span");
icon.className = "field-icon";
icon.appendChild(lucideIcon(measures.includes(key) ? "hash" : "type", { width: "14", height: "14" }));
const label = document.createElement("span");
label.className = "field-label";
label.textContent = columnLabel(key, dataset);
item.append(icon, label);
list.appendChild(item);
}
group.append(heading, list);
root.appendChild(group);
}

appendGroup("Measures", measures);
appendGroup("Columns", dimensions);
}

function setupAppChromeControls() {
const fieldFilter = document.querySelector(".field-filter");
if (!fieldFilter) return;
fieldFilter.addEventListener("input", () => renderFieldList(activeDataset()));
}

function renderDataPreview(dataset) {
const root = document.getElementById("data-preview");
if (!root) return;
destroyDataTable(root);
root.innerHTML = "";
const rows = chartRows(dataset);
renderDataTable(root, {
columns: tableColumns(dataset, rows),
emptyLabel: "No rows match the selected filters.",
maxRows: 80,
pageSize: isDetailDisplayMode() ? 12 : 8,
rows,
});
}

function appendSourceRow(root, label, value, options = {}) {
if (value == null || value === "") return;
if (options.code) {
const details = document.createElement("details");
details.className = "source-disclosure";
const summary = document.createElement("summary");
summary.textContent = label;
const code = document.createElement("pre");
code.className = "source-code";
code.dataset.language = options.language || label;
renderSourceCode(code, value, code.dataset.language);
details.append(summary, code);
root.appendChild(details);
return;
}
const row = document.createElement("div");
row.className = "source-row";
const labelEl = document.createElement("span");
labelEl.textContent = label;
const valueEl = document.createElement("strong");
if (options.multiline) {
valueEl.className = "source-row-list";
for (const item of sourceDetailList(value)) {
const line = document.createElement("span");
line.textContent = text(item);
valueEl.appendChild(line);
}
}
else {
valueEl.textContent = text(value);
}
row.append(labelEl, valueEl);
root.appendChild(row);
}

function appendSourcePreviewRows(root, dataset) {
const table = resultTableFor(dataset) || {};
const rows = asArray(table.rows).filter((row) => row && typeof row === "object").slice(0, 10);
if (!rows.length) {
appendSourceRow(root, "Preview rows", "No preview rows available");
return;
}
const columns = [];
const seen = new Set();
for (const column of asArray(table.columns)) {
const key = column && (column.key || column.field);
if (key && !seen.has(key)) {
seen.add(key);
columns.push(key);
}
}
for (const row of rows) {
for (const key of Object.keys(row)) {
if (!seen.has(key)) {
seen.add(key);
columns.push(key);
}
}
}
const wrapper = document.createElement("div");
wrapper.className = "source-row source-row-table";
const labelEl = document.createElement("span");
labelEl.textContent = "Preview rows";
const tableShell = document.createElement("div");
tableShell.className = "source-preview-shell";
const previewTable = document.createElement("table");
previewTable.className = "source-preview-table";
const thead = document.createElement("thead");
const headRow = document.createElement("tr");
for (const column of columns) {
const th = document.createElement("th");
th.textContent = column;
headRow.appendChild(th);
}
thead.appendChild(headRow);
const tbody = document.createElement("tbody");
for (const row of rows) {
const tr = document.createElement("tr");
for (const column of columns) {
const td = document.createElement("td");
td.textContent = text(row[column]);
tr.appendChild(td);
}
tbody.appendChild(tr);
}
previewTable.append(thead, tbody);
tableShell.appendChild(previewTable);
wrapper.append(labelEl, tableShell);
root.appendChild(wrapper);
}

function renderSourceDetails(dataset) {
const root = document.getElementById("source-details");
if (!root) return;
root.innerHTML = "";
const sourceQuery = sourceQueryFor(dataset) || {};
const metadataObjects = sourceMetadataObjects(dataset);
const queryCode = sqlTextFor(dataset);
const queryLanguage = queryLanguageFor(dataset);
const explicitTables = sourceTableNamesFromMetadata(metadataObjects);
const inferredTables = extractTablesFromSql(queryCode);
const tables = explicitTables.length ? explicitTables : inferredTables;
const explicitFilters = firstListFromObjects(metadataObjects, [
"filters",
"filter_descriptions",
"filterDescriptions",
"filter_description",
"filterDescription",
]);
const activeFilters = activeDataFilterSummary(dataset);
const filters = explicitFilters.length ? explicitFilters : activeFilters === "None" ? ["None declared"] : [activeFilters];
const metrics = metricDefinitionList(dataset);
appendSourceRow(root, "Dataset", valueFor(dataset, "dataset", payload.dataset) || sourceLabelFor(dataset) || "Not declared");
if (sourceQuery.description) appendSourceRow(root, "Description", sourceQuery.description);
appendSourceRow(root, "Tables used", sourceDetailList(tables.length ? tables : ["Not declared"]), { multiline: true });
appendSourceRow(root, "Filters", sourceDetailText(filters));
appendSourceRow(root, "Metric definitions", sourceDetailList(metrics.length ? metrics : ["Displayed directly from source columns"]), { multiline: true });
appendSourceRow(root, "Snapshot", sourceQuery.executed_at || valueFor(dataset, "executed_at", payload.executed_at) || "Not declared");
if (queryCode) appendSourceRow(root, "Source query", queryCode, { code: true, language: queryLanguage });
appendSourcePreviewRows(root, dataset);
if (!root.childElementCount) {
const empty = document.createElement("p");
empty.className = "source-note";
empty.textContent = "Static reviewed data.";
root.appendChild(empty);
}
}

function renderSqlPreview(dataset) {
const root = document.getElementById("sql-preview");
if (!root) return;
root.innerHTML = "";
const bottomSplit = document.getElementById("bottom-split");
const sql = sqlTextFor(dataset);
if (bottomSplit) bottomSplit.classList.toggle("has-sql", Boolean(sql));
if (!sql) {
const empty = document.createElement("div");
empty.className = "empty";
empty.setAttribute("role", "status");
const heading = document.createElement("strong");
heading.textContent = "No query available";
const detail = document.createElement("span");
detail.textContent = "This chart payload did not include SQL or Python source code.";
empty.append(heading, detail);
root.appendChild(empty);
return;
}

const code = document.createElement("pre");
code.className = "source-code";
code.dataset.language = queryLanguageFor(dataset);
renderSourceCode(code, sql, code.dataset.language);
root.appendChild(code);
}

function renderAppChrome(dataset) {
renderSourceDetails(dataset);
renderFieldList(dataset);
renderDataPreview(dataset);
renderSqlPreview(dataset);
}

function groupData(data) {
const groups = new Map();
for (const point of data) {
const y = number(point && point.y);
if (y == null) continue;
const series = text(point.series || "Value");
if (!groups.has(series)) groups.set(series, []);
groups.get(series).push({ x: text(point.x), y, label: point.label, raw: point });
}
return groups;
}

function rechartsLegendNamesForDataset(dataset, type) {
if (type === "histogram" || type === "heatmap" || type === "boxPlot") return [];
const chartSpec = chartSpecFor(dataset);
const encodings = chartSpec && typeof chartSpec.encodings === "object" && !Array.isArray(chartSpec.encodings)
? chartSpec.encodings
: {};
const yFields = asArray(encodings.y && encodings.y.fields).map(text).filter(Boolean);
if (yFields.length) return yFields;
const colorField = text(encodings.color && encodings.color.field);
if (colorField) {
return uniqueProjectedSeriesValues(chartRows(dataset)).map((value, index) => syntheticSeriesField(value, index));
}
const yField = text(encodings.y && encodings.y.field);
return yField ? [yField] : [];
}

function uniqueX(data) {
const seen = new Set();
const values = [];
for (const point of data) {
const x = text(point && point.x);
if (seen.has(x)) continue;
seen.add(x);
values.push(x);
}
return values;
}

function svgEl(name, attrs = {}) {
const element = document.createElementNS("http://www.w3.org/2000/svg", name);
for (const [key, value] of Object.entries(attrs)) {
if (value != null) element.setAttribute(key, String(value));
}
return element;
}

function lucideIcon(name, attrs = {}) {
const svg = svgEl("svg", {
viewBox: "0 0 24 24",
fill: "none",
"aria-hidden": "true",
focusable: "false",
...attrs,
});
svg.setAttribute("stroke", "currentColor");
svg.setAttribute("stroke-width", "2");
svg.setAttribute("stroke-linecap", "round");
svg.setAttribute("stroke-linejoin", "round");
const icons = {
check: [["path", { d: "M20 6 9 17l-5-5" }]],
chevronDown: [["path", { d: "m6 9 6 6 6-6" }]],
chevronRight: [["path", { d: "m9 18 6-6-6-6" }]],
fileDown: [
["path", { d: "M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z" }],
["path", { d: "M14 2v4a2 2 0 0 0 2 2h4" }],
["path", { d: "M12 18v-6" }],
["path", { d: "m9 15 3 3 3-3" }],
],
fileText: [
["path", { d: "M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z" }],
["path", { d: "M14 2v4a2 2 0 0 0 2 2h4" }],
["path", { d: "M10 9H8" }],
["path", { d: "M16 13H8" }],
["path", { d: "M16 17H8" }],
],
printer: [
["path", { d: "M6 9V2h12v7" }],
["path", { d: "M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2" }],
["path", { d: "M6 14h12v8H6z" }],
],
hash: [
["line", { x1: "4", x2: "20", y1: "9", y2: "9" }],
["line", { x1: "4", x2: "20", y1: "15", y2: "15" }],
["line", { x1: "10", x2: "8", y1: "3", y2: "21" }],
["line", { x1: "16", x2: "14", y1: "3", y2: "21" }],
],
calendar: [
["path", { d: "M8 2v4" }],
["path", { d: "M16 2v4" }],
["rect", { x: "3", y: "4", width: "18", height: "18", rx: "2" }],
["path", { d: "M3 10h18" }],
],
maximize2: [
["polyline", { points: "15 3 21 3 21 9" }],
["polyline", { points: "9 21 3 21 3 15" }],
["line", { x1: "21", x2: "14", y1: "3", y2: "10" }],
["line", { x1: "3", x2: "10", y1: "21", y2: "14" }],
],
minimize2: [
["polyline", { points: "4 14 10 14 10 20" }],
["polyline", { points: "20 10 14 10 14 4" }],
["line", { x1: "14", x2: "21", y1: "10", y2: "3" }],
["line", { x1: "3", x2: "10", y1: "21", y2: "14" }],
],
presentation: [
["path", { d: "M2 3h20" }],
["path", { d: "M21 3v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V3" }],
["path", { d: "m7 21 5-5 5 5" }],
],
refreshCw: [
["path", { d: "M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8" }],
["path", { d: "M21 3v5h-5" }],
["path", { d: "M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16" }],
["path", { d: "M8 16H3v5" }],
],
type: [
["polyline", { points: "4 7 4 4 20 4 20 7" }],
["line", { x1: "9", x2: "15", y1: "20", y2: "20" }],
["line", { x1: "12", x2: "12", y1: "4", y2: "20" }],
],
};
for (const [tag, attrs] of icons[name] || icons.chevronDown) {
svg.appendChild(svgEl(tag, attrs));
}
return svg;
}

function renderEmpty(message, title = "Chart cannot be rendered") {
destroyChartInstance();
const chartRoot = document.getElementById("chart");
const empty = document.createElement("div");
empty.className = "empty";
empty.setAttribute("role", "status");
const heading = document.createElement("strong");
heading.textContent = title;
const detail = document.createElement("span");
detail.textContent = message;
empty.append(heading, detail);
chartRoot.appendChild(empty);
}

function destroyChartInstance() {
destroyRechartsChart(document.getElementById("chart"));
destroyDataTable(document.getElementById("chart"));
chartInstance = null;
}

function hideExternalLegend() {
const root = document.getElementById("legend");
const legendShell = document.getElementById("legend-shell");
if (root) root.innerHTML = "";
if (legendShell) {
legendShell.hidden = true;
legendShell.classList.add("is-empty");
legendShell.setAttribute("aria-hidden", "true");
}
}

function chartPalette() {
return resolveCssColors(colors).filter(Boolean);
}

function chartBorderPalette() {
return resolveCssColors(colorEdges).filter(Boolean);
}

function resizeChartInstance() {
// Recharts responds to the container resize; the layout code only needs
// to reserve the region, not recreate the chart.
}

function renderChart() {
const dataset = projectedDataset(activeDataset());
const chartRoot = document.getElementById("chart");
destroyChartInstance();
chartRoot.innerHTML = "";
activeVisualizationType = widgetVisualizationType(activeVisualizationType || "bar");
applyChartSettingsAttributes();
const type = rendererVisualizationType(activeVisualizationType);
const legendNames = rechartsLegendNamesForDataset(dataset, type);
reconcileVisibleSeries(legendNames);
try {
renderRechartsChart(chartRoot, dataset, type, {
colors: chartPalette(),
borderColors: chartBorderPalette(),
height: isDetailDisplayMode() ? "100%" : undefined,
onVisibleSeriesChange(nextVisibleSeries) {
visibleSeries = orderedVisibleSeries(legendNames, nextVisibleSeries);
renderChart();
},
visibleSeries,
timeUnit: chartConfig.timeUnit,
unit: unitFor(dataset),
baseline: number(specValue(dataset, "baseline", payload.baseline)),
settings: {
orientation: chartSettings.barOrientation,
group_mode: chartSettings.barGroupMode,
},
surface: isDetailDisplayMode() ? "explorer" : "compact",
title: text(valueFor(dataset, "title", payload.title || "Data Analytics chart")),
});
hideExternalLegend();
} catch (error) {
chartRoot.innerHTML = "";
renderEmpty(error && error.message ? `Choose compatible fields or reset the chart configuration. ${error.message}` : "Choose compatible fields or reset the chart configuration.");
hideExternalLegend();
}
}

function renderTableFallback(dataset) {
destroyChartInstance();
const chartRoot = document.getElementById("chart");
const controls = document.getElementById("controls");
const legendShell = document.getElementById("legend-shell");
const dataPreview = document.getElementById("data-preview");
controls.hidden = true;
if (legendShell) legendShell.hidden = true;
if (dataPreview) {
destroyDataTable(dataPreview);
dataPreview.innerHTML = "";
}
destroyDataTable(chartRoot);
chartRoot.innerHTML = "";

const resultTable = resultTableFor(dataset);
const rows = resultTable ? chartRows(dataset) : [];
if (!rows.length) {
renderEmpty("No table rows to render.", "No table data");
return;
}

const maxRows = Math.max(1, Number(valueFor(dataset, "max_rows", payload.max_rows)) || 50);
const columns = tableColumns(dataset, rows);
renderDataTable(chartRoot, {
columns,
emptyLabel: "No table rows to render.",
maxRows,
pageSize: isDetailDisplayMode() ? 12 : 8,
rows,
});
}

function renderLegend(groupNames) {
const root = document.getElementById("legend");
const legendShell = document.getElementById("legend-shell");
root.innerHTML = "";
if (legendShell) {
const empty = groupNames.length <= 1;
legendShell.hidden = empty && !isDetailDisplayMode();
legendShell.classList.toggle("is-empty", empty);
legendShell.setAttribute("aria-hidden", String(empty));
}
if (!groupNames.length || groupNames.length <= 1) return;
groupNames.forEach((name, index) => {
const item = document.createElement("li");
item.className = "legend-item";
item.style.color = colors[index % colors.length];
const button = document.createElement("button");
button.type = "button";
button.className = "legend-button";
button.setAttribute("aria-pressed", String(visibleSeries.has(name)));
button.addEventListener("click", () => {
if (visibleSeries.has(name)) {
if (visibleSeries.size === 1) return;
visibleSeries.delete(name);
}
else visibleSeries.add(name);
visibleSeries = orderedVisibleSeries(groupNames, visibleSeries);
renderChart();
});
const swatch = document.createElement("span");
swatch.className = "swatch";
const label = document.createElement("span");
label.textContent = name;
button.append(swatch, label);
item.appendChild(button);
root.appendChild(item);
});
}

function chartTypeLabel(type) {
for (const section of chartPickerSections) {
for (const option of section.options) {
if (option.type === type) return option.label;
}
}
return text(type).replaceAll("_", " ");
}

function activeDataFilterSummary(dataset = activeDataset()) {
const active = dataFilterSpecs(dataset)
.map((spec) => {
const value = selectedDataFilterValue(dataset, spec.key);
return value === "all" ? null : `${spec.label}: ${value}`;
})
.filter(Boolean);
return active.length ? active.join(", ") : "None";
}

function promptSourceLines(dataset = activeDataset()) {
const sourceQuery = sourceQueryFor(dataset) || {};
const resultTable = resultTableFor(dataset) || {};
const lines = [];
if (sourceQuery.label || sourceQuery.id) lines.push(`Source query: ${sourceQuery.label || sourceQuery.id}`);
if (sourceQuery.engine) lines.push(`Source: ${sourceQuery.engine}`);
if (sourceQuery.executed_at) lines.push(`Executed at: ${sourceQuery.executed_at}`);
if (sourceQuery.description) lines.push(`Description: ${sourceQuery.description}`);
if (Number.isFinite(Number(resultTable.row_count))) {
lines.push(`Rows: ${formatNumber(Number(resultTable.row_count), 0)}${resultTable.truncated ? " sampled" : ""}`);
}
if (sourceQuery.sql) lines.push(`Query:\n${sourceQuery.sql}`);
return lines.length ? lines.join("\n") : "Source query: not declared in the widget payload.";
}

function promptContext(dataset = activeDataset()) {
const title = text(valueFor(dataset, "title", payload.title || "Data Analytics chart"));
return [
`Widget URL: ${window.location.href}`,
`Chart title: ${title}`,
`Chart type: ${chartTypeLabel(activeVisualizationType)}`,
`X field: ${fieldLabel(dataset, chartConfig.xField, chartConfig.xField)}`,
`Y field: ${fieldLabel(dataset, chartConfig.yField, chartConfig.yField)}`,
`Grouping field: ${chartConfig.colorField ? fieldLabel(dataset, chartConfig.colorField, chartConfig.colorField) : "None"}`,
`Filters: ${activeDataFilterSummary(dataset)}`,
promptSourceLines(dataset),
].join("\n");
}

function refreshPrompt(dataset = activeDataset()) {
return `Refresh this inline chart using the same declared query and the latest available time frame.

Re-run the existing source, update the widget data, preserve the current chart structure unless the latest data makes it invalid, and verify the refreshed chart in the inline and detail views.

${promptContext(dataset)}`;
}

function exportPrompt(target, dataset = activeDataset()) {
const context = promptContext(dataset);
if (target === "html") {
return `Export this inline chart detail view through the canonical portable artifact path. Wrap the current chart configuration, reviewed dataset, active filters, query/source details, caveats, and table preview in a one-chart report artifact.json using the exact top-level fields surface, manifest, snapshot, sources, and package_info. Then run node <PLUGIN_ROOT>/skills/build-report/scripts/deliver_portable_artifact.mjs --input artifact.json --output report.html. Do not hand-author a second HTML shell or chart runtime. Omit the interactive top bar and app-only controls from the exported artifact. Verify the enhanced reader and semantic fallback before delivery.

${context}`;
}
if (target === "document") {
return `Create a polished document artifact from this inline chart. Preserve the chart, table preview, active filters, query/source details, and caveats, then verify the document.

${context}`;
}
if (target === "slides") {
return `Create an executive-ready slide artifact from this inline chart. Preserve the core takeaway, chart, active filters, table preview, and source details, then verify the deck.

${context}`;
}
return `Use the existing data-analytics:report-to-pdf workflow to create a PDF artifact from this inline chart detail view. Use the static HTML/export path when available, preserve the chart title, chart, table preview, active filters, caveats, and source details, omit the interactive top bar, share menus, edit controls, and app-only controls, then verify the PDF before delivery.

${context}`;
}

function codexPromptUrl(prompt) {
const url = new URL("codex://new");
url.searchParams.set("prompt", prompt);
url.searchParams.set("originUrl", window.location.href);
return url.toString();
}

function sendCodexPromptToHost(prompt) {
const hostApi = window.openai || {};
const payload = {
originUrl: window.location.href,
prompt,
};
const launchers = [hostApi.sendFollowUpMessage, hostApi.openCodexPrompt];
for (const launch of launchers) {
if (typeof launch !== "function") continue;
try {
Promise.resolve(launch.call(hostApi, payload)).catch(() => {});
return true;
} catch (error) {
// Try the next host launcher if one exists.
}
}
return false;
}

async function copyTextToClipboard(value) {
if (!navigator.clipboard || typeof navigator.clipboard.writeText !== "function") return false;
await navigator.clipboard.writeText(value);
return true;
}

function isLocalPreviewHost() {
return ["localhost", "127.0.0.1", "::1"].includes(window.location.hostname);
}

function launchCodexDeepLink(url) {
if (isLocalPreviewHost()) return false;
let linkClicked = false;
try {
const link = document.createElement("a");
link.href = url;
link.target = "_top";
link.rel = "noopener noreferrer";
link.style.display = "none";
document.body.appendChild(link);
link.click();
link.remove();
linkClicked = true;
} catch (error) {
// Continue to the top-level location path below when available.
}
try {
if (window.top === window) {
window.location.assign(url);
return true;
}
} catch (fallbackError) {
// Ignore navigation failures; the copied prompt is the fallback.
}
return linkClicked;
}

function openCodexPrompt(prompt) {
const url = codexPromptUrl(prompt);
void copyTextToClipboard(prompt).catch(() => {});
const sentToHost = sendCodexPromptToHost(prompt);
if (!sentToHost) launchCodexDeepLink(url);
}

function removeMenuSurface(menu, { immediate = false } = {}) {
if (!menu) return;
if (immediate) {
menu.remove();
return;
}
menu.classList.remove("opening");
menu.classList.add("closing");
window.setTimeout(() => menu.remove(), 100);
}

function closeShareMenu(options = {}) {
const menu = document.getElementById("detail-share-menu-list");
const button = document.getElementById("detail-share-button");
removeMenuSurface(menu, options);
if (button) button.setAttribute("aria-expanded", "false");
shareMenuOpen = false;
}

function shareMenuItem(label, iconName, onClick) {
const button = document.createElement("button");
button.type = "button";
button.className = "export-menu-item";
button.setAttribute("role", "menuitem");
button.append(lucideIcon(iconName, { width: "16", height: "16" }), document.createTextNode(label));
button.addEventListener("click", (event) => {
event.stopPropagation();
closeShareMenu();
onClick();
});
return button;
}

function openShareMenu() {
const root = document.getElementById("detail-share-menu");
const button = document.getElementById("detail-share-button");
if (!root || !button) return;
closeFieldMenus();
closeChartPicker();
closeDataFilterMenus();
closeShareMenu({ immediate: true });
shareMenuOpen = true;
button.setAttribute("aria-expanded", "true");
const menu = document.createElement("div");
menu.id = "detail-share-menu-list";
menu.className = "export-menu-list menu-surface opening";
menu.setAttribute("role", "menu");
menu.append(
shareMenuItem("Create HTML file", "fileText", () => openCodexPrompt(exportPrompt("html"))),
shareMenuItem("Create PDF", "fileDown", () => openCodexPrompt(exportPrompt("pdf"))),
shareMenuItem("Create Google Doc", "fileText", () => openCodexPrompt(exportPrompt("document"))),
shareMenuItem("Create Google Slides", "presentation", () => openCodexPrompt(exportPrompt("slides"))),
);
menu.addEventListener("click", (event) => event.stopPropagation());
root.appendChild(menu);
}

function setupDetailRefreshButton() {
const button = document.getElementById("detail-refresh-button");
if (!button) return;
button.addEventListener("click", (event) => {
event.stopPropagation();
closeShareMenu();
openCodexPrompt(refreshPrompt());
});
}

function setupDetailShareMenu() {
const button = document.getElementById("detail-share-button");
if (!button) return;
const label = document.createElement("span");
label.textContent = "Export";
button.replaceChildren(label, caretIcon());
button.addEventListener("click", (event) => {
event.stopPropagation();
if (shareMenuOpen) closeShareMenu();
else openShareMenu();
});
}

function chartPreviewSvg(kind) {
const stroke = "currentColor";
const fill = "color-mix(in srgb, currentColor 28%, transparent)";
const fillStrong = "color-mix(in srgb, currentColor 48%, transparent)";
const grid = `<path d="M8 8v48h80" fill="none" stroke="${stroke}" stroke-width="3" stroke-linecap="round" opacity=".44"/>`;
const frame = (body) => `<svg viewBox="0 0 96 64" aria-hidden="true" fill="none">${grid}${body}</svg>`;
const rect = (attrs) => `<rect ${attrs} rx="2" fill="${fill}" stroke="${stroke}" stroke-width="2.5"/>`;
const segment = (attrs, strong = false) => `<rect ${attrs} rx="1.5" fill="${strong ? fillStrong : fill}" stroke="${stroke}" stroke-width="2.2"/>`;
if (kind === "bar") {
return frame(
`${rect('x="18" y="34" width="7" height="22"')}${rect('x="28" y="24" width="7" height="32"')}` +
`${rect('x="47" y="42" width="7" height="14"')}${rect('x="57" y="18" width="7" height="38"')}` +
`${rect('x="76" y="29" width="7" height="27"')}`,
);
}
if (kind === "stacked-bar" || kind === "stacked-bar-100") {
return frame(
`${segment('x="20" y="38" width="12" height="18"')}${segment('x="20" y="24" width="12" height="14"', true)}` +
`${segment('x="45" y="32" width="12" height="24"')}${segment('x="45" y="15" width="12" height="17"', true)}` +
`${segment('x="70" y="43" width="12" height="13"')}${segment('x="70" y="28" width="12" height="15"', true)}`,
);
}
if (kind === "horizontal-bar") {
return frame(
`${rect('x="18" y="16" width="22" height="6"')}${rect('x="18" y="25" width="36" height="6"')}` +
`${rect('x="18" y="40" width="28" height="6"')}${rect('x="18" y="49" width="53" height="6"')}`,
);
}
if (kind === "horizontal-stacked-bar" || kind === "horizontal-stacked-bar-100") {
return frame(
`${segment('x="18" y="18" width="30" height="9"')}${segment('x="48" y="18" width="22" height="9"', true)}` +
`${segment('x="18" y="39" width="22" height="9"')}${segment('x="40" y="39" width="38" height="9"', true)}`,
);
}
if (kind === "line" || kind === "sparkline") {
return frame(
`<path d="M18 45 34 29l14 9 17-21 17 15" stroke="${stroke}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>` +
`<circle cx="18" cy="45" r="3" fill="${fillStrong}" stroke="${stroke}" stroke-width="2"/><circle cx="34" cy="29" r="3" fill="${fillStrong}" stroke="${stroke}" stroke-width="2"/><circle cx="65" cy="17" r="3" fill="${fillStrong}" stroke="${stroke}" stroke-width="2"/><circle cx="82" cy="32" r="3" fill="${fillStrong}" stroke="${stroke}" stroke-width="2"/>`,
);
}
if (kind === "area" || kind === "stacked-area") {
return frame(
`<path d="M18 47 34 35l14 8 18-23 17 10v26H18Z" fill="${fill}"/>` +
`<path d="M18 47 34 35l14 8 18-23 17 10" stroke="${stroke}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>`,
);
}
if (kind === "histogram") {
return frame(
[16, 27, 38, 49, 60, 71].map((x, i) => {
const heights = [12, 22, 35, 29, 18, 9];
return segment(`x="${x}" y="${56 - heights[i]}" width="9" height="${heights[i]}"`, i === 2 || i === 3);
}).join(""),
);
}
if (kind === "scatter") {
return frame(
[[20, 45], [31, 34], [42, 40], [51, 25], [63, 31], [74, 18], [82, 28]]
.map(([cx, cy]) => `<circle cx="${cx}" cy="${cy}" r="4" fill="${fillStrong}" stroke="${stroke}" stroke-width="2.5"/>`)
.join(""),
);
}
if (kind === "heatmap") {
return frame(
[0, 1, 2].map((row) =>
[0, 1, 2, 3].map((col) => {
const strong = (row + col) % 3 === 0;
const opacity = [".18", ".3", ".46", ".62"][(row * 2 + col) % 4];
return `<rect x="${18 + col * 16}" y="${16 + row * 12}" width="13" height="10" rx="1.5" fill="${strong ? fillStrong : fill}" opacity="${opacity}" stroke="${stroke}" stroke-width="1.8"/>`;
}).join("")
).join(""),
);
}
if (kind === "pie") {
return `<svg viewBox="0 0 96 64" aria-hidden="true" fill="none"><path d="M48 8a24 24 0 1 1-20.8 36" fill="${fill}" stroke="${stroke}" stroke-width="3" stroke-linejoin="round"/><path d="M48 8v24l20.8 12A24 24 0 0 0 48 8Z" fill="${fillStrong}" stroke="${stroke}" stroke-width="3" stroke-linejoin="round"/><path d="M48 32 27.2 44" stroke="${stroke}" stroke-width="3" stroke-linecap="round"/></svg>`;
}
if (kind === "funnel") {
return `<svg viewBox="0 0 96 64" aria-hidden="true" fill="none"><path d="M18 10h60L68 24H28Z" fill="${fillStrong}" stroke="${stroke}" stroke-width="3"/><path d="M30 28h36L58 42H38Z" fill="${fill}" stroke="${stroke}" stroke-width="3"/><path d="M40 46h16l-4 10h-8Z" fill="${fill}" stroke="${stroke}" stroke-width="3"/></svg>`;
}
if (kind === "waterfall") {
return frame(
`${segment('x="18" y="40" width="12" height="16"')}${segment('x="38" y="26" width="12" height="30"', true)}${segment('x="58" y="34" width="12" height="22"')}${segment('x="78" y="20" width="8" height="36"', true)}`,
);
}
if (kind === "leaderboard") {
return frame(
`${segment('x="18" y="17" width="58" height="8"', true)}${segment('x="18" y="31" width="44" height="8"')}${segment('x="18" y="45" width="30" height="8"')}`,
);
}
if (kind === "box-plot") {
return frame(
`<path d="M22 24h52M22 42h42" stroke="${stroke}" stroke-width="3" stroke-linecap="round"/><rect x="34" y="18" width="24" height="12" rx="2" fill="${fill}" stroke="${stroke}" stroke-width="2.5"/><rect x="30" y="36" width="22" height="12" rx="2" fill="${fillStrong}" stroke="${stroke}" stroke-width="2.5"/>`,
);
}
return frame(rect('x="20" y="22" width="52" height="28"'));
}

function caretIcon(extraClass = "") {
const caret = document.createElement("span");
caret.className = `dropdown-caret${extraClass ? ` ${extraClass}` : ""}`;
caret.setAttribute("aria-hidden", "true");
caret.appendChild(lucideIcon("chevronDown"));
return caret;
}

function closeChartPicker() {
const popover = document.getElementById("chart-picker-popover");
const button = document.getElementById("chart-picker-button");
if (popover) {
popover.hidden = true;
popover.classList.remove("opening");
}
if (button) button.setAttribute("aria-expanded", "false");
}

function renderChartPicker(root) {
const picker = document.createElement("div");
picker.className = "chart-picker";
const button = document.createElement("button");
button.id = "chart-picker-button";
button.className = "chart-picker-button";
button.type = "button";
button.setAttribute("aria-haspopup", "true");
button.setAttribute("aria-expanded", "false");
button.setAttribute("aria-label", `Chart type ${chartTypeLabel(activeVisualizationType)}`);
const buttonLabel = document.createElement("span");
buttonLabel.textContent =
isDetailDisplayMode()
? "Chart type"
: chartTypeLabel(activeVisualizationType);
button.append(buttonLabel, caretIcon());

const popover = document.createElement("div");
popover.id = "chart-picker-popover";
popover.className = "chart-picker-popover menu-surface";
popover.hidden = true;
for (const section of compatibleChartPickerSections(activeDataset())) {
const sectionEl = document.createElement("section");
sectionEl.className = "chart-picker-section";
if (section.title) {
const heading = document.createElement("h2");
heading.className = "chart-picker-heading";
heading.textContent = section.title;
sectionEl.appendChild(heading);
}
const grid = document.createElement("div");
grid.className = "chart-option-grid";
for (const option of section.options) {
const optionButton = document.createElement("button");
optionButton.type = "button";
optionButton.className = "chart-option";
optionButton.setAttribute("aria-pressed", String(option.type === activeVisualizationType));
const preview = document.createElement("span");
preview.className = "chart-option-preview";
preview.innerHTML = chartPreviewSvg(option.preview);
const label = document.createElement("span");
label.className = "chart-option-label";
label.textContent = option.label;
const check = document.createElement("span");
check.className = "chart-option-check";
check.appendChild(lucideIcon("check"));
optionButton.append(preview, label, check);
optionButton.addEventListener("click", () => {
activeVisualizationType = option.type;
if (viewMode === "table") setViewMode("both");
closeChartPicker();
render();
notifyChartSpecChange();
});
grid.appendChild(optionButton);
}
sectionEl.appendChild(grid);
popover.appendChild(sectionEl);
}

button.addEventListener("click", (event) => {
event.stopPropagation();
closeFieldMenus();
closeDataFilterMenus();
closeShareMenu();
const nextHidden = !popover.hidden;
popover.hidden = nextHidden;
popover.classList.toggle("opening", !nextHidden);
button.setAttribute("aria-expanded", String(!nextHidden));
});
picker.addEventListener("click", (event) => {
event.stopPropagation();
});
picker.append(button, popover);
root.appendChild(picker);
}

function closeFieldMenus(options = {}) {
document.querySelectorAll(".field-menu").forEach((menu) => removeMenuSurface(menu, options));
document.querySelectorAll(".field-pill[aria-expanded='true']").forEach((button) => button.setAttribute("aria-expanded", "false"));
}

function closeDataFilterMenus(options = {}) {
document.querySelectorAll(".filter-menu-list").forEach((menu) => removeMenuSurface(menu, options));
document.querySelectorAll(".filter-menu-button[aria-expanded='true']").forEach((button) => button.setAttribute("aria-expanded", "false"));
}

function setDataFilter(dataset, fieldKey, value) {
const key = dataFilterKey(dataset, fieldKey);
if (!value || value === "all") delete selectedDataFilters[key];
else selectedDataFilters[key] = value;
pruneDataFilters(dataset);
closeDataFilterMenus();
resetVisibleSeries();
render();
}

function filterOptionLabel(value) {
return value === "all" ? "All" : value;
}

function activeDataFilterCount(dataset = activeDataset()) {
return dataFilterSpecs(dataset).filter((spec) => selectedDataFilterValue(dataset, spec.key) !== "all").length;
}

function positionDataFilterMenu(anchor, menu) {
const boundsLeft = 12;
const boundsRight = window.innerWidth - 12;
menu.style.left = "0px";
menu.style.right = "auto";
const rect = menu.getBoundingClientRect();
let leftOffset = 0;
if (rect.right > boundsRight) leftOffset -= rect.right - boundsRight;
if (rect.left + leftOffset < boundsLeft) leftOffset += boundsLeft - (rect.left + leftOffset);
menu.style.left = `${Math.round(leftOffset)}px`;
}

function openDataFilterMenu(anchor, spec) {
const existing = anchor.parentElement.querySelector(".filter-menu-list");
closeFieldMenus();
closeChartPicker();
if (existing) {
closeDataFilterMenus();
closeShareMenu();
return;
}
closeDataFilterMenus({ immediate: true });
closeShareMenu({ immediate: true });
anchor.setAttribute("aria-expanded", "true");
const menu = document.createElement("div");
menu.className = "filter-menu-list menu-surface opening";
menu.setAttribute("role", "menu");
const current = selectedDataFilterValue(activeDataset(), spec.key);
const options = ["all", ...filterOptionsForSpec(activeDataset(), spec)];
for (const option of options) {
const item = document.createElement("button");
const selected = option === current;
item.type = "button";
item.className = "filter-menu-item";
item.setAttribute("role", "menuitemradio");
item.setAttribute("aria-checked", String(selected));
const label = document.createElement("span");
label.textContent = filterOptionLabel(option);
item.appendChild(label);
if (selected) item.appendChild(lucideIcon("check", { width: "14", height: "14" }));
item.addEventListener("click", (event) => {
event.stopPropagation();
setDataFilter(activeDataset(), spec.key, option);
});
menu.appendChild(item);
}
menu.addEventListener("click", (event) => event.stopPropagation());
anchor.parentElement.appendChild(menu);
positionDataFilterMenu(anchor, menu);
}

function dataFilterChip(spec) {
const wrapper = document.createElement("div");
wrapper.className = "filter-menu";
const button = document.createElement("button");
button.type = "button";
button.className = "filter-menu-button";
button.setAttribute("aria-haspopup", "menu");
button.setAttribute("aria-expanded", "false");
const label = document.createElement("span");
label.className = "filter-menu-label";
label.textContent = spec.label;
const value = document.createElement("span");
value.className = "filter-menu-value";
const selectedValue = selectedDataFilterValue(activeDataset(), spec.key);
if (selectedValue !== "all") {
label.textContent = `${spec.label}:`;
value.textContent = filterOptionLabel(selectedValue);
button.dataset.hasFilter = "true";
button.append(label, caretIcon());
} else {
button.append(label, caretIcon());
}
button.addEventListener("click", (event) => {
event.stopPropagation();
openDataFilterMenu(button, spec);
});
wrapper.appendChild(button);
return wrapper;
}

function dataFilterOptionsPanel(spec) {
const panel = document.createElement("div");
panel.className = "menu-submenu-panel menu-surface";
panel.setAttribute("role", "menu");
const current = selectedDataFilterValue(activeDataset(), spec.key);
const options = ["all", ...filterOptionsForSpec(activeDataset(), spec)];
for (const option of options) {
const selected = option === current;
const row = menuRow(filterOptionLabel(option), selected ? lucideIcon("check", { width: "14", height: "14" }) : "", () => {
setDataFilter(activeDataset(), spec.key, option);
}, { active: selected });
row.setAttribute("role", "menuitemradio");
row.setAttribute("aria-checked", String(selected));
panel.appendChild(row);
}
return panel;
}

function openFiltersMenu(anchor, specs) {
const existing = anchor.parentElement.querySelector(".filter-menu-list");
closeFieldMenus();
closeChartPicker();
if (existing) {
closeDataFilterMenus();
closeShareMenu();
return;
}
closeDataFilterMenus({ immediate: true });
closeShareMenu({ immediate: true });
anchor.setAttribute("aria-expanded", "true");
const menu = document.createElement("div");
menu.className = "filter-menu-list menu-surface opening";
menu.setAttribute("role", "menu");
for (const spec of specs) {
const selected = selectedDataFilterValue(activeDataset(), spec.key);
menu.appendChild(
menuSubmenu(
spec.label,
selected !== "all" ? filterOptionLabel(selected) : "",
dataFilterOptionsPanel(spec),
{ active: selected !== "all" },
),
);
}
const count = activeDataFilterCount(activeDataset());
if (count) {
menu.appendChild(document.createElement("div")).className = "menu-divider";
menu.appendChild(menuRow("Reset filters", "", () => {
selectedDataFilters = {};
closeDataFilterMenus();
resetVisibleSeries();
render();
}));
}
menu.addEventListener("click", (event) => event.stopPropagation());
anchor.parentElement.appendChild(menu);
positionDataFilterMenu(anchor, menu);
}

function filtersMenuChip(specs) {
const wrapper = document.createElement("div");
wrapper.className = "filter-menu";
const button = document.createElement("button");
button.type = "button";
button.className = "filter-menu-button";
button.setAttribute("aria-haspopup", "menu");
button.setAttribute("aria-expanded", "false");
const label = document.createElement("span");
label.className = "filter-menu-label";
label.textContent = "Filters";
const count = activeDataFilterCount(activeDataset());
const value = document.createElement("span");
value.className = "filter-menu-value";
value.textContent = activeDataFilterSummary(activeDataset());
value.title = value.textContent;
button.setAttribute("aria-label", `Filters ${value.textContent}`);
if (count) button.dataset.hasFilter = "true";
button.append(label, caretIcon());
button.addEventListener("click", (event) => {
event.stopPropagation();
openFiltersMenu(button, specs);
});
wrapper.appendChild(button);
return wrapper;
}

function menuRow(label, value, onClick, options = {}) {
const button = document.createElement("button");
button.type = "button";
button.className = `menu-row${options.active ? " is-active" : ""}${options.danger ? " is-danger" : ""}`;
const labelEl = document.createElement("span");
labelEl.textContent = label;
button.appendChild(labelEl);
if (value) {
const valueEl = document.createElement("span");
valueEl.className = "menu-row-value";
if (value instanceof Node) valueEl.appendChild(value);
else valueEl.textContent = value;
button.appendChild(valueEl);
}
button.addEventListener("click", (event) => {
event.stopPropagation();
onClick?.();
});
return button;
}

function menuValue(value, iconName = "chevronRight") {
const wrapper = document.createElement("span");
wrapper.className = "menu-row-value-with-icon";
if (value) {
const valueEl = document.createElement("span");
valueEl.textContent = value;
wrapper.appendChild(valueEl);
}
wrapper.appendChild(lucideIcon(iconName));
return wrapper;
}

function positionSubmenuPanel(wrapper) {
const panel = wrapper.querySelector(".menu-submenu-panel");
if (!panel) return;
panel.style.left = "calc(100% + 8px)";
panel.style.right = "auto";
panel.style.visibility = "hidden";
panel.style.display = "grid";
const rect = panel.getBoundingClientRect();
if (rect.right > window.innerWidth - 12) {
panel.style.left = "auto";
panel.style.right = "calc(100% + 8px)";
}
panel.style.display = "";
panel.style.visibility = "";
}

function menuSubmenu(label, value, panel, options = {}) {
const wrapper = document.createElement("div");
wrapper.className = "menu-submenu";
const trigger = menuRow(label, menuValue(value), null, options);
trigger.classList.add("menu-submenu-trigger");
trigger.setAttribute("aria-haspopup", "menu");
trigger.setAttribute("aria-expanded", "false");
trigger.addEventListener("click", (event) => {
event.stopPropagation();
const open = !wrapper.classList.contains("is-open");
wrapper.parentElement?.querySelectorAll(".menu-submenu.is-open").forEach((item) => {
if (item === wrapper) return;
item.classList.remove("is-open");
item.querySelector(".menu-submenu-trigger")?.setAttribute("aria-expanded", "false");
});
wrapper.classList.toggle("is-open", open);
trigger.setAttribute("aria-expanded", String(open));
if (open) positionSubmenuPanel(wrapper);
});
wrapper.addEventListener("mouseenter", () => positionSubmenuPanel(wrapper));
wrapper.addEventListener("focusin", () => positionSubmenuPanel(wrapper));
wrapper.append(trigger, panel);
return wrapper;
}

function menuHeader(label, value = "") {
const row = document.createElement("div");
row.className = "menu-heading";
const labelEl = document.createElement("span");
labelEl.textContent = label;
row.appendChild(labelEl);
if (value) {
const valueEl = document.createElement("span");
valueEl.textContent = value;
row.appendChild(valueEl);
}
return row;
}

function setChartField(role, key) {
if (role === "x") chartConfig.xField = key;
if (role === "y") chartConfig.yField = key;
if (role === "size") chartConfig.sizeField = key;
if (role === "lineStyle") chartConfig.lineStyleField = key;
if (role === "label") chartConfig.labelField = key;
if (role === "color") {
chartConfig.colorField = key;
revealAllSeriesAfterGroupingChange = true;
}
if (role === "x" && !fieldLooksDateLike(activeDataset(), key)) chartConfig.timeUnit = "none";
if (
role === "y" &&
chartConfig.colorField === measureNamesField &&
compatibleMeasureNameFields(activeDataset()).length <= 1
) {
chartConfig.colorField = "";
}
resetVisibleSeries();
closeFieldMenus();
render();
notifyChartSpecChange();
}

function clearChartFields() {
selectedDataFilters = {};
chartConfig = { xField: "x", yField: "y", colorField: "series", lineStyleField: "", labelField: "", sizeField: "", timeUnit: "none", yAggregation: "sum" };
resetChartSettings(activeDataset());
resetChartConfig(activeDataset());
visibleSeries = {};
resetVisibleSeries();
closeFieldMenus();
closeDataFilterMenus();
closeChartPicker();
render();
notifyChartSpecReset();
}

function fieldIconName(dataset, field) {
if (fieldLooksDateLike(dataset, field.key)) return "calendar";
if (field.numeric) return "hash";
return "type";
}

function fieldGroupLabel(field) {
if (field.synthetic) return "Calculated";
return field.numeric ? "Measures" : "Dimensions";
}

function fieldIsSelectedForRole(role, key) {
if (role === "x") return chartConfig.xField === key;
if (role === "y") return chartConfig.yField === key;
if (role === "size") return chartConfig.sizeField === key;
if (role === "label") return chartConfig.labelField === key;
if (role === "color") return chartConfig.colorField === key;
return false;
}

function fieldMenuRow(dataset, role, field, options = {}) {
const row = menuRow("", "", () => setChartField(role, field.key), {
active: fieldIsSelectedForRole(role, field.key),
});
row.innerHTML = "";
const label = document.createElement("span");
label.className = "menu-field-label";
if (options.icons !== false) {
const icon = document.createElement("span");
icon.className = "menu-field-icon";
icon.appendChild(lucideIcon(fieldIconName(dataset, field), { width: "14", height: "14" }));
label.appendChild(icon);
}
const textEl = document.createElement("span");
textEl.textContent = field.label;
label.appendChild(textEl);
row.appendChild(label);
return row;
}

function renderFieldRows(panel, role, options = {}) {
const dataset = activeDataset();
const fields = compatibleFieldsForRole(dataset, role);
const scroll = document.createElement("div");
scroll.className = "menu-scroll";
const showSearch = options.search !== false && fields.length > fieldMenuSearchThreshold;
if (showSearch) {
const search = document.createElement("input");
search.className = "menu-search";
search.type = "search";
search.placeholder = "Filter...";
panel.append(search);
search.addEventListener("input", () => paint(search.value));
}
panel.append(scroll);

const paint = (query = "") => {
const filter = query.trim().toLowerCase();
scroll.innerHTML = "";
let lastGroup = "";
if (options.includeNone) {
const noneRow = menuRow("None", "", () => setChartField(role, ""), {
active: !fieldKeyForRole(role),
});
scroll.appendChild(noneRow);
}
for (const field of fields) {
if (filter && !field.label.toLowerCase().includes(filter) && !field.key.toLowerCase().includes(filter)) continue;
const group = fieldGroupLabel(field);
if (options.grouped !== false && group !== lastGroup) {
scroll.appendChild(menuHeader(group));
lastGroup = group;
}
scroll.appendChild(fieldMenuRow(dataset, role, field, options));
}
};
paint();
}

function appendTimeGrainRows(panel, dataset) {
for (const option of timeUnitOptionsForDataset(dataset)) {
panel.appendChild(
menuRow(option, canonicalTimeUnit(option) === chartConfig.timeUnit ? lucideIcon("check", { width: "14", height: "14" }) : "", () => {
chartConfig.timeUnit = canonicalTimeUnit(option);
closeFieldMenus();
render();
notifyChartSpecChange();
}, { active: canonicalTimeUnit(option) === chartConfig.timeUnit }),
);
}
}

function appendAggregationRows(panel) {
for (const option of aggregationOptions) {
panel.appendChild(
menuRow(option, canonicalAggregation(option) === chartConfig.yAggregation ? lucideIcon("check", { width: "14", height: "14" }) : "", () => {
chartConfig.yAggregation = canonicalAggregation(option);
closeFieldMenus();
render();
notifyChartSpecChange();
}, { active: canonicalAggregation(option) === chartConfig.yAggregation }),
);
}
}

function positionFieldMenu(anchor, menu) {
const panel = document.querySelector(".app-main");
const panelRect = panel?.getBoundingClientRect();
const boundsLeft = Math.max(12, panelRect ? panelRect.left + 12 : 12);
const boundsRight = Math.min(window.innerWidth - 12, panelRect ? panelRect.right - 12 : window.innerWidth - 12);
menu.style.left = "0px";
menu.style.right = "auto";
menu.style.maxWidth = `${Math.max(180, Math.min(240, boundsRight - boundsLeft))}px`;

const menuRect = menu.getBoundingClientRect();
let leftOffset = 0;
if (menuRect.right > boundsRight) {
leftOffset -= menuRect.right - boundsRight;
}
if (menuRect.left + leftOffset < boundsLeft) {
leftOffset += boundsLeft - (menuRect.left + leftOffset);
}
menu.style.left = `${Math.round(leftOffset)}px`;
}

function openFieldMenu(anchor, spec) {
const role = spec.role;
const existing = anchor.parentElement.querySelector(".field-menu");
closeFieldMenus();
closeChartPicker();
closeDataFilterMenus();
closeShareMenu();
if (existing) return;
anchor.setAttribute("aria-expanded", "true");
const menu = document.createElement("div");
menu.className = "field-menu menu-surface opening";
menu.addEventListener("click", (event) => {
event.stopPropagation();
});
const panel = document.createElement("div");
panel.className = "field-menu-panel";
const dataset = activeDataset();

if (role === "x") {
const supportsTime = spec.time !== false;
renderFieldRows(panel, role, { grouped: false, icons: false });
if (supportsTime && fieldLooksDateLike(dataset, chartConfig.xField)) {
panel.appendChild(document.createElement("div")).className = "menu-divider";
panel.appendChild(menuHeader("Time grain"));
appendTimeGrainRows(panel, dataset);
}
} else if (role === "y") {
const supportsAggregation = spec.aggregate !== false;
renderFieldRows(panel, role, { grouped: false, icons: false });
if (supportsAggregation) {
panel.appendChild(document.createElement("div")).className = "menu-divider";
panel.appendChild(menuHeader("Aggregation"));
appendAggregationRows(panel);
}
} else {
renderFieldRows(panel, role, {
grouped: false,
icons: false,
includeNone: !spec.required,
search: false,
});
}
menu.appendChild(panel);
anchor.parentElement.appendChild(menu);
positionFieldMenu(anchor, menu);
}

function fieldPill(spec) {
const role = spec.role;
const dataset = activeDataset();
const detailChrome = isDetailDisplayMode();
const well = document.createElement("div");
well.className = "field-well";
const button = document.createElement("button");
button.type = "button";
button.className = "field-pill";
button.setAttribute("aria-haspopup", "menu");
button.setAttribute("aria-expanded", "false");
const roleEl = document.createElement("span");
roleEl.className = "field-pill-role";
roleEl.textContent = detailChrome ? detailControlLabel(spec) : spec.label;
button.appendChild(roleEl);
const field = document.createElement("span");
field.className = "field-pill-field";
field.textContent =
role === "x" ? fieldLabel(dataset, chartConfig.xField, spec.fallback) :
role === "y" ? fieldLabel(dataset, chartConfig.yField, spec.fallback) :
role === "size" ? chartConfig.sizeField ? fieldLabel(dataset, chartConfig.sizeField, spec.fallback) : spec.fallback :
role === "label" ? chartConfig.labelField ? fieldLabel(dataset, chartConfig.labelField, spec.fallback) : spec.fallback :
role === "time" ? timeUnitLabel(chartConfig.timeUnit) :
chartConfig.colorField ? fieldLabel(dataset, chartConfig.colorField, spec.fallback) : spec.fallback;
button.setAttribute("aria-label", `${roleEl.textContent}: ${field.textContent}`);
if (!detailChrome) button.appendChild(field);
const modifier = document.createElement("span");
modifier.className = "field-pill-modifier";
if (role === "x" && spec.time !== false && fieldLooksDateLike(dataset, chartConfig.xField)) {
modifier.textContent = timeUnitLabel(chartConfig.timeUnit === "none" ? "" : chartConfig.timeUnit);
}
if (role === "y" && spec.aggregate !== false) modifier.textContent = aggregationLabel(chartConfig.yAggregation);
if (modifier.textContent && !detailChrome) button.appendChild(modifier);
button.appendChild(caretIcon("field-pill-caret"));
button.addEventListener("click", (event) => {
event.stopPropagation();
openFieldMenu(button, spec);
});
well.appendChild(button);
return well;
}

function barSettingsHaveSeries(dataset = activeDataset()) {
if (!chartConfig.colorField) return false;
return projectedSeriesCount(projectedDataForType(dataset, "bar")) > 1;
}

function openSettingMenu(anchor, label, value, options, onChange) {
const existing = anchor.parentElement.querySelector(".field-menu");
closeFieldMenus();
closeChartPicker();
closeDataFilterMenus();
closeShareMenu();
if (existing) return;
anchor.setAttribute("aria-expanded", "true");
const menu = document.createElement("div");
menu.className = "field-menu menu-surface opening";
menu.addEventListener("click", (event) => {
event.stopPropagation();
});
const panel = document.createElement("div");
panel.className = "field-menu-panel";
for (const option of options) {
const selected = option.value === value;
const row = menuRow(option.label, selected ? lucideIcon("check", { width: "14", height: "14" }) : "", () => {
onChange(option.value);
render();
closeFieldMenus({ immediate: true });
notifyChartSpecChange();
}, { active: selected });
row.setAttribute("role", "menuitemradio");
row.setAttribute("aria-checked", String(selected));
panel.appendChild(row);
}
menu.appendChild(panel);
anchor.parentElement.appendChild(menu);
positionFieldMenu(anchor, menu);
}

function settingDropdownChip(label, value, options, onChange) {
const selected = options.find((option) => option.value === value) || options[0];
const well = document.createElement("div");
well.className = "field-well chart-setting-control";
const button = document.createElement("button");
button.type = "button";
button.className = "field-pill chart-setting-option";
button.setAttribute("aria-haspopup", "menu");
button.setAttribute("aria-expanded", "false");
const labelEl = document.createElement("span");
labelEl.className = "field-pill-role";
labelEl.textContent = label;
const valueEl = document.createElement("span");
valueEl.className = "field-pill-field";
valueEl.textContent = selected?.label || "";
button.setAttribute("aria-label", `${label}: ${valueEl.textContent}`);
button.append(labelEl, caretIcon("field-pill-caret"));
button.addEventListener("click", (event) => {
event.stopPropagation();
openSettingMenu(button, label, value, options, onChange);
});
well.appendChild(button);
return well;
}

function renderExpandedSettingsControls(root) {
if (!isDetailDisplayMode()) return;
const wells = document.createElement("div");
wells.className = "chart-settings-wells";
if (activeVisualizationType === "bar") {
wells.appendChild(
settingDropdownChip(
"Orientation",
chartSettings.barOrientation,
[
{ label: "Vertical", value: "vertical" },
{ label: "Horizontal", value: "horizontal" },
],
(value) => {
chartSettings.barOrientation = canonicalBarOrientation(value);
},
),
);
if (barSettingsHaveSeries()) {
const selectedMode = chartSettings.barGroupMode === "single" ? "grouped" : chartSettings.barGroupMode;
wells.appendChild(
settingDropdownChip(
"Mode",
selectedMode,
[
{ label: "Grouped", value: "grouped" },
{ label: "Stacked", value: "stacked" },
{ label: "100%", value: "stacked100" },
],
(value) => {
chartSettings.barGroupMode = canonicalBarGroupMode(value);
},
),
);
}
}
root.appendChild(wells);
}

function renderControls() {
const root = document.getElementById("controls");
const showControls = Boolean(specValue(activeDataset(), "show_controls", payload.show_controls));
const appMode = isDetailDisplayMode();
pruneDataFilters(activeDataset());
root.innerHTML = "";
root.hidden = !appMode && !showControls;

if (showControls || appMode) {
const typeGroup = document.createElement("div");
typeGroup.className = "control-group";
const typeLabel = document.createElement("span");
typeLabel.className = "control-label";
typeLabel.textContent = "View";
typeGroup.appendChild(typeLabel);
renderChartPicker(typeGroup);
root.appendChild(typeGroup);

const wells = document.createElement("div");
wells.className = "field-wells";
wells.append(...chartRoleSpecs().map((spec) => fieldPill(spec)));
root.appendChild(wells);

renderExpandedSettingsControls(root);

const clear = document.createElement("button");
clear.type = "button";
clear.className = "clear-button";
clear.textContent = appMode ? "Reset" : "Clear all";
clear.addEventListener("click", clearChartFields);
root.appendChild(clear);
}
}

function render() {
const dataset = activeDataset();
ensureActiveChartTypeIsSupported(dataset);
const subtitle = specValue(dataset, "subtitle", payload.subtitle);
const title = specValue(dataset, "title", payload.title || "Data Analytics chart");
document.getElementById("title").textContent = text(title);
document.getElementById("subtitle").textContent = text(subtitle);
document.getElementById("subtitle").hidden = !subtitle;
renderDetailHeader(dataset, title, subtitle);
setViewMode(viewMode);
setDataMode(dataMode);
renderQueryControls(dataset);

if (isTablePayload(dataset)) {
renderTableFallback(dataset);
} else {
renderAppChrome(dataset);
renderControls();
renderChart();
}
applySplitLayout();
}

window.addEventListener("message", (event) => {
if (!messageTargetsThisWidget(event.data)) return;
applyHostState(event.data);
applyPayload(event.data, event.data);
});

window.addEventListener("openai:set_globals", (event) => {
const globals = event.detail && event.detail.globals;
if (!messageTargetsThisWidget(globals)) return;
applyHostState(globals);
if (globals && applyPayload(globals.toolOutput, globals)) return;
if (!hasExternalPayload) applyPayload(currentHostPayload(), null);
});

setupDisplayModeControls();
setupViewModeControls();
setupDataModeControls();
setupMenuDismissal();
setupAppChromeControls();
setupDetailRefreshButton();
setupDetailShareMenu();
setupSplitResizer();
window.addEventListener("resize", applySplitLayout);
if (!applyPayload(currentHostPayload())) {
const initialPayload = window.openai ? hostedEmptyPayload() : fallbackPayload;
normalizePayload(initialPayload);
lastPayloadSignature = payloadSignature(initialPayload);
render();
}

let hostPollAttempts = 0;
const hostPoll = window.setInterval(() => {
hostPollAttempts += 1;
setDisplayMode(currentHostDisplayMode());
if (!hasExternalPayload) {
applyPayload(currentHostPayload(), null);
}
if (hostPollAttempts >= 80) window.clearInterval(hostPoll);
}, 250);
