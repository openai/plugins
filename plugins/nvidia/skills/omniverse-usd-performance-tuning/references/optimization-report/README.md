# Optimization Report

<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

## When to Use

Use this reference only at the end of the workflow after profile comparison and validation evidence are available.

## Instructions

1. Confirm the target asset, artifact, or user intent and check the prerequisites listed below.
2. Read only the referenced files needed for the current phase, failure mode, or output contract.
3. Follow the workflow, rules, and safety gates in this reference before invoking downstream references or shell commands.
4. Return the result using the Output Format section and name any blocked prerequisite or unresolved user decision.

Use this reference as the final step in the optimization flow — after
`compare-profiles` has produced its verdict. This reference assembles the
complete optimization story into a structured report.


## Pre-flight Checklist

Before generating the report, re-read and confirm:

- [ ] **HTML must use the committed renderer** — invoke
   `references/report-templates/render_preview.py` with `--fixture` and
   `--output`. Never hand-write HTML. Never use LLM-generated HTML.
- [ ] **JSON conforms to schema** — read
   `scripts/optimization-report.schema.json` in full before writing. Do not
   guess field names from memory.
- [ ] **Runtime context copied verbatim** from `setup-preflight.json`.
- [ ] **Score computed deterministically** — weighted average of metric groups,
   not hand-assigned.

### Anti-pattern: hand-written HTML

If `find` or `glob` does not locate the template, you are looking in the wrong
directory. The template lives at `references/report-templates/` (sibling to
`references/optimization-report/`, NOT inside it). Re-read this file's
*HTML Generation* section rather than concluding no template exists.
## Purpose

Create the final structured JSON, markdown summary, and static HTML report
that records the asset, input/output paths, profile metrics, operations,
validator findings, optimization verdict, agent reasoning, and high-level Stage
Optimization Score. The report title presented to readers is **USD Performance
Tuning Report**.

## Prerequisites

- Baseline and after profile results.
- `compare-profiles` verdict and per-metric comparison.
- Ordered operations performed and their outcomes.
- Validator findings, including clean checks.
- Output path for the optimized stage.
- Measurement context for stage/composition metrics (profiling mode, runtime,
  cache state, sample count, and stage-open method when known).
- Optional runtime profiling handoff details when Omniperf or another runtime
  profiler produced a dashboard/artifact.

## Examples

- "Generate the optimization report from these profile comparisons and validator results."
- "Create the final JSON, markdown summary, and static HTML report for this optimized USD."

## Inputs

Collect from prior steps:

- **Baseline profile** (from `profile-stage` before).
- **After profile** (from `profile-stage` after).
- **Compare-profiles verdict** and per-metric results.
- **Operations performed** — ordered list with method and outcome.
- **Validator findings** — what was checked, what was found, what was clean.
- **Output file path** — where the optimized stage was saved.
- **Runtime context** — copy the `runtime_context` object from
  `<output_path>/setup-preflight.json` verbatim (canonical location; see
  `skills/omniverse-usd-performance-tuning/references/setup-usd-performance-tuning/references/runtime-context-header.md` *Where artifacts live*). The
  report must record exactly which Kit
  application, Scene Optimizer version, and Asset Validator version produced
  the result so a later reader can reproduce or audit the run.
- **Measurement context** — for the stage/composition measurements used in the
  score.
- **Reasoning** — one to two concise paragraphs explaining why this specific
  optimization approach was chosen for this asset, including evidence and
  tradeoffs.
- **Runtime profiling handoff** — if runtime metrics matter, link or reference
  the Omniperf dashboard/artifacts separately instead of mixing RAM, VRAM, FPS,
  frame time, shader, or renderer data into the stage score.

## Output Format

Produce three artifacts:

1. `<output_dir>/<asset_name>_optimization_report.json` — structured, parseable.
2. `<output_dir>/<asset_name>_optimization_report.md` — human-readable summary.
3. `<output_dir>/<asset_name>_optimization_report.html` — static, styled,
   self-contained HTML for stakeholder review.

The markdown and HTML are generated from the JSON — the JSON is the source of truth.

Use the static templates under `references/report-templates/` when available.
Do not use JavaScript charting libraries or external assets. CSS-only score
rings, bars, badges, and color blocks are acceptable.

## HTML Generation (mandatory)

**Do NOT write the HTML report by hand.** Always invoke the committed renderer:

```bash
python3 references/report-templates/render_preview.py \
  --fixture <output_dir>/<asset_name>_optimization_report.json \
  --output  <output_dir>/<asset_name>_optimization_report.html
```

The renderer applies the designed template (`optimization-report.html.template`)
with correct score rings, metric cards, evidence tables, and NVIDIA styling.
Hand-written or LLM-generated HTML will not match the design system and is
**non-conformant** — the `scored_static_html_report_required` guardrail
requires use of this renderer.

## JSON schema

The report JSON must conform to `scripts/optimization-report.schema.json`.

Structure:

```json
{
  "asset_name": "SnowdonTowers_SampleHVAC",
  "input_path": "/path/to/original.usd",
  "output_path": "/path/to/optimized.usdc",
  "timestamp": "2026-01-01T00:00:00Z",
  "verdict": "improved",
  "runtime_context": {
    "kit": {
      "application": "USD Composer",
      "version": "110.1.0",
      "path": "D:\\build\\chk\\usd_composer-fat\\110.1.0+main.…\\kit",
      "build": "110.1.0+main.10181.f4b28ef2.gl.windows-x86_64.release"
    },
    "sceneOptimizer": {
      "extension": "omni.scene.optimizer.core",
      "version": "110.0.4"
    },
    "assetValidator": {
      "package": "omniverse-asset-validator",
      "version": "1.x.y",
      "source": "kit-extension"
    }
  },
  "optimization_score": 7.8,
  "score_scope": "stage_optimization",
  "score_label": "strong",
  "reasoning": "The agent prioritized composition cleanup because the baseline profile showed high layer count, expensive stage open, and repeated structure. The chosen operations reduce composition and traversal cost without changing visual intent.\n\nMore aggressive mesh repair or decimation was left out because validator findings indicate bounded-loss decisions that need user approval. Runtime profiling is separated into an Omniperf handoff.",
  "measurement_context": {
    "profile_mode": "quick USD composition profile",
    "runtime": "standalone USD Python",
    "score_scope": "stage/composition metrics only"
  },
  "runtime_profiling": {
    "status": "not_run",
    "recommended_tool": "Omniperf",
    "dashboard_url": null,
    "artifact_path": null,
    "summary": "Runtime profiling was not run for this report.",
    "caveat": "Use Omniperf for RAM, VRAM, FPS, frame time, shader, renderer, and GPU metrics."
  },
  "artifacts": {
    "json": "/path/to/SnowdonTowers_SampleHVAC_optimization_report.json",
    "markdown": "/path/to/SnowdonTowers_SampleHVAC_optimization_report.md",
    "html": "/path/to/SnowdonTowers_SampleHVAC_optimization_report.html"
  },
  "metric_groups": [
    {
      "id": "load_time",
      "display_name": "Composition Load",
      "score": 9.0,
      "status": "measured",
      "weight": 35,
      "summary": "Cold and warm open improved strongly."
    },
    {
      "id": "composition",
      "display_name": "Composition Complexity",
      "score": 8.5,
      "status": "measured",
      "weight": 25,
      "summary": "Layer and reference graph complexity improved."
    }
  ],
  "metrics": [
    {
      "name": "file_size_mb",
      "display_name": "File Size",
      "category": "storage_proxy",
      "unit": "MB",
      "before": 114.2,
      "after": 56.1,
      "change_pct": -50.9,
      "verdict": "improved"
    }
  ],
  "operations": [
    {
      "order": 1,
      "name": "Duplicate discipline deactivation",
      "method": "USD Python API (SetActive(False))",
      "result": "Removed 30 of 37 discipline subtrees at identical world transforms"
    }
  ],
  "validators": [
    {
      "name": "FlatHierarchiesChecker",
      "issues": 16,
      "notes": "Prototypes flat list, 16 repeated discipline children"
    },
    {
      "name": "EmptyLeafChecker",
      "issues": 1525,
      "notes": "Candidates for pruneLeaves"
    }
  ]
}
```

## Markdown template

```markdown
## USD Performance Tuning Report — {asset_name}

Stage Optimization Score: {optimization_score}/10 ({score_label})
Verdict: {verdict}

### Output File
{output_path}

### Reasoning

{reasoning}

### Runtime Context

| Component | Value |
|---|---|
| Kit application | {runtime_context.kit.application} {runtime_context.kit.version} |
| Kit path | {runtime_context.kit.path} |
| Kit build | {runtime_context.kit.build} |
| Scene Optimizer | {runtime_context.sceneOptimizer.extension} {runtime_context.sceneOptimizer.version} |
| Asset Validator | {runtime_context.assetValidator.package} {runtime_context.assetValidator.version} (via {runtime_context.assetValidator.source}) |

---

### Before / After at a Glance

| Metric | Before | After | Change |
|---|---|---|---|
| {for each metric} |

### Stage Impact Areas

| Area | Score | Status | Notes |
|---|---:|---|---|
| Composition Load | {score}/10 | measured | {summary} |
| Composition Complexity | {score}/10 | measured | {summary} |
| Instancing | {score}/10 | measured | {summary} |
| Validation | {score}/10 | measured | {summary} |

### Runtime Profiling

Runtime metrics such as RAM, VRAM, FPS, frame time, shader cost, and renderer
activity are not part of the Stage Optimization Score. Use Omniperf or an
equivalent runtime profiling dashboard for those measurements.

---

### Operations Performed

| # | Operation | Method | Result |
|---|---|---|---|
| {for each operation} |

---

### Validators Attempted / Result

| Validator | Result |
|---|---|
| {for each validator} |
```

## Rules

> ⚠️ **Schema conformance is mandatory — do not improvise the report shape.**
> Read `scripts/optimization-report.schema.json` **in full** before writing the
> report JSON. Do not synthesize field names or array-item structures from
> partial reads or memory. Each array (`metrics`, `operations`, `validators`)
> uses flat records with specific required keys — not nested objects with
> `baseline/after/deltas` or any other invented layout. If the schema file
> exceeds your context window, use the inline example in this reference as the
> canonical shape and validate your output against the `required` and `items`
> blocks before emitting. The schema rejects extra keys in `metric_groups[]`,
> `metrics[]`, `operations[]`, `validators[]`, and `artifacts`; update the
> schema first if a new report field is genuinely needed. Conformance failures
> are caught by `scored_static_html_report_required` in runtime checks.

- Always save the JSON report — it is the structured record of what happened.
- Always present the markdown to the user in chat.
- Always produce the static HTML report when writing report artifacts. In
  runtime checks, include `scored_static_html_report_required` in
  `phase_guardrails` when planning this final report contract.
- Always title the reader-facing report **USD Performance Tuning Report**.
- Always include a dedicated `Reasoning` section with one to two concise
  paragraphs explaining why the selected optimizations fit the evidence.
- Always compute and present a Stage Optimization Score from stage/composition
  metrics only. Good inputs include open/traverse/attribute-resolution timing,
  prim/layer/reference counts, instance/prototype coverage, time-sample counts,
  extent coverage, duplicate geometry/material findings, and validator deltas.
- Compute the top-level score deterministically from scored metric groups:
  `round(sum(group.score * group.weight) / sum(group.weight), 1)`. Exclude
  groups with `score=null` or `weight=0`. Do not hand-edit the top-level score
  after computing it.
- Derive `score_label` from the computed score: `excellent` for `>= 9.0`,
  `strong` for `>= 7.5`, `moderate` for `>= 5.5`, `neutral` for `>= 4.5`,
  `mixed` for `>= 2.5`, and `regressed` below `2.5`.
- Score each metric group with the same rubric: `10` for very large direct
  improvement (roughly `>= 75%`), `8.5` for strong improvement (`>= 50%`),
  `7` for clear improvement (`>= 25%`), `6` for small improvement (`>= 10%`),
  `5` for neutral/no meaningful change, `3` for mild regression, `1` for major
  regression, and `0` for failed or unusable output. Use intermediate values
  only when the evidence falls between bands, and explain that in `reasoning`
  or the group caveat.
- Do not include RAM, VRAM, FPS, frame time, shader cost, or renderer activity
  in the Stage Optimization Score. Put those in `runtime_profiling` and point
  to Omniperf or equivalent runtime profiler artifacts when available.
- If runtime observations are included for context, label them as external
  profiling observations under a specific configuration, not intrinsic asset
  properties.
- Use structural metrics (`file_size_*`, `prim_count`, `mesh_count`,
  `layer_count`, `total_vertices`, `total_attributes`, material counts) as
  stage/composition evidence. Treat file size carefully: compare total
  referenced footprint, not root-layer size only.
- Generate HTML by invoking `references/report-templates/render_preview.py`
  with `--fixture` pointing to the report JSON and `--output` for the HTML path.
  Never write HTML directly — always use the renderer (see *HTML Generation* above).
- Include metrics that didn't change (neutral) — this shows coverage.
- Include validators that found 0 issues — this shows what was checked.
- If the verdict is "regressed" or "mixed", say so clearly — do not hide regressions.
- Include the timestamp so results are traceable to a specific run.
## Limitations

- Does not profile, validate, or optimize the stage.
- Depends on upstream data quality; missing operations or validators should be marked as unavailable.
- The JSON report is the source of truth, with markdown generated from it.

## Troubleshooting

- If the schema validation fails, compare the report against `scripts/optimization-report.schema.json`.
- If the verdict is missing, return to `compare-profiles` before writing the final report.
- If an output path is unknown, stop and capture it rather than leaving the deliverable ambiguous.
