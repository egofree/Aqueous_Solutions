# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Power portfolio and function redundancy per site (AQS-PLAN-011 section 5.5, task X-LOC-06).

The profile's power_portfolio group lists the sources (primary, backup, or flagged option), the
storage, the worst stretch and the oversize factor (bound to the driver pv_oversize_factor). Primary
sources share the mean generation G. Over a day with a worst stretch of h hours, a source delivers
the fraction f of its mean rate during the stretch; storage (round trip eta) carries the rest:

    24 G = P (24 - h) + (P - phi G) h / eta + phi G h,   phi = sum(share_i f_i)
    G = (P (24 - h) + P h / eta) / (24 - phi h + phi h / eta)

With PV alone and f = 0 this is the reference balance of sizing.power.pv_kWp, so pv_factor() is 1 at
the baseline. Installed capacity is the oversize factor times the balancing capacity. Fission and
other new technologies enter only as flagged options with role 'option'.

Redundancy (flow_graph/param/redundancy.json): every energy and life-support function keeps at least
two source units after the site's scaling actions. An import path never counts: an energy or
life-support unit is eliminated only with a replacement of a different technology (owner, 2026-10-25).

    python3 -m flow_graph.param.portfolio --write    # docs-authority/SITE_POWER.md for the selected site"""
import json, os, sys
from . import site as S, scaling as SC
from . import drivers as DR
from .refs import REFS

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
RED = os.path.join(HERE, 'redundancy.json')
OUT = 'docs-authority/SITE_POWER.md'
KINDS = ('pv', 'wind', 'geothermal', 'hydro', 'wave', 'ocean_thermal', 'fuel_cell', 'engine', 'fission', 'other')
STORAGE_KINDS = ('electrochemical', 'hydrogen', 'thermal', 'pumped_hydro', 'compressed_gas')
ROLES = ('primary', 'backup', 'option')
FLAG_ONLY = ('fission', 'other')


def _e(prof, key):
    g, e = key.split('.', 1)
    grp = prof['groups'].get(g, {})
    return (grp.get('entries') or {}).get(e)


def portfolio(prof):
    ents = prof['groups']['power_portfolio']['entries']
    return {k: ents[k]['value'] for k in ents}


def stretch_hours(prof):
    ws = portfolio(prof)['worst_stretch']
    return _e(prof, ws['hours_entry'])['value']


def phi(prof):
    return sum(s['share'] * s.get('stretch_output_frac', 0.0) for s in portfolio(prof)['sources'] if s['role'] == 'primary')


def mean_generation_per_kW(prof, eta):
    """G / P: mean primary generation per kW of average demand that closes the day through the worst stretch."""
    h = stretch_hours(prof); f = phi(prof)
    return ((24 - h) + h / eta) / (24 - f * h + f * h / eta)


def pv_factor(prof=None, eta=None):
    """Multiplier on the reference PV balance (sizing.power.pv_kWp): PV share times the worst-stretch
    correction. Exactly 1.0 for PV alone with no output in the stretch."""
    prof = prof or S.load_profile()
    if eta is None: eta = DR.val(DR.load(), 'storage_round_trip')
    pv = [s for s in portfolio(prof)['sources'] if s['role'] == 'primary' and s['kind'] == 'pv']
    if not pv: return 0.0
    h = stretch_hours(prof); f = phi(prof)
    return pv[0]['share'] * (24 / (24 - f * h + f * h / eta))


def validate(prof, units=None, plan=None):
    units = units or SC.graph_units(); err = []
    pf = portfolio(prof); prim = []
    for i, s in enumerate(pf['sources']):
        k = f'power_portfolio.sources[{i}]'
        if not (s.get('ref') or s.get('register') or s.get('owner')): err.append(f'{k}: no ref, register id or owner basis')
        if s.get('ref') and s['ref'] not in REFS: err.append(f'{k}: unknown ref {s["ref"]}')
        if s.get('kind') not in KINDS: err.append(f'{k}: kind {s.get("kind")!r} is not one of {", ".join(KINDS)}')
        if s.get('role') not in ROLES: err.append(f'{k}: role {s.get("role")!r} is not one of {", ".join(ROLES)}'); continue
        if s.get('kind') in FLAG_ONLY and not (s['role'] == 'option' and s.get('flagged_option') is True):
            err.append(f'{k}: {s["kind"]} enters only as a flagged option, with its own study before it enters a balance')
        if s.get('unit') not in units: err.append(f'{k}: unit {s.get("unit")!r} is not in the graph')
        elif plan and s['role'] != 'option' and plan.get(s['unit'], {}).get('status') == 'eliminated':
            err.append(f'{k}: {s["unit"]} is eliminated by the scaling actions')
        if s['role'] == 'primary':
            prim.append(s)
            if not (isinstance(s.get('share'), (int, float)) and 0 < s['share'] <= 1): err.append(f'{k}: a primary source needs a share above 0 and at most 1')
            f = s.get('stretch_output_frac', 0.0)
            if not (isinstance(f, (int, float)) and 0 <= f <= 1): err.append(f'{k}: stretch_output_frac must lie between 0 and 1')
            if s.get('kind') == 'pv':
                if not _e(prof, s.get('resource', '')): err.append(f'{k}: PV needs its resource entry ({s.get("resource")!r}) in the profile')
            elif not (isinstance(s.get('capacity_factor'), (int, float)) and 0 < s['capacity_factor'] <= 1):
                err.append(f'{k}: a primary {s.get("kind")} source needs a capacity factor above 0 and at most 1, with its basis')
    if not prim: err.append('power_portfolio.sources: no primary source')
    elif abs(sum(s.get('share', 0) for s in prim if isinstance(s.get('share'), (int, float))) - 1) > 1e-9:
        err.append('power_portfolio.sources: primary shares must sum to 1')
    if len([s for s in prim if s.get('kind') == 'pv']) > 1: err.append('power_portfolio.sources: one PV entry per site')
    for i, st in enumerate(pf['storage']):
        if st.get('kind') not in STORAGE_KINDS: err.append(f'power_portfolio.storage[{i}]: kind {st.get("kind")!r} is not one of {", ".join(STORAGE_KINDS)}')
        if st.get('unit') not in units: err.append(f'power_portfolio.storage[{i}]: unit {st.get("unit")!r} is not in the graph')
    ws = pf['worst_stretch']; he = _e(prof, str(ws.get('hours_entry', '')))
    if not he: err.append(f'power_portfolio.worst_stretch: hours entry {ws.get("hours_entry")!r} is not in the profile')
    elif not (0 < he['value'] <= 24):
        err.append('power_portfolio.worst_stretch: a stretch longer than a day needs the seasonal storage model (with the first polar locale, X-LOC-08)')
    return err


def redundancy(prof, units=None, plan=None, red=None):
    """Return ({function: [(source, count, how)]}, errors) after the site's scaling actions."""
    units = units or SC.graph_units(); red = red or json.load(open(RED))
    if plan is None: plan = SC.resolve(prof, units)[0]
    out, err = {}, []
    for fn, spec in red['functions'].items():
        rows = []
        for u, n in spec['sources'].items():
            p = plan.get(u)
            if p is None: continue                                   # not present in the graph
            if p['status'] == 'kept': rows.append((u, n * p['count'], 'kept'))
            elif p['status'] == 'replaced' or (p['status'] == 'eliminated' and p['replacement']):
                rows.append((p['replacement'], 1, f'replaces {u}'))
        out[fn] = rows
        if sum(r[1] for r in rows) < 2:
            err.append(f'{fn} ({spec["class"].replace("_", "-")}): {sum(r[1] for r in rows)} source unit(s) after the scaling actions; the redundancy rule needs a spare or a source of a different technology')
    return out, err


def check(sid=None):
    prof = S.load_profile(sid); units = SC.graph_units()
    plan, err = SC.resolve(prof, units)
    err += validate(prof, units, plan) + redundancy(prof, units, plan)[1]
    if err: raise SystemExit('site power: ' + '; '.join(err))
    return plan


def render(sid=None):
    prof = S.load_profile(sid); plan = check(sid); units = SC.graph_units()
    d = DR.load(); eta = DR.val(d, 'storage_round_trip'); pf = portfolio(prof)
    h = stretch_hours(prof); f = phi(prof); G = mean_generation_per_kW(prof, eta); ov = pf['oversize_factor']
    L = ['# Site power portfolio and redundancy', '', 'Document number: AQS-SITE-005', 'Revision: A', 'Date: 2026-10-25', '',
         'Generated by `python3 -m flow_graph.param.portfolio --write` from the selected site profile, '
         '`flow_graph/param/redundancy.json` and the flow graph (AQS-PLAN-011 section 5.5). Do not edit by hand.', '',
         f'Site: `{prof["site_id"]}`.', '', '## 1. Balance through the worst stretch', '',
         'Primary sources share the mean generation G. During the worst stretch of h hours a source gives the fraction f of its mean rate, '
         'and storage with round-trip efficiency eta carries the rest of the demand P:', '',
         '`G = (P (24 - h) + P h / eta) / (24 - phi h + phi h / eta)`, with `phi` the share-weighted f of the primary sources.', '',
         'Values are per kW of average demand, so they hold for any plant size. Installed capacity is the oversize factor times the balancing capacity.', '',
         'Table 1. Balance per kW of average demand', '', '| Quantity | Value | Basis |', '| --- | --- | --- |',
         f'| Worst stretch | {pf["worst_stretch"]["kind"]}, {h:g} h | `{pf["worst_stretch"]["hours_entry"]}` |',
         f'| Storage round trip, eta | {eta:g} | driver `storage_round_trip` |',
         f'| phi | {f:g} | primary sources, Table 2 |',
         f'| Mean generation G / P | {G:.4f} | equation above |',
         f'| Energy through storage per kW | {(1 - f * G) * h:.3f} kWh delivered, {(1 - f * G) * h / eta:.3f} kWh charged | (P - phi G) h |',
         f'| Oversize factor | {ov:g} | `power_portfolio.oversize_factor` (driver `pv_oversize_factor`) |',
         f'| PV factor on the reference balance | {pv_factor(prof, eta):g} | `pv_factor()`; 1 for PV alone |', '',
         '## 2. Sources', '', 'Table 2 lists the sources in the profile.', '', 'Table 2. Power sources', '',
         '| Source | Kind | Unit | Role | Share | f in stretch | Balancing mean kW per kW | Basis |', '| --- | --- | --- | --- | --- | --- | --- | --- |']
    for s in pf['sources']:
        prim = s['role'] == 'primary'
        share = s['share'] if prim else '-'; fr = s.get('stretch_output_frac', 0.0) if prim else '-'
        gen = f"{s['share'] * G:.4f}" if prim else '-'
        role = s['role'] + (' (flagged)' if s.get('flagged_option') else '')
        L.append(f"| {s['id']} | {s['kind']} | {s['unit']} | {role} | {share} | {fr} | {gen} | {s.get('ref') or s.get('register') or s.get('owner')} |")
    L += ['', 'Table 3. Storage', '', '| Kind | Unit |', '| --- | --- |'] + [f'| {st["kind"]} | {st["unit"]} |' for st in pf['storage']]
    rows, _ = redundancy(prof, units, plan)
    red = json.load(open(RED))
    L += ['', '## 3. Redundancy of energy and life-support functions', '',
          'Each function keeps at least two source units after the scaling actions: a spare, or a source of a different technology (AGENTS.md, Redundancy). '
          'An import path does not count as a source.', '',
          'Table 4. Sources per function', '', '| Function | Class | Sources | Source units | Basis |', '| --- | --- | --- | --- | --- |']
    for fn, rr in rows.items():
        spec = red['functions'][fn]
        L.append(f'| {fn.replace("_", " ")} | {spec["class"].replace("_", " ")} | ' + ', '.join(f'{u} x{n}' + ('' if how == 'kept' else f' ({how})') for u, n, how in rr)
                 + f' | {sum(r[1] for r in rr)} | {spec["basis"]} |')
    return '\n'.join(L) + '\n'


if __name__ == '__main__':
    txt = render()
    if '--write' in sys.argv:
        open(os.path.join(ROOT, OUT), 'w').write(txt); print(f'{OUT}: written')
    else:
        sys.stdout.write(txt)
