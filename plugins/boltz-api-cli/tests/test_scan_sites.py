from __future__ import annotations

import importlib.util
import itertools
import sys
import types
import unittest
from pathlib import Path
from unittest import mock


def load_scan_sites() -> types.ModuleType:
    scripts_dir = (
        Path(__file__).resolve().parents[1]
        / "skills"
        / "boltz-protein-design"
        / "scripts"
    )
    script_path = scripts_dir / "scan_sites.py"
    common = types.ModuleType("_common")
    common.atom_coords = None
    common.indexed_residues = None
    dependencies = {
        "_common": common,
        "gemmi": types.ModuleType("gemmi"),
        "numpy": types.ModuleType("numpy"),
    }
    spec = importlib.util.spec_from_file_location("boltz_scan_sites", script_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    with mock.patch.dict(sys.modules, dependencies):
        spec.loader.exec_module(module)
    return module


scan_sites = load_scan_sites()


class Chain:
    def __init__(self, name: str) -> None:
        self.name = name


class ScanSitesTest(unittest.TestCase):
    def test_site_clustering_merges_transitive_bridges_in_any_order(self) -> None:
        footprints = [{1, 2}, {3, 4}, {2, 3}]
        for permutation in itertools.permutations(footprints):
            with self.subTest(permutation=permutation):
                self.assertEqual(
                    scan_sites.cluster_sites(permutation, 0.25), [[0, 1, 2]]
                )

    def test_explicit_binder_chain_excludes_other_target_chains(self) -> None:
        model = [Chain("A"), Chain("B"), Chain("C")]
        self.assertEqual(scan_sites._binder_chain_names(model, "A", ["B"]), {"B"})

    def test_single_non_target_chain_is_inferred(self) -> None:
        model = [Chain("A"), Chain("B")]
        self.assertEqual(scan_sites._binder_chain_names(model, "A"), {"B"})

    def test_ambiguous_binder_chains_fail_closed(self) -> None:
        model = [Chain("A"), Chain("B"), Chain("C")]
        with self.assertRaisesRegex(ValueError, "binder chains are ambiguous"):
            scan_sites._binder_chain_names(model, "A")

    def test_target_chain_cannot_be_selected_as_binder(self) -> None:
        model = [Chain("A"), Chain("B")]
        with self.assertRaisesRegex(ValueError, "cannot also be a binder"):
            scan_sites._binder_chain_names(model, "A", ["A"])

    def test_missing_binder_chain_is_rejected(self) -> None:
        model = [Chain("A"), Chain("B")]
        with self.assertRaisesRegex(ValueError, r"binder chain\(s\) C not found"):
            scan_sites._binder_chain_names(model, "A", ["C"])


if __name__ == "__main__":
    unittest.main()
