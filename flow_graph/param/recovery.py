"""Recovery-first inventory of the elements the plant takes as raw ore (owner decision t61u; A-M-476).

Rule: for every element the plant needs, recover it first from waste and byproduct streams anywhere on the graph; raw
ore at the dock is only a top-up for the shortfall left after recovery, sized by the code. Each transfer function that
takes an ore stamps a recovery record on its unit (params.recovery): the element, its use, the need (kg/d of the
element), the amount recovered from waste and the streams it comes from, the ore streams that top it up, and every
unrecovered loss with its basis. This module reads those records and the graph, and check() flags:
- a dock input whose explicit class (params.dock_class, set where the stream is made or by stamp()) is not one of
  raw_ore, water, waste, pending, or that carries no class at all (F-20261110-07: the class is a field, not text);
- a pending import whose task has closed (the exemption dies with its task);
- a raw-ore stream that no recovery record covers;
- an ore input (from the graph rate, the mineral formula and the ore purity) above the shortfall need - recovered;
- an ore input while a loss of the same element is marked recoverable (for example a route that ships a waste it could
  recover);
- a waste outflow to the dock or the air, or into a terminal leach, purge or residue sink (F-20261110-07), that carries
  an element taken as ore, but that no record recovers or declares as an unrecovered loss with a basis.
Run: python3 -m flow_graph.param.recovery [--stamp]   (prints the inventory and the flags;
flow_graph/param/test_recovery_first.py fails on any flag). --stamp writes the dock classes onto the graph."""
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
# Explicit dock classes (F-20261110-07), set where the stream is made and restamped by stamp(): each dock input is
# raw_ore (a listed mineral), water (a water make-up), waste (a received waste stream) or pending (an import the
# recovery-first program has not replaced yet; each pending entry names the task that retires it). No text matching:
# a new dock input joins one of these tables where it is made, or the gate flags it.
WASTE_IN = {   # received waste streams: the plant's designed feed classes (A-M-284 dock feedstock ruling)
}
WATER_IN = {   # water make-ups at the dock boundary
    'IA-H2O-MU',
}
# pending imports with the task that retires each (F-20261110-07: the exemption dies with its task).
# IA-ALCL3-MU left this table with X-QA-19 closed by sizing, not by exemption: the Al line is sized to the
# recoverable aluminium (A-M-495) and the import is retired, so there is no pending entry left to keep alive.
PENDING = {
    'IA-MGCL2-MU': ('X-QA-11', 'CaCl2-MgCl2 brine make-up that restores the Kroll drag-out (A-M-284); a process-chemical '
                    'import, not a mining waste; the on-site salt recovery route is the X-QA-11 program'),
    'IA-CACL2-MU': ('X-QA-11', 'CaCl2 brine make-up of the CA_POT (A-M-284); as IA-MGCL2-MU, a process chemical pending the '
                    'on-site salt recovery route'),
    'IA-FEED-MU': ('X-QA-11', 'feedstock make-up behind the scrap-yard closure (A-M-460: the design feed less the loop '
                   'receipts - wear, shop swarf, frass and the leach return); a characterized lot re-points the feed and '
                   'the closure re-solves (AQS-ASSAY-001 section 7)'),
    'NUT_AQUA': ('X-QA-11', 'mineral nitrate solution for the raceway on the dock mineral manifest (A-M-430: the fish stock '
                 'returns about 13.5 g N/d against a raceway-plus-greens uptake near 260 g N/d; neutralizing the '
                 'nitric-acid line with the ash stream is the locale upgrade that retires the manifest line)'),
    'NUT_AQUA_BED': ('X-QA-11', 'mineral nitrate solution for the media beds on the same dock mineral manifest and the same '
                     'nitrogen basis as the raceway dose (A-M-430)'),
    'CA_HOPPER': ('X-QA-11', 'free-choice mineral calcium carbonate for the livestock on the same dock mineral manifest '
                  '(A-M-430)'),
    'FR_FINISH': ('X-QA-11', 'phosphorus flame-retardant finish of the crew textile line at the reagent resupply class '
                  '(A-M-225; the FR-finished fleece is the designed textile, A-M-429); in-plant synthesis is the locale '
                  'upgrade named on the edge'),
    'IA-WAX-MU': ('X-QA-11', 'pattern wax make-up beyond the dewax reclaim (A-M-286); the plant C19-C28 paraffin cut as the '
                  'make-up source is the audit route not yet landed'),
}
# terminal loss sinks (F-20261110-07): units whose inflow ends the arriving elements - the acid leach (undissolved
# solids report to the crib or the sink circuit), beyond the dock and the air already checked
SINK_UNITS = {'LEACH_CSTR_1'}
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

def _closed_tasks():
    """Task ids the generated plan marks done (docs-authority/TASK_PLAN.md '- [x] **X-...**')."""
    try:
        return set(re.findall(r'- \[x\] \*\*(X-[A-Z0-9-]+)\*\*', open(os.path.join(ROOT, 'docs-authority/TASK_PLAN.md')).read()))
    except OSError:
        return set()

def stamp(g=None):
    """Write the explicit dock class onto every live dock input (F-20261110-07). The writer of a new dock input sets
    params.dock_class where it makes the stream; this pass restamps the classes of the named tables so a hand-added or
    seed-grown input cannot dodge the gate, and leaves every other field alone."""
    g = g or json.load(open(GP))
    n = 0
    for e in g['edges']:
        if e.get('from_unit_id') != 'NORTH_DOCK' or not _live(e):
            continue
        sid = e['stream_id']
        if sid in ORE:
            cls = 'raw_ore'
        elif sid in WASTE_IN:
            cls = 'waste'
        elif sid in PENDING:
            cls = 'pending'
        elif sid in WATER_IN:
            cls = 'water'
        else:
            cls = None
        p = e.setdefault('params', {})
        if p.get('dock_class') != cls:
            p['dock_class'] = cls; n += 1
        if cls == 'pending':
            p['dock_pending_task'] = PENDING[sid][0]
    return g, n

def inventory(g=None, d=None):
    g = g or json.load(open(GP)); d = d or DR.load()
    E = {e['stream_id']: e for e in g['edges']}
    recs = []
    for n in g['nodes']:
        for r in (n.get('params') or {}).get('recovery') or []:
            recs.append(dict(r, unit=n['unit_id']))
    flags = []
    closed = _closed_tasks()
    ore_el = {}
    for sid, (el, f, pk) in ORE.items():
        e = E.get(sid)
        if e is None or not _live(e):
            continue
        ore_el[sid] = float(e['rate']['value'])*frac(f, el)*(DR.val(d, pk) if pk else 1.0)
    covered = {s for r in recs for s in r.get('ore_streams', [])}
    for e in g['edges']:
        if e.get('from_unit_id') != 'NORTH_DOCK' or not _live(e):
            continue
        sid = e['stream_id']
        cls = ((e.get('params') or {}).get('dock_class'))
        if cls == 'raw_ore':
            if sid not in covered:
                flags.append(f'{sid}: raw ore with no recovery record')
        elif cls == 'pending':
            task = (e.get('params') or {}).get('dock_pending_task') or PENDING.get(sid, ('',))[0]
            if task and task in closed:
                flags.append(f'{sid}: pending import whose task {task} has closed, but the import is still present')
        elif cls in ('water', 'waste'):
            pass
        else:
            flags.append(f'{sid}: dock input with no explicit dock_class (set params.dock_class where the stream is made)')
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
    # the plant still needs an element whose ore is fully recovered: the loss check watches every
    # element any recovery record covers, so an undeclared loss cannot hide behind a retired ore
    # draw (F-20261110-07: every stream that ends an element in a leach, purge or residue)
    rec_elements = {r['element'] for r in recs if r['need_kg_d'] > 0}
    watch_elements = ore_elements | rec_elements
    declared = {}
    for r in recs:
        for s in list(r.get('recovered_from', [])) + [u['stream'] for u in r.get('unrecovered', [])]:
            declared.setdefault(r['element'], set()).add(s)
    declared_any = set().union(*declared.values()) if declared else set()
    for e in g['edges']:
        if e.get('to_unit_id') not in {'NORTH_DOCK', 'ATMOS'} | SINK_UNITS or not _live(e):
            continue
        if e['from_unit_id'].startswith(PRODUCT_FROM) or PRODUCT_RE.search((e.get('carries') or '').lower()):
            continue
        for el in elements(e.get('composition')) & watch_elements:
            if e['stream_id'] not in declared.get(el, set()):
                # a loop inflow to the leach (delared under any element's record) is a process use, not a terminal loss
                if e['stream_id'] in declared_any:
                    continue
                flags.append(f"{e['stream_id']}: loss sink {e['to_unit_id']} carries {el}, which the plant takes as ore, but no record recovers it or declares the loss")
    waste_in = [(e['stream_id'], e['to_unit_id'], float(e['rate']['value']), e['carries']) for e in g['edges']
                if e.get('from_unit_id') == 'NORTH_DOCK' and _live(e)
                and ((e.get('params') or {}).get('dock_class') == 'waste')]
    return dict(rows=rows, flags=flags, waste_in=waste_in, ore_el=ore_el)

def check(g=None):
    return inventory(g)['flags']

def main():
    import sys
    if '--stamp' in sys.argv:
        g, n = stamp()
        open(GP, 'w').write(json.dumps(g, indent=2))
        print(f'stamp: {n} dock classes updated')
    inv = inventory()
    for r in inv['rows']:
        print(f"{r['element']:>2} {r['use'][:40]:40} need {r['need_kg_d']:.4f} recovered {r['recovered_kg_d']:.4f} ore {r['ore_kg_d']:.4f} shortfall {r['shortfall_kg_d']:.4f}")
    print('flags:', json.dumps(inv['flags'], indent=1))

if __name__ == '__main__':
    main()
