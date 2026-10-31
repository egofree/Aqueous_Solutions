"""X-INV-05 other building blocks inventory (AQS-INV-004): valves, instruments, electronics and protection, bearings, seals, pipe supports,
fasteners and fabricated sheet/structural parts, by sector > sub-system > unit, with a family rollup (category x item x specification).
Sources: isometric line quantities (AQS-ISO-002) for valves and flow meters; SUPPORTS.md (AQS-PIP-005) for support counts; motor inventory
(AQS-INV-001) for bearings, seals, drives and I/O; wire inventory (AQS-INV-002) for branch protection; models/mfg/*/bom.csv and fasteners.csv
for fabricated parts and their fasteners; graph node class for holdup instruments. Counting rules not taken from a document are flagged
'assumed' (A-M-125). Writes docs-authority/inventory/OTHER_INVENTORY.md, OTHER_INVENTORY.csv, OTHER_FAMILIES.csv.
Run: python3 -m flow_graph.inventory.other"""
import csv, glob, json, math, os, re, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VALVE = {'M1': '316L ball valve, ASME B16.34 Cl 150, RF flanged', 'M2': 'CS A216 WCB ball valve, ASME B16.34 Cl 150, RF flanged',
         'P1': 'PVC-U true-union ball valve, MSS SP-122, EPDM seals', 'P2': 'CPVC true-union ball valve, MSS SP-122, FKM seals',
         'P3': 'PVDF ball valve, ISO 16135, PTFE seats', 'P4': 'PP-H ball valve, ISO 16135, EPDM seals', 'P5': 'PP ball valve with HDPE stub ends, ISO 16135',
         'F1': 'PVC-lined ball valve in FRP service, ISO 16135'}
CHECK = {k: v.replace('ball valve', 'swing/ball check valve').replace(', MSS SP-122', '').replace('ISO 16135', 'ISO 16137') for k, v in VALVE.items()}
HOLD = {'tank', 'vessel', 'cut_tank', 'digest', 'reagent', 'separator', 'evaporator', 'scrubber', 'bmed', 'ew_cell', 'treat', 'farm', 'dryer', 'recycle_pipe'}
BRG = {'63': '6201-2Z', '71': '6202-2Z', '80': '6204-2Z', '90S': '6205-2Z', '90L': '6205-2Z', '100L': '6206-2Z', '112M': '6306-2Z', '132M': '6308-2Z', '160': '6309-2Z', '180M': '6310-2Z'}
def rows():
    g = json.load(open(os.path.join(ROOT, 'flow_graph/plant_flow_graph.json'))); N = {n['unit_id']: n for n in g['nodes']}
    seed = json.load(open(os.path.join(ROOT, 'flow_graph/placement_seed.json'))); st = json.load(open(os.path.join(ROOT, 'flow_graph/placement_study.json')))
    blk = {u: b['block_id'] for b in seed['blocks'] for u in b.get('unit_ids', [])}
    for r in st['units']: blk.setdefault(r['unit_id'], r.get('block_id'))
    R = []
    def add(u, cat, item, size, spec, qty, basis, sector=None, sub=None):
        if qty <= 0: return
        n = N.get(u, {})
        R.append(dict(sector=sector or n.get('sector_id') or 'MFG', subsystem=sub or blk.get(u) or n.get('class') or '-', unit=u, category=cat, item=item, size=size, spec=spec, qty=qty, basis=basis))
    mot = list(csv.DictReader(open(os.path.join(ROOT, 'docs-authority/inventory/MOTOR_INVENTORY.csv'))))
    pumped = {m['unit'] for m in mot if 'pump' in m['device'].lower()}
    iso_p = os.path.join(ROOT, 'docs-authority', 'iso', 'ISO_SHEETS.csv')
    iso = list(csv.DictReader(open(iso_p))) if os.path.exists(iso_p) else []
    sup = {l.split('|')[1].strip(): int(l.split('|')[6]) for l in open(os.path.join(ROOT, 'docs-authority/SUPPORTS.md')) if l.startswith('| ') and l.split('|')[6].strip().isdigit()}
    for s in iso:
        u = s['frm'] if s['frm'] in N else s['to']; dn = f"DN{s['DN']}"; c = s['cls']
        add(u, 'valve', 'isolation valve', dn, VALVE.get(c, VALVE['M1']), 2, f"{s['line']}: one at each end nozzle (assumed)")
        if u in pumped:
            add(u, 'valve', 'check valve', dn, CHECK.get(c, CHECK['M1']), 1, f"{s['line']}: pump discharge (assumed)")
            gas = s['material'].startswith('CS') and False
            add(u, 'instrument', 'flow transmitter', dn, 'electromagnetic, PFA liner, Hastelloy C electrodes, ISO 20456', 1, f"{s['line']}: pumped line (assumed)")
        ns = sup.get(s['line'], 0)
        if ns:
            metal = c.startswith('M')
            add(u, 'support', 'pipe clamp' if not metal else 'U-bolt with guide', dn, 'PP clamp with EPDM liner, MSS SP-58 Type 7' if not metal else '316 U-bolt, MSS SP-58 Type 24', ns, f"{s['line']}: AQS-PIP-005 span count")
            add(u, 'fastener', 'anchor bolt', 'M10', 'ISO 3506 A4-70 wedge anchor', 2*ns, f"{s['line']}: 2 per support (assumed)")
    LIQ_IN = {e['to_unit_id'] for e in g['edges'] if e['presence'] == 'present' and e.get('phase') == 'L' and (e['rate']['value'] or 0) > 0}
    for u, n in N.items():
        if n.get('class') in ('boundary', 'header', 'relief') or u.startswith(('HDR_', 'RELIEF_')): continue
        if os.path.exists(os.path.join(ROOT, f'docs-authority/nozzles/{u}.csv')) or (u in LIQ_IN and n.get('class') not in ('farm', 'product', 'building', 'hab')) or n.get('class') in ('hcl_synthesis', 'pem_electrolyser'):   # HAZOP HZ: liquid units without a nozzle list too
            add(u, 'instrument', 'temperature element', 'Pt100 class A', 'IEC 60751, 316L thermowell', 1, 'duty item 5 (assumed one per unit)')
            dk = (n.get('params') or {}).get('design_kPa') or 0; need = 1.25*dk/100                       # X-CTL-01: range from the design pressure (AQS-CTL-001)
            top = next((x for x in (10, 16, 25, 40, 60, 100, 160, 250, 400) if x >= need), 400)
            add(u, 'instrument', 'pressure transmitter', f'0-{top} bar', 'ceramic diaphragm, IEC 61298' if top <= 16 else '316L thin-film strain gauge, IEC 61298', 1, 'duty item 5 (one per unit); range >= 1.25 x design pressure')
            if n.get('class') in HOLD or u in LIQ_IN:                                                     # X-SAF-01 HZ: every liquid-receiving unit gets level and high level
                add(u, 'instrument', 'level transmitter', 'radar 80 GHz', 'IEC 62828, PTFE lens', 1, 'duty item 5: liquid holdup')
                add(u, 'instrument', 'high-level switch', 'vibrating fork', 'IEC 60947-5, 316L', 1, 'duty item 5: high level trips the inlet')
    gp = os.path.join(ROOT, 'docs-authority/inventory/GAS_DETECTORS.csv')   # X-SAF-06 (AQS-SAF-006)
    if os.path.exists(gp):
        for r in csv.DictReader(open(gp)): add(r['unit'], 'instrument', f"gas detector, {r['gas']}", r['type'], f"alarm {r['alarm']}, trip {r['trip']}, {r['mounting']}", int(r['qty']), f"AQS-SAF-006 {r['voting']}")
    sp = os.path.join(ROOT, 'docs-authority/sif_list.csv')                    # X-CTL-03: SIF hardware (AQS-CTL-003)
    if os.path.exists(sp):
        sl = list(csv.DictReader(open(sp)))
        for r in sl:
            u = r['unit'] if r['unit'] in N else 'CONTROL'
            if 'TE-90' in r['initiator']: add(u, 'instrument', 'temperature element (SIF, independent)', 'Pt100 class A', 'IEC 60751, own thermowell', 1, f"{r['id']} SIL {r['SIL']}")
            if 'ESD' in r['final_element']: add(u, 'valve', 'ESD valve, spring-return actuator', 'DN15', '316L, fail-safe, IEC 61511', 2, f"{r['id']} one per bank half")
        add('PLC', 'electronics', 'safety PLC (SIL 2 capable), CPU and I/O rack', '-', 'IEC 61508 / IEC 61511', 2, f"AQS-CTL-003: {len(sl)} SIFs, redundant pair", sector='CONTROL', sub='SIS')
    for m in mot:
        q = int(m['qty']); u = m['unit']; mt = m['motor_type']; sz = m['size']; kw = float(m['shaft_kW'])
        if mt.startswith('induction'):
            fr = re.search(r'IEC (\d+[SLM]?)', sz); b = BRG.get(fr.group(1) if fr else '', '6204-2Z') if fr else '6204-2Z'
            add(u, 'bearing', 'deep-groove ball bearing', b, 'ISO 15 / ISO 492 normal class, C3', 2*q, f"{m['device']}: drive and non-drive end, IEC 60072 frame {fr.group(1) if fr else '?'} (assumed size)")
            add(u, 'electronics', 'variable-frequency drive' if kw >= 0.75 else 'motor starter (contactor + overload)', sz.split('/')[-1].strip(), 'IEC 61800-5-1' if kw >= 0.75 else 'IEC 60947-4-1', q, f"{m['device']} (assumed VFD at >= 0.75 kW)")
        elif mt.startswith('BLDC') or mt.startswith('stepper'):
            add(u, 'bearing', 'deep-groove ball bearing', '608-2Z' if mt.startswith('stepper') or kw < 0.1 else '6000-2Z', 'ISO 15, normal class', 2*q, f"{m['device']} (assumed size)")
            add(u, 'electronics', 'BLDC driver' if mt.startswith('BLDC') else 'stepper driver', '24/48 V DC', 'IEC 61800-5-1', q, m['device'])
        elif mt.startswith('solenoid'):
            add(u, 'electronics', 'solenoid driver channel', '24 V DC', 'IEC 61131-2 DO', q, m['device'])
        elif mt.startswith('hermetic'):
            add(u, 'electronics', 'compressor contactor + overload', sz, 'IEC 60947-4-1', q, m['device'])
        d = m['device'].lower()
        if mt.startswith('induction') and 'pump' in d and not any(k in d for k in ('magnet', 'mag drive', 'peristaltic', 'diaphragm', 'hermetic', 'canned')):
            add(u, 'seal', 'mechanical seal, single', 'EN 12756', 'SiC/SiC faces, FKM', q, f"{m['device']}: induction-driven pump assumed seal-type; BLDC pumps assumed magnetic drive")
        add(u, 'electronics', 'PLC digital I/O point', '24 V DC', 'IEC 61131-2', 2*q, f"{m['device']}: run and fault (assumed)")
    for w in csv.DictReader(open(os.path.join(ROOT, 'docs-authority/inventory/WIRE_INVENTORY.csv'))):
        mm = re.search(r'at (\d+) A OCPD', w['basis'])
        if mm and w['type'] == 'equipment ground':
            add(w['unit'], 'protection', 'inverse-time circuit breaker, 3-pole', f"{mm.group(1)} A", 'UL 489 / IEC 60947-2', int(w['qty']), 'NEC 430.52, from AQS-INV-002', w['sector'], w['subsystem'])
    for f in sorted(glob.glob(os.path.join(ROOT, 'models/mfg/*/fasteners.csv'))):
        u = f.split('/')[-2]
        for r in csv.DictReader(open(f)):
            add(u, 'fastener', r['size'].split(' with')[0], r['size'], r['grade'], int(float(r['qty'])), f"models/mfg/{u}/fasteners.csv")
    for f in sorted(glob.glob(os.path.join(ROOT, 'models/mfg/*/bom.csv'))):
        u = f.split('/')[-2]; n = sum(1 for l in open(f) if l.strip()) - 1
        add(u, 'fabricated part', 'fabricated part set', f'{n} BOM lines', f'models/mfg/{u}/bom.csv and WORK_ORDER.md', 1, 'unit work order; bought-in lines in the set are counted again in their own inventory')
    io = sum(r['qty'] for r in R if r['category'] == 'instrument')
    add('PLC', 'electronics', 'PLC analog input point', '4-20 mA HART', 'IEC 61131-2', io, 'one per instrument', 'CONTROL', 'PLC')
    nio = sum(r['qty'] for r in R if r['item'].startswith('PLC'))
    add('PLC', 'electronics', 'PLC I/O module, 16 channel', '24 V DC', 'IEC 61131-2', math.ceil(nio/16), f'{nio} points / 16', 'CONTROL', 'PLC')
    return R
def write(R):
    D = os.path.join(ROOT, 'docs-authority/inventory'); R.sort(key=lambda r: (r['sector'], str(r['subsystem']), r['unit'], r['category'], r['item']))
    with open(os.path.join(D, 'OTHER_INVENTORY.csv'), 'w', newline='') as f: w = csv.DictWriter(f, list(R[0].keys())); w.writeheader(); w.writerows(R)
    F = collections.defaultdict(lambda: [0, collections.Counter(), set()])
    for r in R:
        k = (r['category'], r['item'], r['spec'] if r['category'] != 'fabricated part' else 'models/mfg/<unit>/bom.csv')
        F[k][0] += r['qty']; F[k][1][r['size']] += r['qty']; F[k][2].add(r['unit'])
    from flow_graph.inventory.stable_ids import assign, number
    ids = assign(os.path.join(ROOT, 'flow_graph/inventory/other_family_ids.json'), 'OF', ('category', 'item', 'spec'),
                 [k for k, _ in sorted(F.items(), key=lambda kv: (kv[0][0], -kv[1][0]))])
    FF = sorted(F.items(), key=lambda kv: number(ids[kv[0]]))
    out = [dict(family=ids[(c, it, sp)], category=c, item=it, spec=sp, qty=q, sizes='; '.join(f'{s} x{n}' for s, n in cnt.most_common()), units=len(us))
           for (c, it, sp), (q, cnt, us) in FF]
    with open(os.path.join(D, 'OTHER_FAMILIES.csv'), 'w', newline='') as fh: w = csv.DictWriter(fh, list(out[0].keys())); w.writeheader(); w.writerows(out)
    C = collections.Counter()
    for r in R: C[r['category']] += r['qty']
    a = sum(r['qty'] for r in R if 'assumed' in r['basis'])
    L = ['# Other building blocks inventory', '', 'Document number: AQS-INV-004', 'Revision: B', 'Date: 2026-10-25',
         'Authority: AQS-PLAN-007 task X-INV-05; assumption A-M-125. Generated by `flow_graph/inventory/other.py`, with the data in the CSV files beside this page; do not edit this page by hand.', '',
         '| Rev | Description | Date |', '| --- | --- | --- |', '| A | First issue. | 2026-10-15 |', '| B | Purpose and scope added; text rewritten to the documentation style guide (AQS-DOC-002). No item changed. | 2026-10-25 |', '',
         '## Purpose and scope', '', 'This inventory lists the building blocks of the plant that are not motors, pipe or wire: valves, instruments, electronics, fasteners, bearings, seals and similar parts. Section 1 totals the items by category, section 2 groups them into families, and section 3 lists them by sector, sub-system and unit. Flange studs and gaskets are in the pipe inventory (AQS-INV-003), conductors in the wire inventory (AQS-INV-002) and motors in the motor inventory (AQS-INV-001).', '',
         f"The inventory has {len(R)} rows with {sum(C.values())} items in {len(out)} families. Of these, {a} items rest on an assumed counting rule (A-M-125).", '',
         '## 1. By category', '', 'Table 1.1. Items by category', '', '| Category | Items |', '| --- | --- |'] + [f'| {k} | {v} |' for k, v in C.most_common()] + [
         '', '## 2. Family rollup', '', 'Table 2.1. Item families', '', '| Family | Category | Item | Specification | Qty | Sizes | Units |', '| --- | --- | --- | --- | --- | --- | --- |']
    L += [f"| {o['family']} | {o['category']} | {o['item']} | {o['spec']} | {o['qty']} | {o['sizes'][:120]} | {o['units']} |" for o in out]
    L += ['', '## 3. Items by sector, sub-system and unit', '']
    cur = None
    for r in R:
        if r['sector'] != cur:
            cur = r['sector']; L += ['', f'### {cur}', '', '| Sub-system | Unit | Category | Item | Size | Spec | Qty | Basis |', '| --- | --- | --- | --- | --- | --- | --- | --- |']
        L.append(f"| {r['subsystem']} | {r['unit']} | {r['category']} | {r['item']} | {r['size']} | {r['spec']} | {r['qty']} | {r['basis']} |")
    open(os.path.join(D, 'OTHER_INVENTORY.md'), 'w').write('\n'.join(L) + '\n'); return out, C, a
if __name__ == '__main__':
    out, C, a = write(rows()); print(dict(C), 'assumed', a, len(out), 'families')
    for o in out: print(o['family'], o['category'], o['item'][:40], '|', o['spec'][:40], o['qty'])
