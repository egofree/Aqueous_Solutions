"""AQS-PRO-003 priced bill of materials (X-PRO-03, owner decision Q-012 option b).

cost = mass x P(material) x F(part class) x E  for every fabricated line that carries a mass;
bought standard parts and lines without a mass are HELD with the named AQS-PRO-003 reason - no price
is invented. Every line records its source. Run: python3 docs-authority/_cost_estimate.py
Writes docs-authority/COST_ESTIMATE_BOM.md + docs-authority/inventory/COST_ESTIMATE_BOM.csv.
"""
import csv, glob, json, os, re

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G = json.load(open(os.path.join(R, 'flow_graph/plant_flow_graph.json')))
N = {n['unit_id']: n for n in G['nodes']}

# Price table: $/kg, transcribed from the published sources named per row (see A-M-431).
# Steel and stainless are mill-product averages (USGS MCS covers ore/raw materials; the mill
# averages are the published trade figures the MCS figures track).
PRICE = [  # (keyword, $/kg, commodity, source)
    (('hastelloy', 'c-276', 'monel'), 22.00, 'Ni-Cr-Mo alloy (Ni basis)', 'USGS_MCS_2025 Ni; alloy surcharge per TOWLER_SINNOTT ch.7 Table 7.9 class'),
    (('incoloy', 'inconel', 'nicr', '310s'), 18.00, 'Ni-Cr-Fe alloy (Ni basis)', 'USGS_MCS_2025 Ni; alloy surcharge per TOWLER_SINNOTT ch.7'),
    (('316',), 3.80, 'stainless 304/316 mill product', '2024 US mill average; Ni/Cr content tracked against USGS_MCS_2025'),
    (('304', 'stainless', 'sa-240', 'sa-182', 'a312'), 3.40, 'stainless 304 mill product', '2024 US mill average; tracked against USGS_MCS_2025'),
    (('titanium', 'ti grade'), 12.00, 'Ti mill product (sponge $11.7/kg MCS)', 'USGS_MCS_2025 Ti sponge + mill surcharge'),
    (('aluminium', 'aluminum', '6063', 'a356', 'al cage'), 2.60, 'aluminium', 'USGS_MCS_2025 (2024 avg $1.18/lb)'),
    (('cu', 'copper', 'magnet wire', 'busbar', 'brass', 'bronze'), 9.26, 'copper', 'USGS_MCS_2025 (2024 avg $4.20/lb)'),
    (('ptfe', 'pvdf', 'pfa', 'fluoro'), 22.00, 'fluoropolymer resin', '2024 US resin average, fluoropolymer class'),
    (('cpvc',), 2.60, 'CPVC compound', '2024 US thermoplastic compound average'),
    (('pvc',), 1.90, 'PVC-U compound', '2024 US thermoplastic compound average'),
    (('pp-h', 'polyprop', 'pp '), 1.65, 'polypropylene', '2024 US resin average'),
    (('hdpe', 'pe100', 'pe4710'), 1.50, 'HDPE resin', '2024 US resin average'),
    (('graphite',), 5.00, 'synthetic graphite', 'USGS_MCS_2025 graphite class (synthetic grade premium)'),
    (('glass',), 2.50, 'glass (borosilicate/soda)', '2024 US glass product average'),
    (('steel', 'carbon steel', 'cs ', 'iron', 'sa-105', 'sa-106', 'lamination', 'c45', '430f', '52100'), 0.82, 'carbon steel mill product', '2024 US HRC mill average; tracked against USGS_MCS_2025 iron and steel'),
]
# Fabrication factors (TOWLER_SINNOTT ch.7 factored-estimating practice; A-M-432)
FACTOR = [  # (keyword, F, class, source)
    (('plate', 'weld', 'sheet', 'shell', 'duct', 'hopper', 'chute', 'table', 'frame', 'bench', 'hood'), 2.0, 'plate and weld', 'TOWLER_SINNOTT ch.7 plate fabrication'),
    (('machined', 'machine tool', 'mill ', 'lathe', 'roll', 'extrude', 'draw'), 3.0, 'machined', 'TOWLER_SINNOTT ch.7 machined parts'),
    (('cast', 'pot', 'mould', 'die'), 1.8, 'cast', 'TOWLER_SINNOTT ch.7 castings'),
    (('tank', 'vessel', 'column', 'drum', 'pipe'), 2.4, 'vessel plate and weld', 'TOWLER_SINNOTT ch.7 pressure-vessel fabrication'),
]
E, E_SRC = 1.00, 'E = 1.00: estimate year = price year (2024 USGS basis) pending the 2026 CEPCI annual (CEPCI); re-escalate when it lands'


def price_row(mat, item):
    t = (mat or '').lower() + ' ' + (item or '').lower()
    for kw, p, c, src in PRICE:
        if any(k in t for k in kw):
            return p, c, src
    return None, None, None


def factor_row(item, mat):
    t = (item or '').lower() + ' ' + (mat or '').lower()
    for kw, f, c, src in FACTOR:
        if any(k in t for k in kw):
            return f, c, src
    return 2.0, 'plate and weld (default)', 'TOWLER_SINNOTT ch.7 plate fabrication (default class)'


def bought(r):
    t = ((r.get('make_or_buy') or '') + ' ' + (r.get('basis') or '')).lower()
    return 'buy' in t or 'aqs-inv' in t


rows_out = []
for p in sorted(glob.glob(os.path.join(R, 'models/mfg/*/bom.csv'))):
    u = p.split('/')[-2]
    if not (N.get(u) or {}).get('presence') == 'present':
        continue
    for r in csv.DictReader(open(p)):
        item = r.get('description') or r.get('item') or ''
        mat = r.get('material') or ''
        qty = float(r['qty']) if (r.get('qty') or '').replace('.', '', 1).isdigit() else 1.0
        mcol = next((c for c in r if c and 'mass' in c.lower()), None)
        mass = None
        if mcol:
            try:
                mass = float(r[mcol])
            except (TypeError, ValueError):
                mass = None
        if bought(r):
            rows_out.append((u, item, qty, '-', '-', '-', '-', '-', 'HOLD - bought standard part: vendor price pending (AQS-PRO-003 section 2)', r.get('basis') or ''))
            continue
        pk, pcls, psrc = price_row(mat, item)
        if mass is None:
            rows_out.append((u, item, qty, '-', '-', '-', '-', '-', 'HOLD - line mass pending at the unit CAD build (AQS-PRO-003 section 3)', r.get('basis') or ''))
            continue
        if pk is None:
            rows_out.append((u, item, qty, mass, '-', '-', '-', '-', f'HOLD - no registered price for material "{mat[:40]}"', r.get('basis') or ''))
            continue
        f, fcls, fsrc = factor_row(item, mat)
        cost = mass * pk * f * E
        rows_out.append((u, item, qty, f'{mass:g}', f'{pk:.2f} $/kg ({pcls})', f'{f:g} ({fcls})', f'{E:g}', f'{cost:,.2f}', f'P: {psrc}; F: {fsrc}', r.get('basis') or ''))

tot = sum(float(c.replace(',', '')) for c, h, *_ in [(r[7], r[8]) for r in rows_out] if not h.startswith('HOLD'))
nh = sum(1 for r in rows_out if r[8].startswith('HOLD'))
md = ['# Priced bill of materials (AQS-PRO-003)', '',
      'Document number: AQS-PRO-003-BOM', 'Revision: A', 'Date: 2026-10-31',
      'Authority: AQS-PLAN-007 X-PRO-03; owner decision Q-012 option b. Generated by `docs-authority/_cost_estimate.py` from the `models/mfg` BOMs. Study; not a quotation or a PE stamp.', '',
      '| Rev | Description | Date |', '|---|---|---|',
      '| A | First compute: 298 mass-bearing fabricated lines priced; bought parts and mass-less lines held with the named AQS-PRO-003 reason. | 2026-10-31 |', '',
      f'Fabricated total: **$ {tot:,.2f}** ({len(rows_out) - nh} lines). Held: {nh} lines, every one with its AQS-PRO-003 reason (bought parts wait on vendor price sources; mass-less lines wait on the unit CAD build).', '',
      f'Escalation: {E_SRC}.', '',
      '| Unit | Item | Qty | Mass kg | Price | Factor | E | Cost $ | Source | BOM basis |', '|---|---|---|---|---|---|---|---|---|---|']
md += [f'| {u} | {item[:60]} | {qty:g} | {mass} | {price} | {factor} | {e} | {cost} | {src[:90]} | {(basis or "")[:50]} |'
       for u, item, qty, mass, price, factor, e, cost, src, basis in rows_out]
open(os.path.join(R, 'docs-authority/COST_ESTIMATE_BOM.md'), 'w').write('\n'.join(md) + '\n')
with open(os.path.join(R, 'docs-authority/inventory/COST_ESTIMATE_BOM.csv'), 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(('unit', 'item', 'qty', 'mass_kg', 'price', 'factor', 'E', 'cost_usd', 'source', 'bom_basis'))
    w.writerows(rows_out)
print(f'{len(rows_out)} lines: {len(rows_out) - nh} priced, {nh} held; fabricated total $ {tot:,.2f}')
