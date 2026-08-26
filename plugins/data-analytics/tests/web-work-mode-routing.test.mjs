import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { test } from "node:test";

function read(relativePath) {
  return readFileSync(new URL(relativePath, import.meta.url), "utf8");
}

test("preserves desktop data-context and MCP UI capabilities", () => {
  for (const relativePath of [
    "../.mcp.json",
    "../mcp/server.cjs",
    "../src/analytics-app/App.tsx",
    "../skills/create-data-context/SKILL.md",
    "../skills/build-dashboard/specifications/mcp-artifact-dashboard.md",
    "../skills/build-report/specifications/mcp-app-report.md",
  ]) {
    assert.equal(existsSync(new URL(relativePath, import.meta.url)), true, relativePath);
  }
});

test("classifies surface and mode independently while Work Mode overrides surface for delivery", () => {
  const index = read("../skills/index/SKILL.md");

  assert.match(index, /Classify `surface` and `mode` separately/);
  assert.match(index, /`surface = codex_desktop`/);
  assert.match(index, /`surface = chatgpt_web`/);
  assert.match(index, /`mode = work_mode`/);
  assert.match(index, /`mode = chat`/);
  assert.match(index, /Otherwise set the relevant value to `unknown`/);
  assert.match(index, /Never infer mode from surface, missing tools, tool failure/);
  assert.match(index, /When `mode = work_mode` is positively identified, apply one delivery rule regardless of whether the surface is web, desktop, or unknown/);
  assert.doesNotMatch(index, /Treat `mode = work_mode` with `surface = unknown` as a partial web Work Mode signal/);
  assert.doesNotMatch(index, /unless `surface = codex_desktop` is positively identified/);
});

test("ChatGPT web Chat mode recommends Work Mode before doing analytics work", () => {
  const index = read("../skills/index/SKILL.md");
  const dashboard = read("../skills/build-dashboard/SKILL.md");
  const report = read("../skills/build-report/SKILL.md");

  assert.match(index, /ChatGPT web Chat mode stop gate \(read first\)/);
  assert.match(index, /both `surface = chatgpt_web` and `mode = chat`/);
  assert.match(index, /respond only with a concise recommendation to switch to Work Mode/);
  assert.match(index, /Do not load focused analytics skills, inspect data or sources, call tools, ask intake questions, perform analysis, or create an artifact/);
  assert.match(index, /only after the recommendation has been shown and the user explicitly says to continue, proceed, or stay in Chat mode/);
  assert.match(index, /Repeating the original request, adding data, or answering an earlier question does not count as an override/);
  assert.match(index, /resume the original analytics request without making them restate it/);
  assert.match(index, /Follow the Work Mode branch below for intake and persistence/);
  assert.match(index, /keep `mode = chat` for delivery/);
  assert.match(index, /default durable reports and dashboards to portable HTML/);
  assert.match(index, /do not automatically publish to Sites/);
  assert.match(index, /Keep that override for the current analytics request/);
  assert.match(index, /ChatGPT web Chat mode \(`surface = chatgpt_web`, `mode = chat`\)/);
  assert.match(index, /After an explicit override, follow the Work Mode intake guidance below/);
  assert.match(index, /After an override, follow the Work Mode persistence guidance below/);
  assert.match(index, /Do not create outputs before an explicit override/);
  assert.doesNotMatch(index, /follow the Work Mode output guidance/);
  assert.match(dashboard, /After the ChatGPT web Chat-mode stop gate has been explicitly overridden/);
  assert.match(dashboard, /otherwise use portable HTML for a durable dashboard/);
  assert.match(dashboard, /Do not automatically publish to Sites or select the MCP artifact app in this branch/);
  assert.match(report, /ChatGPT web Chat mode after the user explicitly overrides the Work Mode recommendation: use `html`/);
  assert.match(report, /Do not automatically publish to Sites or select `mcp-app` in this branch/);
});

test("Work Mode keeps native structured intake while unifying delivery", () => {
  const index = read("../skills/index/SKILL.md");

  assert.match(index, /After classifying `surface` and `mode`, select the most specific matching runtime branch/);
  assert.match(index, /Work Mode \(`mode = work_mode`\)/);
  assert.match(index, /ChatGPT Desktop outside Work Mode \(`surface = codex_desktop`\)/);
  assert.match(index, /Else: all other or unknown runtimes/);
  assert.ok(index.includes("| Work Mode (`mode = work_mode`) | Use `request_user_input` on ChatGPT Desktop. On every other surface, invoke `$answers-ask-user-input` whenever it is available."));
  assert.ok(index.includes("| ChatGPT Desktop outside Work Mode (`surface = codex_desktop`) | Use `request_user_input` for structured intake when available."));
  assert.match(index, /On ChatGPT Desktop, call `request_user_input` whenever it is available/);
  assert.match(index, /On every other surface or mode, invoke `\$answers-ask-user-input` whenever it is available/);
  assert.match(index, /If the surface-appropriate structured intake action is unavailable but the runtime exposes an equivalent native structured intake action, use that action/);
  assert.match(index, /Do not fall back to conversational choices merely because the runtime is `chatgpt_web`, `work_mode`, or an unknown environment/);
  assert.match(index, /present the same task or fallback choices compactly in normal conversation/);
  assert.doesNotMatch(index, /Use the structured form contract below only when `surface = codex_desktop`/);
  assert.doesNotMatch(index, /including in `web_work_mode`/);
});

test("Work Mode routes explicit semantic-layer setup to persistent skill creation", () => {
  const index = read("../skills/index/SKILL.md");
  const dataContext = read("../skills/create-data-context/SKILL.md");

  assert.match(index, /local creations use that skill's existing `\$CODEX_HOME\/skills\/<area>-semantic-layer` default/);
  assert.match(index, /Use ChatGPT personal Skills persistence when the Skills install surface is available in the run/);
  assert.match(index, /That skill chooses an exposed ChatGPT Skills, local ChatGPT Desktop, or portable package destination/);
  assert.match(index, /For ordinary analytics work using supplied context for the current answer, keep the context current-session only/);
  assert.match(index, /it uses the current runtime's classified `surface` and `mode` values/);
  assert.match(index, /ChatGPT personal Skills, local ChatGPT Desktop, or portable package persistence/);
  assert.match(dataContext, /Use the current runtime's classified `surface` and `mode` values/);
  assert.match(dataContext, /Use structured intake when a supported form action is available/);
  assert.match(dataContext, /Build and validate the same canonical semantic-layer skill package before writing it to any destination/);
  assert.match(dataContext, /Choose one persistence destination by default/);
  assert.match(dataContext, /Destination branch/);
  assert.match(dataContext, /Select this branch when/);
  assert.match(dataContext, /product-backed personal Skills install surface/);
  assert.match(dataContext, /Install the generated skill into the user's personal Skills library/);
  assert.match(dataContext, /include it as a Markdown link in the chat response/);
  assert.match(dataContext, /For ChatGPT personal Skills creations, include the installed skill link in the response/);
  assert.ok(dataContext.includes("`$CODEX_HOME/skills/<area>-semantic-layer`"));
  assert.ok(dataContext.includes("`~/.codex/skills/<area>-semantic-layer`"));
  assert.doesNotMatch(dataContext, /\.agents\/skills/);
  assert.match(dataContext, /For dual ChatGPT web and ChatGPT Desktop availability/);
  assert.match(dataContext, /portable skill package or source plan/);
});

test("semantic-layer create and update results include a weekly refresh automation offer", () => {
  const dataContext = read("../skills/create-data-context/SKILL.md");
  const weeklyPolling = read("../skills/create-data-context/references/semantic-layer/weekly-polling-automation.md");
  const automation = read("../skills/create-data-context/references/automation.md");

  assert.match(dataContext, /After creating or updating a semantic-layer skill/);
  assert.match(dataContext, /always offer weekly refresh/);
  assert.match(dataContext, /do not create it without explicit user approval/);
  assert.match(dataContext, /weekly refresh automation offer or prerequisite blocker/);
  assert.match(dataContext, /iteration guidance/);
  assert.match(dataContext, /refine definitions, add sources, update caveats/);
  assert.match(dataContext, /let the user know they can iterate on the semantic layer/);
  assert.doesNotMatch(dataContext, /validation result/);
  assert.doesNotMatch(dataContext, /validation results/);
  assert.match(weeklyPolling, /Offer weekly polling after semantic-layer creation or refresh/);
  assert.match(automation, /offers exactly one refresh automation/);
});

test("Work Mode on every surface automatically publishes Sites with an HTML backup", () => {
  const index = read("../skills/index/SKILL.md");
  const dashboard = read("../skills/build-dashboard/SKILL.md");
  const report = read("../skills/build-report/SKILL.md");
  const visualize = read("../skills/visualize-data/SKILL.md");
  const nativeInline = read("../skills/visualize-data/references/native-inline-visualizations.md");
  const core = read("../src/analytics-app-core.md");
  const publishSites = read("../skills/publish-artifact-to-sites/SKILL.md");
  const dashboardSpec = read("../skills/build-dashboard/specifications/mcp-artifact-dashboard.md");
  const reportSpec = read("../skills/build-report/specifications/mcp-app-report.md");

  assert.match(index, /For durable reports and dashboards, automatically use Sites when the full create, checkpoint, and deployment lifecycle is callable/);
  assert.match(index, /Use portable HTML automatically when Sites is unavailable, publishing fails, or the user explicitly declines Sites/);
  assert.match(index, /MCP servers and other callable tools remain valid data sources/);
  assert.match(index, /Only after inline delivery is already selected, use native Work Mode rendering/);
  assert.match(index, /treat `charts_widget_v2` as directly surfaced and emit its live `genui` content reference before fallback/);
  assert.match(index, /do not self-declare it unavailable, search for it, or print its payload as bare JSON/);
  assert.match(index, /In Work Mode on any surface, treat MCP apps and generated web apps as unavailable for display/);
  assert.match(dashboard, /do not visibly render the Data Analytics MCP artifact app or a generated web app, regardless of surface/);
  assert.match(dashboard, /automatically use `sites-app` when the full Sites create, checkpoint, and deployment lifecycle is callable/);
  assert.match(dashboard, /Build portable HTML automatically when Sites is unavailable, publishing fails, or the user explicitly declines Sites/);
  assert.match(report, /Work Mode on any surface: automatically use `sites-app`/);
  assert.match(report, /Automatically switch to `html` when Sites is unavailable/);
  assert.match(report, /ChatGPT Desktop outside Work Mode: use `mcp-app` by default/);
  assert.match(visualize, /only after another workflow has already selected inline delivery/);
  assert.match(visualize, /only after the active workflow has already selected inline or chat-visible delivery/);
  assert.match(visualize, /prefer native Work Mode rendering/);
  assert.match(visualize, /native-inline-visualizations\.md/);
  assert.ok(visualize.includes('genui{"charts_widget_v2":{"content":{...}}}'));
  assert.match(visualize, /The inner chart spec alone is not a response/);
  assert.match(visualize, /do not print bare JSON, plain HTML, or a code fence/);
  assert.match(visualize, /treat `charts_widget_v2` as directly surfaced in this runtime/);
  assert.match(visualize, /do not self-declare it unavailable or search for it/);
  assert.match(visualize, /If the Visualize plugin is installed, also consult and follow its current visualization guidance/);
  assert.match(visualize, /do not call `render_chart` or `render_table` for inline delivery/);
  assert.match(visualize, /Use static or Matplotlib charting for this native-render failure fallback/);
  assert.match(visualize, /use a compact table only if no visual renderer can be delivered/);
  assert.match(visualize, /Outside the Work Mode native-render failure fallback, use static Python charting only when/);
  assert.match(visualize, /successful Data Analytics MCP tool result is not delivery confirmation/);
  assert.match(nativeInline, /only after the active workflow has already selected an inline, chat-visible visual/);
  assert.match(nativeInline, /it does not choose inline delivery/);
  assert.match(nativeInline, /`charts_widget_v2`/);
  assert.match(nativeInline, /`app_block`/);
  assert.match(nativeInline, /Never emit a renderer payload as bare JSON/);
  assert.match(nativeInline, /`charts_widget_v2` is the directly surfaced native UI element/);
  assert.match(nativeInline, /do not search for it, self-declare it unavailable/);
  assert.ok(nativeInline.includes('genui{"charts_widget_v2":{"content":{...}}}'));
  assert.ok(nativeInline.includes('genui{"app_block":{"content":"<section>...</section>"}}'));
  assert.match(nativeInline, /do not classify `charts_widget_v2` as unsurfaced before attempting it/);
  assert.match(nativeInline, /ordinary fixed-size `scatter`/);
  assert.match(nativeInline, /true bubble chart is therefore not a `charts_widget_v2` scatter chart/);
  assert.match(nativeInline, /For bubble charts, funnel charts, and any other inline chart family outside that JSON surface, use `app_block` custom interactive HTML/);
  assert.match(nativeInline, /Do not decline the request, ask the user to repeat it, emit an unsupported JSON shape, or fall back to Matplotlib merely because `charts_widget_v2` does not support the family/);
  assert.match(nativeInline, /Mermaid is not a quantitative data-chart renderer/);
  assert.match(nativeInline, /Reproducible static\/Matplotlib chart/);
  assert.match(nativeInline, /prefer a static visual before a compact table/);
  assert.doesNotMatch(index, /native-inline-visualizations/);
  assert.match(core, /Data Analytics MCP widget surface is not available for delivery/);
  assert.match(core, /In any positively identified Work Mode, regardless of surface/);
  assert.match(core, /preserve the delivery mode already selected/);
  assert.match(core, /treat `charts_widget_v2` as directly surfaced/);
  assert.match(core, /emit its live `genui` content reference in the outer shape/);
  assert.ok(core.includes('genui{"charts_widget_v2":{"content":{...}}}'));
  assert.match(core, /do not self-declare it unavailable or search for it/);
  assert.match(core, /Keep `app_block` conditional on the host surfacing it/);
  assert.match(core, /Use image-based\/static charting only after an emitted native reference is rejected or fails to render/);
  assert.match(core, /compact table\/non-MCP output only when no visual renderer can be delivered/);
  assert.match(core, /Do not treat an `ok:true` MCP tool result as proof/);
  assert.match(visualize, /When a durable report or dashboard workflow automatically selects `sites-app`/);
  assert.match(core, /automatically use `sites-app` for durable reports and dashboards when the full Sites publication lifecycle is callable/);
  assert.match(core, /Use self-contained HTML automatically when Sites is unavailable, publishing fails, or the user explicitly declines Sites/);
  assert.match(dashboardSpec, /When `mode = work_mode` is positively identified on any surface/);
  assert.match(dashboardSpec, /select this specification automatically for a durable dashboard when the full Sites create, checkpoint, and deployment lifecycle is callable/);
  assert.match(reportSpec, /When `mode = work_mode` is positively identified on any surface/);
  assert.match(reportSpec, /select this specification automatically for a durable report when the full Sites create, checkpoint, and deployment lifecycle is callable/);
  assert.match(dashboardSpec, /never call `render_artifact`/);
  assert.match(reportSpec, /never call `render_artifact` in Work Mode/);
  assert.match(dashboard, /invoke `\$publish-artifact-to-sites`/);
  assert.match(report, /Invoke `\$publish-artifact-to-sites`/);
  assert.match(publishSites, /In any positively identified Work Mode, a durable report or dashboard request selects Sites automatically when the full Sites building and hosting lifecycle is callable/);
  assert.match(publishSites, /In ChatGPT Desktop outside Work Mode, use this skill only after the user explicitly requests Sites or explicitly accepts/);
  assert.match(publishSites, /Call `export_artifact_package` with the validated payload, the Sites project id in the compatibility field `site_creator_project_id`, and the returned checkout path as `output_dir`/);
  assert.match(publishSites, /Checkpoint the checkout through `\$sites-building`/);
  assert.match(publishSites, /automatically switch to the owning workflow's self-contained HTML mode/);
  assert.doesNotMatch(report, /offer `sites-app` first/);
  assert.doesNotMatch(dashboard, /offer the `Sites app/);
  assert.doesNotMatch(
    [index, dashboard, report, publishSites].join("\n"),
    /\b(?:Plus|Pro|Enterprise|Business|Team)\b/,
  );
});

test("all HTML reports and dashboards use the canonical portable artifact delivery path", () => {
  const agents = read("../AGENTS.md");
  const app = read("../src/analytics-app/App.tsx");
  const chartWidget = read("../src/datascience-chart-widget.js");
  const index = read("../skills/index/SKILL.md");
  const report = read("../skills/build-report/SKILL.md");
  const reportToPdf = read("../skills/build-report/report-to-pdf/SKILL.md");
  const visualize = read("../skills/visualize-data/SKILL.md");
  const dashboardHtml = read("../skills/build-dashboard/specifications/html-dashboard.md");
  const core = read("../src/analytics-app-core.md");

  assert.match(report, /For every selected HTML report path.*canonical `artifact\.json` shape accepted by `validate_artifact`/s);
  assert.match(report, /ChatGPT Desktop explicit HTML.*Google Slides conversion/s);
  assert.match(report, /report:deliver -- --input artifact\.json --output report\.html/);
  assert.match(report, /This one command revalidates the artifact, invokes the only HTML renderer for this workflow/);
  assert.match(report, /when a compatible installed Chromium is available.*chart SVGs.*bounded browser verifier/s);
  assert.match(report, /`stages\.verification: "structural_only"`/);
  assert.match(visualize, /define each visual as a native chart in the canonical `artifact\.json` accepted by `validate_artifact`/);
  assert.match(visualize, /builder-generated semantic representation/);
  assert.match(dashboardHtml, /Author a complete `artifact\.json` in the exact shape accepted by `validate_artifact`/);
  assert.match(dashboardHtml, /shared styling\/tokens, layout, charts, tables, and supported exploration interactions/);
  assert.match(core, /## Portable HTML Packaging/);
  assert.match(core, /exact top-level shape accepted by `validate_artifact`/);
  assert.match(core, /node <PLUGIN_ROOT>\/skills\/build-report\/scripts\/deliver_portable_artifact\.mjs/);
  assert.match(core, /builder also emits a semantic HTML fallback in manifest block order/);
  assert.match(core, /must not require a CDN, remote script, network fetch, MCP host API, local server, runtime sidecar, chart-image sidecar, or sibling data file/);
  assert.match(index, /Every selected HTML report path writes the canonical `artifact\.json` accepted by `validate_artifact`/);
  assert.match(app, /Use \$\{dataAnalyticsPluginMention\(packageInfo\)\} and invoke \$\{workflow\} in portable HTML mode/);
  assert.doesNotMatch(app, /deliver_portable_artifact\.mjs --input artifact\.json --output report\.html/);
  assert.doesNotMatch(app, /Omit the interactive top bar and app-only controls/);
  assert.match(chartWidget, /deliver_portable_artifact\.mjs --input artifact\.json --output report\.html/);
  assert.doesNotMatch(chartWidget, /build_portable_artifact\.mjs --input artifact\.json --output report\.html/);
  assert.match(chartWidget, /Do not hand-author a second HTML shell or chart runtime/);
  assert.doesNotMatch(chartWidget, /Export this .* as a static, portable HTML artifact/);
  assert.match(chartWidget, /Wrap the current chart configuration.*one-chart report artifact\.json/s);
  assert.match(visualize, /non-report, non-dashboard output/);
  assert.match(visualize, /inline-chart HTML.*packaged portable builder/);
  assert.match(core, /optional `package_info`/);
  assert.match(reportToPdf, /deliver_portable_artifact\.mjs --input artifact\.json --output report\.html/);
  assert.doesNotMatch(reportToPdf, /build_portable_artifact\.mjs --input artifact\.json --output report\.html/);
  assert.match(agents, /npm run test:portable-browser/);
  assert.match(agents, /npm run test:portable-parity/);
  assert.match(agents, /npm run test:portable-conversions/);
});

test("ChatGPT Desktop outside Work Mode defaults to MCP while Work Mode uses Sites or HTML", () => {
  const index = read("../skills/index/SKILL.md");
  const report = read("../skills/build-report/SKILL.md");

  assert.match(report, /ChatGPT Desktop outside Work Mode: use `mcp-app` by default/);
  assert.match(report, /Work Mode on any surface: automatically use `sites-app`/);
  assert.match(report, /Automatically switch to `html` when Sites is unavailable/);
  assert.match(report, /On ChatGPT Desktop outside Work Mode, use `html` only when the user explicitly asks/);
  assert.match(report, /an MCP app report was actually attempted and failed/);
  assert.match(index, /Work Mode automatically uses `sites-app` when the full Sites create, checkpoint, and deployment lifecycle is callable/);
  assert.match(index, /ChatGPT Desktop outside Work Mode defaults to `mcp-app`/);
  assert.match(read("../skills/publish-artifact-to-sites/SKILL.md"), /In ChatGPT Desktop outside Work Mode, use this skill only after the user explicitly requests Sites or explicitly accepts/);
});

test("Sites publishing uses production naming", () => {
  assert.equal(existsSync(new URL("../skills/publish-artifact-to-sites/SKILL.md", import.meta.url)), true);
  assert.equal(existsSync(new URL("../skills/publish-artifact-to-sites-preview/SKILL.md", import.meta.url)), false);

  const routingGuidance = [
    read("../skills/index/SKILL.md"),
    read("../skills/build-dashboard/SKILL.md"),
    read("../src/analytics-app-core.md"),
    read("../skills/publish-artifact-to-sites/SKILL.md"),
  ].join("\n");

  assert.doesNotMatch(
    routingGuidance,
    /Sites app \(preview\)|`sites-app` preview|publish-artifact-to-sites-preview|\btest-only\b/i,
  );
});

test("conversion handoffs keep routine verification details out of user-facing responses", () => {
  const createDataContext = read("../skills/create-data-context/SKILL.md");
  const dashboard = read("../skills/build-dashboard/SKILL.md");
  const doc = read("../skills/build-report/report-to-google-doc/SKILL.md");
  const jupyter = read("../skills/jupyter-notebooks/SKILL.md");
  const pdf = read("../skills/build-report/report-to-pdf/SKILL.md");
  const slides = read("../skills/build-report/report-to-google-slides/SKILL.md");

  for (const skill of [dashboard, doc, pdf, slides]) {
    assert.match(skill, /Keep routine check.*support artifacts/);
    assert.match(skill, /Do not list internal checks in the user-facing handoff/);
  }
  assert.match(createDataContext, /Keep routine validation details in support artifacts/);
  assert.match(jupyter, /do not add a separate routine validation section for a clean run/);
  assert.doesNotMatch(slides, /verification performed/);
  assert.doesNotMatch(pdf, /verification performed/);
  assert.doesNotMatch(doc, /validation performed/);
  assert.doesNotMatch(dashboard, /what validation was performed/);
  assert.doesNotMatch(createDataContext, /validation result/);
  assert.doesNotMatch(createDataContext, /validation results/);
  assert.doesNotMatch(jupyter, /Include validation status in the final response/);
});
