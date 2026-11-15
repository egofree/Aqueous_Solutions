"""On-site CaCl2-MgCl2 brine recovery for the foundry pots, recovery first (task X-QA-11, A-M-496).

MG_POT and CA_POT took their chloride make-up at the dock (IA-MGCL2-MU / IA-CACL2-MU, process-chemical
imports, A-M-284). The make-up mass is not consumed in the plant sense: the MgCl2 share is the Kroll
salt-flux drag-out (foundry_kroll_dragout_frac of the retort MgCl2 gross) that cycles MG_POT -> flux ->
melt -> slag -> leach, and the CaCl2 share carries the Ca deoxidizer addition, whose Ca ends the day as
CaCl2 in the dross and leach liquor (the Ca_POT chlorine leaves separately as the IA-CA-CL2-SHIP product
export, netted against the new chloride the halite ore draws carry in). Both salts are therefore present
in the leach liquor at steady state: the HCl leach dissolves the design feed's silicate-oxide class
(AQS-ASSAY-001 section 3, silicate_oxide 18 % of the feed) as Ca and Mg chlorides, on top of the flux
drag-out. The recovery route crystallizes them back:

  BRINE_CRYS (agitated flash crystallizer, FOUNDRY sector) takes a leach-liquor side-stream
  (IA-BRINE-SRC, brine_crys_feed_kg_d) - the same pattern as the IA-LEACH-VCD / IA-VCD-BD pair -
  crystallizes the mixed CaCl2 / MgCl2 to the pot-feed rates, and returns the mother liquor
  (IA-BRINE-ML) to the leach, where the chlorides keep cycling. The pot feeds are unchanged in mass:
  the dock import edges retire, the same kg/d arrive from the crystallizer.

The crystallizer feed draw is sized well above the make-up need (the leach liquor carries order-kg/d of
dissolved Ca+Mg chlorides against the 0.156 kg/d draw), so the route does not lean on a precise brine
assay; the draw size and the heater load are drivers (A-M-496). The docks IA-CACL2-MU / IA-MGCL2-MU
retire here and their PENDING entries leave flow_graph/param/recovery.py with this module.

The pot-feed masses arrive from the foundry_poly solve dict s on the same write grid the retired import
edges carried (R(ca) + R(ca_cl2) / R(mg_ti) + R(cl2_ti) - R(mgcl2_ret)), so the pot electrochemistry
never sees the source swap.

Called from flow_graph/param/foundry_poly.py apply() after the pot feeds are rated.
Run: python3 -m flow_graph.param.salt_recovery   (dry-solve from the current graph rates)
"""
import json
from . import drivers as DR

TAG = 'X-RTE TF: on-site Kroll brine recovery (X-QA-11, A-M-496)'


def design(s=None, E=None, d=None):
    """Pot-feed rates on the foundry write grid. s = foundry_poly.solve() dict; without it the rates
    are read back from the still-present dock-import edges (standalone dry-solve on a graph where the
    route has not landed yet)."""
    d = d or DR.load()
    if s is not None:
        R = lambda x: round(x, 6)
        cacl2 = R(s['ca']) + R(s['ca_cl2'])
        mgcl2 = R(s['mg_ti']) + R(s['cl2_ti']) - R(s['mgcl2_ret'])
    else:
        E = E or {}
        cacl2 = float(E['IA-CACL2-MU']['rate']['value'] or 0)
        mgcl2 = float(E['IA-MGCL2-MU']['rate']['value'] or 0)
    feed = DR.val(d, 'brine_crys_feed_kg_d')
    assert feed >= cacl2 + mgcl2, \
        f'salt_recovery: the brine draw {feed:.4f} kg/d must carry the pot feeds {cacl2 + mgcl2:.4f} kg/d'
    return dict(cacl2_kg_d=cacl2, mgcl2_kg_d=mgcl2, feed_kg_d=feed, ml_kg_d=feed - cacl2 - mgcl2,
                kw=DR.val(d, 'brine_crys_kW'))


STREAMS = (('IA-BRINE-SRC', 'LEACH_CSTR_1', 'BRINE_CRYS', 'L',
            {'water': 0.85, 'CaCl2': 0.05, 'MgCl2': 0.04, 'NaCl': 0.04, 'other salts': 0.02},
            'feed_kg_d', 'leach-liquor side-stream to the crystallizer'),
           ('IA-BRINE-CACL2', 'BRINE_CRYS', 'CA_POT', 'L', {'CaCl2': 1.0},
            'cacl2_kg_d', 'crystallized CaCl2 to the calcium pot (recovered, was the dock import)'),
           ('IA-BRINE-MGCL2', 'BRINE_CRYS', 'MG_POT', 'L', {'MgCl2': 1.0},
            'mgcl2_kg_d', 'crystallized MgCl2 to the magnesium pot (recovered, was the dock import)'),
           ('IA-BRINE-ML', 'BRINE_CRYS', 'LEACH_CSTR_1', 'L',
            {'water': 0.922, 'CaCl2': 0.027, 'MgCl2': 0.022, 'NaCl': 0.021, 'other salts': 0.008},
            'ml_kg_d', 'mother liquor (residual chlorides) returned to the leach'))


def tf(g, E, s, d=None):
    """Create-or-rate the crystallizer node and streams; retire the dock imports."""
    from flow_graph.param.o2_close import _edge, _node
    d = d or DR.load()
    N = {n['unit_id']: n for n in g['nodes']}
    # locale degradation (AQS-SITE-010, X-QA-11 house rule): the route activates only where the
    # brine-bearing streams exist. A locale that eliminates the leach or the pots (leo eliminates
    # LEACH_CSTR_1, MG_POT and CA_POT at microgravity) has no chloride brine source and no pot feeds
    # to restore, so the crystallizer does not land there; the pot chloride rides that locale's own
    # feed arrangement and this writer simply skips.
    _hosts = ('LEACH_CSTR_1', 'CA_POT', 'MG_POT')
    if not all((N.get(u) or {}).get('presence') == 'present' for u in _hosts):
        return None
    r = design(s, E, d)
    assert abs(r['feed_kg_d'] - (r['cacl2_kg_d'] + r['mgcl2_kg_d'] + r['ml_kg_d'])) < 1e-9
    if 'BRINE_CRYS' not in N:
        n = _node('BRINE_CRYS', N['CA_POT']['sector_id'], 'precip', 'load',
                  'Brine crystallizer (A-M-496).', {})
        n['notes'] = 'Agitated flash crystallizer on a leach-liquor side-stream: crystallizes the CaCl2/MgCl2 ' \
                     'pot make-up out of the dissolved feed-assay and salt-flux chlorides and returns the mother ' \
                     'liquor to the leach (X-QA-11, A-M-496). Precipitation class: the crystal harvest is a ' \
                     'filter/centrifuge step, not a buoyant separation, so the unit lands wherever the leach and ' \
                     'the pots run.'
        g['nodes'].append(n); N['BRINE_CRYS'] = n
    N['BRINE_CRYS']['class'] = 'precip'   # re-stamped: precipitation class (unit_needs has no locale-critical need for it)
    for sid, a, b, ph, comp, key, carries in STREAMS:
        note = f"{TAG}: {key.replace('_kg_d', '')} = {r[key]:.6f} kg/d (salt_recovery.py)."
        if sid in E:
            assert (E[sid]['from_unit_id'], E[sid]['to_unit_id']) == (a, b), f'salt_recovery: {sid} names another stream'
        else:
            e = _edge(sid, a, b, ph, ['mass'], carries, r[key], 'kg/d',
                      N[a]['sector_id'], N[b]['sector_id'], comp, note)
            g['edges'].append(e); E[sid] = e
        e = E[sid]
        e.update(carries=carries, presence='present', composition=comp)
        e['rate'] = {'value': round(r[key], 6), 'unit': 'kg/d', 'status': 'study', 'note': note}
    N['BRINE_CRYS']['params']['design'] = {k: round(v, 6) if isinstance(v, float) else v for k, v in r.items()}
    N['BRINE_CRYS']['continuous_kw'] = {'value': round(r['kw'], 4), 'unit': 'kW', 'status': 'study',
                                        'note': f'{TAG}: crystallizer jacket and vacuum ejector at the '
                                                f'{r["feed_kg_d"]:.2f} kg/d side-stream (brine_crys_kW, A-M-496).'}
    if 'SF-BRINE_CRYS' not in E:
        e = _edge('SF-BRINE_CRYS', 'SOL_ARK_60K', 'BRINE_CRYS', 'E', ['elec'], '480 V AC', r['kw'], 'kW',
                  N['SOL_ARK_60K']['sector_id'], N['BRINE_CRYS']['sector_id'], None,
                  f'{TAG}: feed equal to BRINE_CRYS continuous_kw.')
        e['header'] = 'tray'; g['edges'].append(e); E['SF-BRINE_CRYS'] = e
    E['SF-BRINE_CRYS']['rate'] = {'value': round(r['kw'], 4), 'unit': 'kW', 'status': 'study',
                                  'note': f'{TAG}: feed equal to BRINE_CRYS continuous_kw.'}
    for sid, was in (('IA-CACL2-MU', 'CaCl2 brine concentrate'), ('IA-MGCL2-MU', 'CaCl2-MgCl2 brine concentrate')):
        E[sid]['presence'] = 'retired'
        E[sid]['carries'] = f'{was} (retired: BRINE_CRYS crystallizes the make-up out of the leach chlorides, X-QA-11)'
    return r


if __name__ == '__main__':
    g = json.load(open('flow_graph/plant_flow_graph.json')); E = {e['stream_id']: e for e in g['edges']}
    print(json.dumps(design(E=E), indent=1))
