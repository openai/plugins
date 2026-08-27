#!/usr/bin/env python3
"""Profile messy CSV/XLSX data before analyst-grade cleaning.

Outputs JSON with header suggestions, type guesses, domain hints, and quality issues.
This script is intentionally conservative: it profiles and flags; it does not mutate data.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

BLANK_TOKENS = {"", "-", "--", "n/a", "na", "null", "none", "not available", "#n/a", "nan"}
TOTAL_RE = re.compile(r"\b(grand\s+total|subtotal|sub-total|total)\b", re.I)
ID_HINT_RE = re.compile(
    r"\b(id|code|sku|zip|postal|phone|cusip|isin|sedol|ticker|account\s*#|invoice\s*#|po\s*#|employee)\b",
    re.I,
)
CURRENCY_RE = re.compile(r"[$€£¥]|\b(usd|eur|gbp|jpy|cad|aud|chf|cny)\b", re.I)
PERCENT_RE = re.compile(r"%|\bbps\b|\bbasis\s+points\b", re.I)
NUMERIC_RE = re.compile(
    r"^\(?[+-]?\s*[$€£¥]?\s*\d{1,3}(?:,\d{3})*(?:\.\d+)?\s*\)?$|^\(?[+-]?\s*[$€£¥]?\s*\d+(?:\.\d+)?\s*\)?$"
)

DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "financial_statement_reporting": [
        "actual",
        "forecast",
        "guidance",
        "segment",
        "revenue",
        "gross margin",
        "opex",
        "capex",
        "ebitda",
        "eps",
        "fiscal",
        "quarter",
        "annual",
        "cash flow",
        "balance sheet",
        "share count",
    ],
    "investing_markets": [
        "ticker",
        "cusip",
        "isin",
        "sedol",
        "security",
        "portfolio",
        "nav",
        "return",
        "yield",
        "spread",
        "benchmark",
        "price",
        "holdings",
        "exposure",
        "market value",
        "bps",
    ],
    "credit_markets_handoff": [
        "issuer",
        "bond",
        "loan",
        "coupon",
        "maturity",
        "spread",
        "yield",
        "rating",
        "covenant",
        "liquidity",
        "debt",
        "recovery",
        "priority",
        "collateral",
    ],
    "portfolio_risk": [
        "position",
        "weight",
        "exposure",
        "p&l",
        "benchmark",
        "factor",
        "beta",
        "var",
        "sector",
        "gross",
        "net exposure",
        "hedge",
    ],
    "consensus_provider_export": [
        "consensus",
        "estimate",
        "provider",
        "street",
        "actual",
        "revision",
        "mean",
        "median",
        "high",
        "low",
        "fiscal period",
    ],
    "event_driven_special_situations": [
        "deal",
        "consideration",
        "spread",
        "probability",
        "closing",
        "regulatory",
        "approval",
        "break price",
        "unaffected",
        "tender",
        "merger",
    ],
}


def ensure_dependencies() -> None:
    """Load pandas only when profiling runs; argparse --help should not require deps."""
    global pd
    try:
        import pandas as pandas
    except ImportError as exc:
        print("ERROR: pandas is required to profile tabular data.", file=sys.stderr)
        print("Install with: python -m pip install -r scripts/requirements.txt", file=sys.stderr)
        raise SystemExit(2) from exc
    pd = pandas


def norm_cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    return re.sub(r"\s+", " ", str(value).replace("\u00a0", " ").strip())


def is_blank(value: Any) -> bool:
    return norm_cell(value).lower() in BLANK_TOKENS


def map_dataframe(df: pd.DataFrame, func):
    mapper = getattr(df, "map", None)
    if mapper is not None:
        return mapper(func)
    return df.applymap(func)


def safe_sheet_name(name: Any) -> str:
    text = norm_cell(name) or "sheet"
    return text[:80]


def read_input(path: Path, sheet: str | None = None) -> dict[str, pd.DataFrame]:
    ext = path.suffix.lower()
    if ext in {".xlsx", ".xlsm", ".xls"}:
        data = pd.read_excel(
            path,
            sheet_name=sheet if sheet else None,
            header=None,
            dtype=object,
            keep_default_na=False,
        )
        if isinstance(data, pd.DataFrame):
            return {sheet or "sheet1": data}
        return {safe_sheet_name(k): v for k, v in data.items()}
    if ext in {".csv", ".tsv", ".txt"}:
        sep = "\t" if ext == ".tsv" else None
        try:
            df = pd.read_csv(
                path,
                header=None,
                dtype=object,
                keep_default_na=False,
                sep=sep,
                engine="python",
                encoding="utf-8-sig",
            )
        except pd.errors.ParserError:
            df = pd.read_csv(
                path,
                header=None,
                dtype=object,
                keep_default_na=False,
                sep=sep,
                engine="python",
                encoding="utf-8-sig",
                on_bad_lines="warn",
            )
        return {"csv": df}
    raise ValueError(f"unsupported input type: {ext}")


def cell_has_letters(text: str) -> bool:
    return bool(re.search(r"[A-Za-z]", text))


def looks_numeric(text: str) -> bool:
    if not text:
        return False
    return bool(NUMERIC_RE.match(text.replace("%", "")))


def header_score(df: pd.DataFrame, row_idx: int) -> float:
    row = [norm_cell(v) for v in df.iloc[row_idx].tolist()]
    nonempty = [v for v in row if v]
    if len(nonempty) < 2:
        return -1000.0
    unique_ratio = len({v.lower() for v in nonempty}) / max(len(nonempty), 1)
    text_ratio = sum(cell_has_letters(v) for v in nonempty) / max(len(nonempty), 1)
    numeric_ratio = sum(looks_numeric(v) for v in nonempty) / max(len(nonempty), 1)
    next_ratio = 0.0
    if row_idx + 1 < len(df):
        next_vals = [norm_cell(v) for v in df.iloc[row_idx + 1].tolist()]
        next_ratio = sum(bool(v) for v in next_vals) / max(len(next_vals), 1)
    total_penalty = 2.0 if any(TOTAL_RE.search(v) for v in nonempty) else 0.0
    title_penalty = 1.5 if row_idx > 0 and len(nonempty) == 2 else 0.0
    return (
        (len(nonempty) * 0.15)
        + (unique_ratio * 2.0)
        + (text_ratio * 3.0)
        + (next_ratio * 1.5)
        - (numeric_ratio * 2.0)
        - total_penalty
        - title_penalty
    )


def detect_header_row(df: pd.DataFrame) -> int:
    max_scan = min(len(df), 30)
    if max_scan == 0:
        return 0
    scores = [(header_score(df, i), i) for i in range(max_scan)]
    scores.sort(reverse=True)
    best_score, best_idx = scores[0]
    return best_idx if best_score > -999 else 0


def unique_headers(raw_headers: Iterable[Any]) -> tuple[list[str], list[dict[str, Any]]]:
    seen: dict[str, int] = defaultdict(int)
    headers: list[str] = []
    notes: list[dict[str, Any]] = []
    for idx, raw in enumerate(raw_headers, start=1):
        base = norm_cell(raw)
        if not base:
            base = f"column_{idx}"
            notes.append({"column_index": idx, "issue": "blank_header", "cleaned": base})
        cleaned = re.sub(r"\s+", " ", base)
        key = cleaned.lower()
        seen[key] += 1
        if seen[key] > 1:
            cleaned = f"{cleaned}_{seen[key]}"
            notes.append(
                {
                    "column_index": idx,
                    "issue": "duplicate_header",
                    "cleaned": cleaned,
                    "original": base,
                }
            )
        headers.append(cleaned)
    return headers, notes


def parse_number(text: str) -> float | None:
    s = norm_cell(text)
    if not s or s.lower() in BLANK_TOKENS:
        return None
    s = CURRENCY_RE.sub("", s)
    s = s.replace(",", "").replace("%", "").strip()
    neg = s.startswith("(") and s.endswith(")")
    s = s.strip("() ")
    try:
        value = float(s)
        return -value if neg else value
    except ValueError:
        return None


def parse_bool(text: str) -> bool | None:
    s = norm_cell(text).lower()
    if s in {"true", "yes", "y", "1"}:
        return True
    if s in {"false", "no", "n", "0"}:
        return False
    return None


def parse_date_ratio(values: list[str]) -> float:
    candidates = [v for v in values if v and not looks_numeric(v)]
    if not candidates:
        return 0.0
    parsed = pd.to_datetime(pd.Series(candidates[:1000]), errors="coerce")
    return float(parsed.notna().sum()) / max(len(candidates[:1000]), 1)


def infer_type(header: str, values: list[str]) -> dict[str, Any]:
    nonblank = [v for v in values if v and v.lower() not in BLANK_TOKENS]
    sample = nonblank[:5]
    if not nonblank:
        return {"type": "empty", "confidence": 1.0, "sample_values": []}

    header_id_like = bool(ID_HINT_RE.search(header))
    leading_zero = any(re.match(r"^0\d+", v) for v in nonblank[:1000])
    bool_ratio = sum(parse_bool(v) is not None for v in nonblank[:1000]) / max(
        min(len(nonblank), 1000), 1
    )
    num_ratio = sum(parse_number(v) is not None for v in nonblank[:1000]) / max(
        min(len(nonblank), 1000), 1
    )
    pct_ratio = sum(bool(PERCENT_RE.search(v)) for v in nonblank[:1000]) / max(
        min(len(nonblank), 1000), 1
    )
    currency_ratio = sum(bool(CURRENCY_RE.search(v)) for v in nonblank[:1000]) / max(
        min(len(nonblank), 1000), 1
    )
    date_ratio = parse_date_ratio(nonblank)

    if header_id_like or leading_zero:
        guess = "text_identifier"
        conf = 0.90 if header_id_like else 0.75
    elif bool_ratio >= 0.90:
        guess = "boolean"
        conf = bool_ratio
    elif pct_ratio >= 0.60:
        guess = "percent_or_bps"
        conf = pct_ratio
    elif currency_ratio >= 0.40 and num_ratio >= 0.70:
        guess = "currency_amount"
        conf = min(0.95, (currency_ratio + num_ratio) / 2)
    elif num_ratio >= 0.85:
        guess = "number"
        conf = num_ratio
    elif date_ratio >= 0.80:
        guess = "date_or_datetime"
        conf = date_ratio
    elif 0.30 <= num_ratio < 0.85 or 0.30 <= date_ratio < 0.80:
        guess = "mixed"
        conf = max(num_ratio, date_ratio)
    else:
        guess = "text"
        conf = 0.70

    return {
        "type": guess,
        "confidence": round(float(conf), 3),
        "sample_values": sample,
        "numeric_parse_ratio": round(float(num_ratio), 3),
        "date_parse_ratio": round(float(date_ratio), 3),
        "currency_signal_ratio": round(float(currency_ratio), 3),
        "percent_signal_ratio": round(float(pct_ratio), 3),
        "boolean_parse_ratio": round(float(bool_ratio), 3),
    }


def profile_column(header: str, series: pd.Series, row_count: int) -> dict[str, Any]:
    values = [norm_cell(v) for v in series.tolist()]
    missing = sum(v.lower() in BLANK_TOKENS for v in values)
    nonblank = [v for v in values if v.lower() not in BLANK_TOKENS]
    type_info = infer_type(header, values)
    return {
        "field": header,
        "missing_count": int(missing),
        "missing_pct": round(missing / max(row_count, 1), 4),
        "unique_count": int(len(set(nonblank))),
        **type_info,
    }


def duplicate_row_count(df: pd.DataFrame) -> int:
    if df.empty:
        return 0
    normalized = map_dataframe(df, lambda v: norm_cell(v).lower())
    return int(normalized.duplicated().sum())


def likely_total_rows(df: pd.DataFrame) -> list[int]:
    rows: list[int] = []
    for idx, row in df.iterrows():
        vals = [norm_cell(v) for v in row.tolist()[:5]]
        if any(TOTAL_RE.search(v) for v in vals if v):
            rows.append(int(idx) + 1)  # 1-based within cleaned data segment, not original sheet
    return rows[:100]


def infer_domain(headers: list[str], sheet_name: str, data_values: Iterable[str]) -> dict[str, Any]:
    text = " ".join([sheet_name] + headers + list(data_values)[:200]).lower()
    scores: dict[str, int] = {}
    matched: dict[str, list[str]] = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        hits = [kw for kw in keywords if re.search(r"\b" + re.escape(kw.lower()) + r"\b", text)]
        if hits:
            scores[domain] = len(hits)
            matched[domain] = hits[:12]
    if not scores:
        return {"best_guess": "general_tabular", "scores": {}, "matched_keywords": {}}
    best = max(scores.items(), key=lambda x: x[1])[0]
    result = {"best_guess": best, "scores": scores, "matched_keywords": matched}
    if best == "credit_markets_handoff":
        result["routing"] = "route_to_credit_markets"
        result["routing_note"] = (
            "Credit instrument tables belong in Credit Markets unless used only as public-equity risk context."
        )
    return result


def profile_sheet(sheet_name: str, df: pd.DataFrame) -> dict[str, Any]:
    header_idx = detect_header_row(df)
    raw_headers = df.iloc[header_idx].tolist() if len(df) else []
    headers, header_notes = unique_headers(raw_headers)
    data = df.iloc[header_idx + 1 :].copy() if len(df) else pd.DataFrame()
    if len(headers) == data.shape[1]:
        data.columns = headers
    row_count = int(len(data))
    col_count = int(data.shape[1])

    empty_rows = (
        int(sum(all(is_blank(v) for v in row) for row in data.values.tolist())) if row_count else 0
    )
    empty_cols = (
        int(sum(all(is_blank(v) for v in data.iloc[:, i].tolist()) for i in range(data.shape[1])))
        if col_count
        else 0
    )
    col_profiles = [profile_column(col, data[col], row_count) for col in data.columns]
    all_sample_values: list[str] = []
    for col in data.columns[:10]:
        all_sample_values.extend(
            [norm_cell(v) for v in data[col].head(20).tolist() if norm_cell(v)]
        )

    issues: list[dict[str, Any]] = []
    for note in header_notes:
        issues.append({"severity": "warning", "issue_type": note["issue"], "details": note})
    if empty_rows:
        issues.append(
            {"severity": "info", "issue_type": "fully_empty_rows", "affected_count": empty_rows}
        )
    if empty_cols:
        issues.append(
            {"severity": "info", "issue_type": "fully_empty_columns", "affected_count": empty_cols}
        )
    dupes = duplicate_row_count(data)
    if dupes:
        issues.append(
            {"severity": "warning", "issue_type": "exact_duplicate_rows", "affected_count": dupes}
        )
    subtotal_rows = likely_total_rows(data)
    if subtotal_rows:
        issues.append(
            {
                "severity": "warning",
                "issue_type": "possible_total_or_subtotal_rows",
                "example_row_numbers_in_data_segment": subtotal_rows[:20],
                "affected_count_at_least": len(subtotal_rows),
            }
        )
    for cp in col_profiles:
        if cp["missing_pct"] >= 0.80 and cp["type"] != "empty":
            issues.append(
                {
                    "severity": "info",
                    "issue_type": "high_missingness",
                    "field": cp["field"],
                    "missing_pct": cp["missing_pct"],
                }
            )
        if cp["type"] == "mixed":
            issues.append(
                {
                    "severity": "warning",
                    "issue_type": "mixed_type_column",
                    "field": cp["field"],
                    "numeric_parse_ratio": cp.get("numeric_parse_ratio"),
                    "date_parse_ratio": cp.get("date_parse_ratio"),
                }
            )

    return {
        "sheet_name": sheet_name,
        "source_dimensions": {"rows": int(df.shape[0]), "columns": int(df.shape[1])},
        "detected_header_row_1_based": int(header_idx + 1),
        "data_dimensions_after_header": {"rows": row_count, "columns": col_count},
        "domain_hint": infer_domain(headers, sheet_name, all_sample_values),
        "columns": col_profiles,
        "quality_issues": issues,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Profile messy CSV/XLSX data and emit JSON diagnostics."
    )
    parser.add_argument("input", help="input .xlsx, .xls, .csv, .tsv, or .txt file")
    parser.add_argument("--output", "-o", default="profile.json", help="output JSON path")
    parser.add_argument("--sheet", help="optional Excel sheet name to profile")
    args = parser.parse_args()
    ensure_dependencies()

    path = Path(args.input)
    tables = read_input(path, args.sheet)
    profile = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_file": str(path),
        "sheets_profiled": len(tables),
        "sheets": [profile_sheet(name, df) for name, df in tables.items()],
    }
    out = Path(args.output)
    out.write_text(json.dumps(profile, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote profile to {out}")


if __name__ == "__main__":
    main()
