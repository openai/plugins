#!/usr/bin/env python3
"""Validate that the macOS pasteboard holds Figma HTML for an expected node."""

from __future__ import annotations

import argparse
import json
import platform
import re
import subprocess
import sys
import time


def pbpaste(preference: str) -> bytes:
    result = subprocess.run(
        ["pbpaste", "-Prefer", preference],
        check=False,
        capture_output=True,
    )
    return result.stdout if result.returncode == 0 else b""


def pasteboard_types(expected_file: str, expected_node: str) -> list[dict[str, object]]:
    """Inspect every macOS pasteboard type through AppKit without mutating it."""
    swift_file = json.dumps(expected_file)
    swift_node = json.dumps(expected_node.replace("-", ":"))
    code = f"""
import AppKit
import Foundation
let expectedFile = {swift_file}
let expectedNode = {swift_node}
let pasteboard = NSPasteboard.general
let rows: [[String: Any]] = (pasteboard.types ?? []).map {{ type in
    let data = pasteboard.data(forType: type) ?? Data()
    let text = String(data: data, encoding: .utf8) ?? ""
    let normalized = text.replacingOccurrences(of: "-", with: ":")
    let hasFigmeta = text.range(of: "figmeta", options: .caseInsensitive) != nil
    let fileMatches = expectedFile.isEmpty || text.contains(expectedFile)
    let nodeMatches = expectedNode.isEmpty || normalized.contains(expectedNode)
    return [
        "type": type.rawValue,
        "bytes": data.count,
        "has_figmeta": hasFigmeta,
        "file_key_matches": fileMatches,
        "node_id_matches": nodeMatches,
        "matches": hasFigmeta && fileMatches && nodeMatches
    ]
}}
let output = try! JSONSerialization.data(withJSONObject: rows)
print(String(data: output, encoding: .utf8)!)
"""
    result = subprocess.run(
        ["/usr/bin/swift", "-e", code],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    try:
        value = json.loads(result.stdout)
        return value if isinstance(value, list) else []
    except json.JSONDecodeError:
        return []


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expect-file-key")
    parser.add_argument("--expect-node-id")
    parser.add_argument("--require-match", action="store_true")
    parser.add_argument("--wait-seconds", type=float, default=0)
    parser.add_argument("--poll-interval", type=float, default=0.25)
    args = parser.parse_args()

    if platform.system() != "Darwin":
        result = {
            "supported": False,
            "platform": platform.system(),
            "reason": "This helper currently supports the macOS pasteboard only.",
        }
        print(json.dumps(result, indent=2))
        raise SystemExit(2 if args.require_match else 0)

    deadline = time.monotonic() + max(args.wait_seconds, 0)
    attempts = 0
    while True:
        attempts += 1
        html_bytes = pbpaste("html")
        text_bytes = pbpaste("txt")
        html = html_bytes.decode("utf-8", errors="replace")
        normalized_html = html.replace("-", ":")
        html_has_figmeta = re.search(r"figmeta", html, flags=re.IGNORECASE) is not None
        html_file_matches = not args.expect_file_key or args.expect_file_key in html
        expected_node = (args.expect_node_id or "").replace("-", ":")
        html_node_matches = not expected_node or expected_node in normalized_html
        types = pasteboard_types(args.expect_file_key or "", expected_node)
        aggregate_has_figmeta = any(bool(item.get("has_figmeta")) for item in types)
        aggregate_file_matches = any(
            bool(item.get("file_key_matches")) for item in types
        )
        aggregate_node_matches = any(
            bool(item.get("node_id_matches")) for item in types
        )
        custom_match = bool(
            aggregate_has_figmeta
            and aggregate_file_matches
            and aggregate_node_matches
        )
        html_match = bool(
            html_bytes
            and html_has_figmeta
            and html_file_matches
            and html_node_matches
        )
        matches = bool(html_match or custom_match)
        match_basis = "html" if html_match else "aggregate" if custom_match else "none"
        if matches or time.monotonic() >= deadline:
            break
        time.sleep(max(args.poll_interval, 0.05))

    result = {
        "supported": True,
        "html_bytes": len(html_bytes),
        "plain_text_bytes": len(text_bytes),
        "has_figmeta": bool(html_has_figmeta or aggregate_has_figmeta),
        "file_key_matches": bool(html_file_matches or aggregate_file_matches),
        "node_id_matches": bool(html_node_matches or aggregate_node_matches),
        "matches": matches,
        "attempts": attempts,
        "pasteboard_types": types,
        "aggregate_has_figmeta": aggregate_has_figmeta,
        "aggregate_file_key_matches": aggregate_file_matches,
        "aggregate_node_id_matches": aggregate_node_matches,
        "match_basis": match_basis,
        "direct_html": {
            "has_figmeta": html_has_figmeta,
            "file_key_matches": html_file_matches,
            "node_id_matches": html_node_matches,
        },
    }
    print(json.dumps(result, indent=2))
    if args.require_match and not matches:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
