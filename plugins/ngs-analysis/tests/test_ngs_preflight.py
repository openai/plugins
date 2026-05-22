import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import ngs_preflight  # noqa: E402


class InstallPlanArtifactTests(unittest.TestCase):
    def test_bioconda_install_command_is_noninteractive(self) -> None:
        cmd = ngs_preflight.install_command(
            "fastqc",
            {"install": {"conda": "bioconda::fastqc"}},
            "micromamba",
        )
        self.assertEqual(
            cmd, ["micromamba", "install", "-y", "-c", "conda-forge", "-c", "bioconda", "fastqc"]
        )

    def test_install_plan_writes_json_and_guarded_shell_script(self) -> None:
        args = SimpleNamespace(
            tool=None,
            pipeline="shotgun_metagenomics",
            profile=None,
            manager="micromamba",
            network_checks=False,
        )
        registry = {
            "tools": {
                "kraken2": {
                    "executables": ["kraken2"],
                    "install": {"conda": "bioconda::kraken2"},
                    "notes": "Database setup is separate.",
                    "license": "public_or_open",
                }
            }
        }
        entries = ngs_preflight.install_plan_entries(["kraken2"], registry, "micromamba")
        plan = ngs_preflight.build_install_artifact(
            args=args,
            statuses=[
                {
                    "tool": "kraken2",
                    "executables": [{"name": "kraken2", "present": False, "path": None}],
                }
            ],
            missing=["kraken2"],
            runtime_missing=[],
            blocking_missing=["kraken2"],
            plan_entries=entries,
        )
        with tempfile.TemporaryDirectory() as tmp:
            outputs = ngs_preflight.write_install_artifacts(plan, Path(tmp))
            plan_path = Path(outputs["install_plan_json"])
            commands_path = Path(outputs["install_commands_sh"])
            self.assertTrue(plan_path.exists())
            self.assertTrue(commands_path.exists())
            loaded = json.loads(plan_path.read_text(encoding="utf-8"))
            self.assertEqual(
                loaded["permission_model"]["install_script_default_mode"], "review_only"
            )
            self.assertEqual(loaded["install_plan"][0]["tool"], "kraken2")
            script = commands_path.read_text(encoding="utf-8")
            self.assertIn("NGS_RUN_INSTALL_COMMANDS=1", script)
            self.assertIn("Review-only mode", script)
            self.assertIn(
                "run_cmd micromamba install -y -c conda-forge -c bioconda kraken2", script
            )


if __name__ == "__main__":
    unittest.main()
