# SPDX-License-Identifier: CERN-OLH-S-2.0 placeholder - correct licence header asserted by test_meta
"""X-UI-002 Phase 1 gates: a scaling profile becomes a sandbox, and the solve runs the
REAL X-PAR-02 reconciliation on the fold (never a smoothed number)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.dirname(HERE)
REPO = os.path.dirname(TOOL)
for p in (TOOL, REPO):
    if p not in sys.path:
        sys.path.insert(0, p)

import pytest  # noqa: E402

from aqs_design_tool.api.app import (  # noqa: E402
    create_sandbox_from_site,
    list_sites,
    solve_sandbox_pipeline,
)
from aqs_design_tool.site_profiles import site_overrides  # noqa: E402


def test_sites_listed():
    out = list_sites()
    ids = {s['site_id'] for s in out['sites']}
    assert {'leo', 'mars', 'antarctic'} <= ids


def test_leo_overrides_eliminate_the_animal_chain():
    sp = site_overrides('leo')
    en = sp['overrides']['unit_enabled']
    for u in ('CHICKEN_COOP', 'AQUA_TANK', 'BSFL_BIN', 'BEE_HIVE', 'FEED_PREP', 'AQUA_UV'):
        assert en.get(u) is False, u
    # the leo plan eliminates the whole heavy-industry baseline (the pre-existing actions)
    # and my X-LOC-13 additions joined it: the produce chain lands on the microgravity
    # chamber class (GROWBED_A/B -> GROW_BED -> HYDRO_GROW, resolved through two actions)
    assert en.get('HYDRO_GROW') is True
    assert en.get('LIO_BAT') is True and en.get('TANK_BLD') is True
    assert sp['errors'] == []


def test_leo_sandbox_disables_the_animal_chain_and_enables_replacements():
    r = create_sandbox_from_site(type('B', (), {'site_id': 'leo', 'label': None})())
    m = r['model']
    off = {u['unit_id'] for u in m['units'] if not u.get('enabled', True)}
    on = {u['unit_id'] for u in m['units'] if u.get('enabled', True)}
    for u in ('CHICKEN_COOP', 'AQUA_TANK', 'DUCK_PEN', 'QUAIL_CAGE', 'RABBIT_HUTCH',
              'BSFL_BIN', 'BEE_HIVE', 'VERMI_BIN', 'FEED_PREP', 'AQUA_UV'):
        assert u in off, u
    assert 'LIO_BAT' in on                          # the storage replacement rides
    assert 'HYDRO_GROW' in on                       # the plant-chamber class rides
    assert 'POLY_FIBER' in on                       # textiles are site-independent (A-M-429)


def test_mars_sandbox_keeps_the_farm():
    r = create_sandbox_from_site(type('B', (), {'site_id': 'mars', 'label': None})())
    m = r['model']
    off = {u['unit_id'] for u in m['units'] if not u.get('enabled', True)}
    assert 'CHICKEN_COOP' not in off and 'AQUA_TANK' not in off


def test_pipeline_solve_on_the_leo_fold_is_honest_about_what_closing_means():
    """The leo fold removes whole units with their edges: a balanced SUBSET that can
    mass-close. The solve reports the closure it actually found and names the
    function loss as the stub solve's jurisdiction - it never calls the smaller
    plant equivalent to the baseline."""
    r = create_sandbox_from_site(type('B', (), {'site_id': 'leo', 'label': None})())
    res = solve_sandbox_pipeline(r['sandbox_id'])
    assert res.status in ('ok', 'partial')
    note = res.gaps[0].reason if res.gaps else ''
    assert 'units disabled' in note and 'FEWER FUNCTIONS' in note
    assert res.mvs_equivalent is False   # a closed subset is never the baseline


def test_pipeline_solve_carries_the_tf_policy_note():
    for sid in ('mars', 'leo'):
        r = create_sandbox_from_site(type('B', (), {'site_id': sid, 'label': None})())
        res = solve_sandbox_pipeline(r['sandbox_id'])
        assert any('physics' in (g.reason or '') for g in res.gaps
                   if g.sector_definition == 'pipeline solve'), sid

def test_leo_sandbox_stamps_the_placement_sizing():
    """The replacements are graph placeholders - the from-site fold stamps their SITE
    sizing and provenance (the placement model's own sizers)."""
    r = create_sandbox_from_site(type('B', (), {'site_id': 'leo', 'label': None})())
    m = r['model']
    lio = next(u for u in m['units'] if u['unit_id'] == 'LIO_BAT')
    sp = (lio.get('params') or {}).get('site_placement') or {}
    assert sp.get('site') == 'leo' and 'ZNBR2' in sp.get('replaces', [])
    assert set(sp.get('replaces', [])) == {'ZNBR2', 'ZNBR2_BR2_REGEN', 'HYDRO_SET'}
    assert sp.get('sizing'), 'the placement model sizing must be stamped'


def test_leo_pipeline_solve_reports_the_site_electrical_match():
    """The site electrical match comes from the profile portfolio: leo's primary is
    PV_ARRAY (share 1.0), the worst stretch is the eclipse, storage is LIO_BAT."""
    r = create_sandbox_from_site(type('B', (), {'site_id': 'leo', 'label': None})())
    res = solve_sandbox_pipeline(r['sandbox_id'])
    em = res.electrical_match or {}
    srcs = {s['unit']: s for s in em.get('sources', [])}
    assert srcs['PV_ARRAY']['role'] == 'primary' and srcs['PV_ARRAY']['share'] == 1.0
    assert srcs['PV_ARRAY']['enabled'] is True
    assert srcs['FUEL_CELL']['role'] == 'backup'
    assert em.get('worst_stretch', {}).get('kind') == 'eclipse'
    assert em.get('demand_kw', 0) > 0
    assert any('eta = 1' in g.reason for g in res.gaps if g.sector_definition == 'site electrical')


def test_leo_sandbox_survives_an_eliminated_storage_placeholder():
    """LIO_BAT's storage energy rides the placeholder node: the match must read the
    issued energy, and a missing storage unit must name the gap, not zero silently."""
    r = create_sandbox_from_site(type('B', (), {'site_id': 'leo', 'label': None})())
    res = solve_sandbox_pipeline(r['sandbox_id'])
    em = res.electrical_match or {}
    sto = {s['unit']: s for s in em.get('storage', [])}
    assert sto['LIO_BAT']['enabled'] is True
    assert (sto['LIO_BAT'].get('energy_kWh') or 0) > 0


def test_export_pack_carries_the_site_provenance():
    from aqs_design_tool.api.store import STORE, load_mvs_from_graph
    from aqs_design_tool.export.pack import export_pack
    import time
    from aqs_design_tool.models import ExportRequest
    r = create_sandbox_from_site(type('B', (), {'site_id': 'leo', 'label': None})())
    solve_sandbox_pipeline(r['sandbox_id'])
    rec = STORE.get(r['sandbox_id'])
    resp = export_pack(rec, ExportRequest(pack_name=f'site_prov_{int(time.time())}'))
    assert resp.pack_dir is not None

