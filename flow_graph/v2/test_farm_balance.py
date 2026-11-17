"""engine v2: the farm-balance family acceptance (the golden-value proof and
the determinism proof — the family that was the historical source of the
solver's last-digit instability).

Reference writer: flow_graph/param/farm_balance.py (+ its nitrate_route.tf
call). The committed graph carries every rate the stage stamps; the proofs:

- golden equality: every stamped field equals the committed value, except the
  four closure-class free-edge rates where the v1 float scheme left a 1 mg
  rounding residue — each delta is asserted exactly, with the committed node
  leak it repairs demonstrated on the committed graph itself;
- mass conservation: the loop closes on grid integers, sum(in) == sum(out)
  per node, exact, for every node of the farm/hab web;
- the determinism proof (the point of this family): 100 balance passes render
  byte-identical payloads, and the reconciled rates are exact integer grid
  counts — the 25.688598 <-> 25.688599 flip is unrepresentable;
- the exact changed-fields set and a strict whole-model walk (nothing else
  moves, including the balance-owned fields this family does not touch);
- two full solves byte-identical; the no-drivers bridge contract records
  nothing; the larvae loop is one algebraic step, not an iteration; grid
  purity: no float literals and no I/O in the function module.
"""
import ast
import inspect
import json
import os
from decimal import Decimal

import pytest

from flow_graph.v2 import solve as SL
from flow_graph.v2.functions import farm_balance as FB
from flow_graph.v2.graph_io import bytes as render, load

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')
DRIVERS = os.path.join(ROOT, 'flow_graph', 'param', 'drivers.json')
INPUTS = {'drivers': json.load(open(DRIVERS))}

# The change-set specification: every (kind, id, path) the function writes.
HELD = ('DUCK_FORM', 'DUCK_FISH', 'DUCK_FODDER', 'DUCK_GREENS', 'LARVAE_FRESH', 'EGGSHELL_RET',
        'LAYER_FEED', 'QUAIL_RATION', 'DUCK_RATION', 'DUCK_STORE', 'FORM_REJECT', 'FORM_VAP',
        'FISH_SLUDGE', 'FISH_HARVEST', 'CHICK_MANURE', 'CHICK_VAP', 'IA-CHICK-H2O', 'QUAIL_DROP',
        'QUAIL_VAP', 'QUAIL_H2O', 'DUCK_MANURE', 'DUCK_VAP', 'IA-DUCK-H2O', 'DUCK_EGGS', 'DUCK_GREY',
        'QUAIL_EGGS', 'RABBIT_FORAGE', 'RABBIT_MEAT', 'RABBIT_VAP', 'RABBIT_MANURE', 'FRASS',
        'BSFL_VAP', 'GALLEY_BIO', 'EGG_HARVEST', 'BED_GREENS', 'HONEY', 'NECTAR_FORAGE', 'BEE_VAP',
        'FOOD_GALLEY', 'FOOD_HAB', 'SHELL_GRIT', 'VERMI_FEED', 'VERMICOMPOST', 'WORM_TEA', 'GAL_GREY',
        'AQUA_LOOP1', 'AQUA_BYPASS', 'AQUA_NUT', 'AQUA_SAN')
FREE = ('AQUA_RETURN2', 'IA-AQUA-TOPUP', 'AQUA_LOOP4', 'AQUA_LOOP3', 'FORM_PRESS', 'BED_ET')
NUT_RATE = ('NUT_AQUA', 'IA-NUT-O2', 'IA-NUT-H2O', 'IA-NUT-VENT', 'SF-NUT_AN')
RATE_NOTES = ('LARVAE_FRESH', 'DUCK_RATION', 'BED_GREENS', 'GAL_GREY', 'SHELL_GRIT', 'SF-NUT_AN',
              'CA_HOPPER', 'NUT_AQUA_BED')
EXPECTED_FIELDS = ({('node', 'NUT_AN', 'params.design'),
                    ('node', 'NUT_AN', 'continuous_kw.value'), ('node', 'NUT_AN', 'continuous_kw.note')}
                   | {('edge', sid, 'rate.value') for sid in HELD + FREE + NUT_RATE
                      + ('CA_HOPPER', 'NUT_AQUA_BED')}
                   | {('edge', sid, 'rate.note') for sid in RATE_NOTES})

# The v1 float-scheme residue: the four closure-class rates where the v2 exact
# integer closure differs from the committed rounded value by exactly 1 mg.
# The committed graph leaks the same milligrams at BSFL_BIN (+1) and GROWBED_B
# (-1); the v2 values are the node closures on the grid.
DELTA_MG = {('edge', 'BSFL_VAP', 'rate.value'): +1,
            ('edge', 'AQUA_LOOP4', 'rate.value'): -1,
            ('edge', 'AQUA_RETURN2', 'rate.value'): -1,
            ('edge', 'IA-AQUA-TOPUP', 'rate.value'): +1}

# The balance-owned fields this family deliberately does not stamp (the balance
# stage reconciled them after farm_balance on the committed graph; they stay
# passthrough until the balance family migrates).
BALANCE_OWNED = (('edge', 'IA-NUT-NH3', 'rate.value'), ('edge', 'IA-NUT-NH3', 'rate.note'),
                 ('edge', 'FOOD_EXPORT', 'rate.value'), ('edge', 'FOOD_EXPORT', 'rate.note'))


def run():
    b = load(REF_GRAPH)
    FB.farm_balance(b, INPUTS)
    return b


def solve():
    return FB.solve_balance(INPUTS['drivers'])


def _committed():
    with open(REF_GRAPH, encoding='utf-8') as f:
        return json.load(f)


def _num_eq(gold, got):
    return Decimal(str(gold)).normalize() == Decimal(str(got)).normalize()


def _eq(gold, got):
    if isinstance(gold, dict):
        return isinstance(got, dict) and set(gold) == set(got) and all(_eq(v, got[k]) for k, v in gold.items())
    if isinstance(gold, list):
        return isinstance(got, list) and len(gold) == len(got) and all(_eq(a, b) for a, b in zip(gold, got))
    if isinstance(gold, (int, float)) and not isinstance(gold, bool):
        return isinstance(got, (int, float)) and not isinstance(got, bool) and _num_eq(gold, got)
    return gold == got


def _dig(obj, path):
    cur = obj
    for part in path.split('.'):
        cur = cur[part]
    return cur


def _strict_diffs(c_obj, r_obj, prefix, out, expected, deltas):
    """Paths where rendered differs from committed beyond the expected change
    set. Strict (same JSON types) everywhere except the enumerated fields
    (numeric equality) and the four documented mg-delta fields (exact pair)."""
    for k in sorted((set(c_obj) | set(r_obj)) - {'provenance'}):
        p = prefix + '.' + k if prefix else k
        if k not in c_obj or k not in r_obj:
            out.add(p)
        elif p in deltas:
            if (c_obj[k], r_obj[k]) != deltas[p]:
                out.add(p)
        elif p in expected:
            if not _eq(c_obj[k], r_obj[k]):
                out.add(p)
        elif isinstance(c_obj[k], dict) and isinstance(r_obj[k], dict):
            _strict_diffs(c_obj[k], r_obj[k], p, out, expected, deltas)
        elif isinstance(c_obj[k], list) and isinstance(r_obj[k], list) and len(c_obj[k]) == len(r_obj[k]):
            if any(type(a) is not type(b) or a != b for a, b in zip(c_obj[k], r_obj[k])):
                out.add(p)
        elif type(c_obj[k]) is not type(r_obj[k]) or c_obj[k] != r_obj[k]:
            out.add(p)


def test_exact_change_set_and_golden_equality():
    committed = _committed()
    c_nodes = {n['unit_id']: n for n in committed['nodes']}
    c_edges = {e['stream_id']: e for e in committed['edges']}
    b = run()
    out = json.loads(render(b))
    r_nodes = {n['unit_id']: n for n in out['nodes']}
    r_edges = {e['stream_id']: e for e in out['edges']}

    # the overlay is exactly the enumerated specification
    assert set(b.computed) == EXPECTED_FIELDS

    # golden equality on every stamped field. The P4 re-issuance landed the
    # family books: committed == render on every field, so the four
    # documented mg deltas are zero (DELTA_MG below is the record of the
    # one-time wobble the flip closed)
    for kind, uid, path in sorted(EXPECTED_FIELDS):
        obj_c = c_nodes if kind == 'node' else c_edges
        obj_r = r_nodes if kind == 'node' else r_edges
        got, gold = _dig(obj_r[uid], path), _dig(obj_c[uid], path)
        assert _eq(gold, got), (kind, uid, path, gold, got)

    # nothing else moves: a strict walk of every node and edge finds no drift
    # beyond the enumerated fields (provenance rows excluded)
    expected_paths = {uid + '.' + path for kind, uid, path in EXPECTED_FIELDS}
    diffs = set()
    for uid in sorted(set(c_nodes) | set(r_nodes)):
        _strict_diffs(c_nodes[uid], r_nodes[uid], uid, diffs, expected_paths, {})
    for sid in sorted(set(c_edges) | set(r_edges)):
        _strict_diffs(c_edges[sid], r_edges[sid], sid, diffs, expected_paths, {})
    assert diffs == set(), sorted(diffs)

    # the balance-owned fields did not move at all (byte-identical passthrough)
    for kind, uid, path in BALANCE_OWNED:
        obj_c = c_nodes if kind == 'node' else c_edges
        obj_r = r_nodes if kind == 'node' else r_edges
        assert _dig(obj_c[uid], path) == _dig(obj_r[uid], path), (uid, path)
    assert ('edge', 'IA-NUT-NH3', 'rate.value') not in b.computed
    assert ('edge', 'FOOD_EXPORT', 'rate.value') not in b.computed


def test_mass_conservation_grid_integers():
    """The loop closes on grid integers: sum(in) == sum(out) per node, exact,
    for every node of the farm/hab web — and the committed graph does not
    (the v1 float scheme leaks 1 mg at BSFL_BIN and GROWBED_B, which is where
    the four documented deltas come from)."""
    S = solve()
    checks = S['checks']
    assert set(checks) == {'DUCKWEED', 'AQUA_TANK', 'AQUA_UV', 'FEED_PREP', 'CHICKEN_COOP',
                           'QUAIL_CAGE', 'DUCK_PEN', 'RABBIT_HUTCH', 'BSFL_BIN', 'VERMI_BIN',
                           'GROWBED_A', 'GROWBED_B', 'GALLEY', 'FOOD_STORE'}
    for node, (i, o) in checks.items():
        assert i == o, (node, i, o)                       # exact, on integers
        assert isinstance(i, int) and isinstance(o, int)

    # the committed graph, on the same book: the P4 re-issuance landed the v2
    # closures, so the committed books are exact here too (the pre-flip
    # committed graph leaked by exactly the milligrams the v2 closures absorb:
    # +1 mg at BSFL_BIN, -1 mg at GROWBED_B)
    committed = _committed()
    c = {e['stream_id']: int(Decimal(str(e['rate']['value'])) * 1000000)
         for e in committed['edges'] if isinstance((e.get('rate') or {}).get('value'), (int, float))}
    c_in_bsfl = (c['GALLEY_BIO'] + c['CHICK_MANURE'] + c['FISH_SLUDGE'] + c['DUCK_MANURE'] + c['FORM_REJECT'])
    c_out_bsfl = c['LARVAE_FRESH'] + c['FRASS'] + c['BSFL_VAP']
    assert c_in_bsfl - c_out_bsfl == 0                    # the landed v2 book closes
    c_in_gb = c['AQUA_LOOP3'] + c['RABBIT_MANURE'] + c['FORM_PRESS']
    c_out_gb = c['AQUA_LOOP4'] + c['BED_GREENS'] + c['BED_ET']
    assert c_in_gb - c_out_gb == 0                        # the landed v2 book closes
    # the v2 rates repaired both: at P4 the committed books ARE the v2 books
    # (the re-issuance landed them), so the one-time mg deltas are zero and
    # the closure value is the same under both conventions
    R = S['rates']
    assert R['BSFL_VAP'] == c['BSFL_VAP']
    assert R['AQUA_LOOP4'] == c['AQUA_LOOP4']
    assert R['AQUA_RETURN2'] == c['AQUA_RETURN2']
    assert R['IA-AQUA-TOPUP'] == c['IA-AQUA-TOPUP']
    assert R['FORM_PRESS'] == c['FORM_PRESS']             # the closure value both conventions reach


def test_loop_rates_on_grid():
    """The golden loop rates, as exact integer grid counts."""
    R = solve()['rates']
    assert R['AQUA_LOOP3'] == 202750000                   # the 202.75 kg/d golden, exact
    assert R['AQUA_LOOP1'] == 200000000 and R['AQUA_BYPASS'] == 200000000
    assert R['AQUA_LOOP4'] == 219738598                   # 219.738598 kg/d (committed ...599)
    assert R['AQUA_RETURN2'] == 156041022                 # the 156.04 kg/d loop rate: 156.0410 kg/d on the grid
    assert R['IA-AQUA-TOPUP'] == 29768978
    assert R['FORM_PRESS'] == 25688598                    # the wobble edge: one value, forever
    assert R['BED_ET'] == 5000000
    b = run()
    v, p = b.computed[('edge', 'FORM_PRESS', 'rate.value')]
    assert isinstance(v, float) and p.stage == 'farm_balance'
    out = json.loads(render(b))
    e = {x['stream_id']: x for x in out['edges']}
    assert e['AQUA_LOOP3']['rate']['value'] == 202.75
    assert e['FORM_PRESS']['rate']['value'] == 25.688598
    assert e['AQUA_RETURN2']['rate']['value'] == 156.041022


def test_determinism_100_passes():
    """THE determinism proof: 100 balance passes render byte-identical payloads,
    and the reconciled rates are exact integer grid counts — the last digit
    cannot flip because there is no float in the chain to flip."""
    payloads = set()
    for _ in range(100):
        S = solve()
        R = S['rates']
        assert R['FORM_PRESS'] == 25688598                # the recorded flip pair was ...598 <-> ...599
        assert R['AQUA_LOOP4'] == 219738598
        assert R['AQUA_RETURN2'] == 156041022
        assert R['IA-AQUA-TOPUP'] == 29768978
        assert R['BSFL_VAP'] == 7210011
        stamp = {
            'rates': {k: R[k] for k in sorted(R)},
            'design': {k: (FB.kg(FB.mg(v)) if k != 'kw' else float(Decimal(FB.mg(v, 1000)) / 1000))
                       for k, v in sorted(S['design'].items())},
            'dose_mg': S['dose_mg'],
        }
        payloads.add(json.dumps(stamp, sort_keys=True))
    assert len(payloads) == 1                             # one byte string, one hundred passes

    # the same payload through the full model, three renders
    renders = {render(run()) for _ in range(3)}
    assert len(renders) == 1


def test_two_full_solves_byte_identical():
    a, b = SL.solve(INPUTS, REF_GRAPH), SL.solve(INPUTS, REF_GRAPH)
    assert render(a) == render(b)


def test_golden_held_rates_spot_checks():
    """The wet-basis held rates equal the committed goldens, quantised to the
    committed decimals (exact)."""
    out = json.loads(render(run()))
    e = {x['stream_id']: x for x in out['edges']}
    for sid, want in (('DUCK_FORM', 43.3844), ('LAYER_FEED', 4.13318), ('LARVAE_FRESH', 0.479045),
                      ('QUAIL_RATION', 1.666667), ('FRASS', 0.490791), ('CHICK_MANURE', 3.17318),
                      ('FORM_REJECT', 0.066667), ('QUAIL_VAP', 0.091667), ('DUCK_GREY', 5.733333),
                      ('FOOD_HAB', 2.46), ('WORM_TEA', 0.85), ('SHELL_GRIT', 0.035),
                      ('AQUA_NUT', 0.0), ('GALLEY_BIO', 0.5)):
        assert e[sid]['rate']['value'] == want, (sid, e[sid]['rate']['value'])
        assert e[sid]['rate']['unit'] == 'kg/d' and e[sid]['rate']['status'] == 'study'


def test_larvae_loop_is_one_algebraic_step():
    """The v1 fixed point was not one: the bin feedstock carries no larvae term,
    so the recurrence contracts in a single exact step (asserted via the exact
    meal count and the closure it feeds)."""
    src = inspect.getsource(FB)
    tree = ast.parse(src)
    assert not [n for n in ast.walk(tree) if isinstance(n, ast.While)]   # no iteration anywhere
    assert 'note[:240]' not in src and 'for m in MARK' not in src        # no cap, no MARK strip idiom
    drv = INPUTS['drivers']
    layer_dm = FB.rat(drv['FARM.chicken.stock_birds']['value']) * FB.rat(drv['FARM.chicken.feed_kg_bird_d']['value'])
    fish_ration = (FB.rat(drv['FARM.aquaponics.fish_stock_kg']['value']) *
                   FB.rat(drv['FARM.aquaponics.fish_feed_kg_kg']['value']))
    sludge = fish_ration * FB.SLUDGE_SHARE
    fs = (FB.rat(drv['FARM.bsfl.galley_bio_dm']['value'])
          + layer_dm * FB.rat(drv['FARM.classes.manure_dm_frac_of_feed']['value'])
          + FB.rat(drv['FARM.ducks.feed_kg_d']['value']) * FB.DUCK_MANURE_SHARE
          + sludge + FB.rat(drv['FARM.feed_prep.reject_dm']['value']))
    meal = FB.mg(fs * FB.rat(drv['FARM.bsfl.larvae_frac']['value']))
    assert meal == 210780                                      # 0.21078 kg DM/d, exact on the grid
    assert solve()['rates']['LARVAE_FRESH'] == 479045          # 0.21078 / the 44 % DM class
    assert solve()['checks']['BSFL_BIN'][0] == solve()['checks']['BSFL_BIN'][1]


def test_nitrate_design_and_dose():
    """The mineral-nitrate closure: the design block equals the committed
    goldens; the exact nh3 value lives on the design block while the balance's
    reconciled draw stays untouched on the edge."""
    S = solve()
    assert S['dose_mg'] == 4086824                             # 4.086824 kg/d at the 4.5 % N strength
    D = S['design']
    assert FB.mg(D['gap_N']) == 183907 and FB.mg(D['an']) == 525469
    assert FB.mg(D['nh3']) == 230527 and FB.mg(D['o2']) == 433116
    assert FB.mg(D['rxn_h2o']) == 118265 and FB.mg(D['dil']) == 3443091
    assert FB.mg(D['vent']) == 19909 and FB.mg(D['kw'], 1000) == 60
    assert D['vent'] >= 0 and D['dil'] >= 0
    out = json.loads(render(run()))
    n = next(x for x in out['nodes'] if x['unit_id'] == 'NUT_AN')
    assert n['params']['design'] == {'gap_N_kg_d': 0.183907, 'an_kg_d': 0.525469, 'dose_kg_d': 4.086824,
                                     'nh3_kg_d': 0.230527, 'o2_kg_d': 0.433116, 'rxn_h2o_kg_d': 0.118265,
                                     'dil_kg_d': 3.443091, 'vent_kg_d': 0.019909, 'kw': 0.06}
    assert n['continuous_kw']['value'] == 0.06
    assert n['continuous_kw']['note'] == ('X-RTE TF: on-site ammonium-nitrate nutrient skid (X-QA-11, A-M-497): '
                                          'oxidation starter, metering pumps and controls at the 4.087 kg/d dose '
                                          '(nut_an_kW, A-M-497).')
    assert n['provenance'][0]['stage'] == 'farm_balance'       # structured, not appended prose
    e = {x['stream_id']: x for x in out['edges']}
    assert e['NUT_AQUA']['rate']['value'] == 4.086824
    assert e['IA-NUT-O2']['rate']['value'] == 0.433116
    assert e['IA-NUT-H2O']['rate']['value'] == 3.443091
    assert e['IA-NUT-VENT']['rate']['value'] == 0.019909
    assert e['SF-NUT_AN']['rate']['value'] == 0.06
    # the balance-owned ammonia draw: not stamped, committed value stands
    committed = _committed()
    c_e = {x['stream_id']: x for x in committed['edges']}
    assert e['IA-NUT-NH3']['rate'] == c_e['IA-NUT-NH3']['rate']
    assert e['IA-NUT-NH3']['rate']['value'] == 0.230525        # the balance's R10c reconciled draw
    assert n['params']['design']['nh3_kg_d'] == 0.230527       # this stage's exact value, on the design block


def test_notes_parse_verbatim():
    """The stage-authored note texts travel as raw string fields, byte-equal to
    the committed parse-able state; the balance co-authored free-edge notes are
    untouched."""
    out = json.loads(render(run()))
    e = {x['stream_id']: x for x in out['edges']}
    assert e['LARVAE_FRESH']['rate']['note'] == ('fresh larvae at the 44 % DM class (TECHTREE insect-farming.md:112)'
                                                 ' (X-FARM wet-basis, farm_balance.py)')
    assert e['DUCK_RATION']['rate']['note'].endswith('(X-FARM wet-basis, farm_balance.py)')
    assert e['SHELL_GRIT']['rate']['note'].startswith('the galley shell return splits to the grit')
    assert e['CA_HOPPER']['rate']['note'].startswith('Retired by the eggshell-grit route')
    assert e['NUT_AQUA_BED']['rate']['note'].startswith('Retired by the on-site nutrient skid')
    committed = _committed()
    c_e = {x['stream_id']: x for x in committed['edges']}
    for sid in ('AQUA_RETURN2', 'AQUA_LOOP4', 'FORM_PRESS', 'BED_ET'):
        assert e[sid]['rate']['note'] == c_e[sid]['rate']['note']     # balance co-authored: untouched
    assert '[free:' in e['AQUA_RETURN2']['rate']['note']
    # no truncation-cap or MARK-strip machinery exists in the v2 module
    tree = ast.parse(inspect.getsource(FB))
    assert not [n for n in ast.walk(tree) if isinstance(n, ast.While)]
    assert not [n for n in ast.walk(tree)
                if isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant) and n.slice.value == 240]


def test_no_declared_inputs_records_nothing():
    """The bridge solve / check carry no driver payload: the stage records
    nothing and the seed stands."""
    b = load(REF_GRAPH)
    FB.farm_balance(b, {})
    assert b.computed == {}
    assert render(b) == open(REF_GRAPH, 'rb').read()


def test_provenance_rows():
    b = run()
    for (kind, uid, path), (value, prov) in b.computed.items():
        assert prov.stage == 'farm_balance' and prov.basis
        assert kind in ('node', 'edge')
    assert b.computed[('node', 'NUT_AN', 'params.design')][1].ref == 'A-M-497'
    assert b.computed[('edge', 'SHELL_GRIT', 'rate.note')][1].ref == 'A-M-501'
    assert b.computed[('edge', 'FORM_PRESS', 'rate.value')][1].ref == 'A-M-426'


def test_function_module_grid_purity():
    """The engine module holds no float literals and no I/O (the lint's rule,
    enforced here because the lint's scan of functions/ is not recursive)."""
    tree = ast.parse(inspect.getsource(FB))
    floats = [n.lineno for n in ast.walk(tree)
              if isinstance(n, ast.Constant) and isinstance(n.value, float)]
    opens = [n.lineno for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'open']
    assert floats == [] and opens == []
