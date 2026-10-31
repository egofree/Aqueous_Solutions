# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Pipeline solve: run the REAL balance stage on the sandbox-folded graph (X-UI-002 Phase 1).

The sandbox never invents closure: this module folds the live graph with the sandbox's
unit-enabled semantics, runs the actual X-PAR-02 physics + least-squares reconcile from
``flow_graph.param.balance``, and reports the true node residuals. Every number here is
the pipeline's own; a residual is reported, never smoothed away.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from flow_graph.param.balance import physics, reconcile  # noqa: E402
from aqs_design_tool.paths import FLOW_GRAPH_JSON  # noqa: E402


def solve_mass(mvs_units: list[dict], sandbox_id: str | None = None) -> dict[str, Any]:
    """Fold the live graph with the sandbox's disabled units, run the real balance.

    Returns ``{'status', 'residuals': {'mass': [ResidualItem dicts]}, 'nodes_solved',
    'max_residual', 'note'}``.
    """
    g = json.loads(FLOW_GRAPH_JSON.read_text())
    g0 = copy.deepcopy(g)
    disabled = {u['unit_id'] for u in mvs_units if not u.get('enabled', True)}
    if disabled:
        g['nodes'] = [n for n in g['nodes'] if n['unit_id'] not in disabled]
        gone = set(disabled)
        g['edges'] = [e for e in g['edges']
                      if e['from_unit_id'] not in gone and e['to_unit_id'] not in gone]
    # The X-PAR-02 physics TFs are baseline-bound: a fold that removed edges (a leo fold
    # has no ZNBR2 line for T-functions to write) breaks them. Policy: run the full
    # physics pass when the fold survives it; otherwise roll back to the pre-physics
    # graph and reconcile alone, stating the limitation. The baseline and the Earth-site
    # folds (nothing removed) therefore get the full pipeline behaviour.
    tf_note = 'full physics pass'
    try:
        physics(g)
    except (KeyError, AssertionError):
        g = copy.deepcopy(g0)
        tf_note = ('physics TF pass skipped: the fold lacks baseline edges the TFs write; '
                   'reconciliation runs on held study rates alone')
    R = reconcile(g)
    max_resid = float(max(abs(R['r'])) ) if len(R['r']) else 0.0
    items = []
    for k, n in enumerate(R['nodes']):
        r = float(R['r'][k])
        if abs(r) > 1e-3:
            items.append({'id': n, 'kind': 'node mass balance', 'residual': round(r, 6),
                          'unit': 'kg/d', 'status': 'incomplete',
                          'detail': 'held study rates the free edges could not reconcile inside tolerance'})
    # a node on a SINK boundary reports in != out by design (losses, exports): not a gap
    status = 'ok' if max_resid < 1e-3 else 'partial'
    return {'status': status, 'residuals': {'mass': items}, 'nodes_solved': len(R['nodes']),
            'max_residual': round(max_resid, 6), 'sandbox_id': sandbox_id,
            'tf_note': tf_note, 'disabled': len(disabled),
            'note': ('X-PAR-02 least squares on the sandbox fold; boundary sinks are exempt '
                     'by design (NORTH_DOCK trade, ATMOS evaporation, exports). ' + tf_note +
                     f'. {len(disabled)} units disabled: the fold can mass-close as a balanced '
                     'subset while carrying FEWER FUNCTIONS - the functional-gap analysis is the '
                     'stub solve jurisdiction (GET /flags).')}


def _graph_path() -> Path:
    return _REPO / 'flow_graph' / 'plant_flow_graph.json'


def solve_electrical(mvs_electrical: dict, mvs_units: list[dict], site_id: str,
                     disabled: set[str]) -> dict[str, Any]:
    """The site's electrical match from the profile's power portfolio and the fold.

    Real inputs only: the profile's worst stretch, yield and storage entries; the
    fold's enabled loads and nameplate; the storage units' issued energy. Nothing is
    invented: a missing number (a storage round-trip the profile does not state)
    becomes a named gap, and the energy match runs at the eta = 1 optimistic bound,
    labelled as such.
    """
    from flow_graph.param import portfolio as PF
    from flow_graph.param import scaling as SC
    from flow_graph.param import site as SITE

    prof = SITE.load_profile(site_id)
    pf = PF.portfolio(prof)
    g = json.loads(FLOW_GRAPH_JSON.read_text())
    units = {n['unit_id']: n for n in g['nodes']}
    plan, plan_errors = SC.resolve(prof, units)

    # demand: the fold's enabled non-generation continuous draw
    P = 0.0
    load_detail = []
    for u in mvs_units:
        if not u.get('enabled', True) or u.get('electrical_role') == 'generation':
            continue
        ck = u.get('continuous_kw') or {}
        val = ck.get('value')
        if isinstance(val, (int, float)):
            P += float(val)
            load_detail.append((u['unit_id'], float(val)))

    # the worst stretch + the resource entries the portfolio names
    def entry(key):
        if not key:
            return None
        grp, e = str(key).split('.', 1)
        return ((prof['groups'].get(grp, {}).get('entries') or {}).get(e) or {}).get('value')

    ws = pf.get('worst_stretch', {})
    ws_kind = ws.get('kind') or ws.get('value', {}).get('kind')
    hours = entry(ws.get('hours_entry'))
    gaps = []
    if hours is None:
        hours = 0.0
        gaps.append(f'worst-stretch hours entry {ws.get("hours_entry")!r} missing')
    storage = pf.get('storage', [])
    eta = 1.0
    eta_stated = False
    for st in storage:
        if isinstance(st.get('eta'), (int, float)):
            eta = float(st['eta'])
            eta_stated = True
    if not eta_stated:
        gaps.append('storage round-trip efficiency not stated in the profile: the energy match runs at the eta = 1 optimistic bound')

    # sources: eliminated ones are named (the validate rule); the survivors carry the share
    sources_out = []
    phi = 0.0
    for src in pf.get('sources', []):
        u = src.get('unit')
        on = u not in disabled
        eliminated = plan.get(u, {}).get('status') == 'eliminated'
        if eliminated:
            gaps.append(f'power source {u} is eliminated by the scaling actions - the site needs a replacement source or an import path')
        share = src.get('share') if src.get('role') == 'primary' else None
        f = src.get('stretch_output_frac', 0.0) if src.get('role') == 'primary' else None
        if on and share is not None and isinstance(f, (int, float)):
            phi += share * f
        sources_out.append({'id': src.get('id'), 'unit': u, 'kind': src.get('kind'),
                            'role': src.get('role'), 'share': share, 'enabled': on,
                            'eliminated': eliminated})

    # the fold's PV nameplate + the profile's yield: the daily PV energy
    pv_nameplate = None
    elec_block = None
    for u in mvs_units:
        if u['unit_id'] == 'PV_ARRAY':
            sz = (u.get('params') or {}).get('sizing') or {}
            pv_nameplate = sz.get('nameplate_kw')
    el = mvs_electrical or {}
    if el.get('pv_module_kw') is not None and el.get('pv_count') is not None:
        pv_nameplate = el['pv_module_kw'] * el['pv_count']
    pv_yield = entry('solar.pv_yield_kWh_kWp_d')
    pv_day_kwh = round(pv_nameplate * pv_yield, 1) if (pv_nameplate and pv_yield) else None

    # the storage energies: the enabled storage units' issued energy parameters
    storage_out = []
    storage_kwh = 0.0
    for st in storage:
        u = st.get('unit')
        enabled = u not in disabled
        ep = st.get('energy_param')
        node = units.get(u) or {}
        e_val = node.get('params', {}).get(ep)
        if not isinstance(e_val, (int, float)):
            e_val = (node.get('params', {}).get('design') or {}).get('energy_kWh')
        if enabled and isinstance(e_val, (int, float)):
            storage_kwh += float(e_val)
        storage_out.append({'unit': u, 'kind': st.get('kind'), 'enabled': enabled,
                            'energy_kWh': e_val, 'energy_param': ep})

    # the match: eclipse energy vs the storage; the daily energy vs the PV
    eclipse_kwh = round(P * hours, 1) if hours else None
    day_kwh = round(P * 24, 1)
    margins = {}
    if eclipse_kwh is not None:
        margins['eclipse_energy_kwh'] = eclipse_kwh
        margins['storage_energy_kwh'] = round(storage_kwh, 1)
        margins['eclipse_margin_kwh'] = round(storage_kwh - eclipse_kwh / eta, 1)
    if pv_day_kwh is not None:
        margins['pv_daily_energy_kwh'] = pv_day_kwh
        margins['daily_margin_kwh'] = round(pv_day_kwh - day_kwh / eta, 1)

    status = 'ok'
    if margins.get('eclipse_margin_kwh', 0) < 0 or margins.get('daily_margin_kwh', 0) < 0:
        status = 'shortfall'
    if gaps:
        status = 'partial'

    return {'electrical_match': {
        'demand_kw': round(P, 3),
        'load_detail': load_detail[:12],
        'sources': sources_out,
        'storage': storage_out,
        'worst_stretch': {'kind': ws_kind, 'hours': hours},
        'phi': round(phi, 4),
        'eta': eta, 'eta_stated': eta_stated,
        'margins': margins,
        'pv_nameplate_kw': pv_nameplate, 'pv_yield_kWh_kWp_d': pv_yield,
        'status': status,
        'note': ('Site electrical match from the profile portfolio + the fold. The energy '
                 'match runs at the eta = 1 optimistic bound where the profile states no '
                 'round trip. Per-site resource re-sizing is the pipeline regen (--site).')},
        'gaps': gaps, 'redundancy_errors': plan_errors}
