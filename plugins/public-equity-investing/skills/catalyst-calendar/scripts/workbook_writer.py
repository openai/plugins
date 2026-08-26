"""Minimal XLSX writer for catalyst-calendar outputs."""

from __future__ import annotations

import datetime as dt
import zipfile
from html import escape
from pathlib import Path
from typing import Sequence


def col_letter(index: int) -> str:
    result = ""
    while index:
        index, rem = divmod(index - 1, 26)
        result = chr(65 + rem) + result
    return result


def cell_ref(row: int, col: int) -> str:
    return f"{col_letter(col)}{row}"


def xml_cell(value: object, row: int, col: int, style: int = 0) -> str:
    ref = cell_ref(row, col)
    s_attr = f' s="{style}"' if style else ""
    if value is None or value == "":
        return f'<c r="{ref}"{s_attr}/>'
    if isinstance(value, bool):
        return f'<c r="{ref}" t="b"{s_attr}><v>{1 if value else 0}</v></c>'
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return f'<c r="{ref}"{s_attr}><v>{value}</v></c>'
    text = str(value)
    if text.startswith("="):
        return f'<c r="{ref}"{s_attr}><f>{escape(text[1:])}</f></c>'
    return f'<c r="{ref}" t="inlineStr"{s_attr}><is><t>{escape(text)}</t></is></c>'


def sheet_xml(
    headers: Sequence[str],
    rows: Sequence[Sequence[object]],
    title: str = "",
    freeze: bool = True,
) -> str:
    out: list[str] = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>']
    out.append(
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
    )
    out.append('<sheetViews><sheetView workbookViewId="0">')
    if freeze:
        out.append('<pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/>')
    out.append("</sheetView></sheetViews>")
    # Conservative column widths, broad enough for PM notes but not extreme.
    col_count = max(len(headers), max((len(r) for r in rows), default=0), 1)
    out.append("<cols>")
    for i in range(1, col_count + 1):
        width = 14
        if i <= len(headers):
            header = headers[i - 1].lower()
            if (
                "description" in header
                or "notes" in header
                or "why" in header
                or "implication" in header
                or "source" in header
            ):
                width = 32
            elif "event" in header or "ticker" in header or "owner" in header:
                width = 18
            elif "date" in header or "window" in header or "status" in header:
                width = 16
        out.append(f'<col min="{i}" max="{i}" width="{width}" customWidth="1"/>')
    out.append("</cols>")
    out.append("<sheetData>")
    current_row = 1
    if title:
        out.append(f'<row r="{current_row}">{xml_cell(title, current_row, 1, 1)}</row>')
        current_row += 1
    if headers:
        cells = "".join(xml_cell(h, current_row, c, 2) for c, h in enumerate(headers, start=1))
        out.append(f'<row r="{current_row}">{cells}</row>')
        current_row += 1
    for row_values in rows:
        cells = "".join(xml_cell(v, current_row, c, 0) for c, v in enumerate(row_values, start=1))
        out.append(f'<row r="{current_row}">{cells}</row>')
        current_row += 1
    out.append("</sheetData>")
    out.append("</worksheet>")
    return "".join(out)


def workbook_xml(sheet_names: Sequence[str]) -> str:
    sheets = []
    for i, name in enumerate(sheet_names, start=1):
        sheets.append(f'<sheet name="{escape(name)}" sheetId="{i}" r:id="rId{i}"/>')
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        + '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'
        + "".join(sheets)
        + "</sheets></workbook>"
    )


def workbook_rels(sheet_count: int) -> str:
    rels = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    ]
    for i in range(1, sheet_count + 1):
        rels.append(
            f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>'
        )
    rels.append(
        f'<Relationship Id="rId{sheet_count + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
    )
    rels.append("</Relationships>")
    return "".join(rels)


def root_rels() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>"""


def content_types(sheet_count: int) -> str:
    parts = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    ]
    parts.append(
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    )
    parts.append('<Default Extension="xml" ContentType="application/xml"/>')
    parts.append(
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
    )
    parts.append(
        '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
    )
    parts.append(
        '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
    )
    parts.append(
        '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
    )
    for i in range(1, sheet_count + 1):
        parts.append(
            f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        )
    parts.append("</Types>")
    return "".join(parts)


def styles_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="3">
    <font><sz val="11"/><name val="Calibri"/></font>
    <font><b/><sz val="14"/><name val="Calibri"/></font>
    <font><b/><sz val="11"/><name val="Calibri"/><color rgb="FFFFFFFF"/></font>
  </fonts>
  <fills count="3">
    <fill><patternFill patternType="none"/></fill>
    <fill><patternFill patternType="gray125"/></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FF1F4E79"/><bgColor indexed="64"/></patternFill></fill>
  </fills>
  <borders count="2">
    <border><left/><right/><top/><bottom/><diagonal/></border>
    <border><left style="thin"/><right style="thin"/><top style="thin"/><bottom style="thin"/><diagonal/></border>
  </borders>
  <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
  <cellXfs count="3">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
    <xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/>
    <xf numFmtId="0" fontId="2" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1"/>
  </cellXfs>
  <cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>"""


def core_props() -> str:
    now = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:creator>catalyst-calendar skill</dc:creator>
  <cp:lastModifiedBy>catalyst-calendar skill</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>"""


def app_props(sheet_names: Sequence[str]) -> str:
    titles = "".join(f"<vt:lpstr>{escape(name)}</vt:lpstr>" for name in sheet_names)
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>catalyst-calendar skill</Application>
  <DocSecurity>0</DocSecurity>
  <ScaleCrop>false</ScaleCrop>
  <HeadingPairs><vt:vector size="2" baseType="variant"><vt:variant><vt:lpstr>Worksheets</vt:lpstr></vt:variant><vt:variant><vt:i4>{len(sheet_names)}</vt:i4></vt:variant></vt:vector></HeadingPairs>
  <TitlesOfParts><vt:vector size="{len(sheet_names)}" baseType="lpstr">{titles}</vt:vector></TitlesOfParts>
</Properties>'''


def write_xlsx(
    path: Path,
    sheets: Sequence[tuple[str, Sequence[str], Sequence[Sequence[object]], str]],
) -> None:
    sheet_names = [name for name, _, _, _ in sheets]
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types(len(sheets)))
        zf.writestr("_rels/.rels", root_rels())
        zf.writestr("docProps/core.xml", core_props())
        zf.writestr("docProps/app.xml", app_props(sheet_names))
        zf.writestr("xl/workbook.xml", workbook_xml(sheet_names))
        zf.writestr("xl/_rels/workbook.xml.rels", workbook_rels(len(sheets)))
        zf.writestr("xl/styles.xml", styles_xml())
        for idx, (_name, headers, rows, title) in enumerate(sheets, start=1):
            zf.writestr(f"xl/worksheets/sheet{idx}.xml", sheet_xml(headers, rows, title=title))
