# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Power portfolio and function redundancy (AQS-PLAN-011 section 5.5, X-LOC-06)."""
import copy, json
import pytest
from flow_graph.param import portfolio as PF, scaling as SC, site as S, heat_rejection as HR
from flow_graph.param.sizing import power as PW

UNITS = SC.graph_units()


@pytest.fixture
def base():
    return copy.deepcopy(json.load(open(S.path(S.BASELINE))))


def _src(p):
    return p['groups']['power_portfolio']['entries']['sources']['value']


def _err(p):
    plan, e = SC.resolve(p, UNITS)
    return ' | '.join(e + PF.validate(p, UNITS, plan) + PF.redundancy(p, UNITS, plan)[1])


def test_every_profile_passes():
    for sid in S.available():
        PF.check(sid)


def test_baseline_pv_factor_is_exactly_one(base):
    assert PF.pv_factor(base, 0.7) == 1.0


def test_balance_reduces_to_the_reference_pv_formula(base):
    eta, h, P, y, der = 0.7, base['groups']['solar']['entries']['night_hours']['value'], 100.0, 5.0, 0.8
    ref = PW.pv_kWp(P, h, eta, y, der)
    assert PF.mean_generation_per_kW(base, eta) * P * 24 / (y * der) == pytest.approx(ref, rel=1e-12)


def test_output_in_the_stretch_reduces_pv_and_storage(base):
    p = copy.deepcopy(base); s = _src(p)
    s[0]['share'] = 0.6
    s.append({'id': 'wind', 'kind': 'wind', 'unit': 'GEO_ORC', 'role': 'primary', 'share': 0.4, 'stretch_output_frac': 1.0, 'capacity_factor': 0.35, 'register': 'test'})
    assert _err(p) == ''
    assert PF.pv_factor(p, 0.7) < 0.6 * 1.0 + 1e-12 or PF.pv_factor(p, 0.7) < 1.0
    assert PF.mean_generation_per_kW(p, 0.7) < PF.mean_generation_per_kW(base, 0.7)


def test_portfolio_rules(base):
    p = copy.deepcopy(base); _src(p)[0]['share'] = 0.5
    assert 'shares must sum to 1' in _err(p)
    p = copy.deepcopy(base); _src(p).append({'id': 'n', 'kind': 'fission', 'unit': 'GEO_ORC', 'role': 'backup', 'register': 'test'})
    assert 'only as a flagged option' in _err(p)
    p = copy.deepcopy(base); _src(p).append({'id': 'w', 'kind': 'wind', 'unit': 'GEO_ORC', 'role': 'primary', 'share': 0.0, 'register': 'test'})
    assert 'share above 0' in _err(p) and 'capacity factor' in _err(p)
    p = copy.deepcopy(base); _src(p)[1]['unit'] = 'NO_UNIT'
    assert 'not in the graph' in _err(p)
    p = copy.deepcopy(base); del _src(p)[1]['register']
    assert 'no ref, register id or owner basis' in _err(p)
    p = copy.deepcopy(base); p['groups']['power_portfolio']['entries']['worst_stretch']['value']['hours_entry'] = 'solar.none'
    assert 'hours entry' in _err(p)


def test_multi_day_stretch_waits_for_the_seasonal_model(base):
    p = copy.deepcopy(base); p['groups']['solar']['entries']['night_hours']['value'] = 72.0
    assert 'seasonal storage model' in _err(p)


def test_eliminated_portfolio_unit_fails(base):
    p = copy.deepcopy(base)
    p['groups']['scaling']['entries']['actions']['value'] = [{'target': 'MEOH_FC', 'action': 'eliminate', 'replacement': 'GEO_ORC', 'register': 'test'}]
    assert 'eliminated by the scaling actions' in _err(p)


def test_baseline_redundancy_holds(base):
    rows, err = PF.redundancy(base, UNITS)
    assert err == [] and set(rows) >= {'power', 'oxygen', 'water', 'co2_removal', 'thermal_storage', 'food', 'sanitation'}


def test_import_does_not_keep_a_life_support_source(base):
    p = copy.deepcopy(base)
    p['groups']['scaling']['entries']['actions']['value'] = [
        {'target': 'CRYO_ASU', 'action': 'eliminate', 'import_path': {'stream': 'O2 cylinders'}, 'register': 'test'}]
    e = _err(p)
    assert 'CRYO_ASU is a life-support unit' in e and 'oxygen (life-support): 1 source unit' in e


def test_replacement_keeps_the_count(base):
    p = copy.deepcopy(base)
    p['groups']['scaling']['entries']['actions']['value'] = [
        {'target': 'DRY_COOLER', 'action': 'replace', 'replacement': 'GEO_HP', 'register': 'test'}]
    rows, err = PF.redundancy(p, UNITS)
    assert err == [] and ('GEO_HP', 1, 'replaces DRY_COOLER') in rows['heat_rejection']


def test_power_document_renders():
    t = PF.render()
    assert 'Document number: AQS-SITE-005' in t and '| PV factor on the reference balance | 1 |' in t


def _hr(p):
    return p['groups']['heat_rejection']['entries']


def _hrerr(p):
    plan = SC.resolve(p, UNITS)[0]
    return ' | '.join(HR.validate(p, UNITS, plan))


def test_radiator_area_follows_stefan_boltzmann():
    # a black surface at 300 K facing a sink at 0 K radiates sigma * 300**4 W per m2
    assert HR.radiator_m2_per_kW(300.0, 0.0, 1.0) == pytest.approx(1000 / (5.670374419e-8 * 300.0 ** 4), rel=1e-12)
    assert HR.radiator_m2_per_kW(300.0, 200.0, 0.5) == pytest.approx(2 * 1000 / (5.670374419e-8 * (300.0 ** 4 - 200.0 ** 4)))
    with pytest.raises(ValueError):
        HR.radiator_m2_per_kW(250.0, 250.0, 0.9)


def test_carnot_bound():
    assert HR.carnot_cop(300.0, 330.0) == pytest.approx(11.0)


def test_baseline_heat_rejection_holds(base):
    assert _hrerr(base) == ''


def test_mode_needs_its_capabilities(base):
    base['groups']['capabilities']['entries']['air_heat_sink']['value'] = False
    assert 'needs the capabilities air_heat_sink' in _hrerr(base)
    _hr(base)['levels']['value'][0]['mode'] = 'seawater'
    assert 'seawater entry in water_sources' in _hrerr(base)


def test_radiative_mode_needs_its_entries_and_sizes(base):
    lv = _hr(base)['levels']['value'][0]
    lv['mode'] = 'radiative'; lv['radiator_K'] = 330.0
    assert 'heat_rejection.radiator_emissivity' in _hrerr(base)
    _hr(base)['radiator_emissivity'] = {'value': 0.9, 'units': '-', 'owner': 'test'}
    _hr(base)['radiative_sink_K'] = {'value': 250.0, 'units': 'K', 'owner': 'test'}
    assert _hrerr(base) == ''
    assert 'm2 per kW' in HR.rows(base, UNITS)[0][4]
    lv['radiator_K'] = 240.0
    assert 'above the sink temperature' in _hrerr(base)


def test_heat_pump_states_its_lift(base):
    lv = _hr(base)['levels']['value'][0]
    lv.update(mode='heat_pump', sink_mode='air', source_K=300.0, reject_K=330.0)
    assert _hrerr(base) == ''
    assert 'lift 30 K' in HR.rows(base, UNITS)[0][4]
    lv['reject_K'] = 290.0
    assert 'source_K below reject_K' in _hrerr(base)


def test_every_remaining_rejection_unit_needs_a_mode(base):
    _hr(base)['levels']['value'].pop()
    assert 'GEO_GHEX rejects heat at this site' in _hrerr(base)


def test_a_replacement_brings_its_own_mode(base):
    base['groups']['scaling']['entries']['actions']['value'] = [
        {'target': 'DRY_COOLER', 'action': 'replace', 'replacement': 'GEO_HP', 'register': 'test'}]
    e = _hrerr(base)
    assert 'DRY_COOLER does not remain' in e and 'GEO_HP rejects heat at this site' in e


def test_power_document_reports_storage_coverage_and_rejection():
    t = PF.render()
    assert 'coverage' in t and '## 4. Heat rejection' in t and '| DRY_COOLER | air |' in t
