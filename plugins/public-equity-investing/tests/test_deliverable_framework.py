"""Regression checks for the Public Equity Investing deliverable framework."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from shared.dashboard.qa import validate_payload  # noqa: E402
from shared.dashboard.renderer import render_dashboard  # noqa: E402

DASHBOARD_PACK_SKILLS = [
    "company-tearsheet",
    "comps-valuation",
    "deck-report-qc",
    "earnings-deep-dive",
    "earnings-preview",
    "economic-impact-report",
    "event-driven-analyzer",
    "portfolio-risk-management",
    "idea-generation",
    "initiating-coverage",
    "long-short-pitch",
    "meeting-prep",
    "memo-builder",
    "equity-model-update",
    "scenario-sensitivity-generator",
    "thesis-tracker",
]

DASHBOARD_SAMPLE_PAYLOADS = [
    "comps-valuation-sample.json",
    "initiating-coverage-sample.json",
    "idea-generation-sample.json",
    "portfolio-sizing-mode-sample.json",
    "scenario-sensitivity-sample.json",
    "portfolio-hedge-mode-sample.json",
    "deck-report-qc-sample.json",
    "hero-citations-sample.json",
    "production-complete-sample.json",
]

INTAKE_OWNER_SKILLS = [
    "catalyst-calendar",
    "company-tearsheet",
    "comps-valuation",
    "dcf-model-builder",
    "earnings-deep-dive",
    "earnings-preview",
    "economic-impact-report",
    "equity-model-update",
    "event-driven-analyzer",
    "portfolio-risk-management",
    "idea-generation",
    "initiating-coverage",
    "long-short-pitch",
    "meeting-prep",
    "memo-builder",
    "model-audit-tieout",
    "scenario-sensitivity-generator",
    "thesis-tracker",
    "three-statement-model-builder",
]

INTAKE_SUPPORT_SKILLS = [
    "dashboard-builder",
    "deck-report-qc",
    "excel-data-cleaner",
    "financial-source-of-truth",
    "financials-normalizer",
    "style-guide-adapter",
]

ARTIFACT_OWNING_SKILLS = {
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

INTERNAL_SUPPORT_PLAYBOOKS = {
    "daloopa-provider-guide",
    "dashboard-builder",
    "excel-data-cleaner",
    "financial-source-of-truth",
    "quartr-provider-guide",
    "sector-context-overlay",
    "style-guide-adapter",
}
INTERNAL_SUPPORT_PATH = "skills/public-equity-investing/internal-support"


def read(relative_path: str | Path) -> str:
    path = Path(relative_path)
    if not path.is_absolute():
        path = ROOT / path
    return path.read_text(encoding="utf-8")


def load_json(relative_path: str) -> dict[str, object]:
    return json.loads(read(relative_path))


def minimal_dashboard_payload() -> dict[str, object]:
    return {
        "kind": "public_equity_investing_dashboard.v1",
        "title": "Issuer dashboard",
        "issuer": {"ticker": "ACME"},
        "tabs": [
            {
                "id": "overview",
                "label": "Overview",
                "modules": [
                    {"type": "decision_box", "data": {"stance": "Watch"}},
                ],
            }
        ],
        "sources": [{"id": "S1", "title": "Company release"}],
    }


def _payload_has_module(payload: dict[str, object], module_type: str) -> bool:
    tabs = payload.get("tabs")
    if not isinstance(tabs, list):
        return False
    for tab in tabs:
        if not isinstance(tab, dict):
            continue
        modules = tab.get("modules")
        if not isinstance(modules, list):
            continue
        for module in modules:
            if isinstance(module, dict) and module.get("type") == module_type:
                return True
    return False


class DeliverableFrameworkTests(unittest.TestCase):
    def test_shared_framework_defines_artifact_lanes(self) -> None:
        text = read("shared/final-deliverable-framework.md")

        for phrase in [
            "HTML dashboard or report",
            "XLSX workbook",
            "Concise chat answer",
            "Support and audit files",
            "HTML recommendation triggers",
            "Full-depth default",
            "Citation standard",
            "Workbook cover standard",
        ]:
            self.assertIn(phrase, text)

        self.assertIn(
            "Markdown, raw JSON, CSV, manifests, run logs, and plan files are not the default user-facing deliverable",
            text,
        )

    def test_html_artifacts_verify_headline_market_data_anchor(self) -> None:
        standard = read("shared/html-artifact-standard.md")

        for phrase in [
            "market price, return, multiple, or market-derived value",
            "hero card, headline KPI, or decision conclusion",
            "correct issuer, security, or ticker",
            "applicable as-of date",
            "omit the figure from the headline view or label it unavailable",
        ]:
            self.assertIn(phrase, standard)

    def test_adaptive_deliverable_intake_policy_defines_tool_and_fallback_rules(self) -> None:
        policy = read("shared/deliverable-intake-policy.md")

        for phrase in [
            "request_user_input",
            "no more than three questions",
            "free-form `Other` response automatically",
            "never include an",
            "normal chat and wait",
            "non-interactive run",
            "preserve",
            "do not ask again",
            "Excel workbook (.xlsx) (Recommended)",
            "Full working analysis (Recommended)",
            "Depth is not readiness",
            "concise plain-text",
            "do not silently select depth or audience",
            "ask the grouped questions directly",
            "Do not suggest switching products or modes",
            "substantive 60/90-day catalyst calendar",
            "polished standalone HTML artifact",
            "Presentation-Surface Precedence",
            "Apply a saved reader-facing output preference as the default",
            "Otherwise, resolve any new standalone reader-facing output to polished standalone HTML",
            "Use chat-only output only when the user explicitly requests",
            "A direct analytical question, a detail-page hero prompt",
            "Do not choose chat-only output because a concise answer seems sufficient or more useful",
            "Once the presentation surface resolves to HTML, treat that as a committed deliverable decision",
            "do not later reconsider whether the analysis belongs in chat",
        ]:
            self.assertIn(phrase, policy)
        self.assertNotIn("as a bias only", policy)

        framework = read("shared/final-deliverable-framework.md")
        self.assertIn("Do not infer chat-only intent from direct question wording", framework)
        self.assertIn("Do not reopen the presentation decision after source gathering or analysis", framework)
        self.assertNotIn("or one narrow event/section", framework)

    def test_artifact_owning_skills_declare_natural_artifact_and_shared_precedence(self) -> None:
        visible_skills = {path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")}
        self.assertEqual(
            ARTIFACT_OWNING_SKILLS,
            visible_skills - {"public-equity-investing", "user-context"},
        )

        for skill in ARTIFACT_OWNING_SKILLS:
            with self.subTest(skill=skill):
                text = read(f"skills/{skill}/SKILL.md")
                self.assertIn("Apply the presentation-surface precedence", text)
                self.assertIn("../../shared/deliverable-intake-policy.md", text)
                self.assertIn("This workflow's natural artifact is", text)
                self.assertIn(
                    "Do not choose chat-only output unless the user explicitly requests a lightweight response.",
                    text,
                )

    def test_intake_policy_is_wired_to_framework(self) -> None:
        framework = read("shared/final-deliverable-framework.md")

        self.assertIn("shared/deliverable-intake-policy.md", framework)

    def test_default_prompts_showcase_onboarding_earnings_and_theme_screening(self) -> None:
        default_prompts = load_json(".codex-plugin/plugin.json")["interface"]["defaultPrompt"]

        self.assertTrue(all(len(prompt) <= 128 for prompt in default_prompts))
        self.assertEqual(
            default_prompts,
            [
                "Help me get started",
                "Analyze Apple's latest earnings: what changed, what is priced in, and what should an investor watch next",
                "Screen listed-equity beneficiaries of AI data-center power demand and rank the best ideas, risks, and false positives",
            ],
        )

    def test_artifact_owners_use_preflight_and_support_skills_inherit_preferences(self) -> None:
        for skill in INTAKE_OWNER_SKILLS:
            text = read(f"skills/{skill}/SKILL.md")
            self.assertIn("../../shared/deliverable-intake-policy.md", text, skill)
            self.assertIn("request_user_input", text, skill)
            self.assertIn("Before source gathering or analysis", text, skill)

        for skill in INTAKE_SUPPORT_SKILLS:
            relative_path = (
                f"{INTERNAL_SUPPORT_PATH}/{skill}/INTERNAL.md"
                if skill in INTERNAL_SUPPORT_PLAYBOOKS
                else f"skills/{skill}/SKILL.md"
            )
            text = read(relative_path)
            self.assertIn("../../shared/deliverable-intake-policy.md", text, skill)
            self.assertIn("do not re-prompt", text, skill)
            self.assertIn("before source gathering", text, skill)

        overlay = read(f"{INTERNAL_SUPPORT_PATH}/sector-context-overlay/INTERNAL.md")
        self.assertIn("does not own a hero deliverable", overlay)
        self.assertIn("do not call `request_user_input` independently", overlay)

    def test_model_explicit_html_existing_workbook_and_reuse_scenarios_are_covered(self) -> None:
        policy = read("shared/deliverable-intake-policy.md")
        model = read("skills/dcf-model-builder/SKILL.md")

        self.assertIn("model or valuation-package request", policy)
        self.assertIn("Excel workbook (.xlsx)", policy)
        self.assertIn("explicit HTML research report request skips the format question", policy)
        self.assertIn("Duolingo's stock has plummeted since last May", policy)
        self.assertIn("resolves Word format only", policy)
        self.assertIn("unresolved depth and audience", policy)
        self.assertIn("review of an existing workbook preserves `.xlsx`", policy)
        self.assertIn("without repeated prompts", policy)
        self.assertIn("../../shared/deliverable-intake-policy.md", model)

    def test_new_research_and_model_work_start_with_intake(self) -> None:
        framework = read("shared/final-deliverable-framework.md")
        policy = read("shared/deliverable-intake-policy.md")

        self.assertIn("Before source gathering", policy)
        self.assertIn("begins source gathering or analysis", framework)

    def test_implicit_invocation_is_limited_to_the_guarded_router(self) -> None:
        policy = read("shared/invocation-policy.md")
        framework = read("shared/final-deliverable-framework.md")
        router = read("skills/public-equity-investing/SKILL.md")

        for phrase in [
            "Explicit invocation",
            "Perfect-fit mandate",
            "do not activate",
            "A public company name by itself is not sufficient",
        ]:
            self.assertIn(phrase, policy)
        self.assertIn("shared/invocation-policy.md", framework)
        self.assertIn("shared/invocation-policy.md", router)

        skill_names = {path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")}
        yaml_paths = sorted((ROOT / "skills").glob("*/agents/openai.yaml"))
        self.assertEqual(skill_names, {path.parents[1].name for path in yaml_paths})
        for path in yaml_paths:
            skill = path.parents[1].name
            expected = skill == "public-equity-investing"
            with self.subTest(skill=skill):
                self.assertIn(
                    f"allow_implicit_invocation: {str(expected).lower()}",
                    read(path),
                )

    def test_router_resolves_bundled_paths_from_the_plugin_root(self) -> None:
        router_path = ROOT / "skills" / "public-equity-investing" / "SKILL.md"
        router = router_path.read_text(encoding="utf-8")

        self.assertIn("Derive the plugin root once", router)
        self.assertIn("Set the shell working directory to that plugin root", router)
        self.assertIn("Do not apply `../..` to an already resolved plugin root", router)
        for relative_path in [
            "shared/invocation-policy.md",
            "shared/final-deliverable-framework.md",
            "shared/deliverable-intake-policy.md",
            "skills/user-context/SKILL.md",
            "skills/public-equity-investing/internal-support/policy.md",
        ]:
            with self.subTest(relative_path=relative_path):
                self.assertIn(relative_path, router)
                self.assertTrue((ROOT / relative_path).resolve().exists())

    def test_router_selects_lead_skill_without_resolving_presentation(self) -> None:
        router = read("skills/public-equity-investing/SKILL.md")
        invocation_policy = read("shared/invocation-policy.md")

        for phrase in [
            "Pass relevant entries from `saved_context` to the selected lead skill as handoff context",
            "must not interpret saved output preferences",
            "The router owns admission and lead-skill selection only",
            "load `skills/<lead-skill>/SKILL.md` from the plugin root before source gathering",
            "must not continue substantive work as a substitute for the selected owner",
            "without choosing or announcing format, depth, artifact architecture",
            "The selected owner applies `shared/final-deliverable-framework.md`",
            "reads `shared/deliverable-intake-policy.md`",
        ]:
            self.assertIn(phrase, router)
        self.assertIn("The selected lead workflow, not the router", invocation_policy)
        self.assertNotIn("must not be downgraded to chat-only output", router)

    def test_internal_support_playbooks_are_packaged_but_not_visible_skills(self) -> None:
        policy = read(f"{INTERNAL_SUPPORT_PATH}/policy.md")
        router = read("skills/public-equity-investing/SKILL.md")
        visible = {path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")}

        self.assertEqual(23, len(visible))
        self.assertIn("internal-support/policy.md", router)
        for skill in INTERNAL_SUPPORT_PLAYBOOKS:
            self.assertNotIn(skill, visible)
            self.assertIn(f"internal-support/{skill}/INTERNAL.md", policy)
            self.assertTrue((ROOT / INTERNAL_SUPPORT_PATH / skill / "INTERNAL.md").exists())
            self.assertFalse((ROOT / "skills" / skill / "SKILL.md").exists())

    def test_visible_workflows_that_name_internal_capabilities_resolve_policy(self) -> None:
        internal_labels = INTERNAL_SUPPORT_PLAYBOOKS
        for path in (ROOT / "skills").glob("*/SKILL.md"):
            text = read(path)
            if not any(label in text for label in internal_labels):
                continue
            self.assertTrue(
                "internal-support/policy.md" in text
                or "public-equity-investing" in text
                or "support-layer-routing-contract.md" in text
                or "final-deliverable-framework.md" in text,
                path.parent.name,
            )

    def test_provider_guides_load_only_for_callable_selected_routes(self) -> None:
        text = read("shared/workflow-source-resolution.md")
        self.assertIn("Do not load provider guides merely because `.app.json` declares", text)
        for provider in ["daloopa", "quartr"]:
            with self.subTest(provider=provider):
                self.assertIn(
                    f"skills/public-equity-investing/internal-support/{provider}-provider-guide/INTERNAL.md",
                    text,
                )
                self.assertNotIn(
                    f"../skills/public-equity-investing/internal-support/{provider}-provider-guide/INTERNAL.md",
                    text,
                )
                guide_root = ROOT / INTERNAL_SUPPORT_PATH / f"{provider}-provider-guide"
                internal = read(guide_root / "INTERNAL.md")
                self.assertIn("references/connector-playbook.md", internal)
                self.assertIn("references/workbook-mode.md", internal)
                self.assertTrue((guide_root / "references" / "connector-playbook.md").exists())
                self.assertTrue((guide_root / "references" / "workbook-mode.md").exists())

    def test_no_legacy_markdown_or_chat_default_wording(self) -> None:
        docs = [
            ROOT / "shared/final-deliverable-framework.md",
            *ROOT.glob("skills/*/SKILL.md"),
            *ROOT.glob(f"{INTERNAL_SUPPORT_PATH}/*/INTERNAL.md"),
            *ROOT.glob("skills/*/references/*.md"),
        ]
        forbidden_patterns = [
            r"chat-first",
            r"markdown-first",
            r"full markdown",
            r"full\s+[a-z -]*markdown",
            r"default chat",
            r"default deliverable:.*markdown",
            r"generated user-facing markdown",
            r"return a full markdown",
            r"markdown report",
            r"markdown-led",
            r"markdown as final",
            r"markdown file as final",
            r"rendered in chat",
            r"paste .*verbatim",
            r"user-facing markdown",
            r"final markdown",
            r"csv/markdown bundle",
            r"structured json handoff",
            r"use this only when .*asks.*dashboard",
        ]

        failures: list[str] = []
        for relative_path in docs:
            text = read(str(relative_path)).lower()
            for pattern in forbidden_patterns:
                if re.search(pattern, text):
                    failures.append(f"{relative_path}: {pattern}")

        self.assertEqual([], failures)

    def test_dashboard_defaults_cover_substantial_public_equity_investing_workflows(self) -> None:
        expectations = {
            "skills/catalyst-calendar/SKILL.md": [
                "recommended presentation path",
                "in interactive runs",
                "in non-interactive runs",
                "explicitly asks for a standardized dashboard",
            ],
            "skills/earnings-preview/SKILL.md": [
                "polished standalone html pre-earnings report",
                "explicitly asks for a standardized dashboard",
            ],
            "skills/earnings-deep-dive/SKILL.md": [
                "polished standalone html post-earnings report",
                "explicitly asks for a standardized dashboard",
            ],
            "skills/memo-builder/SKILL.md": [
                "polished standalone html investment committee memo",
                "explicitly asks for a standardized dashboard",
            ],
            "skills/comps-valuation/SKILL.md": [
                "polished standalone html comps report",
                "explicitly asks for a standardized dashboard",
            ],
            "skills/event-driven-analyzer/SKILL.md": [
                "polished standalone html event report",
                "explicitly asks for a standardized dashboard",
            ],
            "skills/idea-generation/SKILL.md": [
                "polished standalone html idea-triage report",
                "explicitly asks for a standardized dashboard",
            ],
            "skills/initiating-coverage/SKILL.md": [
                "polished standalone html initiation report",
                "explicitly asks for a standardized dashboard",
            ],
            "skills/portfolio-risk-management/SKILL.md": [
                "polished standalone html risk decision report",
                "explicitly asks for a standardized dashboard",
            ],
        }

        for relative_path, phrases in expectations.items():
            text = read(relative_path).lower()
            for phrase in phrases:
                self.assertIn(phrase.lower(), text, relative_path)

    def test_memo_builder_uses_standalone_html_with_optional_dashboard(self) -> None:
        skill_doc = read("skills/memo-builder/SKILL.md")
        output_contracts = read("skills/memo-builder/references/output-contracts.md")
        quality_workflow = read("skills/memo-builder/references/quality-workflow.md")
        dashboard_pack = read("skills/memo-builder/references/DASHBOARD_PACK.md")
        intake_policy = read("shared/deliverable-intake-policy.md")

        self.assertIn("../../shared/html-artifact-standard.md", skill_doc)
        self.assertIn("polished standalone HTML investment committee memo", skill_doc)
        self.assertIn("explicitly asks for a standardized dashboard", skill_doc)
        self.assertIn("Do not repeat the same recommendation", skill_doc)
        self.assertIn("do not fragment tickers, prices, EPS ranges", skill_doc)
        self.assertIn("local headless-browser screenshots", skill_doc)
        self.assertIn("annualized return / IRR versus a stated hurdle", skill_doc)
        self.assertIn(
            "sufficient to decline initiation today; insufficient to support initiation", skill_doc
        )
        self.assertIn("Standalone HTML Investment Committee Memo", output_contracts)
        self.assertIn("Do not repeat the same recommendation", output_contracts)
        self.assertIn("undiscounted terminal value appreciation", output_contracts)
        self.assertIn("insufficient to support initiation", output_contracts)
        self.assertIn("undiscounted terminal price appreciation", quality_workflow)
        self.assertIn("return hurdle / IRR framing", quality_workflow)
        self.assertIn("Use this pack only when", dashboard_pack)
        self.assertIn("citation rendering remains readable", dashboard_pack)
        self.assertIn("polished standalone HTML investment committee memo", intake_policy)

    def test_initiating_coverage_uses_standalone_html_with_financed_growth_gate(self) -> None:
        skill_doc = read("skills/initiating-coverage/SKILL.md")
        architecture = read("skills/initiating-coverage/references/report-architecture.md")
        valuation = read("skills/initiating-coverage/references/valuation-and-modeling.md")
        source_evidence = read("skills/initiating-coverage/references/source-and-evidence.md")
        output_templates = read("skills/initiating-coverage/references/output-templates.md")
        quality_checklist = read("skills/initiating-coverage/references/quality-checklist.md")
        dashboard_pack = read("skills/initiating-coverage/references/DASHBOARD_PACK.md")
        intake_policy = read("shared/deliverable-intake-policy.md")

        self.assertIn("../../shared/html-artifact-standard.md", skill_doc)
        self.assertIn("polished standalone HTML initiation report", skill_doc)
        self.assertIn("explicitly asks for a standardized dashboard", skill_doc)
        self.assertIn("pro forma fully diluted capitalization", skill_doc)
        self.assertIn("equity-value-to-revenue", skill_doc)
        self.assertIn("Preliminary initiation underwrite", skill_doc)
        self.assertIn("local headless-browser screenshots", skill_doc)
        self.assertIn("do not fragment tickers, fiscal periods, dates", skill_doc)
        self.assertIn("Complete market data and valuation inputs", skill_doc)
        self.assertIn("Keep evidence confidence distinct from underwriting readiness", skill_doc)
        self.assertIn("Standalone HTML Long-Only Initiation Report", architecture)
        self.assertIn("Capital Return And Funding Gate", architecture)
        self.assertIn("Capital-Intensive And Financed Growth Gate", valuation)
        self.assertIn("after-financing return gate", valuation)
        self.assertIn("Market Data And Valuation Inputs Completion Step", source_evidence)
        self.assertIn("Underwriting status", source_evidence)
        self.assertIn("Standalone HTML Long-Only Initiation Report", output_templates)
        self.assertIn("Pro Forma Net Debt + Recorded Leases", output_templates)
        self.assertIn("capital-intensive or externally financed growth", quality_checklist)
        self.assertIn("Evidence confidence is separate from underwriting status", quality_checklist)
        self.assertIn("Use this pack only when", dashboard_pack)
        self.assertIn("citation rendering remains readable", dashboard_pack)
        self.assertIn("polished standalone HTML initiation report", intake_policy)

    def test_portfolio_risk_management_uses_conditional_standalone_html_risk_plan(self) -> None:
        skill_doc = read("skills/portfolio-risk-management/SKILL.md")
        sizing_framework = read("skills/portfolio-risk-management/references/sizing-framework.md")
        source_protocol = read(
            "skills/portfolio-risk-management/references/source-and-context-protocol.md"
        )
        sizing_templates = read(
            "skills/portfolio-risk-management/references/position-sizing-output-templates.md"
        )
        hedge_workflow = read("skills/portfolio-risk-management/references/hedge-workflow.md")
        hedge_templates = read(
            "skills/portfolio-risk-management/references/hedge-output-templates.md"
        )
        quality_control = read("skills/portfolio-risk-management/references/quality-control.md")
        dashboard_pack = read("skills/portfolio-risk-management/references/DASHBOARD_PACK.md")
        intake_policy = read("shared/deliverable-intake-policy.md")

        self.assertIn("../../shared/html-artifact-standard.md", skill_doc)
        self.assertIn("polished standalone HTML risk decision report", skill_doc)
        self.assertIn("explicitly asks for a standardized dashboard", skill_doc)
        self.assertIn("scenario loss budget", skill_doc)
        self.assertIn("absolute loss cap", skill_doc)
        self.assertIn("Conditional risk screen", skill_doc)
        self.assertIn("local headless-browser screenshots", skill_doc)
        self.assertIn("do not fragment tickers, dates, percentages, basis-point amounts", skill_doc)
        self.assertIn("Absolute loss cap", sizing_framework)
        self.assertIn("Standalone HTML Integrated Risk Decision Report", sizing_templates)
        self.assertIn("Hard-Cap Compliant Package", sizing_templates)
        self.assertIn("one listed call contract per 100 shares short", hedge_workflow)
        self.assertIn("A call spread is not compliant with an absolute cap", hedge_templates)
        self.assertIn("scenario loss budget", source_protocol)
        self.assertIn("Not implementation-ready", quality_control)
        self.assertIn("Use this pack only when", dashboard_pack)
        self.assertIn("citation rendering remains readable", dashboard_pack)
        self.assertIn("polished standalone HTML risk decision report", intake_policy)

    def test_dashboard_citation_contract_remains_compact_and_strict(self) -> None:
        skill = read(
            "skills/public-equity-investing/internal-support/dashboard-builder/INTERNAL.md"
        )
        framework = read("shared/final-deliverable-framework.md")
        renderer = read("shared/dashboard/renderer.py")
        qa = read("shared/dashboard/qa.py")
        browser_js = read("shared/dashboard/assets/dashboard.js")

        for phrase in [
            "Every material number",
            "subtle numeric citation links",
            "section-level source note",
            "click-through to the source ledger",
            "hover/focus previews",
            "no numeric material without inline citation support",
        ]:
            self.assertIn(phrase, skill + framework)

        for phrase in [
            "_link_numeric_text",
            "citation-link",
            "section-citation-note",
            "_find_numeric_citation_gaps",
            "_find_unresolved_citations",
        ]:
            self.assertIn(phrase, renderer + qa)

        self.assertIn("citation-popover", browser_js)

    def test_dashboard_builder_indexes_typed_producer_packs(self) -> None:
        text = read("skills/public-equity-investing/internal-support/dashboard-builder/INTERNAL.md")

        self.assertIn("Producer Pack Index", text)
        self.assertIn("Producer skills own the investment analysis", text)
        self.assertIn("`dashboard-builder` owns the shared shell", text)
        for skill in DASHBOARD_PACK_SKILLS:
            self.assertIn(f"{skill}/references/DASHBOARD_PACK.md", text)
        self.assertNotIn("catalyst-calendar/references/DASHBOARD_PACK.md", text)

    def test_catalyst_calendar_uses_flexible_html_artifact_standard(self) -> None:
        skill_doc = read("skills/catalyst-calendar/SKILL.md")
        standard = read("shared/html-artifact-standard.md")

        self.assertFalse((ROOT / "skills/catalyst-calendar/references/DASHBOARD_PACK.md").exists())
        self.assertIn("../../shared/html-artifact-standard.md", skill_doc)
        self.assertNotIn('Do not wait for the user to say "HTML"', skill_doc)
        self.assertIn(
            "default resolves the presentation surface to a polished HTML catalyst calendar",
            skill_doc,
        )
        self.assertIn(
            "default to the HTML catalyst calendar and `Full working analysis`", skill_doc
        )
        self.assertIn("90-Day Catalyst Calendar", skill_doc)
        self.assertIn("Make the catalyst schedule the primary visual object", skill_doc)
        self.assertIn("month-by-month or time-horizon visual summary", skill_doc)
        self.assertIn("lower-priority confirmed issuer events", skill_doc)
        self.assertIn("Do not show format-selection", skill_doc)
        self.assertIn("Let the requested job determine the hierarchy and layout", standard)
        self.assertIn("Prefer legibility, restrained color", standard)
        self.assertIn("Format assumption", standard)
        self.assertIn("standardized dashboard", standard)

    def test_earnings_deep_dive_uses_flexible_html_with_optional_dashboard(self) -> None:
        skill_doc = read("skills/earnings-deep-dive/SKILL.md")
        standard = read("shared/html-artifact-standard.md")
        output_modes = read("skills/earnings-deep-dive/references/OUTPUT_MODES.md")
        dashboard_pack = read("skills/earnings-deep-dive/references/DASHBOARD_PACK.md")

        self.assertIn("../../shared/html-artifact-standard.md", skill_doc)
        self.assertIn("polished standalone HTML post-earnings report", skill_doc)
        self.assertIn("explicitly asks for a standardized dashboard", skill_doc)
        self.assertIn("do not render an empty Q&A table", skill_doc)
        self.assertIn("4-6 high-signal metric tiles", skill_doc)
        self.assertIn("Prefer 4-5 tiles", skill_doc)
        self.assertIn("Give each first-read element a distinct job", skill_doc)
        self.assertIn(
            "Company release reviewed; filing and transcript confirmation pending", skill_doc
        )
        self.assertIn(
            "Keep citations traceable without making the page read like a control log", standard
        )
        self.assertIn("polished standalone HTML report", output_modes)
        self.assertIn(
            "only when the user explicitly requests the standardized dashboard", output_modes
        )
        self.assertIn("Use this only when", dashboard_pack)
        self.assertIn("Do not render empty scenario cards", dashboard_pack)

    def test_earnings_preview_uses_flexible_html_with_optional_dashboard(self) -> None:
        skill_doc = read("skills/earnings-preview/SKILL.md")
        output_spec = read("skills/earnings-preview/references/OUTPUT_SPEC.md")
        dashboard_pack = read("skills/earnings-preview/references/DASHBOARD_PACK.md")
        reference_router = read("skills/earnings-preview/references/REFERENCE_ROUTER.md")
        qa_rules = read("skills/earnings-preview/references/QA_RULES.md")

        self.assertIn("../../shared/html-artifact-standard.md", skill_doc)
        self.assertIn("polished standalone HTML pre-earnings report", skill_doc)
        self.assertIn("explicitly asks for a standardized dashboard", skill_doc)
        self.assertIn("Lead with the expectation bar and the stock-reaction debate", skill_doc)
        self.assertIn("Do not force a fixed dashboard module inventory", skill_doc)
        self.assertIn("do not fragment dates, times, ticker symbols", skill_doc)
        self.assertIn("workflow-resolved standalone HTML pre-earnings report", skill_doc)
        self.assertIn("expiry-tenor volatility context", skill_doc)
        self.assertIn("polished standalone HTML report", output_spec)
        self.assertIn("expiry-tenor volatility context", output_spec)
        self.assertIn("Use this pack only for", dashboard_pack)
        self.assertIn("expiry-tenor volatility context", dashboard_pack)
        self.assertIn("chart axis or displayed scale", qa_rules)
        self.assertIn("expiry-tenor volatility context", qa_rules)
        self.assertIn("Standalone HTML full preview report", reference_router)

    def test_event_driven_analyzer_uses_flexible_html_with_evidence_staging(self) -> None:
        skill_doc = read("skills/event-driven-analyzer/SKILL.md")
        output_templates = read("skills/event-driven-analyzer/references/output_templates.md")
        dashboard_pack = read("skills/event-driven-analyzer/references/DASHBOARD_PACK.md")

        self.assertIn("../../shared/html-artifact-standard.md", skill_doc)
        self.assertIn("polished standalone HTML event report", skill_doc)
        self.assertIn("explicitly asks for a standardized dashboard", skill_doc)
        self.assertIn("underwriting framework or entry screen", skill_doc)
        self.assertIn("do not make the title more actionable than the evidence", skill_doc)
        self.assertIn("For a spin-off or split-off", skill_doc)
        self.assertIn("Use flexible standalone HTML", output_templates)
        self.assertIn("Use this pack only for", dashboard_pack)
        self.assertIn("Do not use an executable", dashboard_pack)

    def test_idea_generation_uses_flexible_html_with_candidate_funnel(self) -> None:
        skill_doc = read("skills/idea-generation/SKILL.md")
        output_standards = read("skills/idea-generation/references/output-standards.md")
        dashboard_pack = read("skills/idea-generation/references/DASHBOARD_PACK.md")

        self.assertIn("../../shared/html-artifact-standard.md", skill_doc)
        self.assertIn("polished standalone HTML idea-triage report", skill_doc)
        self.assertIn("For a new standalone reader-facing idea screen", skill_doc)
        self.assertNotIn("Treat a thematic screen that asks to rank", skill_doc)
        self.assertIn("explicitly asks for a standardized dashboard", skill_doc)
        self.assertIn("candidate funnel", skill_doc)
        self.assertIn("expectations-heavy", skill_doc)
        self.assertIn("needs exposure attribution", skill_doc)
        self.assertIn("research-priority status, not an investment recommendation", skill_doc)
        self.assertIn("Keep methodology and evidence-posture commentary compact", skill_doc)
        self.assertIn("do not fragment years, ticker symbols, ranges", skill_doc)
        self.assertIn("flexible standalone HTML idea-triage report", output_standards)
        self.assertIn("Use this pack only for", dashboard_pack)
        self.assertIn("verified positioning", dashboard_pack)

    def test_company_tearsheet_uses_compact_flexible_html_when_selected(self) -> None:
        skill_doc = read("skills/company-tearsheet/SKILL.md")
        profile_templates = read("skills/company-tearsheet/references/profile-templates.md")
        quality_checks = read("skills/company-tearsheet/references/quality-checks.md")
        dashboard_pack = read("skills/company-tearsheet/references/DASHBOARD_PACK.md")

        self.assertIn("../../shared/html-artifact-standard.md", skill_doc)
        self.assertIn("When the user explicitly requests HTML for a tearsheet", skill_doc)
        self.assertIn("polished standalone HTML tearsheet", skill_doc)
        self.assertIn("explicitly asks for a standardized dashboard", skill_doc)
        self.assertIn("compact issuer baseline", skill_doc)
        self.assertIn("Trailing Valuation Snapshot", skill_doc)
        self.assertIn("Do not include `Debate` in the heading", skill_doc)
        self.assertIn(
            "Do not thread it through earnings drivers, valuation, and multiple summary panels",
            skill_doc,
        )
        self.assertIn("do not fragment tickers, years, dates", skill_doc)
        self.assertIn("Standalone HTML tearsheet", profile_templates)
        self.assertIn("Do not include `Debate` in the heading", profile_templates)
        self.assertIn("compact evidence-gaps block", profile_templates)
        self.assertIn("internal evidence labels", quality_checks)
        self.assertIn(
            "not threaded through earnings drivers, valuation, and multiple summary panels",
            quality_checks,
        )
        self.assertIn("Use this pack only for", dashboard_pack)
        self.assertIn("citation rendering remains readable", dashboard_pack)

    def test_comps_valuation_uses_flexible_html_with_optional_dashboard(self) -> None:
        skill_doc = read("skills/comps-valuation/SKILL.md")
        output_templates = read("skills/comps-valuation/references/output-templates.md")
        valuation_readthrough = read("skills/comps-valuation/references/valuation-readthrough.md")
        source_rules = read("skills/comps-valuation/references/source-and-staleness-rules.md")
        dashboard_pack = read("skills/comps-valuation/references/DASHBOARD_PACK.md")
        p0_integrations = read("skills/comps-valuation/references/p0-integrations.md")
        workbook_mode = read("skills/comps-valuation/references/workbook-mode.md")

        self.assertIn("../../shared/html-artifact-standard.md", skill_doc)
        self.assertIn("polished standalone HTML comps report", skill_doc)
        self.assertIn("explicitly asks for a standardized dashboard", skill_doc)
        self.assertIn("premium or discount is supported", skill_doc)
        self.assertIn("Do not issue add, trim, hedge, sizing, or exit instructions", skill_doc)
        self.assertIn("do not fragment tickers, prices, multiples", skill_doc)
        self.assertIn("Standalone HTML comps report", output_templates)
        self.assertIn("ordinary comps report into an action-rules dashboard", output_templates)
        self.assertIn("illustrative trailing-multiple range", valuation_readthrough)
        self.assertIn("third-party forward estimates", source_rules)
        self.assertIn("not `consensus`", source_rules)
        self.assertIn("third-party forward estimates", output_templates)
        self.assertIn("Use this pack only when", dashboard_pack)
        self.assertIn("citation rendering remains readable", dashboard_pack)
        self.assertIn("standalone HTML comps report", p0_integrations)
        self.assertIn("polished standalone HTML comps report", workbook_mode)

    def test_deck_report_qc_uses_flexible_html_with_optional_dashboard(self) -> None:
        skill_doc = read("skills/deck-report-qc/SKILL.md")
        output_templates = read("skills/deck-report-qc/references/output-templates.md")
        extraction_tieout = read("skills/deck-report-qc/references/extraction-and-tieout.md")
        dashboard_pack = read("skills/deck-report-qc/references/DASHBOARD_PACK.md")

        self.assertIn("../../shared/html-artifact-standard.md", skill_doc)
        self.assertIn("polished standalone HTML senior-review QC report", skill_doc)
        self.assertIn("only when the user explicitly asks for a standardized dashboard", skill_doc)
        self.assertIn("Review scope and evidence limitations", output_templates)
        self.assertIn("Decision-critical tie-out", output_templates)
        self.assertIn("must appear before a narrative `Top Issues`", output_templates)
        self.assertIn(
            "document.documentElement.scrollWidth <= document.documentElement.clientWidth",
            skill_doc,
        )
        self.assertIn("confirmed internal mismatch", extraction_tieout)
        self.assertIn("local headless browser", extraction_tieout)
        self.assertIn("Use this pack only when", dashboard_pack)

    def test_meeting_prep_uses_live_call_sheet_html_with_optional_dashboard(self) -> None:
        skill_doc = read("skills/meeting-prep/SKILL.md")
        output_templates = read("skills/meeting-prep/references/output-templates.md")
        playbooks = read("skills/meeting-prep/references/meeting-type-playbooks.md")
        dashboard_pack = read("skills/meeting-prep/references/DASHBOARD_PACK.md")
        intake_policy = read("shared/deliverable-intake-policy.md")

        self.assertIn("../../shared/html-artifact-standard.md", skill_doc)
        self.assertIn("polished standalone HTML live-meeting brief", skill_doc)
        self.assertIn("explicitly asks for a standardized dashboard", skill_doc)
        self.assertIn("three or four must-ask questions", skill_doc)
        self.assertIn("If Time Permits", skill_doc)
        self.assertIn("Model / thesis implication", skill_doc)
        self.assertIn("Place a compact `Conversation Flow` block immediately after", skill_doc)
        self.assertIn("one short sentence", skill_doc)
        self.assertIn("Standalone HTML management / IR call sheet", output_templates)
        self.assertIn(
            "The `Conversation Flow` block must appear before the detailed must-ask question cards",
            output_templates,
        )
        self.assertIn("Avoid eight equally weighted question cards", output_templates)
        self.assertIn("Live-use output for a public-company management or IR meeting", playbooks)
        self.assertIn("Use this pack only when", dashboard_pack)
        self.assertIn("polished standalone HTML live-meeting brief", intake_policy)

    def test_long_short_pitch_uses_actionability_first_flexible_html(self) -> None:
        skill_doc = read("skills/long-short-pitch/SKILL.md")
        output_contract = read("skills/long-short-pitch/references/output-contract.md")
        playbooks = read("skills/long-short-pitch/references/strategy-playbooks.md")
        dashboard_pack = read("skills/long-short-pitch/references/DASHBOARD_PACK.md")
        intake_policy = read("shared/deliverable-intake-policy.md")

        self.assertIn("../../shared/html-artifact-standard.md", skill_doc)
        self.assertIn("polished standalone HTML trade-pitch report", skill_doc)
        self.assertIn("only when the user explicitly asks for a standardized dashboard", skill_doc)
        self.assertIn("Implementation Gate", skill_doc)
        self.assertIn("Illustrative Scenario Skew", skill_doc)
        self.assertIn("AWS Infrastructure Commitment", skill_doc)
        self.assertIn("Monitoring Triggers", skill_doc)
        self.assertIn("Conditional Action Rules", skill_doc)
        self.assertIn("do not fragment tickers, fiscal years, dates", skill_doc)
        self.assertIn("Standalone HTML Trade-Pitch Report", output_contract)
        self.assertIn("does not clear the trade for implementation", output_contract)
        self.assertIn("not incremental revenue guidance", output_contract)
        self.assertIn("Reserve `Monitoring Dashboard`", output_contract)
        self.assertIn("Reported", output_contract)
        self.assertIn("surface a compact `Implementation Gate`", playbooks)
        self.assertIn("no-position or watchlist HTML pitch", playbooks)
        self.assertIn("Use this pack only when", dashboard_pack)
        self.assertIn("empty scenario fields", dashboard_pack)
        self.assertIn("polished standalone HTML trade-pitch report", intake_policy)

    def test_economic_impact_report_uses_transmission_first_flexible_html(self) -> None:
        skill_doc = read("skills/economic-impact-report/SKILL.md")
        report_template = read("skills/economic-impact-report/references/report-template.md")
        quality_bar = read("skills/economic-impact-report/references/quality-bar.md")
        dashboard_pack = read("skills/economic-impact-report/references/DASHBOARD_PACK.md")
        intake_policy = read("shared/deliverable-intake-policy.md")

        self.assertIn("../../shared/html-artifact-standard.md", skill_doc)
        self.assertIn("polished standalone HTML economic-impact report", skill_doc)
        self.assertIn("only when the user explicitly asks for a standardized dashboard", skill_doc)
        self.assertIn("Event Status And Market Baseline", skill_doc)
        self.assertIn("Event-To-Equity Transmission Map", skill_doc)
        self.assertIn("representative exposure candidates", skill_doc)
        self.assertIn("Do not repeat citation chips", skill_doc)
        self.assertIn(
            "same transmission channel, first affected line item, and directional read-through",
            skill_doc,
        )
        self.assertIn("broad-index performance as context only", skill_doc)
        self.assertIn("exact research cut-off time and time zone", skill_doc)
        self.assertIn("Event Status And Market Baseline", report_template)
        self.assertIn("What Is Priced In Vs. What Requires Proof", report_template)
        self.assertIn("Monitoring Triggers And Research Queue", report_template)
        self.assertIn("Broad-index context", report_template)
        self.assertIn("Combine exposures in one row only", report_template)
        self.assertIn("repeated citation chips", quality_bar)
        self.assertIn("thematic adjacency is not enough", quality_bar)
        self.assertIn("Use this pack only when", dashboard_pack)
        self.assertIn("ordinary standalone HTML economic-impact report", dashboard_pack)
        self.assertIn("polished standalone HTML economic-impact report", intake_policy)

    def test_substantial_workflows_have_typed_dashboard_packs(self) -> None:
        for skill in DASHBOARD_PACK_SKILLS:
            relative_path = f"skills/{skill}/references/DASHBOARD_PACK.md"
            pack = read(relative_path)
            skill_doc = read(f"skills/{skill}/SKILL.md")

            self.assertIn("## Producer Role", pack, relative_path)
            self.assertIn("## Recommended Payload", pack, relative_path)
            self.assertIn("## Tabs And Modules", pack, relative_path)
            self.assertIn("## Required Evidence", pack, relative_path)
            self.assertIn("## Do Not", pack, relative_path)
            self.assertIn("## QA Checks", pack, relative_path)
            self.assertIn("`dashboard-builder` owns", pack, relative_path)
            self.assertIn("metadata.payload_stage", pack, relative_path)
            self.assertIn(
                "public_equity_investing_dashboard.v1", skill_doc, f"skills/{skill}/SKILL.md"
            )
            self.assertIn("references/DASHBOARD_PACK.md", skill_doc, f"skills/{skill}/SKILL.md")

            lowered = pack.lower()
            forbidden = [
                "markdown report",
                "user-facing markdown",
                "final markdown",
                "raw json the lead",
                "json as the lead",
            ]
            for phrase in forbidden:
                self.assertNotIn(phrase, lowered, relative_path)

    def test_dashboard_sample_payloads_validate_in_strict_mode(self) -> None:
        payload_dir = "skills/public-equity-investing/internal-support/dashboard-builder/assets/example_payloads"
        for filename in DASHBOARD_SAMPLE_PAYLOADS:
            relative_path = f"{payload_dir}/{filename}"
            payload = load_json(relative_path)
            report = validate_payload(payload)

            self.assertEqual("strict", payload["metadata"]["citation_policy"], relative_path)
            self.assertEqual("failed" if report["hard_failures"] else "passed", report["status"])
            self.assertEqual([], report["hard_failures"], f"{relative_path}: {report}")
            self.assertTrue(payload.get("sources"), relative_path)
            self.assertTrue(_payload_has_module(payload, "missing_evidence"), relative_path)

    def test_strict_financial_chart_requires_render_ready_rows(self) -> None:
        payload = load_json(
            "skills/public-equity-investing/internal-support/dashboard-builder/assets/example_payloads/financial-trend-incomplete-sample.json"
        )

        report = validate_payload(payload, profile="draft")

        self.assertEqual("failed", report["status"])
        self.assertTrue(
            any(
                "financial_trend_chart has fewer than 2 chart-ready rows" in failure
                and "add missing_evidence" in failure
                for failure in report["hard_failures"]
            ),
            report,
        )

    def test_non_strict_financial_chart_warns_on_incomplete_rows(self) -> None:
        payload = load_json(
            "skills/public-equity-investing/internal-support/dashboard-builder/assets/example_payloads/financial-trend-incomplete-sample.json"
        )
        payload["metadata"]["citation_policy"] = "warn"
        payload["metadata"]["payload_stage"] = "draft"
        payload["metadata"]["readiness_posture"] = "working_draft"

        report = validate_payload(payload, profile="draft")

        self.assertEqual("passed", report["status"])
        self.assertEqual([], report["hard_failures"])

    def test_production_profile_requires_complete_dashboard_contract(self) -> None:
        payload = minimal_dashboard_payload()

        report = validate_payload(payload, profile="production")
        failures = "\n".join(report["hard_failures"])

        self.assertEqual("failed", report["status"])
        for expected in [
            "payload.mode must be a non-empty string",
            "production dashboards must include layout",
            "production dashboards must include metadata",
            "production dashboards must include a non-empty hero",
            "production dashboards must include non-empty snapshot tiles",
        ]:
            self.assertIn(expected, failures)

    def test_production_profile_complete_fixture_passes(self) -> None:
        payload = load_json(
            "skills/public-equity-investing/internal-support/dashboard-builder/assets/example_payloads/production-complete-sample.json"
        )

        report = validate_payload(payload, profile="production")

        self.assertEqual("passed", report["status"], report)
        self.assertEqual([], report["hard_failures"], report)

    def test_production_profile_fails_missing_source_ledger(self) -> None:
        payload = load_json(
            "skills/public-equity-investing/internal-support/dashboard-builder/assets/example_payloads/production-missing-source-fails-sample.json"
        )

        report = validate_payload(payload, profile="production")

        self.assertEqual("failed", report["status"])
        self.assertTrue(
            any(
                "strict dashboards must include a source ledger" in failure
                for failure in report["hard_failures"]
            ),
            report,
        )

    def test_production_profile_fails_unresolved_citation(self) -> None:
        payload = load_json(
            "skills/public-equity-investing/internal-support/dashboard-builder/assets/example_payloads/production-unresolved-citation-fails-sample.json"
        )

        report = validate_payload(payload, profile="production")

        self.assertEqual("failed", report["status"])
        self.assertTrue(
            any("unknown source id 'S99'" in failure for failure in report["hard_failures"]),
            report,
        )

    def test_warn_mode_support_payload_allows_source_and_numeric_gaps_as_warnings(self) -> None:
        payload = load_json(
            "skills/public-equity-investing/internal-support/dashboard-builder/assets/example_payloads/draft-support-source-gap-sample.json"
        )

        report = validate_payload(payload, profile="draft")

        self.assertEqual("passed", report["status"], report)
        self.assertEqual([], report["hard_failures"], report)
        self.assertTrue(
            any(
                "final dashboards should include a source ledger" in warning
                for warning in report["warnings"]
            )
        )
        self.assertTrue(
            any("numeric material without citations" in warning for warning in report["warnings"])
        )

    def test_warn_mode_support_payload_allows_incomplete_chart_as_warning(self) -> None:
        payload = load_json(
            "skills/public-equity-investing/internal-support/dashboard-builder/assets/example_payloads/draft-incomplete-chart-support-sample.json"
        )

        report = validate_payload(payload, profile="draft")

        self.assertEqual("passed", report["status"], report)
        self.assertEqual([], report["hard_failures"], report)
        self.assertTrue(
            any(
                "financial_trend_chart has fewer than 2 chart-ready rows" in warning
                for warning in report["warnings"]
            ),
            report,
        )

    def test_client_ready_posture_forces_production_validation(self) -> None:
        payload = minimal_dashboard_payload()
        payload["metadata"] = {
            "payload_stage": "draft",
            "citation_policy": "warn",
            "readiness_posture": "client_ready",
            "readiness_label": "Client ready",
        }

        report = validate_payload(payload, profile="draft")
        failures = "\n".join(report["hard_failures"])

        self.assertEqual("failed", report["status"])
        self.assertIn(
            "production dashboards must set metadata.citation_policy to 'strict'", failures
        )
        self.assertIn("production dashboards must include a non-empty hero", failures)

    def test_dashboard_render_script_defaults_to_production_profile(self) -> None:
        payload = (
            ROOT
            / "skills/public-equity-investing/internal-support/dashboard-builder/assets/example_payloads/draft-support-source-gap-sample.json"
        )
        script = (
            ROOT
            / "skills/public-equity-investing/internal-support/dashboard-builder/scripts/render_dashboard.py"
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            output = Path(tmp_dir) / "dashboard.html"

            default_result = subprocess.run(
                [sys.executable, str(script), str(payload), str(output)],
                cwd=str(ROOT),
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(0, default_result.returncode)
            self.assertIn("production dashboards must include layout", default_result.stderr)

            draft_result = subprocess.run(
                [sys.executable, str(script), str(payload), str(output), "--profile", "draft"],
                cwd=str(ROOT),
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, draft_result.returncode, draft_result.stderr + draft_result.stdout)
            self.assertTrue(output.exists())

    def test_render_dashboard_default_uses_production_validation(self) -> None:
        payload = minimal_dashboard_payload()

        with self.assertRaisesRegex(ValueError, "production dashboards must include layout"):
            render_dashboard(payload)

        html = render_dashboard(payload, validation_profile="draft")
        self.assertIn("Issuer dashboard", html)

    def test_dashboard_renders_reader_actions_bar_with_print_control(self) -> None:
        payload = load_json(
            "skills/public-equity-investing/internal-support/dashboard-builder/assets/example_payloads/production-complete-sample.json"
        )

        html = render_dashboard(payload)

        self.assertIn("dashboard-utility-bar", html)
        self.assertIn("Reader actions", html)
        self.assertIn("Copy Full Report", html)
        self.assertIn("data-copy-full-report", html)
        self.assertIn("data-print-dashboard", html)
        self.assertIn("Print / Save PDF", html)
        self.assertIn("data-report-copy-root", html)
        self.assertNotIn("print-action", html)
        self.assertNotIn("Open workbook", html)
        self.assertNotIn("Copy executive summary", html)
        self.assertNotIn('<p class="eyebrow"></p>', html)

    def test_dashboard_css_uses_flat_light_surface(self) -> None:
        css = read("shared/dashboard/assets/dashboard.css")

        self.assertIn("--page: #ffffff;", css)
        self.assertIn("--surface-muted: #f8fafc;", css)
        self.assertIn("--data-accent:", css)
        self.assertIn("--status-positive:", css)
        self.assertIn("--narrative-width: 72ch;", css)
        self.assertIn("font-variant-numeric: tabular-nums lining-nums;", css)
        self.assertIn(".dense-table th", css)
        self.assertIn("min-height: 18px;", css)
        for elevated_effect in (
            "box-shadow",
            "linear-gradient",
            "radial-gradient",
            "backdrop-filter",
        ):
            self.assertNotIn(elevated_effect, css)

    def test_single_page_deduplicates_heading_and_aligns_numeric_columns(self) -> None:
        payload = minimal_dashboard_payload()
        payload["layout"] = "single_page"
        payload["tabs"][0]["modules"] = [
            {
                "type": "table",
                "title": "Overview",
                "data": {
                    "columns": [
                        "metric",
                        "revenue",
                        {"key": "delta", "label": "Change", "type": "percent"},
                    ],
                    "rows": [{"metric": "Revenue", "revenue": "$120M", "delta": "12%"}],
                },
            }
        ]

        html = render_dashboard(payload, validate=False)

        self.assertEqual(1, html.count("<h2>Overview</h2>"))
        self.assertIn('<th class="is-numeric">Revenue</th>', html)
        self.assertIn('<th class="is-numeric">Change</th>', html)
        self.assertIn('<td class="is-numeric" data-label="Revenue">', html)

    def test_dashboard_rejects_empty_scenario_cases(self) -> None:
        payload = minimal_dashboard_payload()
        payload["tabs"][0]["modules"] = [
            {"type": "scenario_map", "data": {"cases": [{"label": "Bull", "citations": ["S1"]}]}}
        ]

        report = validate_payload(payload, profile="draft")

        self.assertEqual("failed", report["status"])
        self.assertTrue(
            any("omit empty scenario cards" in failure for failure in report["hard_failures"]),
            report,
        )

    def test_dashboard_renders_scenario_summary_fields(self) -> None:
        payload = minimal_dashboard_payload()
        payload["tabs"][0]["modules"] = [
            {
                "type": "scenario_map",
                "data": {
                    "cases": [
                        {
                            "label": "Bear",
                            "status": "bear",
                            "summary": "Underlying growth remains pressured.",
                            "citations": ["S1"],
                        }
                    ]
                },
            }
        ]

        html = render_dashboard(payload, validate=False)

        self.assertIn('<article class="scenario-card bear">', html)
        self.assertIn("Bear", html)
        self.assertIn("Underlying growth remains pressured.", html)

    def test_market_events_resolve_visible_source_from_citation_ledger(self) -> None:
        payload = minimal_dashboard_payload()
        payload["sources"] = [
            {"id": "S1", "title": "Company release", "url": "https://example.com/release"}
        ]
        payload["tabs"][0]["modules"] = [
            {
                "type": "market_events",
                "data": {
                    "events": [
                        {
                            "date": "May 27, 2026",
                            "event": "Fiscal Q1 results",
                            "impact": "Updated growth debate",
                            "investor_read": "Monitor forward guidance",
                            "citations": ["S1"],
                        }
                    ]
                },
            }
        ]

        html = render_dashboard(payload, validate=False)

        self.assertIn("Company release", html)
        self.assertIn("https://example.com/release", html)
        self.assertNotIn('data-label="Source">Not sourced', html)

    def test_strict_complete_financial_chart_passes(self) -> None:
        payload = minimal_dashboard_payload()
        payload["metadata"] = {"citation_policy": "strict"}
        payload["tabs"][0]["modules"] = [
            {
                "type": "financial_trend_chart",
                "data": {
                    "periods": [
                        {
                            "period": "Q1 FY2026",
                            "revenue": "100",
                            "gross_profit": "60",
                            "net_income": "20",
                            "net_margin": "20%",
                            "citations": ["S1"],
                        },
                        {
                            "period": "Q2 FY2026",
                            "revenue": "110",
                            "gross_profit": "66",
                            "net_income": "22",
                            "net_margin": "20%",
                            "citations": ["S1"],
                        },
                    ]
                },
            }
        ]

        report = validate_payload(payload, profile="draft")

        self.assertEqual("passed", report["status"])
        self.assertEqual([], report["hard_failures"])

    def test_strict_incomplete_chart_intent_passes_when_chart_is_omitted(self) -> None:
        payload = minimal_dashboard_payload()
        payload["metadata"] = {"citation_policy": "strict"}
        payload["tabs"][0]["modules"] = [
            {"type": "decision_box", "data": {"stance": "Watch", "citations": ["S1"]}},
            {
                "type": "missing_evidence",
                "data": {
                    "items": [
                        "Financial trend chart omitted because revenue, gross profit, net income, and margin history are incomplete."
                    ]
                },
            },
        ]

        report = validate_payload(payload, profile="draft")

        self.assertEqual("passed", report["status"])
        self.assertEqual([], report["hard_failures"])

    def test_chart_readiness_covers_eps_and_price_event_charts(self) -> None:
        cases = [
            (
                "eps_actual_vs_estimate_chart",
                {
                    "periods": [
                        {
                            "period": "Q1",
                            "estimated_eps": "1.00",
                            "actual_eps": "1.10",
                            "citations": ["S1"],
                        },
                        {
                            "period": "Q2",
                            "estimated_eps": "1.20",
                            "actual_eps": "",
                            "citations": ["S1"],
                        },
                    ]
                },
                "fewer than 2 chart-ready rows",
            ),
            (
                "equity_price_event_chart",
                {
                    "prices": [
                        {"date": "2026-01-01", "price": "10.00", "citations": ["S1"]},
                        {"date": "2026-01-02", "price": "", "citations": ["S1"]},
                    ],
                    "events": [{"date": "2026-01-01", "event": "Launch", "citations": ["S1"]}],
                },
                "needs at least 10 daily chart-ready price rows; got 1",
            ),
        ]

        for module_type, data, expected in cases:
            payload = minimal_dashboard_payload()
            payload["metadata"] = {"citation_policy": "strict"}
            payload["tabs"][0]["modules"] = [{"type": module_type, "data": data}]

            report = validate_payload(payload, profile="draft")

            self.assertEqual("failed", report["status"], module_type)
            self.assertTrue(
                any(expected in failure for failure in report["hard_failures"]),
                f"{module_type}: {report}",
            )

    def test_price_event_chart_rejects_three_point_daily_reaction_tape(self) -> None:
        payload = minimal_dashboard_payload()
        payload["metadata"] = {"citation_policy": "strict"}
        payload["tabs"][0]["modules"] = [
            {
                "type": "equity_price_event_chart",
                "data": {
                    "price_granularity": "daily",
                    "prices": [
                        {"date": "2026-04-30", "price": 384.94, "citations": ["S1"]},
                        {"date": "2026-05-13", "price": 402.62, "citations": ["S1"]},
                        {"date": "2026-05-19", "price": 399.00, "citations": ["S1"]},
                    ],
                    "events": [
                        {
                            "date": "2026-04-30",
                            "event": "Post-print close",
                            "citations": ["S1"],
                        }
                    ],
                },
            }
        ]

        report = validate_payload(payload, profile="draft")

        self.assertEqual("failed", report["status"])
        self.assertTrue(
            any(
                "needs at least 10 daily chart-ready price rows; got 3" in failure
                for failure in report["hard_failures"]
            ),
            report,
        )

    def test_price_event_chart_accepts_substantive_daily_reaction_tape(self) -> None:
        payload = minimal_dashboard_payload()
        payload["metadata"] = {"citation_policy": "strict"}
        payload["tabs"][0]["modules"] = [
            {
                "type": "equity_price_event_chart",
                "data": {
                    "price_granularity": "daily",
                    "prices": [
                        {"date": f"2026-01-{day:02d}", "price": 100 + day, "citations": ["S1"]}
                        for day in range(1, 11)
                    ],
                    "events": [
                        {"date": "2026-01-05", "event": "Earnings print", "citations": ["S1"]}
                    ],
                },
            }
        ]

        report = validate_payload(payload, profile="draft")

        self.assertEqual("passed", report["status"])
        self.assertEqual([], report["hard_failures"])

    def test_renderer_omits_thin_price_event_chart_when_validation_is_bypassed(self) -> None:
        payload = minimal_dashboard_payload()
        payload["tabs"][0]["modules"] = [
            {
                "type": "equity_price_event_chart",
                "title": "Thin Price Tape",
                "data": {
                    "prices": [{"date": "2026-04-30", "price": 100, "citations": ["S1"]}],
                    "events": [{"date": "2026-04-30", "event": "Earnings", "citations": ["S1"]}],
                },
            }
        ]

        html = render_dashboard(payload, validate=False)

        self.assertNotIn("Thin Price Tape", html)
        self.assertNotIn("price-event-chart", html)

    def test_hero_dek_and_callout_render_citation_links(self) -> None:
        payload = load_json(
            "skills/public-equity-investing/internal-support/dashboard-builder/assets/example_payloads/hero-citations-sample.json"
        )

        html = render_dashboard(payload)

        dek_index = html.index("The hero dek should append a source chip")
        dek_chip_index = html.find("citation-chip", dek_index)
        self.assertGreater(dek_chip_index, dek_index)
        self.assertLess(dek_chip_index, dek_index + 600)

        callout_index = html.index("Revenue grew")
        numeric_link_index = html.find('class="citation-link"', callout_index)
        linked_number_index = html.find("24.5%", callout_index)
        self.assertGreater(numeric_link_index, callout_index)
        self.assertLess(numeric_link_index, callout_index + 600)
        self.assertGreater(linked_number_index, numeric_link_index)
        self.assertLess(linked_number_index, numeric_link_index + 200)

    def test_strict_dashboard_requires_source_ledger(self) -> None:
        payload = minimal_dashboard_payload()
        payload["metadata"] = {"citation_policy": "strict"}
        payload["sources"] = []

        report = validate_payload(payload, profile="draft")

        self.assertEqual("failed", report["status"])
        self.assertTrue(
            any(
                "strict dashboards must include a source ledger" in failure
                for failure in report["hard_failures"]
            )
        )
        self.assertFalse(any("source ledger" in warning for warning in report["warnings"]))

    def test_strict_dashboard_missing_sources_requires_source_ledger(self) -> None:
        payload = minimal_dashboard_payload()
        payload["metadata"] = {"citation_policy": "strict"}
        payload.pop("sources")

        report = validate_payload(payload, profile="draft")

        self.assertEqual("failed", report["status"])
        self.assertTrue(
            any(
                "strict dashboards must include a source ledger" in failure
                for failure in report["hard_failures"]
            )
        )

    def test_top_level_strict_dashboard_requires_source_ledger(self) -> None:
        payload = minimal_dashboard_payload()
        payload["citation_policy"] = "strict"
        payload["sources"] = []

        report = validate_payload(payload, profile="draft")

        self.assertEqual("failed", report["status"])
        self.assertTrue(
            any(
                "strict dashboards must include a source ledger" in failure
                for failure in report["hard_failures"]
            )
        )

    def test_non_strict_dashboard_warns_on_missing_source_ledger(self) -> None:
        payload = minimal_dashboard_payload()
        payload["sources"] = []

        report = validate_payload(payload, profile="draft")

        self.assertEqual("passed", report["status"])
        self.assertTrue(
            any(
                "final dashboards should include a source ledger" in warning
                for warning in report["warnings"]
            )
        )
        self.assertEqual([], report["hard_failures"])

    def test_workbook_covers_are_insight_dashboards_and_audited(self) -> None:
        standard = read("shared/workbook-artifact-standard.md")
        helpers = read("shared/workbook_artifacts.py")
        audit = read("skills/model-audit-tieout/scripts/audit_workbook.py")
        skill = read("skills/model-audit-tieout/SKILL.md")

        for phrase in [
            "recommendation, net read, or decision question",
            "model/workbook status and decision-readiness label",
            "major sensitivities, catalyst/risk flags, or thesis breaks",
            "A table-of-contents cover is not enough",
        ]:
            self.assertIn(phrase, standard)

        for phrase in [
            "Decision question",
            "Executive read-through",
            "KPI tiles",
            "Chart-ready data",
        ]:
            self.assertIn(phrase, helpers)

        self.assertIn('r"update_cover(?:_\\d+)?"', audit)
        self.assertIn("is_update_cover", audit)
        self.assertIn("chart-ready or visual data", audit)
        self.assertIn("first-visible `Cover` tabs", skill)


if __name__ == "__main__":
    unittest.main()
