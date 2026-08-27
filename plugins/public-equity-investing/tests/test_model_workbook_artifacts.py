"""Generated workbook regressions for Public Equity Investing model builders."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

sys.path.insert(0, str(ROOT))

from shared.dashboard.qa import load_payload, validate_payload  # noqa: E402
from shared.dashboard.renderer import render_dashboard  # noqa: E402
from shared.model_citations import validate_model_citations  # noqa: E402
from shared.workbook_inspection import inspect_formula_workbook  # noqa: E402

DCF_SKILL = ROOT / "skills" / "dcf-model-builder"
THREE_STATEMENT_SKILL = ROOT / "skills" / "three-statement-model-builder"

DCF_REQUIRED_FORMULA_SHEETS = [
    "Cover",
    "Executive Summary",
    "Control Panel",
    "Historical Financials",
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
    "Source Notes",
]

THREE_STATEMENT_REQUIRED_FORMULA_SHEETS = [
    "Cover",
    "Executive Summary",
    "Control Panel",
    "Historical Financials",
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
    "Source Notes",
]


def run_command(args: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=str(cwd), text=True, capture_output=True, check=False)


def workbook_sheet_paths(path: Path) -> dict[str, str]:
    with zipfile.ZipFile(path) as zf:
        workbook = ET.fromstring(zf.read("xl/workbook.xml"))
        rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
        relmap = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels}
        sheets = workbook.find(f"{{{NS_MAIN}}}sheets")
        if sheets is None:
            return {}
        paths: dict[str, str] = {}
        for sheet in sheets:
            rid = sheet.attrib[f"{{{NS_REL}}}id"]
            target = relmap[rid].lstrip("/")
            paths[sheet.attrib["name"]] = target if target.startswith("xl/") else f"xl/{target}"
        return paths


def workbook_sheet_names(path: Path) -> list[str]:
    return list(workbook_sheet_paths(path).keys())


def workbook_formula_count(path: Path) -> int:
    count = 0
    with zipfile.ZipFile(path) as zf:
        for sheet_path in workbook_sheet_paths(path).values():
            root = ET.fromstring(zf.read(sheet_path))
            count += len(root.findall(f".//{{{NS_MAIN}}}f"))
    return count


def workbook_external_links(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as zf:
        return [name for name in zf.namelist() if name.startswith("xl/externalLinks/")]


def workbook_cell(path: Path, sheet_name: str, ref: str) -> tuple[str | None, str | None]:
    with zipfile.ZipFile(path) as zf:
        root = ET.fromstring(zf.read(workbook_sheet_paths(path)[sheet_name]))
        for cell in root.findall(f".//{{{NS_MAIN}}}c"):
            if cell.attrib.get("r") != ref:
                continue
            formula = cell.find(f"{{{NS_MAIN}}}f")
            value = cell.find(f"{{{NS_MAIN}}}v")
            inline = cell.find(f"{{{NS_MAIN}}}is/{{{NS_MAIN}}}t")
            return (
                inline.text if inline is not None else value.text if value is not None else None,
                formula.text if formula is not None else None,
            )
    return None, None


def strip_formula_nodes(source: Path, target: Path) -> None:
    with zipfile.ZipFile(source) as zin, zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename.startswith("xl/worksheets/") and info.filename.endswith(".xml"):
                root = ET.fromstring(data)
                for cell in root.findall(f".//{{{NS_MAIN}}}c"):
                    for formula in list(cell.findall(f"{{{NS_MAIN}}}f")):
                        cell.remove(formula)
                data = ET.tostring(root, encoding="utf-8", xml_declaration=True)
            zout.writestr(info, data)


class ModelWorkbookArtifactTests(unittest.TestCase):
    def test_model_builder_docs_default_to_formula_workbook_mode(self) -> None:
        checks = [
            (
                DCF_SKILL,
                "Default model-build artifact level is `banker_formula_workbook`",
                "formula-first public-equity DCF workbooks",
            ),
            (
                THREE_STATEMENT_SKILL,
                "Default model-build artifact level is `banker_formula_workbook`",
                "formula-first public-equity 3-statement operating model workbooks",
            ),
        ]
        for skill_root, contract_phrase, agent_phrase in checks:
            skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
            output_spec = (skill_root / "references" / "output-spec.md").read_text(encoding="utf-8")
            formula_contract = (
                skill_root / "references" / "banker-formula-workbook-contract.md"
            ).read_text(encoding="utf-8")
            agent = (skill_root / "agents" / "openai.yaml").read_text(encoding="utf-8")

            self.assertIn(contract_phrase, skill)
            self.assertIn("Default path: ", skill)
            self.assertIn("Use `python3 scripts/run_pipeline.py", skill)
            self.assertIn("only for controlled computed values", skill)
            self.assertIn(
                "The default model-build path is the banker formula workbook path", output_spec
            )
            self.assertIn("`banker_formula_workbook`: default live formula workbook", output_spec)
            self.assertIn(
                "Formula mode is the default user-facing model-build path", formula_contract
            )
            self.assertIn(agent_phrase, agent)

    def test_deterministic_exports_remain_values_workbooks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir) / "dcf"
            result = run_command(
                [
                    sys.executable,
                    str(DCF_SKILL / "scripts" / "run_pipeline.py"),
                    str(DCF_SKILL / "assets" / "plan_template.json"),
                    "--output-dir",
                    str(output_dir),
                ],
                cwd=DCF_SKILL,
            )

            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            run_log = json.loads((output_dir / "run_log.json").read_text(encoding="utf-8"))
            manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual("deterministic_export", run_log["workbook_mode"])
            self.assertEqual("Cover", workbook_sheet_names(output_dir / "model.xlsx")[0])
            self.assertLess(workbook_formula_count(output_dir / "model.xlsx"), 5)
            self.assertTrue((output_dir / "support_note.md").exists())
            self.assertFalse((output_dir / "report.md").exists())
            self.assertEqual(
                (output_dir / "model.xlsx").resolve(),
                Path(manifest["primary_human_deliverable"]).resolve(),
            )
            self.assertTrue(
                any(
                    row["key"] == "support_note"
                    and row["artifact_role"] == "narrative_support"
                    and row["hidden_unless_requested"]
                    for row in manifest["outputs"]
                )
            )

    def test_three_statement_deterministic_export_remains_values_workbook(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            work_dir = Path(tmp_dir)
            result = run_command(
                [
                    sys.executable,
                    str(THREE_STATEMENT_SKILL / "scripts" / "run_pipeline.py"),
                    str(THREE_STATEMENT_SKILL / "assets" / "plan_template.json"),
                ],
                cwd=work_dir,
            )

            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            output_dir = work_dir / "output"
            run_log = json.loads((output_dir / "run_log.json").read_text(encoding="utf-8"))
            manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual("deterministic_export", run_log["workbook_mode"])
            self.assertEqual("Cover", workbook_sheet_names(output_dir / "model.xlsx")[0])
            self.assertLess(workbook_formula_count(output_dir / "model.xlsx"), 5)
            self.assertTrue((output_dir / "support_note.md").exists())
            self.assertFalse((output_dir / "report.md").exists())
            self.assertEqual(
                (output_dir / "model.xlsx").resolve(),
                Path(manifest["primary_human_deliverable"]).resolve(),
            )
            self.assertTrue(
                any(
                    row["key"] == "support_note"
                    and row["artifact_role"] == "narrative_support"
                    and row["hidden_unless_requested"]
                    for row in manifest["outputs"]
                )
            )

    def test_dcf_formula_workbook_has_required_artifacts_and_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir) / "dcf_formula"
            result = run_command(
                [
                    sys.executable,
                    str(DCF_SKILL / "scripts" / "build_banker_formula_workbook.py"),
                    str(DCF_SKILL / "assets" / "plan_template.json"),
                    "--output-dir",
                    str(output_dir),
                ],
                cwd=DCF_SKILL,
            )

            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            workbook = output_dir / "banker_formula_workbook.xlsx"
            run_log = json.loads(
                (output_dir / "banker_formula_workbook_run_log.json").read_text(encoding="utf-8")
            )
            manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
            model_citations = json.loads(
                (output_dir / "model_citations.json").read_text(encoding="utf-8")
            )

            self.assertTrue(workbook.exists())
            self.assertEqual("completed", run_log["status"])
            self.assertEqual("banker_formula_workbook", run_log["workbook_mode"])
            self.assertEqual("completed", manifest["status"])
            self.assertEqual("banker_formula_workbook", manifest["artifact_mode"])
            self.assertEqual("complete", manifest["blocked_or_partial_status"]["status"])
            self.assertEqual(str(workbook), manifest["primary_human_deliverable"])
            self.assertEqual("Cover", workbook_sheet_names(workbook)[0])
            self.assertTrue(
                set(DCF_REQUIRED_FORMULA_SHEETS).issubset(workbook_sheet_names(workbook))
            )
            inspection = inspect_formula_workbook(
                workbook, required_sheets=DCF_REQUIRED_FORMULA_SHEETS, workbook_type="dcf"
            )
            self.assertGreaterEqual(workbook_formula_count(workbook), 800)
            self.assertTrue(inspection["cover_first"])
            self.assertTrue(inspection["required_formula_sheets_populated"])
            self.assertTrue(
                inspection["has_named_ranges"]
                or run_log["workbook_inspection"]["anchor_map_present"]
            )
            self.assertEqual([], workbook_external_links(workbook))
            self.assertEqual([], run_log["hard_failures"])
            self.assertIn("model_citations", run_log["output_paths"])
            self.assertEqual([], validate_model_citations(model_citations, strict=True))
            self.assertGreaterEqual(len(model_citations["model_citations"]), 5)
            self.assertIn("support_artifacts", manifest)
            self.assertTrue(
                any(
                    item["path"].endswith("model_citations.json")
                    and item["role"] == "support_artifact"
                    for item in manifest["support_artifacts"]
                )
            )
            self.assertTrue(
                any(
                    item["sheet"] == "DCF Valuation" and item["cell"] == "B18"
                    for item in model_citations["model_citations"]
                )
            )

    def test_dcf_formula_workbook_clears_template_history_and_maps_market_data(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            plan = json.loads(
                (DCF_SKILL / "assets" / "plan_template.json").read_text(encoding="utf-8")
            )
            plan["meta"].update({"company": "Airbnb, Inc.", "ticker": "ABNB"})
            plan["timeline"]["start_year"] = 2026
            plan["historicals"].update(
                {
                    "latest_year": 2025,
                    "revenue": 12241.0,
                    "gross_profit_margin": 0.8296,
                    "ebitda": 2635.0,
                    "ebit": 2544.0,
                    "cash_taxes": 232.0,
                    "da": 91.0,
                    "capex": 33.0,
                    "change_nwc": 0.0,
                    "net_working_capital": 0.0,
                    "unlevered_fcf": 4613.0,
                }
            )
            plan["market"] = {
                "current_share_price": 134.5,
                "source_id": "src_market_abnb",
            }
            plan["ev_to_equity_bridge"]["current_share_price"] = 134.5
            plan["source_basis"].append(
                {
                    "id": "src_market_abnb",
                    "topic": "market_data",
                    "label": "web_research",
                    "source_name": "Nasdaq ABNB quote endpoint",
                    "source_type": "exchange_quote",
                    "as_of_date": "2026-05-11",
                    "confidence": "high",
                    "notes": "Closing price used in DCF evaluation.",
                }
            )
            plan_path = tmp / "abnb_plan.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            output_dir = tmp / "abnb_formula"

            result = run_command(
                [
                    sys.executable,
                    str(DCF_SKILL / "scripts" / "build_banker_formula_workbook.py"),
                    str(plan_path),
                    "--output-dir",
                    str(output_dir),
                ],
                cwd=DCF_SKILL,
            )

            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            workbook = output_dir / "banker_formula_workbook.xlsx"
            run_log = json.loads(
                (output_dir / "banker_formula_workbook_run_log.json").read_text(encoding="utf-8")
            )
            self.assertNotEqual("not-decision-ready", run_log["model_status"])
            self.assertNotIn("timeline_latest_historical_year_mismatch", run_log["hard_failures"])
            self.assertEqual(("N/A", None), workbook_cell(workbook, "Revenue Build", "B5"))
            self.assertEqual(("2025A", None), workbook_cell(workbook, "Revenue Build", "D5"))
            self.assertEqual(("2026E", None), workbook_cell(workbook, "Revenue Build", "E5"))
            self.assertEqual((None, None), workbook_cell(workbook, "Revenue Build", "B10"))
            self.assertEqual(("12241.0", None), workbook_cell(workbook, "Revenue Build", "D10"))
            self.assertEqual(("n.m.", None), workbook_cell(workbook, "Capex D&A", "B13"))
            self.assertEqual(("n.m.", None), workbook_cell(workbook, "Capex D&A", "E13"))
            self.assertEqual(
                ("not provided", None), workbook_cell(workbook, "Historical Financials", "K21")
            )
            self.assertEqual(
                ("Nasdaq ABNB quote endpoint", None), workbook_cell(workbook, "Source Notes", "B11")
            )
            self.assertEqual(("web_research", None), workbook_cell(workbook, "Source Notes", "C11"))
            self.assertEqual(
                ("Ending PP&E non-negative when roll-forward modeled", None),
                workbook_cell(workbook, "Checks", "A21"),
            )
            self.assertIn("historical_ppe_or_reinvestment_support", run_log["missing_inputs"])
            self.assertIn(
                "earlier historical columns were intentionally blanked",
                " ".join(run_log["warnings"]),
            )

    def test_dcf_formula_workbook_keeps_market_price_source_open_when_price_is_missing(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            plan = json.loads(
                (DCF_SKILL / "assets" / "plan_template.json").read_text(encoding="utf-8")
            )
            plan["source_basis"].append(
                {
                    "id": "src_market_without_price",
                    "topic": "market_data",
                    "label": "web_research",
                    "source_name": "Market-data endpoint",
                    "source_type": "exchange_quote",
                    "as_of_date": "2026-05-11",
                    "confidence": "high",
                    "notes": "Quote source was available.",
                }
            )
            plan_path = tmp / "missing_price_plan.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            output_dir = tmp / "missing_price_formula"

            result = run_command(
                [
                    sys.executable,
                    str(DCF_SKILL / "scripts" / "build_banker_formula_workbook.py"),
                    str(plan_path),
                    "--output-dir",
                    str(output_dir),
                ],
                cwd=DCF_SKILL,
            )

            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            workbook = output_dir / "banker_formula_workbook.xlsx"
            run_log = json.loads(
                (output_dir / "banker_formula_workbook_run_log.json").read_text(encoding="utf-8")
            )
            self.assertIn("current_share_price", run_log["missing_inputs"])
            self.assertEqual(("Open", None), workbook_cell(workbook, "Source Notes", "H11"))
            self.assertIn(
                "Current share price was not supplied",
                workbook_cell(workbook, "Source Notes", "F11")[0] or "",
            )

    def test_dcf_formula_workbook_rejects_negative_supported_ppe_rollforward(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            plan = json.loads(
                (DCF_SKILL / "assets" / "plan_template.json").read_text(encoding="utf-8")
            )
            plan["historicals"]["ppe"] = 10.0
            for scenario in plan["scenarios"].values():
                scenario["capex_percent_revenue"] = 0.0
                scenario["da_percent_revenue"] = 0.10
            plan_path = tmp / "bad_reinvestment_plan.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            output_dir = tmp / "bad_reinvestment_formula"

            result = run_command(
                [
                    sys.executable,
                    str(DCF_SKILL / "scripts" / "build_banker_formula_workbook.py"),
                    str(plan_path),
                    "--output-dir",
                    str(output_dir),
                ],
                cwd=DCF_SKILL,
            )

            self.assertEqual(2, result.returncode, result.stderr + result.stdout)
            run_log = json.loads(
                (output_dir / "banker_formula_workbook_run_log.json").read_text(encoding="utf-8")
            )
            self.assertEqual("not-decision-ready", run_log["model_status"])
            self.assertIn("negative_forecast_ppe_rollforward", run_log["hard_failures"])

    def test_dcf_formula_workbook_rejects_negative_opening_ppe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            plan = json.loads(
                (DCF_SKILL / "assets" / "plan_template.json").read_text(encoding="utf-8")
            )
            plan["historicals"]["ppe"] = -10.0
            for scenario in plan["scenarios"].values():
                scenario["capex_percent_revenue"] = 0.20
                scenario["da_percent_revenue"] = 0.0
            plan_path = tmp / "negative_opening_ppe_plan.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            output_dir = tmp / "negative_opening_ppe_formula"

            result = run_command(
                [
                    sys.executable,
                    str(DCF_SKILL / "scripts" / "build_banker_formula_workbook.py"),
                    str(plan_path),
                    "--output-dir",
                    str(output_dir),
                ],
                cwd=DCF_SKILL,
            )

            self.assertEqual(2, result.returncode, result.stderr + result.stdout)
            run_log = json.loads(
                (output_dir / "banker_formula_workbook_run_log.json").read_text(encoding="utf-8")
            )
            self.assertEqual("not-decision-ready", run_log["model_status"])
            self.assertIn("negative_historical_ppe", run_log["hard_failures"])

    def test_three_statement_formula_workbook_has_required_artifacts_and_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir) / "three_statement_formula"
            result = run_command(
                [
                    sys.executable,
                    str(THREE_STATEMENT_SKILL / "scripts" / "build_banker_formula_workbook.py"),
                    str(THREE_STATEMENT_SKILL / "assets" / "plan_template.json"),
                    "--output-dir",
                    str(output_dir),
                ],
                cwd=THREE_STATEMENT_SKILL,
            )

            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            workbook = output_dir / "banker_formula_workbook.xlsx"
            run_log = json.loads(
                (output_dir / "banker_formula_workbook_run_log.json").read_text(encoding="utf-8")
            )
            manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
            model_citations = json.loads(
                (output_dir / "model_citations.json").read_text(encoding="utf-8")
            )

            self.assertTrue(workbook.exists())
            self.assertEqual("completed", run_log["status"])
            self.assertEqual("banker_formula_workbook", run_log["workbook_mode"])
            self.assertEqual("completed", manifest["status"])
            self.assertEqual("banker_formula_workbook", manifest["artifact_mode"])
            self.assertEqual("complete", manifest["blocked_or_partial_status"]["status"])
            self.assertEqual(str(workbook), manifest["primary_human_deliverable"])
            self.assertEqual("Cover", workbook_sheet_names(workbook)[0])
            self.assertTrue(
                set(THREE_STATEMENT_REQUIRED_FORMULA_SHEETS).issubset(
                    workbook_sheet_names(workbook)
                )
            )
            inspection = inspect_formula_workbook(
                workbook,
                required_sheets=THREE_STATEMENT_REQUIRED_FORMULA_SHEETS,
                workbook_type="three_statement",
            )
            self.assertGreaterEqual(workbook_formula_count(workbook), 1100)
            self.assertTrue(inspection["cover_first"])
            self.assertTrue(inspection["required_formula_sheets_populated"])
            self.assertTrue(
                inspection["has_named_ranges"]
                or run_log["workbook_inspection"]["anchor_map_present"]
            )
            self.assertEqual([], workbook_external_links(workbook))
            self.assertEqual([], run_log["hard_failures"])
            self.assertIn("model_citations", run_log["output_paths"])
            self.assertEqual([], validate_model_citations(model_citations, strict=True))
            self.assertGreaterEqual(len(model_citations["model_citations"]), 5)
            self.assertIn("support_artifacts", manifest)
            self.assertTrue(
                any(
                    item["path"].endswith("model_citations.json")
                    and item["role"] == "support_artifact"
                    for item in manifest["support_artifacts"]
                )
            )
            self.assertTrue(
                any(
                    item["sheet"] == "Income Statement" and item["cell"] == "I6"
                    for item in model_citations["model_citations"]
                )
            )

    def test_invalid_formula_plan_does_not_claim_formula_workbook(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            bad_plan = Path(tmp_dir) / "bad_plan.json"
            bad_plan.write_text('{"meta": {}}', encoding="utf-8")
            output_dir = Path(tmp_dir) / "bad_formula"

            result = run_command(
                [
                    sys.executable,
                    str(DCF_SKILL / "scripts" / "build_banker_formula_workbook.py"),
                    str(bad_plan),
                    "--output-dir",
                    str(output_dir),
                ],
                cwd=DCF_SKILL,
            )

            self.assertNotEqual(0, result.returncode)
            self.assertFalse((output_dir / "banker_formula_workbook.xlsx").exists())
            self.assertFalse((output_dir / "banker_formula_workbook_run_log.json").exists())

    def test_dcf_formula_workbook_hard_failures_return_nonzero_and_diagnostic_artifacts(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            bad_template = tmp / "dcf_template_without_formulas.xlsx"
            strip_formula_nodes(
                DCF_SKILL / "assets" / "templates" / "banker_formula_workbook_template.xlsx",
                bad_template,
            )
            output_dir = tmp / "dcf_formula_bad"

            result = run_command(
                [
                    sys.executable,
                    str(DCF_SKILL / "scripts" / "build_banker_formula_workbook.py"),
                    str(DCF_SKILL / "assets" / "plan_template.json"),
                    "--output-dir",
                    str(output_dir),
                    "--template",
                    str(bad_template),
                ],
                cwd=DCF_SKILL,
            )

            self.assertEqual(2, result.returncode, result.stderr + result.stdout)
            self.assertTrue((output_dir / "banker_formula_workbook.xlsx").exists())
            run_log = json.loads(
                (output_dir / "banker_formula_workbook_run_log.json").read_text(encoding="utf-8")
            )
            manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))

            self.assertEqual("failed", run_log["status"])
            self.assertEqual("not-decision-ready", run_log["model_status"])
            workbook = output_dir / "banker_formula_workbook.xlsx"
            self.assertEqual(("not-decision-ready", None), workbook_cell(workbook, "Cover", "B6"))
            self.assertEqual(("not-decision-ready", None), workbook_cell(workbook, "Cover", "B35"))
            self.assertEqual(
                ("not-decision-ready", None), workbook_cell(workbook, "Control Panel", "B8")
            )
            self.assertIn(
                "Not decision-ready",
                workbook_cell(workbook, "Executive Summary", "B3")[0] or "",
            )
            self.assertIn(
                "banker_formula_workbook_formula_count_below_threshold", run_log["hard_failures"]
            )
            self.assertIn(
                "banker_formula_workbook_missing_required_formula_sheets", run_log["hard_failures"]
            )
            self.assertEqual("failed", manifest["status"])
            self.assertEqual("not-decision-ready", manifest["blocked_or_partial_status"]["status"])
            self.assertEqual(
                "workbook_diagnostic_status", manifest["final_response_guidance"]["lead_with"]
            )

    def test_three_statement_formula_workbook_hard_failures_return_nonzero_and_diagnostic_artifacts(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            bad_template = tmp / "three_statement_template_without_formulas.xlsx"
            strip_formula_nodes(
                THREE_STATEMENT_SKILL
                / "assets"
                / "templates"
                / "banker_formula_workbook_template.xlsx",
                bad_template,
            )
            output_dir = tmp / "three_statement_formula_bad"

            result = run_command(
                [
                    sys.executable,
                    str(THREE_STATEMENT_SKILL / "scripts" / "build_banker_formula_workbook.py"),
                    str(THREE_STATEMENT_SKILL / "assets" / "plan_template.json"),
                    "--output-dir",
                    str(output_dir),
                    "--template",
                    str(bad_template),
                ],
                cwd=THREE_STATEMENT_SKILL,
            )

            self.assertEqual(2, result.returncode, result.stderr + result.stdout)
            self.assertTrue((output_dir / "banker_formula_workbook.xlsx").exists())
            run_log = json.loads(
                (output_dir / "banker_formula_workbook_run_log.json").read_text(encoding="utf-8")
            )
            manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))

            self.assertEqual("failed", run_log["status"])
            self.assertEqual("not-decision-ready", run_log["model_status"])
            self.assertIn(
                "banker_formula_workbook_formula_count_below_threshold", run_log["hard_failures"]
            )
            self.assertIn(
                "banker_formula_workbook_missing_required_formula_sheets", run_log["hard_failures"]
            )
            self.assertEqual("failed", manifest["status"])
            self.assertEqual("not-decision-ready", manifest["blocked_or_partial_status"]["status"])
            self.assertEqual(
                "workbook_diagnostic_status", manifest["final_response_guidance"]["lead_with"]
            )

    def test_dashboard_renders_model_citations_path_as_source_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            citations = {
                "model_citations": [
                    {
                        "id": "model-output:dcf-value-per-share",
                        "title": "DCF Value Per Share",
                        "short_label": "Model: DCF Valuation!B18",
                        "type": "model_cell",
                        "workbook_path": "/tmp/banker_formula_workbook.xlsx",
                        "sheet": "DCF Valuation",
                        "cell": "B18",
                        "range": "B18",
                        "value": "$48.25",
                        "formula": "=B16/B17",
                        "line_item": "value_per_share",
                        "source_id": "src_shares_001",
                        "evidence_label": "reported",
                    }
                ]
            }
            (tmp_path / "model_citations.json").write_text(json.dumps(citations), encoding="utf-8")
            payload = {
                "kind": "public_equity_investing_dashboard.v1",
                "mode": "dcf_model_dashboard",
                "layout": "single_page",
                "title": "DCF dashboard",
                "issuer": {"ticker": "NSIS"},
                "metadata": {
                    "payload_stage": "production",
                    "freeze_time": "2026-05-18 09:00 ET",
                    "source_posture": "Synthetic formula-workbook fixture.",
                    "readiness_label": "PM-ready fixture",
                    "readiness_posture": "pm_ready",
                    "citation_policy": "strict",
                    "decision_context": "Whether workbook-backed valuation output is source-visible.",
                },
                "hero": {
                    "headline": "DCF workbook dashboard",
                    "dek": {
                        "value": "DCF value is $48.25",
                        "citations": ["model-output:dcf-value-per-share"],
                    },
                    "callout": {
                        "value": "Workbook citation should render",
                        "citations": ["model-output:dcf-value-per-share"],
                    },
                },
                "model_citations_path": "model_citations.json",
                "snapshot": [
                    {
                        "label": "DCF value/share",
                        "value": {
                            "value": "$48.25",
                            "citations": ["model-output:dcf-value-per-share"],
                        },
                        "detail": "Base case model output",
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
                                    "stance": "Watch",
                                    "summary": {
                                        "value": "DCF value is $48.25",
                                        "citations": ["model-output:dcf-value-per-share"],
                                    },
                                },
                            }
                        ],
                    }
                ],
            }
            payload_path = tmp_path / "payload.json"
            payload_path.write_text(json.dumps(payload), encoding="utf-8")

            loaded = load_payload(payload_path)
            report = validate_payload(loaded)
            html = render_dashboard(loaded)

            self.assertEqual("passed", report["status"], report)
            self.assertIn("DCF Valuation!B18", html)
            self.assertIn("formula: =B16/B17", html)
            self.assertIn("source-model-output-dcf-value-per-share", html)
            self.assertIn('class="citation-link"', html)


if __name__ == "__main__":
    unittest.main()
