import { ArrowDown, ArrowUp, ArrowUpRight, Boxes, Camera, ChartArea, ChartBar, ChartColumn, ChartColumnStacked, ChartLine, ChartNoAxesColumn, ChartNoAxesCombined, ChartScatter, ChartSpline, Check, ChevronDown, ChevronLeft, ChevronRight, Copy, Database, Ellipsis, Expand, Filter as FunnelIcon, FileDown, FileText, Globe, Laptop, Pencil, Presentation, RefreshCw, Table2, Tally3, Trash2, X, } from "lucide-react";
import { createContext, useCallback, useContext, useEffect, useId, useLayoutEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { AnalyticsLayoutCanvas } from "./layout/AnalyticsLayoutCanvas";
import { mergeVisibleLayoutPreservingHidden } from "./layout/analyticsLayoutCore";
import { isChartType as sharedIsChartType } from "./charting/chart-compatibility";
import { applyChartSpecOverride, chartEncoding, chartEncodingField, chartEncodingFields, chartEncodingLabel, chartHasEncodingSpec, chartSpecOverrideFromWidgetSpec, chartUsedFields, compatibleChartTypesFor, compatibleChartTypesForArtifactCard, withChartType } from "./charting/chart-app-helpers";
import { ChartRenderer } from "./charting/ChartRenderer";
import { RichMarkdown } from "./layout/RichMarkdown";
import { calculateHorizontalScrollEdges, calculateTableSizing } from "./tables/tableSizing";
import { canonicalPublishedSiteUrl, workModeWebPromptUrl } from "./handoff.mjs";
import { copyElementAsImage, copyTextToClipboard, imageCopySuccessMessage, shouldOfferImageClipboardCopy, usePreparedImageExport } from "./imageExport";
import { launchCodexPromptFallback, loadArtifactFromApi, loadHostedPresentation, loadInlineChartWidgetHtml, loadSourceText, readPersistedValue, saveHostedPresentation, sendPromptToHost, writePersistedValue } from "./runtimeEnvironment";
function cloneSerializable(value) {
return JSON.parse(JSON.stringify(value));
}
const DEFAULT_DASHBOARD_CARD_LAYOUT = "half";
const DEFAULT_REPORT_CARD_LAYOUT = "full";
const CARD_DRAG_CANCEL_SELECTOR = ".viz-card__no-drag, button, a, input, textarea, select, [contenteditable='true'], .rich-markdown-editor, [role='button'], [role='menu'], [role='menuitem'], [role='menuitemradio']";
const CHART_FULLSCREEN_HEIGHT = 520;
const TABLE_CARD_PAGE_SIZE = 15;
const SOURCE_DATA_PREVIEW_PAGE_SIZE = 10;
const TABLE_COLUMN_DEFAULT_WIDTH = 144;
const TABLE_COLUMN_DENSE_HORIZONTAL_PADDING = 16;
const TABLE_COLUMN_HEADER_CHROME_WIDTH = 24;
const TABLE_COLUMN_KEYBOARD_STEP = 24;
const TABLE_COLUMN_MAX_WIDTH = 420;
const TABLE_COLUMN_MIN_WIDTH = 88;
const TABLE_COLUMN_NUMERIC_MAX_WIDTH = 136;
const TABLE_COLUMN_SAMPLE_SIZE = 50;
const TABLE_COLUMN_TEXT_MAX_WIDTH = 220;
const TABLE_COLUMN_LONG_TEXT_MAX_WIDTH = 260;
const TABLE_COLUMN_CONTENT_FIT_MAX_WIDTH = 240;
const TABLE_COLUMN_CONTENT_FIT_TARGET_LENGTH = 28;
const EMPTY_HORIZONTAL_SCROLL_EDGES = {
canScrollLeft: false,
canScrollRight: false,
hasOverflow: false,
scrollbarBlockSize: 0,
scrollbarInlineSize: 0
};
const EMPTY_ACCESS_ISSUES = [];
const EMPTY_CARDS = [];
const EMPTY_CHARTS = [];
const EMPTY_FILTERS = [];
const EMPTY_REPORT_BLOCKS = [];
const EMPTY_TABLES = [];
export const MCP_ARTIFACT_READER_ENVIRONMENT = Object.freeze({
capabilities: Object.freeze({
copyImage: true,
deleteContent: true,
editContent: true,
editVisualization: true,
fetchSourceText: true,
hostFullscreen: true,
hostPrompts: true,
persistState: true,
reorderContent: true
}),
mode: "mcp"
});
export const PORTABLE_ARTIFACT_READER_ENVIRONMENT = Object.freeze({
capabilities: Object.freeze({
copyImage: false,
deleteContent: false,
editContent: false,
editVisualization: false,
fetchSourceText: false,
hostFullscreen: false,
hostPrompts: false,
persistState: false,
reorderContent: false
}),
mode: "portable"
});
const ArtifactReaderContext = createContext({
capabilities: artifactCapabilities(null, MCP_ARTIFACT_READER_ENVIRONMENT),
environment: MCP_ARTIFACT_READER_ENVIRONMENT
});
function useArtifactReaderContext() {
return useContext(ArtifactReaderContext);
}
function getHeatmapFill(intensity) {
const index = clamp(Math.floor(intensity * heatmapBlueScale.length), 0, heatmapBlueScale.length - 1);
return heatmapBlueScale[index];
}
function hostedPackageInfoFromBootstrap() {
if (typeof window === "undefined")
return null;
const hosting = window.__DATASCIENCE_ARTIFACT_HOSTING__;
if (!hosting || typeof hosting !== "object")
return null;
const deliveryMode = hosting.mode === "site_creator"
? hosting.mode
: null;
if (hosting.readOnly !== true && !deliveryMode)
return null;
return {
deliveryMode,
hostedEditing: hosting.editing === "presentation" ? "presentation" : null,
hostedReadOnly: hosting.readOnly === true,
controls: hosting.controls && typeof hosting.controls === "object" ? hosting.controls : {}
};
}
function withHostedBootstrap(packageInfo) {
const bootstrap = hostedPackageInfoFromBootstrap();
if (!bootstrap)
return packageInfo;
const nextPackageInfo = packageInfo && typeof packageInfo === "object" ? packageInfo : {};
const nextControls = nextPackageInfo.controls && typeof nextPackageInfo.controls === "object" ? nextPackageInfo.controls : {};
return {
...nextPackageInfo,
...bootstrap,
controls: {
...nextControls,
...bootstrap.controls
}
};
}
function asNumber(value) {
if (typeof value === "number" && Number.isFinite(value))
return value;
if (typeof value === "string" && value.trim() !== "") {
const numeric = Number(value.replace(/,/g, ""));
if (Number.isFinite(numeric))
return numeric;
}
return null;
}
function asFiniteNumber(value, fallback = 0) {
if (typeof value === "number" && Number.isFinite(value))
return value;
if (typeof value === "string") {
const numeric = Number(value);
if (Number.isFinite(numeric))
return numeric;
}
return fallback;
}
function clamp(value, min, max) {
return Math.max(min, Math.min(max, value));
}
function formatValue(value, format = "compact") {
const numeric = asNumber(value);
if (numeric == null)
return value == null ? "n/a" : String(value);
if (format === "percent") {
return new Intl.NumberFormat(undefined, {
maximumFractionDigits: 1,
style: "percent"
}).format(numeric);
}
if (format === "currency") {
return new Intl.NumberFormat(undefined, {
currency: "USD",
maximumFractionDigits: 2,
notation: "compact",
style: "currency"
}).format(numeric);
}
if (format === "number") {
return new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 }).format(numeric);
}
return new Intl.NumberFormat(undefined, {
maximumFractionDigits: 2,
notation: "compact"
}).format(numeric);
}
function cardLabel(card) {
return cardMetrics(card)[0]?.label ?? card.id;
}
function rowMatchesFilter(row, filter) {
if (!filter)
return true;
return Object.entries(filter).every(([field, expected]) => String(row[field] ?? "") === String(expected ?? ""));
}
function movementDirection(value) {
if (typeof value !== "string")
return null;
const trimmed = value.trim();
if (!trimmed)
return null;
if (/^[+↑]/.test(trimmed))
return "positive";
if (/^[-−↓]/.test(trimmed))
return "negative";
return null;
}
function formatMetricValue(value, metric) {
if (value == null || value === "")
return null;
const numeric = asNumber(value);
const rendered = formatValue(value, metric.format);
if (!metric.signed || numeric == null || numeric === 0)
return rendered;
return `${numeric > 0 ? "+" : ""}${rendered}`;
}
function metricMovementDirection(value, signed = false) {
if (!signed)
return null;
const numeric = asNumber(value);
if (numeric != null) {
if (numeric > 0)
return "positive";
if (numeric < 0)
return "negative";
return "neutral";
}
return movementDirection(value);
}
function cardMetrics(card) {
return Array.isArray(card.metrics) ? card.metrics : [];
}
function MetricInfoIcon({ className }) {
return (<svg aria-hidden="true" className={className} fill="none" height="21" viewBox="0 0 21 21" width="21" xmlns="http://www.w3.org/2000/svg">
<path d="M10.6 9.70459C11.0142 9.70461 11.35 10.0404 11.35 10.4546V13.7876C11.35 14.2018 11.0142 14.5376 10.6 14.5376C10.1858 14.5376 9.84998 14.2018 9.84998 13.7876V10.4546C9.84998 10.0404 10.1858 9.70459 10.6 9.70459Z" fill="currentColor"/>
<path d="M10.6 6.2876C11.1292 6.28762 11.558 6.71732 11.558 7.24658C11.5578 7.77569 11.1291 8.20457 10.6 8.20459C10.0708 8.20459 9.64215 7.7757 9.64197 7.24658C9.64197 6.71731 10.0707 6.2876 10.6 6.2876Z" fill="currentColor"/>
<path clipRule="evenodd" d="M10.6 2.53955C14.9713 2.53955 18.515 6.08326 18.515 10.4546C18.515 14.8259 14.9713 18.3696 10.6 18.3696C6.22864 18.3696 2.68494 14.8259 2.68494 10.4546C2.68494 6.08326 6.22864 2.53955 10.6 2.53955ZM10.6 3.86963C6.96318 3.86963 4.01501 6.81779 4.01501 10.4546C4.01501 14.0914 6.96318 17.0396 10.6 17.0396C14.2368 17.0396 17.1849 14.0914 17.1849 10.4546C17.1849 6.81779 14.2368 3.86963 10.6 3.86963Z" fill="currentColor" fillRule="evenodd"/>
</svg>);
}
const TOOLTIP_OPEN_DELAY_MS = 300;
function MetricDescriptionPopover({ description, label }) {
const tooltipId = useId();
const buttonRef = useRef(null);
const popoverRef = useRef(null);
const openTimerRef = useRef(null);
const [isOpen, setIsOpen] = useState(false);
const [popoverStyle, setPopoverStyle] = useState(null);
const clearOpenTimer = useCallback(() => {
if (openTimerRef.current == null)
return;
window.clearTimeout(openTimerRef.current);
openTimerRef.current = null;
}, []);
const openImmediately = useCallback(() => {
clearOpenTimer();
setIsOpen(true);
}, [clearOpenTimer]);
const openAfterDelay = useCallback(() => {
clearOpenTimer();
openTimerRef.current = window.setTimeout(() => {
openTimerRef.current = null;
setIsOpen(true);
}, TOOLTIP_OPEN_DELAY_MS);
}, [clearOpenTimer]);
const closePopover = useCallback(() => {
clearOpenTimer();
setIsOpen(false);
}, [clearOpenTimer]);
const updatePopoverPosition = useCallback(() => {
if (typeof window === "undefined")
return;
const anchor = buttonRef.current?.getBoundingClientRect();
if (!anchor)
return;
const margin = 12;
const gap = 8;
const maxWidth = Math.max(120, Math.min(320, window.innerWidth - margin * 2));
const popoverRect = popoverRef.current?.getBoundingClientRect();
const width = Math.min(popoverRect?.width ?? maxWidth, maxWidth);
const height = popoverRect?.height ?? 0;
let left = anchor.left + anchor.width / 2 - width / 2;
left = clamp(left, margin, window.innerWidth - margin - width);
let top = anchor.bottom + gap;
if (height && top + height > window.innerHeight - margin && anchor.top - height - gap >= margin) {
top = anchor.top - height - gap;
}
else if (height) {
top = clamp(top, margin, window.innerHeight - margin - height);
}
setPopoverStyle((current) => {
if (current?.left === left && current?.top === top && current?.maxWidth === maxWidth)
return current;
return { left, maxWidth, top };
});
}, []);
useEffect(() => {
if (!isOpen) {
setPopoverStyle(null);
return;
}
updatePopoverPosition();
const frame = window.requestAnimationFrame(updatePopoverPosition);
window.addEventListener("resize", updatePopoverPosition);
window.addEventListener("scroll", updatePopoverPosition, true);
return () => {
window.cancelAnimationFrame(frame);
window.removeEventListener("resize", updatePopoverPosition);
window.removeEventListener("scroll", updatePopoverPosition, true);
};
}, [isOpen, updatePopoverPosition]);
useEffect(() => clearOpenTimer, [clearOpenTimer]);
const renderedPopoverStyle = popoverStyle
? { left: popoverStyle.left, maxWidth: popoverStyle.maxWidth, top: popoverStyle.top }
: { left: 0, maxWidth: "min(320px, calc(100vw - 24px))", top: 0, visibility: "hidden" };
return (<span className="kpi-info-wrap" onBlur={closePopover} onFocus={openImmediately} onMouseEnter={openAfterDelay} onMouseLeave={closePopover}>
<button aria-describedby={isOpen ? tooltipId : undefined} aria-label={`${label}: ${description}`} className="kpi-info" ref={buttonRef} type="button">
<MetricInfoIcon className="kpi-info-icon"/>
</button>
{isOpen && typeof document !== "undefined" ? createPortal(<span className="kpi-info-popover" id={tooltipId} ref={popoverRef} role="tooltip" style={renderedPopoverStyle}>
{description}
</span>, document.body) : null}
</span>);
}
function tableColumnFormat(column) {
if (column.format)
return column.format;
return column.type === "currency" || column.type === "number" || column.type === "percent"
? column.type
: undefined;
}
function tableColumnLooksLikeMovement(column) {
return column.movement === true || column.semantic === "movement" || column.role === "movement";
}
function tableCellMovementClass(column, value) {
if (!tableColumnLooksLikeMovement(column))
return "";
const numeric = asNumber(value);
const direction = numeric == null ? movementDirection(value) : numeric > 0 ? "positive" : numeric < 0 ? "negative" : "neutral";
if (!direction || direction === "neutral")
return "";
return `table-cell-movement table-cell-movement-${direction}`;
}
function formatTableDate(value) {
if (value == null || value === "")
return "";
if (value instanceof Date && !Number.isNaN(value.getTime())) {
return new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(value);
}
if (typeof value !== "string")
return String(value);
const trimmed = value.trim();
const monthMatch = trimmed.match(/^(\d{4})-(\d{2})$/);
if (monthMatch) {
const [, yearValue, monthValue] = monthMatch;
const date = new Date(Date.UTC(Number(yearValue), Number(monthValue) - 1, 1));
if (!Number.isNaN(date.getTime())) {
return new Intl.DateTimeFormat(undefined, {
month: "short",
timeZone: "UTC",
year: "numeric"
}).format(date);
}
}
const dayMatch = trimmed.match(/^(\d{4})-(\d{2})-(\d{2})(?:$|[T\s])/);
if (dayMatch) {
const [, yearValue, monthValue, dayValue] = dayMatch;
const date = new Date(Date.UTC(Number(yearValue), Number(monthValue) - 1, Number(dayValue)));
if (!Number.isNaN(date.getTime())) {
return new Intl.DateTimeFormat(undefined, {
day: "numeric",
month: "short",
timeZone: "UTC",
year: "numeric"
}).format(date);
}
}
return trimmed;
}
function formatTableCellValue(column, value) {
if (column.type === "date")
return formatTableDate(value);
const format = tableColumnFormat(column);
const rendered = format ? formatValue(value, format) : String(value ?? "");
if (!tableColumnLooksLikeMovement(column))
return rendered;
const numeric = asNumber(value);
if (numeric == null || numeric === 0)
return rendered;
return `${numeric > 0 ? "+" : ""}${rendered}`;
}
function normalizedTableTextLength(value) {
return String(value ?? "").replace(/\s+/g, " ").trim().length;
}
function percentileValue(values, percentile) {
if (!values.length)
return 0;
const sorted = [...values].sort((a, b) => a - b);
const index = clamp(Math.ceil(sorted.length * percentile) - 1, 0, sorted.length - 1);
return sorted[index];
}
function isNumericTableColumn(column, rows) {
if (tableColumnFormat(column))
return true;
let observed = false;
for (const row of rows.slice(0, TABLE_COLUMN_SAMPLE_SIZE)) {
const value = row[column.field];
if (value == null || value === "")
continue;
observed = true;
if (asNumber(value) == null)
return false;
}
return observed;
}
function tableColumnDisplayText(column, row) {
return formatTableCellValue(column, row[column.field]);
}
function estimateTableColumnWidth(column, rows, density) {
const sampleRows = rows.slice(0, TABLE_COLUMN_SAMPLE_SIZE);
const labelLength = normalizedTableTextLength(column.label);
const cellLengths = sampleRows
.map((row) => normalizedTableTextLength(tableColumnDisplayText(column, row)))
.filter((length) => length > 0);
const p90Length = percentileValue([labelLength, ...cellLengths], 0.9);
const maxLength = Math.max(labelLength, ...cellLengths, 0);
const columnKey = `${column.field} ${column.label}`.toLowerCase();
const isLongTextColumn = /(comment|description|detail|explanation|insight|interpretation|note|reason|summary)/.test(columnKey)
|| maxLength > 34;
const isNumericColumn = isNumericTableColumn(column, sampleRows);
const isDateColumn = /(date|day|month|quarter|week)/.test(columnKey);
const horizontalPadding = TABLE_COLUMN_HEADER_CHROME_WIDTH + (density === "dense" ? TABLE_COLUMN_DENSE_HORIZONTAL_PADDING : 0);
const charWidth = isNumericColumn ? 7.2 : 7.4;
if (column.sizing === "content") {
const targetLength = Math.min(Math.max(labelLength, p90Length), TABLE_COLUMN_CONTENT_FIT_TARGET_LENGTH);
const measuredContentWidth = Math.ceil(targetLength * charWidth + horizontalPadding);
return clamp(measuredContentWidth, TABLE_COLUMN_MIN_WIDTH, TABLE_COLUMN_CONTENT_FIT_MAX_WIDTH);
}
const targetLength = isLongTextColumn
? Math.min(Math.max(labelLength + 4, p90Length), 44)
: Math.max(labelLength, p90Length);
const measuredWidth = Math.ceil(targetLength * charWidth + horizontalPadding);
if (isNumericColumn) {
const minWidth = tableColumnFormat(column) === "percent" ? 96 : 108;
return clamp(measuredWidth, minWidth, TABLE_COLUMN_NUMERIC_MAX_WIDTH);
}
if (isDateColumn) {
return clamp(measuredWidth, 116, 156);
}
if (isLongTextColumn) {
return clamp(measuredWidth, 220, TABLE_COLUMN_LONG_TEXT_MAX_WIDTH);
}
return clamp(measuredWidth, density === "dense" ? 124 : 112, TABLE_COLUMN_TEXT_MAX_WIDTH);
}
function estimateTableColumnWidths(table, rows, density) {
return Object.fromEntries(table.columns.map((column) => [
column.field,
estimateTableColumnWidth(column, rows, density)
]));
}
function formatDate(value) {
if (!value)
return "Unknown";
const date = new Date(value);
if (Number.isNaN(date.getTime()))
return value;
return new Intl.DateTimeFormat(undefined, {
dateStyle: "medium",
timeStyle: "short"
}).format(date);
}
function snapshotStatusLabel(status) {
if (!status || status === "ready")
return null;
if (status === "fixture")
return "Fixture data";
if (status === "partial")
return null;
return "Blocked snapshot";
}
function getRows(snapshot, dataset) {
return snapshot?.datasets?.[dataset] ?? [];
}
function asArray(value) {
return Array.isArray(value) ? value : [];
}
function asRecord(value) {
return value && typeof value === "object" && !Array.isArray(value)
? value
: {};
}
function normalizeManifest(rawManifest) {
const manifest = asRecord(rawManifest);
return {
...manifest,
version: 1,
title: typeof manifest.title === "string" ? manifest.title : "Data Analytics artifact",
generatedAt: typeof manifest.generatedAt === "string" ? manifest.generatedAt : "",
filters: asArray(manifest.filters).map((rawFilter) => {
const filter = asRecord(rawFilter);
return {
...filter,
targets: asArray(filter.targets)
};
}),
cards: asArray(manifest.cards).map((rawCard) => asRecord(rawCard)),
charts: asArray(manifest.charts).map((rawChart) => {
const chart = asRecord(rawChart);
return {
...chart,
referenceLines: asArray(chart.referenceLines)
};
}),
tables: asArray(manifest.tables).map((rawTable) => {
const table = asRecord(rawTable);
return {
...table,
columns: asArray(table.columns)
};
}),
sources: asArray(manifest.sources).map((rawSource) => asRecord(rawSource)),
blocks: asArray(manifest.blocks).map((rawBlock) => {
const block = asRecord(rawBlock);
return {
...block,
cardIds: asArray(block.cardIds)
};
})
};
}
function normalizeSnapshot(rawSnapshot) {
const snapshot = asRecord(rawSnapshot);
const datasets = {};
const rawDatasets = asRecord(snapshot.datasets);
for (const [dataset, rows] of Object.entries(rawDatasets)) {
datasets[dataset] = asArray(rows).filter((row) => Boolean(row) && typeof row === "object" && !Array.isArray(row));
}
return {
...snapshot,
version: 1,
generatedAt: typeof snapshot.generatedAt === "string" ? snapshot.generatedAt : "",
datasets,
accessIssues: asArray(snapshot.accessIssues)
};
}
function sourceIdentity(source, index) {
return source.id ?? source.path ?? source.href ?? `source:${index}`;
}
function mergedArtifactSources(manifestSources, payloadSources) {
const merged = new Map();
for (const [index, rawSource] of [...asArray(manifestSources), ...asArray(payloadSources)].entries()) {
const source = asRecord(rawSource);
const identity = sourceIdentity(source, index);
merged.set(identity, { ...(merged.get(identity) ?? {}), ...source });
}
return [...merged.values()];
}
function normalizeArtifact(artifact) {
const rawArtifact = asRecord(artifact);
const rawManifest = asRecord(rawArtifact.manifest);
const surface = rawArtifact.surface === "report" || rawArtifact.surface === "dashboard"
? rawArtifact.surface
: rawManifest.surface;
return {
manifest: normalizeManifest({
...rawManifest,
...(surface ? { surface } : {}),
sources: mergedArtifactSources(rawManifest.sources, rawArtifact.sources)
}),
packageInfo: asRecord(rawArtifact.packageInfo ?? rawArtifact.package_info),
snapshot: normalizeSnapshot(rawArtifact.snapshot)
};
}
function normalizeReaderEnvironment(environment) {
const rawEnvironment = asRecord(environment);
const defaults = rawEnvironment.mode === "portable"
? PORTABLE_ARTIFACT_READER_ENVIRONMENT
: MCP_ARTIFACT_READER_ENVIRONMENT;
return {
...defaults,
...rawEnvironment,
capabilities: {
...defaults.capabilities,
...asRecord(rawEnvironment.capabilities)
}
};
}
function filterTargets(filter) {
const targets = [{ dataset: filter.dataset, field: filter.field }];
for (const target of filter.targets ?? []) {
targets.push({ dataset: target.dataset, field: target.field ?? filter.field });
}
const seen = new Set();
return targets.filter((target) => {
const key = `${target.dataset}\u0001${target.field}`;
if (seen.has(key))
return false;
seen.add(key);
return true;
});
}
function filterFieldForDataset(filter, dataset) {
return filterTargets(filter).find((target) => target.dataset === dataset)?.field ?? null;
}
function dashboardSurfaceDatasets(cards, charts, tables) {
return new Set([...cards, ...charts, ...tables]
.map((surface) => surface.dataset)
.filter((dataset) => Boolean(dataset)));
}
function isGlobalFilter(filter, cards, charts, tables) {
const requiredDatasets = dashboardSurfaceDatasets(cards, charts, tables);
if (requiredDatasets.size <= 1)
return true;
const targetDatasets = new Set(filterTargets(filter).map((target) => target.dataset));
return [...requiredDatasets].every((dataset) => targetDatasets.has(dataset));
}
function getGlobalFilters(filters, cards, charts, tables) {
return filters.filter((filter) => isGlobalFilter(filter, cards, charts, tables));
}
function filterRowsForDataset(rows, dataset, filters, selectedFilters, usedFields = []) {
const usedFieldSet = new Set(usedFields.filter(Boolean));
const explicitAllFields = new Set(filters
.map((filter) => {
const field = filterFieldForDataset(filter, dataset);
const selected = selectedFilters[filter.id] ?? filter.defaultValue ?? "all";
return field && selected === "all" && rows.some((row) => String(row[field] ?? "") === "all")
? field
: null;
})
.filter((field) => Boolean(field)));
const filteredRows = rows.filter((row) => filters.every((filter) => {
const field = filterFieldForDataset(filter, dataset);
if (!field)
return true;
const selected = selectedFilters[filter.id] ?? filter.defaultValue ?? "all";
if (selected === "all") {
return !explicitAllFields.has(field) || String(row[field] ?? "") === "all";
}
return String(row[field] ?? "") === selected;
}));
const aggregateFields = Object.keys(rows[0] ?? {}).filter((field) => {
if (usedFieldSet.has(field))
return false;
let hasAggregate = false;
let hasBreakdown = false;
for (const row of filteredRows) {
const value = String(row[field] ?? "");
if (value === "all")
hasAggregate = true;
else if (value)
hasBreakdown = true;
if (hasAggregate && hasBreakdown)
return true;
}
return false;
});
if (!aggregateFields.length)
return filteredRows;
const aggregateRows = filteredRows.filter((row) => aggregateFields.every((field) => String(row[field] ?? "") === "all"));
return aggregateRows.length ? aggregateRows : filteredRows;
}
function DashboardShell({ children, detailMode = false, isEditMode = false, surface }) {
return (<main className={`dashboard-shell ${surface === "report" ? "report-shell" : ""} ${detailMode ? "chart-detail-shell" : ""} ${isEditMode ? "is-app-editing" : ""}`.trim()} data-edit-mode={isEditMode ? "true" : "false"}>
{children}
</main>);
}
function dashboardCardLayout(layout) {
return layout ?? DEFAULT_DASHBOARD_CARD_LAYOUT;
}
function reportCardLayout(layout) {
return layout ?? DEFAULT_REPORT_CARD_LAYOUT;
}
function metricCardBlockId(blockId, cardId) {
return `metric:${blockId}:${cardId}`;
}
function contentLayoutKey(manifest) {
if (!manifest)
return null;
const base = `${manifest.title}:${manifest.generatedAt}`;
return `datascience-dashboard:content-layout:v2:${base}`;
}
function chartTextKey(manifest) {
if (!manifest)
return null;
const base = `${manifest.title}:${manifest.generatedAt}`;
return `datascience-dashboard:chart-text:${base}`;
}
function chartTypeKey(manifest) {
if (!manifest)
return null;
const base = `${manifest.title}:${manifest.generatedAt}`;
return `datascience-${manifest.surface ?? "dashboard"}:chart-type:${base}`;
}
function chartSpecKey(manifest) {
if (!manifest)
return null;
const base = `${manifest.title}:${manifest.generatedAt}`;
return `datascience-${manifest.surface ?? "dashboard"}:chart-spec:${base}`;
}
function pageTitleTextKey(manifest) {
if (!manifest)
return null;
const base = `${manifest.title}:${manifest.generatedAt}`;
return `datascience-${manifest.surface ?? "dashboard"}:page-title:${base}`;
}
function tableTextKey(manifest) {
if (!manifest)
return null;
const base = `${manifest.title}:${manifest.generatedAt}`;
return `datascience-${manifest.surface ?? "dashboard"}:table-text:${base}`;
}
function storageKeyHash(value) {
let hash = 2166136261;
for (let index = 0; index < value.length; index += 1) {
hash ^= value.charCodeAt(index);
hash = Math.imul(hash, 16777619);
}
return (hash >>> 0).toString(36);
}
function blockTextKey(manifest) {
if (!manifest)
return null;
const base = `${manifest.title}:${manifest.generatedAt}`;
const blockSignature = (manifest.blocks ?? [])
.map((block) => `${block.id}:${block.type}:${typeof block.body === "string" ? storageKeyHash(block.body) : ""}`)
.join(",");
return `datascience-report:block-text:${base}:${storageKeyHash(blockSignature)}`;
}
function deletedReportBlocksKey(manifest) {
if (!manifest)
return null;
const base = `${manifest.title}:${manifest.generatedAt}`;
const blockSignature = (manifest.blocks ?? [])
.map((block) => block.id)
.join(",");
return `datascience-report:deleted-blocks:${base}:${blockSignature}`;
}
function tableColumnWidthKey(manifest) {
if (!manifest)
return null;
const base = `${manifest.title}:${manifest.generatedAt}`;
const surface = manifest.surface ?? "dashboard";
const tableSignature = (manifest.tables ?? [])
.map((table) => `${table.id}:${table.columns.map((column) => column.field).join("|")}`)
.join(",");
return `datascience-${surface}:table-column-widths:${base}:${tableSignature}`;
}
function reportContentLayoutKey(manifest) {
if (!manifest)
return null;
const base = `${manifest.title}:${manifest.generatedAt}`;
const blockSignature = (manifest.blocks ?? [])
.map((block) => `${block.id}:${reportCardLayout(block.layout)}:${(block.cardIds ?? []).join("|")}`)
.join(",");
return `datascience-report:content-layout:v4:${base}:${blockSignature}`;
}
function sourceForChart(chart, sources) {
if (chart?.source && typeof chart.source === "object")
return chart.source;
return sources.find((source) => source.id === chart.sourceId) ?? null;
}
function sourceForCard(card, sources) {
if (card?.source && typeof card.source === "object")
return card.source;
return sources.find((source) => source.id === card?.sourceId) ?? null;
}
function sourceForTable(table, sources) {
if (table?.source && typeof table.source === "object")
return table.source;
return sources.find((source) => source.id === table.sourceId) ?? null;
}
function sourceQueryFromChartSpec(chart) {
return chart?.source?.query ?? null;
}
function sourceQueryFromSourceSpec(source) {
if (!source)
return null;
return source.query ?? null;
}
function queryTextFromSourceQuery(sourceQuery) {
return (sourceQuery?.sql ?? "").trim();
}
function accessIssueForChart(chart, issues) {
return (issues.find((issue) => issue.dataset === chart.dataset) ??
issues.find((issue) => issue.sourceId && issue.sourceId === chart.sourceId) ??
null);
}
function activeFilterSummary(filters, selectedFilters) {
const active = filters
.map((filter) => {
const value = selectedFilters[filter.id] ?? filter.defaultValue ?? "all";
return value === "all" ? null : `${filter.label}: ${value}`;
})
.filter(Boolean);
return active.length ? active.join(", ") : "None";
}
function stringListFromValue(value) {
if (Array.isArray(value)) {
return value
.map((item) => {
if (item && typeof item === "object") {
const label = item.label ?? item.name ?? item.table ?? item.field ?? item.metric ?? item.id;
const detail = item.description ?? item.definition ?? item.value ?? item.expression;
return label && detail ? `${label}: ${detail}` : label ?? detail;
}
return item;
})
.map((item) => String(item ?? "").trim())
.filter(Boolean);
}
if (value && typeof value === "object") {
return Object.entries(value)
.map(([key, item]) => `${key}: ${item}`)
.map((item) => item.trim())
.filter(Boolean);
}
const textValue = String(value ?? "").trim();
return textValue ? [textValue] : [];
}
function firstStringList(objects, keys) {
for (const object of objects) {
if (!object)
continue;
for (const key of keys) {
const values = stringListFromValue(object[key]);
if (values.length)
return values;
}
}
return [];
}
function isLikelySourceTableName(value) {
const tableName = String(value ?? "").trim().replace(/^[`"\[]|[`"\]]$/g, "");
return /^[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+){1,3}$/.test(tableName);
}
function sourceTableNamesFromMetadata(objects) {
const values = firstStringList(objects, ["tables_used", "tablesUsed", "source_tables", "sourceTables", "tables"]);
return values.filter(isLikelySourceTableName);
}
function extractTablesFromQuery(queryText) {
const tables = [];
const seen = new Set();
const pattern = /\b(?:from|join)\s+([`"\[]?[\w.-]+(?:\.[\w.-]+){0,3}[`"\]]?)/gi;
let match;
while ((match = pattern.exec(queryText ?? ""))) {
const table = match[1].replace(/^[`"\[]|[`"\]]$/g, "");
const normalized = table.toLowerCase();
if (!table || seen.has(normalized))
continue;
seen.add(normalized);
tables.push(table);
}
return tables;
}
function sourceBuildDetails({ activeFilters, columns = [], dataset, metrics = [], source, sourceQuery, snapshot }) {
const queryText = queryTextFromSourceQuery(sourceQueryFromSourceSpec(source)) || queryTextFromSourceQuery(sourceQuery) || "";
const metadataObjects = [source, sourceQueryFromSourceSpec(source), sourceQuery].filter(Boolean);
const explicitTables = sourceTableNamesFromMetadata(metadataObjects);
const inferredTables = extractTablesFromQuery(queryText);
const tables = explicitTables.length ? explicitTables : inferredTables;
const filters = firstStringList(metadataObjects, [
"filters",
"filter_descriptions",
"filterDescriptions",
"filter_description",
"filterDescription",
]);
const metricDefinitions = firstStringList(metadataObjects, [
"metric_definitions",
"metricDefinitions",
"metrics_definition",
"metricDefinition",
]);
const fallbackMetrics = metricDefinitions.length
? metricDefinitions
: metrics.length
? metrics.map((metric) => `${metric.label}: displayed from ${metric.field}`)
: columns
.filter((column) => ["number", "percent", "currency"].includes(column.format ?? column.type ?? ""))
.map((column) => `${column.label ?? column.field}: displayed from ${column.field}`)
.slice(0, 6);
const selectedFilterRows = typeof activeFilters === "string"
? activeFilters.split(/,\s+(?=[^,:]+:\s)/).map((filter) => filter.trim()).filter(Boolean)
: [];
const filterRows = filters.length
? filters
: activeFilters && activeFilters !== "None" && selectedFilterRows.length
? selectedFilterRows
: ["None declared"];
const tableRows = tables.length ? tables : ["Not declared"];
const snapshotValue = sourceQuery?.executed_at ?? sourceQueryFromSourceSpec(source)?.executed_at ?? snapshot?.generatedAt ?? "Not declared";
return {
dataset: dataset ?? "Not declared",
fields: columns
.map((column) => column.field ?? column.key ?? column.label)
.filter(Boolean),
filters: filterRows,
metricDefinitions: fallbackMetrics.length ? fallbackMetrics : ["Metric values: displayed directly from source columns"],
snapshot: snapshotValue,
tables: tableRows
};
}
function Badge({ children, className = "" }) {
return <span className={`chip ${className}`.trim()}>{children}</span>;
}
function sourceMetadataValue(value, fallback = "Not declared") {
return String(value ?? "").trim() || fallback;
}
function sourceMetadataChips(values, { fallback = "Not declared" } = {}) {
const items = Array.isArray(values) ? values.filter(Boolean) : [values].filter(Boolean);
const visibleItems = items.length ? items : [fallback];
return (<div className="source-metadata-chip-list">
{visibleItems.map((item, index) => <Badge className="source-metadata-chip" key={`${index}-${item}`}>
{item}
</Badge>)}
</div>);
}
function metricDefinitionParts(value) {
const text = String(value ?? "").trim();
const delimiterMatch = text.match(/^(.+?)(:\s*|\s+[=\u2013\u2014]\s+)(.+)$/);
if (delimiterMatch) {
return { definition: delimiterMatch[3], term: delimiterMatch[1] };
}
const proseMatch = text.match(/^(.+?)(\s+(?:are|is|equals|uses?|means|measures|represents|counts|includes|excludes)\s+)(.+)$/i);
if (proseMatch) {
return { definition: `${proseMatch[2].trim()} ${proseMatch[3]}`, term: proseMatch[1] };
}
return { definition: text, term: "Definition" };
}
function metricDefinitionRows(values, fallback = "Not declared") {
const items = Array.isArray(values) ? values.filter(Boolean) : [values].filter(Boolean);
return (items.length ? items : [fallback]).map((item) => {
const definition = metricDefinitionParts(item);
return { definition: definition.definition, metric: definition.term };
});
}
const SOURCE_METRIC_DEFINITION_COLUMNS = [
{ field: "metric", label: "Metric", sizing: "content", type: "text" },
{ field: "definition", label: "Definition", type: "text" }
];
function sourceSnapshotDate(value) {
const formatted = formatDate(value);
return formatted === "Unknown" || formatted === "Not declared" ? "Not declared" : formatted;
}
function compareTableValues(a, b, field, direction) {
const aValue = a[field];
const bValue = b[field];
if (aValue == null && bValue == null)
return 0;
if (aValue == null)
return direction === "asc" ? 1 : -1;
if (bValue == null)
return direction === "asc" ? -1 : 1;
let result = 0;
if (typeof aValue === "number" && typeof bValue === "number") {
result = aValue - bValue;
}
else {
result = String(aValue).localeCompare(String(bValue), undefined, {
numeric: true,
sensitivity: "base"
});
}
return direction === "asc" ? result : -result;
}
function tableDefaultSort(table) {
const defaultSort = table?.defaultSort;
if (!defaultSort || !table.columns.some((column) => column.field === defaultSort.field))
return null;
return {
field: defaultSort.field,
direction: defaultSort.direction === "desc" ? "desc" : "asc"
};
}
function MetricBadge({ metric, row }) {
const value = row[metric.field];
const renderedValue = formatMetricValue(value, metric);
if (!renderedValue)
return null;
const direction = metricMovementDirection(value, metric.signed === true);
return (<Badge className={`metric-badge ${direction ?? "neutral"}`}>
<span className="metric-badge-label">{metric.label}</span>
<span className="metric-badge-value">{renderedValue}</span>
</Badge>);
}
function KpiCard({ action, card, className = "", filters, id, selectedFilters, snapshot }) {
const metrics = cardMetrics(card);
const [primaryMetric, ...supportingMetrics] = metrics;
const rows = filterRowsForDataset(getRows(snapshot, card.dataset), card.dataset, filters, selectedFilters, metrics.map((metric) => metric.field));
const row = rows.find((candidate) => rowMatchesFilter(candidate, card.filter)) ?? {};
const label = cardLabel(card);
const description = card.description?.trim();
return (<section className={`kpi-card ${className}`.trim()} data-artifact-id={id} data-artifact-kind="card" id={id}>
{action}
<div className="kpi-label-row">
<div className="kpi-label">{label}</div>
{description ? <MetricDescriptionPopover description={description} label={label}/> : null}
</div>
<div className="kpi-value">{primaryMetric ? formatValue(row[primaryMetric.field], primaryMetric.format) : "—"}</div>
{supportingMetrics.length ? (<div className="metric-badge-row">
{supportingMetrics.map((metric) => (<MetricBadge key={`${metric.field}:${metric.label}`} metric={metric} row={row}/>))}
</div>) : null}
</section>);
}
function useMeasuredElementSize() {
const ref = useRef(null);
const [size, setSize] = useState({ height: 0, width: 0 });
useEffect(() => {
const element = ref.current;
if (!element)
return;
let frame = 0;
const updateSize = () => {
window.cancelAnimationFrame(frame);
frame = window.requestAnimationFrame(() => {
const rect = element.getBoundingClientRect();
setSize({
height: Math.floor(rect.height),
width: Math.floor(rect.width)
});
});
};
updateSize();
const observer = new ResizeObserver(updateSize);
observer.observe(element);
window.addEventListener("resize", updateSize);
return () => {
window.cancelAnimationFrame(frame);
observer.disconnect();
window.removeEventListener("resize", updateSize);
};
}, []);
return [ref, size];
}
const MENU_CLOSE_ANIMATION_MS = 100;
const NARROW_FIXED_MENU_QUERY = "(max-width: 560px)";
function useDashboardMenu(isOpen, onOpenChange) {
const menuButtonRef = useRef(null);
const menuRef = useRef(null);
const isOpenRef = useRef(isOpen);
const [shouldRenderMenu, setShouldRenderMenu] = useState(isOpen);
const [menuMotionClass, setMenuMotionClass] = useState("opening");
const [fixedMenuStyle, setFixedMenuStyle] = useState(undefined);
useEffect(() => {
isOpenRef.current = isOpen;
}, [isOpen]);
const updateFixedMenuStyle = useCallback(() => {
if (typeof window === "undefined") {
return;
}
if (!window.matchMedia(NARROW_FIXED_MENU_QUERY).matches) {
setFixedMenuStyle(undefined);
return;
}
const anchor = menuButtonRef.current?.getBoundingClientRect();
if (!anchor) {
return;
}
const menuSurface = menuRef.current?.matches?.('[role="menu"]')
? menuRef.current
: menuRef.current?.querySelector?.('[role="menu"]');
const margin = 12;
const gap = 6;
const surfaceHeight = menuSurface?.getBoundingClientRect?.().height ?? 0;
let top = anchor.bottom + gap;
if (surfaceHeight && top + surfaceHeight > window.innerHeight - margin && anchor.top - surfaceHeight - gap >= margin) {
top = anchor.top - surfaceHeight - gap;
}
else if (surfaceHeight) {
top = clamp(top, margin, window.innerHeight - margin - surfaceHeight);
}
else {
top = clamp(top, margin, window.innerHeight - margin);
}
setFixedMenuStyle((current) => {
if (current?.top === top)
return current;
return { top };
});
}, []);
function menuItems() {
return Array.from(menuRef.current?.querySelectorAll('[role="menuitem"], [role="menuitemradio"]') ?? []).filter((item) => !item.disabled);
}
function focusMenuItem(position) {
window.requestAnimationFrame(() => {
const items = menuItems();
if (!items.length)
return;
const index = position === "first"
? 0
: position === "last"
? items.length - 1
: Math.max(0, Math.min(items.length - 1, position));
items[index]?.focus();
});
}
function openMenu() {
setShouldRenderMenu(true);
setMenuMotionClass("opening");
onOpenChange(true);
}
function closeMenu() {
onOpenChange(false);
}
function setMenuOpen(nextIsOpen) {
if (nextIsOpen) {
openMenu();
return;
}
closeMenu();
}
function toggleMenu() {
const nextIsOpen = !isOpenRef.current;
setMenuOpen(nextIsOpen);
return nextIsOpen;
}
useEffect(() => {
if (isOpen) {
setShouldRenderMenu(true);
setMenuMotionClass("opening");
return;
}
if (!shouldRenderMenu)
return;
setMenuMotionClass("closing");
const closeTimer = window.setTimeout(() => {
setShouldRenderMenu(false);
}, MENU_CLOSE_ANIMATION_MS);
return () => {
window.clearTimeout(closeTimer);
};
}, [isOpen, shouldRenderMenu]);
useLayoutEffect(() => {
if (!shouldRenderMenu) {
setFixedMenuStyle(undefined);
return;
}
updateFixedMenuStyle();
const frame = window.requestAnimationFrame(updateFixedMenuStyle);
window.addEventListener("resize", updateFixedMenuStyle);
window.addEventListener("scroll", updateFixedMenuStyle, true);
return () => {
window.cancelAnimationFrame(frame);
window.removeEventListener("resize", updateFixedMenuStyle);
window.removeEventListener("scroll", updateFixedMenuStyle, true);
};
}, [shouldRenderMenu, updateFixedMenuStyle]);
useEffect(() => {
if (!isOpen)
return;
function handlePointerDown(event) {
const target = event.target;
if (!menuRef.current?.contains(target) && !menuButtonRef.current?.contains(target)) {
closeMenu();
}
}
function handleKeyDown(event) {
if (event.key === "Escape") {
closeMenu();
menuButtonRef.current?.focus();
}
}
document.addEventListener("pointerdown", handlePointerDown);
document.addEventListener("keydown", handleKeyDown);
return () => {
document.removeEventListener("pointerdown", handlePointerDown);
document.removeEventListener("keydown", handleKeyDown);
};
}, [isOpen, onOpenChange]);
return {
closeMenu,
fixedMenuStyle,
handleMenuButtonKeyDown: (event) => {
if (event.key === "ArrowDown" || event.key === "ArrowUp") {
event.preventDefault();
openMenu();
focusMenuItem(event.key === "ArrowDown" ? "first" : "last");
}
},
handleMenuKeyDown: (event) => {
if (event.key !== "ArrowDown" &&
event.key !== "ArrowUp" &&
event.key !== "Home" &&
event.key !== "End" &&
event.key !== "Escape") {
return;
}
event.preventDefault();
if (event.key === "Escape") {
closeMenu();
menuButtonRef.current?.focus();
return;
}
const items = menuItems();
if (!items.length)
return;
const activeIndex = items.findIndex((item) => item === document.activeElement);
if (event.key === "Home") {
focusMenuItem("first");
return;
}
if (event.key === "End") {
focusMenuItem("last");
return;
}
const offset = event.key === "ArrowDown" ? 1 : -1;
const nextIndex = activeIndex === -1
? (event.key === "ArrowDown" ? 0 : items.length - 1)
: (activeIndex + offset + items.length) % items.length;
focusMenuItem(nextIndex);
},
menuButtonRef,
menuMotionClass,
menuRef,
toggleMenu,
shouldRenderMenu
};
}
function FilterMenu({ label, onChange, options, value }) {
const [isOpen, setIsOpen] = useState(false);
const { closeMenu, handleMenuButtonKeyDown, handleMenuKeyDown, menuButtonRef, menuMotionClass, menuRef, toggleMenu, shouldRenderMenu } = useDashboardMenu(isOpen, setIsOpen);
const selectedOption = options.find((option) => option.value === value) ?? options[0];
return (<div className="filter-menu" ref={menuRef}>
<button aria-expanded={isOpen} aria-haspopup="menu" className="filter-menu-button" onClick={toggleMenu} onKeyDown={handleMenuButtonKeyDown} ref={menuButtonRef} type="button">
<span className="filter-menu-label">{label}</span>
<span className="filter-menu-value">{selectedOption?.label ?? value}</span>
<ChevronDown aria-hidden="true" size={14} strokeWidth={2}/>
</button>
{shouldRenderMenu ? (<div className={`filter-menu-list menu-surface ${menuMotionClass}`} onKeyDown={handleMenuKeyDown} role="menu">
{options.map((option) => {
const isSelected = option.value === value;
return (<button aria-checked={isSelected} className="filter-menu-item" key={option.value} onClick={() => {
onChange(option.value);
closeMenu();
}} role="menuitemradio" type="button">
<span>{option.label}</span>
{isSelected ? <Check aria-hidden="true" size={14} strokeWidth={2}/> : null}
</button>);
})}
</div>) : null}
</div>);
}
function FilterToolbar({ filters, snapshot, selectedFilters, onChange }) {
if (!filters.length)
return null;
return (<div className="filter-toolbar" aria-label="Analytics filters">
<div className="filter-group">
{filters.map((filter) => {
const options = Array.from(new Set(getRows(snapshot, filter.dataset).map((row) => String(row[filter.field] ?? ""))))
.filter(Boolean)
.sort();
const filterOptions = [
...(filter.includeAll === false ? [] : [{ label: "All", value: "all" }]),
...options.map((option) => ({ label: option, value: option }))
];
const value = selectedFilters[filter.id] ?? filter.defaultValue ?? "all";
return (<FilterMenu key={filter.id} label={filter.label} onChange={(nextValue) => onChange({ ...selectedFilters, [filter.id]: nextValue })} options={filterOptions} value={value}/>);
})}
</div>
</div>);
}
function PanelHeader({ action, children, title, subtitle, titleRowClassName, titleRowProps }) {
return (<div className="panel-header">
<div {...titleRowProps} className={`panel-title-row ${titleRowClassName ?? ""} ${titleRowProps?.className ?? ""}`.trim()}>
{children ?? (<div>
<h2>{title}</h2>
{subtitle ? <p>{subtitle}</p> : null}
</div>)}
</div>
{action}
</div>);
}
function EditablePageTitle({ ariaLabel, isEditMode, onChange, onRequestEditMode, placeholder, readOnly = false, title }) {
const [isEditing, setIsEditing] = useState(false);
const displayTitle = title.trim() ? title : placeholder;
function startEditing() {
if (readOnly)
return;
if (!isEditMode)
onRequestEditMode();
setIsEditing(true);
}
if (readOnly) {
return (<div className="page-title-edit-target page-title-readonly">
<h1>{displayTitle}</h1>
</div>);
}
if (isEditing) {
return (<input aria-label={ariaLabel} autoFocus className="page-title-editor viz-card__no-drag" onBlur={() => setIsEditing(false)} onChange={(event) => onChange(event.currentTarget.value)} onKeyDown={(event) => {
if (event.key === "Enter") {
event.preventDefault();
event.currentTarget.blur();
}
}} placeholder={placeholder} size={Math.max(1, displayTitle.length)} type="text" value={title}/>);
}
return (<div aria-label={ariaLabel} className="page-title-edit-target viz-card__no-drag" data-page-title-edit-mode={isEditMode ? "true" : "false"} onClick={() => {
if (isEditMode)
startEditing();
}} onDoubleClick={startEditing} onKeyDown={(event) => {
if (event.key === "Enter" || event.key === " ") {
event.preventDefault();
startEditing();
}
}} role="button" tabIndex={0}>
<h1>{displayTitle}</h1>
</div>);
}
function composeHeaderMarkdown(title, description) {
return description?.trim() ? `## ${title}\n\n${description}` : `## ${title}`;
}
function composeVisualHeaderMarkdown(title, description, headerMarkdown) {
if (headerMarkdown?.trim()) {
return headerMarkdown;
}
return composeHeaderMarkdown(title, description);
}
function composePageTitle(manifest) {
const fallbackTitle = manifest?.surface === "report" ? "Data Analytics Report" : "Data Analytics Dashboard";
return manifest?.title?.trim() || fallbackTitle;
}
function composeChartHeaderMarkdown(chart) {
return composeVisualHeaderMarkdown(chart.title, chart.showDescription ? chart.subtitle : undefined, chart.headerMarkdown);
}
function composeTableHeaderMarkdown(table) {
return composeVisualHeaderMarkdown(table.title, table.showDescription ? table.subtitle : undefined, table.headerMarkdown);
}
function reportBlockBodyMarkdown(block) {
return typeof block.body === "string" ? block.body : "";
}
function visibleString(value) {
return typeof value === "string" && value.trim() ? value : undefined;
}
function composeBlockMarkdown(block, textOverride) {
if (visibleString(textOverride?.bodyMarkdown))
return textOverride.bodyMarkdown;
return reportBlockBodyMarkdown(block);
}
function composeBlockHtml(block, textOverride) {
if (visibleString(textOverride?.html))
return textOverride.html;
return typeof block.body === "string" ? block.body : "";
}
const REPORT_HTML_BLOCK_CSP = [
"default-src 'none'",
"base-uri 'none'",
"connect-src 'none'",
"font-src data:",
"form-action 'none'",
"frame-src 'none'",
"img-src data: blob:",
"media-src data: blob:",
"object-src 'none'",
"script-src 'none'",
"style-src 'unsafe-inline'",
].join("; ");
function sandboxedReportHtml(html) {
return `<!doctype html><html><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="${REPORT_HTML_BLOCK_CSP}"><meta name="viewport" content="width=device-width, initial-scale=1"><base target="_blank"><style>html,body{margin:0;background:transparent;}img,svg,canvas,video{max-width:100%;height:auto;}</style></head><body>${html}</body></html>`;
}
function measureHtmlFrameHeight(frame) {
const documentElement = frame?.contentDocument?.documentElement;
const body = frame?.contentDocument?.body;
if (!documentElement && !body)
return 0;
return Math.ceil(Math.max(documentElement?.scrollHeight ?? 0, body?.scrollHeight ?? 0));
}
function markdownPlainText(markdown) {
return markdown
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
function ChartBody({ accessIssue, chart, filters, isFullscreen = false, selectedFilters, snapshot }) {
const [visibleSeries, setVisibleSeries] = useState();
const [chartBodyRef, chartBodySize] = useMeasuredElementSize();
const rawRows = filterRowsForDataset(getRows(snapshot, chart.dataset), chart.dataset, filters, selectedFilters, chartUsedFields(chart));
if (accessIssue) {
return (<div className="permission-card">
<div className="permission-card-title">Missing data access</div>
<p>{accessIssue.message}</p>
{accessIssue.actionHref ? (<a href={accessIssue.actionHref} rel="noreferrer" target="_blank">
{accessIssue.actionLabel ?? "Request access"}
</a>) : accessIssue.actionLabel ? (<span>{accessIssue.actionLabel}</span>) : null}
</div>);
}
if (!rawRows.length) {
return <div className="empty-state">No rows match the selected filters.</div>;
}
return (<div className="chart-body-measure" ref={chartBodyRef}>
<ChartRenderer chart={chart} height={isFullscreen ? CHART_FULLSCREEN_HEIGHT : undefined} onVisibleSeriesChange={setVisibleSeries} rows={rawRows} surface={isFullscreen ? "explorer" : "card"} visibleSeries={visibleSeries} width={chartBodySize.width || undefined}/>
</div>);
}
function VizCard({ accessIssue, capabilities, canEditChartSpec = true, chart, children, isEditMode, isMenuOpen, layout, onCopyResult, onDeleteBlock, onRequestEditMode, onTextChange, onMenuOpenChange, onModalOpen, textOverride }) {
const cardRef = useRef(null);
const { closeMenu, fixedMenuStyle, handleMenuButtonKeyDown, handleMenuKeyDown, menuButtonRef, menuMotionClass, menuRef, toggleMenu, shouldRenderMenu } = useDashboardMenu(isMenuOpen, onMenuOpenChange);
const [imageExportState, setImageExportState] = useState({ status: "idle" });
const { getPreparedImageBlob, preparedImageExportStatus, prepareImageExport, resetPreparedImageExport } = usePreparedImageExport(cardRef);
const fallbackHeaderMarkdown = textOverride?.title || textOverride?.subtitle
? composeHeaderMarkdown(textOverride.title ?? chart.title, textOverride.subtitle ?? chart.subtitle)
: composeChartHeaderMarkdown(chart);
const displayHeaderMarkdown = textOverride?.headerMarkdown ?? fallbackHeaderMarkdown;
const displayChart = {
...chart,
subtitle: undefined,
title: markdownFirstLine(displayHeaderMarkdown, chart.title)
};
function prepareImageExportQuietly(force = false) {
if (accessIssue || !capabilities.canCopyImage || !shouldOfferImageClipboardCopy())
return;
const prepared = prepareImageExport({ force });
if (prepared)
void prepared.promise.catch(() => undefined);
}
async function handleCopyAsImage() {
if (!cardRef.current)
return;
setImageExportState({ status: "loading" });
try {
const copyResult = await copyElementAsImage(cardRef.current, getPreparedImageBlob());
setImageExportState({ status: "idle" });
resetPreparedImageExport();
onCopyResult(imageCopySuccessMessage("Copied widget as image.", copyResult));
}
catch (error) {
setImageExportState({
error: error instanceof Error ? error.message : "Failed to copy image.",
status: "error"
});
onCopyResult(error instanceof Error ? error.message : "Failed to copy image.", true);
}
}
const menuItem = (label, icon, onClick, disabled = false, tone = "default", onPrepare) => (<button className={`viz-card-menu-item ${tone === "danger" ? "viz-card-menu-item-danger" : ""}`.trim()} data-artifact-action={label === "View data source" ? "view-source" : undefined} disabled={disabled} key={label} onFocus={onPrepare} onClick={() => {
void onClick();
closeMenu();
}} onPointerEnter={onPrepare} role="menuitem" type="button">
<span aria-hidden="true" className="viz-card-menu-icon">
{icon}
</span>
<span>{label}</span>
</button>);
return (<section className={`panel chart-panel viz-card ${accessIssue ? "has-permission-issue" : ""}`} data-artifact-id={chart.id} data-artifact-kind="chart" id={chart.id} ref={cardRef}>
<PanelHeader action={<div className="viz-card-actions" data-image-export-exclude="true" ref={menuRef}>
<button aria-expanded={isMenuOpen} aria-label={`Open options for ${displayChart.title}`} className="viz-card-menu-button viz-card__no-drag" data-artifact-action="open-options" data-artifact-has-source={chart.sourceId || chart.source ? "true" : "false"} data-artifact-id={chart.id} data-artifact-kind="chart" onClick={(event) => {
event.stopPropagation();
const nextIsMenuOpen = toggleMenu();
if (nextIsMenuOpen) {
prepareImageExportQuietly(true);
}
else {
resetPreparedImageExport();
}
}} onFocus={() => prepareImageExportQuietly()} onKeyDown={handleMenuButtonKeyDown} onPointerEnter={() => prepareImageExportQuietly()} ref={menuButtonRef} type="button">
<Ellipsis aria-hidden="true" size={18} strokeWidth={2}/>
</button>
{shouldRenderMenu ? (<div className={`viz-card-menu viz-card__no-drag menu-surface ${menuMotionClass}`} onKeyDown={handleMenuKeyDown} role="menu" style={fixedMenuStyle}>
{menuItem(canEditChartSpec ? "Edit chart" : "Explore chart", <ChartNoAxesCombined size={18} strokeWidth={2}/>, () => onModalOpen({ chart: displayChart, kind: "fullscreen" }))}
{menuItem("View data source", <Database size={18} strokeWidth={2}/>, () => onModalOpen({ chart: displayChart, kind: "source" }))}
{capabilities.canCopyImage && shouldOfferImageClipboardCopy()
? menuItem("Copy as image", <Camera size={18} strokeWidth={2}/>, handleCopyAsImage, Boolean(accessIssue) ||
imageExportState.status === "loading" ||
preparedImageExportStatus === "pending", "default", prepareImageExportQuietly)
: null}
{onDeleteBlock ? menuItem("Delete", <Trash2 size={18} strokeWidth={2}/>, onDeleteBlock, false, "danger") : null}
</div>) : null}
</div>} subtitle={displayChart.subtitle} title={displayChart.title} titleRowClassName="viz-card__drag-handle">
<RichMarkdown ariaLabel={`Edit markdown header for ${chart.title}`} className="editable-cell-header" isEditMode={isEditMode} markdown={displayHeaderMarkdown} onMarkdownChange={(nextMarkdown) => onTextChange(chart.id, { headerMarkdown: nextMarkdown })} onRequestEditMode={onRequestEditMode} placeholder={composeChartHeaderMarkdown(chart)} variant="cellHeader"/>
</PanelHeader>
{children}
</section>);
}
function AccessIssueStrip({ issues }) {
if (!issues.length)
return null;
return (<section className="access-issue-strip" aria-label="Data access issues">
<div>
<strong>{issues.length === 1 ? "Data access blocker" : "Data access blockers"}</strong>
<p>Some report data could not load because the source query could not complete.</p>
</div>
<ul>
{issues.map((issue) => (<li key={issue.id}>
<span>{issue.scope ?? issue.dataset ?? issue.sourceId ?? issue.id}</span>
<span>{issue.message}</span>
{issue.actionHref ? (<a href={issue.actionHref} rel="noreferrer" target="_blank">
{issue.actionLabel ?? "Request access"}
</a>) : null}
</li>))}
</ul>
</section>);
}
const SQL_KEYWORDS = new Set([
"and",
"as",
"asc",
"by",
"case",
"desc",
"distinct",
"else",
"end",
"from",
"group",
"in",
"is",
"join",
"left",
"like",
"max",
"min",
"not",
"null",
"on",
"or",
"order",
"over",
"partition",
"right",
"select",
"sum",
"then",
"when",
"where",
"with"
]);
const SQL_FUNCTIONS = new Set([
"avg",
"cast",
"coalesce",
"concat",
"count",
"current_date",
"date_trunc",
"dateadd",
"date_add",
"round",
"nullif"
]);
const SQL_TOKEN_PATTERN = /(--[^\n]*|'(?:''|[^'])*'|<>|!=|<=|>=|\b\d+(?:\.\d+)?\b|\b[a-zA-Z_][a-zA-Z0-9_]*\b|[(),.;=*+\-/%<>])/g;
const SQL_FORMAT_LINE_STARTERS = new Set([
"from",
"group",
"having",
"limit",
"order",
"select",
"union",
"where",
"with"
]);
const SQL_JOIN_MODIFIERS = new Set([
"cross",
"full",
"inner",
"join",
"left",
"outer",
"right"
]);
function sqlFormatTokens(sql) {
const tokens = [];
let cursor = 0;
for (const match of sql.matchAll(SQL_TOKEN_PATTERN)) {
const token = match[0];
const index = match.index ?? 0;
const rawGap = sql.slice(cursor, index).trim();
if (rawGap)
tokens.push(...rawGap.split(/\s+/));
tokens.push(token);
cursor = index + token.length;
}
const tail = sql.slice(cursor).trim();
if (tail)
tokens.push(...tail.split(/\s+/));
return tokens;
}
function isSqlWord(token) {
return /^[a-zA-Z_][a-zA-Z0-9_]*$/.test(token);
}
function formatSqlForDisplay(sql) {
const tokens = sqlFormatTokens(sql.trim());
if (!tokens.length)
return "";
const lines = [];
let current = "";
let indent = 0;
const contextStack = [];
let previousToken = "";
function currentIndent(level = indent) {
return "  ".repeat(Math.max(0, level));
}
function pushLine(nextIndent = indent) {
const text = current.trimEnd();
if (text.trim())
lines.push(text);
current = currentIndent(nextIndent);
}
function append(token, { tight = false } = {}) {
if (!current)
current = currentIndent();
const trimmed = current.trimEnd();
const needsSpace = !tight &&
trimmed &&
!trimmed.endsWith("(") &&
!trimmed.endsWith(".") &&
token !== "." &&
token !== "," &&
token !== ")" &&
token !== ";";
current = `${trimmed}${needsSpace ? " " : ""}${token}`;
previousToken = token;
}
for (let index = 0; index < tokens.length; index += 1) {
const token = tokens[index];
const lower = token.toLowerCase();
const previousLower = previousToken.toLowerCase();
const nextLower = tokens[index + 1]?.toLowerCase?.() ?? "";
if (token.startsWith("--")) {
if (current.trim())
pushLine();
append(token);
pushLine();
continue;
}
if (SQL_FORMAT_LINE_STARTERS.has(lower)) {
if (current.trim() && !current.trimEnd().endsWith("("))
pushLine();
append(lower.toUpperCase());
continue;
}
if (SQL_JOIN_MODIFIERS.has(lower)) {
if (!(lower === "join" && SQL_JOIN_MODIFIERS.has(previousLower)) && current.trim())
pushLine();
append(lower.toUpperCase());
continue;
}
if (token === "(") {
const functionCall = SQL_FUNCTIONS.has(previousLower) ||
(isSqlWord(previousToken) && !SQL_KEYWORDS.has(previousLower) && previousLower !== "as");
append(token, { tight: functionCall });
contextStack.push(functionCall ? "function" : "group");
if (!functionCall && (nextLower === "select" || previousLower === "as")) {
indent += 1;
pushLine();
}
else if (!functionCall) {
indent += 1;
}
continue;
}
if (token === ")") {
const context = contextStack.pop();
const nextIndent = Math.max(0, indent - 1);
if (context !== "function" && current.trim() && current.trim() !== currentIndent().trim())
pushLine(nextIndent);
indent = nextIndent;
append(token, { tight: true });
continue;
}
if (token === ",") {
append(token, { tight: true });
if (contextStack[contextStack.length - 1] !== "function")
pushLine();
continue;
}
if (token === ".") {
append(token, { tight: true });
continue;
}
if (token === ";") {
append(token, { tight: true });
pushLine();
continue;
}
append(SQL_KEYWORDS.has(lower) || SQL_FUNCTIONS.has(lower) ? lower.toUpperCase() : token);
}
if (current.trim())
pushLine();
return lines.join("\n");
}
function highlightSql(sql) {
const nodes = [];
let cursor = 0;
for (const match of sql.matchAll(SQL_TOKEN_PATTERN)) {
const token = match[0];
const index = match.index ?? 0;
if (index > cursor) {
nodes.push(sql.slice(cursor, index));
}
const lower = token.toLowerCase();
let className = "sql-token";
if (token.startsWith("--")) {
className += " comment";
}
else if (token.startsWith("'")) {
className += " string";
}
else if (/^\d/.test(token)) {
className += " number";
}
else if (SQL_KEYWORDS.has(lower)) {
className += " keyword";
}
else if (SQL_FUNCTIONS.has(lower)) {
className += " function";
}
else if (/^[(),.;=*+\-/%]$/.test(token)) {
className += " punctuation";
}
else {
className += " identifier";
}
nodes.push(<span className={className} key={`${index}-${token}`}>
{token}
</span>);
cursor = index + token.length;
}
if (cursor < sql.length) {
nodes.push(sql.slice(cursor));
}
return nodes;
}
const SOURCE_FETCH_TIMEOUT_MS = 10000;
function Tabs({ ariaLabel, onSelect, selectedKey, tabs }) {
const listRef = useRef(null);
const indicatorRef = useRef(null);
const updateIndicator = useCallback(() => {
const list = listRef.current;
const indicator = indicatorRef.current;
const activeTab = list?.querySelector('.source-modal-tab[aria-selected="true"]');
if (!(list instanceof HTMLElement) || !(activeTab instanceof HTMLElement) || !(indicator instanceof HTMLElement))
return;
const listRect = list.getBoundingClientRect();
const tabRect = activeTab.getBoundingClientRect();
indicator.style.width = `${tabRect.width}px`;
indicator.style.transform = `translate3d(${tabRect.left - listRect.left + list.scrollLeft}px, 0, 0)`;
indicator.dataset.ready = "true";
}, [selectedKey]);
useLayoutEffect(() => {
updateIndicator();
const list = listRef.current;
if (!(list instanceof HTMLElement) || typeof ResizeObserver !== "function")
return undefined;
const observer = new ResizeObserver(updateIndicator);
observer.observe(list);
list.querySelectorAll(".source-modal-tab").forEach((tab) => observer.observe(tab));
return () => observer.disconnect();
}, [tabs, updateIndicator]);
function handleKeyDown(event) {
const currentIndex = tabs.findIndex((tab) => tab.id === selectedKey);
let nextIndex = currentIndex;
if (event.key === "ArrowRight")
nextIndex = (currentIndex + 1) % tabs.length;
else if (event.key === "ArrowLeft")
nextIndex = (currentIndex - 1 + tabs.length) % tabs.length;
else if (event.key === "Home")
nextIndex = 0;
else if (event.key === "End")
nextIndex = tabs.length - 1;
else
return;
event.preventDefault();
const nextTab = tabs[nextIndex];
if (!nextTab)
return;
onSelect(nextTab.id);
window.requestAnimationFrame(() => document.getElementById(nextTab.tabId)?.focus());
}
return (<div aria-label={ariaLabel} aria-orientation="horizontal" className="source-modal-tabs" onKeyDown={handleKeyDown} ref={listRef} role="tablist">
{tabs.map((tab) => {
const isSelected = selectedKey === tab.id;
return (<div className="source-modal-tab-item" key={tab.id}>
<button aria-controls={tab.panelId} aria-pressed={isSelected} aria-selected={isSelected} className="source-modal-tab" id={tab.tabId} onClick={() => onSelect(tab.id)} role="tab" tabIndex={isSelected ? 0 : -1} type="button">
{tab.label}
</button>
</div>);
})}
<span aria-hidden="true" className="source-modal-tab-indicator" ref={indicatorRef}/>
</div>);
}
function DataSourceDetails({ children, details, environment, itemLabel, itemType, source, sourceQuery }) {
const [activeTab, setActiveTab] = useState("overview");
const tabId = useId();
const tabs = [
{ id: "overview", label: "Overview", panelId: `${tabId}-overview-panel`, tabId: `${tabId}-overview-tab` },
{ id: "data", label: "Data preview", panelId: `${tabId}-data-panel`, tabId: `${tabId}-data-tab` },
{ id: "sql", label: "SQL query", panelId: `${tabId}-sql-panel`, tabId: `${tabId}-sql-tab` }
];
return (<div className="source-modal-content">
<Tabs ariaLabel="Data source sections" onSelect={setActiveTab} selectedKey={activeTab} tabs={tabs}/>
<div className="source-modal-body">
{activeTab === "overview" ? (<section aria-labelledby={`${tabId}-overview-tab`} className="source-modal-tab-panel source-overview" id={`${tabId}-overview-panel`} role="tabpanel">
<div className="source-details-layout">
<dl className="source-details-summary">
<div>
<dt>{itemType}</dt>
<dd>{itemLabel}</dd>
</div>
<div>
<dt>Dataset</dt>
<dd>{sourceMetadataValue(details.dataset)}</dd>
</div>
<div>
<dt>Data snapshot</dt>
<dd>{sourceSnapshotDate(details.snapshot)}</dd>
</div>
</dl>
<dl className="source-details-stack">
<div>
<dt>Tables used</dt>
<dd>{sourceMetadataChips(details.tables)}</dd>
</div>
<div>
<dt>Filters</dt>
<dd>{sourceMetadataChips(details.filters)}</dd>
</div>
</dl>
<div className="source-metric-definitions">
<SourceDataTable columns={SOURCE_METRIC_DEFINITION_COLUMNS} dataset="__source_metric_definitions" density="spacious" fillAvailableWidth rows={metricDefinitionRows(details.metricDefinitions)}/>
</div>
</div>
</section>) : null}
{activeTab === "data" ? (<section aria-labelledby={`${tabId}-data-tab`} className="source-modal-tab-panel source-data" id={`${tabId}-data-panel`} role="tabpanel">
{children}
</section>) : null}
{activeTab === "sql" ? (<section aria-labelledby={`${tabId}-sql-tab`} className="source-modal-tab-panel source-sql" id={`${tabId}-sql-panel`} role="tabpanel">
<SourceQueryBlock environment={environment} source={source} sourceQuery={sourceQuery}/>
</section>) : null}
</div>
</div>);
}
function SourceQueryBlock({ environment = MCP_ARTIFACT_READER_ENVIRONMENT, source, sourceQuery }) {
const [sourceContent, setSourceContent] = useState({ status: "idle" });
const [copyStatus, setCopyStatus] = useState("idle");
const codeRef = useRef(null);
const inlineSourceText = queryTextFromSourceQuery(sourceQueryFromSourceSpec(source)) || queryTextFromSourceQuery(sourceQuery) || "";
const displaySourceText = sourceContent.status === "loaded" ? formatSqlForDisplay(sourceContent.text) : "";
useEffect(() => {
if (inlineSourceText) {
setSourceContent({ status: "loaded", text: inlineSourceText });
return;
}
let cancelled = false;
if (typeof environment.getSourceText === "function") {
setSourceContent({ status: "loading" });
Promise.resolve(environment.getSourceText(source))
.then((text) => {
if (cancelled)
return;
if (typeof text === "string" && text.trim()) {
setSourceContent({ status: "loaded", text });
}
else {
setSourceContent({ status: "unavailable" });
}
})
.catch((error) => {
if (!cancelled) {
setSourceContent({
error: error instanceof Error ? error.message : "Failed to load source",
status: "error"
});
}
});
return () => {
cancelled = true;
};
}
if (!source?.path) {
setSourceContent({ status: "idle" });
return;
}
if (environment.capabilities?.fetchSourceText === false) {
setSourceContent({ status: "unavailable" });
return;
}
setSourceContent({ status: "loading" });
loadSourceText(source.path, SOURCE_FETCH_TIMEOUT_MS)
.then((text) => {
if (!cancelled) {
setSourceContent(typeof text === "string" && text.trim()
? { status: "loaded", text }
: { status: "unavailable" });
}
})
.catch((error) => {
if (!cancelled) {
const isAbort = error instanceof Error && error.name === "AbortError";
setSourceContent({
error: isAbort
? "Source request timed out. Refresh the app and try again."
: error instanceof Error
? error.message
: "Failed to load source",
status: "error"
});
}
});
return () => {
cancelled = true;
};
}, [environment, inlineSourceText, source, source?.path]);
useEffect(() => {
if (copyStatus === "idle")
return;
const timeout = window.setTimeout(() => setCopyStatus("idle"), 1800);
return () => window.clearTimeout(timeout);
}, [copyStatus]);
async function handleCopyQuery(text) {
try {
await copyTextToClipboard(text);
setCopyStatus("copied");
}
catch {
setCopyStatus("blocked");
}
}
if (sourceContent.status === "loading")
return <>Loading source...</>;
if (sourceContent.status === "error") {
return <span className="source-error">{sourceContent.error}</span>;
}
if (sourceContent.status === "unavailable") {
return <>Source text was not included in this portable artifact.</>;
}
if (sourceContent.status === "loaded") {
return (<div className="source-query-shell">
{source?.path || source?.href || source?.label || sourceQuery?.id || sourceQuery?.engine ? (<div className="source-query-meta">
<span>
{source?.href ? (<a href={source.href} rel="noreferrer" target="_blank">
{source.path ?? source.label}
</a>) : (source?.path ?? source?.label ?? sourceQuery?.id ?? sourceQuery?.engine)}
</span>
<button aria-live="polite" className="source-query-copy" onClick={() => void handleCopyQuery(displaySourceText || sourceContent.text)} type="button">
<Copy aria-hidden="true" size={14} strokeWidth={2}/>
{copyStatus === "copied"
? "Copied"
: copyStatus === "blocked"
? "Copy failed"
: "Copy query"}
</button>
</div>) : null}
<pre className="source-query">
<code ref={codeRef}>{highlightSql(displaySourceText || sourceContent.text)}</code>
</pre>
</div>);
}
return <>No source query file mapped.</>;
}
function useModalScrollLock(enabled) {
useEffect(() => {
if (!enabled)
return undefined;
const previousOverflow = document.body.style.overflow;
const previousOverscrollBehavior = document.body.style.overscrollBehavior;
document.body.style.overflow = "hidden";
document.body.style.overscrollBehavior = "none";
return () => {
document.body.style.overflow = previousOverflow;
document.body.style.overscrollBehavior = previousOverscrollBehavior;
};
}, [enabled]);
}
function sourcePreviewColumns(rows, columns = []) {
if (columns.length)
return columns;
const fields = [];
const seen = new Set();
for (const row of rows) {
for (const field of Object.keys(row)) {
if (!seen.has(field)) {
seen.add(field);
fields.push(field);
}
}
}
return fields.map((field) => ({ field, label: field }));
}
function SourceDataTable({ columns = [], dataset, density = "dense", fillAvailableWidth = true, pageSize = TABLE_CARD_PAGE_SIZE, rows = [] }) {
const previewRows = useMemo(() => asArray(rows).filter((row) => row && typeof row === "object"), [rows]);
const previewDataset = dataset ?? "__source_preview_rows";
const table = useMemo(() => ({
columns: sourcePreviewColumns(previewRows, columns),
dataset: previewDataset,
id: `source-preview-${previewDataset}`
}), [columns, previewDataset, previewRows]);
const snapshot = useMemo(() => ({ datasets: { [previewDataset]: previewRows } }), [previewDataset, previewRows]);
const [columnWidths, setColumnWidths] = useState({});
useEffect(() => {
setColumnWidths({});
}, [table.id]);
return (<div className="source-data-table">
<TableContent allowColumnResize={false} columnWidths={columnWidths} density={density} fillAvailableWidth={fillAvailableWidth} filters={EMPTY_FILTERS} onColumnWidthsChange={(_tableId, nextWidths) => setColumnWidths(nextWidths)} pageSize={pageSize} selectedFilters={{}} snapshot={snapshot} table={table}/>
</div>);
}
function querySourceForChart(chart, sources) {
const directSource = sourceForChart(chart, sources);
return (directSource ??
sources.find((source) => {
const label = source.label?.toLowerCase() ?? "";
const path = source.path?.toLowerCase() ?? "";
return path.endsWith(".sql") || label.includes("sql") || label.includes("quer");
}) ??
null);
}
function chartMetricsForBuildDetails(chart) {
const metrics = [];
const seen = new Set();
function addMetric(field, label) {
if (!field || seen.has(field))
return;
seen.add(field);
metrics.push({ field, label: label || field });
}
addMetric(chart.encodings?.y?.field, chart.encodings?.y?.label);
for (const field of chart.encodings?.y?.fields ?? []) {
addMetric(field, field);
}
return metrics;
}
function ChartSourceModalDialog({ activeFilters, chart, environment, manifest, onClose, rows = [], snapshot }) {
const dialogRef = useRef(null);
const source = querySourceForChart(chart, manifest?.sources ?? []);
const sourceQuery = sourceQueryFromSourceSpec(source);
const buildDetails = sourceBuildDetails({
activeFilters,
dataset: chart.dataset,
metrics: chartMetricsForBuildDetails(chart),
source,
sourceQuery,
snapshot
});
useModalScrollLock(true);
useEffect(() => {
const dialog = dialogRef.current;
if (dialog && !dialog.open) {
dialog.showModal();
}
}, []);
return (<dialog aria-labelledby="chart-source-modal-title" className="native-modal source-modal" data-artifact-dialog="source" data-artifact-item-id={chart.id} data-artifact-item-type="chart" onCancel={onClose} onClick={(event) => {
if (event.target === event.currentTarget) {
event.currentTarget.close();
}
}} onClose={onClose} ref={dialogRef}>
<section className="modal-panel source-modal-panel">
<div className="modal-header">
<div>
<h2 id="chart-source-modal-title">Data source</h2>
</div>
<button aria-label="Close data source" className="modal-close-button" onClick={() => dialogRef.current?.close()} type="button">
<X aria-hidden="true" size={20} strokeWidth={2}/>
</button>
</div>
<DataSourceDetails details={buildDetails} environment={environment} itemLabel={chart.title} itemType="Chart" source={source} sourceQuery={sourceQuery}>
<SourceDataTable dataset={chart.dataset} pageSize={SOURCE_DATA_PREVIEW_PAGE_SIZE} rows={rows}/>
</DataSourceDetails>
</section>
</dialog>);
}
function CardSourceModalDialog({ activeFilters, card, environment, filters = EMPTY_FILTERS, manifest, onClose, rows: providedRows, selectedFilters = {}, snapshot }) {
const dialogRef = useRef(null);
const metrics = cardMetrics(card);
const source = sourceForCard(card, manifest?.sources ?? []);
const sourceQuery = sourceQueryFromSourceSpec(source);
const rows = providedRows ?? filterRowsForDataset(getRows(snapshot, card.dataset), card.dataset, filters, selectedFilters, metrics.map((metric) => metric.field))
.filter((row) => rowMatchesFilter(row, card.filter));
const buildDetails = sourceBuildDetails({
activeFilters,
dataset: card.dataset,
metrics,
source,
sourceQuery,
snapshot
});
useModalScrollLock(true);
useEffect(() => {
const dialog = dialogRef.current;
if (dialog && !dialog.open) {
dialog.showModal();
}
}, []);
const label = cardLabel(card);
return (<dialog aria-labelledby="card-source-modal-title" className="native-modal source-modal" data-artifact-dialog="source" data-artifact-item-id={card.id} data-artifact-item-type="card" onCancel={onClose} onClick={(event) => {
if (event.target === event.currentTarget) {
event.currentTarget.close();
}
}} onClose={onClose} ref={dialogRef}>
<section className="modal-panel source-modal-panel">
<div className="modal-header">
<div>
<h2 id="card-source-modal-title">Data source</h2>
</div>
<button aria-label="Close data source" className="modal-close-button" onClick={() => dialogRef.current?.close()} type="button">
<X aria-hidden="true" size={20} strokeWidth={2}/>
</button>
</div>
<DataSourceDetails details={buildDetails} environment={environment} itemLabel={label} itemType="Metric" source={source} sourceQuery={sourceQuery}>
<SourceDataTable dataset={card.dataset} pageSize={SOURCE_DATA_PREVIEW_PAGE_SIZE} rows={rows}/>
</DataSourceDetails>
</section>
</dialog>);
}
function ChartDetailPage({ accessIssue, chart, environment, filters, manifest, onChartSpecChange, onClose, rows, selectedFilters, snapshot }) {
const dialogRef = useRef(null);
const iframeRef = useRef(null);
const pendingPostTimersRef = useRef([]);
const [widgetHtml, setWidgetHtml] = useState(null);
const [widgetError, setWidgetError] = useState(null);
const [sourceQueryText, setSourceQueryText] = useState(null);
const source = querySourceForChart(chart, manifest?.sources ?? []);
const canEditChart = typeof onChartSpecChange === "function";
const modalLabel = `${canEditChart ? "Edit" : "Explore"} ${chart.title}`;
const widgetInstanceId = `report-chart-detail-${chart.id}`;
const widgetPayload = useMemo(() => chartWidgetPayload(chart, rows, source, snapshot, sourceQueryText), [chart, rows, source, snapshot, sourceQueryText]);
const clearPendingPostTimers = useCallback(() => {
pendingPostTimersRef.current.forEach((timer) => window.clearTimeout(timer));
pendingPostTimersRef.current = [];
}, []);
const postWidgetPayload = useCallback(() => {
iframeRef.current?.contentWindow?.postMessage({
displayMode: "modal",
payload: widgetPayload,
targetWidgetInstanceId: widgetInstanceId
}, "*");
}, [widgetInstanceId, widgetPayload]);
const scheduleWidgetPayloadPosts = useCallback(() => {
clearPendingPostTimers();
pendingPostTimersRef.current = [0, 50, 150, 350].map((delay) => window.setTimeout(postWidgetPayload, delay));
}, [clearPendingPostTimers, postWidgetPayload]);
useEffect(() => {
const dialog = dialogRef.current;
if (dialog && !dialog.open) {
dialog.showModal();
}
}, []);
useEffect(() => {
let cancelled = false;
if (accessIssue) {
setWidgetHtml(null);
setWidgetError(null);
return () => {
cancelled = true;
};
}
setWidgetHtml(null);
setWidgetError(null);
void loadInlineChartWidgetHtml(widgetInstanceId)
.then((html) => {
if (!cancelled)
setWidgetHtml(html);
})
.catch((error) => {
if (!cancelled)
setWidgetError(error instanceof Error ? error.message : "Shared chart detail failed to load.");
});
return () => {
cancelled = true;
};
}, [accessIssue, widgetInstanceId]);
useEffect(() => {
let cancelled = false;
if (accessIssue) {
setSourceQueryText(null);
return () => {
cancelled = true;
};
}
const inlineSourceText = queryTextFromSourceQuery(sourceQueryFromSourceSpec(source));
if (inlineSourceText) {
setSourceQueryText(inlineSourceText);
return () => {
cancelled = true;
};
}
if (!source?.path) {
setSourceQueryText(null);
return () => {
cancelled = true;
};
}
setSourceQueryText(null);
void loadSourceText(source.path)
.then((text) => {
if (!cancelled)
setSourceQueryText(text?.trim() || null);
})
.catch(() => {
if (!cancelled)
setSourceQueryText(null);
});
return () => {
cancelled = true;
};
}, [accessIssue, source?.path, source?.query?.query]);
useEffect(() => {
if (!widgetHtml)
return;
scheduleWidgetPayloadPosts();
}, [scheduleWidgetPayloadPosts, widgetHtml]);
useEffect(() => clearPendingPostTimers, [clearPendingPostTimers]);
useEffect(() => {
function handleWidgetMessage(event) {
const data = event.data;
if (!data || typeof data !== "object")
return;
if (data.type === "datascience-chart-widget-display-mode" && data.mode === "inline") {
onClose();
}
if (typeof onChartSpecChange === "function" && data.type === "datascience-chart-widget-spec-reset" && data.widgetInstanceId === widgetInstanceId) {
onChartSpecChange(chart.id, null);
}
if (typeof onChartSpecChange === "function" && data.type === "datascience-chart-widget-spec-change" && data.widgetInstanceId === widgetInstanceId) {
onChartSpecChange(chart.id, data.visualization_spec);
}
if (data.type === "datascience-chart-widget-codex-prompt" && typeof data.prompt === "string" && environment?.capabilities?.hostPrompts !== false) {
void sendPromptToHost(data.prompt, "Continue chart analysis");
}
}
window.addEventListener("message", handleWidgetMessage);
return () => window.removeEventListener("message", handleWidgetMessage);
}, [chart.id, environment, onChartSpecChange, onClose, widgetInstanceId]);
return (<dialog aria-label={modalLabel} className="native-modal chart-explore-modal" onCancel={onClose} onClick={(event) => {
if (event.target === event.currentTarget) {
event.currentTarget.close();
}
}} onClose={onClose} ref={dialogRef}>
<section className="modal-panel chart-explore-panel">
<section aria-label={modalLabel} className="chart-detail-page unified-chart-detail-page chart-explore-body">
{accessIssue ? (<ChartBody accessIssue={accessIssue} chart={chart} filters={filters} isFullscreen selectedFilters={selectedFilters} snapshot={snapshot}/>) : (<>
{!widgetHtml && !widgetError ? <div className="chart-detail-loading">Loading chart detail...</div> : null}
{widgetError ? <div className="empty-state error-state">{widgetError}</div> : null}
<iframe className="unified-chart-detail-frame" hidden={!widgetHtml || Boolean(widgetError)} onLoad={scheduleWidgetPayloadPosts} ref={iframeRef} srcDoc={widgetHtml ?? ""} title={modalLabel}/>
</>)}
</section>
</section>
</dialog>);
}
function chartWidgetColumnType(column, value) {
if (column?.type === "date")
return "date";
if (column?.format || column?.type === "currency" || column?.type === "number" || column?.type === "percent")
return "number";
if (typeof value === "number")
return "number";
if (typeof value === "string" && /^\d{4}-\d{2}(?:-\d{2})?(?:$|[T\s])/.test(value))
return "date";
return "text";
}
function chartWidgetEncodingColumn(chart, role, rows) {
const field = chartEncodingField(chart, role);
if (!field)
return null;
const encoding = chartEncoding(chart, role);
const format = encoding.format ?? (role === "y" ? chart.valueFormat : undefined);
return {
key: field,
label: chartEncodingLabel(chart, role, field),
type: encoding.type === "temporal" ? "date" : encoding.type === "quantitative" ? "number" : chartWidgetColumnType(encoding, rows[0]?.[field]),
...(format ? { format } : {}),
unit: encoding.unit
};
}
function chartWidgetSource(source, sourceQuery, queryText, snapshot) {
return {
id: source?.id,
label: source?.label,
path: source?.path,
href: source?.href,
query: {
engine: sourceQuery?.engine ?? source?.label ?? "report manifest",
executed_at: sourceQuery?.executed_at ?? snapshot?.generatedAt,
id: sourceQuery?.id ?? source?.path ?? source?.href,
url: sourceQuery?.url,
sql: queryText || "",
description: sourceQuery?.description,
language: sourceQuery?.language ?? (source?.path?.toLowerCase().endsWith(".sql") ? "SQL" : undefined),
tables_used: sourceQuery?.tables_used,
filters: sourceQuery?.filters,
metric_definitions: sourceQuery?.metric_definitions
}
};
}
function chartWidgetPayloadFromEncodings(chart, rows, source, snapshot, sourceQueryText) {
const xField = chartEncodingField(chart, "x");
const yField = chartEncodingField(chart, "y");
const yFields = chartEncodingFields(chart, "y");
const colorField = chartEncodingField(chart, "color");
const chartSourceQuery = sourceQueryFromChartSpec(chart);
const sourceSpecQuery = sourceQueryFromSourceSpec(source);
const sourceQuery = chartSourceQuery ?? sourceSpecQuery;
const queryText = queryTextFromSourceQuery(chartSourceQuery) ||
queryTextFromSourceQuery(sourceSpecQuery) ||
sourceQueryText?.trim();
const yEncoding = chartEncoding(chart, "y");
const yFormat = yEncoding.format ?? chart.valueFormat;
const yFormatSpec = yFormat ? { format: yFormat } : {};
const unit = chart.unit ?? yEncoding.unit ?? (yFormat === "currency" ? "USD" : yFormat === "percent" ? "%" : undefined);
const settings = chartWidgetSettings(chart);
if (xField && yField) {
const columns = [
chartWidgetEncodingColumn(chart, "x", rows),
colorField ? chartWidgetEncodingColumn(chart, "color", rows) : null,
chartWidgetEncodingColumn(chart, "y", rows)
].filter(Boolean);
return {
ok: true,
widget_type: "chart",
title: chart.title,
subtitle: chart.showDescription ? chart.subtitle : undefined,
source: chartWidgetSource(source, sourceQuery, queryText, snapshot),
result_table: {
columns,
row_count: rows.length,
rows: rows.map((row) => Object.fromEntries(columns.map((column) => [column.key, row[column.key]]))),
truncated: false
},
visualization_spec: {
version: "1",
intent: chart.intent ?? "custom",
visualization_type: chart.type,
encodings: {
x: { field: xField, type: chartEncoding(chart, "x").type ?? "nominal" },
y: { aggregate: yEncoding.aggregate ?? "sum", field: yField, type: "quantitative", ...yFormatSpec, unit },
...(colorField ? { color: { field: colorField, type: chartEncoding(chart, "color").type ?? "nominal" } } : {})
},
presentation: {
show_controls: true,
unit,
view_mode: "both"
},
settings
}
};
}
if (xField && yFields.length) {
const longRows = rows.flatMap((row) => yFields.map((field) => ({
[xField]: row[xField],
series: field,
value: row[field]
})));
return {
ok: true,
widget_type: "chart",
title: chart.title,
subtitle: chart.showDescription ? chart.subtitle : undefined,
source: chartWidgetSource(source, sourceQuery, queryText, snapshot),
result_table: {
columns: [
{ key: xField, label: chartEncodingLabel(chart, "x", xField), type: chartWidgetColumnType(chartEncoding(chart, "x"), rows[0]?.[xField]) },
{ key: "series", label: "Series", type: "text" },
{ key: "value", label: chartEncodingLabel(chart, "y", "Value"), type: "number", ...yFormatSpec, unit }
],
row_count: longRows.length,
rows: longRows,
truncated: false
},
visualization_spec: {
version: "1",
intent: chart.intent ?? "custom",
visualization_type: chart.type,
encodings: {
x: { field: xField, type: chartEncoding(chart, "x").type ?? "nominal" },
y: { aggregate: "sum", field: "value", type: "quantitative", ...yFormatSpec, unit },
color: { field: "series", type: "nominal" }
},
presentation: {
show_controls: true,
unit,
view_mode: "both"
},
settings
}
};
}
return null;
}
function chartWidgetSettings(chart) {
const source = chart?.settings && typeof chart.settings === "object" && !Array.isArray(chart.settings) ? chart.settings : {};
const type = chart?.type;
const orientation = source.orientation === "horizontal" || type === "horizontalBar" || type === "horizontalStackedBar" || type === "horizontalStackedBar100"
? "horizontal"
: source.orientation === "vertical"
? "vertical"
: undefined;
const groupMode = source.groupMode ?? source.group_mode ?? (type === "stackedBar100" || type === "horizontalStackedBar100"
? "stacked100"
: type === "stackedBar" || type === "horizontalStackedBar"
? "stacked"
: undefined);
return {
...(orientation ? { orientation } : {}),
...(["grouped", "stacked", "stacked100"].includes(groupMode) ? { group_mode: groupMode } : {})
};
}
function chartWidgetPayload(chart, rows, source, snapshot, sourceQueryText) {
const encodedPayload = chartHasEncodingSpec(chart) ? chartWidgetPayloadFromEncodings(chart, rows, source, snapshot, sourceQueryText) : null;
if (encodedPayload)
return encodedPayload;
return null;
}
function TableContent({ allowColumnResize = true, columnWidths, density, fillAvailableWidth = true, filters, onColumnWidthsChange, pageSize: requestedPageSize = TABLE_CARD_PAGE_SIZE, selectedFilters, snapshot, table, isFullscreen = false }) {
const rows = filterRowsForDataset(getRows(snapshot, table.dataset), table.dataset, filters, selectedFilters, table.columns.map((column) => column.field));
const [page, setPage] = useState(0);
const [sortState, setSortState] = useState(() => tableDefaultSort(table));
const [isColumnResizing, setIsColumnResizing] = useState(false);
const [tableViewportWidth, setTableViewportWidth] = useState(0);
const [horizontalScrollEdges, setHorizontalScrollEdges] = useState(EMPTY_HORIZONTAL_SCROLL_EDGES);
const headerCellRefs = useRef({});
const tableElementRef = useRef(null);
const tableWrapRef = useRef(null);
const tableScrollContentRef = useRef(null);
const sortedRows = useMemo(() => {
if (!sortState)
return rows;
return [...rows].sort((a, b) => compareTableValues(a, b, sortState.field, sortState.direction));
}, [rows, sortState]);
const pageSize = isFullscreen ? Math.max(1, sortedRows.length) : Math.max(1, requestedPageSize);
const totalPages = Math.max(1, Math.ceil(sortedRows.length / pageSize));
const currentPage = Math.min(page, totalPages - 1);
const shouldShowPagination = rows.length > 0 && !isFullscreen && totalPages > 1;
const shouldShowCount = rows.length > 0 && shouldShowPagination;
const shouldShowFooter = shouldShowCount || shouldShowPagination;
const resultCountLabel = `${sortedRows.length.toLocaleString()} ${sortedRows.length === 1 ? "result" : "results"}`;
const visibleRows = isFullscreen
? sortedRows
: sortedRows.slice(currentPage * pageSize, currentPage * pageSize + pageSize);
const estimatedColumnWidths = useMemo(() => estimateTableColumnWidths(table, rows, density), [density, rows, table]);
const activeColumnWidths = useMemo(() => {
return Object.fromEntries(table.columns.map((column) => [
column.field,
clamp(Math.round(columnWidths[column.field] ?? estimatedColumnWidths[column.field] ?? TABLE_COLUMN_DEFAULT_WIDTH), TABLE_COLUMN_MIN_WIDTH, TABLE_COLUMN_MAX_WIDTH)
]));
}, [columnWidths, estimatedColumnWidths, table.columns]);
const hasContentSizedColumns = table.columns.some((column) => column.sizing === "content");
const shouldFillAvailableWidth = isFullscreen || fillAvailableWidth;
const tableSizing = calculateTableSizing(table.columns, activeColumnWidths, tableViewportWidth, shouldFillAvailableWidth);
const renderedColumnWidths = tableSizing.columnWidths;
const tableStyle = {
minWidth: `${tableSizing.minimumTableWidth}px`,
tableLayout: "fixed",
width: `${tableSizing.tableWidth}px`
};
const updateHorizontalScrollEdges = useCallback(() => {
const tableWrap = tableWrapRef.current;
const nextEdges = tableWrap
? {
...calculateHorizontalScrollEdges({
clientWidth: tableWrap.clientWidth,
scrollLeft: tableWrap.scrollLeft,
scrollWidth: tableElementRef.current?.offsetWidth ?? tableWrap.scrollWidth
}),
scrollbarBlockSize: Math.max(0, tableWrap.offsetHeight - tableWrap.clientHeight),
scrollbarInlineSize: Math.max(0, tableWrap.offsetWidth - tableWrap.clientWidth)
}
: EMPTY_HORIZONTAL_SCROLL_EDGES;
setHorizontalScrollEdges((currentEdges) => currentEdges.canScrollLeft === nextEdges.canScrollLeft &&
currentEdges.canScrollRight === nextEdges.canScrollRight &&
currentEdges.hasOverflow === nextEdges.hasOverflow &&
currentEdges.scrollbarBlockSize === nextEdges.scrollbarBlockSize &&
currentEdges.scrollbarInlineSize === nextEdges.scrollbarInlineSize
? currentEdges
: nextEdges);
}, []);
function columnWidthStyle(column) {
return {
...(column.sizing === "content" ? { maxWidth: `${TABLE_COLUMN_CONTENT_FIT_MAX_WIDTH}px` } : {}),
width: `${renderedColumnWidths[column.field]}px`
};
}
useEffect(() => {
setPage(0);
}, [isFullscreen, requestedPageSize, rows.length, sortState]);
useEffect(() => {
setSortState(tableDefaultSort(table));
}, [table.defaultSort?.direction, table.defaultSort?.field, table.id]);
useLayoutEffect(() => {
if (tableWrapRef.current) {
tableWrapRef.current.scrollLeft = 0;
updateHorizontalScrollEdges();
}
}, [isFullscreen, rows.length, table.id, updateHorizontalScrollEdges]);
useLayoutEffect(() => {
if (!shouldFillAvailableWidth || !tableWrapRef.current) {
setTableViewportWidth(0);
return undefined;
}
const tableWrap = tableWrapRef.current;
const updateViewportWidth = () => setTableViewportWidth(Math.floor(tableWrap.clientWidth));
updateViewportWidth();
if (typeof ResizeObserver !== "function")
return undefined;
const observer = new ResizeObserver(updateViewportWidth);
observer.observe(tableWrap);
return () => observer.disconnect();
}, [shouldFillAvailableWidth, table.id]);
useLayoutEffect(() => {
const tableWrap = tableWrapRef.current;
const tableScrollContent = tableScrollContentRef.current;
const tableElement = tableElementRef.current;
if (!tableWrap) {
setHorizontalScrollEdges(EMPTY_HORIZONTAL_SCROLL_EDGES);
return undefined;
}
updateHorizontalScrollEdges();
tableWrap.addEventListener("scroll", updateHorizontalScrollEdges, { passive: true });
if (typeof ResizeObserver !== "function") {
window.addEventListener("resize", updateHorizontalScrollEdges);
return () => {
tableWrap.removeEventListener("scroll", updateHorizontalScrollEdges);
window.removeEventListener("resize", updateHorizontalScrollEdges);
};
}
const observer = new ResizeObserver(updateHorizontalScrollEdges);
observer.observe(tableWrap);
if (tableScrollContent)
observer.observe(tableScrollContent);
if (tableElement)
observer.observe(tableElement);
return () => {
observer.disconnect();
tableWrap.removeEventListener("scroll", updateHorizontalScrollEdges);
};
}, [isFullscreen, rows.length, table.id, tableSizing.tableWidth, updateHorizontalScrollEdges]);
function toggleSort(field) {
setSortState((current) => {
if (current?.field !== field)
return { direction: "asc", field };
return { direction: current.direction === "asc" ? "desc" : "asc", field };
});
}
function measuredColumnWidths() {
return Object.fromEntries(table.columns.map((column) => {
const measuredWidth = headerCellRefs.current[column.field]?.getBoundingClientRect().width;
const width = measuredWidth ?? activeColumnWidths[column.field] ?? TABLE_COLUMN_DEFAULT_WIDTH;
return [
column.field,
clamp(Math.round(width), TABLE_COLUMN_MIN_WIDTH, TABLE_COLUMN_MAX_WIDTH)
];
}));
}
function resizeColumnBy(field, delta, shouldPersist) {
const baseWidths = { ...activeColumnWidths, ...measuredColumnWidths(), ...columnWidths };
const currentWidth = baseWidths[field] ?? TABLE_COLUMN_DEFAULT_WIDTH;
onColumnWidthsChange(table.id, {
...baseWidths,
[field]: clamp(Math.round(currentWidth + delta), TABLE_COLUMN_MIN_WIDTH, TABLE_COLUMN_MAX_WIDTH)
}, { persist: shouldPersist });
}
function startColumnResize(event, field) {
event.preventDefault();
event.stopPropagation();
const baseWidths = { ...activeColumnWidths, ...measuredColumnWidths(), ...columnWidths };
const startWidth = baseWidths[field] ?? TABLE_COLUMN_DEFAULT_WIDTH;
const startX = event.clientX;
let latestWidths = baseWidths;
onColumnWidthsChange(table.id, baseWidths, { persist: false });
setIsColumnResizing(true);
document.body.style.cursor = "col-resize";
document.body.style.userSelect = "none";
function handlePointerMove(moveEvent) {
const nextWidth = clamp(Math.round(startWidth + moveEvent.clientX - startX), TABLE_COLUMN_MIN_WIDTH, TABLE_COLUMN_MAX_WIDTH);
latestWidths = { ...baseWidths, [field]: nextWidth };
onColumnWidthsChange(table.id, latestWidths, { persist: false });
}
function finishResize() {
window.removeEventListener("pointermove", handlePointerMove);
window.removeEventListener("pointerup", finishResize);
window.removeEventListener("pointercancel", finishResize);
document.body.style.cursor = "";
document.body.style.userSelect = "";
setIsColumnResizing(false);
onColumnWidthsChange(table.id, latestWidths, { persist: true });
}
window.addEventListener("pointermove", handlePointerMove);
window.addEventListener("pointerup", finishResize);
window.addEventListener("pointercancel", finishResize);
}
function handleResizeHandleKeyDown(event, field) {
if (event.key !== "ArrowLeft" && event.key !== "ArrowRight")
return;
event.preventDefault();
event.stopPropagation();
resizeColumnBy(field, event.key === "ArrowRight" ? TABLE_COLUMN_KEYBOARD_STEP : -TABLE_COLUMN_KEYBOARD_STEP, true);
}
const isScrollableTableRegion = isFullscreen || horizontalScrollEdges.hasOverflow;
const tableScrollShellStyle = {
"--table-scrollbar-block-size": `${horizontalScrollEdges.scrollbarBlockSize}px`,
"--table-scrollbar-inline-size": `${horizontalScrollEdges.scrollbarInlineSize}px`
};
return (<>
{rows.length ? (<div className={`table-scroll-shell ${isFullscreen ? "is-fullscreen" : ""}`} data-can-scroll-left={horizontalScrollEdges.canScrollLeft ? "true" : "false"} data-can-scroll-right={horizontalScrollEdges.canScrollRight ? "true" : "false"} style={tableScrollShellStyle}>
<div aria-label={isScrollableTableRegion ? `Scrollable table: ${table.title}` : undefined} className={`table-wrap table-density-${density} ${isFullscreen ? "fullscreen" : ""}`} ref={tableWrapRef} role={isScrollableTableRegion ? "region" : undefined} tabIndex={isScrollableTableRegion ? 0 : undefined}>
<div className="table-scroll-content" ref={tableScrollContentRef}>
<table className={`data-table data-table-${density} data-table-resizable ${hasContentSizedColumns ? "data-table-smart-layout" : ""} ${isColumnResizing ? "is-column-resizing" : ""}`} ref={tableElementRef} style={tableStyle}>
<colgroup>
{table.columns.map((column) => (<col className={column.sizing === "content" ? "table-column-content-fit" : undefined} key={column.field} style={columnWidthStyle(column)}/>))}
</colgroup>
<thead>
<tr>
{table.columns.map((column) => {
const isSorted = sortState?.field === column.field;
const format = tableColumnFormat(column);
const isNumericColumn = isNumericTableColumn(column, rows);
const isCenteredColumn = column.align === "center";
const SortIcon = isSorted ? (sortState.direction === "asc" ? ArrowUp : ArrowDown) : null;
const headerClassName = [
isNumericColumn ? "table-header-number" : "",
isCenteredColumn ? "center" : "",
column.sizing === "content" ? "table-column-content-fit" : ""
].filter(Boolean).join(" ") || undefined;
return (<th aria-sort={isSorted
? sortState.direction === "asc"
? "ascending"
: "descending"
: "none"} key={column.field} ref={(element) => {
headerCellRefs.current[column.field] = element;
}} className={headerClassName} style={columnWidthStyle(column)}>
<button className="table-sort-button" onClick={() => toggleSort(column.field)} type="button">
<span>{column.label}</span>
{SortIcon ? <SortIcon aria-hidden="true" size={14} strokeWidth={2}/> : null}
</button>
{allowColumnResize ? (<button aria-label={`Resize ${column.label} column`} className="table-column-resize-handle" onKeyDown={(event) => handleResizeHandleKeyDown(event, column.field)} onPointerDown={(event) => startColumnResize(event, column.field)} title={`Resize ${column.label} column`} type="button"/>) : null}
</th>);
})}
</tr>
</thead>
<tbody>
{visibleRows.map((row, rowIndex) => (<tr key={`${currentPage}-${rowIndex}`}>
{table.columns.map((column) => {
const value = row[column.field];
const format = tableColumnFormat(column);
const isNumericColumn = isNumericTableColumn(column, rows);
const isCenteredColumn = column.align === "center";
const className = [
isNumericColumn ? "table-cell-number" : "",
isCenteredColumn ? "center" : "",
column.sizing === "content" ? "table-column-content-fit" : "",
tableCellMovementClass(column, value)
].filter(Boolean).join(" ") || undefined;
return (<td className={className} key={column.field}>
{formatTableCellValue(column, value)}
</td>);
})}
</tr>))}
</tbody>
</table>
</div>
</div>
<span aria-hidden="true" className="table-scroll-edge table-scroll-edge-left" data-image-export-exclude="true"/>
<span aria-hidden="true" className="table-scroll-edge table-scroll-edge-right" data-image-export-exclude="true"/>
</div>) : (<div className="empty-state">No rows match the selected filters.</div>)}
{shouldShowFooter ? (<div className="table-pagination">
{shouldShowCount ? <span className="table-result-count">{resultCountLabel}</span> : null}
{shouldShowPagination ? (<div className="table-page-control">
<span>
Page {currentPage + 1} of {totalPages}
</span>
<div className="table-page-buttons">
<button aria-label="Previous page" className="table-arrow-button" disabled={currentPage === 0} onClick={() => setPage((nextPage) => Math.max(0, nextPage - 1))} type="button">
<ChevronLeft aria-hidden="true" size={16} strokeWidth={2}/>
</button>
<button aria-label="Next page" className="table-arrow-button" disabled={currentPage >= totalPages - 1} onClick={() => setPage((nextPage) => Math.min(totalPages - 1, nextPage + 1))} type="button">
<ChevronRight aria-hidden="true" size={16} strokeWidth={2}/>
</button>
</div>
</div>) : null}
</div>) : null}
</>);
}
function DataTable({ allowColumnResize = true, columnWidths, filters, isEditMode, isMenuOpen, layout, manifest, onColumnWidthsChange, onDeleteBlock, onMenuOpenChange, onModalOpen, onRequestEditMode, onTextChange, selectedFilters, snapshot, table, textOverride }) {
const tableDensity = table.density ?? (manifest?.surface === "report" ? "spacious" : "dense");
const displayHeaderMarkdown = textOverride?.headerMarkdown ?? composeTableHeaderMarkdown(table);
const displayTitle = markdownFirstLine(displayHeaderMarkdown, table.title);
const { closeMenu, fixedMenuStyle, handleMenuButtonKeyDown, handleMenuKeyDown, menuButtonRef, menuMotionClass, menuRef, toggleMenu, shouldRenderMenu } = useDashboardMenu(isMenuOpen, onMenuOpenChange);
const menuItem = (label, icon, onClick, tone = "default") => (<button className={`viz-card-menu-item ${tone === "danger" ? "viz-card-menu-item-danger" : ""}`.trim()} data-artifact-action={label === "View data source" ? "view-source" : undefined} key={label} onClick={() => {
onClick();
closeMenu();
}} role="menuitem" type="button">
<span aria-hidden="true" className="viz-card-menu-icon">
{icon}
</span>
<span>{label}</span>
</button>);
return (<section className={`panel table-panel table-card ${layout === "half" ? "" : "layout-full"}`} data-artifact-id={table.id} data-artifact-kind="table">
<PanelHeader action={<div className="viz-card-actions" data-image-export-exclude="true" ref={menuRef}>
<button aria-expanded={isMenuOpen} aria-label={`Open options for ${table.title}`} className="viz-card-menu-button viz-card__no-drag" data-artifact-action="open-options" data-artifact-has-source={table.sourceId || table.source ? "true" : "false"} data-artifact-id={table.id} data-artifact-kind="table" onClick={(event) => {
event.stopPropagation();
toggleMenu();
}} onKeyDown={handleMenuButtonKeyDown} ref={menuButtonRef} type="button">
<Ellipsis aria-hidden="true" size={18} strokeWidth={2}/>
</button>
{shouldRenderMenu ? (<div className={`viz-card-menu menu-surface ${menuMotionClass}`} onKeyDown={handleMenuKeyDown} role="menu" style={fixedMenuStyle}>
{menuItem("View data source", <Database size={18} strokeWidth={2}/>, () => onModalOpen({ kind: "source", table }))}
{menuItem("View fullscreen", <Expand size={18} strokeWidth={2}/>, () => onModalOpen({ kind: "fullscreen", table }))}
{onDeleteBlock ? menuItem("Delete", <Trash2 size={18} strokeWidth={2}/>, onDeleteBlock, "danger") : null}
</div>) : null}
</div>} subtitle={table.subtitle} title={displayTitle} titleRowClassName="table-card__drag-handle">
<RichMarkdown ariaLabel={`Edit markdown header for ${table.title}`} className="editable-cell-header" isEditMode={isEditMode} markdown={displayHeaderMarkdown} onMarkdownChange={(nextMarkdown) => onTextChange(table.id, { headerMarkdown: nextMarkdown })} onRequestEditMode={onRequestEditMode} placeholder={composeTableHeaderMarkdown(table)} variant="cellHeader"/>
</PanelHeader>
<TableContent allowColumnResize={allowColumnResize} columnWidths={columnWidths} density={tableDensity} filters={filters} onColumnWidthsChange={onColumnWidthsChange} selectedFilters={selectedFilters} snapshot={snapshot} table={table}/>
</section>);
}
function TableModalDialog({ activeFilters, allowColumnResize = true, columnWidths, environment, filters, kind, manifest, onColumnWidthsChange, onClose, selectedFilters, snapshot, table }) {
const dialogRef = useRef(null);
const source = sourceForTable(table, manifest?.sources ?? []);
const title = kind === "fullscreen" ? table.title : "Data source";
const sourceQuery = sourceQueryFromSourceSpec(source);
const previewRows = filterRowsForDataset(getRows(snapshot, table.dataset), table.dataset, filters, selectedFilters, table.columns.map((column) => column.field));
const buildDetails = sourceBuildDetails({
activeFilters,
columns: table.columns,
dataset: table.dataset,
source,
sourceQuery,
snapshot
});
useModalScrollLock(true);
useEffect(() => {
const dialog = dialogRef.current;
if (dialog && !dialog.open) {
dialog.showModal();
}
}, []);
return (<dialog aria-labelledby="table-modal-title" className={`native-modal ${kind === "source" ? "source-modal" : "table-fullscreen-modal"}`.trim()} data-artifact-dialog={kind === "source" ? "source" : undefined} data-artifact-item-id={table.id} data-artifact-item-type="table" onCancel={onClose} onClick={(event) => {
if (event.target === event.currentTarget) {
event.currentTarget.close();
}
}} onClose={onClose} ref={dialogRef}>
<section className={`modal-panel ${kind === "source" ? "source-modal-panel" : "table-fullscreen-panel"}`.trim()}>
<div className="modal-header">
<div>
<h2 id="table-modal-title">{title}</h2>
{kind === "fullscreen" && source?.label ? <p>{source.label}</p> : null}
</div>
<button aria-label={`Close ${kind === "source" ? "data source" : "fullscreen table"}`} className="modal-close-button" onClick={() => dialogRef.current?.close()} type="button">
<X aria-hidden="true" size={20} strokeWidth={2}/>
</button>
</div>
{kind === "fullscreen" ? (<TableContent allowColumnResize={allowColumnResize} columnWidths={columnWidths} density={table.density ?? (manifest?.surface === "report" ? "spacious" : "dense")} filters={filters} isFullscreen onColumnWidthsChange={onColumnWidthsChange} selectedFilters={selectedFilters} snapshot={snapshot} table={table}/>) : (<DataSourceDetails details={buildDetails} environment={environment} itemLabel={table.title} itemType="Table" source={source} sourceQuery={sourceQuery}>
<SourceDataTable columns={table.columns} dataset={table.dataset} density={table.density ?? (manifest?.surface === "report" ? "spacious" : "dense")} pageSize={SOURCE_DATA_PREVIEW_PAGE_SIZE} rows={previewRows}/>
</DataSourceDetails>)}
</section>
</dialog>);
}
function ReportTextBlock({ block, capabilities, isEditMode, isMenuOpen, onCopyResult, onDeleteBlock, onMenuOpenChange, onRequestEditMode, onTextChange, textOverride }) {
const cardRef = useRef(null);
const toneClass = `report-block-${block.type}`;
const blockMarkdown = composeBlockMarkdown(block, textOverride);
const { closeMenu, fixedMenuStyle, handleMenuButtonKeyDown, handleMenuKeyDown, menuButtonRef, menuMotionClass, menuRef, toggleMenu, shouldRenderMenu } = useDashboardMenu(isMenuOpen, onMenuOpenChange);
const { getPreparedImageBlob, preparedImageExportStatus, prepareImageExport, resetPreparedImageExport } = usePreparedImageExport(cardRef);
async function handleCopyMarkdown() {
try {
await copyTextToClipboard(blockMarkdown.trim());
onCopyResult("Copied markdown.");
}
catch (error) {
onCopyResult(error instanceof Error ? error.message : "Failed to copy markdown.", true);
}
}
function prepareImageExportQuietly(force = false) {
if (!capabilities.canCopyImage || !shouldOfferImageClipboardCopy())
return;
const prepared = prepareImageExport({ force });
if (prepared)
void prepared.promise.catch(() => undefined);
}
async function handleCopyAsImage() {
if (!cardRef.current)
return;
try {
const copyResult = await copyElementAsImage(cardRef.current, getPreparedImageBlob());
resetPreparedImageExport();
onCopyResult(imageCopySuccessMessage("Copied text block as image.", copyResult));
}
catch (error) {
onCopyResult(error instanceof Error ? error.message : "Failed to copy image.", true);
}
}
const menuItem = (label, icon, onClick, tone = "default", onPrepare, disabled = false) => (<button className={`viz-card-menu-item ${tone === "danger" ? "viz-card-menu-item-danger" : ""}`.trim()} disabled={disabled} key={label} onFocus={onPrepare} onClick={() => {
void onClick();
closeMenu();
}} onPointerEnter={onPrepare} role="menuitem" type="button">
<span aria-hidden="true" className="viz-card-menu-icon">
{icon}
</span>
<span>{label}</span>
</button>);
return (<section className={`panel report-block report-markdown-block ${toneClass}`} data-artifact-id={block.id} data-artifact-kind="block" id={block.id} ref={cardRef}>
<div className="viz-card-actions" data-image-export-exclude="true" ref={menuRef}>
<button aria-expanded={isMenuOpen} aria-label={`Open options for ${markdownFirstLine(blockMarkdown, "Text block")}`} className="viz-card-menu-button viz-card__no-drag" onClick={(event) => {
event.stopPropagation();
const nextIsMenuOpen = toggleMenu();
if (nextIsMenuOpen) {
prepareImageExportQuietly(true);
}
else {
resetPreparedImageExport();
}
}} onFocus={() => prepareImageExportQuietly()} onKeyDown={handleMenuButtonKeyDown} onPointerEnter={() => prepareImageExportQuietly()} ref={menuButtonRef} type="button">
<Ellipsis aria-hidden="true" size={18} strokeWidth={2}/>
</button>
{shouldRenderMenu ? (<div className={`viz-card-menu viz-card__no-drag menu-surface ${menuMotionClass}`} onKeyDown={handleMenuKeyDown} role="menu" style={fixedMenuStyle}>
{menuItem("Copy markdown", <Copy size={18} strokeWidth={2}/>, handleCopyMarkdown)}
{capabilities.canCopyImage && shouldOfferImageClipboardCopy()
? menuItem("Copy as image", <Camera size={18} strokeWidth={2}/>, handleCopyAsImage, "default", prepareImageExportQuietly, preparedImageExportStatus === "pending")
: null}
{onDeleteBlock ? menuItem("Delete", <Trash2 size={18} strokeWidth={2}/>, onDeleteBlock, "danger") : null}
</div>) : null}
</div>
<div className="report-block-body markdown-body">
<RichMarkdown ariaLabel={`Edit markdown for ${block.type}`} className="report-markdown-editor" isEditMode={isEditMode} markdown={blockMarkdown} minRows={Math.max(2, Math.min(6, blockMarkdown.split(/\r?\n/).length))} onMarkdownChange={(nextMarkdown) => onTextChange(block.id, { bodyMarkdown: nextMarkdown })} onRequestEditMode={onRequestEditMode} placeholder={composeBlockMarkdown(block)} variant="reportBlock"/>
</div>
</section>);
}
function ReportHtmlBlock({ block, htmlOverride, isEditMode, isMenuOpen, onHtmlChange, onCopyResult, onDeleteBlock, onMenuOpenChange }) {
const html = composeBlockHtml(block, htmlOverride);
const title = block.id || "HTML block";
const { closeMenu, fixedMenuStyle, handleMenuButtonKeyDown, handleMenuKeyDown, menuButtonRef, menuMotionClass, menuRef, toggleMenu, shouldRenderMenu } = useDashboardMenu(isMenuOpen, onMenuOpenChange);
const frameRef = useRef(null);
const resizeObserverRef = useRef(null);
const [frameHeight, setFrameHeight] = useState(0);
const updateFrameHeight = useCallback(() => {
const nextHeight = measureHtmlFrameHeight(frameRef.current);
if (nextHeight > 0)
setFrameHeight(nextHeight);
}, []);
const handleFrameLoad = useCallback(() => {
resizeObserverRef.current?.disconnect();
const frameDocument = frameRef.current?.contentDocument;
if (frameDocument && typeof ResizeObserver !== "undefined") {
const observer = new ResizeObserver(updateFrameHeight);
if (frameDocument.documentElement)
observer.observe(frameDocument.documentElement);
if (frameDocument.body)
observer.observe(frameDocument.body);
resizeObserverRef.current = observer;
}
updateFrameHeight();
}, [updateFrameHeight]);
useEffect(() => {
setFrameHeight(0);
}, [html]);
useEffect(() => {
return () => resizeObserverRef.current?.disconnect();
}, []);
async function handleCopyHtml() {
try {
await copyTextToClipboard(html);
onCopyResult("Copied HTML.");
}
catch (error) {
onCopyResult(error instanceof Error ? error.message : "Failed to copy HTML.", true);
}
}
const menuItem = (label, icon, onClick, tone = "default") => (<button className={`viz-card-menu-item ${tone === "danger" ? "viz-card-menu-item-danger" : ""}`.trim()} key={label} onClick={() => {
void onClick();
closeMenu();
}} role="menuitem" type="button">
<span aria-hidden="true" className="viz-card-menu-icon">
{icon}
</span>
<span>{label}</span>
</button>);
return (<section className="report-block report-html-block" data-artifact-id={block.id} data-artifact-kind="block" id={block.id}>
<div className="viz-card-actions" data-image-export-exclude="true" ref={menuRef}>
<button aria-expanded={isMenuOpen} aria-label={`Open options for ${title}`} className="viz-card-menu-button viz-card__no-drag" onClick={(event) => {
event.stopPropagation();
toggleMenu();
}} onKeyDown={handleMenuButtonKeyDown} ref={menuButtonRef} type="button">
<Ellipsis aria-hidden="true" size={18} strokeWidth={2}/>
</button>
{shouldRenderMenu ? (<div className={`viz-card-menu viz-card__no-drag menu-surface ${menuMotionClass}`} onKeyDown={handleMenuKeyDown} role="menu" style={fixedMenuStyle}>
{menuItem("Copy HTML", <Copy size={18} strokeWidth={2}/>, handleCopyHtml)}
{onDeleteBlock ? menuItem("Delete", <Trash2 size={18} strokeWidth={2}/>, onDeleteBlock, "danger") : null}
</div>) : null}
</div>
{isEditMode ? (<textarea aria-label={`Edit HTML for ${title}`} className="report-html-editor" onChange={(event) => onHtmlChange(block.id, { html: event.target.value })} spellCheck={false} value={html}/>) : (<iframe className="report-html-frame" onLoad={handleFrameLoad} ref={frameRef} sandbox="allow-same-origin" srcDoc={sandboxedReportHtml(html)} style={frameHeight ? { height: `${frameHeight}px` } : undefined} title={title}/>)}
</section>);
}
function ArtifactMetricCard({ card, filters, id, isMenuOpen, onDeleteBlock, onMenuOpenChange, onSourceOpen, selectedFilters, snapshot }) {
const { closeMenu, fixedMenuStyle, handleMenuButtonKeyDown, handleMenuKeyDown, menuButtonRef, menuMotionClass, menuRef, toggleMenu, shouldRenderMenu } = useDashboardMenu(isMenuOpen, onMenuOpenChange);
const label = cardLabel(card);
const menuItem = (itemLabel, icon, onClick, tone = "default") => (<button className={`viz-card-menu-item ${tone === "danger" ? "viz-card-menu-item-danger" : ""}`.trim()} data-artifact-action={itemLabel === "View data source" ? "view-source" : undefined} key={itemLabel} onClick={() => {
void onClick();
closeMenu();
}} role="menuitem" type="button">
<span aria-hidden="true" className="viz-card-menu-icon">
{icon}
</span>
<span>{itemLabel}</span>
</button>);
const action = (<div className="viz-card-actions" data-image-export-exclude="true" ref={menuRef}>
<button aria-expanded={isMenuOpen} aria-label={`Open options for ${label}`} className="viz-card-menu-button viz-card__no-drag" data-artifact-action="open-options" data-artifact-has-source={card.sourceId || card.source ? "true" : "false"} data-artifact-id={card.id ?? id} data-artifact-kind="card" onClick={(event) => {
event.stopPropagation();
toggleMenu();
}} onKeyDown={handleMenuButtonKeyDown} ref={menuButtonRef} type="button">
<Ellipsis aria-hidden="true" size={18} strokeWidth={2}/>
</button>
{shouldRenderMenu ? (<div className={`viz-card-menu viz-card__no-drag menu-surface ${menuMotionClass}`} onKeyDown={handleMenuKeyDown} role="menu" style={fixedMenuStyle}>
{menuItem("View data source", <Database size={18} strokeWidth={2}/>, onSourceOpen)}
{onDeleteBlock ? menuItem("Delete", <Trash2 size={18} strokeWidth={2}/>, onDeleteBlock, "danger") : null}
</div>) : null}
</div>);
return (<KpiCard action={action} card={card} className="report-metric-card" filters={filters} id={id} selectedFilters={selectedFilters} snapshot={snapshot}/>);
}
function ReportBlockCard({ accessIssues, allowColumnResize, block, blockTextOverride, canEditChartSpec, canEditHtml, chart, chartSpecOverride, chartTextOverride, chartTypeOverride, columnWidths, filters, isBlockMenuOpen, isChartMenuOpen, isEditMode, isTableMenuOpen, layout, manifest, onBlockMenuOpenChange, onBlockTextChange, onChartTypeChange, onChartMenuOpenChange, onColumnWidthsChange, onDeleteBlock, onChartModalOpen, onCopyResult, onRequestEditMode, onTableMenuOpenChange, onTableModalOpen, onTableTextChange, onTextChange, selectedFilters, snapshot, table, tableTextOverride }) {
const { capabilities } = useArtifactReaderContext();
if (block.type === "html") {
return (<ReportHtmlBlock block={block} htmlOverride={blockTextOverride} isEditMode={isEditMode && canEditHtml} isMenuOpen={isBlockMenuOpen} onHtmlChange={onBlockTextChange} onCopyResult={onCopyResult} onDeleteBlock={onDeleteBlock} onMenuOpenChange={onBlockMenuOpenChange}/>);
}
if (block.type === "chart" && chart) {
const overriddenChart = applyChartSpecOverride(chart, chartSpecOverride);
const chartRows = filterRowsForDataset(getRows(snapshot, overriddenChart.dataset), overriddenChart.dataset, filters, selectedFilters, chartUsedFields(overriddenChart));
const chartTypeOptions = compatibleChartTypesForArtifactCard(overriddenChart, chartRows);
const requestedType = chartTypeOverride ?? overriddenChart.type;
const activeType = chartTypeOptions.some((option) => option.type === requestedType)
? requestedType
: overriddenChart.type;
const displayChart = withChartType(overriddenChart, activeType);
const accessIssue = accessIssueForChart(displayChart, accessIssues);
return (<VizCard accessIssue={accessIssue} capabilities={capabilities} canEditChartSpec={canEditChartSpec} chart={displayChart} chartTypeOptions={chartTypeOptions} isEditMode={isEditMode} isMenuOpen={isChartMenuOpen} layout={layout} onChartTypeChange={onChartTypeChange} onCopyResult={onCopyResult} onDeleteBlock={onDeleteBlock} onMenuOpenChange={onChartMenuOpenChange} onModalOpen={onChartModalOpen} onRequestEditMode={onRequestEditMode} onTextChange={onTextChange} textOverride={chartTextOverride}>
<ChartBody accessIssue={accessIssue} chart={displayChart} filters={filters} layout={layout} selectedFilters={selectedFilters} snapshot={snapshot}/>
</VizCard>);
}
if (block.type === "table" && table) {
return (<DataTable allowColumnResize={allowColumnResize} columnWidths={columnWidths} filters={filters} isEditMode={isEditMode} isMenuOpen={isTableMenuOpen} layout={layout} manifest={manifest} onColumnWidthsChange={onColumnWidthsChange} onDeleteBlock={onDeleteBlock} onMenuOpenChange={onTableMenuOpenChange} onModalOpen={onTableModalOpen} onRequestEditMode={onRequestEditMode} onTextChange={onTableTextChange} selectedFilters={selectedFilters} snapshot={snapshot} table={table} textOverride={tableTextOverride}/>);
}
return (<ReportTextBlock block={block} capabilities={capabilities} isEditMode={isEditMode} isMenuOpen={isBlockMenuOpen} onCopyResult={onCopyResult} onDeleteBlock={onDeleteBlock} onMenuOpenChange={onBlockMenuOpenChange} onRequestEditMode={onRequestEditMode} onTextChange={onBlockTextChange} textOverride={blockTextOverride}/>);
}
const EXPORT_TARGET_LABELS = {
site: "Publish to Sites",
html: "Create HTML file",
pdf: "Create PDF",
document: "Create Google Doc",
slides: "Create Google Slides"
};
const EXPORT_TARGET_ICONS = {
site: <Globe aria-hidden="true" size={16} strokeWidth={2}/>,
html: <FileText aria-hidden="true" size={16} strokeWidth={2}/>,
pdf: <FileDown aria-hidden="true" size={16} strokeWidth={2}/>,
document: <FileText aria-hidden="true" size={16} strokeWidth={2}/>,
slides: <Presentation aria-hidden="true" size={16} strokeWidth={2}/>
};
const EXPORT_TARGET_HANDOFF_DESCRIPTIONS = {
site: "Publish this",
html: "Create a portable HTML file from this",
pdf: "Create a PDF from this",
document: "Create a Google Doc from this",
slides: "Create Google Slides from this"
};
function packageControls(packageInfo) {
return packageInfo?.controls && typeof packageInfo.controls === "object" ? packageInfo.controls : {};
}
function isHostedPresentationSite(packageInfo) {
return packageInfo?.deliveryMode === "site_creator" && packageInfo?.hostedEditing === "presentation";
}
function artifactCapabilities(packageInfo, environment = MCP_ARTIFACT_READER_ENVIRONMENT, presentation = null) {
const controls = packageControls(packageInfo);
const hostedPresentation = isHostedPresentationSite(packageInfo);
const hostedReadOnly = packageInfo?.hostedReadOnly === true || packageInfo?.deliveryMode === "site_creator";
const environmentCapabilities = environment.capabilities ?? MCP_ARTIFACT_READER_ENVIRONMENT.capabilities;
const canHostPrompts = environmentCapabilities.hostPrompts !== false;
const canEditPresentation = hostedPresentation
&& presentation?.canEdit === true
&& controls.edit !== false
&& environmentCapabilities.editContent !== false;
if (hostedPresentation) {
const canAgentHandoff = canEditPresentation && canHostPrompts && controls.export !== false;
const canEditChartSpec = canEditPresentation && environmentCapabilities.editVisualization !== false;
const canDelete = canEditPresentation && environmentCapabilities.deleteContent !== false && controls.delete !== false;
const canReorder = canEditPresentation && environmentCapabilities.reorderContent !== false;
return {
canCopyImage: environmentCapabilities.copyImage !== false,
canDelete,
canDeleteContent: canDelete,
canEdit: canEditPresentation,
canEditChartSpec,
canEditHtml: false,
canEditText: canEditPresentation,
canEditVisualization: canEditChartSpec,
canFetchSourceText: environmentCapabilities.fetchSourceText !== false,
canHostFullscreen: environmentCapabilities.hostFullscreen !== false,
canPersistState: environmentCapabilities.persistState !== false,
canReorder,
canReorderContent: canReorder,
canResizeColumns: false,
canRefresh: canEditPresentation && canHostPrompts && controls.refresh !== false,
canPublishHostedLink: false,
canExportHtml: canAgentHandoff && controls.html !== false,
canExportPdf: canAgentHandoff && controls.pdf !== false,
canExportDocument: canAgentHandoff && controls.document !== false,
canExportSlides: canAgentHandoff && controls.slides !== false,
canSendHostPrompts: canHostPrompts,
isPortable: environment.mode === "portable"
};
}
const canEdit = environmentCapabilities.editContent !== false && !hostedReadOnly && controls.edit !== false;
const canEditVisualization = canEdit && environmentCapabilities.editVisualization !== false;
const canReorder = canEdit && environmentCapabilities.reorderContent !== false;
const canDelete = canEdit && environmentCapabilities.deleteContent !== false && controls.delete !== false;
const canExport = canHostPrompts && !hostedReadOnly && controls.export !== false;
return {
canCopyImage: environmentCapabilities.copyImage !== false,
canDelete,
canDeleteContent: canDelete,
canEdit,
canEditChartSpec: canEditVisualization,
canEditHtml: canEdit,
canEditText: canEdit,
canEditVisualization,
canFetchSourceText: environmentCapabilities.fetchSourceText !== false,
canHostFullscreen: environmentCapabilities.hostFullscreen !== false,
canPersistState: environmentCapabilities.persistState !== false,
canReorder,
canReorderContent: canReorder,
canResizeColumns: canEdit,
canRefresh: canHostPrompts && !hostedReadOnly && controls.refresh !== false,
canPublishHostedLink: canHostPrompts && !hostedReadOnly && controls.exportHostedLink !== false && controls.hostedLink !== false,
canExportHtml: canExport && controls.html !== false,
canExportPdf: canExport && controls.pdf !== false,
canExportDocument: canExport && controls.document !== false,
canExportSlides: canExport && controls.slides !== false,
canSendHostPrompts: canHostPrompts,
isPortable: environment.mode === "portable"
};
}
function exportTargetsForCapabilities(capabilities) {
return Object.keys(EXPORT_TARGET_LABELS).filter((target) => {
if (target === "site")
return capabilities.canPublishHostedLink;
if (target === "html")
return capabilities.canExportHtml;
if (target === "pdf")
return capabilities.canExportPdf;
if (target === "document")
return capabilities.canExportDocument;
if (target === "slides")
return capabilities.canExportSlides;
return false;
});
}
function appSurfaceLabel(manifest) {
return manifest?.surface === "report" ? "report" : "dashboard";
}
function compactArtifactUrl() {
try {
const url = new URL(window.location.href);
for (const name of ["locale", "deviceType", "unsafeSkipTargetOriginCheck"]) {
url.searchParams.delete(name);
}
return url.toString();
}
catch {
return window.location.href;
}
}
function usefulContextPath(value) {
const trimmedValue = value?.trim();
return trimmedValue && trimmedValue !== "tool payload" && !trimmedValue.startsWith("mcp://")
? trimmedValue
: null;
}
function promptContext(manifest, snapshot, packageInfo) {
if (isPublishedArtifactSite(packageInfo)) {
return [
`Published Site: ${canonicalPublishedSiteUrl(window.location.href)}`,
packageInfo?.artifactId ? `Artifact ID: ${packageInfo.artifactId}` : null,
`Generated at: ${snapshot?.generatedAt ?? manifest?.generatedAt ?? "unknown"}`,
"Load the Site's current manifest, snapshot, package metadata, and presentation overrides before acting. Reuse the same Site for refreshes and preserve creator presentation overrides by stable component ID."
]
.filter((line) => Boolean(line))
.join("\n");
}
const packagePath = usefulContextPath(packageInfo?.root);
const manifestPath = usefulContextPath(packageInfo?.manifestPath);
const snapshotPath = usefulContextPath(packageInfo?.snapshotPath);
return [
`Artifact URL: ${compactArtifactUrl()}`,
packagePath ? `Package path: ${packagePath}` : null,
manifestPath ? `Manifest file: ${manifestPath}` : null,
snapshotPath ? `Snapshot file: ${snapshotPath}` : null,
`Generated at: ${snapshot?.generatedAt ?? manifest?.generatedAt ?? "unknown"}`
]
.filter((line) => Boolean(line))
.join("\n");
}
function dataAnalyticsPluginMention(packageInfo) {
const candidate = typeof packageInfo?.handoffPluginName === "string"
? packageInfo.handoffPluginName.trim()
: "";
const name = candidate && candidate.length <= 80 && !/[\r\n]/.test(candidate)
? candidate
: "Data Analytics";
return `@${name}`;
}
function refreshPrompt(manifest, snapshot, packageInfo) {
const surface = appSurfaceLabel(manifest);
const workflow = surface === "report" ? "$build-report" : "$build-dashboard";
const published = isPublishedArtifactSite(packageInfo) ? "published " : "";
return `Use ${dataAnalyticsPluginMention(packageInfo)} and invoke ${workflow} to refresh this ${published}${surface} from its declared sources using the latest available time frame. Follow that workflow's validation and delivery contract.

${promptContext(manifest, snapshot, packageInfo)}`;
}
function exportPrompt(target, manifest, snapshot, packageInfo) {
const surface = appSurfaceLabel(manifest);
const context = promptContext(manifest, snapshot, packageInfo);
const workflow = surface === "report" ? "$build-report" : "$build-dashboard";
if (target === "site") {
return `Publish this finalized ${surface} through Sites so I can share it with coworkers.

Use the current validated Data Analytics artifact as the source of truth. Create or reopen one Sites worker-starter checkout for this logical ${surface}. If the Site is currently verifiably owner-only and the user asked to widen reader access, export before changing access: pass the sole resolved creator email as site_editor_email so the exporter stores only its hash, then apply the requested reader policy. If the Site is already shared, do not infer an editor from its allowlist; omit site_editor_email so any existing seed or explicit disabled state is preserved. Pass null only when the user explicitly asks to disable editing. Call export_artifact_package with the project id and checkout path to materialize the current manifest, bounded snapshot, package metadata, and canonical artifact runtime as checkpointable source. Preserve the rendered layout, charts, tables, source details, and narrative. Checkpoint and deploy the resulting Sites version, then report its URL and snapshot timestamp.

If the local package files are unavailable from the context below, stop and ask for the report package or validated artifact payload rather than publishing an empty or stale report.

${context}`;
}
if (target === "html") {
return `Use ${dataAnalyticsPluginMention(packageInfo)} and invoke ${workflow} in portable HTML mode to export this ${surface}. Follow that workflow's HTML specification and verification contract.

${context}`;
}
if (target === "document") {
return `Use ${dataAnalyticsPluginMention(packageInfo)} and invoke $build-report in HTML mode from this ${surface}'s current content and source evidence, then invoke $report-to-google-doc. Follow both workflows' validation and delivery contracts.

${context}`;
}
if (target === "slides") {
return `Use ${dataAnalyticsPluginMention(packageInfo)} and invoke $build-report in HTML mode from this ${surface}'s current content and source evidence, then invoke $report-to-google-slides. Follow both workflows' validation and delivery contracts.

${context}`;
}
return `Use ${dataAnalyticsPluginMention(packageInfo)} and invoke $report-to-pdf to export this ${surface}. Follow that workflow's source-resolution, validation, and delivery contract.

${context}`;
}
function setOptionalCodexSearchParam(url, name, value) {
const trimmedValue = value?.trim();
if (!trimmedValue)
return;
url.searchParams.set(name, trimmedValue);
}
function codexPromptUrl(prompt, packageInfo) {
const url = new URL("codex://threads/new");
setOptionalCodexSearchParam(url, "prompt", prompt);
if (!isPublishedArtifactSite(packageInfo)) {
setOptionalCodexSearchParam(url, "originUrl", packageInfo?.originUrl);
setOptionalCodexSearchParam(url, "path", packageInfo?.root);
}
return url.toString();
}
function codexHostPromptPayload(prompt, title) {
return title ? { prompt, title } : { prompt };
}
function codexMessagePayload(prompt) {
return {
role: "user",
content: [{ type: "text", text: prompt }]
};
}
async function sendCodexPromptToHost(prompt, title) {
const hostApi = window.openai;
if (typeof hostApi?.sendFollowUpMessage === "function") {
try {
const result = await hostApi.sendFollowUpMessage(codexHostPromptPayload(prompt, title));
return result?.isError !== true;
}
catch {
return false;
}
}
if (typeof hostApi?.sendMessage === "function") {
try {
const result = await hostApi.sendMessage(codexMessagePayload(prompt));
return result?.isError !== true;
}
catch {
return false;
}
}
return null;
}
function isLocalPreviewHost() {
return ["localhost", "127.0.0.1", "::1"].includes(window.location.hostname);
}
function launchCodexDeepLink(url) {
if (isLocalPreviewHost())
return false;
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
}
catch {
}
try {
if (window.top === window) {
window.location.assign(url);
return true;
}
}
catch {
}
return linkClicked;
}
function isPublishedArtifactSite(packageInfo) {
return packageInfo?.hostedReadOnly === true || packageInfo?.deliveryMode === "site_creator";
}
async function submitCodexPrompt(prompt, title, packageInfo, onResult, environment = MCP_ARTIFACT_READER_ENVIRONMENT) {
if (environment.capabilities?.hostPrompts === false) {
onResult("This portable artifact is read-only.", true);
return;
}
if (typeof environment.sendAgentPrompt === "function") {
try {
const accepted = await environment.sendAgentPrompt(prompt, title);
onResult(accepted === false ? "ChatGPT did not accept the request." : `Sent to ChatGPT: ${title}.`, accepted === false);
}
catch {
onResult("ChatGPT did not accept the request.", true);
}
return;
}
const sentToHost = await sendPromptToHost(prompt, title);
if (sentToHost === true) {
onResult(`Sent to ChatGPT: ${title}.`, false);
return;
}
if (sentToHost === false) {
onResult("ChatGPT did not accept the request.", true);
return;
}
const clipboardFallback = isPublishedArtifactSite(packageInfo)
? copyTextToClipboard(prompt)
: null;
const launched = launchCodexPromptFallback(prompt, packageInfo);
if (clipboardFallback) {
try {
await clipboardFallback;
onResult(launched
? `Prompt copied. Opening ChatGPT Desktop: ${title}.`
: "Prompt copied. Open ChatGPT Desktop and paste it to continue.", false);
}
catch {
onResult(launched
? `Opening ChatGPT Desktop: ${title}. Prompt copy was blocked.`
: "Could not copy the prompt from this published site.", !launched);
}
return;
}
onResult(launched
? `Opening ChatGPT Desktop: ${title}.`
: "Open this app inside ChatGPT Desktop to continue.", !launched);
}
function CodexHandoffDialog({ onClose, onResult, packageInfo, request }) {
const dialogRef = useRef(null);
useModalScrollLock(true);
useEffect(() => {
const dialog = dialogRef.current;
if (dialog && !dialog.open) {
dialog.showModal();
dialog.focus({ preventScroll: true });
}
}, []);
const desktopUrl = codexPromptUrl(request.prompt, packageInfo);
const webUrl = workModeWebPromptUrl(request.prompt);
async function copyPrompt() {
try {
await copyTextToClipboard(request.prompt);
onResult("Prompt copied. Paste it into a new ChatGPT task.", false);
dialogRef.current?.close();
}
catch {
onResult("Could not copy the prompt from this Site.", true);
}
}
return (<dialog aria-describedby="codex-handoff-description" aria-labelledby="codex-handoff-title" className="native-modal codex-handoff-modal" onCancel={onClose} onClick={(event) => {
if (event.target === event.currentTarget) {
event.currentTarget.close();
}
}} onClose={onClose} ref={dialogRef} tabIndex={-1}>
<section className="modal-panel codex-handoff-panel">
<div className="modal-header">
<div>
<h2 id="codex-handoff-title">Continue in ChatGPT</h2>
<p id="codex-handoff-description">{request.description}</p>
</div>
<button aria-label="Close ChatGPT handoff" className="modal-close-button" onClick={() => dialogRef.current?.close()} type="button">
<X aria-hidden="true" size={24} strokeWidth={1.75}/>
</button>
</div>
<div className="codex-handoff-options">
<a className="codex-handoff-option" href={desktopUrl} onClick={() => onResult(`Opening ChatGPT Desktop: ${request.title}.`, false)} target="_top">
<Laptop aria-hidden="true" size={20} strokeWidth={2}/>
<strong>Open in desktop app</strong>
<ArrowUpRight aria-hidden="true" className="codex-handoff-option-arrow" size={18} strokeWidth={1.75}/>
</a>
<a className="codex-handoff-option" href={webUrl} onClick={() => onResult(`Opening ChatGPT: ${request.title}.`, false)} rel="noopener noreferrer" target="_blank">
<Globe aria-hidden="true" size={20} strokeWidth={2}/>
<strong>Open on web</strong>
<ArrowUpRight aria-hidden="true" className="codex-handoff-option-arrow" size={18} strokeWidth={1.75}/>
</a>
<button className="codex-handoff-option" onClick={() => void copyPrompt()} type="button">
<Copy aria-hidden="true" size={20} strokeWidth={2}/>
<strong>Copy prompt</strong>
</button>
</div>
</section>
</dialog>);
}
function AnalyticsTopBarFreshness({ dateLabel, disabled = false, onRefresh, status, statusLabel, surfaceLabel }) {
const tooltipId = useId();
const refreshButtonRef = useRef(null);
const [tooltipLeft, setTooltipLeft] = useState(12);
const refreshLabel = dateLabel === "Unknown" ? "Refresh" : dateLabel;
const statusDescription = statusLabel ? ` Status: ${statusLabel}.` : "";
const refreshDescription = disabled
? `Finish editing to refresh this ${surfaceLabel}.${statusDescription}`
: dateLabel === "Unknown"
? `Ask ChatGPT to refresh this ${surfaceLabel}. Last refresh date unavailable.${statusDescription}`
: `Last refreshed ${dateLabel}. Ask ChatGPT to refresh this ${surfaceLabel}.${statusDescription}`;
const positionRefreshTooltip = useCallback(() => {
const buttonRect = refreshButtonRef.current?.getBoundingClientRect();
if (!buttonRect) return;
const viewportPadding = 12;
const tooltipWidth = Math.min(320, Math.max(0, window.innerWidth - (viewportPadding * 2)));
const maxLeft = Math.max(viewportPadding, window.innerWidth - tooltipWidth - viewportPadding);
setTooltipLeft(Math.min(Math.max(buttonRect.left, viewportPadding), maxLeft));
}, []);
useEffect(() => {
window.addEventListener("resize", positionRefreshTooltip);
return () => window.removeEventListener("resize", positionRefreshTooltip);
}, [positionRefreshTooltip]);
if (typeof onRefresh !== "function") {
const snapshotTitle = dateLabel === "Unknown"
? "Published snapshot. Update from the source Data Analytics run."
: `Published snapshot. Last updated ${dateLabel}. Update from the source Data Analytics run.`;
return (<div className="analytics-top-bar-freshness">
<div aria-label={snapshotTitle} className="analytics-top-bar-refresh-label" title={snapshotTitle}>
<span>{dateLabel === "Unknown" ? "Snapshot" : dateLabel}</span>
{statusLabel ? <span className={`snapshot-status ${status}`}>{statusLabel}</span> : null}
</div>
</div>);
}
return (<div className="analytics-top-bar-freshness">
<span className="top-bar-refresh-tooltip-anchor" onFocus={positionRefreshTooltip} onMouseEnter={positionRefreshTooltip}>
<button ref={refreshButtonRef} aria-describedby={tooltipId} aria-label={`Refresh ${surfaceLabel}`} className="top-bar-refresh-datetime" disabled={disabled} onClick={onRefresh} type="button">
<span className="top-bar-refresh-text">{refreshLabel}</span>
</button>
<span className="top-bar-refresh-tooltip" id={tooltipId} role="tooltip" style={{ left: tooltipLeft }}>{refreshDescription}</span>
</span>
{statusLabel ? <span className={`snapshot-status ${status}`}>{statusLabel}</span> : null}
</div>);
}
function AnalyticsReaderFreshness({ dateLabel, status, statusLabel }) {
return (<div className="analytics-top-bar-freshness" aria-label={`Last updated ${dateLabel}`}>
<span className="top-bar-button top-bar-button-ghost top-bar-refresh-button analytics-reader-freshness">
<span className="top-bar-refresh-text">{dateLabel}</span>
{statusLabel ? <span className={`snapshot-status ${status}`}>{statusLabel}</span> : null}
</span>
</div>);
}
function AnalyticsTopBar({ capabilities, chrome = "full", environment, isEditMode, isSavingEdit = false, onCancelEdit, manifest, onCopyResult, onEdit, onRequestFullscreen, onSaveEdit, onTitleChange, packageInfo, snapshot, title }) {
const [isExportMenuOpen, setIsExportMenuOpen] = useState(false);
const [handoffRequest, setHandoffRequest] = useState(null);
const { closeMenu, fixedMenuStyle, handleMenuButtonKeyDown, handleMenuKeyDown, menuButtonRef, menuMotionClass, menuRef, toggleMenu, shouldRenderMenu } = useDashboardMenu(isExportMenuOpen, setIsExportMenuOpen);
const exportTargets = exportTargetsForCapabilities(capabilities);
const lastRefresh = formatDate(snapshot?.generatedAt ?? manifest?.generatedAt);
const statusLabel = snapshotStatusLabel(snapshot?.status);
const dateLabel = lastRefresh;
const showStatusLabel = manifest?.surface !== "report" && statusLabel;
const showActions = chrome === "full";
const showReaderFreshness = chrome === "reader";
const showInlineExpand = chrome === "inline" && typeof onRequestFullscreen === "function";
function requestCodexAction(prompt, actionTitle, description) {
if (isPublishedArtifactSite(packageInfo)) {
setHandoffRequest({ description, prompt, title: actionTitle });
return;
}
void submitCodexPrompt(prompt, actionTitle, packageInfo, onCopyResult, environment);
}
function requestRefresh() {
requestCodexAction(
refreshPrompt(manifest, snapshot, packageInfo),
`Refresh ${appSurfaceLabel(manifest)}`,
`Refresh this ${appSurfaceLabel(manifest)} with the latest available data.`
);
}
function requestExport(target) {
closeMenu();
requestCodexAction(
exportPrompt(target, manifest, snapshot, packageInfo),
EXPORT_TARGET_LABELS[target],
`${EXPORT_TARGET_HANDOFF_DESCRIPTIONS[target]} ${appSurfaceLabel(manifest)}.`
);
}
return (<>
<div className="analytics-top-bar" aria-label={`${appSurfaceLabel(manifest)} actions`}>
<div className="analytics-top-bar-leading">
<div className="analytics-top-bar-title">
<EditablePageTitle ariaLabel={`Edit ${appSurfaceLabel(manifest)} title`} isEditMode={isEditMode} onChange={onTitleChange} onRequestEditMode={onEdit} placeholder={composePageTitle(manifest)} readOnly={!showActions || !capabilities.canEdit} title={title}/>
</div>
{showActions ? <AnalyticsTopBarFreshness dateLabel={dateLabel} disabled={isEditMode} onRefresh={capabilities.canRefresh ? requestRefresh : undefined} status={snapshot?.status} statusLabel={showStatusLabel ? statusLabel : null} surfaceLabel={appSurfaceLabel(manifest)}/> : null}
</div>
{showReaderFreshness ? (<div className="analytics-top-bar-actions">
<AnalyticsReaderFreshness dateLabel={dateLabel} status={snapshot?.status} statusLabel={showStatusLabel ? statusLabel : null}/>
</div>) : showInlineExpand ? (<div className="analytics-top-bar-actions">
<button aria-label={`Expand ${appSurfaceLabel(manifest)} fullscreen`} className="top-bar-button" onClick={onRequestFullscreen} title={`Expand ${appSurfaceLabel(manifest)} fullscreen`} type="button">
<Expand aria-hidden="true" size={14} strokeWidth={2}/>
<span>Expand</span>
</button>
</div>) : showActions ? (<div className="analytics-top-bar-actions">
{isEditMode && capabilities.canEdit ? (<>
<button className="top-bar-button" disabled={isSavingEdit} onClick={onCancelEdit} type="button">
<span>Cancel</span>
</button>
<button aria-busy={isSavingEdit} className="top-bar-button top-bar-button-primary" disabled={isSavingEdit} onClick={onSaveEdit} type="button">
{isSavingEdit ? <RefreshCw aria-hidden="true" className="top-bar-button-spinner" size={14} strokeWidth={2}/> : null}
<span>{isSavingEdit ? "Saving…" : "Save changes"}</span>
</button>
</>) : (<>
{exportTargets.length ? (
<div className="export-menu">
<button ref={menuButtonRef} aria-expanded={isExportMenuOpen} aria-haspopup="menu" aria-label={`More ${appSurfaceLabel(manifest)} actions`} className="top-bar-button top-bar-button-ghost top-bar-overflow-button" onClick={toggleMenu} onKeyDown={handleMenuButtonKeyDown} type="button">
<Ellipsis aria-hidden="true" size={18} strokeWidth={2}/>
</button>
{shouldRenderMenu ? (<div ref={menuRef} className={`export-menu-list menu-surface ${menuMotionClass}`} onKeyDown={handleMenuKeyDown} role="menu" style={fixedMenuStyle}>
{exportTargets.map((target) => (<button className="export-menu-item" key={target} onClick={() => requestExport(target)} role="menuitem" type="button">
{EXPORT_TARGET_ICONS[target]}
{EXPORT_TARGET_LABELS[target]}
</button>))}
</div>) : null}
</div>
): null}
{capabilities.canEdit ? (
<button className="top-bar-button top-bar-edit-button" onClick={onEdit} type="button">
<Pencil aria-hidden="true" size={16} strokeWidth={2}/>
<span>Edit</span>
</button>
): null}
</>)}
</div>) : null}
</div>
{handoffRequest ? (<CodexHandoffDialog onClose={() => setHandoffRequest(null)} onResult={onCopyResult} packageInfo={packageInfo} request={handoffRequest}/>) : null}
</>);
}
export function ArtifactReader({ artifact, displayMode = "fullscreen", environment: requestedEnvironment, onReady, onRequestFullscreen } = {}) {
const environment = useMemo(() => normalizeReaderEnvironment(requestedEnvironment), [requestedEnvironment]);
const normalizedArtifact = useMemo(() => normalizeArtifact(artifact), [artifact]);
const { manifest, snapshot } = normalizedArtifact;
const packageInfo = useMemo(() => withHostedBootstrap(normalizedArtifact.packageInfo), [normalizedArtifact.packageInfo]);
const [hostedPresentation, setHostedPresentation] = useState(null);
const [selectedFilters, setSelectedFilters] = useState({});
const [tableColumnWidths, setTableColumnWidths] = useState({});
const [pageTitle, setPageTitle] = useState("");
const [chartTextOverrides, setChartTextOverrides] = useState({});
const [chartSpecOverrides, setChartSpecOverrides] = useState({});
const [chartTypeOverrides, setChartTypeOverrides] = useState({});
const [tableTextOverrides, setTableTextOverrides] = useState({});
const [blockTextOverrides, setBlockTextOverrides] = useState({});
const [deletedReportBlockIds, setDeletedReportBlockIds] = useState([]);
const [openMenuChartId, setOpenMenuChartId] = useState(null);
const [openMenuTableId, setOpenMenuTableId] = useState(null);
const [openMenuBlockId, setOpenMenuBlockId] = useState(null);
const [cardSourceModal, setCardSourceModal] = useState(null);
const [chartModal, setChartModal] = useState(null);
const [tableModal, setTableModal] = useState(null);
const [copyMessage, setCopyMessage] = useState(null);
const [isEditMode, setIsEditMode] = useState(false);
const [isSavingEdit, setIsSavingEdit] = useState(false);
const [layoutResetKey, setLayoutResetKey] = useState(0);
const editSnapshotRef = useRef(null);
const layoutDraftsRef = useRef({ dashboard: null, report: null });
const deletedReportBlockIdsRef = useRef([]);
const readyCallbackRef = useRef(onReady);
const readyArtifactRef = useRef(null);
useEffect(() => {
readyCallbackRef.current = onReady;
}, [onReady]);
useEffect(() => {
if (!artifact || readyArtifactRef.current === artifact)
return;
let cancelled = false;
const frame = window.requestAnimationFrame(() => {
if (cancelled)
return;
readyArtifactRef.current = artifact;
readyCallbackRef.current?.();
});
return () => {
cancelled = true;
window.cancelAnimationFrame(frame);
};
}, [artifact]);
useEffect(() => {
let cancelled = false;
if (!isHostedPresentationSite(packageInfo)) {
setHostedPresentation(null);
return () => {
cancelled = true;
};
}
void loadHostedPresentation().then((presentation) => {
if (!cancelled) {
setHostedPresentation(presentation && typeof presentation === "object" ? presentation : null);
}
});
return () => {
cancelled = true;
};
}, [packageInfo]);
const filters = manifest?.filters ?? EMPTY_FILTERS;
const cards = manifest?.cards ?? EMPTY_CARDS;
const charts = manifest?.charts ?? EMPTY_CHARTS;
const tables = manifest?.tables ?? EMPTY_TABLES;
const reportBlocks = manifest?.blocks ?? EMPTY_REPORT_BLOCKS;
const globalFilters = useMemo(() => getGlobalFilters(filters, cards, charts, tables), [cards, charts, filters, tables]);
const accessIssues = snapshot?.accessIssues ?? EMPTY_ACCESS_ISSUES;
const capabilities = useMemo(() => artifactCapabilities(packageInfo, environment, hostedPresentation), [environment, hostedPresentation, packageInfo]);
const storageKey = capabilities.canPersistState ? contentLayoutKey(manifest) : null;
const chartTextStorageKey = capabilities.canPersistState ? chartTextKey(manifest) : null;
const chartSpecStorageKey = capabilities.canPersistState ? chartSpecKey(manifest) : null;
const chartTypeStorageKey = capabilities.canPersistState ? chartTypeKey(manifest) : null;
const pageTitleTextStorageKey = capabilities.canPersistState ? pageTitleTextKey(manifest) : null;
const tableTextStorageKey = capabilities.canPersistState ? tableTextKey(manifest) : null;
const blockTextStorageKey = capabilities.canPersistState ? blockTextKey(manifest) : null;
const deletedReportBlockStorageKey = capabilities.canPersistState ? deletedReportBlocksKey(manifest) : null;
const tableColumnWidthStorageKey = capabilities.canPersistState ? tableColumnWidthKey(manifest) : null;
const reportStorageKey = capabilities.canPersistState ? reportContentLayoutKey(manifest) : null;
const isReport = manifest?.surface === "report";
const activeSurfaceFilters = isReport ? filters : globalFilters;
const usesHostedPresentation = isHostedPresentationSite(packageInfo);
const hostedOverrides = usesHostedPresentation && hostedPresentation?.overrides && typeof hostedPresentation.overrides === "object"
? hostedPresentation.overrides
: {};
const activeEditMode = capabilities.canEdit && isEditMode;
const activeLayoutEditMode = activeEditMode && capabilities.canReorderContent;
const canEditChartSpec = capabilities.canEditChartSpec && (!usesHostedPresentation || activeEditMode);
const canDeleteBlocks = capabilities.canDelete && (!usesHostedPresentation || activeEditMode);
const hostedDashboardLayout = activeEditMode && layoutDraftsRef.current.dashboard
? layoutDraftsRef.current.dashboard
: hostedOverrides.dashboardLayout ?? [];
const hostedReportLayout = activeEditMode && layoutDraftsRef.current.report
? layoutDraftsRef.current.report
: hostedOverrides.reportLayout ?? [];
const requestEditMode = capabilities.canEdit ? beginEditMode : undefined;
const effectiveRequestFullscreen = capabilities.canHostFullscreen
? onRequestFullscreen ?? environment.requestFullscreen
: undefined;
const topBarChrome = environment.mode === "portable"
? "reader"
: displayMode === "inline"
? "inline"
: "full";
const readerContextValue = useMemo(() => ({ capabilities, environment }), [capabilities, environment]);
useEffect(() => {
document.title = pageTitle.trim() || composePageTitle(manifest);
}, [manifest, pageTitle]);
useEffect(() => {
if (!capabilities.canEdit && isEditMode) {
setIsEditMode(false);
}
}, [capabilities.canEdit, isEditMode]);
useEffect(() => {
deletedReportBlockIdsRef.current = deletedReportBlockIds;
}, [deletedReportBlockIds]);
const cardsById = useMemo(() => new Map(cards.map((card) => [card.id, card])), [cards]);
const chartsById = useMemo(() => new Map(charts.map((chart) => [chart.id, chart])), [charts]);
const tablesById = useMemo(() => new Map(tables.map((table) => [table.id, table])), [tables]);
const reportGridBlocks = reportBlocks;
const knownDeletableReportIds = useMemo(() => {
const ids = [];
for (const block of reportGridBlocks) {
ids.push(block.id);
if (block.type === "metric-strip") {
for (const cardId of block.cardIds ?? []) {
ids.push(metricCardBlockId(block.id, cardId));
}
}
}
return new Set(ids);
}, [reportGridBlocks]);
const visibleReportGridBlocks = useMemo(() => {
if (!deletedReportBlockIds.length)
return reportGridBlocks;
const deletedIds = new Set(deletedReportBlockIds);
return reportGridBlocks.filter((block) => !deletedIds.has(block.id));
}, [deletedReportBlockIds, reportGridBlocks]);
useEffect(() => {
if (usesHostedPresentation) {
const nextIds = Array.isArray(hostedOverrides.deletedReportBlockIds)
? hostedOverrides.deletedReportBlockIds.filter((id) => typeof id === "string" && knownDeletableReportIds.has(id))
: [];
deletedReportBlockIdsRef.current = nextIds;
setDeletedReportBlockIds(nextIds);
return;
}
if (!capabilities.canDelete || !reportGridBlocks.length || !deletedReportBlockStorageKey) {
deletedReportBlockIdsRef.current = [];
setDeletedReportBlockIds([]);
return;
}
const stored = readPersistedValue(deletedReportBlockStorageKey);
if (!stored) {
deletedReportBlockIdsRef.current = [];
setDeletedReportBlockIds([]);
return;
}
try {
const parsed = JSON.parse(stored);
const nextIds = Array.isArray(parsed)
? parsed.filter((id) => typeof id === "string" && knownDeletableReportIds.has(id))
: [];
deletedReportBlockIdsRef.current = nextIds;
setDeletedReportBlockIds(nextIds);
}
catch {
deletedReportBlockIdsRef.current = [];
setDeletedReportBlockIds([]);
}
}, [capabilities.canDelete, deletedReportBlockStorageKey, hostedOverrides.deletedReportBlockIds, knownDeletableReportIds, reportGridBlocks, usesHostedPresentation]);
useEffect(() => {
if (usesHostedPresentation) {
setTableColumnWidths({});
return;
}
if (!tables.length || !tableColumnWidthStorageKey) {
setTableColumnWidths({});
return;
}
const stored = readPersistedValue(tableColumnWidthStorageKey);
if (!stored) {
setTableColumnWidths({});
return;
}
try {
const parsed = JSON.parse(stored);
const tableFields = new Map(tables.map((table) => [table.id, new Set(table.columns.map((column) => column.field))]));
const nextState = {};
if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
for (const [tableId, rawWidths] of Object.entries(parsed)) {
const fields = tableFields.get(tableId);
if (!fields || !rawWidths || typeof rawWidths !== "object" || Array.isArray(rawWidths)) {
continue;
}
const nextWidths = {};
for (const [field, rawWidth] of Object.entries(rawWidths)) {
const width = typeof rawWidth === "number" ? rawWidth : Number(rawWidth);
if (fields.has(field) && Number.isFinite(width)) {
nextWidths[field] = clamp(Math.round(width), TABLE_COLUMN_MIN_WIDTH, TABLE_COLUMN_MAX_WIDTH);
}
}
if (Object.keys(nextWidths).length) {
nextState[tableId] = nextWidths;
}
}
}
setTableColumnWidths(nextState);
}
catch {
setTableColumnWidths({});
}
}, [tableColumnWidthStorageKey, tables, usesHostedPresentation]);
useEffect(() => {
const fallbackTitle = composePageTitle(manifest);
if (usesHostedPresentation) {
setPageTitle(typeof hostedOverrides.pageTitle === "string" ? hostedOverrides.pageTitle : fallbackTitle);
return;
}
if (!capabilities.canEdit || !pageTitleTextStorageKey) {
setPageTitle(fallbackTitle);
return;
}
const storedTitle = readPersistedValue(pageTitleTextStorageKey);
setPageTitle(storedTitle ?? fallbackTitle);
}, [capabilities.canEdit, hostedOverrides.pageTitle, manifest, pageTitleTextStorageKey, usesHostedPresentation]);
useEffect(() => {
if ((!usesHostedPresentation && !capabilities.canEdit) || !charts.length || (!usesHostedPresentation && !chartTextStorageKey)) {
setChartTextOverrides({});
return;
}
const stored = usesHostedPresentation
? JSON.stringify(hostedOverrides.chartTextOverrides ?? {})
: readPersistedValue(chartTextStorageKey);
if (!stored) {
setChartTextOverrides({});
return;
}
try {
const parsed = JSON.parse(stored);
const knownIds = new Set(charts.map((chart) => chart.id));
const nextOverrides = {};
for (const [chartId, override] of Object.entries(parsed)) {
if (knownIds.has(chartId)
&& override
&& typeof override === "object"
&& (typeof override.headerMarkdown === "string"
|| typeof override.title === "string"
|| typeof override.subtitle === "string")) {
nextOverrides[chartId] = {
...(typeof override.headerMarkdown === "string" ? { headerMarkdown: override.headerMarkdown } : {}),
...(typeof override.title === "string" ? { title: override.title } : {}),
...(typeof override.subtitle === "string" ? { subtitle: override.subtitle } : {})
};
}
}
setChartTextOverrides(nextOverrides);
}
catch {
setChartTextOverrides({});
}
}, [capabilities.canEdit, chartTextStorageKey, charts, hostedOverrides.chartTextOverrides, usesHostedPresentation]);
useEffect(() => {
if ((!usesHostedPresentation && !capabilities.canEdit) || !charts.length || (!usesHostedPresentation && !chartSpecStorageKey)) {
setChartSpecOverrides({});
return;
}
const stored = usesHostedPresentation
? JSON.stringify(hostedOverrides.chartSpecOverrides ?? {})
: readPersistedValue(chartSpecStorageKey);
if (!stored) {
setChartSpecOverrides({});
return;
}
try {
const parsed = JSON.parse(stored);
const chartsByIdForStorage = new Map(charts.map((chart) => [chart.id, chart]));
const nextOverrides = {};
if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
for (const [chartId, override] of Object.entries(parsed)) {
const chart = chartsByIdForStorage.get(chartId);
if (!chart || !override || typeof override !== "object" || Array.isArray(override)) {
continue;
}
const sanitized = {};
if (sharedIsChartType(override.type)) {
sanitized.type = override.type;
}
const chartFields = new Set(chartUsedFields(chart));
if (typeof override.xField === "string" && chartFields.has(override.xField)) {
sanitized.xField = override.xField;
}
if (Array.isArray(override.series)) {
const series = override.series
.filter((entry) => entry && typeof entry === "object" && !Array.isArray(entry) && typeof entry.field === "string" && chartFields.has(entry.field))
.map((entry) => ({
field: entry.field,
...(typeof entry.label === "string" ? { label: entry.label } : {}),
...(typeof entry.color === "string" ? { color: entry.color } : {}),
...(typeof entry.lineStyle === "string" ? { lineStyle: entry.lineStyle } : {}),
...(typeof entry.role === "string" ? { role: entry.role } : {}),
...(typeof entry.semanticRole === "string" ? { semanticRole: entry.semanticRole } : {})
}));
if (series.length) {
sanitized.series = series;
}
}
if (override.encodings && typeof override.encodings === "object" && !Array.isArray(override.encodings)) {
const sizeEncoding = override.encodings.size;
if (sizeEncoding && typeof sizeEncoding === "object" && !Array.isArray(sizeEncoding) && typeof sizeEncoding.field === "string" && chartFields.has(sizeEncoding.field)) {
sanitized.encodings = { size: { ...sizeEncoding, field: sizeEncoding.field } };
}
}
if (override.settings && typeof override.settings === "object" && !Array.isArray(override.settings)) {
sanitized.settings = {
...(override.settings.orientation === "horizontal" || override.settings.orientation === "vertical" ? { orientation: override.settings.orientation } : {}),
...(["grouped", "stacked", "stacked100"].includes(override.settings.groupMode) ? { groupMode: override.settings.groupMode } : {}),
};
if (!Object.keys(sanitized.settings).length) {
delete sanitized.settings;
}
}
if (Object.keys(sanitized).length) {
nextOverrides[chartId] = sanitized;
}
}
}
setChartSpecOverrides(nextOverrides);
}
catch {
setChartSpecOverrides({});
}
}, [capabilities.canEdit, chartSpecStorageKey, charts, hostedOverrides.chartSpecOverrides, usesHostedPresentation]);
useEffect(() => {
if (usesHostedPresentation) {
setChartTypeOverrides({});
return;
}
if (!capabilities.canEdit || !charts.length || !chartTypeStorageKey) {
setChartTypeOverrides({});
return;
}
const stored = readPersistedValue(chartTypeStorageKey);
if (!stored) {
setChartTypeOverrides({});
return;
}
try {
const parsed = JSON.parse(stored);
const knownIds = new Set(charts.map((chart) => chart.id));
const nextOverrides = {};
for (const [chartId, chartType] of Object.entries(parsed)) {
if (knownIds.has(chartId) && isChartType(chartType)) {
nextOverrides[chartId] = chartType;
}
}
setChartTypeOverrides(nextOverrides);
}
catch {
setChartTypeOverrides({});
}
}, [capabilities.canEdit, chartTypeStorageKey, charts, usesHostedPresentation]);
useEffect(() => {
if ((!usesHostedPresentation && !capabilities.canEdit) || !tables.length || (!usesHostedPresentation && !tableTextStorageKey)) {
setTableTextOverrides({});
return;
}
const stored = usesHostedPresentation
? JSON.stringify(hostedOverrides.tableTextOverrides ?? {})
: readPersistedValue(tableTextStorageKey);
if (!stored) {
setTableTextOverrides({});
return;
}
try {
const parsed = JSON.parse(stored);
const knownIds = new Set(tables.map((table) => table.id));
const nextOverrides = {};
for (const [tableId, override] of Object.entries(parsed)) {
if (knownIds.has(tableId)
&& override
&& typeof override === "object"
&& typeof override.headerMarkdown === "string") {
nextOverrides[tableId] = { headerMarkdown: override.headerMarkdown };
}
}
setTableTextOverrides(nextOverrides);
}
catch {
setTableTextOverrides({});
}
}, [capabilities.canEdit, hostedOverrides.tableTextOverrides, tableTextStorageKey, tables, usesHostedPresentation]);
useEffect(() => {
if ((!usesHostedPresentation && !capabilities.canEdit) || !reportGridBlocks.length || (!usesHostedPresentation && !blockTextStorageKey)) {
setBlockTextOverrides({});
return;
}
const stored = usesHostedPresentation
? JSON.stringify(hostedOverrides.blockTextOverrides ?? {})
: readPersistedValue(blockTextStorageKey);
if (!stored) {
setBlockTextOverrides({});
return;
}
try {
const parsed = JSON.parse(stored);
const knownIds = new Set(reportGridBlocks.map((block) => block.id));
const nextOverrides = {};
for (const [blockId, override] of Object.entries(parsed)) {
if (knownIds.has(blockId) && override && typeof override === "object") {
const nextOverride = {
...(visibleString(override.bodyMarkdown) ? { bodyMarkdown: override.bodyMarkdown } : {}),
...(visibleString(override.html) ? { html: override.html } : {})
};
if (Object.keys(nextOverride).length)
nextOverrides[blockId] = nextOverride;
}
}
setBlockTextOverrides(nextOverrides);
}
catch {
setBlockTextOverrides({});
}
}, [blockTextStorageKey, capabilities.canEdit, hostedOverrides.blockTextOverrides, reportGridBlocks, usesHostedPresentation]);
const filterDefaults = useMemo(() => {
return Object.fromEntries(activeSurfaceFilters.map((filter) => [filter.id, filter.defaultValue ?? "all"]));
}, [activeSurfaceFilters]);
useEffect(() => {
setSelectedFilters((current) => ({ ...filterDefaults, ...current }));
}, [filterDefaults]);
useEffect(() => {
if (!copyMessage)
return;
const timeout = window.setTimeout(() => setCopyMessage(null), 2600);
return () => window.clearTimeout(timeout);
}, [copyMessage]);
function persistEditableState() {
if (pageTitleTextStorageKey) {
writePersistedValue(pageTitleTextStorageKey, pageTitle);
}
if (chartTextStorageKey) {
writePersistedValue(chartTextStorageKey, JSON.stringify(chartTextOverrides));
}
if (chartSpecStorageKey) {
writePersistedValue(chartSpecStorageKey, JSON.stringify(chartSpecOverrides));
}
if (chartTypeStorageKey) {
writePersistedValue(chartTypeStorageKey, JSON.stringify(chartTypeOverrides));
}
if (tableTextStorageKey) {
writePersistedValue(tableTextStorageKey, JSON.stringify(tableTextOverrides));
}
if (blockTextStorageKey) {
writePersistedValue(blockTextStorageKey, JSON.stringify(blockTextOverrides));
}
if (deletedReportBlockStorageKey) {
writePersistedValue(deletedReportBlockStorageKey, JSON.stringify(deletedReportBlockIds));
}
if (tableColumnWidthStorageKey) {
writePersistedValue(tableColumnWidthStorageKey, JSON.stringify(tableColumnWidths));
}
if (storageKey && layoutDraftsRef.current.dashboard) {
writePersistedValue(storageKey, JSON.stringify(layoutDraftsRef.current.dashboard));
}
if (reportStorageKey && layoutDraftsRef.current.report) {
writePersistedValue(reportStorageKey, JSON.stringify(layoutDraftsRef.current.report));
}
}
function closeInlineMenus() {
setOpenMenuBlockId(null);
setOpenMenuChartId(null);
setOpenMenuTableId(null);
}
function beginEditMode() {
if (isEditMode)
return;
editSnapshotRef.current = {
blockTextOverrides: cloneSerializable(blockTextOverrides),
chartSpecOverrides: cloneSerializable(chartSpecOverrides),
chartTextOverrides: cloneSerializable(chartTextOverrides),
chartTypeOverrides: cloneSerializable(chartTypeOverrides),
deletedReportBlockIds: [...deletedReportBlockIds],
pageTitle,
tableColumnWidths: cloneSerializable(tableColumnWidths),
tableTextOverrides: cloneSerializable(tableTextOverrides)
};
closeInlineMenus();
setIsEditMode(true);
}
function cancelEditMode() {
if (isSavingEdit)
return;
const snapshotState = editSnapshotRef.current;
if (snapshotState) {
setBlockTextOverrides(cloneSerializable(snapshotState.blockTextOverrides));
setChartSpecOverrides(cloneSerializable(snapshotState.chartSpecOverrides ?? {}));
setChartTextOverrides(cloneSerializable(snapshotState.chartTextOverrides));
setChartTypeOverrides(cloneSerializable(snapshotState.chartTypeOverrides));
const restoredDeletedIds = [...snapshotState.deletedReportBlockIds];
deletedReportBlockIdsRef.current = restoredDeletedIds;
setDeletedReportBlockIds(restoredDeletedIds);
setPageTitle(snapshotState.pageTitle);
setTableColumnWidths(cloneSerializable(snapshotState.tableColumnWidths));
setTableTextOverrides(cloneSerializable(snapshotState.tableTextOverrides));
}
editSnapshotRef.current = null;
layoutDraftsRef.current = { dashboard: null, report: null };
closeInlineMenus();
setIsEditMode(false);
setLayoutResetKey((current) => current + 1);
}
async function saveEditMode() {
if (isSavingEdit)
return;
setIsSavingEdit(true);
try {
if (usesHostedPresentation) {
const blockMarkdownOverrides = Object.fromEntries(Object.entries(blockTextOverrides)
.filter(([, override]) => override && typeof override.bodyMarkdown === "string")
.map(([blockId, override]) => [blockId, { bodyMarkdown: override.bodyMarkdown }]));
const overrides = {
...hostedOverrides,
chartSpecOverrides,
chartTextOverrides,
tableTextOverrides,
blockTextOverrides: blockMarkdownOverrides,
...(layoutDraftsRef.current.dashboard ? { dashboardLayout: layoutDraftsRef.current.dashboard } : {}),
...(layoutDraftsRef.current.report ? { reportLayout: layoutDraftsRef.current.report } : {})
};
const generatedTitle = composePageTitle(manifest);
if (pageTitle !== generatedTitle)
overrides.pageTitle = pageTitle;
else
delete overrides.pageTitle;
if (deletedReportBlockIds.length)
overrides.deletedReportBlockIds = [...deletedReportBlockIds];
else
delete overrides.deletedReportBlockIds;
const savedPresentation = await saveHostedPresentation({
artifactId: hostedPresentation?.artifactId,
revision: hostedPresentation?.revision,
overrides
});
setHostedPresentation(savedPresentation);
setCopyMessage({ isError: false, message: "Changes saved to this Site." });
}
else {
persistEditableState();
}
editSnapshotRef.current = null;
layoutDraftsRef.current = { dashboard: null, report: null };
closeInlineMenus();
setIsEditMode(false);
}
catch (saveError) {
setCopyMessage({
isError: true,
message: saveError instanceof Error ? saveError.message : "Could not save Site changes."
});
}
finally {
setIsSavingEdit(false);
}
}
function recordDashboardLayoutDraft(nextItems, reason) {
layoutDraftsRef.current.dashboard = mergeVisibleLayoutPreservingHidden(
layoutDraftsRef.current.dashboard,
nextItems,
deletedReportBlockIdsRef.current,
reason === "normalize"
);
}
function recordReportLayoutDraft(nextItems, reason) {
layoutDraftsRef.current.report = mergeVisibleLayoutPreservingHidden(
layoutDraftsRef.current.report,
nextItems,
deletedReportBlockIdsRef.current,
reason === "normalize"
);
}
function updatePageTitle(nextTitle) {
setPageTitle(nextTitle);
if (!usesHostedPresentation && !isEditMode && pageTitleTextStorageKey) {
writePersistedValue(pageTitleTextStorageKey, nextTitle);
}
}
function updateChartText(chartId, nextText) {
setChartTextOverrides((current) => {
const merged = {
...current,
[chartId]: {
...current[chartId],
...nextText
}
};
if (!usesHostedPresentation && !isEditMode && chartTextStorageKey) {
writePersistedValue(chartTextStorageKey, JSON.stringify(merged));
}
return merged;
});
}
function updateChartType(chartId, nextType) {
setChartTypeOverrides((current) => {
const originalType = charts.find((chart) => chart.id === chartId)?.type;
const merged = { ...current };
if (!originalType || nextType === originalType) {
delete merged[chartId];
}
else {
merged[chartId] = nextType;
}
if (!usesHostedPresentation && !isEditMode && chartTypeStorageKey) {
writePersistedValue(chartTypeStorageKey, JSON.stringify(merged));
}
return merged;
});
}
function updateChartSpec(chartId, widgetSpec) {
const chart = charts.find((candidate) => candidate.id === chartId);
if (!chart)
return;
if (!widgetSpec) {
setChartSpecOverrides((current) => {
const merged = { ...current };
delete merged[chartId];
if (!usesHostedPresentation && !isEditMode && chartSpecStorageKey) {
writePersistedValue(chartSpecStorageKey, JSON.stringify(merged));
}
return merged;
});
setChartTypeOverrides((current) => {
const merged = { ...current };
delete merged[chartId];
if (!usesHostedPresentation && !isEditMode && chartTypeStorageKey) {
writePersistedValue(chartTypeStorageKey, JSON.stringify(merged));
}
return merged;
});
return;
}
const nextOverride = chartSpecOverrideFromWidgetSpec(chart, widgetSpec);
const nextType = sharedIsChartType(nextOverride.type) ? nextOverride.type : chart.type;
setChartSpecOverrides((current) => {
const merged = { ...current };
if (Object.keys(nextOverride).length) {
merged[chartId] = nextOverride;
}
else {
delete merged[chartId];
}
if (!usesHostedPresentation && !isEditMode && chartSpecStorageKey) {
writePersistedValue(chartSpecStorageKey, JSON.stringify(merged));
}
return merged;
});
setChartTypeOverrides((current) => {
const merged = { ...current };
if (nextType === chart.type) {
delete merged[chartId];
}
else {
merged[chartId] = nextType;
}
if (!usesHostedPresentation && !isEditMode && chartTypeStorageKey) {
writePersistedValue(chartTypeStorageKey, JSON.stringify(merged));
}
return merged;
});
}
function updateTableColumnWidths(tableId, nextWidths, options = {}) {
setTableColumnWidths((current) => {
const tableSpec = tablesById.get(tableId);
if (!tableSpec)
return current;
const validFields = new Set(tableSpec.columns.map((column) => column.field));
const sanitizedWidths = {};
for (const [field, rawWidth] of Object.entries(nextWidths)) {
const width = typeof rawWidth === "number" ? rawWidth : Number(rawWidth);
if (validFields.has(field) && Number.isFinite(width)) {
sanitizedWidths[field] = clamp(Math.round(width), TABLE_COLUMN_MIN_WIDTH, TABLE_COLUMN_MAX_WIDTH);
}
}
const merged = { ...current };
if (Object.keys(sanitizedWidths).length) {
merged[tableId] = sanitizedWidths;
}
else {
delete merged[tableId];
}
if (!usesHostedPresentation && !isEditMode && options.persist !== false && tableColumnWidthStorageKey) {
writePersistedValue(tableColumnWidthStorageKey, JSON.stringify(merged));
}
return merged;
});
}
function updateTableText(tableId, nextText) {
setTableTextOverrides((current) => {
const merged = {
...current,
[tableId]: {
...current[tableId],
...nextText
}
};
if (!usesHostedPresentation && !isEditMode && tableTextStorageKey) {
writePersistedValue(tableTextStorageKey, JSON.stringify(merged));
}
return merged;
});
}
function updateBlockText(blockId, nextText) {
setBlockTextOverrides((current) => {
const nextBlockOverride = {
...current[blockId],
...nextText
};
if ("bodyMarkdown" in nextText && !visibleString(nextText.bodyMarkdown)) {
delete nextBlockOverride.bodyMarkdown;
}
if ("html" in nextText && !visibleString(nextText.html)) {
delete nextBlockOverride.html;
}
const merged = { ...current };
if (Object.keys(nextBlockOverride).length)
merged[blockId] = nextBlockOverride;
else
delete merged[blockId];
if (!usesHostedPresentation && !isEditMode && blockTextStorageKey) {
writePersistedValue(blockTextStorageKey, JSON.stringify(merged));
}
return merged;
});
}
function deleteReportBlocks(blockIds) {
const idsToDelete = [...new Set(blockIds)];
if (!idsToDelete.length)
return;
setDeletedReportBlockIds((current) => {
const existingIds = new Set(current);
const nextIds = [...current];
for (const blockId of idsToDelete) {
if (!existingIds.has(blockId)) {
nextIds.push(blockId);
}
}
if (nextIds.length === current.length)
return current;
deletedReportBlockIdsRef.current = nextIds;
if (!usesHostedPresentation && !isEditMode && deletedReportBlockStorageKey) {
writePersistedValue(deletedReportBlockStorageKey, JSON.stringify(nextIds));
}
return nextIds;
});
setOpenMenuBlockId(null);
setOpenMenuChartId(null);
setOpenMenuTableId(null);
}
function deleteReportBlock(blockId) {
deleteReportBlocks([blockId]);
}
const dashboardContentBlocks = useMemo(() => {
const deletedIds = new Set(deletedReportBlockIds);
return visibleReportGridBlocks.flatMap((block) => {
if (block.type === "metric-strip") {
const metricCards = (block.cardIds ?? [])
.map((cardId) => cardsById.get(cardId))
.filter((card) => Boolean(card) && !deletedIds.has(metricCardBlockId(block.id, card.id)));
return metricCards.map((card) => {
const itemId = metricCardBlockId(block.id, card.id);
return {
className: "report-stack-item report-stack-item-metric-card",
compactGroup: `metric-strip:${block.id}`,
defaultLayout: "half",
id: itemId,
render: () => (<ArtifactMetricCard card={card} filters={activeSurfaceFilters} id={itemId} isMenuOpen={openMenuBlockId === itemId} onDeleteBlock={canDeleteBlocks ? () => deleteReportBlock(itemId) : undefined} onMenuOpenChange={(nextOpen) => {
setOpenMenuChartId(null);
setOpenMenuTableId(null);
setOpenMenuBlockId(nextOpen ? itemId : null);
}} onSourceOpen={() => setCardSourceModal(card)} selectedFilters={selectedFilters} snapshot={snapshot}/>)
};
});
}
const chart = block.chartId ? chartsById.get(block.chartId) : undefined;
const table = block.tableId ? tablesById.get(block.tableId) : undefined;
const className = block.type === "chart"
? "analytics-layout-item-chart"
: block.type === "table"
? "analytics-layout-item-table"
: block.type === "html"
? "analytics-layout-item-html"
: `report-stack-item report-stack-item-${block.type}`;
const defaultLayout = block.type === "chart"
? dashboardCardLayout(block.layout ?? chart?.layout)
: dashboardCardLayout(block.layout ?? table?.layout ?? "full");
return [{
className,
defaultLayout,
id: block.id,
render: (layout) => (<ReportBlockCard accessIssues={accessIssues} allowColumnResize={capabilities.canResizeColumns} block={block} blockTextOverride={blockTextOverrides[block.id]} canEditChartSpec={capabilities.canEditChartSpec} canEditHtml={capabilities.canEditHtml} chart={chart} chartSpecOverride={chart ? chartSpecOverrides[chart.id] : undefined} chartTextOverride={chart ? chartTextOverrides[chart.id] : undefined} chartTypeOverride={chart ? chartTypeOverrides[chart.id] : undefined} columnWidths={table ? tableColumnWidths[table.id] ?? {} : {}} filters={activeSurfaceFilters} isBlockMenuOpen={openMenuBlockId === block.id} isChartMenuOpen={Boolean(chart && openMenuChartId === chart.id)} isEditMode={activeEditMode && capabilities.canEditText} isTableMenuOpen={Boolean(table && openMenuTableId === table.id)} layout={layout} manifest={manifest} onBlockMenuOpenChange={(nextOpen) => {
setOpenMenuChartId(null);
setOpenMenuTableId(null);
setOpenMenuBlockId(nextOpen ? block.id : null);
}} onBlockTextChange={updateBlockText} onChartTypeChange={updateChartType} onChartMenuOpenChange={(nextOpen) => {
setOpenMenuTableId(null);
setOpenMenuBlockId(null);
setOpenMenuChartId(chart && nextOpen ? chart.id : null);
}} onChartModalOpen={setChartModal} onColumnWidthsChange={updateTableColumnWidths} onCopyResult={(message, isError = false) => setCopyMessage({ isError, message })} onDeleteBlock={canDeleteBlocks ? () => deleteReportBlock(block.id) : undefined} onRequestEditMode={requestEditMode} onTableMenuOpenChange={(nextOpen) => {
setOpenMenuChartId(null);
setOpenMenuBlockId(null);
setOpenMenuTableId(table && nextOpen ? table.id : null);
}} onTableModalOpen={setTableModal} onTableTextChange={updateTableText} onTextChange={updateChartText} selectedFilters={selectedFilters} snapshot={snapshot} table={table} tableTextOverride={table ? tableTextOverrides[table.id] : undefined}/>)
}];
});
}, [
accessIssues,
activeSurfaceFilters,
activeEditMode,
blockTextOverrides,
cardsById,
capabilities.canEdit,
capabilities.canEditChartSpec,
capabilities.canEditHtml,
capabilities.canEditText,
canDeleteBlocks,
capabilities.canResizeColumns,
chartTextOverrides,
chartSpecOverrides,
chartTypeOverrides,
chartsById,
deletedReportBlockIds,
manifest,
openMenuBlockId,
openMenuChartId,
openMenuTableId,
requestEditMode,
selectedFilters,
snapshot,
tableColumnWidths,
tableTextOverrides,
tablesById,
visibleReportGridBlocks
]);
const reportContentBlocks = useMemo(() => {
const deletedIds = new Set(deletedReportBlockIds);
return visibleReportGridBlocks.flatMap((block) => {
if (block.type === "metric-strip") {
const metricCards = (block.cardIds ?? [])
.map((cardId) => cardsById.get(cardId))
.filter((card) => Boolean(card) && !deletedIds.has(metricCardBlockId(block.id, card.id)));
return metricCards.map((card) => {
const itemId = metricCardBlockId(block.id, card.id);
return {
className: "report-stack-item report-stack-item-metric-card",
compactGroup: `metric-strip:${block.id}`,
defaultLayout: "half",
id: itemId,
render: () => (<ArtifactMetricCard card={card} filters={activeSurfaceFilters} id={itemId} isMenuOpen={openMenuBlockId === itemId} onDeleteBlock={canDeleteBlocks ? () => deleteReportBlock(itemId) : undefined} onMenuOpenChange={(nextOpen) => {
setOpenMenuChartId(null);
setOpenMenuTableId(null);
setOpenMenuBlockId(nextOpen ? itemId : null);
}} onSourceOpen={() => setCardSourceModal(card)} selectedFilters={selectedFilters} snapshot={snapshot}/>)
};
});
}
const chart = block.chartId ? chartsById.get(block.chartId) : undefined;
const table = block.tableId ? tablesById.get(block.tableId) : undefined;
return [{
className: `report-stack-item report-stack-item-${block.type}`,
defaultLayout: reportCardLayout(block.layout),
id: block.id,
render: (layout) => (<ReportBlockCard accessIssues={accessIssues} allowColumnResize={capabilities.canResizeColumns} block={block} blockTextOverride={blockTextOverrides[block.id]} canEditChartSpec={capabilities.canEditChartSpec} canEditHtml={capabilities.canEditHtml} chart={chart} chartSpecOverride={chart ? chartSpecOverrides[chart.id] : undefined} chartTextOverride={chart ? chartTextOverrides[chart.id] : undefined} chartTypeOverride={chart ? chartTypeOverrides[chart.id] : undefined} columnWidths={table ? tableColumnWidths[table.id] ?? {} : {}} filters={activeSurfaceFilters} isBlockMenuOpen={openMenuBlockId === block.id} isChartMenuOpen={Boolean(chart && openMenuChartId === chart.id)} isEditMode={activeEditMode && capabilities.canEditText} isTableMenuOpen={Boolean(table && openMenuTableId === table.id)} layout={layout} manifest={manifest} onBlockMenuOpenChange={(nextOpen) => {
setOpenMenuChartId(null);
setOpenMenuTableId(null);
setOpenMenuBlockId(nextOpen ? block.id : null);
}} onBlockTextChange={updateBlockText} onChartTypeChange={updateChartType} onChartMenuOpenChange={(nextOpen) => {
setOpenMenuTableId(null);
setOpenMenuBlockId(null);
setOpenMenuChartId(chart && nextOpen ? chart.id : null);
}} onChartModalOpen={setChartModal} onColumnWidthsChange={updateTableColumnWidths} onCopyResult={(message, isError = false) => setCopyMessage({ isError, message })} onDeleteBlock={canDeleteBlocks ? () => deleteReportBlock(block.id) : undefined} onRequestEditMode={requestEditMode} onTableMenuOpenChange={(nextOpen) => {
setOpenMenuChartId(null);
setOpenMenuBlockId(null);
setOpenMenuTableId(table && nextOpen ? table.id : null);
}} onTableModalOpen={setTableModal} onTableTextChange={updateTableText} onTextChange={updateChartText} selectedFilters={selectedFilters} snapshot={snapshot} table={table} tableTextOverride={table ? tableTextOverrides[table.id] : undefined}/>)
}];
});
}, [
accessIssues,
activeSurfaceFilters,
activeEditMode,
blockTextOverrides,
cardsById,
capabilities.canEditChartSpec,
capabilities.canEditHtml,
capabilities.canEditText,
canDeleteBlocks,
capabilities.canResizeColumns,
chartSpecOverrides,
chartTextOverrides,
chartTypeOverrides,
chartsById,
deletedReportBlockIds,
manifest,
openMenuBlockId,
openMenuChartId,
openMenuTableId,
requestEditMode,
selectedFilters,
snapshot,
tableColumnWidths,
tableTextOverrides,
tablesById,
visibleReportGridBlocks
]);
const activeFilters = activeFilterSummary(activeSurfaceFilters, selectedFilters);
const chartModalSourceChart = chartModal
? chartsById.get(chartModal.chart.id) ?? chartModal.chart
: null;
const chartModalBaseChart = chartModalSourceChart
? applyChartSpecOverride(chartModalSourceChart, chartSpecOverrides[chartModalSourceChart.id])
: null;
const chartModalRows = chartModalBaseChart
? filterRowsForDataset(getRows(snapshot, chartModalBaseChart.dataset), chartModalBaseChart.dataset, activeSurfaceFilters, selectedFilters, chartUsedFields(chartModalBaseChart))
: [];
const chartModalTypeOptions = chartModalBaseChart
? compatibleChartTypesFor(chartModalBaseChart, chartModalRows)
: [];
const chartModalRequestedType = chartModalBaseChart
? chartTypeOverrides[chartModalBaseChart.id] ?? chartModalBaseChart.type
: null;
const chartModalActiveType = chartModalRequestedType && chartModalTypeOptions.some((option) => option.type === chartModalRequestedType)
? chartModalRequestedType
: chartModalBaseChart?.type ?? null;
const activeChartModal = chartModal?.kind === "fullscreen" && chartModalBaseChart && chartModalActiveType
? {
chart: withChartType({
...chartModalBaseChart,
subtitle: chartModal.chart.subtitle,
title: chartModal.chart.title
}, chartModalActiveType)
}
: null;
if (isReport) {
return (<ArtifactReaderContext.Provider value={readerContextValue}>
<DashboardShell isEditMode={activeEditMode} surface="report">
<AnalyticsTopBar capabilities={capabilities} chrome={topBarChrome} environment={environment} isEditMode={activeEditMode} isSavingEdit={isSavingEdit} manifest={manifest} onCancelEdit={cancelEditMode} onCopyResult={(message, isError = false) => setCopyMessage({ isError, message })} onEdit={requestEditMode} onRequestFullscreen={effectiveRequestFullscreen} onSaveEdit={saveEditMode} onTitleChange={updatePageTitle} packageInfo={packageInfo} snapshot={snapshot} title={pageTitle}/>
<AccessIssueStrip issues={accessIssues}/>
{copyMessage ? (<div className={`copy-toast ${copyMessage.isError ? "error" : ""}`} role="status">
{copyMessage.message}
</div>) : null}

<AnalyticsLayoutCanvas ariaLabel="Report blocks" blocks={reportContentBlocks} cancelSelector={CARD_DRAG_CANCEL_SELECTOR} className="report-content-grid report-block-stack metric-card-layout" isEditMode={activeLayoutEditMode} layoutResetKey={layoutResetKey} onLayoutChange={recordReportLayoutDraft} persistedLayout={usesHostedPresentation ? hostedReportLayout : undefined} persistenceVersion={usesHostedPresentation ? hostedPresentation?.revision ?? 0 : 0} storageKey={!usesHostedPresentation && capabilities.canEdit ? reportStorageKey : null}/>
{activeChartModal ? (<ChartDetailPage accessIssue={accessIssueForChart(activeChartModal.chart, accessIssues)} chart={activeChartModal.chart} environment={environment} filters={activeSurfaceFilters} manifest={manifest} onChartSpecChange={canEditChartSpec ? updateChartSpec : undefined} onClose={() => setChartModal(null)} rows={chartModalRows} selectedFilters={selectedFilters} snapshot={snapshot}/>) : null}
{chartModal?.kind === "source" && chartModalBaseChart ? (<ChartSourceModalDialog activeFilters={activeFilters} chart={{
...chartModalBaseChart,
subtitle: chartModal.chart.subtitle,
title: chartModal.chart.title
}} environment={environment} manifest={manifest} onClose={() => setChartModal(null)} rows={chartModalRows} snapshot={snapshot}/>) : null}
{cardSourceModal ? (<CardSourceModalDialog activeFilters={activeFilters} card={cardSourceModal} environment={environment} filters={activeSurfaceFilters} manifest={manifest} onClose={() => setCardSourceModal(null)} selectedFilters={selectedFilters} snapshot={snapshot}/>) : null}
{tableModal ? (<TableModalDialog activeFilters={activeFilters} allowColumnResize={capabilities.canResizeColumns} columnWidths={tableColumnWidths[tableModal.table.id] ?? {}} environment={environment} filters={activeSurfaceFilters} kind={tableModal.kind} manifest={manifest} onColumnWidthsChange={updateTableColumnWidths} onClose={() => setTableModal(null)} selectedFilters={selectedFilters} snapshot={snapshot} table={tableModal.table}/>) : null}
</DashboardShell>
</ArtifactReaderContext.Provider>);
}
return (<ArtifactReaderContext.Provider value={readerContextValue}>
<DashboardShell isEditMode={activeEditMode} surface={manifest?.surface}>
<AnalyticsTopBar capabilities={capabilities} chrome={topBarChrome} environment={environment} isEditMode={activeEditMode} isSavingEdit={isSavingEdit} manifest={manifest} onCancelEdit={cancelEditMode} onCopyResult={(message, isError = false) => setCopyMessage({ isError, message })} onEdit={requestEditMode} onRequestFullscreen={effectiveRequestFullscreen} onSaveEdit={saveEditMode} onTitleChange={updatePageTitle} packageInfo={packageInfo} snapshot={snapshot} title={pageTitle}/>
<AccessIssueStrip issues={accessIssues}/>
{copyMessage ? (<div className={`copy-toast ${copyMessage.isError ? "error" : ""}`} role="status">
{copyMessage.message}
</div>) : null}

<FilterToolbar filters={activeSurfaceFilters} onChange={setSelectedFilters} selectedFilters={selectedFilters} snapshot={snapshot}/>

<AnalyticsLayoutCanvas ariaLabel="Dashboard content" blocks={dashboardContentBlocks} cancelSelector={CARD_DRAG_CANCEL_SELECTOR} className="dashboard-content-grid metric-card-layout" isEditMode={activeLayoutEditMode} layoutResetKey={layoutResetKey} onLayoutChange={recordDashboardLayoutDraft} persistedLayout={usesHostedPresentation ? hostedDashboardLayout : undefined} persistenceVersion={usesHostedPresentation ? hostedPresentation?.revision ?? 0 : 0} storageKey={!usesHostedPresentation && capabilities.canEdit ? storageKey : null}/>
{activeChartModal ? (<ChartDetailPage accessIssue={accessIssueForChart(activeChartModal.chart, accessIssues)} chart={activeChartModal.chart} environment={environment} filters={activeSurfaceFilters} manifest={manifest} onChartSpecChange={canEditChartSpec ? updateChartSpec : undefined} onClose={() => setChartModal(null)} rows={chartModalRows} selectedFilters={selectedFilters} snapshot={snapshot}/>) : null}
{chartModal?.kind === "source" && chartModalBaseChart ? (<ChartSourceModalDialog activeFilters={activeFilters} chart={{
...chartModalBaseChart,
subtitle: chartModal.chart.subtitle,
title: chartModal.chart.title
}} environment={environment} manifest={manifest} onClose={() => setChartModal(null)} rows={chartModalRows} snapshot={snapshot}/>) : null}
{cardSourceModal ? (<CardSourceModalDialog activeFilters={activeFilters} card={cardSourceModal} environment={environment} filters={activeSurfaceFilters} manifest={manifest} onClose={() => setCardSourceModal(null)} selectedFilters={selectedFilters} snapshot={snapshot}/>) : null}
{tableModal ? (<TableModalDialog activeFilters={activeFilters} allowColumnResize={capabilities.canResizeColumns} columnWidths={tableColumnWidths[tableModal.table.id] ?? {}} environment={environment} filters={activeSurfaceFilters} kind={tableModal.kind} manifest={manifest} onColumnWidthsChange={updateTableColumnWidths} onClose={() => setTableModal(null)} selectedFilters={selectedFilters} snapshot={snapshot} table={tableModal.table}/>) : null}
</DashboardShell>
</ArtifactReaderContext.Provider>);
}

export default function App({ displayMode = "fullscreen", onRequestFullscreen } = {}) {
const [artifact, setArtifact] = useState(null);
const [error, setError] = useState(null);
useEffect(() => {
let cancelled = false;
void loadArtifactFromApi()
.then((nextArtifact) => {
if (!cancelled)
setArtifact(nextArtifact);
})
.catch((loadError) => {
if (!cancelled)
setError(loadError instanceof Error ? loadError.message : "Failed to load report");
});
return () => {
cancelled = true;
};
}, []);
if (error) {
return (<DashboardShell>
<div className="empty-state error-state">{error}</div>
</DashboardShell>);
}
if (!artifact) {
return (<DashboardShell>
<div className="empty-state">Loading analytics artifact...</div>
</DashboardShell>);
}
return (<ArtifactReader artifact={artifact} displayMode={displayMode} environment={MCP_ARTIFACT_READER_ENVIRONMENT} onRequestFullscreen={onRequestFullscreen}/>);
}
