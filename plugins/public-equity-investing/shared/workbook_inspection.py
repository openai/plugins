"""Workbook inspection gates for Public Equity Investing formula workbooks."""

from __future__ import annotations

import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence
from xml.etree import ElementTree as ET

NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


@dataclass(frozen=True)
class WorkbookInspectionPolicy:
    workbook_type: str
    minimum_formula_count: int
    required_formula_sheets: tuple[str, ...]


POLICIES: dict[str, WorkbookInspectionPolicy] = {
    "dcf": WorkbookInspectionPolicy(
        "dcf",
        800,
        (
            "Revenue Build",
            "Margin Cost Build",
            "Working Capital",
            "Capex D&A",
            "Tax Schedule",
            "Unlevered FCF",
            "WACC",
            "Terminal Value",
            "DCF Valuation",
            "Sensitivities",
            "Checks",
        ),
    ),
    "three_statement": WorkbookInspectionPolicy(
        "three_statement",
        1100,
        (
            "Revenue Build",
            "Expense Build",
            "Income Statement",
            "Working Capital",
            "PP&E D&A",
            "Debt Interest",
            "Tax",
            "Balance Sheet",
            "Cash Flow Statement",
            "Scenarios",
            "Checks",
        ),
    ),
}


def workbook_sheet_paths(path: str | Path) -> tuple[dict[str, str], dict[str, str]]:
    with zipfile.ZipFile(path) as zf:
        workbook = ET.fromstring(zf.read("xl/workbook.xml"))
        rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
        relmap = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels}
        sheets = workbook.find(f"{{{NS_MAIN}}}sheets")
        if sheets is None:
            return {}, {}
        paths: dict[str, str] = {}
        states: dict[str, str] = {}
        for sheet in sheets:
            rid = sheet.attrib[f"{{{NS_REL}}}id"]
            target = relmap[rid].lstrip("/")
            name = sheet.attrib["name"]
            paths[name] = target if target.startswith("xl/") else f"xl/{target}"
            states[name] = sheet.attrib.get("state", "visible")
        return paths, states


def defined_names(path: str | Path) -> list[str]:
    with zipfile.ZipFile(path) as zf:
        workbook = ET.fromstring(zf.read("xl/workbook.xml"))
    node = workbook.find(f"{{{NS_MAIN}}}definedNames")
    if node is None:
        return []
    return [child.attrib["name"] for child in node if child.attrib.get("name")]


def inspect_formula_workbook(
    path: str | Path,
    *,
    required_sheets: Sequence[str],
    workbook_type: str,
    minimum_formula_count: int | None = None,
    required_formula_sheets: Sequence[str] | None = None,
) -> dict[str, Any]:
    policy = POLICIES.get(workbook_type)
    min_formulas = (
        minimum_formula_count
        if minimum_formula_count is not None
        else (policy.minimum_formula_count if policy else 100)
    )
    formula_sheet_requirements = tuple(
        required_formula_sheets or (policy.required_formula_sheets if policy else ())
    )
    with zipfile.ZipFile(path) as zf:
        names = set(zf.namelist())
        sheet_paths, sheet_states = workbook_sheet_paths(path)
        formula_counts_by_sheet: dict[str, int] = {}
        formula_count = 0
        for sheet_name, sheet_path in sheet_paths.items():
            root = ET.fromstring(zf.read(sheet_path))
            count = len(root.findall(f".//{{{NS_MAIN}}}f"))
            formula_counts_by_sheet[sheet_name] = count
            formula_count += count
        external_links = sorted(name for name in names if name.startswith("xl/externalLinks/"))
        has_styles = "xl/styles.xml" in names and len(zf.read("xl/styles.xml")) > 100
    sheet_names = list(sheet_paths.keys())
    visible = [name for name in sheet_names if sheet_states.get(name, "visible") == "visible"]
    names_defined = defined_names(path)
    missing_required = [sheet for sheet in required_sheets if sheet not in sheet_paths]
    missing_formula_sheets = [
        sheet for sheet in formula_sheet_requirements if formula_counts_by_sheet.get(sheet, 0) <= 0
    ]
    return {
        "workbook_type": workbook_type,
        "sheet_names": sheet_names,
        "sheet_states": sheet_states,
        "first_visible_sheet": visible[0] if visible else "",
        "cover_first": bool(visible and visible[0] == "Cover"),
        "required_sheets_present": not missing_required,
        "missing_required_sheets": missing_required,
        "formula_count": formula_count,
        "minimum_formula_count": min_formulas,
        "formula_count_passes_threshold": formula_count >= min_formulas,
        "formula_counts_by_sheet": formula_counts_by_sheet,
        "formula_sheets": sum(1 for count in formula_counts_by_sheet.values() if count > 0),
        "required_formula_sheets": list(formula_sheet_requirements),
        "missing_formula_sheets": missing_formula_sheets,
        "required_formula_sheets_populated": not missing_formula_sheets,
        "defined_names": names_defined,
        "named_ranges_count": len(names_defined),
        "has_named_ranges": bool(names_defined),
        "has_styles": has_styles,
        "external_links": external_links,
        "no_external_links": not external_links,
    }
