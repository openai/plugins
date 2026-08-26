import {
  type CSSProperties,
  type PointerEvent as ReactPointerEvent,
  type ReactNode,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  useState
} from "react";

import {
  type AnalyticsLayoutItemState,
  type AnalyticsLayoutPlacement,
  type AnalyticsLayoutPlacementIntent,
  type AnalyticsLayoutWidth,
  normalize,
  packRows,
  predictPlacement
} from "./analyticsLayoutCore";
import { readPersistedValue, writePersistedValue } from "../runtimeEnvironment";

export type { AnalyticsLayoutWidth } from "./analyticsLayoutCore";

export type AnalyticsLayoutRenderActions = {
  setLayout: (layout: AnalyticsLayoutWidth) => void;
};

export type AnalyticsLayoutBlock = {
  className?: string;
  compactGroup?: string;
  defaultLayout?: AnalyticsLayoutWidth;
  id: string;
  render: (layout: AnalyticsLayoutWidth, actions: AnalyticsLayoutRenderActions) => ReactNode;
};

type AnalyticsLayoutDisplayRow = {
  compactGroup: string | null;
  items: AnalyticsLayoutItemState[];
};

type BlockRect = {
  bottom: number;
  height: number;
  left: number;
  right: number;
  top: number;
  width: number;
};

type DragSession = {
  currentPoint: { x: number; y: number };
  draggedId: string;
  intent: AnalyticsLayoutPlacementIntent;
  isStacked: boolean;
  pointerOffset: { x: number; y: number };
  previewItems: AnalyticsLayoutItemState[];
  rects: Map<string, BlockRect>;
  sourceRect: BlockRect;
  startItems: AnalyticsLayoutItemState[];
  targetId: string | null;
};

const STACK_BREAKPOINT_PX = 760;
const AUTO_SCROLL_EDGE_PX = 72;
const AUTO_SCROLL_STEP_PX = 18;
const REORDER_INSERT_BAND_RATIO = 0.3;
const SPLIT_SIDE_ZONE_RATIO = 0.4;
const SPLIT_INDICATOR_OUTSET_PX = 8;
const COMPACT_ITEM_MIN_WIDTH_PX = 280;
const COMPACT_ITEM_GAP_PX = 8;

function parseStoredLayout(storageKey: string | null): unknown {
  if (!storageKey) return undefined;
  const stored = readPersistedValue(storageKey);
  if (!stored) return undefined;
  try {
    return JSON.parse(stored);
  } catch {
    return undefined;
  }
}

function sameItems(first: AnalyticsLayoutItemState[], second: AnalyticsLayoutItemState[]) {
  return (
    first.length === second.length
    && first.every((item, index) => item.id === second[index]?.id && item.layout === second[index]?.layout)
  );
}

function compactGroupForItem(
  item: AnalyticsLayoutItemState,
  blockById: Map<string, AnalyticsLayoutBlock>
) {
  return blockById.get(item.id)?.compactGroup ?? null;
}

function buildDisplayRows(
  items: AnalyticsLayoutItemState[],
  blockById: Map<string, AnalyticsLayoutBlock>
): AnalyticsLayoutDisplayRow[] {
  const displayRows: AnalyticsLayoutDisplayRow[] = [];
  let index = 0;
  while (index < items.length) {
    const compactGroup = compactGroupForItem(items[index], blockById);
    if (compactGroup) {
      const compactItems: AnalyticsLayoutItemState[] = [];
      while (
        index < items.length
        && compactGroupForItem(items[index], blockById) === compactGroup
      ) {
        compactItems.push(items[index]);
        index += 1;
      }
      displayRows.push({ compactGroup, items: compactItems });
      continue;
    }

    const standardItems: AnalyticsLayoutItemState[] = [];
    while (index < items.length && !compactGroupForItem(items[index], blockById)) {
      standardItems.push(items[index]);
      index += 1;
    }
    for (const packedRow of packRows(standardItems)) {
      displayRows.push({ compactGroup: null, items: [...packedRow] });
    }
  }
  return displayRows;
}

function balancedCompactColumnCount(containerWidth: number, itemCount: number) {
  if (itemCount <= 1 || containerWidth <= 0) return 1;
  const fittingColumns = Math.max(
    1,
    Math.min(
      itemCount,
      Math.floor((containerWidth + COMPACT_ITEM_GAP_PX) / (COMPACT_ITEM_MIN_WIDTH_PX + COMPACT_ITEM_GAP_PX))
    )
  );
  if (fittingColumns <= 1 || fittingColumns === itemCount) return fittingColumns;

  let balancedColumns = fittingColumns;
  let fewestEmptyCells = (fittingColumns - (itemCount % fittingColumns)) % fittingColumns;
  for (let candidate = fittingColumns - 1; candidate >= 2; candidate -= 1) {
    const emptyCells = (candidate - (itemCount % candidate)) % candidate;
    if (emptyCells < fewestEmptyCells) {
      balancedColumns = candidate;
      fewestEmptyCells = emptyCells;
    }
  }
  return balancedColumns;
}

function rectFromElement(element: HTMLElement): BlockRect {
  const rect = element.getBoundingClientRect();
  return {
    bottom: rect.bottom,
    height: rect.height,
    left: rect.left,
    right: rect.right,
    top: rect.top,
    width: rect.width
  };
}

function distanceToRect(x: number, y: number, rect: BlockRect) {
  const dx = x < rect.left ? rect.left - x : x > rect.right ? x - rect.right : 0;
  const dy = y < rect.top ? rect.top - y : y > rect.bottom ? y - rect.bottom : 0;
  return Math.hypot(dx, dy);
}

function shouldCancelDrag(target: EventTarget | null, cancelSelector: string) {
  return target instanceof Element && Boolean(target.closest(cancelSelector));
}

function DragHandleIcon() {
  return (
    <svg
      aria-hidden="true"
      className="analytics-layout-grab-handle-icon"
      fill="none"
      focusable="false"
      height="24"
      viewBox="0 0 24 24"
      width="24"
    >
      <g transform="rotate(-90 12 12)">
        <circle cx="5" cy="8.5" fill="currentColor" r="2" />
        <circle cx="12" cy="8.5" fill="currentColor" r="2" />
        <circle cx="19" cy="8.5" fill="currentColor" r="2" />
        <circle cx="5" cy="15.5" fill="currentColor" r="2" />
        <circle cx="12" cy="15.5" fill="currentColor" r="2" />
        <circle cx="19" cy="15.5" fill="currentColor" r="2" />
      </g>
    </svg>
  );
}

export function AnalyticsLayoutCanvas({
  ariaLabel,
  blocks,
  cancelSelector,
  className,
  isEditMode = false,
  itemClassName,
  layoutResetKey = 0,
  onLayoutChange,
  persistedLayout,
  persistenceVersion = 0,
  storageKey
}: {
  ariaLabel: string;
  blocks: AnalyticsLayoutBlock[];
  cancelSelector: string;
  className?: string;
  isEditMode?: boolean;
  itemClassName?: (block: AnalyticsLayoutBlock, layout: AnalyticsLayoutWidth) => string;
  layoutResetKey?: number;
  onLayoutChange?: (items: AnalyticsLayoutItemState[], reason: "normalize" | "user") => void;
  persistedLayout?: AnalyticsLayoutItemState[] | null;
  persistenceVersion?: number;
  storageKey: string | null;
}) {
  const [items, setItems] = useState<AnalyticsLayoutItemState[]>(() => normalize(blocks));
  const [dragSession, setDragSession] = useState<DragSession | null>(null);
  const [canvasWidth, setCanvasWidth] = useState(0);
  const blockById = useMemo(() => new Map(blocks.map((block) => [block.id, block])), [blocks]);
  const canvasRef = useRef<HTMLDivElement | null>(null);
  const itemRefs = useRef(new Map<string, HTMLElement>());
  const dragSessionRef = useRef<DragSession | null>(null);
  const dragFrameRef = useRef<number | null>(null);
  const dragPointRef = useRef<{ x: number; y: number } | null>(null);
  const layoutLoadRef = useRef<{
    layoutResetKey: number;
    persistenceVersion: number;
    storageKey: string | null;
  } | null>(null);
  const onLayoutChangeRef = useRef(onLayoutChange);

  useEffect(() => {
    onLayoutChangeRef.current = onLayoutChange;
  }, [onLayoutChange]);

  useLayoutEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const updateWidth = () => {
      const nextWidth = Math.floor(canvas.getBoundingClientRect().width);
      setCanvasWidth((currentWidth) => currentWidth === nextWidth ? currentWidth : nextWidth);
    };
    updateWidth();
    if (typeof ResizeObserver === "undefined") {
      window.addEventListener("resize", updateWidth);
      return () => window.removeEventListener("resize", updateWidth);
    }
    const observer = new ResizeObserver(updateWidth);
    observer.observe(canvas);
    return () => observer.disconnect();
  }, []);

  useLayoutEffect(() => {
    const previousLoad = layoutLoadRef.current;
    const shouldReloadStoredLayout =
      !previousLoad
      || previousLoad.layoutResetKey !== layoutResetKey
      || previousLoad.persistenceVersion !== persistenceVersion
      || previousLoad.storageKey !== storageKey;
    layoutLoadRef.current = { layoutResetKey, persistenceVersion, storageKey };
    setItems((currentItems) => {
      const nextItems = normalize(
        blocks,
        shouldReloadStoredLayout ? persistedLayout ?? parseStoredLayout(storageKey) : currentItems
      );
      onLayoutChangeRef.current?.(nextItems, "normalize");
      return nextItems;
    });
  }, [blocks, layoutResetKey, persistedLayout, persistenceVersion, storageKey]);

  useEffect(() => {
    dragSessionRef.current = dragSession;
  }, [dragSession]);

  useEffect(() => {
    if (!dragSession) return;
    function refreshMeasuredRects() {
      const session = dragSessionRef.current;
      const canvas = canvasRef.current;
      if (!session || !canvas) return;
      const nextSession: DragSession = {
        ...session,
        isStacked: canvas.getBoundingClientRect().width < STACK_BREAKPOINT_PX,
        rects: measureBlockRects()
      };
      dragSessionRef.current = nextSession;
      setDragSession(nextSession);
    }
    window.addEventListener("resize", refreshMeasuredRects);
    window.addEventListener("scroll", refreshMeasuredRects, true);
    return () => {
      window.removeEventListener("resize", refreshMeasuredRects);
      window.removeEventListener("scroll", refreshMeasuredRects, true);
    };
  }, [dragSession?.draggedId]);

  useEffect(() => {
    return () => {
      if (dragFrameRef.current != null) window.cancelAnimationFrame(dragFrameRef.current);
    };
  }, []);

  const rows = buildDisplayRows(items, blockById);

  function measureBlockRects() {
    const rects = new Map<string, BlockRect>();
    itemRefs.current.forEach((element, id) => {
      rects.set(id, rectFromElement(element));
    });
    return rects;
  }

  function commitItems(nextItems: AnalyticsLayoutItemState[]) {
    const normalizedItems = normalize(blocks, nextItems);
    setItems(normalizedItems);
    onLayoutChangeRef.current?.(normalizedItems, "user");
    if (!isEditMode && storageKey) {
      writePersistedValue(storageKey, JSON.stringify(normalizedItems));
    }
  }

  function setBlockLayout(blockId: string, layout: AnalyticsLayoutWidth) {
    commitItems(items.map((item) => (item.id === blockId ? { ...item, layout } : item)));
  }

  function findPlacement(
    clientX: number,
    clientY: number,
    session: DragSession,
    rects: Map<string, BlockRect>
  ): AnalyticsLayoutPlacement {
    const candidates = [...rects.entries()]
      .filter(([id]) => id !== session.draggedId)
      .sort((first, second) => first[1].top - second[1].top || first[1].left - second[1].left);
    if (!candidates.length) {
      return { draggedId: session.draggedId, intent: "end" };
    }

    const firstRect = candidates[0][1];
    const lastRect = candidates[candidates.length - 1][1];

    let targetId = candidates[0][0];
    let targetRect = candidates[0][1];
    let bestDistance = Number.POSITIVE_INFINITY;
    for (const [id, rect] of candidates) {
      const distance = distanceToRect(clientX, clientY, rect);
      if (distance < bestDistance) {
        bestDistance = distance;
        targetId = id;
        targetRect = rect;
      }
    }

    const sideBand = targetRect.width * SPLIT_SIDE_ZONE_RATIO;
    const isInsideTargetHeight = clientY >= targetRect.top && clientY <= targetRect.bottom;
    const insertBand = Math.min(targetRect.height * REORDER_INSERT_BAND_RATIO, targetRect.height / 2);
    const isBeforeBand = isInsideTargetHeight && clientY < targetRect.top + insertBand;
    const isAfterBand = isInsideTargetHeight && clientY > targetRect.bottom - insertBand;
    if (isBeforeBand) {
      return { draggedId: session.draggedId, intent: "before", targetId };
    }
    if (isAfterBand) {
      return { draggedId: session.draggedId, intent: "after", targetId };
    }
    if (!session.isStacked && isInsideTargetHeight && clientX < targetRect.left + sideBand) {
      return { draggedId: session.draggedId, intent: "pair-before", targetId };
    }
    if (!session.isStacked && isInsideTargetHeight && clientX > targetRect.right - sideBand) {
      return { draggedId: session.draggedId, intent: "pair-after", targetId };
    }

    if (clientY < firstRect.top + firstRect.height / 2) {
      return { draggedId: session.draggedId, intent: "before", targetId: candidates[0][0] };
    }
    if (clientY > lastRect.top + lastRect.height / 2) {
      return { draggedId: session.draggedId, intent: "end" };
    }

    const targetItem = session.startItems.find((item) => item.id === targetId);
    if (targetItem?.layout === "half") {
      const targetCenterX = targetRect.left + targetRect.width / 2;
      return {
        draggedId: session.draggedId,
        intent: clientX < targetCenterX ? "before" : "after",
        targetId
      };
    }

    const targetCenterY = targetRect.top + targetRect.height / 2;
    return {
      draggedId: session.draggedId,
      intent: clientY < targetCenterY ? "before" : "after",
      targetId
    };
  }

  function autoScroll(clientY: number) {
    if (clientY < AUTO_SCROLL_EDGE_PX) {
      window.scrollBy({ top: -AUTO_SCROLL_STEP_PX });
    } else if (clientY > window.innerHeight - AUTO_SCROLL_EDGE_PX) {
      window.scrollBy({ top: AUTO_SCROLL_STEP_PX });
    }
  }

  function applyDragPoint(clientX: number, clientY: number) {
    const session = dragSessionRef.current;
    if (!session) return;
    autoScroll(clientY);
    const rects = measureBlockRects();
    const placement = findPlacement(clientX, clientY, session, rects);
    const predictedItems = predictPlacement(session.startItems, placement);
    const previewChanged = !sameItems(predictedItems, session.previewItems);
    const previewItems = previewChanged ? predictedItems : session.previewItems;
    const nextSession: DragSession = {
      ...session,
      currentPoint: { x: clientX, y: clientY },
      intent: placement.intent,
      previewItems,
      rects,
      targetId: placement.targetId ?? null
    };
    dragSessionRef.current = nextSession;
    setDragSession(nextSession);
  }

  function scheduleDragPoint(clientX: number, clientY: number) {
    dragPointRef.current = { x: clientX, y: clientY };
    if (dragFrameRef.current != null) return;
    dragFrameRef.current = window.requestAnimationFrame(() => {
      dragFrameRef.current = null;
      const point = dragPointRef.current;
      if (!point) return;
      applyDragPoint(point.x, point.y);
    });
  }

  function startDragSession(event: ReactPointerEvent<HTMLElement>, blockId: string) {
    if (!isEditMode) return;
    if (event.pointerType === "mouse" && event.button !== 0) return;
    if (shouldCancelDrag(event.target, cancelSelector)) return;
    const element = itemRefs.current.get(blockId);
    const canvas = canvasRef.current;
    if (!element || !canvas) return;
    event.preventDefault();
    element.setPointerCapture?.(event.pointerId);
    const sourceRect = rectFromElement(element);
    const rects = measureBlockRects();
    const canvasRect = canvas.getBoundingClientRect();
    const startItems = normalize(blocks, items);
    const session: DragSession = {
      currentPoint: { x: event.clientX, y: event.clientY },
      draggedId: blockId,
      intent: "end",
      isStacked: canvasRect.width < STACK_BREAKPOINT_PX,
      pointerOffset: {
        x: event.clientX - sourceRect.left,
        y: event.clientY - sourceRect.top
      },
      previewItems: startItems,
      rects,
      sourceRect,
      startItems,
      targetId: null
    };
    dragSessionRef.current = session;
    setDragSession(session);
  }

  function handlePointerDown(event: ReactPointerEvent<HTMLDivElement>, blockId: string) {
    startDragSession(event, blockId);
  }

  function finishDrag(commit: boolean) {
    const session = dragSessionRef.current;
    if (dragFrameRef.current != null) {
      window.cancelAnimationFrame(dragFrameRef.current);
      dragFrameRef.current = null;
    }
    dragPointRef.current = null;
    dragSessionRef.current = null;
    setDragSession(null);
    if (commit && session) {
      commitItems(session.previewItems);
    }
  }

  function handlePointerMove(event: ReactPointerEvent<HTMLDivElement>) {
    if (!dragSessionRef.current) return;
    event.preventDefault();
    scheduleDragPoint(event.clientX, event.clientY);
  }

  function ghostStyle(session: DragSession): CSSProperties {
    return {
      height: session.sourceRect.height,
      left: session.currentPoint.x - session.pointerOffset.x,
      top: session.currentPoint.y - session.pointerOffset.y,
      width: session.sourceRect.width
    };
  }

  function dropIndicatorStyle(session: DragSession): { className: string; style: CSSProperties } | null {
    if (session.intent === "hold") return null;
    const canvas = canvasRef.current;
    if (!canvas) return null;
    const canvasRect = canvas.getBoundingClientRect();
    const candidates = [...session.rects.entries()]
      .filter(([id]) => id !== session.draggedId)
      .sort((first, second) => first[1].top - second[1].top || first[1].left - second[1].left);
    if (!candidates.length) return null;

    if (session.intent === "pair-before" || session.intent === "pair-after") {
      if (!session.targetId) return null;
      const targetRect = session.rects.get(session.targetId);
      if (!targetRect) return null;
      const lineX = session.intent === "pair-before"
        ? targetRect.left - SPLIT_INDICATOR_OUTSET_PX
        : targetRect.right + SPLIT_INDICATOR_OUTSET_PX;
      return {
        className: "analytics-layout-drop-indicator is-split",
        style: {
          height: targetRect.height,
          left: lineX - canvasRect.left,
          top: targetRect.top - canvasRect.top
        }
      };
    }

    const targetRect = session.targetId
      ? session.rects.get(session.targetId)
      : candidates[candidates.length - 1]?.[1];
    if (!targetRect) return null;
    const lineY = session.intent === "before"
      ? targetRect.top
      : targetRect.bottom;
    return {
      className: "analytics-layout-drop-indicator is-reorder",
      style: {
        left: 0,
        top: lineY - canvasRect.top,
        width: canvasRect.width
      }
    };
  }

  const dropIndicator = dragSession ? dropIndicatorStyle(dragSession) : null;

  return (
    <section
      aria-label={ariaLabel}
      className={`analytics-layout-canvas ${isEditMode ? "is-edit-mode" : ""} ${dragSession ? "is-layout-dragging" : ""} ${className ?? ""}`.trim()}
      data-analytics-layout-canvas
      data-edit-mode={isEditMode ? "true" : "false"}
      onPointerCancel={() => finishDrag(false)}
      onPointerMove={handlePointerMove}
      onPointerUp={() => finishDrag(true)}
      ref={canvasRef}
    >
      {dropIndicator ? (
        <div
          aria-hidden="true"
          className={dropIndicator.className}
          data-image-export-exclude="true"
          style={dropIndicator.style}
        />
      ) : null}
      {rows.map((row, rowIndex) => {
        const compactColumns = row.compactGroup
          ? balancedCompactColumnCount(canvasWidth, row.items.length)
          : null;
        const rowStyle = compactColumns
          ? { "--analytics-compact-columns": compactColumns } as CSSProperties
          : undefined;
        return (
          <div
            className={`analytics-layout-row ${row.compactGroup ? "is-compact-row" : row.items.length === 2 ? "is-half-row" : "is-full-row"}`}
            data-compact-columns={compactColumns ?? undefined}
            data-compact-group={row.compactGroup ?? undefined}
            key={row.items.map((item) => item.id).join(":")}
            style={rowStyle}
          >
            {row.items.map((item) => {
              const block = blockById.get(item.id);
              if (!block) return null;
              const isDragged = dragSession?.draggedId === item.id;
              const isTarget = dragSession?.targetId === item.id;
              const rendered = block.render(item.layout, {
                setLayout: (nextLayout) => setBlockLayout(item.id, nextLayout)
              });
              return (
                <div
                  className={`analytics-layout-item layout-${item.layout} ${block.className ?? ""} ${itemClassName?.(block, item.layout) ?? ""} ${isDragged ? "is-dragging" : ""} ${isTarget ? `is-drop-target intent-zone-${dragSession?.intent}` : ""}`.trim()}
                  data-analytics-layout-item
                  data-artifact-block-id={item.id}
                  data-layout-block-id={item.id}
                  data-layout-row-index={rowIndex}
                  data-layout-width={item.layout}
                  key={item.id}
                  ref={(node) => {
                    if (node) itemRefs.current.set(item.id, node);
                    else itemRefs.current.delete(item.id);
                  }}
                >
                  {isEditMode ? (
                    <div
                      aria-hidden="true"
                      className="analytics-layout-grab-handle"
                      data-image-export-exclude="true"
                      onPointerDown={(event) => handlePointerDown(event, item.id)}
                      title="Drag to reorder"
                    >
                      <DragHandleIcon />
                    </div>
                  ) : null}
                  <div className="analytics-layout-item-shell">
                    {rendered}
                  </div>
                </div>
              );
            })}
          </div>
        );
      })}
      {dragSession ? (
        <div
          aria-hidden="true"
          className="analytics-layout-ghost"
          data-image-export-exclude="true"
          style={ghostStyle(dragSession)}
        >
          {blockById.get(dragSession.draggedId)?.render(
            dragSession.startItems.find((item) => item.id === dragSession.draggedId)?.layout ?? "full",
            { setLayout: () => undefined }
          )}
        </div>
      ) : null}
    </section>
  );
}
