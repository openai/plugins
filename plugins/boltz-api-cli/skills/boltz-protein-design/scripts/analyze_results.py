#!/usr/bin/env python3
"""Yield readout for a finished design run.

Reads results/index.jsonl and reports the standard binding_confidence summary a
designer expects after every run: the maximum, the 10th-highest, and the
fraction of designs above 0.01 and 0.05. Use the **max binding_confidence** to
pick the winning config when comparing scout runs.

Usage:
    python3 analyze_results.py <run-dir>
    python3 analyze_results.py <run-dir> --json
"""

import argparse
import json
import os
import sys


def load_bc(run_dir):
    idx = os.path.join(run_dir, "results", "index.jsonl")
    if not os.path.exists(idx):
        alt = os.path.join(run_dir, "index.jsonl")
        idx = alt if os.path.exists(alt) else idx
    if not os.path.exists(idx):
        sys.exit(f"error: no results/index.jsonl under {run_dir}")
    bc = []
    with open(idx) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            v = rec.get("metrics", {}).get("binding_confidence")
            if v is not None:
                bc.append(float(v))
    if not bc:
        sys.exit(f"error: no binding_confidence values in {idx}")
    return bc


def summarize(bc):
    """Yield-readout summary for a list of binding_confidence values."""
    bc = sorted(bc, reverse=True)
    n = len(bc)
    return {
        "n_designs": n,
        "max_bc": bc[0],
        "bc_10th": bc[9] if n >= 10 else None,
        "frac_gt_0.01": sum(v > 0.01 for v in bc) / n,
        "frac_gt_0.05": sum(v > 0.05 for v in bc) / n,
    }


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("run_dir")
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = ap.parse_args()

    summary = summarize(load_bc(args.run_dir))
    n = summary["n_designs"]

    if args.json:
        print(json.dumps(summary))
        return
    print(f"designs:            {n}")
    print(f"max binding_conf:   {summary['max_bc']:.4f}   <-- config-selection metric")
    tenth = summary["bc_10th"]
    print(
        f"10th-highest bc:    {tenth:.4f}"
        if tenth is not None
        else "10th-highest bc:    n/a (<10 designs)"
    )
    print(f"fraction bc > 0.01: {summary['frac_gt_0.01']:.3f}")
    print(f"fraction bc > 0.05: {summary['frac_gt_0.05']:.3f}")


if __name__ == "__main__":
    main()
