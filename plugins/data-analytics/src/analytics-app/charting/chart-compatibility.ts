import type { ChartSpec, ChartType } from "./chart-contract";
import { asNumber, type ChartDataRow } from "./chart-transforms";
import { CHART_TYPE_LABELS, CHART_TYPE_ORDER } from "./chart-theme";

export type ChartTypeOption = {
  label: string;
  type: ChartType;
};

export type ChartTypeOptionSection = {
  options: ChartTypeOption[];
  title: string;
};

const CHART_TYPE_MENU_SECTIONS: Array<{ title: string; types: ChartType[] }> = [
  {
    title: "Trends",
    types: ["line", "area", "stackedArea", "sparkline"],
  },
  {
    title: "Comparison",
    types: ["bar", "leaderboard"],
  },
  {
    title: "Distribution",
    types: ["histogram", "boxPlot"],
  },
  {
    title: "Relationships",
    types: ["scatter", "heatmap"],
  },
  {
    title: "Composition",
    types: ["pie"],
  },
  {
    title: "Progression",
    types: ["funnel", "waterfall"],
  },
];

const CHART_TYPE_MENU_ORDER: ChartType[] = CHART_TYPE_MENU_SECTIONS.flatMap((section) => section.types);
const HIDDEN_BAR_VARIANT_TYPE_LIST: ChartType[] = [
  "horizontalBar",
  "stackedBar",
  "stackedBar100",
  "horizontalStackedBar",
  "horizontalStackedBar100",
];
const HIDDEN_BAR_VARIANT_TYPES = new Set<ChartType>(HIDDEN_BAR_VARIANT_TYPE_LIST);
const BAR_SHAPE_TYPES: ChartType[] = ["bar", "leaderboard"];
const FUNNEL_SHAPE_TYPES: ChartType[] = ["bar", "funnel"];
const PIE_SHAPE_TYPES: ChartType[] = ["bar", "pie"];
const WATERFALL_SHAPE_TYPES: ChartType[] = ["bar", "waterfall"];
const STACKED_SHAPE_TYPES: ChartType[] = ["bar", "heatmap"];
const TREND_SHAPE_TYPES: ChartType[] = ["line", "area", "stackedArea", "sparkline", "bar"];

export function isChartType(value: unknown): value is ChartType {
  return typeof value === "string" && CHART_TYPE_ORDER.includes(value as ChartType);
}

function chartTypeOptions(types: readonly ChartType[]): ChartTypeOption[] {
  return types.map((type) => ({
    label: CHART_TYPE_LABELS[type],
    type,
  }));
}

export function compatibleChartTypesFor(_chart: ChartSpec, _rows: ChartDataRow[]): ChartTypeOption[] {
  return chartTypeOptions(CHART_TYPE_MENU_ORDER);
}

function hasMultipleXValues(chart: ChartSpec, rows: ChartDataRow[]): boolean {
  return new Set(rows.map((row) => String(row[chart.xField] ?? ""))).size >= 2;
}

function hasNumericX(chart: ChartSpec, rows: ChartDataRow[]): boolean {
  return rows.some((row) => asNumber(row[chart.xField]) != null);
}

function hasNumericSeries(chart: ChartSpec, rows: ChartDataRow[], seriesLimit = chart.series.length): boolean {
  const series = chart.series.slice(0, Math.max(1, seriesLimit));
  return rows.some((row) => series.some((item) => asNumber(row[item.field]) != null));
}

function hasPositiveSeries(chart: ChartSpec, rows: ChartDataRow[]): boolean {
  return rows.some((row) => chart.series.some((item) => (asNumber(row[item.field]) ?? 0) > 0));
}

function chartTypesForCurrentShape(chart: ChartSpec): ChartType[] {
  const seriesCount = chart.series.length;
  if (chart.type === "line" || chart.type === "area" || chart.type === "stackedArea" || chart.type === "sparkline") {
    return TREND_SHAPE_TYPES;
  }
  if (chart.type === "funnel" || chart.intent === "funnel") return FUNNEL_SHAPE_TYPES;
  if (chart.type === "pie" || chart.intent === "composition") return PIE_SHAPE_TYPES;
  if (chart.type === "waterfall" || chart.intent === "decomposition") return WATERFALL_SHAPE_TYPES;
  if (
    chart.type === "stackedBar" ||
    chart.type === "stackedBar100" ||
    chart.type === "horizontalStackedBar" ||
    chart.type === "horizontalStackedBar100" ||
    chart.type === "heatmap" ||
    seriesCount > 1
  ) {
    return STACKED_SHAPE_TYPES;
  }
  if (chart.type === "bar" || chart.type === "horizontalBar" || chart.type === "leaderboard") {
    return BAR_SHAPE_TYPES;
  }
  if (chart.type === "histogram") return ["histogram"];
  if (chart.type === "boxPlot") return ["boxPlot"];
  if (chart.type === "scatter") return ["scatter"];
  return [chart.type];
}

function chartTypeCanReuseFields(type: ChartType, chart: ChartSpec, rows: ChartDataRow[]): boolean {
  if (type === chart.type) return true;
  if (type === "sparkline" && chart.series.length > 1) return false;
  if ((type === "line" || type === "area" || type === "stackedArea" || type === "sparkline") && !hasMultipleXValues(chart, rows)) {
    return false;
  }
  if ((type === "funnel" || type === "leaderboard" || type === "waterfall") && chart.series.length > 1) {
    return false;
  }
  if (type === "pie" && !hasPositiveSeries(chart, rows)) return false;
  if (type === "histogram" && !hasNumericSeries(chart, rows, 1)) return false;
  if (type === "scatter" && (!hasNumericX(chart, rows) || !hasNumericSeries(chart, rows))) return false;
  if (type === "heatmap" && chart.series.length < 2) return false;
  if (type === "boxPlot" && chart.series.length < 5) return false;
  return true;
}

function chartTypeAllowedByManifest(type: ChartType, chart: ChartSpec, allowedByManifest: Set<ChartType> | null): boolean {
  if (!allowedByManifest) return true;
  if (type === chart.type || allowedByManifest.has(type)) return true;
  return (
    type === "bar" &&
    (HIDDEN_BAR_VARIANT_TYPES.has(chart.type) ||
      HIDDEN_BAR_VARIANT_TYPE_LIST.some((variant) => allowedByManifest.has(variant)))
  );
}

export function compatibleChartTypesForDataShape(chart: ChartSpec, rows: ChartDataRow[]): ChartTypeOption[] {
  const allowedByManifest = chart.compatibleTypes?.length ? new Set(chart.compatibleTypes) : null;
  const shapeTypes = chartTypesForCurrentShape(chart).filter((type) => {
    if (!chartTypeAllowedByManifest(type, chart, allowedByManifest)) return false;
    return chartTypeCanReuseFields(type, chart, rows);
  });
  const orderedTypes = CHART_TYPE_MENU_ORDER.filter((type) => shapeTypes.includes(type));
  if (!orderedTypes.includes(chart.type) && !HIDDEN_BAR_VARIANT_TYPES.has(chart.type)) orderedTypes.push(chart.type);
  return chartTypeOptions(orderedTypes);
}

export function chartTypeSectionsForOptions(options: readonly ChartTypeOption[]): ChartTypeOptionSection[] {
  const optionByType = new Map(options.map((option) => [option.type, option]));
  return CHART_TYPE_MENU_SECTIONS.map((section) => ({
    title: section.title,
    options: section.types.flatMap((type) => {
      const option = optionByType.get(type);
      return option ? [option] : [];
    }),
  })).filter((section) => section.options.length > 0);
}
