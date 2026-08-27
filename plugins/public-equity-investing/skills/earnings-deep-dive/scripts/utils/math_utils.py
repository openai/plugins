from __future__ import annotations


def compute_delta(
    reported: float | None, expected: float | None
) -> tuple[float | None, float | None]:
    """Return (delta, surprise_pct). Surprise pct is None if expected is 0/None."""
    if reported is None or expected is None:
        return None, None
    delta = reported - expected
    if expected == 0:
        return delta, None
    return delta, delta / expected


def margin_delta_bps(
    reported: float | None, expected: float | None, unit_hint: str
) -> float | None:
    """Compute margin delta in bps.

    unit_hint:
      - 'percent' when inputs are in % points (e.g., 35.2)
      - 'decimal' when inputs are 0-1 (e.g., 0.352)
    """
    if reported is None or expected is None:
        return None
    if unit_hint == "decimal":
        return (reported - expected) * 10000.0
    # default percent
    return (reported - expected) * 100.0
