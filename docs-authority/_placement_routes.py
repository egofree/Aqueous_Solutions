# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""X-PIP-03 close-out: routed lengths from the placement model (AQS-3D-BUILD-001 Rev M).

The placement seed (flow_graph/placement_seed.json, Rev M) carries real, sourced unit
centres; this stage routes every piped line whose both ends are placed, by the A-M-074
rack rule (rise to the source-level rack at datum + 3200 mm, X run, Y run, vertical to
the target; risers at least 300 mm, X-PIP-06). Writes:

- docs-authority/ISO_ROUTES.md  / .json  (the X-PIP-05 supports sidecar)
- docs-authority/iso/ISO_SHEETS.csv / .md (the X-INV-003/004 insulation + fittings sidecar)

Lines with an unplaced end are named in the coverage line - a named gap, never an
invented length (AQS-3D-BUILD-001 Rev G stands: no auto-router, no invented mm; every
centre here traces to a seed source). No SVG is written: the isometric presentation
retired with the auto-router (2026-10-27). Supports, stress and clashes: X-PIP-04.

Run: python3 docs-authority/_placement_routes.py
"""
import csv
import json
import math
import os
import runpy

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(R)

ns = runpy.run_path('docs-authority/_line_list.py')
C = ns['C']
rows = ns['rows']
seed = json.load(open('flow_graph/placement_seed.json'))
D = seed['datums_mm']


def lvl(z):
    return min(D, key=lambda k: abs(z - D[k]) if z >= D[k] else 1e9)


OD = {15: 21.3, 20: 26.7, 25: 33.4, 32: 42.2, 40: 48.3, 50: 60.3, 65: 73.0, 80: 88.9,
      100: 114.3, 150: 168.3, 200: 219.1, 250: 273.1, 300: 323.9}                    # ASME B36.10M
B169 = {15: 38, 20: 29, 25: 38, 32: 48, 40: 57, 50: 76, 65: 95, 80: 114, 100: 152,
        150: 229, 200: 305, 250: 381, 300: 457}                                      # ASME B16.9 LR 90
BOLT = {15: (4, '1/2'), 20: (4, '1/2'), 25: (4, '1/2'), 32: (4, '1/2'), 40: (4, '1/2'),
        50: (4, '5/8'), 65: (4, '5/8'), 80: (4, '5/8'), 100: (8, '5/8'), 150: (8, '3/4'),
        200: (8, '3/4'), 250: (12, '7/8'), 300: (12, '7/8')}                         # ASME B16.5 Cl 150
MAT = {'P1': 'PVC-U Sch 80 ASTM D1785', 'P2': 'CPVC Sch 80 ASTM F441',
       'P3': 'PVDF SDR 21 ISO 10931', 'P4': 'PP-H ISO 15494',
       'P5': 'HDPE PE4710 DR 11 (ASTM D3035)', 'M1': '316L ASTM A312',
       'M2': 'CS ASTM A106 Gr B', 'F1': 'FRP vinyl ester', 'G1': 'borosilicate 3.3'}
JOINT = {'P1': 'solvent', 'P2': 'solvent', 'P3': 'fusion', 'P4': 'fusion', 'P5': 'fusion',
         'M1': 'butt weld', 'M2': 'butt weld', 'F1': 'butt-and-strap', 'G1': 'coupling'}
RACK = 3200
MINRISE = 300                                        # X-PIP-06 (A-M-127)

recs = []
miss = []
for r in rows:
    if not r[3].startswith('DN'):
        continue
    a, b = C.get(r[1]), C.get(r[2])
    if not a or not b:
        miss.append(f'{r[0]} ({r[1] if not a else r[2]} unplaced)')
        continue
    (x1, y1, z1), (x2, y2, z2) = a[0], b[0]
    zr = max(D[lvl(z1)] + RACK, max(z1, z2) + MINRISE)   # X-PIP-06 flexible leg
    legs = [zr - z1, x2 - x1, y2 - y1, z2 - zr]
    nz = [v for v in legs if abs(v) > 1]
    dn = int(r[3][2:])
    cl = r[4]
    el = max(len(nz) - 1, 0)
    to = B169.get(dn, 1.5 * dn) if cl.startswith('M') else 0.5 * OD.get(dn, dn)
    cuts = []
    for i, v in enumerate(nz):
        L = abs(v) - to * ((1 if i > 0 else 0) + (1 if i < len(nz) - 1 else 0))
        while L > 6000:
            cuts.append(6000)
            L -= 6000
        cuts.append(max(L, 0))
    pipe_m = sum(cuts) / 1000
    nb, bs = BOLT.get(dn, (8, '3/4'))
    joints = 2 * el + (len(cuts) - len(nz)) + 2
    recs.append(dict(line=r[0], DN=dn, cls=cl, material=MAT.get(cl, cl), frm=r[1], to=r[2],
                     route_m=round(sum(abs(v) for v in nz) / 1000, 2), pipe_m=round(pipe_m, 2),
                     pieces=len(cuts), cut_list_mm=' '.join(f'{c:.0f}' for c in cuts),
                     elbows_90=el, flanges=2, gaskets=2, stud_bolts=2 * nb,
                     stud_size=f'{bs} in', joints=joints, joint_type=JOINT.get(cl, '-')))

# ---- ISO_ROUTES: the supports sidecar (X-PIP-05) --------------------------------
import hashlib

tab = ['| Line | DN | Class | From | To | dZ up | dX | dY | dZ down | Length m | Elbows |',
       '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
jrows = []
tot = 0.0
for rec, r in zip(recs, [r for r in rows if r[3].startswith('DN')
                         and C.get(r[1]) and C.get(r[2])]):
    a, b = C.get(r[1]), C.get(r[2])
    (x1, y1, z1), (x2, y2, z2) = a[0], b[0]
    zr = max(D[lvl(z1)] + RACK, max(z1, z2) + MINRISE)
    legs = [round(zr - z1), round(x2 - x1), round(y2 - y1), round(z2 - zr)]
    L = sum(abs(v) for v in legs) / 1000
    el = max(sum(1 for v in legs if abs(v) > 1) - 1, 0)
    tab.append(f'| {rec["line"]} | {rec["DN"]} | {rec["cls"]} | {r[1]} | {r[2]} | '
               f'{legs[0]} | {legs[1]} | {legs[2]} | {legs[3]} | {L:.1f} | {el} |')
    jrows.append({'line': rec['line'], 'dn': rec['DN'], 'class': rec['cls'],
                  'from': r[1], 'to': r[2], 'legs_mm': legs, 'length_m': round(L, 1),
                  'elbows': el})
    tot += L

out = ['''# Placement routes

Document number: AQS-ISO-001
Revision: B
Date: 2026-10-28
Authority: the placement model (flow_graph/placement_seed.json Rev M, AQS-BLD-001 block plan); the A-M-074 rack rule. Generated by `docs-authority/_placement_routes.py`. Study routes. Not a stamped shop pack. Supersedes the retired auto-router output (AQS-3D-BUILD-001 Rev G rejected auto-routing; this table routes only lines whose BOTH ends carry a sourced placement - no invented mm).

Route rule: up to the source-level rack (datum + 3200 mm, AQS-PIP-002), X run, Y run, then vertical to the target centre. Legs in mm, signed. Elbows = non-zero legs - 1. Risers are at least 300 mm above the higher end so every route keeps a flexible leg (X-PIP-04). Unit centres are the placement-model centres; nozzle lateral offsets refine at detail design (the nozzle schedules carry face + height). Supports and stress: AQS-PIP-005.
''',
     f'Status. {len(recs)} positioned piped lines routed, {tot:.0f} m total. {len(miss)} piped lines wait on unit placements (the named gap: X-BLD-09 / X-RSZ-05).', '']
out += tab + ['']
out += ['Waiting on placements:'] + [f'- {m}' for m in miss] if miss else ['All piped lines routed.']
open('docs-authority/ISO_ROUTES.md', 'w').write('\n'.join(out) + '\n')
json.dump({'_generated_from': {'graph_sha256': hashlib.sha256(open('flow_graph/plant_flow_graph.json', 'rb').read()).hexdigest(),
                               'generator': 'docs-authority/_placement_routes.py',
                               'placement_seed_revision': seed.get('revision')},
           'rows': jrows,
           'summary': {'routed': len(recs), 'missing_position': len(miss), 'total_m': round(tot)}},
          open('docs-authority/ISO_ROUTES.json', 'w'), indent=1)

# ---- ISO_SHEETS: the insulation + fittings sidecar (X-INV-003/004) ---------------
os.makedirs('docs-authority/iso', exist_ok=True)
with open('docs-authority/iso/ISO_SHEETS.csv', 'w', newline='') as f:
    if recs:
        w = csv.DictWriter(f, list(recs[0].keys()))
        w.writeheader()
        w.writerows(recs)
    else:
        w = csv.DictWriter(f, ['line', 'DN', 'cls', 'material', 'frm', 'to', 'route_m',
                               'pipe_m', 'pieces', 'cut_list_mm', 'elbows_90', 'flanges',
                               'gaskets', 'stud_bolts', 'stud_size', 'joints', 'joint_type'])
        w.writeheader()

L = ['# Isometric sheet data (no SVG: the isometric presentation retired 2026-10-27)', '',
     'Document number: AQS-ISO-002',
     f'Status. {len(recs)} routed lines; waiting on placements {len(miss)}. '
     f'Pipe {sum(x["pipe_m"] for x in recs):.0f} m, elbows {sum(x["elbows_90"] for x in recs)}, '
     f'flanges {sum(x["flanges"] for x in recs)}, joints {sum(x["joints"] for x in recs)}.', '',
     'Basis: the AQS-ISO-001 Rev B route rule over the placement model (Rev ' + str(seed.get("revision")) + '); '
     'elbow take-off ASME B16.9 long-radius (metal) or 0.5 x OD (thermoplastic, A-M-121); 6 m random '
     'lengths; flanges at both nozzles; ASME B16.5 Class 150 bolting; OD ASME B36.10M. Not checked '
     'here: clashes with structure and other lines along the rack (X-PIP-04 with supports and stress).', '',
     '## Lines', '', '| Line | From | To | DN | Class | Pipe m | Elbows |', '| --- | --- | --- | --- | --- | --- | --- |']
L += [f"| {x['line']} | {x['frm']} | {x['to']} | {x['DN']} | {x['cls']} | {x['pipe_m']} | {x['elbows_90']} |" for x in recs]
if miss:
    L += ['', 'Waiting on placements:'] + [f'- {m}' for m in miss]
open('docs-authority/ISO_SHEETS.md', 'w').write('\n'.join(L) + '\n')
print(f'placement_routes: {len(recs)} routed ({tot:.0f} m), {len(miss)} waiting on placements')
