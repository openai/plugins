import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
RENDER_PATH = SCRIPT_DIR / "render.py"


def load_render_module():
    spec = importlib.util.spec_from_file_location("morningstar_render", RENDER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RenderReportTests(unittest.TestCase):
    def test_render_report_writes_html(self):
        render = load_render_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "report.html"
            result_path = render.render_report(
                {
                    "FUND_NAME": "Test Growth Fund",
                    "TICKER": "TEST",
                    "STAR_RATING": 4,
                },
                output_path,
            )

            html = result_path.read_text(encoding="utf-8")
            self.assertIn("Test Growth Fund", html)
            self.assertIn("TEST", html)
            self.assertIn('class="export-toolbar"', html)
            self.assertIn(str(RENDER_PATH.parent / "export_report.py"), html)
            self.assertIn(str(result_path), html)

    def test_list_placeholders_does_not_require_data_file(self):
        completed = subprocess.run(
            [sys.executable, str(RENDER_PATH), "--list-placeholders"],
            capture_output=True,
            check=False,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Available placeholders", completed.stdout)

    def test_export_helper_has_cli_help(self):
        completed = subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "export_report.py"), "--help"],
            capture_output=True,
            check=False,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("--format", completed.stdout)


if __name__ == "__main__":
    unittest.main()
