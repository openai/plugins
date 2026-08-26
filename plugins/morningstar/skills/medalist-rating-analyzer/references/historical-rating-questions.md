# Historical, Dated, and Rating-Change Questions

Use this reference for questions about how the Medalist Rating or a People, Process, Parent, or Price pillar changed over time; questions with a date range; or requests to explain a rating change.

## Contents

- [Historical Rating and Pillar Requests](#historical-rating-and-pillar-requests)
- [Rating Change Explanation Questions](#rating-change-explanation-questions)
- [Date Range Filtering](#date-range-filtering)

## Historical Rating and Pillar Requests

- **If historical rating data is already in context,** call `fmt.historical_ratings(data)` (or `fmt.full_report(data)` for the full breakdown). Never hand-copy, retype, or reconstruct the table from memory or raw JSON, even for a short history: the formatter is the only path that preserves every row and every type label exactly.
- **If historical rating data is not in context,** read `full-workflow.md` (linked directly from `SKILL.md`), then call `morningstar:morningstar-data-tool` with the fund's `morningstar_id` and `MMR00`, `MMR1H`, `MMR2H`, `MMR3H`, `MMRGS`, `MMRMT`, `MMR1I`, `MMR2I`, and `MMR3I`. Pass the result through `build_data()` and `fmt.historical_ratings()`; never manually retype raw tool output.
- If `data["historical_data_warning"]` is present, `fmt.historical_ratings()` and `fmt.full_report()` display it automatically. Do not suppress or omit it.

## Rating Change Explanation Questions

1. Use quantitative methodology:
   - Use historical pillar values plus price/fee changes.
   - Call `select_formula(domicile_country, is_index_fund, is_australian_superannuation_fund)` and use its return value, then call `morningstar:morningstar-articles-tool` with `content_filter: "methodology"` and apply that formula.
   - Show a quantitative assessment of each component's direction and contribution, not only a qualitative narrative.
2. Apply the legacy-period rule for ratings from before the current methodology's effective date:

   <details>
   <summary>Current cutoff: April 2026 (a hardcoded date—see maintenance note)</summary>

   The weighted quantitative formula applies only to ratings assigned under the current methodology, effective **April 2026**. For rating changes before that date:
   - They cannot be fully explained with the current methodology.
   - If analyst research discusses a specific pre-cutoff change, include that research-based explanation instead of the general response below.
   - If there is no pillar rating change at the same time, use exactly: "The rating calculation before April 2026 was different from the current methodology. I do not have access to the previous methodology at this moment to explain in detail."

   **Maintenance note:** This is a hardcoded date, not a self-updating rule. Revisit it whenever the methodology changes; otherwise, a stale cutoff can incorrectly classify changes as legacy.
   </details>

## Date Range Filtering

Every time-series formatter method accepts optional `start_date` and `end_date` keyword arguments.

| What the user says | How to call |
|--------------------|-------------|
| "since January 2022" | `start_date="January 2022"` |
| "from June 2020 to December 2022" | `start_date="June 2020", end_date="December 2022"` |
| "in 2021" | `start_date="2021-01-01", end_date="2021-12-31"` |
| "up to 2023" | `end_date="2023"` |

All of the following accept `start_date` and `end_date`:

- `fmt.historical_ratings(data, start_date=..., end_date=...)`
- `fmt.overall_rating(data, start_date=..., end_date=...)`
- `fmt.price_score(data, start_date=..., end_date=...)`
- `fmt.people_pillar(data, start_date=..., end_date=...)`
- `fmt.process_pillar(data, start_date=..., end_date=...)`
- `fmt.parent_pillar(data, start_date=..., end_date=...)`
- `fmt.full_report(data, start_date=..., end_date=...)` — filters every section

**Show rating history since January 2024:**

```python
import sys, io
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
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from formatter import Formatter

fmt = Formatter()
# data is already in context
header = fmt.fund_header(data)
body = fmt.historical_ratings(data, start_date="January 2024")
output = header + "\n\n" + body if header else body
print(output)
```
