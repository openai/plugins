import type { CSSProperties, ReactNode } from "react";
import type { ChartSurface } from "./chart-contract";
import { ChartLegend, type ChartLegendItem } from "./ChartLegend";

export function ChartFrame({
  children,
  className = "",
  height,
  interactiveLegend = false,
  legendItems = [],
  legendPosition = "bottom",
  legendTitle,
  onVisibleChange,
  surface = "card",
  visibleIds,
}: {
  children: ReactNode;
  className?: string;
  height?: number | string;
  interactiveLegend?: boolean;
  legendItems?: ChartLegendItem[];
  legendPosition?: "bottom" | "right";
  legendTitle?: string;
  onVisibleChange?: (visible: Set<string>) => void;
  surface?: ChartSurface;
  visibleIds?: Set<string>;
}) {
  const frameStyle = height == null ? undefined : ({ height } as CSSProperties);
  const showLegend = legendItems.length > 0;
  return (
    <div
      className={[
        "chart-frame",
        `chart-frame--${surface}`,
        showLegend ? "chart-frame--with-legend" : "",
        showLegend && legendPosition === "right" ? "chart-frame--legend-right" : "",
        className,
      ].filter(Boolean).join(" ")}
      style={frameStyle}
    >
      <div className="chart-plot">{children}</div>
      {showLegend ? (
        <ChartLegend
          interactive={interactiveLegend}
          items={legendItems}
          position={legendPosition}
          title={legendTitle}
          onVisibleChange={onVisibleChange}
          visibleIds={visibleIds}
        />
      ) : null}
    </div>
  );
}
