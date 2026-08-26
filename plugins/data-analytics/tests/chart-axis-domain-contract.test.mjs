import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";

function read(path) {
  return readFileSync(new URL(path, import.meta.url), "utf8");
}

test("visualization guidance allows focused domains for compressed delta charts", () => {
  const visualize = read("../skills/visualize-data/SKILL.md");
  const validate = read("../skills/validate-data/SKILL.md");

  for (const source of [visualize, validate]) {
    assert.match(source, /waterfall, bridge, variance, and other delta-focused charts/);
    assert.match(source, /zero would materially compress/);
    assert.match(source, /exact (?:start\/end\/change labels|value labels|values)/);
  }

  assert.match(visualize, /Standard bar charts that compare absolute magnitude should start at zero/);
  assert.match(visualize, /Keep zero in view when values cross zero or the question is absolute magnitude/);
  assert.match(validate, /Bar charts should generally start at zero/);
});

test("waterfall Recharts transform sets a focused y-axis when the zero baseline hides the bridge", () => {
  const transforms = read("../src/analytics-app/charting/chart-transforms.ts");

  assert.match(transforms, /const WATERFALL_NARROW_AXIS_RATIO = 4;/);
  assert.match(transforms, /fullSpan \/ focusedSpan < WATERFALL_NARROW_AXIS_RATIO/);
  assert.match(transforms, /domain: \[axisMin, axisMax\]/);
});
