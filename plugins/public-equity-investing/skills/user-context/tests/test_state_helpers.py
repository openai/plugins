from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = SKILL_ROOT / "scripts"
INIT_SCRIPT = SCRIPT_DIR / "init_user_context_state.py"
RESET_SCRIPT = SCRIPT_DIR / "reset_user_context_state.py"
PREFLIGHT_SCRIPT = SCRIPT_DIR / "user_context_preflight.py"
MARKETPLACE_ID = "oai-maintained-plugins"
PLUGIN_ID = "public-equity-investing"
ROUTER_SKILL = SKILL_ROOT.parent / PLUGIN_ID / "SKILL.md"
MEETING_PREP_SKILL = SKILL_ROOT.parent / "meeting-prep" / "SKILL.md"
COMPANY_TEARSHEET_SKILL = SKILL_ROOT.parent / "company-tearsheet" / "SKILL.md"
COMPANY_TEARSHEET_SOURCE_REFERENCE = (
    SKILL_ROOT.parent / "company-tearsheet" / "references/source-and-evidence.md"
)
ONBOARDING_REFERENCE = SKILL_ROOT / "references/onboarding.md"
AUTOMATION_CONFIG = SKILL_ROOT / "plugin-author-config/automation-config.md"
AUTOMATION_REFERENCE = SKILL_ROOT / "references/automation.md"
PLUGIN_MEMORY_REFERENCE = SKILL_ROOT / "references/plugin-memory.md"
SOURCE_CATEGORY_CONFIG = SKILL_ROOT / "plugin-author-config/source-category-config.json"
SOURCE_CATEGORY_RUNTIME = SKILL_ROOT / "references/source-category-runtime.md"
WORKFLOW_SOURCE_REFERENCE = SKILL_ROOT.parents[1] / "shared/workflow-source-resolution.md"
SPECIALIST_SKILLS = {
    "catalyst-calendar",
    "company-tearsheet",
    "comps-valuation",
    "dcf-model-builder",
    "deck-report-qc",
    "earnings-deep-dive",
    "earnings-preview",
    "economic-impact-report",
    "equity-model-update",
    "event-driven-analyzer",
    "financials-normalizer",
    "idea-generation",
    "initiating-coverage",
    "long-short-pitch",
    "meeting-prep",
    "memo-builder",
    "model-audit-tieout",
    "portfolio-risk-management",
    "scenario-sensitivity-generator",
    "thesis-tracker",
    "three-statement-model-builder",
}
SHARED_SOURCE_SKILLS = {
    "catalyst-calendar": {
        "company_filings_ir",
        "earnings_transcripts_presentations",
        "internal_research",
        "portfolio_models_trackers",
        "market_data_estimates",
    },
    "comps-valuation": {
        "company_filings_ir",
        "market_data_estimates",
        "portfolio_models_trackers",
    },
    "earnings-deep-dive": {
        "company_filings_ir",
        "earnings_transcripts_presentations",
        "internal_research",
        "portfolio_models_trackers",
        "market_data_estimates",
    },
    "earnings-preview": {
        "company_filings_ir",
        "earnings_transcripts_presentations",
        "internal_research",
        "portfolio_models_trackers",
        "market_data_estimates",
    },
    "economic-impact-report": {
        "internal_research",
        "portfolio_models_trackers",
        "market_data_estimates",
    },
    "equity-model-update": {
        "company_filings_ir",
        "earnings_transcripts_presentations",
        "internal_research",
        "portfolio_models_trackers",
        "market_data_estimates",
    },
    "event-driven-analyzer": {
        "company_filings_ir",
        "earnings_transcripts_presentations",
        "internal_research",
        "portfolio_models_trackers",
        "market_data_estimates",
    },
    "financials-normalizer": {
        "company_filings_ir",
        "earnings_transcripts_presentations",
        "internal_research",
        "portfolio_models_trackers",
        "market_data_estimates",
    },
    "idea-generation": {
        "company_filings_ir",
        "earnings_transcripts_presentations",
        "internal_research",
        "portfolio_models_trackers",
        "market_data_estimates",
    },
    "initiating-coverage": {
        "company_filings_ir",
        "earnings_transcripts_presentations",
        "internal_research",
        "portfolio_models_trackers",
        "market_data_estimates",
    },
    "long-short-pitch": {
        "company_filings_ir",
        "earnings_transcripts_presentations",
        "internal_research",
        "portfolio_models_trackers",
        "market_data_estimates",
    },
    "memo-builder": {
        "company_filings_ir",
        "earnings_transcripts_presentations",
        "internal_research",
        "portfolio_models_trackers",
        "market_data_estimates",
    },
    "portfolio-risk-management": {
        "internal_research",
        "portfolio_models_trackers",
        "market_data_estimates",
    },
    "thesis-tracker": {
        "company_filings_ir",
        "earnings_transcripts_presentations",
        "internal_research",
        "portfolio_models_trackers",
        "market_data_estimates",
    },
}


class PublicEquityInvestingStateHelpersTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)
        self.codex_home = self.tmp_path / "codex-home"
        self.state_dir = self.codex_home / "state/plugins" / MARKETPLACE_ID / PLUGIN_ID

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def run_script(self, script: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(script), *args],
            text=True,
            capture_output=True,
        )

    def test_init_uses_namespaced_state_dir_and_creates_only_expected_files(self) -> None:
        proc = self.run_script(INIT_SCRIPT, "--codex-home", str(self.codex_home))

        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        self.assertIn(f"Public Equity Investing state directory: {self.state_dir}", proc.stdout)
        self.assertEqual(
            {path.name for path in self.state_dir.iterdir()},
            {"user-context.md", "onboarding-state.json"},
        )
        self.assertFalse((self.state_dir / "category-state.json").exists())

    def test_init_preserves_existing_files_without_overwrite(self) -> None:
        self.state_dir.mkdir(parents=True)
        (self.state_dir / "user-context.md").write_text("keep me\n", encoding="utf-8")
        (self.state_dir / "onboarding-state.json").write_text(
            json.dumps({"status": "existing"}),
            encoding="utf-8",
        )

        proc = self.run_script(INIT_SCRIPT, "--codex-home", str(self.codex_home))

        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        self.assertIn("user-context.md: preserved", proc.stdout)
        self.assertIn("onboarding-state.json: preserved", proc.stdout)
        self.assertEqual((self.state_dir / "user-context.md").read_text(), "keep me\n")

    def test_init_overwrite_recreates_templates(self) -> None:
        self.state_dir.mkdir(parents=True)
        (self.state_dir / "user-context.md").write_text("replace me\n", encoding="utf-8")
        (self.state_dir / "onboarding-state.json").write_text("{}\n", encoding="utf-8")

        proc = self.run_script(
            INIT_SCRIPT,
            "--codex-home",
            str(self.codex_home),
            "--overwrite",
        )

        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        self.assertIn("user-context.md: overwritten", proc.stdout)
        self.assertIn(
            "# Investor Profile And Output Style", (self.state_dir / "user-context.md").read_text()
        )
        self.assertEqual(
            json.loads((self.state_dir / "onboarding-state.json").read_text()),
            {
                "status": None,
                "orientation": {},
                "memory_preferences": {},
                "source_setup": {},
                "connector_confirmation": {},
                "automations": {},
                "hero_prompt_choice": {
                    "status": None,
                    "options": ["earnings-deep-dive", "long-short-pitch", "idea-generation"],
                    "selected_skill": None,
                    "selected_anchor": None,
                },
            },
        )

    def test_reset_backs_up_known_files(self) -> None:
        self.state_dir.mkdir(parents=True)
        for filename in ("user-context.md", "category-state.json", "onboarding-state.json"):
            (self.state_dir / filename).write_text(filename, encoding="utf-8")
        backup_dir = self.tmp_path / "backup"

        proc = self.run_script(
            RESET_SCRIPT,
            "--state-dir",
            str(self.state_dir),
            "--backup-dir",
            str(backup_dir),
        )

        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        self.assertFalse(self.state_dir.exists())
        for filename in ("user-context.md", "category-state.json", "onboarding-state.json"):
            self.assertEqual((backup_dir / filename).read_text(), filename)

    def test_reset_dry_run_keeps_files(self) -> None:
        self.state_dir.mkdir(parents=True)
        (self.state_dir / "user-context.md").write_text("memory", encoding="utf-8")

        proc = self.run_script(RESET_SCRIPT, "--state-dir", str(self.state_dir), "--dry-run")

        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        self.assertTrue((self.state_dir / "user-context.md").exists())
        self.assertIn("Dry run only; no files were moved.", proc.stdout)

    def test_preflight_reports_missing_state_without_creating_files(self) -> None:
        proc = self.run_script(PREFLIGHT_SCRIPT, "--codex-home", str(self.codex_home))

        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertFalse(payload["initialized"])
        self.assertEqual(payload["user_context_status"], "missing")
        self.assertEqual(payload["onboarding_state_status"], "missing")
        self.assertTrue(payload["onboarding_incomplete"])
        self.assertEqual(payload["next_action"]["id"], "offer_orientation")
        self.assertEqual(
            payload["next_action"]["copy_ref"],
            "skills/user-context/references/onboarding.md#orientation-response-template",
        )
        self.assertFalse(self.state_dir.exists())

    def test_preflight_reports_initialized_state_and_empty_categories(self) -> None:
        self.assertEqual(
            self.run_script(INIT_SCRIPT, "--codex-home", str(self.codex_home)).returncode,
            0,
        )

        proc = self.run_script(PREFLIGHT_SCRIPT, "--codex-home", str(self.codex_home))

        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertTrue(payload["initialized"])
        self.assertIsNone(payload["onboarding_status"])
        self.assertTrue(payload["onboarding_incomplete"])
        self.assertEqual(payload["next_action"]["id"], "offer_orientation")
        self.assertEqual(
            payload["next_action"]["copy_ref"],
            "skills/user-context/references/onboarding.md#orientation-response-template",
        )
        self.assertIn("Investor Profile And Output Style", payload["empty_categories"])
        self.assertEqual(payload["errors"], [])

    def test_preflight_excludes_populated_categories(self) -> None:
        self.assertEqual(
            self.run_script(INIT_SCRIPT, "--codex-home", str(self.codex_home)).returncode,
            0,
        )
        user_context_path = self.state_dir / "user-context.md"
        user_context_path.write_text(
            user_context_path.read_text(encoding="utf-8").replace(
                "## Saved Links And Context\n\nstatus: not provided",
                "## Saved Links And Context\n\n- Watchlist tracker: https://example.com/watchlist",
                1,
            ),
            encoding="utf-8",
        )

        proc = self.run_script(PREFLIGHT_SCRIPT, "--codex-home", str(self.codex_home))

        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertNotIn("Investor Profile And Output Style", payload["empty_categories"])
        self.assertIn("Portfolio Watchlist And Repository Pointers", payload["empty_categories"])
        self.assertEqual(
            payload["saved_context"]["Investor Profile And Output Style"],
            "- Watchlist tracker: https://example.com/watchlist",
        )

    def test_preflight_reports_malformed_onboarding_state(self) -> None:
        self.assertEqual(
            self.run_script(INIT_SCRIPT, "--codex-home", str(self.codex_home)).returncode,
            0,
        )
        onboarding_path = self.state_dir / "onboarding-state.json"
        onboarding_path.write_text("{invalid\n", encoding="utf-8")

        proc = self.run_script(PREFLIGHT_SCRIPT, "--codex-home", str(self.codex_home))

        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertFalse(payload["initialized"])
        self.assertEqual(payload["onboarding_state_status"], "malformed")
        self.assertTrue(payload["onboarding_incomplete"])
        self.assertEqual(payload["next_action"]["id"], "repair_onboarding_state")
        self.assertEqual(
            payload["next_action"]["copy_ref"],
            "skills/user-context/references/onboarding.md#state-repair-response-template",
        )
        self.assertTrue(payload["errors"])
        self.assertEqual(onboarding_path.read_text(encoding="utf-8"), "{invalid\n")

    def test_preflight_reports_completed_onboarding(self) -> None:
        self.assertEqual(
            self.run_script(INIT_SCRIPT, "--codex-home", str(self.codex_home)).returncode,
            0,
        )
        onboarding_path = self.state_dir / "onboarding-state.json"
        onboarding_state = json.loads(onboarding_path.read_text(encoding="utf-8"))
        onboarding_state["status"] = "completed"
        onboarding_path.write_text(json.dumps(onboarding_state), encoding="utf-8")

        proc = self.run_script(PREFLIGHT_SCRIPT, "--codex-home", str(self.codex_home))

        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["onboarding_status"], "completed")
        self.assertFalse(payload["onboarding_incomplete"])
        self.assertIsNone(payload["next_action"])

    def test_router_wires_soft_read_only_preflight(self) -> None:
        router_text = ROUTER_SKILL.read_text(encoding="utf-8")

        self.assertIn("python3 skills/user-context/scripts/user_context_preflight.py", router_text)
        self.assertIn("shell working directory set to this plugin's root", router_text)
        self.assertIn("do not probe alternate relative paths", router_text)
        self.assertIn(
            "Pass relevant entries from `saved_context` to the selected lead skill",
            router_text,
        )
        self.assertIn("must not interpret saved output preferences", router_text)
        self.assertIn("must never block the requested workflow", router_text)
        self.assertIn('next_action.id = "offer_orientation"', router_text)
        self.assertIn("completed, deferred, or quiet", router_text)
        self.assertIn("onboarding, setup, orientation, or get-started requests", router_text)
        self.assertIn("`Help me get started`", router_text)
        self.assertIn(
            "remember, save, update, forget, inspect, export, reset, source-setup, or automation-setup",
            router_text,
        )
        self.assertIn("skills/user-context/SKILL.md", router_text)
        self.assertNotIn("init_user_context_state.py", router_text)

    def test_plugin_memory_reference_keeps_explicit_writes_narrow(self) -> None:
        skill_text = SKILL_ROOT.joinpath("SKILL.md").read_text(encoding="utf-8")
        memory_text = PLUGIN_MEMORY_REFERENCE.read_text(encoding="utf-8")

        self.assertIn("skills/user-context/references/plugin-memory.md", skill_text)
        self.assertIn("Save explicit user-provided durable instructions directly.", memory_text)
        self.assertIn(
            "Ask for approval before saving inferred, discovered, or source-derived entries.",
            memory_text,
        )
        self.assertIn("Do not save raw research packets, live company updates", memory_text)
        self.assertIn("Do not write connector readiness or `category-state.json`.", memory_text)
        self.assertIn("confirm that the saved category appears in `saved_context`", memory_text)

    def test_meeting_prep_consumes_source_plan_without_readiness_writes(self) -> None:
        meeting_prep_text = MEETING_PREP_SKILL.read_text(encoding="utf-8")

        self.assertIn(
            "python3 skills/user-context/scripts/user_context_preflight.py", meeting_prep_text
        )
        self.assertIn("source_category_plan", meeting_prep_text)
        self.assertIn(
            "Attempt the smallest useful native read only when the workflow needs that source.",
            meeting_prep_text,
        )
        self.assertIn(
            "Missing, malformed, or uninitialized context must not block meeting prep.",
            meeting_prep_text,
        )
        self.assertIn("write connector readiness", meeting_prep_text)
        self.assertIn("category-state.json", meeting_prep_text)
        for category in (
            "company_filings_ir",
            "earnings_transcripts_presentations",
            "internal_research",
            "portfolio_models_trackers",
            "market_data_estimates",
        ):
            self.assertIn(f"`{category}`", meeting_prep_text)
        self.assertNotIn("list_available_plugins_to_install", meeting_prep_text)
        self.assertNotIn("request_plugin_install", meeting_prep_text)

    def test_company_tearsheet_consumes_source_plan_without_readiness_writes(self) -> None:
        skill_text = COMPANY_TEARSHEET_SKILL.read_text(encoding="utf-8")
        source_text = COMPANY_TEARSHEET_SOURCE_REFERENCE.read_text(encoding="utf-8")

        self.assertIn("python3 skills/user-context/scripts/user_context_preflight.py", skill_text)
        self.assertIn("source_category_plan", skill_text)
        self.assertIn(
            "Attempt the smallest useful native read only when the workflow needs that source.",
            skill_text,
        )
        self.assertIn(
            "Missing, malformed, or uninitialized context must not block tearsheet work.",
            skill_text,
        )
        self.assertIn("write connector readiness", skill_text)
        self.assertIn("category-state.json", skill_text)
        for category in (
            "company_filings_ir",
            "earnings_transcripts_presentations",
            "internal_research",
            "portfolio_models_trackers",
            "market_data_estimates",
        ):
            self.assertIn(f"`{category}`", skill_text)
        self.assertIn("callable provider apps/connectors or user-provided exports", source_text)
        self.assertIn(
            "Do not imply direct access when the runtime route is not callable.", source_text
        )
        self.assertNotIn("list_available_plugins_to_install", skill_text)
        self.assertNotIn("request_plugin_install", skill_text)

    def test_all_visible_specialists_consume_user_context_preflight(self) -> None:
        actual_specialists = {
            path.parent.name
            for path in SKILL_ROOT.parent.glob("*/SKILL.md")
            if path.parent.name not in {PLUGIN_ID, "user-context"}
        }
        self.assertEqual(actual_specialists, SPECIALIST_SKILLS)

        for skill in sorted(SPECIALIST_SKILLS):
            text = (SKILL_ROOT.parent / skill / "SKILL.md").read_text(encoding="utf-8")
            with self.subTest(skill=skill):
                self.assertIn("python3 skills/user-context/scripts/user_context_preflight.py", text)
                self.assertIn("shell working directory set to this plugin's root", text)
                self.assertIn("saved_context", text)
                self.assertIn("source_category_plan", text)
                self.assertIn("next_action", text)
                self.assertIn("must not block", text)

    def test_source_selecting_specialists_use_shared_lazy_resolution_reference(self) -> None:
        reference_text = WORKFLOW_SOURCE_REFERENCE.read_text(encoding="utf-8")

        self.assertIn("Attempt the smallest useful native read", reference_text)
        self.assertIn("callable only when the runtime exposes a scoped route", reference_text)
        self.assertIn("category-state.json", reference_text)

        for skill, categories in sorted(SHARED_SOURCE_SKILLS.items()):
            text = (SKILL_ROOT.parent / skill / "SKILL.md").read_text(encoding="utf-8")
            with self.subTest(skill=skill):
                self.assertIn("../../shared/workflow-source-resolution.md", text)
                self.assertIn("Use `source_category_plan` lazily", text)
                for category in categories:
                    self.assertIn(f"`{category}`", text)

    def test_preflight_offers_source_setup_after_orientation(self) -> None:
        self.assertEqual(
            self.run_script(INIT_SCRIPT, "--codex-home", str(self.codex_home)).returncode,
            0,
        )
        onboarding_path = self.state_dir / "onboarding-state.json"
        onboarding_state = json.loads(onboarding_path.read_text(encoding="utf-8"))
        onboarding_state["orientation"]["status"] = "completed"
        onboarding_path.write_text(json.dumps(onboarding_state), encoding="utf-8")

        proc = self.run_script(PREFLIGHT_SCRIPT, "--codex-home", str(self.codex_home))

        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["next_action"]["id"], "configure_sources")
        self.assertEqual(
            payload["next_action"]["copy_ref"],
            "skills/user-context/references/onboarding.md#source-setup-response-template",
        )

    def test_preflight_ignores_legacy_pending_memory_preferences(self) -> None:
        self.assertEqual(
            self.run_script(INIT_SCRIPT, "--codex-home", str(self.codex_home)).returncode,
            0,
        )
        onboarding_path = self.state_dir / "onboarding-state.json"
        onboarding_state = json.loads(onboarding_path.read_text(encoding="utf-8"))
        onboarding_state["orientation"]["status"] = "completed"
        onboarding_path.write_text(json.dumps(onboarding_state), encoding="utf-8")

        proc = self.run_script(PREFLIGHT_SCRIPT, "--codex-home", str(self.codex_home))

        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["next_action"]["id"], "configure_sources")
        self.assertEqual(
            payload["next_action"]["copy_ref"],
            "skills/user-context/references/onboarding.md#source-setup-response-template",
        )

    def test_preflight_offers_source_setup_when_memory_preferences_are_skipped(self) -> None:
        self.assertEqual(
            self.run_script(INIT_SCRIPT, "--codex-home", str(self.codex_home)).returncode,
            0,
        )
        onboarding_path = self.state_dir / "onboarding-state.json"
        onboarding_state = json.loads(onboarding_path.read_text(encoding="utf-8"))
        onboarding_state["orientation"]["status"] = "completed"
        onboarding_state["memory_preferences"]["status"] = "skipped"
        onboarding_path.write_text(json.dumps(onboarding_state), encoding="utf-8")

        proc = self.run_script(PREFLIGHT_SCRIPT, "--codex-home", str(self.codex_home))

        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["next_action"]["id"], "configure_sources")

    def test_preflight_offers_automation_setup_after_source_setup(self) -> None:
        self.assertEqual(
            self.run_script(INIT_SCRIPT, "--codex-home", str(self.codex_home)).returncode,
            0,
        )
        onboarding_path = self.state_dir / "onboarding-state.json"
        onboarding_state = json.loads(onboarding_path.read_text(encoding="utf-8"))
        onboarding_state["orientation"]["status"] = "completed"
        onboarding_state["memory_preferences"]["status"] = "completed"
        onboarding_state["source_setup"]["status"] = "completed"
        onboarding_path.write_text(json.dumps(onboarding_state), encoding="utf-8")

        proc = self.run_script(PREFLIGHT_SCRIPT, "--codex-home", str(self.codex_home))

        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["next_action"]["id"], "configure_default_automation")
        self.assertEqual(
            payload["next_action"]["copy_ref"],
            "skills/user-context/references/onboarding.md#automation-setup-response-template",
        )

    def test_preflight_offers_hero_workflows_after_automation_resolution(self) -> None:
        self.assertEqual(
            self.run_script(INIT_SCRIPT, "--codex-home", str(self.codex_home)).returncode,
            0,
        )
        onboarding_path = self.state_dir / "onboarding-state.json"
        onboarding_state = json.loads(onboarding_path.read_text(encoding="utf-8"))
        onboarding_state["orientation"]["status"] = "completed"
        onboarding_state["memory_preferences"]["status"] = "completed"
        onboarding_state["source_setup"]["status"] = "completed"
        onboarding_state["automations"]["status"] = "skipped"
        onboarding_path.write_text(json.dumps(onboarding_state), encoding="utf-8")

        proc = self.run_script(PREFLIGHT_SCRIPT, "--codex-home", str(self.codex_home))

        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["next_action"]["id"], "choose_hero_workflow")
        self.assertEqual(
            payload["next_action"]["copy_ref"],
            "skills/user-context/references/onboarding.md#hero-workflow-response-template",
        )

    def test_preflight_stops_after_hero_workflow_selection(self) -> None:
        self.assertEqual(
            self.run_script(INIT_SCRIPT, "--codex-home", str(self.codex_home)).returncode,
            0,
        )
        onboarding_path = self.state_dir / "onboarding-state.json"
        onboarding_state = json.loads(onboarding_path.read_text(encoding="utf-8"))
        onboarding_state["orientation"]["status"] = "completed"
        onboarding_state["source_setup"]["status"] = "completed"
        onboarding_state["automations"]["status"] = "skipped"
        onboarding_state["hero_prompt_choice"]["status"] = "selected"
        onboarding_state["hero_prompt_choice"]["selected_skill"] = "earnings-deep-dive"
        onboarding_path.write_text(json.dumps(onboarding_state), encoding="utf-8")

        proc = self.run_script(PREFLIGHT_SCRIPT, "--codex-home", str(self.codex_home))

        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertIsNone(payload["next_action"])
        self.assertFalse(payload["onboarding_incomplete"])

    def test_preflight_exposes_four_step_progress_and_hero_options(self) -> None:
        self.assertEqual(
            self.run_script(INIT_SCRIPT, "--codex-home", str(self.codex_home)).returncode,
            0,
        )

        proc = self.run_script(PREFLIGHT_SCRIPT, "--codex-home", str(self.codex_home))

        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        progress = json.loads(proc.stdout)["onboarding_progress"]
        self.assertEqual(
            [step["label"] for step in progress["task_list"]],
            ["Intro and defaults", "Connectors and plugins", "Automation", "Hero workflows"],
        )
        self.assertEqual(
            progress["hero_prompt_options"],
            ["earnings-deep-dive", "long-short-pitch", "idea-generation"],
        )

    def test_preflight_echoes_automation_metadata_without_claiming_live_state(self) -> None:
        self.assertEqual(
            self.run_script(INIT_SCRIPT, "--codex-home", str(self.codex_home)).returncode,
            0,
        )
        onboarding_path = self.state_dir / "onboarding-state.json"
        onboarding_state = json.loads(onboarding_path.read_text(encoding="utf-8"))
        metadata = {
            "status": "completed",
            "configured": {
                "weekday-watchlist-brief": {
                    "automation_id": "automation-123",
                    "name": "Weekday Public Equity Watchlist Brief",
                    "kind": "heartbeat",
                    "status": "active",
                }
            },
        }
        onboarding_state["automations"] = metadata
        onboarding_path.write_text(json.dumps(onboarding_state), encoding="utf-8")

        proc = self.run_script(PREFLIGHT_SCRIPT, "--codex-home", str(self.codex_home))

        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["automation_state"], metadata)
        self.assertEqual(payload["errors"], [])

    def test_automation_reference_keeps_setup_explicit_and_runtime_checked(self) -> None:
        skill_text = SKILL_ROOT.joinpath("SKILL.md").read_text(encoding="utf-8")
        onboarding_text = ONBOARDING_REFERENCE.read_text(encoding="utf-8")
        config_text = AUTOMATION_CONFIG.read_text(encoding="utf-8")
        automation_text = AUTOMATION_REFERENCE.read_text(encoding="utf-8")

        self.assertIn("skills/user-context/references/automation.md", skill_text)
        self.assertIn("### Automation Setup Response Template", onboarding_text)
        self.assertIn("weekday-watchlist-brief", config_text)
        self.assertIn(
            "Do not create an automation until the user explicitly accepts", automation_text
        )
        self.assertIn("automation_update", automation_text)
        self.assertIn("tool_search", automation_text)
        self.assertIn("$CODEX_HOME/automations/*/automation.toml", automation_text)
        self.assertIn("### Canonical Automation Prompt", config_text)
        self.assertIn("Run a read-only weekday Public Equity Investing source check.", config_text)
        self.assertIn(
            "Report only: Upcoming Catalysts, Stale Sources, and Missing Inputs.", config_text
        )
        self.assertIn("Do not invent a portfolio or watchlist.", config_text)
        self.assertIn(
            "does not perform broad research or draft investment analysis;", automation_text
        )
        self.assertIn(
            "Use the configured canonical automation prompt substantially verbatim.",
            automation_text,
        )
        self.assertIn("Do not copy automation metadata into `user-context.md`.", automation_text)

    def test_preflight_offers_automation_when_source_setup_is_skipped(self) -> None:
        self.assertEqual(
            self.run_script(INIT_SCRIPT, "--codex-home", str(self.codex_home)).returncode,
            0,
        )
        onboarding_path = self.state_dir / "onboarding-state.json"
        onboarding_state = json.loads(onboarding_path.read_text(encoding="utf-8"))
        onboarding_state["orientation"]["status"] = "completed"
        onboarding_state["memory_preferences"]["status"] = "completed"
        onboarding_state["source_setup"]["status"] = "skipped"
        onboarding_path.write_text(json.dumps(onboarding_state), encoding="utf-8")

        proc = self.run_script(PREFLIGHT_SCRIPT, "--codex-home", str(self.codex_home))

        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        self.assertEqual(
            json.loads(proc.stdout)["next_action"]["id"],
            "configure_default_automation",
        )

    def test_onboarding_reference_uses_four_step_defaults_and_hero_copy(self) -> None:
        onboarding_text = ONBOARDING_REFERENCE.read_text(encoding="utf-8")
        plugin_memory_text = PLUGIN_MEMORY_REFERENCE.read_text(encoding="utf-8")
        intake_text = (SKILL_ROOT.parents[1] / "shared/deliverable-intake-policy.md").read_text(
            encoding="utf-8"
        )

        for step in (
            "## Step 1: Intro And Defaults",
            "## Step 2: Connectors And Plugins",
            "## Step 3: Automation",
            "## Step 4: Hero Workflows",
        ):
            self.assertIn(step, onboarding_text)
        self.assertIn("Reader-facing output: polished HTML research report", onboarding_text)
        self.assertIn("Word document (.docx)", onboarding_text)
        self.assertIn("Audience: PM or investment team", onboarding_text)
        self.assertIn("models, trackers, workbook updates, deck requests", onboarding_text)
        self.assertIn("1. **Analyze Latest Earnings:**", onboarding_text)
        self.assertIn("2. **Pressure-Test A Stock Idea:**", onboarding_text)
        self.assertIn("3. **Screen A Market Theme:**", onboarding_text)
        self.assertIn(
            "Keep live company updates and one-off research requests in the active workflow.",
            onboarding_text,
        )
        self.assertNotIn("## Memory Preferences", onboarding_text)
        self.assertNotIn("## Complete Or Defer", onboarding_text)
        self.assertIn("saved reader-facing output preference as the default", plugin_memory_text)
        self.assertIn("saved HTML preference resolves the presentation surface to HTML", intake_text)
        self.assertIn("saved HTML preference override an obvious workbook", intake_text)

    def test_source_category_config_defines_static_catalog_only(self) -> None:
        config = json.loads(SOURCE_CATEGORY_CONFIG.read_text(encoding="utf-8"))

        self.assertEqual(
            config["schema_version"], "public_equity_investing_source_category_config.v1"
        )
        self.assertEqual(
            set(config["categories"]),
            {
                "company_filings_ir",
                "earnings_transcripts_presentations",
                "internal_research",
                "portfolio_models_trackers",
                "market_data_estimates",
            },
        )
        self.assertIn("does not inspect connectors", config["description"])
        self.assertIn("does not", config["description"])
        for category in config["categories"].values():
            self.assertTrue(category["label"])
            self.assertTrue(category.get("preferred_apps") or category.get("preferred_plugins"))
            self.assertLessEqual(
                set(category),
                {"label", "preferred_apps", "preferred_plugins", "relevant_skills"},
            )

    def test_source_setup_reference_keeps_discovery_out_of_preflight(self) -> None:
        onboarding_text = ONBOARDING_REFERENCE.read_text(encoding="utf-8")
        runtime_text = SOURCE_CATEGORY_RUNTIME.read_text(encoding="utf-8")
        preflight_text = PREFLIGHT_SCRIPT.read_text(encoding="utf-8")

        self.assertIn("### Source Setup Response Template", onboarding_text)
        self.assertIn("This does not read source contents.", onboarding_text)
        self.assertIn("functions.list_available_plugins_to_install", runtime_text)
        self.assertIn("Do not perform connector reads merely to prove setup.", runtime_text)
        self.assertIn("Do not create, read, or migrate `category-state.json`.", runtime_text)
        self.assertIn("`app_connector_ids` intersects the `.app.json` ids", runtime_text)
        self.assertIn("Keep the app or connector route as fallback", runtime_text)
        self.assertIn(
            "skills or tools are not visible until the next turn or session refresh", runtime_text
        )
        self.assertIn("Install confirmed candidates one at a time.", runtime_text)
        self.assertIn('`action_type: "install"`', runtime_text)
        self.assertIn("`tool_type: <exact returned candidate tool_type>`", runtime_text)
        self.assertIn("`tool_id: <exact returned candidate id>`", runtime_text)
        self.assertIn("`suggest_reason: <concise one-line reason>`", runtime_text)
        self.assertIn("Do not guess `tool_id` values", runtime_text)
        self.assertNotIn("list_available_plugins_to_install", preflight_text)
        self.assertNotIn("request_plugin_install", preflight_text)

    def test_preflight_returns_unconfigured_source_category_plan_without_readiness_claims(
        self,
    ) -> None:
        proc = self.run_script(PREFLIGHT_SCRIPT, "--codex-home", str(self.codex_home))

        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        plan = json.loads(proc.stdout)["source_category_plan"]
        self.assertFalse(plan["readiness_claimed"])
        self.assertTrue(plan["has_setup_gaps"])
        self.assertEqual(
            set(plan["categories"]),
            {
                "company_filings_ir",
                "earnings_transcripts_presentations",
                "internal_research",
                "portfolio_models_trackers",
                "market_data_estimates",
            },
        )
        for category in plan["categories"].values():
            self.assertEqual(category["confirmation_status"], "unconfigured")
            self.assertEqual(category["readiness_status"], "unverified")
            self.assertTrue(category["setup_required"])
            self.assertFalse(category["eager_read"])
            self.assertNotIn("configured_route", category)
        self.assertFalse((self.state_dir / "category-state.json").exists())

    def test_preflight_echoes_saved_source_route_without_claiming_readiness(self) -> None:
        self.assertEqual(
            self.run_script(INIT_SCRIPT, "--codex-home", str(self.codex_home)).returncode,
            0,
        )
        onboarding_path = self.state_dir / "onboarding-state.json"
        onboarding_state = json.loads(onboarding_path.read_text(encoding="utf-8"))
        saved_route = {
            "status": "active",
            "source_kind": "app",
            "app": {"name": "Google Drive"},
        }
        onboarding_state["connector_confirmation"]["company_filings_ir"] = saved_route
        onboarding_path.write_text(json.dumps(onboarding_state), encoding="utf-8")

        proc = self.run_script(PREFLIGHT_SCRIPT, "--codex-home", str(self.codex_home))

        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        plan = json.loads(proc.stdout)["source_category_plan"]
        category = plan["categories"]["company_filings_ir"]
        self.assertEqual(category["confirmation_status"], "saved_unverified")
        self.assertEqual(category["readiness_status"], "unverified")
        self.assertFalse(category["setup_required"])
        self.assertEqual(category["configured_route"], saved_route)
        self.assertTrue(plan["has_setup_gaps"])
        self.assertFalse((self.state_dir / "category-state.json").exists())

    def test_preflight_keeps_missing_saved_source_route_as_setup_gap(self) -> None:
        self.assertEqual(
            self.run_script(INIT_SCRIPT, "--codex-home", str(self.codex_home)).returncode,
            0,
        )
        onboarding_path = self.state_dir / "onboarding-state.json"
        onboarding_state = json.loads(onboarding_path.read_text(encoding="utf-8"))
        onboarding_state["connector_confirmation"]["company_filings_ir"] = {"status": "missing"}
        onboarding_path.write_text(json.dumps(onboarding_state), encoding="utf-8")

        proc = self.run_script(PREFLIGHT_SCRIPT, "--codex-home", str(self.codex_home))

        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        category = json.loads(proc.stdout)["source_category_plan"]["categories"][
            "company_filings_ir"
        ]
        self.assertEqual(category["confirmation_status"], "saved_unverified")
        self.assertTrue(category["setup_required"])

    def test_preflight_suppresses_next_action_when_deferred(self) -> None:
        self.assertEqual(
            self.run_script(INIT_SCRIPT, "--codex-home", str(self.codex_home)).returncode,
            0,
        )
        onboarding_path = self.state_dir / "onboarding-state.json"
        onboarding_state = json.loads(onboarding_path.read_text(encoding="utf-8"))
        onboarding_state["status"] = "deferred"
        onboarding_path.write_text(json.dumps(onboarding_state), encoding="utf-8")

        proc = self.run_script(PREFLIGHT_SCRIPT, "--codex-home", str(self.codex_home))

        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertTrue(payload["onboarding_incomplete"])
        self.assertIsNone(payload["next_action"])

    def test_preflight_suppresses_next_action_when_quiet(self) -> None:
        self.assertEqual(
            self.run_script(INIT_SCRIPT, "--codex-home", str(self.codex_home)).returncode,
            0,
        )
        onboarding_path = self.state_dir / "onboarding-state.json"
        onboarding_state = json.loads(onboarding_path.read_text(encoding="utf-8"))
        onboarding_state["status"] = "quiet"
        onboarding_path.write_text(json.dumps(onboarding_state), encoding="utf-8")

        proc = self.run_script(PREFLIGHT_SCRIPT, "--codex-home", str(self.codex_home))

        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertFalse(payload["onboarding_incomplete"])
        self.assertIsNone(payload["next_action"])


if __name__ == "__main__":
    unittest.main()
