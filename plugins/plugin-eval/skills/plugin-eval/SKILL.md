---
name: plugin-eval
description: Help engineers evaluate a local skill or plugin, explain why it scored that way, show what to fix first, measure real token usage, benchmark starter scenarios, or decide what to run next. Use when the user says things like "evaluate this skill", "give me an analysis of the game dev skill", "why did this score that way", "what should I fix first", "measure the real token usage of this skill", or "what should I run next?".
---

# Plugin Eval

Use this as the beginner-friendly umbrella entrypoint for local Codex skill and plugin evaluation.

## Start Here

1. Resolve whether the target path is a skill, a plugin, or another local folder.
2. Prefer the chat-first router when the user speaks naturally or is not sure which command they need:

```bash
plugin-eval start <path> --request "<user request>" --format markdown
```

3. Route natural chat requests to the matching workflow:
   - "Give me an analysis of the game dev skill." -> resolve the named skill path, run `plugin-eval analyze <path> --format markdown`, then initialize a benchmark and show the setup questions needed to tailor `benchmark.json`
   - "Evaluate this skill." -> `plugin-eval analyze <path> --format markdown`
   - "Why did this score that way?" -> `plugin-eval analyze <path> --format markdown`
   - "What should I fix first?" -> `plugin-eval analyze <path> --format markdown`
   - "Explain the token budget for this skill." -> `plugin-eval explain-budget <path> --format markdown`
   - "Measure the real token usage of this skill." -> benchmark flow, then `plugin-eval measurement-plan`
   - "Help me benchmark this plugin." -> starter benchmark flow
   - "What should I run next?" -> `plugin-eval start <path> --request "What should I run next?" --format markdown`
4. If the user wants rewrite help after evaluation, route to `../improve-skill/SKILL.md`.
5. If the user wants a custom rubric, route to `../metric-pack-designer/SKILL.md`.
6. If the user names a skill instead of giving a path, resolve it locally before running commands:
   - check `~/.codex/skills/<skill-name>` first
   - then check any repo-local `skills/<skill-name>` directory
   - if the name is still ambiguous, ask one short clarifying question before continuing
7. When the request sounds like "analysis" rather than just "evaluate", do the fuller path:
   - run the report
   - initialize `.plugin-eval/benchmark.json`
   - surface the setup questions that will refine the starter scenarios
   - preview the dry-run command the user can execute next

## Chat Requests To Recognize

- `Give me an analysis of the game dev skill.`
- `Evaluate this skill.`
- `Evaluate this plugin.`
- `Why did this score that way?`
- `What should I fix first?`
- `Explain the token budget for this skill.`
- `Measure the real token usage of this skill.`
- `Help me benchmark this plugin.`
- `What should I run next?`

## Matching Commands

```bash
plugin-eval start <path> --request "Evaluate this skill." --format markdown
plugin-eval start <path> --request "Give me a full analysis of this skill, including benchmark setup." --format markdown
plugin-eval analyze <path> --format markdown
plugin-eval explain-budget <path> --format markdown
plugin-eval measurement-plan <path> --format markdown
plugin-eval init-benchmark <path>
plugin-eval benchmark <path> --dry-run
plugin-eval benchmark <path>
```

## Output Expectations

- Prefer the JSON result as the source of truth.
- Lead with `At a Glance`, `Why It Matters`, `Fix First`, and `Recommended Next Step`.
- Keep the `why` content terse and easy to skim.
- Call out whether budget numbers are static estimates or measured harness results.
- Show the user the exact chat phrase they can reuse next, the `plugin-eval start` command that routes it, and the first local workflow command behind it.
- When the user asks for an analysis of a named skill, do not stop at the report if benchmark setup is still missing.
- When the user is asking about a skill specifically, hand off to `../evaluate-skill/SKILL.md`.
- When the user is asking about a plugin bundle, hand off to `../evaluate-plugin/SKILL.md`.

## References

- `../../references/chat-first-workflows.md`
- `../../references/technical-design.md`
- `../../references/evaluation-result-schema.md`
