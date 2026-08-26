---
name: medalist-rating-analyzer
description: Analyzes a fund's Morningstar Medalist Rating using live Morningstar MCP data, including pillar scores, rating history, and analyst research. Use when asked to rate, analyze, or look up a specific fund by ticker, name, or Morningstar ID.
---

# Medalist Rating Analyzer

Analyzes Morningstar Medalist Ratings using the **Morningstar MCP server**.
Includes only two steps:

1. **Search** — resolve a fund name or ticker to a `morningstar_id`
2. **Fetch** — call the MCP server once to get all research/rating data for that fund

Do not call MCP tools if you have already fetched the same data for the same `morningstar_id` in the same session — keep it in context and answer all follow-up questions from that data.
Do not expose Morningstar internal data id values (e.g., `MMR01`) in your final answers — those are for your internal use only when reasoning about which data to pull and how to answer.
Do not expose internal routing/decision logic for choosing a rating formula. Keep that reasoning private unless the user explicitly asks methodology details.

---

## Plugin Domain Rules

Morningstar domain rules for this skill:

- For fund lookups by name/ticker, call `morningstar:morningstar-id-lookup-tool` first.
- When calling `morningstar:morningstar-id-lookup-tool`, pass only the fund identifier text (ticker, exact Morningstar ID, or fund name), not the full user sentence.
- If the user provides a direct Morningstar ID, skip lookup and proceed directly to the fetch workflow with that ID.
- When MCP-backed formatter output contains a "Disclosure" section with separator lines (────), you MUST reproduce that disclosure text EXACTLY AS PROVIDED in the tool output, word-for-word, without paraphrasing, summarizing, or omitting any sentences. **If it appears more than once in the formatter output, reproduce it that many times, in the same positions — never collapse repeated occurrences into one.** The disclosure text is legally required and must be complete and verbatim.
- **Disclosure handling — never add manually.** `fmt.full_report()` and `fmt.fund_header()` handle all disclosure placement automatically based on `data["disclosure_type"]`. Do NOT write or append a disclosure block yourself anywhere in the response. If you find yourself typing the disclosure text, stop — that means the formatter already placed it.
- If the needed fund data is already provided in session context, answer follow-up questions about the same fund directly and do not call Morningstar MCP data tools again unless the user asks about a different fund.
- When presenting historical pillar score output from `morningstar:morningstar-data-tool`, do NOT omit any rating type labels (e.g. `Analyst Assigned`, `Algorithmic`, `Quantitative`). The type labels must appear in your response exactly as they appear in the tool output.
- For comparison requests, fetch each fund, then synthesize a comparison.
- Never invent fund data; rely on tool output and provided context.
- Show complete relevant tool-backed output; do not provide empty sections.
- Avoid fenced code blocks in user-facing answers; write formulas as plain text.
- If a tool explicitly returns an MCP-service-unavailable error, respond exactly: "Sorry, the Morningstar MCP service is not available at this moment. Please try again later."
- Do not infer MCP outage from user text or model assumptions; only use the outage response when a tool call indicates service unavailability.

### Routing logic for fund-specific methodology questions

- Keep formula-routing logic internal unless the user explicitly asks for methodology details.
- This is a deterministic decision, not a judgment call — never re-derive it by reasoning over the flags in prose. Call `select_formula(domicile_country, is_index_fund, is_australian_superannuation_fund)` from `scripts/data_normalizer.py` (also exported as `scripts.select_formula`) and use its return value directly: `"Active"`, `"Passive"`, `"Superannuation"`, or `"clarification_needed"`.
- Use routing flag values injected in the current-fund context block (domicile_country, is_index_fund, is_australian_superannuation_fund) — these come directly from the data tool. Do NOT infer or default missing values before passing them to `select_formula`.
- If the result is `"clarification_needed"`, follow the clarification instruction in the routing flags block (`Formatter.routing_flags()` in `scripts/formatter.py`) — that is the single canonical source for the exact clarification wording.

---

## Data Source — Morningstar APIs

Data comes from Morningstar MCP.

Three MCP tools are used:

| Tool | Purpose |
|------|---------|
| `morningstar:morningstar-id-lookup-tool` | Resolve ticker / name → `morningstar_id` |
| `morningstar:morningstar-analyst-research-tool` | Fetch analyst research, pillar narratives, and Medalist Rating |
| `morningstar:morningstar-data-tool` | Supplement with structured datapoints (current rating/pillars, fees, historical overall + pillar timelines) |

**If the MCP server is unreachable, inform the user.**

---

## Reference Files

Read only the reference required for the request. Every reference below is one hop from this file.

| Situation | Read |
|-----------|------|
| A new fund, a different fund, or no current-fund `data` in session | [references/full-workflow.md](references/full-workflow.md) — lookup, fetch, normalization, current snapshot, and pre-response workflow |
| A standard question about a fetched fund: full report, current rating, price/fees, a current pillar, or fund identity | [references/follow-up-questions.md](references/follow-up-questions.md) — formatter routing and follow-up examples |
| A historical rating/pillar question, a date-bounded question, or an explanation of a rating change | [references/historical-rating-questions.md](references/historical-rating-questions.md) — history IDs, date filtering, and change-explanation rules |
| How a current Parent, People, or Process pillar is calculated | [references/pillar-input-questions.md](references/pillar-input-questions.md) — the input-data retrieval workflow |
| The precise shape or ownership of a normalized `data` field | [references/normalized-data.md](references/normalized-data.md) — complete `data` schema |
| The input datapoint-ID table or `get_pillar_data_id` usage details | [references/pillar_rating_input_data.md](references/pillar_rating_input_data.md) or [references/pillar_data_query_reference.md](references/pillar_data_query_reference.md) |

For a general Medalist Rating methodology question that is not tied to a specific fund, use `morningstar:morningstar-articles-tool` with `content_filter: "methodology"`; do not load a fund workflow reference.

Executable code lives in `scripts/` (`data_normalizer.py`, `formatter.py`, `pillar_data_query.py`) — import and call these, don't read them as documentation; the reference files above are the documentation.
