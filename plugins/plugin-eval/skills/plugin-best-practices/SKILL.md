---
name: plugin-best-practices
description: Guide Codex plugin design, review, evals, and submission readiness. Use when building/reviewing plugins, designing MCP tools, planning evals, or preparing submission.
---

# Plugin Best Practices

Use this skill for concrete plugin design review, eval planning, or submission feedback.

## Workflow

1. Classify the request: design, review, MCP tool design, skill improvement, eval plan, or submission readiness.
2. Gather artifacts: manifest, skills, tool schemas/descriptions, auth, prompts, evals, and review/demo account notes.
3. Existing local plugin: use `../evaluate-plugin/SKILL.md`, run `plugin-eval analyze <plugin-root> --format markdown`, then add rubric judgment.
4. Route skill rewrites to `../improve-skill/SKILL.md`; route automated checks to `../metric-pack-designer/SKILL.md`.
5. Read `../../references/plugin-best-practices.md` for examples, eval design, auth, response guidance, or checklist work.

## Review Rubric

Check:

- App/tools: expected product actions; namespaced typed tools; structured outputs; stable IDs; annotations; separated read/write behavior.
- Context: scoped search/filter, concise human-readable data, match rationale, and actionable errors.
- Skills: terminology, tool order, inspect-before-act rules, write confirmations, summaries, and edge cases.
- Auth/safety: low drop-off, tool-level auth where possible, guest/demo reads where reasonable, and gated sensitive writes.
- Evals/submission: realistic hero prompts, expected outcomes, safety behavior, fixtures, review account, metadata, logos, and focused scope.

## Output Shape

Lead with `Verdict: Ready/Close/Needs work`, then `Fix first`, grouped gaps, and 1-3 next steps.

Be concrete. Name the tool, skill, prompt, schema field, or submission artifact that should change. If the user only provides an idea, propose a minimal v1 plugin shape before listing gaps.
