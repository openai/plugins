import type {
  ChartBarGroupMode,
  ChartBarOrientation,
  ChartLineStyle,
  ChartPaletteKind,
  ChartSeriesColor,
  ChartSeriesRole,
  ChartType,
} from "./chart-contract";

export const CHART_TYPE_ORDER: ChartType[] = [
  "line",
  "area",
  "stackedArea",
  "bar",
  "horizontalBar",
  "stackedBar",
  "stackedBar100",
  "horizontalStackedBar",
  "horizontalStackedBar100",
  "leaderboard",
  "sparkline",
  "scatter",
  "histogram",
  "heatmap",
  "pie",
  "funnel",
  "waterfall",
  "boxPlot",
];

export const CHART_TYPE_LABELS: Record<ChartType, string> = {
  area: "Area",
  bar: "Bar",
  boxPlot: "Box plot",
  funnel: "Funnel",
  heatmap: "Heatmap",
  histogram: "Histogram",
  horizontalBar: "Horizontal bar",
  horizontalStackedBar: "Horizontal stacked bar",
  horizontalStackedBar100: "100% horizontal stacked bar",
  leaderboard: "Leaderboard",
  line: "Line",
  pie: "Pie",
  scatter: "Scatter",
  sparkline: "Sparkline",
  stackedArea: "Stacked area",
  stackedBar: "Stacked bar",
  stackedBar100: "100% stacked bar",
  waterfall: "Waterfall",
};

export const SERIES_COLORS: Record<ChartSeriesColor, string> = {
  blue: "var(--ds-chart-series-blue)",
  purple: "var(--ds-chart-series-purple)",
  yellow: "var(--ds-chart-series-yellow)",
  orange: "var(--ds-chart-series-orange)",
  green: "var(--ds-chart-series-green)",
  pink: "var(--ds-chart-series-pink)",
  neutral: "var(--ds-chart-series-neutral)",
  red: "var(--ds-chart-series-red)",
};

export const DEFAULT_SERIES_COLOR_ORDER: ChartSeriesColor[] = [
  "blue",
  "orange",
  "green",
  "purple",
  "red",
  "pink",
  "yellow",
  "neutral",
];

export const SEMANTIC_ROLE_COLORS: Partial<Record<ChartSeriesRole, ChartSeriesColor>> = {
  actual: "blue",
  baseline: "neutral",
  comparison: "purple",
  forecast: "neutral",
  plan: "neutral",
  target: "neutral",
};

export const STACKED_SERIES_FALLBACK_COLORS = [
  "var(--ds-chart-stack-1)",
  "var(--ds-chart-stack-2)",
  "var(--ds-chart-stack-3)",
  "var(--ds-chart-stack-4)",
  "var(--ds-chart-stack-5)",
  "var(--ds-chart-stack-6)",
  "var(--ds-chart-stack-7)",
  "var(--ds-chart-stack-8)",
];

export const SEQUENTIAL_SERIES_COLORS = [
  "var(--ds-chart-sequential-1)",
  "var(--ds-chart-sequential-2)",
  "var(--ds-chart-sequential-3)",
  "var(--ds-chart-sequential-4)",
  "var(--ds-chart-sequential-5)",
  "var(--ds-chart-sequential-6)",
  "var(--ds-chart-sequential-7)",
  "var(--ds-chart-sequential-8)",
  "var(--ds-chart-sequential-9)",
];

export const DIVERGING_SERIES_COLORS = [
  "var(--ds-chart-diverging-negative-2)",
  "var(--ds-chart-diverging-negative-1)",
  "var(--ds-chart-diverging-neutral)",
  "var(--ds-chart-diverging-positive-1)",
  "var(--ds-chart-diverging-positive-2)",
];

export const HEATMAP_BLUE_SCALE = [
  "var(--ds-chart-heatmap-1)",
  "var(--ds-chart-heatmap-2)",
  "var(--ds-chart-heatmap-3)",
  "var(--ds-chart-heatmap-4)",
  "var(--ds-chart-heatmap-5)",
  "var(--ds-chart-heatmap-6)",
  "var(--ds-chart-heatmap-7)",
  "var(--ds-chart-heatmap-8)",
  "var(--ds-chart-heatmap-9)",
];

export const FUNNEL_STAGE_COLORS = [
  "var(--ds-chart-funnel-1)",
  "var(--ds-chart-funnel-2)",
  "var(--ds-chart-funnel-3)",
  "var(--ds-chart-funnel-4)",
  "var(--ds-chart-funnel-5)",
];

export function strokeDasharrayForLineStyle(lineStyle: ChartLineStyle | undefined): string | undefined {
  if (lineStyle === "dotted") return "2 4";
  if (lineStyle === "dashed") return "5 5";
  return undefined;
}

export function colorForSequentialValue(value: number | null, min: number, max: number): string {
  if (value == null || !Number.isFinite(value)) return SEQUENTIAL_SERIES_COLORS[0];
  const range = max - min;
  const intensity = range === 0 ? 1 : (value - min) / range;
  const index = Math.max(
    0,
    Math.min(SEQUENTIAL_SERIES_COLORS.length - 1, Math.round(intensity * (SEQUENTIAL_SERIES_COLORS.length - 1))),
  );
  return SEQUENTIAL_SERIES_COLORS[index] ?? SEQUENTIAL_SERIES_COLORS[0];
}

export function colorForDivergingValue(value: number | null, midpoint = 0): string {
  if (value == null || !Number.isFinite(value)) return DIVERGING_SERIES_COLORS[2];
  if (value < midpoint) return DIVERGING_SERIES_COLORS[0];
  if (value > midpoint) return DIVERGING_SERIES_COLORS[4];
  return DIVERGING_SERIES_COLORS[2];
}

export function isStackedChartType(type: ChartType, groupMode?: ChartBarGroupMode): boolean {
  return (
    type === "stackedArea" ||
    type === "stackedBar" ||
    type === "stackedBar100" ||
    type === "horizontalStackedBar" ||
    type === "horizontalStackedBar100" ||
    (type === "bar" && (groupMode === "stacked" || groupMode === "stacked100"))
  );
}

export function isNormalizedStackedChartType(type: ChartType, groupMode?: ChartBarGroupMode): boolean {
  return type === "stackedBar100" || type === "horizontalStackedBar100" || (type === "bar" && groupMode === "stacked100");
}

export function isHorizontalChartType(type: ChartType, orientation?: ChartBarOrientation): boolean {
  return type === "horizontalBar" || type === "horizontalStackedBar" || type === "horizontalStackedBar100" || (type === "bar" && orientation === "horizontal");
}

export function colorForSeries(
  color: ChartSeriesColor | undefined,
  index: number,
  options: {
    paletteKind?: ChartPaletteKind;
    semanticRole?: ChartSeriesRole;
    singleSeriesTrend?: boolean;
    stacked?: boolean;
  } = {},
): string {
  if (color) return SERIES_COLORS[color] ?? SERIES_COLORS.blue;
  if (options.paletteKind === "semantic" && options.semanticRole) {
    return SERIES_COLORS[SEMANTIC_ROLE_COLORS[options.semanticRole] ?? "blue"];
  }
  if (options.paletteKind === "sequential") {
    return SEQUENTIAL_SERIES_COLORS[index % SEQUENTIAL_SERIES_COLORS.length];
  }
  if (options.paletteKind === "diverging") {
    return DIVERGING_SERIES_COLORS[index % DIVERGING_SERIES_COLORS.length];
  }
  if (options.stacked && !color) {
    return STACKED_SERIES_FALLBACK_COLORS[index % STACKED_SERIES_FALLBACK_COLORS.length];
  }
  if (options.singleSeriesTrend && !color) return SERIES_COLORS.blue;
  return SERIES_COLORS[DEFAULT_SERIES_COLOR_ORDER[index % DEFAULT_SERIES_COLOR_ORDER.length]] ?? SERIES_COLORS.blue;
}
