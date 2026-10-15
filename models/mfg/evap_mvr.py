"""X-MFG-30 parametric MVR falling-film evaporator (CadQuery). Reads the design from the graph (params.design written by
flow_graph/param/evap_design.py) and writes models/mfg/<UNIT>/export/<unit>.step and .stl, bom.csv, fasteners.csv.
Run: /tmp/cqvenv/bin/python models/mfg/evap_mvr.py EVAP_ACID"""
import json, math, os, sys
import cadquery as cq
U = sys.argv[1]; acid = U == 'EVAP_ACID'
g = json.load(open('flow_graph/plant_flow_graph.json')); p = next(n for n in g['nodes'] if n['unit_id'] == U)['params']; d = p['design']
D = d['shell_D_mm']; L = d['tube_L_mm']; n = d['tubes']; di = d['tube_id_mm']; wall = 6.0 if acid else 2.0; do = di + 2*wall
sump = 400.0; head = 150.0; sep_h = 900.0; t_sh = 10.0 if acid else 6.0; ts = 40.0 if acid else 25.0
pitch = 1.25*do
pts = []; r = 0
while len(pts) < n:   # triangular-pitch rings
    r += 1
    for k in range(6*r):
        a = 2*math.pi*k/(6*r); pts.append((r*pitch*math.cos(a), r*pitch*math.sin(a)))
pts = [(0, 0)] + pts[:n-1]
z0 = 0.0
body = cq.Workplane('XY').circle(D/2).circle(D/2 - t_sh).extrude(sump + L + head)                       # shell (sump, tube zone, top head)
body = body.union(cq.Workplane('XY').circle(D/2).extrude(t_sh))                                           # bottom plate
for zt in (sump, sump + L - ts):
    tsheet = cq.Workplane('XY').workplane(offset=zt).circle(D/2 - t_sh).extrude(ts)
    tsheet = tsheet.cut(cq.Workplane('XY').workplane(offset=zt).pushPoints(pts).circle(do/2).extrude(ts))
    body = body.union(tsheet)
tubes = cq.Workplane('XY').workplane(offset=sump).pushPoints(pts).circle(do/2).circle(di/2).extrude(L)
body = body.union(tubes)
sep = cq.Workplane('XY').workplane(offset=sump + L + head).circle(D/2).circle(D/2 - t_sh).extrude(sep_h)
sep = sep.union(cq.Workplane('XY').workplane(offset=sump + L + head + sep_h - t_sh).circle(D/2).extrude(t_sh))
body = body.union(sep)
blower = cq.Workplane('XY').box(450, 450, 450).translate((D/2 + 220, 0, sump + L + head + 300))          # in-house blower envelope (X-MFG-32)
ix = cq.Workplane('XY').box(200, 300, 600).translate((D/2 + 95, 0, 400))                                  # interchanger block
model = body.union(blower).union(ix)
col = d.get('column')
if col:   # free-standing glass column beside the body, on the same frame (AQS-DUTY-060 section 7)
    Dc = col['DN'] + 20; xc = -(D/2 + 125 + Dc/2)
    column = cq.Workplane('XY').circle(Dc/2).circle(Dc/2 - 8).extrude(col['height_mm']).translate((xc, 0, 0))
    column = column.union(cq.Workplane('XY').circle(Dc/2).extrude(8).translate((xc, 0, 0)))
    duct = cq.Workplane('YZ').circle(40).extrude(abs(xc) - D/2 + 10).translate((xc + Dc/2 - 10, 0, sump + L + head + 400))
    model = model.union(column).union(duct)
out = f'models/mfg/{U}/export'; os.makedirs(out, exist_ok=True)
cq.exporters.export(model, f'{out}/{U.lower()}.step'); cq.exporters.export(model, f'{out}/{U.lower()}.stl')
mat_t = 'impregnated graphite (PERRY9_MAT)' if acid else 'nickel 200 (PERRY9_MAT)'
mat_s = 'carbon steel, PTFE-lined process side' if acid else 'nickel 200'
rows = [('1', f'Shell DN{int(D)} x {int(sump+L+head)} mm, wall {t_sh} mm', 1, mat_s, 'AQS-DUTY-060 section 2'),
        ('2', f'Tubes ID {di} x OD {do} x {int(L)} mm', n, mat_t, f'falling film {d["A_ff_m2"]} m2 at U from PERRY9_EVAP'),
        ('3', f'Tubesheets {ts} mm', 2, mat_t, 'AQS-DUTY-060'),
        ('4', f'Vapour separator DN{int(D)} x {int(sep_h)} mm with mesh pad', 1, mat_s + '; PTFE or PVDF mesh', 'AQS-DUTY-060'),
        ('5', f'Blower, single-stage centrifugal, ratio {d["ratio"]}, {d["comp_shaft_kW"]} kW shaft', 1, 'impeller titanium grade 7 or PVDF-lined (acid); nickel (base)', 'X-MFG-32 in-house line; motor IEC 60034 frame'),
        ('6', f'Feed/condensate/product interchanger {d["ix_A_m2"]} m2', 1, mat_t, f'{d["ix_Q_kW"]} kW, outlets {d["T_out_C"]} C'),
        ('7', f'Recirculation pump {d["recirc_kg_h"]} kg/h at 4 m', 1, 'PVDF (acid) or nickel (base) wetted', 'X-MFG-32'),
        ('8', 'Body relief valve API 526 D orifice, set 100 kPa g', 1, 'PTFE-lined (acid) or nickel trim (base)', 'fire case ISO 23251, sized in-house'),
        ('9', 'Shell relief valve API 526 D orifice, set 350 kPa g', 1, 'stainless trim on steam side', 'blocked outlet, sized in-house')]
if d.get('column'):
    c = d['column']
    rows += [('10', f"HCl column DN{c['DN']}, packed {c['packed_mm']} mm ({c['column_stages']} ideal stages x HETP x margin), height {c['height_mm']} mm", 1, c['material'].replace(',', ';'), 'PERRY7_HCL_VLE stage count; condensate %.2f wt%% HCl' % c['cond_hcl_wt_pct']),
             ('11', 'Vapour duct DN80 separator to column; column bottoms line DN15 back to the body', 1, 'PTFE-lined steel / PVDF', 'AQS-DUTY-060')]
open(f'models/mfg/{U}/bom.csv', 'w').write('item,description,qty,material,basis\n' + '\n'.join(','.join(str(x) for x in r) for r in rows) + '\n')
open(f'models/mfg/{U}/fasteners.csv', 'w').write('item,size,grade,qty,location,basis\n'
    f'1,M16 stud + 2 nuts (ISO 4014 / ISO 4032),{"ISO 3506 A4-70 outside the wetted zone" if acid else "ISO 898-1 8.8 zinc"},{2*12},body flanges,ISO 7005-1 PN10 DN{int(D)} pattern (study)\n'
    f'2,Flange gasket,{"PTFE envelope" if acid else "graphite sheet"},2,body flanges,AQS-NZ-001\n')
print(U, 'tubes', n, 'shell', D, 'height', sump + L + head + sep_h)
