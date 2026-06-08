import sys
import unittest
from pathlib import Path
from unittest import mock

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

try:
    import run_scrnaseq_post_count_qc as runner  # type: ignore
except ImportError:  # pragma: no cover
    runner = None

analysis_stack_ready = False
try:
    import anndata as ad  # type: ignore
    import scipy.sparse as sp  # type: ignore

    if runner is not None:
        analysis_stack_ready = bool(runner.load_analysis_modules().get("ok"))
except ImportError:  # pragma: no cover
    ad = None
    sp = None


@unittest.skipIf(runner is None, "runner unavailable")
class ScrnaPythonDependencyTests(unittest.TestCase):
    def test_python_dependency_status_reports_missing_module_without_importing_stack(self) -> None:
        def fake_find_spec(name: str) -> object | None:
            return None if name == "scanpy" else object()

        with mock.patch.object(runner.importlib.util, "find_spec", side_effect=fake_find_spec):
            status = runner.python_dependency_status()
        self.assertFalse(status["ok"])
        self.assertEqual(status["missing"], ["scanpy"])

    def test_r_dependency_status_fails_when_required_package_is_missing(self) -> None:
        probe = {"ok": True, "stdout_tail": "DropletUtils=TRUE;scDblFinder=FALSE;SoupX=TRUE"}
        with (
            mock.patch.object(runner, "command_path", return_value="/usr/bin/Rscript"),
            mock.patch.object(runner, "run_cmd", return_value=probe),
        ):
            status = runner.r_dependency_status(None)
        self.assertFalse(status["ok"])
        self.assertEqual(status["missing"], ["scDblFinder"])

    def test_combined_tool_preflight_status_preserves_failed_r_status(self) -> None:
        status = runner.combined_tool_preflight_status(
            {"ok": True, "python_modules": {}},
            {"ok": False, "missing": ["scDblFinder"]},
        )
        self.assertFalse(status["ok"])
        self.assertEqual(status["r_dependencies"]["missing"], ["scDblFinder"])


@unittest.skipIf(
    runner is None or ad is None or sp is None or not analysis_stack_ready,
    "scanpy/anndata stack unavailable",
)
class ScrnaPostCountRunnerTests(unittest.TestCase):
    def test_scdbfinder_readiness_flags_tiny_sparse_matrix(self) -> None:
        adata = ad.AnnData(X=sp.csr_matrix([[1], [0]]))
        adata.obs["total_counts"] = [1, 0]
        readiness = runner.scdbfinder_readiness(adata)
        self.assertFalse(readiness["ok"])
        self.assertEqual(readiness["reason"], "too_few_informative_cells")
        self.assertEqual(readiness["informative_cells"], 1)
        self.assertEqual(readiness["nonzero_entries"], 1)
