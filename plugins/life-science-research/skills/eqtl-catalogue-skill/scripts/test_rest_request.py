import importlib.util
import unittest
from pathlib import Path
from unittest import mock

import requests

MODULE_PATH = Path(__file__).with_name("rest_request.py")
SPEC = importlib.util.spec_from_file_location("eqtl_catalogue_rest_request", MODULE_PATH)
rest_request = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(rest_request)


class _FakeResponse:
    def __init__(self, status_code: int, body: str, content_type: str = "application/json") -> None:
        self.status_code = status_code
        self.text = body
        self.headers = {"content-type": content_type}

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error", response=self)

    def json(self):
        import json

        return json.loads(self.text)


class _FakeSession:
    def __init__(self, response: _FakeResponse) -> None:
        self.headers = {}
        self._response = response

    def request(self, method: str, url: str, **kwargs):
        return self._response

    def close(self) -> None:
        return None


class RestRequestTests(unittest.TestCase):
    def test_parse_input_backfills_eqtl_association_defaults(self) -> None:
        payload = {
            "base_url": "https://www.ebi.ac.uk/eqtl/api",
            "path": "genes/ENSG00000141510/associations",
            "params": {"variant_id": "rs7903146", "size": 10},
        }

        parsed = rest_request.parse_input(payload)

        self.assertEqual(parsed["params"]["variant_id"], "rs7903146")
        self.assertEqual(parsed["params"]["snp"], "rs7903146")
        self.assertEqual(parsed["params"]["quant_method"], "ge")
        self.assertEqual(parsed["params"]["p_lower"], 0)
        self.assertEqual(parsed["params"]["p_upper"], 1)
        self.assertEqual(parsed["params"]["study"], "")
        self.assertEqual(parsed["params"]["tissue"], "")
        self.assertEqual(parsed["params"]["gene_id"], "")
        self.assertEqual(parsed["params"]["molecular_trait_id"], "")
        self.assertEqual(parsed["params"]["qtl_group"], "")

    def test_parse_input_does_not_backfill_other_services(self) -> None:
        payload = {
            "base_url": "https://www.ebi.ac.uk/gwas/rest/api/v2",
            "path": "associations",
            "params": {"mapped_gene": "BRCA1"},
        }

        parsed = rest_request.parse_input(payload)

        self.assertEqual(parsed["params"], {"mapped_gene": "BRCA1"})

    def test_execute_surfaces_http_error_body(self) -> None:
        payload = {
            "base_url": "https://www.ebi.ac.uk/eqtl/api",
            "path": "studies/BadStudy/associations",
            "params": {"size": 1},
        }
        response = _FakeResponse(400, '{"message":"upstream validation exploded"}')

        with mock.patch.object(
            rest_request.requests, "Session", return_value=_FakeSession(response)
        ):
            output = rest_request.execute(payload)

        self.assertFalse(output["ok"])
        self.assertEqual(output["error"]["code"], "http_error")
        self.assertIn("HTTP 400", output["error"]["message"])
        self.assertIn("upstream validation exploded", output["error"]["message"])


if __name__ == "__main__":
    unittest.main()
