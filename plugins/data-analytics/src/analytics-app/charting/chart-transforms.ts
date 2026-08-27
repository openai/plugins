import type { ChartSeriesSpec, ChartSpec, ValueFormat } from "./chart-contract";

export type ChartDataRow = Record<string, string | number | boolean | [number, number] | null | undefined>;

export const PERCENT_AXIS_TICKS = [0, 0.25, 0.5, 0.75, 1];
const Y_AXIS_TICK_COUNT = 5;
const COMPACT_VALUE_THRESHOLD = 100_000;
const DATE_AXIS_MIN_TICKS = 5;
const DATE_AXIS_MAX_TICKS = 10;
const DATE_AXIS_ESTIMATED_TICK_WIDTH = 90;

export function asNumber(value: unknown): number | null {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string" && value.trim() !== "") {
    const numeric = Number(value);
    if (Number.isFinite(numeric)) return numeric;
  }
  return null;
}

export function asFiniteNumber(value: unknown, fallback = 0): number {
  return asNumber(value) ?? fallback;
}

export function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

function isUsdUnit(unit: string): boolean {
  return unit === "$" || unit.toUpperCase() === "USD";
}

function unitScaleSuffix(unit: string): string | null {
  const normalized = unit.toLowerCase();
  if (normalized === "usd millions" || normalized === "usd million") return "M";
  if (normalized === "usd billions" || normalized === "usd billion") return "B";
  if (normalized === "usd thousands" || normalized === "usd thousand") return "K";
  if (/^\$[kmbt]$/i.test(unit)) return unit.slice(1).toUpperCase();
  return null;
}

function compactDigits(value: number): number {
  const absolute = Math.abs(value);
  if (absolute >= COMPACT_VALUE_THRESHOLD) return 1;
  return 2;
}

function formatPlainNumber(value: number, compact = false): string {
  const absolute = Math.abs(value);
  return new Intl.NumberFormat(undefined, {
    maximumFractionDigits: compactDigits(value),
    notation: compact && absolute >= COMPACT_VALUE_THRESHOLD ? "compact" : "standard",
  }).format(value);
}

function formatCurrency(value: number): string {
  const absolute = Math.abs(value);
  return new Intl.NumberFormat(undefined, {
    currency: "USD",
    maximumFractionDigits: compactDigits(value),
    notation: absolute >= COMPACT_VALUE_THRESHOLD ? "compact" : "standard",
    style: "currency",
  }).format(value);
}

function isPercentWordUnit(unit: string): boolean {
  const normalized = unit.toLowerCase();
  return normalized === "percent" || normalized === "percentage";
}

export function formatValue(value: unknown, format: ValueFormat = "compact", unit?: string): string {
  const numeric = asNumber(value);
  if (numeric == null) return value == null ? "n/a" : String(value);
  const cleanUnit = unit?.trim();
  if (format === "percent" && cleanUnit === "%") {
    return new Intl.NumberFormat(undefined, {
      maximumFractionDigits: 1,
      style: "percent",
    }).format(numeric);
  }
  if (cleanUnit) {
    if (isPercentWordUnit(cleanUnit)) {
      return new Intl.NumberFormat(undefined, {
        maximumFractionDigits: 1,
        style: "percent",
      }).format(numeric);
    }
    if (cleanUnit === "%" || cleanUnit.startsWith("%")) return `${formatPlainNumber(numeric)}%`;
    if (isUsdUnit(cleanUnit)) return formatCurrency(numeric);
    const scaleSuffix = unitScaleSuffix(cleanUnit);
    if (scaleSuffix) return `$${formatPlainNumber(numeric)}${scaleSuffix}`;
    if (cleanUnit.startsWith("$")) return `$${formatPlainNumber(numeric)}${cleanUnit.slice(1)}`;
    return `${formatPlainNumber(numeric, format === "compact")} ${cleanUnit}`;
  }
  if (format === "percent") {
    return new Intl.NumberFormat(undefined, {
      maximumFractionDigits: 1,
      style: "percent",
    }).format(numeric);
  }
  if (format === "currency") {
    return formatCurrency(numeric);
  }
  if (format === "number") {
    return formatPlainNumber(numeric);
  }
  return formatPlainNumber(numeric, true);
}

export function isDateAxisValue(value: unknown): value is string {
  return dateAxisParts(value) != null;
}

function dateAxisParts(value: unknown): { day: number; granularity: "day"; month: number; year: number } | { granularity: "month"; month: number; year: number } | null {
  if (typeof value !== "string") return null;
  const trimmed = value.trim();
  const match = trimmed.match(/^(\d{4})-(\d{2})-(\d{2})(?:$|[T\s])/);
  if (!match) {
    const monthMatch = trimmed.match(/^(\d{4})-(\d{2})$/);
    if (!monthMatch) return null;
    const [, monthYear, monthValue] = monthMatch;
    const monthParts = {
      granularity: "month" as const,
      month: Number(monthValue),
      year: Number(monthYear),
    };
    const date = new Date(Date.UTC(monthParts.year, monthParts.month - 1, 1));
    if (date.getUTCFullYear() !== monthParts.year || date.getUTCMonth() !== monthParts.month - 1) {
      return null;
    }
    return monthParts;
  }
  const [, year, month, day] = match;
  const parts = {
    day: Number(day),
    granularity: "day" as const,
    month: Number(month),
    year: Number(year),
  };
  const date = new Date(Date.UTC(parts.year, parts.month - 1, parts.day));
  if (
    date.getUTCFullYear() !== parts.year ||
    date.getUTCMonth() !== parts.month - 1 ||
    date.getUTCDate() !== parts.day
  ) {
    return null;
  }
  return parts;
}

export function formatDateAxisLabel(value: unknown, options: { includeYear?: boolean } = {}): string {
  const parts = dateAxisParts(value);
  if (!parts) return value == null ? "" : String(value);
  if (parts.granularity === "month") {
    return new Intl.DateTimeFormat(undefined, {
      month: "short",
      timeZone: "UTC",
      year: "numeric",
    }).format(new Date(Date.UTC(parts.year, parts.month - 1, 1)));
  }
  return new Intl.DateTimeFormat(undefined, {
    day: "numeric",
    month: "short",
    timeZone: "UTC",
    year: options.includeYear ? "numeric" : undefined,
  }).format(new Date(Date.UTC(parts.year, parts.month - 1, parts.day)));
}

function uniqueOrderedValues(values: string[]): string[] {
  const seen = new Set<string>();
  const unique: string[] = [];
  for (const value of values) {
    if (seen.has(value)) continue;
    seen.add(value);
    unique.push(value);
  }
  return unique;
}

function targetDateAxisTickCount(valueCount: number, availableWidth: number): number {
  if (valueCount <= 7) return valueCount;
  const widthTarget = Math.floor(availableWidth / DATE_AXIS_ESTIMATED_TICK_WIDTH);
  return clamp(widthTarget, DATE_AXIS_MIN_TICKS, Math.min(valueCount, DATE_AXIS_MAX_TICKS));
}

export function getDateAxisTicks(rows: ChartDataRow[], xField: string, availableWidth = 760): string[] | undefined {
  const values = uniqueOrderedValues(
    rows
      .map((row) => row[xField])
      .filter((value): value is string => typeof value === "string"),
  );
  if (values.length === 0 || !values.every(isDateAxisValue)) return undefined;
  if (values.length === 1) return values;
  const targetCount = targetDateAxisTickCount(values.length, availableWidth);
  if (targetCount >= values.length) return values;

  const lastIndex = values.length - 1;
  const step = Math.max(1, Math.ceil(lastIndex / Math.max(1, targetCount - 1)));
  const ticks = values.filter((_, index) => index % step === 0);
  const last = values[lastIndex];
  if (ticks[ticks.length - 1] !== last) ticks.push(last);
  return ticks;
}

function niceAxisStep(value: number): number {
  if (!Number.isFinite(value) || value <= 0) return 1;
  const magnitude = 10 ** Math.floor(Math.log10(value));
  const normalized = value / magnitude;
  const niceStep = [1, 1.5, 2, 2.5, 3, 4, 5, 7.5, 9, 10].find(
    (candidate) => normalized <= candidate,
  );
  return (niceStep ?? 10) * magnitude;
}

export function getYAxisScaleForSeries(
  chart: ChartSpec,
  rows: ChartDataRow[],
  seriesList: ChartSeriesSpec[],
): { labels: string[]; ticks: number[] } {
  const barGroupMode = chart.settings?.groupMode;
  const normalizedStackedBars =
    chart.type === "stackedBar100" ||
    chart.type === "horizontalStackedBar100" ||
    (chart.type === "bar" && barGroupMode === "stacked100");
  const stackedBars =
    chart.type === "stackedBar" ||
    chart.type === "horizontalStackedBar" ||
    (chart.type === "bar" && (barGroupMode === "stacked" || barGroupMode === "stacked100"));

  if (normalizedStackedBars) {
    return {
      labels: PERCENT_AXIS_TICKS.map((value) => formatValue(value, "percent")),
      ticks: PERCENT_AXIS_TICKS,
    };
  }

  const values: number[] = [0];
  for (const row of rows) {
    if (chart.type === "stackedArea" || stackedBars) {
      let positiveTotal = 0;
      let negativeTotal = 0;
      for (const series of seriesList) {
        const value = asNumber(row[series.field]);
        if (value == null) continue;
        if (value >= 0) positiveTotal += value;
        else negativeTotal += value;
      }
      values.push(positiveTotal, negativeTotal);
    } else {
      for (const series of seriesList) {
        const value = asNumber(row[series.field]);
        if (value != null) values.push(value);
      }
    }
  }

  const min = Math.min(...values);
  const max = Math.max(...values);
  const roughTickStep = niceAxisStep((max - min) / Math.max(1, Y_AXIS_TICK_COUNT - 1));
  const axisMin = min < 0 ? Math.floor(min / roughTickStep) * roughTickStep : 0;
  const tickStep = niceAxisStep((max - axisMin) / Math.max(1, Y_AXIS_TICK_COUNT - 1));
  const axisMax = max > 0 ? Math.ceil(max / tickStep) * tickStep : 0;
  const tickSlots = Math.max(1, Math.round((axisMax - axisMin) / tickStep));
  const ticks =
    axisMin === axisMax
      ? [axisMin]
      : Array.from({ length: tickSlots + 1 }, (_, index) => axisMin + tickStep * index);
  return {
    labels: ticks.map((value) => formatValue(value, chart.valueFormat)),
    ticks,
  };
}

export type BoxPlotDataRow = ChartDataRow & {
  __boxMax: number;
  __boxMedian: number;
  __boxMin: number;
  __boxQ1: number;
  __boxQ3: number;
  __boxRange: [number, number];
};

export function buildBoxPlotRows(chart: ChartSpec, rows: ChartDataRow[]): BoxPlotDataRow[] {
  const [minSeries, q1Series, medianSeries, q3Series, maxSeries] = chart.series;
  return rows.map((row) => {
    const min = asFiniteNumber(row[minSeries?.field ?? ""]);
    const q1 = asFiniteNumber(row[q1Series?.field ?? ""], min);
    const median = asFiniteNumber(row[medianSeries?.field ?? ""], q1);
    const q3 = asFiniteNumber(row[q3Series?.field ?? ""], median);
    const max = asFiniteNumber(row[maxSeries?.field ?? ""], q3);
    return {
      ...row,
      __boxMax: max,
      __boxMedian: median,
      __boxMin: min,
      __boxQ1: q1,
      __boxQ3: q3,
      __boxRange: [q1, q3],
    };
  });
}

export function getBoxPlotXAxisScale(rows: BoxPlotDataRow[]): { domain: [number, number]; ticks: number[] } {
  const values = rows.flatMap((row) => [row.__boxMin, row.__boxMax]);
  const min = Math.min(0, ...values);
  const max = Math.max(0, ...values);
  const roughTickStep = niceAxisStep((max - min) / Math.max(1, Y_AXIS_TICK_COUNT - 1));
  const axisMin = min < 0 ? Math.floor(min / roughTickStep) * roughTickStep : 0;
  const tickStep = niceAxisStep((max - axisMin) / Math.max(1, Y_AXIS_TICK_COUNT - 1));
  const axisMax = max > 0 ? Math.ceil(max / tickStep) * tickStep : 0;
  if (axisMin === axisMax) {
    const fallbackMax = axisMin + tickStep;
    return { domain: [axisMin, fallbackMax], ticks: [axisMin, fallbackMax] };
  }
  const tickSlots = Math.max(1, Math.round((axisMax - axisMin) / tickStep));
  const ticks = Array.from({ length: tickSlots + 1 }, (_, index) => axisMin + tickStep * index);
  return { domain: [axisMin, axisMax], ticks };
}

export type WaterfallDataRow = ChartDataRow & {
  __waterfallEnd: number;
  __waterfallIsLast: boolean;
  __waterfallIsPositive: boolean;
  __waterfallRange: [number, number];
  __waterfallRowCount: number;
  __waterfallStart: number;
  __waterfallValue: number;
};

export function buildWaterfallRows(chart: ChartSpec, rows: ChartDataRow[]): WaterfallDataRow[] {
  const series = chart.series[0];
  let running = 0;
  return rows.map((row, index) => {
    const value = asFiniteNumber(row[series?.field ?? ""]);
    const start = running;
    const end = start + value;
    running = end;
    return {
      ...row,
      __waterfallEnd: end,
      __waterfallIsLast: index === rows.length - 1,
      __waterfallIsPositive: value >= 0,
      __waterfallRange: [Math.min(start, end), Math.max(start, end)],
      __waterfallRowCount: rows.length,
      __waterfallStart: start,
      __waterfallValue: value,
    };
  });
}

const WATERFALL_NARROW_AXIS_RATIO = 4;
const WATERFALL_AXIS_PADDING_RATIO = 0.12;

export function getWaterfallYAxisScale(
  rows: WaterfallDataRow[],
): { domain: [number, number]; ticks: number[] } | undefined {
  const points = rows
    .flatMap((row) => [row.__waterfallStart, row.__waterfallEnd])
    .filter((value) => Number.isFinite(value));
  const nonZeroPoints = points.filter((value) => value !== 0);
  if (nonZeroPoints.length < 2) return undefined;

  const min = Math.min(...points, 0);
  const max = Math.max(...points, 0);
  const focusedMin = Math.min(...nonZeroPoints);
  const focusedMax = Math.max(...nonZeroPoints);
  const focusedSpan = focusedMax - focusedMin;
  const fullSpan = max - min;
  const sameSideOfZero = focusedMin > 0 || focusedMax < 0;
  if (!sameSideOfZero || focusedSpan <= 0 || fullSpan / focusedSpan < WATERFALL_NARROW_AXIS_RATIO) {
    return undefined;
  }

  const padding = Math.max(
    focusedSpan * WATERFALL_AXIS_PADDING_RATIO,
    niceAxisStep(focusedSpan / Math.max(1, Y_AXIS_TICK_COUNT - 1)) / 2,
  );
  const paddedMin = focusedMin - padding;
  const paddedMax = focusedMax + padding;
  const tickStep = niceAxisStep((paddedMax - paddedMin) / Math.max(1, Y_AXIS_TICK_COUNT - 1));
  const axisMin = Math.floor(paddedMin / tickStep) * tickStep;
  const axisMax = Math.ceil(paddedMax / tickStep) * tickStep;
  if (!Number.isFinite(axisMin) || !Number.isFinite(axisMax) || axisMin === axisMax) return undefined;

  const tickSlots = Math.max(1, Math.round((axisMax - axisMin) / tickStep));
  return {
    domain: [axisMin, axisMax],
    ticks: Array.from({ length: tickSlots + 1 }, (_, index) => axisMin + tickStep * index),
  };
}

export function buildPieRows(chart: ChartSpec, rows: ChartDataRow[]): ChartDataRow[] {
  if (chart.series.length > 1) {
    return chart.series
      .map((series, index) => ({
        __pieIndex: index,
        __pieField: series.field,
        __pieName: String(series.label ?? series.field),
        __pieValue: rows.reduce((sum, row) => sum + Math.max(0, asNumber(row[series.field]) ?? 0), 0),
      }))
      .filter((row) => Number(row.__pieValue) > 0);
  }
  const series = chart.series[0];
  return rows
    .map((row, index) => ({
      ...row,
      __pieIndex: index,
      __pieName: formatDateAxisLabel(row[chart.xField]),
      __pieValue: Math.max(0, asNumber(row[series?.field ?? ""]) ?? 0),
    }))
    .filter((row) => asNumber(row.__pieValue) != null && Number(row.__pieValue) > 0);
}

export function buildFunnelRows(chart: ChartSpec, rows: ChartDataRow[], getStageColor: (index: number, rowCount: number) => string): ChartDataRow[] {
  const series = chart.series[0];
  return rows.map((row, index) => {
    const value = asNumber(row[series?.field ?? ""]) ?? 0;
    const baseline = (asNumber(rows[0]?.[series?.field ?? ""]) ?? value) || 1;
    return {
      ...row,
      __funnelIndex: index,
      __funnelLabel: formatDateAxisLabel(row[chart.xField]),
      __funnelPairLabel: `${formatDateAxisLabel(row[chart.xField])}\u0000${formatValue(value, chart.valueFormat, chart.unit)}`,
      __funnelRowCount: rows.length,
      __funnelShareLabel: index === 0 ? "100%" : formatValue(value / baseline, "percent"),
      __funnelStageColor: getStageColor(index, rows.length),
      __funnelValueLabel: formatValue(value, chart.valueFormat, chart.unit),
    };
  });
}

export function chartEmptyMessage(chart: ChartSpec, rows: ChartDataRow[], visibleFields?: Set<string>): string {
  if (!rows.length) return chart.emptyState || "No rows match the selected filters.";
  const visibleSeries = chart.series.filter(
    (series) => !visibleFields || !visibleFields.size || visibleFields.has(series.field),
  );
  if (chart.series.length && !visibleSeries.length) return "No visible series selected.";
  if (chart.type === "scatter" && !rows.some((row) => asNumber(row[chart.xField]) != null && visibleSeries.some((series) => asNumber(row[series.field]) != null))) {
    return "Scatter plots need numeric x and y values.";
  }
  if (chart.type === "histogram" && !rows.some((row) => asNumber(row[chart.series[0]?.field ?? chart.xField]) != null)) {
    return "Histogram needs numeric values.";
  }
  if (chart.type === "pie" && !buildPieRows(chart, rows).length) return "Pie charts need positive values.";
  if ((chart.type === "line" || chart.type === "area" || chart.type === "stackedArea" || chart.type === "sparkline") && new Set(rows.map((row) => String(row[chart.xField] ?? ""))).size < 2) {
    return `${chart.type === "stackedArea" ? "Stacked area" : "Trend"} charts need at least two x values.`;
  }
  return "";
}
