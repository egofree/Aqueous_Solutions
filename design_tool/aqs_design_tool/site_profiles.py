# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Site-profile sandboxes: a scaling profile becomes sandbox overrides (X-UI-002).

The scaling engine (``flow_graph.param.scaling``) owns the action semantics; this module
only translates its resolved plan into the sandbox override vocabulary (unit enabled flags)
and reports what it could not carry. A size/duplicate action has no sandbox-wide equivalent
yet and is returned as ``unapplied`` rather than silently ignored.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from flow_graph.param import scaling as SC          # noqa: E402
from flow_graph.param import site as SITE           # noqa: E402


def available_sites() -> list[str]:
    return [s for s in SITE.available() if s != SITE.BASELINE]


def _graph_units() -> dict[str, dict]:
    g = json_graph()
    # placeholder units carry the locale replacements (LIO_BAT, RAD_PANEL, ...): they are
    # legitimate resolve targets even though they are not built at the baseline
    return {n['unit_id']: n for n in g['nodes'] if n.get('presence') in ('present', 'placeholder')}


def json_graph() -> dict:
    return json.loads((_REPO / 'flow_graph' / 'plant_flow_graph.json').read_text())


def site_overrides(site_id: str) -> dict[str, Any]:
    """Translate a site scaling profile into sandbox overrides.

    Returns ``{'overrides': <SandboxOverrides dict>, 'site_id', 'applied': [...],
    'unapplied': [...], 'replacement_of': {unit: replacement}}``.
    """
    prof = SITE.load_profile(site_id)
    units = _graph_units()
    plan, errors = SC.resolve(prof, units)
    unit_enabled: dict[str, bool] = {}
    applied: list[str] = []
    unapplied: list[str] = []
    replacement_of: dict[str, str] = {}
    for u, p in sorted(plan.items()):
        if p['status'] == 'eliminated':
            unit_enabled[u] = False
            applied.append(f'{u}: eliminated' + (f' -> {p["replacement"]}' if p.get('replacement') else ''))
            if p.get('replacement'):
                replacement_of[u] = p['replacement']
                unit_enabled.setdefault(p['replacement'], True)
        elif p['status'] == 'replaced' and p.get('replacement'):
            unit_enabled[u] = False
            unit_enabled[p['replacement']] = True
            replacement_of[u] = p['replacement']
            applied.append(f'{u}: replaced by {p["replacement"]}')
        elif p.get('factor', 1.0) != 1.0:
            unapplied.append(f'{u}: size factor {p["factor"]} (no sandbox-wide unit scaling yet)')
        elif p.get('count', 1) != 1:
            unapplied.append(f'{u}: duplicate count {p["count"]} (no sandbox duplicate yet)')
    return {'overrides': {'unit_enabled': unit_enabled}, 'site_id': site_id,
            'applied': applied, 'unapplied': unapplied, 'replacement_of': replacement_of,
            'errors': errors}


def site_power_portfolio(site_id: str) -> dict[str, Any]:
    """The profile's power portfolio (sources, storage, worst stretch, oversize)."""
    prof = SITE.load_profile(site_id)
    return prof['groups'].get('power_portfolio', {})

def site_placement_units(site_id: str) -> list[dict[str, Any]]:
    """The profile's replacement placements as fold-ready unit dicts.

    The replacements are placeholder units in the graph already - what the fold
    lacks is their SITE sizing and provenance, which the placement model sizes
    (flow_graph.param.site_units SIZERS). Returns one dict per placement."""
    from flow_graph.param import site_units as SU
    g = json_graph()
    out = []
    for rep, e in SU.placements(site_id, g):
        out.append({'unit_id': rep, 'sector_id': e['sector'], 'enabled': True,
                    'class': e['class'],
                    'params': {'site_placement': {'site': site_id, 'replaces': e['replaces'],
                                                  'sizing': e['sizing'],
                                                  'register': 'AQS-SITE-013 (SITE_UNITS.md)'},
                               'design': e['design']}})
    return out
