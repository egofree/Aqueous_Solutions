# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Scaling actions and unit needs (AQS-PLAN-011 section 5, X-LOC-05)."""
import copy, json
import pytest
from flow_graph.param import scaling as SC, site as S

UNITS = SC.graph_units(); NT = SC.needs_table()


@pytest.fixture
def base():
    return copy.deepcopy(json.load(open(S.path(S.BASELINE))))


def _run(prof, *acts, drop=()):
    p = copy.deepcopy(prof)
    p['groups']['scaling']['entries']['actions']['value'] = [dict(a, register=a.get('register', 'test')) for a in acts]
    for n in drop: p['groups']['capabilities']['entries'][n]['value'] = False
    return SC.resolve(p, UNITS, NT)


def _errs(*a, **k):
    return ' | '.join(_run(*a, **k)[1])


def test_every_profile_resolves():
    for sid in S.available():
        assert SC.resolve(S.load_profile(sid), UNITS, NT)[1] == []


def test_needs_table_matches_the_graph_and_the_schema():
    classes = {n.get('class') for n in UNITS.values()}
    assert set(NT['by_class']) <= classes
    assert set(NT['by_unit']) <= set(UNITS) and set(NT['function_by_unit']) <= set(UNITS)
    assert set(S.groups_spec()['capabilities']['entries']) == set(NT['needs'])
    for spec in list(NT['by_class'].values()) + [v['needs'] for v in NT['by_unit'].values()]:
        assert set(spec) <= set(NT['needs'])


def test_baseline_keeps_every_unit(base):
    plan, err = _run(base)
    assert err == [] and all(p['status'] == 'kept' and p['factor'] == 1.0 and p['count'] == 1 for p in plan.values())


def test_size_and_duplicate(base):
    plan, err = _run(base, {'target': 'sector:FOUNDRY', 'action': 'size', 'factor': 0.5}, {'target': 'FUEL_CELL', 'action': 'duplicate', 'count': 2})
    assert err == [] and plan['FUEL_CELL']['count'] == 2
    assert all(plan[u]['factor'] == 0.5 for u in UNITS if UNITS[u].get('sector_id') == 'FOUNDRY' and u in plan)
    assert 'factor above zero' in _errs(base, {'target': 'HX8', 'action': 'size', 'factor': 0})
    assert 'count of 2 or more' in _errs(base, {'target': 'HX8', 'action': 'duplicate', 'count': 1})


def test_unknown_target_or_action_or_basis(base):
    assert 'not a unit or a sector' in _errs(base, {'target': 'NO_UNIT', 'action': 'size', 'factor': 2})
    assert 'is not one of' in _errs(base, {'target': 'HX8', 'action': 'shrink'})
    p = copy.deepcopy(base); p['groups']['scaling']['entries']['actions']['value'] = [{'target': 'HX8', 'action': 'size', 'factor': 2}]
    assert 'no ref, register id or owner basis' in ' '.join(SC.resolve(p, UNITS, NT)[1])


def test_unmet_need_forces_replace_or_eliminate(base):
    e = _errs(base, drop=['air_heat_sink'])
    assert 'DRY_COOLER: needs air_heat_sink' in e
    assert 'DRY_COOLER: needs' not in _errs(base, {'target': 'DRY_COOLER', 'action': 'replace', 'replacement': 'GEO_HP'}, drop=['air_heat_sink'])


def test_elimination_needs_import_or_replacement(base):
    assert 'needs an import path or a replacement' in _errs(base, {'target': 'GLASS_MILL', 'action': 'eliminate'})
    assert _errs(base, {'target': 'GLASS_MILL', 'action': 'eliminate', 'import_path': {'stream': 'glass cullet by ship', 'resupply_interval_d': 90}}) == ''


def test_energy_or_life_support_elimination_needs_a_different_technology(base):
    e = _errs(base, {'target': 'BACKUP_GEN', 'action': 'eliminate', 'import_path': {'stream': 'grid'}})
    assert 'energy unit; eliminating it needs a replacement of a different technology' in e
    e = _errs(base, {'target': 'GROW_BED', 'action': 'eliminate', 'import_path': {'stream': 'food by ship'}})
    assert 'life-support unit' in e
    assert _errs(base, {'target': 'BACKUP_GEN', 'action': 'eliminate', 'replacement': 'FUEL_CELL'}) == ''


def test_replacement_rules(base):
    assert 'same technology' in _errs(base, {'target': 'Q1_A', 'action': 'replace', 'replacement': 'Q1_B'})
    assert 'does not perform the energy function' in _errs(base, {'target': 'BACKUP_GEN', 'action': 'replace', 'replacement': 'GLASS_MILL'})
    assert 'not a unit in the graph' in _errs(base, {'target': 'BACKUP_GEN', 'action': 'replace', 'replacement': 'RADIATOR'})
    assert 'already replaced' in _errs(base, {'target': 'BACKUP_GEN', 'action': 'replace', 'replacement': 'FUEL_CELL'},
                                       {'target': 'BACKUP_GEN', 'action': 'eliminate', 'replacement': 'PV_ARRAY'})


def test_replacement_needs_are_checked(base):
    e = _errs(base, {'target': 'GEO_HP', 'action': 'replace', 'replacement': 'DRY_COOLER'}, {'target': 'DRY_COOLER', 'action': 'size', 'factor': 1.0}, drop=['air_heat_sink'])
    assert 'replacement DRY_COOLER needs air_heat_sink' in e


def test_capabilities_cannot_exceed_the_profile(base):
    p = copy.deepcopy(base); p['groups']['gravity']['entries']['g_m_s2']['value'] = 0.0
    assert 'claimed with no apparent gravity' in ' '.join(SC.resolve(p, UNITS, NT)[1])
    p = copy.deepcopy(base); p['groups']['atmosphere']['entries']['pressure_Pa']['value'] = 600
    assert 'triple point' in ' '.join(SC.resolve(p, UNITS, NT)[1])
    p = copy.deepcopy(base); p['groups']['atmosphere']['entries']['oxidant']['value'] = False
    assert 'differs from atmosphere.oxidant' in ' '.join(SC.resolve(p, UNITS, NT)[1])


def test_scaling_document_renders():
    t = SC.render()
    assert 'Document number: AQS-SITE-004' in t and 'no scaling action' in t
