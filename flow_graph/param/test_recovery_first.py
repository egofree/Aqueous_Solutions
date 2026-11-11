"""Recovery-first rule (owner decision t61u, A-M-476): every element taken as raw ore at the dock is first recovered
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
    # F-20261110-07: a live sink stream carrying an element a recovery record covers must be
    # declared - here the furnace fume loses its briquette credit with no loss basis, so the
    # gate flags it even though the dock quartz draw is retired (the plant still needs silicon)
    g = json.load(open(recovery.GP)); g2 = copy.deepcopy(g)
    for n in g2['nodes']:
        if n['unit_id'] == 'SI_REDUCE':
            n['params']['recovery'][0]['unrecovered'] = []
    for e in g2['edges']:
        if e['stream_id'] == 'IA-SI-FUME':
            e['presence'] = 'present'
            e['rate'] = {'value': 0.001, 'unit': 'kg/d', 'status': 'study', 'note': 'test: the fume credit withdrawn'}
            e['composition'] = {'SiO2': 1.0}
    assert any(f.startswith('IA-SI-FUME') for f in recovery.check(g2))


def test_dock_class_is_a_field_not_text():
    # F-20261110-07: every live dock input carries an explicit class; the gate tests the field
    g = json.load(open(recovery.GP)); g2 = copy.deepcopy(g)
    for e in g2['edges']:
        if e.get('from_unit_id') == 'NORTH_DOCK' and recovery._live(e):
            (e.setdefault('params', {})).pop('dock_class', None)
    flags = recovery.check(g2)
    assert flags and all('no explicit dock_class' in f for f in flags), flags
