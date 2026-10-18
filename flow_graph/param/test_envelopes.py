"""X-PAR-04 gate: every unit with a size in the graph has a study envelope STL whose bounding box matches it (1 mm). Regenerate with
<cadquery python> -m flow_graph.param.envelopes --all."""
import json, os, re
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def bbox_mm(p):
    v = [tuple(map(float, m.groups())) for m in re.finditer(r'vertex\s+(\S+)\s+(\S+)\s+(\S+)', open(p).read())]
    return sorted(round((max(x[i] for x in v) - min(x[i] for x in v)) * 1000) for i in range(3))
def test_envelopes_match_sizes():
    g = json.load(open(os.path.join(R, 'flow_graph/plant_flow_graph.json'))); bad = []
    for n in g['nodes']:
        p = n.get('params', {}); s = (p.get('sizing') or {}).get('size_mm') or p.get('size_mm')
        if not s: continue
        f = os.path.join(R, 'cad/stl', n['unit_id'] + '.stl')
        if not os.path.exists(f) or any(abs(a - b) > 1 for a, b in zip(bbox_mm(f), sorted(round(x) for x in s[:3]))): bad.append(n['unit_id'])
    assert not bad, bad
