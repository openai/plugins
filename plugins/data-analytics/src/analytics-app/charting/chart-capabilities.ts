import type { ChartPaletteKind, ChartType } from "./chart-contract";

export type ChartCapability =
  | "axisFormatting"
  | "categoryColor"
  | "interactiveLegend"
  | "referenceLines"
  | "seriesLineStyle"
  | "stacking"
  | "timeSeries"
  | "valueLabels";

export type ChartCapabilitySpec = {
  capabilities: ChartCapability[];
  paletteKinds: ChartPaletteKind[];
};

const TREND_PALETTES: ChartPaletteKind[] = ["categorical", "semantic", "identity"];
const COMPARISON_PALETTES: ChartPaletteKind[] = ["categorical", "semantic", "identity"];
const INTENSITY_PALETTES: ChartPaletteKind[] = ["sequential", "diverging"];

export const CHART_CAPABILITIES: Record<ChartType, ChartCapabilitySpec> = {
  area: {
    capabilities: ["axisFormatting", "interactiveLegend", "referenceLines", "seriesLineStyle", "timeSeries", "valueLabels"],
    paletteKinds: TREND_PALETTES,
  },
  bar: {
    capabilities: ["axisFormatting", "categoryColor", "interactiveLegend", "referenceLines", "stacking", "valueLabels"],
    paletteKinds: COMPARISON_PALETTES,
  },
  boxPlot: {
    capabilities: ["axisFormatting"],
    paletteKinds: ["semantic", "identity"],
  },
  funnel: {
    capabilities: [],
    paletteKinds: ["sequential", "identity"],
  },
  heatmap: {
    capabilities: ["axisFormatting"],
    paletteKinds: INTENSITY_PALETTES,
  },
  histogram: {
    capabilities: ["axisFormatting", "referenceLines", "valueLabels"],
    paletteKinds: ["sequential", "semantic", "identity"],
  },
  horizontalBar: {
    capabilities: ["axisFormatting", "categoryColor", "interactiveLegend", "referenceLines", "valueLabels"],
    paletteKinds: COMPARISON_PALETTES,
  },
  horizontalStackedBar: {
    capabilities: ["axisFormatting", "interactiveLegend", "referenceLines", "stacking", "valueLabels"],
    paletteKinds: COMPARISON_PALETTES,
  },
  horizontalStackedBar100: {
    capabilities: ["axisFormatting", "interactiveLegend", "referenceLines", "stacking", "valueLabels"],
    paletteKinds: COMPARISON_PALETTES,
  },
  leaderboard: {
    capabilities: ["axisFormatting"],
    paletteKinds: ["semantic", "identity"],
  },
  line: {
    capabilities: ["axisFormatting", "interactiveLegend", "referenceLines", "seriesLineStyle", "timeSeries", "valueLabels"],
    paletteKinds: TREND_PALETTES,
  },
  pie: {
    capabilities: [],
    paletteKinds: COMPARISON_PALETTES,
  },
  scatter: {
    capabilities: ["axisFormatting", "interactiveLegend", "referenceLines"],
    paletteKinds: COMPARISON_PALETTES,
  },
  sparkline: {
    capabilities: ["seriesLineStyle", "timeSeries", "valueLabels"],
    paletteKinds: TREND_PALETTES,
  },
  stackedArea: {
    capabilities: ["axisFormatting", "interactiveLegend", "referenceLines", "seriesLineStyle", "stacking", "timeSeries", "valueLabels"],
    paletteKinds: COMPARISON_PALETTES,
  },
  stackedBar: {
    capabilities: ["axisFormatting", "interactiveLegend", "referenceLines", "stacking", "valueLabels"],
    paletteKinds: COMPARISON_PALETTES,
  },
  stackedBar100: {
    capabilities: ["axisFormatting", "interactiveLegend", "referenceLines", "stacking", "valueLabels"],
    paletteKinds: COMPARISON_PALETTES,
  },
  waterfall: {
    capabilities: ["axisFormatting", "referenceLines"],
    paletteKinds: ["diverging", "semantic", "identity"],
  },
};

export function chartCapabilitiesFor(type: ChartType): ChartCapabilitySpec {
  return CHART_CAPABILITIES[type];
}

export function chartSupportsCapability(type: ChartType, capability: ChartCapability): boolean {
  return chartCapabilitiesFor(type).capabilities.includes(capability);
}

export function chartSupportsPaletteKind(type: ChartType, paletteKind: ChartPaletteKind): boolean {
  return chartCapabilitiesFor(type).paletteKinds.includes(paletteKind);
}
