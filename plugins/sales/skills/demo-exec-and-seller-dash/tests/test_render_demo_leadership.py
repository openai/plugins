"""Regression coverage for leadership dashboards and shared demo rendering."""

from __future__ import annotations

import json
import re
import socket
import tempfile
import threading
import unittest
from pathlib import Path
from typing import Any

from sales_test_support import DEMO_RENDERER as RENDERER
from sales_test_support import SKILL_DIRECTORY, SalesTestCase


class LeadershipDashboardTests(SalesTestCase):
    def setUp(self) -> None:
        self.portfolio: dict[str, Any] = RENDERER.load_portfolio()

    def test_leadership_dashboard_uses_the_same_fictional_company_and_account_portfolio(
        self,
    ) -> None:
        leadership = RENDERER.load_leadership_data(portfolio=self.portfolio)
        portfolio_accounts = {
            account["account"]
            for group in RENDERER.EXPECTED_COUNTS
            for account in self.portfolio[group]
        }

        self.assertEqual(leadership["company"]["name"], self.portfolio["demo"]["company"])
        self.assertEqual(leadership["company"]["featuredSeller"], self.portfolio["seller"]["name"])
        self.assertEqual({deal["account"] for deal in leadership["topDeals"]}, portfolio_accounts)
        self.assertGreaterEqual(len(leadership["metrics"]), 6)
        self.assertGreaterEqual(len(leadership["signals"]), 5)
        self.assertGreaterEqual(len(leadership["decisions"]), 5)
        self.assertIn("fictional", leadership["disclosure"]["message"].lower())
        self.assertEqual(leadership["company"]["divisionLead"]["name"], "Maya Chen")
        self.assertEqual(leadership["company"]["division"], "North America Enterprise")
        self.assertEqual(leadership["reporting"]["teamAccountCount"], 38)
        self.assertEqual(leadership["reporting"]["teamOpportunityCount"], 31)
        self.assertEqual(len(leadership["divisionTeams"]), 3)
        self.assertEqual(
            sum(team["forecast"] for team in leadership["divisionTeams"]),
            leadership["forecast"]["base"],
        )

        northstar = next(
            deal for deal in leadership["topDeals"] if deal["account"] == "Northstar Health"
        )
        self.assertEqual(northstar["value"], 420000)
        self.assertEqual(northstar["stage"], "Security review")
        self.assertEqual(northstar["forecastCategory"].lower(), "best case")
        self.assertTrue(any(event["source"] == "Slack" for event in northstar["evidence"]))

    def test_leadership_reporting_scopes_reconcile_to_division_and_manager_totals(self) -> None:
        leadership = RENDERER.load_leadership_data(portfolio=self.portfolio)
        geographies = leadership["geographySummaries"]
        segments = leadership["segmentSummaries"]
        division = geographies["all"]
        regions = [geographies[team["region"]] for team in leadership["divisionTeams"]]
        industries = [segments[segment["name"]] for segment in leadership["segments"]]

        self.assertEqual(set(geographies), {"all", "West", "Central", "East"})
        self.assertEqual(
            set(segments),
            {"all", *(segment["name"] for segment in leadership["segments"])},
        )
        for field in (
            "forecast",
            "target",
            "accounts",
            "opportunities",
            "pipelineCreated",
            "closedWon",
            "weeklyMovement",
        ):
            with self.subTest(field=field):
                self.assertEqual(sum(region[field] for region in regions), division[field])
        for field in ("forecast", "target", "pipelineCreated", "closedWon", "weeklyMovement"):
            with self.subTest(segment_field=field):
                self.assertEqual(sum(industry[field] for industry in industries), division[field])

        self.assertEqual(sum(industry["accounts"] for industry in industries), 36)
        self.assertEqual(sum(industry["opportunities"] for industry in industries), 29)
        self.assertIn("two paused", segments["all"]["reportingBasis"].lower())
        for team in leadership["divisionTeams"]:
            with self.subTest(region=team["region"]):
                summary = geographies[team["region"]]
                self.assertEqual(summary["forecast"], team["forecast"])
                self.assertEqual(summary["target"], team["target"])
                self.assertEqual(sum(summary["forecastComponents"].values()), summary["forecast"])
                self.assertIn(team["manager"], summary["reportingBasis"])
        for industry in industries:
            with self.subTest(industry=industry["label"]):
                self.assertEqual(sum(industry["forecastComponents"].values()), industry["forecast"])

    def test_leadership_dashboard_has_three_focused_sections_without_global_filters(
        self,
    ) -> None:
        template = (
            SKILL_DIRECTORY / "assets" / "sales-leadership-dashboard.template.html"
        ).read_text(encoding="utf-8")

        self.assertEqual(
            re.findall(r'<section class="section" id="([^"]+)"', template),
            ["forecast", "accounts", "team"],
        )
        self.assertEqual(
            re.findall(r'<a(?: class="active")? href="#([^"]+)"', template),
            ["forecast", "accounts", "team"],
        )
        self.assert_contains(template, "Forecast &amp; key metrics", "Account Focus", "Team Focus")
        self.assert_excludes(
            template,
            'id="segment-filter"',
            'id="manager-filter"',
            'id="period-filter"',
            'id="geography-filter"',
            'id="product-filter"',
            'id="geography-switches"',
            'id="segment-switches"',
            'id="deal-search"',
            'id="deal-stage"',
            'id="deal-forecast"',
            'id="deal-motion"',
            'id="brief-toggle"',
            "Read-only leadership view",
            'class="read-only"',
            "Based on 0 material signals",
        )

    def test_leadership_briefings_are_visible_and_forecast_scenarios_stay_interactive(
        self,
    ) -> None:
        template = (
            SKILL_DIRECTORY / "assets" / "sales-leadership-dashboard.template.html"
        ).read_text(encoding="utf-8")

        for briefing_id in ("forecastBriefing", "accountBriefing"):
            with self.subTest(briefing=briefing_id):
                opening_tag = re.search(
                    rf'<[^>]+\bid="{re.escape(briefing_id)}"[^>]*>',
                    template,
                )
                self.assertIsNotNone(opening_tag)
                if opening_tag is not None:
                    self.assertNotRegex(opening_tag.group(0), r"\bhidden(?:\s|>|=)")
                    self.assertNotIn("aria-expanded", opening_tag.group(0))

        self.assert_contains(
            template,
            'id="scenario-tabs"',
            'id="sliders"',
            'id="forecast-position"',
            'id="forecast-total"',
            "data.forecast.scenarios",
            "data-scenario=",
            "below",
            "above",
        )

    def test_forecast_scenario_sliders_are_clear_and_preserve_drag_interaction(self) -> None:
        template_path = SKILL_DIRECTORY / "assets" / "sales-leadership-dashboard.template.html"
        template = template_path.read_text(encoding="utf-8")
        leadership = RENDERER.load_leadership_data(portfolio=self.portfolio)

        self.assertEqual(
            [scenario["label"] for scenario in leadership["forecast"]["scenarios"]],
            ["Conservative", "Expected", "Stretch"],
        )
        self.assertEqual(
            leadership["forecast"]["previousQuarter"],
            {
                "label": "Last quarter",
                "commitCloseRate": 94,
                "additionalPipelineWinRate": 37,
                "dealSizeUplift": 6,
            },
        )
        for label, definition in (
            ("Commit close rate", "Committed deals expected to close this quarter."),
            (
                "Additional pipeline win rate",
                "Other qualified opportunities expected to close.",
            ),
            (
                "Average deal-size uplift",
                "Added value on eligible expansion deals that close.",
            ),
        ):
            with self.subTest(control=label):
                self.assertIn(label, template)
                self.assertIn(definition, template)

        self.assertIn('if (!sliderRoot.querySelector("[data-slider]"))', template)
        self.assertIn('control.addEventListener("input"', template)
        self.assertIn('data-slider-impact="', template)
        self.assertIn('control.setAttribute("aria-valuetext"', template)
        self.assertIn('typeof benchmark === "number" && Number.isFinite(benchmark)', template)
        self.assertIn('class="slider-baseline"', template)
        self.assertIn('class="slider-info" type="button"', template)
        self.assertIn('role="tooltip"', template)
        self.assert_matches(
            template,
            (
                r"\.sliders\s*\{[^}]*grid-template-columns:\s*"
                r"repeat\(3,\s*minmax\(0,\s*1fr\)\);"
                r"[^}]*grid-template-rows:\s*repeat\(4,\s*auto\);"
            ),
            (
                r"\.scenario-control\s*\{[^}]*display:\s*grid;"
                r"[^}]*grid-row:\s*span\s+4;[^}]*grid-template-rows:\s*subgrid;"
            ),
            r"\.slider-caption\s*\{[^}]*min-height:\s*3\.1em;",
            r"\.slider-baseline\s*\{[^}]*min-height:\s*1\.55em;",
            r'\.sliders input\[type="range"\]\s*\{[^}]*margin-top:\s*0;',
        )
        self.assertIn('class="slider-baseline" aria-hidden="true"', template)
        self.assert_matches(
            template,
            (
                r"\.slider-definition\s*\{[^}]*position:\s*absolute;"
                r"[^}]*visibility:\s*hidden;"
            ),
            (
                r"\.slider-info:hover\s*\+\s*\.slider-definition,\s*"
                r"\.slider-info:focus\s*\+\s*\.slider-definition\s*\{"
                r"[^}]*visibility:\s*visible;"
            ),
            (
                r"\.slider-caption strong\s*\{[^}]*inline-size:\s*4\.5ch;"
                r"[^}]*font-variant-numeric:\s*tabular-nums;"
            ),
            (
                r"\.forecast-gap-value\s*\{[^}]*inline-size:\s*7ch;"
                r"[^}]*font-variant-numeric:\s*tabular-nums;"
            ),
        )
        self.assertNotIn('$("sliders").innerHTML = controls.map', template)
        self.assertNotIn("Commit realization", template)
        self.assertNotIn("Best-case conversion", template)
        self.assertNotIn("Upside capture", template)

        drag_check = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const template = fs.readFileSync(process.argv[1], 'utf8');
const match = template.match(
  /function renderScenarioControls\(components\) \{([\s\S]*?)\n        \}/
);
assert.ok(match, 'Scenario sliders must have a stable, independently testable render function');

class Slider {
  constructor(key) {
    this.dataset = {slider: key};
    this.value = '';
    this.handlers = {};
    this.attributes = {};
  }
  addEventListener(type, callback) { this.handlers[type] = callback; }
  setAttribute(name, value) { this.attributes[name] = value; }
}

const root = {
  writes: 0,
  sliders: [],
  values: {},
  impacts: {},
  set innerHTML(markup) {
    this.writes += 1;
    this.markup = markup;
    const keys = [...markup.matchAll(/\sdata-slider="([^"]+)"/g)].map(match => match[1]);
    this.sliders = keys.map(key => new Slider(key));
    this.values = Object.fromEntries(keys.map(key => [key, {textContent: ''}]));
    this.impacts = Object.fromEntries(keys.map(key => [key, {textContent: ''}]));
  },
  querySelector(selector) {
    if (selector === '[data-slider]') return this.sliders[0] || null;
    const match = selector.match(/^\[data-slider(-value|-impact)?="([^"]+)"\]$/);
    if (!match) return null;
    if (match[1] === '-value') return this.values[match[2]];
    if (match[1] === '-impact') return this.impacts[match[2]];
    return this.sliders.find(slider => slider.dataset.slider === match[2]) || null;
  },
  querySelectorAll(selector) { return selector === '[data-slider]' ? this.sliders : []; }
};

const state = {
  sliders: {commitCloseRate: 100, additionalPipelineWinRate: 40, dealSizeUplift: 0}
};
const data = {
  forecast: {
    previousQuarter: {
      label: 'Last quarter',
      commitCloseRate: 94,
      additionalPipelineWinRate: 37,
      dealSizeUplift: 6
    }
  }
};
const components = [
  {key: 'commit', adjusted: 2720000},
  {key: 'bestCase', adjusted: 1700000},
  {key: 'upside', adjusted: 0}
];
let redraws = 0;
const renderer = new Function('components', '$', 'state', 'escape', 'money', 'renderForecast',
  'data', match[1]);
const money = value => '$' + Math.round(value).toLocaleString('en-US');
function draw() {
  renderer(components, () => root, state, value => String(value), money, updateForecast, data);
}
function updateForecast() {
  redraws += 1;
  components[1].adjusted = 4250000 * state.sliders.additionalPipelineWinRate / 100;
  draw();
}

draw();
assert.equal(root.writes, 1);
assert.match(root.markup, /id="slider-baseline-commitCloseRate">Last quarter: 94%/);
assert.match(root.markup, /id="slider-baseline-additionalPipelineWinRate">Last quarter: 37%/);
assert.match(root.markup, /id="slider-baseline-dealSizeUplift">Last quarter: 6%/);
assert.match(root.markup,
  /aria-describedby="slider-definition-additionalPipelineWinRate slider-baseline-additionalPipelineWinRate"/);
assert.equal((root.markup.match(/class="slider-info"/g) || []).length, 3);
assert.equal((root.markup.match(/role="tooltip"/g) || []).length, 3);
assert.match(root.markup,
  /aria-label="About Additional pipeline win rate" aria-describedby="slider-definition-additionalPipelineWinRate"/);
assert.match(root.markup,
  /id="slider-definition-additionalPipelineWinRate" role="tooltip">Other qualified opportunities expected to close\./);
assert.doesNotMatch(root.markup, /<label class="scenario-control">/);
const original = root.sliders.find(slider => slider.dataset.slider === 'additionalPipelineWinRate');
for (const value of ['44', '46', '48']) {
  original.value = value;
  original.handlers.input();
  assert.strictEqual(root.sliders[1], original,
    'Dragging must never replace the active input element during a forecast redraw');
  assert.equal(root.writes, 1, 'Slider markup is mounted once and remains stable throughout drag');
}
assert.equal(redraws, 3);
assert.equal(state.sliders.additionalPipelineWinRate, 48);
assert.equal(root.values.additionalPipelineWinRate.textContent, '48%');
assert.match(root.impacts.additionalPipelineWinRate.textContent, /2,040,000/);
assert.match(original.attributes['aria-valuetext'], /48%;/);
"""

        self.assert_node_script(drag_check, str(template_path))

    def test_leadership_account_focus_is_ranked_actionable_and_source_grounded(
        self,
    ) -> None:
        leadership = RENDERER.load_leadership_data(portfolio=self.portfolio)
        account_overview = leadership["accountOverview"]
        portfolio_rows = {
            account["account"]: account
            for group in RENDERER.EXPECTED_COUNTS
            for account in self.portfolio[group]
        }
        template = (
            SKILL_DIRECTORY / "assets" / "sales-leadership-dashboard.template.html"
        ).read_text(encoding="utf-8")

        self.assertGreater(len(account_overview), len(portfolio_rows))
        self.assertEqual(
            len(account_overview),
            len(portfolio_rows) + len(leadership["divisionAccounts"]),
        )
        self.assertEqual(
            [account["priorityRank"] for account in account_overview],
            list(range(1, len(account_overview) + 1)),
        )
        priorities = {"High": 0, "Action": 1, "Watch": 2, "Paused": 3}
        self.assertEqual(
            [priorities[account["priority"]] for account in account_overview],
            sorted(priorities[account["priority"]] for account in account_overview),
        )
        self.assertEqual(
            [account["name"] for account in account_overview[:3]],
            ["Northstar Health", "Atlas Manufacturing", "Solstice Financial"],
        )
        division_accounts = {
            account["account"]: account for account in leadership["divisionAccounts"]
        }
        valid_sellers = {seller["name"] for seller in leadership["sellerOverview"]}
        for account in account_overview:
            with self.subTest(account=account["name"]):
                self.assertIn(account["seller"], valid_sellers)
                if account["name"] in portfolio_rows:
                    portfolio_row = portfolio_rows[account["name"]]
                    self.assertEqual(account["seller"], portfolio_row["owner"])
                    self.assertEqual(
                        account["value"],
                        int(portfolio_row["value"].replace("$", "").replace(",", "")),
                    )
                else:
                    self.assertIn(account["name"], division_accounts)
                    self.assertEqual(account["value"], division_accounts[account["name"]]["value"])
                    self.assertEqual(account["seller"], division_accounts[account["name"]]["owner"])
                for field in ("headline", "briefing", "nextStep"):
                    self.assertTrue(account[field], field)
                for field in ("rationale", "monitor", "unblock", "sourceEvidence"):
                    self.assertTrue(account[field], field)

        northstar = account_overview[0]
        self.assertEqual(northstar["name"], "Northstar Health")
        self.assertEqual(northstar["value"], 420000)
        self.assertEqual(northstar["seller"], "Riley Morgan")
        priority_context = " ".join(
            (
                northstar["briefing"],
                *northstar["monitor"],
                *northstar["unblock"],
                northstar["nextStep"],
            )
        ).lower()
        self.assertIn("pilot", priority_context)
        self.assertIn("uptime", priority_context)
        self.assert_contains(
            template,
            "focus-account-row",
            "data-account-id",
            'id="accountFocusDetail"',
            "Account Context and Recommended Action",
            "Recommended executive action",
            "Priority Rationale",
            "What to monitor",
        )

    def test_leadership_account_rows_visually_separate_customer_names_and_stages(
        self,
    ) -> None:
        template = (
            SKILL_DIRECTORY / "assets" / "sales-leadership-dashboard.template.html"
        ).read_text(encoding="utf-8")

        self.assertIn(
            '<span class="account-label"><span class="account-name">',
            template,
        )
        self.assertIn('<span class="account-subline">', template)
        self.assertIn('escape(account.stage || account.type || "Opportunity review")', template)
        self.assert_matches(
            template,
            (
                r"\.account-label\s*\{[^}]*display:\s*flex;"
                r"[^}]*flex-direction:\s*column;[^}]*gap:\s*(?:[5-9]|1[0-2])px;"
            ),
            r"\.account-name,\s*\.account-subline\s*\{[^}]*display:\s*block;",
        )
        self.assertIn('aria-controls="account-drawer"', template)
        row_renderer = template.split("function renderAccountFocus()", maxsplit=1)[1].split(
            "function openAccountDrawer(", maxsplit=1
        )[0]
        self.assertNotIn("Manager-reported", row_renderer)
        self.assertNotIn("account-scope-badge", row_renderer)
        self.assertIn("Manager-reported summary only", template)

    def test_leadership_account_table_opens_shared_accessible_right_side_account_drawer(
        self,
    ) -> None:
        template = (
            SKILL_DIRECTORY / "assets" / "sales-leadership-dashboard.template.html"
        ).read_text(encoding="utf-8")

        self.assert_shared_accessible_account_drawer(template, detail_id="accountFocusDetail")
        self.assertRegex(
            template,
            r"\.account-workspace\s*\{[^}]*display:\s*block;[^}]*width:\s*100%;",
        )
        account_section = re.search(
            r'<section class="section" id="accounts">(?P<body>.*?)</section>',
            template,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(account_section)
        if account_section is not None:
            account_markup = account_section.group("body")
            self.assertIn('<div class="account-workspace">', account_markup)
            self.assertIn('<div class="account-list">', account_markup)
            self.assertNotIn('id="accountFocusDetail"', account_markup)
            for column in ("Account", "Size", "Seller", "Priority"):
                with self.subTest(column=column):
                    self.assertIn(f">{column}</span>", account_markup)
        self.assertIn('aria-controls="account-drawer"', template)
        self.assertIn("openAccountDrawer(account, button)", template)
        self.assertIn("if (event.target === drawer) closeAccountDrawer()", template)
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

    def test_leadership_account_table_passes_boundary_scrolling_to_the_page(self) -> None:
        template = (
            SKILL_DIRECTORY / "assets" / "sales-leadership-dashboard.template.html"
        ).read_text(encoding="utf-8")
        styles = re.search(r"#accountFocusList\s*\{(?P<body>[^}]+)\}", template)

        self.assertIsNotNone(styles)
        if styles is not None:
            self.assertRegex(styles.group("body"), r"overflow-y:\s*auto")
            self.assertRegex(styles.group("body"), r"overscroll-behavior-y:\s*auto")
            self.assertNotRegex(
                styles.group("body"),
                r"overscroll-behavior(?:-y)?:\s*(?:contain|none)",
            )

    def test_leadership_account_ownership_spans_real_division_sellers_without_changing_jordans_book(
        self,
    ) -> None:
        leadership = RENDERER.load_leadership_data(portfolio=self.portfolio)
        featured_seller = self.portfolio["seller"]["name"]
        seller_roster = {seller["name"]: seller for seller in leadership["sellerOverview"]}
        portfolio_accounts = {
            account["account"]: account
            for group in RENDERER.EXPECTED_COUNTS
            for account in self.portfolio[group]
        }
        division_accounts = leadership["divisionAccounts"]
        executive_accounts = leadership["accountOverview"]

        self.assertGreaterEqual(len(division_accounts), 5)
        self.assertTrue(
            {account["account"] for account in division_accounts}.isdisjoint(portfolio_accounts)
        )
        self.assertEqual(
            {account["seller"] for account in executive_accounts},
            set(seller_roster),
        )
        for account in division_accounts:
            with self.subTest(account=account["account"]):
                self.assertIn(account["owner"], seller_roster)
                self.assertNotEqual(account["owner"], featured_seller)
                self.assertEqual(
                    account["manager"],
                    seller_roster[account["owner"]]["manager"],
                )
                self.assertTrue(account["sourceEvidence"])

        self.assertEqual(
            {deal["owner"] for deal in leadership["topDeals"]},
            {featured_seller},
        )
        self.assertEqual(
            {account["owner"] for account in portfolio_accounts.values()},
            {featured_seller},
        )
        self.assertEqual(
            {
                account["name"]
                for account in executive_accounts
                if account["seller"] == featured_seller
            },
            set(portfolio_accounts),
        )
        self.assertEqual(executive_accounts[0]["name"], "Northstar Health")
        self.assertEqual(executive_accounts[0]["seller"], featured_seller)
        self.assertEqual(
            sum(seller["forecast"] for seller in seller_roster.values()),
            leadership["forecast"]["base"],
        )
        self.assertEqual(
            leadership["reporting"]["samplePortfolioValue"],
            sum(
                int(account["value"].replace("$", "").replace(",", ""))
                for account in portfolio_accounts.values()
            ),
        )

    def test_leadership_team_focus_reconciles_and_never_invents_seller_growth(
        self,
    ) -> None:
        leadership = RENDERER.load_leadership_data(portfolio=self.portfolio)
        teams = leadership["teamFocus"]
        template = (
            SKILL_DIRECTORY / "assets" / "sales-leadership-dashboard.template.html"
        ).read_text(encoding="utf-8")

        self.assertEqual(len(teams), len(leadership["divisionTeams"]))
        self.assertEqual(sum(team["forecast"] for team in teams), leadership["forecast"]["base"])
        self.assertEqual(sum(team["target"] for team in teams), leadership["forecast"]["target"])
        self.assertEqual(
            sum(team["accounts"] for team in teams), leadership["reporting"]["teamAccountCount"]
        )
        self.assertEqual(
            sum(team["opportunities"] for team in teams),
            leadership["reporting"]["teamOpportunityCount"],
        )

        nested_sellers = []
        for team in teams:
            with self.subTest(manager=team["name"]):
                previous_forecast = team["forecast"] - team["weeklyMovement"]
                self.assertGreater(previous_forecast, 0)
                self.assertAlmostEqual(
                    team["growthRate"],
                    round(team["weeklyMovement"] / previous_forecast * 100, 1),
                    places=1,
                )
                self.assertEqual(team["growthBasis"], "Regional forecast week-over-week")
                self.assertTrue(team["wins"])
                self.assertTrue(team["attention"])
                self.assertTrue(team["sellers"])
                for seller in team["sellers"]:
                    with self.subTest(seller=seller["name"]):
                        self.assertEqual(seller["manager"], team["name"])
                        self.assertIsNone(seller["growthRate"])
                        self.assertEqual(
                            seller["growthBasis"],
                            "Individual seller growth is not reported.",
                        )
                        self.assertTrue(seller["goingWell"])
                        self.assertTrue(seller["needsAttention"])
                        nested_sellers.append(seller)

        self.assertEqual(len(nested_sellers), len(leadership["sellerOverview"]))
        self.assert_contains(
            template,
            'id="teamFocusGrid"',
            'aria-label="Regional manager performance"',
            'aria-label="Account executive performance"',
            "performance-row",
            "Outperforming",
            "Behind plan",
            "What's going well",
            "Needs attention",
        )
        self.assertNotIn('class="team-focus-card"', template)
        self.assertNotIn('class="seller-card"', template)

    def test_leadership_performance_tables_open_source_grounded_detail_drawers(self) -> None:
        template_path = SKILL_DIRECTORY / "assets" / "sales-leadership-dashboard.template.html"
        template = template_path.read_text(encoding="utf-8")

        tables = re.findall(
            r'<table class="performance-table" aria-label="([^"]+)">(?P<body>.*?)</table>',
            template,
            flags=re.DOTALL,
        )
        self.assertEqual(
            [name for name, _ in tables],
            ["Regional manager performance", "Account executive performance"],
        )
        for name, markup in tables:
            headers = re.findall(r"<th>([^<]+)</th>", markup)
            for dimension in ("Region", "Forecast / Target", "Attainment", "Accounts", "Status"):
                with self.subTest(table=name, dimension=dimension):
                    self.assertIn(dimension, headers)
            if name == "Regional manager performance":
                self.assertIn("Weekly growth", headers)
                self.assertIn('id="teamFocusGrid"', markup)
            else:
                self.assertNotIn("Weekly growth", headers)
                self.assertIn("Manager", headers)
                self.assertIn('id="seller-grid"', markup)

        self.assertIn("function openPerformanceDrawer(person, kind, row)", template)
        self.assertIn("function renderPerformanceDetail(person, kind)", template)
        self.assertIn("function bindPerformanceRows(container, people, kind)", template)
        self.assertIn('row.addEventListener("click", open)', template)
        self.assertIn('row.addEventListener("keydown"', template)
        self.assertIn('aria-controls="account-drawer"', template)
        self.assertIn('$("account-drawer-title").textContent', template)

        performance_check = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const template = fs.readFileSync(process.argv[1], 'utf8');
function bodyFor(name) {
  const match = template.match(new RegExp(
    'function ' + name + '\\([^)]*\\) \\{([\\s\\S]*?)\\n        \\}'
  ));
  assert.ok(match, 'Leadership helper ' + name + ' must exist');
  return match[1];
}

const status = new Function('attainment', bodyFor('performanceStatus'));
assert.deepEqual(status(103), {label: 'Outperforming', tone: 'outperforming'});
assert.deepEqual(status(100), {label: 'Outperforming', tone: 'outperforming'});
assert.deepEqual(status(99.9), {label: 'Behind plan', tone: 'behind'});

const list = value => Array.isArray(value) ? value.filter(Boolean) : value ? [value] : [];
const attention = new Function('account', 'decision', 'details', 'list',
  bodyFor('executiveAttention'));
const northstar = attention({
  headline: 'Pilot review upcoming',
  briefing: 'The $420,000 expansion is at risk because unresolved customer uptime feedback blocks the buyer decision.',
  monitor: ['The pilot scorecard and uptime concern are not validated.']
}, {}, {}, list);
assert.equal(northstar.label, 'Deal at risk');
assert.match(northstar.context, /uptime/i);
assert.notEqual(northstar.context, 'Pilot review upcoming');
assert.equal(attention({briefing: 'The opportunity has stalled after the customer freeze.'}, {}, {}, list).label,
  'Opportunity is stalling');
assert.equal(attention({briefing: 'The implementation ownership is missing.'}, {}, {}, list).label,
  'Ownership gap');
assert.equal(attention({briefing: 'A new seller needs reviewed support before the buyer decision.'}, {}, {}, list).label,
  'Seller support needed');
"""
        self.assert_node_script(performance_check, str(template_path))

    def test_seller_overview_reconciles_to_every_manager_and_division_total(self) -> None:
        leadership = RENDERER.load_leadership_data(portfolio=self.portfolio)
        sellers = leadership["sellerOverview"]

        self.assertEqual(len(sellers), 6)
        self.assertEqual(
            sum(seller["forecast"] for seller in sellers), leadership["forecast"]["base"]
        )
        self.assertEqual(
            sum(seller["target"] for seller in sellers), leadership["forecast"]["target"]
        )
        self.assertEqual(sum(seller["accounts"] for seller in sellers), 38)
        self.assertEqual(sum(seller["opportunities"] for seller in sellers), 31)
        self.assertEqual(
            [seller["name"] for seller in sellers if seller.get("featured")],
            [self.portfolio["seller"]["name"]],
        )

        for team in leadership["divisionTeams"]:
            with self.subTest(manager=team["manager"]):
                manager_sellers = [
                    seller for seller in sellers if seller["manager"] == team["manager"]
                ]
                self.assertTrue(manager_sellers)
                self.assertEqual(
                    sum(seller["forecast"] for seller in manager_sellers), team["forecast"]
                )
                self.assertEqual(
                    sum(seller["target"] for seller in manager_sellers), team["target"]
                )

    def test_demo_performance_shows_realistic_winners_risks_and_regional_momentum(self) -> None:
        leadership = RENDERER.load_leadership_data(portfolio=self.portfolio)
        teams = leadership["divisionTeams"]
        sellers = leadership["sellerOverview"]
        above_plan = [seller for seller in sellers if seller["forecast"] >= seller["target"]]
        below_plan = [seller for seller in sellers if seller["forecast"] < seller["target"]]

        self.assertGreaterEqual(len(above_plan), 2)
        self.assertGreaterEqual(len(below_plan), 2)
        self.assertTrue(any(team["forecast"] >= team["target"] for team in teams))
        self.assertTrue(any(team["forecast"] < team["target"] for team in teams))
        regional_movements = [
            leadership["geographySummaries"][team["region"]]["weeklyMovement"] for team in teams
        ]
        self.assertTrue(any(movement > 0 for movement in regional_movements))
        self.assertTrue(any(movement < 0 for movement in regional_movements))
        self.assertEqual(sum(regional_movements), leadership["forecast"]["weeklyMovement"])
        self.assertEqual(
            {segment["tone"] for segment in leadership["segments"]},
            {"positive", "neutral", "attention"},
        )
        self.assertEqual(
            {metric["tone"] for metric in leadership["momentum"]},
            {"positive", "attention"},
        )

        template = (
            SKILL_DIRECTORY / "assets" / "sales-leadership-dashboard.template.html"
        ).read_text(encoding="utf-8")
        self.assertIn(".performance-growth.negative { color: var(--amber); }", template)
        self.assertIn('Number(person.growthRate) < 0 ? " negative" : ""', template)

    def test_fictional_sales_people_have_distinct_first_names(self) -> None:
        leadership = RENDERER.load_leadership_data(portfolio=self.portfolio)
        people = {leadership["company"]["divisionLead"]["name"]}
        people.update(team["manager"] for team in leadership["divisionTeams"])
        people.update(seller["name"] for seller in leadership["sellerOverview"])

        for group in RENDERER.EXPECTED_COUNTS:
            for account in self.portfolio[group]:
                contact = account.get("primaryContact")
                if isinstance(contact, str):
                    people.add(contact.split(" · ", maxsplit=1)[0])
        for detail in self.portfolio["accountDetails"].values():
            for stakeholder in detail.get("stakeholders", []):
                people.add(stakeholder["name"])
        for deal in leadership["topDeals"]:
            for buyer_field in ("executiveBuyer", "technicalBuyer"):
                buyer = deal.get(buyer_field)
                if isinstance(buyer, str):
                    people.add(buyer.split(" · ", maxsplit=1)[0])

        people_by_first_name: dict[str, list[str]] = {}
        for person in sorted(people):
            if re.fullmatch(r"[A-Z][a-z]+ [A-Z][a-z]+", person):
                people_by_first_name.setdefault(person.split()[0], []).append(person)
        repeated_first_names = {
            name: identities
            for name, identities in people_by_first_name.items()
            if len(identities) > 1
        }
        self.assertEqual(repeated_first_names, {})

    def test_leadership_loader_rejects_unreconciled_seller_overview(self) -> None:
        leadership = RENDERER.load_leadership_data(portfolio=self.portfolio)
        leadership["sellerOverview"][0]["forecast"] += 1000

        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_path = Path(temporary_directory) / "leadership.json"
            fixture_path.write_text(json.dumps(leadership), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "Seller forecast amounts must reconcile"):
                RENDERER.load_leadership_data(fixture_path, self.portfolio)

    def test_leadership_real_data_requires_verified_sources_and_avoids_sample_defaults(
        self,
    ) -> None:
        template = (
            SKILL_DIRECTORY / "assets" / "sales-leadership-dashboard.template.html"
        ).read_text(encoding="utf-8")

        self.assertIn("source.verified === true", template)
        self.assertIn(".navigation a[hidden] { display: none !important; }", template)
        self.assertIn('$("viewer-persona").textContent', template)
        self.assertIn("decision.problem || decision.rationale", template)
        self.assertIn("decision.proposedSolution ||", template)
        self.assertIn("Array.isArray(decision.sourceEvidence)", template)
        self.assertNotIn("same ten accounts from Riley’s priority view", template)
        self.assertNotIn(
            '["Northstar Health", "Atlas Manufacturing", "Solstice Financial"].includes',
            template,
        )

    def test_renderer_creates_complete_standalone_leadership_dashboard(self) -> None:
        leadership = RENDERER.load_leadership_data(portfolio=self.portfolio)

        with tempfile.TemporaryDirectory() as temporary_directory:
            output_path = Path(temporary_directory) / "leadership" / "index.html"
            dashboard_path = RENDERER.render_leadership_dashboard(
                leadership,
                output_path=output_path,
            )
            rendered = dashboard_path.read_text(encoding="utf-8")

        self.assertEqual(dashboard_path, output_path.resolve())
        self.assertNotIn(RENDERER.LEADERSHIP_PLACEHOLDER, rendered)
        self.assertIn("Revenue Leadership Command Center", rendered)
        self.assertIn("Forecast &amp; key metrics", rendered)
        self.assertIn("Account Focus", rendered)
        self.assertIn("Team Focus", rendered)
        self.assertEqual(
            re.findall(r'<section class="section" id="([^"]+)"', rendered),
            ["forecast", "accounts", "team"],
        )
        self.assertIn("What to monitor", rendered)
        self.assertIn("Account Context and Recommended Action", rendered)
        self.assertIn("Recommended executive action", rendered)
        self.assertIn("Priority Rationale", rendered)
        self.assertIn("What's going well", rendered)
        self.assertIn("Needs attention", rendered)
        self.assertIn("below", rendered)
        self.assertIn("above", rendered)
        self.assertIn("Northstar Health", rendered)
        self.assertIn("Harbor Technologies", rendered)
        self.assertIn("Meridian Governance Verified Controls", rendered)
        self.assertIn("fictional", rendered.lower())
        self.assertIn('id="viewer-persona"', rendered)
        self.assertIn("data.company?.divisionLead?.name", rendered)
        self.assertIn("data.company?.leadershipRole ||", rendered)
        self.assertIn("replace(/^Your third-largest opportunity:/i", rendered)
        self.assertIn('replace(/^Your (?=\\$)/i, "A ")', rendered)
        self.assertIn("top?.briefing || top?.headline", rendered)
        self.assertNotIn("material customer-level lever", rendered)
        self.assertNotIn("no SLA breach, cause, or guaranteed fix is established", rendered)
        self.assertIn("Decision after pilot review", rendered)
        self.assertNotIn("Thursday decision", rendered)
        self.assertIn('id="forecastBriefing"', rendered)
        self.assertIn('id="accountBriefing"', rendered)
        self.assertIn('id="accountFocusDetail"', rendered)
        self.assertIn('id="teamFocusGrid"', rendered)
        self.assertIn('<footer class="shell dashboard-footer">', rendered)
        self.assertEqual(rendered.count('id="disclosure"'), 1)

    def test_leadership_template_preserves_aligned_gutters_and_responsive_metric_cards(
        self,
    ) -> None:
        template = (
            SKILL_DIRECTORY / "assets" / "sales-leadership-dashboard.template.html"
        ).read_text(encoding="utf-8")

        self.assertIn("--page-gutter:", template)
        self.assertRegex(
            template,
            r"\.shell\s*\{[^}]*padding-right:\s*var\(--page-gutter\);"
            r"[^}]*padding-left:\s*var\(--page-gutter\);",
        )
        self.assertRegex(template, r"main\s*\{[^}]*padding-top:\s*64px")
        self.assertRegex(
            template,
            r"\.kpi-strip\s*\{[^}]*grid-template-columns:\s*"
            r"repeat\(4,\s*minmax\(0,\s*1fr\)\)",
        )
        self.assertIn("@media (max-width: 980px)", template)
        self.assertIn("@media (max-width: 700px)", template)
        self.assertIn("@media (max-width: 460px)", template)
        self.assertIn(".kpi-strip { grid-template-columns: repeat(2, minmax(0, 1fr))", template)
        self.assertIn(".kpi-strip { grid-template-columns: 1fr; }", template)
        self.assertIn(".performance-table-wrap { overflow-x: auto; }", template)
        self.assertIn(".performance-table { min-width: 760px; }", template)
        self.assertIn(
            ".account-list-header .seller-column, .focus-account-row .seller-column", template
        )

    def test_meeting_transcript_and_crm_rules_define_reviewable_safe_update(self) -> None:
        transcript = (SKILL_DIRECTORY / "references" / "northstar-followup-meeting.md").read_text(
            encoding="utf-8"
        )
        rules = (SKILL_DIRECTORY / "references" / "crm-update-rules.md").read_text(encoding="utf-8")
        salesforce = (SKILL_DIRECTORY / "references" / "sources" / "salesforce.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("## Condensed Transcript", transcript)
        self.assertIn("## Proposed Review-Only Salesforce Changes", transcript)
        self.assertIn("Primary meeting goal", transcript)
        self.assertIn("Jordan Lee", transcript)
        self.assertIn("Casey Patel", transcript)
        self.assertIn("Priya Shah", transcript)
        self.assertIn("4,500", transcript)
        self.assertIn("$420,000", transcript)
        for field in ("Next Step", "Deal Notes", "Decision Criteria", "Risks and Asks"):
            with self.subTest(field=field):
                self.assertIn(field, transcript)
                self.assertIn(field, rules)
        for unchanged in ("Security review", "$420,000", "Best Case"):
            with self.subTest(unchanged=unchanged):
                self.assertIn(unchanged, transcript)
                self.assertIn(unchanged, rules)
                self.assertIn(unchanged, salesforce)
        self.assertIn("explicitly approves the exact proposal", rules)
        self.assertIn("never calls a write tool", rules)

    def test_local_server_serves_account_and_leadership_dashboards_together(self) -> None:
        leadership = RENDERER.load_leadership_data(portfolio=self.portfolio)

        with tempfile.TemporaryDirectory() as temporary_directory:
            root_directory = Path(temporary_directory)
            account_path = RENDERER.render_dashboard(
                self.portfolio,
                output_path=root_directory / "index.html",
            )
            RENDERER.render_leadership_dashboard(
                leadership,
                output_path=root_directory / "leadership" / "index.html",
            )

            with RENDERER.create_dashboard_server(
                account_path, root_directory=root_directory
            ) as server:
                server_thread = threading.Thread(target=server.serve_forever, daemon=True)
                server_thread.start()
                try:
                    for route, expected in (
                        ("/", "Riley’s Account Home"),
                        ("/leadership/", "Revenue Leadership Command Center"),
                    ):
                        with self.subTest(route=route):
                            with socket.create_connection(
                                server.server_address, timeout=3
                            ) as connection:
                                connection.sendall(
                                    f"GET {route} HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n".encode()
                                )
                                chunks: list[bytes] = []
                                while chunk := connection.recv(65536):
                                    chunks.append(chunk)
                                html = b"".join(chunks).decode("utf-8")

                            self.assertIn("200 OK", html)
                            self.assertIn(expected, html)
                finally:
                    server.shutdown()
                    server_thread.join(timeout=3)

    def test_renderer_escapes_script_tag_data(self) -> None:
        portfolio = json.loads(json.dumps(self.portfolio))
        portfolio["workNow"][0]["whyItMatters"] = "</script><script>alert('unsafe')</script>"

        with tempfile.TemporaryDirectory() as temporary_directory:
            output_path = Path(temporary_directory) / "index.html"
            rendered = RENDERER.render_dashboard(portfolio, output_path=output_path).read_text(
                encoding="utf-8"
            )

        self.assertNotIn("</script><script>alert('unsafe')</script>", rendered)
        self.assertIn("\\u003c/script>\\u003cscript>alert('unsafe')\\u003c/script>", rendered)

    def test_local_server_binds_only_to_loopback_and_serves_the_dashboard(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_path = Path(temporary_directory) / "index.html"
            dashboard_path = RENDERER.render_dashboard(self.portfolio, output_path=output_path)

            with RENDERER.create_dashboard_server(dashboard_path) as server:
                server_thread = threading.Thread(target=server.serve_forever, daemon=True)
                server_thread.start()

                try:
                    self.assertEqual(server.server_address[0], "127.0.0.1")
                    with socket.create_connection(server.server_address, timeout=3) as connection:
                        connection.sendall(
                            b"GET / HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n"
                        )
                        chunks: list[bytes] = []
                        while chunk := connection.recv(65536):
                            chunks.append(chunk)
                        html = b"".join(chunks).decode("utf-8")

                    self.assertIn("200 OK", html)
                    self.assertIn(self.portfolio["workNow"][0]["account"], html)
                    self.assertIn(self.portfolio["watch"][0]["account"], html)
                finally:
                    server.shutdown()
                    server_thread.join(timeout=3)

    def test_loader_rejects_missing_fictional_disclosure(self) -> None:
        portfolio = json.loads(json.dumps(self.portfolio))
        portfolio["demo"]["mode"] = "live"

        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_path = Path(temporary_directory) / "portfolio.json"
            fixture_path.write_text(json.dumps(portfolio), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "fictional demo mode"):
                RENDERER.load_portfolio(fixture_path)

    def test_loader_rejects_duplicate_accounts(self) -> None:
        portfolio = json.loads(json.dumps(self.portfolio))
        portfolio["watch"][0]["account"] = portfolio["workNow"][0]["account"]

        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_path = Path(temporary_directory) / "portfolio.json"
            fixture_path.write_text(json.dumps(portfolio), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "Duplicate demo account"):
                RENDERER.load_portfolio(fixture_path)

    def test_leadership_fixture_reuses_the_same_accounts_values_and_seller(self) -> None:
        leadership = RENDERER.load_leadership_data(portfolio=self.portfolio)
        account_rows = {
            account["account"]: account
            for group in RENDERER.EXPECTED_COUNTS
            for account in self.portfolio[group]
        }

        self.assertEqual(leadership["company"]["name"], self.portfolio["demo"]["company"])
        self.assertEqual(leadership["company"]["featuredSeller"], self.portfolio["seller"]["name"])
        self.assertEqual(leadership["company"]["salesLeader"], "Maya Chen")
        self.assertEqual(leadership["company"]["regionalManager"], "Sam Rivera")
        self.assertIn("Vice President", leadership["company"]["leadershipRole"])
        self.assertEqual(leadership["reporting"]["sampleAccountCount"], len(account_rows))
        self.assertIn("fictional", leadership["disclosure"]["message"].lower())
        self.assertGreaterEqual(len(leadership["metrics"]), 6)
        self.assertGreaterEqual(len(leadership["signals"]), 4)
        self.assertGreaterEqual(len(leadership["decisions"]), 4)

        for deal in leadership["topDeals"]:
            with self.subTest(account=deal["account"]):
                matching_account = account_rows[deal["account"]]
                expected_value = int(matching_account["value"].replace("$", "").replace(",", ""))
                self.assertEqual(deal["value"], expected_value)
                self.assertEqual(deal["owner"], matching_account["owner"])

        northstar = next(
            deal for deal in leadership["topDeals"] if deal["account"] == "Northstar Health"
        )
        self.assertEqual(northstar["stage"], "Security review")
        self.assertEqual(northstar["forecastCategory"].lower(), "best case")

    def test_leadership_renderer_creates_safe_standalone_shared_scenario_dashboard(self) -> None:
        leadership = RENDERER.load_leadership_data(portfolio=self.portfolio)

        with tempfile.TemporaryDirectory() as temporary_directory:
            output_path = Path(temporary_directory) / "leadership" / "index.html"
            leadership_path = RENDERER.render_leadership_dashboard(
                leadership, output_path=output_path
            )
            rendered = leadership_path.read_text(encoding="utf-8")

        self.assertEqual(leadership_path, output_path.resolve())
        self.assertNotIn(RENDERER.LEADERSHIP_PLACEHOLDER, rendered)
        self.assertIn("Meridian Cloud Revenue Leadership Command Center", rendered)
        self.assertIn("Northstar Health", rendered)
        self.assertIn("Atlas Manufacturing", rendered)
        self.assertIn("Harbor Technologies", rendered)
        self.assertIn("Riley Morgan", rendered)
        self.assertIn("Maya Chen", rendered)
        self.assertIn(leadership["disclosure"]["message"], rendered)
        self.assertNotIn("{{fiscal_year}}", rendered)
        self.assertNotIn("{{today}}", rendered)
        self.assertNotIn('data-action="draft"', rendered)
        self.assertNotIn('data-action="publish"', rendered)

    def test_leadership_renderer_escapes_script_tag_data(self) -> None:
        leadership = RENDERER.load_leadership_data(portfolio=self.portfolio)
        leadership["signals"][0]["title"] = "</script><script>alert('unsafe')</script>"

        with tempfile.TemporaryDirectory() as temporary_directory:
            output_path = Path(temporary_directory) / "leadership.html"
            rendered = RENDERER.render_leadership_dashboard(
                leadership, output_path=output_path
            ).read_text(encoding="utf-8")

        self.assertNotIn("</script><script>alert('unsafe')</script>", rendered)
        self.assertIn("\\u003c/script>\\u003cscript>alert('unsafe')\\u003c/script>", rendered)

    def test_leadership_loader_rejects_an_account_from_a_different_scenario(self) -> None:
        leadership = RENDERER.load_leadership_data(portfolio=self.portfolio)
        leadership["topDeals"][0]["account"] = "Unrelated Customer Incorporated"

        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_path = Path(temporary_directory) / "leadership.json"
            fixture_path.write_text(json.dumps(leadership), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "unknown seller-portfolio account"):
                RENDERER.load_leadership_data(fixture_path, self.portfolio)

    def test_local_server_serves_both_account_and_leadership_dashboards(self) -> None:
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
                server_thread = threading.Thread(target=server.serve_forever, daemon=True)
                server_thread.start()

                try:
                    for route, expected_text in (
                        ("/", "Riley’s Account Home"),
                        ("/leadership/", "Meridian Cloud Revenue Leadership Command Center"),
                    ):
                        with self.subTest(route=route):
                            with socket.create_connection(
                                server.server_address, timeout=3
                            ) as connection:
                                connection.sendall(
                                    (
                                        f"GET {route} HTTP/1.1\r\n"
                                        "Host: 127.0.0.1\r\nConnection: close\r\n\r\n"
                                    ).encode("utf-8")
                                )
                                chunks: list[bytes] = []
                                while chunk := connection.recv(65536):
                                    chunks.append(chunk)

                            response = b"".join(chunks).decode("utf-8")
                            self.assertIn("200 OK", response)
                            self.assertIn(expected_text, response)
                finally:
                    server.shutdown()
                    server_thread.join(timeout=3)

    def test_meeting_fixture_and_crm_rules_preserve_reviewed_salesforce_write_boundary(
        self,
    ) -> None:
        transcript = (SKILL_DIRECTORY / "references" / "northstar-followup-meeting.md").read_text(
            encoding="utf-8"
        )
        policy = (SKILL_DIRECTORY / "references" / "crm-update-rules.md").read_text(
            encoding="utf-8"
        )
        crm_fixture = (SKILL_DIRECTORY / "references" / "sources" / "salesforce.md").read_text(
            encoding="utf-8"
        )

        for text in (transcript, policy):
            with self.subTest(source="transcript" if text == transcript else "policy"):
                self.assertIn("fictional", text.lower())
                self.assertIn("Northstar Health", text)
                self.assertIn("$420,000", text)
                self.assertIn("Security review", text)
                self.assertIn("Casey Patel", text)
                self.assertIn("Priya Shah", text)
                self.assertIn("Jordan Lee", text)
                self.assertIn("Riley Morgan", text)
                self.assertIn("{{next_thursday}}", text)

        self.assertIn("## Condensed Transcript", transcript)
        self.assertIn("Primary meeting goal", transcript)
        self.assertIn("## Proposed Review-Only Salesforce Changes", transcript)
        self.assertIn("## Opportunity-Update Policy", policy)
        self.assertIn("## Review Before Any Write", policy)
        self.assertIn("explicitly approves the exact proposal", policy)
        self.assertIn("never move a deal to commit", policy.lower())
        self.assertIn("DEMO-NORTHSTAR-OPPORTUNITY", policy)
        self.assertIn("Best Case", crm_fixture)
        self.assertNotIn("| Forecast category | Pipeline", crm_fixture)

        for field in (
            "Next Step",
            "Deal Notes",
            "Decision Criteria & Purchase Process",
            "Risks and Asks",
        ):
            with self.subTest(field=field):
                self.assertIn(f"| {field} |", transcript)

        for protection in ("stage", "amount", "close date", "forecast", "owner"):
            with self.subTest(protection=protection):
                self.assertIn(protection, policy.lower())


if __name__ == "__main__":
    unittest.main()
