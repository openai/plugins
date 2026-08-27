import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

test("inline Recharts bridge normalizes word percent units into valueFormat", async () => {
  const source = await readFile(new URL("../src/recharts-renderer.jsx", import.meta.url), "utf8");

  assert.match(source, /const percentWordUnit = isPercentWordUnit\(rawUnit\);/);
  assert.match(source, /const unit = percentWordUnit \? "" : rawUnit;/);
  assert.match(source, /valueFormat: existing\.valueFormat \|\| \(percentWordUnit \? "percent" : unit === "\$" \? "currency" : "compact"\)/);
});

test("inline Recharts bridge clears serialized live markup before remounting", async () => {
  const source = await readFile(new URL("../src/recharts-renderer.jsx", import.meta.url), "utf8");
  const destroyer = source
    .split("export function destroyRechartsChart", 2)[1]
    .split("export function renderRechartsChart", 1)[0];
  const destroyRechartsChart = new Function(
    `return function destroyRechartsChart${destroyer}`,
  )();
  const serializedContainer = {
    childNodes: [{}, {}],
    replaceChildren() {
      this.childNodes = [];
    },
  };

  assert.match(destroyer, /if \(!container\) return;/);
  assert.match(destroyer, /container\.replaceChildren\(\);/);
  assert.match(source, /destroyRechartsChart\(container\);\n  const mount = document\.createElement/);
  destroyRechartsChart(serializedContainer);
  assert.deepEqual(serializedContainer.childNodes, []);
});

test("inline chart widget projection preserves selected measure value formats", async () => {
  const source = await readFile(new URL("../src/datascience-chart-widget.js", import.meta.url), "utf8");

  assert.match(source, /function selectedMeasureColumn\(dataset\)/);
  assert.match(source, /function valueFormatFor\(dataset, existing = chartSpecFor\(dataset\)\)/);
  assert.match(source, /const valueFormat = valueFormatFor\(dataset, existing\);/);
  assert.match(source, /\.\.\.\(valueFormat \? \{ format: valueFormat \} : \{\}\),/);
  assert.match(source, /valueFormat,\nsettings: \{/);
});
