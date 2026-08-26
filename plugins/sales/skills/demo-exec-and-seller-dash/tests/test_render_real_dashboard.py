"""Regression coverage for grounded, durable seller and leadership dashboards."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

from sales_test_support import SalesTestCase, load_script, run_command

DEMO_SKILL_DIRECTORY = Path(__file__).resolve().parent.parent
PLUGIN_DIRECTORY = DEMO_SKILL_DIRECTORY.parent.parent
RENDERER_PATH = PLUGIN_DIRECTORY / "scripts" / "render_real_dashboard.py"
RENDERER = load_script(RENDERER_PATH, "sales_real_dashboard_renderer")


class RealDashboardRenderingTests(SalesTestCase):
    def setUp(self) -> None:
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        self.project_root = Path(temporary_directory.name)

    @staticmethod
    def seller_payload(
        *,
        owner: str = "Casey Rivera",
        account_scope: str = "Casey Rivera's complete enterprise account book",
    ) -> dict[str, object]:
        return {
            "title": f"{owner.split()[0]}'s Account Home",
            "generatedAt": "2026-08-06T14:30:00Z",
            "company": {"name": "Summit Analytics"},
            "seller": {"name": owner, "firstName": owner.split()[0], "team": "West Enterprise"},
            "source": {"label": "Verified Salesforce export", "status": "Connected"},
            "scope": {
                "sourceOfTruth": "Verified Salesforce account export",
                "sourcesChecked": ["Salesforce"],
                "accountSet": account_scope,
                "rankingBasis": "Verified customer timing and documented opportunity risk",
                "assumptions": "No unsupported assumptions",
                "motionGoal": "mixed",
            },
            "connectedSources": [{"name": "Salesforce", "verified": True, "status": "Connected"}],
            "accountDetails": {
                "Harbor Health": {
                    "stakeholders": [{"name": "Taylor Brooks", "role": "Customer sponsor"}],
                    "events": [
                        {
                            "source": "Salesforce",
                            "title": "Security review requires a customer owner",
                            "detail": "The account owner documented the next customer decision.",
                        }
                    ],
                }
            },
            "workNow": [
                {
                    "rank": 1,
                    "account": "Harbor Health",
                    "motion": "Expansion",
                    "stage": "Security review",
                    "value": "$250,000",
                    "whyItMatters": "A verified customer security decision is outstanding.",
                    "nextAction": "Confirm the customer security-review owner.",
                    "owner": owner,
                    "dueDate": "2026-08-12",
                    "confidence": "High",
                    "status": "Needs attention",
                }
            ],
            "watch": [
                {
                    "rank": 2,
                    "account": "Cedar Energy",
                    "motion": "Renewal",
                    "stage": "Customer relationship",
                    "value": "Value unavailable",
                    "whyItMatters": "Renewal timing has not yet been confirmed.",
                    "nextAction": "Monitor the documented renewal checkpoint.",
                    "owner": owner,
                    "dueDate": "No date set",
                    "confidence": "Low",
                    "status": "Monitoring",
                }
            ],
            "paused": [],
            "evidenceGaps": ["Cedar Energy renewal date is not available in the source."],
        }

    @staticmethod
    def leadership_payload(
        *,
        company: str = "Summit Analytics",
        division: str = "Enterprise Revenue",
        leader: str = "Priya Desai",
    ) -> dict[str, object]:
        return {
            "title": f"{company} Revenue Leadership Dashboard",
            "company": {
                "name": company,
                "division": division,
                "divisionLead": {"name": leader},
                "leadershipRole": "Vice President of Sales",
            },
            "quarter": {"label": "Q3 2026", "elapsedPercent": 47},
            "reporting": {"snapshot": "2026-08-06", "teamAccountCount": 2},
            "forecast": {
                "target": 2_000_000,
                "base": 1_750_000,
                "components": [
                    {"key": "closedWon", "label": "Closed won", "value": 1_000_000},
                    {"key": "commit", "label": "Validated commit", "value": 500_000},
                    {"key": "bestCase", "label": "Weighted pipeline", "value": 250_000},
                ],
                "scenarios": [
                    {
                        "key": "base",
                        "label": "Expected",
                        "value": 1_750_000,
                        "commitCloseRate": 100,
                        "additionalPipelineWinRate": 40,
                        "dealSizeUplift": 0,
                    }
                ],
            },
            "sourceCoverage": [{"name": "Salesforce", "verified": True, "status": "Connected"}],
            "topDeals": [
                {
                    "account": "Harbor Health",
                    "owner": "Casey Rivera",
                    "value": 250_000,
                    "motion": "Expansion",
                    "stage": "Security review",
                    "risk": "A verified customer security-review owner is still needed.",
                    "nextCustomerStep": "Confirm the customer security-review owner.",
                    "sources": ["Salesforce"],
                }
            ],
            "divisionTeams": [
                {
                    "manager": "Morgan Lee",
                    "region": "West",
                    "forecast": 1_750_000,
                    "target": 2_000_000,
                    "accountCount": 2,
                }
            ],
            "sellerOverview": [
                {"name": "Casey Rivera", "manager": "Morgan Lee", "forecast": 1_750_000}
            ],
            "evidenceGaps": ["No prior forecast snapshot was supplied."],
        }

    @staticmethod
    def dashboard_identity(persona: str, *, viewer: str = "Jordan Park") -> dict[str, object]:
        return {
            "persona": persona,
            "owner": {
                "name": viewer,
                "id": f"verified-viewer-{viewer.casefold().replace(' ', '-')}",
            },
            "scope": f"{viewer}'s private {persona} dashboard",
        }

    @classmethod
    def placeholder_payload(cls, persona: str, *, viewer: str = "Jordan Park") -> dict[str, object]:
        payload: dict[str, object] = {
            "dashboardMode": "placeholder",
            "dashboardLabel": "Empty placeholder — no verified sales data",
            "dashboardIdentity": cls.dashboard_identity(persona, viewer=viewer),
            "title": "Empty sales dashboard placeholder",
            "company": {"name": "Summit Analytics"},
            "evidenceGaps": ["No verified account, team, or forecast data was supplied."],
        }
        if persona == "seller":
            payload.update(
                {
                    "connectedSources": [],
                    "workNow": [],
                    "watch": [],
                    "paused": [],
                    "accountDetails": {},
                }
            )
        else:
            payload.update(
                {
                    "sourceCoverage": [],
                    "forecast": {},
                    "topDeals": [],
                    "divisionTeams": [],
                    "sellerOverview": [],
                    "metrics": [],
                }
            )
        return payload

    @classmethod
    def representative_payload(
        cls, persona: str, *, viewer: str = "Jordan Park"
    ) -> dict[str, object]:
        payload = cls.seller_payload() if persona == "seller" else cls.leadership_payload()
        return {
            **payload,
            "dashboardMode": "representative",
            "dashboardLabel": "Representative view of verified available sales data",
            "dashboardIdentity": cls.dashboard_identity(persona, viewer=viewer),
        }

    def embedded_payload(self, html: str, persona: str) -> tuple[dict[str, object], int, int]:
        marker = RENDERER.PERSONA_ASSIGNMENTS[persona]
        self.assertEqual(html.count(marker), 1)
        value_start = html.index(marker) + len(marker)
        whitespace = len(html[value_start:]) - len(html[value_start:].lstrip())
        value_start += whitespace
        payload, consumed = json.JSONDecoder().raw_decode(html[value_start:])
        self.assertIsInstance(payload, dict)
        self.assertTrue(html[value_start + consumed :].lstrip().startswith(";"))
        return payload, value_start, value_start + consumed

    def test_persona_templates_reuse_actual_interactive_sales_dashboards(self) -> None:
        expected_assets = {
            "seller": "account-priority-workspace.template.html",
            "leadership": "sales-leadership-dashboard.template.html",
        }

        for persona, filename in expected_assets.items():
            with self.subTest(persona=persona):
                self.assertEqual(
                    RENDERER.PERSONA_TEMPLATES[persona],
                    DEMO_SKILL_DIRECTORY / "assets" / filename,
                )

    def test_real_seller_dashboard_uses_personalized_grounded_data_without_demo_defaults(
        self,
    ) -> None:
        payload = self.seller_payload()
        project = self.project_root / "casey-owned-account-home"

        output = RENDERER.render_dashboard("seller", payload, project)

        self.assertEqual(output, project.resolve() / "index.html")
        rendered = output.read_text(encoding="utf-8")
        embedded, _, _ = self.embedded_payload(rendered, "seller")
        self.assertEqual(embedded, payload)
        self.assertIn("Casey Rivera", rendered)
        self.assertIn("Harbor Health", rendered)
        self.assertIn("Cedar Energy", rendered)
        self.assertNotIn("__PRIORITIZE_ACCOUNTS_DATA_JSON__", rendered)
        for view in ("Home", "Accounts", "Pipeline"):
            with self.subTest(view=view):
                self.assertRegex(rendered, rf">{view}</button>")
        for fictional_identity in ("Riley Morgan", "Meridian Cloud", "Northstar Health"):
            with self.subTest(fictional_identity=fictional_identity):
                self.assertFalse(
                    fictional_identity in rendered,
                    f"Fictional dashboard identity leaked: {fictional_identity}",
                )
        self.assert_excludes(
            rendered,
            'id="book-value-metric">10<',
            'id="renewal-value-metric">5<',
            'id="source-count-metric">6 sources<',
            'id="accounts-summary">10 accounts · 3 need attention<',
        )
        self.assertFalse((project / ".openai" / "hosting.json").exists())

    def test_real_leadership_dashboard_uses_verified_division_evidence_without_demo_copy(
        self,
    ) -> None:
        payload = self.leadership_payload()
        output = RENDERER.render_dashboard(
            "leadership", payload, self.project_root / "priya-revenue-dashboard"
        )

        rendered = output.read_text(encoding="utf-8")
        embedded, _, _ = self.embedded_payload(rendered, "leadership")
        self.assertEqual(embedded, payload)
        self.assertIn("Priya Desai", rendered)
        self.assertIn("Summit Analytics", rendered)
        self.assertIn("Harbor Health", rendered)
        self.assertIn("Forecast &amp; key metrics", rendered)
        self.assertIn("Account Focus", rendered)
        self.assertIn("Team Focus", rendered)
        self.assertNotIn("__LEADERSHIP_DATA_JSON__", rendered)
        for fictional_identity in ("Meridian Cloud", "Maya Chen", "Northstar"):
            with self.subTest(fictional_identity=fictional_identity):
                self.assertFalse(
                    fictional_identity in rendered,
                    f"Fictional dashboard identity leaked: {fictional_identity}",
                )

    def test_codex_pet_is_rendered_only_from_a_safe_supplied_image(self) -> None:
        image_url = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ"
        pet = {"name": "Codex", "imageUrl": image_url}

        for persona, baseline in (
            ("seller", self.seller_payload()),
            ("leadership", self.leadership_payload()),
        ):
            with self.subTest(persona=persona):
                payload = {**baseline, "codexPet": pet}
                output = RENDERER.render_dashboard(
                    persona, payload, self.project_root / f"pet-{persona}"
                )
                rendered = output.read_text(encoding="utf-8")
                embedded, _, _ = self.embedded_payload(rendered, persona)
                self.assertEqual(embedded["codexPet"], pet)
                self.assertIn('id="codex-pet"', rendered)
                self.assertIn("suppliedCodexPet", rendered)

        invalid_pets: tuple[object, ...] = (
            {"name": "Codex", "imageUrl": "https://example.com/pet.png"},
            {"name": "Codex", "imageUrl": "data:image/svg+xml;base64,PHN2Zz4="},
            {"name": "Codex"},
            {"name": "", "imageUrl": image_url},
            "Codex",
        )
        for index, pet_value in enumerate(invalid_pets):
            with self.subTest(invalid_pet=pet_value):
                with self.assertRaises(ValueError):
                    RENDERER.render_dashboard(
                        "seller",
                        {**self.seller_payload(), "codexPet": pet_value},
                        self.project_root / f"invalid-pet-{index}",
                    )

    def test_escapes_script_terminators_without_changing_real_customer_text(self) -> None:
        customer_text = '</script><script>alert("customer-data")</script>'

        for persona, payload in (
            ("seller", {**self.seller_payload(), "title": customer_text}),
            ("leadership", {**self.leadership_payload(), "title": customer_text}),
        ):
            with self.subTest(persona=persona):
                output = RENDERER.render_dashboard(
                    persona, payload, self.project_root / f"escaped-{persona}"
                )
                rendered = output.read_text(encoding="utf-8")
                embedded, _, _ = self.embedded_payload(rendered, persona)

                self.assertNotIn(customer_text, rendered)
                self.assertIn(r"\u003c/script>\u003cscript>", rendered)
                self.assertEqual(embedded["title"], customer_text)

    def test_rejects_actual_fictional_demo_payloads_and_fictional_markers(self) -> None:
        actual_fixtures = {
            "seller": DEMO_SKILL_DIRECTORY / "references" / "demo-portfolio.json",
            "leadership": DEMO_SKILL_DIRECTORY / "references" / "demo-leadership.json",
        }

        for persona, fixture_path in actual_fixtures.items():
            with self.subTest(persona=persona, marker="bundled fictional fixture"):
                fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
                project = self.project_root / f"fictional-fixture-{persona}"
                with self.assertRaises(ValueError):
                    RENDERER.render_dashboard(persona, fixture, project)
                self.assertFalse(project.exists())

            baseline = self.seller_payload() if persona == "seller" else self.leadership_payload()
            fictional_markers: tuple[tuple[str, dict[str, object]], ...] = (
                ("demo", {"mode": "FiCtIoNaL"}),
                ("disclosure", {"isFictional": True}),
                ("source", {"label": "Fictional connected account sample"}),
            )
            for key, marker in fictional_markers:
                with self.subTest(persona=persona, marker=key):
                    with self.assertRaises(ValueError):
                        RENDERER.render_dashboard(
                            persona,
                            {**baseline, key: marker},
                            self.project_root / f"fictional-{persona}-{key}",
                        )

    def test_real_dashboards_require_at_least_one_explicitly_verified_source(self) -> None:
        personas = (
            ("seller", self.seller_payload(), "connectedSources"),
            ("leadership", self.leadership_payload(), "sourceCoverage"),
        )
        invalid_sources: tuple[object, ...] = (
            [],
            [{"name": "Salesforce", "verified": False}],
            [{"name": "Salesforce"}],
            [{"verified": True}],
            [{"name": "Fictional Salesforce fixture", "verified": True}],
            [{"name": "Salesforce", "label": "Simulated sample", "verified": True}],
            [{"name": "Salesforce", "status": "Disconnected", "verified": True}],
            [{"name": "Salesforce", "status": "Not connected", "verified": True}],
            ["Salesforce"],
            "Salesforce",
        )

        for persona, payload, source_key in personas:
            for index, records in enumerate(invalid_sources):
                with self.subTest(persona=persona, source_records=records):
                    with self.assertRaises(ValueError):
                        RENDERER.render_dashboard(
                            persona,
                            {**payload, source_key: records},
                            self.project_root / f"unverified-{persona}-{index}",
                        )

            unmarked_export = {key: value for key, value in payload.items() if key != source_key}
            with self.assertRaises(ValueError):
                RENDERER.render_dashboard(
                    persona, unmarked_export, self.project_root / f"unmarked-export-{persona}"
                )

            authoritative_export = {
                **unmarked_export,
                source_key: [{"name": "User-provided CRM export", "verified": True}],
            }
            output = RENDERER.render_dashboard(
                persona, authoritative_export, self.project_root / f"verified-export-{persona}"
            )
            embedded, _, _ = self.embedded_payload(output.read_text(encoding="utf-8"), persona)
            self.assertEqual(embedded[source_key], authoritative_export[source_key])

    def test_empty_placeholder_renders_both_personas_without_sales_identity_or_sources(
        self,
    ) -> None:
        for persona in ("seller", "leadership"):
            with self.subTest(persona=persona):
                payload = self.placeholder_payload(persona)
                output = RENDERER.render_dashboard(
                    persona, payload, self.project_root / f"empty-{persona}", mode="placeholder"
                )

                rendered = output.read_text(encoding="utf-8")
                embedded, _, _ = self.embedded_payload(rendered, persona)
                self.assertEqual(embedded, payload)
                self.assertIn('data-sales-dashboard-disclosure="placeholder"', rendered)
                self.assertIn('data-sales-dashboard-empty-state="true"', rendered)
                self.assertIn("Empty placeholder; no verified customer, account, team", rendered)
                self.assertIn("Jordan Park", rendered)
                self.assertNotIn("Casey Rivera", rendered)
                self.assertNotIn("Priya Desai", rendered)
                self.assertNotIn("Harbor Health", rendered)
                self.assertNotIn("Northstar", rendered)
                self.assertNotIn("Meridian Cloud", rendered)
                self.assertFalse(embedded.get("connectedSources", []))
                self.assertFalse(embedded.get("sourceCoverage", []))
                self.assertFalse(embedded.get("forecast", {}))
                self.assertFalse(embedded.get("workNow", []))
                self.assertFalse(embedded.get("topDeals", []))
                self.assertIn("No verified account or opportunity data is available.", rendered)
                self.assertIn("Account follow-up data unavailable.", rendered)

    def test_placeholder_rejects_sales_data_fake_roles_sources_and_nested_smuggling(self) -> None:
        for persona in ("seller", "leadership"):
            baseline = self.placeholder_payload(persona)
            identity = baseline["dashboardIdentity"]
            assert isinstance(identity, dict)
            owner = identity["owner"]
            assert isinstance(owner, dict)
            invalid_payloads: dict[str, dict[str, object]] = {
                "missing-marker": {
                    key: value for key, value in baseline.items() if key != "dashboardMode"
                },
                "wrong-marker": {**baseline, "dashboardMode": "representative"},
                "missing-label": {
                    key: value for key, value in baseline.items() if key != "dashboardLabel"
                },
                "misleading-label": {**baseline, "dashboardLabel": "Your verified sales data"},
                "missing-viewer-identity": {
                    key: value for key, value in baseline.items() if key != "dashboardIdentity"
                },
                "wrong-persona": {
                    **baseline,
                    "dashboardIdentity": {
                        **identity,
                        "persona": "leadership" if persona == "seller" else "seller",
                    },
                },
                "anonymous-viewer": {
                    **baseline,
                    "dashboardIdentity": {**identity, "owner": {"name": " "}},
                },
                "hidden-viewer-role": {
                    **baseline,
                    "dashboardIdentity": {
                        **identity,
                        "owner": {**owner, "role": "Vice President of Sales"},
                    },
                },
                "nested-viewer-account": {
                    **baseline,
                    "dashboardIdentity": {**identity, "accounts": ["Sensitive Customer"]},
                },
                "nested-viewer-identifier": {
                    **baseline,
                    "dashboardIdentity": {
                        **identity,
                        "owner": {**owner, "id": {"forecast": 999_999}},
                    },
                },
                "anonymous-scope": {
                    **baseline,
                    "dashboardIdentity": {**identity, "scope": " "},
                },
                "seller-claim": {**baseline, "seller": {"name": "Fake Sales Owner"}},
                "leadership-claim": {
                    **baseline,
                    "company": {
                        "name": "Summit Analytics",
                        "divisionLead": {"name": "Fake Sales Leader"},
                    },
                },
                "scope-claim": {
                    **baseline,
                    "scope": {"accountSet": "Another seller's private accounts"},
                },
                "source-claim": {**baseline, "source": {"label": "Verified Salesforce"}},
                "connected-source": {
                    **baseline,
                    "connectedSources": [{"name": "Salesforce", "verified": True}],
                },
                "leadership-source": {
                    **baseline,
                    "sourceCoverage": [{"name": "Salesforce", "verified": True}],
                },
                "customer-account": {
                    **baseline,
                    "workNow": [{"account": "Sensitive Customer", "owner": "Other Seller"}],
                },
                "customer-details": {
                    **baseline,
                    "accountDetails": {"Sensitive Customer": {"value": 999_999}},
                },
                "customer-deal": {
                    **baseline,
                    "topDeals": [{"account": "Sensitive Customer", "value": 999_999}],
                },
                "forecast-target": {**baseline, "forecast": {"target": 999_999}},
                "reporting-metrics": {**baseline, "reporting": {"teamAccountCount": 10}},
                "seller-team": {**baseline, "divisionTeams": [{"manager": "Other Leader"}]},
                "business-metrics": {**baseline, "metrics": [{"value": 999_999}]},
                "unknown-opportunities": {
                    **baseline,
                    "opportunities": [{"account": "Sensitive Customer"}],
                },
                "nested-title": {**baseline, "title": {"forecast": 999_999}},
                "nested-timestamp": {
                    **baseline,
                    "generatedAt": {"accounts": ["Sensitive Customer"]},
                },
                "nested-disclosure": {
                    **baseline,
                    "disclosure": {"isFictional": {"accounts": ["Sensitive Customer"]}},
                },
                "fictional-disclosure": {**baseline, "disclosure": {"isFictional": True}},
            }

            for invalid_case, invalid_payload in invalid_payloads.items():
                with self.subTest(persona=persona, invalid_case=invalid_case):
                    project = self.project_root / f"{persona}-unsafe-{invalid_case}"
                    with self.assertRaises(ValueError):
                        RENDERER.render_dashboard(
                            persona, invalid_payload, project, mode="placeholder"
                        )
                    self.assertFalse(project.exists())

    def test_representative_view_preserves_actual_owner_and_separate_requesting_viewer(
        self,
    ) -> None:
        for persona, expected_owner in (("seller", "Casey Rivera"), ("leadership", "Priya Desai")):
            with self.subTest(persona=persona):
                payload = self.representative_payload(persona)
                output = RENDERER.render_dashboard(
                    persona,
                    payload,
                    self.project_root / f"representative-{persona}",
                    mode="representative",
                )

                rendered = output.read_text(encoding="utf-8")
                embedded, _, _ = self.embedded_payload(rendered, persona)
                self.assertEqual(embedded, payload)
                self.assertIn('data-sales-dashboard-disclosure="representative"', rendered)
                self.assertNotIn('data-sales-dashboard-empty-state="true"', rendered)
                self.assertIn(
                    f"Verified data for {expected_owner}; requested by Jordan Park", rendered
                )
                self.assertIn("Not the requester&#x27;s own sales dashboard.", rendered)
                self.assertIn("Harbor Health", rendered)

                viewer_identity = embedded["dashboardIdentity"]
                assert isinstance(viewer_identity, dict)
                viewer = viewer_identity["owner"]
                assert isinstance(viewer, dict)
                self.assertEqual(viewer["name"], "Jordan Park")
                if persona == "seller":
                    represented = embedded["seller"]
                    assert isinstance(represented, dict)
                    self.assertEqual(represented["name"], expected_owner)
                else:
                    company = embedded["company"]
                    assert isinstance(company, dict)
                    represented = company["divisionLead"]
                    assert isinstance(represented, dict)
                    self.assertEqual(represented["name"], expected_owner)

    def test_representative_rejects_unverified_sources_and_anonymous_viewers_or_owners(
        self,
    ) -> None:
        for persona in ("seller", "leadership"):
            baseline = self.representative_payload(persona)
            identity = baseline["dashboardIdentity"]
            assert isinstance(identity, dict)
            source_key = "connectedSources" if persona == "seller" else "sourceCoverage"
            invalid_payloads: dict[str, dict[str, object]] = {
                "missing-source": {
                    key: value for key, value in baseline.items() if key != source_key
                },
                "empty-source": {**baseline, source_key: []},
                "unverified-source": {
                    **baseline,
                    source_key: [{"name": "Salesforce", "verified": False}],
                },
                "fictional-source": {
                    **baseline,
                    source_key: [{"name": "Fictional Salesforce fixture", "verified": True}],
                },
                "disconnected-source": {
                    **baseline,
                    source_key: [
                        {"name": "Salesforce", "verified": True, "status": "Disconnected"}
                    ],
                },
                "anonymous-viewer": {
                    **baseline,
                    "dashboardIdentity": {**identity, "owner": {"name": " "}},
                },
                "missing-viewer": {
                    key: value for key, value in baseline.items() if key != "dashboardIdentity"
                },
                "wrong-persona": {
                    **baseline,
                    "dashboardIdentity": {
                        **identity,
                        "persona": "leadership" if persona == "seller" else "seller",
                    },
                },
                "misleading-label": {**baseline, "dashboardLabel": "Your exact owned dashboard"},
                "missing-marker": {
                    key: value for key, value in baseline.items() if key != "dashboardMode"
                },
                "viewer-impersonates-represented-owner": {
                    **baseline,
                    "dashboardIdentity": self.dashboard_identity(
                        persona,
                        viewer="Casey Rivera" if persona == "seller" else "Priya Desai",
                    ),
                },
            }
            if persona == "seller":
                accounts = baseline["workNow"]
                assert isinstance(accounts, list)
                account = accounts[0]
                assert isinstance(account, dict)
                invalid_payloads["viewer-impersonates-account-owner"] = {
                    **baseline,
                    "workNow": [{**account, "owner": "Jordan Park"}],
                }
            else:
                company = baseline["company"]
                assert isinstance(company, dict)
                invalid_payloads["anonymous-represented-owner"] = {
                    **baseline,
                    "company": {**company, "divisionLead": {"id": "leader-without-display-name"}},
                }

            for invalid_case, invalid_payload in invalid_payloads.items():
                with self.subTest(persona=persona, invalid_case=invalid_case):
                    project = self.project_root / f"{persona}-bad-representative-{invalid_case}"
                    with self.assertRaises(ValueError):
                        RENDERER.render_dashboard(
                            persona, invalid_payload, project, mode="representative"
                        )
                    self.assertFalse(project.exists())

    def test_dashboard_mode_must_match_explicit_payload_marker_in_both_directions(self) -> None:
        for persona in ("seller", "leadership"):
            real = self.seller_payload() if persona == "seller" else self.leadership_payload()
            fallback = self.placeholder_payload(persona)
            representative = self.representative_payload(persona)
            invalid_cases = (
                ("placeholder-with-real-payload", "placeholder", real),
                ("representative-with-real-payload", "representative", real),
                ("real-with-placeholder-marker", "real", fallback),
                ("real-with-representative-marker", "real", representative),
                ("placeholder-with-representative-marker", "placeholder", representative),
                ("representative-with-placeholder-marker", "representative", fallback),
                (
                    "real-with-hidden-fallback-metadata",
                    "real",
                    {
                        **real,
                        "dashboardIdentity": self.dashboard_identity(persona),
                        "dashboardLabel": "Representative view",
                    },
                ),
                ("unsupported-mode", "simulated", real),
            )
            for invalid_case, mode, payload in invalid_cases:
                with self.subTest(persona=persona, invalid_case=invalid_case):
                    project = self.project_root / f"{persona}-{invalid_case}"
                    with self.assertRaises(ValueError):
                        RENDERER.render_dashboard(persona, payload, project, mode=mode)
                    self.assertFalse(project.exists())

    def test_fallback_disclosures_escape_user_controlled_labels_and_viewer_names(self) -> None:
        unsafe_viewer = 'Jordan <img src=x onerror="alert(1)">'
        for persona in ("seller", "leadership"):
            for mode in ("placeholder", "representative"):
                with self.subTest(persona=persona, mode=mode):
                    payload = (
                        self.placeholder_payload(persona, viewer=unsafe_viewer)
                        if mode == "placeholder"
                        else self.representative_payload(persona, viewer=unsafe_viewer)
                    )
                    unsafe_label = f'{mode.title()} <script>alert("dashboard")</script>'
                    payload["dashboardLabel"] = unsafe_label
                    output = RENDERER.render_dashboard(
                        persona,
                        payload,
                        self.project_root / f"escaped-{mode}-{persona}",
                        mode=mode,
                    )
                    rendered = output.read_text(encoding="utf-8")
                    embedded, _, _ = self.embedded_payload(rendered, persona)

                    self.assertEqual(embedded["dashboardLabel"], unsafe_label)
                    self.assertIn(
                        "&lt;script&gt;alert(&quot;dashboard&quot;)&lt;/script&gt;", rendered
                    )
                    self.assertIn("Jordan &lt;img src=x onerror=&quot;alert(1)&quot;&gt;", rendered)
                    self.assertNotIn(unsafe_label, rendered)
                    self.assertNotIn(unsafe_viewer, rendered)

    def test_seller_requires_verified_owner_scope_unique_accounts_and_complete_groups(self) -> None:
        payload = self.seller_payload()
        scope = payload["scope"]
        owner = payload["seller"]
        work_now = payload["workNow"]
        assert isinstance(scope, dict)
        assert isinstance(owner, dict)
        assert isinstance(work_now, list)
        account = work_now[0]
        assert isinstance(account, dict)

        invalid_payloads = {
            "missing-owner": {**payload, "seller": {}},
            "blank-owner": {**payload, "seller": {**owner, "name": "  "}},
            "missing-source-of-truth": {**payload, "scope": {**scope, "sourceOfTruth": ""}},
            "missing-account-set": {**payload, "scope": {**scope, "accountSet": ""}},
            "missing-account-group": {
                key: value for key, value in payload.items() if key != "watch"
            },
            "duplicate-account": {**payload, "watch": [{**account, "account": "HARBOR HEALTH"}]},
            "different-account-owner": {
                **payload,
                "workNow": [{**account, "owner": "A different account owner"}],
            },
            "blank-account": {**payload, "workNow": [{**account, "account": " "}]},
        }

        for invalid_case, invalid_payload in invalid_payloads.items():
            with self.subTest(invalid_case=invalid_case):
                with self.assertRaises(ValueError):
                    RENDERER.render_dashboard(
                        "seller", invalid_payload, self.project_root / invalid_case
                    )

    def test_leadership_requires_company_and_forecast_without_inventing_optional_data(self) -> None:
        verified_company = {
            "name": "Summit Analytics",
            "division": "Enterprise Revenue",
            "divisionLead": {"name": "Priya Desai"},
        }
        for invalid_case, payload in (
            ("missing-company", {"forecast": {}}),
            ("blank-company", {"company": {"name": " "}, "forecast": {}}),
            ("anonymous-company", {"company": "Summit Analytics", "forecast": {}}),
            (
                "missing-division",
                {
                    "company": {
                        key: value for key, value in verified_company.items() if key != "division"
                    },
                    "forecast": {},
                },
            ),
            (
                "missing-owner",
                {
                    "company": {
                        key: value
                        for key, value in verified_company.items()
                        if key != "divisionLead"
                    },
                    "forecast": {},
                },
            ),
            (
                "anonymous-owner",
                {"company": {**verified_company, "divisionLead": {"name": " "}}, "forecast": {}},
            ),
            ("missing-forecast", {"company": verified_company}),
        ):
            with self.subTest(invalid_case=invalid_case):
                with self.assertRaises(ValueError):
                    RENDERER.render_dashboard(
                        "leadership", payload, self.project_root / invalid_case
                    )

        minimal_payload = {
            "company": verified_company,
            "forecast": {},
            "sourceCoverage": [{"name": "User-provided CRM export", "verified": True}],
        }
        output = RENDERER.render_dashboard(
            "leadership", minimal_payload, self.project_root / "minimal-grounded-leadership"
        )
        embedded, _, _ = self.embedded_payload(output.read_text(encoding="utf-8"), "leadership")
        self.assertEqual(embedded, minimal_payload)
        forecast = embedded["forecast"]
        self.assertIsInstance(forecast, dict)
        self.assert_excludes(
            forecast,
            "target",
            "weeklyMovement",
            "previousQuarter",
            "confidence",
            "scenarios",
            "sellerGrowth",
        )

    def test_refresh_preserves_custom_html_hosting_identity_and_other_project_files(self) -> None:
        personas = (
            ("seller", self.seller_payload()),
            ("leadership", self.leadership_payload()),
        )

        for persona, original_payload in personas:
            with self.subTest(persona=persona):
                project = self.project_root / f"existing-{persona}-project"
                hosting = project / ".openai" / "hosting.json"
                hosting.parent.mkdir(parents=True)
                hosting_text = f'{{"project_id":"private-{persona}-project"}}\n'
                hosting.write_text(hosting_text, encoding="utf-8")
                user_styles = project / "customer-theme.css"
                user_styles.write_text(
                    "/* preserve the seller's custom theme */\n", encoding="utf-8"
                )

                output = RENDERER.render_dashboard(persona, original_payload, project)
                customized = output.read_text(encoding="utf-8").replace(
                    "</head>",
                    '<meta name="user-custom-layout" content="saved-account-filters" />\n</head>',
                    1,
                )
                output.write_text(customized, encoding="utf-8")
                _, previous_start, previous_end = self.embedded_payload(customized, persona)

                refreshed_payload = {
                    **original_payload,
                    "title": f"Updated {persona} dashboard for the same verified owner",
                    "evidenceGaps": ["Updated verified account context."],
                }
                refreshed_output = RENDERER.render_dashboard(persona, refreshed_payload, project)
                refreshed = refreshed_output.read_text(encoding="utf-8")
                embedded, refreshed_start, refreshed_end = self.embedded_payload(refreshed, persona)

                self.assertEqual(refreshed_output, output)
                self.assertEqual(embedded, refreshed_payload)
                self.assertEqual(
                    customized[:previous_start] + customized[previous_end:],
                    refreshed[:refreshed_start] + refreshed[refreshed_end:],
                )
                self.assertIn('name="user-custom-layout"', refreshed)
                self.assertEqual(hosting.read_text(encoding="utf-8"), hosting_text)
                self.assertEqual(
                    user_styles.read_text(encoding="utf-8"),
                    "/* preserve the seller's custom theme */\n",
                )

    def test_refresh_rejects_different_persona_owner_scope_or_leadership_identity(self) -> None:
        seller_project = self.project_root / "existing-casey-account-home"
        seller_output = RENDERER.render_dashboard("seller", self.seller_payload(), seller_project)
        original_seller_html = seller_output.read_text(encoding="utf-8")
        seller_mismatches = (
            ("different-persona", "leadership", self.leadership_payload()),
            (
                "different-owner",
                "seller",
                self.seller_payload(
                    owner="Jordan Park", account_scope="Jordan Park's enterprise accounts"
                ),
            ),
            (
                "different-account-scope",
                "seller",
                self.seller_payload(account_scope="Casey Rivera's unrelated strategic territory"),
            ),
        )

        for mismatch, persona, payload in seller_mismatches:
            with self.subTest(mismatch=mismatch):
                with self.assertRaises(ValueError):
                    RENDERER.render_dashboard(persona, payload, seller_project)
                self.assertEqual(seller_output.read_text(encoding="utf-8"), original_seller_html)

        leadership_project = self.project_root / "existing-priya-leadership-dashboard"
        leadership_output = RENDERER.render_dashboard(
            "leadership", self.leadership_payload(), leadership_project
        )
        original_leadership_html = leadership_output.read_text(encoding="utf-8")
        leadership_mismatches = {
            "different-company": self.leadership_payload(company="Unrelated Organization"),
            "different-division": self.leadership_payload(division="Unrelated Division"),
            "different-leader": self.leadership_payload(leader="Another Sales Leader"),
        }

        for mismatch, payload in leadership_mismatches.items():
            with self.subTest(mismatch=mismatch):
                with self.assertRaises(ValueError):
                    RENDERER.render_dashboard("leadership", payload, leadership_project)
                self.assertEqual(
                    leadership_output.read_text(encoding="utf-8"), original_leadership_html
                )

    def test_refresh_accepts_stable_owner_ids_without_resetting_verified_name_continuity(
        self,
    ) -> None:
        for persona, name_only, renamed in (
            (
                "seller",
                self.seller_payload(),
                self.seller_payload(
                    owner="Casey Morgan",
                    account_scope="Casey Rivera's complete enterprise account book",
                ),
            ),
            (
                "leadership",
                self.leadership_payload(),
                self.leadership_payload(leader="Priya Shah"),
            ),
        ):
            with_id = json.loads(json.dumps(name_only))
            renamed_with_id = json.loads(json.dumps(renamed))
            for identified_payload in (with_id, renamed_with_id):
                if persona == "seller":
                    owner = identified_payload["seller"]
                else:
                    owner = identified_payload["company"]["divisionLead"]
                owner["id"] = f"verified-{persona}-owner"

            continuity_cases = (
                ("stable-id-added", name_only, with_id),
                ("stable-id-removed", with_id, name_only),
                ("verified-owner-renamed", with_id, renamed_with_id),
            )
            for transition, original, refreshed_payload in continuity_cases:
                with self.subTest(persona=persona, transition=transition):
                    project = self.project_root / f"{persona}-{transition}"
                    output = RENDERER.render_dashboard(persona, original, project)
                    customized = output.read_text(encoding="utf-8").replace(
                        "</head>", '<meta name="preserve-owner-dashboard" />\n</head>', 1
                    )
                    output.write_text(customized, encoding="utf-8")
                    hosting = project / ".openai" / "hosting.json"
                    hosting.parent.mkdir()
                    hosting.write_text('{"project_id":"existing-private-dashboard"}\n')

                    refreshed = RENDERER.render_dashboard(persona, refreshed_payload, project)
                    refreshed_html = refreshed.read_text(encoding="utf-8")
                    embedded, _, _ = self.embedded_payload(refreshed_html, persona)

                    self.assertEqual(refreshed, output)
                    self.assertEqual(embedded, refreshed_payload)
                    self.assertIn('name="preserve-owner-dashboard"', refreshed_html)
                    self.assertEqual(
                        hosting.read_text(encoding="utf-8"),
                        '{"project_id":"existing-private-dashboard"}\n',
                    )

    def test_fallback_refresh_preserves_visible_disclosure_customizations_and_viewer_identity(
        self,
    ) -> None:
        for persona in ("seller", "leadership"):
            for mode in ("placeholder", "representative"):
                with self.subTest(persona=persona, mode=mode):
                    original = (
                        self.placeholder_payload(persona)
                        if mode == "placeholder"
                        else self.representative_payload(persona)
                    )
                    project = self.project_root / f"refresh-{mode}-{persona}"
                    output = RENDERER.render_dashboard(persona, original, project, mode=mode)
                    customized = output.read_text(encoding="utf-8").replace(
                        "</head>", '<meta name="preserve-fallback-customization" />\n</head>', 1
                    )
                    output.write_text(customized, encoding="utf-8")
                    hosting = project / ".openai" / "hosting.json"
                    hosting.parent.mkdir()
                    hosting.write_text('{"project_id":"existing-fallback-dashboard"}\n')

                    refreshed_payload = json.loads(json.dumps(original))
                    refreshed_payload["dashboardLabel"] = f"Updated {mode} with truthful disclosure"
                    identity = refreshed_payload["dashboardIdentity"]
                    assert isinstance(identity, dict)
                    viewer = identity["owner"]
                    assert isinstance(viewer, dict)
                    viewer["name"] = "Jordan Morgan"

                    refreshed = RENDERER.render_dashboard(
                        persona, refreshed_payload, project, mode=mode
                    )
                    rendered = refreshed.read_text(encoding="utf-8")
                    embedded, _, _ = self.embedded_payload(rendered, persona)

                    self.assertEqual(refreshed, output)
                    self.assertEqual(embedded, refreshed_payload)
                    self.assertEqual(len(RENDERER.DISCLOSURE_PATTERN.findall(rendered)), 1)
                    self.assertIn(f"Updated {mode} with truthful disclosure", rendered)
                    self.assertIn('data-sales-dashboard-viewer="Jordan Morgan"', rendered)
                    self.assertIn('name="preserve-fallback-customization"', rendered)
                    self.assertEqual(
                        hosting.read_text(encoding="utf-8"),
                        '{"project_id":"existing-fallback-dashboard"}\n',
                    )
                    if mode == "placeholder":
                        self.assertIn('data-sales-dashboard-empty-state="true"', rendered)

    def test_refresh_never_converts_between_real_placeholder_and_representative_modes(
        self,
    ) -> None:
        for persona in ("seller", "leadership"):
            payloads = {
                "real": self.seller_payload() if persona == "seller" else self.leadership_payload(),
                "placeholder": self.placeholder_payload(persona),
                "representative": self.representative_payload(persona),
            }
            for existing_mode, original in payloads.items():
                for replacement_mode, replacement in payloads.items():
                    if existing_mode == replacement_mode:
                        continue
                    with self.subTest(
                        persona=persona,
                        existing_mode=existing_mode,
                        replacement_mode=replacement_mode,
                    ):
                        project = self.project_root / (
                            f"{persona}-{existing_mode}-to-{replacement_mode}"
                        )
                        output = RENDERER.render_dashboard(
                            persona, original, project, mode=existing_mode
                        )
                        original_html = output.read_text(encoding="utf-8")

                        with self.assertRaises(ValueError):
                            RENDERER.render_dashboard(
                                persona, replacement, project, mode=replacement_mode
                            )

                        self.assertEqual(output.read_text(encoding="utf-8"), original_html)

    def test_fallback_refresh_rejects_another_viewer_viewer_scope_or_represented_owner(
        self,
    ) -> None:
        for persona in ("seller", "leadership"):
            for mode in ("placeholder", "representative"):
                original = (
                    self.placeholder_payload(persona)
                    if mode == "placeholder"
                    else self.representative_payload(persona)
                )
                another_viewer = json.loads(json.dumps(original))
                identity = another_viewer["dashboardIdentity"]
                assert isinstance(identity, dict)
                identity["owner"] = {"name": "Taylor Brooks", "id": "another-viewers-stable-id"}
                another_viewer_scope = json.loads(json.dumps(original))
                scoped_identity = another_viewer_scope["dashboardIdentity"]
                assert isinstance(scoped_identity, dict)
                scoped_identity["scope"] = "Another private dashboard project scope"
                replacements = {
                    "another-viewer": another_viewer,
                    "another-viewer-scope": another_viewer_scope,
                }

                if mode == "representative":
                    represented_replacement = (
                        self.seller_payload(
                            owner="Avery Price",
                            account_scope="Casey Rivera's complete enterprise account book",
                        )
                        if persona == "seller"
                        else self.leadership_payload(leader="Another Sales Leader")
                    )
                    replacements["another-represented-owner"] = {
                        **represented_replacement,
                        "dashboardMode": "representative",
                        "dashboardLabel": original["dashboardLabel"],
                        "dashboardIdentity": original["dashboardIdentity"],
                    }

                for case, replacement in replacements.items():
                    with self.subTest(persona=persona, mode=mode, case=case):
                        project = self.project_root / f"{persona}-{mode}-{case}"
                        output = RENDERER.render_dashboard(persona, original, project, mode=mode)
                        original_html = output.read_text(encoding="utf-8")

                        with self.assertRaises(ValueError):
                            RENDERER.render_dashboard(persona, replacement, project, mode=mode)

                        self.assertEqual(output.read_text(encoding="utf-8"), original_html)

    def test_fallback_refresh_rejects_removed_or_mismatched_visible_disclosures(self) -> None:
        for persona in ("seller", "leadership"):
            for mode in ("placeholder", "representative"):
                original = (
                    self.placeholder_payload(persona)
                    if mode == "placeholder"
                    else self.representative_payload(persona)
                )
                tampered_markers = [
                    (
                        "wrong-mode",
                        f'data-sales-dashboard-disclosure="{mode}"',
                        'data-sales-dashboard-disclosure="hidden"',
                    ),
                    (
                        "hidden-banner",
                        f'<aside data-sales-dashboard-disclosure="{mode}"',
                        f'<aside hidden data-sales-dashboard-disclosure="{mode}"',
                    ),
                    (
                        "aria-hidden-banner",
                        f'<aside data-sales-dashboard-disclosure="{mode}"',
                        f'<aside aria-hidden="true" data-sales-dashboard-disclosure="{mode}"',
                    ),
                    (
                        "css-hidden-banner",
                        'style="padding:14px',
                        'style="display:none;padding:14px',
                    ),
                    (
                        "missing-viewer",
                        'data-sales-dashboard-viewer="Jordan Park" ',
                        "",
                    ),
                    (
                        "different-viewer",
                        'data-sales-dashboard-viewer="Jordan Park"',
                        'data-sales-dashboard-viewer="Another Viewer"',
                    ),
                ]
                if mode == "placeholder":
                    tampered_markers.extend(
                        (
                            (
                                "missing-empty-state",
                                'data-sales-dashboard-empty-state="true"',
                                'data-sales-dashboard-empty-state="removed"',
                            ),
                            (
                                "inert-empty-state",
                                '<script data-sales-dashboard-empty-state="true">',
                                (
                                    '<script data-sales-dashboard-empty-state="true" '
                                    'type="application/json">'
                                ),
                            ),
                            (
                                "altered-empty-state",
                                "No verified account or opportunity data is available.",
                                "Every customer account is healthy.",
                            ),
                        )
                    )
                for case, original_marker, replacement_marker in tampered_markers:
                    with self.subTest(persona=persona, mode=mode, case=case):
                        project = self.project_root / (f"tampered-{persona}-{mode}-{case}")
                        output = RENDERER.render_dashboard(persona, original, project, mode=mode)
                        tampered = output.read_text(encoding="utf-8").replace(
                            original_marker, replacement_marker, 1
                        )
                        output.write_text(tampered, encoding="utf-8")

                        with self.assertRaises(ValueError):
                            RENDERER.render_dashboard(persona, original, project, mode=mode)

                        self.assertEqual(output.read_text(encoding="utf-8"), tampered)

    def test_refresh_rejects_changed_owner_ids_or_unverified_name_transitions(self) -> None:
        for persona, initial, another_owner in (
            (
                "seller",
                self.seller_payload(),
                self.seller_payload(
                    owner="Jordan Park",
                    account_scope="Casey Rivera's complete enterprise account book",
                ),
            ),
            (
                "leadership",
                self.leadership_payload(),
                self.leadership_payload(leader="Another Sales Leader"),
            ),
        ):
            identified = json.loads(json.dumps(initial))
            different_id = json.loads(json.dumps(initial))
            identified_other_owner = json.loads(json.dumps(another_owner))
            for owner_payload, owner_id in (
                (identified, f"verified-{persona}-owner"),
                (different_id, "another-users-stable-id"),
                (identified_other_owner, "another-users-stable-id"),
            ):
                if persona == "seller":
                    owner = owner_payload["seller"]
                else:
                    owner = owner_payload["company"]["divisionLead"]
                owner["id"] = owner_id

            cross_owner_cases = (
                ("different-ids-with-same-name", identified, different_id),
                ("new-id-with-different-name", initial, identified_other_owner),
                ("removed-id-with-different-name", identified, another_owner),
            )
            for transition, original, replacement in cross_owner_cases:
                with self.subTest(persona=persona, transition=transition):
                    project = self.project_root / f"{persona}-rejected-{transition}"
                    output = RENDERER.render_dashboard(persona, original, project)
                    original_html = output.read_text(encoding="utf-8")

                    with self.assertRaises(ValueError):
                        RENDERER.render_dashboard(persona, replacement, project)

                    self.assertEqual(output.read_text(encoding="utf-8"), original_html)

        id_only_leadership = self.leadership_payload()
        company = id_only_leadership["company"]
        assert isinstance(company, dict)
        company["divisionLead"] = {"id": "verified-leadership-owner"}
        for transition, original, replacement in (
            ("id-only-to-unrelated-name", id_only_leadership, self.leadership_payload()),
            ("name-only-to-anonymous-id", self.leadership_payload(), id_only_leadership),
        ):
            with self.subTest(persona="leadership", transition=transition):
                project = self.project_root / f"leadership-{transition}"
                output = RENDERER.render_dashboard("leadership", original, project)
                original_html = output.read_text(encoding="utf-8")

                with self.assertRaises(ValueError):
                    RENDERER.render_dashboard("leadership", replacement, project)

                self.assertEqual(output.read_text(encoding="utf-8"), original_html)

    def test_refresh_rejects_anonymous_fictional_or_unverified_existing_dashboards(self) -> None:
        seller = self.seller_payload()
        seller_scope = seller["scope"]
        leadership = self.leadership_payload()
        leadership_company = leadership["company"]
        assert isinstance(seller_scope, dict)
        assert isinstance(leadership_company, dict)

        unsafe_existing_payloads: tuple[
            tuple[str, str, dict[str, object], dict[str, object]], ...
        ] = (
            ("missing-seller-owner", "seller", seller, {**seller, "seller": {}}),
            (
                "missing-account-scope",
                "seller",
                seller,
                {**seller, "scope": {**seller_scope, "accountSet": ""}},
            ),
            (
                "fictional-seller",
                "seller",
                seller,
                {**seller, "demo": {"mode": "fictional"}},
            ),
            (
                "unverified-seller-source",
                "seller",
                seller,
                {**seller, "connectedSources": [{"name": "Salesforce", "verified": False}]},
            ),
            (
                "missing-leadership-division",
                "leadership",
                leadership,
                {**leadership, "company": {**leadership_company, "division": ""}},
            ),
            (
                "missing-leadership-owner",
                "leadership",
                leadership,
                {**leadership, "company": {**leadership_company, "divisionLead": {}}},
            ),
            (
                "anonymous-leadership-scope",
                "leadership",
                leadership,
                {**leadership, "company": "Summit Analytics"},
            ),
            (
                "fictional-leadership",
                "leadership",
                leadership,
                {**leadership, "disclosure": {"isFictional": True}},
            ),
        )

        for case, persona, replacement, existing_payload in unsafe_existing_payloads:
            with self.subTest(case=case):
                project = self.project_root / case
                output = RENDERER.render_dashboard(persona, replacement, project)
                original = output.read_text(encoding="utf-8")
                _, start, end = self.embedded_payload(original, persona)
                unsafe_html = (
                    original[:start]
                    + json.dumps(existing_payload, separators=(",", ":")).replace("<", "\\u003c")
                    + original[end:]
                )
                output.write_text(unsafe_html, encoding="utf-8")

                with self.assertRaises(ValueError):
                    RENDERER.render_dashboard(persona, replacement, project)

                self.assertEqual(output.read_text(encoding="utf-8"), unsafe_html)

    def test_unrelated_existing_project_is_never_overwritten(self) -> None:
        project = self.project_root / "unrelated-custom-site"
        project.mkdir()
        original_html = "<!doctype html><html><body>Another user's private project</body></html>"
        index = project / "index.html"
        index.write_text(original_html, encoding="utf-8")

        with self.assertRaises(ValueError):
            RENDERER.render_dashboard("seller", self.seller_payload(), project)

        self.assertEqual(index.read_text(encoding="utf-8"), original_html)

    def test_rejects_symbolic_link_projects_and_pages_without_external_writes(self) -> None:
        outside_project = self.project_root / "another-users-project"
        outside_project.mkdir()
        outside_page = outside_project / "private.html"
        outside_page.write_text("Another user's unchanged private dashboard", encoding="utf-8")

        linked_project = self.project_root / "linked-project"
        linked_project.symlink_to(outside_project, target_is_directory=True)
        with self.assertRaises(ValueError):
            RENDERER.render_dashboard("seller", self.seller_payload(), linked_project)
        self.assertFalse((outside_project / "index.html").exists())

        for persona, payload in (
            ("seller", self.seller_payload()),
            ("leadership", self.leadership_payload()),
        ):
            with self.subTest(persona=persona, link="existing target"):
                project = self.project_root / f"{persona}-linked-index"
                project.mkdir()
                index = project / "index.html"
                index.symlink_to(outside_page)

                with self.assertRaises(ValueError):
                    RENDERER.render_dashboard(persona, payload, project)

                self.assertTrue(index.is_symlink())
                self.assertEqual(
                    outside_page.read_text(encoding="utf-8"),
                    "Another user's unchanged private dashboard",
                )

            with self.subTest(persona=persona, link="missing target"):
                project = self.project_root / f"{persona}-dangling-index"
                project.mkdir()
                missing_target = outside_project / f"{persona}-must-not-be-created.html"
                (project / "index.html").symlink_to(missing_target)

                with self.assertRaises(ValueError):
                    RENDERER.render_dashboard(persona, payload, project)

                self.assertFalse(missing_target.exists())

    def test_rejects_symbolic_links_in_absolute_and_relative_project_ancestors(self) -> None:
        workspace = self.project_root / "selected-user-workspace"
        workspace.mkdir()
        outside_workspace = self.project_root / "another-users-workspace"
        outside_workspace.mkdir()
        redirected_parent = workspace / "linked-account-projects"
        redirected_parent.symlink_to(outside_workspace, target_is_directory=True)

        for persona, payload in (
            ("seller", self.seller_payload()),
            ("leadership", self.leadership_payload()),
        ):
            absolute_project = redirected_parent / f"{persona}-nested" / "dashboard"
            relative_project = Path(os.path.relpath(absolute_project, Path.cwd()))
            for path_kind, requested_project in (
                ("absolute", absolute_project),
                ("relative", relative_project),
            ):
                with self.subTest(persona=persona, path_kind=path_kind):
                    with self.assertRaises(ValueError):
                        RENDERER.render_dashboard(persona, payload, requested_project)

                    self.assertFalse((outside_workspace / f"{persona}-nested").exists())

        existing_project = outside_workspace / "matching-seller-dashboard"
        existing = RENDERER.render_dashboard("seller", self.seller_payload(), existing_project)
        original_html = existing.read_text(encoding="utf-8")

        with self.assertRaises(ValueError):
            RENDERER.render_dashboard(
                "seller",
                {**self.seller_payload(), "title": "Unauthorized redirected refresh"},
                redirected_parent / "matching-seller-dashboard",
            )

        self.assertEqual(existing.read_text(encoding="utf-8"), original_html)

    def test_accepts_safe_relative_dashboard_project_without_symbolic_links(self) -> None:
        expected_project = self.project_root / "safe-relative-user-project"
        relative_project = Path(os.path.relpath(expected_project, Path.cwd()))

        rendered = RENDERER.render_dashboard("seller", self.seller_payload(), relative_project)

        self.assertEqual(rendered, expected_project.resolve() / "index.html")
        self.assertTrue(rendered.is_file())

    @unittest.skipUnless(sys.platform == "darwin", "macOS owns these fixed root aliases")
    def test_accepts_macos_system_temp_aliases_but_rejects_links_below_them(self) -> None:
        for temp_root in ("/tmp", tempfile.gettempdir()):
            with (
                self.subTest(temp_root=temp_root),
                tempfile.TemporaryDirectory(dir=temp_root) as tmp,
            ):
                root = Path(tmp)
                project = root / "dashboard"
                output = RENDERER.render_dashboard("seller", self.seller_payload(), project)
                self.assertEqual(output, project.resolve() / "index.html")
                self.assertTrue(output.is_file())

                redirected = root / "redirected"
                redirected.symlink_to(project, target_is_directory=True)
                original = output.read_bytes()
                with self.assertRaisesRegex(ValueError, "symbolic links"):
                    RENDERER.render_dashboard("seller", self.seller_payload(), redirected)
                self.assertEqual(output.read_bytes(), original)

    def test_rejects_dashboard_projects_inside_the_installed_sales_plugin(self) -> None:
        for persona, payload in (
            ("seller", self.seller_payload()),
            ("leadership", self.leadership_payload()),
        ):
            for project in (PLUGIN_DIRECTORY, PLUGIN_DIRECTORY / "generated-user-dashboards"):
                with self.subTest(persona=persona, project=project):
                    with self.assertRaises(ValueError):
                        RENDERER.render_dashboard(persona, payload, project)

    def test_cli_renders_both_personas_into_the_explicit_stable_project(self) -> None:
        for persona, payload in (
            ("seller", self.seller_payload()),
            ("leadership", self.leadership_payload()),
        ):
            with self.subTest(persona=persona):
                payload_path = self.project_root / f"{persona}-verified-payload.json"
                payload_path.write_text(json.dumps(payload), encoding="utf-8")
                project = self.project_root / f"user-owned-{persona}-project"

                result = run_command(
                    [
                        sys.executable,
                        str(RENDERER_PATH),
                        "--persona",
                        persona,
                        "--payload",
                        str(payload_path),
                        "--project-dir",
                        str(project),
                    ],
                    timeout=None,
                )

                self.assertEqual(result.returncode, 0, result.stderr)
                output = project / "index.html"
                self.assertTrue(output.is_file())
                self.assertEqual(result.stdout.strip(), str(output.resolve()))
                self.assertFalse((project / ".openai" / "hosting.json").exists())

    def test_cli_requires_matching_explicit_mode_for_placeholder_and_representative_views(
        self,
    ) -> None:
        for persona in ("seller", "leadership"):
            for mode in ("placeholder", "representative"):
                with self.subTest(persona=persona, mode=mode):
                    payload = (
                        self.placeholder_payload(persona)
                        if mode == "placeholder"
                        else self.representative_payload(persona)
                    )
                    payload_path = self.project_root / f"{mode}-{persona}.json"
                    payload_path.write_text(json.dumps(payload), encoding="utf-8")
                    project = self.project_root / f"cli-{mode}-{persona}"
                    base_command = [
                        sys.executable,
                        str(RENDERER_PATH),
                        "--persona",
                        persona,
                        "--payload",
                        str(payload_path),
                        "--project-dir",
                        str(project),
                    ]

                    missing_mode = run_command(base_command, timeout=None)
                    self.assertNotEqual(missing_mode.returncode, 0)
                    self.assertIn("must exactly match", missing_mode.stderr)
                    self.assertFalse(project.exists())

                    wrong_mode = "representative" if mode == "placeholder" else "placeholder"
                    mismatch = run_command([*base_command, "--mode", wrong_mode], timeout=None)
                    self.assertNotEqual(mismatch.returncode, 0)
                    self.assertIn("must exactly match", mismatch.stderr)
                    self.assertFalse(project.exists())

                    explicit = run_command([*base_command, "--mode", mode], timeout=None)
                    self.assertEqual(explicit.returncode, 0, explicit.stderr)
                    output = project / "index.html"
                    self.assertEqual(explicit.stdout.strip(), str(output.resolve()))
                    self.assertIn(
                        f'data-sales-dashboard-disclosure="{mode}"',
                        output.read_text(encoding="utf-8"),
                    )

    def test_cli_requires_explicit_project_directory(self) -> None:
        payload_path = self.project_root / "seller-payload.json"
        payload_path.write_text(json.dumps(self.seller_payload()), encoding="utf-8")

        result = run_command(
            [
                sys.executable,
                str(RENDERER_PATH),
                "--persona",
                "seller",
                "--payload",
                str(payload_path),
            ],
            timeout=None,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--project-dir", result.stderr)


class DashboardLifecycleInstructionsTests(SalesTestCase):
    def test_shared_lifecycle_requires_matching_site_local_first_and_explicit_hosting_consent(
        self,
    ) -> None:
        lifecycle = (PLUGIN_DIRECTORY / "references" / "dashboard-lifecycle.md").read_text(
            encoding="utf-8"
        )

        self.assert_contains(
            lifecycle,
            "current user-linked private Site",
            ".openai/hosting.json",
            "exactly one verified match",
            "owner, persona, and account/team scope",
            "another owner's Site",
            "ambiguous match",
            "ask the user",
            "creating a duplicate",
            "stable user-owned workspace project",
            "return the actual working local dashboard first",
            "offer to create a private Site",
            "overrides the Sites skills' normal auto-publish default",
            "unless the user explicitly agrees",
            "`sites-building` and `sites-hosting`",
            "preserves customized HTML during refresh",
            "never creates, publishes, or shares a Site",
        )

    def test_both_real_dashboard_skills_reuse_the_shared_local_first_lifecycle(self) -> None:
        for skill_name in ("seller-account-dashboard", "sales-leadership-dashboard"):
            with self.subTest(skill=skill_name):
                skill = (PLUGIN_DIRECTORY / "skills" / skill_name / "SKILL.md").read_text(
                    encoding="utf-8"
                )
                metadata = (
                    PLUGIN_DIRECTORY / "skills" / skill_name / "agents" / "openai.yaml"
                ).read_text(encoding="utf-8")

                self.assert_contains(
                    skill,
                    "[the shared Sales skill instructions](../../shared_skill_instructions.md)",
                    "[shared dashboard lifecycle](../../references/dashboard-lifecycle.md)",
                    "## Key Dependency Categories",
                )
                self.assertEqual(skill.count("[Blocking]"), 1)
                self.assertIn(".openai/hosting.json", skill)
                self.assertIn("ambiguous", skill.lower())
                self.assertIn("user customizations", skill)
                self.assertIn("local-first", skill)
                self.assertIn("explicitly agrees", skill)
                self.assertIn("render_real_dashboard.py", skill)
                self.assertIn("allow_implicit_invocation: false", metadata)


if __name__ == "__main__":
    unittest.main()
