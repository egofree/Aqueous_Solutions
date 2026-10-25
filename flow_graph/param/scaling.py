# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Sector and unit scaling per site (AQS-PLAN-011 section 5, task X-LOC-05).

The profile's scaling group lists actions on a unit or a sector ('sector:<SECTOR_ID>'):
  size       factor > 0, biases the solver's size (section 5.2)
  duplicate  count >= 2 parallel units
  replace    a unit of a different technology (another class) performing the same function
  eliminate  the function is not performed at the site; needs an import path or a replacement
Each action carries a basis (ref, register or owner). Unit needs (flow_graph/param/unit_needs.json)
are checked against the profile's capabilities group: a present unit whose need the site does not
meet must be replaced or eliminated. An energy or life-support unit may be eliminated only with a
replacement of a different technology; an import path alone does not keep the function (AGENTS.md,
Redundancy).

    python3 -m flow_graph.param.scaling --write    # docs-authority/SITE_SCALING.md for the selected site"""
import json, os, sys
from . import site as S
from .refs import REFS

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
NEEDS = os.path.join(HERE, 'unit_needs.json')
GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')
OUT = 'docs-authority/SITE_SCALING.md'
ACTIONS = ('size', 'duplicate', 'replace', 'eliminate')
GUARDED = ('energy', 'life_support')
P_TRIPLE_PA = 611.657   # triple point pressure of water [IAPWS_IF97]


def needs_table():
    return json.load(open(NEEDS))


def graph_units(graph=None):
    g = graph or json.load(open(GRAPH))
    return {n['unit_id']: n for n in g['nodes']}


def unit_needs(u, node, nt):
    over = nt['by_unit'].get(u, {})
    return sorted(over['needs'] if 'needs' in over else nt['by_class'].get(node.get('class'), []))


def _red_sources():
    r = json.load(open(os.path.join(HERE, 'redundancy.json')))
    return {u: f['class'] for f in r['functions'].values() for u in f['sources']}


def function(u, node, nt):
    """energy, life_support or process: the unit map, then the units named in redundancy.json, then the sector."""
    return nt['function_by_unit'].get(u) or _red_sources().get(u) or nt['function_by_sector'].get(node.get('sector_id')) or 'process'


def capabilities(prof):
    grp = prof['groups']['capabilities']
    return {k for k, e in grp['entries'].items() if e['value'] is True}


def consistency(prof, have):
    """A capability may not claim more than the profile's physical values allow."""
    err = []; g = prof['groups']; at = g['atmosphere']['entries']
    if g['gravity']['entries']['g_m_s2']['value'] <= 0:
        err += [f'capabilities.{n}: claimed with no apparent gravity' for n in ('buoyant_separation', 'free_surface') if n in have]
    for n, flag in (('vent_sink', 'vent_sink'), ('air_oxidant', 'oxidant')):
        if (n in have) != bool(at[flag]['value']): err.append(f'capabilities.{n}: differs from atmosphere.{flag}')
    if 'liquid_water_at_ambient' in have and at['pressure_Pa']['value'] <= P_TRIPLE_PA:
        err.append('capabilities.liquid_water_at_ambient: external pressure is at or below the triple point of water')
    if 'ground_contact' in have and 'entries' not in g['ground']:
        err.append('capabilities.ground_contact: claimed with no ground group values')
    return err


def actions(prof):
    grp = prof['groups']['scaling']
    return grp['entries']['actions']['value'] if 'entries' in grp else []


def _targets(t, units):
    if t.startswith('sector:'):
        return sorted(u for u, n in units.items() if n.get('sector_id') == t[7:])
    return [t] if t in units else []


def resolve(prof, units=None, nt=None):
    """Return (plan, errors). plan: unit -> {'status', 'factor', 'count', 'replacement', 'import_path'}."""
    units = units or graph_units(); nt = nt or needs_table(); err = []
    plan = {u: {'status': 'kept', 'factor': 1.0, 'count': 1, 'replacement': None, 'import_path': None}
            for u, n in units.items() if n.get('presence') == 'present'}
    have = capabilities(prof)
    for need in sorted(have - set(nt['needs'])): err.append(f'capabilities.{need}: not a need in unit_needs.json')
    err += consistency(prof, have)
    for i, a in enumerate(actions(prof)):
        k = f'scaling.actions[{i}]'
        if not isinstance(a, dict): err.append(f'{k}: not an object'); continue
        if not (a.get('ref') or a.get('register') or a.get('owner')): err.append(f'{k}: no ref, register id or owner basis')
        if a.get('ref') and a['ref'] not in REFS: err.append(f'{k}: unknown ref {a["ref"]}')
        act, tgt = a.get('action'), str(a.get('target', ''))
        if act not in ACTIONS: err.append(f'{k}: action {act!r} is not one of {", ".join(ACTIONS)}'); continue
        ts = _targets(tgt, units)
        if not ts: err.append(f'{k}: target {tgt!r} is not a unit or a sector in the graph'); continue
        rep = a.get('replacement')
        if act == 'size' and not (isinstance(a.get('factor'), (int, float)) and a['factor'] > 0):
            err.append(f'{k}: size needs a factor above zero')
        if act == 'duplicate' and not (isinstance(a.get('count'), int) and a['count'] >= 2):
            err.append(f'{k}: duplicate needs a whole count of 2 or more')
        if act in ('replace', 'eliminate') and rep is not None:
            if rep not in units: err.append(f'{k}: replacement {rep!r} is not a unit in the graph'); rep = None
        if act == 'replace' and rep is None and not any(f'{k}: replacement' in e for e in err):
            err.append(f'{k}: replace needs a replacement unit')
        if act == 'eliminate' and rep is None and not a.get('import_path'):
            err.append(f'{k}: eliminate needs an import path or a replacement')
        for u in ts:
            if u not in plan: continue
            p = plan[u]; fn = function(u, units[u], nt)
            if act in ('replace', 'eliminate') and p['status'] != 'kept':
                err.append(f'{k}: {u} is already {p["status"]}')
            if act == 'size': p['factor'] = a.get('factor', 1.0)
            elif act == 'duplicate': p['count'] = a.get('count', 1)
            else:
                p['status'] = 'replaced' if act == 'replace' else 'eliminated'
                p['replacement'] = rep; p['import_path'] = a.get('import_path')
                if rep is not None:
                    if units[rep].get('class') == units[u].get('class'):
                        err.append(f'{k}: {rep} is the same technology ({units[u].get("class")}) as {u}; use duplicate or size')
                    if function(rep, units[rep], nt) != fn:
                        err.append(f'{k}: {rep} ({function(rep, units[rep], nt)}) does not perform the {fn} function of {u}')
                if act == 'eliminate' and fn in GUARDED and rep is None:
                    err.append(f'{k}: {u} is a {fn.replace("_", "-")} unit; eliminating it needs a replacement of a different technology, an import path alone does not keep the function')
    for u, p in plan.items():
        if p['status'] != 'kept': continue
        miss = [n for n in unit_needs(u, units[u], nt) if n not in have]
        if miss: err.append(f'{u}: needs {", ".join(miss)}, which the site does not provide; replace or eliminate it')
    for u, p in plan.items():
        r = p['replacement']
        if r and r in units:
            miss = [n for n in unit_needs(r, units[r], nt) if n not in have]
            if miss: err.append(f'{u}: replacement {r} needs {", ".join(miss)}, which the site does not provide')
    return plan, err


def check(sid=None):
    prof = S.load_profile(sid)
    plan, err = resolve(prof)
    if err: raise SystemExit('site scaling: ' + '; '.join(err))
    return plan


def render(sid=None):
    prof = S.load_profile(sid); units = graph_units(); nt = needs_table()
    plan, err = resolve(prof, units, nt)
    if err: raise SystemExit('site scaling: ' + '; '.join(err))
    have = capabilities(prof); acts = actions(prof)
    L = ['# Site scaling', '', 'Document number: AQS-SITE-004', 'Revision: A', 'Date: 2026-10-25', '',
         'Generated by `python3 -m flow_graph.param.scaling --write` from the selected site profile, '
         '`flow_graph/param/unit_needs.json` and the flow graph (AQS-PLAN-011 section 5). Do not edit by hand.', '',
         f'Site: `{prof["site_id"]}`.', '', '## 1. Site capabilities', '',
         'Table 1 lists each environmental need and whether the site provides it.', '', 'Table 1. Capabilities', '',
         '| Need | Meaning | Provided | Basis |', '| --- | --- | --- | --- |']
    for n, m in nt['needs'].items():
        e = prof['groups']['capabilities']['entries'][n]
        L.append(f'| {n} | {m} | {"yes" if n in have else "no"} | {e.get("ref") or e.get("register") or e.get("owner")} |')
    L += ['', '## 2. Scaling actions', '']
    if not acts:
        L += ['The profile applies no scaling action: every unit is built as in the reference plant.']
    else:
        L += ['Table 2 lists the actions in the profile.', '', 'Table 2. Scaling actions', '',
              '| Target | Action | Factor or count | Replacement or import path | Basis |', '| --- | --- | --- | --- | --- |']
        for a in acts:
            fc = a.get('factor', a.get('count', ''))
            ri = a.get('replacement') or (json.dumps(a['import_path']) if a.get('import_path') else '')
            L.append(f'| {a["target"]} | {a["action"]} | {fc} | {ri} | {a.get("ref") or a.get("register") or a.get("owner")} |')
    L += ['', '## 3. Units with environmental needs', '',
          'Table 3 lists every present unit that has an environmental need, with its function and its status at this site.', '',
          'Table 3. Unit needs and status', '', '| Unit | Class | Function | Needs | Status |', '| --- | --- | --- | --- | --- |']
    for u in sorted(plan):
        nd = unit_needs(u, units[u], nt)
        if nd or plan[u]['status'] != 'kept':
            st = plan[u]['status'] + (f' by {plan[u]["replacement"]}' if plan[u]['replacement'] else '')
            L.append(f'| {u} | {units[u].get("class")} | {function(u, units[u], nt).replace("_", " ")} | {", ".join(nd) or "-"} | {st} |')
    return '\n'.join(L) + '\n'


if __name__ == '__main__':
    txt = render()
    if '--write' in sys.argv:
        open(os.path.join(ROOT, OUT), 'w').write(txt); print(f'{OUT}: written')
    else:
        sys.stdout.write(txt)
