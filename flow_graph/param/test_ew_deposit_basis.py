"""Electrowinning cascade basis (AQS-DUTY-051, AQS-ASSAY-001).

1. The cell currents follow Faraday's law, I = m z F / (M t CE), checked here against an
   independent calculation with the CODATA 2018 Faraday constant (96 485.332 12 C/mol) and
   the current efficiency in drivers.json.
2. The plated metal cannot exceed the plateable metal the design feed carries. The deposit
   rows the cascade is sized on (drivers.json DIGESTER.ew-cascade-train.ew_s08_deposits_kg_d)
   come from the S08 booking, which cites a 150 kg/d feed audit, and exceed the plateable
   metal of the 102.68 kg/d design feed. This test records that defect as an expected failure
   until the deposits are computed from the IA-FEED-01 assay (task X-QA-04). strict=True makes
   the test fail once the defect is fixed, so the marker is removed with the fix.
"""
import json, os, subprocess, sys
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from flow_graph.param import drivers as DR

F_CODATA = 96485.33212
EL = {1: (196.97, 3), 2: (107.87, 1), 3: (63.546, 2), 4: (207.2, 2), 5: (118.71, 2),
      6: (58.693, 2), 7: (55.845, 2), 8: (112.41, 2), 9: (65.38, 2)}   # Au Ag Cu Pb Sn Ni Fe Cd Zn


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


@pytest.mark.xfail(strict=True, reason='X-QA-04: EW deposit rows are not derived from the IA-FEED-01 assay')
def test_plated_metal_within_feed_plateable_metal():
    e = _graph_edge('IA-FEED-01'); feed = e['rate']['value']
    env = e['params']['assay_envelope']
    fr = max(c['metal_plateable'] for c in env['cases'].values())
    plated = sum(r['dep_kg_d'] for r in _ew_rows())
    assert plated <= feed * fr * 1.0 + 1e-6, (plated, feed * fr)
