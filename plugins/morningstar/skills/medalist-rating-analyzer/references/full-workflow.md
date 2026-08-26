## Contents

- [Prerequisites](#prerequisites)
- [Step-by-Step Workflow](#step-by-step-workflow) — Step 1 (resolve fund), Step 2 (fetch + `build_data()`), Step 2b (populate current-snapshot values), Step 3 (mandatory pre-response verification), Datapoint IDs reference, historical-data rules
- [Behavior Rules](#behavior-rules) — fetch-once, investment-type coverage check, disclosure handling, off-topic
- [Error Reference](#error-reference)

---

## Prerequisites

None required. `scripts/formatter.py` uses `python-dateutil` for flexible date parsing when it's available, and falls back to a built-in parser (covering ISO, US, and common natural-language date formats) when it isn't — no install step is needed either way.

---

## Step-by-Step Workflow

Copy this checklist and track your progress on every new fund fetch — Step 2b is easy to skip because it isn't inside `build_data()`, and skipping it silently produces a report with no current Medalist Rating or pillar scores:

```
Fund Fetch Progress:
- [ ] Step 1: Resolve fund to a morningstar_id
- [ ] Step 2: Call all three MCP tools, build `data` via build_data()
- [ ] Step 2b: Populate current-snapshot values into `data` yourself (medal, pillar scores, price, fees)
- [ ] Step 3: Run the mandatory Pre-Response Verification checklist before replying
```

### Step 1 — Resolve the fund to a morningstar_id

The host agent calls `morningstar:morningstar-id-lookup-tool` and passes the result here.

```python
# lookup_results is provided by the host agent from morningstar:morningstar-id-lookup-tool.
# Shape: [{"morningstar_id": "...", "investment_name": "...", "ticker": "...", ...}]

if not lookup_results:
    print(
        "No funds found. Please try the exact ticker, full legal name, or Morningstar ID."
    )

elif len(lookup_results) == 1:
    r = lookup_results[0]
    ticker = f" ({r['ticker']})" if r.get("ticker") else ""
    print(f"Found: {r['investment_name']}{ticker}  |  ID: {r['morningstar_id']}")
    # ONE result — proceed directly to Step 2 with r['morningstar_id']

else:
    # MULTIPLE results — show numbered list and STOP; wait for user to choose
    print("Multiple funds found. Please select one by entering its number:\n")
    for i, r in enumerate(lookup_results, 1):
        ticker = f" ({r['ticker']})" if r.get("ticker") else ""
        itype = r.get("investment_type", "")
        exch = r.get("exchange", "")
        meta = " | ".join(filter(None, [itype, exch]))
        print(
            f"  {i}. {r['investment_name']}{ticker}  —  {meta}  |  ID: {r['morningstar_id']}"
        )
    print("\nEnter the number of the fund you want to analyze.")
    # STOP HERE — do not proceed to Step 2 until the user replies with their selection
```

- **One result** → proceed directly to Step 2 with that `morningstar_id`
- **Multiple results** → display the numbered list, ask the user to choose, **then wait** — do not fetch until the user replies
- **User gives a Morningstar ID directly** → skip to Step 2

---

### Step 2 — Fetch and normalize fund data

**Preserve immutable formatter blocks.** Reproduce any Disclosure block and formatter-generated table verbatim, including every occurrence and its position. Do not rewrite, summarize, reformat, or restructure those blocks. You may add agent-authored text only where this workflow expressly requires it, such as ambiguity handling, no-result responses, comparisons, pillar-input tables, or rating-change explanations.

The host agent calls all three MCP tools and passes the raw payloads to `build_data()`.

**Important:**
  Use `morningstar:morningstar-data-tool` for historical ratings and pillar timelines.
  The historical datapoint IDs are `MMR00` for overall Medalist Rating, `MMR1H` for Parent, `MMR2H` for People, `MMR3H` for Process, and `MMRGS` for Price.
  The rating/pillar assignment-type IDs are `MMRMT` for overall rating type, `MMR1I` for Parent type, `MMR2I` for People type, and `MMR3I` for Process type.
  Do not attempt to parse historical pillar scores from analyst research text or current datapoints.

| # | MCP Tool (called by host agent) | Purpose |
|---|---------------------------------|---------|
| 1 | `morningstar:morningstar-id-lookup-tool` (with `datapoints`) | Discover datapoint IDs for current rating, pillars, fees |
| 2 | `morningstar:morningstar-analyst-research-tool` | Fetch analyst narrative text for all pillars |
| 3 | `morningstar:morningstar-data-tool` (current + historical IDs) | Fetch structured current values, fees, and historical monthly overall + pillar timelines |

```python
import sys
import io
import glob, os

sys.path.insert(
    0,
    next(
        (
            p
            for p in [
                "skills/medalist-rating-analyzer/scripts",
                *glob.glob(".remote-plugins/*/skills/medalist-rating-analyzer/scripts"),
            ]
            if os.path.isdir(p)
        ),
        "skills/medalist-rating-analyzer/scripts",
    ),
)

# Set UTF-8 encoding for stdout (required on Windows for Unicode symbols like ≥, ×)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from data_normalizer import build_data
from formatter import Formatter

# All raw payloads are provided by the host agent:
#   lookup        — dict from morningstar:morningstar-id-lookup-tool (the chosen result)
#   research_raw  — dict from morningstar:morningstar-analyst-research-tool
#   datapoints_raw — dict from morningstar:morningstar-data-tool (current datapoints)
#   history_raw   — dict from morningstar:morningstar-data-tool (historical: MMR00/MMR1H/MMR2H/MMR3H/MMRGS)

morningstar_id = lookup["morningstar_id"]  # from Step 1

data = build_data(
    lookup=lookup,
    research_raw=research_raw,
    datapoints_raw=datapoints_raw,
    history_raw=history_raw,
    morningstar_id=morningstar_id,
)

fmt = Formatter()

# Check for errors
if isinstance(data, dict) and data.get("error"):
    print("Error: " + str(data["error"]))
else:
    investment_type = data.get("investment_type")
    # is_covered: semantic match against the 7 covered types — see "Investment type
    # coverage check" in Behavior Rules for the full list and matching rules.
    is_covered = ...

    if not is_covered:
        # Fund is not covered - show basic info and friendly message
        fund_info = data.get("fund_info", [])
        print("This fund is not covered by current Morningstar Medalist Rating.\n")
        print("Fund Information:")
        for item in fund_info:
            if isinstance(item, dict):
                attr = item.get("Attribute", "")
                val = item.get("Value", "")
                if (
                    attr
                    in [
                        "Share Class Name",
                        "Ticker",
                        "Morningstar ID",
                        "Investment Type",
                    ]
                    or attr == "Domicile"
                ):
                    print(f"  {attr}: {val}")
    else:
        # Fund is covered - show full report
        # Note: Disclosure is automatically handled by fmt.full_report() based on data['disclosure_type']
        header = fmt.fund_header(data)
        body = fmt.full_report(data)
        output = header + "\n\n" + body if header else body
        print(output)
```

**Check for truncation before using this output.** A cut-off bash capture is easy to miss silently. Inspect the tail of stdout (e.g. `tail -c 100` on the captured output) and confirm it ends with a complete sentence or the final section's closing content — not mid-word or mid-sentence. If it's truncated, re-run with a higher output limit before continuing.

### Step 2b — Populate current-snapshot values (your responsibility, not `build_data()`)

`build_data()` deliberately only fills in two categories of field:
1. **Routing/compliance flags** (`domicile_country`, `is_index_fund`, `is_australian_superannuation_fund`, `investment_type`, `disclosure_type`) — these gate `select_formula()` and the mandatory disclosure text, so they stay code.
2. **Historical time series** — pivoting hundreds of raw values by date is exact bookkeeping, so it stays code (`extract_historical_rows`/`merge_historical_rows`).

It does **not** fill in the *current* Medalist Rating, current pillar scores, price score, or fees. Those are a handful of simple 1:1 lookups from a small, stable datapoint-ID table, and you read them directly from the already-fetched `datapoints_raw` response — there's no code transformation step to call for these.

Immediately after `build_data()` returns, before calling any formatter method, read these IDs out of `datapoints_raw` and set them into `data` yourself:

| Datapoint ID | Set into `data[...]` |
|---|---|
| `MMR01` (Medalist Rating) | `overall_rating_raw` = the raw value (e.g. `"Gold"`); `overall_rating` = the mapped int (Gold=2, Silver=1, Bronze=0, Neutral=-1, Negative=-2); `rating_symbol` = `medal_symbol(overall_rating)` from `scripts/data_normalizer.py` — **always call this helper, never hand-type the dot symbol string** |
| `MMR2E` (People Pillar) | `people_pillar["data"] = [{"PeopleScore": <value>, "PeopleScoreType": "Morningstar Data", "EndDate": ""}]` |
| `MMR3E` (Process Pillar) | `process_pillar["data"]` — same shape, key `ProcessScore`/`ProcessScoreType` |
| `MMR1E` (Parent Pillar) | `parent_pillar["data"]` — same shape, key `ParentScore`/`ParentScoreType` |
| `MMRGS` (Price Pillar) | `medalist_price_score` = the raw value |
| Annual fee / category median fee | No fixed ID exists for these in this integration — match by the `datapointName` the lookup-discovery step returned (containing "fee" or "expense"), then set `price["data"] = [{"AnnualFee": ..., "CategoryMedianAnnualFee": ..., "FeeType": "Annual", "EndDate": ""}]` |

Rules for this step:
- **Preserve, don't clobber:** `people_pillar`/`process_pillar`/`parent_pillar`/`price` already have a `text` field from the narrative research — only set `data`, never overwrite `text`.
- **Strip the `^Q` suffix** (e.g. `"High^Q"`) before displaying a pillar value — it marks a quantitative/algorithmic assignment, it isn't part of the label.
- This is current/latest-snapshot only — it has nothing to do with the historical time series, which `build_data()` already populated.

**`data` now contains everything.** Keep it in context for all follow-up questions.

**How the tools contribute:**
- `morningstar:morningstar-id-lookup-tool` (with `datapoints=["Morningstar Medalist Rating", "People Pillar", ...]`) discovers the datapoint IDs needed by `morningstar:morningstar-data-tool`.
- Confirmed current IDs: `MMR01` = Medalist Rating, `MMR2E` = People Pillar, `MMR3E` = Process Pillar, `MMR1E` = Parent Pillar, `MMRGS` = Price Pillar.
- `morningstar:morningstar-analyst-research-tool` provides narrative text for each pillar section (People, Process, Parent, Price, overall analysis).
- `morningstar:morningstar-data-tool` returns structured current values — medal (Gold/Silver/Bronze/Neutral/Negative), current pillar scores (-2 to +2), fees, and historical overall/pillar timelines. Current-snapshot values are read and applied by you per Step 2b above; historical values are merged by `build_data()` and are authoritative over any text-derived estimate.

### Step 3 — Verify before responding

**Mandatory gate — do not send the response until every item below is checked.** This is a hard stop between generating output and replying, not an optional review.

```
Pre-Response Verification:
- [ ] Output ends cleanly — no mid-word or mid-sentence truncation (see the truncation check in Step 2)
- [ ] Historical ratings table (if the question calls for one) is present in full, every row
- [ ] Disclosure appears exactly as many times as it does in the formatter output, in the same positions — not collapsed, not duplicated
- [ ] Disclosure blocks and formatter-generated tables are unchanged; any authored text is required by this workflow
```

If any item fails, fix it before responding — re-run the formatter call, don't hand-patch the text.

### Datapoint IDs (reference: `scripts/data_normalizer.py`)

Use these IDs when reasoning about current vs historical pillar scores:

| Metric                                      | Datapoint ID | Source |
|---------------------------------------------|--------------|--------|
| Medalist Rating (overall, current)          | `MMR01` | `morningstar:morningstar-data-tool` |
| People Pillar (current)                     | `MMR2E` | `morningstar:morningstar-data-tool` |
| Process Pillar (current)                    | `MMR3E` | `morningstar:morningstar-data-tool` |
| Parent Pillar (current)                     | `MMR1E` | `morningstar:morningstar-data-tool` |
| Price Pillar (current)                      | `MMRGS` | `morningstar:morningstar-data-tool` |
| Historical overall Medalist Rating timeline | `MMR00` | `morningstar:morningstar-data-tool` |
| Historical Parent pillar timeline           | `MMR1H` | `morningstar:morningstar-data-tool` |
| Historical People pillar timeline           | `MMR2H` | `morningstar:morningstar-data-tool` |
| Historical Process pillar timeline          | `MMR3H` | `morningstar:morningstar-data-tool` |
| Historical Price pillar timeline            | `MMRGS` | `morningstar:morningstar-data-tool` |
| Historical overall Medalist Rating Type     | `MMRMT` | `morningstar:morningstar-data-tool` |
| Historical Process Pillar Type              | `MMR3I` | `morningstar:morningstar-data-tool` |
| Historical People Pillar Type               | `MMR2I` | `morningstar:morningstar-data-tool` |
| Historical Parent Pillar Type               | `MMR1I` | `morningstar:morningstar-data-tool` |
| Fund Domicile Country                       | `LS017` | `morningstar:morningstar-data-tool` |
| Is Index Fund                               | `OF00C` | `morningstar:morningstar-data-tool` |
| Is Australian Superannuation Fund           | `OS280` | `morningstar:morningstar-data-tool` |
| Investment Type                             | `LS466` | `morningstar:morningstar-data-tool` |
| Disclosure Type                             | `CNAXS` | `morningstar:morningstar-data-tool` |

Rule: use `morningstar:morningstar-data-tool` for all historical rating questions (overall + pillars).

> **Rating formula selection (domicile-aware):** This is a deterministic lookup, not a judgment call — never reason it out in prose. Call `select_formula(data["domicile_country"], data["is_index_fund"], data["is_australian_superannuation_fund"])` from `scripts/data_normalizer.py`. It returns `"Active"`, `"Passive"`, `"Superannuation"`, or `"clarification_needed"`. If it returns `"clarification_needed"`, use the exact clarification wording produced by `Formatter.routing_flags()` in `scripts/formatter.py` — that is the single canonical source for that sentence; do not compose your own.

**Don't** use current datapoints or `fmt.*` current-value methods alone to answer historical People/Process/Parent pillar timeline questions — read `historical-rating-questions.md` (linked directly from `SKILL.md`) for the canonical historical ID set and response rules.

### MCP historical datapoint request contract

Use this MCP JSON-RPC request shape for historical ratings:

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "morningstar:morningstar-data-tool",
    "arguments": {
      "investment_ids": ["FOUSA00L8W"],
      "datapoint_ids": ["MMR00", "MMR1H", "MMR2H", "MMR3H", "MMRGS", "MMRMT", "MMR3I", "MMR2I", "MMR1I"],
      "start_date": "2025-01-01",
      "end_date": "2026-01-01"
    }
  }
}
```

Default date range when the user does not supply one:
- `end_date` = last month-end relative to today
- `start_date` = 3 years before `end_date`

---

## Behavior Rules

- **Fetch once, answer many.** After Step 2 succeeds, answer all follow-up questions about the same fund from `data` — never re-fetch for the same fund in the same session.
- **Investment type coverage check.** After fetching fund data, evaluate whether `data["investment_type"]` semantically matches one of these 7 covered vehicle types: (1) Open-end mutual funds, (2) ETFs, (3) Separate accounts, (4) Model portfolios, (5) Variable annuity/life subaccounts, (6) Collective Investment Trusts (CITs), (7) Australian superannuation vehicles. Use meaning-based matching (consider abbreviations, singular/plural, case variations). If the fund is NOT covered, show only basic fund information (name, ticker, security id, domicile country, and investment type) with the message: "This fund is not covered by current Morningstar Medalist Rating." Do not show rating or pillar analysis for uncovered types. If investment_type is missing/None, assume the fund IS covered.
- **Show complete output.** Never truncate or summarize formatter output — return it in full.
- **Complete analysis includes all narrative text.** When generating a full analysis (`fmt.full_report(data)`), the response **must** contain every narrative text field present in `data`:
  - `data["rating_breakdown"]["derivation_text"]` — overall analysis narrative
  - `data["price"]["text"]` — price score narrative
  - `data["people_pillar"]["text"]` — People pillar narrative
  - `data["process_pillar"]["text"]` — Process pillar narrative
  - `data["parent_pillar"]["text"]` — Parent pillar narrative
- **Fund switched.** When the user asks about a different fund, run Steps 1 and 2 again for the new fund. Replace `data` with the new response.
- **No results from lookup.** Ask the user to try the exact ticker, full legal name, or Morningstar ID.
- **MCP server unreachable.** Inform the user clearly — there is no offline fallback.
- **Historical MCP datapoints unreachable.** Continue with current MCP-derived data and clearly say historical pillar score history may be incomplete.
- **Empty research results.** If `morningstar:morningstar-analyst-research-tool` returns no results, pass an empty `research_raw` to `build_data()`; inform the user the full analyst research is not available.
- **Disclosure handling.** The formatter automatically handles disclosure display. When `data["disclosure_type"]` is "Issuer Initiated Rating" or "Tracks Morningstar Index", `fmt.full_report()` automatically prepends the appropriate disclosure text at the beginning of the output with separator lines. No manual disclosure handling is needed.
- **Off-topic.** Respond: *"I specialize in Morningstar Medalist Rating analysis. Ask me about a fund by name, ticker, or Morningstar ID."*
- **include the fund name and ticker in all responses** to avoid confusion when the user is asking about multiple funds in the same session.
- **disclosure text** When summarizing, always keep the original disclosure text if present, do not shorten it. Keep the fund name and ticker in the summary.
## Error Reference

| Condition | Cause | Agent response |
|-----------|-------|----------------|
| `lookup_results` is empty list | Ticker/name not in Morningstar DB | Ask user for exact ticker, full legal name, or Morningstar ID |
| `research_raw` has empty results | Fund has no analyst research | Pass empty payload to `build_data()`; inform user analyst research is not available |
