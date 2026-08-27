#!/usr/bin/env python3
"""Create a starter Source_Index CSV from a folder of source files."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path

HEADER = [
    "source_id",
    "source_name",
    "source_type",
    "owner_or_provider",
    "period_covered",
    "as_of_date",
    "retrieved_at",
    "file_tab_page_url_or_location",
    "source_rank",
    "freshness_status",
    "notes",
]

EXT_TYPES = {
    ".pdf": "uploaded_file",
    ".xlsx": "uploaded_file",
    ".xls": "uploaded_file",
    ".csv": "uploaded_file",
    ".json": "uploaded_file",
    ".docx": "uploaded_file",
    ".pptx": "uploaded_file",
    ".txt": "uploaded_file",
    ".md": "uploaded_file",
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a starter Source_Index CSV from a source folder"
    )
    parser.add_argument("source_folder", type=Path)
    parser.add_argument("output_csv", type=Path)
    args = parser.parse_args()
    if not args.source_folder.exists() or not args.source_folder.is_dir():
        raise SystemExit(f"source folder not found: {args.source_folder}")
    files = sorted(
        [p for p in args.source_folder.rglob("*") if p.is_file() and not p.name.startswith(".")]
    )
    retrieved_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=HEADER)
        writer.writeheader()
        for idx, path in enumerate(files, start=1):
            writer.writerow(
                {
                    "source_id": f"SRC-{idx:03d}",
                    "source_name": path.name,
                    "source_type": EXT_TYPES.get(path.suffix.lower(), "uploaded_file"),
                    "owner_or_provider": "user_provided",
                    "period_covered": "",
                    "as_of_date": "",
                    "retrieved_at": retrieved_at,
                    "file_tab_page_url_or_location": str(path),
                    "source_rank": "1",
                    "freshness_status": "unknown",
                    "notes": "starter index; review period/as-of/reliability after inspection",
                }
            )
    print(f"wrote {len(files)} sources to {args.output_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
