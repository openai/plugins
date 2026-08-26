import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { test } from "node:test";

const here = dirname(fileURLToPath(import.meta.url));
const pluginRoot = resolve(here, "..");
const builderPath = resolve(
  pluginRoot,
  "skills/build-report/scripts/build_portable_artifact.mjs",
);
const slidesHelper = resolve(
  pluginRoot,
  "skills/build-report/report-to-google-slides/scripts/report_to_google_slides.py",
);

function chartSvg(primary, secondary) {
  return `<svg class="portable-static-chart-svg" aria-hidden="true" focusable="false" viewBox="0 0 640 360" width="640" height="360"><line x1="64" y1="300" x2="600" y2="300" stroke="${secondary}"/><rect x="120" y="120" width="120" height="180" fill="${primary}"/><rect x="320" y="80" width="120" height="220" fill="${secondary}"/><path d="M80 260 L220 190 L380 140 L560 90" fill="none" stroke="${primary}"/></svg>`;
}

function artifactInput() {
  return {
    surface: "report",
    manifest: {
      version: 1,
      surface: "report",
      title: "Portable conversion fixture",
      description: "Verifies portable semantic fallback conversion.",
      generatedAt: "2026-07-07T20:00:00Z",
      cards: [
        {
          id: "revenue",
          description: "Current revenue.",
          dataset: "summary",
          sourceId: "revenue_sql",
          metrics: [{ label: "Revenue", field: "revenue", format: "currency" }],
        },
        {
          id: "margin",
          dataset: "summary",
          sourceId: "revenue_sql",
          metrics: [{ label: "Gross margin", field: "margin", format: "percent" }],
        },
        {
          id: "retention",
          description: "Retention for strategic enterprise accounts.",
          dataset: "summary",
          sourceId: "revenue_sql",
          metrics: [
            {
              label: "Net revenue retention across strategic enterprise accounts",
              field: "retention",
              format: "percent",
            },
          ],
        },
      ],
      charts: [
        {
          id: "quarterly_revenue",
          title: "Revenue is accelerating",
          subtitle: "Actual revenue remains ahead of plan.",
          headerMarkdown: "Revenue is **accelerating**",
          type: "bar",
          dataset: "quarterly",
          sourceId: "revenue_sql",
          encodings: {
            x: { field: "quarter", type: "ordinal", label: "Quarter" },
            y: {
              field: "revenue",
              type: "quantitative",
              label: "Revenue",
              format: "currency",
            },
            color: { field: "series", type: "nominal", label: "Series" },
          },
        },
      ],
      tables: [
        {
          id: "segment_detail",
          title: "Segment performance",
          headerMarkdown: "Segment **performance**",
          dataset: "segments",
          sourceId: "revenue_sql",
          columns: [
            { field: "segment", label: "Segment", type: "text" },
            { field: "revenue", label: "Revenue", format: "currency" },
          ],
        },
      ],
      sources: [
        { id: "revenue_sql", label: "Revenue warehouse query", path: "queries/revenue.sql" },
      ],
      blocks: [
        {
          id: "title",
          type: "markdown",
          body: "# Portable conversion fixture",
        },
        {
          id: "headline",
          type: "markdown",
          body: "## Executive summary\n\nRevenue remains ahead of plan.",
        },
        {
          id: "metrics",
          type: "metric-strip",
          cardIds: ["revenue", "margin", "retention"],
        },
        { id: "chart", type: "chart", chartId: "quarterly_revenue" },
        { id: "detail", type: "table", tableId: "segment_detail" },
        {
          id: "conclusions",
          type: "markdown",
          sourceId: "revenue_sql",
          body:
            "## Conclusions\n\nConversion-adjusted pipeline reached **$6.73M** and delivered a 12.8% lift.",
        },
      ],
    },
    snapshot: {
      version: 1,
      generatedAt: "2026-07-07T20:00:00Z",
      status: "ready",
      datasets: {
        summary: [{ revenue: 7420000, margin: 0.713, retention: 1.126 }],
        quarterly: [
          { quarter: "Q1", series: "Actual", revenue: 5800000 },
          { quarter: "Q1", series: "Plan", revenue: 5600000 },
          { quarter: "Q2", series: "Actual", revenue: 6400000 },
          { quarter: "Q2", series: "Plan", revenue: 6100000 },
        ],
        segments: Array.from({ length: 16 }, (_, index) => ({
          segment: index === 0 ? "Enterprise" : `Segment ${index + 1}`,
          revenue: 4100000 - index * 100000,
        })),
      },
    },
    sources: [
      {
        id: "revenue_sql",
        label: "Revenue warehouse query",
        path: "queries/revenue.sql",
        query: {
          engine: "trino",
          sql: "SELECT quarter, series, segment, revenue FROM analytics.reader_qa",
          description: "Reviewed revenue evidence for conversion QA.",
          executed_at: "2026-07-07T19:58:00Z",
        },
      },
    ],
    package_info: {},
  };
}

const pythonDeps = spawnSync(
  "python3",
  ["-c", "import bs4, PIL, pptx"],
  { encoding: "utf8" },
);

test(
  "Google Slides conversion preserves portable metrics, chart evidence, and provenance",
  { skip: pythonDeps.status === 0 ? false : "optional conversion dependencies unavailable" },
  () => {
    const work = mkdtempSync(join(tmpdir(), "portable-slides-conversion-"));
    const input = join(work, "artifact.json");
    const html = join(work, "report.html");
    const output = join(work, "slides");
    writeFileSync(input, JSON.stringify(artifactInput()), "utf8");

    execFileSync(process.execPath, [builderPath, "--input", input, "--output", html]);
    const original = readFileSync(html, "utf8");
    assert.equal(original.match(/<h1>Portable conversion fixture<\/h1>/g)?.length, 1);
    assert.doesNotMatch(original, /data-artifact-block-id="title"/);
    const lightChart = `<div class="portable-static-chart-variant portable-static-chart-light" aria-hidden="true">${chartSvg("#1473e6", "#6f6e69")}</div>`;
    const darkChart = `<div class="portable-static-chart-variant portable-static-chart-dark" aria-hidden="true">${chartSvg("#66a8ff", "#aaa9a4")}</div>`;
    const withStaticCharts = original.replace(
      /(<figure class="portable-content-card portable-chart-summary"[^>]*>)/,
      `$1<div class="portable-static-chart" role="img" aria-label="Revenue trend chart">${lightChart}${darkChart}</div>`,
    );
    assert.notEqual(withStaticCharts, original);
    const withNestedLegacyTooltip = withStaticCharts.replace(
      'class="portable-source-tooltip-content"',
      'class="portable-inline-source-content portable-source-tooltip-content"',
    );
    assert.notEqual(withNestedLegacyTooltip, withStaticCharts);
    writeFileSync(html, withNestedLegacyTooltip, "utf8");
    execFileSync("python3", [slidesHelper, html, "--out-dir", output]);

    const manifest = JSON.parse(readFileSync(join(output, "manifest.json"), "utf8"));
    const plan = JSON.parse(readFileSync(join(output, "deck_plan.json"), "utf8"));
    const preflight = JSON.parse(
      readFileSync(join(output, "preflight_checks.json"), "utf8"),
    );

    assert.equal(preflight.status, "passed");
    assert.equal(manifest.title, "Portable conversion fixture");
    assert.equal(manifest.sections["Portable conversion fixture"], undefined);
    assert.equal(manifest.counts.metrics, 3);
    assert.equal(manifest.counts.charts, 1);
    assert.equal(manifest.counts.tables, 1);
    assert.equal(manifest.charts[0].source_kind, "portable_data_table");
    assert.equal(manifest.charts[0].title, "Revenue is accelerating");
    assert.equal(manifest.charts[0].data_table.rows.length, 4);
    assert.match(manifest.charts[0].source, /Revenue warehouse query/);
    assert.match(manifest.charts[0].source_query, /analytics\.reader_qa/);
    assert.ok(manifest.metrics.every((metric) => metric.portable && metric.source));
    assert.deepEqual(
      manifest.metrics.map(({ value }) => value),
      ["$7.42M", "71.3%", "112.6%"],
    );
    assert.equal(manifest.metrics[1].note, "");
    assert.ok(
      manifest.metrics.every(({ source_query }) =>
        source_query.includes("FROM analytics.reader_qa")
      ),
    );
    assert.equal(manifest.tables[0].title, "Segment performance");
    assert.equal(manifest.tables[0].rows.length, 15);
    assert.deepEqual(manifest.tables[0].rows[0], ["Enterprise", "$4.1M"]);
    assert.match(manifest.tables[0].note, /16 results · Showing first 15/);
    assert.match(manifest.tables[0].source, /Revenue warehouse query/);
    assert.match(manifest.tables[0].source_query, /analytics\.reader_qa/);
    assert.doesNotMatch(
      JSON.stringify({
        metrics: manifest.metrics.map(({ label, value, note }) => ({ label, value, note })),
        table: {
          headers: manifest.tables[0].headers,
          rows: manifest.tables[0].rows,
        },
      }),
      /Source for|Revenue warehouse query|analytics\.reader_qa/,
    );
    assert.equal(
      manifest.metrics[2].label,
      "Net revenue retention across strategic enterprise accounts",
    );
    assert.deepEqual(
      manifest.sections.Conclusions.paragraphs,
      ["Conversion-adjusted pipeline reached $6.73M and delivered a 12.8% lift."],
    );
    const sourcedNarrative = JSON.stringify(manifest.sections.Conclusions);
    assert.equal(sourcedNarrative.match(/\$6\.73M/g)?.length, 1);
    assert.equal(sourcedNarrative.match(/12\.8%/g)?.length, 1);
    assert.doesNotMatch(
      sourcedNarrative,
      /Source for|Revenue warehouse query|analytics\.reader_qa/,
    );

    const chartSlide = plan.find((slide) => slide.kind === "chart_evidence");
    assert.ok(chartSlide);
    assert.equal(chartSlide.source_kind, "portable_data_table");
    assert.match(chartSlide.source, /Table: analytics\.reader_qa/);
    assert.equal(plan.filter((slide) => slide.kind === "table").length, 1);
    const executiveSlide = plan.find((slide) => slide.kind === "executive_summary");
    assert.deepEqual(
      executiveSlide.elements.filter((element) => element.startsWith("metric-card-")),
      ["metric-card-1", "metric-card-2", "metric-card-3"],
    );
    const conclusionsSlide = plan.find(
      (slide) => slide.kind === "conclusions_implications",
    );
    assert.ok(conclusionsSlide);
    assert.deepEqual(conclusionsSlide.source_paragraphs.conclusions, [
      "Conversion-adjusted pipeline reached $6.73M and delivered a 12.8% lift.",
    ]);

    for (const checkName of [
      "source:portable_chart_summaries",
      "coverage:portable_chart_provenance",
      "coverage:portable_metric_provenance",
    ]) {
      const check = preflight.checks.find(({ name }) => name === checkName);
      assert.equal(check?.status, "passed", checkName);
    }

    const longLabelCheck = preflight.checks.find(
      ({ name }) => name === "text_fit:summary-metric-label-3",
    );
    const longNoteCheck = preflight.checks.find(
      ({ name }) => name === "text_fit:summary-metric-note-3",
    );
    assert.equal(longLabelCheck?.status, "passed");
    assert.ok(longLabelCheck.details.box[2] >= 3.9, "odd KPI card should span the metric pane");
    assert.ok(longLabelCheck.details.font_size_pt >= 8, "long KPI label should remain readable");
    assert.equal(longNoteCheck?.status, "passed");
    assert.ok(longNoteCheck.details.font_size_pt >= 8, "long KPI note should remain readable");

    const deck = join(output, "deck.pptx");
    execFileSync("python3", ["-m", "zipfile", "-t", deck]);
    const slideXml = execFileSync(
      "python3",
      [
        "-c",
        "import sys,zipfile; z=zipfile.ZipFile(sys.argv[1]); print(' '.join(z.read(n).decode('utf-8') for n in z.namelist() if n.startswith('ppt/slides/slide') and n.endswith('.xml')))",
        deck,
      ],
      { encoding: "utf8", maxBuffer: 8 * 1024 * 1024 },
    );
    assert.match(slideXml, /Revenue warehouse query/);
    assert.equal(slideXml.match(/\$6\.73M/g)?.length, 1);
    assert.equal(slideXml.match(/12\.8%/g)?.length, 1);
    assert.doesNotMatch(slideXml, /Source for \$6\.73M/);
    assert.doesNotMatch(slideXml, /Source: Source:/);
  },
);
