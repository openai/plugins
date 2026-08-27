import {
  Fragment,
  type CSSProperties,
  type ReactNode,
  type SVGProps,
  useCallback,
  useLayoutEffect,
  useRef,
  useState,
} from "react";
import { createPortal } from "react-dom";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Funnel,
  FunnelChart,
  LabelList,
  Line,
  LineChart,
  Pie,
  PieChart,
  ReferenceLine,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from "recharts";

import type { ChartSeriesSpec, ChartSpec, ChartSurface, ChartValueLabelMode } from "./chart-contract";
import { ChartFrame } from "./ChartFrame";
import { BoxPlotTooltip, ChartTooltip, type ChartTooltipPayloadItem, WaterfallTooltip } from "./ChartTooltip";
import {
  asFiniteNumber,
  asNumber,
  buildBoxPlotRows,
  buildFunnelRows,
  buildPieRows,
  buildWaterfallRows,
  chartEmptyMessage,
  clamp,
  formatDateAxisLabel,
  formatValue,
  getBoxPlotXAxisScale,
  getDateAxisTicks,
  getWaterfallYAxisScale,
  getYAxisScaleForSeries,
  type ChartDataRow,
  type WaterfallDataRow,
} from "./chart-transforms";
import {
  colorForSeries,
  FUNNEL_STAGE_COLORS,
  HEATMAP_BLUE_SCALE,
  isHorizontalChartType,
  isNormalizedStackedChartType,
  isStackedChartType,
} from "./chart-theme";
import { chartEncodingField, rechartsChartFromEncodedSpec } from "./chart-app-helpers";
import { calculateViewportTooltipPosition, type ViewportTooltipPosition } from "./tooltipPositioning";

const AXIS_LABEL_GAP = 8;
const RECHARTS_AXIS_TICK_SIZE = 6;
const RECHARTS_AXIS_TICK_MARGIN = AXIS_LABEL_GAP - RECHARTS_AXIS_TICK_SIZE;
const Y_AXIS_TICK_LABEL_OVERHANG = 8;
const CHART_COMPACT_HEIGHT = 240;
const CHART_CARD_DEFAULT_HEIGHT = 320;
const CHART_CARD_ROTATED_CATEGORY_HEIGHT = 400;
const CHART_FULLSCREEN_HEIGHT = 520;
const CHART_STATIC_WIDTH = 760;
const CHART_MIN_PLOT_HEIGHT = 180;
const CHART_LEGEND_RESERVED_HEIGHT = 28;
const CHART_HORIZONTAL_BAR_ROW_HEIGHT = 28;
const COMPLEX_CHART_GRID_GAP = 4;
const COMPLEX_CHART_MIN_ROW_HEIGHT = 28;
const HEATMAP_HEADER_ROW_HEIGHT = 24;
const FUNNEL_CORNER_RADIUS = 7;
const FUNNEL_LABEL_GAP = 6;
const FUNNEL_SEGMENT_GAP = 4;
const SCATTER_AUTO_LABEL_LIMIT = 20;
const CATEGORY_X_AXIS_LABEL_ROTATION_DEGREES = -40;
const CATEGORY_X_AXIS_LONG_LABEL_LENGTH = 16;
const CATEGORY_X_AXIS_LONG_AVERAGE_LABEL_LENGTH = 11;
const CATEGORY_X_AXIS_ROTATED_HEIGHT = 82;
const CATEGORY_X_AXIS_ROTATED_HEIGHT_WITH_TITLE = 96;
const CATEGORY_X_AXIS_ROTATED_TICK_MARGIN = 10;
const CATEGORY_X_AXIS_WRAPPED_HEIGHT = 38;
const CATEGORY_X_AXIS_WRAPPED_HEIGHT_WITH_TITLE = 48;
const CATEGORY_X_AXIS_WRAPPED_TICK_MARGIN = 6;
const CATEGORY_X_AXIS_ESTIMATED_CHAR_WIDTH = 7;
const CATEGORY_X_AXIS_LABEL_SLOT_GAP = 16;
const CATEGORY_X_AXIS_MIN_VISIBLE_TICK_SPACING = 72;
const BAR_AUTO_VALUE_LABEL_LIMIT = 8;
const BAR_VALUE_LABEL_OFFSET = 8;
const BAR_NEGATIVE_VALUE_LABEL_OFFSET = 18;
const BAR_VALUE_LABEL_HORIZONTAL_GUTTER = 56;
const BAR_VALUE_LABEL_VERTICAL_GUTTER = 34;
const BAR_NEGATIVE_VALUE_LABEL_AXIS_GUTTER = 40;

type AxisTickCoordinate = number | string;

type AxisTickProps = {
  payload?: { value?: unknown };
  textAnchor?: "end" | "inherit" | "middle" | "start";
  x?: AxisTickCoordinate;
  y?: AxisTickCoordinate;
};

type WaterfallBarShapeProps = {
  height?: number | string;
  isActive?: boolean;
  parentViewBox?: { width?: number };
  payload?: WaterfallDataRow;
  width?: number | string;
  x?: number | string;
  y?: number | string;
};

type SvgPoint = {
  x: number;
  y: number;
};

type FunnelShapeProps = {
  className?: string;
  fill?: string;
  height?: number | string;
  labelViewBox?: FunnelViewBox;
  lowerWidth?: number | string;
  name?: unknown;
  option?: unknown;
  parentViewBox?: unknown;
  payload?: ChartDataRow;
  shapeType?: unknown;
  stroke?: string;
  strokeWidth?: number | string;
  tooltipPayload?: unknown;
  tooltipPosition?: unknown;
  upperWidth?: number | string;
  val?: unknown;
  value?: unknown;
  width?: number | string;
  x?: number | string;
  y?: number | string;
};

type FunnelViewBox = {
  height?: number | string;
  lowerWidth?: number | string;
  upperWidth?: number | string;
  width?: number | string;
  x?: number | string;
  y?: number | string;
};

type FunnelLabelProps = {
  height?: number | string;
  payload?: ChartDataRow;
  value?: unknown;
  viewBox?: {
    height?: number | string;
    width?: number | string;
    x?: number | string;
    y?: number | string;
  };
  width?: number | string;
  x?: number | string;
  y?: number | string;
};

type BarValueLabelProps = {
  height?: number | string;
  value?: unknown;
  width?: number | string;
  x?: number | string;
  y?: number | string;
};

type BarValueLabelSides = {
  hasNegative: boolean;
  hasNonNegative: boolean;
};

type BarSignState = {
  hasNegative: boolean;
  hasPositive: boolean;
  hasZero: boolean;
};

function chartHeightForSurface(surface: ChartSurface, height?: number | string): number | string | undefined {
  if (height != null) return height;
  if (surface === "explorer") return CHART_FULLSCREEN_HEIGHT;
  return undefined;
}

function chartCardHeightForContent({
  hasLegend,
  horizontal,
  rotateCategoryXAxisLabels,
  rowCount,
}: {
  hasLegend: boolean;
  horizontal: boolean;
  rotateCategoryXAxisLabels: boolean;
  rowCount: number;
}): number {
  const legendReserve = hasLegend ? CHART_LEGEND_RESERVED_HEIGHT : 0;

  if (horizontal) {
    return Math.max(
      CHART_CARD_DEFAULT_HEIGHT,
      Math.max(1, rowCount) * CHART_HORIZONTAL_BAR_ROW_HEIGHT + legendReserve + 96,
    );
  }

  if (rotateCategoryXAxisLabels) {
    return CHART_CARD_ROTATED_CATEGORY_HEIGHT + legendReserve;
  }

  return CHART_CARD_DEFAULT_HEIGHT + legendReserve;
}

function chartFrameHeightForContent({
  hasLegend,
  height,
  horizontal,
  rotateCategoryXAxisLabels,
  rowCount,
  surface,
}: {
  hasLegend: boolean;
  height?: number | string;
  horizontal: boolean;
  rotateCategoryXAxisLabels: boolean;
  rowCount: number;
  surface: ChartSurface;
}): number | string | undefined {
  const requestedHeight = chartHeightForSurface(surface, height);
  if (requestedHeight != null) return requestedHeight;
  if (surface !== "card") return requestedHeight;

  return chartCardHeightForContent({
    hasLegend,
    horizontal,
    rotateCategoryXAxisLabels,
    rowCount,
  });
}

function numericChartDimension(value: number | string | undefined, fallback: number): number {
  if (typeof value === "number" && Number.isFinite(value) && value > 0) return value;
  if (typeof value === "string") {
    const parsed = Number(value);
    if (Number.isFinite(parsed) && parsed > 0) return parsed;
  }
  return fallback;
}

function complexChartFrameHeight({
  height,
  rowCount,
  surface,
  headerRows = 0,
}: {
  height?: number | string;
  rowCount: number;
  surface: ChartSurface;
  headerRows?: number;
}): number | string | undefined {
  const requestedHeight = chartHeightForSurface(surface, height);
  if (typeof requestedHeight === "string" && Number.isNaN(Number(requestedHeight))) {
    return requestedHeight;
  }
  const defaultHeight = surface === "explorer" ? CHART_FULLSCREEN_HEIGHT : CHART_COMPACT_HEIGHT;
  const baseHeight = numericChartDimension(requestedHeight, defaultHeight);
  const visibleRows = Math.max(0, rowCount);
  const visibleHeaderRows = Math.max(0, headerRows);
  const rowSlots = visibleRows + visibleHeaderRows;
  const minimumContentHeight =
    visibleHeaderRows * HEATMAP_HEADER_ROW_HEIGHT +
    visibleRows * COMPLEX_CHART_MIN_ROW_HEIGHT +
    Math.max(0, rowSlots - 1) * COMPLEX_CHART_GRID_GAP;

  return Math.max(baseHeight, minimumContentHeight);
}

function NumericYAxisTick({
  payload,
  textAnchor = "end",
  valueFormat = "compact",
  x = 0,
  y = 0,
}: AxisTickProps & { valueFormat?: ChartSpec["valueFormat"] }) {
  const numericX = typeof x === "number" ? x : Number(x) || 0;
  const numericY = typeof y === "number" ? y : Number(y) || 0;
  return (
    <text
      className="recharts-cartesian-axis-tick-value chart-axis-number"
      dominantBaseline="middle"
      textAnchor={textAnchor}
      x={numericX}
      y={numericY}
    >
      {formatValue(payload?.value, valueFormat)}
    </text>
  );
}

function XAxisEndpointTick({
  firstTick,
  lastTick,
  payload,
  x = 0,
  y = 0,
}: AxisTickProps & { firstTick?: string; lastTick?: string }) {
  const value = String(payload?.value ?? "");
  const numericX = typeof x === "number" ? x : Number(x) || 0;
  const textAnchor = value === firstTick ? "start" : value === lastTick ? "end" : "middle";
  return (
    <text
      className="recharts-cartesian-axis-tick-value"
      dominantBaseline="hanging"
      textAnchor={textAnchor}
      x={numericX}
      y={y}
    >
      {formatDateAxisLabel(value)}
    </text>
  );
}

function truncateCategoryAxisLabel(value: string, maxLength: number): string {
  const safeMaxLength = Math.max(1, Math.floor(maxLength));
  if (value.length <= safeMaxLength) return value;
  if (safeMaxLength === 1) return "…";
  return `${value.slice(0, safeMaxLength - 1).trimEnd()}…`;
}

function balancedCategoryAxisLabelSplit(value: string): [string, string] {
  const midpoint = value.length / 2;
  const wordBreaks = [...value.matchAll(/\s+/g)]
    .map((match) => match.index)
    .filter((index): index is number => index > 0 && index < value.length);
  const splitIndex = wordBreaks.length
    ? wordBreaks.reduce((best, index) =>
        Math.abs(index - midpoint) < Math.abs(best - midpoint) ? index : best,
      )
    : Math.ceil(midpoint);
  return [value.slice(0, splitIndex).trimEnd(), value.slice(splitIndex).trimStart()];
}

function wrapCategoryAxisLabel(value: string, maxLength: number): string[] {
  const normalized = value.trim();
  const safeMaxLength = Math.max(1, Math.floor(maxLength));
  if (!normalized || normalized.length <= safeMaxLength) return [normalized];
  return balancedCategoryAxisLabelSplit(normalized)
    .map((line) => truncateCategoryAxisLabel(line, safeMaxLength))
    .filter(Boolean);
}

function WrappedCategoryXAxisTick({
  maxLineLength,
  payload,
  x = 0,
  y = 0,
}: AxisTickProps & { maxLineLength: number }) {
  const numericX = typeof x === "number" ? x : Number(x) || 0;
  const value = String(payload?.value ?? "");
  const lines = wrapCategoryAxisLabel(value, maxLineLength);
  return (
    <text
      className="recharts-cartesian-axis-tick-value"
      dominantBaseline="hanging"
      textAnchor="middle"
      x={numericX}
      y={y}
    >
      {lines.some((line) => line.includes("…")) ? <title>{value}</title> : null}
      {lines.map((line, index) => (
        <tspan dy={index === 0 ? 0 : "1.2em"} key={`${line}-${index}`} x={numericX}>
          {line}
        </tspan>
      ))}
    </text>
  );
}

function categoryXAxisLabels(chart: ChartSpec, rows: ChartDataRow[]): string[] {
  return [
    ...new Set(
      rows
        .map((row) => row[chart.xField])
        .filter((value) => value != null)
        .map((value) => String(value)),
    ),
  ];
}

function categoryXAxisLabelSlotWidth(labels: string[], availableWidth: number): number {
  return Math.max(
    0,
    availableWidth / Math.max(1, labels.length) - CATEGORY_X_AXIS_LABEL_SLOT_GAP,
  );
}

function shouldRotateCategoryXAxisLabels({
  chart,
  horizontal,
  xAxisTicks,
}: {
  chart: ChartSpec;
  horizontal: boolean;
  xAxisTicks?: string[];
}): boolean {
  if (horizontal || xAxisTicks?.length) return false;
  return chart.settings?.categoryLabelPolicy === "rotate";
}

function shouldWrapCategoryXAxisLabels({
  availableWidth,
  chart,
  horizontal,
  rows,
  xAxisTicks,
}: {
  availableWidth: number;
  chart: ChartSpec;
  horizontal: boolean;
  rows: ChartDataRow[];
  xAxisTicks?: string[];
}): boolean {
  if (horizontal || xAxisTicks?.length) return false;
  const labelPolicy = chart.settings?.categoryLabelPolicy;
  if (labelPolicy === "wrap") return true;
  if (labelPolicy === "rotate" || labelPolicy === "truncate") return false;

  const labels = categoryXAxisLabels(chart, rows);
  if (labels.length < 2) return false;

  const maxLength = Math.max(...labels.map((label) => label.length));
  const longestLabelWidth = maxLength * CATEGORY_X_AXIS_ESTIMATED_CHAR_WIDTH;
  const labelSlotWidth = categoryXAxisLabelSlotWidth(labels, availableWidth);
  if (longestLabelWidth <= labelSlotWidth) return false;

  if (maxLength >= CATEGORY_X_AXIS_LONG_LABEL_LENGTH) return true;

  const averageLength =
    labels.reduce((total, label) => total + label.length, 0) / labels.length;
  return labels.length >= 4 && averageLength >= CATEGORY_X_AXIS_LONG_AVERAGE_LABEL_LENGTH;
}

function categoryXAxisWrappedLineLength(chart: ChartSpec, rows: ChartDataRow[], availableWidth: number): number {
  const slotWidth = categoryXAxisLabelSlotWidth(categoryXAxisLabels(chart, rows), availableWidth);
  return Math.max(1, Math.floor(slotWidth / CATEGORY_X_AXIS_ESTIMATED_CHAR_WIDTH));
}

function sparseCategoryXAxisTicks({
  availableWidth,
  chart,
  horizontal,
  rotateCategoryXAxisLabels,
  rows,
  wrapCategoryXAxisLabels,
  xAxisTicks,
}: {
  availableWidth: number;
  chart: ChartSpec;
  horizontal: boolean;
  rotateCategoryXAxisLabels: boolean;
  rows: ChartDataRow[];
  wrapCategoryXAxisLabels: boolean;
  xAxisTicks?: string[];
}): string[] | undefined {
  if (horizontal || xAxisTicks?.length || (!rotateCategoryXAxisLabels && !wrapCategoryXAxisLabels)) {
    return xAxisTicks;
  }
  const labels = categoryXAxisLabels(chart, rows);
  if (labels.length <= 2) return undefined;
  const maxVisibleTicks = Math.max(2, Math.floor(availableWidth / CATEGORY_X_AXIS_MIN_VISIBLE_TICK_SPACING));
  if (labels.length <= maxVisibleTicks) return undefined;

  const lastIndex = labels.length - 1;
  const step = Math.max(1, Math.ceil(lastIndex / Math.max(1, maxVisibleTicks - 1)));
  const ticks = labels.filter((_, index) => index % step === 0);
  const last = labels[lastIndex];
  if (ticks[ticks.length - 1] !== last) ticks.push(last);
  return ticks;
}

function getFunnelStageColor(index: number, rowCount: number): string {
  const colorIndex = Math.round(
    (index * (FUNNEL_STAGE_COLORS.length - 1)) / Math.max(1, rowCount - 1),
  );
  return FUNNEL_STAGE_COLORS[clamp(colorIndex, 0, FUNNEL_STAGE_COLORS.length - 1)];
}

function getHeatmapFill(intensity: number): string {
  const index = clamp(
    Math.floor(intensity * HEATMAP_BLUE_SCALE.length),
    0,
    HEATMAP_BLUE_SCALE.length - 1,
  );
  return HEATMAP_BLUE_SCALE[index] ?? HEATMAP_BLUE_SCALE[0];
}

function formatSvgNumber(value: number): string {
  return Number.isInteger(value) ? String(value) : value.toFixed(3).replace(/\.?0+$/, "");
}

function getPointDistance(from: SvgPoint, to: SvgPoint): number {
  return Math.hypot(to.x - from.x, to.y - from.y);
}

function movePointToward(from: SvgPoint, to: SvgPoint, distance: number): SvgPoint {
  const totalDistance = getPointDistance(from, to);
  if (!Number.isFinite(totalDistance) || totalDistance <= 0 || distance <= 0) return from;
  const ratio = Math.min(1, distance / totalDistance);
  return {
    x: from.x + (to.x - from.x) * ratio,
    y: from.y + (to.y - from.y) * ratio,
  };
}

function interpolatePoint(from: SvgPoint, to: SvgPoint, ratio: number): SvgPoint {
  return {
    x: from.x + (to.x - from.x) * ratio,
    y: from.y + (to.y - from.y) * ratio,
  };
}

function getRoundedPolygonPath(points: SvgPoint[], radius: number): string {
  if (points.length < 3) return "";
  const cornerRadii = points.map((point, index) => {
    const previous = points[(index - 1 + points.length) % points.length] ?? point;
    const next = points[(index + 1) % points.length] ?? point;
    return Math.min(radius, getPointDistance(point, previous) / 2, getPointDistance(point, next) / 2);
  });
  const cornerStarts = points.map((point, index) => {
    const previous = points[(index - 1 + points.length) % points.length] ?? point;
    return movePointToward(point, previous, cornerRadii[index] ?? 0);
  });
  const cornerEnds = points.map((point, index) => {
    const next = points[(index + 1) % points.length] ?? point;
    return movePointToward(point, next, cornerRadii[index] ?? 0);
  });
  const firstStart = cornerStarts[0];
  if (!firstStart) return "";
  const commands = [`M ${formatSvgNumber(firstStart.x)} ${formatSvgNumber(firstStart.y)}`];
  points.forEach((point, index) => {
    const cornerEnd = cornerEnds[index];
    if (!cornerEnd) return;
    commands.push(
      `Q ${formatSvgNumber(point.x)} ${formatSvgNumber(point.y)} ${formatSvgNumber(cornerEnd.x)} ${formatSvgNumber(cornerEnd.y)}`,
    );
    const nextStart = cornerStarts[index + 1];
    if (nextStart) {
      commands.push(`L ${formatSvgNumber(nextStart.x)} ${formatSvgNumber(nextStart.y)}`);
    }
  });
  commands.push("Z");
  return commands.join(" ");
}

const PLANNING_SERIES_ROLES = new Set(["baseline", "target", "forecast", "plan"]);

function isTrendChartType(type: ChartSpec["type"]): boolean {
  return type === "area" || type === "line" || type === "sparkline" || type === "stackedArea";
}

function isPlanningSeries(series: ChartSeriesSpec): boolean {
  return PLANNING_SERIES_ROLES.has(series.semanticRole ?? series.role ?? "");
}

function getSeriesColor(chart: ChartSpec, series: ChartSeriesSpec, index: number): string {
  const color = isPlanningSeries(series) && !series.color
    ? "neutral"
    : series.color;
  return colorForSeries(color, index, {
    singleSeriesTrend: (chart.type === "line" || chart.type === "area") && chart.series.length === 1,
    stacked: isStackedChartType(chart.type, chart.settings?.groupMode),
  });
}

function getSeriesStrokeDasharray(chart: ChartSpec, series: ChartSeriesSpec): string | undefined {
  if (!isTrendChartType(chart.type)) return undefined;
  if (series.lineStyle === "solid") return undefined;
  if (series.lineStyle === "dotted") return "2 4";
  if (series.lineStyle === "dashed" || isPlanningSeries(series)) return "5 5";
  return undefined;
}

function shouldColorBarsByCategory(): boolean {
  return false;
}

function renderCategoryBarCells(chart: ChartSpec, series: ChartSeriesSpec, rows: ChartDataRow[], colorBarsBySign = false) {
  if (colorBarsBySign) {
    return rows.map((row, index) => (
      <Cell
        fill={barSignColor(asNumber(row[series.field]))}
        key={`${chart.id}-${series.field}-${String(row[chart.xField] ?? index)}-${index}`}
      />
    ));
  }
  if (!shouldColorBarsByCategory() || series.color) return null;
  return rows.map((row, index) => (
    <Cell
      fill={colorForSeries(undefined, index)}
      key={`${chart.id}-${series.field}-${String(row[chart.xField] ?? index)}-${index}`}
    />
  ));
}

function waterfallBarPath({
  height,
  isPositive,
  radius,
  width,
  x,
  y,
}: {
  height: number;
  isPositive: boolean;
  radius: number;
  width: number;
  x: number;
  y: number;
}) {
  const right = x + width;
  const bottom = y + height;

  if (radius <= 0) {
    return `M${x},${y}H${right}V${bottom}H${x}Z`;
  }

  if (isPositive) {
    return [
      `M${x},${bottom}`,
      `V${y + radius}`,
      `Q${x},${y} ${x + radius},${y}`,
      `H${right - radius}`,
      `Q${right},${y} ${right},${y + radius}`,
      `V${bottom}`,
      "Z",
    ].join("");
  }

  return [
    `M${x},${y}`,
    `H${right}`,
    `V${bottom - radius}`,
    `Q${right},${bottom} ${right - radius},${bottom}`,
    `H${x + radius}`,
    `Q${x},${bottom} ${x},${bottom - radius}`,
    "Z",
  ].join("");
}

function renderWaterfallBarShape(props: WaterfallBarShapeProps) {
  const payload = props.payload;
  const x = asFiniteNumber(props.x);
  const y = asFiniteNumber(props.y);
  const width = Math.max(2, asFiniteNumber(props.width));
  const height = Math.max(2, asFiniteNumber(props.height));
  const isPositive = Boolean(payload?.__waterfallIsPositive);
  const isLast = Boolean(payload?.__waterfallIsLast);
  const value = asFiniteNumber(payload?.__waterfallValue);
  const rowCount = Math.max(1, asFiniteNumber(payload?.__waterfallRowCount, 1));
  const slotWidth = props.parentViewBox?.width ? props.parentViewBox.width / rowCount : width;
  const connectorY = isPositive ? y : y + height;
  const connectorEndX = x + slotWidth;
  const radius = value === 0 ? 0 : Math.min(6, width / 2, height / 2);
  const fill = isPositive ? "var(--ds-chart-series-green)" : "var(--ds-chart-series-red)";

  return (
    <g className={`waterfall-bar-shape ${props.isActive ? "active" : ""}`}>
      {!isLast ? (
        <line
          className="waterfall-connector"
          stroke="var(--ds-chart-reference-line)"
          strokeLinecap="round"
          strokeWidth={1}
          vectorEffect="non-scaling-stroke"
          x1={x + width + 3}
          x2={Math.max(x + width + 3, connectorEndX - 3)}
          y1={connectorY}
          y2={connectorY}
        />
      ) : null}
      <path
        d={waterfallBarPath({ height, isPositive, radius, width, x, y })}
        fill={fill}
        vectorEffect="non-scaling-stroke"
      />
    </g>
  );
}

function renderRoundedFunnelShape(props: FunnelShapeProps) {
  const {
    className,
    fill,
    height,
    labelViewBox,
    lowerWidth,
    name: _name,
    option: _option,
    parentViewBox: _parentViewBox,
    payload,
    shapeType: _shapeType,
    stroke: _stroke,
    strokeWidth: _strokeWidth,
    tooltipPayload: _tooltipPayload,
    tooltipPosition: _tooltipPosition,
    upperWidth,
    val: _val,
    value: _value,
    width: _width,
    x,
    y,
    ...svgProps
  } = props;
  const topX = asFiniteNumber(labelViewBox?.x ?? x);
  const topY = asFiniteNumber(labelViewBox?.y ?? y);
  const topWidth = asFiniteNumber(labelViewBox?.upperWidth ?? upperWidth);
  const bottomWidth = asFiniteNumber(labelViewBox?.lowerWidth ?? lowerWidth);
  const segmentHeight = asFiniteNumber(labelViewBox?.height ?? height);
  if (topWidth <= 0 || bottomWidth <= 0 || segmentHeight <= 0) return null;

  const segmentIndex = asFiniteNumber(payload?.__funnelIndex);
  const segmentCount = asFiniteNumber(payload?.__funnelRowCount, 1);
  const topInset = segmentIndex > 0 ? FUNNEL_SEGMENT_GAP / 2 : 0;
  const bottomInset = segmentIndex < segmentCount - 1 ? FUNNEL_SEGMENT_GAP / 2 : 0;
  const topInsetRatio = topInset / segmentHeight;
  const bottomInsetRatio = bottomInset / segmentHeight;
  const widthGap = topWidth - bottomWidth;
  const bottomRightX = topX + topWidth - widthGap / 2;
  const bottomLeftX = bottomRightX - bottomWidth;
  const topLeft = { x: topX, y: topY };
  const topRight = { x: topX + topWidth, y: topY };
  const bottomRight = { x: bottomRightX, y: topY + segmentHeight };
  const bottomLeft = { x: bottomLeftX, y: topY + segmentHeight };
  const segmentPath = getRoundedPolygonPath(
    [
      interpolatePoint(topLeft, bottomLeft, topInsetRatio),
      interpolatePoint(topRight, bottomRight, topInsetRatio),
      interpolatePoint(bottomRight, topRight, bottomInsetRatio),
      interpolatePoint(bottomLeft, topLeft, bottomInsetRatio),
    ],
    FUNNEL_CORNER_RADIUS,
  );

  return (
    <path
      {...(svgProps as SVGProps<SVGPathElement>)}
      className={`funnel-segment ${className ?? ""}`.trim()}
      d={segmentPath}
      fill={fill}
      shapeRendering="geometricPrecision"
      stroke="none"
    />
  );
}

function renderFunnelCenterLabel(props: FunnelLabelProps) {
  const viewBox = props.viewBox;
  const x = asFiniteNumber(viewBox?.x ?? props.x, Number.NaN);
  const y = asFiniteNumber(viewBox?.y ?? props.y, Number.NaN);
  const width = asFiniteNumber(viewBox?.width ?? props.width, Number.NaN);
  const height = asFiniteNumber(viewBox?.height ?? props.height, Number.NaN);
  if (![x, y, width, height].every(Number.isFinite)) return null;

  const [fallbackLabel = "", fallbackValue = ""] =
    typeof props.value === "string" ? props.value.split("\u0000") : [];
  const label = String(props.payload?.__funnelLabel ?? fallbackLabel);
  const value = String(props.payload?.__funnelValueLabel ?? fallbackValue);
  if (!label && !value) return null;

  return (
    <text className="funnel-label" dominantBaseline="middle" textAnchor="middle" x={x + width / 2} y={y + height / 2}>
      <tspan className="funnel-label-text">{label}</tspan>
      <tspan className="funnel-label-value" dx={FUNNEL_LABEL_GAP}>
        {value}
      </tspan>
    </text>
  );
}

function renderScatterPointLabel(props: {
  value?: unknown;
  x?: number | string;
  y?: number | string;
}) {
  const label = props.value == null ? "" : String(props.value).trim();
  const x = asFiniteNumber(props.x, Number.NaN);
  const y = asFiniteNumber(props.y, Number.NaN);
  if (!label || !Number.isFinite(x) || !Number.isFinite(y)) return null;
  const shortLabel = label.length > 28 ? `${label.slice(0, 25)}...` : label;
  return (
    <text className="scatter-point-label" dominantBaseline="auto" textAnchor="middle" x={x} y={y - 8}>
      {shortLabel}
    </text>
  );
}

function valueLabelMode(chart: ChartSpec): ChartValueLabelMode {
  const explicitMode = chart.labels?.values;
  if (explicitMode) return explicitMode;
  if (chart.settings?.showValues === true) return "all";
  if (chart.settings?.showValues === false) return "none";
  return "auto";
}

function visibleBarValueCount(rows: ChartDataRow[], series: ChartSeriesSpec[]): number {
  return rows.reduce(
    (count, row) => count + series.filter((candidate) => asNumber(row[candidate.field]) != null).length,
    0,
  );
}

function visibleBarValueLabelSides(rows: ChartDataRow[], series: ChartSeriesSpec[]): BarValueLabelSides {
  return rows.reduce<BarValueLabelSides>(
    (sides, row) => {
      for (const candidate of series) {
        const value = asNumber(row[candidate.field]);
        if (value == null) continue;
        if (value < 0) {
          sides.hasNegative = true;
        } else {
          sides.hasNonNegative = true;
        }
      }
      return sides;
    },
    { hasNegative: false, hasNonNegative: false },
  );
}

function barSignState(rows: ChartDataRow[], series: ChartSeriesSpec[]): BarSignState {
  return rows.reduce<BarSignState>(
    (state, row) => {
      for (const candidate of series) {
        const value = asNumber(row[candidate.field]);
        if (value == null) continue;
        if (value > 0) state.hasPositive = true;
        else if (value < 0) state.hasNegative = true;
        else state.hasZero = true;
      }
      return state;
    },
    { hasNegative: false, hasPositive: false, hasZero: false },
  );
}

function shouldColorBarsBySign({
  activeSeries,
  chart,
  signState,
  stacked,
}: {
  activeSeries: ChartSeriesSpec[];
  chart: ChartSpec;
  signState: BarSignState;
  stacked: boolean;
}): boolean {
  if (stacked || activeSeries.length !== 1) return false;
  if (chart.type !== "bar" && chart.type !== "horizontalBar") return false;
  return signState.hasPositive && signState.hasNegative;
}

function barSignColor(value: number | null): string {
  if (value == null || value === 0) return "var(--ds-chart-series-neutral)";
  return value > 0 ? "var(--ds-chart-series-green)" : "var(--ds-chart-series-red)";
}

function formatSignedValue(value: number, chart: ChartSpec, showPositiveSign: boolean): string {
  const label = formatValue(value, chart.valueFormat, chart.unit);
  return showPositiveSign && value > 0 ? `+${label}` : label;
}

function shouldShowBarValueLabels({
  activeSeries,
  chart,
  rows,
  stacked,
}: {
  activeSeries: ChartSeriesSpec[];
  chart: ChartSpec;
  rows: ChartDataRow[];
  stacked: boolean;
}): boolean {
  if (chart.type !== "bar" && chart.type !== "horizontalBar" && chart.type !== "histogram") {
    return false;
  }
  if (stacked) return false;
  const labelMode = valueLabelMode(chart);
  if (labelMode === "none" || labelMode === "endpoints") return false;
  if (labelMode === "all") return true;

  const valueCount = visibleBarValueCount(rows, activeSeries);
  return valueCount > 0 && valueCount <= BAR_AUTO_VALUE_LABEL_LIMIT;
}

function renderBarValueLabel({
  chart,
  height,
  horizontal,
  showPositiveSign = false,
  value,
  width,
  x,
  y,
}: BarValueLabelProps & {
  chart: ChartSpec;
  horizontal: boolean;
  showPositiveSign?: boolean;
}) {
  const numericValue = asNumber(value);
  const numericX = asFiniteNumber(x, Number.NaN);
  const numericY = asFiniteNumber(y, Number.NaN);
  const numericWidth = asFiniteNumber(width, Number.NaN);
  const numericHeight = asFiniteNumber(height, Number.NaN);
  if (
    numericValue == null ||
    ![numericX, numericY, numericWidth, numericHeight].every(Number.isFinite)
  ) {
    return null;
  }

  const label = formatSignedValue(numericValue, chart, showPositiveSign);
  const isNegative = numericValue < 0;
  if (horizontal) {
    const left = Math.min(numericX, numericX + numericWidth);
    const right = Math.max(numericX, numericX + numericWidth);
    return (
      <text
        className="chart-bar-value-label"
        dominantBaseline="middle"
        textAnchor={isNegative ? "end" : "start"}
        x={isNegative ? left - BAR_VALUE_LABEL_OFFSET : right + BAR_VALUE_LABEL_OFFSET}
        y={numericY + numericHeight / 2}
      >
        {label}
      </text>
    );
  }

  const top = Math.min(numericY, numericY + numericHeight);
  const bottom = Math.max(numericY, numericY + numericHeight);
  return (
    <text
      className="chart-bar-value-label"
      dominantBaseline={isNegative ? "hanging" : "auto"}
      textAnchor="middle"
      x={numericX + numericWidth / 2}
      y={isNegative ? bottom + BAR_NEGATIVE_VALUE_LABEL_OFFSET : top - BAR_VALUE_LABEL_OFFSET}
    >
      {label}
    </text>
  );
}

function categoryBarTooltipColor(chart: ChartSpec, rows: ChartDataRow[], item: ChartTooltipPayloadItem, colorBarsBySign = false): string | undefined {
  if (colorBarsBySign) return barSignColor(asNumber(item.value));
  if (!shouldColorBarsByCategory()) return undefined;
  if (chart.series[0]?.color) return undefined;
  const payload = item.payload && typeof item.payload === "object"
    ? item.payload as ChartDataRow
    : null;
  const category = payload ? payload[chart.xField] : null;
  const rowIndex = rows.findIndex((row) => String(row[chart.xField] ?? "") === String(category ?? ""));
  return colorForSeries(undefined, rowIndex < 0 ? 0 : rowIndex);
}

function getAreaGradientId(chart: ChartSpec, series: ChartSeriesSpec): string {
  return `${chart.id}-${series.field}`.replace(/[^a-zA-Z0-9_-]/g, "-");
}

function referenceLines(chart: ChartSpec, horizontal = false) {
  return (chart.referenceLines ?? []).map((line, index) => {
    const axis = line.axis ?? (horizontal ? "x" : "y");
    const value = typeof line.value === "number" ? line.value : Number(line.value);
    if (!Number.isFinite(value)) return null;
    const props = {
      stroke: "var(--ds-chart-reference-line)",
      strokeDasharray: value === 0 ? undefined : "4 4",
    };
    const key = `${axis}-${value}-${index}`;
    return axis === "x" ? <ReferenceLine key={key} {...props} x={value} /> : <ReferenceLine key={key} {...props} y={value} />;
  });
}

function chartLegendItems(chart: ChartSpec, visibleSeries: ChartSeriesSpec[], signState?: BarSignState | null, rows: ChartDataRow[] = []) {
  if (signState) {
    const items = [];
    if (signState.hasPositive) items.push({ color: barSignColor(1), id: "__positive", value: "positive" });
    if (signState.hasNegative) items.push({ color: barSignColor(-1), id: "__negative", value: "negative" });
    if (signState.hasZero) items.push({ color: barSignColor(0), id: "__zero", value: "neutral" });
    return items;
  }
  if (chart.type === "pie") {
    return buildPieRows(chart, rows).map((row) => ({
      color: getSeriesColor(chart, chart.series[0], asFiniteNumber(row.__pieIndex)),
      id: String(row.__pieField ?? row.__pieName ?? row.__pieIndex),
      value: String(row.__pieName ?? row.__pieField ?? ""),
    }));
  }
  if (chart.series.length <= 1) return [];
  if (
    chart.type !== "area" &&
    chart.type !== "bar" &&
    chart.type !== "horizontalBar" &&
    chart.type !== "line" &&
    chart.type !== "scatter" &&
    chart.type !== "stackedArea" &&
    chart.type !== "stackedBar" &&
    chart.type !== "stackedBar100" &&
    chart.type !== "horizontalStackedBar" &&
    chart.type !== "horizontalStackedBar100" &&
    chart.type !== "pie"
  ) {
    return [];
  }
  return chart.series.map((series, index) => ({
    color: getSeriesColor(chart, series, index),
    id: series.field,
    lineStyle: series.lineStyle ?? (isTrendChartType(chart.type) && isPlanningSeries(series) ? "dashed" : undefined),
    value: series.label ?? series.field,
    visible: visibleSeries.some((visible) => visible.field === series.field),
  }));
}

function renderAreaGradientDefs(chart: ChartSpec) {
  const shouldRenderAreaFill =
    chart.type === "area" || chart.type === "stackedArea" || chart.type === "sparkline";
  if (!shouldRenderAreaFill) return null;
  return (
    <defs>
      {chart.series.map((series, index) => {
        const color = getSeriesColor(chart, series, index);
        const gradientId = getAreaGradientId(chart, series);
        return (
          <linearGradient id={gradientId} key={gradientId} x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity={0.12} />
            <stop offset="100%" stopColor={color} stopOpacity={0} />
          </linearGradient>
        );
      })}
    </defs>
  );
}

function LeaderboardPanel({ chart, rows }: { chart: ChartSpec; rows: ChartDataRow[] }) {
  const series = chart.series[0];
  const requestedRows = typeof chart.maxRows === "number" && Number.isFinite(chart.maxRows) ? chart.maxRows : 6;
  const rowLimit = Math.max(1, Math.min(8, Math.floor(requestedRows)));
  const rankedRows = [...rows].sort(
    (a, b) => Math.abs(asNumber(b[series?.field ?? ""]) ?? 0) - Math.abs(asNumber(a[series?.field ?? ""]) ?? 0),
  );
  const visibleRows = rankedRows.slice(0, rowLimit);
  const max = Math.max(...visibleRows.map((row) => Math.abs(asNumber(row[series?.field ?? ""]) ?? 0)), 1);
  const style = { "--leaderboard-row-count": visibleRows.length } as CSSProperties;
  return (
    <div className="leaderboard" style={style}>
      {visibleRows.map((row, index) => {
        const value = asNumber(row[series?.field ?? ""]) ?? 0;
        const width = `${Math.max(4, (Math.abs(value) / max) * 100)}%`;
        const rowStyle = {
          "--bar-color": getSeriesColor(chart, series, 0),
          "--bar-width": width,
        } as CSSProperties;
        return (
          <div
            className={`leaderboard-row ${value >= 0 ? "positive" : "negative"}`}
            key={`${String(row[chart.xField])}-${index}`}
            style={rowStyle}
          >
            <span className="leaderboard-label">{String(row[chart.xField] ?? "")}</span>
            <span className="leaderboard-value">{formatValue(value, chart.valueFormat, chart.unit)}</span>
          </div>
        );
      })}
    </div>
  );
}

type HeatmapTooltipData = {
  anchor: HTMLSpanElement;
  key: string;
  markerColor: string;
  rowLabel: string;
  seriesLabel: string;
  valueLabel: string;
};

function HeatmapTooltipPortal({ tooltip }: { tooltip: HeatmapTooltipData }) {
  const tooltipRef = useRef<HTMLSpanElement | null>(null);
  const [position, setPosition] = useState<ViewportTooltipPosition | null>(null);
  const updatePosition = useCallback(() => {
    const tooltipElement = tooltipRef.current;
    if (!tooltipElement || !tooltip.anchor.isConnected) {
      setPosition(null);
      return;
    }
    const anchorRect = tooltip.anchor.getBoundingClientRect();
    const scrollContainerRect = tooltip.anchor.closest(".heatmap-grid-panel")?.getBoundingClientRect();
    const visibleTop = Math.max(0, scrollContainerRect?.top ?? 0);
    const visibleRight = Math.min(window.innerWidth, scrollContainerRect?.right ?? window.innerWidth);
    const visibleBottom = Math.min(window.innerHeight, scrollContainerRect?.bottom ?? window.innerHeight);
    const visibleLeft = Math.max(0, scrollContainerRect?.left ?? 0);
    if (
      anchorRect.bottom <= visibleTop
      || anchorRect.left >= visibleRight
      || anchorRect.top >= visibleBottom
      || anchorRect.right <= visibleLeft
    ) {
      setPosition(null);
      return;
    }
    const tooltipRect = tooltipElement.getBoundingClientRect();
    const nextPosition = calculateViewportTooltipPosition({
      anchorRect,
      tooltipSize: { height: tooltipRect.height, width: tooltipRect.width },
      viewport: { height: window.innerHeight, width: window.innerWidth },
    });
    setPosition((current) => current
      && current.left === nextPosition.left
      && current.placement === nextPosition.placement
      && current.top === nextPosition.top
      ? current
      : nextPosition);
  }, [tooltip]);

  useLayoutEffect(() => {
    let frame = 0;
    const schedulePositionUpdate = () => {
      window.cancelAnimationFrame(frame);
      frame = window.requestAnimationFrame(updatePosition);
    };
    updatePosition();
    window.addEventListener("resize", schedulePositionUpdate);
    window.addEventListener("scroll", schedulePositionUpdate, true);
    const observer = typeof ResizeObserver === "function" ? new ResizeObserver(schedulePositionUpdate) : null;
    observer?.observe(tooltip.anchor);
    if (tooltipRef.current) observer?.observe(tooltipRef.current);
    return () => {
      window.cancelAnimationFrame(frame);
      observer?.disconnect();
      window.removeEventListener("resize", schedulePositionUpdate);
      window.removeEventListener("scroll", schedulePositionUpdate, true);
    };
  }, [tooltip.anchor, updatePosition]);

  if (typeof document === "undefined") return null;
  const style = position
    ? { left: position.left, top: position.top }
    : { left: 0, top: 0, visibility: "hidden" };
  return createPortal(
    <span
      className="chart-tooltip heatmap-tooltip"
      data-placement={position?.placement}
      ref={tooltipRef}
      role="tooltip"
      style={style}
    >
      <span className="chart-tooltip-label">{tooltip.rowLabel}</span>
      <span className="chart-tooltip-items">
        <span className="chart-tooltip-item">
          <span
            aria-hidden="true"
            className="chart-tooltip-marker"
            style={{ background: tooltip.markerColor }}
          />
          <span className="chart-tooltip-name">{tooltip.seriesLabel}</span>
          <span className="chart-tooltip-value">{tooltip.valueLabel}</span>
        </span>
      </span>
    </span>,
    document.body,
  );
}

function HeatmapPanel({ chart, rows }: { chart: ChartSpec; rows: ChartDataRow[] }) {
  const [focusedTooltip, setFocusedTooltip] = useState<HeatmapTooltipData | null>(null);
  const [hoveredTooltip, setHoveredTooltip] = useState<HeatmapTooltipData | null>(null);
  const activeTooltip = hoveredTooltip ?? focusedTooltip;
  useLayoutEffect(() => {
    setFocusedTooltip(null);
    setHoveredTooltip(null);
  }, [chart.id, rows]);
  const values = rows.flatMap((row) =>
    chart.series
      .map((series) => asNumber(row[series.field]))
      .filter((value): value is number => value != null),
  );
  if (!values.length) return <div className="empty-state">No numeric heatmap values.</div>;
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const heatmapStyle = {
    "--heatmap-row-min-height": `${COMPLEX_CHART_MIN_ROW_HEIGHT}px`,
    "--heatmap-header-row-height": `${HEATMAP_HEADER_ROW_HEIGHT}px`,
    gridTemplateColumns: `minmax(88px, max-content) repeat(${chart.series.length}, minmax(40px, 1fr))`,
    gridTemplateRows: `repeat(${rows.length}, minmax(var(--heatmap-row-min-height), 1fr)) minmax(var(--heatmap-header-row-height), auto)`,
  } as CSSProperties;

  return (
    <div className="heatmap-grid-panel">
      <div className="heatmap-grid" style={heatmapStyle}>
        {rows.map((row, rowIndex) => {
          const rowLabel = String(row[chart.xField] ?? "");
          return (
            <Fragment key={`${chart.id}-heatmap-row-${rowIndex}`}>
              <strong key={`${rowIndex}-label`}>{rowLabel}</strong>
              {chart.series.map((series) => {
                const seriesLabel = series.label ?? series.field;
                const value = asNumber(row[series.field]) ?? min;
                const intensity = clamp((value - min) / range, 0, 1);
                const valueLabel = formatValue(value, chart.valueFormat, chart.unit);
                const label = `${rowLabel} ${seriesLabel}: ${valueLabel}`;
                const markerColor = getHeatmapFill(intensity);
                const tooltipKey = `${rowIndex}-${series.field}`;
                const tooltipForAnchor = (anchor: HTMLSpanElement): HeatmapTooltipData => ({
                  anchor,
                  key: tooltipKey,
                  markerColor,
                  rowLabel,
                  seriesLabel,
                  valueLabel,
                });
                return (
                  <span
                    aria-label={label}
                    className="heatmap-cell"
                    key={tooltipKey}
                    onBlur={() => setFocusedTooltip((current) => current?.key === tooltipKey ? null : current)}
                    onFocus={(event) => setFocusedTooltip(tooltipForAnchor(event.currentTarget))}
                    onPointerCancel={() => setHoveredTooltip((current) => current?.key === tooltipKey ? null : current)}
                    onPointerEnter={(event) => setHoveredTooltip(tooltipForAnchor(event.currentTarget))}
                    onPointerLeave={() => setHoveredTooltip((current) => current?.key === tooltipKey ? null : current)}
                    role="img"
                    style={{ background: markerColor }}
                    tabIndex={0}
                  />
                );
              })}
            </Fragment>
          );
        })}
        <span className="heatmap-axis-corner" />
        {chart.series.map((series) => (
          <b key={series.field}>{series.label ?? series.field}</b>
        ))}
      </div>
      {activeTooltip ? <HeatmapTooltipPortal key={activeTooltip.key} tooltip={activeTooltip} /> : null}
    </div>
  );
}

function CustomPanelFrame({
  chart,
  children,
  height,
  surface,
}: {
  chart: ChartSpec;
  children: ReactNode;
  height?: number | string;
  surface: ChartSurface;
}) {
  return (
    <ChartFrame
      className={`chart-frame--custom chart-frame--${chart.type}`}
      height={chartHeightForSurface(surface, height)}
      surface={surface}
    >
      {children}
    </ChartFrame>
  );
}

export function ChartRenderer({
  chart: chartSpec,
  height,
  onVisibleSeriesChange,
  responsive = true,
  rows: rawRows,
  showLegend = true,
  surface,
  visibleSeries,
  width,
}: {
  chart: ChartSpec;
  height?: number | string;
  onVisibleSeriesChange?: (visible: Set<string>) => void;
  responsive?: boolean;
  rows: ChartDataRow[];
  showLegend?: boolean;
  surface?: ChartSurface;
  visibleSeries?: Set<string>;
  width?: number | string;
}) {
  const { chart, rows } = rechartsChartFromEncodedSpec(chartSpec, rawRows);
  const resolvedSurface = surface ?? chart.surface?.surface ?? "card";
  const activeSeries = chart.series.filter((series) => !visibleSeries || !visibleSeries.size || visibleSeries.has(series.field));
  const firstSeries = chart.series[0];
  if (!firstSeries) return <div className="empty-state">Chart needs at least one series.</div>;

  if (chart.type === "leaderboard") {
    return <CustomPanelFrame chart={chart} height={height} surface={resolvedSurface}><LeaderboardPanel chart={chart} rows={rows} /></CustomPanelFrame>;
  }
  if (chart.type === "heatmap") {
    return (
      <CustomPanelFrame
        chart={chart}
        height={complexChartFrameHeight({ headerRows: 1, height, rowCount: rows.length, surface: resolvedSurface })}
        surface={resolvedSurface}
      >
        <HeatmapPanel chart={chart} rows={rows} />
      </CustomPanelFrame>
    );
  }

  const fixedChartWidth = numericChartDimension(width, CHART_STATIC_WIDTH);
  const xAxisTicks = getDateAxisTicks(rows, chart.xField, fixedChartWidth);
  const barGroupMode = chart.settings?.groupMode;
  const barOrientation = chart.settings?.orientation;
  const horizontal = isHorizontalChartType(chart.type, barOrientation);
  const rotateCategoryXAxisLabels = shouldRotateCategoryXAxisLabels({
    chart,
    horizontal,
    xAxisTicks,
  });
  const wrapCategoryXAxisLabels = shouldWrapCategoryXAxisLabels({
    availableWidth: fixedChartWidth,
    chart,
    horizontal,
    rows,
    xAxisTicks,
  });
  const categoryXAxisTicks = sparseCategoryXAxisTicks({
    availableWidth: fixedChartWidth,
    chart,
    horizontal,
    rotateCategoryXAxisLabels,
    rows,
    wrapCategoryXAxisLabels,
    xAxisTicks,
  });
  const wrappedCategoryXAxisLineLength = categoryXAxisWrappedLineLength(chart, rows, fixedChartWidth);
  const stacked = isStackedChartType(chart.type, barGroupMode);
  const normalized = isNormalizedStackedChartType(chart.type, barGroupMode);
  const currentBarSignState = barSignState(rows, activeSeries);
  const colorBarsBySign = shouldColorBarsBySign({
    activeSeries,
    chart,
    signState: currentBarSignState,
    stacked,
  });
  const showBarValueLabels = shouldShowBarValueLabels({
    activeSeries,
    chart,
    rows,
    stacked,
  });
  const barValueLabelSides = showBarValueLabels
    ? visibleBarValueLabelSides(rows, activeSeries)
    : { hasNegative: false, hasNonNegative: false };
  const legendItems = showLegend ? chartLegendItems(chart, activeSeries, colorBarsBySign ? currentBarSignState : null, rows) : [];
  const tooltipChart = chart;
  const yAxisScale = getYAxisScaleForSeries(chart, rows, activeSeries);
  const frameHeight = chartFrameHeightForContent({
    hasLegend: legendItems.length > 0,
    height,
    horizontal,
    rotateCategoryXAxisLabels,
    rowCount: rows.length,
    surface: resolvedSurface,
  });
  const commonProps = { data: rows };
  const tooltipWrapperStyle: CSSProperties = { pointerEvents: "none", zIndex: 40 };
  const fastTooltipProps = {
    animationDuration: 0,
    animationEasing: "linear",
    isAnimationActive: false,
    offset: 12,
    wrapperStyle: tooltipWrapperStyle,
  };
  const subtleTooltipCursor = {
    fill: "var(--ds-chart-hover-bg)",
    stroke: "transparent",
    strokeWidth: 0,
  };
  const visibleIds = new Set(activeSeries.map((series) => series.field));
  const interactiveLegend = Boolean(onVisibleSeriesChange) && !colorBarsBySign;
  const fixedFrameHeight = numericChartDimension(
    frameHeight,
    resolvedSurface === "explorer" ? CHART_FULLSCREEN_HEIGHT : CHART_COMPACT_HEIGHT,
  );
  const fixedLegendReserve = legendItems.length ? CHART_LEGEND_RESERVED_HEIGHT : 0;
  const fixedChartHeight = Math.max(CHART_MIN_PLOT_HEIGHT, fixedFrameHeight - fixedLegendReserve);
  function bottomAxisLabel(value: string) {
    return {
        offset: -4,
        position: "insideBottom",
        style: { fill: "var(--ds-text-primary)", fontSize: 12, fontWeight: 500, textAnchor: "middle" },
        value,
      };
  }

  function leftAxisLabel(value: string) {
    return {
        angle: -90,
        offset: 0,
        position: "insideLeft",
        style: { fill: "var(--ds-text-primary)", fontSize: 12, fontWeight: 500, textAnchor: "middle" },
        value,
      };
  }

  const xAxisLabel = chart.xAxisTitle ? bottomAxisLabel(chart.xAxisTitle) : undefined;
  const yAxisLabel = chart.yAxisTitle ? leftAxisLabel(chart.yAxisTitle) : undefined;
  const horizontalValueAxisLabel = chart.xAxisTitle ? bottomAxisLabel(chart.xAxisTitle) : undefined;
  // Horizontal bars already show category names as row labels; an extra axis title competes for left-side space.
  const horizontalCategoryAxisLabel = undefined;
  const bottomMarginAxisLabel = horizontal ? horizontalValueAxisLabel : xAxisLabel;
  const leftMarginAxisLabel = horizontal ? horizontalCategoryAxisLabel : yAxisLabel;
  const baseBottomMargin = !horizontal && rotateCategoryXAxisLabels ? (bottomMarginAxisLabel ? 16 : 8) : bottomMarginAxisLabel ? 8 : 0;
  const baseLeftMargin = leftMarginAxisLabel ? 4 : 0;
  const cartesianMargin = {
    bottom:
      !horizontal && barValueLabelSides.hasNegative
        ? Math.max(baseBottomMargin, BAR_NEGATIVE_VALUE_LABEL_AXIS_GUTTER)
        : baseBottomMargin,
    left:
      horizontal && barValueLabelSides.hasNegative
        ? Math.max(baseLeftMargin, BAR_VALUE_LABEL_HORIZONTAL_GUTTER)
        : baseLeftMargin,
    right:
      horizontal && barValueLabelSides.hasNonNegative
        ? BAR_VALUE_LABEL_HORIZONTAL_GUTTER
        : 0,
    top:
      !horizontal && barValueLabelSides.hasNonNegative
        ? Math.max(Y_AXIS_TICK_LABEL_OVERHANG, BAR_VALUE_LABEL_VERTICAL_GUTTER)
        : Y_AXIS_TICK_LABEL_OVERHANG,
  };
  const resolveTooltipColor = (item: ChartTooltipPayloadItem) => categoryBarTooltipColor(chart, rows, item, colorBarsBySign);
  const responsiveChartProps = responsive
    ? {
        margin: cartesianMargin,
      }
    : {
        height: fixedChartHeight,
        margin: cartesianMargin,
        width: fixedChartWidth,
      };
  const chartProps = { ...responsiveChartProps, ...commonProps };
  const emptyMessage = chartEmptyMessage(chart, rows, visibleSeries);
  if (emptyMessage) {
    return (
      <ChartFrame
        height={frameHeight}
        interactiveLegend={interactiveLegend}
        legendItems={legendItems}
        onVisibleChange={onVisibleSeriesChange}
        surface={resolvedSurface}
        visibleIds={visibleIds}
      >
        <div className="empty-state">{emptyMessage}</div>
      </ChartFrame>
    );
  }

  function renderYAxis(dataKey?: string) {
    const yAxisValueFormat = normalized ? "percent" : chart.valueFormat ?? "compact";
    return (
      <YAxis
        axisLine={false}
        dataKey={dataKey}
        domain={normalized ? [0, 1] : undefined}
        interval={0}
        label={yAxisLabel}
        tick={(props: AxisTickProps) => (
          <NumericYAxisTick {...props} valueFormat={yAxisValueFormat} />
        )}
        tickFormatter={(value) => formatValue(value, yAxisValueFormat)}
        tickLine={false}
        tickMargin={RECHARTS_AXIS_TICK_MARGIN}
        tickSize={RECHARTS_AXIS_TICK_SIZE}
        ticks={yAxisScale.ticks}
        width="auto"
      />
    );
  }

  function shouldShowSeriesPoints(series: ChartSeriesSpec): boolean {
    const showPoints = chart.settings?.showPoints;
    if (showPoints === "always") return true;
    if (showPoints === "never") return false;
    let definedPointCount = 0;
    for (const row of rows) {
      if (asNumber(row[series.field]) == null) continue;
      definedPointCount += 1;
      if (definedPointCount > 1) return false;
    }
    return definedPointCount === 1;
  }

  function renderSeries() {
    return activeSeries.map((series, index) => {
      const originalIndex = chart.series.findIndex((item) => item.field === series.field);
      const color = getSeriesColor(chart, series, originalIndex < 0 ? index : originalIndex);
      const key = `${chart.id}-${series.field}`;
      if (
        chart.type === "bar" ||
        chart.type === "horizontalBar" ||
        chart.type === "histogram" ||
        chart.type === "stackedBar" ||
        chart.type === "stackedBar100" ||
        chart.type === "horizontalStackedBar" ||
        chart.type === "horizontalStackedBar100"
      ) {
        const isStacked = stacked;
        const isHorizontal = horizontal;
        const isHorizontalStacked = horizontal && stacked;
        const isTopStackSegment = isStacked && index === activeSeries.length - 1;
        return (
          <Bar
            dataKey={series.field}
            fill={color}
            isAnimationActive={false}
            key={key}
            minPointSize={!isStacked && showBarValueLabels ? 2 : undefined}
            name={series.label ?? series.field}
            radius={isStacked ? (isTopStackSegment ? (isHorizontalStacked ? [0, 6, 6, 0] : [6, 6, 0, 0]) : 0) : (isHorizontal ? [0, 6, 6, 0] : [6, 6, 0, 0])}
            stackId={isStacked ? "stack" : undefined}
          >
            {!isStacked ? renderCategoryBarCells(chart, series, rows, colorBarsBySign) : null}
            {showBarValueLabels ? (
              <LabelList
                content={(props) => renderBarValueLabel({
                  ...props,
                  chart,
                  horizontal: isHorizontal,
                  showPositiveSign: colorBarsBySign,
                })}
                dataKey={series.field}
              />
            ) : null}
          </Bar>
        );
      }
      if (chart.type === "area" || chart.type === "stackedArea" || chart.type === "sparkline") {
        const strokeDasharray = getSeriesStrokeDasharray(chart, series);
        return (
          <Area
            dataKey={series.field}
            dot={shouldShowSeriesPoints(series)}
            fill={`url(#${getAreaGradientId(chart, series)})`}
            fillOpacity={1}
            isAnimationActive={false}
            key={key}
            name={series.label ?? series.field}
            stackId={chart.type === "stackedArea" ? "stack" : undefined}
            stroke={color}
            strokeDasharray={strokeDasharray}
            strokeWidth={2}
            type="monotone"
          />
        );
      }
      const strokeDasharray = getSeriesStrokeDasharray(chart, series);
      return (
        <Line
          dataKey={series.field}
          dot={shouldShowSeriesPoints(series)}
          isAnimationActive={false}
          key={key}
          name={series.label ?? series.field}
          stroke={color}
          strokeDasharray={strokeDasharray}
          strokeWidth={2}
          type="monotone"
        />
      );
    });
  }

  const xAxisProps = {
    angle: rotateCategoryXAxisLabels ? CATEGORY_X_AXIS_LABEL_ROTATION_DEGREES : undefined,
    axisLine: false,
    dataKey: chart.xField,
    height: rotateCategoryXAxisLabels
      ? xAxisLabel
        ? CATEGORY_X_AXIS_ROTATED_HEIGHT_WITH_TITLE
        : CATEGORY_X_AXIS_ROTATED_HEIGHT
      : wrapCategoryXAxisLabels
        ? xAxisLabel
          ? CATEGORY_X_AXIS_WRAPPED_HEIGHT_WITH_TITLE
          : CATEGORY_X_AXIS_WRAPPED_HEIGHT
      : undefined,
    interval: rotateCategoryXAxisLabels || wrapCategoryXAxisLabels || categoryXAxisTicks ? 0 : undefined,
    label: xAxisLabel,
    tick: xAxisTicks
      ? ((props: AxisTickProps) => (
          <XAxisEndpointTick
            {...props}
            firstTick={xAxisTicks[0]}
            lastTick={xAxisTicks[xAxisTicks.length - 1]}
          />
        ))
      : wrapCategoryXAxisLabels
        ? ((props: AxisTickProps) => (
            <WrappedCategoryXAxisTick
              {...props}
              maxLineLength={wrappedCategoryXAxisLineLength}
            />
          ))
        : undefined,
    tickLine: false,
    tickMargin: rotateCategoryXAxisLabels
      ? CATEGORY_X_AXIS_ROTATED_TICK_MARGIN
      : wrapCategoryXAxisLabels
        ? CATEGORY_X_AXIS_WRAPPED_TICK_MARGIN
        : RECHARTS_AXIS_TICK_MARGIN,
    tickSize: RECHARTS_AXIS_TICK_SIZE,
    ticks: categoryXAxisTicks,
    textAnchor: rotateCategoryXAxisLabels ? "end" : undefined,
  };

  const boxPlotRows = chart.type === "boxPlot" ? buildBoxPlotRows(chart, rows) : [];
  const boxPlotXAxisScale = chart.type === "boxPlot" ? getBoxPlotXAxisScale(boxPlotRows) : null;
  const waterfallRows = chart.type === "waterfall" ? buildWaterfallRows(chart, rows) : [];
  const waterfallYAxisScale = chart.type === "waterfall" ? getWaterfallYAxisScale(waterfallRows) : undefined;
  const funnelRows = chart.type === "funnel" ? buildFunnelRows(chart, rows, getFunnelStageColor) : [];
  const pieRows = chart.type === "pie"
    ? buildPieRows(chart, rows).filter((row) => chart.series.length <= 1 || visibleIds.has(String(row.__pieField ?? "")))
    : [];
  const scatterYField = chart.type === "scatter" ? chartEncodingField(chart, "y") : undefined;
  const scatterLabelField = chart.type === "scatter" ? chartEncodingField(chart, "label") : undefined;
  const scatterSizeField = chart.type === "scatter" ? chartEncodingField(chart, "size") : undefined;
  const scatterLabelCount = scatterLabelField
    ? rows.filter((row) => row[scatterLabelField] != null && String(row[scatterLabelField]).trim()).length
    : 0;
  const showScatterPointLabels = Boolean(
    scatterLabelField &&
    chart.labels?.values !== "none" &&
    (chart.labels?.values === "all" || scatterLabelCount <= SCATTER_AUTO_LABEL_LIMIT),
  );

  const chartElement =
    chart.type === "boxPlot" ? (
      <BarChart {...chartProps} data={boxPlotRows} layout="vertical" margin={{ ...cartesianMargin, top: 0 }}>
        <CartesianGrid horizontal={false} />
        <XAxis axisLine={false} domain={boxPlotXAxisScale?.domain} label={horizontalValueAxisLabel} tickFormatter={(value) => formatValue(value, chart.valueFormat)} tickLine={false} tickMargin={RECHARTS_AXIS_TICK_MARGIN} tickSize={RECHARTS_AXIS_TICK_SIZE} ticks={boxPlotXAxisScale?.ticks} type="number" />
        <YAxis axisLine={false} dataKey={chart.xField} interval={0} label={horizontalCategoryAxisLabel} tickLine={false} tickMargin={RECHARTS_AXIS_TICK_MARGIN} tickSize={RECHARTS_AXIS_TICK_SIZE} type="category" width="auto" />
        <Tooltip {...fastTooltipProps} content={<BoxPlotTooltip chart={tooltipChart} />} cursor={false} />
        <Bar barSize={22} dataKey="__boxRange" fill="var(--ds-chart-series-blue)" isAnimationActive={false} name="Quartile range" radius={[6, 6, 6, 6]} />
      </BarChart>
    ) : chart.type === "waterfall" ? (
      <BarChart {...chartProps} data={waterfallRows} margin={cartesianMargin}>
        <CartesianGrid vertical={false} />
        <XAxis {...xAxisProps} />
        <YAxis axisLine={false} domain={waterfallYAxisScale?.domain} interval={0} label={yAxisLabel} tick={(props: AxisTickProps) => (<NumericYAxisTick {...props} valueFormat={chart.valueFormat ?? "compact"} />)} tickFormatter={(value) => formatValue(value, chart.valueFormat)} tickLine={false} tickMargin={RECHARTS_AXIS_TICK_MARGIN} tickSize={RECHARTS_AXIS_TICK_SIZE} ticks={waterfallYAxisScale?.ticks} width="auto" />
        <ReferenceLine y={0} stroke="var(--ds-chart-reference-line)" strokeWidth={1} />
        <Tooltip {...fastTooltipProps} content={<WaterfallTooltip chart={tooltipChart} />} cursor={subtleTooltipCursor} />
        <Bar
          background={{ fill: "transparent" }}
          dataKey="__waterfallRange"
          isAnimationActive={false}
          name={firstSeries.label ?? firstSeries.field}
          shape={renderWaterfallBarShape}
        />
      </BarChart>
    ) : horizontal && !stacked && (chart.type === "bar" || chart.type === "horizontalBar") ? (
      <BarChart {...chartProps} layout="vertical" margin={{ ...cartesianMargin, top: 0 }}>
        <CartesianGrid horizontal={false} />
        <XAxis axisLine={false} label={horizontalValueAxisLabel} tickFormatter={(value) => formatValue(value, chart.valueFormat)} tickLine={false} tickMargin={RECHARTS_AXIS_TICK_MARGIN} tickSize={RECHARTS_AXIS_TICK_SIZE} ticks={yAxisScale.ticks} type="number" />
        <YAxis axisLine={false} dataKey={chart.xField} interval={0} label={horizontalCategoryAxisLabel} tickLine={false} tickMargin={RECHARTS_AXIS_TICK_MARGIN} tickSize={RECHARTS_AXIS_TICK_SIZE} type="category" width="auto" />
        {referenceLines(chart, true)}
        <Tooltip {...fastTooltipProps} content={<ChartTooltip chart={tooltipChart} getItemColor={resolveTooltipColor} />} cursor={subtleTooltipCursor} />
        {renderSeries()}
      </BarChart>
    ) : horizontal && stacked && (
      chart.type === "bar" ||
      chart.type === "horizontalStackedBar" ||
      chart.type === "horizontalStackedBar100"
    ) ? (
      <BarChart {...chartProps} layout="vertical" margin={cartesianMargin} stackOffset={normalized ? "expand" : undefined}>
        <CartesianGrid horizontal={false} />
        <XAxis axisLine={false} domain={normalized ? [0, 1] : undefined} label={horizontalValueAxisLabel} tickFormatter={(value) => formatValue(value, normalized ? "percent" : chart.valueFormat)} tickLine={false} tickMargin={RECHARTS_AXIS_TICK_MARGIN} tickSize={RECHARTS_AXIS_TICK_SIZE} type="number" />
        <YAxis axisLine={false} dataKey={chart.xField} interval={0} label={horizontalCategoryAxisLabel} tickLine={false} tickMargin={RECHARTS_AXIS_TICK_MARGIN} tickSize={RECHARTS_AXIS_TICK_SIZE} type="category" width="auto" />
        {referenceLines(chart, true)}
        <Tooltip {...fastTooltipProps} content={<ChartTooltip chart={tooltipChart} getItemColor={resolveTooltipColor} />} cursor={subtleTooltipCursor} />
        {renderSeries()}
      </BarChart>
    ) : chart.type === "funnel" ? (
      <FunnelChart {...chartProps} data={funnelRows} margin={{ bottom: 0, left: 24, right: 24, top: 0 }}>
        <Tooltip {...fastTooltipProps} content={<ChartTooltip chart={tooltipChart} getItemColor={resolveTooltipColor} />} cursor={subtleTooltipCursor} />
        <Funnel
          data={funnelRows}
          dataKey={firstSeries.field}
          fill={FUNNEL_STAGE_COLORS[0]}
          isAnimationActive={false}
          nameKey={chart.xField}
          shape={renderRoundedFunnelShape}
          stroke="none"
        >
          {funnelRows.map((row, index) => (
            <Cell key={`${chart.id}-funnel-stage-${index}`} fill={String(row.__funnelStageColor)} />
          ))}
          <LabelList content={renderFunnelCenterLabel} dataKey="__funnelPairLabel" position="center" />
        </Funnel>
      </FunnelChart>
    ) : chart.type === "pie" ? (
      <PieChart {...chartProps} data={pieRows} margin={{ bottom: 0, left: 0, right: 0, top: 0 }}>
        <Tooltip {...fastTooltipProps} content={<ChartTooltip chart={tooltipChart} getItemColor={resolveTooltipColor} />} cursor={subtleTooltipCursor} />
        <Pie data={pieRows} dataKey="__pieValue" innerRadius="42%" isAnimationActive={false} nameKey="__pieName" outerRadius="78%">
          {pieRows.map((row) => (
            <Cell fill={getSeriesColor(chart, firstSeries, asFiniteNumber(row.__pieIndex))} key={`${chart.id}-pie-${row.__pieIndex}`} />
          ))}
        </Pie>
      </PieChart>
    ) : chart.type === "sparkline" ? (
      <AreaChart {...chartProps} margin={{ bottom: 20, left: 8, right: 8, top: 18 }}>
        {renderAreaGradientDefs(chart)}
        <XAxis dataKey={chart.xField} hide />
        <YAxis hide />
        <Tooltip {...fastTooltipProps} content={<ChartTooltip chart={tooltipChart} getItemColor={resolveTooltipColor} />} cursor={subtleTooltipCursor} />
        <Area dataKey={firstSeries.field} dot={false} fill={`url(#${getAreaGradientId(chart, firstSeries)})`} fillOpacity={1} isAnimationActive={false} name={firstSeries.label ?? firstSeries.field} stroke={getSeriesColor(chart, firstSeries, 0)} strokeDasharray={getSeriesStrokeDasharray(chart, firstSeries)} strokeWidth={2} type="monotone" />
      </AreaChart>
    ) : chart.type === "histogram" || (!horizontal && (
      chart.type === "bar" ||
      chart.type === "stackedBar" ||
      chart.type === "stackedBar100"
    )) ? (
      <BarChart {...chartProps} barCategoryGap={chart.type === "histogram" ? 1 : undefined} stackOffset={normalized ? "expand" : undefined}>
        {renderAreaGradientDefs(chart)}
        <CartesianGrid vertical={false} />
        <XAxis {...xAxisProps} />
        {renderYAxis()}
        {referenceLines(chart)}
        <Tooltip {...fastTooltipProps} content={<ChartTooltip chart={tooltipChart} getItemColor={resolveTooltipColor} />} cursor={subtleTooltipCursor} />
        {renderSeries()}
      </BarChart>
    ) : chart.type === "scatter" ? (
      <ScatterChart {...chartProps}>
        <CartesianGrid vertical={false} />
        <XAxis axisLine={false} dataKey={chart.xField} label={xAxisLabel} name={chart.xAxisTitle ?? chart.xField} tickLine={false} tickMargin={RECHARTS_AXIS_TICK_MARGIN} tickSize={RECHARTS_AXIS_TICK_SIZE} type="number" />
        {renderYAxis(scatterYField ?? firstSeries.field)}
        {scatterSizeField ? <ZAxis dataKey={scatterSizeField} range={[72, 420]} type="number" /> : null}
        {referenceLines(chart)}
        <Tooltip {...fastTooltipProps} content={<ChartTooltip chart={tooltipChart} getItemColor={resolveTooltipColor} />} cursor={subtleTooltipCursor} />
        {activeSeries.map((series, index) => {
          const originalIndex = chart.series.findIndex((item) => item.field === series.field);
          const seriesRows = rows.filter((row) => asNumber(row[series.field]) != null);
          const scatterDataKey = scatterYField && seriesRows.some((row) => asNumber(row[scatterYField]) != null)
            ? scatterYField
            : series.field;
          return (
            <Scatter
              data={seriesRows}
              dataKey={scatterDataKey}
              fill={getSeriesColor(chart, series, originalIndex < 0 ? index : originalIndex)}
              isAnimationActive={false}
              key={`${chart.id}-${series.field}`}
              name={series.label ?? series.field}
            >
              {showScatterPointLabels && scatterLabelField ? (
                <LabelList content={renderScatterPointLabel} dataKey={scatterLabelField} />
              ) : null}
            </Scatter>
          );
        })}
      </ScatterChart>
    ) : chart.type === "area" || chart.type === "stackedArea" ? (
      <AreaChart {...chartProps}>
        {renderAreaGradientDefs(chart)}
        <CartesianGrid vertical={false} />
        <XAxis {...xAxisProps} />
        {renderYAxis()}
        {referenceLines(chart)}
        <Tooltip {...fastTooltipProps} content={<ChartTooltip chart={tooltipChart} getItemColor={resolveTooltipColor} />} cursor={subtleTooltipCursor} />
        {renderSeries()}
      </AreaChart>
    ) : (
      <LineChart {...chartProps}>
        <CartesianGrid vertical={false} />
        <XAxis {...xAxisProps} />
        {renderYAxis()}
        {referenceLines(chart)}
        <Tooltip {...fastTooltipProps} content={<ChartTooltip chart={tooltipChart} getItemColor={resolveTooltipColor} />} cursor={subtleTooltipCursor} />
        {renderSeries()}
      </LineChart>
    );

  return (
    <ChartFrame
      height={frameHeight}
      interactiveLegend={interactiveLegend}
      legendItems={legendItems}
      onVisibleChange={onVisibleSeriesChange}
      surface={resolvedSurface}
      visibleIds={visibleIds}
    >
      {responsive ? (
        <ResponsiveContainer height="100%" initialDimension={{ height: 1, width: 1 }} width="100%">
          {chartElement}
        </ResponsiveContainer>
      ) : (
        chartElement
      )}
    </ChartFrame>
  );
}
