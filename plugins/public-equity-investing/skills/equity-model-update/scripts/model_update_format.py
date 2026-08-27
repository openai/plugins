from __future__ import annotations

import math
import re
from typing import Any

INVALID_NUMBERS = {"na", "n/a", "nm", "-", "--", "input required"}


def text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def first_text(row: dict[str, str], fields: tuple[str, ...]) -> str:
    for field in fields:
        value = text(row.get(field))
        if value:
            return value
    return ""


def parse_number(value: Any) -> float | None:
    raw = text(value)
    if not raw:
        return None
    if raw.lower() in INVALID_NUMBERS:
        return None
    negative = raw.startswith("(") and raw.endswith(")")
    cleaned = raw.replace(",", "").replace("$", "").replace("%", "").strip("() ")
    match = re.search(r"[-+]?\d+(?:\.\d+)?", cleaned)
    if not match:
        return None
    number = float(match.group(0))
    if negative:
        return -abs(number)
    return number


def first_number(row: dict[str, str], fields: tuple[str, ...]) -> float | None:
    for field in fields:
        parsed = parse_number(row.get(field))
        if parsed is not None:
            return parsed
    return None


def fmt_number(value: float | None) -> str:
    if value is None or not math.isfinite(value):
        return ""
    rendered = f"{value:.1f}" if abs(value) >= 100 else f"{value:.2f}"
    return rendered.rstrip("0").rstrip(".")
