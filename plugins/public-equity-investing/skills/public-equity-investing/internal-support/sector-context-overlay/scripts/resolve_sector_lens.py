#!/usr/bin/env python3
"""Resolve a public-equity-investing sector overlay from prompt text.

The helper is intentionally simple and dependency-free. It gives the agent a
deterministic routing guardrail for ambiguous or cross-sector prompts; it does
not replace investment judgment.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

REFERENCE_FILES = {
    "always": ["archetypes.md", "kpi-cheat-sheet.md", "red-flags.md", "output-overlays.md"],
    "modeling": ["modeling-rules.md", "model-architecture.md"],
    "valuation": ["valuation-rules.md"],
    "source": ["source-hierarchy.md"],
}

SECTOR_RULES: dict[str, dict[str, Any]] = {
    "banks": {
        "folder": "references/banks/",
        "strong": [
            "bank",
            "bancorp",
            "bank holding company",
            "thrift",
            "deposit",
            "deposits",
            "loan loss",
            "nii",
            "net interest income",
            "nim",
            "aoci",
            "cet1",
            "tier 1",
            "tangible book",
            "p/tbv",
        ],
        "weak": ["asset quality", "funding", "credit costs", "commercial real estate", "cre"],
        "first_questions": "deposits, funding confidence, asset quality, capital, NII sensitivity, AOCI/TBV",
    },
    "biotech-pharma": {
        "folder": "references/biotech-pharma/",
        "strong": [
            "biotech",
            "pharma",
            "clinical",
            "phase 1",
            "phase 2",
            "phase 3",
            "pdufa",
            "fda",
            "drug",
            "label",
            "loe",
            "loss of exclusivity",
            "pipeline",
            "rnpv",
            "royalty",
        ],
        "weak": [
            "trial",
            "launch curve",
            "gross-to-net",
            "manufacturing",
            "cash runway",
            "milestone",
        ],
        "first_questions": "asset archetype, probability of success, label, launch curve, LOE, runway",
    },
    "consumer-internet-marketplaces": {
        "folder": "references/consumer-internet-marketplaces/",
        "strong": [
            "marketplace",
            "gmv",
            "gov",
            "gms",
            "take rate",
            "bookings",
            "resale",
            "classifieds",
            "delivery",
            "mobility",
            "travel platform",
            "rideshare",
            "airbnb",
            "uber",
            "doordash",
            "etsy",
            "mercadolibre",
            "incentives",
        ],
        "weak": ["consumer internet", "liquidity", "cohort", "fraud", "trust", "churn"],
        "first_questions": "scarce side, liquidity, GMV/bookings bridge, take rate, incentives, cohort quality",
    },
    "exchanges-market-infrastructure": {
        "folder": "references/exchanges-market-infrastructure/",
        "strong": [
            "exchange",
            "clearing house",
            "ccp",
            "default waterfall",
            "open interest",
            "rpc",
            "net capture",
            "listings",
            "index data",
            "derivatives venue",
            "options exchange",
        ],
        "weak": ["market data", "collateral spread", "trading volume", "outage", "cyber"],
        "first_questions": "volume/open interest, RPC, data/index quality, clearing risk, collateral spread",
    },
    "insurance": {
        "folder": "references/insurance/",
        "strong": [
            "insurance",
            "insurer",
            "reinsurer",
            "combined ratio",
            "loss ratio",
            "reserves",
            "accident year",
            "catastrophe",
            "cat load",
            "reinsurance",
            "statutory capital",
        ],
        "weak": ["premium", "underwriting", "alm", "rbc", "ratings", "holdco", "opco"],
        "first_questions": "reserves, accident-year margin, cat load, reinsurance, ALM, capital regime",
    },
    "oil-gas-ep": {
        "folder": "references/oil-gas-ep/",
        "strong": [
            "e&p",
            "exploration and production",
            "upstream",
            "pdp",
            "pud",
            "shale",
            "basin",
            "decline curve",
            "rbl",
            "wt i",
            "wti",
            "henry hub",
            "proved reserves",
        ],
        "weak": ["production", "hedges", "differentials", "abandonment", "maintenance capex"],
        "first_questions": "basin, commodity mix, reserves, decline curve, inventory, hedges, RBL risk",
    },
    "reits": {
        "folder": "references/reits/",
        "strong": [
            "reit",
            "ffo",
            "affo",
            "same-store noi",
            "leasing spread",
            "occupancy",
            "nav",
            "cap rate",
            "landlord",
            "rent roll",
            "net lease",
            "industrial reit",
            "apartment reit",
            "office reit",
            "retail reit",
            "data center reit",
            "tower reit",
            "digital realty",
            "equinix",
        ],
        "weak": ["property", "tenant", "lease", "dividend sustainability", "debt maturity wall"],
        "first_questions": "property type, same-store NOI, occupancy, leasing spreads, FFO/AFFO, NAV",
    },
    "saas-subscription-software": {
        "folder": "references/saas-subscription-software/",
        "strong": [
            "saas",
            "software",
            "arr",
            "rpo",
            "remaining performance obligations",
            "billings",
            "net retention",
            "gross retention",
            "nrr",
            "grr",
            "subscription",
            "cloud software",
            "consumption data platform",
            "cybersecurity saas",
            "snowflake",
            "rapid7",
            "cloudflare",
            "datadog",
            "crowdstrike",
            "zscaler",
            "okta",
            "mongodb",
            "servicenow",
            "salesforce",
        ],
        "weak": [
            "churn",
            "cac payback",
            "rule of 40",
            "sbc",
            "ai workloads",
            "large-customer growth",
        ],
        "first_questions": "ARR/revenue bridge, billings/RPO, retention, churn, CAC payback, SBC, FCF quality",
    },
}


MANDATE_RULES = {
    "long_only": [
        "long-only",
        "long only",
        "benchmark",
        "active weight",
        "core holding",
        "portfolio weight",
    ],
    "long_short": [
        "long/short",
        "hedge fund",
        "short",
        "pair trade",
        "borrow",
        "cover",
        "gross",
        "net exposure",
    ],
    "sell_side": [
        "sell-side",
        "sell side",
        "rating",
        "target price",
        "initiation",
        "coverage",
        "client note",
    ],
    "etf_index": [
        "etf",
        "index",
        "constituent",
        "rebalance",
        "russell",
        "s&p",
        "msci",
        "passive flow",
        "float",
    ],
    "diligence": [
        "diligence",
        "underwrite",
        "source packet",
        "governance",
        "accounting quality",
        "management credibility",
    ],
    "model": ["model", "forecast", "dcf", "three-statement", "comps", "valuation"],
    "earnings": ["earnings", "print", "quarter", "guidance", "transcript"],
    "event": ["event", "catalyst", "merger", "spin", "tender", "lockup", "offering"],
}

MANDATE_REQUIREMENTS = {
    "long_only": [
        "benchmark-relative risk",
        "portfolio role",
        "downside capture",
        "add/trim discipline",
    ],
    "long_short": ["variant wedge", "catalyst timing", "borrow/crowding", "cover or exit triggers"],
    "sell_side": [
        "rating/target implication",
        "estimate revision bridge",
        "Street debate",
        "risk-to-rating",
    ],
    "etf_index": [
        "index methodology",
        "constituent weight",
        "float/liquidity",
        "passive flow relevance",
    ],
    "diligence": ["business quality", "governance", "accounting quality", "next source needed"],
    "model": ["driver hierarchy", "valuation convention", "model line affected", "sensitivity"],
    "earnings": ["estimate path", "KPI debate", "revision risk", "next falsifier"],
    "event": ["event path", "probability", "payoff", "liquidity/exit risk"],
}

MODE_KEYWORDS = {
    "modeling": [
        "model",
        "forecast",
        "three-statement",
        "dcf",
        "sensitivity",
        "scenario",
        "underwrite",
    ],
    "valuation": ["valuation", "multiple", "comps", "price target", "nav", "sotp", "rn pv", "rnpv"],
    "source": ["source", "provenance", "conflict", "citation", "filing", "transcript", "deck"],
}


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9%&./+ -]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def phrase_hits(text: str, phrases: list[str]) -> list[str]:
    hits = []
    padded = f" {text} "
    for phrase in phrases:
        needle = normalize(phrase)
        if not needle:
            continue
        if " " in needle or "/" in needle or "&" in needle:
            if needle in text:
                hits.append(phrase)
        elif re.search(rf"(?<![a-z0-9]){re.escape(needle)}(?![a-z0-9])", padded):
            hits.append(phrase)
    return hits


def score_prompt(prompt: str) -> dict[str, dict[str, Any]]:
    text = normalize(prompt)
    scores: dict[str, dict[str, Any]] = {}
    for sector, rules in SECTOR_RULES.items():
        strong_hits = phrase_hits(text, list(rules["strong"]))
        weak_hits = phrase_hits(text, list(rules["weak"]))
        score = (3 * len(strong_hits)) + len(weak_hits)
        scores[sector] = {
            "score": score,
            "strong_hits": strong_hits,
            "weak_hits": weak_hits,
            "folder": rules["folder"],
            "first_questions": rules["first_questions"],
        }
    return scores


def selected_reference_files(prompt: str) -> list[str]:
    text = normalize(prompt)
    files = list(REFERENCE_FILES["always"])
    for mode, keywords in MODE_KEYWORDS.items():
        if phrase_hits(text, keywords):
            files.extend(REFERENCE_FILES[mode])
    return list(dict.fromkeys(files))


def detect_mandates(prompt: str) -> list[str]:
    text = normalize(prompt)
    mandates: list[str] = []
    for mandate, keywords in MANDATE_RULES.items():
        if phrase_hits(text, keywords):
            mandates.append(mandate)
    return mandates or ["public_equity_diligence"]


def mandate_output_requirements(mandates: list[str]) -> dict[str, list[str]]:
    return {mandate: MANDATE_REQUIREMENTS.get(mandate, []) for mandate in mandates}


def resolve(prompt: str) -> dict[str, Any]:
    mandates = detect_mandates(prompt)
    scores = score_prompt(prompt)
    ranked = sorted(scores.items(), key=lambda item: item[1]["score"], reverse=True)
    primary, primary_data = ranked[0]
    secondary = [{"sector": sector, **data} for sector, data in ranked[1:4] if data["score"] > 0]
    top_score = int(primary_data["score"])
    second_score = int(secondary[0]["score"]) if secondary else 0

    if top_score == 0:
        confidence = "unsupported"
        primary_sector = None
    elif top_score >= 6 and top_score >= (second_score * 2):
        confidence = "high"
        primary_sector = primary
    elif top_score >= 4 and top_score > second_score:
        confidence = "medium"
        primary_sector = primary
    else:
        confidence = "ambiguous"
        primary_sector = primary

    notes: list[str] = []
    if confidence == "unsupported":
        notes.append(
            "No local sector overlay matched; use the primary Public Equity Investing skill without a sector overlay."
        )
    elif confidence == "ambiguous":
        notes.append(
            "Multiple sector lenses matched; choose the economics that drive the investment case and cite secondary lenses."
        )
    elif secondary:
        notes.append("Secondary sector clues exist; state why the primary lens controls.")

    return {
        "primary_sector": primary_sector,
        "confidence": confidence,
        "selected_folder": primary_data["folder"] if primary_sector else None,
        "selected_reference_files": selected_reference_files(prompt) if primary_sector else [],
        "first_questions": primary_data["first_questions"] if primary_sector else None,
        "mandate_lenses": mandates,
        "mandate_output_requirements": mandate_output_requirements(mandates),
        "secondary_lenses": secondary,
        "all_scores": scores,
        "routing_notes": notes,
    }


def markdown(result: dict[str, Any]) -> str:
    if not result["primary_sector"]:
        return "\n".join(
            [
                "# Sector Lens Resolution",
                "",
                "Primary sector: **unsupported**",
                "Confidence: **unsupported**",
                "",
                "Use the owning Public Equity Investing skill without a local sector overlay.",
            ]
        )

    lines = [
        "# Sector Lens Resolution",
        "",
        f"Primary sector: **{result['primary_sector']}**",
        f"Confidence: **{result['confidence']}**",
        f"Reference folder: `{result['selected_folder']}`",
        "Reference files: " + ", ".join(f"`{name}`" for name in result["selected_reference_files"]),
        "",
        f"First questions: {result['first_questions']}",
        "Mandate lenses: " + ", ".join(f"`{name}`" for name in result.get("mandate_lenses", [])),
    ]
    if result["secondary_lenses"]:
        lines.append("")
        lines.append("Secondary lenses:")
        for item in result["secondary_lenses"]:
            lines.append(
                f"- `{item['sector']}` score {item['score']}: {', '.join(item['strong_hits'] + item['weak_hits'])}"
            )
    if result["routing_notes"]:
        lines.append("")
        lines.extend(f"- {note}" for note in result["routing_notes"])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resolve the Public Equity Investing sector-context-overlay lens."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--prompt", help="Prompt or issuer description to classify.")
    source.add_argument(
        "--prompt-file", type=Path, help="Text file containing the prompt or issuer description."
    )
    parser.add_argument("--json-out", type=Path, help="Optional JSON output path.")
    parser.add_argument("--markdown-out", type=Path, help="Optional Markdown output path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    prompt = (
        args.prompt if args.prompt is not None else args.prompt_file.read_text(encoding="utf-8")
    )
    result = resolve(prompt)

    payload = json.dumps(result, indent=2)
    print(payload)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(payload + "\n", encoding="utf-8")
    if args.markdown_out:
        args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_out.write_text(markdown(result) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
