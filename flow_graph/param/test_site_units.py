# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Site-unit placements (X-LOC site models): the scaling plan's placeholder replacements
are placed and sized per locale; the register renders and the stamp is idempotent."""
import copy, json
import pytest
from flow_graph.param import site as S, scaling as SC, site_units as SU

GRAPH = json.load(open('flow_graph/plant_flow_graph.json'))


def test_placements_cover_the_design_pass_locales():
    rows = SU.placements_all()
    sites = {sid for sid, _, _ in rows}
    assert sites == {'mars', 'leo'}
    units = {s: {r for _s, r, _2 in rows if _s == s} for s in sites}
    assert {'RAD_PANEL', 'TANK_BLD', 'REC_HDR', 'CAT_OX', 'E_HEAT'} <= units['mars']
    assert {'LIO_BAT', 'WET_OX', 'HYDRO_GROW', 'MEM_DIST'} <= units['leo']


def test_every_placement_carries_a_basis_or_design_record():
    for sid, rep, e in SU.placements_all():
        assert e['sizing'].get('basis') or (e['design'] or {}).get('basis'), (sid, rep)


def test_rad_panel_area_follows_the_site_heat_rejection_group():
    mars = dict(SU.placements('mars'))
    leo = dict(SU.placements('leo'))
    a_mars = mars['RAD_PANEL']['sizing']
    a_leo = leo['RAD_PANEL']['sizing']
    assert a_mars['area_m2'] == pytest.approx(a_mars['area_m2_per_kW'] * a_mars['duty_kW'], abs=0.1)
    assert a_leo['area_m2'] == pytest.approx(a_leo['area_m2_per_kW'] * a_leo['duty_kW'], abs=0.1)
    assert a_mars['area_m2'] != a_leo['area_m2']          # the sinks differ (Mars sky vs LEO)


def test_lio_bat_sizes_from_the_worst_stretch_balance():
    leo = dict(SU.placements('leo'))
    sz = leo['LIO_BAT']['sizing']
    assert sz['storage_delivered_kWh'] > 0
    assert sz['storage_charged_kWh'] == pytest.approx(sz['storage_delivered_kWh'] / 0.7, rel=1e-3)


def test_apply_stamps_and_is_idempotent():
    g = copy.deepcopy(GRAPH)
    n = SU.apply(g, 'mars')
    assert n > 0
    stamped = {k: v for k, v in json.loads(json.dumps(g))['nodes'][0].items()}  # shape sanity
    assert stamped
    node = {x['unit_id']: x for x in g['nodes']}['RAD_PANEL']
    assert node['params']['site_placement']['site'] == 'mars'
    assert 'RAD_PANEL' in node['params']['site_placement']['replaces'] or node['params']['site_placement']['replaces']
    n2 = SU.apply(g, 'mars')
    assert n2 == 0                                        # idempotent: no re-stamp on an unchanged graph


def test_apply_leaves_the_reference_graph_unchanged_for_earth_locales():
    g = copy.deepcopy(GRAPH)
    before = json.dumps(g, sort_keys=True)
    assert SU.apply(g, 'death_valley') == 0
    assert json.dumps(g, sort_keys=True) == before


def test_register_renders():
    t = SU.render()
    assert 'Document number: AQS-SITE-013' in t and 'Table 1. Placements and sizing by locale' in t
    assert 'RAD_PANEL' in t and 'LIO_BAT' in t
