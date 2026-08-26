import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { describe, test } from "node:test";
import ts from "typescript";

async function loadTableSizing() {
  const source = await readFile(join(process.cwd(), "src", "analytics-app", "tables", "tableSizing.ts"), "utf8");
  const { outputText } = ts.transpileModule(source, {
    compilerOptions: {
      module: ts.ModuleKind.ES2022,
      target: ts.ScriptTarget.ES2022,
    },
  });
  const url = `data:text/javascript;base64,${Buffer.from(outputText).toString("base64")}`;
  return import(url);
}

describe("artifact table sizing", () => {
  test("reports horizontal scroll affordances only where more content exists", async () => {
    const { calculateHorizontalScrollEdges } = await loadTableSizing();

    assert.deepEqual(
      calculateHorizontalScrollEdges({ clientWidth: 768, scrollLeft: 0, scrollWidth: 768 }),
      { canScrollLeft: false, canScrollRight: false, hasOverflow: false },
    );
    assert.deepEqual(
      calculateHorizontalScrollEdges({ clientWidth: 320, scrollLeft: 0, scrollWidth: 960 }),
      { canScrollLeft: false, canScrollRight: true, hasOverflow: true },
    );
    assert.deepEqual(
      calculateHorizontalScrollEdges({ clientWidth: 320, scrollLeft: 240, scrollWidth: 960 }),
      { canScrollLeft: true, canScrollRight: true, hasOverflow: true },
    );
    assert.deepEqual(
      calculateHorizontalScrollEdges({ clientWidth: 320, scrollLeft: 639.4, scrollWidth: 960 }),
      { canScrollLeft: true, canScrollRight: false, hasOverflow: true },
    );
  });

  test("distributes spare viewport width without introducing horizontal overflow", async () => {
    const { calculateTableSizing } = await loadTableSizing();
    const columns = ["week", "revenue", "attainment", "refund_rate"].map((field) => ({ field }));
    const result = calculateTableSizing(
      columns,
      { attainment: 96, refund_rate: 96, revenue: 112, week: 125 },
      768,
      true,
    );

    assert.equal(result.minimumTableWidth, 768);
    assert.equal(result.tableWidth, 768);
    assert.equal(Object.values(result.columnWidths).reduce((sum, width) => sum + width, 0), 768);
  });

  test("preserves a wide table width so its container can scroll", async () => {
    const { calculateTableSizing } = await loadTableSizing();
    const columns = Array.from({ length: 12 }, (_, index) => ({ field: `column_${index}` }));
    const widths = Object.fromEntries(columns.map((column) => [column.field, 144]));
    const result = calculateTableSizing(columns, widths, 768, true);

    assert.equal(result.minimumTableWidth, 1728);
    assert.equal(result.tableWidth, 1728);
  });

  test("keeps content-sized columns fixed while flexible columns absorb spare width", async () => {
    const { calculateTableSizing } = await loadTableSizing();
    const columns = [
      { field: "metric", sizing: "content" },
      { field: "definition" },
    ];
    const result = calculateTableSizing(columns, { definition: 100, metric: 120 }, 300, true);

    assert.deepEqual(result.columnWidths, { definition: 180, metric: 120 });
    assert.equal(result.tableWidth, 300);
  });
});
