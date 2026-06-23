#!/usr/bin/env python3
"""All-atom radius crop around a binding site.

A target residue is kept if any of its atoms is within R angstrom of any atom of
any site residue (all-atom to all-atom, on both sides). Prints the kept
`crop_residues` (0-based API indices) for each radius. Site residues are given
as 0-based API indices and are always kept.

Scout a couple of radii rather than all five, and run each radius twice as
separate configs: once with the site in `epitope_residues`, once without.

Usage:
    python3 crop_radius.py target.cif --chain A --site 42,43,44 --radii 15,25,35
"""

import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import atom_coords, indexed_residues, load_chain  # noqa: E402


def parse_int_list(s):
    return [int(x) for x in s.replace(" ", "").split(",") if x != ""]


def parse_float_list(s):
    return [float(x) for x in s.replace(" ", "").split(",") if x != ""]


def crop_within(pairs, site, radius):
    """Indices kept within `radius` (all-atom) of any site residue; site always
    kept. `pairs` is [(api_index, residue), ...]; `site` is a set of api indices.
    """
    by_idx = {idx: res for idx, res in pairs}
    site_atoms = np.vstack([atom_coords(by_idx[s]) for s in site])
    keep = []
    for idx, res in pairs:
        coords = atom_coords(res)
        d2 = ((coords[:, None, :] - site_atoms[None, :, :]) ** 2).sum(-1)
        if np.sqrt(d2.min()) < radius:
            keep.append(idx)
    return sorted(set(keep) | set(site))


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("cif")
    ap.add_argument("--chain", default="A")
    ap.add_argument(
        "--site",
        required=True,
        help="comma-separated 0-based API indices of site residues",
    )
    ap.add_argument(
        "--radii",
        default="10,15,25,30,35",
        help="comma-separated radii in angstrom (default 10,15,25,30,35)",
    )
    args = ap.parse_args()

    _, _, poly = load_chain(args.cif, args.chain)
    pairs, used_label_seq = indexed_residues(poly)
    if not used_label_seq:
        print(
            "warning: chain lacks label_seq; indices use enumeration order",
            file=sys.stderr,
        )

    site = set(parse_int_list(args.site))
    radii = sorted(parse_float_list(args.radii))

    by_idx = {idx: res for idx, res in pairs}
    missing = sorted(s for s in site if s not in by_idx)
    if missing:
        sys.exit(f"error: site indices not present in chain {args.chain}: {missing}")

    for r in radii:
        keep = crop_within(pairs, site, r)
        print(f"# radius {r:g} A: {len(keep)} residues kept")
        print(json.dumps(keep))


if __name__ == "__main__":
    main()
