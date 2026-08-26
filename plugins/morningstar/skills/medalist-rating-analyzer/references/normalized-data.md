# Normalized `data` Schema

Read this reference only when inspecting a field in the normalized `data` dictionary. Fields are marked **[code]** when `build_data()` sets them deterministically and **[agent — Step 2b]** when they must be set from `datapoints_raw` after `build_data()` returns.

```python
data = {
    # Identifiers — [code]
    "share_class_id": "0P0000006A",   # morningstar_id used as identifier
    "morningstar_id": "0P0000006A",

    # Fund identity (list of {Attribute, Value} rows) — [code]
    "fund_info": [
        {"Attribute": "Share Class Name", "Value": "Vanguard 500 Index Fund Admiral"},
        {"Attribute": "Ticker",           "Value": "VFIAX"},
        {"Attribute": "Investment Type",  "Value": "Mutual Fund"},
        {"Attribute": "Exchange",         "Value": "..."},
        {"Attribute": "Morningstar ID",   "Value": "0P0000006A"},
        {"Attribute": "Research Published", "Value": "2025-03-15"},  # if available
        {"Attribute": "Reference URL",    "Value": "https://..."},   # if available
    ],

    # Overall rating (numeric: 2=Gold, 1=Silver, 0=Bronze, -1=Neutral, -2=Negative) — [agent — Step 2b, from MMR01]
    "overall_rating":  0,
    "rating_symbol":   "●●●◐◯",   # always via medal_symbol(overall_rating), never hand-typed
    "rating_breakdown": {
        "weighted_score":  None,        # not returned by MCP research
        "formula_text":    "",
        "derivation_text": "...",       # [code] extracted from overall_analysis content
    },

    # Historical ratings — [code] (merged from morningstar:morningstar-data-tool historical datapoints)
    "historical_ratings": [
        {
            "EndDate":                        "2026-03-31",
            "Medalist Rating":                0,            # numeric: 2=Gold … -2=Negative
            "Medalist Rating Type":           "Analyst Assigned",  # MMRMT — string or None
            "Weighted Medalist Rating Score":  -0.1432,
            "People":       0,   "People Type":  "Algorithmic",    # MMR2I — string or None
            "Process":      1,   "Process Type": "Analyst Assigned", # MMR3I — string or None
            "Parent":      -1,   "Parent Type":  "Analyst Assigned", # MMR1I — string or None
            "Price Score":  0,
        },
        # ...
    ],
    # If raw MCP historical dates do not merge (a parsing gap, not missing data), build_data() sets this — [code]:
    "historical_data_warning": None,  # or a string; fmt.historical_ratings()/full_report() surface it automatically

    # Price — medalist_price_score and price["data"] are [agent — Step 2b, from MMRGS + fee datapoints]
    "medalist_price_score": -1,
    "price": {
        "data": [],
        "text": "Price pillar narrative...",   # [code] — do not overwrite when setting "data" in Step 2b
    },

    # Pillars — "text" is [code] (analyst-research narrative); "data" is [agent — Step 2b, from MMR2E/MMR3E/MMR1E]
    "people_pillar": {
        "data":             [{"PeopleScore": 0, "PeopleScoreType": "Morningstar Data", "EndDate": ""}],
        "algorithmic_data": [],
        "text":             "People pillar narrative...",
    },
    "process_pillar": {
        "data":             [{"ProcessScore": 1, "ProcessScoreType": "Morningstar Data", "EndDate": ""}],
        "algorithmic_data": [],
        "text":             "Process pillar narrative...",
    },
    "parent_pillar": {
        "data":             [{"ParentScore": -1, "ParentScoreType": "Morningstar Data", "EndDate": ""}],
        "algorithmic_data": [],
        "text":             "Parent pillar narrative...",
    },

    # MCP metadata — [code]
    "source":        "mcp",
    "published_at":  "2025-03-15T00:00:00Z",
    "reference_url": "https://www.morningstar.com/...",
    "error":         None,

    # Fund attribute flags — [code]. They drive select_formula() and mandatory disclosure handling.
    "domicile_country":                 "United States",  # LS017: fund domicile country
    "is_australian_domicile":           False,              # derived from LS017 (True for AUS/Australia)
    "is_index_fund":                    False,  # OF00C: True if fund is an index fund
    "is_australian_superannuation_fund": False, # OS280: True if Australian super fund
    "investment_type":                  "Open-end mutual funds",  # LS466: investment vehicle type
    "disclosure_type":                  None,   # CNAXS: "Issuer Initiated Rating", "Tracks Morningstar Index", or None
}
```
