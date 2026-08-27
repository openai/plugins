"""Issue-detection logic for the Public Equity Investing deck/report QC helper."""

from __future__ import annotations

import math
import re
from collections import defaultdict

SOURCE_TERMS = re.compile(
    r"\b(source|sources|note|notes|footnote|as of|as-of|company filing|"
    r"filings|10-k|10-q|8-k|transcript|press release|factset|bloomberg|"
    r"capital iq|s&p|lseg|refinitiv|morningstar|moody|fitch|management|"
    r"issuer|company presentation|investor presentation|model|internal "
    r"estimate|consensus)\b",
    re.I,
)
DATE_TERMS = re.compile(
    r"\b(as of|as-of|through|dated|date|period ended|fye|fiscal year|"
    r"quarter ended|q[1-4]|fy\d{2,4}|cy\d{2,4}|ltm|ntm|ytd|"
    r"\d{1,2}/\d{1,2}/\d{2,4}|\d{4}-\d{2}-\d{2}|jan\.?|feb\.?|"
    r"mar\.?|apr\.?|may|jun\.?|jul\.?|aug\.?|sep\.?|sept\.?|oct\.?|"
    r"nov\.?|dec\.?)\b",
    re.I,
)
MARKET_TERMS = re.compile(
    r"\b(share price|stock price|market cap|enterprise value|ev|equity "
    r"value|yield|spread|bps|rate|fx|commodity|index|multiple|consensus|"
    r"estimate|short interest|volume|price target|valuation|trading|"
    r"credit spread)\b",
    re.I,
)
CLAIM_WORDS = re.compile(
    r"\b(best[- ]in[- ]class|market leader|clear leader|dominant|unique|"
    r"proprietary|significant|compelling|attractive|resilient|defensible|"
    r"downside protected|conservative|undervalued|overvalued|mispriced|"
    r"strong visibility|high quality|mission critical)\b",
    re.I,
)


def add_issue(
    issues: list[dict[str, str]],
    severity: str,
    issue_type: str,
    confidence: str,
    source_file: str,
    location: str,
    metric_or_claim: str,
    finding: str,
    evidence: str,
    why: str,
    fix: str,
    route: str = "deck-report-qc",
) -> None:
    issues.append(
        {
            "issue_id": f"QC-{len(issues) + 1:03d}",
            "severity": severity,
            "issue_type": issue_type,
            "confidence": confidence,
            "source_file": source_file,
            "location": location,
            "metric_or_claim": metric_or_claim,
            "finding": finding,
            "evidence": evidence,
            "why_it_matters": why,
            "suggested_fix": fix,
            "owner_route": route,
            "status": "open",
        }
    )


def analyze_segment_sources(
    issues: list[dict[str, str]],
    seg: dict[str, str],
    seg_nums: list[dict[str, str]],
) -> None:
    text = seg.get("text", "") or ""
    number_count = len(seg_nums)
    source_present = bool(SOURCE_TERMS.search(text))
    date_present = bool(DATE_TERMS.search(text))
    market_present = bool(MARKET_TERMS.search(text))
    if number_count >= 5 and not source_present:
        add_issue(
            issues,
            "medium",
            "source_gap",
            "possible",
            seg["source_file"],
            seg["location"],
            "data-heavy page/section",
            "material numerical content appears without an obvious source footnote",
            f"{number_count} numerical mentions detected; no source terms detected",
            "unsupported numbers reduce senior-review confidence and make tie-out difficult",
            "add source, period/as-of date, and relevant caveats",
            "financial-source-of-truth",
        )
    elif number_count >= 5 and source_present and market_present and not date_present:
        add_issue(
            issues,
            "medium",
            "source_gap",
            "possible",
            seg["source_file"],
            seg["location"],
            "market-sensitive data",
            "market-sensitive numerical content has a source but no obvious as-of date",
            "source terms and market terms detected, but no date/as-of term detected",
            "market data can become stale quickly",
            "add as-of date or period for market/consensus data",
            "financial-source-of-truth",
        )


def suffix_set(seg_nums: list[dict[str, str]]) -> set[str]:
    suffixes: set[str] = set()
    for number_row in seg_nums:
        raw_value = number_row["raw_value"].lower()
        if re.search(r"\b(mm|m|million)\b|\d(mm|m)$", raw_value):
            suffixes.add("millions")
        if re.search(r"\b(bn|b|billion)\b|\d(bn|b)$", raw_value):
            suffixes.add("billions")
        if "%" in raw_value:
            suffixes.add("percent")
        if "bp" in raw_value:
            suffixes.add("bps")
    return suffixes


def analyze_segment_units(
    issues: list[dict[str, str]],
    seg: dict[str, str],
    seg_nums: list[dict[str, str]],
) -> None:
    suffixes = suffix_set(seg_nums)
    if {"millions", "billions"}.issubset(suffixes):
        add_issue(
            issues,
            "needs_review",
            "unit_or_period_ambiguity",
            "possible",
            seg["source_file"],
            seg["location"],
            "mixed scale",
            "both million and billion scale markers appear in the same page/section",
            ", ".join(sorted(suffixes)),
            "mixed scale may be correct, but should be explicit in table headers and labels",
            "confirm units are intentional and label scale clearly",
        )
    if {"percent", "bps"}.issubset(suffixes):
        add_issue(
            issues,
            "needs_review",
            "unit_or_period_ambiguity",
            "possible",
            seg["source_file"],
            seg["location"],
            "percent vs bps",
            "both percent and bps markers appear in the same page/section",
            ", ".join(sorted(suffixes)),
            "percentage levels and percentage-point changes are often confused",
            "confirm bps/percentage-point convention in labels and bullets",
        )


def analyze_segment_claims(
    issues: list[dict[str, str]],
    seg: dict[str, str],
    seg_nums: list[dict[str, str]],
) -> None:
    text = seg.get("text", "") or ""
    source_present = bool(SOURCE_TERMS.search(text))
    claim_match = CLAIM_WORDS.search(text)
    if claim_match and len(seg_nums) < 2 and not source_present:
        claim = claim_match.group(0)
        add_issue(
            issues,
            "needs_review",
            "narrative_contradiction",
            "possible",
            seg["source_file"],
            seg["location"],
            claim,
            "strong qualitative claim appears with limited visible support",
            claim,
            "senior reviewers will expect evidence for strong claims",
            "add support, soften language, or route to evidence ledger",
            "financial-source-of-truth",
        )


def analyze_repeated_metrics(
    issues: list[dict[str, str]],
    numbers: list[dict[str, str]],
) -> None:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for number_row in numbers:
        if number_row["metric_key"] and number_row["metric_key"] != "unknown":
            groups[number_row["metric_key"]].append(number_row)

    for key, rows in groups.items():
        if len(rows) < 2:
            continue
        locs = sorted({row["location"] for row in rows})
        values_by_unit: dict[str, list[float]] = defaultdict(list)
        for row in rows:
            try:
                values_by_unit[row["unit_class"]].append(float(row["normalized_value"]))
            except Exception:
                pass
        for unit_class, values in values_by_unit.items():
            uniq = sorted({round(v, 4) for v in values if math.isfinite(v)})
            if len(uniq) < 2:
                continue
            lo, hi = min(uniq), max(uniq)
            denom = max(abs(hi), abs(lo), 1.0)
            diff_pct = abs(hi - lo) / denom
            threshold = 0.005 if unit_class in {"percent", "bps", "multiple"} else 0.01
            if diff_pct >= threshold:
                examples = [
                    f"{row['location']}: {row['raw_value']} ({row['context'][:120]})"
                    for row in rows[:8]
                ]
                add_issue(
                    issues,
                    "needs_review",
                    "number_mismatch",
                    "possible",
                    rows[0]["source_file"],
                    "; ".join(locs[:6]),
                    key,
                    "same detected metric key appears with different values across locations",
                    " | ".join(examples),
                    "repeated metrics should tie unless period, unit, scenario, or definition differs",
                    "verify period/unit/scenario; update summary and detail pages to controlling value",
                    "model-audit-tieout",
                )


def analyze_segments(
    segments: list[dict[str, str]],
    numbers: list[dict[str, str]],
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    for seg in segments:
        text = seg.get("text", "") or ""
        if not text.strip():
            continue
        seg_nums = [
            number_row
            for number_row in numbers
            if number_row["source_file"] == seg["source_file"]
            and number_row["location"] == seg["location"]
        ]
        analyze_segment_sources(issues, seg, seg_nums)
        analyze_segment_units(issues, seg, seg_nums)
        analyze_segment_claims(issues, seg, seg_nums)

    analyze_repeated_metrics(issues, numbers)
    return issues


def posture_from_issues(issues: list[dict[str, str]]) -> str:
    severities = [issue["severity"] for issue in issues]
    targeted_issue_types = {"source_gap", "number_mismatch", "unit_or_period_ambiguity"}
    if "critical" in severities:
        return "not-circulable"
    if "high" in severities:
        return "needs-targeted-fixes"
    if "medium" in severities:
        return "needs-targeted-fixes"
    if any(issue["issue_type"] in targeted_issue_types for issue in issues):
        return "needs-targeted-fixes"
    if "needs_review" in severities:
        return "needs-targeted-fixes"
    if issues:
        return "senior-review-ready"
    return "first-pass-clear"
