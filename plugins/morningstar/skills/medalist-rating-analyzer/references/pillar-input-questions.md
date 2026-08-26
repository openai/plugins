# Current Pillar Input Questions

Use this reference only when the user asks how a current Parent, People, or Process pillar score/rating is calculated for a specific fund.

1. Ensure the fund has been resolved and fetched before retrieving pillar-input datapoints. If it is not, read `full-workflow.md` (linked directly from `SKILL.md`) first.
2. If the pillar is **People** and the fund is **passive-managed**, answer directly from **Passive People** in the Core Methodology. Do not look up an input data ID or value.
3. Otherwise, use `get_pillar_data_id(pillar, manage_type)` from `scripts/pillar_data_query.py` to load the requested pillar and management-type IDs (`is_index_fund`: `True` → `"passive"`; `False` → `"active"`). For **Process**, call both `get_pillar_data_id("process", "active")` and `get_pillar_data_id("process", "passive")`, then merge the results. Do not branch on `is_index_fund` or ask the user to choose.
4. Call `morningstar:morningstar-data-tool` once with those datapoint IDs and the fund's `morningstar_id`.
5. Render individual datapoint values only—no total, sum, or aggregate row—and use `N/A` for missing values:

| Name | Latest Value |
|------|--------------|

This is current/latest data only. For timelines, read `historical-rating-questions.md` (linked directly from `SKILL.md`).
