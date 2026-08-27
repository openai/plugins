#!/usr/bin/env python3
"""I/O utilities (CSV/XLSX) + small formatting helpers.

Design goals:
- Deterministic: no network, no terminal dependencies.
- Tolerant: case-insensitive columns, stable output ordering.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Iterable

import pandas as pd

SNAKE_RE_1 = re.compile(r"(.)([A-Z][a-z]+)")
SNAKE_RE_2 = re.compile(r"([a-z0-9])([A-Z])")


def to_snake_case(name: str) -> str:
    """Convert column names to snake_case."""
    name = name.strip().replace(" ", "_").replace("-", "_")
    name = SNAKE_RE_1.sub(r"\1_\2", name)
    name = SNAKE_RE_2.sub(r"\1_\2", name)
    name = re.sub(r"__+", "_", name)
    return name.lower()


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [to_snake_case(str(c)) for c in df.columns]
    return df


def read_table(path: Path) -> pd.DataFrame:
    """Read a CSV or XLSX into a DataFrame."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    if path.suffix.lower() in {".csv", ".txt"}:
        df = pd.read_csv(path)
    elif path.suffix.lower() in {".xlsx", ".xls"}:
        df = pd.read_excel(path)
    else:
        raise ValueError(f"Unsupported file type: {path.suffix}")

    return normalize_columns(df)


def require_columns(df: pd.DataFrame, required: Iterable[str], table_name: str) -> list[str]:
    """Return a list of missing columns (do not raise)."""
    required = [to_snake_case(c) for c in required]
    missing = [c for c in required if c not in df.columns]
    return missing


def coerce_numeric(df: pd.DataFrame, cols: Iterable[str]) -> pd.DataFrame:
    df = df.copy()
    for c in cols:
        c = to_snake_case(c)
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)


def read_json(path: Path) -> object:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def scale_suffix(scale: float) -> str:
    try:
        s = float(scale)
    except Exception:
        return ""
    if s == 1_000:
        return "k"
    if s == 1_000_000:
        return "m"
    if s == 1_000_000_000:
        return "b"
    return ""


def fmt_number(value: float | None, unit: str = "", scale: float = 1.0, decimals: int = 1) -> str:
    """Human-readable number for markdown note.

    - Currency scaled values use k/m/b suffix.
    - Ratios are rendered as percent.
    """
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except Exception:
        pass

    unit_l = (unit or "").lower()

    # Ratios and percents
    if unit_l in {"ratio", "pct", "percent"}:
        # assume ratio in [0,1] for margins/retention; render as %
        return f"{value * 100:.{decimals}f}%"

    # Basis points (already in bps)
    if unit_l == "bps":
        return f"{value:.0f}bps"

    # Currency / counts
    suf = scale_suffix(scale)
    try:
        v = float(value)
    except Exception:
        return str(value)

    if suf:
        return f"{v:,.{decimals}f}{suf}"

    # Non-scaled
    if abs(v) >= 1000:
        return f"{v:,.{decimals}f}"
    return f"{v:.{decimals}f}"


def df_to_markdown_table(df: pd.DataFrame, max_rows: int = 50) -> str:
    """Render a small DataFrame as a markdown table (no external deps)."""
    if df is None or df.empty:
        return "(no data)"

    df = df.copy()
    if len(df) > max_rows:
        df = df.head(max_rows)

    # Convert everything to string
    cols = list(df.columns)
    rows = []
    for _, r in df.iterrows():
        rows.append(["" if pd.isna(r[c]) else str(r[c]) for c in cols])

    # Column widths
    widths = [len(str(c)) for c in cols]
    for row in rows:
        widths = [max(w, len(str(cell))) for w, cell in zip(widths, row)]

    def fmt_row(vals: list[str]) -> str:
        return "| " + " | ".join(str(v).ljust(w) for v, w in zip(vals, widths)) + " |"

    header = fmt_row([str(c) for c in cols])
    sep = "| " + " | ".join("-" * w for w in widths) + " |"
    body = "\n".join(fmt_row(r) for r in rows)
    return "\n".join([header, sep, body])
