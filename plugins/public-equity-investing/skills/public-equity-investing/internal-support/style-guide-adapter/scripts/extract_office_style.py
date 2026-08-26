#!/usr/bin/env python3
"""Extract lightweight style metadata from Office files.

Supports .pptx, .docx, and .xlsx files without modifying them. The output is a
style reconnaissance aid, not a replacement for rendered visual review.

Usage:
  python scripts/extract_office_style.py path/to/file.pptx --format markdown
  python scripts/extract_office_style.py deck.pptx memo.docx model.xlsx --format json --out style.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterable
from xml.etree import ElementTree as ET

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
}


def _read_xml(zf: zipfile.ZipFile, name: str) -> ET.Element | None:
    try:
        with zf.open(name) as fh:
            return ET.parse(fh).getroot()
    except (KeyError, ET.ParseError, zipfile.BadZipFile):
        return None


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _attr(el: ET.Element, name: str) -> str | None:
    value = el.attrib.get(name)
    if value is not None:
        return value
    for key, val in el.attrib.items():
        if key.endswith("}" + name):
            return val
    return None


def _count_members(zf: zipfile.ZipFile, prefix: str, pattern: str) -> int:
    rx = re.compile(pattern)
    return sum(1 for n in zf.namelist() if n.startswith(prefix) and rx.search(n))


def _unique_sorted(values: Iterable[str], limit: int = 30) -> list[str]:
    clean = [v for v in values if v]
    return sorted(set(clean))[:limit]


def _top(counter: Counter, limit: int = 12) -> list[dict[str, Any]]:
    return [{"value": k, "count": v} for k, v in counter.most_common(limit) if k]


def _theme_summary(zf: zipfile.ZipFile, candidates: list[str]) -> dict[str, Any]:
    root = None
    source = None
    for name in candidates:
        root = _read_xml(zf, name)
        if root is not None:
            source = name
            break
    if root is None:
        return {}

    theme: dict[str, Any] = {"source": source}
    theme_name = _attr(root, "name")
    if theme_name:
        theme["theme_name"] = theme_name

    colors: dict[str, str] = {}
    clr_scheme = root.find(".//a:clrScheme", NS)
    if clr_scheme is not None:
        for child in list(clr_scheme):
            slot = _local(child.tag)
            rgb = child.find(".//a:srgbClr", NS)
            sysclr = child.find(".//a:sysClr", NS)
            if rgb is not None and _attr(rgb, "val"):
                colors[slot] = "#" + _attr(rgb, "val").upper()
            elif sysclr is not None:
                last = _attr(sysclr, "lastClr")
                val = _attr(sysclr, "val")
                colors[slot] = ("#" + last.upper()) if last else f"system:{val}"
    if colors:
        theme["colors"] = colors

    fonts: dict[str, str] = {}
    for slot, xpath in [
        ("major_latin", ".//a:majorFont/a:latin"),
        ("minor_latin", ".//a:minorFont/a:latin"),
    ]:
        el = root.find(xpath, NS)
        if el is not None and _attr(el, "typeface"):
            fonts[slot] = _attr(el, "typeface")
    if fonts:
        theme["fonts"] = fonts

    return theme


def _drawing_text_style_counts(root: ET.Element) -> dict[str, Any]:
    fonts: Counter = Counter()
    sizes: Counter = Counter()
    colors: Counter = Counter()

    for rpr in root.findall(".//a:rPr", NS):
        sz = _attr(rpr, "sz")
        if sz and sz.isdigit():
            sizes[str(int(sz) / 100)] += 1
        latin = rpr.find("a:latin", NS)
        if latin is not None and _attr(latin, "typeface"):
            fonts[_attr(latin, "typeface")] += 1
        srgb = rpr.find(".//a:solidFill/a:srgbClr", NS)
        if srgb is not None and _attr(srgb, "val"):
            colors["#" + _attr(srgb, "val").upper()] += 1

    return {
        "observed_text_fonts": _top(fonts),
        "observed_text_sizes_pt": _top(sizes),
        "observed_text_colors": _top(colors),
    }


def _pptx_summary(path: Path, zf: zipfile.ZipFile) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "type": "pptx",
        "slide_count": _count_members(zf, "ppt/slides/", r"slide\d+\.xml$"),
        "layout_count": _count_members(zf, "ppt/slideLayouts/", r"slideLayout\d+\.xml$"),
        "master_count": _count_members(zf, "ppt/slideMasters/", r"slideMaster\d+\.xml$"),
    }
    theme = _theme_summary(zf, ["ppt/theme/theme1.xml"])
    if theme:
        summary["theme"] = theme

    presentation = _read_xml(zf, "ppt/presentation.xml")
    if presentation is not None:
        sld_sz = presentation.find("p:sldSz", NS)
        if sld_sz is not None:
            summary["slide_size_emu"] = {
                "cx": _attr(sld_sz, "cx"),
                "cy": _attr(sld_sz, "cy"),
                "type": _attr(sld_sz, "type"),
            }

    layout_names: list[str] = []
    for name in zf.namelist():
        if name.startswith("ppt/slideLayouts/slideLayout") and name.endswith(".xml"):
            root = _read_xml(zf, name)
            if root is None:
                continue
            csld = root.find("p:cSld", NS)
            if csld is not None and _attr(csld, "name"):
                layout_names.append(_attr(csld, "name"))
    if layout_names:
        summary["layout_names"] = _unique_sorted(layout_names)

    font_counts: Counter = Counter()
    size_counts: Counter = Counter()
    color_counts: Counter = Counter()
    fill_counts: Counter = Counter()
    line_counts: Counter = Counter()

    for name in zf.namelist():
        if not (
            name.startswith(
                ("ppt/slides/slide", "ppt/slideMasters/slideMaster", "ppt/slideLayouts/slideLayout")
            )
        ):
            continue
        if not name.endswith(".xml"):
            continue
        root = _read_xml(zf, name)
        if root is None:
            continue
        counts = _drawing_text_style_counts(root)
        for item in counts["observed_text_fonts"]:
            font_counts[item["value"]] += item["count"]
        for item in counts["observed_text_sizes_pt"]:
            size_counts[item["value"]] += item["count"]
        for item in counts["observed_text_colors"]:
            color_counts[item["value"]] += item["count"]
        for srgb in root.findall(".//a:solidFill/a:srgbClr", NS):
            if _attr(srgb, "val"):
                fill_counts["#" + _attr(srgb, "val").upper()] += 1
        for srgb in root.findall(".//a:ln//a:srgbClr", NS):
            if _attr(srgb, "val"):
                line_counts["#" + _attr(srgb, "val").upper()] += 1

    summary["observed"] = {
        "text_fonts": _top(font_counts),
        "text_sizes_pt": _top(size_counts),
        "text_colors": _top(color_counts),
        "fill_colors": _top(fill_counts),
        "line_colors": _top(line_counts),
    }
    return summary


def _docx_summary(path: Path, zf: zipfile.ZipFile) -> dict[str, Any]:
    summary: dict[str, Any] = {"type": "docx"}
    theme = _theme_summary(zf, ["word/theme/theme1.xml"])
    if theme:
        summary["theme"] = theme

    styles = _read_xml(zf, "word/styles.xml")
    style_rows: list[dict[str, Any]] = []
    if styles is not None:
        for st in styles.findall("w:style", NS):
            row: dict[str, Any] = {
                "type": _attr(st, "type"),
                "style_id": _attr(st, "styleId"),
            }
            name_el = st.find("w:name", NS)
            if name_el is not None:
                row["name"] = _attr(name_el, "val")
            based_on = st.find("w:basedOn", NS)
            if based_on is not None:
                row["based_on"] = _attr(based_on, "val")
            rfonts = st.find(".//w:rFonts", NS)
            if rfonts is not None:
                row["font"] = (
                    _attr(rfonts, "ascii") or _attr(rfonts, "hAnsi") or _attr(rfonts, "cs")
                )
            sz = st.find(".//w:sz", NS)
            if sz is not None and _attr(sz, "val") and _attr(sz, "val").isdigit():
                row["size_pt"] = int(_attr(sz, "val")) / 2
            color = st.find(".//w:color", NS)
            if color is not None and _attr(color, "val") and _attr(color, "val") != "auto":
                row["color"] = "#" + _attr(color, "val").upper()
            if row.get("name") or row.get("style_id"):
                style_rows.append(row)
    summary["styles"] = style_rows[:80]

    document = _read_xml(zf, "word/document.xml")
    if document is not None:
        para_styles: Counter = Counter()
        table_count = len(document.findall(".//w:tbl", NS))
        for pstyle in document.findall(".//w:pStyle", NS):
            if _attr(pstyle, "val"):
                para_styles[_attr(pstyle, "val")] += 1
        summary["document_usage"] = {
            "paragraph_style_counts": _top(para_styles),
            "table_count": table_count,
        }
    return summary


def _xlsx_summary(path: Path, zf: zipfile.ZipFile) -> dict[str, Any]:
    summary: dict[str, Any] = {"type": "xlsx"}
    theme = _theme_summary(zf, ["xl/theme/theme1.xml"])
    if theme:
        summary["theme"] = theme

    workbook = _read_xml(zf, "xl/workbook.xml")
    if workbook is not None:
        sheets = []
        for sh in workbook.findall(".//x:sheet", NS):
            row = {"name": _attr(sh, "name"), "sheet_id": _attr(sh, "sheetId")}
            if row["name"]:
                sheets.append(row)
        summary["sheets"] = sheets

    styles = _read_xml(zf, "xl/styles.xml")
    if styles is not None:
        fonts = []
        for font in styles.findall("x:fonts/x:font", NS):
            row: dict[str, Any] = {}
            name_el = font.find("x:name", NS)
            sz_el = font.find("x:sz", NS)
            color_el = font.find("x:color", NS)
            if name_el is not None:
                row["name"] = _attr(name_el, "val")
            if sz_el is not None:
                row["size_pt"] = _attr(sz_el, "val")
            if color_el is not None:
                if _attr(color_el, "rgb"):
                    row["color"] = "#" + _attr(color_el, "rgb")[-6:].upper()
                elif _attr(color_el, "theme"):
                    row["theme_color"] = _attr(color_el, "theme")
            if row:
                fonts.append(row)

        fills = []
        for fill in styles.findall("x:fills/x:fill", NS):
            fg = fill.find(".//x:fgColor", NS)
            if fg is not None:
                if _attr(fg, "rgb"):
                    fills.append("#" + _attr(fg, "rgb")[-6:].upper())
                elif _attr(fg, "theme"):
                    fills.append("theme:" + _attr(fg, "theme"))

        cell_styles = []
        for st in styles.findall("x:cellStyles/x:cellStyle", NS):
            row = {"name": _attr(st, "name"), "builtin_id": _attr(st, "builtinId")}
            if row["name"]:
                cell_styles.append(row)

        num_fmts = []
        for nf in styles.findall("x:numFmts/x:numFmt", NS):
            fmt = _attr(nf, "formatCode")
            if fmt:
                num_fmts.append(fmt)

        summary["styles"] = {
            "fonts": fonts[:60],
            "fills": _unique_sorted(fills, limit=40),
            "cell_styles": cell_styles[:80],
            "custom_number_formats": num_fmts[:80],
        }
    return summary


def inspect_file(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "file": str(path),
        "name": path.name,
        "extension": path.suffix.lower(),
    }
    if not path.exists():
        result["error"] = "file not found"
        return result
    if path.suffix.lower() not in {".pptx", ".docx", ".xlsx"}:
        result["error"] = "unsupported file type"
        return result
    try:
        with zipfile.ZipFile(path) as zf:
            if path.suffix.lower() == ".pptx":
                result.update(_pptx_summary(path, zf))
            elif path.suffix.lower() == ".docx":
                result.update(_docx_summary(path, zf))
            else:
                result.update(_xlsx_summary(path, zf))
    except zipfile.BadZipFile:
        result["error"] = "not a valid Office zip container"
    return result


def _md_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    if not rows:
        return ""
    out = ["| " + " | ".join(columns) + " |", "|" + "|".join(["---"] * len(columns)) + "|"]
    for row in rows:
        out.append("| " + " | ".join(str(row.get(c, "")) for c in columns) + " |")
    return "\n".join(out)


def to_markdown(results: list[dict[str, Any]]) -> str:
    lines: list[str] = ["# Office style extraction summary", ""]
    for res in results:
        lines.append(f"## {res.get('name', res.get('file'))}")
        if res.get("error"):
            lines.append(f"- Error: {res['error']}")
            lines.append("")
            continue
        lines.append(f"- Type: {res.get('type')}")
        for key in ["slide_count", "layout_count", "master_count"]:
            if key in res:
                lines.append(f"- {key.replace('_', ' ').title()}: {res[key]}")
        if "slide_size_emu" in res:
            lines.append(f"- Slide size EMU: {res['slide_size_emu']}")
        theme = res.get("theme", {})
        if theme:
            lines.append("\n### Theme")
            if theme.get("theme_name"):
                lines.append(f"- Theme name: {theme['theme_name']}")
            if theme.get("fonts"):
                lines.append(f"- Fonts: {theme['fonts']}")
            if theme.get("colors"):
                lines.append("- Colors:")
                for slot, color in theme["colors"].items():
                    lines.append(f"  - {slot}: {color}")
        if res.get("layout_names"):
            lines.append("\n### Layout names")
            for name in res["layout_names"][:30]:
                lines.append(f"- {name}")
        if res.get("sheets"):
            lines.append("\n### Sheets")
            lines.append(_md_table(res["sheets"], ["name", "sheet_id"]))
        if res.get("observed"):
            lines.append("\n### Observed style usage")
            for label, rows in res["observed"].items():
                if rows:
                    lines.append(f"\n**{label.replace('_', ' ').title()}**")
                    lines.append(_md_table(rows, ["value", "count"]))
        if res.get("document_usage"):
            usage = res["document_usage"]
            lines.append("\n### Document usage")
            lines.append(f"- Table count: {usage.get('table_count', 0)}")
            if usage.get("paragraph_style_counts"):
                lines.append(_md_table(usage["paragraph_style_counts"], ["value", "count"]))
        if res.get("styles"):
            styles = res["styles"]
            lines.append("\n### Styles")
            if isinstance(styles, list):
                lines.append(
                    _md_table(styles[:40], ["type", "style_id", "name", "font", "size_pt", "color"])
                )
            elif isinstance(styles, dict):
                if styles.get("fonts"):
                    lines.append("\n**Fonts**")
                    lines.append(
                        _md_table(styles["fonts"][:30], ["name", "size_pt", "color", "theme_color"])
                    )
                if styles.get("cell_styles"):
                    lines.append("\n**Cell styles**")
                    lines.append(_md_table(styles["cell_styles"][:40], ["name", "builtin_id"]))
                if styles.get("fills"):
                    lines.append("\n**Fills**")
                    for fill in styles["fills"][:30]:
                        lines.append(f"- {fill}")
                if styles.get("custom_number_formats"):
                    lines.append("\n**Custom number formats**")
                    for fmt in styles["custom_number_formats"][:30]:
                        lines.append(f"- `{fmt}`")
        lines.append("")
    lines.append(
        "Note: This extraction is metadata-only. Confirm visual layout, charts, images, and manual overrides by rendering or inspecting the artifact before final delivery."
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extract style metadata from .pptx, .docx, and .xlsx files without modifying them."
    )
    parser.add_argument("files", nargs="+", help="Office files to inspect")
    parser.add_argument(
        "--format", choices=["markdown", "json"], default="json", help="Output format"
    )
    parser.add_argument("--out", help="Optional output file")
    args = parser.parse_args(argv)

    results = [inspect_file(Path(p)) for p in args.files]
    if args.format == "json":
        output = json.dumps(results, indent=2)
    else:
        output = to_markdown(results)

    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
    else:
        print(output)

    return 1 if any("error" in r for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
