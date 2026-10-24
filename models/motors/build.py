"""X-INV-02C motor family models, drawings and BOMs. Geometry from AQS-INV-005 (docs-authority/inventory/MOTOR_DESIGNS.csv, MAGNET_COMPARISON.csv)
and IEC 60072-1 frame dimensions; writes models/motors/<MF-nn>/export/<mf>.step, .stl, drawing.svg, bom.csv, fasteners.csv, WORK_ORDER.md.
Study models: envelope-correct parts (lamination stack with slots, rotor, shaft, frame or flange housing), not production tolerancing.
Run: $CADQUERY_PYTHON models/motors/build.py (A-M-131)"""
import csv, math, os, sys
import cadquery as cq
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from flow_graph.inventory.motor_designs import IEC72, BRG
D = {r['family']: r for r in csv.DictReader(open(f'{ROOT}/docs-authority/inventory/MOTOR_DESIGNS.csv'))}
F = {r['family']: r for r in csv.DictReader(open(f'{ROOT}/docs-authority/inventory/MOTOR_FAMILIES.csv'))}
MG = {r['family']: r for r in csv.DictReader(open(f'{ROOT}/docs-authority/inventory/MAGNET_COMPARISON.csv')) if r['magnet'] == 'NdFeB'}
def slotted(od, idd, L, q, depth, width, inner=True):
    b = cq.Workplane('XY').circle(od/2).circle(idd/2).extrude(L)
    r0 = idd/2 if inner else od/2 - depth
    for k in range(q):
        a = 360*k/q
        s = cq.Workplane('XY').box(depth, width, L, centered=(False, True, False)).translate((r0, 0, 0)).rotate((0, 0, 0), (0, 0, 1), a)
        b = b.cut(s)
    return b
def induction(f, d):
    fr = (F[f]['size'].split('IEC ')[1].split(' ')[0]) if 'IEC' in F[f]['size'] else None
    Dg, L, Do = float(d['Dg_mm']), float(d['L_mm']), float(d['Dout_mm'])
    Qs = 24 if Do < 140 else 36; Qr = 22 if Qs == 24 else 28
    st = slotted(Do, Dg + 0.6, L, Qs, 0.22*(Do - Dg), math.pi*Dg/Qs*0.5)
    ro = slotted(Dg - 0.6, Dg*0.33, L, Qr, 0.08*Dg, math.pi*Dg/Qr*0.45, inner=False).translate((0, 0, 0))
    parts = [('stator stack', st), ('rotor stack', ro)]
    bom = [('stator laminations M400-50A (EN 10106) 0.5 mm', round(L/0.5), 'EN 10106'), ('rotor laminations M400-50A 0.5 mm', round(L/0.5), 'EN 10106'),
           (f"magnet wire IEC 60317-13 {d['conductor']}", f"{d['copper_kg']} kg", 'X-INV-03 wire line'), ('die-cast Al cage (bars + rings)', f"{0.12*float(d['steel_kg']):.2f} kg", 'A356 in-house melt (assumed 12 % of steel mass)')]
    if fr in IEC72:
        H, Ds, E, A, Bb, K = IEC72[fr]; shL = L + 2*60 + E
        sh = cq.Workplane('XY').circle(Ds/2).extrude(shL).translate((0, 0, -60))
        fo = min(2*H*0.98, Do + 24); fr_ = cq.Workplane('XY').circle(fo/2).circle(Do/2).extrude(L + 40).translate((0, 0, -20))
        feet = cq.Workplane('XY').box(A + 20, 12, Bb + 40).translate((0, -H + 6, L/2)).union(cq.Workplane('XY').box(A*0.6, H - fo/2 + 14, Bb + 20).translate((0, -H + 12 + (H - fo/2 + 2)/2, L/2)))
        for sx in (-1, 1):
            for z in (L/2 - Bb/2, L/2 + Bb/2):
                feet = feet.cut(cq.Workplane('XZ').circle(K/2).extrude(-20).translate((sx*A/2, -H + 16, z)))
        parts += [('shaft C45', sh), ('frame A356', fr_.union(feet))]
        bom += [(f'shaft C45 (EN 10083-2) D{Ds} x {shL:.0f} mm, key to IEC 60072-1', 1, 'turned'), (f'frame A356 IEC {fr}, feet A{A} x B{Bb}, holes K{K}', 1, 'cast + machined'),
                ('end shields A356', 2, 'cast + machined'), (f'bearing {BRG.get(fr, "6204-2Z")}', 2, 'X-INV-05 OF bearing family'), ('fan PP + fan cover steel', 1, 'IC 411'), ('terminal box + 6-stud block', 1, 'IEC 60034-8 marking')]
        fas = [('M5 x 16 end-shield screw', 'ISO 4762 8.8 Zn', 8), ('M4 x 10 terminal box screw', 'ISO 7380 A2', 4), (f'M{K - 2} foot bolt (by user)', 'ISO 898-1 8.8', 4)]
    else:
        sh = cq.Workplane('XY').circle(max(8, Dg*0.2)/2).extrude(L + 40).translate((0, 0, -20)); parts.append(('shaft C45', sh))
        bom += [('shaft C45', 1, 'turned'), ('compressor shell (scroll line X-MFG-35)', 0, 'not in this model')]; fas = [('lead feed-through, hermetic glass-to-metal', 'UL 60335-2-34', 1)]
    return parts, bom, fas
def pm(f, d, flange, kind):
    m = MG.get(f) or MG['MF-01']; Dr, L = float(m['D_mm']), float(m['L_mm']); Ds = max(3.0, Dr*0.3)
    so = flange*0.8; st = slotted(so, Dr + 1.0, L, 12 if kind == 'BLDC' else 8, 0.3*(so - Dr), math.pi*Dr/12*0.6)
    ro = cq.Workplane('XY').circle(Dr/2 - 3).circle(Ds/2).extrude(L); mag = cq.Workplane('XY').circle(Dr/2).circle(Dr/2 - 3).extrude(L)
    hs = cq.Workplane('XY').rect(flange, flange).extrude(L + 20).translate((0, 0, -10)).cut(cq.Workplane('XY').circle(so/2).extrude(L + 20).translate((0, 0, -10)))
    sh = cq.Workplane('XY').circle(Ds/2).extrude(L + 40).translate((0, 0, -10))
    parts = [('stator stack', st), ('rotor core', ro), ('magnet ring NdFeB', mag), ('housing Al 6063', hs), ('shaft', sh)]
    bom = [('stator laminations M270-35A 0.35 mm', round(L/0.35), 'EN 10106'), (f"NdFeB magnets {m['magnet_g']} g (basis; ferrite variant in AQS-INV-005)", 1, 'X-INV-02D'),
           ('magnet wire IEC 60317-13 class 200', '-', 'X-INV-03 wire line'), (f'housing extruded 6063, NEMA ICS 16 {flange} mm flange', 1, 'extruded + machined'),
           ('bearing 608-2Z' if kind == 'stepper' else 'bearing 6000-2Z', 2, 'X-INV-05'), ('Hall sensor PCB' if kind == 'BLDC' else 'connector 4-pin', 1, 'X-INV-05 electronics')]
    fas = [('M3 x 8 end-cap screw', 'ISO 7380 A2', 4), (f"M{4 if flange < 57 else 5} flange screw (by user)", 'ISO 4762 A2', 4)]
    return parts, bom, fas
def solenoid(f):
    c = cq.Workplane('XY').circle(15).circle(11.2).extrude(30); p = cq.Workplane('XY').circle(6).extrude(40).translate((0, 0, -5))
    return [('coil', c), ('plunger 430F', p)], [('coil PA66-GF bobbin, class H wire IEC 60317-13', 1, 'X-INV-03'), ('plunger and frame 430F', 1, 'turned'), ('connector EN 175301-803', 1, '')], [('M3 x 6 frame screw', 'ISO 7380 A2', 2)]
for f, r in F.items():
    d = D.get(f, {}); t = r['motor_type']
    if t.startswith(('induction', 'hermetic')): parts, bom, fas = induction(f, d)
    elif t == 'BLDC': parts, bom, fas = pm(f, d, 42 if '42' in r['size'] else 57, 'BLDC')
    elif t.startswith('BLDC actuator'):
        parts, bom, fas = pm('MF-01', d, 42, 'BLDC'); bom += [('worm gear set (bronze wheel, steel worm)', 1, 'cut in-house'), ('ISO 5211 F03 output flange + 9 mm square', 1, 'machined')]
    elif t == 'stepper': parts, bom, fas = pm(f, d, 57 if '57' in r['size'] else 86, 'stepper')
    else: parts, bom, fas = solenoid(f)
    o = f'{ROOT}/models/motors/{f}'; x = f'{o}/export'; os.makedirs(x, exist_ok=True)
    parts = [(n, s.rotate((0, 0, 0), (1, 0, 0), 90)) for n, s in parts]     # axis horizontal (-Y), feet down (-Z), as mounted (IM B3)
    asm = cq.Assembly(name=f)
    for n, s in parts: asm.add(s, name=n.replace(' ', '_'))
    asm.save(f'{x}/{f.lower()}.step')
    comp = parts[0][1]
    for _, s in parts[1:]: comp = comp.union(s)
    cq.exporters.export(comp, f'{x}/{f.lower()}.stl')
    # this CadQuery SVG exporter draws world +Z toward the bottom of the sheet; spin the solid 180 deg about the view axis (rigid, no mirror) so feet print down
    PD = (1, -1, 0.7)
    cq.exporters.export(comp.rotate((0, 0, 0), PD, 180), f'{x}/drawing.svg', opt={'projectionDir': PD, 'showHidden': False, 'width': 800, 'height': 600, 'marginLeft': 60, 'marginTop': 60})
    with open(f'{o}/bom.csv', 'w', newline='') as fh:
        w = csv.writer(fh); w.writerow(['item', 'description', 'qty', 'basis']); [w.writerow([i, a, q, b]) for i, (a, q, b) in enumerate(bom, 1)]
    with open(f'{o}/fasteners.csv', 'w', newline='') as fh:
        w = csv.writer(fh); w.writerow(['item', 'size', 'grade', 'qty']); [w.writerow([i, a, g, q]) for i, (a, g, q) in enumerate(fas, 1)]
    open(f'{o}/WORK_ORDER.md', 'w').write(f"# Work order {f}: {t}, {r['size']}, {r['voltage']}\n\nDesign sheet: docs-authority/inventory/motor_families/{f}.md (AQS-INV-005). Model: export/{f.lower()}.step (assembly), .stl, drawing.svg. BOM: bom.csv; fasteners: fasteners.csv.\n\nQuantity: {r['count']} for {r['units']} units. Follow the manufacturing plan in the design sheet section 2; first article to X-INV-02B type test.\n")
    print(f, len(parts), 'parts')
