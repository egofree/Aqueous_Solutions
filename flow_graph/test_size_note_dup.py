# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""No node parameter string repeats the same sentence (X-QA-15).

Writers stamp note strings by appending; a writer that appends without stripping its
own previous stamp duplicates a sentence on every regeneration pass (the retired
"Size follows the machine build (style builder ...)" stamp did exactly that). This
guard fails on any repeated sentence inside one node params or notes string, so the
class cannot bake back into the graph unnoticed. Scan by hand with:
python3 - <<'EOF' (split every params/notes string into sentences, count repeats).
"""
import json
import os
import re
from collections import Counter

_SENT = re.compile(r'(?<=[.!?])\s+(?=[A-Z("\'])')

GRAPH = os.path.join(os.path.dirname(__file__), 'plant_flow_graph.json')


def _strings(obj, path=''):
    """Every (path, text) pair under a JSON value, strings only."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from _strings(v, f'{path}.{k}' if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _strings(v, f'{path}[{i}]')
    elif isinstance(obj, str):
        yield path, obj


def test_no_repeated_sentences_in_node_params():
    bad = []
    for n in json.load(open(GRAPH))['nodes']:
        for path, text in _strings(n.get('params'), 'params'):
            if path == 'params':     # a bare string param is a label, not a note
                continue
            counts = Counter(s.strip() for s in _SENT.split(text) if s.strip())
            for sentence, count in counts.items():
                if count > 1:
                    bad.append(f"{n['unit_id']} {path}: {count}x {sentence}")
    assert not bad, 'repeated sentences in node params:\n' + '\n'.join(bad)


def test_no_repeated_sentences_in_node_notes():
    bad = []
    for n in json.load(open(GRAPH))['nodes']:
        note = n.get('notes')
        if isinstance(note, str):
            counts = Counter(s.strip() for s in _SENT.split(note) if s.strip())
            for sentence, count in counts.items():
                if count > 1:
                    bad.append(f"{n['unit_id']} notes: {count}x {sentence}")
    assert not bad, 'repeated sentences in node notes:\n' + '\n'.join(bad)
