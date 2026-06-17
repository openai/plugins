#!/usr/bin/env python3
"""Verify OpenAI Ads CAPI credentials are not exposed to browser-visible code."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Iterable

SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".next",
    ".nuxt",
    ".turbo",
    ".venv",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "out",
    "target",
    "venv",
}

SKIP_FILES = {
    "verify_capi_secret_not_exposed.py",
    "verify_ads_setup.py",
}

TEXT_EXTENSIONS = {
    ".astro",
    ".cjs",
    ".css",
    ".erb",
    ".go",
    ".html",
    ".java",
    ".js",
    ".json",
    ".jsx",
    ".mjs",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".scss",
    ".svelte",
    ".ts",
    ".tsx",
    ".vue",
    ".yaml",
    ".yml",
}


def is_env_file(filename: str) -> bool:
    return filename == ".env" or filename.startswith(".env.")


CLIENT_HINTS = {
    "app",
    "assets",
    "browser",
    "client",
    "components",
    "frontend",
    "pages",
    "public",
    "src",
    "static",
    "ui",
    "web",
}

SERVER_ONLY_HINTS = {
    "backend",
    "server",
}

SERVER_ROUTE_PATTERNS = {
    ("app", "api"),
    ("pages", "api"),
    ("src", "app", "api"),
    ("src", "pages", "api"),
}

BROWSER_EXTENSIONS = {
    ".astro",
    ".html",
    ".js",
    ".jsx",
    ".mjs",
    ".svelte",
    ".ts",
    ".tsx",
    ".vue",
}

STATIC_ASSET_EXTENSIONS = {
    ".json",
}

STATIC_ASSET_HINTS = {
    "assets",
    "public",
    "static",
}

PUBLIC_ENV_RE = re.compile(
    r"\b(?:NEXT_PUBLIC|NUXT_PUBLIC|PUBLIC|REACT_APP|VITE)_"
    r"(?:[A-Z0-9]+_)*(?:OPENAI_ADS|OPENAI|ADS|CAPI|CONVERSION|CONVERSIONS)"
    r"(?:_[A-Z0-9]+)*_(?:API_KEY|KEY|SECRET|TOKEN)[A-Z0-9_]*\b",
)

OPENAI_ADS_SECRET_RE = re.compile(
    r"\b("
    r"OPENAI_ADS_CONVERSIONS_API_KEY|"
    r"OPENAI_ADS_CAPI_KEY|"
    r"OPENAI_CAPI_KEY|"
    r"OPENAI_CONVERSIONS_API_KEY|"
    r"CONVERSIONS_API_KEY|"
    r"CAPI_API_KEY|"
    r"CAPI_SECRET"
    r")\b",
    re.IGNORECASE,
)

OPENAI_ADS_SECRET_ASSIGNMENT_RE = re.compile(
    r"['\"]?\b("
    r"OPENAI_ADS_CONVERSIONS_API_KEY|"
    r"OPENAI_ADS_CAPI_KEY|"
    r"OPENAI_CAPI_KEY|"
    r"OPENAI_CONVERSIONS_API_KEY|"
    r"CONVERSIONS_API_KEY|"
    r"CAPI_API_KEY|"
    r"CAPI_SECRET"
    r")\b['\"]?\s*[:=]\s*['\"]?([A-Za-z0-9_\-./+=]{12,})['\"]?",
    re.IGNORECASE,
)
PLACEHOLDER_VALUE_RE = re.compile(
    r"(?i)^(process\.env|os\.environ|env\.|import\.meta\.env|your|replace|placeholder|example|todo)"
)

LITERAL_SECRET_RE = re.compile(
    r"(?i)\b(openai|ads|capi|conversion|conversions)[a-z0-9_\-.\s]{0,50}"
    r"(api[_\-\s]?key|secret|token)\b\s*[:=]\s*['\"][A-Za-z0-9_\-./+=]{16,}['\"]"
)

MASK_VALUE_RE = re.compile(r"(['\"])[A-Za-z0-9_\-./+=]{12,}(['\"])")
UNQUOTED_SECRET_VALUE_RE = re.compile(
    r"(?i)(\b[A-Z0-9_.-]*(?:API[_-]?KEY|CAPI|SECRET|TOKEN)[A-Z0-9_.-]*\b\s*[:=]\s*)"
    r"([^\s#,'\"]{8,})"
)


def iter_candidate_files(root: Path) -> Iterable[Path]:
    for current_root, dirs, files in os.walk(root):
        dirs[:] = [
            directory
            for directory in dirs
            if directory not in SKIP_DIRS and not (Path(current_root) / directory).is_symlink()
        ]

        for filename in files:
            if filename in SKIP_FILES:
                continue
            path = Path(current_root) / filename
            if is_env_file(filename) or path.suffix.lower() in TEXT_EXTENSIONS:
                yield path


def is_client_visible(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    parts = tuple(part.lower() for part in rel.parts)
    lower_parts = set(parts)
    if path.suffix.lower() in {".html", ".css", ".scss"}:
        return True
    if path.suffix.lower() in STATIC_ASSET_EXTENSIONS and bool(lower_parts & STATIC_ASSET_HINTS):
        return True
    if path.suffix.lower() in BROWSER_EXTENSIONS and bool(lower_parts & STATIC_ASSET_HINTS):
        return True
    # "api" alone is often a browser API wrapper, e.g. src/api/client.ts.
    # Only classify well-known framework API route paths as server-only.
    if any(
        parts[index : index + len(pattern)] == pattern
        for pattern in SERVER_ROUTE_PATTERNS
        for index in range(len(parts) - len(pattern) + 1)
    ):
        return False
    if bool(lower_parts & SERVER_ONLY_HINTS):
        return False
    return path.suffix.lower() in BROWSER_EXTENSIONS and bool(lower_parts & CLIENT_HINTS)


def masked_context(line: str) -> str:
    masked = MASK_VALUE_RE.sub(r"\1***\2", line.strip())
    masked = UNQUOTED_SECRET_VALUE_RE.sub(r"\1***", masked)
    return masked[:240]


def has_literal_openai_ads_secret_assignment(line: str) -> bool:
    match = OPENAI_ADS_SECRET_ASSIGNMENT_RE.search(line)
    if not match:
        return False
    return PLACEHOLDER_VALUE_RE.search(match.group(2)) is None


def maybe_add_context(
    finding: dict[str, object], line: str, include_context: bool
) -> dict[str, object]:
    if include_context:
        finding["context"] = masked_context(line)
    return finding


def scan_file(path: Path, root: Path, include_context: bool) -> list[dict[str, object]]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []

    client_visible = is_client_visible(path, root)
    findings: list[dict[str, object]] = []

    for line_number, line in enumerate(text.splitlines(), start=1):
        public_env_match = PUBLIC_ENV_RE.search(line)
        if public_env_match:
            findings.append(
                maybe_add_context(
                    {
                        "severity": "high",
                        "rule": "public_env_secret_name",
                        "path": str(path.relative_to(root)),
                        "line": line_number,
                        "message": "Potential CAPI/API secret uses a browser-visible env var prefix.",
                    },
                    line,
                    include_context,
                )
            )

        secret_name_match = OPENAI_ADS_SECRET_RE.search(line)
        if secret_name_match and client_visible:
            findings.append(
                maybe_add_context(
                    {
                        "severity": "high",
                        "rule": "capi_secret_name_in_client_file",
                        "path": str(path.relative_to(root)),
                        "line": line_number,
                        "message": "Potential OpenAI Ads CAPI secret reference appears in client-visible code.",
                    },
                    line,
                    include_context,
                )
            )

        if has_literal_openai_ads_secret_assignment(line):
            findings.append(
                maybe_add_context(
                    {
                        "severity": "high",
                        "rule": "literal_capi_secret_assignment",
                        "path": str(path.relative_to(root)),
                        "line": line_number,
                        "message": "Potential literal OpenAI Ads CAPI credential assignment found.",
                    },
                    line,
                    include_context,
                )
            )

        literal_match = LITERAL_SECRET_RE.search(line)
        if literal_match:
            findings.append(
                maybe_add_context(
                    {
                        "severity": "high",
                        "rule": "literal_secret_like_assignment",
                        "path": str(path.relative_to(root)),
                        "line": line_number,
                        "message": "Potential literal conversion API credential assignment found.",
                    },
                    line,
                    include_context,
                )
            )

    return findings


def exit_code(findings: list[dict[str, object]], fail_on: str) -> int:
    if fail_on == "none":
        return 0
    severities = {str(finding["severity"]) for finding in findings}
    if fail_on == "high" and "high" in severities:
        return 2
    if fail_on == "medium" and severities & {"high", "medium"}:
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify OpenAI Ads CAPI credentials are not exposed to browser-visible code."
    )
    parser.add_argument("root", nargs="?", default=".", help="Repository root to verify.")
    parser.add_argument(
        "--include-context",
        action="store_true",
        help="Include masked source-line context in findings. By default, only paths, line numbers, rules, and summaries are reported.",
    )
    parser.add_argument(
        "--fail-on",
        choices=("high", "medium", "none"),
        default="high",
        help="Minimum severity that should produce a non-zero exit code.",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    findings: list[dict[str, object]] = []
    for path in iter_candidate_files(root):
        findings.extend(scan_file(path, root, args.include_context))

    result = {
        "root": str(root),
        "output_policy": {
            "runs_locally": True,
            "transmits_repository_contents": False,
            "source_context_included": args.include_context,
        },
        "summary": {
            "total": len(findings),
            "high": sum(1 for finding in findings if finding["severity"] == "high"),
            "medium": sum(1 for finding in findings if finding["severity"] == "medium"),
        },
        "findings": findings,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return exit_code(findings, args.fail_on)


if __name__ == "__main__":
    sys.exit(main())
