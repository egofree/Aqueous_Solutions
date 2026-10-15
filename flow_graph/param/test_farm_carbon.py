"""A-M-141..143: every crop unit sized from BVAD takes CO2 and gives O2 on the graph (no food from water alone)."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_crop_units_have_carbon():
    g = json.load(open(os.path.join(ROOT, 'flow_graph/plant_flow_graph.json')))
    for n in g['nodes']:
        if 'crop_basis' not in (n.get('params') or {}): continue
        u = n['unit_id']
        co2 = sum(e['rate']['value'] for e in g['edges'] if e['to_unit_id'] == u and (e.get('composition') or {}).get('CO2'))
        o2 = sum(e['rate']['value'] for e in g['edges'] if e['from_unit_id'] == u and (e.get('composition') or {}).get('O2'))
        assert co2 > 0 and o2 > 0, u
        assert abs(o2/co2 - 0.727) < 0.05, (u, o2/co2)
