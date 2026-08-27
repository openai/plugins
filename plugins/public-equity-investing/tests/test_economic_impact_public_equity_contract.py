"""Public-equity boundary tests for economic-impact-report."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


class EconomicImpactPublicEquityContractTests(unittest.TestCase):
    def test_skill_is_narrowed_to_public_equity_decision_impact(self) -> None:
        text = read("skills/economic-impact-report/SKILL.md")

        for phrase in [
            "issuer, sector, earnings, valuation, positioning, and portfolio",
            "not a generic cross-asset macro note",
            "No Portfolio / Watchlist Fallback",
            "general public-equity exposure map",
            "Public Equity Framing",
            "Issuer And Sector Impact",
            "Earnings, Valuation, And Positioning Read-Through",
            "public_equity_investing_dashboard.v1",
            "../../shared/html-artifact-standard.md",
            "polished standalone HTML economic-impact report",
            "only when the user explicitly asks for a standardized dashboard",
            "Event Status And Market Baseline",
            "Event-To-Equity Transmission Map",
            "representative exposure candidates",
            "Do not repeat citation chips",
            "share the same transmission channel, first affected line item, and directional read-through",
            "broad-index performance as context only",
            "exact research cut-off time and time zone",
        ]:
            self.assertIn(phrase, text)

        for phrase in [
            "standalone macro, rates, FX, futures, options, commodities, or credit strategy",
            "route out",
        ]:
            self.assertIn(phrase, text)

    def test_report_template_forces_public_equity_bottom_line(self) -> None:
        text = read("skills/economic-impact-report/references/report-template.md")

        for phrase in [
            "Public Equity Bottom Line",
            "General Exposure Map If No Portfolio Was Provided",
            "Industries / countries / currencies / companies / commodities",
            "What Is New Vs. Expected",
            "Event Status And Market Baseline",
            "Event-To-Equity Transmission Map",
            "Transmission Map",
            "Ranked Equity Impact Map",
            "Issuer And Sector Impact",
            "Earnings, Valuation, And Positioning Read-Through",
            "Public Equity Framing",
            "What Is Priced In Vs. What Requires Proof",
            "Second-, Third-, And Fourth-Order Equity Effects",
            "Monitoring Triggers And Research Queue",
            "What Would Change The View",
            "Research cut-off",
            "Broad-index context",
            "Combine exposures in one row only when they share the same transmission channel",
        ]:
            self.assertIn(phrase, text)

        for stale in [
            "Private Company Impact",
            "Country And Currency Impact",
            "Rates Impact",
            "Options Impact",
            "Futures Impact",
            "Best cross-asset expression",
        ]:
            self.assertNotIn(stale, text)

    def test_domain_checklists_keep_cross_asset_inputs_inside_equity_frame(self) -> None:
        text = read("skills/economic-impact-report/references/domain-checklists.md")

        for phrase in [
            "Public Equity Issuers",
            "Sector And Peer Group",
            "Portfolio And Positioning",
            "If no portfolio, watchlist, thesis, benchmark, or positions were provided",
            "Build a general exposure map across industries, countries/currencies, public companies, relevant private companies, commodities",
            "Macro, FX, Rates, Commodities, Options, And Futures As Inputs",
            "Credit Signals As Equity Read-Through",
            "common-equity downside signal",
            "Credit Markets",
        ]:
            self.assertIn(phrase, text)

    def test_dashboard_pack_rejects_standalone_cross_asset_output(self) -> None:
        text = read("skills/economic-impact-report/references/DASHBOARD_PACK.md")

        for phrase in [
            "public-equity mechanism",
            "Line item affected",
            "general exposure map for industries, countries/currencies, public companies, relevant private companies, commodities",
            "Priced-in status",
            "PM action",
            "Source posture",
            "Missing evidence",
            "Do not turn the dashboard into a standalone rates, FX, commodity, futures, options, or credit-security dashboard",
        ]:
            self.assertIn(phrase, text)

        self.assertIn(
            "Use this pack only when the user explicitly selects a standardized dashboard", text
        )
        self.assertIn("ordinary standalone HTML economic-impact report", text)

    def test_quality_bar_fails_generic_macro_outputs(self) -> None:
        text = read("skills/economic-impact-report/references/quality-bar.md")

        for phrase in [
            "It lacks issuer, sector, earnings, valuation, positioning, or portfolio implications.",
            "It recommends a standalone rates, FX, options, futures, commodity, or credit-security expression",
            "It fails to state what is already priced in",
            "It does not identify what would change the PM action",
            "If no portfolio/watchlist was provided",
            "Event Status And Market Baseline",
            "fixed dashboard module inventory",
            "repeated citation chips",
            "thematic adjacency is not enough",
            "broad-index performance as context rather than primary evidence",
            "exact research cut-off time and time zone",
        ]:
            self.assertIn(phrase, text)

    def test_checker_accepts_public_equity_framing_section_name(self) -> None:
        checker = read("skills/economic-impact-report/scripts/check_economic_impact_report.py")
        for phrase in [
            '"public equity framing"',
            '"event status and market baseline"',
            '"ranked equity impact map"',
            '"what is priced in vs what requires proof"',
            '"monitoring triggers and research queue"',
            '"event to equity transmission map"',
        ]:
            self.assertIn(phrase, checker)
        self.assertNotIn('"market framing"', checker)


if __name__ == "__main__":
    unittest.main()
