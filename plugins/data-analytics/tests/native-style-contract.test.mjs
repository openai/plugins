import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { createRequire } from "node:module";
import { test } from "node:test";
import { gunzipSync } from "node:zlib";

const require = createRequire(import.meta.url);
const server = require("../mcp/server.cjs");

function read(relativePath) {
  return readFileSync(new URL(relativePath, import.meta.url), "utf8");
}

function readBundledWidget(baseName) {
  const assetsUrl = new URL("../assets/", import.meta.url);
  const encoded = readdirSync(assetsUrl)
    .filter((name) => name.startsWith(`${baseName}.html.gz.b64.part`))
    .sort()
    .map((name) => readFileSync(new URL(name, assetsUrl), "utf8").trim())
    .join("");
  return gunzipSync(Buffer.from(encoded, "base64")).toString("utf8");
}

test("widget entrypoints load the Codex baseline before analytics tokens", () => {
  const sources = [
    read("../src/analytics-app/main.tsx"),
    read("../src/datascience-artifact-widget.jsx"),
    read("../src/datascience-chart-widget.js"),
    read("../src/datascience-table-widget.js"),
  ];

  for (const source of sources) {
    assert.ok(source.includes("codex-theme.css"));
    assert.ok(source.indexOf("codex-theme.css") < source.indexOf("tokens.css"));
  }

  const baseline = read("../src/styles/codex-theme.css");
  assert.match(baseline, /--codex-accent:/);
  assert.match(baseline, /--codex-font-sans:/);
});

test("analytics tokens alias shared roles to the Codex baseline", () => {
  const tokens = read("../src/analytics-app/tokens.css");

  assert.match(tokens, /--ds-bg: var\(--codex-bg\);/);
  assert.match(tokens, /--ds-surface: var\(--codex-panel\);/);
  assert.match(tokens, /--ds-border: var\(--codex-border\);/);
  assert.match(tokens, /--ds-shadow: var\(--codex-shadow-lg\);/);
  assert.match(tokens, /--ds-dropdown-row-height: var\(--codex-button-height\);/);

  const chartTokens = read("../src/analytics-app/charting/chart-tokens.css");
  assert.match(chartTokens, /--ds-chart-font-family: var\(--ds-font, var\(--codex-font-sans,/);
});

test("report tables retain contained horizontal scrolling and Codex-aligned reading edges", () => {
  const source = read("../src/analytics-app/tables/DataTable.jsx");
  const tableStyles = read("../src/analytics-app/tables/data-table.css");
  const styles = read("../src/analytics-app/styles.css");
  const app = read("../src/analytics-app/App.tsx");

  assert.match(source, /const DEFAULT_PAGE_SIZE = 15;/);
  assert.match(read("../src/datascience-table-widget.js"), /const TABLE_CARD_PAGE_SIZE = 15;/);
  assert.match(read("../src/analytics-app/tokens.css"), /--ds-report-content-half-width: 384px;/);
  assert.match(styles, /--report-table-content-inset: max\(var\(--ds-gutter\), calc\(50vw - var\(--ds-report-content-half-width\)\)\);/);
  assert.match(styles, /\.report-stack-item-table \.table-wrap \{[\s\S]*width: 100%;/);
  assert.match(styles, /\.report-stack-item-table \.table-wrap \{[\s\S]*max-width: 100%;/);
  assert.match(styles, /\.report-stack-item-table \.table-wrap \{[\s\S]*margin-left: 0;/);
  assert.match(styles, /\.report-stack-item-table \.table-scroll-content \{[\s\S]*padding-left: 0;/);
  assert.match(styles, /\.table-density-spacious table:not\(\.data-table-resizable\) \{/);
  assert.match(app, /calculateTableSizing\(table\.columns, activeColumnWidths, tableViewportWidth, shouldFillAvailableWidth\)/);
  assert.match(app, /const shouldFillAvailableWidth = isFullscreen \|\| fillAvailableWidth;/);
  assert.match(app, /minWidth: `\$\{tableSizing\.minimumTableWidth\}px`/);
  assert.match(app, /width: `\$\{tableSizing\.tableWidth\}px`/);
  assert.match(app, /function TableContent\(\{[\s\S]*fillAvailableWidth = true,/);
  assert.match(app, /function SourceDataTable\(\{[\s\S]*fillAvailableWidth = true,/);
  assert.match(app, /calculateHorizontalScrollEdges\(\{[\s\S]*clientWidth: tableWrap\.clientWidth,[\s\S]*scrollLeft: tableWrap\.scrollLeft,[\s\S]*scrollWidth: tableElementRef\.current\?\.offsetWidth \?\? tableWrap\.scrollWidth/);
  assert.match(app, /scrollbarBlockSize: Math\.max\(0, tableWrap\.offsetHeight - tableWrap\.clientHeight\)/);
  assert.match(app, /scrollbarInlineSize: Math\.max\(0, tableWrap\.offsetWidth - tableWrap\.clientWidth\)/);
  assert.match(app, /tableWrap\.addEventListener\("scroll", updateHorizontalScrollEdges, \{ passive: true \}\)/);
  assert.match(app, /observer\.observe\(tableScrollContent\)/);
  assert.match(app, /observer\.observe\(tableElement\)/);
  assert.match(app, /data-can-scroll-left=\{horizontalScrollEdges\.canScrollLeft/);
  assert.match(app, /data-can-scroll-right=\{horizontalScrollEdges\.canScrollRight/);
  assert.match(app, /role=\{isScrollableTableRegion \? "region" : undefined\}/);
  assert.match(app, /tabIndex=\{isScrollableTableRegion \? 0 : undefined\}/);
  assert.match(app, /className="table-scroll-edge table-scroll-edge-left" data-image-export-exclude="true"/);
  assert.match(app, /className="table-scroll-edge table-scroll-edge-right" data-image-export-exclude="true"/);
  assert.match(styles, /\.table-scroll-shell \{[\s\S]*--table-scroll-edge-surface: var\(--ds-bg\);[\s\S]*--table-scrollbar-block-size: 0px;[\s\S]*--table-scrollbar-inline-size: 0px;[\s\S]*position: relative;/);
  assert.match(styles, /\.native-modal \.table-scroll-shell \{[\s\S]*--table-scroll-edge-surface: var\(--ds-overlay-bg\);/);
  assert.match(styles, /\.table-scroll-edge \{[\s\S]*width: 28px;[\s\S]*opacity: 0;[\s\S]*pointer-events: none;[\s\S]*transition: opacity 150ms ease;/);
  assert.match(styles, /\.table-scroll-edge \{[\s\S]*bottom: var\(--table-scrollbar-block-size\);/);
  assert.match(styles, /\.table-scroll-edge-right \{[\s\S]*right: var\(--table-scrollbar-inline-size\);/);
  assert.match(styles, /\.table-scroll-shell\[data-can-scroll-left="true"\] \.table-scroll-edge-left,[\s\S]*\.table-scroll-shell\[data-can-scroll-right="true"\] \.table-scroll-edge-right \{[\s\S]*opacity: 1;/);
  assert.match(styles, /@media print, \(forced-colors: active\) \{[\s\S]*\.table-scroll-edge \{[\s\S]*display: none;/);
  assert.match(styles, /--ds-menu-hover-bg: #2b2b2b;/);
  assert.doesNotMatch(styles, /\.report-stack-item-table \.table-wrap \{[^}]*padding-left:/);
  assert.match(styles, /\.modal-panel \{[\s\S]*background: var\(--ds-overlay-bg\);/);
  assert.match(styles, /\.native-modal\.source-modal \{[\s\S]*width: min\(800px, calc\(100vw - 48px\)\);/);
  assert.match(styles, /\.source-modal-panel \{[\s\S]*overflow: hidden;[\s\S]*background: var\(--ds-overlay-bg\);[\s\S]*padding: 0;/);
  assert.match(styles, /\.native-modal\.table-fullscreen-modal \{[\s\S]*width: min\(1200px, calc\(100dvw - 32px\)\);[\s\S]*height: fit-content;/);
  assert.match(styles, /\.table-fullscreen-panel \{[\s\S]*height: auto;[\s\S]*max-height: calc\(100dvh - 32px\);/);
  assert.match(styles, /\.table-wrap\.fullscreen \{[\s\S]*flex: 0 1 auto;[\s\S]*max-height: min\(700px, calc\(100dvh - 138px\)\);[\s\S]*overflow: auto;/);
  assert.match(read("../src/analytics-app/tokens.css"), /--ds-menu-bg: var\(--ds-overlay-bg\);/);
  assert.match(styles, /\.chip \{[\s\S]*background: var\(--ds-surface-tertiary\);/);
  assert.match(styles, /\.metric-badge\.positive \{[\s\S]*color: var\(--ds-green\);/);
  assert.match(styles, /\.metric-badge\.negative \{[\s\S]*color: var\(--ds-red\);/);
  assert.match(tableStyles, /\.data-table td \{[\s\S]*color: var\(--ds-text-secondary\);/);
  assert.match(tableStyles, /\.data-table td:first-child \{[\s\S]*color: var\(--ds-text-primary\);/);
  assert.match(source, /tableWrapRef\.current\.scrollLeft = 0/);
  assert.match(app, /const TABLE_CARD_PAGE_SIZE = 15;/);
  assert.match(app, /minWidth: `\$\{tableSizing\.minimumTableWidth\}px`/);
  assert.match(app, /width: `\$\{tableSizing\.tableWidth\}px`/);
  assert.match(tableStyles, /\.table-sort-button:hover,\s*\.table-sort-button:focus-visible \{[\s\S]*border-radius: 0;/);
});

test("report top-bar title uses the compact supported text style", () => {
  const styles = read("../src/analytics-app/styles.css");
  const target = styles
    .split(".analytics-top-bar .page-title-edit-target {", 2)[1]
    .split("}", 1)[0];
  const title = styles
    .split(".analytics-top-bar .page-title-edit-target h1 {", 2)[1]
    .split("}", 1)[0];
  const editor = styles
    .split(".analytics-top-bar .page-title-editor {", 2)[1]
    .split("}", 1)[0];

  for (const block of [title, editor]) {
    assert.match(block, /font-size: 14px;/);
    assert.match(block, /font-weight: 500;/);
    assert.match(block, /line-height: 20px;/);
    assert.match(block, /letter-spacing: -0\.13px;/);
  }

  for (const block of [target, editor]) {
    assert.match(block, /width: calc\(100% \+ 16px\);/);
    assert.match(block, /max-width: calc\(100% \+ 16px\);/);
    assert.match(block, /margin: -4px -8px;/);
    assert.match(block, /padding: 4px 8px;/);
  }
  assert.match(editor, /border: 0;/);
});

test("chart detail actions distinguish editing from hosted exploration and use an icon-only inline expand action", () => {
  const app = read("../src/analytics-app/App.tsx");
  const widget = read("../src/datascience-chart-widget.js");
  const widgetMarkup = read("../src/datascience-chart-widget.html");
  const widgetStyles = read("../src/datascience-chart-widget.css");
  const inlineControl = widgetMarkup.match(/<button(?=[^>]*id="display-mode-button")[^>]*>[\s\S]*?<\/button>/)?.[0];

  assert.match(app, /menuItem\(canEditChartSpec \? "Edit chart" : "Explore chart"/);
  assert.doesNotMatch(app, /Switch chart type/);
  assert.doesNotMatch(app, /<h2>Edit chart<\/h2>/);
  assert.ok(inlineControl);
  assert.match(inlineControl, /title="Expand chart"/);
  assert.match(inlineControl, /aria-label="Expand chart"/);
  assert.match(inlineControl, /<svg/);
  assert.match(inlineControl, /m21 21-6-6/);
  assert.doesNotMatch(inlineControl, /M6 2H2v4/);
  assert.doesNotMatch(inlineControl, /<span|Edit/);
  assert.match(widget, /const showInlineExpand = mode === "inline" && hostSupportsDisplayMode\(\);/);
  assert.match(widget, /button\.hidden = !showInlineExpand;/);
  assert.match(widget, /button\.title = "Expand chart";/);
  assert.doesNotMatch(widget, /"Edit chart"|display-mode-button-label|exploreIcon/);
  assert.doesNotMatch(widget, /Explore chart/);
  assert.match(widgetStyles, /\.display-mode-button \{[\s\S]*aspect-ratio: 1 \/ 1;[\s\S]*width: 32px;[\s\S]*height: 32px;[\s\S]*border-radius: 50%;/);
});

test("artifact reader exposes stable nonvisual verification hooks", () => {
  const app = read("../src/analytics-app/App.tsx");
  const layoutCanvas = read("../src/analytics-app/layout/AnalyticsLayoutCanvas.tsx");
  const styles = read("../src/analytics-app/styles.css");
  const menuButtonRule = styles.match(
    /\.viz-card-menu-button \{\s*display: inline-flex;[\s\S]*?\n\}/,
  )?.[0];

  assert.match(layoutCanvas, /data-artifact-block-id=\{item\.id\}/);
  assert.match(app, /data-artifact-action="open-options"/);
  assert.match(app, /data-artifact-has-source=/);
  assert.match(app, /data-artifact-action=\{(?:label|itemLabel) === "View data source" \? "view-source" : undefined\}/);
  assert.match(app, /data-artifact-dialog="source"/);
  assert.match(app, /data-artifact-dialog=\{kind === "source" \? "source" : undefined\}/);
  assert.match(app, /data-artifact-item-type="chart"/);
  assert.match(app, /data-artifact-item-type="card"/);
  assert.match(app, /data-artifact-item-type="table"/);
  assert.ok(menuButtonRule);
  assert.match(menuButtonRule, /opacity: 0;/);
  assert.doesNotMatch(menuButtonRule, /visibility: hidden;/);
});

test("report and dashboard metrics render as independent draggable cards in canonical block order", () => {
  const app = read("../src/analytics-app/App.tsx");
  const layoutCanvas = read("../src/analytics-app/layout/AnalyticsLayoutCanvas.tsx");
  const serverSource = read("../mcp/server.cjs");
  const styles = read("../src/analytics-app/styles.css");
  const dashboardResolver = app
    .split("const dashboardContentBlocks = useMemo(() => {", 2)[1]
    .split("const reportContentBlocks = useMemo(() => {", 1)[0];

  assert.ok(dashboardResolver);
  assert.match(app, /function metricCardBlockId\(blockId, cardId\)/);
  assert.match(app, /visibleReportGridBlocks\.flatMap\(\(block\) =>/);
  assert.match(app, /className: "report-stack-item report-stack-item-metric-card"/);
  assert.match(app, /compactGroup: `metric-strip:\$\{block\.id\}`/);
  assert.match(app, /defaultLayout: "half"/);
  assert.match(layoutCanvas, /function buildDisplayRows/);
  assert.match(layoutCanvas, /function compactGroupForItem/);
  assert.match(layoutCanvas, /compactGroupForItem\(items\[index\], blockById\) === compactGroup/);
  assert.match(layoutCanvas, /while \(index < items\.length && !compactGroupForItem\(items\[index\], blockById\)\)/);
  assert.match(layoutCanvas, /row\.compactGroup \? "is-compact-row"/);
  assert.match(layoutCanvas, /function balancedCompactColumnCount/);
  assert.match(layoutCanvas, /const \[canvasWidth, setCanvasWidth\] = useState\(0\)/);
  assert.match(layoutCanvas, /new ResizeObserver\(updateWidth\)/);
  assert.match(layoutCanvas, /fewestEmptyCells/);
  assert.match(layoutCanvas, /"--analytics-compact-columns": compactColumns/);
  assert.match(app, /function ArtifactMetricCard/);
  assert.match(app, /datascience-dashboard:content-layout:v2:/);
  assert.doesNotMatch(app, /function KpiStrip/);
  assert.match(dashboardResolver, /return visibleReportGridBlocks\.flatMap\(\(block\) =>/);
  assert.match(dashboardResolver, /if \(block\.type === "metric-strip"\)/);
  assert.match(dashboardResolver, /const chart = block\.chartId \? chartsById\.get\(block\.chartId\) : undefined;/);
  assert.match(dashboardResolver, /const table = block\.tableId \? tablesById\.get\(block\.tableId\) : undefined;/);
  assert.doesNotMatch(dashboardResolver, /charts\.map|tables\.map|const metricBlocks/);
  assert.match(app, /className="dashboard-content-grid metric-card-layout"/);
  assert.match(app, /className="report-content-grid report-block-stack metric-card-layout"/);
  assert.match(app, /menuItem\("View data source"/);
  assert.match(app, /onDeleteBlock \? menuItem\("Delete"/);
  assert.match(app, /knownDeletableReportIds\.has\(id\)/);
  assert.match(styles, /\.report-metric-card \{[\s\S]*border: 1px solid var\(--ds-border-subtle\);[\s\S]*border-radius: var\(--ds-radius-panel\);/);
  assert.match(styles, /\.report-metric-card \{[\s\S]*justify-content: flex-start;/);
  assert.match(styles, /\.report-metric-card \{[\s\S]*padding: 20px;/);
  assert.match(styles, /\.report-metric-card \{[\s\S]*overflow: visible;/);
  assert.match(styles, /\.kpi-card \{[^}]*background: transparent;/);
  assert.match(styles, /\.report-metric-card \{[^}]*background: transparent;/);
  assert.doesNotMatch(styles, /\.report-metric-card \{[\s\S]*min-height: 132px;/);
  assert.match(styles, /\.analytics-layout-item-shell > \.report-metric-card \{[\s\S]*height: 100%;/);
  assert.match(styles, /\.report-metric-card \.kpi-label-row \{[\s\S]*flex: 0 0 auto;/);
  assert.match(styles, /\.report-metric-card \.kpi-info-wrap \{[\s\S]*height: 20px;/);
  assert.match(styles, /\.report-metric-card \.kpi-info \{[\s\S]*position: absolute;[\s\S]*transform: translate\(-50%, -50%\);/);
  assert.match(styles, /\.report-metric-card \.viz-card-actions \{[\s\S]*position: absolute;[\s\S]*top: 12px;[\s\S]*right: 12px;/);
  assert.doesNotMatch(styles, /padding: 20px 56px 20px 24px;/);
  assert.doesNotMatch(styles, /padding: 18px 52px 18px 20px;/);
  assert.match(styles, /--metric-card-gap: 8px;/);
  assert.match(styles, /--metric-card-min-width: 280px;/);
  assert.match(layoutCanvas, /const COMPACT_ITEM_MIN_WIDTH_PX = 280;/);
  assert.match(styles, /\.kpi-label \{[\s\S]*text-overflow: ellipsis;[\s\S]*white-space: nowrap;/);
  assert.match(styles, /\.metric-badge-row \{[\s\S]*flex-wrap: nowrap;/);
  assert.match(styles, /\.metric-badge-row \{[\s\S]*max-width: 100%;[\s\S]*overflow: hidden;/);
  assert.match(styles, /\.report-metric-card \.metric-badge \{[\s\S]*white-space: nowrap;/);
  assert.match(styles, /\.report-metric-card \.metric-badge \{[\s\S]*max-width: 100%;[\s\S]*overflow: hidden;/);
  assert.match(styles, /\.metric-badge-label \{[\s\S]*text-overflow: ellipsis;/);
  assert.match(styles, /\.metric-badge-value \{[\s\S]*text-overflow: ellipsis;/);
  assert.match(styles, /\.metric-card-layout \.analytics-layout-row\.is-compact-row \{[\s\S]*grid-template-columns: repeat\([\s\S]*var\(--analytics-compact-columns, auto-fit\),[\s\S]*minmax\(min\(100%, var\(--metric-card-min-width\)\), 1fr\)[\s\S]*\);/);
  assert.match(styles, /\.metric-card-layout \.analytics-layout-row\.is-compact-row > \.analytics-layout-item\.layout-full \{[\s\S]*grid-column: auto;/);
  assert.doesNotMatch(styles, /\.kpi-strip|kpi-columns-/);
  assert.match(serverSource, /cardIds: \{[\s\S]*minItems: 1,[\s\S]*There is no preferred or maximum card count/);
  assert.doesNotMatch(styles, /@container report-block-stack/);
  assert.doesNotMatch(styles, /\.report-block-stack \.analytics-layout-row\.is-compact-row \{\s*grid-template-columns: 1fr;/);
  assert.doesNotMatch(app, /function ReportMetricStripBlock/);
});

test("dashboard chart rows expand to contain their rendered chart bodies", () => {
  const styles = read("../src/analytics-app/styles.css");

  assert.match(
    styles,
    /\.dashboard-content-grid \.viz-card \.chart-body-measure \{[^}]*flex: 0 0 auto;[^}]*height: auto;[^}]*max-height: none;[^}]*min-height: 0;/,
  );
});

test("artifact top bar matches the title-date-overflow-edit layout", () => {
  const app = read("../src/analytics-app/App.tsx");
  const bundledApp = readBundledWidget("datascience-artifact-widget");
  const styles = read("../src/analytics-app/styles.css");
  const host = read("../src/mcp-host.js");
  const runtimeEnvironment = read("../src/analytics-app/runtimeEnvironment.ts");
  const editablePageTitle = app
    .split("function EditablePageTitle", 2)[1]
    .split("function composeHeaderMarkdown", 1)[0];
  const handoff = read("../src/analytics-app/handoff.mjs");
  const submitPrompt = app
    .split("function submitCodexPrompt", 2)[1]
    .split("function AnalyticsTopBarFreshness", 1)[0];
  const freshness = app
    .split("function AnalyticsTopBarFreshness", 2)[1]
    .split("function AnalyticsReaderFreshness", 1)[0];
  const topBar = app
    .split("function AnalyticsTopBar(", 2)[1]
    .split("export default function App", 1)[0];
  const topBarStyles = styles
    .split(".analytics-top-bar {", 2)[1]
    .split("}", 1)[0];
  const leadingStyles = styles
    .split(".analytics-top-bar-leading {", 2)[1]
    .split("}", 1)[0];
  const titleStyles = styles
    .split(".analytics-top-bar-title {", 2)[1]
    .split("}", 1)[0];
  const datetimeStyles = styles
    .split(".top-bar-refresh-datetime {", 2)[1]
    .split("}", 1)[0];
  const tooltipStyles = styles
    .split(".top-bar-refresh-tooltip {", 2)[1]
    .split("}", 1)[0];
  const overflowStyles = styles
    .split(".top-bar-overflow-button {", 2)[1]
    .split("}", 1)[0];
  const editStyles = styles
    .split(".top-bar-edit-button {", 2)[1]
    .split("}", 1)[0];

  assert.match(app, /const refreshLabel = dateLabel === "Unknown" \? "Refresh" : dateLabel;/);
  assert.match(app, /<span className="top-bar-refresh-text">\{refreshLabel\}<\/span>/);
  assert.match(app, /className="top-bar-refresh-tooltip"[^>]*role="tooltip"/);
  assert.match(app, /Ask ChatGPT to refresh this \$\{surfaceLabel\}/);
  assert.match(app, /requestCodexAction\([\s\S]*refreshPrompt\(manifest, snapshot, packageInfo\),[\s\S]*`Refresh \$\{appSurfaceLabel\(manifest\)\}`/);
  assert.ok(submitPrompt);
  assert.match(submitPrompt, /await sendPromptToHost\(prompt, title\)/);
  assert.match(app, /if \(isPublishedArtifactSite\(packageInfo\)\) \{[\s\S]*setHandoffRequest\(\{ description, prompt, title: actionTitle \}\)/);
  assert.match(app, /function CodexHandoffDialog\(/);
  assert.match(app, /Continue in ChatGPT/);
  assert.match(app, /Open in desktop app/);
  assert.match(app, /<Laptop aria-hidden="true"/);
  assert.match(app, /Open on web/);
  assert.match(app, /Copy prompt/);
  assert.doesNotMatch(app, /workspace that owns this Site|deep link cannot currently select a ChatGPT workspace/);
  const handoffDialog = app
    .split("function CodexHandoffDialog", 2)[1]
    .split("function AnalyticsTopBarFreshness", 1)[0];
  assert.ok(handoffDialog);
  assert.equal(handoffDialog.match(/className="codex-handoff-option"/g)?.length, 3);
  assert.equal(handoffDialog.match(/<ArrowUpRight aria-hidden="true"/g)?.length, 2);
  assert.doesNotMatch(handoffDialog, /<small>/);
  assert.match(handoffDialog, /dialog\.focus\(\{ preventScroll: true \}\)/);
  assert.match(handoffDialog, /tabIndex=\{-1\}/);
  assert.match(handoffDialog, /aria-describedby="codex-handoff-description"/);
  assert.match(handoffDialog, /<p id="codex-handoff-description">\{request\.description\}<\/p>/);
  assert.doesNotMatch(handoffDialog, /workspace/i);
  assert.match(app, /html: "Create a portable HTML file from this"/);
  assert.match(app, /className="codex-handoff-option" onClick=\{\(\) => void copyPrompt\(\)\}/);
  assert.match(app, /Use \$\{dataAnalyticsPluginMention\(packageInfo\)\} and invoke \$\{workflow\} in portable HTML mode/);
  assert.match(app, /Use \$\{dataAnalyticsPluginMention\(packageInfo\)\} and invoke \$report-to-pdf/);
  assert.match(app, /invoke \$build-report in HTML mode[\s\S]*then invoke \$report-to-google-doc/);
  assert.match(app, /invoke \$build-report in HTML mode[\s\S]*then invoke \$report-to-google-slides/);
  assert.match(handoff, /function workModeWebPromptUrl\(prompt\) \{[\s\S]*https:\/\/chatgpt\.com\/[\s\S]*disable_auto_send: "1"/);
  assert.match(handoff, /Select Work Mode, then send this request:/);
  assert.match(handoff, /function canonicalPublishedSiteUrl\(href\) \{[\s\S]*`\$\{url\.origin\}\$\{url\.pathname\}`/);
  assert.match(bundledApp, /Continue in ChatGPT/);
  assert.match(bundledApp, /Open in desktop app/);
  assert.match(bundledApp, /Open on web/);
  assert.match(bundledApp, /Copy prompt/);
  assert.match(bundledApp, /Create a portable HTML file from this/);
  assert.doesNotMatch(bundledApp, /workspace that owns this Site|Continue in Codex|Open Codex desktop/);
  assert.match(styles, /\.native-modal\.codex-handoff-modal \{[\s\S]*width: min\(400px, calc\(100vw - 48px\)\);/);
  assert.match(styles, /\.native-modal\.codex-handoff-modal:focus \{[\s\S]*outline: none;/);
  assert.match(styles, /\.codex-handoff-panel \{[\s\S]*gap: 24px;[\s\S]*padding: 24px;[\s\S]*border-radius: 24px;/);
  assert.match(styles, /\.codex-handoff-option \{[\s\S]*gap: 12px;[\s\S]*align-items: center;[\s\S]*min-height: 44px;[\s\S]*padding: 11px;[\s\S]*border-radius: 16px;/);
  assert.match(app, /function isPublishedArtifactSite\(packageInfo\) \{[\s\S]*hostedReadOnly === true \|\| packageInfo\?\.deliveryMode === "site_creator";/);
  assert.match(runtimeEnvironment, /const result = await hostApi\.sendFollowUpMessage\(title \? \{ prompt, title \} : \{ prompt \}\);[\s\S]*result\?\.isError !== true/);
  assert.match(runtimeEnvironment, /const result = await hostApi\.sendMessage\(\{[\s\S]*content: \[\{ type: "text", text: prompt \}\][\s\S]*result\?\.isError !== true/);
  assert.doesNotMatch(runtimeEnvironment, /hostApi\?\.openCodexPrompt/);
  assert.match(host, /app\.getHostCapabilities\(\)\?\.message\?\.text/);
  assert.match(host, /existing\.sendMessage = \(message\) => app\.sendMessage\(message\)/);
  assert.match(topBarStyles, /height: 48px;/);
  assert.match(topBarStyles, /padding: 8px 12px;/);
  assert.match(leadingStyles, /display: flex;/);
  assert.match(leadingStyles, /flex: 1 1 auto;/);
  assert.match(leadingStyles, /height: 32px;/);
  assert.match(titleStyles, /flex: 0 1 auto;/);
  assert.match(titleStyles, /margin-right: 8px;/);
  assert.doesNotMatch(styles, /\.is-app-editing \.analytics-top-bar-title/);
  assert.match(datetimeStyles, /height: 32px;/);
  assert.match(datetimeStyles, /padding: 0 12px;/);
  assert.match(datetimeStyles, /border: 0;/);
  assert.match(datetimeStyles, /background: transparent;/);
  assert.match(datetimeStyles, /font-size: 14px;/);
  assert.match(datetimeStyles, /font-weight: 400;/);
  assert.match(datetimeStyles, /line-height: 20px;/);
  assert.match(tooltipStyles, /position: fixed;/);
  assert.match(tooltipStyles, /top: 48px;/);
  assert.match(tooltipStyles, /left: 12px;/);
  assert.doesNotMatch(tooltipStyles, /right:/);
  assert.match(overflowStyles, /width: 32px;/);
  assert.match(overflowStyles, /min-width: 32px;/);
  assert.match(overflowStyles, /padding: 0;/);
  assert.match(editStyles, /min-width: 74px;/);
  assert.match(styles, /\.top-bar-refresh-tooltip \{[\s\S]*visibility: hidden;/);
  assert.match(styles, /\.top-bar-refresh-tooltip-anchor:hover \.top-bar-refresh-tooltip,[\s\S]*visibility: visible;/);
  assert.match(styles, /\.top-bar-refresh-tooltip-anchor:hover \.top-bar-refresh-tooltip \{[\s\S]*transition-delay: 300ms;/);
  assert.match(styles, /\.top-bar-refresh-tooltip-anchor:focus-within \.top-bar-refresh-tooltip \{[\s\S]*transition-delay: 0ms;/);
  assert.match(styles, /\.analytics-top-bar \.page-title-editor \{[\s\S]*height: 32px;[\s\S]*max-height: 32px;[\s\S]*overflow-x: auto;[\s\S]*overflow-y: hidden;[\s\S]*white-space: nowrap;/);
  assert.match(editablePageTitle, /return \(<input[\s\S]*type="text"/);
  assert.match(editablePageTitle, /event\.key === "Enter"[\s\S]*event\.preventDefault\(\);[\s\S]*event\.currentTarget\.blur\(\);/);
  assert.doesNotMatch(editablePageTitle, /<textarea/);
  assert.match(app, /const TOOLTIP_OPEN_DELAY_MS = 300;/);
  assert.match(app, /openTimerRef\.current = window\.setTimeout\([\s\S]*TOOLTIP_OPEN_DELAY_MS/);
  assert.match(app, /onFocus=\{openImmediately\} onMouseEnter=\{openAfterDelay\} onMouseLeave=\{closePopover\}/);
  assert.match(styles, /@media \(max-width: 760px\) \{[\s\S]*\.top-bar-refresh-datetime \{[\s\S]*max-width: min\(180px, 34vw\);/);
  assert.match(styles, /@media \(max-width: 560px\) \{[\s\S]*\.analytics-top-bar \{[\s\S]*flex-wrap: nowrap;[\s\S]*\.analytics-top-bar-actions \{[\s\S]*width: auto;/);
  assert.doesNotMatch(styles, /\.top-bar-refresh-text[^}]*display: none/);
  assert.match(app, /canRefresh: canHostPrompts && !hostedReadOnly && controls\.refresh !== false/);
  assert.match(app, /disabled=\{isEditMode\} onRefresh=\{capabilities\.canRefresh \? requestRefresh : undefined\}/);
  assert.match(app, /Published snapshot\. Last updated \$\{dateLabel\}/);
  assert.doesNotMatch(app, /<span>Refresh<\/span>\\n\{statusLabel/);
});

test("artifact chart edit modal uses contained modal chart chrome", () => {
  const app = read("../src/analytics-app/App.tsx");
  const appStyles = read("../src/analytics-app/styles.css");
  const runtimeEnvironment = read("../src/analytics-app/runtimeEnvironment.ts");
  const widget = read("../src/datascience-chart-widget.js");
  const widgetStyles = read("../src/datascience-chart-widget.css");

  assert.match(app, /loadInlineChartWidgetHtml\(widgetInstanceId\)/);
  assert.match(runtimeEnvironment, /inline-chart-widget\?displayMode=modal/);
  assert.match(runtimeEnvironment, /displayMode: "modal"/);
  assert.match(app, /function chartWidgetSettings\(chart\)/);
  assert.match(app, /settings\s*\n\s*\}/);
  assert.match(app, /datascience-chart-widget-spec-reset/);
  assert.match(app, /onChartSpecChange\(chart\.id, null\)/);
  assert.doesNotMatch(app, /chart-explore-header/);
  assert.match(appStyles, /\.native-modal\.chart-explore-modal \{[\s\S]*width: min\(1180px, calc\(100vw - 96px\)\);/);
  assert.match(widget, /function isDetailDisplayMode\(mode = displayMode\)/);
  assert.match(widget, /raw === "modal" \|\| raw === "dialog"/);
  assert.match(widget, /modal-title-close-button/);
  assert.match(widget, /requestDisplayMode\("inline"\)/);
  assert.match(widgetStyles, /\.widget\[data-display-mode="modal"\] \.detail-topbar \{[\s\S]*display: none;/);
  assert.match(widgetStyles, /\.widget\[data-display-mode="modal"\] \.bottom-split \{[\s\S]*display: none;/);
  assert.match(widgetStyles, /\.widget\[data-display-mode="modal"\] \.modal-title-close-button \{[\s\S]*display: inline-flex;/);
  assert.match(widgetStyles, /html\[data-display-mode="modal"\],\s*body\[data-display-mode="modal"\] \{[\s\S]*overflow: hidden;/);
  assert.match(widgetStyles, /\.widget\[data-display-mode="modal"\] \.chart-shell \{[\s\S]*height: 100%;[\s\S]*min-height: 0;/);
  assert.match(widgetStyles, /\.widget:is\(\[data-display-mode="fullscreen"\], \[data-display-mode="modal"\]\) \.detail-title-section h1 \{[\s\S]*font-size: 28px;[\s\S]*line-height: 34px;/);
  assert.doesNotMatch(widget, /segmented\.className = "segmented chart-setting-segmented"/);
  assert.match(widget, /function openSettingMenu\(anchor, label, value, options, onChange\)/);
  assert.doesNotMatch(widget, /panel\.appendChild\(menuHeader\(label\)\)/);
  assert.match(widget, /function settingDropdownChip\(label, value, options, onChange\)/);
  assert.match(widget, /button\.setAttribute\("aria-haspopup", "menu"\)/);
  assert.match(widget, /button\.append\(labelEl, caretIcon\("field-pill-caret"\)\)/);
  assert.match(widget, /\? "Chart type"\s*: chartTypeLabel\(activeVisualizationType\)/);
  assert.match(widget, /if \(!detailChrome\) button\.appendChild\(field\)/);
  assert.match(widget, /visibleSeries = \{\};/);
  assert.match(widget, /function notifyChartSpecReset\(\)/);
  assert.match(widget, /type: "datascience-chart-widget-spec-reset"/);
  assert.match(widget, /closeFieldMenus\(\{ immediate: true \}\)/);
  assert.match(widgetStyles, /\.detail-title-row \{[\s\S]*width: 100%;/);
  assert.match(widgetStyles, /\.widget:is\(\[data-display-mode="fullscreen"\], \[data-display-mode="modal"\]\) \.app-main \{[\s\S]*flex: 1 1 auto;[\s\S]*width: 100%;/);
  assert.match(widgetStyles, /\.widget:is\(\[data-display-mode="fullscreen"\], \[data-display-mode="modal"\]\) \.detail-title-section h1 \{[\s\S]*flex: 1 1 auto;/);
  assert.match(widgetStyles, /\.modal-title-close-button \{[\s\S]*margin-left: auto;/);
  const expandedResetRule = widgetStyles.match(
    /\.widget:is\(\[data-display-mode="fullscreen"\], \[data-display-mode="modal"\]\) \.clear-button \{[^}]*\}/,
  );
  assert.ok(expandedResetRule);
  assert.doesNotMatch(expandedResetRule[0], /margin-left: auto/);
});

test("artifact HTML exports delegate rendering details to the owning workflow", () => {
  const app = read("../src/analytics-app/App.tsx");
  const htmlDashboard = read("../skills/build-dashboard/specifications/html-dashboard.md");

  assert.match(app, /Use \$\{dataAnalyticsPluginMention\(packageInfo\)\} and invoke \$\{workflow\} in portable HTML mode/);
  assert.doesNotMatch(app, /Omit the interactive top bar and app-only controls from the exported artifact/);
  assert.match(htmlDashboard, /Keep portable HTML exports content-only:[\s\S]*omit the MCP app top bar and app-only controls/);
});

test("artifact fallback remains neutral and excludes sample report data", () => {
  const source = read("../src/datascience-artifact-widget.jsx");
  const fallback = source
    .split("const fallbackPayload =", 2)[1]
    .split("function createMemoryStorage", 1)[0];

  assert.match(fallback, /title: "Data Analytics artifact"/);
  assert.match(fallback, /description: "Waiting for an artifact payload\."/);
  assert.match(fallback, /id: "empty_state"/);
  assert.match(fallback, /status: "blocked"/);
  assert.match(fallback, /datasets: \{\}/);
  assert.doesNotMatch(source, /Local regression showcase|Synthetic weekly revenue fixture/);
  assert.doesNotMatch(source, /Weekly Revenue Performance|net_revenue_card|revenue_summary_table/);
  assert.doesNotMatch(source, /const hostedEmptyPayload/);
  assert.match(source, /requestArtifactDisplayMode\("fullscreen"/);
});

test("report and dashboard artifacts render inline with a single expand action", () => {
  const artifactSource = read("../src/datascience-artifact-widget.jsx");
  const app = read("../src/analytics-app/App.tsx");
  const styles = read("../src/analytics-app/styles.css");
  const host = read("../src/mcp-host.js");

  assert.match(artifactSource, /normalizeDisplayMode\([\s\S]*payload\?\.displayMode[\s\S]*\) \|\| "inline"/);
  assert.match(artifactSource, /const canRequestFullscreen =[\s\S]*displayMode !== "fullscreen";/);
  assert.match(artifactSource, /onRequestFullscreen=\{requestFullscreen\}/);
  assert.match(host, /initialDisplayMode/);
  assert.match(host, /rememberDismissedInitialDisplayMode\(name, "fullscreen"\)/);
  assert.match(host, /clearDismissedInitialDisplayMode\(name, "fullscreen"\)/);
  assert.match(host, /hasDismissedInitialDisplayMode\(name, normalized\)/);
  assert.doesNotMatch(artifactSource, /function ArtifactInlineLauncher/);
  assert.doesNotMatch(artifactSource, /showInlineLauncher/);
  assert.doesNotMatch(artifactSource, /datascience-artifact-inline-card/);
  assert.match(app, /function AnalyticsTopBar\(\{[\s\S]*onRequestFullscreen/);
  assert.match(app, /const showInlineExpand = chrome === "inline" && typeof onRequestFullscreen === "function";/);
  assert.match(app, /showInlineExpand \? \(<div className="analytics-top-bar-actions">/);
  assert.match(app, /<Expand aria-hidden="true" size=\{14\} strokeWidth=\{2\}\/>/);
  assert.match(app, /<span>Expand<\/span>/);
  assert.doesNotMatch(styles, /body\[data-display-mode="inline"\]/);
  assert.doesNotMatch(styles, /\.datascience-artifact-inline-card/);
  assert.doesNotMatch(styles, /\.datascience-artifact-display-button/);
});

test("artifact package export advertises its filesystem write behavior", () => {
  const exportTool = server.toolDefinitions().find((tool) => tool.name === "export_artifact_package");
  const renderTool = server.toolDefinitions().find((tool) => tool.name === "render_artifact");

  assert.ok(exportTool);
  assert.equal(exportTool.annotations.readOnlyHint, false);
  assert.equal(exportTool.annotations.destructiveHint, false);
  assert.equal(exportTool.annotations.idempotentHint, false);
  assert.deepEqual(exportTool.inputSchema.properties.site_editor_email.type, ["string", "null"]);
  assert.ok(renderTool);
  assert.equal(renderTool.annotations.readOnlyHint, true);
});

test("hosted read-only markdown does not expose edit affordances", () => {
  const richMarkdown = read("../src/analytics-app/layout/RichMarkdown.tsx");

  assert.match(richMarkdown, /const canEdit = isEditMode \|\| typeof onRequestEditMode === "function"/);
  assert.match(richMarkdown, /if \(!canEdit\) return;/);
  assert.match(richMarkdown, /aria-label=\{canEdit \? ariaLabel : undefined\}/);
  assert.match(richMarkdown, /role=\{canEdit \? "button" : undefined\}/);
  assert.match(richMarkdown, /tabIndex=\{canEdit \? 0 : undefined\}/);
});

test("hosted presentation actions remain owner-scoped", () => {
  const app = read("../src/analytics-app/App.tsx");
  const layoutCanvas = read("../src/analytics-app/layout/AnalyticsLayoutCanvas.tsx");

  assert.match(app, /const canEditPresentation = hostedPresentation[\s\S]*presentation\?\.canEdit === true[\s\S]*controls\.edit !== false[\s\S]*environmentCapabilities\.editContent !== false/);
  assert.match(app, /const canAgentHandoff = canEditPresentation && canHostPrompts && controls\.export !== false/);
  assert.match(app, /const canEditChartSpec = canEditPresentation && environmentCapabilities\.editVisualization !== false/);
  assert.match(app, /canEditChartSpec,/);
  assert.match(app, /canEditHtml: false/);
  assert.match(app, /canEditText: canEditPresentation/);
  assert.match(app, /const canReorder = canEditPresentation && environmentCapabilities\.reorderContent !== false/);
  assert.match(app, /canReorder,/);
  assert.match(app, /canResizeColumns: false/);
  assert.match(app, /const canDelete = canEditPresentation && environmentCapabilities\.deleteContent !== false && controls\.delete !== false/);
  assert.match(app, /canDelete,/);
  assert.match(app, /canRefresh: canEditPresentation && canHostPrompts && controls\.refresh !== false/);
  assert.match(app, /canExportHtml: canAgentHandoff && controls\.html !== false/);
  assert.match(app, /canExportPdf: canAgentHandoff && controls\.pdf !== false/);
  assert.match(app, /canExportDocument: canAgentHandoff && controls\.document !== false/);
  assert.match(app, /canExportSlides: canAgentHandoff && controls\.slides !== false/);
  assert.match(app, /const canExport = canHostPrompts && !hostedReadOnly && controls\.export !== false/);
  assert.match(app, /canExportHtml: canExport && controls\.html !== false/);
  assert.match(app, /canExportPdf: canExport && controls\.pdf !== false/);
  assert.match(app, /canExportDocument: canExport && controls\.document !== false/);
  assert.match(app, /canExportSlides: canExport && controls\.slides !== false/);
  assert.match(app, /const canDeleteBlocks = capabilities\.canDelete && \(!usesHostedPresentation \|\| activeEditMode\)/);
  assert.match(app, /onDeleteBlock=\{canDeleteBlocks \? \(\) => deleteReportBlock/);
  assert.doesNotMatch(app, /canRestoreDeletedBlocks|Restore deleted blocks|restoreDeletedReportBlocks/);
  assert.match(app, /mergeVisibleLayoutPreservingHidden\([\s\S]*deletedReportBlockIdsRef\.current/);
  assert.match(app, /const requestEditMode = capabilities\.canEdit \? beginEditMode : undefined/);
  assert.match(app, /canEditChartSpec \? "Edit chart" : "Explore chart"/);
  assert.match(app, /const modalLabel = `\$\{canEditChart \? "Edit" : "Explore"\} \$\{chart\.title\}`/);
  assert.match(app, /const packageInfo = useMemo\(\(\) => withHostedBootstrap\(normalizedArtifact\.packageInfo\)/);
  assert.match(app, /void loadHostedPresentation\(\)\.then/);
  assert.match(app, /saveHostedPresentation\(\{[\s\S]*artifactId: hostedPresentation\?\.artifactId[\s\S]*revision: hostedPresentation\?\.revision/);
  assert.match(app, /hostedOverrides\.deletedReportBlockIds[\s\S]*knownDeletableReportIds\.has\(id\)/);
  assert.match(app, /overrides\.deletedReportBlockIds = \[\.\.\.deletedReportBlockIds\]/);
  assert.match(app, /if \(!isPublishedArtifactSite\(packageInfo\)\) \{[\s\S]*originUrl[\s\S]*packageInfo\?\.root/);
  assert.match(app, /if \(isPublishedArtifactSite\(packageInfo\)\) \{[\s\S]*Published Site:[\s\S]*Artifact ID:/);
  assert.match(app, /if \(!usesHostedPresentation && !isEditMode && pageTitleTextStorageKey\)/);
  assert.match(app, /isEditMode=\{isEditMode && canEditHtml\}/);
  assert.match(app, /allowColumnResize=\{capabilities\.canResizeColumns\}/);
  assert.match(app, /storageKey=\{!usesHostedPresentation && capabilities\.canEdit \? reportStorageKey : null\}/);
  assert.match(app, /storageKey=\{!usesHostedPresentation && capabilities\.canEdit \? storageKey : null\}/);
  assert.match(layoutCanvas, /persistedLayout \?\? parseStoredLayout\(storageKey\)/);
  assert.match(layoutCanvas, /previousLoad\.persistenceVersion !== persistenceVersion/);
});

test("the MCP app offers user-initiated Sites publishing", () => {
  const app = read("../src/analytics-app/App.tsx");

  assert.match(app, /site: "Publish to Sites"/);
  assert.match(app, /Publish this finalized \$\{surface\} through Sites so I can share it with coworkers/);
  assert.match(app, /Call export_artifact_package with the project id and checkout path/);
});
