import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { test } from "node:test";


const require = createRequire(import.meta.url);
const server = require("../mcp/server.cjs");

function sourceQueryForTest() {
  return {
    query: {
      engine: "trino",
      sql: "SELECT category, value FROM warehouse.chart_source",
      description: "Loads category/value rows for chart tests.",
      id: "test-query",
    },
  };
}

function queryTablePayload() {
  return {
    title: "ARR trend",
    source: {
      query: {
        engine: "databricks",
        sql: "SELECT reporting_date, arr_b FROM gtm.example",
        description: "Loads ARR by reporting date for widget tests.",
        id: "query-123",
        executed_at: "2026-05-01T00:00:00Z",
      },
    },
    table: {
      columns: [
        { key: "reporting_date", label: "Reporting date", type: "date" },
        { key: "arr_b", label: "ARR", type: "number", unit: "$B" },
      ],
      rows: [
        { reporting_date: "2026-03-31", arr_b: 2.73 },
        { reporting_date: "2026-04-30", arr_b: 2.9 },
      ],
      row_count: 2,
      truncated: false,
    },
    chart: {
      type: "line",
      fields: {
        x: { field: "reporting_date", type: "temporal", time_unit: "month" },
        y: { field: "arr_b", type: "quantitative", aggregate: "sum", unit: "$B" },
      },
    },
    display: {
      baseline: 2.8,
      unit: "$B",
      controls: true,
    },
  };
}

function artifactPayload(surface = "dashboard") {
  const manifest = {
    version: 1,
    surface,
    title: "Revenue momentum",
    generatedAt: "2026-05-07T00:00:00Z",
    cards: [
      {
        id: "revenue_card",
        dataset: "weekly_revenue",
        sourceId: "weekly_revenue_sql",
        metrics: [{ label: "Revenue", field: "revenue_m", format: "currency" }],
      },
    ],
    charts: [
      {
        id: "revenue_chart",
        title: "Revenue by segment",
        type: "bar",
        dataset: "weekly_revenue",
        sourceId: "weekly_revenue_sql",
        encodings: {
          x: { field: "segment", type: "nominal" },
          y: { field: "revenue_m", type: "quantitative" },
        },
      },
    ],
    tables: [
      {
        id: "revenue_table",
        title: "Revenue rows",
        dataset: "weekly_revenue",
        sourceId: "weekly_revenue_sql",
        columns: [
          { field: "segment", label: "Segment" },
          { field: "revenue_m", label: "Revenue", format: "currency" },
        ],
      },
    ],
    sources: [{ id: "weekly_revenue_sql", label: "Revenue SQL", path: "queries/revenue.sql" }],
  };
  if (surface === "report") {
    manifest.blocks = [
      {
        id: "summary_text",
        type: "markdown",
        body: "Revenue is concentrated in Beta.",
      },
      {
        id: "revenue_chart_block",
        type: "chart",
        chartId: "revenue_chart",
      },
      {
        id: "revenue_table_block",
        type: "table",
        tableId: "revenue_table",
      },
    ];
  } else {
    manifest.blocks = [
      {
        id: "revenue_metrics",
        type: "metric-strip",
        cardIds: ["revenue_card"],
      },
      {
        id: "revenue_chart_block",
        type: "chart",
        chartId: "revenue_chart",
      },
      {
        id: "revenue_table_block",
        type: "table",
        tableId: "revenue_table",
      },
    ];
  }
  return {
    surface,
    manifest,
    snapshot: {
      version: 1,
      generatedAt: "2026-05-07T00:00:00Z",
      status: "ready",
      datasets: {
        weekly_revenue: [
          { segment: "Alpha", revenue_m: 12 },
          { segment: "Beta", revenue_m: 18 },
        ],
      },
    },
    sources: [
      {
        id: "weekly_revenue_sql",
        query: {
          engine: "trino",
          sql: "SELECT segment, revenue_m FROM warehouse.weekly_revenue",
          description: "Loads weekly revenue by segment for artifact tests.",
        },
      },
    ],
  };
}

async function widgetResourceHtml(uri) {
  const response = await server.handleRpc({
    jsonrpc: "2.0",
    id: 1,
    method: "resources/read",
    params: { uri },
  });
  return response.result.contents[0].text;
}

test("MCP widget resources serve bundled apps, not local development redirects", async () => {
  const chartHtml = await widgetResourceHtml(server.CHART_WIDGET_URI);
  const tableHtml = await widgetResourceHtml(server.TABLE_WIDGET_URI);
  const artifactHtml = await widgetResourceHtml(server.ARTIFACT_WIDGET_URI);

  for (const html of [chartHtml, tableHtml, artifactHtml]) {
    assert.doesNotMatch(html, /Redirecting to the local widget source/);
    assert.doesNotMatch(html, /window\.location\.replace\(target\)/);
  }
  assert.match(chartHtml, /@modelcontextprotocol\/ext-apps/);
  assert.match(tableHtml, /@modelcontextprotocol\/ext-apps/);
  assert.match(artifactHtml, /Data Analytics Artifact App/);
});

test("changed widget URIs change with the plugin version", () => {
  assert.equal(
    server.ARTIFACT_WIDGET_URI,
    `ui://widget/datascience-artifact-${encodeURIComponent(server.SERVER_VERSION)}.html`,
  );
  assert.equal(
    server.CHART_WIDGET_URI,
    `ui://widget/datascience-chart-${encodeURIComponent(server.SERVER_VERSION)}.html`,
  );
  assert.doesNotMatch(server.ARTIFACT_WIDGET_URI, /[?#]/);
  assert.doesNotMatch(server.CHART_WIDGET_URI, /[?#]/);
  assert.equal(server.TABLE_WIDGET_URI, "ui://widget/datascience-table.html");
});

test("changed widgets retain constrained stable and versioned resource aliases", async () => {
  const priorVersion = "0.2.6";
  const resourceCases = [
    {
      aliases: [
        "ui://widget/datascience-artifact.html",
        `ui://widget/datascience-artifact.html?v=${encodeURIComponent(server.SERVER_VERSION)}`,
        `ui://widget/datascience-artifact.html?v=${priorVersion}`,
        `ui://widget/datascience-artifact-${priorVersion}.html`,
        "ui://widget/datascience-artifact-0.2.7-rc.1.html",
      ],
      contentPattern: /Data Analytics Artifact App/,
    },
    {
      aliases: [
        "ui://widget/datascience-chart.html",
        `ui://widget/datascience-chart.html?v=${encodeURIComponent(server.SERVER_VERSION)}`,
        `ui://widget/datascience-chart.html?v=${priorVersion}`,
        `ui://widget/datascience-chart-${priorVersion}.html`,
        "ui://widget/datascience-chart-0.2.7-rc.1.html",
      ],
      contentPattern: /@modelcontextprotocol\/ext-apps/,
    },
  ];

  for (const { aliases, contentPattern } of resourceCases) {
    for (const uri of aliases) {
      const response = await server.handleRpc({
        jsonrpc: "2.0",
        id: 1,
        method: "resources/read",
        params: { uri },
      });

      assert.equal(response.result.contents[0].uri, uri);
      assert.match(response.result.contents[0].text, contentPattern);
    }
  }
});

test("JavaScript MCP server renders hosted artifact payloads", () => {
  const payload = server.callTool("render_artifact", artifactPayload("report"));

  assert.equal(payload.widget_type, "artifact");
  assert.equal(payload.surface, "report");
  assert.equal(payload.manifest.title, "Revenue momentum");
  assert.equal(payload.snapshot.datasets.weekly_revenue[1].segment, "Beta");
});

test("JavaScript MCP server exposes only canonical tool names", () => {
  const names = server.toolDefinitions().map((tool) => tool.name);
  assert.deepEqual(names, [
    "validate_artifact",
    "render_artifact",
    "export_artifact_package",
    "render_chart",
    "render_table",
  ]);

  assert.throws(
    () => server.callTool("render_datascience_chart", queryTablePayload()),
    /unknown Data Analytics widget tool: render_datascience_chart/,
  );
});

test("JavaScript MCP UI tool instructions guard Work Mode delivery on every surface", () => {
  const tools = Object.fromEntries(server.toolDefinitions().map((tool) => [tool.name, tool]));
  const workModeGuidance = [
    server.SERVER_INSTRUCTIONS,
    tools.render_artifact.description,
    tools.render_chart.description,
    tools.render_table.description,
  ].join("\n");

  assert.match(server.SERVER_INSTRUCTIONS, /do not call render_artifact, render_chart, or render_table/);
  assert.match(server.SERVER_INSTRUCTIONS, /mode = work_mode is positively identified/);
  assert.match(server.SERVER_INSTRUCTIONS, /regardless of surface/);
  assert.match(server.SERVER_INSTRUCTIONS, /lack appContext/);
  assert.match(server.SERVER_INSTRUCTIONS, /Preserve the delivery mode already selected/);
  assert.match(server.SERVER_INSTRUCTIONS, /treat charts_widget_v2 as directly surfaced/);
  assert.match(server.SERVER_INSTRUCTIONS, /emit its live genui content reference before fallback/);
  assert.match(server.SERVER_INSTRUCTIONS, /do not self-declare it unavailable, search for it, or print its payload as bare JSON/);
  assert.match(server.SERVER_INSTRUCTIONS, /Keep app_block conditional on/);
  assert.ok(server.SERVER_INSTRUCTIONS.includes('genui{"charts_widget_v2":{"content":{...}}}'));
  assert.match(server.SERVER_INSTRUCTIONS, /not standalone assistant text/);
  assert.match(server.SERVER_INSTRUCTIONS, /Use image-based\/static charting only after an emitted native reference is rejected or fails to render/);
  assert.match(server.SERVER_INSTRUCTIONS, /Use image-based\/static charting for that native-render failure fallback/);
  assert.match(server.SERVER_INSTRUCTIONS, /publish[\s\S]{0,120}Sites/);
  assert.match(server.SERVER_INSTRUCTIONS, /HTML as the automatic fallback/);
  assert.match(server.SERVER_INSTRUCTIONS, /In ChatGPT Desktop outside Work Mode/);
  assert.match(server.SERVER_INSTRUCTIONS, /image-based\/static charting/);
  assert.match(server.SERVER_INSTRUCTIONS, /Do not say a visual rendered above/);
  assert.match(tools.render_artifact.description, /mode = work_mode is positively identified/);
  assert.match(tools.render_artifact.description, /regardless of surface/);
  assert.match(tools.render_artifact.description, /publish[\s\S]{0,120}Sites/);
  assert.match(tools.render_artifact.description, /HTML as the fallback/);
  assert.match(tools.render_artifact.description, /not delivery confirmation/);
  assert.match(tools.render_chart.description, /Do not call this tool for inline visual delivery/);
  assert.match(tools.render_chart.description, /mode = work_mode is positively identified/);
  assert.match(tools.render_chart.description, /regardless of surface/);
  assert.match(tools.render_chart.description, /treat charts_widget_v2 as directly surfaced/);
  assert.match(tools.render_chart.description, /emit its live genui content reference before fallback/);
  assert.match(tools.render_chart.description, /do not self-declare it unavailable, search for it, or print its payload as bare JSON/);
  assert.match(tools.render_chart.description, /Keep app_block conditional on/);
  assert.ok(tools.render_chart.description.includes('genui{"charts_widget_v2":{"content":{...}}}'));
  assert.match(tools.render_chart.description, /not standalone assistant text/);
  assert.match(tools.render_chart.description, /Use image-based\/static charting only after an emitted native reference is rejected or fails to render/);
  assert.match(tools.render_chart.description, /Use image-based\/static charting for that native-render failure fallback/);
  assert.match(tools.render_chart.description, /not delivery confirmation/);
  assert.match(tools.render_table.description, /Do not call this tool for inline table delivery/);
  assert.match(tools.render_table.description, /mode = work_mode is positively identified/);
  assert.match(tools.render_table.description, /regardless of surface/);
  assert.match(tools.render_table.description, /not delivery confirmation/);
  assert.doesNotMatch(workModeGuidance, /ChatGPT web Work Mode/);
  assert.doesNotMatch(workModeGuidance, /unknown surface/);
  assert.doesNotMatch(workModeGuidance, /not positively codex_desktop/);
});

test("Sites exporter retains legacy private protocol identifiers", () => {
  const tools = Object.fromEntries(server.toolDefinitions().map((tool) => [tool.name, tool]));
  const exportProperties = tools.export_artifact_package.inputSchema.properties;
  const serverSource = readFileSync(new URL("../mcp/server.cjs", import.meta.url), "utf8");

  assert.ok(exportProperties.site_creator_project_id);
  assert.equal(exportProperties.sites_project_id, undefined);
  assert.match(serverSource, /mode: "site_creator"/);
  assert.match(serverSource, /deliveryMode: "site_creator"/);
  assert.match(serverSource, /export_type: "site_creator_package"/);
  assert.doesNotMatch(serverSource, /deliveryMode: "sites"/);
  assert.doesNotMatch(serverSource, /export_type: "sites_package"/);
});

test("JavaScript MCP server advertises Data Analytics icons on server info", async () => {
  assert.equal(server.DATA_ANALYTICS_ICONS[0].mimeType, "image/svg+xml");
  assert.deepEqual(server.DATA_ANALYTICS_ICONS[0].sizes, ["24x24"]);
  assert.match(server.DATA_ANALYTICS_ICONS[0].src, /^data:image\/svg\+xml;base64,/);
  assert.equal(server.DATA_ANALYTICS_ICONS[1].mimeType, "image/png");
  assert.deepEqual(server.DATA_ANALYTICS_ICONS[1].sizes, ["360x360"]);
  assert.match(server.DATA_ANALYTICS_ICONS[1].src, /^data:image\/png;base64,/);

  for (const tool of server.toolDefinitions()) {
    assert.equal(tool.icons, undefined);
  }

  const response = await server.handleRpc({
    jsonrpc: "2.0",
    id: 1,
    method: "initialize",
    params: {},
  });
  assert.equal(response.result.serverInfo.title, "Data Analytics");
  assert.equal(
    response.result.serverInfo.description,
    "Render Data Analytics charts, tables, dashboards, and report artifacts.",
  );
  assert.deepEqual(response.result.serverInfo.icons, server.DATA_ANALYTICS_ICONS);
});

test("JavaScript MCP server validates artifact payloads without widget metadata", async () => {
  const payload = server.callTool("validate_artifact", artifactPayload("report"));

  assert.equal(payload.ok, true);
  assert.equal(payload.validation_type, "artifact");
  assert.equal(payload.surface, "report");
  assert.equal(payload.manifest_title, "Revenue momentum");
  assert.equal(payload.dataset_count, 1);
  assert.equal(payload.artifact_payload.widget_type, "artifact");
  assert.match(payload.message, /Follow the selected delivery surface/);
  assert.doesNotMatch(payload.message, /safe to call render_artifact/i);

  const validateTool = server
    .toolDefinitions()
    .find((tool) => tool.name === "validate_artifact");
  assert.ok(validateTool);
  assert.equal(validateTool._meta, undefined);

  const rpcPayload = await server.handleRpc({
    jsonrpc: "2.0",
    id: 1,
    method: "tools/call",
    params: { name: "validate_artifact", arguments: artifactPayload("report") },
  });
  assert.equal(rpcPayload.result.structuredContent.ok, true);
  assert.match(rpcPayload.result.structuredContent.message, /Follow the selected delivery surface/);
  assert.doesNotMatch(rpcPayload.result.structuredContent.message, /safe to call render_artifact/i);
  assert.equal(rpcPayload.result._meta, undefined);
});

test("JavaScript MCP server rejects artifact chart y encodings without numeric values", () => {
  const args = artifactPayload("report");
  args.manifest.charts[0] = {
    ...args.manifest.charts[0],
    title: "Product-line share by country",
    dataset: "product_line_share",
    encodings: {
      x: { field: "country_name", type: "nominal" },
      y: { field: "product_line", type: "nominal" },
    },
  };
  args.snapshot.datasets.product_line_share = [
    { country_name: "India", product_line: "Consumer", share_pct: 71 },
    { country_name: "India", product_line: "API", share_pct: 18 },
  ];

  assert.throws(
    () => server.callTool("validate_artifact", args),
    /manifest\.charts\[0\]\.encodings\.y\.field "product_line" must reference a numeric dataset field/,
  );
});

test("JavaScript MCP server rejects legacy artifact chart fields", () => {
  const args = artifactPayload("report");
  args.manifest.charts[0].xField = "segment";

  assert.throws(
    () => server.callTool("validate_artifact", args),
    /manifest\.charts\[0\]\.xField is not supported for artifact charts; use encodings/,
  );
});

test("JavaScript MCP server rejects table-shaped artifact snapshot datasets", () => {
  const args = artifactPayload("report");
  args.snapshot.datasets.weekly_revenue = {
    columns: [
      { key: "segment", label: "Segment" },
      { key: "revenue_m", label: "Revenue", type: "currency" },
    ],
    rows: args.snapshot.datasets.weekly_revenue,
  };

  assert.throws(
    () => server.callTool("render_artifact", args),
    /snapshot\.datasets\.weekly_revenue must be an array of row objects/,
  );
});

test("JavaScript MCP server rejects key aliases for report table columns", () => {
  const args = artifactPayload("report");
  args.manifest.tables[0].columns = [
    { key: "segment", label: "Segment" },
    { key: "revenue_m", label: "Revenue", type: "currency" },
  ];

  assert.throws(
    () => server.callTool("render_artifact", args),
    /manifest\.tables\["revenue_table"\]\.columns\[0\]\.field/,
  );
});

test("JavaScript MCP server accepts and validates artifact table default sorts", () => {
  const args = artifactPayload("report");
  args.manifest.tables[0].defaultSort = {
    field: "revenue_m",
    direction: "desc",
  };

  const payload = server.callTool("render_artifact", args);
  assert.deepEqual(payload.manifest.tables[0].defaultSort, {
    field: "revenue_m",
    direction: "desc",
  });

  const unknownField = artifactPayload("report");
  unknownField.manifest.tables[0].defaultSort = {
    field: "missing_metric",
    direction: "desc",
  };
  assert.throws(
    () => server.callTool("validate_artifact", unknownField),
    /defaultSort\.field must reference a declared table column/,
  );

  const invalidDirection = artifactPayload("report");
  invalidDirection.manifest.tables[0].defaultSort = {
    field: "revenue_m",
    direction: "descending",
  };
  assert.throws(
    () => server.callTool("validate_artifact", invalidDirection),
    /defaultSort\.direction must be asc or desc/,
  );
});

test("JavaScript MCP server accepts body strings in report markdown blocks", () => {
  const args = artifactPayload("report");
  args.manifest.blocks[0] = {
    id: "summary_text",
    type: "markdown",
    body: "## Summary\n\n- **Beta** leads\n- [Source](https://example.com)",
  };

  const payload = server.callTool("render_artifact", args);

  assert.equal(payload.manifest.blocks[0].body, "## Summary\n\n- **Beta** leads\n- [Source](https://example.com)");
});

test("JavaScript MCP server validates block-wide markdown provenance against merged sources", () => {
  const documentSource = artifactPayload("report");
  documentSource.manifest.blocks[0] = {
    id: "summary_text",
    type: "markdown",
    body: "## Summary\n\nRevenue increased **18%** in the reviewed period.",
    sourceId: "revenue_brief",
  };
  documentSource.sources.push({
    id: "revenue_brief",
    label: "Revenue planning brief",
    path: "documents/revenue-planning-brief.pdf",
  });

  const payload = server.callTool("validate_artifact", documentSource);
  assert.equal(payload.ok, true);
  assert.equal(payload.artifact_payload.manifest.blocks[0].sourceId, "revenue_brief");
  assert.equal(
    payload.artifact_payload.sources.find((source) => source.id === "revenue_brief").path,
    "documents/revenue-planning-brief.pdf",
  );

  const missingSource = artifactPayload("report");
  missingSource.manifest.blocks[0].sourceId = "missing_brief";
  assert.throws(
    () => server.callTool("validate_artifact", missingSource),
    /manifest\.blocks\[0\]\.sourceId "missing_brief" does not resolve to a canonical merged source/,
  );

  const invalidSourceId = artifactPayload("report");
  invalidSourceId.manifest.blocks[0].sourceId = 42;
  assert.throws(
    () => server.callTool("validate_artifact", invalidSourceId),
    /manifest\.blocks\[0\]\.sourceId must be a string/,
  );
});

test("JavaScript MCP server rejects legacy narrative fields and removed block types", () => {
  const args = artifactPayload("report");
  args.manifest.blocks[0].markdown = "Legacy markdown field";
  delete args.manifest.blocks[0].body;
  assert.throws(
    () => server.callTool("render_artifact", args),
    /uses markdown, but markdown blocks render body/,
  );

  const titled = artifactPayload("report");
  titled.manifest.blocks[0].title = "Legacy title";
  titled.manifest.blocks[0].content = "Legacy content";
  delete titled.manifest.blocks[0].body;
  assert.throws(
    () => server.callTool("render_artifact", titled),
    /uses content, but markdown blocks render body/,
  );

  const bodyArray = artifactPayload("report");
  bodyArray.manifest.blocks[0].body = ["Legacy array body"];
  assert.throws(
    () => server.callTool("render_artifact", bodyArray),
    /body must be a non-empty string/,
  );

  const textType = artifactPayload("report");
  textType.manifest.blocks[0].type = "text";
  assert.throws(
    () => server.callTool("render_artifact", textType),
    /type must be one of markdown, metric-strip, chart, table, html/,
  );

  const removedType = artifactPayload("report");
  removedType.manifest.blocks.push({
    id: "next_steps",
    type: "recommendation",
    body: "Review account drivers.",
  });
  assert.throws(
    () => server.callTool("render_artifact", removedType),
    /type must be one of markdown, metric-strip, chart, table, html/,
  );
});

test("JavaScript MCP server preserves inline ordered-list markers in report body", () => {
  const args = artifactPayload("report");
  args.manifest.blocks[0] = {
    id: "summary_text",
    type: "markdown",
    body: "1. Review account drivers 2. Ask account teams for context 3. Monitor next week",
  };
  args.manifest.blocks.push({
    id: "questions_text",
    type: "markdown",
    body: "1. Is the gain durable? 2. Which migrations explain it?",
  });

  const payload = server.callTool("render_artifact", args);

  assert.equal(
    payload.manifest.blocks[0].body,
    "1. Review account drivers 2. Ask account teams for context 3. Monitor next week",
  );
  assert.equal(
    payload.manifest.blocks[3].body,
    "1. Is the gain durable? 2. Which migrations explain it?",
  );
});

test("JavaScript MCP server leaves percent chart scale to the manifest data contract", () => {
  const args = artifactPayload("report");
  args.manifest.charts[0].valueFormat = "percent";
  args.manifest.charts[0].encodings.y = { field: "share", type: "quantitative" };
  args.snapshot.datasets.weekly_revenue = [
    { segment: "Alpha", share: 2.0 },
    { segment: "Beta", share: 0.851 },
  ];

  assert.equal(server.callTool("validate_artifact", args).ok, true);
});

test("JavaScript MCP server preserves percent format and percent unit for rate chart tooltips", () => {
  const payload = server.callTool("render_chart", {
    title: "Daily no-deployment rate",
    source: sourceQueryForTest(),
    table: {
      columns: [
        { key: "ds", label: "Date", type: "date" },
        { key: "segment", label: "Segment", type: "text" },
        { key: "no_deployment_rate", label: "No-deployment rate", type: "number", format: "percent", unit: "%" },
      ],
      rows: [
        { ds: "2026-05-25", segment: "Broad", no_deployment_rate: 0.98 },
        { ds: "2026-05-25", segment: "Narrow", no_deployment_rate: 0.97 },
        { ds: "2026-05-26", segment: "Broad", no_deployment_rate: 0.965 },
        { ds: "2026-05-26", segment: "Narrow", no_deployment_rate: 0.955 },
      ],
      row_count: 4,
      truncated: false,
    },
    chart: {
      type: "line",
      fields: {
        x: { field: "ds", type: "temporal" },
        y: { field: "no_deployment_rate", type: "quantitative", unit: "%" },
        color: { field: "segment", type: "nominal" },
      },
      options: { points: "always" },
    },
    display: {
      unit: "%",
      y_axis_title: "no_deployment_rate (%)",
    },
  });

  assert.equal(payload.chart_spec.valueFormat, "percent");
  assert.equal(payload.chart_spec.unit, "%");
  assert.equal(payload.chart_spec.encodings.y.format, "percent");
  assert.equal(payload.chart_spec.encodings.y.unit, "%");
  assert.deepEqual(payload.data.map((row) => row.y), [0.98, 0.97, 0.965, 0.955]);
});

test("artifact chart widget bridge preserves y value formats for synthetic value fields", () => {
  const app = readFileSync(new URL("../src/analytics-app/App.tsx", import.meta.url), "utf8");

  assert.match(app, /const yFormat = yEncoding\.format \?\? chart\.valueFormat;/);
  assert.match(app, /\.\.\.\(format \? \{ format \} : \{\}\),/);
  assert.match(app, /\{ key: "value", label: chartEncodingLabel\(chart, "y", "Value"\), type: "number", \.\.\.yFormatSpec, unit \}/);
  assert.match(app, /y: \{ aggregate: "sum", field: "value", type: "quantitative", \.\.\.yFormatSpec, unit \}/);
});

test("JavaScript MCP server requires explicit artifact chart source links", () => {
  const args = artifactPayload("report");
  delete args.manifest.charts[0].sourceId;

  assert.throws(
    () => server.callTool("validate_artifact", args),
    /actual SQL query text/,
  );
});

test("JavaScript MCP server accepts custom HTML artifact blocks", () => {
  const args = artifactPayload("report");
  args.manifest.blocks.push({
    id: "custom_html",
    type: "html",
    body: '<section style="font: 14px sans-serif"><strong>Custom HTML</strong><div data-value="42"></div></section>',
  });

  const payload = server.callTool("render_artifact", args);

  assert.equal(payload.manifest.blocks[3].type, "html");
  assert.match(payload.manifest.blocks[3].body, /Custom HTML/);

  const htmlField = artifactPayload("report");
  htmlField.manifest.blocks.push({
    id: "custom_html",
    type: "html",
    html: "<strong>Custom HTML</strong>",
  });
  assert.throws(
    () => server.callTool("render_artifact", htmlField),
    /uses html, but html blocks render body/,
  );

  const fixedHeight = artifactPayload("report");
  fixedHeight.manifest.blocks.push({
    id: "custom_html",
    type: "html",
    body: "<strong>Custom HTML</strong>",
    height: 240,
  });
  assert.throws(
    () => server.callTool("render_artifact", fixedHeight),
    /height is not supported for html blocks/,
  );

  const missingHtml = artifactPayload("report");
  missingHtml.manifest.blocks.push({
    id: "custom_html",
    type: "html",
  });

  assert.throws(
    () => server.callTool("validate_artifact", missingHtml),
    /manifest\.blocks\[3\]\.body must be a non-empty HTML string/,
  );
});

test("JavaScript MCP server accepts additional ordered report blocks", () => {
  const args = artifactPayload("report");
  args.manifest.blocks.push({
    id: "questions_text",
    type: "markdown",
    body: "- Is the revenue shift durable?",
  });

  const payload = server.callTool("render_artifact", args);

  assert.equal(payload.manifest.blocks[3].id, "questions_text");
});

test("JavaScript MCP server validates metric-strip blocks", () => {
  const args = artifactPayload("report");
  args.manifest.blocks.unshift({
    id: "headline_metrics",
    type: "metric-strip",
    cardIds: ["revenue_card"],
  });

  const payload = server.callTool("validate_artifact", args);
  assert.equal(payload.ok, true);

  const missingCard = artifactPayload("report");
  missingCard.manifest.blocks.unshift({
    id: "headline_metrics",
    type: "metric-strip",
    cardIds: ["missing_card"],
  });
  assert.throws(
    () => server.callTool("validate_artifact", missingCard),
    /cardIds\[0\] does not match a manifest card/,
  );

  const missingSource = artifactPayload("report");
  missingSource.manifest.blocks.unshift({
    id: "headline_metrics",
    type: "metric-strip",
    cardIds: ["revenue_card"],
  });
  delete missingSource.manifest.cards[0].sourceId;
  assert.throws(
    () => server.callTool("validate_artifact", missingSource),
    /manifest\.cards\[0\]\.source must include the actual SQL query text/,
  );

  const missingDashboardSource = artifactPayload("dashboard");
  delete missingDashboardSource.manifest.cards[0].sourceId;
  assert.throws(
    () => server.callTool("validate_artifact", missingDashboardSource),
    /manifest\.cards\[0\]\.source must include the actual SQL query text/,
  );

  const inlineSource = artifactPayload("report");
  inlineSource.manifest.blocks.unshift({
    id: "headline_metrics",
    type: "metric-strip",
    cardIds: ["revenue_card"],
  });
  delete inlineSource.manifest.cards[0].sourceId;
  inlineSource.manifest.cards[0].source = sourceQueryForTest();
  assert.equal(server.callTool("validate_artifact", inlineSource).ok, true);

  for (const cardCount of [5, 7]) {
    const manyCards = artifactPayload("dashboard");
    manyCards.manifest.cards = Array.from({ length: cardCount }, (_, index) => ({
      ...manyCards.manifest.cards[0],
      id: `revenue_card_${index + 1}`,
      metrics: [{ label: `Revenue ${index + 1}`, field: "revenue_m", format: "currency" }],
    }));
    manyCards.manifest.blocks[0].cardIds = manyCards.manifest.cards.map((card) => card.id);
    const rendered = server.callTool("render_artifact", manyCards);
    assert.deepEqual(rendered.manifest.blocks[0].cardIds, manyCards.manifest.blocks[0].cardIds);
    assert.equal(rendered.manifest.cards.length, cardCount);
  }
});

test("funnel labels use an explicit high-contrast fill", () => {
  const chartTokens = readFileSync(
    new URL("../src/analytics-app/charting/chart-tokens.css", import.meta.url),
    "utf8",
  );
  const appCss = readFileSync(new URL("../src/analytics-app/styles.css", import.meta.url), "utf8");

  assert.match(chartTokens, /--ds-chart-funnel-label: #ffffff;/);
  for (const css of [chartTokens, appCss]) {
    const funnelLabelBlock = css.split(".funnel-label", 2)[1].split("}", 1)[0];
    assert.match(funnelLabelBlock, /fill: var\(--ds-chart-funnel-label, #ffffff\);/);
    assert.doesNotMatch(funnelLabelBlock, /mix-blend-mode/);
    assert.doesNotMatch(funnelLabelBlock, /fill: var\(--ds-surface/);
  }
});

test("bar charts render direct value labels without hover", () => {
  const renderer = readFileSync(
    new URL("../src/analytics-app/charting/ChartRenderer.tsx", import.meta.url),
    "utf8",
  );
  const chartTokens = readFileSync(
    new URL("../src/analytics-app/charting/chart-tokens.css", import.meta.url),
    "utf8",
  );

  assert.match(renderer, /function shouldShowBarValueLabels/);
  assert.match(renderer, /function visibleBarValueLabelSides/);
  assert.match(renderer, /const showBarValueLabels = shouldShowBarValueLabels/);
  assert.match(renderer, /barValueLabelSides\.hasNegative/);
  assert.match(renderer, /barValueLabelSides\.hasNonNegative/);
  assert.match(renderer, /<LabelList/);
  assert.match(renderer, /renderBarValueLabel/);
  assert.match(chartTokens, /\.chart-bar-value-label/);
});

test("signed vertical bar labels are positioned outside negative bars", () => {
  const renderer = readFileSync(
    new URL("../src/analytics-app/charting/ChartRenderer.tsx", import.meta.url),
    "utf8",
  );
  const labelRenderer = renderer
    .split("function renderBarValueLabel", 2)[1]
    .split("function categoryBarTooltipColor", 1)[0];

  assert.match(labelRenderer, /const top = Math\.min\(numericY, numericY \+ numericHeight\);/);
  assert.match(labelRenderer, /const bottom = Math\.max\(numericY, numericY \+ numericHeight\);/);
  assert.match(labelRenderer, /y=\{isNegative \? bottom \+ BAR_NEGATIVE_VALUE_LABEL_OFFSET : top - BAR_VALUE_LABEL_OFFSET\}/);
});

test("signed vertical bar labels reserve compact axis clearance", () => {
  const labelRenderer = readFileSync(
    new URL("../src/analytics-app/charting/ChartRenderer.tsx", import.meta.url),
    "utf8",
  );
  assert.match(labelRenderer, /const BAR_NEGATIVE_VALUE_LABEL_AXIS_GUTTER = 40;/);
});

test("signed horizontal bar labels reserve clearance on their value side", () => {
  const renderer = readFileSync(
    new URL("../src/analytics-app/charting/ChartRenderer.tsx", import.meta.url),
    "utf8",
  );
  const labelRenderer = renderer
    .split("function renderBarValueLabel", 2)[1]
    .split("function categoryBarTooltipColor", 1)[0];

  assert.match(labelRenderer, /textAnchor=\{isNegative \? "end" : "start"\}/);
  assert.match(labelRenderer, /x=\{isNegative \? left - BAR_VALUE_LABEL_OFFSET : right \+ BAR_VALUE_LABEL_OFFSET\}/);
  assert.match(
    renderer,
    /horizontal && barValueLabelSides\.hasNegative\s+\? Math\.max\(baseLeftMargin, BAR_VALUE_LABEL_HORIZONTAL_GUTTER\)/,
  );
  assert.match(
    renderer,
    /horizontal && barValueLabelSides\.hasNonNegative\s+\? BAR_VALUE_LABEL_HORIZONTAL_GUTTER/,
  );
});

test("encoded funnel charts keep a single series even when color is present", () => {
  const helpers = readFileSync(
    new URL("../src/analytics-app/charting/chart-app-helpers.tsx", import.meta.url),
    "utf8",
  );

  assert.match(helpers, /if \(chart\.type === "funnel" \|\| !colorField \|\| shouldKeepSignedBarAsSingleSeries/);
});

test("encoded grouped scatter rows preserve size and label fields", () => {
  const helpers = readFileSync(
    new URL("../src/analytics-app/charting/chart-app-helpers.tsx", import.meta.url),
    "utf8",
  );
  const groupedSeriesBlock = helpers
    .split("const seriesFields = new Map", 2)[1]
    .split("const rowsByX = new Map", 1)[0];

  assert.match(groupedSeriesBlock, /if \(chart\.type === "scatter"\)/);
  assert.match(groupedSeriesBlock, /rows: rows\.map/);
  assert.match(groupedSeriesBlock, /\{ \.\.\.row, \[seriesField\]: row\[yField\] \}/);
});

test("encoded grouped scatter renders each bubble from the encoded y field", () => {
  const renderer = readFileSync(
    new URL("../src/analytics-app/charting/ChartRenderer.tsx", import.meta.url),
    "utf8",
  );
  const scatterBlock = renderer
    .split(') : chart.type === "scatter" ? (', 2)[1]
    .split(') : chart.type === "area" || chart.type === "stackedArea" ?', 1)[0];

  assert.match(renderer, /const scatterYField = chart\.type === "scatter" \? chartEncodingField\(chart, "y"\) : undefined;/);
  assert.match(scatterBlock, /renderYAxis\(scatterYField \?\? firstSeries\.field\)/);
  assert.match(scatterBlock, /const seriesRows = rows\.filter\(\(row\) => asNumber\(row\[series\.field\]\) != null\);/);
  assert.match(scatterBlock, /const scatterDataKey = scatterYField && seriesRows\.some\(\(row\) => asNumber\(row\[scatterYField\]\) != null\)/);
  assert.match(scatterBlock, /data=\{seriesRows\}/);
  assert.match(scatterBlock, /dataKey=\{scatterDataKey\}/);
});

test("legend buttons stay transparent at rest while exposing hover and focus states", () => {
  const chartTokens = readFileSync(
    new URL("../src/analytics-app/charting/chart-tokens.css", import.meta.url),
    "utf8",
  );

  assert.match(chartTokens, /\.chart-legend-button:hover/);
  assert.match(chartTokens, /\.chart-legend-button:focus-visible/);
  assert.match(chartTokens, /\.chart-legend-button \{[\s\S]*border: 0;[\s\S]*background: transparent;/);
  assert.match(chartTokens, /\.chart-legend-button:hover \{[\s\S]*color: var\(--ds-chart-text\);/);
  assert.match(chartTokens, /box-shadow: 0 0 0 3px/);
});

test("source data modal tables fill the available modal width", () => {
  const app = readFileSync(new URL("../src/analytics-app/App.tsx", import.meta.url), "utf8");
  const css = readFileSync(new URL("../src/analytics-app/styles.css", import.meta.url), "utf8");

  assert.match(app, /className="source-data-table"/);
  assert.match(css, /\.source-data-table \{/);
  assert.match(css, /\.source-data-table \.table-scroll-content \{/);
  assert.match(css, /width: 100%;/);
  assert.match(css, /min-width: 100%;/);
});

test("funnel shapes use Recharts label view box geometry", () => {
  const renderer = readFileSync(
    new URL("../src/analytics-app/charting/ChartRenderer.tsx", import.meta.url),
    "utf8",
  );
  const shapeRenderer = renderer
    .split("function renderRoundedFunnelShape", 2)[1]
    .split("function renderFunnelCenterLabel", 1)[0];

  assert.match(shapeRenderer, /labelViewBox\?\.x \?\? x/);
  assert.match(shapeRenderer, /labelViewBox\?\.y \?\? y/);
  assert.match(shapeRenderer, /labelViewBox\?\.upperWidth \?\? upperWidth/);
  assert.match(shapeRenderer, /labelViewBox\?\.lowerWidth \?\? lowerWidth/);
  assert.match(shapeRenderer, /labelViewBox\?\.height \?\? height/);
});

test("category x-axis labels wrap when crowded and rotate only when requested", () => {
  const renderer = readFileSync(
    new URL("../src/analytics-app/charting/ChartRenderer.tsx", import.meta.url),
    "utf8",
  );
  const rotationPolicy = renderer
    .split("function shouldRotateCategoryXAxisLabels", 2)[1]
    .split("function shouldWrapCategoryXAxisLabels", 1)[0];
  const wrappingHeuristic = renderer
    .split("function shouldWrapCategoryXAxisLabels", 2)[1]
    .split("function getFunnelStageColor", 1)[0];

  assert.match(rotationPolicy, /categoryLabelPolicy === "rotate"/);
  assert.match(wrappingHeuristic, /availableWidth: number/);
  assert.match(wrappingHeuristic, /labelPolicy === "wrap"/);
  assert.match(wrappingHeuristic, /longestLabelWidth <= labelSlotWidth\) return false/);
  assert.match(wrappingHeuristic, /if \(maxLength >= CATEGORY_X_AXIS_LONG_LABEL_LENGTH\) return true/);
  assert.match(renderer, /function WrappedCategoryXAxisTick/);
  assert.match(renderer, /function sparseCategoryXAxisTicks/);
  assert.match(renderer, /CATEGORY_X_AXIS_MIN_VISIBLE_TICK_SPACING/);
  assert.match(renderer, /if \(ticks\[ticks\.length - 1\] !== last\) ticks\.push\(last\)/);
  assert.match(renderer, /ticks: categoryXAxisTicks/);
});

test("category x-axis wrapping respects narrow slots and balances long labels", () => {
  const renderer = readFileSync(
    new URL("../src/analytics-app/charting/ChartRenderer.tsx", import.meta.url),
    "utf8",
  );
  const lineLengthBudget = renderer
    .split("function categoryXAxisWrappedLineLength", 2)[1]
    .split("function sparseCategoryXAxisTicks", 1)[0];
  const balancedSplit = renderer
    .split("function balancedCategoryAxisLabelSplit", 2)[1]
    .split("function wrapCategoryAxisLabel", 1)[0];
  const wrappedTick = renderer
    .split("function WrappedCategoryXAxisTick", 2)[1]
    .split("function categoryXAxisLabels", 1)[0];

  assert.doesNotMatch(renderer, /CATEGORY_X_AXIS_MIN_LINE_CHARACTERS/);
  assert.match(lineLengthBudget, /Math\.max\(1, Math\.floor\(slotWidth \/ CATEGORY_X_AXIS_ESTIMATED_CHAR_WIDTH\)\)/);
  assert.match(balancedSplit, /const midpoint = value\.length \/ 2/);
  assert.match(balancedSplit, /value\.matchAll\(\/\\s\+\/g\)/);
  assert.match(balancedSplit, /Math\.abs\(index - midpoint\) < Math\.abs\(best - midpoint\)/);
  assert.match(balancedSplit, /Math\.ceil\(midpoint\)/);
  assert.match(renderer, /if \(safeMaxLength === 1\) return "…"/);
  assert.match(wrappedTick, /<title>\{value\}<\/title>/);
});

test("numeric axis ticks omit repeated units while axis titles carry unit context", () => {
  const renderer = readFileSync(
    new URL("../src/analytics-app/charting/ChartRenderer.tsx", import.meta.url),
    "utf8",
  );
  const helpers = readFileSync(
    new URL("../src/analytics-app/charting/chart-app-helpers.tsx", import.meta.url),
    "utf8",
  );
  const transforms = readFileSync(
    new URL("../src/analytics-app/charting/chart-transforms.ts", import.meta.url),
    "utf8",
  );
  const numericTick = renderer
    .split("function NumericYAxisTick", 2)[1]
    .split("function XAxisEndpointTick", 1)[0];
  const horizontalBar = renderer
    .split('horizontal && !stacked && (chart.type === "bar" || chart.type === "horizontalBar") ? (', 2)[1]
    .split(") : horizontal && stacked && (", 1)[0];

  assert.match(numericTick, /formatValue\(payload\?\.value, valueFormat\)/);
  assert.doesNotMatch(numericTick, /\bunit\b/);
  assert.doesNotMatch(renderer, /tickFormatter=\{\(value\) => formatValue\(value, [^}\n]*chart\.unit/);
  assert.match(transforms, /labels: ticks\.map\(\(value\) => formatValue\(value, chart\.valueFormat\)\)/);
  assert.match(helpers, /function chartEncodingAxisTitle/);
  assert.match(helpers, /function axisTitlesForEncodedChart/);
  assert.match(helpers, /horizontal \? encodedYAxisTitle : encodedXAxisTitle/);
  assert.match(helpers, /return `\$\{label\} \(\$\{unit\}\)`/);
  assert.match(renderer, /const horizontalValueAxisLabel = chart\.xAxisTitle \? bottomAxisLabel\(chart\.xAxisTitle\) : undefined;/);
  assert.match(horizontalBar, /<XAxis[^>]*label=\{horizontalValueAxisLabel\}/);
  assert.match(horizontalBar, /<YAxis[^>]*label=\{horizontalCategoryAxisLabel\}/);
  assert.doesNotMatch(horizontalBar, /label=\{yAxisLabel\}/);
  assert.doesNotMatch(horizontalBar, /label=\{xAxisLabel\}/);
});

test("the top bar uses the main page background surface", () => {
  const styles = readFileSync(new URL("../src/analytics-app/styles.css", import.meta.url), "utf8");
  const topBar = styles
    .split(".analytics-top-bar {", 2)[1]
    .split("}", 1)[0];

  assert.match(topBar, /background: var\(--ds-bg\);/);
  assert.doesNotMatch(topBar, /background: var\(--ds-surface\);/);
});

test("artifact table movement cells render explicit positive and negative signs", () => {
  const app = readFileSync(new URL("../src/analytics-app/App.tsx", import.meta.url), "utf8");
  const tableFormatter = app
    .split("function formatTableCellValue", 2)[1]
    .split("function normalizedTableTextLength", 1)[0];

  assert.match(tableFormatter, /tableColumnLooksLikeMovement\(column\)/);
  assert.match(tableFormatter, /numeric == null \|\| numeric === 0/);
  assert.match(tableFormatter, /return `\$\{numeric > 0 \? "\+" : ""\}\$\{rendered\}`/);
  assert.match(app, /tableCellMovementClass\(column, value\)/);
});

test("artifact tables initialize interactive sorting from the manifest default", () => {
  const app = readFileSync(new URL("../src/analytics-app/App.tsx", import.meta.url), "utf8");
  const artifactWidget = readFileSync(
    new URL("../src/datascience-artifact-widget.jsx", import.meta.url),
    "utf8",
  );

  assert.match(app, /function tableDefaultSort\(table\)/);
  assert.match(app, /useState\(\(\) => tableDefaultSort\(table\)\)/);
  assert.match(app, /setSortState\(tableDefaultSort\(table\)\)/);
  assert.match(artifactWidget, /defaultSort\.field must reference a declared table column/);
  assert.match(artifactWidget, /defaultSort\.direction must be asc or desc/);
});

test("artifact card chart type menu is limited by data shape", () => {
  const compatibility = readFileSync(
    new URL("../src/analytics-app/charting/chart-compatibility.ts", import.meta.url),
    "utf8",
  );
  const helpers = readFileSync(
    new URL("../src/analytics-app/charting/chart-app-helpers.tsx", import.meta.url),
    "utf8",
  );
  const app = readFileSync(new URL("../src/analytics-app/App.tsx", import.meta.url), "utf8");

  assert.match(compatibility, /export function compatibleChartTypesForDataShape/);
  assert.match(compatibility, /const FUNNEL_SHAPE_TYPES: ChartType\[\] = \["bar", "funnel"\]/);
  assert.match(compatibility, /types: \["bar", "leaderboard"\]/);
  assert.match(compatibility, /const HIDDEN_BAR_VARIANT_TYPE_LIST: ChartType\[\] = \[/);
  assert.match(compatibility, /if \(chart\.type === "funnel" \|\| chart\.intent === "funnel"\) return FUNNEL_SHAPE_TYPES;/);
  assert.match(helpers, /export function compatibleChartTypesForArtifactCard/);
  assert.equal((app.match(/compatibleChartTypesForArtifactCard\(overriddenChart, chartRows\)/g) || []).length, 1);
  assert.match(app, /const dashboardContentBlocks = useMemo\([\s\S]*<ReportBlockCard/);
  assert.match(app, /applyChartSpecOverride\(chart, chartSpecOverride\)/);
  assert.match(app, /chartSpecOverride=\{chart \? chartSpecOverrides\[chart\.id\] : undefined\}/);
  assert.match(app, /const chartModalTypeOptions = chartModalBaseChart\s+\?\s+compatibleChartTypesFor\(chartModalBaseChart, chartModalRows\)/);
});

test("artifact data source dialogs use three accessible tabs with one scroll body", () => {
  const app = readFileSync(new URL("../src/analytics-app/App.tsx", import.meta.url), "utf8");
  const tableSizing = readFileSync(new URL("../src/analytics-app/tables/tableSizing.ts", import.meta.url), "utf8");
  const styles = readFileSync(new URL("../src/analytics-app/styles.css", import.meta.url), "utf8");

  assert.match(app, /function Tabs\(\{ ariaLabel, onSelect, selectedKey, tabs \}\)/);
  assert.match(app, /role="tablist"/);
  assert.match(app, /\{ id: "overview", label: "Overview", panelId:/);
  assert.match(app, /\{ id: "data", label: "Data preview", panelId:/);
  assert.match(app, /\{ id: "sql", label: "SQL query", panelId:/);
  assert.match(app, /className="source-modal-tab-indicator"/);
  assert.equal((app.match(/className="source-modal-tab-indicator"/g) || []).length, 1);
  assert.match(app, /const updateIndicator = useCallback/);
  assert.match(app, /indicator\.style\.transform = `translate3d/);
  assert.match(app, /new ResizeObserver\(updateIndicator\)/);
  assert.match(app, /event\.key === "ArrowRight"/);
  assert.match(app, /event\.key === "Home"/);
  assert.match(app, /activeTab === "data"/);
  assert.match(app, /id=\{`\$\{tabId\}-data-panel`\}/);
  assert.doesNotMatch(app, /<h3>Data preview<\/h3>/);
  assert.match(app, /function Badge\(\{ children, className = "" \}\)/);
  assert.match(app, /function sourceMetadataValue/);
  assert.match(app, /function sourceMetadataChips/);
  assert.match(app, /<Badge className="source-metadata-chip"/);
  assert.doesNotMatch(app, /function sourceMetadataBadge/);
  assert.doesNotMatch(app, /className="source-metadata-code"/);
  assert.match(app, /<dd>\{sourceMetadataValue\(details\.dataset\)\}<\/dd>/);
  assert.match(app, /sourceMetadataChips\(details\.tables\)/);
  assert.match(app, /sourceMetadataChips\(details\.filters\)/);
  assert.match(app, /function metricDefinitionRows/);
  assert.match(app, /const SOURCE_METRIC_DEFINITION_COLUMNS = \[/);
  assert.match(app, /dataset="__source_metric_definitions" density="spacious" fillAvailableWidth rows=\{metricDefinitionRows/);
  assert.doesNotMatch(app, /<dt>Metric definitions<\/dt>/);
  assert.doesNotMatch(app, /className="source-metric-definition-table"/);
  assert.match(app, /are\|is\|equals\|uses\?\|means\|measures/);
  assert.match(app, /itemLabel=\{chart\.title\} itemType="Chart"/);
  assert.match(app, /itemLabel=\{label\} itemType="Metric"/);
  assert.match(app, /itemLabel=\{table\.title\} itemType="Table"/);
  assert.match(app, /function sourceSnapshotDate/);
  assert.match(app, /<dt>Data snapshot<\/dt>/);
  assert.match(app, /sourceSnapshotDate\(details\.snapshot\)/);
  assert.doesNotMatch(app, /sourceSnapshotSubtitle/);
  assert.doesNotMatch(app, /source-overview-summary/);
  assert.doesNotMatch(app, /const summary =/);
  assert.match(app, /className="source-modal-body"/);
  assert.match(app, /function SourceDataTable/);
  assert.match(app, /function CardSourceModalDialog/);
  assert.match(app, /function sourceForCard/);
  assert.doesNotMatch(app, /kpi-source-button|kpi-source-icon|FileSearch2/);
  assert.match(app, /<CardSourceModalDialog activeFilters=/);
  assert.match(app, /className="source-data-table"/);
  assert.match(app, /<TableContent allowColumnResize=\{false\} columnWidths=/);
  assert.match(app, /const SOURCE_DATA_PREVIEW_PAGE_SIZE = 10;/);
  assert.match(app, /pageSize: requestedPageSize = TABLE_CARD_PAGE_SIZE/);
  assert.match(app, /pageSize=\{SOURCE_DATA_PREVIEW_PAGE_SIZE\}/);
  assert.equal((app.match(/pageSize=\{SOURCE_DATA_PREVIEW_PAGE_SIZE\}/g) || []).length, 3);
  assert.doesNotMatch(app, /function SourcePreviewRows/);
  assert.match(app, /className="modal-close-button"/);
  assert.match(app, /useModalScrollLock\(true\)/);
  assert.match(styles, /\.native-modal\.source-modal/);
  assert.doesNotMatch(styles, /\.kpi-source-button|\.kpi-source-icon/);
  assert.match(styles, /\.source-query \{[\s\S]*?max-height: none;[\s\S]*?overflow: visible;/);
  assert.match(styles, /\.source-query \{[\s\S]*?white-space: pre-wrap;/);
  assert.match(styles, /\.source-modal-body \{[\s\S]*?overflow-y: auto;/);
  assert.match(styles, /\.source-details-summary \{[\s\S]*?grid-template-columns: repeat\(3, minmax\(0, 1fr\)\);/);
  assert.match(styles, /\.source-details-stack \{[\s\S]*?display: grid;[\s\S]*?gap: 16px;/);
  assert.match(styles, /\.chip \{[\s\S]*?border-radius: var\(--ds-radius-pill\);/);
  assert.match(styles, /\.source-metadata-chip \{[\s\S]*?background: transparent;[\s\S]*?color: var\(--ds-text-primary\);[\s\S]*?font-family: var\(--ds-font\);[\s\S]*?font-size: var\(--codex-font-size-base\);[\s\S]*?font-weight: 400;[\s\S]*?padding-block: 4px;/);
  assert.doesNotMatch(styles, /\.source-metadata-code \{/);
  assert.doesNotMatch(styles, /\.source-metric-definitions > dt \{/);
  assert.match(styles, /\.source-metric-definitions \{[\s\S]*?min-width: 0;/);
  assert.match(styles, /\.source-metric-definitions tbody \.table-column-content-fit \{[\s\S]*?font-weight: 500;/);
  assert.doesNotMatch(styles, /\.source-metric-definition-table \{/);
  assert.match(styles, /\.source-modal-tab \{[\s\S]*?padding: 0 0 13px;/);
  assert.match(styles, /\.source-modal-panel > \.modal-header \{[\s\S]*?padding: 20px 24px 4px;/);
  assert.match(styles, /\.native-modal\.source-modal \{[\s\S]*?height: fit-content;[\s\S]*?max-height: min\(760px, calc\(100dvh - 48px\)\);/);
  assert.match(styles, /\.source-modal-panel \{[\s\S]*?height: auto;[\s\S]*?max-height: min\(760px, calc\(100dvh - 48px\)\);/);
  assert.match(styles, /\.source-modal-tabs \{[\s\S]*?border-bottom: 1px solid var\(--ds-border-subtle\);/);
  assert.match(styles, /\.source-modal-tab-indicator \{[\s\S]*?height: 2px;[\s\S]*?transform 180ms/);
  assert.match(styles, /\.source-modal-tab-indicator\[data-ready="true"\] \{[\s\S]*?opacity: 1;/);
  assert.doesNotMatch(styles, /\.source-modal-panel > \.modal-header \{[^}]*border(?:-bottom)?:/);
  assert.doesNotMatch(styles, /\.source-filter-chip \{/);
  assert.match(app, /\{ field: "metric", label: "Metric", sizing: "content", type: "text" \}/);
  assert.match(app, /column\.sizing === "content"/);
  assert.match(app, /calculateTableSizing\(table\.columns, activeColumnWidths, tableViewportWidth, shouldFillAvailableWidth\)/);
  assert.match(tableSizing, /column\.sizing !== "content"/);
  assert.match(tableSizing, /normalizedViewportWidth - baseTableWidth/);
  assert.match(tableSizing, /extraWidthPerFlexibleColumn/);
  assert.match(app, /new ResizeObserver\(updateViewportWidth\)/);
  assert.match(styles, /\.data-table-smart-layout \.table-column-content-fit/);
  assert.match(styles, /\.source-query \{[\s\S]*?max-height: none;[\s\S]*?overflow: visible;/);
  assert.match(styles, /\.source-query \{[\s\S]*?white-space: pre-wrap;/);
});

test("JavaScript MCP server rejects ready artifacts with access issues", () => {
  const args = artifactPayload("report");
  args.snapshot.accessIssues = [
    {
      id: "optional_join_denied",
      sourceId: "exploratory_join",
      message: "Optional use-case join was not readable.",
    },
  ];

  assert.throws(
    () => server.callTool("render_artifact", args),
    /\$\.snapshot\.accessIssues is only allowed when \$\.snapshot\.status is partial or blocked/,
  );
});

test("JavaScript MCP server rejects malformed report block shapes before rendering", () => {
  const missingTitle = artifactPayload("report");
  delete missingTitle.manifest.title;
  assert.throws(
    () => server.callTool("render_artifact", missingTitle),
    /\$\.manifest\.title is required for artifact rendering/,
  );

  const blankTitle = artifactPayload("report");
  blankTitle.manifest.title = "  ";
  assert.throws(
    () => server.callTool("validate_artifact", blankTitle),
    /\$\.manifest\.title is required for artifact rendering/,
  );

  const withAudience = artifactPayload("report");
  withAudience.manifest.audience = "product stakeholders";
  assert.throws(
    () => server.callTool("validate_artifact", withAudience),
    /\$\.manifest\.audience is not supported/,
  );

  const withFreshness = artifactPayload("report");
  withFreshness.manifest.freshness = { snapshotPath: "data/snapshot.json" };
  assert.throws(
    () => server.callTool("validate_artifact", withFreshness),
    /\$\.manifest\.freshness is not supported/,
  );

  const withLegacyMetricDelta = artifactPayload("report");
  withLegacyMetricDelta.manifest.cards[0].deltaField = "wow";
  assert.throws(
    () => server.callTool("validate_artifact", withLegacyMetricDelta),
    /\$\.manifest\.cards\[0\]\.deltaField is not supported; use metrics\[\]/,
  );

  const withInitialView = artifactPayload("report");
  withInitialView.initial_view = { displayMode: "inline" };
  assert.throws(
    () => server.callTool("render_artifact", withInitialView),
    /initial_view is not supported/,
  );

  const withDefinitions = artifactPayload("report");
  withDefinitions.snapshot.definitions = [{ metric: "Revenue", definition: "Booked usage." }];
  assert.throws(
    () => server.callTool("validate_artifact", withDefinitions),
    /\$\.snapshot\.definitions is not supported/,
  );

  const noBlocks = artifactPayload("report");
  delete noBlocks.manifest.blocks;
  assert.throws(
    () => server.callTool("render_artifact", noBlocks),
    /must contain top-level artifact blocks/,
  );
});

test("JavaScript MCP server allows a visible report heading that matches the report title", () => {
  const args = artifactPayload("report");
  args.manifest.blocks[0].body = "# Revenue momentum";

  assert.equal(server.callTool("validate_artifact", args).ok, true);
});

test("JavaScript MCP server requires canonical dashboard blocks", () => {
  const noBlocks = artifactPayload("dashboard");
  delete noBlocks.manifest.blocks;
  assert.throws(
    () => server.callTool("render_artifact", noBlocks),
    /must contain top-level artifact blocks/,
  );

});

test("JavaScript MCP server requires reports to include a chart visualization", () => {
  const args = artifactPayload("report");
  args.manifest.blocks = args.manifest.blocks.filter((block) => block.type !== "chart");

  assert.throws(
    () => server.callTool("validate_artifact", args),
    /must include at least one chart block for report artifacts/,
  );
  assert.throws(
    () => server.callTool("render_artifact", args),
    /must include at least one chart block for report artifacts/,
  );
});

test("JavaScript MCP server advertises artifact handoff before fallback widgets", () => {
  const toolDefinitions = server.toolDefinitions();
  const artifactTool = toolDefinitions
    .find((tool) => tool.name === "render_artifact");
  const chartTool = toolDefinitions
    .find((tool) => tool.name === "render_chart");
  const validateTool = toolDefinitions
    .find((tool) => tool.name === "validate_artifact");

  assert.ok(artifactTool);
  assert.ok(chartTool);
  assert.ok(validateTool);
  assert.match(server.SERVER_INSTRUCTIONS, /^Before rendering a report or dashboard artifact/);
  assert.match(server.SERVER_INSTRUCTIONS, /manifest\.blocks/);
  assert.match(server.SERVER_INSTRUCTIONS, /first markdown block whose body is a # heading matching manifest\.title/);
  assert.match(server.SERVER_INSTRUCTIONS, /independently editable major report section/);
  assert.match(server.SERVER_INSTRUCTIONS, /multiple peer ## headings/);
  assert.match(server.SERVER_INSTRUCTIONS, /One headline metric does not mean one metrics\[\] entry/);
  assert.match(server.SERVER_INSTRUCTIONS, /defaultSort/);
  assert.match(validateTool.description, /without rendering a hosted widget/);
  assert.equal(validateTool._meta, undefined);
  assert.match(artifactTool.description, /dashboard or report artifact/);
  assert.match(artifactTool.description, /Call validate_artifact first/);
  assert.match(artifactTool.inputSchema.properties.manifest.description, /top-level manifest\.blocks/);
  assert.match(artifactTool.inputSchema.properties.manifest.description, /first content heading/);
  assert.match(artifactTool.inputSchema.properties.manifest.properties.blocks.description, /type "html"/);
  assert.match(artifactTool.inputSchema.properties.manifest.properties.blocks.description, /independently editable major report section/);
  assert.match(artifactTool.inputSchema.properties.manifest.properties.title.description, /first content heading/);
  const manifestSchema = artifactTool.inputSchema.properties.manifest;
  const cardSchema = manifestSchema.properties.cards.items;
  assert.ok(cardSchema.required.includes("metrics"));
  assert.equal(cardSchema.properties.valueField, undefined);
  assert.equal(cardSchema.properties.sourceId.type[0], "string");
  assert.ok(cardSchema.properties.source);
  assert.match(cardSchema.properties.sourceId.description, /data-source modal/);
  assert.match(cardSchema.properties.metrics.description, /One headline metric/);
  assert.match(cardSchema.properties.metrics.description, /One headline does not mean one metrics\[\] entry/);
  assert.match(cardSchema.properties.metrics.description, /executive summary or findings/);
  assert.match(cardSchema.properties.metrics.description, /independent secondary metrics/);
  assert.equal(cardSchema.properties.metrics.items.properties.field.type, "string");
  assert.match(cardSchema.properties.metrics.items.properties.format.description, /Use "percent" only for fractional-rate values/);

  const tableSchema = manifestSchema.properties.tables.items;
  const tableColumnSchema = tableSchema.properties.columns.items;
  assert.ok(tableColumnSchema.required.includes("field"));
  assert.equal(tableColumnSchema.properties.key, undefined);
  assert.deepEqual(tableSchema.properties.defaultSort.required, ["field", "direction"]);
  assert.deepEqual(tableSchema.properties.defaultSort.properties.direction.enum, ["asc", "desc"]);
  assert.match(tableColumnSchema.properties.format.description, /98.*use "number" with unit "%"/);

  const chartSchema = manifestSchema.properties.charts.items;
  assert.match(chartSchema.properties.title.description, /Neutral, descriptive chart title/);
  assert.match(chartSchema.properties.title.description, /Do not infer a narrative takeaway/);
  assert.match(chartSchema.properties.valueFormat.description, /0\.98 for 98%/);

  const blockSchema = manifestSchema.properties.blocks.items;
  assert.ok(blockSchema.required.includes("id"));
  assert.equal(blockSchema.properties.markdown, undefined);
  assert.match(blockSchema.properties.sourceId.description, /block-wide provenance for a markdown block/);
  assert.match(blockSchema.properties.sourceId.description, /merged canonical sources/);
  assert.match(blockSchema.properties.sourceId.description, /File and document sources are valid and do not require SQL/);
  assert.match(blockSchema.properties.body.description, /one peer ## heading/);
  assert.match(blockSchema.properties.body.description, /other than the first # title block/);
  assert.match(blockSchema.properties.body.description, /HTML blocks contain raw HTML/);
  assert.deepEqual(artifactTool._meta.ui, {
    resourceUri: server.ARTIFACT_WIDGET_URI,
    visibility: ["model"],
  });
  assert.deepEqual(chartTool._meta.ui, {
    resourceUri: server.CHART_WIDGET_URI,
    visibility: ["model"],
  });
});

test("JavaScript MCP server rejects artifact source and safety violations", () => {
  const args = artifactPayload();
  args.sources[0].id = "not_declared";
  assert.throws(
    () => server.callTool("render_artifact", args),
    /declared in manifest\.sources/,
  );

  const unsafe = artifactPayload();
  unsafe.snapshot.datasets.weekly_revenue[0].customer_email = "person@example.com";
  assert.throws(
    () => server.callTool("render_artifact", unsafe),
    /looks unsafe/,
  );
});

test("JavaScript MCP server allows reviewed customer dimensions in artifacts", () => {
  const args = artifactPayload();
  args.contains_sensitive_data = true;
  args.snapshot.datasets.weekly_revenue[0].customer_name = "Acme Corp";

  const payload = server.callTool("render_artifact", args);

  assert.equal(payload.widget_type, "artifact");
  assert.equal(payload.snapshot.datasets.weekly_revenue[0].customer_name, "Acme Corp");
});

test("JavaScript MCP server renders query-shaped chart payloads", () => {
  const payload = server.callTool("render_chart", queryTablePayload());

  assert.equal(payload.widget_type, "chart");
  assert.equal(payload.source.query.id, "query-123");
  assert.equal(payload.chart.type, "line");
  assert.equal(payload.chart_spec.type, "line");
  assert.equal(payload.chart_spec.encodings.x.field, "reporting_date");
  assert.equal(payload.chart_spec.encodings.y.field, "arr_b");
  assert.equal("xField" in payload.chart_spec, false);
  assert.equal("series" in payload.chart_spec, false);
  assert.equal(payload.chart_spec.xAxisTitle, undefined);
  assert.equal(payload.chart_spec.yAxisTitle, undefined);
  assert.equal(payload.chart_spec.unit, "$B");
  assert.equal("referenceLines" in payload.chart_spec, false);
  assert.equal("chart_rows" in payload, false);
  assert.equal("x_field" in payload, false);
  assert.equal("y_field" in payload, false);
  assert.equal("x_axis_title" in payload, false);
  assert.equal("y_axis_title" in payload, false);
  assert.equal("time_unit" in payload, false);
  assert.deepEqual(payload.data, [
    {
      reporting_date: "2026-03-31",
      arr_b: 2.73,
      x: "2026-03-31",
      y: 2.73,
      size: null,
      series: "ARR",
    },
    {
      reporting_date: "2026-04-30",
      arr_b: 2.9,
      x: "2026-04-30",
      y: 2.9,
      size: null,
      series: "ARR",
    },
  ]);
});

test("JavaScript MCP server requires model-provided chart type and fields", () => {
  const missingType = queryTablePayload();
  delete missingType.chart.type;
  assert.throws(() => server.callTool("render_chart", missingType), /chart\.type is required/);

  const missingX = queryTablePayload();
  delete missingX.chart.fields.x;
  assert.throws(() => server.callTool("render_chart", missingX), /chart\.fields\.x\.field is required/);

  const missingY = queryTablePayload();
  delete missingY.chart.fields.y;
  assert.throws(() => server.callTool("render_chart", missingY), /chart\.fields\.y\.field is required/);
});

test("JavaScript MCP server accepts custom chart axis titles", () => {
  const args = queryTablePayload();
  args.display.x_axis_title = "Fiscal month";
  args.display.y_axis_title = "ARR, billions";

  const payload = server.callTool("render_chart", args);

  assert.equal(payload.display.x_axis_title, "Fiscal month");
  assert.equal(payload.display.y_axis_title, "ARR, billions");
  assert.equal(payload.chart_spec.xAxisTitle, "Fiscal month");
  assert.equal(payload.chart_spec.yAxisTitle, "ARR, billions");
  assert.equal("x_label" in payload, false);
  assert.equal("y_label" in payload, false);
});

test("JavaScript MCP server preserves physical axis titles for horizontal bars", () => {
  const payload = server.callTool("render_chart", {
    title: "Horizontal activation milestones",
    source: sourceQueryForTest(),
    table: {
      columns: [
        { key: "milestone", label: "Activation milestone", type: "text" },
        { key: "workspaces", label: "Activated workspaces", type: "number", format: "number" },
      ],
      rows: [
        { milestone: "Admin invited teammates", workspaces: 1820 },
        { milestone: "Slack integration connected", workspaces: 1428 },
      ],
      row_count: 2,
      truncated: false,
    },
    chart: {
      type: "bar",
      fields: {
        x: { field: "milestone", type: "nominal" },
        y: { field: "workspaces", type: "quantitative" },
      },
      options: { orientation: "horizontal" },
    },
    display: {
      x_axis_title: "Activated workspaces",
      y_axis_title: "Activation milestone",
    },
  });

  assert.equal(payload.chart_spec.settings.orientation, "horizontal");
  assert.equal(payload.chart_spec.xAxisTitle, "Activated workspaces");
  assert.equal(payload.chart_spec.yAxisTitle, "Activation milestone");
});

test("JavaScript MCP server normalizes heatmap encodings to widget field roles", () => {
  const payload = server.callTool("render_chart", {
    title: "Heatmap",
    source: {
      query: {
        engine: "trino",
        sql: "SELECT day_name, segment, score FROM warehouse.heatmap_source",
        id: "heatmap-query",
      },
    },
    table: {
      columns: [
        { key: "day_name", label: "Day", type: "text" },
        { key: "segment", label: "Segment", type: "text" },
        { key: "score", label: "Score", type: "number" },
      ],
      rows: [
        { day_name: "Mon", segment: "Self-serve", score: 18 },
        { day_name: "Mon", segment: "Enterprise", score: 26 },
        { day_name: "Tue", segment: "Self-serve", score: 21 },
        { day_name: "Tue", segment: "Enterprise", score: 31 },
      ],
    },
    chart: {
      type: "heatmap",
      fields: {
        x: { field: "day_name", type: "ordinal" },
        y: { field: "segment", type: "nominal" },
        color: { field: "score", type: "quantitative" },
      },
    },
  });

  assert.equal(payload.chart.fields.y.field, "score");
  assert.equal(payload.chart.fields.color.field, "segment");
  assert.deepEqual(payload.data.map((point) => [point.x, point.y, point.series]), [
    ["Mon", 18, "Self-serve"],
    ["Mon", 26, "Enterprise"],
    ["Tue", 21, "Self-serve"],
    ["Tue", 31, "Enterprise"],
  ]);
});

test("JavaScript MCP server reports heatmap field roles when value encoding is not numeric", () => {
  assert.throws(() => server.callTool("render_chart", {
    title: "Heatmap",
    source: {
      query: {
        engine: "trino",
        sql: "SELECT day_name, segment, score_label FROM warehouse.heatmap_source",
        id: "heatmap-query",
      },
    },
    table: {
      columns: [
        { key: "day_name", label: "Day", type: "text" },
        { key: "segment", label: "Segment", type: "text" },
        { key: "score_label", label: "Score label", type: "text" },
      ],
      rows: [
        { day_name: "Mon", segment: "Self-serve", score_label: "Low" },
        { day_name: "Mon", segment: "Enterprise", score_label: "High" },
      ],
    },
    chart: {
      type: "heatmap",
      fields: {
        x: { field: "day_name", type: "ordinal" },
        y: { field: "score_label", type: "text" },
        color: { field: "segment", type: "nominal" },
      },
    },
  }), /numeric heatmap cell value/);
});

test("JavaScript MCP server keeps scatter size on the source field", () => {
  const payload = server.callTool("render_chart", {
    title: "ARR efficiency by segment",
    source: sourceQueryForTest(),
    table: {
      columns: [
        { key: "conversion_rate", label: "Conversion", type: "percent" },
        { key: "arr_usd", label: "ARR", type: "currency", unit: "USD" },
        { key: "active_accounts", label: "Active Accounts", type: "number" },
        { key: "segment", label: "Segment", type: "text" },
      ],
      rows: [
        { conversion_rate: 0.24, arr_usd: 1445000, active_accounts: 95, segment: "Enterprise" },
        { conversion_rate: 0.20, arr_usd: 846000, active_accounts: 161, segment: "Mid-Market" },
      ],
    },
    chart: {
      type: "scatter",
      fields: {
        x: { field: "conversion_rate", type: "quantitative" },
        y: { field: "arr_usd", type: "quantitative" },
        size: { field: "active_accounts", type: "quantitative" },
        color: { field: "segment", type: "nominal" },
      },
    },
  });

  assert.equal(payload.chart_spec.encodings.size.field, "active_accounts");
  assert.equal(payload.chart_spec.encodings.size.label, "Active Accounts");
  assert.equal(payload.chart_spec.encodings.size.format, "number");
  assert.equal(payload.chart_spec.encodings.x.field, "conversion_rate");
  assert.equal(payload.chart_spec.encodings.y.field, "arr_usd");
  assert.equal(payload.chart_spec.encodings.color.field, "segment");
  assert.equal("chart_rows" in payload, false);
  assert.deepEqual(payload.table.rows.map((row) => row.active_accounts), [95, 161]);
  assert.equal(payload.table.rows.some((row) => "__pointSize" in row), false);
});

test("JavaScript MCP server accepts non-scatter label fields as optional display metadata", () => {
  const payload = server.callTool("render_chart", {
    title: "Leaderboard",
    source: sourceQueryForTest(),
    table: {
      columns: [
        { key: "rank_order", label: "Rank", type: "number" },
        { key: "team", label: "Team", type: "text" },
        { key: "score", label: "Score", type: "number" },
      ],
      rows: [
        { rank_order: 1, team: "Team Atlas", score: 980 },
        { rank_order: 2, team: "Team Beacon", score: 870 },
      ],
    },
    chart: {
      type: "leaderboard",
      fields: {
        x: { field: "team", type: "nominal" },
        y: { field: "score", type: "quantitative" },
        label: { field: "rank_order", type: "quantitative" },
      },
    },
  });

  assert.equal(payload.ok, true);
  assert.equal(payload.chart.fields.label.field, "rank_order");
});

test("JavaScript MCP server exposes chart v1 settings in the chart schema", () => {
  const chartTool = server.toolDefinitions().find((tool) => tool.name === "render_chart");
  const properties = chartTool.inputSchema.properties;
  const chart = chartTool.inputSchema.properties.chart.properties;
  const options = chart.options.properties;
  const display = chartTool.inputSchema.properties.display.properties;
  const tableColumn = properties.table.properties.columns.items.properties;

  assert.match(properties.title.description, /Neutral, descriptive chart title/);
  assert.match(properties.title.description, /Do not infer a narrative takeaway/);
  assert.match(properties.title.description, /explicitly requests a takeaway-led title/);
  assert.match(properties.subtitle.description, /insight or takeaway/);
  assert.match(properties.subtitle.description, /source\.query/);
  assert.deepEqual(options.orientation.enum, ["vertical", "horizontal", null]);
  assert.deepEqual(options.grouping.enum, ["single", "grouped", "stacked", "stacked100", null]);
  assert.ok(options.points);
  assert.equal("zero_line" in options, false);
  assert.equal("limit" in options, false);
  assert.equal("show_values" in options, false);
  assert.equal("category_label_policy" in options, false);
  assert.equal("sort" in options, false);
  assert.equal("show_latest_value" in options, false);
  assert.equal("bins" in options, false);
  assert.equal("max_segments" in options, false);
  assert.equal("other_threshold" in options, false);
  assert.equal("show_percent" in options, false);
  assert.equal("legend" in display, false);
  assert.equal("view_mode" in display, false);
  assert.equal("labels" in display, false);
  assert.equal("number_format" in display, false);
  assert.deepEqual(tableColumn.format.enum, ["compact", "number", "percent", "currency", null]);
  assert.match(tableColumn.format.description, /Use "percent" only for fractional-rate values/);
  assert.match(tableColumn.format.description, /98.*use "number" with unit "%"/);
  assert.equal("version" in chart, false);
  assert.equal("comparisonContext" in chart, false);
  assert.equal("notes" in properties, false);
  assert.equal("datasets" in properties, false);
  assert.equal("selected_dataset" in properties, false);
  assert.equal("query_binding" in properties, false);
  assert.equal("facet" in chart.fields.properties, false);
  assert.equal("tooltip" in chart.fields.properties, false);
  assert.equal("sort" in chart, false);
  assert.equal("notes" in display, false);
  assert.equal("tooltip" in display, false);
  assert.equal("empty_state" in display, false);
  assert.equal("reference_lines" in display, false);
  assert.match(server.SERVER_INSTRUCTIONS, /chart\.type "bar"/);
  assert.match(server.SERVER_INSTRUCTIONS, /Default every chart title to a neutral, descriptive label/);
  assert.match(server.SERVER_INSTRUCTIONS, /Do not infer a narrative takeaway/);
  assert.match(server.SERVER_INSTRUCTIONS, /Chart subtitles should add a reader-facing insight/);
});

test("visualization guidance defaults chart titles to neutral descriptions", () => {
  const visualize = readFileSync(new URL("../skills/visualize-data/SKILL.md", import.meta.url), "utf8");
  const appCore = readFileSync(new URL("../src/analytics-app-core.md", import.meta.url), "utf8");

  for (const source of [visualize, appCore]) {
    assert.match(source, /neutral, descriptive label/);
    assert.match(source, /Do not infer a narrative takeaway/);
    assert.match(source, /explicitly requests (?:one|a takeaway-led title)/);
  }

  assert.doesNotMatch(visualize, /Standalone static charts may use takeaway-led titles/);
});

test("JavaScript MCP server rejects removed inline snake_case chart names", () => {
  const args = queryTablePayload();
  args.chart.type = "grouped_column";
  assert.throws(
    () => server.callTool("render_chart", args),
    /chart\.type must be one of/,
  );
});

test("JavaScript MCP server strips inline chart notes while table notes remain supported", () => {
  const chartArgs = queryTablePayload();
  chartArgs.notes = ["top-level chart note"];
  chartArgs.chart.version = "legacy";
  chartArgs.chart.comparisonContext = { baseline: "legacy" };
  chartArgs.chart.sort = "legacy";
  chartArgs.chart.options = {
    show_values: true,
    category_label_policy: "wrap",
    show_latest_value: true,
    bins: 12,
    max_segments: 8,
    other_threshold: 0.1,
    show_percent: true,
  };
  chartArgs.chart.fields.facet = { field: "legacy" };
  chartArgs.chart.fields.tooltip = [{ field: "legacy" }];
  chartArgs.display.notes = ["presentation chart note"];
  chartArgs.display.layout = "split";
  chartArgs.display.source_panel = "sidebar";
  chartArgs.display.sql_panel_position = "bottom_right";
  chartArgs.display.table_panel_position = "bottom_left";
  chartArgs.display.legend = { title: "Legacy" };
  chartArgs.display.view_mode = "table";
  chartArgs.display.number_format = "currency";
  chartArgs.display.labels = { values: "all" };
  chartArgs.query_binding = { label: "legacy binding" };
  chartArgs.datasets = [{ id: "legacy dataset input" }];
  chartArgs.selected_dataset = "legacy dataset input";

  const chartPayload = server.callTool("render_chart", chartArgs);
  const tablePayload = server.callTool("render_table", {
    title: "Preview",
    source: chartArgs.source,
    notes: ["table note"],
    columns: [{ key: "segment", label: "Segment", type: "text" }],
    rows: [{ segment: "Enterprise" }],
  });
  const tableSchema =
    server
      .toolDefinitions()
      .find((tool) => tool.name === "render_table")
      .inputSchema.properties;

  assert.equal("notes" in chartPayload, false);
  assert.equal("notes" in (chartPayload.display || {}), false);
  assert.equal("version" in chartPayload.chart, false);
  assert.equal("comparisonContext" in chartPayload.chart, false);
  assert.equal("sort" in chartPayload.chart, false);
  assert.deepEqual(chartPayload.chart.options, undefined);
  assert.equal("facet" in chartPayload.chart.fields, false);
  assert.equal("tooltip" in chartPayload.chart.fields, false);
  assert.equal("layout" in (chartPayload.display || {}), false);
  assert.equal("source_panel" in (chartPayload.display || {}), false);
  assert.equal("sql_panel_position" in (chartPayload.display || {}), false);
  assert.equal("table_panel_position" in (chartPayload.display || {}), false);
  assert.equal("legend" in (chartPayload.display || {}), false);
  assert.equal("view_mode" in (chartPayload.display || {}), false);
  assert.equal("number_format" in (chartPayload.display || {}), false);
  assert.equal("legend" in chartPayload.chart_spec, false);
  assert.equal("labels" in chartPayload.chart_spec, false);
  assert.equal("viewMode" in chartPayload.chart_spec.surface, false);
  assert.equal("view_mode" in chartPayload, false);
  assert.equal("labels" in (chartPayload.display || {}), false);
  assert.equal("datasets" in chartPayload, false);
  assert.equal("selected_dataset" in chartPayload, false);
  assert.equal("query_binding" in chartPayload, false);
  assert.ok("notes" in tableSchema);
  assert.deepEqual(tablePayload.notes, ["table note"]);
});

test("JavaScript MCP server preserves chart-compatible source SQL for table widgets", () => {
  const chartArgs = queryTablePayload();
  const payload = server.callTool("render_table", {
    title: "ARR rows",
    source: chartArgs.source,
    result_table: chartArgs.table,
  });
  const tableSchema =
    server
      .toolDefinitions()
      .find((tool) => tool.name === "render_table")
      .inputSchema.properties;

  assert.equal(payload.widget_type, "table");
  assert.equal(payload.source.query.sql, "SELECT reporting_date, arr_b FROM gtm.example");
  assert.equal("query" in payload.source.query, false);
  assert.equal(payload.source.query.id, "query-123");
  assert.equal(payload.source_query, undefined);
  assert.ok(tableSchema.source);
  assert.ok(tableSchema.source.properties.query.properties.sql);
  assert.ok(tableSchema.source.properties.query.properties.filters);
  assert.ok(tableSchema.source.properties.query.properties.description);
});

test("JavaScript MCP server removes source.query.query from table widget payloads", () => {
  const chartArgs = queryTablePayload();
  chartArgs.source.query.query = "Loads ARR by reporting date for widget tests.";

  const payload = server.callTool("render_table", {
    title: "ARR rows",
    source: chartArgs.source,
    result_table: chartArgs.table,
  });

  assert.equal(payload.widget_type, "table");
  assert.equal(payload.source.query.sql, "SELECT reporting_date, arr_b FROM gtm.example");
  assert.equal("query" in payload.source.query, false);
  assert.equal(payload.result_table.rows.length, 2);
});

test("JavaScript MCP server rejects payloads that only use removed source.query.query", () => {
  const chartArgs = queryTablePayload();
  delete chartArgs.source.query.sql;
  chartArgs.source.query.query = "SELECT reporting_date, arr_b FROM gtm.example";

  assert.throws(
    () => server.callTool("render_table", {
      title: "ARR rows",
      source: chartArgs.source,
      result_table: chartArgs.table,
    }),
    /actual SQL query text/,
  );
});

test("JavaScript MCP server rejects redundant bar chart type aliases", () => {
  assert.throws(() => server.callTool("render_chart", {
    title: "Revenue mix",
    source: sourceQueryForTest(),
    table: {
      columns: [
        { key: "segment", type: "text" },
        { key: "channel", type: "text" },
        { key: "revenue", type: "number" },
      ],
      rows: [
        { segment: "Enterprise", channel: "Direct", revenue: 40 },
        { segment: "Enterprise", channel: "Partner", revenue: 60 },
      ],
    },
    chart: {
      type: "horizontalStackedBar100",
      fields: {
        x: { field: "segment", type: "nominal" },
        y: { field: "revenue", type: "quantitative" },
        color: { field: "channel", type: "nominal" },
      },
    },
  }), /chart\.type must be one of/);
});

test("JavaScript MCP server rejects invalid grouped and percent stacked bar configs", () => {
  const baseArgs = {
    title: "Revenue mix",
    source: sourceQueryForTest(),
    table: {
      columns: [
        { key: "segment", type: "text" },
        { key: "channel", type: "text" },
        { key: "revenue", type: "number" },
      ],
      rows: [{ segment: "Enterprise", channel: "Direct", revenue: 0 }],
    },
    chart: {
      type: "bar",
      options: { grouping: "stacked" },
      fields: {
        x: { field: "segment", type: "nominal" },
        y: { field: "revenue", type: "quantitative" },
      },
    },
  };

  assert.throws(
    () => server.callTool("render_chart", baseArgs),
    /requires chart\.fields\.color\.field/,
  );

  const invalidPercent = structuredClone(baseArgs);
  invalidPercent.chart.options.grouping = "stacked100";
  invalidPercent.chart.fields.color = { field: "channel", type: "nominal" };
  assert.throws(
    () => server.callTool("render_chart", invalidPercent),
    /positive denominator/,
  );
});

test("JavaScript MCP server rejects auto chart setting modes", () => {
  const args = queryTablePayload();

  args.chart.options = { points: "auto" };
  assert.throws(
    () => server.callTool("render_chart", args),
    /chart\.options\.points must be one of always, never/,
  );
});

test("JavaScript MCP server warns on dense compact bars and pies", () => {
  const rows = Array.from({ length: 25 }, (_, index) => ({ category: `C${index}`, value: index + 1 }));
  const columns = [{ key: "category", type: "text" }, { key: "value", type: "number" }];
  const barPayload = server.callTool("render_chart", {
    title: "Dense categories",
    source: sourceQueryForTest(),
    table: { columns, rows },
    chart: {
      type: "bar",
      fields: { x: { field: "category" }, y: { field: "value" } },
    },
  });
  const piePayload = server.callTool("render_chart", {
    title: "Dense slices",
    source: sourceQueryForTest(),
    table: { columns, rows: rows.slice(0, 9) },
    chart: {
      type: "pie",
      fields: { x: { field: "category" }, y: { field: "value" } },
    },
  });

  assert.match(barPayload.quality_warnings.join(" "), /Compact bar chart has 25 categories/);
  assert.match(piePayload.quality_warnings.join(" "), /Compact pie chart has 9 slices/);
});

test("JavaScript MCP server returns typed resource errors", async () => {
  const response = await server.handleRpc({
    jsonrpc: "2.0",
    id: 1,
    method: "resources/read",
    params: { uri: "ui://widget/missing.html" },
  });

  assert.equal(response.error.code, -32602);
  assert.match(response.error.message, /unknown Data Analytics widget resource/);
});

test("JavaScript MCP server rejects malformed widget resource aliases", async () => {
  for (const uri of [
    "ui://widget/datascience-chart-999.0.0.html",
    "ui://widget/datascience-chart.html?v=999.0.0",
    "ui://widget/datascience-chart-0.2.8-alpha.1.html",
    `ui://widget/datascience-chart-${server.SERVER_VERSION}+future.html`,
    "ui://widget/datascience-chart-latest.html",
    "ui://widget/datascience-chart.html?v=0.2.6&variant=old",
    server.TABLE_WIDGET_URI.replace(".html", "-old.html"),
    "ui://widget/datascience-artifact-latest.html",
    "ui://widget/datascience-artifact-999.0.0.html",
    "ui://widget/datascience-artifact.html?v=999.0.0",
    "ui://widget/datascience-artifact-0.2.7-rc.01.html",
    `ui://widget/datascience-artifact-${server.SERVER_VERSION}+future.html`,
    "ui://widget/datascience-artifact-0.2.6%2Fpreview.html",
    "ui://widget/datascience-artifact.html?v=latest",
  ]) {
    const response = await server.handleRpc({
      jsonrpc: "2.0",
      id: 1,
      method: "resources/read",
      params: { uri },
    });

    assert.equal(response.error.code, -32602);
    assert.match(response.error.message, /unknown Data Analytics widget resource/);
  }
});

test("artifact share menu labels Sites publishing clearly", () => {
  const app = readFileSync(new URL("../src/analytics-app/App.tsx", import.meta.url), "utf8");
  assert.match(app, /site: "Publish to Sites"/);
  assert.doesNotMatch(app, /Publish hosted link/);
});

test("local artifact fallback stays neutral and excludes the regression showcase", () => {
  const widget = readFileSync(new URL("../src/datascience-artifact-widget.jsx", import.meta.url), "utf8");
  const fallback = widget.split("const fallbackPayload =", 2)[1].split("function createMemoryStorage", 1)[0];
  assert.match(fallback, /ok: false/);
  assert.match(fallback, /widget_type: "artifact"/);
  assert.match(fallback, /status: "blocked"/);
  assert.doesNotMatch(fallback, /Local regression showcase/);
  assert.doesNotMatch(fallback, /Synthetic weekly revenue fixture/);
});

test("artifact charts request the versioned chart widget resource", () => {
  const widget = readFileSync(new URL("../src/datascience-artifact-widget.jsx", import.meta.url), "utf8");
  assert.match(widget, /import pluginManifest from "\.\.\/\.codex-plugin\/plugin\.json"/);
  assert.match(
    widget,
    /`ui:\/\/widget\/datascience-chart-\$\{encodeURIComponent\(pluginManifest\.version\)\}\.html`/,
  );
  assert.doesNotMatch(widget, /CHART_WIDGET_RESOURCE_URI = "ui:\/\/widget\/datascience-chart\.html"/);
});

test("artifact charts wire clickable legend state into the renderer", () => {
  const app = readFileSync(new URL("../src/analytics-app/App.tsx", import.meta.url), "utf8");
  assert.match(app, /const \[visibleSeries, setVisibleSeries\] = useState\(\)/);
  assert.match(app, /onVisibleSeriesChange=\{setVisibleSeries\}/);
  assert.match(app, /visibleSeries=\{visibleSeries\}/);
});

test("JavaScript MCP server rejects unsafe widget fields", () => {
  const args = queryTablePayload();
  args.table.columns.push({ key: "customer_email", label: "Email" });
  args.table.rows[0].customer_email = "person@example.com";

  assert.throws(
    () => server.callTool("render_chart", args),
    /looks unsafe/,
  );
});

test("JavaScript MCP server allows reviewed customer dimensions in widgets", () => {
  const args = queryTablePayload();
  args.table.contains_sensitive_data = true;
  args.table.columns.push({ key: "customer_name", label: "Customer" });
  args.table.rows[0].customer_name = "Acme Corp";

  const payload = server.callTool("render_chart", args);

  assert.equal(payload.widget_type, "chart");
  assert.equal(payload.table.rows[0].customer_name, "Acme Corp");
});
