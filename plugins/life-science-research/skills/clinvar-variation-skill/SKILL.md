---
name: clinvar-variation-skill
description: Submit compact ClinVar Clinical Tables and NCBI Variation requests for search, VCV, RCV, SCV, and RefSNP lookups. Use when a user wants variant-level summaries or identifier mapping
---

## Operating rules
- Use `scripts/clinvar_variation.py` for all ClinVar and NCBI Variation work.
- The script accepts `max_items`; for `action=search`, start around `max_items=10`.
- For `vcv`, `rcv`, `scv`, and `refsnp`, omit `max_items` unless you need to trim nested arrays in the summary.
- Re-run requests in long conversations instead of relying on prior tool output.
- Treat displayed `...` in tool previews as UI truncation, not literal request content.
- If the user asks for full JSON, set `save_raw=true` and report the saved file path instead of pasting large payloads into chat.

## Execution behavior
- Return concise markdown summaries from the script JSON by default.
- Return the JSON verbatim only if the user explicitly asks for machine-readable output.
- Use `action=search` for the Clinical Tables endpoint.
- Use `action=vcv|rcv|scv|refsnp` for NCBI Variation beta objects.

## Input
- Read one JSON object from stdin.
- Required field: `action`
- Action-specific required fields:
  - `search`: `terms`
  - `vcv`: `vcv`
  - `rcv`: `rcv`
  - `scv`: `scv`
  - `refsnp`: `refsnp`
- Optional fields: `params`, `max_items`, `max_depth`, `timeout_sec`, `save_raw`, `raw_output_path`

## Output
- `search` returns `total`, `identifiers`, `display_rows`, `extra_fields`, and truncation metadata.
- `vcv|rcv|scv|refsnp` return a compact `summary` and optional `top_keys`.
- Use `raw_output_path` when `save_raw=true`.
- Failures return `ok=false` with `error.code` and `error.message`.

## Execution
```bash
echo '{"action":"search","terms":"VCV000013080","max_items":10}' | python scripts/clinvar_variation.py
```

## References
- No additional runtime references are required; keep the import package limited to this file and `scripts/clinvar_variation.py`.
