---
name: ngs-bcl-to-fastq
description: Validate Illumina BCL run folders and sample sheets, plan demultiplexing, review index/UMI/lane choices, run BCL-to-FASTQ conversion, and interpret demux metrics while surfacing license/download boundaries.
---

# BCL To FASTQ

Use this skill when the input is an Illumina BCL run folder or the user asks to demultiplex a sequencing run. This is a deep demultiplexing and run-validation skill, not only a command wrapper.

## Essential Inputs

Confirm:

- run folder path with `RunInfo.xml`
- sample sheet path and format
- output directory
- instrument/run metadata from `RunInfo.xml` and `RunParameters.xml`
- lane handling: split by lane or combine lanes
- index mismatch tolerance
- index read structure and dual-index orientation
- UMI layout, if any
- whether adapter trimming/masking should happen during conversion
- whether undetermined reads and demultiplexing metrics should be reviewed before downstream analysis

## Public Tool Boundary

Prefer `bcl-convert` if it is already installed. It is free for local use but proprietary and RPM-distributed by Illumina, so do not auto-download without explicit user approval.

Legacy `bcl2fastq` may exist in older environments. Use it only when BCL Convert is unavailable or the run requires legacy compatibility.

## Preflight

```bash
python plugins/ngs-analysis/scripts/ngs_preflight.py --pipeline bcl_to_fastq --emit-install-plan
```

Also check run-folder structure:

```bash
test -f /path/to/run/RunInfo.xml
test -f /path/to/SampleSheet.csv
find /path/to/run -maxdepth 4 -type d -name BaseCalls
```

## Local Execution Package

Use the plugin-owned runner when the user provides a local run folder and sample sheet:

```bash
python plugins/ngs-analysis/scripts/run_bcl_to_fastq.py \
  --run-folder /path/to/run \
  --sample-sheet /path/to/SampleSheet.csv \
  --output-directory /path/to/fastq_out
```

Add `--execute` only when conversion is requested. The runner validates `RunInfo.xml`, optional `RunParameters.xml`, the BaseCalls directory, sample-sheet rows, duplicate lane/index combinations, and index length compatibility. With `--execute`, it uses installed `bcl-convert`, then legacy `bcl2fastq` if available; if neither exists, it records the blocker instead of downloading proprietary software.

## Validation Checklist

Before conversion, validate:

- `RunInfo.xml` exists and its read structure matches the expected sequencing design.
- `SampleSheet.csv` exists, is the intended version, and has no duplicate sample/index combinations within each lane.
- Index sequence lengths match the index reads and any trimming/masking requested by the sample sheet.
- Dual-index orientation is explicit for the instrument and library prep; do not infer i5 orientation from filenames.
- UMI bases are assigned to the intended read or index read and carried through to FASTQ headers or output metadata as needed.
- Lane-splitting, sample-name normalization, and output directory behavior are agreed before running.
- Disk space is sufficient for output FASTQs, reports, and temporary files.

## Kickoff Pattern

First produce a preflight plan with paths and sample sheet validation. Then run conversion only after the user confirms:

```bash
bcl-convert \
  --bcl-input-directory /path/to/run \
  --output-directory /path/to/fastq_out \
  --sample-sheet /path/to/SampleSheet.csv
```

## Metrics Review

After conversion, inspect and report:

- total clusters, clusters passing filter, and yield by lane
- percent assigned by sample and percent undetermined by lane
- top undetermined index sequences when available
- per-sample FASTQ counts and read-pair consistency
- unexpected index hopping, barcode collision, or sample-sheet mismatch signals

Record software version, command, sample sheet checksum, run-folder path, output path, and conversion metrics. Do not start downstream analysis until severe demultiplexing anomalies are surfaced.
