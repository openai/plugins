"""Regression coverage for the connector-free seller account-home demo."""

from __future__ import annotations

import json
import re
import shutil
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from typing import Any

from sales_test_support import DEMO_RENDERER as RENDERER
from sales_test_support import SKILL_DIRECTORY, SalesTestCase, run_command

CANONICAL_NORTHSTAR_TEMPLATE_URL = "https://docs.google.com/presentation/d/1JM3bmarfM9neOoTOBtGW12wGUYuYeLqT9HWKdDlMamU/edit?slide=id.p1#slide=id.p1"
HOSTED_LEADERSHIP_URL = "https://meridian-sales-operating-views.openai.chatgpt.site/leadership"
HOSTED_SELLER_URL = "https://meridian-sales-operating-views.openai.chatgpt.site/seller"
NORTHSTAR_PRESENTATION_NEXT_STEP = (
    "**Next:** Let’s fast-forward to after the customer meeting and review the follow-up "
    "and proposed Salesforce updates."
)
INSTALLED_MEETING_NEXT_STEP = (
    "**Next:** Build your seller dashboard and try meeting prep, account planning, "
    "and other workflows with your real data."
)
CRM_REVIEW_NOTICE = (
    "**These updates could be saved to Salesforce after your approval; nothing has been applied.**"
)
RENDERER_PATH = SKILL_DIRECTORY / "scripts" / "render_demo_dashboard.py"


class AccountPrioritizationDemoTests(SalesTestCase):
    def setUp(self) -> None:
        self.portfolio: dict[str, Any] = RENDERER.load_portfolio()

    def test_bundled_portfolio_has_the_documented_groups_and_accounts(self) -> None:
        self.assertEqual(len(self.portfolio["workNow"]), 5)
        self.assertEqual(len(self.portfolio["watch"]), 3)
        self.assertEqual(len(self.portfolio["paused"]), 2)
        self.assertEqual(self.portfolio["workNow"][0]["rank"], 1)
        self.assertEqual(self.portfolio["watch"][0]["rank"], 6)
        self.assertEqual(self.portfolio["demo"]["mode"], "fictional")
        self.assertEqual(self.portfolio["title"], "Riley’s Account Home")
        self.assertEqual(self.portfolio["seller"]["name"], "Riley Morgan")
        self.assertEqual(self.portfolio["seller"]["firstName"], "Riley")
        self.assertEqual(self.portfolio["viewerInitials"], "RM")
        self.assertEqual(self.portfolio["recentLaunch"]["targetContact"], "Jordan Lee")
        self.assertIn("fictional", self.portfolio["demo"]["disclaimer"].lower())
        self.assertEqual(
            sum(account["confidence"] == "High" for account in self.portfolio["workNow"]),
            3,
        )

    def test_portfolio_supports_account_home_and_legacy_personalized_titles(self) -> None:
        supported_titles = (
            "Riley’s Account Home",
            "Riley's Account Home",
            "Riley’s Account Overview",
            "Riley's Account Overview",
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_path = Path(temporary_directory) / "portfolio.json"
            for title in supported_titles:
                with self.subTest(title=title):
                    portfolio = {**self.portfolio, "title": title}
                    fixture_path.write_text(json.dumps(portfolio), encoding="utf-8")

                    loaded = RENDERER.load_portfolio(fixture_path)

                    self.assertEqual(loaded["title"], title)

    def test_demo_priority_scores_and_northstar_reply_states_are_explicitly_grounded(self) -> None:
        account_rows = [
            account for group in RENDERER.EXPECTED_COUNTS for account in self.portfolio[group]
        ]
        self.assertEqual(
            [account["priorityScore"] for account in account_rows],
            [98, 93, 89, 84, 78, 71, 66, 59, 42, 34],
        )
        for account in account_rows:
            with self.subTest(account=account["account"]):
                detail_score = (
                    self.portfolio["accountDetails"].get(account["account"], {}).get("score")
                )
                if detail_score is not None:
                    self.assertEqual(account["priorityScore"], detail_score)

        northstar = account_rows[0]
        self.assertEqual(northstar["account"], "Northstar Health")
        self.assertEqual(northstar["stage"], "Security review")
        self.assertEqual(northstar["status"], "Pilot review upcoming")
        self.assertTrue(northstar["nextAction"].startswith("Prepare for the meeting:"))
        self.assertIn("your pilot scorecard", northstar["nextAction"])

        events = self.portfolio["accountDetails"]["Northstar Health"]["events"]
        unresolved_email = [
            event
            for event in events
            if event["source"] == "Gmail" and event.get("replyStatus") == "Unresolved"
        ]
        replied_customer_message = [
            event
            for event in events
            if event["source"] == "Slack"
            and "#ext-northstar-health" in event["reference"]
            and event.get("replyStatus") == "Replied"
        ]
        self.assertEqual(len(unresolved_email), 1)
        self.assertEqual(len(replied_customer_message), 1)

        slack_source = (SKILL_DIRECTORY / "references" / "sources" / "slack.md").read_text(
            encoding="utf-8"
        )
        customer_channel = slack_source.split("## Northstar Health Shared Customer Channel", 1)[
            1
        ].split("## Northstar Health Account Team", 1)[0]
        self.assertIn(
            "- Riley Morgan: I'll bring the existing pilot-readiness presentation",
            customer_channel,
        )

        upcoming_decisions = [event for event in events if event["source"] == "Google Calendar"]
        self.assertEqual(len(upcoming_decisions), 1)
        decision_context = " ".join(
            [upcoming_decisions[0]["title"], upcoming_decisions[0]["detail"]]
        ).lower()
        for fact in ("pilot", "uptime", "decision"):
            with self.subTest(meeting_fact=fact):
                self.assertIn(fact, decision_context)

    def test_company_context_covers_every_dashboard_account(self) -> None:
        company_context = (SKILL_DIRECTORY / "references" / "company-context.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("Everything in this reference is fictional", company_context)
        self.assertIn("## Editable Scenario Card", company_context)
        self.assertIn("Featured target-company archetype", company_context)
        self.assertIn("Primary buyer persona", company_context)
        self.assertIn(
            f"**Featured sample account:** {self.portfolio['workNow'][0]['account']}",
            company_context,
        )
        for group in RENDERER.EXPECTED_COUNTS:
            for account in self.portfolio[group]:
                with self.subTest(account=account["account"]):
                    self.assertIn(
                        f"## Account {account['rank']}: {account['account']}", company_context
                    )

    def test_connector_source_fixtures_are_labeled_fictional_and_cover_hero_account(self) -> None:
        fixture_names = (
            "salesforce.md",
            "gmail.md",
            "google-calendar.md",
            "granola.md",
            "slack.md",
            "google-drive.md",
            "gtm-resource-hub.md",
        )

        for fixture_name in fixture_names:
            with self.subTest(source=fixture_name):
                source_text = (SKILL_DIRECTORY / "references" / "sources" / fixture_name).read_text(
                    encoding="utf-8"
                )
                self.assertIn("fictional", source_text.lower())
                self.assertIn(self.portfolio["workNow"][0]["account"], source_text)

    def test_demo_flow_preserves_the_three_act_demo_and_reviewed_terminal_state(self) -> None:
        flow = (SKILL_DIRECTORY / "references" / "demo-flow.md").read_text(encoding="utf-8")

        self.assertEqual(
            re.findall(r"^### Step \d+: ([a-z_]+)$", flow, flags=re.MULTILINE),
            [
                "leadership_dashboard",
                "account_priority_view",
                "meeting_followup",
                "salesforce_review_complete",
            ],
        )
        self.assertIn("### Branch: connector_explanation", flow)
        self.assertIn("### Branch: northstar_presentation_draft", flow)
        self.assertIn("### Branch: launch_reengagement_draft", flow)
        self.assertIn("### Branch: site_publication", flow)
        self.assertIn("### Branch: crm_update_rules", flow)
        self.assertIn("Track the active state", flow)
        self.assertIn("Return immediately after sending each final message", flow)

    def test_demo_openings_keep_persona_goal_and_grounded_context_concise(self) -> None:
        flow = (SKILL_DIRECTORY / "references" / "demo-flow.md").read_text(encoding="utf-8")
        launcher = SKILL_DIRECTORY / "scripts" / "start_demo_fast.py"
        openings = (
            (
                "leadership",
                "leadership_dashboard",
                "You're **Maya Chen",
                (
                    "It's 8:30 AM on Monday and you'd like to review your team's progress towards "
                    "your revenue targets and learn where you can be most helpful. "
                    "Your Exec Dashboard is ready with the latest context."
                ),
                "**Connected context**",
            ),
            (
                "account",
                "account_priority_view",
                "You're now **Riley Morgan",
                "You'd like help prioritizing your top 3 accounts to focus on this week.",
                "**Key context**",
            ),
        )

        for step, state, persona, goal, source_heading in openings:
            with self.subTest(step=step):
                section = re.search(
                    rf"^### Step \d+: {re.escape(state)}\n(?P<section>.*?)(?=^### Step \d+:)",
                    flow,
                    flags=re.MULTILINE | re.DOTALL,
                )
                self.assertIsNotNone(section)
                if section is None:
                    continue
                final_message = section.group("section").split("- **Final message:**", 1)[1]
                required_order = ("**Scenario**", persona, goal, source_heading, "**Overview**")
                if step == "leadership":
                    required_order = (
                        "**Scenario**",
                        persona,
                        goal,
                        source_heading,
                        "| Connector | What was found | Example resource |",
                        "**Overview**",
                    )
                positions = [final_message.index(value) for value in required_order]
                self.assertEqual(positions, sorted(positions))

                delivered = run_command(
                    [sys.executable, str(launcher), "--step", step, "--delivery-mode", "work"],
                    cwd=SKILL_DIRECTORY,
                    check=True,
                ).stdout
                for expected in (persona, goal, source_heading, "**Overview**"):
                    self.assertIn(expected, delivered)
                self.assertLess(delivered.index("**Scenario**"), delivered.index(persona))
                self.assertLess(delivered.index(goal), delivered.index(source_heading))
                self.assertLess(delivered.index(source_heading), delivered.index("**Overview**"))
                self.assertNotIn("**Output:**", delivered)
                self.assertNotIn("**Your goal:**", delivered)
                if step == "leadership":
                    self.assertEqual(len(re.findall(r"(?m)^\d+\. ", delivered)), 2)
                    self.assertIn("**Scenario**", delivered)
                    self.assertEqual(
                        delivered.count("| Connector | What was found | Example resource |"), 1
                    )
                else:
                    self.assertNotRegex(delivered, r"(?m)^\d+\. ")
                    self.assertTrue(
                        delivered.rstrip().endswith(
                            "After you've taken a look, let's make a deck to prep for the meeting "
                            "to make sure it lands"
                        )
                    )
                    self.assertNotIn("See the next demo: Following up", delivered)
                    self.assertIn("**Scenario**", delivered)
                    self.assertNotIn("| Connector | What was found | Example resource |", delivered)
                    self.assertNotIn("**Sources reviewed**", delivered)

    def test_only_leadership_shows_connectors_and_followup_copy_stays_focused(self) -> None:
        flow = (SKILL_DIRECTORY / "references" / "demo-flow.md").read_text(encoding="utf-8")
        launcher = SKILL_DIRECTORY / "scripts" / "start_demo_fast.py"
        connector_heading = "| Connector | What was found | Example resource |"

        self.assertEqual(flow.count(connector_heading), 1)
        first_step = flow.split("### Step 1: leadership_dashboard", 1)[1].split(
            "### Step 2: account_priority_view", 1
        )[0]
        self.assertIn(connector_heading, first_step)
        self.assertIn("**Connected context**", first_step)

        scenarios = (
            ("account", "**Switching gears: Riley Morgan's account home**"),
            (
                "presentation",
                "**Northstar Health: pilot-completion and rollout-readiness presentation**",
            ),
            ("email", "**Northstar Health pilot-readiness and customer-sync draft**"),
            ("meeting", "Your messaging landed well with the customer."),
        )
        for step, title in scenarios:
            with self.subTest(step=step):
                delivered = run_command(
                    [sys.executable, str(launcher), "--step", step, "--delivery-mode", "work"],
                    cwd=SKILL_DIRECTORY,
                    check=True,
                ).stdout
                self.assertIn(title, delivered)
                self.assertNotIn(connector_heading, delivered)
                self.assertNotIn("**Connected context**", delivered)
                self.assertNotIn("**Sources reviewed**", delivered)
                if step == "account":
                    self.assertIn("**Key context**", delivered)
                    self.assertIn("**Overview**", delivered)
                    self.assertIn("**[Seller Account Dashboard]", delivered)
                    self.assertLess(
                        delivered.index("**Scenario**"),
                        delivered.index("You're now **Riley Morgan"),
                    )
                elif step == "presentation":
                    introduction = (
                        "Okay, I've built a draft of a deck you can go through with the customer."
                    )
                    self.assertLess(delivered.index(title), delivered.index(introduction))
                    self.assertLess(
                        delivered.index(introduction),
                        delivered.index(CANONICAL_NORTHSTAR_TEMPLATE_URL),
                    )
                    self.assertLess(
                        delivered.index(CANONICAL_NORTHSTAR_TEMPLATE_URL),
                        delivered.index("**Recommended approach**"),
                    )
                    self.assertNotIn("You're **Riley Morgan", delivered)
                    self.assertNotIn("You're now **Riley Morgan", delivered)
                    self.assertNotIn("**Scenario**", delivered)
                    self.assertNotIn("**Output:**", delivered)
                    self.assertNotIn("**Your goal:**", delivered)
                    self.assertNotIn("**Context gathered for your deck**", delivered)
                    self.assertNotIn("$420,000", delivered)
                    self.assertNotRegex(delivered, r"(?m)^\d+\. ")
                    self.assertTrue(delivered.rstrip().endswith(NORTHSTAR_PRESENTATION_NEXT_STEP))
                    for recommendation in (
                        "**What's going well:**",
                        "**Their core objection is:**",
                        "**To address this:**",
                        "**Potential mitigations:**",
                        "**Messaging:**",
                        "**Who to pull into the meeting and what they should say:**",
                    ):
                        self.assertIn(recommendation, delivered)
                    for person in ("Jordan Lee", "Casey Patel", "Priya Shah", "Riley Morgan"):
                        self.assertIn(person, delivered)
                elif step == "email":
                    self.assertNotIn("**Scenario**", delivered)
                    self.assertNotIn("**Output:**", delivered)
                    self.assertNotIn("**Your goal:**", delivered)
                    self.assertEqual(delivered.count("-----"), 2)
                    self.assertIn("create a draft in Gmail or even send it", delivered)
                    self.assertIn("if requested", delivered)
                    self.assertIn("fast forward to after your meeting", delivered)
                    self.assertNotRegex(delivered, r"(?m)^\d+\. ")
                elif step == "meeting":
                    self.assertTrue(delivered.startswith(title))
                    self.assertNotIn("You're **Riley Morgan", delivered)
                    self.assertNotIn("You're now **Riley Morgan", delivered)
                    self.assertNotIn("**Northstar Health meeting follow-up**", delivered)
                    self.assertNotIn("**Scenario**", delivered)
                    self.assertNotIn("**Output:**", delivered)
                    self.assertNotIn("**Your goal:**", delivered)
                    self.assertNotIn("**CRM guardrail:**", delivered)
                    self.assertLess(
                        delivered.index("**What happens next**"),
                        delivered.index("| Field | Current | Proposed |"),
                    )
                    self.assertIn("- Sync with engineering on their reliability roadmap", delivered)
                    self.assertIn(
                        "- **Salesforce update:** Make sure your CRM is up to date for "
                        "your team's visibility",
                        delivered,
                    )
                    self.assertIn("| Field | Current | Proposed |", delivered)
                    self.assertIn(CRM_REVIEW_NOTICE, delivered)
                    self.assertTrue(delivered.rstrip().endswith(INSTALLED_MEETING_NEXT_STEP))
                    self.assertNotRegex(delivered, r"(?m)^\d+\. ")
                    self.assertNotIn("Save it to Salesforce", delivered)

    def test_demo_skill_fast_start_requires_only_its_own_portable_package(self) -> None:
        demo_skill = (SKILL_DIRECTORY / "SKILL.md").read_text(encoding="utf-8")

        self.assert_contains(
            demo_skill,
            "## Fast Demo Start",
            "first answer in under ten seconds",
            "Run exactly one prepared launcher action through `functions.exec`",
            "safe instruction/resource reads do not count as launcher actions",
            "scripts/start_demo_fast.py --step leadership",
            "the same ready-to-send opening",
        )
        self.assertNotIn("ALL_TOOLS", demo_skill)
        self.assertNotIn("sitesAvailable", demo_skill)
        self.assertNotIn("--sites-available", demo_skill)
        self.assertIn("complete within this skill directory", demo_skill)
        self.assert_excludes(
            demo_skill,
            "../../dependencies.md",
            "../../shared_skill_instructions.md",
            "../index/SKILL.md",
            "../prioritize-accounts/",
            "../executive-account-overview/",
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            isolated_skill = Path(temporary_directory) / "demo-exec-and-seller-dash"
            shutil.copytree(
                SKILL_DIRECTORY,
                isolated_skill,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
            opening = run_command(
                [
                    sys.executable,
                    str(isolated_skill / "scripts" / "start_demo_fast.py"),
                    "--delivery-mode",
                    "work",
                ],
                cwd=isolated_skill,
                check=True,
            ).stdout
            self.assertIn(HOSTED_LEADERSHIP_URL, opening)
            self.assertNotIn("127.0.0.1", opening)

    def test_fast_launcher_returns_the_prepared_canonical_response_in_one_local_command(
        self,
    ) -> None:
        leadership = RENDERER.load_leadership_data(portfolio=self.portfolio)

        with tempfile.TemporaryDirectory() as temporary_directory:
            site_root = Path(temporary_directory)
            account_path = RENDERER.render_dashboard(
                self.portfolio, output_path=site_root / "index.html"
            )
            RENDERER.render_leadership_dashboard(
                leadership, output_path=site_root / "leadership" / "index.html"
            )

            with RENDERER.create_dashboard_server(account_path, root_directory=site_root) as server:
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                base_url = f"http://127.0.0.1:{server.server_address[1]}"
                launcher = SKILL_DIRECTORY / "scripts" / "start_demo_fast.py"

                try:
                    started = time.monotonic()
                    opening = run_command(
                        [
                            sys.executable,
                            str(launcher),
                            "--step",
                            "leadership",
                            "--sites-available",
                            "--base-url",
                            f"{base_url}/leadership/#deals",
                        ],
                        cwd=SKILL_DIRECTORY,
                        check=True,
                    ).stdout
                    self.assertLess(time.monotonic() - started, 10)
                    self.assertIn("You're **Maya Chen", opening)
                    self.assertIn("**Connected context**", opening)
                    self.assertIn(f"[sales leadership dashboard]({base_url}/leadership/)", opening)
                    self.assertNotIn("**FYI:**", opening)
                    self.assertIn(
                        "1. Next demo showing the seller account dashboard\n"
                        "2. Learn more about how Codex gathers context to give a better answer",
                        opening,
                    )
                    self.assertNotRegex(opening, r"(?im)^\d+\. .*\b(?:publish|sites?)\b")
                    self.assertNotIn("{{", opening)
                    self.assertNotIn("- **Sites-available reply", opening)

                    without_sites = run_command(
                        [sys.executable, str(launcher), "--base-url", base_url],
                        cwd=SKILL_DIRECTORY,
                        check=True,
                    ).stdout
                    self.assertIn(
                        "1. Next demo showing the seller account dashboard", without_sites
                    )
                    self.assertEqual(opening, without_sites)

                    for step, required in (
                        ("account", f"[Seller Account Dashboard]({base_url}/)"),
                        ("meeting", INSTALLED_MEETING_NEXT_STEP),
                        (
                            "presentation",
                            CANONICAL_NORTHSTAR_TEMPLATE_URL,
                        ),
                        ("email", "Northstar pilot readiness and the remaining uptime question"),
                    ):
                        with self.subTest(step=step):
                            response = run_command(
                                [
                                    sys.executable,
                                    str(launcher),
                                    "--step",
                                    step,
                                    "--base-url",
                                    base_url,
                                ],
                                cwd=SKILL_DIRECTORY,
                                check=True,
                            ).stdout
                            self.assertIn(required, response)
                            self.assertNotIn("{{", response)
                finally:
                    server.shutdown()
                    thread.join(timeout=2)

    def test_browserless_launcher_defaults_to_published_sites_and_the_hardcoded_deck(self) -> None:
        launcher = SKILL_DIRECTORY / "scripts" / "start_demo_fast.py"

        for step, expected_url in (
            ("leadership", HOSTED_LEADERSHIP_URL),
            ("account", HOSTED_SELLER_URL),
            ("presentation", CANONICAL_NORTHSTAR_TEMPLATE_URL),
        ):
            with self.subTest(step=step):
                response = run_command(
                    [sys.executable, str(launcher), "--step", step],
                    cwd=SKILL_DIRECTORY,
                    check=True,
                ).stdout
                self.assertIn(expected_url, response)
                self.assertNotIn("127.0.0.1", response)
                self.assertNotIn("localhost", response)

        invalid_preview = run_command(
            [sys.executable, str(launcher), "--base-url", "https://example.com"],
            cwd=SKILL_DIRECTORY,
        )
        self.assertNotEqual(invalid_preview.returncode, 0)

    def test_hosted_work_mode_reuses_both_published_dashboards_without_local_preview(self) -> None:
        launcher = SKILL_DIRECTORY / "scripts" / "start_demo_fast.py"

        for step, expected_url in (
            ("leadership", HOSTED_LEADERSHIP_URL),
            ("account", HOSTED_SELLER_URL),
        ):
            with self.subTest(step=step):
                response = run_command(
                    [sys.executable, str(launcher), "--step", step, "--delivery-mode", "work"],
                    cwd=SKILL_DIRECTORY,
                    check=True,
                ).stdout
                self.assertIn(expected_url, response)
                self.assertNotIn("127.0.0.1", response)
                self.assertNotIn("localhost", response)
                self.assertNotIn("Publish this dashboard", response)

        skill = (SKILL_DIRECTORY / "SKILL.md").read_text(encoding="utf-8")
        flow = (SKILL_DIRECTORY / "references" / "demo-flow.md").read_text(encoding="utf-8")
        for instruction_surface in (skill, flow):
            with self.subTest(instruction_surface=instruction_surface[:40]):
                self.assertIn("DEVELOPMENT", instruction_surface)
                self.assertIn("WORK MODE/PUBLISHED DEMOS", instruction_surface)
                self.assertIn(HOSTED_LEADERSHIP_URL, instruction_surface)
                self.assertIn(HOSTED_SELLER_URL, instruction_surface)
        self.assertIn(
            f"[sales leadership dashboard]({HOSTED_LEADERSHIP_URL})",
            flow,
        )
        self.assertIn(f"[Seller Account Dashboard]({HOSTED_SELLER_URL})", flow)
        self.assertNotRegex(flow, r"\]\((?:actual-|localhost|127\.0\.0\.1)")
        self.assertIn("Both", skill)
        self.assertIn("never substitute `localhost`", skill)
        self.assertIn("without explicit authorization", skill)
        self.assertIn(
            "Future work: package the complete, self-contained demo skill for hosted delivery "
            "(for example, the OpenAI CDN) so a demo prompt can load it from a hosted URL.",
            skill,
        )

    def test_hosted_work_mode_needs_no_writable_temporary_directory(self) -> None:
        launcher = SKILL_DIRECTORY / "scripts" / "start_demo_fast.py"
        bootstrap = (
            "import runpy, sys, tempfile\n"
            "launcher = sys.argv.pop(1)\n"
            "tempfile.gettempdir = lambda: (_ for _ in ()).throw("
            "FileNotFoundError('No usable temporary directory'))\n"
            "runpy.run_path(launcher, run_name='__main__')\n"
        )
        for step, expected_url in (
            ("leadership", HOSTED_LEADERSHIP_URL),
            ("account", HOSTED_SELLER_URL),
            ("presentation", CANONICAL_NORTHSTAR_TEMPLATE_URL),
        ):
            with self.subTest(step=step):
                response = run_command(
                    [
                        sys.executable,
                        "-c",
                        bootstrap,
                        str(launcher),
                        "--step",
                        step,
                        "--delivery-mode",
                        "work",
                    ],
                    cwd=SKILL_DIRECTORY,
                    check=True,
                )

                self.assertIn(expected_url, response.stdout)
                self.assertNotRegex(response.stdout, r"\]\(https?://(?:www\.)?google\.com/?\)")
                self.assertNotIn("hosted-link placeholder", response.stdout)
                self.assertEqual(response.stderr, "")

    def test_hosted_demo_declares_immutable_links_before_running_any_command(self) -> None:
        skill = (SKILL_DIRECTORY / "SKILL.md").read_text(encoding="utf-8")
        flow = (SKILL_DIRECTORY / "references" / "demo-flow.md").read_text(encoding="utf-8")
        link_contract = skill.split("## Canonical Published Demo Links", maxsplit=1)[1].split(
            "## Fast Demo Start", maxsplit=1
        )[0]

        for canonical_url in (
            HOSTED_LEADERSHIP_URL,
            HOSTED_SELLER_URL,
            CANONICAL_NORTHSTAR_TEMPLATE_URL,
        ):
            with self.subTest(canonical_url=canonical_url):
                self.assertIn(canonical_url, link_contract)
                self.assertIn(canonical_url, flow.split("## State Machine", maxsplit=1)[0])

        self.assertIn("Never substitute the Google homepage", link_contract)
        self.assertIn("including any fallback when command execution is unavailable", link_contract)
        self.assertIn("--step leadership --delivery-mode work", skill)
        self.assertIn("--step account --delivery-mode work", skill)
        self.assertIn("--step presentation --delivery-mode work", skill)
        self.assertNotIn("visibleBrowserUrl", skill)

    def test_hosted_work_mode_rejects_a_visible_local_preview(self) -> None:
        launcher = SKILL_DIRECTORY / "scripts" / "start_demo_fast.py"
        response = run_command(
            [
                sys.executable,
                str(launcher),
                "--step",
                "leadership",
                "--delivery-mode",
                "work",
                "--base-url",
                "http://127.0.0.1:9876",
            ],
            cwd=SKILL_DIRECTORY,
        )

        self.assertNotEqual(response.returncode, 0)
        self.assertIn("Work-mode delivery requires hosted Sites URLs", response.stderr)

    def test_sites_never_changes_or_clutters_the_two_choice_leadership_menu(self) -> None:
        launcher = SKILL_DIRECTORY / "scripts" / "start_demo_fast.py"
        flow = (SKILL_DIRECTORY / "references" / "demo-flow.md").read_text(encoding="utf-8")
        responses = []

        for arguments in ([], ["--sites-available"]):
            with self.subTest(sites_available=bool(arguments)):
                response = run_command(
                    [
                        sys.executable,
                        str(launcher),
                        "--step",
                        "leadership",
                        "--delivery-mode",
                        "work",
                        *arguments,
                    ],
                    cwd=SKILL_DIRECTORY,
                    check=True,
                ).stdout
                responses.append(response)
                self.assertIn(HOSTED_LEADERSHIP_URL, response)
                self.assertNotIn("**FYI:**", response)
                self.assertEqual(
                    re.findall(r"(?m)^\d+\. ([^\n]+)$", response),
                    [
                        "Next demo showing the seller account dashboard",
                        "Learn more about how Codex gathers context to give a better answer",
                    ],
                )
                self.assertNotRegex(response, r"(?im)^\d+\. .*\b(?:publish|sites?)\b")

        self.assertEqual(responses[0], responses[1])

        compatibility_branch = flow.split("### Branch: site_publication", maxsplit=1)[1].split(
            "### Branch:", maxsplit=1
        )[0]
        self.assertIn("Retained as a compatibility identifier only", compatibility_branch)
        self.assertIn(
            "not a numbered choice or an action within the canned walkthrough", compatibility_branch
        )
        self.assertIn("If the user separately asks", compatibility_branch)
        self.assertIn("exit the fictional demo", compatibility_branch)
        self.assertIn("specifically authorized artifact", compatibility_branch)
        self.assertIn("Do not publish the canned dashboard", compatibility_branch)
        self.assertNotRegex(compatibility_branch, r"(?m)^\d+\. ")

    def test_leadership_followups_do_not_repeat_topics_already_answered(self) -> None:
        flow = (SKILL_DIRECTORY / "references" / "demo-flow.md").read_text(encoding="utf-8")
        skill = (SKILL_DIRECTORY / "SKILL.md").read_text(encoding="utf-8")
        question_map = (SKILL_DIRECTORY / "references" / "demo-followup-map.md").read_text(
            encoding="utf-8"
        )

        leadership = flow.split("### Step 1: leadership_dashboard", maxsplit=1)[1].split(
            "### Step 2: account_priority_view", maxsplit=1
        )[0]
        self.assertIn(
            "After you've reviewed:\n\n"
            "1. Next demo showing the seller account dashboard\n"
            "2. Learn more about how Codex gathers context to give a better answer",
            leadership,
        )
        self.assertIn("- **Reply `2`:** Enter `connector_explanation`", leadership)
        self.assertNotIn("Help me understand the biggest forecast risks", leadership)

        connector_branch = flow.split("### Branch: connector_explanation", maxsplit=1)[1].split(
            "### Branch:", maxsplit=1
        )[0]
        self.assertIn(
            "offer only `1. Next demo showing the seller account dashboard`", connector_branch
        )
        self.assertIn("never repeat the context-explanation option", connector_branch)

        risk_branch = flow.split("### Branch: forecast_risk_explanation", maxsplit=1)[1].split(
            "### Branch:", maxsplit=1
        )[0]
        self.assertIn("Optional, explicitly requested", risk_branch)
        self.assertIn("never suggest the forecast-risk question again", risk_branch)
        self.assertIn(
            "Never suggest an option, forecast-risk question, or context explanation", skill
        )
        self.assertIn("Never repeat a suggestion the user has already chosen", question_map)

    def test_hosted_work_mode_rejects_loopback_and_invalid_dashboard_routes(self) -> None:
        launcher = SKILL_DIRECTORY / "scripts" / "start_demo_fast.py"
        invalid_argument_sets = (
            ("--base-url", "http://127.0.0.1:9000"),
            ("--leadership-url", "http://127.0.0.1:9000/leadership"),
            ("--seller-url", "http://localhost:9000/seller"),
            (
                "--seller-url",
                "https://meridian-sales-operating-views.openai.chatgpt.site/leadership",
            ),
        )

        for arguments in invalid_argument_sets:
            with self.subTest(arguments=arguments):
                result = run_command(
                    [sys.executable, str(launcher), "--delivery-mode", "work", *arguments],
                    cwd=SKILL_DIRECTORY,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(result.stderr)

    def test_demo_flow_uses_numbered_final_messages_instead_of_input_widgets(self) -> None:
        flow = (SKILL_DIRECTORY / "references" / "demo-flow.md").read_text(encoding="utf-8")
        skill = (SKILL_DIRECTORY / "SKILL.md").read_text(encoding="utf-8")

        self.assertGreaterEqual(
            len(
                re.findall(
                    r"(?m)(?:^Next steps$|After you've reviewed:$)",
                    flow,
                )
            ),
            1,
        )
        self.assertIn("After you've reviewed:", flow)
        self.assertIn(
            "1. Next demo showing the seller account dashboard\n"
            "2. Learn more about how Codex gathers context to give a better answer",
            flow,
        )
        self.assertNotIn("Help me understand the biggest forecast risks", flow)
        self.assertNotRegex(flow, r"(?im)^\d+\. .*\b(?:publish|sites?)\b")
        self.assertNotIn("When Sites is unavailable", flow)
        self.assertNotIn("Sites-available reply", flow)
        self.assertIn(
            "After you've taken a look, let's make a deck to prep for the meeting "
            "to make sure it lands",
            flow,
        )
        self.assertNotIn("After you've taken a look, we can:", flow)
        self.assertNotIn("See the next demo: Following up after the Northstar meeting", flow)
        self.assertIn(NORTHSTAR_PRESENTATION_NEXT_STEP, flow)
        self.assertIn(
            "- **Requested next demo:** Treat `okay`, `yes`, `continue`, or another acceptance "
            "of the suggested next step as a direct transition to `meeting_followup`",
            flow,
        )
        self.assertNotIn("Publish this account overview", flow)
        self.assertNotIn("1. Save it to Salesforce", flow)
        self.assertIn(INSTALLED_MEETING_NEXT_STEP, flow)
        self.assertIn("Each demo step is a complete normal assistant final message", skill)
        self.assertIn("Do not call `request_user_input`", skill)
        self.assertNotIn("**Form question:**", flow)
        self.assertNotIn("**Recommended choice:**", flow)

    def test_opening_includes_dashboard_and_meeting_starts_with_save_approval(self) -> None:
        flow = (SKILL_DIRECTORY / "references" / "demo-flow.md").read_text(encoding="utf-8")

        first_step = re.search(
            r"^### Step 1: leadership_dashboard\n(?P<section>.*?)(?=^### Step 2:)",
            flow,
            flags=re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(first_step)
        if first_step is not None:
            section = first_step.group("section")
            self.assertIn("| Connector | What was found | Example resource |", section)
            self.assertIn("**Overview**", section)
            self.assertIn("[sales leadership dashboard]", section)
            self.assertIn("Maya Chen", section)
            self.assertNotIn("**FYI:**", section)
            self.assertIn(
                "Click here to open your "
                "**[sales leadership dashboard]"
                "(https://meridian-sales-operating-views.openai.chatgpt.site/leadership)**. "
                "After you've reviewed:",
                section,
            )
            self.assertIn("1. Next demo showing the seller account dashboard", section)
            self.assertIn(
                "2. Learn more about how Codex gathers context to give a better answer", section
            )
            self.assertNotRegex(section, r"(?m)^3\. ")
            self.assertNotRegex(section, r"(?im)^\d+\. .*\b(?:publish|sites?)\b")
            self.assertNotIn("| Rank | Account |", section)
            self.assertNotIn("| Rank | Account | Opportunity |", section)
            self.assertLess(
                section.index("| Connector | What was found | Example resource |"),
                section.index("**Overview**"),
            )
            takeaways = section.split("**Overview**", maxsplit=1)[1].split(
                "[sales leadership dashboard]",
                maxsplit=1,
            )[0]
            self.assertGreaterEqual(len(re.findall(r"(?m)^- ", takeaways)), 1)
            self.assertLessEqual(len(re.findall(r"(?m)^- ", takeaways)), 3)

        seller_step = re.search(
            r"^### Step 2: account_priority_view\n(?P<section>.*?)(?=^### Step 3:)",
            flow,
            flags=re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(seller_step)
        if seller_step is not None:
            section = seller_step.group("section")
            self.assertIn("Riley Morgan", section)
            self.assertIn("**Overview**", section)
            self.assertIn("[Seller Account Dashboard]", section)
            self.assertNotIn("**Your priorities**", section)
            self.assertNotIn("3 high-priority accounts | 2 additional actions", section)
            self.assertIn(
                "After you've taken a look, let's make a deck to prep for the meeting "
                "to make sure it lands",
                section,
            )
            self.assertNotIn("After you've taken a look, we can:", section)
            self.assertNotIn("See the next demo: Following up after the Northstar meeting", section)
            self.assertNotRegex(section, r"(?m)^\d+\. ")
            self.assertNotIn("Publish this account overview", section)
            self.assertIn("**Key context**", section)
            self.assertNotIn("**Sources reviewed**", section)
            self.assertNotIn("| Connector | What was found | Example resource |", section)
            self.assertLess(
                section.index("**Key context**"),
                section.index("**Overview**"),
            )
            key_context = section.split("**Key context**", maxsplit=1)[1].split(
                "**Overview**", maxsplit=1
            )[0]
            self.assertEqual(len(re.findall(r"(?m)^- ", key_context)), 3)
            account_home = section.split("**Overview**", maxsplit=1)[1].split(
                "[Seller Account Dashboard]",
                maxsplit=1,
            )[0]
            self.assertEqual(len(re.findall(r"(?m)^- ", account_home)), 3)
            self.assert_matches(
                account_home,
                r"(?m)^- \*\*Northstar Health — prepare for the pilot review:",
                r"(?m)^- \*\*Atlas Manufacturing — investigate a performance issue:",
                r"(?m)^- \*\*Solstice Financial — confirm the product fits:",
            )
            self.assertIn("review the customer's concerns", account_home)
            self.assertIn("meets the customer's admin requirements", account_home)
            self.assertNotIn("| Rank | Account |", section)

        meeting_step = re.search(
            r"^### Step 3: meeting_followup\n(?P<section>.*?)(?=^### Step 4:)",
            flow,
            flags=re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(meeting_step)
        if meeting_step is not None:
            section = meeting_step.group("section")
            self.assertIn(CRM_REVIEW_NOTICE, section)
            self.assertIn(INSTALLED_MEETING_NEXT_STEP, section)
            self.assertNotIn("1. Save it to Salesforce", section)
            self.assertIn("Current", section)
            self.assertIn("Proposed", section)
            self.assertIn("Security review", section)

        terminal = flow.split("### Step 4: salesforce_review_complete", maxsplit=1)[1]
        terminal = re.split(r"^### Branch:", terminal, maxsplit=1, flags=re.MULTILINE)[0]
        self.assertNotIn("\nNext steps\n", terminal)
        self.assertRegex(terminal, r"(?m)^1\. \*\*Build your seller account home\*\*")
        self.assertRegex(terminal, r"(?m)^2\. \*\*Prepare for a customer meeting\*\*")
        self.assertRegex(terminal, r"(?m)^3\. \*\*Review meeting follow-up and CRM updates\*\*")

    def test_northstar_presentation_branch_reuses_the_exact_existing_google_slides_deck(
        self,
    ) -> None:
        references = SKILL_DIRECTORY / "references"
        flow = (references / "demo-flow.md").read_text(encoding="utf-8")
        skill = (SKILL_DIRECTORY / "SKILL.md").read_text(encoding="utf-8")
        presentation_brief = (references / "northstar-presentation-brief.md").read_text(
            encoding="utf-8"
        )
        gtm_hub = (references / "sources" / "gtm-resource-hub.md").read_text(encoding="utf-8")
        google_drive = (references / "sources" / "google-drive.md").read_text(encoding="utf-8")

        branch = flow.split("### Branch: northstar_presentation_draft", maxsplit=1)[1]
        branch = re.split(r"^### Branch:", branch, maxsplit=1, flags=re.MULTILINE)[0]
        self.assertNotIn("| Connector | What was found | Example resource |", branch)
        final_message = branch.split("- **Final message:**\n\n", maxsplit=1)[1].split(
            "\n- **Artifact link:**", maxsplit=1
        )[0]
        self.assertNotIn("**Scenario**", final_message)
        self.assertNotIn("**Output:**", final_message)
        self.assertNotIn("**Your goal:**", final_message)
        self.assertNotIn("**Context gathered for your deck**", final_message)
        self.assertNotIn("$420,000", final_message)
        self.assertNotRegex(final_message, r"(?m)^\d+\. ")
        self.assert_contains(
            branch,
            "northstar-presentation-brief.md",
            "sources/granola.md",
            "sources/google-drive.md",
            "sources/gtm-resource-hub.md",
            "sources/salesforce.md",
        )

        exact_deck = CANONICAL_NORTHSTAR_TEMPLATE_URL
        self.assertIn("[Open the Northstar pilot-readiness presentation]", final_message)
        self.assertIn(exact_deck, final_message)
        self.assertNotIn("verified-local-editable-northstar-powerpoint-path", branch)
        self.assertNotIn("[Preview the presentation]", final_message)
        self.assertIn("1,200-user pilot", final_message)
        self.assertIn("**Recommended approach**", final_message)
        self.assertIn("**What's going well:**", final_message)
        self.assertIn("**Their core objection is:**", final_message)
        self.assertIn("**To address this:**", final_message)
        self.assertIn("**Potential mitigations:**", final_message)
        self.assertIn("**Messaging:**", final_message)
        self.assertIn("**Who to pull into the meeting and what they should say:**", final_message)
        self.assertEqual(len(re.findall(r"(?m)^- \*\*", final_message)), 3)
        self.assertEqual(len(re.findall(r"(?m)^  - \*\*", final_message)), 3)
        self.assertIn("engagement, repeat-usage, and deployment goals", final_message)
        self.assertIn("customer-reported uptime feedback", final_message)
        self.assertTrue(final_message.rstrip().endswith(NORTHSTAR_PRESENTATION_NEXT_STEP))
        for person in ("Jordan Lee", "Casey Patel", "Priya Shah", "Riley Morgan"):
            self.assertIn(person, final_message)
        self.assertIn("northstar-presentation-brief.md", skill)
        self.assertIn("sources/gtm-resource-hub.md", skill)
        self.assertIn("do not invoke presentation-authoring tools", skill)
        self.assertIn(exact_deck, presentation_brief)
        self.assertIn(exact_deck, google_drive)
        self.assertIn(exact_deck, skill)
        self.assertEqual(
            self.portfolio["accountDetails"]["Northstar Health"]["presentationUrl"], exact_deck
        )
        leadership_data = RENDERER.load_leadership_data(portfolio=self.portfolio)
        northstar_decision = next(
            decision
            for decision in leadership_data["decisions"]
            if "Northstar Health" in decision["accounts"]
        )
        presentation_evidence = next(
            evidence
            for evidence in northstar_decision["sourceEvidence"]
            if evidence["source"] == "Google Drive"
        )
        self.assertEqual(presentation_evidence["url"], exact_deck)
        self.assertIn("canonical northstar customer presentation", presentation_brief.lower())
        self.assertIn("canonical northstar customer presentation", google_drive.lower())

        for artifact_text in (presentation_brief, google_drive, gtm_hub):
            with self.subTest(artifact=artifact_text[:60]):
                self.assertIn("Northstar", artifact_text)

        self.assertIn("Cedar Valley Care", gtm_hub)
        self.assertIn("Lakeshore Care Network", gtm_hub)
        self.assertIn("external sharing", gtm_hub)
        self.assertIn("Regulated-Industry Executive Decision Brief", google_drive)
        self.assertIn("Pilot Progress + Open Security Questions", google_drive)

    def test_northstar_presentation_never_assumes_customer_permission_or_external_action(
        self,
    ) -> None:
        references = SKILL_DIRECTORY / "references"
        flow = (references / "demo-flow.md").read_text(encoding="utf-8")
        branch = flow.split("### Branch: northstar_presentation_draft", maxsplit=1)[1]
        branch = re.split(r"^### Branch:", branch, maxsplit=1, flags=re.MULTILINE)[0]
        presentation_brief = (references / "northstar-presentation-brief.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("only after the user explicitly chooses", presentation_brief)
        self.assertIn("$420,000 proposed expansion", presentation_brief)
        self.assertIn("meeting, or authorization to send, publish, or share", presentation_brief)
        self.assertIn("unapproved services", branch)
        self.assertIn("booked meeting", branch)
        self.assertIn("Never substitute a generated PowerPoint", branch)
        self.assertIn("Do not create, copy, edit, export", branch)
        self.assertNotIn("Publish this dashboard", branch)
        self.assertNotIn("/Users/", branch)

    def test_northstar_pilot_readiness_is_consistent_across_all_scenario_sources(self) -> None:
        references = SKILL_DIRECTORY / "references"
        northstar = self.portfolio["accountDetails"]["Northstar Health"]
        leadership = RENDERER.load_leadership_data(portfolio=self.portfolio)
        first_decision = leadership["decisions"][0]

        self.assertEqual(first_decision["accounts"], ["Northstar Health"])
        self.assertEqual(first_decision["impact"], 420000)
        for required_fact in ("pilot", "uptime", "Jordan Lee", "Casey Patel", "Priya Shah"):
            with self.subTest(required_fact=required_fact):
                joined = " ".join(
                    (
                        first_decision["problem"],
                        first_decision["customerContext"],
                        first_decision["proposedSolution"],
                        first_decision["nextStep"],
                        northstar["strategy"],
                        northstar["risk"],
                    )
                )
                self.assertIn(required_fact.lower(), joined.lower())

        source_paths = (
            references / "company-context.md",
            references / "northstar-followup-meeting.md",
            references / "crm-update-rules.md",
            references / "sources" / "salesforce.md",
            references / "sources" / "gmail.md",
            references / "sources" / "google-calendar.md",
            references / "sources" / "granola.md",
            references / "sources" / "slack.md",
            references / "sources" / "google-drive.md",
        )
        for source_path in source_paths:
            with self.subTest(source=source_path.name):
                source_text = source_path.read_text(encoding="utf-8").lower()
                self.assertIn("pilot", source_text)
                self.assertIn("uptime", source_text)

    def test_terminal_offers_real_workflows_without_claiming_connector_availability(
        self,
    ) -> None:
        flow = (SKILL_DIRECTORY / "references" / "demo-flow.md").read_text(encoding="utf-8")
        terminal = flow.split("### Step 4: salesforce_review_complete", maxsplit=1)[1]
        terminal = re.split(r"^### Branch:", terminal, maxsplit=1, flags=re.MULTILINE)[0]

        self.assertIn("**Demo complete**", terminal)
        self.assertIn("The Salesforce update was simulated.", terminal)
        self.assertIn("**No Salesforce records were changed.**", terminal)
        self.assertIn("**Try it with your own data**", terminal)
        self.assertIn(
            "Never claim a provider is already connected or available without verification",
            terminal,
        )
        self.assertIn("separate action-specific approval", terminal)
        final_message = terminal.split("- **Final message:**", maxsplit=1)[1].split(
            "- **Workflow selection:**", maxsplit=1
        )[0]
        numbered_workflows = re.findall(r"(?m)^\d+\. \*\*([^*]+)\*\*[^\n]*$", final_message)
        self.assertEqual(
            numbered_workflows,
            [
                "Build your seller account home",
                "Prepare for a customer meeting",
                "Review meeting follow-up and CRM updates",
            ],
        )
        self.assertLessEqual(len(numbered_workflows), 3)
        workflow_lines = re.findall(r"(?m)^\d+\. [^\n]+$", final_message)
        self.assertTrue(all("Connect " in workflow for workflow in workflow_lines))
        self.assertRegex(workflow_lines[0], r"Salesforce, Gmail, Google Calendar, and Slack")
        self.assertRegex(workflow_lines[1], r"Google Calendar, Gmail, and Google Drive")
        self.assertRegex(workflow_lines[2], r"Salesforce and meeting notes")
        self.assertTrue(
            final_message.rstrip().endswith(
                "Tell me which workflow you'd like to run, and I'll walk you through "
                "connecting the tools it needs."
            )
        )
        self.assert_excludes(
            final_message,
            "**Sales integrations in your environment**",
            "**Available in this session:**",
            "**Not currently available:**",
            "**Available to add:**",
            "{connected connectors}",
            "{available connectors}",
            "are already connected",
            "connection not verified",
        )

    def test_completion_launcher_emits_a_truthful_read_only_real_workflow_handoff(self) -> None:
        launcher = SKILL_DIRECTORY / "scripts" / "start_demo_fast.py"
        source_paths = (
            SKILL_DIRECTORY / "references" / "demo-portfolio.json",
            SKILL_DIRECTORY / "references" / "sources" / "salesforce.md",
        )
        original_sources = {path: path.read_bytes() for path in source_paths}

        completed = run_command(
            [sys.executable, str(launcher), "--step", "complete", "--delivery-mode", "work"],
            cwd=SKILL_DIRECTORY,
            check=True,
        ).stdout

        self.assertTrue(completed.startswith("**Demo complete**"))
        self.assertIn("The Salesforce update was simulated.", completed)
        self.assertIn("**No Salesforce records were changed.**", completed)
        self.assertIn("**Try it with your own data**", completed)
        self.assertEqual(
            re.findall(r"(?m)^\d+\. \*\*([^*]+)\*\*", completed),
            [
                "Build your seller account home",
                "Prepare for a customer meeting",
                "Review meeting follow-up and CRM updates",
            ],
        )
        self.assertTrue(
            completed.rstrip().endswith(
                "Tell me which workflow you'd like to run, and I'll walk you through "
                "connecting the tools it needs."
            )
        )
        self.assert_excludes(
            completed,
            "**Available in this session:**",
            "**Not currently available:**",
            "**Available to add:**",
            "already connected",
            "{connected connectors}",
            "{available connectors}",
            "{{",
            "- **Workflow selection:**",
        )
        self.assertEqual({path: path.read_bytes() for path in source_paths}, original_sources)

        flow = (SKILL_DIRECTORY / "references" / "demo-flow.md").read_text(encoding="utf-8")
        meeting = flow.split("### Step 3: meeting_followup", maxsplit=1)[1].split(
            "### Step 4: salesforce_review_complete", maxsplit=1
        )[0]
        self.assertIn(CRM_REVIEW_NOTICE, meeting)
        self.assertIn(INSTALLED_MEETING_NEXT_STEP, meeting)
        self.assertNotIn("1. Save it to Salesforce", meeting)
        self.assertIn("explicitly approved the exact displayed proposal", meeting)

    def test_meeting_shows_concise_next_actions_before_a_review_only_field_diff(
        self,
    ) -> None:
        flow = (SKILL_DIRECTORY / "references" / "demo-flow.md").read_text(encoding="utf-8")
        meeting = re.search(
            r"^### Step 3: meeting_followup\n(?P<section>.*?)(?=^### Step 4:)",
            flow,
            flags=re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(meeting)
        if meeting is None:
            return

        section = meeting.group("section")
        final_message = section.split("- **Final message:**\n\n", maxsplit=1)[1].split(
            "\n- **Reply `1`:**", maxsplit=1
        )[0]
        self.assertTrue(final_message.startswith("Your messaging landed well with the customer."))
        self.assertNotIn("**Northstar Health meeting follow-up**", final_message)
        self.assertNotIn("**Scenario**", final_message)
        self.assertNotIn("**Output:**", final_message)
        self.assertNotIn("**Your goal:**", final_message)
        self.assertIn("**What happens next**", section)
        self.assertNotIn("**Sources reviewed**", section)
        self.assertNotIn("| Connector | What was found | Example resource |", section)
        self.assertLess(
            final_message.index("**What happens next**"),
            final_message.index("**Salesforce Opportunity — proposed updates**"),
        )
        next_actions = final_message.split("**What happens next**\n\n", maxsplit=1)[1].split(
            "\n\n**Salesforce Opportunity — proposed updates**", maxsplit=1
        )[0]
        self.assertEqual(
            next_actions.splitlines(),
            [
                "- Sync with engineering on their reliability roadmap",
                "- **Salesforce update:** Make sure your CRM is up to date for your team's visibility",
            ],
        )
        self.assertIn("| Field | Current | Proposed |", final_message)
        self.assertIn(CRM_REVIEW_NOTICE, final_message)
        self.assertTrue(final_message.rstrip().endswith(INSTALLED_MEETING_NEXT_STEP))
        self.assertNotIn("1. Save it to Salesforce", final_message)
        self.assertNotIn("2. Explain the CRM update rules", final_message)
        self.assertNotIn("3. Return to the account overview", final_message)

    def test_only_the_opening_chat_message_discloses_the_scenario(self) -> None:
        flow = (SKILL_DIRECTORY / "references" / "demo-flow.md").read_text(encoding="utf-8")

        for step, section in re.findall(
            r"^### Step \d+: ([a-z_]+)\n(.*?)(?=^### (?:Step \d+:|Branch:)|\Z)",
            flow,
            flags=re.MULTILINE | re.DOTALL,
        ):
            with self.subTest(step=step):
                final_message = section.split("- **Final message:**", maxsplit=1)[1]
                final_message = re.split(r"(?m)^- \*\*", final_message, maxsplit=1)[0]
                final_message = final_message.replace(
                    "See the next demo: Following up after the Northstar meeting", ""
                )
                disclosure_terms = re.findall(
                    r"\b(?:fictional|simulated|sample|demo)\b",
                    final_message,
                    flags=re.IGNORECASE,
                )
                if step == "leadership_dashboard":
                    self.assertTrue(disclosure_terms)
                    self.assertEqual(
                        len(re.findall(r"\bfictional\b", final_message, flags=re.IGNORECASE)),
                        1,
                    )
                elif step == "salesforce_review_complete":
                    self.assertEqual(
                        [term.lower() for term in disclosure_terms], ["demo", "simulated"]
                    )
                    self.assertIn("**No Salesforce records were changed.**", final_message)
                else:
                    self.assertFalse(disclosure_terms)

    def test_scenario_distinguishes_jordans_seller_view_from_mayas_division_leadership(
        self,
    ) -> None:
        context = (SKILL_DIRECTORY / "references" / "company-context.md").read_text(
            encoding="utf-8"
        )
        flow = (SKILL_DIRECTORY / "references" / "demo-flow.md").read_text(encoding="utf-8")
        leadership = RENDERER.load_leadership_data(portfolio=self.portfolio)

        self.assertIn("**Seller persona:** Riley Morgan", context)
        self.assertIn("**Division-leader persona:** Maya Chen", context)
        self.assertIn("**Demo perspective changes:**", context)
        self.assertIn("38 accounts", context)
        self.assertIn("31 open opportunities", context)
        self.assertEqual(leadership["company"]["salesLeader"], "Maya Chen")

        leadership_step = re.search(
            r"^### Step 1: leadership_dashboard\n(?P<section>.*?)(?=^### Step 2:)",
            flow,
            flags=re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(leadership_step)
        if leadership_step is not None:
            self.assertIn("Maya Chen", leadership_step.group("section"))
            self.assertRegex(
                leadership_step.group("section"),
                r"(?i)division lead|vice president of sales",
            )
        seller_step = re.search(
            r"^### Step 2: account_priority_view\n(?P<section>.*?)(?=^### Step 3:)",
            flow,
            flags=re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(seller_step)
        if seller_step is not None:
            self.assertIn("Riley Morgan", seller_step.group("section"))
            self.assertIn("account home", seller_step.group("section").lower())

    def test_opening_message_matches_the_requested_copy_and_connector_table(self) -> None:
        flow = (SKILL_DIRECTORY / "references" / "demo-flow.md").read_text(encoding="utf-8")
        context = (SKILL_DIRECTORY / "references" / "company-context.md").read_text(
            encoding="utf-8"
        )

        self.assertIn(
            "Note: This walkthrough uses fictional data to demonstrate what's possible "
            "before you connect your own company context.",
            flow,
        )
        self.assertIn("You're **Maya Chen, Vice President of Sales", flow)
        self.assertIn("Meridian Cloud builds governed enterprise AI assistants", flow)
        self.assertIn("three regional teams, 38 accounts, and 31 opportunities", flow)
        self.assertIn(
            "Riley Morgan, Strategic Enterprise Account Executive at Meridian Cloud", flow
        )
        self.assertIn("| Connector | What was found | Example resource |", flow)
        self.assertNotIn("| Connector category | Connector name |", flow)
        self.assertIn(
            "You'd like help prioritizing your top 3 accounts to focus on this week.", flow
        )
        self.assertIn("**Overview**", flow)
        self.assertIn("[Seller Account Dashboard]", flow)
        self.assertNotIn("**Your priorities**", flow)
        self.assertNotIn("3 high-priority accounts | 2 additional actions", flow)
        self.assertIn("customer data can stay distributed", flow)
        self.assertIn("source-specific authority", flow)
        self.assertIn("still-unconfirmed replacement", flow)
        self.assertIn("approved local files", flow)

        for text in (flow, context):
            with self.subTest(source="flow" if text == flow else "context"):
                self.assertNotIn("salesforce_mcp_soql_query", text)
                self.assertNotIn("gmail_search_emails", text)
                self.assertNotIn("granola_get_meeting_transcript", text)

    def test_fragmented_customer_context_is_explained_without_requiring_centralization(
        self,
    ) -> None:
        context = (SKILL_DIRECTORY / "references" / "company-context.md").read_text(
            encoding="utf-8"
        )
        flow = (SKILL_DIRECTORY / "references" / "demo-flow.md").read_text(encoding="utf-8")
        skill = (SKILL_DIRECTORY / "SKILL.md").read_text(encoding="utf-8")

        self.assert_contains(
            context,
            "## How Fragmented Customer Context Is Handled",
            "**Assemble evidence in place:**",
            "**Match related records carefully:**",
            "**Respect source authority:**",
            "**Surface conflicts:**",
            "**Name coverage gaps:**",
            "**Support approved cleanup:**",
            "**Reuse workflow knowledge safely:**",
        )

        connector_branch = flow.split("### Branch: connector_explanation", maxsplit=1)[1]
        connector_branch = re.split(
            r"^### Branch:", connector_branch, maxsplit=1, flags=re.MULTILINE
        )[0]
        self.assertIn("customer data can stay distributed", connector_branch)
        self.assertIn("conflicting records", connector_branch)
        self.assertIn("incomplete connectivity", connector_branch)
        self.assertIn("Harbor's former sponsor", connector_branch)
        self.assertIn("human approval", connector_branch)
        self.assertIn("without implying data was centralized or rewritten", skill)

    def test_scripted_connector_activity_is_explicitly_fictional_and_complete(self) -> None:
        context = (SKILL_DIRECTORY / "references" / "company-context.md").read_text(
            encoding="utf-8"
        )
        flow = (SKILL_DIRECTORY / "references" / "demo-flow.md").read_text(encoding="utf-8")

        self.assertIn("## Illustrative Connector Summary", context)
        self.assertIn("fictional demo-display values, not actual tool calls", context)
        self.assertIn("no live systems are accessed", flow)
        for connector in (
            "CRM: Salesforce",
            "Call notes: Granola",
            "Email: Gmail",
            "Calendar: Google Calendar",
            "Internal communication: Slack",
            "Account documents: Google Drive",
        ):
            with self.subTest(connector=connector):
                self.assertIn(f"| {connector} |", context)
                self.assertIn(f"| {connector} |", flow)

    def test_connector_examples_have_specific_resource_types_and_dynamic_dates(self) -> None:
        flow = (SKILL_DIRECTORY / "references" / "demo-flow.md").read_text(encoding="utf-8")
        context = (SKILL_DIRECTORY / "references" / "company-context.md").read_text(
            encoding="utf-8"
        )
        skill = (SKILL_DIRECTORY / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("### Dynamic Demo Dates", context)
        self.assertIn("Resolve the dynamic date tokens", skill)
        self.assertIn("Never display unresolved placeholders", skill)
        for resource_label, token in (
            ("Opportunity: Northstar Health", "{{next_thursday}}"),
            ("Call: Northstar Health Expansion & Security Review", "{{two_business_days_ago}}"),
            ("Email: Re: Northstar Health deployment decision", "{{previous_business_day}}"),
            ("Event: Northstar Health Executive Deployment Decision", "{{next_thursday}}"),
            ("#acct-northstar-health", "{{today}}"),
            (
                "Northstar Health — Pilot Completion & Company-Wide Rollout Readiness",
                "{{previous_business_day}}",
            ),
        ):
            with self.subTest(resource=resource_label):
                self.assertIn(resource_label, flow)
                self.assertIn(token, flow)
                self.assertIn(resource_label, context)

        dated_sources = {
            "salesforce.md": "{{next_thursday}}",
            "granola.md": "{{two_business_days_ago}}",
            "gmail.md": "{{previous_business_day}}",
            "google-calendar.md": "{{next_thursday}}",
            "slack.md": "{{today}}",
            "google-drive.md": "{{previous_business_day}}",
        }
        for fixture_name, token in dated_sources.items():
            with self.subTest(source=fixture_name):
                source = (SKILL_DIRECTORY / "references" / "sources" / fixture_name).read_text(
                    encoding="utf-8"
                )
                self.assertIn(token, source)

    def test_reviewed_crm_and_email_paths_never_execute_without_explicit_approval(self) -> None:
        flow = (SKILL_DIRECTORY / "references" / "demo-flow.md").read_text(encoding="utf-8")
        skill = (SKILL_DIRECTORY / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("without creating, saving, or sending the email", flow)
        self.assertIn("if requested", flow)
        self.assertIn("a separate, explicit action-specific request and approval", flow)
        self.assertIn("No Salesforce records were changed", flow)
        self.assertIn("Save it to Salesforce", flow)
        self.assertIn("explicit", skill.lower())
        self.assertIn("Salesforce", skill)

    def test_renderer_creates_complete_standalone_dashboard(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_path = Path(temporary_directory) / "nested" / "account-priorities.html"
            dashboard_path = RENDERER.render_dashboard(self.portfolio, output_path=output_path)
            rendered = dashboard_path.read_text(encoding="utf-8")

        self.assertEqual(dashboard_path, output_path.resolve())
        self.assertNotIn(RENDERER.PLACEHOLDER, rendered)
        self.assertIn(self.portfolio["workNow"][0]["account"], rendered)
        self.assertIn(self.portfolio["watch"][0]["account"], rendered)
        self.assertIn(self.portfolio["source"]["label"], rendered)
        self.assertIn(self.portfolio["demo"]["disclaimer"], rendered)
        self.assertIn("Priority Rationale", rendered)
        self.assertIn("Riley’s Account Home", rendered)
        self.assertIn("ACCOUNT OVERVIEW", rendered)
        self.assertNotIn("Why this matters", rendered)
        self.assertNotIn("YOUR #1 PRIORITY", rendered)
        self.assertNotIn("QUESTIONS YOU CAN ASK", rendered)
        self.assertNotIn("YOUR NEXT BEST ACTION", rendered)
        self.assertNotIn('id="draft-backdrop"', rendered)
        self.assertNotIn('data-action="draft"', rendered)
        self.assertNotIn('id="launch-draft-button"', rendered)
        self.assertIn('<footer class="site-disclosure" id="site-disclosure"></footer>', rendered)
        self.assertIn('isFictionalDemo ? "Fictional data · For demonstration only."', rendered)
        self.assertNotIn('<span class="demo-badge">Fictional sample data</span>', rendered)
        self.assertNotIn("all six fictional connected sources", rendered)

    def test_seller_account_home_has_exactly_three_accessible_account_home_views(self) -> None:
        template = (
            SKILL_DIRECTORY / "assets" / "account-priority-workspace.template.html"
        ).read_text(encoding="utf-8")

        self.assertRegex(template, r'<(?:nav|div)\b[^>]*\brole="tablist"[^>]*>')
        self.assertEqual(
            re.findall(
                r'<button\b(?=[^>]*\brole="tab")[^>]*>\s*'
                r"(Home|Accounts|Pipeline)\s*</button>",
                template,
            ),
            ["Home", "Accounts", "Pipeline"],
        )
        self.assertEqual(len(re.findall(r'<button\b[^>]*\brole="tab"', template)), 3)

        for view_name, view_label in (
            ("home", "Home"),
            ("accounts", "Accounts"),
            ("pipeline", "Pipeline"),
        ):
            with self.subTest(view=view_name):
                selected = "true" if view_name == "home" else "false"
                tab_index = "0" if view_name == "home" else "-1"
                self.assertRegex(
                    template,
                    rf'<button\b(?=[^>]*\bid="tab-{view_name}")'
                    rf'(?=[^>]*\brole="tab")'
                    rf'(?=[^>]*\baria-controls="view-{view_name}")'
                    rf'(?=[^>]*\baria-selected="{selected}")'
                    rf'(?=[^>]*\btabindex="{tab_index}")'
                    rf"[^>]*>\s*{view_label}\s*</button>",
                )
                panel = re.search(
                    rf'<section\b(?=[^>]*\brole="tabpanel")'
                    rf'(?=[^>]*\bid="view-{view_name}")'
                    rf'(?=[^>]*\baria-labelledby="tab-{view_name}")'
                    rf"[^>]*>",
                    template,
                )
                self.assertIsNotNone(panel)
                if panel is not None:
                    self.assertEqual(
                        bool(re.search(r"\shidden(?:\s|>)", panel.group())), view_name != "home"
                    )

    def test_account_home_views_separate_daily_work_relationships_and_pipeline(self) -> None:
        template = (
            SKILL_DIRECTORY / "assets" / "account-priority-workspace.template.html"
        ).read_text(encoding="utf-8")
        panels = list(
            re.finditer(
                r'<section\b(?=[^>]*\brole="tabpanel")'
                r'(?=[^>]*\bid="view-(home|accounts|pipeline)")[^>]*>',
                template,
            )
        )
        self.assertEqual([panel.group(1) for panel in panels], ["home", "accounts", "pipeline"])
        panel_content = {
            panel.group(1): template[
                panel.end() : panels[index + 1].start()
                if index + 1 < len(panels)
                else len(template)
            ]
            for index, panel in enumerate(panels)
        }

        self.assert_contains(
            panel_content["home"],
            "Needs your attention",
            "Upcoming meetings",
            "Recent account activity",
            'id="attention-list"',
            'id="meeting-list"',
            'id="activity-list"',
            'id="book-value-metric"',
            'id="renewal-value-metric"',
            'id="expansion-value-metric"',
            'id="source-count-metric"',
        )

        self.assert_contains(
            panel_content["accounts"],
            "Your accounts",
            'class="account-table"',
            'id="accounts-list"',
            "Priority score",
            "Open items",
            "Suggested next action",
        )
        self.assertNotIn("#1", panel_content["accounts"])
        self.assertNotIn("Your priorities", panel_content["accounts"])

        self.assert_contains(
            panel_content["pipeline"],
            "Opportunity work queues",
            'id="opportunity-list"',
            "Pilot & rollout",
            "Security review",
            "Buyer & ownership",
            "Commercial alignment",
            "Renewal readiness",
            "On hold",
        )

        self.assert_excludes(
            panel_content["pipeline"],
            "Pipeline snapshot",
            'id="pipeline-value"',
            'id="pipeline-renewals"',
            'id="pipeline-expansion"',
            'id="pipeline-active"',
            'id="stage-breakdown"',
            'class="portfolio-health pipeline-metrics"',
        )

        self.assertRegex(
            panel_content["pipeline"],
            r'^\s*<section\b[^>]*\bclass="work-card pipeline-opportunities"',
        )

    def test_seller_view_tabs_switch_by_click_keyboard_and_open_account_details(self) -> None:
        template_path = SKILL_DIRECTORY / "assets" / "account-priority-workspace.template.html"
        interaction_check = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const template = fs.readFileSync(process.argv[1], 'utf8');

function bodyFor(name) {
  const match = template.match(new RegExp(
    'function ' + name + '\\([^)]*\\) \\{([\\s\\S]*?)\\n      \\}'
  ));
  assert.ok(match, 'The executable seller-home function ' + name + ' must exist');
  return match[1];
}

const elements = Object.fromEntries(
  ['home', 'accounts', 'pipeline'].flatMap(name => [
    ['tab-' + name, {
      attributes: {}, handlers: {}, tabIndex: name === 'home' ? 0 : -1, focused: 0,
      setAttribute(key, value) { this.attributes[key] = value; },
      addEventListener(event, handler) { this.handlers[event] = handler; },
      focus() { this.focused += 1; }
    }],
    ['view-' + name, {hidden: name !== 'home'}]
  ])
);
const document = {
  getElementById(id) {
    assert.ok(elements[id], 'Every selected seller view must resolve a real tab/panel: ' + id);
    return elements[id];
  }
};
const selectViewBody = new Function('name', 'focus', 'document', bodyFor('selectView'));
const selectView = (name, focus) => selectViewBody(name, focus, document);
const setupViews = new Function('document', 'selectView', bodyFor('setupViews'));
setupViews(document, selectView);

function assertSelected(active) {
  for (const candidate of ['home', 'accounts', 'pipeline']) {
    const selected = candidate === active;
    assert.equal(elements['tab-' + candidate].attributes['aria-selected'], String(selected));
    assert.equal(elements['tab-' + candidate].tabIndex, selected ? 0 : -1);
    assert.equal(elements['view-' + candidate].hidden, !selected);
  }
}

elements['tab-accounts'].handlers.click();
assertSelected('accounts');
elements['tab-pipeline'].handlers.click();
assertSelected('pipeline');

function press(tab, key, expected) {
  let prevented = false;
  elements['tab-' + tab].handlers.keydown({key, preventDefault() { prevented = true; }});
  assert.equal(prevented, true, key + ' must consume standard tab-list navigation');
  assertSelected(expected);
  assert.ok(elements['tab-' + expected].focused, key + ' must focus the selected tab');
}

press('pipeline', 'ArrowRight', 'home');
press('home', 'ArrowLeft', 'pipeline');
press('pipeline', 'Home', 'home');
press('home', 'End', 'pipeline');

const opened = [];
function create(tag, className, content) {
  return {
    tag, className, content, attributes: {}, handlers: {}, children: [],
    setAttribute(key, value) { this.attributes[key] = value; },
    addEventListener(event, handler) { this.handlers[event] = handler; },
    append(...children) { this.children.push(...children); }
  };
}
const openAccountDrawer = (account, trigger) => opened.push({account, trigger});
const accountButton = new Function(
  'account', 'title', 'detail', 'meta', 'value', 'create', 'openAccountDrawer',
  bodyFor('accountButton')
);
const account = {account: 'Northstar Health'};
const workItem = accountButton(
  account, account.account, 'Review the customer request', 'Today', '', create, openAccountDrawer
);
assert.equal(workItem.attributes['aria-haspopup'], 'dialog');
assert.equal(workItem.attributes['aria-controls'], 'account-drawer');
workItem.handlers.click();
assert.deepEqual(opened, [{account, trigger: workItem}]);
"""

        self.assert_node_script(interaction_check, str(template_path))

    def test_accounts_sort_grounded_priority_scores_and_expose_the_real_next_action(self) -> None:
        template_path = SKILL_DIRECTORY / "assets" / "account-priority-workspace.template.html"
        template = template_path.read_text(encoding="utf-8")

        self.assertRegex(
            template,
            r'<th\b(?=[^>]*\bid="priority-column")'
            r'(?=[^>]*\baria-sort="descending")[^>]*>'
            r'[\s\S]*?<button\b(?=[^>]*\bid="priority-sort")[^>]*>'
            r"\s*Priority score",
        )
        self.assertIn("row.dataset.priorityScore = score == null", template)
        self.assertIn('score == null ? "—" : String(score)', template)
        self.assertIn("sortedAccounts().forEach((account)", template)
        self.assertIn("suggestedNextAction(account)", template)
        self.assertNotIn("meeting-prep", template)

        priority_check = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const template = fs.readFileSync(process.argv[1], 'utf8');
const portfolio = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));

function bodyFor(name) {
  const match = template.match(new RegExp(
    'function ' + name + '\\([^)]*\\) \\{([\\s\\S]*?)\\n      \\}'
  ));
  assert.ok(match, 'The source-grounded account helper ' + name + ' must exist');
  return match[1];
}

const text = (value, fallback) => value == null || value === '' ? fallback || '' : String(value);
const detailFor = row => portfolio.accountDetails[row.account] || {};
const scoreFor = new Function('row', 'detailFor', bodyFor('priorityScore'));
const priorityScore = row => scoreFor(row, detailFor);
const actualRows = [...portfolio.workNow, ...portfolio.watch, ...portfolio.paused];
const northstar = actualRows.find(row => row.account === 'Northstar Health');

assert.equal(priorityScore(northstar), 98);
assert.equal(priorityScore({...northstar, priorityScore: 76}), 76,
  'An explicitly supplied row score takes precedence over account-detail data');
assert.equal(priorityScore({account: 'Northstar Health'}), 98,
  'An explicitly supplied account-detail score remains a valid fallback');
for (const row of [
  {account: 'Actual Customer', confidence: 'High', rank: 1},
  {account: 'Actual Customer', priorityScore: ''},
  {account: 'Actual Customer', priorityScore: -1},
  {account: 'Actual Customer', priorityScore: 101},
  {account: 'Actual Customer', priorityScore: 'not-a-score'}
]) {
  assert.equal(priorityScore(row), null,
    'Real customer accounts without a valid sourced score must not receive a fabricated score');
}

const unknown = {account: 'Actual Customer', rank: 0, confidence: 'High'};
const allRows = [...actualRows].reverse().concat(unknown);
const state = {sortDescending: true};
const sorted = new Function('allRows', 'priorityScore', 'state', bodyFor('sortedAccounts'));
let arranged = sorted(allRows, priorityScore, state);
assert.deepEqual(arranged.map(priorityScore), [98, 93, 89, 84, 78, 71, 66, 59, 42, 34, null]);
state.sortDescending = false;
arranged = sorted(allRows, priorityScore, state);
assert.deepEqual(arranged.map(priorityScore), [34, 42, 59, 66, 71, 78, 84, 89, 93, 98, null]);

const suggestedNextAction = new Function('row', 'text', bodyFor('suggestedNextAction'));
assert.equal(suggestedNextAction(northstar, text),
  'Review your pilot scorecard and the uptime concern with Jordan Lee, Casey Patel, and Priya Shah.');
assert.equal(suggestedNextAction({account: 'Actual Customer'}, text),
  'Review verified account context');

const button = {
  handlers: {}, indicator: {textContent: ''},
  addEventListener(event, callback) { this.handlers[event] = callback; },
  querySelector(selector) { assert.equal(selector, '.sort-indicator'); return this.indicator; }
};
const column = {attributes: {}, setAttribute(name, value) { this.attributes[name] = value; }};
const document = {
  getElementById(id) {
    return id === 'priority-sort' ? button : id === 'priority-column' ? column : null;
  }
};
state.sortDescending = true;
let rerendered = 0;
const setupAccountSorting = new Function(
  'document', 'state', 'renderAccounts', bodyFor('setupAccountSorting')
);
setupAccountSorting(document, state, () => { rerendered += 1; });
button.handlers.click();
assert.equal(state.sortDescending, false);
assert.equal(column.attributes['aria-sort'], 'ascending');
assert.equal(button.indicator.textContent, '↑');
assert.equal(rerendered, 1);
button.handlers.click();
assert.equal(state.sortDescending, true);
assert.equal(column.attributes['aria-sort'], 'descending');
assert.equal(button.indicator.textContent, '↓');
assert.equal(rerendered, 2);
"""

        self.assert_node_script(
            priority_check,
            str(template_path),
            str(SKILL_DIRECTORY / "references" / "demo-portfolio.json"),
        )

    def test_seller_account_home_uses_complete_book_and_dynamic_verified_source_metadata(
        self,
    ) -> None:
        template = (
            SKILL_DIRECTORY / "assets" / "account-priority-workspace.template.html"
        ).read_text(encoding="utf-8")

        self.assertRegex(
            template,
            r"const state = \{ selected: allRows\[0\] \|\| null, (?:modalOpen|drawerOpen): false",
        )
        self.assertIn('<table class="account-table"', template)
        self.assertIn('<tbody id="accounts-list"></tbody>', template)
        self.assertIn('const row = create("tr", "account-row")', template)
        self.assertIn('row.addEventListener("click", select)', template)
        table_headers = [
            re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", header)).strip()
            for header in re.findall(r"<th\b[^>]*>([\s\S]*?)</th>", template)
        ]
        for table_column in (
            "Customer",
            "Opportunity",
            "Status",
            "Priority score",
            "Open items",
            "Suggested next action",
        ):
            with self.subTest(table_column=table_column):
                self.assertTrue(
                    any(
                        header == table_column or header.startswith(f"{table_column} ")
                        for header in table_headers
                    ),
                    f"Missing seller account column {table_column!r}: {table_headers}",
                )
        self.assertNotIn("prioritized customer accounts", template.lower())
        self.assert_excludes(
            template,
            'id="sort-select"',
            'id="filter-stack"',
            'id="sources-button"',
            'class="sidebar"',
            "pin-button",
        )
        self.assertIn('id="book-value-metric"', template)
        self.assertIn('id="renewal-value-metric"', template)
        self.assertIn('id="expansion-value-metric"', template)
        self.assertIn('id="source-count-metric"', template)
        self.assertIn("payload.connectedSources", template)
        self.assertIn("payload.scope?.sourcesChecked", template)
        self.assertIn("source.verified !== false", template)
        self.assertIn("if(!isFictionalDemo)return [];", template)
        self.assertNotIn('name:"Priya Shah"', template)
        self.assertIn("Pilot success and uptime feedback remain unresolved", template)
        self.assertIn("Context and Next Steps", template)
        self.assertIn('label: "Needs attention"', template)
        self.assertNotIn('label: "Needs review"', template)
        self.assertNotIn("Evidence and account context", template)
        self.assertIn('isFictionalDemo ? "Fictional data · For demonstration only."', template)

    def test_demo_source_labels_distinguish_sample_data_from_live_connections(self) -> None:
        template = (
            SKILL_DIRECTORY / "assets" / "account-priority-workspace.template.html"
        ).read_text(encoding="utf-8")

        self.assertIn('isFictionalDemo ? "sample source" : "verified source"', template)
        self.assertIn('isFictionalDemo ? "Demo · " : ""', template)
        self.assertIn('isFictionalDemo ? "Sample context" : "Connected context"', template)
        self.assertIn('isFictionalDemo ? "Fictional account evidence"', template)
        self.assertIn(".header-context.is-demo .connection-dot", template)
        self.assertNotIn('"Verified customer conversations"', template)
        self.assertNotIn('"Verified customer evidence"', template)

    def test_recent_account_activity_is_current_and_spans_distinct_accounts(self) -> None:
        template_path = SKILL_DIRECTORY / "assets" / "account-priority-workspace.template.html"

        activity_check = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const template = fs.readFileSync(process.argv[1], 'utf8');
const match = template.match(
  /function recentAccountActivity\(rows\) \{([\s\S]*?)\n      \}/
);
assert.ok(match, 'The recent-account activity helper must exist');
const text = (value, fallback) => value == null || value === '' ? fallback || '' : String(value);
const verifiedAccountEvents = row => row.events;
const meetingTiming = event => /calendar/i.test(event.source) ? 'upcoming' : 'not-calendar';
const recentAccountActivity = new Function(
  'rows', 'verifiedAccountEvents', 'text', 'isFictionalDemo', 'meetingTiming', match[1]
);
const event = (source, hour) => ({source, when: `Aug 5, 2026 · ${hour}:00 AM`});
const rows = [
  {account: 'Alpha', events: [event('Google Calendar', 11), event('Gmail', 8), event('Slack', 7)]},
  {account: 'Beta', events: [event('Slack', 9)]},
  {account: 'Gamma', events: [event('Gmail', 10)]},
  {account: 'Delta', events: [event('Salesforce', 11)]},
  {account: 'Epsilon', events: [event('Slack', 7)]},
];
const activity = recentAccountActivity(rows, verifiedAccountEvents, text, true, meetingTiming);
assert.deepEqual(activity.map(item => item.row.account), ['Delta', 'Gamma', 'Beta', 'Alpha'],
  'Recent activity should show the latest real updates across four distinct accounts');
assert.ok(activity.every(item => item.event.source !== 'Google Calendar'),
  'A future calendar invitation is not recent account activity');
"""

        self.assert_node_script(activity_check, str(template_path))

    def test_seller_account_table_opens_shared_accessible_right_side_account_drawer(
        self,
    ) -> None:
        template = (
            SKILL_DIRECTORY / "assets" / "account-priority-workspace.template.html"
        ).read_text(encoding="utf-8")

        self.assertRegex(template, r"\.seller-workspace\s*\{\s*display:\s*block;\s*width:\s*100%;")
        self.assert_shared_accessible_account_drawer(template, detail_id="detail-panel")
        self.assertNotIn('class="account-modal"', template)
        self.assert_contains(
            template,
            'row.setAttribute("aria-controls", "account-drawer")',
            'row.setAttribute("aria-haspopup", "dialog")',
            "const select = () => openAccountDrawer(account, row)",
            "if (event.target === drawer) closeAccountDrawer()",
            'row.addEventListener("keydown"',
            "Context and Next Steps",
            "Priority Rationale",
            "Meetings",
            "Recent Communications",
            "flaggedIssue(account)",
        )
        self.assert_excludes(
            template,
            "Customer context",
            "Why this matters",
            "What needs doing",
            "Buying team",
            "Evidence and account context",
        )
        drawer_sections = (
            'appendSection(overview, "Context and Next Steps")',
            'appendSection(overview, "Priority Rationale")',
            'appendSection(overview, "Meetings")',
            'appendSection(overview, "Recent Communications")',
        )
        positions = [template.index(section) for section in drawer_sections]
        self.assertEqual(positions, sorted(positions))
        self.assertIn('create("p", "next-step-takeaway", suggestedNextAction(row))', template)
        self.assertIn(".stage-column, .issue-column, .stage-cell { display: none; }", template)
        self.assertIn(".mobile-stage { display: block; }", template)
        self.assertIn(".account-table colgroup { display: none; }", template)
        self.assertIn(".account-table thead tr, .account-row { display: grid;", template)
        self.assertIn(".account-row .stage-cell { display: none; }", template)
        self.assertIn(".issue-cell { grid-column: 1 / -1; display: block;", template)

    def test_demo_calendar_meetings_are_two_viewer_local_business_days_away(self) -> None:
        template_path = SKILL_DIRECTORY / "assets" / "account-priority-workspace.template.html"
        template = template_path.read_text(encoding="utf-8")

        self.assertIn("function meetingWhen(event, now)", template)
        self.assertGreaterEqual(template.count("meetingWhen(event)"), 2)
        self.assertIn("function recentAccountActivity(rows)", template)
        self.assertIn(
            ".filter((event) => !/^(?:google|outlook) calendar$/i.test(text(event.source))",
            template,
        )
        self.assertIn('(!isFictionalDemo && meetingTiming(event) === "past")', template)
        self.assertIn("!isFictionalDemo || !original", template)
        northstar = self.portfolio["workNow"][0]
        self.assertEqual(northstar["account"], "Northstar Health")
        self.assertEqual(northstar["dueDate"], "Before customer review")
        self.assertNotRegex(
            " ".join(self.portfolio["accountDetails"]["Northstar Health"]["rationale"]),
            r"\b(?:Monday|Tuesday|Wednesday|Thursday|Friday)\b|\{\{next_thursday\}\}",
            "A rolling meeting must not appear after a contradictory hard-coded decision date.",
        )
        for account, details in self.portfolio["accountDetails"].items():
            for event in details.get("events", []):
                if event.get("source") == "Google Calendar":
                    with self.subTest(account=account):
                        self.assertNotRegex(
                            event["title"],
                            r"\b(?:Monday|Tuesday|Wednesday|Thursday|Friday)\b",
                            "Relative meeting titles must not contradict viewer-local dates.",
                        )

        meeting_check = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const template = fs.readFileSync(process.argv[1], 'utf8');
const match = template.match(
  /function meetingWhen\(event, now\) \{([\s\S]*?)\n      \}/
);
assert.ok(match, 'The viewer-local meeting date helper must exist');
const text = (value, fallback) => value == null || value === '' ? fallback || '' : String(value);
const meetingWhen = new Function('event', 'now', 'isFictionalDemo', 'text', match[1]);
const event = {when: 'Thu, Aug 6 · 11:00 AM'};

assert.equal(meetingWhen(event, new Date(2026, 7, 3, 23, 30), true, text),
  'Wed, Aug 5 · 11:00 AM', 'Monday viewers should see Wednesday in their local timezone');
assert.equal(meetingWhen(event, new Date(2026, 7, 5, 23, 30), true, text),
  'Fri, Aug 7 · 11:00 AM', 'Wednesday viewers should see Friday');
assert.equal(meetingWhen(event, new Date(2026, 7, 6, 23, 30), true, text),
  'Mon, Aug 10 · 11:00 AM', 'Thursday viewers must skip the weekend');
assert.equal(meetingWhen(event, new Date(2026, 7, 7, 23, 30), true, text),
  'Tue, Aug 11 · 11:00 AM', 'Friday viewers must skip Saturday and Sunday');
assert.equal(meetingWhen(event, new Date(2026, 7, 8, 23, 30), true, text),
  'Tue, Aug 11 · 11:00 AM', 'Weekend viewers should count Monday as the first business day');
assert.equal(meetingWhen({when: 'Monday · 14:30'}, new Date(2026, 7, 7), true, text),
  'Tue, Aug 11 · 14:30', 'The original 24-hour meeting time must remain unchanged');
assert.equal(meetingWhen(event, new Date(2026, 7, 7), false, text), event.when,
  'Real customer calendar dates must never be rewritten');
assert.equal(meetingWhen({when: ''}, new Date(2026, 7, 7), true, text), '',
  'An absent meeting timestamp cannot be fabricated');
"""

        self.assert_node_script(meeting_check, str(template_path))

    def test_account_detail_separates_verified_meetings_and_customer_communications(self) -> None:
        template_path = SKILL_DIRECTORY / "assets" / "account-priority-workspace.template.html"
        template = template_path.read_text(encoding="utf-8")

        self.assertIn('appendSection(overview, "Meetings")', template)
        self.assertIn('appendSection(overview, "Recent Communications")', template)
        self.assertIn('"Email"', template)
        self.assertIn('"Slack"', template)
        self.assertIn('return "Unresolved"', template)
        self.assertIn('return "Replied"', template)
        self.assertIn('return "Update"', template)
        self.assertIn("event.replyStatus", template)

        communication_check = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const template = fs.readFileSync(process.argv[1], 'utf8');
const portfolio = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));

function bodyFor(name) {
  const match = template.match(new RegExp(
    'function ' + name + '\\([^)]*\\) \\{([\\s\\S]*?)\\n      \\}'
  ));
  assert.ok(match, 'The evidence-safe account helper ' + name + ' must exist');
  return match[1];
}

const text = (value, fallback) => value == null || value === '' ? fallback || '' : String(value);
const communicationStatus = new Function('event', 'text', bodyFor('communicationStatus'));
const events = portfolio.accountDetails['Northstar Health'].events;
const email = events.find(event => event.source === 'Gmail');
const customerSlack = events.find(event =>
  event.source === 'Slack' && event.reference.includes('#ext-northstar-health')
);
assert.equal(communicationStatus(email, text), 'Unresolved');
assert.equal(communicationStatus(customerSlack, text), 'Replied');
assert.equal(communicationStatus({source: 'Gmail', title: 'Customer requested pricing'}, text),
  'Update', 'A generic request without sourced response-state evidence must remain neutral');
assert.equal(communicationStatus({source: 'Slack', title: 'Customer shared a question'}, text),
  'Update', 'A message without sourced reply-state evidence must never be marked replied');
const userOpsMessage = events.find(event =>
  event.source === 'Slack' && event.reference.includes('#userops-enterprise-rollouts')
);
assert.ok(userOpsMessage, 'The actual Northstar UserOps evidence must exist');
assert.equal(userOpsMessage.replyStatus, undefined);
assert.match(userOpsMessage.title + ' ' + userOpsMessage.detail, /resolved/i);
assert.equal(communicationStatus(userOpsMessage, text), 'Update',
  'Future-tense UserOps language about work that needs to be resolved is not a customer reply');
for (const misleadingText of [
  'The uptime feedback needs to be resolved before rollout planning',
  'The question must be answered before the customer review',
  'The buyer remains unresolved until the next check-in',
  'The message was replied to according to an unverified free-text note'
]) {
  assert.equal(communicationStatus({source: 'Slack', title: misleadingText}, text), 'Update',
    'Free-text wording without explicit response metadata must never manufacture a reply state');
}
assert.equal(communicationStatus({source: 'Slack', responseStatus: 'Replied'}, text), 'Replied');
assert.equal(communicationStatus({source: 'Gmail', status: 'Unresolved'}, text), 'Unresolved');

const sources = [
  {name: 'Google Calendar'}, {name: 'Gmail'}, {name: 'Slack'}, {name: 'Salesforce'}
];
const detailEvents = row => row.events || portfolio.accountDetails[row.account]?.events || [];
const collectEvents = new Function('row', 'detailEvents', 'sources', 'text',
  bodyFor('verifiedAccountEvents'));
const verifiedAccountEvents = row => collectEvents(row, detailEvents, sources, text);
const classifyMeeting = new Function(
  'event', 'now', 'text', 'isFictionalDemo', bodyFor('meetingTiming')
);
const meetingTiming = event => classifyMeeting(event, undefined, text, true);
const collectMeetings = new Function('row', 'verifiedAccountEvents', 'meetingTiming',
  bodyFor('verifiedMeetingEvents'));
const northstar = portfolio.workNow[0];
const upcoming = collectMeetings(northstar, verifiedAccountEvents, meetingTiming);
assert.equal(upcoming.length, 1);
assert.equal(upcoming[0].source, 'Google Calendar');
assert.match(upcoming[0].title + ' ' + upcoming[0].detail, /pilot/i);
assert.match(upcoming[0].title + ' ' + upcoming[0].detail, /uptime/i);
assert.match(upcoming[0].title + ' ' + upcoming[0].detail, /decision/i);

const unrelated = {
  account: 'Actual Customer',
  events: [
    {source: 'Granola', title: 'Upcoming meeting and future deployment review'},
    {source: 'Unverified Calendar', title: 'Upcoming customer meeting'},
    {source: 'Slack', title: 'Schedule the customer meeting'}
  ]
};
assert.deepEqual(collectMeetings(unrelated, verifiedAccountEvents, meetingTiming), [],
  'Historical notes, message text, and unverified calendars cannot create upcoming meetings');
assert.deepEqual(verifiedAccountEvents({account: 'Actual Customer'}), [],
  'Real accounts without supplied event evidence cannot manufacture meetings or communications');

const detailFor = row => portfolio.accountDetails[row.account] || {};
const groups = {workNow: portfolio.workNow};
const explicitStatus = event => communicationStatus(event, text);
const countOpenItems = new Function(
  'row', 'detailFor', 'verifiedAccountEvents', 'communicationStatus', 'groups', 'text',
  'isFictionalDemo',
  bodyFor('openItemsFor')
);
const openItemsFor = row => countOpenItems(
  row, detailFor, verifiedAccountEvents, explicitStatus, groups, text, true
);
assert.equal(openItemsFor(northstar), 3,
  'Northstar retains its three explicitly documented source-backed account tasks');
const internalOnly = {
  account: 'Actual Customer',
  events: [
    {
      source: 'Slack',
      reference: '#userops-enterprise-rollouts',
      title: 'UserOps needs the uptime feedback resolved before rollout planning'
    },
    {
      source: 'Slack',
      reference: '#acct-actual-customer',
      title: 'The open customer question needs to be answered'
    }
  ]
};
assert.equal(openItemsFor(internalOnly), 0,
  'Unsupplied future-tense internal messages cannot become customer reply-needed items');
const repliedOnly = {
  account: 'Actual Customer',
  events: [{source: 'Slack', reference: '#ext-actual-customer', replyStatus: 'Replied'}]
};
assert.equal(openItemsFor(repliedOnly), 0,
  'An explicitly replied customer communication is no longer an unanswered open item');
const unansweredCustomer = {
  account: 'Actual Customer',
  events: [{source: 'Gmail', title: 'Customer request', replyStatus: 'Unresolved'}]
};
assert.equal(openItemsFor(unansweredCustomer), 1,
  'An explicitly unresolved verified customer communication remains actionable');
assert.equal(openItemsFor({account: 'Actual Customer', openItems: ['Prepare deck', 'Review notes']}),
  2, 'Explicitly supplied account tasks remain legitimate open work');
"""

        self.assert_node_script(
            communication_check,
            str(template_path),
            str(SKILL_DIRECTORY / "references" / "demo-portfolio.json"),
        )

    def test_account_drawer_animation_is_smooth_and_respects_reduced_motion(self) -> None:
        template = (
            SKILL_DIRECTORY / "assets" / "account-priority-workspace.template.html"
        ).read_text(encoding="utf-8")

        self.assertRegex(template, r"\.account-drawer\s*\{[^}]*animation:\s*drawer-backdrop-in")
        self.assertRegex(template, r"\.account-drawer-panel\s*\{[^}]*animation:\s*drawer-slide-in")
        self.assertRegex(template, r"\.account-drawer-panel\s*\{[^}]*transition:\s*transform")
        self.assertRegex(template, r"@keyframes\s+drawer-slide-in\s*\{[\s\S]*?translateX")
        self.assertRegex(
            template,
            r"@media\s*\(prefers-reduced-motion:\s*reduce\)\s*\{[\s\S]*?"
            r"\.account-drawer,\s*\.account-drawer-panel\s*\{[^}]*"
            r"animation:\s*none\s*!important;[^}]*transition:\s*none\s*!important;",
        )

    def test_northstar_account_context_tees_up_pilot_readiness_and_uptime_validation(
        self,
    ) -> None:
        template = (
            SKILL_DIRECTORY / "assets" / "account-priority-workspace.template.html"
        ).read_text(encoding="utf-8")
        northstar = self.portfolio["accountDetails"]["Northstar Health"]
        seller_account = self.portfolio["workNow"][0]

        self.assertIn(
            'groups.workNow.includes(row) ? "NEEDS ATTENTION" : "ACCOUNT OVERVIEW"', template
        )
        self.assertNotIn("#1 priority", template.lower())
        self.assertNotIn("YOUR #1 PRIORITY · CUSTOMER BLOCKER", template)
        self.assertIn("Context and Next Steps", template)
        self.assertIn("Priority Rationale", template)
        self.assertNotIn("Customer context", template)
        self.assertNotIn("ACCOUNT CONTEXT", template)
        self.assertEqual(self.portfolio["recentLaunch"]["targetAccount"], "Northstar Health")
        self.assertEqual(self.portfolio["recentLaunch"]["targetContact"], "Jordan Lee")

        priority_text = " ".join(
            [
                northstar["strategy"],
                northstar["risk"],
                *northstar["rationale"],
                seller_account["whyItMatters"],
                seller_account["nextAction"],
                northstar["draft"]["body"],
            ]
        ).lower()
        self.assert_contains(
            priority_text,
            "jordan lee",
            "casey patel",
            "priya",
            "pilot",
            "uptime",
            "engagement",
            "repeat usage",
            "deployment",
            "audit",
            "retention",
        )

        self.assertEqual(northstar["draft"]["to"], "Jordan Lee")
        self.assertIn("pilot", northstar["draft"]["subject"].lower())
        self.assertIn("uptime", northstar["draft"]["subject"].lower())

    def test_seller_and_executive_dashboards_share_one_restrained_visual_design_language(
        self,
    ) -> None:
        seller_template = (
            SKILL_DIRECTORY / "assets" / "account-priority-workspace.template.html"
        ).read_text(encoding="utf-8")
        executive_template = (
            SKILL_DIRECTORY / "assets" / "sales-leadership-dashboard.template.html"
        ).read_text(encoding="utf-8")

        for token in (
            "--canvas: #f6f6f6",
            "--surface: #ffffff",
            "--ink: #171717",
            "--muted: #626262",
            "--line: #d2d2d2",
            "--green: #00a240",
            "--accent: #171717",
            "--page-width: 1320px",
            '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
        ):
            with self.subTest(token=token):
                self.assertIn(token, seller_template)
                self.assertIn(token, executive_template)

        for legacy_token in ("--canvas: #f7f6f2", "--green: #147457"):
            with self.subTest(legacy_token=legacy_token):
                self.assertNotIn(legacy_token, seller_template)
                self.assertNotIn(legacy_token, executive_template)

    def test_seller_and_leadership_dashboards_use_legible_operational_typography(self) -> None:
        dashboards = (
            (
                "seller",
                "account-priority-workspace.template.html",
                {
                    ".workspace-tab": 14,
                    ".account-table th": 12,
                    ".account-name": 14,
                    ".work-card-header h2": 18,
                    ".detail-copy": 13,
                    ".signal-source": 12,
                },
            ),
            (
                "leadership",
                "sales-leadership-dashboard.template.html",
                {
                    ".navigation a": 14,
                    ".account-list-header": 12,
                    ".account-name": 14,
                    ".drawer-title": 14,
                    ".detail-list li": 13,
                    ".subheading h3": 18,
                },
            ),
        )

        for dashboard_name, template_name, meaningful_selectors in dashboards:
            with self.subTest(dashboard=dashboard_name):
                template = (SKILL_DIRECTORY / "assets" / template_name).read_text(encoding="utf-8")
                stylesheet = re.search(r"<style>([\s\S]*?)</style>", template)
                self.assertIsNotNone(stylesheet)
                if stylesheet is None:
                    continue

                styles = stylesheet.group(1)
                body_font = re.search(
                    r"\bbody\s*\{[^}]*\bfont:\s*(\d+(?:\.\d+)?)px\s*/\s*(\d+(?:\.\d+)?)",
                    styles,
                )
                self.assertIsNotNone(body_font)
                if body_font is not None:
                    self.assertGreaterEqual(float(body_font.group(1)), 15)
                    self.assertGreaterEqual(float(body_font.group(2)), 1.4)

                tiny_type = re.findall(r"\bfont-size:\s*(\d+(?:\.\d+)?)px\b", styles)
                self.assertTrue(tiny_type)
                self.assertGreaterEqual(min(map(float, tiny_type)), 12)

                for selector, minimum_size in meaningful_selectors.items():
                    with self.subTest(dashboard=dashboard_name, selector=selector):
                        font_size = re.search(
                            rf"{re.escape(selector)}\s*\{{[^}}]*\bfont-size:\s*"
                            r"(\d+(?:\.\d+)?)px\b",
                            styles,
                        )
                        self.assertIsNotNone(font_size)
                        if font_size is not None:
                            self.assertGreaterEqual(float(font_size.group(1)), minimum_size)

    def test_seller_and_executive_dashboards_are_owned_by_the_same_portable_skill(self) -> None:
        skill = (SKILL_DIRECTORY / "SKILL.md").read_text(encoding="utf-8")
        skill_metadata = (SKILL_DIRECTORY / "agents" / "openai.yaml").read_text(encoding="utf-8")
        launcher = (SKILL_DIRECTORY / "scripts" / "start_demo_fast.py").read_text(encoding="utf-8")

        self.assertIn("name: demo-exec-and-seller-dash", skill)
        self.assertIn(
            'description: "Use only when the user explicitly requests a fictional, '
            "connector-free Sales demo or walkthrough",
            skill,
        )
        self.assertIn("Never select it for ordinary real seller", skill)
        self.assertIn("explicitly opts out of shared instructions and dependencies", skill)
        self.assertIn('display_name: "Executive and Seller Dashboard Demo"', skill_metadata)
        self.assertIn(
            'short_description: "Preview executive dashboards, seller work, and meeting follow-up"',
            skill_metadata,
        )
        self.assertIn("allow_implicit_invocation: false", skill_metadata)
        self.assertNotIn("account prioritization", skill_metadata.lower())
        self.assertEqual(RENDERER.DEFAULT_TEMPLATE.parent, SKILL_DIRECTORY / "assets")
        self.assertEqual(RENDERER.DEFAULT_LEADERSHIP_TEMPLATE.parent, SKILL_DIRECTORY / "assets")
        self.assertEqual(RENDERER.DEFAULT_PORTFOLIO.parent, SKILL_DIRECTORY / "references")
        self.assertEqual(RENDERER.DEFAULT_LEADERSHIP.parent, SKILL_DIRECTORY / "references")
        self.assertIn("account-priority-workspace.template.html", skill)
        self.assertIn("sales-leadership-dashboard.template.html", skill)
        self.assertIn("render_demo_dashboard.py", launcher)

        for markdown_file in SKILL_DIRECTORY.rglob("*.md"):
            with self.subTest(markdown_file=markdown_file.relative_to(SKILL_DIRECTORY)):
                content = markdown_file.read_text(encoding="utf-8")
                self.assertNotRegex(
                    content,
                    r"(?:\.\./){2}(?:dependencies\.md|shared_skill_instructions\.md)",
                )
                self.assertNotIn("../index/SKILL.md", content)

    def test_real_dashboards_have_distinct_grounded_persona_owners(self) -> None:
        production_skill = (
            SKILL_DIRECTORY.parent / "seller-account-dashboard" / "SKILL.md"
        ).read_text(encoding="utf-8")
        leadership_skill = (
            SKILL_DIRECTORY.parent / "sales-leadership-dashboard" / "SKILL.md"
        ).read_text(encoding="utf-8")
        lifecycle = (
            SKILL_DIRECTORY.parent.parent / "references" / "dashboard-lifecycle.md"
        ).read_text(encoding="utf-8")
        sales_index = (SKILL_DIRECTORY.parent / "index" / "SKILL.md").read_text(encoding="utf-8")

        home_heading = "## Real Account Canvas"
        focused_heading = "## Explicit Account Ranking"
        self.assertLess(
            production_skill.index(home_heading), production_skill.index(focused_heading)
        )
        self.assert_contains(
            production_skill,
            "**Home**, **Accounts**, and **Pipeline**",
            "requested additional sections",
            "../demo-exec-and-seller-dash/assets/account-priority-workspace.template.html",
            "complete owned-account universe",
            "every owned account exactly once",
            "suppression and fallbacks",
            "**Suggested Focus**, **Monitor**, or **Suppress Or Block**",
            "weekly read-only rerun",
            "Never use the fictional demo renderer",
            "explicit account prioritization",
        )
        self.assertIn("name: sales-leadership-dashboard", leadership_skill)
        self.assertIn(
            "**Forecast & key metrics**, **Account Focus**, and **Team Focus**", leadership_skill
        )
        self.assertIn("verified: true", leadership_skill)
        self.assertIn("Ordinary forecast analysis remains with `review-forecast`", leadership_skill)
        for skill in (production_skill, leadership_skill):
            self.assert_contains(
                skill,
                "[the shared Sales skill instructions](../../shared_skill_instructions.md)",
                "[shared dashboard lifecycle](../../references/dashboard-lifecycle.md)",
                "../../scripts/render_real_dashboard.py",
                "user explicitly agrees",
            )
        self.assert_contains(
            lifecycle,
            "local-first preference overrides",
            "exactly one verified match on owner, persona, and account/team scope",
            "Preserve that dashboard's URL, project identity, source, and customizations",
        )
        self.assertIn("Select the best focused owner based on those descriptions", sales_index)
        self.assertNotIn("prioritize-accounts", sales_index)
        self.assertNotIn("seller-account-dashboard", sales_index)
        self.assertNotIn("sales-leadership-dashboard", sales_index)
        self.assertNotIn("demo-exec-and-seller-dash", sales_index)
        self.assertNotIn("prepare-for-meeting", sales_index)

    def test_shared_seller_template_has_no_fictional_initial_shell(self) -> None:
        template = RENDERER.DEFAULT_TEMPLATE.read_text(encoding="utf-8")

        self.assertIn("<title>Seller Account Home</title>", template)
        self.assertNotIn("Riley Morgan", template)
        self.assertNotIn("Riley’s Account Home", template)
        self.assertNotIn("Meridian Cloud", template)
        self.assertNotIn('id="book-value-metric">10<', template)
        self.assertNotIn('id="renewal-value-metric">5<', template)
        self.assertNotIn('id="source-count-metric">6 sources<', template)
        self.assertNotIn("10 accounts · 3 need attention", template)

    def test_every_northstar_deck_link_uses_the_actual_twelve_slide_presentation(self) -> None:
        deck_surfaces = (
            SKILL_DIRECTORY / "SKILL.md",
            SKILL_DIRECTORY / "references" / "demo-flow.md",
            SKILL_DIRECTORY / "references" / "northstar-presentation-brief.md",
            SKILL_DIRECTORY / "references" / "company-context.md",
            SKILL_DIRECTORY / "references" / "sources" / "google-drive.md",
            SKILL_DIRECTORY / "references" / "demo-portfolio.json",
            SKILL_DIRECTORY / "references" / "demo-leadership.json",
        )

        for deck_surface in deck_surfaces:
            with self.subTest(deck_surface=deck_surface.relative_to(SKILL_DIRECTORY)):
                content = deck_surface.read_text(encoding="utf-8")
                self.assertIn(CANONICAL_NORTHSTAR_TEMPLATE_URL, content)
                presentation_urls = {
                    url.rstrip(".")
                    for url in re.findall(
                        r'https://docs\.google\.com/presentation/d/[^\s)"`]+', content
                    )
                }
                self.assertEqual(presentation_urls, {CANONICAL_NORTHSTAR_TEMPLATE_URL})
                self.assertNotIn("1WEQVS8-UQ1_KmKogHLPmLPjD2OkymLhAx5lkMwZrQBk", content)

    def test_fictional_buyer_names_avoid_accidental_celebrity_collisions(self) -> None:
        buyer_surfaces = (
            SKILL_DIRECTORY / "references" / "company-context.md",
            SKILL_DIRECTORY / "references" / "sources" / "salesforce.md",
            SKILL_DIRECTORY / "references" / "sources" / "google-calendar.md",
            SKILL_DIRECTORY / "references" / "demo-portfolio.json",
            SKILL_DIRECTORY / "references" / "demo-leadership.json",
        )

        for buyer_surface in buyer_surfaces:
            with self.subTest(buyer_surface=buyer_surface.relative_to(SKILL_DIRECTORY)):
                content = buyer_surface.read_text(encoding="utf-8")
                self.assertIn("Cameron Ruiz", content)
                self.assertNotIn("Cameron Diaz", content)

    def test_chat_owns_all_followups_and_never_offers_more_than_three_options(self) -> None:
        flow = (SKILL_DIRECTORY / "references" / "demo-flow.md").read_text(encoding="utf-8")
        skill = (SKILL_DIRECTORY / "SKILL.md").read_text(encoding="utf-8")
        question_map = (SKILL_DIRECTORY / "references" / "demo-followup-map.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("All generated drafts, follow-up questions", flow)
        self.assertIn("Show no more than three numbered options", flow)
        self.assertIn("Keep all suggested questions, next steps, and generated drafts", skill)
        self.assertIn(
            "Both dashboards remain read-only evidence and reporting artifacts", question_map
        )

        menus = re.findall(
            r"(?:\nNext steps|After you've reviewed:)\n\n"
            r"(?P<options>(?:\d+\. [^\n]+\n?)+)",
            flow,
        )
        self.assertTrue(menus)
        self.assertIn(
            "After you've taken a look, let's make a deck to prep for the meeting "
            "to make sure it lands",
            flow,
        )
        for menu in menus:
            with self.subTest(menu=menu):
                self.assertLessEqual(len(re.findall(r"(?m)^\d+\. ", menu)), 3)

    def test_demo_has_source_grounded_launch_followups_and_seller_owned_actions(self) -> None:
        flow = (SKILL_DIRECTORY / "references" / "demo-flow.md").read_text(encoding="utf-8")
        question_map = (SKILL_DIRECTORY / "references" / "demo-followup-map.md").read_text(
            encoding="utf-8"
        )

        self.assertEqual(self.portfolio["recentLaunch"]["targetAccount"], "Northstar Health")
        self.assertEqual(self.portfolio["recentLaunch"]["targetContact"], "Jordan Lee")
        self.assertIn("pilot-readiness", flow)
        self.assertIn("uptime", flow)
        self.assertIn("without creating, saving, or sending the email", flow)
        launch_branch = flow.split("### Branch: launch_reengagement_draft", maxsplit=1)[1]
        launch_branch = re.split(r"^### Branch:", launch_branch, maxsplit=1, flags=re.MULTILINE)[0]
        self.assertIn("Jordan Lee", launch_branch)
        self.assertIn("Would you and Casey", launch_branch)
        self.assertIn("Priya Shah", launch_branch)
        self.assertIn("fast forward to after your meeting", launch_branch)
        self.assertIn("if requested", launch_branch)
        self.assertNotIn("Publish this account overview", launch_branch)
        self.assertIn("Which other accounts match last week's launch?", flow)
        self.assertIn("Why is Northstar Health first?", question_map)
        self.assertIn("What is missing, conflicting, or uncertain?", question_map)
        self.assertIn("Who should I contact, and why?", question_map)
        self.assertIn("Did selecting Save it to Salesforce write anything?", question_map)

        for group in RENDERER.EXPECTED_COUNTS:
            for account in self.portfolio[group]:
                with self.subTest(account=account["account"]):
                    self.assertEqual(account["owner"], self.portfolio["seller"]["name"])
                    self.assertRegex(
                        account["nextAction"].lower(),
                        r"^(?:ask|draft|invite|prepare|review|watch|monitor|pause)\b",
                        "Seller actions should be concrete imperatives without requiring repetitive possessives.",
                    )

    def test_recent_signals_identify_provider_artifact_and_concrete_account_facts(self) -> None:
        supported_sources = {
            "Salesforce",
            "Gmail",
            "Google Calendar",
            "Granola",
            "Slack",
            "Google Drive",
        }
        for account_name, details in self.portfolio["accountDetails"].items():
            events = details.get("events", [])
            with self.subTest(account=account_name):
                self.assertGreaterEqual(len(events), 4)
                self.assertIn("Salesforce", {event["source"] for event in events})
            for event in events:
                with self.subTest(account=account_name, source=event.get("source")):
                    self.assertIn(event["source"], supported_sources)
                    self.assertTrue(event.get("reference"))
                    self.assertTrue(event.get("detail"))

        atlas = self.portfolio["accountDetails"]["Atlas Manufacturing"]["events"]
        salesforce = next(event for event in atlas if event["source"] == "Salesforce")
        slack = next(event for event in atlas if event["source"] == "Slack")
        self.assertIn("Multi-Plant Governed Operations Expansion", salesforce["reference"])
        self.assertIn("$680,000", salesforce["title"])
        self.assertIn("#acct-atlas-manufacturing", slack["reference"])
        self.assertIn("Sam Rivera", slack["reference"])

    def test_northstar_sources_distinguish_customer_account_billing_and_userops_channels(
        self,
    ) -> None:
        references = SKILL_DIRECTORY / "references"
        slack_source = (references / "sources" / "slack.md").read_text(encoding="utf-8")
        company_context = (references / "company-context.md").read_text(encoding="utf-8")
        flow = (references / "demo-flow.md").read_text(encoding="utf-8")
        leadership = RENDERER.load_leadership_data(portfolio=self.portfolio)
        northstar = self.portfolio["accountDetails"]["Northstar Health"]
        slack_events = {
            event["reference"] for event in northstar["events"] if event["source"] == "Slack"
        }
        slack_coverage = next(
            source for source in leadership["sourceCoverage"] if source["name"] == "Slack"
        )

        for channel in (
            "#ext-northstar-health",
            "#acct-northstar-health",
            "#billing-deal-desk",
            "#userops-enterprise-rollouts",
        ):
            with self.subTest(channel=channel):
                self.assertIn(channel, slack_source)
                self.assertIn(channel, company_context)
                self.assertIn(channel, flow)
                self.assertIn(channel, slack_coverage["detail"])
                self.assertTrue(any(channel in reference for reference in slack_events))

        self.assertIn("external slack connect", slack_source.lower())
        self.assertIn("internal", slack_source.lower())
        self.assertIn("never expose", slack_source.lower())
        self.assertEqual(northstar["commercialGuardrails"]["approvedAnnualOpportunity"], 420000)
        self.assertEqual(northstar["commercialGuardrails"]["currentSeats"], 1200)
        self.assertEqual(northstar["commercialGuardrails"]["proposedSeats"], 4500)
        self.assertFalse(northstar["commercialGuardrails"]["servicesApproved"])
        self.assertFalse(northstar["commercialGuardrails"]["servicesQuoted"])

    def test_northstar_pricing_and_packaging_deck_is_visible_across_every_evidence_surface(
        self,
    ) -> None:
        references = SKILL_DIRECTORY / "references"
        drive_source = (references / "sources" / "google-drive.md").read_text(encoding="utf-8")
        company_context = (references / "company-context.md").read_text(encoding="utf-8")
        flow = (references / "demo-flow.md").read_text(encoding="utf-8")
        leadership = RENDERER.load_leadership_data(portfolio=self.portfolio)
        northstar = self.portfolio["accountDetails"]["Northstar Health"]
        drive_events = [event for event in northstar["events"] if event["source"] == "Google Drive"]
        drive_coverage = next(
            source for source in leadership["sourceCoverage"] if source["name"] == "Google Drive"
        )

        for source in (drive_source, company_context, flow, drive_coverage["detail"]):
            with self.subTest(source=source[:80]):
                self.assertIn("Pricing & Packaging Options", source)
                self.assertIn("Customer Working Session", source)
                self.assertIn("FY{{fiscal_year}} Pricing & Packaging Options", source)

        self.assertTrue(
            any(
                "Pricing & Packaging Options" in event["reference"]
                and "$420,000" in f"{event['title']} {event['detail']}"
                and "unapproved" in event["detail"]
                for event in drive_events
            )
        )

    def test_leadership_issues_pair_grounded_customer_blockers_with_tangible_interventions(
        self,
    ) -> None:
        leadership = RENDERER.load_leadership_data(portfolio=self.portfolio)
        account_details = self.portfolio["accountDetails"]

        cases = (
            (
                "Atlas Manufacturing",
                ("Taylor Reed", "plant", "performance", "Priya Shah", "Devon Brooks"),
                ("on-site", "onsite"),
            ),
            (
                "Solstice Financial",
                ("Dana Kim", "Reese Bennett", "Leila Chen", "delegated"),
                ("product manager",),
            ),
        )

        for account, expected_facts, intervention_terms in cases:
            with self.subTest(account=account):
                signals = [
                    signal for signal in leadership["signals"] if account in signal["accounts"]
                ]
                decisions = [
                    decision
                    for decision in leadership["decisions"]
                    if account in decision["accounts"]
                ]
                self.assertTrue(signals)
                self.assertTrue(decisions)

                action_decisions = [
                    decision
                    for decision in decisions
                    if all(
                        decision.get(field)
                        for field in (
                            "problem",
                            "customerContext",
                            "proposedSolution",
                            "sourceEvidence",
                        )
                    )
                ]
                self.assertTrue(action_decisions)

                leadership_text = json.dumps(signals + action_decisions).lower()
                account_text = json.dumps(account_details[account]).lower()
                for fact in expected_facts:
                    self.assertIn(fact.lower(), leadership_text)
                    self.assertIn(fact.lower(), account_text)
                self.assertTrue(any(term in leadership_text for term in intervention_terms))
                self.assertTrue(any(term in account_text for term in intervention_terms))

                self.assertTrue(
                    any(
                        source.get("source") in {"Slack", "Granola", "Google Drive", "Salesforce"}
                        and source.get("reference")
                        and source.get("detail")
                        for decision in action_decisions
                        for source in decision["sourceEvidence"]
                    )
                )

    def test_each_account_has_specific_source_grounded_commercial_priority_rationale(self) -> None:
        rationales: dict[str, list[str]] = {}

        for group in RENDERER.EXPECTED_COUNTS:
            for account in self.portfolio[group]:
                with self.subTest(account=account["account"]):
                    details = self.portfolio["accountDetails"].get(account["account"], {})
                    rationale = details.get("rationale") or account.get("rationale")
                    self.assertIsInstance(rationale, list)
                    if not isinstance(rationale, list):
                        continue
                    self.assertGreaterEqual(len(rationale), 2)
                    self.assertLessEqual(len(rationale), 3)
                    self.assertTrue(
                        all(isinstance(item, str) and item.strip() for item in rationale)
                    )
                    self.assertTrue(
                        any(account["value"] in item for item in rationale),
                        "At least one rationale should name the account's exact commercial value.",
                    )
                    rationales[account["account"]] = rationale

        self.assertIn("third-largest", " ".join(rationales["Northstar Health"]).lower())
        self.assertIn("largest", " ".join(rationales["Atlas Manufacturing"]).lower())
        redwood_rationale = " ".join(rationales["Redwood Retail"])
        self.assertIn("renewal", redwood_rationale.lower())
        self.assertIn("SignalStack AI", redwood_rationale)
        self.assertIn("freeze", " ".join(rationales["Ember Energy"]).lower())
        self.assertIn("second-largest", " ".join(rationales["Lattice Public Sector"]).lower())

        for source in ("gmail.md", "slack.md"):
            with self.subTest(source=source):
                evidence = (SKILL_DIRECTORY / "references" / "sources" / source).read_text(
                    encoding="utf-8"
                )
                self.assertIn("SignalStack AI", evidence)
        leadership = RENDERER.load_leadership_data(portfolio=self.portfolio)
        redwood_leadership = next(
            deal for deal in leadership["topDeals"] if deal["account"] == "Redwood Retail"
        )
        self.assertIn("SignalStack", redwood_leadership["risk"])


if __name__ == "__main__":
    unittest.main()
