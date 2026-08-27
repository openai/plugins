import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { copyFileSync, existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { tmpdir } from "node:os";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { test } from "node:test";

const require = createRequire(import.meta.url);
const server = require("../mcp/server.cjs");

function artifactPayload(
  outputDir,
  {
    generatedAt = "2026-07-06T12:00:00Z",
    siteEditorEmail = undefined,
    versionShape = "initial",
  } = {},
) {
  const changingChart = versionShape === "refreshed"
    ? {
        id: "margin_chart",
        title: "Margin by segment",
        type: "bar",
        dataset: "weekly_revenue",
        sourceId: "weekly_revenue_sql",
        encodings: {
          x: { field: "segment", type: "nominal" },
          y: { field: "revenue_m", type: "quantitative" },
        },
      }
    : {
        id: "legacy_chart",
        title: "Legacy segment view",
        type: "bar",
        dataset: "weekly_revenue",
        sourceId: "weekly_revenue_sql",
        encodings: {
          x: { field: "segment", type: "nominal" },
          y: { field: "revenue_m", type: "quantitative" },
        },
      };
  return {
    surface: "dashboard",
    manifest: {
      version: 1,
      surface: "dashboard",
      title: "Sites export test",
      generatedAt,
      charts: [
        {
          id: "revenue_chart",
          title: "Revenue by segment",
          type: "bar",
          dataset: "weekly_revenue",
          sourceId: "weekly_revenue_sql",
          encodings: {
            x: { field: "segment", type: "nominal" },
            y: { field: "revenue_m", type: "quantitative" },
          },
        },
        changingChart,
      ],
      blocks: [
        { id: "revenue_chart_block", type: "chart", chartId: "revenue_chart" },
        {
          id: versionShape === "refreshed" ? "margin_chart_block" : "legacy_chart_block",
          type: "chart",
          chartId: changingChart.id,
        },
      ],
      sources: [{ id: "weekly_revenue_sql", label: "Revenue SQL", path: "queries/revenue.sql" }],
    },
    snapshot: {
      version: 1,
      generatedAt,
      status: "ready",
      datasets: {
        weekly_revenue: [
          { segment: "Alpha", revenue_m: 12 },
          { segment: "Beta", revenue_m: 18 },
        ],
      },
    },
    sources: [
      {
        id: "weekly_revenue_sql",
        path: "queries/revenue.sql",
        query: { sql: "SELECT segment, revenue_m FROM warehouse.weekly_revenue" },
      },
    ],
    package_info: {
      manifestPath: "/Users/test/private/manifest.json",
      originUrl: "git@github.com:example/private.git",
      root: "/Users/test/private/report",
      snapshotPath: "/Users/test/private/snapshot.json",
      sourceKind: "test-fixture",
    },
    output_dir: outputDir,
    site_creator_project_id: "site-project-test-123",
    ...(siteEditorEmail !== undefined ? { site_editor_email: siteEditorEmail } : {}),
  };
}

async function loadWorker(workerPath) {
  const modulePath = `${workerPath}.mjs`;
  copyFileSync(workerPath, modulePath);
  return import(`${pathToFileURL(modulePath).href}?test=${Date.now()}`);
}

class FakeD1Statement {
  constructor(database, sql, bindings = []) {
    this.database = database;
    this.sql = sql;
    this.bindings = bindings;
  }

  bind(...bindings) {
    return new FakeD1Statement(this.database, this.sql, bindings);
  }

  async first() {
    if (!this.sql.startsWith("SELECT revision")) throw new Error(`Unsupported first query: ${this.sql}`);
    return this.database.row ? { ...this.database.row } : null;
  }

  async run() {
    if (this.sql.startsWith("CREATE TABLE")) return { meta: { changes: 0 } };
    if (this.sql.startsWith("INSERT OR IGNORE")) {
      if (this.database.row) return { meta: { changes: 0 } };
      const [key] = this.bindings;
      this.database.row = {
        key,
        revision: 0,
        overrides_json: "{}",
      };
      return { meta: { changes: 1 } };
    }
    if (this.sql.startsWith("UPDATE data_analytics_presentation_v1")) {
      const [revision, overridesJson, key, expectedRevision] = this.bindings;
      const row = this.database.row;
      if (!row || row.key !== key || row.revision !== expectedRevision) {
        return { meta: { changes: 0 } };
      }
      this.database.row = {
        ...row,
        revision,
        overrides_json: overridesJson,
      };
      return { meta: { changes: 1 } };
    }
    throw new Error(`Unsupported run query: ${this.sql}`);
  }
}

class FakeD1 {
  row = null;

  prepare(sql) {
    return new FakeD1Statement(this, sql);
  }
}

function request(pathname, { body, email, method = "GET" } = {}) {
  return new Request(`https://sites.test${pathname}`, {
    method,
    headers: {
      ...(email ? { "oai-authenticated-user-email": email } : {}),
      ...(body ? { "content-type": "application/json" } : {}),
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
  });
}

function createSitesCheckout(outputDir, projectId = "site-project-test-123") {
  mkdirSync(path.join(outputDir, ".openai"), { recursive: true });
  mkdirSync(path.join(outputDir, "worker"), { recursive: true });
  writeFileSync(
    path.join(outputDir, ".openai", "hosting.json"),
    `${JSON.stringify({ d1: null, r2: null, project_id: projectId }, null, 2)}\n`,
  );
  writeFileSync(path.join(outputDir, "package.json"), '{"name":"sites-worker-checkout","type":"module"}\n');
  writeFileSync(path.join(outputDir, "worker", "index.js"), "export default { fetch() {} };\n");
}

test("Sites export creates a checkpointable Worker project from an empty directory", () => {
  const root = mkdtempSync(path.join(tmpdir(), "data-analytics-sites-empty-export-"));
  const outputDir = path.join(root, "site");
  try {
    const result = server.exportDataScienceArtifactPackage(
      artifactPayload(outputDir, { siteEditorEmail: "owner@example.com" }),
    );
    const packageJson = JSON.parse(readFileSync(path.join(outputDir, "package.json"), "utf8"));

    assert.deepEqual(packageJson.scripts, {
      build: "bash scripts/build.sh",
      validate: "node scripts/validate-artifact.mjs",
    });
    assert.equal(existsSync(path.join(outputDir, "scripts", "build.sh")), true);
    assert.equal(existsSync(path.join(outputDir, "scripts", "validate-artifact.mjs")), true);

    execFileSync("npm", ["run", "build"], { cwd: outputDir, encoding: "utf8" });
    execFileSync("npm", ["run", "validate"], { cwd: outputDir, encoding: "utf8" });

    assert.equal(existsSync(path.join(outputDir, "dist", "server", "index.js")), true);
    assert.equal(existsSync(path.join(outputDir, "dist", ".openai", "hosting.json")), true);
    assert.equal(result.source_entrypoint, path.join(outputDir, "worker", "index.js"));
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test("Sites export seeds creator-only presentation editing before reader access widens", async () => {
  const root = mkdtempSync(path.join(tmpdir(), "data-analytics-sites-export-"));
  const outputDir = path.join(root, "site");
  try {
    createSitesCheckout(outputDir);

    const result = server.exportDataScienceArtifactPackage(
      artifactPayload(outputDir, { siteEditorEmail: "owner@example.com" }),
    );

    assert.equal(result.export_type, "site_creator_package");
    const packageMetadata = JSON.parse(
      readFileSync(path.join(result.output_dir, "dist", "client", "data", "package.json"), "utf8"),
    );
    assert.deepEqual(packageMetadata.controls, {
      delete: true,
      edit: true,
      export: true,
      exportHostedLink: false,
      refresh: true,
      hostedLink: false,
      html: true,
      pdf: true,
      document: true,
      slides: true,
    });
    assert.equal(packageMetadata.hostedEditing, "presentation");
    assert.equal(packageMetadata.handoffPluginName, "Data Analytics");
    for (const localField of ["manifestPath", "originUrl", "root", "snapshotPath", "sourceKind"]) {
      assert.equal(packageMetadata[localField], undefined);
    }
    assert.equal(result.presentation_editing, true);
    assert.equal(
      readFileSync(result.database_schema_path, "utf8"),
      'export const presentationSchemaSql = "CREATE TABLE IF NOT EXISTS data_analytics_presentation_v1 (key TEXT PRIMARY KEY, revision INTEGER NOT NULL, overrides_json TEXT NOT NULL)";\n',
    );

    const hostedHtml = readFileSync(path.join(result.output_dir, "dist", "client", "index.html"), "utf8");
    assert.match(
      hostedHtml,
      /\.dashboard-content-grid \.viz-card \.chart-body-measure \{[^}]*flex: 0 0 auto;[^}]*height: auto;[^}]*max-height: none;[^}]*min-height: 0;/,
      "hosted dashboard chart rows should contain their rendered chart bodies",
    );
    const bootstrap = hostedHtml.match(/window\.__DATASCIENCE_ARTIFACT_HOSTING__=(\{.*?\});/);
    assert.ok(bootstrap, "hosted HTML should declare fail-closed Sites metadata");
    assert.deepEqual(JSON.parse(bootstrap[1]), {
      editing: "presentation",
      mode: "site_creator",
      readOnly: true,
      controls: packageMetadata.controls,
    });

    const expectedHosting = { d1: "DB", r2: null, project_id: "site-project-test-123" };
    assert.deepEqual(JSON.parse(readFileSync(result.hosting_config_path, "utf8")), expectedHosting);
    assert.deepEqual(JSON.parse(readFileSync(result.packaged_hosting_config_path, "utf8")), expectedHosting);

    const archiveEntries = execFileSync("tar", ["-tzf", result.archive_path], { encoding: "utf8" });
    assert.match(archiveEntries, /^dist\/server\/index\.js$/m);
    assert.match(archiveEntries, /^dist\/\.openai\/hosting\.json$/m);
    assert.equal(readFileSync(result.source_entrypoint, "utf8"), readFileSync(result.worker_entrypoint, "utf8"));
    const workerSource = readFileSync(result.source_entrypoint, "utf8");
    assert.match(workerSource, /const PRESENTATION_EDITING_ENABLED = true;/);
    assert.doesNotMatch(workerSource, /owner@example\.com/);
    assert.doesNotMatch(workerSource, /\/Users\/test\/private|private\.git/);
    assert.equal(
      readFileSync(path.join(outputDir, "package.json"), "utf8"),
      '{"name":"sites-worker-checkout","type":"module"}\n',
    );

    rmSync(path.join(outputDir, "dist"), { recursive: true, force: true });
    mkdirSync(path.dirname(result.worker_entrypoint), { recursive: true });
    mkdirSync(path.dirname(result.packaged_hosting_config_path), { recursive: true });
    copyFileSync(result.source_entrypoint, result.worker_entrypoint);
    copyFileSync(result.hosting_config_path, result.packaged_hosting_config_path);

    const worker = await loadWorker(result.worker_entrypoint);
    for (const route of [
      "/",
      "/api/manifest",
      "/api/snapshot",
      "/api/package",
      "/api/inline-chart-widget",
    ]) {
      const response = await worker.default.fetch(new Request(`https://sites.test${route}`));
      assert.equal(response.status, 200, route);
    }
    const database = new FakeD1();
    const anonymousPresentation = await worker.default.fetch(request("/api/presentation"), { DB: database });
    assert.equal(anonymousPresentation.status, 200);
    assert.deepEqual(await anonymousPresentation.json(), {
      artifactId: packageMetadata.artifactId,
      revision: 0,
      overrides: {},
      canEdit: false,
    });

    const viewerFirstPresentation = await worker.default.fetch(
      request("/api/presentation", { email: "viewer@example.com" }),
      { DB: database },
    );
    assert.equal(viewerFirstPresentation.status, 200);
    assert.equal((await viewerFirstPresentation.json()).canEdit, false);
    const viewerFirstWrite = await worker.default.fetch(
      request("/api/presentation", {
        body: { artifactId: packageMetadata.artifactId, revision: 0, overrides: {} },
        email: "viewer@example.com",
        method: "PUT",
      }),
      { DB: database },
    );
    assert.equal(viewerFirstWrite.status, 403);

    const ownerPresentation = await worker.default.fetch(
      request("/api/presentation", { email: "owner@example.com" }),
      { DB: database },
    );
    assert.equal(ownerPresentation.status, 200);
    assert.equal((await ownerPresentation.json()).canEdit, true);

    const chartSpecOverrides = {
      revenue_chart: {
        type: "horizontalBar",
        xField: "segment",
        series: [
          {
            field: "revenue_m",
            label: "Revenue",
            color: "blue",
            lineStyle: "dashed",
            semanticRole: "actual",
          },
        ],
        encodings: { size: { field: "revenue_m" } },
        settings: { orientation: "horizontal", groupMode: "grouped" },
      },
      legacy_chart: {
        type: "bar",
        xField: "segment",
        series: [{ field: "revenue_m", label: "Legacy revenue" }],
      },
    };
    const overrides = {
      pageTitle: "Edited revenue review",
      chartSpecOverrides,
      chartTextOverrides: {
        revenue_chart: { headerMarkdown: "## Edited chart title" },
        legacy_chart: { headerMarkdown: "## Edited legacy title" },
      },
      dashboardLayout: [
        { id: "legacy_chart_block", layout: "half" },
        { id: "revenue_chart_block", layout: "full" },
      ],
      deletedReportBlockIds: ["legacy_chart_block", "revenue_chart_block"],
    };
    const savedPresentation = await worker.default.fetch(
      request("/api/presentation", {
        body: { artifactId: packageMetadata.artifactId, revision: 0, overrides },
        email: "owner@example.com",
        method: "PUT",
      }),
      { DB: database },
    );
    assert.equal(savedPresentation.status, 200);
    assert.deepEqual(await savedPresentation.json(), {
      artifactId: packageMetadata.artifactId,
      revision: 1,
      overrides,
      canEdit: true,
    });

    const ownerReadPresentation = await worker.default.fetch(
      request("/api/presentation", { email: "owner@example.com" }),
      { DB: database },
    );
    assert.deepEqual((await ownerReadPresentation.json()).overrides.chartSpecOverrides, chartSpecOverrides);

    const invalidChartSpecWrite = await worker.default.fetch(
      request("/api/presentation", {
        body: {
          artifactId: packageMetadata.artifactId,
          revision: 1,
          overrides: { chartSpecOverrides: { revenue_chart: { xField: "unknown_field" } } },
        },
        email: "owner@example.com",
        method: "PUT",
      }),
      { DB: database },
    );
    assert.equal(invalidChartSpecWrite.status, 400);

    const viewerPresentation = await worker.default.fetch(
      request("/api/presentation", { email: "viewer@example.com" }),
      { DB: database },
    );
    const viewerPayload = await viewerPresentation.json();
    assert.equal(viewerPayload.canEdit, false);
    assert.deepEqual(viewerPayload.overrides, overrides);

    const viewerWrite = await worker.default.fetch(
      request("/api/presentation", {
        body: { artifactId: packageMetadata.artifactId, revision: 1, overrides: {} },
        email: "viewer@example.com",
        method: "PUT",
      }),
      { DB: database },
    );
    assert.equal(viewerWrite.status, 403);

    const staleWrite = await worker.default.fetch(
      request("/api/presentation", {
        body: { artifactId: packageMetadata.artifactId, revision: 0, overrides },
        email: "owner@example.com",
        method: "PUT",
      }),
      { DB: database },
    );
    assert.equal(staleWrite.status, 409);

    const invalidDeletedBlockWrite = await worker.default.fetch(
      request("/api/presentation", {
        body: {
          artifactId: packageMetadata.artifactId,
          revision: 1,
          overrides: { deletedReportBlockIds: ["unknown_block"] },
        },
        email: "owner@example.com",
        method: "PUT",
      }),
      { DB: database },
    );
    assert.equal(invalidDeletedBlockWrite.status, 400);

    const unavailablePresentation = await worker.default.fetch(
      request("/api/presentation", { email: "owner@example.com" }),
    );
    assert.deepEqual(await unavailablePresentation.json(), {
      artifactId: packageMetadata.artifactId,
      revision: 0,
      overrides: {},
      canEdit: false,
    });

    const refreshedOutputDir = outputDir;
    const refreshedResult = server.exportDataScienceArtifactPackage(
      artifactPayload(refreshedOutputDir, {
        generatedAt: "2026-07-07T12:00:00Z",
        siteEditorEmail: undefined,
        versionShape: "refreshed",
      }),
    );
    const refreshedPackage = JSON.parse(
      readFileSync(path.join(refreshedResult.output_dir, "dist", "client", "data", "package.json"), "utf8"),
    );
    assert.notEqual(refreshedPackage.artifactId, packageMetadata.artifactId);
    const refreshedWorker = await loadWorker(refreshedResult.worker_entrypoint);
    const refreshedPresentation = await refreshedWorker.default.fetch(
      request("/api/presentation", { email: "owner@example.com" }),
      { DB: database },
    );
    const refreshedPayload = await refreshedPresentation.json();
    assert.equal(refreshedPayload.artifactId, refreshedPackage.artifactId);
    assert.equal(refreshedPayload.revision, 1);
    assert.deepEqual(refreshedPayload.overrides, {
      pageTitle: "Edited revenue review",
      chartSpecOverrides: {
        revenue_chart: chartSpecOverrides.revenue_chart,
      },
      chartTextOverrides: {
        revenue_chart: { headerMarkdown: "## Edited chart title" },
      },
      dashboardLayout: [{ id: "revenue_chart_block", layout: "full" }],
      deletedReportBlockIds: ["revenue_chart_block"],
    });
    assert.equal(refreshedPayload.overrides.chartSpecOverrides.legacy_chart, undefined);
    assert.equal(refreshedPayload.overrides.chartTextOverrides.margin_chart, undefined);

    const readOnlyOutputDir = path.join(root, "read-only-site");
    const readOnlyResult = server.exportDataScienceArtifactPackage(
      artifactPayload(readOnlyOutputDir, { siteEditorEmail: null }),
    );
    const readOnlyPackage = JSON.parse(
      readFileSync(path.join(readOnlyResult.output_dir, "dist", "client", "data", "package.json"), "utf8"),
    );
    assert.equal(readOnlyResult.presentation_editing, false);
    assert.equal(readOnlyPackage.hostedEditing, null);
    for (const control of ["delete", "edit", "export", "refresh", "html", "pdf", "document", "slides"]) {
      assert.equal(readOnlyPackage.controls[control], false);
    }
    assert.equal(JSON.parse(readFileSync(readOnlyResult.hosting_config_path, "utf8")).d1, null);
    assert.equal(readOnlyResult.database_schema_path, null);
    assert.equal(existsSync(path.join(readOnlyOutputDir, "db", "schema.ts")), false);

    const incompatibleOutputDir = path.join(root, "incompatible-site");
    mkdirSync(path.join(incompatibleOutputDir, ".openai"), { recursive: true });
    mkdirSync(path.join(incompatibleOutputDir, "worker"), { recursive: true });
    writeFileSync(
      path.join(incompatibleOutputDir, ".openai", "hosting.json"),
      `${JSON.stringify({ d1: "DATABASE", r2: null, project_id: "site-project-test-123" }, null, 2)}\n`,
    );
    writeFileSync(path.join(incompatibleOutputDir, "worker", "index.js"), "export default { fetch() {} };\n");
    assert.throws(
      () => server.exportDataScienceArtifactPackage(
        artifactPayload(incompatibleOutputDir, { siteEditorEmail: "owner@example.com" }),
      ),
      /requires the D1 binding name "DB"/,
    );

    const sourceResponse = await worker.default.fetch(
      new Request("https://sites.test/api/source-file?id=weekly_revenue_sql"),
    );
    assert.equal(sourceResponse.status, 200);
    assert.equal(await sourceResponse.text(), "SELECT segment, revenue_m FROM warehouse.weekly_revenue");
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test("republishing after reader access widens preserves the seeded creator", async () => {
  const root = mkdtempSync(path.join(tmpdir(), "data-analytics-sites-shared-republish-"));
  try {
    const outputDir = path.join(root, "site");
    createSitesCheckout(outputDir);
    const firstSharedOutputDir = path.join(root, "first-shared-without-seed");
    createSitesCheckout(firstSharedOutputDir);
    const firstSharedWithoutSeed = server.exportDataScienceArtifactPackage(
      artifactPayload(firstSharedOutputDir, { siteEditorEmail: undefined }),
    );
    assert.equal(firstSharedWithoutSeed.presentation_editing, false);

    const ownerOnlyExport = server.exportDataScienceArtifactPackage(
      artifactPayload(outputDir, { siteEditorEmail: "owner@example.com" }),
    );
    assert.equal(ownerOnlyExport.presentation_editing, true);

    const sharedRepublish = server.exportDataScienceArtifactPackage(
      artifactPayload(outputDir, {
        generatedAt: "2026-07-07T12:00:00Z",
        siteEditorEmail: undefined,
      }),
    );
    assert.equal(sharedRepublish.presentation_editing, true);
    const worker = await loadWorker(sharedRepublish.worker_entrypoint);
    const database = new FakeD1();
    const creator = await worker.default.fetch(
      request("/api/presentation", { email: "owner@example.com" }),
      { DB: database },
    );
    assert.equal((await creator.json()).canEdit, true);
    const viewer = await worker.default.fetch(
      request("/api/presentation", { email: "viewer@example.com" }),
      { DB: database },
    );
    assert.equal((await viewer.json()).canEdit, false);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test("explicit null is the only sticky disable and email remains a compatibility fallback", async () => {
  const root = mkdtempSync(path.join(tmpdir(), "data-analytics-sites-editor-state-"));
  try {
    const disabledOutputDir = path.join(root, "disabled");
    createSitesCheckout(disabledOutputDir);
    const disabled = server.exportDataScienceArtifactPackage(
      artifactPayload(disabledOutputDir, { siteEditorEmail: null }),
    );
    assert.equal(disabled.presentation_editing, false);
    assert.match(readFileSync(disabled.source_entrypoint, "utf8"), /const PRESENTATION_EDITING_ENABLED = false;/);

    const preservedDisabled = server.exportDataScienceArtifactPackage(
      artifactPayload(disabledOutputDir, { generatedAt: "2026-07-07T12:00:00Z" }),
    );
    assert.equal(preservedDisabled.presentation_editing, false);
    const disabledWorker = await loadWorker(preservedDisabled.worker_entrypoint);
    const disabledOwner = await disabledWorker.default.fetch(
      request("/api/presentation", { email: "owner@example.com" }),
      { DB: new FakeD1() },
    );
    assert.equal((await disabledOwner.json()).canEdit, false);

    const legacyOutputDir = path.join(root, "legacy-email");
    createSitesCheckout(legacyOutputDir);
    const legacy = server.exportDataScienceArtifactPackage(
      artifactPayload(legacyOutputDir, { siteEditorEmail: "owner@example.com" }),
    );
    const legacyWorker = await loadWorker(legacy.worker_entrypoint);
    const legacyOwner = await legacyWorker.default.fetch(
      request("/api/presentation", { email: "owner@example.com" }),
      { DB: new FakeD1() },
    );
    assert.equal((await legacyOwner.json()).canEdit, true);
    const legacyViewer = await legacyWorker.default.fetch(
      request("/api/presentation", { email: "viewer@example.com" }),
      { DB: new FakeD1() },
    );
    assert.equal((await legacyViewer.json()).canEdit, false);
    assert.throws(
      () => server.exportDataScienceArtifactPackage(
        artifactPayload(path.join(root, "empty-email"), { siteEditorEmail: "" }),
      ),
      /valid non-empty email address/,
    );
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});
