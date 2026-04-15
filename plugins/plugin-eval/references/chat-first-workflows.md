# Plugin Eval Chat-First Workflows

`plugin-eval` should feel usable from Codex chat before a user knows any CLI flags.

## One Paved Road

If the user speaks in natural language first, use:

```bash
plugin-eval start <path> --request "<chat request>" --format markdown
```

That entrypoint recognizes the request, explains why the workflow fits, and shows the exact local command sequence behind it.

## Recommended Beginner Requests

Use these exact phrases as the paved road:

- `Give me an analysis of the game dev skill.`
- `Evaluate this skill.`
- `Evaluate this plugin.`
- `Explain the token budget for this skill.`
- `Measure the real token usage of this skill.`
- `Help me benchmark this plugin.`
- `What should I run next?`

## How Those Requests Map To Local Workflows

### Give me an analysis of the game dev skill

Start with:

```bash
plugin-eval start ~/.codex/skills/game-dev --request "give me an analysis of the game dev skill" --format markdown
plugin-eval analyze ~/.codex/skills/game-dev --format markdown
plugin-eval init-benchmark ~/.codex/skills/game-dev
plugin-eval benchmark ~/.codex/skills/game-dev --config ~/.codex/skills/game-dev/.plugin-eval/benchmark.json
```

Use this when the user wants the overall report and wants Codex to set up starter benchmark scaffolding instead of stopping after the first report.

### Evaluate this skill

Start with:

```bash
plugin-eval start <skill-path> --request "Evaluate this skill." --format markdown
plugin-eval analyze <skill-path> --format markdown
```

Use this when the user wants the overall report first.

### Explain the token budget for this skill

Start with:

```bash
plugin-eval start <skill-path> --request "Explain the token budget for this skill." --format markdown
plugin-eval explain-budget <skill-path> --format markdown
```

Use this when the question is about cost, context pressure, or why a skill feels heavy.

### Measure the real token usage of this skill

Start with:

```bash
plugin-eval start <skill-path> --request "Measure the real token usage of this skill." --format markdown
plugin-eval init-benchmark <skill-path>
plugin-eval benchmark <skill-path> --config <benchmark.json>
plugin-eval analyze <skill-path> --observed-usage <benchmark-usage.jsonl> --format markdown
plugin-eval measurement-plan <skill-path> --observed-usage <benchmark-usage.jsonl> --format markdown
```

Use this when the user wants measured usage from a real Codex run, not just the static estimate.

### Help me benchmark this plugin

Start with:

```bash
plugin-eval start <plugin-root> --request "Help me benchmark this plugin." --format markdown
plugin-eval init-benchmark <plugin-root>
plugin-eval benchmark <plugin-root> --config <benchmark.json>
```

Use this when the user wants starter scenarios or a repeatable real-Codex measurement harness.

### What should I run next?

Start with:

```bash
plugin-eval start <path> --request "What should I run next?" --format markdown
```

Use this when the user is unsure whether they should evaluate, explain a budget, benchmark, or collect measured usage next.
