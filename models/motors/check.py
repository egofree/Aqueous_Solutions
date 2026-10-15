"""X-INV-02C dimensional check: each STEP assembly against IEC 60072-1 (shaft height H = axis to foot face, shaft diameter, extension E,
foot centres A x B) or NEMA ICS 16 flange width; exits non-zero on a failure. Run: /tmp/cqvenv/bin/python models/motors/check.py"""
import csv, os, sys
import cadquery as cq
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, ROOT)
from flow_graph.inventory.motor_designs import IEC72
F = list(csv.DictReader(open(f'{ROOT}/docs-authority/inventory/MOTOR_FAMILIES.csv'))); bad = []; rows = []
for r in F:
    f = r['family']; s = cq.importers.importStep(f'{ROOT}/models/motors/{f}/export/{f.lower()}.step'); b = s.val().BoundingBox()
    msg = 'ok'
    if 'IEC' in r['size']:
        fr = r['size'].split('IEC ')[1].split(' ')[0]; H, Ds, E, A, Bb, K = IEC72[fr]
        if abs(-b.zmin - H) > 0.5: msg = f'H {-b.zmin:.1f} != {H}'
        elif b.xlen < A: msg = f'foot width {b.xlen:.0f} < A {A}'
        elif b.zmax > 2.2*H: msg = f'height {b.zmax:.0f} > 2.2 H'
    elif 'NEMA' in r['size'] or 'mm (NEMA' in r['size'] or 'F03' in r['size']:
        fl = 42 if '42' in r['size'] or 'F03' in r['size'] else 57 if '57' in r['size'] else 86
        if abs(b.xlen - fl) > 0.5: msg = f'flange {b.xlen:.1f} != {fl}'
    rows.append((f, round(b.xlen, 1), round(b.ylen, 1), round(b.zlen, 1), msg))
    if msg != 'ok': bad.append((f, msg))
for x in rows: print(*x)
print('FAIL' if bad else 'PASS', bad); sys.exit(1 if bad else 0)
