import assert from "node:assert/strict";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { execFile } from "node:child_process";
import test from "node:test";
import { promisify } from "node:util";

import { analyzePath, explainBudget } from "../src/core/analyze.js";
import { initializeBenchmark, runBenchmark } from "../src/core/benchmark.js";
import { provisionBenchmarkWorkspace } from "../src/core/benchmark-workspace.js";
import { parseCodexJsonStream, summarizeCodexEvents } from "../src/core/benchmark-events.js";
import { compareResults } from "../src/core/compare.js";
import { buildWorkflowGuide } from "../src/core/workflow-guide.js";
import { parseFrontmatter } from "../src/lib/frontmatter.js";
import { formatCommandPath } from "../src/lib/files.js";
import { renderPayload } from "../src/renderers/index.js";

const execFileAsync = promisify(execFile);
const repoRoot = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const fixturesRoot = path.join(repoRoot, "fixtures");
const cliPath = path.join(repoRoot, "scripts", "plugin-eval.js");
const nodeBin = process.execPath;

async function makeTempDir(prefix) {
  return fs.mkdtemp(path.join(os.tmpdir(), `${prefix}-`));
}

async function writeSkillFixture(rootPath, { description, bodyLines }) {
  await fs.mkdir(rootPath, { recursive: true });
  const body = Array.from({ length: bodyLines }, (_, index) => `Line ${index + 1}`).join("\n");
  await fs.writeFile(
    path.join(rootPath, "SKILL.md"),
    `---\nname: temp-skill\ndescription: ${description}\n---\n\n# Temp Skill\n\n${body}\n`,
    "utf8",
  );
}

async function writeBlockScalarSkillFixture(rootPath, { style = ">", descriptionLines, bodyLines = 3 }) {
  await fs.mkdir(rootPath, { recursive: true });
  const description = descriptionLines.map((line) => `  ${line}`).join("\n");
  const body = Array.from({ length: bodyLines }, (_, index) => `Line ${index + 1}`).join("\n");
  await fs.writeFile(
    path.join(rootPath, "SKILL.md"),
    `---\nname: temp-skill\ndescription: ${style}\n${description}\n---\n\n# Temp Skill\n\n${body}\n`,
    "utf8",
  );
}

async function copyDirectory(source, destination) {
  await fs.cp(source, destination, { recursive: true });
}

async function createFakeCodexExecutable(rootPath) {
  const binDir = path.join(rootPath, "bin");
  const executablePath = path.join(binDir, "codex");
  await fs.mkdir(binDir, { recursive: true });
  await fs.writeFile(
    executablePath,
    `#!/bin/sh
if [ "$1" = "--version" ]; then
  echo "codex-cli fake-test"
  exit 0
fi

if [ "$1" = "exec" ]; then
  final=""
  workspace=""
  while [ "$#" -gt 0 ]; do
    if [ "$1" = "--output-last-message" ]; then
      shift
      final="$1"
    elif [ "$1" = "--cd" ]; then
      shift
      workspace="$1"
    fi
    shift
  done

  mkdir -p "$(dirname "$final")"
  printf "Implemented benchmark fixture.\\n" > "$final"
  printf 'export const generated = 1;\\n' > "$workspace/generated.ts"
  printf 'import { generated } from "./generated";\\nexport default generated;\\n' > "$workspace/generated.test.ts"
  printf '{"type":"thread.started","thread_id":"thread-test"}\\n'
  printf '{"type":"tool.called","tool_name":"functions.exec_command"}\\n'
  printf '{"type":"shell.command","command":"npm test"}\\n'
  printf '{"type":"turn.completed","usage":{"input_tokens":120,"output_tokens":45,"total_tokens":165}}\\n'
  exit 0
fi

echo "unsupported invocation" >&2
exit 1
`,
    "utf8",
  );
  await fs.chmod(executablePath, 0o755);
  return executablePath;
}

test("analyze minimal skill and render markdown/html", async () => {
  const skillPath = path.join(fixturesRoot, "minimal-skill");
  const result = await analyzePath(skillPath);

  assert.equal(result.target.kind, "skill");
  assert.equal(result.budgets.method, "estimated-static");
  assert.ok(result.summary.score > 0);
  assert.ok(result.metrics.some((metric) => metric.id === "trigger_cost_tokens"));
  assert.ok(Array.isArray(result.summary.whyBullets));
  assert.ok(Array.isArray(result.summary.fixFirst));
  assert.ok(result.nextAction);

  const markdown = renderPayload(result, "markdown");
  const html = renderPayload(result, "html");

  assert.match(markdown, /Plugin Eval Report: minimal-skill/);
  assert.match(markdown, /At a Glance/);
  assert.match(markdown, /Why It Matters/);
  assert.match(markdown, /Fix First/);
  assert.match(markdown, /Recommended Next Step/);
  assert.match(markdown, /<details>/);
  assert.match(html, /<!doctype html>/i);
  assert.match(html, /Risk Assessment/);
  assert.match(html, /Use From Codex Chat/);
  assert.match(html, /Quick local entrypoint/);
});

test("flags oversized descriptions and bloated SKILL.md files", async () => {
  const tempDir = await makeTempDir("plugin-eval-skill");
  await writeSkillFixture(tempDir, {
    description: `Verbose description ${"x".repeat(1300)}`,
    bodyLines: 650,
  });

  const result = await analyzePath(tempDir);
  const ids = new Set(result.checks.map((check) => check.id));

  assert.ok(ids.has("description-too-long"));
  assert.ok(ids.has("skill-large") || ids.has("skill-too-large"));
  assert.notEqual(result.budgets.trigger_cost_tokens.band, "good");
});

test("parses folded and literal YAML block scalars in frontmatter", async () => {
  const folded = parseFrontmatter(`---\nname: temp-skill\ndescription: >\n  Use when the task needs\n  a folded block scalar.\n---\n`);
  const literal = parseFrontmatter(`---\nname: temp-skill\ndescription: |\n  First line.\n  Second line.\n---\n`);

  assert.deepEqual(folded.errors, []);
  assert.equal(folded.data.description, "Use when the task needs a folded block scalar.");

  assert.deepEqual(literal.errors, []);
  assert.equal(literal.data.description, "First line.\nSecond line.");
});

test("analyze accepts skills with block-scalar descriptions", async () => {
  const tempDir = await makeTempDir("plugin-eval-block-scalar");
  await writeBlockScalarSkillFixture(tempDir, {
    style: ">",
    descriptionLines: [
      "Use when the task needs",
      "a folded block scalar description.",
    ],
  });

  const result = await analyzePath(tempDir);
  const ids = new Set(result.checks.map((check) => check.id));

  assert.ok(!ids.has("frontmatter-invalid"));
  assert.ok(!ids.has("name-missing"));
  assert.ok(!ids.has("description-missing"));
  assert.ok(result.summary.score > 0);
});

test("finds broken plugin manifests, missing paths, and prompt issues", async () => {
  const tempDir = await makeTempDir("plugin-eval-plugin");
  await fs.mkdir(path.join(tempDir, ".codex-plugin"), { recursive: true });
  await fs.writeFile(
    path.join(tempDir, ".codex-plugin", "plugin.json"),
    JSON.stringify(
      {
        name: "bad-plugin",
        version: "0.1.0",
        description: "Broken plugin for testing.",
        author: {
          name: "Plugin Eval",
          email: "support@example.com",
          url: "https://example.com/",
        },
        homepage: "https://example.com/",
        repository: "https://example.com/repo",
        license: "MIT",
        keywords: ["fixture"],
        skills: "./missing-skills/",
        interface: {
          displayName: "Bad Plugin",
          shortDescription: "Broken fixture",
          longDescription: "Broken fixture for plugin-eval tests.",
          developerName: "Plugin Eval",
          category: "Coding",
          capabilities: ["Interactive", "Write"],
          websiteURL: "https://example.com/",
          privacyPolicyURL: "https://example.com/privacy",
          termsOfServiceURL: "https://example.com/terms",
          defaultPrompt: [
            "Prompt one that is fine.",
            "Prompt two that is also fine.",
            "Prompt three that is also fine.",
            "Prompt four is ignored and should be flagged because there are too many starter prompts in this broken fixture, and this sentence is intentionally extended well past the interface length budget so the evaluator can deterministically flag it as too long."
          ],
          brandColor: "teal",
          composerIcon: "./assets/missing.svg",
          logo: "./assets/missing.svg",
          screenshots: []
        }
      },
      null,
      2,
    ),
    "utf8",
  );

  const result = await analyzePath(tempDir);
  const ids = new Set(result.checks.map((check) => check.id));

  assert.ok(ids.has("skills-path-missing"));
  assert.ok(ids.has("default-prompt-too-many"));
  assert.ok(ids.has("default-prompt-too-long"));
  assert.ok(ids.has("brand-color-invalid"));
  assert.ok(ids.has("plugin-skills-missing"));
});

test("collects deterministic TypeScript and Python metrics", async () => {
  const samplePath = path.join(fixturesRoot, "ts-python-sample");
  const result = await analyzePath(samplePath);

  const metric = (id) => result.metrics.find((item) => item.id === id)?.value;

  assert.equal(metric("ts_file_count"), 2);
  assert.equal(metric("py_file_count"), 2);
  assert.equal(metric("ts_test_file_count"), 1);
  assert.equal(metric("py_test_file_count"), 1);
  assert.ok(metric("ts_max_cyclomatic_complexity") >= 4);
  assert.ok(metric("py_max_cyclomatic_complexity") >= 4);
});

test("ingests lcov, coverage.xml, and coverage-final.json artifacts", async () => {
  const samplePath = path.join(fixturesRoot, "coverage-samples");
  const result = await analyzePath(samplePath);
  const coveragePercent = result.metrics.find((metric) => metric.id === "coverage_percent")?.value;

  assert.equal(coveragePercent, 82);
  assert.equal(result.metrics.find((metric) => metric.id === "coverage_artifact_count")?.value, 3);
});

test("merges custom metric pack output without changing the core summary", async () => {
  const skillPath = path.join(fixturesRoot, "minimal-skill");
  const result = await analyzePath(skillPath, {
    metricPackManifests: [path.join(fixturesRoot, "metric-pack", "manifest.json")],
  });

  assert.equal(result.extensions.length, 1);
  assert.equal(result.extensions[0].metrics[0].id, "custom-pack-score");
  assert.ok(result.summary.score > 0);
});

test("ingests observed usage files and compares estimates against real sessions", async () => {
  const skillPath = path.join(fixturesRoot, "minimal-skill");
  const usagePath = path.join(fixturesRoot, "observed-usage", "responses.jsonl");
  const result = await analyzePath(skillPath, {
    observedUsagePaths: [usagePath],
  });

  assert.equal(result.observedUsage.sampleCount, 3);
  assert.equal(result.metrics.find((metric) => metric.id === "observed_usage_sample_count")?.value, 3);
  assert.ok(result.metrics.some((metric) => metric.id === "estimate_vs_observed_input_ratio"));
  assert.ok(result.measurementPlan.toolsets.length >= 5);
});

test("init-benchmark writes a beginner-friendly starter config", async () => {
  const sourcePath = path.join(fixturesRoot, "minimal-skill");
  const tempDir = await makeTempDir("plugin-eval-benchmark-init");
  const skillPath = path.join(tempDir, "minimal-skill");
  await copyDirectory(sourcePath, skillPath);

  const payload = await initializeBenchmark(skillPath);
  const config = JSON.parse(await fs.readFile(path.join(skillPath, ".plugin-eval", "benchmark.json"), "utf8"));

  assert.equal(payload.kind, "benchmark-template-init");
  assert.equal(config.kind, "plugin-eval-benchmark");
  assert.equal(config.schemaVersion, 2);
  assert.equal(config.runner.type, "codex-cli");
  assert.equal(config.workspace.setupMode, "copy");
  assert.equal(config.scenarios.length, 3);
  assert.ok(Array.isArray(config.setupQuestions));
  assert.ok(config.setupQuestions.length >= 3);
  assert.match(config.notes[0], /workspace\.sourcePath/i);
  assert.ok(Array.isArray(payload.setupQuestions));
  assert.ok(payload.setupQuestions.some((item) => /must-pass/i.test(item)));
  assert.ok(payload.workflowGuide);
});

test("benchmark rejects the removed dry-run mode", async () => {
  const sourcePath = path.join(fixturesRoot, "minimal-skill");
  const tempDir = await makeTempDir("plugin-eval-benchmark-dry-run");
  const skillPath = path.join(tempDir, "minimal-skill");
  await copyDirectory(sourcePath, skillPath);

  await initializeBenchmark(skillPath);
  await assert.rejects(
    () =>
      runBenchmark(skillPath, {
        configPath: path.join(skillPath, ".plugin-eval", "benchmark.json"),
        dryRun: true,
      }),
    /no longer supports --dry-run/i,
  );
});

test("parses codex json event streams and extracts usage plus shell activity", async () => {
  const stream = [
    JSON.stringify({ type: "thread.started", thread_id: "thread-123" }),
    JSON.stringify({ type: "tool.called", tool_name: "functions.exec_command" }),
    JSON.stringify({ type: "shell.command", command: "npm test" }),
    "warning text that should be ignored",
    JSON.stringify({ type: "turn.completed", usage: { input_tokens: 101, output_tokens: 44, total_tokens: 145 } }),
  ].join("\n");

  const parsed = parseCodexJsonStream(stream);
  const summary = summarizeCodexEvents(parsed.events);

  assert.equal(parsed.events.length, 4);
  assert.equal(parsed.ignoredLines.length, 1);
  assert.equal(summary.threadId, "thread-123");
  assert.equal(summary.toolCallCount, 1);
  assert.equal(summary.shellCommandCount, 1);
  assert.equal(summary.failedShellCommandCount, 0);
  assert.equal(summary.usage.input_tokens, 101);
  assert.equal(summary.finalStatus, "completed");
});

test("formats command paths with home shorthand for user-facing commands", () => {
  const formatted = formatCommandPath(path.join(os.homedir(), ".codex", "skills", "game-dev"), {
    cwd: repoRoot,
  });

  assert.equal(formatted, "~/.codex/skills/game-dev");
});

test("workflow guide next action uses the first actionable local command", async () => {
  const sourcePath = path.join(fixturesRoot, "minimal-skill");
  const tempDir = await makeTempDir("plugin-eval-workflow-guide");
  const skillPath = path.join(tempDir, "minimal-skill");
  await copyDirectory(sourcePath, skillPath);

  const guide = await buildWorkflowGuide(skillPath, {
    request: "Measure the real token usage of this skill.",
  });

  assert.equal(guide.nextAction.command, `plugin-eval init-benchmark ${formatCommandPath(skillPath)}`);
});

test("benchmark run writes usage logs and generated-code analysis from a codex-cli run", async () => {
  const sourcePath = path.join(fixturesRoot, "minimal-skill");
  const tempDir = await makeTempDir("plugin-eval-benchmark-live");
  const skillPath = path.join(tempDir, "minimal-skill");
  await copyDirectory(sourcePath, skillPath);

  await initializeBenchmark(skillPath);
  const payload = await runBenchmark(skillPath, {
    configPath: path.join(skillPath, ".plugin-eval", "benchmark.json"),
    processRunner: async ({ kind, args }) => {
      if (kind === "codex-version") {
        return {
          code: 0,
          signal: null,
          durationMs: 1,
          stdoutText: "codex-cli fake-test\n",
          stderrText: "",
        };
      }

      if (kind === "codex") {
        const finalMessagePath = args[args.indexOf("--output-last-message") + 1];
        const workspacePath = args[args.indexOf("--cd") + 1];
        await fs.writeFile(finalMessagePath, "Benchmark completed.\n", "utf8");
        await fs.writeFile(path.join(workspacePath, "generated.ts"), "export const value = 1;\n", "utf8");
        await fs.writeFile(path.join(workspacePath, "generated.test.ts"), "import { value } from './generated';\nconsole.log(value);\n", "utf8");
        return {
          code: 0,
          signal: null,
          durationMs: 10,
          stdoutText: [
            JSON.stringify({ type: "thread.started", thread_id: "thread-test" }),
            JSON.stringify({ type: "tool.called", tool_name: "functions.exec_command" }),
            JSON.stringify({ type: "shell.command", command: "npm test" }),
            JSON.stringify({ type: "turn.completed", usage: { input_tokens: 150, output_tokens: 70, total_tokens: 220 } }),
          ].join("\n"),
          stderrText: "",
        };
      }

      return {
        code: 0,
        signal: null,
        durationMs: 5,
        stdoutText: "",
        stderrText: "",
      };
    },
  });

  assert.equal(payload.mode, "codex-cli");
  assert.equal(payload.summary.sampleCount, 3);
  assert.equal(payload.summary.generatedFileCount, 6);
  assert.equal(payload.summary.generatedTestFileCount, 3);
  assert.equal(payload.scenarios[0].generatedCode.metrics.find((metric) => metric.id === "ts_file_count")?.value, 2);

  const result = await analyzePath(skillPath, {
    observedUsagePaths: [payload.usageLogPath],
  });
  assert.equal(result.observedUsage.sampleCount, 3);
});

test("benchmark run uses config-based approval policy syntax for codex exec", async () => {
  const sourcePath = path.join(fixturesRoot, "minimal-skill");
  const tempDir = await makeTempDir("plugin-eval-benchmark-args");
  const skillPath = path.join(tempDir, "minimal-skill");
  await copyDirectory(sourcePath, skillPath);

  await initializeBenchmark(skillPath);
  const seenArgs = [];

  await runBenchmark(skillPath, {
    configPath: path.join(skillPath, ".plugin-eval", "benchmark.json"),
    processRunner: async ({ kind, args }) => {
      if (kind === "codex-version") {
        return {
          code: 0,
          signal: null,
          durationMs: 1,
          stdoutText: "codex-cli fake-test\n",
          stderrText: "",
        };
      }

      if (kind === "codex") {
        seenArgs.push(args);
        const finalMessagePath = args[args.indexOf("--output-last-message") + 1];
        const workspacePath = args[args.indexOf("--cd") + 1];
        await fs.writeFile(finalMessagePath, "Benchmark completed.\n", "utf8");
        await fs.writeFile(path.join(workspacePath, "generated.ts"), "export const value = 1;\n", "utf8");
        return {
          code: 0,
          signal: null,
          durationMs: 10,
          stdoutText: [
            JSON.stringify({ type: "thread.started", thread_id: "thread-test" }),
            JSON.stringify({ type: "turn.completed", usage: { input_tokens: 150, output_tokens: 70, total_tokens: 220 } }),
          ].join("\n"),
          stderrText: "",
        };
      }

      return {
        code: 0,
        signal: null,
        durationMs: 5,
        stdoutText: "",
        stderrText: "",
      };
    },
  });

  assert.equal(seenArgs.length, 3);
  assert.ok(seenArgs.every((args) => !args.includes("-a")));
  assert.ok(seenArgs.every((args) => args.includes("-c")));
  assert.ok(seenArgs.every((args) => args.includes('approval_policy="never"')));
});

test("provisionBenchmarkWorkspace seeds auth and config into the isolated codex home", async () => {
  const sourcePath = path.join(fixturesRoot, "minimal-skill");
  const tempDir = await makeTempDir("plugin-eval-benchmark-home");
  const skillPath = path.join(tempDir, "minimal-skill");
  const codexHomeSource = path.join(tempDir, "codex-home-source");
  await copyDirectory(sourcePath, skillPath);
  await fs.mkdir(codexHomeSource, { recursive: true });
  await fs.writeFile(path.join(codexHomeSource, "auth.json"), '{"token":"test"}\n', "utf8");
  await fs.writeFile(path.join(codexHomeSource, "config.toml"), 'model = "gpt-5.4"\n', "utf8");

  const previousSource = process.env.PLUGIN_EVAL_CODEX_HOME_SOURCE;
  process.env.PLUGIN_EVAL_CODEX_HOME_SOURCE = codexHomeSource;

  const provisioned = await provisionBenchmarkWorkspace({
    target: {
      kind: "skill",
      name: "minimal-skill",
      path: skillPath,
    },
    config: {
      workspace: {
        sourcePath: skillPath,
        setupMode: "copy",
      },
      targetProvisioning: {
        mode: "isolated-skill-home",
      },
    },
    scenarioId: "seed-auth",
  });

  try {
    assert.equal(
      await fs.readFile(path.join(provisioned.codexHomePath, "auth.json"), "utf8"),
      '{"token":"test"}\n',
    );
    assert.equal(
      await fs.readFile(path.join(provisioned.codexHomePath, "config.toml"), "utf8"),
      'model = "gpt-5.4"\n',
    );
  } finally {
    if (previousSource === undefined) {
      delete process.env.PLUGIN_EVAL_CODEX_HOME_SOURCE;
    } else {
      process.env.PLUGIN_EVAL_CODEX_HOME_SOURCE = previousSource;
    }
    await provisioned.cleanup();
  }
});

test("generates improvement briefs and comparison payloads", async () => {
  const goodPath = path.join(fixturesRoot, "minimal-skill");
  const badDir = await makeTempDir("plugin-eval-compare");
  await writeSkillFixture(badDir, {
    description: `Verbose description ${"y".repeat(1300)}`,
    bodyLines: 650,
  });

  const before = await analyzePath(badDir);
  const after = await analyzePath(goodPath);
  const diff = compareResults(before, after);

  assert.match(after.improvementBrief.suggestedPrompt, /skill-creator/i);
  assert.ok(diff.scoreDelta > 0);
  assert.ok(diff.resolvedFailures.length >= 1);
});

test("summary includes deductions, category totals, and risk reasons", async () => {
  const tempDir = await makeTempDir("plugin-eval-summary");
  await writeSkillFixture(tempDir, {
    description: `Verbose description ${"z".repeat(1300)}`,
    bodyLines: 650,
  });

  const result = await analyzePath(tempDir);

  assert.ok(result.summary.scoreBreakdown.totalDeductions > 0);
  assert.ok(result.summary.deductions.length > 0);
  assert.ok(result.summary.categoryDeductions.length > 0);
  assert.ok(result.summary.riskReasons.length > 0);
  assert.equal(result.summary.scoreBreakdown.finalScore, result.summary.score);
});

test("CLI analyze, report, compare, and explain-budget commands work together", async () => {
  const tempDir = await makeTempDir("plugin-eval-cli");
  const resultPath = path.join(tempDir, "result.json");
  const markdownPath = path.join(tempDir, "result.md");
  const comparePath = path.join(tempDir, "compare.md");
  const briefPath = path.join(tempDir, "brief.json");
  const measuresPath = path.join(tempDir, "measures.md");
  const skillPath = path.join(fixturesRoot, "minimal-skill");
  const usagePath = path.join(fixturesRoot, "observed-usage", "responses.jsonl");

  await execFileAsync(
    nodeBin,
    [cliPath, "analyze", skillPath, "--output", resultPath, "--brief-out", briefPath, "--observed-usage", usagePath],
    {
      cwd: repoRoot,
    },
  );
  const result = JSON.parse(await fs.readFile(resultPath, "utf8"));
  assert.equal(result.target.kind, "skill");
  assert.ok(await fs.stat(briefPath));
  assert.equal(result.observedUsage.sampleCount, 3);

  await execFileAsync(nodeBin, [cliPath, "report", resultPath, "--format", "markdown", "--output", markdownPath], {
    cwd: repoRoot,
  });
  assert.match(await fs.readFile(markdownPath, "utf8"), /Plugin Eval Report/);
  assert.match(await fs.readFile(markdownPath, "utf8"), /Recommended Next Step/);

  await execFileAsync(nodeBin, [cliPath, "compare", resultPath, resultPath, "--format", "markdown", "--output", comparePath], {
    cwd: repoRoot,
  });
  assert.match(await fs.readFile(comparePath, "utf8"), /Plugin Eval Comparison/);
  assert.match(await fs.readFile(comparePath, "utf8"), /Recommended Next Step/);

  const { stdout } = await execFileAsync(nodeBin, [cliPath, "explain-budget", skillPath], {
    cwd: repoRoot,
  });
  const budgetPayload = JSON.parse(stdout);
  assert.equal(budgetPayload.kind, "budget-explanation");
  assert.ok(budgetPayload.nextAction);

  await execFileAsync(
    nodeBin,
    [cliPath, "measurement-plan", skillPath, "--format", "markdown", "--output", measuresPath, "--observed-usage", usagePath],
    {
      cwd: repoRoot,
    },
  );
  assert.match(await fs.readFile(measuresPath, "utf8"), /Measurement Plan/);
  assert.match(await fs.readFile(measuresPath, "utf8"), /Recommended Next Step/);
  assert.match(await fs.readFile(measuresPath, "utf8"), /<details>/);
});

test("CLI init-benchmark and benchmark commands work together with a fake codex executable", async () => {
  const sourcePath = path.join(fixturesRoot, "minimal-skill");
  const tempDir = await makeTempDir("plugin-eval-cli-benchmark");
  const skillPath = path.join(tempDir, "minimal-skill");
  const fakeCodexPath = await createFakeCodexExecutable(tempDir);
  const initPath = path.join(tempDir, "init.md");
  const runPath = path.join(tempDir, "run.md");
  await copyDirectory(sourcePath, skillPath);

  await execFileAsync(
    nodeBin,
    [cliPath, "init-benchmark", skillPath, "--format", "markdown", "--output", path.join(skillPath, ".plugin-eval", "benchmark.json")],
    {
      cwd: repoRoot,
    },
  );

  const { stdout } = await execFileAsync(
    nodeBin,
    [cliPath, "init-benchmark", skillPath, "--format", "markdown"],
    {
      cwd: repoRoot,
    },
  );
  await fs.writeFile(initPath, stdout, "utf8");
  assert.match(await fs.readFile(initPath, "utf8"), /Benchmark Template Ready/);
  assert.match(await fs.readFile(initPath, "utf8"), /Use From Codex Chat/);

  const run = await execFileAsync(
    nodeBin,
    [cliPath, "benchmark", skillPath, "--format", "markdown"],
    {
      cwd: repoRoot,
      env: {
        ...process.env,
        PATH: `${path.dirname(fakeCodexPath)}:${process.env.PATH}`,
        PLUGIN_EVAL_CODEX_EXECUTABLE: fakeCodexPath,
      },
    },
  );
  await fs.writeFile(runPath, run.stdout, "utf8");
  assert.match(await fs.readFile(runPath, "utf8"), /Benchmark Run/);
  assert.match(await fs.readFile(runPath, "utf8"), /Recommended Next Step/);
  assert.match(await fs.readFile(runPath, "utf8"), /Scenarios/);
  assert.match(await fs.readFile(runPath, "utf8"), /Codex version: codex-cli fake-test/);
});

test("explainBudget returns a budget-only payload", async () => {
  const payload = await explainBudget(path.join(fixturesRoot, "minimal-skill"));

  assert.equal(payload.kind, "budget-explanation");
  assert.equal(payload.budgets.method, "estimated-static");
  assert.ok(payload.budgets.trigger_cost_tokens.value > 0);
  assert.ok(payload.workflowGuide);
});

test("workflow guide routes natural chat requests into the beginner-friendly path", async () => {
  const skillPath = path.join(fixturesRoot, "minimal-skill");
  const guide = await buildWorkflowGuide(skillPath, {
    request: "Measure the real token usage of this skill.",
  });
  const markdown = renderPayload(guide, "markdown");

  assert.equal(guide.kind, "workflow-guide");
  assert.equal(guide.recommendedWorkflowId, "measure");
  assert.equal(guide.requestRouting.goal, "measure");
  assert.ok(guide.nextAction);
  assert.match(markdown, /Plugin Eval Start Here/);
  assert.match(markdown, /Measure the real token usage of this skill\./);
  assert.match(markdown, /Quick local entrypoint: `plugin-eval start/);
  assert.match(markdown, /plugin-eval init-benchmark/);
});

test("workflow guide routes analysis requests into report plus benchmark setup", async () => {
  const skillPath = path.join(fixturesRoot, "minimal-skill");
  const guide = await buildWorkflowGuide(skillPath, {
    request: "give me an analysis of the game dev skill",
  });
  const markdown = renderPayload(guide, "markdown");

  assert.equal(guide.kind, "workflow-guide");
  assert.equal(guide.recommendedWorkflowId, "analysis");
  assert.equal(guide.requestRouting.goal, "analysis");
  assert.equal(guide.startHere.firstCommand, `plugin-eval analyze ${formatCommandPath(skillPath)} --format markdown`);
  assert.ok(guide.startHere.commands.some((command) => command.includes("plugin-eval init-benchmark")));
  assert.match(markdown, /Full Skill Analysis/);
  assert.match(markdown, /plugin-eval init-benchmark/);
});

test("CLI start command renders chat-first workflow suggestions", async () => {
  const skillPath = path.join(fixturesRoot, "minimal-skill");
  const { stdout } = await execFileAsync(
    nodeBin,
    [cliPath, "start", skillPath, "--request", "what should I run next?", "--format", "markdown"],
    {
      cwd: repoRoot,
    },
  );

  assert.match(stdout, /Plugin Eval Start Here/);
  assert.match(stdout, /What should I run next\?/i);
  assert.match(stdout, /plugin-eval start .*what should I run next/i);
  assert.match(stdout, /plugin-eval analyze/);
  assert.match(stdout, /Recommended Next Step/);
});

test("shipped plugin surfaces advertise beginner chat prompts", async () => {
  const manifest = JSON.parse(await fs.readFile(path.join(repoRoot, ".codex-plugin", "plugin.json"), "utf8"));
  const umbrellaSkill = await fs.readFile(path.join(repoRoot, "skills", "plugin-eval", "SKILL.md"), "utf8");
  const readme = await fs.readFile(path.join(repoRoot, "README.md"), "utf8");

  assert.match(manifest.interface.longDescription, /plugin-eval start/i);
  assert.deepEqual(manifest.interface.defaultPrompt, [
    "Give me an analysis of the game studio plugin.",
    "Evaluate this plugin.",
    "Why did this score that way?",
    "What should I fix first?"
  ]);
  assert.match(umbrellaSkill, /plugin-eval start <path> --request/);
  assert.match(umbrellaSkill, /analysis of the game dev skill/i);
  assert.match(umbrellaSkill, /plugin-eval measurement-plan/);
  assert.match(umbrellaSkill, /What should I fix first\?/);
  assert.match(readme, /Start From Chat/);
  assert.match(readme, /plugin-eval start <path> --request/);
  assert.match(readme, /analysis of the game dev skill/i);
  assert.match(readme, /Why did this score that way\?/);
});
