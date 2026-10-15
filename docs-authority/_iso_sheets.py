"""X-PIP-03 isometric sheet per line (AQS-ISO-002). Route legs from the AQS-ISO-001 rule (_iso_routes.py); per line: isometric SVG with
leg dimensions, cut list, fittings, flanges, bolting, gaskets and joint count. Elbow take-off: ASME B16.9 long-radius 90 deg centre-to-end
for metal classes; thermoplastic socket and fusion elbows take 0.5 x OD (A-M-121, set from ASTM D2467 / ISO 15494 tables at fabrication).
Random length 6 m. Flanges at both equipment nozzles (AQS-PIP-003 'flanged at equipment'); ASME B16.5 Class 150 bolting.
Writes docs-authority/iso/<LINE>.svg, docs-authority/iso/ISO_SHEETS.csv and docs-authority/ISO_SHEETS.md. Run: python3 docs-authority/_iso_sheets.py"""
import runpy, json, math, os, csv, collections
ns = runpy.run_path('docs-authority/_line_list.py'); C = ns['C']; rows = ns['rows']
seed = json.load(open('flow_graph/placement_seed.json')); D = seed['datums_mm']
def lvl(z): return min(D, key=lambda k: abs(z - D[k]) if z >= D[k] else 1e9)
OD = {15: 21.3, 20: 26.7, 25: 33.4, 32: 42.2, 40: 48.3, 50: 60.3, 65: 73.0, 80: 88.9, 100: 114.3, 150: 168.3, 200: 219.1, 250: 273.1, 300: 323.9}   # ASME B36.10M
B169 = {15: 38, 20: 29, 25: 38, 32: 48, 40: 57, 50: 76, 65: 95, 80: 114, 100: 152, 150: 229, 200: 305, 250: 381, 300: 457}                  # ASME B16.9 LR 90
BOLT = {15: (4, '1/2'), 20: (4, '1/2'), 25: (4, '1/2'), 32: (4, '1/2'), 40: (4, '1/2'), 50: (4, '5/8'), 65: (4, '5/8'), 80: (4, '5/8'), 100: (8, '5/8'),
        150: (8, '3/4'), 200: (8, '3/4'), 250: (12, '7/8'), 300: (12, '7/8')}                                                                # ASME B16.5 Class 150
MAT = {'P1': 'PVC-U Sch 80 ASTM D1785', 'P2': 'CPVC Sch 80 ASTM F441', 'P3': 'PVDF SDR 21 ISO 10931', 'P4': 'PP-H ISO 15494', 'P5': 'HDPE PE4710 DR 11 (ASTM D3035)', 'M1': '316L ASTM A312', 'M2': 'CS ASTM A106 Gr B', 'F1': 'FRP vinyl ester', 'G1': 'borosilicate 3.3'}
JOINT = {'P1': 'solvent', 'P2': 'solvent', 'P3': 'fusion', 'P4': 'fusion', 'P5': 'fusion', 'M1': 'butt weld', 'M2': 'butt weld', 'F1': 'butt-and-strap', 'G1': 'coupling'}
RACK = 3200; os.makedirs('docs-authority/iso', exist_ok=True)
def svg(name, legs, dn, cl, a, b, info):
    pts = [(0.0, 0.0, 0.0)]
    for k, v in zip('zxyz', legs):
        x, y, z = pts[-1]; pts.append((x + (v if k == 'x' else 0), y + (v if k == 'y' else 0), z + (v if k == 'z' else 0)))
    P = [((x - y)*math.cos(math.pi/6), -(z + (x + y)*math.sin(math.pi/6))) for x, y, z in pts]
    xs, ys = [p[0] for p in P], [p[1] for p in P]; w = max(max(xs) - min(xs), 1); h = max(max(ys) - min(ys), 1); s = 520/max(w, h)
    Q = [(40 + (px - min(xs))*s, 60 + (py - min(ys))*s) for px, py in P]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="820" height="680" font-family="sans-serif" font-size="11"><rect x="1" y="1" width="818" height="678" fill="white" stroke="black"/>',
         f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in Q)}" fill="none" stroke="black" stroke-width="3"/>']
    for i, (v, k) in enumerate(zip(legs, 'ZXYZ')):
        if abs(v) > 1:
            mx, my = (Q[i][0] + Q[i + 1][0])/2, (Q[i][1] + Q[i + 1][1])/2; o.append(f'<text x="{mx + 6:.1f}" y="{my - 4:.1f}">{k} {v:+.0f}</text>')
    o.append(f'<circle cx="{Q[0][0]:.1f}" cy="{Q[0][1]:.1f}" r="5" fill="black"/><text x="{Q[0][0] + 8:.1f}" y="{Q[0][1] + 14:.1f}">{a}</text>')
    o.append(f'<circle cx="{Q[-1][0]:.1f}" cy="{Q[-1][1]:.1f}" r="5" fill="none" stroke="black"/><text x="{Q[-1][0] + 8:.1f}" y="{Q[-1][1] + 14:.1f}">{b}</text>')
    o.append('<g transform="translate(600,610)"><line x1="0" y1="0" x2="26" y2="-15" stroke="black"/><text x="28" y="-15">+X</text><line x1="0" y1="0" x2="-26" y2="-15" stroke="black"/><text x="-48" y="-15">+Y</text><line x1="0" y1="0" x2="0" y2="-30" stroke="black"/><text x="4" y="-32">+Z</text></g>')
    tb = [f'AQS-ISO-002  {name}', f'DN{dn}  class {cl}  {MAT.get(cl, cl)}', f'{a} -> {b}'] + info
    o += [f'<text x="20" y="{600 + 14*i}">{t}</text>' for i, t in enumerate(tb[:6])]
    open(f'docs-authority/iso/{name}.svg', 'w').write('\n'.join(o) + '</svg>\n')
recs = []; miss = []
for r in rows:
    if not r[3].startswith('DN'): continue
    a, b = C.get(r[1]), C.get(r[2])
    if not a or not b: miss.append(r[0]); continue
    (x1, y1, z1), (x2, y2, z2) = a[0], b[0]; zr = D[lvl(z1)] + RACK
    legs = [zr - z1, x2 - x1, y2 - y1, z2 - zr]; nz = [v for v in legs if abs(v) > 1]
    dn = int(r[3][2:]); cl = r[4]; el = max(len(nz) - 1, 0)
    to = B169.get(dn, 1.5*dn) if cl.startswith('M') else 0.5*OD.get(dn, dn)
    cuts = []
    for i, v in enumerate(nz):
        L = abs(v) - to*((1 if i > 0 else 0) + (1 if i < len(nz) - 1 else 0))
        while L > 6000: cuts.append(6000); L -= 6000
        cuts.append(max(L, 0))
    pipe_m = sum(cuts)/1000; nb, bs = BOLT.get(dn, (8, '3/4'))
    joints = 2*el + (len(cuts) - len(nz)) + 2
    rec = dict(line=r[0], DN=dn, cls=cl, material=MAT.get(cl, cl), frm=r[1], to=r[2], route_m=round(sum(abs(v) for v in nz)/1000, 2), pipe_m=round(pipe_m, 2),
               pieces=len(cuts), cut_list_mm=' '.join(f'{c:.0f}' for c in cuts), elbows_90=el, flanges=2, gaskets=2, stud_bolts=2*nb, stud_size=f'{bs} in', joints=joints, joint_type=JOINT.get(cl, '-'))
    recs.append(rec)
    svg(r[0], legs, dn, cl, r[1], r[2], [f"pipe {pipe_m:.2f} m in {len(cuts)} pieces; cut {rec['cut_list_mm']} mm"[:110], f'{el} x 90 LR elbow; 2 flanges B16.5 Cl150; {2*nb} studs {bs} in; {joints} {JOINT.get(cl, "")} joints', 'Study isometric. Supports and stress X-PIP-04.'])
with open('docs-authority/iso/ISO_SHEETS.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, list(recs[0].keys())); w.writeheader(); w.writerows(recs)
T = collections.defaultdict(lambda: dict(n=0, m=0.0, el=0, fl=0, j=0))
for x in recs:
    t = T[(x['cls'], x['DN'])]; t['n'] += 1; t['m'] += x['pipe_m']; t['el'] += x['elbows_90']; t['fl'] += x['flanges']; t['j'] += x['joints']
L = ['# Isometric sheets', '', 'Document number: AQS-ISO-002', 'Revision: A', 'Date: 2026-10-15',
     'Authority: AQS-PLAN-007 X-PIP-03. Generated by `docs-authority/_iso_sheets.py` from the AQS-ISO-001 routes and the AQS-PIP-004 line list. One sheet per line in `docs-authority/iso/<LINE>.svg`; quantities in `docs-authority/iso/ISO_SHEETS.csv`. Study. Not a stamped shop pack. A-M-121.', '',
     '| Rev | Description | Date |', '| --- | --- | --- |', '| A | First issue: every piped line. | 2026-10-15 |', '',
     f'Lines {len(recs)}; waiting on positions {len(miss)}{": " + ", ".join(miss) if miss else ""}. Pipe {sum(x["pipe_m"] for x in recs):.0f} m, elbows {sum(x["elbows_90"] for x in recs)}, flanges {sum(x["flanges"] for x in recs)}, joints {sum(x["joints"] for x in recs)}.', '',
     'Basis: route rule of AQS-ISO-001; elbow take-off ASME B16.9 long-radius (metal) or 0.5 x OD (thermoplastic, A-M-121); 6 m random lengths; flanges at both nozzles; ASME B16.5 Class 150 bolting; OD ASME B36.10M. Not checked here: clashes with structure and other lines along the rack (X-PIP-04 with supports and stress).', '',
     '## Quantities by class and size', '', '| Class | Material | DN | Lines | Pipe m | 90 deg elbows | Flanges | Joints |', '| --- | --- | --- | --- | --- | --- | --- | --- |']
L += [f'| {c} | {MAT.get(c, c)} | {dn} | {t["n"]} | {t["m"]:.1f} | {t["el"]} | {t["fl"]} | {t["j"]} |' for (c, dn), t in sorted(T.items())]
L += ['', '## Sheet index', '', '| Line | DN | Class | From | To | Pipe m | Elbows | Sheet |', '| --- | --- | --- | --- | --- | --- | --- | --- |']
L += [f"| {x['line']} | {x['DN']} | {x['cls']} | {x['frm']} | {x['to']} | {x['pipe_m']} | {x['elbows_90']} | [svg](iso/{x['line']}.svg) |" for x in recs]
open('docs-authority/ISO_SHEETS.md', 'w').write('\n'.join(L) + '\n'); print(len(recs), len(miss), round(sum(x['pipe_m'] for x in recs)))
