"""Electrowinning cascade basis (AQS-DUTY-051, AQS-ASSAY-001).

1. The cell currents follow Faraday's law, I = m z F / (M t CE), checked here against an
   independent calculation with the CODATA 2018 Faraday constant (96 485.332 12 C/mol) and
   the current efficiency in drivers.json.
2. The equipment of every cell is rated at the AQS-ASSAY-001 element envelope (owner ruling
   Q-038, 2026-11-05; AGENTS.md sizing rule): the sizing deposit of each cell equals the design
   feed rate times the element fraction of AQS-ASSAY-001 table 4.1 at leach recovery 1.0, and
   no element bound exceeds the plateable class of the case it governs.
3. The booked deposit rows are computed from the feed assay (X-QA-04, 2026-11-10): solver
   .ew_products derives each cell's booked deposit from the IA-FEED-01 rate, the AQS-ASSAY-001
   reference-point element fraction and the leach recovery, with the lumped other_plateable
   class split evenly over the five minor metals (A-M-470). The booked rows stay within the
   plateable metal of the reference feed - the check that failed while the rows still carried
   the S08 booking of the retired 150 kg/d feed audit.
"""
import json, os, subprocess, sys
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from flow_graph.param import drivers as DR
from flow_graph.param import solver
from flow_graph.param.sizing import electrochem

F_CODATA = 96485.33212
EL = {1: (196.97, 3), 2: (107.87, 1), 3: (63.546, 2), 4: (207.2, 2), 5: (118.71, 2),
      6: (58.693, 2), 7: (55.845, 2), 8: (112.41, 2), 9: (65.38, 2)}   # Au Ag Cu Pb Sn Ni Fe Cd Zn
ENV_KEY = {1: 'Au', 2: 'Ag', 3: 'Cu', 4: 'other_plateable', 5: 'other_plateable',
           6: 'other_plateable', 7: 'Fe', 8: 'other_plateable', 9: 'other_plateable'}


def _ew_rows():
    out = subprocess.run([sys.executable, 'docs-authority/_ew_sizing.py'], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)['rows']


def _graph_edge(sid):
    g = json.load(open(os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')))
    return next(e for e in g['edges'] if e['stream_id'] == sid)


def test_cell_current_follows_faraday():
    d = DR.load(); ce = DR.val(d, 'ew_current_efficiency_design')
    for r in _ew_rows():
        n = int(r['cell'].split('_')[1]); M, z = EL[n]
        expect = r['dep_kg_d'] * 1000.0 / M * z * F_CODATA / 86400.0 / ce
        assert r['I_A'] == pytest.approx(expect, rel=1e-4), r['cell']


def test_equipment_sized_at_the_element_envelope():
    d = DR.load()
    e = _graph_edge('IA-FEED-01'); feed = e['rate']['value']
    els = e['params']['assay_envelope']['element_envelope']['elements']
    rec = DR.val(d, 'ew_leach_recovery_design')
    rows = _ew_rows()
    assert len(rows) == 9
    for r in rows:
        n = int(r['cell'].split('_')[1])
        expect = feed * els[ENV_KEY[n]]['fraction'] * rec
        assert r['dep_kg_d'] == pytest.approx(expect, rel=1e-9), r['cell']
        assert r['env_case'] == els[ENV_KEY[n]]['case'], r['cell']
    # no element bound exceeds the plateable class of the case that governs it
    cases = e['params']['assay_envelope']['cases']
    for key, spec in els.items():
        cls = cases[spec['case']]['metal_plateable']
        assert spec['fraction'] <= cls, (key, spec, cls)


def test_booked_s08_deposits_within_reference_feed():
    """X-QA-04: the booked deposit rows are computed from the feed assay (solver.ew_products),
    so their sum stays inside the plateable class of the reference feed (AQS-ASSAY-001)."""
    e = _graph_edge('IA-FEED-01'); feed = e['rate']['value']
    cls = e['params']['assay_envelope']['cases']['reference_point']['metal_plateable']
    booked = sum(r['dep_ref_kg_d'] for r in _ew_rows())
    assert booked <= feed * cls + 1e-6, (booked, feed * cls)


def test_minor_metal_arrangement_carried_both_ways():
    """Q-041: no clear winner between the selective and merged minor-metal arrangements,
    so both are carried in the design data; the driver selects and names a valid value."""
    d = DR.load()
    arr = DR.val(d, 'ew_minor_metal_arrangement')
    assert arr in ('selective', 'merged'), arr
    out = json.loads(subprocess.run([sys.executable, 'docs-authority/_ew_sizing.py'], cwd=ROOT,
                                    capture_output=True, text=True, check=True).stdout)
    m, rows = out['merged_alt'], out['rows']
    minor = (4, 5, 6, 8, 9)
    # the merged bounding current is the largest single-element current of the five (nickel basis)
    assert m['I_A'] == pytest.approx(max(rows[n - 1]['I_A'] for n in minor), rel=1e-9)
    assert m['cathodes'] >= 1 and len(m['size_mm']) == 3
    assert all(r['cell'] == f'EW_{n}' for n, r in zip(range(1, 10), rows))


def test_minor_metal_merged_option_books_the_full_blend():
    """Q-041 / X-QA-05 (A-M-494): 'merged' carries the same lumped blend on one current-carrying
    minor cell - the first, rated at the nickel basis, the largest of the five selective ratings -
    and 'selective' restores today's book. The booking ledger is arrangement-independent."""
    g = json.load(open(os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')))
    d0 = DR.load()
    dm = dict(d0)
    dm['ew_minor_metal_arrangement'] = dict(d0['ew_minor_metal_arrangement'], value='merged')
    sel = solver.ew(d0, g)
    mer = solver.ew(dm, g)
    minor = tuple(int(n) for n in DR.val(d0, 'ew_minor_metal_cells'))
    host = minor[0]
    # the ledger does not move: the blend books fully in both arrangements
    assert solver.ew_products(d0, g)['blend'] == solver.ew_products(dm, g)['blend'] > 0
    # the cell count drops: five current-carrying minor cells to one, on the first
    assert [n for n in minor if sel[f'EW_{n}']['I_A'] > 0] == list(minor)
    assert [n for n in minor if mer[f'EW_{n}']['I_A'] > 0] == [host]
    assert all(mer[f'EW_{n}']['I_A'] == 0.0 and mer[f'EW_{n}']['dep_kg_d'] == 0.0
               for n in minor if n != host)
    # the merged rating is the largest single-element rating of the five (nickel basis),
    # carried at the full lumped-class envelope deposit
    assert mer[f'EW_{host}']['I_A'] == pytest.approx(max(sel[f'EW_{n}']['I_A'] for n in minor), rel=1e-9)
    assert mer[f'EW_{host}']['dep_kg_d'] == pytest.approx(sel[f'EW_{host}']['dep_kg_d'], rel=1e-12)
    M_ni, z = EL[6]
    ce = DR.val(d0, 'ew_current_efficiency_design')
    assert mer[f'EW_{host}']['I_A'] == pytest.approx(
        mer[f'EW_{host}']['dep_kg_d'] * 1000.0 / M_ni * z * F_CODATA / 86400.0 / ce, rel=1e-4)
    # the primary cells do not move and the rectifier book follows the reduced set
    for n in (1, 2, 3, 7):
        assert mer[f'EW_{n}'] == sel[f'EW_{n}']
    assert mer['RECT_EW']['I_A'] == pytest.approx(sum(mer[f'EW_{n}']['I_A'] for n in range(1, 10)))
    assert mer['RECT_EW']['I_A'] < sel['RECT_EW']['I_A']
    # switching back restores today's book
    assert solver.ew(d0, g) == sel
    # the solver seam reproduces the sizing sheet's merged cell (cathode count, AQS-DUTY-051 section 4)
    out = json.loads(subprocess.run([sys.executable, 'docs-authority/_ew_sizing.py'], cwd=ROOT,
                                    capture_output=True, text=True, check=True).stdout)
    ap = 2 * DR.val(d0, 'DIGESTER.ew-cascade-train.ew_plate_height_m') * DR.val(d0, 'DIGESTER.ew-cascade-train.ew_plate_width_m')
    assert electrochem.cathode_count(mer[f'EW_{host}']['I_A'], DR.val(d0, 'ew_current_density_A_m2'), ap) \
        == out['merged_alt']['cathodes']
