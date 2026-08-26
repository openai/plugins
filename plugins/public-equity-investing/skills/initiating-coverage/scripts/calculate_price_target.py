#!/usr/bin/env python3
"""Simple deterministic price target helper.

Supports three methods:
- multiple: enterprise value from target multiple * metric, minus net debt, divided by diluted shares
- pe: target EPS * target P/E multiple
- dcf: equity value divided by diluted shares

Usage:
    python calculate_price_target.py assumptions.json
"""

import argparse
import json
from pathlib import Path


def require(d, key):
    if key not in d or d[key] is None:
        raise ValueError(f"missing required field: {key}")
    try:
        return float(d[key])
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{key} must be numeric") from exc


def require_positive(d, key):
    value = require(d, key)
    if value <= 0:
        raise ValueError(f"{key} must be positive")
    return value


def calculate(data):
    method = data.get("method")
    if method == "multiple":
        metric = require(data, "metric")
        multiple = require(data, "target_multiple")
        net_debt = float(data.get("net_debt", 0) or 0)
        non_operating_adjustments = float(data.get("non_operating_adjustments", 0) or 0)
        shares = require_positive(data, "diluted_shares")
        enterprise_value = metric * multiple
        equity_value = enterprise_value - net_debt + non_operating_adjustments
        price = equity_value / shares
        return {
            "method": method,
            "enterprise_value": enterprise_value,
            "equity_value": equity_value,
            "price_target": price,
            "formula": "((metric * target_multiple) - net_debt + non_operating_adjustments) / diluted_shares",
        }
    if method == "pe":
        eps = require(data, "target_eps")
        pe = require(data, "target_pe")
        return {"method": method, "price_target": eps * pe, "formula": "target_eps * target_pe"}
    if method == "dcf":
        equity_value = require(data, "equity_value")
        shares = require_positive(data, "diluted_shares")
        return {
            "method": method,
            "price_target": equity_value / shares,
            "formula": "equity_value / diluted_shares",
        }
    raise ValueError("method must be one of: multiple, pe, dcf")


def main():
    parser = argparse.ArgumentParser(
        description="Calculate a deterministic initiation price target from structured assumptions."
    )
    parser.add_argument(
        "assumptions_json",
        type=Path,
        help="JSON file containing method-specific price-target assumptions.",
    )
    args = parser.parse_args()
    try:
        with args.assumptions_json.open("r", encoding="utf-8") as f:
            data = json.load(f)
        result = calculate(data)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
