#!/usr/bin/env python3
"""Run the Earnings Deep Dive & Summary pipeline.

This script intentionally focuses on deterministic steps:
- Validate inputs
- Compute beat/miss and guidance deltas
- Render markdown outputs (ExecutiveOverview, TearSheet, DeepDive)
- Optionally update a model workbook via driver registry and create a changelog + diff

It does **not** invent narrative. If drivers bullets, watch list, or narrative
are not provided, generated reports use precise limitation labels and fail QA
if authoring placeholders remain.
"""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

if __name__ == "__main__" and any(arg in {"-h", "--help"} for arg in sys.argv[1:]):
    print("Usage: python scripts/run_plan.py plan.json")
    print("Run the deterministic earnings deep-dive pipeline.")
    raise SystemExit(0)

import pandas as pd

try:
    from .utils.io_utils import ensure_dir, read_json, write_text
    from .utils.math_utils import compute_delta
    from .utils.validation_utils import as_float_or_none, is_missing
    from .validate_plan import validate_plan
except ImportError:
    from utils.io_utils import ensure_dir, read_json, write_text
    from utils.math_utils import compute_delta
    from utils.validation_utils import as_float_or_none, is_missing
    from validate_plan import validate_plan


def _read_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def _format_number(val: float | None, units: str) -> str:
    if val is None:
        return "not provided"
    # Heuristic formatting
    if units.strip() in {"USD", "EPS"}:
        return f"{val:.2f}"
    if units.endswith("%"):
        return f"{val:.2f}%"
    # default
    if abs(val) >= 1000:
        return f"{val:,.0f}"
    return f"{val:,.2f}"


def _format_pct(val: float | None) -> str:
    if val is None:
        return "not provided"
    return f"{val * 100:.1f}%"


def _display(value: Any, fallback: str = "not provided") -> str:
    return fallback if is_missing(value) else str(value)


PLACEHOLDER_RE = re.compile(
    r"(\{[A-Z0-9_]+\}|\bTODO\b|MISSING:\s*(add|explain|map|summarize|write|list|populate|decompose))",
    re.IGNORECASE,
)


def unresolved_placeholder_errors(outputs: dict[str, str]) -> list[str]:
    errors: list[str] = []
    for name, text in outputs.items():
        matches = sorted({m.group(0) for m in PLACEHOLDER_RE.finditer(text)})
        if matches:
            errors.append(f"{name}: unresolved authoring placeholder(s): {', '.join(matches[:6])}")
    return errors


@dataclass
class BeatMissRow:
    metric: str
    period: str
    units: str
    reported: float | None
    consensus: float | None
    internal: float | None
    delta_cons: float | None
    surprise_cons: float | None
    delta_int: float | None
    surprise_int: float | None
    source_tag: str
    gaap_flag: str = ""
    comparable_gaap_metric: str = ""
    reconciliation_source_tag: str = ""
    notes: str = ""


@dataclass
class GuidanceRow:
    metric: str
    period: str
    units: str
    low: float | None
    high: float | None
    midpoint: float | None
    consensus: float | None
    internal: float | None
    delta_cons_mid: float | None
    delta_int_mid: float | None
    source_tag: str


def _pick_first(df: pd.DataFrame, metric: str, period: str, est_type: str) -> float | None:
    sub = df[
        (df["MetricName"] == metric) & (df["Period"] == period) & (df["EstimateType"] == est_type)
    ]
    if len(sub) == 0:
        return None
    return as_float_or_none(sub.iloc[0]["Value"])


def compute_beat_miss(metrics_df: pd.DataFrame, estimates_df: pd.DataFrame) -> list[BeatMissRow]:
    rows: list[BeatMissRow] = []
    m = metrics_df.copy()
    m["IsTearSheet"] = m["IsTearSheet"].astype(str)
    m = m[m["IsTearSheet"].str.upper().isin(["Y", "YES", "TRUE", "1"])].copy()

    def _order(x: str) -> int:
        try:
            return int(float(x))
        except Exception:
            return 999

    m["_order"] = m["DisplayOrder"].apply(_order)
    m = m.sort_values("_order")

    for _, r in m.iterrows():
        metric = r["MetricName"]
        period = r["Period"]
        units = r["Units"]
        reported = as_float_or_none(r["Value"])
        source_tag = _display(r.get("SourceTag"), "source not provided")

        cons = _pick_first(estimates_df, metric, period, "Consensus")
        internal = _pick_first(estimates_df, metric, period, "Internal")

        dcons, scons = compute_delta(reported, cons)
        dint, sint = compute_delta(reported, internal)

        rows.append(
            BeatMissRow(
                metric=metric,
                period=period,
                units=units,
                reported=reported,
                consensus=cons,
                internal=internal,
                delta_cons=dcons,
                surprise_cons=scons,
                delta_int=dint,
                surprise_int=sint,
                source_tag=source_tag,
                gaap_flag=str(r.get("GAAP_Flag") or ""),
                comparable_gaap_metric=str(r.get("ComparableGAAPMetricName") or ""),
                reconciliation_source_tag=str(r.get("ReconciliationSourceTag") or ""),
                notes=str(r.get("Notes") or ""),
            )
        )

    return rows


def compute_guidance(guidance_df: pd.DataFrame, estimates_df: pd.DataFrame) -> list[GuidanceRow]:
    rows: list[GuidanceRow] = []
    for _, r in guidance_df.iterrows():
        metric = r["MetricName"]
        period = r["Period"]
        units = r["Units"]
        low = as_float_or_none(r["Low"])
        high = as_float_or_none(r["High"])
        source_tag = _display(r.get("SourceTag"), "source not provided")

        midpoint: float | None = None
        if low is not None and high is not None:
            midpoint = (low + high) / 2.0

        cons = _pick_first(estimates_df, metric, period, "Consensus")
        internal = _pick_first(estimates_df, metric, period, "Internal")

        dcons, _ = compute_delta(midpoint, cons)
        dint, _ = compute_delta(midpoint, internal)

        rows.append(
            GuidanceRow(
                metric=metric,
                period=period,
                units=units,
                low=low,
                high=high,
                midpoint=midpoint,
                consensus=cons,
                internal=internal,
                delta_cons_mid=dcons,
                delta_int_mid=dint,
                source_tag=source_tag,
            )
        )
    return rows


def _md_table_beatmiss(rows: list[BeatMissRow]) -> str:
    lines: list[str] = []
    lines.append(
        "| Metric | Reported | Consensus | Δ | Surprise % | Internal | Δ | Surprise % | SourceTag |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---|")
    for r in rows:
        lines.append(
            "| {m} | {rep} | {c} | {dc} | {sc} | {i} | {di} | {si} | {src} |".format(
                m=r.metric,
                rep=_format_number(r.reported, r.units),
                c=_format_number(r.consensus, r.units),
                dc=_format_number(r.delta_cons, r.units),
                sc=_format_pct(r.surprise_cons),
                i=_format_number(r.internal, r.units),
                di=_format_number(r.delta_int, r.units),
                si=_format_pct(r.surprise_int),
                src=r.source_tag,
            )
        )
    return "\n".join(lines)


def _md_table_guidance(rows: list[GuidanceRow]) -> str:
    lines: list[str] = []
    lines.append(
        "| Metric | Period | Low | High | Mid | Consensus | Δ(mid) | Internal | Δ(mid) | SourceTag |"
    )
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---|")
    for r in rows:
        lines.append(
            "| {m} | {p} | {lo} | {hi} | {mid} | {c} | {dc} | {i} | {di} | {src} |".format(
                m=r.metric,
                p=r.period,
                lo=_format_number(r.low, r.units),
                hi=_format_number(r.high, r.units),
                mid=_format_number(r.midpoint, r.units),
                c=_format_number(r.consensus, r.units),
                dc=_format_number(r.delta_cons_mid, r.units),
                i=_format_number(r.internal, r.units),
                di=_format_number(r.delta_int_mid, r.units),
                src=r.source_tag,
            )
        )
    return "\n".join(lines)


EPS_DISTORTION_TERMS = (
    "asset sale",
    "below-the-line",
    "equity investment",
    "fair value",
    "fx",
    "gain",
    "impairment",
    "litigation",
    "loss",
    "mark-to-market",
    "non-operating",
    "non-recurring",
    "one-time",
    "pension",
    "restructuring",
    "share count",
    "tax",
)


def _metric_has(row: BeatMissRow, *needles: str) -> bool:
    metric = row.metric.lower()
    return all(needle.lower() in metric for needle in needles)


def _first_row(rows: list[BeatMissRow], *needles: str, period: str = "") -> BeatMissRow | None:
    for row in rows:
        if period and row.period != period:
            continue
        if _metric_has(row, *needles):
            return row
    return None


def _distortion_text(row: BeatMissRow) -> str:
    text = " ".join(
        [
            row.metric,
            row.gaap_flag,
            row.comparable_gaap_metric,
            row.reconciliation_source_tag,
            row.notes,
        ]
    ).lower()
    found = [term for term in EPS_DISTORTION_TERMS if term in text]
    return ", ".join(found)


def _surprise_gap_flag(eps_row: BeatMissRow, peer_row: BeatMissRow | None, label: str) -> str:
    if eps_row.surprise_cons is None or peer_row is None or peer_row.surprise_cons is None:
        return ""
    eps_surprise = abs(eps_row.surprise_cons)
    peer_surprise = abs(peer_row.surprise_cons)
    if eps_surprise >= 0.15 and eps_surprise > max(peer_surprise * 2.0, peer_surprise + 0.10):
        return f"GAAP EPS surprise materially outpaced {label} surprise"
    return ""


def render_eps_quality_screen(rows: list[BeatMissRow]) -> str:
    gaap_eps_rows = [
        row
        for row in rows
        if "eps" in row.metric.lower()
        and ("gaap" in row.metric.lower() or row.gaap_flag.lower() == "gaap")
    ]
    if not gaap_eps_rows:
        return (
            "EPS quality screen not run: GAAP diluted EPS row was not provided in "
            "normalized metrics. Add GAAP EPS, adjusted/operating EPS if available, "
            "and below-the-line notes before using EPS surprise as a recurring "
            "earnings signal."
        )

    lines: list[str] = []
    lines.append("| Check | Status | Read-through | Source |")
    lines.append("|---|---|---|---|")

    for eps_row in gaap_eps_rows:
        revenue_row = _first_row(rows, "revenue", period=eps_row.period)
        operating_row = _first_row(rows, "operating", period=eps_row.period)
        adjusted_eps_row = _first_row(rows, "adjusted", "eps", period=eps_row.period)
        flags = [
            flag
            for flag in [
                _distortion_text(eps_row),
                _surprise_gap_flag(eps_row, revenue_row, "revenue"),
                _surprise_gap_flag(eps_row, operating_row, "operating income"),
            ]
            if flag
        ]

        if flags:
            status = "expanded bridge required"
            read_through = (
                "Do not capitalize the full GAAP EPS beat as recurring until "
                + "; ".join(flags)
                + " is isolated."
            )
        else:
            status = "no material trigger in normalized inputs"
            read_through = (
                "GAAP EPS still needs filing/release tie-out, but no explicit "
                "distortion flag was supplied."
            )

        lines.append(
            f"| GAAP EPS surprise quality ({eps_row.period}) | {status} | "
            f"{read_through} | {eps_row.source_tag} |"
        )

        if adjusted_eps_row:
            lines.append(
                "| Adjusted / operating EPS comparison | provided | "
                f"Compare {_format_number(eps_row.reported, eps_row.units)} GAAP EPS "
                f"with {_format_number(adjusted_eps_row.reported, adjusted_eps_row.units)} "
                "adjusted/operating EPS before updating forward EPS. | "
                f"{adjusted_eps_row.source_tag} |"
            )
        else:
            lines.append(
                "| Adjusted / operating EPS comparison | source not provided | "
                "Request company reconciliation or calculate a clearly labeled "
                "analyst-derived recurring EPS bridge if the EPS beat matters. | "
                "source not provided |"
            )

    return "\n".join(lines)


def _read_optional_lines(path: Path, max_items: int) -> list[str]:
    if not path.exists():
        return []
    txt = path.read_text(encoding="utf-8").splitlines()
    items: list[str] = []
    for line in txt:
        line = line.strip()
        if not line:
            continue
        items.append(line)
        if len(items) >= max_items:
            break
    return items


def render_tearsheet(
    plan: dict[str, Any],
    beatmiss_rows: list[BeatMissRow],
    guidance_rows: list[GuidanceRow],
    quotes_df: pd.DataFrame,
    driver_updates_df: pd.DataFrame,
    diff_path: Path | None,
    estimate_asof: str,
    artifact_summary: str,
) -> str:
    ev = plan["event"]
    ticker = _display(ev.get("ticker"))
    period = _display(ev.get("fiscal_period"))

    est_asof = estimate_asof

    norm_dir = Path(
        plan.get("inputs", {}).get("normalized", {}).get("metrics_csv", "normalized/metrics.csv")
    ).parent
    drivers_bullets = _read_optional_lines(norm_dir / "drivers_bullets.md", 8)
    if not drivers_bullets:
        drivers_bullets = [
            "Driver bullets not provided in normalized inputs; add source-supported driver bullets for committee use."
        ]

    watch_list = _read_optional_lines(norm_dir / "watch_list.md", 5)
    if not watch_list:
        watch_list = [
            "Watch list not provided in normalized inputs; add measurable next-quarter watch items."
        ]

    # Quotes (max 8)
    quotes: list[dict[str, str]] = []
    if not quotes_df.empty:
        for _, r in quotes_df.iterrows():
            if len(quotes) >= 8:
                break
            qt = r.get("QuoteText")
            if is_missing(qt):
                continue
            quotes.append(
                {
                    "Section": _display(r.get("Section")),
                    "Speaker": _display(r.get("Speaker")),
                    "Questioner": r.get("Questioner") or "",
                    "TopicTag": _display(r.get("TopicTag")),
                    "QuoteText": qt,
                    "SourceTag": _display(r.get("SourceTag"), "source not provided"),
                }
            )

    # Model impact from driver_updates
    model_impact_lines: list[str] = []
    if not driver_updates_df.empty:
        for _, r in driver_updates_df.iterrows():
            did = _display(r.get("DriverID"))
            newv = _display(r.get("NewValue"))
            units = r.get("Units") or ""
            why = _display(r.get("Why"))
            src = _display(r.get("SourceTag"), "source not provided")
            oldv = _display(r.get("OldValue"))
            model_impact_lines.append(
                f"- {did}: {oldv} → {newv} ({units}) | Why: {why} | Source: {src}"
            )
            if len(model_impact_lines) >= 8:
                break
    else:
        model_impact_lines.append(
            "- Driver updates not provided; create a driver update packet before using this as a model-impact artifact."
        )

    diff_note = ""
    if diff_path and diff_path.exists():
        diff_note = f"\n\n**Diff:** see `{diff_path.as_posix()}`"

    lines: list[str] = []
    lines.append(f"# {ticker} — {period} Earnings Tear Sheet")
    lines.append("")
    lines.append(f"**Event:** {_display(ev.get('event_date'))} ({_display(ev.get('timezone'))})  ")
    lines.append(f"**Estimate set (as-of):** {est_asof}  ")
    lines.append(f"**Artifacts:** {artifact_summary}  ")
    lines.append(f"**Base units:** {_display(ev.get('base_currency'))}{ev.get('base_scale', '')}  ")
    lines.append("")

    lines.append("## Beat/Miss vs expectations")
    lines.append(_md_table_beatmiss(beatmiss_rows))
    lines.append("")

    lines.append("## EPS quality screen")
    lines.append(render_eps_quality_screen(beatmiss_rows))
    lines.append("")

    lines.append("## Guidance delta")
    lines.append(_md_table_guidance(guidance_rows))
    lines.append("")

    lines.append("## Drivers (5–8)")
    for b in drivers_bullets:
        if b.startswith("-"):
            lines.append(b)
        else:
            lines.append(f"- {b}")
    lines.append("")

    lines.append("## Key quotes (max 4–8)")
    if quotes:
        for q in quotes:
            qhdr = f"**[{q['TopicTag']}] {q['Speaker']} ({q['Section']})**"
            if q["Section"] == "Q&A" and q["Questioner"]:
                qhdr = f"**[{q['TopicTag']}] {q['Speaker']} (Q&A; Q: {q['Questioner']})**"
            lines.append(f"> {qhdr}: “{q['QuoteText']}”  ")
            lines.append(f"> Source: {q['SourceTag']}")
            lines.append("")
    else:
        lines.append(
            "> Quote pack not provided in normalized inputs; add high-signal quotes with speaker and SourceTag for quote mode."
        )
        lines.append("")

    lines.append("## Model impact")
    lines.append("Top driver changes applied (old → new):")
    lines += model_impact_lines
    lines.append("")
    lines.append("Key output deltas (old → new):")
    lines.append(
        "- Output deltas not computed in this run; recalc model or provide output registry to summarize top deltas."
    )
    lines.append(diff_note)
    lines.append("")

    lines.append("## Watch list (next quarter)")
    for i, w in enumerate(watch_list, start=1):
        w = w.lstrip("0123456789. ")
        lines.append(f"{i}. {w}")

    return "\n".join(lines)


def render_executive_overview(
    plan: dict[str, Any], beatmiss_rows: list[BeatMissRow], guidance_rows: list[GuidanceRow]
) -> str:
    ev = plan["event"]
    ticker = _display(ev.get("ticker"))
    period = _display(ev.get("fiscal_period"))

    # Heuristic ranking: guidance deltas first, then headline surprises.
    bullets: list[str] = []

    # Guidance bullets (top 5)
    for r in guidance_rows[:5]:
        if r.midpoint is None:
            continue
        bullets.append(
            f"Guidance ({r.metric}, {r.period}) midpoint vs consensus: {_format_number(r.delta_cons_mid, r.units)} ({r.units}); Source: {r.source_tag}"
        )

    # Beat/miss bullets (top 5)
    for r in beatmiss_rows[:5]:
        if r.reported is None:
            continue
        bullets.append(
            f"Reported {r.metric} vs consensus: {_format_number(r.delta_cons, r.units)} ({_format_pct(r.surprise_cons)}); Source: {r.source_tag}"
        )

    # Pad to 10
    while len(bullets) < 10:
        bullets.append(
            "Additional source-supported what-mattered point not provided in normalized inputs."
        )

    lines: list[str] = []
    lines.append(f"# Executive Overview — {ticker} {period}")
    lines.append("")
    lines.append("## What matters (ranked)")
    for i, b in enumerate(bullets[:15], start=1):
        lines.append(f"{i}. {b}")
    lines.append("")
    lines.append("## Stock move frame (vs expectations)")
    lines.append(
        "Stock move frame not provided in normalized inputs; frame the move against the estimate set before committee use."
    )
    lines.append("")
    lines.append("## EPS quality screen")
    lines.append(render_eps_quality_screen(beatmiss_rows))
    lines.append("")
    lines.append("## Bull / Base / Bear narrative delta")
    lines.append("Bull/base/bear narrative delta not provided in normalized inputs.")
    return "\n".join(lines)


def render_deep_dive(
    plan: dict[str, Any],
    beatmiss_rows: list[BeatMissRow],
    guidance_rows: list[GuidanceRow],
    quotes_df: pd.DataFrame,
) -> str:
    ev = plan["event"]
    ticker = _display(ev.get("ticker"))
    period = _display(ev.get("fiscal_period"))

    lines: list[str] = []
    lines.append(f"# Earnings Deep Dive — {ticker} {period}")
    lines.append("")
    lines.append("## 1. Headline results vs expectations")
    lines.append(_md_table_beatmiss(beatmiss_rows))
    lines.append("")
    lines.append("## 2. EPS quality screen")
    lines.append(render_eps_quality_screen(beatmiss_rows))
    lines.append("")
    lines.append("## 3. Guidance and outlook")
    lines.append(_md_table_guidance(guidance_rows))
    lines.append("")
    lines.append("## 4. Results drivers (write-up)")
    lines.append(
        "Results-driver narrative not provided in normalized inputs; add source-tagged driver decomposition before using as a full deep dive."
    )
    lines.append("")
    lines.append("## 5. Transcript themes + Q&A (high signal)")
    if not quotes_df.empty:
        for _, r in quotes_df.head(12).iterrows():
            qt = r.get("QuoteText")
            if is_missing(qt):
                continue
            lines.append(
                f"- [{_display(r.get('TopicTag'))}] {_display(r.get('Speaker'))} ({_display(r.get('Section'))}): “{qt}” (Source: {_display(r.get('SourceTag'), 'source not provided')})"
            )
    else:
        lines.append("Quote themes not provided in normalized inputs.")
    lines.append("")
    lines.append("## 6. Model changes")
    lines.append(
        "Model-change narrative not provided in normalized inputs; map surprises and guidance into driver updates before using as a model-update artifact."
    )
    return "\n".join(lines)


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python scripts/run_plan.py plan.json")
        return 1

    plan_path = sys.argv[1]
    plan = read_json(plan_path)

    # Plan validation (structure)
    v = validate_plan(plan)
    if v["errors"]:
        for e in v["errors"]:
            print(f"ERROR: {e}")
        return 1

    out_dir = Path(plan.get("outputs", {}).get("output_dir", "output"))
    ensure_dir(str(out_dir))
    ensure_dir(str(out_dir / "audit"))
    ensure_dir(str(out_dir / "model"))

    # Validate normalized inputs (structural + SourceTag hygiene)
    val_script = Path(__file__).resolve().parent / "validate_normalized_inputs.py"
    proc = subprocess.run([sys.executable, str(val_script), plan_path])
    if proc.returncode != 0:
        return proc.returncode

    # Read normalized tables
    norm = plan.get("inputs", {}).get("normalized", {})
    metrics_df = _read_csv(norm["metrics_csv"])
    estimates_df = _read_csv(norm["estimates_csv"])
    guidance_df = _read_csv(norm["guidance_csv"])
    quotes_df = _read_csv(norm["quotes_csv"])
    driver_updates_df = _read_csv(norm["driver_updates_csv"])

    # Estimate set AsOf (best-effort)
    estimate_asof = "not provided"
    if "AsOf" in estimates_df.columns:
        vals = [
            v
            for v in estimates_df["AsOf"].tolist()
            if str(v).strip() and str(v).strip().upper() != "MISSING"
        ]
        if vals:
            estimate_asof = str(vals[0]).strip()

    # Artifact summary (for tear sheet header)
    artifacts = plan.get("inputs", {}).get("artifacts", {})
    parts = []
    if isinstance(artifacts, dict):
        for k, v in artifacts.items():
            if isinstance(v, str) and v.strip().upper() != "MISSING":
                parts.append(f"{k}={Path(v).name}")
    artifact_summary = ", ".join(parts) if parts else "not provided"

    beatmiss_rows = compute_beat_miss(metrics_df, estimates_df)
    guidance_rows = compute_guidance(guidance_df, estimates_df)

    # Optional model update
    diff_path: Path | None = None
    if plan.get("outputs", {}).get("model_update", {}).get("enabled"):
        mode = plan.get("outputs", {}).get("model_update", {}).get("mode", "apply")
        if mode == "apply":
            try:
                try:
                    from .apply_model_updates import apply_model_updates
                except ImportError:
                    from apply_model_updates import apply_model_updates

                updated_model_path, changelog_path = apply_model_updates(plan)
                if plan.get("outputs", {}).get("model_update", {}).get("write_diff"):
                    try:
                        try:
                            from .model_diff import write_diff
                        except ImportError:
                            from model_diff import write_diff

                        diff_path = out_dir / "audit" / "WhatChanged_Diff.csv"
                        write_diff(plan, diff_path, updated_model_path)
                    except Exception as e:
                        print(f"WARN: diff generation failed: {e}")
            except Exception as e:
                print(f"WARN: model update failed: {e}")
        else:
            # packet mode
            packet_path = out_dir / "audit" / "ModelUpdatePacket.csv"
            driver_updates_df.to_csv(packet_path, index=False)

    # Render markdown outputs
    tearsheet_md = render_tearsheet(
        plan,
        beatmiss_rows,
        guidance_rows,
        quotes_df,
        driver_updates_df,
        diff_path,
        estimate_asof,
        artifact_summary,
    )
    exec_md = render_executive_overview(plan, beatmiss_rows, guidance_rows)
    deep_md = render_deep_dive(plan, beatmiss_rows, guidance_rows, quotes_df)

    write_text(exec_md, str(out_dir / "ExecutiveOverview.md"))
    write_text(tearsheet_md, str(out_dir / "TearSheet.md"))
    write_text(deep_md, str(out_dir / "DeepDive.md"))

    output_errors = unresolved_placeholder_errors(
        {
            "ExecutiveOverview.md": exec_md,
            "TearSheet.md": tearsheet_md,
            "DeepDive.md": deep_md,
        }
    )
    if output_errors:
        qa_path = out_dir / "audit" / "PlaceholderQA.md"
        write_text(
            "# Placeholder QA\n\n" + "\n".join(f"- {e}" for e in output_errors) + "\n", str(qa_path)
        )
        for e in output_errors:
            print(f"ERROR: {e}")
        return 1

    print(f"Wrote outputs to: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
