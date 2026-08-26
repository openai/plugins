#!/usr/bin/env python3
"""
First-pass deck/report QC extractor for Public Equity Investing deliverables.

Supported inputs: .pptx, .docx, .xlsx, .xlsm, .csv, .txt, .md
Outputs: public_equity_investing_deck_qc_report.html plus support CSV/JSON/support-note artifacts

This script is intentionally conservative. It identifies leads for review; it does
not replace visual review, model tie-out, or source-of-truth analysis. After that
review is completed, use --finalize to reconcile the final HTML and manifest.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

SCRIPT_DIR = Path(__file__).resolve().parent
PLUGIN_ROOT = Path(__file__).resolve().parents[3]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from qc_analysis import analyze_segments, posture_from_issues

from shared.artifact_packager import (  # noqa: E402
    artifact_item,
    logs_dir,
    support_dir,
    write_artifact_manifest,
    write_dashboard_contract,
    write_report_html,
)

TEXT_EXTS = {".txt", ".md", ".markdown"}
ZIP_EXTS = {".pptx", ".docx", ".xlsx", ".xlsm"}

COMMON_METRICS = [
    "revenue",
    "sales",
    "arr",
    "nrr",
    "gross margin",
    "ebitda margin",
    "ebitda",
    "adjusted ebitda",
    "street ebitda",
    "internal-case ebitda",
    "ebit",
    "eps",
    "free cash flow",
    "fcf",
    "capex",
    "working capital",
    "nwc",
    "cash",
    "debt",
    "net debt",
    "enterprise value",
    "equity value",
    "market cap",
    "share price",
    "ev",
    "valuation",
    "multiple",
    "ev/ebitda",
    "p/e",
    "irr",
    "moic",
    "npv",
    "nav",
    "ltv",
    "dscr",
    "debt yield",
    "leverage",
    "net leverage",
    "gross leverage",
    "liquidity",
    "refinancing",
    "rating",
    "credit spread signal",
    "rate",
    "inflation",
    "cagr",
    "growth",
    "margin",
    "bps",
    "price target",
    "wacc",
    "terminal growth",
    "terminal value",
    "multiple",
]
COMMON_METRICS.sort(key=len, reverse=True)

PERIOD_RE = re.compile(
    r"\b(fy\s?\d{2,4}e?|cy\s?\d{2,4}e?|20\d{2}e?|19\d{2}|q[1-4]\s?['`]?\d{2}|q[1-4]\s?20\d{2}|ltm|ntm|ytd|run[- ]rate|base case|downside|upside|management case|company guidance|street case|consensus case|credit handoff case|event case|internal case)\b",
    re.I,
)
NUMBER_RE = re.compile(
    r"(?<![A-Za-z0-9])(?P<full>(?P<prefix>[$€£])?\s*\(?-?\d+(?:,\d{3})*(?:\.\d+)?\)?\s*(?P<suffix>%|bps?|x|turns?|mm|m|bn|b|k|thousand|million|billion)?)",
    re.I,
)

REPORT_FILENAME = "public_equity_investing_deck_qc_report.html"
CONTRACT_FILENAME = "deck_report_qc_dashboard_contract.json"


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def safe_text(parts: Iterable[str]) -> str:
    text = " ".join(p.strip() for p in parts if p and p.strip())
    text = re.sub(r"\s+", " ", text).strip()
    return text


def xml_text(xml_bytes: bytes) -> str:
    try:
        root = ET.fromstring(xml_bytes)
    except Exception:
        return ""
    vals = []
    for elem in root.iter():
        if local_name(elem.tag) in {"t", "v"} and elem.text:
            vals.append(elem.text)
    return safe_text(vals)


def paragraphs_from_xml(xml_bytes: bytes) -> list[str]:
    try:
        root = ET.fromstring(xml_bytes)
    except Exception:
        return []
    paras: list[str] = []
    for elem in root.iter():
        if local_name(elem.tag) == "p":
            vals = []
            for child in elem.iter():
                if local_name(child.tag) == "t" and child.text:
                    vals.append(child.text)
            txt = safe_text(vals)
            if txt:
                paras.append(txt)
    return paras


def numeric_sort_key(name: str) -> tuple[int, str]:
    nums = re.findall(r"\d+", name)
    return (int(nums[-1]) if nums else 0, name)


def extract_pptx(path: Path) -> list[dict[str, str]]:
    segments: list[dict[str, str]] = []
    with zipfile.ZipFile(path) as zf:
        slide_names = sorted(
            [n for n in zf.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)],
            key=numeric_sort_key,
        )
        for idx, name in enumerate(slide_names, 1):
            text = xml_text(zf.read(name))
            title = text.split(". ", 1)[0][:120] if text else ""
            segments.append(
                {
                    "source_file": str(path),
                    "file_type": "pptx",
                    "location_type": "slide",
                    "location": f"Slide {idx}",
                    "title": title,
                    "text": text,
                }
            )
        note_names = sorted(
            [n for n in zf.namelist() if re.match(r"ppt/notesSlides/notesSlide\d+\.xml$", n)],
            key=numeric_sort_key,
        )
        for idx, name in enumerate(note_names, 1):
            text = xml_text(zf.read(name))
            if text:
                segments.append(
                    {
                        "source_file": str(path),
                        "file_type": "pptx",
                        "location_type": "notes",
                        "location": f"Notes {idx}",
                        "title": "speaker notes",
                        "text": text,
                    }
                )
        chart_names = sorted(
            [n for n in zf.namelist() if re.match(r"ppt/charts/chart\d+\.xml$", n)],
            key=numeric_sort_key,
        )
        for idx, name in enumerate(chart_names, 1):
            text = xml_text(zf.read(name))
            if text:
                segments.append(
                    {
                        "source_file": str(path),
                        "file_type": "pptx",
                        "location_type": "chart_xml",
                        "location": f"Chart {idx}",
                        "title": "embedded chart data",
                        "text": text,
                    }
                )
    return segments


def extract_docx(path: Path) -> list[dict[str, str]]:
    segments: list[dict[str, str]] = []
    with zipfile.ZipFile(path) as zf:
        for name, label in [
            ("word/document.xml", "paragraph"),
            ("word/footnotes.xml", "footnote"),
            ("word/endnotes.xml", "endnote"),
            ("word/comments.xml", "comment"),
        ]:
            if name not in zf.namelist():
                continue
            paras = paragraphs_from_xml(zf.read(name))
            for idx, para in enumerate(paras, 1):
                segments.append(
                    {
                        "source_file": str(path),
                        "file_type": "docx",
                        "location_type": label,
                        "location": f"{label.title()} {idx}",
                        "title": para[:100],
                        "text": para,
                    }
                )
    return segments


def read_shared_strings(zf: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in zf.namelist():
        return []
    try:
        root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
    except Exception:
        return []
    strings = []
    for si in root.iter():
        if local_name(si.tag) == "si":
            vals = []
            for child in si.iter():
                if local_name(child.tag) == "t" and child.text:
                    vals.append(child.text)
            strings.append("".join(vals))
    return strings


def extract_xlsx(path: Path) -> list[dict[str, str]]:
    segments: list[dict[str, str]] = []
    with zipfile.ZipFile(path) as zf:
        shared = read_shared_strings(zf)
        sheet_names = sorted(
            [n for n in zf.namelist() if re.match(r"xl/worksheets/sheet\d+\.xml$", n)],
            key=numeric_sort_key,
        )
        for idx, name in enumerate(sheet_names, 1):
            try:
                root = ET.fromstring(zf.read(name))
            except Exception:
                continue
            rows = []
            for row in root.iter():
                if local_name(row.tag) != "row":
                    continue
                vals = []
                for c in row:
                    if local_name(c.tag) != "c":
                        continue
                    ref = c.attrib.get("r", "")
                    ctype = c.attrib.get("t")
                    val_text = ""
                    formula = ""
                    for child in c:
                        lname = local_name(child.tag)
                        if lname == "f" and child.text:
                            formula = "=" + child.text
                        elif lname == "v" and child.text:
                            raw = child.text
                            if ctype == "s":
                                try:
                                    val_text = shared[int(raw)]
                                except Exception:
                                    val_text = raw
                            else:
                                val_text = raw
                        elif lname == "is":
                            val_text = safe_text(
                                [
                                    t.text
                                    for t in child.iter()
                                    if local_name(t.tag) == "t" and t.text
                                ]
                            )
                    if formula:
                        vals.append(f"{ref}:{formula}")
                    elif val_text:
                        vals.append(f"{ref}:{val_text}")
                if vals:
                    rows.append(" | ".join(vals))
            if rows:
                text = "\n".join(rows)
                segments.append(
                    {
                        "source_file": str(path),
                        "file_type": "xlsx",
                        "location_type": "sheet",
                        "location": f"Sheet {idx}",
                        "title": f"Sheet {idx}",
                        "text": text[:200000],
                    }
                )
    return segments


def extract_csv(path: Path) -> list[dict[str, str]]:
    raw = path.read_text(errors="replace")
    lines = raw.splitlines()
    segments = []
    block_size = 50
    for start in range(0, len(lines), block_size):
        block = lines[start : start + block_size]
        if not block:
            continue
        segments.append(
            {
                "source_file": str(path),
                "file_type": "csv",
                "location_type": "row_block",
                "location": f"Rows {start + 1}-{start + len(block)}",
                "title": block[0][:100] if block else "",
                "text": "\n".join(block),
            }
        )
    return segments


def extract_text_file(path: Path) -> list[dict[str, str]]:
    raw = path.read_text(errors="replace")
    lines = raw.splitlines()
    segments = []
    block_size = 40
    for start in range(0, len(lines), block_size):
        block = lines[start : start + block_size]
        if not block:
            continue
        segments.append(
            {
                "source_file": str(path),
                "file_type": path.suffix.lower().lstrip("."),
                "location_type": "line_block",
                "location": f"Lines {start + 1}-{start + len(block)}",
                "title": block[0][:100] if block else "",
                "text": "\n".join(block),
            }
        )
    return segments


def extract_file(path: Path) -> list[dict[str, str]]:
    ext = path.suffix.lower()
    if ext == ".pptx":
        return extract_pptx(path)
    if ext == ".docx":
        return extract_docx(path)
    if ext in {".xlsx", ".xlsm"}:
        return extract_xlsx(path)
    if ext == ".csv":
        return extract_csv(path)
    if ext in TEXT_EXTS:
        return extract_text_file(path)
    return [
        {
            "source_file": str(path),
            "file_type": ext.lstrip("."),
            "location_type": "unsupported",
            "location": "File",
            "title": "unsupported file type",
            "text": "",
        }
    ]


def normalize_number(raw: str) -> tuple[float | None, str]:
    s = raw.strip().replace(" ", "")
    prefix = "currency" if any(sym in s for sym in "$€£") else ""
    suffix_match = re.search(r"(%|bps?|x|turns?|mm|m|bn|b|k|thousand|million|billion)$", s, re.I)
    suffix = suffix_match.group(1).lower() if suffix_match else ""
    neg = s.startswith("-") or ("(" in s and ")" in s)
    num_s = re.sub(r"[^0-9.\-]", "", s)
    try:
        val = float(num_s)
    except Exception:
        return None, "unknown"
    if neg and val > 0:
        val *= -1
    unit_class = "number"
    multiplier = 1.0
    if suffix == "%":
        unit_class = "percent"
    elif suffix in {"bp", "bps"}:
        unit_class = "bps"
    elif suffix in {"x", "turn", "turns"}:
        unit_class = "multiple"
    elif suffix in {"k", "thousand"}:
        unit_class = "currency_or_count"
        multiplier = 1_000.0
    elif suffix in {"m", "mm", "million"}:
        unit_class = "currency_or_count"
        multiplier = 1_000_000.0
    elif suffix in {"b", "bn", "billion"}:
        unit_class = "currency_or_count"
        multiplier = 1_000_000_000.0
    elif prefix:
        unit_class = "currency"
    return val * multiplier, unit_class


def metric_key(context: str) -> str:
    c = context.lower()
    marker = c.find("__num__")
    if marker < 0:
        marker = len(c) // 2

    metric = ""
    best_dist = 10**9
    for m in COMMON_METRICS:
        for hit in re.finditer(r"\b" + re.escape(m) + r"\b", c):
            dist = min(abs(hit.start() - marker), abs(hit.end() - marker))
            if dist < best_dist:
                best_dist = dist
                metric = m

    period = ""
    best_period_dist = 10**9
    for hit in PERIOD_RE.finditer(context):
        dist = min(abs(hit.start() - marker), abs(hit.end() - marker))
        if dist < best_period_dist:
            best_period_dist = dist
            period = hit.group(0).lower().replace(" ", "")

    if metric:
        return "|".join([p for p in [metric, period] if p])
    # Fallback to words immediately before the number.
    before = re.sub(r"[^A-Za-z0-9%/ -]", " ", context[: max(context.find("__NUM__"), 0)])
    words = [w.lower() for w in before.split()[-5:] if len(w) > 2]
    return " ".join(words[-4:]) if words else "unknown"


def extract_numbers(segments: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for seg in segments:
        text = seg.get("text", "") or ""
        for match in NUMBER_RE.finditer(text):
            raw = match.group("full").strip()
            start, end = match.span()
            # Skip numbers that are clearly components of common date strings such as 1/15/2026 or 2026-01-15.
            if (start > 0 and text[start - 1] in "/-") or (
                end < len(text) and text[end : end + 1] in "/-"
            ):
                continue
            # Skip obvious year-only cases unless context suggests a metric.
            val, unit_class = normalize_number(raw)
            if val is None:
                continue
            context = text[max(0, start - 100) : min(len(text), end + 100)].replace("\n", " ")
            marked_context = (
                context[: start - max(0, start - 100)]
                + "__NUM__"
                + context[start - max(0, start - 100) :]
            )
            key = metric_key(marked_context)
            if (
                unit_class == "number"
                and 1900 <= abs(val) <= 2100
                and not re.search(
                    r"\b(fy|cy|q[1-4]|year|revenue|ebitda|margin|growth|debt|valuation|source|as of)\b",
                    context,
                    re.I,
                )
            ):
                continue
            rows.append(
                {
                    "source_file": seg["source_file"],
                    "file_type": seg["file_type"],
                    "location": seg["location"],
                    "location_type": seg["location_type"],
                    "metric_key": key,
                    "raw_value": raw,
                    "normalized_value": f"{val:.8g}",
                    "unit_class": unit_class,
                    "context": re.sub(r"\s+", " ", context).strip(),
                }
            )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_report_text(
    input_files: list[Path],
    segments: list[dict[str, str]],
    numbers: list[dict[str, str]],
    issues: list[dict[str, str]],
) -> str:
    severity_rank = {"critical": 0, "high": 1, "medium": 2, "needs_review": 3, "low": 4}
    top = sorted(issues, key=lambda i: severity_rank.get(i["severity"], 99))[:20]
    lines = []
    lines.append("# First-pass Deck / Report QC Scan")
    lines.append("")
    lines.append(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    lines.append(f"Input files: {', '.join(str(p) for p in input_files)}")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- Segments extracted: {len(segments)}")
    lines.append(f"- Numerical mentions detected: {len(numbers)}")
    lines.append(f"- Potential issues flagged: {len(issues)}")
    lines.append(f"- First-pass scan posture: {posture_from_issues(issues)}")
    lines.append("")
    lines.append(
        "This scan is a first pass. It is not a final external-circulation certification. Confirm chart, formatting, source, and model issues through visual review and source/model tie-out."
    )
    lines.append("")
    lines.append("## Top flagged issues")
    if not top:
        lines.append(
            "No heuristic issues flagged. Still perform visual review and source/model tie-out before circulation."
        )
    else:
        lines.append("| ID | Severity | Type | Location | Finding | Suggested fix |")
        lines.append("|---|---|---|---|---|---|")
        for i in top:
            lines.append(
                f"| {i['issue_id']} | {i['severity']} | {i['issue_type']} | {i['location']} | {i['finding']} | {i['suggested_fix']} |"
            )
    lines.append("")
    lines.append("## Files generated")
    lines.append("- segments.csv")
    lines.append("- numbers.csv")
    lines.append("- issues.csv")
    lines.append("- scan.json")
    return "\n".join(lines)


def load_review_record(path: Path) -> dict[str, object]:
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing review record: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid review record JSON: {path}: {exc}") from exc
    if not isinstance(record, dict):
        raise ValueError("review record must be a JSON object")
    for key in ("completed_reviews", "missing_inputs"):
        values = record.get(key, [])
        if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
            raise ValueError(f"review record field {key!r} must be a list of strings")
    return record


def finalized_support_artifacts(
    scan_dir: Path, review_record_path: Path, contract_path: Path | None
) -> list[dict[str, object]]:
    candidates = [
        (
            scan_dir / "support" / "segments.csv",
            "csv",
            "Extracted text segment inventory.",
            True,
            "CSV is extraction support.",
        ),
        (
            scan_dir / "support" / "numbers.csv",
            "csv",
            "Extracted number inventory.",
            True,
            "CSV supports number tie-out.",
        ),
        (
            scan_dir / "support" / "qc_issue_log.csv",
            "csv",
            "Raw first-pass QC issue leads.",
            True,
            "CSV is first-pass issue extraction support.",
        ),
        (
            scan_dir / "support" / "repeated_number_tieout.csv",
            "csv",
            "Repeated metric tie-out leads.",
            True,
            "CSV supports model/source reconciliation.",
        ),
        (
            scan_dir / "support" / "source_coverage.csv",
            "csv",
            "Source coverage issue leads.",
            True,
            "CSV supports source review.",
        ),
        (
            scan_dir / "support" / "chart_narrative_tieout.csv",
            "csv",
            "Chart and narrative tie-out leads.",
            True,
            "CSV supports visual/narrative review.",
        ),
        (
            scan_dir / "support" / "qc_support_note.md",
            "markdown",
            "First-pass extraction support note.",
            True,
            "Markdown is extraction support, not the final QC report.",
        ),
        (
            scan_dir / "logs" / "scan.json",
            "json",
            "Machine-readable extraction scan.",
            True,
            "JSON is internal extraction support.",
        ),
        (
            review_record_path,
            "json",
            "Completed-review and remaining-verification record.",
            False,
            "Review record reconciles final artifact status and open verification items.",
        ),
    ]
    if contract_path is not None:
        candidates.append(
            (
                contract_path,
                "json",
                "Explicit standardized-dashboard contract.",
                False,
                "Contract JSON is renderer plumbing for the requested dashboard route.",
            )
        )
    return [
        artifact_item(path, "support_artifact", kind, description, False, analysis, reason)
        for path, kind, description, analysis, reason in candidates
        if path.exists()
    ]


def update_dashboard_contract(
    contract_path: Path, primary_report: Path, status: dict[str, object]
) -> None:
    if not contract_path.exists():
        return
    try:
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return
    if not isinstance(contract, dict):
        return
    deliverable = contract.get("deliverable")
    if isinstance(deliverable, dict):
        deliverable["primary_artifact"] = str(primary_report)
        actions = deliverable.get("hero_actions", [])
        if isinstance(actions, list):
            for action in actions:
                if isinstance(action, dict) and action.get("label") == "Open QC report":
                    action["path"] = str(primary_report)
    hero = contract.get("hero")
    if isinstance(hero, dict):
        hero["callout"] = str(primary_report)
    contract["blocked_output_context"] = {
        "blocked": status.get("status") == "blocked",
        "reason": status.get("reason", ""),
        "completed_reviews": status.get("completed_reviews", []),
        "missing_inputs": status.get("missing_inputs", []),
    }
    contract_path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")


def finalize_review(args: argparse.Namespace) -> int:
    if not args.primary_report or not args.review_record:
        print(
            "error: --finalize requires --primary-report and --review-record",
            file=sys.stderr,
        )
        return 2
    outdir = Path(args.outdir).resolve()
    scan_dir = Path(args.scan_dir or args.outdir).resolve()
    primary_report = Path(args.primary_report).resolve()
    review_record_path = Path(args.review_record).resolve()
    if not primary_report.exists():
        print(f"error: missing primary report: {primary_report}", file=sys.stderr)
        return 2
    if primary_report.suffix.lower() not in {".html", ".htm"}:
        print("error: finalized primary report must be HTML", file=sys.stderr)
        return 2
    try:
        record = load_review_record(review_record_path)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    completed_reviews = list(record.get("completed_reviews", []))
    missing_inputs = list(record.get("missing_inputs", []))
    status = str(record.get("status") or ("partial" if missing_inputs else "complete"))
    reason = str(
        record.get("reason")
        or (
            "Internal QC review completed; external/source confirmation remains open."
            if missing_inputs
            else "QC review steps recorded as complete."
        )
    )
    final_status: dict[str, object] = {
        "status": status,
        "reason": reason,
        "completed_reviews": completed_reviews,
        "missing_inputs": missing_inputs,
    }

    contract_path = scan_dir / "logs" / CONTRACT_FILENAME
    retained_contract: Path | None = None
    if args.keep_dashboard_contract:
        update_dashboard_contract(contract_path, primary_report, final_status)
        retained_contract = contract_path if contract_path.exists() else None
    else:
        contract_path.unlink(missing_ok=True)

    provisional_report = scan_dir / REPORT_FILENAME
    if provisional_report != primary_report:
        provisional_report.unlink(missing_ok=True)
    provisional_manifest = scan_dir / "manifest.json"
    if provisional_manifest != outdir / "manifest.json":
        provisional_manifest.unlink(missing_ok=True)

    write_artifact_manifest(
        outdir,
        "deck-report-qc",
        "html_report",
        primary_report,
        support_artifacts=finalized_support_artifacts(
            scan_dir, review_record_path, retained_contract
        ),
        blocked_or_partial_status=final_status,
        extra={"review_completion_record": str(review_record_path)},
    )
    print(f"finalized QC review manifest at {outdir / 'manifest.json'}")
    print(f"primary_report={primary_report} status={status}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="First-pass QC extractor for Public Equity Investing decks and reports"
    )
    parser.add_argument(
        "files", nargs="*", help="input files: pptx, docx, xlsx, xlsm, csv, txt, md"
    )
    parser.add_argument("--outdir", default="qc_out", help="output directory")
    parser.add_argument(
        "--finalize",
        action="store_true",
        help="finalize a completed substantive review around its polished HTML report",
    )
    parser.add_argument(
        "--scan-dir",
        help="directory containing first-pass extraction support; defaults to --outdir",
    )
    parser.add_argument("--primary-report", help="final polished HTML report for --finalize")
    parser.add_argument("--review-record", help="JSON completion record for --finalize")
    parser.add_argument(
        "--keep-dashboard-contract",
        action="store_true",
        help="retain/update the dashboard contract only for an explicitly selected dashboard route",
    )
    args = parser.parse_args(argv)

    if args.finalize:
        return finalize_review(args)
    if not args.files:
        parser.error("at least one input file is required unless --finalize is used")

    input_files = [Path(f).resolve() for f in args.files]
    outdir = Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    segments: list[dict[str, str]] = []
    for path in input_files:
        if not path.exists():
            print(f"error: missing file: {path}", file=sys.stderr)
            return 2
        if path.suffix.lower() in ZIP_EXTS and not zipfile.is_zipfile(path):
            print(
                f"warning: {path} does not look like a valid zip-based Office file",
                file=sys.stderr,
            )
        try:
            segments.extend(extract_file(path))
        except Exception as exc:
            segments.append(
                {
                    "source_file": str(path),
                    "file_type": path.suffix.lower().lstrip("."),
                    "location_type": "error",
                    "location": "File",
                    "title": "extraction error",
                    "text": f"extraction failed: {exc}",
                }
            )

    numbers = extract_numbers(segments)
    issues = analyze_segments(segments, numbers)

    csv_dir = support_dir(outdir)
    log_dir = logs_dir(outdir)
    write_csv(
        csv_dir / "segments.csv",
        segments,
        ["source_file", "file_type", "location_type", "location", "title", "text"],
    )
    write_csv(
        csv_dir / "numbers.csv",
        numbers,
        [
            "source_file",
            "file_type",
            "location",
            "location_type",
            "metric_key",
            "raw_value",
            "normalized_value",
            "unit_class",
            "context",
        ],
    )
    issue_fields = [
        "issue_id",
        "severity",
        "issue_type",
        "confidence",
        "source_file",
        "location",
        "metric_or_claim",
        "finding",
        "evidence",
        "why_it_matters",
        "suggested_fix",
        "owner_route",
        "status",
    ]
    write_csv(csv_dir / "qc_issue_log.csv", issues, issue_fields)
    repeated_number_rows = [
        issue for issue in issues if issue.get("issue_type") == "number_mismatch"
    ]
    source_coverage_rows = [issue for issue in issues if issue.get("issue_type") == "source_gap"]
    chart_narrative_rows = [
        issue
        for issue in issues
        if issue.get("issue_type")
        in {"narrative_contradiction", "chart_tieout", "unit_or_period_ambiguity"}
    ]
    summary_fields = [
        "issue_id",
        "severity",
        "source_file",
        "location",
        "metric_or_claim",
        "finding",
        "evidence",
        "suggested_fix",
        "status",
    ]
    write_csv(csv_dir / "repeated_number_tieout.csv", repeated_number_rows, summary_fields)
    write_csv(csv_dir / "source_coverage.csv", source_coverage_rows, summary_fields)
    write_csv(csv_dir / "chart_narrative_tieout.csv", chart_narrative_rows, summary_fields)
    (log_dir / "scan.json").write_text(
        json.dumps({"segments": segments, "numbers": numbers, "issues": issues}, indent=2),
        encoding="utf-8",
    )
    report_text = write_report_text(input_files, segments, numbers, issues)
    support_note_path = csv_dir / "qc_support_note.md"
    support_note_path.write_text(report_text, encoding="utf-8")
    report_path = write_report_html(
        outdir / REPORT_FILENAME,
        "Public Equity Investing Deck / Report QC",
        report_text,
    )
    contract_path = log_dir / CONTRACT_FILENAME
    write_dashboard_contract(
        contract_path,
        "deck-report-qc",
        "Public Equity Investing Deck / Report QC",
        "Public Equity Investing deliverable",
        "report_only",
        report_path,
        executive_summary="First-pass QC report with issue severity, repeated-number tie-out, source coverage, and chart/narrative review leads.",
        hero_actions=[
            {"label": "Open QC report", "path": str(report_path)},
            {"label": "Review issue log", "path": str(csv_dir / "qc_issue_log.csv")},
        ],
        supporting_outputs=[
            {"path": str(csv_dir / "qc_issue_log.csv"), "label": "QC issue log", "role": "support"}
        ],
        report_body=[{"heading": "QC Summary", "body": report_text}],
        readiness_posture=posture_from_issues(issues),
        blocked_output_context={
            "blocked": False,
            "reason": "Text extraction is first-pass and does not replace visual, model, or source review.",
            "missing_inputs": [
                "Visual page review",
                "Model tie-out",
                "Source-of-truth confirmation",
            ],
        },
    )
    write_artifact_manifest(
        outdir,
        "deck-report-qc",
        "html_report",
        report_path,
        support_artifacts=[
            artifact_item(
                csv_dir / "segments.csv",
                "support_artifact",
                "csv",
                "Extracted text segment inventory.",
                False,
                True,
                "CSV is extraction support.",
            ),
            artifact_item(
                csv_dir / "numbers.csv",
                "support_artifact",
                "csv",
                "Extracted number inventory.",
                False,
                True,
                "CSV supports number tie-out.",
            ),
            artifact_item(
                csv_dir / "qc_issue_log.csv",
                "support_artifact",
                "csv",
                "Raw QC issue log.",
                False,
                True,
                "CSV backs the HTML QC report.",
            ),
            artifact_item(
                csv_dir / "repeated_number_tieout.csv",
                "support_artifact",
                "csv",
                "Repeated metric tie-out leads.",
                False,
                True,
                "CSV supports model/source reconciliation.",
            ),
            artifact_item(
                csv_dir / "source_coverage.csv",
                "support_artifact",
                "csv",
                "Source coverage issue leads.",
                False,
                True,
                "CSV supports source review.",
            ),
            artifact_item(
                csv_dir / "chart_narrative_tieout.csv",
                "support_artifact",
                "csv",
                "Chart and narrative tie-out leads.",
                False,
                True,
                "CSV supports visual/narrative review.",
            ),
            artifact_item(
                support_note_path,
                "support_artifact",
                "markdown",
                "Narrative support note backing the HTML report.",
                False,
                True,
                "Markdown is support material, not the lead artifact.",
            ),
            artifact_item(
                log_dir / "scan.json",
                "support_artifact",
                "json",
                "Machine-readable extraction scan.",
                False,
                True,
                "JSON is internal extraction support.",
            ),
            artifact_item(
                contract_path,
                "support_artifact",
                "json",
                "Dashboard/report contract.",
                False,
                False,
                "Contract JSON is renderer plumbing.",
            ),
        ],
        blocked_or_partial_status={
            "status": "partial",
            "reason": "First-pass extraction does not replace visual, model, or source review.",
            "missing_inputs": [
                "Visual page review",
                "Model tie-out",
                "Source-of-truth confirmation",
            ],
        },
    )

    print(f"wrote QC scan to {outdir}")
    print(
        f"segments={len(segments)} numbers={len(numbers)} issues={len(issues)} posture={posture_from_issues(issues)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
