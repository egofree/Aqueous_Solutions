"""The S08 composition table of FEED_ASSAY.md (table 5.1, AQS-FEED-001 section 5) is the graph
booking in prose: its deposit rows must equal solver.ew_products at the published precision, so
the hand page cannot drift from the solver (F-20261110-02). The silicate residual row is checked
against its own arithmetic (the S08 rate less the deposits; the registered crib carry, A-M-490)."""
import json, re

from flow_graph.param import drivers as DR, solver
from flow_graph.param.ew_cells import EW_CELLS

CELL_OF_ELEMENT = {el: n for n, (el, _z, _cls) in EW_CELLS.items()}


def _table_rows():
    text = open(solver.ROOT + '/docs-authority/FEED_ASSAY.md').read()
    block = text.split('Table 5.1. Composition of S08', 1)[1]
    rows, started = [], False
    for line in block.splitlines():
        if not line.startswith('|'):
            if started:
                break                       # the table ended; prose or a later table follows
            continue
        m = re.match(r'\| (.+?) \| ([0-9.]+) \| ([0-9.]+) \| (.+?) \|$', line.strip())
        if m:
            started = True                  # the separator row has no numbers and does not match
            rows.append((m.group(1).strip(), float(m.group(2)), float(m.group(3)), m.group(4).strip()))
    assert rows, 'table 5.1 not found in FEED_ASSAY.md'
    return rows


def test_deposit_rows_match_solver():
    d = DR.load()
    g = json.load(open(solver.ROOT + '/flow_graph/plant_flow_graph.json'))
    dep = solver.ew_products(d, g)['dep']
    s08 = next(e for e in g['edges'] if e['stream_id'] == 'S08')['rate']['value']
    seen = {}
    for name, kg_d, frac, source in _table_rows():
        if source != 'deposit':
            continue
        assert name in CELL_OF_ELEMENT, f'table 5.1 deposit row {name!r} has no cell in the booking map'
        cell = CELL_OF_ELEMENT[name]
        seen[cell] = kg_d
        assert kg_d == dep[cell], f'table 5.1 {name} row {kg_d} != solver.ew_products {dep[cell]} (cell EW_{cell})'
        assert frac == round(kg_d / s08, 8), f'table 5.1 {name} fraction {frac} != kg/d over the S08 rate'
    assert set(seen) == set(EW_CELLS), f'table 5.1 deposit rows cover {sorted(seen)}, the map covers {sorted(EW_CELLS)}'


def test_silicate_residual_row():
    d = DR.load()
    g = json.load(open(solver.ROOT + '/flow_graph/plant_flow_graph.json'))
    dep = solver.ew_products(d, g)['dep']
    s08 = next(e for e in g['edges'] if e['stream_id'] == 'S08')['rate']['value']
    rows = {name: (kg_d, frac) for name, kg_d, frac, _src in _table_rows()}
    sil = next(v for k, v in rows.items() if k.startswith('SiO'))
    residual = round(s08 - sum(dep.values()), 6)
    assert sil[0] == residual, f'table 5.1 silicate residual {sil[0]} != S08 rate less the deposits {residual}'
    assert sil[1] == round(sil[0] / s08, 8), 'table 5.1 silicate fraction inconsistent with the row and the S08 rate'
    assert round(sum(kg for kg, _f in rows.values()), 6) == round(s08, 6), 'table 5.1 rows must sum to the S08 rate'
