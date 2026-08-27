"""Minimal XLSX writer for three-statement deterministic exports."""

from __future__ import annotations

import re
import zipfile
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value == value


def _xlsx_col_ref(col_1idx: int) -> str:
    value = ""
    col = col_1idx
    while col:
        col, rem = divmod(col - 1, 26)
        value = chr(65 + rem) + value
    return value


def _xlsx_cell_ref(row_1idx: int, col_1idx: int) -> str:
    return f"{_xlsx_col_ref(col_1idx)}{row_1idx}"


def _xlsx_shared_string(text: str, shared_map: dict[str, int], shared_list: list[str]) -> int:
    if text not in shared_map:
        shared_map[text] = len(shared_list)
        shared_list.append(text)
    return shared_map[text]


def sanitize_sheet_name(name: str) -> str:
    cleaned = re.sub(r"[][\\/*?:]", "_", str(name))[:31]
    return cleaned or "Sheet"


def _cell_xml(
    row_1idx: int,
    col_1idx: int,
    value: Any,
    shared_map: dict[str, int],
    shared_list: list[str],
) -> str:
    if value is None or value == "":
        return ""
    ref = _xlsx_cell_ref(row_1idx, col_1idx)
    if isinstance(value, bool):
        return f'<c r="{ref}" t="b"><v>{1 if value else 0}</v></c>'
    if _is_number(value):
        return f'<c r="{ref}"><v>{float(value)}</v></c>'
    idx = _xlsx_shared_string(str(value), shared_map, shared_list)
    return f'<c r="{ref}" t="s"><v>{idx}</v></c>'


def _sheet_xml(
    rows: list[dict[str, Any]], shared_map: dict[str, int], shared_list: list[str]
) -> str:
    if rows:
        headers = list(rows[0].keys())
    else:
        headers = ["message"]
        rows = [{"message": "no rows"}]
    sheet_rows: list[str] = []
    header_cells = "".join(
        _cell_xml(1, c, value, shared_map, shared_list) for c, value in enumerate(headers, start=1)
    )
    sheet_rows.append(f'<row r="1">{header_cells}</row>')
    for row_num, row in enumerate(rows, start=2):
        cells = "".join(
            _cell_xml(row_num, c, row.get(header, ""), shared_map, shared_list)
            for c, header in enumerate(headers, start=1)
        )
        sheet_rows.append(f'<row r="{row_num}">{cells}</row>')
    dimension = f"A1:{_xlsx_cell_ref(len(rows) + 1, len(headers))}"
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f'<dimension ref="{dimension}"/>'
        '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>'
        "<sheetData>" + "".join(sheet_rows) + "</sheetData>"
        "</worksheet>"
    )


def _shared_strings_xml(shared_list: list[str]) -> str:
    def item_xml(text: str) -> str:
        needs_preserve = text[:1].isspace() or text[-1:].isspace()
        attr = ' xml:space="preserve"' if needs_preserve else ""
        return f"<si><t{attr}>{escape(text)}</t></si>"

    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        f'count="{len(shared_list)}" uniqueCount="{len(shared_list)}">'
        + "".join(item_xml(item) for item in shared_list)
        + "</sst>"
    )


def _styles_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="1"><font><sz val="11"/><color theme="1"/><name val="Calibri"/><family val="2"/></font></fonts>
  <fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>
  <borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
  <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
  <cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs>
  <cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>
"""


def _workbook_parts(sheet_xmls: list[tuple[str, str]]) -> tuple[str, str, str, str]:
    workbook_sheets = []
    rels = []
    content_overrides = []
    for idx, (name, _) in enumerate(sheet_xmls, start=1):
        workbook_sheets.append(f'<sheet name="{escape(name)}" sheetId="{idx}" r:id="rId{idx}"/>')
        rels.append(
            f'<Relationship Id="rId{idx}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{idx}.xml"/>'
        )
        content_overrides.append(
            f'<Override PartName="/xl/worksheets/sheet{idx}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        )
    style_rid = len(sheet_xmls) + 1
    sst_rid = len(sheet_xmls) + 2
    rels.append(
        f'<Relationship Id="rId{style_rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
    )
    rels.append(
        f'<Relationship Id="rId{sst_rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings" Target="sharedStrings.xml"/>'
    )

    workbook_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'
        + "".join(workbook_sheets)
        + "</sheets></workbook>"
    )
    workbook_rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        + "".join(rels)
        + "</Relationships>"
    )
    root_rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>
"""
    content_types_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        + "".join(content_overrides)
        + '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        + '<Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/>'
        + "</Types>"
    )
    return content_types_xml, root_rels_xml, workbook_xml, workbook_rels_xml


def write_xlsx(
    path: Path, sheets: dict[str, list[dict[str, Any]]], sheet_name: str = "Model"
) -> None:
    """Write a minimal multi-sheet .xlsx workbook using only stdlib zip/xml."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not sheets:
        raise ValueError("No sheets to write")
    if isinstance(sheets, list):
        sheets = {sheet_name: sheets}  # type: ignore[assignment]

    shared_map: dict[str, int] = {}
    shared_list: list[str] = []
    sheet_xmls: list[tuple[str, str]] = []
    used_names: set[str] = set()
    for raw_name, rows in sheets.items():
        name = sanitize_sheet_name(raw_name)
        base_name = name
        suffix = 1
        while name in used_names:
            suffix += 1
            name = sanitize_sheet_name(f"{base_name[:28]}{suffix}")
        used_names.add(name)
        sheet_xmls.append((name, _sheet_xml(rows, shared_map, shared_list)))

    content_types_xml, root_rels_xml, workbook_xml, workbook_rels_xml = _workbook_parts(sheet_xmls)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types_xml)
        archive.writestr("_rels/.rels", root_rels_xml)
        archive.writestr("xl/workbook.xml", workbook_xml)
        archive.writestr("xl/_rels/workbook.xml.rels", workbook_rels_xml)
        for idx, (_, sheet_xml) in enumerate(sheet_xmls, start=1):
            archive.writestr(f"xl/worksheets/sheet{idx}.xml", sheet_xml)
        archive.writestr("xl/sharedStrings.xml", _shared_strings_xml(shared_list))
        archive.writestr("xl/styles.xml", _styles_xml())
