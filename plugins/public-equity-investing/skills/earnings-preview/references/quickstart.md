# Earnings Preview Pack Quickstart

The deterministic sample run builds a pre-earnings preview note, model-driver tables, QA outputs, and a run manifest.

From the skill root after installing dependencies, copy the bundled sample plan to a temporary workspace and run from there. This keeps examples from dirtying the packaged skill folder.

```bash
TMPDIR="$(mktemp -d)"
cp assets/sample_run/plan.json "$TMPDIR/plan.json"
python scripts/validate_plan.py "$TMPDIR/plan.json"
python scripts/run_plan.py "$TMPDIR/plan.json"
```

Outputs land in `/tmp/public_equity_investing_earnings_preview_sample_output/ACME/FY2026Q1/` unless you edit `output_dir` in the copied plan.
