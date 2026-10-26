# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Heat rejection modes per site (AQS-PLAN-011 section 5.5, task X-LOC-06).

The profile's heat_rejection group lists, per level of the heat ladder, the unit that rejects the
heat, its mode and the graph parameter that gives its duty. Each mode needs site capabilities:

    air          air_heat_sink
    evaporative  air_heat_sink, vent_sink, liquid_water_at_ambient
    ground       ground_contact
    seawater     liquid_water_at_ambient and a water_sources entry whose name holds 'sea'
    radiative    none; the group then carries radiator_emissivity and radiative_sink_K
    heat_pump    the capabilities of its sink_mode; source_K and reject_K give the lift

Radiator area per kW rejected (Stefan-Boltzmann law, sigma from CODATA 2018):

    A / Q = 1000 / (eps sigma (T_r^4 - T_s^4))   [m2 per kW]

Every unit of the heat_rejection function in redundancy.json that remains after the scaling actions
needs a level, so no rejection unit runs without a mode the site supports. The unit that remains is
the kept source, or the replacement a scaling action registers for it: a replacement that rejects
heat carries its own level."""
import json
from . import site as S, scaling as SC

SIGMA = 5.670374419e-8   # W/(m2 K4) [CODATA2018]
MODES = {'air': ('air_heat_sink',), 'evaporative': ('air_heat_sink', 'vent_sink', 'liquid_water_at_ambient'),
         'ground': ('ground_contact',), 'seawater': ('liquid_water_at_ambient',), 'radiative': (), 'heat_pump': ()}


def group(prof):
    return prof['groups']['heat_rejection']['entries']


def radiator_m2_per_kW(radiator_K, sink_K, emissivity):
    """Radiator area in m2 per kW rejected from a surface at radiator_K to a sink at sink_K."""
    if not 0 < emissivity <= 1: raise ValueError('emissivity must lie above 0 and at most 1')
    if radiator_K <= sink_K: raise ValueError('a radiator rejects heat only above the sink temperature')
    return 1000.0 / (emissivity * SIGMA * (radiator_K ** 4 - sink_K ** 4))


def carnot_cop(source_K, reject_K):
    """Upper bound on the heating COP of a lift from source_K to reject_K."""
    if reject_K <= source_K: raise ValueError('a heat pump lifts to a higher temperature')
    return reject_K / (reject_K - source_K)


def _caps(prof):
    c = prof['groups']['capabilities'].get('entries') or {}
    return {k for k, e in c.items() if e['value'] is True}


def _sea(prof):
    w = prof['groups'].get('water_sources', {}).get('entries') or {}
    return any('sea' in k for k in w)


def validate(prof, units=None, plan=None, red=None):
    units = units or SC.graph_units()
    if plan is None: plan = SC.resolve(prof, units)[0]
    from .portfolio import RED
    red = red or json.load(open(RED))
    g = group(prof); levels = g['levels']['value']; caps = _caps(prof); err = []
    # a level may sit on a kept unit or on the replacement an action registers: the replacement
    # is the unit that runs at this site (the placeholder it activates is not a plan unit)
    repl = {p['replacement'] for p in plan.values() if p.get('replacement')}
    def need(mode, k, lv):
        if mode not in MODES or mode == 'heat_pump': err.append(f'{k}: mode {mode!r} is not one of {", ".join(MODES)}'); return
        miss = [c for c in MODES[mode] if c not in caps]
        if miss: err.append(f'{k}: mode {mode} needs the capabilities {", ".join(miss)}')
        if mode == 'seawater' and not _sea(prof): err.append(f'{k}: seawater mode needs a seawater entry in water_sources')
        if mode == 'radiative':
            for e in ('radiator_emissivity', 'radiative_sink_K'):
                if e not in g: err.append(f'{k}: radiative mode needs heat_rejection.{e}')
            if not isinstance(lv.get('radiator_K', lv.get('reject_K')), (int, float)): err.append(f'{k}: radiative mode needs radiator_K')
    for i, lv in enumerate(levels):
        k = f'heat_rejection.levels[{i}]'
        if not (lv.get('ref') or lv.get('register') or lv.get('owner')): err.append(f'{k}: no ref, register id or owner basis')
        u = lv.get('unit')
        if u not in units: err.append(f'{k}: unit {u!r} is not in the graph'); continue
        if plan.get(u, {}).get('status') != 'kept' and u not in repl:
            err.append(f'{k}: {u} does not remain after the scaling actions')
        if not isinstance(units[u].get('params', {}).get(lv.get('duty_param')), (int, float)):
            err.append(f'{k}: duty parameter {lv.get("duty_param")!r} is not a number on {u}')
        m = lv.get('mode')
        if m == 'heat_pump':
            if not all(isinstance(lv.get(t), (int, float)) for t in ('source_K', 'reject_K')) or lv['reject_K'] <= lv['source_K']:
                err.append(f'{k}: a heat pump needs source_K below reject_K')
            need(lv.get('sink_mode'), k, lv)
        else: need(m, k, lv)
    have = {lv.get('unit') for lv in levels}
    for u in red['functions']['heat_rejection']['sources']:
        p = plan.get(u)
        if p is None: continue
        v = u if p['status'] == 'kept' else p.get('replacement')
        if v and v not in have: err.append(f'heat_rejection.levels: {v} rejects heat at this site and needs a level with its mode')
    if not err:
        for lv in levels:
            if 'radiative' in (lv.get('mode'), lv.get('sink_mode')):
                try: radiator_m2_per_kW(lv.get('radiator_K', lv.get('reject_K')), g['radiative_sink_K']['value'], g['radiator_emissivity']['value'])
                except ValueError as x: err.append(f'heat_rejection.levels ({lv["unit"]}): {x}')
    return err


def rows(prof, units=None):
    """[(level, unit, mode, duty kW, note)] for the selected site."""
    units = units or SC.graph_units(); g = group(prof); out = []
    for lv in group(prof)['levels']['value']:
        q = units[lv['unit']]['params'][lv['duty_param']]; m = lv['mode']; note = []
        if m == 'heat_pump':
            note.append(f'lift {lv["reject_K"] - lv["source_K"]:g} K, Carnot COP bound {carnot_cop(lv["source_K"], lv["reject_K"]):.2f}, to {lv["sink_mode"]}')
        if 'radiative' in (m, lv.get('sink_mode')):
            tr = lv.get('radiator_K', lv.get('reject_K')); a = radiator_m2_per_kW(tr, g['radiative_sink_K']['value'], g['radiator_emissivity']['value'])
            note.append(f'radiator at {tr:g} K: {a:.2f} m2 per kW, {a * q:.1f} m2 at duty')
        out.append((lv['level'], lv['unit'], m, q, '; '.join(note) or '-', lv.get('ref') or lv.get('register') or lv.get('owner')))
    return out
