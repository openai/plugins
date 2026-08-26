#!/usr/bin/env python3
"""Core calculations for the preview pack.

All functions are deterministic and should be unit-tested.
"""

from __future__ import annotations

import math
import re

import pandas as pd

PERIOD_RE = re.compile(r"^FY(?P<year>[0-9]{4})Q(?P<q>[1-4])$")


def parse_fiscal_period_id(fiscal_period_id: str) -> tuple[int, int]:
    m = PERIOD_RE.match(str(fiscal_period_id).strip())
    if not m:
        raise ValueError(f"Invalid fiscal_period_id format: {fiscal_period_id} (expected FY2026Q1)")
    return int(m.group("year")), int(m.group("q"))


def shift_period(fiscal_period_id: str, delta_quarters: int) -> str:
    """Shift a FYxxxxQx by delta_quarters (negative for past)."""
    y, q = parse_fiscal_period_id(fiscal_period_id)
    idx = (y * 4 + (q - 1)) + delta_quarters
    new_y = idx // 4
    new_q = idx % 4 + 1
    return f"FY{new_y:04d}Q{new_q}"


def is_rate_metric(metric_id: str, unit: str) -> bool:
    """Heuristic: treat ratios/percents and *_margin/*_rate as rates."""
    u = (unit or "").lower()
    mid = (metric_id or "").lower()
    if u in {"ratio", "pct", "percent", "bps"}:
        return True
    if mid.endswith(("_margin", "_rate")) or mid in {"nrr", "grr", "nim"}:
        return True
    return False


def safe_pct_change(curr: float | None, prev: float | None) -> float | None:
    if curr is None or prev is None:
        return None
    try:
        if pd.isna(curr) or pd.isna(prev):
            return None
    except Exception:
        pass
    if prev <= 0:
        return None
    return curr / prev - 1.0


def safe_abs_change(curr: float | None, prev: float | None) -> float | None:
    if curr is None or prev is None:
        return None
    try:
        if pd.isna(curr) or pd.isna(prev):
            return None
    except Exception:
        pass
    return curr - prev


def safe_bps_change(curr_ratio: float | None, prev_ratio: float | None) -> float | None:
    """Return change in basis points (assumes ratios, e.g., 0.742)."""
    d = safe_abs_change(curr_ratio, prev_ratio)
    if d is None:
        return None
    return d * 10_000.0


def two_year_stack(curr: float | None, two_year_ago: float | None) -> float | None:
    return safe_pct_change(curr, two_year_ago)


def trend_slope(values: list[float]) -> float | None:
    """Simple slope estimate over equally spaced periods.

    Returns slope per period (not percent). Use only for directional 'trend' flags.
    """
    vals = [v for v in values if v is not None and not (isinstance(v, float) and math.isnan(v))]
    if len(vals) < 3:
        return None
    n = len(vals)
    xs = list(range(n))
    x_mean = sum(xs) / n
    y_mean = sum(vals) / n
    num = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, vals))
    den = sum((x - x_mean) ** 2 for x in xs)
    if den == 0:
        return None
    return num / den


def auto_flag_delta(curr_est: float | None, cons_est: float | None, metric_is_rate: bool) -> bool:
    """Heuristic flag when whisper differs from consensus meaningfully."""
    if curr_est is None or cons_est is None:
        return False
    try:
        if pd.isna(curr_est) or pd.isna(cons_est):
            return False
    except Exception:
        pass

    if metric_is_rate:
        # Ratio: flag if >=25 bps difference (tunable)
        return abs(curr_est - cons_est) >= 0.0025
    # Level: flag if >=1% difference (tunable)
    if cons_est == 0:
        return False
    return abs(curr_est / cons_est - 1.0) >= 0.01
