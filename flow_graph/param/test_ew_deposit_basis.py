"""Electrowinning cascade basis (AQS-DUTY-051, AQS-ASSAY-001).

1. The cell currents follow Faraday's law, I = m z F / (M t CE), checked here against an
   independent calculation with the CODATA 2018 Faraday constant (96 485.332 12 C/mol) and
   the current efficiency in drivers.json.
2. The equipment of every cell is rated at the AQS-ASSAY-001 element envelope (owner ruling
   Q-038, 2026-11-05; AGENTS.md sizing rule): the sizing deposit of each cell equals the design
   feed rate times the element fraction of AQS-ASSAY-001 table 4.1 at leach recovery 1.0, and
   no element bound exceeds the plateable class of the case it governs.
3. The booked S08 deposit rows (the stream-rate basis) still exceed the plateable metal of the
   reference feed they cite. That defect stays an expected failure until the booked rates are
   computed from the assay (task X-QA-04). strict=True makes the test fail once the defect is
   fixed, so the marker is removed with the fix.
"""
import json, os, subprocess, sys
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from flow_graph.param import drivers as DR

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


@pytest.mark.xfail(strict=True, reason='X-QA-04: the booked S08 deposit rows are not derived from the IA-FEED-01 assay')
def test_booked_s08_deposits_within_reference_feed():
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
