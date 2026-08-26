import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";

function read(path) {
  return readFileSync(new URL(path, import.meta.url), "utf8");
}

test("portable HTML reports preserve canonical provenance and accessible source details", () => {
  const reportSkill = read("../skills/build-report/SKILL.md");

  assert.match(reportSkill, /Give every source-backed card, chart, and table canonical inline `source` metadata or a `sourceId`/);
  assert.match(reportSkill, /exact source identity and, for structured data, the fully qualified table or view/);
  assert.match(reportSkill, /list every material source for joined or multi-input evidence/);
  assert.match(reportSkill, /Never invent provenance/);
  assert.match(reportSkill, /markdown block may declare block-wide provenance with `sourceId` only when every quantitative claim/);
  assert.match(reportSkill, /Split mixed-provenance claims into separate markdown blocks/);
  assert.match(reportSkill, /omit `sourceId` on title-only or prose-only blocks/);
  assert.match(reportSkill, /structured query, file, or document and does not require SQL/);
  assert.match(reportSkill, /never guess a source/);
  assert.match(reportSkill, /accessible source affordances, source tooltips\/detail views, shared styling, and the semantic source inventory as builder outputs/);
  assert.match(reportSkill, /preserves safe canonical provenance exactly/);
  assert.match(reportSkill, /does not strip, normalize, or rewrite source fields/);
  assert.match(reportSkill, /npm run report:deliver -- --input artifact\.json --output report\.html/);
  assert.match(reportSkill, /confirms that the HTML embeds the exact canonical artifact/);
  assert.match(reportSkill, /reuses an installed Chromium.+never downloading a browser/);
  assert.match(reportSkill, /Do not write a bespoke Playwright script, take routine screenshots, or repeat browser inspection when it passes/);
  assert.match(reportSkill, /the actual interactive `report\.html` file is the primary deliverable/);
  assert.match(reportSkill, /never use `image\.png`, a screenshot, or another flattened image as the only report handoff/);
  assert.match(reportSkill, /Browsers that cannot start the enhanced reader retain the semantic fallback/);
  assert.match(reportSkill, /deeper compatibility checks belong to the shared reader's CI/);
});

test("the shared portable packaging contract owns source UI and semantic provenance", () => {
  const core = read("../src/analytics-app-core.md");
  const dashboard = read("../skills/build-dashboard/specifications/html-dashboard.md");
  const mcpReport = read("../skills/build-report/specifications/mcp-app-report.md");

  assert.match(core, /Give every source-backed card, chart, and table an inline `source` or a `sourceId`/);
  assert.match(core, /source affordances, tooltips, detail views, and semantic source inventory derive from this metadata/);
  assert.match(core, /Packaging preserves safe canonical source objects exactly rather than sanitizing them/);
  assert.match(core, /they are never silently removed or rewritten/);
  assert.match(core, /success receipt with `stages\.verification: "passed"` as sufficient per-report QA/);
  assert.match(core, /`stages\.verification: "structural_only"`/);
  assert.match(core, /chart SVG extraction and per-artifact browser QA did not run/);
  assert.match(core, /Multi-engine, keyboard, touch, print, semantic-fallback, conversion, and pixel-parity certification belongs to shared reader CI/);
  assert.match(dashboard, /Treat accessible source affordances, tooltips\/detail views, and the semantic source inventory as builder outputs/);
  for (const guidance of [core, dashboard, mcpReport]) {
    assert.match(guidance, /markdown block/i);
    assert.match(guidance, /sourceId/);
    assert.match(guidance, /all quantitative claims|every quantitative claim/);
    assert.match(guidance, /Split mixed-provenance claims into separate (markdown )?blocks/);
    assert.match(guidance, /title-only or prose-only blocks/);
    assert.match(guidance, /never guess/i);
    assert.match(guidance, /file, or a document|file or document|File and document sources/);
    assert.match(guidance, /do(?:es)? not (need|require) (?:`source\.query\.sql`|SQL)/);
  }
  assert.match(core + dashboard, /canonical source|canonical sources/);
});
