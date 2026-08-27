#!/usr/bin/env python3
"""Materialize a screen-grade comps framework when market data is incomplete.

This helper is a deterministic fallback, not a populated market-data model. It
writes a peer framework, source requirements, missing-data requests, markdown
summary, run log, and output manifest so comps workflows never fail with an
empty artifact when live data or workbook dependencies are unavailable.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
PLUGIN_ROOT = SKILL_ROOT.parents[1]
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from shared.artifact_packager import dict_rows_to_sheet, write_cover_first_workbook  # noqa: E402

DEFAULT_REQUIRED_METRICS = [
    "current price",
    "basic and diluted shares",
    "cash and debt",
    "minority interest / preferred / leases where relevant",
    "LTM revenue",
    "LTM EBITDA or sector denominator",
    "NTM revenue estimate",
    "NTM EBITDA or EPS estimate where meaningful",
    "market data as-of date",
    "estimate source and estimate as-of date",
]

SOURCE_REQUIREMENTS = [
    (
        "Market data",
        "Price, market cap, shares, EV bridge",
        "fact_secondary",
        "Market-data provider or exchange data with as-of date",
    ),
    (
        "Company filings",
        "Cash, debt, minority interest, preferreds, share count support",
        "fact_primary",
        "Latest 10-K/10-Q/20-F/6-K or equivalent",
    ),
    (
        "Consensus estimates",
        "NTM revenue, EBITDA, EBIT, EPS, FCF",
        "third_party_estimate",
        "Consensus provider export with estimate-as-of date",
    ),
    (
        "Peer rationale",
        "Business model, geography, growth/margin fit, inclusion/exclusion logic",
        "inference",
        "Analyst judgment tied to source evidence",
    ),
    (
        "Adjustments",
        "One-time items, lease/SBC/capex normalization, calendarization",
        "assumption",
        "Documented adjustment source and rationale",
    ),
]


def normalize_header(header: str) -> str:
    return header.strip().lower().replace(" ", "_").replace("-", "_")


def load_peer_rows(peer_csv: Path | None, warnings: list[str]) -> list[dict[str, str]]:
    if peer_csv is None:
        return []
    if not peer_csv.exists():
        warnings.append(
            f"Peer CSV not found: {peer_csv}; using placeholder/watchlist peer framework."
        )
        return []
    with peer_csv.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        rows = []
        for row in reader:
            normalized = {
                normalize_header(key or ""): str(value or "").strip() for key, value in row.items()
            }
            company = (
                normalized.get("company")
                or normalized.get("company_name")
                or normalized.get("name")
            )
            ticker = normalized.get("ticker") or normalized.get("symbol")
            if company or ticker:
                rows.append(
                    {
                        "company": company or "TBD",
                        "ticker": ticker or "TBD",
                        "peer_tier": normalized.get("peer_tier")
                        or normalized.get("tier")
                        or "Watchlist",
                        "business_model_note": normalized.get("business_model_note")
                        or normalized.get("business_model")
                        or "",
                        "inclusion_rationale": normalized.get("inclusion_rationale")
                        or normalized.get("rationale")
                        or "",
                        "exclusion_rationale": normalized.get("exclusion_rationale") or "",
                    }
                )
    return rows


def peer_list_rows(peer_list: str) -> list[dict[str, str]]:
    rows = []
    for item in [part.strip() for part in peer_list.split(",") if part.strip()]:
        if ":" in item:
            ticker, company = [part.strip() for part in item.split(":", 1)]
        else:
            ticker, company = item, item
        rows.append(
            {
                "company": company,
                "ticker": ticker.upper(),
                "peer_tier": "Watchlist",
                "business_model_note": "User-provided peer candidate; validate business-model fit.",
                "inclusion_rationale": "Requires source-supported peer rationale before use in selected range.",
                "exclusion_rationale": "",
            }
        )
    return rows


def build_peer_framework(args: argparse.Namespace) -> list[dict[str, str]]:
    warnings: list[str] = getattr(args, "warnings", [])
    rows = [
        {
            "company": args.target,
            "ticker": args.ticker,
            "peer_tier": "Target",
            "peer_role": "target",
            "business_model_note": args.business_model or "Target business model not provided.",
            "inclusion_rationale": "Subject company.",
            "exclusion_rationale": "",
            "market_data_status": "missing"
            if args.market_data_status == "missing"
            else args.market_data_status,
            "required_metrics": "; ".join(DEFAULT_REQUIRED_METRICS),
            "source_requirement": "Target market data, filings, financials, estimates, and EV bridge required.",
            "notes": "Do not use this row for valuation until populated with sourced values.",
        }
    ]

    input_rows = load_peer_rows(args.peer_csv, warnings) + peer_list_rows(args.peer_list or "")
    if not input_rows:
        input_rows = [
            {
                "company": f"Peer candidate {idx}",
                "ticker": "TBD",
                "peer_tier": "Watchlist",
                "business_model_note": "Placeholder peer candidate.",
                "inclusion_rationale": "Identify actual public peer and validate fit.",
                "exclusion_rationale": "",
            }
            for idx in range(1, args.placeholder_peer_count + 1)
        ]

    for row in input_rows:
        tier = row.get("peer_tier") or "Watchlist"
        rows.append(
            {
                "company": row.get("company", "TBD"),
                "ticker": row.get("ticker", "TBD"),
                "peer_tier": tier,
                "peer_role": "core_peer" if tier.lower() == "core" else "watchlist_peer",
                "business_model_note": row.get("business_model_note", ""),
                "inclusion_rationale": row.get("inclusion_rationale")
                or "Validate similarity in model, growth, margin, geography, and capitalization.",
                "exclusion_rationale": row.get("exclusion_rationale", ""),
                "market_data_status": args.market_data_status,
                "required_metrics": "; ".join(DEFAULT_REQUIRED_METRICS),
                "source_requirement": "Populate market data, filings, consensus, EV bridge, and source dates before decision use.",
                "notes": "Screen-grade candidate; not a valuation anchor until sourced.",
            }
        )
    return rows


def build_missing_data_rows(args: argparse.Namespace) -> list[dict[str, str]]:
    return [
        {
            "priority": "P0",
            "needed_item": "Current share price and market-data as-of date",
            "why_it_matters": "Enterprise and equity value become stale immediately.",
            "affected_output": "EV, P/E, all trading multiples",
            "minimum_substitute": "User-provided price with date",
        },
        {
            "priority": "P0",
            "needed_item": "Basic/diluted share count and dilution treatment",
            "why_it_matters": "Equity value and per-share outputs can be wrong without share basis.",
            "affected_output": "Market cap, equity value, P/E, per-share value",
            "minimum_substitute": "Latest filing share count plus stated dilution assumption",
        },
        {
            "priority": "P0",
            "needed_item": "Cash, debt, preferreds, minority interest, leases, and other EV bridge items",
            "why_it_matters": "EV can be materially misstated.",
            "affected_output": "EV/revenue, EV/EBITDA, EV/FCF",
            "minimum_substitute": "Latest filing balance sheet with bridge caveat",
        },
        {
            "priority": "P0",
            "needed_item": "LTM financials and period end",
            "why_it_matters": "Denominator quality drives comparability.",
            "affected_output": "LTM multiples and margin context",
            "minimum_substitute": "Latest reported fiscal period with LTM bridge",
        },
        {
            "priority": "P0",
            "needed_item": "Consensus NTM estimates and estimate-as-of date",
            "why_it_matters": "Forward multiples are not usable without estimate source and date.",
            "affected_output": "NTM multiples and selected range",
            "minimum_substitute": "User-provided estimate clearly labeled as assumption",
        },
        {
            "priority": "P1",
            "needed_item": "Peer inclusion/exclusion rationale",
            "why_it_matters": "Prevents cherry-picked peer set.",
            "affected_output": "Selected multiple range and premium/discount logic",
            "minimum_substitute": f"{args.sector or 'Sector'} peer screen with explicit caveats",
        },
        {
            "priority": "P1",
            "needed_item": "Accounting adjustments and non-recurring items",
            "why_it_matters": "Reported and adjusted denominators may not be comparable.",
            "affected_output": "EBITDA, EPS, FCF, sector KPIs",
            "minimum_substitute": "Reported-only view labeled as unadjusted",
        },
    ]


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_screen_grade_workbook(
    output_dir: Path,
    args: argparse.Namespace,
    peer_rows: list[dict[str, str]],
    missing_rows: list[dict[str, str]],
    source_rows: list[dict[str, str]],
) -> Path:
    workbook = output_dir / "screen_grade_comps_framework.xlsx"
    peer_count = max(len(peer_rows) - 1, 0)
    cover_rows = [
        ["Screen-Grade Comps Framework"],
        ["Primary human deliverable", "Yes"],
        ["Target", args.target],
        ["Ticker", args.ticker],
        [
            "Sector / business model",
            f"{args.sector or 'not provided'} / {args.business_model or 'not provided'}",
        ],
        ["Valuation date", args.valuation_date],
        ["Model status", "screen-grade"],
        ["Market data status", args.market_data_status],
        ["Peer candidates included", peer_count],
        [
            "PM decision impact",
            "Framework is useful for peer triage, but not valuation, target, rating, sizing, or circulation until source fields are populated.",
        ],
        [
            "Next workflow",
            "Populate market data and estimates, then run comps-valuation or create a populated comps-valuation workbook.",
        ],
        [
            "Support artifacts",
            "CSV, Markdown, JSON, and logs are hidden support files unless requested.",
        ],
    ]
    tables = {
        "Peer Framework": dict_rows_to_sheet(peer_rows),
        "Missing Data Requests": dict_rows_to_sheet(missing_rows),
        "Source Requirements": dict_rows_to_sheet(source_rows),
    }
    return write_cover_first_workbook(workbook, cover_rows, tables)


def markdown_summary(
    args: argparse.Namespace, peer_rows: list[dict[str, str]], output_dir: Path
) -> str:
    peer_count = max(len(peer_rows) - 1, 0)
    lines = [
        "# Screen-Grade Comparable Companies Framework",
        "",
        "Comps posture: screen-grade; missing market data and/or estimates are explicitly labeled.",
        "",
        "Market data, estimates, EV bridge, and source dates must be populated before decision use.",
        "",
        "## Scope",
        "",
        f"- Target: {args.target} ({args.ticker})",
        f"- Sector / business model: {args.sector or 'not provided'} / {args.business_model or 'not provided'}",
        f"- Valuation date: {args.valuation_date}",
        f"- Peer candidates included: {peer_count}",
        "",
        "## What This Fallback Provides",
        "",
        "- Peer set framework with inclusion/exclusion logic fields.",
        "- Missing-market-data caveats and explicit source requirements.",
        "- Data request list for decision-grade comps work.",
        "- No implied valuation conclusion and no live market-data claim.",
        "",
        "## Initial Peer Framework",
        "",
        "| Company | Ticker | Tier | Role | Market data status | Inclusion logic |",
        "|---|---|---|---|---|---|",
    ]
    for row in peer_rows[:12]:
        lines.append(
            f"| {row['company']} | {row['ticker']} | {row['peer_tier']} | {row['peer_role']} | "
            f"{row['market_data_status']} | {row['inclusion_rationale']} |"
        )
    lines.extend(
        [
            "",
            "## Source Requirements",
            "",
            "| Source area | Required evidence | Evidence label | Minimum acceptable source |",
            "|---|---|---|---|",
        ]
    )
    for area, evidence, label, minimum in SOURCE_REQUIREMENTS:
        lines.append(f"| {area} | {evidence} | {label} | {minimum} |")
    lines.extend(
        [
            "",
            "## Output Files",
            "",
            f"- `peer_framework.csv`: {output_dir / 'peer_framework.csv'}",
            f"- `missing_data_requests.csv`: {output_dir / 'missing_data_requests.csv'}",
            f"- `source_requirements.csv`: {output_dir / 'source_requirements.csv'}",
            f"- `screen_grade_comps_support_note.md`: {output_dir / 'screen_grade_comps_support_note.md'}",
            "",
            "## Next Step",
            "",
            "Populate the required source fields or hand the framework to `comps-valuation` for a screen-grade read-through with explicit caveats.",
        ]
    )
    return "\n".join(lines) + "\n"


def manifest_rows(output_dir: Path, *, workbook_primary: bool = True) -> list[dict[str, Any]]:
    outputs = [
        (
            "workbook",
            "screen_grade_comps_framework.xlsx",
            True,
            "Cover-first screen-grade comps framework workbook.",
            "primary_human_deliverable" if workbook_primary else "support_artifact",
            not workbook_primary,
        ),
        (
            "peer_framework",
            "peer_framework.csv",
            True,
            "Screen-grade peer framework and rationale fields.",
            "support_artifact",
            True,
        ),
        (
            "missing_data_requests",
            "missing_data_requests.csv",
            True,
            "Exact missing items needed for decision-grade comps.",
            "support_artifact",
            True,
        ),
        (
            "source_requirements",
            "source_requirements.csv",
            True,
            "Source hierarchy and evidence labels.",
            "support_artifact",
            True,
        ),
        (
            "support_note",
            "screen_grade_comps_support_note.md",
            True,
            "Human-readable fallback comps support note.",
            "narrative_support",
            True,
        ),
        (
            "run_log",
            "run_log.json",
            True,
            "Status, warnings, hard failures, source basis, and output paths.",
            "machine_support",
            True,
        ),
        (
            "manifest",
            "manifest.json",
            True,
            "Machine-readable output manifest.",
            "machine_support",
            True,
        ),
    ]
    return [
        {
            "key": key,
            "path": str(output_dir / filename),
            "required": required,
            "written": (output_dir / filename).exists(),
            "artifact_role": artifact_role,
            "hidden_unless_requested": hidden,
            "user_visible_default": not hidden,
            "description": description,
            "support_reason": ""
            if not hidden
            else "Support artifact for audit/import/provenance; the XLSX workbook is the first-read deliverable.",
        }
        for key, filename, required, description, artifact_role, hidden in outputs
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Materialize a screen-grade comps fallback framework."
    )
    parser.add_argument(
        "--output-dir", type=Path, default=Path("/tmp/public_equity_investing_comps_fallback")
    )
    parser.add_argument("--target", default="TargetCo")
    parser.add_argument("--ticker", default="TGT")
    parser.add_argument("--sector", default="")
    parser.add_argument("--business-model", default="")
    parser.add_argument("--valuation-date", default=date.today().isoformat())
    parser.add_argument(
        "--market-data-status",
        choices=["missing", "stale", "user-provided", "connector-provided"],
        default="missing",
    )
    parser.add_argument(
        "--peer-csv", type=Path, help="Optional CSV with company/ticker/peer_tier/rationale fields."
    )
    parser.add_argument(
        "--peer-list", default="", help="Comma-separated peers; use TICKER:Company when helpful."
    )
    parser.add_argument("--placeholder-peer-count", type=int, default=8)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    warnings: list[str] = [
        "Screen-grade fallback only; no live market data, EV bridge, estimates, or valuation conclusion is generated.",
        "Populate source requirements before using as a decision-grade comparable-company model.",
    ]
    args.warnings = warnings
    hard_failures: list[str] = []
    try:
        peer_rows = build_peer_framework(args)
        missing_rows = build_missing_data_rows(args)
        source_rows = [
            {
                "source_area": area,
                "required_evidence": evidence,
                "evidence_label": label,
                "minimum_acceptable_source": minimum,
            }
            for area, evidence, label, minimum in SOURCE_REQUIREMENTS
        ]

        write_csv(output_dir / "peer_framework.csv", peer_rows)
        write_csv(output_dir / "missing_data_requests.csv", missing_rows)
        write_csv(output_dir / "source_requirements.csv", source_rows)
        (output_dir / "screen_grade_comps_support_note.md").write_text(
            markdown_summary(args, peer_rows, output_dir), encoding="utf-8"
        )
        write_screen_grade_workbook(output_dir, args, peer_rows, missing_rows, source_rows)
    except Exception as exc:
        hard_failures.append(str(exc))

    outputs = {
        "workbook": str(output_dir / "screen_grade_comps_framework.xlsx"),
        "peer_framework": str(output_dir / "peer_framework.csv"),
        "missing_data_requests": str(output_dir / "missing_data_requests.csv"),
        "source_requirements": str(output_dir / "source_requirements.csv"),
        "support_note": str(output_dir / "screen_grade_comps_support_note.md"),
        "run_log": str(output_dir / "run_log.json"),
        "manifest": str(output_dir / "manifest.json"),
    }
    payload = {
        "status": "failed" if hard_failures else "completed",
        "model_status": "screen-grade" if not hard_failures else "not-decision-ready",
        "artifact_level": "screen_grade_fallback",
        "workbook_mode": "screen_grade_workbook",
        "artifact_mode": "workbook" if not hard_failures else "blocked",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_basis": ["user_input", "explicit_assumption"],
        "warnings": warnings,
        "hard_failures": hard_failures,
        "dependency_status": {
            "python_stdlib": "available",
            "XlsxWriter": "not_required",
            "openpyxl": "not_required",
        },
        "outputs": outputs,
        "primary_human_deliverable": None if hard_failures else outputs["workbook"],
        "support_artifacts_user_visible_default": False,
        "final_response_guidance": {
            "lead_with": "blocked_status" if hard_failures else "primary_human_deliverable",
            "mention_support_artifacts": "only_briefly_unless_requested",
        },
        "output_manifest": [],
    }
    payload["output_manifest"] = manifest_rows(output_dir, workbook_primary=not hard_failures)
    (output_dir / "run_log.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (output_dir / "manifest.json").write_text(
        json.dumps(
            {
                "primary_human_deliverable": payload["primary_human_deliverable"],
                "artifact_mode": payload["artifact_mode"],
                "support_artifacts_user_visible_default": False,
                "final_response_guidance": payload["final_response_guidance"],
                "outputs": payload["output_manifest"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    if hard_failures:
        print("ERROR: " + "; ".join(hard_failures))
        return 1
    print(f"Wrote screen-grade comps fallback to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
