"""Minimal XLSX writer for dcf-model-builder deterministic exports."""

from __future__ import annotations

import os
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _col_letter(idx: int) -> str:
    result = ""
    n = idx
    while n:
        n, rem = divmod(n - 1, 26)
        result = chr(65 + rem) + result
    return result


def _cell_ref(row_idx: int, col_idx: int) -> str:
    return f"{_col_letter(col_idx)}{row_idx}"


def _xml_text(value: Any) -> str:
    return escape(str(value), {'"': "&quot;"})


def _sheet_name(name: str, used: set[str]) -> str:
    invalid = set("[]:*?/\\")
    clean = "".join("_" if char in invalid else char for char in name).strip() or "Sheet"
    clean = clean[:31]
    original = clean
    i = 2
    while clean in used:
        suffix = f"_{i}"
        clean = (original[: 31 - len(suffix)] + suffix)[:31]
        i += 1
    used.add(clean)
    return clean


def _sheet_xml(rows: list[list[Any]]) -> str:
    xml_rows: list[str] = []
    for r_idx, row in enumerate(rows, start=1):
        cells: list[str] = []
        for c_idx, value in enumerate(row, start=1):
            if value is None:
                continue
            ref = _cell_ref(r_idx, c_idx)
            if isinstance(value, bool):
                cells.append(f'<c r="{ref}" t="b"><v>{1 if value else 0}</v></c>')
            elif _is_number(value):
                cells.append(f'<c r="{ref}"><v>{float(value):.12g}</v></c>')
            else:
                cells.append(f'<c r="{ref}" t="inlineStr"><is><t>{_xml_text(value)}</t></is></c>')
        xml_rows.append(f'<row r="{r_idx}">{"".join(cells)}</row>')

    dimension = "A1"
    if rows:
        max_cols = max((len(row) for row in rows), default=1)
        dimension = f"A1:{_cell_ref(len(rows), max_cols)}"
    cols = "".join(
        f'<col min="{idx}" max="{idx}" width="18" customWidth="1"/>'
        for idx in range(1, max((len(row) for row in rows), default=1) + 1)
    )
    return "".join(
        [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" ',
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">',
            f'<dimension ref="{dimension}"/>',
            '<sheetViews><sheetView showGridLines="0" workbookViewId="0">',
            '<pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/>',
            "</sheetView></sheetViews>",
            f"<cols>{cols}</cols>",
            "<sheetData>",
            "".join(xml_rows),
            "</sheetData>",
            "</worksheet>",
        ]
    )


def _content_types(sheet_count: int) -> str:
    overrides = [
        (
            '<Override PartName="/xl/workbook.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.'
            'spreadsheetml.sheet.main+xml"/>'
        ),
        (
            '<Override PartName="/xl/styles.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.'
            'spreadsheetml.styles+xml"/>'
        ),
        (
            '<Override PartName="/docProps/core.xml" '
            'ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
        ),
        (
            '<Override PartName="/docProps/app.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.'
            'extended-properties+xml"/>'
        ),
    ]
    for idx in range(1, sheet_count + 1):
        overrides.append(
            f'<Override PartName="/xl/worksheets/sheet{idx}.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.'
            'spreadsheetml.worksheet+xml"/>'
        )
    return "".join(
        [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
            '<Default Extension="rels" '
            'ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
            '<Default Extension="xml" ContentType="application/xml"/>',
            "".join(overrides),
            "</Types>",
        ]
    )


def _root_rels() -> str:
    return "".join(
        [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
            '<Relationship Id="rId1" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
            'Target="xl/workbook.xml"/>',
            '<Relationship Id="rId2" '
            'Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" '
            'Target="docProps/core.xml"/>',
            '<Relationship Id="rId3" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" '
            'Target="docProps/app.xml"/>',
            "</Relationships>",
        ]
    )


def _workbook_xml(sheet_names: list[str]) -> str:
    sheets = [
        f'<sheet name="{_xml_text(name)}" sheetId="{idx}" r:id="rId{idx}"/>'
        for idx, name in enumerate(sheet_names, start=1)
    ]
    return "".join(
        [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" ',
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">',
            "<bookViews><workbookView/></bookViews>",
            f"<sheets>{''.join(sheets)}</sheets>",
            "</workbook>",
        ]
    )


def _workbook_rels(sheet_count: int) -> str:
    rels = []
    for idx in range(1, sheet_count + 1):
        rels.append(
            f'<Relationship Id="rId{idx}" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
            f'Target="worksheets/sheet{idx}.xml"/>'
        )
    rels.append(
        f'<Relationship Id="rId{sheet_count + 1}" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" '
        'Target="styles.xml"/>'
    )
    return "".join(
        [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
            "".join(rels),
            "</Relationships>",
        ]
    )


def _styles_xml() -> str:
    return "".join(
        [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">',
            '<fonts count="1"><font><sz val="11"/><color theme="1"/>',
            '<name val="Calibri"/><family val="2"/></font></fonts>',
            '<fills count="2"><fill><patternFill patternType="none"/></fill>',
            '<fill><patternFill patternType="gray125"/></fill></fills>',
            '<borders count="1"><border><left/><right/><top/><bottom/>',
            "<diagonal/></border></borders>",
            '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" ',
            'borderId="0"/></cellStyleXfs>',
            '<cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" ',
            'borderId="0" xfId="0"/></cellXfs>',
            '<cellStyles count="1"><cellStyle name="Normal" xfId="0" ',
            'builtinId="0"/></cellStyles>',
            "</styleSheet>",
        ]
    )


def _core_xml() -> str:
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    return "".join(
        [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" ',
            'xmlns:dc="http://purl.org/dc/elements/1.1/" ',
            'xmlns:dcterms="http://purl.org/dc/terms/" ',
            'xmlns:dcmitype="http://purl.org/dc/dcmitype/" ',
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
            "<dc:title>DCF Model Export</dc:title>",
            "<dc:creator>dcf-model-builder</dc:creator>",
            f'<dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>',
            f'<dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>',
            "</cp:coreProperties>",
        ]
    )


def _app_xml(sheet_names: list[str]) -> str:
    names = "".join(f"<vt:lpstr>{_xml_text(name)}</vt:lpstr>" for name in sheet_names)
    return "".join(
        [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" ',
            'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">',
            "<Application>dcf-model-builder</Application>",
            '<HeadingPairs><vt:vector size="2" baseType="variant">',
            "<vt:variant><vt:lpstr>Worksheets</vt:lpstr></vt:variant>",
            f"<vt:variant><vt:i4>{len(sheet_names)}</vt:i4></vt:variant>",
            "</vt:vector></HeadingPairs>",
            f'<TitlesOfParts><vt:vector size="{len(sheet_names)}" baseType="lpstr">',
            names,
            "</vt:vector></TitlesOfParts>",
            "</Properties>",
        ]
    )


def write_xlsx(path: str | os.PathLike[str], rows: Any, sheet_name: str = "Model") -> None:
    """Write a minimal valid XLSX. `rows` may be a table or dict of sheet tables."""
    sheets_input = rows if isinstance(rows, dict) else {sheet_name: rows}
    used: set[str] = set()
    sheet_names = []
    sheet_tables = []
    for raw_name, table in sheets_input.items():
        name = _sheet_name(str(raw_name), used)
        sheet_names.append(name)
        sheet_tables.append(table)

    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", _content_types(len(sheet_names)))
        zf.writestr("_rels/.rels", _root_rels())
        zf.writestr("xl/workbook.xml", _workbook_xml(sheet_names))
        zf.writestr("xl/_rels/workbook.xml.rels", _workbook_rels(len(sheet_names)))
        zf.writestr("xl/styles.xml", _styles_xml())
        zf.writestr("docProps/core.xml", _core_xml())
        zf.writestr("docProps/app.xml", _app_xml(sheet_names))
        for idx, table in enumerate(sheet_tables, start=1):
            zf.writestr(f"xl/worksheets/sheet{idx}.xml", _sheet_xml(table))
