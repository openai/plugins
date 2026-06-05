---
name: ngs-analysis-router
description: Route BCL, FASTQ, BAM/CRAM, count-matrix, or VCF sequencing requests to the right public NGS analysis skill and ask only the missing assay-specific setup questions.
---

# Life Sciences NGS Analysis Router

Use this skill as the top-level entrypoint for ambiguous or broad sequencing-analysis requests.

## Start Here

Inspect the available inputs before asking the user questions. Look for:

- Illumina run-folder files: `RunInfo.xml`, `RunParameters.xml`, `SampleSheet.csv`, `Data/Intensities/BaseCalls`
- FASTQs: `*.fastq`, `*.fq`, `*.fastq.gz`, `*.fq.gz`
- BAM/CRAM/VCF: `*.bam`, `*.cram`, `*.vcf`, `*.vcf.gz`
- count matrices: `matrix.mtx`, `features.tsv`, `barcodes.tsv`, `*.h5`, `*.h5ad`, `*.rds`
- metadata: sample sheets, design files, target BEDs, reference FASTA/GTF, primer files

Read `references/intake-schema.json` and `references/pipeline-registry.json` when forming the route.

## Intake Rules

Ask the smallest set of missing questions needed to choose a defensible pipeline. Do not ask the full questionnaire if file inspection already answers a field.

Always resolve:

- input type
- assay type
- desired output
- organism/reference
- paired-end vs single-end when FASTQs are involved
- any assay-specific design file or metadata required for the requested result
- runtime constraints: local/HPC/cloud, container availability, and whether installs are allowed

For human data, ask whether cloud upload is allowed before suggesting BaseSpace, Terra, DNAnexus, or any cloud path.

## Routing

Route to one leaf skill:

- BCL run folder or demultiplexing: `ngs-bcl-to-fastq`
- QC/trimming only: `ngs-fastq-qc`
- WGS/WES/panel variants: `ngs-dna-variant-calling`, then a subtype skill when the analysis model is clear
- germline WGS/WES/panel variants: `ngs-dna-germline-variants`
- tumor-normal or tumor-only somatic variants: `ngs-dna-somatic-variants`
- UMI, duplex, or low-frequency targeted panels: `ngs-dna-umi-panel-variants`
- bulk RNA-seq kickoff: `ngs-bulk-rnaseq`
- bulk RNA-seq FASTQ-to-count QC: `ngs-bulk-rnaseq-counts-qc`
- bulk RNA-seq differential expression from counts: `ngs-bulk-rnaseq-differential-expression`
- single-cell or single-nucleus FASTQ-to-matrix kickoff: `ngs-scrna-seq`
- single-cell or single-nucleus post-count QC/annotation/UMAP: `scrna-seq-qc`
- epigenomics kickoff: `ngs-epigenomics-peaks`
- ATAC-seq QC/peaks/accessibility: `ngs-atacseq-peaks-qc`
- ChIP-seq, CUT&RUN, or CUT&Tag QC/peaks: `ngs-chip-cutrun-peaks-qc`
- 16S/18S/ITS/COI amplicons: `ngs-amplicon-microbiome`
- shotgun metagenomics: `ngs-shotgun-metagenomics`
- runtime/package setup only: `ngs-runtime-env`

Prefer public, runtime-installable packages and nf-core workflows. Surface license/EULA/account boundaries before using proprietary or cloud tools.

## Preflight

Before proposing installation or execution, run a preflight plan from the repo root:

```bash
python plugins/ngs-analysis/scripts/ngs_preflight.py --pipeline <pipeline_key> --emit-install-plan
```

When the user needs an approval-ready install handoff, write persistent install artifacts:

```bash
python plugins/ngs-analysis/scripts/ngs_preflight.py --pipeline <pipeline_key> --manager micromamba --install-plan-outdir runtime_readiness/<pipeline_key>_install
```

Treat `install_plan.json` as the canonical review artifact. `install_commands.sh` is generated from the same plan and stays review-only unless the user explicitly approves execution with `NGS_RUN_INSTALL_COMMANDS=1`.

For reference- or database-heavy pipelines, also create a resource plan before saying the workflow is runnable:

```bash
python plugins/ngs-analysis/scripts/ngs_reference_manager.py plan --pipeline <pipeline_key> --genome-build <build> --outdir resource_readiness/<pipeline_key>
```

Use `--include-optional` for shotgun, amplicon, or motif-enabled epigenomics runs when optional databases materially affect the requested output.

Use `--network-checks` only when the user allows network checks. Use `--install-missing --yes` only when the user explicitly asks to install.

## Output Contract

Return:

1. the routed analysis type and confidence
2. missing essential parameters, if any
3. recommended public pipeline or package family
4. local tool preflight summary
5. preflight-first command or next concrete action
6. caveats around licenses, cloud upload, database size, and reference data
