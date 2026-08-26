# Deterministic Script Quickstart

These scripts support deterministic parts of the earnings deep-dive workflow: validation, beat/miss and guidance math, tear-sheet generation, model-update packets, and model diffs.

From the skill root, copy the templates into a temporary workspace. The bundled template defaults to packet/dry-run mode and writes outside the skill tree so sample execution does not dirty the repository.

```bash
TMPDIR="$(mktemp -d)"
mkdir -p "$TMPDIR/normalized"
cp assets/templates/plan.template.json "$TMPDIR/plan.json"
cp assets/templates/normalized_*.csv "$TMPDIR/normalized/"
cp assets/templates/driver_updates.csv "$TMPDIR/normalized/driver_updates.csv"

python scripts/validate_plan.py "$TMPDIR/plan.json"
python scripts/validate_normalized_inputs.py "$TMPDIR/plan.json"
python scripts/run_plan.py "$TMPDIR/plan.json"
python scripts/verify_tearsheet.py /tmp/public_equity_investing_earnings_deep_dive_output/TearSheet.md
```

Switch `outputs.model_update.enabled` to `true` and `mode` to `apply` only when the user has supplied a real prior model and explicitly wants workbook changes.
