"""Recovery-first inventory of the elements the plant takes as raw ore (owner decision t61u; A-M-423).

Rule: for every element the plant needs, recover it first from waste and byproduct streams anywhere on the graph; raw
ore at the dock is only a top-up for the shortfall left after recovery, sized by the code. Each transfer function that
takes an ore stamps a recovery record on its unit (params.recovery): the element, its use, the need (kg/d of the
element), the amount recovered from waste and the streams it comes from, the ore streams that top it up, and every
unrecovered loss with its basis. This module reads those records and the graph, and check() flags:
- a dock input that is neither a listed raw ore, water, a mining-waste stream nor a listed pending import;
- a raw-ore stream that no recovery record covers;
- an ore input (from the graph rate, the mineral formula and the ore purity) above the shortfall need - recovered;
- an ore input while a loss of the same element is marked recoverable (for example a route that ships a waste it could
  recover);
- a waste outflow at the dock or to the air that carries an element taken as ore, but that no record recovers or
  declares as an unrecovered loss with a basis.
Run: python3 -m flow_graph.param.recovery   (prints the inventory and the flags; flow_graph/param/test_recovery_first.py
fails on any flag)."""
import json, os, re
from . import drivers as DR

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GP = os.path.join(ROOT, 'flow_graph/plant_flow_graph.json')
AW = dict(H=1.008, C=12.011, N=14.007, O=15.999, F=18.998, Na=22.990, Mg=24.305, Al=26.982, Si=28.085, S=32.06,
          Cl=35.453, Ca=40.078, Ti=47.867, Cr=51.996, Mo=95.95)
# dock raw-ore streams: element, mineral formula, ore-purity driver (None: the stream is rated as the pure mineral)
ORE = {'IA-CAF2-MU': ('F', 'CaF2', 'POLYMERS.fluoropolymer-train.fluorspar_CaF2_wt'),
       'IA-TIO2-MU': ('Ti', 'TiO2', None), 'IA-MOO3-MU': ('Mo', 'MoO3', None), 'IA-CR2O3-MU': ('Cr', 'Cr2O3', None),
       'IA-QUARTZ-MU': ('Si', 'SiO2', None), 'IA-SILICA-MU': ('Si', 'SiO2', None), 'IA-SULFUR-MU': ('S', 'S', None),
       'IA-TRONA-MU': ('Na', 'Na2CO3.NaHCO3.2H2O', 'trona_ore_purity'), 'IA-HALITE-MU': ('Na', 'NaCl', 'halite_ore_purity'),
       'IA-LIMESTONE-MU': ('Ca', 'CaCO3', 'limestone_ore_purity')}
WASTE_RE = re.compile(r'mining-waste|\bwaste\b')
WATER_RE = re.compile(r'water make-up')
PENDING = {'IA-SOLV-MU': 'X-RTE-IMPORT-IA-SOLV-MU', 'IA-WAX-MU': 'X-RTE-IMPORT-IA-WAX-MU'}
PRODUCT_FROM = ('PROD_', 'METAL_STORE', 'WAFER_FAB')
PRODUCT_RE = re.compile(r'\bexport\b|\bshipped\b|\bproduct\b')

def _formula(f):
    """Element mass of one formula unit, e.g. 'Na2CO3.NaHCO3.2H2O' -> {'Na': ..., 'C': ..., 'O': ..., 'H': ...}."""
    out = {}
    for part in f.split('.'):
        m = re.match(r'^(\d+)(.*)$', part); k = int(m.group(1)) if m else 1; part = m.group(2) if m else part
        for el, n in re.findall(r'([A-Z][a-z]?)(\d*)', part):
            if el not in AW:
                return {}
            out[el] = out.get(el, 0.0) + k*(int(n) if n else 1)*AW[el]
    return out

def frac(formula, el):
    m = _formula(formula); t = sum(m.values())
    return m.get(el, 0.0)/t if t else 0.0

def elements(comp):
    """Elements present in a composition dict whose keys are formulas (non-formula keys such as 'water' are skipped)."""
    s = set()
    for k in (comp or {}):
        if k == 'water':
            s |= {'H', 'O'}
        s |= set(_formula(k)) if _formula(k) else set()
    return s

def _live(e):
    return e.get('presence') != 'retired' and 'mass' in (e.get('layers') or []) and (e.get('rate') or {}).get('unit') == 'kg/d' \
        and float((e.get('rate') or {}).get('value') or 0) > 0

def inventory(g=None, d=None):
    g = g or json.load(open(GP)); d = d or DR.load()
    E = {e['stream_id']: e for e in g['edges']}
    recs = []
    for n in g['nodes']:
        for r in (n.get('params') or {}).get('recovery') or []:
            recs.append(dict(r, unit=n['unit_id']))
    flags = []
    ore_el = {}
    for sid, (el, f, pk) in ORE.items():
        e = E.get(sid)
        if e is None or not _live(e):
            continue
        ore_el[sid] = float(e['rate']['value'])*frac(f, el)*(DR.val(d, pk) if pk else 1.0)
    covered = {s for r in recs for s in r.get('ore_streams', [])}
    for e in g['edges']:
        if e['from_unit_id'] != 'NORTH_DOCK' or not _live(e):
            continue
        sid, c = e['stream_id'], (e.get('carries') or '').lower()
        if sid in ORE:
            if sid not in covered:
                flags.append(f'{sid}: raw ore with no recovery record')
        elif not (WASTE_RE.search(c) or WATER_RE.search(c) or sid in PENDING):
            flags.append(f'{sid}: dock input that is not a listed raw ore, water, waste or pending import ({e["carries"]})')
    rows = []
    for r in recs:
        ore = sum(ore_el.get(s, 0.0) for s in r.get('ore_streams', []))
        short = r['need_kg_d'] - r['recovered_kg_d']
        tol = 1e-6 + 1e-4*max(r['need_kg_d'], 0.0)
        if ore > short + tol:
            flags.append(f"{r['element']} ({r['use']}, {r['unit']}): ore {ore:.6f} kg/d exceeds the unrecovered shortfall {short:.6f} kg/d")
        for u in r.get('unrecovered', []):
            if not u.get('basis'):
                flags.append(f"{r['element']} ({r['use']}): unrecovered loss on {u['stream']} has no basis")
            if u.get('recoverable') and ore > tol:
                flags.append(f"{r['element']} ({r['use']}): ore is taken while the loss on {u['stream']} is recoverable ({u['basis']})")
        rows.append(dict(r, ore_kg_d=ore, shortfall_kg_d=short))
    ore_elements = {ORE[s][0] for s, v in ore_el.items() if v > 0}
    declared = {}
    for r in recs:
        for s in list(r.get('recovered_from', [])) + [u['stream'] for u in r.get('unrecovered', [])]:
            declared.setdefault(r['element'], set()).add(s)
    for e in g['edges']:
        if e['to_unit_id'] not in ('NORTH_DOCK', 'ATMOS') or not _live(e):
            continue
        if e['from_unit_id'].startswith(PRODUCT_FROM) or PRODUCT_RE.search((e.get('carries') or '').lower()):
            continue
        for el in elements(e.get('composition')) & ore_elements:
            if e['stream_id'] not in declared.get(el, set()):
                flags.append(f"{e['stream_id']}: waste outflow carries {el}, which the plant takes as ore, but no record recovers it or declares the loss")
    waste_in = [(e['stream_id'], e['to_unit_id'], float(e['rate']['value']), e['carries']) for e in g['edges']
                if e['from_unit_id'] == 'NORTH_DOCK' and _live(e) and WASTE_RE.search((e.get('carries') or '').lower())]
    return dict(rows=rows, flags=flags, waste_in=waste_in, ore_el=ore_el)

def check(g=None):
    return inventory(g)['flags']

if __name__ == '__main__':
    inv = inventory()
    for r in inv['rows']:
        print(f"{r['element']:>2} {r['use'][:40]:40} need {r['need_kg_d']:.4f} recovered {r['recovered_kg_d']:.4f} ore {r['ore_kg_d']:.4f} shortfall {r['shortfall_kg_d']:.4f}")
    print('flags:', json.dumps(inv['flags'], indent=1))
