import type {
  ChartReferenceLineSpec,
  ChartComparisonContext,
  ChartIntent,
  ChartSeriesColor,
  ChartSurfaceOptions,
  ChartType as SharedChartType,
} from "./charting/chart-contract";

export type ValueFormat = "compact" | "number" | "percent" | "currency";
export type ChartType = SharedChartType;
export type LayoutWidth = "full" | "half";
export type TableDensity = "dense" | "spacious";
export type SnapshotStatus = "ready" | "partial" | "blocked" | "fixture";
export type AnalyticsSurface = "dashboard" | "report";
export type ReportBlockType =
  | "markdown"
  | "metric-strip"
  | "chart"
  | "table"
  | "html";

export type DashboardRow = Record<string, string | number | boolean | null>;

export type DashboardSnapshot = {
  version: 1;
  generatedAt: string;
  status?: SnapshotStatus;
  datasets: Record<string, DashboardRow[]>;
  accessIssues?: AccessIssue[];
};

export type AppPackageInfo = {
  root: string;
  manifestPath: string;
  snapshotPath: string;
  originUrl?: string;
};

export type ArtifactReaderMode = "mcp" | "portable";

export type ArtifactReaderCapabilities = {
  copyImage: boolean;
  deleteContent: boolean;
  editContent: boolean;
  editVisualization: boolean;
  fetchSourceText: boolean;
  hostFullscreen: boolean;
  hostPrompts: boolean;
  persistState: boolean;
  reorderContent: boolean;
};

export type ArtifactReaderEnvironment = {
  capabilities: ArtifactReaderCapabilities;
  getSourceText?: (source: SourceSpec) => Promise<string | null> | string | null;
  mode: ArtifactReaderMode;
  requestFullscreen?: () => Promise<unknown> | unknown;
  sendAgentPrompt?: (prompt: string, title: string) => Promise<boolean> | boolean;
};

export type ArtifactReaderArtifact = {
  manifest: DashboardManifest;
  packageInfo?: AppPackageInfo & Record<string, unknown>;
  snapshot: DashboardSnapshot;
  sources?: SourceSpec[];
  surface?: AnalyticsSurface;
};

export type DashboardManifest = {
  version: 1;
  surface?: AnalyticsSurface;
  title: string;
  description?: string;
  generatedAt: string;
  filters?: FilterSpec[];
  cards?: CardSpec[];
  charts?: ChartSpec[];
  tables?: TableSpec[];
  sources?: SourceSpec[];
  blocks?: ReportBlockSpec[];
};

export type ReportBlockSpec = {
  id: string;
  type: ReportBlockType;
  body?: string;
  layout?: LayoutWidth;
  cardIds?: string[];
  chartId?: string;
  tableId?: string;
  sourceId?: string;
};

export type FilterSpec = {
  id: string;
  label: string;
  dataset: string;
  field: string;
  defaultValue?: string;
  includeAll?: boolean;
  targets?: FilterTargetSpec[];
};

export type FilterTargetSpec = {
  dataset: string;
  field?: string;
};

export type CardMetricSpec = {
  label: string;
  field: string;
  format?: ValueFormat;
  signed?: boolean;
};

export type CardSpec = {
  id: string;
  description?: string;
  dataset: string;
  sourceId?: string;
  source?: SourceSpec;
  filter?: Record<string, string | number | boolean | null>;
  metrics: CardMetricSpec[];
};

export type ChartSeriesSpec = {
  field: string;
  label?: string;
  color?: ChartSeriesColor;
  lineStyle?: "solid" | "dashed" | "dotted";
  role?: "actual" | "baseline" | "target" | "forecast" | "plan" | "comparison";
  semanticRole?: "actual" | "baseline" | "target" | "forecast" | "plan" | "comparison";
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
  source?: SourceSpec;
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
  layout?: LayoutWidth;
  combinationRationale?: string;
  maxRows?: number;
  referenceLines?: ChartReferenceLineSpec[];
  emptyState?: string;
  compatibleTypes?: ChartType[];
  surface?: ChartSurfaceOptions;
};

export type SourceQuerySpec = {
  engine?: string;
  query?: string;
  sql?: string;
  id?: string;
  url?: string;
  description?: string;
  executed_at?: string;
  language?: string;
  filters?: string[];
  metric_definitions?: string[];
  tables_used?: string[];
};

export type TableSpec = {
  id: string;
  title: string;
  subtitle?: string;
  showDescription?: boolean;
  headerMarkdown?: string;
  dataset: string;
  defaultSort?: {
    field: string;
    direction: "asc" | "desc";
  };
  density?: TableDensity;
  sourceId?: string;
  source?: SourceSpec;
  layout?: LayoutWidth;
  columns: Array<{
    field: string;
    label: string;
    format?: ValueFormat;
    movement?: boolean;
    role?: "movement" | "value" | string;
    semantic?: "movement" | "value" | string;
    type?: ValueFormat | "date" | "text";
  }>;
};

export type SourceSpec = {
  id?: string;
  label?: string;
  path?: string;
  href?: string;
  query?: SourceQuerySpec;
};

export type AccessIssue = {
  id: string;
  scope?: string;
  sourceId?: string;
  dataset?: string;
  message: string;
  actionLabel?: string;
  actionHref?: string;
};
