import type { CSSProperties } from "react";

export type ChartLegendItem = {
  color: string;
  id: string;
  lineStyle?: "solid" | "dashed" | "dotted";
  value: string;
};

function strokeDasharrayForLegend(lineStyle: ChartLegendItem["lineStyle"]) {
  if (lineStyle === "dotted") return "2 4";
  if (lineStyle === "dashed") return "6 5";
  return undefined;
}

function orderedVisibleIds(items: ChartLegendItem[], visibleIds: Set<string>): Set<string> {
  return new Set(items.map((item) => item.id).filter((id) => visibleIds.has(id)));
}

export function ChartLegend({
  interactive = false,
  items,
  onVisibleChange,
  position = "bottom",
  title,
  visibleIds,
}: {
  interactive?: boolean;
  items: ChartLegendItem[];
  onVisibleChange?: (visible: Set<string>) => void;
  position?: "bottom" | "right";
  title?: string;
  visibleIds?: Set<string>;
}) {
  if (!items.length) return null;
  const activeIds = visibleIds ?? new Set(items.map((item) => item.id));

  function toggle(id: string) {
    if (!interactive || !onVisibleChange) return;
    const next = new Set(activeIds);
    if (next.has(id)) {
      if (next.size === 1) return;
      next.delete(id);
    }
    else next.add(id);
    onVisibleChange(orderedVisibleIds(items, next));
  }

  return (
    <div className={`chart-legend-wrap chart-legend-wrap--${position}`}>
      {title ? <div className="chart-legend-title">{title}</div> : null}
      <ul className="recharts-default-legend chart-legend">
        {items.map((item) => {
          const isVisible = activeIds.has(item.id);
          const markerStyle = { "--legend-color": item.color } as CSSProperties;
          const marker = item.lineStyle ? (
            <svg aria-hidden="true" className="chart-legend-line" style={markerStyle} viewBox="0 0 28 8">
              <line
                stroke="var(--legend-color)"
                strokeDasharray={strokeDasharrayForLegend(item.lineStyle)}
                strokeLinecap="round"
                strokeWidth="2.5"
                x1="1.5"
                x2="26.5"
                y1="4"
                y2="4"
              />
            </svg>
          ) : (
            <span aria-hidden="true" className="chart-legend-dot" style={markerStyle} />
          );
          return (
            <li className="recharts-legend-item chart-legend-item" key={item.id}>
              {interactive ? (
                <button
                  aria-pressed={isVisible}
                  className="chart-legend-button"
                  onClick={() => toggle(item.id)}
                  type="button"
                >
                  {marker}
                  <span>{item.value}</span>
                </button>
              ) : (
                <>
                  {marker}
                  <span>{item.value}</span>
                </>
              )}
            </li>
          );
        })}
      </ul>
    </div>
  );
}
