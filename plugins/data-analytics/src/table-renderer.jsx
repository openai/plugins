import React from "react";
import { createRoot } from "react-dom/client";

import { DataTable } from "./analytics-app/tables/DataTable.jsx";
import "./analytics-app/tables/data-table.css";

export function destroyDataTable(container) {
  if (!container || !container.__datascienceDataTableRoot) return;
  container.__datascienceDataTableRoot.unmount();
  container.__datascienceDataTableRoot = null;
}

export function renderDataTable(container, options = {}) {
  if (!container) return;
  destroyDataTable(container);
  const root = createRoot(container);
  container.__datascienceDataTableRoot = root;
  root.render(
    <DataTable
      columns={options.columns}
      emptyLabel={options.emptyLabel}
      maxRows={options.maxRows}
      pageSize={options.pageSize}
      rows={options.rows}
      showCount={options.showCount}
    />,
  );
}
