"""engine v2: the house_scrubbers-family acceptance (the golden-value proof).

Reference writer: flow_graph/param/house_scrubbers.py `--write` (ledger row
`sizing_house_scrubbers`, section B - X-PAR-03 packed-column sizing on the four
house scrubbers, A-M-164). The committed graph carries every field the family
stamps; the proofs:

- exact change set: the family's overlay equals the hand-enumerated
  specification (17 fields per unit x 4 units, 4 SF re-rates), and a strict
  whole-model walk (nodes and edges, same JSON types) proves nothing else
  moved;
- golden equality: every changed field equals the committed golden, numbers
  quantised to the golden's decimals (exact repr equality, zero enumerated
  drift);
- the packing chain re-derived on exact Decimal arithmetic (the module runs
  exact books throughout): the flood velocity, the flooding diameter, the
  packed bed ln(1/(1-removal)), the minimum-wetting liquid (the pi-cancelling
  identity L = MWR a Q / (f u_f)), the pressure drop and the fan/pump books;
- grid spot-checks: the 50 mm vessel-diameter grid, the 300 mm bed floor,
  integer mm books with their JSON types;
- the driver-tamper table: the removal target, the fan efficiency, the gas
  density and the diameter floor move the books as the exact chain predicts;
- the bridge contracts: no driver payload records nothing; drivers without
  the site profile record nothing (the pump needs the site gravity);
- the topology contract: a seed carrying an SQ heat edge the Rev AC graph
  retired fails loudly;
- determinism: two runs, byte-identical;
- purity: no float literals and no I/O in the family module.

Integer-scale table (half-even throughout, Python round()'s tie rule): design
books 4 dp (gas, Q, u_flood, liquid, dP, fan, pump, kW); bed height, vessel
diameter (50 mm ceiling grid), vessel height and size_mm integer books; duty,
material and the size note verbatim texts.
"""
import ast
import inspect
import json
import os
from decimal import Decimal

from flow_graph.v2.functions import house_scrubbers as HS
from flow_graph.v2.graph_io import bytes as render, load

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')
DRIVERS = os.path.join(ROOT, 'flow_graph', 'param', 'drivers.json')
INPUTS = {'drivers': json.load(open(DRIVERS)),
          'site_profile': json.load(open(os.path.join(ROOT, 'flow_graph', 'param', 'sites', 'baseline.json')))}
UNITS = ('ALK_SCRUBBER', 'ACID_POLISH_SCRUB', 'NOX_SCRUB', 'MET_SCRUB')
DESIGN_KEYS = ('duty', 'gas_kg_d', 'Q_m3_s', 'u_flood_m_s', 'D_mm', 'packed_mm', 'H_mm', 'recirc_m3_h',
               'dP_Pa', 'fan_W', 'pump_W', 'kW', 'material')

# The change-set specification: every (unit, field path) the family writes.
EXPECTED_FIELDS = [(u, 'params.design.' + k) for u in UNITS for k in DESIGN_KEYS] + [
    (u, field) for u in UNITS
    for field in ('params.size_mm', 'params.size_note', 'continuous_kw.value', 'continuous_kw.note')]
EXPECTED_EDGES = [('SF-' + u, 'rate') for u in UNITS]

PI = Decimal('3141592653589793') / Decimal('10') ** 15
G = Decimal('9.80665')                                       # the baseline profile gravity (v1 SITE.g())
qi_d = lambda x: int(x.quantize(Decimal(1), rounding='ROUND_HALF_EVEN'))   # the v1 round() half-even book


def run(inputs=None):
    b = load(REF_GRAPH)
    HS.house_scrubbers(b, inputs if inputs is not None else INPUTS)
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


def gas_census(unit, edges):
    """The graph gas inflow of a unit (kg/d): the mass-layer G and L/G phase
    edges in, exactly summed."""
    return sum((Decimal(str(e['rate']['value'] or 0)) for e in edges
                if e['to_unit_id'] == unit and 'mass' in (e.get('layers') or [])
                and e['phase'].startswith(('G', 'L/G'))), Decimal(0))


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


def test_packing_chain_on_exact_books():
    """The scrubber chain re-derived independently as exact Decimal books: the
    flood velocity, the flooding diameter, the packed bed, the pi-cancelling
    minimum-wetting identity, the pressure drop and the fan/pump books."""
    b = run()
    rho_g = Decimal('1.2')
    uf = Decimal('0.07') * ((Decimal(1000) - rho_g) / rho_g).sqrt()      # 2.01951314264932019...
    z = Decimal('0.5') * (Decimal(1) / Decimal('0.01')).ln()             # HTU x ln(1/(1 - 0.99))
    d_p = Decimal('400') * z + Decimal('250')
    assert HS.flood_velocity(Decimal('0.07'), Decimal(1000), rho_g) == uf
    assert uf.quantize(Decimal('0.0001')) == Decimal('2.0195')
    assert z.quantize(Decimal('0.0001')) == Decimal('2.3026')
    assert d_p.quantize(Decimal('0.001')) == Decimal('1171.034')         # the unit-shared dP book
    for u in UNITS:
        gas = gas_census(u, committed()['edges'])
        q_gas = gas / rho_g / Decimal('86400')
        d_m = max((4 * q_gas / (PI * Decimal('0.7') * uf)).sqrt(), Decimal('0.2'))
        liq = Decimal('0.08') * Decimal('190') * PI * d_m * d_m / 4     # the module's own formula
        fan = q_gas * d_p / Decimal('0.5')
        pump = liq / Decimal('3600') * 1000 * G * Decimal('10') / Decimal('0.4')
        got = {k.split('.', 2)[2]: b.computed[('node', u, k)][0]
               for k in ('params.design.gas_kg_d', 'params.design.Q_m3_s', 'params.design.D_mm',
                         'params.design.packed_mm', 'params.design.recirc_m3_h', 'params.design.dP_Pa',
                         'params.design.fan_W', 'params.design.pump_W', 'params.design.kW')}
        assert abs(Decimal(str(got['gas_kg_d'])) - gas.quantize(Decimal('0.0001'))) < Decimal('1e-9'), u
        assert got['Q_m3_s'] == float(q_gas.quantize(Decimal('0.0001'), rounding='ROUND_HALF_EVEN')), u
        assert got['recirc_m3_h'] == float(liq.quantize(Decimal('0.0001'), rounding='ROUND_HALF_EVEN')), u
        assert got['dP_Pa'] == float(d_p.quantize(Decimal('0.0001'), rounding='ROUND_HALF_EVEN')), u
        assert abs(Decimal(str(got['fan_W'])) - fan.quantize(Decimal('0.0001'))) < Decimal('1e-9'), u
        assert abs(Decimal(str(got['pump_W'])) - pump.quantize(Decimal('0.0001'))) < Decimal('1e-9'), u
        assert got['kW'] == float(((fan + pump) / 1000).quantize(Decimal('0.0001'),
                                                                 rounding='ROUND_HALF_EVEN')), u
        d_mm = int((d_m * 1000 / 50).to_integral_value(rounding='ROUND_CEILING')) * 50
        assert got['D_mm'] == d_mm and d_mm % 50 == 0                    # the 50 mm envelope grid
        assert got['packed_mm'] == qi_d(z * 1000) == 2303                # half-even of 2302.585...
    # the unit-shared books are identical; the gas census sets the column size
    alk = b.computed[('node', 'ALK_SCRUBBER', 'params.design.gas_kg_d')][0]
    acid = b.computed[('node', 'ACID_POLISH_SCRUB', 'params.design.gas_kg_d')][0]
    nox = b.computed[('node', 'NOX_SCRUB', 'params.design.gas_kg_d')][0]
    met = b.computed[('node', 'MET_SCRUB', 'params.design.gas_kg_d')][0]
    assert alk == acid == 37509.8546 and nox == 283.4578 and met == 71604.0


def test_grid_spot_checks_and_texts():
    """Integer mm books with their JSON types, the verbatim texts, and the
    envelope closure."""
    b = run()
    out = json.loads(render(b))
    by_id = {n['unit_id']: n for n in out['nodes']}
    for u in UNITS:
        d = by_id[u]['params']['design']
        assert type(d['D_mm']) is int and type(d['packed_mm']) is int and type(d['H_mm']) is int
        assert d['duty'] == HS.UNITS[u] and d['material'] == HS.MATERIAL
        assert by_id[u]['params']['size_note'] == HS.SIZE_NOTE
        assert all(type(x) is int for x in by_id[u]['params']['size_mm'])
        size = by_id[u]['params']['size_mm']
        assert size == [d['D_mm'] + 400, d['D_mm'] + 400, d['H_mm'] + 300]   # the envelope closure
        assert by_id[u]['continuous_kw']['value'] == d['kW']
        assert by_id[u]['continuous_kw']['note'].startswith('X-PAR-03 house scrubber')
    assert by_id['ALK_SCRUBBER']['continuous_kw']['note'] == \
        'X-PAR-03 house scrubber (flow_graph/param/house_scrubbers.py, A-M-164). Fan 847 W, pump 265 W.'
    assert by_id['NOX_SCRUB']['continuous_kw']['note'].endswith('Fan 6 W, pump 33 W.')
    assert by_id['MET_SCRUB']['params']['size_mm'] == [1200, 1200, 4103]
    feed = b.computed[('edge', 'SF-ALK_SCRUBBER', 'rate')][0]
    seed = next(e for e in committed()['edges'] if e['stream_id'] == 'SF-ALK_SCRUBBER')['rate']
    assert feed['value'] == 1.1122 and feed['note'] == HS.TAG + '.'          # note replaced, unit/status kept
    assert feed['unit'] == seed['unit'] and feed['status'] == seed['status']


def test_driver_tamper_table():
    """The drivers move the books through the registered function as the exact
    chain predicts: the removal target, the fan efficiency, the gas density
    and the packing-diameter floor. Expected books are quantised from the
    exact chain at the stored decimals - never scaled from the stored floats
    (the quantise of a doubled chain is not the doubled quantise)."""
    z99 = (Decimal(1) / Decimal('0.01')).ln() / 2                # the packed bed, 2.302585... m
    q4 = lambda x: float(x.quantize(Decimal('0.0001'), rounding='ROUND_HALF_EVEN'))
    d_p0 = Decimal('400') * z99 + 250                            # the unit-shared dP book
    def books(tamper, unit='ALK_SCRUBBER'):
        drv = json.loads(json.dumps(INPUTS['drivers']))
        for key, val in tamper.items():
            drv[key]['value'] = val
        bb = run({'drivers': drv, 'site_profile': INPUTS['site_profile']})
        return {p: bb.computed[('node', unit, p)][0]
                for p in ('params.design.packed_mm', 'params.design.dP_Pa', 'params.design.fan_W',
                          'params.design.D_mm', 'params.design.u_flood_m_s', 'params.design.kW')}
    base = books({})
    rho_g = Decimal('1.2')
    uf = Decimal('0.07') * ((Decimal(1000) - rho_g) / rho_g).sqrt()
    gas = gas_census('ALK_SCRUBBER', committed()['edges'])
    q_gas = gas / rho_g / Decimal('86400')
    z = Decimal('0.5') * (Decimal(1) / Decimal('0.001')).ln()    # removal 0.999 -> ln(1000)
    t = books({'hs_removal': 0.999})
    assert t['params.design.packed_mm'] == qi_d(z * 1000)        # 3454, the taller bed
    assert t['params.design.dP_Pa'] == q4(Decimal('400') * z + 250)
    assert t['params.design.fan_W'] == q4(q_gas * (Decimal('400') * z + 250) / Decimal('0.5'))
    assert t['params.design.fan_W'] > base['params.design.fan_W']       # the taller bed, the same gas
    t = books({'hs_fan_eff': 0.25})                              # half the efficiency: the fan doubles
    assert t['params.design.fan_W'] == q4(q_gas * d_p0 / Decimal('0.25'))
    t = books({'hs_Cs_flood_m_s': 0.14})                         # double Cs: u_f doubles
    assert t['params.design.u_flood_m_s'] == q4(Decimal('0.14') * ((Decimal(1000) - rho_g) / rho_g).sqrt())
    t = books({'vs_d_over_dp': 16.0})                            # the diameter floor doubles past flooding
    assert t['params.design.D_mm'] == max(base['params.design.D_mm'], 400)   # 25 mm x 16 = 400 mm floor
    t = books({'GAS.scrubbing-headers-train.scrubbing.hs_fixed_dP_Pa': 500.0})
    assert t['params.design.dP_Pa'] == q4(Decimal('400') * z99 + 500)
    assert t['params.design.kW'] > base['params.design.kW']


def test_bridge_contracts():
    """No driver payload records nothing; drivers without the site profile
    record nothing (the pump arithmetic needs the site gravity)."""
    b = run({})
    assert b.computed == {}
    b = run({'drivers': INPUTS['drivers']})
    assert b.computed == {}


def test_topology_assert_fires():
    """A seed carrying an SQ heat edge the Rev AC graph retired fails loudly
    (builder topology, not this family's write)."""
    b = load(REF_GRAPH)
    clone = json.loads(json.dumps(next(e for e in committed()['edges']
                                       if e['stream_id'] == 'SF-ALK_SCRUBBER')))
    clone.update(stream_id='SQ-ALK_SCRUBBER', from_unit_id='ALK_SCRUBBER', to_unit_id='HEAT_SINK',
                 layers=['energy'])
    b.data['edges'].append(clone)
    b.edges['SQ-ALK_SCRUBBER'] = clone
    try:
        HS.house_scrubbers(b, INPUTS)
    except AssertionError:
        pass
    else:
        raise SystemExit('the retired-SQ-edge assert did not fire')


def test_determinism_two_runs_byte_identical():
    assert render(run()) == render(run())


def test_provenance_rows():
    b = run()
    for (kind, uid, path), (value, prov) in b.computed.items():
        assert prov.stage == 'sizing_house_scrubbers' and prov.basis
        assert prov.ref == 'A-M-164'


def test_function_module_grid_purity():
    """The engine module holds no float literals and no I/O (the lint's rule)."""
    tree = ast.parse(inspect.getsource(HS))
    floats = [n.lineno for n in ast.walk(tree)
              if isinstance(n, ast.Constant) and isinstance(n.value, float)]
    opens = [n.lineno for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'open']
    assert floats == [] and opens == []
