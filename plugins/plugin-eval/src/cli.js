import path from "node:path";

import { compareResults } from "./core/compare.js";
import { analyzePath, explainBudget, recommendMeasures } from "./core/analyze.js";
import { initializeBenchmark, runBenchmark } from "./core/benchmark.js";
import { buildWorkflowGuide } from "./core/workflow-guide.js";
import { readJson, writeText } from "./lib/files.js";
import { renderPayload } from "./renderers/index.js";
import { normalizeDistribution } from "./core/distribution.js";

function usage() {
  return `Plugin Eval helps first-time skill authors start from chat and keep the workflow local-first.

Start here:
  plugin-eval start <path> [--request "<chat request>"] [--goal evaluate|budget|measure|benchmark|next] [--format json|markdown|html] [--output <file>]

Core workflows:
  plugin-eval analyze <path> [--distribution unspecified|private-local|public] [--format json|markdown|html] [--output <file>] [--metric-pack <manifest.json>] [--observed-usage <file>] [--brief-out <file>]
  plugin-eval explain-budget <path> [--format json|markdown] [--output <file>]
  plugin-eval measurement-plan <path> [--format json|markdown] [--observed-usage <file>] [--output <file>]
  plugin-eval init-benchmark <path> [--output <benchmark.json>] [--model <model>] [--format json|markdown]
  plugin-eval benchmark <path> [--config <benchmark.json>] [--usage-out <usage.jsonl>] [--result-out <result.json>] [--model <model>] [--format json|markdown|html] [--output <file>]

Reports:
  plugin-eval report <result.json> [--format json|markdown|html] [--output <file>]
  plugin-eval compare <before.json> <after.json> [--format json|markdown|html] [--output <file>]

Context estimates:
  --additional-context <instruction-file>  Include a known additional instruction file; repeatable.
  Supported by analyze, explain-budget, measurement-plan, and start. External coverage remains incomplete.
Distribution scope:
  Use --distribution private-local for private local plugins, or public for public-release checks.
  The default unspecified scope does not grade public listing URLs. A local path or npm private flag does not establish distribution scope.

Chat-first examples:
  plugin-eval start ./skills/my-skill --request "evaluate this skill" --format markdown
  plugin-eval start ./skills/my-skill --request "measure the real token usage of this skill" --format markdown
  plugin-eval start ./plugins/my-plugin --request "help me benchmark this plugin" --format markdown
  plugin-eval start ./skills/my-skill --request "what should I run next?" --format markdown

Compatibility aliases:
  guide -> start
  recommend-measures -> measurement-plan
`;
}

function parseOptions(argv) {
  const positional = [];
  const options = {
    format: "json",
    output: null,
    metricPackManifests: [],
    observedUsagePaths: [],
    additionalContextPaths: [],
    configPath: null,
    usageOutPath: null,
    resultOutPath: null,
    model: null,
    goal: null,
    request: null,
    dryRun: false,
    briefOut: null,
    distribution: "unspecified",
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--distribution") {
      if (argv[index + 1] === undefined) {
        throw new Error("Missing distribution value. Use unspecified, private-local, or public.");
      }
      options.distribution = normalizeDistribution(argv[index + 1]);
      index += 1;
    } else if (arg === "--format") {
      options.format = argv[index + 1];
      index += 1;
    } else if (arg === "--output") {
      options.output = argv[index + 1];
      index += 1;
    } else if (arg === "--metric-pack") {
      options.metricPackManifests.push(argv[index + 1]);
      index += 1;
    } else if (arg === "--observed-usage") {
      options.observedUsagePaths.push(argv[index + 1]);
      index += 1;
    } else if (arg === "--additional-context") {
      const value = argv[index + 1];
      if (!value || value.startsWith("--")) throw new Error("Missing additional context file path.");
      options.additionalContextPaths.push(path.resolve(value));
      index += 1;
    } else if (arg === "--config") {
      options.configPath = argv[index + 1];
      index += 1;
    } else if (arg === "--usage-out") {
      options.usageOutPath = argv[index + 1];
      index += 1;
    } else if (arg === "--result-out") {
      options.resultOutPath = argv[index + 1];
      index += 1;
    } else if (arg === "--model") {
      options.model = argv[index + 1];
      index += 1;
    } else if (arg === "--goal") {
      options.goal = argv[index + 1];
      index += 1;
    } else if (arg === "--request") {
      options.request = argv[index + 1];
      index += 1;
    } else if (arg === "--dry-run") {
      options.dryRun = true;
    } else if (arg === "--brief-out") {
      options.briefOut = argv[index + 1];
      index += 1;
    } else if (arg === "--help" || arg === "-h") {
      options.help = true;
    } else {
      positional.push(arg);
    }
  }

  return { positional, options };
}

async function emit(payload, format, output) {
  const rendered = renderPayload(payload, format);
  if (output) {
    await writeText(path.resolve(output), rendered);
    return;
  }
  process.stdout.write(rendered);
}

export async function runCli(argv) {
  const [command, ...rest] = argv;
  if (!command || command === "--help" || command === "-h") {
    process.stdout.write(usage());
    return;
  }

  const { positional, options } = parseOptions(rest);
  if (options.help) {
    process.stdout.write(usage());
    return;
  }

  if (command === "analyze") {
    if (positional.length < 1) {
      throw new Error("Missing target path.\n\n" + usage());
    }
    const result = await analyzePath(positional[0], {
      distribution: options.distribution,
      metricPackManifests: options.metricPackManifests,
      additionalContextPaths: options.additionalContextPaths,
      observedUsagePaths: options.observedUsagePaths,
    });
    if (options.briefOut) {
      await writeText(path.resolve(options.briefOut), `${JSON.stringify(result.improvementBrief, null, 2)}\n`);
    }
    await emit(result, options.format, options.output);
    return;
  }

  if (command === "report") {
    if (positional.length < 1) {
      throw new Error("Missing result.json path.\n\n" + usage());
    }
    const result = await readJson(path.resolve(positional[0]));
    await emit(result, options.format, options.output);
    return;
  }

  if (command === "compare") {
    if (positional.length < 2) {
      throw new Error("Missing before/after result paths.\n\n" + usage());
    }
    const before = await readJson(path.resolve(positional[0]));
    const after = await readJson(path.resolve(positional[1]));
    await emit(compareResults(before, after), options.format, options.output);
    return;
  }

  if (command === "start" || command === "guide") {
    if (positional.length < 1) {
      throw new Error("Missing target path.\n\n" + usage());
    }
    const payload = await buildWorkflowGuide(positional[0], {
      distribution: options.distribution,
      goal: options.goal,
      request: options.request,
      additionalContextPaths: options.additionalContextPaths,
    });
    await emit(payload, options.format, options.output);
    return;
  }

  if (command === "explain-budget") {
    if (positional.length < 1) {
      throw new Error("Missing target path.\n\n" + usage());
    }
    const payload = await explainBudget(positional[0], { additionalContextPaths: options.additionalContextPaths, distribution: options.distribution });
    await emit(payload, options.format, options.output);
    return;
  }

  if (command === "measurement-plan" || command === "recommend-measures") {
    if (positional.length < 1) {
      throw new Error("Missing target path.\n\n" + usage());
    }
    const payload = await recommendMeasures(positional[0], {
      additionalContextPaths: options.additionalContextPaths,
      distribution: options.distribution,
      observedUsagePaths: options.observedUsagePaths,
    });
    await emit(payload, options.format, options.output);
    return;
  }

  if (command === "init-benchmark") {
    if (positional.length < 1) {
      throw new Error("Missing target path.\n\n" + usage());
    }
    const payload = await initializeBenchmark(positional[0], {
      outputPath: options.output,
      model: options.model,
    });
    await emit(payload, options.format, null);
    return;
  }

  if (command === "benchmark") {
    if (positional.length < 1) {
      throw new Error("Missing target path.\n\n" + usage());
    }
    const payload = await runBenchmark(positional[0], {
      configPath: options.configPath,
      usageOutPath: options.usageOutPath,
      resultOutPath: options.resultOutPath,
      model: options.model,
      dryRun: options.dryRun,
    });
    await emit(payload, options.format, options.output);
    return;
  }

  throw new Error(`Unknown command: ${command}\n\n${usage()}`);
}
