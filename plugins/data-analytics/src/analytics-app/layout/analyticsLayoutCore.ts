export type AnalyticsLayoutWidth = "full" | "half";

export type AnalyticsLayoutItemState = {
  id: string;
  layout: AnalyticsLayoutWidth;
};

export type AnalyticsLayoutBlockSource = {
  id: string;
  defaultLayout?: AnalyticsLayoutWidth;
};

export type AnalyticsLayoutPlacementIntent =
  | "after"
  | "before"
  | "end"
  | "hold"
  | "pair-after"
  | "pair-before";

export type AnalyticsLayoutPlacement = {
  draggedId: string;
  intent: AnalyticsLayoutPlacementIntent;
  targetId?: string | null;
};

function isLayoutWidth(value: unknown): value is AnalyticsLayoutWidth {
  return value === "full" || value === "half";
}

function uniqueKnownBlocks(blocks: AnalyticsLayoutBlockSource[]): AnalyticsLayoutBlockSource[] {
  const seen = new Set<string>();
  return blocks.filter((block) => {
    if (!block.id || seen.has(block.id)) return false;
    seen.add(block.id);
    return true;
  });
}

export function expandToFull(item: AnalyticsLayoutItemState): AnalyticsLayoutItemState {
  return { ...item, layout: "full" };
}

export function collapseToHalf(item: AnalyticsLayoutItemState): AnalyticsLayoutItemState {
  return { ...item, layout: "half" };
}

export function packRows(items: AnalyticsLayoutItemState[]): AnalyticsLayoutItemState[][] {
  const rows: AnalyticsLayoutItemState[][] = [];
  for (let index = 0; index < items.length; index += 1) {
    const item = items[index];
    const nextItem = items[index + 1];
    if (item.layout === "half" && nextItem?.layout === "half") {
      rows.push([item, nextItem]);
      index += 1;
    } else {
      rows.push([expandToFull(item)]);
    }
  }
  return rows;
}

function flattenPackedRows(rows: AnalyticsLayoutItemState[][]): AnalyticsLayoutItemState[] {
  return rows.flatMap((row) => {
    if (row.length === 2) {
      return row.map(collapseToHalf);
    }
    return row.map(expandToFull);
  });
}

export function normalize(
  blocks: AnalyticsLayoutBlockSource[],
  storedLayout?: unknown
): AnalyticsLayoutItemState[] {
  const knownBlocks = uniqueKnownBlocks(blocks);
  const blockById = new Map(knownBlocks.map((block) => [block.id, block]));
  const storedItems = Array.isArray(storedLayout)
    ? storedLayout
      .map((item): AnalyticsLayoutItemState | null => {
        if (!item || typeof item !== "object") return null;
        const candidate = item as Partial<AnalyticsLayoutItemState>;
        if (typeof candidate.id !== "string" || !blockById.has(candidate.id)) return null;
        return {
          id: candidate.id,
          layout: isLayoutWidth(candidate.layout) ? candidate.layout : blockById.get(candidate.id)?.defaultLayout ?? "full"
        };
      })
      .filter((item): item is AnalyticsLayoutItemState => Boolean(item))
    : [];
  const storedIds = new Set(storedItems.map((item) => item.id));
  const missingItems = knownBlocks
    .filter((block) => !storedIds.has(block.id))
    .map((block) => ({
      id: block.id,
      layout: block.defaultLayout ?? "full"
    }));
  return flattenPackedRows(packRows([...storedItems, ...missingItems]));
}

export function mergeVisibleLayoutPreservingHidden(
  previousLayout: AnalyticsLayoutItemState[] | null | undefined,
  visibleLayout: AnalyticsLayoutItemState[],
  hiddenIds: Iterable<string>,
  preserveVisibleWidths = false
): AnalyticsLayoutItemState[] {
  const hidden = new Set(hiddenIds);
  if (!hidden.size || !previousLayout?.length) {
    return visibleLayout.map((item) => ({ ...item }));
  }

  const previousById = new Map(previousLayout.map((item) => [item.id, item]));
  const visibleItems = visibleLayout.filter((item) => !hidden.has(item.id));
  const visibleIds = new Set(visibleItems.map((item) => item.id));
  const next: AnalyticsLayoutItemState[] = [];
  let visibleIndex = 0;

  for (const previousItem of previousLayout) {
    if (hidden.has(previousItem.id)) {
      next.push({ ...previousItem });
      continue;
    }
    if (!visibleIds.has(previousItem.id)) continue;
    const visibleItem = visibleItems[visibleIndex];
    if (!visibleItem) continue;
    next.push({
      ...visibleItem,
      layout: preserveVisibleWidths
        ? previousById.get(visibleItem.id)?.layout ?? visibleItem.layout
        : visibleItem.layout
    });
    visibleIndex += 1;
  }

  for (; visibleIndex < visibleItems.length; visibleIndex += 1) {
    const visibleItem = visibleItems[visibleIndex];
    next.push({
      ...visibleItem,
      layout: preserveVisibleWidths
        ? previousById.get(visibleItem.id)?.layout ?? visibleItem.layout
        : visibleItem.layout
    });
  }
  return next;
}

export function moveBlock(
  items: AnalyticsLayoutItemState[],
  draggedId: string,
  targetId: string | null | undefined,
  position: "after" | "before" | "end"
): AnalyticsLayoutItemState[] {
  const dragged = items.find((item) => item.id === draggedId);
  if (!dragged) return items;
  const remaining = items
    .filter((item) => item.id !== draggedId)
    .map((item) => ({ ...item }));
  const nextDragged = expandToFull(dragged);
  if (position === "end" || !targetId) {
    return flattenPackedRows(packRows([...remaining, nextDragged]));
  }
  const targetIndex = remaining.findIndex((item) => item.id === targetId);
  if (targetIndex === -1) return flattenPackedRows(packRows([...remaining, nextDragged]));
  const insertionIndex = position === "after" ? targetIndex + 1 : targetIndex;
  const next = [...remaining];
  next.splice(insertionIndex, 0, nextDragged);
  return flattenPackedRows(packRows(next));
}

export function pairWithTarget(
  items: AnalyticsLayoutItemState[],
  draggedId: string,
  targetId: string,
  side: "after" | "before"
): AnalyticsLayoutItemState[] {
  if (draggedId === targetId) return items;
  const dragged = items.find((item) => item.id === draggedId);
  if (!dragged || !items.some((item) => item.id === targetId)) return items;
  const remaining = items
    .filter((item) => item.id !== draggedId)
    .map((item) => (item.id === targetId ? collapseToHalf(item) : { ...item }));
  const targetIndex = remaining.findIndex((item) => item.id === targetId);
  const nextDragged = collapseToHalf(dragged);
  const insertionIndex = side === "after" ? targetIndex + 1 : targetIndex;
  const next = [...remaining];
  next.splice(insertionIndex, 0, nextDragged);
  return flattenPackedRows(packRows(next));
}

export function predictPlacement(
  items: AnalyticsLayoutItemState[],
  placement: AnalyticsLayoutPlacement
): AnalyticsLayoutItemState[] {
  if (placement.intent === "hold") {
    return items;
  }
  if (placement.intent === "pair-before" && placement.targetId) {
    return pairWithTarget(items, placement.draggedId, placement.targetId, "before");
  }
  if (placement.intent === "pair-after" && placement.targetId) {
    return pairWithTarget(items, placement.draggedId, placement.targetId, "after");
  }
  if (placement.intent === "before") {
    return moveBlock(items, placement.draggedId, placement.targetId, "before");
  }
  if (placement.intent === "after") {
    return moveBlock(items, placement.draggedId, placement.targetId, "after");
  }
  return moveBlock(items, placement.draggedId, null, "end");
}
