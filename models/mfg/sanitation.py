"""X-SAN-01 sanitation train (CadQuery): BLACK_DIGEST, BLACK_DEWATER, BLACK_PASTEUR, BLACK_ALK_HOLD. Reads params.design written by
flow_graph/param/sanitation.py; writes models/mfg/<UNIT>/export STEP/STL, bom.csv, fasteners.csv, WORK_ORDER.md.
Run: $CADQUERY_PYTHON models/mfg/sanitation.py"""
import json, os
import cadquery as cq
g = json.load(open('flow_graph/plant_flow_graph.json')); N = {n['unit_id']: n for n in g['nodes']}
def tank(D, H, t, n=1, gap=150):
    m = None
    for i in range(n):
        b = cq.Workplane('XY').circle(D/2).circle(D/2 - t).extrude(H).union(cq.Workplane('XY').circle(D/2).extrude(t)).union(
            cq.Workplane('XY').workplane(offset=H).circle(D/2 + 30).extrude(t + 6)).translate((i*(D + gap), 0, 0))
        for k in range(4): b = b.union(cq.Workplane('YZ').circle(16.7).extrude(60).translate((D/2 - 5, 0, H*(0.2 + 0.18*k))).rotate((0, 0, 0), (0, 0, 1), k*90).translate((i*(D + gap), 0, 0)))
        m = b if m is None else m.union(b)
    return m
S = {}
_bd = N.get('BLACK_DIGEST')
if not (_bd and _bd.get('presence') == 'present' and 'design' in (_bd.get('params') or {})):
    raise SystemExit('BLACK_DIGEST absent or unsized on the graph; nothing to build')
d = _bd['params']['design']; S['BLACK_DIGEST'] = (tank(d['D_mm'], d['H_mm'], d['wall_mm']), [
    ('1', f"Shell DN{d['D_mm']} x {d['H_mm']} mm x {d['wall_mm']} mm, flat bottom, domed gas lid", 1, 'PP-H sheet, extrusion-welded (DVS 2207-11)', 'AQS-DUTY-063 section 2'),
    ('2', 'Nozzles DN25: blackwater in, toilet solids in, digestate out, biogas out, gas recirc in', 5, 'PP-H', 'AQS-DUTY-063'),
    ('3', 'Biogas recirculation diaphragm blower about 2 L/min', 1, 'PP/EPDM', 'X-INV-01 family'), ('4', 'Heating mat 150 W, thermostat 55 C, two RTDs', 1, 'silicone / 316L', 'AQS-DUTY-063'),
    ('5', 'PIR insulation 50 mm, PE cladding', 1, 'PIR', 'AQS-DUTY-063'), ('6', 'Water seal and flame arrester on the biogas line to AFTERBURNER', 1, '316L', 'NFPA 54 / ISO 16852')])
# BLACK_DEWATER / BLACK_PASTEUR / BLACK_ALK_HOLD retired with their units (2026-10-30 cleanup); the train is BLACK_DIGEST only
for U, (m, rows) in S.items():
    o = f'models/mfg/{U}/export'; os.makedirs(o, exist_ok=True)
    cq.exporters.export(m, f'{o}/{U.lower()}.step'); cq.exporters.export(m, f'{o}/{U.lower()}.stl')
    __import__('csv').writer(open(f'models/mfg/{U}/bom.csv', 'w', newline='')).writerows([('item', 'description', 'qty', 'material', 'basis')] + [tuple(r) for r in rows])   # quoted: materials carry commas
    open(f'models/mfg/{U}/fasteners.csv', 'w').write('item,size,grade,qty,location,basis\n1,M8 x 30 lid bolt with nut and washers,ISO 3506 A4-70,12,lid flange,study\n2,M10 anchor,ISO 3506 A4-70,4,feet,study\n')
    open(f'models/mfg/{U}/WORK_ORDER.md', 'w').write(f"# Work order {U}\n\nAuthority: AQS-DUTY-063 (X-SAN-01). In-house fabrication.\n\n" + '\n'.join(f'{i+1}. Make and fit item {r[0]}: {r[1]} ({r[3]}).' for i, r in enumerate(rows)) +
        f"\n{len(rows)+1}. Test: {'hydrostatic fill 24 h, no leak; gas-tightness of the lid at 5 kPa' if U == 'BLACK_DIGEST' else 'temperature mapping at 70 C, both RTDs within 0.5 K, hold timer trip test' if U == 'BLACK_PASTEUR' else 'release interlock test with a failed and a passed result' if U == 'BLACK_ALK_HOLD' else 'run test on water and bran slurry, cake TS'}.\n")
    print(U)
