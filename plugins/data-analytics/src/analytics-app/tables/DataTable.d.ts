import type { ReactElement } from "react";

export type SharedTableColumn = {
  align?: "center" | "left" | "right";
  field?: string;
  format?: "compact" | "currency" | "number" | "percent" | string;
  key?: string;
  label?: string;
  minWidth?: number;
  movement?: boolean;
  name?: string;
  role?: "movement" | "value" | string;
  semantic?: "movement" | "value" | string;
  type?: "currency" | "date" | "number" | "percent" | "text" | string;
  unit?: string;
};

export type SharedDataTableColumnWidthOptions = {
  persist?: boolean;
};

export type SharedDataTableProps = {
  columnWidths?: Record<string, number>;
  columns?: SharedTableColumn[];
  density?: "dense" | "spacious";
  emptyLabel?: string;
  isFullscreen?: boolean;
  maxRows?: number;
  onColumnWidthsChange?: (
    nextWidths: Record<string, number>,
    options?: SharedDataTableColumnWidthOptions
  ) => void;
  pageSize?: number;
  rows?: Array<Record<string, unknown>>;
  showCount?: boolean;
};

export function DataTable(props: SharedDataTableProps): ReactElement;

export function tableRowsToMarkdown(args: {
  columns?: SharedTableColumn[];
  maxRows?: number;
  rows?: Array<Record<string, unknown>>;
}): string;
