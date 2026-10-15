"""X-INV-03 wire inventory (AQS-INV-002). Every conductor by sector > sub-system > unit: size, insulation, voltage class, length, ampacity
basis. Sources: motor inventory (AQS-INV-001) -> branch circuits sized to NEC 2023 430.22 (125 % FLC, Table 430.250 / 430.248) on
Table 310.16 75 C copper with the 240.4(D) small-conductor limits; equipment grounding conductor NEC 250.122; collection bus
(AQS-ELEC-008) inverter outputs and section mains; MV 12.47 kV transformer feeders; PV source circuits (graph PV_ARRAY); hall lighting
branch circuits (EXT_HALL hvac.light); grounding grid (AQS-ELEC-005); 24 V DC control pairs for BLDC, stepper, solenoid and actuator
items. Lengths: Manhattan distance from the unit to the electrical room (SOL_ARK_60K) x 1.2 + 5 m; everything not sized from a
document is flagged 'assumed' (A-M-122). Writes docs-authority/inventory/WIRE_INVENTORY.md, WIRE_INVENTORY.csv, WIRE_FAMILIES.csv.
Run: python3 -m flow_graph.inventory.wire"""
import csv, json, math, os, runpy, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AMP = [('14 AWG', 15), ('12 AWG', 20), ('10 AWG', 30), ('8 AWG', 50), ('6 AWG', 65), ('4 AWG', 85), ('3 AWG', 100), ('2 AWG', 115), ('1 AWG', 130), ('1/0 AWG', 150),
       ('2/0 AWG', 175), ('3/0 AWG', 200), ('4/0 AWG', 230), ('250 kcmil', 255), ('300 kcmil', 285), ('350 kcmil', 310), ('400 kcmil', 335), ('500 kcmil', 380), ('600 kcmil', 420)]   # NEC 310.16 75 C Cu; 240.4(D)
EGC = [(15, '14 AWG'), (20, '12 AWG'), (60, '10 AWG'), (100, '8 AWG'), (200, '6 AWG'), (300, '4 AWG'), (400, '3 AWG'), (500, '2 AWG'), (600, '1 AWG'), (800, '1/0 AWG'), (1000, '2/0 AWG'), (1200, '3/0 AWG')]  # NEC 250.122
FLC460 = [(0.5, 1.1), (0.75, 1.6), (1, 2.1), (1.5, 3.0), (2, 3.4), (3, 4.8), (5, 7.6), (7.5, 11), (10, 14), (15, 21), (20, 27), (25, 34), (30, 40), (40, 52), (50, 65)]   # NEC Table 430.250
FLC208 = [(0.5, 2.4), (0.75, 3.5), (1, 4.6), (1.5, 6.6), (2, 7.5), (3, 10.6), (5, 16.7), (7.5, 24.2), (10, 30.8)]
OCPD = [15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100, 110, 125, 150, 175, 200, 225, 250, 300, 350, 400, 450, 500, 600, 700, 800, 1000]
def cond(I):
    return next(s for s, a in AMP if a >= I)
def egc(ocpd): return next(s for a, s in EGC if a >= ocpd)
RKM = {'14 AWG': 10.3, '12 AWG': 6.33, '10 AWG': 3.97, '8 AWG': 2.51, '6 AWG': 1.61, '4 AWG': 1.01, '3 AWG': 0.804, '2 AWG': 0.636, '1 AWG': 0.505, '1/0 AWG': 0.400, '2/0 AWG': 0.317,
       '3/0 AWG': 0.251, '4/0 AWG': 0.199, '250 kcmil': 0.169, '300 kcmil': 0.141, '350 kcmil': 0.120, '400 kcmil': 0.105, '500 kcmil': 0.0847, '600 kcmil': 0.0702}   # ohm/km, NEC Ch. 9 Table 8 uncoated Cu
SIZES = [s for s, _ in AMP]
def vd(size, I, L, V): return math.sqrt(3)*I*L/1000*RKM[size]/V*100      # % three-phase, resistive (NEC 210.19 IN No. 4 / 215.2 IN No. 2 limits 3 % / 5 %)
def upsize(size, I, L, V, lim):
    i = SIZES.index(size)
    while vd(SIZES[i], I, L, V) > lim and i < len(SIZES) - 1: i += 1
    return SIZES[i]
PMAP = {}
LOCAL = True      # X-ELS-02A: branch circuits from a local panel per sector on routed tray
def rows(local=None, pmap=None):
    local = LOCAL if local is None else local
    pmap = PMAP if pmap is None else pmap
    host = lambda sec: pmap.get(sec, sec)
    inv = list(csv.DictReader(open(os.path.join(ROOT, 'docs-authority/inventory/MOTOR_INVENTORY.csv'))))
    C = runpy.run_path(os.path.join(ROOT, 'docs-authority/_line_list.py'))['C']
    g = json.load(open(os.path.join(ROOT, 'flow_graph/plant_flow_graph.json'))); N = {n['unit_id']: n for n in g['nodes']}
    er = C.get('SOL_ARK_60K', ([0, 0, 0], ''))[0]
    man = lambda a, b: (abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2]))/1000
    PAN = {}
    if local:
        pts = collections.defaultdict(list)
        for m in inv:
            if m['unit'] in C: pts[host(m['sector'])].append(C[m['unit']][0])
        for sec, P in pts.items():
            PAN[sec] = [sorted(p[k] for p in P)[len(P)//2] for k in range(3)]     # panel at the sector median point (Manhattan-optimal), A-M-122 Rev B
    def run(u, sec=None):
        c = C.get(u)
        if not c: return 30.0, 'no position: 30 m (assumed)'
        p = c[0]
        if local and host(sec) in PAN: return man(p, PAN[host(sec)])*1.1 + 3, f'routed tray from panel LP-{host(sec)} (Manhattan x 1.1 + 3 m drop, assumed)'
        return man(p, er)*1.2 + 5, 'Manhattan to the electrical room x 1.2 + 5 m (assumed)'
    load = collections.defaultdict(list)
    R = []
    def add(sec, sub, unit, circ, ctype, size, ins, V, n, L, basis, qty=1):
        R.append(dict(sector=sec, subsystem=sub, unit=unit, circuit=circ, type=ctype, size=size, insulation=ins, voltage_class=V, conductors=n, length_m=round(L, 1), qty=qty,
                      total_m=round(n*L*qty, 1), basis=basis))
    for m in inv:
        q = int(m['qty']); kw = float(m['shaft_kW']); u = m['unit']; L, lb = run(u, m['sector'])
        if m['voltage'].startswith(('480', '208')):
            hp = kw*1.341*1.15; tbl = FLC460 if m['voltage'].startswith('480') else FLC208
            flc = next((a for h, a in tbl if h >= hp), None)
            if flc is None: flc = hp*746/(math.sqrt(3)*(460 if tbl is FLC460 else 208)*0.85*0.9)
            I = 1.25*flc; s = cond(I); oc = next(o for o in OCPD if o >= 2.5*flc)          # NEC 430.52 inverse-time breaker 250 %
            Vl = 460 if tbl is FLC460 else 208; s0 = s; s = upsize(s, flc, L, Vl, 3.0); load[host(m['sector'])].append((flc, q, Vl))
            if s != s0: lb += f'; upsized from {s0} for 3 % drop'
            add(m['sector'], m['subsystem'], u, f"{m['device']} feeder", 'power, 3 ph + EGC', s, 'XHHW-2 Cu, 600 V, tray cable TC-ER', '600 V', 3, L, f'NEC 430.22: 1.25 x {flc:.1f} A FLC; {lb}', q)
            add(m['sector'], m['subsystem'], u, f"{m['device']} EGC", 'equipment ground', egc(oc), 'green XHHW-2 Cu', '600 V', 1, L, f'NEC 250.122 at {oc} A OCPD', q)
            add(m['sector'], m['subsystem'], u, f"{m['device']} control", 'control', '18 AWG', 'TFFN 3-pair, shielded', '600 V', 6, L, 'start/stop, run, fault (assumed)', q)
        else:
            Lc = 10.0
            add(m['sector'], m['subsystem'], u, f"{m['device']} power", 'DC power pair', '16 AWG' if kw < 0.06 else '14 AWG', 'TC-ER 2-cond', '600 V', 2, Lc, 'from the local 24/48 V DC panel at the unit, 10 m (assumed)', q)
            add(m['sector'], m['subsystem'], u, f"{m['device']} signal", 'control', '18 AWG', 'shielded pair', '300 V', 2, Lc, 'speed/position feedback (assumed)', q)
    for sec, ld in load.items():                                            # panel feeders, NEC 430.24
        if not (local and sec in PAN): continue
        for Vl in (460, 208):
            fl = [f for f, q, v in ld for _ in range(q) if v == Vl]
            if not fl: continue
            I = 1.25*max(fl) + sum(fl) - max(fl); L = man(PAN[sec], er)*1.2 + 5; ns = math.ceil(I/380); s = upsize(cond(I/ns), I/ns, L, Vl, 2.0)
            add(sec, 'distribution', f'LP-{sec}', f'panel feeder {Vl} V', 'power, 3 ph + EGC', s, 'XHHW-2 Cu, tray cable TC-ER', '600 V', 4*ns, L, f'NEC 430.24: {I:.1f} A in {ns} parallel set(s) (310.10(G)); drop <= 2 % feeder so branch 3 % keeps total under 5 %; Manhattan to the electrical room x 1.2 + 5 m')
    # collection bus and MV
    cb = [l.split('|')[1:-1] for l in open(os.path.join(ROOT, 'docs-authority/COLLECTION_BUS.md')) if l.startswith('| CB-')]
    for c in cb:
        name, ninv, Ia, br = c[0].strip(), int(c[1]), float(c[3]), int(c[4])
        add('ELEC', 'collection bus', name, 'inverter AC output to section bus', 'power, 3 ph', cond(1.25*60e3/(math.sqrt(3)*480)), 'XHHW-2 Cu', '600 V', 3, 25.0, 'NEC 705.28: 1.25 x 72.2 A; 25 m inverter to section board (assumed)', ninv)
        sets = 3 if br <= 1000 else 4
        add('ELEC', 'collection bus', name, f'section main to {name} transformer LV', 'power, 3 ph parallel', cond(br/sets), 'XHHW-2 Cu', '600 V', 3*sets, 15.0, f'{sets} sets for {br} A main (NEC 310.10(G)); 15 m (assumed)')
        add('ELEC', 'collection bus', name, 'section EGC', 'equipment ground', egc(br), 'green XHHW-2 Cu', '600 V', sets, 15.0, 'NEC 250.122')
        add('ELEC', 'MV', name, 'transformer MV to the PCC switchgear', 'MV power, 3 ph', '2 AWG', 'MV-105 Cu, 133 % insulation, tape shield', '15 kV', 3, 100.0, '34.7 A; minimum practical 15 kV size; 100 m (assumed)')
    # PV source circuits
    pv = N['PV_ARRAY']['params']; nmod = pv['count']; per = 18; ns = math.ceil(nmod/per)
    add('ELEC_PV', 'roof array', 'PV_ARRAY', 'PV source circuit home run (+/-)', 'PV DC', '10 AWG', 'PV Wire, UL 4703, 2 kV', '2000 V DC', 2, 60.0, f'{nmod} modules / {per} per string (Voc x 1.1 < 1000 V, assumed) = {ns} strings; NEC 690.8 1.56 x Isc; 60 m mean home run (assumed)', ns)
    add('ELEC_PV', 'roof array', 'PV_ARRAY', 'array EGC', 'equipment ground', '10 AWG', 'bare Cu', '-', 1, 60.0, 'NEC 690.45 / 250.122', ns)
    # hall lighting
    h = N['EXT_HALL']['params']['hvac']; inst = h['light_kW']/0.10; nc = math.ceil(inst/(0.8*20*277/1000))
    lsz = next(z for z in SIZES[1:] if 2*16.0*120.0/1000*RKM[z]/277*100 <= 3.0)    # X-ELS-06: 16 A (80 % of 20 A) over 120 m, single-phase drop <= 3 % (NEC 210.19 IN No. 4)
    add('ELEC_PV', 'hall', 'EXT_HALL', 'lighting branch circuit 277 V', 'power, 1 ph + N + EGC', lsz, 'THHN/THWN-2 Cu in EMT', '600 V', 3, 120.0, f'installed {inst:.0f} kW (average {h["light_kW"]} kW at 10 % lit) / 4.43 kW per 20 A circuit at 80 % (16 A); 120 m mean (assumed); {lsz} for 3 % drop (X-ELS-06)', nc)
    # grounding grid
    gs = json.loads(os.popen(f'cd {ROOT} && python3 docs-authority/_grounding_study.py').read().strip().splitlines()[-1])
    add('ELEC', 'grounding', 'GROUND_GRID', 'ring and mesh conductors', 'bare grounding', '4/0 AWG', 'bare soft-drawn Cu', '-', 1, gs['ring_m'] + gs['mesh_m'], f"AQS-ELEC-005 ring {gs['ring_m']:.0f} m + mesh {gs['mesh_m']:.0f} m; 4/0 assumed (IEEE 80 conductor sizing at X-ELS)")
    return R
def write(R):
    D = os.path.join(ROOT, 'docs-authority/inventory'); R.sort(key=lambda r: (r['sector'], str(r['subsystem']), r['unit'], r['circuit']))
    with open(os.path.join(D, 'WIRE_INVENTORY.csv'), 'w', newline='') as f: w = csv.DictWriter(f, list(R[0].keys())); w.writeheader(); w.writerows(R)
    F = collections.defaultdict(lambda: [0.0, 0])
    for r in R: k = (r['type'].split(',')[0], r['size'], r['insulation'], r['voltage_class']); F[k][0] += r['total_m']; F[k][1] += r['qty']
    FF = sorted(F.items(), key=lambda kv: -kv[1][0])
    with open(os.path.join(D, 'WIRE_FAMILIES.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['family', 'type', 'size', 'insulation', 'voltage_class', 'conductor_m', 'circuits'])
        for i, ((t, s, ins, V), (m, n)) in enumerate(FF, 1): w.writerow([f'WF-{i:02d}', t, s, ins, V, round(m), n])
    tot = sum(r['total_m'] for r in R); a = sum(r['total_m'] for r in R if 'assumed' in r['basis'])
    L = ['# Wire inventory', '', 'Document number: AQS-INV-002', 'Revision: C', 'Date: 2026-10-15',
         'Authority: AQS-PLAN-007 X-INV-03. Generated by `flow_graph/inventory/wire.py`; CSVs beside this file. A-M-122.', '', '| Rev | Description | Date |', '| --- | --- | --- |', '| A | First issue. | 2026-10-15 |', '| B | X-ELS-02A: branch circuits from a local panel per sector (LP-<sector>) on routed tray; panel feeders NEC 430.24; conductors upsized for 3 % branch / 2 % feeder drop (NEC Ch. 9 Table 8). Conductor 216.1 -> 130.0 km; copper mass 14.2 -> 13.9 t (mass is dominated by the collection bus, MV and grid, which do not change). | 2026-10-15 |', '| C | X-ELS-02 panel merge by calculation (section 0). | 2026-10-15 |', '',
         f'{len(R)} circuit rows, {tot/1000:.1f} km of conductor; {a/1000:.1f} km rests on assumed lengths or counts (A-M-122). Sizing: NEC 2023 430.22 / Table 430.250 for motor branch circuits, Table 310.16 75 C copper with 240.4(D), 250.122 equipment grounding, 705.28 inverter outputs, 690.8 PV source circuits. Voltage drop: branch <= 3 %, feeder <= 2 % (resistive, NEC Ch. 9 Table 8). Tray fill is checked with the cable schedule (X-ELS-02).', '',
         '## 1. Family rollup', '', '| Family | Type | Size | Insulation | Voltage class | Conductor m | Circuits |', '| --- | --- | --- | --- | --- | --- | --- |']
    L += [f'| WF-{i:02d} | {t} | {s} | {ins} | {V} | {m:.0f} | {n} |' for i, ((t, s, ins, V), (m, n)) in enumerate(FF, 1)]
    L += ['', '## 2. Circuits by sector > sub-system > unit', '']
    cur = None
    for r in R:
        if r['sector'] != cur:
            cur = r['sector']; L += ['', f'### {cur}', '', '| Sub-system | Unit | Circuit | Size | Insulation | Cond. | Length m | Qty | Total m | Basis |', '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
        L.append(f"| {r['subsystem']} | {r['unit']} | {r['circuit']} | {r['size']} | {r['insulation']} | {r['conductors']} | {r['length_m']} | {r['qty']} | {r['total_m']} | {r['basis']} |")
    open(os.path.join(D, 'WIRE_INVENTORY.md'), 'w').write('\n'.join(L) + '\n'); return FF, tot, a
CUKG = {'18 AWG': 0.823, '16 AWG': 1.31, '14 AWG': 2.08, '12 AWG': 3.31, '10 AWG': 5.26, '8 AWG': 8.37, '6 AWG': 13.3, '4 AWG': 21.2, '3 AWG': 26.7, '2 AWG': 33.6, '1 AWG': 42.4,
        '1/0 AWG': 53.5, '2/0 AWG': 67.4, '3/0 AWG': 85.0, '4/0 AWG': 107, '250 kcmil': 127, '300 kcmil': 152, '350 kcmil': 177, '400 kcmil': 203, '500 kcmil': 253, '600 kcmil': 304}   # mm2
def cu_kg(R): return sum(r['total_m']*CUKG.get(r['size'], 0)*8.96e-3 for r in R)
def vd_ok(R): return all(r['size'] != SIZES[-1] for r in R if 'upsized' in r['basis'] or r['circuit'].startswith('panel feeder'))
def merge_panels():
    """X-ELS-02 panel merge by calculation: repeatedly fold the panel with the smallest feeder into the panel that minimises copper, accepting the
    merge only if total copper mass does not rise and every branch/feeder still meets its drop limit without running past the largest size.
    A panel removed is a board, enclosure and main breaker not built; copper is the only cost traded against it (A-M-122 Rev C)."""
    pmap = {}; R = rows(True, pmap); best = cu_kg(R); log = []
    while True:
        pans = sorted({r['unit'][3:] for r in R if r['circuit'].startswith('panel feeder')}, key=lambda h: sum(r['total_m']*CUKG.get(r['size'], 0) for r in R if r['unit'] == f'LP-{h}'))
        done = False
        for small in pans:
            trial = []
            for h in pans:
                if h == small: continue
                pm = {k: (h if v == small else v) for k, v in pmap.items()}; pm[small] = h
                Rt = rows(True, pm)
                if vd_ok(Rt): trial.append((cu_kg(Rt), h, pm, Rt))
            if trial:
                c, h, pm, Rt = min(trial, key=lambda t: t[0])
                if c <= best + 1e-6:
                    log.append((small, h, round(best, 1), round(c, 1))); best, pmap, R = c, pm, Rt; done = True; break
                else: log.append((small, None, round(best, 1), round(c, 1)))
        if not done: return pmap, log, R
if __name__ == '__main__':
    c0 = cu_kg(rows(True, {})); n0 = len({r['unit'] for r in rows(True, {}) if r['circuit'].startswith('panel feeder')})
    pm, log, R = merge_panels(); PMAP.update(pm); FF, tot, a = write(R); print(round(tot), 'm', round(a), 'assumed', len(FF), 'families')
    n1 = len({r['unit'] for r in R if r['circuit'].startswith('panel feeder')}); c1 = cu_kg(R)
    nd = {}
    for sm, h, b, c in log:
        if h is None and c - b < 5.0: nd[sm] = min(nd.get(sm, 9e9), c - b)
    near = sorted(nd.items(), key=lambda t: t[1])
    md = os.path.join(ROOT, 'docs-authority/inventory/WIRE_INVENTORY.md'); txt = open(md).read()
    txt = txt.replace('## 1. Family rollup', '\n'.join(['## 0. Panel merge (X-ELS-02, by calculation)', '',
        f'Rule (`merge_panels`): fold the panel with the least feeder copper into the host that minimises total copper; accept only if total copper mass does not rise and every branch and feeder meets 3 % / 2 % drop without exceeding 600 kcmil. Result: {n0} -> {n1} panels, copper {c0/1000:.2f} -> {c1/1000:.2f} t.', '',
        '| Merged sector | Host panel |', '| --- | --- |'] + [f'| {k} | LP-{v} |' for k, v in sorted(pm.items())] + ['',
        'Rejected by less than 5 kg of copper (kept separate under the rule; a panel enclosure and main breaker probably outweigh this, but no cost basis is registered, so they are held for review): ' + ', '.join(f'{k} (+{d:.1f} kg)' for k, d in near) + '.', '', '## 1. Family rollup']))
    txt = txt.replace("'| B | X-ELS-02A", "'| B | X-ELS-02A")
    open(md, 'w').write(txt); print(n0, '->', n1, 'panels', round(c0), '->', round(c1), 'kg', near)
    for i, ((t, s, ins, V), (m, n)) in enumerate(FF, 1): print(f'WF-{i:02d}', t, s, ins, V, round(m), n)
