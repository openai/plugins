#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from unittest import mock

SCRIPT_PATH = Path(__file__).with_name("map_locus_to_gene.py")
SPEC = importlib.util.spec_from_file_location("map_locus_to_gene", SCRIPT_PATH)
assert SPEC and SPEC.loader
map_locus_to_gene = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(map_locus_to_gene)


def refsnp_payload() -> dict:
    return {
        "primary_snapshot_data": {
            "placements_with_allele": [
                {
                    "seq_id": "NC_000010.11",
                    "placement_annot": {
                        "seq_id_traits_by_assembly": [
                            {
                                "assembly_name": "GRCh38.p14",
                                "is_top_level": True,
                                "is_chromosome": True,
                                "is_alt": False,
                                "is_patch": False,
                            }
                        ]
                    },
                    "alleles": [
                        {
                            "allele": {
                                "spdi": {
                                    "position": 112998589,
                                    "deleted_sequence": "C",
                                    "inserted_sequence": "C",
                                }
                            }
                        },
                        {
                            "allele": {
                                "spdi": {
                                    "position": 112998589,
                                    "deleted_sequence": "C",
                                    "inserted_sequence": "G",
                                }
                            }
                        },
                        {
                            "allele": {
                                "spdi": {
                                    "position": 112998589,
                                    "deleted_sequence": "C",
                                    "inserted_sequence": "T",
                                }
                            }
                        },
                    ],
                },
                {
                    "seq_id": "NC_000010.10",
                    "placement_annot": {
                        "seq_id_traits_by_assembly": [
                            {
                                "assembly_name": "GRCh37.p13",
                                "is_top_level": True,
                                "is_chromosome": True,
                                "is_alt": False,
                                "is_patch": False,
                            }
                        ]
                    },
                    "alleles": [
                        {
                            "allele": {
                                "spdi": {
                                    "position": 114758348,
                                    "deleted_sequence": "C",
                                    "inserted_sequence": "C",
                                }
                            }
                        },
                        {
                            "allele": {
                                "spdi": {
                                    "position": 114758348,
                                    "deleted_sequence": "C",
                                    "inserted_sequence": "T",
                                }
                            }
                        },
                    ],
                },
            ],
            "allele_annotations": [
                {
                    "assembly_annotation": [
                        {
                            "seq_id": "NC_000010.11",
                            "genes": [
                                {
                                    "name": "transcription factor 7 like 2",
                                    "locus": "TCF7L2",
                                    "rnas": [
                                        {
                                            "sequence_ontology": [
                                                {"name": "intron_variant"},
                                            ]
                                        }
                                    ],
                                }
                            ],
                        }
                    ]
                }
            ],
        }
    }


class RefSnpResolutionTests(unittest.TestCase):
    def test_refsnp_base_uses_current_numeric_lookup_endpoint(self) -> None:
        self.assertEqual(
            map_locus_to_gene.REFSNP_BASE,
            "https://api.ncbi.nlm.nih.gov/variation/v0/refsnp",
        )

    def test_resolve_refsnp_coordinates_uses_top_level_grch_placements(self) -> None:
        with mock.patch.object(map_locus_to_gene, "safe_get_json", return_value=refsnp_payload()):
            coords = map_locus_to_gene.resolve_refsnp_coordinates("rs7903146", [], [])

        self.assertEqual(coords["grch38"]["chr"], "10")
        self.assertEqual(coords["grch38"]["pos"], 112998590)
        self.assertEqual(coords["grch38"]["ref"], "C")
        self.assertEqual(coords["grch38"]["alt"], "T")
        self.assertEqual(coords["grch37"]["pos"], 114758349)

    def test_fetch_refsnp_annotations_uses_gene_locus_symbols(self) -> None:
        with mock.patch.object(map_locus_to_gene, "safe_get_json", return_value=refsnp_payload()):
            annotations = map_locus_to_gene.fetch_refsnp_annotations(["rs7903146"], [])

        self.assertEqual(annotations["rs7903146"]["genes"], ["TCF7L2"])
        self.assertIn("intron_variant", annotations["rs7903146"]["consequence_terms"])


if __name__ == "__main__":
    unittest.main()
