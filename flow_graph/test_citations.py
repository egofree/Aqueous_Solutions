# SPDX-License-Identifier: MIT
# Copyright 2026 Mike Matthews.
"""Live text cites only current document numbers, sectors, paths, script names and commits.

The data that defines "retired" is kept outside this test: the Former number lines on renumbered
pages, RETIRED_SECTOR_IDS in the design tool, docs-authority/retired_names.json and
docs-authority/rewritten_commits.json. See flow_graph/check_citations.py."""
import json
import os
import subprocess

from flow_graph import check_citations as cc

ROOT = cc.ROOT


def test_no_stale_citations():
    found = cc.scan()
    assert not found, 'stale citations (run python3 -m flow_graph.check_citations --fix, then fix the rest by hand):\n' + \
        '\n'.join(' | '.join(map(str, r)) for r in found[:40])


def test_retired_paths_are_gone():
    rules = json.load(open(os.path.join(ROOT, 'docs-authority/retired_names.json')))['paths']
    tracked = cc.tracked()
    for r in rules:
        live = [f for f in tracked if f.startswith(r['old']) and not any(f.startswith(k) for k in r.get('keep', []))]
        if r['old'] == 'notes/':
            continue   # notes/ still holds the older study notes; only moved notes are retired
        assert not live, f"{r['old']} is listed as retired but still holds {live[:3]}"


def test_rewritten_commit_map():
    m = json.load(open(os.path.join(ROOT, 'docs-authority/rewritten_commits.json')))['map']
    def in_history(s):   # an ancestor of HEAD; a stale local branch may still hold the old objects
        return subprocess.run(['git', 'merge-base', '--is-ancestor', s, 'HEAD'], cwd=ROOT, capture_output=True).returncode == 0
    for old, new in m.items():
        assert in_history(new), f'mapped commit {new} is not in the history of HEAD'
        assert not in_history(old), f'pre-rewrite commit {old} is in the history of HEAD; it needs no mapping'


def test_edge_sectors_follow_nodes():
    g = json.load(open(os.path.join(ROOT, 'flow_graph/plant_flow_graph.json')))
    sector = {n['unit_id']: n.get('sector_id') for n in g['nodes'] if n.get('sector_id')}
    bad = [(e['stream_id'], end) for e in g['edges'] for end in ('from', 'to')
           if e[f'{end}_unit_id'] in sector and e.get(f'{end}_sector_id') != sector[e[f'{end}_unit_id']]]
    assert not bad, f'edges whose sector differs from their unit (stage edge_sectors): {bad[:10]}'
