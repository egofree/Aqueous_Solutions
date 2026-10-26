# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""X-LOC locale pipeline: site_outputs.run() stamps the placements into the locale
worktree graph before the regen; the stamp is deterministic and idempotent, and the
reference graph is untouched. See flow_graph/param/site_units.py (AQS-SITE-013)."""
import json, os
from flow_graph.param import site as S, site_units as SU


def test_stamp_places_and_sizes_the_site_units(tmp_path):
    import subprocess, sys
    R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    wt = tmp_path / 'wt'
    subprocess.run(['git', 'worktree', 'add', '--detach', str(wt), 'HEAD'],
                   cwd=R, capture_output=True, text=True, check=True)
    try:
        gp = wt / 'flow_graph' / 'plant_flow_graph.json'
        n = SU.stamp_worktree(str(wt), 'mars')
        assert n > 0
        g = json.load(open(gp))
        units = {x['unit_id']: x for x in g['nodes']}
        assert units['RAD_PANEL']['params']['site_placement']['site'] == 'mars'
        assert units['RAD_PANEL']['params']['site_placement']['sizing']['area_m2'] > 0
        # baseline nodes keep their reference placement
        assert 'site_placement' not in units['IND_MELT']['params']
        # idempotent
        assert SU.stamp_worktree(str(wt), 'mars') == 0
    finally:
        subprocess.run(['git', 'worktree', 'remove', '--force', str(wt)],
                       cwd=R, capture_output=True, text=True)


def test_baseline_stamp_is_a_no_op():
    assert SU.stamp_worktree('.', S.BASELINE) == 0
