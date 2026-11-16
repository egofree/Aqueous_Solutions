"""engine v2: golden equality for the section H/J physics books - the
arithmetic halves the renderer wave split out of their MIXED rows, proven
against the v1 reference writers and the committed doc fields:

- functions/fire_book against flow_graph/param/fire.py (the v1 library, run
  under the baseline site) and flow_graph/param/pressure_nodes.py GAS;
- functions/building against models/freecad/params.py and
  flow_graph/param/water_tower.py (the tests import the I/O-carrying v1
  libraries; the books themselves may not);
- functions/protection against the print-only v1 stages
  docs-authority/_grounding_study.py and _protection.py (their stdout books);
- functions/gas_detection against the committed GAS_DETECTORS.csv;
- functions/haz_area against the graph-derived columns of the committed
  HAZ_AREA.csv.

The PROTECTION.md page is NOT a golden: it is hand-authored and its figures
predate the current roof and inverter count (no writer exists in the tree);
the book golden is the v1 stage stdout.
"""
import ast
import csv
import json
import os
import subprocess
import sys

from flow_graph.v2 import solve as SL
from flow_graph.v2.functions import building as _BLD
from flow_graph.v2.functions import fire_book as _FB
from flow_graph.v2.functions import gas_detection as _GD
from flow_graph.v2.functions import haz_area as _HAZ
from flow_graph.v2.functions import protection as _PROT
from flow_graph.v2.render import electrical as _ELEC

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')
DRIVERS = os.path.join(ROOT, 'flow_graph', 'param', 'drivers.json')
PROFILE = os.path.join(ROOT, 'flow_graph', 'param', 'sites', 'baseline.json')
INPUTS = {'drivers': json.load(open(DRIVERS)),
          'site_profile': json.load(open(PROFILE))}


def model():
    return SL.solve(INPUTS, REF_GRAPH)


def _resolved_drivers():
    """The resolved driver payload (the v1 DR.load() read: drivers.json with
    the baseline profile's binds applied)."""
    d = dict(INPUTS['drivers'])
    for grp in INPUTS['site_profile']['groups'].values():
        for e in (grp.get('entries') or {}).values():
            k = e.get('binds')
            if k:
                d[k] = {f: x for f, x in e.items() if f != 'binds'}
    return d


def _committed(path):
    with open(os.path.join(ROOT, path), newline='', encoding='utf-8') as f:
        return f.read()


# ---- functions/fire_book --------------------------------------------------------

def test_fire_demand_zones_supply_equal_v1_library():
    from flow_graph.param import fire as F1
    from flow_graph.param import site as SITE1
    d = _resolved_drivers()
    m = model()
    plate = _BLD.PLATE_L * _BLD.PLATE_W / 1000000
    rows2, vf2 = _FB.demand(d, plate)
    rows1, vf1 = F1.demand(plate)
    assert rows2 == rows1 and vf2 == vf1
    z2, z1 = _FB.zones(d), F1.zones()
    assert z2 == z1
    static = SITE1.g() * _BLD.building_book(m, d, SITE1.g())['HYDRO']['z_res0_m']
    s2 = _FB.supply(d, rows2, vf2, static)
    s1 = F1.supply(rows1, vf1, static)
    assert s2 == s1


def test_receiver_fire_case_equal_v1_library():
    from flow_graph.param import fire as F1
    from flow_graph.param import receivers as RC1
    from flow_graph.param import site as SITE1
    d = _resolved_drivers()
    m = model()
    fake = [dict(n, params=dict(n.get('params') or {})) for n in m.data['nodes'] if n['unit_id'] in _FB.GAS_FIRE]
    rr = RC1.design(d, {'nodes': fake, 'edges': m.data['edges']})
    from flow_graph.param.sizing.relief import equiv_bore_mm, gas_area_in2
    gas = _FB.gas_book(d)
    mg = d['press_design_margin']['value']
    win = d['ely_window_h']['value']
    for u in _FB.GAS_FIRE:
        c = gas[u]
        des = c['P_bar'] * mg * 100
        w = sum((e['rate']['value'] or 0) / (win if e['from_unit_id'] == 'H2O_ELYZ' else 24)
                for e in m.data['edges'] if e['to_unit_id'] == u and e['presence'] == 'present'
                and (e['rate'] or {}).get('unit') == 'kg/d')
        p1 = 1.10 * des + SITE1.p_process_kPa()
        p1_v1 = dict(design=rr[u], design_kPa=round(des, 1),
                     relief_basis={'P1_kPa_abs': round(p1, 1), 'T_K': c['T_K'], 'M_kg_kmol': c['M'], 'k': c['k'], 'Z': c['Z'],
                                   'W_kg_h': round(w, 4),
                                   'bore_req_mm': round(equiv_bore_mm(gas_area_in2(w * 2.20462, c['k'], p1 / 6.894757,
                                                                                   c['T_K'] * 1.8, c['Z'], c['M'])), 2)})
        f1 = F1.receiver_fire(p1_v1)
        f2 = _FB.receiver_fire(p1_v1, SITE1.p_process_kPa())
        assert f2 == f1, u


def test_gas_book_equal_pressure_nodes():
    from flow_graph.param import pressure_nodes as PN1
    d = _resolved_drivers()
    book = _FB.gas_book(d)
    for u in _FB.GAS_FIRE:
        assert book[u] == PN1.GAS[u], u


# ---- functions/building ---------------------------------------------------------

def test_building_book_equal_params_library():
    sys.path.insert(0, os.path.join(ROOT, 'models', 'freecad'))
    import params as P1                                                   # noqa: E402  (the v1 library; loads drivers + graph)
    from flow_graph.param import water_tower as WT1                       # noqa: E402
    d = _resolved_drivers()
    m = model()
    from flow_graph.param import site as SITE1
    g = SITE1.g()
    b = _BLD.building_book(m, d, g)
    for attr in ('PLATE_L', 'PLATE_W', 'SLAB_THK', 'Z_Lm1', 'Z_Lm2', 'Z_L1', 'Z_L2', 'Z_L0', 'SHOP_LEVELS', 'LIFE_LEVELS',
                 'CORE_X', 'CORE_Y', 'STAIR_BOX', 'STAIR_MAINT_W', 'STAIR_SERVICE_L', 'STAIR_SERVICE_W',
                 'STAIR_SERVICE_X', 'STAIR_SERVICE_Y', 'HYDRO_RES_Z0', 'HYDRO_RES_CLEAR', 'HYDRO_RES_LEVELS', 'Z_ROOF',
                 'CATCH_TANK_L', 'CATCH_TANK_W', 'CATCH_TANK_H', 'CATCH_TANK_X', 'CATCH_TANK_Y', 'CATCH_TANK_Z'):
        assert b[attr] == getattr(P1, attr), attr
    assert b['HYDRO'] == P1.HYDRO
    r2 = _BLD.hydro_solve(b['HYDRO']['E_kWh'], _BLD.PLATE_L, _BLD.PLATE_W,
                          b['Z_L2'] + d['wt_level_clear_mm']['value'], _BLD.basement_z(_BLD.BASEMENT_LEVELS - 1), d, g,
                          v_dead=b['HYDRO']['V_fire_m3'])
    r1 = WT1.solve(b['HYDRO']['E_kWh'], P1.PLATE_L, P1.PLATE_W,
                   P1.Z_L2 + d['wt_level_clear_mm']['value'], P1.basement_z(P1.BASEMENT_LEVELS - 1),
                   d, V_dead=b['HYDRO']['V_fire_m3'])
    assert r2 == r1 and r2 == P1.HYDRO
    s2 = _BLD.seismic_wind(P1.HYDRO, P1.PLATE_L, P1.PLATE_W, d, g)
    s1 = WT1.seismic_wind(P1.HYDRO, P1.PLATE_L, P1.PLATE_W)
    assert s2 == s1


# ---- functions/protection -------------------------------------------------------

def _one_line_feeders():
    """The one-line table rows as the committed display carries them (the v1
    stage parsed A and Breaker out of the ONE_LINE.md text): composed here from
    the landed electrical book with the same display rounding."""
    from flow_graph.param.sizing import power as _PWS
    m = model()
    d = _resolved_drivers()
    b = _ELEC._one_line_book(m, d)
    rows = []
    for bb, u, k, _bs in sorted(b['rows'], key=lambda r: (r[0], -r[2])):
        kp = max(k, b['PK'].get(u) or 0)
        a = b['amps'](kp) if '480' in bb else b['amps'](kp, 3, 208)
        a = float(f'{a:.1f}')
        br = _PWS.breaker(a, list(_ELEC.BRK))
        rows.append((bb, u, a, br))
    return rows, b['xf']


def test_grounding_study_equal_v1_stage_stdout():
    m = model()
    d = _resolved_drivers()
    got = _PROT.grounding_study(m, d)
    out = subprocess.run([sys.executable, 'docs-authority/_grounding_study.py'], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout
    want = json.loads(out)
    assert got == want


def test_protection_book_equal_v1_stage_stdout():
    m = model()
    d = _resolved_drivers()
    grid = _PROT.grounding_study(m, d)
    feeders, xf = _one_line_feeders()
    got = _PROT.protection_book(m, d, feeders, xf, grid)
    out = subprocess.run([sys.executable, 'docs-authority/_protection.py'], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout
    want = json.loads(out)
    assert got['Irated'] == want['Irated']
    assert got['Ifault'] == want['Ifault']
    assert got['feeders'] == want['feeders']
    assert got['main'] == want['main']
    for k in ('Rg', 'GPR', 'Em', 'Es', 'n', 'ts'):
        assert got[k] == want[k], k
    assert got['tolerable'] == want['tolerable']


# ---- functions/gas_detection ----------------------------------------------------

def test_gas_detector_rows_equal_committed_csv():
    rows = _GD.detector_rows(model())
    got = list(csv.DictReader(_committed('docs-authority/inventory/GAS_DETECTORS.csv').splitlines()))
    assert len(rows) == len(got)
    for r, g in zip(rows, got):
        assert g['unit'] == r['unit'] and g['gas'] == r['gas']
        assert g['sector'] == str(r['sector'])
        assert g['type'] == r['type'] and g['mounting'] == r['mounting']
        assert g['alarm'] == r['alarm'] and g['trip'] == r['trip']
        assert int(g['qty']) == r['qty'] and g['voting'] == r['voting']


# ---- functions/haz_area ---------------------------------------------------------

def test_haz_area_rows_equal_committed_csv_fields():
    d = _resolved_drivers()
    rows = _HAZ.release_rows(model(), d)
    got = list(csv.DictReader(_committed('docs-authority/inventory/HAZ_AREA.csv').splitlines()))
    assert len(rows) == len(got)
    for r, g in zip(rows, got):
        assert g['unit'] == r['unit']
        assert g['sector'] == str(r['sector'])
        assert g['substances'] == r['substances']
        assert float(g['kg_d']) == r['kg_d']
        assert g['group'] == r['group'] and g['T_class'] == r['T_class']
        assert g['zone0'] == r['zone0'] and g['zone1'] == r['zone1'] and g['zone2'] == r['zone2']
        assert g['protection'] == r['protection']


# ---- discipline -----------------------------------------------------------------

def test_books_pure():
    """No I/O and no float literals in the book modules (the engine lint's
    discipline; the drivers, profiles and seed books carry the values)."""
    banned = {'datetime', 'random', 'uuid', 'time', 'tempfile'}
    for mod in (_BLD, _FB, _GD, _HAZ, _PROT):
        path = mod.__file__
        with open(path, encoding='utf-8') as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    assert a.name.split('.')[0] not in banned, f'{path}: banned import {a.name}'
            elif isinstance(node, ast.ImportFrom):
                assert (node.module or '').split('.')[0] not in banned, f'{path}: banned import from {node.module}'
            elif isinstance(node, ast.Constant):
                assert not isinstance(node.value, float), f'{path}:{node.lineno}: float literal'
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'open':
                raise AssertionError(f'{path}:{node.lineno}: file I/O in a book module')
