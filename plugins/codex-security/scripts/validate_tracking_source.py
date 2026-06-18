#!/usr/bin/env python3
"""Validate a sealed scan and list or select findings for tracking."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any


def _load_finalizer() -> ModuleType:
    script = Path(__file__).resolve().with_name("finalize_scan_contract.py")
    spec = importlib.util.spec_from_file_location("codex_security_scan_contract", script)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load scan contract validator: {script}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


FINALIZER = _load_finalizer()


def _select_findings(
    findings: list[dict[str, Any]],
    finding_id: str | None,
    fingerprint: str | None,
) -> list[dict[str, Any]]:
    if finding_id is not None:
        matches = [finding for finding in findings if finding["findingId"] == finding_id]
    elif fingerprint is not None:
        matches = [
            finding for finding in findings if finding["fingerprints"]["primary"] == fingerprint
        ]
    else:
        return findings

    if len(matches) != 1:
        raise ValueError("the selector did not resolve exactly one finding")
    return matches


def validate_source(
    scan_dir: Path,
    *,
    finding_id: str | None = None,
    fingerprint: str | None = None,
) -> list[dict[str, Any]]:
    if finding_id is not None and fingerprint is not None:
        raise ValueError("use only one of --finding-id or --fingerprint")

    scan_dir = scan_dir.expanduser().resolve(strict=True)
    schema_dir = Path(__file__).resolve().parents[1] / "schemas"
    manifest, _ = FINALIZER._read_scan_local_json_bytes(
        scan_dir,
        "scan-manifest.json",
        "scan-manifest.json",
    )
    FINALIZER._validate_manifest(manifest)
    FINALIZER.validate_against_schema(manifest, schema_dir / "scan-manifest.schema.json")

    scan = FINALIZER._require_dict(manifest, "scan", "manifest")
    findings_ref = scan["findingsRef"]
    findings_document, findings_bytes = FINALIZER._read_scan_local_json_bytes(
        scan_dir,
        findings_ref,
        findings_ref,
    )
    coverage_ref = scan["coverageRef"]
    coverage_document, coverage_bytes = FINALIZER._read_scan_local_json_bytes(
        scan_dir,
        coverage_ref,
        coverage_ref,
    )
    FINALIZER._validate_existing_seal(
        scan_dir,
        scan,
        artifact_contents={
            findings_ref: findings_bytes,
            coverage_ref: coverage_bytes,
        },
    )
    FINALIZER._validate_findings(manifest, findings_document)
    FINALIZER._enrich_findings(manifest, findings_document)
    FINALIZER._validate_coverage(manifest, coverage_document, scan_dir)
    FINALIZER._validate_sealed_coverage_receipts(scan, coverage_document)
    FINALIZER.validate_against_schema(
        findings_document,
        schema_dir / "findings.schema.json",
    )
    FINALIZER.validate_against_schema(
        coverage_document,
        schema_dir / "coverage.schema.json",
    )
    return _select_findings(
        findings_document["findings"],
        finding_id,
        fingerprint,
    )


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scan_dir", type=Path)
    selector = parser.add_mutually_exclusive_group()
    selector.add_argument("--finding-id")
    selector.add_argument("--fingerprint")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    try:
        findings = validate_source(
            args.scan_dir,
            finding_id=args.finding_id,
            fingerprint=args.fingerprint,
        )
    except (OSError, ValueError, RecursionError) as exc:
        print(f"tracking source preflight failed: {exc}", file=sys.stderr)
        return 2
    for finding in findings:
        print(finding["findingId"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
