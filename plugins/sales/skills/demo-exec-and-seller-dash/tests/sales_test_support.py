"""Shared assertion and script-loading helpers for the portable Sales test suite."""

from __future__ import annotations

import importlib.util
import re
import subprocess
import unittest
from collections.abc import Sequence
from pathlib import Path
from types import ModuleType
from typing import Any

SKILL_DIRECTORY = Path(__file__).resolve().parent.parent


def load_script(path: Path, module_name: str | None = None) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name or path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load Sales script: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


DEMO_RENDERER = load_script(SKILL_DIRECTORY / "scripts" / "render_demo_dashboard.py")


def run_command(
    arguments: Sequence[str | Path],
    *,
    cwd: Path | None = None,
    check: bool = False,
    timeout: float | None = 10,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        arguments, cwd=cwd, capture_output=True, text=True, check=check, timeout=timeout
    )


class SalesTestCase(unittest.TestCase):
    def assert_contains(self, container: Any, *members: Any) -> None:
        for member in members:
            with self.subTest(contains=member):
                self.assertIn(member, container)

    def assert_excludes(self, container: Any, *members: Any) -> None:
        for member in members:
            with self.subTest(excludes=member):
                self.assertNotIn(member, container)

    def assert_matches(self, text: str, *patterns: str) -> None:
        for pattern in patterns:
            with self.subTest(matches=pattern):
                self.assertRegex(text, pattern)

    def assert_node_script(self, script: str, *arguments: Path | str, timeout: int = 10) -> None:
        result = run_command(
            ["node", "-e", script, *(str(argument) for argument in arguments)],
            timeout=timeout,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def assert_shared_accessible_account_drawer(self, template: str, *, detail_id: str) -> None:
        self.assertRegex(
            template,
            r'<div class="account-drawer account-drawer-overlay" id="account-drawer" '
            r'role="dialog" aria-modal="true" aria-labelledby="account-drawer-title" hidden>',
        )
        self.assertIn('class="account-drawer-panel"', template)
        self.assertIn('class="drawer-header drawer-toolbar"', template)
        self.assert_matches(
            template,
            (
                r'<button\b(?=[^>]*\bclass="drawer-close")'
                r'(?=[^>]*\bid="account-drawer-close")[^>]*>'
            ),
            (
                rf'<(?:article|aside|div)\b(?=[^>]*\bclass="[^\"]*\bdrawer-content\b[^\"]*")'
                rf'(?=[^>]*\bid="{re.escape(detail_id)}")[^>]*>'
            ),
            r'(?:\bid="account-drawer-title"|\.id\s*=\s*"account-drawer-title")',
        )
        self.assertIn("body.drawer-open { overflow: hidden; }", template)
        self.assertRegex(
            template,
            r"\.account-drawer-panel\s*\{[^}]*right:\s*0;[^}]*"
            r"width:\s*min\(100vw,\s*clamp\(420px,\s*54vw,\s*620px\)\);"
            r"[^}]*height:\s*100dvh;",
        )
        self.assertRegex(
            template,
            r"@media\s*\(max-width:\s*640px\)[\s\S]*?"
            r"\.account-drawer-panel\s*\{[^}]*width:\s*100vw;",
        )
        for function in ("openAccountDrawer", "closeAccountDrawer", "setupAccountDrawer"):
            with self.subTest(drawer_function=function):
                self.assertIn(f"function {function}(", template)
        self.assertIn('document.body.classList.add("drawer-open")', template)
        self.assertIn('document.body.classList.remove("drawer-open")', template)
        self.assertIn('if (event.key === "Escape")', template)
        self.assertIn("closeAccountDrawer()", template)
        self.assertIn("restoreFocus.focus()", template)
