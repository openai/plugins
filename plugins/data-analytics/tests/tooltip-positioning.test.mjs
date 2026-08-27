import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { describe, test } from "node:test";
import ts from "typescript";

async function loadTooltipPositioning() {
  const source = await readFile(
    join(process.cwd(), "src", "analytics-app", "charting", "tooltipPositioning.ts"),
    "utf8",
  );
  const { outputText } = ts.transpileModule(source, {
    compilerOptions: {
      module: ts.ModuleKind.ES2022,
      target: ts.ScriptTarget.ES2022,
    },
  });
  const url = `data:text/javascript;base64,${Buffer.from(outputText).toString("base64")}`;
  return import(url);
}

describe("viewport tooltip positioning", () => {
  test("centers a tooltip above its anchor when it fits", async () => {
    const { calculateViewportTooltipPosition } = await loadTooltipPositioning();
    assert.deepEqual(
      calculateViewportTooltipPosition({
        anchorRect: { bottom: 240, left: 300, right: 340, top: 200 },
        tooltipSize: { height: 80, width: 184 },
        viewport: { height: 600, width: 800 },
      }),
      { left: 228, placement: "above", top: 112 },
    );
  });

  test("flips below anchors near the top edge", async () => {
    const { calculateViewportTooltipPosition } = await loadTooltipPositioning();
    assert.deepEqual(
      calculateViewportTooltipPosition({
        anchorRect: { bottom: 52, left: 300, right: 340, top: 20 },
        tooltipSize: { height: 80, width: 184 },
        viewport: { height: 600, width: 800 },
      }),
      { left: 228, placement: "below", top: 60 },
    );
  });

  test("clamps tooltips inside both horizontal viewport edges", async () => {
    const { calculateViewportTooltipPosition } = await loadTooltipPositioning();
    const base = {
      tooltipSize: { height: 80, width: 184 },
      viewport: { height: 600, width: 800 },
    };
    assert.equal(calculateViewportTooltipPosition({
      ...base,
      anchorRect: { bottom: 240, left: 0, right: 40, top: 200 },
    }).left, 12);
    assert.equal(calculateViewportTooltipPosition({
      ...base,
      anchorRect: { bottom: 240, left: 760, right: 800, top: 200 },
    }).left, 604);
  });

  test("clamps vertically when neither side has enough space", async () => {
    const { calculateViewportTooltipPosition } = await loadTooltipPositioning();
    assert.deepEqual(
      calculateViewportTooltipPosition({
        anchorRect: { bottom: 65, left: 70, right: 90, top: 45 },
        tooltipSize: { height: 100, width: 160 },
        viewport: { height: 120, width: 200 },
      }),
      { left: 12, placement: "below", top: 12 },
    );
  });
});
