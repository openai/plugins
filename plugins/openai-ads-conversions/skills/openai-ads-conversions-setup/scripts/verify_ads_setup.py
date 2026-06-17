#!/usr/bin/env python3
"""Static sanity checks for OpenAI Ads Pixel and CAPI integrations."""

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
    "test",
    "tests",
    "venv",
    "__tests__",
}

SKIP_FILES = {
    "verify_capi_secret_not_exposed.py",
    "verify_ads_setup.py",
}

TEXT_EXTENSIONS = {
    ".astro",
    ".cjs",
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
    ".svelte",
    ".ts",
    ".tsx",
    ".vue",
    ".yaml",
    ".yml",
}

DOC_EXTENSIONS = {
    ".md",
    ".mdx",
    ".rst",
}


def is_env_file(filename: str) -> bool:
    return filename == ".env" or filename.startswith(".env.")


def is_env_template_file(filename: str) -> bool:
    return is_env_file(filename) and (
        filename in {".env.example", ".env.sample", ".env.template"}
        or filename.endswith((".example", ".sample", ".template"))
    )


PIXEL_MARKER_RE = re.compile(
    r"(?i)(openai[_\-\s]?ads[_\-\s]?pixel|openai[_\-\s]?pixel|measurement[_\-\s]?pixel|OPENAI_ADS_PIXEL_ID)"
)
CAPI_MARKER_RE = re.compile(
    r"(?i)(openai[_\-\s]?ads[_\-\s]?(conversions[_\-\s]?)?(api|capi)|conversions[_\-\s]?api|OPENAI_ADS_CONVERSIONS_API_KEY)"
)
EVENT_ID_RE = re.compile(r"(?i)\b(event[_\-]?id|eventId|dedupe|deduplication|idempotency)\b")
OPPREF_RE = re.compile(r"(?i)\b(__oppref|oppref)\b")
SOURCE_URL_RE = re.compile(r"(?i)\b(source_url|sourceUrl|sourceURL)\b")
OPENAI_ADS_CAPI_CONTEXT_RE = re.compile(
    r"(?i)(bzr\.openai\.com/v1/events|/v1/events\?pid=|OPENAI_ADS_CONVERSIONS_API_KEY|"
    r"OPENAI_ADS_CAPI_KEY|openai[_\-\s]?ads[_\-\s]?(conversions[_\-\s]?)?(api|capi))"
)
CAPI_LEGACY_FIELD_RE = re.compile(
    r"(?i)(?:[\"']|\b)(event_name|event_time_epoch_ms|event_source_url|event_data)(?:[\"']|\b)\s*:"
)
VALIDATE_ONLY_TRUE_RE = re.compile(
    r"(?i)^\s*(?:export\s+)?"
    r"OPENAI_ADS(?:_(?:CAPI|CONVERSIONS|CONVERSIONS_API))?_VALIDATE_ONLY"
    r"\s*[:=]\s*[\"']?(?:true|1|yes)[\"']?\s*(?:#.*)?$"
)
PUBLIC_CAPI_ENV_RE = re.compile(
    r"\b(?:NEXT_PUBLIC|NUXT_PUBLIC|PUBLIC|REACT_APP|VITE)_"
    r"(?:[A-Z0-9]+_)*(?:OPENAI_ADS|OPENAI|ADS|CAPI|CONVERSION|CONVERSIONS)"
    r"(?:_[A-Z0-9]+)*_(?:API_KEY|KEY|SECRET|TOKEN)[A-Z0-9_]*\b",
)
PUBLIC_PIXEL_ENV_RE = re.compile(
    r"\b(?:NEXT_PUBLIC|NUXT_PUBLIC|PUBLIC|REACT_APP|VITE)_OPENAI_ADS_PIXEL_ID\b"
)
SERVER_PIXEL_ENV_RE = re.compile(r"\bOPENAI_ADS_PIXEL_ID\b")
SHARED_PIXEL_GUIDANCE_RE = re.compile(
    r"(?i)(same|shared|reuse|match|identical|alias|same value).{0,80}"
    r"(pixel id|OPENAI_ADS_PIXEL_ID)"
)
ADS_MEASURE_EVENT_RE = re.compile(
    r"(?is)(?:\bwindow\s*\.\s*)?\boaiq\s*(?:\?\.)?\(\s*"
    r"[\"']measure[\"']\s*,\s*[\"']([a-z0-9_-]+)[\"']"
)
SUPPORTED_EVENT_NAMES = {
    "appointment_scheduled",
    "checkout_started",
    "contents_viewed",
    "custom",
    "items_added",
    "lead_created",
    "order_created",
    "page_viewed",
    "registration_completed",
    "subscription_created",
    "trial_started",
}


def iter_candidate_files(root: Path, *, include_docs: bool = False) -> Iterable[Path]:
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
            suffix = path.suffix.lower()
            if (
                is_env_file(filename)
                or suffix in TEXT_EXTENSIONS
                or (include_docs and suffix in DOC_EXTENSIONS)
            ):
                yield path


def read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def first_hits(
    root: Path,
    pattern: re.Pattern[str],
    limit: int = 20,
    *,
    include_docs: bool = False,
) -> list[dict[str, object]]:
    hits: list[dict[str, object]] = []
    for path in iter_candidate_files(root, include_docs=include_docs):
        text = read_file(path)
        for line_number, line in enumerate(text.splitlines(), start=1):
            if pattern.search(line):
                hits.append(
                    {
                        "path": str(path.relative_to(root)),
                        "line": line_number,
                    }
                )
                break
        if len(hits) >= limit:
            break
    return hits


def literal_hits(root: Path, literal: str, limit: int = 20) -> list[dict[str, object]]:
    if not literal:
        return []

    hits: list[dict[str, object]] = []
    for path in iter_candidate_files(root):
        text = read_file(path)
        for line_number, line in enumerate(text.splitlines(), start=1):
            if literal in line:
                hits.append(
                    {
                        "path": str(path.relative_to(root)),
                        "line": line_number,
                    }
                )
                break
        if len(hits) >= limit:
            break
    return hits


def unsupported_event_hits(root: Path, limit: int = 20) -> list[dict[str, object]]:
    hits: list[dict[str, object]] = []
    for path in iter_candidate_files(root):
        text = read_file(path)
        for match in ADS_MEASURE_EVENT_RE.finditer(text):
            event_name = match.group(1)
            if event_name in SUPPORTED_EVENT_NAMES:
                continue

            hits.append(
                {
                    "path": str(path.relative_to(root)),
                    "line": text.count("\n", 0, match.start(1)) + 1,
                    "event_name": event_name,
                }
            )
            if len(hits) >= limit:
                return hits
    return hits


def legacy_capi_field_hits(root: Path, limit: int = 20) -> list[dict[str, object]]:
    hits: list[dict[str, object]] = []
    for path in iter_candidate_files(root):
        text = read_file(path)
        if not OPENAI_ADS_CAPI_CONTEXT_RE.search(text):
            continue

        for match in CAPI_LEGACY_FIELD_RE.finditer(text):
            hits.append(
                {
                    "path": str(path.relative_to(root)),
                    "line": text.count("\n", 0, match.start(1)) + 1,
                    "field_name": match.group(1),
                }
            )
            if len(hits) >= limit:
                return hits
    return hits


def validate_only_default_hits(root: Path, limit: int = 20) -> list[dict[str, object]]:
    hits: list[dict[str, object]] = []
    for path in iter_candidate_files(root):
        if not is_env_template_file(path.name):
            continue

        text = read_file(path)
        for line_number, line in enumerate(text.splitlines(), start=1):
            if not VALIDATE_ONLY_TRUE_RE.search(line):
                continue

            hits.append(
                {
                    "path": str(path.relative_to(root)),
                    "line": line_number,
                }
            )
            if len(hits) >= limit:
                return hits
    return hits


def make_check(
    name: str, passed: bool, hits: list[dict[str, object]], message: str
) -> dict[str, object]:
    return {
        "name": name,
        "passed": passed,
        "message": message,
        "hits": hits,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run static sanity checks for OpenAI Ads Pixel and CAPI instrumentation."
    )
    parser.add_argument("root", nargs="?", default=".", help="Repository root to verify.")
    parser.add_argument("--pixel-id", default="", help="Expected Pixel ID literal, if known.")
    parser.add_argument(
        "--capi-env",
        default="OPENAI_ADS_CONVERSIONS_API_KEY",
        help="Expected server-only env var or secret config name for CAPI.",
    )
    parser.add_argument(
        "--require",
        action="append",
        choices=(
            "pixel",
            "capi",
            "dedupe",
            "shared-pixel-id",
            "supported-events",
            "oppref",
            "source-url",
        ),
        default=[],
        help="Require a specific check to pass. Can be passed more than once.",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()

    pixel_hits = (
        literal_hits(root, args.pixel_id) if args.pixel_id else first_hits(root, PIXEL_MARKER_RE)
    )
    capi_marker_hits = first_hits(root, CAPI_MARKER_RE)
    capi_env_hits = literal_hits(root, args.capi_env) if args.capi_env else []
    event_id_hits = first_hits(root, EVENT_ID_RE)
    public_capi_env_hits = first_hits(root, PUBLIC_CAPI_ENV_RE)
    public_pixel_env_hits = first_hits(root, PUBLIC_PIXEL_ENV_RE)
    server_pixel_env_hits = first_hits(root, SERVER_PIXEL_ENV_RE)
    shared_pixel_guidance_hits = first_hits(root, SHARED_PIXEL_GUIDANCE_RE, include_docs=True)
    oppref_hits = first_hits(root, OPPREF_RE)
    source_url_hits = first_hits(root, SOURCE_URL_RE)
    event_name_unsupported_hits = unsupported_event_hits(root)
    legacy_capi_fields = legacy_capi_field_hits(root)
    validate_only_defaults = validate_only_default_hits(root)
    has_public_and_server_pixel_config = bool(public_pixel_env_hits and server_pixel_env_hits)

    checks = [
        make_check(
            "pixel_marker",
            bool(pixel_hits),
            pixel_hits,
            "Found expected Pixel ID or OpenAI Ads Pixel marker.",
        ),
        make_check(
            "capi_marker",
            bool(capi_marker_hits or capi_env_hits),
            capi_marker_hits + capi_env_hits,
            "Found CAPI marker or expected server-only secret reference.",
        ),
        make_check(
            "dedupe_marker",
            bool(event_id_hits),
            event_id_hits,
            "Found event_id/deduplication/idempotency marker.",
        ),
        make_check(
            "no_public_capi_env",
            not public_capi_env_hits,
            public_capi_env_hits,
            "No browser-visible CAPI/API secret env references found.",
        ),
        make_check(
            "shared_pixel_id_guidance",
            not has_public_and_server_pixel_config or bool(shared_pixel_guidance_hits),
            public_pixel_env_hits + server_pixel_env_hits + shared_pixel_guidance_hits,
            "If browser and server Pixel ID config names both exist, docs/code explain they are the same logical Pixel ID.",
        ),
        make_check(
            "supported_event_names",
            not event_name_unsupported_hits,
            event_name_unsupported_hits,
            "No unsupported OpenAI Ads Pixel event names found in measure calls.",
        ),
        make_check(
            "oppref_marker",
            bool(oppref_hits),
            oppref_hits,
            "Found oppref or __oppref marker for CAPI attribution context.",
        ),
        make_check(
            "source_url_marker",
            bool(source_url_hits),
            source_url_hits,
            "Found source_url/sourceUrl marker for CAPI web source context.",
        ),
        make_check(
            "no_legacy_capi_fields",
            not legacy_capi_fields,
            legacy_capi_fields,
            "No removed legacy CAPI request field names found in OpenAI Ads CAPI files.",
        ),
        make_check(
            "no_validate_only_default",
            not validate_only_defaults,
            validate_only_defaults,
            "Checked-in env templates do not default OpenAI Ads CAPI validate_only mode to true.",
        ),
    ]

    required_to_check = {
        "pixel": "pixel_marker",
        "capi": "capi_marker",
        "dedupe": "dedupe_marker",
        "shared-pixel-id": "shared_pixel_id_guidance",
        "supported-events": "supported_event_names",
        "oppref": "oppref_marker",
        "source-url": "source_url_marker",
    }
    check_by_name = {str(check["name"]): check for check in checks}
    failed_required = [
        required
        for required in args.require
        if not check_by_name[required_to_check[required]]["passed"]
    ]
    failed_security = [
        check["name"]
        for check in checks
        if check["name"] == "no_public_capi_env" and not check["passed"]
    ]
    failed_correctness = [
        check["name"]
        for check in checks
        if check["name"]
        in {
            "supported_event_names",
            "no_legacy_capi_fields",
            "no_validate_only_default",
        }
        and not check["passed"]
    ]

    result = {
        "root": str(root),
        "required": args.require,
        "checks": checks,
        "passed": not failed_required and not failed_security and not failed_correctness,
        "failed_required": failed_required,
        "failed_security": failed_security,
        "failed_correctness": failed_correctness,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 2


if __name__ == "__main__":
    sys.exit(main())
