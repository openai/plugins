"""Shared helpers for the boltz-protein-design target-exploration scripts.

Indexing contract: every script emits and consumes **0-based API residue
indices**, the same indices used by `crop_residues` / `epitope_residues` /
`flexible_residues` in the payload. The mapping is:

    API index = canonical label_seq_id - 1

We read `label_seq` from the CIF (not author numbering) so outputs drop straight
into the payload with no offset arithmetic. Do not reintroduce auth-number
offsets.
"""

import sys

import gemmi
import numpy as np


def load_chain(cif_path, chain_id):
    """Return (structure, chain, polymer) for one chain, or exit with a message."""
    st = gemmi.read_structure(str(cif_path))
    st.setup_entities()
    model = st[0]
    chain = next((c for c in model if c.name == chain_id), None)
    if chain is None:
        avail = ", ".join(c.name for c in model)
        sys.exit(f"error: chain '{chain_id}' not found (available chains: {avail})")
    poly = chain.get_polymer()
    if len(poly) == 0:
        sys.exit(f"error: chain '{chain_id}' has no polymer residues")
    return st, chain, poly


def indexed_residues(poly):
    """Return ([(api_index, residue), ...], used_label_seq).

    Prefer canonical label_seq (gap-safe). Fall back to enumeration order only
    when label_seq is absent; that misaligns across unmodeled internal gaps, so
    callers should warn when used_label_seq is False.
    """
    used_label_seq = all(r.label_seq is not None for r in poly)
    pairs = []
    for pos, res in enumerate(poly):
        idx = (res.label_seq - 1) if used_label_seq else pos
        pairs.append((idx, res))
    return pairs, used_label_seq


def atom_coords(res):
    """(n_atoms, 3) float array of a residue's atom positions."""
    return np.array([[a.pos.x, a.pos.y, a.pos.z] for a in res], dtype=float)


def residue_bfactor(res):
    """Mean B-iso of a residue's atoms (pLDDT for predicted structures)."""
    vals = [a.b_iso for a in res]
    return sum(vals) / len(vals) if vals else float("nan")


def internal_runs(flagged_indices, all_indices, min_len):
    """Runs of consecutive flagged residues longer than min_len that do not
    touch either terminus. `all_indices` must be sorted; flags are a set.

    Returns a list of (start_pos, end_pos) index-position spans into all_indices.
    """
    flagged = set(flagged_indices)
    runs = []
    n = len(all_indices)
    i = 0
    while i < n:
        if all_indices[i] in flagged:
            j = i
            while j + 1 < n and all_indices[j + 1] in flagged:
                j += 1
            touches_terminus = (i == 0) or (j == n - 1)
            if (j - i + 1) > min_len and not touches_terminus:
                runs.append((i, j))
            i = j + 1
        else:
            i += 1
    return runs
