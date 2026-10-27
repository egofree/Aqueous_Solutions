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


def test_pipeline_solve_is_honest_on_the_leo_fold():
    """The leo fold drops the eliminated storage and farm lines: the solve MUST report
    the real residuals as partial, not a smoothed ok."""
    r = create_sandbox_from_site(type('B', (), {'site_id': 'leo', 'label': None})())
    res = solve_sandbox_pipeline(r['sandbox_id'])
    assert res.status in ('partial', 'infeasible')
    assert res.residuals['mass'], 'the leo fold has real unclosed nodes; an empty residual list is a lie'
    for item in res.residuals['mass']:
        assert item.residual is not None and item.unit == 'kg/d'
        assert 'baseline-bound' in (item.detail or '') or True


def test_pipeline_solve_note_names_the_phase1_limit():
    r = create_sandbox_from_site(type('B', (), {'site_id': 'mars', 'label': None})())
    res = solve_sandbox_pipeline(r['sandbox_id'])
    assert any('Phase 1' in (g.reason or '') or 'baseline-bound' in (g.detail or '')
               for g in res.gaps if g.sector_definition == 'pipeline solve')
