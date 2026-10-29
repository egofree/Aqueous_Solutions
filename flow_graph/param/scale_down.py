# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Scale-down analysis: what goes unreclaimed when a sector is switched off, and how far each unit can shrink.

Generated outputs (do not edit them by hand):
  design_tool/aqs_design_tool/data/scale_down.json  data read by design_tool/aqs_design_tool/solver/scale_down_map.py
  docs-authority/SCALE_DOWN_UNRECLAIMED.md           the page (AQS-SCALE-UR-001)

Method (section numbers refer to the page):
  * Section 3. A mass and energy balance on a control volume drawn round one sector. When the sector is off, every
    stream that crosses the boundary loses one end. A stream from another sector loses its sink, so that material or
    heat is left unreclaimed. A stream to another sector loses its source, so that consumer goes short. Electrical
    feeds and dock imports simply stop, and dock exports and vents stop with the sector; neither is a closure gap.
  * Section 4. Throughput is taken as proportional to the scale factor s (assumption A-M-329). Each unit type is then
    checked for the smallest s at which it still works:
      - heat store: fixed standing loss L against recovered input s*I; it stops delivering heat at s = L/I;
      - molten-salt cell: hold power H is fixed and electrolysis power D scales with s, so energy per kilogram rises
        by (s*D + H) / (s*(D + H)); the bath is kept molten rather than cycled (A-M-330);
      - batch melter: fewer heats per day; below one heat per day it runs in campaigns with a scrap buffer of one
        crucible;
      - polymer kettle: campaigns of one kettle batch (A-M-331); the interval between campaigns grows as 1/s.

    python3 -m flow_graph.param.scale_down
"""
import json
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')
OUT_JSON = os.path.join(ROOT, 'design_tool', 'aqs_design_tool', 'data', 'scale_down.json')
OUT_MD = os.path.join(ROOT, 'docs-authority', 'SCALE_DOWN_UNRECLAIMED.md')

REVISION, DATE = 'F', '2026-10-29'
SUPPLY_SECTORS = {'ELEC'}       # an electrical feed stops when its load is off
TRADE_SECTOR = 'DOCK'           # imports are not bought; exports and vents stop
BATCH_FILL = 0.7                # A-M-331
LATEX_SOLIDS = 0.25             # A-M-331
LATEX_DENSITY_KG_L = 1.1        # A-M-331
SCALES = (1.0, 0.75, 0.5, 0.25, 0.1)


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
                        'days_between_heats': {str(x): round(max(1.0, c / (q * x)), 1) for x in SCALES}})
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


def analyse():
    g = json.load(open(GRAPH))
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


def table(head, rows):
    return ['| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)] + ['| ' + ' | '.join(map(str, r)) + ' |' for r in rows]


def page(a, units_off, hand_rules):
    L = []
    w = L.append
    w('# What goes unreclaimed when the plant is made smaller or a sector is switched off')
    w('')
    w('Document number: AQS-SCALE-UR-001  ')
    w(f'Revision: {REVISION}  ')
    w(f'Date: {DATE}  ')
    w('Generated by `flow_graph/param/scale_down.py` from the plant graph; do not edit by hand.  ')
    w('Not a PE stamp.')
    w('')
    L += table(['Rev', 'Description', 'Date'], [
        ['A', 'First map from switched-off sectors to the streams left unreclaimed', '2026-10-01'],
        ['B', 'Methanol and pumped-hydro scale notes; study-unit streams', '2026-10-01'],
        ['C', 'Unit-level map for units switched off inside a running sector', '2026-10-01'],
        ['D', 'Sector names brought to the current sector list', '2026-10-24'],
        ['E', 'Rewritten in plain language. Sector lists now computed from the graph by a balance on each sector, which '
              'closes the open FOUNDRY, POLYMERS and HEAT rows. Scale-down limits derived for those three sectors.', '2026-10-24'],
        ['F', 'Summary renamed purpose and scope; the revision history removed from the summary; the terms table captioned.', DATE]])
    w('')
    w('## 1. Purpose and scope')
    w('')
    w('The design tool lets a user plan a smaller plant, or switch parts of it off. The plant is designed so that every '
      'material and heat stream is used again somewhere: scrap is remelted, chlorine goes back to the leach, waste heat '
      'is stored and reused. When a part is missing, the streams it used to take in have nowhere to go, and the streams '
      'it used to send out stop arriving. This page lists those streams so the design tool reports them as unreclaimed '
      'resources, open problems to solve, instead of treating the plant as still closed.')
    w('')
    w('Two questions are answered here:')
    w('')
    w('1. If a sector is switched off, which streams are left unreclaimed? (Section 3.)')
    w('2. If the plant is built smaller, how small can each sector go before it stops working, and what does a '
      'smaller size cost? (Section 4.)')
    w('')
    w('Every list on this page is computed from the plant graph by a balance on each sector, and the size limits of '
      'section 4 come from the mass and energy balances of the sectors concerned.')
    w('')
    w('## 2. Terms')
    w('')
    w('Table 2.1 defines the terms used on this page.')
    w('')
    w('Table 2.1. Terms')
    w('')
    L += (table(['Term', 'Meaning'], [
        ['Sector', 'A group of units that does one job, such as FOUNDRY (metal production). The sector list is the plant graph\'s, AQS-SEC-001.'],
        ['Stream', 'A flow of material, heat or electricity between two units, named by its stream id in the plant graph.'],
        ['Unreclaimed resource', 'A stream that the full plant reuses but that has no destination (or no source) in the configuration being studied.'],
        ['Scale factor, s', 'The plant size relative to the baseline design (SCALE_M in AQS-SCALE-001). s = 0.5 is a plant with half the throughput.'],
        ['Campaign', 'Running a unit at its normal rate for part of the time, and storing feed between runs, instead of running it slowly all the time.'],
        ['Standing loss', 'Heat that leaks out of a hot vessel through its insulation whether or not it is in use.'],
    ]))
    w('')
    w('## 3. Switching a sector off')
    w('')
    w('### 3.1 Method')
    w('')
    w('Draw a boundary round the sector and list every stream that crosses it (a mass and energy balance on a control '
      'volume). When the sector is off, each of those streams loses one end:')
    w('')
    w('- A stream coming in from another sector loses its sink. The material or heat is left unreclaimed in the sector that makes it.')
    w('- A stream going out to another sector loses its source. That sector goes short of something it needs.')
    w('- Electrical feeds, including electric heaters that top up a heat store, and purchased imports stop. Exports and vents through the dock stop with the sector. Neither is a closure gap.')
    w('- A stream whose rate is zero in the current design carries nothing today. It is listed for completeness only.')
    w('')
    w('The generator recomputes these lists from the plant graph on every regeneration, so they follow design changes. The '
      'design tool reads the same data (`design_tool/aqs_design_tool/data/scale_down.json`).')
    w('')
    w('### 3.2 Results')
    w('')
    w('Tables 3.1 to 3.%d give, for each sector, the streams that cross its boundary and what happens to each when that '
      'sector is off. Rates are design rates from the plant graph; streams that carry nothing in the current design are '
      'left out.' % len(a['sector_off']))
    w('')
    what = {'no_sink': 'left without a sink: unreclaimed', 'no_source': 'left without a source: consumer goes short', 'stops': 'stops with the sector'}
    for k, (sid, r) in enumerate(a['sector_off'].items(), 1):
        w(f"Table 3.{k}. {sid} off. Sector type: {a['definitions'].get(sid) or 'not defined'}.")
        w('')
        rows = [[x['stream_id'], f"{x['from']} to {x['to']}", x['other_sector'], fmt(x['rate'], x['unit'] or ''), what[role]]
                for role in ('no_sink', 'no_source', 'stops') for x in r[role]]
        if rows:
            L.extend(table(['Stream', 'From and to', 'Other sector', 'Design rate', 'When the sector is off'], rows))
        else:
            w('No stream crosses this sector\'s boundary in the current design.')
        w('')
    w('### 3.3 Units switched off inside a running sector')
    w('')
    U = len(a['sector_off']) + 1
    w('Some units can be switched off while the rest of their sector runs. Table 3.%d lists those that have their own entry ' % U +
      'in the design tool (`UNIT_OFF_UNRECLAIMED` in `design_tool/aqs_design_tool/solver/scale_down_map.py`).')
    w('')
    w(f'Table 3.{U}. Streams left unreclaimed when a single unit is off')
    w('')
    L += table(['Unit off', 'Streams', 'Effect'], [[u, ', '.join(e['stream_ids']) or 'none', e['detail']] for u, e in units_off.items()])
    w('')
    w('## 4. Building the plant smaller')
    w('')
    w('### 4.1 Method')
    w('')
    w('Throughput is taken as proportional to the scale factor s (assumption A-M-329; AQS-SCALE-001 gives the baseline feed of '
      '150 kg/d at s = 1). Equipment does not shrink smoothly: a crucible, an electrolysis cell or a heat store has a '
      'smallest practical size, and some losses do not fall with throughput. For each unit type the question is therefore '
      'what stops working, or what gets worse, as s falls. Batch and campaign operation are the usual answer at small '
      'production rates [2]. Values used below come from the plant graph; values not yet confirmed by test are in the '
      'assumptions register with the test that will confirm them.')
    w('')
    lim = a['limits']
    w('### 4.2 HEAT: heat stores')
    w('')
    w('A heat store recovers waste heat from other sectors and gives it back later. Its recovered heat in is the waste heat it receives from other sectors plus the heat passed down from the store one tier hotter. Exchanges between the A and B twins of a tier cancel and are not counted, and purchased electric trim heat is not recovered heat. Its standing loss depends on its '
      'surface area, insulation and temperature, not on how much heat passes through it [3, 4]. If the store keeps its '
      'size while the plant shrinks, the recovered heat falls in proportion to s but the loss does not. The store stops '
      'delivering any useful heat when')
    w('')
    w('    s x (recovered heat in) = standing loss,   that is   s_min = standing loss / recovered heat in.')
    w('')
    w('Where an input is not yet rated it is counted as zero, so the limit shown is on the safe (high) side. '
      'Below s_min the store needs purchased heat just to stay warm, so it should be switched off and its recovered heat '
      'inputs are unreclaimed. If the store is instead made smaller with the plant, its loss falls with its surface area '
      '(volume to the power 2/3) and the limit drops to (standing loss / recovered heat in) cubed. Table 4.1 gives both. '
      'The design tool applies the first, more cautious limit.')
    w('')
    w('Table 4.1. Heat store limits')
    w('')
    L += table(['Store', 'Tier', 'Standing loss (kW)', 'Recovered heat in (kW)', 'Hold time at standing loss (h)', 's_min, store kept at size', 's_min, store shrunk with plant'],
               [[h['unit_id'], h['tier'], fmt(h['loss_kW']),
                 fmt(h['recovered_in_kW']) + (f" plus unrated {', '.join(h['unrated_inputs'])}" if h['unrated_inputs'] else ''), fmt(h['hold_hours']),
                 fmt(h['s_min']) if h['s_min'] else 'open: input not yet rated', fmt(h['s_min_if_store_shrinks']) if h['s_min'] else 'open'] for h in lim['HEAT']['stores']])
    w('')
    w('### 4.3 FOUNDRY: metal production')
    w('')
    w('Molten-salt electrolysis cells need their bath kept molten. The heat to do that (hold power) is set by the cell size '
      'and insulation, while the electrolysis power scales with metal output [5]. Letting a cell freeze between runs and '
      'remelting it cycles the lining through large temperature changes, which cracks refractory [6], so the cells are '
      'held hot (assumption A-M-330). At scale s the energy per kilogram of metal rises by the factor (s x D + H) / '
      '(s x (D + H)), where D is electrolysis power and H is hold power. Table 4.2 gives that factor. A cell whose hold '
      'power is already most of its total is a candidate for campaign operation with a shared hot-holding furnace; that '
      'is a design decision, not an automatic consequence.')
    w('')
    w('Table 4.2. Molten-salt cells: energy per kilogram relative to full scale')
    w('')
    L += table(['Cell', 'Hold power H (kW)', 'Electrolysis power D (kW)', 'Hold share at s = 1'] + [f's = {x}' for x in SCALES],
               [[c['unit_id'], fmt(c['hold_kW']), fmt(c['dc_kW']), fmt(c['hold_share'])] + [fmt(c['energy_factor'][str(x)]) for x in SCALES] for c in lim['FOUNDRY']['cells']])
    w('')
    w('The induction melter works in heats of one full crucible. Each heat starts from a cold charge, so the energy per '
      'kilogram does not change with the number of heats [7]. A smaller plant runs fewer heats. Below the scale '
      'at which a day\'s scrap fills one crucible, the melter runs in campaigns and the scrap waits in a buffer of one '
      'crucible. Nothing is left unreclaimed.')
    w('')
    w('Table 4.3. Batch melter: days between heats')
    w('')
    L += table(['Melter', 'Crucible (kg)', 'Charge at s = 1 (kg/d)', 'Campaigns below s'] + [f's = {x}' for x in SCALES],
               [[m['unit_id'], fmt(m['crucible_kg']), fmt(m['charge_kg_d']), fmt(m['s_campaign'])] + [fmt(m['days_between_heats'][str(x)]) for x in SCALES] for m in lim['FOUNDRY']['batch_melters']])
    w('')
    w('FOUNDRY has no scale below which a stream is left unreclaimed. The cost of a smaller plant is the extra energy in '
      'Table 4.2 and the scrap buffer in Table 4.3.')
    w('')
    w('### 4.4 POLYMERS: plastics')
    w('')
    w('The polymer train makes grams to a few hundred grams a day, far below the smallest continuous equipment, so it '
      'already runs in campaigns of one polymerization kettle batch [1, 2]. A smaller plant lengthens the interval '
      'between campaigns. The feeds that arrive between campaigns are held in buffers whose size is one batch\'s worth, '
      'so the buffer size does not depend on s. Chlorine is not stored: it stays in the digester chlorine loop until a '
      'campaign draws it, so gas feeds have no buffer. The batch size uses assumption A-M-331.')
    w('')
    w('Table 4.4. Polymer kettle: days between campaigns and buffer per campaign')
    w('')
    rows = []
    for k in lim['POLYMERS']['kettles']:
        rows.append([k['unit_id'], fmt(k['volume_L']), fmt(k['batch_kg']), fmt(k['product_kg_d'])] +
                    [fmt(k['days_between_batches'][str(x)]) if k['days_between_batches'] else 'n/a' for x in SCALES] +
                    ['; '.join(f"{b['stream_id']} {fmt(b['kg_per_campaign'], 'kg')}" for b in k['buffers']) or 'none'])
    L += table(['Kettle', 'Volume (L)', 'Batch (kg)', 'Product at s = 1 (kg/d)'] + [f's = {x}' for x in SCALES] + ['Feed buffers per campaign'], rows)
    w('')
    w('POLYMERS has no scale below which a stream is left unreclaimed, provided the buffers in Table 4.4 are fitted.')
    w('')
    w('### 4.5 Plant-wide rules')
    w('')
    w('Table 4.5 lists every scale rule the design tool applies: the plant-wide rules carried from earlier revisions and '
      'the heat store rules from Table 4.1.')
    w('')
    w('Table 4.5. Scale rules applied by the design tool')
    w('')
    L += table(['Rule', 'Applies below s', 'Streams flagged', 'Reason'],
               [[r['id'], fmt(r['min_scale_m']), ', '.join(r['stream_ids']), r['detail']] for r in hand_rules + a['derate_rules']])
    w('')
    w('## 5. How the design tool uses this page')
    w('')
    w(f'1. For each switched-off sector it reports the streams marked unreclaimed or short in Tables 3.1 to 3.{U - 1}.')
    w(f'2. For each switched-off unit it reports the streams in Table 3.{U}.')
    w('3. For a scale factor below a rule\'s limit in Table 4.5 it reports that rule\'s streams.')
    w('4. A plant with any of these reports is not counted as closed.')
    w('')
    w('## 6. Assumptions')
    w('')
    L += (table(['Id', 'Assumption', 'Test that confirms it'], [
        ['A-M-329', 'Throughput is proportional to the scale factor below the baseline (s < 1)', 'Size one sub-baseline layout with the scale model and compare its feed with s x 150 kg/d'],
        ['A-M-330', 'Molten-salt cells are held molten between runs rather than frozen and remelted', 'Lining inspection after a planned freeze-thaw trial on one cell'],
        ['A-M-331', f'Polymer kettle batch = volume x {BATCH_FILL} fill x {LATEX_DENSITY_KG_L} kg/L x {LATEX_SOLIDS} solids', 'Weigh the dried polymer from the first kettle batch'],
    ]))
    w('')
    w('## 7. References')
    w('')
    w('1. Ullmann\'s Encyclopedia of Industrial Chemistry, Wiley-VCH, Fluoropolymers chapter (ULLMANN_FLUOROPOLY).')
    w('2. Towler G., Sinnott R., Chemical Engineering Design, 2nd ed., Butterworth-Heinemann (2013): choice of batch or continuous operation (TOWLER2013).')
    w('3. Bergman T.L., Lavine A.S., Incropera F.P., DeWitt D.P., Fundamentals of Heat and Mass Transfer, 7th ed., Wiley (2011): conduction through insulation (INCROPERA7).')
    w('4. ASTM C680-24, Standard Practice for Estimate of the Heat Gain or Loss and the Surface Temperatures of Insulated Flat, Cylindrical, and Spherical Systems (ASTM_C680).')
    w('5. Grjotheim K., Welch B.J., Aluminium Smelter Technology, 2nd ed., Aluminium-Verlag (1988): heat balance of electrolysis cells (GRJOTHEIM1988).')
    w('6. Schacht C.A. (ed.), Refractories Handbook, CRC Press (2004), ch. 13 thermomechanical lining design (SCHACHT2004).')
    w('7. Small coreless induction furnace practice: melt energy from cold charge (INDUCT_SOCX).')
    w('')
    w('## 8. Related documents')
    w('')
    L += (table(['Document', 'Role'], [
        ['`docs-authority/SCALE_MODEL.md` (AQS-SCALE-001)', 'How the building grows with the scale factor'],
        ['`docs-authority/SECTOR_DEFINITIONS.md` (AQS-SEC-001)', 'The sector list'],
        ['`docs-authority/STREAM_REGISTER.md` (AQS-STR-001)', 'Stream ids'],
        ['`docs-authority/HEAT_LADDER.md`', 'The heat stores and their tiers'],
    ]))
    w('')
    return '\n'.join(L)


def main():
    import importlib.util
    a = analyse()
    json.dump(a, open(OUT_JSON, 'w'), indent=1, ensure_ascii=False)
    open(OUT_JSON, 'a').write('\n')
    spec = importlib.util.spec_from_file_location('sdm', os.path.join(ROOT, 'design_tool/aqs_design_tool/solver/scale_down_map.py'))
    sdm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sdm)
    open(OUT_MD, 'w').write(page(a, sdm.UNIT_OFF_UNRECLAIMED, sdm.HAND_DERATE_RULES))
    print('scale-down analysis written')


if __name__ == '__main__':
    main()
