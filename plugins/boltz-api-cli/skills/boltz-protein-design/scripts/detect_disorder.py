#!/usr/bin/env python3
"""Suggest internal disordered regions to crop away from a target.

This is a confidence/mobility heuristic, not a true secondary-structure
detector (the weakest exploration axis — confirm the suggestion looks sane).
Two modes:

  --mode plddt   (default): treat the B-factor column as pLDDT; flag residues
                 with mean pLDDT below --cutoff (default 70). Use for predicted
                 targets (AlphaFold / Boltz), which carry pLDDT and no SS records.
  --mode bfactor : flag residues with mean B-factor above --cutoff (default 60);
                 high B = mobile. Use for experimental structures.

Internal runs of flagged residues longer than --min-loop are reported as
disorder crops; runs touching either terminus are left to terminus trimming.
Prints the kept `crop_residues` (0-based API indices) with internal runs removed.

Usage:
    python3 detect_disorder.py target.cif --chain A --min-loop 10
    python3 detect_disorder.py xtal.cif --chain A --mode bfactor --cutoff 60
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import indexed_residues, internal_runs, load_chain, residue_bfactor  # noqa: E402


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("cif")
    ap.add_argument("--chain", default="A")
    ap.add_argument("--mode", choices=["plddt", "bfactor"], default="plddt")
    ap.add_argument(
        "--cutoff",
        type=float,
        default=None,
        help="pLDDT floor (plddt mode, default 70) or B-factor "
        "ceiling (bfactor mode, default 60)",
    )
    ap.add_argument(
        "--min-loop",
        type=int,
        default=10,
        help="minimum internal run length to crop (default 10)",
    )
    args = ap.parse_args()

    cutoff = args.cutoff
    if cutoff is None:
        cutoff = 70.0 if args.mode == "plddt" else 60.0

    _, _, poly = load_chain(args.cif, args.chain)
    pairs, used_label_seq = indexed_residues(poly)
    if not used_label_seq:
        print(
            "warning: chain lacks label_seq; indices use enumeration order",
            file=sys.stderr,
        )

    all_indices = [idx for idx, _ in pairs]
    if args.mode == "plddt":
        flagged = {idx for idx, res in pairs if residue_bfactor(res) < cutoff}
    else:
        flagged = {idx for idx, res in pairs if residue_bfactor(res) > cutoff}

    runs = internal_runs(flagged, all_indices, args.min_loop)
    removed = set()
    for i, j in runs:
        span = all_indices[i : j + 1]
        removed.update(span)
        print(
            f"# internal disorder run: API {span[0]}..{span[-1]} "
            f"({len(span)} residues)",
            file=sys.stderr,
        )
    if not runs:
        print(
            f"# no internal disorder runs longer than {args.min_loop} residues "
            f"(mode={args.mode}, cutoff={cutoff:g})",
            file=sys.stderr,
        )

    keep = [idx for idx in all_indices if idx not in removed]
    print(f"# kept {len(keep)} of {len(all_indices)} residues (removed {len(removed)})")
    print(json.dumps(keep))


if __name__ == "__main__":
    main()
