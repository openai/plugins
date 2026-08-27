"""Workbook-first regressions for equity-model-update."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "equity-model-update" / "scripts" / "materialize_workbook_update.py"
CSV_SCRIPT = ROOT / "skills" / "equity-model-update" / "scripts" / "materialize_model_update.py"
NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"

sys.path.insert(0, str(ROOT))

from shared.dashboard.qa import load_payload, validate_payload  # noqa: E402
from shared.dashboard.renderer import render_dashboard  # noqa: E402


def qn(ns: str, name: str) -> str:
    return f"{{{ns}}}{name}"


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    fields = sorted({field for row in rows for field in row})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_minimal_workbook(
    path: Path, *, formula_cell: bool = False, local_defined_name: bool = False
) -> None:
    b2 = '<c r="B2"><f>A1+A2</f><v>3</v></c>' if formula_cell else '<c r="B2"><v>10</v></c>'
    sheet_scoped_name = (
        '<definedName name="_xlnm.Print_Area" localSheetId="0">\'Inputs\'!$A$1:$B$2</definedName>'
        if local_defined_name
        else ""
    )
    sheet_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="{NS_MAIN}" xmlns:r="{NS_REL}">
  <sheetData>
    <row r="1"><c r="A1"><v>1</v></c></row>
    <row r="2"><c r="A2"><v>2</v></c>{b2}</row>
  </sheetData>
</worksheet>
"""
    workbook_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="{NS_MAIN}" xmlns:r="{NS_REL}">
  <sheets>
    <sheet name="Inputs" sheetId="1" r:id="rId1"/>
  </sheets>
  <definedNames><definedName name="Input_Cell">'Inputs'!$B$2</definedName>{sheet_scoped_name}</definedNames>
</workbook>
"""
    workbook_rels = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="{NS_PKG_REL}">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
</Relationships>
"""
    root_rels = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="{NS_PKG_REL}">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>
"""
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>
"""
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", root_rels)
        zf.writestr("xl/workbook.xml", workbook_xml)
        zf.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
        zf.writestr("xl/worksheets/sheet1.xml", sheet_xml)


def add_manual_calc_metadata(path: Path) -> None:
    with zipfile.ZipFile(path) as zf:
        entries = {info.filename: zf.read(info.filename) for info in zf.infolist()}

    workbook_xml = entries["xl/workbook.xml"].decode("utf-8")
    workbook_xml = workbook_xml.replace(
        f'<workbook xmlns="{NS_MAIN}" xmlns:r="{NS_REL}">',
        f'<workbook xmlns="{NS_MAIN}" xmlns:r="{NS_REL}"><calcPr calcMode="manual"/>',
    )
    entries["xl/workbook.xml"] = workbook_xml.encode("utf-8")
    entries["xl/calcChain.xml"] = (
        f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><calcChain xmlns="{NS_MAIN}"><c r="B2" i="1"/></calcChain>'
    ).encode("utf-8")

    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for filename, data in entries.items():
            zf.writestr(filename, data)


def workbook_sheet_paths(path: Path) -> dict[str, str]:
    with zipfile.ZipFile(path) as zf:
        workbook = ET.fromstring(zf.read("xl/workbook.xml"))
        rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
        relmap = {
            rel.attrib["Id"]: rel.attrib["Target"]
            for rel in rels.findall(qn(NS_PKG_REL, "Relationship"))
        }
        paths: dict[str, str] = {}
        sheets = workbook.find(qn(NS_MAIN, "sheets"))
        assert sheets is not None
        for sheet in sheets.findall(qn(NS_MAIN, "sheet")):
            target = relmap[sheet.attrib[qn(NS_REL, "id")]]
            paths[sheet.attrib["name"]] = (
                f"xl/{target.lstrip('/')}" if not target.startswith("xl/") else target
            )
        return paths


def workbook_sheet_names(path: Path) -> list[str]:
    return list(workbook_sheet_paths(path))


def defined_name_local_sheet_id(path: Path, name: str) -> str | None:
    with zipfile.ZipFile(path) as zf:
        workbook = ET.fromstring(zf.read("xl/workbook.xml"))
    defined_names = workbook.find(qn(NS_MAIN, "definedNames"))
    assert defined_names is not None
    for defined_name in defined_names.findall(qn(NS_MAIN, "definedName")):
        if defined_name.attrib.get("name") == name:
            return defined_name.attrib.get("localSheetId")
    return None


def read_cell(path: Path, sheet_name: str, cell_ref: str) -> str:
    with zipfile.ZipFile(path) as zf:
        sheet_path = workbook_sheet_paths(path)[sheet_name]
        root = ET.fromstring(zf.read(sheet_path))
        for cell in root.iter(qn(NS_MAIN, "c")):
            if cell.attrib.get("r") != cell_ref:
                continue
            formula = cell.find(qn(NS_MAIN, "f"))
            if formula is not None:
                return f"={formula.text or ''}"
            value = cell.find(qn(NS_MAIN, "v"))
            return "" if value is None or value.text is None else value.text
    return ""


def run_command(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=str(cwd), text=True, capture_output=True, check=False)


class EquityModelUpdateWorkbookTests(unittest.TestCase):
    def test_skill_requires_final_presentation_workbook_metadata_promotion(self) -> None:
        skill = (ROOT / "skills" / "equity-model-update" / "SKILL.md").read_text(encoding="utf-8")
        executable_contract = (
            ROOT / "skills" / "equity-model-update" / "references" / "executable-contract.md"
        ).read_text(encoding="utf-8")
        for phrase in [
            "final presentation workbook",
            "run_log.json",
            "manifest.json",
            "model_update_citations.json",
            "final sheet names",
        ]:
            self.assertIn(phrase, skill)
        self.assertIn("it replaces the intermediate workbook", executable_contract)

    def test_safe_workbook_update_copies_and_updates_mapped_input_cell(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            workbook = tmp_path / "model.xlsx"
            input_csv = tmp_path / "updates.csv"
            out_dir = tmp_path / "out"
            write_minimal_workbook(workbook)
            write_rows(
                input_csv,
                [
                    {
                        "company": "Northstar Instruments",
                        "ticker": "NSIS",
                        "fiscal_period": "FY2026",
                        "model_section": "Inputs",
                        "model_line": "Revenue growth",
                        "source_metric": "FY2026 revenue growth",
                        "current_model_value": "10",
                        "proposed_model_value": "12.5",
                        "workbook_sheet": "Inputs",
                        "workbook_cell": "B2",
                        "source_id": "src-release",
                        "source_name": "Company release",
                        "as_of_date": "2026-05-12",
                        "confidence": "high",
                    }
                ],
            )

            result = run_command(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(input_csv),
                    "--workbook",
                    str(workbook),
                    "--out",
                    str(out_dir),
                    "--run-date",
                    "2026-05-18",
                ],
                cwd=ROOT,
            )

            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            updated_workbook = out_dir / "updated_model.xlsx"
            self.assertTrue(updated_workbook.exists())
            self.assertEqual("10", read_cell(workbook, "Inputs", "B2"))
            self.assertEqual("12.5", read_cell(updated_workbook, "Inputs", "B2"))
            self.assertEqual("Inputs", workbook_sheet_names(updated_workbook)[0])
            for sheet in [
                "Update_Cover",
                "Source_Map",
                "Rebuild_Requirements",
                "Change_Log",
                "Tie_Out",
                "Stale_Data",
            ]:
                self.assertIn(sheet, workbook_sheet_names(updated_workbook))

            run_log = json.loads((out_dir / "run_log.json").read_text(encoding="utf-8"))
            manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
            citations = json.loads(
                (out_dir / "model_update_citations.json").read_text(encoding="utf-8")
            )
            source_rows = read_csv_rows(out_dir / "source_to_model.csv")

            self.assertEqual("xlsx_update_copy", run_log["workbook_mode"])
            self.assertEqual(str(updated_workbook), run_log["primary_human_deliverable"])
            self.assertEqual(str(updated_workbook), manifest["primary_human_deliverable"])
            self.assertEqual(1, run_log["workbook_update_summary"]["applied_count"])
            self.assertEqual("yes", source_rows[0]["applied_to_workbook"])
            self.assertEqual("applied_to_copy", source_rows[0]["review_status"])
            self.assertEqual("Inputs", citations["model_update_citations"][0]["sheet"])
            self.assertEqual("B2", citations["model_update_citations"][0]["cell"])
            self.assertTrue(citations["model_update_citations"][0]["applied"])
            self.assertEqual(citations["model_update_citations"], citations["model_citations"])

            citation_id = citations["model_citations"][0]["id"]
            payload_path = out_dir / "dashboard_payload.json"
            payload_path.write_text(
                json.dumps(
                    {
                        "kind": "public_equity_investing_dashboard.v1",
                        "mode": "equity_model_update",
                        "layout": "single_page",
                        "title": "NSIS model update",
                        "issuer": {"ticker": "NSIS"},
                        "metadata": {
                            "payload_stage": "production",
                            "freeze_time": "2026-05-18 09:00 ET",
                            "source_posture": "Synthetic workbook update fixture.",
                            "readiness_label": "PM-ready fixture",
                            "readiness_posture": "pm_ready",
                            "citation_policy": "strict",
                            "decision_context": "Whether the copied workbook update is ready for review.",
                        },
                        "hero": {
                            "headline": "NSIS copied-workbook update",
                            "dek": {
                                "value": "Inputs!B2 updated from source map",
                                "citations": [citation_id],
                            },
                            "callout": {
                                "value": "Safe update path used",
                                "citations": [citation_id],
                            },
                        },
                        "model_citations_path": "model_update_citations.json",
                        "snapshot": [
                            {
                                "label": "Updated cell",
                                "value": {"value": "Inputs!B2", "citations": [citation_id]},
                                "detail": "Safe copied-workbook update",
                            }
                        ],
                        "tabs": [
                            {
                                "id": "overview",
                                "label": "Overview",
                                "modules": [
                                    {
                                        "type": "decision_box",
                                        "data": {
                                            "stance": "Ready for review",
                                            "summary": {
                                                "value": "Inputs!B2 updated in copied workbook",
                                                "citations": [citation_id],
                                            },
                                        },
                                    }
                                ],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            loaded_payload = load_payload(payload_path)
            report = validate_payload(loaded_payload)
            html = render_dashboard(loaded_payload)
            self.assertEqual("passed", report["status"], report)
            self.assertIn("Inputs!B2; source: Company release", html)

    def test_formula_cell_routes_to_control_pack_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            workbook = tmp_path / "model.xlsx"
            input_csv = tmp_path / "updates.csv"
            out_dir = tmp_path / "out"
            write_minimal_workbook(workbook, formula_cell=True)
            write_rows(
                input_csv,
                [
                    {
                        "model_line": "Calculated revenue growth",
                        "source_metric": "FY2026 revenue growth",
                        "current_model_value": "3",
                        "proposed_model_value": "12.5",
                        "workbook_sheet": "Inputs",
                        "workbook_cell": "B2",
                        "source_id": "src-release",
                        "source_name": "Company release",
                        "as_of_date": "2026-05-12",
                    }
                ],
            )

            result = run_command(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(input_csv),
                    "--workbook",
                    str(workbook),
                    "--out",
                    str(out_dir),
                    "--run-date",
                    "2026-05-18",
                ],
                cwd=ROOT,
            )

            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            control_pack = out_dir / "model_update_control_pack.xlsx"
            self.assertTrue(control_pack.exists())
            self.assertEqual("=A1+A2", read_cell(control_pack, "Inputs", "B2"))
            run_log = json.loads((out_dir / "run_log.json").read_text(encoding="utf-8"))
            source_rows = read_csv_rows(out_dir / "source_to_model.csv")

            self.assertEqual("xlsx_control_pack", run_log["workbook_mode"])
            self.assertEqual(str(control_pack), run_log["primary_human_deliverable"])
            self.assertEqual(0, run_log["workbook_update_summary"]["applied_count"])
            self.assertEqual(1, run_log["workbook_update_summary"]["blocked_count"])
            self.assertEqual("Update_Cover", workbook_sheet_names(control_pack)[0])
            self.assertEqual("ready_for_review", run_log["artifact_readiness"])
            self.assertEqual("not_updated_requires_mapping_or_rebuild", run_log["model_readiness"])
            self.assertFalse(run_log["recalculation_warning"]["recalc_required"])
            self.assertIn(
                "No recalculation is required from this run",
                run_log["recalculation_warning"]["required_next_step"],
            )
            self.assertEqual("no", source_rows[0]["applied_to_workbook"])
            self.assertEqual(
                "formula_cell_not_overwritten_without_approval", source_rows[0]["blocked_reason"]
            )

    def test_reference_only_fact_does_not_become_an_update_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            workbook = tmp_path / "model.xlsx"
            input_csv = tmp_path / "updates.csv"
            out_dir = tmp_path / "out"
            write_minimal_workbook(workbook, formula_cell=True)
            write_rows(
                input_csv,
                [
                    {
                        "model_line": "Annual free cash flow forecast anchor",
                        "source_metric": "Q1 FY2027 reported free cash flow",
                        "source_value": "48.554",
                        "current_model_value": "33.750",
                        "mapping_treatment": "reference_only",
                        "workbook_sheet": "Inputs",
                        "workbook_cell": "B2",
                        "source_id": "src-release",
                        "as_of_date": "2026-05-12",
                        "notes": "Quarterly actual is not an annual forecast replacement.",
                    }
                ],
            )

            result = run_command(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(input_csv),
                    "--workbook",
                    str(workbook),
                    "--out",
                    str(out_dir),
                    "--run-date",
                    "2026-05-18",
                ],
                cwd=ROOT,
            )

            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            source_rows = read_csv_rows(out_dir / "source_to_model.csv")
            change_rows = read_csv_rows(out_dir / "change_log.csv")
            tieout_rows = read_csv_rows(out_dir / "tieout_checklist.csv")
            citations = json.loads(
                (out_dir / "model_update_citations.json").read_text(encoding="utf-8")
            )
            run_log = json.loads((out_dir / "run_log.json").read_text(encoding="utf-8"))

            self.assertEqual("reference_only", source_rows[0]["update_action"])
            self.assertEqual("reference_only", source_rows[0]["review_status"])
            self.assertEqual("", source_rows[0]["proposed_model_value"])
            self.assertEqual("", source_rows[0]["delta"])
            self.assertEqual([], change_rows)
            self.assertEqual("reference_only", tieout_rows[1]["status"])
            self.assertIn("retained only as a cited reference", tieout_rows[1]["check_description"])
            self.assertEqual("model_reference_cell", citations["model_citations"][0]["type"])
            self.assertEqual(
                "Annual free cash flow forecast anchor workbook reference",
                citations["model_citations"][0]["title"],
            )
            self.assertEqual(1, run_log["workbook_update_summary"]["reference_only_count"])
            self.assertEqual(0, run_log["workbook_update_summary"]["blocked_count"])

    def test_non_update_treatments_normalize_spaces_and_hyphens_before_workbook_edit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            workbook = tmp_path / "model.xlsx"
            input_csv = tmp_path / "updates.csv"
            out_dir = tmp_path / "out"
            write_minimal_workbook(workbook)
            write_rows(
                input_csv,
                [
                    {
                        "model_line": "Revenue forecast",
                        "source_metric": "Reported revenue",
                        "source_value": "99",
                        "current_model_value": "10",
                        "mapping_treatment": "reference-only",
                        "workbook_sheet": "Inputs",
                        "workbook_cell": "B2",
                        "source_id": "src-release",
                        "as_of_date": "2026-05-12",
                    },
                    {
                        "model_line": "Margin forecast",
                        "source_metric": "Reported margin",
                        "source_value": "88",
                        "current_model_value": "1",
                        "mapping_treatment": "missing model architecture",
                        "workbook_sheet": "Inputs",
                        "workbook_cell": "A1",
                        "source_id": "src-release",
                        "as_of_date": "2026-05-12",
                    },
                ],
            )

            result = run_command(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(input_csv),
                    "--workbook",
                    str(workbook),
                    "--out",
                    str(out_dir),
                    "--run-date",
                    "2026-05-18",
                ],
                cwd=ROOT,
            )

            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            control_pack = out_dir / "model_update_control_pack.xlsx"
            source_rows = read_csv_rows(out_dir / "source_to_model.csv")
            self.assertEqual("10", read_cell(control_pack, "Inputs", "B2"))
            self.assertEqual("1", read_cell(control_pack, "Inputs", "A1"))
            self.assertEqual("reference_only", source_rows[0]["mapping_treatment"])
            self.assertEqual("missing_model_architecture", source_rows[1]["mapping_treatment"])
            self.assertEqual("reference_only", source_rows[0]["review_status"])
            self.assertEqual("blocked_missing_model_architecture", source_rows[1]["review_status"])

    def test_promoted_cover_preserves_sheet_scoped_defined_names(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            workbook = tmp_path / "model.xlsx"
            input_csv = tmp_path / "updates.csv"
            out_dir = tmp_path / "out"
            write_minimal_workbook(workbook, formula_cell=True, local_defined_name=True)
            write_rows(
                input_csv,
                [
                    {
                        "model_line": "Calculated revenue growth",
                        "source_metric": "FY2026 revenue growth",
                        "proposed_model_value": "12.5",
                        "workbook_sheet": "Inputs",
                        "workbook_cell": "B2",
                        "source_id": "src-release",
                        "as_of_date": "2026-05-12",
                    }
                ],
            )

            result = run_command(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(input_csv),
                    "--workbook",
                    str(workbook),
                    "--out",
                    str(out_dir),
                    "--run-date",
                    "2026-05-18",
                ],
                cwd=ROOT,
            )

            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            control_pack = out_dir / "model_update_control_pack.xlsx"
            self.assertEqual("0", defined_name_local_sheet_id(workbook, "_xlnm.Print_Area"))
            self.assertEqual(["Update_Cover", "Inputs"], workbook_sheet_names(control_pack)[:2])
            self.assertEqual("1", defined_name_local_sheet_id(control_pack, "_xlnm.Print_Area"))

    def test_rebuild_required_target_uses_rebuild_citation_label(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            workbook = tmp_path / "model.xlsx"
            input_csv = tmp_path / "updates.csv"
            out_dir = tmp_path / "out"
            write_minimal_workbook(workbook, formula_cell=True)
            write_rows(
                input_csv,
                [
                    {
                        "model_line": "Annual free cash flow forecast anchor",
                        "source_metric": "Q1 FY2027 reported free cash flow",
                        "source_value": "48.554",
                        "mapping_treatment": "rebuild_required",
                        "workbook_sheet": "Inputs",
                        "workbook_cell": "B2",
                        "source_id": "src-release",
                        "as_of_date": "2026-05-12",
                    }
                ],
            )

            result = run_command(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(input_csv),
                    "--workbook",
                    str(workbook),
                    "--out",
                    str(out_dir),
                    "--run-date",
                    "2026-05-18",
                ],
                cwd=ROOT,
            )

            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            citations = json.loads(
                (out_dir / "model_update_citations.json").read_text(encoding="utf-8")
            )
            citation = citations["model_citations"][0]
            self.assertEqual("model_rebuild_requirement", citation["type"])
            self.assertEqual(
                "Annual free cash flow forecast anchor rebuild requirement", citation["title"]
            )
            self.assertEqual("rebuild_required", citation["mapping_treatment"])

    def test_missing_model_architecture_is_blocked_without_fake_delta(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            workbook = tmp_path / "model.xlsx"
            input_csv = tmp_path / "updates.csv"
            out_dir = tmp_path / "out"
            write_minimal_workbook(workbook)
            write_rows(
                input_csv,
                [
                    {
                        "model_line": "Revenue forecast",
                        "source_metric": "Q2 FY2027 revenue guidance",
                        "source_value": "91.0",
                        "mapping_treatment": "missing_model_architecture",
                        "source_id": "src-guide",
                        "as_of_date": "2026-05-12",
                    }
                ],
            )

            result = run_command(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(input_csv),
                    "--workbook",
                    str(workbook),
                    "--out",
                    str(out_dir),
                    "--run-date",
                    "2026-05-18",
                ],
                cwd=ROOT,
            )

            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            source_rows = read_csv_rows(out_dir / "source_to_model.csv")
            change_rows = read_csv_rows(out_dir / "change_log.csv")
            run_log = json.loads((out_dir / "run_log.json").read_text(encoding="utf-8"))

            self.assertEqual("rebuild_required", source_rows[0]["update_action"])
            self.assertEqual("blocked_missing_model_architecture", source_rows[0]["review_status"])
            self.assertEqual("missing_model_architecture", source_rows[0]["blocked_reason"])
            self.assertEqual("", source_rows[0]["proposed_model_value"])
            self.assertEqual([], change_rows)
            self.assertEqual(1, run_log["workbook_update_summary"]["missing_architecture_count"])
            self.assertIn(
                "Rebuild_Requirements",
                workbook_sheet_names(out_dir / "model_update_control_pack.xlsx"),
            )

    def test_missing_sheet_routes_to_workbook_control_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            workbook = tmp_path / "model.xlsx"
            input_csv = tmp_path / "updates.csv"
            out_dir = tmp_path / "out"
            write_minimal_workbook(workbook)
            write_rows(
                input_csv,
                [
                    {
                        "model_line": "Revenue growth",
                        "source_metric": "FY2026 revenue growth",
                        "proposed_model_value": "12.5",
                        "workbook_sheet": "Missing Sheet",
                        "workbook_cell": "B2",
                        "source_id": "src-release",
                        "as_of_date": "2026-05-12",
                    }
                ],
            )

            result = run_command(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(input_csv),
                    "--workbook",
                    str(workbook),
                    "--out",
                    str(out_dir),
                    "--run-date",
                    "2026-05-18",
                ],
                cwd=ROOT,
            )

            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            self.assertTrue((out_dir / "model_update_control_pack.xlsx").exists())
            source_rows = read_csv_rows(out_dir / "source_to_model.csv")
            change_rows = read_csv_rows(out_dir / "change_log.csv")
            self.assertEqual("workbook_sheet_not_found", source_rows[0]["blocked_reason"])
            self.assertEqual("blocked", change_rows[0]["status"])

    def test_non_gaap_eps_does_not_trigger_gaap_recurring_driver_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            input_csv = tmp_path / "updates.csv"
            out_dir = tmp_path / "out"
            write_rows(
                input_csv,
                [
                    {
                        "model_line": "Diluted EPS",
                        "source_metric": "Q1 non-GAAP diluted EPS",
                        "source_value": "1.87",
                        "proposed_model_value": "1.87",
                        "earnings_basis": "non-GAAP",
                        "source_id": "src-release",
                        "as_of_date": "2026-05-12",
                    },
                    {
                        "model_line": "Diluted EPS",
                        "source_metric": "Q1 GAAP diluted EPS",
                        "source_value": "2.39",
                        "proposed_model_value": "2.39",
                        "earnings_basis": "GAAP",
                        "source_id": "src-release",
                        "as_of_date": "2026-05-12",
                    },
                ],
            )

            result = run_command(
                [
                    sys.executable,
                    str(CSV_SCRIPT),
                    str(input_csv),
                    "--out",
                    str(out_dir),
                    "--run-date",
                    "2026-05-18",
                ],
                cwd=ROOT,
            )
            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            source_rows = read_csv_rows(out_dir / "source_to_model.csv")
            self.assertNotIn(
                "gaap_eps_requires_recurring_driver_check", source_rows[0]["issue_flags"]
            )
            self.assertIn("gaap_eps_requires_recurring_driver_check", source_rows[1]["issue_flags"])

    def test_csv_materializer_treats_workbook_request_as_handoff_not_hard_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            input_csv = tmp_path / "updates.csv"
            out_dir = tmp_path / "out"
            write_rows(
                input_csv,
                [
                    {
                        "model_line": "Revenue growth",
                        "source_metric": "FY2026 revenue growth",
                        "proposed_model_value": "12.5",
                        "source_id": "src-release",
                        "workbook_write_requested": "true",
                    }
                ],
            )

            result = run_command(
                [
                    sys.executable,
                    str(CSV_SCRIPT),
                    str(input_csv),
                    "--out",
                    str(out_dir),
                    "--run-date",
                    "2026-05-18",
                ],
                cwd=ROOT,
            )
            run_log = json.loads((out_dir / "run_log.json").read_text(encoding="utf-8"))

            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            self.assertEqual("update_map_export", run_log["workbook_mode"])
            self.assertEqual([], run_log["hard_failures"])
            self.assertTrue(
                any("materialize_workbook_update.py" in warning for warning in run_log["warnings"])
            )

    def test_workbook_update_surfaces_formula_cache_and_recalc_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            workbook = tmp_path / "model.xlsx"
            input_csv = tmp_path / "updates.csv"
            out_dir = tmp_path / "out"
            write_minimal_workbook(workbook, formula_cell=True)
            add_manual_calc_metadata(workbook)
            write_rows(
                input_csv,
                [
                    {
                        "model_line": "Revenue input",
                        "source_metric": "FY2026 revenue",
                        "current_model_value": "1",
                        "proposed_model_value": "5",
                        "workbook_sheet": "Inputs",
                        "workbook_cell": "A1",
                        "source_id": "src-release",
                        "source_name": "Company release",
                        "as_of_date": "2026-05-12",
                    }
                ],
            )

            result = run_command(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(input_csv),
                    "--workbook",
                    str(workbook),
                    "--out",
                    str(out_dir),
                    "--run-date",
                    "2026-05-18",
                ],
                cwd=ROOT,
            )

            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            run_log = json.loads((out_dir / "run_log.json").read_text(encoding="utf-8"))
            preflight = run_log["workbook_preflight"]
            recalc = run_log["recalculation_warning"]

            self.assertEqual(1, preflight["formula_cell_count"])
            self.assertEqual(1, preflight["cached_formula_value_count"])
            self.assertTrue(preflight["calc_chain_present"])
            self.assertEqual("manual", preflight["calc_mode"])
            self.assertTrue(preflight["recalc_required"])
            self.assertTrue(recalc["recalc_required"])
            self.assertFalse(recalc["runtime_recalculated_formulas"])
            self.assertTrue(
                any(
                    "does not recalculate downstream formula caches" in warning
                    for warning in run_log["warnings"]
                )
            )


if __name__ == "__main__":
    unittest.main()
