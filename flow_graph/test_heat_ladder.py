"""X-THM-01: every heat-ladder store closes on the graph thermal rates (A-M-166)."""
import collections, json, os
G = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plant_flow_graph.json')

def test_heat_ladder_stores_close():
    g = json.load(open(G)); b = collections.Counter()
    for e in g['edges']:
        if 'thermal' in e['layers'] and e.get('presence') != 'retired' and e['rate'].get('unit') == 'kW':
            v = float(e['rate']['value'] or 0); b[e['from_unit_id']] -= v; b[e['to_unit_id']] += v
    bad = {u: round(v, 4) for u, v in b.items() if u[:3] in ('Q1_', 'Q2_', 'Q3_', 'Q4_') and abs(v) > 0.01}
    assert not bad, bad

def test_line_losses_carried():
    g = json.load(open(G))
    hl = [e for e in g['edges'] if e['stream_id'].startswith('HL-') and (e.get('params') or {}).get('duty_rated_kw')]
    assert hl and all('line_loss_W' in e['params'] for e in hl if e['stream_id'] != 'HL-HX8-Q4-A' and e['stream_id'] != 'HL-HX8-Q4-B')
