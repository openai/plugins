#!/usr/bin/env python3
"""Summarize leaks output from an Apple .memgraph file."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path


LEAK_RE = re.compile(r"^Leak:\s+(?P<address>0x[0-9a-fA-F]+)\s+size=(?P<size>\d+)\s+(?P<rest>.*)$")
TOTAL_RE = re.compile(r"Process\s+\S+:\s+(?P<count>\d+)\s+leaks?\s+for\s+(?P<bytes>\d+)\s+total leaked bytes")


def run_leaks(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["leaks", *args], text=True, capture_output=True, check=False)


def parse_leaks(output: str) -> tuple[str | None, list[dict[str, str]]]:
    total = None
    leaks: list[dict[str, str]] = []
    for line in output.splitlines():
        if total is None:
            match = TOTAL_RE.search(line)
            if match:
                total = f"{match.group('count')} leaks / {match.group('bytes')} bytes"
        match = LEAK_RE.match(line)
        if match:
            fields = match.groupdict()
            rest = fields.pop("rest")
            rest = re.sub(r"^zone:\s+\S+\s+", "", rest)
            parts = re.split(r"\s{2,}", rest.strip(), maxsplit=2)
            if len(parts) == 3:
                fields["type"], fields["language"], fields["image"] = parts
            elif len(parts) == 2:
                fields["type"], fields["image"] = parts
                fields["language"] = "<unknown>"
            else:
                fields["type"] = rest.strip() or "<unknown>"
                fields["language"] = "<unknown>"
                fields["image"] = "<unknown>"
            leaks.append(fields)
    return total, leaks


def trace_excerpt(memgraph: Path, address: str, max_lines: int) -> str:
    result = run_leaks([f"--traceTree={address}", str(memgraph)])
    text = result.stdout or result.stderr
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines[:max_lines])


def group_by_type_excerpt(memgraph: Path, max_lines: int) -> str:
    result = run_leaks(["--groupByType", str(memgraph)])
    text = result.stdout or result.stderr
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines[:max_lines])


def render(memgraph: Path, trace_limit: int, trace_lines: int, raw_output: str) -> str:
    total, leaks = parse_leaks(raw_output)
    by_type = Counter(leak["type"] for leak in leaks)
    by_image = Counter(leak["image"] for leak in leaks)

    lines: list[str] = []
    lines.append(f"# Leak Summary: {memgraph}")
    lines.append("")
    lines.append(f"- Total: {total or 'not found'}")
    lines.append(f"- Parsed leak entries: {len(leaks)}")
    lines.append("")

    if by_type:
        lines.append("## Top Types")
        for name, count in by_type.most_common(20):
            lines.append(f"- {count}x {name}")
        lines.append("")

    if by_image:
        lines.append("## Top Images")
        for name, count in by_image.most_common(20):
            lines.append(f"- {count}x {name}")
        lines.append("")

    if leaks:
        lines.append("## Leak Entries")
        for leak in leaks[:50]:
            lines.append(
                f"- {leak['address']} size={leak['size']} type={leak['type']} "
                f"image={leak['image']}"
            )
        if len(leaks) > 50:
            lines.append(f"- ... {len(leaks) - 50} more")
        lines.append("")

    if trace_limit > 0 and leaks:
        lines.append("## TraceTree Excerpts")
        for leak in leaks[:trace_limit]:
            lines.append(f"### {leak['address']} {leak['type']}")
            excerpt = trace_excerpt(memgraph, leak["address"], trace_lines)
            lines.append("~~~text")
            lines.append(excerpt or "<no trace output>")
            lines.append("~~~")
            lines.append("")

    if leaks:
        lines.append("## Grouped Leak Tree")
        lines.append("Use this when `traceTree` has no roots, which is common for unreachable retain cycles.")
        lines.append("~~~text")
        lines.append(group_by_type_excerpt(memgraph, trace_lines) or "<no grouped leak output>")
        lines.append("~~~")
        lines.append("")

    lines.append("## Raw Commands")
    lines.append("~~~bash")
    lines.append(f"leaks --list {memgraph}")
    if leaks:
        lines.append(f"leaks --groupByType {memgraph}")
    if leaks:
        lines.append(f"leaks --traceTree={leaks[0]['address']} {memgraph}")
    lines.append("~~~")
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("memgraph", type=Path)
    parser.add_argument("--trace-limit", type=int, default=0, help="Number of leaks to trace with --traceTree")
    parser.add_argument("--trace-lines", type=int, default=80, help="Max lines per traceTree excerpt")
    parser.add_argument("--out", type=Path, help="Write markdown summary to this file")
    args = parser.parse_args()

    if not args.memgraph.exists():
        print(f"memgraph not found: {args.memgraph}", file=sys.stderr)
        return 2

    result = run_leaks(["--list", str(args.memgraph)])
    raw = result.stdout or result.stderr
    total, leaks = parse_leaks(raw)
    if result.returncode != 0 and total is None and not leaks:
        print(raw, file=sys.stderr, end="" if raw.endswith("\n") else "\n")
        return result.returncode or 1

    summary = render(args.memgraph, args.trace_limit, args.trace_lines, raw)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(summary)
        print(args.out)
    else:
        print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
