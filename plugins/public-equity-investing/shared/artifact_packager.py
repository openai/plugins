"""Shared artifact packaging helpers for Public Equity Investing skills.

The helpers enforce the Public Equity Investing output surface: DOCX, XLSX,
HTML, and chat are the normal reader-facing artifacts, while JSON, CSV, logs,
manifests, and support notes remain support material unless explicitly requested.
"""

from __future__ import annotations

import html
import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

MANIFEST_VERSION = "1.0"
SUPPORT_PRIMARY_EXTENSIONS = {".csv", ".json", ".md", ".markdown", ".log", ".txt"}
HTML_MODES = {"html_dashboard", "html_report"}
WORKBOOK_MODES = {"workbook", "banker_formula_workbook", "xlsx_update_copy", "xlsx_control_pack"}
PRIMARY_EXEMPT_MODES = {"blocked", "chat_only", "support_only"}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _string_path(path: str | Path | None) -> str:
    return "" if path is None else str(path)


def artifact_type_from_path(path: str | Path) -> str:
    suffix = Path(path).suffix.lower()
    return {
        ".xlsx": "xlsx",
        ".xlsm": "xlsm",
        ".html": "html",
        ".htm": "html",
        ".pptx": "native_deck",
        ".docx": "native_document",
        ".csv": "csv",
        ".json": "json",
        ".md": "markdown",
        ".markdown": "markdown",
        ".log": "log",
        ".txt": "text",
    }.get(suffix, "file")


def artifact_item(
    path: str | Path,
    role: str,
    artifact_type: str | None = None,
    description: str = "",
    user_visible_default: bool = False,
    contains_new_analysis: bool = False,
    support_reason: str = "",
    user_requested_machine_readable: bool = False,
) -> dict[str, Any]:
    return {
        "path": _string_path(path),
        "role": role,
        "artifact_type": artifact_type or artifact_type_from_path(path),
        "description": description,
        "user_visible_default": bool(user_visible_default),
        "contains_new_analysis": bool(contains_new_analysis),
        "support_reason": support_reason,
        "user_requested_machine_readable": bool(user_requested_machine_readable),
    }


def support_dir(output_dir: str | Path) -> Path:
    path = Path(output_dir) / "support"
    path.mkdir(parents=True, exist_ok=True)
    return path


def logs_dir(output_dir: str | Path) -> Path:
    path = Path(output_dir) / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def validate_artifact_manifest(manifest: Mapping[str, Any]) -> None:
    errors: list[str] = []
    primary = str(manifest.get("primary_human_deliverable") or "")
    mode = str(manifest.get("artifact_mode") or "")
    status = manifest.get("blocked_or_partial_status")
    status_value = status.get("status") if isinstance(status, Mapping) else ""
    primary_exempt = mode in PRIMARY_EXEMPT_MODES or status_value in {"blocked", "support_only"}

    for field in [
        "manifest_version",
        "plugin",
        "skill",
        "artifact_mode",
        "output_dir",
        "first_read",
        "human_deliverables",
        "companion_deliverables",
        "support_artifacts",
        "agent_artifacts",
        "support_artifacts_user_visible_default",
        "blocked_or_partial_status",
        "final_response_guidance",
        "discipline_note",
    ]:
        if field not in manifest:
            errors.append(f"missing required field: {field}")
    if manifest.get("manifest_version") != MANIFEST_VERSION:
        errors.append("manifest_version must be 1.0")
    if not primary and not primary_exempt:
        errors.append(
            "primary_human_deliverable is required unless output is blocked/chat/support-only"
        )
    if primary:
        suffix = Path(primary).suffix.lower()
        user_requested = bool(manifest.get("user_requested_machine_readable"))
        if suffix in SUPPORT_PRIMARY_EXTENSIONS and not user_requested:
            errors.append(
                "support-format files cannot be primary unless user_requested_machine_readable is true"
            )
        if mode in HTML_MODES and suffix not in {".html", ".htm"}:
            errors.append("HTML modes require an .html primary deliverable")
        if mode in WORKBOOK_MODES and suffix not in {".xlsx", ".xlsm"}:
            errors.append("workbook modes require an .xlsx or .xlsm primary deliverable")
    for item in manifest.get("support_artifacts", []) or []:
        if not isinstance(item, Mapping):
            errors.append("support_artifacts entries must be objects")
            continue
        if not item.get("support_reason"):
            errors.append(f"support artifact lacks support_reason: {item.get('path', '<unknown>')}")
        if item.get("user_visible_default") is True:
            errors.append(
                f"support artifact cannot be user_visible_default=true: {item.get('path', '<unknown>')}"
            )
    if errors:
        raise ValueError("; ".join(errors))


def write_artifact_manifest(
    output_dir: str | Path,
    skill: str,
    artifact_mode: str,
    primary_human_deliverable: str | Path | None = None,
    *,
    human_deliverables: Sequence[Mapping[str, Any]] | None = None,
    companion_deliverables: Sequence[Mapping[str, Any]] | None = None,
    support_artifacts: Sequence[Mapping[str, Any]] | None = None,
    agent_artifacts: Sequence[Mapping[str, Any]] | None = None,
    first_read: Mapping[str, Any] | None = None,
    blocked_or_partial_status: Mapping[str, Any] | None = None,
    final_response_guidance: Mapping[str, Any] | None = None,
    user_requested_machine_readable: bool = False,
    manifest_name: str = "manifest.json",
    extra: Mapping[str, Any] | None = None,
    validate: bool = True,
) -> dict[str, Any]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    manifest_path = out / manifest_name
    primary = _string_path(primary_human_deliverable)
    humans = list(human_deliverables or [])
    if primary and not humans:
        humans.append(
            artifact_item(
                primary,
                "human_deliverable",
                description="Primary Public Equity Investing reader-facing deliverable.",
                user_visible_default=True,
                contains_new_analysis=True,
                user_requested_machine_readable=user_requested_machine_readable,
            )
        )
    agents = list(agent_artifacts or [])
    if not any(
        str(item.get("path", "")).endswith(manifest_name)
        for item in agents
        if isinstance(item, Mapping)
    ):
        agents.append(
            artifact_item(
                manifest_path,
                "agent_artifact",
                "json",
                "Artifact manifest used to preserve deliverable hierarchy.",
                False,
                False,
                "Manifest is audit/routing support, not the Public Equity Investing deliverable.",
            )
        )
    status = dict(
        blocked_or_partial_status
        or {"status": "complete" if primary else "support_only", "reason": "", "missing_inputs": []}
    )
    manifest: dict[str, Any] = {
        "manifest_version": MANIFEST_VERSION,
        "plugin": "public-equity-investing",
        "skill": skill,
        "artifact_mode": artifact_mode,
        "output_dir": str(out),
        "first_read": dict(
            first_read
            or {
                "path": primary,
                "role": "primary_human_deliverable",
                "why": "Open this first; support files are audit/import material.",
            }
        ),
        "primary_human_deliverable": primary,
        "human_deliverables": humans,
        "companion_deliverables": list(companion_deliverables or []),
        "support_artifacts": list(support_artifacts or []),
        "agent_artifacts": agents,
        "support_artifacts_user_visible_default": False,
        "blocked_or_partial_status": status,
        "final_response_guidance": dict(
            final_response_guidance
            or {
                "lead_with": "primary_human_deliverable",
                "mention_support_artifacts": "only_briefly_unless_requested",
            }
        ),
        "discipline_note": "Use the DOCX/HTML/XLSX human deliverable as the main output; JSON, CSV, logs, manifests, and support notes are audit support unless requested.",
        "created_at": utc_now_iso(),
        "user_requested_machine_readable": bool(user_requested_machine_readable),
    }
    if extra:
        manifest.update(dict(extra))
    if validate:
        validate_artifact_manifest(manifest)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def _column_name(index: int) -> str:
    index += 1
    name = ""
    while index:
        index, rem = divmod(index - 1, 26)
        name = chr(65 + rem) + name
    return name


def _sheet_name(name: str, used: set[str]) -> str:
    cleaned = re.sub(r"[\[\]:*?/\\]", "_", str(name)).strip() or "Sheet"
    cleaned = cleaned[:31]
    base = cleaned
    suffix = 1
    while cleaned in used:
        tail = f"_{suffix}"
        cleaned = f"{base[: 31 - len(tail)]}{tail}"
        suffix += 1
    used.add(cleaned)
    return cleaned


def _sheet_xml(rows: Sequence[Sequence[Any]]) -> str:
    parts = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>']
    parts.append(
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'
    )
    for r_idx, row in enumerate(rows, start=1):
        parts.append(f'<row r="{r_idx}">')
        for c_idx, value in enumerate(row):
            if value is None:
                continue
            ref = f"{_column_name(c_idx)}{r_idx}"
            if isinstance(value, bool):
                parts.append(f'<c r="{ref}" t="b"><v>{1 if value else 0}</v></c>')
            elif isinstance(value, (int, float)) and not isinstance(value, bool):
                parts.append(f'<c r="{ref}"><v>{value}</v></c>')
            else:
                parts.append(
                    f'<c r="{ref}" t="inlineStr"><is><t>{html.escape(str(value))}</t></is></c>'
                )
        parts.append("</row>")
    parts.append("</sheetData></worksheet>")
    return "".join(parts)


def write_simple_xlsx_from_tables(
    path: str | Path, sheets: Mapping[str, Sequence[Sequence[Any]]]
) -> Path:
    workbook = Path(path)
    workbook.parent.mkdir(parents=True, exist_ok=True)
    used: set[str] = set()
    normalized = [(_sheet_name(name, used), list(rows)) for name, rows in sheets.items()]
    if not normalized:
        normalized = [("Cover", [["Generated workbook", "No tabular data supplied."]])]
    if normalized[0][0] != "Cover":
        raise ValueError("first sheet must be Cover")
    content_types = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>']
    content_types.append(
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    )
    content_types.append(
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    )
    content_types.append('<Default Extension="xml" ContentType="application/xml"/>')
    content_types.append(
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
    )
    content_types.append(
        '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
    )
    for idx in range(1, len(normalized) + 1):
        content_types.append(
            f'<Override PartName="/xl/worksheets/sheet{idx}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        )
    content_types.append("</Types>")
    workbook_xml = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>']
    workbook_xml.append(
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'
    )
    for idx, (name, _rows) in enumerate(normalized, start=1):
        workbook_xml.append(f'<sheet name="{html.escape(name)}" sheetId="{idx}" r:id="rId{idx}"/>')
    workbook_xml.append("</sheets></workbook>")
    rels = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>']
    rels.append(
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    )
    for idx in range(1, len(normalized) + 1):
        rels.append(
            f'<Relationship Id="rId{idx}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{idx}.xml"/>'
        )
    rels.append(
        f'<Relationship Id="rId{len(normalized) + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
    )
    rels.append("</Relationships>")
    with zipfile.ZipFile(workbook, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", "".join(content_types))
        zf.writestr(
            "_rels/.rels",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>',
        )
        zf.writestr("xl/workbook.xml", "".join(workbook_xml))
        zf.writestr("xl/_rels/workbook.xml.rels", "".join(rels))
        zf.writestr(
            "xl/styles.xml",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><fonts count="1"><font><sz val="11"/><name val="Aptos"/></font></fonts><fills count="1"><fill><patternFill patternType="none"/></fill></fills><borders count="1"><border/></borders><cellStyleXfs count="1"><xf/></cellStyleXfs><cellXfs count="1"><xf xfId="0"/></cellXfs></styleSheet>',
        )
        for idx, (_name, rows) in enumerate(normalized, start=1):
            zf.writestr(f"xl/worksheets/sheet{idx}.xml", _sheet_xml(rows))
    return workbook


def write_cover_first_workbook(
    path: str | Path,
    cover_rows: Sequence[Sequence[Any]],
    tables: Mapping[str, Sequence[Sequence[Any]]] | None = None,
) -> Path:
    sheets: dict[str, Sequence[Sequence[Any]]] = {"Cover": cover_rows}
    sheets.update(dict(tables or {}))
    return write_simple_xlsx_from_tables(path, sheets)


def dict_rows_to_sheet(
    rows: Sequence[Mapping[str, Any]], headers: Sequence[str] | None = None
) -> list[list[Any]]:
    if headers is None:
        seen: list[str] = []
        for row in rows:
            for key in row.keys():
                if str(key) not in seen:
                    seen.append(str(key))
        headers = seen
    header_list = [str(header) for header in headers]
    return [header_list, *[[row.get(header, "") for header in header_list] for row in rows]]


def write_report_html(
    path: str | Path,
    title: str,
    markdown_text: str,
    subtitle: str = "Reader-facing Public Equity Investing report. Backing files are support artifacts.",
) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    html_text = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    body {{ margin:0; font-family: Arial, Helvetica, sans-serif; background:#f6f7f9; color:#111827; }}
    .topbar {{ background:#0f172a; color:#fff; padding:18px 28px; position:sticky; top:0; z-index:10; }}
    .topbar h1 {{ margin:0; font-size:1.45rem; }}
    .topbar p {{ margin:6px 0 0; color:#dbeafe; }}
    main {{ max-width:1120px; margin:0 auto; padding:28px; }}
    .card {{ background:#fff; border:1px solid #d7dae0; border-radius:8px; padding:24px; box-shadow:0 16px 36px rgba(15,23,42,.08); }}
    pre {{ white-space:pre-wrap; overflow-wrap:anywhere; margin:0; font:0.94rem/1.58 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
    @media (max-width:720px) {{ main {{ padding:16px; }} .card {{ padding:18px; }} }}
  </style>
</head>
<body>
  <header class="topbar"><h1>{html.escape(title)}</h1><p>{html.escape(subtitle)}</p></header>
  <main><section class="card"><pre>{html.escape(markdown_text)}</pre></section></main>
</body>
</html>"""
    target.write_text(html_text, encoding="utf-8")
    return target


def write_dashboard_contract(
    path: str | Path,
    skill: str,
    title: str,
    entity: str,
    render_mode: str,
    primary_artifact: str | Path,
    *,
    executive_summary: str | Sequence[Any] | Mapping[str, Any] | None = None,
    hero_actions: Sequence[Mapping[str, Any]] | None = None,
    supporting_outputs: Sequence[Mapping[str, Any]] | None = None,
    report_body: Sequence[Mapping[str, Any]] | None = None,
    readiness_posture: str = "draft",
    citation_policy: str = "strict",
    blocked_output_context: Mapping[str, Any] | None = None,
    extra: Mapping[str, Any] | None = None,
) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    contract: dict[str, Any] = {
        "dashboard_title": title,
        "entity": entity,
        "skill": skill,
        "render_mode": render_mode,
        "posture": readiness_posture,
        "metadata": {"readiness_posture": readiness_posture, "citation_policy": citation_policy},
        "deliverable": {
            "render_mode": render_mode,
            "primary_artifact": _string_path(primary_artifact),
            "primary_artifact_type": artifact_type_from_path(primary_artifact),
            "readiness_posture": readiness_posture,
            "citation_policy": citation_policy,
            "executive_summary": executive_summary or [],
            "hero_actions": list(hero_actions or []),
            "utility_controls": {
                "copy_full_report": True,
                "print_pdf": True,
                "open_primary_artifact": True,
            },
            "table_export_default": True,
            "hero_callout": "Open the primary artifact first; support files are audit/import material.",
        },
        "hero": {
            "eyebrow": skill,
            "headline": title,
            "dek": "Public Equity Investing output with support artifacts kept behind the reader-facing artifact.",
            "callout_label": "First read",
            "callout": _string_path(primary_artifact),
        },
        "report_body": list(report_body or []),
        "supporting_outputs": list(supporting_outputs or []),
        "blocked_output_context": dict(
            blocked_output_context or {"blocked": False, "reason": "", "missing_inputs": []}
        ),
    }
    if extra:
        contract.update(dict(extra))
    target.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
    return target
