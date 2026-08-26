"""
Data Normalizer

Converts raw Morningstar MCP server responses into the structured ``data``
dict that formatter.py already consumes.

Main entry points:
    from data_normalizer import normalize, supplement_with_datapoints, build_data

    # Low-level (step-by-step):
    data = normalize(lookup_result, research_raw, morningstar_id)
    data = supplement_with_datapoints(data, datapoints_raw, datapoint_ids=ids_map)
    merge_historical_rows(data, history_rows)

    # High-level (all pre-fetched payloads at once):
    data = build_data(lookup, research_raw, datapoints_raw, history_raw, morningstar_id)

All functions are pure / stateless — no network calls, no I/O.
The MCP transport and OAuth are handled by the host agent app.

Scope note: build_data() only fills in routing/compliance flags
(domicile_country, is_index_fund, is_australian_superannuation_fund,
investment_type, disclosure_type — these feed select_formula() and the
mandatory disclosure text, so they stay deterministic) and historical time
series (exact bookkeeping across hundreds of raw values, also kept in code).
Current-snapshot values — the current Medalist Rating, current pillar
scores, price score, fees — are a handful of simple 1:1 lookups from a
small, stable datapoint-ID table and are populated by the calling agent
directly from the raw datapoints_raw response instead of here (see "Current
Snapshot Values" / Step 2b in references/full-workflow.md, and medal_symbol()
below for the one piece — the exact rating symbol string — worth keeping
as code even in that step).
"""

from __future__ import annotations

import re
from datetime import date, timedelta
from typing import Any

# ---------------------------------------------------------------------------
# Rating / pillar label mappings
# ---------------------------------------------------------------------------

_INT_TO_SYMBOL: dict[int, str] = {
    2:  "●●●●●",
    1:  "●●●●◯",
    0:  "●●●◐◯",
    -1: "●●◯◯◯",
    -2: "●◯◯◯◯",
}


def medal_symbol(overall_rating: int | None) -> str:
    """Return the exact Medalist Rating dot-symbol string for a numeric rating.

    2=Gold, 1=Silver, 0=Bronze, -1=Neutral, -2=Negative. The agent reads the
    current Medalist Rating directly from the raw morningstar-data-tool
    response (see "Current Snapshot Values" in references/full-workflow.md) and
    should call this rather than hand-typing the dot sequence for
    `data["rating_symbol"]` — a mistyped Unicode character here is easy to
    make and easy to miss on review.
    """
    if overall_rating is None:
        return ""
    return _INT_TO_SYMBOL.get(int(overall_rating), "")


def _strip_quantitative_marker(value: Any) -> Any:
    """Remove Morningstar's ^Q suffix from textual pillar values."""
    if not isinstance(value, str):
        return value
    cleaned = re.sub(r"\s*\^Q\s*", "", value)
    cleaned = cleaned.strip()
    return cleaned if cleaned != "" else None


_BOOL_STRINGS: dict[str, bool] = {
    "true": True, "1": True, "yes": True,
    "false": False, "0": False, "no": False,
}


def _parse_optional_bool(value: Any) -> bool | None:
    """Parse boolean-like datapoint values; return None when value is unknown/blank."""
    if value is None:
        return None
    return _BOOL_STRINGS.get(str(value).strip().lower())

# ---------------------------------------------------------------------------
# Datapoint ID registry (public — host agent uses these to build MCP calls)
# ---------------------------------------------------------------------------

KNOWN_DATAPOINT_IDS: dict[str, str] = {
    "MedalistRating":                 "MMR01",  # Morningstar Medalist Rating      → Gold/Silver/Bronze/Neutral/Negative
    "PeoplePillar":                   "MMR2E",  # MM Rating People Pillar           → High/Above Average/Average/...
    "ProcessPillar":                  "MMR3E",  # MM Rating Process Pillar          → High/Above Average/Average/...
    "ParentPillar":                   "MMR1E",  # MM Rating Parent Pillar           → High/Above Average/Average/...
    "PricePillar":                    "MMR4E",  # MM Rating Price Pillar (current snapshot)
    "FundDomicileCountry":            "LS017",  # Domicile                          → country name/code
    "IsIndexFund":                    "OF00C",  # Is Index Fund                     → true/false
    "IsAustralianSuperannuationFund": "OS280",  # Is Australian Superannuation Fund → true/false
    "InvestmentType":                 "LS466",  # Investment Type                   → fund vehicle type
    "DisclosureType":                 "CNAXS",  # Disclosure Type                   → "Issuer Initiated Rating", "Tracks Morningstar Index", or None
}

# ---------------------------------------------------------------------------
# Default historical date-range helper
# ---------------------------------------------------------------------------

def default_historical_range() -> tuple[str, str]:
    """Return a default 3-year historical date range ending at last month-end.

    3 years is long enough to show a rating trend across multiple review
    cycles without requesting more history than most questions need; the
    agent can always pass an explicit start_date/end_date to override it.
    """
    today = date.today()
    first_of_month = today.replace(day=1)
    end_date = first_of_month - timedelta(days=1)
    try:
        start_date = end_date.replace(year=end_date.year - 3)
    except ValueError:
        start_date = end_date - timedelta(days=1)
        start_date = start_date.replace(year=start_date.year - 3)
    return start_date.isoformat(), end_date.isoformat()


# ---------------------------------------------------------------------------
# Low-level text extraction helpers (for analyst research content)
# ---------------------------------------------------------------------------
#
# NOTE: this module intentionally does NOT guess a medal/pillar score from
# narrative text (e.g. regex-hunting for "Gold" or "High" in prose). Any such
# guess would either be silently overwritten by supplement_with_datapoints()
# when structured data is available, or -- when it isn't -- would fabricate a
# rating value the model presents as real. Both outcomes violate the "never
# invent fund data" rule (see SKILL.md). Narrative text is extracted here only
# to preserve it as display copy; scores come solely from the MCP structured
# datapoints.

def _concat_content(results: list[dict]) -> str:
    return " ".join(r.get("content", "") for r in results)


def _extract_value(key: str, text: str, max_chars: int = 2000) -> str:
    """Extract the value for a JSON key from the MCP content string.

    max_chars=2000 default is generous enough for a price/overall-analysis
    paragraph without buffering an unbounded amount of MCP content into a
    single field; callers pass a larger value (see _extract_pillars) for
    fields known to run longer.
    """
    pattern = re.compile(
        re.escape(f'"{key}":') + r'\s*"(.*?)(?:(?<=[^\\])",\s*"|"[,}\s])',
        re.DOTALL,
    )
    m = pattern.search(text)
    if m:
        val = m.group(1)
        val = re.sub(r"\\u([0-9a-fA-F]{4})", lambda x: chr(int(x.group(1), 16)), val)
        val = val.replace("\\n", "\n").replace("\\t", " ")
        return val[:max_chars]
    idx = text.find(f'"{key}":')
    if idx == -1:
        return ""
    snippet = text[idx + len(key) + 4: idx + len(key) + 4 + max_chars]
    snippet = snippet.lstrip(' "')
    return snippet.split('"')[0] if '"' in snippet else snippet


# ---------------------------------------------------------------------------
# fund_info builder
# ---------------------------------------------------------------------------

def _build_fund_info(lookup: dict, morningstar_id: str) -> list[dict]:
    fields = [
        ("Share Class Name", lookup.get("investment_name", "")),
        ("Ticker",           lookup.get("ticker", "")),
        ("Investment Type",  lookup.get("investment_type", "")),
        ("Exchange",         lookup.get("exchange", "")),
    ]
    rows = [{"Attribute": attr, "Value": val} for attr, val in fields if val]
    rows.append({"Attribute": "Morningstar ID", "Value": morningstar_id})
    return rows


def _set_fund_info_value(data: dict, attr: str, value: Any) -> None:
    """Upsert an Attribute/Value row in fund_info."""
    if value in (None, ""):
        return
    rows = data.setdefault("fund_info", [])
    if not isinstance(rows, list):
        return
    for row in rows:
        if isinstance(row, dict) and row.get("Attribute") == attr:
            row["Value"] = value
            return
    rows.append({"Attribute": attr, "Value": value})


def _is_australia_domicile(value: Any) -> bool | None:
    """Return True/False when domicile is known, else None."""
    raw = str(value).strip().lower() if value is not None else ""
    if not raw:
        return None
    return raw.replace(" ", "") in ("aus", "au", "australia") or "australia" in raw


def select_formula(
    domicile_country: Any,
    is_index_fund: bool | None,
    is_australian_superannuation_fund: bool | None,
) -> str:
    """Deterministically select the weighted Medalist Rating formula for a fund.

    This is the single source of truth for the routing precedence described in
    SKILL.md ("Routing logic for fund-specific methodology questions"):
      1. Non-Australian domicile -> route by is_index_fund only.
      2. Australian domicile:
         - is_australian_superannuation_fund True  -> Superannuation
         - is_australian_superannuation_fund False -> route by is_index_fund
         - is_australian_superannuation_fund unknown -> ask the user (caller
           should treat "clarification_needed" as a signal to use the exact
           clarification wording from Formatter.routing_flags()).

    Returns one of: "Active", "Passive", "Superannuation", "clarification_needed".
    """
    if not _is_australia_domicile(domicile_country):
        return "Passive" if is_index_fund else "Active"

    if is_australian_superannuation_fund is True:
        return "Superannuation"
    if is_australian_superannuation_fund is False:
        return "Passive" if is_index_fund else "Active"
    return "clarification_needed"


# ---------------------------------------------------------------------------
# Pillar / price narrative extraction from analyst research text
# ---------------------------------------------------------------------------

_PILLAR_CONTENT_KEYS: dict[str, list[str]] = {
    "people_pillar":  ["People", "people_pillar_analysis", "People Pillar"],
    "process_pillar": ["Investment Process", "process_pillar_analysis", "Process Pillar"],
    "parent_pillar":  ["parent_pillar_analysis", "Parent", "Parent Pillar"],
}
_PRICE_CONTENT_KEYS   = ["Fund Price", "price_pillar_analysis", "Price", "Price Pillar"]
_OVERALL_CONTENT_KEYS = ["overall_analysis", "Overall Analysis", "Medalist Rating"]


def _first_extracted_value(keys: list[str], content: str, max_chars: int = 2000) -> str:
    """Return the first non-empty _extract_value() hit across candidate JSON keys."""
    for k in keys:
        val = _extract_value(k, content, max_chars=max_chars)
        if val:
            return val
    return ""


def _extract_pillars(content: str) -> dict[str, dict]:
    """Extract narrative text only. Scores come from supplement_with_datapoints()."""
    # Pillar analysis paragraphs run longer than price/overall commentary in
    # practice, hence the larger max_chars than _extract_value's 2000 default.
    return {
        pillar_key: {
            "data":             [],
            "algorithmic_data": [],
            "text":             _first_extracted_value(keys, content, max_chars=3000),
        }
        for pillar_key, keys in _PILLAR_CONTENT_KEYS.items()
    }


def _extract_price(content: str) -> dict:
    """Extract narrative text only. The price score is set by the agent (Step 2b), not here."""
    return {"data": [], "text": _first_extracted_value(_PRICE_CONTENT_KEYS, content)}


def _extract_overall(content: str) -> str:
    """Extract narrative text only. The medal rating is set by the agent (Step 2b), not here."""
    return _first_extracted_value(_OVERALL_CONTENT_KEYS, content)


# ---------------------------------------------------------------------------
# Historical rows helpers
# ---------------------------------------------------------------------------

def _clean_mcp_value(value: Any) -> Any:
    """Preserve the MCP value as-is, trimming only surrounding whitespace on strings."""
    if value is None:
        return None
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned if cleaned != "" else None
    return value


def _try_json(s: str) -> Any:
    import json
    try:
        return json.loads(s)
    except Exception:
        return s


# Shared *data* (key spellings) between extract_historical_rows() and
# _count_distinct_raw_dates() — safe to share, since a new key spelling
# should be recognized identically by both. What's NOT shared is the
# grouping/filtering logic itself (see _count_distinct_raw_dates docstring).
_TS_KEYS = ("timeSeriesData", "TimeSeriesData", "timeSeries", "TimeSeries", "history", "History")


def _read_end_date(item: dict) -> str:
    return str(
        item.get("EndDate") or item.get("endDate") or item.get("End_Date") or
        item.get("Date") or item.get("date") or item.get("asOfDate") or ""
    ).strip()


_HISTORY_ROW_FIELDS = (
    "Medalist Rating", "Medalist Rating Type",
    "People", "People Type",
    "Process", "Process Type",
    "Parent", "Parent Type",
    "Price Score",
)


def extract_historical_rows(raw: Any) -> list[dict]:
    """Pivot historical time series into per-date rows while preserving raw MCP values."""
    by_date: dict[str, dict[str, Any]] = {}

    def _record(field: str, series: list) -> None:
        for item in series:
            if not isinstance(item, dict):
                continue
            end_date = _read_end_date(item)
            if not end_date:
                continue
            raw_val = None
            for key in ("Value", "value", "val"):
                if key in item:
                    raw_val = item.get(key)
                    break
            converted = _clean_mcp_value(raw_val)
            if field in {"People", "Process", "Parent"}:
                converted = _strip_quantitative_marker(converted)
            if converted is None:
                continue
            row = by_date.setdefault(end_date, {"EndDate": end_date})
            row[field] = converted

    def _walk(node: Any) -> None:
        if isinstance(node, str):
            node = _try_json(node)

        if isinstance(node, dict):
            dp_id = str(node.get("datapointId") or node.get("datapoint_id") or "").strip().upper()
            field = {
                "MMR00": "Medalist Rating",
                "MMR1H": "Parent",
                "MMR2H": "People",
                "MMR3H": "Process",
                "MMRGS": "Price Score",
                # Assignment-type fields
                "MMRMT": "Medalist Rating Type",
                "MMR3I": "Process Type",
                "MMR2I": "People Type",
                "MMR1I": "Parent Type",
            }.get(dp_id)
            if field:
                for ts_key in _TS_KEYS:
                    ts = node.get(ts_key)
                    if isinstance(ts, list):
                        _record(field, ts)
                        break

            for value in node.values():
                if isinstance(value, (dict, list)):
                    _walk(value)
            return

        if isinstance(node, list):
            for item in node:
                _walk(item)

    _walk(raw)

    rows = [
        {
            "EndDate": d,
            "Weighted Medalist Rating Score": None,
            **{f: row.get(f) for f in _HISTORY_ROW_FIELDS},
        }
        for d, row in by_date.items()
        if any(row.get(f) is not None for f in _HISTORY_ROW_FIELDS)
    ]
    return sorted(rows, key=lambda r: r["EndDate"], reverse=True)


def _count_distinct_raw_dates(raw: Any) -> int:
    """Count distinct EndDates present anywhere in the raw historical payload.

    This is a deliberately independent walk from extract_historical_rows() —
    it does NOT reuse its _walk()/_record() grouping logic — so a bug there
    can't also corrupt the check meant to catch it. (It does share the pure
    key-spelling lookups above, since those are data, not logic: a new key
    spelling should be recognized identically by both, not silently diverge.)
    Used only as a post-merge sanity check in build_data(): if a raw date
    never makes it into historical_ratings, that's surfaced as a warning
    instead of a silent gap the model would have no way to notice.
    """
    dates: set[str] = set()

    def _walk(node: Any) -> None:
        if isinstance(node, str):
            node = _try_json(node)
        if isinstance(node, dict):
            for ts_key in _TS_KEYS:
                ts = node.get(ts_key)
                if isinstance(ts, list):
                    for item in ts:
                        if isinstance(item, dict):
                            end_date = _read_end_date(item)
                            if end_date:
                                dates.add(end_date)
            for value in node.values():
                if isinstance(value, (dict, list)):
                    _walk(value)
            return
        if isinstance(node, list):
            for item in node:
                _walk(item)

    _walk(raw)
    return len(dates)


def merge_historical_rows(data: dict, rows: list[dict]) -> None:
    """Merge historical rating rows (from morningstar-data-tool) into normalized data.

    Updates ``data["historical_ratings"]`` in-place and back-fills raw MCP
    snapshot values from the most recent row when current datapoints did not
    return them.
    """
    existing = data.get("historical_ratings") or []
    by_date = {
        str(r.get("EndDate", "")): dict(r)
        for r in existing
        if isinstance(r, dict) and r.get("EndDate")
    }

    for row in rows:
        if not isinstance(row, dict):
            continue
        end_date = str(row.get("EndDate", ""))
        if not end_date:
            continue
        merged = dict(by_date.get(end_date, {}))
        for key, value in row.items():
            if value is not None:
                merged[key] = value
        by_date[end_date] = merged

    merged_rows = sorted(by_date.values(), key=lambda r: str(r.get("EndDate", "")), reverse=True)
    if merged_rows:
        data["historical_ratings"] = merged_rows

    latest = merged_rows[0] if merged_rows else None
    if not latest:
        return

    # Back-fill scalar snapshot fields from the latest historical row when the
    # agent's current-snapshot values (Step 2b) haven't been set yet.
    for src_field, dst_key in (("Medalist Rating", "overall_rating_raw"), ("Price Score", "medalist_price_score")):
        val = latest.get(src_field)
        if val is not None and data.get(dst_key) is None:
            data[dst_key] = val

    weighted = latest.get("Weighted Medalist Rating Score")
    if weighted is not None:
        breakdown = data.setdefault("rating_breakdown", {})
        if breakdown.get("weighted_score") is None:
            breakdown["weighted_score"] = weighted


# ---------------------------------------------------------------------------
# Structured datapoint application helpers
# ---------------------------------------------------------------------------

def _apply_datapoint(
    data: dict,
    dp_name: str,
    dp_id: str,
    dp_val: Any,
    ts: list,
) -> None:
    """Apply one morningstar-data-tool ROUTING/COMPLIANCE datapoint to the normalized data dict.

    dp_name: canonical name from our ids_map (e.g. "FundDomicileCountry").
    dp_id:   raw datapoint ID from the server (e.g. "LS017").
    dp_val:  current scalar value.
    ts:      timeSeriesData list (unused here — routing/compliance flags are
             point-in-time attributes, not time series).

    Deliberately narrow scope: this only fills the handful of fields that feed
    select_formula() and the mandatory disclosure text (domicile_country,
    is_index_fund, is_australian_superannuation_fund, investment_type,
    disclosure_type). Those decisions were made deterministic on purpose (see
    select_formula() and Formatter._format_disclosure()) precisely to remove
    model-judgment risk from routing and legally-required text — so their
    *inputs* stay code too, for the same reason.

    Current-snapshot DISPLAY values (Medalist Rating, People/Process/Parent/
    Price pillar scores, fees) are intentionally NOT handled here. They are a
    dozen simple 1:1 lookups from the small, stable ID table already
    documented in references/full-workflow.md, and the agent reads them directly from
    the raw morningstar-data-tool response — see "Current Snapshot Values"
    there for the exact contract. Historical time series remain in code
    (extract_historical_rows / merge_historical_rows) because pivoting
    hundreds of raw values by date is exact bookkeeping code does reliably and
    free-text transcription does not — that distinction is the whole reason
    this function is this narrow.
    """
    nk = (dp_name or "").lower().replace(" ", "").replace("_", "")
    clean = str(dp_val).strip() if dp_val is not None else ""

    # ── Is Index Fund (OF00C) ────────────────────────────────────────────────
    if nk == "isindexfund" or dp_id == "OF00C":
        data["is_index_fund"] = _parse_optional_bool(dp_val)

    # ── Domicile Country (LS017) ──────────────────────────────────────────────
    elif nk in ("funddomicilecountry", "domicile") or dp_id == "LS017":
        if clean:
            data["domicile_country"] = clean
            data["is_australian_domicile"] = _is_australia_domicile(clean)
            _set_fund_info_value(data, "Domicile", clean)

    # ── Is Australian Superannuation Fund (OS280) ────────────────────────────
    elif "isaustralian" in nk or dp_id == "OS280":
        data["is_australian_superannuation_fund"] = _parse_optional_bool(dp_val)

    # ── Investment Type (LS466) ────────────────────────────────────────────────
    elif nk == "investmenttype" or dp_id == "LS466":
        if clean:
            data["investment_type"] = clean
            _set_fund_info_value(data, "Investment Type", clean)

    # ── Disclosure Type (CNAXS) ────────────────────────────────────────────────
    elif nk == "disclosuretype" or dp_id == "CNAXS":
        if clean in ("Issuer Initiated Rating", "Tracks Morningstar Index"):
            data["disclosure_type"] = clean


# ---------------------------------------------------------------------------
# Main public functions
# ---------------------------------------------------------------------------

def normalize(
    lookup: dict,
    research_raw: dict,
    morningstar_id: str,
) -> dict[str, Any]:
    """Convert MCP analyst-research response into a formatter-compatible data dict.

    Extracts narrative text only (pillar/price/overall analysis copy). The
    current Medalist Rating, pillar scores, and price score are NOT set here —
    they're populated by the agent directly from datapoints_raw (see "Current
    Snapshot Values" / Step 2b in references/full-workflow.md). Call
    ``supplement_with_datapoints()`` immediately after to fill in the
    routing/compliance flags and any historical backfill.
    """
    results: list[dict] = research_raw.get("results") or []

    published_at  = results[0].get("published_at", "") if results else ""
    reference_url = results[0].get("url", "")          if results else ""
    content       = _concat_content(results)

    pillars      = _extract_pillars(content)
    price_obj    = _extract_price(content)
    overall_text = _extract_overall(content)

    fund_info = _build_fund_info(lookup, morningstar_id)
    if published_at:
        fund_info.append({"Attribute": "Research Published", "Value": published_at[:10]})
    if reference_url:
        fund_info.append({"Attribute": "Reference URL", "Value": reference_url})

    return {
        "share_class_id": morningstar_id,
        "morningstar_id": morningstar_id,
        "fund_info":      fund_info,

        "overall_rating": None,
        "overall_rating_raw": None,
        "rating_symbol":  "",
        "rating_breakdown": {
            "weighted_score":  None,
            "formula_text":    "",
            "derivation_text": overall_text,
        },

        "historical_ratings":   [],
        "medalist_price_score": None,
        "price":                price_obj,

        "people_pillar":  pillars["people_pillar"],
        "process_pillar": pillars["process_pillar"],
        "parent_pillar":  pillars["parent_pillar"],

        "source":        "mcp",
        "published_at":  published_at,
        "reference_url": reference_url,
        "error":         None,

        # Fund attribute flags (populated by supplement_with_datapoints)
        "domicile_country":                 None,   # LS017 — country name/code
        "is_australian_domicile":           None,   # Derived from LS017
        "is_index_fund":                    None,   # OF00C — True/False/None
        "is_australian_superannuation_fund": None,  # OS280 — True/False/None
        "investment_type":                  None,   # LS466 — Investment vehicle type
        "disclosure_type":                  None,   # CNAXS — "Issuer Initiated Rating", "Tracks Morningstar Index", or None
    }


def supplement_with_datapoints(
    data: dict,
    datapoints_raw: dict,
    datapoint_ids: dict[str, str] | None = None,
) -> dict:
    """Enrich data with structured values from a morningstar-data-tool response.

    Accepts ``datapoints_raw`` — the pre-fetched raw response dict from the
    host agent's morningstar-data-tool call.  No network I/O is performed here.

    Structured values are AUTHORITATIVE — they overwrite any text-parsed
    estimates made by ``normalize()``.  Best-effort: exceptions are silently
    swallowed so the caller always receives a usable data dict.

    Parameters
    ----------
    data           Normalized dict returned by ``normalize()``.
    datapoints_raw Raw response dict from morningstar-data-tool
                   (e.g. ``{"result": {"<morningstar_id>": {"values": [...]}}}``).
    datapoint_ids  Optional mapping ``{"MedalistRating": "MMR01", …}``
                   as returned by the host agent's ID-discovery step.
                   Merged with ``KNOWN_DATAPOINT_IDS``.
    """
    morningstar_id = data.get("morningstar_id") or data.get("share_class_id", "")
    if not morningstar_id:
        return data

    ids_map: dict[str, str] = {**KNOWN_DATAPOINT_IDS}
    if datapoint_ids:
        ids_map.update(datapoint_ids)

    id_to_name: dict[str, str] = {v: k for k, v in ids_map.items()}

    try:
        fund_result = ((datapoints_raw.get("result") or {}).get(morningstar_id) or {})
        values      = fund_result.get("values") or []

        for v in values:
            dp_id   = v.get("datapointId", "")
            dp_val  = v.get("value")
            ts      = v.get("timeSeriesData") or []
            dp_name = id_to_name.get(dp_id) or v.get("datapointName", "")
            _apply_datapoint(data, dp_name, dp_id, dp_val, ts)

    except Exception:
        pass  # best-effort — never break the caller

    return data


def build_data(
    lookup: dict,
    research_raw: dict,
    datapoints_raw: dict,
    history_raw: Any,
    morningstar_id: str,
    datapoint_ids: dict[str, str] | None = None,
) -> dict:
    """Build the complete normalized data dict from all pre-fetched MCP payloads.

    This is the high-level entry point for building the full normalized data dict.
    All payloads are supplied by the host agent — no network calls are made here.

    Parameters
    ----------
    lookup          Result dict from morningstar-id-lookup-tool
                    (keys: morningstar_id, investment_name, ticker, …).
    research_raw    Raw response from morningstar-analyst-research-tool
                    (shape: ``{"results": [{"content": "...", …}]}``).
    datapoints_raw  Raw response from morningstar-data-tool for current
                    datapoints (MMR01, MMR2E, MMR3E, MMR1E, MMRGS).
    history_raw     Raw response from morningstar-data-tool for historical
                    datapoints (MMR00, MMR1H, MMR2H, MMR3H), or None / {} to skip.
    morningstar_id  The fund's Morningstar ID string.
    datapoint_ids   Optional discovered datapoint ID mapping from the host agent.

    Returns
    -------
    Formatter-compatible data dict (same shape as documented in SKILL.md).
    On unrecoverable error returns ``{"error": "...", "morningstar_id": morningstar_id}``.
    """
    try:
        data = normalize(lookup, research_raw, morningstar_id)
        data = supplement_with_datapoints(data, datapoints_raw, datapoint_ids=datapoint_ids)

        if history_raw:
            try:
                history_rows = extract_historical_rows(history_raw)
                if history_rows:
                    merge_historical_rows(data, history_rows)

                expected_dates = _count_distinct_raw_dates(history_raw)
                actual_dates = len(data.get("historical_ratings") or [])
                if expected_dates and actual_dates < expected_dates:
                    data["historical_data_warning"] = (
                        f"{expected_dates - actual_dates} of {expected_dates} historical date(s) "
                        f"in the raw MCP payload did not merge into historical_ratings — the "
                        f"history shown below may be incomplete."
                    )
            except Exception as hist_exc:
                import sys as _sys
                print(
                    f"[data_normalizer WARNING] extract_historical_rows({morningstar_id}): "
                    f"{hist_exc}",
                    file=_sys.stderr,
                )

        return data

    except Exception as exc:
        return {"error": str(exc), "morningstar_id": morningstar_id}
