import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { describe, test } from "node:test";
import ts from "typescript";

async function loadCore() {
  const source = await readFile(new URL("./layout/analyticsLayoutCore.ts", import.meta.url), "utf8");
  const { outputText } = ts.transpileModule(source, {
    compilerOptions: {
      module: ts.ModuleKind.ES2022,
      target: ts.ScriptTarget.ES2022
    }
  });
  const url = `data:text/javascript;base64,${Buffer.from(outputText).toString("base64")}`;
  return import(url);
}

describe("analytics layout core", () => {
  test("normalizes stored order, removes unknown blocks, appends missing blocks, and expands orphan halves", async () => {
    const { normalize } = await loadCore();
    assert.deepEqual(
      normalize(
        [{ id: "chart-a" }, { id: "table-a" }, { id: "text-a" }],
        [
          { id: "table-a", layout: "half" },
          { id: "ghost", layout: "full" },
          { id: "chart-a", layout: "half" }
        ]
      ),
      [
        { id: "table-a", layout: "half" },
        { id: "chart-a", layout: "half" },
        { id: "text-a", layout: "full" }
      ]
    );
  });

  test("pairs a dragged block with a full-width target", async () => {
    const { pairWithTarget } = await loadCore();
    assert.deepEqual(
      pairWithTarget(
        [
          { id: "a", layout: "full" },
          { id: "b", layout: "full" },
          { id: "c", layout: "full" }
        ],
        "c",
        "a",
        "after"
      ),
      [
        { id: "a", layout: "half" },
        { id: "c", layout: "half" },
        { id: "b", layout: "full" }
      ]
    );
  });

  test("preserves a hidden block's original order and width when it returns", async () => {
    const { mergeVisibleLayoutPreservingHidden } = await loadCore();
    assert.deepEqual(
      mergeVisibleLayoutPreservingHidden(
        [
          { id: "metric-a", layout: "half" },
          { id: "metric-b", layout: "half" },
          { id: "chart-a", layout: "full" }
        ],
        [
          { id: "chart-a", layout: "full" },
          { id: "metric-a", layout: "full" }
        ],
        ["metric-b"],
        true
      ),
      [
        { id: "chart-a", layout: "full" },
        { id: "metric-b", layout: "half" },
        { id: "metric-a", layout: "half" }
      ]
    );
    assert.deepEqual(
      mergeVisibleLayoutPreservingHidden(
        [
          { id: "metric-a", layout: "half" },
          { id: "metric-b", layout: "half" }
        ],
        [{ id: "metric-a", layout: "full" }],
        ["metric-b"]
      ),
      [
        { id: "metric-a", layout: "full" },
        { id: "metric-b", layout: "half" }
      ]
    );
  });

  test("moving a half block above another block expands it and unpairs its previous row", async () => {
    const { moveBlock } = await loadCore();
    assert.deepEqual(
      moveBlock(
        [
          { id: "a", layout: "half" },
          { id: "b", layout: "half" },
          { id: "c", layout: "full" }
        ],
        "a",
        "c",
        "before"
      ),
      [
        { id: "b", layout: "full" },
        { id: "a", layout: "full" },
        { id: "c", layout: "full" }
      ]
    );
  });

  test("predicts center-zone reorder without half-width promotion", async () => {
    const { predictPlacement } = await loadCore();
    assert.deepEqual(
      predictPlacement(
        [
          { id: "a", layout: "full" },
          { id: "b", layout: "full" },
          { id: "c", layout: "full" }
        ],
        { draggedId: "c", intent: "before", targetId: "b" }
      ),
      [
        { id: "a", layout: "full" },
        { id: "c", layout: "full" },
        { id: "b", layout: "full" }
      ]
    );
  });

  test("holding in a split-intent zone keeps the current preview stable", async () => {
    const { predictPlacement } = await loadCore();
    const items = [
      { id: "a", layout: "full" },
      { id: "b", layout: "full" },
      { id: "c", layout: "full" }
    ];
    assert.deepEqual(
      predictPlacement(items, { draggedId: "c", intent: "hold", targetId: "a" }),
      items
    );
  });

  test("dragging to the end keeps mixed chart/table/text blocks packed", async () => {
    const { moveBlock, packRows } = await loadCore();
    const next = moveBlock(
      [
        { id: "chart-a", layout: "half" },
        { id: "table-a", layout: "half" },
        { id: "text-a", layout: "full" }
      ],
      "chart-a",
      null,
      "end"
    );
    assert.deepEqual(next, [
      { id: "table-a", layout: "full" },
      { id: "text-a", layout: "full" },
      { id: "chart-a", layout: "full" }
    ]);
    assert.deepEqual(packRows(next), [
      [{ id: "table-a", layout: "full" }],
      [{ id: "text-a", layout: "full" }],
      [{ id: "chart-a", layout: "full" }]
    ]);
  });
});
