#!/usr/bin/env python3
"""Generate and post-process Codex Security scan worklists.

This script stays deliberately model-free:

- `make-repo-rank-input` creates the deterministic repository or scoped-path
  JSONL candidate worklist that ranking subagents consume.
- `make-diff-rank-input` creates the deterministic diff-scoped JSONL candidate
  worklist from Git changed paths. It supports committed revision diffs and
  local working-tree patches.
- `make-rank-shards` partitions the ranking input into deterministic shards.
- `validate-rank-shard` validates one completed worker output before the
  coordinator closes that worker and schedules the next shard.
- `merge-rank-outputs` validates and combines worker-local shard outputs.
- `copy-deep-review-input` copies every candidate into the deep-review worklist
  for exhaustive mode.
- `select-deep-review-input` selects the ranked rows for deep review.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from collections.abc import Callable
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

SHARD_INPUT_GLOB = "rank-shard-*.input.jsonl"
SHARD_OUTPUT_GLOB = "rank-shard-*.output.jsonl"

JsonRow = dict[str, object]
RowValidator = Callable[[JsonRow, Path, int], None]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Codex Security scan worklist helper.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    make = subparsers.add_parser(
        "make-repo-rank-input",
        help="Create rank_input.jsonl for subagent-based file ranking.",
    )
    make.add_argument("--repo", required=True, help="Repository root.")
    make.add_argument(
        "--scope",
        default=".",
        help="Path within the repository to scan. Defaults to the repository root.",
    )
    make.add_argument("--out", required=True, help="Output rank_input.jsonl path.")
    make.add_argument("--area", default="", help="Area label. Defaults to scope.")
    make.add_argument(
        "--preview-bytes",
        type=int,
        default=200,
        help="Number of bytes to include in the preview field.",
    )

    diff = subparsers.add_parser(
        "make-diff-rank-input",
        help="Create rank_input.jsonl from Git changed source-like files.",
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
    diff.add_argument("--out", required=True, help="Output rank_input.jsonl path.")
    diff.add_argument("--area", default="diff", help="Area label for ranking rows.")
    diff.add_argument(
        "--preview-bytes",
        type=int,
        default=200,
        help="Number of bytes to include in the preview field.",
    )

    shards = subparsers.add_parser(
        "make-rank-shards",
        help="Partition rank_input.jsonl into deterministic worker input shards.",
    )
    shards.add_argument("--rank-input", required=True, help="Deterministic rank input JSONL.")
    shards.add_argument("--out-dir", required=True, help="Directory for worker input shards.")
    shards.add_argument(
        "--max-rows",
        type=int,
        default=5,
        help="Maximum rows per shard. Defaults to 5.",
    )

    validate_shard = subparsers.add_parser(
        "validate-rank-shard",
        help="Validate one worker output against its rank input shard.",
    )
    validate_shard.add_argument("--input", required=True, help="Worker rank input shard.")
    validate_shard.add_argument("--output", required=True, help="Worker rank output shard.")

    merge = subparsers.add_parser(
        "merge-rank-outputs",
        help="Validate worker shard outputs and create rank_output.jsonl.",
    )
    merge.add_argument("--rank-input", required=True, help="Authoritative rank input JSONL.")
    merge.add_argument("--shard-dir", required=True, help="Directory of input and output shards.")
    merge.add_argument("--out", required=True, help="Output rank_output.jsonl path.")

    copy = subparsers.add_parser(
        "copy-deep-review-input",
        help="Create deep_review_input.jsonl directly from rank_input.jsonl.",
    )
    copy.add_argument("--rank-input", required=True, help="Deterministic rank input JSONL.")
    copy.add_argument("--out", required=True, help="Output deep_review_input.jsonl path.")

    select = subparsers.add_parser(
        "select-deep-review-input",
        help="Create deep_review_input.jsonl from worker-produced rank_output.jsonl.",
    )
    select.add_argument("--rank-output", required=True, help="Worker ranking output JSONL.")
    select.add_argument("--out", required=True, help="Output deep_review_input.jsonl path.")
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
    return path.name.endswith((".min.js", ".map"))


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


def write_jsonl(output: Path, rows: list[JsonRow]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
            handle.write("\n")


def load_jsonl(path: Path, label: str, validator: RowValidator) -> list[JsonRow]:
    if not path.exists():
        raise SystemExit(f"{label} missing: {path}")

    rows: list[JsonRow] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            if not raw_line.strip():
                raise SystemExit(f"{path}:{line_number}: blank JSONL rows are not allowed")
            try:
                parsed: object = json.loads(raw_line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{line_number}: invalid JSON: {exc.msg}") from exc
            if not isinstance(parsed, dict):
                raise SystemExit(f"{path}:{line_number}: expected a JSON object")
            row = {str(key): value for key, value in parsed.items()}
            validator(row, path, line_number)
            rows.append(row)
    return rows


def require_exact_fields(row: JsonRow, expected: set[str], path: Path, line_number: int) -> None:
    actual = set(row)
    if actual != expected:
        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)
        details: list[str] = []
        if missing:
            details.append(f"missing fields {missing}")
        if unexpected:
            details.append(f"unexpected fields {unexpected}")
        raise SystemExit(f"{path}:{line_number}: {'; '.join(details)}")


def require_string(
    row: JsonRow, field: str, path: Path, line_number: int, *, allow_empty: bool
) -> None:
    value = row[field]
    if not isinstance(value, str) or (not allow_empty and not value.strip()):
        requirement = "a string" if allow_empty else "a non-empty string"
        raise SystemExit(f"{path}:{line_number}: {field} must be {requirement}")


def validate_rank_input_row(row: JsonRow, path: Path, line_number: int) -> None:
    require_exact_fields(row, {"path", "area", "preview"}, path, line_number)
    require_string(row, "path", path, line_number, allow_empty=False)
    require_string(row, "area", path, line_number, allow_empty=True)
    require_string(row, "preview", path, line_number, allow_empty=True)


def validate_rank_output_row(row: JsonRow, path: Path, line_number: int) -> None:
    require_exact_fields(row, {"path", "area", "score", "include", "reason"}, path, line_number)
    require_string(row, "path", path, line_number, allow_empty=False)
    require_string(row, "area", path, line_number, allow_empty=True)
    score = row["score"]
    if isinstance(score, bool) or not isinstance(score, int):
        raise SystemExit(f"{path}:{line_number}: score must be an integer from 1 through 10")
    if not 1 <= score <= 10:
        raise SystemExit(f"{path}:{line_number}: score must be from 1 through 10")
    if not isinstance(row["include"], bool):
        raise SystemExit(f"{path}:{line_number}: include must be a boolean")
    require_string(row, "reason", path, line_number, allow_empty=False)


def require_unique_paths(rows: list[JsonRow], label: str) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for row in rows:
        path = str(row["path"])
        if path in seen:
            duplicates.add(path)
        seen.add(path)
    if duplicates:
        raise SystemExit(f"{label} contains duplicate paths: {sorted(duplicates)}")


def make_repo_rank_input(args: argparse.Namespace) -> None:
    repo = Path(args.repo).expanduser().resolve()
    if not repo.is_dir():
        raise SystemExit(f"Repo path not found: {repo}")
    scope_abs = resolve_scope(repo, args.scope)
    scope_rel = scope_abs.relative_to(repo).as_posix()
    area = args.area or scope_rel

    rows: list[JsonRow] = []
    for path in scope_abs.rglob("*"):
        try:
            if not path.is_file():
                continue
        except OSError:
            continue
        rel = path.relative_to(repo)
        if path_is_excluded(rel) or path.suffix.lower() not in TEXT_CODE_EXTENSIONS:
            continue

        preview, is_binary = preview_for(path, args.preview_bytes)
        if is_binary:
            continue
        rows.append({"path": rel.as_posix(), "area": area, "preview": preview})

    rows.sort(key=lambda row: str(row["path"]))
    output = Path(args.out).expanduser()
    write_jsonl(output, rows)
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
        if path.exists() and path.is_file():
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

    rows: list[JsonRow] = []
    for path in git_changed_paths(repo, args.base, args.head, args.mode):
        rel = path.relative_to(repo)
        if path_is_excluded(rel) or path.suffix.lower() not in TEXT_CODE_EXTENSIONS:
            continue

        preview, is_binary = preview_for(path, args.preview_bytes)
        if is_binary:
            continue
        rows.append({"path": rel.as_posix(), "area": args.area, "preview": preview})

    rows.sort(key=lambda row: str(row["path"]))
    output = Path(args.out).expanduser()
    write_jsonl(output, rows)
    print(f"Wrote {len(rows)} rows to {output}")


def make_rank_shards(args: argparse.Namespace) -> None:
    if args.max_rows < 1:
        raise SystemExit("--max-rows must be at least 1")

    rank_input = Path(args.rank_input).expanduser()
    rows = load_jsonl(rank_input, "Rank input", validate_rank_input_row)
    require_unique_paths(rows, "Rank input")

    output_dir = Path(args.out_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    existing = sorted((*output_dir.glob(SHARD_INPUT_GLOB), *output_dir.glob(SHARD_OUTPUT_GLOB)))
    if existing:
        raise SystemExit(f"Rank shard directory already contains shard files: {output_dir}")

    shard_count = 0
    for start in range(0, len(rows), args.max_rows):
        shard_count += 1
        shard_path = output_dir / f"rank-shard-{shard_count:04d}.input.jsonl"
        write_jsonl(shard_path, rows[start : start + args.max_rows])

    print(f"Wrote {shard_count} rank shards to {output_dir}")


def validate_rank_shard(
    input_shard: Path, output_shard: Path
) -> tuple[list[JsonRow], list[JsonRow]]:
    shard_inputs = load_jsonl(input_shard, "Rank input shard", validate_rank_input_row)
    require_unique_paths(shard_inputs, f"Rank input shard {input_shard.name}")
    shard_outputs = load_jsonl(output_shard, "Rank output shard", validate_rank_output_row)
    require_unique_paths(shard_outputs, f"Rank output shard {output_shard.name}")

    expected_paths = {str(row["path"]) for row in shard_inputs}
    actual_paths = {str(row["path"]) for row in shard_outputs}
    if expected_paths != actual_paths:
        missing = sorted(expected_paths - actual_paths)
        unknown = sorted(actual_paths - expected_paths)
        raise SystemExit(
            f"{output_shard}: paths do not match its input shard; "
            f"missing={missing}; unknown={unknown}"
        )

    area_by_path = {str(row["path"]): row["area"] for row in shard_inputs}
    for row in shard_outputs:
        row_path = str(row["path"])
        if row["area"] != area_by_path[row_path]:
            raise SystemExit(f"{output_shard}: area does not match rank input for {row_path}")
    return shard_inputs, shard_outputs


def validate_rank_shard_command(args: argparse.Namespace) -> None:
    input_shard = Path(args.input).expanduser()
    output_shard = Path(args.output).expanduser()
    _, output_rows = validate_rank_shard(input_shard, output_shard)
    print(f"Validated {len(output_rows)} ranking rows in {output_shard}")


def merge_rank_outputs(args: argparse.Namespace) -> None:
    rank_input = Path(args.rank_input).expanduser()
    authoritative_rows = load_jsonl(rank_input, "Rank input", validate_rank_input_row)
    require_unique_paths(authoritative_rows, "Rank input")

    shard_dir = Path(args.shard_dir).expanduser()
    if not shard_dir.is_dir():
        raise SystemExit(f"Rank shard directory missing: {shard_dir}")
    input_shards = sorted(shard_dir.glob(SHARD_INPUT_GLOB))
    output_shards = sorted(shard_dir.glob(SHARD_OUTPUT_GLOB))
    expected_output_names = {
        path.name.replace(".input.jsonl", ".output.jsonl") for path in input_shards
    }
    actual_output_names = {path.name for path in output_shards}
    if expected_output_names != actual_output_names:
        missing = sorted(expected_output_names - actual_output_names)
        unexpected = sorted(actual_output_names - expected_output_names)
        details: list[str] = []
        if missing:
            details.append(f"missing output shards {missing}")
        if unexpected:
            details.append(f"unexpected output shards {unexpected}")
        raise SystemExit(f"Rank shard outputs are incomplete: {'; '.join(details)}")

    sharded_inputs: list[JsonRow] = []
    output_by_path: dict[str, JsonRow] = {}
    for input_shard in input_shards:
        output_shard = input_shard.with_name(
            input_shard.name.replace(".input.jsonl", ".output.jsonl")
        )
        shard_inputs, shard_outputs = validate_rank_shard(input_shard, output_shard)
        sharded_inputs.extend(shard_inputs)
        for row in shard_outputs:
            row_path = str(row["path"])
            if row_path in output_by_path:
                raise SystemExit(f"Rank outputs contain duplicate path: {row_path}")
            output_by_path[row_path] = row

    if sharded_inputs != authoritative_rows:
        raise SystemExit("Rank input shards do not exactly partition the authoritative rank input")

    merged = [output_by_path[str(row["path"])] for row in authoritative_rows]
    output = Path(args.out).expanduser()
    write_jsonl(output, merged)
    print(f"Merged {len(merged)} ranking rows into {output}")


def copy_deep_review_input(args: argparse.Namespace) -> None:
    rank_input = Path(args.rank_input).expanduser()
    rows = load_jsonl(rank_input, "Rank input", validate_rank_input_row)
    require_unique_paths(rows, "Rank input")
    selected = [{"path": row["path"], "area": row["area"]} for row in rows]

    output = Path(args.out).expanduser()
    write_jsonl(output, selected)
    print(f"Copied {len(selected)} rows into {output}")


def select_deep_review_input(args: argparse.Namespace) -> None:
    rank_output = Path(args.rank_output).expanduser()
    rows = load_jsonl(rank_output, "Rank output", validate_rank_output_row)
    require_unique_paths(rows, "Rank output")

    included = [row for row in rows if row["include"]]
    base_rows = included if included else rows
    base_rows.sort(key=lambda row: (-int(row["score"]), str(row["path"])))
    keep = max(1, int(len(base_rows) * (args.top_percent / 100.0))) if base_rows else 0
    selected = [{"path": row["path"], "area": row["area"]} for row in base_rows[:keep]]

    output = Path(args.out).expanduser()
    write_jsonl(output, selected)
    print(f"Selected {len(selected)} of {len(base_rows)} rows into {output}")


def main() -> None:
    args = parse_args()
    if args.command == "make-repo-rank-input":
        make_repo_rank_input(args)
    elif args.command == "make-diff-rank-input":
        make_diff_rank_input(args)
    elif args.command == "make-rank-shards":
        make_rank_shards(args)
    elif args.command == "validate-rank-shard":
        validate_rank_shard_command(args)
    elif args.command == "merge-rank-outputs":
        merge_rank_outputs(args)
    elif args.command == "copy-deep-review-input":
        copy_deep_review_input(args)
    elif args.command == "select-deep-review-input":
        select_deep_review_input(args)
    else:
        raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
