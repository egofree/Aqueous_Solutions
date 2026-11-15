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


def _dust_record(prof):
    """The profile's dust-stretch design record (the F-20261113-01 study the mars portfolio cites)."""
    return ((prof.get('groups', {}).get('power_portfolio', {}).get('entries', {})
             .get('dust_stretch_design', {}) or {}).get('value') or {})


def _demand_kw(g):
    """The demand a locale whose portfolio closes on a non-PV source books: the converged need minus the
    EXT_HALL roof extension, which exists to carry the roof PV and is not built at such a locale
    (write_graph power generic path books the base plate, A-M-231/A-M-234)."""
    P = _need_kw(g)
    if not P:
        return 0.0
    ext = g and {n['unit_id']: n for n in g['nodes']}.get('EXT_HALL')
    q = (ext or {}).get('continuous_kw')
    v = q.get('value') if isinstance(q, dict) else q
    return P - (float(v) if isinstance(v, (int, float)) else 0.0)


def _fsp_40k(prof, node, g):
    """Dust-season fission sizing (F-20261113-01): through the dust stretch the PV share delivers only
    its stretch fraction of its mean rate, and the deficit is carried in NASA FSP 40 kW_e units with
    one installed spare (N+1). Inputs: the profile's worst-stretch balance and its dust-stretch design
    record; the unit rating is the node's published NASA_FSP rating. No count is hard-coded."""
    import math
    from . import portfolio as PF
    from . import drivers as DR
    d = DR.load(); eta = DR.val(d, 'storage_round_trip')
    P = _demand_kw(g)
    unit_kw = (node.get('params') or {}).get('unit_kW_e')
    if not P or not unit_kw:
        return {}
    rec = _dust_record(prof)
    frac = rec.get('pv_stretch_output_frac')
    if frac is None:                                  # fall back to the portfolio's PV entry
        pv = [s for s in PF.portfolio(prof)['sources'] if s['role'] == 'primary' and s.get('kind') == 'pv']
        frac = pv[0].get('stretch_output_frac', 0.0) if pv else 0.0
    share_pv = next((s['share'] for s in PF.portfolio(prof)['sources']
                     if s['role'] == 'primary' and s.get('kind') == 'pv'), 0.0)
    G = PF.mean_generation_per_kW(prof, eta) * P      # mean total generation at the mix shares
    pv_dust = frac * share_pv * G                     # PV output through the dust stretch
    deficit = P - pv_dust
    duty = math.ceil(deficit / unit_kw)
    return {'demand_kW': round(P, 2), 'mean_generation_kW': round(G, 2),
            'pv_share': share_pv, 'dust_pv_output_frac': frac,
            'pv_dust_output_kW': round(pv_dust, 2), 'dust_deficit_kW': round(deficit, 2),
            'unit_kW_e': unit_kw, 'count_duty': duty, 'count_installed_n_plus_1': duty + 1,
            'installed_kW_e': round((duty + 1) * unit_kw, 1),
            'basis': 'AQS-PLAN-011 section 5.5 worst-stretch balance at the portfolio shares; dust fraction '
                     'from power_portfolio.dust_stretch_design (F-20261113-01); unit rating NASA_FSP; '
                     'one installed spare per the N+1 rule'}


def _mmrtg(prof, node, g):
    """RTG trickle sizing (F-20261113-01): the controls-and-instruments slice of the critical list
    (backup_fuel.critical_list, the single source) carried in NASA MMRTG 110 W_e units. The kW-class
    criticals stay on the fission base and the fuel cell; no count is hard-coded."""
    import math
    import flow_graph.param.backup_fuel as BF
    from . import drivers as DR
    d = DR.load()
    crit = BF.critical_list({n['unit_id']: n for n in g['nodes']}, d)
    trickle_kw = crit.get('controls and instruments')
    unit_w = (node.get('params') or {}).get('unit_W_e')
    if not trickle_kw or not unit_w:
        return {}
    count = math.ceil(trickle_kw * 1000.0 / unit_w)
    return {'critical_list_kW': round(sum(crit.values()), 2), 'controls_trickle_kW': trickle_kw,
            'unit_W_e': unit_w, 'count': count, 'carries_W_e': round(count * unit_w, 1),
            'basis': 'backup_fuel.critical_list controls slice (AQS-ELEC-007); unit rating NASA_RTG; '
                     'the kW-class criticals stay on the fission base and the fuel cell (F-20261113-01)'}


SIZERS = {'RAD_PANEL': _rad_panel, 'LIO_BAT': _lio_bat, 'FSP_40K': _fsp_40k, 'MMRTG': _mmrtg}


def _sizing(rep, prof, node, g):
    sizer = SIZERS.get(rep)
    return sizer(prof, node, g) if sizer else {}


def placements(sid, g=None):
    """[(unit, placement dict)] for the placeholder units sid's plan and portfolio name."""
    from . import site as S
    from . import scaling as SC
    from . import portfolio as PF
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
    for s in PF.portfolio(prof).get('sources', []):
        # a designed source the portfolio names (role primary or backup): placed and sized per
        # locale from its profile record; flagged options (role option) stay studies, not placements
        node = units.get(s.get('unit'))
        if not node or node.get('presence') != 'placeholder' or s.get('role') not in ('primary', 'backup'):
            continue
        out.setdefault(s['unit'], {'unit': s['unit'], 'class': node.get('class'),
                                   'sector': node.get('sector_id'), 'replaces': [],
                                   'design': node.get('params', {}).get('design') or {}})
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
            for k in ('area_m2', 'area_m2_per_kW', 'storage_delivered_kWh', 'duty_kW', 'radiator_K', 'stretch_h',
                      'count_duty', 'count_installed_n_plus_1', 'installed_kW_e', 'dust_deficit_kW', 'count', 'carries_W_e'):
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
