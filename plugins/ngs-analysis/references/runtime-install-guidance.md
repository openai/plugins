# Runtime Install And Existence Checks

Use this guidance before downloading or installing anything.

## Default Policy

1. Check whether the executable already exists on `PATH`.
2. Check whether a Python module can be imported when the tool is Python-backed.
3. Check the active environment with `conda list`, `mamba list`, `micromamba list`, or `pip show` when available.
4. If the tool is missing, emit an install plan first.
5. Only query package indexes or container registries when network checks are allowed.
6. Only install when the user explicitly asked for installation or execution that requires installation.

Avoid modifying system Python. Prefer an isolated conda/mamba/micromamba environment, a Nextflow container profile, Docker, Singularity, or Apptainer.

## Package Existence Checks

Local checks:

```bash
command -v fastqc
command -v nextflow
command -v snakemake
python -c "import scanpy"
python -m pip show multiqc
conda list fastqc
```

Network checks:

```bash
conda search -c bioconda fastqc
python -m pip index versions multiqc
docker manifest inspect google/deepvariant:latest
nextflow info nf-core/rnaseq
```

Network checks can be slow and may hit rate limits, so they should be explicit.

## Install Planning

Prefer one of these patterns:

```bash
mamba create -n ngs-qc -c conda-forge -c bioconda fastqc multiqc fastp cutadapt seqkit
mamba create -n ngs-nextflow -c conda-forge -c bioconda nextflow
mamba create -n ngs-local -c conda-forge -c bioconda snakemake fastqc multiqc fastp seqkit salmon samtools bcftools
python -m pip install --user multiqc
```

For nf-core workflows, prefer containerized execution:

```bash
nextflow run nf-core/rnaseq -profile test,docker --outdir results/rnaseq_test
```

When Docker, registry egress, or Nextflow process containers are unstable, use the local execution profile instead of forcing a full nf-core run:

```bash
python plugins/ngs-analysis/scripts/ngs_preflight.py --profile local_light --emit-install-plan
```

For approval handoff, persist the executable/package plan:

```bash
python plugins/ngs-analysis/scripts/ngs_preflight.py --pipeline shotgun_metagenomics --manager micromamba --install-plan-outdir runtime_readiness/shotgun_install
```

`install_plan.json` is the canonical artifact for Codex/user review. `install_commands.sh` is generated from that JSON and is guarded: by default it prints the plan path and exits without installing. Execute it only after explicit user approval by setting `NGS_RUN_INSTALL_COMMANDS=1`.

Then use a plugin-owned runner when the selected lane has one, such as `run_fastq_qc.py` or `run_scrnaseq_fastq_to_count.py`. For lanes that do not yet have dedicated runners, prepare an assay-specific workflow envelope before execution.

The local execution profile is meant for compact, auditable runs. When a site has a validated nf-core, WDL/Cromwell, or lab pipeline, preserve that pipeline's parameters and acceptance criteria.

For large reference databases, do not auto-download. First estimate size, target path, and whether the database already exists.

## Proprietary Or Credentialed Boundaries

Public package routing does not mean every useful tool is open-source or credential-free.

- Illumina BCL Convert: public/free local installer, proprietary, RPM-based.
- 10x Cell Ranger: public download with EULA; use only when the user has accepted the license or explicitly requests it.
- DRAGEN and Sentieon: commercial/licensed tools.
- BaseSpace, Terra, DNAnexus: account, permission, billing, and cloud-upload constraints.
- COSMIC, HGMD Professional, controlled human data repositories: licensing or authorization may be required.
