# Plugin Eval Technical Design

## Overview

`plugin-eval` is a local-first Codex plugin and CLI for evaluating Codex skills and plugins. The design centers on a deterministic local engine that emits a stable `evaluation-result` JSON document. Skills orchestrate the engine. Report renderers, comparison views, workflow guides, and future app visualizations consume the same JSON contract.

The first version is intentionally static:

- No live Codex benchmarking
- No remote repository evaluation
- No automatic test execution
- No requirement for external dependencies beyond Node

## Primary Goals

- Evaluate local skill and plugin bundles with predictable results.
- Make token and context costs visible early, especially for skill authors.
- Provide concrete quality signals for TypeScript and Python code.
- Create a normalized extension point for custom metric packs.
- Generate improvement briefs that pair naturally with the shipped `skill-creator` workflow.
- Make the recommended chat-first workflow obvious for first-time skill authors.

## Non-Goals For V1

- Measuring actual Codex desktop host token consumption end to end
- Running a skill inside the Codex host as part of the evaluation
- Replacing model or product-level eval frameworks
- Language-specific deep analysis for every language beyond TypeScript and Python

## Architecture

### 1. Core Engine

The core engine lives under `src/core/` and owns:

- target resolution (`skill`, `plugin`, or generic directory/file)
- result schema creation
- budget calculation and banding
- score and risk summary generation
- metric-pack execution
- improvement brief generation

The engine is the source of truth. Other surfaces must not invent their own scoring logic.

### 2. Evaluators

Evaluators live under `src/evaluators/` and return normalized fragments:

- `checks[]`
- `metrics[]`
- `artifacts[]`

Built-in evaluators:

- skill structure and frontmatter checks
- plugin manifest and path checks
- token and context budget analysis
- TypeScript metrics
- Python metrics
- coverage artifact ingestion

### 3. Renderers

Renderers live under `src/renderers/` and consume the canonical evaluation payload.

Supported report formats:

- JSON
- Markdown
- HTML

The report output is deliberately thin. It should present the existing result cleanly, not compute new conclusions.

### 4. Codex Skills

The plugin exposes lightweight skills that route users into the engine:

- `plugin-eval`
- `evaluate-skill`
- `evaluate-plugin`
- `metric-pack-designer`
- `improve-skill`

These skills stay small and point users to references and CLI commands instead of embedding bulky logic.

The beginner paved road is:

1. User asks in chat: "Evaluate this skill." or "What should I run next?"
2. The umbrella skill or focused skill can run `plugin-eval start <path> --request "<user request>" --format markdown` to route that request intentionally.
3. The rendered output shows the routed chat request, the quick local entrypoint, and the first underlying workflow command side by side.

## Canonical Result Shape

The canonical result is a JSON object with:

- `target`
- `summary`
- `budgets`
- `checks[]`
- `metrics[]`
- `artifacts[]`
- `extensions[]`
- `improvementBrief`

### Summary

`summary` includes:

- `score`
- `grade`
- `riskLevel`
- `topRecommendations[]`

The summary is calculated from built-in checks only. Extension metric packs are stored under `extensions[]` and do not overwrite the core summary.

### Checks

Every check uses the normalized fields:

- `id`
- `category`
- `severity`
- `status`
- `message`
- `evidence[]`
- `remediation[]`
- `source`

### Metrics

Every metric uses the normalized fields:

- `id`
- `category`
- `value`
- `unit`
- `band`
- `source`

## Budget Model

The budget model is a first-class part of the evaluation result and uses three buckets:

- `trigger_cost_tokens`
- `invoke_cost_tokens`
- `deferred_cost_tokens`

### Definitions

- `trigger_cost_tokens`: text likely to matter before explicit invocation, such as names, descriptions, and starter prompts
- `invoke_cost_tokens`: core instruction payloads that are likely loaded when the skill or plugin is invoked
- `deferred_cost_tokens`: supporting references, scripts, and related text assets that are only pulled in later

### Measurement Mode In V1

The current implementation labels budget analysis as `estimated-static`.

That means:

- token counts are estimated locally from file contents
- the estimate is deterministic and repeatable
- budget bands are calibrated against a baseline corpus of shipped Codex skills and plugins when available locally

### Why Static Estimation First

We do not currently assume that the Codex plugin runtime exposes per-skill or per-plugin host token telemetry to plugins. The official OpenAI docs do show token usage support at the Responses API layer, but that is different from host-level Codex plugin execution telemetry.

## OpenAI Token Telemetry Notes

### What The Official Docs Do Show

As of April 7, 2026:

- the Responses API returns a `usage` object with `input_tokens`, `output_tokens`, and `total_tokens`
- the Responses API exposes `POST /v1/responses/input_tokens` to count request input tokens without running a full generation
- reasoning-capable responses expose extra token detail such as reasoning token counts

### What We Did Not Confirm

We did not find official documentation showing that a Codex plugin or skill can directly inspect the host runtime's own per-skill token usage from inside Codex.

### Design Consequence

V1 keeps token analysis local and estimated.

V2 can add an optional measured harness that:

- wraps a skill or plugin task in a controlled Responses API request
- captures `usage` from the response object
- optionally calls the input-token-count endpoint before execution
- records measured results beside static estimates instead of replacing them

## Future Harness Design

The future measured harness should be a separate execution mode, not the default.

Recommended shape:

- `static` mode: current default, zero network requirement
- `measured` mode: explicit opt-in, requires API credentials and a harness config

Measured harness outputs should live next to the static budget fields, for example:

- `budgets.method: "estimated-static"` or `"measured-responses-api"`
- `artifacts[]` entry for raw usage snapshots
- `extensions[]` or a dedicated measured-budget artifact for side-by-side comparison

This keeps the schema forward-compatible.

### Observed Usage In The Current Implementation

The current CLI now supports an intermediate step between purely static analysis and a fully managed harness:

- users can pass one or more `--observed-usage` files to `plugin-eval analyze`
- the files can contain Responses API usage payloads or Codex-like local session exports
- the result stores an `observedUsage` summary with averages, min/max values, cached tokens, and estimate drift
- the tool emits a built-in measurement plan so teams can decide what else to instrument beyond tokens

This keeps the default local-first while giving teams a way to calibrate the estimate against reality.

## Benchmark Harness For New Skill Authors

The next layer is a guided benchmark harness designed to be approachable for first-time skill authors:

- `plugin-eval init-benchmark <path>` writes a starter benchmark config with editable plain-language scenarios
- `plugin-eval benchmark <path> --dry-run` previews the exact Requests API payload shape before any network call
- `plugin-eval benchmark <path>` runs the scenarios, captures `usage`, and writes a local JSONL usage log
- the resulting usage log can be fed directly back into `plugin-eval analyze --observed-usage ...`

The benchmark harness is intentionally not framed as a full scientific eval system. It is the paved road for collecting:

- representative token usage
- first-pass scenario coverage
- a reusable scenario file that teams can gradually improve

This keeps the workflow intuitive:

1. Generate starter scenarios.
2. Edit them to match the real task.
3. Dry-run to preview.
4. Run live.
5. Feed the usage file back into analysis.

## Chat-First Workflow Guide

The CLI now includes a beginner router:

- `plugin-eval start <path>`

It is intentionally small and deterministic. It does not replace the engine or invent new scoring. It only maps natural user intents such as:

- `Evaluate this skill.`
- `Measure the real token usage of this skill.`
- `Help me benchmark this plugin.`
- `What should I run next?`

to the existing local command sequences.

## Metric Packs

Metric packs are external evaluators that produce schema-compatible findings.

Manifest responsibilities:

- `name`
- `version`
- `supportedTargetKinds`
- `command`

Runtime contract:

- the pack executes locally
- the pack receives target path and target kind
- the pack writes JSON to stdout
- the JSON may contain `checks[]`, `metrics[]`, and optional `artifacts[]`

The core engine stores the result under `extensions[]` without allowing packs to rewrite the main summary.

## Improvement Loop

The improvement loop is:

1. Evaluate a skill or plugin.
2. Review the prioritized checks and budget findings.
3. Generate an improvement brief.
4. Use `improve-skill` together with `skill-creator` guidance to refactor the skill.
5. Re-run evaluation and compare results.

## Testing Strategy

Fixture-driven tests verify:

- valid result JSON generation
- Markdown and HTML report rendering
- oversized descriptions and bloated `SKILL.md` detection
- broken plugin manifests and missing paths
- TypeScript and Python metrics
- coverage artifact ingestion
- custom metric-pack merging
- improvement brief generation
- comparison output

## References

- Responses API reference: [https://platform.openai.com/docs/api-reference/responses/create?api-mode=responses](https://platform.openai.com/docs/api-reference/responses/create?api-mode=responses)
- Responses input items and input token counts: [https://platform.openai.com/docs/api-reference/responses/input-items?lang=node.js](https://platform.openai.com/docs/api-reference/responses/input-items?lang=node.js)
- Reasoning token usage example: [https://platform.openai.com/docs/guides/reasoning/reasoning%3B.docx](https://platform.openai.com/docs/guides/reasoning/reasoning%3B.docx)
