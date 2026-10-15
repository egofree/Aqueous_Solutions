"""X-PAR-10 parametric vent scrubber EVAP_ACID_VS (CadQuery). Reads params on the graph (written by flow_graph/param/write_graph.py
from flow_graph/param/vent_scrubber.py) and writes models/mfg/EVAP_ACID_VS/export/evap_acid_vs.step and .stl, bom.csv, fasteners.csv.
Run: /tmp/cqvenv/bin/python models/mfg/vent_scrubber.py"""
import json, os
import cadquery as cq
U = 'EVAP_ACID_VS'
g = json.load(open('flow_graph/plant_flow_graph.json')); p = next(n for n in g['nodes'] if n['unit_id'] == U)['params']
DN = p['DN']; OD = {100: 114.3, 125: 141.3, 150: 168.3, 200: 219.1}[DN]; t = {100: 8.6, 125: 9.5, 150: 11.0, 200: 12.7}[DN]   # ASTM D1785 Sch 80
bed = p['packed_mm']; H = p['height_mm']; sump = 450.0; top = H - sump - bed
shell = cq.Workplane('XY').circle(OD/2).circle(OD/2 - t).extrude(H)
shell = shell.union(cq.Workplane('XY').circle(OD/2).extrude(t)).union(cq.Workplane('XY').workplane(offset=H - t).circle(OD/2).extrude(t))
support = cq.Workplane('XY').workplane(offset=sump).circle(OD/2 - t).extrude(10)                      # perforated support plate envelope
packing = cq.Workplane('XY').workplane(offset=sump + 10).circle(OD/2 - t - 1).extrude(bed - 10)        # random ring bed envelope
demister = cq.Workplane('XY').workplane(offset=H - 160).circle(OD/2 - t).extrude(100)
noz = lambda z, ang: cq.Workplane('YZ').circle(16.7).extrude(80).translate((OD/2 - 5, 0, z)).rotate((0, 0, 0), (0, 0, 1), ang)
model = shell.union(support).union(packing).union(demister)
for z, a in ((sump - 120, 0), (H - 250, 90), (100, 180), (sump + bed + 80, 270)):                    # vent in, liquor in, spent out, NaOH in
    model = model.union(noz(z, a))
model = model.union(cq.Workplane('XY').workplane(offset=H).circle(16.7).extrude(80))                   # off-gas outlet
out = f'models/mfg/{U}/export'; os.makedirs(out, exist_ok=True)
cq.exporters.export(model, f'{out}/{U.lower()}.step'); cq.exporters.export(model, f'{out}/{U.lower()}.stl')
rows = [('1', f'Shell PVC-U DN{DN} Sch 80 x {H} mm with solvent-welded caps', 1, 'PVC-U (ASTM D1785)', 'AQS-DUTY-061 section 2'),
        ('2', 'Packing support plate, perforated, 50 % open', 1, 'PVC-U sheet', 'PERRY9_ABS'),
        ('3', f'Random packing: 16 mm PVC tube rings cut L = D, bed {bed} mm', 1, 'PVC-U (in-house cut, X-MFG-32 jellybean line)', f"16 mm x {p['packed_mm']} mm bed; D/dp 8 (PERRY9_ABS)"),
        ('4', 'Liquid distributor, drip pipe with 4 holes', 1, 'PVC-U', 'PERRY9_ABS'),
        ('5', 'Mesh demister pad 100 mm', 1, 'PVC or PP mesh', 'AQS-DUTY-061'),
        ('6', 'Sump recirculation pump, magnetic drive, about 0.35 m3/h at 10 m', 1, 'PVDF or PP wetted', 'X-MFG-32 in-house pump line'),
        ('7', 'Nozzles DN25: vent in, liquor in, spent out, NaOH in, off-gas out', 5, 'PVC-U socket', 'AQS-DUTY-061'),
        ('8', 'Sump level switch and pH probe', 1, 'PVDF body', 'pH > 12 control of the NaOH bleed (A-M-111)')]
open(f'models/mfg/{U}/bom.csv', 'w').write('item,description,qty,material,basis\n' + '\n'.join(','.join(str(x) for x in r) for r in rows) + '\n')
open(f'models/mfg/{U}/fasteners.csv', 'w').write('item,size,grade,qty,location,basis\n1,M10 U-bolt for DN%d,ISO 3506 A4-70,2,frame clamps to the EVAP_ACID frame,study\n2,Solvent cement,PVC-U per ASTM D2564,1,all joints,ASTM D2564\n' % DN)
print(U, 'DN', DN, 'H', H, 'bed', bed)
