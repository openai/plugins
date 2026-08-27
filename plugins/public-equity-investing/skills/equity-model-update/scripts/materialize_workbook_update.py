#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))

from model_update_artifacts import build_change_log, build_tieout_checklist
from model_update_core import output_paths
from model_update_dates import parse_date
from model_update_fields import CHANGE_LOG_FIELDS, SOURCE_TO_MODEL_FIELDS, TIEOUT_FIELDS, TRUTHY
from model_update_format import text
from model_update_io import load_rows, write_csv, write_run_log
from model_update_rows import build_source_to_model_rows

NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_DOC_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
NS_CONTENT_TYPES = "http://schemas.openxmlformats.org/package/2006/content-types"
NS_XML = "http://www.w3.org/XML/1998/namespace"

REL_TYPE_WORKSHEET = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"
WORKSHEET_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"

CELL_RE = re.compile(r"^([A-Za-z]{1,3})([1-9][0-9]*)$")


def qn(ns: str, name: str) -> str:
    return f"{{{ns}}}{name}"


def xml_bytes(root: ET.Element) -> bytes:
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def col_to_num(col: str) -> int:
    number = 0
    for char in col.upper():
        number = number * 26 + ord(char) - ord("A") + 1
    return number


def num_to_col(number: int) -> str:
    col = ""
    while number:
        number, rem = divmod(number - 1, 26)
        col = chr(ord("A") + rem) + col
    return col


def parse_cell_ref(cell_ref: str) -> tuple[int, int] | None:
    match = CELL_RE.match(cell_ref.strip())
    if not match:
        return None
    return col_to_num(match.group(1)), int(match.group(2))


def normalize_cell_ref(cell_ref: str) -> str:
    parsed = parse_cell_ref(cell_ref)
    if parsed is None:
        return cell_ref.strip()
    col, row = parsed
    return f"{num_to_col(col)}{row}"


def cell_in_range(cell_ref: str, range_ref: str) -> bool:
    if ":" not in range_ref:
        return normalize_cell_ref(cell_ref) == normalize_cell_ref(range_ref)
    start_ref, end_ref = range_ref.split(":", 1)
    cell = parse_cell_ref(cell_ref)
    start = parse_cell_ref(start_ref)
    end = parse_cell_ref(end_ref)
    if cell is None or start is None or end is None:
        return False
    cell_col, cell_row = cell
    start_col, start_row = start
    end_col, end_row = end
    return min(start_col, end_col) <= cell_col <= max(start_col, end_col) and min(
        start_row, end_row
    ) <= cell_row <= max(start_row, end_row)


def values_equivalent(left: str, right: str) -> bool:
    left_clean = left.strip()
    right_clean = right.strip()
    if left_clean == right_clean:
        return True
    try:
        return abs(float(left_clean.replace(",", "")) - float(right_clean.replace(",", ""))) < 1e-9
    except ValueError:
        return False


def is_truthy(value: str) -> bool:
    return text(value).lower() in TRUTHY


def unique_sheet_name(base: str, existing: set[str]) -> str:
    candidate = base[:31]
    counter = 2
    while candidate in existing:
        suffix = f"_{counter}"
        candidate = f"{base[: 31 - len(suffix)]}{suffix}"
        counter += 1
    existing.add(candidate)
    return candidate


def slug(value: str) -> str:
    clean = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return clean or "row"


@dataclass
class WorkbookInspection:
    sheet_paths: dict[str, str]
    first_visible_sheet: str
    hidden_sheets: list[str]
    protected_sheets: list[str]
    named_ranges: list[str]
    external_links: list[str]
    has_vba: bool
    calc_chain_present: bool
    formula_cell_count: int
    cached_formula_value_count: int
    calc_mode: str
    full_calc_on_load: str
    force_full_calc: str
    max_sheet_id: int
    max_relationship_id: int
    used_sheet_numbers: set[int]

    def as_dict(self, *, recalc_required: bool = False) -> dict[str, object]:
        return {
            "sheet_names": list(self.sheet_paths),
            "first_visible_sheet": self.first_visible_sheet,
            "hidden_sheets": self.hidden_sheets,
            "hidden_sheet_count": len(self.hidden_sheets),
            "protected_sheets": self.protected_sheets,
            "protected_sheet_count": len(self.protected_sheets),
            "named_ranges": self.named_ranges,
            "named_range_count": len(self.named_ranges),
            "external_links": self.external_links,
            "external_link_count": len(self.external_links),
            "has_vba": self.has_vba,
            "calc_chain_present": self.calc_chain_present,
            "formula_cell_count": self.formula_cell_count,
            "cached_formula_value_count": self.cached_formula_value_count,
            "calc_mode": self.calc_mode,
            "full_calc_on_load": self.full_calc_on_load,
            "force_full_calc": self.force_full_calc,
            "recalc_required": recalc_required,
        }


def load_zip_entries(path: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(path) as zf:
        return {name: zf.read(name) for name in zf.namelist()}


def relationship_target_to_path(target: str) -> str:
    target = target.replace("\\", "/")
    if target.startswith("/"):
        return target.lstrip("/")
    if target.startswith("xl/"):
        return target
    return f"xl/{target}"


def inspect_workbook(
    entries: dict[str, bytes],
) -> tuple[WorkbookInspection, ET.Element, ET.Element, ET.Element]:
    required = {"xl/workbook.xml", "xl/_rels/workbook.xml.rels", "[Content_Types].xml"}
    missing = sorted(required - set(entries))
    if missing:
        raise ValueError(f"workbook is missing required XLSX parts: {', '.join(missing)}")

    workbook_root = ET.fromstring(entries["xl/workbook.xml"])
    rels_root = ET.fromstring(entries["xl/_rels/workbook.xml.rels"])
    content_root = ET.fromstring(entries["[Content_Types].xml"])

    rel_targets = {
        rel.attrib["Id"]: relationship_target_to_path(rel.attrib.get("Target", ""))
        for rel in rels_root.findall(qn(NS_PKG_REL, "Relationship"))
    }
    sheets_parent = workbook_root.find(qn(NS_MAIN, "sheets"))
    if sheets_parent is None:
        raise ValueError("workbook has no sheets collection")

    sheet_paths: dict[str, str] = {}
    hidden_sheets: list[str] = []
    first_visible_sheet = ""
    max_sheet_id = 0
    used_sheet_numbers: set[int] = set()

    for sheet in sheets_parent.findall(qn(NS_MAIN, "sheet")):
        name = sheet.attrib.get("name", "")
        state = sheet.attrib.get("state", "visible")
        rid = sheet.attrib.get(qn(NS_DOC_REL, "id"), "")
        target = rel_targets.get(rid, "")
        if not name or not target:
            continue
        sheet_paths[name] = target
        if state != "visible":
            hidden_sheets.append(name)
        elif not first_visible_sheet:
            first_visible_sheet = name
        try:
            max_sheet_id = max(max_sheet_id, int(sheet.attrib.get("sheetId", "0")))
        except ValueError:
            pass
        match = re.search(r"sheet([0-9]+)\.xml$", target)
        if match:
            used_sheet_numbers.add(int(match.group(1)))

    protected_sheets: list[str] = []
    formula_cell_count = 0
    cached_formula_value_count = 0
    for name, path in sheet_paths.items():
        if path in entries:
            root = ET.fromstring(entries[path])
            if root.find(qn(NS_MAIN, "sheetProtection")) is not None:
                protected_sheets.append(name)
            for cell in root.iter(qn(NS_MAIN, "c")):
                formula = cell.find(qn(NS_MAIN, "f"))
                if formula is not None:
                    formula_cell_count += 1
                    value = cell.find(qn(NS_MAIN, "v"))
                    if value is not None and value.text not in (None, ""):
                        cached_formula_value_count += 1

    named_ranges: list[str] = []
    defined_names = workbook_root.find(qn(NS_MAIN, "definedNames"))
    if defined_names is not None:
        for defined_name in defined_names.findall(qn(NS_MAIN, "definedName")):
            name = defined_name.attrib.get("name", "")
            if name:
                named_ranges.append(name)

    max_relationship_id = 0
    for rel in rels_root.findall(qn(NS_PKG_REL, "Relationship")):
        match = re.match(r"rId([0-9]+)$", rel.attrib.get("Id", ""))
        if match:
            max_relationship_id = max(max_relationship_id, int(match.group(1)))

    calc_pr = workbook_root.find(qn(NS_MAIN, "calcPr"))
    calc_mode = calc_pr.attrib.get("calcMode", "auto") if calc_pr is not None else "auto"
    full_calc_on_load = calc_pr.attrib.get("fullCalcOnLoad", "") if calc_pr is not None else ""
    force_full_calc = calc_pr.attrib.get("forceFullCalc", "") if calc_pr is not None else ""

    inspection = WorkbookInspection(
        sheet_paths=sheet_paths,
        first_visible_sheet=first_visible_sheet,
        hidden_sheets=hidden_sheets,
        protected_sheets=protected_sheets,
        named_ranges=named_ranges,
        external_links=sorted(name for name in entries if name.startswith("xl/externalLinks/")),
        has_vba="xl/vbaProject.bin" in entries,
        calc_chain_present="xl/calcChain.xml" in entries,
        formula_cell_count=formula_cell_count,
        cached_formula_value_count=cached_formula_value_count,
        calc_mode=calc_mode,
        full_calc_on_load=full_calc_on_load,
        force_full_calc=force_full_calc,
        max_sheet_id=max_sheet_id,
        max_relationship_id=max_relationship_id,
        used_sheet_numbers=used_sheet_numbers,
    )
    return inspection, workbook_root, rels_root, content_root


def read_shared_strings(entries: dict[str, bytes]) -> list[str]:
    if "xl/sharedStrings.xml" not in entries:
        return []
    root = ET.fromstring(entries["xl/sharedStrings.xml"])
    values: list[str] = []
    for si in root.findall(qn(NS_MAIN, "si")):
        fragments = [node.text or "" for node in si.findall(f".//{qn(NS_MAIN, 't')}")]
        values.append("".join(fragments))
    return values


def find_cell(sheet_root: ET.Element, cell_ref: str) -> ET.Element | None:
    normalized = normalize_cell_ref(cell_ref)
    for cell in sheet_root.iter(qn(NS_MAIN, "c")):
        if cell.attrib.get("r") == normalized:
            return cell
    return None


def merged_ranges(sheet_root: ET.Element) -> list[str]:
    container = sheet_root.find(qn(NS_MAIN, "mergeCells"))
    if container is None:
        return []
    return [
        merge.attrib.get("ref", "")
        for merge in container.findall(qn(NS_MAIN, "mergeCell"))
        if merge.attrib.get("ref")
    ]


def cell_display_value(cell: ET.Element, shared_strings: list[str]) -> str:
    formula = cell.find(qn(NS_MAIN, "f"))
    if formula is not None:
        return f"={formula.text or ''}"
    cell_type = cell.attrib.get("t", "")
    if cell_type == "inlineStr":
        text_nodes = cell.findall(f".//{qn(NS_MAIN, 't')}")
        return "".join(node.text or "" for node in text_nodes)
    value = cell.find(qn(NS_MAIN, "v"))
    if value is None or value.text is None:
        return ""
    if cell_type == "s":
        try:
            return shared_strings[int(value.text)]
        except (ValueError, IndexError):
            return value.text
    if cell_type == "b":
        return "TRUE" if value.text == "1" else "FALSE"
    return value.text


def set_cell_value(cell: ET.Element, value: str) -> None:
    for child in list(cell):
        if child.tag in {qn(NS_MAIN, "f"), qn(NS_MAIN, "v"), qn(NS_MAIN, "is")}:
            cell.remove(child)

    raw = value.strip()
    try:
        float(raw.replace(",", ""))
        is_number = raw not in {"", ".", "-", "+"}
    except ValueError:
        is_number = False

    if is_number:
        cell.attrib.pop("t", None)
        value_node = ET.SubElement(cell, qn(NS_MAIN, "v"))
        value_node.text = raw.replace(",", "")
    else:
        cell.attrib["t"] = "inlineStr"
        inline = ET.SubElement(cell, qn(NS_MAIN, "is"))
        text_node = ET.SubElement(inline, qn(NS_MAIN, "t"))
        if raw != value:
            text_node.attrib[qn(NS_XML, "space")] = "preserve"
        text_node.text = value


def content_namespace(root: ET.Element) -> str:
    if root.tag.startswith("{"):
        return root.tag[1:].split("}", 1)[0]
    return NS_CONTENT_TYPES


def table_sheet_xml(rows: list[list[object]]) -> bytes:
    worksheet = ET.Element(qn(NS_MAIN, "worksheet"))
    sheet_data = ET.SubElement(worksheet, qn(NS_MAIN, "sheetData"))
    for row_index, row_values in enumerate(rows, start=1):
        row = ET.SubElement(sheet_data, qn(NS_MAIN, "row"), {"r": str(row_index)})
        for col_index, value in enumerate(row_values, start=1):
            cell_ref = f"{num_to_col(col_index)}{row_index}"
            cell = ET.SubElement(row, qn(NS_MAIN, "c"), {"r": cell_ref, "t": "inlineStr"})
            inline = ET.SubElement(cell, qn(NS_MAIN, "is"))
            text_node = ET.SubElement(inline, qn(NS_MAIN, "t"))
            cell_text = "" if value is None else str(value)
            if cell_text != cell_text.strip():
                text_node.attrib[qn(NS_XML, "space")] = "preserve"
            text_node.text = cell_text
    return xml_bytes(worksheet)


def next_sheet_number(used: set[int]) -> int:
    number = 1
    while number in used:
        number += 1
    used.add(number)
    return number


def shift_sheet_scoped_defined_names_for_inserted_first_sheet(workbook_root: ET.Element) -> None:
    defined_names = workbook_root.find(qn(NS_MAIN, "definedNames"))
    if defined_names is None:
        return
    for defined_name in defined_names.findall(qn(NS_MAIN, "definedName")):
        local_sheet_id = defined_name.attrib.get("localSheetId")
        if local_sheet_id is None:
            continue
        try:
            defined_name.set("localSheetId", str(int(local_sheet_id) + 1))
        except ValueError:
            continue


def append_review_sheets(
    entries: dict[str, bytes],
    workbook_root: ET.Element,
    rels_root: ET.Element,
    content_root: ET.Element,
    inspection: WorkbookInspection,
    tables: dict[str, list[list[object]]],
    *,
    promote_cover: bool = False,
) -> None:
    sheets_parent = workbook_root.find(qn(NS_MAIN, "sheets"))
    if sheets_parent is None:
        raise ValueError("workbook has no sheets collection")

    existing_names = set(inspection.sheet_paths)
    sheet_id = inspection.max_sheet_id
    rel_id = inspection.max_relationship_id
    ct_ns = content_namespace(content_root)

    for base_name, table_rows in tables.items():
        sheet_id += 1
        rel_id += 1
        sheet_number = next_sheet_number(inspection.used_sheet_numbers)
        sheet_name = unique_sheet_name(base_name, existing_names)
        sheet_path = f"xl/worksheets/sheet{sheet_number}.xml"
        target = f"worksheets/sheet{sheet_number}.xml"
        rid = f"rId{rel_id}"

        sheet = ET.Element(
            qn(NS_MAIN, "sheet"),
            {"name": sheet_name, "sheetId": str(sheet_id), qn(NS_DOC_REL, "id"): rid},
        )
        if promote_cover and base_name == "Update_Cover":
            shift_sheet_scoped_defined_names_for_inserted_first_sheet(workbook_root)
            sheets_parent.insert(0, sheet)
            book_views = workbook_root.find(qn(NS_MAIN, "bookViews"))
            if book_views is None:
                book_views = ET.Element(qn(NS_MAIN, "bookViews"))
                workbook_root.insert(list(workbook_root).index(sheets_parent), book_views)
            workbook_view = book_views.find(qn(NS_MAIN, "workbookView"))
            if workbook_view is None:
                workbook_view = ET.SubElement(book_views, qn(NS_MAIN, "workbookView"))
            workbook_view.set("activeTab", "0")
            workbook_view.set("firstSheet", "0")
        else:
            sheets_parent.append(sheet)
        ET.SubElement(
            rels_root,
            qn(NS_PKG_REL, "Relationship"),
            {"Id": rid, "Type": REL_TYPE_WORKSHEET, "Target": target},
        )
        ET.SubElement(
            content_root,
            qn(ct_ns, "Override"),
            {"PartName": f"/{sheet_path}", "ContentType": WORKSHEET_CONTENT_TYPE},
        )
        entries[sheet_path] = table_sheet_xml(table_rows)


def source_basis(source_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {
            "source_id": row.get("source_id", ""),
            "source_name": row.get("source_name", ""),
            "source_location": row.get("source_location", ""),
            "evidence_label": row.get("evidence_label", ""),
            "as_of_date": row.get("as_of_date", ""),
            "confidence": row.get("confidence", ""),
        }
        for row in source_rows
        if row.get("source_id")
    ]


def build_citation(row: dict[str, str], index: int, workbook_path: Path) -> dict[str, object]:
    sheet = row.get("workbook_sheet", "")
    cell = row.get("workbook_cell", "")
    source_id = row.get("source_id", "")
    model_line = row.get("model_line", "")
    citation_id = (
        f"model-update:{slug(source_id or model_line or str(index))}:{slug(sheet)}:{slug(cell)}"
    )
    treatment = row.get("mapping_treatment", "")
    if treatment == "reference_only":
        citation_title = f"{model_line} workbook reference"
        citation_label = "Model Reference"
        citation_type = "model_reference_cell"
    elif treatment in {"missing_model_architecture", "rebuild_required"}:
        citation_title = f"{model_line} rebuild requirement"
        citation_label = "Rebuild Required"
        citation_type = "model_rebuild_requirement"
    elif treatment == "assumption_required":
        citation_title = f"{model_line} assumption review"
        citation_label = "Assumption Review"
        citation_type = "model_assumption_review"
    else:
        citation_title = f"{model_line} workbook update"
        citation_label = "Model Update"
        citation_type = "model_update_cell"
    return {
        "id": citation_id,
        "title": citation_title,
        "short_label": f"{citation_label}: {sheet}!{cell}" if sheet and cell else citation_label,
        "type": citation_type,
        "workbook_path": str(workbook_path),
        "sheet": sheet,
        "cell": cell,
        "range": cell,
        "prior_value": row.get("prior_value", ""),
        "new_value": row.get("new_value", "") or row.get("proposed_model_value", ""),
        "model_line": model_line,
        "source_id": source_id,
        "source_label": row.get("source_name", "") or row.get("evidence_label", ""),
        "source_date": row.get("as_of_date", ""),
        "freshness": row.get("freshness_status", ""),
        "confidence": row.get("confidence", ""),
        "update_action": row.get("update_action", ""),
        "mapping_treatment": treatment,
        "applied": row.get("applied_to_workbook") == "yes",
        "blocked_reason": row.get("blocked_reason", ""),
    }


def apply_workbook_updates(
    entries: dict[str, bytes],
    inspection: WorkbookInspection,
    source_rows: list[dict[str, str]],
    force_review_reason: str | None,
) -> tuple[list[dict[str, str]], list[str], dict[str, int]]:
    updated_rows = [deepcopy(row) for row in source_rows]
    shared_strings = read_shared_strings(entries)
    warnings: list[str] = []
    counts = {
        "target_row_count": 0,
        "applied_count": 0,
        "blocked_count": 0,
        "no_change_count": 0,
        "reference_only_count": 0,
        "missing_architecture_count": 0,
        "rebuild_required_count": 0,
        "assumption_required_count": 0,
    }
    parsed_sheets: dict[str, ET.Element] = {}
    dirty_sheet_paths: set[str] = set()

    for row in updated_rows:
        treatment = text(row.get("mapping_treatment"))
        if treatment == "reference_only":
            row["review_status"] = "reference_only"
            row["applied_to_workbook"] = "no"
            row["blocked_reason"] = ""
            counts["reference_only_count"] += 1
            continue
        if treatment in {
            "missing_model_architecture",
            "rebuild_required",
            "assumption_required",
        }:
            row["applied_to_workbook"] = "no"
            counts["blocked_count"] += 1
            if treatment == "missing_model_architecture":
                counts["missing_architecture_count"] += 1
            elif treatment == "rebuild_required":
                counts["rebuild_required_count"] += 1
            else:
                counts["assumption_required_count"] += 1
            continue
        sheet = text(row.get("workbook_sheet"))
        cell_ref = normalize_cell_ref(text(row.get("workbook_cell")))
        new_value = text(row.get("new_value")) or text(row.get("proposed_model_value"))
        action = text(row.get("update_action"))
        if not sheet and not cell_ref:
            row["blocked_reason"] = "missing_workbook_target"
            row["review_status"] = "control_pack_review"
            counts["blocked_count"] += 1
            continue

        counts["target_row_count"] += 1
        row["workbook_cell"] = cell_ref

        if force_review_reason:
            row["blocked_reason"] = force_review_reason
        elif not sheet:
            row["blocked_reason"] = "missing_workbook_sheet"
        elif not cell_ref or parse_cell_ref(cell_ref) is None:
            row["blocked_reason"] = "missing_or_invalid_workbook_cell"
        elif not new_value:
            row["blocked_reason"] = "missing_new_value"
        elif sheet not in inspection.sheet_paths:
            row["blocked_reason"] = "workbook_sheet_not_found"
        elif sheet in inspection.protected_sheets:
            row["blocked_reason"] = "protected_sheet"
        elif action == "no_change":
            row["review_status"] = "no_change"
            row["applied_to_workbook"] = "no"
            counts["no_change_count"] += 1
            continue

        if row.get("blocked_reason"):
            row["review_status"] = "control_pack_review"
            row["applied_to_workbook"] = "no"
            counts["blocked_count"] += 1
            continue

        sheet_path = inspection.sheet_paths[sheet]
        sheet_root = parsed_sheets.get(sheet_path)
        if sheet_root is None:
            sheet_root = ET.fromstring(entries[sheet_path])
            parsed_sheets[sheet_path] = sheet_root

        if any(cell_in_range(cell_ref, range_ref) for range_ref in merged_ranges(sheet_root)):
            row["blocked_reason"] = "merged_cell_target"
            row["review_status"] = "control_pack_review"
            row["applied_to_workbook"] = "no"
            counts["blocked_count"] += 1
            continue

        cell = find_cell(sheet_root, cell_ref)
        if cell is None:
            row["blocked_reason"] = "workbook_cell_not_found"
            row["review_status"] = "control_pack_review"
            row["applied_to_workbook"] = "no"
            counts["blocked_count"] += 1
            continue

        formula = cell.find(qn(NS_MAIN, "f"))
        if formula is not None and not is_truthy(row.get("overwrite_formula_allowed", "")):
            row["blocked_reason"] = "formula_cell_not_overwritten_without_approval"
            row["review_status"] = "control_pack_review"
            row["applied_to_workbook"] = "no"
            counts["blocked_count"] += 1
            continue

        prior_from_workbook = cell_display_value(cell, shared_strings)
        supplied_prior = text(row.get("prior_value")) or text(row.get("current_model_value"))
        row["prior_value"] = prior_from_workbook
        if (
            supplied_prior
            and prior_from_workbook
            and not values_equivalent(supplied_prior, prior_from_workbook)
        ):
            row["blocked_reason"] = "prior_value_mismatch"
            row["review_status"] = "control_pack_review"
            row["applied_to_workbook"] = "no"
            counts["blocked_count"] += 1
            continue

        if formula is not None:
            warnings.append(
                f"{sheet}!{cell_ref}: formula overwritten because overwrite_formula_allowed was explicit"
            )
        set_cell_value(cell, new_value)
        row["applied_to_workbook"] = "yes"
        row["blocked_reason"] = ""
        row["review_status"] = "applied_to_copy"
        counts["applied_count"] += 1
        dirty_sheet_paths.add(sheet_path)

    for sheet_path in dirty_sheet_paths:
        entries[sheet_path] = xml_bytes(parsed_sheets[sheet_path])
    return updated_rows, warnings, counts


def cover_rows(
    *,
    mode: str,
    original_workbook: Path,
    output_workbook: Path,
    inspection: WorkbookInspection,
    counts: dict[str, int],
    warnings: list[str],
    failures: list[str],
) -> list[list[object]]:
    artifact_readiness = "not_ready" if failures else "ready_for_review"
    model_readiness = (
        "not_ready_validation_failure"
        if failures
        else "updated_requires_tieout"
        if mode == "xlsx_update_copy"
        else "not_updated_requires_mapping_or_rebuild"
    )
    rows: list[list[object]] = [
        ["Equity Model Update", "Safe workbook update copy"],
        ["Status", "failed" if failures else "completed"],
        ["Artifact readiness", artifact_readiness],
        ["Model readiness", model_readiness],
        ["Workbook mode", mode],
        ["Original workbook", str(original_workbook)],
        ["Output workbook", str(output_workbook)],
        ["First visible sheet preserved", inspection.first_visible_sheet],
        ["Target rows", counts.get("target_row_count", 0)],
        ["Applied updates", counts.get("applied_count", 0)],
        ["Blocked updates", counts.get("blocked_count", 0)],
        ["Reference-only facts", counts.get("reference_only_count", 0)],
        ["Missing model architecture", counts.get("missing_architecture_count", 0)],
        ["Rebuild-required rows", counts.get("rebuild_required_count", 0)],
        ["Assumption-required rows", counts.get("assumption_required_count", 0)],
        ["No-change rows", counts.get("no_change_count", 0)],
        ["External links detected", len(inspection.external_links)],
        ["Formula cells detected", inspection.formula_cell_count],
        ["Cached formula values detected", inspection.cached_formula_value_count],
        ["Calc chain present", "yes" if inspection.calc_chain_present else "no"],
        ["Workbook calc mode", inspection.calc_mode],
        [
            "Excel/Sheets recalculation required",
            "yes" if counts.get("applied_count") and inspection.formula_cell_count else "no",
        ],
        ["Hidden sheets detected", len(inspection.hidden_sheets)],
        ["Protected sheets detected", len(inspection.protected_sheets)],
        ["Named ranges detected", len(inspection.named_ranges)],
        ["VBA/macros detected", "yes" if inspection.has_vba else "no"],
        ["Next handoff", "model-audit-tieout for formula integrity and final tie-out"],
        [],
        ["Warnings"],
    ]
    rows.extend([[warning] for warning in warnings] or [["None"]])
    if failures:
        rows.append([])
        rows.append(["Hard failures"])
        rows.extend([[failure] for failure in failures])
    return rows


def dict_rows_table(
    title: str, rows: list[dict[str, str]], fields: list[str]
) -> list[list[object]]:
    return [[title], fields] + [[row.get(field, "") for field in fields] for row in rows]


def stale_rows(source_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        row
        for row in source_rows
        if row.get("freshness_status") in {"stale", "unknown"}
        or "missing" in row.get("issue_flags", "")
    ]


def rebuild_rows(source_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        row
        for row in source_rows
        if row.get("mapping_treatment")
        in {"missing_model_architecture", "rebuild_required", "assumption_required"}
    ]


def write_workbook(entries: dict[str, bytes], output_path: Path) -> None:
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, payload in entries.items():
            zf.writestr(name, payload)


def workbook_output_paths(out_dir: Path, workbook_key: str, workbook_path: Path) -> dict[str, str]:
    paths = output_paths(out_dir)
    return {
        workbook_key: str(workbook_path),
        "source_to_model": paths["source_to_model"],
        "change_log": paths["change_log"],
        "tieout_checklist": paths["tieout_checklist"],
        "model_update_citations": str(out_dir / "model_update_citations.json"),
        "run_log": paths["run_log"],
        "manifest": paths["manifest"],
    }


def materialize_workbook_update(
    input_csv: Path,
    workbook: Path,
    out_dir: Path,
    run_date: datetime,
    stale_days: int,
) -> int:
    rows = load_rows(input_csv)
    out_dir.mkdir(parents=True, exist_ok=True)

    source_rows, warnings, failures = build_source_to_model_rows(rows, run_date, stale_days)
    entries = load_zip_entries(workbook)
    inspection, workbook_root, rels_root, content_root = inspect_workbook(entries)
    source_rows, workbook_warnings, counts = apply_workbook_updates(
        entries,
        inspection,
        source_rows,
        force_review_reason=(
            "input_validation_failure"
            if failures
            else "macro_enabled_workbook_requires_manual_review"
            if inspection.has_vba
            else None
        ),
    )
    warnings.extend(workbook_warnings)
    warnings.extend(
        [
            "workbook has external links; final tie-out should confirm links/calculation integrity"
            if inspection.external_links
            else "",
            "workbook contains formulas with cached values; this runtime edited copied input cells but does not recalculate downstream formula caches. Open in Excel/Sheets and recalculate, then run model-audit-tieout before relying on formula outputs."
            if counts["applied_count"] and inspection.formula_cell_count
            else "",
            "workbook formula outputs were inspected as cached values; no model inputs were updated in this control pack, so it is not a refreshed valuation."
            if not counts["applied_count"] and inspection.formula_cell_count
            else "",
            "workbook calc mode is manual; recalculation is required after applied input updates"
            if counts["applied_count"] and inspection.calc_mode.lower() == "manual"
            else "",
            "calcChain.xml is present; downstream formula dependency chain may be stale after copied input updates"
            if counts["applied_count"] and inspection.calc_chain_present
            else "",
            "macro-enabled workbook detected; model cells were routed to review instead of edited"
            if inspection.has_vba
            else "",
        ]
    )
    warnings = [warning for warning in warnings if warning]
    mode = "xlsx_update_copy" if counts["applied_count"] else "xlsx_control_pack"
    workbook_key = "updated_model" if mode == "xlsx_update_copy" else "model_update_control_pack"
    suffix = ".xlsm" if workbook.suffix.lower() == ".xlsm" or inspection.has_vba else ".xlsx"
    workbook_name = f"{workbook_key}{suffix}"
    output_workbook = out_dir / workbook_name
    outputs = workbook_output_paths(out_dir, workbook_key, output_workbook)

    change_log = build_change_log(source_rows)
    tieout = build_tieout_checklist(source_rows)
    review_tables = {
        "Update_Cover": cover_rows(
            mode=mode,
            original_workbook=workbook,
            output_workbook=output_workbook,
            inspection=inspection,
            counts=counts,
            warnings=warnings,
            failures=failures,
        ),
        "Source_Map": dict_rows_table("Source-to-model map", source_rows, SOURCE_TO_MODEL_FIELDS),
        "Rebuild_Requirements": dict_rows_table(
            "Missing architecture or rebuild requirements",
            rebuild_rows(source_rows),
            SOURCE_TO_MODEL_FIELDS,
        ),
        "Change_Log": dict_rows_table("Change log", change_log, CHANGE_LOG_FIELDS),
        "Tie_Out": dict_rows_table("Tie-out checklist", tieout, TIEOUT_FIELDS),
        "Stale_Data": dict_rows_table(
            "Stale or missing source rows", stale_rows(source_rows), SOURCE_TO_MODEL_FIELDS
        ),
    }
    append_review_sheets(
        entries,
        workbook_root,
        rels_root,
        content_root,
        inspection,
        review_tables,
        promote_cover=mode == "xlsx_control_pack",
    )
    entries["xl/workbook.xml"] = xml_bytes(workbook_root)
    entries["xl/_rels/workbook.xml.rels"] = xml_bytes(rels_root)
    entries["[Content_Types].xml"] = xml_bytes(content_root)

    write_workbook(entries, output_workbook)
    write_csv(out_dir / "source_to_model.csv", source_rows, SOURCE_TO_MODEL_FIELDS)
    write_csv(out_dir / "change_log.csv", change_log, CHANGE_LOG_FIELDS)
    write_csv(out_dir / "tieout_checklist.csv", tieout, TIEOUT_FIELDS)

    citation_rows = [
        build_citation(row, index, output_workbook)
        for index, row in enumerate(source_rows, start=1)
        if row.get("workbook_sheet") or row.get("workbook_cell")
    ]
    citations = {
        "model_citations": citation_rows,
        "model_update_citations": citation_rows,
    }
    (out_dir / "model_update_citations.json").write_text(
        json.dumps(citations, indent=2) + "\n", encoding="utf-8"
    )

    status = "failed" if failures else "completed"
    write_run_log(
        out_dir / "run_log.json",
        status=status,
        input_path=input_csv,
        row_count=len(rows),
        outputs=outputs,
        warnings=warnings,
        failures=failures,
        source_basis=source_basis(source_rows),
        artifact_level="workbook_update",
        workbook_mode=mode,
        primary_human_deliverable=str(output_workbook),
        workbook_preflight=inspection.as_dict(
            recalc_required=bool(counts.get("applied_count") and inspection.formula_cell_count)
        ),
        workbook_update_summary=counts,
        recalculation_warning={
            "recalc_required": bool(counts.get("applied_count") and inspection.formula_cell_count),
            "formula_cell_count": inspection.formula_cell_count,
            "cached_formula_value_count": inspection.cached_formula_value_count,
            "calc_chain_present": inspection.calc_chain_present,
            "calc_mode": inspection.calc_mode,
            "runtime_recalculated_formulas": False,
            "required_next_step": (
                "Open the copied workbook in Excel/Sheets, recalculate, save, and run model-audit-tieout before relying on formula outputs."
                if counts.get("applied_count") and inspection.formula_cell_count
                else "No recalculation is required from this run because no model cells were changed; map safe inputs or rebuild the forecast architecture before refreshing valuation."
            ),
        },
        capability_boundary=(
            "safe copied-workbook updater; original workbook is never mutated, formulas are preserved unless "
            "overwrite_formula_allowed is explicit, blocked targets are surfaced in review tabs, and formula caches are not recalculated by this runtime"
        ),
    )
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1
    print(f"Wrote equity model update workbook package to {out_dir}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Safely materialize equity-model-update artifacts into a copied workbook package."
    )
    parser.add_argument("input_csv", type=Path, help="CSV with source/model/workbook mapping rows.")
    parser.add_argument(
        "--workbook",
        required=True,
        type=Path,
        help="Uploaded XLSX/XLSM workbook to copy and update.",
    )
    parser.add_argument("--out", type=Path, default=Path("output"), help="Output directory.")
    parser.add_argument(
        "--run-date",
        default=datetime.now(timezone.utc).date().isoformat(),
        help="Run date used by freshness checks, YYYY-MM-DD.",
    )
    parser.add_argument("--stale-days", type=int, default=45, help="Stale threshold in days.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    run_date = parse_date(args.run_date)
    if run_date is None:
        print("ERROR: --run-date must be parseable as YYYY-MM-DD")
        return 1
    try:
        return materialize_workbook_update(
            args.input_csv, args.workbook, args.out, run_date, args.stale_days
        )
    except Exception as exc:
        args.out.mkdir(parents=True, exist_ok=True)
        outputs = output_paths(args.out)
        write_run_log(
            args.out / "run_log.json",
            status="failed",
            input_path=args.input_csv,
            row_count=0,
            outputs=outputs,
            warnings=[],
            failures=[str(exc)],
            artifact_level="workbook_update",
            workbook_mode="xlsx_update_failed",
            capability_boundary="safe copied-workbook updater failed before workbook materialization",
        )
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
