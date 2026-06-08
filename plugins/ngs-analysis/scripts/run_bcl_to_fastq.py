#!/usr/bin/env python3
"""Validate Illumina BCL run folders and run local BCL-to-FASTQ conversion when available."""

from __future__ import annotations

import argparse
import csv
import shlex
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from ngs_run_utils import (
    build_artifact_index,
    command_path,
    run_cmd,
    slug_timestamp,
    software_versions,
    tool_preflight,
    write_json,
    write_standard_manifest,
    write_text,
)

WORKSPACE_ROOT = Path.cwd()
DEFAULT_RUN_ROOT = WORKSPACE_ROOT / "ngs_runs" / "bcl_to_fastq"
DOCKER_MOUNT_ROOTS = (Path("/Users"), Path("/private"), Path("/Volumes"))
DEMUX_QC_THRESHOLDS = {
    "warn_undetermined_fraction": 0.20,
    "fail_undetermined_fraction": 0.50,
    "warn_top_unknown_fraction": 0.01,
}


def parse_runinfo(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "ok": False,
        "reads": [],
        "errors": [],
    }
    if not path.exists():
        result["errors"].append("RunInfo.xml is missing")
        return result
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        result["errors"].append(f"RunInfo.xml parse failed: {exc}")
        return result

    run = root.find(".//Run")
    if run is not None:
        result["run_id"] = run.attrib.get("Id")
        result["flowcell"] = run.attrib.get("Flowcell")
        result["instrument"] = run.attrib.get("Instrument")

    reads = []
    for read in root.findall(".//Reads/Read"):
        read_info = {
            "number": int(read.attrib.get("Number", "0") or 0),
            "num_cycles": int(read.attrib.get("NumCycles", "0") or 0),
            "is_indexed_read": read.attrib.get("IsIndexedRead", "").lower() == "y",
        }
        reads.append(read_info)
    result["reads"] = sorted(reads, key=lambda item: item["number"])
    result["indexed_reads"] = [item for item in result["reads"] if item["is_indexed_read"]]
    result["sequencing_reads"] = [item for item in result["reads"] if not item["is_indexed_read"]]
    if not result["reads"]:
        result["errors"].append("RunInfo.xml does not contain Reads/Read entries")
    result["ok"] = not result["errors"]
    return result


def parse_runparameters(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "ok": True,
        "values": {},
        "errors": [],
    }
    if not path.exists():
        result["ok"] = False
        result["errors"].append("RunParameters.xml is missing")
        return result
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        result["ok"] = False
        result["errors"].append(f"RunParameters.xml parse failed: {exc}")
        return result

    wanted = [
        "ApplicationName",
        "ApplicationVersion",
        "InstrumentType",
        "RunID",
        "ExperimentName",
        "FlowCellType",
    ]
    values = {}
    for tag in wanted:
        node = root.find(f".//{tag}")
        if node is not None and node.text:
            values[tag] = node.text.strip()
    result["values"] = values
    return result


def normalize_header(value: str) -> str:
    return value.strip().lstrip("\ufeff")


def parse_sample_sheet(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "ok": False,
        "sections": [],
        "data_columns": [],
        "data_rows": [],
        "reads": [],
        "settings": {},
        "errors": [],
        "warnings": [],
    }
    if not path.exists():
        result["errors"].append("sample sheet is missing")
        return result

    with path.open(newline="", encoding="utf-8-sig") as handle:
        parsed = list(csv.reader(handle))

    current_section: str | None = None
    data_header: list[str] | None = None
    in_data = False
    for raw_row in parsed:
        row = [item.strip() for item in raw_row]
        if not row or not any(row):
            continue
        first = normalize_header(row[0])
        if first.startswith("[") and first.endswith("]"):
            current_section = first.strip("[]")
            result["sections"].append(current_section)
            in_data = current_section.lower().endswith("data") or current_section.lower() == "data"
            data_header = None
            continue
        if current_section is None:
            if data_header is None:
                data_header = [normalize_header(item) for item in row]
                result["data_columns"] = data_header
                in_data = True
            else:
                values = row + [""] * (len(data_header) - len(row))
                result["data_rows"].append(dict(zip(data_header, values)))
            continue
        section_key = current_section.lower()
        if section_key == "reads":
            try:
                result["reads"].append(int(row[0]))
            except ValueError:
                result["warnings"].append(f"could not parse [Reads] row: {','.join(row)}")
            continue
        if section_key in {"settings", "header"} and len(row) >= 2:
            result["settings"][row[0]] = row[1]
            continue
        if in_data:
            if data_header is None:
                data_header = [normalize_header(item) for item in row]
                result["data_columns"] = data_header
            else:
                values = row + [""] * (len(data_header) - len(row))
                result["data_rows"].append(dict(zip(data_header, values)))

    data_rows = result["data_rows"]
    if not data_rows:
        result["errors"].append("sample sheet does not contain data rows")
        return result

    duplicate_keys: set[tuple[str, str, str]] = set()
    for index, row in enumerate(data_rows, start=1):
        sample = (
            row.get("Sample_ID")
            or row.get("SampleID")
            or row.get("Sample_Name")
            or row.get("sample")
            or ""
        )
        i7 = row.get("index") or row.get("Index") or row.get("I7_Index_ID") or ""
        i5 = row.get("index2") or row.get("Index2") or row.get("I5_Index_ID") or ""
        lane = row.get("Lane") or row.get("lane") or "all"
        if not sample:
            result["errors"].append(f"data row {index}: sample identifier is missing")
        if not i7 and not i5:
            result["warnings"].append(f"data row {index}: no index sequence columns were found")
        key = (lane, i7, i5)
        if key in duplicate_keys:
            result["errors"].append(
                f"data row {index}: duplicate lane/index/index2 combination {key}"
            )
        duplicate_keys.add(key)

    result["sample_count"] = len(
        {
            row.get("Sample_ID")
            or row.get("SampleID")
            or row.get("Sample_Name")
            or row.get("sample")
            or f"row_{i}"
            for i, row in enumerate(data_rows, start=1)
        }
    )
    result["index_lengths"] = sorted(
        {
            len(row.get("index") or row.get("Index") or "")
            for row in data_rows
            if row.get("index") or row.get("Index")
        }
    )
    result["index2_lengths"] = sorted(
        {
            len(row.get("index2") or row.get("Index2") or "")
            for row in data_rows
            if row.get("index2") or row.get("Index2")
        }
    )
    result["ok"] = not result["errors"]
    return result


def validate_index_lengths(runinfo: dict[str, Any], sample_sheet: dict[str, Any]) -> list[str]:
    warnings = []
    indexed_cycles = [item.get("num_cycles", 0) for item in runinfo.get("indexed_reads", [])]
    sequencing_cycles = [item.get("num_cycles", 0) for item in runinfo.get("sequencing_reads", [])]
    sample_sheet_reads = sample_sheet.get("reads") or []
    if (
        sample_sheet_reads
        and sequencing_cycles
        and sample_sheet_reads != sequencing_cycles[: len(sample_sheet_reads)]
    ):
        warnings.append(
            f"sample sheet [Reads] values do not match RunInfo sequencing reads: sample sheet {sample_sheet_reads}, RunInfo {sequencing_cycles}"
        )
    if not indexed_cycles:
        return warnings
    index_lengths = sample_sheet.get("index_lengths") or []
    index2_lengths = sample_sheet.get("index2_lengths") or []
    if (
        index_lengths
        and indexed_cycles
        and any(length > indexed_cycles[0] for length in index_lengths)
    ):
        warnings.append(
            f"i7 index length exceeds RunInfo index read cycles: sample sheet {index_lengths}, RunInfo {indexed_cycles[0]}"
        )
    if (
        index2_lengths
        and len(indexed_cycles) >= 2
        and any(length > indexed_cycles[1] for length in index2_lengths)
    ):
        warnings.append(
            f"i5 index length exceeds RunInfo index read cycles: sample sheet {index2_lengths}, RunInfo {indexed_cycles[1]}"
        )
    if index2_lengths and len(indexed_cycles) < 2:
        warnings.append(
            "sample sheet has index2 values but RunInfo.xml has fewer than two indexed reads"
        )
    return warnings


def validate_inputs(args: argparse.Namespace) -> dict[str, Any]:
    run_folder = args.run_folder.expanduser().resolve()
    sample_sheet = args.sample_sheet.expanduser().resolve()
    runinfo = parse_runinfo(run_folder / "RunInfo.xml")
    runparameters = parse_runparameters(run_folder / "RunParameters.xml")
    sheet = parse_sample_sheet(sample_sheet)
    basecalls = run_folder / "Data" / "Intensities" / "BaseCalls"
    errors = []
    warnings = []
    if not run_folder.exists():
        errors.append(f"run folder does not exist: {run_folder}")
    if not basecalls.exists():
        errors.append(f"BaseCalls directory does not exist: {basecalls}")
    errors.extend(runinfo.get("errors", []))
    errors.extend(sheet.get("errors", []))
    warnings.extend(runparameters.get("errors", []))
    warnings.extend(sheet.get("warnings", []))
    warnings.extend(validate_index_lengths(runinfo, sheet))

    validation = {
        "ok": not errors,
        "run_folder": str(run_folder),
        "sample_sheet": str(sample_sheet),
        "output_directory": str(args.output_directory.expanduser().resolve()),
        "runinfo": runinfo,
        "runparameters": runparameters,
        "sample_sheet_summary": sheet,
        "basecalls_directory": str(basecalls),
        "basecalls_directory_exists": basecalls.exists(),
        "errors": errors,
        "warnings": warnings,
    }
    return validation


def select_converter(args: argparse.Namespace) -> str | None:
    if args.converter:
        return args.converter if command_path(args.converter) else None
    if command_path("bcl-convert"):
        return "bcl-convert"
    if command_path("bcl2fastq"):
        return "bcl2fastq"
    return None


def conversion_command(converter: str, args: argparse.Namespace) -> list[str]:
    run_folder = str(args.run_folder.expanduser().resolve())
    sample_sheet = str(args.sample_sheet.expanduser().resolve())
    output_directory = str(args.output_directory.expanduser().resolve())
    if Path(converter).name == "bcl2fastq" or converter == "bcl2fastq":
        return [
            converter,
            "--runfolder-dir",
            run_folder,
            "--output-dir",
            output_directory,
            "--sample-sheet",
            sample_sheet,
        ]
    return [
        converter,
        "--bcl-input-directory",
        run_folder,
        "--output-directory",
        output_directory,
        "--sample-sheet",
        sample_sheet,
    ]


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def parse_int(value: str | None) -> int | None:
    if not value:
        return None
    try:
        return int(value.replace(",", ""))
    except ValueError:
        return None


def parse_float(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def path_within_roots(path: Path, roots: tuple[Path, ...]) -> bool:
    return any(path == root or root in path.parents for root in roots)


def converter_runtime_preflight(converter: str | None, args: argparse.Namespace) -> dict[str, Any]:
    result: dict[str, Any] = {
        "converter": converter,
        "converter_path": command_path(converter) if converter else None,
        "uses_docker_wrapper": False,
        "docker_daemon_ok": None,
        "errors": [],
        "warnings": [],
        "mount_roots": [str(item) for item in DOCKER_MOUNT_ROOTS],
    }
    if not converter:
        return result
    converter_path = Path(result["converter_path"] or converter)
    if converter_path.exists():
        try:
            head = converter_path.read_text(encoding="utf-8", errors="ignore")[:2000]
            result["uses_docker_wrapper"] = "docker run" in head
        except OSError:
            pass
    if result["uses_docker_wrapper"]:
        probe = run_cmd(["docker", "info"], WORKSPACE_ROOT, timeout=30)
        result["docker_daemon_ok"] = probe.get("ok", False)
        if not probe.get("ok", False):
            result["warnings"].append(
                "docker daemon is not ready for the Docker-backed bcl-convert wrapper"
            )
        for label, candidate in {
            "run_folder": args.run_folder.expanduser().resolve(),
            "sample_sheet": args.sample_sheet.expanduser().resolve(),
            "output_directory": args.output_directory.expanduser().resolve(),
        }.items():
            if not path_within_roots(candidate, DOCKER_MOUNT_ROOTS):
                result["errors"].append(
                    f"{label} is outside the Docker wrapper mount roots {', '.join(str(item) for item in DOCKER_MOUNT_ROOTS)}"
                )
    return result


def docker_daemon_error(result: dict[str, Any]) -> bool:
    output = str(result.get("stdout_tail", "") or "")
    return "Cannot connect to the Docker daemon" in output


def wait_for_docker_daemon(timeout_seconds: int = 60, poll_seconds: int = 5) -> dict[str, Any]:
    attempts = []
    deadline = time.time() + timeout_seconds
    while time.time() <= deadline:
        probe = run_cmd(["docker", "info"], WORKSPACE_ROOT, timeout=30)
        attempts.append(
            {
                "ok": probe.get("ok", False),
                "finished_at": probe.get("finished_at"),
                "stdout_tail": probe.get("stdout_tail", ""),
            }
        )
        if probe.get("ok", False):
            return {"ok": True, "attempts": attempts}
        if time.time() + poll_seconds > deadline:
            break
        time.sleep(poll_seconds)
    return {"ok": False, "attempts": attempts}


def normalize_report_path(path_value: str, output_directory: Path) -> Path:
    normalized = (
        path_value.replace("/host", "", 1) if path_value.startswith("/host/") else path_value
    )
    candidate = Path(normalized)
    if candidate.exists():
        return candidate
    return output_directory / Path(path_value).name


def summarize_fastq_outputs(
    output_directory: Path, demux_rows: list[dict[str, str]]
) -> list[dict[str, Any]]:
    by_sample = {
        row.get("SampleID", ""): parse_int(row.get("# Reads"))
        for row in demux_rows
        if row.get("SampleID")
    }
    rows = []
    reports_dir = output_directory / "Reports"
    for entry in read_csv_rows(reports_dir / "fastq_list.csv"):
        for read_key in ("Read1File", "Read2File"):
            path_value = entry.get(read_key)
            if not path_value:
                continue
            path = normalize_report_path(path_value, output_directory)
            rows.append(
                {
                    "sample": entry.get("RGSM"),
                    "lane": entry.get("Lane"),
                    "read": "R1" if read_key == "Read1File" else "R2",
                    "path": str(path),
                    "bytes": path.stat().st_size if path.exists() else None,
                    "read_pairs": by_sample.get(entry.get("RGSM", "")),
                }
            )
    undetermined_reads = by_sample.get("Undetermined")
    for path in sorted(output_directory.glob("Undetermined*.fastq.gz")):
        rows.append(
            {
                "sample": "Undetermined",
                "lane": "1",
                "read": "R1" if "_R1_" in path.name else "R2",
                "path": str(path),
                "bytes": path.stat().st_size,
                "read_pairs": undetermined_reads,
            }
        )
    return rows


def parse_report_bundle(output_directory: Path) -> dict[str, Any] | None:
    reports_dir = output_directory / "Reports"
    if not reports_dir.exists():
        return None
    demux_rows = read_csv_rows(reports_dir / "Demultiplex_Stats.csv")
    quality_rows = read_csv_rows(reports_dir / "Quality_Metrics.csv")
    unknown_rows = read_csv_rows(reports_dir / "Top_Unknown_Barcodes.csv")
    assigned_reads = sum(
        parse_int(row.get("# Reads")) or 0
        for row in demux_rows
        if row.get("SampleID") != "Undetermined"
    )
    undetermined_reads = sum(
        parse_int(row.get("# Reads")) or 0
        for row in demux_rows
        if row.get("SampleID") == "Undetermined"
    )
    total_reads = assigned_reads + undetermined_reads
    assigned_fraction = (assigned_reads / total_reads) if total_reads else None
    undetermined_fraction = (undetermined_reads / total_reads) if total_reads else None
    top_unknown = [
        {
            "index": row.get("index"),
            "index2": row.get("index2"),
            "reads": parse_int(row.get("# Reads")),
            "fraction_of_all_reads": parse_float(row.get("% of All Reads")),
        }
        for row in unknown_rows[:5]
    ]
    quality_by_sample = {}
    for row in quality_rows:
        sample = row.get("SampleID", "unknown")
        quality_by_sample.setdefault(sample, {})[f"read_{row.get('ReadNumber')}"] = {
            "yield": parse_int(row.get("Yield")),
            "q30_fraction": parse_float(row.get("% Q30")),
            "mean_quality_pf": parse_float(row.get("Mean Quality Score (PF)")),
        }
    issues = []
    assessment = "pass"
    if (
        undetermined_fraction is not None
        and undetermined_fraction >= DEMUX_QC_THRESHOLDS["fail_undetermined_fraction"]
    ):
        assessment = "fail"
        issues.append(
            f"undetermined reads are {undetermined_fraction:.2%}, above the fail threshold of {DEMUX_QC_THRESHOLDS['fail_undetermined_fraction']:.0%}"
        )
    elif (
        undetermined_fraction is not None
        and undetermined_fraction >= DEMUX_QC_THRESHOLDS["warn_undetermined_fraction"]
    ):
        assessment = "warning"
        issues.append(
            f"undetermined reads are {undetermined_fraction:.2%}, above the warning threshold of {DEMUX_QC_THRESHOLDS['warn_undetermined_fraction']:.0%}"
        )
    top_unknown_fraction = max(
        (
            item["fraction_of_all_reads"]
            for item in top_unknown
            if item["fraction_of_all_reads"] is not None
        ),
        default=None,
    )
    if (
        top_unknown_fraction is not None
        and top_unknown_fraction >= DEMUX_QC_THRESHOLDS["warn_top_unknown_fraction"]
    ):
        assessment = "warning" if assessment == "pass" else assessment
        issues.append(
            f"top unknown barcode accounts for {top_unknown_fraction:.2%} of all reads, at or above the warning threshold of {DEMUX_QC_THRESHOLDS['warn_top_unknown_fraction']:.0%}"
        )
    return {
        "output_directory": str(output_directory),
        "report_directory": str(reports_dir),
        "assigned_reads": assigned_reads,
        "undetermined_reads": undetermined_reads,
        "total_reads": total_reads,
        "assigned_fraction": assigned_fraction,
        "undetermined_fraction": undetermined_fraction,
        "assessment": assessment,
        "issues": issues,
        "quality_by_sample": quality_by_sample,
        "top_unknown_barcodes": top_unknown,
        "fastq_outputs": summarize_fastq_outputs(output_directory, demux_rows),
    }


def write_commands(run_dir: Path, args: argparse.Namespace, converter: str | None) -> None:
    lines = ["#!/usr/bin/env bash", "set -euo pipefail"]
    if converter:
        lines.append(shlex.join(conversion_command(converter, args)))
    else:
        lines.append("# bcl-convert or bcl2fastq is required before execution.")
        lines.append(
            "# "
            + shlex.join(
                [
                    "bcl-convert",
                    "--bcl-input-directory",
                    str(args.run_folder.expanduser().resolve()),
                    "--output-directory",
                    str(args.output_directory.expanduser().resolve()),
                    "--sample-sheet",
                    str(args.sample_sheet.expanduser().resolve()),
                ]
            )
        )
    write_text(run_dir / "commands.sh", "\n".join(lines) + "\n")


def execute_conversion(
    run_dir: Path, args: argparse.Namespace, converter: str, runtime_preflight: dict[str, Any]
) -> dict[str, Any]:
    output_directory = args.output_directory.expanduser().resolve()
    output_directory.parent.mkdir(parents=True, exist_ok=True)
    command = conversion_command(converter, args)
    attempts = []
    result = run_cmd(command, run_dir, timeout=args.timeout_seconds)
    attempts.append(result)
    if (
        runtime_preflight.get("uses_docker_wrapper")
        and not result.get("ok")
        and docker_daemon_error(result)
    ):
        daemon_wait = wait_for_docker_daemon()
        if daemon_wait.get("ok"):
            retry = run_cmd(command, run_dir, timeout=args.timeout_seconds)
            retry["retry_reason"] = "docker_daemon_ready_after_wait"
            attempts.append(retry)
            result = retry
    payload = {
        "ok": result.get("ok"),
        "converter": converter,
        "output_directory": str(output_directory),
        "command": result.get("cmd"),
        "attempts": attempts,
    }
    write_json(run_dir / "logs" / "bcl_conversion.json", payload)
    write_text(run_dir / "logs" / "bcl_conversion.log", result.get("stdout_tail", ""))
    return payload


def write_summary(
    run_dir: Path,
    status: str,
    validation: dict[str, Any],
    converter: str | None,
    runtime_preflight: dict[str, Any],
    report_bundle: dict[str, Any] | None,
) -> None:
    sheet = validation.get("sample_sheet_summary", {})
    runinfo = validation.get("runinfo", {})
    lines = [
        "# BCL To FASTQ Run Summary",
        "",
        f"Status: `{status}`",
        f"Converter: `{converter or 'not installed'}`",
        f"Run folder: `{validation.get('run_folder')}`",
        f"Samples parsed: `{sheet.get('sample_count', 0)}`",
        f"Read structure: `{runinfo.get('reads', [])}`",
    ]
    if runtime_preflight.get("uses_docker_wrapper"):
        lines.extend(
            [
                f"Docker-backed wrapper: `{runtime_preflight.get('converter_path')}`",
                f"Docker daemon ready: `{runtime_preflight.get('docker_daemon_ok')}`",
            ]
        )
    if report_bundle:
        lines.extend(
            [
                "",
                "## Demux QC",
                "",
                f"Assessment: `{report_bundle['assessment']}`",
                f"Assigned reads: `{report_bundle['assigned_reads']}` (`{report_bundle['assigned_fraction']:.2%}`)",
                f"Undetermined reads: `{report_bundle['undetermined_reads']}` (`{report_bundle['undetermined_fraction']:.2%}`)",
            ]
        )
        if report_bundle["issues"]:
            lines.extend(f"- {issue}" for issue in report_bundle["issues"])
        top_unknown = report_bundle["top_unknown_barcodes"][:3]
        if top_unknown:
            lines.extend(["", "Top unknown barcodes:"])
            lines.extend(
                f"- {item['index']}-{item['index2']}: {item['reads']} reads ({item['fraction_of_all_reads']:.2%} of all reads)"
                for item in top_unknown
                if item["reads"] is not None and item["fraction_of_all_reads"] is not None
            )
        lines.extend(["", "FASTQ outputs:"])
        lines.extend(
            f"- `{Path(item['path']).name}`: {item['read_pairs']} read pairs, {item['bytes']} bytes"
            for item in report_bundle["fastq_outputs"]
        )
    lines.extend(
        [
            "",
            "## Key Artifacts",
            "",
            "- `validation/runinfo.json`",
            "- `validation/samplesheet_summary.json`",
            "- `qc/demux_qc_summary.json` when conversion succeeds",
            "- `logs/bcl_conversion.log` when conversion executes",
            "- `run_manifest.json` and `artifact_index.json`",
            "",
        ]
    )
    if validation.get("errors"):
        lines.extend(["## Blockers", ""])
        lines.extend(f"- {error}" for error in validation["errors"])
    combined_warnings = [*validation.get("warnings", []), *runtime_preflight.get("warnings", [])]
    if combined_warnings:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in combined_warnings)
    write_text(run_dir / "summary.md", "\n".join(lines) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-folder", type=Path, required=True)
    parser.add_argument("--sample-sheet", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--outdir", type=Path)
    parser.add_argument("--run-id", default=slug_timestamp("bcl-to-fastq"))
    parser.add_argument("--converter", choices=["bcl-convert", "bcl2fastq"])
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=86400)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_dir = (args.outdir or (DEFAULT_RUN_ROOT / args.run_id)).expanduser().resolve()
    if run_dir.exists():
        raise FileExistsError(f"run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True)
    (run_dir / "logs").mkdir(parents=True, exist_ok=True)

    validation = validate_inputs(args)
    converter = select_converter(args)
    runtime_preflight = converter_runtime_preflight(converter, args)
    tool_status = tool_preflight([], optional=["bcl-convert", "bcl2fastq"])
    if args.execute and converter is None:
        tool_status["ok"] = False
        tool_status["missing_required"] = ["bcl-convert or bcl2fastq"]
    tool_status["runtime"] = runtime_preflight
    if runtime_preflight.get("errors"):
        tool_status["ok"] = False
        tool_status["runtime_errors"] = runtime_preflight["errors"]

    write_json(
        run_dir / "config.json",
        {
            "run_folder": str(args.run_folder.expanduser().resolve()),
            "sample_sheet": str(args.sample_sheet.expanduser().resolve()),
            "output_directory": str(args.output_directory.expanduser().resolve()),
        },
    )
    write_json(
        run_dir / "validation" / "input_summary.json",
        {
            "run_folder": validation["run_folder"],
            "sample_sheet": validation["sample_sheet"],
            "output_directory": validation["output_directory"],
        },
    )
    write_json(run_dir / "validation" / "validation_summary.json", validation)
    write_json(run_dir / "validation" / "runtime_preflight.json", runtime_preflight)
    write_json(run_dir / "validation" / "runinfo.json", validation["runinfo"])
    write_json(run_dir / "validation" / "runparameters.json", validation["runparameters"])
    write_json(
        run_dir / "validation" / "samplesheet_summary.json", validation["sample_sheet_summary"]
    )
    write_json(run_dir / "validation" / "tool_preflight.json", tool_status)
    write_commands(run_dir, args, converter)
    write_json(
        run_dir / "versions" / "software_versions.json",
        software_versions(
            {"bcl-convert": ["bcl-convert", "--version"], "bcl2fastq": ["bcl2fastq", "--version"]}
        ),
    )

    dry_run = {
        "ok": validation["ok"] and (converter is not None or not args.execute),
        "detail": "run folder and sample sheet validation completed",
    }
    write_json(run_dir / "logs" / "validation_dry_run.json", dry_run)
    execution = None
    report_bundle = None
    status = "blocked" if not dry_run["ok"] else "validated"
    if args.execute and validation["ok"] and converter:
        execution = execute_conversion(run_dir, args, converter, runtime_preflight)
        status = "completed" if execution.get("ok") else "failed"
        if execution.get("ok"):
            report_bundle = parse_report_bundle(args.output_directory.expanduser().resolve())
            if report_bundle:
                write_json(run_dir / "qc" / "demux_qc_summary.json", report_bundle)
    elif args.execute and not converter:
        execution = {"ok": False, "reason": "bcl-convert or bcl2fastq is not installed"}
        status = "blocked"

    write_standard_manifest(
        run_dir,
        run_id=args.run_id,
        lane="bcl_to_fastq",
        workflow="local_bcl_convert_or_bcl2fastq",
        status=status,
        execute_requested=args.execute,
        validation=validation,
        tool_preflight_result=tool_status,
        dry_run=dry_run,
        execution=execution,
        inputs={"run_folder": validation["run_folder"], "sample_sheet": validation["sample_sheet"]},
        outputs={
            "output_directory": validation["output_directory"],
            "conversion_logs": "logs/bcl_conversion.log",
        },
        method={
            "converter": converter,
            "converter_selection": "bcl-convert preferred, bcl2fastq fallback",
        },
        review_bundle={"demux_qc": report_bundle} if report_bundle else {},
    )
    write_summary(run_dir, status, validation, converter, runtime_preflight, report_bundle)
    extra_roots = (
        {"output_directory": args.output_directory.expanduser().resolve()}
        if report_bundle
        else None
    )
    write_json(
        run_dir / "artifact_index.json", build_artifact_index(run_dir, extra_roots=extra_roots)
    )
    print(run_dir)
    return 1 if status in {"blocked", "failed"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
