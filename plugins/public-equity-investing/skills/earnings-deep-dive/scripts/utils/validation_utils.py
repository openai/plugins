from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence


@dataclass
class ValidationIssue:
    level: str  # "ERROR" or "WARN"
    message: str


def is_missing(val: Any) -> bool:
    if val is None:
        return True
    if isinstance(val, float):
        # NaN
        return val != val
    if isinstance(val, str) and val.strip() == "":
        return True
    if isinstance(val, str) and val.strip().upper() == "MISSING":
        return True
    return False


def as_float_or_none(val: Any) -> float | None:
    """Parse a numeric value; return None if MISSING or unparsable."""
    if is_missing(val):
        return None
    try:
        return float(str(val).replace(",", ""))
    except Exception:
        return None


def require_columns(df, required: Sequence[str]) -> list[str]:
    missing = [c for c in required if c not in df.columns]
    return missing


def enum_check(value: Any, allowed: Sequence[str]) -> bool:
    if is_missing(value):
        return False
    return str(value).strip() in set(allowed)
