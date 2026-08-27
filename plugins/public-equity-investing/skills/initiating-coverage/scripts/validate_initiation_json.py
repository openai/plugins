#!/usr/bin/env python3
"""Validate structured initiating coverage JSON."""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

VALID_EVIDENCE = {
    "fact",
    "company_claim",
    "street_estimate",
    "model_derived",
    "banker_or_pm_judgment",
    "assumption",
    "mixed",
    "needs_source",
}
VALID_CONFIDENCE = {"high", "medium", "low"}
VALID_MODES = {
    "sell_side_initiation",
    "buy_side_deep_dive",
    "long_only_initiation",
    "hedge_fund_initiation",
    "credit_adjacent_initiation",
    "sector_initiation",
    "model_first_initiation",
    "report_refresh",
}
PLACEHOLDER_TERMS = {"TBD", "TODO", "MISSING", "[PLACEHOLDER]", "PLACEHOLDER"}
SOURCE_DATE_FIELDS = ("date_accessed", "date_published", "as_of_date", "source_as_of")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def is_placeholder(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    text = value.strip().upper()
    return text in PLACEHOLDER_TERMS or text.startswith("TBD -")


def placeholder_paths(value: Any, prefix: str = "") -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            paths.extend(placeholder_paths(child, child_prefix))
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            child_prefix = f"{prefix}[{idx}]"
            paths.extend(placeholder_paths(child, child_prefix))
    elif is_placeholder(value):
        paths.append(prefix or "<root>")
    return paths


def valid_iso_date(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        datetime.strptime(value.strip(), "%Y-%m-%d")
    except ValueError:
        return False
    return True


def validate(data, publication_ready=False):
    errors = []
    warnings = []

    if not data.get("company"):
        errors.append("missing required field: company")

    mode = data.get("report_mode")
    if not mode:
        errors.append("missing required field: report_mode")
    elif mode not in VALID_MODES:
        warnings.append(f"report_mode '{mode}' is not one of expected modes")

    sources = data.get("sources") or data.get("source_register") or []
    if not isinstance(sources, list) or len(sources) == 0:
        errors.append("at least one source/source_register entry is required")

    source_ids = set()
    for i, src in enumerate(sources):
        sid = src.get("source_id") if isinstance(src, dict) else None
        if not sid:
            message = f"source {i} missing source_id"
            (errors if publication_ready else warnings).append(message)
        else:
            source_ids.add(sid)
        if publication_ready and isinstance(src, dict):
            if not any(src.get(field) for field in SOURCE_DATE_FIELDS):
                errors.append(f"source {sid or i} missing source date/as_of metadata")
            for field in SOURCE_DATE_FIELDS:
                if src.get(field) and not valid_iso_date(src.get(field)):
                    errors.append(f"source {sid or i} {field} must be YYYY-MM-DD")
            if not (src.get("reliability") or src.get("reliability_tier")):
                errors.append(f"source {sid or i} missing reliability/reliability_tier")
            if not (src.get("stale_flag") is not None or src.get("freshness_status")):
                errors.append(f"source {sid or i} missing stale_flag/freshness_status")

    thesis = data.get("thesis_pillars") or data.get("thesis_hypotheses") or []
    user_view = data.get("user_view") or data.get("md_pm_answer")
    if not thesis and not user_view:
        errors.append("provide thesis_pillars/thesis_hypotheses or user_view/md_pm_answer")

    for section_name in ["thesis_pillars", "model_drivers"]:
        for i, item in enumerate(data.get(section_name, []) or []):
            if not isinstance(item, dict):
                errors.append(f"{section_name}[{i}] must be an object")
                continue
            ev = item.get("evidence_label")
            if ev and ev not in VALID_EVIDENCE:
                errors.append(f"{section_name}[{i}] invalid evidence_label: {ev}")
            conf = item.get("confidence")
            if conf and conf not in VALID_CONFIDENCE:
                errors.append(f"{section_name}[{i}] invalid confidence: {conf}")
            for sid in item.get("source_ids", []) or []:
                if source_ids and sid not in source_ids:
                    message = f"{section_name}[{i}] references unknown source_id: {sid}"
                    (errors if publication_ready else warnings).append(message)
            if ev in {"fact", "company_claim", "street_estimate", "model_derived"} and not item.get(
                "source_ids"
            ):
                warnings.append(
                    f"{section_name}[{i}] evidence_label {ev} should include source_ids"
                )

    valuation = data.get("valuation") or {}
    if (
        data.get("target_price")
        or valuation.get("target_price")
        or valuation.get("target_price_math")
    ):
        if not (data.get("current_price") or valuation.get("current_price")):
            warnings.append("target price provided without current_price")
        if not (data.get("currency") or valuation.get("currency")):
            warnings.append("target price provided without currency")
        if not (valuation.get("primary_method") or valuation.get("target_price_math")):
            warnings.append("target price provided without primary valuation method or math")

    if publication_ready:
        for path in placeholder_paths(data):
            errors.append(f"publication-ready output contains unresolved placeholder at {path}")

    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Validate structured initiating coverage JSON.")
    parser.add_argument("input_json", help="Path to structured initiating coverage JSON")
    parser.add_argument(
        "--publication-ready",
        action="store_true",
        help="Escalate placeholder, source freshness, and unknown source-id issues to errors.",
    )
    args = parser.parse_args()

    path = Path(args.input_json)
    data = load_json(path)
    errors, warnings = validate(data, publication_ready=args.publication_ready)
    for w in warnings:
        print(f"WARNING: {w}")
    for e in errors:
        print(f"ERROR: {e}")
    if errors:
        return 1
    print("validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
