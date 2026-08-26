"""Regression coverage for review findings in the portable Sales demo launcher."""

from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

from sales_test_support import DEMO_RENDERER as RENDERER
from sales_test_support import SKILL_DIRECTORY, load_script, run_command

LAUNCHER_PATH = SKILL_DIRECTORY / "scripts/start_demo_fast.py"
LAUNCHER = load_script(LAUNCHER_PATH, "sales_demo_launch_contracts")


class DemoLaunchContractTests(unittest.TestCase):
    def test_custom_output_prints_its_escaped_artifact_route(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "seller #1.html"
            server = MagicMock()
            server.__enter__.return_value = server
            server.server_address = ("127.0.0.1", 8765)
            server.serve_forever.side_effect = KeyboardInterrupt
            stdout = io.StringIO()
            with (
                patch.object(
                    sys,
                    "argv",
                    ["renderer", "--dashboard", "account", "--output", str(output), "--serve"],
                ),
                patch.object(RENDERER, "create_dashboard_server", return_value=server),
                contextlib.redirect_stdout(stdout),
            ):
                RENDERER.main()
            self.assertTrue(output.is_file())
            urls = [line for line in stdout.getvalue().splitlines() if line.startswith("http:")]
            self.assertEqual(urls, ["http://127.0.0.1:8765/seller%20%231.html"])
            root = output.resolve().parent
            self.assertEqual(RENDERER.dashboard_route(root / "index.html", root), "/")
            self.assertEqual(
                RENDERER.dashboard_route(root / "leadership/index.html", root), "/leadership/"
            )

    def test_readiness_timeout_reaps_the_owned_child(self) -> None:
        for ignores_termination in (False, True):
            with self.subTest(ignores_termination=ignores_termination):
                process = MagicMock()
                process.poll.return_value = None
                if ignores_termination:
                    process.wait.side_effect = [subprocess.TimeoutExpired("preview", 1), 0]
                candidate = MagicMock()
                candidate.__enter__.return_value = candidate
                candidate.getsockname.return_value = ("127.0.0.1", 8765)
                with (
                    patch.object(LAUNCHER.socket, "socket", return_value=candidate),
                    patch.object(LAUNCHER.subprocess, "Popen", return_value=process) as popen,
                    patch.object(LAUNCHER.time, "monotonic", side_effect=[0, 4]),
                    self.assertRaisesRegex(RuntimeError, "three seconds"),
                ):
                    LAUNCHER.launch_preview(current_date=date(2026, 8, 17))
                process.terminate.assert_called_once_with()
                self.assertEqual(process.kill.call_count, int(ignores_termination))
                self.assertEqual(process.wait.call_count, 1 + int(ignores_termination))
                command = popen.call_args.args[0]
                self.assertEqual(command[-2:], ["--current-date", "2026-08-17"])

    def test_successful_preview_is_not_terminated(self) -> None:
        process = MagicMock()
        candidate = MagicMock()
        candidate.__enter__.return_value = candidate
        candidate.getsockname.return_value = ("127.0.0.1", 8765)
        with (
            patch.object(LAUNCHER.socket, "socket", return_value=candidate),
            patch.object(LAUNCHER.subprocess, "Popen", return_value=process),
            patch.object(LAUNCHER, "preview_is_ready", return_value=True),
            patch.object(LAUNCHER, "write_preview_cache"),
        ):
            self.assertEqual(LAUNCHER.launch_preview(), "http://127.0.0.1:8765")
        process.terminate.assert_not_called()
        process.wait.assert_not_called()

    def test_leadership_requires_the_complete_seller_portfolio(self) -> None:
        portfolio = RENDERER.load_portfolio()
        leadership = json.loads(RENDERER.DEFAULT_LEADERSHIP.read_text(encoding="utf-8"))
        missing = leadership["topDeals"].pop()["account"]
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "leadership.json"
            source.write_text(json.dumps(leadership), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "omit seller-portfolio accounts") as error:
                RENDERER.load_leadership_data(source, portfolio)
        self.assertIn(missing, str(error.exception))

    def test_distinct_custom_account_names_get_distinct_stable_ids(self) -> None:
        portfolio = RENDERER.load_portfolio()
        leadership = json.loads(RENDERER.DEFAULT_LEADERSHIP.read_text(encoding="utf-8"))
        replacements = {
            portfolio["workNow"][0]["account"]: "A B",
            portfolio["workNow"][1]["account"]: "A-B",
        }
        for group in RENDERER.EXPECTED_COUNTS:
            for account in portfolio[group]:
                account["account"] = replacements.get(account["account"], account["account"])
        for deal in leadership["topDeals"]:
            deal["account"] = replacements.get(deal["account"], deal["account"])
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "leadership.json"
            source.write_text(json.dumps(leadership), encoding="utf-8")
            overview = RENDERER.load_leadership_data(source, portfolio)["accountOverview"]
        ids = [account["id"] for account in overview]
        self.assertEqual(len(ids), len(set(ids)))
        by_name = {account["name"]: account["id"] for account in overview}
        self.assertNotEqual(by_name["A B"], by_name["A-B"])
        self.assertEqual(by_name["A B"], RENDERER._account_id("A B"))

    def test_user_timezone_and_explicit_date_override_the_host_clock(self) -> None:
        instant = datetime(2026, 8, 18, 0, 30, tzinfo=timezone.utc)
        clock = MagicMock()
        clock.now.side_effect = lambda zone=None: instant.astimezone(zone) if zone else instant
        with patch.object(RENDERER, "datetime", clock):
            self.assertEqual(
                RENDERER.resolve_demo_date(time_zone="America/Los_Angeles"), date(2026, 8, 17)
            )
            self.assertEqual(RENDERER.resolve_demo_date(time_zone="Asia/Tokyo"), date(2026, 8, 18))
            self.assertEqual(
                RENDERER.resolve_demo_date(date(2026, 8, 16), "Asia/Tokyo"), date(2026, 8, 16)
            )
        with self.assertRaisesRegex(ValueError, "Unknown IANA timezone"):
            RENDERER.resolve_demo_date(time_zone="Not/A_Timezone")

        result = run_command(
            [
                sys.executable,
                str(LAUNCHER_PATH),
                "--delivery-mode",
                "work",
                "--current-date",
                "2026-08-17",
            ],
            check=True,
        )
        self.assertIn("Mon, Aug 17", result.stdout)
        self.assertIn("Fri, Aug 14", result.stdout)
        self.assertNotIn("{{", result.stdout)

    def test_one_user_date_reaches_both_artifacts_and_the_detached_server(self) -> None:
        today = date(2026, 8, 17)
        with (
            patch.object(LAUNCHER.renderer, "render_dashboard") as seller,
            patch.object(LAUNCHER.renderer, "render_leadership_dashboard") as leadership,
            patch.object(LAUNCHER, "cached_preview_url", return_value=None),
            patch.object(LAUNCHER, "preview_is_ready", return_value=False),
            patch.object(
                LAUNCHER, "launch_preview", return_value="http://127.0.0.1:8765"
            ) as launch,
        ):
            LAUNCHER.ensure_preview(None, current_date=today)
        self.assertEqual(seller.call_args.kwargs["current_date"], today)
        self.assertEqual(leadership.call_args.kwargs["current_date"], today)
        launch.assert_called_once_with(current_date=today)


if __name__ == "__main__":
    unittest.main()
