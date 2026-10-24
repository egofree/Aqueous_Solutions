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


# --- one copy of every document -------------------------------------------------------------

import hashlib
import importlib.util
import subprocess
from collections import defaultdict


def _tracked(suffix):
    try:
        out = subprocess.run(['git', 'ls-files', '-z', f'*{suffix}'], cwd=ROOT, capture_output=True, text=True, check=True).stdout
        return [ROOT / f for f in out.split('\0') if f and (ROOT / f).is_file()]
    except (OSError, subprocess.CalledProcessError):
        return [p for p in ROOT.rglob(f'*{suffix}') if '.git' not in p.parts]


def test_no_duplicate_markdown_content():
    """Two files with the same text drift apart; keep one and point to it."""
    seen = defaultdict(list)
    for p in _tracked('.md'):
        body = ' '.join(p.read_text(errors='replace').split())
        if len(body) >= 200:                                      # ignore trivial stubs
            seen[hashlib.sha256(body.encode()).hexdigest()].append(str(p.relative_to(ROOT)))
    dups = [v for v in seen.values() if len(v) > 1]
    assert not dups, f'identical Markdown files (keep one, point to it): {dups}'


def test_no_duplicate_titles_in_hand_written_docs():
    """Hand-written pages at the top of docs-authority/, notes/ and the root have distinct H1 titles."""
    pages = [*ROOT.glob('*.md'), *(ROOT / 'docs-authority').glob('*.md'), *(ROOT / 'notes').glob('*.md'),
             *(ROOT / 'docs-authority/notes').glob('*.md'), *(ROOT / 'docs-authority/internal').glob('*.md')]
    titles = defaultdict(list)
    for p in pages:
        m = re.search(r'^# (.+)$', p.read_text(errors='replace'), flags=re.M)
        if m:
            titles[m.group(1).strip().lower()].append(str(p.relative_to(ROOT)))
    dups = {t: v for t, v in titles.items() if len(v) > 1}
    assert not dups, f'two pages share a title (merge them or retitle one): {dups}'


# --- heat ladder (AQS-HEAT-LADDER-001): rules stated in prose, enforced here ------------------

def _tier(unit):
    m = re.match(r'Q([1-4])_', unit or '')
    return int(m.group(1)) if m else None


def test_heat_ladder_moves_heat_down_only():
    present = [e for e in GRAPH['edges'] if e.get('presence') == 'present']
    for e in present:
        a, b = e['from_unit_id'], e['to_unit_id']
        ta, tb = _tier(a), _tier(b)
        if ta and tb:
            assert tb >= ta, f'{e["stream_id"]}: {a} -> {b} lifts heat up the ladder'
        if ta in (1, 2, 3):
            assert b != 'Q4_BUS', f'{e["stream_id"]}: {a} lands on Q4_BUS, skipping the Q4 battery'
        if a == 'HX8':
            assert _tier(b) != 3, f'{e["stream_id"]}: HX-8 feeds Q3; it preheats the Q4 return'
        if a == 'GEO_HP':
            assert _tier(b) in (None, 4), f'{e["stream_id"]}: GEO_HP lifts into {b}; it feeds Q4 and the farm only'


# --- sector catalogue: design tool, generated page and graph agree ---------------------------

def _sector_module():
    p = ROOT / 'design_tool/aqs_design_tool/sector_definitions.py'
    spec = importlib.util.spec_from_file_location('aqs_sector_definitions', p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_design_tool_sector_catalogue_matches_graph():
    mod = _sector_module()
    graph = {s['sector_id']: s for s in GRAPH['mvs']['sectors']}
    cat = {r['sector_id']: r for r in mod.SECTOR_CATALOGUE}
    assert set(cat) == set(graph), f'design-tool catalogue drifted: missing {sorted(set(graph) - set(cat))}, extra {sorted(set(cat) - set(graph))}'
    for sid, row in cat.items():
        assert row['sector_definition'] == graph[sid]['sector_definition'], sid
        assert row['required_for_mvs_closure'] == graph[sid]['required_for_mvs_closure'], sid


def test_retired_sector_ids_are_not_current():
    mod = _sector_module()
    retired = set(mod.RETIRED_SECTOR_IDS) | set(mod.NON_SECTOR_ALIASES)
    clash = retired & set(SECTORS)
    assert not clash, f'ids listed as retired or alias are live graph sectors: {sorted(clash)}'
    for old, row in mod.RETIRED_SECTOR_IDS.items():
        for new in row['now']:
            assert new in SECTORS, f'retired sector {old} points to {new}, which is not a graph sector'


def test_unit_sectors_are_graph_sectors():
    bad = sorted({n['sector_id'] for n in GRAPH['nodes']} - set(SECTORS))
    assert not bad, f'units carry sector ids missing from mvs.sectors: {bad}'


def test_glossary_sector_entries_match_graph():
    """Every graph sector has a glossary entry; any other entry described as a sector is marked former."""
    text = (ROOT / 'docs-authority/GLOSSARY.md').read_text()
    entries = dict(re.findall(r'^\{([A-Z][A-Z0-9_]+) -- ([^}]*)\}', text, flags=re.M))
    missing = sorted(s for s in SECTORS if s not in entries)
    assert not missing, f'GLOSSARY.md has no entry for graph sectors {missing}'
    for term, body in entries.items():
        if term not in SECTORS and re.search(r'\bsector\b', body.split('.')[0], flags=re.I):
            assert body.lower().startswith('former'), f'GLOSSARY.md describes {term} as a sector, but the graph has no such sector'
