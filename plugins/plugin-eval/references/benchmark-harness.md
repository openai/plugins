# Benchmark Harness

The benchmark harness gives `plugin-eval` a beginner-friendly path to measured usage.

## Goals

- help first-time skill authors collect real usage without building their own harness
- keep the workflow local-first and transparent
- produce usage logs that can be fed back into `plugin-eval analyze --observed-usage`

## Workflow

1. Run `plugin-eval init-benchmark <path>`.
2. Edit the generated `benchmark.json` so `workspace.sourcePath`, the scenarios, and any verifier commands match real tasks.
3. Run the benchmark with `plugin-eval benchmark <path> --config <file>`.
4. Feed the usage log into `plugin-eval analyze` when usage telemetry is available.

## Design Choices

- The generated benchmark file is meant to be edited by humans.
- Scenarios use plain-language fields such as `title`, `purpose`, `userInput`, and `successChecklist`.
- Benchmarking means real `codex exec` runs, not simulated single-turn Responses API requests.
- Each benchmark run captures raw Codex logs plus a normalized report under `.plugin-eval/runs/<timestamp>/`.
- When token usage is emitted by Codex, the benchmark also writes JSONL usage logs in a shape that `--observed-usage` already understands.

## Commands

```bash
plugin-eval init-benchmark ./skills/my-skill
plugin-eval benchmark ./skills/my-skill
plugin-eval analyze ./skills/my-skill --observed-usage ./skills/my-skill/.plugin-eval/benchmark-usage.jsonl --format markdown
```
