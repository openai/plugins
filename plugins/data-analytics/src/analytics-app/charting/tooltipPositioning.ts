export type ViewportRect = {
  bottom: number;
  left: number;
  right: number;
  top: number;
};

export type TooltipSize = {
  height: number;
  width: number;
};

export type ViewportSize = {
  height: number;
  width: number;
};

export type ViewportTooltipPosition = {
  left: number;
  placement: "above" | "below";
  top: number;
};

function clamp(value: number, minimum: number, maximum: number) {
  return Math.max(minimum, Math.min(maximum, value));
}

export function calculateViewportTooltipPosition({
  anchorRect,
  gap = 8,
  margin = 12,
  tooltipSize,
  viewport,
}: {
  anchorRect: ViewportRect;
  gap?: number;
  margin?: number;
  tooltipSize: TooltipSize;
  viewport: ViewportSize;
}): ViewportTooltipPosition {
  const maximumLeft = Math.max(margin, viewport.width - margin - tooltipSize.width);
  const maximumTop = Math.max(margin, viewport.height - margin - tooltipSize.height);
  const centeredLeft = anchorRect.left + (anchorRect.right - anchorRect.left - tooltipSize.width) / 2;
  const aboveTop = anchorRect.top - gap - tooltipSize.height;
  const belowTop = anchorRect.bottom + gap;
  const fitsAbove = aboveTop >= margin;
  const fitsBelow = belowTop <= maximumTop;
  const availableAbove = anchorRect.top - margin - gap;
  const availableBelow = viewport.height - margin - anchorRect.bottom - gap;
  const placement = fitsAbove || (!fitsBelow && availableAbove >= availableBelow) ? "above" : "below";
  const preferredTop = placement === "above" ? aboveTop : belowTop;

  return {
    left: clamp(centeredLeft, margin, maximumLeft),
    placement,
    top: clamp(preferredTop, margin, maximumTop),
  };
}
