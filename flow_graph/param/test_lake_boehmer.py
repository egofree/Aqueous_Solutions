# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Lake Boehmer site design pass checks (AQS-SITE-015, X-LOC-05): salt and power closure,
the electrodialysis transfer function, the crew-0 scaling guard and redundancy relief, and
the profile's keep/eliminate plan."""
import copy, json
import pytest
from flow_graph.param import drivers as DR, site as S, scaling as SC, portfolio as PF, lake_boehmer as LB
from flow_graph.param.sizing.power import pv_kWp

UNITS = SC.graph_units()
NT = SC.needs_table()


def _compute():
    sid = S.site_id()
    return LB.compute(DR.load(sid), S.load_profile(sid))


def test_salt_balance_closes():
    fl = _compute()['flows']
    assert fl['salt_closure_kg_d'] == pytest.approx(0.0, abs=1e-6)
    assert fl['salt_feed_kg_d'] == pytest.approx(fl['salt_product_kg_d'] + fl['salt_concentrate_kg_d'], rel=1e-9)
    assert fl['concentrate_tds_g_L'] > fl['feed_tds_g_L']


def test_sec_matches_the_transfer_function():
    d = DR.load(S.site_id())
    F = 96485.33212
    for t0, t1 in ((105.0, 45.0), (45.0, 15.0)):
        dc_eq = 2.0 * (t0 - t1) / 58.44 * 1000.0
        want = F * dc_eq * DR.val(d, 'WTR.lake-boehmer.ed_cellpair_voltage_V') / (
            DR.val(d, 'WTR.lake-boehmer.ed_current_efficiency') * 3.6e6)
        got = [s for s in _compute()['stages'] if s['tds_in_g_L'] == t0 and s['tds_out_g_L'] == t1][0]['sec_kwh_m3']
        assert got == pytest.approx(want, rel=0.01)


def test_module_and_container_counts_cover_the_duty():
    c = _compute()
    spare = DR.val(DR.load(S.site_id()), 'WTR.lake-boehmer.ed_spare_modules_per_stage')
    per_cont = DR.val(DR.load(S.site_id()), 'WTR.lake-boehmer.ed_modules_per_container')
    for s in c['stages']:
        assert s['modules_installed'] == s['modules_duty'] + spare and s['modules_duty'] >= 1
    assert c['ed']['ed_containers'] == sum(-(-s['modules_installed'] // int(per_cont)) for s in c['stages'])
    assert c['containers_total'] == c['ed']['ed_containers'] + c['ed']['utility_container_total'] + c['power']['battery_containers']


def test_power_balance_follows_the_drivers():
    import math
    d = DR.load(S.site_id())
    c = _compute()
    pw = c['power']
    p = c['ed']['demand_kw']
    bal = pv_kWp(p, DR.val(d, 'night_hours'), DR.val(d, 'storage_round_trip'),
                 DR.val(d, 'pv_yield_kWh_kWp_d'), DR.val(d, 'pv_system_derate'))
    assert pw['pv_nameplate_kWp'] == math.ceil(bal * DR.val(d, 'pv_oversize_factor'))
    usable = p * DR.val(d, 'night_hours') + p * 24.0 * DR.val(d, 'WTR.lake-boehmer.battery_contingency_days')
    assert pw['battery_charged_kwh'] == pytest.approx(usable / DR.val(d, 'storage_round_trip'), abs=0.11)
    assert pw['battery_containers'] == math.ceil(pw['battery_charged_kwh'] / DR.val(d, 'WTR.lake-boehmer.bess_container_kWh'))


def test_net_lake_salt_removal_is_zero_with_both_streams_returned():
    c = _compute()
    assert c['net_lake_salt_removal']['kg_d'] == 0.0
    assert 'Q-037' in c['net_lake_salt_removal']['statement']


def test_profile_plan_keeps_and_eliminates():
    prof = S.load_profile('lake_boehmer')
    plan, err = SC.resolve(prof, UNITS, NT)
    assert err == []
    for u, p in plan.items():
        if p['status'] == 'kept':
            assert UNITS[u].get('sector_id') in ('ELEC', 'WTR', 'HEAT', 'DOCK'), u
    for u in ('BACKUP_GEN', 'FUEL_CELL', 'ZNBR2', 'HYDRO_SET', 'MEOH_FC'):
        assert plan[u]['status'] == 'eliminated' and plan[u]['replacement'] == 'LIO_BAT', u
    assert plan['GEO_GHEX']['replacement'] == 'DRY_COOLER'
    for u in LB.LB_UNITS:
        assert u not in plan and UNITS[u]['presence'] == 'placeholder'
    for u in ('HABITATION', 'GROW_BED', 'FOOD_STORE', 'CRYO_ASU', 'H2O_ELYZ', 'HDR_O2'):
        assert plan[u]['status'] == 'eliminated' and plan[u]['replacement'] is None


def test_portfolio_and_heat_rejection_hold_at_the_locale():
    PF.check('lake_boehmer')          # raises on any portfolio, redundancy or rejection rule


def _crew0_profile(prof):
    p = copy.deepcopy(prof)
    p['groups']['identity']['entries']['crew'] = {
        'value': 0, 'units': 'persons', 'owner': 'test crew-0 ruling'}
    return p


def _errs(prof, *acts):
    p = copy.deepcopy(prof)
    p['groups']['scaling']['entries']['actions']['value'] = [dict(a, register=a.get('register', 'test')) for a in acts]
    return ' | '.join(SC.resolve(p, UNITS, NT)[1])


def test_crew_zero_guard_scopes():
    base = json.load(open(S.path(S.BASELINE)))
    ruling = 'Q-036: crew of zero, no life-support demand'
    # crew of 4: the guard holds without a replacement
    assert 'life-support unit' in _errs(base, {'target': 'GROW_BED', 'action': 'eliminate'})
    # crew of 0: the ruling admits the life-support elimination
    assert _errs(_crew0_profile(base), {'target': 'GROW_BED', 'action': 'eliminate', 'ruling': ruling}) == ''
    # crew of 0 without the recorded ruling: the guard still holds
    assert 'life-support unit' in _errs(_crew0_profile(base), {'target': 'GROW_BED', 'action': 'eliminate'})
    # crew of 0 does not waive the energy guard
    assert 'energy unit' in _errs(_crew0_profile(base), {'target': 'BACKUP_GEN', 'action': 'eliminate', 'ruling': ruling})
    # the ruling waives nothing for a process unit
    assert 'waives nothing' in _errs(_crew0_profile(base), {'target': 'GLASS_MILL', 'action': 'eliminate', 'ruling': ruling})


def test_stamp_is_idempotent_and_complete():
    g = json.load(open('flow_graph/plant_flow_graph.json'))
    g = copy.deepcopy(g)
    c = _compute()
    n = LB.stamp(g, c)
    assert n >= len(LB.LB_UNITS) + 1
    units = {x['unit_id']: x for x in g['nodes']}
    assert units['LB_ED1']['params']['lb_design']['modules_installed'] == \
        [s for s in c['stages'] if s['unit'] == 'LB_ED1'][0]['modules_installed']
    assert units['LIO_BAT']['params']['lb_design']['battery_charged_kwh'] == c['power']['battery_charged_kwh']
    assert units['LB_PROD_OUTLET']['params']['lb_design']['net_lake_salt_removal_kg_d'] == 0.0
    assert LB.stamp(g, c) == 0


def test_main_writes_nothing_outside_the_locale_worktree(monkeypatch):
    monkeypatch.delenv('AQS_LOCALE_WORKTREE', raising=False)
    before = open('flow_graph/plant_flow_graph.json').read()
    assert LB.main([]) == 0
    assert open('flow_graph/plant_flow_graph.json').read() == before
    if S.site_id() == 'lake_boehmer':
        with pytest.raises(SystemExit, match='locale worktree'):
            LB.main(['--write'])                 # the selected site refuses outside the locale worktree
    else:
        assert LB.main(['--write']) == 0        # baseline: not the selected site; nothing written
    assert open('flow_graph/plant_flow_graph.json').read() == before
    # an explicit lake_boehmer context outside the locale worktree refuses
    monkeypatch.setattr('flow_graph.param.site.site_id', lambda: 'lake_boehmer')
    with pytest.raises(SystemExit, match='locale worktree'):
        LB.main(['--write'])
    assert open('flow_graph/plant_flow_graph.json').read() == before
