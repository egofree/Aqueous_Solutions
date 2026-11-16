"""engine v2: the upw_polish-family acceptance (the golden-value proof).

Reference writer: flow_graph/param/upw_polish.py `--write` (ledger row
`sizing_upw_polish`, section B - the X-MFG-34 RO/EDI polish on
BMED_UPW_POLISH, A-M-176 / AQS-DUTY-070). The committed graph carries every
field the family stamps; the proofs:

- exact change set: the family's overlay equals the hand-enumerated
  specification (15 params.design fields, the internals text, 2 continuous_kw
  fields, 1 SF re-rate), and a strict whole-model walk (nodes and edges, same
  JSON types) proves nothing else moved;
- golden equality: every changed field equals the committed golden, numbers
  quantised to the golden's decimals (exact repr equality) - including the
  raw-float books the family ported as v1 float books (the foundry
  precedent: the RO feed itself carries the v1 float dust on the graph);
- the solution-diffusion and EDI chains re-derived on exact Decimal
  arithmetic: the graph recovery, the mean osmotic pressure [BAKER2012], the
  membrane area at the design flux, the EDI current on the permeate salt
  [ALVARADO2014] and the specific-energy books;
- grid spot-checks: the module count (one standby) as an integer book, the
  4 dp kW books;
- the driver-tamper table: the flux, the permeance, the rejection and the EDI
  current efficiency move the books as the exact chain predicts;
- the bridge contracts: no driver payload records nothing; a seed without the
  graph duty edges records nothing; the SQ-assert fires on retired topology;
- determinism: two runs, byte-identical;
- purity: no float literals and no I/O in the family module.

Integer-scale table (half-even throughout, Python round()'s tie rule): the
continuous_kw book 4 dp; every params.design field a raw v1 float book except
the module count, which stays the driver's integer book.
"""
import ast
import inspect
import json
import os
from decimal import Decimal

from flow_graph.v2.functions import upw_polish as UP
from flow_graph.v2.graph_io import bytes as render, load

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')
DRIVERS = os.path.join(ROOT, 'flow_graph', 'param', 'drivers.json')
INPUTS = {'drivers': json.load(open(DRIVERS))}
DUTY_EDGES = ('IA-UPW-FAB', 'S01', 'IA-UPW-REJ', 'IA-UPW-REMIN')

# The change-set specification: every (unit, field path) the family writes.
EXPECTED_FIELDS = [('BMED_UPW_POLISH', 'params.design.' + k) for k in (
    'UPW_kg_d', 'bypass_kg_d', 'RO_feed_kg_d', 'recovery', 'osmotic_bar', 'feed_bar', 'membrane_m2',
    'modules', 'RO_kW', 'EDI_A', 'EDI_kW', 'UV_kW', 'total_kW', 'kWh_per_m3', 'kWh_per_m3_RO_EDI')] + [
    ('BMED_UPW_POLISH', 'params.internals'),
    ('BMED_UPW_POLISH', 'continuous_kw.value'), ('BMED_UPW_POLISH', 'continuous_kw.note')]
EXPECTED_EDGES = [('SF-BMED_UPW_POLISH', 'rate')]


def run(inputs=None):
    b = load(REF_GRAPH)
    UP.upw_polish(b, inputs if inputs is not None else INPUTS)
    return b


def committed():
    with open(REF_GRAPH, encoding='utf-8') as f:
        return json.load(f)


def _num_eq(gold, got):
    return Decimal(str(gold)).normalize() == Decimal(str(got)).normalize()


def _eq(gold, got):
    if isinstance(gold, dict):
        return isinstance(got, dict) and set(gold) == set(got) and all(_eq(v, got[k]) for k, v in gold.items())
    if isinstance(gold, list):
        return isinstance(got, list) and len(gold) == len(got) and all(_eq(a, x) for a, x in zip(gold, got))
    if isinstance(gold, (int, float)) and not isinstance(gold, bool):
        return isinstance(got, (int, float)) and not isinstance(got, bool) and _num_eq(gold, got)
    return gold == got


def _dig(obj, path):
    cur = obj
    for part in path.split('.'):
        cur = cur[part]
    return cur


def _strict_diffs(c_obj, r_obj, prefix, out, expected):
    for k in sorted((set(c_obj) | set(r_obj)) - {'provenance'}):
        p = prefix + '.' + k if prefix else k
        if k not in c_obj or k not in r_obj:
            out.add(p)
        elif p in expected:
            if not _eq(c_obj[k], r_obj[k]):
                out.add(p)
        elif isinstance(c_obj[k], dict) and isinstance(r_obj[k], dict):
            _strict_diffs(c_obj[k], r_obj[k], p, out, expected)
        elif isinstance(c_obj[k], list) and isinstance(r_obj[k], list) and len(c_obj[k]) == len(r_obj[k]):
            if any(type(a) is not type(x) or a != x for a, x in zip(c_obj[k], r_obj[k])):
                out.add(p)
        elif type(c_obj[k]) is not type(r_obj[k]) or c_obj[k] != r_obj[k]:
            out.add(p)


def rates():
    edges = {e['stream_id']: e for e in committed()['edges']}
    return {sid: Decimal(str(edges[sid]['rate']['value'])) for sid in DUTY_EDGES}


def test_exact_change_set_and_golden_equality():
    c = committed()
    c_nodes = {n['unit_id']: n for n in c['nodes']}
    c_edges = {e['stream_id']: e for e in c['edges']}
    b = run()
    out = json.loads(render(b))
    r_nodes = {n['unit_id']: n for n in out['nodes']}
    r_edges = {e['stream_id']: e for e in out['edges']}

    got_nodes = sorted((uid, path) for (kind, uid, path) in b.computed if kind == 'node')
    got_edges = sorted((sid, path) for (kind, sid, path) in b.computed if kind == 'edge')
    assert got_nodes == sorted(EXPECTED_FIELDS), (
        sorted(set(got_nodes) - set(EXPECTED_FIELDS)), sorted(set(EXPECTED_FIELDS) - set(got_nodes)))
    assert got_edges == sorted(EXPECTED_EDGES)

    for uid, path in EXPECTED_FIELDS:
        assert _eq(_dig(c_nodes[uid], path), _dig(r_nodes[uid], path)), (uid, path)
    for sid, path in EXPECTED_EDGES:
        assert _eq(_dig(c_edges[sid], path), _dig(r_edges[sid], path)), (sid, path)

    expected_paths = {uid + '.' + path for uid, path in EXPECTED_FIELDS} \
        | {sid + '.' + path for sid, path in EXPECTED_EDGES}
    diffs = set()
    for uid in sorted(set(c_nodes) | set(r_nodes)):
        _strict_diffs(c_nodes[uid], r_nodes[uid], uid, diffs, expected_paths)
    assert diffs == set(), sorted(diffs)
    for sid in sorted(set(c_edges) | set(r_edges)):
        _strict_diffs(c_edges[sid], r_edges[sid], sid, diffs, expected_paths)
    assert diffs == set(), sorted(diffs)


def test_solution_diffusion_chain_on_exact_books():
    """The RO/EDI chain re-derived as exact Decimal books, independent of the
    float-replica stamps: the graph recovery, the osmotic pressure, the
    membrane area, the EDI current and the specific-energy books."""
    b = run()
    r = rates()
    upw, feed = r['IA-UPW-FAB'] + r['S01'], r['IA-UPW-FAB'] + r['S01'] + r['IA-UPW-REJ']
    rec = upw / feed                                             # the exact recovery
    c = Decimal('20') / Decimal('58.44')                         # mol/m3 NaCl at the driver TDS
    dpi = UP.osmotic_bar(c, rec, Decimal('0.98'), Decimal('298.15'))
    assert abs(dpi - Decimal(str(b.computed[('node', 'BMED_UPW_POLISH', 'params.design.osmotic_bar')][0]))) \
        < Decimal('1e-9')
    area = upw / 24 / Decimal('20')                              # kg/d ~ L/d over the design flux
    got_area = Decimal(str(b.computed[('node', 'BMED_UPW_POLISH', 'params.design.membrane_m2')][0]))
    assert abs(area - got_area) < Decimal('1e-12')
    c_perm = c * Decimal('0.02')                                 # the salt left in the permeate
    n_mol = upw / 1000 / 86400 * c_perm                          # mol/s
    i_edi = Decimal('96485') * n_mol / Decimal('0.1')            # the reference writer's Faraday book
    got_i = Decimal(str(b.computed[('node', 'BMED_UPW_POLISH', 'params.design.EDI_A')][0]))
    assert abs(i_edi - got_i) < Decimal('1e-12')
    p_edi = i_edi * Decimal('4') * 10 / 1000
    got_pe = Decimal(str(b.computed[('node', 'BMED_UPW_POLISH', 'params.design.EDI_kW')][0]))
    assert abs(p_edi - got_pe) < Decimal('1e-15')
    total = got_pe + Decimal(str(b.computed[('node', 'BMED_UPW_POLISH', 'params.design.RO_kW')][0])) \
        + Decimal('0.015')
    got_total = Decimal(str(b.computed[('node', 'BMED_UPW_POLISH', 'params.design.total_kW')][0]))
    assert abs(total - got_total) < Decimal('1e-12')
    got_kwh = Decimal(str(b.computed[('node', 'BMED_UPW_POLISH', 'params.design.kWh_per_m3')][0]))
    assert abs(got_total * 24 / (feed / 1000) - got_kwh) < Decimal('1e-9')
    # the raw float books carry the v1 chain verbatim (the foundry precedent)
    assert b.computed[('node', 'BMED_UPW_POLISH', 'params.design.RO_feed_kg_d')][0] == 133.34539999999998
    assert b.computed[('node', 'BMED_UPW_POLISH', 'params.design.UV_kW')][0] == 0.015
    assert b.computed[('node', 'BMED_UPW_POLISH', 'continuous_kw.value')][0] == 0.018
    assert b.computed[('edge', 'SF-BMED_UPW_POLISH', 'rate')][0]['value'] == 0.018
    seed = next(e for e in committed()['edges'] if e['stream_id'] == 'SF-BMED_UPW_POLISH')['rate']
    assert b.computed[('edge', 'SF-BMED_UPW_POLISH', 'rate')][0]['note'] == seed['note']  # value-only re-rate


def test_grid_spot_checks_and_texts():
    """The module count stays an integer book (one standby), the internals
    text is verbatim, and the note formats the per-stage books."""
    b = run()
    out = json.loads(render(b))
    node = next(n for n in out['nodes'] if n['unit_id'] == 'BMED_UPW_POLISH')
    assert type(node['params']['design']['modules']) is int and node['params']['design']['modules'] == 2
    assert node['params']['internals'] == UP.INTERNALS
    assert node['continuous_kw']['note'] == \
        'X-MFG-34 (A-M-176, AQS-DUTY-070): RO pump 2.6 W + EDI 0.39 W + UV 15 W; potable share bypasses.'
    assert node['continuous_kw']['unit'] == 'kW' and node['continuous_kw']['status'] == 'study'
    d = node['params']['design']
    assert d['UPW_kg_d'] == 127.300395 and d['bypass_kg_d'] == 221.446099    # the seed duty, verbatim


def test_driver_tamper_table():
    """The drivers move the books through the registered function as the exact
    chain predicts: the flux, the permeance, the rejection and the EDI current
    efficiency. Expected books come from the exact chain at the stored
    decimals - never scaled from the stored floats."""
    def books(tamper):
        drv = json.loads(json.dumps(INPUTS['drivers']))
        for key, val in tamper.items():
            drv[key]['value'] = val
        bb = run({'drivers': drv})
        return {p: bb.computed[('node', 'BMED_UPW_POLISH', p)][0]
                for p in ('params.design.membrane_m2', 'params.design.feed_bar', 'params.design.EDI_A',
                          'params.design.RO_kW', 'params.design.total_kW', 'continuous_kw.value')}
    base = books({})
    r = rates()
    upw = r['IA-UPW-FAB'] + r['S01']
    t = books({'ro_flux_LMH': 40.0})                             # double flux: half the area
    assert abs(Decimal(str(t['params.design.membrane_m2']))
               - Decimal(str(base['params.design.membrane_m2'])) / 2) < Decimal('1e-12')
    assert t['params.design.EDI_A'] == base['params.design.EDI_A']   # the EDI never sees the flux
    t = books({'ro_A_LMH_bar': 6.0})                             # double the permeance: less feed pressure
    assert t['params.design.RO_kW'] < base['params.design.RO_kW']
    assert t['params.design.total_kW'] < base['params.design.total_kW']
    assert t['continuous_kw.value'] < base['continuous_kw.value']
    t = books({'ro_rejection': 0.99})                            # tighter rejection: half the permeate salt
    c = Decimal('20') / Decimal('58.44')
    rec = upw / (upw + r['IA-UPW-REJ'])
    dpi = UP.osmotic_bar(c, rec, Decimal('0.99'), Decimal('298.15'))
    assert abs(Decimal(str(t['params.design.EDI_A']))
               - Decimal(str(base['params.design.EDI_A'])) / 2) < Decimal('1e-12')
    assert abs(t['params.design.feed_bar'] - float(Decimal('20') / Decimal('3') + dpi)) < Decimal('0.001')
    t = books({'edi_CE': 0.2})                                   # double the current efficiency: half the amps
    assert abs(Decimal(str(t['params.design.EDI_A']))
               - Decimal(str(base['params.design.EDI_A'])) / 2) < Decimal('1e-12')
    t = books({'upw_uv_W': 30.0})                                # double the lamp: + 15 W on the total
    assert abs(Decimal(str(t['params.design.total_kW'])) - Decimal(str(base['params.design.total_kW']))
               - Decimal('0.015')) < Decimal('1e-12')


def test_bridge_contracts():
    """No driver payload records nothing; a seed without the graph duty edges
    records nothing (the v1 r() reads would KeyError - the port fails soft)."""
    b = run({})
    assert b.computed == {}
    b = load(REF_GRAPH)
    b.data['edges'] = [e for e in b.data['edges'] if e['stream_id'] != 'IA-UPW-REJ']
    b.edges.pop('IA-UPW-REJ')
    UP.upw_polish(b, INPUTS)
    assert b.computed == {}


def test_topology_assert_fires():
    """A seed carrying an SQ heat edge the Rev AC graph retired fails loudly
    (builder topology, not this family's write)."""
    b = load(REF_GRAPH)
    clone = json.loads(json.dumps(next(e for e in committed()['edges']
                                       if e['stream_id'] == 'SF-BMED_UPW_POLISH')))
    clone['stream_id'], clone['from_unit_id'], clone['to_unit_id'] = \
        'SQ-BMED_UPW_POLISH', 'BMED_UPW_POLISH', 'HEAT_SINK'
    b.data['edges'].append(clone)
    b.edges['SQ-BMED_UPW_POLISH'] = clone
    try:
        UP.upw_polish(b, INPUTS)
    except AssertionError:
        pass
    else:
        raise SystemExit('the retired-SQ-edge assert did not fire')


def test_determinism_two_runs_byte_identical():
    assert render(run()) == render(run())


def test_provenance_rows():
    b = run()
    for (kind, uid, path), (value, prov) in b.computed.items():
        assert prov.stage == 'sizing_upw_polish' and prov.basis
        assert prov.ref == 'A-M-176'


def test_function_module_grid_purity():
    """The engine module holds no float literals and no I/O (the lint's rule)."""
    tree = ast.parse(inspect.getsource(UP))
    floats = [n.lineno for n in ast.walk(tree)
              if isinstance(n, ast.Constant) and isinstance(n.value, float)]
    opens = [n.lineno for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'open']
    assert floats == [] and opens == []
