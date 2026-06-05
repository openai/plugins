#!/usr/bin/env python3
"""Small visualization helpers for plugin-owned NGS runners."""

from __future__ import annotations

import csv
import html
import json
import os
import shlex
import shutil
import socket
import subprocess
import sys
import textwrap
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


def _json_default(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    return str(value)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, default=_json_default) + "\n", encoding="utf-8"
    )


def rel_link(index_dir: Path, target: Path) -> str:
    try:
        return os.path.relpath(target, index_dir)
    except ValueError:
        return str(target)


def _is_url(value: str) -> bool:
    return value.startswith(("http://", "https://"))


def localhost_url_for_path(
    relative_path: str | Path, *, port: int = 8765, host: str = "127.0.0.1"
) -> str:
    rel = Path(relative_path).as_posix().lstrip("/")
    return f"http://{host}:{port}/{rel}"


def preferred_http_server_python() -> str:
    system_python = Path("/usr/bin/python3")
    if system_python.exists():
        return str(system_python)
    return shutil.which("python3") or sys.executable or "python3"


def reachable_localhost_url_for_path(
    relative_path: str | Path,
    *,
    port: int = 8765,
    host: str = "127.0.0.1",
    timeout_seconds: float = 0.75,
) -> str | None:
    url = localhost_url_for_path(relative_path, port=port, host=host)
    request = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:  # noqa: S310
            if response.status == 200:
                return url
    except (urllib.error.URLError, TimeoutError, OSError):
        return None
    return None


def write_localhost_launch_hint(
    run_dir: Path,
    *,
    report_entries: list[tuple[str, str | Path]],
    port: int = 8765,
    host: str = "127.0.0.1",
) -> Path:
    python_cmd = preferred_http_server_python()
    lines = [
        f"cd {run_dir}",
        f"{python_cmd} -m http.server {port} --bind {host}",
        "",
    ]
    reported = 0
    for label, rel_path in report_entries:
        candidate = run_dir / rel_path
        if candidate.exists():
            lines.append(f"{label}: {localhost_url_for_path(rel_path, port=port, host=host)}")
            reported += 1
    if not reported:
        lines.append("No MultiQC reports were generated for this run.")
    path = run_dir / "visualizations" / "localhost_launch_hint.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def artifact_entry(
    *,
    artifact_id: str,
    title: str,
    path: str | Path | None,
    kind: str,
    status: str,
    description: str,
    source: str | None = None,
) -> dict[str, Any]:
    return {
        "id": artifact_id,
        "title": title,
        "path": str(path) if path else None,
        "kind": kind,
        "status": status,
        "description": description,
        "source": source,
    }


def copy_visual_asset(source: Path, dest: Path) -> Path | None:
    if not source.exists():
        return None
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)
    return dest


def find_free_localhost_port(
    *, host: str = "127.0.0.1", start_port: int = 2719, max_tries: int = 50
) -> int:
    for port in range(start_port, start_port + max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind((host, port))
            except OSError:
                continue
            return port
    raise RuntimeError(f"Unable to find a free localhost port starting at {start_port}")


def wait_for_http_ready(url: str, *, timeout_seconds: float = 12.0) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1.5) as response:  # noqa: S310
                if response.status < 500:
                    return True
        except (urllib.error.URLError, TimeoutError, OSError):
            time.sleep(0.4)
    return False


def launch_marimo_review_app(
    *,
    notebook_path: Path,
    run_dir: Path,
    host: str = "127.0.0.1",
    start_port: int = 2719,
    python_executable: str | None = None,
) -> dict[str, Any]:
    runtime_root = run_dir / ".runtime" / "marimo"
    logs_dir = run_dir / "logs"
    runtime_root.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    xdg_cache_home = runtime_root / "xdg_cache"
    xdg_state_home = runtime_root / "xdg_state"
    xdg_cache_home.mkdir(parents=True, exist_ok=True)
    xdg_state_home.mkdir(parents=True, exist_ok=True)
    port = find_free_localhost_port(host=host, start_port=start_port)
    url = f"http://{host}:{port}/"
    log_path = logs_dir / "marimo_server.log"
    env = os.environ.copy()
    env["XDG_CACHE_HOME"] = str(xdg_cache_home)
    env["XDG_STATE_HOME"] = str(xdg_state_home)
    cmd = [
        python_executable or sys.executable,
        "-m",
        "marimo",
        "run",
        str(notebook_path),
        "--host",
        host,
        "--port",
        str(port),
        "--headless",
        "--no-token",
    ]
    with log_path.open("a", encoding="utf-8") as log_handle:
        process = subprocess.Popen(  # noqa: S603
            cmd,
            cwd=run_dir,
            env=env,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    ready = wait_for_http_ready(url, timeout_seconds=12.0)
    result = {
        "ok": ready,
        "url": url,
        "port": port,
        "pid": process.pid,
        "log_path": str(log_path),
        "command": cmd,
        "xdg_cache_home": str(xdg_cache_home),
        "xdg_state_home": str(xdg_state_home),
    }
    if not ready:
        result["error"] = "Marimo review app did not become ready before timeout."
    return result


def write_visualization_index(
    run_dir: Path,
    *,
    title: str,
    description: str,
    entries: list[dict[str, Any]],
    notes: list[str] | None = None,
    analysis_intent: str = "real_analysis",
    provenance_summary: dict[str, Any] | None = None,
) -> Path:
    index_dir = run_dir / "visualizations"
    index_dir.mkdir(parents=True, exist_ok=True)
    notes = notes or []
    manifest_path = index_dir / "visualization_manifest.json"
    write_json(
        manifest_path,
        {
            "title": title,
            "description": description,
            "analysis_intent": analysis_intent,
            "provenance_summary": provenance_summary or {},
            "entries": entries,
            "notes": notes,
        },
    )

    rows = []
    for entry in entries:
        target = entry.get("path")
        if target:
            target_str = str(target)
            if _is_url(target_str):
                href = target_str
            else:
                href = (
                    rel_link(index_dir, run_dir / target)
                    if not Path(target).is_absolute()
                    else rel_link(index_dir, Path(target))
                )
            link = f'<a href="{html.escape(href)}">{html.escape(str(target))}</a>'
        else:
            link = ""
        rows.append(
            "<tr>"
            f"<td>{html.escape(entry.get('title', ''))}</td>"
            f'<td><span class="status {html.escape(entry.get("status", "unknown"))}">{html.escape(entry.get("status", "unknown"))}</span></td>'
            f"<td>{html.escape(entry.get('kind', ''))}</td>"
            f"<td>{link}</td>"
            f"<td>{html.escape(entry.get('description', ''))}</td>"
            "</tr>"
        )
    note_items = "\n".join(f"<li>{html.escape(note)}</li>" for note in notes)
    body = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(title)}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; color: #202124; }}
    h1 {{ margin-bottom: 0.25rem; }}
    p {{ max-width: 920px; line-height: 1.45; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 1.5rem; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #ddd; padding: 10px 8px; text-align: left; vertical-align: top; }}
    th {{ background: #f6f8fa; }}
    .status {{ border-radius: 4px; padding: 2px 6px; background: #eef2f7; }}
    .created {{ background: #e6f4ea; }}
    .not_available {{ background: #fff4ce; }}
    .blocked {{ background: #fce8e6; }}
    .notes {{ margin-top: 1.5rem; }}
    code {{ background: #f6f8fa; padding: 1px 4px; border-radius: 4px; }}
  </style>
</head>
<body>
  <h1>{html.escape(title)}</h1>
  <p>{html.escape(description)}</p>
  <p><strong>Analysis intent:</strong> {html.escape(analysis_intent)}</p>
  <table>
    <thead><tr><th>Artifact</th><th>Status</th><th>Kind</th><th>Path</th><th>Description</th></tr></thead>
    <tbody>
      {"".join(rows)}
    </tbody>
  </table>
  <div class="notes">
    <h2>Notes</h2>
    <ul>{note_items}</ul>
  </div>
</body>
</html>
"""
    index_path = index_dir / "index.html"
    index_path.write_text(body, encoding="utf-8")
    return index_path


def _read_tsv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8", errors="replace") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = [{key: (value or "").strip() for key, value in row.items()} for row in reader]
        return list(reader.fieldnames or []), rows


def _render_html_table(
    headers: list[str], rows: list[dict[str, str]], *, limit: int | None = None
) -> str:
    if not headers:
        return "<p>No table data were available.</p>"
    limited_rows = rows[:limit] if limit is not None else rows
    head_html = "".join(f"<th>{html.escape(column)}</th>" for column in headers)
    row_html = []
    for row in limited_rows:
        row_html.append(
            "<tr>"
            + "".join(f"<td>{html.escape(str(row.get(column, '')))}</td>" for column in headers)
            + "</tr>"
        )
    return (
        '<div class="table-wrap">'
        "<table>"
        f"<thead><tr>{head_html}</tr></thead>"
        f"<tbody>{''.join(row_html)}</tbody>"
        "</table>"
        "</div>"
    )


def _summarize_status_columns(
    rows: list[dict[str, str]], headers: list[str]
) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    valid = {"pass", "warn", "fail"}
    for column in headers:
        counts = {"pass": 0, "warn": 0, "fail": 0}
        for row in rows:
            value = (row.get(column) or "").strip().lower()
            if value in valid:
                counts[value] += 1
        if any(counts.values()):
            summaries.append({"module": column, **counts})
    return sorted(summaries, key=lambda item: (-item["fail"], -item["warn"], item["module"]))


def write_multiqc_browser_helper(
    run_dir: Path,
    *,
    report_path: str | Path,
    title: str,
    localhost_port: int = 8765,
) -> Path | None:
    report_rel = Path(report_path)
    report_abs = report_rel if report_rel.is_absolute() else run_dir / report_rel
    if not report_abs.exists():
        return None

    multiqc_dir = report_abs.parent
    helper_path = multiqc_dir / "multiqc_browser_helper.html"
    data_dir = multiqc_dir / "multiqc_data"
    general_stats_headers: list[str] = []
    general_stats_rows: list[dict[str, str]] = []
    if (data_dir / "multiqc_general_stats.txt").exists():
        general_stats_headers, general_stats_rows = _read_tsv_rows(
            data_dir / "multiqc_general_stats.txt"
        )

    fastqc_headers: list[str] = []
    fastqc_rows: list[dict[str, str]] = []
    if (data_dir / "multiqc_fastqc.txt").exists():
        fastqc_headers, fastqc_rows = _read_tsv_rows(data_dir / "multiqc_fastqc.txt")
    module_summaries = _summarize_status_columns(fastqc_rows, fastqc_headers) if fastqc_rows else []

    try:
        report_rel_to_run_dir = report_abs.relative_to(run_dir)
    except ValueError:
        report_rel_to_run_dir = Path(report_abs.name)
    localhost_url = reachable_localhost_url_for_path(report_rel_to_run_dir, port=localhost_port)
    python_cmd = preferred_http_server_python()
    serve_cmd = "\n".join(
        [
            f"cd {shlex.quote(str(run_dir))}",
            f"{python_cmd} -m http.server {localhost_port} --bind 127.0.0.1",
        ]
    )
    localhost_link_html = (
        f'<a href="{html.escape(localhost_url)}">Open full MultiQC over localhost</a>'
        if localhost_url
        else "<span>The localhost review URL is not live yet. Start the server below, then reload this helper.</span>"
    )
    body = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(title)}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; color: #202124; }}
    h1, h2 {{ margin-bottom: 0.5rem; }}
    p {{ max-width: 960px; line-height: 1.45; }}
    .alert {{ padding: 16px; border-radius: 8px; background: #fff4ce; margin: 18px 0; }}
    .links a {{ display: inline-block; margin-right: 14px; margin-bottom: 8px; }}
    .table-wrap {{ overflow-x: auto; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #ddd; padding: 10px 8px; text-align: left; vertical-align: top; white-space: nowrap; }}
    th {{ background: #f6f8fa; }}
    code, pre {{ background: #f6f8fa; border-radius: 6px; }}
    code {{ padding: 2px 6px; }}
    pre {{ padding: 12px; overflow-x: auto; }}
    .pill {{ border-radius: 999px; padding: 2px 8px; }}
    .pass {{ background: #e6f4ea; }}
    .warn {{ background: #fff4ce; }}
    .fail {{ background: #fce8e6; }}
    .caption {{ color: #5f6368; font-size: 13px; }}
  </style>
</head>
<body>
  <h1>{html.escape(title)}</h1>
  <p>This helper is a browser-safe review surface for MultiQC outputs. The raw interactive MultiQC HTML can stall under <code>file://</code> in the Codex in-app browser even when the report itself is valid.</p>
  <div class="alert">
    <strong>Recommended path:</strong> use this helper for quick review. If you need the full interactive report, start the local HTTP server below and then refresh this page.
  </div>
  <div class="links">
    {localhost_link_html}
    <a href="{html.escape(report_abs.name)}">Open raw MultiQC HTML</a>
  </div>

  <h2>Serve Locally</h2>
  <p class="caption">Run this in a terminal if the full interactive report is stuck on “Loading report..”:</p>
  <pre>{html.escape(serve_cmd)}</pre>

  <h2>General Statistics</h2>
  <p class="caption">Embedded from <code>multiqc_data/multiqc_general_stats.txt</code>. This table is self-contained and does not depend on the raw MultiQC app booting correctly.</p>
  {_render_html_table(general_stats_headers, general_stats_rows, limit=50)}

  <h2>FastQC Module Status Summary</h2>
  <p class="caption">Aggregated from the embedded <code>multiqc_fastqc.txt</code> table when present.</p>
  {_render_html_table(["module", "fail", "warn", "pass"], module_summaries, limit=50) if module_summaries else "<p>No FastQC module-status summary was available for this report.</p>"}
</body>
</html>
"""
    helper_path.write_text(body, encoding="utf-8")
    return helper_path


def write_marimo_review_notebook(
    notebook_path: Path,
    *,
    title: str,
    run_dir: Path,
    image_items: list[tuple[str, str]],
    table_items: list[tuple[str, str]],
    object_items: list[tuple[str, str]] | None = None,
) -> Path:
    object_items = object_items or []
    notebook_path.parent.mkdir(parents=True, exist_ok=True)
    image_literal = repr(image_items)
    table_literal = repr(table_items)
    object_literal = repr(object_items)
    source = f'''import marimo

__generated_with = "0.13.0"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    from pathlib import Path
    import pandas as pd
    ROOT = Path({str(run_dir)!r})
    return ROOT, Path, mo, pd


@app.cell
def _(ROOT, mo):
    mo.md("""
# {title}

Run directory: `{{}}`
""".format(ROOT))
    return


@app.cell
def _(ROOT, mo):
    _items = []
    for _title, _rel_path in {image_literal}:
        _path = ROOT / _rel_path
        if _path.exists():
            _items.append(mo.md(f"## {{_title}}"))
            _items.append(mo.image(src=str(_path)))
        else:
            _items.append(mo.md(f"## {{_title}}\\nMissing: `{{_rel_path}}`"))
    mo.vstack(_items)
    return


@app.cell
def _(ROOT, mo, pd):
    _items = []
    for _title, _rel_path in {table_literal}:
        _path = ROOT / _rel_path
        if _path.exists():
            _items.append(mo.md(f"## {{_title}}"))
            _sep = "\\t" if _path.suffix in {{".tsv", ".tab"}} else ","
            _items.append(mo.ui.table(pd.read_csv(_path, sep=_sep).head(200)))
        else:
            _items.append(mo.md(f"## {{_title}}\\nMissing: `{{_rel_path}}`"))
    mo.vstack(_items)
    return


@app.cell
def _(ROOT, mo):
    _lines = ["## Analysis Objects"]
    for _title, _rel_path in {object_literal}:
        _path = ROOT / _rel_path
        _state = "present" if _path.exists() else "missing"
        _lines.append(f"- {{_title}}: `{{_rel_path}}` ({{_state}})")
    mo.md("\\n".join(_lines))
    return


if __name__ == "__main__":
    app.run()
'''
    notebook_path.write_text(textwrap.dedent(source), encoding="utf-8")
    return notebook_path


def discover_vcf_artifacts(
    run_dir: Path,
    *,
    search_roots: list[str] | None = None,
) -> list[tuple[str, str]]:
    """Return display labels and run-relative paths for output VCF/gVCF artifacts."""
    search_roots = search_roots or ["variants", "gvcf", "joint", "results"]
    seen: set[str] = set()
    items: list[tuple[str, str]] = []
    for root_name in search_roots:
        root = run_dir / root_name
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.vcf.gz")):
            rel = path.relative_to(run_dir).as_posix()
            if rel in seen:
                continue
            seen.add(rel)
            label = rel
            if rel.startswith("variants/"):
                label = f"Variant VCF: {path.name}"
            elif rel.startswith("gvcf/"):
                label = f"GVCF: {path.name}"
            elif rel.startswith("joint/"):
                label = f"Joint VCF: {path.name}"
            items.append((label, rel))
    return items


def write_vcf_review_notebook(
    notebook_path: Path,
    *,
    title: str,
    run_dir: Path,
    vcf_items: list[tuple[str, str]],
    table_items: list[tuple[str, str]] | None = None,
    object_items: list[tuple[str, str]] | None = None,
) -> Path:
    """Write a generic Marimo notebook that previews discovered VCF artifacts."""
    table_items = table_items or []
    object_items = object_items or []
    notebook_path.parent.mkdir(parents=True, exist_ok=True)
    vcf_literal = repr(vcf_items)
    table_literal = repr(table_items)
    object_literal = repr(object_items)
    source = f'''import marimo

__generated_with = "0.23.4"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import subprocess
    from pathlib import Path
    ROOT = Path({str(run_dir)!r})
    return ROOT, Path, mo, pd, subprocess


@app.cell
def _(ROOT, mo):
    mo.md("""
# {title}

Run directory: `{{}}`
""".format(ROOT))
    return


@app.cell
def _(mo):
    _vcf_items = {vcf_literal}
    if not _vcf_items:
        selector = None
        _component = mo.md("## VCF Artifacts\\nNo `.vcf.gz` artifacts were discovered in the run envelope.")
    else:
        _labels = [item[0] for item in _vcf_items]
        selector = mo.ui.dropdown(options=_labels, value=_labels[0], label="VCF artifact", full_width=False)
        _component = mo.hstack([selector], justify="start")
    _component
    return (selector,)


@app.cell
def _(ROOT, mo, pd, subprocess):
    _rows = []
    for _label, _rel_path in {vcf_literal}:
        _abs = ROOT / _rel_path
        _row = {{"artifact": _label, "path": _rel_path}}
        if _abs.exists():
            _result = subprocess.run(
                ["bcftools", "stats", str(_abs)],
                check=True,
                capture_output=True,
                text=True,
            )
            for _line in _result.stdout.splitlines():
                if not _line.startswith("SN\\t"):
                    continue
                _, _, _key, _value = _line.split("\\t", 3)
                if _key == "number of records:":
                    _row["record_count"] = int(_value)
                elif _key == "number of SNPs:":
                    _row["snp_count"] = int(_value)
                elif _key == "number of indels:":
                    _row["indel_count"] = int(_value)
        else:
            _row["error"] = "missing VCF"
        _rows.append(_row)
    _df = pd.DataFrame(_rows).fillna("")
    mo.vstack([mo.md("## bcftools stats summary"), mo.ui.table(_df)])
    return


@app.cell
def _(ROOT, mo, pd):
    _items = []
    for _title, _rel_path in {table_literal}:
        _path = ROOT / _rel_path
        if _path.exists():
            _items.append(mo.md(f"## {{_title}}"))
            _sep = "\\t" if _path.suffix in {{".tsv", ".tab"}} else ","
            _items.append(mo.ui.table(pd.read_csv(_path, sep=_sep).head(200)))
        else:
            _items.append(mo.md(f"## {{_title}}\\nMissing: `{{_rel_path}}`"))
    if _items:
        _component = mo.vstack(_items)
    else:
        _component = mo.md("## Tables\\nNo table artifacts were configured for this review.")
    _component
    return


@app.cell
def _(ROOT, mo, subprocess, selector):
    _vcf_items = {vcf_literal}
    if not _vcf_items or selector is None:
        _component = mo.md("## Selected VCF\\nNo selectable VCF artifacts were discovered.")
    else:
        _selected_label = selector.value
        _selected_rel = next(_rel for _label, _rel in _vcf_items if _label == _selected_label)
        _selected_abs = ROOT / _selected_rel
        _header = subprocess.run(
            ["bcftools", "view", "-h", str(_selected_abs)],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        _body = subprocess.run(
            ["bcftools", "view", "-H", str(_selected_abs)],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        _header_preview = "\\n".join(_header[-20:])
        _body_preview = "\\n".join(_body[:25]) if _body else "# no variant rows"
        _component = mo.vstack(
            [
                mo.md(f"## Selected VCF: `{{_selected_label}}`"),
                mo.md(f"`{{_selected_rel}}`"),
                mo.md("### Header preview"),
                mo.md(f"```text\\n{{_header_preview}}\\n```"),
                mo.md("### Variant rows"),
                mo.md(f"```text\\n{{_body_preview}}\\n```"),
            ]
        )
    _component
    return


@app.cell
def _(ROOT, mo):
    _lines = ["## Analysis Objects"]
    for _title, _rel_path in {object_literal}:
        _path = ROOT / _rel_path
        _state = "present" if _path.exists() else "missing"
        _lines.append(f"- {{_title}}: `{{_rel_path}}` ({{_state}})")
    mo.md("\\n".join(_lines))
    return


if __name__ == "__main__":
    app.run()
'''
    notebook_path.write_text(textwrap.dedent(source), encoding="utf-8")
    return notebook_path


def add_vcf_review_notebook_entry(
    run_dir: Path,
    entries: list[dict[str, Any]],
    *,
    title: str,
    notebook_filename: str = "vcf_review.marimo.py",
    table_items: list[tuple[str, str]] | None = None,
    object_items: list[tuple[str, str]] | None = None,
) -> dict[str, str]:
    """Append a generic VCF review notebook artifact entry when VCF outputs exist."""
    vcf_items = discover_vcf_artifacts(run_dir)
    if not vcf_items:
        entries.append(
            artifact_entry(
                artifact_id="vcf_review_notebook",
                title="VCF Review Notebook",
                path=None,
                kind="notebook",
                status="not_available",
                description="No output VCF/gVCF artifacts were present in this run, so the generic VCF review notebook was not created.",
            )
        )
        return {}
    notebook_path = write_vcf_review_notebook(
        run_dir / "notebooks" / notebook_filename,
        title=title,
        run_dir=run_dir,
        vcf_items=vcf_items,
        table_items=table_items,
        object_items=object_items,
    )
    rel = notebook_path.relative_to(run_dir)
    entries.append(
        artifact_entry(
            artifact_id="vcf_review_notebook",
            title="VCF Review Notebook",
            path=rel,
            kind="notebook",
            status="created",
            description="Generic Marimo notebook that prepopulates any VCF/gVCF artifacts found in the run envelope.",
        )
    )
    return {"review_notebook": str(rel)}
