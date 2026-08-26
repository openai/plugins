import type { ChartEncodingSpec, ChartSpec, ValueFormat } from "./chart-contract";
import { chartEncoding, chartEncodingField } from "./chart-app-helpers";
import { asNumber, formatDateAxisLabel, formatValue } from "./chart-transforms";
import { colorForSeries, isNormalizedStackedChartType, isStackedChartType } from "./chart-theme";

export type ChartTooltipPayloadItem = {
  color?: string;
  dataKey?: string | number;
  fill?: string;
  name?: string | number;
  payload?: unknown;
  stroke?: string;
  value?: unknown;
};

export type ChartTooltipColorResolver = (item: ChartTooltipPayloadItem, index: number) => string | undefined;

function isGenericTooltipName(value: unknown): boolean {
  return value == null || String(value).trim().toLowerCase() === "value";
}

function normalizedLabel(value: unknown): string {
  return String(value ?? "")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "");
}

function humanizeFieldName(field: string): string {
  const withoutUnit = field.replace(/_(usd|dollars?|amount|value)$/i, "");
  return withoutUnit
    .replace(/_/g, " ")
    .replace(/\b\w[\w-]*/g, (word) => {
      const upper = word.toUpperCase();
      if (["api", "arr", "mrr", "usd", "eur", "gbp", "id"].includes(word.toLowerCase())) return upper;
      return `${word.charAt(0).toUpperCase()}${word.slice(1)}`;
    });
}

function isCategoryAxisName(chart: ChartSpec, value: unknown): boolean {
  const normalized = normalizedLabel(value);
  return Boolean(normalized) && (
    normalized === normalizedLabel(chart.xField) ||
    normalized === normalizedLabel(humanizeFieldName(chart.xField))
  );
}

function isValueFormat(value: unknown): value is ValueFormat {
  return value === "compact" || value === "number" || value === "percent" || value === "currency";
}

function tooltipEncoding(chart: ChartSpec, item: ChartTooltipPayloadItem): ChartEncodingSpec | null {
  const dataKey = item.dataKey == null ? "" : String(item.dataKey);
  if (!dataKey) return null;
  for (const role of ["size", "x", "y"] as const) {
    if (chartEncodingField(chart, role) === dataKey) return chartEncoding(chart, role);
  }
  return null;
}

function isPercentSymbolUnit(unit: string | undefined): boolean {
  return unit?.trim() === "%";
}

function tooltipEncodingValueFormat(chart: ChartSpec, encoding: ChartEncodingSpec): ValueFormat {
  if (isValueFormat(encoding.format)) return encoding.format;
  if (chart.valueFormat === "percent" && isPercentSymbolUnit(encoding.unit)) return "percent";
  return "number";
}

function tooltipItemName(chart: ChartSpec, item: ChartTooltipPayloadItem): string | null {
  const dataKey = item.dataKey == null ? "" : String(item.dataKey);
  const encoding = tooltipEncoding(chart, item);
  if (encoding?.label) return encoding.label;
  const series = chart.series.find((candidate) => (
    candidate.field === dataKey || String(candidate.label ?? "") === String(item.name ?? "")
  ));
  const candidate = series?.label ?? item.name ?? item.dataKey;
  if (chart.series.length === 1 && isCategoryAxisName(chart, candidate) && dataKey) {
    return humanizeFieldName(dataKey);
  }
  if (!isGenericTooltipName(candidate)) return String(candidate);

  const fallback = chart.series.length === 1 ? chart.series[0]?.label ?? chart.series[0]?.field : null;
  if (chart.series.length === 1 && isCategoryAxisName(chart, fallback) && dataKey) {
    return humanizeFieldName(dataKey);
  }
  return isGenericTooltipName(fallback) ? null : String(fallback);
}

function tooltipItemColor(chart: ChartSpec, item: ChartTooltipPayloadItem, itemIndex: number): string {
  const dataKey = item.dataKey == null ? "" : String(item.dataKey);
  const seriesIndex = chart.series.findIndex((series) => series.field === dataKey || series.label === item.name);
  return item.color
    ?? item.stroke
    ?? item.fill
    ?? colorForSeries(undefined, seriesIndex < 0 ? itemIndex : seriesIndex);
}

function tooltipItemValue(chart: ChartSpec, item: ChartTooltipPayloadItem, visibleTotal: number): string {
  const encoding = tooltipEncoding(chart, item);
  if (encoding) {
    const valueFormat = tooltipEncodingValueFormat(chart, encoding);
    return formatValue(item.value, valueFormat, encoding.unit);
  }
  const numeric = asNumber(item.value);
  if (isNormalizedStackedChartType(chart.type, chart.settings?.groupMode) && numeric != null && visibleTotal > 0) {
    const share = numeric / visibleTotal;
    return `${formatValue(share, "percent")} (${formatValue(numeric, chart.valueFormat, chart.unit)})`;
  }
  return formatValue(item.value, chart.valueFormat, chart.unit);
}

function scatterPointLabel(chart: ChartSpec, payload: ChartTooltipPayloadItem[]): string | null {
  if (chart.type !== "scatter") return null;
  const labelField = chartEncodingField(chart, "label");
  if (!labelField) return null;
  const row = payload.find((item) => item.payload && typeof item.payload === "object")?.payload as
    | Record<string, unknown>
    | undefined;
  const label = row?.[labelField];
  return label == null || String(label).trim() === "" ? null : String(label);
}

export function ChartTooltip({
  active,
  chart,
  getItemColor,
  label,
  payload = [],
}: {
  active?: boolean;
  chart: ChartSpec;
  getItemColor?: ChartTooltipColorResolver;
  label?: unknown;
  payload?: ChartTooltipPayloadItem[];
}) {
  if (!active || !payload.length) return null;
  const seriesIndex = new Map(chart.series.map((series, index) => [series.field, index]));
  const items = payload
    .filter((item) => item.value != null)
    .sort((a, b) => {
      if (isStackedChartType(chart.type, chart.settings?.groupMode)) {
        return (seriesIndex.get(String(b.dataKey)) ?? 0) - (seriesIndex.get(String(a.dataKey)) ?? 0);
      }
      return (asNumber(b.value) ?? Number.NEGATIVE_INFINITY) - (asNumber(a.value) ?? Number.NEGATIVE_INFINITY);
    });
  const visibleTotal = isNormalizedStackedChartType(chart.type, chart.settings?.groupMode)
    ? items.reduce((sum, item) => {
        const numeric = asNumber(item.value);
        return numeric == null ? sum : sum + Math.abs(numeric);
      }, 0)
    : 0;
  const pointLabel = scatterPointLabel(chart, items);
  const tooltipLabel = pointLabel ?? (label != null ? formatDateAxisLabel(label, { includeYear: true }) : null);

  return (
    <div className="chart-tooltip" role="presentation">
      {tooltipLabel != null ? <div className="chart-tooltip-label">{tooltipLabel}</div> : null}
      <div className="chart-tooltip-items">
        {items.map((item, index) => {
          const color = getItemColor?.(item, index) ?? tooltipItemColor(chart, item, index);
          const itemName = tooltipItemName(chart, item);
          const key = `${String(item.dataKey ?? item.name)}-${String(item.value)}`;
          return (
            <div className="chart-tooltip-item" key={key}>
              <span
                aria-hidden="true"
                className="chart-tooltip-marker"
                style={{ background: color }}
              />
              {itemName ? <span className="chart-tooltip-name">{itemName}</span> : null}
              <span className="chart-tooltip-value">
                {tooltipItemValue(chart, item, visibleTotal)}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export function BoxPlotTooltip({
  active,
  chart,
  label,
  payload = [],
}: {
  active?: boolean;
  chart: ChartSpec;
  label?: unknown;
  payload?: ChartTooltipPayloadItem[];
}) {
  const row = payload[0]?.payload as Record<string, number> | undefined;
  if (!active || !row) return null;
  const items: Array<[string, number]> = [
    ["Max", row.__boxMax],
    ["Q3", row.__boxQ3],
    ["Median", row.__boxMedian],
    ["Q1", row.__boxQ1],
    ["Min", row.__boxMin],
  ];
  return (
    <div className="chart-tooltip" role="presentation">
      {label != null ? <div className="chart-tooltip-label">{formatDateAxisLabel(label, { includeYear: true })}</div> : null}
      <div className="chart-tooltip-items">
        {items.map(([name, value]) => (
          <div className="chart-tooltip-item" key={name}>
            <span aria-hidden="true" className="chart-tooltip-marker" style={{ background: "var(--ds-chart-series-blue)" }} />
            <span className="chart-tooltip-name">{name}</span>
            <span className="chart-tooltip-value">{formatValue(value, chart.valueFormat, chart.unit)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function WaterfallTooltip({
  active,
  chart,
  label,
  payload = [],
}: {
  active?: boolean;
  chart: ChartSpec;
  label?: unknown;
  payload?: ChartTooltipPayloadItem[];
}) {
  const row = payload[0]?.payload as Record<string, number | boolean> | undefined;
  if (!active || !row) return null;
  const color = row.__waterfallIsPositive ? "var(--ds-chart-series-green)" : "var(--ds-chart-series-red)";
  return (
    <div className="chart-tooltip" role="presentation">
      {label != null ? <div className="chart-tooltip-label">{formatDateAxisLabel(label, { includeYear: true })}</div> : null}
      <div className="chart-tooltip-items">
        <div className="chart-tooltip-item">
          <span aria-hidden="true" className="chart-tooltip-marker" style={{ background: color }} />
          <span className="chart-tooltip-name">{chart.series[0]?.label ?? chart.series[0]?.field}</span>
          <span className="chart-tooltip-value">{formatValue(row.__waterfallValue, chart.valueFormat, chart.unit)}</span>
        </div>
        <div className="chart-tooltip-item">
          <span aria-hidden="true" className="chart-tooltip-marker" style={{ background: "var(--ds-chart-series-neutral)" }} />
          <span className="chart-tooltip-name">Running total</span>
          <span className="chart-tooltip-value">{formatValue(row.__waterfallEnd, chart.valueFormat, chart.unit)}</span>
        </div>
      </div>
    </div>
  );
}
