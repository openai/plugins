export type TableSizingColumn = {
  field: string;
  sizing?: string;
};

export type HorizontalScrollMetrics = {
  clientWidth: number;
  scrollLeft: number;
  scrollWidth: number;
};

const HORIZONTAL_SCROLL_EDGE_TOLERANCE_PX = 1;

export function calculateHorizontalScrollEdges({
  clientWidth,
  scrollLeft,
  scrollWidth,
}: HorizontalScrollMetrics) {
  const maximumScrollLeft = Math.max(0, scrollWidth - clientWidth);
  const hasOverflow = maximumScrollLeft > HORIZONTAL_SCROLL_EDGE_TOLERANCE_PX;
  const normalizedScrollLeft = Math.min(maximumScrollLeft, Math.max(0, scrollLeft));

  return {
    canScrollLeft: hasOverflow && normalizedScrollLeft > HORIZONTAL_SCROLL_EDGE_TOLERANCE_PX,
    canScrollRight:
      hasOverflow && normalizedScrollLeft < maximumScrollLeft - HORIZONTAL_SCROLL_EDGE_TOLERANCE_PX,
    hasOverflow,
  };
}

export function calculateTableSizing(
  columns: TableSizingColumn[],
  activeColumnWidths: Record<string, number>,
  viewportWidth: number,
  fillAvailableWidth: boolean,
) {
  const flexibleColumns = columns.filter((column) => column.sizing !== "content");
  const flexibleColumnIndexes = new Map(flexibleColumns.map((column, index) => [column.field, index]));
  const baseTableWidth = columns.reduce((total, column) => total + (activeColumnWidths[column.field] ?? 0), 0);
  const normalizedViewportWidth = Math.max(0, Math.round(viewportWidth));
  const fillExtraWidth = fillAvailableWidth
    ? Math.max(0, normalizedViewportWidth - baseTableWidth)
    : 0;
  const extraWidthPerFlexibleColumn = flexibleColumns.length
    ? Math.floor(fillExtraWidth / flexibleColumns.length)
    : 0;
  const extraWidthRemainder = flexibleColumns.length ? fillExtraWidth % flexibleColumns.length : 0;
  const columnWidths = Object.fromEntries(columns.map((column) => {
    const flexibleIndex = flexibleColumnIndexes.get(column.field);
    const extraWidth = flexibleIndex == null
      ? 0
      : extraWidthPerFlexibleColumn + (flexibleIndex < extraWidthRemainder ? 1 : 0);
    return [column.field, (activeColumnWidths[column.field] ?? 0) + extraWidth];
  }));
  const minimumTableWidth = columns.reduce((total, column) => total + (columnWidths[column.field] ?? 0), 0);
  const tableWidth = fillAvailableWidth
    ? Math.max(normalizedViewportWidth, minimumTableWidth)
    : minimumTableWidth;

  return { columnWidths, minimumTableWidth, tableWidth };
}
