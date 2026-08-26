#!/usr/bin/env python3
"""Back up and clear local Public Equity Investing user-context foundation files."""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from state_paths import PLUGIN_LABEL, STATE_DIR_HELP, STATE_FILENAMES, resolve_state_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=f"Move active {PLUGIN_LABEL} local state files into a sibling backup directory."
    )
    parser.add_argument(
        "--codex-home",
        type=Path,
        default=None,
        help="Codex home directory. Defaults to $CODEX_HOME or ~/.codex.",
    )
    parser.add_argument("--state-dir", type=Path, default=None, help=STATE_DIR_HELP)
    parser.add_argument(
        "--backup-dir",
        type=Path,
        default=None,
        help="Backup directory to create. Defaults to a timestamped sibling directory.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would move without changing files.",
    )
    return parser.parse_args()


def resolve_paths(args: argparse.Namespace) -> tuple[Path, Path]:
    state_dir = resolve_state_dir(args.codex_home, args.state_dir)
    if args.backup_dir:
        backup_dir = args.backup_dir.expanduser()
    else:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_dir = state_dir.parent / f"{state_dir.name}-backup-{timestamp}"
    return state_dir, backup_dir


def main() -> int:
    args = parse_args()
    state_dir, backup_dir = resolve_paths(args)
    existing_state_files = [
        state_dir / filename for filename in STATE_FILENAMES if (state_dir / filename).exists()
    ]

    if not existing_state_files:
        print(f"No active {PLUGIN_LABEL} state files found in: {state_dir}")
        return 0
    if backup_dir.exists():
        print(f"Backup directory already exists: {backup_dir}", file=sys.stderr)
        return 1

    if args.dry_run:
        print(f"{PLUGIN_LABEL} state directory: {state_dir}")
        print(f"Backup directory: {backup_dir}")
        for path in existing_state_files:
            print(f"would move: {path.name}")
        print("Dry run only; no files were moved.")
        return 0

    backup_dir.mkdir(parents=True)
    for path in existing_state_files:
        shutil.move(str(path), str(backup_dir / path.name))

    try:
        state_dir.rmdir()
        directory_status = "removed because it was empty"
    except OSError:
        directory_status = "kept because it still contains other files"

    print(f"{PLUGIN_LABEL} state directory: {state_dir}")
    print(f"Backup directory: {backup_dir}")
    for path in existing_state_files:
        print(f"moved: {path.name}")
    print(f"state directory: {directory_status}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
