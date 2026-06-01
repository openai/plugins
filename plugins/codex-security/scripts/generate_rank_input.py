#!/usr/bin/env python3
"""Generate and post-process Codex Security scan worklists.

This script stays deliberately model-free:

- `make-repo-rank-input` creates the deterministic repository-wide candidate CSV
  that ranking subagents consume.
- `make-diff-rank-input` creates the deterministic diff-scoped candidate CSV
  from Git changed paths that ranking subagents consume. It supports committed
  revision diffs and local working-tree patches.
- `copy-deep-review-input` copies every candidate row into the deep-review input for
  exhaustive mode.
- `select-deep-review-input` parses worker-produced ranking output and selects
  the rows for deep review.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from pathlib import Path

EXCLUDED_DIRS = {
    ".cache",
    ".circleci",
    ".devcontainer",
    ".git",
    ".github",
    ".idea",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    ".vscode",
    "__pycache__",
    "bench",
    "benchmark",
    "bintest",
    "build",
    "build_config",
    "build_configs",
    "build-tools",
    "build_tools",
    "ci",
    "coverage",
    "deps",
    "dev",
    "dist",
    "doc",
    "docs",
    "example",
    "examples",
    "external",
    "extern",
    "fixture",
    "fixtures",
    "generated",
    "node_modules",
    "sample",
    "samples",
    "target",
    "test",
    "tests",
    "testing",
    "third-party",
    "third_party",
    "tmp",
    "vendor",
}

EXCLUDED_FILENAMES = {
    ".DS_Store",
    "CHANGELOG",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "Dockerfile",
    "Gemfile",
    "Gemfile.lock",
    "LICENSE",
    "LICENSE.md",
    "Makefile",
    "NEWS",
    "NEWS.md",
    "NOTICE",
    "README",
    "README.md",
    "README.rst",
    "Rakefile",
    "SECURITY.md",
    "TODO",
    "TODO.md",
    "docker-compose.yml",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
}

TEXT_CODE_EXTENSIONS = {
    ".c",
    ".cc",
    ".cfg",
    ".clj",
    ".cpp",
    ".cs",
    ".css",
    ".cue",
    ".cxx",
    ".dart",
    ".ex",
    ".exs",
    ".go",
    ".graphql",
    ".h",
    ".hpp",
    ".hs",
    ".html",
    ".java",
    ".js",
    ".json",
    ".jsx",
    ".kt",
    ".kts",
    ".lua",
    ".mjs",
    ".mm",
    ".php",
    ".proto",
    ".py",
    ".rb",
    ".rs",
    ".scala",
    ".sh",
    ".sql",
    ".swift",
    ".toml",
    ".ts",
    ".tsx",
    ".vue",
    ".xml",
    ".yaml",
    ".yml",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Codex Security scan worklist helper.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    make = subparsers.add_parser(
        "make-repo-rank-input",
        help="Create rank_input.csv for subagent-based file ranking.",
    )
    make.add_argument("--repo", required=True, help="Repository root.")
    make.add_argument("--scope", default=".", help="Subdirectory to scan.")
    make.add_argument("--out", required=True, help="Output rank_input.csv path.")
    make.add_argument("--area", default="", help="Area label. Defaults to scope.")
    make.add_argument(
        "--preview-bytes",
        type=int,
        default=200,
        help="Number of bytes to include in preview column.",
    )

    diff = subparsers.add_parser(
        "make-diff-rank-input",
        help="Create rank_input.csv from Git changed source-like files.",
    )
    diff.add_argument("--repo", required=True, help="Repository root.")
    diff.add_argument("--base", required=True, help="Git diff base revision.")
    diff.add_argument(
        "--mode",
        choices=("revisions", "local-patch"),
        default="revisions",
        help="Git diff mode: committed revisions or staged plus unstaged local patch.",
    )
    diff.add_argument("--head", default="HEAD", help="Git diff head revision.")
    diff.add_argument("--out", required=True, help="Output rank_input.csv path.")
    diff.add_argument("--area", default="diff", help="Area label for assess rows.")
    diff.add_argument(
        "--preview-bytes",
        type=int,
        default=200,
        help="Number of bytes to include in preview column.",
    )

    select = subparsers.add_parser(
        "copy-deep-review-input",
        help="Create deep_review_input.csv directly from rank_input.csv for exhaustive mode.",
    )
    select.add_argument("--rank-input", required=True, help="Deterministic rank input CSV.")
    select.add_argument("--out", required=True, help="Output deep_review_input.csv path.")

    select = subparsers.add_parser(
        "select-deep-review-input",
        help="Create deep_review_input.csv from worker-produced rank_output.csv.",
    )
    select.add_argument("--rank-output", required=True, help="Worker ranking CSV.")
    select.add_argument("--out", required=True, help="Output deep_review_input.csv path.")
    select.add_argument(
        "--top-percent",
        type=int,
        default=20,
        help="Percent of included files to keep for deep review.",
    )
    return parser.parse_args()


def is_binary_sample(data: bytes) -> bool:
    return b"\0" in data


def preview_for(path: Path, preview_bytes: int) -> tuple[str, bool]:
    try:
        data = path.read_bytes()
    except OSError:
        return "", True
    sample = data[:4096]
    if is_binary_sample(sample):
        return "", True
    preview = (
        data[:preview_bytes].decode("utf-8", errors="ignore").replace("\n", " ").replace("\r", " ")
    )
    return preview, False


def path_is_excluded(path: Path) -> bool:
    if any(part in EXCLUDED_DIRS for part in path.parts):
        return True
    if path.name in EXCLUDED_FILENAMES:
        return True
    if path.name.endswith((".min.js", ".map")):
        return True
    return False


def resolve_scope(repo: Path, scope: str) -> Path:
    scope_path = Path(scope).expanduser()
    if not scope_path.is_absolute():
        scope_path = repo / scope_path
    scope_path = scope_path.resolve()
    repo_resolved = repo.resolve()
    try:
        scope_path.relative_to(repo_resolved)
    except ValueError as exc:
        raise SystemExit(f"Scope must be inside repo: {scope_path}") from exc
    if not scope_path.is_dir():
        raise SystemExit(f"Scope path not found: {scope_path}")
    return scope_path


def write_rows(output: Path, rows: list[tuple[str, str, str]], headers: list[str]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)


def make_repo_rank_input(args: argparse.Namespace) -> None:
    repo = Path(args.repo).expanduser().resolve()
    if not repo.is_dir():
        raise SystemExit(f"Repo path not found: {repo}")
    scope_abs = resolve_scope(repo, args.scope)
    scope_rel = scope_abs.relative_to(repo).as_posix()
    area = args.area or scope_rel

    rows: list[tuple[str, str, str]] = []
    for path in scope_abs.rglob("*"):
        try:
            if not path.is_file():
                continue
        except OSError:
            continue
        rel = path.relative_to(repo)
        if path_is_excluded(rel):
            continue
        if path.suffix.lower() not in TEXT_CODE_EXTENSIONS:
            continue

        preview, is_binary = preview_for(path, args.preview_bytes)
        if is_binary:
            continue
        rows.append((rel.as_posix(), area, preview))

    rows.sort(key=lambda row: row[0])
    output = Path(args.out).expanduser()
    write_rows(output, rows, ["path", "area", "preview"])

    print(f"Wrote {len(rows)} rows to {output}")


def run_git_changed_paths(repo: Path, diff_args: list[str]) -> list[Path]:
    result = subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "diff",
            "--name-only",
            "--diff-filter=ACMR",
            *diff_args,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    paths: list[Path] = []
    for line in result.stdout.splitlines():
        if not line:
            continue
        path = repo / line
        if not path.exists() or not path.is_file():
            continue
        paths.append(path)
    return paths


def git_changed_paths(repo: Path, base: str, head: str, mode: str) -> list[Path]:
    if mode == "revisions":
        return run_git_changed_paths(repo, [f"{base}..{head}"])
    if mode == "local-patch":
        unstaged = run_git_changed_paths(repo, [base])
        staged = run_git_changed_paths(repo, ["--cached", base])
        return sorted(set(unstaged + staged))
    raise SystemExit(f"Unknown diff mode: {mode}")


def make_diff_rank_input(args: argparse.Namespace) -> None:
    repo = Path(args.repo).expanduser().resolve()
    if not repo.is_dir():
        raise SystemExit(f"Repo path not found: {repo}")

    rows: list[tuple[str, str, str]] = []
    for path in git_changed_paths(repo, args.base, args.head, args.mode):
        rel = path.relative_to(repo)
        if path_is_excluded(rel):
            continue
        if path.suffix.lower() not in TEXT_CODE_EXTENSIONS:
            continue

        preview, is_binary = preview_for(path, args.preview_bytes)
        if is_binary:
            continue
        rows.append((rel.as_posix(), args.area, preview))

    rows.sort(key=lambda row: row[0])
    output = Path(args.out).expanduser()
    write_rows(output, rows, ["path", "area", "preview"])
    print(f"Wrote {len(rows)} rows to {output}")


def parse_bool(value: object) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes", "y"}:
        return True
    if normalized in {"false", "0", "no", "n"}:
        return False
    return None


def select_deep_review_input(args: argparse.Namespace) -> None:
    rank_output = Path(args.rank_output).expanduser()
    if not rank_output.exists():
        raise SystemExit(f"Rank output missing: {rank_output}")

    rows: list[dict[str, object]] = []
    with rank_output.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            payload: dict[str, object] = {}
            raw_payload = row.get("result_json") or ""
            if raw_payload:
                try:
                    parsed = json.loads(raw_payload)
                    if isinstance(parsed, dict):
                        payload = parsed
                except json.JSONDecodeError:
                    payload = {}

            score_raw: object = row.get("score") or payload.get("score") or 0
            try:
                row["score"] = int(score_raw)
            except (TypeError, ValueError):
                row["score"] = 0

            include = parse_bool(row.get("include"))
            if include is None:
                include = parse_bool(payload.get("include"))
            row["include"] = True if include is None else include
            rows.append(row)

    included = [row for row in rows if row.get("include")]
    base_rows = included if included else rows
    base_rows.sort(key=lambda row: int(row["score"]), reverse=True)
    keep = max(1, int(len(base_rows) * (args.top_percent / 100.0))) if base_rows else 0
    selected = base_rows[:keep]

    output = Path(args.out).expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["path", "area"])
        for row in selected:
            writer.writerow([row.get("path", ""), row.get("area", "")])

    print(f"Selected {len(selected)} of {len(base_rows)} rows into {output}")


def copy_deep_review_input(args: argparse.Namespace) -> None:
    rank_input = Path(args.rank_input).expanduser()
    if not rank_input.exists():
        raise SystemExit(f"Rank input missing: {rank_input}")

    count = 0
    output = Path(args.out).expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)
    with rank_input.open(newline="") as f, output.open("w", newline="") as out:
        reader = csv.DictReader(f)
        writer = csv.writer(out)
        writer.writerow(["path", "area"])
        for row in reader:
            writer.writerow([row.get("path", ""), row.get("area", "")])
            count += 1

    print(f"Copied {count} rows into {output}")


def main() -> None:
    args = parse_args()
    if args.command == "make-repo-rank-input":
        make_repo_rank_input(args)
    elif args.command == "make-diff-rank-input":
        make_diff_rank_input(args)
    elif args.command == "copy-deep-review-input":
        copy_deep_review_input(args)
    elif args.command == "select-deep-review-input":
        select_deep_review_input(args)
    else:
        raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
