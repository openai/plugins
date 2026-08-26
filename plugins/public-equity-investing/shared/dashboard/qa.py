"""Validation for Public Equity Investing dashboard payloads."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .module_registry import MODULES, supported_module_names

EXPECTED_KIND = "public_equity_investing_dashboard.v1"
VALIDATION_PROFILES = {"draft", "production", "standard"}
PRODUCTION_READY_POSTURES = {
    "board_ready",
    "board-ready",
    "client_ready",
    "client-ready",
    "committee_ready",
    "committee-ready",
    "external",
    "final",
    "investor_ready",
    "investor-ready",
    "pm_ready",
    "pm-ready",
    "publication_ready",
    "publication-ready",
    "senior_review_ready",
    "senior-review-ready",
}
DRAFT_POSTURES = {
    "draft",
    "draft_with_citation_gaps",
    "draft-with-citation-gaps",
    "preliminary",
    "screen_grade",
    "screen-grade",
    "working_draft",
    "working-draft",
}
PRODUCTION_METADATA_FIELDS = (
    "payload_stage",
    "freeze_time",
    "source_posture",
    "readiness_label",
    "readiness_posture",
    "citation_policy",
    "decision_context",
)
_ID_RE = re.compile(r"^[a-z][a-z0-9-]*$")
_BAD_TEXT_PATTERNS = (
    "TODO",
    "FIXME",
    "[TOKEN]",
    "{PLACEHOLDER}",
    "undefined",
)
_CITATION_RE = re.compile(r"\[([A-Za-z][A-Za-z0-9_.:-]{0,40})\]")
_NUMERIC_RE = re.compile(r"(?<![A-Za-z])(?:\$?\d[\d,]*(?:\.\d+)?%?|\d{4})(?![A-Za-z])")
_MATERIAL_KEYS = {
    "value",
    "price",
    "detail",
    "summary",
    "body",
    "text",
    "headline",
    "callout",
    "stance",
    "thesis_change",
    "estimate_revision",
    "stock_skew",
    "next_catalyst",
    "event",
    "impact",
    "investor_read",
    "pm_read",
    "read",
    "current",
    "prior",
    "growth",
    "compare",
    "trajectory",
    "revenue",
    "gross_profit",
    "net_income",
    "net_margin",
    "operating_margin",
    "adjusted_operating_margin",
    "ebitda_margin",
    "fcf_margin",
    "margin_rationale",
    "margin_note",
    "estimated_eps",
    "actual_eps",
    "surprise",
}
_SKIP_CITATION_KEYS = {
    "id",
    "source_id",
    "source_ids",
    "citation",
    "citations",
    "citation_ids",
    "url",
    "href",
    "source_url",
    "local_path",
    "model_citations",
    "model_citations_path",
    "workbook_citations",
    "workbook_citations_path",
    "_payload_dir",
    "accent_color",
    "brand_color",
    "ticker_badge_color",
}

_PRICE_EVENT_GRANULARITY_KEYS = (
    "price_granularity",
    "price_frequency",
    "price_interval",
    "granularity",
    "frequency",
    "interval",
)
_PRICE_EVENT_GRANULARITY_ALIASES = {
    "1d": "daily",
    "day": "daily",
    "daily": "daily",
    "eod": "daily",
    "endofday": "daily",
    "close": "daily",
    "closing": "daily",
    "1h": "hourly",
    "60m": "hourly",
    "60min": "hourly",
    "60minute": "hourly",
    "60minutes": "hourly",
    "hour": "hourly",
    "hourly": "hourly",
    "1m": "minute",
    "1min": "minute",
    "1minute": "minute",
    "5m": "minute",
    "5min": "minute",
    "5minute": "minute",
    "15m": "minute",
    "15min": "minute",
    "15minute": "minute",
    "30m": "minute",
    "30min": "minute",
    "30minute": "minute",
    "intraday": "minute",
    "minute": "minute",
    "minutely": "minute",
}
_PRICE_EVENT_POINT_MINIMUMS = {"daily": 10, "hourly": 24, "minute": 60}
_PRICE_EVENT_SPAN_MINUTES = {
    "daily": 7 * 24 * 60,
    "hourly": 6 * 60,
    "minute": 45,
}


def load_payload(path: str | Path) -> dict[str, Any]:
    payload_path = Path(path)
    with payload_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("Dashboard payload must be a JSON object.")
    payload["_payload_dir"] = str(payload_path.resolve().parent)
    return payload


def validate_payload(payload: Mapping[str, Any], profile: str = "production") -> dict[str, Any]:
    hard_failures: list[str] = []
    warnings: list[str] = []
    validation_profile = _normalise_profile(profile)
    if validation_profile not in VALIDATION_PROFILES:
        hard_failures.append(
            f"profile must be one of {sorted(VALIDATION_PROFILES)}; got {profile!r}."
        )
        validation_profile = "draft"
    readiness_posture = _readiness_posture(payload)
    production_required = (
        validation_profile == "production" or readiness_posture in PRODUCTION_READY_POSTURES
    )
    citation_strict = _citation_policy(payload) == "strict" or production_required
    sources = payload.get("sources", [])
    source_records = _source_records(payload)
    source_ids = _source_id_set(source_records)

    if payload.get("kind") != EXPECTED_KIND:
        hard_failures.append(f"kind must be {EXPECTED_KIND!r}; got {payload.get('kind')!r}")

    if production_required:
        _validate_production_contract(
            payload,
            readiness_posture,
            hard_failures,
            warnings,
        )

    _require_string(payload, "title", hard_failures)

    layout = str(payload.get("layout") or "tabs")
    if layout not in {"tabs", "single_page"}:
        hard_failures.append("layout must be either 'tabs' or 'single_page' when provided.")

    issuer = payload.get("issuer")
    if not isinstance(issuer, Mapping):
        hard_failures.append("issuer must be an object with at least ticker or name.")
    elif not (issuer.get("ticker") or issuer.get("name")):
        hard_failures.append("issuer must include ticker or name.")

    tabs = payload.get("tabs")
    if not isinstance(tabs, Sequence) or isinstance(tabs, (str, bytes)):
        hard_failures.append("tabs must be a non-empty list.")
        tabs = []
    elif not tabs:
        hard_failures.append("tabs must contain at least one tab.")

    seen_tabs: set[str] = set()
    for tab_index, tab in enumerate(tabs):
        if not isinstance(tab, Mapping):
            hard_failures.append(f"tabs[{tab_index}] must be an object.")
            continue
        tab_id = str(tab.get("id", ""))
        if not _ID_RE.match(tab_id):
            hard_failures.append(f"tabs[{tab_index}].id must be kebab-case starting with a letter.")
        if tab_id in seen_tabs:
            hard_failures.append(f"duplicate tab id: {tab_id}")
        seen_tabs.add(tab_id)
        _require_string(tab, "label", hard_failures, f"tabs[{tab_index}]")
        modules = tab.get("modules", [])
        if not isinstance(modules, Sequence) or isinstance(modules, (str, bytes)):
            hard_failures.append(f"tabs[{tab_index}].modules must be a list.")
            continue
        if not modules:
            warnings.append(f"tab {tab_id or tab_index} has no modules.")
        for module_index, module in enumerate(modules):
            _validate_module(
                module,
                f"tabs[{tab_index}].modules[{module_index}]",
                hard_failures,
                warnings,
                citation_strict,
            )

    source_ledger_message = _source_ledger_message(source_records, source_ids, citation_strict)
    if source_ledger_message:
        target = hard_failures if citation_strict else warnings
        target.append(source_ledger_message)

    snapshot = payload.get("snapshot", [])
    if isinstance(snapshot, Sequence) and not isinstance(snapshot, (str, bytes)):
        for index, item in enumerate(snapshot):
            if not isinstance(item, Mapping):
                continue
            label = str(item.get("label") or "").strip().lower()
            if label in {"quarter", "period", "fiscal period"}:
                warnings.append(
                    f"snapshot[{index}] duplicates period metadata; keep the quarter prominent in the hero/title instead."
                )

    unresolved = _find_unresolved_text(payload)
    if unresolved:
        hard_failures.extend(unresolved[:20])
        if len(unresolved) > 20:
            hard_failures.append(f"{len(unresolved) - 20} additional unresolved text hits.")

    unresolved_citations = _find_unresolved_citations(payload, source_ids)
    if unresolved_citations:
        target = hard_failures if citation_strict else warnings
        target.extend(unresolved_citations[:20])
        if len(unresolved_citations) > 20:
            target.append(f"{len(unresolved_citations) - 20} additional unresolved citation hits.")

    numeric_gaps = _find_numeric_citation_gaps(payload)
    if numeric_gaps:
        target = hard_failures if citation_strict else warnings
        prefix = "citation gap" if citation_strict else "citation warning"
        target.extend(f"{prefix}: {gap}" for gap in numeric_gaps[:30])
        if len(numeric_gaps) > 30:
            target.append(f"{len(numeric_gaps) - 30} additional numeric citation gaps.")

    return {
        "status": "failed" if hard_failures else "passed",
        "hard_failures": hard_failures,
        "warnings": warnings,
        "supported_modules": supported_module_names(),
        "profile": "production" if production_required else validation_profile,
    }


def _validate_module(
    module: Any,
    path: str,
    hard_failures: list[str],
    warnings: list[str],
    citation_strict: bool,
) -> None:
    if not isinstance(module, Mapping):
        hard_failures.append(f"{path} must be an object.")
        return

    module_type = module.get("type")
    if module_type not in MODULES:
        hard_failures.append(
            f"{path}.type {module_type!r} is not supported; use one of {supported_module_names()}."
        )
        return

    data = module.get("data", {})
    if not isinstance(data, Mapping):
        hard_failures.append(f"{path}.data must be an object.")
        return

    spec = MODULES[str(module_type)]
    for key in spec.required_keys:
        if key not in data:
            hard_failures.append(f"{path}.data missing required key {key!r}.")

    if module_type == "table":
        columns = data.get("columns")
        rows = data.get("rows")
        if not isinstance(columns, Sequence) or isinstance(columns, (str, bytes)) or not columns:
            hard_failures.append(f"{path}.data.columns must be a non-empty list.")
        if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)):
            hard_failures.append(f"{path}.data.rows must be a list.")
    if module_type == "bar_chart":
        items = data.get("items")
        if not isinstance(items, Sequence) or isinstance(items, (str, bytes)) or not items:
            hard_failures.append(f"{path}.data.items must be a non-empty list.")
    if module_type == "scenario_map":
        cases = data.get("cases")
        if not isinstance(cases, Sequence) or isinstance(cases, (str, bytes)) or not cases:
            hard_failures.append(f"{path}.data.cases must be a non-empty list.")
        else:
            for index, case in enumerate(cases):
                if not isinstance(case, Mapping):
                    hard_failures.append(f"{path}.data.cases[{index}] must be an object.")
                    continue
                text_fields = ("title", "headline", "body", "summary")
                has_text = any(str(case.get(key) or "").strip() for key in text_fields)
                bullets = case.get("bullets")
                has_bullets = (
                    isinstance(bullets, Sequence)
                    and not isinstance(bullets, (str, bytes))
                    and any(str(item or "").strip() for item in bullets)
                )
                if not has_text and not has_bullets:
                    hard_failures.append(
                        f"{path}.data.cases[{index}] has no substantive title, summary, body, or bullets; omit empty scenario cards."
                    )
    if module_type == "market_events":
        events = data.get("events")
        if not isinstance(events, Sequence) or isinstance(events, (str, bytes)) or not events:
            hard_failures.append(f"{path}.data.events must be a non-empty list.")
    if module_type in {"financial_trend_chart", "eps_actual_vs_estimate_chart"}:
        periods = data.get("periods") or data.get("rows")
        if not isinstance(periods, Sequence) or isinstance(periods, (str, bytes)) or not periods:
            hard_failures.append(f"{path}.data.periods must be a non-empty list.")
        else:
            _validate_chart_ready_rows(
                str(module_type), data, path, hard_failures, warnings, citation_strict
            )
    if module_type == "equity_price_event_chart":
        prices = data.get("prices")
        events = data.get("events")
        prices_valid = (
            isinstance(prices, Sequence) and not isinstance(prices, (str, bytes)) and bool(prices)
        )
        events_valid = (
            isinstance(events, Sequence) and not isinstance(events, (str, bytes)) and bool(events)
        )
        if not prices_valid:
            hard_failures.append(
                f"{path}.data.prices must be a non-empty list of sourced price points."
            )
        if not isinstance(events, Sequence) or isinstance(events, (str, bytes)) or not events:
            hard_failures.append(f"{path}.data.events must be a non-empty list.")
        if prices_valid and events_valid:
            _validate_chart_ready_rows(
                str(module_type), data, path, hard_failures, warnings, citation_strict
            )


def _validate_chart_ready_rows(
    module_type: str,
    data: Mapping[str, Any],
    path: str,
    hard_failures: list[str],
    warnings: list[str],
    citation_strict: bool,
) -> None:
    if module_type == "financial_trend_chart":
        ready_count = len(_financial_trend_ready_rows(data))
        if ready_count < 2:
            _append_chart_readiness_issue(
                module_type,
                path,
                "has fewer than 2 chart-ready rows",
                hard_failures,
                warnings,
                citation_strict,
            )
        return

    if module_type == "eps_actual_vs_estimate_chart":
        ready_count = len(_eps_ready_rows(data))
        if ready_count < 2:
            _append_chart_readiness_issue(
                module_type,
                path,
                "has fewer than 2 chart-ready rows",
                hard_failures,
                warnings,
                citation_strict,
            )
        return

    if module_type == "equity_price_event_chart":
        readiness = equity_price_event_readiness(data)
        for issue in readiness["issues"]:
            _append_chart_readiness_issue(
                module_type,
                path,
                str(issue),
                hard_failures,
                warnings,
                citation_strict,
            )


def _append_chart_readiness_issue(
    module_type: str,
    path: str,
    problem: str,
    hard_failures: list[str],
    warnings: list[str],
    citation_strict: bool,
) -> None:
    message = (
        f"{path} {module_type} {problem}; omit the chart and add missing_evidence "
        "for unavailable series."
    )
    target = hard_failures if citation_strict else warnings
    target.append(message)


def _financial_trend_ready_rows(data: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    periods = data.get("periods") or data.get("rows") or []
    rows = [row for row in periods if isinstance(row, Mapping)]
    margin_key = _selected_margin_metric_for_validation(data, rows)
    return [
        row
        for row in rows
        if row.get("period")
        and _to_float(row.get("revenue")) is not None
        and _to_float(row.get("gross_profit")) is not None
        and _to_float(row.get("net_income")) is not None
        and _to_ratio(row.get(margin_key)) is not None
    ]


def _eps_ready_rows(data: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    periods = data.get("periods") or data.get("rows") or []
    rows = [row for row in periods if isinstance(row, Mapping)]
    return [
        row
        for row in rows
        if row.get("period")
        and _to_float(row.get("estimated_eps")) is not None
        and _to_float(row.get("actual_eps")) is not None
    ]


def equity_price_event_readiness(data: Mapping[str, Any]) -> dict[str, Any]:
    """Return readiness details shared by QA and renderer gating."""
    price_rows = _price_event_ready_price_rows(data)
    distinct_price_rows = _distinct_price_rows(price_rows)
    event_rows = _price_event_ready_event_rows(data)
    granularity = _normalise_price_granularity(data) or _infer_price_granularity(
        distinct_price_rows
    )
    issues: list[str] = []

    if granularity not in _PRICE_EVENT_POINT_MINIMUMS:
        if granularity:
            issues.append(
                f"uses unsupported price granularity {granularity!r}; use daily, hourly, or minute data"
            )
        else:
            issues.append(
                "must include enough parseable daily, hourly, or minute price data to infer granularity"
            )
        granularity = "daily"

    required_points = _PRICE_EVENT_POINT_MINIMUMS[granularity]
    ready_price_count = len(distinct_price_rows)
    if ready_price_count < required_points:
        issues.append(
            f"needs at least {required_points} {granularity} chart-ready price rows; got {ready_price_count}"
        )

    if granularity in {"hourly", "minute"}:
        timed_price_count = len(
            {
                _price_timestamp_key(row)
                for row in distinct_price_rows
                if _price_timestamp_has_time(row)
            }
        )
        if timed_price_count < required_points:
            issues.append(
                f"needs at least {required_points} time-stamped {granularity} price rows; got {timed_price_count}"
            )

    if ready_price_count >= 2:
        span_minutes = _price_span_minutes(distinct_price_rows)
        required_span = _PRICE_EVENT_SPAN_MINUTES[granularity]
        if span_minutes is None:
            issues.append("needs parseable price timestamps to prove the price-window coverage")
        elif span_minutes < required_span:
            issues.append(
                f"needs a {granularity} price window spanning at least {_format_minutes(required_span)}; got {_format_minutes(span_minutes)}"
            )

    if len(event_rows) < 1:
        issues.append("needs at least 1 chart-ready event row with date and event text")

    missing_source_count = _price_source_gap_count(distinct_price_rows, data)
    if missing_source_count:
        issues.append(
            f"has {missing_source_count} price rows without direct price-source citations or module-level price source"
        )

    return {
        "ready": not issues,
        "granularity": granularity,
        "required_price_points": required_points,
        "ready_price_count": ready_price_count,
        "price_rows": distinct_price_rows,
        "event_rows": event_rows,
        "issues": issues,
    }


def _price_event_ready_price_rows(data: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    prices = data.get("prices") or []
    if not isinstance(prices, Sequence) or isinstance(prices, (str, bytes)):
        return []
    rows = [
        row
        for row in prices
        if isinstance(row, Mapping)
        and _price_timestamp_raw(row)
        and _to_float(row.get("price")) is not None
    ]
    return sorted(rows, key=lambda row: _price_timestamp_parts(row)[0] or datetime.max)


def _price_event_ready_event_rows(data: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    events = data.get("events") or []
    if not isinstance(events, Sequence) or isinstance(events, (str, bytes)):
        return []
    return [
        row
        for row in events
        if isinstance(row, Mapping) and row.get("date") and (row.get("event") or row.get("title"))
    ]


def _distinct_price_rows(rows: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    seen: set[str] = set()
    distinct: list[Mapping[str, Any]] = []
    for row in rows:
        key = _price_timestamp_key(row)
        if key in seen:
            continue
        seen.add(key)
        distinct.append(row)
    return distinct


def _normalise_price_granularity(data: Mapping[str, Any]) -> str | None:
    for key in _PRICE_EVENT_GRANULARITY_KEYS:
        raw = data.get(key)
        if raw is None:
            continue
        compact = re.sub(r"[^a-z0-9]+", "", str(raw).strip().lower())
        if compact in _PRICE_EVENT_GRANULARITY_ALIASES:
            return _PRICE_EVENT_GRANULARITY_ALIASES[compact]
        if compact.endswith(("min", "minute", "minutes")):
            return "minute"
        if compact.endswith(("h", "hour", "hours")):
            return "hourly"
        if compact:
            return compact
    return None


def _infer_price_granularity(rows: Sequence[Mapping[str, Any]]) -> str | None:
    parsed = [_price_timestamp_parts(row) for row in rows]
    parsed_dates = sorted(timestamp for timestamp, _ in parsed if timestamp is not None)
    if len(parsed_dates) < 2:
        return None
    timed_count = len([1 for timestamp, has_time in parsed if timestamp is not None and has_time])
    if timed_count < max(2, len(parsed_dates) // 2):
        return "daily"
    diffs = sorted(
        (parsed_dates[index] - parsed_dates[index - 1]).total_seconds() / 60
        for index in range(1, len(parsed_dates))
        if parsed_dates[index] > parsed_dates[index - 1]
    )
    if not diffs:
        return None
    median_gap = diffs[len(diffs) // 2]
    if median_gap <= 30:
        return "minute"
    if median_gap <= 180:
        return "hourly"
    return "daily"


def _price_span_minutes(rows: Sequence[Mapping[str, Any]]) -> float | None:
    parsed_dates = sorted(
        timestamp
        for timestamp, _ in (_price_timestamp_parts(row) for row in rows)
        if timestamp is not None
    )
    if len(parsed_dates) < 2:
        return None
    return (parsed_dates[-1] - parsed_dates[0]).total_seconds() / 60


def _price_timestamp_has_time(row: Mapping[str, Any]) -> bool:
    _, has_time = _price_timestamp_parts(row)
    return has_time


def _price_timestamp_key(row: Mapping[str, Any]) -> str:
    timestamp, _ = _price_timestamp_parts(row)
    if timestamp is not None:
        return timestamp.isoformat()
    return str(_price_timestamp_raw(row) or "").strip()


def _price_timestamp_parts(row: Mapping[str, Any]) -> tuple[datetime | None, bool]:
    raw = _price_timestamp_raw(row)
    if raw is None:
        return None, False
    text = str(raw).strip()
    if not text:
        return None, False
    has_time = bool(re.search(r"\d{1,2}:\d{2}", text))
    cleaned = text.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(cleaned)
    except ValueError:
        try:
            parsed = datetime.strptime(text[:10], "%Y-%m-%d")
        except ValueError:
            return None, has_time
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed, has_time


def _price_timestamp_raw(row: Mapping[str, Any]) -> Any:
    return row.get("timestamp") or row.get("datetime") or row.get("date")


def _price_source_gap_count(rows: Sequence[Mapping[str, Any]], data: Mapping[str, Any]) -> int:
    module_has_price_source = _has_direct_citation_support(data) or any(
        str(data.get(key) or "").strip()
        for key in ("price_source", "price_source_title", "price_source_url", "price_as_of")
    )
    if module_has_price_source:
        return 0
    return len([row for row in rows if not _has_direct_citation_support(row)])


def _has_direct_citation_support(value: Mapping[str, Any]) -> bool:
    if value.get("citation") or value.get("source_id") or value.get("source_url"):
        return True
    return any(_listify(value.get(key)) for key in ("citations", "citation_ids", "source_ids"))


def _format_minutes(minutes: float) -> str:
    rounded = int(round(minutes))
    if rounded >= 24 * 60 and rounded % (24 * 60) == 0:
        days = rounded // (24 * 60)
        return f"{days} day{'s' if days != 1 else ''}"
    if rounded >= 60 and rounded % 60 == 0:
        hours = rounded // 60
        return f"{hours} hour{'s' if hours != 1 else ''}"
    return f"{rounded} minute{'s' if rounded != 1 else ''}"


def _selected_margin_metric_for_validation(
    data: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
) -> str:
    explicit = (
        data.get("margin_metric")
        or data.get("line_metric")
        or data.get("profitability_metric")
        or data.get("margin_key")
    )
    if explicit:
        return str(explicit)
    for candidate in (
        "net_margin",
        "operating_margin",
        "adjusted_operating_margin",
        "ebitda_margin",
        "fcf_margin",
    ):
        if any(_to_ratio(row.get(candidate)) is not None for row in rows):
            return candidate
    return "net_margin"


def _to_float(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.replace("%", "").replace(",", "").replace("$", "").replace("+", "").strip()
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def _to_ratio(value: Any) -> float | None:
    if isinstance(value, str) and "%" in value:
        parsed = _to_float(value)
        return None if parsed is None else parsed / 100.0
    parsed = _to_float(value)
    if parsed is None:
        return None
    return parsed / 100.0 if abs(parsed) > 2 else parsed


def _require_string(
    obj: Mapping[str, Any],
    key: str,
    hard_failures: list[str],
    path: str = "payload",
) -> None:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        hard_failures.append(f"{path}.{key} must be a non-empty string.")


def _normalise_profile(profile: str) -> str:
    value = str(profile or "draft").strip().lower().replace("_", "-")
    if value in {"standard", "support"}:
        return "draft"
    return value.replace("-", "_")


def _normalise_posture(value: Any) -> str:
    return str(value or "").strip().lower().replace(" ", "_").replace("-", "_")


def _readiness_posture(payload: Mapping[str, Any]) -> str:
    metadata = payload.get("metadata")
    posture = payload.get("readiness_posture")
    if isinstance(metadata, Mapping):
        posture = (
            metadata.get("readiness_posture")
            or metadata.get("readiness")
            or metadata.get("readiness_label")
            or posture
        )
    return _normalise_posture(posture)


def _validate_production_contract(
    payload: Mapping[str, Any],
    readiness_posture: str,
    hard_failures: list[str],
    warnings: list[str],
) -> None:
    _require_string(payload, "mode", hard_failures)

    if not isinstance(payload.get("layout"), str) or not str(payload.get("layout")).strip():
        hard_failures.append("production dashboards must include layout.")

    metadata = payload.get("metadata")
    if not isinstance(metadata, Mapping):
        hard_failures.append("production dashboards must include metadata.")
    else:
        for key in PRODUCTION_METADATA_FIELDS:
            _require_string(metadata, key, hard_failures, "metadata")
        if str(metadata.get("payload_stage") or "").strip().lower() != "production":
            hard_failures.append(
                "production dashboards must set metadata.payload_stage to 'production'."
            )
        if str(metadata.get("citation_policy") or "").strip().lower() != "strict":
            hard_failures.append(
                "production dashboards must set metadata.citation_policy to 'strict'."
            )
        if readiness_posture in DRAFT_POSTURES:
            hard_failures.append("production dashboards cannot use a draft readiness_posture.")

    hero = payload.get("hero")
    if not isinstance(hero, Mapping) or not hero:
        hard_failures.append("production dashboards must include a non-empty hero.")
    elif not any(str(hero.get(key) or "").strip() for key in ("headline", "dek", "callout")):
        hard_failures.append(
            "production dashboards must include hero headline, dek, or callout text."
        )

    snapshot = payload.get("snapshot")
    if not isinstance(snapshot, Sequence) or isinstance(snapshot, (str, bytes)) or not snapshot:
        hard_failures.append("production dashboards must include non-empty snapshot tiles.")

    _ = warnings


def _find_unresolved_text(value: Any, path: str = "$") -> list[str]:
    hits: list[str] = []
    if isinstance(value, str):
        for pattern in _BAD_TEXT_PATTERNS:
            if pattern in value:
                hits.append(f"{path} contains unresolved text pattern {pattern!r}.")
                break
    elif isinstance(value, Mapping):
        for key, child in value.items():
            hits.extend(_find_unresolved_text(child, f"{path}.{key}"))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            hits.extend(_find_unresolved_text(child, f"{path}[{index}]"))
    return hits


def _citation_policy(payload: Mapping[str, Any]) -> str:
    metadata = payload.get("metadata")
    policy = payload.get("citation_policy")
    if isinstance(metadata, Mapping):
        policy = metadata.get("citation_policy") or policy
    return str(policy or "warn").strip().lower()


def _source_id_set(sources: Any) -> set[str]:
    ids: set[str] = set()
    if not isinstance(sources, Sequence) or isinstance(sources, (str, bytes)):
        return ids
    for index, source in enumerate(sources, start=1):
        if not isinstance(source, Mapping):
            continue
        source_id = str(source.get("id") or source.get("source_id") or f"S{index}").strip()
        if source_id:
            ids.add(source_id)
    return ids


def _source_records(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for key in ("sources", "model_citations", "workbook_citations"):
        value = payload.get(key)
        if isinstance(value, Mapping):
            records.extend(
                dict(item, id=record_id)
                for record_id, item in value.items()
                if isinstance(item, Mapping)
            )
        elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            records.extend(item for item in value if isinstance(item, Mapping))
    for key in ("model_citations_path", "workbook_citations_path"):
        records.extend(_load_source_records_from_path(payload, payload.get(key)))
    return records


def _resolve_payload_path(payload: Mapping[str, Any], path_value: Any) -> Path | None:
    raw = str(path_value or "").strip()
    if not raw or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", raw):
        return None
    path = Path(raw)
    if not path.is_absolute() and payload.get("_payload_dir"):
        path = Path(str(payload.get("_payload_dir"))) / path
    return path


def _load_source_records_from_path(
    payload: Mapping[str, Any], path_value: Any
) -> list[dict[str, Any]]:
    path = _resolve_payload_path(payload, path_value)
    if not path or not path.exists():
        return []
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    if isinstance(loaded, Mapping):
        for key in ("model_citations", "workbook_citations", "sources"):
            if isinstance(loaded.get(key), Sequence) and not isinstance(
                loaded.get(key), (str, bytes)
            ):
                return [item for item in loaded[key] if isinstance(item, Mapping)]
        return [
            dict(item, id=record_id)
            for record_id, item in loaded.items()
            if isinstance(item, Mapping)
        ]
    if isinstance(loaded, Sequence) and not isinstance(loaded, (str, bytes)):
        return [item for item in loaded if isinstance(item, Mapping)]
    return []


def _source_ledger_message(
    sources: Any,
    source_ids: set[str],
    citation_strict: bool,
) -> str | None:
    if not isinstance(sources, Sequence) or isinstance(sources, (str, bytes)):
        problem = "sources must be a non-empty list"
    elif not sources or not source_ids:
        problem = "sources is empty"
    else:
        return None

    if citation_strict:
        return f"{problem}; strict dashboards must include a source ledger."
    return f"{problem}; final dashboards should include a source ledger."


def _find_unresolved_citations(value: Any, source_ids: set[str], path: str = "$") -> list[str]:
    hits: list[str] = []
    if isinstance(value, str):
        for source_id in _CITATION_RE.findall(value):
            if source_id not in source_ids:
                hits.append(f"{path} cites unknown source id {source_id!r}.")
    elif isinstance(value, Mapping):
        for key in ("citation", "source_id"):
            source_id = value.get(key)
            if source_id and str(source_id) not in source_ids:
                hits.append(f"{path}.{key} references unknown source id {source_id!r}.")
        for key in ("citations", "citation_ids", "source_ids"):
            for source_id in _listify(value.get(key)):
                if source_id and str(source_id) not in source_ids:
                    hits.append(f"{path}.{key} references unknown source id {source_id!r}.")
        for key, child in value.items():
            if key in _SKIP_CITATION_KEYS:
                continue
            hits.extend(_find_unresolved_citations(child, source_ids, f"{path}.{key}"))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            hits.extend(_find_unresolved_citations(child, source_ids, f"{path}[{index}]"))
    return hits


def _find_numeric_citation_gaps(
    value: Any, path: str = "$", inherited_support: bool = False, key: str = ""
) -> list[str]:
    hits: list[str] = []
    if isinstance(value, Mapping):
        support = inherited_support or _has_citation_support(value)
        for child_key, child in value.items():
            if child_key in _SKIP_CITATION_KEYS or child_key in {"sources", "qa"}:
                continue
            child_support = support
            if child_key in {
                "rows",
                "items",
                "events",
                "periods",
                "cases",
                "questions",
                "snapshot",
            }:
                child_support = support
            hits.extend(
                _find_numeric_citation_gaps(child, f"{path}.{child_key}", child_support, child_key)
            )
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            hits.extend(
                _find_numeric_citation_gaps(child, f"{path}[{index}]", inherited_support, key)
            )
    elif isinstance(value, str):
        if (
            key in _MATERIAL_KEYS
            and _NUMERIC_RE.search(value)
            and not (inherited_support or _has_inline_citation(value))
        ):
            snippet = re.sub(r"\s+", " ", value.strip())
            if len(snippet) > 90:
                snippet = snippet[:87] + "..."
            hits.append(f"{path} has numeric material without citations: {snippet!r}")
    return hits


def _has_citation_support(value: Mapping[str, Any]) -> bool:
    if value.get("citation") or value.get("source_id") or value.get("source_url"):
        return True
    for key in ("citations", "citation_ids", "source_ids"):
        if _listify(value.get(key)):
            return True
    return any(isinstance(child, str) and _has_inline_citation(child) for child in value.values())


def _has_inline_citation(value: str) -> bool:
    return bool(_CITATION_RE.search(value))


def _listify(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, str):
        if "," in value or ";" in value:
            return [item.strip() for item in re.split(r"[,;]", value) if item.strip()]
        return [value]
    return [value]
