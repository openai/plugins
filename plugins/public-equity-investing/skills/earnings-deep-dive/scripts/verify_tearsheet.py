#!/usr/bin/env python3
"""Lightweight tear sheet QA.

Checks:
- Required section headers exist
- No unrendered {PLACEHOLDER} tokens remain
- Beat/Miss and Guidance tables exist and include a SourceTag column
- Table rows do not have empty SourceTag cells
- Warn if tear sheet is likely >1 page (heuristic by line count)

Exit codes:
  0 = pass (warnings may exist)
  1 = fail
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def _find_table_block(lines: list[str], header_pattern: str) -> list[str]:
    # Find the first markdown table after a header
    for i, line in enumerate(lines):
        if re.match(header_pattern, line.strip()):
            # scan forward for the first table header line
            for j in range(i + 1, min(i + 50, len(lines))):
                if lines[j].strip().startswith("|") and "SourceTag" in lines[j]:
                    # take until blank line
                    block = []
                    for k in range(j, len(lines)):
                        if not lines[k].strip():
                            break
                        block.append(lines[k])
                    return block
    return []


def main() -> int:
    if any(arg in {"-h", "--help"} for arg in sys.argv[1:]):
        print("Usage: python scripts/verify_tearsheet.py output/TearSheet.md")
        return 0
    if len(sys.argv) != 2:
        print("Usage: python scripts/verify_tearsheet.py output/TearSheet.md")
        return 1

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"ERROR: Tear sheet not found: {path}")
        return 1

    txt = path.read_text(encoding="utf-8")
    lines = txt.splitlines()

    errors: list[str] = []
    warnings: list[str] = []

    # Required sections
    required_headers = [
        "## Beat/Miss vs expectations",
        "## Guidance delta",
        "## Drivers",
        "## Key quotes",
        "## Model impact",
        "## Watch list",
    ]
    for h in required_headers:
        if h not in txt:
            errors.append(f"Missing required section header: {h}")

    # Unrendered placeholders
    if re.search(r"\{[A-Z0-9_]+\}", txt):
        errors.append("Found unrendered {PLACEHOLDER} token(s)")
    if re.search(r"\bTODO\b", txt):
        errors.append("Found TODO placeholder token(s)")
    unresolved_missing = re.findall(
        r"MISSING:\s*(add|explain|map|summarize|write|list|populate|decompose)[^\n]*",
        txt,
        flags=re.IGNORECASE,
    )
    if unresolved_missing:
        errors.append("Found unresolved authoring placeholder(s) beginning with MISSING:")

    # Tables
    beat_tbl = _find_table_block(lines, r"^## Beat/Miss vs expectations$")
    guid_tbl = _find_table_block(lines, r"^## Guidance delta$")

    if not beat_tbl:
        errors.append("Beat/Miss table not found or missing SourceTag column")
    if not guid_tbl:
        errors.append("Guidance table not found or missing SourceTag column")

    def _check_src_cells(tbl: list[str], label: str):
        # Skip first two lines (header + separator)
        for row in tbl[2:]:
            if not row.strip().startswith("|"):
                continue
            cells = [c.strip() for c in row.strip().strip("|").split("|")]
            if len(cells) < 1:
                continue
            src = cells[-1]
            if src == "":
                errors.append(f"{label}: empty SourceTag cell")

    if beat_tbl:
        _check_src_cells(beat_tbl, "Beat/Miss")
    if guid_tbl:
        _check_src_cells(guid_tbl, "Guidance")

    # 1-page heuristic
    if len(lines) > 140:
        warnings.append(
            f"Tear sheet is {len(lines)} lines; may exceed one page depending on formatting"
        )

    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print(f"  - {w}")

    if errors:
        print("ERRORS:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("Tear sheet QA passed (warnings may exist).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
