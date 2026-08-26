import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import {
  mkdtempSync,
  readFileSync,
  readdirSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { test } from "node:test";
import { gunzipSync } from "node:zlib";

import {
  FALLBACK_ROOT_ID,
  PAYLOAD_SOURCE_ID,
  READER_ASSET,
  READER_ROOT_ID,
  READER_READY_EVENT,
  RUNTIME_SOURCE_ID,
  assertPortableReaderRuntime,
  buildPortableArtifact,
  encodeCompressedText,
  preparePortablePayload,
  readPackagedReaderRuntime,
  semanticFallback,
} from "../skills/build-report/scripts/build_portable_artifact.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const pluginRoot = resolve(here, "..");
const builderPath = resolve(
  pluginRoot,
  "skills/build-report/scripts/build_portable_artifact.mjs",
);
const assetDirectory = resolve(pluginRoot, "assets");

const fakeRuntime = `<!doctype html>
<html>
<head><style>#root{min-height:20px}</style></head>
<body><div id="root"></div><script type="module">
const payload = window.__DATA_ANALYTICS_PORTABLE_ARTIFACT__;
document.getElementById("root").textContent = payload.manifest.title;
document.dispatchEvent(new CustomEvent("${READER_READY_EVENT}"));
</script></body>
</html>`;

function staticSvg(theme, color) {
  return [
    `<svg aria-hidden="true" class="portable-static-chart-svg" focusable="false" height="320" preserveAspectRatio="xMidYMid meet" viewBox="0 0 640 320" width="640" xmlns="http://www.w3.org/2000/svg">`,
    `<defs><clipPath id="portable-chart-${theme}-clip"><rect height="280" width="600" x="20" y="20"></rect></clipPath></defs>`,
    `<g clip-path="url(#portable-chart-${theme}-clip)"><rect fill="${color}" height="180" width="120" x="80" y="100"></rect><text fill="rgb(31, 31, 31)" font-size="12px" text-anchor="middle" x="140" y="298">Alpha</text></g>`,
    "</svg>",
  ].join("");
}

const staticCharts = {
  chart: {
    dark: {
      legend: {
        items: [{ color: "rgb(102, 168, 255)", label: "Revenue", marker: "dot" }],
        position: "bottom",
        title: null,
      },
      svg: staticSvg("dark", "rgb(102, 168, 255)"),
    },
    height: 320,
    light: {
      legend: {
        items: [{ color: "rgb(20, 115, 230)", label: "Revenue", marker: "dot" }],
        position: "bottom",
        title: null,
      },
      svg: staticSvg("light", "rgb(20, 115, 230)"),
    },
    width: 640,
  },
};

function artifactInput(surface = "report") {
  return {
    surface,
    manifest: {
      version: 1,
      surface,
      title: "Revenue momentum",
      description: "A decision-ready revenue report.",
      generatedAt: "2026-07-07T12:00:00Z",
      filters: [
        {
          id: "segment_filter",
          label: "Segment",
          dataset: "weekly_revenue",
          field: "segment",
          includeAll: true,
          targets: [{ dataset: "weekly_revenue", field: "segment" }],
        },
      ],
      cards: [
        {
          id: "revenue_card",
          description: "Current period revenue and growth.",
          dataset: "weekly_revenue",
          sourceId: "weekly_revenue_sql",
          filter: { segment: "Alpha" },
          metrics: [
            { label: "Revenue", field: "revenue_m", format: "currency" },
            { label: "Growth", field: "growth", format: "percent", signed: true },
          ],
        },
      ],
      charts: [
        {
          id: "revenue_chart",
          title: "Revenue by segment",
          subtitle: "Beta is the largest segment.",
          headerMarkdown: "Data is shown for the **current period**.",
          type: "bar",
          dataset: "weekly_revenue",
          sourceId: "weekly_revenue_sql",
          valueFormat: "currency",
          encodings: {
            x: { field: "segment", type: "nominal", label: "Segment" },
            y: { field: "revenue_m", type: "quantitative", label: "Revenue" },
            tooltip: [{ field: "growth", type: "quantitative", label: "Growth", format: "percent" }],
          },
        },
      ],
      tables: [
        {
          id: "revenue_table",
          title: "Revenue detail",
          subtitle: "Reviewed rows used in the analysis.",
          dataset: "weekly_revenue",
          sourceId: "weekly_revenue_sql",
          defaultSort: { field: "revenue_m", direction: "desc" },
          columns: [
            { field: "segment", label: "Segment", type: "text" },
            { field: "revenue_m", label: "Revenue", format: "currency" },
            { field: "growth", label: "Growth", format: "percent" },
          ],
        },
      ],
      sources: [
        {
          id: "weekly_revenue_sql",
          label: "Revenue warehouse query",
          path: "queries/revenue.sql",
        },
      ],
      blocks: [
        {
          id: "summary",
          type: "markdown",
          body: "## Summary\n\n- **Beta** leads revenue.\n- Growth remains positive.",
        },
        { id: "metrics", type: "metric-strip", cardIds: ["revenue_card"] },
        { id: "chart", type: "chart", chartId: "revenue_chart" },
        { id: "table", type: "table", tableId: "revenue_table" },
        {
          id: "custom",
          type: "html",
          body: '<section class="custom-insight"><strong>Custom insight</strong></section>',
        },
      ],
    },
    snapshot: {
      version: 1,
      generatedAt: "2026-07-07T12:00:00Z",
      status: "partial",
      datasets: {
        weekly_revenue: [
          { segment: "Alpha", revenue_m: 12, growth: 0.08 },
          { segment: "Beta", revenue_m: 18, growth: 0.12 },
        ],
      },
      accessIssues: [
        {
          id: "forecast_unavailable",
          dataset: "forecast",
          message: "Forecast data was not available for this snapshot.",
        },
      ],
    },
    sources: [
      {
        id: "weekly_revenue_sql",
        query: {
          engine: "trino",
          sql: "SELECT segment, revenue_m, growth FROM warehouse.weekly_revenue",
          description: "Loads reviewed weekly revenue by segment.",
          executed_at: "2026-07-07T11:55:00Z",
        },
      },
    ],
    package_info: {
      originUrl: "artifact://revenue-momentum",
      controls: { edit: true, refresh: true },
    },
  };
}

function templateBody(html, id) {
  const match = new RegExp(`<template id="${id}"[^>]*>([\\s\\S]*?)<\\/template>`).exec(html);
  assert.ok(match, `expected ${id} template`);
  return match[1];
}

function templateText(html, id) {
  return templateBody(html, id).replace(/\s/g, "");
}

function decodeTemplate(html, id) {
  return gunzipSync(Buffer.from(templateText(html, id), "base64")).toString("utf8");
}

function fallbackItem(html, tag, attribute, id) {
  const match = new RegExp(`<${tag}[^>]*${attribute}="${id}"[^>]*>([\\s\\S]*?)<\\/${tag}>`).exec(html);
  assert.ok(match, `expected ${attribute}=${id}`);
  return match[0];
}

function packagedRuntimeExists() {
  const prefix = `${READER_ASSET}.gz.b64.part`;
  return readdirSync(assetDirectory).some((name) => name.startsWith(prefix));
}

test("portable builder reuses canonical validation and prepares one read-only reader payload", () => {
  const prepared = preparePortablePayload(artifactInput());

  assert.equal(prepared.widget_type, "artifact");
  assert.equal(prepared.package_info.mode, "portable_html");
  assert.equal(prepared.package_info.deliveryMode, "portable_html");
  assert.equal(prepared.package_info.portableHtml, true);
  assert.equal(prepared.package_info.readOnly, true);
  assert.equal(prepared.package_info.controls.edit, false);
  assert.equal(prepared.package_info.controls.refresh, false);
  assert.equal(prepared.package_info.controls.persistence, false);
  assert.equal(prepared.package_info.controls.copyAsImage, false);
  assert.deepEqual(prepared.packageInfo, prepared.package_info);
  assert.equal(prepared.manifest.sources[0].path, "queries/revenue.sql");
  assert.equal(
    prepared.sources[0].query.sql,
    "SELECT segment, revenue_m, growth FROM warehouse.weekly_revenue",
  );
  assert.equal(prepared.manifest.sources[0].label, "Revenue warehouse query");
});

test("portable builder output is deterministic, self-contained, and progressively enhanced", () => {
  const first = buildPortableArtifact(artifactInput(), { runtimeHtml: fakeRuntime });
  const second = buildPortableArtifact(artifactInput(), { runtimeHtml: fakeRuntime });

  assert.equal(first, second);
  assert.match(first, /<!doctype html>/);
  assert.match(first, /<meta name="color-scheme" content="light dark" \/>/);
  assert.match(first, new RegExp(`id="${FALLBACK_ROOT_ID}"`));
  assert.match(first, /data-portable-fallback="true"/);
  assert.doesNotMatch(first, /data-static-chart-id=/);
  assert.equal(first.match(/data-data-analytics-portable-source-tooltips="true"/g)?.length, 1);
  assert.match(first, /data-data-analytics-portable-loader="true"/);
  assert.ok(
    first.indexOf('data-data-analytics-portable-source-tooltips="true"')
      < first.indexOf('data-data-analytics-portable-loader="true"'),
    "the lightweight source runtime should run before the enhanced reader loader",
  );
  assert.match(first, /data-portable-source-tooltips-ready/);
  assert.match(first, /data-portable-source-tooltip-open/);
  assert.match(first, /data-portable-source-tooltip-mobile-positioned/);
  assert.match(
    first,
    /html:not\(\[data-portable-source-tooltips-ready\]\) \.portable-source-tooltip-content\{position:absolute;top:auto;right:auto;bottom:calc\(100% \+ 8px\);left:50%;max-width:min\(360px,80vw\);transform:translateX\(-50%\)\}/,
  );
  assert.match(first, /--portable-safe-area-top:env\(safe-area-inset-top,0px\)/);
  assert.match(first, /--portable-safe-area-right:env\(safe-area-inset-right,0px\)/);
  assert.match(first, /--portable-safe-area-bottom:env\(safe-area-inset-bottom,0px\)/);
  assert.match(first, /--portable-safe-area-left:env\(safe-area-inset-left,0px\)/);
  assert.match(
    first,
    /@media screen and \(max-width:760px\)\{[^\n]*\.portable-page-header\{position:static;[^}]*flex-direction:column;[^}]*border-bottom:0;background:transparent;[^}]*\}/,
  );
  assert.doesNotMatch(first, /data-portable-title-block/);
  assert.match(
    first,
    /\.portable-page-meta\{order:-1;display:flex;[^}]*font-size:11px;[^}]*text-transform:uppercase\}/,
  );
  assert.match(first, /\.portable-table-source-region\{width:fit-content;max-width:100%\}/);
  assert.match(first, /\.portable-table-source-cell\{overflow:visible!important\}/);
  assert.match(first, /\.portable-source-tooltip\{[^}]*cursor:help;[^}]*text-decoration:underline dotted;[^}]*touch-action:manipulation\}/);
  assert.match(first, /\.portable-table-scroll:has\(\.portable-source-tooltip:hover\)/);
  assert.doesNotMatch(first, /portable-table-source-side/);
  assert.doesNotMatch(first, /top:64px;right:16px/);
  assert.match(first, /const viewport = window\.visualViewport/);
  assert.match(first, /viewport\?\.offsetTop \?\? 0/);
  assert.match(first, /viewport\?\.offsetLeft \?\? 0/);
  assert.match(first, /rootPixelValue\("--portable-safe-area-left"\)/);
  assert.match(first, /rootPixelValue\("--portable-safe-area-right"\)/);
  assert.match(first, /rootPixelValue\("--portable-safe-area-top"\)/);
  assert.match(first, /rootPixelValue\("--portable-safe-area-bottom"\)/);
  assert.match(first, /const MOBILE_POSITIONED_ATTRIBUTE = "data-portable-source-tooltip-mobile-positioned"/);
  assert.match(first, /host\.setAttribute\(MOBILE_POSITIONED_ATTRIBUTE, "true"\)/);
  assert.match(first, /data-portable-source-tooltip-mobile-positioned\]>\.portable-source-tooltip-content/);
  assert.match(first, /--portable-source-tooltip-mobile-left/);
  assert.match(first, /--portable-source-tooltip-mobile-top/);
  assert.match(first, /--portable-source-tooltip-mobile-width/);
  assert.match(first, /--portable-source-tooltip-mobile-max-height/);
  assert.ok(first.includes('const cell = target.closest("td.portable-table-source-cell");'));
  assert.ok(first.includes('host = cell?.querySelector(":scope > " + HOST_SELECTOR) ?? null;'));
  assert.match(first, /window\.visualViewport\?\.addEventListener\("resize", handleViewportChange\)/);
  assert.match(first, /window\.visualViewport\?\.addEventListener\("scroll", handleViewportChange\)/);
  assert.match(first, /SCROLL_DISMISS_THRESHOLD = 24/);
  assert.match(first, /function handlePointerDown\(event\)/);
  assert.match(first, /document\.addEventListener\("pointerdown", handlePointerDown, true\)/);
  assert.match(first, /keeping the CSS fallback/);
  assert.match(first, /const DISCOVERABLE_SELECTOR = "\.portable-source-tooltip"/);
  assert.match(first, /host\.setAttribute\("role", "button"\)/);
  assert.match(first, /host\.setAttribute\("aria-expanded"/);
  assert.match(first, /__DATA_ANALYTICS_PORTABLE_ARTIFACT__/);
  assert.doesNotMatch(first, /type="application\/json"/);
  assert.match(first, /DecompressionStream/);
  assert.match(first, /requestAnimationFrame\(\(\) => window\.setTimeout/);
  assert.match(first, /dataAnalyticsPortableReader = "unsupported"/);
  assert.match(first, /dataAnalyticsPortableReader = "failed"/);
  assert.match(first, /keeping semantic fallback/);
  assert.match(first, new RegExp(READER_READY_EVENT));
  assert.match(first, /fallback\.classList\.add\("portable-enhanced-hidden"\)/);
  assert.doesNotMatch(first, new RegExp(`<main[^>]+id="${FALLBACK_ROOT_ID}"[^>]+hidden`));
  assert.match(first, /connect-src &#39;none&#39;/);
  assert.match(first, /default-src &#39;none&#39;/);

  const payload = JSON.parse(decodeTemplate(first, PAYLOAD_SOURCE_ID));
  const runtime = decodeTemplate(first, RUNTIME_SOURCE_ID);
  assert.equal(payload.manifest.title, "Revenue momentum");
  assert.equal(payload.package_info.controls.share, false);
  assert.equal(runtime, fakeRuntime);
});

test("static fallback removes duplicate title headings without changing the payload", () => {
  const input = artifactInput();
  input.manifest.blocks.unshift({
    id: "title",
    type: "markdown",
    body: "# Revenue momentum",
  });

  const payload = preparePortablePayload(input);
  const fallback = semanticFallback(payload);
  const embedded = JSON.parse(decodeTemplate(
    buildPortableArtifact(input, { runtimeHtml: fakeRuntime }),
    PAYLOAD_SOURCE_ID,
  ));
  assert.equal(payload.manifest.blocks[0].body, "# Revenue momentum");
  assert.deepEqual(embedded.manifest.blocks, payload.manifest.blocks);
  assert.equal(fallback.match(/<h1>Revenue momentum<\/h1>/g)?.length, 1);
  assert.doesNotMatch(fallback, /data-artifact-block-id="title"/);

  const titleBlock = payload.manifest.blocks.shift();
  payload.manifest.blocks.push(titleBlock);
  assert.doesNotMatch(
    semanticFallback(payload),
    /data-artifact-block-id="title"/,
    "the static fallback should not depend on the duplicate title block's position",
  );

  for (const body of ["# *Revenue momentum*", "# Revenue  momentum"]) {
    input.manifest.blocks[0].body = body;
    const equivalentTitleFallback = semanticFallback(preparePortablePayload(input));
    assert.equal(equivalentTitleFallback.match(/<h1>Revenue momentum<\/h1>/g)?.length, 1);
    assert.doesNotMatch(equivalentTitleFallback, /data-artifact-block-id="title"/);
  }

  input.manifest.title = "Résumé momentum";
  input.manifest.blocks[0].body = "# Re\u0301sume\u0301 momentum";
  assert.doesNotMatch(
    semanticFallback(preparePortablePayload(input)),
    /data-artifact-block-id="title"/,
    "visually equivalent Unicode title forms should deduplicate",
  );
  input.manifest.title = "Revenue momentum";

  input.manifest.title = "**Revenue momentum**";
  input.manifest.blocks[0].body = "# Revenue momentum";
  const literalMarkdownTitleFallback = semanticFallback(preparePortablePayload(input));
  assert.match(literalMarkdownTitleFallback, /<h1>\*\*Revenue momentum\*\*<\/h1>/);
  assert.match(literalMarkdownTitleFallback, /data-artifact-block-id="title"/);
  input.manifest.title = "Revenue momentum";

  for (const body of [
    "## Revenue momentum",
    "# Different title",
    "# `*Revenue momentum*`",
  ]) {
    input.manifest.blocks[0].body = body;
    assert.match(
      semanticFallback(preparePortablePayload(input)),
      /data-artifact-block-id="title"/,
      `should preserve non-duplicate title content ${JSON.stringify(body)}`,
    );
  }

  input.manifest.blocks[0].sourceId = "weekly_revenue_sql";
  input.manifest.blocks[0].body = [
    "# Revenue momentum",
    "",
    "*Generated July 9, 2026*",
    "",
    "## Executive Summary",
    "",
    "Additional context reached **$12M**.",
  ].join("\n");
  const mixedContentFallback = semanticFallback(preparePortablePayload(input));
  const mixedContentBlock = fallbackItem(
    mixedContentFallback,
    "div",
    "data-artifact-block-id",
    "title",
  );
  assert.match(mixedContentFallback, /data-artifact-block-id="title"/);
  assert.match(mixedContentBlock, /<em>Generated July 9, 2026<\/em>/);
  assert.match(mixedContentBlock, /<h2>Executive Summary<\/h2>/);
  assert.match(mixedContentBlock, /class="portable-source-tooltip portable-source-value"/);
  assert.match(mixedContentBlock, /class="portable-inline-source portable-source-summary"/);
  assert.equal(mixedContentFallback.match(/<h1>Revenue momentum<\/h1>/g)?.length, 1);

  input.manifest.blocks[0].body = "# Revenue momentum\n\n```text\n  retained  ";
  assert.match(
    fallbackItem(
      semanticFallback(preparePortablePayload(input)),
      "div",
      "data-artifact-block-id",
      "title",
    ),
    /<pre><code>  retained  <\/code><\/pre>/,
    "stripping the title should preserve authored whitespace in the remaining markdown",
  );
});

test("mobile static source tooltips escape table clipping without duplicating tooltip content", () => {
  const html = buildPortableArtifact(artifactInput(), { runtimeHtml: fakeRuntime });

  assert.match(
    html,
    /@media screen and \(max-width:600px\)\{html:not\(\[data-portable-source-tooltips-ready\]\) \.portable-table-scroll:focus-within\{overflow:visible\}html:not\(\[data-portable-source-tooltips-ready\]\) td\.portable-table-source-cell:focus-within\{overflow:visible!important\}/,
  );
  assert.match(
    html,
    /\.portable-source-tooltip-content\[data-portable-source-tooltip-mobile-portaled\]\{position:fixed;z-index:1000;/,
  );
  assert.match(
    html,
    /\.portable-source-tooltip-content\[data-portable-source-tooltip-mobile-portaled\]\[data-portable-source-tooltip-mobile-positioned\]\{top:var\(--portable-source-tooltip-mobile-top\);/,
  );
  assert.match(
    html,
    /const MOBILE_PORTALED_ATTRIBUTE = "data-portable-source-tooltip-mobile-portaled"/,
  );
  assert.ok(html.includes('split(/\\s+/u)'), "generated runtime should preserve the described-by whitespace matcher");
  assert.match(
    html,
    /activeTooltipOrigin = \{ nextSibling: tooltip\.nextSibling, parent, tooltip \};\s+tooltip\.setAttribute\(MOBILE_PORTALED_ATTRIBUTE, "true"\);\s+fallback\.appendChild\(tooltip\);/,
  );
  assert.match(
    html,
    /const \{ nextSibling, parent, tooltip \} = origin;\s+tooltip\.removeAttribute\(MOBILE_PORTALED_ATTRIBUTE\);\s+tooltip\.removeAttribute\(MOBILE_POSITIONED_ATTRIBUTE\);\s+if \(nextSibling\?\.parentNode === parent\) parent\.insertBefore\(tooltip, nextSibling\);\s+else parent\.appendChild\(tooltip\);/,
  );
  assert.match(
    html,
    /tooltip\.setAttribute\(MOBILE_POSITIONED_ATTRIBUTE, "true"\)/,
  );
  assert.match(
    html,
    /if \(placementFrame\) \{\s+window\.cancelAnimationFrame\(placementFrame\);\s+placementFrame = 0;\s+\}\s+const host = activeHost;/,
  );
  assert.doesNotMatch(html, /cloneNode\s*\(/);
  assert.match(html, /window\.addEventListener\("beforeprint", \(\) => closeMobileTray\(\)\)/);
  assert.match(
    html,
    new RegExp(`window\\.addEventListener\\("${READER_READY_EVENT}", \\(\\) => closeMobileTray\\(\\), \\{ once: true \\}\\)`),
  );
  assert.match(
    html,
    new RegExp(`document\\.addEventListener\\("${READER_READY_EVENT}", \\(\\) => closeMobileTray\\(\\), \\{ once: true \\}\\)`),
  );
});

test("portable builder can embed responsive light and dark chart SVGs without losing semantic data", () => {
  const options = { runtimeHtml: fakeRuntime, staticCharts };
  const first = buildPortableArtifact(artifactInput(), options);
  const second = buildPortableArtifact(artifactInput(), options);
  const payload = preparePortablePayload(artifactInput());
  const fallback = semanticFallback(payload, { staticCharts });

  assert.equal(first, second);
  assert.match(first, /data-static-chart-id="revenue_chart"/);
  assert.match(first, /class="portable-static-chart"[^>]+role="img"[^>]+aria-label="Revenue by segment chart"/);
  assert.match(first, /class="portable-static-chart"[^>]+style="max-width:640px"/);
  assert.match(first, /portable-static-chart-light[^>]*aria-hidden="true"><svg/);
  assert.match(first, /portable-static-chart-dark[^>]*aria-hidden="true"><svg/);
  assert.match(first, /class="portable-static-chart-svg" focusable="false"/);
  assert.match(first, /clip-path="url\(#portable-chart-light-clip\)"/);
  assert.match(first, /class="portable-static-chart-legend"/);
  assert.doesNotMatch(first, /<img[^>]+portable-static-chart|data:image\//);
  assert.match(first, /<div class="portable-chart-data portable-chart-data-has-vector"><div class="portable-table-scroll">/);
  assert.doesNotMatch(first, /View chart data/);
  assert.match(first, /\.portable-chart-data-has-vector\{position:absolute!important;display:block!important;width:1px!important/);
  assert.match(first, /Revenue by segment data/);
  assert.match(first, /Source for Data is shown for the current period\./);
  assert.match(first, /@media print\{[\s\S]*?\.portable-static-chart-light\{display:block!important\}/);
  assert.match(first, /@media print\{[\s\S]*?\.portable-static-chart-dark\{display:none!important\}/);
  assert.match(fallback, /data-static-chart-id="revenue_chart"/);

  assert.doesNotThrow(() => semanticFallback(payload, {
    staticCharts: {
      chart: {
        ...staticCharts.chart,
        light: {
          ...staticCharts.chart.light,
          legend: {
            ...staticCharts.chart.light.legend,
            items: [{ ...staticCharts.chart.light.legend.items[0], label: "x".repeat(500) }],
          },
        },
      },
    },
  }));
  assert.throws(
    () => semanticFallback(payload, {
      staticCharts: {
        chart: {
          ...staticCharts.chart,
          light: {
            ...staticCharts.chart.light,
            legend: {
              ...staticCharts.chart.light.legend,
              items: [{ ...staticCharts.chart.light.legend.items[0], label: "x".repeat(501) }],
            },
          },
        },
      },
    }),
    /1 through 500 characters/,
  );

  assert.throws(
    () => semanticFallback(payload, {
      staticCharts: {
        chart: {
          ...staticCharts.chart,
          light: { ...staticCharts.chart.light, svg: '<svg onload="alert(1)" xmlns="http://www.w3.org/2000/svg"><rect></rect></svg>' },
        },
      },
    }),
    /unsupported active or externally styled SVG content/,
  );
  assert.throws(
    () => semanticFallback(payload, {
      staticCharts: {
        chart: {
          ...staticCharts.chart,
          light: { ...staticCharts.chart.light, svg: '<svg xmlns="http://www.w3.org/2000/svg"><foreignObject></foreignObject></svg>' },
        },
      },
    }),
    /unsupported <foreignObject> content/,
  );
  assert.throws(
    () => semanticFallback(payload, {
      staticCharts: {
        chart: {
          ...staticCharts.chart,
          light: { ...staticCharts.chart.light, svg: '<svg xmlns="http://www.w3.org/2000/svg"><rect fill="url(https://example.com/a.svg#paint)"></rect></svg>' },
        },
      },
    }),
    /external SVG reference/,
  );
  assert.throws(
    () => semanticFallback(payload, {
      staticCharts: {
        chart: {
          ...staticCharts.chart,
          light: { ...staticCharts.chart.light, svg: '<svg xmlns="http://www.w3.org/2000/svg"><rect clip-path="url(#missing)"></rect></svg>' },
        },
      },
    }),
    /unresolved SVG reference/,
  );
  assert.throws(
    () => semanticFallback(payload, {
      staticCharts: {
        chart: {
          ...staticCharts.chart,
          light: {
            ...staticCharts.chart.light,
            svg: '<svg xmlns="http://www.w3.org/2000/svg"><g><g><script x="y"</g>globalThis.__svgPwned=41+1</script x="y"</g></svg>',
          },
        },
      },
    }),
    /malformed SVG markup/,
  );
  assert.throws(
    () => semanticFallback(payload, {
      staticCharts: {
        chart: {
          ...staticCharts.chart,
          light: {
            ...staticCharts.chart.light,
            svg: '<svg xmlns="http://www.w3.org/2000/svg"><rect fill="&#117;rl(&#104;ttps&#58;//example.com/a.svg)"></rect></svg>',
          },
        },
      },
    }),
    /external SVG reference/,
  );
  assert.throws(
    () => semanticFallback(payload, {
      staticCharts: {
        chart: {
          ...staticCharts.chart,
          light: {
            ...staticCharts.chart.light,
            svg: '<svg xmlns="https://example.com/not-svg"><rect></rect></svg>',
          },
        },
      },
    }),
    /standard SVG namespace/,
  );
  assert.throws(
    () => semanticFallback(payload, {
      staticCharts: {
        chart: {
          ...staticCharts.chart,
          light: {
            ...staticCharts.chart.light,
            svg: '<svg xmlns="http://www.w3.org/2000/svg"><g><rect></rect></svg>',
          },
        },
      },
    }),
    /unbalanced SVG elements/,
  );
  assert.throws(
    () => semanticFallback(payload, {
      staticCharts: {
        chart: {
          ...staticCharts.chart,
          light: {
            ...staticCharts.chart.light,
            svg: '<svg xmlns="http://www.w3.org/2000/svg"><rect clip-path="URL(#missing)"></rect></svg>',
          },
        },
      },
    }),
    /unresolved SVG reference/,
  );
  assert.throws(
    () => semanticFallback(payload, {
      staticCharts: { chart: { ...staticCharts.chart, width: 0 } },
    }),
    /integer from 1 through 10000/,
  );
});

test("portable runtime input is strictly decoded, cross-checked, and canonically re-encoded", () => {
  const canonicalEncoded = encodeCompressedText(fakeRuntime);
  const differentRuntime = fakeRuntime.replace("payload.manifest.title", "payload.manifest.description");

  assert.throws(
    () => buildPortableArtifact(artifactInput(), {
      runtimeEncoded: encodeCompressedText(differentRuntime),
      runtimeHtml: fakeRuntime,
    }),
    /must decode to identical runtime HTML/,
  );

  const alignment = "A".repeat((76 - (canonicalEncoded.length % 76)) % 76);
  const breakout = `${canonicalEncoded}${alignment}</template><script>globalThis.__portableInjected=true</script><template>`;
  assert.throws(
    () => buildPortableArtifact(artifactInput(), { runtimeEncoded: breakout }),
    /canonical base64/,
  );

  const html = buildPortableArtifact(artifactInput(), {
    runtimeEncoded: canonicalEncoded,
    runtimeHtml: fakeRuntime,
  });
  assert.equal(templateText(html, RUNTIME_SOURCE_ID), canonicalEncoded);
  assert.doesNotMatch(html, /__portableInjected/);
});

test("portable provenance preserves the canonical source object without mutating safe fields", () => {
  const input = artifactInput();
  input.package_info = {
    controls: { edit: true },
    debug: true,
    manifestPath: "/Users/alex/private/manifest.json",
    originUrl: "artifact://private-revenue",
    request_id: "request-secret-123",
    root: "/Users/alex/private/customer",
  };
  input.manifest.sources[0].path = "queries/revenue.sql";
  input.manifest.sources[0].href = "https://analytics.example/revenue?request_id=request-secret-123#debug";
  input.sources[0].query.id = "request-123";
  input.sources[0].query.url = "https://warehouse.example/query?request_id=request-123#debug";
  input.sources[0].query.tables_used = ["warehouse.weekly_revenue"];
  input.sources[0].query.metric_definitions = ["Revenue is the reviewed weekly total"];
  input.sources[0].query.owner = { team: "Revenue analytics" };

  const prepared = preparePortablePayload(input);
  const source = prepared.sources[0];
  const serialized = JSON.stringify(prepared);

  assert.deepEqual(Object.keys(prepared.package_info).sort(), [
    "artifactRuntime",
    "controls",
    "deliveryMode",
    "hostedReadOnly",
    "mode",
    "portableHtml",
    "readOnly",
  ]);
  assert.equal(source.id, "weekly_revenue_sql");
  assert.equal(source.label, "Revenue warehouse query");
  assert.equal(source.path, "queries/revenue.sql");
  assert.equal(source.href, "https://analytics.example/revenue?request_id=request-secret-123#debug");
  assert.equal(source.query.id, "request-123");
  assert.equal(source.query.url, "https://warehouse.example/query?request_id=request-123#debug");
  assert.equal(source.query.sql, "SELECT segment, revenue_m, growth FROM warehouse.weekly_revenue");
  assert.deepEqual(source.query.tables_used, ["warehouse.weekly_revenue"]);
  assert.deepEqual(source.query.metric_definitions, ["Revenue is the reviewed weekly total"]);
  assert.deepEqual(source.query.owner, { team: "Revenue analytics" });
  assert.equal(prepared.manifest.sources[0].href, input.manifest.sources[0].href);
  assert.doesNotMatch(serialized, /\/Users\/alex\/private\/(?:manifest\.json|customer)|artifact:\/\/private-revenue|"debug":true/);
});

test("portable provenance rejects unsafe credential and local-path data instead of rewriting it", () => {
  const credential = artifactInput();
  credential.sources[0].query.sql = "SELECT * FROM warehouse.weekly_revenue WHERE password = 'portable-secret'";
  assert.throws(
    () => preparePortablePayload(credential),
    /credential-like text/,
  );

  const localPath = artifactInput();
  localPath.manifest.sources[0].path = "/Users/alex/private/revenue.sql";
  assert.throws(
    () => preparePortablePayload(localPath),
    /local filesystem path/,
  );

  const credentialUrl = artifactInput();
  credentialUrl.sources[0].query.url = "https://warehouse.example/query?token=portable-secret";
  assert.throws(
    () => preparePortablePayload(credentialUrl),
    /sensitive URL parameter/,
  );

  const credentialUserInfo = artifactInput();
  credentialUserInfo.sources[0].query.url = "https://user:password@warehouse.example/query";
  assert.throws(
    () => preparePortablePayload(credentialUserInfo),
    /URL credentials/,
  );

  for (const unsafeUrl of [
    "https://warehouse.example/query?signature=portable-secret",
    "https://warehouse.example/query?X-Amz-Credential=portable-secret",
    "https://warehouse.example/query?X-Amz-Signature=portable-secret",
  ]) {
    const signedUrl = artifactInput();
    signedUrl.sources[0].query.url = unsafeUrl;
    assert.throws(
      () => preparePortablePayload(signedUrl),
      /sensitive URL parameter/,
    );
  }

  for (const unsafePath of [
    "/etc/private/report.sql",
    "/Volumes/private/report.sql",
    "../private/report.sql",
    "queries/../private/report.sql",
    "..\\private\\report.sql",
    "queries\\..\\private\\report.sql",
    "C:\\Users\\alex\\private\\report.sql",
    "D:/private/report.sql",
    "\\\\server\\share\\report.sql",
  ]) {
    const absolutePath = artifactInput();
    absolutePath.manifest.sources[0].path = unsafePath;
    assert.throws(
      () => preparePortablePayload(absolutePath),
      /local filesystem path/,
    );
  }
});

test("print media restores the semantic fallback and suppresses the hydrated reader", () => {
  const html = buildPortableArtifact(artifactInput(), { runtimeHtml: fakeRuntime });
  const fallback = semanticFallback(preparePortablePayload(artifactInput()));

  assert.match(html, /@media screen\{\.portable-fallback\.portable-enhanced-hidden,\.portable-sources,\.portable-source-summary\{display:none!important\}\}/);
  assert.match(
    html,
    new RegExp(`@media print\\{#${READER_ROOT_ID}\\{display:none!important\\}`),
  );
  assert.match(html, /\.portable-fallback\{display:block!important;width:100%;padding:0\}/);
  assert.match(html, /\.portable-sources\{display:none!important\}/);
  assert.match(html, /\.portable-source-tooltip\{cursor:inherit;text-decoration:none\}/);
  assert.match(
    html,
    /\.portable-source-tooltip>\.portable-source-tooltip-content,\.portable-source-tooltip-content\[data-portable-source-tooltip-mobile-portaled\]\{display:none!important\}/,
  );
  assert.match(html, /\.portable-inline-source\{position:static!important;inset:auto!important;display:block!important/);
  assert.match(html, /\.portable-source-tooltip-content,\.portable-source-summary-content\{position:static!important/);
  assert.match(html, /max-height:none!important;padding:0!important;overflow:visible!important/);
  assert.doesNotMatch(html, /class="portable-source-tooltip-trigger"/);
  assert.match(html, /fallback\.classList\.add\("portable-enhanced-hidden"\)/);
  assert.doesNotMatch(html, /fallback\.hidden\s*=\s*true/);
  assert.doesNotMatch(html, /fallback\.setAttribute\("aria-hidden"/);
  assert.match(
    html,
    /<details class="portable-source-query" open><summary>SQL query<\/summary><pre><code>SELECT segment, revenue_m, growth/,
  );
  assert.equal(fallback.match(/class="portable-inline-source portable-source-summary"/g)?.length, 2);
  assert.equal(fallback.match(/class="portable-inline-source-content portable-source-summary-content"/g)?.length, 2);
  assert.equal(fallback.match(/>Source for Revenue<\/span>/g)?.length, 1);
  assert.equal(fallback.match(/>Source for Revenue detail<\/span>/g)?.length, 1);
});

test("semantic fallback follows manifest block order and covers common artifact content", () => {
  const payload = preparePortablePayload(artifactInput());
  const fallback = semanticFallback(payload);
  const blockIds = ["summary", "metrics", "chart", "table", "custom"];
  const offsets = blockIds.map((id) => fallback.indexOf(`data-artifact-block-id="${id}"`));

  assert.ok(offsets.every((offset) => offset >= 0));
  assert.deepEqual(offsets, [...offsets].sort((left, right) => left - right));
  assert.match(fallback, /<h2>Summary<\/h2>/);
  assert.match(fallback, /portable-metric-value"><span class="portable-source-tooltip portable-source-value"[^>]*><span class="portable-source-value-text">\$12<\/span>/);
  assert.match(fallback, /data-artifact-id="metric:metrics:revenue_card" data-artifact-kind="card"/);
  assert.match(fallback, /Revenue by segment data/);
  assert.match(fallback, /<th scope="col" class="portable-table-number">Growth<\/th>/);
  assert.match(fallback, /Data access issues/);
  assert.match(fallback, /Forecast data was not available/);
  assert.match(fallback, /Revenue warehouse query/);
  assert.match(fallback, /SELECT segment, revenue_m, growth/);
  assert.match(fallback, /<details class="portable-source-query" open>/);
  const metric = fallbackItem(fallback, "article", "data-card-id", "revenue_card");
  const table = fallbackItem(fallback, "section", "data-table-id", "revenue_table");
  const valueTriggers = [...fallback.matchAll(/<span class="portable-source-tooltip portable-source-value" data-portable-source-host="true" tabindex="0" aria-describedby="(portable-source-tooltip-\d+)">/g)];
  const sourceHosts = [...fallback.matchAll(/data-portable-source-host="true" tabindex="0"(?: aria-label="[^"]+")? aria-describedby="(portable-source-tooltip-\d+)"/g)];
  const tooltipIds = [...fallback.matchAll(/class="(?:portable-inline-source-content )?portable-source-tooltip-content" id="(portable-source-tooltip-\d+)" role="tooltip"/g)];

  assert.equal(valueTriggers.length, 6);
  assert.equal(table.match(/class="portable-source-tooltip portable-source-value"/g)?.length, 4);
  assert.equal(sourceHosts.length, 7);
  assert.equal(new Set(sourceHosts.map((match) => match[1])).size, 7);
  assert.equal(tooltipIds.length, 7);
  assert.deepEqual(
    new Set(tooltipIds.map((match) => match[1])),
    new Set(sourceHosts.map((match) => match[1])),
  );
  assert.doesNotMatch(metric, /<article[^>]*data-portable-source-host/);
  assert.doesNotMatch(table, /<div class="portable-table-source-region"[^>]*data-portable-source-host/);
  assert.match(table, /<td>Beta<\/td>/);
  assert.match(table, /<td>Alpha<\/td>/);
  assert.match(table, /<td class="portable-table-source-cell portable-table-number"><span class="portable-source-tooltip portable-source-value"/);
  assert.equal(fallback.match(/class="portable-inline-source portable-source-summary"/g)?.length, 2);
  assert.equal(fallback.match(/<div class="portable-inline-source" data-source-id="weekly_revenue_sql">/g)?.length, 1);
  assert.equal(fallback.match(/class="portable-source-query-data"/g)?.length, 3);
  assert.equal(fallback.match(/class="portable-source-description-data"/g)?.length, 3);
  assert.match(fallback, />Source for Revenue<\/span>/);
  assert.match(fallback, /data-portable-visual-title="Data is shown for the current period\."/);
  assert.match(fallback, />Source for Data is shown for the current period\.<\/span>/);
  assert.match(fallback, />Source for Revenue detail<\/span>/);
  assert.doesNotMatch(fallback, /portable-source-tooltip-trigger|portable-source-disclosure|>Source<\/summary>|<button\b/);
  assert.doesNotMatch(fallback, /class="portable-source-tooltip portable-source-value"[^>]*\stitle=/);
  assert.match(fallback, /<strong>Source: Revenue warehouse query<\/strong><span class="portable-source-meta">Table: warehouse\.weekly_revenue<\/span>/);
  assert.match(fallback, /class="portable-source-query-data" aria-hidden="true"><code>SELECT segment, revenue_m, growth/);
  assert.match(fallback, /class="portable-source-description-data">Loads reviewed weekly revenue by segment/);
  assert.match(fallback, /<iframe sandbox=""/);
  assert.match(fallback, /script-src &#39;none&#39;/);
});

test("source-backed markdown exposes quantitative literals without annotating incidental numbers", () => {
  const input = artifactInput();
  input.manifest.blocks[0] = {
    ...input.manifest.blocks[0],
    sourceId: "weekly_revenue_sql",
    body: [
      "## Source-backed summary",
      "",
      "Revenue reached 42 with **$1.2M** booked and *18%* margin. Net adds were +24 across 1,234 accounts; pipeline is 2.4M and churn was −3%.",
      "",
      "Do not annotate `99`, [77 customers](https://example.com/metrics), July 7, 2026, 07/07/2026, 2026-07-07, 2025, Q2, FY2026, or account123.",
    ].join("\n"),
  };

  const sourcedFallback = semanticFallback(preparePortablePayload(input));
  const sourcedMarkdown = fallbackItem(
    sourcedFallback,
    "div",
    "data-artifact-block-id",
    "summary",
  );
  const sourcedValues = [...sourcedMarkdown.matchAll(
    /<span class="portable-source-value-text">([^<]+)<\/span>/g,
  )].map((match) => match[1]);

  assert.deepEqual(sourcedValues, ["42", "$1.2M", "18%", "+24", "1,234", "2.4M", "−3%"]);
  assert.equal(
    sourcedMarkdown.match(/class="portable-inline-source portable-source-summary"/g)?.length,
    1,
    "a sourced narrative should retain one print-only canonical source summary",
  );
  assert.match(sourcedMarkdown, />Source for Source-backed summary<\/span>/);
  assert.match(
    sourcedMarkdown,
    /<strong><span class="portable-source-tooltip portable-source-value"[^>]*><span class="portable-source-value-text">\$1\.2M<\/span>/,
  );
  assert.match(
    sourcedMarkdown,
    /<em><span class="portable-source-tooltip portable-source-value"[^>]*><span class="portable-source-value-text">18%<\/span>/,
  );
  assert.match(sourcedMarkdown, /<code>99<\/code>/);
  assert.match(
    sourcedMarkdown,
    /<a href="https:\/\/example\.com\/metrics" rel="noreferrer">77 customers<\/a>/,
  );
  assert.match(sourcedMarkdown, /July 7, 2026, 07\/07\/2026, 2026-07-07, 2025, Q2, FY2026, or account123/);

  delete input.manifest.blocks[0].sourceId;
  const unsourcedFallback = semanticFallback(preparePortablePayload(input));
  const unsourcedMarkdown = fallbackItem(
    unsourcedFallback,
    "div",
    "data-artifact-block-id",
    "summary",
  );

  assert.doesNotMatch(unsourcedMarkdown, /portable-source-tooltip|portable-source-value/);
  assert.doesNotMatch(unsourcedMarkdown, /portable-source-summary/);
  assert.match(
    unsourcedMarkdown,
    /Revenue reached 42 with <strong>\$1\.2M<\/strong> booked and <em>18%<\/em> margin\./,
  );
  assert.match(unsourcedMarkdown, /<code>99<\/code>/);
  assert.match(
    unsourcedMarkdown,
    /<a href="https:\/\/example\.com\/metrics" rel="noreferrer">77 customers<\/a>/,
  );
  assert.match(unsourcedMarkdown, /July 7, 2026, 07\/07\/2026, 2026-07-07, 2025, Q2, FY2026, or account123/);
});

test("semantic fallback mirrors report and dashboard layout, filter, and status defaults", () => {
  const reportInput = artifactInput("report");
  reportInput.manifest.charts[0].layout = "half";
  reportInput.manifest.tables[0].layout = "half";
  const report = semanticFallback(preparePortablePayload(reportInput));

  assert.match(report, /data-artifact-block-id="chart"[^>]+data-layout="full"/);
  assert.match(report, /data-artifact-block-id="table"[^>]+data-layout="full"/);
  assert.doesNotMatch(report, /portable-filter-bar|portable-status/);
  assert.match(report, /<time datetime="2026-07-07T12:00:00Z">Jul 7, 2026, 12:00 PM UTC<\/time>/);

  const dashboardInput = artifactInput("dashboard");
  const dashboard = semanticFallback(preparePortablePayload(dashboardInput));

  assert.match(dashboard, /data-artifact-block-id="chart"[^>]+data-layout="half"/);
  assert.match(dashboard, /data-artifact-block-id="table"[^>]+data-layout="full"/);
  assert.match(dashboard, /class="portable-filter-bar"/);
  assert.match(dashboard, /class="portable-status">partial<\/span>/);
});

test("described metrics remain discoverable without a provenance source", () => {
  const payload = preparePortablePayload(artifactInput());
  delete payload.manifest.cards[0].source;
  delete payload.manifest.cards[0].sourceId;
  const fallback = semanticFallback(payload);
  const metric = fallbackItem(fallback, "article", "data-card-id", "revenue_card");

  assert.equal(metric.match(/class="portable-source-tooltip portable-source-value"/g)?.length, 1);
  assert.match(metric, /class="portable-source-tooltip portable-source-value" data-portable-source-host="true" tabindex="0" aria-describedby="portable-source-tooltip-\d+"><span class="portable-source-value-text">\$12<\/span>/);
  assert.match(metric, /class="portable-source-context">Current period revenue and growth\.<\/span>/);
  assert.match(metric, />About \$12<\/span>/);
  assert.doesNotMatch(metric, /<article[^>]*data-portable-source-host|portable-source-summary/);
  assert.doesNotMatch(metric, /data-source-id=|<strong>Source:/);
});

test("semantic fallback applies initial filter values and table default sorting", () => {
  const input = artifactInput();
  input.manifest.filters[0].defaultValue = "Alpha";
  delete input.manifest.cards[0].filter;
  input.manifest.charts[0].subtitle = "Filtered rows only.";
  input.snapshot.datasets.weekly_revenue = [
    { segment: "Alpha", revenue_m: 7, growth: 0.04 },
    { segment: "Beta", revenue_m: 18, growth: 0.12 },
    { segment: "Alpha", revenue_m: 12, growth: 0.08 },
  ];

  const fallback = semanticFallback(preparePortablePayload(input));
  const metric = fallbackItem(fallback, "article", "data-card-id", "revenue_card");
  const chart = fallbackItem(fallback, "figure", "data-chart-id", "revenue_chart");
  const table = fallbackItem(fallback, "section", "data-table-id", "revenue_table");

  assert.match(metric, /portable-metric-value"><span class="portable-source-tooltip portable-source-value"[^>]*><span class="portable-source-value-text">\$7<\/span>/);
  assert.doesNotMatch(chart, /<td>Beta<\/td>/);
  assert.doesNotMatch(table, /<td>Beta<\/td>/);
  assert.ok(
    table.indexOf('<span class="portable-source-value-text">$12</span>')
      < table.indexOf('<span class="portable-source-value-text">$7</span>'),
  );
});

test("semantic fallback preserves every canonical table movement annotation", () => {
  for (const annotation of ["movement", "semantic", "role"]) {
    const input = artifactInput();
    const column = input.manifest.tables[0].columns[2];
    if (annotation === "movement") column.movement = true;
    else column[annotation] = "movement";
    const payload = preparePortablePayload(input);
    payload.snapshot.datasets.weekly_revenue[0].growth = 0.08;
    payload.snapshot.datasets.weekly_revenue[1].growth = "↓4%";

    const fallback = semanticFallback(payload);
    const table = fallbackItem(fallback, "section", "data-table-id", "revenue_table");
    assert.match(table, /<td class="portable-table-source-cell portable-table-number portable-table-positive"><span[^>]*><span class="portable-source-value-text">\+8%<\/span>/, annotation);
    assert.match(table, /<td class="portable-table-source-cell portable-table-number portable-table-negative"><span[^>]*><span class="portable-source-value-text">↓4%<\/span>/, annotation);
  }
});

test("semantic fallback selects explicit all aggregate rows like the shared reader", () => {
  const input = artifactInput();
  input.manifest.filters[0].defaultValue = "all";
  delete input.manifest.cards[0].filter;
  input.manifest.charts[0].subtitle = "Aggregate row only.";
  input.snapshot.datasets.weekly_revenue = [
    { segment: "Alpha", region: "East", revenue_m: 12, growth: 0.08 },
    { segment: "Beta", region: "West", revenue_m: 18, growth: 0.12 },
    { segment: "all", region: "all", revenue_m: 30, growth: 0.1 },
  ];

  const fallback = semanticFallback(preparePortablePayload(input));
  const metric = fallbackItem(fallback, "article", "data-card-id", "revenue_card");
  const chart = fallbackItem(fallback, "figure", "data-chart-id", "revenue_chart");
  const table = fallbackItem(fallback, "section", "data-table-id", "revenue_table");

  assert.match(metric, /portable-metric-value"><span class="portable-source-tooltip portable-source-value"[^>]*><span class="portable-source-value-text">\$30<\/span>/);
  assert.match(chart, /<td>all<\/td>/);
  assert.match(table, /<td>all<\/td>/);
  assert.doesNotMatch(chart, /<td>(?:Alpha|Beta)<\/td>/);
  assert.doesNotMatch(table, /<td>(?:Alpha|Beta)<\/td>/);
});

test("dashboard artifacts keep a readable fallback when their bounded snapshot is blocked or empty", () => {
  const input = artifactInput("dashboard");
  input.snapshot.status = "blocked";
  input.snapshot.datasets = {};
  input.snapshot.accessIssues = [
    {
      id: "warehouse_blocked",
      scope: "Revenue warehouse",
      message: "Warehouse access is required to populate this dashboard.",
    },
  ];

  const html = buildPortableArtifact(input, { runtimeHtml: fakeRuntime });
  const payload = JSON.parse(decodeTemplate(html, PAYLOAD_SOURCE_ID));

  assert.equal(payload.surface, "dashboard");
  assert.equal(payload.manifest.surface, "dashboard");
  assert.match(html, /Warehouse access is required/);
  assert.match(html, /portable-metric-value">—/);
  assert.match(html, /No rows available/);
});

test("payload and semantic fallback cannot break out of their inert containers", () => {
  const input = artifactInput();
  input.manifest.title = "Revenue </title><script>alert(1)</script>";
  input.manifest.blocks[0].body = "## Summary\n\n<img src=x onerror=alert(2)> [bad](javascript:alert(3))";
  input.manifest.blocks[4].body = '<script>alert(4)</script><img src="https://example.invalid/x" onerror="alert(5)">';
  input.snapshot.datasets.weekly_revenue[0].segment = "</td><script>alert(6)</script>";
  input.sources[0].query.sql = "SELECT '</script><script>alert(7)</script>' AS segment, 1 AS revenue_m, 0 AS growth";

  const html = buildPortableArtifact(input, { runtimeHtml: fakeRuntime });
  const payload = JSON.parse(decodeTemplate(html, PAYLOAD_SOURCE_ID));

  assert.equal(payload.manifest.title, input.manifest.title);
  assert.doesNotMatch(html, /<script>alert\([1-7]\)<\/script>/);
  assert.doesNotMatch(html, /<img src=x onerror=/);
  assert.match(html, /&lt;img src=x onerror=alert\(2\)&gt;/);
  assert.match(html, /href="#"/);
  assert.match(html, /&lt;script&gt;alert\(4\)&lt;\/script&gt;/);
  assert.match(html, /sandbox=""/);
  assert.match(templateText(html, PAYLOAD_SOURCE_ID), /^[A-Za-z0-9+/=]+$/);
});

test("portable artifact contains no reader network, API, or MCP-host dependency", () => {
  const html = buildPortableArtifact(artifactInput(), { runtimeHtml: fakeRuntime });

  assert.doesNotMatch(html, /\bwindow\.openai\b/);
  assert.doesNotMatch(html, /@modelcontextprotocol\/ext-apps/);
  assert.doesNotMatch(html, /\/api\/(?:manifest|snapshot|package|source|inline-chart-widget)/);
  assert.doesNotMatch(html, /\bfetch\s*\(/);
  assert.doesNotMatch(html, /<script\b[^>]*\bsrc\s*=/i);
  assert.doesNotMatch(html, /<link\b[^>]*\bhref\s*=/i);
});

test("portable reader runtime contract rejects redirects, host APIs, network calls, and missing readiness", () => {
  assert.throws(
    () => assertPortableReaderRuntime("Redirecting to the local widget source"),
    /development redirect/,
  );
  assert.throws(
    () => assertPortableReaderRuntime(`<script>window.openai.callTool();dispatchEvent(new Event("${READER_READY_EVENT}"))</script>`),
    /window\.openai/,
  );
  assert.throws(
    () => assertPortableReaderRuntime(`<script>fetch("\/api\/manifest");dispatchEvent(new Event("${READER_READY_EVENT}"))</script>`),
    /artifact API dependency|network fetch/,
  );
  assert.throws(
    () => assertPortableReaderRuntime("<!doctype html><body><div id=root></div></body>"),
    new RegExp(READER_READY_EVENT),
  );
  assert.throws(
    () => assertPortableReaderRuntime(`<script>localStorage.getItem("state");dispatchEvent(new Event("${READER_READY_EVENT}"))</script>`),
    /browser storage dependency/,
  );
  assert.throws(
    () => assertPortableReaderRuntime(`<script>navigator.sendBeacon("\/collect");dispatchEvent(new Event("${READER_READY_EVENT}"))</script>`),
    /beacon client/,
  );
  assert.throws(
    () => assertPortableReaderRuntime(`<script>location.assign("codex:\/\/threads\/new");dispatchEvent(new Event("${READER_READY_EVENT}"))</script>`),
    /top-level navigation/,
  );
  assert.throws(
    () => buildPortableArtifact(artifactInput(), { runtimeEncoded: "not-gzip" }),
  );
});

test("packaged portable reader contains no storage, navigation, network, API, or MCP dependency", {
  skip: packagedRuntimeExists() ? false : "portable reader bundle has not been built yet",
}, () => {
  const { html } = readPackagedReaderRuntime();
  assert.doesNotMatch(html, /\b(?:localStorage|sessionStorage|indexedDB)\b/i);
  assert.doesNotMatch(html, /\bnavigator\.sendBeacon\b/i);
  assert.doesNotMatch(html, /(?:\bwindow\.)?\blocation\.(?:assign|replace)\s*\(/i);
  assert.doesNotMatch(html, /\bwindow\.open\s*\(/i);
  assert.doesNotMatch(html, /\bwindow\.openai\b|@modelcontextprotocol\/ext-apps/i);
  assert.doesNotMatch(html, /\/api\/(?:manifest|snapshot|package|source|inline-chart-widget)|\bfetch\s*\(/i);
});

test("canonical validator rejects malformed, unsafe, and oversized builder inputs", () => {
  const malformed = artifactInput();
  malformed.manifest.blocks = [];
  assert.throws(
    () => buildPortableArtifact(malformed, { runtimeHtml: fakeRuntime }),
    /manifest\.blocks must contain top-level artifact blocks/,
  );

  const unsafe = artifactInput();
  unsafe.snapshot.datasets.weekly_revenue[0].api_key = "should-not-render";
  assert.throws(
    () => buildPortableArtifact(unsafe, { runtimeHtml: fakeRuntime }),
    /field name "api_key" looks unsafe/,
  );

  const oversized = artifactInput();
  oversized.snapshot.datasets.weekly_revenue = Array.from({ length: 900 }, (_, index) => ({
    segment: `Segment ${index}`,
    revenue_m: index + 1,
    growth: 0.1,
    note: "x".repeat(3_500),
  }));
  assert.throws(
    () => buildPortableArtifact(oversized, { runtimeHtml: fakeRuntime }),
    /artifact payload exceeds 3000000 bytes/,
  );
});

test("portable builder accepts a bounded payload close to the canonical three-megabyte ceiling", () => {
  const input = artifactInput();
  input.snapshot.datasets.weekly_revenue = Array.from({ length: 830 }, (_, index) => ({
    segment: `Segment ${index}`,
    revenue_m: index + 1,
    growth: 0.1,
    note: `${index}:`.padEnd(3_400, "x"),
  }));
  assert.ok(Buffer.byteLength(JSON.stringify(input)) > 2_700_000);

  const html = buildPortableArtifact(input, { runtimeHtml: fakeRuntime });
  const payload = JSON.parse(decodeTemplate(html, PAYLOAD_SOURCE_ID));

  assert.equal(payload.snapshot.datasets.weekly_revenue.length, 830);
  assert.match(html, /830 results · Showing first 50/);
});

test("packaged reader stays within runtime and fixed-overhead budgets", {
  skip: packagedRuntimeExists() ? false : "portable reader bundle has not been built yet",
}, () => {
  const html = buildPortableArtifact(artifactInput());
  const payload = preparePortablePayload(artifactInput());
  const fallback = semanticFallback(payload);
  const runtimeEncoded = templateText(html, RUNTIME_SOURCE_ID);
  const payloadBody = templateBody(html, PAYLOAD_SOURCE_ID);
  const runtimeBytes = Buffer.from(runtimeEncoded, "base64").byteLength;
  const fixedBytes = Buffer.byteLength(html) - Buffer.byteLength(fallback) - Buffer.byteLength(payloadBody);
  const maxLineLength = Math.max(...html.split("\n").map((line) => line.length));

  assert.ok(runtimeBytes <= 350_000, `reader runtime is ${runtimeBytes} gzip bytes`);
  assert.ok(fixedBytes <= 650_000, `fixed portable reader and shell overhead is ${fixedBytes} bytes`);
  assert.ok(maxLineLength < 10_000, `maximum generated line is ${maxLineLength} characters`);
});

test("documented two-argument CLI builds from packaged normalized reader parts", {
  skip: packagedRuntimeExists() ? false : "portable reader bundle has not been built yet",
}, () => {
  const directory = mkdtempSync(join(tmpdir(), "data-analytics-portable-artifact-"));
  const inputPath = join(directory, "artifact.json");
  const outputPath = join(directory, "report.html");
  const alternateOutputPath = join(directory, "report-alternate-timezone.html");
  writeFileSync(inputPath, JSON.stringify(artifactInput()), "utf8");

  const stdout = execFileSync(process.execPath, [
    builderPath,
    "--input",
    inputPath,
    "--output",
    outputPath,
  ], { encoding: "utf8", env: { ...process.env, TZ: "UTC" } });
  execFileSync(process.execPath, [
    builderPath,
    "--input",
    inputPath,
    "--output",
    alternateOutputPath,
  ], { encoding: "utf8", env: { ...process.env, TZ: "America/Los_Angeles" } });
  const output = readFileSync(outputPath, "utf8");
  const alternateOutput = readFileSync(alternateOutputPath, "utf8");

  assert.match(stdout, /validated, self-contained Data Analytics HTML artifact/);
  assert.match(output, /data-data-analytics-portable-artifact="true"/);
  assert.equal(alternateOutput, output);
  assert.equal(JSON.parse(decodeTemplate(output, PAYLOAD_SOURCE_ID)).manifest.title, "Revenue momentum");
});
