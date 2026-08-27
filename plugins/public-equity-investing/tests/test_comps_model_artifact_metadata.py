"""Comps model artifact metadata and hero-deliverable contracts."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "comps-valuation"
CREATE_SCRIPT = SKILL / "scripts" / "create_comps_template.py"
FALLBACK_SCRIPT = SKILL / "scripts" / "materialize_screening_comps.py"
AUDIT_SCRIPT = SKILL / "scripts" / "audit_comps_workbook.py"
NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def run_script(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args], cwd=str(ROOT), text=True, capture_output=True, check=False
    )


def workbook_sheet_names(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as zf:
        workbook = ET.fromstring(zf.read("xl/workbook.xml"))
        sheets = workbook.find(f"{{{NS_MAIN}}}sheets")
        if sheets is None:
            return []
        return [sheet.attrib["name"] for sheet in sheets]


class CompsModelArtifactMetadataTests(unittest.TestCase):
    @unittest.skipUnless(
        importlib.util.find_spec("xlsxwriter"), "xlsxwriter required for template workbook build"
    )
    def test_create_template_marks_xlsx_as_primary_human_deliverable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            output = tmp / "comps_template.xlsx"

            result = run_script(
                [
                    str(CREATE_SCRIPT),
                    "--output",
                    str(output),
                    "--target",
                    "ACME Software",
                    "--ticker",
                    "ACME",
                ]
            )

            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            run_log = json.loads((tmp / "run_log.json").read_text(encoding="utf-8"))
            manifest = json.loads((tmp / "manifest.json").read_text(encoding="utf-8"))

            self.assertEqual(str(output.resolve()), run_log["primary_human_deliverable"])
            self.assertEqual("workbook", run_log["artifact_mode"])
            self.assertFalse(run_log["support_artifacts_user_visible_default"])
            workbook_row = next(
                row for row in run_log["output_manifest"] if row["key"] == "workbook"
            )
            self.assertEqual("primary_human_deliverable", workbook_row["artifact_role"])
            self.assertFalse(workbook_row["hidden_unless_requested"])
            self.assertEqual(str(output.resolve()), manifest["primary_human_deliverable"])
            self.assertTrue(
                all(
                    row["hidden_unless_requested"]
                    for row in run_log["output_manifest"]
                    if row["key"] in {"run_log", "manifest"}
                )
            )

    def test_screening_fallback_creates_primary_xlsx_and_hides_support_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir) / "fallback"

            result = run_script(
                [
                    str(FALLBACK_SCRIPT),
                    "--output-dir",
                    str(output_dir),
                    "--target",
                    "ACME Software",
                    "--ticker",
                    "ACME",
                    "--sector",
                    "Software",
                    "--peer-list",
                    "MSFT:Microsoft,CRM:Salesforce",
                ]
            )

            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            workbook = output_dir / "screen_grade_comps_framework.xlsx"
            run_log = json.loads((output_dir / "run_log.json").read_text(encoding="utf-8"))
            manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))

            self.assertTrue(workbook.exists())
            self.assertEqual(
                ["Cover", "Peer Framework", "Missing Data Requests", "Source Requirements"],
                workbook_sheet_names(workbook),
            )
            self.assertEqual(str(workbook.resolve()), run_log["primary_human_deliverable"])
            self.assertEqual("workbook", run_log["artifact_mode"])
            self.assertEqual("screen-grade", run_log["model_status"])
            self.assertFalse(run_log["support_artifacts_user_visible_default"])
            self.assertEqual(str(workbook.resolve()), manifest["primary_human_deliverable"])
            workbook_row = next(
                row for row in run_log["output_manifest"] if row["key"] == "workbook"
            )
            self.assertEqual("primary_human_deliverable", workbook_row["artifact_role"])
            self.assertFalse(workbook_row["hidden_unless_requested"])
            for row in run_log["output_manifest"]:
                if row["key"] != "workbook":
                    self.assertTrue(row["hidden_unless_requested"], row)
                    self.assertNotEqual("primary_human_deliverable", row["artifact_role"], row)

    @unittest.skipUnless(
        importlib.util.find_spec("openpyxl"), "openpyxl required for comps workbook audit"
    )
    def test_audit_outputs_are_support_only_not_primary_deliverables(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir) / "fallback"
            audit_dir = Path(tmp_dir) / "audit"
            result = run_script([str(FALLBACK_SCRIPT), "--output-dir", str(output_dir)])
            self.assertEqual(0, result.returncode, result.stderr + result.stdout)

            result = run_script(
                [
                    str(AUDIT_SCRIPT),
                    str(output_dir / "screen_grade_comps_framework.xlsx"),
                    "--json-out",
                    str(audit_dir / "audit.json"),
                    "--markdown-out",
                    str(audit_dir / "audit.md"),
                ]
            )

            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            run_log = json.loads((audit_dir / "run_log.json").read_text(encoding="utf-8"))
            manifest = json.loads((audit_dir / "manifest.json").read_text(encoding="utf-8"))

            self.assertIsNone(run_log["primary_human_deliverable"])
            self.assertEqual("support_only", run_log["artifact_mode"])
            self.assertFalse(run_log["support_artifacts_user_visible_default"])
            self.assertIsNone(manifest["primary_human_deliverable"])
            self.assertEqual("support_only", manifest["artifact_mode"])
            self.assertTrue(run_log["output_manifest"])
            for row in run_log["output_manifest"]:
                self.assertTrue(row["hidden_unless_requested"], row)
                self.assertNotEqual("primary_human_deliverable", row["artifact_role"], row)


if __name__ == "__main__":
    unittest.main()
