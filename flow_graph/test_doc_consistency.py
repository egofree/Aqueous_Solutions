# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Hand-written pages that list graph structure must agree with the graph.

Documents describe structure, not current counts (AGENTS.md, "Parametric documentation").
Where a hand-written page does list structure, this test is what keeps it true: it fails
when the graph gains, loses or renames a sector and the page is not updated.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAPH = json.loads((ROOT / 'flow_graph/plant_flow_graph.json').read_text())
SECTORS = {s['sector_id']: s['sector_definition'] for s in GRAPH['mvs']['sectors']}

# README "Kind" column -> prefix of the graph's sector_definition
KINDS = {'Process': 'Process', 'Life support': 'Life support', 'Utilities': 'Utility',
         'Energy storage': 'Energy Storage', 'Export': 'Export'}


def _readme_sector_table():
    text = (ROOT / 'README.md').read_text()
    rows = re.findall(r'^\| *([^|]+?) *\| *([^|]+?) *\|$', text, flags=re.M)
    table = {}
    for kind, cell in rows:
        if kind in KINDS:
            cell = re.sub(r'\([^)]*\)', '', cell)        # parenthetical remarks are not sector ids
            table[kind] = re.findall(r'\b[A-Z][A-Z0-9_]+\b', cell)
    return table


def test_readme_sector_table_matches_graph():
    table = _readme_sector_table()
    listed = [s for ids in table.values() for s in ids]
    assert len(listed) == len(set(listed)), f'README lists a sector twice: {listed}'
    assert set(listed) == set(SECTORS), (
        f'README sector table drifted from graph mvs.sectors: missing {sorted(set(SECTORS) - set(listed))}, '
        f'unknown {sorted(set(listed) - set(SECTORS))}')
    for kind, ids in table.items():
        for s in ids:
            assert SECTORS[s].startswith(KINDS[kind]), f'README puts {s} under {kind}; graph says {SECTORS[s]!r}'
