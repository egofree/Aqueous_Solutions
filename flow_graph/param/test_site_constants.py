# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Earth-surface constants come from the site profile (AQS-PLAN-011 section 3.2, task X-LOC-03).

Model code (flow_graph, models/freecad and the docs-authority generators named in the regeneration
manifest) holds no standard gravity or standard pressure literal. The exceptions are listed below with
their reason. The modules that use the rounded gravity 9.81 wait for the owner's decision in Q-032;
the list is frozen so that no new module adds one."""
import json, os, re, subprocess
from flow_graph.param import site as S

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
G_STD = re.compile(r'(?<![\d.])9\.80665(?!\d)')
G_ROUND = re.compile(r'(?<![\d.])9\.81(?!\d)')
P_STD = re.compile(r'(?<![\d.])(101\.325|101325(\.0)?|1\.01325)(?![\d])')
AIR = re.compile(r'(?<![\d.])(0\.2095|0\.7808|0\.209476|0\.78084)(?!\d)')

# (file, reason): a literal that is not the site's external pressure.
P_ALLOWED = {
    'flow_graph/param/balance.py': 'HENRY CO2 bound: pure CO2 at one standard atmosphere, not the external air',
    'flow_graph/param/sizing/scrubber.py': 'Fuller diffusivity correlation: pressure in standard atmospheres (unit conversion)',
}
G_ALLOWED = {'flow_graph/param/report.py': 'text naming the equation constants of the baseline'}
G_ROUND_PENDING = {   # Q-032: replace 9.81 by the profile gravity (outputs change) or keep
    'flow_graph/inventory/motors.py', 'flow_graph/param/ess_tf.py', 'flow_graph/param/evap_design.py',
    'flow_graph/param/geo_loop.py', 'flow_graph/param/heat_battery.py', 'flow_graph/param/house_scrubbers.py',
    'flow_graph/param/reactor_design.py', 'flow_graph/param/vent_scrubber.py', 'flow_graph/param/water_tower.py',
    'flow_graph/param/write_graph.py', 'flow_graph/param/report.py', 'models/freecad/frame.py', 'docs-authority/_design_check.py',
    'docs-authority/_ew_busbar.py', 'docs-authority/_fire.py', 'docs-authority/_foundation.py',
    'docs-authority/_frame_check.py', 'docs-authority/_hydro_siting.py', 'docs-authority/_water_tower.py',
}


def _model_files():
    m = json.load(open(os.path.join(ROOT, 'flow_graph/param/regen_manifest.json')))
    da = 'docs-authority'   # generators named in the manifest
    gen = {a for s in m['stages'] for a in s['argv'] if a.startswith(da + os.sep + '_') and a.endswith('.py')}
    tracked = subprocess.run(['git', 'ls-files', 'flow_graph/*.py', 'models/freecad/*.py'], cwd=ROOT,
                             capture_output=True, text=True).stdout.split()
    return [f for f in tracked + sorted(gen)
            if not re.search(r'(^|/)test_', f) and f not in ('flow_graph/param/refs.py', 'flow_graph/param/site.py')]


def _hits(pat):
    out = {}
    for f in _model_files():
        for i, line in enumerate(open(os.path.join(ROOT, f), errors='replace'), 1):
            if pat.search(line.split('#')[0]): out.setdefault(f, []).append(i)
    return out


def test_no_standard_gravity_literal():
    bad = {f: l for f, l in _hits(G_STD).items() if f not in G_ALLOWED}
    assert bad == {}, 'read gravity from flow_graph/param/site.py: ' + repr(bad)


def test_no_standard_pressure_or_air_literal():
    bad = {f: l for f, l in {**_hits(P_STD), **_hits(AIR)}.items() if f not in P_ALLOWED}
    assert bad == {}, 'read the external pressure and air from flow_graph/param/site.py: ' + repr(bad)


def test_rounded_gravity_list_does_not_grow():
    assert set(_hits(G_ROUND)) <= G_ROUND_PENDING, set(_hits(G_ROUND)) - G_ROUND_PENDING


def test_baseline_constants_equal_the_old_literals(monkeypatch):
    monkeypatch.delenv(S.ENV, raising=False)
    assert S.g() == 9.80665
    assert S.p_atm_Pa() == 101325 and S.p_atm_kPa() == 101.325
    assert S.air_fraction('O2') * S.p_atm_Pa() == 0.2095 * 101325
    assert S.air_fraction('N2') * S.p_atm_Pa() == 0.7808 * 101325
