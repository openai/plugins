#!/usr/bin/env python3
"""Validate a structured company tearsheet JSON file.

Expected top-level shape:
{
  "entity": "ExampleCo",
  "profile_type": "public_company",
  "as_of_date": "2026-05-07",
  "sources": [{"source_id": "S1", "source_name": "...", ...}],
  "metrics": [{"metric": "Revenue", "period": "FY2025", "value": 123, ...}],
  "sections": {"one_line_view": "...", "business_snapshot": [...], ...}
}

This script performs lightweight deterministic checks. It does not verify whether
source claims are true; the assistant must still apply the skill's evidence rules.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ALLOWED_EVIDENCE = {
    "fact_source_reported",
    "fact_provider_standardized",
    "derived_calculation",
    "issuer_management_claim",
    "management_adjusted",
    "analyst_adjusted",
    "estimate_consensus",
    "analyst_interpretation",
    "assumption_user_provided",
    "assumption_inferred",
    "stale_source",
    "contradicted_source",
    "missing_required_source",
    "unknown",
}

ALLOWED_CONFIDENCE = {"high", "medium", "low"}
ALLOWED_PROFILE_TYPES = {"public_company", "equity_issuer_profile", "public_sector_peer"}
REQUIRED_TOP_LEVEL = ["entity", "profile_type", "as_of_date"]
REQUIRED_SOURCE_FIELDS = ["source_id", "source_name", "source_type"]
REQUIRED_METRIC_FIELDS = ["metric", "period", "value", "units", "source", "evidence", "confidence"]


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit("top-level json must be an object")
    return data


def validate(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    warnings: list[str] = []

    for field in REQUIRED_TOP_LEVEL:
        if not data.get(field):
            errors.append(f"missing top-level field: {field}")
    if data.get("profile_type") and data["profile_type"] not in ALLOWED_PROFILE_TYPES:
        errors.append(f"profile_type must be one of: {', '.join(sorted(ALLOWED_PROFILE_TYPES))}")

    sources = data.get("sources", [])
    if not isinstance(sources, list):
        errors.append("sources must be a list")
        sources = []
    source_ids = set()
    for idx, source in enumerate(sources, start=1):
        if not isinstance(source, dict):
            errors.append(f"source {idx} must be an object")
            continue
        for field in REQUIRED_SOURCE_FIELDS:
            if not source.get(field):
                errors.append(f"source {idx} missing field: {field}")
        if source.get("source_id"):
            source_ids.add(str(source["source_id"]))
        if not source.get("as_of_date"):
            warnings.append(f"source {idx} missing as_of_date")

    metrics = data.get("metrics", [])
    if metrics and not isinstance(metrics, list):
        errors.append("metrics must be a list")
        metrics = []
    for idx, metric in enumerate(metrics, start=1):
        if not isinstance(metric, dict):
            errors.append(f"metric {idx} must be an object")
            continue
        for field in REQUIRED_METRIC_FIELDS:
            if field not in metric or metric.get(field) in (None, ""):
                errors.append(f"metric {idx} missing field: {field}")
        evidence = metric.get("evidence")
        if evidence and evidence not in ALLOWED_EVIDENCE:
            errors.append(f"metric {idx} has invalid evidence label: {evidence}")
        confidence = metric.get("confidence")
        if confidence and confidence not in ALLOWED_CONFIDENCE:
            errors.append(f"metric {idx} has invalid confidence label: {confidence}")
        source_ref = str(metric.get("source", ""))
        source_id = source_ref.split()[0] if source_ref else ""
        if source_id and source_ids and source_id not in source_ids:
            warnings.append(f"metric {idx} source id not found in sources: {source_id}")
        if not metric.get("period"):
            errors.append(f"metric {idx} missing period")
        if metric.get("evidence") == "assumption_inferred" and metric.get("confidence") != "low":
            warnings.append(f"metric {idx} inferred assumptions should usually be low confidence")

    data_quality_flags = data.get("data_quality_flags", [])
    if data_quality_flags and not isinstance(data_quality_flags, list):
        errors.append("data_quality_flags must be a list")

    return [f"ERROR: {e}" for e in errors] + [f"WARNING: {w}" for w in warnings]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a company tearsheet JSON file")
    parser.add_argument("input_json", type=Path, help="Path to tearsheet JSON")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    args = parser.parse_args()

    data = load_json(args.input_json)
    messages = validate(data)
    for message in messages:
        print(message)

    has_error = any(m.startswith("ERROR:") for m in messages)
    has_warning = any(m.startswith("WARNING:") for m in messages)
    if has_error or (args.strict and has_warning):
        return 1
    print("validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
