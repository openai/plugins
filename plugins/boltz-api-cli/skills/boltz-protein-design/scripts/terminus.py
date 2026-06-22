#!/usr/bin/env python3
"""Print the first/last resolved residue of a chain as 0-based API indices.

Use this to trim unmodeled N/C-terminal overhang before designing. Residues
present in the model (with atoms) are "resolved"; the kept crop is the resolved
set between the first and last resolved residue. For a typical CIF that contains
only modeled residues, `crop_residues: all` already excludes unmodeled termini —
use this script when the template includes unmodeled residues or when you want
the explicit index range.

Usage:
    python3 terminus.py target.cif --chain A
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import indexed_residues, load_chain  # noqa: E402


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("cif")
    ap.add_argument("--chain", default="A")
    args = ap.parse_args()

    _, _, poly = load_chain(args.cif, args.chain)
    pairs, used_label_seq = indexed_residues(poly)
    if not used_label_seq:
        print(
            "warning: chain lacks label_seq; using enumeration order "
            "(may misalign across unmodeled internal gaps)",
            file=sys.stderr,
        )

    keep = [idx for idx, _ in pairs]
    print(f"chain {args.chain}: {len(keep)} resolved residues")
    print(f"first resolved API index: {keep[0]}")
    print(f"last  resolved API index: {keep[-1]}")
    print("crop_residues (0-based API indices):")
    print(json.dumps(keep))


if __name__ == "__main__":
    main()
