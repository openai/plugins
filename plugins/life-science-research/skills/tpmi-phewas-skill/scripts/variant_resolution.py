from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

import requests

ENSEMBL_GRCH38 = "https://rest.ensembl.org"
ENSEMBL_GRCH37 = "https://grch37.rest.ensembl.org"

DEFAULT_TIMEOUT_S = 15
USER_AGENT = "variant-coordinate-finder/1.0 (+requests)"

SEP_RE = re.compile(r"[-:_/\s]+")
CHR_RE = re.compile(r"^(?:chr)?([0-9]{1,2}|X|Y|M|MT)$", re.IGNORECASE)
ALLELE_RE = re.compile(r"^[A-Za-z*]+$")


class VariantResolutionError(Exception):
    def __init__(self, code: str, message: str, warnings: list[str] | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.warnings = warnings or []


@dataclass
class Coord:
    chr: str
    pos: int
    ref: str | None
    alts: list[str]


def build_key_for(build: str) -> str:
    return "grch37" if build in {"GRCh37", "hg19"} else "grch38"


def build_variant_record(
    chrom: str,
    pos: int,
    ref: str | None,
    alt: str | None,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "chr": chrom,
        "pos": pos,
        "ref": ref,
        "alt": alt,
    }
    if ref is not None and alt is not None:
        record["canonical"] = f"{chrom}:{pos}-{ref}-{alt}"
    return record


def parse_variant_string(value: str) -> tuple[str, int, str, str]:
    raw = value.strip()
    if not raw:
        raise ValueError("Variant string is empty.")

    parts = [part for part in SEP_RE.split(raw) if part]
    if len(parts) != 4:
        raise ValueError(
            "Invalid variant format. Expected chrom-pos-ref-alt with flexible separators."
        )

    chrom_raw, pos_raw, ref_raw, alt_raw = parts
    match = CHR_RE.match(chrom_raw)
    if not match:
        raise ValueError(f"Invalid chromosome: {chrom_raw!r}")

    chrom = match.group(1).upper()
    if chrom == "M":
        chrom = "MT"

    try:
        pos = int(pos_raw)
    except ValueError as exc:
        raise ValueError(f"Invalid position: {pos_raw!r}") from exc
    if pos <= 0:
        raise ValueError("Position must be > 0.")

    ref = ref_raw.upper()
    alt = alt_raw.upper()
    if not ALLELE_RE.match(ref):
        raise ValueError(f"Invalid REF allele: {ref_raw!r}")
    if not ALLELE_RE.match(alt):
        raise ValueError(f"Invalid ALT allele: {alt_raw!r}")

    return chrom, pos, ref, alt


def extract_variant_input(payload: Any, *, default_build_key: str) -> tuple[str, str]:
    if isinstance(payload, str):
        return default_build_key, payload.strip()

    if not isinstance(payload, dict):
        raise ValueError("Input must be a JSON string or object.")

    provided: list[tuple[str, str]] = []
    for key in ("rsid", "grch37", "grch38", "variant"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            provided.append((key, value.strip()))

    if not provided:
        raise ValueError(
            f"Provide exactly one of `rsid`, `grch37`, `grch38`, or `{default_build_key}`."
        )
    if len(provided) != 1:
        raise ValueError(
            "Provide exactly one variant input: `rsid`, `grch37`, `grch38`, or `variant`."
        )

    input_type, input_value = provided[0]
    if input_type == "variant":
        input_type = default_build_key
    return input_type, input_value


def _server_for(build: str) -> str:
    return ENSEMBL_GRCH37 if build in {"GRCh37", "hg19"} else ENSEMBL_GRCH38


def _assembly_cmp(build: str) -> str:
    return "GRCh37" if build in {"GRCh37", "hg19"} else "GRCh38"


def _get_json(url: str, *, timeout: int = DEFAULT_TIMEOUT_S) -> Any:
    headers = {
        "Accept": "application/json",
        "User-Agent": USER_AGENT,
    }
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response.json()


def lookup_rsid(rsid: str, build: str = "GRCh38") -> Coord | None:
    server = _server_for(build)
    asm = _assembly_cmp(build)
    url = (
        f"{server}/variation/human/{requests.utils.quote(rsid, safe='')}"
        "?content-type=application/json"
    )

    data = _get_json(url, timeout=DEFAULT_TIMEOUT_S)
    mappings = data.get("mappings") if isinstance(data, dict) else None
    if not mappings:
        return None

    for mapping in mappings:
        if (
            isinstance(mapping, dict)
            and mapping.get("assembly_name") == asm
            and mapping.get("seq_region_name")
            and mapping.get("start") is not None
        ):
            allele_string = mapping.get("allele_string")
            alleles = allele_string.split("/") if isinstance(allele_string, str) else []
            ref = alleles[0] if alleles else None
            alts = alleles[1:] if len(alleles) > 1 else []
            return Coord(
                chr=str(mapping["seq_region_name"]),
                pos=int(mapping["start"]),
                ref=ref,
                alts=alts,
            )

    return None


def lookup_position(
    chrom: str,
    pos: int,
    build: str = "GRCh38",
) -> tuple[str, str | None, list[str]] | None:
    server = _server_for(build)
    url = (
        f"{server}/overlap/region/human/{chrom}:{pos}-{pos}"
        "?feature=variation;content-type=application/json"
    )

    data = _get_json(url, timeout=DEFAULT_TIMEOUT_S)
    if not isinstance(data, list) or not data:
        return None

    for variant in data:
        if (
            isinstance(variant, dict)
            and isinstance(variant.get("id"), str)
            and variant["id"].startswith("rs")
        ):
            alleles = variant.get("alleles") if isinstance(variant.get("alleles"), list) else []
            ref = alleles[0] if alleles else None
            alts = alleles[1:] if len(alleles) > 1 else []
            return variant["id"], ref, alts

    return None


def resolve_rsid_both_builds(rsid: str) -> dict[str, Any]:
    g38 = None
    g37 = None
    warnings: list[str] = []

    try:
        g38 = lookup_rsid(rsid, "GRCh38")
    except Exception as exc:  # noqa: BLE001
        warnings.append(f"GRCh38 lookup failed: {type(exc).__name__}: {exc}")

    try:
        g37 = lookup_rsid(rsid, "GRCh37")
    except Exception as exc:  # noqa: BLE001
        warnings.append(f"GRCh37 lookup failed: {type(exc).__name__}: {exc}")

    ref = (g38.ref if g38 else None) or (g37.ref if g37 else None)
    alts = (g38.alts if (g38 and g38.alts) else []) or (g37.alts if g37 else [])

    return {
        "rsid": rsid,
        "grch38": {"chr": g38.chr if g38 else None, "pos": g38.pos if g38 else None},
        "grch37": {"chr": g37.chr if g37 else None, "pos": g37.pos if g37 else None},
        "ref": ref,
        "alts": alts,
        "warnings": warnings,
    }


def resolve_position_both_builds(chrom: str, pos: int, build: str) -> dict[str, Any] | None:
    is_hg19 = build in {"hg19", "GRCh37"}
    other_build = "GRCh38" if is_hg19 else "GRCh37"

    pos_result = lookup_position(chrom, pos, build)
    if not pos_result:
        return None

    rsid, ref, alts = pos_result

    other = None
    warnings: list[str] = []
    try:
        other = lookup_rsid(rsid, other_build)
    except Exception as exc:  # noqa: BLE001
        warnings.append(f"Other-build lookup failed: {type(exc).__name__}: {exc}")

    if is_hg19:
        return {
            "rsid": rsid,
            "grch38": {"chr": other.chr if other else None, "pos": other.pos if other else None},
            "grch37": {"chr": chrom, "pos": pos},
            "ref": (other.ref if other and other.ref else ref),
            "alts": (other.alts if other and other.alts else alts),
            "warnings": warnings,
        }

    return {
        "rsid": rsid,
        "grch38": {"chr": chrom, "pos": pos},
        "grch37": {"chr": other.chr if other else None, "pos": other.pos if other else None},
        "ref": ref,
        "alts": alts,
        "warnings": warnings,
    }


def resolve_variant(input_type: str, input_value: str) -> dict[str, Any]:
    warnings: list[str] = []

    if input_type == "rsid":
        rsid = input_value.strip()
        if not rsid.startswith("rs"):
            raise ValueError("rsid must start with 'rs'.")

        resolved = resolve_rsid_both_builds(rsid)
        warnings.extend(resolved.get("warnings", []))

        ref = resolved.get("ref")
        alts = resolved.get("alts") or []
        alt = alts[0] if alts else None

        g37 = None
        if resolved.get("grch37", {}).get("chr") and resolved.get("grch37", {}).get("pos"):
            g37 = build_variant_record(
                resolved["grch37"]["chr"],
                resolved["grch37"]["pos"],
                ref,
                alt,
            )

        g38 = None
        if resolved.get("grch38", {}).get("chr") and resolved.get("grch38", {}).get("pos"):
            g38 = build_variant_record(
                resolved["grch38"]["chr"],
                resolved["grch38"]["pos"],
                ref,
                alt,
            )

        return {
            "input": {"type": "rsid", "value": rsid},
            "rsid": rsid,
            "grch37": g37,
            "grch38": g38,
            "warnings": warnings,
        }

    if input_type not in {"grch37", "grch38"}:
        raise ValueError(f"Unsupported input type: {input_type!r}")

    build = "GRCh37" if input_type == "grch37" else "GRCh38"
    chrom, pos, ref_in, alt_in = parse_variant_string(input_value)

    resolved = resolve_position_both_builds(chrom, pos, build)
    if not resolved:
        raise VariantResolutionError(
            "not_found",
            f"No rsID found at {chrom}:{pos} on {build} via Ensembl overlap endpoint.",
        )

    warnings.extend(resolved.get("warnings", []))

    ref = resolved.get("ref")
    alts = resolved.get("alts") or []
    if ref and ref_in != ref:
        warnings.append(f"Input ref {ref_in} != resolved ref {ref}; keeping resolved ref.")

    alt = alt_in if alt_in in alts else (alts[0] if alts else alt_in)
    if alts and alt_in not in alts:
        warnings.append(f"Input alt {alt_in} not among resolved alts {alts}; using {alt}.")

    rsid = resolved.get("rsid")

    g37 = None
    if resolved.get("grch37", {}).get("chr") and resolved.get("grch37", {}).get("pos"):
        g37 = build_variant_record(
            resolved["grch37"]["chr"],
            resolved["grch37"]["pos"],
            ref,
            alt,
        )

    g38 = None
    if resolved.get("grch38", {}).get("chr") and resolved.get("grch38", {}).get("pos"):
        g38 = build_variant_record(
            resolved["grch38"]["chr"],
            resolved["grch38"]["pos"],
            ref,
            alt,
        )

    return {
        "input": {"type": input_type, "value": input_value},
        "rsid": rsid,
        "grch37": g37,
        "grch38": g38,
        "warnings": warnings,
    }


def resolve_query_variant(
    *,
    input_type: str,
    input_value: str,
    target_build: str,
) -> dict[str, Any]:
    target_key = build_key_for(target_build)
    if input_type == target_key:
        chrom, pos, ref, alt = parse_variant_string(input_value)
        target_variant = build_variant_record(chrom, pos, ref, alt)
        return {
            "input": {"type": input_type, "value": input_value},
            "query_variant": target_variant,
            "rsid": None,
            "grch37": target_variant if target_key == "grch37" else None,
            "grch38": target_variant if target_key == "grch38" else None,
            "warnings": [],
        }

    resolved = resolve_variant(input_type, input_value)
    target_variant = resolved.get(target_key)
    if not isinstance(target_variant, dict) or not target_variant.get("canonical"):
        raise VariantResolutionError(
            "resolution_failed",
            f"Could not resolve input variant to {target_build}.",
            warnings=list(resolved.get("warnings") or []),
        )

    return {
        "input": resolved["input"],
        "query_variant": target_variant,
        "rsid": resolved.get("rsid"),
        "grch37": resolved.get("grch37"),
        "grch38": resolved.get("grch38"),
        "warnings": list(resolved.get("warnings") or []),
    }
