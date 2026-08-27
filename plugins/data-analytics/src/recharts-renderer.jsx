import React from "react";
import { createRoot } from "react-dom/client";

import { ChartRenderer } from "./analytics-app/charting/ChartRenderer";
import "./analytics-app/charting/chart-tokens.css";
import { asArray, number, text } from "./recharts-config.js";

const DEFAULT_COMPACT_HEIGHT = 280;
const DEFAULT_EXPLORER_HEIGHT = 520;
const DEFAULT_CHART_WIDTH = 760;
const MIN_CHART_WIDTH = 280;
const MIN_COMPACT_CHART_HEIGHT = 280;
const MIN_EXPLORER_CHART_HEIGHT = 320;

function formatBinValue(value) {
  return new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 }).format(value);
}

function buildHistogramRows(data) {
  const values = asArray(data)
    .map((point) => number(point && (point.y != null ? point.y : point.x)))
    .filter((value) => value != null);
  if (!values.length) return [];
  const min = Math.min(...values);
  const max = Math.max(...values);
  const binCount = Math.max(1, Math.min(12, Math.max(5, Math.ceil(Math.sqrt(values.length)))));
  const binWidth = (max - min || 1) / binCount;
  const rows = Array.from({ length: binCount }, (_, index) => {
    const start = min + index * binWidth;
    const end = min + (index + 1) * binWidth;
    return {
      count: 0,
      x: `${formatBinValue(start)}-${formatBinValue(end)}`,
    };
  });
  for (const value of values) {
    const index = Math.min(binCount - 1, Math.max(0, Math.floor((value - min) / binWidth)));
    rows[index].count += 1;
  }
  return rows;
}

function quantile(sortedValues, percentile) {
  if (!sortedValues.length) return 0;
  const index = (sortedValues.length - 1) * percentile;
  const lower = Math.floor(index);
  const upper = Math.ceil(index);
  if (lower === upper) return sortedValues[lower] ?? 0;
  const weight = index - lower;
  return (sortedValues[lower] ?? 0) * (1 - weight) + (sortedValues[upper] ?? 0) * weight;
}

function buildBoxPlotRows(data) {
  const grouped = new Map();
  for (const point of asArray(data)) {
    const value = number(point && point.y);
    if (value == null) continue;
    const key = text(point && point.x);
    if (!grouped.has(key)) grouped.set(key, []);
    grouped.get(key).push(value);
  }
  return [...grouped.entries()].map(([x, values]) => {
    const sorted = [...values].sort((a, b) => a - b);
    return {
      x,
      min: sorted[0] ?? 0,
      q1: quantile(sorted, 0.25),
      median: quantile(sorted, 0.5),
      q3: quantile(sorted, 0.75),
      max: sorted[sorted.length - 1] ?? 0,
    };
  });
}

function resultRows(dataset) {
  const table = dataset?.table && typeof dataset.table === "object"
    ? dataset.table
    : dataset?.result_table && typeof dataset.result_table === "object"
      ? dataset.result_table
      : null;
  if (Array.isArray(table?.rows)) return table.rows;
  return asArray(dataset?.data);
}

function rowsForType(dataset, type) {
  const rows = resultRows(dataset);
  if (type === "histogram") return buildHistogramRows(rows);
  if (type === "boxPlot") return buildBoxPlotRows(rows);
  return rows;
}

function chartSettingsForDataset(dataset, existing, overrides = {}) {
  const visualizationSettings = dataset?.visualization_spec?.settings;
  const source =
    existing?.settings && typeof existing.settings === "object"
      ? existing.settings
      : visualizationSettings && typeof visualizationSettings === "object"
        ? visualizationSettings
        : {};
  const merged = {
    ...source,
    ...(overrides && typeof overrides === "object" ? overrides : {}),
  };
  return {
    ...merged,
    groupMode: merged.groupMode ?? merged.group_mode,
    orientation: merged.orientation,
    showPoints: merged.showPoints ?? merged.show_points,
  };
}

function isPercentWordUnit(unit) {
  const normalized = text(unit).toLowerCase();
  return normalized === "percent" || normalized === "percentage";
}

function chartSpecForDataset(dataset, type, options) {
  const existing = dataset.chart_spec && typeof dataset.chart_spec === "object" ? dataset.chart_spec : {};
  const { series: _legacySeries, xField: _legacyXField, ...encodedExisting } = existing;
  const rawUnit = options.unit || existing.unit || "";
  const percentWordUnit = isPercentWordUnit(rawUnit);
  const unit = percentWordUnit ? "" : rawUnit;
  const settings = chartSettingsForDataset(dataset, existing, options.settings);
  const existingEncodings = existing.encodings && typeof existing.encodings === "object" && !Array.isArray(existing.encodings) ? existing.encodings : {};
  const hasScatterSize = type === "scatter" && asArray(dataset.data).some((point) => number(point && point.size) != null);
  const encodings = {
    ...existingEncodings,
    ...(hasScatterSize && !existingEncodings.size ? { size: { field: "size", label: "Size", type: "quantitative" } } : {}),
  };
  const referenceLines = Array.isArray(existing.referenceLines) ? [...existing.referenceLines] : [];
  const baseline = number(options.baseline);
  if (baseline != null && !referenceLines.some((line) => number(line && line.value) === baseline)) {
    referenceLines.push({
      axis:
        type === "horizontalBar" ||
        type === "horizontalStackedBar" ||
        type === "horizontalStackedBar100" ||
        (type === "bar" && settings.orientation === "horizontal")
          ? "x"
          : "y",
      value: baseline,
    });
  }
  return {
    ...encodedExisting,
    dataset: existing.dataset || dataset.id || "inline",
    id: existing.id || dataset.id || "inline-chart",
    referenceLines,
    settings,
    surface: {
      ...(existing.surface || {}),
      interactiveLegend: Boolean(options.onVisibleSeriesChange),
      surface: options.surface || "compact",
    },
    title: existing.title || dataset.title || options.title || "Data Analytics chart",
    type,
    unit,
    valueFormat: existing.valueFormat || (percentWordUnit ? "percent" : unit === "$" ? "currency" : "compact"),
    encodings:
      type === "histogram"
        ? {
            x: { field: "x", label: existing.xAxisTitle || "Bucket", type: "ordinal" },
            y: { field: "count", label: "Count", type: "quantitative" },
          }
        : type === "boxPlot"
          ? {
              x: { field: "x", label: existing.xAxisTitle || "Category", type: "ordinal" },
              y: { fields: ["min", "q1", "median", "q3", "max"], label: existing.yAxisTitle || "Distribution", type: "quantitative" },
            }
          : encodings,
  };
}

function positiveNumber(value) {
  if (typeof value === "number" && Number.isFinite(value) && value > 0) return value;
  if (typeof value === "string") {
    const parsed = Number(value);
    if (Number.isFinite(parsed) && parsed > 0) return parsed;
  }
  return null;
}

function measuredRect(element) {
  if (!element || typeof element.getBoundingClientRect !== "function") {
    return { height: 0, width: 0 };
  }
  const rect = element.getBoundingClientRect();
  return {
    height: Number.isFinite(rect.height) ? rect.height : 0,
    width: Number.isFinite(rect.width) ? rect.width : 0,
  };
}

function chartDimensionsForMount(mount, options = {}) {
  const surface = options.surface === "explorer" ? "explorer" : "compact";
  const mountRect = measuredRect(mount);
  const containerRect = measuredRect(mount && mount.parentElement);
  const shellRect = measuredRect(mount && mount.parentElement && mount.parentElement.parentElement);
  const width = Math.max(
    MIN_CHART_WIDTH,
    Math.floor(positiveNumber(options.width) || mountRect.width || containerRect.width || shellRect.width || DEFAULT_CHART_WIDTH),
  );
  const fallbackHeight = surface === "explorer" ? DEFAULT_EXPLORER_HEIGHT : DEFAULT_COMPACT_HEIGHT;
  const minHeight = surface === "explorer" ? MIN_EXPLORER_CHART_HEIGHT : MIN_COMPACT_CHART_HEIGHT;
  const measuredHeight = surface === "explorer" ? mountRect.height || containerRect.height || shellRect.height : 0;
  const height = Math.max(
    minHeight,
    Math.floor(positiveNumber(options.height) || measuredHeight || fallbackHeight),
  );
  return { height, width };
}

function MeasuredChartRenderer({
  chart,
  dataset,
  mount,
  options,
  type,
}) {
  const [dimensions, setDimensions] = React.useState(() => chartDimensionsForMount(mount, options));

  React.useLayoutEffect(() => {
    let frame = 0;
    const update = () => {
      window.cancelAnimationFrame(frame);
      frame = window.requestAnimationFrame(() => {
        setDimensions((current) => {
          const next = chartDimensionsForMount(mount, options);
          return current.width === next.width && current.height === next.height ? current : next;
        });
      });
    };

    update();
    const observer = typeof ResizeObserver === "function" ? new ResizeObserver(update) : null;
    if (observer) {
      observer.observe(mount);
      if (mount.parentElement) observer.observe(mount.parentElement);
      if (mount.parentElement && mount.parentElement.parentElement) {
        observer.observe(mount.parentElement.parentElement);
      }
    }
    window.addEventListener("resize", update);
    if (document.fonts && typeof document.fonts.ready?.then === "function") {
      document.fonts.ready.then(update).catch(() => {});
    }
    return () => {
      window.cancelAnimationFrame(frame);
      observer?.disconnect();
      window.removeEventListener("resize", update);
    };
  }, [mount, options.height, options.surface, options.width]);

  return (
    <ChartRenderer
      chart={chart}
      height={dimensions.height}
      onVisibleSeriesChange={options.onVisibleSeriesChange}
      responsive={false}
      rows={rowsForType(dataset, type)}
      showLegend={true}
      surface={options.surface === "explorer" ? "explorer" : "compact"}
      visibleSeries={options.visibleSeries}
      width={dimensions.width}
    />
  );
}

export function destroyRechartsChart(container) {
  if (!container) return;
  if (container.__datascienceRechartsRoot) {
    container.__datascienceRechartsRoot.unmount();
    container.__datascienceRechartsRoot = null;
  }
  // Uploaded or serialized HTML can contain a prior live mount without its
  // in-memory React root. Clear it before remounting so boot stays idempotent.
  container.replaceChildren();
}

export function renderRechartsChart(container, dataset, type, options = {}) {
  destroyRechartsChart(container);
  const mount = document.createElement("div");
  mount.className = "chart-canvas-wrap recharts-chart-wrap";
  mount.setAttribute("role", "img");
  mount.setAttribute("aria-label", text(dataset.title || options.title || "Data Analytics chart"));
  container.appendChild(mount);
  const root = createRoot(mount);
  const chart = chartSpecForDataset(dataset, type, options);
  container.__datascienceRechartsRoot = root;
  root.render(
    <MeasuredChartRenderer
      chart={chart}
      dataset={dataset}
      mount={mount}
      options={options}
      type={type}
    />,
  );
}
