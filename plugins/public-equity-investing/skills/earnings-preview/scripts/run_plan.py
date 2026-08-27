#!/usr/bin/env python3
"""Execute an Earnings Preview Pack plan.

This script is deterministic: it reads local inputs, computes tables, fills templates, and writes outputs.
It does NOT fetch data from the internet.

Example:
  python scripts/run_plan.py path/to/plan.json
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

if __name__ == "__main__" and any(arg in {"-h", "--help"} for arg in sys.argv[1:]):
    print("Usage: python scripts/run_plan.py plan.json")
    print("Execute an earnings preview pack plan.")
    raise SystemExit(0)

import pandas as pd
from lib.calc import (
    auto_flag_delta,
    is_rate_metric,
    safe_bps_change,
    safe_pct_change,
    shift_period,
    trend_slope,
    two_year_stack,
)
from lib.changelog import maybe_write_changelog
from lib.io_utils import df_to_markdown_table, fmt_number, read_json, sha256_file, write_json
from lib.kpi_packs import get_kpis_for_pack, load_sector_packs
from lib.qa import resolve_input_paths, validate_inputs, validate_plan
from lib.render import TOKEN_RE, render_text

SKILL_ROOT = Path(__file__).resolve().parents[1]


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def render_with_defaults(template_path: Path, mapping: dict[str, str], default: str) -> str:
    """Render bracket-token templates and fill any unsupported tokens explicitly."""
    text = template_path.read_text(encoding="utf-8")
    complete = dict(mapping)
    for token in set(TOKEN_RE.findall(text)):
        if token not in complete or complete[token] in (None, ""):
            complete[token] = default
    return render_text(text, complete)


def unresolved_output_errors(output_name: str, text: str) -> list[str]:
    errors: list[str] = []
    if re.search(r"\[[A-Za-z0-9_]+\]", text):
        errors.append(f"{output_name}: unresolved bracket token remains")
    if re.search(r"\bTODO\b", text):
        errors.append(f"{output_name}: TODO placeholder remains")
    if re.search(r"\{\{[^}]+\}\}|\{[A-Z0-9_]+\}", text):
        errors.append(f"{output_name}: unresolved brace placeholder remains")
    return errors


def get_value(
    df: pd.DataFrame | None, ticker: str, fiscal_period_id: str, metric_id: str, value_col: str
) -> float | None:
    if df is None or df.empty:
        return None
    m = (
        (df.get("ticker") == ticker)
        & (df.get("fiscal_period_id") == fiscal_period_id)
        & (df.get("metric_id") == metric_id)
    )
    if m.sum() == 0:
        return None
    v = df.loc[m, value_col].iloc[0]
    try:
        return float(v)
    except Exception:
        return None


def get_unit_scale(
    df: pd.DataFrame | None, ticker: str, fiscal_period_id: str, metric_id: str, value_col: str
) -> tuple[str, float]:
    if df is None or df.empty:
        return ("", 1.0)
    m = (
        (df.get("ticker") == ticker)
        & (df.get("fiscal_period_id") == fiscal_period_id)
        & (df.get("metric_id") == metric_id)
    )
    if m.sum() == 0:
        return ("", 1.0)
    row = df.loc[m].iloc[0]
    unit = str(row.get("unit", ""))
    try:
        scale = float(row.get("scale", 1.0))
    except Exception:
        scale = 1.0
    return unit, scale


def fmt_metric(
    df: pd.DataFrame | None, ticker: str, fiscal_period_id: str, metric_id: str, value_col: str
) -> str:
    v = get_value(df, ticker, fiscal_period_id, metric_id, value_col)
    unit, scale = get_unit_scale(df, ticker, fiscal_period_id, metric_id, value_col)
    rate = is_rate_metric(metric_id, unit)
    decimals = 2 if rate else 1
    return fmt_number(v, unit, scale, decimals)


def pick_company_name(plan: dict, company_master: pd.DataFrame | None, ticker: str) -> str:
    if plan.get("company_name"):
        return str(plan.get("company_name")).strip()
    if company_master is None or company_master.empty:
        return ticker
    m = company_master.get("ticker") == ticker
    if m.sum() == 0:
        return ticker
    return str(company_master.loc[m, "company_name"].iloc[0])


def build_kpi_dashboard(
    ticker: str,
    fiscal_period_id: str,
    actuals: pd.DataFrame,
    consensus: pd.DataFrame,
    whisper: pd.DataFrame | None,
    kpi_list: list[str],
) -> pd.DataFrame:
    """Pretty (string) dashboard table for the note."""

    t = fiscal_period_id
    t_1 = shift_period(t, -1)
    t_4 = shift_period(t, -4)
    t_8 = shift_period(t, -8)

    rows = []
    for metric_id in kpi_list:
        # Prefer unit/scale from consensus (for the upcoming quarter), else fall back to last actual.
        cons_unit, cons_scale = get_unit_scale(consensus, ticker, t, metric_id, "estimate_value")
        act_unit, act_scale = get_unit_scale(actuals, ticker, t_1, metric_id, "value")
        unit = cons_unit or act_unit
        scale = cons_scale if cons_unit else act_scale
        metric_rate = is_rate_metric(metric_id, unit)

        last_act = get_value(actuals, ticker, t_1, metric_id, "value")
        yoy_base = get_value(actuals, ticker, t_4, metric_id, "value")
        stack_base = get_value(actuals, ticker, t_8, metric_id, "value")

        cons_est = get_value(consensus, ticker, t, metric_id, "estimate_value")
        whi_est = (
            get_value(whisper, ticker, t, metric_id, "whisper_value")
            if whisper is not None
            else None
        )

        # Growth/deltas
        if metric_rate:
            qoq = safe_bps_change(cons_est, last_act)
            yoy = safe_bps_change(cons_est, yoy_base)
        else:
            qoq = safe_pct_change(cons_est, last_act)
            yoy = safe_pct_change(cons_est, yoy_base)

        stack2 = two_year_stack(cons_est, stack_base) if (not metric_rate) else None

        # Trend: last 4 actual points (t-1 ... t-4)
        hist_vals = [
            get_value(actuals, ticker, shift_period(t, -i), metric_id, "value") for i in range(1, 5)
        ]
        tr = trend_slope([v for v in hist_vals if v is not None])

        flag = auto_flag_delta(whi_est, cons_est, metric_rate)

        rows.append(
            {
                "flag": "!" if flag else "",
                "metric_id": metric_id,
                "t_cons": fmt_number(cons_est, unit, scale, decimals=2 if metric_rate else 1),
                "t_1_act": fmt_number(last_act, unit, scale, decimals=2 if metric_rate else 1),
                "qoq": (
                    fmt_number(qoq, "bps", 1, 0)
                    if metric_rate
                    else ("" if qoq is None else f"{qoq * 100:.1f}%")
                ),
                "yoy": (
                    fmt_number(yoy, "bps", 1, 0)
                    if metric_rate
                    else ("" if yoy is None else f"{yoy * 100:.1f}%")
                ),
                "stack_2yr": ("" if stack2 is None else f"{stack2 * 100:.1f}%"),
                "whisper": fmt_number(whi_est, unit, scale, decimals=2 if metric_rate else 1),
                "trend": "" if tr is None else ("up" if tr > 0 else "down"),
                "commentary": "",
            }
        )

    df = pd.DataFrame(rows)
    return df[
        [
            "flag",
            "metric_id",
            "t_cons",
            "t_1_act",
            "qoq",
            "yoy",
            "stack_2yr",
            "whisper",
            "trend",
            "commentary",
        ]
    ]


def build_cons_vs_whisper_table(
    ticker: str,
    fiscal_period_id: str,
    consensus: pd.DataFrame,
    whisper: pd.DataFrame | None,
    metrics: list[str],
) -> pd.DataFrame:
    t = fiscal_period_id
    rows = []
    for metric_id in metrics:
        cons_val = get_value(consensus, ticker, t, metric_id, "estimate_value")
        cons_unit, cons_scale = get_unit_scale(consensus, ticker, t, metric_id, "estimate_value")
        metric_rate = is_rate_metric(metric_id, cons_unit)

        whi_val = (
            get_value(whisper, ticker, t, metric_id, "whisper_value")
            if whisper is not None
            else None
        )
        conf = None
        prov = ""
        if whisper is not None:
            m = (
                (whisper.get("ticker") == ticker)
                & (whisper.get("fiscal_period_id") == t)
                & (whisper.get("metric_id") == metric_id)
            )
            if m.sum() > 0:
                r = whisper.loc[m].iloc[0]
                conf = r.get("confidence_score")
                prov = str(r.get("provenance", ""))

        if metric_rate:
            delta = safe_bps_change(whi_val, cons_val)
            delta_str = fmt_number(delta, "bps", 1, 0)
        else:
            delta = safe_pct_change(whi_val, cons_val)
            delta_str = "" if delta is None else f"{delta * 100:.1f}%"

        rows.append(
            {
                "metric_id": metric_id,
                "consensus": fmt_number(
                    cons_val, cons_unit, cons_scale, decimals=2 if metric_rate else 1
                ),
                "whisper": fmt_number(
                    whi_val, cons_unit, cons_scale, decimals=2 if metric_rate else 1
                ),
                "delta": delta_str,
                "confidence": ""
                if conf is None or (isinstance(conf, float) and math.isnan(conf))
                else str(conf),
                "provenance": prov,
            }
        )
    return pd.DataFrame(rows)


def load_scenarios(path: Path) -> dict[str, dict[str, dict[str, float]]]:
    if not path.exists():
        return {}
    df = pd.read_csv(path)
    df.columns = [str(c).strip().lower() for c in df.columns]
    needed = {"scenario_name", "metric_id", "delta_type", "delta_value"}
    if not needed.issubset(set(df.columns)):
        return {}
    df["delta_value"] = pd.to_numeric(df["delta_value"], errors="coerce")
    out: dict[str, dict[str, dict[str, float]]] = {}
    for _, r in df.iterrows():
        scen = str(r["scenario_name"]).strip().lower()
        mid = str(r["metric_id"]).strip()
        dt = str(r["delta_type"]).strip().lower()
        dv = r["delta_value"]
        if scen not in out:
            out[scen] = {}
        out[scen][mid] = {"delta_type": dt, "delta_value": float(dv) if not pd.isna(dv) else 0.0}
    return out


def apply_delta(base_value: float | None, delta_type: str, delta_value: float) -> float | None:
    if base_value is None:
        return None
    if delta_type == "pct":
        return base_value * (1.0 + delta_value)
    if delta_type == "abs":
        return base_value + delta_value
    if delta_type == "bps":
        return base_value + (delta_value / 10_000.0)
    return base_value


def build_questions(sector_pack: str) -> tuple[str, list[str]]:
    """Return (markdown question list, watch-fors)."""

    universal = [
        (
            "Demand",
            [
                "What is changing in demand vs last quarter (by segment/channel), and what is the leading indicator?",
                "Where are you seeing pipeline conversion improve/worsen, and what is the time-to-close trend?",
            ],
        ),
        (
            "Pricing",
            [
                "What is price vs volume/mix this quarter? Any change in discounting or promotions?",
                "Are you seeing willingness-to-pay change (new logo pricing, renewals, upsells)?",
            ],
        ),
        (
            "Margins",
            [
                "What are the gross margin drivers (mix, input costs, cloud costs, utilization)?",
                "What is the incremental margin on revenue upside/downside into next quarter?",
            ],
        ),
        (
            "Guidance",
            [
                "How should we translate this quarter into next-quarter and FY guidance (assumptions and conservatism)?",
                "What changed since last quarter in the guidance algorithm (macro, FX, backlog, pipeline)?",
            ],
        ),
        (
            "Competition",
            [
                "What are you seeing competitively (win/loss, pricing pressure, feature parity)?",
            ],
        ),
        (
            "Capital allocation",
            [
                "Any changes in buybacks, capex, hiring pace, or balance sheet priorities?",
            ],
        ),
    ]

    watch = [
        "Vague 'macro' explanations without segment detail",
        "Guidance framed as a range but with asymmetric downside risk",
        "Non-GAAP addbacks expanding without clear explanation",
    ]

    addl: list[str] = []
    sp = sector_pack.lower()
    if sp == "saas":
        addl = [
            "NRR and churn: what is driving change (usage, seats, pricing, downgrades)?",
            "Bookings/billings: what is the pipeline build and conversion into next quarter?",
            "AI monetization: attach rate, pricing, cannibalization, and gross margin impact.",
        ]
        watch.extend(
            [
                "NRR stability vs seasonal/one-time factors",
                "RPO growth slowing (demand pullback signal)",
            ]
        )
    elif sp == "semiconductors":
        addl = [
            "Channel inventory: weeks on hand and evidence of double-ordering/destocking.",
            "Backlog quality: firm vs cancellable, and conversion timing.",
            "Units vs ASP: what is mix vs true demand?",
        ]
        watch.extend(["Lead times collapsing", "Backlog shrinking faster than shipments"])
    elif sp == "consumer_retail":
        addl = [
            "Comps breakdown: traffic vs ticket vs price; any trade-down?",
            "Markdown intensity and inventory health.",
            "Shrink/labor: what changed and what is the path forward?",
        ]
        watch.extend(
            ["Promo cadence increasing (margin risk)", "Inventory build without sales acceleration"]
        )

    lines = []
    qnum = 1
    for cat, qs in universal:
        lines.append(f"**{cat}**")
        for q in qs:
            lines.append(f"{qnum}) {q}")
            qnum += 1
        lines.append("")

    if addl:
        lines.append(f"**Sector add-ons ({sector_pack})**")
        for q in addl:
            lines.append(f"{qnum}) {q}")
            qnum += 1
        lines.append("")

    return "\n".join(lines).strip(), watch


def write_exports_xlsx(path: Path, tables: dict[str, pd.DataFrame | None]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for sheet, df in tables.items():
            if df is None:
                continue
            sheet_name = sheet[:31]
            df.to_excel(writer, sheet_name=sheet_name, index=False)


def write_exports_csv(dir_path: Path, tables: dict[str, pd.DataFrame | None]) -> None:
    dir_path.mkdir(parents=True, exist_ok=True)
    for name, df in tables.items():
        if df is None:
            continue
        (dir_path / f"{name}.csv").write_text(df.to_csv(index=False), encoding="utf-8")


def build_prior_quarter_table(ticker: str, fiscal_period_id: str, actuals: pd.DataFrame) -> str:
    """Small context table: last 4 quarters revenue and EPS actual."""
    periods = [shift_period(fiscal_period_id, -i) for i in range(1, 5)]
    rows = []
    for p in periods:
        rows.append(
            {
                "period": p,
                "revenue": fmt_metric(actuals, ticker, p, "revenue", "value"),
                "eps_diluted": fmt_metric(actuals, ticker, p, "eps_diluted", "value"),
            }
        )
    return df_to_markdown_table(pd.DataFrame(rows))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("plan_path", help="Path to plan.json")
    args = ap.parse_args()

    plan_path = Path(args.plan_path).resolve()
    plan = read_json(plan_path)
    if not isinstance(plan, dict):
        raise SystemExit("plan.json must be a JSON object")

    # Validate plan and inputs
    errors, warnings = validate_plan(plan)
    e2, w2, dfs = validate_inputs(plan, SKILL_ROOT)
    errors.extend(e2)
    warnings.extend(w2)
    if errors:
        raise SystemExit(
            "Validation failed. Run scripts/validate_plan.py and fix errors before executing."
        )

    ticker = str(plan.get("ticker")).strip()
    fiscal_period_id = str(plan.get("fiscal_period_id")).strip()
    sector_pack = str(plan.get("sector_pack")).strip()

    output_base = Path(str(plan.get("output_dir")))
    if not output_base.is_absolute():
        output_base = (SKILL_ROOT / output_base).resolve()
    output_run_dir = (output_base / ticker / fiscal_period_id).resolve()
    output_run_dir.mkdir(parents=True, exist_ok=True)

    # Preserve previous manifest for diff
    prev_manifest_path = output_run_dir / "run_manifest.json"
    if prev_manifest_path.exists():
        (output_run_dir / "run_manifest.previous.json").write_text(
            prev_manifest_path.read_text(encoding="utf-8"), encoding="utf-8"
        )

    # Load inputs
    paths = resolve_input_paths(plan, SKILL_ROOT)

    reported_financials = dfs.get("reported_financials")
    kpi_timeseries = dfs.get("kpi_timeseries")
    consensus = dfs.get("consensus_estimates")

    # Coerce numeric
    for df, col in [
        (reported_financials, "value"),
        (kpi_timeseries, "value"),
        (consensus, "estimate_value"),
    ]:
        if df is not None and col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    whisper = dfs.get("whisper_estimates")
    if whisper is not None and "whisper_value" in whisper.columns:
        whisper["whisper_value"] = pd.to_numeric(whisper["whisper_value"], errors="coerce")

    # Combine actuals
    actuals = pd.concat([reported_financials, kpi_timeseries], ignore_index=True, sort=False)

    # KPI list from sector pack + overrides
    packs = load_sector_packs(SKILL_ROOT / "assets/sector_kpi_packs.yaml")
    default_kpis = get_kpis_for_pack(packs, sector_pack)
    overrides = plan.get("kpi_overrides", {}) or {}
    inc = [str(x) for x in (overrides.get("include") or [])]
    exc = {str(x) for x in (overrides.get("exclude") or [])}

    kpi_list: list[str] = []
    for k in default_kpis + inc:
        if k and k not in exc and k not in kpi_list:
            kpi_list.append(k)

    # KPI dashboard + key tables
    kpi_dash = build_kpi_dashboard(ticker, fiscal_period_id, actuals, consensus, whisper, kpi_list)

    # Expectation bar: revenue, eps, + first two non-(rev,eps) KPIs
    key_metrics = ["revenue", "eps_diluted"]
    extras = [m for m in kpi_list if m not in key_metrics]
    key_metrics.extend(extras[:2])
    cons_vs_whisper = build_cons_vs_whisper_table(
        ticker, fiscal_period_id, consensus, whisper, key_metrics
    )

    # Scenario framing
    scen_file = (plan.get("scenarios") or {}).get("file")
    scenarios = load_scenarios((SKILL_ROOT / scen_file).resolve()) if scen_file else {}

    base_rev = get_value(consensus, ticker, fiscal_period_id, "revenue", "estimate_value")
    base_eps = get_value(consensus, ticker, fiscal_period_id, "eps_diluted", "estimate_value")

    def scen_val(s: str, metric_id: str, base: float | None) -> float | None:
        d = (scenarios.get(s, {}) or {}).get(metric_id)
        if not d:
            return base
        return apply_delta(base, d.get("delta_type", ""), float(d.get("delta_value", 0.0)))

    bull_rev = scen_val("bull", "revenue", base_rev)
    bear_rev = scen_val("bear", "revenue", base_rev)
    bull_eps = scen_val("bull", "eps_diluted", base_eps)
    bear_eps = scen_val("bear", "eps_diluted", base_eps)

    # Questions + watch-fors
    q_list_md, watch_fors = build_questions(sector_pack)
    call_questions = [line for line in q_list_md.splitlines() if re.match(r"^\d+\)", line.strip())]

    # Company name and timestamps
    company_master = dfs.get("company_master")
    company_name = pick_company_name(plan, company_master, ticker)
    freeze_ts = str(plan.get("freeze_time"))

    # Consensus snapshot timestamp (best effort)
    cons_ts = ""
    try:
        cr = consensus[
            (consensus.get("ticker") == ticker)
            & (consensus.get("fiscal_period_id") == fiscal_period_id)
        ]
        if len(cr) > 0:
            cons_ts = str(cr.get("snapshot_datetime").iloc[0])
    except Exception:
        cons_ts = ""

    # Fill KPI placeholders
    kpi1 = extras[0] if len(extras) > 0 else ""
    kpi2 = extras[1] if len(extras) > 1 else ""

    def cons_row(metric_id: str) -> dict:
        if cons_vs_whisper is None or cons_vs_whisper.empty:
            return {}
        m = cons_vs_whisper["metric_id"] == metric_id
        if m.sum() == 0:
            return {}
        r = cons_vs_whisper.loc[m].iloc[0].to_dict()
        return {k: "" if v is None else str(v) for k, v in r.items()}

    r_rev = cons_row("revenue")
    r_eps = cons_row("eps_diluted")
    r_k1 = cons_row(kpi1) if kpi1 else {}
    r_k2 = cons_row(kpi2) if kpi2 else {}

    # Prior quarter table
    prior_tbl = build_prior_quarter_table(ticker, fiscal_period_id, actuals)

    # Provenance notes
    prov_lines = [
        f"Inputs: {len([p for p in paths.values() if p.exists()])} files on disk.",
        f"Consensus snapshot: {cons_ts or freeze_ts}.",
        "See run_manifest.json for exact file paths and SHA256 hashes.",
    ]

    template_path = Path(
        str(
            (plan.get("templates") or {}).get(
                "preview_note", "assets/templates/preview_note_template.md"
            )
        )
    )
    if not template_path.is_absolute():
        template_path = (SKILL_ROOT / template_path).resolve()

    top_metrics = [m for m in [kpi1, kpi2, extras[2] if len(extras) > 2 else ""] if m]
    top_metric_text = (
        ", ".join(top_metrics) if top_metrics else "revenue, EPS, and the most debated company KPI"
    )
    bar_numbers = f"Revenue {fmt_metric(consensus, ticker, fiscal_period_id, 'revenue', 'estimate_value')}; EPS {fmt_metric(consensus, ticker, fiscal_period_id, 'eps_diluted', 'estimate_value')}"
    source_limited = "not modeled in deterministic sample inputs"

    mapping = {
        "COMPANY_NAME": company_name,
        "TICKER": ticker,
        "FISCAL_PERIOD_ID": fiscal_period_id,
        "PREVIEW_PERIOD": fiscal_period_id,
        "PRIOR_PERIOD": shift_period(fiscal_period_id, -1),
        "YEAR_AGO_PERIOD": shift_period(fiscal_period_id, -4),
        "FREEZE_TS": freeze_ts,
        "CONSENSUS_SNAPSHOT_TS": cons_ts or freeze_ts,
        "THESIS_1P": f"{company_name} is framed against a consensus bar of {bar_numbers}. The deterministic pack is screen-grade: it uses local sample inputs, not live market data, so peer read-through, options, and stock-reaction sections are explicitly marked where unsupported. The core debate should focus on {top_metric_text}.",
        "WHAT_MATTERS_1": extras[0] if len(extras) > 0 else "revenue",
        "WHAT_MATTERS_2": extras[1] if len(extras) > 1 else "EPS",
        "WHAT_MATTERS_3": extras[2] if len(extras) > 2 else "guidance quality",
        "CONS_REV": fmt_metric(consensus, ticker, fiscal_period_id, "revenue", "estimate_value"),
        "CONS_EPS": fmt_metric(
            consensus, ticker, fiscal_period_id, "eps_diluted", "estimate_value"
        ),
        "WHISPER_REV": r_rev.get("whisper", ""),
        "WHISPER_EPS": r_eps.get("whisper", ""),
        "REV_DELTA": r_rev.get("delta", ""),
        "EPS_DELTA": r_eps.get("delta", ""),
        "REV_NOTE": "",
        "EPS_NOTE": "Confirm whether consensus is GAAP, adjusted, operating, or provider-standardized EPS.",
        "EPS_QUALITY_WATCH": (
            "| Item | Why it could distort EPS | Post-print evidence needed | Model line affected |\n"
            "|---|---|---|---|\n"
            "| EPS basis | GAAP, adjusted, operating, and provider-standardized EPS can "
            "produce different surprise math. | Company reconciliation, filing EPS "
            "table, and consensus definition/as-of. | EPS / net income |\n"
            "| Tax / below-the-line / share count | Non-operating gains, tax items, FX, "
            "interest, marks, or dilution can flatter or depress headline EPS. | "
            "Source-tagged bridge from GAAP EPS to recurring or operating EPS if "
            "material. | EPS / net income / share count |"
        ),
        "CONS_KPI1": r_k1.get("consensus", ""),
        "WHISPER_KPI1": r_k1.get("whisper", ""),
        "KPI1_DELTA": r_k1.get("delta", ""),
        "KPI1_NOTE": "",
        "CONS_KPI2": r_k2.get("consensus", ""),
        "WHISPER_KPI2": r_k2.get("whisper", ""),
        "KPI2_DELTA": r_k2.get("delta", ""),
        "KPI2_NOTE": "",
        "IMPLIED_MOVE_PCT": "N/A",
        "VOL_NOTES": "N/A",
        "KPI_DASHBOARD_TABLE": df_to_markdown_table(kpi_dash),
        "BULL_DRIVERS": "upside to consensus on revenue/EPS and clean KPI momentum",
        "BASE_DRIVERS": "consensus case with stable KPI trend and no definition break",
        "BEAR_DRIVERS": "miss versus consensus or KPI deceleration versus recent trend",
        "BULL_REV": fmt_number(bull_rev, "USD", 1_000_000, 1) if bull_rev is not None else "",
        "BASE_REV": fmt_number(base_rev, "USD", 1_000_000, 1) if base_rev is not None else "",
        "BEAR_REV": fmt_number(bear_rev, "USD", 1_000_000, 1) if bear_rev is not None else "",
        "BULL_EPS": fmt_number(bull_eps, "USD", 1, 2) if bull_eps is not None else "",
        "BASE_EPS": fmt_number(base_eps, "USD", 1, 2) if base_eps is not None else "",
        "BEAR_EPS": fmt_number(bear_eps, "USD", 1, 2) if bear_eps is not None else "",
        "BULL_RXN": "positive revision skew if beat is broad-based",
        "BASE_RXN": "stock reaction depends on quality of guidance and KPI commentary",
        "BEAR_RXN": "negative revision skew if miss is tied to demand or margin quality",
        "BULL_KILL": "bull case weakens if KPI trend fails to confirm revenue/EPS upside",
        "BASE_KILL": "base case weakens if guidance quality or KPI definition changes",
        "BEAR_KILL": "bear case weakens if upside is broad-based and guidance is credible",
        "BULL_1": "Consensus may understate the operating leverage if revenue/KPI momentum holds.",
        "BULL_2": "A clean guide and stable KPI definitions would raise confidence in upside quality.",
        "BEAR_1": "Revenue/EPS upside without KPI support may be low-quality or one-time.",
        "BEAR_2": "Guidance conservatism or metric definition changes could blur the true bar.",
        "BAR_1": f"The bar is primarily {bar_numbers}; unsupported sections should be treated as data requests, not conclusions.",
        "DYNAMIC_QUESTION_LIST": q_list_md,
        "WATCHFOR_1": watch_fors[0] if len(watch_fors) > 0 else "",
        "WATCHFOR_2": watch_fors[1] if len(watch_fors) > 1 else "",
        "WATCHFOR_3": watch_fors[2] if len(watch_fors) > 2 else "",
        "PRIOR_Q_TABLE": prior_tbl,
        "PROVENANCE_NOTES": "\n".join([f"- {x}" for x in prov_lines]),
        "LAST_Q_BEAT_MISS": "See prior-quarter table; deterministic sample does not include explicit surprise history.",
        "LAST_Q_NARRATIVE": "Not modeled in deterministic sample inputs.",
        "LAST_Q_REACTION": "Not modeled in deterministic sample inputs.",
        "LAST_Q_DEBATED_KPI": top_metrics[0]
        if top_metrics
        else "not modeled in deterministic sample inputs",
        "LAST_Q_STILL_RELEVANT": "Confirm KPI durability and guidance quality.",
        "GUIDE_REV": "Not provided in deterministic sample inputs",
        "GUIDE_REV_SOURCE_Q": source_limited,
        "GUIDE_REV_TYPE": source_limited,
        "GUIDE_REV_NOTE": source_limited,
        "GUIDE_EPS": "Not provided in deterministic sample inputs",
        "GUIDE_EPS_SOURCE_Q": source_limited,
        "GUIDE_EPS_TYPE": source_limited,
        "GUIDE_EPS_NOTE": source_limited,
        "GUIDE_KPI": "Not provided in deterministic sample inputs",
        "GUIDE_KPI_SOURCE_Q": source_limited,
        "GUIDE_KPI_TYPE": source_limited,
        "GUIDE_KPI_NOTE": source_limited,
        "GUIDANCE_CREDIBILITY": "Guidance history was not analyzed in this deterministic sample run.",
        "WHISPER_FRAMING": "Whisper is shown only where local whisper inputs exist; otherwise treat as unavailable.",
        "WHISPER_CONFIDENCE": "source-dependent",
        "CATEGORY": "peer",
        "NAME": source_limited,
        "SIGNAL": source_limited,
        "WHY": source_limited,
        "READ_THROUGH": source_limited,
        "CONFIDENCE": "low",
        "QTR": source_limited,
        "CONTEXT": source_limited,
        "MOVE": source_limited,
        "DRIVER": source_limited,
        "DRIFT": source_limited,
        "IMPLIED_VS_HISTORY": source_limited,
        "MACRO_POSITIVE": source_limited,
        "MACRO_NEGATIVE": source_limited,
        "MACRO_UNCERTAIN": source_limited,
        "CATALYST": source_limited,
        "DIRECTION": source_limited,
        "EVIDENCE": source_limited,
        "SIGNAL_QUALITY": source_limited,
        "TOP_BAR_NUMBERS": bar_numbers,
        "TOP_3_METRICS": top_metric_text,
        "BULL_CATALYST": "broad-based beat plus credible guide",
        "BEAR_RISK": "KPI/margin miss or low-quality guide",
        "KEY_READ_THROUGH": source_limited,
        "MOVE_COMPARISON": source_limited,
        "CALL_WATCH": call_questions[0]
        if call_questions
        else "guidance assumptions and KPI durability",
    }

    rendered_note = render_with_defaults(template_path, mapping, source_limited)
    (output_run_dir / "preview_note.md").write_text(rendered_note, encoding="utf-8")

    # Exports
    cover = pd.DataFrame(
        [
            {
                "section": "Header",
                "metric": "Company / ticker",
                "value": f"{company_name} / {ticker}",
                "notes": "Earnings preview export pack landing page.",
            },
            {
                "section": "Header",
                "metric": "Preview period",
                "value": fiscal_period_id,
                "notes": f"Sector pack: {sector_pack}",
            },
            {
                "section": "Header",
                "metric": "Freeze time / consensus snapshot",
                "value": f"{freeze_ts} / {cons_ts or freeze_ts}",
                "notes": "Refresh inputs before relying on the workbook for PM/IC use.",
            },
            {
                "section": "Status",
                "metric": "Workbook mode",
                "value": "earnings_preview_export_pack",
                "notes": "Deterministic local-input export pack, not a live-market data pull.",
            },
            {
                "section": "Status",
                "metric": "Warnings",
                "value": len(warnings),
                "notes": "; ".join(str(w) for w in warnings[:3]) if warnings else "None flagged",
            },
            {
                "section": "Executive read-through",
                "metric": "Consensus bar",
                "value": bar_numbers,
                "notes": f"Core debate: {top_metric_text}",
            },
            {
                "section": "Scenario framing",
                "metric": "Revenue bull / base / bear",
                "value": f"{mapping['BULL_REV']} / {mapping['BASE_REV']} / {mapping['BEAR_REV']}",
                "notes": "Scenario assumptions are local-plan driven.",
            },
            {
                "section": "Scenario framing",
                "metric": "EPS bull / base / bear",
                "value": f"{mapping['BULL_EPS']} / {mapping['BASE_EPS']} / {mapping['BEAR_EPS']}",
                "notes": "Confirm GAAP/adjusted/operating EPS definition before comparing surprises.",
            },
            {
                "section": "KPI dashboard",
                "metric": "KPI rows",
                "value": len(kpi_dash),
                "notes": "See 07_KPI_Dashboard for chart-ready detail.",
            },
            {
                "section": "KPI dashboard",
                "metric": "Consensus vs whisper rows",
                "value": len(cons_vs_whisper),
                "notes": "See 08_Cons_vs_Whisper for deltas and confidence.",
            },
            {
                "section": "Call watch",
                "metric": "Primary call question",
                "value": call_questions[0]
                if call_questions
                else "guidance assumptions and KPI durability",
                "notes": "Use preview_note.md for the full written setup.",
            },
            {
                "section": "Source posture",
                "metric": "Input files found",
                "value": len([p for p in paths.values() if p.exists()]),
                "notes": "See run_manifest.json for paths, mtimes, and hashes.",
            },
            {
                "section": "Workbook map",
                "metric": "01-06 source tables",
                "value": "Period, financials, KPIs, guidance, consensus, whisper",
                "notes": "Raw/support exports; do not treat missing sections as analyzed.",
            },
            {
                "section": "Workbook map",
                "metric": "07-08 dashboard tables",
                "value": "KPI dashboard and consensus-vs-whisper",
                "notes": "Use these as chart-ready dashboard data.",
            },
        ]
    )
    tables: dict[str, pd.DataFrame | None] = {
        "Cover": cover,
        "01_PeriodIndex": dfs.get("fiscal_period_index"),
        "02_Financials_Q": dfs.get("reported_financials"),
        "03_KPIs_Q": dfs.get("kpi_timeseries"),
        "04_Guidance_History": dfs.get("guidance_history"),
        "05_Consensus_Snapshot": dfs.get("consensus_estimates"),
        "06_Whisper": dfs.get("whisper_estimates"),
        "07_KPI_Dashboard": kpi_dash,
        "08_Cons_vs_Whisper": cons_vs_whisper,
    }

    write_exports_xlsx(output_run_dir / "exports.xlsx", tables)
    write_exports_csv(output_run_dir / "exports", tables)

    # QA report
    output_errors = []
    output_errors.extend(unresolved_output_errors("preview_note.md", rendered_note))

    qa = {
        "status": "FAIL" if output_errors else ("PASS_WITH_WARNINGS" if warnings else "PASS"),
        "errors": output_errors,
        "warnings": warnings,
        "generated_at": utcnow_iso(),
    }
    write_json(output_run_dir / "qa_report.json", qa)
    (output_run_dir / "qa_report.md").write_text(
        "# QA report\n\n"
        + (
            "## Errors\n" + "\n".join([f"- {e}" for e in output_errors]) + "\n\n"
            if output_errors
            else ""
        )
        + (
            "## Warnings\n" + "\n".join([f"- {w}" for w in warnings])
            if warnings
            else "- No warnings"
        )
        + "\n",
        encoding="utf-8",
    )

    # Run manifest
    inputs_manifest = {}
    for name, p in paths.items():
        if p.exists():
            inputs_manifest[name] = {
                "path": str(p),
                "sha256": sha256_file(p),
                "mtime_utc": datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)
                .replace(microsecond=0)
                .isoformat()
                .replace("+00:00", "Z"),
            }

    manifest = {
        "run_id": utcnow_iso(),
        "ticker": ticker,
        "company_name": company_name,
        "fiscal_period_id": fiscal_period_id,
        "sector_pack": sector_pack,
        "freeze_time": freeze_ts,
        "consensus_statistic": plan.get("consensus_statistic"),
        "plan_path": str(plan_path),
        "outputs": {
            "output_run_dir": str(output_run_dir),
            "preview_note": str(output_run_dir / "preview_note.md"),
            "exports_xlsx": str(output_run_dir / "exports.xlsx"),
            "exports_csv_dir": str(output_run_dir / "exports"),
        },
        "inputs": {"files": inputs_manifest},
        "warnings": warnings,
    }
    write_json(output_run_dir / "run_manifest.json", manifest)

    # Changelog (if previous manifest exists)
    maybe_write_changelog(output_run_dir, manifest)

    print(f"Wrote outputs to: {output_run_dir}")
    if output_errors:
        raise SystemExit("Output QA failed. See qa_report.md for unresolved placeholders.")


if __name__ == "__main__":
    main()
