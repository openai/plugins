#!/usr/bin/env python3
"""Check economic-impact report/support-note text for required structure and source posture."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REQUIRED_SECTIONS = [
    "executive call",
    "event status and market baseline",
    "what is new vs expected",
    "public equity framing",
    "ranked equity impact map",
    "what is priced in vs what requires proof",
    "scenario matrix",
    "monitoring triggers and research queue",
    "what would change the view",
    "bottom line judgment",
]

REQUIRED_SECTION_ALIASES = {
    "transmission map": {"transmission map", "event to equity transmission map"},
}

SOURCE_TERMS = [
    "source and freshness",
    "data cut-off",
    "data cutoff",
    "as of",
    "sources used",
    "source register",
    "retrieved",
    "published",
]

SOURCE_SECTION_HEADINGS = {
    "source and freshness",
    "sources and freshness",
    "source freshness",
    "source posture",
    "source register",
    "source inventory",
    "evidence posture",
    "evidence and freshness",
}

SOURCE_FIELD_ALIASES = {
    "data_cutoff": {
        "data cut off",
        "data cutoff",
        "data cut",
        "as of",
        "as of date",
        "accessed",
        "accessed at",
        "retrieved",
        "retrieved at",
        "freeze time",
        "data freeze",
    },
    "sources_used": {
        "source used",
        "sources used",
        "sources",
        "source register",
        "source inventory",
        "source ids",
        "source id",
    },
    "stale_or_missing_data": {
        "stale or missing data",
        "missing or stale data",
        "stale missing data",
        "stale data",
        "missing data",
        "open evidence gaps",
        "evidence gaps",
        "missing evidence",
        "open source gaps",
        "source gaps",
    },
    "evidence_posture": {
        "evidence posture",
        "source posture",
        "source quality",
        "evidence quality",
    },
}

WEAK_EVIDENCE_PATTERNS = [
    r"\bweak\b",
    r"\blow confidence\b",
    r"\bnot supportable\b",
    r"\bassumption[- ]led\b",
    r"\bassumption[_ -]inferred\b",
    r"\bassumption[_ -]user[_ -]provided\b",
    r"\bpreliminary\b",
    r"\bunverified\b",
    r"\buncorroborated\b",
    r"\brumou?r\b",
    r"\bnews only\b",
    r"\bsecondary only\b",
    r"\bsingle source\b",
    r"\bno primary\b",
    r"\bunknown\b",
    r"\bunknown freshness\b",
    r"\bunsourced\b",
    r"\bnot available\b",
    r"\bunavailable\b",
    r"\bpending\b",
    r"\bmissing_required_source\b",
    r"\bunknown\b",
]

STALE_EVIDENCE_PATTERNS = [
    r"\bstale\b",
    r"\bstale_source\b",
    r"\boutdated\b",
    r"\bsuperseded\b",
    r"\bpotentially superseded\b",
    r"\bold quote\b",
    r"\bold price\b",
    r"\bno timestamp\b",
    r"\bno as[- ]of\b",
]

NO_MATERIAL_GAP_PATTERNS = [
    r"^none$",
    r"^none material$",
    r"^not material$",
    r"^n/?a$",
    r"^no material gaps?$",
    r"^no material source gaps?$",
    r"^no material evidence gaps?$",
    r"^no stale or missing data$",
    r"^no material stale or missing data$",
]

PLACEHOLDER_PATTERNS = [
    r"\[[^\]]+\]",
    r"\bTBD\b",
    r"\bTODO\b",
    r"\.\.\.",
]


def normalize_heading(text: str) -> str:
    text = re.sub(r"^#+\s*", "", text.strip()).lower()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def headings(markdown: str) -> set[str]:
    out: set[str] = set()
    for line in markdown.splitlines():
        if line.startswith("## "):
            out.add(normalize_heading(line))
    return out


def has_source_posture(markdown: str) -> bool:
    lowered = markdown.lower()
    return any(term in lowered for term in SOURCE_TERMS)


def source_section(markdown: str) -> str:
    section_lines: list[str] = []
    in_section = False
    for line in markdown.splitlines():
        if line.startswith("## "):
            if in_section:
                break
            in_section = normalize_heading(line) in SOURCE_SECTION_HEADINGS
            continue
        if in_section:
            section_lines.append(line)
    return "\n".join(section_lines).strip()


def compact_value(value: str) -> str:
    value = re.sub(r"\s+", " ", value.strip().lower())
    return value.strip(" .;:-")


def is_placeholder_value(value: str) -> bool:
    compact = compact_value(value)
    if compact in {
        "",
        "tbd",
        "todo",
        "unknown",
        "pending",
        "not available",
        "unavailable",
        "n/a",
        "na",
    }:
        return True
    return any(
        re.fullmatch(pattern, value.strip(), flags=re.IGNORECASE)
        for pattern in PLACEHOLDER_PATTERNS
    )


def matches_any(value: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, value, flags=re.IGNORECASE) for pattern in patterns)


def no_material_gap(value: str) -> bool:
    compact = compact_value(value)
    return any(
        re.fullmatch(pattern, compact, flags=re.IGNORECASE) for pattern in NO_MATERIAL_GAP_PATTERNS
    )


def source_field_values(section: str) -> dict[str, list[str]]:
    values: dict[str, list[str]] = {key: [] for key in SOURCE_FIELD_ALIASES}
    for line in section.splitlines():
        stripped = re.sub(r"^\s*[-*]\s*", "", line.strip())
        if ":" not in stripped:
            continue
        raw_key, raw_value = stripped.split(":", 1)
        key = normalize_heading(raw_key)
        value = raw_value.strip()
        for field, aliases in SOURCE_FIELD_ALIASES.items():
            if key in aliases:
                values[field].append(value)
                break
    return values


def joined(values: list[str]) -> str:
    return " ".join(value for value in values if value).strip()


def source_freshness_issues(markdown: str) -> list[str]:
    section = source_section(markdown)
    if not section:
        if has_source_posture(markdown):
            return ["source/freshness posture is not in a dedicated Source And Freshness section"]
        return ["missing source/freshness posture: add a Source And Freshness section"]

    values = source_field_values(section)
    issues: list[str] = []

    data_cutoff = joined(values["data_cutoff"])
    if not data_cutoff:
        issues.append("missing data cut-off/as-of date in Source And Freshness")
    elif is_placeholder_value(data_cutoff):
        issues.append(
            "weak source/freshness posture: data cut-off/as-of date is blank, unknown, or placeholder"
        )

    sources_used = joined(values["sources_used"])
    if not sources_used:
        issues.append("missing sources used/source register in Source And Freshness")
    elif is_placeholder_value(sources_used) or matches_any(sources_used, WEAK_EVIDENCE_PATTERNS):
        issues.append(
            "weak source evidence: sources used/source register is blank, unknown, or relies on weak evidence"
        )

    stale_or_missing = joined(values["stale_or_missing_data"])
    if not stale_or_missing:
        issues.append("missing stale/missing-data assessment in Source And Freshness")
    elif not no_material_gap(stale_or_missing):
        if is_placeholder_value(stale_or_missing) or matches_any(
            stale_or_missing, WEAK_EVIDENCE_PATTERNS
        ):
            issues.append(
                "missing evidence disclosed in Source And Freshness: unresolved source gaps remain"
            )
        elif matches_any(stale_or_missing, STALE_EVIDENCE_PATTERNS):
            issues.append("stale evidence disclosed in Source And Freshness")

    evidence_posture = joined(values["evidence_posture"])
    if evidence_posture and (
        is_placeholder_value(evidence_posture)
        or matches_any(evidence_posture, WEAK_EVIDENCE_PATTERNS)
    ):
        issues.append("weak evidence posture disclosed in Source And Freshness")

    return issues


def placeholder_hits(markdown: str) -> list[str]:
    hits: list[str] = []
    for pattern in PLACEHOLDER_PATTERNS:
        for match in re.findall(pattern, markdown, flags=re.IGNORECASE):
            hits.append(str(match))
    return hits[:25]


def check(markdown: str, mode: str = "delivery") -> dict:
    if mode not in {"draft", "delivery"}:
        raise ValueError("mode must be 'draft' or 'delivery'")
    found = headings(markdown)
    missing = [section for section in REQUIRED_SECTIONS if section not in found]
    missing.extend(
        label for label, aliases in REQUIRED_SECTION_ALIASES.items() if found.isdisjoint(aliases)
    )
    placeholders = placeholder_hits(markdown)
    warnings: list[str] = []
    source_issues = source_freshness_issues(markdown)
    if mode == "delivery":
        errors: list[str] = source_issues.copy()
    else:
        errors = []
        warnings.extend(source_issues)
    if len(markdown.split()) < 250:
        warnings.append("report appears short for a decision-grade economic impact report")
    if missing:
        errors.append("missing required sections: " + ", ".join(missing))
    if placeholders:
        errors.append("unresolved placeholders detected")
    return {
        "valid": not errors,
        "mode": mode,
        "errors": errors,
        "warnings": warnings,
        "source_freshness_issues": source_issues,
        "missing_sections": missing,
        "placeholder_hits": placeholders,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate economic-impact report markdown structure."
    )
    parser.add_argument(
        "--mode",
        choices=["draft", "delivery"],
        default="delivery",
        help="draft warns on source/freshness gaps; delivery fails missing, stale, or weak evidence posture",
    )
    parser.add_argument("report_md", type=Path)
    args = parser.parse_args()
    try:
        result = check(args.report_md.read_text(encoding="utf-8"), mode=args.mode)
    except Exception as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)], "warnings": []}, indent=2))
        return 1
    print(json.dumps(result, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
