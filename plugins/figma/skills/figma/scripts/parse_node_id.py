#!/usr/bin/env python3
"""Extract a Figma file key and node-id from a Figma URL (draft helper)."""

from __future__ import annotations

import re
import sys
from urllib.parse import parse_qs, urlparse


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: parse_node_id.py <figma-url>", file=sys.stderr)
        return 2

    url = sys.argv[1]
    parsed = urlparse(url)
    parts = [p for p in parsed.path.split("/") if p]
    try:
        design_idx = parts.index("design")
        file_key = parts[design_idx + 1]
    except (ValueError, IndexError):
        print("Could not parse file key from URL", file=sys.stderr)
        return 1

    node_id = parse_qs(parsed.query).get("node-id", [None])[0]
    if not node_id:
        print("URL missing node-id query parameter", file=sys.stderr)
        return 1

    print(f"fileKey={file_key}")
    print(f"nodeIdUrl={node_id}")
    print(f"nodeIdTool={node_id.replace('-', ':')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
