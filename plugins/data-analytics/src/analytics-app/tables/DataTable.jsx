import React from "react";
import { ArrowDown, ArrowUp, ChevronLeft, ChevronRight } from "lucide-react";

const DEFAULT_PAGE_SIZE = 15;
const TABLE_COLUMN_DEFAULT_WIDTH = 160;
const TABLE_COLUMN_KEYBOARD_STEP = 24;
const TABLE_COLUMN_MAX_WIDTH = 720;
const TABLE_COLUMN_MIN_WIDTH = 88;
const TABLE_COLUMN_RANK_MIN_WIDTH = 72;
const TABLE_COLUMN_SAMPLE_SIZE = 25;
const COMPACT_VALUE_THRESHOLD = 100_000;

function text(value) {
  return value == null ? "" : String(value);
}

function numeric(value) {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string") {
    const parsed = Number(value.replace(/[,%]/g, ""));
    return Number.isFinite(parsed) ? parsed : null;
  }
  return null;
}

function dateParts(value) {
  if (typeof value !== "string") return null;
  const match = value.trim().match(/^(\d{4})-(\d{2})-(\d{2})(?:$|[T\s])/);
  if (!match) return null;
  const [, year, month, day] = match;
  return {
    day: Number(day),
    month: Number(month),
    year: Number(year),
  };
}

function isDateLikeValue(value) {
  if (value instanceof Date) return !Number.isNaN(value.getTime());
  const parts = dateParts(value);
  if (!parts) return false;
  const date = new Date(parts.year, parts.month - 1, parts.day);
  return (
    date.getFullYear() === parts.year &&
    date.getMonth() === parts.month - 1 &&
    date.getDate() === parts.day
  );
}

function formatTableDate(value) {
  if (value instanceof Date && !Number.isNaN(value.getTime())) {
    return new Intl.DateTimeFormat(undefined, {
      day: "numeric",
      month: "short",
      year: "numeric",
    }).format(value);
  }
  const parts = dateParts(value);
  if (!parts) return text(value);
  return new Intl.DateTimeFormat(undefined, {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(parts.year, parts.month - 1, parts.day));
}

function titleCaseKey(key) {
  return text(key)
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function isUsdUnit(unit) {
  return unit === "$" || text(unit).toUpperCase() === "USD";
}

function unitScaleSuffix(unit) {
  const normalized = text(unit).toLowerCase();
  if (normalized === "usd millions" || normalized === "usd million") return "M";
  if (normalized === "usd billions" || normalized === "usd billion") return "B";
  if (normalized === "usd thousands" || normalized === "usd thousand") return "K";
  if (/^\$[kmbt]$/i.test(text(unit))) return text(unit).slice(1).toUpperCase();
  return null;
}

function compactDigits(value) {
  const absolute = Math.abs(value);
  if (absolute >= COMPACT_VALUE_THRESHOLD) return 1;
  return 2;
}

function formatNumber(value, { compact = false } = {}) {
  const absolute = Math.abs(value);
  return new Intl.NumberFormat(undefined, {
    maximumFractionDigits: compactDigits(value),
    notation: compact && absolute >= COMPACT_VALUE_THRESHOLD ? "compact" : "standard",
  }).format(value);
}

function formatCurrency(value) {
  const absolute = Math.abs(value);
  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: compactDigits(value),
    notation: absolute >= COMPACT_VALUE_THRESHOLD ? "compact" : "standard",
  }).format(value);
}

function signedLabel(value, label, signed = false) {
  if (signed && value > 0) return `+${label}`;
  return label;
}

function formatScaledCurrency(value, scaleSuffix, signed) {
  const absolute = Math.abs(value);
  const sign = value < 0 ? "-" : signed && value > 0 ? "+" : "";
  return `${sign}$${formatNumber(absolute)}${scaleSuffix}`;
}

export function inferTableColumns(rows) {
  const seen = new Set();
  const columns = [];
  for (const row of Array.isArray(rows) ? rows : []) {
    if (!row || typeof row !== "object") continue;
    for (const key of Object.keys(row)) {
      if (seen.has(key)) continue;
      seen.add(key);
      columns.push({ key, label: titleCaseKey(key) });
    }
  }
  return columns;
}

export function normalizeTableColumns(columns, rows) {
  const normalized = [];
  const seen = new Set();
  for (const column of Array.isArray(columns) ? columns : []) {
    if (!column || typeof column !== "object") continue;
    const key = text(column.key || column.field);
    if (!key || seen.has(key)) continue;
    seen.add(key);
    normalized.push({
      ...column,
      field: column.field || key,
      key,
      label: column.label || column.name || titleCaseKey(key),
    });
  }
  return normalized.length ? normalized : inferTableColumns(rows);
}

export function columnType(column, rows) {
  if (column?.type) return column.type;
  if (column?.format === "currency") return "currency";
  if (column?.format === "percent") return "percent";
  if (column?.format) return "number";
  const key = column?.key || column?.field;
  const values = (Array.isArray(rows) ? rows : [])
    .map((row) => row && row[key])
    .filter((value) => value != null);
  if (values.length && values.every(isDateLikeValue)) return "date";
  if (values.length && values.every((value) => typeof value === "number")) return "number";
  if (values.length && values.every((value) => numeric(value) != null)) return "number";
  return "text";
}

export function formatTableValue(value, type, unit, options = {}) {
  const signed = Boolean(options.signed);
  if (value == null) return "";
  if (type === "date") return formatTableDate(value);
  const numericValue = numeric(value);
  if (type === "percent" && numericValue != null) {
    const label = new Intl.NumberFormat(undefined, {
      style: "percent",
      maximumFractionDigits: Math.abs(numericValue) < 0.1 ? 1 : 0,
    }).format(numericValue);
    return signedLabel(numericValue, label, signed);
  }
  const scaleSuffix = unitScaleSuffix(unit);
  if (scaleSuffix && numericValue != null) {
    return formatScaledCurrency(numericValue, scaleSuffix, signed);
  }
  if (type === "currency" && numericValue != null) {
    return signedLabel(numericValue, formatCurrency(numericValue), signed);
  }
  if (type === "number" && numericValue != null) {
    if (isUsdUnit(unit)) return signedLabel(numericValue, formatCurrency(numericValue), signed);
    const suffix = unit ? ` ${unit}` : "";
    return signedLabel(numericValue, `${formatNumber(numericValue, { compact: true })}${suffix}`, signed);
  }
  return text(value);
}

function isMovementColumn(column) {
  return column?.movement === true || column?.semantic === "movement" || column?.role === "movement";
}

function movementDirection(column, value) {
  if (!isMovementColumn(column)) return null;
  if (typeof value !== "string") {
    const numericValue = numeric(value);
    if (numericValue > 0) return "positive";
    if (numericValue < 0) return "negative";
    return null;
  }
  const trimmed = value.trim();
  if (!trimmed) return null;
  if (/^[+↑]/.test(trimmed)) return "positive";
  if (/^[-−↓]/.test(trimmed)) return "negative";
  const numericValue = numeric(trimmed);
  if (numericValue > 0) return "positive";
  if (numericValue < 0) return "negative";
  return null;
}

function movementClassName(column, value) {
  const direction = movementDirection(column, value);
  if (!direction || direction === "neutral") return "";
  return `table-cell-movement table-cell-movement-${direction}`;
}

function columnLooksLikeRank(column) {
  const descriptor = text(column?.key || column?.field || column?.label || column?.name).trim();
  return /^(#|rank|ranking|position)$/i.test(descriptor);
}

function columnMinWidth(column) {
  if (column?.minWidth != null) {
    const parsed = Number(column.minWidth);
    if (Number.isFinite(parsed)) return clamp(parsed, TABLE_COLUMN_RANK_MIN_WIDTH, TABLE_COLUMN_MAX_WIDTH);
  }
  return columnLooksLikeRank(column) ? TABLE_COLUMN_RANK_MIN_WIDTH : TABLE_COLUMN_MIN_WIDTH;
}

function defaultColumnAlign(column, type) {
  if (column.align) return column.align;
  if (columnLooksLikeRank(column)) return "center";
  if (type === "number" || type === "percent" || type === "currency") return "right";
  return "left";
}

function columnGrowWeight(column, rows) {
  if (columnLooksLikeRank(column)) return 0;
  const type = columnType(column, rows);
  if (type === "text" || type === "date") return 1.4;
  return 1;
}

function sortRows(rows, columns, sortState) {
  if (!sortState?.key) return rows;
  const column = columns.find((item) => item.key === sortState.key) || {};
  const type = columnType(column, rows);
  return [...rows].sort((a, b) => {
    const av = a ? a[sortState.key] : null;
    const bv = b ? b[sortState.key] : null;
    let result = 0;
    if (type === "number" || type === "percent" || type === "currency") {
      const aNumber = numeric(av);
      const bNumber = numeric(bv);
      if (aNumber == null && bNumber == null) result = 0;
      else if (aNumber == null) result = 1;
      else if (bNumber == null) result = -1;
      else result = aNumber - bNumber;
    } else {
      result = text(av).localeCompare(text(bv), undefined, { numeric: true });
    }
    return sortState.direction === "desc" ? -result : result;
  });
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function estimateTableColumnWidths(columns, rows) {
  return Object.fromEntries(
    columns.map((column) => {
      const key = column.key;
      const type = columnType(column, rows);
      const sampleValues = rows
        .slice(0, TABLE_COLUMN_SAMPLE_SIZE)
        .map((row) => formatTableValue(row && row[key], type, column.unit));
      const longest = Math.max(text(column.label).length, ...sampleValues.map((value) => text(value).length));
      const width = clamp(Math.ceil(longest * 7.5) + 42, columnMinWidth(column), TABLE_COLUMN_MAX_WIDTH);
      return [key, width];
    }),
  );
}

function stretchTableColumnWidths(columns, rows, baseWidths, targetWidth) {
  const baseWidth = columns.reduce(
    (total, column) => total + (baseWidths[column.key] ?? TABLE_COLUMN_DEFAULT_WIDTH),
    0,
  );
  const availableWidth = Number.isFinite(targetWidth) ? Math.floor(targetWidth) : 0;
  if (availableWidth <= baseWidth) return baseWidths;

  const weights = columns.map((column) => columnGrowWeight(column, rows));
  const totalWeight = weights.reduce((total, weight) => total + weight, 0);
  if (!totalWeight) return baseWidths;

  const extraWidth = availableWidth - baseWidth;
  return Object.fromEntries(
    columns.map((column, index) => [
      column.key,
      (baseWidths[column.key] ?? TABLE_COLUMN_DEFAULT_WIDTH) + (extraWidth * weights[index]) / totalWeight,
    ]),
  );
}

function SortIcon({ direction }) {
  const Icon = direction === "desc" ? ArrowDown : ArrowUp;
  return <Icon aria-hidden="true" className="table-sort-icon" size={12} strokeWidth={2} />;
}

function markdownCell(value) {
  return text(value)
    .replace(/\r?\n/g, "<br>")
    .replace(/\|/g, "\\|")
    .trim();
}

export function tableRowsToMarkdown({ columns, maxRows = 2000, rows }) {
  const safeRows = Array.isArray(rows) ? rows : [];
  const normalizedColumns = normalizeTableColumns(columns, safeRows);
  if (!normalizedColumns.length) return "";
  const header = `| ${normalizedColumns.map((column) => markdownCell(column.label)).join(" | ")} |`;
  const divider = `| ${normalizedColumns.map(() => "---").join(" | ")} |`;
  const body = safeRows.slice(0, maxRows).map((row) => {
    const cells = normalizedColumns.map((column) => {
      const type = columnType(column, safeRows);
      return markdownCell(
        formatTableValue(row && row[column.key], type, column.unit, {
          signed: isMovementColumn(column),
        }),
      );
    });
    return `| ${cells.join(" | ")} |`;
  });
  return [header, divider, ...body].join("\n");
}

export function DataTable({
  columnWidths,
  columns,
  density = "dense",
  emptyLabel = "No rows to render.",
  isFullscreen = false,
  maxRows = 2000,
  onColumnWidthsChange,
  pageSize = DEFAULT_PAGE_SIZE,
  rows,
  showCount = true,
}) {
  const safeRows = Array.isArray(rows) ? rows : [];
  const normalizedColumns = React.useMemo(
    () => normalizeTableColumns(columns, safeRows),
    [columns, safeRows],
  );
  const [sortState, setSortState] = React.useState(null);
  const [page, setPage] = React.useState(0);
  const [internalColumnWidths, setInternalColumnWidths] = React.useState({});
  const [tableWrapWidth, setTableWrapWidth] = React.useState(0);
  const [isColumnResizing, setIsColumnResizing] = React.useState(false);
  const tableWrapRef = React.useRef(null);
  const effectiveColumnWidths = columnWidths || internalColumnWidths;

  React.useEffect(() => {
    setPage(0);
    if (!columnWidths) setInternalColumnWidths({});
  }, [rows, columns]);

  React.useLayoutEffect(() => {
    if (tableWrapRef.current) tableWrapRef.current.scrollLeft = 0;
  }, [rows, columns]);

  React.useLayoutEffect(() => {
    const node = tableWrapRef.current;
    if (!node) return undefined;

    const measure = () => {
      const nextWidth = Math.floor(node.getBoundingClientRect().width || 0);
      setTableWrapWidth((current) => (current === nextWidth ? current : nextWidth));
    };

    measure();
    const observer = typeof ResizeObserver === "function" ? new ResizeObserver(measure) : null;
    observer?.observe(node);
    window.addEventListener("resize", measure);
    return () => {
      observer?.disconnect();
      window.removeEventListener("resize", measure);
    };
  }, []);

  const sortedRows = React.useMemo(
    () => sortRows(safeRows, normalizedColumns, sortState).slice(0, maxRows),
    [maxRows, normalizedColumns, safeRows, sortState],
  );
  const effectivePageSize = isFullscreen ? Math.max(1, sortedRows.length) : pageSize;
  const totalPages = Math.max(1, Math.ceil(sortedRows.length / effectivePageSize));
  const currentPage = Math.min(page, totalPages - 1);
  const visibleRows = sortedRows.slice(
    currentPage * effectivePageSize,
    currentPage * effectivePageSize + effectivePageSize,
  );
  const isTruncated = safeRows.length > sortedRows.length;
  const shouldShowPagination = safeRows.length > 0 && !isFullscreen && totalPages > 1;
  const shouldShowCount = showCount && (shouldShowPagination || isTruncated);
  const resultCountLabel = safeRows.length > sortedRows.length
    ? `${sortedRows.length.toLocaleString()} of ${safeRows.length.toLocaleString()} results`
    : `${safeRows.length.toLocaleString()} ${safeRows.length === 1 ? "result" : "results"}`;
  const activeColumnWidths = React.useMemo(() => {
    const estimatedWidths = estimateTableColumnWidths(normalizedColumns, safeRows);
    return Object.fromEntries(
      normalizedColumns.map((column) => {
        const key = column.key;
        return [
          key,
          clamp(
            Math.round(effectiveColumnWidths[key] ?? estimatedWidths[key] ?? TABLE_COLUMN_DEFAULT_WIDTH),
            columnMinWidth(column),
            TABLE_COLUMN_MAX_WIDTH,
          ),
        ];
      }),
    );
  }, [effectiveColumnWidths, normalizedColumns, safeRows]);
  const renderedColumnWidths = React.useMemo(
    () => stretchTableColumnWidths(normalizedColumns, safeRows, activeColumnWidths, tableWrapWidth),
    [activeColumnWidths, normalizedColumns, safeRows, tableWrapWidth],
  );
  const tablePixelWidth = normalizedColumns.reduce(
    (total, column) => total + (activeColumnWidths[column.key] ?? TABLE_COLUMN_DEFAULT_WIDTH),
    0,
  );
  const renderedTableWidth = normalizedColumns.reduce(
    (total, column) => total + (renderedColumnWidths[column.key] ?? activeColumnWidths[column.key] ?? TABLE_COLUMN_DEFAULT_WIDTH),
    0,
  );

  function toggleSort(key) {
    setSortState((current) => {
      if (current?.key === key) {
        return { key, direction: current.direction === "asc" ? "desc" : "asc" };
      }
      return { key, direction: "asc" };
    });
    setPage(0);
  }

  function resizeColumnBy(key, delta) {
    const currentWidth = renderedColumnWidths[key] ?? activeColumnWidths[key] ?? TABLE_COLUMN_DEFAULT_WIDTH;
    const column = normalizedColumns.find((item) => item.key === key);
    commitColumnWidths({
      ...activeColumnWidths,
      ...effectiveColumnWidths,
      [key]: clamp(Math.round(currentWidth + delta), columnMinWidth(column), TABLE_COLUMN_MAX_WIDTH),
    }, { persist: true });
  }

  function startColumnResize(event, key) {
    event.preventDefault();
    event.stopPropagation();
    const baseWidths = { ...activeColumnWidths, ...renderedColumnWidths, ...effectiveColumnWidths };
    const startWidth = baseWidths[key] ?? TABLE_COLUMN_DEFAULT_WIDTH;
    const startX = event.clientX;
    const column = normalizedColumns.find((item) => item.key === key);
    let latestWidths = baseWidths;
    commitColumnWidths(baseWidths, { persist: false });
    setIsColumnResizing(true);
    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";

    function handlePointerMove(moveEvent) {
      latestWidths = {
        ...baseWidths,
        [key]: clamp(
          Math.round(startWidth + moveEvent.clientX - startX),
          columnMinWidth(column),
          TABLE_COLUMN_MAX_WIDTH,
        ),
      };
      commitColumnWidths(latestWidths, { persist: false });
    }

    function finishResize() {
      window.removeEventListener("pointermove", handlePointerMove);
      window.removeEventListener("pointerup", finishResize);
      window.removeEventListener("pointercancel", finishResize);
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
      setIsColumnResizing(false);
      commitColumnWidths(latestWidths, { persist: true });
    }

    window.addEventListener("pointermove", handlePointerMove);
    window.addEventListener("pointerup", finishResize);
    window.addEventListener("pointercancel", finishResize);
  }

  function commitColumnWidths(nextWidths, options) {
    if (onColumnWidthsChange) {
      onColumnWidthsChange(nextWidths, options);
      return;
    }
    setInternalColumnWidths(nextWidths);
  }

  if (!safeRows.length || !normalizedColumns.length) {
    return <div className="empty-state">{emptyLabel}</div>;
  }

  return (
    <div className="shared-table-shell">
      <div className={`table-wrap table-density-${density} ${isFullscreen ? "fullscreen" : ""}`.trim()} ref={tableWrapRef}>
        <table
          className={`data-table data-table-${density} data-table-resizable ${isColumnResizing ? "is-column-resizing" : ""}`}
          style={{
            minWidth: `${tablePixelWidth}px`,
            tableLayout: "fixed",
            width: `${renderedTableWidth}px`,
          }}
        >
          <colgroup>
            {normalizedColumns.map((column) => (
              <col key={column.key} style={{ width: `${renderedColumnWidths[column.key] ?? activeColumnWidths[column.key] ?? TABLE_COLUMN_DEFAULT_WIDTH}px` }} />
            ))}
          </colgroup>
          <thead>
            <tr>
              {normalizedColumns.map((column) => {
                const key = column.key;
                const active = sortState?.key === key;
                const type = columnType(column, safeRows);
                const align = defaultColumnAlign(column, type);
                return (
                  <th
                    aria-sort={active ? (sortState.direction === "asc" ? "ascending" : "descending") : "none"}
                    className={`${align === "right" ? "numeric" : align === "center" ? "center" : "left"} ${active ? "is-sorted" : ""}`}
                    key={key}
                    style={{ width: `${renderedColumnWidths[key] ?? activeColumnWidths[key] ?? TABLE_COLUMN_DEFAULT_WIDTH}px` }}
                  >
                    <button
                      aria-label={
                        active
                          ? `Sort ${column.label} ${sortState.direction === "asc" ? "descending" : "ascending"}`
                          : `Sort ${column.label} ascending`
                      }
                      className="table-sort-button"
                      onClick={() => toggleSort(key)}
                      type="button"
                    >
                      <span>{column.label}</span>
                      {active ? <SortIcon direction={sortState.direction} /> : null}
                    </button>
                    <button
                      aria-label={`Resize ${column.label} column`}
                      className="table-column-resize-handle"
                      onKeyDown={(event) => {
                        if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
                        event.preventDefault();
                        event.stopPropagation();
                        resizeColumnBy(key, event.key === "ArrowRight" ? TABLE_COLUMN_KEYBOARD_STEP : -TABLE_COLUMN_KEYBOARD_STEP);
                      }}
                      onPointerDown={(event) => startColumnResize(event, key)}
                      title={`Resize ${column.label} column`}
                      type="button"
                    />
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody>
            {visibleRows.map((row, rowIndex) => (
              <tr key={rowIndex}>
                {normalizedColumns.map((column) => {
                  const type = columnType(column, safeRows);
                  const align = defaultColumnAlign(column, type);
                  const value = row ? row[column.key] : null;
                  const className = [
                    align === "right" ? "table-cell-number" : "",
                    align === "center" ? "center" : "",
                    type === "date" ? "table-cell-date" : "",
                    movementClassName(column, value),
                  ].filter(Boolean).join(" ") || undefined;
                  return (
                    <td
                      className={className}
                      key={column.key}
                    >
                      {formatTableValue(value, type, column.unit, {
                        signed: isMovementColumn(column),
                      })}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {shouldShowCount || shouldShowPagination ? (
        <div className="shared-table-footer table-pagination">
          {shouldShowCount ? (
            <span className="table-result-count">{resultCountLabel}</span>
          ) : null}
          {shouldShowPagination ? (
            <div className="table-page-control">
              <span>Page {currentPage + 1} of {totalPages}</span>
              <div className="table-page-buttons">
                <button
                  aria-label="Previous page"
                  className="table-arrow-button"
                  disabled={currentPage === 0}
                  onClick={() => setPage(Math.max(0, currentPage - 1))}
                  type="button"
                >
                  <ChevronLeft aria-hidden="true" size={14} strokeWidth={2} />
                </button>
                <button
                  aria-label="Next page"
                  className="table-arrow-button"
                  disabled={currentPage >= totalPages - 1}
                  onClick={() => setPage(Math.min(totalPages - 1, currentPage + 1))}
                  type="button"
                >
                  <ChevronRight aria-hidden="true" size={14} strokeWidth={2} />
                </button>
              </div>
            </div>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
