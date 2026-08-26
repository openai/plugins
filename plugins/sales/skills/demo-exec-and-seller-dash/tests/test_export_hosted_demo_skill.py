"""Executable parity and portability checks for the single-file hosted Sales demo."""

from __future__ import annotations

import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from sales_test_support import SalesTestCase, load_script, run_command

SKILL_DIRECTORY = Path(__file__).resolve().parent.parent
EXPORTER = SKILL_DIRECTORY / "scripts" / "export_hosted_demo_skill.py"
LAUNCHER = SKILL_DIRECTORY / "scripts" / "start_demo_fast.py"


class HostedDemoSkillExportTests(SalesTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.exporter = load_script(EXPORTER, "sales_demo_hosted_export_test")
        cls.launcher = cls.exporter.load_launcher()
        cls.document = cls.exporter.build_hosted_skill(launcher=cls.launcher)

    def response_for(self, state: str, document: str | None = None) -> str:
        source = self.document if document is None else document
        match = re.search(
            rf"<!-- BEGIN PREPARED RESPONSE: {re.escape(state)} -->\n"
            rf"(.*?)\n<!-- END PREPARED RESPONSE: {re.escape(state)} -->",
            source,
            re.DOTALL,
        )
        self.assertIsNotNone(match, f"Missing hosted prepared response for {state}")
        assert match is not None
        return match.group(1)

    def test_embedded_states_match_launcher_except_the_hosted_install_handoff(self) -> None:
        self.assertEqual(
            tuple(self.launcher.STATE_HEADINGS),
            ("leadership", "account", "meeting", "complete", "presentation", "email"),
        )
        for state in self.launcher.STATE_HEADINGS:
            with self.subTest(state=state):
                launched = run_command(
                    [sys.executable, str(LAUNCHER), "--step", state, "--delivery-mode", "work"],
                )
                self.assertEqual(launched.returncode, 0, launched.stderr)
                expected = launched.stdout.strip()
                if state == "meeting":
                    self.assertIn(self.exporter.INSTALLED_MEETING_NEXT_STEP, expected)
                    expected = expected.replace(
                        self.exporter.INSTALLED_MEETING_NEXT_STEP,
                        self.exporter.HOSTED_MEETING_NEXT_STEP,
                        1,
                    )
                self.assertEqual(self.response_for(state), expected)

    def test_hosted_document_is_self_contained_safe_compact_and_truthful(self) -> None:
        self.assertLess(len(self.document.encode("utf-8")), 100_000)
        self.assertIn("## Mandatory Hosted Execution Override", self.document)
        self.assertIn("send the corresponding embedded prepared response verbatim", self.document)
        self.assertIn("Do not read local files, run commands", self.document)
        self.assertIn("call tools or connectors", self.document)
        self.assertIn("or perform external writes", self.document)
        for inaccessible in (
            "references/",
            "scripts/",
            "start_demo_fast.py",
            "render_demo_dashboard.py",
            "functions.exec",
            "tools.exec",
            "localhost",
            "127.0.0.1",
            "{{",
        ):
            self.assertNotIn(inaccessible, self.document, inaccessible)

        self.assertEqual(self.document.count(self.exporter.OPENING_DISCLOSURE), 1)
        self.assertIn(self.launcher.HOSTED_LEADERSHIP_URL, self.document)
        self.assertIn(self.launcher.HOSTED_SELLER_URL, self.document)
        self.assertIn("1JM3bmarfM9neOoTOBtGW12wGUYuYeLqT9HWKdDlMamU", self.document)
        for account in ("Northstar Health", "Atlas Manufacturing", "Solstice Financial"):
            self.assertIn(account, self.document)

        meeting = self.response_for("meeting")
        complete = self.response_for("complete")
        self.assertIn("could be saved to Salesforce after your approval", meeting)
        self.assertIn(self.exporter.HOSTED_MEETING_NEXT_STEP, meeting)
        self.assertNotIn("1. Save it to Salesforce", meeting)
        self.assertNotIn("No Salesforce records were changed.", meeting)
        self.assertIn("The Salesforce update was simulated.", complete)
        self.assertIn("No Salesforce records were changed.", complete)
        self.assertIn("separately and explicitly requested save is simulated only", self.document)

    def test_export_embeds_the_simplified_northstar_deck_and_meeting_responses(self) -> None:
        presentation = self.response_for("presentation")
        self.assertIn(
            "Okay, I've built a draft of a deck you can go through with the customer.", presentation
        )
        self.assertIn("**Recommended approach**", presentation)
        self.assertIn("**What's going well:**", presentation)
        self.assertIn("**Their core objection is:**", presentation)
        self.assertIn("**Potential mitigations:**", presentation)
        self.assertIn("**Messaging:**", presentation)
        self.assertIn("**Who to pull into the meeting and what they should say:**", presentation)
        self.assertNotIn("**Scenario**", presentation)
        self.assertNotIn("**Context gathered for your deck**", presentation)
        self.assertNotRegex(presentation, r"(?m)^\d+\. ")
        self.assertTrue(
            presentation.endswith(
                "**Next:** Let’s fast-forward to after the customer meeting and review "
                "the follow-up and proposed Salesforce updates."
            )
        )
        self.assertIn("`okay`, `yes`, `continue`", self.document)

        meeting = self.response_for("meeting")
        self.assertTrue(meeting.startswith("Your messaging landed well with the customer."))
        self.assert_contains(
            meeting,
            "- Sync with engineering on their reliability roadmap",
            "- **Salesforce update:** Make sure your CRM is up to date for your team's visibility",
            "| Field | Current | Proposed |",
            (
                "**These updates could be saved to Salesforce after your approval; "
                "nothing has been applied.**"
            ),
        )
        self.assertTrue(meeting.endswith(self.exporter.HOSTED_MEETING_NEXT_STEP))
        self.assertNotIn(self.exporter.INSTALLED_MEETING_NEXT_STEP, meeting)
        self.assertNotIn("Save it to Salesforce", meeting)
        self.assertNotRegex(meeting, r"(?m)^\d+\. ")
        self.assertNotIn("**Scenario**", meeting)
        self.assertNotIn("**Output:**", meeting)
        self.assertNotIn("**Your goal:**", meeting)

    def test_source_changes_regenerate_both_skill_contract_and_canonical_response(self) -> None:
        self.assertEqual(self.document, self.exporter.build_hosted_skill(launcher=self.launcher))

        with tempfile.TemporaryDirectory() as directory:
            isolated = Path(directory)
            references = isolated / "references"
            references.mkdir()
            for name in ("demo-portfolio.json", "demo-leadership.json"):
                shutil.copyfile(SKILL_DIRECTORY / "references" / name, references / name)

            original_core = (SKILL_DIRECTORY / "SKILL.md").read_text(encoding="utf-8")
            marker = "Show how connected sales context supports"
            self.assertIn(marker, original_core)
            (isolated / "SKILL.md").write_text(
                original_core.replace(marker, "UPDATED HOSTED CORE: " + marker, 1),
                encoding="utf-8",
            )

            original_flow = self.launcher.FLOW_REFERENCE
            changed_flow = references / "changed-canonical-flow.md"
            before = original_flow.read_text(encoding="utf-8")
            self.assertIn("It's 8:30 AM on Monday", before)
            changed_flow.write_text(
                before.replace("It's 8:30 AM on Monday", "It's 8:45 AM on Monday", 1),
                encoding="utf-8",
            )
            self.launcher.FLOW_REFERENCE = changed_flow
            try:
                changed = self.exporter.build_hosted_skill(isolated, launcher=self.launcher)
                self.assertEqual(
                    changed, self.exporter.build_hosted_skill(isolated, launcher=self.launcher)
                )
            finally:
                self.launcher.FLOW_REFERENCE = original_flow

        self.assertIn("UPDATED HOSTED CORE", changed)
        self.assertIn("It's 8:45 AM on Monday", self.response_for("leadership", changed))
        self.assertNotEqual(changed, self.document)
        self.assertIn("## Deterministic Source Provenance", changed)

    def test_cli_exports_the_complete_single_file_without_other_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "nested" / "sales-plugin-demo.md"
            result = run_command([sys.executable, str(EXPORTER), "--output", str(destination)])
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(destination.read_text(encoding="utf-8"), self.document)
            self.assertEqual(
                [path.name for path in destination.parent.iterdir()], [destination.name]
            )
            self.assertIn("Exported", result.stdout)


if __name__ == "__main__":
    unittest.main()
