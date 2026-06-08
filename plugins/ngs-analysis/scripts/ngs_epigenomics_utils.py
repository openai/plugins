#!/usr/bin/env python3
"""Shared epigenomics artifact parsers and browser-track helpers."""

from __future__ import annotations

import csv
import html
import statistics
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from ngs_planner_utils import write_tsv
from ngs_run_utils import write_json, write_text

EPIGENOMICS_SUMMARY_FIELDS = [
    "sample",
    "layout",
    "is_control",
    "control_sample",
    "status",
    "filtered_bam",
    "filtered_bam_exists",
    "total_filtered_reads",
    "mapped_reads",
    "duplicate_reads",
    "frip_reads",
    "frip",
    "raw_peak_count",
    "blacklist_filtered_peak_count",
    "consensus_peak_count",
    "insert_size_count",
    "insert_size_median",
    "insert_size_mean",
    "nucleosome_free_fraction",
    "bigwig",
    "bigwig_exists",
    "tss_matrix_exists",
    "tss_profile_exists",
    "tss_heatmap_exists",
    "motif_summary_exists",
    "notes",
]


def parse_first_int(value: str) -> int | None:
    try:
        return int(str(value).strip().split()[0])
    except (ValueError, IndexError):
        return None


def parse_flagstat(path: Path) -> dict[str, int | None]:
    metrics: dict[str, int | None] = {
        "total_reads": None,
        "mapped_reads": None,
        "duplicate_reads": None,
    }
    if not path.exists():
        return metrics
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if " in total " in line:
            metrics["total_reads"] = parse_first_int(line)
        elif " mapped (" in line and " mate mapped" not in line:
            metrics["mapped_reads"] = parse_first_int(line)
        elif " duplicates" in line:
            metrics["duplicate_reads"] = parse_first_int(line)
    return metrics


def read_int(path: Path) -> int | None:
    if not path.exists():
        return None
    try:
        return int(float(path.read_text(encoding="utf-8", errors="replace").strip().split()[0]))
    except (ValueError, IndexError):
        return None


def count_bed_rows(path: Path) -> int | None:
    if not path.exists():
        return None
    count = 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line and not line.startswith("#"):
            count += 1
    return count


def parse_insert_sizes(path: Path) -> dict[str, float | int | None]:
    metrics: dict[str, float | int | None] = {
        "insert_size_count": None,
        "insert_size_median": None,
        "insert_size_mean": None,
        "nucleosome_free_fraction": None,
    }
    if not path.exists():
        return metrics
    values: list[float] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            value = abs(float(line.strip()))
        except ValueError:
            continue
        if value > 0:
            values.append(value)
    if not values:
        return metrics
    metrics["insert_size_count"] = len(values)
    metrics["insert_size_median"] = round(float(statistics.median(values)), 3)
    metrics["insert_size_mean"] = round(float(sum(values) / len(values)), 3)
    metrics["nucleosome_free_fraction"] = round(
        sum(1 for value in values if value < 100) / len(values), 4
    )
    return metrics


def _rel(path: Path, run_dir: Path) -> str:
    try:
        return str(path.relative_to(run_dir))
    except ValueError:
        return str(path)


def _to_float(value: Any) -> float | None:
    if value in {None, ""}:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _write_svg_message(path: Path, title: str, message: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = f"""<svg xmlns="http://www.w3.org/2000/svg" width="900" height="180" role="img" aria-label="{html.escape(title)}">
  <rect width="100%" height="100%" fill="#ffffff"/>
  <text x="32" y="48" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#202124">{html.escape(title)}</text>
  <text x="32" y="92" font-family="Arial, sans-serif" font-size="15" fill="#5f6368">{html.escape(message)}</text>
</svg>
"""
    path.write_text(body, encoding="utf-8")


def write_frip_peak_overview_svg(
    run_dir: Path, rows: list[dict[str, Any]], output_prefix: str, title: str
) -> str:
    path = run_dir / "qc" / f"{output_prefix}_frip_peak_overview.svg"
    values = []
    for row in rows:
        frip = _to_float(row.get("frip"))
        peak_count = _to_float(
            row.get("blacklist_filtered_peak_count") or row.get("raw_peak_count")
        )
        if frip is not None or peak_count is not None:
            values.append(
                {"sample": str(row.get("sample", "")), "frip": frip, "peak_count": peak_count}
            )
    if not values:
        _write_svg_message(
            path,
            f"{title} FRiP And Peak Overview",
            "FRiP and peak-count metrics will populate after peak calling outputs are present.",
        )
        return _rel(path, run_dir)

    width = 980
    row_height = 44
    height = 96 + row_height * len(values)
    max_peak = max((item["peak_count"] or 0 for item in values), default=1) or 1
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" role="img" aria-label="{html.escape(title)} FRiP and peak overview">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="32" y="42" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#202124">{html.escape(title)} FRiP And Peak Overview</text>',
        '<text x="260" y="76" font-family="Arial, sans-serif" font-size="12" fill="#5f6368">FRiP</text>',
        '<text x="555" y="76" font-family="Arial, sans-serif" font-size="12" fill="#5f6368">Peak count</text>',
    ]
    for index, item in enumerate(values):
        y = 104 + index * row_height
        sample = item["sample"]
        frip = item["frip"] or 0.0
        peak_count = item["peak_count"] or 0.0
        frip_width = max(2, min(220, frip * 220))
        peak_width = max(2, min(280, peak_count / max_peak * 280))
        lines.extend(
            [
                f'<text x="32" y="{y + 15}" font-family="Arial, sans-serif" font-size="13" fill="#202124">{html.escape(sample)}</text>',
                f'<rect x="260" y="{y}" width="220" height="18" fill="#eef2f7"/>',
                f'<rect x="260" y="{y}" width="{frip_width:.1f}" height="18" fill="#2f80ed"/>',
                f'<text x="488" y="{y + 14}" font-family="Arial, sans-serif" font-size="12" fill="#202124">{frip:.4g}</text>',
                f'<rect x="555" y="{y}" width="280" height="18" fill="#eef2f7"/>',
                f'<rect x="555" y="{y}" width="{peak_width:.1f}" height="18" fill="#34a853"/>',
                f'<text x="846" y="{y + 14}" font-family="Arial, sans-serif" font-size="12" fill="#202124">{int(peak_count)}</text>',
            ]
        )
    lines.append("</svg>\n")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return _rel(path, run_dir)


def write_insert_size_distribution_svg(
    run_dir: Path, samples: list[dict[str, str]], output_prefix: str, title: str
) -> str:
    path = run_dir / "qc" / f"{output_prefix}_insert_size_distribution.svg"
    bins = [(0, 100), (100, 200), (200, 400), (400, 800), (800, 2000)]
    counts = [0 for _ in bins]
    total = 0
    for sample in samples:
        insert_path = run_dir / "qc" / f"{sample['sample']}.insert_sizes.txt"
        if not insert_path.exists():
            continue
        for line in insert_path.read_text(encoding="utf-8", errors="replace").splitlines():
            value = _to_float(line.strip())
            if value is None:
                continue
            total += 1
            abs_value = abs(value)
            for index, (start, end) in enumerate(bins):
                if start <= abs_value < end:
                    counts[index] += 1
                    break
    if not total:
        _write_svg_message(
            path,
            f"{title} Insert-Size Distribution",
            "Insert-size bars will populate after paired-read alignment metrics are available.",
        )
        return _rel(path, run_dir)

    width = 900
    height = 300
    max_count = max(counts) or 1
    chart_x = 82
    chart_y = 66
    chart_h = 160
    bar_w = 110
    gap = 28
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" role="img" aria-label="{html.escape(title)} insert-size distribution">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="32" y="40" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#202124">{html.escape(title)} Insert-Size Distribution</text>',
        f'<text x="32" y="268" font-family="Arial, sans-serif" font-size="12" fill="#5f6368">Total fragments parsed: {total}</text>',
    ]
    for index, ((start, end), count) in enumerate(zip(bins, counts)):
        x = chart_x + index * (bar_w + gap)
        bar_h = max(2, count / max_count * chart_h)
        y = chart_y + chart_h - bar_h
        label = f"{start}-{end}"
        lines.extend(
            [
                f'<rect x="{x}" y="{chart_y}" width="{bar_w}" height="{chart_h}" fill="#f6f8fa"/>',
                f'<rect x="{x}" y="{y:.1f}" width="{bar_w}" height="{bar_h:.1f}" fill="#7b61ff"/>',
                f'<text x="{x + bar_w / 2:.1f}" y="{chart_y + chart_h + 24}" font-family="Arial, sans-serif" font-size="12" text-anchor="middle" fill="#202124">{label}</text>',
                f'<text x="{x + bar_w / 2:.1f}" y="{y - 8:.1f}" font-family="Arial, sans-serif" font-size="12" text-anchor="middle" fill="#202124">{count}</text>',
            ]
        )
    lines.append("</svg>\n")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return _rel(path, run_dir)


def write_browser_track_preview(run_dir: Path, track_summary: dict[str, Any], title: str) -> str:
    path = run_dir / "tracks" / "browser_track_preview.html"
    rows = []
    for row in track_summary.get("tracks", []):
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(row.get('sample', '')))}</td>"
            f"<td>{html.escape(str(row.get('exists', '')))}</td>"
            f"<td><code>{html.escape(str(row.get('bigwig', '')))}</code></td>"
            f"<td><code>{html.escape(str(row.get('track_line', '')))}</code></td>"
            "</tr>"
        )
    if not rows:
        rows.append('<tr><td colspan="4">No track rows were available.</td></tr>')
    body = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(title)} Browser Tracks</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 28px; color: #202124; }}
    table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
    th, td {{ border-bottom: 1px solid #ddd; padding: 8px; text-align: left; vertical-align: top; }}
    th {{ background: #f6f8fa; }}
    code {{ white-space: pre-wrap; overflow-wrap: anywhere; }}
  </style>
</head>
<body>
  <h1>{html.escape(title)} Browser Tracks</h1>
  <p>Use these rows as a handoff for IGV/UCSC-style review. Relative bigWig paths require serving the run directory or replacing them with hosted URLs.</p>
  <table>
    <thead><tr><th>Sample</th><th>Exists</th><th>bigWig</th><th>UCSC Track Line</th></tr></thead>
    <tbody>{"".join(rows)}</tbody>
  </table>
</body>
</html>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return _rel(path, run_dir)


def write_epigenomics_dashboard(
    run_dir: Path,
    rows: list[dict[str, Any]],
    *,
    output_prefix: str,
    title: str,
    visual_paths: dict[str, str],
) -> str:
    path = run_dir / "qc" / f"{output_prefix}_dashboard.html"
    headers = [
        "sample",
        "status",
        "frip",
        "raw_peak_count",
        "blacklist_filtered_peak_count",
        "insert_size_median",
        "nucleosome_free_fraction",
        "bigwig_exists",
        "notes",
    ]
    row_html = []
    for row in rows:
        row_html.append(
            "<tr>"
            + "".join(f"<td>{html.escape(str(row.get(header, '')))}</td>" for header in headers)
            + "</tr>"
        )
    if not row_html:
        row_html.append(
            f'<tr><td colspan="{len(headers)}">No sample rows were available.</td></tr>'
        )
    links = "".join(
        f'<li><a href="{html.escape(str(Path(rel).relative_to("qc") if rel.startswith("qc/") else Path("..") / rel))}">{html.escape(label)}</a></li>'
        for label, rel in [
            ("FRiP and peak overview", visual_paths.get("frip_peak_overview", "")),
            ("Insert-size distribution", visual_paths.get("insert_size_distribution", "")),
            ("Browser track preview", visual_paths.get("browser_track_preview", "")),
        ]
        if rel
    )
    body = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(title)} QC Dashboard</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 28px; color: #202124; }}
    table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
    th, td {{ border-bottom: 1px solid #ddd; padding: 8px; text-align: left; vertical-align: top; }}
    th {{ background: #f6f8fa; }}
  </style>
</head>
<body>
  <h1>{html.escape(title)} QC Dashboard</h1>
  <p>Compact native review of FRiP, peak counts, insert-size metrics, signal-track state, and remaining caveats parsed from the run directory.</p>
  <ul>{links}</ul>
  <table>
    <thead><tr>{"".join(f"<th>{html.escape(header)}</th>" for header in headers)}</tr></thead>
    <tbody>{"".join(row_html)}</tbody>
  </table>
</body>
</html>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return _rel(path, run_dir)


def peak_paths(run_dir: Path, sample: str, peak_mode: str) -> tuple[Path, Path]:
    raw_suffix = "narrowPeak" if peak_mode == "narrow" else "broadPeak"
    raw = run_dir / "peaks" / f"{sample}_peaks.{raw_suffix}"
    filtered = run_dir / "peaks" / f"{sample}.blacklist_filtered.{peak_mode}Peak"
    return raw, filtered


def write_track_outputs(
    run_dir: Path, samples: list[dict[str, str]], *, title: str
) -> dict[str, Any]:
    rows = []
    resources = []
    for sample in samples:
        name = sample["sample"]
        bw = run_dir / "tracks" / f"{name}.bw"
        exists = bw.exists()
        row = {
            "sample": name,
            "bigwig": _rel(bw, run_dir),
            "exists": str(exists).lower(),
            "track_line": f'track type=bigWig name="{name}" description="{title} {name}" bigDataUrl={_rel(bw, run_dir)} visibility=full autoScale=on',
        }
        rows.append(row)
        if exists:
            resources.append(
                f'    <Resource path="{escape(str(bw))}" name="{escape(name)}" type="bigwig" />'
            )
    write_tsv(
        run_dir / "tracks" / "browser_tracks.tsv",
        rows,
        ["sample", "bigwig", "exists", "track_line"],
    )
    write_text(
        run_dir / "tracks" / "ucsc_track_lines.txt",
        "\n".join(row["track_line"] for row in rows) + "\n",
    )
    igv = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<Session name="{escape(title)}" version="8">',
        "  <Resources>",
    ]
    igv.extend(resources)
    igv.extend(["  </Resources>", "</Session>", ""])
    write_text(run_dir / "tracks" / "igv_session.xml", "\n".join(igv))
    summary = {
        "status": "created" if any(row["exists"] == "true" for row in rows) else "not_available",
        "tracks": rows,
        "outputs": {
            "browser_tracks": "tracks/browser_tracks.tsv",
            "ucsc_track_lines": "tracks/ucsc_track_lines.txt",
            "igv_session": "tracks/igv_session.xml",
        },
        "note": "UCSC track lines use relative bigDataUrl values; serve the run directory over HTTP or edit URLs for a genome browser.",
    }
    write_json(run_dir / "tracks" / "track_manifest.json", summary)
    return summary


def summarize_motif_outputs(run_dir: Path, samples: list[dict[str, str]]) -> dict[str, Any]:
    rows = []
    for sample in samples:
        name = sample["sample"]
        known = run_dir / "motifs" / name / "knownResults.txt"
        homer = run_dir / "motifs" / name / "homerResults.html"
        row = {
            "sample": name,
            "known_results": _rel(known, run_dir),
            "known_results_exists": str(known.exists()).lower(),
            "homer_results": _rel(homer, run_dir),
            "homer_results_exists": str(homer.exists()).lower(),
            "top_motif": "",
            "top_p_value": "",
        }
        if known.exists():
            try:
                with known.open(newline="", encoding="utf-8", errors="replace") as handle:
                    reader = csv.DictReader(handle, delimiter="\t")
                    first = next(reader, None)
                if first:
                    row["top_motif"] = (
                        first.get("Motif Name") or first.get("Name") or first.get("motif") or ""
                    )
                    row["top_p_value"] = (
                        first.get("P-value") or first.get("p-value") or first.get("Pvalue") or ""
                    )
            except Exception:
                row["top_motif"] = ""
        rows.append(row)
    write_tsv(
        run_dir / "motifs" / "motif_summary.tsv",
        rows,
        [
            "sample",
            "known_results",
            "known_results_exists",
            "homer_results",
            "homer_results_exists",
            "top_motif",
            "top_p_value",
        ],
    )
    summary = {
        "status": "created"
        if any(
            row["known_results_exists"] == "true" or row["homer_results_exists"] == "true"
            for row in rows
        )
        else "not_available",
        "samples": rows,
        "outputs": {"motif_summary": "motifs/motif_summary.tsv"},
    }
    write_json(run_dir / "motifs" / "motif_summary.json", summary)
    return summary


def summarize_epigenomics_outputs(
    run_dir: Path,
    samples: list[dict[str, str]],
    *,
    peak_mode: str,
    output_prefix: str,
    title: str,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    consensus_count = count_bed_rows(run_dir / "peaks" / "consensus_peaks.bed")
    motif_summary = summarize_motif_outputs(run_dir, samples)
    track_summary = write_track_outputs(run_dir, samples, title=title)
    for sample in samples:
        name = sample["sample"]
        is_control = str(sample.get("is_control", "")).lower() == "true"
        filtered_bam = run_dir / "alignment" / f"{name}.filtered.bam"
        flagstat = parse_flagstat(run_dir / "qc" / f"{name}.flagstat.txt")
        insert = parse_insert_sizes(run_dir / "qc" / f"{name}.insert_sizes.txt")
        frip_reads = read_int(run_dir / "qc" / f"{name}.frip_reads.txt")
        filtered_reads = read_int(run_dir / "qc" / f"{name}.filtered_reads.txt")
        raw_peak, filtered_peak = peak_paths(run_dir, name, peak_mode)
        raw_peak_count = count_bed_rows(raw_peak)
        filtered_peak_count = count_bed_rows(filtered_peak)
        bw = run_dir / "tracks" / f"{name}.bw"
        tss_matrix = run_dir / "qc" / f"{name}.tss_matrix.gz"
        tss_profile = run_dir / "qc" / f"{name}.tss_profile.png"
        tss_heatmap = run_dir / "qc" / f"{name}.tss_heatmap.png"
        motif_known = run_dir / "motifs" / name / "knownResults.txt"
        observed = [
            filtered_bam.exists(),
            flagstat["total_reads"] is not None,
            raw_peak_count is not None,
            bw.exists(),
            frip_reads is not None and filtered_reads is not None,
        ]
        notes = []
        if not is_control and (frip_reads is None or filtered_reads in {None, 0}):
            notes.append("FRiP inputs not found")
        if not is_control and raw_peak_count is None:
            notes.append("peak file not found")
        if not bw.exists():
            notes.append("bigWig track not found")
        if insert["insert_size_count"] is None:
            notes.append("insert-size distribution not found")
        if is_control:
            notes.append("control sample: peak and FRiP outputs are not expected")
        frip = ""
        if not is_control and frip_reads is not None and filtered_reads:
            frip = round(frip_reads / filtered_reads, 5)
        status = (
            "created"
            if all(observed[:2]) and (is_control or observed[2])
            else ("partial" if any(observed) else "not_executed")
        )
        rows.append(
            {
                "sample": name,
                "layout": sample.get("layout", ""),
                "is_control": str(is_control).lower(),
                "control_sample": sample.get("control_sample", ""),
                "status": status,
                "filtered_bam": _rel(filtered_bam, run_dir),
                "filtered_bam_exists": str(filtered_bam.exists()).lower(),
                "total_filtered_reads": filtered_reads if filtered_reads is not None else "",
                "mapped_reads": flagstat["mapped_reads"]
                if flagstat["mapped_reads"] is not None
                else "",
                "duplicate_reads": flagstat["duplicate_reads"]
                if flagstat["duplicate_reads"] is not None
                else "",
                "frip_reads": frip_reads if frip_reads is not None else "",
                "frip": frip,
                "raw_peak_count": raw_peak_count if raw_peak_count is not None else "",
                "blacklist_filtered_peak_count": filtered_peak_count
                if filtered_peak_count is not None
                else "",
                "consensus_peak_count": consensus_count if consensus_count is not None else "",
                "insert_size_count": insert["insert_size_count"]
                if insert["insert_size_count"] is not None
                else "",
                "insert_size_median": insert["insert_size_median"]
                if insert["insert_size_median"] is not None
                else "",
                "insert_size_mean": insert["insert_size_mean"]
                if insert["insert_size_mean"] is not None
                else "",
                "nucleosome_free_fraction": insert["nucleosome_free_fraction"]
                if insert["nucleosome_free_fraction"] is not None
                else "",
                "bigwig": _rel(bw, run_dir),
                "bigwig_exists": str(bw.exists()).lower(),
                "tss_matrix_exists": str(tss_matrix.exists()).lower(),
                "tss_profile_exists": str(tss_profile.exists()).lower(),
                "tss_heatmap_exists": str(tss_heatmap.exists()).lower(),
                "motif_summary_exists": str(motif_known.exists()).lower(),
                "notes": "; ".join(notes),
            }
        )
    write_tsv(run_dir / "qc" / f"{output_prefix}_summary.tsv", rows, EPIGENOMICS_SUMMARY_FIELDS)
    visual_paths = {
        "frip_peak_overview": write_frip_peak_overview_svg(run_dir, rows, output_prefix, title),
        "insert_size_distribution": write_insert_size_distribution_svg(
            run_dir, samples, output_prefix, title
        ),
        "browser_track_preview": write_browser_track_preview(run_dir, track_summary, title),
    }
    visual_paths["dashboard"] = write_epigenomics_dashboard(
        run_dir,
        rows,
        output_prefix=output_prefix,
        title=title,
        visual_paths=visual_paths,
    )
    summary = {
        "status": "created"
        if any(row["status"] in {"created", "partial"} for row in rows)
        else "not_available",
        "samples": rows,
        "samples_with_peaks": sum(1 for row in rows if row["raw_peak_count"] != ""),
        "samples_with_tracks": sum(1 for row in rows if row["bigwig_exists"] == "true"),
        "consensus_peak_count": consensus_count,
        "track_manifest": track_summary,
        "motif_summary": motif_summary,
        "visuals": visual_paths,
        "outputs": {
            "summary_table": f"qc/{output_prefix}_summary.tsv",
            "summary_json": f"qc/{output_prefix}_summary.json",
            "dashboard": visual_paths["dashboard"],
            "frip_peak_overview": visual_paths["frip_peak_overview"],
            "insert_size_distribution": visual_paths["insert_size_distribution"],
            "track_manifest": "tracks/track_manifest.json",
            "browser_tracks": "tracks/browser_tracks.tsv",
            "browser_track_preview": visual_paths["browser_track_preview"],
            "igv_session": "tracks/igv_session.xml",
            "motif_summary": "motifs/motif_summary.tsv",
        },
    }
    write_json(run_dir / "qc" / f"{output_prefix}_summary.json", summary)
    return summary
