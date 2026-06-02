import { spawn } from "node:child_process";
import fs from "node:fs/promises";
import path from "node:path";

import { analyzeCoverageArtifacts } from "../evaluators/coverage.js";
import { analyzePythonFiles } from "../evaluators/python.js";
import { analyzeTypeScriptFiles } from "../evaluators/typescript.js";
import { formatCommandPath, pathExists, readJson, readText, relativePath, writeJson, writeText } from "../lib/files.js";
import { createBenchmarkRunNextAction, createBenchmarkTemplateNextAction } from "./presentation.js";
import { createArtifact } from "./schema.js";
import { summarizeCodexEvents, parseCodexJsonStream } from "./benchmark-events.js";
import {
  defaultTargetProvisioningMode,
  diffWorkspaceSnapshots,
  provisionBenchmarkWorkspace,
  snapshotWorkspace,
  summarizeWorkspaceDiff,
} from "./benchmark-workspace.js";
import { resolveTarget } from "./target.js";
import { buildWorkflowGuide } from "./workflow-guide.js";

const BENCHMARK_SCHEMA_VERSION = 2;

function sanitizeId(value) {
  return String(value || "scenario")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "") || "scenario";
}

function benchmarkDirectoryForTarget(target) {
  return path.join(target.path, ".plugin-eval");
}

function benchmarkRunsDirectoryForTarget(target) {
  return path.join(benchmarkDirectoryForTarget(target), "runs");
}

function defaultBenchmarkConfigPath(target) {
  return path.join(benchmarkDirectoryForTarget(target), "benchmark.json");
}

function defaultUsageLogPath(target) {
  return path.join(benchmarkDirectoryForTarget(target), "benchmark-usage.jsonl");
}

function defaultModelForTarget(target) {
  return target.kind === "plugin" ? "gpt-5.4" : "gpt-5.4-mini";
}

function createRunId() {
  return new Date().toISOString().replaceAll(":", "-").replace(/\..+$/, "");
}

function normalizeScenario(scenario, index) {
  return {
    id: sanitizeId(scenario.id || scenario.title || `scenario-${index + 1}`),
    title: scenario.title || `Scenario ${index + 1}`,
    purpose: scenario.purpose || "",
    userInput: scenario.userInput || "",
    successChecklist: Array.isArray(scenario.successChecklist) ? scenario.successChecklist : [],
  };
}

function normalizeConfig(config, target) {
  if (config?.schemaVersion === 1 || config?.harnessPrompt || config?.baseUrl || config?.apiKeyEnv) {
    throw new Error(
      "Legacy Responses-style benchmark configs are no longer supported. Re-run `plugin-eval init-benchmark <path>` to generate a CLI-only Codex benchmark config.",
    );
  }

  if (!config || config.kind !== "plugin-eval-benchmark") {
    throw new Error("Invalid benchmark config. Expected a plugin-eval benchmark config file.");
  }

  if (config.schemaVersion !== BENCHMARK_SCHEMA_VERSION) {
    throw new Error(
      `Unsupported benchmark schema version: ${config.schemaVersion}. Re-run \`plugin-eval init-benchmark ${formatCommandPath(target.path)}\` to regenerate the config.`,
    );
  }

  if (config.runner?.type !== "codex-cli") {
    throw new Error("Benchmark runner.type must be \"codex-cli\".");
  }

  if (!config.workspace?.sourcePath) {
    throw new Error("Benchmark config must set workspace.sourcePath.");
  }

  if (!config.targetProvisioning?.mode) {
    throw new Error("Benchmark config must set targetProvisioning.mode.");
  }

  return config;
}

function buildSetupQuestions(target) {
  const label = target.kind === "plugin" ? "plugin" : "skill";
  return [
    `What are the 3 highest-value real tasks this ${label} should help complete inside a workspace?`,
    `Which scenario is the must-pass end-to-end task for this ${label}?`,
    `What output should exist on disk if the scenario succeeds?`,
    `Which verification command would tell you the result is actually usable?`,
    `What boundary case should this ${label} narrow, refuse, or hand off instead of overreaching on?`,
  ];
}

function buildSkillScenarios(target) {
  return [
    {
      id: "happy-path",
      title: "Happy path implementation",
      purpose: "Run a representative task that should clearly justify using this skill inside the workspace.",
      userInput: `Use the local Codex skill "${target.name}" if it helps. Complete a representative task for this skill in the current workspace and leave the result on disk.`,
      successChecklist: [
        "The task is completed in the workspace, not only described.",
        "The final answer explains what changed.",
        "The run stays aligned with the skill's specialty.",
      ],
    },
    {
      id: "follow-up",
      title: "Focused refinement",
      purpose: "Measure whether the skill can improve an implementation cleanly instead of restarting from scratch.",
      userInput: `Use the local Codex skill "${target.name}" if it helps. Refine or extend the current workspace with one focused follow-up improvement and finish the change end to end.`,
      successChecklist: [
        "The result makes a concrete change on disk.",
        "The follow-up remains scoped and coherent.",
      ],
    },
    {
      id: "boundary-case",
      title: "Boundary handling",
      purpose: "Check whether the skill avoids overreaching when the task is only a partial fit.",
      userInput: `This task is only a partial match for the local Codex skill "${target.name}". Handle the appropriate slice in the workspace and narrow or refuse the rest honestly.`,
      successChecklist: [
        "The run sets good boundaries instead of pretending the skill fits everything.",
        "Any edits stay aligned with the justified scope.",
      ],
    },
  ];
}

function buildPluginScenarios(target) {
  return [
    {
      id: "entrypoint-routing",
      title: "Entrypoint routing",
      purpose: "Check whether the plugin routes a representative request through the right capability and finishes the task in the workspace.",
      userInput: `Use the local Codex plugin "${target.name}" if it helps. Handle a representative request for this plugin in the current workspace and finish the task.`,
      successChecklist: [
        "The run uses the right plugin capability.",
        "The result changes the workspace instead of only describing work.",
      ],
    },
    {
      id: "multi-skill-follow-up",
      title: "Multi-capability follow-up",
      purpose: "Measure whether a second request stays coherent when the plugin needs a different angle.",
      userInput: `Use the local Codex plugin "${target.name}" if it helps. Complete a follow-up task in the current workspace that needs a different angle from the same plugin, and keep the result cohesive.`,
      successChecklist: [
        "The task completes end to end.",
        "The run stays coherent instead of redoing unrelated work.",
      ],
    },
    {
      id: "plugin-boundary",
      title: "Plugin boundary",
      purpose: "Check whether the plugin narrows scope when the request is a weak match.",
      userInput: `This task is a weak match for the local Codex plugin "${target.name}". Handle the appropriate slice in the workspace, leave unrelated work alone, and explain the boundary clearly.`,
      successChecklist: [
        "The run narrows scope instead of forcing a bad fit.",
        "Any edits stay justified by the request.",
      ],
    },
  ];
}

async function createStarterBenchmarkConfig(target, options = {}) {
  if (!["skill", "plugin"].includes(target.kind)) {
    throw new Error("Benchmarking only supports Codex skills and plugins.");
  }

  return {
    kind: "plugin-eval-benchmark",
    schemaVersion: BENCHMARK_SCHEMA_VERSION,
    version: BENCHMARK_SCHEMA_VERSION,
    targetKind: target.kind,
    targetName: target.name,
    runner: {
      type: "codex-cli",
      model: options.model || defaultModelForTarget(target),
      sandbox: "workspace-write",
      approvalPolicy: "never",
      extraArgs: [],
    },
    workspace: {
      sourcePath: path.resolve(options.sourcePath || process.cwd()),
      setupMode: "copy",
      preserve: "on-failure",
    },
    targetProvisioning: {
      mode: defaultTargetProvisioningMode(target),
    },
    verifiers: {
      commands: [],
    },
    notes: [
      "Edit workspace.sourcePath so it points at the repo or template you want Codex to work inside.",
      "Edit the scenarios so they match real tasks instead of generic starter prompts.",
      "Benchmark means real codex exec runs now. There is no simulated dry-run mode.",
    ],
    setupQuestions: buildSetupQuestions(target),
    scenarios: target.kind === "plugin" ? buildPluginScenarios(target) : buildSkillScenarios(target),
  };
}

async function loadBenchmarkConfig(target, options = {}) {
  if (options.configPath) {
    const config = readJson(path.resolve(options.configPath));
    return {
      config: normalizeConfig(await config, target),
      configPath: path.resolve(options.configPath),
      source: "file",
    };
  }

  const defaultConfigPath = defaultBenchmarkConfigPath(target);
  if (await pathExists(defaultConfigPath)) {
    const config = await readJson(defaultConfigPath);
    return {
      config: normalizeConfig(config, target),
      configPath: defaultConfigPath,
      source: "file",
    };
  }

  const generated = await createStarterBenchmarkConfig(target, options);
  return {
    config: generated,
    configPath: null,
    source: "generated",
  };
}

async function runProcessCapture({
  command,
  args,
  cwd,
  env,
  stdoutPath,
  stderrPath,
}) {
  const startedAt = Date.now();
  const child = spawn(command, args, {
    cwd,
    env,
    stdio: ["ignore", "pipe", "pipe"],
  });

  const stdoutChunks = [];
  const stderrChunks = [];

  if (child.stdout) {
    child.stdout.on("data", (chunk) => {
      stdoutChunks.push(chunk);
    });
  }

  if (child.stderr) {
    child.stderr.on("data", (chunk) => {
      stderrChunks.push(chunk);
    });
  }

  const outcome = await new Promise((resolve, reject) => {
    child.once("error", reject);
    child.once("close", (code, signal) => {
      resolve({ code: code ?? 1, signal });
    });
  });

  const stdoutText = Buffer.concat(stdoutChunks).toString("utf8");
  const stderrText = Buffer.concat(stderrChunks).toString("utf8");

  if (stdoutPath) {
    await writeText(stdoutPath, stdoutText);
  }
  if (stderrPath) {
    await writeText(stderrPath, stderrText);
  }

  return {
    ...outcome,
    durationMs: Date.now() - startedAt,
    stdoutText,
    stderrText,
  };
}

function buildObservedUsageLine(target, scenario, usage) {
  return JSON.stringify({
    id: `${target.name}-${scenario.id}`,
    usage: usage.raw || usage,
    metadata: {
      scenario: scenario.title,
      scenario_id: scenario.id,
      benchmark_target_name: target.name,
      benchmark_target_kind: target.kind,
    },
  });
}

function tomlString(value) {
  return JSON.stringify(String(value));
}

function buildCodexExecArgs({
  config,
  model,
  workspacePath,
  finalMessagePath,
  prompt,
}) {
  return [
    "exec",
    "--json",
    "--ephemeral",
    "--skip-git-repo-check",
    "--cd",
    workspacePath,
    "--output-last-message",
    finalMessagePath,
    "-s",
    config.runner.sandbox || "workspace-write",
    "-c",
    `approval_policy=${tomlString(config.runner.approvalPolicy || "never")}`,
    "-m",
    model,
    ...(Array.isArray(config.runner.extraArgs) ? config.runner.extraArgs : []),
    prompt,
  ];
}

function filterCodeFiles(filePaths) {
  const tsFiles = [];
  const pyFiles = [];

  for (const filePath of filePaths) {
    const extension = path.extname(filePath).toLowerCase();
    if ([".ts", ".tsx", ".mts", ".cts"].includes(extension)) {
      tsFiles.push(filePath);
    } else if (extension === ".py") {
      pyFiles.push(filePath);
    }
  }

  return { tsFiles, pyFiles };
}

async function analyzeChangedWorkspaceCode(workspacePath, changedRelativePaths) {
  const absoluteFilePaths = changedRelativePaths
    .map((filePath) => path.join(workspacePath, filePath))
    .filter((filePath) => path.extname(filePath));
  const { tsFiles, pyFiles } = filterCodeFiles(absoluteFilePaths);
  const tsAnalysis = await analyzeTypeScriptFiles(tsFiles, workspacePath);
  const pyAnalysis = await analyzePythonFiles(pyFiles, workspacePath);
  const coverageAnalysis = await analyzeCoverageArtifacts(workspacePath);

  return {
    checks: [...tsAnalysis.checks, ...pyAnalysis.checks, ...coverageAnalysis.checks],
    metrics: [...tsAnalysis.metrics, ...pyAnalysis.metrics, ...coverageAnalysis.metrics],
    artifacts: [...tsAnalysis.artifacts, ...pyAnalysis.artifacts, ...coverageAnalysis.artifacts],
  };
}

async function runVerifierCommands({ commands, cwd, processRunner, basePath }) {
  const results = [];

  for (let index = 0; index < commands.length; index += 1) {
    const command = commands[index];
    const stdoutPath = path.join(basePath, `verifier-${index + 1}.stdout.log`);
    const stderrPath = path.join(basePath, `verifier-${index + 1}.stderr.log`);
    const outcome = await processRunner({
      kind: "verifier",
      command: "/bin/zsh",
      args: ["-lc", command],
      cwd,
      env: process.env,
      stdoutPath,
      stderrPath,
    });

    results.push({
      command,
      status: outcome.code === 0 ? "passed" : "failed",
      exitCode: outcome.code,
      signal: outcome.signal || null,
      durationMs: outcome.durationMs,
      stdoutPath,
      stderrPath,
    });
  }

  return results;
}

function summarizeRunScenarios(runScenarios) {
  const usageSamples = runScenarios.filter((scenario) => scenario.usage);
  const completedScenarios = runScenarios.filter((scenario) => scenario.status === "completed").length;
  const failedScenarios = runScenarios.filter((scenario) => scenario.status !== "completed").length;
  const input = usageSamples.reduce((sum, scenario) => sum + (scenario.usage?.input_tokens || 0), 0);
  const output = usageSamples.reduce((sum, scenario) => sum + (scenario.usage?.output_tokens || 0), 0);
  const total = usageSamples.reduce((sum, scenario) => sum + (scenario.usage?.total_tokens || 0), 0);
  const generatedFileCount = runScenarios.reduce((sum, scenario) => sum + (scenario.workspaceSummary?.generatedFileCount || 0), 0);
  const generatedTestFileCount = runScenarios.reduce((sum, scenario) => sum + (scenario.workspaceSummary?.generatedTestFileCount || 0), 0);
  const toolCallCount = runScenarios.reduce((sum, scenario) => sum + (scenario.telemetry?.toolCallCount || 0), 0);
  const shellCommandCount = runScenarios.reduce((sum, scenario) => sum + (scenario.telemetry?.shellCommandCount || 0), 0);
  const failedShellCommands = runScenarios.reduce((sum, scenario) => sum + (scenario.telemetry?.failedShellCommandCount || 0), 0);
  const verifierPassCount = runScenarios.reduce(
    (sum, scenario) => sum + scenario.verifierResults.filter((result) => result.status === "passed").length,
    0,
  );
  const verifierFailCount = runScenarios.reduce(
    (sum, scenario) => sum + scenario.verifierResults.filter((result) => result.status === "failed").length,
    0,
  );

  return {
    scenarioCount: runScenarios.length,
    completedScenarios,
    failedScenarios,
    sampleCount: usageSamples.length,
    usageAvailability:
      usageSamples.length === 0
        ? "unavailable"
        : usageSamples.length === runScenarios.length
          ? "present"
          : "partial",
    averageInputTokens: usageSamples.length > 0 ? Number((input / usageSamples.length).toFixed(2)) : 0,
    averageOutputTokens: usageSamples.length > 0 ? Number((output / usageSamples.length).toFixed(2)) : 0,
    averageTotalTokens: usageSamples.length > 0 ? Number((total / usageSamples.length).toFixed(2)) : 0,
    generatedFileCount,
    generatedTestFileCount,
    toolCallCount,
    shellCommandCount,
    failedShellCommands,
    verifierPassCount,
    verifierFailCount,
  };
}

export async function initializeBenchmark(targetPath, options = {}) {
  const target = await resolveTarget(targetPath);
  const config = await createStarterBenchmarkConfig(target, options);
  const outputPath = path.resolve(options.outputPath || defaultBenchmarkConfigPath(target));
  await writeJson(outputPath, config);

  const payload = {
    kind: "benchmark-template-init",
    createdAt: new Date().toISOString(),
    target: {
      ...target,
      relativePath: relativePath(process.cwd(), target.path),
    },
    configPath: outputPath,
    scenarioCount: config.scenarios.length,
    notes: config.notes,
    setupQuestions: config.setupQuestions || [],
    nextSteps: [
      `Edit ${formatCommandPath(outputPath)} so workspace.sourcePath, scenarios, and verifiers match your real workflow.`,
      `Run the benchmark with: plugin-eval benchmark ${formatCommandPath(target.path)} --config ${formatCommandPath(outputPath)}`,
      "The benchmark result will be written under .plugin-eval/runs/<timestamp>/benchmark-run.json.",
    ],
    workflowGuide: await buildWorkflowGuide(target.path, {
      goal: "benchmark",
    }),
    artifact: createArtifact({
      id: "benchmark-template",
      type: "benchmark-template",
      label: "Benchmark template",
      description: "Starter benchmark config for Codex CLI execution.",
      path: outputPath,
    }),
  };
  payload.nextAction = createBenchmarkTemplateNextAction(payload);
  return payload;
}

export async function runBenchmark(targetPath, options = {}) {
  const target = await resolveTarget(targetPath);
  const { config, configPath, source } = await loadBenchmarkConfig(target, options);
  const scenarios = (config.scenarios || []).map(normalizeScenario).filter((scenario) => scenario.userInput);
  if (scenarios.length === 0) {
    throw new Error("Benchmark config does not contain any runnable scenarios.");
  }
  if (options.dryRun) {
    throw new Error("CLI-only benchmarking no longer supports --dry-run. Edit the benchmark config, then run `plugin-eval benchmark` for a real Codex execution.");
  }

  const processRunner = options.processRunner || runProcessCapture;
  const codexExecutable = options.codexExecutable || process.env.PLUGIN_EVAL_CODEX_EXECUTABLE || "codex";
  const runId = createRunId();
  const runDirectory = path.join(benchmarkRunsDirectoryForTarget(target), runId);
  await fs.mkdir(runDirectory, { recursive: true });

  let codexVersion = "unknown";
  try {
    const versionResult = await processRunner({
      kind: "codex-version",
      command: codexExecutable,
      args: ["--version"],
      cwd: process.cwd(),
      env: process.env,
      stdoutPath: path.join(runDirectory, "codex-version.stdout.log"),
      stderrPath: path.join(runDirectory, "codex-version.stderr.log"),
    });
    codexVersion = (versionResult.stdoutText || versionResult.stderrText || "unknown").trim().split(/\r?\n/).pop() || "unknown";
  } catch {
    codexVersion = "unknown";
  }

  const usageLines = [];
  const runScenarios = [];

  for (let index = 0; index < scenarios.length; index += 1) {
    const scenario = scenarios[index];
    const scenarioDirectory = path.join(runDirectory, `${String(index + 1).padStart(2, "0")}-${scenario.id}`);
    await fs.mkdir(scenarioDirectory, { recursive: true });

    const provisioned = await provisionBenchmarkWorkspace({
      target,
      config,
      scenarioId: scenario.id,
    });
    const beforeSnapshot = await snapshotWorkspace(provisioned.workspacePath);
    const stdoutPath = path.join(scenarioDirectory, "codex.stdout.jsonl");
    const stderrPath = path.join(scenarioDirectory, "codex.stderr.log");
    const finalMessagePath = path.join(scenarioDirectory, "final-message.txt");

    const args = buildCodexExecArgs({
      config,
      model: options.model || config.runner.model || defaultModelForTarget(target),
      workspacePath: provisioned.workspacePath,
      finalMessagePath,
      prompt: scenario.userInput,
    });

    const codexRun = await processRunner({
      kind: "codex",
      command: codexExecutable,
      args,
      cwd: provisioned.workspacePath,
      env: {
        ...process.env,
        HOME: provisioned.homePath,
        CODEX_HOME: provisioned.codexHomePath,
      },
      stdoutPath,
      stderrPath,
    });

    const parsedEvents = parseCodexJsonStream(codexRun.stdoutText);
    const telemetry = summarizeCodexEvents(parsedEvents.events);
    telemetry.ignoredLineCount = parsedEvents.ignoredLines.length;

    const afterSnapshot = await snapshotWorkspace(provisioned.workspacePath);
    const workspaceDiff = diffWorkspaceSnapshots(beforeSnapshot, afterSnapshot);
    const workspaceSummary = summarizeWorkspaceDiff(workspaceDiff);
    const generatedCode = await analyzeChangedWorkspaceCode(
      provisioned.workspacePath,
      workspaceSummary.changedFiles.map((entry) => entry.path),
    );
    const verifierResults = await runVerifierCommands({
      commands: Array.isArray(config.verifiers?.commands) ? config.verifiers.commands : [],
      cwd: provisioned.workspacePath,
      processRunner,
      basePath: scenarioDirectory,
    });

    const finalMessage = await readText(finalMessagePath).catch(() => "");
    const codexSucceeded = codexRun.code === 0 && telemetry.finalStatus !== "failed";
    const verifiersPassed = verifierResults.every((result) => result.status === "passed");
    const scenarioStatus = codexSucceeded && verifiersPassed ? "completed" : "failed";

    if (telemetry.usage) {
      usageLines.push(buildObservedUsageLine(target, scenario, telemetry.usage));
    }

    const preserveMode = config.workspace.preserve || "on-failure";
    const shouldPreserveWorkspace =
      preserveMode === "always" ||
      (preserveMode === "on-failure" && scenarioStatus !== "completed");

    runScenarios.push({
      id: scenario.id,
      title: scenario.title,
      purpose: scenario.purpose,
      successChecklist: scenario.successChecklist,
      status: scenarioStatus,
      exitCode: codexRun.code,
      signal: codexRun.signal || null,
      durationMs: codexRun.durationMs,
      prompt: scenario.userInput,
      finalMessagePath: await pathExists(finalMessagePath) ? finalMessagePath : null,
      finalMessagePreview: finalMessage.trim() || null,
      rawEventLogPath: stdoutPath,
      stderrLogPath: stderrPath,
      usage: telemetry.usage,
      usageAvailability: telemetry.usageAvailability,
      telemetry,
      workspacePath: shouldPreserveWorkspace ? provisioned.workspacePath : null,
      workspaceSummary,
      workspaceChanges: workspaceSummary.allChanges,
      generatedCode,
      verifierResults,
      installedTargetPath: provisioned.installedTargetPath,
      codexHomePath: provisioned.codexHomePath,
    });

    if (!shouldPreserveWorkspace) {
      await provisioned.cleanup();
    }
  }

  const usageOutPath = usageLines.length > 0
    ? path.resolve(options.usageOutPath || defaultUsageLogPath(target))
    : null;
  if (usageOutPath) {
    await writeText(usageOutPath, `${usageLines.join("\n")}\n`);
    await writeText(path.join(runDirectory, "observed-usage.jsonl"), `${usageLines.join("\n")}\n`);
  }

  const resultOutPath = path.resolve(options.resultOutPath || path.join(runDirectory, "benchmark-run.json"));
  const summary = summarizeRunScenarios(runScenarios);
  const payload = {
    kind: "benchmark-run",
    createdAt: new Date().toISOString(),
    mode: "codex-cli",
    target: {
      ...target,
      relativePath: relativePath(process.cwd(), target.path),
    },
    codexVersion,
    config: {
      source,
      path: configPath,
      runnerType: config.runner.type,
      model: options.model || config.runner.model || defaultModelForTarget(target),
      sandbox: config.runner.sandbox || "workspace-write",
      approvalPolicy: config.runner.approvalPolicy || "never",
      scenarioCount: scenarios.length,
      workspaceSourcePath: path.resolve(config.workspace.sourcePath),
      workspaceSetupMode: config.workspace.setupMode || "copy",
      workspacePreserve: config.workspace.preserve || "on-failure",
      targetProvisioningMode: config.targetProvisioning.mode,
      verifierCount: Array.isArray(config.verifiers?.commands) ? config.verifiers.commands.length : 0,
    },
    runDirectory,
    usageLogPath: usageOutPath,
    resultPath: resultOutPath,
    summary,
    scenarios: runScenarios,
    nextSteps: usageOutPath
      ? [
          `Analyze the observed usage with: plugin-eval analyze ${formatCommandPath(target.path)} --observed-usage ${formatCommandPath(usageOutPath)} --format markdown`,
          `Review the measurement plan with: plugin-eval measurement-plan ${formatCommandPath(target.path)} --observed-usage ${formatCommandPath(usageOutPath)} --format markdown`,
        ]
      : [
          `Review the benchmark report with: plugin-eval report ${formatCommandPath(resultOutPath)} --format markdown`,
          "If token usage was unavailable, use the workspace outputs and verifier results as the primary quality signal.",
        ],
    workflowGuide: await buildWorkflowGuide(target.path, {
      goal: summary.sampleCount > 0 ? "measure" : "benchmark",
    }),
  };

  payload.nextAction = createBenchmarkRunNextAction(payload);
  await writeJson(resultOutPath, payload);
  return payload;
}
