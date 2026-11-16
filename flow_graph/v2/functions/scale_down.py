"""The scale-down analysis family (family migration; reference writer
flow_graph/param/scale_down.py, ledger row `scale_down`, section F, MIXED:
split analysis -> this function, doc+json -> the renderer wave).

AQS-SCALE-UR-001: what goes unreclaimed when a sector is switched off, and how
far each unit can shrink. Section 3 - a mass and energy balance on a control
volume drawn round one sector: every stream that crosses the boundary loses one
end (no_sink / no_source), electrical feeds from the supply sector and dock
trade simply stop, and a zero-rate stream is listed as inactive. Section 4 -
throughput proportional to the scale factor s (A-M-329), with per-unit-type
limits: heat stores stop delivering at s = standing loss / recovered heat in
(INCROPERA7 conduction; ASTM_C680 insulated vessel), molten-salt cells are
held molten so their energy per kilogram rises by (s*D + H)/(s*(D + H))
(A-M-330), batch melters campaign below one heat per day, and polymer kettles
campaign on one batch (A-M-331).

The pure kernel is analyse(g): a function of the plain committed-graph
structure only (nodes, edges, mvs.sectors). Its golden is the committed
design_tool/aqs_design_tool/data/scale_down.json, which this kernel
reproduces exactly; the renderer wave serializes it (json, indent 1) and
renders docs-authority/SCALE_DOWN_UNRECLAIMED.md beside it.

Float doctrine: the reference writer solves in float space (round() on
doubles, '%.3g' cells), so this is a float replica of that chain over the
same plain books - no float literals (the lint holds this); the constants
enter as the decimal strings of the v1 literals (BATCH_FILL 0.7, LATEX_SOLIDS
0.25, LATEX_DENSITY_KG_L 1.1, the scale ladder). Pure: no I/O, no wall-clock,
no RNG.
"""
import math

SUPPLY_SECTORS = {'ELEC'}       # an electrical feed stops when its load is off
TRADE_SECTOR = 'DOCK'           # imports are not bought; exports and vents stop
BATCH_FILL = float('0.7')       # A-M-331
LATEX_SOLIDS = float('0.25')    # A-M-331
LATEX_DENSITY_KG_L = float('1.1')  # A-M-331
SCALES = tuple(float(s) for s in ('1.0', '0.75', '0.5', '0.25', '0.1'))


def rate(e):
    r = e.get('rate') or {}
    return r.get('value'), r.get('unit')


def fmt(v, unit=''):
    if v is None:
        return 'not yet rated'
    s = f'{v:.3g}' if abs(v) < 100 else f'{v:,.0f}'
    return f'{s} {unit}'.strip()


def classify(e, sector):
    """Role of a boundary stream when `sector` is switched off."""
    out = e['from_sector_id'] == sector
    other = e['to_sector_id'] if out else e['from_sector_id']
    if not out and other in SUPPLY_SECTORS and ('elec' in e.get('layers', []) or e.get('phase') == 'electric'):
        return 'stops', other
    if other == TRADE_SECTOR:
        return 'stops', other
    return ('no_source' if out else 'no_sink'), other


def boundary(g):
    sectors = [s['sector_id'] for s in g['mvs']['sectors']]
    res = {}
    for s in sectors:
        rows = {'no_sink': [], 'no_source': [], 'stops': [], 'inactive': []}
        for e in g['edges']:
            if (e['from_sector_id'] == s) == (e['to_sector_id'] == s):
                continue
            role, other = classify(e, s)
            v, u = rate(e)
            item = {'stream_id': e['stream_id'], 'from': e['from_unit_id'], 'to': e['to_unit_id'], 'other_sector': other,
                    'rate': v, 'unit': u, 'carries': e.get('carries', '')}
            rows['inactive' if v == 0 else role].append(item)
        for k in rows:
            rows[k].sort(key=lambda x: x['stream_id'])
        res[s] = rows
    return res


def heat_limits(g, N):
    """Each heat store: recovered heat in against standing loss (INCROPERA7 conduction; ASTM_C680 insulated vessel)."""
    out = []
    for u, n in sorted(N.items()):
        if n.get('class') != 'heat_battery':
            continue
        d = n['params'].get('design', {})
        loss_edges = [e for e in g['edges'] if e['from_unit_id'] == u and e['to_unit_id'] == 'BOUNDARY_EXPORT']
        loss = sum(rate(e)[0] or 0 for e in loss_edges) if loss_edges else (d.get('issued_loss_kW') or d.get('standing_loss_kW'))
        twin = {v for v, m in N.items() if m.get('class') == 'heat_battery' and m['params'].get('design', {}).get('tier') == d.get('tier')}
        ins = [e for e in g['edges'] if e['to_unit_id'] == u and e['from_unit_id'] not in twin   # A/B cross-ties cancel
               and 'elec' not in e.get('layers', []) and e.get('phase') != 'electric']             # electric trim is purchased
        vals = [rate(e)[0] for e in ins]
        I = sum(v for v in vals if v is not None) or None     # an unrated input counts as zero: the limit errs high
        unrated = [e['stream_id'] for e, v in zip(ins, vals) if v is None]
        out.append({'unit_id': u, 'tier': d.get('tier'), 'loss_kW': loss, 'recovered_in_kW': I, 'unrated_inputs': unrated,
                    'inputs': [e['stream_id'] for e in ins], 'hold_kWh': d.get('hold_kWh_th'),
                    'hold_hours': round(d['hold_kWh_th'] / loss, 1) if loss and d.get('hold_kWh_th') else None,
                    's_min': round(loss / I, 3) if I and loss else None,
                    's_min_if_store_shrinks': round((loss / I) ** 3, 4) if I and loss else None})
    return out


def cell_limits(N, sector):
    out = []
    for u, n in sorted(N.items()):
        if n.get('sector_id') != sector:
            continue
        s = n['params'].get('sizing', {})
        if 'hold_kW' in s and 'dc_kW' in s:
            H, D = s['hold_kW'], s['dc_kW']
            out.append({'unit_id': u, 'hold_kW': H, 'dc_kW': D, 'hold_share': round(H / (H + D), 3) if H + D else None,
                        'energy_factor': {str(x): (round((x * D + H) / (x * (D + H)), 2) if D + H else None) for x in SCALES}})
    return out


def batch_limits(N, sector):
    out = []
    for u, n in sorted(N.items()):
        if n.get('sector_id') != sector:
            continue
        s = n['params'].get('sizing', {})
        if 'crucible_kg' in s and s.get('charge_kg_d'):
            c, q = s['crucible_kg'], s['charge_kg_d']
            out.append({'unit_id': u, 'crucible_kg': c, 'charge_kg_d': q, 'heats_d': s.get('heats_d'),
                        's_campaign': round(c / q, 3),
                        'days_between_heats': {str(x): round(max(float('1.0'), c / (q * x)), 1) for x in SCALES}})
    return out


def kettle_limits(g, N, sector):
    out = []
    for u, n in sorted(N.items()):
        if n.get('sector_id') != sector:
            continue
        d = n['params'].get('design', {})
        if not ('D_mm' in d and 'H_mm' in d and 'vessel' in d):
            continue
        V = math.pi / 4 * (d['D_mm'] / 1000) ** 2 * (d['H_mm'] / 1000) * 1000          # litres
        batch = V * BATCH_FILL * LATEX_DENSITY_KG_L * LATEX_SOLIDS
        prod = sum(v for k, v in d.items() if k in ('pvdf_kg_d', 'ptfe_kg_d') and isinstance(v, (int, float)))
        feeds = [e for e in g['edges'] if e['to_sector_id'] == sector and e['from_sector_id'] != sector
                 and e['from_sector_id'] not in SUPPLY_SECTORS | {TRADE_SECTOR} and (rate(e)[0] or 0) > 0
                 and e.get('phase') != 'G']        # gases stay in their source loop until a campaign draws them
        out.append({'unit_id': u, 'volume_L': round(V, 2), 'batch_kg': round(batch, 3), 'product_kg_d': prod,
                    'days_between_batches': {str(x): round(batch / (prod * x), 1) for x in SCALES} if prod else None,
                    'buffers': [{'stream_id': e['stream_id'], 'kg_per_campaign': round(rate(e)[0] * batch / prod, 2)} for e in feeds] if prod else []})
    return out


def analyse(g):
    """The full analysis book (the v1 analyse()): sector-off boundary tables,
    the HEAT/FOUNDRY/POLYMERS scale limits, and the heat-store derate rules.
    Pure function of the plain graph structure."""
    N = {n['unit_id']: n for n in g['nodes']}
    b = boundary(g)
    heat = heat_limits(g, N)
    rules = []
    for h in heat:
        if h['s_min']:
            rules.append({'id': f"heat_store_{h['unit_id']}", 'min_scale_m': h['s_min'], 'stream_ids': h['inputs'],
                          'sector_ids': ['HEAT'],
                          'detail': f"{h['unit_id']} loses more heat ({h['loss_kW']} kW standing loss) than it recovers below "
                                    f"s = {h['s_min']}; its recovered heat inputs are then unreclaimed"})
    return {
        '_about': 'Generated by flow_graph/param/scale_down.py from flow_graph/plant_flow_graph.json; see AQS-SCALE-UR-001.',
        'sector_off': b,
        'definitions': {s['sector_id']: s.get('sector_definition') for s in g['mvs']['sectors']},
        'limits': {'HEAT': {'stores': heat},
                   'FOUNDRY': {'cells': cell_limits(N, 'FOUNDRY'), 'batch_melters': batch_limits(N, 'FOUNDRY')},
                   'POLYMERS': {'kettles': kettle_limits(g, N, 'POLYMERS')}},
        'derate_rules': rules,
        'scales': list(SCALES),
    }
