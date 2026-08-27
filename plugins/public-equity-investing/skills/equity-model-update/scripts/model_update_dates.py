from __future__ import annotations

from datetime import datetime, timezone

from model_update_format import text


def parse_date(value: object) -> datetime | None:
    raw = text(value)
    if not raw:
        return None
    formats = ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d")
    for date_format in formats:
        try:
            return datetime.strptime(raw, date_format).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if parsed.tzinfo:
        return parsed
    return parsed.replace(tzinfo=timezone.utc)


def freshness(row: dict[str, str], run_date: datetime, stale_days: int) -> tuple[str, str | None]:
    explicit = text(row.get("freshness_status"))
    if explicit:
        return explicit, None
    as_of = parse_date(row.get("as_of_date") or row.get("source_as_of_date"))
    if as_of is None:
        return "unknown", "missing_as_of_date"
    age_days = (run_date - as_of).days
    if age_days > stale_days:
        return "stale", f"source data is {age_days} days old"
    return "current", None
