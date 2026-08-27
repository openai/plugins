import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

test("tooltip percent encodings inherit chart percent semantics for literal percent units", async () => {
  const source = await readFile(new URL("../src/analytics-app/charting/ChartTooltip.tsx", import.meta.url), "utf8");

  assert.match(source, /function tooltipEncodingValueFormat\(chart: ChartSpec, encoding: ChartEncodingSpec\): ValueFormat/);
  assert.match(source, /chart\.valueFormat === "percent" && isPercentSymbolUnit\(encoding\.unit\)/);
  assert.match(source, /formatValue\(item\.value, valueFormat, encoding\.unit\)/);
});

test("chart and heatmap data tooltips reveal immediately without clipping", async () => {
  const styles = await readFile(new URL("../src/analytics-app/charting/chart-tokens.css", import.meta.url), "utf8");
  const appStyles = await readFile(new URL("../src/analytics-app/styles.css", import.meta.url), "utf8");
  const renderer = await readFile(new URL("../src/analytics-app/charting/ChartRenderer.tsx", import.meta.url), "utf8");

  assert.match(styles, /@keyframes chart-tooltip-reveal/);
  assert.match(styles, /\.recharts-tooltip-wrapper \.chart-tooltip \{[\s\S]*animation: chart-tooltip-reveal 80ms ease both;/);
  assert.doesNotMatch(styles, /\.recharts-tooltip-wrapper \.chart-tooltip \{[^}]*300ms/);
  assert.match(styles, /\.chart-frame--heatmap \{[^}]*overflow: hidden;/);
  assert.match(styles, /\.chart-frame--heatmap > \.chart-plot \{[^}]*overflow: hidden;/);
  assert.match(styles, /\.heatmap-grid-panel \{[^}]*overflow: auto;/);
  assert.match(styles, /\.chart-tooltip\.heatmap-tooltip \{[^}]*position: fixed;/);
  assert.doesNotMatch(styles, /\.heatmap-cell:hover \.heatmap-tooltip/);
  assert.doesNotMatch(appStyles, /\.chart-frame--custom\.chart-frame--heatmap/);
  assert.match(renderer, /createPortal\(/);
  assert.match(renderer, /calculateViewportTooltipPosition\(/);
  assert.match(renderer, /aria-label=\{label\}/);
  assert.doesNotMatch(renderer, /aria-describedby=\{activeTooltip/);
  assert.match(renderer, /role="tooltip"/);
});
