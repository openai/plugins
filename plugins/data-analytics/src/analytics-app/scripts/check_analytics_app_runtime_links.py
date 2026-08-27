#!/usr/bin/env python3
"""Fail when analytics app runtime paths drift from their expected layout."""

from __future__ import annotations

from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[3]
ANALYTICS_APP_SRC = PLUGIN_ROOT / "src" / "analytics-app"

EXPECTED_LOCAL_PATHS = {
    ANALYTICS_APP_SRC / "charting": [
        "ChartFrame.tsx",
        "ChartLegend.tsx",
        "ChartRenderer.tsx",
        "ChartTooltip.tsx",
        "chart-capabilities.ts",
        "chart-compatibility.ts",
        "chart-contract.ts",
        "chart-theme.ts",
        "chart-tokens.css",
        "chart-transforms.ts",
    ],
    ANALYTICS_APP_SRC / "tables": [
        "DataTable.d.ts",
        "DataTable.jsx",
        "data-table.css",
    ],
    ANALYTICS_APP_SRC / "layout": [
        "AnalyticsLayoutCanvas.tsx",
        "RichMarkdown.tsx",
        "analyticsLayoutCore.ts",
    ],
    ANALYTICS_APP_SRC / "fonts": [
        "SystemSansVariableVF.woff2",
    ],
}

EXPECTED_LOCAL_FILES = [
    ANALYTICS_APP_SRC / "analytics-layout.test.mjs",
    ANALYTICS_APP_SRC / "main.tsx",
    ANALYTICS_APP_SRC / "tokens.css",
]


def layout_problems() -> list[str]:
    problems: list[str] = []
    for path, required_files in EXPECTED_LOCAL_PATHS.items():
        if path.is_symlink():
            problems.append(f"{path.relative_to(PLUGIN_ROOT)} must be a real directory")
            continue
        if not path.is_dir():
            problems.append(f"{path.relative_to(PLUGIN_ROOT)} is not a directory")
            continue
        for filename in required_files:
            if not (path / filename).is_file():
                problems.append(f"{(path / filename).relative_to(PLUGIN_ROOT)} is missing")
    for path in EXPECTED_LOCAL_FILES:
        if path.is_symlink():
            problems.append(f"{path.relative_to(PLUGIN_ROOT)} must be a real file")
        elif not path.is_file():
            problems.append(f"{path.relative_to(PLUGIN_ROOT)} is missing")
    return problems


def main() -> int:
    problems = layout_problems()
    if problems:
        names = "\n".join(f" - {problem}" for problem in problems)
        raise SystemExit(f"Analytics app runtime layout is out of sync:\n{names}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
