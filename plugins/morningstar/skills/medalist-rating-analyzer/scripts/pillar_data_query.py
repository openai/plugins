"""Tool for querying pillar rating input data IDs."""

import os
from typing import List, Literal


def _load_rows() -> List[dict]:
    """Parse the pillar rating input data reference markdown table into row dicts."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    skill_root = os.path.dirname(current_dir)
    md_path = os.path.join(skill_root, 'references', 'pillar_rating_input_data.md')

    try:
        with open(md_path, encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"pillar_rating_input_data.md not found at {md_path}. "
            "Ensure the file is present alongside the skill package."
        ) from exc

    table_lines = [line.strip() for line in lines if line.strip().startswith('|')]
    # Drop the header row and the "|---|---|---|---|" separator row.
    data_lines = table_lines[2:]

    rows = []
    for line in data_lines:
        cells = [cell.strip() for cell in line.strip('|').split('|')]
        if len(cells) != 4:
            continue
        pillar, active_passive, data_id, name = cells
        rows.append({
            'Pillar': pillar,
            'Active/Passive': active_passive,
            'ID': data_id,
            'Name': name,
        })
    return rows


def get_pillar_data_id(
    pillar: Literal["parent", "people", "process"],
    manage_type: Literal["active", "passive"]
) -> List[str]:
    """
    Query pillar rating input data and return matching IDs.

    Args:
        pillar: The pillar type (parent, people, or process)
        manage_type: The management type (active or passive)

    Returns:
        List of matching data point IDs
    """
    rows = _load_rows()

    # Normalize inputs for case-insensitive matching
    pillar_normalized = pillar.lower().capitalize()
    manage_type_normalized = manage_type.lower().capitalize()

    # Parent inputs are shared across active and passive vehicles.
    if pillar_normalized == "Parent":
        matches = [r for r in rows if r['Pillar'] == pillar_normalized]
    # Filter data based on pillar and manage_type.
    # Handle both exact matches and "Passive/Active" entries for passive queries.
    elif manage_type_normalized == "Passive":
        matches = [
            r for r in rows
            if r['Pillar'] == pillar_normalized
            and r['Active/Passive'] in (manage_type_normalized, 'Passive/Active')
        ]
    else:
        matches = [
            r for r in rows
            if r['Pillar'] == pillar_normalized
            and r['Active/Passive'] == manage_type_normalized
        ]

    return [r['ID'] for r in matches]
