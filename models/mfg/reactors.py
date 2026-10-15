"""X-MFG-31 parametric in-house reaction chambers (CadQuery): GLASS_DIGEST, DIGESTER, OIL_PYRO. Reads params.design on the graph
(written by flow_graph/param/reactor_design.py) and writes models/mfg/<UNIT>/export/<unit>.step and .stl, bom.csv, fasteners.csv and
WORK_ORDER.md. Run: /tmp/cqvenv/bin/python models/mfg/reactors.py"""
import json, os
import cadquery as cq
g = json.load(open('flow_graph/plant_flow_graph.json')); N = {n['unit_id']: n for n in g['nodes']}
SPEC = {'GLASS_DIGEST': dict(mat='CPVC sheet, rolled and extrusion-welded (DVS 2207-3)', noz=('feed slurry in', 'NaOH in', 'liquor out', 'drain', 'vent'), coil=True, agit=True, legs=4),
        'DIGESTER': dict(mat='HDPE PE100 sheet, rolled and extrusion-welded (DVS 2207-4)', noz=('feed in', 'digestate out', 'gas out', 'gas recirc in', 'drain'), coil=False, agit=False, legs=3),
        'YEAST': dict(mat='HDPE PE100 sheet, rolled and extrusion-welded (DVS 2207-4)', noz=('sugar in', 'beer out', 'CO2 out', 'recirculation', 'drain'), coil=False, agit=False, legs=3),
        'ABE': dict(mat='HDPE PE100 sheet, rolled and extrusion-welded (DVS 2207-4)', noz=('sugar in', 'broth out', 'gas out', 'N2 blanket', 'drain'), coil=False, agit=False, legs=3),
        'ACETOX': dict(mat='PP-H sheet, extrusion-welded (DVS 2207-11)', noz=('ethanol in', 'acid out', 'O2 sparge', 'vent', 'drain'), coil=False, agit=False, legs=3),
        'OIL_PYRO': dict(mat='SA-240 304H plate, rolled, GTAW (ASME IX)', noz=('oil feed in', 'vapour out to OIL_FRAC', 'char out', 'thermowell', 'bursting disc'), coil=False, agit=False, legs=3)}
for U, s in SPEC.items():
    d = N[U]['params']['design']; D = d['D_mm']; H = d['H_mm']; t = d['wall_mm']
    body = cq.Workplane('XY').circle(D/2).circle(D/2 - t).extrude(H).union(cq.Workplane('XY').circle(D/2).extrude(t))
    lid = cq.Workplane('XY').workplane(offset=H).circle(D/2 + 30).circle(D/2 - t).extrude(t + 6).union(cq.Workplane('XY').workplane(offset=H + t + 6).circle(D/2 + 30).extrude(t + 6))
    m = body.union(lid)
    for i, _ in enumerate(s['noz']):
        z = H*0.2 + i*H*0.15
        m = m.union(cq.Workplane('YZ').circle(16.7).extrude(60).translate((D/2 - 5, 0, z)).rotate((0, 0, 0), (0, 0, 1), i*72))
    for i in range(s['legs']):
        m = m.union(cq.Workplane('XY').rect(40, 40).extrude(300).translate((0, 0, -300)).translate(((D/2 - 20), 0, 0)).rotate((0, 0, 0), (0, 0, 1), i*360/s['legs']))
    if s['agit']:
        a = d['agitator']; m = m.union(cq.Workplane('XY').workplane(offset=H*0.25).circle(12).extrude(H*0.75 + 2*t + 12 + 150)).union(cq.Workplane('XY').workplane(offset=H*0.25).rect(a['D_imp_mm'], 25).extrude(20))
    if s['coil']:
        m = m.union(cq.Workplane('XY').workplane(offset=H*0.15).circle(D/2 - t - 40).circle(D/2 - t - 56).extrude(H*0.5))
    if U == 'OIL_PYRO':
        m = m.union(cq.Workplane('XY').workplane(offset=t).circle(D/2 + 60).circle(D/2).extrude(H - t))   # heater band and insulation envelope
    o = f'models/mfg/{U}/export'; os.makedirs(o, exist_ok=True)
    cq.exporters.export(m, f'{o}/{U.lower()}.step'); cq.exporters.export(m, f'{o}/{U.lower()}.stl')
    rows = [('1', f'Shell DN{D} x {H} mm x {t} mm wall with flat bottom', 1, s['mat'], 'AQS-DUTY-062 section 1'),
            ('2', f'Bolted flat lid with gasket', 1, s['mat'], 'AQS-DUTY-062'),
            ('3', 'Nozzles DN25: ' + '; '.join(s['noz']), len(s['noz']), s['mat'], 'AQS-DUTY-062'),
            ('4', f"Legs 40x40 x 300 mm", s['legs'], s['mat'], 'study')]
    if s['agit']: rows += [('5', f"Top-entry agitator, 4-blade 45 deg PBT D{d['agitator']['D_imp_mm']} at {d['agitator']['rpm']} rpm, {d['agitator']['motor_kW']} kW motor, PVDF sleeve", 1, 'PVDF / 316L', 'PERRY9_MIX')]
    if s['coil']: rows += [('6', 'Q3 heating coil, PVDF tube DN15', 1, 'PVDF', 'graph HL-Q3-A/B-HX6')]
    if U in ('YEAST', 'ABE', 'ACETOX'): rows += [('5', f"PIR insulation 50 mm with PE cladding; {d['mixer']}", 1, 'PIR', 'AQS-DUTY-062 section 5'), ('6', f"Heater mat {max(5, round(d['heat_W']*2))} W with thermostat", 1, 'silicone', 'AQS-DUTY-062 section 5')]
    if U == 'DIGESTER': rows += [('5', 'Biogas recirculation blower, diaphragm, about 1 L/min', 1, 'PP/EPDM', 'AQS-DUTY-062'), ('6', 'PIR insulation 50 mm with PE cladding', 1, 'PIR', 'AQS-DUTY-062')]
    if U == 'OIL_PYRO': rows += [('5', f"Ceramic band heaters, {d['kW']:.2f} kW installed rounded up to 2.0 kW, 480 V", 1, 'mica/ceramic', 'AQS-DUTY-062'), ('6', 'Ceramic fibre insulation 60 mm with SS cladding', 1, 'Al2O3-SiO2 fibre', 'ASTM C892'), ('7', 'Bursting disc DN25 to flare header', 1, 'Inconel', 'ASME VIII-1 UG-127')]
    open(f'models/mfg/{U}/bom.csv', 'w').write('item,description,qty,material,basis\n' + '\n'.join(','.join(str(x) for x in r) for r in rows) + '\n')
    bolts = max(8, int(3.14159*(D + 60)/100)//4*4)
    open(f'models/mfg/{U}/fasteners.csv', 'w').write(f"item,size,grade,qty,location,basis\n1,M10 x 40 lid bolt with nut and washers,{'ASTM A193 B8' if U == 'OIL_PYRO' else 'ISO 3506 A4-70'},{bolts},lid flange at 100 mm pitch,study\n2,M12 anchor,ISO 3506 A4-70,{s['legs']},leg feet,study\n")
    open(f'models/mfg/{U}/WORK_ORDER.md', 'w').write(f"""# Work order {U}

Authority: AQS-DUTY-062 (X-MFG-31). In-house fabrication; no bought vessel.

1. Cut and roll the shell DN{D}, {t} mm, height {H} mm; cut the bottom and lid discs ({s['mat']}).
2. Weld the longitudinal seam and the bottom; weld the lid flange ring.
3. Cut and weld {len(s['noz'])} DN25 nozzles: {', '.join(s['noz'])}.
4. Weld {s['legs']} legs; drill {bolts} lid bolt holes.
5. {'Fit the agitator and the Q3 coil.' if s['agit'] else 'Fit the gas recirculation sparge and insulation.' if U in ('DIGESTER', 'ABE') else 'Fit the O2 sparger, heater mat and insulation.' if U == 'ACETOX' else 'Fit the recirculation connection, heater mat and insulation.' if U == 'YEAST' else 'Fit the band heaters, thermowell, insulation and bursting disc.'}
6. Test: {'hydrostatic fill to the brim, 24 h, no leak (DVS 2205)' if U != 'OIL_PYRO' else 'hydrostatic test at 1.3 x design pressure (ASME VIII-1 UG-99); heater insulation resistance; dry-run to 500 C'}.
7. Inspect against models/mfg/{U}/export/{U.lower()}.step; record dimensions on the traveller.
""")
    print(U, D, H, t)

# MEOH_SYNTH (A-M-156): jacketed fixed-bed tube, pressure part to ASME VIII-1; flanges ASME B16.5 Class 600 (Group 1.1 rating at 260 C above 55 bar g)
U = 'MEOH_SYNTH'; d = N[U]['params']['design']; L = d['L_bed_mm'] + 400; OD = 60.3; t = d['t_nom_mm']
tube = cq.Workplane('XY').circle(OD/2).circle(OD/2 - t).extrude(L)
fl = lambda z: cq.Workplane('XY').workplane(offset=z).circle(165/2).circle(OD/2 - t).extrude(32)      # DN50 Class 600 WN flange OD 165, thk 32 (B16.5)
jk = cq.Workplane('XY').workplane(offset=150).circle(114.3/2).circle(114.3/2 - 6.02).extrude(L - 300)   # DN100 Sch 40 jacket
m = tube.union(fl(-32)).union(fl(L)).union(jk)
for z in (250, L - 250): m = m.union(cq.Workplane('YZ').circle(16.7).extrude(60).translate((114.3/2 - 5, 0, z)))
o = f'models/mfg/{U}/export'; os.makedirs(o, exist_ok=True)
cq.exporters.export(m, f'{o}/{U.lower()}.step'); cq.exporters.export(m, f'{o}/{U.lower()}.stl')
rows = [('1', f"Reactor tube {d['tube']}, {L} mm, {d['tubes']} off", d['tubes'], 'SA-106 B', 'AQS-DUTY-062 section 4; UG-27'),
        ('2', 'Weld-neck flange DN50 Class 600 RF', 2*d['tubes'], 'SA-105', 'ASME B16.5'), ('3', 'Blind flange DN50 Class 600 with DN15 nozzle', 2*d['tubes'], 'SA-105', 'ASME B16.5'),
        ('4', 'Spiral-wound gasket DN50 Class 600, 316/graphite', 2*d['tubes'], '316L / flexible graphite', 'ASME B16.20'),
        ('5', f"Jacket DN100 Sch 40, {L - 300} mm, thermal oil in/out DN25", d['tubes'], 'SA-106 B', 'AQS-DUTY-062'),
        ('6', f"Cu/ZnO/Al2O3 catalyst pellets {d['cat_kg']:.2f} kg ({d['V_bed_L']:.2f} L)", 1, 'Cu/ZnO/Al2O3', 'CTC2020_CZA'),
        ('7', 'Catalyst support grid and inert alumina balls top and bottom', 1, '316L / alpha-alumina', 'study'),
        ('8', f"Feed preheater, {d['preheat_kW']:.2f} kW electric", 1, 'mineral-insulated cable on 316L', 'AQS-DUTY-062'),
        ('9', 'Safety valve, conventional, set at design pressure (API 520 sized orifice in the graph relief_basis)', 1, '316L', 'API 520')]
open(f'models/mfg/{U}/bom.csv', 'w').write('item,description,qty,material,basis\n' + '\n'.join(','.join(str(x) for x in r) for r in rows) + '\n')
open(f'models/mfg/{U}/fasteners.csv', 'w').write('item,size,grade,qty,location,basis\n1,5/8 in stud bolt with 2 heavy hex nuts,ASTM A193 B7 / A194 2H,' + str(8*2*d['tubes']) + ',DN50 Class 600 flanges (8 per joint),ASME B16.5\n')
open(f'models/mfg/{U}/WORK_ORDER.md', 'w').write(f"""# Work order {U}

Authority: AQS-DUTY-062 section 4 (X-MFG-31, A-M-156). In-house fabrication to ASME VIII-1; welders and procedure qualified to ASME IX.

1. Cut the {d['tube']} tube to {L} mm; bevel both ends.
2. Butt-weld the DN50 Class 600 weld-neck flanges (GTAW root, ASME IX qualified WPS); 100 % radiography of the circumferential welds (UW-11).
3. Fit the DN100 jacket with end plates and two DN25 thermal-oil nozzles; fillet-weld to the tube.
4. Hydrostatic test of the tube at 1.3 x {d['design_MPa']:.2f} MPa (UG-99), jacket at 1.3 x its design.
5. Load the support grid, inert balls, {d['cat_kg']:.2f} kg catalyst, inert balls; close with the blind flanges and spiral-wound gaskets, torque per ASME PCC-1.
6. Reduce the catalyst in dilute H2 at the supplier-independent schedule in the operating procedure (X-OPS-01).
7. Inspect against models/mfg/{U}/export/{U.lower()}.step; record on the traveller.
""")
print(U, L)

# HTC (X-MFG-31 batch 2): flanged autoclave spool, DN100 Sch 10S SA-312 TP316L, ASME B16.5 Class 300 (316L rating at 200 C above the design)
U = 'HTC'; d = N[U]['params']['design']; L = max(d['H_mm'], 200); OD = 114.3; t = 3.05
m = cq.Workplane('XY').circle(OD/2).circle(OD/2 - t).extrude(L)
for z in (-28.4, L): m = m.union(cq.Workplane('XY').workplane(offset=z).circle(254/2).extrude(28.4))      # DN100 Class 300 blind/WN, OD 254 (B16.5)
m = m.union(cq.Workplane('XY').workplane(offset=30).circle(OD/2 + 50).circle(OD/2).extrude(L - 60))      # heater band + mineral wool envelope
o = f'models/mfg/{U}/export'; os.makedirs(o, exist_ok=True)
cq.exporters.export(m, f'{o}/{U.lower()}.step'); cq.exporters.export(m, f'{o}/{U.lower()}.stl')
rows = [('1', f'Autoclave spool DN100 Sch 10S, {L} mm', 1, 'SA-312 TP316L', f"AQS-DUTY-062 section 5; UG-27 t_req {d['t_req_mm']:.2f} mm vs 2.67 mm min"),
        ('2', 'Weld-neck flange DN100 Class 300 RF', 1, 'SA-182 F316L', 'ASME B16.5'), ('3', 'Blind flange DN100 Class 300 with DN15 feed/discharge and thermowell', 2, 'SA-182 F316L', 'ASME B16.5'),
        ('4', 'Spiral-wound gasket DN100 Class 300', 2, '316L / flexible graphite', 'ASME B16.20'),
        ('5', f"Band heater {max(50, round(d['heat_W']*2))} W with PID and high-limit", 1, 'mica', 'AQS-DUTY-062 section 5'),
        ('6', 'Mineral wool 50 mm with SS cladding', 1, 'mineral wool', 'ASTM C547'), ('7', 'Safety valve DN15, set at design pressure', 1, '316L', 'API 520 (graph relief_basis)')]
open(f'models/mfg/{U}/bom.csv', 'w').write('item,description,qty,material,basis\n' + '\n'.join(','.join(str(x) for x in r) for r in rows) + '\n')
open(f'models/mfg/{U}/fasteners.csv', 'w').write('item,size,grade,qty,location,basis\n1,3/4 in stud bolt with 2 heavy hex nuts,ASTM A193 B8M / A194 8M,16,two DN100 Class 300 joints (8 each),ASME B16.5\n')
open(f'models/mfg/{U}/WORK_ORDER.md', 'w').write(f"""# Work order {U}

Authority: AQS-DUTY-062 section 5 (X-MFG-31). In-house fabrication to ASME VIII-1; welders and procedure qualified to ASME IX.

1. Cut DN100 Sch 10S 316L pipe to {L} mm; bevel; butt-weld the Class 300 weld-neck flange (GTAW, back-purged).
2. Drill and weld the DN15 nozzles and thermowell into the blind flanges.
3. Hydrostatic test at 1.3 x {d['design_MPa']:.2f} MPa (UG-99).
4. Fit the band heater, high-limit, insulation and safety valve.
5. Inspect against models/mfg/{U}/export/{U.lower()}.step; record on the traveller.
""")
print(U, L)
