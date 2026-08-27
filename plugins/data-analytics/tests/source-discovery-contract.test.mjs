import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";

const skillNames = [
  "index",
  "build-dashboard",
  "design-kpis",
  "kpi-reporting",
  "market-sizing",
  "metric-diagnostics",
  "product-business-analysis",
];

function readSkill(name) {
  return readFileSync(new URL(`../skills/${name}/SKILL.md`, import.meta.url), "utf8");
}

function sourceDiscoverySection(source) {
  const startHeading = "### Source Discovery And Verification";
  const endHeading = "### Source Access Guardrail";
  const start = source.indexOf(startHeading);
  assert.notEqual(start, -1, `missing section start: ${startHeading}`);
  const end = source.indexOf(endHeading, start + startHeading.length);
  assert.notEqual(end, -1, `missing section end: ${endHeading}`);
  return source.slice(start, end);
}

test("analytical preflight exhausts plausible cross-source discovery", () => {
  for (const name of skillNames) {
    const preflight = sourceDiscoverySection(readSkill(name));

    assert.match(preflight, /1\. \*\*Explore all possible sources\.\*\*/, name);
    assert.match(preflight, /Search every connected or provided source that could contain task-relevant data or change the interpretation/, name);
    assert.match(preflight, /run fresh catalog or metadata discovery/, name);
    assert.match(preflight, /starting points, not stopping points/, name);
    assert.match(preflight, /2\. \*\*Compare duplicates and conflicts\.\*\*/, name);
    assert.match(preflight, /compare ownership, freshness, definition, grain, coverage, and directness/, name);
    assert.match(preflight, /Use the best authoritative source, or combine complementary sources when needed/, name);
    assert.match(preflight, /explain why the selected source or sources control the answer/, name);
    assert.ok(preflight.trim().split(/\s+/).length <= 130, `${name} source preflight is too long`);
  }
});

test("business-context retrieval cannot short-circuit comprehensive discovery", () => {
  const context = readSkill("gather-business-context");

  assert.match(context, /1\. \*\*Explore all possible sources\.\*\*/);
  assert.match(context, /Search every enabled or provided source family that could contain useful context or task-relevant data/);
  assert.match(context, /run fresh catalog or metadata discovery/);
  assert.match(context, /starting points, not stopping points/);
  assert.match(context, /2\. \*\*Compare duplicates and conflicts\.\*\*/);
  assert.match(context, /compare authority, freshness, definition, scope, and directness/);
  assert.match(context, /explain which source or combination should guide downstream analysis/);
});
