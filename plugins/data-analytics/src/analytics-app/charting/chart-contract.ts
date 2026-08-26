export const CHART_TYPES = [
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
] as const;

export type ChartType = (typeof CHART_TYPES)[number];

export type ValueFormat = "compact" | "number" | "percent" | "currency";

export type ChartSurface = "compact" | "card" | "explorer" | "export";

export type ChartIntent =
  | "status"
  | "trend"
  | "comparison"
  | "composition"
  | "decomposition"
  | "distribution"
  | "relationship"
  | "funnel"
  | "lookup"
  | "custom";

export type ChartComparisonContext = {
  baseline?: string;
  denominator?: string;
  grain?: string;
  normalization?: string;
  semanticFamily?: string;
  unit?: string;
};

export type ChartPaletteKind =
  | "categorical"
  | "sequential"
  | "diverging"
  | "semantic"
  | "identity";

export type ChartLineStyle = "solid" | "dashed" | "dotted";

export type ChartSeriesColor =
  | "blue"
  | "purple"
  | "green"
  | "neutral"
  | "orange"
  | "yellow"
  | "pink"
  | "red";

export type ChartSeriesRole =
  | "actual"
  | "baseline"
  | "target"
  | "forecast"
  | "plan"
  | "comparison";

export type ChartSeriesSpec = {
  field: string;
  label?: string;
  color?: ChartSeriesColor;
  lineStyle?: ChartLineStyle;
  role?: ChartSeriesRole;
  semanticRole?: ChartSeriesRole;
};

export type ChartEncodingSpec = {
  field?: string;
  fields?: string[];
  type?: "nominal" | "ordinal" | "quantitative" | "temporal" | "text";
  aggregate?: "none" | "sum" | "avg" | "min" | "max" | "count" | "countDistinct";
  format?: ValueFormat;
  label?: string;
  unit?: string;
};

export type ChartPaletteSpec = {
  kind: ChartPaletteKind;
  name?: string;
  midpoint?: number;
};

export type ChartReferenceLineSpec = {
  axis?: "x" | "y";
  color?: ChartSeriesColor;
  label?: string;
  lineStyle?: ChartLineStyle;
  value: number | string;
};

export type ChartLegendOptions = {
  position?: "bottom" | "right";
  sort?: "spec" | "labelAsc" | "labelDesc";
  title?: string;
};

export type ChartValueLabelMode = "none" | "auto" | "all" | "endpoints";

export type ChartLabelOptions = {
  values?: ChartValueLabelMode;
};

export type ChartSurfaceOptions = {
  surface?: ChartSurface;
  compact?: boolean;
  interactiveLegend?: boolean;
  showControls?: boolean;
  viewMode?: "visualization" | "table" | "both";
};

export type ChartBarOrientation = "vertical" | "horizontal";

export type ChartBarGroupMode = "single" | "grouped" | "stacked" | "stacked100";

export type ChartSettings = {
  bins?: number;
  categoryLabelPolicy?: "wrap" | "truncate" | "rotate";
  groupMode?: ChartBarGroupMode;
  limit?: number;
  maxSegments?: number;
  orientation?: ChartBarOrientation;
  otherThreshold?: number;
  showLatestValue?: boolean;
  showPercent?: boolean;
  showPoints?: "always" | "never";
  showValues?: boolean;
  sort?: "none" | "ascending" | "descending" | "custom";
};

export type ChartSpec = {
  id: string;
  title: string;
  subtitle?: string;
  showDescription?: boolean;
  headerMarkdown?: string;
  intent?: ChartIntent;
  question?: string;
  rationale?: string;
  comparisonContext?: ChartComparisonContext;
  type: ChartType;
  dataset: string;
  sourceId?: string;
  encodings?: {
    x?: ChartEncodingSpec;
    y?: ChartEncodingSpec;
    color?: ChartEncodingSpec;
    lineStyle?: ChartEncodingSpec;
    size?: ChartEncodingSpec;
    facet?: ChartEncodingSpec;
    label?: ChartEncodingSpec;
    tooltip?: ChartEncodingSpec[];
  };
  xField?: string;
  xAxisTitle?: string;
  yAxisTitle?: string;
  series?: ChartSeriesSpec[];
  valueFormat?: ValueFormat;
  unit?: string;
  layout?: "full" | "half";
  combinationRationale?: string;
  labels?: ChartLabelOptions;
  legend?: ChartLegendOptions;
  maxRows?: number;
  palette?: ChartPaletteSpec;
  referenceLines?: ChartReferenceLineSpec[];
  emptyState?: string;
  compatibleTypes?: ChartType[];
  settings?: ChartSettings;
  surface?: ChartSurfaceOptions;
};

export function isChartType(value: unknown): value is ChartType {
  return typeof value === "string" && (CHART_TYPES as readonly string[]).includes(value);
}
