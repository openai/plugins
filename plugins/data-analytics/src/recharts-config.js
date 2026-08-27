export const CANONICAL_CHART_TYPES = [
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

export const chartPickerSections = [
  {
    title: "Trends",
    options: [
      { type: "line", label: "Line", preview: "line" },
      { type: "area", label: "Area", preview: "area" },
      { type: "stackedArea", label: "Stacked area", preview: "stacked-area" },
      { type: "sparkline", label: "Sparkline", preview: "sparkline" },
    ],
  },
  {
    title: "Comparison",
    options: [
      { type: "bar", label: "Bar", preview: "bar" },
      { type: "leaderboard", label: "Leaderboard", preview: "leaderboard" },
    ],
  },
  {
    title: "Distribution",
    options: [
      { type: "histogram", label: "Histogram", preview: "histogram" },
      { type: "boxPlot", label: "Box plot", preview: "box-plot" },
    ],
  },
  {
    title: "Relationships",
    options: [
      { type: "scatter", label: "Scatter", preview: "scatter" },
      { type: "heatmap", label: "Heatmap", preview: "heatmap" },
    ],
  },
  {
    title: "Composition",
    options: [
      { type: "pie", label: "Pie", preview: "pie" },
    ],
  },
  {
    title: "Progression",
    options: [
      { type: "funnel", label: "Funnel", preview: "funnel" },
      { type: "waterfall", label: "Waterfall", preview: "waterfall" },
    ],
  },
];

const DEFAULT_COLORS = [
  "var(--ds-chart-stack-1, #003f7a)",
  "var(--ds-chart-stack-2, #0169cc)",
  "var(--ds-chart-stack-3, #8046d9)",
  "var(--ds-chart-stack-4, #339cff)",
  "var(--ds-chart-stack-5, #ad7bf9)",
  "var(--ds-chart-series-green, #00692a)",
  "var(--ds-chart-series-orange, #923b0f)",
  "var(--ds-chart-series-neutral, #8f8f8f)",
];
const COMPACT_VALUE_THRESHOLD = 100_000;

export function asArray(value) {
  return Array.isArray(value) ? value : [];
}

export function text(value) {
  return value == null ? "" : String(value);
}

export function number(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

export function unique(values) {
  const seen = new Set();
  const output = [];
  for (const value of values) {
    const key = text(value);
    if (seen.has(key)) continue;
    seen.add(key);
    output.push(key);
  }
  return output;
}

export function isCanonicalChartType(value) {
  return CANONICAL_CHART_TYPES.includes(value);
}

export function canonicalVisualizationType(value) {
  return isCanonicalChartType(value) ? value : "bar";
}

export function groupData(data) {
  const groups = new Map();
  for (const point of asArray(data)) {
    const y = number(point && point.y);
    if (y == null) continue;
    const series = text((point && point.series) || "Value");
    if (!groups.has(series)) groups.set(series, []);
    groups.get(series).push({ x: point && point.x, y, label: point && point.label, raw: point });
  }
  return groups;
}

export function rechartsLegendNames(data, chartType) {
  if (chartType === "histogram" || chartType === "heatmap" || chartType === "boxPlot") return [];
  return [...groupData(data).keys()];
}

export function hasNumericX(data) {
  return asArray(data).some((point) => number(point && point.x) != null);
}

export function emptyChartMessage(data, chartType, visibleSeries = new Set()) {
  const rows = asArray(data);
  if (!rows.length) return "No chart data to render.";
  const legendNames = rechartsLegendNames(rows, chartType);
  const seriesNames = [...groupData(rows).keys()];
  if (legendNames.length && visibleSeries instanceof Set && visibleSeries.size && !legendNames.some((name) => visibleSeries.has(name))) {
    return "No visible series selected.";
  }
  if (chartType === "scatter" && !hasNumericX(rows)) return "Scatter plots need numeric x and y values.";
  if (chartType === "histogram" && !rows.some((point) => number(point && (point.y != null ? point.y : point.x)) != null)) {
    return "Histogram needs numeric values.";
  }
  if (chartType === "heatmap" && seriesNames.length <= 1) return "Heatmaps need a grouping field with at least two series.";
  if (chartType === "pie") {
    const total = rows.reduce((sum, point) => sum + Math.max(0, number(point && point.y) ?? 0), 0);
    if (!total) return "Pie charts need positive values.";
    if (seriesNames.length <= 1) return "Pie charts need a grouping field with at least two slices.";
  }
  if ((chartType === "line" || chartType === "area" || chartType === "stackedArea" || chartType === "sparkline") && unique(rows.map((point) => point && point.x)).length < 2) {
    return `${chartType === "stackedArea" ? "Stacked area" : "Trend"} charts need at least two x values.`;
  }
  if (chartType === "stackedArea" && seriesNames.length <= 1) return "Stacked area charts need a grouping field with at least two series.";
  if (chartType === "funnel") {
    const xCount = unique(rows.map((point) => point && point.x)).length;
    if (seriesNames.length > 1) return "Funnel charts need a single series.";
    if (xCount < 2 || xCount > 8) return "Funnel charts need between two and eight stages.";
    if (rows.some((point) => (number(point && point.y) ?? 0) < 0)) return "Funnel charts need non-negative values.";
  }
  if (chartType === "waterfall") {
    const xCount = unique(rows.map((point) => point && point.x)).length;
    if (seriesNames.length > 1) return "Waterfall charts need a single series.";
    if (xCount < 2 || xCount > 12) return "Waterfall charts need between two and twelve steps.";
  }
  if (chartType === "leaderboard") {
    const xCount = unique(rows.map((point) => point && point.x)).length;
    if (seriesNames.length > 1) return "Leaderboards need a single series.";
    if (xCount < 2) return "Leaderboards need at least two ranked categories.";
  }
  if (chartType === "boxPlot") {
    const numericRows = rows.filter((point) => number(point && point.y) != null);
    const valuesByCategory = new Map();
    for (const point of numericRows) {
      const key = text(point && point.x);
      valuesByCategory.set(key, (valuesByCategory.get(key) || 0) + 1);
    }
    if (numericRows.length < 10 || Math.max(0, ...valuesByCategory.values()) < 5) {
      return "Box plots need at least ten numeric values and five values in one category.";
    }
  }
  return "";
}

export function isDateLikeValue(value) {
  if (value instanceof Date && Number.isFinite(value.getTime())) return true;
  if (typeof value !== "string") return false;
  const raw = value.trim();
  if (!raw) return false;
  if (!/^\d{4}[-/]\d{1,2}(?:[-/]\d{1,2})?(?:[T\s]\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)?$/.test(raw)) {
    return false;
  }
  return Number.isFinite(new Date(raw).getTime());
}

export function resolveCssColor(value, root = document.documentElement) {
  const raw = text(value).trim();
  if (!raw.startsWith("var(")) return raw;
  const match = raw.match(/^var\((--[^,\s)]+)(?:,\s*([^)]+))?\)$/);
  if (!match) return raw;
  const resolved = getComputedStyle(root).getPropertyValue(match[1]).trim();
  return resolved || text(match[2]).trim();
}

export function resolveCssColors(values, root) {
  return asArray(values).map((value) => resolveCssColor(value, root)).filter(Boolean);
}

export function colorAt(colors, index) {
  return colors[index % colors.length] || DEFAULT_COLORS[index % DEFAULT_COLORS.length];
}

function compactDigits(value) {
  const absolute = Math.abs(value);
  if (absolute >= COMPACT_VALUE_THRESHOLD) return 1;
  return 2;
}

function formatNumber(value, compact = false) {
  const absolute = Math.abs(value);
  return new Intl.NumberFormat(undefined, {
    maximumFractionDigits: compactDigits(value),
    notation: compact && absolute >= COMPACT_VALUE_THRESHOLD ? "compact" : "standard",
  }).format(value);
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
  const absolute = Math.abs(value);
  return new Intl.NumberFormat(undefined, {
    currency: "USD",
    maximumFractionDigits: compactDigits(value),
    notation: absolute >= COMPACT_VALUE_THRESHOLD ? "compact" : "standard",
    style: "currency",
  }).format(value).replace(/\.0([KMBT])$/i, "$1");
}

function isPercentWordUnit(unit) {
  const normalized = text(unit).toLowerCase();
  return normalized === "percent" || normalized === "percentage";
}

function formatPercent(value) {
  return new Intl.NumberFormat(undefined, {
    maximumFractionDigits: 1,
    style: "percent",
  }).format(value);
}

export function formatValue(value, unit = "") {
  const numeric = number(value);
  if (numeric == null) return text(value);
  const cleanUnit = text(unit);
  if (!cleanUnit) return formatNumber(numeric, true);
  if (isPercentWordUnit(cleanUnit)) return formatPercent(numeric);
  if (cleanUnit === "%" || cleanUnit.startsWith("%")) return `${formatNumber(numeric)}%`;
  if (isUsdUnit(cleanUnit)) return formatCurrency(numeric);
  const scaleSuffix = unitScaleSuffix(cleanUnit);
  if (scaleSuffix) return `$${formatNumber(numeric)}${scaleSuffix}`;
  if (cleanUnit.startsWith("$")) return `$${formatNumber(numeric)}${cleanUnit.slice(1)}`;
  return `${formatNumber(numeric, true)} ${cleanUnit}`;
}

export function buildCategoryRows(data) {
  const groups = groupData(data);
  const xValues = unique(asArray(data).map((point) => point && point.x));
  return xValues.map((x) => {
    const row = { x: text(x) };
    for (const [series, points] of groups.entries()) {
      const point = points.find((item) => text(item.x) === text(x));
      row[series] = point ? point.y : null;
    }
    return row;
  });
}

export function histogramBins(data, requestedBinCount) {
  const values = asArray(data)
    .map((point) => number(point && (point.y != null ? point.y : point.x)))
    .filter((value) => value != null);
  if (!values.length) return [];
  const min = Math.min(...values);
  const max = Math.max(...values);
  const binCount = Math.max(1, requestedBinCount || Math.min(12, Math.max(5, Math.ceil(Math.sqrt(values.length)))));
  const binWidth = (max - min || 1) / binCount;
  const bins = Array.from({ length: binCount }, (_, index) => ({
    x: `${formatValue(min + index * binWidth)}-${formatValue(min + (index + 1) * binWidth)}`,
    count: 0,
    start: min + index * binWidth,
    end: min + (index + 1) * binWidth,
  }));
  for (const value of values) {
    const index = Math.min(binCount - 1, Math.max(0, Math.floor((value - min) / binWidth)));
    bins[index].count += 1;
  }
  return bins;
}

export function pieRows(data) {
  const groups = groupData(data);
  return [...groups.entries()]
    .map(([name, points]) => ({
      name,
      value: points.reduce((sum, point) => sum + Math.max(0, point.y), 0),
    }))
    .filter((row) => row.value > 0);
}
