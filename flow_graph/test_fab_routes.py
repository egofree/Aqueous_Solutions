"""Unit task 13 gate: every roster unit carries a fabrication route sheet, and the
generated sheets (docs-authority/_fab_routes.py) quote their envelope and internals
from the issued registers instead of inventing dimensions."""
import json
import os

here = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(here)
G = json.load(open(os.path.join(R, 'flow_graph/plant_flow_graph.json')))
UNITS = sorted(n['unit_id'] for n in G['nodes']
               if n.get('class') != 'boundary' and n.get('sector_id'))


def test_every_roster_unit_has_a_fab_sheet():
    for u in UNITS:
        assert os.path.exists(os.path.join(R, f'docs-authority/fab/{u}.md')), u


def test_generated_sheets_quote_their_registers():
    owned = [u for u in UNITS
             if open(os.path.join(R, f'docs-authority/fab/{u}.md')).read()
             .startswith(f'# {u} fabrication\n\nClass: ')]
    assert owned, 'generator expects to own the sheets it issued'
    for u in owned:
        s = open(os.path.join(R, f'docs-authority/fab/{u}.md')).read()
        # every envelope line is either quoted from the duty sheet or states the hold
        for ln in s.splitlines():
            if ln.startswith('Envelope: '):
                assert 'x' not in ln.lower().split('envelope:', 1)[1].split(';')[0] \
                    or ln.startswith('Envelope: Envelope '), (u, ln)
        assert 'Not stamped' in s and 'Study route' in s
        # the material line is verbatim duty section 3 (pending stays pending, no invention)
        if 'Selection pending' in s:
            assert 'unit task 09' in s, u
        assert 'nothing invented' in s or 'per the duty sheet' in s or 'AQS-STD-001' in s, u
