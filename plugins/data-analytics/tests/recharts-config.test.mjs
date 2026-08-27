import assert from "node:assert/strict";
import test from "node:test";

import {
  CANONICAL_CHART_TYPES,
  buildCategoryRows,
  canonicalVisualizationType,
  emptyChartMessage,
  formatValue,
  histogramBins,
  isCanonicalChartType,
  isDateLikeValue,
  pieRows,
  rechartsLegendNames,
  colorAt,
  resolveCssColor,
} from "../src/recharts-config.js";

test("canonical chart types expose the shared Recharts superset", () => {
  assert.deepEqual(CANONICAL_CHART_TYPES, [
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
  ]);
  assert.equal(canonicalVisualizationType("bar"), "bar");
  assert.equal(canonicalVisualizationType("stackedArea"), "stackedArea");
  assert.equal(isCanonicalChartType("grouped_column"), false);
  assert.equal(isCanonicalChartType("stacked_area"), false);
  assert.equal(canonicalVisualizationType("grouped_column"), "bar");
  assert.equal(canonicalVisualizationType("stacked_area"), "bar");
});

test("pivots long chart rows into Recharts category rows", () => {
  assert.deepEqual(
    buildCategoryRows([
      { x: "2026-01-01", y: 10, series: "A" },
      { x: "2026-01-02", y: 20, series: "A" },
      { x: "2026-01-01", y: 4, series: "B" },
    ]),
    [
      { x: "2026-01-01", A: 10, B: 4 },
      { x: "2026-01-02", A: 20, B: null },
    ],
  );
});

test("builds histogram bins and pie rows from shared data helpers", () => {
  const rows = [1, 1, 2, 3, 5, 8, 13].map((value) => ({ x: value, y: value, series: "Value" }));
  const bins = histogramBins(rows);

  assert.ok(bins.length >= 5);
  assert.equal(bins.reduce((sum, bin) => sum + bin.count, 0), 7);
  assert.deepEqual(
    pieRows([
      { x: "ignored", y: 10, series: "A" },
      { x: "ignored", y: 20, series: "B" },
      { x: "ignored", y: -5, series: "C" },
    ]),
    [
      { name: "A", value: 10 },
      { name: "B", value: 20 },
    ],
  );
});

test("formats large chart values compactly with currency-like units", () => {
  assert.equal(formatValue(400000000, "USD"), "$400M");
  assert.equal(formatValue(725.4, "USD millions"), "$725.4M");
  assert.equal(formatValue(182300), "182.3K");
});

test("formats word percent units as semantic rates", () => {
  assert.equal(formatValue(0.6, "percent"), "60%");
  assert.equal(formatValue(0.625, "percentage"), "62.5%");
  assert.equal(formatValue(60, "%"), "60%");
});

test("uses semantic chart-token categorical fallbacks", () => {
  assert.equal(colorAt([], 0), "var(--ds-chart-stack-1, #003f7a)");
  assert.equal(colorAt([], 1), "var(--ds-chart-stack-2, #0169cc)");
});

test("reports chart-specific empty states", () => {
  assert.equal(emptyChartMessage([], "line"), "No chart data to render.");
  assert.equal(emptyChartMessage([{ x: "a", y: 1, series: "A" }], "scatter"), "Scatter plots need numeric x and y values.");
  assert.equal(emptyChartMessage([{ x: "a", y: 1, series: "A" }], "heatmap"), "Heatmaps need a grouping field with at least two series.");
  assert.equal(emptyChartMessage([{ x: "a", y: -1, series: "A" }], "pie"), "Pie charts need positive values.");
  assert.equal(
    emptyChartMessage(
      [
        { x: "A", y: 4, series: "Alpha" },
        { x: "B", y: 6, series: "Beta" },
      ],
      "funnel",
    ),
    "Funnel charts need a single series.",
  );
  assert.equal(
    emptyChartMessage(
      [
        { x: "A", y: 4, series: "Alpha" },
        { x: "B", y: 6, series: "Beta" },
      ],
      "waterfall",
    ),
    "Waterfall charts need a single series.",
  );
  assert.deepEqual(rechartsLegendNames([{ x: "a", y: 1, series: "A" }], "histogram"), []);
  assert.deepEqual(
    rechartsLegendNames(
      [
        { x: 1, y: 2, series: "Activation" },
        { x: 2, y: 3, series: "Retention" },
      ],
      "scatter",
    ),
    ["Activation", "Retention"],
  );
});

test("keeps date detection strict and CSS variable resolution browser-compatible", () => {
  assert.equal(isDateLikeValue("2026-01-01"), true);
  assert.equal(isDateLikeValue(42), false);
  assert.equal(isDateLikeValue("not a date"), false);

  const root = {};
  globalThis.getComputedStyle = () => ({
    getPropertyValue: (name) => (name === "--ds-chart-series-blue" ? "#abc123" : ""),
  });

  assert.equal(resolveCssColor("var(--ds-chart-series-blue)", root), "#abc123");
  assert.equal(resolveCssColor("var(--missing, #fff)", root), "#fff");
  assert.equal(resolveCssColor("#000", root), "#000");
});
