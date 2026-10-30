"""Recovery-first rule (owner decision t61u, A-M-423): every element taken as raw ore at the dock is first recovered
from the plant's waste and byproduct streams, and the ore covers only the shortfall. flow_graph/param/recovery.py
holds the checks."""
import copy, json
from flow_graph.param import recovery, drivers as DR


def test_no_recovery_flags():
    flags = recovery.check()
    assert not flags, flags


def test_every_dock_ore_has_a_record():
    inv = recovery.inventory()
    covered = {s for r in inv['rows'] for s in r.get('ore_streams', [])}
    assert set(inv['ore_el']) <= covered, set(inv['ore_el']) - covered


def test_ore_above_shortfall_is_flagged():
    g = json.load(open(recovery.GP)); g2 = copy.deepcopy(g)
    e = [x for x in g2['edges'] if x['stream_id'] == 'IA-SULFUR-MU'][0]
    e['rate']['value'] = float(e['rate']['value'])*2 + 0.01
    assert any('exceeds the unrecovered shortfall' in f for f in recovery.check(g2))


def test_undeclared_waste_outflow_is_flagged():
    g = json.load(open(recovery.GP)); g2 = copy.deepcopy(g)
    for n in g2['nodes']:
        if n['unit_id'] == 'SHELL_BUILD':
            n['params']['recovery'][0]['unrecovered'] = []
    assert any(f.startswith('IA-SHELL-EXPORT') for f in recovery.check(g2))
