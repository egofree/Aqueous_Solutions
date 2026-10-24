# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Identifiers are unique, so a citation always resolves to one thing.

Covers document numbers (via docs-authority/_doc_register.py, the same scan that writes
DOC_REGISTER.md), assumption ids, open-question ids, task ids, and graph unit and stream ids.
New numbers come from `python3 docs-authority/_doc_register.py --next AQS-SERIES`; new ids in
the other families take the next unused id in their sequence. These tests fail on a
collision instead of relying on anyone remembering what is taken.
"""
import importlib.util
import json
import os
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DA = ROOT / 'docs-authority'

_spec = importlib.util.spec_from_file_location('_doc_register', DA / '_doc_register.py')
REG = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(REG)
CLAIMS, PARTS, FORMERS, PROBLEMS = REG.scan()


def _dups(ids):
    return sorted(k for k, n in Counter(ids).items() if n > 1)


def test_document_numbers_unique_and_present():
    assert not PROBLEMS, '\n'.join(PROBLEMS)


def test_next_free_number_is_unused():
    used = set(CLAIMS) | {f['old'] for f in FORMERS} | {p['number'] for p in PARTS}
    for series in {REG.series_of(n)[0] for n in CLAIMS} - {None}:
        assert REG.next_free(series) not in used, series


def test_register_is_current():
    want = REG.render(CLAIMS, PARTS, FORMERS)
    have = (ROOT / REG.OUT).read_text()
    assert have == want, 'DOC_REGISTER.md is stale: run python3 docs-authority/_doc_register.py'


def test_docs_map_lists_every_page_with_its_number():
    by_path = {x['path']: n for n, xs in CLAIMS.items() for x in xs}
    listed, wrong = set(), []
    for href, num in re.findall(r'^\| \[[^\]]+\]\(([^)]+)\) \| ([^|]*) \|', (DA / 'README.md').read_text(), flags=re.M):
        p = os.path.normpath(f'docs-authority/{href}')
        listed.add(p)
        if p in by_path and num.strip() != by_path[p]:
            wrong.append(f'{p}: docs map says {num.strip()!r}, page says {by_path[p]}')
    pages = {f'docs-authority/{f.name}' for f in DA.glob('*.md') if f.name != 'README.md'}
    assert not wrong, '\n'.join(wrong)
    assert not pages - listed, f'pages missing from the docs map: {sorted(pages - listed)}'


def test_assumption_ids_unique():
    manual = [a['id'] for a in json.loads((DA / 'assumptions_manual.json').read_text())]
    assert not _dups(manual), _dups(manual)
    register = re.findall(r'^\| (A-[A-Z]-[^ |]+) \|', (DA / 'ASSUMPTIONS_REGISTER.md').read_text(), flags=re.M)
    assert register and not _dups(register), _dups(register)


def test_open_question_ids_unique():
    ids = re.findall(r'^\| (Q-[0-9A-Za-z-]+) \|', (DA / 'OPEN_QUESTIONS.md').read_text(), flags=re.M)
    assert ids and not _dups(ids), _dups(ids)


def test_task_ids_unique():
    ids = re.findall(r'^\s*- \[[ x~-]\] \**([A-Z][A-Za-z0-9_]*(?:-[A-Za-z0-9_]+)+)',
                     (DA / 'TASK_PLAN.md').read_text(), flags=re.M)
    assert ids and not _dups(ids), _dups(ids)


def test_graph_unit_and_stream_ids_unique():
    g = json.loads((ROOT / 'flow_graph/plant_flow_graph.json').read_text())
    units = [n.get('unit_id') for n in g['nodes']]
    streams = [e.get('stream_id') for e in g['edges']]
    assert None not in units and None not in streams
    assert not _dups(units), _dups(units)
    assert not _dups(streams), _dups(streams)
