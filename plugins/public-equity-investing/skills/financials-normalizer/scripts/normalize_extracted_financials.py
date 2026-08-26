#!/usr/bin/env python3
"""Normalize already-extracted financial rows into the financials-normalizer long-form schema.

Inputs may be CSV or JSON. This script is intentionally conservative: it preserves
source labels and signs, maps only clear aliases, and leaves low-confidence items
flagged for review rather than forcing an analyst judgment.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

OUTPUT_COLUMNS = [
    "entity",
    "source_id",
    "statement",
    "line_item_original",
    "line_item_standard",
    "line_item_id",
    "period_end",
    "period_label",
    "period_type",
    "currency",
    "units",
    "source_value",
    "normalized_value",
    "normalization_method",
    "source_location",
    "evidence_label",
    "confidence",
    "normalization_note",
]

ISSUE_COLUMNS = [
    "severity",
    "issue_type",
    "row_number",
    "field",
    "source_id",
    "description",
    "recommended_action",
]

SOURCE_INDEX_COLUMNS = [
    "source_id",
    "source_name",
    "source_type",
    "owner_or_provider",
    "period_covered",
    "as_of_date",
    "retrieved_at",
    "file_tab_page_url_or_location",
    "source_rank",
    "freshness_status",
    "notes",
]

ALLOWED_STATEMENTS = {
    "income_statement",
    "balance_sheet",
    "cash_flow",
    "kpi_schedule",
    "segment",
    "equity_risk_debt_liquidity_context",
    "share_count",
    "working_capital",
    "capital_allocation",
    "consensus_estimate",
    "etf_index_context",
    "adjustment",
}

EVIDENCE_LABELS = {
    "fact_source_reported",
    "fact_provider_standardized",
    "derived_calculation",
    "issuer_management_claim",
    "management_adjusted",
    "analyst_adjusted",
    "analyst_interpretation",
    "assumption_user_provided",
    "assumption_inferred",
    "estimate_consensus",
    "stale_source",
    "contradicted_source",
    "missing_required_source",
    "unknown",
}

LOCATION_OPTIONAL_LABELS = {
    "assumption_user_provided",
    "assumption_inferred",
    "missing_required_source",
    "unknown",
}


def norm(value: Any) -> str:
    return "" if value is None else str(value).strip()


def slug(value: str) -> str:
    value = value.lower().replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return re.sub(r"_+", "_", value).strip("_")


def parse_number(value: Any) -> str:
    parsed = parse_numeric(value)
    if parsed is None:
        return ""
    return format_number(parsed)


def parse_numeric(value: Any) -> float | None:
    text = norm(value)
    if not text or text.lower() in {"na", "n/a", "nm", "-", "--"}:
        return None
    neg = text.startswith("(") and text.endswith(")")
    cleaned = text.replace(",", "").replace("$", "").replace("%", "")
    cleaned = cleaned.strip("() ")
    match = re.search(r"[-+]?\d+(?:\.\d+)?", cleaned)
    if not match:
        return None
    val = float(match.group(0))
    if neg:
        val = -abs(val)
    return val


def format_number(value: float | None) -> str:
    if value is None:
        return ""
    rendered = f"{value:.6f}".rstrip("0").rstrip(".")
    return "0" if rendered in {"-0", ""} else rendered


def infer_period_type(period_label: str, period_type: str) -> str:
    if period_type:
        return period_type
    p = period_label.lower()
    if re.search(r"outlook|guidance|budget|forecast|plan|case|scenario|estimate", p):
        return "forecast"
    if "ltm" in p:
        return "ltm"
    if "ytd" in p:
        return "ytd"
    if re.search(r"q[1-4]|quarter", p):
        return "quarterly"
    if re.search(r"fy|year", p):
        return "annual"
    if re.search(r"jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec", p):
        return "monthly"
    return ""


def infer_period_end(period_end: str, period_label: str) -> str:
    if period_end:
        return period_end
    label = period_label.lower().replace(" ", "")
    year_match = re.search(r"(20\d{2}|19\d{2})", label)
    short_year = re.search(r"(?:fy|cy|q[1-4])'?(\d{2})", label)
    year = int(year_match.group(1)) if year_match else None
    if year is None and short_year:
        year = 2000 + int(short_year.group(1))
    if year is None:
        return ""
    # A fiscal-quarter label alone does not identify an issuer's calendar date.
    is_calendar_period = "cy" in label or "calendar" in label
    if not is_calendar_period:
        return ""
    quarter_ends = {"q1": "03-31", "q2": "06-30", "q3": "09-30", "q4": "12-31"}
    for quarter, month_day in quarter_ends.items():
        if quarter in label:
            return f"{year}-{month_day}"
    if "fy" in label or "cy" in label or "year" in label:
        return f"{year}-12-31"
    return ""


def normalize_currency(currency: str, units: str, raw_value: str) -> str:
    raw = " ".join([currency, units, raw_value]).lower()
    if currency:
        return currency.upper()
    if "$" in raw or "usd" in raw:
        return "USD"
    if "€" in raw or "eur" in raw:
        return "EUR"
    if "£" in raw or "gbp" in raw:
        return "GBP"
    return ""


def normalize_source_type(source_type: str, source_name: str) -> str:
    normalized = norm(source_type) or "uploaded_file"
    if normalized == "user_prompt" and Path(source_name).suffix:
        return "uploaded_file"
    return normalized


def infer_units(units: str, raw_value: str) -> str:
    raw = " ".join([units, raw_value]).lower().replace(" ", "")
    if "%" in raw:
        return "%"
    if "bps" in raw or raw.endswith("bp"):
        return "bps"
    if "x" in raw and re.search(r"\d", raw):
        return "x"
    if any(token in raw for token in ["$bn", "usdbn", "billion", "bn"]):
        return "$mm"
    if any(token in raw for token in ["$000", "$k", "thousand", "usd000"]):
        return "$mm"
    if any(token in raw for token in ["$mm", "$m", "million", "usdmm"]):
        return "$mm"
    return units


def scale_factor_to_normalized_units(units: str, raw_value: str) -> float:
    raw = " ".join([units, raw_value]).lower().replace(" ", "")
    if any(token in raw for token in ["$bn", "usdbn", "billion", "bn"]):
        return 1000.0
    if any(token in raw for token in ["$000", "$k", "thousand", "usd000"]):
        return 0.001
    return 1.0


def apply_sign_convention(
    statement: str, original: str, value: float | None
) -> tuple[float | None, str]:
    if value is None:
        return None, ""
    original_slug = slug(original)
    capex_terms = ("capex", "capital_expenditure", "capital_expenditures")
    if (
        statement == "cash_flow"
        and any(term in original_slug for term in capex_terms)
        and value > 0
    ):
        return -value, "sign_flipped_for_cash_flow_capex"
    return value, ""


def load_aliases(path: Path) -> dict[str, dict[str, str]]:
    aliases: dict[str, dict[str, str]] = {}
    with path.open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            alias = slug(norm(row.get("alias")))
            if alias:
                aliases[alias] = {
                    "line_item_id": norm(row.get("line_item_id")),
                    "line_item_standard": norm(row.get("line_item_standard")),
                    "statement": norm(row.get("statement")),
                }
    return aliases


def load_input(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8-sig") as f:
            return [dict(row) for row in csv.DictReader(f)]
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [dict(row) for row in data]
        if isinstance(data, dict):
            rows = data.get("rows") or data.get("records") or data.get("data") or []
            if isinstance(rows, list):
                metadata = data.get("metadata") or {}
                return [dict(metadata, **dict(row)) for row in rows]
        raise ValueError("json input must be a list or an object with rows/records/data")
    raise ValueError("input must be .csv or .json")


def normalize_row(row: dict[str, Any], aliases: dict[str, dict[str, str]]) -> dict[str, str]:
    original = norm(
        row.get("line_item_original")
        or row.get("label")
        or row.get("line_item")
        or row.get("source_label")
    )
    alias = aliases.get(slug(original), {})
    source_value_raw = norm(row.get("source_value") or row.get("value") or row.get("amount"))
    source_numeric = parse_numeric(source_value_raw)
    statement = norm(row.get("statement") or alias.get("statement"))
    legacy_debt_schedule = statement == "debt_schedule"
    if legacy_debt_schedule:
        statement = "equity_risk_debt_liquidity_context"
    if statement not in ALLOWED_STATEMENTS:
        statement = alias.get("statement", statement)
    line_item_id = norm(row.get("line_item_id") or alias.get("line_item_id"))
    line_item_standard = norm(row.get("line_item_standard") or alias.get("line_item_standard"))
    confidence = norm(row.get("confidence")) or "high"
    note_parts = []
    if legacy_debt_schedule:
        note_parts.append("legacy debt_schedule migrated to equity-risk debt/liquidity context")
    if not line_item_id:
        line_item_id = "unmapped_" + (slug(original) or "unknown")
        line_item_standard = original or "Unmapped"
        confidence = "low"
        note_parts.append("mapping requires analyst review")
    if not statement or statement not in ALLOWED_STATEMENTS:
        raw_value = norm(row.get("source_value") or row.get("value"))
        statement = (
            "kpi_schedule" if "margin" in slug(original) or "%" in raw_value else "income_statement"
        )
        confidence = "low"
        note_parts.append("statement inferred; review")

    source_location = norm(
        row.get("source_location") or row.get("locator") or row.get("cell") or row.get("page")
    )
    evidence_label = norm(row.get("evidence_label")) or "fact_source_reported"
    if evidence_label == "management_claim":
        evidence_label = "issuer_management_claim"
    if evidence_label not in EVIDENCE_LABELS:
        confidence = "low"
        note_parts.append("unrecognized evidence_label; review")
    if statement == "consensus_estimate" and evidence_label == "issuer_management_claim":
        statement = "kpi_schedule"
        note_parts.append("issuer guidance retained separately from external consensus")
    elif statement == "consensus_estimate" and evidence_label != "estimate_consensus":
        evidence_label = "estimate_consensus"
        confidence = "low"
        note_parts.append(
            "consensus evidence label normalized to estimate_consensus; verify external source"
        )
    source_id = norm(row.get("source_id"))
    if not source_location and evidence_label not in LOCATION_OPTIONAL_LABELS:
        confidence = "low"
        note_parts.append("source location missing")
    if not source_id:
        confidence = "low"
        note_parts.append("source_id missing; provenance must be fixed before downstream use")
    source_units = norm(row.get("units") or row.get("unit") or row.get("scale"))
    units = infer_units(source_units, source_value_raw)
    scaled = None
    if source_numeric is not None:
        scaled = source_numeric * scale_factor_to_normalized_units(source_units, source_value_raw)
    normalized_numeric, sign_note = apply_sign_convention(statement, original, scaled)
    normalized_value = format_number(normalized_numeric)
    methods = ["as_reported"]
    if source_numeric is not None and normalized_numeric != source_numeric:
        methods.append("scaled_or_sign_normalized")
    if sign_note:
        note_parts.append(sign_note)
    method = "+".join(methods)
    period_label = norm(row.get("period_label") or row.get("period"))
    note = norm(row.get("normalization_note"))
    if note:
        note_parts.insert(0, note)

    return {
        "entity": norm(row.get("entity") or row.get("entity_name") or row.get("company")),
        "source_id": source_id or "SRC-UNSPECIFIED",
        "statement": statement,
        "line_item_original": original,
        "line_item_standard": line_item_standard,
        "line_item_id": line_item_id,
        "period_end": infer_period_end(norm(row.get("period_end")), period_label),
        "period_label": period_label,
        "period_type": infer_period_type(period_label, norm(row.get("period_type"))),
        "currency": normalize_currency(norm(row.get("currency")), source_units, source_value_raw),
        "units": units,
        "source_value": source_value_raw,
        "normalized_value": normalized_value,
        "normalization_method": method,
        "source_location": source_location,
        "evidence_label": evidence_label,
        "confidence": confidence,
        "normalization_note": "; ".join(p for p in note_parts if p),
    }


def build_normalization_issues(
    rows: list[dict[str, Any]], normalized: list[dict[str, str]]
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    for idx, (raw, normed) in enumerate(zip(rows, normalized), start=2):
        raw_source_id = norm(raw.get("source_id"))
        source_id = normed.get("source_id", "")
        if not raw_source_id:
            issues.append(
                {
                    "severity": "error",
                    "issue_type": "missing_source_id",
                    "row_number": str(idx),
                    "field": "source_id",
                    "source_id": source_id or "SRC-UNSPECIFIED",
                    "description": (
                        "Input row is missing source_id; normalized output used "
                        "SRC-UNSPECIFIED as a visible placeholder."
                    ),
                    "recommended_action": (
                        "Assign a stable source_id from Source_Index before using this row downstream."
                    ),
                }
            )
        elif not raw_source_id.startswith("SRC-"):
            issues.append(
                {
                    "severity": "warning",
                    "issue_type": "nonstandard_source_id",
                    "row_number": str(idx),
                    "field": "source_id",
                    "source_id": raw_source_id,
                    "description": "source_id does not follow the expected SRC-### convention.",
                    "recommended_action": (
                        "Use a stable SRC-### source_id so downstream citations and tie-outs are consistent."
                    ),
                }
            )
        if (
            not normed.get("source_location")
            and normed.get("evidence_label") not in LOCATION_OPTIONAL_LABELS
        ):
            issues.append(
                {
                    "severity": "warning",
                    "issue_type": "missing_source_location",
                    "row_number": str(idx),
                    "field": "source_location",
                    "source_id": source_id,
                    "description": "Source-backed row is missing page, tab, cell, URL, or other source locator.",
                    "recommended_action": "Add a source_location before relying on the value for decision-grade work.",
                }
            )
        if not normed.get("period_end"):
            issues.append(
                {
                    "severity": "warning",
                    "issue_type": "missing_period_end",
                    "row_number": str(idx),
                    "field": "period_end",
                    "source_id": source_id,
                    "description": (
                        "Period end is not explicitly sourced; fiscal labels are not "
                        "converted to assumed calendar dates."
                    ),
                    "recommended_action": (
                        "Add the issuer's reported fiscal period-end date before loading "
                        "the row downstream."
                    ),
                }
            )
    return issues


def write_csv(path: Path, rows: list[dict[str, str]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def write_source_index(path: Path, rows: list[dict[str, Any]]) -> None:
    sources: dict[str, dict[str, str]] = {}
    retrieved_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for row in rows:
        raw_source_id = norm(row.get("source_id"))
        source_id = raw_source_id or "SRC-UNSPECIFIED"
        if source_id not in sources:
            if raw_source_id:
                notes = "review source rank and freshness before relying on output"
            else:
                notes = "ERROR: source_id missing; assign a stable SRC-### id before downstream use"
            sources[source_id] = {
                "source_id": source_id,
                "source_name": norm(row.get("source_name") or row.get("source")),
                "source_type": normalize_source_type(
                    norm(row.get("source_type")),
                    norm(
                        row.get("source_name")
                        or row.get("source")
                        or row.get("source_location")
                        or row.get("locator")
                        or row.get("file")
                    ),
                ),
                "owner_or_provider": norm(row.get("owner_or_provider") or row.get("provider")),
                "period_covered": norm(row.get("period_label") or row.get("period")),
                "as_of_date": norm(row.get("as_of_date") or row.get("source_date")),
                "retrieved_at": norm(row.get("retrieved_at")) or retrieved_at,
                "file_tab_page_url_or_location": norm(
                    row.get("source_location") or row.get("locator") or row.get("file")
                ),
                "source_rank": norm(row.get("source_rank")),
                "freshness_status": norm(row.get("freshness_status")) or "unknown",
                "notes": notes,
            }
    write_csv(path, list(sources.values()), SOURCE_INDEX_COLUMNS)


def write_support_manifest(
    output_dir: Path, *, standalone: bool, issues: list[dict[str, str]]
) -> None:
    outputs = {
        "normalized_financials": output_dir / "Normalized_Financials_Long.csv",
        "source_index": output_dir / "Source_Index.csv",
        "normalization_issues": output_dir / "Normalization_Issues.csv",
        "run_log": output_dir / "run_log.json",
        "manifest": output_dir / "manifest.json",
    }
    primary = str(outputs["normalized_financials"]) if standalone else None
    output_manifest = [
        {
            "key": key,
            "path": str(path),
            "required": True,
            "written": path.exists() or key in {"run_log", "manifest"},
            "artifact_role": "primary_human_deliverable"
            if primary and str(path) == primary
            else "support_artifact",
            "hidden_unless_requested": not (primary and str(path) == primary),
            "description": "Financials-normalizer support artifact for Public Equity Investing workflows.",
        }
        for key, path in outputs.items()
    ]
    hard_failures = [issue["description"] for issue in issues if issue.get("severity") == "error"]
    run_log = {
        "status": "failed" if hard_failures else "completed",
        "model_status": "screen-grade" if issues else "senior-review-ready",
        "artifact_level": "standalone_support_request"
        if standalone
        else "embedded_support_artifact",
        "workbook_mode": "csv_normalization_support",
        "primary_human_deliverable": primary,
        "support_artifacts_user_visible_default": False,
        "warnings": [issue["description"] for issue in issues if issue.get("severity") != "error"],
        "hard_failures": hard_failures,
        "output_manifest": output_manifest,
        "final_response_guidance": {
            "lead_with": "normalization_package" if standalone else "owning_workflow_hero_artifact",
            "mention_support_artifacts": "only_briefly_unless_requested",
        },
    }
    outputs["run_log"].write_text(json.dumps(run_log, indent=2) + "\n", encoding="utf-8")
    outputs["manifest"].write_text(
        json.dumps(
            {
                "outputs": output_manifest,
                "primary_human_deliverable": primary,
                "support_artifacts_user_visible_default": False,
                "final_response_guidance": run_log["final_response_guidance"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Normalize extracted financial rows into long-form CSV"
    )
    parser.add_argument("input_file", type=Path, help="Extracted financial rows as CSV or JSON")
    parser.add_argument("output_dir", type=Path, nargs="?", help="Directory for output CSV files")
    parser.add_argument(
        "--output-dir", dest="output_dir_flag", type=Path, help="Directory for output CSV files"
    )
    parser.add_argument(
        "--aliases",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "references" / "line_item_aliases.csv",
    )
    parser.add_argument(
        "--standalone-normalization-package",
        action="store_true",
        help="Mark the normalized CSV package as the explicit support-task deliverable.",
    )
    args = parser.parse_args()
    output_dir = args.output_dir_flag or args.output_dir
    if output_dir is None:
        parser.error("output directory is required")

    aliases = load_aliases(args.aliases)
    raw_rows = load_input(args.input_file)
    normalized = [normalize_row(row, aliases) for row in raw_rows]
    issues = build_normalization_issues(raw_rows, normalized)
    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "Normalized_Financials_Long.csv", normalized, OUTPUT_COLUMNS)
    write_source_index(output_dir / "Source_Index.csv", raw_rows)
    write_csv(output_dir / "Normalization_Issues.csv", issues, ISSUE_COLUMNS)
    write_support_manifest(
        output_dir, standalone=args.standalone_normalization_package, issues=issues
    )
    print(f"wrote {len(normalized)} rows to {output_dir / 'Normalized_Financials_Long.csv'}")
    error_count = sum(1 for issue in issues if issue.get("severity") == "error")
    if error_count:
        print(
            "ERROR: "
            f"{error_count} provenance issue(s) require remediation; "
            f"see {output_dir / 'Normalization_Issues.csv'}"
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
