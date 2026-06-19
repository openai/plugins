---
name: imagegen-cli
description: Run the API-backed ImageGen CLI. Use when the user explicitly asks for CLI, API, model selection, masks, direct output controls, batch JSONL jobs, or accepts the true-transparency fallback. Do not trigger for ordinary image requests. Requires OPENAI_API_KEY for live calls.
---

# ImageGen CLI

Use the bundled `scripts/image_gen.py` only after the user explicitly chooses the CLI/API path. Do not silently route ordinary image requests here.

## Preconditions

- Require `OPENAI_API_KEY` for live generation or editing.
- A dry run needs neither the key nor the OpenAI package.
- Ask before moving from built-in `image_gen` or CLI `gpt-image-2` to `gpt-image-1.5`, unless the user already requested that model or confirmed the true-transparency fallback.
- Never modify `scripts/image_gen.py` during an image task. If a needed feature is absent, explain the gap.

## Workflow

1. Resolve `scripts/image_gen.py` relative to this `SKILL.md`; do not assume a fixed installation directory.
2. Read [cli.md](references/cli.md) for commands and supported options.
3. Read [image-api.md](references/image-api.md) for model-specific parameter constraints.
4. Read [codex-network.md](references/codex-network.md) only when network policy or sandboxing blocks an API call.
5. Use `generate`, `edit`, or `generate-batch` as appropriate.
6. Write project deliverables under `output/imagegen/` unless the user named another workspace path.
7. Validate the output and report the final path, prompt, model, and key execution settings.

## Defaults and boundaries

- Default model: `gpt-image-2`
- Default quality: `medium`
- Default size: `auto`
- Default format: `png`
- Use one prompt per distinct batch asset; reserve `n` for variants of one prompt.
- Do not pass `input_fidelity` or `background=transparent` to `gpt-image-2`.
- Use `gpt-image-1.5 --background transparent --output-format png` only for a user-confirmed native-transparency fallback.
- Do not create a one-off SDK wrapper when the bundled CLI can perform the task.

Before a live request, use `--dry-run` when it helps verify payload, output paths, or model constraints without spending API resources.
