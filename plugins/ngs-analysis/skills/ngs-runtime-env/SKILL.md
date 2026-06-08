---
name: ngs-runtime-env
description: Check whether public NGS tools and packages already exist before downloading, installing, or running a sequencing pipeline.
---

# NGS Runtime Environment

Use this skill whenever an NGS workflow needs package checks, install planning, or runtime validation.

## Existence Check Order

1. Check executables on `PATH` with `command -v` or `shutil.which`.
2. Check Python imports for Python-backed tools.
3. Check active package managers with `conda list`, `mamba list`, `micromamba list`, or `pip show`.
4. If requested, check package indexes or container registries.
5. Emit an install plan before installing.
6. Install only when explicitly requested by the user.

Do not modify system Python. Prefer isolated conda/mamba environments or containers.

## Script

From the repo root:

```bash
python plugins/ngs-analysis/scripts/ngs_preflight.py --list
python plugins/ngs-analysis/scripts/ngs_preflight.py --tool fastqc --emit-install-plan
python plugins/ngs-analysis/scripts/ngs_preflight.py --profile local_light --emit-install-plan
python plugins/ngs-analysis/scripts/ngs_preflight.py --pipeline dna_variant_calling --network-checks --emit-install-plan
python plugins/ngs-analysis/scripts/ngs_preflight.py --pipeline shotgun_metagenomics --manager micromamba --install-plan-outdir runtime_readiness/shotgun_install
```

Use `--install-plan-outdir` when a user needs a reviewable permission handoff. It writes `install_plan.json` as the canonical machine-readable plan and `install_commands.sh` as a guarded shell companion generated from the same plan. The shell companion is review-only by default; it exits without installing unless `NGS_RUN_INSTALL_COMMANDS=1` is set after explicit user approval.

Check reference and database bundle readiness separately from executable readiness:

```bash
python plugins/ngs-analysis/scripts/ngs_reference_manager.py list
python plugins/ngs-analysis/scripts/ngs_reference_manager.py check --kind reference --bundle grch38_core --root /refs/GRCh38
python plugins/ngs-analysis/scripts/ngs_reference_manager.py explain-missing --kind database --bundle kraken2_standard --root /db/kraken2/standard
python plugins/ngs-analysis/scripts/ngs_reference_manager.py plan --pipeline shotgun_metagenomics --include-optional --outdir resource_readiness/shotgun
python plugins/ngs-analysis/scripts/ngs_reference_manager.py setup-plan --pipeline shotgun_metagenomics --include-optional --outdir resource_readiness/shotgun_setup
python plugins/ngs-analysis/scripts/ngs_reference_manager.py plan --pipeline atacseq --genome-build GRCh38 --bundle-root grch38_core=/refs/GRCh38 --outdir resource_readiness/atac
python plugins/ngs-analysis/scripts/ngs_reference_manager.py inventory --outdir resource_readiness/inventory
python plugins/ngs-analysis/scripts/ngs_reference_manager.py lock --outdir resource_readiness/lock --include-checksums
python plugins/ngs-analysis/scripts/ngs_reference_manager.py verify-lock --lockfile resource_readiness/lock/resource_lock.json --outdir resource_readiness/lock_verify --fail-on-mismatch
python plugins/ngs-analysis/scripts/ngs_reference_manager.py check-all --kind database --output resource_readiness/database_audit.json
```

Use `plan` before claiming that a reference- or database-heavy workflow is runnable. The plan output writes `resource_plan.json`, `resource_manifest.tsv`, `resource_env.sh`, `resource_readiness.md`, and setup-plan artifacts; missing required bundles are blocking, while optional bundles such as Bracken/HUMAnN or HOMER motif resources should stay explicit.

Use `setup-plan` when the user needs an actionable resource/database setup checklist without running an assay. It writes `resource_setup_plan.json`, `resource_setup_plan.tsv`, `resource_setup_plan.md`, and `resource_setup_commands.sh`. The shell skeleton keeps setup hints commented by default, so large reference/database downloads remain deliberate and reviewable.

Use `inventory` when the user needs a broader resource/database audit across the plugin. It writes `resource_inventory.json`, `resource_inventory.tsv`, `resource_env.sh`, and `resource_dashboard.md`, including missing files, env vars, setup hints, license notes, and pipeline usage for every known bundle.

Use `lock` after resources are ready for a project or handoff. It snapshots the resource inventory into `resource_lock.json`, `resource_lock.tsv`, and `resource_lock.md`; `verify-lock` compares the lockfile against current local paths and writes a drift report before reruns.

The nf-core adapter performs the same resource gate automatically unless `--skip-resource-plan` is supplied:

```bash
python plugins/ngs-analysis/scripts/run_nfcore_pipeline.py --pipeline taxprofiler --sample-sheet samples.csv --profile docker --bundle-root kraken2_standard=/db/kraken2/standard --include-optional-resources
```

The direct bulk RNA-seq counts/QC, scRNA FASTQ-to-count, generic DNA, germline DNA, somatic DNA, UMI panel, ATAC, ChIP/CUT&RUN, amplicon, and shotgun backend runners also emit run-local `resources/` readiness bundles. These direct runners use advisory resource checks by default so custom or reduced local inputs can still be planned; add `--require-resource-plan` when missing registered bundles should block readiness.

Use `--install-missing --yes` only after explicit user approval:

```bash
python plugins/ngs-analysis/scripts/ngs_preflight.py --pipeline fastq_qc --manager mamba --install-missing --yes
```

## Install Strategy

Prefer these patterns:

- nf-core workflows: install/check `nextflow`; use Docker/Singularity/Apptainer profiles for process tools.
- local execution: install/check `snakemake`; use `mamba` or `micromamba` environments and avoid containers by default.
- small QC tools: install with `mamba` or `micromamba` from `conda-forge` and `bioconda`.
- Python analysis packages: install in a dedicated environment, not global Python.
- large databases and references: estimate size and check existing paths before downloading.
- pipeline resource plans: use `--bundle-root bundle=/path` or the registry `root_env` variables so downstream runs can cite the exact local bundle roots.

## Report

Summarize:

- present tools and paths
- missing tools
- package-index checks, if performed
- suggested install commands
- tools that are proprietary, EULA-bound, cloud-bound, or database-heavy
