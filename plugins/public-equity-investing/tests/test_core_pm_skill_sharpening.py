"""Core public-equity PM skill sharpening contracts."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


class CorePMSkillSharpeningTests(unittest.TestCase):
    def test_company_tearsheet_requires_security_ownership_positioning_defaults(self) -> None:
        text = (
            read("skills/company-tearsheet/SKILL.md")
            + "\n"
            + read("skills/company-tearsheet/references/profile-templates.md")
            + "\n"
            + read("skills/company-tearsheet/references/metric-library.md")
            + "\n"
            + read("skills/company-tearsheet/references/quality-checks.md")
        ).lower()
        for phrase in [
            "market cap",
            "float",
            "adv/liquidity",
            "index membership",
            "etf/passive ownership",
            "top holders",
            "short interest",
            "borrow/crowding",
            "factor exposure",
            "governance",
            "capital allocation",
            "sell-side coverage",
            "consensus setup",
            "next analytical route",
        ]:
            self.assertIn(phrase, text)

    def test_memo_builder_has_scratch_build_scaffold_and_pm_judgment(self) -> None:
        text = (
            read("skills/memo-builder/SKILL.md")
            + "\n"
            + read("skills/memo-builder/references/memo-modes.md")
            + "\n"
            + read("skills/memo-builder/references/output-contracts.md")
            + "\n"
            + read("skills/memo-builder/references/source-policy.md")
        ).lower()
        for phrase in [
            "screen-grade-scratch-memo",
            "intake checklist",
            "source packet requirements",
            "first-pass house view",
            "variant wedge",
            "what is priced in",
            "estimate path",
            "valuation/skew",
            "downside mechanism",
            "disconfirmers",
            "action rules",
            "evidence needed to upgrade",
        ]:
            self.assertIn(phrase, text)

    def test_thesis_tracker_operating_model_is_explicit(self) -> None:
        text = (
            read("skills/thesis-tracker/SKILL.md")
            + "\n"
            + read("skills/thesis-tracker/references/workflow-core.md")
            + "\n"
            + read("skills/thesis-tracker/references/output-templates.md")
            + "\n"
            + read("skills/thesis-tracker/references/thesis-schema.md")
        ).lower()
        for phrase in [
            "pm owner",
            "analyst owner",
            "evidence owner",
            "kpi owner",
            "model owner",
            "decision authority",
            "review cadence",
            "post-catalyst update sla",
            "escalation triggers",
            "next review gate",
            "action threshold",
            "append-only decision log",
        ]:
            self.assertIn(phrase, text)

    def test_thesis_tracker_workbook_update_separates_readiness_and_decision_authority(
        self,
    ) -> None:
        text = (
            read("skills/thesis-tracker/SKILL.md")
            + "\n"
            + read("skills/thesis-tracker/references/workflow-core.md")
            + "\n"
            + read("skills/thesis-tracker/references/output-templates.md")
            + "\n"
            + read("skills/thesis-tracker/references/quality-guardrails.md")
            + "\n"
            + read("skills/thesis-tracker/references/thesis-schema.md")
            + "\n"
            + read("skills/thesis-tracker/references/DASHBOARD_PACK.md")
        ).lower()
        for phrase in [
            "polished xlsx thesis tracker workbook",
            "company-thesis status",
            "security-thesis readiness",
            "not decision-grade",
            "draft threshold for pm confirmation",
            "approved monitoring rule",
            "current public price",
            "render every",
            "score chart",
            "explicitly requests an html dashboard/report",
            "override rationale",
            "multiple core pillars",
            "full action-rule",
            "dedicated tabs",
        ]:
            self.assertIn(phrase, text)

    def test_meeting_prep_has_first_class_public_equity_modes(self) -> None:
        text = (
            read("skills/meeting-prep/SKILL.md")
            + "\n"
            + read("skills/meeting-prep/references/meeting-type-playbooks.md")
            + "\n"
            + read("skills/meeting-prep/references/output-templates.md")
            + "\n"
            + read("skills/meeting-prep/references/DASHBOARD_PACK.md")
        ).lower()
        for phrase in [
            "management_ir",
            "expert_call",
            "pm_internal_review",
            "sell_side_call",
            "earnings_call",
            "investor_day",
            "portfolio_watchlist_review",
            "model_review",
            "what not to ask",
            "evidence requests",
            "likely pushbacks",
            "follow-up actions",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
