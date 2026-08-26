import {
  Boxes,
  ChartArea,
  ChartBar,
  ChartColumn,
  ChartColumnStacked,
  ChartLine,
  ChartNoAxesColumn,
  ChartNoAxesCombined,
  ChartScatter,
  ChartSpline,
  Filter as FunnelIcon,
  Table2,
  Tally3,
} from "lucide-react";
import {
  chartTypeSectionsForOptions as sharedChartTypeSectionsForOptions,
  compatibleChartTypesForDataShape as sharedCompatibleChartTypesForDataShape,
  compatibleChartTypesFor as sharedCompatibleChartTypesFor,
  isChartType as sharedIsChartType,
} from "./chart-compatibility";
import { isDateAxisValue } from "./chart-transforms";

export const CHART_TYPE_LABELS = {
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

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function asNumber(value) {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string" && value.trim() !== "") {
    const numeric = Number(value.replace(/,/g, ""));
    if (Number.isFinite(numeric)) return numeric;
  }
  return null;
}

function plainObject(value) {
  return value && typeof value === "object" && !Array.isArray(value) ? value : {};
}

export function chartTypeIcon(type) {
  const iconProps = { "aria-hidden": true, size: 18, strokeWidth: 2 };
  if (type === "area") return <ChartArea {...iconProps} />;
  if (type === "bar") return <ChartColumn {...iconProps} />;
  if (type === "boxPlot") return <Boxes {...iconProps} />;
  if (type === "funnel") return <FunnelIcon {...iconProps} />;
  if (type === "heatmap") return <Table2 {...iconProps} />;
  if (type === "histogram") return <ChartNoAxesColumn {...iconProps} />;
  if (type === "horizontalBar") return <ChartBar {...iconProps} />;
  if (type === "horizontalStackedBar" || type === "horizontalStackedBar100") return <ChartColumnStacked {...iconProps} />;
  if (type === "leaderboard") return <Tally3 {...iconProps} />;
  if (type === "line") return <ChartLine {...iconProps} />;
  if (type === "pie") return <ChartNoAxesCombined {...iconProps} />;
  if (type === "scatter") return <ChartScatter {...iconProps} />;
  if (type === "sparkline") return <ChartSpline {...iconProps} />;
  if (type === "stackedArea") return <ChartArea {...iconProps} />;
  if (type === "stackedBar" || type === "stackedBar100") return <ChartColumnStacked {...iconProps} />;
  return <ChartNoAxesCombined {...iconProps} />;
}

function chartTypePreviewKind(type) {
  if (type === "boxPlot") return "box-plot";
  if (type === "horizontalBar") return "horizontal-bar";
  if (type === "horizontalStackedBar") return "horizontal-stacked-bar";
  if (type === "horizontalStackedBar100") return "horizontal-stacked-bar-100";
  if (type === "stackedArea") return "stacked-area";
  if (type === "stackedBar") return "stacked-bar";
  if (type === "stackedBar100") return "stacked-bar-100";
  return type;
}

export function chartTypePreviewIcon(type) {
  const kind = chartTypePreviewKind(type);
  const stroke = "currentColor";
  const fill = "color-mix(in srgb, currentColor 28%, transparent)";
  const fillStrong = "color-mix(in srgb, currentColor 48%, transparent)";
  const grid = <path d="M8 8v48h80" fill="none" opacity=".44" stroke={stroke} strokeLinecap="round" strokeWidth="3" />;
  const frame = (body) => (
    <svg aria-hidden="true" fill="none" viewBox="0 0 96 64">
      {grid}
      {body}
    </svg>
  );
  const rect = (x, y, width, height) => (
    <rect fill={fill} height={height} rx="2" stroke={stroke} strokeWidth="2.5" width={width} x={x} y={y} />
  );
  const segment = (x, y, width, height, strong = false, key) => (
    <rect fill={strong ? fillStrong : fill} height={height} key={key} rx="1.5" stroke={stroke} strokeWidth="2.2" width={width} x={x} y={y} />
  );
  if (kind === "bar") {
    return frame(<>{rect(18, 34, 7, 22)}{rect(28, 24, 7, 32)}{rect(47, 42, 7, 14)}{rect(57, 18, 7, 38)}{rect(76, 29, 7, 27)}</>);
  }
  if (kind === "stacked-bar" || kind === "stacked-bar-100") {
    return frame(<>{segment(20, 38, 12, 18)}{segment(20, 24, 12, 14, true)}{segment(45, 32, 12, 24)}{segment(45, 15, 12, 17, true)}{segment(70, 43, 12, 13)}{segment(70, 28, 12, 15, true)}</>);
  }
  if (kind === "horizontal-bar") {
    return frame(<>{rect(18, 16, 22, 6)}{rect(18, 25, 36, 6)}{rect(18, 40, 28, 6)}{rect(18, 49, 53, 6)}</>);
  }
  if (kind === "horizontal-stacked-bar" || kind === "horizontal-stacked-bar-100") {
    return frame(<>{segment(18, 18, 30, 9)}{segment(48, 18, 22, 9, true)}{segment(18, 39, 22, 9)}{segment(40, 39, 38, 9, true)}</>);
  }
  if (kind === "line" || kind === "sparkline") {
    return frame(<>
      <path d="M18 45 34 29l14 9 17-21 17 15" stroke={stroke} strokeLinecap="round" strokeLinejoin="round" strokeWidth="4" />
      {[["18", "45"], ["34", "29"], ["65", "17"], ["82", "32"]].map(([cx, cy]) => <circle cx={cx} cy={cy} fill={fillStrong} key={`${cx}-${cy}`} r="3" stroke={stroke} strokeWidth="2" />)}
    </>);
  }
  if (kind === "area" || kind === "stacked-area") {
    return frame(<>
      <path d="M18 47 34 35l14 8 18-23 17 10v26H18Z" fill={fill} />
      <path d="M18 47 34 35l14 8 18-23 17 10" stroke={stroke} strokeLinecap="round" strokeLinejoin="round" strokeWidth="4" />
    </>);
  }
  if (kind === "histogram") {
    const heights = [12, 22, 35, 29, 18, 9];
    return frame(<>{[16, 27, 38, 49, 60, 71].map((x, index) => segment(x, 56 - heights[index], 9, heights[index], index === 2 || index === 3, `hist-${index}`))}</>);
  }
  if (kind === "scatter") {
    return frame(<>{[[20, 45], [31, 34], [42, 40], [51, 25], [63, 31], [74, 18], [82, 28]].map(([cx, cy]) => <circle cx={cx} cy={cy} fill={fillStrong} key={`${cx}-${cy}`} r="4" stroke={stroke} strokeWidth="2.5" />)}</>);
  }
  if (kind === "heatmap") {
    return frame(<>{[0, 1, 2].flatMap((row) => [0, 1, 2, 3].map((col) => {
      const strong = (row + col) % 3 === 0;
      const opacity = [".18", ".3", ".46", ".62"][(row * 2 + col) % 4];
      return <rect fill={strong ? fillStrong : fill} height="10" key={`${row}-${col}`} opacity={opacity} rx="1.5" stroke={stroke} strokeWidth="1.8" width="13" x={18 + col * 16} y={16 + row * 12} />;
    }))}</>);
  }
  if (kind === "pie") {
    return <svg aria-hidden="true" fill="none" viewBox="0 0 96 64"><path d="M48 8a24 24 0 1 1-20.8 36" fill={fill} stroke={stroke} strokeLinejoin="round" strokeWidth="3" /><path d="M48 8v24l20.8 12A24 24 0 0 0 48 8Z" fill={fillStrong} stroke={stroke} strokeLinejoin="round" strokeWidth="3" /><path d="M48 32 27.2 44" stroke={stroke} strokeLinecap="round" strokeWidth="3" /></svg>;
  }
  if (kind === "funnel") {
    return <svg aria-hidden="true" fill="none" viewBox="0 0 96 64"><path d="M18 10h60L68 24H28Z" fill={fillStrong} stroke={stroke} strokeWidth="3" /><path d="M30 28h36L58 42H38Z" fill={fill} stroke={stroke} strokeWidth="3" /><path d="M40 46h16l-4 10h-8Z" fill={fill} stroke={stroke} strokeWidth="3" /></svg>;
  }
  if (kind === "waterfall") {
    return frame(<>{segment(18, 40, 12, 16)}{segment(38, 26, 12, 30, true)}{segment(58, 34, 12, 22)}{segment(78, 20, 8, 36, true)}</>);
  }
  if (kind === "leaderboard") {
    return frame(<>{segment(18, 17, 58, 8, true)}{segment(18, 31, 44, 8)}{segment(18, 45, 30, 8)}</>);
  }
  if (kind === "box-plot") {
    return frame(<><path d="M22 24h52M22 42h42" stroke={stroke} strokeLinecap="round" strokeWidth="3" /><rect fill={fill} height="12" rx="2" stroke={stroke} strokeWidth="2.5" width="24" x="34" y="18" /><rect fill={fillStrong} height="12" rx="2" stroke={stroke} strokeWidth="2.5" width="22" x="30" y="36" /></>);
  }
  return frame(rect(20, 22, 52, 28));
}

export function withChartType(chart, type) {
  return chart.type === type ? chart : { ...chart, type };
}

function chartWidgetBarType(type, settings) {
  const rawType = String(type ?? "").trim();
  if (rawType !== "bar") return sharedIsChartType(rawType) ? rawType : null;
  const orientation = String(settings?.orientation ?? "").toLowerCase();
  const groupMode = String(settings?.group_mode ?? settings?.groupMode ?? "").toLowerCase();
  if (orientation === "horizontal" && groupMode === "stacked100") return "horizontalStackedBar100";
  if (orientation === "horizontal" && groupMode === "stacked") return "horizontalStackedBar";
  if (orientation === "horizontal") return "horizontalBar";
  if (groupMode === "stacked100") return "stackedBar100";
  if (groupMode === "stacked") return "stackedBar";
  return "bar";
}

export function chartSpecOverrideFromWidgetSpec(chart, widgetSpec) {
  const spec = plainObject(widgetSpec);
  const encodings = plainObject(spec.encodings);
  const settings = plainObject(spec.settings);
  const originalSettings = plainObject(chart.settings);
  const override = {};
  const nextType = chartWidgetBarType(spec.visualization_type, settings);
  if (nextType && nextType !== chart.type) override.type = nextType;
  const chartFields = new Set(chartUsedFields(chart));
  const xField = plainObject(encodings.x).field;
  if (typeof xField === "string" && chartFields.has(xField) && xField !== chart.xField) override.xField = xField;
  const yField = plainObject(encodings.y).field;
  const currentSeries = asArray(chart.series);
  if (typeof yField === "string" && chartFields.has(yField) && currentSeries[0]?.field !== yField) {
    override.series = [{ ...currentSeries[0], field: yField, label: currentSeries.find((series) => series.field === yField)?.label ?? currentSeries[0]?.label ?? yField }];
  }
  const sizeField = plainObject(encodings.size).field;
  if (typeof sizeField === "string" && chartFields.has(sizeField) && chartEncodingField(chart, "size") !== sizeField) {
    override.encodings = { ...plainObject(chart.encodings), size: { ...plainObject(chartEncoding(chart, "size")), field: sizeField } };
  }
  const nextSettings = {};
  const orientation = settings.orientation === "horizontal" || settings.orientation === "vertical" ? settings.orientation : null;
  if (orientation && originalSettings.orientation !== orientation) nextSettings.orientation = orientation;
  const groupMode = settings.group_mode ?? settings.groupMode;
  if (["grouped", "stacked", "stacked100"].includes(groupMode) && originalSettings.groupMode !== groupMode) nextSettings.groupMode = groupMode;
  if (Object.keys(nextSettings).length) override.settings = { ...originalSettings, ...nextSettings };
  return override;
}

export function applyChartSpecOverride(chart, override) {
  if (!override || typeof override !== "object") return chart;
  return {
    ...chart,
    ...(sharedIsChartType(override.type) ? { type: override.type } : {}),
    ...(typeof override.xField === "string" ? { xField: override.xField } : {}),
    ...(override.encodings && typeof override.encodings === "object" ? { encodings: { ...chart.encodings, ...override.encodings } } : {}),
    ...(Array.isArray(override.series) && override.series.length ? { series: override.series } : {}),
    ...(override.settings && typeof override.settings === "object" ? { settings: { ...chart.settings, ...override.settings } } : {}),
  };
}

export function chartEncoding(chart, role) {
  return chart?.encodings && typeof chart.encodings === "object" && chart.encodings[role] && typeof chart.encodings[role] === "object" ? chart.encodings[role] : {};
}

export function chartEncodingField(chart, role) {
  const field = chartEncoding(chart, role).field;
  return typeof field === "string" && field.trim() ? field : null;
}

export function chartEncodingFields(chart, role) {
  const encoding = chartEncoding(chart, role);
  return Array.isArray(encoding.fields) ? encoding.fields.filter((field) => typeof field === "string" && field.trim()) : [];
}

export function chartEncodingLabel(chart, role, fallback) {
  const label = chartEncoding(chart, role).label;
  return typeof label === "string" && label.trim() ? label : fallback;
}

function chartEncodingAxisTitle(chart, role, fallback) {
  const label = chartEncodingLabel(chart, role, fallback);
  const unit = (
    chartEncoding(chart, role).unit ??
    (role === "y" ? chart.unit : undefined)
  )?.trim();
  if (!unit || label.toLowerCase().includes(unit.toLowerCase())) return label;
  return `${label} (${unit})`;
}

function chartTooltipEncodings(chart) {
  return Array.isArray(chart?.encodings?.tooltip) ? chart.encodings.tooltip : [];
}

export function chartHasEncodingSpec(chart) {
  return Boolean(chart?.encodings && typeof chart.encodings === "object" && chartEncodingField(chart, "x") && (chartEncodingField(chart, "y") || chartEncodingFields(chart, "y").length));
}

export function chartUsedFields(chart) {
  const fields = [
    chart.xField,
    ...asArray(chart.series).map((series) => series?.field),
    chartEncodingField(chart, "x"),
    chartEncodingField(chart, "y"),
    ...chartEncodingFields(chart, "y"),
    chartEncodingField(chart, "color"),
    chartEncodingField(chart, "lineStyle"),
    chartEncodingField(chart, "size"),
    chartEncodingField(chart, "facet"),
    chartEncodingField(chart, "label"),
    ...chartTooltipEncodings(chart).map((tooltip) => tooltip?.field),
  ];
  return [...new Set(fields.filter((field) => typeof field === "string" && field.trim()))];
}

function syntheticSeriesField(value, index) {
  const slug = String(value ?? "value").toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "").slice(0, 40);
  return `__series_${index}_${slug || "value"}`;
}

function normalizedLineStyle(value) {
  return value === "solid" || value === "dashed" || value === "dotted" ? value : undefined;
}

function rowLineStyle(row, lineStyleField) {
  return lineStyleField ? normalizedLineStyle(row?.[lineStyleField]) : undefined;
}

function inferredSeriesRole(value) {
  const normalized = String(value ?? "").trim().toLowerCase();
  if (/\b(actual|actuals|observed)\b/.test(normalized)) return "actual";
  if (/\b(baseline|benchmark)\b/.test(normalized)) return "baseline";
  if (/\b(target|goal)\b/.test(normalized)) return "target";
  if (/\b(estimate|estimated|forecast|projected|projection)\b/.test(normalized)) return "forecast";
  if (/\b(plan|planned|budget|quota)\b/.test(normalized)) return "plan";
  return undefined;
}

function isSignedCategoryValue(value) {
  const normalized = String(value ?? "").trim().toLowerCase();
  return normalized === "positive" || normalized === "negative" || normalized === "neutral" || normalized === "zero";
}

function shouldKeepSignedBarAsSingleSeries(chart, rows, colorField) {
  if (chart.type !== "bar" && chart.type !== "horizontalBar") return false;
  const colorLabel = `${colorField ?? ""} ${chartEncodingLabel(chart, "color", "")}`.toLowerCase();
  if (!colorLabel.includes("movement") && !colorLabel.includes("direction") && !colorLabel.includes("sign")) return false;
  let observed = false;
  for (const row of rows) {
    const value = row[colorField];
    if (value == null || value === "") continue;
    observed = true;
    if (!isSignedCategoryValue(value)) return false;
  }
  return observed;
}

function isHorizontalBarChart(chart) {
  return (
    chart.type === "horizontalBar" ||
    chart.type === "horizontalStackedBar" ||
    chart.type === "horizontalStackedBar100" ||
    (chart.type === "bar" && chart.settings?.orientation === "horizontal")
  );
}

function axisTitlesForEncodedChart(chart, xField, yField) {
  const horizontal = isHorizontalBarChart(chart);
  const encodedXAxisTitle = chartEncodingAxisTitle(chart, "x", xField);
  const encodedYAxisTitle = chartEncodingAxisTitle(chart, "y", yField);
  return {
    xAxisTitle: chart.xAxisTitle ?? (horizontal ? encodedYAxisTitle : encodedXAxisTitle),
    yAxisTitle: chart.yAxisTitle ?? (horizontal ? encodedXAxisTitle : encodedYAxisTitle),
  };
}

export function rechartsChartFromEncodedSpec(chart, rows) {
  if (!chartHasEncodingSpec(chart)) return { chart, rows };
  const xField = chartEncodingField(chart, "x");
  const yField = chartEncodingField(chart, "y");
  const yFields = chartEncodingFields(chart, "y");
  const colorField = chartEncodingField(chart, "color");
  const lineStyleField = chartEncodingField(chart, "lineStyle");
  if (yFields.length) {
    const horizontal = isHorizontalBarChart(chart);
    const xAxisTitle = chartEncodingAxisTitle(chart, "x", xField);
    const yAxisTitle = chartEncodingAxisTitle(chart, "y", "Value");
    return {
      chart: {
        ...chart,
        xField,
        xAxisTitle: chart.xAxisTitle ?? (horizontal ? yAxisTitle : xAxisTitle),
        yAxisTitle: chart.yAxisTitle ?? (horizontal ? xAxisTitle : yAxisTitle),
        series: yFields.map((field) => ({ field, label: field, semanticRole: inferredSeriesRole(field) })),
      },
      rows,
    };
  }
  if (!yField) return { chart, rows };
  if (chart.type === "funnel" || !colorField || shouldKeepSignedBarAsSingleSeries(chart, rows, colorField)) {
    const lineStyle = rowLineStyle(rows.find((row) => rowLineStyle(row, lineStyleField)), lineStyleField);
    const axisTitles = axisTitlesForEncodedChart(chart, xField, yField);
    return {
      chart: {
        ...chart,
        xField,
        ...axisTitles,
        series: [{ field: yField, label: chartEncodingLabel(chart, "y", yField), lineStyle, semanticRole: inferredSeriesRole(chartEncodingLabel(chart, "y", yField)) }],
      },
      rows,
    };
  }
  const seriesValues = [];
  const seriesLineStyles = new Map();
  for (const row of rows) {
    const value = row[colorField];
    if (value == null || value === "") continue;
    const key = String(value);
    if (!seriesValues.includes(key)) seriesValues.push(key);
    const lineStyle = rowLineStyle(row, lineStyleField);
    if (lineStyle && !seriesLineStyles.has(key)) seriesLineStyles.set(key, lineStyle);
  }
  const seriesFields = new Map(seriesValues.map((value, index) => [value, syntheticSeriesField(value, index)]));
  if (chart.type === "scatter") {
    const axisTitles = axisTitlesForEncodedChart(chart, xField, yField);
    return {
      chart: {
        ...chart,
        xField,
        ...axisTitles,
        series: seriesValues.map((value) => ({ field: seriesFields.get(value), label: value, lineStyle: seriesLineStyles.get(value), semanticRole: inferredSeriesRole(value) })),
      },
      rows: rows.map((row) => {
        const seriesField = seriesFields.get(String(row[colorField] ?? ""));
        return seriesField ? { ...row, [seriesField]: row[yField] } : row;
      }),
    };
  }
  const rowsByX = new Map();
  for (const row of rows) {
    const xValue = row[xField];
    const xKey = String(xValue ?? "");
    if (!rowsByX.has(xKey)) rowsByX.set(xKey, { [xField]: xValue });
    const seriesField = seriesFields.get(String(row[colorField] ?? ""));
    if (seriesField) rowsByX.get(xKey)[seriesField] = row[yField];
  }
  const axisTitles = axisTitlesForEncodedChart(chart, xField, yField);
  return {
    chart: {
      ...chart,
      xField,
      ...axisTitles,
      series: seriesValues.map((value) => ({ field: seriesFields.get(value), label: value, lineStyle: seriesLineStyles.get(value), semanticRole: inferredSeriesRole(value) })),
    },
    rows: [...rowsByX.values()],
  };
}

export function chartHasNumericSeries(chart, rows) {
  if (!rows.length) return false;
  return chart.series.every((series) => rows.some((row) => asNumber(row[series.field]) != null));
}

export function chartHasNonNegativeSeries(chart, rows) {
  let observed = false;
  for (const row of rows) {
    for (const series of chart.series) {
      const value = asNumber(row[series.field]);
      if (value == null) continue;
      observed = true;
      if (value < 0) return false;
    }
  }
  return observed;
}

export function hasNumericXAxis(chart, rows) {
  let observed = false;
  const xField = chartEncodingField(chart, "x") ?? chart.xField;
  for (const row of rows) {
    const value = row[xField];
    if (value == null) continue;
    observed = true;
    if (asNumber(value) == null) return false;
  }
  return observed;
}

function chartContextText(chart) {
  return `${chart.id} ${chart.title} ${chart.subtitle ?? ""} ${chartEncodingField(chart, "x") ?? chart.xField ?? ""}`.toLowerCase();
}

function chartHasContextMarker(chart, markers) {
  const context = chartContextText(chart);
  return markers.some((marker) => context.includes(marker));
}

export function hasTemporalXAxis(chart, rows) {
  if (chartHasContextMarker(chart, ["date", "day", "month", "quarter", "time", "week", "year", "period"])) return true;
  const xField = chartEncodingField(chart, "x") ?? chart.xField;
  return rows.some((row) => isDateAxisValue(row[xField]));
}

export function chartHasBoxPlotFields(chart) {
  const fields = new Set(asArray(chart.series).map((series) => series?.field).filter((field) => typeof field === "string").map((field) => field.toLowerCase()));
  return ["min", "q1", "median", "q3", "max"].every((marker) => [...fields].some((field) => field.includes(marker)));
}

export function compatibleChartTypesFor(chart, rows) {
  const rechartsChart = rechartsChartFromEncodedSpec(chart, rows);
  return sharedCompatibleChartTypesFor(rechartsChart.chart, rechartsChart.rows);
}

export function compatibleChartTypesForArtifactCard(chart, rows) {
  const rechartsChart = rechartsChartFromEncodedSpec(chart, rows);
  return sharedCompatibleChartTypesForDataShape(rechartsChart.chart, rechartsChart.rows);
}

export function chartTypeSectionsForOptions(options) {
  return sharedChartTypeSectionsForOptions(options);
}
