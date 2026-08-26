#!/usr/bin/env python3

"""Render the fictional Sales seller and leadership dashboards from shared evidence."""

from __future__ import annotations

import argparse
import json
import tempfile
from copy import deepcopy
from datetime import date, datetime, timedelta, timezone
from functools import partial
from html import escape
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import quote
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

SKILL_DIRECTORY = Path(__file__).resolve().parent.parent
DEFAULT_PORTFOLIO = SKILL_DIRECTORY / "references" / "demo-portfolio.json"
DEFAULT_TEMPLATE = SKILL_DIRECTORY / "assets" / "account-priority-workspace.template.html"
DEFAULT_LEADERSHIP = SKILL_DIRECTORY / "references" / "demo-leadership.json"
DEFAULT_LEADERSHIP_TEMPLATE = (
    SKILL_DIRECTORY / "assets" / "sales-leadership-dashboard.template.html"
)
PLACEHOLDER = "__PRIORITIZE_ACCOUNTS_DATA_JSON__"
LEADERSHIP_PLACEHOLDER = "__LEADERSHIP_DATA_JSON__"
try:
    DEFAULT_OUTPUT_DIRECTORY = Path(tempfile.gettempdir()) / "sales-seller-account-home-demo"
except FileNotFoundError:
    DEFAULT_OUTPUT_DIRECTORY = Path("/tmp") / "sales-seller-account-home-demo"
EXPECTED_COUNTS = {"workNow": 5, "watch": 3, "paused": 2}
REQUIRED_ROOT_FIELDS = {
    "title",
    "generatedAt",
    "source",
    "scope",
    "seller",
    "workNow",
    "watch",
    "paused",
    "evidenceGaps",
}
REQUIRED_ACCOUNT_FIELDS = {
    "rank",
    "account",
    "motion",
    "stage",
    "value",
    "whyItMatters",
    "nextAction",
    "owner",
    "dueDate",
    "confidence",
    "status",
}


class DashboardRequestHandler(SimpleHTTPRequestHandler):
    """Serve the generated dashboard without noisy missing-favicon requests."""

    def do_GET(self) -> None:
        if self.path.split("?", maxsplit=1)[0] == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return
        super().do_GET()

    def log_message(self, format: str, *args: Any) -> None:
        return


def load_portfolio(portfolio_path: Path = DEFAULT_PORTFOLIO) -> dict[str, Any]:
    """Load and validate the bundled fictional account portfolio."""

    loaded = json.loads(portfolio_path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("The demo portfolio must contain a JSON object.")

    missing_root_fields = sorted(REQUIRED_ROOT_FIELDS - loaded.keys())
    if missing_root_fields:
        raise ValueError(f"The demo portfolio is missing root fields: {missing_root_fields}")

    title = loaded.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("The dashboard needs a personalized seller-facing title.")

    demo_metadata = loaded.get("demo")
    if not isinstance(demo_metadata, dict) or demo_metadata.get("mode") != "fictional":
        raise ValueError("The account portfolio must explicitly declare fictional demo mode.")
    disclaimer = demo_metadata.get("disclaimer")
    if not isinstance(disclaimer, str) or "fictional" not in disclaimer.lower():
        raise ValueError("The account portfolio needs a visible fictional-data disclosure.")

    seller = loaded.get("seller")
    if not isinstance(seller, dict):
        raise ValueError("The account portfolio must identify the seller who owns the workspace.")
    seller_name = seller.get("name")
    seller_first_name = seller.get("firstName")
    if not isinstance(seller_name, str) or not seller_name.strip():
        raise ValueError("The seller needs a non-empty full name.")
    if not isinstance(seller_first_name, str) or not seller_first_name.strip():
        raise ValueError("The seller needs a non-empty first name.")
    normalized_title = title.replace("’", "'")
    if not normalized_title.startswith(
        (f"{seller_first_name}'s Account Home", f"{seller_first_name}'s Account Overview")
    ):
        raise ValueError("The seller account-home dashboard title must be personalized.")

    source = loaded.get("source")
    if not isinstance(source, dict) or "fictional" not in str(source.get("label", "")).lower():
        raise ValueError("The dashboard source must explicitly disclose fictional sample data.")

    account_names: set[str] = set()
    account_ranks: set[int] = set()

    for group, expected_count in EXPECTED_COUNTS.items():
        rows = loaded.get(group)
        if not isinstance(rows, list) or len(rows) != expected_count:
            raise ValueError(f"The {group} group must contain exactly {expected_count} accounts.")

        for row in rows:
            if not isinstance(row, dict):
                raise ValueError(f"Every {group} account must be a JSON object.")

            missing_account_fields = sorted(REQUIRED_ACCOUNT_FIELDS - row.keys())
            if missing_account_fields:
                raise ValueError(
                    f"Account {row.get('account', '<unknown>')} is missing fields: "
                    f"{missing_account_fields}"
                )

            account = row["account"]
            rank = row["rank"]
            if not isinstance(account, str) or not account.strip():
                raise ValueError("Every demo account needs a non-empty account name.")
            if account in account_names:
                raise ValueError(f"Duplicate demo account: {account}")
            if not isinstance(rank, int) or isinstance(rank, bool) or rank < 1:
                raise ValueError(f"Invalid account rank for {account}: {rank}")
            if rank in account_ranks:
                raise ValueError(f"Duplicate demo account rank: {rank}")
            if row["confidence"] not in {"High", "Medium", "Low"}:
                raise ValueError(f"Invalid confidence for {account}: {row['confidence']}")
            if row["owner"] != seller_name:
                raise ValueError(
                    f"Account {account} must be owned by the same seller: {seller_name}"
                )

            account_names.add(account)
            account_ranks.add(rank)

    return loaded


def _account_priority(group: str, rank: int) -> str:
    """Preserve the seller's existing account order in the leadership overview."""

    if group == "workNow":
        return "High" if rank <= 3 else "Action"
    if group == "watch":
        return "Watch"
    return "Paused"


def _account_id(name: str) -> str:
    """Keep distinct fictional account names distinct without lossy slug normalization."""

    return "account-" + name.encode("utf-8").hex()


def _account_focus_records(
    leadership: dict[str, Any], portfolio: dict[str, Any]
) -> list[dict[str, Any]]:
    """Join detailed seller evidence with explicitly manager-reported division accounts."""

    accounts_by_name = {
        account["account"]: (group, account)
        for group in EXPECTED_COUNTS
        for account in portfolio[group]
    }
    overview: list[dict[str, Any]] = []

    for deal in leadership["topDeals"]:
        group, account = accounts_by_name[deal["account"]]
        rank = account["rank"]
        priority = _account_priority(group, rank)
        risk = deal.get("risk") or account["whyItMatters"]
        decision_window = deal.get("closeWindow") or account["dueDate"]
        monitor = [risk, f"Decision checkpoint: {decision_window}."]
        unblock = [
            deal.get("leadershipDecision") or account["nextAction"],
            deal.get("nextCustomerStep") or account["nextAction"],
        ]

        deal.setdefault("priorityRank", rank)
        deal.setdefault("priority", priority)
        deal.setdefault("monitor", monitor)
        deal.setdefault("helpUnblock", unblock)

        evidence = deal.get("evidence")
        source_evidence = evidence if isinstance(evidence, list) else []
        if not source_evidence:
            source_evidence = [
                {
                    "source": source,
                    "reference": f"{account['account']} · {deal['stage']} account context",
                    "detail": account["whyItMatters"],
                }
                for source in deal.get("sources", [])
                if isinstance(source, str)
            ]
        references = list(
            dict.fromkeys(
                event["source"]
                for event in source_evidence
                if isinstance(event, dict) and isinstance(event.get("source"), str)
            )
        )

        rationale = account.get("rationale") or deal.get("rationale")
        if not isinstance(rationale, list) or not rationale:
            rationale = [account["whyItMatters"], account["nextAction"]]

        overview.append(
            {
                "id": _account_id(account["account"]),
                "name": account["account"],
                "value": deal["value"],
                "valueLabel": account["value"],
                "seller": deal["owner"],
                "priority": priority,
                "priorityRank": rank,
                "sellerPriorityRank": rank,
                "stage": deal["stage"],
                "type": deal.get("motion", account["motion"]),
                "decisionDate": decision_window,
                "headline": account["status"],
                "briefing": account["whyItMatters"],
                "rationale": deepcopy(rationale),
                "monitor": deepcopy(deal["monitor"]),
                "unblock": deepcopy(deal["helpUnblock"]),
                "evidence": references,
                "sourceEvidence": deepcopy(source_evidence),
                "evidenceScope": "seller-account",
                "nextStep": account["nextAction"],
                "_priorityOrder": rank,
            }
        )

    verified_sellers = {
        seller["name"]
        for seller in leadership.get("sellerOverview", [])
        if isinstance(seller, dict) and isinstance(seller.get("name"), str)
    }
    for account in leadership.get("divisionAccounts", []):
        if account["owner"] not in verified_sellers:
            continue
        evidence = account["sourceEvidence"]
        overview.append(
            {
                "id": _account_id(account["account"]),
                "name": account["account"],
                "value": account["value"],
                "valueLabel": f"${account['value']:,.0f}",
                "seller": account["owner"],
                "manager": account["manager"],
                "region": account["region"],
                "priority": account["priority"],
                "priorityRank": 0,
                "sellerPriorityRank": None,
                "stage": account["stage"],
                "type": account["motion"],
                "decisionDate": account["closeWindow"],
                "headline": account["headline"],
                "briefing": account["briefing"],
                "rationale": deepcopy(account["rationale"]),
                "monitor": deepcopy(account["monitor"]),
                "unblock": deepcopy(account["unblock"]),
                "evidence": list(dict.fromkeys(item["source"] for item in evidence)),
                "sourceEvidence": deepcopy(evidence),
                "evidenceScope": account["evidenceScope"],
                "nextStep": account["nextStep"],
                "_priorityOrder": account["priorityOrder"],
            }
        )

    priority_order = {"High": 0, "Action": 1, "Watch": 2, "Paused": 3}
    overview.sort(
        key=lambda account: (
            priority_order.get(account["priority"], len(priority_order)),
            account["_priorityOrder"],
        )
    )
    for rank, account in enumerate(overview, start=1):
        account["priorityRank"] = rank
        account.pop("_priorityOrder")
    return overview


def _team_focus_records(leadership: dict[str, Any]) -> list[dict[str, Any]]:
    """Expose measured regional growth without inventing individual seller growth."""

    raw_summaries = leadership.get("geographySummaries")
    summaries = raw_summaries if isinstance(raw_summaries, dict) else {}
    roster = leadership.get("sellerOverview") or []
    teams: list[dict[str, Any]] = []

    for team in leadership["divisionTeams"]:
        raw_summary = summaries.get(team["region"])
        summary = raw_summary if isinstance(raw_summary, dict) else {}
        raw_movement = summary.get("weeklyMovement")
        weekly_movement = (
            raw_movement
            if isinstance(raw_movement, (int, float)) and not isinstance(raw_movement, bool)
            else None
        )
        previous_forecast = (
            team["forecast"] - weekly_movement if weekly_movement is not None else None
        )
        growth_rate = (
            round(weekly_movement / previous_forecast * 100, 1)
            if weekly_movement is not None
            and previous_forecast is not None
            and previous_forecast > 0
            else None
        )
        sellers: list[dict[str, Any]] = []

        for seller in roster:
            if seller["manager"] != team["manager"]:
                continue
            going_well = seller.get("goingWell") or [
                (
                    f"${seller['forecast'] / 1_000_000:.2f}M seller-reported forecast across "
                    f"{seller['opportunities']} opportunities."
                )
            ]
            needs_attention = seller.get("needsAttention") or [
                seller.get("focus") or "Confirm customer decision timing and accountable ownership."
            ]
            sellers.append(
                {
                    "name": seller["name"],
                    "role": seller.get("role") or "Account executive",
                    "region": seller["region"],
                    "manager": seller["manager"],
                    "forecast": seller["forecast"],
                    "target": seller["target"],
                    "attainment": round(seller["forecast"] / seller["target"] * 100, 1),
                    "growthRate": None,
                    "growthBasis": "Individual seller growth is not reported.",
                    "goingWell": deepcopy(going_well),
                    "needsAttention": deepcopy(needs_attention),
                    "accounts": seller["accounts"],
                    "opportunities": seller["opportunities"],
                    "featured": bool(seller.get("featured")),
                }
            )

        accounts = summary.get("accounts")
        if not isinstance(accounts, int) or isinstance(accounts, bool) or accounts < 0:
            accounts = sum(seller["accounts"] for seller in sellers)
        opportunities = summary.get("opportunities")
        if (
            not isinstance(opportunities, int)
            or isinstance(opportunities, bool)
            or opportunities < 0
        ):
            opportunities = sum(seller["opportunities"] for seller in sellers)

        wins: list[str] = []
        coverage = team.get("coverage")
        if isinstance(coverage, (int, float)) and not isinstance(coverage, bool):
            wins.append(f"{coverage:.1f}× pipeline coverage across {accounts} regional accounts.")
        win_rate = summary.get("winRate")
        created_pipeline = summary.get("pipelineCreated")
        if (
            isinstance(win_rate, (int, float))
            and not isinstance(win_rate, bool)
            and isinstance(created_pipeline, (int, float))
            and not isinstance(created_pipeline, bool)
        ):
            wins.append(
                f"{win_rate:.1f}% regional win rate with "
                f"${created_pipeline / 1_000_000:.2f}M in created pipeline."
            )
        if not wins:
            wins.append(
                f"${team['forecast'] / 1_000_000:.2f}M manager-reported forecast against "
                f"a ${team['target'] / 1_000_000:.2f}M team target."
            )
        attention = [
            concern
            for concern in (team.get("trend"), summary.get("riskSummary"))
            if isinstance(concern, str) and concern.strip()
        ]
        if not attention:
            attention.append("Review manager-reported risks and accountable customer next steps.")

        teams.append(
            {
                "name": team["manager"],
                "role": "Regional Sales Manager",
                "team": team["name"],
                "region": team["region"],
                "forecast": team["forecast"],
                "target": team["target"],
                "attainment": round(team["forecast"] / team["target"] * 100, 1),
                "growthRate": growth_rate,
                "weeklyMovement": weekly_movement,
                "growthBasis": (
                    "Regional forecast week-over-week"
                    if growth_rate is not None
                    else "Regional week-over-week growth is not reported."
                ),
                "wins": wins,
                "attention": attention,
                "accounts": accounts,
                "opportunities": opportunities,
                "sellers": sellers,
            }
        )

    return teams


def load_leadership_data(
    leadership_path: Path = DEFAULT_LEADERSHIP,
    portfolio: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate the fictional leadership view against its shared seller-account evidence."""

    loaded = json.loads(leadership_path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("The leadership dashboard must contain a JSON object.")

    title = loaded.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("The leadership dashboard needs a non-empty title.")

    company = loaded.get("company")
    company_name = company.get("name") if isinstance(company, dict) else company
    if not isinstance(company_name, str) or not company_name.strip():
        raise ValueError("The leadership dashboard needs a named company.")
    if not isinstance(company, dict):
        raise ValueError(
            "The leadership dashboard must identify its division and leadership persona."
        )
    division = company.get("division")
    if not isinstance(division, str) or not division.strip():
        raise ValueError("The leadership dashboard must identify its division.")
    division_lead = company.get("divisionLead")
    if not isinstance(division_lead, dict):
        raise ValueError("The leadership dashboard must identify its division leader.")
    for field in ("name", "title"):
        value = division_lead.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"The division leader needs a non-empty {field}.")
    if company.get("salesLeader") != division_lead["name"]:
        raise ValueError("The sales leadership persona must match the named division leader.")

    disclosure = loaded.get("disclosure")
    if isinstance(disclosure, dict):
        disclosure = disclosure.get("message") or disclosure.get("text")
    if not isinstance(disclosure, str) or "fictional" not in disclosure.lower():
        raise ValueError("The leadership dashboard needs a visible fictional-data disclosure.")

    for field in ("metrics", "topDeals", "signals", "decisions"):
        entries = loaded.get(field)
        if not isinstance(entries, list) or not entries:
            raise ValueError(f"The leadership dashboard needs non-empty {field} data.")

    source_coverage = loaded.get("sourceCoverage")
    if not isinstance(source_coverage, list) or not source_coverage:
        raise ValueError("The leadership dashboard needs source-grounded connector coverage.")

    forecast = loaded.get("forecast")
    if not isinstance(forecast, dict):
        raise ValueError("The leadership dashboard needs a clearly scoped forecast.")
    for field in ("target", "base"):
        amount = forecast.get(field)
        if not isinstance(amount, (int, float)) or isinstance(amount, bool) or amount <= 0:
            raise ValueError(f"The leadership forecast needs a positive {field} amount.")

    division_teams = loaded.get("divisionTeams")
    if not isinstance(division_teams, list) or len(division_teams) < 2:
        raise ValueError("The division dashboard needs multiple regional manager teams.")
    manager_names: set[str] = set()
    for team in division_teams:
        if not isinstance(team, dict) or not str(team.get("manager", "")).strip():
            raise ValueError("Every division team needs a named regional manager.")
        manager_name = team["manager"]
        if manager_name in manager_names:
            raise ValueError(f"Duplicate regional division manager: {manager_name}")
        manager_names.add(manager_name)
    if sum(team.get("forecast", 0) for team in division_teams) != forecast["base"]:
        raise ValueError("Regional team forecasts must reconcile with the division forecast.")
    if sum(team.get("target", 0) for team in division_teams) != forecast["target"]:
        raise ValueError("Regional team targets must reconcile with the division revenue target.")

    source_portfolio = portfolio or load_portfolio()
    portfolio_company = source_portfolio.get("demo", {}).get("company")
    if company_name != portfolio_company:
        raise ValueError(
            "The leadership dashboard and seller account priorities must use the same company."
        )

    seller_overview = loaded.get("sellerOverview")
    if seller_overview is not None:
        if not isinstance(seller_overview, list) or not seller_overview:
            raise ValueError("The seller overview must contain at least one verified seller.")

        seller_names: set[str] = set()
        sellers_by_manager: dict[str, list[dict[str, Any]]] = {
            manager_name: [] for manager_name in manager_names
        }
        for seller in seller_overview:
            if not isinstance(seller, dict):
                raise ValueError("Every seller overview entry must be a JSON object.")
            seller_name = seller.get("name")
            if not isinstance(seller_name, str) or not seller_name.strip():
                raise ValueError("Every seller overview entry needs a non-empty seller name.")
            if seller_name in seller_names:
                raise ValueError(f"Duplicate seller in leadership overview: {seller_name}")
            seller_names.add(seller_name)

            manager_name = seller.get("manager")
            if manager_name not in manager_names:
                raise ValueError(
                    f"Seller {seller_name} must belong to a verified division manager."
                )
            manager_team = next(team for team in division_teams if team["manager"] == manager_name)
            if seller.get("region") != manager_team.get("region"):
                raise ValueError(
                    f"Seller {seller_name} must belong to {manager_name}'s verified region."
                )

            for field in ("forecast", "target"):
                amount = seller.get(field)
                if not isinstance(amount, (int, float)) or isinstance(amount, bool) or amount <= 0:
                    raise ValueError(f"Seller {seller_name} needs a positive {field} amount.")
            for field in ("accounts", "opportunities"):
                count = seller.get(field)
                if not isinstance(count, int) or isinstance(count, bool) or count < 0:
                    raise ValueError(f"Seller {seller_name} needs a valid {field} count.")
            for field in ("goingWell", "needsAttention"):
                highlights = seller.get(field)
                if highlights is not None:
                    if (
                        not isinstance(highlights, list)
                        or not highlights
                        or any(
                            not isinstance(highlight, str) or not highlight.strip()
                            for highlight in highlights
                        )
                    ):
                        raise ValueError(
                            f"Seller {seller_name} needs source-grounded {field} highlights."
                        )
            sellers_by_manager[manager_name].append(seller)

        geography_summaries = loaded.get("geographySummaries")
        if not isinstance(geography_summaries, dict):
            raise ValueError("Seller overview reconciliation needs regional reporting summaries.")
        for team in division_teams:
            manager_sellers = sellers_by_manager[team["manager"]]
            if not manager_sellers:
                raise ValueError(f"Regional manager {team['manager']} has no seller coverage.")
            for field in ("forecast", "target"):
                if sum(seller[field] for seller in manager_sellers) != team[field]:
                    raise ValueError(
                        f"Seller {field} amounts must reconcile with {team['manager']}'s team."
                    )
            regional_summary = geography_summaries.get(team.get("region"))
            if not isinstance(regional_summary, dict):
                raise ValueError(f"Missing regional reporting summary for {team.get('region')}.")
            for field in ("accounts", "opportunities"):
                if sum(seller[field] for seller in manager_sellers) != regional_summary.get(field):
                    raise ValueError(
                        f"Seller {field} counts must reconcile with {team['manager']}'s region."
                    )

        featured_sellers = [seller for seller in seller_overview if seller.get("featured")]
        if len(featured_sellers) != 1:
            raise ValueError("The seller overview needs exactly one featured account executive.")
        portfolio_seller = source_portfolio.get("seller", {}).get("name")
        if featured_sellers[0]["name"] != portfolio_seller:
            raise ValueError(
                "The featured leadership seller must match the shared seller portfolio."
            )
        featured_manager = featured_sellers[0]["manager"]
        featured_team = next(team for team in division_teams if team["manager"] == featured_manager)
        if featured_team.get("featuredSeller") != portfolio_seller:
            raise ValueError(
                "The featured seller must match their regional manager's seller drill-down."
            )

    portfolio_accounts = {
        account["account"]: account
        for group in EXPECTED_COUNTS
        for account in source_portfolio[group]
    }
    seen_accounts: set[str] = set()
    for deal in loaded["topDeals"]:
        if not isinstance(deal, dict):
            raise ValueError("Every leadership top deal must be a JSON object.")
        account = deal.get("account")
        if not isinstance(account, str) or account not in portfolio_accounts:
            raise ValueError(f"Leadership deal uses an unknown seller-portfolio account: {account}")
        if account in seen_accounts:
            raise ValueError(f"Duplicate leadership account: {account}")
        seen_accounts.add(account)

        source_account = portfolio_accounts[account]
        expected_value = float(str(source_account["value"]).replace("$", "").replace(",", ""))
        deal_value = deal.get("value")
        if (
            not isinstance(deal_value, (int, float))
            or isinstance(deal_value, bool)
            or deal_value != expected_value
        ):
            raise ValueError(
                f"Leadership deal value for {account} must match its seller-portfolio opportunity."
            )
        if deal.get("owner") != source_account["owner"]:
            raise ValueError(
                f"Leadership deal owner for {account} must match its seller-portfolio opportunity."
            )
        if deal.get("stage") != source_account["stage"]:
            raise ValueError(
                f"Leadership deal stage for {account} must match its seller-portfolio opportunity."
            )
        if deal.get("manager") not in manager_names:
            raise ValueError(f"Leadership deal manager for {account} must belong to the division.")

        account_detail = source_portfolio.get("accountDetails", {}).get(account)
        if isinstance(account_detail, dict):
            for field, source_field in (
                ("evidence", "events"),
                ("rationale", "rationale"),
                ("stakeholders", "stakeholders"),
                ("strategy", "strategy"),
            ):
                if source_field in account_detail:
                    deal.setdefault(field, deepcopy(account_detail[source_field]))

    missing_accounts = sorted(portfolio_accounts.keys() - seen_accounts)
    if missing_accounts:
        raise ValueError(f"Leadership top deals omit seller-portfolio accounts: {missing_accounts}")

    division_accounts = loaded.get("divisionAccounts", [])
    if not isinstance(division_accounts, list):
        raise ValueError("Additional division accounts must be provided as a JSON array.")

    if division_accounts and seller_overview is not None:
        division_reporting = loaded.get("divisionAccountReporting")
        if not isinstance(division_reporting, dict) or not all(
            isinstance(division_reporting.get(field), str) and division_reporting[field].strip()
            for field in ("basis", "forecastTreatment")
        ):
            raise ValueError(
                "Additional division accounts must disclose their evidence and forecast treatment."
            )

        roster = {seller["name"]: seller for seller in seller_overview}
        connector_names = {
            source.get("name")
            for source in source_coverage
            if isinstance(source, dict) and isinstance(source.get("name"), str)
        }
        seen_division_accounts: set[str] = set()
        priority_orders: set[int] = set()
        for account in division_accounts:
            if not isinstance(account, dict):
                raise ValueError("Every additional division account must be a JSON object.")
            account_name = account.get("account")
            if not isinstance(account_name, str) or not account_name.strip():
                raise ValueError("Every additional division account needs a non-empty name.")
            if account_name in portfolio_accounts or account_name in seen_division_accounts:
                raise ValueError(f"Duplicate or reassigned division account: {account_name}")
            seen_division_accounts.add(account_name)

            owner = roster.get(account.get("owner"))
            if owner is None:
                raise ValueError(
                    f"Division account {account_name} needs a seller from the verified team roster."
                )
            if account.get("manager") != owner["manager"]:
                raise ValueError(
                    f"Division account {account_name} must use its seller's actual manager."
                )
            if account.get("region") != owner["region"]:
                raise ValueError(
                    f"Division account {account_name} must use its seller's actual region."
                )
            value = account.get("value")
            if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
                raise ValueError(f"Division account {account_name} needs a positive value.")
            if value > owner["forecast"]:
                raise ValueError(
                    f"Division account {account_name} cannot exceed its seller's existing forecast."
                )
            if account.get("priority") not in {"High", "Action", "Watch", "Paused"}:
                raise ValueError(f"Division account {account_name} needs a supported priority.")
            order = account.get("priorityOrder")
            if not isinstance(order, int) or isinstance(order, bool) or order < 1:
                raise ValueError(f"Division account {account_name} needs a valid priority order.")
            if order in priority_orders:
                raise ValueError(f"Duplicate additional division-account priority order: {order}")
            priority_orders.add(order)

            for field in ("stage", "motion", "closeWindow", "headline", "briefing", "nextStep"):
                field_value = account.get(field)
                if not isinstance(field_value, str) or not field_value.strip():
                    raise ValueError(f"Division account {account_name} needs a non-empty {field}.")
            for field in ("rationale", "monitor", "unblock", "sources", "sourceEvidence"):
                entries = account.get(field)
                if not isinstance(entries, list) or not entries:
                    raise ValueError(
                        f"Division account {account_name} needs source-grounded {field}."
                    )
            if account.get("evidenceScope") != "manager-reported":
                raise ValueError(
                    f"Division account {account_name} must identify its manager-reported scope."
                )
            for evidence in account["sourceEvidence"]:
                if not isinstance(evidence, dict):
                    raise ValueError(
                        f"Division account {account_name} needs attributed evidence records."
                    )
                if evidence.get("source") not in connector_names:
                    raise ValueError(
                        f"Division account {account_name} cannot use an unlisted evidence source."
                    )
                if not all(
                    isinstance(evidence.get(field), str) and evidence[field].strip()
                    for field in ("reference", "detail")
                ):
                    raise ValueError(
                        f"Division account {account_name} needs explicit source evidence details."
                    )

    reporting = loaded.get("reporting")
    if not isinstance(reporting, dict) or not str(reporting.get("scope", "")).strip():
        raise ValueError("The leadership dashboard must identify the scope of its financial data.")
    portfolio_total = sum(
        float(str(account["value"]).replace("$", "").replace(",", ""))
        for account in portfolio_accounts.values()
    )
    if reporting.get("samplePortfolioValue") != portfolio_total:
        raise ValueError("Leadership sample portfolio value must equal its shared seller accounts.")
    if reporting.get("sampleAccountCount") != len(portfolio_accounts):
        raise ValueError("Leadership detailed-account count must equal its shared seller accounts.")

    loaded["accountOverview"] = _account_focus_records(loaded, source_portfolio)
    loaded["teamFocus"] = _team_focus_records(loaded)

    return loaded


def _display_date(value: date) -> str:
    return f"{value:%a, %b} {value.day}"


def resolve_demo_date(current_date: date | None = None, time_zone: str | None = None) -> date:
    """Use the supplied conversation date or timezone before the legacy host-clock default."""

    if current_date is not None:
        return current_date
    if time_zone is not None:
        try:
            return datetime.now(ZoneInfo(time_zone)).date()
        except (ZoneInfoNotFoundError, ValueError) as error:
            raise ValueError(f"Unknown IANA timezone: {time_zone}") from error
    return datetime.now().astimezone().date()


def demo_relative_dates(current_date: date | None = None) -> dict[str, str]:
    """Resolve the relative dates shared by demo content and the seller dashboard."""

    today = resolve_demo_date(current_date)
    previous_business_days: list[date] = []
    candidate = today
    while len(previous_business_days) < 2:
        candidate -= timedelta(days=1)
        if candidate.weekday() < 5:
            previous_business_days.append(candidate)

    days_until_thursday = (3 - today.weekday()) % 7 or 7
    next_thursday = today + timedelta(days=days_until_thursday)

    return {
        "today": _display_date(today),
        "previous_business_day": _display_date(previous_business_days[0]),
        "two_business_days_ago": _display_date(previous_business_days[1]),
        "next_thursday": _display_date(next_thursday),
        "fiscal_year": str(today.year)[-2:],
    }


def _resolve_relative_dates(value: Any, relative_dates: dict[str, str]) -> Any:
    if isinstance(value, str):
        for token, replacement in relative_dates.items():
            value = value.replace("{{" + token + "}}", replacement)
        return value
    if isinstance(value, list):
        return [_resolve_relative_dates(item, relative_dates) for item in value]
    if isinstance(value, dict):
        return {key: _resolve_relative_dates(item, relative_dates) for key, item in value.items()}
    return value


def render_dashboard(
    portfolio: dict[str, Any],
    template_path: Path = DEFAULT_TEMPLATE,
    output_path: Path | None = None,
    *,
    current_date: date | None = None,
) -> Path:
    """Embed personalized fictional account context in the interactive seller workspace."""

    template = template_path.read_text(encoding="utf-8")
    if template.count(PLACEHOLDER) != 1:
        raise ValueError("The account-priority template must contain exactly one data placeholder.")

    destination = output_path or (DEFAULT_OUTPUT_DIRECTORY / "index.html")
    destination = destination.expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)

    hydrated_portfolio = _resolve_relative_dates(
        deepcopy(portfolio), demo_relative_dates(current_date)
    )
    hydrated_portfolio["generatedAt"] = datetime.now(timezone.utc).isoformat()
    serialized = json.dumps(hydrated_portfolio, ensure_ascii=False, separators=(",", ":"))
    safe_serialized = serialized.replace("<", "\\u003c")
    rendered = template.replace(PLACEHOLDER, safe_serialized, 1)
    rendered = rendered.replace(
        "<title>Seller Account Home</title>",
        f"<title>{escape(hydrated_portfolio['title'])}</title>",
        1,
    )
    if PLACEHOLDER in rendered:
        raise ValueError("The rendered dashboard still contains an unresolved data placeholder.")

    destination.write_text(rendered, encoding="utf-8")
    return destination


def render_leadership_dashboard(
    leadership_data: dict[str, Any],
    template_path: Path = DEFAULT_LEADERSHIP_TEMPLATE,
    output_path: Path | None = None,
    *,
    current_date: date | None = None,
) -> Path:
    """Render a self-contained, read-only sales-leadership command center."""

    template = template_path.read_text(encoding="utf-8")
    if template.count(LEADERSHIP_PLACEHOLDER) != 1:
        raise ValueError("The leadership template must contain exactly one data placeholder.")

    destination = output_path or (DEFAULT_OUTPUT_DIRECTORY / "leadership" / "index.html")
    destination = destination.expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)

    hydrated_data = _resolve_relative_dates(
        deepcopy(leadership_data), demo_relative_dates(current_date)
    )
    hydrated_data["generatedAt"] = datetime.now(timezone.utc).isoformat()
    serialized = json.dumps(hydrated_data, ensure_ascii=False, separators=(",", ":"))
    safe_serialized = serialized.replace("<", "\\u003c")
    rendered = template.replace(LEADERSHIP_PLACEHOLDER, safe_serialized, 1)
    if LEADERSHIP_PLACEHOLDER in rendered:
        raise ValueError("The leadership dashboard still contains an unresolved data placeholder.")

    destination.write_text(rendered, encoding="utf-8")
    return destination


def create_dashboard_server(
    dashboard_path: Path,
    port: int = 0,
    root_directory: Path | None = None,
) -> ThreadingHTTPServer:
    """Expose only the generated demo directory on the loopback interface."""

    site_root = root_directory or dashboard_path.parent
    request_handler = partial(DashboardRequestHandler, directory=str(site_root))
    return ThreadingHTTPServer(("127.0.0.1", port), request_handler)


def dashboard_route(dashboard_path: Path, site_root: Path) -> str:
    """Return the actual served artifact path, including escaped custom filenames."""

    route = dashboard_path.relative_to(site_root).as_posix()
    if dashboard_path.name == "index.html":
        route = route[: -len("index.html")]
    return "/" + quote(route, safe="/")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render connector-free fictional Sales seller and leadership dashboards."
    )
    parser.add_argument("--portfolio", type=Path, default=DEFAULT_PORTFOLIO)
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--current-date", type=date.fromisoformat, help="User-local date (YYYY-MM-DD)."
    )
    parser.add_argument("--timezone", help="User's IANA timezone when no date was supplied.")
    parser.add_argument(
        "--dashboard",
        choices=("account", "leadership", "both"),
        default="both",
        help="Dashboard to render; the default keeps account and leadership views together.",
    )
    parser.add_argument("--leadership-data", type=Path, default=DEFAULT_LEADERSHIP)
    parser.add_argument("--leadership-template", type=Path, default=DEFAULT_LEADERSHIP_TEMPLATE)
    parser.add_argument(
        "--leadership-output",
        type=Path,
        help="Optional output path for the leadership dashboard when rendering both views.",
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Open the dashboard through a loopback-only local server.",
    )
    parser.add_argument(
        "--port", type=int, default=0, help="Local server port; zero chooses a free port."
    )
    arguments = parser.parse_args()
    try:
        current_date = resolve_demo_date(arguments.current_date, arguments.timezone)
    except ValueError as error:
        parser.error(str(error))

    portfolio = load_portfolio(arguments.portfolio)
    account_path: Path | None = None
    leadership_path: Path | None = None

    if arguments.dashboard in {"account", "both"}:
        account_path = render_dashboard(
            portfolio, arguments.template, arguments.output, current_date=current_date
        )
        print(account_path, flush=True)
        print(
            "Fictional sample portfolio: "
            f"{len(portfolio['workNow'])} Work now, "
            f"{len(portfolio['watch'])} Watch, "
            f"{len(portfolio['paused'])} Paused.",
            flush=True,
        )

    if arguments.dashboard in {"leadership", "both"}:
        leadership_data = load_leadership_data(arguments.leadership_data, portfolio)
        leadership_output = arguments.leadership_output
        if arguments.dashboard == "leadership" and arguments.output:
            leadership_output = arguments.output
        elif account_path is not None and leadership_output is None:
            leadership_output = account_path.parent / "leadership" / "index.html"
        leadership_path = render_leadership_dashboard(
            leadership_data,
            arguments.leadership_template,
            leadership_output,
            current_date=current_date,
        )
        print(leadership_path, flush=True)

    print("No connected tools or live customer systems were accessed.", flush=True)

    if arguments.serve:
        primary_path = account_path or leadership_path
        if primary_path is None:
            raise ValueError("At least one dashboard must be rendered before starting the server.")

        if account_path is not None:
            site_root = account_path.parent
        elif leadership_path is not None and leadership_path.parent.name == "leadership":
            site_root = leadership_path.parent.parent
        else:
            site_root = primary_path.parent

        with create_dashboard_server(primary_path, arguments.port, site_root) as server:
            base_url = f"http://127.0.0.1:{server.server_address[1]}"
            if account_path is not None:
                print(f"{base_url}{dashboard_route(account_path, site_root)}", flush=True)
            if leadership_path is not None:
                print(f"{base_url}{dashboard_route(leadership_path, site_root)}", flush=True)
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass


if __name__ == "__main__":
    main()
