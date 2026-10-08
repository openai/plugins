from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = PLUGIN_ROOT / "scripts" / "validate_source_presentation.py"
REGISTRY_PATH = PLUGIN_ROOT / "references" / "source-links.json"
CONTRACT_PATH = PLUGIN_ROOT / "references" / "source-presentation.md"
SKILLS_DIR = PLUGIN_ROOT / "skills"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class SourcePresentationTests(unittest.TestCase):
    def test_full_contract_validation(self) -> None:
        validator = _load_module("source_presentation_validator", VALIDATOR_PATH)
        self.assertEqual([], validator.validate())

    def test_contract_defines_conditional_output_modes(self) -> None:
        contract = CONTRACT_PATH.read_text(encoding="utf-8")
        normalized_contract = " ".join(contract.split())
        for output_mode in (
            "Record or evidence lookup",
            "Search or result list",
            "Connectivity or schema check",
            "Source metadata or service status",
            "Empty result or failed request",
            "Router or planner",
            "Local synthesis or derived analysis",
            "Raw machine-readable output",
        ):
            self.assertIn(output_mode, contract)
        self.assertIn(
            "every substantive externally sourced claim should remain traceable",
            normalized_contract,
        )
        self.assertIn(
            "not every skill invocation needs a clickable evidence link",
            normalized_contract,
        )

    def test_all_skill_headers_use_v2_conditional_contract(self) -> None:
        skill_paths = sorted(SKILLS_DIR.glob("*/SKILL.md"))
        self.assertEqual(50, len(skill_paths))
        for skill_path in skill_paths:
            text = skill_path.read_text(encoding="utf-8")
            self.assertIn("<!-- source-presentation-contract:v2 -->", text)
            self.assertIn(
                "only for substantive external claims supported by the response",
                text,
            )
            self.assertIn(
                "Do not force evidence links for connectivity or schema checks",
                text,
            )
            self.assertNotIn("<!-- source-presentation-contract:v1 -->", text)

    def test_router_and_mapper_handle_non_evidence_sources_explicitly(self) -> None:
        router = (SKILLS_DIR / "research-router-skill" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Do not seed the router with example citations", router)
        self.assertIn("returns no evidence, or fails", router)
        self.assertNotIn("UniProt P01116", router)
        self.assertNotIn("R-HSA-6802949", router)

        mapper = (SKILLS_DIR / "locus-to-gene-mapper-skill" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Distinguish evidence-contributing sources", mapper)
        self.assertIn("queried sources that returned no", mapper)
        self.assertIn("queried-but-empty sources", mapper)

    def test_representative_canonical_links(self) -> None:
        registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))["skills"]
        cases = {
            ("uniprot-skill", "UniProtKB accession"): (
                "P01116",
                "https://www.uniprot.org/uniprotkb/P01116/entry",
            ),
            ("reactome-skill", "Reactome stable ID"): (
                "R-HSA-6802949",
                "https://reactome.org/content/detail/R-HSA-6802949",
            ),
            ("clinicaltrials-skill", "NCT ID"): (
                "NCT01234567",
                "https://clinicaltrials.gov/study/NCT01234567",
            ),
            ("rcsb-pdb-skill", "PDB ID"): (
                "4OBE",
                "https://www.rcsb.org/structure/4OBE",
            ),
            ("clinvar-variation-skill", "numeric ClinVar Variation ID"): (
                "13080",
                "https://www.ncbi.nlm.nih.gov/clinvar/variation/13080/",
            ),
            ("pride-skill", "PRIDE project accession"): (
                "PXD000001",
                "https://www.ebi.ac.uk/pride/archive/projects/PXD000001",
            ),
            ("ncbi-entrez-skill", "PMID"): (
                "12345678",
                "https://pubmed.ncbi.nlm.nih.gov/12345678/",
            ),
        }
        for (skill_name, identifier_type), (identifier, expected) in cases.items():
            templates = registry[skill_name]["record_url_templates"]
            template = next(
                item["template"]
                for item in templates
                if item["identifier_type"] == identifier_type
            )
            self.assertEqual(expected, template.format(id=identifier))

    def test_generic_client_redacts_secret_query_values(self) -> None:
        client_path = (
            PLUGIN_ROOT / "skills" / "uniprot-skill" / "scripts" / "rest_request.py"
        )
        client = _load_module("uniprot_rest_request", client_path)
        sanitized = client._sanitize_request_url(  # noqa: SLF001
            "https://alice:password@example.org/record?"
            "id=P01116&api_key=secret&token=hidden&sig=signed&code=oauth"
            "#access_token=fragment-secret"
        )
        self.assertTrue(sanitized.startswith("https://example.org/record?"))
        self.assertIn("id=P01116", sanitized)
        self.assertNotIn("alice", sanitized)
        self.assertNotIn("password", sanitized)
        self.assertNotIn("secret", sanitized)
        self.assertNotIn("hidden", sanitized)
        self.assertNotIn("signed", sanitized)
        self.assertNotIn("oauth", sanitized)
        self.assertNotIn("#", sanitized)
        self.assertEqual(4, sanitized.count("REDACTED"))

    def test_generic_clients_use_registry_display_names(self) -> None:
        registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))["skills"]
        client_paths = sorted(SKILLS_DIR.glob("*/scripts/rest_request.py"))
        self.assertEqual(31, len(client_paths))

        for index, client_path in enumerate(client_paths):
            skill_name = client_path.parents[1].name
            client = _load_module(f"generic_source_client_{index}", client_path)
            self.assertEqual(
                registry[skill_name]["source_name"],
                client.SOURCE_NAME,
            )

    def test_gtex_source_url_reproduces_the_variant_query(self) -> None:
        script_dir = PLUGIN_ROOT / "skills" / "gtex-eqtl-skill" / "scripts"
        sys.path.insert(0, str(script_dir))
        try:
            client = _load_module(
                "gtex_eqtl_source_client", script_dir / "gtex_eqtl.py"
            )
        finally:
            sys.path.remove(str(script_dir))

        self.assertEqual(
            client.build_request_url("chr10_112998590_C_T_b38"),
            "https://gtexportal.org/api/v2/association/singleTissueEqtl?"
            "variantId=chr10_112998590_C_T_b38",
        )

    def test_clinicaltrials_summary_keeps_record_link_fields(self) -> None:
        client_path = (
            PLUGIN_ROOT
            / "skills"
            / "clinicaltrials-skill"
            / "scripts"
            / "clinicaltrials_client.py"
        )
        client = _load_module("clinicaltrials_source_client", client_path)
        summary = client._compact_study(  # noqa: SLF001
            {
                "protocolSection": {
                    "identificationModule": {
                        "nctId": "NCT01234567",
                        "briefTitle": "Representative study",
                        "officialTitle": "Representative official study title",
                    },
                    "statusModule": {"overallStatus": "RECRUITING"},
                    "designModule": {"studyType": "INTERVENTIONAL"},
                },
                "hasResults": False,
            }
        )

        self.assertEqual(summary["nctId"], "NCT01234567")
        self.assertEqual(summary["briefTitle"], "Representative study")
        self.assertEqual(summary["overallStatus"], "RECRUITING")

    def test_provenance_helper_leaves_errors_unchanged(self) -> None:
        client_path = (
            PLUGIN_ROOT / "skills" / "civic-skill" / "scripts" / "civic_graphql.py"
        )
        client = _load_module("civic_graphql_client", client_path)
        payload = {"ok": False, "error": {"code": "example", "message": "failed"}}
        self.assertIs(
            payload, client._attach_sources(payload, "CIViC", "https://civicdb.org/")
        )
        self.assertNotIn("sources", payload)

    def test_provenance_helper_adds_authoritative_source_url(self) -> None:
        client_path = (
            PLUGIN_ROOT / "skills" / "civic-skill" / "scripts" / "civic_graphql.py"
        )
        client = _load_module("civic_graphql_success_client", client_path)
        payload = {"ok": True, "summary": {"variant": "KRAS G12C"}}
        output = client._attach_sources(payload, "CIViC", "https://civicdb.org/")
        self.assertEqual("CIViC", output["sources"][0]["name"])
        self.assertEqual("https://civicdb.org/", output["sources"][0]["url"])
        self.assertNotIn("request_url", output["sources"][0])


if __name__ == "__main__":
    unittest.main()
