"use strict";

const fs = require("node:fs");
const crypto = require("node:crypto");
const os = require("node:os");
const path = require("node:path");
const readline = require("node:readline");
const childProcess = require("node:child_process");
const zlib = require("node:zlib");

const SERVER_NAME = "data-analytics-widgets";
const PLUGIN_ROOT = path.resolve(__dirname, "..");
const PLUGIN_MANIFEST = JSON.parse(
  fs.readFileSync(path.join(PLUGIN_ROOT, ".codex-plugin", "plugin.json"), "utf8"),
);
const SERVER_VERSION = PLUGIN_MANIFEST.version || "0.1.1";
const DATA_ANALYTICS_DISPLAY_NAME =
  PLUGIN_MANIFEST.interface?.displayName || "Data Analytics";
const DATA_ANALYTICS_ICON = {
  src: assetDataUrl("datascience-small.svg", "image/svg+xml"),
  mimeType: "image/svg+xml",
  sizes: ["24x24"],
};
const DATA_ANALYTICS_LOGO = {
  src: assetDataUrl("datascience.png", "image/png"),
  mimeType: "image/png",
  sizes: ["360x360"],
};
const DATA_ANALYTICS_ICONS = [DATA_ANALYTICS_ICON, DATA_ANALYTICS_LOGO];
const TABLE_WIDGET_URI = "ui://widget/datascience-table.html";
const CHART_WIDGET_BASE_URI = "ui://widget/datascience-chart.html";
const CHART_WIDGET_URI =
  `ui://widget/datascience-chart-${encodeURIComponent(SERVER_VERSION)}.html`;
const ARTIFACT_WIDGET_BASE_URI = "ui://widget/datascience-artifact.html";
const ARTIFACT_WIDGET_URI =
  `ui://widget/datascience-artifact-${encodeURIComponent(SERVER_VERSION)}.html`;
const WIDGET_RESOURCE_VERSION_PATTERN =
  /^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$/;
const WIDGET_MIME_TYPE = "text/html;profile=mcp-app";
const MEASURE_NAMES_FIELD = "__measure_names__";
const WIDGET_RESOURCE_DOMAINS = ["https://cdn.openai.com"];
const TOOL_NAMES = {
  validateArtifact: "validate_artifact",
  renderArtifact: "render_artifact",
  exportArtifactPackage: "export_artifact_package",
  renderChart: "render_chart",
  renderTable: "render_table",
};
const VALUE_FORMAT_DESCRIPTION =
  'Display format for numeric values. Use "percent" only for fractional-rate values: pass 0.98 for 98%, 1 for 100%, and 2 for 200%. If reviewed data is already in percentage points such as 98, use "number" with unit "%".';
const MAX_WIDGET_ROWS = 500;
const MAX_WIDGET_COLUMNS = 80;
const MAX_WIDGET_DATA_POINTS = 2000;
const MAX_WIDGET_CELLS = 12000;
const MAX_WIDGET_FIELD_NAME_CHARS = 128;
const MAX_WIDGET_CELL_STRING_CHARS = 4000;
const MAX_WIDGET_PAYLOAD_BYTES = 750000;
const MAX_ARTIFACT_DATASETS = 50;
const MAX_ARTIFACT_ROWS_PER_DATASET = 2000;
const MAX_ARTIFACT_PAYLOAD_BYTES = 3_000_000;
const MAX_ARTIFACT_INLINE_SOURCE_CHARS = 200_000;
const PRESENTATION_SCHEMA_SQL =
  "CREATE TABLE IF NOT EXISTS data_analytics_presentation_v1 (key TEXT PRIMARY KEY, revision INTEGER NOT NULL, overrides_json TEXT NOT NULL)";
const CANONICAL_CHART_TYPES = [
  "line",
  "area",
  "stackedArea",
  "bar",
  "histogram",
  "scatter",
  "heatmap",
  "pie",
  "leaderboard",
  "sparkline",
  "funnel",
  "waterfall",
  "boxPlot",
];
const CANONICAL_CHART_TYPE_SET = new Set(CANONICAL_CHART_TYPES);
const BAR_ORIENTATIONS = ["vertical", "horizontal"];
const BAR_GROUP_MODES = ["single", "grouped", "stacked", "stacked100"];
const TREND_POINT_MODES = ["always", "never"];
const SERIES_LINE_STYLES = ["solid", "dashed", "dotted"];
const COMPACT_BAR_CATEGORY_WARNING_THRESHOLD = 24;
const COMPACT_PIE_SEGMENT_WARNING_THRESHOLD = 8;
const UNSAFE_FIELD_PATTERNS = [
  "password",
  "passwd",
  "pwd",
  "secret",
  "api[-_]?key",
  "access[-_]?token",
  "refresh[-_]?token",
  "credential",
  "authorization",
  "cookie",
  "private[-_]?key",
  "session[-_]?id",
  "ssn",
  "social[-_]?security",
  "credit[-_]?card",
  "card[-_]?number",
  "cvv",
  "email[-_]?address",
  "user[-_]?email",
  "customer[-_]?email",
  "phone[-_]?number",
  "street[-_]?address",
  "ip[-_]?address",
  "raw[-_]?pii",
  "hidden[-_]?reasoning",
];
const UNSAFE_FIELD_NAME_PATTERN = new RegExp(
  `(^|[_\\-.])(${UNSAFE_FIELD_PATTERNS.join("|")})([_\\-.]|$)`,
  "i",
);

const WIDGET_TOOL_URIS = {
  [TOOL_NAMES.renderArtifact]: ARTIFACT_WIDGET_URI,
  [TOOL_NAMES.renderChart]: CHART_WIDGET_URI,
  [TOOL_NAMES.renderTable]: TABLE_WIDGET_URI,
};
const WIDGET_TOOL_VISIBILITY = {
  [TOOL_NAMES.renderArtifact]: ["model"],
  [TOOL_NAMES.renderChart]: ["model"],
  [TOOL_NAMES.renderTable]: ["model"],
};
const TOOL_INVOCATION_LABELS = {
  [TOOL_NAMES.renderArtifact]: {
    invoking: "Rendering artifact",
    invoked: "Rendered artifact",
  },
  [TOOL_NAMES.renderChart]: {
    invoking: "Rendering chart",
    invoked: "Rendered chart",
  },
  [TOOL_NAMES.renderTable]: {
    invoking: "Rendering table",
    invoked: "Rendered table",
  },
};
const WIDGET_DESCRIPTIONS = {
  [ARTIFACT_WIDGET_URI]:
    [
      "A hosted Data Analytics artifact app that renders dashboard and report manifests",
      "with bounded snapshots, source details, shared chart/table components, and agent-mediated",
      "refresh/export prompts.",
    ].join(" "),
  [TABLE_WIDGET_URI]:
    "A compact sortable Data Analytics table for reviewed query preview rows and lookup rows.",
  [CHART_WIDGET_URI]:
    [
      "A compact Data Analytics chart card that accepts provenance, a reviewed table,",
      "and a declarative chart spec, then expands into a full chart explorer",
      "app with field wells for re-encoding exploration-ready rows.",
    ].join(" "),
};
const WORK_MODE_WIDGET_DELIVERY_GUARD = [
  "When mode = work_mode is positively identified, regardless of surface,",
  "do not call render_artifact, render_chart, or render_table to deliver visuals or reports;",
  "the trusted Work Mode rendering path may drop standalone plugin widgets that lack appContext.",
  "Preserve the delivery mode already selected by the owning workflow. For already-selected inline",
  "visuals with exactly one supported bar, line, pie, or scatter chart, treat charts_widget_v2 as",
  "directly surfaced and emit its live genui content reference before fallback; use the outer shape",
  "genui{\"charts_widget_v2\":{\"content\":{...}}} without Markdown backticks, not",
  "standalone assistant text; do not self-declare it unavailable, search for it, or print its payload",
  "as bare JSON. Keep app_block conditional on",
  "the host surfacing it for a richer composition.",
  "For a durable report or dashboard in Work Mode, publish the validated artifact through Sites",
  "when the full Sites building and hosting lifecycle is callable, with HTML as the automatic fallback.",
  "Use image-based/static charting only after an",
  "emitted native reference is rejected or fails to render, or when no suitable native renderer exists;",
  "then use a compact table or other non-MCP fallback only when no visual renderer can be delivered.",
  "Use image-based/static charting for that native-render failure fallback or when the user",
  "explicitly requests Python, a static image/file, notebook-oriented output, or export. Do not",
  "say a visual rendered above unless the selected non-MCP or native Work Mode surface actually rendered.",
].join(" ");
const SERVER_INSTRUCTIONS = [
  "Before rendering a report or dashboard artifact, call validate_artifact with the",
  "complete manifest and bounded snapshot. Fix validation errors there first; do not use",
  "render_artifact as an iterative validator because failed render attempts can create",
  "visible placeholder cards. After validation passes outside Work Mode, use render_artifact to host the",
  "complete Data Analytics dashboard or report manifest with a bounded snapshot inside the MCP app;",
  "this is the default reader handoff outside Work Mode and should be attempted before",
  "static HTML, localhost, or file:// delivery.",
  WORK_MODE_WIDGET_DELIVERY_GUARD,
  "Artifact snapshots must be bounded: at most 50 datasets, 2,000 rows per dataset, 3MB total",
  "payload, and 200k total inline source characters. Use the canonical artifact snapshot shape:",
  "snapshot.datasets is an object keyed by dataset id, and each value is a plain array of row objects",
  "like {\"weekly_revenue\":[{\"week\":\"2026-05-04\",\"arr\":123}]}. Do not put {columns, rows}",
  "objects inside artifact snapshot datasets; table-shaped dataset objects are rejected.",
  "Use snapshot.accessIssues only when required report/dashboard data is missing and the snapshot",
  "status is partial or blocked. Do not use accessIssues for optional source limitations, denied",
  "exploratory joins, methodology caveats, or provenance notes when the artifact is otherwise ready;",
  "put those in manifest sources or markdown body blocks instead.",
  "All artifacts must declare a reader-facing manifest.title plus top-level manifest.blocks.",
  "Cards, charts, and tables define reusable renderable assets; blocks establish the artifact",
  "reading order. Report artifacts must include at least one chart data visualization block and",
  "a first markdown block whose body is a # heading matching manifest.title.",
  "Give each independently editable major report section its own markdown block. Do not put",
  "multiple peer ## headings in one markdown body; reserve ### headings for subordinate content",
  "that should remain in the same card. One headline metric does not mean one metrics[] entry:",
  "keep short, directly relevant directional comparisons as later labeled badge metrics, especially",
  "when the same comparison appears in the executive summary or findings.",
  "Native artifact charts must use encodings.x.field plus encodings.y.field or encodings.y.fields,",
  "with optional encodings.color.field for grouped tidy data. Legacy manifest chart fields",
  "xField and series are rejected; use validate_artifact to check chart shape before rendering.",
  "Give each native artifact table a defaultSort with a declared column field and asc or desc",
  "direction chosen to make the initial row order describe the data clearly.",
  "When a validated MCP artifact report or dashboard needs a hosted Sites link, call",
  "export_artifact_package and deploy that package instead of hand-rolling standalone HTML.",
  "In ChatGPT Desktop outside Work Mode, render the MCP artifact first and publish to Sites only after the user explicitly",
  "requests or accepts the optional coworker-sharing follow-up.",
  "The exporter preserves the real artifact runtime and serves /api/manifest, /api/snapshot,",
  "/api/package, /api/presentation, /api/source-file, and /api/inline-chart-widget, with db/schema.ts",
  "when presentation editing is enabled.",
  "Use render_chart after a Data Analytics workflow has already produced a small,",
  "shareable source query result.",
  "Pass source, table, chart, and display for chart widgets.",
  "Default every chart title to a neutral, descriptive label that identifies what is plotted,",
  "such as the metric, comparison, dimension, or time scope. Do not infer a narrative takeaway,",
  "claim, clever headline, or new jargon for the title unless the user explicitly requests one.",
  "Chart subtitles should add a reader-facing insight or takeaway not already covered by the",
  "title. Do not use subtitles for source names, query ids, table names, SQL intent, metric",
  "definitions, or provenance; put those details in source.query/source metadata instead.",
  "For chart widgets, make table exploration-ready: include useful dimensions,",
  "measures, time columns, and grouping columns returned by the reviewed query, not only the",
  "plotted chart fields.",
  "For scatter widgets, prefer one row per meaningful observation rather than a few broad",
  "aggregates, with a stable point label, numeric x and y measures at the same grain,",
  "denominator or sample-size fields, one volume/size candidate, and one interpretable grouping",
  "or filter field when safe.",
  "Treat by <dimension> in a chart title, subtitle, or visible header as an encoding contract.",
  "An x/y axis dimension already satisfies that contract. If <dimension> is not on an axis and",
  "is not otherwise visibly encoded through color/series, grouped or stacked marks, faceting,",
  "or direct labels, remove by <dimension> from the visible text. For render_chart, a time or",
  "category x-axis chart titled ... by segment or ... by market must bind that second dimension",
  "through chart.fields.color.field or an equivalent visible grouping rather than only retaining",
  "it in the source table.",
  "When a grouped chart uses color, series, grouped, stacked, or faceted behavior, make the",
  "group names visible with a legend or direct labels.",
  "Only set chart.fields.color.field when it is a meaningful",
  "grouping dimension such as segment, product_line, or series; omit color for single-series charts.",
  "For trend charts, chart.fields.lineStyle.field may point to a text column with solid, dashed,",
  "or dotted values so grouped lines and their legends use different stroke styles.",
  'Use chart.type "bar" plus chart.options.orientation and chart.options.grouping',
  "for bar-family charts.",
  "Prefer tidy long rows, keep the payload compact, set row_count and truncated when sampling,",
  "and order sampled rows deterministically.",
  "After running a durable query, use render_table to show a compact preview of reviewed",
  "rows before or alongside interpretation.",
  "Source SQL belongs in source.query.sql and must be runnable SQL, not prose. Put the",
  "human-readable query summary in source.query.description. Source metadata should name actual",
  "tables such as example.analytics.fact_revenue, and metric definitions should state calculations,",
  "windows, units, denominators, and material exclusions.",
  "Include reviewed analytical dimensions such as customer, account, company, segment, and product names when relevant.",
  "Do not send hidden reasoning, credentials, secrets, or direct personal contact/payment identifiers to widgets.",
].join(" ");

function assetDataUrl(fileName, mimeType) {
  const assetBytes = fs.readFileSync(path.join(PLUGIN_ROOT, "assets", fileName));
  return `data:${mimeType};base64,${assetBytes.toString("base64")}`;
}

function objectSchema(properties, required = [], additionalProperties = false) {
  return { type: "object", properties, required, additionalProperties };
}

function toolUiMeta(resourceUri, toolName = null) {
  const ui = { resourceUri };
  const visibility = WIDGET_TOOL_VISIBILITY[toolName || ""];
  if (visibility) ui.visibility = visibility;
  const meta = {
    ui,
    "ui/resourceUri": resourceUri,
    "openai/outputTemplate": resourceUri,
    "openai/widgetAccessible": true,
  };
  const invocationLabels = TOOL_INVOCATION_LABELS[toolName];
  if (invocationLabels != null) {
    meta["openai/toolInvocation/invoking"] = invocationLabels.invoking;
    meta["openai/toolInvocation/invoked"] = invocationLabels.invoked;
  }
  return meta;
}

function tool(name, title, description, inputSchema, outputTemplate, annotations = {}) {
  const definition = {
    name,
    title,
    description,
    inputSchema,
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false,
      ...annotations,
    },
  };
  if (outputTemplate) definition._meta = toolUiMeta(outputTemplate, name);
  return definition;
}

function toolDefinitions() {
  const scalar = { type: ["string", "number", "boolean", "null"] };
  const row = {
    type: "object",
    description: [
      "One reviewed result row. For chart widgets, include all useful fields needed",
      "for re-encoding in the expanded explorer, not only plotted x/y/series.",
    ].join(" "),
    additionalProperties: scalar,
  };
  const columnType = {
    type: ["string", "null"],
    enum: ["text", "number", "percent", "currency", "date", null],
  };
  const visualizationType = {
    type: "string",
    enum: CANONICAL_CHART_TYPES,
    description:
      'Use canonical chart.type values. Bar-family charts should use "bar" with chart.options.orientation and chart.options.grouping.',
  };
  const column = objectSchema(
    {
      key: { type: "string" },
      label: { type: ["string", "null"] },
      type: columnType,
      format: {
        type: ["string", "null"],
        enum: ["compact", "number", "percent", "currency", null],
        description: VALUE_FORMAT_DESCRIPTION,
      },
      unit: { type: ["string", "null"] },
      align: { type: ["string", "null"], enum: ["left", "right", "center", null] },
    },
    ["key"],
  );
  column.description = [
    "Column metadata for reviewed query results. Include useful fields from the source query",
    "so users can swap encodings in the expanded chart widget.",
  ].join(" ");
  const sourceQuery = objectSchema({
    engine: { type: ["string", "null"] },
    id: { type: ["string", "null"] },
    url: { type: ["string", "null"] },
    sql: {
      type: ["string", "null"],
      description:
        "Preferred field for the actual runnable SQL used to produce the exposed rows. Paste the executed SQL here; never put prose, methodology, or a summary here.",
    },
    description: {
      type: ["string", "null"],
      description:
        "High-level human-readable description of what the query does. Do not put runnable SQL here.",
    },
    language: { type: ["string", "null"] },
    executed_at: { type: ["string", "null"] },
    tables_used: {
      type: "array",
      items: { type: "string" },
      description:
        "Actual source table names used by the query, preferably fully qualified names such as example.analytics.fact_revenue.",
    },
    filters: {
      type: "array",
      items: { type: "string" },
      description:
        "Human-readable static source predicates, including date windows, population/cohort criteria, material exclusions, and sampling or limit rules.",
    },
    metric_definitions: {
      type: "array",
      items: { type: "string" },
      description:
        "Formulas and scope rules for displayed metrics, including windows, exclusions, denominators, and units.",
    },
  });
  const sourceSchema = objectSchema({
    id: { type: ["string", "null"] },
    label: { type: ["string", "null"] },
    path: { type: ["string", "null"] },
    href: { type: ["string", "null"] },
    query: sourceQuery,
  });
  const resultTable = {
    type: "object",
    description: [
      "Exploration-ready reviewed source query result. For chart widgets, prefer this over",
      "pre-shaped data points and include useful dimensions, measures, time,",
      "and grouping fields so users can change chart encodings in the expanded UI. For scatter",
      "charts, prefer one row per meaningful observation rather than a few broad aggregates,",
      "with a stable point label, numeric x and y measures at the same grain, denominator or",
      "sample-size fields, one volume/size candidate, and one interpretable grouping or filter",
      "field when safe. Keep the",
      "payload compact; set row_count to the full reviewed result count and truncated=true",
      "when rows are sampled.",
    ].join(" "),
    properties: {
      columns: {
        type: "array",
        items: column,
        default: [],
        description: "Column metadata for all useful fields exposed to the chart explorer.",
      },
      rows: {
        type: "array",
        items: row,
        default: [],
        description: "Reviewed rows to preview and re-encode. Prefer tidy long-form rows.",
      },
      row_count: {
        type: ["integer", "null"],
        minimum: 0,
        description:
          "Full reviewed result row count, even when rows contains a deterministic sample.",
      },
      truncated: {
        type: ["boolean", "null"],
        description: "True when rows is a safe deterministic sample of a larger reviewed result.",
      },
    },
    additionalProperties: true,
  };
  const encoding = {
    type: "object",
    properties: {
      field: { type: ["string", "null"] },
      type: {
        type: ["string", "null"],
        enum: ["nominal", "ordinal", "quantitative", "temporal", "text", null],
      },
      aggregate: {
        type: ["string", "null"],
        enum: ["none", "sum", "avg", "min", "max", "count", null],
      },
      time_unit: {
        type: ["string", "null"],
        enum: ["none", "year", "quarter", "month", "week", "day", "hour", "minute", "second", null],
      },
      label: { type: ["string", "null"] },
      unit: { type: ["string", "null"] },
    },
    additionalProperties: true,
  };
  const chartOptions = objectSchema({
    orientation: { type: ["string", "null"], enum: [...BAR_ORIENTATIONS, null] },
    grouping: { type: ["string", "null"], enum: [...BAR_GROUP_MODES, null] },
    points: { type: ["string", "null"], enum: [...TREND_POINT_MODES, null] },
    multi_measure_series: { type: ["boolean", "null"] },
  });
  const chart = objectSchema(
    {
      type: visualizationType,
      fields: objectSchema(
        {
          x: encoding,
          y: encoding,
          size: encoding,
          color: encoding,
          lineStyle: encoding,
          label: encoding,
        },
        ["x", "y"],
      ),
      options: chartOptions,
    },
    ["type", "fields"],
  );
  const display = objectSchema({
    unit: { type: ["string", "null"] },
    baseline: { type: ["number", "null"] },
    x_axis_title: {
      type: ["string", "null"],
      description: "X-axis title override. Defaults to the x field column label.",
    },
    y_axis_title: {
      type: ["string", "null"],
      description: "Y-axis title override. Defaults to the y field column label.",
    },
    controls: { type: ["boolean", "null"] },
  });
  const metric = objectSchema(
    {
      label: { type: "string" },
      value: scalar,
      delta: { type: ["string", "number", "null"] },
    },
    ["label", "value"],
  );
  const common = {
    title: { type: "string" },
    subtitle: { type: ["string", "null"] },
    source: sourceSchema,
  };

  const chartInputSchema = objectSchema(
    {
      title: {
        type: "string",
        description: [
          "Neutral, descriptive chart title identifying what is plotted, such as the metric,",
          "comparison, dimension, or time scope. Do not infer a narrative takeaway, claim, clever",
          "headline, or new jargon unless the user explicitly requests a takeaway-led title.",
        ].join(" "),
      },
      subtitle: {
        type: ["string", "null"],
        description: [
          "Optional reader-facing subtitle. Use it for a concise insight or takeaway not",
          "covered by the title. Do not put source names, query ids, table names, SQL intent,",
          "metric definitions, or provenance here; those belong in source.query/source metadata.",
        ].join(" "),
      },
      source: sourceSchema,
      table: resultTable,
      chart,
      display,
    },
    ["title", "source", "table", "chart"],
  );
  const tableInputSchema = objectSchema(
    {
      ...common,
      columns: { type: "array", items: column, default: [] },
      rows: { type: "array", items: row, default: [] },
      result_table: resultTable,
      max_rows: { type: "integer", minimum: 1, maximum: 500, default: 50 },
      metrics: { type: "array", items: metric, default: [] },
      notes: { type: "array", items: { type: "string" }, default: [] },
    },
    ["title", "source"],
  );
  const artifactMetricFormat = {
    type: ["string", "null"],
    enum: ["compact", "number", "percent", "currency", null],
    description: VALUE_FORMAT_DESCRIPTION,
  };
  const artifactCardMetric = objectSchema(
    {
      label: {
        type: "string",
        description: "Reader-facing metric label.",
      },
      field: {
        type: "string",
        description:
          "Dataset field to render. Metric cards do not support valueField, deltaField, indicators, or standalone card format fields.",
      },
      format: artifactMetricFormat,
      signed: {
        type: ["boolean", "null"],
        description: "Set true for signed deltas or movement metrics.",
      },
    },
    ["label", "field"],
  );
  const artifactCard = objectSchema(
    {
      id: { type: "string" },
      description: { type: ["string", "null"] },
      dataset: { type: "string" },
      sourceId: {
        type: ["string", "null"],
        description:
          "Reference to manifest.sources[] for this card's data-source modal. Required for cards used by dashboard or report metric-strip blocks unless source is provided inline.",
      },
      source: sourceSchema,
      filter: { type: "object", additionalProperties: scalar },
      metrics: {
        type: "array",
        minItems: 1,
        items: artifactCardMetric,
        description:
          "One headline metric followed by concise comparison context for that same metric, such as a prior-period value, target, or delta. One headline does not mean one metrics[] entry: include a short directional comparison when it is decision-relevant, especially when the same comparison appears in the executive summary or findings. Put independent secondary metrics in their own cards, charts, tables, or narrative. Use metrics[].field and signed: true for signed changes; do not use legacy card fields such as valueField, deltaField, label, title, format, or indicators.",
      },
    },
    ["id", "dataset", "metrics"],
  );
  const artifactChartEncoding = objectSchema(
    {
      field: { type: ["string", "null"] },
      fields: { type: "array", items: { type: "string" } },
      type: {
        type: ["string", "null"],
        enum: ["nominal", "ordinal", "quantitative", "temporal", "text", null],
      },
      aggregate: {
        type: ["string", "null"],
        enum: ["none", "sum", "avg", "min", "max", "count", "countDistinct", null],
      },
      format: artifactMetricFormat,
      label: { type: ["string", "null"] },
      unit: { type: ["string", "null"] },
    },
    [],
    true,
  );
  const artifactChartEncodings = objectSchema(
    {
      x: artifactChartEncoding,
      y: artifactChartEncoding,
      color: artifactChartEncoding,
      size: artifactChartEncoding,
      facet: artifactChartEncoding,
      label: artifactChartEncoding,
      tooltip: { type: "array", items: artifactChartEncoding },
    },
    [],
    true,
  );
  const artifactSource = sourceSchema;
  const artifactChart = objectSchema(
    {
      id: { type: "string" },
      title: {
        type: "string",
        description: [
          "Neutral, descriptive chart title identifying what is plotted, such as the metric,",
          "comparison, dimension, or time scope. Do not infer a narrative takeaway, claim, clever",
          "headline, or new jargon unless the user explicitly requests a takeaway-led title.",
        ].join(" "),
      },
      subtitle: { type: ["string", "null"] },
      showDescription: { type: ["boolean", "null"] },
      headerMarkdown: { type: ["string", "null"] },
      intent: { type: ["string", "null"] },
      question: { type: ["string", "null"] },
      rationale: { type: ["string", "null"] },
      comparisonContext: { type: "object", additionalProperties: true },
      type: {
        type: "string",
        enum: [
          "line",
          "area",
          "stackedArea",
          "bar",
          "horizontalBar",
          "stackedBar",
          "stackedBar100",
          "horizontalStackedBar",
          "horizontalStackedBar100",
          "histogram",
          "scatter",
          "heatmap",
          "pie",
          "leaderboard",
          "sparkline",
          "funnel",
          "waterfall",
          "boxPlot",
        ],
      },
      dataset: { type: "string" },
      sourceId: { type: ["string", "null"] },
      source: sourceSchema,
      encodings: artifactChartEncodings,
      xAxisTitle: { type: ["string", "null"] },
      yAxisTitle: { type: ["string", "null"] },
      valueFormat: artifactMetricFormat,
      unit: { type: ["string", "null"] },
      layout: { type: ["string", "null"] },
      combinationRationale: { type: ["string", "null"] },
      maxRows: { type: ["integer", "null"], minimum: 1 },
      referenceLines: { type: "array", items: { type: "object", additionalProperties: true } },
      emptyState: { type: ["string", "null"] },
      compatibleTypes: { type: "array", items: { type: "string" } },
      surface: { type: "object", additionalProperties: true },
    },
    ["id", "title", "type", "dataset"],
    true,
  );
  const artifactTableColumn = objectSchema(
    {
      field: {
        type: "string",
        description:
          "Dataset field to display. Artifact report tables use field, not the standalone table widget's key property.",
      },
      label: { type: "string" },
      format: artifactMetricFormat,
      movement: { type: ["boolean", "null"] },
      role: { type: ["string", "null"] },
      semantic: { type: ["string", "null"] },
      type: { type: ["string", "null"], enum: ["text", "number", "percent", "currency", "date", null] },
      unit: { type: ["string", "null"] },
      align: { type: ["string", "null"], enum: ["left", "right", "center", null] },
    },
    ["field", "label"],
  );
  const artifactTableDefaultSort = objectSchema(
    {
      field: {
        type: "string",
        description: "Declared table column field used for the initial row order.",
      },
      direction: {
        type: "string",
        enum: ["asc", "desc"],
        description: "Initial sort direction.",
      },
    },
    ["field", "direction"],
  );
  const artifactTable = objectSchema(
    {
      id: { type: "string" },
      title: { type: "string" },
      subtitle: { type: ["string", "null"] },
      showDescription: { type: ["boolean", "null"] },
      headerMarkdown: { type: ["string", "null"] },
      dataset: { type: "string" },
      density: { type: ["string", "null"], enum: ["compact", "comfortable", "spacious", null] },
      sourceId: { type: ["string", "null"] },
      source: sourceSchema,
      layout: { type: ["string", "null"] },
      defaultSort: {
        ...artifactTableDefaultSort,
        description:
          "Initial table sort chosen to make the first view answer the table's question. The field must appear in columns.",
      },
      columns: {
        type: "array",
        minItems: 1,
        items: artifactTableColumn,
        description:
          "Artifact table columns. Use columns[].field; do not use columns[].key in manifest.tables.",
      },
    },
    ["id", "title", "dataset", "columns"],
  );
  const artifactBlock = objectSchema(
    {
      id: { type: "string" },
      type: {
        type: "string",
        enum: ["markdown", "metric-strip", "chart", "table", "html"],
      },
      body: {
        type: "string",
        description:
          'Block body for markdown or html blocks. For report markdown blocks other than the first # title block, give each independently editable major section its own block with one peer ## heading; use ### only for subordinate content that belongs in the same card. HTML blocks contain raw HTML and do not use Markdown heading syntax. Markdown blocks render body; do not use "markdown", "content", "text", "title", "html", or "height" block fields.',
      },
      cardIds: {
        type: "array",
        minItems: 1,
        items: { type: "string" },
        description:
          'Required for type "metric-strip"; references one or more manifest.cards[].id values in display order. There is no preferred or maximum card count: include all and only decision-relevant metrics.',
      },
      chartId: {
        type: "string",
        description: 'Required for type "chart"; references manifest.charts[].id.',
      },
      tableId: {
        type: "string",
        description: 'Required for type "table"; references manifest.tables[].id.',
      },
      sourceId: {
        type: ["string", "null"],
        description:
          "Optional block-wide provenance for a markdown block whose quantitative claims all come from one canonical source. The id must resolve against the merged canonical sources. Split mixed-provenance claims into separate blocks, omit sourceId on title-only or prose-only blocks, and never guess a source. File and document sources are valid and do not require SQL.",
      },
      layout: { type: ["string", "null"] },
    },
    ["id", "type"],
  );
  const artifactManifest = {
    type: "object",
    description: [
      "Dashboard/report manifest. All artifact manifests must declare renderable content as",
      "top-level manifest.blocks. The blocks array establishes the artifact reading order.",
      "manifest.title is required. Reports also render it as the first content heading.",
      "Report artifacts must include at least one chart data visualization block.",
    ].join(" "),
    properties: {
      version: { type: "integer", enum: [1] },
      surface: { type: ["string", "null"], enum: ["dashboard", "report", null] },
      title: {
        type: "string",
        description:
          "Reader-facing artifact title. Required for dashboards and reports; reports also render it as the first content heading.",
      },
      description: { type: ["string", "null"] },
      generatedAt: { type: ["string", "null"] },
      filters: { type: "array", items: { type: "object", additionalProperties: true }, default: [] },
      cards: { type: "array", items: artifactCard, default: [] },
      charts: { type: "array", items: artifactChart, default: [] },
      tables: { type: "array", items: artifactTable, default: [] },
      sources: { type: "array", items: artifactSource, default: [] },
      blocks: {
        type: "array",
        items: artifactBlock,
        default: [],
        description:
          "Top-level artifact blocks. Required for dashboards and reports; array order is the artifact reading path. Markdown blocks use type \"markdown\" with body: string. Give each independently editable major report section its own markdown block rather than putting multiple peer ## headings in one body. Metric strips use type \"metric-strip\" with cardIds. Custom HTML blocks use type \"html\" with raw HTML in body and auto-size to content. The content, text, markdown, title, html, and height fields are not part of the artifact block contract.",
      },
    },
    required: ["version", "title", "blocks"],
    additionalProperties: true,
  };
  const artifactSnapshot = {
    type: "object",
    description: [
      "Bounded artifact snapshot: max 50 datasets and 2,000 rows per dataset.",
      "Canonical shape: snapshot.datasets is an object keyed by dataset id, and each value",
      "is a plain array of reviewed row objects. Example: {\"weekly_revenue\":[{\"week\":\"2026-05-04\",\"arr\":123}]}.",
      "Do not use {columns, rows} for artifact datasets; table-shaped dataset objects are rejected.",
    ].join(" "),
    properties: {
      version: { type: "integer", enum: [1] },
      generatedAt: { type: ["string", "null"] },
      status: {
        type: ["string", "null"],
        enum: ["ready", "partial", "blocked", "fixture", null],
      },
      datasets: {
        type: "object",
        additionalProperties: { type: "array", items: row },
      },
      accessIssues: {
        type: "array",
        items: { type: "object", additionalProperties: true },
        default: [],
        description:
          "Required-data access failures for partial or blocked artifacts only. Do not use for optional source limitations or caveats in ready artifacts.",
      },
    },
    required: ["version", "datasets"],
    additionalProperties: true,
  };
  const artifactInputSchema = objectSchema(
    {
      surface: { type: "string", enum: ["dashboard", "report"] },
      manifest: artifactManifest,
      snapshot: artifactSnapshot,
      sources: {
        type: "array",
        items: artifactSource,
        default: [],
        description:
          "Optional inline source query payloads for source ids or paths already declared in manifest.sources.",
      },
      package_info: {
        type: ["object", "null"],
        additionalProperties: true,
        description:
          "Optional provenance metadata for display only. File paths are never read by the MCP server; include bounded source query text explicitly in sources[].query.sql.",
      },
    },
    ["surface", "manifest", "snapshot"],
  );
  const artifactPackageExportInputSchema = {
    ...artifactInputSchema,
    properties: {
      ...artifactInputSchema.properties,
      output_dir: {
        type: ["string", "null"],
        description:
          "Optional output directory for the Sites package. Pass the checkout returned by the Sites worker-starter lifecycle to update its worker source in place, or an empty shared-workspace directory for standalone export. Desktop-only calls may omit it and use a deterministic OS temp directory.",
      },
      site_creator_project_id: {
        type: ["string", "null"],
        description:
          "Optional existing Sites project id to persist in .openai/hosting.json and dist/.openai/hosting.json. The field name is retained for exporter compatibility.",
      },
      site_editor_email: {
        type: ["string", "null"],
        description:
          "Optional verified creator identity for presentation-only Site editing. Pass the sole resolved email while the Site is still verifiably owner-only, before widening reader access. The exporter stores only a SHA-256 hash in worker source. Omit this field to preserve an existing editor seed or disabled state across republishing, and pass null explicitly to disable editing.",
      },
    },
  };
  return [
    tool(
      TOOL_NAMES.validateArtifact,
      "Validate Artifact",
      [
        "Validate a Data Analytics dashboard/report manifest and bounded snapshot",
        "without rendering a hosted widget. Use this first while iterating on artifact shape;",
        "outside Work Mode, only call render_artifact after validation succeeds to avoid creating",
        "visible broken placeholder cards. snapshot.accessIssues is reserved for missing",
        "required data in partial or blocked artifacts; use markdown body blocks or source notes for optional",
        "source limitations in ready artifacts. All artifacts require manifest.title and",
        "manifest.blocks.",
      ].join(" "),
      artifactInputSchema,
    ),
    tool(
      TOOL_NAMES.renderArtifact,
      "Render Artifact",
      [
        "Render a hosted Data Analytics dashboard or report artifact from a generated manifest",
        "and bounded snapshot. Use this when the user should see the full dashboard/report app",
        "inside MCP without running a local server. Call validate_artifact first",
        "while iterating on manifest shape so invalid attempts do not create visible broken",
        "artifact cards. snapshot.accessIssues is reserved for missing required data in partial",
        "or blocked artifacts; use markdown body blocks or source notes for optional source limitations in",
        "ready artifacts. All artifacts require manifest.title and manifest.blocks.",
        "Do not use this tool as the report delivery surface whenever mode = work_mode is positively",
        "identified, regardless of surface. For a durable report or dashboard in Work Mode, publish the",
        "validated artifact through Sites when the full Sites building and hosting lifecycle is callable,",
        "with HTML as the fallback.",
        "That trusted rendering path can drop standalone plugin widgets without appContext.",
        "A successful tool result is not delivery confirmation in that runtime.",
        "Refresh and export controls are v1 agent-mediated prompts; do not",
        "include live connector refresh actions.",
      ].join(" "),
      artifactInputSchema,
      ARTIFACT_WIDGET_URI,
    ),
    tool(
      TOOL_NAMES.exportArtifactPackage,
      "Export Artifact Package",
      [
        "Materialize the current Data Analytics dashboard/report artifact as a Sites-ready",
        "Cloudflare Worker package. This exporter preserves the real MCP artifact app runtime instead",
        "of generating standalone report HTML. It writes worker/index.js for the Sites source checkout,",
        "dist/server/index.js, dist/client assets,",
        ".openai/hosting.json, dist/.openai/hosting.json, optional db/schema.ts, and an archive that serves",
        "/api/manifest, /api/snapshot, /api/package, /api/presentation, /api/source-file, and",
        "/api/inline-chart-widget from the validated payload.",
        "Use this before publishing MCP artifact reports through Sites; do not hand-roll a",
        "separate HTML renderer.",
      ].join(" "),
      artifactPackageExportInputSchema,
      undefined,
      {
        readOnlyHint: false,
        idempotentHint: false,
      },
    ),
    tool(
      TOOL_NAMES.renderChart,
      "Render Chart",
      [
        "Render a compact Data Analytics chart from already-reviewed provenance and table data.",
        "Pass source.query.sql with the actual SQL used to produce the chart table, plus source.query.description for the human-readable query summary, an exploration-ready table, chart, and display.",
        "Do not call this tool for inline visual delivery whenever mode = work_mode is positively",
        "identified, regardless of surface;",
        "for an already-selected inline visual with exactly one supported bar, line, pie, or scatter chart,",
        "treat charts_widget_v2 as directly surfaced and emit its live genui content reference before fallback;",
        "use the outer shape genui{\"charts_widget_v2\":{\"content\":{...}}} without Markdown",
        "backticks, not standalone assistant text; do not self-declare it unavailable, search for it,",
        "or print its payload as bare JSON.",
        "Keep app_block conditional on the host surfacing it for a richer composition.",
        "Use image-based/static charting only after an emitted native reference is rejected or fails to render,",
        "or when no suitable native renderer exists, with a compact table or other non-MCP fallback only",
        "when no visual renderer can be delivered.",
        "Use image-based/static charting for that native-render failure fallback or when the user explicitly requests Python, a static image/file, notebook-oriented output, or export.",
        "A successful tool result is not delivery confirmation in that runtime.",
        "Default the title to a neutral, descriptive label that identifies what is plotted, such as the metric, comparison, dimension, or time scope. Do not infer a narrative takeaway, claim, clever headline, or new jargon unless the user explicitly requests a takeaway-led title.",
        "Use the subtitle for a reader-facing insight or takeaway not covered by the title, not for source names, query ids, table names, SQL intent, metric definitions, or provenance.",
        "The table should retain useful",
        "dimensions, measures, time columns, and grouping columns so users can change",
        "chart fields in the expanded widget. Only pass chart.fields.color.field for meaningful",
        "grouping dimensions like segment, product_line, or series; omit it for single-series charts.",
        "For scatter charts, prefer one row per meaningful observation rather than a few broad aggregates; retain a stable point label, numeric x and y measures at the same grain, denominator or sample-size fields, one volume/size candidate, and one interpretable grouping or filter field when safe.",
        "Treat by <dimension> in a visible chart title, subtitle, or header as an encoding contract:",
        "if that dimension is not on an x/y axis, visibly encode it through chart.fields.color.field",
        "or equivalent grouped, stacked, faceted, or direct-label behavior; when grouped, show a",
        "legend or direct labels.",
        "For line, area, stackedArea, and sparkline charts, chart.fields.lineStyle.field can reference a column with solid, dashed, or dotted values.",
        'Use chart.type "bar" plus',
        "chart.options.orientation and chart.options.grouping for bar-family charts.",
      ].join(" "),
      chartInputSchema,
      CHART_WIDGET_URI,
    ),
    tool(
      TOOL_NAMES.renderTable,
      "Render Table",
      [
        "Render a compact sortable Data Analytics table from already-reviewed query preview rows",
        "or exact lookup rows. Use after running a durable query when the user should see the",
        "sampled rows that support the analysis. Pass source.query.sql with the same actual SQL",
        "source payload shape used by chart widgets so the expanded table detail view can show the query.",
        "Do not call this tool for inline table delivery whenever mode = work_mode is positively",
        "identified, regardless of surface;",
        "use native Work Mode table rendering when available, or a compact conversational/static table fallback.",
        "A successful tool result is not delivery confirmation in that runtime.",
      ].join(" "),
      tableInputSchema,
      TABLE_WIDGET_URI,
    ),
  ];
}

function decodedWidgetResourceVersion(encodedVersion) {
  try {
    return decodeURIComponent(encodedVersion);
  } catch {
    return null;
  }
}

function parsedWidgetResourceVersion(version) {
  const match = WIDGET_RESOURCE_VERSION_PATTERN.exec(version);
  if (!match) return null;
  const prerelease = match[4] ? match[4].split(".") : [];
  const hasInvalidNumericPrerelease = prerelease.some(
    (identifier) => /^\d+$/.test(identifier) && identifier.length > 1 && identifier.startsWith("0"),
  );
  if (hasInvalidNumericPrerelease) return null;
  return {
    core: [BigInt(match[1]), BigInt(match[2]), BigInt(match[3])],
    prerelease,
  };
}

function compareWidgetResourceVersions(left, right) {
  for (let index = 0; index < left.core.length; index += 1) {
    if (left.core[index] < right.core[index]) return -1;
    if (left.core[index] > right.core[index]) return 1;
  }
  if (!left.prerelease.length && !right.prerelease.length) return 0;
  if (!left.prerelease.length) return 1;
  if (!right.prerelease.length) return -1;
  const identifierCount = Math.max(left.prerelease.length, right.prerelease.length);
  for (let index = 0; index < identifierCount; index += 1) {
    const leftIdentifier = left.prerelease[index];
    const rightIdentifier = right.prerelease[index];
    if (leftIdentifier == null) return -1;
    if (rightIdentifier == null) return 1;
    if (leftIdentifier === rightIdentifier) continue;
    const leftIsNumeric = /^\d+$/.test(leftIdentifier);
    const rightIsNumeric = /^\d+$/.test(rightIdentifier);
    if (leftIsNumeric && rightIsNumeric) {
      return BigInt(leftIdentifier) < BigInt(rightIdentifier) ? -1 : 1;
    }
    if (leftIsNumeric) return -1;
    if (rightIsNumeric) return 1;
    return leftIdentifier < rightIdentifier ? -1 : 1;
  }
  return 0;
}

function isSupportedWidgetResourceVersion(version) {
  const requested = parsedWidgetResourceVersion(version);
  const current = parsedWidgetResourceVersion(SERVER_VERSION);
  if (requested == null || current == null) return false;
  const precedence = compareWidgetResourceVersions(requested, current);
  return precedence < 0 || (precedence === 0 && version === SERVER_VERSION);
}

function matchesWidgetResourceUri(uri, baseUri, resourceName) {
  if (typeof uri !== "string") return false;
  if (uri === baseUri) return true;

  const queryPrefix = `${baseUri}?v=`;
  if (uri.startsWith(queryPrefix)) {
    const version = decodedWidgetResourceVersion(uri.slice(queryPrefix.length));
    return version != null && isSupportedWidgetResourceVersion(version);
  }

  const pathPrefix = `ui://widget/${resourceName}-`;
  const pathSuffix = ".html";
  if (!uri.startsWith(pathPrefix) || !uri.endsWith(pathSuffix)) return false;
  const encodedVersion = uri.slice(pathPrefix.length, -pathSuffix.length);
  const version = decodedWidgetResourceVersion(encodedVersion);
  return version != null && isSupportedWidgetResourceVersion(version);
}

function canonicalWidgetUri(uri) {
  if (matchesWidgetResourceUri(uri, ARTIFACT_WIDGET_BASE_URI, "datascience-artifact")) {
    return ARTIFACT_WIDGET_URI;
  }
  if (matchesWidgetResourceUri(uri, CHART_WIDGET_BASE_URI, "datascience-chart")) {
    return CHART_WIDGET_URI;
  }
  if (uri === TABLE_WIDGET_URI) return TABLE_WIDGET_URI;
  return null;
}

function widgetResourceMeta(uri) {
  const canonicalUri = canonicalWidgetUri(uri) || uri;
  const description = WIDGET_DESCRIPTIONS[canonicalUri] || "A Data Analytics widget.";
  return {
    "openai/widgetDescription": description,
    "openai/widgetPrefersBorder": false,
    "openai/widgetCSP": { connect_domains: [], resource_domains: WIDGET_RESOURCE_DOMAINS, frame_domains: [] },
    ui: {
      prefersBorder: false,
      csp: { connectDomains: [], resourceDomains: WIDGET_RESOURCE_DOMAINS, frameDomains: [] },
    },
  };
}

function resources() {
  return [
    {
      uri: ARTIFACT_WIDGET_URI,
      name: "datascience_artifact_app",
      title: "Data Analytics artifact app",
      description: WIDGET_DESCRIPTIONS[ARTIFACT_WIDGET_URI],
      mimeType: WIDGET_MIME_TYPE,
      _meta: widgetResourceMeta(ARTIFACT_WIDGET_URI),
    },
    {
      uri: TABLE_WIDGET_URI,
      name: "datascience_table_widget",
      title: "Data Analytics table widget",
      description: WIDGET_DESCRIPTIONS[TABLE_WIDGET_URI],
      mimeType: WIDGET_MIME_TYPE,
      _meta: widgetResourceMeta(TABLE_WIDGET_URI),
    },
    {
      uri: CHART_WIDGET_URI,
      name: "datascience_chart_widget",
      title: "Data Analytics chart widget",
      description: WIDGET_DESCRIPTIONS[CHART_WIDGET_URI],
      mimeType: WIDGET_MIME_TYPE,
      _meta: widgetResourceMeta(CHART_WIDGET_URI),
    },
  ];
}

function resourceText(uri) {
  const canonicalUri = canonicalWidgetUri(uri);
  if (canonicalUri === ARTIFACT_WIDGET_URI) {
    return readWidgetHtmlAsset("datascience-artifact-widget.html");
  }
  if (canonicalUri === TABLE_WIDGET_URI) {
    return readWidgetHtmlAsset("datascience-table-widget.html");
  }
  if (canonicalUri === CHART_WIDGET_URI) {
    return readWidgetHtmlAsset("datascience-chart-widget.html");
  }
  throw new Error(`unknown Data Analytics widget resource: ${uri}`);
}

function readWidgetHtmlAsset(fileName) {
  const assetDir = path.join(PLUGIN_ROOT, "assets");
  const prefix = `${fileName}.gz.b64.part`;
  const chunks = fs
    .readdirSync(assetDir)
    .filter((name) => name.startsWith(prefix))
    .sort();
  if (!chunks.length) {
    throw new Error(`missing widget asset chunks for ${fileName}; run npm run build from plugins/datascience`);
  }

  const encoded = chunks
    .map((name) => fs.readFileSync(path.join(assetDir, name), "utf8").trim())
    .join("");
  return zlib.gunzipSync(Buffer.from(encoded, "base64")).toString("utf8");
}

function knownResourceUri(uri) {
  return Boolean(canonicalWidgetUri(uri));
}

function isPlainObject(value) {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function asObject(value) {
  return isPlainObject(value) ? { ...value } : {};
}

function asList(value) {
  return Array.isArray(value) ? value : [];
}

function firstValue(...values) {
  for (const value of values) {
    if (value !== null && value !== undefined && value !== "") return value;
  }
  return null;
}

function titleCaseKey(key) {
  return String(key)
    .replace(/_/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function isScalar(value) {
  return value === null || ["string", "number", "boolean"].includes(typeof value);
}

function validateFieldName(key, fieldPath) {
  if (key.length > MAX_WIDGET_FIELD_NAME_CHARS) {
    throw new Error(`${fieldPath} field name exceeds ${MAX_WIDGET_FIELD_NAME_CHARS} characters`);
  }
  if (UNSAFE_FIELD_NAME_PATTERN.test(key)) {
    throw new Error(`${fieldPath} field name ${JSON.stringify(key)} looks unsafe for widget rendering`);
  }
}

function validateSafetyFlags(value, fieldPath) {
  for (const key of ["safe_to_render", "reviewed"]) {
    if (value[key] === false) throw new Error(`${fieldPath}.${key} must not be false for widget rendering`);
  }
}

function validateCellValue(value, fieldPath) {
  if (!isScalar(value)) throw new Error(`${fieldPath} must be a scalar widget cell value`);
  if (typeof value === "string" && value.length > MAX_WIDGET_CELL_STRING_CHARS) {
    throw new Error(`${fieldPath} string exceeds ${MAX_WIDGET_CELL_STRING_CHARS} characters`);
  }
}

function validateRows(rows, fieldPath, maxRows = MAX_WIDGET_ROWS, maxCells = MAX_WIDGET_CELLS) {
  if (rows.length > maxRows) throw new Error(`${fieldPath} has ${rows.length} rows; maximum is ${maxRows}`);
  let cellCount = 0;
  rows.forEach((row, rowIndex) => {
    if (!isPlainObject(row)) throw new Error(`${fieldPath}[${rowIndex}] must be an object`);
    Object.entries(row).forEach(([key, value]) => {
      validateFieldName(key, `${fieldPath}[${rowIndex}]`);
      validateCellValue(value, `${fieldPath}[${rowIndex}].${key}`);
      cellCount += 1;
      if (cellCount > maxCells) throw new Error(`${fieldPath} has more than ${maxCells} cells`);
    });
  });
  return cellCount;
}

function validateColumns(columns, fieldPath) {
  if (columns.length > MAX_WIDGET_COLUMNS) {
    throw new Error(`${fieldPath} has ${columns.length} columns; maximum is ${MAX_WIDGET_COLUMNS}`);
  }
  columns.forEach((column, columnIndex) => {
    if (!isPlainObject(column)) throw new Error(`${fieldPath}[${columnIndex}] must be an object`);
    if (typeof column.key === "string") validateFieldName(column.key, `${fieldPath}[${columnIndex}].key`);
    for (const metadataKey of ["label", "unit"]) {
      const value = column[metadataKey];
      if (typeof value === "string" && value.length > MAX_WIDGET_CELL_STRING_CHARS) {
        throw new Error(
          `${fieldPath}[${columnIndex}].${metadataKey} exceeds ${MAX_WIDGET_CELL_STRING_CHARS} characters`,
        );
      }
    }
  });
}

function validateResultTable(resultTable, fieldPath) {
  if (!isPlainObject(resultTable)) return;
  validateSafetyFlags(resultTable, fieldPath);
  validateColumns(asList(resultTable.columns), `${fieldPath}.columns`);
  validateRows(asList(resultTable.rows), `${fieldPath}.rows`);
}

function validateWidgetPayload(payload) {
  validateSafetyFlags(payload, "$");
  const encoded = JSON.stringify(payload);
  if (Buffer.byteLength(encoded, "utf8") > MAX_WIDGET_PAYLOAD_BYTES) {
    throw new Error(`widget payload exceeds ${MAX_WIDGET_PAYLOAD_BYTES} bytes; pass a compact reviewed sample`);
  }
  if (payload.table) validateResultTable(payload.table, "$.table");
  else validateResultTable(payload.result_table, "$.result_table");
  if (Array.isArray(payload.rows)) validateRows(payload.rows, "$.rows");
  if (Array.isArray(payload.columns)) validateColumns(payload.columns, "$.columns");
  if (Array.isArray(payload.data)) validateRows(payload.data, "$.data", MAX_WIDGET_DATA_POINTS);
}

function validatedWidgetPayload(payload) {
  validateWidgetPayload(payload);
  return payload;
}

function validateIdentifier(value, fieldPath) {
  if (value == null) return;
  if (typeof value !== "string") throw new Error(`${fieldPath} must be a string`);
  validateFieldName(value, fieldPath);
}

function requireIdentifier(value, fieldPath) {
  if (typeof value !== "string" || !value) throw new Error(`${fieldPath} is required`);
  validateFieldName(value, fieldPath);
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

function validateNoLegacyArtifactChartFields(chart, fieldPath) {
  for (const key of ["xField", "series"]) {
    if (chart[key] != null) {
      throw new Error(`${fieldPath}.${key} is not supported for artifact charts; use encodings`);
    }
  }
}

function validateChartEncodingSpec(chart, fieldPath, { requireType = false } = {}) {
  validateNoLegacyArtifactChartFields(chart, fieldPath);
  if (!hasChartEncodingSpec(chart)) {
    throw new Error(`${fieldPath}.encodings.x.field and ${fieldPath}.encodings.y.field or ${fieldPath}.encodings.y.fields are required for artifact charts`);
  }
  if (requireType) requireIdentifier(chart.type, `${fieldPath}.type`);
  requireIdentifier(chart.id, `${fieldPath}.id`);
  requireIdentifier(chart.dataset, `${fieldPath}.dataset`);
  requireIdentifier(chartEncodingField(chart, "x"), `${fieldPath}.encodings.x.field`);
  const yField = chartEncodingField(chart, "y");
  const yFields = chartEncodingFields(chart, "y");
  if (yField) validateIdentifier(yField, `${fieldPath}.encodings.y.field`);
  if (yFields.length) yFields.forEach((field, index) => validateIdentifier(field, `${fieldPath}.encodings.y.fields[${index}]`));
  if (!yField && !yFields.length) {
    throw new Error(`${fieldPath}.encodings.y must declare field or fields`);
  }
  for (const role of ["color", "size", "facet", "label"]) {
    validateIdentifier(chartEncodingField(chart, role), `${fieldPath}.encodings.${role}.field`);
  }
  asList(chartEncoding(chart, "tooltip")).forEach((tooltip, index) => {
    if (!isPlainObject(tooltip)) throw new Error(`${fieldPath}.encodings.tooltip[${index}] must be an object`);
    validateIdentifier(tooltip.field, `${fieldPath}.encodings.tooltip[${index}].field`);
  });
  return true;
}

function normalizeSourceList(value) {
  if (Array.isArray(value)) return value.filter(isPlainObject).map((source) => ({ ...source }));
  return [];
}

function sourceKey(source) {
  if (!isPlainObject(source)) return null;
  for (const key of ["id", "path", "href"]) {
    if (typeof source[key] === "string" && source[key]) return source[key];
  }
  return null;
}

function mergeArtifactSources(manifest, sources) {
  const outputByKey = new Map();
  const output = [];

  function addSource(source) {
    if (!isPlainObject(source)) return;
    const key = sourceKey(source);
    if (!key) return;
    const existing = outputByKey.get(key);
    const candidate = { ...(existing || {}), ...source };
    if (existing) Object.assign(existing, candidate);
    else {
      outputByKey.set(key, candidate);
      output.push(candidate);
    }
  }

  sources.forEach(addSource);
  asList(manifest.sources).forEach(addSource);
  return output;
}

function declaredSourceKeys(manifest) {
  const keys = new Set();
  for (const source of asList(manifest.sources)) {
    if (!isPlainObject(source)) continue;
    for (const key of ["id", "path", "href"]) {
      if (typeof source[key] === "string" && source[key]) keys.add(source[key]);
    }
  }
  return keys;
}

function validateManifestSources(manifest) {
  asList(manifest.sources).forEach((source, index) => {
    if (!isPlainObject(source)) throw new Error(`$.manifest.sources[${index}] must be an object`);
    if (source.id != null) validateIdentifier(source.id, `$.manifest.sources[${index}].id`);
    for (const key of ["label", "path", "href"]) {
      if (source[key] != null && typeof source[key] !== "string") {
        throw new Error(`$.manifest.sources[${index}].${key} must be a string`);
      }
    }
  });
}

function stripLeadingSqlComments(text) {
  return String(text || "")
    .replace(/^\s*(?:--[^\n]*\n\s*)+/u, "")
    .replace(/^\s*(?:\/\*[\s\S]*?\*\/\s*)+/u, "")
    .trim();
}

function looksLikeSqlQuery(text) {
  const stripped = stripLeadingSqlComments(text);
  if (!stripped) return false;
  return (
    /^(with|select|insert|create|replace|merge|update|delete|copy|explain)\b/iu.test(stripped) ||
    /\bselect\b[\s\S]+\bfrom\b/iu.test(stripped)
  );
}

function firstSqlText(...values) {
  for (const value of values) {
    if (typeof value === "string" && looksLikeSqlQuery(value)) return value;
  }
  return null;
}

function actualSqlTextFromSourceQuery(value) {
  const query = asObject(value);
  return firstSqlText(query.sql);
}

function actualSqlTextFromSourceLike(value) {
  const source = asObject(value);
  return actualSqlTextFromSourceQuery(source.query);
}

function hasSqlFileSource(value) {
  const source = asObject(value);
  return [source.path, source.href].some((item) => {
    if (typeof item !== "string") return false;
    const lower = item.toLowerCase();
    return lower.endsWith(".sql") || lower.includes(".sql?");
  });
}

function validateActualSqlSource(value, fieldPath, { allowSqlFile = false } = {}) {
  const sourceQuery = asObject(asObject(value).query);
  const declaredQuery = sourceQuery.sql;
  const sqlText = actualSqlTextFromSourceLike(value);
  if (typeof sqlText === "string" && looksLikeSqlQuery(sqlText)) return;
  if (typeof declaredQuery === "string" && declaredQuery.trim()) {
    throw new Error(`${fieldPath} must include the actual SQL query text used to produce widget source data`);
  }
  if (allowSqlFile && hasSqlFileSource(value)) return;
  throw new Error(`${fieldPath} must include the actual SQL query text used to produce widget source data`);
}

function sourceForArtifactItem(item, sources) {
  if (isPlainObject(item.source)) return item.source;
  const sourceId = typeof item.sourceId === "string" ? item.sourceId : null;
  if (!sourceId) return null;
  return sources.find((source) => isPlainObject(source) && source.id === sourceId) || null;
}

const REPORT_BLOCK_TYPES = new Set([
  "markdown",
  "metric-strip",
  "chart",
  "table",
  "html",
]);
const MARKDOWN_REPORT_BLOCK_TYPES = new Set(["markdown"]);

function hasVisibleHtml(block) {
  return typeof block.body === "string" && block.body.trim();
}

function hasVisibleReportText(block) {
  return typeof block.body === "string" && block.body.trim();
}

function validateReportRenderableCard(card, fieldPath) {
  if (!isPlainObject(card)) throw new Error(`${fieldPath} must reference a manifest card object`);
  for (const key of ["id", "dataset"]) {
    requireIdentifier(card[key], `${fieldPath}.${key}`);
  }
  const metrics = asList(card.metrics);
  if (!metrics.length) throw new Error(`${fieldPath}.metrics must contain at least one metric object`);
  metrics.forEach((metric, metricIndex) => {
    if (!isPlainObject(metric)) throw new Error(`${fieldPath}.metrics[${metricIndex}] must be an object`);
    requireIdentifier(metric.label, `${fieldPath}.metrics[${metricIndex}].label`);
    requireIdentifier(metric.field, `${fieldPath}.metrics[${metricIndex}].field`);
  });
}

function validateReportRenderableChart(chart, fieldPath) {
  if (!isPlainObject(chart)) throw new Error(`${fieldPath} must reference a manifest chart object`);
  validateChartEncodingSpec(chart, fieldPath, { requireType: true });
}

function validateReportRenderableTable(table, fieldPath) {
  if (!isPlainObject(table)) throw new Error(`${fieldPath} must reference a manifest table object`);
  for (const key of ["id", "dataset"]) {
    requireIdentifier(table[key], `${fieldPath}.${key}`);
  }
  const columns = asList(table.columns);
  if (!columns.length) {
    throw new Error(`${fieldPath}.columns must contain at least one column object for artifact rendering`);
  }
  columns.forEach((column, columnIndex) => {
    if (!isPlainObject(column)) throw new Error(`${fieldPath}.columns[${columnIndex}] must be an object`);
    requireIdentifier(column.field, `${fieldPath}.columns[${columnIndex}].field`);
  });
}

function validateArtifactTableDefaultSort(table, fieldPath) {
  if (table.defaultSort == null) return;
  if (!isPlainObject(table.defaultSort)) {
    throw new Error(`${fieldPath}.defaultSort must be an object`);
  }
  requireIdentifier(table.defaultSort.field, `${fieldPath}.defaultSort.field`);
  if (!["asc", "desc"].includes(table.defaultSort.direction)) {
    throw new Error(`${fieldPath}.defaultSort.direction must be asc or desc`);
  }
  const columnFields = new Set(
    asList(table.columns)
      .filter(isPlainObject)
      .map((column) => column.field),
  );
  if (!columnFields.has(table.defaultSort.field)) {
    throw new Error(`${fieldPath}.defaultSort.field must reference a declared table column`);
  }
}

function validateArtifactBlockManifestShape(manifest, surface) {
  if (manifest.blocks != null && !Array.isArray(manifest.blocks)) {
    throw new Error("$.manifest.blocks must be an array of top-level artifact blocks");
  }

  const blocks = asList(manifest.blocks);
  if (!blocks.length) {
    throw new Error(
      "$.manifest.blocks must contain top-level artifact blocks",
    );
  }

  const cardsById = new Map(asList(manifest.cards).filter(isPlainObject).map((card) => [card.id, card]));
  const chartsById = new Map(asList(manifest.charts).filter(isPlainObject).map((chart) => [chart.id, chart]));
  const tablesById = new Map(asList(manifest.tables).filter(isPlainObject).map((table) => [table.id, table]));
  const blockIds = new Set();
  let renderableBlockCount = 0;
  let chartBlockCount = 0;

  blocks.forEach((block, index) => {
    if (!isPlainObject(block)) throw new Error(`$.manifest.blocks[${index}] must be an object`);
    validateIdentifier(block.id, `$.manifest.blocks[${index}].id`);
    validateIdentifier(block.sourceId, `$.manifest.blocks[${index}].sourceId`);
    if (typeof block.id !== "string" || !block.id) {
      throw new Error(`$.manifest.blocks[${index}].id is required for artifact rendering`);
    }
    if (blockIds.has(block.id)) throw new Error(`$.manifest.blocks[${index}].id duplicates ${JSON.stringify(block.id)}`);
    blockIds.add(block.id);

    if (typeof block.type !== "string" || !REPORT_BLOCK_TYPES.has(block.type)) {
      throw new Error(
        `$.manifest.blocks[${index}].type must be one of ${Array.from(REPORT_BLOCK_TYPES).join(", ")}`,
      );
    }
    if (MARKDOWN_REPORT_BLOCK_TYPES.has(block.type)) {
      for (const field of ["bodyMarkdown", "content", "markdown", "text"]) {
        if (block[field] != null) {
          throw new Error(`$.manifest.blocks[${index}] uses ${field}, but markdown blocks render body; use body instead`);
        }
      }
      if (block.title != null) {
        throw new Error(`$.manifest.blocks[${index}] uses title, but markdown blocks render body; include headings in body instead`);
      }
      if (block.html != null) {
        throw new Error(`$.manifest.blocks[${index}] uses html, but markdown blocks render body; use body instead`);
      }
      if (typeof block.body !== "string" || !block.body.trim()) {
        throw new Error(`$.manifest.blocks[${index}].body must be a non-empty string`);
      }
    }

    if (MARKDOWN_REPORT_BLOCK_TYPES.has(block.type) && hasVisibleReportText(block)) renderableBlockCount += 1;
    if (block.type === "html") {
      if (block.height != null) {
        throw new Error(`$.manifest.blocks[${index}].height is not supported for html blocks; html blocks auto-size to content`);
      }
      for (const field of ["bodyMarkdown", "content", "html", "markdown", "text", "title"]) {
        if (block[field] != null) {
          throw new Error(`$.manifest.blocks[${index}] uses ${field}, but html blocks render body; use body instead`);
        }
      }
      if (!hasVisibleHtml(block)) {
        throw new Error(`$.manifest.blocks[${index}].body must be a non-empty HTML string`);
      }
      renderableBlockCount += 1;
    }
    if (block.type === "metric-strip") {
      const cardIds = asList(block.cardIds);
      if (!cardIds.length) {
        throw new Error(`$.manifest.blocks[${index}].cardIds must reference at least one manifest card`);
      }
      cardIds.forEach((cardId, cardIndex) => {
        validateIdentifier(cardId, `$.manifest.blocks[${index}].cardIds[${cardIndex}]`);
        if (!cardsById.has(cardId)) {
          throw new Error(`$.manifest.blocks[${index}].cardIds[${cardIndex}] does not match a manifest card`);
        }
        validateReportRenderableCard(cardsById.get(cardId), `$.manifest.cards[${JSON.stringify(cardId)}]`);
      });
      renderableBlockCount += 1;
    }
    if (block.type === "chart") {
      validateIdentifier(block.chartId, `$.manifest.blocks[${index}].chartId`);
      if (!chartsById.has(block.chartId)) throw new Error(`$.manifest.blocks[${index}].chartId does not match a manifest chart`);
      validateReportRenderableChart(chartsById.get(block.chartId), `$.manifest.charts[${JSON.stringify(block.chartId)}]`);
      renderableBlockCount += 1;
      chartBlockCount += 1;
    }
    if (block.type === "table") {
      validateIdentifier(block.tableId, `$.manifest.blocks[${index}].tableId`);
      if (!tablesById.has(block.tableId)) throw new Error(`$.manifest.blocks[${index}].tableId does not match a manifest table`);
      validateReportRenderableTable(tablesById.get(block.tableId), `$.manifest.tables[${JSON.stringify(block.tableId)}]`);
      renderableBlockCount += 1;
    }
  });

  if (!renderableBlockCount) {
    throw new Error("$.manifest.blocks does not contain any renderable artifact content");
  }
  if (surface === "report" && !chartBlockCount) {
    throw new Error("$.manifest.blocks must include at least one chart block for report artifacts");
  }
}

function validateArtifactManifest(manifest, surface) {
  if (!isPlainObject(manifest)) throw new Error("$.manifest must be an object");
  if (manifest.version !== 1) throw new Error("$.manifest.version must be 1");
  const manifestSurface = manifest.surface;
  if (manifestSurface != null && manifestSurface !== surface) {
    throw new Error("$.manifest.surface must match $.surface");
  }
  if (typeof manifest.title !== "string" || !manifest.title.trim()) {
    throw new Error("$.manifest.title is required for artifact rendering");
  }
  if (manifest.audience != null) {
    throw new Error("$.manifest.audience is not supported for artifact rendering");
  }
  if (manifest.freshness != null) {
    throw new Error("$.manifest.freshness is not supported for artifact rendering");
  }
  validateSafetyFlags(manifest, "$.manifest");
  validateManifestSources(manifest);

  asList(manifest.cards).forEach((card, index) => {
    if (!isPlainObject(card)) throw new Error(`$.manifest.cards[${index}] must be an object`);
    for (const key of ["valueField", "format", "label", "title", "indicators", "deltaField", "deltaLabel"]) {
      if (card[key] != null) throw new Error(`$.manifest.cards[${index}].${key} is not supported; use metrics[]`);
    }
    for (const key of ["id", "dataset", "sourceId"]) {
      validateIdentifier(card[key], `$.manifest.cards[${index}].${key}`);
    }
    if (!Array.isArray(card.metrics) || !card.metrics.length) {
      throw new Error(`$.manifest.cards[${index}].metrics must contain at least one metric object`);
    }
    card.metrics.forEach((metric, metricIndex) => {
      if (!isPlainObject(metric)) {
        throw new Error(`$.manifest.cards[${index}].metrics[${metricIndex}] must be an object`);
      }
      validateIdentifier(metric.label, `$.manifest.cards[${index}].metrics[${metricIndex}].label`);
      validateIdentifier(metric.field, `$.manifest.cards[${index}].metrics[${metricIndex}].field`);
      validateIdentifier(metric.format, `$.manifest.cards[${index}].metrics[${metricIndex}].format`);
      if (metric.signed != null && typeof metric.signed !== "boolean") {
        throw new Error(`$.manifest.cards[${index}].metrics[${metricIndex}].signed must be a boolean`);
      }
      if (metric.movement != null) {
        throw new Error(`$.manifest.cards[${index}].metrics[${metricIndex}].movement is not supported; use signed`);
      }
    });
  });

  asList(manifest.charts).forEach((chart, index) => {
    if (!isPlainObject(chart)) throw new Error(`$.manifest.charts[${index}] must be an object`);
    validateChartEncodingSpec(chart, `$.manifest.charts[${index}]`, { requireType: true });
  });

  asList(manifest.tables).forEach((table, index) => {
    if (!isPlainObject(table)) throw new Error(`$.manifest.tables[${index}] must be an object`);
    for (const key of ["id", "dataset"]) validateIdentifier(table[key], `$.manifest.tables[${index}].${key}`);
    asList(table.columns).forEach((column, columnIndex) => {
      if (!isPlainObject(column)) {
        throw new Error(`$.manifest.tables[${index}].columns[${columnIndex}] must be an object`);
      }
      validateIdentifier(column.field, `$.manifest.tables[${index}].columns[${columnIndex}].field`);
    });
    validateArtifactTableDefaultSort(table, `$.manifest.tables[${index}]`);
  });

  validateArtifactBlockManifestShape(manifest, surface);
}

function validateArtifactSnapshot(snapshot) {
  if (!isPlainObject(snapshot)) throw new Error("$.snapshot must be an object");
  if (snapshot.version !== 1) throw new Error("$.snapshot.version must be 1");
  const status = snapshot.status;
  if (status != null && !["ready", "partial", "blocked", "fixture"].includes(status)) {
    throw new Error("$.snapshot.status must be ready, partial, blocked, or fixture");
  }
  if (!isPlainObject(snapshot.datasets)) throw new Error("$.snapshot.datasets must be an object");
  if (snapshot.definitions != null) {
    throw new Error("$.snapshot.definitions is not supported for artifact rendering");
  }
  const accessIssues = asList(snapshot.accessIssues);
  if (accessIssues.length && status !== "partial" && status !== "blocked") {
    throw new Error(
      "$.snapshot.accessIssues is only allowed when $.snapshot.status is partial or blocked; use a markdown body block or manifest.sources for optional source limitations in ready artifacts",
    );
  }
  const datasets = Object.entries(snapshot.datasets);
  if (datasets.length > MAX_ARTIFACT_DATASETS) {
    throw new Error(`$.snapshot.datasets has ${datasets.length} datasets; maximum is ${MAX_ARTIFACT_DATASETS}`);
  }
  datasets.forEach(([datasetId, rows]) => {
    validateIdentifier(datasetId, `$.snapshot.datasets.${datasetId}`);
    if (!Array.isArray(rows)) {
      throw new Error(`$.snapshot.datasets.${datasetId} must be an array of row objects`);
    }
    validateRows(
      rows,
      `$.snapshot.datasets.${datasetId}`,
      MAX_ARTIFACT_ROWS_PER_DATASET,
      Number.POSITIVE_INFINITY,
    );
  });
}

function normalizeArtifactSnapshot(snapshot) {
  const datasets = {};
  for (const [datasetId, value] of Object.entries(asObject(snapshot.datasets))) {
    const rows = isPlainObject(value) ? value.rows : value;
    datasets[datasetId] = asList(rows).filter(isPlainObject).map((row) => ({ ...row }));
  }
  return {
    ...snapshot,
    datasets,
  };
}

function normalizeArtifactManifest(manifest, surface) {
  const normalized = {
    ...manifest,
    surface: manifest.surface ?? surface,
  };
  if (surface === "dashboard") {
    normalized.blocks = Array.isArray(manifest.blocks) ? manifest.blocks : [];
  }
  if (Array.isArray(manifest.blocks)) {
    normalized.blocks = manifest.blocks.map((block) => {
      if (!isPlainObject(block)) return block;
      return { ...block };
    });
  }
  return normalized;
}

function validateArtifactSources(payload) {
  const declared = declaredSourceKeys(payload.manifest);
  let totalInlineChars = 0;
  payload.sources.forEach((source, index) => {
    if (!isPlainObject(source)) throw new Error(`$.sources[${index}] must be an object`);
    if (source.id != null) validateIdentifier(source.id, `$.sources[${index}].id`);
    const queryText = asObject(source.query).sql;
    const hasInlineQuery = typeof queryText === "string" && queryText.length > 0;
    if (!hasInlineQuery) return;
    const id = typeof source.id === "string" ? source.id : "";
    const pathValue = typeof source.path === "string" ? source.path : "";
    if (!declared.has(id) && !declared.has(pathValue)) {
      throw new Error(`$.sources[${index}].query.sql is only allowed for sources declared in manifest.sources`);
    }
    totalInlineChars += queryText.length;
    if (totalInlineChars > MAX_ARTIFACT_INLINE_SOURCE_CHARS) {
      throw new Error(
        `inline source text exceeds ${MAX_ARTIFACT_INLINE_SOURCE_CHARS} characters; pass a bounded source excerpt`,
      );
    }
  });
}

function validateArtifactMarkdownSourceReferences(manifest, sources) {
  const sourceIds = new Set(
    asList(sources)
      .filter(isPlainObject)
      .map((source) => source.id)
      .filter((sourceId) => typeof sourceId === "string" && sourceId),
  );
  asList(manifest.blocks).forEach((block, index) => {
    if (!isPlainObject(block) || block.type !== "markdown" || block.sourceId == null) return;
    if (!sourceIds.has(block.sourceId)) {
      throw new Error(
        `$.manifest.blocks[${index}].sourceId ${JSON.stringify(block.sourceId)} does not resolve to a canonical merged source`,
      );
    }
  });
}

function validateArtifactDatasetReferences(manifest, snapshot) {
  const datasets = new Set(Object.keys(snapshot.datasets || {}));
  const references = [
    ...asList(manifest.cards).map((item) => item.dataset),
    ...asList(manifest.charts).map((item) => item.dataset),
    ...asList(manifest.tables).map((item) => item.dataset),
  ].filter(Boolean);
  for (const dataset of references) {
    if (!datasets.has(dataset) && snapshot.status !== "blocked") {
      throw new Error(`$.snapshot.datasets is missing dataset ${JSON.stringify(dataset)}`);
    }
  }
}

function validateArtifactChartDataCompatibility(manifest, snapshot) {
  const datasets = snapshot.datasets || {};
  asList(manifest.charts).forEach((chart, index) => {
    if (!isPlainObject(chart)) return;
    const rows = asList(datasets[chart.dataset]).filter(isPlainObject);
    if (!rows.length) return;
    if (hasChartEncodingSpec(chart)) {
      const yFields = [
        chartEncodingField(chart, "y"),
        ...chartEncodingFields(chart, "y"),
      ].filter(Boolean);
      yFields.forEach((field, fieldIndex) => {
        const hasNumericValue = rows.some((row) => numeric(row[field]) != null);
        if (!hasNumericValue) {
          throw new Error(
            `$.manifest.charts[${index}].encodings.y${fieldIndex ? ".fields" : ".field"} ${JSON.stringify(field)} ` +
              "must reference a numeric dataset field with at least one numeric value",
          );
        }
      });
      return;
    }
    asList(chart.series).forEach((item, seriesIndex) => {
      if (!isPlainObject(item) || typeof item.field !== "string") return;
      const hasNumericValue = rows.some((row) => numeric(row[item.field]) != null);
      if (!hasNumericValue) {
        throw new Error(
          `$.manifest.charts[${index}].series[${seriesIndex}].field ${JSON.stringify(item.field)} ` +
            "must reference a numeric dataset field with at least one numeric value",
        );
      }
    });
  });
}

function validateArtifactSourceQueries(manifest, sources) {
  const cardIds = new Set(
    asList(manifest.blocks)
      .filter((block) => isPlainObject(block) && block.type === "metric-strip")
      .flatMap((block) => asList(block.cardIds))
      .filter((cardId) => typeof cardId === "string"),
  );
  asList(manifest.cards).forEach((card, index) => {
    if (!isPlainObject(card) || !cardIds.has(card.id)) return;
    const cardSource = sourceForArtifactItem(card, sources);
    validateActualSqlSource(cardSource, `$.manifest.cards[${index}].source`, {
      allowSqlFile: true,
    });
  });
  const chartBlocks = new Set(
    asList(manifest.blocks)
      .filter((block) => isPlainObject(block) && block.type === "chart" && typeof block.chartId === "string")
      .map((block) => block.chartId),
  );
  asList(manifest.charts).forEach((chart, index) => {
    if (!isPlainObject(chart)) return;
    if (chartBlocks.size && !chartBlocks.has(chart.id)) return;
    const chartSource = sourceForArtifactItem(chart, sources);
    validateActualSqlSource(chartSource, `$.manifest.charts[${index}].source`, {
      allowSqlFile: true,
    });
  });
  const tableBlocks = new Set(
    asList(manifest.blocks)
      .filter((block) => isPlainObject(block) && block.type === "table" && typeof block.tableId === "string")
      .map((block) => block.tableId),
  );
  asList(manifest.tables).forEach((table, index) => {
    if (!isPlainObject(table)) return;
    if (tableBlocks.size && !tableBlocks.has(table.id)) return;
    const tableSource = sourceForArtifactItem(table, sources);
    validateActualSqlSource(tableSource, `$.manifest.tables[${index}].source`, {
      allowSqlFile: true,
    });
  });
}

function validateArtifactPayload(payload) {
  validateSafetyFlags(payload, "$");
  if (payload.surface !== "dashboard" && payload.surface !== "report") {
    throw new Error('surface must be "dashboard" or "report"');
  }
  validateArtifactManifest(payload.manifest, payload.surface);
  validateArtifactSnapshot(payload.snapshot);
  validateArtifactDatasetReferences(payload.manifest, payload.snapshot);
  validateArtifactChartDataCompatibility(payload.manifest, payload.snapshot);
  validateArtifactSources(payload);
  validateArtifactMarkdownSourceReferences(payload.manifest, payload.sources);
  validateArtifactSourceQueries(payload.manifest, payload.sources);
  const encoded = JSON.stringify(payload);
  if (Buffer.byteLength(encoded, "utf8") > MAX_ARTIFACT_PAYLOAD_BYTES) {
    throw new Error(`artifact payload exceeds ${MAX_ARTIFACT_PAYLOAD_BYTES} bytes; pass a bounded snapshot`);
  }
}

function buildArtifactPayload(args) {
  if (args.initial_view != null) {
    throw new Error("initial_view is not supported for artifact rendering; artifacts open fullscreen by default");
  }
  const surface = args.surface;
  const manifest = normalizeArtifactManifest(asObject(args.manifest), surface);
  const snapshot = asObject(args.snapshot);
  const sources = normalizeSourceList(args.sources);
  const packageInfo = asObject(args.package_info);
  const mergedSources = mergeArtifactSources(manifest, sources);
  return {
    ok: true,
    widget_type: "artifact",
    surface,
    manifest,
    snapshot,
    sources: mergedSources,
    package_info: Object.keys(packageInfo).length ? packageInfo : null,
    packageInfo: Object.keys(packageInfo).length ? packageInfo : null,
  };
}

function validatedArtifactPayload(payload) {
  validateArtifactPayload(payload);
  return payload;
}

function artifactId(payload) {
  return crypto.createHash("sha256").update(JSON.stringify(payload)).digest("hex");
}

function safeHtmlJson(value) {
  return JSON.stringify(value).replace(/</g, "\\u003c").replace(/>/g, "\\u003e");
}

function hostedArtifactHtml(html, payload) {
  const packageInfo = asObject(payload.package_info || payload.packageInfo);
  const editingEnabled = packageInfo.hostedEditing === "presentation";
  const hosting = {
    editing: editingEnabled ? "presentation" : null,
    mode: "site_creator",
    readOnly: true,
    controls: {
      delete: editingEnabled,
      edit: editingEnabled,
      export: editingEnabled,
      exportHostedLink: false,
      refresh: editingEnabled,
      hostedLink: false,
      html: editingEnabled,
      pdf: editingEnabled,
      document: editingEnabled,
      slides: editingEnabled,
    },
  };
  const script = [
    "<script>",
    `window.__DATASCIENCE_ARTIFACT_HOSTING__=${safeHtmlJson(hosting)};`,
    "window.openai=Object.assign({},window.openai,{",
    `toolOutput:${safeHtmlJson(payload)},`,
    `toolResponseMetadata:${safeHtmlJson(payload)},`,
    'availableDisplayModes:["inline","fullscreen"],',
    'displayMode:"fullscreen",',
    'hostContext:{availableDisplayModes:["inline","fullscreen"],displayMode:"fullscreen"}',
    "});",
    "</script>",
  ].join("");
  if (/<head(\s[^>]*)?>/i.test(html)) {
    return html.replace(/<head(\s[^>]*)?>/i, (match) => `${match}\n${script}`);
  }
  return `${script}\n${html}`;
}

function inlineSourceText(source) {
  if (!isPlainObject(source)) return null;
  const query = asObject(source.query);
  if (typeof query.sql === "string") return query.sql;
  if (typeof source.text === "string") return source.text;
  if (typeof source.source === "string") return source.source;
  return null;
}

function sourceLookupEntries(payload) {
  const entries = [];
  const seen = new Set();
  for (const source of [...asList(payload.manifest?.sources), ...asList(payload.sources)]) {
    if (!isPlainObject(source)) continue;
    const text = inlineSourceText(source);
    if (text == null) continue;
    for (const key of [source.path, source.id, source.href]) {
      if (typeof key !== "string" || !key || seen.has(key)) continue;
      seen.add(key);
      entries.push([key, text]);
    }
  }
  return entries;
}

function normalizeOutputDir(outputDir, id) {
  if (outputDir == null || outputDir === "") {
    return {
      outputDir: path.join(os.tmpdir(), `datascience-artifact-site-${id.slice(0, 12)}`),
      isDefault: true,
    };
  }
  if (typeof outputDir !== "string") {
    throw new Error("output_dir must be a string when provided");
  }
  return { outputDir: path.resolve(outputDir), isDefault: false };
}

function ensureWritableOutputDir(outputDir, isDefault) {
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
    return false;
  }
  const entries = fs.readdirSync(outputDir);
  if (!entries.length) return false;
  if (isDefault && path.basename(outputDir).startsWith("datascience-artifact-site-")) {
    fs.rmSync(outputDir, { recursive: true, force: true });
    fs.mkdirSync(outputDir, { recursive: true });
    return false;
  }
  if (
    fs.existsSync(path.join(outputDir, ".openai", "hosting.json")) &&
    fs.existsSync(path.join(outputDir, "worker", "index.js"))
  ) {
    return true;
  }
  throw new Error(`output_dir already exists and is not empty: ${outputDir}`);
}

function readHostingConfig(filePath) {
  try {
    const value = JSON.parse(fs.readFileSync(filePath, "utf8"));
    if (!isPlainObject(value)) throw new Error("hosting config must be an object");
    return value;
  } catch (error) {
    throw new Error(`failed to read Sites hosting config: ${error.message}`);
  }
}

function writeJsonFile(filePath, value) {
  fs.writeFileSync(filePath, `${JSON.stringify(value, null, 2)}\n`, "utf8");
}

const WORKER_STARTER_PACKAGE = {
  name: "data-analytics-sites-worker",
  private: true,
  type: "module",
  scripts: {
    build: "bash scripts/build.sh",
    validate: "node scripts/validate-artifact.mjs",
  },
};

const WORKER_STARTER_BUILD_SCRIPT = [
  "#!/usr/bin/env bash",
  "set -euo pipefail",
  "",
  'project_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)',
  'dist_root="$project_root/dist"',
  "",
  'rm -rf "$dist_root"',
  'mkdir -p "$dist_root/server" "$dist_root/.openai"',
  'cp "$project_root/worker/index.js" "$dist_root/server/index.js"',
  'cp "$project_root/.openai/hosting.json" "$dist_root/.openai/hosting.json"',
  "",
  'echo "Built $dist_root"',
  "",
].join("\n");

const WORKER_STARTER_VALIDATE_SCRIPT = [
  'import assert from "node:assert/strict";',
  'import { readFile } from "node:fs/promises";',
  'import { resolve } from "node:path";',
  'import { fileURLToPath, pathToFileURL } from "node:url";',
  "",
  'const projectRoot = resolve(fileURLToPath(new URL("..", import.meta.url)));',
  'const workerPath = resolve(projectRoot, "dist/server/index.js");',
  'const manifestPath = resolve(projectRoot, "dist/.openai/hosting.json");',
  "",
  "const [source, manifest] = await Promise.all([",
  '  readFile(workerPath, "utf8"),',
  '  readFile(manifestPath, "utf8"),',
  "]);",
  "JSON.parse(manifest);",
  "",
  "// A data URL forces ESM parsing even though the generated output has no package.json.",
  'const moduleUrl = `data:text/javascript;base64,${Buffer.from(source).toString("base64")}`;',
  "const workerModule = await import(moduleUrl);",
  "assert.equal(",
  '  typeof workerModule.default?.fetch,',
  '  "function",',
  '  `${pathToFileURL(workerPath)} must export default.fetch`,',
  ");",
  "",
  'console.log("Artifact is valid ESM and exports default.fetch");',
  "",
].join("\n");

function writeFileIfMissing(filePath, contents) {
  if (fs.existsSync(filePath)) return;
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, contents, "utf8");
}

function ensureWorkerStarterScaffold(outputDir) {
  writeFileIfMissing(
    path.join(outputDir, "package.json"),
    `${JSON.stringify(WORKER_STARTER_PACKAGE, null, 2)}\n`,
  );
  writeFileIfMissing(path.join(outputDir, "scripts", "build.sh"), WORKER_STARTER_BUILD_SCRIPT);
  writeFileIfMissing(
    path.join(outputDir, "scripts", "validate-artifact.mjs"),
    WORKER_STARTER_VALIDATE_SCRIPT,
  );
}

function normalizedSiteEditorEmail(value) {
  if (value == null) return null;
  if (typeof value !== "string") throw new Error("site_editor_email must be a string when provided");
  const email = value.trim().toLowerCase();
  if (!email || email.length > 320 || !email.includes("@")) {
    throw new Error("site_editor_email must be a valid non-empty email address");
  }
  return email;
}

function siteEditorEmailHash(value) {
  const email = normalizedSiteEditorEmail(value);
  return email ? crypto.createHash("sha256").update(email).digest("hex") : null;
}

function existingSiteEditorState(outputDir) {
  try {
    const source = fs.readFileSync(path.join(outputDir, "worker", "index.js"), "utf8");
    const enabledMatch = source.match(/const PRESENTATION_EDITING_ENABLED = (true|false);/);
    const emailMatch = source.match(/const EDITOR_EMAIL_HASH = "([0-9a-f]{64})";/);
    return {
      enabled: enabledMatch ? enabledMatch[1] === "true" : emailMatch ? true : null,
      emailHash: emailMatch ? emailMatch[1] : null,
    };
  } catch {
    return { enabled: null, emailHash: null };
  }
}

function workerSource({ artifactHtml, chartHtml, editingEnabled, editorEmailHash, manifest, snapshot, packageInfo, sourceEntries }) {
  return `"use strict";

const INDEX_HTML = ${JSON.stringify(artifactHtml)};
const CHART_WIDGET_HTML = ${JSON.stringify(chartHtml)};
const MANIFEST = ${JSON.stringify(manifest)};
const SNAPSHOT = ${JSON.stringify(snapshot)};
const PACKAGE_INFO = ${JSON.stringify(packageInfo)};
const SOURCE_TEXT = new Map(${JSON.stringify(sourceEntries)});
const ARTIFACT_ID = PACKAGE_INFO.artifactId;
const PRESENTATION_EDITING_ENABLED = ${JSON.stringify(editingEnabled)};
const EDITOR_EMAIL_HASH = ${JSON.stringify(editorEmailHash)};
const PRESENTATION_KEY = "current";
const PRESENTATION_SCHEMA_SQL = ${JSON.stringify(PRESENTATION_SCHEMA_SQL)};
const MAX_PRESENTATION_BYTES = 250000;
const MAX_PRESENTATION_TEXT = 20000;

function isPlainObject(value) {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function validationError(message) {
  const error = new Error(message);
  error.status = 400;
  throw error;
}

function normalizedEmail(request) {
  return String(request.headers.get("oai-authenticated-user-email") || "").trim().toLowerCase();
}

async function sha256Hex(value) {
  const digest = await globalThis.crypto.subtle.digest("SHA-256", new TextEncoder().encode(value));
  return Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, "0")).join("");
}

async function canEditPresentation(request) {
  if (!PRESENTATION_EDITING_ENABLED) return false;
  const email = normalizedEmail(request);
  if (!email || !EDITOR_EMAIL_HASH) return false;
  try {
    return await sha256Hex(email) === EDITOR_EMAIL_HASH;
  } catch {
    return false;
  }
}

function knownIds(items) {
  return new Set((Array.isArray(items) ? items : []).map((item) => item && item.id).filter((id) => typeof id === "string"));
}

const CHART_IDS = knownIds(MANIFEST.charts);
const CHARTS_BY_ID = new Map((Array.isArray(MANIFEST.charts) ? MANIFEST.charts : [])
  .filter((chart) => chart && typeof chart.id === "string")
  .map((chart) => [chart.id, chart]));
const TABLE_IDS = knownIds(MANIFEST.tables);
const BLOCK_TEXT_IDS = new Set((Array.isArray(MANIFEST.blocks) ? MANIFEST.blocks : [])
  .filter((block) => block && block.type === "markdown" && typeof block.id === "string")
  .map((block) => block.id));
const PRESENTATION_CHART_TYPES = new Set([
  "line",
  "area",
  "stackedArea",
  "bar",
  "horizontalBar",
  "stackedBar",
  "stackedBar100",
  "horizontalStackedBar",
  "horizontalStackedBar100",
  "histogram",
  "scatter",
  "heatmap",
  "pie",
  "leaderboard",
  "sparkline",
  "funnel",
  "waterfall",
  "boxPlot",
]);
const PRESENTATION_SERIES_COLORS = new Set([
  "blue",
  "purple",
  "green",
  "neutral",
  "orange",
  "yellow",
  "pink",
  "red",
]);
const PRESENTATION_SERIES_LINE_STYLES = new Set(["solid", "dashed", "dotted"]);
const PRESENTATION_SERIES_ROLES = new Set([
  "actual",
  "baseline",
  "target",
  "forecast",
  "plan",
  "comparison",
]);
const LAYOUT_IDS = new Set();
for (const block of Array.isArray(MANIFEST.blocks) ? MANIFEST.blocks : []) {
  if (!block || typeof block.id !== "string") continue;
  LAYOUT_IDS.add(block.id);
  if (block.type === "metric-strip" && Array.isArray(block.cardIds)) {
    for (const cardId of block.cardIds) {
      if (typeof cardId === "string") LAYOUT_IDS.add("metric:" + block.id + ":" + cardId);
    }
  }
}

function sanitizeTextMap(value, allowedIds, allowedFields, strict) {
  if (value == null) return {};
  if (!isPlainObject(value)) validationError("presentation text overrides must be objects");
  const output = {};
  for (const [id, rawOverride] of Object.entries(value)) {
    if (!allowedIds.has(id)) {
      if (strict) validationError("presentation override references an unknown id");
      continue;
    }
    if (!isPlainObject(rawOverride)) {
      if (strict) validationError("presentation text override must be an object");
      continue;
    }
    const nextOverride = {};
    for (const [field, rawText] of Object.entries(rawOverride)) {
      if (!allowedFields.includes(field)) {
        if (strict) validationError("presentation override contains an unsupported field");
        continue;
      }
      if (typeof rawText !== "string" || rawText.length > MAX_PRESENTATION_TEXT) {
        if (strict) validationError("presentation text is invalid or too large");
        continue;
      }
      nextOverride[field] = rawText;
    }
    if (Object.keys(nextOverride).length) output[id] = nextOverride;
  }
  return output;
}

function sanitizeLayout(value, strict) {
  if (value == null) return [];
  if (!Array.isArray(value) || value.length > 500) validationError("presentation layout must be a bounded array");
  const seen = new Set();
  const output = [];
  for (const item of value) {
    const id = item && item.id;
    const layout = item && item.layout;
    if (typeof id !== "string" || !LAYOUT_IDS.has(id) || seen.has(id) || (layout !== "full" && layout !== "half")) {
      if (strict) validationError("presentation layout contains an invalid item");
      continue;
    }
    seen.add(id);
    output.push({ id, layout });
  }
  return output;
}

function sanitizeDeletedIds(value, strict) {
  if (value == null) return [];
  if (!Array.isArray(value) || value.length > 500) validationError("deleted presentation blocks must be a bounded array");
  const seen = new Set();
  const output = [];
  for (const id of value) {
    if (typeof id !== "string" || !LAYOUT_IDS.has(id) || seen.has(id)) {
      if (strict) validationError("deleted presentation blocks contain an invalid id");
      continue;
    }
    seen.add(id);
    output.push(id);
  }
  return output;
}

function knownChartFields(chart) {
  const fields = new Set();
  const addField = (field) => {
    if (typeof field === "string" && field) fields.add(field);
  };
  addField(chart && chart.xField);
  for (const series of Array.isArray(chart && chart.series) ? chart.series : []) {
    addField(series && series.field);
  }
  const encodings = isPlainObject(chart && chart.encodings) ? chart.encodings : {};
  for (const role of ["x", "y", "color", "lineStyle", "size", "facet", "label"]) {
    const encoding = isPlainObject(encodings[role]) ? encodings[role] : {};
    addField(encoding.field);
    for (const field of Array.isArray(encoding.fields) ? encoding.fields : []) addField(field);
  }
  for (const tooltip of Array.isArray(encodings.tooltip) ? encodings.tooltip : []) {
    addField(tooltip && tooltip.field);
  }
  return fields;
}

function sanitizeChartSpecOverrides(value, strict) {
  if (value == null) return {};
  if (!isPlainObject(value)) validationError("chart spec overrides must be an object");
  const output = {};
  const allowedFields = new Set(["type", "xField", "series", "encodings", "settings"]);
  for (const [chartId, rawOverride] of Object.entries(value)) {
    const chart = CHARTS_BY_ID.get(chartId);
    if (!chart) {
      if (strict) validationError("chart spec override references an unknown chart");
      continue;
    }
    if (!isPlainObject(rawOverride)) {
      if (strict) validationError("chart spec override must be an object");
      continue;
    }
    if (strict) {
      for (const field of Object.keys(rawOverride)) {
        if (!allowedFields.has(field)) validationError("chart spec override contains an unsupported field");
      }
    }
    const chartFields = knownChartFields(chart);
    const nextOverride = {};
    if (rawOverride.type != null) {
      if (typeof rawOverride.type === "string" && PRESENTATION_CHART_TYPES.has(rawOverride.type)) {
        nextOverride.type = rawOverride.type;
      } else if (strict) {
        validationError("chart spec override contains an invalid chart type");
      }
    }
    if (rawOverride.xField != null) {
      if (typeof rawOverride.xField === "string" && chartFields.has(rawOverride.xField)) {
        nextOverride.xField = rawOverride.xField;
      } else if (strict) {
        validationError("chart spec override contains an invalid x field");
      }
    }
    if (rawOverride.series != null) {
      if (!Array.isArray(rawOverride.series) || rawOverride.series.length > 50) {
        if (strict) validationError("chart spec override series must be a bounded array");
      } else {
        const series = [];
        for (const rawSeries of rawOverride.series) {
          if (!isPlainObject(rawSeries) || typeof rawSeries.field !== "string" || !chartFields.has(rawSeries.field)) {
            if (strict) validationError("chart spec override contains an invalid series field");
            continue;
          }
          const nextSeries = { field: rawSeries.field };
          if (rawSeries.label != null) {
            if (typeof rawSeries.label === "string" && rawSeries.label.length <= 500) nextSeries.label = rawSeries.label;
            else if (strict) validationError("chart spec override contains an invalid series label");
          }
          if (rawSeries.color != null) {
            if (typeof rawSeries.color === "string" && PRESENTATION_SERIES_COLORS.has(rawSeries.color)) nextSeries.color = rawSeries.color;
            else if (strict) validationError("chart spec override contains an invalid series color");
          }
          if (rawSeries.lineStyle != null) {
            if (typeof rawSeries.lineStyle === "string" && PRESENTATION_SERIES_LINE_STYLES.has(rawSeries.lineStyle)) nextSeries.lineStyle = rawSeries.lineStyle;
            else if (strict) validationError("chart spec override contains an invalid series line style");
          }
          for (const roleField of ["role", "semanticRole"]) {
            if (rawSeries[roleField] == null) continue;
            if (typeof rawSeries[roleField] === "string" && PRESENTATION_SERIES_ROLES.has(rawSeries[roleField])) {
              nextSeries[roleField] = rawSeries[roleField];
            } else if (strict) {
              validationError("chart spec override contains an invalid series role");
            }
          }
          series.push(nextSeries);
        }
        if (series.length) nextOverride.series = series;
      }
    }
    if (rawOverride.encodings != null) {
      if (!isPlainObject(rawOverride.encodings)) {
        if (strict) validationError("chart spec override encodings must be an object");
      } else {
        const size = rawOverride.encodings.size;
        if (size != null) {
          if (isPlainObject(size) && typeof size.field === "string" && chartFields.has(size.field)) {
            nextOverride.encodings = { size: { field: size.field } };
          } else if (strict) {
            validationError("chart spec override contains an invalid size field");
          }
        }
      }
    }
    if (rawOverride.settings != null) {
      if (!isPlainObject(rawOverride.settings)) {
        if (strict) validationError("chart spec override settings must be an object");
      } else {
        const settings = {};
        if (rawOverride.settings.orientation === "horizontal" || rawOverride.settings.orientation === "vertical") {
          settings.orientation = rawOverride.settings.orientation;
        } else if (rawOverride.settings.orientation != null && strict) {
          validationError("chart spec override contains an invalid orientation");
        }
        if (["grouped", "stacked", "stacked100"].includes(rawOverride.settings.groupMode)) {
          settings.groupMode = rawOverride.settings.groupMode;
        } else if (rawOverride.settings.groupMode != null && strict) {
          validationError("chart spec override contains an invalid group mode");
        }
        if (Object.keys(settings).length) nextOverride.settings = settings;
      }
    }
    if (Object.keys(nextOverride).length) output[chartId] = nextOverride;
  }
  return output;
}

function sanitizePresentationOverrides(value, strict = true) {
  if (!isPlainObject(value)) validationError("presentation overrides must be an object");
  const allowedFields = new Set([
    "pageTitle",
    "chartSpecOverrides",
    "chartTextOverrides",
    "tableTextOverrides",
    "blockTextOverrides",
    "dashboardLayout",
    "reportLayout",
    "deletedReportBlockIds",
  ]);
  if (strict) {
    for (const field of Object.keys(value)) {
      if (!allowedFields.has(field)) validationError("presentation overrides contain an unsupported field");
    }
  }
  const output = {};
  if (typeof value.pageTitle === "string" && value.pageTitle.length <= 500) output.pageTitle = value.pageTitle;
  else if (value.pageTitle != null && strict) validationError("presentation title is invalid or too large");
  const chartTextOverrides = sanitizeTextMap(value.chartTextOverrides, CHART_IDS, ["headerMarkdown"], strict);
  const chartSpecOverrides = sanitizeChartSpecOverrides(value.chartSpecOverrides, strict);
  const tableTextOverrides = sanitizeTextMap(value.tableTextOverrides, TABLE_IDS, ["headerMarkdown"], strict);
  const blockTextOverrides = sanitizeTextMap(value.blockTextOverrides, BLOCK_TEXT_IDS, ["bodyMarkdown"], strict);
  const dashboardLayout = sanitizeLayout(value.dashboardLayout, strict);
  const reportLayout = sanitizeLayout(value.reportLayout, strict);
  const deletedReportBlockIds = sanitizeDeletedIds(value.deletedReportBlockIds, strict);
  if (Object.keys(chartSpecOverrides).length) output.chartSpecOverrides = chartSpecOverrides;
  if (Object.keys(chartTextOverrides).length) output.chartTextOverrides = chartTextOverrides;
  if (Object.keys(tableTextOverrides).length) output.tableTextOverrides = tableTextOverrides;
  if (Object.keys(blockTextOverrides).length) output.blockTextOverrides = blockTextOverrides;
  if (dashboardLayout.length) output.dashboardLayout = dashboardLayout;
  if (reportLayout.length) output.reportLayout = reportLayout;
  if (deletedReportBlockIds.length) output.deletedReportBlockIds = deletedReportBlockIds;
  return output;
}

function storedOverrides(row) {
  if (!row || typeof row.overrides_json !== "string") return {};
  try {
    return sanitizePresentationOverrides(JSON.parse(row.overrides_json), false);
  } catch {
    return {};
  }
}

async function ensurePresentationTable(db) {
  if (!db || typeof db.prepare !== "function") throw new Error("Sites database binding is unavailable");
  await db.prepare(PRESENTATION_SCHEMA_SQL).run();
}

async function presentationRow(db) {
  return db.prepare("SELECT revision, overrides_json FROM data_analytics_presentation_v1 WHERE key = ?")
    .bind(PRESENTATION_KEY)
    .first();
}

async function initializePresentation(db) {
  await db.prepare("INSERT OR IGNORE INTO data_analytics_presentation_v1 (key, revision, overrides_json) VALUES (?, 0, '{}')")
    .bind(PRESENTATION_KEY)
    .run();
  return presentationRow(db);
}

function presentationPayload(row, canEdit) {
  return {
    artifactId: ARTIFACT_ID,
    revision: Number.isInteger(row && row.revision) ? row.revision : Number(row && row.revision) || 0,
    overrides: storedOverrides(row),
    canEdit: Boolean(canEdit),
  };
}

async function getPresentation(request, env) {
  const canEdit = await canEditPresentation(request);
  try {
    await ensurePresentationTable(env && env.DB);
    const row = await initializePresentation(env.DB);
    return jsonResponse(presentationPayload(row, canEdit));
  } catch {
    return jsonResponse(presentationPayload(null, false));
  }
}

async function putPresentation(request, env) {
  const email = normalizedEmail(request);
  if (!email) return jsonResponse({ error: "Sign in to edit this Site." }, { status: 401 });
  if (!await canEditPresentation(request)) {
    return jsonResponse({ error: "Only the Site creator can edit this presentation." }, { status: 403 });
  }
  let rawBody;
  try {
    rawBody = await request.text();
  } catch {
    return jsonResponse({ error: "Could not read presentation changes." }, { status: 400 });
  }
  if (rawBody.length > MAX_PRESENTATION_BYTES) return jsonResponse({ error: "Presentation changes are too large." }, { status: 413 });
  let body;
  try {
    body = rawBody ? JSON.parse(rawBody) : {};
  } catch {
    return jsonResponse({ error: "Presentation changes must be valid JSON." }, { status: 400 });
  }
  if (!isPlainObject(body) || body.artifactId !== ARTIFACT_ID || !Number.isInteger(body.revision) || body.revision < 0) {
    return jsonResponse({ error: "This Site changed. Reload before saving." }, { status: 409 });
  }
  let overrides;
  try {
    overrides = sanitizePresentationOverrides(body.overrides);
  } catch (error) {
    return jsonResponse({ error: error.message }, { status: error.status || 400 });
  }
  try {
    await ensurePresentationTable(env && env.DB);
    const row = await initializePresentation(env.DB);
    const currentRevision = Number(row.revision) || 0;
    if (currentRevision !== body.revision) {
      return jsonResponse({ ...presentationPayload(row, true), error: "This Site changed. Reload before saving." }, { status: 409 });
    }
    const nextRevision = currentRevision + 1;
    const result = await env.DB.prepare("UPDATE data_analytics_presentation_v1 SET revision = ?, overrides_json = ? WHERE key = ? AND revision = ?")
      .bind(nextRevision, JSON.stringify(overrides), PRESENTATION_KEY, currentRevision)
      .run();
    if (!result || !result.meta || Number(result.meta.changes) !== 1) {
      const latestRow = await presentationRow(env.DB);
      return jsonResponse({ ...presentationPayload(latestRow, true), error: "This Site changed. Reload before saving." }, { status: 409 });
    }
    const savedRow = await presentationRow(env.DB);
    return jsonResponse(presentationPayload(savedRow, true));
  } catch {
    return jsonResponse({ error: "Presentation editing is temporarily unavailable." }, { status: 503 });
  }
}

function jsonResponse(body, init = {}) {
  return new Response(JSON.stringify(body), {
    status: init.status || 200,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
      ...(init.headers || {}),
    },
  });
}

function textResponse(body, init = {}) {
  return new Response(String(body == null ? "" : body), {
    status: init.status || 200,
    headers: {
      "content-type": init.contentType || "text/plain; charset=utf-8",
      "cache-control": "no-store",
      ...(init.headers || {}),
    },
  });
}

function sourceTextFor(url) {
  const key =
    url.searchParams.get("path") ||
    url.searchParams.get("id") ||
    url.searchParams.get("source") ||
    url.searchParams.get("sourceId") ||
    "";
  return SOURCE_TEXT.get(key) || null;
}

export default {
  async fetch(request, env = {}) {
    const url = new URL(request.url);
    if (url.pathname === "/api/manifest") return jsonResponse(MANIFEST);
    if (url.pathname === "/api/snapshot") return jsonResponse(SNAPSHOT);
    if (url.pathname === "/api/package") return jsonResponse(PACKAGE_INFO);
    if (url.pathname === "/api/presentation") {
      if (request.method === "GET") return getPresentation(request, env);
      if (request.method === "PUT") return putPresentation(request, env);
      return jsonResponse({ error: "Method not allowed." }, { status: 405, headers: { allow: "GET, PUT" } });
    }
    if (url.pathname === "/api/inline-chart-widget") {
      return textResponse(CHART_WIDGET_HTML, { contentType: "text/html; charset=utf-8" });
    }
    if (url.pathname === "/api/source-file" || url.pathname === "/api/source") {
      const text = sourceTextFor(url);
      if (text != null) return textResponse(text);
      return textResponse("Source text was not included in this hosted artifact.", { status: 404 });
    }
    if (url.pathname === "/" || url.pathname === "/index.html") {
      return textResponse(INDEX_HTML, { contentType: "text/html; charset=utf-8" });
    }
    return textResponse("Not found", { status: 404 });
  },
};
`;
}

function createTarArchive(outputDir, archivePath) {
  const result = childProcess.spawnSync("tar", ["-C", outputDir, "-czf", archivePath, "dist"], {
    encoding: "utf8",
  });
  if (result.status !== 0) {
    throw new Error(`failed to create Sites archive: ${result.stderr || result.stdout || "tar failed"}`);
  }
}

function exportDataScienceArtifactPackage(args) {
  const payload = validatedArtifactPayload(buildArtifactPayload(args));
  const id = artifactId(payload);
  const { outputDir, isDefault } = normalizeOutputDir(args.output_dir, id);
  const isSitesCheckout = ensureWritableOutputDir(outputDir, isDefault);
  ensureWorkerStarterScaffold(outputDir);
  const hostingDir = path.join(outputDir, ".openai");
  const existingHostingConfig = isSitesCheckout
    ? readHostingConfig(path.join(hostingDir, "hosting.json"))
    : {};
  const existingEditorState = existingSiteEditorState(outputDir);
  const hasEditorEmail = Object.prototype.hasOwnProperty.call(args, "site_editor_email");
  const editorEmailHash = hasEditorEmail
    ? siteEditorEmailHash(args.site_editor_email)
    : existingEditorState.emailHash;
  const editingEnabled = hasEditorEmail
    ? args.site_editor_email !== null
    : existingEditorState.enabled ?? Boolean(existingEditorState.emailHash);

  const distDir = path.join(outputDir, "dist");
  const serverDir = path.join(distDir, "server");
  const clientDir = path.join(distDir, "client");
  const dataDir = path.join(clientDir, "data");
  const sourceDir = path.join(outputDir, "worker");
  const dbDir = path.join(outputDir, "db");
  const packagedHostingDir = path.join(distDir, ".openai");
  fs.mkdirSync(serverDir, { recursive: true });
  fs.mkdirSync(dataDir, { recursive: true });
  fs.mkdirSync(sourceDir, { recursive: true });
  fs.mkdirSync(hostingDir, { recursive: true });
  fs.mkdirSync(packagedHostingDir, { recursive: true });

  const packageInfo = {
    artifactId: id,
    artifactRuntime: "datascience-artifact-widget.html",
    deliveryMode: "site_creator",
    exportedAt: new Date().toISOString(),
    handoffPluginName: DATA_ANALYTICS_DISPLAY_NAME,
    hostedEditing: editingEnabled ? "presentation" : null,
    hostedReadOnly: true,
    controls: {
      delete: editingEnabled,
      edit: editingEnabled,
      export: editingEnabled,
      exportHostedLink: false,
      refresh: editingEnabled,
      hostedLink: false,
      html: editingEnabled,
      pdf: editingEnabled,
      document: editingEnabled,
      slides: editingEnabled,
    },
  };
  const hostedPayload = { ...payload, package_info: packageInfo, packageInfo };
  const sourceEntries = sourceLookupEntries(hostedPayload);
  const artifactHtml = hostedArtifactHtml(readWidgetHtmlAsset("datascience-artifact-widget.html"), hostedPayload);
  const chartHtml = readWidgetHtmlAsset("datascience-chart-widget.html");
  const existingD1Binding = existingHostingConfig.d1 ?? null;
  if (editingEnabled && existingD1Binding && existingD1Binding !== "DB") {
    throw new Error(`Sites presentation editing requires the D1 binding name "DB"; found ${JSON.stringify(existingD1Binding)}`);
  }
  const hostingConfig = {
    ...existingHostingConfig,
    d1: editingEnabled ? "DB" : existingD1Binding,
    r2: existingHostingConfig.r2 ?? null,
  };
  if (typeof args.site_creator_project_id === "string" && args.site_creator_project_id) {
    if (hostingConfig.project_id && hostingConfig.project_id !== args.site_creator_project_id) {
      throw new Error("site_creator_project_id does not match the Sites checkout");
    }
    hostingConfig.project_id = args.site_creator_project_id;
  }

  writeJsonFile(path.join(dataDir, "manifest.json"), hostedPayload.manifest);
  writeJsonFile(path.join(dataDir, "snapshot.json"), hostedPayload.snapshot);
  writeJsonFile(path.join(dataDir, "package.json"), packageInfo);
  writeJsonFile(path.join(dataDir, "sources.json"), Object.fromEntries(sourceEntries));
  writeJsonFile(path.join(hostingDir, "hosting.json"), hostingConfig);
  writeJsonFile(path.join(packagedHostingDir, "hosting.json"), hostingConfig);
  if (editingEnabled) {
    fs.mkdirSync(dbDir, { recursive: true });
    fs.writeFileSync(
      path.join(dbDir, "schema.ts"),
      `export const presentationSchemaSql = ${JSON.stringify(PRESENTATION_SCHEMA_SQL)};\n`,
      "utf8",
    );
  }
  fs.writeFileSync(path.join(clientDir, "index.html"), artifactHtml, "utf8");
  const worker = workerSource({
    artifactHtml,
    chartHtml,
    editingEnabled,
    editorEmailHash,
    manifest: hostedPayload.manifest,
    snapshot: hostedPayload.snapshot,
    packageInfo,
    sourceEntries,
  });
  fs.writeFileSync(path.join(sourceDir, "index.js"), worker, "utf8");
  fs.writeFileSync(path.join(serverDir, "index.js"), worker, "utf8");

  const archivePath = `${outputDir}.tar.gz`;
  createTarArchive(outputDir, archivePath);
  return {
    ok: true,
    export_type: "site_creator_package",
    artifact_id: id,
    manifest_title: hostedPayload.manifest.title || null,
    surface: hostedPayload.surface,
    dataset_count: Object.keys(hostedPayload.snapshot.datasets || {}).length,
    source_count: sourceEntries.length,
    output_dir: outputDir,
    archive_path: archivePath,
    source_entrypoint: path.join(sourceDir, "index.js"),
    worker_entrypoint: path.join(serverDir, "index.js"),
    database_schema_path: editingEnabled ? path.join(dbDir, "schema.ts") : null,
    hosting_config_path: path.join(hostingDir, "hosting.json"),
    packaged_hosting_config_path: path.join(packagedHostingDir, "hosting.json"),
    presentation_editing: editingEnabled,
    routes: ["/", "/api/manifest", "/api/snapshot", "/api/package", "/api/presentation", "/api/source-file", "/api/inline-chart-widget"],
    message:
      "Exported the validated Data Analytics artifact with the canonical MCP app runtime for Sites deployment.",
  };
}

function normalizeChartSource(args) {
  const source = asObject(args.source);
  if (!Object.keys(source).length) return null;
  const query = asObject(source.query);
  const normalized = {};
  for (const key of ["id", "label", "path", "href"]) {
    if (source[key] != null) normalized[key] = source[key];
  }
  if (Object.keys(query).length) {
    normalized.query = {};
    for (const key of [
      "engine",
      "id",
      "url",
      "sql",
      "description",
      "language",
      "executed_at",
      "tables_used",
      "filters",
      "metric_definitions",
    ]) {
      if (query[key] != null) normalized.query[key] = query[key];
    }
  }
  return Object.keys(normalized).length ? normalized : null;
}

function normalizeColumns(columns, rows) {
  const normalized = [];
  const seen = new Set();
  for (const column of asList(columns)) {
    if (!isPlainObject(column)) continue;
    const key = column.key;
    if (typeof key !== "string" || !key || seen.has(key)) continue;
    seen.add(key);
    normalized.push({ ...column });
  }
  if (normalized.length || !rows.length) return normalized;
  const inferredKeys = [];
  for (const row of rows) {
    for (const key of Object.keys(row)) {
      if (!inferredKeys.includes(key)) inferredKeys.push(key);
    }
  }
  return inferredKeys.map((key) => ({ key, label: titleCaseKey(key) }));
}

function normalizeResultTable(value, { fallbackColumns = null, fallbackRows = null } = {}) {
  const table = asObject(value);
  const hasTable = Object.keys(table).length > 0;
  const rowsValue = hasTable ? table.rows : fallbackRows;
  const rows = asList(rowsValue).filter(isPlainObject).map((row) => ({ ...row }));
  const columns = normalizeColumns(hasTable ? table.columns : fallbackColumns, rows);
  if (!rows.length && !columns.length && !hasTable) return null;
  const rowCount = Number.isInteger(table.row_count) ? table.row_count : rows.length;
  return { ...table, columns, rows, row_count: rowCount, truncated: hasTable ? Boolean(table.truncated) : false };
}

function columnKeys(resultTable) {
  const keys = new Set();
  for (const column of asList((resultTable || {}).columns)) {
    if (isPlainObject(column) && typeof column.key === "string" && column.key) keys.add(column.key);
  }
  for (const row of asList((resultTable || {}).rows)) {
    if (!isPlainObject(row)) continue;
    for (const key of Object.keys(row)) {
      if (key) keys.add(key);
    }
  }
  return keys;
}

function columnType(resultTable, key) {
  if (!key) return null;
  for (const column of asList((resultTable || {}).columns)) {
    if (isPlainObject(column) && column.key === key) return typeof column.type === "string" ? column.type : null;
  }
  return null;
}

function columnUnit(resultTable, key) {
  if (!key) return null;
  for (const column of asList((resultTable || {}).columns)) {
    if (isPlainObject(column) && column.key === key && typeof column.unit === "string") {
      const unit = column.unit.trim();
      return unit || null;
    }
  }
  return null;
}

function columnValueFormat(resultTable, key) {
  if (!key) return null;
  for (const column of asList((resultTable || {}).columns)) {
    if (!isPlainObject(column) || column.key !== key) continue;
    if (["compact", "number", "percent", "currency"].includes(column.format)) {
      return column.format;
    }
    if (["number", "percent", "currency"].includes(column.type)) {
      return column.type;
    }
    return null;
  }
  return null;
}

function columnLabel(resultTable, key) {
  if (key === MEASURE_NAMES_FIELD) return "Measure names";
  for (const column of asList((resultTable || {}).columns)) {
    if (isPlainObject(column) && column.key === key && typeof column.label === "string" && column.label) {
      return column.label;
    }
  }
  return titleCaseKey(key);
}

function numeric(value) {
  if (typeof value === "boolean") return null;
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string") {
    const parsed = Number(value.replace(/,/g, ""));
    return Number.isFinite(parsed) ? parsed : null;
  }
  return null;
}

function numericColumnKeys(resultTable) {
  const rows = asList((resultTable || {}).rows).filter(isPlainObject);
  let keys = Array.from(columnKeys(resultTable));
  const declaredOrder = asList((resultTable || {}).columns)
    .filter((column) => isPlainObject(column) && typeof column.key === "string")
    .map((column) => column.key);
  if (declaredOrder.length) keys = declaredOrder.filter((key) => keys.includes(key));
  const output = [];
  for (const key of keys) {
    const declaredType = columnType(resultTable, key);
    if (["number", "percent", "currency"].includes(declaredType)) {
      output.push(key);
      continue;
    }
    if (["text", "date"].includes(declaredType)) continue;
    if (rows.some((row) => numeric(row[key]) !== null)) output.push(key);
  }
  return output;
}

function isNumericColumn(resultTable, key) {
  return Boolean(key) && numericColumnKeys(resultTable).includes(key);
}

function measureCompatibilityKey(resultTable, key) {
  if (!key) return null;
  const unit = columnUnit(resultTable, key);
  if (unit) return `unit:${unit.toLowerCase()}`;
  return columnType(resultTable, key) === "percent" ? "type:percent" : null;
}

function multiMeasureSeriesEnabled(spec) {
  return asObject(spec && spec.settings).multi_measure_series === true;
}

function usesMultiMeasureSeries(spec) {
  return multiMeasureSeriesEnabled(spec) || encodingField(spec, "color") === MEASURE_NAMES_FIELD;
}

function compatibleMeasureKeys(resultTable, spec) {
  const xField = encodingField(spec, "x");
  const measureKeys = numericColumnKeys(resultTable).filter((key) => key !== xField);
  if (multiMeasureSeriesEnabled(spec)) return measureKeys;
  const yField = encodingField(spec, "y");
  const compatibilityKey = measureCompatibilityKey(resultTable, yField);
  if (!compatibilityKey) return [];
  return measureKeys.filter((key) => measureCompatibilityKey(resultTable, key) === compatibilityKey);
}

function normalizeVisualizationTypeAndSettings(rawVisualizationType, rawSettings) {
  const visualizationType = rawVisualizationType;
  const raw = asObject(rawSettings);
  const settings = {};
  if (raw.show_points != null) settings.show_points = raw.show_points;
  if (raw.multi_measure_series != null) settings.multi_measure_series = raw.multi_measure_series;
  if (visualizationType === "bar") {
    settings.orientation = firstValue(raw.orientation, "vertical");
    settings.group_mode = firstValue(raw.group_mode, "single");
  }
  return {
    visualizationType,
    settings: Object.keys(settings).length ? settings : undefined,
  };
}

function validateEnumSetting(settings, key, acceptedValues) {
  const value = settings[key];
  if (value == null || acceptedValues.includes(value)) return;
  const publicKey = key === "group_mode" ? "grouping" : key === "show_points" ? "points" : key;
  throw new Error(`chart.options.${publicKey} must be one of ${acceptedValues.join(", ")}`);
}

function validateBooleanSetting(settings, key) {
  const value = settings[key];
  if (value == null || typeof value === "boolean") return;
  throw new Error(`chart.options.${key} must be true or false`);
}

function normalizeHeatmapEncodingsForWidget(resultTable, encodings) {
  const x = asObject(encodings.x);
  const y = asObject(encodings.y);
  const color = asObject(encodings.color);
  if (!resultTable || !y.field || !color.field) {
    return { x, y, color };
  }
  const yIsNumeric = isNumericColumn(resultTable, y.field);
  const colorIsNumeric = isNumericColumn(resultTable, color.field);
  if (!yIsNumeric && colorIsNumeric) {
    return { x, y: color, color: y };
  }
  return { x, y, color };
}

function validatePercentStackedBarShape(resultTable, spec) {
  if (!resultTable) return;
  const rows = asList(resultTable.rows).filter(isPlainObject);
  if (!rows.length) return;
  const xField = encodingField(spec, "x");
  const yField = encodingField(spec, "y");
  if (!yField) return;
  const totals = new Map();
  let numericCount = 0;
  for (const row of rows) {
    const yValue = numeric(row[yField]);
    if (yValue === null) continue;
    if (yValue < 0) {
      throw new Error(
        "chart.options.grouping stacked100 requires non-negative y values so percentages have a valid denominator",
      );
    }
    numericCount += 1;
    const category = xField ? String(row[xField]) : "__all__";
    totals.set(category, (totals.get(category) || 0) + yValue);
  }
  if (!numericCount) return;
  if ([...totals.values()].some((total) => total <= 0)) {
    throw new Error(
      "chart.options.grouping stacked100 requires a positive denominator for every stacked category",
    );
  }
}

function validateVisualizationSettings(spec, resultTable) {
  const settings = asObject(spec.settings);
  validateEnumSetting(settings, "orientation", BAR_ORIENTATIONS);
  validateEnumSetting(settings, "group_mode", BAR_GROUP_MODES);
  validateEnumSetting(settings, "show_points", TREND_POINT_MODES);
  validateBooleanSetting(settings, "multi_measure_series");
  if (spec.visualization_type !== "bar") return;
  const groupMode = settings.group_mode || "single";
  if (["grouped", "stacked", "stacked100"].includes(groupMode) && !encodingField(spec, "color")) {
    throw new Error(
      `chart.options.grouping ${groupMode} requires chart.fields.color.field`,
    );
  }
  if (groupMode === "stacked100") validatePercentStackedBarShape(resultTable, spec);
}

function isHorizontalBarType(visualizationType, settings = {}) {
  if (visualizationType !== "bar") return false;
  return asObject(settings).orientation === "horizontal";
}

function chartQualityWarnings(spec, resultTable) {
  const warnings = [];
  const visualizationType = spec.visualization_type;
  const subtitle = String(asObject(spec.presentation).subtitle || "").trim();
  if (subtitleLooksLikeSourceOrQueryMetadata(subtitle)) {
    warnings.push(
      "Chart subtitle looks like source/query metadata; use source.query/source metadata for provenance and make the subtitle a reader-facing insight.",
    );
  }
  if (
    visualizationType === "leaderboard" &&
    String(encodingField(spec, "x") || "").toLowerCase().includes("metric")
  ) {
    warnings.push("Leaderboard over metric definitions is usually better as KPI cards or a table.");
  }
  if (resultTable && resultTable.truncated) {
    warnings.push("Chart uses a sampled result table; verify omitted rows do not change the claim.");
  }
  const xField = encodingField(spec, "x");
  const distinctCategories = distinctResultValues(resultTable, xField);
  if (visualizationType === "bar" && distinctCategories > COMPACT_BAR_CATEGORY_WARNING_THRESHOLD) {
    warnings.push(
      `Compact bar chart has ${distinctCategories} categories; consider a reviewed top-N slice.`,
    );
  }
  if (visualizationType === "pie" && distinctCategories > COMPACT_PIE_SEGMENT_WARNING_THRESHOLD) {
    warnings.push(
      `Compact pie chart has ${distinctCategories} slices; consider a reviewed aggregation.`,
    );
  }
  return warnings;
}

function subtitleLooksLikeSourceOrQueryMetadata(subtitle) {
  if (!subtitle) return false;
  const lower = subtitle.toLowerCase();
  if (/\b(source|query|sql|select|where|join|dashboard|notebook|partition)\b/.test(lower)) {
    return true;
  }
  if (/\b(metric|table|warehouse|schema|dataset|view|cube|source id|query id)\s*:/.test(lower)) {
    return true;
  }
  if (/\b[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*\b/.test(lower)) {
    return true;
  }
  if (/\b[a-z][a-z0-9]*_[a-z0-9_]*\b/.test(subtitle) && /\b(metric|field|column|source)\b/.test(lower)) {
    return true;
  }
  return false;
}

function distinctResultValues(resultTable, field) {
  if (!resultTable || !field) return 0;
  const values = new Set();
  for (const row of asList(resultTable.rows).filter(isPlainObject)) {
    if (row[field] != null) values.add(String(row[field]));
  }
  return values.size;
}

function looksLikeIdentifierField(key) {
  return /(^|_)(id|uuid|url|email)$/i.test(String(key || ""));
}

function scatterPointLabelField(resultTable, spec) {
  if (!resultTable || spec.visualization_type !== "scatter") return null;
  const explicitLabelField = encodingField(spec, "label");
  if (explicitLabelField) return explicitLabelField;
  const xField = encodingField(spec, "x");
  const yField = encodingField(spec, "y");
  const sizeField = encodingField(spec, "size");
  const colorField = encodingField(spec, "color");
  const excluded = new Set([xField, yField, sizeField, colorField].filter(Boolean));
  const declaredOrder = asList(resultTable.columns)
    .filter((column) => isPlainObject(column) && typeof column.key === "string")
    .map((column) => column.key);
  const keys = declaredOrder.length ? declaredOrder : Array.from(columnKeys(resultTable));
  const candidates = [];
  for (const key of keys) {
    if (!key || excluded.has(key) || looksLikeIdentifierField(key)) continue;
    if (isNumericColumn(resultTable, key)) continue;
    if (columnType(resultTable, key) === "date") continue;
    const distinct = distinctResultValues(resultTable, key);
    if (distinct >= 2) candidates.push(key);
  }
  return candidates.length === 1 ? candidates[0] : null;
}

function chartInputFromLegacyVisualizationSpec(args) {
  const spec = asObject(args.visualization_spec);
  const settings = asObject(spec.settings);
  const encodings = asObject(spec.encodings);
  return {
    type: spec.visualization_type,
    fields: {
      ...(encodings.x ? { x: encodings.x } : {}),
      ...(encodings.y ? { y: encodings.y } : {}),
      ...(encodings.size ? { size: encodings.size } : {}),
      ...(encodings.color ? { color: encodings.color } : {}),
      ...(encodings.label ? { label: encodings.label } : {}),
    },
    options: {
      ...(settings.orientation != null ? { orientation: settings.orientation } : {}),
      ...(settings.group_mode != null ? { grouping: settings.group_mode } : {}),
      ...(settings.show_points != null ? { points: settings.show_points } : {}),
      ...(settings.multi_measure_series != null
        ? { multi_measure_series: settings.multi_measure_series }
        : {}),
    },
  };
}

function displayInputFromLegacyVisualizationSpec(args) {
  const presentation = asObject(asObject(args.visualization_spec).presentation);
  return {
    ...(firstValue(presentation.unit, args.unit) != null
      ? { unit: firstValue(presentation.unit, args.unit) }
      : {}),
    ...(firstValue(presentation.baseline, args.baseline) != null
      ? { baseline: firstValue(presentation.baseline, args.baseline) }
      : {}),
    ...(firstValue(presentation.x_axis_title, presentation.x_label, args.x_axis_title, args.x_label) != null
      ? {
          x_axis_title: firstValue(
            presentation.x_axis_title,
            presentation.x_label,
            args.x_axis_title,
            args.x_label,
          ),
        }
      : {}),
    ...(firstValue(presentation.y_axis_title, presentation.y_label, args.y_axis_title, args.y_label) != null
      ? {
          y_axis_title: firstValue(
            presentation.y_axis_title,
            presentation.y_label,
            args.y_axis_title,
            args.y_label,
          ),
        }
      : {}),
    ...(firstValue(presentation.show_controls, args.show_controls) != null
      ? { controls: firstValue(presentation.show_controls, args.show_controls) }
      : {}),
  };
}

function normalizeChartInput(args) {
  const chart = Object.keys(asObject(args.chart)).length
    ? asObject(args.chart)
    : chartInputFromLegacyVisualizationSpec(args);
  const display = Object.keys(asObject(args.display)).length
    ? asObject(args.display)
    : displayInputFromLegacyVisualizationSpec(args);
  return {
    source: normalizeChartSource(args),
    table: normalizeResultTable(firstValue(args.table, args.result_table)),
    chart,
    display,
  };
}

function visualizationArgsFromChartInput(args, chartInput) {
  const chart = asObject(chartInput.chart);
  const fields = asObject(chart.fields);
  const options = asObject(chart.options);
  const display = asObject(chartInput.display);
  return {
    ...args,
    visualization_spec: {
      visualization_type: chart.type,
      encodings: {
        ...(fields.x ? { x: fields.x } : {}),
        ...(fields.y ? { y: fields.y } : {}),
        ...(fields.size ? { size: fields.size } : {}),
        ...(fields.color ? { color: fields.color } : {}),
        ...(fields.lineStyle ? { lineStyle: fields.lineStyle } : {}),
        ...(fields.label ? { label: fields.label } : {}),
      },
      settings: {
        ...(options.orientation != null ? { orientation: options.orientation } : {}),
        ...(options.grouping != null ? { group_mode: options.grouping } : {}),
        ...(options.points != null ? { show_points: options.points } : {}),
        ...(options.multi_measure_series != null
          ? { multi_measure_series: options.multi_measure_series }
          : {}),
      },
      presentation: {
        title: args.title,
        subtitle: args.subtitle,
        ...(display.unit != null ? { unit: display.unit } : {}),
        ...(display.baseline != null ? { baseline: display.baseline } : {}),
        ...(display.x_axis_title != null ? { x_axis_title: display.x_axis_title } : {}),
        ...(display.y_axis_title != null ? { y_axis_title: display.y_axis_title } : {}),
        ...(display.controls != null ? { show_controls: display.controls } : {}),
      },
    },
    show_controls: display.controls,
  };
}

function chartOutputFromVisualizationSpec(spec) {
  const encodings = asObject(spec.encodings);
  const settings = asObject(spec.settings);
  return {
    type: spec.visualization_type,
    fields: {
      ...(encodings.x ? { x: encodings.x } : {}),
      ...(encodings.y ? { y: encodings.y } : {}),
      ...(encodings.size ? { size: encodings.size } : {}),
      ...(encodings.color ? { color: encodings.color } : {}),
      ...(encodings.lineStyle ? { lineStyle: encodings.lineStyle } : {}),
      ...(encodings.label ? { label: encodings.label } : {}),
    },
    ...(Object.keys(settings).length
      ? {
          options: {
            ...(settings.orientation != null ? { orientation: settings.orientation } : {}),
            ...(settings.group_mode != null ? { grouping: settings.group_mode } : {}),
            ...(settings.show_points != null ? { points: settings.show_points } : {}),
            ...(settings.multi_measure_series != null
              ? { multi_measure_series: settings.multi_measure_series }
              : {}),
          },
        }
      : {}),
  };
}

function displayOutputFromVisualizationSpec(spec) {
  const presentation = asObject(spec.presentation);
  const display = {
    ...(presentation.unit != null ? { unit: presentation.unit } : {}),
    ...(presentation.baseline != null ? { baseline: presentation.baseline } : {}),
    ...(presentation.x_axis_title != null ? { x_axis_title: presentation.x_axis_title } : {}),
    ...(presentation.y_axis_title != null ? { y_axis_title: presentation.y_axis_title } : {}),
    ...(presentation.show_controls != null ? { controls: presentation.show_controls } : {}),
  };
  return Object.keys(display).length ? display : null;
}

function normalizeVisualizationSpec(args, resultTable) {
  const spec = asObject(args.visualization_spec);
  const {
    intent: _intent,
    question: _question,
    rationale: _rationale,
    version: _version,
    comparisonContext: _comparisonContext,
    sort: _sort,
    ...specWithoutRemovedMetadata
  } = spec;
  const encodings = asObject(spec.encodings);
  const presentation = asObject(spec.presentation);
  const requestedVisualizationType = spec.visualization_type;
  if (requestedVisualizationType == null) {
    throw new Error("chart.type is required");
  }
  if (!CANONICAL_CHART_TYPE_SET.has(requestedVisualizationType)) {
    throw new Error(`chart.type must be one of ${CANONICAL_CHART_TYPES.join(", ")}`);
  }
  const normalizedType = normalizeVisualizationTypeAndSettings(requestedVisualizationType, spec.settings);
  const visualizationType = normalizedType.visualizationType;
  const settings = normalizedType.settings;
  let x = asObject(encodings.x);
  let y = asObject(encodings.y);
  const size = asObject(encodings.size);
  let color = asObject(encodings.color);
  const lineStyle = asObject(encodings.lineStyle);
  const label = asObject(encodings.label);
  if (visualizationType === "heatmap") {
    ({ x, y, color } = normalizeHeatmapEncodingsForWidget(resultTable, { x, y, color }));
  }
  const requestedXLabel = firstValue(presentation.x_axis_title, presentation.x_label);
  const requestedYLabel = firstValue(presentation.y_axis_title, presentation.y_label);
  if (typeof x.field !== "string" || !x.field) {
    throw new Error("chart.fields.x.field is required");
  }
  if (typeof y.field !== "string" || !y.field) {
    throw new Error("chart.fields.y.field is required");
  }
  const resolvedEncodings = { x, y };
  if (size.field) resolvedEncodings.size = size;
  if (color.field) resolvedEncodings.color = color;
  if (lineStyle.field) resolvedEncodings.lineStyle = lineStyle;
  if (label.field) resolvedEncodings.label = label;
  const resolvedPresentation = {
    title: firstValue(presentation.title, args.title),
    subtitle: firstValue(presentation.subtitle, args.subtitle),
    x_label: requestedXLabel,
    y_label: requestedYLabel,
    unit: firstValue(presentation.unit, y.unit, columnUnit(resultTable, y.field)),
    baseline: presentation.baseline,
    show_controls: firstValue(presentation.show_controls, args.show_controls),
  };
  const normalizedSpec = {
    ...specWithoutRemovedMetadata,
    visualization_type: visualizationType,
    settings,
    encodings: resolvedEncodings,
    presentation: {
      ...resolvedPresentation,
      x_axis_title: resolvedPresentation.x_label,
      y_axis_title: resolvedPresentation.y_label,
    },
  };
  validateVisualizationSettings(normalizedSpec, resultTable);
  return normalizedSpec;
}

function encodingField(spec, role) {
  const field = asObject(asObject((spec || {}).encodings)[role]).field;
  return typeof field === "string" && field ? field : null;
}

function chartEncodingForField(spec, resultTable, role, fallbackField = null) {
  const source = asObject(asObject((spec || {}).encodings)[role]);
  const field = typeof fallbackField === "string" && fallbackField ? fallbackField : encodingField(spec, role);
  if (!field) return null;
  const encoding = { ...source, field };
  if (!encoding.label) encoding.label = columnLabel(resultTable, field);
  if (!encoding.format) {
    const format = columnValueFormat(resultTable, field);
    if (format) encoding.format = format;
  }
  if (!encoding.unit) {
    const unit = columnUnit(resultTable, field);
    if (unit) encoding.unit = unit;
  }
  if (!encoding.type) {
    const type = columnType(resultTable, field);
    if (type === "date") encoding.type = "temporal";
    else if (type === "text") encoding.type = "nominal";
    else if (type === "percent" || type === "currency" || type === "number") encoding.type = "quantitative";
  }
  return encoding;
}

function encodingValue(spec, role, key) {
  return asObject(asObject((spec || {}).encodings)[role])[key];
}

function validateVisualizationFields(resultTable, spec) {
  if (!resultTable) return;
  const keys = columnKeys(resultTable);
  if (!keys.size) return;
  const visualizationType = spec.visualization_type;
  const heatmapColorField = visualizationType === "heatmap" ? encodingField(spec, "color") : null;
  if (visualizationType === "heatmap" && !heatmapColorField) {
    throw new Error("chart.fields.color.field is required for heatmap charts and represents the Y-axis category");
  }
  for (const role of ["x", "y", "size", "color", "lineStyle", "label"]) {
    const field = encodingField(spec, role);
    if (role === "color" && field === MEASURE_NAMES_FIELD) {
      if (compatibleMeasureKeys(resultTable, spec).length > 1) continue;
      throw new Error(
        "chart.fields.color.field \"__measure_names__\" requires at least two compatible measures or chart.options.multi_measure_series=true",
      );
    }
    if (field && !keys.has(field)) {
      throw new Error(
        `chart.fields.${role}.field ${JSON.stringify(field)} is not present in table`,
      );
    }
    if (
      role === "y" &&
      field &&
      encodingValue(spec, "y", "aggregate") !== "count" &&
      !isNumericColumn(resultTable, field)
    ) {
      const message =
        visualizationType === "heatmap"
          ? "chart.fields.y.field must reference the numeric heatmap cell value; use chart.fields.color.field for the Y-axis category"
          : "chart.fields.y.field must reference a numeric table column";
      throw new Error(message);
    }
    if (role === "size" && field && spec.visualization_type !== "scatter") {
      throw new Error("chart.fields.size.field is only supported for scatter charts");
    }
    if (role === "size" && field && !isNumericColumn(resultTable, field)) {
      throw new Error("chart.fields.size.field must reference a numeric table column");
    }
  }
  const lineStyleField = encodingField(spec, "lineStyle");
  if (lineStyleField) {
    if (!["line", "area", "stackedArea", "sparkline"].includes(visualizationType)) {
      throw new Error("chart.fields.lineStyle.field is only supported for line, area, stackedArea, and sparkline charts");
    }
    for (const row of asList(resultTable.rows).filter(isPlainObject)) {
      const rawStyle = row[lineStyleField];
      if (rawStyle == null || rawStyle === "") continue;
      const style = String(rawStyle);
      if (!SERIES_LINE_STYLES.includes(style)) {
        throw new Error(
          `chart.fields.lineStyle.field values must be one of ${SERIES_LINE_STYLES.join(", ")}`,
        );
      }
    }
  }
}

function deriveChartPoints(resultTable, spec) {
  if (!resultTable) return [];
  const rows = asList(resultTable.rows).filter(isPlainObject);
  if (!rows.length) return [];
  const xField = encodingField(spec, "x");
  const yField = encodingField(spec, "y");
  const sizeField = encodingField(spec, "size");
  const colorField = encodingField(spec, "color");
  const yAggregate = String(encodingValue(spec, "y", "aggregate") || "sum").toLowerCase();
  const visualizationType = String(spec.visualization_type);
  const output = [];
  for (const row of rows) {
    const xValue = xField ? row[xField] : null;
    if (usesMultiMeasureSeries(spec)) {
      for (const measureKey of compatibleMeasureKeys(resultTable, spec)) {
        const yValue = numeric(row[measureKey]);
        if (yValue === null) continue;
        output.push({
          ...row,
          x: xValue,
          y: yValue,
          size: sizeField ? numeric(row[sizeField]) : null,
          series: columnLabel(resultTable, measureKey),
        });
      }
      continue;
    }
    let yValue;
    if (yAggregate === "count") {
      yValue = 1;
    } else {
      let sourceY = yField ? row[yField] : null;
      if (sourceY == null && visualizationType === "histogram") sourceY = xValue;
      yValue = numeric(sourceY);
    }
    if (yValue === null) continue;
    const seriesValue = colorField ? row[colorField] : null;
    const seriesLabel = colorField
      ? firstValue(seriesValue, "Value")
      : firstValue(presentationValue(spec, {}, "y_label"), columnLabel(resultTable, yField), "Value");
    output.push({
      ...row,
      x: xValue,
      y: yValue,
      size: sizeField ? numeric(row[sizeField]) : null,
      series: String(seriesLabel),
    });
  }
  return output;
}

function normalizeTablePayload(args) {
  const source = normalizeChartSource(args);
  validateActualSqlSource(source, "$.source.query.sql");
  const resultTable = normalizeResultTable(args.result_table, {
    fallbackColumns: args.columns,
    fallbackRows: args.rows,
  });
  const rows = asList((resultTable || {}).rows);
  const viewConfig = asObject(args.view_config);
  const maxRows = firstValue(args.max_rows, viewConfig.max_rows, 50);
  return {
    ok: true,
    widget_type: "table",
    title: String(firstValue(args.title, "Query preview")),
    subtitle: args.subtitle,
    source,
    result_table: resultTable,
    columns: (resultTable || {}).columns || [],
    rows,
    metrics: args.metrics || [],
    notes: args.notes || [],
    max_rows: Number.parseInt(maxRows || 50, 10),
  };
}

function presentationValue(spec, args, key) {
  return firstValue(asObject(spec.presentation)[key], args[key]);
}

function axisTitleValue(spec, args, axis) {
  return firstValue(
    asObject(spec.presentation)[`${axis}_axis_title`],
    asObject(spec.presentation)[`${axis}_label`],
    args[`${axis}_axis_title`],
    args[`${axis}_label`],
  );
}

function axisTitleForField(spec, args, resultTable, axis, field) {
  const title = axisTitleValue(spec, args, axis);
  return title == null || title === "" ? undefined : String(title);
}

function chartSpecFromVisualizationSpec(spec, args, resultTable, id = "chart") {
  const xField = encodingField(spec, "x") || "x";
  const yField = encodingField(spec, "y") || "y";
  const sizeField = encodingField(spec, "size");
  const colorField = encodingField(spec, "color");
  const lineStyleField = encodingField(spec, "lineStyle");
  const xAxisTitle = axisTitleForField(spec, args, resultTable, "x", xField);
  const yAxisTitle = axisTitleForField(spec, args, resultTable, "y", yField);
  const encodings = {};
  encodings.x = chartEncodingForField(spec, resultTable, "x", xField);
  if (usesMultiMeasureSeries(spec)) {
    const fields = compatibleMeasureKeys(resultTable, spec);
    encodings.y = {
      ...asObject(asObject((spec || {}).encodings).y),
      fields,
      label: presentationValue(spec, {}, "y_label") || "Value",
      type: "quantitative",
    };
    delete encodings.y.field;
  } else {
    encodings.y = chartEncodingForField(spec, resultTable, "y", yField);
  }
  if (colorField) {
    encodings.color = chartEncodingForField(spec, resultTable, "color", colorField);
  }
  if (lineStyleField) {
    encodings.lineStyle = chartEncodingForField(spec, resultTable, "lineStyle", lineStyleField);
  }
  if (spec.visualization_type === "scatter" && sizeField) {
    encodings.size = chartEncodingForField(spec, resultTable, "size", sizeField);
  }
  const labelField = scatterPointLabelField(resultTable, spec);
  if (spec.visualization_type === "scatter" && labelField && asList((resultTable || {}).rows).some((row) => isPlainObject(row) && row[labelField] != null)) {
    encodings.label = chartEncodingForField(spec, resultTable, "label", labelField);
  }
  return {
    id: String(firstValue(args.id, id)),
    title: String(presentationValue(spec, args, "title") || args.title || "Data Analytics chart"),
    subtitle: presentationValue(spec, args, "subtitle"),
    type: spec.visualization_type,
    dataset: String(firstValue(args.id, args.label, "default")),
    ...(Object.keys(encodings).length ? { encodings } : {}),
    xAxisTitle,
    yAxisTitle,
    unit: presentationValue(spec, args, "unit"),
    valueFormat: columnValueFormat(resultTable, yField) || undefined,
    settings: spec.settings,
    surface: {
      surface: "compact",
      showControls: Boolean(presentationValue(spec, args, "show_controls")),
    },
  };
}

function normalizeChartPayload(args) {
  const chartInput = normalizeChartInput(args);
  validateActualSqlSource(chartInput.source, "$.source.query.sql");
  const resultTable = chartInput.table;
  const normalizedArgs = visualizationArgsFromChartInput(args, chartInput);
  const visualizationSpec = normalizeVisualizationSpec(normalizedArgs, resultTable);
  validateVisualizationFields(resultTable, visualizationSpec);

  const data = deriveChartPoints(resultTable, visualizationSpec);
  const chartSpec = chartSpecFromVisualizationSpec(visualizationSpec, normalizedArgs, resultTable, "default");
  const qualityWarnings = chartQualityWarnings(visualizationSpec, resultTable);
  if (!asList((resultTable || {}).rows).length) {
    throw new Error("chart widgets require table.rows");
  }

  return {
    ok: true,
    widget_type: "chart",
    title: String(presentationValue(visualizationSpec, normalizedArgs, "title") || args.title),
    subtitle: presentationValue(visualizationSpec, normalizedArgs, "subtitle"),
    source: chartInput.source,
    table: resultTable,
    chart: chartOutputFromVisualizationSpec(visualizationSpec),
    display: displayOutputFromVisualizationSpec(visualizationSpec),
    quality_warnings: qualityWarnings,
    chart_spec: chartSpec,
    visualization_type: visualizationSpec.visualization_type,
    show_controls: presentationValue(visualizationSpec, normalizedArgs, "show_controls"),
    data,
    unit: presentationValue(visualizationSpec, normalizedArgs, "unit"),
    baseline: presentationValue(visualizationSpec, normalizedArgs, "baseline"),
  };
}

function callTool(name, inputArgs = {}) {
  const args = isPlainObject(inputArgs) ? { ...inputArgs } : {};
  const toolName = name;

  if (toolName === TOOL_NAMES.validateArtifact) {
    const payload = validatedArtifactPayload(buildArtifactPayload(args));
    return {
      ok: true,
      validation_type: "artifact",
      surface: payload.surface,
      manifest_title: payload.manifest.title || null,
      dataset_count: Object.keys(payload.snapshot.datasets || {}).length,
      source_count: asList(payload.sources).length,
      snapshot_status: payload.snapshot.status || null,
      message: "Artifact payload is valid. Follow the selected delivery surface for rendering or export.",
      artifact_payload: payload,
    };
  }
  if (toolName === TOOL_NAMES.renderArtifact) {
    return validatedArtifactPayload(buildArtifactPayload(args));
  }
  if (toolName === TOOL_NAMES.exportArtifactPackage) {
    return exportDataScienceArtifactPackage(args);
  }
  if (toolName === TOOL_NAMES.renderChart) {
    return validatedWidgetPayload(normalizeChartPayload({ ...args, widget_type: "chart" }));
  }
  if (toolName === TOOL_NAMES.renderTable) {
    return validatedWidgetPayload(normalizeTablePayload({ ...args, widget_type: "table" }));
  }

  throw new Error(`unknown Data Analytics widget tool: ${name}`);
}

function widgetUriForPayload(payload) {
  if (payload.widget_type === "artifact") return ARTIFACT_WIDGET_URI;
  if (payload.widget_type === "table") return TABLE_WIDGET_URI;
  if (payload.widget_type === "chart") return CHART_WIDGET_URI;
  return null;
}

function toolResult(payload, toolName) {
  const result = {
    content: [{ type: "text", text: JSON.stringify(payload) }],
    structuredContent: payload,
    isError: false,
  };
  const widgetUri = widgetUriForPayload(payload) || WIDGET_TOOL_URIS[toolName];
  if (widgetUri) result._meta = toolUiMeta(widgetUri, toolName);
  return result;
}

function toolError(message) {
  const payload = { ok: false, error: message };
  return {
    content: [{ type: "text", text: JSON.stringify(payload) }],
    structuredContent: payload,
    isError: true,
  };
}

function rpcResponse(id, result) {
  return { jsonrpc: "2.0", id, result };
}

function rpcError(id, code, message) {
  return { jsonrpc: "2.0", id, error: { code, message } };
}

async function handleRpc(message) {
  if (!isPlainObject(message)) return rpcError(null, -32600, "Invalid Request");
  const messageId = message.id;
  const method = message.method;
  const params = isPlainObject(message.params) ? message.params : {};
  if (typeof method !== "string") return messageId != null ? rpcError(messageId, -32600, "Invalid Request") : null;
  if (method.startsWith("notifications/") || method === "$/cancelRequest") return null;
  try {
    if (method === "initialize") {
      return rpcResponse(messageId, {
        protocolVersion: params.protocolVersion || "2024-11-05",
        capabilities: {
          tools: { listChanged: false },
          resources: { subscribe: false, listChanged: false },
        },
        serverInfo: {
          name: SERVER_NAME,
          title: "Data Analytics",
          version: SERVER_VERSION,
          description: "Render Data Analytics charts, tables, dashboards, and report artifacts.",
          icons: DATA_ANALYTICS_ICONS,
        },
        instructions: SERVER_INSTRUCTIONS,
      });
    }
    if (method === "ping") return rpcResponse(messageId, {});
    if (method === "tools/list") return rpcResponse(messageId, { tools: toolDefinitions() });
    if (method === "tools/call") {
      const name = params.name;
      if (typeof name !== "string") return rpcError(messageId, -32602, "tools/call requires a tool name");
      const args = params.arguments || {};
      if (!isPlainObject(args)) return rpcError(messageId, -32602, "tools/call arguments must be an object");
      try {
        return rpcResponse(messageId, toolResult(callTool(name, args), name));
      } catch (error) {
        return rpcResponse(messageId, toolError(error && error.message ? error.message : String(error)));
      }
    }
    if (method === "resources/list") return rpcResponse(messageId, { resources: resources() });
    if (method === "resources/read") {
      const uri = params.uri;
      if (typeof uri !== "string") return rpcError(messageId, -32602, "resources/read requires a resource uri");
      if (!knownResourceUri(uri)) {
        return rpcError(messageId, -32602, `unknown Data Analytics widget resource: ${uri}`);
      }
      return rpcResponse(messageId, {
        contents: [
          {
            uri,
            mimeType: WIDGET_MIME_TYPE,
            text: resourceText(uri),
            _meta: widgetResourceMeta(uri),
          },
        ],
      });
    }
    if (method === "resources/templates/list") return rpcResponse(messageId, { resourceTemplates: [] });
    if (method === "prompts/list") return rpcResponse(messageId, { prompts: [] });
  } catch (error) {
    return rpcError(messageId, -32000, error && error.message ? error.message : String(error));
  }
  return rpcError(messageId, -32601, `Method not found: ${method}`);
}

function writeRpc(message) {
  process.stdout.write(`${JSON.stringify(message)}\n`);
}

function runStdio() {
  const rl = readline.createInterface({ input: process.stdin });
  rl.on("line", async (line) => {
    const trimmed = line.trim();
    if (!trimmed) return;
    let decoded;
    try {
      decoded = JSON.parse(trimmed);
    } catch (error) {
      writeRpc(rpcError(null, -32700, `Parse error: ${error.message}`));
      return;
    }
    if (Array.isArray(decoded)) {
      const responses = [];
      for (const request of decoded) {
        const response = await handleRpc(request);
        if (response) responses.push(response);
      }
      if (responses.length) writeRpc(responses);
      return;
    }
    const response = await handleRpc(decoded);
    if (response) writeRpc(response);
  });
}

module.exports = {
  SERVER_NAME,
  SERVER_VERSION,
  ARTIFACT_WIDGET_URI,
  TABLE_WIDGET_URI,
  CHART_WIDGET_URI,
  SERVER_INSTRUCTIONS,
  DATA_ANALYTICS_ICONS,
  MEASURE_NAMES_FIELD,
  MAX_WIDGET_ROWS,
  MAX_ARTIFACT_DATASETS,
  MAX_ARTIFACT_ROWS_PER_DATASET,
  MAX_ARTIFACT_PAYLOAD_BYTES,
  MAX_ARTIFACT_INLINE_SOURCE_CHARS,
  toolDefinitions,
  resources,
  callTool,
  exportDataScienceArtifactPackage,
  handleRpc,
};

if (require.main === module) {
  runStdio();
}
