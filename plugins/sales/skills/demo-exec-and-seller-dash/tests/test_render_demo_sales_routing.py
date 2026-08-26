"""Regression coverage for Sales skill routing and instruction ownership."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from sales_test_support import SalesTestCase

SKILL_DIRECTORY = Path(__file__).resolve().parent.parent


class SalesSkillRoutingTests(SalesTestCase):
    def test_focused_workflows_require_shared_guidance_except_explicit_demo(self) -> None:
        plugin = SKILL_DIRECTORY.parent.parent
        index = (plugin / "skills/index/SKILL.md").read_text(encoding="utf-8")
        shared = (plugin / "shared_skill_instructions.md").read_text(encoding="utf-8")
        demo = (SKILL_DIRECTORY / "SKILL.md").read_text(encoding="utf-8")
        manifest = json.loads((plugin / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))

        self.assertIn("## Initial Skill Frontmatter Read.", index)
        self.assertIn("Do this quickly before handling any other instructions", index)
        self.assertIn("## Mandatory Focused Workflow Path", index)
        self.assertLess(
            index.index("## Initial Skill Frontmatter Read."),
            index.index("## Mandatory Focused Workflow Path"),
        )
        self.assertIn("including its `## Key Dependency Categories`", index)
        self.assertIn("Select the best focused owner based on those descriptions", index)
        self.assertIn("selected focused skill's description explicitly declares", index)
        self.assertIn(
            "Instruction reads and other safe setup tool calls may run in parallel", index
        )
        self.assertIn("including self-contained demonstrations", index)
        self.assertIn("shared instructions and dependencies are optional", index)
        self.assertIn("including when already loaded or read in parallel", index)
        self.assertIn("no strictly sequential tool-call barrier is required", index)
        self.assertIn("before resolving dependencies", index)
        self.assertIn("before the first clarification or `request_user_input` call", index)
        self.assertIn("Reading installed instructions is safe setup", index)
        self.assertNotIn("MANDATORY SEQUENTIAL BARRIER", index)
        self.assertNotIn("wait for its complete tool result", index)
        self.assertNotIn("same parallel tool-call batch", index)
        self.assertNotIn("never load plugin-level shared instructions or dependencies", index)
        self.assertIn("honor that focused skill's declared exception", index)
        self.assertLess(
            index.index("honor that focused skill's declared exception"),
            index.index("1. Read this Sales index"),
        )
        self.assertNotIn("Route real seller account-home", index)
        self.assertNotIn("For a bare request such as", index)
        self.assertNotIn("demo-exec-and-seller-dash", index)
        self.assertIn("EXPLICIT SHARED-INSTRUCTIONS OPT-OUT", demo)
        self.assertIn("MANDATORY SELF-CONTAINED PATH", demo)
        self.assertIn("Shared instructions and dependencies are optional", demo)
        self.assertIn("already be in context or be read in parallel", demo)
        self.assertIn("already-loaded or safely batched instruction reads are allowed", demo)
        self.assertIn("safe instruction/resource reads do not count as launcher actions", demo)
        self.assertNotIn("read only the Sales index and this demo skill", demo)
        self.assertNotIn("Do not read `shared_skill_instructions.md`", demo)
        self.assertNotIn("never load shared_skill_instructions.md or dependencies.md", demo)
        self.assertIn("MANDATORY: Read [dependencies.md](dependencies.md) in full", shared)
        self.assertIn("#### Limitations And Improvements", shared)
        self.assertIn("two or three highly likely", shared)
        self.assertIn("stricter option count and one-question-per-call", shared)
        self.assertIn("`request_user_input` is available", shared)
        self.assertNotIn("answers-ask-user-input", shared)
        self.assertEqual(manifest["apps"], "./.app.json")
        self.assertTrue((plugin / ".app.json").is_file())
        self.assertTrue((plugin / "skills/sales-presentations/SKILL.md").is_file())
        for retired_skill in (
            "answers-ask-user-input",
            "apollo",
            "hubspot",
            "salesforce",
            "zoominfo",
        ):
            with self.subTest(retired_skill=retired_skill):
                self.assertFalse((plugin / "skills" / retired_skill).exists())

        for focused_skill in sorted((plugin / "skills").glob("*/SKILL.md")):
            skill_name = focused_skill.parent.name
            if skill_name in {"index", "demo-exec-and-seller-dash"}:
                continue
            with self.subTest(skill=skill_name):
                instructions = focused_skill.read_text(encoding="utf-8")
                self.assertIn("## Key Dependency Categories", instructions)
                self.assertIn(
                    "[the shared Sales skill instructions](../../shared_skill_instructions.md)",
                    instructions,
                )
                self.assertNotIn("../index/SKILL.md#limitations-and-improvements", instructions)
                self.assertNotIn("../index/SKILL.md#4-next-steps", instructions)

    def test_sufficient_first_sale_context_delivers_a_plan_before_optional_questions(
        self,
    ) -> None:
        strategy = (SKILL_DIRECTORY.parent / "plan-deal-strategy" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        first_sale = strategy.partition("#### First-Sale Motion From Supplied Context")[2]
        self.assertTrue(first_sale, "A supplied first-sale motion needs its own explicit path.")
        first_sale = first_sale.partition("\n### 2.")[0]

        self.assert_contains(
            first_sale,
            "product or offer",
            "target buyer",
            "pilot or evaluation",
            "stated objections",
            "Deliver a substantive first-pass plan before requesting clarification",
            "or using `request_user_input`",
            "buyer discovery",
            "pilot sequencing",
            "data-handling safeguards",
            "staff-time mitigation",
            "concrete next sales actions",
            "preserve the user's supplied pilot duration",
            "State missing details as assumptions or unresolved questions",
            "Ask optional follow-up questions only after the useful plan",
            "existing opportunity",
            "customer commitment",
            "pricing",
            "approved security posture",
        )

    def test_orientation_recommends_the_guided_demo_after_real_workflows(self) -> None:
        orientation = (
            SKILL_DIRECTORY.parent / "index/references/orientation-response.md"
        ).read_text(encoding="utf-8")

        self.assertNotIn("## Start With The Guided Sales Demo", orientation)
        self.assertIn(
            "@Sales create my account dashboard to prioritize accounts, track what changed, "
            "flag pipeline risk, and recommend what to do next.",
            orientation,
        )
        self.assertIn(
            "@Sales create my executive dashboard to grow revenue, monitor forecast risk, "
            "focus strategic accounts, and improve team performance.",
            orientation,
        )
        self.assert_excludes(
            orientation,
            "| Prioritize accounts |",
            "| Understand what changed in an account |",
            "| Triage pipeline and forecast risk |",
        )
        self.assertTrue(
            orientation.rstrip().endswith(
                "A great starting point is to go through the guided demo workflow. "
                "Would you like to start there?"
            )
        )
        self.assertLess(
            orientation.index("## Simpler Use Cases"),
            orientation.index("## More Advanced Use Cases"),
        )

    def test_dashboard_role_mismatches_offer_safe_targeting_choices(self) -> None:
        lifecycle = (SKILL_DIRECTORY.parent.parent / "references/dashboard-lifecycle.md").read_text(
            encoding="utf-8"
        )

        for skill_name in ("seller-account-dashboard", "sales-leadership-dashboard"):
            with self.subTest(skill=skill_name):
                instructions = (SKILL_DIRECTORY.parent / skill_name / "SKILL.md").read_text(
                    encoding="utf-8"
                )
                for choice in ("placeholder", "representative", "target user"):
                    self.assertIn(choice, instructions.lower())
                    self.assertIn(choice, lifecycle.lower())
                self.assertIn("empty placeholder never requires CRM", instructions)

        self.assertIn("unknown", lifecycle.lower())
        self.assertIn("authorized", lifecycle.lower())
        self.assertIn("without CRM", lifecycle)
        self.assertIn("never probe additional connectors solely to determine a role", lifecycle)
        self.assertIn("Wait for the user's choice", lifecycle)
        self.assertIn("--mode placeholder", lifecycle)
        self.assertIn("--mode representative", lifecycle)
        self.assertIn("dashboardIdentity", lifecycle)
        self.assertIn("names that actual export", lifecycle)

    def test_seller_focus_personalizes_one_complete_grounded_dashboard(self) -> None:
        lifecycle = (SKILL_DIRECTORY.parent.parent / "references/dashboard-lifecycle.md").read_text(
            encoding="utf-8"
        )
        seller = (SKILL_DIRECTORY.parent / "seller-account-dashboard/SKILL.md").read_text(
            encoding="utf-8"
        )

        for instructions in (lifecycle, seller):
            with self.subTest(source="lifecycle" if instructions is lifecycle else "seller"):
                for capability in ("Home", "Accounts", "Pipeline", "Your focus"):
                    self.assertIn(capability, instructions)
                for capability in ("search", "filters", "stakeholders"):
                    self.assertIn(capability, instructions.lower())
                self.assertRegex(instructions.lower(), r"(?:never|omit).{0,100}(?:invent|fabricat)")

        self.assertIn("saved goal determines only", lifecycle)
        self.assertIn("never a competing one-off page", seller)

    def test_dashboards_ask_for_goals_and_offer_next_steps_sequentially(self) -> None:
        lifecycle = (SKILL_DIRECTORY.parent.parent / "references/dashboard-lifecycle.md").read_text(
            encoding="utf-8"
        )
        goal_question = (
            "What do you want front and center in your dashboard? "
            "You can always customize this later."
        )
        style_question = "What look and feel would you like for your dashboard?"

        for skill_name in ("seller-account-dashboard", "sales-leadership-dashboard"):
            with self.subTest(skill=skill_name):
                instructions = (SKILL_DIRECTORY.parent / skill_name / "SKILL.md").read_text(
                    encoding="utf-8"
                )
                self.assertIn("goal", instructions.lower())
                self.assertIn("style", instructions.lower())
                self.assertIn("exactly one next step", instructions)
                self.assertIn(goal_question, instructions)
                self.assertIn(style_question, instructions)
                self.assertIn("exactly three", instructions)
                self.assertNotIn("all of the above", instructions.lower())
                self.assertRegex(instructions, r"exactly one question|questions\.length === 1")
                self.assertIn("If the Sales index has not genuinely been read", instructions)

        for requirement in (
            "request_user_input",
            "one private dashboard",
            "bookmark",
            "automation",
            "one-line",
            "one at a time",
            "explicit",
            "customize",
            "imagegen",
            "image_gen",
            "storyboard",
            "anonymized",
            "before implementation",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, lifecycle.lower())

        self.assertIn("published only with permission", lifecycle)
        self.assertIn("only after explicit user approval", lifecycle)
        self.assertIn("automation_update", lifecycle)
        self.assertIn("Other", lifecycle)
        self.assertIn("automatically", lifecycle)
        self.assertIn(goal_question, lifecycle)
        self.assertIn(style_question, lifecycle)
        self.assertNotIn("all of the above", lifecycle.lower())
        self.assertIn("exactly one question object", lifecycle)
        self.assertIn("wait for its answer", lifecycle)
        self.assertIn("A broad request naming multiple outcomes", lifecycle)
        self.assertIn("exactly three mutually exclusive", lifecycle)
        self.assertIn("never include an explicit Other option", lifecycle)
        self.assertIn("never include real customer names, CRM values", lifecycle)
        self.assertIn("reuse the saved goal, style, and image reference", lifecycle)
        self.assertLess(
            lifecycle.index("1. Without a matching private Site:"),
            lifecycle.index("2. Once that Site exists:"),
        )
        self.assertLess(
            lifecycle.index("2. Once that Site exists:"),
            lifecycle.index("3. Once that automation exists:"),
        )

        leadership = (SKILL_DIRECTORY.parent / "sales-leadership-dashboard/SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Omit unsupported", leadership)
        self.assertIn("preserve verified zero values", leadership)
        self.assertIn(
            "How should I handle the fact that Salesforce does not identify you "
            "as a sales manager or executive?",
            leadership,
        )

    def test_dashboard_goal_choices_use_existing_memory_and_authorized_context(self) -> None:
        lifecycle = (SKILL_DIRECTORY.parent.parent / "references/dashboard-lifecycle.md").read_text(
            encoding="utf-8"
        )
        goal_section = lifecycle.partition("## Orient The User And Establish Their Goal")[2]
        goal_section = goal_section.partition("## Select A Design Direction")[0]

        self.assertIn("reliable existing user memories", lifecycle)
        self.assertIn("quickly available, already-authorized context", lifecycle)
        self.assertIn("never perform additional connector probes", lifecycle.lower())
        self.assertIn("never invent or disclose private memory details", lifecycle.lower())
        self.assertIn("current conversation", lifecycle.lower())
        self.assertRegex(lifecycle.lower(), r"memor(?:y|ies).{0,80}already available")
        self.assertIn("saved preferences", lifecycle.lower())
        self.assertRegex(
            lifecycle.lower(), r"never perform additional connector probes.{0,120}(?:search|lookup)"
        )
        self.assertIn("Explicit current-task preferences override saved conventions", goal_section)
        self.assertIn(
            "only for wording, never as proof of a role, account, metric, "
            "source access, or authorization",
            goal_section,
        )
        self.assertIn("never inspect other conversations, history, files, CRM", goal_section)
        self.assertIn("persist a one-off preference", goal_section)
        self.assertNotIn("memory tool", goal_section.lower())
        for context_source in ("conversation", "request", "role", "portfolio", "preferences"):
            with self.subTest(context_source=context_source):
                self.assertIn(context_source, lifecycle.lower())

        self.assertRegex(goal_section.lower(), r"personaliz(?:e|ed|ing).*(?:goal|choice|option)")
        self.assertIn(
            "What do you want front and center in your dashboard? "
            "You can always customize this later.",
            goal_section,
        )
        self.assertNotIn("all of the above", goal_section.lower())
        self.assertIn("exactly three", goal_section)
        self.assertIn("request_user_input", goal_section)
        self.assertIn("automatically", goal_section)
        self.assertIn("Other", goal_section)
        self.assertRegex(lifecycle.lower(), r"(?:fallback|fall back).{0,100}(?:default|generic)")

        for skill_name in ("seller-account-dashboard", "sales-leadership-dashboard"):
            with self.subTest(skill=skill_name):
                instructions = (SKILL_DIRECTORY.parent / skill_name / "SKILL.md").read_text(
                    encoding="utf-8"
                )
                goal_line = next(
                    line
                    for line in instructions.splitlines()
                    if line.startswith("**Dashboard goal:**")
                )
                self.assertRegex(goal_line.lower(), r"personaliz(?:e|ed|ing)")
                self.assertRegex(goal_line.lower(), r"memor(?:y|ies)")
                self.assertIn("context", goal_line.lower())
                self.assertIn("exactly three", goal_line)
                self.assertIn("What do you want front and center in your dashboard?", goal_line)
                self.assertIn("(Recommended)", goal_line)

        seller = (SKILL_DIRECTORY.parent / "seller-account-dashboard/SKILL.md").read_text(
            encoding="utf-8"
        )
        leadership = (SKILL_DIRECTORY.parent / "sales-leadership-dashboard/SKILL.md").read_text(
            encoding="utf-8"
        )
        for option in (
            "Account priorities and changes (Recommended)",
            "Pipeline and forecast risk",
            "Customer meetings and follow-ups",
        ):
            self.assertIn(option, seller)
        for option in (
            "Forecast and revenue growth (Recommended)",
            "Strategic account focus",
            "Team performance and coaching",
        ):
            self.assertIn(option, leadership)

    def test_dashboard_questions_load_instructions_first_and_advance_one_stage(self) -> None:
        plugin = SKILL_DIRECTORY.parent.parent
        index = (plugin / "skills/index/SKILL.md").read_text(encoding="utf-8")
        shared = (plugin / "shared_skill_instructions.md").read_text(encoding="utf-8")
        lifecycle = (plugin / "references/dashboard-lifecycle.md").read_text(encoding="utf-8")

        self.assertIn("before the first clarification or `request_user_input` call", index)
        self.assertIn("mandatory workflow reference", index)
        self.assertIn("Reading installed instructions is safe setup", index)
        self.assertIn("stricter option count and one-question-per-call", shared)
        self.assertIn("questions.length === 1", lifecycle)
        self.assertIn("exactly three options", lifecycle)
        self.assertIn("wait for its answer", lifecycle)
        self.assertIn("same execution turn", lifecycle)
        self.assertIn("ask in chat", lifecycle)
        self.assertLess(
            lifecycle.index("verified role mismatch"), lifecycle.index("dashboard goal")
        )

        for skill_name in ("seller-account-dashboard", "sales-leadership-dashboard"):
            with self.subTest(skill=skill_name):
                instructions = (plugin / "skills" / skill_name / "SKILL.md").read_text(
                    encoding="utf-8"
                )
                self.assertIn("If the Sales index has not genuinely been read", instructions)
                self.assertIn("reread this focused skill in full", instructions)
                self.assertIn("questions.length === 1", instructions)

    def test_dashboard_omission_and_opt_out_override_legacy_ranking_contract(self) -> None:
        plugin = SKILL_DIRECTORY.parent.parent
        lifecycle = (plugin / "references/dashboard-lifecycle.md").read_text(encoding="utf-8")
        seller = (plugin / "skills/seller-account-dashboard/SKILL.md").read_text(encoding="utf-8")
        legacy_schema = json.loads(
            (
                plugin / "skills/seller-account-dashboard/references/template-payload.schema.json"
            ).read_text(encoding="utf-8")
        )

        self.assertIn("rank", legacy_schema["$defs"]["accountRow"]["required"])
        self.assertIn("value", legacy_schema["$defs"]["accountRow"]["required"])
        self.assertIn("only this explicit pane", seller.lower())
        self.assertRegex(seller.lower(), r"never apply.{0,80}broad dashboard")
        self.assertRegex(seller.lower(), r"(?:omit|omits).{0,80}(?:unsourced|unsupported)")
        self.assertRegex(lifecycle.lower(), r"conversational fallback.{0,120}(?:never|omit)")
        self.assertIn("preserve account order without assigning priority", lifecycle)
        self.assertIn("verified account values and opportunity amounts separate", lifecycle)
        self.assertIn("explicitly declines image generation", lifecycle)
        self.assertIn("without an image-permission question or image-tool call", lifecycle)
        self.assertIn("without inspecting files, profiles, CRM, or connectors", lifecycle)

    def test_dashboard_design_choices_are_personalized_without_exposing_private_context(
        self,
    ) -> None:
        lifecycle = (SKILL_DIRECTORY.parent.parent / "references/dashboard-lifecycle.md").read_text(
            encoding="utf-8"
        )
        style_section = lifecycle.partition(
            "## Select A Design Direction And Generate Its Visual Reference"
        )[2]
        style_section = style_section.partition("## Match The Current User")[0]

        self.assertRegex(
            style_section.lower(), r"personaliz(?:e|ed|ing).*(?:choice|selection|alternative)"
        )
        self.assertRegex(style_section.lower(), r"(?:memor(?:y|ies)|context|preferences)")
        self.assert_contains(
            style_section,
            "exactly three mutually exclusive",
            "What look and feel would you like for your dashboard?",
            "Codex Default (Recommended)",
            "Clean surfaces, crisp type, quiet contrast.",
            "options two and three",
            "context-appropriate alternatives",
            "never use a fixed alternative pair",
            "at most eight words",
            "model judgment",
            "accessible",
            "not a thirteenth catalog direction",
            "light theme",
            "medium density",
            "system sans typography",
            "#f6f6f6",
            "#ffffff",
            "#f0f0f0",
            "#e5e5e5",
            "#171717",
            "#626262",
            "#d2d2d2",
            "6px control radii",
            "10px medium-container radii",
            "restrained hairline or small shadows",
            "monospace only for identifiers",
            "44px interactive-target requirement overrides",
        )
        for direction, character, density in (
            ("Precision Modern", "Crisp grid, warm white, ink, one sharp accent", "Medium"),
            (
                "Executive Briefing",
                "Editorial typography, narrative headlines, restrained charts",
                "Low",
            ),
            ("Mission Control", "Dark mode, live status, layered operational detail", "High"),
            (
                "Electric Neon",
                "Charcoal canvas, acid green/violet, glowing signals",
                "Medium–high",
            ),
            ("Swiss Data System", "Strong grid, bold type, primary-color blocks", "High"),
            ("Soft Utility", "Tinted neutrals, rounded controls, approachable calm", "Medium"),
            (
                "Terminal Intelligence",
                "Monospace, command-line cues, raw data confidence",
                "Very high",
            ),
            (
                "Glass Observatory",
                "Deep gradient, translucent panels, atmospheric charts",
                "Low–medium",
            ),
            (
                "Financial Ledger",
                "Dense tables, precision numbers, subtle red/green",
                "Very high",
            ),
            (
                "Magazine Dashboard",
                "Big visual stories, asymmetric composition, curated metrics",
                "Low",
            ),
            (
                "Builder’s Workbench",
                "Practical, modular, component-library feel",
                "Medium–high",
            ),
            ("Arcade Analytics", "Retro-futurist, pixel/signal motifs, playful urgency", "Medium"),
        ):
            with self.subTest(direction=direction):
                self.assertIn(f"| {direction} | {character} | {density} |", style_section)
        for obsolete_generic_direction in (
            "Simple and focused",
            "Open and spacious",
            "Compact and efficient",
            "Detailed and structured",
            "Warm and welcoming",
            "Calm and understated",
            "Bright and energetic",
            "Friendly and playful",
            "Classic and professional",
            "Modern and polished",
            "Elegant and editorial",
            "Bold and expressive",
            "Dark and refined",
            "Premium and minimal",
        ):
            self.assertNotIn(obsolete_generic_direction, style_section)
        self.assertIn("automatically", style_section)
        self.assertIn("never include an explicit Other option", style_section)
        self.assertIn("Only **Codex Default** carries `(Recommended)`", style_section)
        self.assertIn("anonymized", style_section)
        self.assertIn("never include real customer names, CRM values", style_section)
        self.assertIn("private memory details", style_section)
        self.assertIn("user supplies an authorized genuine asset", style_section)
        self.assertIn(
            "never generate, imitate, trace, search for, or assume a Codex pet", style_section
        )
        self.assertIn("omit it otherwise", style_section)

        for skill_name in ("seller-account-dashboard", "sales-leadership-dashboard"):
            with self.subTest(skill=skill_name):
                instructions = (SKILL_DIRECTORY.parent / skill_name / "SKILL.md").read_text(
                    encoding="utf-8"
                )
                style_line = next(
                    line
                    for line in instructions.splitlines()
                    if line.startswith("**Design style:**")
                )
                self.assertRegex(style_line.lower(), r"personaliz(?:e|ed|ing)")
                self.assertRegex(style_line.lower(), r"memor(?:y|ies)")
                self.assertIn("context", style_line.lower())
                self.assertIn("three distinct", style_line)
                self.assertIn("What look and feel would you like for your dashboard?", style_line)
                self.assertIn("visual", style_line.lower())
                self.assertIn("Codex Default (Recommended)", style_line)
                self.assertIn("Clean surfaces, crisp type, quiet contrast.", style_line)
                self.assertIn("two contextual alternatives", style_line)
                self.assertIn("full twelve-direction catalog", style_line)
                self.assertIn("never use a fixed pair", style_line)
                self.assertIn("at most eight words", style_line)
                self.assertIn("user supplies an authorized genuine asset", style_line)
                self.assertIn(
                    "never generate, imitate, trace, search for, or assume one", style_line
                )

    def test_dashboard_visual_personalities_are_accessible_and_business_ready(self) -> None:
        lifecycle = (SKILL_DIRECTORY.parent.parent / "references/dashboard-lifecycle.md").read_text(
            encoding="utf-8"
        )
        style_section = lifecycle.partition(
            "## Select A Design Direction And Generate Its Visual Reference"
        )[2].partition("## Match The Current User")[0]

        for requirement in (
            "professional",
            "polished",
            "accessible",
            "verified",
            "functional",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, style_section.lower())

        forbidden_styles = (
            "Field-notes expedition",
            "Editorial account studio",
            "Mission-control observatory",
            "Modern executive editorial",
            "Revenue operating review",
            "Calm customer cockpit",
            "Crisp deal desk",
            "Detailed account view",
            "Detailed performance view",
            "Clean executive summary",
        )
        for skill_name in ("seller-account-dashboard", "sales-leadership-dashboard"):
            with self.subTest(skill=skill_name):
                instructions = (SKILL_DIRECTORY.parent / skill_name / "SKILL.md").read_text(
                    encoding="utf-8"
                )
                style_line = next(
                    line
                    for line in instructions.splitlines()
                    if line.startswith("**Design style:**")
                )
                self.assertIn("three distinct", style_line)
                self.assertIn("visual", style_line.lower())
                self.assertIn("Codex Default (Recommended)", style_line)
                for obsolete_style in forbidden_styles:
                    self.assertNotIn(obsolete_style, instructions)
                self.assertIn("character", style_line.lower())
                self.assertIn("density", style_line.lower())
                self.assertIn("accessible", style_line.lower())

        self.assert_contains(
            style_section,
            "Mission Control",
            "Electric Neon",
            "Glass Observatory",
            "Arcade Analytics",
            "dark, neon, translucent, pixel, or playful aesthetics remain selectable",
            "pointless radar rings",
        )

    def test_dashboard_storyboards_follow_verified_data_and_feasible_interactions(self) -> None:
        lifecycle = (SKILL_DIRECTORY.parent.parent / "references/dashboard-lifecycle.md").read_text(
            encoding="utf-8"
        )
        style_section = lifecycle.partition(
            "## Select A Design Direction And Generate Its Visual Reference"
        )[2].partition("## Match The Current User")[0]
        normalized_style = style_section.lower()

        self.assertIn("before crafting the storyboard", normalized_style)
        self.assertIn("verified available data", normalized_style)
        self.assertRegex(normalized_style, r"credible(?: and|,)\s+implementable")
        self.assertIn("interactions", normalized_style)
        self.assertIn("anonymized", normalized_style)
        self.assertIn("never include real customer names, crm values", normalized_style)
        self.assertIn("before implementation", normalized_style)
        self.assertLess(
            normalized_style.index("before crafting the storyboard"),
            normalized_style.index("storyboard showing"),
        )
        self.assertLess(
            normalized_style.index("storyboard showing"),
            normalized_style.index("use the existing polished demo template"),
        )
        self.assertRegex(normalized_style, r"(?:no|never).{0,100}speculative")
        self.assert_contains(
            normalized_style,
            "placeholder",
            "selected exact direction",
            "character",
            "density",
            "palette",
            "materials",
            "typography",
            "css-variable",
            "canvas",
            "sticky bars",
            "focus indicators",
            "theme color",
            "opaque fallback",
            "red/green comparisons",
            "redundant text or icons",
            "44px",
            "reduced-motion",
            "preserve the customized html/theme",
        )

    def test_dashboards_omit_unsupported_widgets_and_verify_every_visible_control(self) -> None:
        lifecycle = (SKILL_DIRECTORY.parent.parent / "references/dashboard-lifecycle.md").read_text(
            encoding="utf-8"
        )
        normalized_lifecycle = lifecycle.lower()

        self.assert_contains(
            normalized_lifecycle,
            "verified evidence",
            "genuinely functional",
            "decision-critical",
            "conversational response",
            "never in dashboard panels",
            "clean intentional empty state",
            "no invented target or attainment",
            "evidence & limits",
            "forecast integrity",
            "neon",
            "radar",
            "dead navigation",
        )

        self.assertRegex(normalized_lifecycle, r"giant.{0,30}decorative whitespace")
        self.assertRegex(normalized_lifecycle, r"quota.{0,25}attainment.{0,25}unavailable")
        self.assertRegex(normalized_lifecycle, r"(?:click|exercise).{0,120}(?:tab|navigation)")
        self.assertRegex(normalized_lifecycle, r"(?:exercise|test).{0,80}(?:search|filter)")
        self.assertRegex(normalized_lifecycle, r"(?:inspect|check).{0,80}chart")
        self.assertRegex(normalized_lifecycle, r"(?:trace|verify).{0,80}(?:verified|evidence)")
        self.assertRegex(normalized_lifecycle, r"(?:remove|omit).{0,100}(?:unsupported|nonworking)")
        self.assertIn("placeholder/representative disclosures", lifecycle)
        self.assertIn("preserve verified zero values", normalized_lifecycle)

        for skill_name in ("seller-account-dashboard", "sales-leadership-dashboard"):
            with self.subTest(skill=skill_name):
                instructions = (SKILL_DIRECTORY.parent / skill_name / "SKILL.md").read_text(
                    encoding="utf-8"
                )
                self.assertIn("verified", instructions.lower())
                self.assertIn("functional", instructions.lower())
                self.assertRegex(instructions.lower(), r"(?:omit|hide).{0,60}unsupported")

    def test_leadership_dashboard_renderer_owns_interactive_final_artifact(self) -> None:
        instructions = (
            SKILL_DIRECTORY.parent / "sales-leadership-dashboard" / "SKILL.md"
        ).read_text(encoding="utf-8")
        lowered = instructions.lower()
        self.assertIn("once the production renderer succeeds", lowered)
        self.assertIn("never directly", lowered)
        self.assertIn("apply_patch", instructions)
        self.assertIn("hand-write, delete, or replace", lowered)
        self.assertIn("refine only the verified payload", lowered)
        self.assertIn("rerun the exact production renderer", lowered)
        self.assertIn("salesforce_mcp_soql_query", instructions)
        self.assertIn("invoke the official", lowered)
        self.assertIn("seller growth unavailable", lowered)
        self.assertIn("prior snapshots", lowered)
        self.assert_contains(
            instructions,
            "#accountFocusList [data-account-id]",
            "#account-focus-search",
            "#account-focus-search-clear",
            "#account-drawer",
            "#accountFocusDetail",
            "#account-drawer-close",
        )

    def test_existing_unpublished_dashboard_is_chosen_before_goals_without_duplication(
        self,
    ) -> None:
        lifecycle = (SKILL_DIRECTORY.parent.parent / "references/dashboard-lifecycle.md").read_text(
            encoding="utf-8"
        )
        orientation = lifecycle.partition("## Orient The User And Establish Their Goal")[
            2
        ].partition("## Select A Design Direction")[0]
        normalized_orientation = orientation.lower()

        for choice in ("Use existing (Recommended)", "Modify existing", "Create new"):
            with self.subTest(choice=choice):
                self.assertIn(choice, orientation)
                self.assertLess(
                    orientation.index(choice),
                    orientation.index(
                        "When the user has not already clearly supplied one primary goal"
                    ),
                )

        self.assertIn("unpublished", normalized_orientation)
        self.assertIn("local", normalized_orientation)
        self.assertIn("request_user_input", orientation)
        self.assertIn("exactly three", orientation)
        self.assertIn("automatically", orientation)
        self.assertIn("Other", orientation)
        for identity in ("viewer", "persona", "target", "scope", "mode"):
            with self.subTest(identity=identity):
                self.assertIn(identity, normalized_orientation)
        self.assert_matches(
            normalized_orientation,
            r"(?:published.{0,100}reuse|reuse.{0,100}published)",
            r"(?:explicit.{0,100}(?:new|duplicate)|(?:new|duplicate).{0,100}explicit)",
        )

    def test_existing_dashboard_picker_requires_a_verified_unpublished_match(self) -> None:
        lifecycle = (SKILL_DIRECTORY.parent.parent / "references/dashboard-lifecycle.md").read_text(
            encoding="utf-8"
        )
        sources = {"shared lifecycle": lifecycle}
        for skill_name in ("seller-account-dashboard", "sales-leadership-dashboard"):
            sources[skill_name] = (SKILL_DIRECTORY.parent / skill_name / "SKILL.md").read_text(
                encoding="utf-8"
            )

        for name, instructions in sources.items():
            with self.subTest(source=name):
                self.assertIn(
                    "only after exactly one matching unpublished dashboard is verified "
                    "or authoritatively identified",
                    instructions,
                )
                self.assertIn("If no matching dashboard exists, skip this question", instructions)

        self.assertIn("a matching published Site do not imply an existing unpublished", lifecycle)
        self.assertIn(
            "A matching published private Site is reused or updated by default", lifecycle
        )

    def test_dashboard_sites_offer_is_exact_private_and_separately_approved(self) -> None:
        lifecycle = (SKILL_DIRECTORY.parent.parent / "references/dashboard-lifecycle.md").read_text(
            encoding="utf-8"
        )
        publication_prompt = (
            "Would you like me to publish it with the Sites feature so you can access it "
            "from the web?"
        )

        self.assertIn(publication_prompt, lifecycle)
        self.assertIn("published only with permission", lifecycle)
        self.assertIn("private", lifecycle.lower())
        self.assertIn("explicit", lifecycle.lower())
        self.assertIn("Publishing always requires its own separate explicit approval", lifecycle)
        self.assertIn("local-first preference overrides", lifecycle)
        self.assertLess(
            lifecycle.index("actual working local dashboard"), lifecycle.index(publication_prompt)
        )

    def test_dashboard_browser_handoff_checks_interactions_animation_and_reduced_motion(
        self,
    ) -> None:
        lifecycle = (SKILL_DIRECTORY.parent.parent / "references/dashboard-lifecycle.md").read_text(
            encoding="utf-8"
        )
        handoff = lifecycle.partition("## Verify Every Visible Element Before Handoff")[2].lower()

        self.assert_contains(
            handoff,
            "browser",
            "navigation",
            "tab",
            "button",
            "search",
            "filter",
            "sort",
            "drawer",
            "popover",
            "escape",
            "focus",
            "responsive",
            "smooth",
            "animation",
        )
        self.assertRegex(handoff, r"reduced[ -]motion")
        self.assertIn("remove unsupported or nonworking", handoff)

    def test_customer_facing_presentation_requests_route_through_the_sales_index(self) -> None:
        sales_index = (SKILL_DIRECTORY.parent / "index" / "SKILL.md").read_text(encoding="utf-8")
        presentation_metadata = (
            SKILL_DIRECTORY.parent / "sales-presentations" / "agents" / "openai.yaml"
        ).read_text(encoding="utf-8")

        self.assert_contains(
            sales_index,
            "sales presentations",
            "customer-facing slides",
            "PowerPoint",
            "Google Slides",
        )

        self.assertIn("allow_implicit_invocation: false", presentation_metadata)

    def test_complete_customer_fact_packet_routes_to_sales_presentation_owner_first(
        self,
    ) -> None:
        sales_index = (SKILL_DIRECTORY.parent / "index" / "SKILL.md").read_text(encoding="utf-8")
        presentation = (SKILL_DIRECTORY.parent / "sales-presentations" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        presentation_description = next(
            line for line in presentation.splitlines() if line.startswith("description:")
        )

        self.assertIn("complete user-supplied customer fact packet", presentation_description)
        self.assertIn("standalone buyer-ready decision deck", presentation_description)
        self.assertIn("without new seller analysis", presentation_description)
        self.assertIn("complete user-supplied customer fact packet", sales_index)
        self.assertIn("is owned by `sales-presentations`", sales_index)
        self.assertIn("`skills/sales-presentations/SKILL.md` by itself in full", sales_index)
        self.assertIn("before reading the generic Presentations authoring skill", sales_index)
        self.assertIn("or selecting `build-business-case`", sales_index)

    def test_sales_index_description_stays_compact_while_covering_commercial_artifacts(
        self,
    ) -> None:
        sales_index = (SKILL_DIRECTORY.parent / "index" / "SKILL.md").read_text(encoding="utf-8")
        description = next(
            line for line in sales_index.splitlines() if line.startswith("description:")
        )

        self.assertLessEqual(len(description.split()), 70)
        self.assertIn("customer- and revenue-facing work", description)
        self.assertIn("sales presentations", description)
        self.assertIn("customer-facing slides", description)

    def test_business_case_decision_deck_loads_its_seller_owner_before_presentations(self) -> None:
        business_case = (SKILL_DIRECTORY.parent / "build-business-case" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        presentation = (SKILL_DIRECTORY.parent / "sales-presentations" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        business_description = next(
            line for line in business_case.splitlines() if line.startswith("description:")
        )
        presentation_description = next(
            line for line in presentation.splitlines() if line.startswith("description:")
        )

        self.assertIn("turn customer ROI analysis into a decision deck", business_description)
        self.assertIn("buyer-ready decision-deck development", presentation_description)
        self.assertIn("belong to their respective seller workflows", presentation_description)
        self.assertIn(
            "already completed meeting brief or approved customer proposal",
            presentation_description,
        )
        self.assertNotIn("## Explicit Decision Deck Routing", business_case)
        self.assertIn("### 6. Build the Decision Deck", business_case)
        self.assertIn(
            "this selected business-case skill remains the seller-workflow owner", business_case
        )
        self.assertIn("Read and follow [Sales Presentations]", business_case)
        self.assertIn("as the downstream presentation partner", business_case)
        self.assertIn("before a substantive final response", business_case)
        self.assertIn("If the user accepts a deck offer after the case is complete", business_case)

    def test_meeting_and_call_readout_decks_route_from_descriptions_then_compose(self) -> None:
        for skill_name, description_cue, execution_heading, removed_heading in (
            (
                "prepare-for-meeting",
                "customer-facing presentation or deck for a first call",
                "### Requested Meeting Documents And Decks",
                "## Explicit Meeting Deck Routing",
            ),
            (
                "follow-up-after-call",
                "completed-call discovery, pilot, evaluation, or customer-readout deck",
                "### 5. Build the Customer Readout Deck",
                "## Explicit Customer Readout Routing",
            ),
        ):
            with self.subTest(skill=skill_name):
                instructions = (SKILL_DIRECTORY.parent / skill_name / "SKILL.md").read_text(
                    encoding="utf-8"
                )
                description = next(
                    line for line in instructions.splitlines() if line.startswith("description:")
                )
                self.assertIn(description_cue, description)
                self.assertIn(execution_heading, instructions)
                self.assertNotIn(removed_heading, instructions)
                self.assertIn("Read and follow [Sales Presentations]", instructions)
                self.assertIn("as the downstream presentation partner", instructions)
                self.assertIn("before a substantive final response", instructions)
                self.assertIn("remains the seller-workflow owner", instructions)

    def test_contact_discovery_and_outreach_drafting_have_distinct_focused_owners(self) -> None:
        enrichment = (
            SKILL_DIRECTORY.parent / "enrich-company-and-contact-data" / "SKILL.md"
        ).read_text(encoding="utf-8")
        company_research = (
            SKILL_DIRECTORY.parent / "sales-company-research" / "SKILL.md"
        ).read_text(encoding="utf-8")
        enrichment_description = next(
            line for line in enrichment.splitlines() if line.startswith("description:")
        )
        research_description = next(
            line for line in company_research.splitlines() if line.startswith("description:")
        )

        self.assertIn("who to reach out to at a prospective customer", enrichment_description)
        self.assertIn("when the person or role must first be identified", enrichment_description)
        self.assertIn("an already known customer, recipient, or audience", research_description)
        self.assertIn("Exclude who-to-contact discovery", research_description)

    def test_every_non_index_sales_skill_requires_explicit_selection(self) -> None:
        skills_directory = SKILL_DIRECTORY.parent
        index_metadata = (skills_directory / "index" / "agents" / "openai.yaml").read_text(
            encoding="utf-8"
        )

        self.assertIn("allow_implicit_invocation: true", index_metadata)

        for focused_skill in sorted(skills_directory.glob("*/SKILL.md")):
            skill_name = focused_skill.parent.name
            if skill_name == "index":
                continue

            metadata = (focused_skill.parent / "agents" / "openai.yaml").read_text(encoding="utf-8")
            with self.subTest(skill_name=skill_name):
                self.assertIn("allow_implicit_invocation: false", metadata)

    def test_enrichment_discloses_approval_before_provider_credit_spending(self) -> None:
        enrichment = (
            SKILL_DIRECTORY.parent / "enrich-company-and-contact-data" / "SKILL.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Obtain explicit approval before any credit-consuming", enrichment)
        self.assertIn("explicitly state in the final response", enrichment)
        self.assertIn("Do not run any credit-consuming search, export, enrichment", enrichment)
        self.assertIn(
            "personal-contact access without the user's prior explicit approval", enrichment
        )

    def test_sales_shared_instruction_links_point_to_existing_headings(self) -> None:
        plugin = SKILL_DIRECTORY.parent.parent

        for markdown in sorted(plugin.rglob("*.md")):
            for target in re.findall(
                r"\[[^\]]+\]\(([^)]+)\)", markdown.read_text(encoding="utf-8")
            ):
                if "shared_skill_instructions.md" not in target and "dependencies.md" not in target:
                    continue
                relative_path, _, heading = target.partition("#")
                destination = (markdown.parent / relative_path).resolve()
                with self.subTest(source=markdown.relative_to(plugin), target=target):
                    self.assertTrue(destination.is_file())
                    if not heading:
                        continue
                    headings = re.findall(
                        r"^#{1,6}\s+(.+?)\s*$",
                        destination.read_text(encoding="utf-8"),
                        re.MULTILINE,
                    )
                    anchors = {
                        re.sub(r"[^\w\s-]", "", title.lower()).strip().replace(" ", "-")
                        for title in headings
                    }
                    self.assertIn(heading, anchors)

    def test_direct_sales_presentations_invocation_preserves_index_first(self) -> None:
        presentation = (SKILL_DIRECTORY.parent / "sales-presentations" / "SKILL.md").read_text(
            encoding="utf-8"
        )

        presentation_description = next(
            line for line in presentation.splitlines() if line.startswith("description:")
        )
        self.assertIn(
            "explicitly requested customer-facing PowerPoint or Google Slides",
            presentation_description,
        )
        self.assertNotIn("Sales index", presentation_description)
        self.assertNotRegex(presentation_description, r"\b(?:load|read|invoke)\b")
        index_instruction = "read [the Sales index](../index/SKILL.md)"
        shared_instruction = (
            "[the shared Sales skill instructions](../../shared_skill_instructions.md)"
        )
        self.assertIn(index_instruction, presentation)
        self.assertIn("then reread this focused skill in full", presentation)
        self.assertLess(
            presentation.index(index_instruction), presentation.index(shared_instruction)
        )
        self.assertIn("use the native plugin-install surface when available", presentation)
        self.assertIn("Never recover an excluded plugin from a global cache", presentation)

    def test_declined_calendar_install_uses_bounded_native_fallback(self) -> None:
        meeting = (SKILL_DIRECTORY.parent / "prepare-for-meeting" / "SKILL.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("If installation is unavailable or declined", meeting)
        self.assertIn("follow [User Input](../../shared_skill_instructions.md#user-input)", meeting)
        self.assertIn("when `request_user_input` is available", meeting)
        self.assertIn("offer two or three likely ways to identify the meeting", meeting)
        self.assertIn("never repeat a declined installation offer", meeting)

    def test_user_supplied_meeting_identity_has_explicit_source_label(self) -> None:
        meeting = (SKILL_DIRECTORY.parent / "prepare-for-meeting" / "SKILL.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("**Meeting source:**", meeting)
        self.assertIn("User-supplied meeting identity; not Calendar-verified", meeting)
        self.assertIn("even when a later email or message corroborates", meeting)
        self.assertIn("PROVENANCE HARD REQUIREMENT", meeting)
        self.assertIn("must begin with the exact words", meeting)
        self.assertIn("cite it after the required label, never instead of it", meeting)
        self.assertIn("only when no Calendar event was directly read", meeting)
        self.assertIn("cite it beside the date and omit the separate source line", meeting)


class MeetingPrepOutputTests(SalesTestCase):
    def setUp(self) -> None:
        self.meeting = (SKILL_DIRECTORY.parent / "prepare-for-meeting" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.single = self.meeting.split("### 1. Single Meeting Prep\n", 1)[1].split(
            "\n### 3. Customer Presentation", 1
        )[0]
        self.template = self.single.split("```md\n", 1)[1].split("\n```", 1)[0]

    def test_nvidia_walkthrough_golden_has_the_preferred_brief_structure(self) -> None:
        # Regression for meeting-prep-nvidia-data-analytics-walkthrough-golden.
        # Fix the presentation contract without baking customer answers into the skill.
        self.assertEqual(
            re.findall(r"^## (.+)$", self.template, re.MULTILINE),
            [
                "Summary",
                "Goal",
                "Recommended walkthrough spine",
                "Open questions",
                "Proposed 30-minute agenda",
                "People to lean on",
                "Recommended posture",
                "Confidence and gaps",
            ],
        )
        spine = self.template.split("## Recommended walkthrough spine\n", 1)[1].split(
            "\n## Open questions", 1
        )[0]
        self.assertRegex(spine, r"(?m)^> \[One customer-specific storyline")
        self.assertEqual(len(re.findall(r"^- \[Sourced ", spine, re.MULTILINE)), 2)
        self.assertIn("**[Person]:** [Sourced role/contribution", self.template)
        self.assertNotIn("## Background Context", self.template)

    def test_agenda_is_spaced_timed_and_adapts_to_the_invite(self) -> None:
        agenda = self.template.split("## Proposed 30-minute agenda\n", 1)[1].split(
            "\n## People to lean on", 1
        )[0]
        stages = re.findall(
            r"(?m)^(\d)\. \*\*(\d+)–(\d+) min — [^\n]+\*\*\n   \[[^\n]+\]\n",
            agenda,
        )
        self.assertEqual(
            stages,
            [
                ("1", "0", "3"),
                ("2", "3", "8"),
                ("3", "8", "18"),
                ("4", "18", "25"),
                ("5", "25", "30"),
            ],
        )
        self.assertIn(
            "Adapt the heading, timing, and stage count to the actual invite", self.single
        )
        self.assertIn("If the duration is unknown", self.single)
        self.assertIn("label any suggested duration as a proposal", self.single)

    def test_optional_sections_and_metadata_do_not_leak_into_other_modes(self) -> None:
        metadata = self.template.split("\n## Summary", 1)[0]
        self.assertEqual(
            re.findall(r"^\*\*([^*]+):\*\*", metadata, re.MULTILINE),
            ["Date", "Attendees"],
        )
        self.assertIn("Omit this section for other meetings", self.single)
        self.assertIn("only when evidence supports the named attendees' roles", self.single)
        self.assertIn("do not infer roles from attendance alone", self.single)
        self.assertIn("do not add separate Format, Accepted, or Declined fields", self.single)
        self.assertIn("without installing or querying an unnecessary provider", self.single)

        digest = self.meeting.split("### 2. Daily Prep Digest\n", 1)[1]
        for heading in ("## Today's Meetings", "## Priority Watchouts"):
            self.assertIn(heading, digest)
        for label in ("Goal", "Key context", "Watchout", "Suggested close"):
            self.assertIn(f"**{label}:**", digest)
        self.assertNotIn("Recommended walkthrough spine", digest)
        self.assertIn("no external meeting qualifies, or the workflow is blocked", self.meeting)

    def test_richer_format_preserves_cutoffs_provenance_and_deck_contract(self) -> None:
        self.assert_contains(
            self.meeting,
            "exact Calendar event ID or link, read that event directly",
            "do not run a broad event search",
            "When the user supplies an effective or as-of time",
            "before:<Unix epoch seconds>",
            "CreatedDate <= <as-of instant>",
            "LastModifiedDate <= <as-of instant>",
            "artifacts created after the effective time are unavailable",
            "next 3 business days, with 25 max results",
            "do not let an unrelated same-account opportunity drive the brief",
            "Always cite sources using hyperlinks",
            "artifact is the first deliverable",
            "reading back the finished document or deck",
            "Would you like me to turn this into a 6–9 slide customer presentation using @presentations?",
            "do not append a competing automation or document offer",
        )


if __name__ == "__main__":
    unittest.main()
