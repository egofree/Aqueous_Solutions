# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Per-site placement and sizing of the locale-replacement units (X-LOC site models).

The scaling plan (flow_graph/param/scaling.py) eliminates reference units at a locale and
names a replacement unit of a different technology. The replacements are placeholders in
the reference graph - designed, not installed. This module places them per site:

  placements(sid)   the placeholder replacements a locale's plan names, with the sizing
                    that follows from that site's profile (heat-rejection radiator area,
                    worst-stretch storage energy) and the design record carried by the node
  apply(g, sid)     stamp those placements into a locale graph (params.site_placement);
                    idempotent, and a no-op for sites whose plan names no placeholder units
  stamp_worktree(wt, sid)   apply to the flow graph of a locale worktree (site_outputs)
  render()          docs-authority/SITE_UNITS.md: the placement register per locale

Sizes are computed from the site profile only (A-M-396/397 radiator class, A-M-402
storage interim, AQS-PLAN-011 section 5.5 balance) so the register is deterministic in
every worktree; where no profile value sizes a unit, the placement carries the design
record and states that the unit sizes at the locale design pass. Nothing here changes
the reference plant: the baseline graph is untouched.

    python3 -m flow_graph.param.site_units --write   # docs-authority/SITE_UNITS.md"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
GP = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')
OUT = 'docs-authority/SITE_UNITS.md'

import json as _json


def _graph(path=GP):
    return _json.load(open(path))


def _need_kw(g):
    return (g.get('mvs', {}).get('electrical', {}).get('need_kw', {}) or {}).get('value')


def _heat_level(prof, unit):
    grp = prof['groups'].get('heat_rejection', {}).get('entries', {})
    for lv in (grp.get('levels', {}).get('value') or []):
        if lv.get('unit') == unit:
            return lv, grp
    return None, grp


def _rad_panel(prof, node, g):
    from . import heat_rejection as HR
    lv, grp = _heat_level(prof, 'RAD_PANEL')
    if not lv:
        return {}
    rad_k = lv.get('radiator_K')
    sink = grp.get('radiative_sink_K', {}).get('value')
    eps = grp.get('radiator_emissivity', {}).get('value')
    duty = node.get('params', {}).get('rated_kW')
    out = {'radiator_K': rad_k, 'sink_K': sink, 'emissivity': eps, 'duty_kW': duty}
    if rad_k and sink and eps and duty:
        a1 = HR.radiator_m2_per_kW(rad_k, sink, eps)
        out['area_m2_per_kW'] = round(a1, 3)
        out['area_m2'] = round(a1 * duty, 1)
        out['basis'] = 'A-M-396 (sink), A-M-397 (emissivity); Stefan-Boltzmann'
    return out


def _lio_bat(prof, node, g):
    from . import portfolio as PF
    from . import drivers as DR
    d = DR.load()
    eta = DR.val(d, 'storage_round_trip')
    h = PF.stretch_hours(prof)
    f = PF.phi(prof)
    G = PF.mean_generation_per_kW(prof, eta)
    P = _need_kw(g)
    if not P:
        return {}
    delivered = (1 - f * G) * h * P
    out = {'stretch_h': h, 'demand_kW': P, 'storage_delivered_kWh': round(delivered, 1),
           'storage_charged_kWh': round(delivered / eta, 1),
           'basis': 'AQS-PLAN-011 section 5.5 worst-stretch balance; A-M-402 interim'}
    return out


SIZERS = {'RAD_PANEL': _rad_panel, 'LIO_BAT': _lio_bat}


def _sizing(rep, prof, node, g):
    sizer = SIZERS.get(rep)
    return sizer(prof, node, g) if sizer else {}


def placements(sid, g=None):
    """[(unit, placement dict)] for the placeholder replacements in sid's plan."""
    from . import site as S
    from . import scaling as SC
    g = g or _graph()
    units = SC.graph_units(g)
    prof = S.load_profile(sid)
    SC.resolve(prof, units)
    out = {}
    for a in SC.actions(prof):
        rep = a.get('replacement')
        node = units.get(rep) if rep else None
        if not node or node.get('presence') != 'placeholder':
            continue                       # kept reference units are not placements
        e = out.setdefault(rep, {'unit': rep, 'class': node.get('class'),
                                 'sector': node.get('sector_id'), 'replaces': [],
                                 'design': node.get('params', {}).get('design') or {}})
        if a['target'] not in e['replaces']:
            e['replaces'].append(a['target'])
    for rep, e in out.items():
        sizer = SIZERS.get(rep)
        e['sizing'] = _sizing(rep, prof, units[rep], g)
    return sorted(out.items())


def placements_all():
    from . import site as S
    rows = []
    for sid in S.available():
        if sid == S.BASELINE:
            continue
        for rep, e in placements(sid, _graph()):
            rows.append((sid, rep, e))
    return rows


def apply(g, sid):
    """Stamp the placements into a locale graph dict. Idempotent; no topology change."""
    from . import site as S
    from . import scaling as SC
    prof = S.load_profile(sid)
    units = SC.graph_units(g)
    SC.resolve(prof, units)
    n = 0
    for rep, e in placements(sid, g):
        node = units[rep]
        p = node.setdefault('params', {})
        if p.get('site_placement', {}).get('site') == sid and p['site_placement'].get('sizing') == e['sizing']:
            continue
        p['site_placement'] = {'site': sid, 'replaces': e['replaces'], 'sizing': e['sizing'],
                               'register': 'AQS-SITE-013 (SITE_UNITS.md)'}
        n += 1
    return n


def stamp_worktree(wt, sid):
    """Apply the placements to the flow graph of a locale worktree (site_outputs.run)."""
    from . import site as S
    if sid == S.BASELINE:
        return 0
    gp = os.path.join(wt, 'flow_graph', 'plant_flow_graph.json')
    g = _json.load(open(gp))
    n = apply(g, sid)
    if n or g != _json.load(open(gp)):
        open(gp, 'w').write(_json.dumps(g, indent=2) + '\n')
    return n


def render():
    from . import site as S
    rows = placements_all()
    L = ['# Site unit placements', '', 'Document number: AQS-SITE-013', 'Revision: A', 'Date: 2026-10-26',
         'Licence: CERN-OHL-S-2.0.', '',
         'Generated by `python3 -m flow_graph.param.site_units --write` from the committed site profiles '
         'and the placeholder replacement units (X-LOC site models). Do not edit by hand.', '',
         'A locale scaling plan eliminates reference units and names a replacement of a different '
         'technology. The replacements are designed placeholder units in the reference graph; at a '
         'locale they are placed and sized from that site profile. Sizes carry their basis; a unit '
         'without a profile-based size states that it sizes at the locale design pass.', '',
         'Table 1. Placements and sizing by locale', '',
         '| Site | Unit | Replaces | Sizing | Basis |', '| --- | --- | --- | --- | --- |']
    if not rows:
        L.append('| (no placements) | | | | |')
    for sid, rep, e in rows:
        sz = e['sizing'] or {}
        if sz:
            bits = []
            for k in ('area_m2', 'area_m2_per_kW', 'storage_delivered_kWh', 'duty_kW', 'radiator_K', 'stretch_h'):
                if k in sz:
                    bits.append(f'{k.replace("_", " ")} {sz[k]:g}')
            what = '; '.join(bits) if bits else 'design record'
            basis = sz.get('basis', '-')
        else:
            what = 'design record; sizes at the locale design pass'
            basis = (e['design'] or {}).get('basis', '-')
        L.append(f'| {sid} | {rep} | {", ".join(e["replaces"])} | {what} | {basis} |')
    L += ['', '## 2. Placement in the locale models', '',
          'During a locale regeneration the placements are stamped into the locale flow graph '
          '(`sites/<site_id>/flow_graph/plant_flow_graph.json`, `params.site_placement`); the reference '
          'graph is untouched. Units without a profile-based size keep their design record and size at '
          'the locale design pass.', '']
    return '\n'.join(L) + '\n'


if __name__ == '__main__':
    txt = render()
    if '--write' in sys.argv:
        open(os.path.join(ROOT, OUT), 'w').write(txt)
        print(f'{OUT}: written')
    else:
        sys.stdout.write(txt)
