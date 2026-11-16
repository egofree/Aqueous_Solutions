"""engine v2: the h2_purifier-family acceptance (the golden-value proof).

Reference writer: flow_graph/param/h2_purifier.py `--write` (ledger row
`sizing_h2_purifier`, section B - the X-MFG-39 H2 purifier bed train, A-M-168).
The committed graph carries every field the family stamps; the proofs:

- exact change set: the family's overlay equals the hand-enumerated
  specification (16 params.design fields, 2 continuous_kw fields, the size_mm
  book, 2 edge rate re-rates), and a strict whole-model walk (nodes and edges,
  same JSON types) proves nothing else moved;
- golden equality: every changed field equals the committed golden, numbers
  quantised to the golden's decimals (exact repr equality, zero enumerated
  drift) - including the raw-float books the family ported as v1 float books
  (the foundry precedent);
- the mol/mass audit books re-derived on exact Decimal arithmetic: the mol
  book, the water and sieve loads, the guard charge and the TSA volume, with
  the integer identities the drivers fix (sieve = water x 10, guard = HCl x
  900 at the committed drivers);
- grid spot-checks: the 300 mm minimum bed length floor, the 0.25 L tube
  switch (DN25/DN50), the duplicated-bed count, the envelope size_mm;
- the driver-tamper table: the ppmv, GHSV, guard-interval and cycle drivers
  move the books through the registered function as the exact chain predicts;
- the bridge contracts: no driver payload records nothing; a seed without the
  feed edges records nothing; the S49 fallback sizes off S49; the IA-H2P-H2O
  topology assert fires on a seed without the condensate edge;
- determinism: two runs, byte-identical;
- purity: no float literals and no I/O in the family module.
"""
import ast
import inspect
import json
import os
from decimal import Decimal

from flow_graph.v2.functions import h2_purifier as HP
from flow_graph.v2.graph_io import bytes as render, load

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')
DRIVERS = os.path.join(ROOT, 'flow_graph', 'param', 'drivers.json')
INPUTS = {'drivers': json.load(open(DRIVERS))}

# The change-set specification: every (unit, field path) the family writes.
EXPECTED_FIELDS = [
    ('H2_DRYER', 'params.design.H2_kg_d'), ('H2_DRYER', 'params.design.Nm3_h'),
    ('H2_DRYER', 'params.design.O2_mol_d'), ('H2_DRYER', 'params.design.water_kg_d'),
    ('H2_DRYER', 'params.design.HCl_kg_d'), ('H2_DRYER', 'params.design.guard_kg'),
    ('H2_DRYER', 'params.design.sieve_kg'), ('H2_DRYER', 'params.design.beds'),
    ('H2_DRYER', 'params.design.regen_W'), ('H2_DRYER', 'params.design.loss_W'),
    ('H2_DRYER', 'params.design.insulation_mm'), ('H2_DRYER', 'params.design.kW'),
    ('H2_DRYER', 'params.design.D_mm'), ('H2_DRYER', 'params.design.H_mm'),
    ('H2_DRYER', 'params.design.T_C'), ('H2_DRYER', 'params.design.wall_mm'),
    ('H2_DRYER', 'continuous_kw.value'), ('H2_DRYER', 'continuous_kw.note'),
    ('H2_DRYER', 'params.size_mm'),
]
EXPECTED_EDGES = [
    ('SF-H2_DRYER', 'rate'), ('IA-H2P-H2O', 'rate'),
]
DESIGN_KEYS = [p.split('.', 2)[2] for u, p in EXPECTED_FIELDS if '.design.' in p]


def run(inputs=None):
    b = load(REF_GRAPH)
    HP.h2_purifier_beds(b, inputs if inputs is not None else INPUTS)
    return b


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
    """Paths where the rendered model differs from the committed graph beyond
    the expected change set: strict (same JSON types) everywhere except the
    enumerated fields, where equality at the golden's decimals holds.
    Provenance rows, added by the serializer on touched objects, are excluded."""
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


def committed():
    with open(REF_GRAPH, encoding='utf-8') as f:
        return json.load(f)


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


def test_integer_books_keep_their_json_types():
    """The integer books stay JSON integers (the v1 round()/driver passthrough
    semantics): bed lengths, counts, the envelope mm and size_mm."""
    b = run()
    out = json.loads(render(b))
    node = next(n for n in out['nodes'] if n['unit_id'] == 'H2_DRYER')
    d = node['params']['design']
    assert type(d['insulation_mm']) is int
    for bed in d['beds'].values():
        assert type(bed['L_mm']) is int and type(bed['count']) is int
    assert type(d['D_mm']) is int and type(d['H_mm']) is int and type(d['kW']) is float
    assert all(type(x) is int for x in node['params']['size_mm'])
    assert node['continuous_kw']['value'] == 0.0198


def test_mol_and_mass_books_on_exact_decimal():
    """The audit books re-derived as exact Decimal arithmetic, independent of
    the float-replica stamps: the mol book, the water and sieve loads, the
    guard charge and the TSA volume, with the integer identities the committed
    drivers fix (sieve = water x 10; guard = HCl x 900)."""
    feed = next(e for e in committed()['edges'] if e['stream_id'] == 'IA-HDR-H2-02')
    rate = Decimal(str(feed['rate']['value']))
    n = HP.mol_book(rate)                                        # mol/d, exact
    assert n == Decimal('1.103286') / Decimal('2.016') * 1000
    o2 = n * Decimal('1000') / Decimal('1000000')                # 1000 ppmv driver
    w = o2 * 2 * Decimal('18.015') / 1000                        # kg/d, 2 H2O per O2
    hcl = n / Decimal('1000000') * Decimal('36.461') / 1000
    assert (w * Decimal('8') / 24 / Decimal('0.1') * Decimal('3')) == w * 10        # the integer identity
    assert (hcl * Decimal('90') / Decimal('0.1')) == hcl * 900                      # the integer identity
    b = run()
    sieve = Decimal(str(b.computed[('node', 'H2_DRYER', 'params.design.sieve_kg')][0]))
    guard = Decimal(str(b.computed[('node', 'H2_DRYER', 'params.design.guard_kg')][0]))
    assert abs(sieve - w * 10) < Decimal('1e-12')
    assert abs(guard - hcl * 900) < Decimal('1e-12')
    tsa = Decimal(str(b.computed[('node', 'H2_DRYER', 'params.design.beds')][0]['TSA']['V_L']))
    assert abs(tsa - w * 10 / Decimal('0.7')) < Decimal('1e-12')
    # the regeneration energy: sieve + steel sensible + water desorption per cycle
    steel = Decimal('3141592653589793') / Decimal('10') ** 15 * Decimal('60.3') / 1000 * Decimal('0.3') \
        * Decimal('0.0039') * 8000
    q_kJ = (w * 10 * Decimal('0.92') * 225 + steel * Decimal('0.5') * 225) / 1000 + w * Decimal('8') / 24 * 2500
    regen = q_kJ * 1000 / 86400 * 3
    got = Decimal(str(b.computed[('node', 'H2_DRYER', 'params.design.regen_W')][0]))
    assert abs(regen - got) < Decimal('1e-12')
    kw = b.computed[('node', 'H2_DRYER', 'params.design.kW')][0]
    assert kw == 0.0198 and b.computed[('node', 'H2_DRYER', 'continuous_kw.value')][0] == 0.0198


def test_grid_spot_checks():
    """The bed geometry grid: the 300 mm minimum length floor holds for every
    bed (the TSA length book is under it), the 0.25 L tube switch sets the DN
    pair, the beds are duplicated, and the envelope closes."""
    b = run()
    beds = b.computed[('node', 'H2_DRYER', 'params.design.beds')][0]
    assert list(beds) == ['deoxo', 'guard', 'TSA']               # the serialized key order
    for bed, row in beds.items():
        assert row['L_mm'] == 300 and row['count'] == 2          # the minimum-length floor, duplicated beds
        assert row['tube'] == ('DN50 Sch 40 316L' if bed == 'TSA' else 'DN25 Sch 40 316L')
    assert beds['TSA']['V_L'] > 0.25 > beds['deoxo']['V_L']      # the tube switch driver
    assert beds['guard']['V_L'] == 0.05                          # the minimum-volume floor
    assert b.computed[('node', 'H2_DRYER', 'params.size_mm')][0] == [600, 400, 1000]
    assert b.computed[('node', 'H2_DRYER', 'params.design.insulation_mm')][0] == 38   # the ASTM_C680 ladder
    note = b.computed[('node', 'H2_DRYER', 'continuous_kw.note')][0]
    assert note == 'X-MFG-39 (A-M-168): TSA regeneration 0.6 W / 0.7 + half the insulated loss.'


def test_insulation_ladder_table():
    """The ASTM_C680 thickness ladder is walked in order until the surface is
    at or under 50 C: data rows over the pure derivation (OD 60.3, L 0.3 m)."""
    table = [(100, 13), (150, 25), (200, 38), (250, 38)]         # (T_C -> thk_mm)
    for t_c, thk in table:
        ins, loss = HP.insulated_cylinder(HP.fl(t_c), HP.fl('60.3'), HP.fl('0.3'))
        assert ins == thk and loss > 0
    # the committed bed: 250 C stops at the 38 mm rung, 37.98 W while hot
    ins, loss = HP.insulated_cylinder(HP.fl('250'), HP.fl('60.3'), HP.fl('0.3'))
    assert ins == 38 and abs(Decimal(str(loss)) - Decimal('37.98279150873541')) < Decimal('1e-9')


def test_driver_tamper_table():
    """The drivers move the books through the registered function as the exact
    chain predicts: the ppmv pair, the GHSV, the guard interval and the cycle.
    Expected books come from the exact chain - never scaled from the stored
    floats (the quantise of a doubled chain is not the doubled quantise)."""
    def books(tamper):
        drv = json.loads(json.dumps(INPUTS['drivers']))
        for key, val in tamper.items():
            drv[key]['value'] = val
        bb = run({'drivers': drv})
        return {p: bb.computed[('node', 'H2_DRYER', p)][0]
                for _u, p in EXPECTED_FIELDS if '.design.' in p}
    rate = Decimal('1.103286')
    n = HP.mol_book(rate)
    w = n * 1000 / Decimal('1000000') * 2 * Decimal('18.015') / 1000          # at the 1000 ppmv driver
    hcl = n / Decimal('1000000') * Decimal('36.461') / 1000
    dex = lambda x: Decimal(str(x))
    base = books({})
    # O2 ppmv doubled: the O2 book doubles, the deoxo water doubles, the sieve doubles
    t = books({'h2p_o2_ppmv': 2000.0})
    assert abs(dex(t['params.design.O2_mol_d']) - dex(base['params.design.O2_mol_d']) * 2) < Decimal('1e-9')
    assert abs(dex(t['params.design.water_kg_d']) - w * 2) < Decimal('1e-9')
    assert abs(dex(t['params.design.sieve_kg']) - w * 2 * 10) < Decimal('1e-9')
    # the guard interval doubled: the guard charge doubles, the TSA and deoxo are untouched
    t = books({'h2p_guard_days': 180.0})
    assert abs(dex(t['params.design.guard_kg']) - hcl * 1800) < Decimal('1e-12')
    assert t['params.design.sieve_kg'] == base['params.design.sieve_kg']
    assert t['params.design.O2_mol_d'] == base['params.design.O2_mol_d']
    # the space velocity halved: the deoxo volume doubles
    t = books({'h2p_deoxo_ghsv_h': 2500.0})
    nm3 = dex(base['params.design.Nm3_h'])
    assert abs(dex(t['params.design.beds']['deoxo']['V_L']) - nm3 / 2500 * 1000) < Decimal('1e-9')
    # the cycle doubled: the sieve doubles (w x cycle/24 x 30)
    t = books({'h2p_cycle_h': 16.0})
    assert abs(dex(t['params.design.sieve_kg']) - w * 20) < Decimal('1e-9')


def test_bridge_no_drivers_records_nothing():
    """The bridge solve / check carry no driver payload: the family records
    nothing and the seed stands."""
    b = run({})
    assert b.computed == {}


def test_bridge_feed_guards_and_s49_fallback():
    """Without any H2 feed edge the family records nothing; with only S49 the
    fallback sizes the train off S49 (the v1 read-back)."""
    b = load(REF_GRAPH)
    del b.edges['IA-HDR-H2-02']
    del b.edges['S49']
    HP.h2_purifier_beds(b, INPUTS)
    assert b.computed == {}
    b = load(REF_GRAPH)
    del b.edges['IA-HDR-H2-02']
    HP.h2_purifier_beds(b, INPUTS)
    assert b.computed[('node', 'H2_DRYER', 'params.design.H2_kg_d')][0] == 4.8   # the S49 pool rate
    assert b.computed[('edge', 'IA-H2P-H2O', 'rate')][0]['value'] == 0.0         # S49 carries no water book


def test_topology_asserts_fire():
    """The IA-H2P-H2O condensate edge is builder topology the seed must carry:
    a seed without it fails loudly instead of writing."""
    b = load(REF_GRAPH)
    b.data['edges'] = [e for e in b.data['edges'] if e['stream_id'] != 'IA-H2P-H2O']
    b.edges.pop('IA-H2P-H2O')
    try:
        HP.h2_purifier_beds(b, INPUTS)
    except AssertionError:
        pass
    else:
        raise SystemExit('the missing-condensate-edge assert did not fire')


def test_seed_note_preserved_on_the_feed_edge():
    """The SF edge re-rate replaces the value only: the seed note, unit and
    status the v1 writer preserved stay in the book."""
    b = run()
    book = b.computed[('edge', 'SF-H2_DRYER', 'rate')][0]
    seed = next(e for e in committed()['edges'] if e['stream_id'] == 'SF-H2_DRYER')['rate']
    assert book['value'] == 0.0198 and book['note'] == seed['note'] and book['unit'] == seed['unit'] \
        and book['status'] == seed['status']
    water = b.computed[('edge', 'IA-H2P-H2O', 'rate')][0]
    assert water['value'] == 0.0 and water['note'].startswith('X-PAR-15:')
    assert water['unit'] == 'kg/d' and water['status'] == 'study'


def test_determinism_two_runs_byte_identical():
    assert render(run()) == render(run())


def test_provenance_rows():
    b = run()
    for (kind, uid, path), (value, prov) in b.computed.items():
        assert prov.stage == 'sizing_h2_purifier' and prov.basis
        assert prov.ref == 'A-M-168'


def test_function_module_grid_purity():
    """The engine module holds no float literals and no I/O (the lint's rule)."""
    tree = ast.parse(inspect.getsource(HP))
    floats = [n.lineno for n in ast.walk(tree)
              if isinstance(n, ast.Constant) and isinstance(n.value, float)]
    opens = [n.lineno for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'open']
    assert floats == [] and opens == []
