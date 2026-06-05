#!/usr/bin/env python3
"""Aggregate Salmon quant.sf files into transcript- and gene-level matrices."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def parse_gtf_attributes(raw: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for chunk in raw.strip().split(";"):
        part = chunk.strip()
        if not part or " " not in part:
            continue
        key, value = part.split(" ", 1)
        values[key] = value.strip().strip('"')
    return values


def tx2gene_from_gtf(path: Path | None) -> dict[str, dict[str, str]]:
    if not path or not path.exists():
        return {}
    mapping: dict[str, dict[str, str]] = {}
    with path.open("rt", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line or line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 9 or fields[2] != "transcript":
                continue
            attrs = parse_gtf_attributes(fields[8])
            transcript_id = attrs.get("transcript_id")
            gene_id = attrs.get("gene_id")
            if not transcript_id or not gene_id:
                continue
            mapping[transcript_id] = {
                "gene_id": gene_id,
                "gene_name": attrs.get("gene_name", gene_id),
            }
    return mapping


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--quant", action="append", default=[], help="sample=/path/to/quant.sf")
    return parser.parse_args()


def read_quant_sf(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return {row["Name"]: row for row in reader}


def write_matrix(path: Path, header: list[str], rows: list[list[str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(header)
        writer.writerows(rows)


def main() -> int:
    args = parse_args()
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    sample_to_quant: dict[str, Path] = {}
    for item in args.quant:
        sample, raw_path = item.split("=", 1)
        sample_to_quant[sample] = Path(raw_path)

    sample_names = sorted(sample_to_quant)
    per_sample = {sample: read_quant_sf(path) for sample, path in sample_to_quant.items()}
    transcript_ids = sorted({tx for table in per_sample.values() for tx in table})
    gtf_path = (
        Path(config["references"]["annotation_gtf"])
        if config.get("references", {}).get("annotation_gtf")
        else None
    )
    tx2gene = tx2gene_from_gtf(gtf_path)

    tpm_rows: list[list[str]] = []
    num_reads_rows: list[list[str]] = []
    effective_length_rows: list[list[str]] = []
    for transcript_id in transcript_ids:
        tpm_row = [transcript_id]
        num_reads_row = [transcript_id]
        effective_length_row = [transcript_id]
        for sample in sample_names:
            record = per_sample[sample].get(transcript_id)
            tpm_row.append(record["TPM"] if record else "")
            num_reads_row.append(record["NumReads"] if record else "")
            effective_length_row.append(record["EffectiveLength"] if record else "")
        tpm_rows.append(tpm_row)
        num_reads_rows.append(num_reads_row)
        effective_length_rows.append(effective_length_row)

    write_matrix(outdir / "tpm.tsv", ["transcript_id", *sample_names], tpm_rows)
    write_matrix(outdir / "num_reads.tsv", ["transcript_id", *sample_names], num_reads_rows)
    write_matrix(
        outdir / "effective_length.tsv", ["transcript_id", *sample_names], effective_length_rows
    )

    tx2gene_rows: list[list[str]] = []
    gene_num_reads: dict[str, list[float]] = {}
    gene_tpm: dict[str, list[float]] = {}
    for transcript_id in transcript_ids:
        gene_record = tx2gene.get(transcript_id)
        gene_id = gene_record["gene_id"] if gene_record else transcript_id
        gene_name = gene_record["gene_name"] if gene_record else transcript_id
        tx2gene_rows.append([transcript_id, gene_id, gene_name])
        gene_num_reads.setdefault(gene_id, [0.0] * len(sample_names))
        gene_tpm.setdefault(gene_id, [0.0] * len(sample_names))
        for idx, sample in enumerate(sample_names):
            record = per_sample[sample].get(transcript_id)
            if not record:
                continue
            gene_num_reads[gene_id][idx] += float(record["NumReads"])
            gene_tpm[gene_id][idx] += float(record["TPM"])

    write_matrix(outdir / "tx2gene.tsv", ["transcript_id", "gene_id", "gene_name"], tx2gene_rows)
    write_matrix(
        outdir / "gene_num_reads.tsv",
        ["gene_id", *sample_names],
        [
            [gene_id, *[f"{value:.6f}" for value in gene_num_reads[gene_id]]]
            for gene_id in sorted(gene_num_reads)
        ],
    )
    write_matrix(
        outdir / "gene_tpm.tsv",
        ["gene_id", *sample_names],
        [
            [gene_id, *[f"{value:.6f}" for value in gene_tpm[gene_id]]]
            for gene_id in sorted(gene_tpm)
        ],
    )

    sample_rows = []
    for sample in sample_names:
        info = config["rnaseq_salmon_samples"][sample]
        sample_rows.append(
            [
                sample,
                info["layout"],
                info["strandedness"],
                info.get("salmon_libtype", ""),
                info.get("salmon_libtype_source", ""),
                ",".join(str(index) for index in info["row_indices"]),
                str(len(info["r1"])),
                str(len(info.get("r2", []))),
            ]
        )
    write_matrix(
        outdir / "samples.tsv",
        [
            "sample",
            "layout",
            "strandedness",
            "salmon_libtype",
            "salmon_libtype_source",
            "technical_replicate_rows",
            "fastq_1_files",
            "fastq_2_files",
        ],
        sample_rows,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
